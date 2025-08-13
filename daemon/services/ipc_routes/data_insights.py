"""
数据洞察路由

提供智能数据分析、实体查询和洞察展示的API接口
"""

import logging
from typing import Optional

from ..ipc_protocol import IPCRequest, IPCResponse
from ..ipc_router import IPCRouter
from core.service_facade import get_data_insights_service

logger = logging.getLogger(__name__)


def create_data_insights_router() -> IPCRouter:
    """创建数据洞察路由"""
    router = IPCRouter()
    insights_service = get_data_insights_service()

    @router.get("/data/dashboard")
    async def get_dashboard_overview(request: IPCRequest) -> IPCResponse:
        """获取仪表板概览数据"""
        try:
            overview = insights_service.get_dashboard_overview()
            return IPCResponse.success_response(
                data=overview,
                request_id=request.request_id,
            )
        except Exception as e:
            logger.error(f"获取仪表板概览失败: {e}")
            return IPCResponse.error_response(
                error_code="DASHBOARD_ERROR",
                message=f"Failed to get dashboard overview: {str(e)}",
                request_id=request.request_id,
            )

    @router.get("/data/insights")
    async def get_ai_insights(request: IPCRequest) -> IPCResponse:
        """获取AI智能洞察"""
        try:
            insights = insights_service.get_ai_insights()
            return IPCResponse.success_response(
                data=insights,
                request_id=request.request_id,
            )
        except Exception as e:
            logger.error(f"获取AI洞察失败: {e}")
            return IPCResponse.error_response(
                error_code="INSIGHTS_ERROR",
                message=f"Failed to get AI insights: {str(e)}",
                request_id=request.request_id,
            )

    @router.get("/data/entities")
    async def get_entities_by_type(request: IPCRequest) -> IPCResponse:
        """按类型获取实体数据"""
        try:
            # 从查询参数获取筛选条件
            query_params = request.query_params or {}
            entity_type = query_params.get("type", "")
            limit = int(query_params.get("limit", 20))
            offset = int(query_params.get("offset", 0))

            if not entity_type:
                return IPCResponse.error_response(
                    error_code="INVALID_PARAMS",
                    message="Missing required parameter: type",
                    request_id=request.request_id,
                )

            entities = insights_service.get_entities_by_type(entity_type, limit, offset)
            return IPCResponse.success_response(
                data=entities,
                request_id=request.request_id,
            )
        except ValueError as e:
            return IPCResponse.error_response(
                error_code="INVALID_PARAMS",
                message=f"Invalid parameter: {str(e)}",
                request_id=request.request_id,
            )
        except Exception as e:
            logger.error(f"获取实体数据失败: {e}")
            return IPCResponse.error_response(
                error_code="ENTITIES_ERROR",
                message=f"Failed to get entities: {str(e)}",
                request_id=request.request_id,
            )

    @router.get("/data/timeline")
    async def get_activity_timeline(request: IPCRequest) -> IPCResponse:
        """获取活动时间线"""
        try:
            query_params = request.query_params or {}
            limit = int(query_params.get("limit", 10))

            timeline = insights_service.get_activity_timeline(limit)
            return IPCResponse.success_response(
                data={"timeline": timeline},
                request_id=request.request_id,
            )
        except ValueError as e:
            return IPCResponse.error_response(
                error_code="INVALID_PARAMS",
                message=f"Invalid parameter: {str(e)}",
                request_id=request.request_id,
            )
        except Exception as e:
            logger.error(f"获取活动时间线失败: {e}")
            return IPCResponse.error_response(
                error_code="TIMELINE_ERROR",
                message=f"Failed to get activity timeline: {str(e)}",
                request_id=request.request_id,
            )

    @router.post("/data/search")
    async def search_entities(request: IPCRequest) -> IPCResponse:
        """搜索实体"""
        try:
            data = request.data or {}
            query = data.get("query", "").strip()
            entity_type = data.get("type")
            limit = int(data.get("limit", 20))

            if not query:
                return IPCResponse.error_response(
                    error_code="INVALID_PARAMS",
                    message="Missing required parameter: query",
                    request_id=request.request_id,
                )

            results = insights_service.search_entities(query, entity_type, limit)
            return IPCResponse.success_response(
                data={"results": results, "query": query},
                request_id=request.request_id,
            )
        except ValueError as e:
            return IPCResponse.error_response(
                error_code="INVALID_PARAMS",
                message=f"Invalid parameter: {str(e)}",
                request_id=request.request_id,
            )
        except Exception as e:
            logger.error(f"搜索实体失败: {e}")
            return IPCResponse.error_response(
                error_code="SEARCH_ERROR",
                message=f"Failed to search entities: {str(e)}",
                request_id=request.request_id,
            )

    @router.get("/insights/overview")
    async def get_insights_overview(request: IPCRequest) -> IPCResponse:
        """获取完整的数据洞察概览 - 专为UI层设计"""
        try:
            # 获取完整的洞察概览数据
            overview = insights_service.get_complete_insights_overview()
            return IPCResponse.success_response(
                data=overview,
                request_id=request.request_id,
            )
        except Exception as e:
            logger.error(f"获取完整洞察概览失败: {e}")
            return IPCResponse.error_response(
                error_code="OVERVIEW_ERROR", 
                message=f"Failed to get insights overview: {str(e)}",
                request_id=request.request_id,
            )

    @router.get("/data/stats")
    async def get_data_statistics(request: IPCRequest) -> IPCResponse:
        """获取数据统计信息"""
        try:
            # 组合仪表板概览和AI洞察提供完整统计
            overview = insights_service.get_dashboard_overview()
            ai_insights = insights_service.get_ai_insights()

            stats = {
                "overview": overview,
                "insights": ai_insights,
                "summary": {
                    "total_entities": overview.get("total_entities", 0),
                    "today_entities": overview.get("today_entities", 0),
                    "growth_rate": overview.get("growth_rate", 0),
                    "ai_confidence": ai_insights.get("confidence_score", 0),
                    "work_mode": ai_insights.get("work_patterns", {}).get("primary_work_mode", "unknown"),
                }
            }

            return IPCResponse.success_response(
                data=stats,
                request_id=request.request_id,
            )
        except Exception as e:
            logger.error(f"获取数据统计失败: {e}")
            return IPCResponse.error_response(
                error_code="STATS_ERROR",
                message=f"Failed to get data statistics: {str(e)}",
                request_id=request.request_id,
            )

    return router