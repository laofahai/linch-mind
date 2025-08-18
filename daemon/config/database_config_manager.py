#!/usr/bin/env python3
"""
数据库配置管理器 - 替代原有的文件配置系统
完全基于数据库的统一配置管理，提供与原有UserConfig兼容的接口

核心特性:
- 完全替代配置文件（除构建相关配置外）
- 保持与原有UserConfig接口的兼容性
- 支持环境隔离和实时配置更新
- 配置缓存和懒加载
- 配置变更通知和历史记录
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone

from core.environment_manager import get_environment_manager
from core.service_facade import get_database_service
from models.database_models import SystemConfigEntry, SystemConfigHistory

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """数据库配置数据类"""
    type: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    database: str = "linch_mind"
    username: str = ""
    password: str = ""
    sqlite_file: str = "linch_mind.db"
    use_encryption: bool = True
    max_connections: int = 20
    connection_timeout: int = 30


@dataclass
class OllamaConfig:
    """Ollama AI配置数据类"""
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
class VectorConfig:
    """向量存储配置数据类"""
    provider: str = "faiss"
    vector_dimension: int = 384
    compressed_dimension: int = 256
    shard_size_limit: int = 100000
    compression_method: str = "PQ"
    index_type: str = "HNSW"
    max_memory_mb: int = 1024
    preload_hot_shards: bool = True
    max_search_results: int = 10
    search_timeout: int = 5


@dataclass
class IPCConfig:
    """IPC通信配置数据类"""
    socket_path: str = ""
    socket_permissions: str = "0600"
    pipe_name: str = ""
    max_connections: int = 100
    connection_timeout: int = 30
    auth_required: bool = True
    buffer_size: int = 8192
    enable_compression: bool = False


@dataclass
class SecurityConfig:
    """安全配置数据类"""
    encrypt_database: bool = True
    encrypt_vectors: bool = False
    encrypt_logs: bool = False
    enable_access_control: bool = True
    allowed_processes: List[str] = field(default_factory=list)
    enable_audit_logging: bool = True
    audit_log_retention_days: int = 90
    require_authentication: bool = True
    session_timeout_minutes: int = 60


@dataclass
class PerformanceConfig:
    """性能配置数据类"""
    enable_caching: bool = True
    cache_size_mb: int = 512
    cache_ttl_seconds: int = 3600
    max_workers: int = 4
    max_concurrent_requests: int = 100
    max_memory_gb: float = 2.0
    max_storage_gb: float = 10.0
    auto_cleanup: bool = True
    cleanup_interval_hours: int = 24


@dataclass
class LoggingConfig:
    """日志配置数据类"""
    level: str = "info"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_console: bool = True
    enable_file: bool = True
    log_file: str = "linch-mind.log"
    max_file_size_mb: int = 10
    backup_count: int = 5
    component_levels: Dict[str, str] = field(default_factory=dict)


@dataclass
class ConnectorConfig:
    """连接器配置数据类"""
    config_directory: str = "connectors"
    binary_directory: str = "connectors/bin"
    enabled_connectors: Dict[str, bool] = field(default_factory=dict)
    auto_start: bool = True
    restart_on_failure: bool = True
    max_restart_attempts: int = 3
    restart_delay_seconds: int = 5
    health_check_interval: int = 30
    log_level: str = "info"


@dataclass
class UIConfig:
    """用户界面配置数据类"""
    theme: str = "auto"
    language: str = "zh-CN"
    layout_density: str = "comfortable"
    enable_animations: bool = True
    sidebar_collapsed: bool = False
    show_advanced_options: bool = False
    max_recent_items: int = 10
    auto_save_interval: int = 30


@dataclass
class RecommendationConfig:
    """推荐配置数据类"""
    enable_smart_suggestions: bool = True
    suggestion_threshold: float = 0.7
    max_suggestions: int = 5
    learning_rate: float = 0.1
    enable_context_awareness: bool = True
    update_frequency_hours: int = 24


@dataclass
class SearchConfig:
    """搜索配置数据类"""
    enable_fuzzy_search: bool = True
    fuzzy_threshold: float = 0.8
    max_search_history: int = 100
    enable_search_suggestions: bool = True
    search_result_grouping: str = "category"
    index_update_interval: int = 300


@dataclass
class UnifiedConfig:
    """统一配置对象 - 替代原有的UserConfig"""
    # 应用基础信息
    app_name: str = "Linch Mind"
    version: str = "0.1.0"
    debug: bool = False
    
    # 各个配置段
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    vector: VectorConfig = field(default_factory=VectorConfig)
    ipc: IPCConfig = field(default_factory=IPCConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    connectors: ConnectorConfig = field(default_factory=ConnectorConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    recommendation: RecommendationConfig = field(default_factory=RecommendationConfig)
    search: SearchConfig = field(default_factory=SearchConfig)


class DatabaseConfigManager:
    """数据库配置管理器
    
    完全基于数据库的配置管理，替代原有的文件配置系统
    提供与原有UserConfigManager兼容的接口
    """

    def __init__(self):
        self.env_manager = get_environment_manager()
        self._db_service = None  # 延迟初始化数据库服务
        self._cached_config: Optional[UnifiedConfig] = None
        self._config_sections = [
            "app", "database", "ollama", "vector", "ipc", 
            "security", "performance", "logging", "connectors",
            "ui", "recommendation", "search"
        ]
        
        logger.info(f"DatabaseConfigManager initialized for environment: {self.env_manager.current_environment.value}")

    @property
    def db_service(self):
        """延迟获取数据库服务，避免循环依赖"""
        if self._db_service is None:
            try:
                # 直接从DI容器获取，避免ServiceFacade循环依赖
                from core.container import get_container
                from services.unified_database_service import UnifiedDatabaseService
                container = get_container()
                self._db_service = container.get_service(UnifiedDatabaseService)
            except Exception as e:
                logger.warning(f"数据库服务暂不可用: {e}")
                return None
        return self._db_service

    def get_config_value(self, section: str, key: str, default: Any = None) -> Any:
        """同步获取配置值（用于兼容现有代码）
        
        Args:
            section: 配置段
            key: 配置键  
            default: 默认值
            
        Returns:
            配置值
        """
        try:
            with self.db_service.get_session() as session:
                entry = session.query(SystemConfigEntry).filter_by(
                    scope="user",
                    config_section=section,
                    config_key=key
                ).first()
                
                if entry:
                    return entry.config_value
                else:
                    return default
                    
        except Exception as e:
            logger.error(f"同步获取配置失败 {section}.{key}: {e}")
            return default

    async def set_config_value(self, section: str, key: str, value: Any, scope: str = "user") -> bool:
        """异步设置配置值
        
        Args:
            section: 配置段
            key: 配置键
            value: 配置值
            scope: 作用域
            
        Returns:
            是否设置成功
        """
        return await self._set_config(section, key, value, scope, "config_manager")

    async def _get_section_configs(self, section: str, include_sensitive: bool = False) -> Dict[str, Any]:
        """获取配置段的所有配置"""
        try:
            with self.db_service.get_session() as session:
                query = session.query(SystemConfigEntry).filter_by(
                    scope="user", 
                    config_section=section
                )
                
                if not include_sensitive:
                    query = query.filter_by(is_sensitive=False)
                    
                entries = query.all()
                
                result = {}
                for entry in entries:
                    result[entry.config_key] = entry.config_value
                    
                return result
                
        except Exception as e:
            logger.error(f"获取配置段失败 {section}: {e}")
            return {}

    async def _get_config(self, section: str, key: str, scope: str = "user", default: Any = None) -> Any:
        """异步获取单个配置值"""
        try:
            with self.db_service.get_session() as session:
                entry = session.query(SystemConfigEntry).filter_by(
                    scope=scope,
                    config_section=section,
                    config_key=key
                ).first()
                
                if entry:
                    return entry.config_value
                else:
                    return default
                    
        except Exception as e:
            logger.error(f"异步获取配置失败 {section}.{key}: {e}")
            return default

    async def _set_config(self, section: str, key: str, value: Any, scope: str = "user", changed_by: str = "system") -> bool:
        """异步设置配置值"""
        try:
            with self.db_service.get_session() as session:
                # 查找现有配置
                entry = session.query(SystemConfigEntry).filter_by(
                    scope=scope,
                    config_section=section,
                    config_key=key
                ).first()
                
                if entry:
                    # 更新现有配置
                    old_value = entry.config_value
                    entry.config_value = value
                    entry.updated_at = datetime.now(timezone.utc)
                    entry.last_modified_by = changed_by
                else:
                    # 创建新配置
                    entry = SystemConfigEntry(
                        scope=scope,
                        config_section=section,
                        config_key=key,
                        config_value=value,
                        config_type="user_preference",
                        value_type=self._get_value_type(value),
                        last_modified_by=changed_by
                    )
                    session.add(entry)
                    old_value = None
                    
                    # 先提交获取ID
                    session.flush()
                
                # 记录配置变更历史
                change_type = "update" if old_value is not None else "create"
                history = SystemConfigHistory(
                    config_entry_id=entry.id,
                    scope=scope,
                    config_section=section,
                    config_key=key,
                    old_value=old_value,
                    new_value=value,
                    change_type=change_type,
                    changed_by=changed_by,
                    change_reason="config_update"
                )
                session.add(history)
                
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"设置配置失败 {section}.{key}: {e}")
            return False

    async def _initialize_all_configs(self) -> bool:
        """初始化所有默认配置"""
        try:
            # 创建默认配置对象
            default_config = UnifiedConfig()
            
            # 初始化各个配置段
            config_sections = {
                "app": {
                    "name": default_config.app_name,
                    "version": default_config.version,
                    "debug": default_config.debug
                },
                "database": {
                    "type": default_config.database.type,
                    "host": default_config.database.host,
                    "port": default_config.database.port,
                    "database": default_config.database.database,
                    "username": default_config.database.username,
                    "password": default_config.database.password,
                    "sqlite_file": default_config.database.sqlite_file,
                    "use_encryption": default_config.database.use_encryption,
                    "max_connections": default_config.database.max_connections,
                    "connection_timeout": default_config.database.connection_timeout
                },
                "ollama": {
                    "host": default_config.ollama.host,
                    "embedding_model": default_config.ollama.embedding_model,
                    "llm_model": default_config.ollama.llm_model,
                    "value_threshold": default_config.ollama.value_threshold,
                    "entity_threshold": default_config.ollama.entity_threshold,
                    "max_content_length": default_config.ollama.max_content_length,
                    "request_timeout": default_config.ollama.request_timeout,
                    "connection_timeout": default_config.ollama.connection_timeout,
                    "enable_cache": default_config.ollama.enable_cache,
                    "cache_ttl_seconds": default_config.ollama.cache_ttl_seconds
                },
                "vector": {
                    "provider": default_config.vector.provider,
                    "vector_dimension": default_config.vector.vector_dimension,
                    "compressed_dimension": default_config.vector.compressed_dimension,
                    "shard_size_limit": default_config.vector.shard_size_limit,
                    "compression_method": default_config.vector.compression_method,
                    "index_type": default_config.vector.index_type,
                    "max_memory_mb": default_config.vector.max_memory_mb,
                    "preload_hot_shards": default_config.vector.preload_hot_shards,
                    "max_search_results": default_config.vector.max_search_results,
                    "search_timeout": default_config.vector.search_timeout
                },
                "ipc": {
                    "socket_path": default_config.ipc.socket_path,
                    "socket_permissions": default_config.ipc.socket_permissions,
                    "pipe_name": default_config.ipc.pipe_name,
                    "max_connections": default_config.ipc.max_connections,
                    "connection_timeout": default_config.ipc.connection_timeout,
                    "auth_required": default_config.ipc.auth_required,
                    "buffer_size": default_config.ipc.buffer_size,
                    "enable_compression": default_config.ipc.enable_compression
                }
            }
            
            # 将配置写入数据库
            for section_name, section_config in config_sections.items():
                for key, value in section_config.items():
                    await self._set_config(section_name, key, value, "system", "default_initialization")
            
            logger.info("默认配置初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"初始化默认配置失败: {e}")
            return False

    def _get_value_type(self, value: Any) -> str:
        """获取值的类型字符串"""
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "number"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, (list, tuple)):
            return "array"
        elif isinstance(value, dict):
            return "object"
        else:
            return "string"

    async def get_config(self, force_reload: bool = False) -> UnifiedConfig:
        """获取完整配置（支持缓存）
        
        Args:
            force_reload: 是否强制重新加载
            
        Returns:
            完整的统一配置对象
        """
        if self._cached_config is None or force_reload:
            self._cached_config = await self._load_config_from_database()
        
        return self._cached_config

    async def _load_config_from_database(self) -> UnifiedConfig:
        """从数据库加载完整配置"""
        logger.debug("从数据库加载配置...")
        
        try:
            # 创建基础配置对象
            config = UnifiedConfig()
            
            # 从数据库加载各个配置段
            for section_name in self._config_sections:
                section_configs = await self._get_section_configs(
                    section=section_name,
                    include_sensitive=True  # 内部使用，包含敏感配置
                )
                
                if section_configs:
                    # 将配置应用到相应的配置对象
                    await self._apply_section_config(config, section_name, section_configs)
            
            logger.info("数据库配置加载完成")
            return config
            
        except Exception as e:
            logger.error(f"从数据库加载配置失败: {e}")
            # 返回默认配置作为降级
            return UnifiedConfig()

    async def _apply_section_config(self, config: UnifiedConfig, section_name: str, section_configs: Dict[str, Any]):
        """将配置段数据应用到配置对象"""
        try:
            if section_name == "app":
                # 应用基础应用配置
                config.app_name = section_configs.get("name", config.app_name)
                config.version = section_configs.get("version", config.version)
                config.debug = section_configs.get("debug", config.debug)
            else:
                # 获取相应的配置段对象
                section_obj = getattr(config, section_name, None)
                if section_obj is None:
                    logger.warning(f"未知的配置段: {section_name}")
                    return
                
                # 将配置应用到段对象
                for key, value in section_configs.items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)
                        logger.debug(f"应用配置: {section_name}.{key} = {value}")
                    else:
                        logger.warning(f"未知的配置键: {section_name}.{key}")
                        
        except Exception as e:
            logger.error(f"应用配置段失败 {section_name}: {e}")

    async def set_config(
        self,
        section: str,
        key: str,
        value: Any,
        scope: str = "user"
    ) -> bool:
        """设置单个配置值
        
        Args:
            section: 配置段
            key: 配置键
            value: 配置值
            scope: 作用域
            
        Returns:
            是否设置成功
        """
        try:
            success = await self._set_config(
                section=section,
                key=key,
                value=value,
                scope=scope,
                changed_by="config_manager"
            )
            
            if success:
                # 清除缓存，强制重新加载
                self._cached_config = None
                logger.info(f"配置设置成功: {section}.{key}")
            
            return success
            
        except Exception as e:
            logger.error(f"设置配置失败 {section}.{key}: {e}")
            return False


    async def reset_section(self, section: str) -> bool:
        """重置配置段为默认值
        
        Args:
            section: 配置段名称
            
        Returns:
            是否重置成功
        """
        try:
            # 删除数据库中的配置段，这样会回退到默认值
            from models.database_models import SystemConfigEntry
            from core.service_facade import get_database_service
            
            db_service = get_database_service()
            environment = self.env_manager.current_environment.value
            
            with db_service.get_session() as session:
                config_entries = (
                    session.query(SystemConfigEntry)
                    .filter_by(
                        scope="user",
                        config_section=section
                    )
                    .all()
                )
                
                for entry in config_entries:
                    session.delete(entry)
                
                session.commit()
                
            # 清除缓存
            self._cached_config = None
            
            logger.info(f"配置段重置成功: {section}")
            return True
            
        except Exception as e:
            logger.error(f"重置配置段失败 {section}: {e}")
            return False

    async def initialize_default_configs(self) -> bool:
        """初始化默认配置到数据库
        
        Returns:
            是否初始化成功
        """
        try:
            success = await self._initialize_all_configs()
            
            if success:
                # 清除缓存，确保下次获取最新配置
                self._cached_config = None
                logger.info("默认配置初始化成功")
            
            return success
            
        except Exception as e:
            logger.error(f"初始化默认配置失败: {e}")
            return False

    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要信息"""
        try:
            # 这里使用同步方法，因为原有接口是同步的
            # 在实际使用中，调用者应该使用异步版本
            if self._cached_config:
                config = self._cached_config
            else:
                # 如果没有缓存，返回基本信息
                return {
                    "app_name": "Linch Mind",
                    "version": "0.1.0",
                    "environment": self.env_manager.current_environment.value,
                    "config_source": "database",
                    "status": "not_loaded"
                }
            
            return {
                "app_name": config.app_name,
                "version": config.version,
                "environment": self.env_manager.current_environment.value,
                "debug": config.debug,
                "database_type": config.database.type,
                "database_encryption": config.database.use_encryption,
                "ollama_host": config.ollama.host,
                "vector_provider": config.vector.provider,
                "ipc_auth_required": config.ipc.auth_required,
                "security_enabled": config.security.enable_access_control,
                "config_source": "database",
                "status": "loaded"
            }
            
        except Exception as e:
            logger.error(f"获取配置摘要失败: {e}")
            return {
                "config_source": "database",
                "status": "error",
                "error": str(e)
            }

    def clear_cache(self):
        """清除配置缓存"""
        self._cached_config = None
        logger.debug("配置缓存已清除")


# 全局单例
_database_config_manager: Optional[DatabaseConfigManager] = None


def get_database_config_manager() -> DatabaseConfigManager:
    """获取数据库配置管理器单例"""
    global _database_config_manager
    if _database_config_manager is None:
        _database_config_manager = DatabaseConfigManager()
    return _database_config_manager


# 向后兼容的别名
def get_unified_config_manager() -> DatabaseConfigManager:
    """获取统一配置管理器（向后兼容别名）"""
    return get_database_config_manager()


# 同步获取配置的便捷函数（用于兼容原有代码）
def get_unified_config() -> UnifiedConfig:
    """获取统一配置（同步版本，用于兼容）
    
    注意：这是一个同步函数，只返回缓存的配置
    如果需要最新配置，请使用 await get_database_config_manager().get_config()
    """
    manager = get_database_config_manager()
    if manager._cached_config is not None:
        return manager._cached_config
    else:
        # 返回默认配置作为降级
        logger.warning("配置未加载，返回默认配置")
        return UnifiedConfig()


# 兼容性别名
UserConfig = UnifiedConfig  # 向后兼容
get_user_config = get_unified_config  # 向后兼容