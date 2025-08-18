#!/usr/bin/env python3
"""
核心配置管理 - Session V61 简化重构
简化环境变量处理，移除复杂的正则表达式，专注稳定性
"""

import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import yaml

if TYPE_CHECKING:
    from .config_context import ConfigContext

from .error_handling import (
    ConfigFileError,
    ConfigValidationError,
    get_logger,
    safe_operation,
    validate_required_field,
)

logger = get_logger(__name__)


@dataclass
class IPCServerConfig:
    """IPC服务器配置 - 纯IPC架构，无端口概念"""

    socket_path: Optional[str] = None  # Unix Socket路径，None表示自动生成
    pipe_name: Optional[str] = None  # Windows Named Pipe名称，None表示自动生成
    reload: bool = True
    log_level: str = "info"
    debug: bool = True
    max_connections: int = 100  # 最大并发连接数
    connection_timeout: int = 30  # 连接超时时间（秒）
    auth_required: bool = True  # 是否要求认证


@dataclass
class DatabaseConfig:
    """数据库配置"""

    sqlite_url: str = ""
    chroma_persist_directory: str = ""
    embedding_model: str = "all-MiniLM-L6-v2"
    vector_dimension: int = 384


@dataclass
class StorageConfig:
    """三层存储架构配置"""

    # 数据目录
    data_directory: str = ""

    # 图数据库配置
    graph_enable_cache: bool = True
    graph_cache_ttl_seconds: int = 300
    graph_max_workers: int = 4

    # 向量数据库配置
    vector_dimension: int = 384
    vector_index_type: str = "IVF"  # Flat, IVF, HNSW
    vector_index_path: str = "vector_index.bin"
    distance_metric: str = "cosine"  # cosine, euclidean, inner_product
    vector_max_workers: int = 4

    # 嵌入服务配置
    embedding_model_name: str = "all-MiniLM-L6-v2"
    embedding_cache_enabled: bool = True
    embedding_max_workers: int = 2

    # 数据同步配置
    auto_sync_enabled: bool = True
    sync_interval_minutes: int = 10

    # 数据生命周期配置
    entity_retention_days: int = 90
    behavior_retention_days: int = 30
    conversation_retention_days: int = 60
    auto_cleanup_enabled: bool = True
    cleanup_interval_hours: int = 24

    # 性能配置
    max_storage_gb: float = 10.0
    cache_size_mb: int = 512


@dataclass
class ConnectorConfig:
    """连接器配置"""

    config_dir: str = "connectors"
    
    # 动态连接器启用状态配置 - 支持任意连接器ID
    # 默认为空字典，不硬编码任何连接器
    enabled_connectors: dict = field(default_factory=dict)
    
    def is_connector_enabled(self, connector_id: str) -> bool:
        """检查指定连接器是否启用"""
        if isinstance(self.enabled_connectors, dict) and connector_id in self.enabled_connectors:
            return self.enabled_connectors[connector_id]
        
        # 默认新连接器为禁用状态
        return False
    
    def enable_connector(self, connector_id: str) -> None:
        """启用指定连接器"""
        if not isinstance(self.enabled_connectors, dict):
            self.enabled_connectors = {}
        self.enabled_connectors[connector_id] = True
    
    def disable_connector(self, connector_id: str) -> None:
        """禁用指定连接器"""
        if not isinstance(self.enabled_connectors, dict):
            self.enabled_connectors = {}
        self.enabled_connectors[connector_id] = False


@dataclass
class ConnectorRegistryConfig:
    """连接器注册表配置"""

    url: str = (
        "https://github.com/laofahai/linch-mind/releases/latest/download/registry.json"
    )
    cache_duration_hours: int = 6
    auto_refresh: bool = True


@dataclass
class AIConfig:
    """AI配置"""

    default_embedding_model: str = "all-MiniLM-L6-v2"
    max_search_results: int = 10
    recommendation_threshold: float = 0.7
    providers: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AppConfig:
    """应用配置 - 核心配置入口"""

    app_name: str = "Linch Mind"
    version: str = "0.1.0"
    description: str = "Personal AI Life Assistant API"
    debug: bool = False

    # 子配置
    server: IPCServerConfig = field(default_factory=IPCServerConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    connectors: ConnectorConfig = field(default_factory=ConnectorConfig)
    connector_registry: ConnectorRegistryConfig = field(
        default_factory=ConnectorRegistryConfig
    )
    ai: AIConfig = field(default_factory=AIConfig)


class CoreConfigManager:
    """核心配置管理器

    Session V61 简化原则:
    1. 移除复杂的环境变量正则处理
    2. 使用标准的 os.getenv() 处理环境变量
    3. 单一配置文件路径策略
    4. 清晰的错误处理和日志记录
    """

    def __init__(
        self,
        config_context: Optional["ConfigContext"] = None,
        config_root: Optional[Path] = None,
    ):
        """
        初始化配置管理器 - 企业级最佳实践

        Args:
            config_context: 配置上下文接口（推荐使用）
            config_root: 配置根目录（向后兼容，将被弃用）
        """
        # 依赖倒置：接受配置上下文抽象
        if config_context is not None:
            self.context = config_context
        else:
            # 向后兼容和工厂模式
            from .config_context import create_config_context

            self.context = create_config_context(config_root)

        # 使用配置上下文获取路径信息 - 关注点分离
        self.config_dir = self.context.get_config_dir()
        self.data_dir = self.context.get_data_dir()
        self.logs_dir = self.context.get_logs_dir()
        self.db_dir = self.context.get_database_dir()

        # 配置文件路径 - 优先使用 TOML
        self.config_root = config_root or Path(__file__).parent.parent.parent
        self.primary_config_path = self.config_dir / "app.toml"
        self.primary_yaml_path = self.config_dir / "app.yaml"
        self.fallback_config_path = self.config_root / "linch-mind.config.toml"
        self.fallback_yaml_path = self.config_root / "linch-mind.config.yaml"

        # 加载配置
        self.config = self._load_config()
        self._setup_dynamic_paths()
        self._apply_env_overrides()

        logger.info(
            f"Core config loaded - Environment: {self.context.get_environment_name()}, Path: {self._get_active_config_path()}"
        )

    def _get_active_config_path(self) -> Path:
        """获取当前活跃的配置文件路径"""
        # 按优先级检查：TOML > YAML
        if self.primary_config_path.exists():
            return self.primary_config_path
        elif self.primary_yaml_path.exists():
            return self.primary_yaml_path
        elif self.fallback_config_path.exists():
            return self.fallback_config_path
        elif self.fallback_yaml_path.exists():
            return self.fallback_yaml_path
        else:
            return self.primary_config_path  # 将要创建的路径（TOML）

    def _load_config(self) -> AppConfig:
        """加载配置 - 支持 TOML 和 YAML"""

        # 1. 尝试从主配置路径加载（优先 TOML）
        if self.primary_config_path.exists():
            try:
                return self._load_from_file(self.primary_config_path)
            except Exception as e:
                logger.error(f"Failed to load primary TOML config: {e}")
        
        # 2. 尝试加载 YAML 配置
        if self.primary_yaml_path.exists():
            try:
                return self._load_from_file(self.primary_yaml_path)
            except Exception as e:
                logger.error(f"Failed to load primary YAML config: {e}")

        # 3. 尝试从项目根目录配置加载
        if self.fallback_config_path.exists():
            try:
                config = self._load_from_file(self.fallback_config_path)
                # 保存到主配置路径
                self._save_config(config, self.primary_config_path)
                logger.info("Migrated config from project root to user directory")
                return config
            except Exception as e:
                logger.error(f"Failed to load fallback TOML config: {e}")
        
        if self.fallback_yaml_path.exists():
            try:
                config = self._load_from_file(self.fallback_yaml_path)
                # 保存到主配置路径
                self._save_config(config, self.primary_config_path)
                logger.info("Migrated config from project root to user directory")
                return config
            except Exception as e:
                logger.error(f"Failed to load fallback YAML config: {e}")

        # 4. 创建默认配置
        config = AppConfig()
        self._save_config(config, self.primary_config_path)
        logger.info("Created default configuration")
        return config

    def _load_from_file(self, config_path: Path) -> AppConfig:
        """从配置文件加载（支持 TOML 和 YAML）"""

        def load_operation():
            try:
                if config_path.suffix == '.toml':
                    # 加载 TOML 文件
                    try:
                        import tomli
                    except ImportError:
                        logger.warning("tomli not installed, falling back to tomllib")
                        import tomllib as tomli
                    
                    with open(config_path, "rb") as f:
                        config_data = tomli.load(f)
                else:
                    # 加载 YAML 文件
                    with open(config_path, "r", encoding="utf-8") as f:
                        config_data = yaml.safe_load(f)

                if not config_data:
                    config_data = {}

                return self._dict_to_config(config_data)
            except FileNotFoundError:
                raise ConfigFileError(
                    file_path=str(config_path),
                    operation="read",
                    reason="File not found",
                )
            except (yaml.YAMLError if config_path.suffix != '.toml' else Exception) as e:
                raise ConfigFileError(
                    file_path=str(config_path),
                    operation="parse",
                    reason=f"Invalid {config_path.suffix[1:].upper()} syntax: {e}",
                )
            except PermissionError:
                raise ConfigFileError(
                    file_path=str(config_path),
                    operation="read",
                    reason="Permission denied",
                )

        return safe_operation(
            operation_name=f"load_config_from_{config_path.name}",
            operation_func=load_operation,
            logger=logger,
            error_type=ConfigFileError,
            reraise=True,
        )

    def _dict_to_config(self, data: Dict[str, Any]) -> AppConfig:
        """将字典转换为配置对象 - 增强错误处理"""
        try:
            # 处理嵌套配置，确保都是字典类型
            server_data = data.get("server", {})
            database_data = data.get("database", {})
            storage_data = data.get("storage", {})
            connectors_data = data.get("connectors", {})
            connector_registry_data = data.get("connector_registry", {})
            ai_data = data.get("ai", {})

            # 类型检查和修正
            if not isinstance(server_data, dict):
                server_data = {}
            if not isinstance(database_data, dict):
                database_data = {}
            if not isinstance(storage_data, dict):
                storage_data = {}
            if not isinstance(connectors_data, dict):
                connectors_data = {}
            if not isinstance(connector_registry_data, dict):
                connector_registry_data = {}
            if not isinstance(ai_data, dict):
                ai_data = {}

            return AppConfig(
                app_name=data.get("app_name", "Linch Mind"),
                version=data.get("version", "0.1.0"),
                description=data.get("description", "Personal AI Life Assistant API"),
                debug=bool(data.get("debug", False)),
                server=IPCServerConfig(**server_data),
                database=DatabaseConfig(**database_data),
                storage=StorageConfig(**storage_data),
                connectors=ConnectorConfig(**connectors_data),
                connector_registry=ConnectorRegistryConfig(**connector_registry_data),
                ai=AIConfig(**ai_data),
            )
        except Exception as e:
            logger.error(f"Failed to parse config dict: {e}")
            logger.warning("Using default configuration due to parsing error")
            return AppConfig()

    def _save_config(self, config: AppConfig, config_path: Path):
        """保存配置文件 - 支持 TOML 和 YAML"""
        config_dict = asdict(config)
        
        # 清理 None 值，TOML 不支持 None
        def clean_none_values(d):
            """递归清理字典中的 None 值"""
            if not isinstance(d, dict):
                return d
            cleaned = {}
            for k, v in d.items():
                if v is not None:
                    if isinstance(v, dict):
                        cleaned[k] = clean_none_values(v)
                    elif isinstance(v, list):
                        cleaned[k] = [clean_none_values(item) if isinstance(item, dict) else item for item in v]
                    else:
                        cleaned[k] = v
            return cleaned
        
        config_dict = clean_none_values(config_dict)

        try:
            # 确保配置目录存在
            config_path.parent.mkdir(parents=True, exist_ok=True)

            if config_path.suffix == '.toml':
                # 保存为 TOML 格式
                try:
                    import tomli_w
                except ImportError:
                    logger.warning("tomli_w not installed, falling back to YAML")
                    config_path = config_path.with_suffix('.yaml')
                else:
                    with open(config_path, "wb") as f:
                        tomli_w.dump(config_dict, f)
                    logger.info(f"TOML configuration saved to: {config_path}")
                    return
            
            # 保存为 YAML 格式（后备选项）
            yaml_content = f"""# Linch Mind Configuration
# Generated: {datetime.now(timezone.utc).isoformat()}

"""
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(yaml_content)
                yaml.dump(
                    config_dict,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    indent=2,
                )

            logger.info(f"YAML configuration saved to: {config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise

    def _setup_dynamic_paths(self):
        """设置动态路径配置 - 环境管理器集成版本"""
        # 🆕 使用环境管理器提供的路径配置
        import os

        # 检测是否为测试环境 (通过环境管理器已处理，这里保持兼容性)
        is_test_env = (
            os.getenv("PYTEST_CURRENT_TEST") is not None
            or os.getenv("TESTING") == "1"
            or "test" in sys.argv[0].lower()
            or any("test" in arg for arg in sys.argv)
        )

        # 使用配置上下文的数据库配置 - 最佳实践
        if is_test_env or self.context.is_test_environment():
            # 测试环境：只有当database.sqlite_url为空时才使用内存数据库
            if not self.config.database.sqlite_url:
                self.config.database.sqlite_url = "sqlite:///:memory:"
                logger.info("测试环境检测：使用内存数据库（默认）")
            if not self.config.database.chroma_persist_directory:
                self.config.database.chroma_persist_directory = ":memory:"
        else:
            # 使用配置上下文的数据库配置
            self.config.database.sqlite_url = self.context.get_database_url()
            self.config.database.chroma_persist_directory = (
                self.context.get_chroma_persist_directory()
            )

            logger.info("使用配置上下文的数据库配置")
            logger.info(f"  Database: {self.config.database.sqlite_url}")
            logger.info(f"  ChromaDB: {self.config.database.chroma_persist_directory}")

        # 设置存储目录路径 - 使用环境特定的数据目录
        if not self.config.storage.data_directory:
            self.config.storage.data_directory = str(self.data_dir)

        # 设置向量索引路径 - 环境隔离
        vector_index_path = self.context.get_vector_index_path()
        if hasattr(self.config.storage, "vector_index_path"):
            self.config.storage.vector_index_path = str(vector_index_path)

        # 设置连接器目录路径 - 使用项目目录 (连接器配置可以跨环境共享)
        if self.config.connectors.config_dir == "connectors":
            # 获取项目根目录（daemon目录的父目录）
            project_root = Path(__file__).parent.parent.parent
            project_connectors_dir = project_root / "connectors"
            if project_connectors_dir.exists():
                self.config.connectors.config_dir = str(project_connectors_dir)
                logger.debug(f"使用项目连接器目录: {project_connectors_dir}")
            else:
                # 如果项目connectors目录不存在，使用环境特定的connectors目录
                env_connectors_dir = self.context.get_connectors_dir()
                env_connectors_dir.mkdir(exist_ok=True)
                self.config.connectors.config_dir = str(env_connectors_dir)
                logger.debug(f"使用环境connectors目录: {env_connectors_dir}")

        # 环境特定的调试配置
        if self.context.is_debug_enabled():
            self.config.debug = True
            self.config.server.debug = True
            logger.debug(f"环境 {self.context.get_environment_name()} 启用调试模式")

    def _apply_env_overrides(self):
        """应用配置文件覆盖 - 用户配置优先"""
        # 尝试从数据库配置获取覆盖设置
        try:
            from .database_config_manager import get_database_config_manager
            config_manager = get_database_config_manager()
            
            # 检查数据库服务是否可用，如果不可用则跳过数据库配置覆盖
            if config_manager.db_service is None:
                logger.debug("数据库服务暂不可用，跳过数据库配置覆盖")
                return
            
            # 尝试获取关键配置项
            debug_config = config_manager.get_config_value('app', 'debug', None)
            if debug_config is not None:
                self.config.debug = debug_config
                self.config.server.debug = debug_config
                
            socket_path = config_manager.get_config_value('ipc', 'socket_path', None)
            if socket_path:
                self.config.server.socket_path = socket_path
                
            pipe_name = config_manager.get_config_value('ipc', 'pipe_name', None)
            if pipe_name:
                self.config.server.pipe_name = pipe_name
                
            max_connections = config_manager.get_config_value('ipc', 'max_connections', None)
            if max_connections:
                self.config.server.max_connections = max_connections
                
            auth_required = config_manager.get_config_value('ipc', 'auth_required', None)
            if auth_required is not None:
                self.config.server.auth_required = auth_required
                
            logger.debug("Applied database config overrides to core config")
            
        except Exception as e:
            logger.debug(f"No database config overrides available: {e}")
            
        # 仍然支持关键的环境变量作为后备（仅限测试和开发）
        import os
        critical_env_vars = {
            "LINCH_ENV": None,  # 环境变量由环境管理器处理
            "PYTEST_CURRENT_TEST": None,  # 测试环境检测
            "TESTING": None,  # 测试标志
        }
        
        # 只处理调试相关的环境变量作为后备
        if os.getenv("LINCH_DEBUG"):
            debug_value = os.getenv("LINCH_DEBUG").lower() in ("true", "1", "yes")
            self.config.debug = debug_value
            self.config.server.debug = debug_value
            logger.debug(f"Applied debug override from LINCH_DEBUG: {debug_value}")

    def save_config(self):
        """保存当前配置"""
        self._save_config(self.config, self.primary_config_path)

    def reload_config(self) -> bool:
        """重新加载配置"""
        try:
            old_config = self.config
            self.config = self._load_config()
            self._setup_dynamic_paths()
            self._apply_env_overrides()
            logger.info("Configuration reloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
            self.config = old_config  # 恢复旧配置
            return False

    def get_paths(self) -> Dict[str, Path]:
        """获取各种路径 - 使用配置上下文"""
        return {
            "config": self.config_dir,
            "data": self.data_dir,
            "app_data": self.data_dir,  # 向后兼容的别名
            "logs": self.logs_dir,
            "database": self.db_dir,
            "primary_config": self.primary_config_path,
            "fallback_config": self.fallback_config_path,
        }

    def get_server_info(self) -> Dict[str, Any]:
        """获取IPC服务器信息"""
        return {
            "app_name": self.config.app_name,
            "version": self.config.version,
            "socket_path": self.config.server.socket_path,
            "pipe_name": self.config.server.pipe_name,
            "max_connections": self.config.server.max_connections,
            "auth_required": self.config.server.auth_required,
            "debug": self.config.debug,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "config_source": str(self._get_active_config_path()),
        }

    def validate_config(self) -> List[str]:
        """验证配置完整性 - 企业级最佳实践实现"""
        errors = []

        # 验证应用基础配置
        try:
            validate_required_field("app_name", self.config.app_name, str)
            validate_required_field("version", self.config.version, str)
            if not self.config.app_name.strip():
                errors.append("app_name cannot be empty")
            if not self.config.version.strip():
                errors.append("version cannot be empty")
        except ConfigValidationError as e:
            errors.append(str(e))
        except Exception as e:
            errors.append(f"App config validation failed: {e}")

        # 验证IPC服务器配置
        try:
            # 验证日志级别
            valid_log_levels = {"debug", "info", "warning", "error", "critical"}
            if self.config.server.log_level.lower() not in valid_log_levels:
                errors.append(f"Invalid log_level: must be one of {valid_log_levels}")

            # 验证连接数限制
            if self.config.server.max_connections <= 0:
                errors.append("max_connections must be positive")
            elif self.config.server.max_connections > 10000:
                errors.append("max_connections should not exceed 10000 for stability")

            # 验证超时配置
            if self.config.server.connection_timeout <= 0:
                errors.append("connection_timeout must be positive")
            elif self.config.server.connection_timeout > 300:
                errors.append("connection_timeout should not exceed 300 seconds")

            # 验证socket路径（如果指定的话）
            if self.config.server.socket_path:
                socket_path = Path(self.config.server.socket_path)
                if not socket_path.parent.exists():
                    errors.append(
                        f"Socket parent directory does not exist: {socket_path.parent}"
                    )

        except ConfigValidationError as e:
            errors.append(str(e))
        except Exception as e:
            errors.append(f"IPC server config validation failed: {e}")

        # 验证数据库配置
        try:
            validate_required_field(
                "database.sqlite_url", self.config.database.sqlite_url, str
            )
            validate_required_field(
                "database.embedding_model", self.config.database.embedding_model, str
            )

            if self.config.database.vector_dimension <= 0:
                errors.append("database.vector_dimension must be positive")

        except ConfigValidationError as e:
            errors.append(str(e))
        except Exception as e:
            errors.append(f"Database config validation failed: {e}")

        # 验证存储配置
        try:
            data_dir = Path(self.config.storage.data_directory)
            if not data_dir.parent.exists():
                errors.append(
                    f"Storage parent directory does not exist: {data_dir.parent}"
                )

            # 验证数值配置
            if self.config.storage.graph_cache_ttl_seconds <= 0:
                errors.append("graph_cache_ttl_seconds must be positive")
            if self.config.storage.max_storage_gb <= 0:
                errors.append("max_storage_gb must be positive")
            if self.config.storage.cache_size_mb <= 0:
                errors.append("cache_size_mb must be positive")

        except Exception as e:
            errors.append(f"Storage config validation failed: {e}")

        # 验证连接器配置
        try:
            connectors_dir = Path(self.config.connectors.config_dir)
            if not connectors_dir.exists():
                logger.info(f"Creating connectors directory: {connectors_dir}")
                try:
                    connectors_dir.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    errors.append(f"Cannot create connectors directory: {e}")
        except Exception as e:
            errors.append(f"Connectors config validation failed: {e}")

        # 记录验证结果
        if errors:
            logger.warning(f"Configuration validation found {len(errors)} issues")
            for error in errors:
                logger.warning(f"Config validation: {error}")
        else:
            logger.debug("Configuration validation passed")

        return errors

    def get_connector_config(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取特定连接器的配置"""
        # 这里应该从数据库或配置文件中获取连接器特定配置
        # 暂时返回空字典作为占位符
        logger.info(f"获取连接器配置: {connector_id}")
        return {}

    def update_connector_config(
        self, connector_id: str, config: Dict[str, Any]
    ) -> bool:
        """更新连接器配置"""
        try:
            # 这里应该将配置保存到数据库或文件系统
            # 暂时只记录日志作为占位符实现
            logger.info(f"更新连接器配置: {connector_id}, config: {config}")
            return True
        except Exception as e:
            logger.error(f"更新连接器配置失败 {connector_id}: {e}")
            return False

    def get_system_config(self) -> Dict[str, Any]:
        """获取系统配置 - 包含环境信息"""
        system_config = {
            "app_name": self.config.app_name,
            "version": self.config.version,
            "debug": self.config.debug,
            "server": asdict(self.config.server),
            "database": asdict(self.config.database),
            "connectors": asdict(self.config.connectors),
            "ai": asdict(self.config.ai),
        }

        # 🆕 添加环境信息 - 使用配置上下文
        system_config["environment"] = {
            "name": self.context.get_environment_name(),
            "debug": self.context.is_debug_enabled(),
            "test_mode": self.context.is_test_environment(),
        }

        return system_config

    def update_system_config(self, config_updates: Dict[str, Any]) -> bool:
        """更新系统配置"""
        try:
            # 更新配置对象
            for key, value in config_updates.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                    logger.info(f"更新系统配置: {key} = {value}")

            # 保存配置到文件
            self.save_config()
            return True
        except Exception as e:
            logger.error(f"更新系统配置失败: {e}")
            return False

    # 🆕 环境管理相关方法 - 使用配置上下文
    def get_environment_info(self) -> Dict[str, Any]:
        """获取当前环境信息"""
        return {
            "name": self.context.get_environment_name(),
            "debug": self.context.is_debug_enabled(),
            "test_mode": self.context.is_test_environment(),
            "config_dir": str(self.context.get_config_dir()),
            "data_dir": str(self.context.get_data_dir()),
            "database_url": self.context.get_database_url(),
        }

    def list_all_environments(self) -> List[Dict[str, Any]]:
        """列出所有可用环境"""
        # 简化版本 - 返回当前环境信息
        return [self.get_environment_info()]

    def switch_environment(self, env_name: str) -> bool:
        """切换到指定环境 (需要重启服务)"""
        logger.warning(f"环境切换需要通过环境管理器实现: {env_name}")
        return False  # 需要外部环境管理器支持

    def get_environment_paths(self) -> Dict[str, str]:
        """获取当前环境的路径信息"""
        return {
            "config": str(self.context.get_config_dir()),
            "data": str(self.context.get_data_dir()),
            "logs": str(self.context.get_logs_dir()),
            "database": str(self.context.get_database_dir()),
        }


# 全局单例
_core_config_manager = None


def get_core_config() -> CoreConfigManager:
    """获取核心配置管理器单例"""
    global _core_config_manager
    if _core_config_manager is None:
        _core_config_manager = CoreConfigManager()
    return _core_config_manager


# 便捷访问函数
def get_server_config() -> IPCServerConfig:
    """获取服务器配置"""
    return get_core_config().config.server


def get_database_config() -> DatabaseConfig:
    """获取数据库配置"""
    return get_core_config().config.database


def get_connector_config() -> ConnectorConfig:
    """获取连接器配置"""
    return get_core_config().config.connectors


def get_ai_config() -> AIConfig:
    """获取AI配置"""
    return get_core_config().config.ai


def get_storage_config() -> StorageConfig:
    """获取存储配置"""
    return get_core_config().config.storage


# get_data_config() 已移除 - 使用 get_storage_config() 代替
