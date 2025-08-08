"""
连接器配置路由

处理连接器的配置管理，包括schema获取、配置更新等
"""

import logging

from core.service_facade import get_service
from services.connectors.connector_config_service import ConnectorConfigService
from ..ipc_protocol import (
    IPCRequest,
    IPCResponse,
    internal_error_response,
    invalid_request_response,
    resource_not_found_response,
)
from ..ipc_router import IPCRouter

logger = logging.getLogger(__name__)


def create_connector_config_router() -> IPCRouter:
    """创建连接器配置路由"""
    router = IPCRouter(prefix="/connector-config")

    @router.get("/schema/{connector_id}")
    async def get_config_schema(request: IPCRequest) -> IPCResponse:
        """获取连接器配置schema"""
        connector_id = request.path_params.get("connector_id")
        if not connector_id:
            return invalid_request_response(
                "Missing connector_id in path", {"required_param": "connector_id"}
            )

        try:
            # 使用现代化ServiceFacade模式获取配置服务
            config_service = get_service(ConnectorConfigService)
            schema_data = await config_service.get_config_schema(connector_id)

            if not schema_data:
                return resource_not_found_response(
                    f"配置schema不存在: {connector_id}", {"connector_id": connector_id}
                )

            return IPCResponse.success_response(
                data=schema_data, request_id=request.request_id
            )

        except Exception as e:
            logger.error(f"获取配置schema失败 {connector_id}: {e}")
            return internal_error_response(
                f"Failed to get config schema: {str(e)}",
                {"connector_id": connector_id, "operation": "get_config_schema"},
            )

    @router.get("/current/{connector_id}")
    async def get_current_config(request: IPCRequest) -> IPCResponse:
        """获取连接器当前配置"""
        connector_id = request.path_params.get("connector_id")
        if not connector_id:
            return invalid_request_response(
                "Missing connector_id in path", {"required_param": "connector_id"}
            )

        try:
            # 使用现代化ServiceFacade模式获取配置服务
            config_service = get_service(ConnectorConfigService)
            config_data = await config_service.get_current_config(connector_id)

            if config_data is None:
                # 返回空配置而不是错误
                config_data = {}

            return IPCResponse.success_response(
                data={"config": config_data}, request_id=request.request_id
            )

        except Exception as e:
            logger.error(f"获取当前配置失败 {connector_id}: {e}")
            return internal_error_response(
                f"Failed to get current config: {str(e)}",
                {"connector_id": connector_id, "operation": "get_current_config"},
            )

    @router.post("/validate")
    async def validate_config(request: IPCRequest) -> IPCResponse:
        """验证配置数据"""
        data = request.data
        if not data or "connector_id" not in data or "config" not in data:
            return invalid_request_response(
                "Missing connector_id or config in request data",
                {"required_fields": ["connector_id", "config"]},
            )

        connector_id = data["connector_id"]
        config = data["config"]

        try:
            # 使用现代化ServiceFacade模式获取配置服务
            config_service = get_service(ConnectorConfigService)
            validation_result = await config_service.validate_config(connector_id, config)

            return IPCResponse.success_response(
                data=validation_result, request_id=request.request_id
            )

        except Exception as e:
            logger.error(f"验证配置失败 {connector_id}: {e}")
            return internal_error_response(
                f"Failed to validate config: {str(e)}",
                {"connector_id": connector_id, "operation": "validate_config"},
            )

    @router.put("/update")
    async def update_config(request: IPCRequest) -> IPCResponse:
        """更新连接器配置"""
        data = request.data
        if not data or "connector_id" not in data or "config" not in data:
            return invalid_request_response(
                "Missing connector_id or config in request data",
                {"required_fields": ["connector_id", "config"]},
            )

        connector_id = data["connector_id"]
        config = data["config"]
        config_version = data.get("config_version", "1.0.0")
        change_reason = data.get("change_reason", "用户更新")

        try:
            # 使用现代化ServiceFacade模式获取配置服务
            config_service = get_service(ConnectorConfigService)
            result = await config_service.update_config(
                connector_id, config, config_version, change_reason
            )

            return IPCResponse.success_response(
                data=result, request_id=request.request_id
            )

        except Exception as e:
            logger.error(f"更新配置失败 {connector_id}: {e}")
            return internal_error_response(
                f"Failed to update config: {str(e)}",
                {"connector_id": connector_id, "operation": "update_config"},
            )

    @router.post("/reset")
    async def reset_config(request: IPCRequest) -> IPCResponse:
        """重置连接器配置"""
        data = request.data
        if not data or "connector_id" not in data:
            return invalid_request_response(
                "Missing connector_id in request data",
                {"required_field": "connector_id"},
            )

        connector_id = data["connector_id"]
        to_defaults = data.get("to_defaults", True)

        try:
            # 使用现代化ServiceFacade模式获取配置服务
            config_service = get_service(ConnectorConfigService)
            result = await config_service.reset_config(connector_id, to_defaults)

            return IPCResponse.success_response(
                data=result, request_id=request.request_id
            )

        except Exception as e:
            logger.error(f"重置配置失败 {connector_id}: {e}")
            return internal_error_response(
                f"Failed to reset config: {str(e)}",
                {"connector_id": connector_id, "operation": "reset_config"},
            )

    @router.get("/history/{connector_id}")
    async def get_config_history(request: IPCRequest) -> IPCResponse:
        """获取配置变更历史"""
        connector_id = request.path_params.get("connector_id")
        if not connector_id:
            return invalid_request_response(
                "Missing connector_id in path", {"required_param": "connector_id"}
            )

        limit = int(request.query_params.get("limit", 10))
        offset = int(request.query_params.get("offset", 0))

        try:
            # 使用现代化ServiceFacade模式获取配置服务
            config_service = get_service(ConnectorConfigService)
            history = await config_service.get_config_history(connector_id, limit, offset)

            return IPCResponse.success_response(
                data=history, request_id=request.request_id
            )

        except Exception as e:
            logger.error(f"获取配置历史失败 {connector_id}: {e}")
            return internal_error_response(
                f"Failed to get config history: {str(e)}",
                {"connector_id": connector_id, "operation": "get_config_history"},
            )

    @router.get("/all-schemas")
    async def get_all_schemas(request: IPCRequest) -> IPCResponse:
        """获取所有连接器的配置Schema概览"""
        try:
            # 使用现代化ServiceFacade模式获取配置服务
            config_service = get_service(ConnectorConfigService)
            schemas = await config_service.get_all_schemas()

            return IPCResponse.success_response(
                data=schemas, request_id=request.request_id
            )

        except Exception as e:
            logger.error(f"获取所有Schema失败: {e}")
            return internal_error_response(
                f"Failed to get all schemas: {str(e)}", {"operation": "get_all_schemas"}
            )

    return router
