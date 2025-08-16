#!/usr/bin/env python3
"""
统一配置管理器 - High级别架构优化
解决配置管理复杂度过高的问题，统一30+个get_*_config()函数

核心设计原则:
1. 单一配置入口点 - 一个管理器统管所有配置
2. 3层架构清晰分离 - 模型/管理器/上下文
3. 智能延迟加载 - 按需加载，提升启动性能
4. 环境感知配置 - 完美集成EnvironmentManager
5. 向后兼容API - 渐进式迁移，无破坏性变更
"""

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from core.environment_manager import get_environment_manager
from core.error_handling import handle_errors, ErrorSeverity, ErrorCategory
from .error_handling import get_logger

# 配置模型导入
from .core_config import (
    AppConfig, IPCServerConfig, DatabaseConfig, StorageConfig,
    ConnectorConfig, ConnectorRegistryConfig, AIConfig
)
from .intelligent_storage import IntelligentStorageConfig, IntelligentStorageConfigManager
from .ipc_security_config import IPCSecurityConfig, IPCSecurityManager
from .logging_config import LoggingConfig

logger = get_logger(__name__)

# 泛型类型变量
T = TypeVar('T')

class ConfigType:
    """配置类型常量 - 类型安全的配置访问"""
    APP = AppConfig
    IPC_SERVER = IPCServerConfig
    DATABASE = DatabaseConfig
    STORAGE = StorageConfig
    CONNECTOR = ConnectorConfig
    CONNECTOR_REGISTRY = ConnectorRegistryConfig
    AI = AIConfig
    INTELLIGENT_STORAGE = IntelligentStorageConfig
    IPC_SECURITY = IPCSecurityConfig
    LOGGING = LoggingConfig


class UnifiedConfigManager:
    """统一配置管理器 - 解决配置管理复杂度问题
    
    功能特性:
    - 🎯 统一配置入口：替代30+个分散的get_*_config()函数
    - 🚀 智能延迟加载：按需加载配置段，显著提升启动性能
    - 🔧 环境感知配置：完整集成EnvironmentManager
    - 📦 类型安全访问：泛型支持，编译时类型检查
    - 🔄 智能缓存策略：LRU缓存+失效机制，平衡性能与内存
    - ⚡ 向后兼容API：无破坏性变更，支持渐进式迁移
    """

    def __init__(self, config_root: Optional[Path] = None):
        """初始化统一配置管理器
        
        Args:
            config_root: 配置根目录，None则使用环境管理器路径
        """
        # 环境管理器集成
        self.env_manager = get_environment_manager()
        self.config_root = config_root
        
        # 配置上下文（延迟初始化）
        self._config_context = None
        
        # 专用配置管理器实例（延迟初始化）
        self._core_config_manager = None
        self._intelligent_storage_manager = None
        self._ipc_security_manager = None
        self._logging_config = None
        
        # 缓存状态跟踪
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'loads': 0
        }
        
        logger.info("🎯 UnifiedConfigManager初始化完成 - 智能延迟加载模式")

    @property
    def config_context(self):
        """延迟初始化配置上下文"""
        if self._config_context is None:
            from .config_context import create_config_context
            self._config_context = create_config_context(self.config_root)
            logger.debug("📂 配置上下文已延迟加载")
        return self._config_context

    def get_config(self, config_type: Type[T]) -> T:
        """统一配置获取接口 - 类型安全的配置访问
        
        Args:
            config_type: 配置类型（ConfigType.*）
            
        Returns:
            指定类型的配置对象
            
        Example:
            >>> manager = get_unified_config_manager()
            >>> db_config = manager.get_config(ConfigType.DATABASE)
            >>> server_config = manager.get_config(ConfigType.IPC_SERVER)
        """
        # 类型到加载方法的映射
        type_to_loader = {
            AppConfig: self._get_app_config,
            IPCServerConfig: self._get_ipc_server_config,
            DatabaseConfig: self._get_database_config,
            StorageConfig: self._get_storage_config,
            ConnectorConfig: self._get_connector_config,
            ConnectorRegistryConfig: self._get_connector_registry_config,
            AIConfig: self._get_ai_config,
            IntelligentStorageConfig: self._get_intelligent_storage_config,
            IPCSecurityConfig: self._get_ipc_security_config,
            LoggingConfig: self._get_logging_config,
        }
        
        loader = type_to_loader.get(config_type)
        if not loader:
            raise ValueError(f"不支持的配置类型: {config_type}")
        
        try:
            self._cache_stats['loads'] += 1
            config = loader()
            logger.debug(f"✅ 配置加载成功: {config_type.__name__}")
            return config
        except Exception as e:
            logger.error(f"❌ 配置加载失败: {config_type.__name__} - {e}")
            raise

    @lru_cache(maxsize=32)
    def _get_core_config_manager(self):
        """获取核心配置管理器 - 缓存单例"""
        if self._core_config_manager is None:
            from .core_config import CoreConfigManager
            self._core_config_manager = CoreConfigManager(
                config_context=self.config_context,
                config_root=self.config_root
            )
            logger.debug("🔧 CoreConfigManager已创建")
        return self._core_config_manager

    @lru_cache(maxsize=8)
    def _get_app_config(self) -> AppConfig:
        """获取应用配置 - 智能缓存"""
        return self._get_core_config_manager().config

    @lru_cache(maxsize=8)
    def _get_ipc_server_config(self) -> IPCServerConfig:
        """获取IPC服务器配置"""
        return self._get_app_config().server

    @lru_cache(maxsize=8)
    def _get_database_config(self) -> DatabaseConfig:
        """获取数据库配置"""
        return self._get_app_config().database

    @lru_cache(maxsize=8)
    def _get_storage_config(self) -> StorageConfig:
        """获取存储配置"""
        return self._get_app_config().storage

    @lru_cache(maxsize=8)
    def _get_connector_config(self) -> ConnectorConfig:
        """获取连接器配置"""
        return self._get_app_config().connectors

    @lru_cache(maxsize=8)
    def _get_connector_registry_config(self) -> ConnectorRegistryConfig:
        """获取连接器注册表配置"""
        return self._get_app_config().connector_registry

    @lru_cache(maxsize=8)
    def _get_ai_config(self) -> AIConfig:
        """获取AI配置"""
        return self._get_app_config().ai

    @lru_cache(maxsize=8)
    def _get_intelligent_storage_config(self) -> IntelligentStorageConfig:
        """获取智能存储配置"""
        if self._intelligent_storage_manager is None:
            self._intelligent_storage_manager = IntelligentStorageConfigManager()
        return self._intelligent_storage_manager.get_config()

    @lru_cache(maxsize=8)
    def _get_ipc_security_config(self) -> IPCSecurityConfig:
        """获取IPC安全配置"""
        if self._ipc_security_manager is None:
            from .ipc_security_config import get_ipc_security_manager
            self._ipc_security_manager = get_ipc_security_manager()
        return self._ipc_security_manager.config

    @lru_cache(maxsize=8)
    def _get_logging_config(self) -> LoggingConfig:
        """获取日志配置"""
        if self._logging_config is None:
            from .logging_config import get_logging_config
            self._logging_config = get_logging_config()
        return self._logging_config

    # === 便捷配置访问方法 - 向后兼容API ===
    
    def get_server_config(self) -> IPCServerConfig:
        """获取服务器配置 - 兼容性方法"""
        return self.get_config(ConfigType.IPC_SERVER)

    def get_database_config(self) -> DatabaseConfig:
        """获取数据库配置 - 兼容性方法"""
        return self.get_config(ConfigType.DATABASE)

    def get_storage_config(self) -> StorageConfig:
        """获取存储配置 - 兼容性方法"""
        return self.get_config(ConfigType.STORAGE)

    def get_connector_config(self) -> ConnectorConfig:
        """获取连接器配置 - 兼容性方法"""
        return self.get_config(ConfigType.CONNECTOR)

    def get_ai_config(self) -> AIConfig:
        """获取AI配置 - 兼容性方法"""
        return self.get_config(ConfigType.AI)

    def get_intelligent_storage_config(self) -> IntelligentStorageConfig:
        """获取智能存储配置 - 兼容性方法"""
        return self.get_config(ConfigType.INTELLIGENT_STORAGE)

    def get_ipc_security_config(self) -> IPCSecurityConfig:
        """获取IPC安全配置 - 兼容性方法"""
        return self.get_config(ConfigType.IPC_SECURITY)

    def get_logging_config(self) -> LoggingConfig:
        """获取日志配置 - 兼容性方法"""
        return self.get_config(ConfigType.LOGGING)

    # === 路径访问方法 - 统一路径管理 ===
    
    @lru_cache(maxsize=16)
    def get_paths(self) -> Dict[str, Path]:
        """获取所有重要路径信息 - 统一路径访问"""
        env_config = self.env_manager.current_config
        return {
            "config": env_config.config_dir,
            "data": env_config.data_dir,
            "logs": env_config.logs_dir,
            "database": env_config.database_dir,
            "primary_config": env_config.config_dir / "app.toml",
            "app_data": env_config.data_dir / "app_data",
            "connectors": env_config.data_dir / "connectors",
            "cache": env_config.data_dir / "cache",
            "temp": env_config.data_dir / "temp",
        }

    def get_config_dir(self) -> Path:
        """获取配置目录"""
        return self.env_manager.current_config.config_dir

    def get_data_dir(self) -> Path:
        """获取数据目录"""
        return self.env_manager.current_config.data_dir

    def get_logs_dir(self) -> Path:
        """获取日志目录"""
        return self.env_manager.current_config.logs_dir

    def get_database_dir(self) -> Path:
        """获取数据库目录"""
        return self.env_manager.current_config.database_dir

    # === 特殊配置方法 - 高级配置访问 ===
    
    def get_connector_specific_config(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取特定连接器配置
        
        Args:
            connector_id: 连接器ID
            
        Returns:
            连接器专用配置，如果不存在返回None
        """
        core_manager = self._get_core_config_manager()
        if hasattr(core_manager, 'get_connector_config'):
            return core_manager.get_connector_config(connector_id)
        return None

    def get_system_config(self) -> Dict[str, Any]:
        """获取系统配置快照 - 用于IPC路由"""
        core_manager = self._get_core_config_manager()
        if hasattr(core_manager, 'get_system_config'):
            return core_manager.get_system_config()
        
        # 构建基础系统配置
        app_config = self.get_config(ConfigType.APP)
        return {
            "app_name": app_config.app_name,
            "version": app_config.version,
            "debug": app_config.debug,
            "environment": self.env_manager.current_environment.value,
            "paths": {str(k): str(v) for k, v in self.get_paths().items()},
        }

    # === 配置验证和管理 ===
    
    @handle_errors(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.CONFIGURATION,
        user_message="配置验证失败"
    )
    def validate_all_configs(self) -> List[str]:
        """验证所有配置 - 全面配置健康检查
        
        Returns:
            配置错误列表，空列表表示全部正常
        """
        all_errors = []
        
        # 验证核心配置
        try:
            app_config = self.get_config(ConfigType.APP)
            if not app_config.app_name:
                all_errors.append("应用名称不能为空")
        except Exception as e:
            all_errors.append(f"核心配置验证失败: {e}")

        # 验证智能存储配置
        try:
            storage_manager = self._intelligent_storage_manager
            if storage_manager:
                storage_errors = storage_manager.validate_config()
                all_errors.extend([f"存储配置: {err}" for err in storage_errors])
        except Exception as e:
            all_errors.append(f"智能存储配置验证失败: {e}")

        # 验证环境配置
        try:
            paths = self.get_paths()
            for path_name, path_obj in paths.items():
                if path_name.endswith('_dir') and not path_obj.exists():
                    all_errors.append(f"目录不存在: {path_name} = {path_obj}")
        except Exception as e:
            all_errors.append(f"路径配置验证失败: {e}")

        logger.info(f"配置验证完成，发现 {len(all_errors)} 个问题")
        return all_errors

    def clear_cache(self) -> None:
        """清理所有配置缓存 - 开发和调试用"""
        # 清理LRU缓存
        cache_methods = [
            self._get_core_config_manager,
            self._get_app_config,
            self._get_ipc_server_config,
            self._get_database_config,
            self._get_storage_config,
            self._get_connector_config,
            self._get_connector_registry_config,
            self._get_ai_config,
            self._get_intelligent_storage_config,
            self._get_ipc_security_config,
            self._get_logging_config,
            self.get_paths,
        ]
        
        for method in cache_methods:
            try:
                method.cache_clear()
            except AttributeError:
                pass  # 方法可能没有缓存装饰器

        # 重置专用管理器
        self._core_config_manager = None
        self._intelligent_storage_manager = None
        self._ipc_security_manager = None
        self._logging_config = None
        self._config_context = None

        # 重置统计信息
        self._cache_stats = {'hits': 0, 'misses': 0, 'loads': 0}
        
        logger.info("🧹 统一配置管理器缓存已清理")

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息 - 监控和优化"""
        cache_info_dict = {}
        
        # 收集缓存信息
        cache_methods = [
            ('core_manager', self._get_core_config_manager),
            ('app_config', self._get_app_config),
            ('server_config', self._get_ipc_server_config),
            ('database_config', self._get_database_config),
            ('storage_config', self._get_storage_config),
            ('connector_config', self._get_connector_config),
            ('ai_config', self._get_ai_config),
            ('paths', self.get_paths),
        ]
        
        for name, method in cache_methods:
            try:
                info = method.cache_info()
                cache_info_dict[name] = {
                    'hits': info.hits,
                    'misses': info.misses,
                    'maxsize': info.maxsize,
                    'currsize': info.currsize
                }
            except AttributeError:
                cache_info_dict[name] = {'status': 'no_cache'}

        total_hits = sum(info.get('hits', 0) for info in cache_info_dict.values() if isinstance(info, dict))
        total_misses = sum(info.get('misses', 0) for info in cache_info_dict.values() if isinstance(info, dict))
        hit_rate = total_hits / (total_hits + total_misses) if (total_hits + total_misses) > 0 else 0

        return {
            "cache_hit_rate": f"{hit_rate:.2%}",
            "total_cache_hits": total_hits,
            "total_cache_misses": total_misses,
            "config_loads": self._cache_stats['loads'],
            "cache_details": cache_info_dict,
            "environment": self.env_manager.current_environment.value,
            "managers_initialized": {
                'core_config': self._core_config_manager is not None,
                'intelligent_storage': self._intelligent_storage_manager is not None,
                'ipc_security': self._ipc_security_manager is not None,
                'logging': self._logging_config is not None,
            }
        }


# === 全局单例管理 ===

_unified_config_manager: Optional[UnifiedConfigManager] = None


def get_unified_config_manager(**kwargs) -> UnifiedConfigManager:
    """获取全局统一配置管理器实例
    
    这是替代30+个get_*_config()函数的统一入口点
    
    Returns:
        UnifiedConfigManager: 全局配置管理器实例
        
    Example:
        >>> manager = get_unified_config_manager()
        >>> db_config = manager.get_config(ConfigType.DATABASE)
        >>> server_config = manager.get_server_config()  # 兼容性API
    """
    global _unified_config_manager
    
    if _unified_config_manager is None:
        _unified_config_manager = UnifiedConfigManager(**kwargs)
        logger.info("🎯 全局统一配置管理器已创建")
    
    return _unified_config_manager


def reset_unified_config_manager():
    """重置全局配置管理器 - 测试和开发用"""
    global _unified_config_manager
    
    if _unified_config_manager:
        _unified_config_manager.clear_cache()
    
    _unified_config_manager = None
    logger.info("🔄 全局统一配置管理器已重置")


# === 兼容性函数 - 渐进式迁移支持 ===

def get_config(config_type: Type[T]) -> T:
    """全局配置获取函数 - 统一入口点
    
    这个函数替代了所有分散的get_*_config()函数
    
    Args:
        config_type: 配置类型（使用ConfigType.*常量）
        
    Returns:
        指定类型的配置对象
        
    Example:
        >>> from config.unified_config_manager import get_config, ConfigType
        >>> db_config = get_config(ConfigType.DATABASE)
        >>> storage_config = get_config(ConfigType.STORAGE)
    """
    return get_unified_config_manager().get_config(config_type)


# 向后兼容的便捷函数 - 支持旧代码渐进式迁移
def get_server_config() -> IPCServerConfig:
    """兼容性函数：获取服务器配置"""
    return get_config(ConfigType.IPC_SERVER)


def get_database_config() -> DatabaseConfig:
    """兼容性函数：获取数据库配置"""
    return get_config(ConfigType.DATABASE)


def get_storage_config() -> StorageConfig:
    """兼容性函数：获取存储配置"""
    return get_config(ConfigType.STORAGE)


def get_connector_config() -> ConnectorConfig:
    """兼容性函数：获取连接器配置"""
    return get_config(ConfigType.CONNECTOR)


def get_ai_config() -> AIConfig:
    """兼容性函数：获取AI配置"""
    return get_config(ConfigType.AI)


def get_intelligent_storage_config() -> IntelligentStorageConfig:
    """兼容性函数：获取智能存储配置"""
    return get_config(ConfigType.INTELLIGENT_STORAGE)


if __name__ == "__main__":
    # 演示统一配置管理器的使用
    print("=== 统一配置管理器演示 ===")
    
    manager = get_unified_config_manager()
    
    # 新式API - 类型安全
    db_config = manager.get_config(ConfigType.DATABASE)
    server_config = manager.get_config(ConfigType.IPC_SERVER)
    
    print(f"数据库URL: {db_config.sqlite_url}")
    print(f"服务器调试模式: {server_config.debug}")
    
    # 兼容性API
    storage_config = manager.get_storage_config()
    print(f"存储数据目录: {storage_config.data_directory}")
    
    # 性能统计
    stats = manager.get_performance_stats()
    print(f"缓存命中率: {stats['cache_hit_rate']}")
    print(f"配置加载次数: {stats['config_loads']}")
    
    # 验证配置
    errors = manager.validate_all_configs()
    print(f"配置验证结果: {len(errors)} 个错误")