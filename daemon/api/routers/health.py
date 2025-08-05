#!/usr/bin/env python3
"""
健康检查路由 - 系统状态和服务信息
Session 5 架构重构 - 模块化路由
"""

from datetime import datetime

from api.dependencies import get_config_manager
from config.core_config import CoreConfigManager
from fastapi import APIRouter, Depends
from models.api_models import ServerInfo

router = APIRouter(prefix="", tags=["health"])


@router.get("/")
async def root(config: CoreConfigManager = Depends(get_config_manager)):
    """根路径 - 基本服务信息"""
    server_info = config.get_server_info()
    return {
        "message": "Linch Mind API is running!",
        "version": server_info["version"],
        "port": server_info["port"],
        "started_at": server_info["started_at"],
    }


@router.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "linch-mind-daemon",
    }


@router.get("/server/info", response_model=ServerInfo)
async def get_server_info(config: CoreConfigManager = Depends(get_config_manager)):
    """获取详细服务器信息"""
    info = config.get_server_info()
    return ServerInfo(
        version=info["version"],
        port=info["port"],
        started_at=(
            datetime.fromisoformat(info["started_at"])
            if info["started_at"]
            else datetime.now()
        ),
    )
