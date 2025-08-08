#!/usr/bin/env python3
"""
数据质量分析器
专注于分析数据质量并提供评分
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from sqlalchemy import and_, func, or_, select

from models.database_models import EntityMetadata, EntityRelationship
from services.optimized_sqlite_service import get_optimized_sqlite_service

from .models import DataQualityReport

logger = logging.getLogger(__name__)


class DataQualityAnalyzer:
    """数据质量分析器"""

    def __init__(self):
        self.db_service = get_optimized_sqlite_service()
        logger.info("DataQualityAnalyzer 初始化完成")

    def analyze_data_quality(self) -> DataQualityReport:
        """分析数据质量并生成报告"""
        try:
            with self.db_service.get_session() as session:
                # 基础统计
                total_entities = (
                    session.scalar(select(func.count()).select_from(EntityMetadata))
                    or 0
                )

                if total_entities == 0:
                    return DataQualityReport(
                        score=0.0,
                        total_entities=0,
                        description_coverage=0.0,
                        relationship_coverage=0.0,
                        activity_rate=0.0,
                    )

                # 描述完整性分析
                description_coverage = self._analyze_description_coverage(
                    session, total_entities
                )

                # 关系完整性分析
                relationship_coverage = self._analyze_relationship_coverage(
                    session, total_entities
                )

                # 数据活跃性分析
                activity_rate = self._analyze_activity_rate(session, total_entities)

                # 计算综合质量评分（0-1）
                quality_score = (
                    description_coverage * 0.3  # 描述完整性权重30%
                    + relationship_coverage * 0.4  # 关系完整性权重40%
                    + activity_rate * 0.3  # 数据活跃性权重30%
                )

                return DataQualityReport(
                    score=quality_score,
                    total_entities=total_entities,
                    description_coverage=description_coverage,
                    relationship_coverage=relationship_coverage,
                    activity_rate=activity_rate,
                )

        except Exception as e:
            logger.error(f"分析数据质量失败: {e}")
            return DataQualityReport(
                score=0.0,
                total_entities=0,
                description_coverage=0.0,
                relationship_coverage=0.0,
                activity_rate=0.0,
            )

    def _analyze_description_coverage(self, session, total_entities: int) -> float:
        """分析描述完整性"""
        try:
            # 有描述的实体数量
            entities_with_desc = (
                session.scalar(
                    select(func.count())
                    .select_from(EntityMetadata)
                    .where(
                        and_(
                            EntityMetadata.description.isnot(None),
                            EntityMetadata.description != "",
                        )
                    )
                )
                or 0
            )

            # 有意义描述的实体（长度>10字符）
            entities_with_meaningful_desc = (
                session.scalar(
                    select(func.count())
                    .select_from(EntityMetadata)
                    .where(func.length(EntityMetadata.description) > 10)
                )
                or 0
            )

            # 综合描述完整性评分
            basic_coverage = entities_with_desc / total_entities
            meaningful_coverage = entities_with_meaningful_desc / total_entities

            return basic_coverage * 0.4 + meaningful_coverage * 0.6

        except Exception as e:
            logger.error(f"分析描述完整性失败: {e}")
            return 0.0

    def _analyze_relationship_coverage(self, session, total_entities: int) -> float:
        """分析关系完整性"""
        try:
            # 有关系的实体数量
            entities_with_relations = (
                session.scalar(
                    select(
                        func.count(func.distinct(EntityRelationship.source_entity))
                    ).select_from(EntityRelationship)
                )
                or 0
            )

            # 多关系实体数量（>= 2个关系）
            entities_with_multiple_relations = (
                session.execute(
                    select(func.count()).select_from(
                        select(EntityRelationship.source_entity)
                        .select_from(EntityRelationship)
                        .group_by(EntityRelationship.source_entity)
                        .having(func.count() >= 2)
                        .subquery()
                    )
                ).scalar()
                or 0
            )

            # 关系质量评分（强度>0.5的关系比例）
            high_quality_relations = (
                session.scalar(
                    select(func.count())
                    .select_from(EntityRelationship)
                    .where(EntityRelationship.strength >= 0.5)
                )
                or 0
            )

            total_relations = (
                session.scalar(select(func.count()).select_from(EntityRelationship))
                or 1
            )

            # 综合关系完整性评分
            basic_coverage = min(entities_with_relations / total_entities, 1.0)
            depth_coverage = min(entities_with_multiple_relations / total_entities, 1.0)
            quality_ratio = high_quality_relations / total_relations

            return basic_coverage * 0.4 + depth_coverage * 0.3 + quality_ratio * 0.3

        except Exception as e:
            logger.error(f"分析关系完整性失败: {e}")
            return 0.0

    def _analyze_activity_rate(self, session, total_entities: int) -> float:
        """分析数据活跃性"""
        try:
            now = datetime.now(timezone.utc)

            # 最近30天活跃的实体
            recent_active = (
                session.scalar(
                    select(func.count())
                    .select_from(EntityMetadata)
                    .where(EntityMetadata.last_accessed >= now - timedelta(days=30))
                )
                or 0
            )

            # 最近90天活跃的实体
            medium_active = (
                session.scalar(
                    select(func.count())
                    .select_from(EntityMetadata)
                    .where(EntityMetadata.last_accessed >= now - timedelta(days=90))
                )
                or 0
            )

            # 有访问记录的实体
            ever_accessed = (
                session.scalar(
                    select(func.count())
                    .select_from(EntityMetadata)
                    .where(EntityMetadata.last_accessed.isnot(None))
                )
                or 0
            )

            # 综合活跃性评分
            recent_rate = recent_active / total_entities
            medium_rate = medium_active / total_entities
            access_rate = ever_accessed / total_entities

            return recent_rate * 0.5 + medium_rate * 0.3 + access_rate * 0.2

        except Exception as e:
            logger.error(f"分析数据活跃性失败: {e}")
            return 0.0

    def get_quality_insights(self) -> Dict[str, Any]:
        """获取质量分析洞察"""
        try:
            quality_report = self.analyze_data_quality()

            insights = []

            # 基于质量评分提供建议
            if quality_report.score < 0.3:
                insights.append("数据质量较低，建议重点改进描述和关系建设")
            elif quality_report.score < 0.6:
                insights.append("数据质量中等，有改进空间")
            else:
                insights.append("数据质量良好")

            # 具体建议
            if quality_report.description_coverage < 0.5:
                insights.append("建议为更多实体添加详细描述")

            if quality_report.relationship_coverage < 0.4:
                insights.append("建议建立更多实体间的关联关系")

            if quality_report.activity_rate < 0.3:
                insights.append("数据活跃度较低，可能需要清理无用数据")

            return {
                "quality_report": quality_report.to_dict(),
                "insights": insights,
                "recommendations": self._generate_recommendations(quality_report),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"获取质量洞察失败: {e}")
            return {"error": str(e)}

    def _generate_recommendations(self, report: DataQualityReport) -> List[str]:
        """生成改进建议"""
        recommendations = []

        # 基于各项指标生成具体建议
        if report.description_coverage < 0.4:
            recommendations.append("为缺少描述的实体添加详细说明")

        if report.relationship_coverage < 0.3:
            recommendations.append("增加实体间的关联关系建设")

        if report.activity_rate < 0.2:
            recommendations.append("清理长期未使用的数据")

        if report.total_entities < 100:
            recommendations.append("扩充知识库内容")
        elif report.total_entities > 50000:
            recommendations.append("考虑数据归档和优化")

        return recommendations

    def get_entity_quality_score(self, entity_id: str) -> Dict[str, Any]:
        """获取单个实体的质量评分"""
        try:
            with self.db_service.get_session() as session:
                entity = session.execute(
                    select(EntityMetadata).where(EntityMetadata.id == entity_id)
                ).scalar_one_or_none()

                if not entity:
                    return {"error": "实体不存在"}

                # 描述质量评分
                desc_score = 0.0
                if entity.description:
                    if len(entity.description) > 50:
                        desc_score = 1.0
                    elif len(entity.description) > 10:
                        desc_score = 0.6
                    else:
                        desc_score = 0.3

                # 关系质量评分
                relation_count = (
                    session.scalar(
                        select(func.count())
                        .select_from(EntityRelationship)
                        .where(
                            or_(
                                EntityRelationship.source_entity == entity_id,
                                EntityRelationship.target_entity == entity_id,
                            )
                        )
                    )
                    or 0
                )

                relation_score = min(relation_count / 5.0, 1.0)  # 5个关系为满分

                # 活跃性评分
                activity_score = 0.0
                if entity.last_accessed:
                    days_ago = (datetime.now(timezone.utc) - entity.last_accessed).days
                    if days_ago < 30:
                        activity_score = 1.0
                    elif days_ago < 90:
                        activity_score = 0.7
                    elif days_ago < 365:
                        activity_score = 0.4
                    else:
                        activity_score = 0.1

                # 综合评分
                overall_score = (
                    desc_score * 0.4 + relation_score * 0.4 + activity_score * 0.2
                )

                return {
                    "entity_id": entity_id,
                    "overall_score": round(overall_score, 2),
                    "description_score": round(desc_score, 2),
                    "relationship_score": round(relation_score, 2),
                    "activity_score": round(activity_score, 2),
                    "relationship_count": relation_count,
                    "access_count": entity.access_count or 0,
                    "last_accessed": (
                        entity.last_accessed.isoformat()
                        if entity.last_accessed
                        else None
                    ),
                }

        except Exception as e:
            logger.error(f"获取实体质量评分失败: {e}")
            return {"error": str(e)}
