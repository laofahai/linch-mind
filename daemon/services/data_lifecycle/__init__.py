#!/usr/bin/env python3
"""
数据生命周期管理模块
提供数据分层、清理和质量分析的统一接口
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from .data_tier_manager import DataTierManager
from .data_cleanup_engine import DataCleanupEngine
from .data_quality_analyzer import DataQualityAnalyzer
from .models import DataTier, DataCleanupSuggestion, DataQualityReport, TierStatistics

logger = logging.getLogger(__name__)


class IntelligentDataLifecycle:
    """智能数据生命周期管理主协调器
    
    整合数据分层、清理和质量分析功能
    遵循单一职责原则，每个组件专注于特定功能
    """

    def __init__(self):
        self.tier_manager = DataTierManager()
        self.cleanup_engine = DataCleanupEngine()
        self.quality_analyzer = DataQualityAnalyzer()
        
        logger.info("IntelligentDataLifecycle 主协调器初始化完成")

    def get_data_overview(self) -> Dict[str, Any]:
        """获取数据概览"""
        try:
            # 获取分层统计
            tier_stats = self.tier_manager.get_tier_statistics()
            
            # 获取质量报告
            quality_report = self.quality_analyzer.analyze_data_quality()
            
            # 获取清理统计
            cleanup_stats = self.cleanup_engine.get_cleanup_statistics()
            
            return {
                "total_entities": quality_report.total_entities,
                "data_tiers": tier_stats.to_dict(),
                "quality_score": quality_report.score,
                "quality_details": quality_report.to_dict()["details"],
                "cleanup_potential": {
                    "stale_entities": cleanup_stats.get("stale_entities", 0),
                    "isolated_entities": cleanup_stats.get("isolated_entities", 0),
                    "total_candidates": cleanup_stats.get("total_cleanup_candidates", 0)
                },
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取数据概览失败: {e}")
            return {"error": str(e)}

    def auto_tier_management(self) -> Dict[str, Any]:
        """自动数据分层管理"""
        return self.tier_manager.auto_tier_management()

    def identify_cleanup_candidates(self, limit: int = 100) -> List[DataCleanupSuggestion]:
        """识别清理候选数据"""
        return self.cleanup_engine.identify_cleanup_candidates(limit)

    def cleanup_expired_data(self, days_threshold: int = 1095) -> Dict[str, Any]:
        """清理过期数据"""
        return self.cleanup_engine.cleanup_expired_data(days_threshold)

    def get_data_quality_score(self) -> DataQualityReport:
        """获取数据质量评分"""
        return self.quality_analyzer.analyze_data_quality()

    def get_quality_insights(self) -> Dict[str, Any]:
        """获取质量分析洞察"""
        return self.quality_analyzer.get_quality_insights()

    def get_entities_by_tier(self, tier: DataTier, limit: int = 100) -> List[Dict[str, Any]]:
        """根据分层获取实体"""
        return self.tier_manager.get_entities_by_tier(tier, limit)

    def get_entity_quality_score(self, entity_id: str) -> Dict[str, Any]:
        """获取单个实体的质量评分"""
        return self.quality_analyzer.get_entity_quality_score(entity_id)

    def cleanup_orphaned_relationships(self) -> Dict[str, Any]:
        """清理孤儿关系"""
        return self.cleanup_engine.cleanup_orphaned_relationships()

    def run_comprehensive_maintenance(self) -> Dict[str, Any]:
        """运行综合维护"""
        try:
            maintenance_results = {
                "tier_management": self.auto_tier_management(),
                "orphan_cleanup": self.cleanup_orphaned_relationships(),
                "quality_check": self.get_quality_insights(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info("综合维护完成")
            return maintenance_results
            
        except Exception as e:
            logger.error(f"综合维护失败: {e}")
            return {"error": str(e)}


# 全局服务实例
_intelligent_data_lifecycle: Optional[IntelligentDataLifecycle] = None


def get_intelligent_data_lifecycle() -> IntelligentDataLifecycle:
    """获取智能数据生命周期服务实例（单例模式）"""
    global _intelligent_data_lifecycle
    if _intelligent_data_lifecycle is None:
        _intelligent_data_lifecycle = IntelligentDataLifecycle()
    return _intelligent_data_lifecycle


def cleanup_intelligent_data_lifecycle():
    """清理智能数据生命周期服务"""
    global _intelligent_data_lifecycle
    if _intelligent_data_lifecycle:
        _intelligent_data_lifecycle = None
        logger.info("IntelligentDataLifecycle 已清理")


# 导出主要类和函数
__all__ = [
    'IntelligentDataLifecycle',
    'DataTierManager',
    'DataCleanupEngine', 
    'DataQualityAnalyzer',
    'DataTier',
    'DataCleanupSuggestion',
    'DataQualityReport',
    'TierStatistics',
    'get_intelligent_data_lifecycle',
    'cleanup_intelligent_data_lifecycle'
]