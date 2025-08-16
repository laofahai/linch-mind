#!/usr/bin/env python3
"""
用户友好的配置文件管理器
统一配置文件格式，消除环境变量依赖

核心设计原则:
1. 用户友好的配置文件格式（支持 TOML/YAML/JSON）
2. 环境特定配置覆盖机制
3. 配置验证和默认值管理
4. 配置模板生成和管理
5. 零环境变量依赖，纯配置文件驱动
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import yaml

from core.environment_manager import get_environment_manager, Environment
from core.error_handling import handle_errors, ErrorSeverity, ErrorCategory

logger = logging.getLogger(__name__)


@dataclass
class UserDatabaseConfig:
    """用户数据库配置"""
    type: str = "sqlite"  # sqlite, postgresql, mysql
    host: str = "localhost"
    port: int = 5432
    database: str = "linch_mind"
    username: str = ""
    password: str = ""
    # SQLite特定配置
    sqlite_file: str = "linch_mind.db"
    use_encryption: bool = True  # 生产环境默认加密
    # 连接池配置
    max_connections: int = 20
    connection_timeout: int = 30


@dataclass
class UserOllamaConfig:
    """Ollama AI服务配置"""
    host: str = "http://localhost:11434"
    # 模型配置
    embedding_model: str = "nomic-embed-text:latest"
    llm_model: str = "qwen2.5:0.5b"
    # AI阈值配置
    value_threshold: float = 0.3
    entity_threshold: float = 0.8
    # 性能配置
    max_content_length: int = 10000
    request_timeout: int = 30
    connection_timeout: int = 5
    # 缓存配置
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600


@dataclass
class UserVectorConfig:
    """向量数据库配置"""
    # 向量存储类型
    provider: str = "faiss"  # faiss, chroma, pinecone
    # FAISS配置
    vector_dimension: int = 384
    compressed_dimension: int = 256
    shard_size_limit: int = 100000
    compression_method: str = "PQ"  # PQ, SQ, HNSW
    index_type: str = "HNSW"  # HNSW, IVF, Flat
    # 性能配置
    max_memory_mb: int = 1024
    preload_hot_shards: bool = True
    # 搜索配置
    max_search_results: int = 10
    search_timeout: int = 5


@dataclass
class UserIPCConfig:
    """IPC通信配置"""
    # Unix Socket配置 (Linux/macOS)
    socket_path: str = ""  # 空字符串表示自动生成
    socket_permissions: str = "0600"
    # Named Pipe配置 (Windows)
    pipe_name: str = ""  # 空字符串表示自动生成
    # 连接配置
    max_connections: int = 100
    connection_timeout: int = 30
    auth_required: bool = True
    # 性能配置
    buffer_size: int = 8192
    enable_compression: bool = False


@dataclass
class UserConnectorConfig:
    """连接器配置"""
    # 连接器目录
    config_directory: str = "connectors"
    binary_directory: str = "connectors/bin"
    # 启用的连接器
    enabled_connectors: Dict[str, bool] = field(default_factory=dict)
    # 连接器设置
    auto_start: bool = True
    restart_on_failure: bool = True
    max_restart_attempts: int = 3
    restart_delay_seconds: int = 5
    # 监控配置
    health_check_interval: int = 30
    log_level: str = "info"


@dataclass
class UserSecurityConfig:
    """安全配置"""
    # 数据加密
    encrypt_database: bool = True
    encrypt_vectors: bool = False  # 性能考虑，默认关闭
    encrypt_logs: bool = False
    # 访问控制
    enable_access_control: bool = True
    allowed_processes: List[str] = field(default_factory=list)
    # 审计日志
    enable_audit_logging: bool = True
    audit_log_retention_days: int = 90
    # API安全
    require_authentication: bool = True
    session_timeout_minutes: int = 60


@dataclass
class UserPerformanceConfig:
    """性能配置"""
    # 缓存配置
    enable_caching: bool = True
    cache_size_mb: int = 512
    cache_ttl_seconds: int = 3600
    # 并发配置
    max_workers: int = 4
    max_concurrent_requests: int = 100
    # 资源限制
    max_memory_gb: float = 2.0
    max_storage_gb: float = 10.0
    # 清理配置
    auto_cleanup: bool = True
    cleanup_interval_hours: int = 24


@dataclass
class UserLoggingConfig:
    """日志配置"""
    # 日志级别
    level: str = "info"  # debug, info, warning, error, critical
    # 日志格式
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    # 日志输出
    enable_console: bool = True
    enable_file: bool = True
    # 文件配置
    log_file: str = "linch-mind.log"
    max_file_size_mb: int = 10
    backup_count: int = 5
    # 组件日志级别
    component_levels: Dict[str, str] = field(default_factory=dict)


@dataclass
class UserConfig:
    """完整的用户配置"""
    # 应用信息
    app_name: str = "Linch Mind"
    version: str = "0.1.0"
    debug: bool = False
    
    # 子配置模块
    database: UserDatabaseConfig = field(default_factory=UserDatabaseConfig)
    ollama: UserOllamaConfig = field(default_factory=UserOllamaConfig)
    vector: UserVectorConfig = field(default_factory=UserVectorConfig)
    ipc: UserIPCConfig = field(default_factory=UserIPCConfig)
    connectors: UserConnectorConfig = field(default_factory=UserConnectorConfig)
    security: UserSecurityConfig = field(default_factory=UserSecurityConfig)
    performance: UserPerformanceConfig = field(default_factory=UserPerformanceConfig)
    logging: UserLoggingConfig = field(default_factory=UserLoggingConfig)


class UserConfigManager:
    """用户友好的配置文件管理器
    
    特性:
    - 支持多种配置文件格式 (TOML, YAML, JSON)
    - 环境特定配置覆盖
    - 配置验证和默认值
    - 配置模板生成
    - 零环境变量依赖
    """
    
    def __init__(self):
        """初始化配置管理器"""
        self.env_manager = get_environment_manager()
        self.config_dir = self.env_manager.get_config_directory()
        
        # 配置文件路径（按优先级排序）
        self.config_files = {
            'toml': self.config_dir / "linch-mind.toml",
            'yaml': self.config_dir / "linch-mind.yaml", 
            'json': self.config_dir / "linch-mind.json"
        }
        
        # 环境特定配置文件
        env_name = self.env_manager.current_environment.value
        self.env_config_files = {
            'toml': self.config_dir / f"linch-mind.{env_name}.toml",
            'yaml': self.config_dir / f"linch-mind.{env_name}.yaml",
            'json': self.config_dir / f"linch-mind.{env_name}.json"
        }
        
        # 缓存的配置
        self._cached_config: Optional[UserConfig] = None
        
        logger.info(f"UserConfigManager initialized for environment: {env_name}")
    
    def get_config(self, force_reload: bool = False) -> UserConfig:
        """获取配置（支持缓存）
        
        Args:
            force_reload: 是否强制重新加载
            
        Returns:
            完整的用户配置对象
        """
        if self._cached_config is None or force_reload:
            self._cached_config = self._load_config()
        
        return self._cached_config
    
    def _load_config(self) -> UserConfig:
        """加载配置文件"""
        # 1. 加载基础配置
        base_config = self._load_base_config()
        
        # 2. 加载环境特定配置
        env_overrides = self._load_environment_config()
        
        # 3. 合并配置
        merged_config = self._merge_configs(base_config, env_overrides)
        
        # 4. 应用环境默认值
        self._apply_environment_defaults(merged_config)
        
        # 5. 验证配置
        self._validate_config(merged_config)
        
        logger.info("Configuration loaded successfully")
        return merged_config
    
    def _load_base_config(self) -> UserConfig:
        """加载基础配置文件"""
        # 按优先级尝试加载配置文件
        for format_name, config_path in self.config_files.items():
            if config_path.exists():
                try:
                    return self._load_config_file(config_path, format_name)
                except Exception as e:
                    logger.warning(f"Failed to load {format_name} config: {e}")
                    continue
        
        # 没有找到配置文件，创建默认配置
        logger.info("No configuration file found, creating default configuration")
        default_config = UserConfig()
        self._create_default_config_file(default_config)
        return default_config
    
    def _load_environment_config(self) -> Dict[str, Any]:
        """加载环境特定配置"""
        env_overrides = {}
        
        # 按优先级尝试加载环境配置文件
        for format_name, config_path in self.env_config_files.items():
            if config_path.exists():
                try:
                    env_config = self._load_config_file(config_path, format_name)
                    env_overrides = asdict(env_config)
                    logger.info(f"Loaded environment config from {config_path}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to load environment {format_name} config: {e}")
                    continue
        
        return env_overrides
    
    def _load_config_file(self, config_path: Path, format_name: str) -> UserConfig:
        """加载指定格式的配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if format_name == 'toml':
                    try:
                        import tomli
                    except ImportError:
                        import tomllib as tomli
                    # TOML需要二进制模式
                    with open(config_path, 'rb') as bf:
                        config_data = tomli.load(bf)
                elif format_name == 'yaml':
                    config_data = yaml.safe_load(f)
                elif format_name == 'json':
                    config_data = json.load(f)
                else:
                    raise ValueError(f"Unsupported config format: {format_name}")
            
            return self._dict_to_config(config_data or {})
            
        except Exception as e:
            logger.error(f"Failed to load config file {config_path}: {e}")
            raise
    
    def _dict_to_config(self, data: Dict[str, Any]) -> UserConfig:
        """将字典转换为配置对象"""
        try:
            # 提取各个配置段
            database_data = data.get('database', {})
            ollama_data = data.get('ollama', {})
            vector_data = data.get('vector', {})
            ipc_data = data.get('ipc', {})
            connectors_data = data.get('connectors', {})
            security_data = data.get('security', {})
            performance_data = data.get('performance', {})
            logging_data = data.get('logging', {})
            
            return UserConfig(
                app_name=data.get('app_name', 'Linch Mind'),
                version=data.get('version', '0.1.0'),
                debug=bool(data.get('debug', False)),
                database=UserDatabaseConfig(**database_data),
                ollama=UserOllamaConfig(**ollama_data),
                vector=UserVectorConfig(**vector_data),
                ipc=UserIPCConfig(**ipc_data),
                connectors=UserConnectorConfig(**connectors_data),
                security=UserSecurityConfig(**security_data),
                performance=UserPerformanceConfig(**performance_data),
                logging=UserLoggingConfig(**logging_data)
            )
        except Exception as e:
            logger.warning(f"Failed to parse config data: {e}, using defaults")
            return UserConfig()
    
    def _merge_configs(self, base_config: UserConfig, env_overrides: Dict[str, Any]) -> UserConfig:
        """合并基础配置和环境覆盖配置"""
        if not env_overrides:
            return base_config
        
        # 将基础配置转换为字典
        config_dict = asdict(base_config)
        
        # 深度合并环境覆盖
        self._deep_merge_dict(config_dict, env_overrides)
        
        # 转换回配置对象
        return self._dict_to_config(config_dict)
    
    def _deep_merge_dict(self, target: Dict[str, Any], source: Dict[str, Any]):
        """深度合并字典"""
        for key, value in source.items():
            if key in target:
                if isinstance(target[key], dict) and isinstance(value, dict):
                    self._deep_merge_dict(target[key], value)
                else:
                    target[key] = value
            else:
                target[key] = value
    
    def _apply_environment_defaults(self, config: UserConfig):
        """应用环境特定的默认值"""
        env = self.env_manager.current_environment
        
        if env == Environment.DEVELOPMENT:
            # 开发环境默认值
            config.debug = True
            config.database.use_encryption = False
            config.security.encrypt_database = False
            config.security.enable_audit_logging = False
            config.logging.level = "debug"
            config.performance.auto_cleanup = False
            
        elif env == Environment.STAGING:
            # 测试环境默认值
            config.debug = True
            config.database.use_encryption = True
            config.security.encrypt_database = True
            config.security.enable_audit_logging = True
            config.logging.level = "info"
            config.performance.auto_cleanup = True
            
        elif env == Environment.PRODUCTION:
            # 生产环境默认值
            config.debug = False
            config.database.use_encryption = True
            config.security.encrypt_database = True
            config.security.enable_audit_logging = True
            config.logging.level = "warning"
            config.performance.auto_cleanup = True
            
        logger.debug(f"Applied environment defaults for {env.value}")
    
    def _validate_config(self, config: UserConfig) -> List[str]:
        """验证配置完整性"""
        errors = []
        
        # 验证基础配置
        if not config.app_name.strip():
            errors.append("app_name cannot be empty")
        
        # 验证数据库配置
        if config.database.type not in ['sqlite', 'postgresql', 'mysql']:
            errors.append(f"Invalid database type: {config.database.type}")
        
        if config.database.type == 'sqlite' and not config.database.sqlite_file:
            errors.append("sqlite_file is required for SQLite database")
        
        # 验证Ollama配置
        if not config.ollama.host:
            errors.append("ollama.host cannot be empty")
        
        if not (0 <= config.ollama.value_threshold <= 1):
            errors.append("ollama.value_threshold must be between 0 and 1")
        
        # 验证向量配置
        if config.vector.vector_dimension <= 0:
            errors.append("vector.vector_dimension must be positive")
        
        # 验证性能配置
        if config.performance.max_memory_gb <= 0:
            errors.append("performance.max_memory_gb must be positive")
        
        if config.performance.max_storage_gb <= 0:
            errors.append("performance.max_storage_gb must be positive")
        
        # 验证日志配置
        valid_log_levels = ['debug', 'info', 'warning', 'error', 'critical']
        if config.logging.level not in valid_log_levels:
            errors.append(f"logging.level must be one of {valid_log_levels}")
        
        if errors:
            logger.warning(f"Configuration validation found {len(errors)} issues")
            for error in errors:
                logger.warning(f"Config validation: {error}")
        
        return errors
    
    def _create_default_config_file(self, config: UserConfig):
        """创建默认配置文件"""
        try:
            # 优先创建TOML格式
            config_path = self.config_files['toml']
            self._save_config_file(config, config_path, 'toml')
            logger.info(f"Created default configuration file: {config_path}")
        except Exception as e:
            logger.error(f"Failed to create default config file: {e}")
    
    def save_config(self, config: UserConfig, format_name: str = 'toml'):
        """保存配置到文件
        
        Args:
            config: 配置对象
            format_name: 文件格式 (toml, yaml, json)
        """
        if format_name not in self.config_files:
            raise ValueError(f"Unsupported format: {format_name}")
        
        config_path = self.config_files[format_name]
        self._save_config_file(config, config_path, format_name)
        
        # 更新缓存
        self._cached_config = config
        
        logger.info(f"Configuration saved to {config_path}")
    
    def _save_config_file(self, config: UserConfig, config_path: Path, format_name: str):
        """保存配置到指定文件"""
        # 确保配置目录存在
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 转换为字典并清理None值
        config_dict = asdict(config)
        config_dict = self._clean_config_dict(config_dict)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                if format_name == 'toml':
                    try:
                        import tomli_w
                        # TOML需要二进制模式写入
                        with open(config_path, 'wb') as bf:
                            tomli_w.dump(config_dict, bf)
                    except ImportError:
                        logger.warning("tomli_w not available, falling back to YAML")
                        format_name = 'yaml'
                
                if format_name == 'yaml':
                    # 添加文档头部
                    f.write(f"# Linch Mind Configuration\n")
                    f.write(f"# Environment: {self.env_manager.current_environment.value}\n")
                    f.write(f"# Generated automatically\n\n")
                    yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True, indent=2)
                
                elif format_name == 'json':
                    json.dump(config_dict, f, ensure_ascii=False, indent=2)
                    
        except Exception as e:
            logger.error(f"Failed to save config file {config_path}: {e}")
            raise
    
    def _clean_config_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清理配置字典，移除None值和空字典"""
        cleaned = {}
        for key, value in data.items():
            if value is not None:
                if isinstance(value, dict):
                    cleaned_value = self._clean_config_dict(value)
                    if cleaned_value:  # 只保留非空字典
                        cleaned[key] = cleaned_value
                elif isinstance(value, list):
                    cleaned[key] = [item for item in value if item is not None]
                else:
                    cleaned[key] = value
        return cleaned
    
    def create_template(self, format_name: str = 'toml', include_comments: bool = True) -> str:
        """创建配置模板
        
        Args:
            format_name: 模板格式 (toml, yaml, json)
            include_comments: 是否包含注释
            
        Returns:
            配置模板字符串
        """
        template_config = UserConfig()
        config_dict = asdict(template_config)
        
        if format_name == 'toml':
            return self._create_toml_template(config_dict, include_comments)
        elif format_name == 'yaml':
            return self._create_yaml_template(config_dict, include_comments)
        elif format_name == 'json':
            return json.dumps(config_dict, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format_name}")
    
    def _create_toml_template(self, config_dict: Dict[str, Any], include_comments: bool) -> str:
        """创建TOML模板"""
        lines = []
        
        if include_comments:
            lines.extend([
                "# Linch Mind Configuration File",
                f"# Environment: {self.env_manager.current_environment.value}",
                "# This file contains user-friendly configuration settings",
                "# Modify values as needed for your setup",
                "",
            ])
        
        # 基础应用配置
        lines.extend([
            f"app_name = \"{config_dict['app_name']}\"",
            f"version = \"{config_dict['version']}\"",
            f"debug = {str(config_dict['debug']).lower()}",
            "",
        ])
        
        # 各个配置段
        sections = [
            ('database', '数据库配置'),
            ('ollama', 'Ollama AI服务配置'),
            ('vector', '向量数据库配置'),
            ('ipc', 'IPC通信配置'),
            ('connectors', '连接器配置'),
            ('security', '安全配置'),
            ('performance', '性能配置'),
            ('logging', '日志配置'),
        ]
        
        for section_name, section_desc in sections:
            if include_comments:
                lines.append(f"# {section_desc}")
            lines.append(f"[{section_name}]")
            
            section_data = config_dict[section_name]
            for key, value in section_data.items():
                if isinstance(value, str):
                    lines.append(f"{key} = \"{value}\"")
                elif isinstance(value, bool):
                    lines.append(f"{key} = {str(value).lower()}")
                elif isinstance(value, list):
                    if value:  # 只显示非空列表
                        lines.append(f"{key} = {value}")
                elif isinstance(value, dict):
                    if value:  # 只显示非空字典
                        lines.append(f"{key} = {value}")
                else:
                    lines.append(f"{key} = {value}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _create_yaml_template(self, config_dict: Dict[str, Any], include_comments: bool) -> str:
        """创建YAML模板"""
        lines = []
        
        if include_comments:
            lines.extend([
                "# Linch Mind Configuration File",
                f"# Environment: {self.env_manager.current_environment.value}",
                "# This file contains user-friendly configuration settings",
                "# Modify values as needed for your setup",
                "",
            ])
        
        yaml_content = yaml.dump(config_dict, default_flow_style=False, allow_unicode=True, indent=2)
        lines.append(yaml_content)
        
        return "\n".join(lines)
    
    def export_template(self, output_path: Path, format_name: str = 'toml', include_comments: bool = True):
        """导出配置模板到文件
        
        Args:
            output_path: 输出文件路径
            format_name: 模板格式
            include_comments: 是否包含注释
        """
        template_content = self.create_template(format_name, include_comments)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        logger.info(f"Configuration template exported to: {output_path}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要信息"""
        config = self.get_config()
        
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
            "config_files": {
                name: str(path) for name, path in self.config_files.items()
                if path.exists()
            }
        }


# 全局单例
_user_config_manager: Optional[UserConfigManager] = None


def get_user_config_manager() -> UserConfigManager:
    """获取用户配置管理器单例"""
    global _user_config_manager
    if _user_config_manager is None:
        _user_config_manager = UserConfigManager()
    return _user_config_manager


def get_user_config() -> UserConfig:
    """获取用户配置"""
    return get_user_config_manager().get_config()


# 便捷访问函数
def get_user_database_config() -> UserDatabaseConfig:
    """获取用户数据库配置"""
    return get_user_config().database


def get_user_ollama_config() -> UserOllamaConfig:
    """获取用户Ollama配置"""
    return get_user_config().ollama


def get_user_vector_config() -> UserVectorConfig:
    """获取用户向量配置"""
    return get_user_config().vector


def get_user_ipc_config() -> UserIPCConfig:
    """获取用户IPC配置"""
    return get_user_config().ipc


def get_user_security_config() -> UserSecurityConfig:
    """获取用户安全配置"""
    return get_user_config().security