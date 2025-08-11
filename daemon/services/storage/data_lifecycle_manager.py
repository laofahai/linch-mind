#!/usr/bin/env python3
"""
数据生命周期管理器 - 智能数据管理和优化
负责数据清理、归档、性能优化和监控
"""

import asyncio
import json
import logging
import os
import shutil
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

from core.service_facade import get_database_service
from models.database_models import (
    AIConversation,
    EntityMetadata,
    EntityRelationship,
    UserBehavior,
)

from .storage_orchestrator import get_storage_orchestrator

logger = logging.getLogger(__name__)


@dataclass
class DataLifecycleConfig:
    """数据生命周期配置"""

    # 数据保留策略
    entity_retention_days: int = 90  # 实体数据保留天数
    behavior_retention_days: int = 30  # 行为数据保留天数
    conversation_retention_days: int = 60  # 对话数据保留天数

    # 清理策略
    auto_cleanup_enabled: bool = True
    cleanup_interval_hours: int = 24
    max_storage_gb: float = 10.0  # 最大存储空间限制

    # 归档策略
    archive_enabled: bool = True
    archive_threshold_days: int = 30
    compressed_archive: bool = True

    # 性能优化
    auto_vacuum_enabled: bool = True
    index_optimization_enabled: bool = True
    cache_cleanup_enabled: bool = True


@dataclass
class DataHealthReport:
    """数据健康报告"""

    total_entities: int
    total_relationships: int
    total_behaviors: int
    total_conversations: int
    storage_usage_mb: float
    storage_usage_percentage: float

    # 数据质量指标
    orphaned_entities: int
    duplicate_relationships: int
    invalid_vectors: int
    broken_references: int

    # 性能指标
    avg_query_time_ms: float
    cache_hit_rate: float
    index_efficiency: float

    # 清理统计
    cleaned_entities: int
    cleaned_behaviors: int
    cleaned_conversations: int
    archived_items: int

    last_cleanup: datetime
    last_optimization: datetime
    health_score: float  # 0-100


class DataLifecycleManager:
    """数据生命周期管理器 - 智能数据管理"""

    def __init__(self, config: Optional[DataLifecycleConfig] = None):
        self.config = config or DataLifecycleConfig()
        self.storage_orchestrator = None
        self.db_service = None

        # 任务状态
        self._cleanup_task: Optional[asyncio.Task] = None
        self._optimization_task: Optional[asyncio.Task] = None
        self._running = False

        # 统计信息
        self._last_cleanup = datetime.utcnow()
        self._last_optimization = datetime.utcnow()
        self._health_report = DataHealthReport(
            total_entities=0,
            total_relationships=0,
            total_behaviors=0,
            total_conversations=0,
            storage_usage_mb=0.0,
            storage_usage_percentage=0.0,
            orphaned_entities=0,
            duplicate_relationships=0,
            invalid_vectors=0,
            broken_references=0,
            avg_query_time_ms=0.0,
            cache_hit_rate=0.0,
            index_efficiency=0.0,
            cleaned_entities=0,
            cleaned_behaviors=0,
            cleaned_conversations=0,
            archived_items=0,
            last_cleanup=datetime.utcnow(),
            last_optimization=datetime.utcnow(),
            health_score=100.0,
        )

    async def initialize(self) -> bool:
        """初始化数据生命周期管理器"""
        try:
            self.storage_orchestrator = await get_storage_orchestrator()
            self.db_service = get_database_service()

            # 启动自动任务
            if self.config.auto_cleanup_enabled:
                self._cleanup_task = asyncio.create_task(self._auto_cleanup_task())

            if (
                self.config.auto_vacuum_enabled
                or self.config.index_optimization_enabled
            ):
                self._optimization_task = asyncio.create_task(
                    self._auto_optimization_task()
                )

            self._running = True

            # 生成初始健康报告
            await self.generate_health_report()

            logger.info("数据生命周期管理器初始化完成")
            return True

        except Exception as e:
            logger.error(f"数据生命周期管理器初始化失败: {e}")
            return False

    async def close(self):
        """关闭数据生命周期管理器"""
        try:
            self._running = False

            # 取消自动任务
            if self._cleanup_task:
                self._cleanup_task.cancel()
            if self._optimization_task:
                self._optimization_task.cancel()

            logger.info("数据生命周期管理器已关闭")

        except Exception as e:
            logger.error(f"关闭数据生命周期管理器失败: {e}")

    # === 数据清理 ===

    async def cleanup_expired_data(self) -> Dict[str, int]:
        """清理过期数据"""
        cleanup_stats = {
            "entities": 0,
            "relationships": 0,
            "behaviors": 0,
            "conversations": 0,
            "vectors": 0,
        }

        try:
            logger.info("开始清理过期数据...")

            # 1. 清理过期行为数据
            if self.config.behavior_retention_days > 0:
                cleanup_stats["behaviors"] = await self._cleanup_behaviors()

            # 2. 清理过期对话数据
            if self.config.conversation_retention_days > 0:
                cleanup_stats["conversations"] = await self._cleanup_conversations()

            # 3. 清理孤儿实体
            cleanup_stats["entities"] = await self._cleanup_orphaned_entities()

            # 4. 清理孤儿关系
            cleanup_stats["relationships"] = (
                await self._cleanup_orphaned_relationships()
            )

            # 5. 清理无效向量
            cleanup_stats["vectors"] = await self._cleanup_invalid_vectors()

            # 更新统计
            self._last_cleanup = datetime.utcnow()
            self._health_report.last_cleanup = self._last_cleanup
            self._health_report.cleaned_entities = cleanup_stats["entities"]
            self._health_report.cleaned_behaviors = cleanup_stats["behaviors"]
            self._health_report.cleaned_conversations = cleanup_stats["conversations"]

            total_cleaned = sum(cleanup_stats.values())
            logger.info(f"数据清理完成，清理了 {total_cleaned} 条记录: {cleanup_stats}")

            return cleanup_stats

        except Exception as e:
            logger.error(f"数据清理失败: {e}")
            return cleanup_stats

    async def _cleanup_behaviors(self) -> int:
        """清理过期行为数据"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(
                days=self.config.behavior_retention_days
            )

            with self.db_service.get_session() as session:
                deleted_count = (
                    session.query(UserBehavior)
                    .filter(UserBehavior.timestamp < cutoff_date)
                    .delete()
                )
                session.commit()

                logger.debug(f"清理行为数据: {deleted_count} 条")
                return deleted_count

        except Exception as e:
            logger.error(f"清理行为数据失败: {e}")
            return 0

    async def _cleanup_conversations(self) -> int:
        """清理过期对话数据"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(
                days=self.config.conversation_retention_days
            )

            with self.db_service.get_session() as session:
                deleted_count = (
                    session.query(AIConversation)
                    .filter(AIConversation.timestamp < cutoff_date)
                    .delete()
                )
                session.commit()

                logger.debug(f"清理对话数据: {deleted_count} 条")
                return deleted_count

        except Exception as e:
            logger.error(f"清理对话数据失败: {e}")
            return 0

    async def _cleanup_orphaned_entities(self) -> int:
        """清理孤儿实体（无关系的长期未访问实体）"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(
                days=self.config.entity_retention_days
            )

            with self.db_service.get_session() as session:
                # 查找孤儿实体
                orphaned_entities = (
                    session.query(EntityMetadata)
                    .filter(
                        (EntityMetadata.last_accessed < cutoff_date)
                        | (EntityMetadata.last_accessed.is_(None)),
                        EntityMetadata.access_count < 5,  # 访问次数很少
                    )
                    .all()
                )

                deleted_count = 0
                for entity in orphaned_entities:
                    # 检查是否有关系
                    has_relationships = (
                        session.query(EntityRelationship)
                        .filter(
                            (EntityRelationship.source_entity == entity.id)
                            | (EntityRelationship.target_entity == entity.id)
                        )
                        .first()
                        is not None
                    )

                    if not has_relationships:
                        # 删除实体
                        await self.storage_orchestrator.delete_entity(entity.id)
                        deleted_count += 1

                logger.debug(f"清理孤儿实体: {deleted_count} 个")
                return deleted_count

        except Exception as e:
            logger.error(f"清理孤儿实体失败: {e}")
            return 0

    async def _cleanup_orphaned_relationships(self) -> int:
        """清理孤儿关系（引用不存在实体的关系）"""
        try:
            with self.db_service.get_session() as session:
                # 查找所有关系
                relationships = session.query(EntityRelationship).all()

                deleted_count = 0
                for rel in relationships:
                    # 检查源实体是否存在
                    source_exists = (
                        session.query(EntityMetadata)
                        .filter(EntityMetadata.id == rel.source_entity)
                        .first()
                        is not None
                    )

                    # 检查目标实体是否存在
                    target_exists = (
                        session.query(EntityMetadata)
                        .filter(EntityMetadata.id == rel.target_entity)
                        .first()
                        is not None
                    )

                    if not source_exists or not target_exists:
                        session.delete(rel)
                        deleted_count += 1

                session.commit()
                logger.debug(f"清理孤儿关系: {deleted_count} 条")
                return deleted_count

        except Exception as e:
            logger.error(f"清理孤儿关系失败: {e}")
            return 0

    async def _cleanup_invalid_vectors(self) -> int:
        """清理无效向量（无对应实体的向量）"""
        try:
            if not self.storage_orchestrator.vector_service:
                return 0

            deleted_count = 0
            vector_service = self.storage_orchestrator.vector_service

            # 获取所有向量文档
            if hasattr(vector_service, "id_to_doc"):
                for doc_id, doc in list(vector_service.id_to_doc.items()):
                    if doc.entity_id:
                        # 检查对应实体是否存在
                        entity = await self.storage_orchestrator.get_entity(
                            doc.entity_id
                        )
                        if not entity:
                            await vector_service.remove_document(doc_id)
                            deleted_count += 1

            logger.debug(f"清理无效向量: {deleted_count} 个")
            return deleted_count

        except Exception as e:
            logger.error(f"清理无效向量失败: {e}")
            return 0

    # === 数据归档 ===

    async def archive_old_data(self, archive_path: Optional[Path] = None) -> int:
        """归档旧数据"""
        try:
            if not self.config.archive_enabled:
                return 0

            if not archive_path:
                from config.core_config import get_data_config

                data_config = get_data_config()
                archive_path = Path(data_config.data_directory) / "archive"

            archive_path.mkdir(parents=True, exist_ok=True)

            cutoff_date = datetime.utcnow() - timedelta(
                days=self.config.archive_threshold_days
            )
            archived_count = 0

            # 归档对话数据
            with self.db_service.get_session() as session:
                old_conversations = (
                    session.query(AIConversation)
                    .filter(AIConversation.timestamp < cutoff_date)
                    .all()
                )

                if old_conversations:
                    archive_file = (
                        archive_path
                        / f"conversations_{datetime.utcnow().strftime('%Y%m%d')}.json"
                    )

                    conversations_data = []
                    for conv in old_conversations:
                        conversations_data.append(
                            {
                                "id": conv.id,
                                "session_id": conv.session_id,
                                "user_message": conv.user_message,
                                "ai_response": conv.ai_response,
                                "timestamp": conv.timestamp.isoformat(),
                                "message_type": conv.message_type,
                                "context_entities": conv.context_entities,
                            }
                        )

                    # 保存归档文件
                    with open(archive_file, "w", encoding="utf-8") as f:
                        json.dump(conversations_data, f, ensure_ascii=False, indent=2)

                    # 删除已归档的数据
                    session.query(AIConversation).filter(
                        AIConversation.timestamp < cutoff_date
                    ).delete()
                    session.commit()

                    archived_count += len(old_conversations)

                    # 压缩归档文件
                    if self.config.compressed_archive:
                        await self._compress_archive_file(archive_file)

            self._health_report.archived_items = archived_count
            logger.info(f"数据归档完成: {archived_count} 条记录")

            return archived_count

        except Exception as e:
            logger.error(f"数据归档失败: {e}")
            return 0

    async def _compress_archive_file(self, file_path: Path):
        """压缩归档文件"""
        try:
            import gzip

            compressed_path = file_path.with_suffix(file_path.suffix + ".gz")

            with open(file_path, "rb") as f_in:
                with gzip.open(compressed_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # 删除原文件
            file_path.unlink()

            logger.debug(f"归档文件已压缩: {compressed_path}")

        except Exception as e:
            logger.error(f"压缩归档文件失败: {e}")

    # === 性能优化 ===

    async def optimize_database(self) -> bool:
        """优化数据库性能"""
        try:
            logger.info("开始数据库优化...")

            # 1. 执行VACUUM
            if self.config.auto_vacuum_enabled:
                await self._vacuum_database()

            # 2. 优化索引
            if self.config.index_optimization_enabled:
                await self._optimize_indexes()

            # 3. 更新统计信息
            await self._update_statistics()

            # 4. 清理缓存
            if self.config.cache_cleanup_enabled:
                await self._cleanup_caches()

            self._last_optimization = datetime.utcnow()
            self._health_report.last_optimization = self._last_optimization

            logger.info("数据库优化完成")
            return True

        except Exception as e:
            logger.error(f"数据库优化失败: {e}")
            return False

    async def _vacuum_database(self):
        """执行数据库VACUUM操作"""
        try:
            # 获取数据库文件路径
            from config.core_config import get_database_config

            db_config = get_database_config()
            db_path = db_config.sqlite_url.replace("sqlite:///", "")

            # 直接连接SQLite执行VACUUM
            conn = sqlite3.connect(db_path)
            conn.execute("VACUUM")
            conn.close()

            logger.debug("数据库VACUUM完成")

        except Exception as e:
            logger.error(f"数据库VACUUM失败: {e}")

    async def _optimize_indexes(self):
        """优化数据库索引"""
        try:
            with self.db_service.get_session() as session:
                # 重建索引统计信息
                session.execute("ANALYZE")
                session.commit()

                logger.debug("索引优化完成")

        except Exception as e:
            logger.error(f"索引优化失败: {e}")

    async def _update_statistics(self):
        """更新数据库统计信息"""
        try:
            with self.db_service.get_session() as session:
                session.execute("PRAGMA optimize")
                session.commit()

                logger.debug("统计信息更新完成")

        except Exception as e:
            logger.error(f"更新统计信息失败: {e}")

    async def _cleanup_caches(self):
        """清理各级缓存"""
        try:
            # 清理存储编排器缓存
            if self.storage_orchestrator:
                self.storage_orchestrator._entity_cache.clear()
                self.storage_orchestrator._cache_timestamps.clear()

            # 清理图服务缓存
            if self.storage_orchestrator.graph_service:
                self.storage_orchestrator.graph_service._invalidate_cache()

            logger.debug("缓存清理完成")

        except Exception as e:
            logger.error(f"缓存清理失败: {e}")

    # === 健康监控 ===

    async def generate_health_report(self) -> DataHealthReport:
        """生成数据健康报告"""
        try:
            logger.debug("生成数据健康报告...")

            # 获取基础数据统计
            with self.db_service.get_session() as session:
                self._health_report.total_entities = session.query(
                    EntityMetadata
                ).count()
                self._health_report.total_relationships = session.query(
                    EntityRelationship
                ).count()
                self._health_report.total_behaviors = session.query(
                    UserBehavior
                ).count()
                self._health_report.total_conversations = session.query(
                    AIConversation
                ).count()

            # 获取存储使用情况
            await self._calculate_storage_usage()

            # 检查数据质量
            await self._analyze_data_quality()

            # 评估性能指标
            await self._analyze_performance()

            # 计算健康分数
            self._calculate_health_score()

            logger.debug("数据健康报告生成完成")
            return self._health_report

        except Exception as e:
            logger.error(f"生成健康报告失败: {e}")
            return self._health_report

    async def _calculate_storage_usage(self):
        """计算存储使用情况"""
        try:
            # 获取数据库文件大小
            from config.core_config import get_database_config

            db_config = get_database_config()
            db_path = db_config.sqlite_url.replace("sqlite:///", "")

            if os.path.exists(db_path):
                db_size = os.path.getsize(db_path)
                self._health_report.storage_usage_mb = db_size / (1024 * 1024)

            # 添加向量和图数据大小
            if self.storage_orchestrator:
                storage_metrics = await self.storage_orchestrator.get_metrics()
                self._health_report.storage_usage_mb = storage_metrics.storage_usage_mb

            # 计算使用百分比
            max_storage_mb = self.config.max_storage_gb * 1024
            self._health_report.storage_usage_percentage = (
                self._health_report.storage_usage_mb / max_storage_mb * 100
            )

        except Exception as e:
            logger.error(f"计算存储使用情况失败: {e}")

    async def _analyze_data_quality(self):
        """分析数据质量"""
        try:
            with self.db_service.get_session() as session:
                # 检查孤儿实体
                total_entities = session.query(EntityMetadata).count()
                entities_with_relationships = (
                    session.query(EntityMetadata.id)
                    .join(
                        EntityRelationship,
                        (EntityMetadata.id == EntityRelationship.source_entity)
                        | (EntityMetadata.id == EntityRelationship.target_entity),
                    )
                    .distinct()
                    .count()
                )

                self._health_report.orphaned_entities = (
                    total_entities - entities_with_relationships
                )

                # 检查重复关系
                total_relationships = session.query(EntityRelationship).count()
                unique_relationships = (
                    session.query(
                        EntityRelationship.source_entity,
                        EntityRelationship.target_entity,
                        EntityRelationship.relationship_type,
                    )
                    .distinct()
                    .count()
                )

                self._health_report.duplicate_relationships = (
                    total_relationships - unique_relationships
                )

                # 检查断开的引用
                broken_refs = 0
                relationships = session.query(EntityRelationship).all()

                for rel in relationships:
                    source_exists = (
                        session.query(EntityMetadata)
                        .filter(EntityMetadata.id == rel.source_entity)
                        .first()
                        is not None
                    )

                    target_exists = (
                        session.query(EntityMetadata)
                        .filter(EntityMetadata.id == rel.target_entity)
                        .first()
                        is not None
                    )

                    if not source_exists or not target_exists:
                        broken_refs += 1

                self._health_report.broken_references = broken_refs

        except Exception as e:
            logger.error(f"分析数据质量失败: {e}")

    async def _analyze_performance(self):
        """分析性能指标"""
        try:
            # 简化版本 - 实际实现可以更复杂
            self._health_report.avg_query_time_ms = 50.0  # 模拟值
            self._health_report.cache_hit_rate = 0.85  # 模拟值
            self._health_report.index_efficiency = 0.90  # 模拟值

        except Exception as e:
            logger.error(f"分析性能指标失败: {e}")

    def _calculate_health_score(self):
        """计算健康分数（0-100）"""
        try:
            score = 100.0

            # 存储使用情况扣分
            if self._health_report.storage_usage_percentage > 90:
                score -= 20
            elif self._health_report.storage_usage_percentage > 75:
                score -= 10

            # 数据质量扣分
            total_data = (
                self._health_report.total_entities
                + self._health_report.total_relationships
            )

            if total_data > 0:
                quality_issues = (
                    self._health_report.orphaned_entities
                    + self._health_report.duplicate_relationships
                    + self._health_report.broken_references
                )

                quality_ratio = quality_issues / total_data
                score -= quality_ratio * 30

            # 性能指标扣分
            if self._health_report.avg_query_time_ms > 100:
                score -= 15

            if self._health_report.cache_hit_rate < 0.7:
                score -= 10

            self._health_report.health_score = max(0, min(100, score))

        except Exception as e:
            logger.error(f"计算健康分数失败: {e}")
            self._health_report.health_score = 50.0

    # === 自动任务 ===

    async def _auto_cleanup_task(self):
        """自动清理任务"""
        while self._running:
            try:
                # 等待指定间隔
                await asyncio.sleep(self.config.cleanup_interval_hours * 3600)

                if not self._running:
                    break

                # 执行清理
                await self.cleanup_expired_data()

                # 检查存储空间
                if self._health_report.storage_usage_percentage > 90:
                    logger.warning("存储空间不足，执行紧急清理")
                    await self.emergency_cleanup()

            except Exception as e:
                logger.error(f"自动清理任务异常: {e}")
                await asyncio.sleep(3600)  # 出错时等待1小时

    async def _auto_optimization_task(self):
        """自动优化任务"""
        while self._running:
            try:
                # 每天优化一次
                await asyncio.sleep(24 * 3600)

                if not self._running:
                    break

                # 执行优化
                await self.optimize_database()

            except Exception as e:
                logger.error(f"自动优化任务异常: {e}")
                await asyncio.sleep(6 * 3600)  # 出错时等待6小时

    async def emergency_cleanup(self) -> bool:
        """紧急清理 - 存储空间不足时"""
        try:
            logger.warning("执行紧急清理...")

            # 1. 清理所有缓存
            await self._cleanup_caches()

            # 2. 强制清理过期数据（缩短保留期）
            original_config = self.config

            # 临时减少保留期
            self.config.behavior_retention_days = max(
                7, self.config.behavior_retention_days // 2
            )
            self.config.conversation_retention_days = max(
                14, self.config.conversation_retention_days // 2
            )

            await self.cleanup_expired_data()

            # 3. 清理低价值数据
            await self._cleanup_low_value_data()

            # 4. 压缩数据库
            await self._vacuum_database()

            # 恢复原配置
            self.config = original_config

            logger.info("紧急清理完成")
            return True

        except Exception as e:
            logger.error(f"紧急清理失败: {e}")
            return False

    async def _cleanup_low_value_data(self):
        """清理低价值数据"""
        try:
            with self.db_service.get_session() as session:
                # 删除访问次数很少且很久没访问的实体
                cutoff_date = datetime.utcnow() - timedelta(days=7)

                low_value_entities = (
                    session.query(EntityMetadata)
                    .filter(
                        EntityMetadata.access_count <= 1,
                        (EntityMetadata.last_accessed < cutoff_date)
                        | (EntityMetadata.last_accessed.is_(None)),
                    )
                    .all()
                )

                deleted_count = 0
                for entity in low_value_entities:
                    await self.storage_orchestrator.delete_entity(entity.id)
                    deleted_count += 1

                logger.info(f"紧急清理低价值数据: {deleted_count} 个实体")

        except Exception as e:
            logger.error(f"清理低价值数据失败: {e}")


# 全局数据生命周期管理器实例
_lifecycle_manager: Optional[DataLifecycleManager] = None


async def get_lifecycle_manager() -> DataLifecycleManager:
    """获取数据生命周期管理器实例（单例模式）"""
    global _lifecycle_manager
    if _lifecycle_manager is None:
        from config.core_config import get_storage_config

        storage_config = get_storage_config()

        # 从存储配置创建生命周期配置
        lifecycle_config = DataLifecycleConfig(
            entity_retention_days=storage_config.entity_retention_days,
            behavior_retention_days=storage_config.behavior_retention_days,
            conversation_retention_days=storage_config.conversation_retention_days,
            auto_cleanup_enabled=storage_config.auto_cleanup_enabled,
            cleanup_interval_hours=storage_config.cleanup_interval_hours,
            max_storage_gb=storage_config.max_storage_gb,
        )

        _lifecycle_manager = DataLifecycleManager(lifecycle_config)
        await _lifecycle_manager.initialize()

    return _lifecycle_manager


async def cleanup_lifecycle_manager():
    """清理数据生命周期管理器"""
    global _lifecycle_manager
    if _lifecycle_manager:
        await _lifecycle_manager.close()
        _lifecycle_manager = None
