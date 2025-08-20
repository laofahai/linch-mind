#!/usr/bin/env python3
"""
核心依赖注入模块 - 纯IPC架构
从api/dependencies.py中提取，移除所有FastAPI依赖
"""

import logging
import sys

# 🔧 移除lru_cache - 使用DI容器替代
from pathlib import Path

# 使用标准Python包导入，无需动态路径添加

from config.config_manager import ConfigManager

logger = logging.getLogger(__name__)


# 🔧 移除@lru_cache装饰器 - 使用DI容器管理单例
def get_config_manager() -> ConfigManager:
    """获取配置管理器 - 现在通过DI容器管理"""
    from core.service_facade import get_service
    from config.config_manager import ConfigManager
    
    return get_service(ConfigManager)


# 🚨 架构修复：移除对services层的直接依赖
# 服务清理现在通过DI容器统一管理，不在config层处理
