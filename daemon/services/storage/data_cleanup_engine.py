#!/usr/bin/env python3
"""
数据清理引擎
专门负责数据清理相关功能
从data_lifecycle_manager.py中拆分出来
"""

import logging
from datetime import datetime, timedelta
from typing import Dict

from core.service_facade import get_database_service
from models.database_models import (
    AIConversation,
    EntityMetadata,
    EntityRelationship,
    UserBehavior,
)

logger = logging.getLogger(__name__)


class DataCleanupEngine:
    """数据清理引擎"""

    def __init__(self, config):
        self.config = config
        self.db_service = None

    async def initialize(self):
        """初始化清理引擎"""
        try:
            self.db_service = get_database_service()
            logger.info("数据清理引擎初始化完成")
            return True
        except Exception as e:
            logger.error(f"数据清理引擎初始化失败: {e}")
            return False

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
            cleanup_stats["relationships"] = await self._cleanup_orphaned_relationships()

            # 5. 清理无效向量
            cleanup_stats["vectors"] = await self._cleanup_invalid_vectors()

            logger.info(f"过期数据清理完成: {cleanup_stats}")
            return cleanup_stats

        except Exception as e:
            logger.error(f"清理过期数据失败: {e}")
            return cleanup_stats

    async def _cleanup_behaviors(self) -> int:
        """清理过期行为数据"""
        try:
            if not self.db_service:
                return 0

            cutoff_date = datetime.utcnow() - timedelta(
                days=self.config.behavior_retention_days
            )

            with self.db_service.get_session() as session:
                expired_behaviors = (
                    session.query(UserBehavior)
                    .filter(UserBehavior.created_at < cutoff_date)
                    .all()
                )

                count = len(expired_behaviors)
                for behavior in expired_behaviors:
                    session.delete(behavior)

                session.commit()

                logger.info(f"清理过期行为数据: {count} 条")
                return count

        except Exception as e:
            logger.error(f"清理行为数据失败: {e}")
            return 0

    async def _cleanup_conversations(self) -> int:
        """清理过期对话数据"""
        try:
            if not self.db_service:
                return 0

            cutoff_date = datetime.utcnow() - timedelta(
                days=self.config.conversation_retention_days
            )

            with self.db_service.get_session() as session:
                expired_conversations = (
                    session.query(AIConversation)
                    .filter(AIConversation.created_at < cutoff_date)
                    .all()
                )

                count = len(expired_conversations)
                for conversation in expired_conversations:
                    session.delete(conversation)

                session.commit()

                logger.info(f"清理过期对话数据: {count} 条")
                return count

        except Exception as e:
            logger.error(f"清理对话数据失败: {e}")
            return 0

    async def _cleanup_orphaned_entities(self) -> int:
        """清理孤儿实体"""
        try:
            if not self.db_service:
                return 0

            with self.db_service.get_session() as session:
                # 查找没有关系的孤儿实体
                orphaned_entities = (
                    session.query(EntityMetadata)
                    .filter(
                        ~EntityMetadata.id.in_(
                            session.query(EntityRelationship.source_entity_id)
                            .union(session.query(EntityRelationship.target_entity_id))
                            .subquery()
                            .select()
                        )
                    )
                    .all()
                )

                count = len(orphaned_entities)
                for entity in orphaned_entities:
                    session.delete(entity)

                session.commit()

                logger.info(f"清理孤儿实体: {count} 条")
                return count

        except Exception as e:
            logger.error(f"清理孤儿实体失败: {e}")
            return 0

    async def _cleanup_orphaned_relationships(self) -> int:
        """清理孤儿关系"""
        try:
            if not self.db_service:
                return 0

            with self.db_service.get_session() as session:
                # 查找引用不存在实体的关系
                orphaned_relationships = (
                    session.query(EntityRelationship)
                    .filter(
                        ~EntityRelationship.source_entity_id.in_(
                            session.query(EntityMetadata.id).subquery().select()
                        )
                        | ~EntityRelationship.target_entity_id.in_(
                            session.query(EntityMetadata.id).subquery().select()
                        )
                    )
                    .all()
                )

                count = len(orphaned_relationships)
                for relationship in orphaned_relationships:
                    session.delete(relationship)

                session.commit()

                logger.info(f"清理孤儿关系: {count} 条")
                return count

        except Exception as e:
            logger.error(f"清理孤儿关系失败: {e}")
            return 0

    async def _cleanup_invalid_vectors(self) -> int:
        """清理无效向量数据"""
        try:
            # 这里需要与向量服务集成
            # 目前返回0，等待向量服务重构完成
            logger.debug("向量清理功能待实现")
            return 0

        except Exception as e:
            logger.error(f"清理无效向量失败: {e}")
            return 0

    async def cleanup_by_storage_limit(self) -> Dict[str, int]:
        """基于存储限制清理数据"""
        cleanup_stats = {
            "entities": 0,
            "relationships": 0,
            "behaviors": 0,
            "conversations": 0,
        }

        try:
            # 检查存储使用量
            storage_usage = await self._get_storage_usage_mb()
            max_storage_mb = self.config.max_storage_gb * 1024

            if storage_usage <= max_storage_mb:
                logger.debug(f"存储使用量未超限: {storage_usage:.2f}MB / {max_storage_mb}MB")
                return cleanup_stats

            logger.info(
                f"存储使用量超限，开始清理: {storage_usage:.2f}MB > {max_storage_mb}MB"
            )

            # 按优先级清理数据
            # 1. 首先清理最旧的行为数据
            cleanup_stats["behaviors"] = await self._cleanup_oldest_behaviors(
                target_mb=(storage_usage - max_storage_mb) * 0.4
            )

            # 2. 清理最旧的对话数据
            cleanup_stats["conversations"] = await self._cleanup_oldest_conversations(
                target_mb=(storage_usage - max_storage_mb) * 0.3
            )

            # 3. 清理孤儿数据
            cleanup_stats["entities"] = await self._cleanup_orphaned_entities()
            cleanup_stats["relationships"] = await self._cleanup_orphaned_relationships()

            logger.info(f"存储限制清理完成: {cleanup_stats}")
            return cleanup_stats

        except Exception as e:
            logger.error(f"存储限制清理失败: {e}")
            return cleanup_stats

    async def _cleanup_oldest_behaviors(self, target_mb: float) -> int:
        """清理最旧的行为数据"""
        try:
            if not self.db_service or target_mb <= 0:
                return 0

            with self.db_service.get_session() as session:
                # 按时间顺序获取最旧的行为数据
                old_behaviors = (
                    session.query(UserBehavior)
                    .order_by(UserBehavior.created_at.asc())
                    .limit(int(target_mb * 100))  # 粗略估算需要删除的条数
                    .all()
                )

                count = len(old_behaviors)
                for behavior in old_behaviors:
                    session.delete(behavior)

                session.commit()

                logger.info(f"清理最旧行为数据: {count} 条")
                return count

        except Exception as e:
            logger.error(f"清理最旧行为数据失败: {e}")
            return 0

    async def _cleanup_oldest_conversations(self, target_mb: float) -> int:
        """清理最旧的对话数据"""
        try:
            if not self.db_service or target_mb <= 0:
                return 0

            with self.db_service.get_session() as session:
                old_conversations = (
                    session.query(AIConversation)
                    .order_by(AIConversation.created_at.asc())
                    .limit(int(target_mb * 10))  # 对话数据通常更大
                    .all()
                )

                count = len(old_conversations)
                for conversation in old_conversations:
                    session.delete(conversation)

                session.commit()

                logger.info(f"清理最旧对话数据: {count} 条")
                return count

        except Exception as e:
            logger.error(f"清理最旧对话数据失败: {e}")
            return 0

    async def _get_storage_usage_mb(self) -> float:
        """获取存储使用量(MB)"""
        try:
            if not self.db_service:
                return 0.0

            # 获取数据库文件大小
            db_stats = self.db_service.get_database_stats()
            database_path = db_stats.get("database_path", "")

            if database_path and database_path != ":memory:":
                import os
                if database_path.startswith("sqlite:///"):
                    file_path = database_path.replace("sqlite:///", "")
                    if os.path.exists(file_path):
                        size_bytes = os.path.getsize(file_path)
                        return size_bytes / (1024 * 1024)  # 转换为MB

            return 0.0

        except Exception as e:
            logger.error(f"获取存储使用量失败: {e}")
            return 0.0