#!/usr/bin/env python3
"""
连接器生命周期管理API - 简化版
专注于核心连接器操作：发现、安装、启动、停止
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from models.api_models import ApiResponse
from pydantic import BaseModel
from services.connectors.connector_manager import get_connector_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/connector-lifecycle", tags=["connector-lifecycle"])


class ConnectorInstallRequest(BaseModel):
    connector_id: str
    source: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


@router.get("/discovery")
async def discover_connectors(
    manager=Depends(get_connector_manager),
) -> ApiResponse:
    """发现可用的连接器"""
    try:
        logger.info("发现本地连接器...")
        
        # 扫描本地连接器
        connectors = manager.discover_local_connectors()
        
        return ApiResponse(
            success=True,
            data={"connectors": connectors},
            message=f"发现 {len(connectors)} 个本地连接器"
        )
        
    except Exception as e:
        logger.error(f"连接器发现失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collectors")
async def list_collectors(
    manager=Depends(get_connector_manager),
) -> ApiResponse:
    """列出所有连接器实例"""
    try:
        logger.info("获取连接器列表...")
        
        connectors = manager.list_connectors()
        
        return ApiResponse(
            success=True,
            data={"collectors": connectors},
            message=f"找到 {len(connectors)} 个连接器实例"
        )
        
    except Exception as e:
        logger.error(f"获取连接器列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collectors/{collector_id}")
async def get_collector_status(
    collector_id: str,
    manager=Depends(get_connector_manager),
) -> ApiResponse:
    """获取连接器状态"""
    try:
        logger.info(f"获取连接器 {collector_id} 状态...")
        
        status = manager.get_connector_status(collector_id)
        if not status:
            raise HTTPException(
                status_code=404,
                detail=f"连接器 {collector_id} 不存在"
            )
        
        return ApiResponse(
            success=True,
            data={"collector": status},
            message=f"成功获取 {collector_id} 状态"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取连接器状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collectors/{collector_id}/start")
async def start_collector(
    collector_id: str,
    manager=Depends(get_connector_manager),
) -> ApiResponse:
    """启动连接器"""
    try:
        logger.info(f"启动连接器 {collector_id}...")
        
        success = await manager.start_connector(collector_id)
        
        if success:
            return ApiResponse(
                success=True,
                message=f"成功启动连接器 {collector_id}"
            )
        else:
            return ApiResponse(
                success=False,
                message=f"启动连接器 {collector_id} 失败"
            )
        
    except Exception as e:
        logger.error(f"启动连接器失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collectors/{collector_id}/stop")
async def stop_collector(
    collector_id: str,
    manager=Depends(get_connector_manager),
) -> ApiResponse:
    """停止连接器"""
    try:
        logger.info(f"停止连接器 {collector_id}...")
        
        success = await manager.stop_connector(collector_id)
        
        if success:
            return ApiResponse(
                success=True,
                message=f"成功停止连接器 {collector_id}"
            )
        else:
            return ApiResponse(
                success=False,
                message=f"停止连接器 {collector_id} 失败"
            )
        
    except Exception as e:
        logger.error(f"停止连接器失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collectors/{collector_id}/restart")
async def restart_collector(
    collector_id: str,
    manager=Depends(get_connector_manager),
) -> ApiResponse:
    """重启连接器"""
    try:
        logger.info(f"重启连接器 {collector_id}...")
        
        # 先停止后启动
        stop_success = await manager.stop_connector(collector_id)
        if not stop_success:
            return ApiResponse(
                success=False,
                message=f"停止连接器 {collector_id} 失败"
            )
        
        start_success = await manager.start_connector(collector_id)
        
        if start_success:
            return ApiResponse(
                success=True,
                message=f"成功重启连接器 {collector_id}"
            )
        else:
            return ApiResponse(
                success=False,
                message=f"重启连接器 {collector_id} 失败"
            )
        
    except Exception as e:
        logger.error(f"重启连接器失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/install")
async def install_connector(
    request: ConnectorInstallRequest,
    manager=Depends(get_connector_manager),
) -> ApiResponse:
    """安装连接器"""
    try:
        logger.info(f"安装连接器 {request.connector_id}...")
        
        success = await manager.install_connector(
            request.connector_id,
            request.source,
            request.config
        )
        
        if success:
            return ApiResponse(
                success=True,
                message=f"成功安装连接器 {request.connector_id}"
            )
        else:
            return ApiResponse(
                success=False,
                message=f"安装连接器 {request.connector_id} 失败"
            )
        
    except Exception as e:
        logger.error(f"安装连接器失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def system_health(
    manager=Depends(get_connector_manager),
) -> ApiResponse:
    """系统健康检查"""
    try:
        logger.info("执行系统健康检查...")
        
        connectors = manager.list_connectors()
        running_count = len([c for c in connectors if c.get("status") == "running"])
        total_count = len(connectors)
        
        health_data = {
            "total_connectors": total_count,
            "running_connectors": running_count,
            "healthy": running_count > 0,
            "timestamp": manager.get_current_timestamp()
        }
        
        return ApiResponse(
            success=True,
            data=health_data,
            message=f"系统健康，{running_count}/{total_count} 个连接器运行中"
        )
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))