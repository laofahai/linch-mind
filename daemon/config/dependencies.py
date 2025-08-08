#!/usr/bin/env python3
"""
核心依赖注入模块 - 纯IPC架构
从api/dependencies.py中提取，移除所有FastAPI依赖
"""

import logging
import sys
from functools import lru_cache
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.core_config import CoreConfigManager, get_core_config
from services.connectors.connector_manager import (
    ConnectorManager,
    get_connector_manager,
)
from services.database_service import DatabaseService, get_database_service

logger = logging.getLogger(__name__)


@lru_cache()
def get_config_manager() -> CoreConfigManager:
    """获取配置管理器单例"""
    config_manager = get_core_config()
    logger.info("核心配置管理器初始化完成")
    return config_manager


def get_database() -> DatabaseService:
    """获取数据库服务单例"""
    return get_database_service()


def get_connector_service() -> ConnectorManager:
    """获取连接器管理器单例"""
    return get_connector_manager()


async def cleanup_services():
    """清理所有服务资源"""
    logger.info("开始清理服务资源...")

    # 清理连接器管理器
    try:
        connector_manager = get_connector_manager()
        await connector_manager.stop_all_connectors()
        logger.info("连接器管理器资源已清理")
    except Exception as e:
        logger.error(f"清理连接器管理器时出错: {e}")

    logger.info("所有服务资源清理完成")
