#!/usr/bin/env python3
"""
连接器配置管理API路由
Schema驱动的配置系统实现
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from services.connectors.connector_config_service import get_connector_config_service, ConnectorConfigService
from models.api_models import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/connector-config", tags=["connector-config"])

# 请求模型定义
class GetConfigSchemaRequest(BaseModel):
    connector_id: str

class UpdateConfigRequest(BaseModel):
    connector_id: str
    config: Dict[str, Any]
    config_version: Optional[str] = "1.0.0"
    change_reason: Optional[str] = "用户更新"

class ValidateConfigRequest(BaseModel):
    connector_id: str
    config: Dict[str, Any]

class ResetConfigRequest(BaseModel):
    connector_id: str
    to_defaults: bool = True

class RegisterSchemaRequest(BaseModel):
    connector_id: str
    config_schema: Dict[str, Any]
    ui_schema: Optional[Dict[str, Any]] = {}
    connector_name: Optional[str] = ""
    connector_description: Optional[str] = ""
    schema_source: Optional[str] = "runtime"

# 依赖注入
def get_config_service():
    return get_connector_config_service()

@router.get("/schema/{connector_id}")
async def get_connector_config_schema(
    connector_id: str,
    config_service: ConnectorConfigService = Depends(get_config_service)
):
    """获取连接器配置schema"""
    try:
        schema = await config_service.get_config_schema(connector_id)
        if not schema:
            raise HTTPException(status_code=404, detail=f"连接器 {connector_id} 不存在或无配置schema")
        
        return ApiResponse(
            success=True,
            data={
                "connector_id": connector_id,
                "schema": schema["schema"],
                "ui_schema": schema.get("ui_schema", {}),
                "default_values": schema.get("default_values", {}),
                "schema_version": schema.get("version", "1.0.0")
            },
            message=f"获取连接器 {connector_id} 配置schema成功"
        )
    except Exception as e:
        logger.error(f"获取配置schema失败 {connector_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/current/{connector_id}")
async def get_current_config(
    connector_id: str,
    config_service: ConnectorConfigService = Depends(get_config_service)
):
    """获取连接器当前配置"""
    try:
        config = await config_service.get_current_config(connector_id)
        if config is None:
            raise HTTPException(status_code=404, detail=f"连接器 {connector_id} 不存在")
        
        return ApiResponse(
            success=True,
            data={
                "connector_id": connector_id,
                "config": config["current_config"],
                "config_schema": config["config_schema"],
                "config_version": config["config_version"],
                "config_valid": config["config_valid"],
                "validation_errors": config["validation_errors"],
                "last_updated": config["updated_at"]
            },
            message=f"获取连接器 {connector_id} 当前配置成功"
        )
    except Exception as e:
        logger.error(f"获取当前配置失败 {connector_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_config(
    request: ValidateConfigRequest,
    config_service: ConnectorConfigService = Depends(get_config_service)
):
    """验证配置数据"""
    try:
        validation_result = await config_service.validate_config(
            request.connector_id, 
            request.config
        )
        
        return ApiResponse(
            success=validation_result["valid"],
            data={
                "connector_id": request.connector_id,
                "valid": validation_result["valid"],
                "errors": validation_result.get("errors", []),
                "warnings": validation_result.get("warnings", []),
                "normalized_config": validation_result.get("normalized_config", request.config)
            },
            message="配置验证完成" if validation_result["valid"] else "配置验证失败"
        )
    except Exception as e:
        logger.error(f"配置验证失败 {request.connector_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update")
async def update_config(
    request: UpdateConfigRequest,
    config_service: ConnectorConfigService = Depends(get_config_service)
):
    """更新连接器配置"""
    try:
        # 先验证配置
        validation = await config_service.validate_config(request.connector_id, request.config)
        if not validation["valid"]:
            return ApiResponse(
                success=False,
                data={"errors": validation["errors"]},
                message="配置验证失败，无法更新"
            )
        
        # 更新配置
        result = await config_service.update_config(
            connector_id=request.connector_id,
            new_config=validation["normalized_config"],
            config_version=request.config_version,
            change_reason=request.change_reason
        )
        
        return ApiResponse(
            success=True,
            data={
                "connector_id": request.connector_id,
                "config_version": result["config_version"],
                "hot_reload_applied": result["hot_reload_applied"],
                "requires_restart": result["requires_restart"],
                "updated_at": result["updated_at"]
            },
            message=f"连接器 {request.connector_id} 配置更新成功"
        )
    except Exception as e:
        logger.error(f"更新配置失败 {request.connector_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
async def reset_config(
    request: ResetConfigRequest,
    config_service: ConnectorConfigService = Depends(get_config_service)
):
    """重置连接器配置"""
    try:
        result = await config_service.reset_config(
            connector_id=request.connector_id,
            to_defaults=request.to_defaults
        )
        
        return ApiResponse(
            success=True,
            data={
                "connector_id": request.connector_id,
                "reset_to": "defaults" if request.to_defaults else "empty",
                "config": result["config"],
                "requires_restart": result["requires_restart"]
            },
            message=f"连接器 {request.connector_id} 配置重置成功"
        )
    except Exception as e:
        logger.error(f"重置配置失败 {request.connector_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{connector_id}")
async def get_config_history(
    connector_id: str,
    limit: int = 10,
    offset: int = 0,
    config_service: ConnectorConfigService = Depends(get_config_service)
):
    """获取配置变更历史"""
    try:
        history = await config_service.get_config_history(
            connector_id=connector_id,
            limit=limit,
            offset=offset
        )
        
        return ApiResponse(
            success=True,
            data={
                "connector_id": connector_id,
                "history": history["records"],
                "total_count": history["total"],
                "has_more": history["has_more"]
            },
            message=f"获取连接器 {connector_id} 配置历史成功"
        )
    except Exception as e:
        logger.error(f"获取配置历史失败 {connector_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all-schemas")
async def get_all_connector_schemas(
    config_service: ConnectorConfigService = Depends(get_config_service)
):
    """获取所有连接器的配置schema概览"""
    try:
        schemas = await config_service.get_all_schemas()
        
        return ApiResponse(
            success=True,
            data={
                "schemas": schemas,
                "total_count": len(schemas)
            },
            message=f"获取所有连接器配置schema成功，共 {len(schemas)} 个"
        )
    except Exception as e:
        logger.error(f"获取所有配置schema失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register-schema/{connector_id}")
async def register_connector_schema(
    connector_id: str,
    request: RegisterSchemaRequest,
    config_service = Depends(get_config_service)
):
    """注册连接器配置schema（由连接器运行时调用）"""
    try:
        # 准备schema数据
        schema_data = {
            "config_schema": request.config_schema,
            "ui_schema": request.ui_schema,
            "default_config": {},  # 从schema中提取默认值
            "connector_name": request.connector_name,
            "connector_description": request.connector_description,
            "schema_source": request.schema_source
        }
        
        # 注册运行时schema
        success = await config_service.register_runtime_schema(connector_id, schema_data)
        
        if success:
            return ApiResponse(
                success=True,
                data={
                    "connector_id": connector_id,
                    "schema_registered": True,
                    "schema_source": request.schema_source
                },
                message=f"连接器 {connector_id} 配置schema注册成功"
            )
        else:
            raise HTTPException(status_code=500, detail="Schema注册失败")
            
    except Exception as e:
        logger.error(f"注册配置schema失败 {connector_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))