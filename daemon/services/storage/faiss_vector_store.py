#!/usr/bin/env python3
"""
FAISS分片向量存储 - 支持持续数据积累的智能向量数据库
实现压缩存储、分片管理、冷热分离的向量存储架构
"""

import asyncio
import json
import logging
import pickle
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import faiss
import numpy as np

from core.error_handling import handle_errors, ErrorSeverity, ErrorCategory
from core.service_facade import get_service
from core.environment_manager import get_environment_manager
from services.shared_executor_service import get_shared_executor_service

logger = logging.getLogger(__name__)


@dataclass
class VectorDocument:
    """向量文档 - 压缩存储优化"""
    id: str
    summary: str  # 替代原文，最多100字
    embedding: np.ndarray  # 压缩向量
    metadata: Dict[str, Any]
    entity_id: Optional[str] = None
    timestamp: datetime = None
    content_type: str = "text"
    value_score: float = 0.0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class SearchResult:
    """搜索结果"""
    id: str
    summary: str
    score: float
    metadata: Dict[str, Any]
    entity_id: Optional[str] = None
    timestamp: datetime = None
    content_type: str = "text"
    value_score: float = 0.0


@dataclass
class ShardInfo:
    """分片信息"""
    shard_id: str
    index_file: Path
    metadata_file: Path
    summary_file: Path
    created_at: datetime
    last_updated: datetime
    document_count: int
    total_size_mb: float
    tier: str = "hot"  # hot/warm/cold
    is_active: bool = True


@dataclass
class FAISSMetrics:
    """FAISS向量存储性能指标"""
    total_documents: int
    total_shards: int
    hot_shards: int
    warm_shards: int
    cold_shards: int
    compression_ratio: float
    avg_search_time_ms: float
    storage_size_mb: float
    memory_usage_mb: float
    last_updated: datetime


class FAISSVectorStore:
    """FAISS分片向量存储 - 支持持续积累的智能存储"""

    def __init__(
        self,
        storage_dir: Optional[Path] = None,
        vector_dim: int = 384,
        compressed_dim: int = 256,
        shard_size_limit: int = 100000,
        compression_method: str = "PQ",
        max_workers: int = 4,
    ):
        # 存储配置
        env_manager = get_environment_manager()
        self.storage_dir = Path(storage_dir) if storage_dir else \
            env_manager.get_data_dir() / "knowledge"
        
        self.vector_dim = vector_dim
        self.compressed_dim = compressed_dim
        self.shard_size_limit = shard_size_limit
        self.compression_method = compression_method
        
        # 目录结构
        self.hot_dir = self.storage_dir / "hot_index"
        self.warm_dir = self.storage_dir / "warm_index" 
        self.cold_dir = self.storage_dir / "cold_archive"
        self.cache_dir = self.storage_dir / "ollama_cache"
        
        # 确保目录存在
        for dir_path in [self.hot_dir, self.warm_dir, self.cold_dir, self.cache_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 分片管理
        self.shards: Dict[str, ShardInfo] = {}
        self.current_shard: Optional[ShardInfo] = None
        self.shard_metadata_file = self.storage_dir / "shard_metadata.json"
        
        # 内存中的活跃索引
        self.active_indices: Dict[str, faiss.Index] = {}
        self.document_cache: Dict[str, VectorDocument] = {}
        
        # 性能优化
        self.max_workers = max_workers
        self._executor = get_shared_executor_service()
        
        # 性能监控
        self._search_times: List[float] = []
        self._max_history = 100
        
        self._metrics = FAISSMetrics(
            total_documents=0,
            total_shards=0,
            hot_shards=0,
            warm_shards=0,
            cold_shards=0,
            compression_ratio=0.0,
            avg_search_time_ms=0.0,
            storage_size_mb=0.0,
            memory_usage_mb=0.0,
            last_updated=datetime.utcnow(),
        )

    async def initialize(self) -> bool:
        """初始化FAISS向量存储"""
        try:
            # 加载分片元数据
            await self._load_shard_metadata()
            
            # 加载当前活跃分片
            await self._load_active_shard()
            
            # 预加载热数据索引
            await self._preload_hot_indices()
            
            await self._update_metrics()
            
            logger.info(f"FAISS向量存储初始化完成 - 分片数: {len(self.shards)}, 文档数: {self._metrics.total_documents}")
            return True
            
        except Exception as e:
            logger.error(f"FAISS向量存储初始化失败: {e}")
            return False

    async def close(self):
        """关闭向量存储"""
        try:
            # 保存当前活跃分片
            if self.current_shard:
                await self._save_current_shard()
            
            # 保存分片元数据
            await self._save_shard_metadata()
            
            # 清理内存
            self.active_indices.clear()
            self.document_cache.clear()
            
            logger.info("FAISS向量存储已关闭")
            
        except Exception as e:
            logger.error(f"关闭FAISS向量存储失败: {e}")

    # === 分片管理 ===

    async def _load_shard_metadata(self):
        """加载分片元数据"""
        try:
            if self.shard_metadata_file.exists():
                with open(self.shard_metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                for shard_data in metadata.get('shards', []):
                    shard_info = ShardInfo(
                        shard_id=shard_data['shard_id'],
                        index_file=Path(shard_data['index_file']),
                        metadata_file=Path(shard_data['metadata_file']),
                        summary_file=Path(shard_data['summary_file']),
                        created_at=datetime.fromisoformat(shard_data['created_at']),
                        last_updated=datetime.fromisoformat(shard_data['last_updated']),
                        document_count=shard_data['document_count'],
                        total_size_mb=shard_data['total_size_mb'],
                        tier=shard_data.get('tier', 'hot'),
                        is_active=shard_data.get('is_active', True),
                    )
                    self.shards[shard_info.shard_id] = shard_info
                
                logger.info(f"加载分片元数据: {len(self.shards)} 个分片")
                
        except Exception as e:
            logger.error(f"加载分片元数据失败: {e}")

    async def _save_shard_metadata(self):
        """保存分片元数据"""
        try:
            metadata = {
                'shards': [
                    {
                        'shard_id': shard.shard_id,
                        'index_file': str(shard.index_file),
                        'metadata_file': str(shard.metadata_file),
                        'summary_file': str(shard.summary_file),
                        'created_at': shard.created_at.isoformat(),
                        'last_updated': shard.last_updated.isoformat(),
                        'document_count': shard.document_count,
                        'total_size_mb': shard.total_size_mb,
                        'tier': shard.tier,
                        'is_active': shard.is_active,
                    }
                    for shard in self.shards.values()
                ],
                'updated_at': datetime.utcnow().isoformat(),
            }
            
            with open(self.shard_metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"保存分片元数据失败: {e}")

    async def _load_active_shard(self):
        """加载当前活跃分片"""
        try:
            # 查找当前最新的活跃分片
            active_shards = [s for s in self.shards.values() 
                           if s.is_active and s.tier == "hot"]
            
            if active_shards:
                # 按更新时间排序，选择最新的
                active_shards.sort(key=lambda x: x.last_updated, reverse=True)
                latest_shard = active_shards[0]
                
                # 检查是否需要创建新分片
                if latest_shard.document_count >= self.shard_size_limit:
                    await self.create_new_shard()
                else:
                    self.current_shard = latest_shard
                    await self._load_shard_index(latest_shard)
            else:
                # 创建第一个分片
                await self.create_new_shard()
                
        except Exception as e:
            logger.error(f"加载活跃分片失败: {e}")

    async def create_new_shard(self) -> bool:
        """创建新的分片"""
        try:
            # 生成分片ID
            current_quarter = f"{datetime.utcnow().year}_Q{(datetime.utcnow().month - 1) // 3 + 1}"
            shard_id = f"hot_{current_quarter}_{len(self.shards):03d}"
            
            # 分片文件路径
            shard_dir = self.hot_dir / shard_id
            shard_dir.mkdir(exist_ok=True)
            
            shard_info = ShardInfo(
                shard_id=shard_id,
                index_file=shard_dir / "vectors.faiss",
                metadata_file=shard_dir / "metadata.pkl",
                summary_file=shard_dir / "summaries.json",
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                document_count=0,
                total_size_mb=0.0,
                tier="hot",
                is_active=True,
            )
            
            # 创建FAISS索引
            index = await self._create_faiss_index()
            
            # 注册新分片
            self.shards[shard_id] = shard_info
            self.current_shard = shard_info
            self.active_indices[shard_id] = index
            
            logger.info(f"创建新分片: {shard_id}")
            return True
            
        except Exception as e:
            logger.error(f"创建新分片失败: {e}")
            return False

    async def _create_faiss_index(self) -> faiss.Index:
        """创建压缩FAISS索引"""
        from services.shared_executor_service import TaskType
        return await self._executor.submit(
            self._create_faiss_index_sync,
            task_type=TaskType.CPU
        )

    def _create_faiss_index_sync(self) -> faiss.Index:
        """同步创建FAISS索引"""
        # 使用压缩后的维度创建索引
        index_dim = self.compressed_dim
        
        if self.compression_method == "PQ":
            # Product Quantization压缩 - 使用更少的聚类中心和比特数
            m = min(4, index_dim // 4) if index_dim >= 16 else 2  # 子空间数量
            if index_dim % m != 0:
                m = 2  # 回退到安全值
            nbits = 4  # 减少比特数以降低训练数据需求 (2^4=16 vs 2^8=256)
            nlist = 10  # 使用更少的聚类中心，适合小数据集
            
            quantizer = faiss.IndexFlatIP(index_dim)
            index = faiss.IndexIVFPQ(quantizer, index_dim, nlist, m, nbits)
            
        elif self.compression_method == "SQ":
            # Scalar Quantization压缩
            nlist = 10  # 使用更少的聚类中心
            quantizer = faiss.IndexFlatIP(index_dim) 
            index = faiss.IndexIVFScalarQuantizer(quantizer, index_dim, nlist, faiss.SCALAR_8bit)
            
        else:
            # 默认使用简单的FlatL2索引，不需要训练
            index = faiss.IndexFlatL2(index_dim)
            
        return index

    # === 文档操作 ===

    @handle_errors(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.STORAGE_OPERATION,
        user_message="文档添加失败"
    )
    async def add_document(self, document: VectorDocument) -> bool:
        """添加文档到向量索引（压缩存储）"""
        try:
            if not self.current_shard:
                await self.create_new_shard()
            
            # 验证向量维度
            if document.embedding.shape[0] != self.vector_dim:
                logger.error(f"向量维度不匹配: 期望 {self.vector_dim}, 实际 {document.embedding.shape[0]}")
                return False
            
            # 压缩向量
            compressed_vector = await self._compress_vector(document.embedding)
            document.embedding = compressed_vector
            
            # 添加到当前分片
            index = self.active_indices[self.current_shard.shard_id]
            
            # 训练索引（如果需要）
            if hasattr(index, 'is_trained') and not index.is_trained:
                await self._train_index_if_needed(index, compressed_vector)
            
            # 添加到索引
            vector = compressed_vector.reshape(1, -1).astype(np.float32)
            from services.shared_executor_service import TaskType
            await self._executor.submit(
                lambda: index.add(vector),
                task_type=TaskType.CPU
            )
            
            # 缓存文档
            self.document_cache[document.id] = document
            
            # 更新分片信息
            self.current_shard.document_count += 1
            self.current_shard.last_updated = datetime.utcnow()
            
            # 检查是否需要创建新分片
            if self.current_shard.document_count >= self.shard_size_limit:
                await self._finalize_current_shard()
                await self.create_new_shard()
            
            logger.debug(f"添加文档到分片 {self.current_shard.shard_id}: {document.id}")
            return True
            
        except Exception as e:
            logger.error(f"添加文档失败 [{document.id}]: {e}")
            return False

    async def add_documents_batch(self, documents: List[VectorDocument]) -> int:
        """批量添加文档"""
        try:
            if not documents:
                return 0
            
            success_count = 0
            for doc in documents:
                if await self.add_document(doc):
                    success_count += 1
            
            logger.info(f"批量添加文档: {success_count}/{len(documents)} 成功")
            return success_count
            
        except Exception as e:
            logger.error(f"批量添加文档失败: {e}")
            return 0

    # === 搜索操作 ===

    @handle_errors(
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.SEARCH_OPERATION,
        user_message="向量搜索失败"
    )
    async def search_similar(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        search_tiers: List[str] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """多分片并行检索"""
        try:
            if search_tiers is None:
                search_tiers = ["hot", "warm"]  # 默认不搜索冷数据
            
            start_time = datetime.utcnow()
            
            # 压缩查询向量
            compressed_query = await self._compress_vector(query_vector)
            
            # 并行搜索多个分片
            search_tasks = []
            for shard in self.shards.values():
                if shard.tier in search_tiers and shard.is_active:
                    task = self._search_shard(shard, compressed_query, k * 2)
                    search_tasks.append(task)
            
            if not search_tasks:
                logger.warning("没有可搜索的分片")
                return []
            
            # 等待所有搜索完成
            shard_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # 合并结果
            all_results = []
            for result in shard_results:
                if isinstance(result, list):
                    all_results.extend(result)
            
            # 应用元数据过滤
            if filter_metadata:
                all_results = [r for r in all_results 
                             if self._match_metadata_filter(r.metadata, filter_metadata)]
            
            # 按分数排序并返回top-k
            all_results.sort(key=lambda x: x.score, reverse=True)
            final_results = all_results[:k]
            
            # 记录搜索性能
            search_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._record_search_time(search_time)
            
            logger.debug(f"多分片搜索完成: {len(final_results)} 结果, 耗时 {search_time:.2f}ms")
            return final_results
            
        except Exception as e:
            logger.error(f"向量搜索失败: {e}")
            return []

    async def _search_shard(
        self,
        shard: ShardInfo,
        query_vector: np.ndarray,
        k: int,
    ) -> List[SearchResult]:
        """搜索单个分片"""
        try:
            # 加载分片索引（如果未加载）
            if shard.shard_id not in self.active_indices:
                await self._load_shard_index(shard)
            
            index = self.active_indices.get(shard.shard_id)
            if not index or index.ntotal == 0:
                return []
            
            # 执行搜索
            query = query_vector.reshape(1, -1).astype(np.float32)
            from services.shared_executor_service import TaskType
            scores, indices = await self._executor.submit(
                lambda: index.search(query, min(k, index.ntotal)),
                task_type=TaskType.CPU
            )
            
            # 加载分片文档数据
            shard_docs = await self._load_shard_documents(shard)
            
            # 构建结果
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:  # 无效结果
                    continue
                
                # 查找对应文档
                doc_id = self._get_document_id_by_index(shard_docs, idx)
                if doc_id and doc_id in shard_docs:
                    doc = shard_docs[doc_id]
                    results.append(SearchResult(
                        id=doc.id,
                        summary=doc.summary,
                        score=float(score),
                        metadata=doc.metadata,
                        entity_id=doc.entity_id,
                        timestamp=doc.timestamp,
                        content_type=doc.content_type,
                        value_score=doc.value_score,
                    ))
            
            return results
            
        except Exception as e:
            logger.error(f"分片搜索失败 [{shard.shard_id}]: {e}")
            return []

    # === 压缩和优化 ===

    async def _compress_vector(self, vector: np.ndarray) -> np.ndarray:
        """向量压缩（384维→256维+float16）"""
        try:
            if len(vector) <= self.compressed_dim:
                return vector.astype(np.float16)
            
            # PCA降维（简化版，实际应该用训练好的变换矩阵）
            # 这里使用简单的截断作为示例
            compressed = vector[:self.compressed_dim]
            return compressed.astype(np.float16)
            
        except Exception as e:
            logger.error(f"向量压缩失败: {e}")
            return vector.astype(np.float16)

    async def _train_index_if_needed(self, index: faiss.Index, sample_vector: np.ndarray):
        """训练索引（如果需要）"""
        try:
            if not hasattr(index, 'is_trained') or index.is_trained:
                return
            
            # 生成训练数据 - 确保足够的训练样本
            nlist = getattr(index, 'nlist', 10)
            nbits = getattr(index, 'nbits', 4) if hasattr(index, 'nbits') else 4
            m = getattr(index, 'm', 1) if hasattr(index, 'm') else 1
            
            # 计算所需的最小训练样本数
            # PQ索引需要考虑多个子空间，每个子空间需要足够的样本
            min_for_nlist = nlist * 39  # FAISS建议至少39倍于聚类数
            min_for_pq = (2 ** nbits) * 39 * m  # 每个子空间都需要足够样本
            min_samples = max(min_for_nlist, min_for_pq, 1000)  # 使用更安全的基础值
            num_training_samples = min_samples
            training_data = []
            
            for _ in range(num_training_samples):
                noise = np.random.normal(0, 0.1, sample_vector.shape)
                training_vector = sample_vector + noise
                training_data.append(training_vector)
            
            training_vectors = np.vstack(training_data).astype(np.float32)
            
            # 执行训练
            from services.shared_executor_service import TaskType
            await self._executor.submit(
                lambda: index.train(training_vectors),
                task_type=TaskType.ML
            )
            
            logger.info(f"索引训练完成: {num_training_samples} 个样本")
            
        except Exception as e:
            logger.error(f"索引训练失败: {e}")

    # === 分片生命周期管理 ===

    async def _finalize_current_shard(self):
        """完成当前分片"""
        try:
            if not self.current_shard:
                return
            
            # 保存分片索引
            await self._save_shard_index(self.current_shard)
            
            # 保存分片文档
            await self._save_shard_documents(self.current_shard)
            
            # 标记为非活跃
            self.current_shard.is_active = False
            self.current_shard.last_updated = datetime.utcnow()
            
            logger.info(f"完成分片: {self.current_shard.shard_id}, 文档数: {self.current_shard.document_count}")
            
        except Exception as e:
            logger.error(f"完成分片失败: {e}")

    async def _save_current_shard(self):
        """保存当前分片"""
        if self.current_shard:
            await self._save_shard_index(self.current_shard)
            await self._save_shard_documents(self.current_shard)

    # === 数据持久化 ===

    async def _load_shard_index(self, shard: ShardInfo):
        """加载分片索引"""
        try:
            if shard.index_file.exists():
                from services.shared_executor_service import TaskType
                index = await self._executor.submit(
                    lambda: faiss.read_index(str(shard.index_file)),
                    task_type=TaskType.IO
                )
                self.active_indices[shard.shard_id] = index
                logger.debug(f"加载分片索引: {shard.shard_id}")
            else:
                # 创建新索引
                index = await self._create_faiss_index()
                self.active_indices[shard.shard_id] = index
                
        except Exception as e:
            logger.error(f"加载分片索引失败 [{shard.shard_id}]: {e}")

    async def _save_shard_index(self, shard: ShardInfo):
        """保存分片索引"""
        try:
            if shard.shard_id in self.active_indices:
                index = self.active_indices[shard.shard_id]
                from services.shared_executor_service import TaskType
                await self._executor.submit(
                    lambda: faiss.write_index(index, str(shard.index_file)),
                    task_type=TaskType.IO
                )
                logger.debug(f"保存分片索引: {shard.shard_id}")
                
        except Exception as e:
            logger.error(f"保存分片索引失败 [{shard.shard_id}]: {e}")

    async def _load_shard_documents(self, shard: ShardInfo) -> Dict[str, VectorDocument]:
        """加载分片文档数据"""
        try:
            if shard.metadata_file.exists():
                from services.shared_executor_service import TaskType
                return await self._executor.submit(
                    lambda: self._load_shard_documents_sync(shard),
                    task_type=TaskType.IO
                )
            return {}
            
        except Exception as e:
            logger.error(f"加载分片文档失败 [{shard.shard_id}]: {e}")
            return {}

    def _load_shard_documents_sync(self, shard: ShardInfo) -> Dict[str, VectorDocument]:
        """同步加载分片文档"""
        with open(shard.metadata_file, 'rb') as f:
            return pickle.load(f)

    async def _save_shard_documents(self, shard: ShardInfo):
        """保存分片文档数据"""
        try:
            # 获取分片相关文档
            shard_docs = {
                doc_id: doc for doc_id, doc in self.document_cache.items()
                # 这里可以添加分片文档的筛选逻辑
            }
            
            from services.shared_executor_service import TaskType
            await self._executor.submit(
                lambda: self._save_shard_documents_sync(shard, shard_docs),
                task_type=TaskType.IO
            )
            
        except Exception as e:
            logger.error(f"保存分片文档失败 [{shard.shard_id}]: {e}")

    def _save_shard_documents_sync(self, shard: ShardInfo, documents: Dict[str, VectorDocument]):
        """同步保存分片文档"""
        with open(shard.metadata_file, 'wb') as f:
            pickle.dump(documents, f, protocol=pickle.HIGHEST_PROTOCOL)

    # === 预加载热数据 ===

    async def _preload_hot_indices(self):
        """预加载热数据索引"""
        try:
            hot_shards = [s for s in self.shards.values() if s.tier == "hot"]
            for shard in hot_shards:
                await self._load_shard_index(shard)
            
            logger.info(f"预加载热数据索引: {len(hot_shards)} 个分片")
            
        except Exception as e:
            logger.error(f"预加载热数据失败: {e}")

    # === 工具方法 ===

    def _get_document_id_by_index(self, documents: Dict[str, VectorDocument], idx: int) -> Optional[str]:
        """根据索引获取文档ID"""
        # 简化实现，实际需要维护索引映射
        doc_list = list(documents.keys())
        return doc_list[idx] if 0 <= idx < len(doc_list) else None

    def _match_metadata_filter(self, metadata: Dict[str, Any], filter_criteria: Dict[str, Any]) -> bool:
        """检查元数据过滤条件"""
        for key, value in filter_criteria.items():
            if key not in metadata:
                return False
            
            if isinstance(value, list):
                if metadata[key] not in value:
                    return False
            elif isinstance(value, dict):
                if "min" in value and metadata[key] < value["min"]:
                    return False
                if "max" in value and metadata[key] > value["max"]:
                    return False
            else:
                if metadata[key] != value:
                    return False
        
        return True

    def _record_search_time(self, time_ms: float):
        """记录搜索时间"""
        self._search_times.append(time_ms)
        if len(self._search_times) > self._max_history:
            self._search_times = self._search_times[-self._max_history:]

    # === 性能监控 ===

    async def get_metrics(self) -> FAISSMetrics:
        """获取性能指标"""
        await self._update_metrics()
        return self._metrics

    async def _update_metrics(self):
        """更新性能指标"""
        try:
            self._metrics.total_documents = sum(s.document_count for s in self.shards.values())
            self._metrics.total_shards = len(self.shards)
            self._metrics.hot_shards = len([s for s in self.shards.values() if s.tier == "hot"])
            self._metrics.warm_shards = len([s for s in self.shards.values() if s.tier == "warm"])
            self._metrics.cold_shards = len([s for s in self.shards.values() if s.tier == "cold"])
            
            if self._search_times:
                self._metrics.avg_search_time_ms = np.mean(self._search_times)
            
            # 计算压缩比
            total_original_size = self._metrics.total_documents * self.vector_dim * 4  # float32
            total_compressed_size = self._metrics.total_documents * self.compressed_dim * 2  # float16
            if total_original_size > 0:
                self._metrics.compression_ratio = total_original_size / total_compressed_size
            
            # 存储大小
            self._metrics.storage_size_mb = sum(s.total_size_mb for s in self.shards.values())
            
            # 内存使用
            import psutil
            process = psutil.Process()
            self._metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024
            
            self._metrics.last_updated = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"更新指标失败: {e}")


# === 服务单例管理 ===

_faiss_vector_store: Optional[FAISSVectorStore] = None

async def get_faiss_vector_store() -> FAISSVectorStore:
    """获取FAISS向量存储实例（单例模式）"""
    global _faiss_vector_store
    if _faiss_vector_store is None:
        # 从配置获取向量维度和其他参数
        from core.service_facade import get_database_config_manager
        config_manager = get_database_config_manager()
        
        _faiss_vector_store = FAISSVectorStore(
            vector_dim=config_manager.get_config_value("vector", "vector_dimension", default=384),
            compressed_dim=config_manager.get_config_value("vector", "compressed_dimension", default=256),
            shard_size_limit=config_manager.get_config_value("vector", "shard_size_limit", default=100000),
            compression_method=config_manager.get_config_value("vector", "compression_method", default="PQ"),
        )
        if not await _faiss_vector_store.initialize():
            raise RuntimeError("FAISS向量存储初始化失败")
    return _faiss_vector_store

async def cleanup_faiss_vector_store():
    """清理FAISS向量存储"""
    global _faiss_vector_store
    if _faiss_vector_store:
        await _faiss_vector_store.close()
        _faiss_vector_store = None