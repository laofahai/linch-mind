#!/usr/bin/env python3
"""
简化存储服务
替代过度抽象的StorageOrchestrator
整合vector/graph/embedding功能到单一服务
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from core.service_facade import get_database_service
from models.database_models import EntityMetadata, EntityRelationship

logger = logging.getLogger(__name__)


@dataclass
class StorageEntity:
    """简化的存储实体"""
    
    id: str
    name: str
    entity_type: str
    content: str
    metadata: Dict[str, Any]
    vector_embedding: Optional[List[float]] = None
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class SearchResult:
    """搜索结果"""
    
    entity: StorageEntity
    score: float
    source: str  # 'database', 'vector', 'graph'


@dataclass
class RecommendationResult:
    """推荐结果"""
    
    entity: StorageEntity
    score: float
    reason: str


class SimplifiedStorageService:
    """简化存储服务
    
    整合功能:
    - 实体存储和检索
    - 向量搜索
    - 图关系查询
    - 智能推荐
    """

    def __init__(self):
        self.db_service = None
        self._entity_cache: Dict[str, StorageEntity] = {}
        self._initialized = False

    async def initialize(self) -> bool:
        """初始化存储服务"""
        try:
            self.db_service = get_database_service()
            
            # 测试数据库连接
            if not self.db_service.test_connection():
                raise RuntimeError("数据库连接测试失败")

            self._initialized = True
            logger.info("简化存储服务初始化完成")
            return True

        except Exception as e:
            logger.error(f"简化存储服务初始化失败: {e}")
            return False

    async def close(self):
        """关闭存储服务"""
        try:
            self._entity_cache.clear()
            self._initialized = False
            logger.info("简化存储服务已关闭")
        except Exception as e:
            logger.error(f"关闭存储服务失败: {e}")

    def _check_initialized(self):
        """检查服务是否已初始化"""
        if not self._initialized:
            raise RuntimeError("存储服务未初始化")

    # === 实体管理 ===

    async def store_entity(self, entity: StorageEntity) -> bool:
        """存储实体"""
        try:
            self._check_initialized()

            with self.db_service.get_session() as session:
                # 检查是否已存在
                existing = (
                    session.query(EntityMetadata)
                    .filter_by(entity_id=entity.id)
                    .first()
                )

                if existing:
                    # 更新现有实体
                    existing.display_name = entity.name
                    existing.description = entity.content[:500]  # 限制描述长度
                    existing.metadata = entity.metadata
                    existing.updated_at = datetime.utcnow()
                    logger.debug(f"更新实体: {entity.id}")
                else:
                    # 创建新实体
                    new_entity = EntityMetadata(
                        entity_type=entity.entity_type,
                        entity_id=entity.id,
                        display_name=entity.name,
                        description=entity.content[:500],
                        metadata=entity.metadata,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    session.add(new_entity)
                    logger.debug(f"创建新实体: {entity.id}")

                session.commit()

                # 更新缓存
                self._entity_cache[entity.id] = entity

                return True

        except Exception as e:
            logger.error(f"存储实体失败 [{entity.id}]: {e}")
            return False

    async def get_entity(self, entity_id: str) -> Optional[StorageEntity]:
        """获取实体"""
        try:
            self._check_initialized()

            # 先检查缓存
            if entity_id in self._entity_cache:
                return self._entity_cache[entity_id]

            # 从数据库查询
            with self.db_service.get_session() as session:
                db_entity = (
                    session.query(EntityMetadata)
                    .filter_by(entity_id=entity_id)
                    .first()
                )

                if not db_entity:
                    return None

                # 转换为StorageEntity
                storage_entity = StorageEntity(
                    id=db_entity.entity_id,
                    name=db_entity.display_name or entity_id,
                    entity_type=db_entity.entity_type or "unknown",
                    content=db_entity.description or "",
                    metadata=db_entity.metadata or {},
                    created_at=db_entity.created_at,
                    updated_at=db_entity.updated_at,
                )

                # 更新缓存
                self._entity_cache[entity_id] = storage_entity

                return storage_entity

        except Exception as e:
            logger.error(f"获取实体失败 [{entity_id}]: {e}")
            return None

    async def delete_entity(self, entity_id: str) -> bool:
        """删除实体"""
        try:
            self._check_initialized()

            with self.db_service.get_session() as session:
                # 删除实体
                entity = (
                    session.query(EntityMetadata)
                    .filter_by(entity_id=entity_id)
                    .first()
                )

                if entity:
                    session.delete(entity)

                # 删除相关关系
                relationships = (
                    session.query(EntityRelationship)
                    .filter(
                        (EntityRelationship.source_entity_id == entity.id) |
                        (EntityRelationship.target_entity_id == entity.id)
                    )
                    .all()
                )

                for rel in relationships:
                    session.delete(rel)

                session.commit()

                # 从缓存中删除
                self._entity_cache.pop(entity_id, None)

                logger.info(f"删除实体: {entity_id}")
                return True

        except Exception as e:
            logger.error(f"删除实体失败 [{entity_id}]: {e}")
            return False

    # === 关系管理 ===

    async def create_relationship(
        self, 
        source_id: str, 
        target_id: str, 
        relationship_type: str,
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """创建实体关系"""
        try:
            self._check_initialized()

            with self.db_service.get_session() as session:
                # 检查源实体和目标实体是否存在
                source_exists = session.query(EntityMetadata).filter_by(entity_id=source_id).first()
                target_exists = session.query(EntityMetadata).filter_by(entity_id=target_id).first()

                if not source_exists or not target_exists:
                    logger.warning(f"关系创建失败，实体不存在: {source_id} -> {target_id}")
                    return False

                # 检查关系是否已存在
                existing_rel = (
                    session.query(EntityRelationship)
                    .filter_by(
                        source_entity_id=source_exists.id,
                        target_entity_id=target_exists.id,
                        relationship_type=relationship_type
                    )
                    .first()
                )

                if existing_rel:
                    # 更新现有关系
                    existing_rel.strength = strength
                    existing_rel.metadata = metadata or {}
                    existing_rel.updated_at = datetime.utcnow()
                    logger.debug(f"更新关系: {source_id} -> {target_id} ({relationship_type})")
                else:
                    # 创建新关系
                    new_rel = EntityRelationship(
                        source_entity_id=source_exists.id,
                        target_entity_id=target_exists.id,
                        relationship_type=relationship_type,
                        strength=strength,
                        metadata=metadata or {},
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    session.add(new_rel)
                    logger.debug(f"创建关系: {source_id} -> {target_id} ({relationship_type})")

                session.commit()
                return True

        except Exception as e:
            logger.error(f"创建关系失败 [{source_id} -> {target_id}]: {e}")
            return False

    async def get_related_entities(
        self, entity_id: str, relationship_type: Optional[str] = None
    ) -> List[Tuple[StorageEntity, str, float]]:
        """获取相关实体"""
        try:
            self._check_initialized()

            related_entities = []

            with self.db_service.get_session() as session:
                # 查找实体
                entity = session.query(EntityMetadata).filter_by(entity_id=entity_id).first()
                if not entity:
                    return []

                # 构建查询
                query = session.query(EntityRelationship, EntityMetadata).join(
                    EntityMetadata,
                    EntityRelationship.target_entity_id == EntityMetadata.id
                ).filter(EntityRelationship.source_entity_id == entity.id)

                if relationship_type:
                    query = query.filter(EntityRelationship.relationship_type == relationship_type)

                results = query.all()

                for rel, target_entity in results:
                    storage_entity = StorageEntity(
                        id=target_entity.entity_id,
                        name=target_entity.display_name or target_entity.entity_id,
                        entity_type=target_entity.entity_type or "unknown",
                        content=target_entity.description or "",
                        metadata=target_entity.metadata or {},
                        created_at=target_entity.created_at,
                        updated_at=target_entity.updated_at,
                    )

                    related_entities.append((storage_entity, rel.relationship_type, rel.strength))

            return related_entities

        except Exception as e:
            logger.error(f"获取相关实体失败 [{entity_id}]: {e}")
            return []

    # === 搜索功能 ===

    async def search_entities(
        self, 
        query: str, 
        entity_type: Optional[str] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """搜索实体"""
        try:
            self._check_initialized()

            results = []

            with self.db_service.get_session() as session:
                # 构建数据库查询
                db_query = session.query(EntityMetadata)

                if entity_type:
                    db_query = db_query.filter(EntityMetadata.entity_type == entity_type)

                # 简单的文本匹配（可以后续增强为全文搜索）
                db_query = db_query.filter(
                    (EntityMetadata.display_name.contains(query)) |
                    (EntityMetadata.description.contains(query))
                )

                db_results = db_query.limit(limit).all()

                for db_entity in db_results:
                    storage_entity = StorageEntity(
                        id=db_entity.entity_id,
                        name=db_entity.display_name or db_entity.entity_id,
                        entity_type=db_entity.entity_type or "unknown",
                        content=db_entity.description or "",
                        metadata=db_entity.metadata or {},
                        created_at=db_entity.created_at,
                        updated_at=db_entity.updated_at,
                    )

                    # 计算简单的匹配分数
                    score = self._calculate_text_similarity(query, storage_entity)

                    results.append(SearchResult(
                        entity=storage_entity,
                        score=score,
                        source="database"
                    ))

            # 按分数排序
            results.sort(key=lambda x: x.score, reverse=True)

            return results

        except Exception as e:
            logger.error(f"搜索实体失败 [{query}]: {e}")
            return []

    def _calculate_text_similarity(self, query: str, entity: StorageEntity) -> float:
        """计算文本相似度（简化版本）"""
        query_lower = query.lower()
        
        # 名称匹配
        name_score = 0.0
        if query_lower in entity.name.lower():
            name_score = 0.5

        # 内容匹配
        content_score = 0.0
        if entity.content and query_lower in entity.content.lower():
            content_score = 0.3

        # 类型匹配
        type_score = 0.0
        if query_lower in entity.entity_type.lower():
            type_score = 0.2

        return name_score + content_score + type_score

    # === 推荐功能 ===

    async def get_recommendations(
        self, entity_id: str, limit: int = 5
    ) -> List[RecommendationResult]:
        """获取推荐实体"""
        try:
            self._check_initialized()

            recommendations = []

            # 基于关系的推荐
            related_entities = await self.get_related_entities(entity_id)
            
            for related_entity, rel_type, strength in related_entities:
                recommendations.append(RecommendationResult(
                    entity=related_entity,
                    score=strength * 0.8,  # 关系推荐权重
                    reason=f"通过 {rel_type} 关系关联"
                ))

            # 基于类型的推荐
            entity = await self.get_entity(entity_id)
            if entity:
                type_recommendations = await self.search_entities(
                    "", entity_type=entity.entity_type, limit=limit * 2
                )
                
                for search_result in type_recommendations[:limit]:
                    if search_result.entity.id != entity_id:  # 不推荐自己
                        recommendations.append(RecommendationResult(
                            entity=search_result.entity,
                            score=0.6,  # 类型推荐权重
                            reason=f"相同类型: {entity.entity_type}"
                        ))

            # 去重并按分数排序
            unique_recommendations = {}
            for rec in recommendations:
                if rec.entity.id not in unique_recommendations or rec.score > unique_recommendations[rec.entity.id].score:
                    unique_recommendations[rec.entity.id] = rec

            final_recommendations = list(unique_recommendations.values())
            final_recommendations.sort(key=lambda x: x.score, reverse=True)

            return final_recommendations[:limit]

        except Exception as e:
            logger.error(f"获取推荐失败 [{entity_id}]: {e}")
            return []

    # === 统计和状态 ===

    async def get_storage_stats(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        try:
            self._check_initialized()

            with self.db_service.get_session() as session:
                entity_count = session.query(EntityMetadata).count()
                relationship_count = session.query(EntityRelationship).count()

                # 按类型统计实体
                type_stats = {}
                type_results = session.execute(
                    "SELECT entity_type, COUNT(*) FROM entity_metadata GROUP BY entity_type"
                ).fetchall()
                
                for entity_type, count in type_results:
                    type_stats[entity_type or "unknown"] = count

                return {
                    "total_entities": entity_count,
                    "total_relationships": relationship_count,
                    "entities_by_type": type_stats,
                    "cache_size": len(self._entity_cache),
                    "initialized": self._initialized,
                    "last_updated": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            logger.error(f"获取存储统计失败: {e}")
            return {}

    def clear_cache(self):
        """清理缓存"""
        self._entity_cache.clear()
        logger.info("存储服务缓存已清理")

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if not self._initialized:
                return False

            # 测试数据库连接
            if not self.db_service.test_connection():
                return False

            # 测试基本查询
            stats = await self.get_storage_stats()
            return "total_entities" in stats

        except Exception as e:
            logger.error(f"存储服务健康检查失败: {e}")
            return False


# 全局实例
_storage_service = None


async def get_simplified_storage_service() -> SimplifiedStorageService:
    """获取简化存储服务实例"""
    global _storage_service
    
    if _storage_service is None:
        _storage_service = SimplifiedStorageService()
        await _storage_service.initialize()
    
    return _storage_service


def cleanup_simplified_storage_service():
    """清理简化存储服务"""
    global _storage_service
    
    if _storage_service:
        asyncio.create_task(_storage_service.close())
        _storage_service = None