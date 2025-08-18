#!/usr/bin/env python3
"""
配置桥接器 - 新旧配置系统兼容性桥接
确保平滑过渡到新的配置文件系统

功能:
- 新旧配置系统的兼容性桥接
- 配置迁移和转换
- 统一配置访问接口
- 向后兼容支持
"""

import logging
from typing import Any, Dict, Optional, Type, TypeVar
from pathlib import Path

from core.environment_manager import get_environment_manager
from core.error_handling import handle_errors, ErrorSeverity, ErrorCategory

logger = logging.getLogger(__name__)

# 类型变量
T = TypeVar('T')


class ConfigurationBridge:
    """配置桥接器 - 统一新旧配置系统访问
    
    这个类提供了一个统一的接口来访问配置，
    自动处理新旧配置系统之间的转换和兼容性问题。
    """
    
    def __init__(self):
        """初始化配置桥接器"""
        self.env_manager = get_environment_manager()
        
        # 延迟初始化各种配置管理器
        self._database_config_manager = None
        self._core_config_manager = None
        self._unified_config_manager = None
        self._intelligent_storage_manager = None
        
        # 配置缓存
        self._config_cache = {}
        
        logger.info("Configuration bridge initialized")
    
    @property
    def database_config_manager(self):
        """获取数据库配置管理器（延迟加载）"""
        if self._database_config_manager is None:
            try:
                from .database_config_manager import get_database_config_manager
                self._database_config_manager = get_database_config_manager()
                logger.debug("Database config manager loaded")
            except Exception as e:
                logger.warning(f"Failed to load database config manager: {e}")
                self._database_config_manager = None
        return self._database_config_manager
    
    # 向后兼容别名
    @property
    def user_config_manager(self):
        """获取用户配置管理器（向后兼容别名）"""
        return self.database_config_manager
    
    @property
    def core_config_manager(self):
        """获取核心配置管理器（延迟加载）"""
        if self._core_config_manager is None:
            try:
                from .core_config import get_core_config
                self._core_config_manager = get_core_config()
                logger.debug("Core config manager loaded")
            except Exception as e:
                logger.warning(f"Failed to load core config manager: {e}")
                self._core_config_manager = None
        return self._core_config_manager
    
    @property
    def unified_config_manager(self):
        """获取统一配置管理器（延迟加载）"""
        if self._unified_config_manager is None:
            try:
                from .unified_config_manager import get_unified_config_manager
                self._unified_config_manager = get_unified_config_manager()
                logger.debug("Unified config manager loaded")
            except Exception as e:
                logger.warning(f"Failed to load unified config manager: {e}")
                self._unified_config_manager = None
        return self._unified_config_manager
    
    @property
    def intelligent_storage_manager(self):
        """获取智能存储配置管理器（延迟加载）"""
        if self._intelligent_storage_manager is None:
            try:
                from .intelligent_storage import get_config_manager
                self._intelligent_storage_manager = get_config_manager()
                logger.debug("Intelligent storage manager loaded")
            except Exception as e:
                logger.warning(f"Failed to load intelligent storage manager: {e}")
                self._intelligent_storage_manager = None
        return self._intelligent_storage_manager
    
    @handle_errors(
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.CONFIGURATION,
        user_message="配置获取失败"
    )
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置 - 优先使用用户配置"""
        cache_key = "database_config"
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        try:
            # 优先使用用户配置
            if self.user_config_manager:
                user_config = self.user_config_manager.get_config()
                config = {
                    "type": user_config.database.type,
                    "host": user_config.database.host,
                    "port": user_config.database.port,
                    "database": user_config.database.database,
                    "username": user_config.database.username,
                    "password": user_config.database.password,
                    "sqlite_file": user_config.database.sqlite_file,
                    "use_encryption": user_config.database.use_encryption,
                    "max_connections": user_config.database.max_connections,
                    "connection_timeout": user_config.database.connection_timeout,
                }
                self._config_cache[cache_key] = config
                return config
        except Exception as e:
            logger.warning(f"Failed to get user database config: {e}")
        
        # 回退到核心配置
        try:
            if self.core_config_manager:
                core_config = self.core_config_manager.config.database
                config = {
                    "type": "sqlite",
                    "sqlite_url": core_config.sqlite_url,
                    "chroma_persist_directory": core_config.chroma_persist_directory,
                    "embedding_model": core_config.embedding_model,
                    "vector_dimension": core_config.vector_dimension,
                }
                self._config_cache[cache_key] = config
                return config
        except Exception as e:
            logger.warning(f"Failed to get core database config: {e}")
        
        # 最终默认值
        default_config = {
            "type": "sqlite",
            "sqlite_file": "linch_mind.db",
            "use_encryption": True,
            "max_connections": 20,
            "connection_timeout": 30,
        }
        self._config_cache[cache_key] = default_config
        return default_config
    
    @handle_errors(
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.CONFIGURATION,
        user_message="Ollama配置获取失败"
    )
    def get_ollama_config(self) -> Dict[str, Any]:
        """获取Ollama配置 - 优先使用用户配置"""
        cache_key = "ollama_config"
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        try:
            # 优先使用用户配置
            if self.user_config_manager:
                user_config = self.user_config_manager.get_config()
                config = {
                    "host": user_config.ollama.host,
                    "embedding_model": user_config.ollama.embedding_model,
                    "llm_model": user_config.ollama.llm_model,
                    "value_threshold": user_config.ollama.value_threshold,
                    "entity_threshold": user_config.ollama.entity_threshold,
                    "max_content_length": user_config.ollama.max_content_length,
                    "request_timeout": user_config.ollama.request_timeout,
                    "connection_timeout": user_config.ollama.connection_timeout,
                    "enable_cache": user_config.ollama.enable_cache,
                    "cache_ttl_seconds": user_config.ollama.cache_ttl_seconds,
                }
                self._config_cache[cache_key] = config
                return config
        except Exception as e:
            logger.warning(f"Failed to get user ollama config: {e}")
        
        # 回退到智能存储配置
        try:
            if self.intelligent_storage_manager:
                storage_config = self.intelligent_storage_manager.get_config()
                config = {
                    "host": storage_config.ollama.host,
                    "embedding_model": storage_config.ollama.embedding_model,
                    "llm_model": storage_config.ollama.llm_model,
                    "value_threshold": storage_config.ollama.value_threshold,
                    "entity_threshold": storage_config.ollama.entity_threshold,
                    "max_content_length": storage_config.ollama.max_content_length,
                    "request_timeout": storage_config.ollama.request_timeout,
                    "connection_timeout": storage_config.ollama.connection_timeout,
                }
                self._config_cache[cache_key] = config
                return config
        except Exception as e:
            logger.warning(f"Failed to get intelligent storage ollama config: {e}")
        
        # 最终默认值
        default_config = {
            "host": "http://localhost:11434",
            "embedding_model": "nomic-embed-text:latest",
            "llm_model": "qwen2.5:0.5b",
            "value_threshold": 0.3,
            "entity_threshold": 0.8,
            "max_content_length": 10000,
            "request_timeout": 30,
            "connection_timeout": 5,
        }
        self._config_cache[cache_key] = default_config
        return default_config
    
    @handle_errors(
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.CONFIGURATION,
        user_message="IPC配置获取失败"
    )
    def get_ipc_config(self) -> Dict[str, Any]:
        """获取IPC配置 - 优先使用用户配置"""
        cache_key = "ipc_config"
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        try:
            # 优先使用用户配置
            if self.user_config_manager:
                user_config = self.user_config_manager.get_config()
                config = {
                    "socket_path": user_config.ipc.socket_path,
                    "socket_permissions": user_config.ipc.socket_permissions,
                    "pipe_name": user_config.ipc.pipe_name,
                    "max_connections": user_config.ipc.max_connections,
                    "connection_timeout": user_config.ipc.connection_timeout,
                    "auth_required": user_config.ipc.auth_required,
                    "buffer_size": user_config.ipc.buffer_size,
                    "enable_compression": user_config.ipc.enable_compression,
                }
                self._config_cache[cache_key] = config
                return config
        except Exception as e:
            logger.warning(f"Failed to get user ipc config: {e}")
        
        # 回退到核心配置
        try:
            if self.core_config_manager:
                core_config = self.core_config_manager.config.server
                config = {
                    "socket_path": core_config.socket_path,
                    "pipe_name": core_config.pipe_name,
                    "max_connections": core_config.max_connections,
                    "connection_timeout": core_config.connection_timeout,
                    "auth_required": core_config.auth_required,
                    "reload": core_config.reload,
                    "log_level": core_config.log_level,
                    "debug": core_config.debug,
                }
                self._config_cache[cache_key] = config
                return config
        except Exception as e:
            logger.warning(f"Failed to get core ipc config: {e}")
        
        # 最终默认值
        default_config = {
            "socket_path": "",
            "pipe_name": "",
            "max_connections": 100,
            "connection_timeout": 30,
            "auth_required": True,
            "buffer_size": 8192,
            "enable_compression": False,
        }
        self._config_cache[cache_key] = default_config
        return default_config
    
    def get_vector_config(self) -> Dict[str, Any]:
        """获取向量配置"""
        cache_key = "vector_config"
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        try:
            # 优先使用用户配置
            if self.user_config_manager:
                user_config = self.user_config_manager.get_config()
                config = {
                    "provider": user_config.vector.provider,
                    "vector_dimension": user_config.vector.vector_dimension,
                    "compressed_dimension": user_config.vector.compressed_dimension,
                    "shard_size_limit": user_config.vector.shard_size_limit,
                    "compression_method": user_config.vector.compression_method,
                    "index_type": user_config.vector.index_type,
                    "max_memory_mb": user_config.vector.max_memory_mb,
                    "preload_hot_shards": user_config.vector.preload_hot_shards,
                    "max_search_results": user_config.vector.max_search_results,
                    "search_timeout": user_config.vector.search_timeout,
                }
                self._config_cache[cache_key] = config
                return config
        except Exception as e:
            logger.warning(f"Failed to get user vector config: {e}")
        
        # 最终默认值
        default_config = {
            "provider": "faiss",
            "vector_dimension": 384,
            "compressed_dimension": 256,
            "shard_size_limit": 100000,
            "compression_method": "PQ",
            "index_type": "HNSW",
            "max_memory_mb": 1024,
            "preload_hot_shards": True,
            "max_search_results": 10,
            "search_timeout": 5,
        }
        self._config_cache[cache_key] = default_config
        return default_config
    
    def get_security_config(self) -> Dict[str, Any]:
        """获取安全配置"""
        cache_key = "security_config"
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        try:
            # 优先使用用户配置
            if self.user_config_manager:
                user_config = self.user_config_manager.get_config()
                config = {
                    "encrypt_database": user_config.security.encrypt_database,
                    "encrypt_vectors": user_config.security.encrypt_vectors,
                    "encrypt_logs": user_config.security.encrypt_logs,
                    "enable_access_control": user_config.security.enable_access_control,
                    "allowed_processes": user_config.security.allowed_processes,
                    "enable_audit_logging": user_config.security.enable_audit_logging,
                    "audit_log_retention_days": user_config.security.audit_log_retention_days,
                    "require_authentication": user_config.security.require_authentication,
                    "session_timeout_minutes": user_config.security.session_timeout_minutes,
                }
                self._config_cache[cache_key] = config
                return config
        except Exception as e:
            logger.warning(f"Failed to get user security config: {e}")
        
        # 最终默认值 - 根据环境调整
        is_production = self.env_manager.current_environment.value == "production"
        default_config = {
            "encrypt_database": is_production,
            "encrypt_vectors": False,
            "encrypt_logs": False,
            "enable_access_control": is_production,
            "allowed_processes": [],
            "enable_audit_logging": is_production,
            "audit_log_retention_days": 90,
            "require_authentication": is_production,
            "session_timeout_minutes": 60,
        }
        self._config_cache[cache_key] = default_config
        return default_config
    
    def get_performance_config(self) -> Dict[str, Any]:
        """获取性能配置"""
        cache_key = "performance_config"
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        try:
            # 优先使用用户配置
            if self.user_config_manager:
                user_config = self.user_config_manager.get_config()
                config = {
                    "enable_caching": user_config.performance.enable_caching,
                    "cache_size_mb": user_config.performance.cache_size_mb,
                    "cache_ttl_seconds": user_config.performance.cache_ttl_seconds,
                    "max_workers": user_config.performance.max_workers,
                    "max_concurrent_requests": user_config.performance.max_concurrent_requests,
                    "max_memory_gb": user_config.performance.max_memory_gb,
                    "max_storage_gb": user_config.performance.max_storage_gb,
                    "auto_cleanup": user_config.performance.auto_cleanup,
                    "cleanup_interval_hours": user_config.performance.cleanup_interval_hours,
                }
                self._config_cache[cache_key] = config
                return config
        except Exception as e:
            logger.warning(f"Failed to get user performance config: {e}")
        
        # 最终默认值
        default_config = {
            "enable_caching": True,
            "cache_size_mb": 512,
            "cache_ttl_seconds": 3600,
            "max_workers": 4,
            "max_concurrent_requests": 100,
            "max_memory_gb": 2.0,
            "max_storage_gb": 10.0,
            "auto_cleanup": True,
            "cleanup_interval_hours": 24,
        }
        self._config_cache[cache_key] = default_config
        return default_config
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        cache_key = "logging_config"
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        try:
            # 优先使用用户配置
            if self.user_config_manager:
                user_config = self.user_config_manager.get_config()
                config = {
                    "level": user_config.logging.level,
                    "format": user_config.logging.format,
                    "enable_console": user_config.logging.enable_console,
                    "enable_file": user_config.logging.enable_file,
                    "log_file": user_config.logging.log_file,
                    "max_file_size_mb": user_config.logging.max_file_size_mb,
                    "backup_count": user_config.logging.backup_count,
                    "component_levels": user_config.logging.component_levels,
                }
                self._config_cache[cache_key] = config
                return config
        except Exception as e:
            logger.warning(f"Failed to get user logging config: {e}")
        
        # 最终默认值
        default_config = {
            "level": "info",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "enable_console": True,
            "enable_file": True,
            "log_file": "linch-mind.log",
            "max_file_size_mb": 10,
            "backup_count": 5,
            "component_levels": {},
        }
        self._config_cache[cache_key] = default_config
        return default_config
    
    def clear_cache(self):
        """清理配置缓存"""
        self._config_cache.clear()
        logger.debug("Configuration cache cleared")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        return {
            "environment": self.env_manager.current_environment.value,
            "config_directory": str(self.env_manager.get_config_directory()),
            "has_user_config": self.user_config_manager is not None,
            "has_core_config": self.core_config_manager is not None,
            "has_unified_config": self.unified_config_manager is not None,
            "cache_size": len(self._config_cache),
            "cached_configs": list(self._config_cache.keys()),
        }
    
    def migrate_env_vars_to_config(self) -> Dict[str, Any]:
        """将环境变量迁移到配置文件"""
        import os
        
        migration_report = {
            "migrated_vars": [],
            "skipped_vars": [],
            "errors": []
        }
        
        # 环境变量映射
        env_var_mappings = {
            'OLLAMA_HOST': ('ollama', 'host'),
            'OLLAMA_EMBEDDING_MODEL': ('ollama', 'embedding_model'),
            'OLLAMA_LLM_MODEL': ('ollama', 'llm_model'),
            'AI_VALUE_THRESHOLD': ('ollama', 'value_threshold'),
            'ENABLE_INTELLIGENT_PROCESSING': ('performance', 'enable_caching'),
            'LINCH_DEBUG': ('debug', None),
        }
        
        try:
            if not self.user_config_manager:
                migration_report["errors"].append("User config manager not available")
                return migration_report
            
            user_config = self.user_config_manager.get_config()
            
            for env_var, (section, key) in env_var_mappings.items():
                env_value = os.getenv(env_var)
                if env_value is not None:
                    try:
                        if section == 'debug':
                            user_config.debug = env_value.lower() in ('true', '1', 'yes')
                            migration_report["migrated_vars"].append(f"{env_var} -> debug")
                        else:
                            section_obj = getattr(user_config, section)
                            
                            # 类型转换
                            if key == 'value_threshold':
                                value = float(env_value)
                            elif key in ['enable_caching']:
                                value = env_value.lower() in ('true', '1', 'yes')
                            else:
                                value = env_value
                            
                            setattr(section_obj, key, value)
                            migration_report["migrated_vars"].append(f"{env_var} -> {section}.{key}")
                            
                    except Exception as e:
                        migration_report["errors"].append(f"Failed to migrate {env_var}: {e}")
                else:
                    migration_report["skipped_vars"].append(env_var)
            
            # 保存更新的配置
            if migration_report["migrated_vars"]:
                self.user_config_manager.save_config(user_config)
                
        except Exception as e:
            migration_report["errors"].append(f"Migration failed: {e}")
        
        return migration_report


# 全局配置桥接器实例
_config_bridge: Optional[ConfigurationBridge] = None


def get_config_bridge() -> ConfigurationBridge:
    """获取配置桥接器单例"""
    global _config_bridge
    if _config_bridge is None:
        _config_bridge = ConfigurationBridge()
    return _config_bridge


# 便捷访问函数
def get_bridged_database_config() -> Dict[str, Any]:
    """获取桥接的数据库配置"""
    return get_config_bridge().get_database_config()


def get_bridged_ollama_config() -> Dict[str, Any]:
    """获取桥接的Ollama配置"""
    return get_config_bridge().get_ollama_config()


def get_bridged_ipc_config() -> Dict[str, Any]:
    """获取桥接的IPC配置"""
    return get_config_bridge().get_ipc_config()


def get_bridged_security_config() -> Dict[str, Any]:
    """获取桥接的安全配置"""
    return get_config_bridge().get_security_config()