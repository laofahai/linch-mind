"""
通用搜索路由 - 支持所有连接器类型的统一搜索API

重构说明 (2025-08-16):
- 替代原有的文件系统特定搜索接口
- 支持文件、URL、邮箱、电话等所有内容类型
- 保持Everything级别搜索性能
- 提供分层搜索策略 (hot/warm/cold)
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..ipc_protocol import IPCRequest, IPCResponse
from ..ipc_router import IPCRouter
from .generic_event_storage import get_generic_event_storage

logger = logging.getLogger(__name__)


def create_universal_search_router() -> IPCRouter:
    """创建通用搜索路由"""
    router = IPCRouter(prefix="/search")

    @router.post("/universal")
    async def universal_search(request: IPCRequest) -> IPCResponse:
        """
        通用搜索API - 支持所有连接器类型

        请求格式：
        {
            "query": "搜索关键词",
            "limit": 100,
            "content_types": ["file_path", "url", "email"],  // 可选
            "connector_ids": ["connector_1", "connector_2"],   // 可选，任意连接器ID
            "index_tiers": ["hot", "warm"],                   // 可选，性能优化
            "include_metadata": false                         // 可选，是否包含详细元数据
        }

        响应格式：
        {
            "results": [
                {
                    "id": "connector_id:content_type:hash",
                    "connector_id": "connector_id",
                    "content_type": "file_path",
                    "primary_key": "/Users/john/Documents/report.pdf",
                    "display_name": "report.pdf",
                    "searchable_text": "report.pdf Documents john",
                    "score": 8.5,
                    "structured_data": {...},
                    "metadata": {...},
                    "last_modified": "2025-08-15T19:00:00Z"
                }
            ],
            "total_results": 25,
            "search_time_ms": 4.2,
            "performance_tier": "hot"
        }
        """
        try:
            data = request.data or {}
            
            # 验证必需字段
            if "query" not in data:
                return IPCResponse.error_response(
                    "INVALID_REQUEST", "Missing required field: query"
                )
            
            query = data["query"]
            if not query or not query.strip():
                return IPCResponse.error_response(
                    "INVALID_REQUEST", "Query cannot be empty"
                )
            
            # 提取搜索参数
            limit = data.get("limit", 100)
            content_types = data.get("content_types", [])
            connector_ids = data.get("connector_ids", [])
            include_metadata = data.get("include_metadata", False)
            
            # 性能优化：根据查询复杂度智能选择索引层级
            index_tiers = data.get("index_tiers")
            if not index_tiers:
                # 智能层级选择
                if len(query.strip().split()) == 1 and len(query) < 50:
                    # 简单查询，优先使用热层
                    index_tiers = ["hot", "warm"]
                else:
                    # 复杂查询，使用所有层级
                    index_tiers = ["hot", "warm", "cold"]
            
            start_time = datetime.now()
            
            logger.info(f"🔍 执行通用搜索: query='{query}', types={content_types}, connectors={connector_ids}")
            
            # 获取存储服务并执行搜索
            storage = get_generic_event_storage()
            search_results = storage.search_universal_index(
                query=query,
                limit=limit,
                content_types=content_types,
                connector_ids=connector_ids,
                include_metadata=include_metadata
            )
            
            # 计算性能指标
            search_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # 确定性能层级
            performance_tier = "hot" if search_time_ms < 10 else ("warm" if search_time_ms < 100 else "cold")
            
            logger.info(f"🎯 搜索完成: {len(search_results)} 结果, 耗时 {search_time_ms:.1f}ms, 层级 {performance_tier}")
            
            return IPCResponse.success_response({
                "results": search_results,
                "total_results": len(search_results),
                "search_time_ms": round(search_time_ms, 2),
                "performance_tier": performance_tier,
                "query_info": {
                    "original_query": query,
                    "content_types_filtered": content_types,
                    "connector_ids_filtered": connector_ids,
                    "index_tiers_used": index_tiers
                }
            })
            
        except Exception as e:
            logger.error(f"❌ 通用搜索失败: {str(e)}")
            return IPCResponse.error_response(
                "SEARCH_ERROR", f"Search failed: {str(e)}"
            )

    @router.post("/by_connector")
    async def search_by_connector(request: IPCRequest) -> IPCResponse:
        """
        按连接器搜索 - 快捷接口

        请求格式：
        {
            "connector_id": "example_connector",
            "query": "report",
            "limit": 50
        }
        """
        try:
            data = request.data or {}
            
            # 验证必需字段
            required_fields = ["connector_id", "query"]
            for field in required_fields:
                if field not in data:
                    return IPCResponse.error_response(
                        "INVALID_REQUEST", f"Missing required field: {field}"
                    )
            
            connector_id = data["connector_id"]
            query = data["query"]
            limit = data.get("limit", 50)
            
            # 调用通用搜索，限定连接器
            storage = get_generic_event_storage()
            search_results = storage.search_universal_index(
                query=query,
                limit=limit,
                connector_ids=[connector_id]
            )
            
            return IPCResponse.success_response({
                "results": search_results,
                "connector_id": connector_id,
                "total_results": len(search_results)
            })
            
        except Exception as e:
            logger.error(f"❌ 按连接器搜索失败: {str(e)}")
            return IPCResponse.error_response(
                "SEARCH_ERROR", f"Connector search failed: {str(e)}"
            )

    @router.post("/by_content_type")
    async def search_by_content_type(request: IPCRequest) -> IPCResponse:
        """
        按内容类型搜索 - 快捷接口

        请求格式：
        {
            "content_type": "file_path",  // file_path | url | email | phone | text
            "query": "report",
            "limit": 50
        }
        """
        try:
            data = request.data or {}
            
            # 验证必需字段
            required_fields = ["content_type", "query"]
            for field in required_fields:
                if field not in data:
                    return IPCResponse.error_response(
                        "INVALID_REQUEST", f"Missing required field: {field}"
                    )
            
            content_type = data["content_type"]
            query = data["query"]
            limit = data.get("limit", 50)
            
            # 验证内容类型
            valid_types = ["file_path", "url", "email", "phone", "text", "contact", "document", "other"]
            if content_type not in valid_types:
                return IPCResponse.error_response(
                    "INVALID_REQUEST", f"Invalid content_type. Must be one of: {valid_types}"
                )
            
            # 调用通用搜索，限定内容类型
            storage = get_generic_event_storage()
            search_results = storage.search_universal_index(
                query=query,
                limit=limit,
                content_types=[content_type]
            )
            
            return IPCResponse.success_response({
                "results": search_results,
                "content_type": content_type,
                "total_results": len(search_results)
            })
            
        except Exception as e:
            logger.error(f"❌ 按内容类型搜索失败: {str(e)}")
            return IPCResponse.error_response(
                "SEARCH_ERROR", f"Content type search failed: {str(e)}"
            )

    @router.get("/stats")
    async def get_search_stats(request: IPCRequest) -> IPCResponse:
        """
        获取搜索统计信息

        响应格式：
        {
            "total_entries": 150000,
            "entries_by_tier": {
                "hot": 50000,
                "warm": 75000,
                "cold": 25000
            },
            "entries_by_type": {
                "file_path": 45000,
                "url": 30000,
                "email": 15000,
                "text": 60000
            },
            "entries_by_connector": {
                "connector_1": 45000,
                "connector_2": 30000,
                "connector_3": 75000
            },
            "search_requests": 2500,
            "avg_search_time_ms": 8.5,
            "database_size": 104857600
        }
        """
        try:
            storage = get_generic_event_storage()
            stats = storage.get_universal_index_stats()
            
            return IPCResponse.success_response(stats)
            
        except Exception as e:
            logger.error(f"❌ 获取搜索统计失败: {str(e)}")
            return IPCResponse.error_response(
                "STATS_ERROR", f"Failed to get stats: {str(e)}"
            )

    @router.post("/clear")
    async def clear_search_index(request: IPCRequest) -> IPCResponse:
        """
        清理搜索索引 - 管理接口

        请求格式：
        {
            "connector_id": "example_connector"  // 可选，清理特定连接器的索引
        }
        """
        try:
            data = request.data or {}
            connector_id = data.get("connector_id")
            
            # 这里应该添加权限验证，确保只有管理员可以清理
            # TODO: 实现权限验证
            
            from services.storage.universal_index_service import get_universal_index_service
            index_service = get_universal_index_service()
            
            success = index_service.clear_index(connector_id)
            
            if success:
                message = f"已清理索引: {connector_id}" if connector_id else "已清理全部索引"
                logger.info(f"🧹 {message}")
                return IPCResponse.success_response({
                    "message": message,
                    "connector_id": connector_id
                })
            else:
                return IPCResponse.error_response(
                    "CLEAR_ERROR", "Failed to clear index"
                )
            
        except Exception as e:
            logger.error(f"❌ 清理搜索索引失败: {str(e)}")
            return IPCResponse.error_response(
                "CLEAR_ERROR", f"Failed to clear index: {str(e)}"
            )

    @router.get("/performance")
    async def get_performance_metrics(request: IPCRequest) -> IPCResponse:
        """
        获取搜索性能指标 - 监控接口

        响应格式：
        {
            "search_performance": {
                "hot_tier_avg_ms": 3.2,
                "warm_tier_avg_ms": 25.8,
                "cold_tier_avg_ms": 180.5
            },
            "index_performance": {
                "indexing_rate_per_sec": 1500,
                "total_indexed_today": 25000
            },
            "system_health": {
                "database_health": "healthy",
                "memory_usage_mb": 85.6,
                "disk_usage_mb": 120.5
            }
        }
        """
        try:
            # 获取基础统计
            storage = get_generic_event_storage()
            stats = storage.get_universal_index_stats()
            
            # 构建性能指标
            performance_metrics = {
                "search_performance": {
                    "avg_search_time_ms": stats.get("avg_search_time_ms", 0),
                    "total_search_requests": stats.get("search_requests", 0),
                    "search_requests_per_hour": 0  # TODO: 实现小时级统计
                },
                "index_performance": {
                    "total_entries": stats.get("total_entries", 0),
                    "last_update": stats.get("last_update"),
                    "indexing_status": "active" if stats.get("total_entries", 0) > 0 else "idle"
                },
                "storage_breakdown": {
                    "entries_by_tier": stats.get("entries_by_tier", {}),
                    "entries_by_type": stats.get("entries_by_type", {}),
                    "entries_by_connector": stats.get("entries_by_connector", {})
                },
                "system_health": {
                    "database_size_mb": round(stats.get("database_size", 0) / (1024 * 1024), 2),
                    "status": "healthy" if stats.get("total_entries", 0) > 0 else "initializing"
                }
            }
            
            return IPCResponse.success_response(performance_metrics)
            
        except Exception as e:
            logger.error(f"❌ 获取性能指标失败: {str(e)}")
            return IPCResponse.error_response(
                "METRICS_ERROR", f"Failed to get performance metrics: {str(e)}"
            )

    return router