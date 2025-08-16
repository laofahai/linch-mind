#!/usr/bin/env python3
"""
统一搜索服务 - 消除14个重复搜索实现
整合向量搜索、图搜索、文本搜索为统一接口
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from core.service_facade import get_service

logger = logging.getLogger(__name__)


class SearchType(Enum):
    """搜索类型枚举"""
    SEMANTIC = "semantic"      # 语义搜索 (向量)
    GRAPH = "graph"           # 图遍历搜索
    TEXT = "text"             # 全文搜索  
    HYBRID = "hybrid"         # 混合搜索
    SIMILAR = "similar"       # 相似性搜索
    PATH = "path"             # 路径搜索


@dataclass
class SearchQuery:
    """统一搜索查询对象"""
    query: str                                    # 查询内容
    search_type: SearchType                       # 搜索类型
    limit: int = 10                              # 结果数量限制
    filters: Dict[str, Any] = field(default_factory=dict)  # 过滤条件
    options: Dict[str, Any] = field(default_factory=dict)  # 搜索选项
    
    # 图搜索专用参数
    start_entity_id: Optional[str] = None         # 起始实体ID
    target_entity_id: Optional[str] = None        # 目标实体ID (路径搜索)
    max_depth: int = 1                           # 最大搜索深度
    relationship_filter: Optional[List[str]] = None  # 关系类型过滤
    
    # 向量搜索专用参数  
    similarity_threshold: float = 0.0             # 相似度阈值
    include_metadata: bool = True                 # 是否包含元数据


@dataclass
class SearchResult:
    """统一搜索结果对象"""
    entity_id: str                               # 实体ID
    score: float                                 # 相关性分数
    content: str                                 # 内容
    entity_type: str = "unknown"                 # 实体类型
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
    path: Optional[List[str]] = None             # 路径信息 (图搜索)
    highlights: List[str] = field(default_factory=list)     # 高亮片段
    source: str = "unified"                      # 结果来源


@dataclass
class SearchStats:
    """搜索统计信息"""
    total_searches: int = 0
    semantic_searches: int = 0
    graph_searches: int = 0
    text_searches: int = 0
    avg_search_time_ms: float = 0.0
    last_search_time: Optional[datetime] = None


class UnifiedSearchService:
    """统一搜索服务 - 消除14个重复搜索实现"""
    
    def __init__(self):
        self.stats = SearchStats()
        self._search_times: List[float] = []
        self._max_history = 100
        
        # 延迟加载底层搜索引擎
        self._vector_service = None
        self._graph_service = None 
        self._storage_service = None
        self._embedding_service = None
        
        logger.info("🔍 UnifiedSearchService 初始化")
    
    async def initialize(self):
        """初始化搜索服务"""
        try:
            # 尝试获取各个底层服务
            try:
                from services.storage.vector_service import VectorService
                self._vector_service = get_service(VectorService)
                logger.info("✅ VectorService 已加载")
            except Exception as e:
                logger.warning(f"VectorService 不可用: {e}")
            
            try:
                from services.storage.graph_service import GraphService
                self._graph_service = get_service(GraphService)
                logger.info("✅ GraphService 已加载")
            except Exception as e:
                logger.warning(f"GraphService 不可用: {e}")
                
            try:
                from services.storage.unified_storage_service import UnifiedStorageService
                self._storage_service = get_service(UnifiedStorageService)
                logger.info("✅ UnifiedStorageService 已加载")
            except Exception as e:
                logger.warning(f"UnifiedStorageService 不可用: {e}")
                
            try:
                from services.storage.embedding_service import EmbeddingService
                self._embedding_service = get_service(EmbeddingService)
                logger.info("✅ EmbeddingService 已加载")
            except Exception as e:
                logger.warning(f"EmbeddingService 不可用: {e}")
            
            logger.info("🔍 UnifiedSearchService 初始化完成")
            
        except Exception as e:
            logger.error(f"UnifiedSearchService 初始化失败: {e}")
            raise

    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """统一搜索入口 - 替代14个重复搜索实现"""
        start_time = datetime.utcnow()
        
        try:
            results = []
            
            # 根据搜索类型分发到对应的引擎
            if query.search_type == SearchType.SEMANTIC:
                results = await self._semantic_search(query)
                self.stats.semantic_searches += 1
                
            elif query.search_type == SearchType.GRAPH:
                results = await self._graph_search(query)
                self.stats.graph_searches += 1
                
            elif query.search_type == SearchType.TEXT:
                results = await self._text_search(query)
                self.stats.text_searches += 1
                
            elif query.search_type == SearchType.HYBRID:
                results = await self._hybrid_search(query)
                self.stats.semantic_searches += 1
                self.stats.graph_searches += 1
                
            elif query.search_type == SearchType.SIMILAR:
                results = await self._similarity_search(query)
                self.stats.semantic_searches += 1
                
            elif query.search_type == SearchType.PATH:
                results = await self._path_search(query)
                self.stats.graph_searches += 1
            
            else:
                logger.warning(f"不支持的搜索类型: {query.search_type}")
                return []
            
            # 记录统计信息
            search_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._record_search_time(search_time)
            self.stats.total_searches += 1
            self.stats.last_search_time = datetime.utcnow()
            
            logger.debug(f"搜索完成: {len(results)} 结果, 耗时 {search_time:.2f}ms")
            return results
            
        except Exception as e:
            logger.error(f"搜索失败 [{query.search_type.value}]: {e}")
            return []

    async def _semantic_search(self, query: SearchQuery) -> List[SearchResult]:
        """语义搜索 - 整合VectorService和EmbeddingService"""
        try:
            if not self._vector_service or not self._embedding_service:
                logger.warning("语义搜索服务不可用")
                return []
            
            # 生成查询向量
            query_embedding = await self._embedding_service.encode_text(query.query)
            if query_embedding is None:
                return []
            
            # 执行向量搜索
            vector_results = await self._vector_service.search(
                query_vector=query_embedding,
                k=query.limit,
                filter_metadata=query.filters
            )
            
            # 转换为统一结果格式
            results = []
            for result in vector_results:
                if result.score >= query.similarity_threshold:
                    results.append(SearchResult(
                        entity_id=result.id,
                        score=result.score,
                        content=result.content,
                        entity_type=result.metadata.get("entity_type", "unknown"),
                        metadata=result.metadata if query.include_metadata else {},
                        source="vector"
                    ))
            
            return results
            
        except Exception as e:
            logger.error(f"语义搜索失败: {e}")
            return []

    async def _graph_search(self, query: SearchQuery) -> List[SearchResult]:
        """图搜索 - 整合GraphService"""
        try:
            if not self._graph_service or not query.start_entity_id:
                return []
            
            # 执行图遍历
            neighbors = await self._graph_service.find_neighbors(
                entity_id=query.start_entity_id,
                max_depth=query.max_depth,
                relationship_filter=query.relationship_filter
            )
            
            # 转换为统一结果格式
            results = []
            for neighbor_id in neighbors[:query.limit]:
                entity = await self._graph_service.get_entity(neighbor_id)
                if entity:
                    results.append(SearchResult(
                        entity_id=neighbor_id,
                        score=1.0,  # 图搜索使用固定分数
                        content=entity.attributes.get("content", entity.name),
                        entity_type=entity.entity_type,
                        metadata=entity.metadata if query.include_metadata else {},
                        source="graph"
                    ))
            
            return results
            
        except Exception as e:
            logger.error(f"图搜索失败: {e}")
            return []

    async def _text_search(self, query: SearchQuery) -> List[SearchResult]:
        """文本搜索 - 整合UnifiedStorageService的FTS"""
        try:
            if not self._storage_service:
                return []
            
            # 执行全文搜索
            storage_results = await self._storage_service.search_entities(
                query=query.query,
                entity_type=query.filters.get("entity_type"),
                limit=query.limit
            )
            
            # 转换为统一结果格式
            results = []
            for result in storage_results:
                results.append(SearchResult(
                    entity_id=result["id"],
                    score=result.get("score", 0.0),
                    content=result.get("content", result.get("description", "")),
                    entity_type=result.get("entity_type", "unknown"),
                    metadata=result.get("metadata", {}) if query.include_metadata else {},
                    highlights=result.get("highlights", []),
                    source="text"
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"文本搜索失败: {e}")
            return []

    async def _similarity_search(self, query: SearchQuery) -> List[SearchResult]:
        """相似性搜索 - 基于已有实体查找相似项"""
        try:
            if not self._vector_service or not query.start_entity_id:
                return []
            
            # 执行基于文档的相似性搜索
            similar_results = await self._vector_service.search_by_document(
                document_id=query.start_entity_id,
                k=query.limit,
                exclude_self=True
            )
            
            # 转换为统一结果格式
            results = []
            for result in similar_results:
                if result.score >= query.similarity_threshold:
                    results.append(SearchResult(
                        entity_id=result.id,
                        score=result.score,
                        content=result.content,
                        entity_type=result.metadata.get("entity_type", "unknown"),
                        metadata=result.metadata if query.include_metadata else {},
                        source="similarity"
                    ))
            
            return results
            
        except Exception as e:
            logger.error(f"相似性搜索失败: {e}")
            return []

    async def _path_search(self, query: SearchQuery) -> List[SearchResult]:
        """路径搜索 - 查找两个实体间的路径"""
        try:
            if not self._graph_service or not query.start_entity_id or not query.target_entity_id:
                return []
            
            # 查找最短路径
            path = await self._graph_service.find_shortest_path(
                source=query.start_entity_id,
                target=query.target_entity_id
            )
            
            if not path:
                return []
            
            # 构建路径搜索结果
            results = []
            for i, entity_id in enumerate(path):
                entity = await self._graph_service.get_entity(entity_id)
                if entity:
                    results.append(SearchResult(
                        entity_id=entity_id,
                        score=1.0 - (i / len(path)),  # 距离起点越近分数越高
                        content=entity.attributes.get("content", entity.name),
                        entity_type=entity.entity_type,
                        metadata=entity.metadata if query.include_metadata else {},
                        path=path,
                        source="path"
                    ))
            
            return results
            
        except Exception as e:
            logger.error(f"路径搜索失败: {e}")
            return []

    async def _hybrid_search(self, query: SearchQuery) -> List[SearchResult]:
        """混合搜索 - 结合语义搜索和图搜索"""
        try:
            # 并行执行语义搜索和图搜索
            semantic_query = SearchQuery(
                query=query.query,
                search_type=SearchType.SEMANTIC,
                limit=query.limit // 2,
                filters=query.filters,
                similarity_threshold=query.similarity_threshold,
                include_metadata=query.include_metadata
            )
            
            graph_query = SearchQuery(
                query=query.query,
                search_type=SearchType.GRAPH,
                start_entity_id=query.start_entity_id,
                limit=query.limit // 2,
                max_depth=query.max_depth,
                relationship_filter=query.relationship_filter,
                include_metadata=query.include_metadata
            )
            
            semantic_results, graph_results = await asyncio.gather(
                self._semantic_search(semantic_query),
                self._graph_search(graph_query),
                return_exceptions=True
            )
            
            # 处理异常结果
            if isinstance(semantic_results, Exception):
                semantic_results = []
            if isinstance(graph_results, Exception):
                graph_results = []
            
            # 合并和去重结果
            all_results = []
            seen_ids = set()
            
            # 优先添加语义搜索结果（权重更高）
            for result in semantic_results:
                if result.entity_id not in seen_ids:
                    result.score = result.score * 0.7  # 语义搜索权重
                    all_results.append(result)
                    seen_ids.add(result.entity_id)
            
            # 添加图搜索结果
            for result in graph_results:
                if result.entity_id not in seen_ids:
                    result.score = result.score * 0.3  # 图搜索权重  
                    all_results.append(result)
                    seen_ids.add(result.entity_id)
            
            # 按分数排序并限制结果数量
            all_results.sort(key=lambda x: x.score, reverse=True)
            return all_results[:query.limit]
            
        except Exception as e:
            logger.error(f"混合搜索失败: {e}")
            return []

    # === 便捷方法 - 替代原有的各种搜索方法 ===
    
    async def semantic_search(self, query: str, limit: int = 10, **kwargs) -> List[SearchResult]:
        """语义搜索便捷方法"""
        search_query = SearchQuery(
            query=query,
            search_type=SearchType.SEMANTIC,
            limit=limit,
            **kwargs
        )
        return await self.search(search_query)
    
    async def graph_search(self, start_entity_id: str, depth: int = 1, limit: int = 10) -> List[SearchResult]:
        """图搜索便捷方法"""
        search_query = SearchQuery(
            query="",
            search_type=SearchType.GRAPH,
            start_entity_id=start_entity_id,
            max_depth=depth,
            limit=limit
        )
        return await self.search(search_query)
    
    async def find_similar(self, entity_id: str, limit: int = 10, threshold: float = 0.0) -> List[SearchResult]:
        """相似性搜索便捷方法"""
        search_query = SearchQuery(
            query="",
            search_type=SearchType.SIMILAR,
            start_entity_id=entity_id,
            limit=limit,
            similarity_threshold=threshold
        )
        return await self.search(search_query)
    
    async def find_path(self, start_id: str, target_id: str) -> List[SearchResult]:
        """路径搜索便捷方法"""
        search_query = SearchQuery(
            query="",
            search_type=SearchType.PATH,
            start_entity_id=start_id,
            target_entity_id=target_id
        )
        return await self.search(search_query)

    # === 统计和监控 ===
    
    def _record_search_time(self, time_ms: float):
        """记录搜索时间"""
        self._search_times.append(time_ms)
        if len(self._search_times) > self._max_history:
            self._search_times = self._search_times[-self._max_history:]
        
        # 更新平均搜索时间
        if self._search_times:
            self.stats.avg_search_time_ms = sum(self._search_times) / len(self._search_times)
    
    def get_stats(self) -> SearchStats:
        """获取搜索统计信息"""
        return self.stats
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = SearchStats()
        self._search_times.clear()


# 全局实例管理 - 使用ServiceFacade模式
_unified_search_service: Optional[UnifiedSearchService] = None


async def get_unified_search_service() -> UnifiedSearchService:
    """获取统一搜索服务实例"""
    global _unified_search_service
    
    if _unified_search_service is None:
        _unified_search_service = UnifiedSearchService()
        await _unified_search_service.initialize()
    
    return _unified_search_service


async def cleanup_unified_search_service():
    """清理统一搜索服务"""
    global _unified_search_service
    
    if _unified_search_service:
        try:
            # 执行清理逻辑
            logger.info("🔍 UnifiedSearchService 已清理")
        except Exception as e:
            logger.error(f"清理UnifiedSearchService失败: {e}")
        finally:
            _unified_search_service = None