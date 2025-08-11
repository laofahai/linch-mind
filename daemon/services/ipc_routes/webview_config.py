"""
WebView配置路由

处理WebView配置界面的生成和管理
"""

import logging

from ..ipc_protocol import (
    IPCErrorCode,
    IPCRequest,
    IPCResponse,
    internal_error_response,
    invalid_request_response,
    resource_not_found_response,
)
from ..ipc_router import IPCRouter

logger = logging.getLogger(__name__)


def create_webview_config_router() -> IPCRouter:
    """创建WebView配置路由"""
    router = IPCRouter(prefix="/webview-config")

    @router.get("/check-support/{connector_id}")
    async def check_webview_support(request: IPCRequest) -> IPCResponse:
        """检查连接器是否支持WebView配置"""
        connector_id = request.path_params.get("connector_id")
        if not connector_id:
            return invalid_request_response(
                "Missing connector_id in path", {"required_param": "connector_id"}
            )

        try:
            from core.service_facade import get_connector_config_service

            service = get_connector_config_service()
            schema_data = await service.get_config_schema(connector_id)

            supports_webview = False
            if schema_data and schema_data.get("source", "").startswith(
                "static_manifest"
            ):
                # 检查连接器是否在manifest中声明了webview_config: true
                from core.service_facade import get_database_service
                from daemon.models.database_models import Connector

                db_service = get_database_service()
                with db_service.get_session() as session:
                    connector = (
                        session.query(Connector)
                        .filter_by(connector_id=connector_id)
                        .first()
                    )
                    if connector and connector.config_data:
                        capabilities = connector.config_data.get("capabilities", {})
                        supports_webview = capabilities.get("webview_config", False)

            return IPCResponse.success_response(
                data={"supports_webview": supports_webview},
                request_id=request.request_id,
            )

        except Exception as e:
            logger.error(f"检查WebView支持失败 {connector_id}: {e}")
            return internal_error_response(
                f"Failed to check webview support: {str(e)}",
                {"connector_id": connector_id, "operation": "check_webview_support"},
            )

    @router.get("/html/{connector_id}")
    async def get_webview_config_html(request: IPCRequest) -> IPCResponse:
        """获取连接器WebView配置HTML"""
        connector_id = request.path_params.get("connector_id")
        if not connector_id:
            return invalid_request_response(
                "Missing connector_id in path", {"required_param": "connector_id"}
            )

        template_name = request.query_params.get("template_name")

        try:
            from core.service_facade import (
                get_connector_config_service,
                get_webview_config_service,
            )
            from daemon.config.core_config import get_core_config_manager

            # 获取配置和schema数据
            config_service = get_connector_config_service()
            schema_data = await config_service.get_config_schema(connector_id)
            current_config_data = await config_service.get_current_config(connector_id)

            if not schema_data:
                return resource_not_found_response(
                    f"连接器配置schema不存在: {connector_id}",
                    {"connector_id": connector_id},
                )

            # 提取schema和ui_schema
            config_schema = schema_data.get("schema", {})
            ui_schema = schema_data.get("ui_schema", {})
            current_config = (
                current_config_data.get("current_config", {})
                if current_config_data
                else {}
            )

            # 创建WebView配置服务
            config_manager = get_core_config_manager()
            webview_service = get_webview_config_service()

            # 生成HTML内容
            html_content = await webview_service.generate_webview_html(
                connector_id=connector_id,
                config_schema=config_schema,
                ui_schema=ui_schema,
                current_config=current_config,
                template_name=template_name,
            )

            return IPCResponse.success_response(
                data={"html": html_content}, request_id=request.request_id
            )

        except Exception as e:
            logger.error(f"生成WebView配置HTML失败 {connector_id}: {e}")
            return internal_error_response(
                f"Failed to generate webview html: {str(e)}",
                {"connector_id": connector_id, "operation": "get_webview_html"},
            )

    @router.get("/preview/{connector_id}")
    async def get_preview_html(request: IPCRequest) -> IPCResponse:
        """获取预览HTML内容"""
        connector_id = request.path_params.get("connector_id")
        if not connector_id:
            return invalid_request_response(
                "Missing connector_id in path", {"required_param": "connector_id"}
            )

        template_name = request.query_params.get("template_name")

        try:
            # 使用相同的逻辑生成预览HTML，但可能使用测试数据
            from core.service_facade import (
                get_connector_config_service,
                get_webview_config_service,
            )
            from daemon.config.core_config import get_core_config_manager

            config_service = get_connector_config_service()
            schema_data = await config_service.get_config_schema(connector_id)

            if not schema_data:
                return resource_not_found_response(
                    f"连接器配置schema不存在: {connector_id}",
                    {"connector_id": connector_id},
                )

            config_schema = schema_data.get("schema", {})
            ui_schema = schema_data.get("ui_schema", {})
            # 预览使用默认值作为当前配置
            current_config = schema_data.get("default_values", {})

            config_manager = get_core_config_manager()
            webview_service = get_webview_config_service()

            html_content = await webview_service.generate_webview_html(
                connector_id=connector_id,
                config_schema=config_schema,
                ui_schema=ui_schema,
                current_config=current_config,
                template_name=template_name,
            )

            return IPCResponse.success_response(
                data={"html": html_content}, request_id=request.request_id
            )

        except Exception as e:
            logger.error(f"生成预览HTML失败 {connector_id}: {e}")
            return internal_error_response(
                f"Failed to generate preview html: {str(e)}",
                {"connector_id": connector_id, "operation": "get_preview_html"},
            )

    @router.get("/templates")
    async def get_available_templates(request: IPCRequest) -> IPCResponse:
        """获取可用模板列表"""
        try:
            from core.service_facade import get_webview_config_service
            from daemon.config.core_config import get_core_config_manager

            config_manager = get_core_config_manager()
            webview_service = get_webview_config_service()

            templates = await webview_service.get_available_templates()

            return IPCResponse.success_response(
                data=templates, request_id=request.request_id
            )

        except Exception as e:
            logger.error(f"获取模板列表失败: {e}")
            return internal_error_response(
                f"Failed to get templates: {str(e)}",
                {"operation": "get_available_templates"},
            )

    @router.post("/templates/{template_name}")
    async def save_custom_template(request: IPCRequest) -> IPCResponse:
        """保存自定义模板"""
        template_name = request.path_params.get("template_name")
        if not template_name:
            return invalid_request_response(
                "Missing template_name in path", {"required_param": "template_name"}
            )

        data = request.data
        if not data or "content" not in data:
            return invalid_request_response(
                "Missing template content", {"required_field": "content"}
            )

        template_content = data["content"]
        connector_id = data.get("connector_id")

        try:
            from core.service_facade import get_webview_config_service
            from daemon.config.core_config import get_core_config_manager

            config_manager = get_core_config_manager()
            webview_service = get_webview_config_service()

            # 验证模板
            validation_result = webview_service.validate_template(template_content)
            if not validation_result["valid"]:
                return IPCResponse.error_response(
                    IPCErrorCode.VALIDATION_ERROR,
                    f"模板验证失败: {validation_result['message']}",
                    validation_result,
                    request_id=request.request_id,
                )

            # 保存模板
            success = await webview_service.save_custom_template(
                connector_id or template_name, template_content, template_name
            )

            if success:
                return IPCResponse.success_response(
                    data={
                        "template_name": template_name,
                        "saved": True,
                        "message": "模板保存成功",
                    },
                    request_id=request.request_id,
                )
            else:
                return IPCResponse.error_response(
                    IPCErrorCode.INTERNAL_ERROR,
                    "模板保存失败",
                    {"template_name": template_name},
                    request_id=request.request_id,
                )

        except Exception as e:
            logger.error(f"保存自定义模板失败 {template_name}: {e}")
            return internal_error_response(
                f"Failed to save template: {str(e)}",
                {"template_name": template_name, "operation": "save_custom_template"},
            )

    @router.post("/validate-template")
    async def validate_template(request: IPCRequest) -> IPCResponse:
        """验证模板内容"""
        data = request.data
        if not data or "content" not in data:
            return invalid_request_response(
                "Missing template content", {"required_field": "content"}
            )

        template_content = data["content"]

        try:
            from core.service_facade import get_webview_config_service
            from daemon.config.core_config import get_core_config_manager

            config_manager = get_core_config_manager()
            webview_service = get_webview_config_service()

            validation_result = webview_service.validate_template(template_content)

            return IPCResponse.success_response(
                data=validation_result, request_id=request.request_id
            )

        except Exception as e:
            logger.error(f"验证模板失败: {e}")
            return internal_error_response(
                f"Failed to validate template: {str(e)}",
                {"operation": "validate_template"},
            )

    return router
