"""
系统配置路由

处理系统级配置管理，包括连接器注册表等
使用服务层实现，完全脱离HTTP API依赖
"""

import logging

from ..ipc_protocol import (
    IPCRequest,
    IPCResponse,
    internal_error_response,
    success_response,
)
from ..ipc_router import IPCRouter
from ..system_config_service import get_system_config_service

logger = logging.getLogger(__name__)


def create_system_config_router() -> IPCRouter:
    """创建系统配置路由"""
    router = IPCRouter(prefix="/system-config")
    system_config_service = get_system_config_service()

    @router.get("/registry/connectors")
    async def get_registry_connectors(request: IPCRequest) -> IPCResponse:
        """获取注册表中的连接器列表"""
        try:
            result = await system_config_service.get_registry_connectors()

            if result["success"]:
                return success_response(result["data"])
            else:
                return internal_error_response(
                    result.get("error", "Unknown error"),
                    {"operation": "get_registry_connectors"},
                )

        except Exception as e:
            logger.error(f"获取注册表连接器失败: {e}")
            return internal_error_response(
                f"Failed to get registry connectors: {str(e)}",
                {"operation": "get_registry_connectors"},
            )

    @router.get("/registry/connectors/{connector_id}/download")
    async def get_connector_download_info(request: IPCRequest) -> IPCResponse:
        """获取连接器下载信息"""
        try:
            connector_id = request.path_params.get("connector_id")
            if not connector_id:
                return internal_error_response(
                    "Missing connector_id parameter",
                    {"operation": "get_connector_download_info"},
                )

            result = await system_config_service.get_connector_download_info(
                connector_id
            )

            if result["success"]:
                return success_response(result["data"])
            else:
                return internal_error_response(
                    result.get("error", "Unknown error"),
                    {"operation": "get_connector_download_info"},
                )

        except Exception as e:
            logger.error(f"获取连接器下载信息失败: {e}")
            return internal_error_response(
                f"Failed to get connector download info: {str(e)}",
                {"operation": "get_connector_download_info"},
            )

    @router.post("/registry/refresh")
    async def refresh_registry(request: IPCRequest) -> IPCResponse:
        """刷新注册表"""
        try:
            force = request.data.get("force", False)
            result = await system_config_service.refresh_registry(force=force)

            if result["success"]:
                return success_response(result["data"])
            else:
                return internal_error_response(
                    result.get("error", "Unknown error"),
                    {"operation": "refresh_registry"},
                )

        except Exception as e:
            logger.error(f"刷新注册表失败: {e}")
            return internal_error_response(
                f"Failed to refresh registry: {str(e)}",
                {"operation": "refresh_registry"},
            )

    @router.get("/registry")
    async def get_registry_config(request: IPCRequest) -> IPCResponse:
        """获取注册表配置"""
        try:
            result = await system_config_service.get_registry_config()

            if result["success"]:
                return success_response(result["data"])
            else:
                return internal_error_response(
                    result.get("error", "Unknown error"),
                    {"operation": "get_registry_config"},
                )

        except Exception as e:
            logger.error(f"获取注册表配置失败: {e}")
            return internal_error_response(
                f"Failed to get registry config: {str(e)}",
                {"operation": "get_registry_config"},
            )

    return router
