"""
IPC路由兼容性层

该文件现在作为兼容性导入层，实际的路由实现已拆分到 ipc_routes 模块中。
重构完成，保持向后兼容性。

原始路由文件大小：887行
重构后模块化架构：
- health.py: 健康检查路由 (~70行)
- auth.py: 认证路由 (~65行)
- connector_lifecycle.py: 连接器生命周期路由 (~560行)
- connector_config.py: 连接器配置路由 (~120行)
- system_config.py: 系统配置路由 (~80行)
- __init__.py: 统一注册入口 (~50行)
"""

import logging
import warnings

logger = logging.getLogger(__name__)

# 向后兼容性导入
try:
    from .ipc_routes import (
        register_all_routes,
        create_auth_router,
        create_health_router,
        create_connector_lifecycle_router,
        create_connector_config_router,
        create_system_config_router
    )
except ImportError:
    # 如果新的模块化结构不可用，则退回到警告
    warnings.warn(
        "模块化路由结构不可用，请检查 ipc_routes 目录是否存在",
        UserWarning,
        stacklevel=2
    )
    
    def register_all_routes(app):
        """兼容性函数 - 无法加载模块化路由"""
        logger.error("无法加载模块化路由结构")
        raise ImportError("模块化IPC路由不可用")
    
    def create_auth_router():
        raise ImportError("模块化IPC路由不可用")
    
    def create_health_router():
        raise ImportError("模块化IPC路由不可用")
    
    def create_connector_lifecycle_router():
        raise ImportError("模块化IPC路由不可用")
    
    def create_connector_config_router():
        raise ImportError("模块化IPC路由不可用")
    
    def create_system_config_router():
        raise ImportError("模块化IPC路由不可用")


# 保持原有的导出接口
__all__ = [
    'register_all_routes',
    'create_auth_router',
    'create_health_router',
    'create_connector_lifecycle_router',
    'create_connector_config_router',
    'create_system_config_router'
]