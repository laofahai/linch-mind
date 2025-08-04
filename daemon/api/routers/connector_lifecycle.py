#!/usr/bin/env python3
"""
连接器安装器API路由
提供连接器的安装、卸载、更新功能
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
import logging

from services.connectors.connector_manager import get_connector_manager
from models.api_models import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/connectors", tags=["connector-management"])

# 简化的连接器管理API，专注于启动/停止/状态查询

@router.post("/start/{connector_id}")
async def start_connector(connector_id: str):
    """启动连接器"""
    try:
        manager = get_connector_manager()
        success = await manager.start_connector(connector_id)
        
        if not success:
            raise HTTPException(status_code=400, detail=f"Failed to start connector: {connector_id}")
        
        return ApiResponse(
            success=True,
            data={"connector_id": connector_id},
            message=f"Connector '{connector_id}' started successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start connector {connector_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop/{connector_id}")
async def stop_connector(connector_id: str):
    """停止连接器"""
    try:
        manager = get_connector_manager()
        success = await manager.stop_connector(connector_id)
        
        if not success:
            raise HTTPException(status_code=400, detail=f"Failed to stop connector: {connector_id}")
        
        return ApiResponse(
            success=True,
            data={"connector_id": connector_id},
            message=f"Connector '{connector_id}' stopped successfully"
        )
        
    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"Failed to stop connector {connector_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restart/{connector_id}")
async def restart_connector(connector_id: str):
    """重启连接器"""
    try:
        manager = get_connector_manager()
        success = await manager.restart_connector(connector_id)
        
        if not success:
            raise HTTPException(status_code=400, detail=f"Failed to restart connector: {connector_id}")
        
        return ApiResponse(
            success=True,
            data={"connector_id": connector_id},
            message=f"Connector '{connector_id}' restarted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to restart connector {connector_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_connectors():
    """列出所有已注册的连接器"""
    try:
        manager = get_connector_manager()
        connectors = manager.list_connectors()
        
        return ApiResponse(
            success=True,
            data={
                "connectors": connectors,
                "total": len(connectors)
            },
            message=f"Found {len(connectors)} registered connectors"
        )
        
    except Exception as e:
        logger.error(f"Failed to list connectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{connector_id}")
async def get_connector_status(connector_id: str):
    """获取连接器状态"""
    try:
        manager = get_connector_manager()
        status = manager.get_connector_status(connector_id)
        
        if not status:
            raise HTTPException(status_code=404, detail=f"Connector '{connector_id}' not found")
        
        return ApiResponse(
            success=True,
            data=status,
            message=f"Connector '{connector_id}' status retrieved"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get connector status for {connector_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 移除复杂的依赖验证功能