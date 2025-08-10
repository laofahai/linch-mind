#!/usr/bin/env python3
"""
存储编排器 - 统一数据访问接口
协调SQLite + NetworkX + FAISS三层存储架构
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from models.database_models import (
    AIConversation,
    EntityMetadata,
    EntityRelationship,
    UserBehavior,
)

from ..database_service import DatabaseService
from core.service_facade import get_database_service
from .embedding_service import EmbeddingService, get_embedding_service
from .graph_service import EntityNode, GraphService, RelationshipEdge, get_graph_service
from .vector_service import (
    SearchResult,
    VectorDocument,
    VectorService,
    get_vector_service,
)

logger = logging.getLogger(__name__)


@dataclass
class StorageMetrics:
    """存储系统整体指标"""

    total_entities: int
    total_relationships: int
    total_vectors: int
    total_behaviors: int
    total_conversations: int
    storage_usage_mb: float
    last_sync_time: datetime
    health_status: str


@dataclass
class KnowledgeEntity:
    """知识实体 - 统一的实体表示"""

    id: str
    name: str
    entity_type: str
    description: Optional[str]
    attributes: Dict[str, Any]
    metadata: Dict[str, Any]
    embedding_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_accessed: Optional[datetime]
    access_count: int
    relevance_score: float


@dataclass
class SmartRecommendation:
    """智能推荐结果"""

    entity_id: str
    entity_name: str
    entity_type: str
    score: float
    reason: str
    source: str  # 'graph', 'vector', 'behavior', 'hybrid'
    related_entities: List[str]
    confidence: float


class StorageOrchestrator:
    """存储编排器 - 三层存储的统一接口"""

    def __init__(self):
        self.db_service: Optional[DatabaseService] = None
        self.graph_service: Optional[GraphService] = None
        self.vector_service: Optional[VectorService] = None
        self.embedding_service: Optional[EmbeddingService] = None

        # 缓存管理
        self._entity_cache: Dict[str, KnowledgeEntity] = {}
        self._cache_ttl = 300  # 5分钟
        self._cache_timestamps: Dict[str, datetime] = {}

        # 同步状态
        self._last_sync = datetime.utcnow()
        self._sync_interval = timedelta(minutes=10)
        self._auto_sync_enabled = True

        # 性能监控
        self._metrics = StorageMetrics(
            total_entities=0,
            total_relationships=0,
            total_vectors=0,
            total_behaviors=0,
            total_conversations=0,
            storage_usage_mb=0.0,
            last_sync_time=datetime.utcnow(),
            health_status="initializing",
        )

    async def initialize(self) -> bool:
        """初始化存储编排器"""
        try:
            # 初始化四个核心服务
            self.db_service = get_database_service()
            self.graph_service = await get_graph_service()
            self.vector_service = await get_vector_service()
            self.embedding_service = await get_embedding_service()

            # 执行初始同步
            await self._initial_sync()

            # 启动自动同步任务
            if self._auto_sync_enabled:
                asyncio.create_task(self._auto_sync_task())

            self._metrics.health_status = "healthy"
            logger.info("存储编排器初始化完成")
            return True

        except Exception as e:
            logger.error(f"存储编排器初始化失败: {e}")
            self._metrics.health_status = "error"
            return False

    async def close(self):
        """关闭存储编排器"""
        try:
            self._auto_sync_enabled = False

            # 最终同步
            await self.sync_all()

            # 关闭服务
            if self.vector_service:
                await self.vector_service.close()
            if self.graph_service:
                await self.graph_service.close()

            logger.info("存储编排器已关闭")

        except Exception as e:
            logger.error(f"关闭存储编排器失败: {e}")

    # === 实体管理 ===

    async def create_entity(
        self,
        entity_id: str,
        name: str,
        entity_type: str,
        description: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        source_path: Optional[str] = None,
        content: Optional[str] = None,
        auto_embed: bool = True,
    ) -> bool:
        """创建知识实体（三层同步）"""
        try:
            attributes = attributes or {}
            metadata = {
                "source_path": source_path,
                "created_by": "system",
                "version": "1.0",
            }

            # 初始化embedding相关变量
            embedding = None
            embedding_id = None

            # 3. 如果有内容，生成embedding（优先处理，因为后续需要使用）
            if content and auto_embed:
                # 自动生成embedding
                embedding = await self.embedding_service.encode_text(content)
                embedding_id = f"emb_{entity_id}"

            # 1. 创建SQLite记录
            with self.db_service.get_session() as session:
                entity_record = EntityMetadata(
                    id=entity_id,
                    entity_type=entity_type,
                    name=name,
                    description=description,
                    source_path=source_path,
                    entity_metadata={"attributes": attributes, **metadata},
                    embedding_id=embedding_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    access_count=0,
                    relevance_score=0.0,
                )
                session.add(entity_record)
                session.commit()

            # 2. 添加到图数据库
            graph_entity = EntityNode(
                id=entity_id,
                entity_type=entity_type,
                name=name,
                attributes=attributes,
                metadata=metadata,
            )
            await self.graph_service.add_entity(graph_entity)

            # 4. 添加到向量数据库（如果已生成embedding）
            if embedding is not None:

                vector_doc = VectorDocument(
                    id=f"emb_{entity_id}",
                    content=content,
                    embedding=embedding,
                    metadata={
                        "entity_id": entity_id,
                        "entity_type": entity_type,
                        "entity_name": name,
                        **metadata,
                    },
                    entity_id=entity_id,
                )
                await self.vector_service.add_document(vector_doc)

            # 4. 清除缓存
            self._invalidate_entity_cache(entity_id)

            logger.info(f"创建实体: {entity_id} ({entity_type})")
            return True

        except Exception as e:
            logger.error(f"创建实体失败 [{entity_id}]: {e}")
            return False

    async def get_entity(self, entity_id: str) -> Optional[KnowledgeEntity]:
        """获取知识实体（带缓存）"""
        # 检查缓存
        if self._is_entity_cached(entity_id):
            return self._entity_cache[entity_id]

        try:
            # 从SQLite获取基础信息
            with self.db_service.get_session() as session:
                entity_record = (
                    session.query(EntityMetadata)
                    .filter(EntityMetadata.id == entity_id)
                    .first()
                )

                if not entity_record:
                    return None

                # 转换为统一格式
                entity = KnowledgeEntity(
                    id=entity_record.id,
                    name=entity_record.name,
                    entity_type=entity_record.entity_type,
                    description=entity_record.description,
                    attributes=entity_record.entity_metadata.get("attributes", {}),
                    metadata=entity_record.entity_metadata or {},
                    embedding_id=entity_record.embedding_id,
                    created_at=entity_record.created_at,
                    updated_at=entity_record.updated_at,
                    last_accessed=entity_record.last_accessed,
                    access_count=entity_record.access_count,
                    relevance_score=entity_record.relevance_score,
                )

                # 更新访问统计
                entity_record.last_accessed = datetime.utcnow()
                entity_record.access_count += 1
                session.commit()

                # 缓存结果
                self._cache_entity(entity_id, entity)

                return entity

        except Exception as e:
            logger.error(f"获取实体失败 [{entity_id}]: {e}")
            return None

    async def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """更新知识实体（三层同步）"""
        try:
            # 1. 更新SQLite
            with self.db_service.get_session() as session:
                entity_record = (
                    session.query(EntityMetadata)
                    .filter(EntityMetadata.id == entity_id)
                    .first()
                )

                if not entity_record:
                    logger.warning(f"实体不存在: {entity_id}")
                    return False

                # 更新字段
                for key, value in updates.items():
                    if hasattr(entity_record, key):
                        setattr(entity_record, key, value)

                entity_record.updated_at = datetime.utcnow()
                session.commit()

            # 2. 更新图数据库
            graph_updates = {}
            if "name" in updates:
                graph_updates["name"] = updates["name"]
            if "attributes" in updates:
                graph_updates["attributes"] = updates["attributes"]
            if "metadata" in updates:
                graph_updates["metadata"] = updates["metadata"]

            if graph_updates:
                await self.graph_service.update_entity(entity_id, graph_updates)

            # 3. 清除缓存
            self._invalidate_entity_cache(entity_id)

            logger.debug(f"更新实体: {entity_id}")
            return True

        except Exception as e:
            logger.error(f"更新实体失败 [{entity_id}]: {e}")
            return False

    async def delete_entity(self, entity_id: str) -> bool:
        """删除知识实体（三层同步）"""
        try:
            # 1. 删除SQLite记录
            with self.db_service.get_session() as session:
                entity_record = (
                    session.query(EntityMetadata)
                    .filter(EntityMetadata.id == entity_id)
                    .first()
                )

                if entity_record:
                    embedding_id = entity_record.embedding_id
                    session.delete(entity_record)
                    session.commit()

                    # 2. 删除向量文档
                    if embedding_id:
                        await self.vector_service.remove_document(embedding_id)

                # 删除相关关系
                session.query(EntityRelationship).filter(
                    (EntityRelationship.source_entity == entity_id)
                    | (EntityRelationship.target_entity == entity_id)
                ).delete()
                session.commit()

            # 3. 从图数据库删除
            await self.graph_service.remove_entity(entity_id)

            # 4. 清除缓存
            self._invalidate_entity_cache(entity_id)

            logger.info(f"删除实体: {entity_id}")
            return True

        except Exception as e:
            logger.error(f"删除实体失败 [{entity_id}]: {e}")
            return False

    # === 关系管理 ===

    async def create_relationship(
        self,
        source_entity: str,
        target_entity: str,
        relationship_type: str,
        strength: float = 1.0,
        confidence: float = 1.0,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """创建实体关系（双层同步）"""
        try:
            attributes = attributes or {}

            # 1. 创建SQLite记录
            with self.db_service.get_session() as session:
                relationship = EntityRelationship(
                    source_entity=source_entity,
                    target_entity=target_entity,
                    relationship_type=relationship_type,
                    strength=strength,
                    confidence=confidence,
                    relationship_data=attributes,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                session.add(relationship)
                session.commit()

            # 2. 添加到图数据库
            graph_relationship = RelationshipEdge(
                source=source_entity,
                target=target_entity,
                relationship_type=relationship_type,
                strength=strength,
                confidence=confidence,
                attributes=attributes,
            )
            await self.graph_service.add_relationship(graph_relationship)

            logger.debug(
                f"创建关系: {source_entity} -> {target_entity} ({relationship_type})"
            )
            return True

        except Exception as e:
            logger.error(f"创建关系失败: {e}")
            return False

    # === 智能搜索 ===

    async def semantic_search(
        self, query: str, k: int = 10, entity_types: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """语义搜索"""
        try:
            # 使用内置的embedding服务
            query_embedding = await self.embedding_service.encode_text(query)

            # 构建过滤条件
            filter_metadata = {}
            if entity_types:
                filter_metadata["entity_type"] = entity_types

            # 执行向量搜索
            results = await self.vector_service.search(
                query_vector=query_embedding, k=k, filter_metadata=filter_metadata
            )

            # 过滤结果
            if filter_metadata:
                filtered_results = []
                for result in results:
                    if self._match_entity_filter(result.metadata, filter_metadata):
                        filtered_results.append(result)
                results = filtered_results[:k]

            logger.debug(f"语义搜索: '{query}' -> {len(results)} 结果")
            return results

        except Exception as e:
            logger.error(f"语义搜索失败: {e}")
            return []

    async def graph_search(
        self,
        entity_id: str,
        max_depth: int = 2,
        relationship_types: Optional[List[str]] = None,
        max_results: int = 20,
    ) -> List[str]:
        """图结构搜索"""
        try:
            neighbors = await self.graph_service.find_neighbors(
                entity_id=entity_id,
                max_depth=max_depth,
                relationship_filter=relationship_types,
            )

            return neighbors[:max_results]

        except Exception as e:
            logger.error(f"图搜索失败 [{entity_id}]: {e}")
            return []

    # === 智能推荐 ===

    async def get_smart_recommendations(
        self,
        user_context: Optional[Dict[str, Any]] = None,
        max_recommendations: int = 10,
        algorithm: str = "hybrid",
    ) -> List[SmartRecommendation]:
        """获取智能推荐"""
        try:
            recommendations = []

            if algorithm in ["hybrid", "graph"]:
                # 基于图结构的推荐
                graph_recs = await self._get_graph_recommendations(
                    user_context, max_recommendations
                )
                recommendations.extend(graph_recs)

            if algorithm in ["hybrid", "vector"]:
                # 基于向量相似性的推荐
                vector_recs = await self._get_vector_recommendations(
                    user_context, max_recommendations
                )
                recommendations.extend(vector_recs)

            if algorithm in ["hybrid", "behavior"]:
                # 基于用户行为的推荐
                behavior_recs = await self._get_behavior_recommendations(
                    user_context, max_recommendations
                )
                recommendations.extend(behavior_recs)

            # 去重并排序
            unique_recs = {}
            for rec in recommendations:
                if (
                    rec.entity_id not in unique_recs
                    or rec.score > unique_recs[rec.entity_id].score
                ):
                    unique_recs[rec.entity_id] = rec

            final_recs = list(unique_recs.values())
            final_recs.sort(key=lambda x: x.score, reverse=True)

            return final_recs[:max_recommendations]

        except Exception as e:
            logger.error(f"智能推荐失败: {e}")
            return []

    async def _get_graph_recommendations(
        self, user_context: Optional[Dict[str, Any]], max_recommendations: int
    ) -> List[SmartRecommendation]:
        """基于图结构的推荐"""
        recommendations = []

        try:
            # 获取中心性分析
            centrality = await self.graph_service.calculate_centrality("pagerank")

            # 转换为推荐结果
            for entity_id, score in list(centrality.items())[:max_recommendations]:
                entity = await self.get_entity(entity_id)
                if entity:
                    recommendations.append(
                        SmartRecommendation(
                            entity_id=entity_id,
                            entity_name=entity.name,
                            entity_type=entity.entity_type,
                            score=score,
                            reason="高重要性实体",
                            source="graph",
                            related_entities=[],
                            confidence=0.8,
                        )
                    )

        except Exception as e:
            logger.error(f"图推荐失败: {e}")

        return recommendations

    async def _get_vector_recommendations(
        self, user_context: Optional[Dict[str, Any]], max_recommendations: int
    ) -> List[SmartRecommendation]:
        """基于向量相似性的推荐"""
        recommendations = []

        try:
            # 这里需要根据用户上下文生成查询向量
            # 简化实现：随机推荐一些向量文档
            if (
                hasattr(self.vector_service, "id_to_doc")
                and self.vector_service.id_to_doc
            ):
                doc_ids = list(self.vector_service.id_to_doc.keys())[
                    :max_recommendations
                ]

                for doc_id in doc_ids:
                    doc = self.vector_service.id_to_doc[doc_id]
                    if doc.entity_id:
                        entity = await self.get_entity(doc.entity_id)
                        if entity:
                            recommendations.append(
                                SmartRecommendation(
                                    entity_id=doc.entity_id,
                                    entity_name=entity.name,
                                    entity_type=entity.entity_type,
                                    score=0.7,
                                    reason="内容相关性",
                                    source="vector",
                                    related_entities=[],
                                    confidence=0.7,
                                )
                            )

        except Exception as e:
            logger.error(f"向量推荐失败: {e}")

        return recommendations

    async def _get_behavior_recommendations(
        self, user_context: Optional[Dict[str, Any]], max_recommendations: int
    ) -> List[SmartRecommendation]:
        """基于用户行为的推荐"""
        recommendations = []

        try:
            # 分析最近的用户行为
            with self.db_service.get_session() as session:
                recent_behaviors = (
                    session.query(UserBehavior)
                    .filter(
                        UserBehavior.timestamp >= datetime.utcnow() - timedelta(days=7)
                    )
                    .limit(100)
                    .all()
                )

                # 统计实体访问频率
                entity_scores = {}
                for behavior in recent_behaviors:
                    if behavior.target_entity:
                        entity_scores[behavior.target_entity] = (
                            entity_scores.get(behavior.target_entity, 0)
                            + behavior.interaction_strength
                            or 1.0
                        )

                # 转换为推荐结果
                sorted_entities = sorted(
                    entity_scores.items(), key=lambda x: x[1], reverse=True
                )

                for entity_id, score in sorted_entities[:max_recommendations]:
                    entity = await self.get_entity(entity_id)
                    if entity:
                        recommendations.append(
                            SmartRecommendation(
                                entity_id=entity_id,
                                entity_name=entity.name,
                                entity_type=entity.entity_type,
                                score=min(score / 10.0, 1.0),  # 归一化分数
                                reason="最近访问过",
                                source="behavior",
                                related_entities=[],
                                confidence=0.9,
                            )
                        )

        except Exception as e:
            logger.error(f"行为推荐失败: {e}")

        return recommendations

    # === 数据同步 ===

    async def sync_all(self) -> bool:
        """同步所有存储层的数据"""
        try:
            logger.info("开始数据同步...")

            # 1. 同步实体数据 (SQLite -> Graph)
            await self._sync_entities()

            # 2. 同步关系数据 (SQLite -> Graph)
            await self._sync_relationships()

            # 3. 保存图数据
            await self.graph_service.save_graph()

            # 4. 保存向量索引
            await self.vector_service.save_index()

            # 5. 更新指标
            await self._update_metrics()

            self._last_sync = datetime.utcnow()
            self._metrics.last_sync_time = self._last_sync

            logger.info("数据同步完成")
            return True

        except Exception as e:
            logger.error(f"数据同步失败: {e}")
            return False

    async def _sync_entities(self):
        """同步实体数据"""
        with self.db_service.get_session() as session:
            entities = session.query(EntityMetadata).all()

            for entity_record in entities:
                # 检查图中是否存在
                graph_entity = await self.graph_service.get_entity(entity_record.id)

                if not graph_entity:
                    # 添加到图数据库
                    graph_entity = EntityNode(
                        id=entity_record.id,
                        entity_type=entity_record.entity_type,
                        name=entity_record.name,
                        attributes=entity_record.entity_metadata.get("attributes", {}),
                        metadata=entity_record.entity_metadata or {},
                    )
                    await self.graph_service.add_entity(graph_entity)

    async def _sync_relationships(self):
        """同步关系数据"""
        with self.db_service.get_session() as session:
            relationships = session.query(EntityRelationship).all()

            for rel_record in relationships:
                # 添加到图数据库（图服务会处理重复）
                graph_relationship = RelationshipEdge(
                    source=rel_record.source_entity,
                    target=rel_record.target_entity,
                    relationship_type=rel_record.relationship_type,
                    strength=rel_record.strength,
                    confidence=rel_record.confidence,
                    attributes=rel_record.relationship_data or {},
                )
                await self.graph_service.add_relationship(graph_relationship)

    async def _initial_sync(self):
        """初始化同步"""
        logger.info("执行初始数据同步...")
        await self.sync_all()

    async def _auto_sync_task(self):
        """自动同步任务"""
        while self._auto_sync_enabled:
            try:
                if datetime.utcnow() - self._last_sync > self._sync_interval:
                    await self.sync_all()

                await asyncio.sleep(60)  # 每分钟检查一次

            except Exception as e:
                logger.error(f"自动同步任务异常: {e}")
                await asyncio.sleep(300)  # 出错时等待5分钟

    # === 性能监控 ===

    async def get_metrics(self) -> StorageMetrics:
        """获取存储系统指标"""
        await self._update_metrics()
        return self._metrics

    async def _update_metrics(self):
        """更新系统指标"""
        try:
            with self.db_service.get_session() as session:
                self._metrics.total_entities = session.query(EntityMetadata).count()
                self._metrics.total_relationships = session.query(
                    EntityRelationship
                ).count()
                self._metrics.total_behaviors = session.query(UserBehavior).count()
                self._metrics.total_conversations = session.query(
                    AIConversation
                ).count()

            if self.vector_service:
                vector_metrics = await self.vector_service.get_metrics()
                self._metrics.total_vectors = vector_metrics.total_vectors
                self._metrics.storage_usage_mb += vector_metrics.memory_usage_mb

            if self.graph_service:
                graph_metrics = await self.graph_service.get_metrics()
                self._metrics.storage_usage_mb += graph_metrics.memory_usage_mb

        except Exception as e:
            logger.error(f"更新指标失败: {e}")

    # === 缓存管理 ===

    def _is_entity_cached(self, entity_id: str) -> bool:
        """检查实体是否在缓存中"""
        if entity_id not in self._entity_cache:
            return False

        timestamp = self._cache_timestamps.get(entity_id)
        if not timestamp:
            return False

        return (datetime.utcnow() - timestamp).total_seconds() < self._cache_ttl

    def _cache_entity(self, entity_id: str, entity: KnowledgeEntity):
        """缓存实体"""
        self._entity_cache[entity_id] = entity
        self._cache_timestamps[entity_id] = datetime.utcnow()

    def _invalidate_entity_cache(self, entity_id: str):
        """清除实体缓存"""
        self._entity_cache.pop(entity_id, None)
        self._cache_timestamps.pop(entity_id, None)

    def _match_entity_filter(
        self, metadata: Dict[str, Any], filter_criteria: Dict[str, Any]
    ) -> bool:
        """检查实体是否匹配过滤条件"""
        for key, value in filter_criteria.items():
            if key not in metadata:
                return False

            if isinstance(value, list):
                if metadata[key] not in value:
                    return False
            else:
                if metadata[key] != value:
                    return False

        return True


# 全局存储编排器实例
_storage_orchestrator: Optional[StorageOrchestrator] = None


async def get_storage_orchestrator() -> StorageOrchestrator:
    """获取存储编排器实例（单例模式）"""
    global _storage_orchestrator
    if _storage_orchestrator is None:
        _storage_orchestrator = StorageOrchestrator()
        await _storage_orchestrator.initialize()

    return _storage_orchestrator


async def cleanup_storage_orchestrator():
    """清理存储编排器"""
    global _storage_orchestrator
    if _storage_orchestrator:
        await _storage_orchestrator.close()
        _storage_orchestrator = None
