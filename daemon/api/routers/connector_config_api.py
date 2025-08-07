"""
连接器配置管理API - 纯IPC实现
"""

import logging
from typing import Any, Dict

from services.connectors.connector_config_service import get_connector_config_service
from services.ipc_router import IPCRequest, IPCResponse

logger = logging.getLogger(__name__)

async def get_config_schema(request: IPCRequest) -> IPCResponse:
    """获取连接器配置schema"""
    connector_id = request.path_params.get("connector_id")
    if not connector_id:
        return IPCResponse(status_code=400, data={"error": "Missing connector_id"})
    
    try:
        logger.info(f"获取连接器 {connector_id} 的配置schema")
        service = get_connector_config_service()
        schema_data = await service.get_config_schema(connector_id)
        
        if not schema_data:
            return IPCResponse(
                status_code=404,
                data={"error": f"连接器 {connector_id} 的配置schema不存在"}
            )
        
        return IPCResponse(
            success=True,
            data=schema_data,
            message=f"成功获取 {connector_id} 的配置schema"
        )
        
    except Exception as e:
        logger.error(f"获取配置schema失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})

async def get_current_config(request: IPCRequest) -> IPCResponse:
    """获取连接器当前配置"""
    connector_id = request.path_params.get("connector_id")
    if not connector_id:
        return IPCResponse(status_code=400, data={"error": "Missing connector_id"})
        
    try:
        logger.info(f"获取连接器 {connector_id} 的当前配置")
        service = get_connector_config_service()
        config_data = await service.get_current_config(connector_id)
        
        return IPCResponse(
            success=True,
            data=config_data or {},
            message=f"成功获取 {connector_id} 的当前配置"
        )
        
    except Exception as e:
        logger.error(f"获取当前配置失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})

async def validate_config(request: IPCRequest) -> IPCResponse:
    """验证连接器配置"""
    body = await request.json()
    connector_id = body.get("connector_id")
    config = body.get("config")

    if not connector_id or config is None:
        return IPCResponse(status_code=400, data={"error": "Missing connector_id or config"})

    try:
        logger.info(f"验证连接器 {connector_id} 的配置")
        service = get_connector_config_service()
        validation_result = await service.validate_config(connector_id, config)
        
        return IPCResponse(
            success=validation_result["valid"],
            data=validation_result,
            message="配置验证完成" if validation_result["valid"] else "配置验证失败"
        )
        
    except Exception as e:
        logger.error(f"配置验证失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})

async def update_config(request: IPCRequest) -> IPCResponse:
    """更新连接器配置"""
    body = await request.json()
    connector_id = body.get("connector_id")
    config = body.get("config")
    change_reason = body.get("change_reason", "IPC API更新")

    if not connector_id or config is None:
        return IPCResponse(status_code=400, data={"error": "Missing connector_id or config"})

    try:
        logger.info(f"更新连接器 {connector_id} 的配置")
        service = get_connector_config_service()
        
        # 先验证配置
        validation_result = await service.validate_config(connector_id, config)
        
        if not validation_result["valid"]:
            return IPCResponse(
                success=False,
                data=validation_result,
                message="配置验证失败"
            )
        
        # 更新配置
        success = await service.update_config(
            connector_id,
            config,
            change_reason
        )
        
        if success:
            return IPCResponse(
                success=True,
                data={"config": config},
                message=f"成功更新 {connector_id} 的配置"
            )
        else:
            return IPCResponse(
                success=False,
                message=f"更新 {connector_id} 的配置失败"
            )
        
    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})

async def get_all_schemas(request: IPCRequest) -> IPCResponse:
    """获取所有连接器的配置schema"""
    try:
        logger.info("获取所有连接器的配置schema")
        service = get_connector_config_service()
        all_schemas = await service.get_all_schemas()
        
        return IPCResponse(
            success=True,
            data=all_schemas,
            message=f"成功获取 {len(all_schemas)} 个连接器的配置schema"
        )
        
    except Exception as e:
        logger.error(f"获取所有schema失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})

# 注意：这个文件现在只包含处理函数。
# 路由注册已移至 services/ipc_routes.py
