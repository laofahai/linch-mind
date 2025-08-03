#!/usr/bin/env python3
"""
依赖注入模块 - 管理所有服务实例
Session 5 架构重构 - 职责分离和依赖管理
"""

import sys
from pathlib import Path
from functools import lru_cache
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.database_service import DatabaseService
from services.connectors.lifecycle_manager import ConnectorLifecycleManager, get_lifecycle_manager
from services.storage_strategy import SmartContentProcessor
from config.core_config import CoreConfigManager, get_core_config

logger = logging.getLogger(__name__)

# 全局服务实例
_db_service = None
_content_processor = None


@lru_cache()
def get_config_manager() -> CoreConfigManager:
    """获取配置管理器单例 (Session V61: 使用核心配置)"""
    config_manager = get_core_config()
    logger.info("核心配置管理器初始化完成")
    return config_manager


def get_database_service() -> DatabaseService:
    """获取数据库服务单例"""
    global _db_service
    if _db_service is None:
        config = get_config_manager()
        _db_service = DatabaseService(config.get_paths()["database"])
        logger.info("数据库服务初始化完成")
    return _db_service


def get_connector_manager():
    """已弃用：使用 get_lifecycle_manager() 替代"""
    logger.warning("get_connector_manager() 已弃用，请使用 get_lifecycle_manager()")
    return get_lifecycle_manager()


def get_content_processor() -> SmartContentProcessor:
    """获取智能内容处理器单例"""
    global _content_processor
    if _content_processor is None:
        _content_processor = SmartContentProcessor()
        logger.info("智能内容处理器初始化完成")
    return _content_processor


async def cleanup_services():
    """清理所有服务资源"""
    logger.info("开始清理服务资源...")
    
    # 清理连接器生命周期管理器
    try:
        lifecycle_manager = get_lifecycle_manager()
        await lifecycle_manager.shutdown_all()
        logger.info("连接器生命周期管理器资源已清理")
    except Exception as e:
        logger.error(f"清理生命周期管理器时出错: {e}")
    
    logger.info("所有服务资源清理完成")


# FastAPI依赖函数
async def get_db():
    """FastAPI依赖: 获取数据库会话"""
    db_service = get_database_service()
    db = db_service.SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_db_service() -> DatabaseService:
    """FastAPI依赖: 获取数据库服务（高级功能）"""
    return get_database_service()


async def get_connectors():
    """FastAPI依赖: 获取连接器管理器（已弃用，使用 get_lifecycle）"""
    logger.warning("get_connectors() 依赖已弃用，请使用 get_lifecycle()")
    return get_lifecycle_manager()


async def get_processor() -> SmartContentProcessor:
    """FastAPI依赖: 获取内容处理器"""
    return get_content_processor()


async def get_lifecycle() -> ConnectorLifecycleManager:
    """FastAPI依赖: 获取连接器生命周期管理器"""
    return get_lifecycle_manager()