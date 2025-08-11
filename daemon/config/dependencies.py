#!/usr/bin/env python3
"""
核心依赖注入模块 - 纯IPC架构
从api/dependencies.py中提取，移除所有FastAPI依赖
"""

import logging
import sys

# 🔧 移除lru_cache - 使用DI容器替代
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.core_config import CoreConfigManager, get_core_config

logger = logging.getLogger(__name__)


# 🔧 移除@lru_cache装饰器 - 使用DI容器管理单例
def get_config_manager() -> CoreConfigManager:
    """获取配置管理器 - 现在通过DI容器管理"""
    from core.service_facade import get_config_manager as get_manager_from_container

    return get_manager_from_container()


# 🚨 架构修复：移除对services层的直接依赖
# 服务清理现在通过DI容器统一管理，不在config层处理
