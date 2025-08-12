#!/usr/bin/env python3
"""
数据健康监控器
专门负责数据健康报告和监控功能
从data_lifecycle_manager.py中拆分出来
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from core.service_facade import get_database_service
from models.database_models import (
    AIConversation,
    EntityMetadata,
    EntityRelationship,
    UserBehavior,
)

logger = logging.getLogger(__name__)


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


class DataHealthMonitor:
    """数据健康监控器"""

    def __init__(self, config):
        self.config = config
        self.db_service = None
        self._last_report = None

    async def initialize(self):
        """初始化健康监控器"""
        try:
            self.db_service = get_database_service()
            logger.info("数据健康监控器初始化完成")
            return True
        except Exception as e:
            logger.error(f"数据健康监控器初始化失败: {e}")
            return False

    async def generate_health_report(self) -> DataHealthReport:
        """生成数据健康报告"""
        try:
            logger.info("生成数据健康报告...")

            # 收集基础统计信息
            basic_stats = await self._collect_basic_statistics()
            
            # 收集数据质量指标
            quality_metrics = await self._analyze_data_quality()
            
            # 收集性能指标
            performance_metrics = await self._analyze_performance()
            
            # 收集存储信息
            storage_info = await self._analyze_storage_usage()

            # 计算健康分数
            health_score = self._calculate_health_score({
                **basic_stats,
                **quality_metrics,
                **performance_metrics,
                **storage_info
            })

            # 创建报告
            report = DataHealthReport(
                # 基础统计
                total_entities=basic_stats.get("total_entities", 0),
                total_relationships=basic_stats.get("total_relationships", 0),
                total_behaviors=basic_stats.get("total_behaviors", 0),
                total_conversations=basic_stats.get("total_conversations", 0),
                
                # 存储信息
                storage_usage_mb=storage_info.get("usage_mb", 0.0),
                storage_usage_percentage=storage_info.get("usage_percentage", 0.0),
                
                # 数据质量
                orphaned_entities=quality_metrics.get("orphaned_entities", 0),
                duplicate_relationships=quality_metrics.get("duplicate_relationships", 0),
                invalid_vectors=quality_metrics.get("invalid_vectors", 0),
                broken_references=quality_metrics.get("broken_references", 0),
                
                # 性能指标
                avg_query_time_ms=performance_metrics.get("avg_query_time_ms", 0.0),
                cache_hit_rate=performance_metrics.get("cache_hit_rate", 0.0),
                index_efficiency=performance_metrics.get("index_efficiency", 0.0),
                
                # 清理统计（从上次报告继承）
                cleaned_entities=0,
                cleaned_behaviors=0,
                cleaned_conversations=0,
                archived_items=0,
                
                # 时间戳
                last_cleanup=datetime.utcnow(),
                last_optimization=datetime.utcnow(),
                health_score=health_score,
            )

            self._last_report = report
            logger.info(f"数据健康报告生成完成，健康分数: {health_score:.1f}")
            
            return report

        except Exception as e:
            logger.error(f"生成数据健康报告失败: {e}")
            # 返回默认报告
            return DataHealthReport(
                total_entities=0, total_relationships=0, total_behaviors=0,
                total_conversations=0, storage_usage_mb=0.0, storage_usage_percentage=0.0,
                orphaned_entities=0, duplicate_relationships=0, invalid_vectors=0,
                broken_references=0, avg_query_time_ms=0.0, cache_hit_rate=0.0,
                index_efficiency=0.0, cleaned_entities=0, cleaned_behaviors=0,
                cleaned_conversations=0, archived_items=0,
                last_cleanup=datetime.utcnow(), last_optimization=datetime.utcnow(),
                health_score=0.0
            )

    async def _collect_basic_statistics(self) -> Dict:
        """收集基础统计信息"""
        try:
            if not self.db_service:
                return {}

            stats = {}

            with self.db_service.get_session() as session:
                # 统计各类数据数量
                stats["total_entities"] = session.query(EntityMetadata).count()
                stats["total_relationships"] = session.query(EntityRelationship).count()
                stats["total_behaviors"] = session.query(UserBehavior).count()
                stats["total_conversations"] = session.query(AIConversation).count()

            return stats

        except Exception as e:
            logger.error(f"收集基础统计失败: {e}")
            return {}

    async def _analyze_data_quality(self) -> Dict:
        """分析数据质量"""
        try:
            if not self.db_service:
                return {}

            quality = {}

            with self.db_service.get_session() as session:
                # 检查孤儿实体
                orphaned_entities_query = session.query(EntityMetadata).filter(
                    ~EntityMetadata.id.in_(
                        session.query(EntityRelationship.source_entity_id)
                        .union(session.query(EntityRelationship.target_entity_id))
                        .subquery()
                        .select()
                    )
                )
                quality["orphaned_entities"] = orphaned_entities_query.count()

                # 检查重复关系
                duplicate_relationships = session.execute("""
                    SELECT source_entity_id, target_entity_id, relationship_type, COUNT(*) as cnt
                    FROM entity_relationships 
                    GROUP BY source_entity_id, target_entity_id, relationship_type
                    HAVING COUNT(*) > 1
                """).fetchall()
                quality["duplicate_relationships"] = len(duplicate_relationships)

                # 检查破损引用
                broken_refs = session.query(EntityRelationship).filter(
                    ~EntityRelationship.source_entity_id.in_(
                        session.query(EntityMetadata.id).subquery().select()
                    ) |
                    ~EntityRelationship.target_entity_id.in_(
                        session.query(EntityMetadata.id).subquery().select()
                    )
                ).count()
                quality["broken_references"] = broken_refs

            # 无效向量检查（待实现）
            quality["invalid_vectors"] = 0

            return quality

        except Exception as e:
            logger.error(f"分析数据质量失败: {e}")
            return {}

    async def _analyze_performance(self) -> Dict:
        """分析性能指标"""
        try:
            performance = {}

            # 执行简单的查询性能测试
            test_queries = [
                "SELECT COUNT(*) FROM entity_metadata;",
                "SELECT COUNT(*) FROM entity_relationships;",
                "SELECT COUNT(*) FROM user_behaviors;",
            ]

            query_times = []
            for query in test_queries:
                try:
                    start_time = datetime.utcnow()
                    
                    with self.db_service.get_session() as session:
                        session.execute(query).fetchall()
                    
                    end_time = datetime.utcnow()
                    duration_ms = (end_time - start_time).total_seconds() * 1000
                    query_times.append(duration_ms)
                    
                except Exception as e:
                    logger.warning(f"性能测试查询失败: {query}: {e}")

            # 计算平均查询时间
            if query_times:
                performance["avg_query_time_ms"] = sum(query_times) / len(query_times)
            else:
                performance["avg_query_time_ms"] = 0.0

            # 其他性能指标（待实现）
            performance["cache_hit_rate"] = 0.0
            performance["index_efficiency"] = 0.0

            return performance

        except Exception as e:
            logger.error(f"分析性能指标失败: {e}")
            return {}

    async def _analyze_storage_usage(self) -> Dict:
        """分析存储使用情况"""
        try:
            storage = {}

            if not self.db_service:
                return {"usage_mb": 0.0, "usage_percentage": 0.0}

            # 获取数据库大小
            db_stats = self.db_service.get_database_stats()
            database_path = db_stats.get("database_path", "")

            if database_path and database_path.startswith("sqlite:///"):
                import os
                file_path = database_path.replace("sqlite:///", "")
                if os.path.exists(file_path):
                    size_bytes = os.path.getsize(file_path)
                    size_mb = size_bytes / (1024 * 1024)
                    
                    storage["usage_mb"] = size_mb
                    
                    # 计算使用百分比（基于配置的最大存储限制）
                    max_storage_mb = self.config.max_storage_gb * 1024
                    storage["usage_percentage"] = (size_mb / max_storage_mb) * 100
                else:
                    storage["usage_mb"] = 0.0
                    storage["usage_percentage"] = 0.0
            else:
                storage["usage_mb"] = 0.0
                storage["usage_percentage"] = 0.0

            return storage

        except Exception as e:
            logger.error(f"分析存储使用失败: {e}")
            return {"usage_mb": 0.0, "usage_percentage": 0.0}

    def _calculate_health_score(self, metrics: Dict) -> float:
        """计算健康分数 (0-100)"""
        try:
            score = 100.0

            # 存储使用扣分 (最多扣20分)
            storage_percentage = metrics.get("storage_usage_percentage", 0)
            if storage_percentage > 90:
                score -= 20
            elif storage_percentage > 75:
                score -= 15
            elif storage_percentage > 50:
                score -= 10

            # 数据质量扣分 (最多扣30分)
            orphaned_entities = metrics.get("orphaned_entities", 0)
            duplicate_relationships = metrics.get("duplicate_relationships", 0)
            broken_references = metrics.get("broken_references", 0)

            total_entities = metrics.get("total_entities", 1)
            total_relationships = metrics.get("total_relationships", 1)

            orphan_ratio = orphaned_entities / max(total_entities, 1)
            duplicate_ratio = duplicate_relationships / max(total_relationships, 1)
            broken_ratio = broken_references / max(total_relationships, 1)

            if orphan_ratio > 0.1:  # >10% 孤儿实体
                score -= 15
            elif orphan_ratio > 0.05:
                score -= 10

            if duplicate_ratio > 0.05:  # >5% 重复关系
                score -= 10

            if broken_ratio > 0.01:  # >1% 破损引用
                score -= 15

            # 性能扣分 (最多扣20分)
            avg_query_time = metrics.get("avg_query_time_ms", 0)
            if avg_query_time > 1000:  # >1秒
                score -= 20
            elif avg_query_time > 500:  # >500ms
                score -= 15
            elif avg_query_time > 100:  # >100ms
                score -= 10

            # 确保分数在0-100范围内
            return max(0.0, min(100.0, score))

        except Exception as e:
            logger.error(f"计算健康分数失败: {e}")
            return 50.0  # 默认中等健康分数

    def get_last_report(self) -> DataHealthReport:
        """获取上次的健康报告"""
        return self._last_report

    async def get_health_summary(self) -> Dict:
        """获取健康状况摘要"""
        try:
            if not self._last_report:
                report = await self.generate_health_report()
            else:
                report = self._last_report

            # 根据健康分数确定状态
            if report.health_score >= 90:
                status = "excellent"
                status_text = "优秀"
            elif report.health_score >= 75:
                status = "good"
                status_text = "良好"
            elif report.health_score >= 60:
                status = "fair"
                status_text = "一般"
            elif report.health_score >= 40:
                status = "poor"
                status_text = "较差"
            else:
                status = "critical"
                status_text = "危险"

            # 生成建议
            recommendations = []
            
            if report.storage_usage_percentage > 80:
                recommendations.append("存储空间不足，建议清理或归档旧数据")
            
            if report.orphaned_entities > 0:
                recommendations.append(f"发现{report.orphaned_entities}个孤儿实体，建议清理")
            
            if report.duplicate_relationships > 0:
                recommendations.append(f"发现{report.duplicate_relationships}个重复关系，建议去重")
            
            if report.avg_query_time_ms > 100:
                recommendations.append("查询性能较慢，建议优化数据库索引")

            return {
                "health_score": report.health_score,
                "status": status,
                "status_text": status_text,
                "summary": {
                    "total_records": (
                        report.total_entities + report.total_relationships +
                        report.total_behaviors + report.total_conversations
                    ),
                    "storage_usage_mb": report.storage_usage_mb,
                    "storage_usage_percentage": report.storage_usage_percentage,
                    "data_quality_issues": (
                        report.orphaned_entities + report.duplicate_relationships + 
                        report.broken_references
                    ),
                    "avg_query_time_ms": report.avg_query_time_ms,
                },
                "recommendations": recommendations,
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"获取健康摘要失败: {e}")
            return {
                "health_score": 0.0,
                "status": "unknown",
                "status_text": "未知",
                "summary": {},
                "recommendations": ["无法获取健康状况，请检查系统状态"],
                "last_updated": datetime.utcnow().isoformat(),
            }