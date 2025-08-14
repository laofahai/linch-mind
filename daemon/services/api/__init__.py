"""
API服务模块 - 对外提供数据查询和分析接口
"""

from .data_insights_service import DataInsightsService
from core.service_facade import get_data_insights_service

__all__ = [
    'DataInsightsService',
    'get_data_insights_service'
]