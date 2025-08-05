#!/usr/bin/env python3
"""
连接器自定义UI API路由
支持连接器注册和提供自定义UI组件
"""

import logging
import mimetypes
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from models.api_models import ApiResponse
from services.connectors.connector_ui_service import ConnectorUIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/connector-ui", tags=["connector-ui"])


# 依赖注入
def get_ui_service():
    return ConnectorUIService()


@router.post("/register-custom-widget")
async def register_custom_widget(
    request: Dict[str, Any], ui_service: ConnectorUIService = None
):
    """注册连接器自定义UI组件"""
    if ui_service is None:
        ui_service = get_ui_service()

    try:
        connector_id = request.get("connector_id")
        widget_name = request.get("widget_name")
        widget_config = request.get("widget_config", {})

        if not connector_id or not widget_name:
            raise HTTPException(
                status_code=400, detail="connector_id and widget_name are required"
            )

        success = await ui_service.register_custom_widget(
            connector_id=connector_id,
            widget_name=widget_name,
            widget_config=widget_config,
        )

        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to register custom widget"
            )

        return ApiResponse(
            success=True,
            data={
                "connector_id": connector_id,
                "widget_name": widget_name,
                "registered": True,
            },
            message=f"自定义组件 {widget_name} 注册成功",
        )

    except Exception as e:
        logger.error(f"注册自定义组件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/custom-widget/{connector_id}/{widget_name}")
async def get_custom_widget_config(
    connector_id: str, widget_name: str, ui_service: ConnectorUIService = None
):
    """获取自定义组件配置"""
    if ui_service is None:
        ui_service = get_ui_service()

    try:
        widget_config = await ui_service.get_custom_widget_config(
            connector_id=connector_id, widget_name=widget_name
        )

        if not widget_config:
            raise HTTPException(
                status_code=404,
                detail=f"Custom widget {widget_name} not found for connector {connector_id}",
            )

        return ApiResponse(
            success=True,
            data={
                "connector_id": connector_id,
                "widget_name": widget_name,
                "widget_config": widget_config,
            },
            message="获取自定义组件配置成功",
        )

    except Exception as e:
        logger.error(f"获取自定义组件配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/iframe-content/{connector_id}/{component_name}")
async def serve_iframe_content(
    connector_id: str,
    component_name: str,
    request: Request,
    ui_service: ConnectorUIService = None,
):
    """为iframe组件提供HTML内容"""
    if ui_service is None:
        ui_service = get_ui_service()

    try:
        # 获取iframe内容
        content_info = await ui_service.get_iframe_content(
            connector_id=connector_id,
            component_name=component_name,
            request_params=dict(request.query_params),
        )

        if not content_info:
            raise HTTPException(
                status_code=404,
                detail=f"Iframe content not found for {connector_id}/{component_name}",
            )

        content_type = content_info.get("content_type", "text/html")
        content = content_info.get("content", "")

        return HTMLResponse(content=content, media_type=content_type)

    except Exception as e:
        logger.error(f"获取iframe内容失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/static/{connector_id}/{file_path:path}")
async def serve_static_file(
    connector_id: str, file_path: str, ui_service: ConnectorUIService = None
):
    """为连接器提供静态文件服务"""
    if ui_service is None:
        ui_service = get_ui_service()

    try:
        file_info = await ui_service.get_static_file(
            connector_id=connector_id, file_path=file_path
        )

        if not file_info or not file_info["exists"]:
            raise HTTPException(status_code=404, detail="File not found")

        file_full_path = Path(file_info["full_path"])
        content_type = (
            mimetypes.guess_type(str(file_full_path))[0] or "application/octet-stream"
        )

        return FileResponse(path=str(file_full_path), media_type=content_type)

    except Exception as e:
        logger.error(f"获取静态文件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate-custom-config")
async def validate_custom_config(
    request: Dict[str, Any], ui_service: ConnectorUIService = None
):
    """验证自定义组件配置"""
    if ui_service is None:
        ui_service = get_ui_service()

    try:
        connector_id = request.get("connector_id")
        widget_name = request.get("widget_name")
        config_data = request.get("config_data", {})

        if not connector_id or not widget_name:
            raise HTTPException(
                status_code=400, detail="connector_id and widget_name are required"
            )

        validation_result = await ui_service.validate_custom_config(
            connector_id=connector_id, widget_name=widget_name, config_data=config_data
        )

        return ApiResponse(
            success=validation_result["valid"],
            data={
                "connector_id": connector_id,
                "widget_name": widget_name,
                "valid": validation_result["valid"],
                "errors": validation_result.get("errors", []),
                "warnings": validation_result.get("warnings", []),
            },
            message="自定义配置验证完成",
        )

    except Exception as e:
        logger.error(f"验证自定义配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available-widgets/{connector_id}")
async def get_available_widgets(
    connector_id: str, ui_service: ConnectorUIService = None
):
    """获取连接器可用的自定义组件列表"""
    if ui_service is None:
        ui_service = get_ui_service()

    try:
        widgets = await ui_service.get_available_widgets(connector_id)

        return ApiResponse(
            success=True,
            data={
                "connector_id": connector_id,
                "widgets": widgets,
                "total_count": len(widgets),
            },
            message=f"获取连接器 {connector_id} 可用组件成功",
        )

    except Exception as e:
        logger.error(f"获取可用组件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute-widget-action")
async def execute_widget_action(
    request: Dict[str, Any], ui_service: ConnectorUIService = None
):
    """执行自定义组件动作"""
    if ui_service is None:
        ui_service = get_ui_service()

    try:
        connector_id = request.get("connector_id")
        widget_name = request.get("widget_name")
        action_name = request.get("action_name")
        action_params = request.get("action_params", {})

        if not all([connector_id, widget_name, action_name]):
            raise HTTPException(
                status_code=400,
                detail="connector_id, widget_name, and action_name are required",
            )

        result = await ui_service.execute_widget_action(
            connector_id=connector_id,
            widget_name=widget_name,
            action_name=action_name,
            action_params=action_params,
        )

        return ApiResponse(
            success=result.get("success", True),
            data=result.get("data", {}),
            message=result.get("message", "组件动作执行完成"),
        )

    except Exception as e:
        logger.error(f"执行组件动作失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
