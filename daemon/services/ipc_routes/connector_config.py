"""
连接器配置路由

处理连接器的配置管理，包括schema获取、配置更新等
"""

import logging

from core.error_handling import (
    ErrorCategory,
    ErrorContext,
    ErrorSeverity,
    get_enhanced_error_handler,
)
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
            # 使用增强错误处理器
            enhanced_handler = get_enhanced_error_handler()
            context = ErrorContext(
                function_name="get_config_schema",
                module_name=__name__,
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.CONNECTOR_MANAGEMENT,
                user_message="获取连接器配置模板失败",
                recovery_suggestions="检查连接器是否正确安装",
                technical_details=f"connector_id: {connector_id}",
            )

            processed_error = enhanced_handler.process_error(
                e, context, request.request_id
            )
            return IPCResponse.from_processed_error(processed_error, request.request_id)

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
            validation_result = await config_service.validate_config(
                connector_id, config
            )

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
            history = await config_service.get_config_history(
                connector_id, limit, offset
            )

            return IPCResponse.success_response(
                data=history, request_id=request.request_id
            )

        except Exception as e:
            logger.error(f"获取配置历史失败 {connector_id}: {e}")
            return internal_error_response(
                f"Failed to get config history: {str(e)}",
                {"connector_id": connector_id, "operation": "get_config_history"},
            )

    @router.get("/defaults/{connector_id}")
    async def get_default_config(request: IPCRequest) -> IPCResponse:
        """获取连接器的默认配置"""
        connector_id = request.path_params.get("connector_id")
        if not connector_id:
            return invalid_request_response(
                "Missing connector_id in path", {"required_param": "connector_id"}
            )

        try:
            # 使用现代化ServiceFacade模式获取配置服务
            config_service = get_service(ConnectorConfigService)
            result = await config_service.get_default_config(connector_id)

            return IPCResponse.success_response(
                data=result, request_id=request.request_id
            )

        except Exception as e:
            logger.error(f"获取默认配置失败 {connector_id}: {e}")
            return internal_error_response(
                f"Failed to get default config: {str(e)}",
                {"connector_id": connector_id, "operation": "get_default_config"},
            )

    @router.post("/apply-defaults")
    async def apply_defaults_to_config(request: IPCRequest) -> IPCResponse:
        """将默认值应用到现有配置中"""
        data = request.data
        if not data or "connector_id" not in data:
            return invalid_request_response(
                "Missing connector_id in request data",
                {"required_field": "connector_id"},
            )

        connector_id = data["connector_id"]
        current_config = data.get("current_config")  # 可选，如果未提供则从数据库获取

        try:
            # 使用现代化ServiceFacade模式获取配置服务
            config_service = get_service(ConnectorConfigService)
            result = await config_service.apply_defaults_to_config(
                connector_id, current_config
            )

            return IPCResponse.success_response(
                data=result, request_id=request.request_id
            )

        except Exception as e:
            logger.error(f"应用默认配置失败 {connector_id}: {e}")
            return internal_error_response(
                f"Failed to apply defaults: {str(e)}",
                {"connector_id": connector_id, "operation": "apply_defaults_to_config"},
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
