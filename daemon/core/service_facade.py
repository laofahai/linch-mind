#!/usr/bin/env python3
"""
统一服务获取Facade - 消除代码重复的核心解决方案
替代所有重复的get_*_service()全局函数调用
提供标准化服务获取和错误处理模式
"""

import logging
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any, Dict, Optional, Type, TypeVar

from .container import ServiceNotRegisteredError, get_container

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ServiceErrorType(Enum):
    """服务错误类型"""

    NOT_REGISTERED = "not_registered"
    INITIALIZATION_FAILED = "initialization_failed"
    SERVICE_UNAVAILABLE = "service_unavailable"
    DEPENDENCY_ERROR = "dependency_error"


@dataclass
class ServiceResult:
    """服务获取结果封装"""

    success: bool
    service: Optional[Any] = None
    error_type: Optional[ServiceErrorType] = None
    error_message: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.success

    def unwrap(self):
        """解包服务实例，失败时抛异常"""
        if not self.success:
            raise ServiceError(self.error_type, self.error_message)
        return self.service


class ServiceError(Exception):
    """统一服务异常"""

    def __init__(self, error_type: ServiceErrorType, message: str):
        self.error_type = error_type
        super().__init__(message)


class ServiceFacade:
    """统一服务获取Facade

    核心功能:
    - 消除重复的get_*_service()调用
    - 提供标准化错误处理
    - 统一服务获取接口
    - 支持服务状态监控
    """

    def __init__(self):
        self._container = None  # 延迟获取容器
        self._access_stats: Dict[str, int] = {}

    @property
    def container(self):
        """延迟获取容器实例，确保在服务注册完成后获取"""
        if self._container is None:
            self._container = get_container()
            logger.debug(
                f"ServiceFacade获取到容器，已注册服务数: {len(self._container.get_all_services())}"
            )
        return self._container

    def reset_container(self):
        """重置容器实例，用于服务注册完成后刷新"""
        self._container = None
        logger.debug("ServiceFacade容器已重置，下次获取时将刷新")

    def get_service(self, service_type: Type[T], safe: bool = False) -> T:
        """获取服务实例

        Args:
            service_type: 服务类型
            safe: 是否安全模式(返回ServiceResult而非抛异常)

        Returns:
            服务实例(普通模式) 或 ServiceResult(安全模式)
        """
        service_name = service_type.__name__

        try:
            # 统计访问次数
            self._access_stats[service_name] = (
                self._access_stats.get(service_name, 0) + 1
            )

            # 调试信息
            container = self.container
            registered_services = list(container.get_all_services().keys())
            logger.debug(
                f"尝试获取服务 {service_name}，容器中已注册: {registered_services}"
            )

            # 从容器获取服务
            service = container.get_service(service_type)

            if safe:
                return ServiceResult(success=True, service=service)

            logger.debug(f"✅ 成功获取服务: {service_name}")
            return service

        except ServiceNotRegisteredError as e:
            error_msg = f"服务 {service_name} 未注册: {e}"
            logger.error(error_msg)

            if safe:
                return ServiceResult(
                    success=False,
                    error_type=ServiceErrorType.NOT_REGISTERED,
                    error_message=error_msg,
                )
            raise ServiceError(ServiceErrorType.NOT_REGISTERED, error_msg)

        except Exception as e:
            error_msg = f"获取服务 {service_name} 失败: {e}"
            logger.error(error_msg)

            if safe:
                return ServiceResult(
                    success=False,
                    error_type=ServiceErrorType.INITIALIZATION_FAILED,
                    error_message=error_msg,
                )
            raise ServiceError(ServiceErrorType.INITIALIZATION_FAILED, error_msg)

    def try_get_service(self, service_type: Type[T]) -> Optional[T]:
        """尝试获取服务，失败返回None"""
        try:
            return self.get_service(service_type)
        except:
            return None

    def get_service_safe(self, service_type: Type[T]) -> ServiceResult:
        """安全获取服务，返回结果封装"""
        return self.get_service(service_type, safe=True)

    def is_service_available(self, service_type: Type[T]) -> bool:
        """检查服务是否可用"""
        return self.container.is_registered(service_type)

    def get_service_stats(self) -> Dict[str, Any]:
        """获取服务访问统计"""
        return {
            "access_stats": self._access_stats.copy(),
            "registered_services": list(self.container.get_all_services().keys()),
            "total_accesses": sum(self._access_stats.values()),
        }


# 全局服务facade实例
_service_facade = ServiceFacade()


def get_service_facade() -> ServiceFacade:
    """获取全局服务facade"""
    return _service_facade


# 便捷函数 - 兼容旧API模式
def get_service(service_type: Type[T]) -> T:
    """便捷服务获取函数 - 兼容旧代码"""
    return _service_facade.get_service(service_type)


def try_get_service(service_type: Type[T]) -> Optional[T]:
    """便捷服务尝试获取函数"""
    return _service_facade.try_get_service(service_type)


def reset_service_facade():
    """重置全局ServiceFacade容器，用于服务注册完成后刷新"""
    _service_facade.reset_container()


# 标准化错误处理装饰器
def with_service_error_handling(service_name: str = None):
    """标准化服务错误处理装饰器

    统一处理服务获取和操作中的异常
    消除424个相似错误处理模式
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            operation_name = service_name or func.__name__

            try:
                return func(*args, **kwargs)

            except ServiceError as e:
                logger.error(f"❌ 服务操作失败 [{operation_name}]: {e}")
                raise

            except Exception as e:
                logger.error(f"❌ 未知错误 [{operation_name}]: {e}")
                raise ServiceError(
                    ServiceErrorType.SERVICE_UNAVAILABLE, f"服务操作异常: {e}"
                )

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            operation_name = service_name or func.__name__

            try:
                return await func(*args, **kwargs)

            except ServiceError as e:
                logger.error(f"❌ 异步服务操作失败 [{operation_name}]: {e}")
                raise

            except Exception as e:
                logger.error(f"❌ 异步未知错误 [{operation_name}]: {e}")
                raise ServiceError(
                    ServiceErrorType.SERVICE_UNAVAILABLE, f"异步服务操作异常: {e}"
                )

        # 根据函数类型返回对应的装饰器
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    return decorator


# 专用服务获取函数 - 逐步替代原有get_*_service函数
def get_connector_manager():
    """获取连接器管理器 - 替代重复的get_connector_manager调用"""
    from services.connectors.connector_manager import ConnectorManager

    return get_service(ConnectorManager)


def get_database_service():
    """获取数据库服务 - 替代重复的get_database_service调用"""
    from services.database_service import DatabaseService

    return get_service(DatabaseService)


def get_security_manager():
    """获取安全管理器"""
    from services.ipc_security import IPCSecurityManager

    return get_service(IPCSecurityManager)


def get_config_manager():
    """获取配置管理器"""
    from config.core_config import CoreConfigManager

    return get_service(CoreConfigManager)


def get_connector_config_service():
    """获取连接器配置服务"""
    from services.connectors.connector_config_service import ConnectorConfigService

    return get_service(ConnectorConfigService)


def get_webview_config_service():
    """获取WebView配置服务"""
    from services.webview_config_service import WebViewConfigService

    return get_service(WebViewConfigService)


def get_environment_manager():
    """获取环境管理器"""
    from core.environment_manager import EnvironmentManager

    return get_service(EnvironmentManager)


if __name__ == "__main__":
    # 测试服务facade
    logging.basicConfig(level=logging.DEBUG)

    facade = get_service_facade()
    print("服务Facade初始化成功")
    print(f"可用服务: {facade.container.get_all_services()}")
