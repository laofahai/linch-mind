#!/usr/bin/env python3
"""
数据分层管理器
专注于数据的hot/warm/cold分层管理
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from sqlalchemy import and_, func, or_, select, text

from core.service_facade import get_service
from models.database_models import EntityMetadata
from services.unified_database_service import UnifiedDatabaseService as DatabaseService

from .models import DataTier, TierStatistics

logger = logging.getLogger(__name__)


class DataTierManager:
    """数据分层管理器"""

    def __init__(self):
        self.db_service = get_service(DatabaseService)

        # 数据分层阈值（基于现实使用模式）
        self.tier_thresholds = {
            DataTier.HOT: timedelta(days=90),  # 3个月
            DataTier.WARM: timedelta(days=365),  # 1年
            DataTier.COLD: timedelta(days=730),  # 2年
        }

        logger.info("DataTierManager 初始化完成")

    def get_tier_statistics(self) -> TierStatistics:
        """获取数据分层统计"""
        try:
            with self.db_service.get_session() as session:
                now = datetime.now(timezone.utc)
                hot_threshold = now - self.tier_thresholds[DataTier.HOT]
                warm_threshold = now - self.tier_thresholds[DataTier.WARM]

                # Hot数据：最近访问或新创建的数据
                hot_entities = (
                    session.scalar(
                        select(func.count())
                        .select_from(EntityMetadata)
                        .where(
                            or_(
                                EntityMetadata.last_accessed >= hot_threshold,
                                EntityMetadata.last_accessed.is_(None),  # 新创建的数据
                            )
                        )
                    )
                    or 0
                )

                # Warm数据：中等时间范围内访问的数据
                warm_entities = (
                    session.scalar(
                        select(func.count())
                        .select_from(EntityMetadata)
                        .where(
                            and_(
                                EntityMetadata.last_accessed < hot_threshold,
                                EntityMetadata.last_accessed >= warm_threshold,
                            )
                        )
                    )
                    or 0
                )

                # Cold数据：长期未访问的数据
                cold_entities = (
                    session.scalar(
                        select(func.count())
                        .select_from(EntityMetadata)
                        .where(EntityMetadata.last_accessed < warm_threshold)
                    )
                    or 0
                )

                return TierStatistics(
                    hot=hot_entities, warm=warm_entities, cold=cold_entities
                )

        except Exception as e:
            logger.error(f"获取数据分层统计失败: {e}")
            return TierStatistics(hot=0, warm=0, cold=0)

    def auto_tier_management(self) -> Dict[str, Any]:
        """自动数据分层管理"""
        try:
            results = {
                "moved_to_hot": 0,
                "moved_to_warm": 0,
                "moved_to_cold": 0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            with self.db_service.get_session() as session:
                now = datetime.now(timezone.utc)
                hot_threshold = now - self.tier_thresholds[DataTier.HOT]
                warm_threshold = now - self.tier_thresholds[DataTier.WARM]

                # Hot数据：最近访问且访问频率高
                hot_update_result = session.execute(
                    text(
                        """
                        UPDATE entity_metadata
                        SET relevance_score = 1.0
                        WHERE (last_accessed >= :hot_threshold OR last_accessed IS NULL)
                        AND access_count >= 5
                    """
                    ),
                    {"hot_threshold": hot_threshold},
                )
                results["moved_to_hot"] = hot_update_result.rowcount

                # Warm数据：中等访问频率
                warm_update_result = session.execute(
                    text(
                        """
                        UPDATE entity_metadata
                        SET relevance_score = 0.5
                        WHERE last_accessed < :hot_threshold
                        AND last_accessed >= :warm_threshold
                        AND access_count >= 2
                    """
                    ),
                    {"hot_threshold": hot_threshold, "warm_threshold": warm_threshold},
                )
                results["moved_to_warm"] = warm_update_result.rowcount

                # Cold数据：长期未访问
                cold_update_result = session.execute(
                    text(
                        """
                        UPDATE entity_metadata
                        SET relevance_score = 0.1
                        WHERE last_accessed < :warm_threshold
                        OR access_count < 2
                    """
                    ),
                    {"warm_threshold": warm_threshold},
                )
                results["moved_to_cold"] = cold_update_result.rowcount

                # 运行数据库优化
                session.execute(text("PRAGMA optimize"))

                logger.info(f"数据分层管理完成: {results}")
                return results

        except Exception as e:
            logger.error(f"自动数据分层管理失败: {e}")
            return {"error": str(e)}

    def get_entities_by_tier(self, tier: DataTier, limit: int = 100) -> list:
        """根据分层获取实体"""
        try:
            with self.db_service.get_session() as session:
                now = datetime.now(timezone.utc)

                if tier == DataTier.HOT:
                    threshold = now - self.tier_thresholds[DataTier.HOT]
                    entities = (
                        session.execute(
                            select(EntityMetadata)
                            .where(
                                or_(
                                    EntityMetadata.last_accessed >= threshold,
                                    EntityMetadata.last_accessed.is_(None),
                                )
                            )
                            .limit(limit)
                        )
                        .scalars()
                        .all()
                    )

                elif tier == DataTier.WARM:
                    hot_threshold = now - self.tier_thresholds[DataTier.HOT]
                    warm_threshold = now - self.tier_thresholds[DataTier.WARM]
                    entities = (
                        session.execute(
                            select(EntityMetadata)
                            .where(
                                and_(
                                    EntityMetadata.last_accessed < hot_threshold,
                                    EntityMetadata.last_accessed >= warm_threshold,
                                )
                            )
                            .limit(limit)
                        )
                        .scalars()
                        .all()
                    )

                else:  # COLD
                    threshold = now - self.tier_thresholds[DataTier.WARM]
                    entities = (
                        session.execute(
                            select(EntityMetadata)
                            .where(EntityMetadata.last_accessed < threshold)
                            .limit(limit)
                        )
                        .scalars()
                        .all()
                    )

                return [
                    {
                        "id": entity.id,
                        "name": entity.name,
                        "type": entity.entity_type,
                        "last_accessed": (
                            entity.last_accessed.isoformat()
                            if entity.last_accessed
                            else None
                        ),
                        "access_count": entity.access_count or 0,
                        "relevance_score": entity.relevance_score or 0.0,
                    }
                    for entity in entities
                ]

        except Exception as e:
            logger.error(f"根据分层获取实体失败: {e}")
            return []
