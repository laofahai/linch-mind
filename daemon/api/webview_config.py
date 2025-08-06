#!/usr/bin/env python3
"""
WebView配置API - 为连接器提供WebView配置界面
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from typing import Dict, Any, Optional

from services.webview_config_service import WebViewConfigService
from config.core_config import CoreConfigManager
from models.api_models import ApiResponse

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/webview-config", tags=["WebView Config"])


async def get_webview_config_service() -> WebViewConfigService:
    """获取WebView配置服务"""
    config_manager = CoreConfigManager()
    return WebViewConfigService(config_manager)


@router.get(
    "/html/{connector_id}",
    response_class=HTMLResponse,
    summary="获取连接器WebView配置HTML",
    description="为指定连接器生成WebView配置界面HTML内容",
)
async def get_connector_webview_html(
    connector_id: str,
    template_name: Optional[str] = None,
    webview_service: WebViewConfigService = Depends(get_webview_config_service),
) -> HTMLResponse:
    """获取连接器WebView配置HTML"""
    try:
        logger.info(f"生成连接器 {connector_id} 的WebView配置HTML")

        # 获取配置管理器

        # 获取连接器的配置schema
        schema_data = await webview_service.connector_config_service.get_config_schema(connector_id)
        if not schema_data:
            logger.error(f"未找到连接器 {connector_id} 的配置schema")
            raise HTTPException(
                status_code=404, 
                detail=f"连接器 {connector_id} 的配置schema不存在"
            )

        config_schema = schema_data.get("config_schema", {})
        ui_schema = schema_data.get("ui_schema", {})

        # 获取当前配置
        current_config = await webview_service.connector_config_service.get_current_config(connector_id)
        if current_config is None:
            current_config = {}

        # 生成HTML内容
        html_content = await webview_service.generate_webview_html(
            connector_id=connector_id,
            config_schema=config_schema,
            ui_schema=ui_schema,
            current_config=current_config,
            template_name=template_name,
        )

        return HTMLResponse(content=html_content)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成WebView配置HTML失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成配置界面失败: {str(e)}")


@router.get(
    "/check-support/{connector_id}",
    response_model=ApiResponse,
    summary="检查连接器是否支持WebView配置",
    description="检查指定连接器是否支持WebView配置界面",
)
async def check_webview_support(
    connector_id: str,
    webview_service: WebViewConfigService = Depends(get_webview_config_service),
) -> ApiResponse:
    """检查连接器WebView支持情况"""
    try:
        # 获取连接器的配置schema
        schema_data = await webview_service.connector_config_service.get_config_schema(connector_id)

        if not schema_data:
            return ApiResponse(
                success=False,
                message=f"连接器 {connector_id} 不存在",
            )

        # 检查是否支持WebView配置
        ui_schema = schema_data.get("ui_schema", {})
        webview_config = ui_schema.get("ui:webview", {})
        
        supports_webview = webview_config.get("enabled", False)
        template_name = webview_config.get("template")
        custom_html = webview_config.get("custom_html")

        return ApiResponse(
            success=True,
            data={
                "connector_id": connector_id,
                "supports_webview": supports_webview,
                "template_name": template_name,
                "has_custom_html": bool(custom_html),
                "webview_config": webview_config,
            },
            message="WebView支持检查完成",
        )

    except Exception as e:
        logger.error(f"检查WebView支持失败: {e}")
        return ApiResponse(
            success=False,
            message=f"检查失败: {str(e)}",
        )


@router.get(
    "/templates",
    response_model=ApiResponse,
    summary="获取可用模板列表",
    description="获取所有可用的WebView配置模板",
)
async def get_available_templates(
    webview_service: WebViewConfigService = Depends(get_webview_config_service),
) -> ApiResponse:
    """获取可用模板列表"""
    try:
        templates = await webview_service.get_available_templates()
        
        return ApiResponse(
            success=True,
            data=templates,
            message=f"找到 {len(templates)} 个可用模板",
        )

    except Exception as e:
        logger.error(f"获取模板列表失败: {e}")
        return ApiResponse(
            success=False,
            message=f"获取模板列表失败: {str(e)}",
        )


@router.post(
    "/templates/{template_name}",
    response_model=ApiResponse,
    summary="保存自定义模板",
    description="保存或更新自定义WebView配置模板",
)
async def save_custom_template(
    template_name: str,
    request_data: Dict[str, Any],
    webview_service: WebViewConfigService = Depends(get_webview_config_service),
) -> ApiResponse:
    """保存自定义模板"""
    try:
        template_content = request_data.get("content", "")
        connector_id = request_data.get("connector_id")

        if not template_content:
            raise HTTPException(status_code=400, detail="模板内容不能为空")

        # 验证模板
        validation_result = webview_service.validate_template(template_content)
        if not validation_result["valid"]:
            return ApiResponse(
                success=False,
                message=f"模板验证失败: {validation_result['message']}",
                data=validation_result,
            )

        # 保存模板
        success = await webview_service.save_custom_template(
            connector_id=connector_id or "custom",
            template_content=template_content,
            template_name=template_name,
        )

        if success:
            return ApiResponse(
                success=True,
                message=f"模板 {template_name} 保存成功",
            )
        else:
            return ApiResponse(
                success=False,
                message=f"模板 {template_name} 保存失败",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"保存模板失败: {e}")
        return ApiResponse(
            success=False,
            message=f"保存模板失败: {str(e)}",
        )


@router.post(
    "/validate-template",
    response_model=ApiResponse,
    summary="验证模板内容",
    description="验证WebView配置模板的语法和结构",
)
async def validate_template_content(
    request_data: Dict[str, Any],
    webview_service: WebViewConfigService = Depends(get_webview_config_service),
) -> ApiResponse:
    """验证模板内容"""
    try:
        template_content = request_data.get("content", "")

        if not template_content:
            return ApiResponse(
                success=False,
                message="模板内容不能为空",
            )

        # 验证模板
        validation_result = webview_service.validate_template(template_content)

        return ApiResponse(
            success=validation_result["valid"],
            data=validation_result,
            message=validation_result["message"],
        )

    except Exception as e:
        logger.error(f"验证模板失败: {e}")
        return ApiResponse(
            success=False,
            message=f"验证模板失败: {str(e)}",
        )


@router.get(
    "/preview/{connector_id}",
    response_class=HTMLResponse,
    summary="预览连接器WebView配置",
    description="预览指定连接器的WebView配置界面（带测试数据）",
)
async def preview_connector_webview(
    connector_id: str,
    template_name: Optional[str] = None,
    webview_service: WebViewConfigService = Depends(get_webview_config_service),
) -> HTMLResponse:
    """预览连接器WebView配置"""
    try:
        logger.info(f"预览连接器 {connector_id} 的WebView配置")

        # 获取配置管理器

        # 获取连接器的配置schema
        schema_data = await webview_service.connector_config_service.get_config_schema(connector_id)
        if not schema_data:
            # 生成示例schema用于预览
            config_schema = {
                "type": "object",
                "properties": {
                    "example_field": {
                        "type": "string",
                        "title": "示例字段",
                        "description": "这是一个示例配置字段",
                    }
                },
                "required": ["example_field"],
            }
            ui_schema = {
                "ui:title": f"{connector_id} 配置预览",
                "ui:description": "这是一个配置预览界面",
            }
        else:
            config_schema = schema_data.get("config_schema", {})
            ui_schema = schema_data.get("ui_schema", {})

        # 使用示例配置数据
        current_config = {}

        # 生成HTML内容
        html_content = await webview_service.generate_webview_html(
            connector_id=connector_id,
            config_schema=config_schema,
            ui_schema=ui_schema,
            current_config=current_config,
            template_name=template_name,
        )

        return HTMLResponse(content=html_content)

    except Exception as e:
        logger.error(f"预览WebView配置失败: {e}")
        error_html = f"""
<!DOCTYPE html>
<html>
<head><title>预览失败</title></head>
<body>
    <div style="text-align: center; padding: 40px; font-family: Arial, sans-serif;">
        <h1 style="color: #dc3545;">预览失败</h1>
        <p>{str(e)}</p>
    </div>
</body>
</html>
        """
        return HTMLResponse(content=error_html, status_code=500)