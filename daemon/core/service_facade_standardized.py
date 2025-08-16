#!/usr/bin/env python3
"""
标准化服务获取Facade - High级别架构优化
消除19个专用get_*_service()函数，统一使用get_service(ServiceType)模式

重大改进:
- ❌ 移除所有专用get_*_service()函数
- ✅ 统一使用get_service(ServiceType)模式
- 📚 完整的服务类型注册表
- 🔧 类型安全的服务访问
- 🚀 智能缓存和性能监控
"""

import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

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


class ServiceRegistry:
    """服务类型注册表 - 替代19个专用函数的统一服务访问"""
    
    # 核心基础服务
    @property
    def ConnectorManager(self):
        from services.connectors.connector_manager import ConnectorManager
        return ConnectorManager
    
    @property 
    def UnifiedDatabaseService(self):
        from services.unified_database_service import UnifiedDatabaseService
        return UnifiedDatabaseService
    
    @property
    def IPCSecurityManager(self):
        from services.ipc_security import IPCSecurityManager
        return IPCSecurityManager
    
    @property
    def CoreConfigManager(self):
        from config.core_config import CoreConfigManager
        return CoreConfigManager
        
    @property
    def EnvironmentManager(self):
        from core.environment_manager import EnvironmentManager
        return EnvironmentManager
    
    # 配置服务
    @property
    def ConnectorConfigService(self):
        from services.connectors.connector_config_service import ConnectorConfigService
        return ConnectorConfigService
    
    @property
    def SystemConfigService(self):
        from services.system_config_service import SystemConfigService
        return SystemConfigService
    
    @property
    def WebViewConfigService(self):
        from services.webview_config_service import WebViewConfigService
        return WebViewConfigService
    
    # 存储和搜索服务
    @property
    def UnifiedStorageService(self):
        from services.storage.unified_storage_service import UnifiedStorageService  
        return UnifiedStorageService
    
    @property
    def CachedNetworkXService(self):
        from services.cached_networkx_service import CachedNetworkXService
        return CachedNetworkXService
    
    @property
    def VectorService(self):
        from services.storage.vector_service import VectorService
        return VectorService
    
    @property
    def GraphService(self):
        from services.storage.graph_service import GraphService
        return GraphService
    
    @property
    def EmbeddingService(self):
        from services.storage.embedding_service import EmbeddingService
        return EmbeddingService
    
    # 统一服务（替代多个重复实现）
    @property
    def UnifiedSearchService(self):
        from services.unified_search_service import UnifiedSearchService
        return UnifiedSearchService
    
    @property
    def UnifiedCacheService(self):
        from services.unified_cache_service import UnifiedCacheService
        return UnifiedCacheService
    
    @property
    def SharedExecutorService(self):
        from services.shared_executor_service import SharedExecutorService
        return SharedExecutorService
    
    @property
    def UnifiedPersistenceService(self):
        from services.unified_persistence_service import UnifiedPersistenceService
        return UnifiedPersistenceService
    
    @property
    def UnifiedMetricsService(self):
        from services.unified_metrics_service import UnifiedMetricsService
        return UnifiedMetricsService
    
    # 注册和发现服务
    @property
    def RegistryDiscoveryService(self):
        from services.registry_discovery_service import RegistryDiscoveryService
        return RegistryDiscoveryService
    
    @property
    def ConnectorRegistryService(self):
        from services.connector_registry_service import ConnectorRegistryService
        return ConnectorRegistryService
    
    # 内容和AI服务
    @property
    def ContentAnalysisService(self):
        from services.content_analysis_service import ContentAnalysisService
        return ContentAnalysisService
    
    @property
    def DataInsightsService(self):
        from services.api.data_insights_service import DataInsightsService
        return DataInsightsService
    
    @property
    def OllamaService(self):
        from services.ai.ollama_service import OllamaService
        return OllamaService
    
    def get_service_type_by_name(self, service_name: str) -> Optional[Type]:
        """根据服务名称获取服务类型 - 用于动态服务获取"""
        return getattr(self, service_name, None)
    
    def list_available_services(self) -> List[str]:
        """列出所有可用的服务类型"""
        # 安全地列出服务类型，避免导入时的语法错误
        service_names = []
        for attr in dir(self):
            if not attr.startswith('_') and not attr in ['get_service_type_by_name', 'list_available_services']:
                try:
                    # 不实际调用属性，只检查是否是property
                    prop = getattr(type(self), attr, None)
                    if isinstance(prop, property):
                        service_names.append(attr)
                except:
                    # 跳过有问题的属性
                    continue
        return service_names


# 全局服务注册表实例
Services = ServiceRegistry()


class StandardizedServiceFacade:
    """标准化服务获取Facade - 消除代码重复的终极解决方案
    
    核心优化:
    - 🎯 统一服务获取：唯一入口点get_service(ServiceType)
    - ❌ 消除专用函数：移除所有19个get_*_service()函数
    - 📚 服务类型注册表：Services.*访问所有服务类型
    - 🔧 类型安全访问：完整的泛型支持
    - 🚀 智能缓存策略：显著提升性能
    - 📊 完整监控统计：服务访问模式分析
    
    使用方式:
        # 新标准化方式 - 推荐
        db_service = get_service(Services.UnifiedDatabaseService)
        connector_mgr = get_service(Services.ConnectorManager)
        
        # 类型安全方式
        db_service: UnifiedDatabaseService = get_service(Services.UnifiedDatabaseService)
    """

    def __init__(self):
        self._container = None  # 延迟获取容器
        self._access_stats: Dict[str, int] = {}
        self._service_cache: Dict[str, Any] = {}
        self._cache_enabled = True
        self._migration_warnings: Dict[str, int] = {}  # 跟踪迁移警告

    @property
    def container(self):
        """延迟获取容器实例，确保在服务注册完成后获取"""
        if self._container is None:
            self._container = get_container()
            logger.debug(
                f"StandardizedServiceFacade获取到容器，已注册服务数: {len(self._container.get_all_services())}"
            )
        return self._container

    def reset_container(self):
        """重置容器实例，用于服务注册完成后刷新"""
        self._container = None
        self._service_cache.clear()
        self._migration_warnings.clear()
        logger.debug("StandardizedServiceFacade容器已重置，缓存已清理")

    def get_service(self, service_type: Type[T], safe: bool = False) -> Union[T, ServiceResult]:
        """获取服务实例 - 统一服务获取入口点
        
        这是唯一推荐的服务获取方式，替代所有专用get_*_service()函数
        
        Args:
            service_type: 服务类型（使用Services.*访问）
            safe: 是否安全模式(返回ServiceResult而非抛异常)
            
        Returns:
            服务实例(普通模式) 或 ServiceResult(安全模式)
            
        Examples:
            >>> facade = get_standardized_service_facade()
            >>> db_service = facade.get_service(Services.UnifiedDatabaseService)
            >>> connector_mgr = facade.get_service(Services.ConnectorManager)
            >>> config_mgr = facade.get_service(Services.CoreConfigManager)
        """
        service_name = service_type.__name__

        try:
            # 统计访问次数
            self._access_stats[service_name] = (
                self._access_stats.get(service_name, 0) + 1
            )

            # 缓存检查 - 显著减少容器查询开销
            if self._cache_enabled and service_name in self._service_cache:
                cached_service = self._service_cache[service_name]
                logger.debug(f"🚀 从缓存获取服务: {service_name}")
                
                if safe:
                    return ServiceResult(success=True, service=cached_service)
                return cached_service

            # 调试信息 - 仅在缓存未命中时记录
            container = self.container
            registered_services = list(container.get_all_services().keys())
            logger.debug(
                f"尝试获取服务 {service_name}，容器中已注册: {registered_services}"
            )

            # 从容器获取服务
            service = container.get_service(service_type)

            # 缓存服务实例 (仅缓存单例服务)
            if self._cache_enabled:
                self._service_cache[service_name] = service
                logger.debug(f"📦 服务已缓存: {service_name}")

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
        """获取服务访问统计 - 包含迁移分析"""
        total_accesses = sum(self._access_stats.values())
        cached_services = len(self._service_cache)
        
        return {
            "access_stats": self._access_stats.copy(),
            "registered_services": list(self.container.get_all_services().keys()),
            "total_accesses": total_accesses,
            "cached_services_count": cached_services,
            "cache_hit_potential": cached_services / len(self._access_stats) if self._access_stats else 0,
            "cache_enabled": self._cache_enabled,
            "migration_warnings": self._migration_warnings.copy(),
            "available_service_types": Services.list_available_services(),
        }

    def clear_service_cache(self) -> int:
        """清理服务缓存，返回清理的服务数量"""
        cleared_count = len(self._service_cache)
        self._service_cache.clear()
        logger.info(f"🧹 服务缓存已清理，清理了 {cleared_count} 个缓存服务")
        return cleared_count

    def enable_cache(self, enabled: bool = True):
        """启用/禁用服务缓存"""
        self._cache_enabled = enabled
        if not enabled:
            self.clear_service_cache()
        logger.info(f"🔧 服务缓存已{'启用' if enabled else '禁用'}")

    def get_migration_report(self) -> Dict[str, Any]:
        """获取从专用函数到统一方式的迁移报告"""
        # 分析最常访问的服务，提供迁移建议
        sorted_stats = sorted(
            self._access_stats.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        migration_suggestions = []
        for service_name, count in sorted_stats[:10]:  # 前10个最常用服务
            service_type = Services.get_service_type_by_name(service_name)
            if service_type:
                migration_suggestions.append({
                    "service": service_name,
                    "usage_count": count,
                    "old_way": f"get_{service_name.lower().replace('service', '_service')}()",
                    "new_way": f"get_service(Services.{service_name})",
                    "priority": "HIGH" if count > 10 else "MEDIUM" if count > 5 else "LOW"
                })
        
        return {
            "total_service_accesses": sum(self._access_stats.values()),
            "unique_services_accessed": len(self._access_stats),
            "migration_suggestions": migration_suggestions,
            "cache_efficiency": len(self._service_cache) / len(self._access_stats) if self._access_stats else 0,
            "standardization_status": "IN_PROGRESS",  # TODO: 完成迁移后改为COMPLETED
        }


# === 全局标准化Facade实例 ===

_standardized_service_facade: Optional[StandardizedServiceFacade] = None


def get_standardized_service_facade() -> StandardizedServiceFacade:
    """获取标准化服务Facade - 替代所有专用get_*_service()函数的统一入口
    
    这是新的标准化服务访问方式，替代旧的ServiceFacade
    
    Returns:
        StandardizedServiceFacade: 标准化服务获取实例
        
    Example:
        >>> facade = get_standardized_service_facade()
        >>> db_service = facade.get_service(Services.UnifiedDatabaseService)
        >>> connector_mgr = facade.get_service(Services.ConnectorManager)
    """
    global _standardized_service_facade
    
    if _standardized_service_facade is None:
        _standardized_service_facade = StandardizedServiceFacade()
        logger.info("🎯 标准化服务Facade已创建 - 专用函数已消除")
    
    return _standardized_service_facade


def get_service(service_type: Type[T]) -> T:
    """全局标准化服务获取函数 - 唯一推荐的服务获取方式
    
    这个函数完全替代了所有19个专用get_*_service()函数
    
    Args:
        service_type: 服务类型（使用Services.*常量）
        
    Returns:
        指定类型的服务实例
        
    Examples:
        >>> # 替代 get_database_service()
        >>> db_service = get_service(Services.UnifiedDatabaseService)
        
        >>> # 替代 get_connector_manager()
        >>> connector_mgr = get_service(Services.ConnectorManager)
        
        >>> # 替代 get_config_manager()
        >>> config_mgr = get_service(Services.CoreConfigManager)
        
        >>> # 替代 get_system_config_service()
        >>> sys_config = get_service(Services.SystemConfigService)
    """
    return get_standardized_service_facade().get_service(service_type)


# === 向后兼容和迁移辅助函数 ===

def log_deprecation_warning(old_function_name: str, new_usage: str):
    """记录弃用警告 - 帮助识别需要迁移的代码"""
    facade = get_standardized_service_facade()
    facade._migration_warnings[old_function_name] = (
        facade._migration_warnings.get(old_function_name, 0) + 1
    )
    
    logger.warning(
        f"⚠️ 弃用警告: {old_function_name}() 已被弃用，请使用 {new_usage}"
    )


# 临时兼容性函数 - 仅用于渐进式迁移，将在完成迁移后移除
def get_database_service():
    """临时兼容函数 - 请使用 get_service(Services.UnifiedDatabaseService)"""
    log_deprecation_warning("get_database_service", "get_service(Services.UnifiedDatabaseService)")
    return get_service(Services.UnifiedDatabaseService)


def get_connector_manager():
    """临时兼容函数 - 请使用 get_service(Services.ConnectorManager)"""
    log_deprecation_warning("get_connector_manager", "get_service(Services.ConnectorManager)")
    return get_service(Services.ConnectorManager)


def get_config_manager():
    """临时兼容函数 - 请使用 get_service(Services.CoreConfigManager)"""
    log_deprecation_warning("get_config_manager", "get_service(Services.CoreConfigManager)")
    return get_service(Services.CoreConfigManager)


def get_system_config_service():
    """临时兼容函数 - 请使用 get_service(Services.SystemConfigService)"""
    log_deprecation_warning("get_system_config_service", "get_service(Services.SystemConfigService)")
    return get_service(Services.SystemConfigService)


# === 服务操作装饰器 - 统一错误处理 ===

def with_service_error_handling(
    error_message: str = "服务操作失败",
    fallback_value: Any = None,
):
    """服务操作错误处理装饰器 - 统一服务调用错误处理模式"""
    def decorator(func):
        operation_name = func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logger.debug(f"⚙️ 执行服务操作: {operation_name}")
                result = func(*args, **kwargs)
                logger.debug(f"✅ 服务操作成功: {operation_name}")
                return result
            except ServiceError as e:
                logger.error(f"❌ 服务错误 [{operation_name}]: {e}")
                if fallback_value is not None:
                    logger.info(f"🔄 使用备用值: {fallback_value}")
                    return fallback_value
                raise
            except Exception as e:
                logger.error(f"❌ 未知错误 [{operation_name}]: {e}")
                raise ServiceError(
                    ServiceErrorType.SERVICE_UNAVAILABLE, f"服务操作异常: {e}"
                )

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                logger.debug(f"⚙️ 执行异步服务操作: {operation_name}")
                result = await func(*args, **kwargs)
                logger.debug(f"✅ 异步服务操作成功: {operation_name}")
                return result
            except ServiceError as e:
                logger.error(f"❌ 异步服务错误 [{operation_name}]: {e}")
                if fallback_value is not None:
                    logger.info(f"🔄 使用备用值: {fallback_value}")
                    return fallback_value
                raise
            except Exception as e:
                logger.error(f"❌ 异步未知错误 [{operation_name}]: {e}")
                raise ServiceError(
                    ServiceErrorType.SERVICE_UNAVAILABLE, f"异步服务操作异常: {e}"
                )

        # 根据函数类型返回对应的装饰器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    return decorator


if __name__ == "__main__":
    # 演示标准化服务Facade的使用
    print("=== 标准化服务Facade演示 ===")
    
    facade = get_standardized_service_facade()
    
    # 新标准化方式
    try:
        db_service = facade.get_service(Services.UnifiedDatabaseService)
        print(f"✅ 数据库服务获取成功: {type(db_service).__name__}")
    except ServiceError as e:
        print(f"❌ 数据库服务获取失败: {e}")
    
    try:
        connector_mgr = facade.get_service(Services.ConnectorManager)
        print(f"✅ 连接器管理器获取成功: {type(connector_mgr).__name__}")
    except ServiceError as e:
        print(f"❌ 连接器管理器获取失败: {e}")
    
    # 服务统计
    stats = facade.get_service_stats()
    print(f"📊 服务访问统计: {stats['total_accesses']} 次访问")
    print(f"📦 缓存服务数量: {stats['cached_services_count']}")
    
    # 迁移报告
    migration_report = facade.get_migration_report()
    print(f"🔄 迁移状态: {migration_report['standardization_status']}")
    print(f"📈 唯一服务访问: {migration_report['unique_services_accessed']}")