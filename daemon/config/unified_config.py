#!/usr/bin/env python3
"""
统一配置管理 - 消除重复定义和架构混乱
合并 core_config.py 和 database_config_manager.py 的重复功能

Linus原则：
- KISS原则：一个配置概念只定义一次  
- 消除重复：DatabaseConfig、IPCConfig、OllamaConfig统一定义
- 数据结构优先：清晰的配置数据结构设计
"""

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from core.environment_manager import get_environment_manager
from core.service_facade import get_database_service
from models.database_models import SystemConfigEntry, SystemConfigHistory
from .bootstrap_config import get_bootstrap_config, BootstrapConfigManager
from .error_handling import (
    ConfigFileError,
    ConfigValidationError,
    get_logger,
    safe_operation,
    validate_required_field,
)

logger = get_logger(__name__)


@dataclass
class UnifiedDatabaseConfig:
    """统一数据库配置 - 合并所有数据库相关配置"""
    
    # SQLite基础配置
    sqlite_file: str = "linch_mind.db"
    chroma_persist_directory: str = ""
    
    # 完整数据库连接配置
    type: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    database: str = "linch_mind"
    username: str = ""
    password: str = ""
    use_encryption: bool = True
    max_connections: int = 20
    connection_timeout: int = 30
    
    @property
    def sqlite_url(self) -> str:
        """向后兼容属性：将sqlite_file转换为sqlite_url格式"""
        if not self.sqlite_file:
            return ""
        if self.sqlite_file == ":memory:":
            return "sqlite:///:memory:"
        return f"sqlite:///{self.sqlite_file}"


@dataclass
class UnifiedIPCConfig:
    """统一IPC配置 - 合并所有IPC相关配置"""
    
    # 基础IPC配置
    socket_path: Optional[str] = None
    pipe_name: Optional[str] = None
    reload: bool = True
    log_level: str = "info"
    debug: bool = False  # 默认关闭debug，减少日志噪音
    max_connections: int = 100
    connection_timeout: int = 30
    auth_required: bool = True
    
    # 扩展IPC配置
    socket_permissions: str = "0600"
    buffer_size: int = 8192
    enable_compression: bool = False


@dataclass
class UnifiedOllamaConfig:
    """统一Ollama AI配置 - 消除重复定义"""
    host: str = "http://localhost:11434"
    embedding_model: str = "nomic-embed-text:latest"
    llm_model: str = "qwen2.5:0.5b"
    value_threshold: float = 0.3
    entity_threshold: float = 0.8
    max_content_length: int = 10000
    request_timeout: int = 30
    connection_timeout: int = 5
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600


@dataclass
class UnifiedMonitoringConfig:
    """统一监控配置 - 修复重复调用问题"""
    health_check_interval: int = 60  # 从10秒改为60秒，减少噪音
    resource_monitor_interval: int = 30  # 资源监控间隔
    enable_debug_logging: bool = False  # 生产环境关闭debug日志
    log_service_calls: bool = False  # 关闭service调用日志


@dataclass
class UnifiedConfig:
    """统一配置根对象"""
    
    database: UnifiedDatabaseConfig = field(default_factory=UnifiedDatabaseConfig)
    ipc: UnifiedIPCConfig = field(default_factory=UnifiedIPCConfig)
    ollama: UnifiedOllamaConfig = field(default_factory=UnifiedOllamaConfig)
    monitoring: UnifiedMonitoringConfig = field(default_factory=UnifiedMonitoringConfig)
    
    # 元信息
    version: str = "1.0"
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class UnifiedConfigManager:
    """统一配置管理器 - KISS原则实现"""
    
    _instance: Optional['UnifiedConfigManager'] = None
    _config: Optional[UnifiedConfig] = None
    
    def __new__(cls) -> 'UnifiedConfigManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._load_config()
    
    def _load_config(self):
        """简化的配置加载逻辑"""
        try:
            # 从bootstrap获取基础配置
            bootstrap_config = get_bootstrap_config()
            
            # 创建统一配置
            self._config = UnifiedConfig()
            
            # 基础配置映射
            if hasattr(bootstrap_config, 'database'):
                self._config.database.sqlite_file = getattr(bootstrap_config.database, 'sqlite_file', self._config.database.sqlite_file)
            
            logger.info("统一配置加载成功")
            
        except Exception as e:
            logger.error(f"配置加载失败: {e}")
            self._config = UnifiedConfig()
    
    @property
    def config(self) -> UnifiedConfig:
        """获取当前配置"""
        return self._config
    
    def get_config_value(self, section: str, key: str, default: Any = None) -> Any:
        """获取配置值"""
        try:
            section_obj = getattr(self._config, section)
            return getattr(section_obj, key, default)
        except AttributeError:
            return default


# 全局配置管理器实例
_config_manager = None

def get_unified_config_manager() -> UnifiedConfigManager:
    """获取统一配置管理器单例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = UnifiedConfigManager()
    return _config_manager


def get_unified_config() -> UnifiedConfig:
    """获取统一配置对象"""
    return get_unified_config_manager().config


# 向后兼容接口
def get_config_value(section: str, key: str, default: Any = None) -> Any:
    """向后兼容：获取配置值"""
    return get_unified_config_manager().get_config_value(section, key, default)


# 向后兼容的配置类型别名
DatabaseConfig = UnifiedDatabaseConfig
IPCServerConfig = UnifiedIPCConfig
IPCConfig = UnifiedIPCConfig
OllamaConfig = UnifiedOllamaConfig