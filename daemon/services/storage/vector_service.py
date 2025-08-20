#!/usr/bin/env python3
"""
FAISS向量搜索服务 - 语义搜索和内容相似性计算
支持10GB-50GB向量数据的高性能搜索
"""

import asyncio
import logging
import pickle
from services.shared_executor_service import get_shared_executor_service, TaskType
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import faiss
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class VectorMetrics:
    """向量数据库性能指标"""

    total_vectors: int
    dimension: int
    index_type: str
    memory_usage_mb: float
    search_time_avg_ms: float
    last_updated: datetime


@dataclass
class VectorDocument:
    """向量文档"""

    id: str
    content: str
    embedding: np.ndarray
    metadata: Dict[str, Any]
    entity_id: Optional[str] = None


@dataclass
class SearchResult:
    """搜索结果"""

    id: str
    content: str
    score: float
    metadata: Dict[str, Any]
    entity_id: Optional[str] = None


class VectorService:
    """FAISS向量搜索服务 - 语义搜索的核心引擎"""

    def __init__(
        self,
        data_dir: Path,
        dimension: int = 384,  # sentence-transformers默认维度
        index_type: str = "IVF",
        max_workers: int = 4,
    ):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 向量参数
        self.dimension = dimension
        self.index_type = index_type

        # FAISS索引
        self.index: Optional[faiss.Index] = None
        self.index_file = self.data_dir / "vector_index.faiss"

        # 文档映射 - ID到文档的映射
        self.id_to_doc: Dict[str, VectorDocument] = {}
        self.metadata_file = self.data_dir / "vector_metadata.pkl"

        # 内部ID映射 - FAISS内部ID到文档ID的映射
        self.internal_to_doc_id: Dict[int, str] = {}
        self.doc_id_to_internal: Dict[str, int] = {}
        self.next_internal_id = 0

        # 性能优化
        self.max_workers = max_workers
        self._executor = get_shared_executor_service()

        # 统计信息
        self._metrics = VectorMetrics(
            total_vectors=0,
            dimension=dimension,
            index_type=index_type,
            memory_usage_mb=0.0,
            search_time_avg_ms=0.0,
            last_updated=datetime.utcnow(),
        )

        # 搜索性能记录
        self._search_times: List[float] = []
        self._max_search_history = 100

    async def initialize(self) -> bool:
        """初始化向量服务"""
        try:
            # 尝试加载现有索引
            if self.index_file.exists() and self.metadata_file.exists():
                await self._load_index()
                logger.info(
                    f"加载向量索引: {self._metrics.total_vectors} 向量, "
                    f"维度 {self._metrics.dimension}"
                )
            else:
                await self._create_index()
                logger.info(
                    f"创建新向量索引: 维度 {self.dimension}, 类型 {self.index_type}"
                )

            await self._update_metrics()
            return True

        except Exception as e:
            logger.error(f"向量服务初始化失败: {e}")
            return False

    async def close(self):
        """关闭向量服务"""
        try:
            await self.save_index()
            self._executor.shutdown(wait=True)
            logger.info("向量服务已关闭")
        except Exception as e:
            logger.error(f"向量服务关闭失败: {e}")

    # === 索引管理 ===

    async def _create_index(self):
        """创建FAISS索引"""
        loop = asyncio.get_event_loop()
        self.index = await loop.run_in_executor(self._executor, self._create_index_sync)

    def _create_index_sync(self) -> faiss.Index:
        """同步创建索引"""
        if self.index_type == "Flat":
            # 暴力搜索索引 - 精确但慢
            index = faiss.IndexFlatIP(self.dimension)  # 内积相似度
        elif self.index_type == "IVF":
            # 倒排文件索引 - 平衡精度和速度
            nlist = 100  # 聚类中心数量
            quantizer = faiss.IndexFlatIP(self.dimension)
            index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
        elif self.index_type == "HNSW":
            # 分层导航小世界图 - 快速搜索
            M = 32  # 连接数
            index = faiss.IndexHNSWFlat(self.dimension, M)
        else:
            logger.warning(f"不支持的索引类型 {self.index_type}, 使用默认Flat索引")
            index = faiss.IndexFlatIP(self.dimension)

        return index

    async def _train_ivf_index_if_needed(self, sample_vector: np.ndarray):
        """训练IVF索引（如果需要）"""
        try:
            if not hasattr(self.index, "is_trained") or self.index.is_trained:
                return

            # IVF索引需要训练数据，使用当前向量作为训练样本
            # 为了快速训练，创建一些随机样本
            import numpy as np

            # 生成训练数据（使用样本向量 + 一些随机变化）
            num_training_samples = max(100, self.index.nlist * 2)  # 至少2倍于聚类中心数
            training_data = []

            for _ in range(num_training_samples):
                # 在原向量基础上添加小的随机扰动
                noise = np.random.normal(0, 0.1, sample_vector.shape)
                training_vector = sample_vector + noise
                training_data.append(training_vector)

            training_vectors = np.vstack(training_data).astype(np.float32)

            # 执行训练
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor, self.index.train, training_vectors
            )

            logger.info(f"IVF索引训练完成: {num_training_samples} 个训练样本")

        except Exception as e:
            logger.error(f"IVF索引训练失败: {e}")
            # 失败时切换到Flat索引
            logger.info("切换到Flat索引作为备选方案")
            self.index = faiss.IndexFlatIP(self.dimension)

    async def _load_index(self):
        """加载索引和元数据"""
        loop = asyncio.get_event_loop()

        # 加载FAISS索引
        self.index = await loop.run_in_executor(
            self._executor, faiss.read_index, str(self.index_file)
        )

        # 加载元数据
        await loop.run_in_executor(self._executor, self._load_metadata_sync)

    def _load_metadata_sync(self):
        """同步加载元数据"""
        with open(self.metadata_file, "rb") as f:
            metadata = pickle.load(f)
            self.id_to_doc = metadata["id_to_doc"]
            self.internal_to_doc_id = metadata["internal_to_doc_id"]
            self.doc_id_to_internal = metadata["doc_id_to_internal"]
            self.next_internal_id = metadata["next_internal_id"]

    async def save_index(self) -> bool:
        """保存索引和元数据"""
        try:
            if self.index is None:
                logger.warning("索引为空，跳过保存")
                return False

            loop = asyncio.get_event_loop()

            # 保存FAISS索引
            await loop.run_in_executor(
                self._executor, faiss.write_index, self.index, str(self.index_file)
            )

            # 保存元数据
            await loop.run_in_executor(self._executor, self._save_metadata_sync)

            logger.info(f"向量索引已保存: {self.index_file}")
            return True

        except Exception as e:
            logger.error(f"保存索引失败: {e}")
            return False

    def _save_metadata_sync(self):
        """同步保存元数据"""
        metadata = {
            "id_to_doc": self.id_to_doc,
            "internal_to_doc_id": self.internal_to_doc_id,
            "doc_id_to_internal": self.doc_id_to_internal,
            "next_internal_id": self.next_internal_id,
        }

        with open(self.metadata_file, "wb") as f:
            pickle.dump(metadata, f, protocol=pickle.HIGHEST_PROTOCOL)

    # === 文档操作 ===

    async def add_document(self, document: VectorDocument) -> bool:
        """添加文档到向量索引"""
        try:
            if self.index is None:
                logger.error("索引未初始化")
                return False

            # 验证向量维度
            if document.embedding.shape[0] != self.dimension:
                logger.error(
                    f"向量维度不匹配: 期望 {self.dimension}, 实际 {document.embedding.shape[0]}"
                )
                return False

            # 准备向量数据
            vector = document.embedding.reshape(1, -1).astype(np.float32)

            # 检查IVF索引是否需要训练
            if hasattr(self.index, "is_trained") and not self.index.is_trained:
                await self._train_ivf_index_if_needed(vector)

            # 添加到索引
            internal_id = self.next_internal_id

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self._executor, self.index.add, vector)

            # 更新映射
            self.internal_to_doc_id[internal_id] = document.id
            self.doc_id_to_internal[document.id] = internal_id
            self.id_to_doc[document.id] = document
            self.next_internal_id += 1

            logger.debug(f"添加文档到向量索引: {document.id}")
            return True

        except Exception as e:
            logger.error(f"添加文档失败 [{document.id}]: {e}")
            return False

    async def add_documents_batch(self, documents: List[VectorDocument]) -> int:
        """批量添加文档"""
        try:
            if self.index is None or not documents:
                return 0

            # 准备批量向量数据
            vectors = []
            valid_docs = []

            for doc in documents:
                if doc.embedding.shape[0] == self.dimension:
                    vectors.append(doc.embedding.astype(np.float32))
                    valid_docs.append(doc)
                else:
                    logger.warning(f"跳过维度不匹配的文档: {doc.id}")

            if not vectors:
                return 0

            # 转换为numpy数组
            vectors_array = np.vstack(vectors)

            # 批量添加到索引
            start_internal_id = self.next_internal_id

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self._executor, self.index.add, vectors_array)

            # 更新映射
            for i, doc in enumerate(valid_docs):
                internal_id = start_internal_id + i
                self.internal_to_doc_id[internal_id] = doc.id
                self.doc_id_to_internal[doc.id] = internal_id
                self.id_to_doc[doc.id] = doc

            self.next_internal_id += len(valid_docs)

            logger.info(f"批量添加文档: {len(valid_docs)} 个")
            return len(valid_docs)

        except Exception as e:
            logger.error(f"批量添加文档失败: {e}")
            return 0

    async def remove_document(self, document_id: str) -> bool:
        """删除文档（标记删除，FAISS不支持真正删除）"""
        try:
            if document_id not in self.id_to_doc:
                logger.warning(f"文档不存在: {document_id}")
                return False

            # 从映射中删除
            internal_id = self.doc_id_to_internal.pop(document_id)
            self.internal_to_doc_id.pop(internal_id)
            self.id_to_doc.pop(document_id)

            logger.debug(f"删除文档: {document_id}")
            return True

        except Exception as e:
            logger.error(f"删除文档失败 [{document_id}]: {e}")
            return False

    async def get_document(self, document_id: str) -> Optional[VectorDocument]:
        """获取文档"""
        return self.id_to_doc.get(document_id)

    # === 搜索操作 ===

    async def search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """向量相似性搜索"""
        try:
            if self.index is None or self.index.ntotal == 0:
                logger.warning("索引为空")
                return []

            # 验证查询向量维度
            if query_vector.shape[0] != self.dimension:
                logger.error(
                    f"查询向量维度不匹配: 期望 {self.dimension}, 实际 {query_vector.shape[0]}"
                )
                return []

            # 记录搜索开始时间
            start_time = datetime.utcnow()

            # 准备查询向量
            query = query_vector.reshape(1, -1).astype(np.float32)

            # 执行搜索
            loop = asyncio.get_event_loop()
            scores, indices = await loop.run_in_executor(
                self._executor,
                self.index.search,
                query,
                min(k * 2, self.index.ntotal),  # 搜索更多结果用于过滤
            )

            # 记录搜索时间
            search_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._record_search_time(search_time)

            # 转换结果
            results = []
            for _i, (score, internal_id) in enumerate(zip(scores[0], indices[0])):
                if internal_id == -1:  # FAISS返回-1表示无效结果
                    continue

                doc_id = self.internal_to_doc_id.get(internal_id)
                if not doc_id or doc_id not in self.id_to_doc:
                    continue  # 已删除的文档

                doc = self.id_to_doc[doc_id]

                # 应用元数据过滤
                if filter_metadata and not self._match_metadata_filter(
                    doc.metadata, filter_metadata
                ):
                    continue

                results.append(
                    SearchResult(
                        id=doc.id,
                        content=doc.content,
                        score=float(score),
                        metadata=doc.metadata,
                        entity_id=doc.entity_id,
                    )
                )

                if len(results) >= k:
                    break

            logger.debug(f"向量搜索完成: {len(results)} 结果, 耗时 {search_time:.2f}ms")
            return results

        except Exception as e:
            logger.error(f"向量搜索失败: {e}")
            return []

    async def search_by_document(
        self, document_id: str, k: int = 10, exclude_self: bool = True
    ) -> List[SearchResult]:
        """基于文档的相似性搜索"""
        doc = self.id_to_doc.get(document_id)
        if not doc:
            logger.warning(f"文档不存在: {document_id}")
            return []

        results = await self.search(doc.embedding, k + (1 if exclude_self else 0))

        if exclude_self:
            results = [r for r in results if r.id != document_id][:k]

        return results

    async def search_by_text(
        self, query_text: str, k: int = 10, embedding_model: Optional[Any] = None
    ) -> List[SearchResult]:
        """基于文本的语义搜索"""
        if not embedding_model:
            logger.error("需要提供embedding模型进行文本搜索")
            return []

        try:
            # 生成查询向量
            loop = asyncio.get_event_loop()
            query_vector = await loop.run_in_executor(
                self._executor, embedding_model.encode, query_text
            )

            return await self.search(query_vector, k)

        except Exception as e:
            logger.error(f"文本搜索失败: {e}")
            return []

    # === 高级搜索功能 ===

    async def find_similar_entities(
        self, entity_id: str, k: int = 10
    ) -> List[SearchResult]:
        """查找相似实体"""
        # 收集实体相关的所有文档
        entity_docs = [
            doc for doc in self.id_to_doc.values() if doc.entity_id == entity_id
        ]

        if not entity_docs:
            logger.warning(f"实体无关联文档: {entity_id}")
            return []

        # 计算实体向量（平均向量）
        entity_vectors = [doc.embedding for doc in entity_docs]
        entity_vector = np.mean(entity_vectors, axis=0)

        # 搜索相似文档
        all_results = await self.search(entity_vector, k * 3)

        # 按实体分组并计算实体相似度
        entity_scores = {}
        entity_docs_count = {}

        for result in all_results:
            if result.entity_id and result.entity_id != entity_id:
                if result.entity_id not in entity_scores:
                    entity_scores[result.entity_id] = 0
                    entity_docs_count[result.entity_id] = 0

                entity_scores[result.entity_id] += result.score
                entity_docs_count[result.entity_id] += 1

        # 计算平均分数并排序
        avg_scores = [
            (eid, score / entity_docs_count[eid])
            for eid, score in entity_scores.items()
        ]
        avg_scores.sort(key=lambda x: x[1], reverse=True)

        # 转换为搜索结果
        results = []
        for entity_id, avg_score in avg_scores[:k]:
            # 找到该实体的最佳文档
            entity_results = [r for r in all_results if r.entity_id == entity_id]
            if entity_results:
                best_result = max(entity_results, key=lambda x: x.score)
                best_result.score = avg_score  # 使用实体平均分数
                results.append(best_result)

        return results

    async def cluster_documents(
        self, k_clusters: int = 10, max_documents: Optional[int] = None
    ) -> Dict[int, List[str]]:
        """文档聚类"""
        try:
            if self.index is None or self.index.ntotal == 0:
                return {}

            # 获取所有向量
            doc_ids = list(self.id_to_doc.keys())
            if max_documents:
                doc_ids = doc_ids[:max_documents]

            vectors = []
            valid_doc_ids = []

            for doc_id in doc_ids:
                doc = self.id_to_doc[doc_id]
                vectors.append(doc.embedding)
                valid_doc_ids.append(doc_id)

            if len(vectors) < k_clusters:
                logger.warning(f"文档数量 {len(vectors)} 少于聚类数 {k_clusters}")
                return {0: valid_doc_ids}

            vectors_array = np.vstack(vectors).astype(np.float32)

            # 使用FAISS进行K-means聚类
            loop = asyncio.get_event_loop()
            kmeans = await loop.run_in_executor(
                self._executor, self._kmeans_clustering, vectors_array, k_clusters
            )

            # 分配文档到聚类
            _, cluster_assignments = kmeans.index.search(vectors_array, 1)

            clusters = {}
            for doc_id, cluster_id in zip(valid_doc_ids, cluster_assignments.flatten()):
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                clusters[cluster_id].append(doc_id)

            logger.info(f"文档聚类完成: {len(clusters)} 个聚类")
            return clusters

        except Exception as e:
            logger.error(f"文档聚类失败: {e}")
            return {}

    def _kmeans_clustering(self, vectors: np.ndarray, k: int) -> faiss.Kmeans:
        """K-means聚类"""
        kmeans = faiss.Kmeans(self.dimension, k, niter=20, verbose=False)
        kmeans.train(vectors)
        return kmeans

    # === 性能监控 ===

    async def get_metrics(self) -> VectorMetrics:
        """获取向量数据库性能指标"""
        await self._update_metrics()
        return self._metrics

    async def _update_metrics(self):
        """更新性能指标"""
        try:
            import psutil

            self._metrics.total_vectors = len(self.id_to_doc)

            # 计算平均搜索时间
            if self._search_times:
                self._metrics.search_time_avg_ms = np.mean(self._search_times)

            # 内存使用情况（简化估算）
            process = psutil.Process()
            self._metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024

            self._metrics.last_updated = datetime.utcnow()

        except Exception as e:
            logger.error(f"更新指标失败: {e}")

    def _record_search_time(self, time_ms: float):
        """记录搜索时间"""
        self._search_times.append(time_ms)
        if len(self._search_times) > self._max_search_history:
            self._search_times = self._search_times[-self._max_search_history :]

    # === 工具方法 ===

    def _match_metadata_filter(
        self, metadata: Dict[str, Any], filter_criteria: Dict[str, Any]
    ) -> bool:
        """检查元数据是否匹配过滤条件"""
        for key, value in filter_criteria.items():
            if key not in metadata:
                return False

            if isinstance(value, list):
                # 列表过滤 - metadata值必须在列表中
                if metadata[key] not in value:
                    return False
            elif isinstance(value, dict):
                # 范围过滤 - 支持 {'min': x, 'max': y}
                if "min" in value and metadata[key] < value["min"]:
                    return False
                if "max" in value and metadata[key] > value["max"]:
                    return False
            else:
                # 精确匹配
                if metadata[key] != value:
                    return False

        return True

    async def rebuild_index(self, new_index_type: Optional[str] = None) -> bool:
        """重建索引（用于优化或更改索引类型）"""
        try:
            if not self.id_to_doc:
                logger.warning("没有文档数据，跳过重建")
                return True

            # 保存当前数据
            old_docs = list(self.id_to_doc.values())

            # 更新索引类型
            if new_index_type:
                self.index_type = new_index_type
                self._metrics.index_type = new_index_type

            # 重新创建索引
            await self._create_index()

            # 清空映射
            self.id_to_doc.clear()
            self.internal_to_doc_id.clear()
            self.doc_id_to_internal.clear()
            self.next_internal_id = 0

            # 重新添加所有文档
            added_count = await self.add_documents_batch(old_docs)

            logger.info(f"索引重建完成: {added_count} 个文档")
            return added_count == len(old_docs)

        except Exception as e:
            logger.error(f"重建索引失败: {e}")
            return False


# === 服务管理函数 ===

# 全局服务实例
_vector_service: Optional[VectorService] = None


# 已删除：get_vector_service() - 违反ServiceFacade统一服务获取铁律
# 请使用：from core.service_facade import get_service; get_service(VectorService)


async def cleanup_vector_service():
    """清理向量服务"""
    global _vector_service
    if _vector_service:
        try:
            await _vector_service.save_index()
            logger.info("向量服务已清理")
        except Exception as e:
            logger.error(f"向量服务清理失败: {e}")
        finally:
            _vector_service = None


# ServiceFacade现在负责管理服务单例，但保留向后兼容的函数
