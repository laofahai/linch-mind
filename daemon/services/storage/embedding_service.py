#!/usr/bin/env python3
"""
Embedding模型服务 - 文本向量化和语义理解
集成sentence-transformers提供统一的文本嵌入接口
"""

import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingMetrics:
    """嵌入服务性能指标"""

    total_embeddings: int
    model_name: str
    model_dimension: int
    avg_encoding_time_ms: float
    cache_hit_rate: float
    memory_usage_mb: float
    last_updated: datetime


class EmbeddingService:
    """Embedding模型服务 - 统一的文本向量化接口"""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        cache_dir: Optional[Path] = None,
        max_workers: int = 2,
        enable_cache: bool = True,
    ):
        self.model_name = model_name
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.max_workers = max_workers
        self.enable_cache = enable_cache

        # 模型和线程池
        self.model = None
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

        # 缓存管理
        self._embedding_cache: Dict[str, np.ndarray] = {}
        self._cache_file = None
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._cache_file = (
                self.cache_dir / f"embedding_cache_{model_name.replace('/', '_')}.json"
            )

        # 性能监控
        self._encoding_times: List[float] = []
        self._max_history = 100
        self._cache_hits = 0
        self._cache_misses = 0

        self._metrics = EmbeddingMetrics(
            total_embeddings=0,
            model_name=model_name,
            model_dimension=0,
            avg_encoding_time_ms=0.0,
            cache_hit_rate=0.0,
            memory_usage_mb=0.0,
            last_updated=datetime.utcnow(),
        )

    async def initialize(self) -> bool:
        """初始化嵌入服务"""
        try:
            # 在线程池中加载模型，避免阻塞主线程
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(self._executor, self._load_model)

            if self.model is None:
                logger.error("模型加载失败")
                return False

            # 获取模型维度
            test_embedding = self.model.encode("test")
            self._metrics.model_dimension = len(test_embedding)

            # 加载缓存
            if self.enable_cache:
                await self._load_cache()

            logger.info(
                f"嵌入服务初始化完成: 模型 {self.model_name}, 维度 {self._metrics.model_dimension}"
            )
            return True

        except Exception as e:
            logger.error(f"嵌入服务初始化失败: {e}")
            return False

    def _load_model(self):
        """同步加载模型"""
        try:
            from sentence_transformers import SentenceTransformer

            logger.info(f"加载嵌入模型: {self.model_name}")
            model = SentenceTransformer(self.model_name)
            logger.info("模型加载完成")
            return model

        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            return None

    async def close(self):
        """关闭嵌入服务"""
        try:
            # 保存缓存
            if self.enable_cache:
                await self._save_cache()

            # 关闭线程池
            self._executor.shutdown(wait=True)

            logger.info("嵌入服务已关闭")

        except Exception as e:
            logger.error(f"关闭嵌入服务失败: {e}")

    # === 文本嵌入 ===

    async def encode_text(self, text: str) -> np.ndarray:
        """编码单个文本为向量"""
        if not text or not text.strip():
            logger.warning("空文本，返回零向量")
            return np.zeros(self._metrics.model_dimension, dtype=np.float32)

        # 检查缓存
        cache_key = self._get_cache_key(text)
        if self.enable_cache and cache_key in self._embedding_cache:
            self._cache_hits += 1
            return self._embedding_cache[cache_key]

        try:
            start_time = datetime.utcnow()

            # 在线程池中编码
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                self._executor, self.model.encode, text.strip()
            )

            # 转换为numpy数组并确保数据类型
            embedding = np.array(embedding, dtype=np.float32)

            # 记录性能
            encoding_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._record_encoding_time(encoding_time)

            # 缓存结果
            if self.enable_cache:
                self._embedding_cache[cache_key] = embedding
                self._cache_misses += 1

            self._metrics.total_embeddings += 1

            logger.debug(f"文本编码完成: {len(text)} 字符, 耗时 {encoding_time:.2f}ms")
            return embedding

        except Exception as e:
            logger.error(f"文本编码失败: {e}")
            return np.zeros(self._metrics.model_dimension, dtype=np.float32)

    async def encode_texts(self, texts: List[str]) -> np.ndarray:
        """批量编码文本为向量矩阵"""
        if not texts:
            return np.array([], dtype=np.float32).reshape(
                0, self._metrics.model_dimension
            )

        try:
            # 过滤空文本
            valid_texts = [text.strip() for text in texts if text and text.strip()]
            if not valid_texts:
                logger.warning("所有文本都为空")
                return np.zeros(
                    (len(texts), self._metrics.model_dimension), dtype=np.float32
                )

            # 检查缓存
            cached_embeddings = {}
            uncached_texts = []
            uncached_indices = []

            if self.enable_cache:
                for i, text in enumerate(valid_texts):
                    cache_key = self._get_cache_key(text)
                    if cache_key in self._embedding_cache:
                        cached_embeddings[i] = self._embedding_cache[cache_key]
                        self._cache_hits += 1
                    else:
                        uncached_texts.append(text)
                        uncached_indices.append(i)
                        self._cache_misses += 1
            else:
                uncached_texts = valid_texts
                uncached_indices = list(range(len(valid_texts)))

            # 批量编码未缓存的文本
            if uncached_texts:
                start_time = datetime.utcnow()

                loop = asyncio.get_event_loop()
                new_embeddings = await loop.run_in_executor(
                    self._executor, self.model.encode, uncached_texts
                )

                encoding_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                self._record_encoding_time(encoding_time / len(uncached_texts))

                # 转换为numpy数组
                new_embeddings = np.array(new_embeddings, dtype=np.float32)

                # 缓存新结果
                if self.enable_cache:
                    for i, text in enumerate(uncached_texts):
                        cache_key = self._get_cache_key(text)
                        self._embedding_cache[cache_key] = new_embeddings[i]

                # 合并结果
                for i, uncached_idx in enumerate(uncached_indices):
                    cached_embeddings[uncached_idx] = new_embeddings[i]

            # 构建最终结果矩阵
            result_embeddings = np.zeros(
                (len(valid_texts), self._metrics.model_dimension), dtype=np.float32
            )
            for i in range(len(valid_texts)):
                if i in cached_embeddings:
                    result_embeddings[i] = cached_embeddings[i]

            self._metrics.total_embeddings += len(valid_texts)

            logger.debug(f"批量编码完成: {len(valid_texts)} 个文本")
            return result_embeddings

        except Exception as e:
            logger.error(f"批量编码失败: {e}")
            return np.zeros(
                (len(texts), self._metrics.model_dimension), dtype=np.float32
            )

    # === 相似性计算 ===

    async def compute_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似性"""
        try:
            embedding1 = await self.encode_text(text1)
            embedding2 = await self.encode_text(text2)

            # 计算余弦相似性
            similarity = np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )

            return float(similarity)

        except Exception as e:
            logger.error(f"相似性计算失败: {e}")
            return 0.0

    async def find_most_similar(
        self, query: str, candidates: List[str], top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """找到最相似的文本"""
        try:
            if not candidates:
                return []

            # 编码查询文本
            query_embedding = await self.encode_text(query)

            # 批量编码候选文本
            candidate_embeddings = await self.encode_texts(candidates)

            # 计算相似性分数
            similarities = []
            for i, candidate_embedding in enumerate(candidate_embeddings):
                similarity = np.dot(query_embedding, candidate_embedding) / (
                    np.linalg.norm(query_embedding)
                    * np.linalg.norm(candidate_embedding)
                )
                similarities.append((candidates[i], float(similarity)))

            # 排序并返回top-k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]

        except Exception as e:
            logger.error(f"相似性搜索失败: {e}")
            return []

    # === 缓存管理 ===

    def _get_cache_key(self, text: str) -> str:
        """生成缓存键"""
        import hashlib

        return hashlib.md5(text.encode("utf-8")).hexdigest()

    async def _load_cache(self):
        """加载嵌入缓存"""
        if not self._cache_file or not self._cache_file.exists():
            return

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self._executor, self._load_cache_sync)

            logger.info(f"加载嵌入缓存: {len(self._embedding_cache)} 条记录")

        except Exception as e:
            logger.error(f"加载缓存失败: {e}")

    def _load_cache_sync(self):
        """同步加载缓存"""
        with open(self._cache_file, "r", encoding="utf-8") as f:
            cache_data = json.load(f)

            for key, embedding_list in cache_data.items():
                self._embedding_cache[key] = np.array(embedding_list, dtype=np.float32)

    async def _save_cache(self):
        """保存嵌入缓存"""
        if not self._cache_file or not self._embedding_cache:
            return

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self._executor, self._save_cache_sync)

            logger.debug(f"保存嵌入缓存: {len(self._embedding_cache)} 条记录")

        except Exception as e:
            logger.error(f"保存缓存失败: {e}")

    def _save_cache_sync(self):
        """同步保存缓存"""
        # 转换numpy数组为列表用于JSON序列化
        cache_data = {}
        for key, embedding in self._embedding_cache.items():
            cache_data[key] = embedding.tolist()

        with open(self._cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)

    async def clear_cache(self):
        """清空缓存"""
        self._embedding_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0

        if self._cache_file and self._cache_file.exists():
            self._cache_file.unlink()

        logger.info("嵌入缓存已清空")

    # === 性能监控 ===

    async def get_metrics(self) -> EmbeddingMetrics:
        """获取嵌入服务性能指标"""
        await self._update_metrics()
        return self._metrics

    async def _update_metrics(self):
        """更新性能指标"""
        try:
            import psutil

            # 计算平均编码时间
            if self._encoding_times:
                self._metrics.avg_encoding_time_ms = np.mean(self._encoding_times)

            # 计算缓存命中率
            total_requests = self._cache_hits + self._cache_misses
            if total_requests > 0:
                self._metrics.cache_hit_rate = self._cache_hits / total_requests

            # 内存使用情况（简化估算）
            process = psutil.Process()
            self._metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024

            self._metrics.last_updated = datetime.utcnow()

        except Exception as e:
            logger.error(f"更新指标失败: {e}")

    def _record_encoding_time(self, time_ms: float):
        """记录编码时间"""
        self._encoding_times.append(time_ms)
        if len(self._encoding_times) > self._max_history:
            self._encoding_times = self._encoding_times[-self._max_history :]

    # === 工具方法 ===

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型基本信息"""
        return {
            "model_name": self.model_name,
            "dimension": self._metrics.model_dimension,
            "max_sequence_length": (
                getattr(self.model, "max_seq_length", 512) if self.model else 512
            ),
            "cache_enabled": self.enable_cache,
            "cache_size": len(self._embedding_cache),
        }

    async def warmup(self, sample_texts: Optional[List[str]] = None):
        """预热模型（预编码一些样本文本）"""
        if not sample_texts:
            sample_texts = [
                "这是一个测试文本",
                "Hello, this is a test",
                "Sample document for embedding",
                "人工智能和机器学习",
            ]

        try:
            logger.info("开始模型预热...")
            start_time = datetime.utcnow()

            await self.encode_texts(sample_texts)

            warmup_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"模型预热完成，耗时 {warmup_time:.2f} 秒")

        except Exception as e:
            logger.error(f"模型预热失败: {e}")


# 全局嵌入服务实例
_embedding_service: Optional[EmbeddingService] = None


async def get_embedding_service() -> EmbeddingService:
    """获取嵌入服务实例（单例模式）"""
    global _embedding_service
    if _embedding_service is None:
        from config.core_config import get_storage_config

        storage_config = get_storage_config()

        _embedding_service = EmbeddingService(
            model_name=storage_config.embedding_model_name,
            cache_dir=Path(storage_config.data_directory) / "embeddings",
            max_workers=storage_config.embedding_max_workers,
            enable_cache=storage_config.embedding_cache_enabled,
        )
        await _embedding_service.initialize()

    return _embedding_service


async def cleanup_embedding_service():
    """清理嵌入服务"""
    global _embedding_service
    if _embedding_service:
        await _embedding_service.close()
        _embedding_service = None
