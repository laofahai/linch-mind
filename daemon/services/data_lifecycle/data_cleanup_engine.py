#!/usr/bin/env python3
"""
数据清理引擎
专注于识别和清理过期或无用的数据
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from sqlalchemy import and_, func, or_, select, text

from core.service_facade import get_service
from models.database_models import EntityMetadata, EntityRelationship
from services.unified_database_service import UnifiedDatabaseService as DatabaseService

from .models import DataCleanupSuggestion

logger = logging.getLogger(__name__)


class DataCleanupEngine:
    """数据清理引擎"""

    def __init__(self):
        self.db_service = get_service(DatabaseService)
        logger.info("DataCleanupEngine 初始化完成")

    def identify_cleanup_candidates(
        self, limit: int = 100
    ) -> List[DataCleanupSuggestion]:
        """识别清理候选数据"""
        candidates = []

        try:
            with self.db_service.get_session() as session:
                # 1. 长期未访问的数据（>2年）
                candidates.extend(self._find_stale_entities(session, limit // 2))

                # 2. 无关联的孤立实体
                candidates.extend(self._find_isolated_entities(session, limit // 4))

                # 3. 重复或相似的实体
                candidates.extend(self._find_duplicate_entities(session, limit // 4))

                logger.info(f"识别出 {len(candidates)} 个清理候选项")
                return candidates[:limit]

        except Exception as e:
            logger.error(f"识别清理候选数据失败: {e}")
            return []

    def _find_stale_entities(self, session, limit: int) -> List[DataCleanupSuggestion]:
        """查找长期未访问的实体"""
        candidates = []

        try:
            now = datetime.now(timezone.utc)
            stale_threshold = now - timedelta(days=730)  # 2年

            stale_entities = (
                session.execute(
                    select(EntityMetadata)
                    .where(
                        and_(
                            EntityMetadata.last_accessed < stale_threshold,
                            EntityMetadata.access_count < 5,  # 访问次数很少
                        )
                    )
                    .limit(limit)
                )
                .scalars()
                .all()
            )

            for entity in stale_entities:
                candidates.append(
                    DataCleanupSuggestion(
                        entity_id=entity.id,
                        reason="长期未访问且使用频率低",
                        last_accessed=entity.last_accessed,
                        suggested_action="考虑归档或删除",
                        impact_score=0.2,  # 低影响
                    )
                )

        except Exception as e:
            logger.error(f"查找长期未访问实体失败: {e}")

        return candidates

    def _find_isolated_entities(
        self, session, limit: int
    ) -> List[DataCleanupSuggestion]:
        """查找无关联的孤立实体"""
        candidates = []

        try:
            isolated_entities = (
                session.execute(
                    select(EntityMetadata)
                    .where(
                        and_(
                            ~EntityMetadata.id.in_(
                                select(EntityRelationship.source_entity).union(
                                    select(EntityRelationship.target_entity)
                                )
                            ),
                            EntityMetadata.access_count < 3,
                        )
                    )
                    .limit(limit)
                )
                .scalars()
                .all()
            )

            for entity in isolated_entities:
                candidates.append(
                    DataCleanupSuggestion(
                        entity_id=entity.id,
                        reason="孤立实体，无关联关系",
                        last_accessed=entity.last_accessed,
                        suggested_action="考虑删除",
                        impact_score=0.1,  # 很低影响
                    )
                )

        except Exception as e:
            logger.error(f"查找孤立实体失败: {e}")

        return candidates

    def _find_duplicate_entities(
        self, session, limit: int
    ) -> List[DataCleanupSuggestion]:
        """查找重复或相似的实体"""
        candidates = []

        try:
            # 查找名称相同但ID不同的实体
            duplicate_names = session.execute(
                select(EntityMetadata.name, func.count())
                .group_by(EntityMetadata.name)
                .having(func.count() > 1)
                .limit(limit // 2)
            ).all()

            for name, count in duplicate_names:
                duplicate_entities = (
                    session.execute(
                        select(EntityMetadata)
                        .where(EntityMetadata.name == name)
                        .limit(count)
                    )
                    .scalars()
                    .all()
                )

                if len(duplicate_entities) > 1:
                    # 按访问次数排序，保留最活跃的
                    sorted_entities = sorted(
                        duplicate_entities,
                        key=lambda x: x.access_count or 0,
                        reverse=True,
                    )

                    # 除了第一个，其他都是重复候选
                    for entity in sorted_entities[1:]:
                        candidates.append(
                            DataCleanupSuggestion(
                                entity_id=entity.id,
                                reason=f"可能与 {sorted_entities[0].id} 重复",
                                last_accessed=entity.last_accessed,
                                suggested_action="检查并考虑合并",
                                impact_score=0.3,  # 中低影响
                            )
                        )

        except Exception as e:
            logger.error(f"查找重复实体失败: {e}")

        return candidates

    def cleanup_expired_data(self, days_threshold: int = 1095) -> Dict[str, Any]:
        """清理过期数据（默认3年以上）"""
        try:
            cleanup_results = {
                "deleted_entities": 0,
                "deleted_relationships": 0,
                "deleted_behaviors": 0,
                "deleted_conversations": 0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_threshold)

            with self.db_service.get_session() as session:

                # 删除过期的行为记录（保留最近的分析数据）
                behavior_delete_result = session.execute(
                    text(
                        """
                        DELETE FROM user_behaviors
                        WHERE timestamp < :cutoff_date
                        AND session_id NOT IN (
                            SELECT DISTINCT session_id
                            FROM user_behaviors
                            WHERE timestamp >= :recent_threshold
                        )
                    """
                    ),
                    {
                        "cutoff_date": cutoff_date,
                        "recent_threshold": datetime.now(timezone.utc)
                        - timedelta(days=30),
                    },
                )
                cleanup_results["deleted_behaviors"] = behavior_delete_result.rowcount

                # 删除过期的对话记录（保留重要对话）
                conversation_delete_result = session.execute(
                    text(
                        """
                        DELETE FROM ai_conversations
                        WHERE timestamp < :cutoff_date
                        AND satisfaction_rating IS NULL
                        AND message_type != 'important'
                    """
                    ),
                    {"cutoff_date": cutoff_date},
                )
                cleanup_results["deleted_conversations"] = (
                    conversation_delete_result.rowcount
                )

                # 删除无用的关系（连接到已删除实体的关系）
                relationship_cleanup_result = session.execute(
                    text(
                        """
                        DELETE FROM entity_relationships
                        WHERE source_entity NOT IN (SELECT id FROM entity_metadata)
                        OR target_entity NOT IN (SELECT id FROM entity_metadata)
                    """
                    )
                )
                cleanup_results["deleted_relationships"] = (
                    relationship_cleanup_result.rowcount
                )

                # 运行清理优化
                session.execute(text("VACUUM"))
                session.execute(text("PRAGMA optimize"))

                logger.info(f"过期数据清理完成: {cleanup_results}")
                return cleanup_results

        except Exception as e:
            logger.error(f"清理过期数据失败: {e}")
            return {"error": str(e)}

    def cleanup_orphaned_relationships(self) -> Dict[str, Any]:
        """清理孤儿关系（指向不存在实体的关系）"""
        try:
            with self.db_service.get_session() as session:
                cleanup_result = session.execute(
                    text(
                        """
                        DELETE FROM entity_relationships
                        WHERE source_entity NOT IN (SELECT id FROM entity_metadata)
                        OR target_entity NOT IN (SELECT id FROM entity_metadata)
                    """
                    )
                )

                deleted_count = cleanup_result.rowcount

                # 运行优化
                session.execute(text("PRAGMA optimize"))

                logger.info(f"清理孤儿关系完成，删除 {deleted_count} 条记录")

                return {
                    "deleted_relationships": deleted_count,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            logger.error(f"清理孤儿关系失败: {e}")
            return {"error": str(e)}

    def get_cleanup_statistics(self) -> Dict[str, Any]:
        """获取清理统计信息"""
        try:
            with self.db_service.get_session() as session:
                now = datetime.now(timezone.utc)

                # 可清理的数据统计
                stale_threshold = now - timedelta(days=730)
                stale_entities = (
                    session.scalar(
                        select(func.count())
                        .select_from(EntityMetadata)
                        .where(
                            and_(
                                EntityMetadata.last_accessed < stale_threshold,
                                EntityMetadata.access_count < 5,
                            )
                        )
                    )
                    or 0
                )

                isolated_entities = (
                    session.scalar(
                        select(func.count())
                        .select_from(EntityMetadata)
                        .where(
                            ~EntityMetadata.id.in_(
                                select(EntityRelationship.source_entity).union(
                                    select(EntityRelationship.target_entity)
                                )
                            )
                        )
                    )
                    or 0
                )

                # 孤儿关系统计
                orphaned_relationships = (
                    session.scalar(
                        select(func.count())
                        .select_from(EntityRelationship)
                        .where(
                            or_(
                                ~EntityRelationship.source_entity.in_(
                                    select(EntityMetadata.id)
                                ),
                                ~EntityRelationship.target_entity.in_(
                                    select(EntityMetadata.id)
                                ),
                            )
                        )
                    )
                    or 0
                )

                return {
                    "stale_entities": stale_entities,
                    "isolated_entities": isolated_entities,
                    "orphaned_relationships": orphaned_relationships,
                    "total_cleanup_candidates": stale_entities + isolated_entities,
                    "cleanup_potential_mb": round(
                        (stale_entities + isolated_entities) * 0.001, 2
                    ),  # 估算
                }

        except Exception as e:
            logger.error(f"获取清理统计失败: {e}")
            return {"error": str(e)}
