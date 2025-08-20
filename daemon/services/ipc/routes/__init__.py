"""
IPC路由模块

提供模块化的IPC路由管理，将原来的大文件拆分为独立的功能模块：
- health: 健康检查和系统信息
- auth: 认证和授权管理
- connector_lifecycle: 连接器生命周期管理（CRUD、启动/停止、状态管理）
- connector_config: 连接器配置管理
- webview_config: WebView配置界面管理
- system_config: 系统配置和注册表管理
"""

import logging

logger = logging.getLogger(__name__)


def register_all_routes(app):
    """
    注册所有IPC路由到应用程序

    按照以下顺序注册：
    1. 认证路由 - 必须首先注册，提供身份验证
    2. 健康检查路由 - 基础服务状态检查
    3. 环境管理路由 - 环境切换和管理功能 (🆕 V62环境隔离)
    4. 连接器生命周期路由 - 核心连接器管理功能
    5. 连接器配置路由 - 连接器配置管理
    6. WebView配置路由 - WebView配置界面管理
    7. 系统配置路由 - 系统级配置和注册表
    """
    from .auth import create_auth_router
    # from .connector_config import create_connector_config_router  # 暂时注释
    # from .connector_lifecycle import create_connector_lifecycle_router  # 暂时注释
    # from .connector_status import create_connector_status_router  # 暂时注释
    from .data_insights import create_data_insights_router  # 🆕 数据洞察路由
    from .environment import create_environment_router  # 🆕 环境管理路由
    from .ai_correlation import create_ai_correlation_router  # 🆕 AI关联路由
    from .events import create_events_router
    from .health import create_health_router
    from .starry_universe_data import create_starry_universe_data_router  # 🆕 星空宇宙数据路由
    from .system_config import create_system_config_router
    from .universal_search import create_universal_search_router  # 🆕 通用搜索路由
    from .webview_config import create_webview_config_router

    # 按优先级顺序注册路由
    app.include_router(create_auth_router())  # 认证路由必须首先注册
    app.include_router(create_health_router())
    app.include_router(create_environment_router())  # 🆕 环境管理路由
    app.include_router(create_data_insights_router())  # 🆕 数据洞察路由
    app.include_router(create_events_router())  # 事件处理路由
    app.include_router(create_ai_correlation_router())  # 🆕 AI关联路由
    app.include_router(create_universal_search_router())  # 🆕 通用搜索路由
    app.include_router(create_starry_universe_data_router())  # 🆕 星空宇宙数据路由
    # app.include_router(create_connector_lifecycle_router())  # 暂时注释
    # app.include_router(create_connector_config_router())  # 暂时注释
    # app.include_router(create_connector_status_router())  # 暂时注释
    app.include_router(create_webview_config_router())
    app.include_router(create_system_config_router())

    logger.info("所有IPC V2路由已注册完成（模块化架构 + 环境管理）")


# 为了兼容性，导出主要的路由创建函数
from .auth import create_auth_router
# from .connector_config import create_connector_config_router  # 暂时注释掉有问题的导入
# from .connector_lifecycle import create_connector_lifecycle_router  # 暂时注释
# from .connector_status import create_connector_status_router  # 暂时注释
from .data_insights import create_data_insights_router  # 🆕 数据洞察路由
from .environment import create_environment_router  # 🆕 环境管理路由
from .ai_correlation import create_ai_correlation_router  # 🆕 AI关联路由
from .events import create_events_router
from .health import create_health_router
from .starry_universe_data import create_starry_universe_data_router  # 🆕 星空宇宙数据路由
from .system_config import create_system_config_router
from .universal_search import create_universal_search_router  # 🆕 通用搜索路由
from .webview_config import create_webview_config_router

__all__ = [
    "register_all_routes",
    "create_auth_router",
    "create_health_router",
    "create_environment_router",  # 🆕 环境管理路由
    "create_data_insights_router",  # 🆕 数据洞察路由
    "create_events_router",
    "create_ai_correlation_router",  # 🆕 AI关联路由
    "create_universal_search_router",  # 🆕 通用搜索路由
    "create_starry_universe_data_router",  # 🆕 星空宇宙数据路由
    # "create_connector_lifecycle_router",  # 暂时注释
    # "create_connector_config_router",  # 暂时注释
    # "create_connector_status_router",  # 暂时注释
    "create_webview_config_router",
    "create_system_config_router",
]
