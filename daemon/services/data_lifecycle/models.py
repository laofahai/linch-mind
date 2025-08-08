#!/usr/bin/env python3
"""
数据生命周期管理的共享数据模型
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class DataTier(Enum):
    """数据分层枚举"""

    HOT = "hot"  # 最近3个月活跃数据
    WARM = "warm"  # 最近1年访问数据
    COLD = "cold"  # 历史归档数据


@dataclass
class DataCleanupSuggestion:
    """数据清理建议"""

    entity_id: str
    reason: str
    last_accessed: Optional[datetime]
    suggested_action: str
    impact_score: float  # 0-1, 影响程度

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "reason": self.reason,
            "last_accessed": (
                self.last_accessed.isoformat() if self.last_accessed else None
            ),
            "suggested_action": self.suggested_action,
            "impact_score": self.impact_score,
        }


@dataclass
class DataQualityReport:
    """数据质量报告"""

    score: float
    total_entities: int
    description_coverage: float
    relationship_coverage: float
    activity_rate: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": round(self.score, 2),
            "details": {
                "total_entities": self.total_entities,
                "description_coverage": round(self.description_coverage * 100, 1),
                "relationship_coverage": round(self.relationship_coverage * 100, 1),
                "activity_rate": round(self.activity_rate * 100, 1),
            },
        }


@dataclass
class TierStatistics:
    """数据分层统计"""

    hot: int
    warm: int
    cold: int

    def to_dict(self) -> Dict[str, Any]:
        return {"hot": self.hot, "warm": self.warm, "cold": self.cold}
