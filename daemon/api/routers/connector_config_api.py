#!/usr/bin/env python3
"""
连接器配置管理API路由 - 简化版
保留核心功能，移除复杂特性
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from models.api_models import ApiResponse
from pydantic import BaseModel
from services.connectors.connector_config_service import (ConnectorConfigService,
                                                          get_connector_config_service)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/connector-config", tags=["connector-config"])


class ConfigUpdateRequest(BaseModel):
    connector_id: str
    config: Dict[str, Any]
    change_reason: Optional[str] = "API更新"


class ConfigValidationRequest(BaseModel):
    connector_id: str
    config: Dict[str, Any]


@router.get("/schema/{connector_id}")
async def get_config_schema(
    connector_id: str,
    service: ConnectorConfigService = Depends(get_connector_config_service),
) -> ApiResponse:
    """获取连接器配置schema"""
    try:
        logger.info(f"获取连接器 {connector_id} 的配置schema")
        
        schema_data = await service.get_connector_config_schema(connector_id)
        if not schema_data:
            raise HTTPException(
                status_code=404,
                detail=f"连接器 {connector_id} 的配置schema不存在"
            )
        
        return ApiResponse(
            success=True,
            data=schema_data,
            message=f"成功获取 {connector_id} 的配置schema"
        )
        
    except Exception as e:
        logger.error(f"获取配置schema失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current/{connector_id}")
async def get_current_config(
    connector_id: str,
    service: ConnectorConfigService = Depends(get_connector_config_service),
) -> ApiResponse:
    """获取连接器当前配置"""
    try:
        logger.info(f"获取连接器 {connector_id} 的当前配置")
        
        config_data = await service.get_current_config(connector_id)
        
        return ApiResponse(
            success=True,
            data=config_data or {},
            message=f"成功获取 {connector_id} 的当前配置"
        )
        
    except Exception as e:
        logger.error(f"获取当前配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_config(
    request: ConfigValidationRequest,
    service: ConnectorConfigService = Depends(get_connector_config_service),
) -> ApiResponse:
    """验证连接器配置"""
    try:
        logger.info(f"验证连接器 {request.connector_id} 的配置")
        
        validation_result = await service.validate_config(
            request.connector_id,
            request.config
        )
        
        return ApiResponse(
            success=validation_result["valid"],
            data=validation_result,
            message="配置验证完成" if validation_result["valid"] else "配置验证失败"
        )
        
    except Exception as e:
        logger.error(f"配置验证失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update")
async def update_config(
    request: ConfigUpdateRequest,
    service: ConnectorConfigService = Depends(get_connector_config_service),
) -> ApiResponse:
    """更新连接器配置"""
    try:
        logger.info(f"更新连接器 {request.connector_id} 的配置")
        
        # 先验证配置
        validation_result = await service.validate_config(
            request.connector_id,
            request.config
        )
        
        if not validation_result["valid"]:
            return ApiResponse(
                success=False,
                data=validation_result,
                message="配置验证失败"
            )
        
        # 更新配置
        success = await service.update_connector_config(
            request.connector_id,
            request.config,
            request.change_reason
        )
        
        if success:
            return ApiResponse(
                success=True,
                data={"config": request.config},
                message=f"成功更新 {request.connector_id} 的配置"
            )
        else:
            return ApiResponse(
                success=False,
                message=f"更新 {request.connector_id} 的配置失败"
            )
        
    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all-schemas")
async def get_all_schemas(
    service: ConnectorConfigService = Depends(get_connector_config_service),
) -> ApiResponse:
    """获取所有连接器的配置schema"""
    try:
        logger.info("获取所有连接器的配置schema")
        
        all_schemas = await service.get_all_connector_schemas()
        
        return ApiResponse(
            success=True,
            data=all_schemas,
            message=f"成功获取 {len(all_schemas)} 个连接器的配置schema"
        )
        
    except Exception as e:
        logger.error(f"获取所有schema失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))