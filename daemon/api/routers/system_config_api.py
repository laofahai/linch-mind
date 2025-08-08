"""
系统配置API - 纯IPC实现
"""

import logging

from config.core_config import get_core_config
from services.ipc_router import IPCRequest, IPCResponse
from services.registry_discovery_service import get_registry_discovery_service

logger = logging.getLogger(__name__)


async def get_registry_config(request: IPCRequest) -> IPCResponse:
    """获取注册表配置"""
    try:
        discovery_service = get_registry_discovery_service()
        core_config = get_core_config()
        registry_config = core_config.config.connector_registry
        status = discovery_service.get_discovery_status()
        registry_metadata, _ = await discovery_service.discover_registry()
        metadata = registry_metadata.get("metadata", {}) if registry_metadata else {}

        response_data = {
            "registry_url": registry_config.url,
            "cache_duration_hours": registry_config.cache_duration_hours,
            "auto_refresh": registry_config.auto_refresh,
            "current_source": status.get("last_successful_source", {}).get(
                "description"
            ),
            "last_updated": metadata.get("last_updated"),
            "total_connectors": metadata.get("total_count"),
            "status": "available" if registry_metadata else "unavailable",
        }
        return IPCResponse.success_response(data=response_data)

    except Exception as e:
        logger.error(f"获取注册表配置失败: {e}")
        from services.ipc_protocol import IPCErrorCode

        return IPCResponse.error_response(
            IPCErrorCode.INTERNAL_ERROR,
            f"获取注册表配置失败: {str(e)}",
            {"operation": "get_registry_config"},
        )


async def update_registry_config(request: IPCRequest) -> IPCResponse:
    """更新注册表配置"""
    try:
        body = await request.json()
        core_config = get_core_config()

        if "registry_url" in body:
            core_config.config.connector_registry.url = body["registry_url"]
        if "cache_duration_hours" in body:
            core_config.config.connector_registry.cache_duration_hours = body[
                "cache_duration_hours"
            ]
        if "auto_refresh" in body:
            core_config.config.connector_registry.auto_refresh = body["auto_refresh"]

        core_config.save_config()
        discovery_service = get_registry_discovery_service()
        discovery_service.__init__()  # Re-initialize

        await discovery_service.discover_registry(force_refresh=True)
        return await get_registry_config(request)  # Return updated config

    except Exception as e:
        logger.error(f"更新注册表配置失败: {e}")
        from services.ipc_protocol import IPCErrorCode

        return IPCResponse.error_response(
            IPCErrorCode.INTERNAL_ERROR,
            f"更新注册表配置失败: {str(e)}",
            {"operation": "update_registry_config"},
        )


async def test_registry_url(request: IPCRequest) -> IPCResponse:
    """测试注册表URL可用性"""
    try:
        body = await request.json()
        test_url = body.get("test_url")
        if not test_url:
            from services.ipc_protocol import IPCErrorCode

            return IPCResponse.error_response(
                IPCErrorCode.MISSING_PARAMETER,
                "Missing test_url parameter",
                {"required_parameter": "test_url"},
            )

        from services.registry_discovery_service import (RegistrySource,
                                                         RegistrySourceType)

        discovery_service = get_registry_discovery_service()
        test_source = RegistrySource(
            type=RegistrySourceType.USER_CONFIGURED,
            url=test_url,
            priority=1,
            timeout=30,
            description="测试URL",
        )
        registry_data = await discovery_service._fetch_from_source(test_source)

        if registry_data and discovery_service._validate_registry_data(registry_data):
            count = len(registry_data.get("connectors", {}))
            return IPCResponse.success_response(
                data={
                    "status": "success",
                    "message": f"URL可用，发现 {count} 个连接器",
                    "connector_count": count,
                    "last_updated": registry_data.get("last_updated"),
                }
            )
        else:
            return IPCResponse.success_response(
                data={"status": "error", "message": "URL不可用或数据格式错误"}
            )

    except Exception as e:
        logger.error(f"测试注册表URL失败: {e}")
        return IPCResponse.success_response(
            data={"status": "error", "message": f"测试失败: {str(e)}"}
        )


async def get_system_config(request: IPCRequest) -> IPCResponse:
    """获取系统配置概览"""
    try:
        core_config = get_core_config()
        discovery_service = get_registry_discovery_service()
        registry_config_resp = await get_registry_config(request)
        status = discovery_service.get_discovery_status()

        return IPCResponse.success_response(
            data={
                "registry": registry_config_resp.data,
                "app_data_dir": str(core_config.app_data_dir),
                "config_sources": status["sources"],
            }
        )

    except Exception as e:
        logger.error(f"获取系统配置失败: {e}")
        from services.ipc_protocol import IPCErrorCode

        return IPCResponse.error_response(
            IPCErrorCode.INTERNAL_ERROR,
            f"获取系统配置失败: {str(e)}",
            {"operation": "get_system_config"},
        )


async def refresh_registry(request: IPCRequest) -> IPCResponse:
    """手动刷新注册表缓存"""
    try:
        discovery_service = get_registry_discovery_service()
        registry_data, source = await discovery_service.discover_registry(
            force_refresh=True
        )

        if registry_data:
            count = len(registry_data.get("connectors", {}))
            return IPCResponse.success_response(
                data={
                    "status": "success",
                    "message": f"注册表已刷新，发现 {count} 个连接器",
                    "source": source.description if source else "unknown",
                    "connector_count": count,
                }
            )
        else:
            return IPCResponse.success_response(
                data={"status": "error", "message": "刷新注册表失败"}
            )

    except Exception as e:
        logger.error(f"刷新注册表失败: {e}")
        return IPCResponse.success_response(
            data={"status": "error", "message": f"刷新失败: {str(e)}"}
        )


async def get_registry_sources(request: IPCRequest) -> IPCResponse:
    """获取注册表源状态"""
    try:
        discovery_service = get_registry_discovery_service()
        status = discovery_service.get_discovery_status()
        return IPCResponse.success_response(
            data={
                "sources": status["sources"],
                "last_successful_source": status["last_successful_source"],
                "cache_info": status["cache_info"],
            }
        )
    except Exception as e:
        logger.error(f"获取注册表源状态失败: {e}")
        from services.ipc_protocol import IPCErrorCode

        return IPCResponse.error_response(
            IPCErrorCode.INTERNAL_ERROR,
            f"获取注册表源状态失败: {str(e)}",
            {"operation": "get_registry_sources"},
        )


async def get_registry_connectors(request: IPCRequest) -> IPCResponse:
    """获取注册表中的连接器列表"""
    try:
        from services.connector_registry_service import get_connector_registry_service

        registry_service = get_connector_registry_service()

        if not registry_service._cache:
            await registry_service.fetch_registry(force_refresh=True)

        query = request.query_params.get("query", "")
        category = request.query_params.get("category")
        connectors = await registry_service.search_connectors(
            query=query,
            category=category if category and category != "all" else None,
        )
        return IPCResponse.success_response(data=connectors)

    except Exception as e:
        logger.error(f"获取注册表连接器失败: {e}")
        from services.ipc_protocol import IPCErrorCode

        return IPCResponse.error_response(
            IPCErrorCode.INTERNAL_ERROR,
            f"获取注册表连接器失败: {str(e)}",
            {"operation": "get_registry_connectors"},
        )


async def get_connector_download_info(request: IPCRequest) -> IPCResponse:
    """获取连接器下载信息"""
    try:
        from services.connector_registry_service import get_connector_registry_service

        registry_service = get_connector_registry_service()
        connector_id = request.path_params.get("connector_id")
        platform = request.query_params.get("platform", "linux-x64")

        download_info = await registry_service.get_connector_download_info(
            connector_id, platform
        )

        if download_info:
            return IPCResponse.success_response(data=download_info)
        else:
            from services.ipc_protocol import IPCErrorCode

            return IPCResponse.error_response(
                IPCErrorCode.RESOURCE_NOT_FOUND,
                f"连接器 {connector_id} 不存在或不支持平台 {platform}",
                {"connector_id": connector_id, "platform": platform},
            )

    except Exception as e:
        logger.error(f"获取连接器下载信息失败: {e}")
        from services.ipc_protocol import IPCErrorCode

        return IPCResponse.error_response(
            IPCErrorCode.INTERNAL_ERROR,
            f"获取连接器下载信息失败: {str(e)}",
            {"operation": "get_connector_download_info"},
        )


# 注意：这个文件现在只包含处理函数。
# 路由注册已移至 services/ipc_routes.py
