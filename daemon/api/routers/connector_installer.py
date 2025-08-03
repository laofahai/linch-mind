#!/usr/bin/env python3
"""
连接器安装器API路由
提供连接器的安装、卸载、更新功能
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
import logging

from services.connectors.installer import ConnectorInstaller
from services.connectors.lifecycle_manager import get_lifecycle_manager
from models.api_models import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/connectors", tags=["connector-installer"])

# 全局安装器实例
_installer = None

def get_installer() -> ConnectorInstaller:
    """获取安装器实例"""
    global _installer
    if _installer is None:
        lifecycle_manager = get_lifecycle_manager()
        _installer = ConnectorInstaller(lifecycle_manager)
    return _installer

@router.get("/registry")
async def list_available_connectors():
    """列出注册表中可用的连接器"""
    try:
        installer = get_installer()
        result = await installer.list_available_connectors()
        
        if "error" in result:
            raise HTTPException(status_code=503, detail=f"Registry unavailable: {result['error']}")
        
        return ApiResponse(
            success=True,
            data=result,
            message=f"Found {result['total']} available connectors"
        )
        
    except Exception as e:
        logger.error(f"Failed to list available connectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/registry/{connector_id}")
async def get_connector_info(connector_id: str):
    """获取特定连接器的详细信息"""
    try:
        installer = get_installer()
        connector_info = await installer.get_connector_info(connector_id)
        
        if not connector_info:
            raise HTTPException(status_code=404, detail=f"Connector '{connector_id}' not found in registry")
        
        return ApiResponse(
            success=True,
            data=connector_info,
            message=f"Connector '{connector_id}' information retrieved"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get connector info for {connector_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/install/{connector_id}")
async def install_connector(
    connector_id: str, 
    version: Optional[str] = "latest",
    background_tasks: BackgroundTasks = None
):
    """安装连接器"""
    try:
        installer = get_installer()
        
        # 异步安装（可选择后台任务）
        result = await installer.install_connector(connector_id, version)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return ApiResponse(
            success=True,
            data={
                "connector_id": connector_id,
                "version": version,
                "install_dir": result.get("install_dir")
            },
            message=f"Connector '{connector_id}' v{version} installed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to install connector {connector_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/uninstall/{connector_id}")
async def uninstall_connector(connector_id: str, force: bool = False):
    """卸载连接器"""
    try:
        installer = get_installer()
        result = await installer.uninstall_connector(connector_id, force)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return ApiResponse(
            success=True,
            data={"connector_id": connector_id},
            message=result["message"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to uninstall connector {connector_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update/{connector_id}")
async def update_connector(connector_id: str, target_version: Optional[str] = "latest"):
    """更新连接器"""
    try:
        installer = get_installer()
        result = await installer.update_connector(connector_id, target_version)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return ApiResponse(
            success=True,
            data={
                "connector_id": connector_id,
                "target_version": target_version
            },
            message=result["message"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update connector {connector_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/installed")
async def list_installed_connectors():
    """列出已安装的连接器"""
    try:
        lifecycle_manager = get_lifecycle_manager()
        
        # 获取所有连接器类型（已安装的）
        discovered_connectors = await lifecycle_manager.discover_connectors()
        
        installed_connectors = []
        for connector in discovered_connectors:
            # 检查连接器运行状态
            is_running = await lifecycle_manager.is_connector_running(connector.id)
            
            connector_dict = {
                "id": connector.id,
                "name": connector.name,
                "description": connector.description,
                "version": connector.version,
                "author": connector.author,
                "status": "running" if is_running else "stopped",
                "is_enabled": True  # 已安装就是已启用
            }
            
            installed_connectors.append(connector_dict)
        
        return ApiResponse(
            success=True,
            data={
                "connectors": installed_connectors,
                "total": len(installed_connectors)
            },
            message=f"Found {len(installed_connectors)} installed connectors"
        )
        
    except Exception as e:
        logger.error(f"Failed to list installed connectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate-dependencies/{connector_id}")
async def validate_connector_dependencies(connector_id: str):
    """验证连接器依赖"""
    try:
        # 这个功能需要连接器类已经加载
        # 简化版：返回基本状态
        return ApiResponse(
            success=True,
            data={
                "connector_id": connector_id,
                "dependencies_status": "validation_not_implemented"
            },
            message="Dependency validation not yet implemented"
        )
        
    except Exception as e:
        logger.error(f"Failed to validate dependencies for {connector_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))