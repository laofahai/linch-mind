#!/usr/bin/env python3
"""
ServiceFacade - 精简版服务获取门面
清理43个重复函数，统一使用get_service()接口
"""

import logging
from typing import Type, TypeVar, Optional, Any, Union, List, Dict
from functools import wraps

from core.container import get_container

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ServiceResult:
    """服务获取结果包装器"""
    
    def __init__(self, service: Optional[Any] = None, error: Optional[str] = None):
        self.service = service
        self.error = error
        self.success = service is not None and error is None
    
    def unwrap(self) -> Any:
        """解包服务，如果失败则抛出异常"""
        if not self.success:
            raise RuntimeError(f"Service unavailable: {self.error}")
        return self.service
    
    def unwrap_or(self, default: Any) -> Any:
        """解包服务，如果失败则返回默认值"""
        return self.service if self.success else default


class ServiceFacade:
    """简化的服务门面 - 统一服务获取入口
    
    设计原则:
    1. 单一函数：仅提供get_service()和get_service_safe()
    2. 类型安全：完整的泛型支持
    3. 错误处理：提供安全和不安全两种模式
    4. 统计监控：服务获取统计和缓存
    """
    
    def __init__(self):
        self.container = get_container()
        # 服务访问统计
        self._access_stats: Dict[str, int] = {}
        # 缓存已获取的服务类型名称
        self._service_names: Dict[Type, str] = {}
    
    def get_service(self, service_type: Type[T], safe: bool = False) -> T:
        """获取服务实例 - 统一入口
        
        Args:
            service_type: 服务类型
            safe: 是否使用安全模式(不抛异常)
            
        Returns:
            服务实例
            
        Raises:
            RuntimeError: 服务不可用(仅在safe=False时)
        """
        service_name = self._get_service_name(service_type)
        
        # 更新访问统计
        self._access_stats[service_name] = self._access_stats.get(service_name, 0) + 1
        
        try:
            service = self.container.get_service(service_type)
            # logger.debug(f"Service获取成功: {service_name}")  # 减少日志噪音
            return service
            
        except Exception as e:
            error_msg = f"Service获取失败 {service_name}: {e}"
            logger.error(error_msg)
            
            if safe:
                return None
            else:
                raise RuntimeError(error_msg)
    
    def get_service_safe(self, service_type: Type[T]) -> ServiceResult:
        """安全获取服务 - 返回结果包装器"""
        service_name = self._get_service_name(service_type)
        
        try:
            service = self.get_service(service_type, safe=True)
            if service is None:
                return ServiceResult(error=f"{service_name} not available")
            return ServiceResult(service=service)
            
        except Exception as e:
            return ServiceResult(error=str(e))
    
    def is_service_available(self, service_type: Type) -> bool:
        """检查服务是否可用"""
        return self.container.is_registered(service_type)
    
    def get_service_info(self, service_type: Type) -> Dict[str, Any]:
        """获取服务信息"""
        service_name = self._get_service_name(service_type)
        access_count = self._access_stats.get(service_name, 0)
        
        return {
            "name": service_name,
            "available": self.is_service_available(service_type),
            "access_count": access_count,
            "container_info": self.container.get_service_info(service_type) if self.is_service_available(service_type) else None
        }
    
    def get_all_services_info(self) -> Dict[str, Dict[str, Any]]:
        """获取所有服务信息"""
        return {
            service_name: {
                "access_count": count,
                "container_info": self.container.get_all_services().get(service_name, {})
            }
            for service_name, count in self._access_stats.items()
        }
    
    def _get_service_name(self, service_type: Type) -> str:
        """获取服务类型名称（缓存）"""
        if service_type not in self._service_names:
            if hasattr(service_type, "__name__"):
                self._service_names[service_type] = service_type.__name__
            else:
                self._service_names[service_type] = str(service_type)
        return self._service_names[service_type]


# =================
# 全局单例
# =================

_service_facade: Optional[ServiceFacade] = None

def get_service_facade() -> ServiceFacade:
    """获取全局ServiceFacade实例"""
    global _service_facade
    if _service_facade is None:
        _service_facade = ServiceFacade()
    return _service_facade

def reset_service_facade():
    """重置ServiceFacade - 测试用"""
    global _service_facade
    _service_facade = None


# =================
# 便捷API函数
# =================

def get_service(service_type: Type[T]) -> T:
    """便捷服务获取函数 - 全局入口"""
    return get_service_facade().get_service(service_type)

def get_service_safe(service_type: Type[T]) -> ServiceResult:
    """便捷安全服务获取函数"""
    return get_service_facade().get_service_safe(service_type)

def is_service_available(service_type: Type) -> bool:
    """便捷服务可用性检查"""
    return get_service_facade().is_service_available(service_type)


# =================
# 装饰器支持
# =================

def with_service(service_type: Type, safe: bool = False):
    """服务注入装饰器
    
    用法:
    @with_service(DatabaseService)
    def my_function(db_service):
        # 使用db_service
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if safe:
                service_result = get_service_safe(service_type)
                if not service_result.success:
                    logger.warning(f"服务不可用，跳过函数调用: {func.__name__}")
                    return None
                service = service_result.service
            else:
                service = get_service(service_type)
            
            return func(service, *args, **kwargs)
        return wrapper
    return decorator


# =================
# 常用服务快捷函数 (仅保留最常用的)
# =================

def get_config():
    """获取配置管理器 - 最常用服务"""
    from config.config_manager import ConfigManager
    return get_service(ConfigManager)

def get_connector_manager():
    """获取连接器管理器 - 最常用服务"""
    from services.connectors.connector_manager import ConnectorManager
    return get_service(ConnectorManager)

def get_database_service():
    """获取数据库服务 - 最常用服务"""
    from services.storage.core.database import UnifiedDatabaseService
    return get_service(UnifiedDatabaseService)

def get_database_config_manager():
    """获取数据库配置管理器 - 常用服务"""
    from config.database_config_manager import DatabaseConfigManager
    return get_service(DatabaseConfigManager)


# =================
# 向后兼容(临时保留，建议逐步迁移到get_service)
# =================

# 这些函数将在下个版本中移除，请使用 get_service(ServiceType) 替代

def get_security_manager():
    """@deprecated 使用 get_service(IPCSecurityManager) 替代"""
    from services.ipc.core.security import IPCSecurityManager
    return get_service(IPCSecurityManager)

def get_environment_manager():
    """@deprecated 使用 get_service(EnvironmentManager) 替代"""
    from core.environment_manager import EnvironmentManager
    return get_service(EnvironmentManager)

def get_system_config_service():
    """@deprecated 使用 get_service(SystemConfigService) 替代"""
    from services.system_config_service import SystemConfigService
    return get_service(SystemConfigService)

def get_content_analysis_service():
    """@deprecated 使用 get_service(ContentAnalysisService) 替代"""
    from services.content_analysis_service import ContentAnalysisService
    return get_service(ContentAnalysisService)

def get_data_insights_service():
    """@deprecated 使用 get_service(DataInsightsService) 替代"""
    from services.api.data_insights_service import DataInsightsService
    return get_service(DataInsightsService)


# =================
# 统计和监控
# =================

def get_service_stats() -> Dict[str, Any]:
    """获取服务使用统计"""
    facade = get_service_facade()
    return {
        "total_services": len(facade._access_stats),
        "total_accesses": sum(facade._access_stats.values()),
        "services": facade.get_all_services_info()
    }

def print_service_stats():
    """打印服务使用统计"""
    stats = get_service_stats()
    print(f"\n📊 Service Usage Statistics:")
    print(f"Total Services: {stats['total_services']}")
    print(f"Total Accesses: {stats['total_accesses']}")
    print("\nTop Services:")
    
    # 按访问次数排序
    services = [(name, info["access_count"]) for name, info in stats["services"].items()]
    services.sort(key=lambda x: x[1], reverse=True)
    
    for name, count in services[:10]:  # 显示前10个
        print(f"  {name}: {count} accesses")