#!/usr/bin/env python3
"""
数据迁移服务 - SQLite到三层存储架构的数据迁移
负责将现有的SQLite数据迁移到图数据库和向量数据库
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from core.service_facade import get_database_service
from models.database_models import EntityMetadata, EntityRelationship

from .embedding_service import get_embedding_service
from .storage_orchestrator import StorageOrchestrator, get_storage_orchestrator

logger = logging.getLogger(__name__)


@dataclass
class MigrationStats:
    """迁移统计信息"""

    total_entities: int = 0
    migrated_entities: int = 0
    failed_entities: int = 0

    total_relationships: int = 0
    migrated_relationships: int = 0
    failed_relationships: int = 0

    total_embeddings: int = 0
    migrated_embeddings: int = 0
    failed_embeddings: int = 0

    start_time: datetime = None
    end_time: datetime = None

    @property
    def duration_seconds(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def entity_success_rate(self) -> float:
        if self.total_entities == 0:
            return 0.0
        return self.migrated_entities / self.total_entities * 100

    @property
    def relationship_success_rate(self) -> float:
        if self.total_relationships == 0:
            return 0.0
        return self.migrated_relationships / self.total_relationships * 100


class DataMigrationService:
    """数据迁移服务 - 将SQLite数据迁移到三层存储架构"""

    def __init__(self):
        self.storage_orchestrator: Optional[StorageOrchestrator] = None
        self.embedding_service = None
        self.db_service = None
        self.stats = MigrationStats()

    async def initialize(self) -> bool:
        """初始化迁移服务"""
        try:
            self.storage_orchestrator = await get_storage_orchestrator()
            self.embedding_service = await get_embedding_service()
            self.db_service = get_database_service()

            logger.info("数据迁移服务初始化完成")
            return True

        except Exception as e:
            logger.error(f"数据迁移服务初始化失败: {e}")
            return False

    async def migrate_all_data(
        self,
        force_rebuild: bool = False,
        batch_size: int = 100,
        auto_embed: bool = True,
    ) -> MigrationStats:
        """迁移所有数据"""
        try:
            logger.info("开始数据迁移...")
            self.stats = MigrationStats()
            self.stats.start_time = datetime.utcnow()

            # 1. 检查现有数据
            await self._analyze_existing_data()

            # 2. 迁移实体数据
            await self._migrate_entities(batch_size, auto_embed, force_rebuild)

            # 3. 迁移关系数据
            await self._migrate_relationships(batch_size, force_rebuild)

            # 4. 验证迁移结果
            await self._validate_migration()

            # 5. 同步所有存储层
            await self.storage_orchestrator.sync_all()

            self.stats.end_time = datetime.utcnow()

            logger.info(f"数据迁移完成！耗时 {self.stats.duration_seconds:.2f} 秒")
            logger.info(
                f"实体: {self.stats.migrated_entities}/{self.stats.total_entities} "
                f"({self.stats.entity_success_rate:.1f}%)"
            )
            logger.info(
                f"关系: {self.stats.migrated_relationships}/{self.stats.total_relationships} "
                f"({self.stats.relationship_success_rate:.1f}%)"
            )
            logger.info(
                f"向量: {self.stats.migrated_embeddings}/{self.stats.total_embeddings}"
            )

            return self.stats

        except Exception as e:
            logger.error(f"数据迁移失败: {e}")
            self.stats.end_time = datetime.utcnow()
            return self.stats

    async def _analyze_existing_data(self):
        """分析现有数据"""
        try:
            with self.db_service.get_session() as session:
                self.stats.total_entities = session.query(EntityMetadata).count()
                self.stats.total_relationships = session.query(
                    EntityRelationship
                ).count()

            logger.info(
                f"待迁移数据: {self.stats.total_entities} 个实体, "
                f"{self.stats.total_relationships} 个关系"
            )

        except Exception as e:
            logger.error(f"分析现有数据失败: {e}")

    async def _migrate_entities(
        self, batch_size: int, auto_embed: bool, force_rebuild: bool
    ):
        """迁移实体数据"""
        try:
            logger.info("开始迁移实体数据...")

            with self.db_service.get_session() as session:
                # 分批处理实体
                offset = 0
                while True:
                    entities = (
                        session.query(EntityMetadata)
                        .offset(offset)
                        .limit(batch_size)
                        .all()
                    )
                    if not entities:
                        break

                    # 处理当前批次
                    for entity in entities:
                        success = await self._migrate_single_entity(
                            entity, auto_embed, force_rebuild
                        )
                        if success:
                            self.stats.migrated_entities += 1
                            if auto_embed and entity.description:
                                self.stats.migrated_embeddings += 1
                                self.stats.total_embeddings += 1
                        else:
                            self.stats.failed_entities += 1

                    offset += batch_size

                    # 显示进度
                    progress = (
                        min(offset, self.stats.total_entities)
                        / self.stats.total_entities
                        * 100
                    )
                    logger.info(
                        f"实体迁移进度: {progress:.1f}% "
                        f"({self.stats.migrated_entities}/{self.stats.total_entities})"
                    )

            logger.info("实体数据迁移完成")

        except Exception as e:
            logger.error(f"迁移实体数据失败: {e}")

    async def _migrate_single_entity(
        self, entity: EntityMetadata, auto_embed: bool, force_rebuild: bool
    ) -> bool:
        """迁移单个实体"""
        try:
            # 检查图数据库中是否已存在
            if not force_rebuild:
                existing_graph_entity = (
                    await self.storage_orchestrator.graph_service.get_entity(entity.id)
                )
                if existing_graph_entity:
                    logger.debug(f"跳过已存在的实体: {entity.id}")
                    return True

            # 准备实体内容
            content = None
            if entity.description:
                content = f"{entity.name}\n{entity.description}"
            elif entity.name:
                content = entity.name

            # 直接使用存储编排器的create_entity方法
            success = await self.storage_orchestrator.create_entity(
                entity_id=entity.id,
                name=entity.name,
                entity_type=entity.entity_type,
                description=entity.description,
                attributes=(
                    entity.entity_metadata.get("attributes", {})
                    if entity.entity_metadata
                    else {}
                ),
                source_path=entity.source_path,
                content=content,
                auto_embed=auto_embed and content is not None,
            )

            if success:
                logger.debug(f"迁移实体成功: {entity.id}")
            else:
                logger.warning(f"迁移实体失败: {entity.id}")

            return success

        except Exception as e:
            logger.error(f"迁移实体失败 [{entity.id}]: {e}")
            return False

    async def _migrate_relationships(self, batch_size: int, force_rebuild: bool):
        """迁移关系数据"""
        try:
            logger.info("开始迁移关系数据...")

            with self.db_service.get_session() as session:
                # 分批处理关系
                offset = 0
                while True:
                    relationships = (
                        session.query(EntityRelationship)
                        .offset(offset)
                        .limit(batch_size)
                        .all()
                    )
                    if not relationships:
                        break

                    # 处理当前批次
                    for relationship in relationships:
                        success = await self._migrate_single_relationship(
                            relationship, force_rebuild
                        )
                        if success:
                            self.stats.migrated_relationships += 1
                        else:
                            self.stats.failed_relationships += 1

                    offset += batch_size

                    # 显示进度
                    progress = (
                        min(offset, self.stats.total_relationships)
                        / self.stats.total_relationships
                        * 100
                    )
                    logger.info(
                        f"关系迁移进度: {progress:.1f}% "
                        f"({self.stats.migrated_relationships}/{self.stats.total_relationships})"
                    )

            logger.info("关系数据迁移完成")

        except Exception as e:
            logger.error(f"迁移关系数据失败: {e}")

    async def _migrate_single_relationship(
        self, relationship: EntityRelationship, force_rebuild: bool
    ) -> bool:
        """迁移单个关系"""
        try:
            # 检查源实体和目标实体是否存在于图数据库
            source_exists = await self.storage_orchestrator.graph_service.get_entity(
                relationship.source_entity
            )
            target_exists = await self.storage_orchestrator.graph_service.get_entity(
                relationship.target_entity
            )

            if not source_exists:
                logger.warning(
                    f"源实体不存在，跳过关系: {relationship.source_entity} -> {relationship.target_entity}"
                )
                return False

            if not target_exists:
                logger.warning(
                    f"目标实体不存在，跳过关系: {relationship.source_entity} -> {relationship.target_entity}"
                )
                return False

            # 使用存储编排器创建关系
            success = await self.storage_orchestrator.create_relationship(
                source_entity=relationship.source_entity,
                target_entity=relationship.target_entity,
                relationship_type=relationship.relationship_type,
                strength=relationship.strength,
                confidence=relationship.confidence,
                attributes=relationship.relationship_data or {},
            )

            if success:
                logger.debug(
                    f"迁移关系成功: {relationship.source_entity} -> {relationship.target_entity}"
                )
            else:
                logger.warning(
                    f"迁移关系失败: {relationship.source_entity} -> {relationship.target_entity}"
                )

            return success

        except Exception as e:
            logger.error(f"迁移关系失败: {e}")
            return False

    async def _validate_migration(self):
        """验证迁移结果"""
        try:
            logger.info("验证迁移结果...")

            # 获取图数据库统计信息
            graph_metrics = await self.storage_orchestrator.graph_service.get_metrics()
            vector_metrics = (
                await self.storage_orchestrator.vector_service.get_metrics()
            )

            logger.info(
                f"图数据库: {graph_metrics.node_count} 节点, {graph_metrics.edge_count} 边"
            )
            logger.info(f"向量数据库: {vector_metrics.total_vectors} 个向量")

            # 检查数据一致性
            consistency_errors = []

            # 检查实体数量一致性
            expected_entities = self.stats.migrated_entities
            actual_entities = graph_metrics.node_count
            if expected_entities != actual_entities:
                consistency_errors.append(
                    f"实体数量不一致: 期望 {expected_entities}, 实际 {actual_entities}"
                )

            # 检查关系数量一致性
            expected_relationships = self.stats.migrated_relationships
            actual_relationships = graph_metrics.edge_count
            if expected_relationships != actual_relationships:
                consistency_errors.append(
                    f"关系数量不一致: 期望 {expected_relationships}, 实际 {actual_relationships}"
                )

            if consistency_errors:
                logger.warning("发现数据一致性问题:")
                for error in consistency_errors:
                    logger.warning(f"  - {error}")
            else:
                logger.info("数据一致性验证通过")

        except Exception as e:
            logger.error(f"验证迁移结果失败: {e}")

    async def migrate_incremental(
        self, since: Optional[datetime] = None, auto_embed: bool = True
    ) -> MigrationStats:
        """增量迁移 - 迁移指定时间之后的数据"""
        try:
            logger.info("开始增量数据迁移...")
            self.stats = MigrationStats()
            self.stats.start_time = datetime.utcnow()

            if not since:
                # 默认迁移最近24小时的数据
                since = datetime.utcnow() - timedelta(days=1)

            with self.db_service.get_session() as session:
                # 查找新增或更新的实体
                new_entities = (
                    session.query(EntityMetadata)
                    .filter(
                        (EntityMetadata.created_at >= since)
                        | (EntityMetadata.updated_at >= since)
                    )
                    .all()
                )

                # 查找新增或更新的关系
                new_relationships = (
                    session.query(EntityRelationship)
                    .filter(
                        (EntityRelationship.created_at >= since)
                        | (EntityRelationship.updated_at >= since)
                    )
                    .all()
                )

                self.stats.total_entities = len(new_entities)
                self.stats.total_relationships = len(new_relationships)

                logger.info(
                    f"增量迁移: {self.stats.total_entities} 个实体, "
                    f"{self.stats.total_relationships} 个关系"
                )

                # 迁移实体
                for entity in new_entities:
                    success = await self._migrate_single_entity(
                        entity, auto_embed, force_rebuild=True
                    )
                    if success:
                        self.stats.migrated_entities += 1
                        if auto_embed and entity.description:
                            self.stats.migrated_embeddings += 1
                            self.stats.total_embeddings += 1
                    else:
                        self.stats.failed_entities += 1

                # 迁移关系
                for relationship in new_relationships:
                    success = await self._migrate_single_relationship(
                        relationship, force_rebuild=True
                    )
                    if success:
                        self.stats.migrated_relationships += 1
                    else:
                        self.stats.failed_relationships += 1

            # 同步存储层
            await self.storage_orchestrator.sync_all()

            self.stats.end_time = datetime.utcnow()
            logger.info(f"增量迁移完成，耗时 {self.stats.duration_seconds:.2f} 秒")

            return self.stats

        except Exception as e:
            logger.error(f"增量迁移失败: {e}")
            self.stats.end_time = datetime.utcnow()
            return self.stats

    async def check_migration_status(self) -> Dict[str, Any]:
        """检查迁移状态"""
        try:
            # 获取SQLite数据统计
            with self.db_service.get_session() as session:
                sqlite_entities = session.query(EntityMetadata).count()
                sqlite_relationships = session.query(EntityRelationship).count()

            # 获取图数据库统计
            graph_metrics = await self.storage_orchestrator.graph_service.get_metrics()
            vector_metrics = (
                await self.storage_orchestrator.vector_service.get_metrics()
            )

            # 计算迁移状态
            entity_migration_rate = 0.0
            if sqlite_entities > 0:
                entity_migration_rate = graph_metrics.node_count / sqlite_entities * 100

            relationship_migration_rate = 0.0
            if sqlite_relationships > 0:
                relationship_migration_rate = (
                    graph_metrics.edge_count / sqlite_relationships * 100
                )

            return {
                "sqlite_stats": {
                    "entities": sqlite_entities,
                    "relationships": sqlite_relationships,
                },
                "graph_stats": {
                    "nodes": graph_metrics.node_count,
                    "edges": graph_metrics.edge_count,
                },
                "vector_stats": {"documents": vector_metrics.total_vectors},
                "migration_rates": {
                    "entities": entity_migration_rate,
                    "relationships": relationship_migration_rate,
                },
                "needs_migration": (
                    entity_migration_rate < 100.0 or relationship_migration_rate < 100.0
                ),
            }

        except Exception as e:
            logger.error(f"检查迁移状态失败: {e}")
            return {"error": str(e)}


# 全局迁移服务实例
_migration_service: Optional[DataMigrationService] = None


async def get_migration_service() -> DataMigrationService:
    """获取迁移服务实例（单例模式）"""
    global _migration_service
    if _migration_service is None:
        _migration_service = DataMigrationService()
        await _migration_service.initialize()

    return _migration_service


async def cleanup_migration_service():
    """清理迁移服务"""
    global _migration_service
    if _migration_service:
        _migration_service = None
