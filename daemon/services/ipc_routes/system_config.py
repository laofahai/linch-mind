"""
系统配置路由

处理系统级配置管理，包括连接器注册表等
"""

import logging

from ..ipc_protocol import IPCRequest, IPCResponse, internal_error_response
from ..ipc_router import IPCRouter

logger = logging.getLogger(__name__)


def create_system_config_router() -> IPCRouter:
    """创建系统配置路由"""
    router = IPCRouter(prefix="/system-config")

    @router.get("/registry/connectors")
    async def get_registry_connectors(request: IPCRequest) -> IPCResponse:
        """获取注册表中的连接器列表"""
        try:
            # 导入系统配置API函数
            from daemon.api.routers.system_config_api import get_registry_connectors

            return await get_registry_connectors(request)
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
            from daemon.api.routers.system_config_api import get_connector_download_info

            return await get_connector_download_info(request)
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
            from daemon.api.routers.system_config_api import refresh_registry

            return await refresh_registry(request)
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
            from daemon.api.routers.system_config_api import get_registry_config

            return await get_registry_config(request)
        except Exception as e:
            logger.error(f"获取注册表配置失败: {e}")
            return internal_error_response(
                f"Failed to get registry config: {str(e)}",
                {"operation": "get_registry_config"},
            )

    return router
