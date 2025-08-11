#!/usr/bin/env python3
"""
核心配置管理 - Session V61 简化重构
简化环境变量处理，移除复杂的正则表达式，专注稳定性
"""

import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .error_handling import (
    ConfigFileError,
    ConfigValidationError,
    get_logger,
    safe_operation,
    validate_required_field,
)

logger = get_logger(__name__)


@dataclass
class ServerConfig:
    """服务器配置"""

    host: str = "0.0.0.0"  # nosec B104
    port: int = 0  # 0表示使用随机端口
    port_range: List[int] = field(
        default_factory=lambda: [49152, 65535]
    )  # 使用标准动态端口范围
    reload: bool = True
    log_level: str = "info"
    debug: bool = True  # 🔧 开发环境保持debug日志


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
    filesystem_enabled: bool = True
    clipboard_enabled: bool = False


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
    server: ServerConfig = field(default_factory=ServerConfig)
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

    def __init__(self, config_root: Optional[Path] = None):
        self.config_root = config_root or Path(__file__).parent.parent.parent

        # 🆕 Environment Manager Integration - V62环境隔离架构
        from core.environment_manager import get_environment_manager

        self.env_manager = get_environment_manager()

        # 使用环境管理器提供的路径，而非硬编码路径
        env_config = self.env_manager.current_config

        # 环境隔离的目录结构
        self.app_data_dir = env_config.base_path
        self.config_dir = env_config.config_dir
        self.data_dir = env_config.data_dir
        self.logs_dir = env_config.logs_dir
        self.db_dir = env_config.database_dir

        # 确保目录存在 (EnvironmentManager已创建，这里是双重保险)
        for dir_path in [self.config_dir, self.data_dir, self.logs_dir, self.db_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # 环境特定的配置文件路径
        self.primary_config_path = self.config_dir / "app.yaml"
        self.fallback_config_path = self.config_root / "linch-mind.config.yaml"

        # 加载配置
        self.config = self._load_config()
        self._setup_dynamic_paths()
        self._apply_env_overrides()

        logger.info(
            f"Core config loaded - Environment: {self.env_manager.current_environment.value}, Path: {self._get_active_config_path()}"
        )

    def _get_active_config_path(self) -> Path:
        """获取当前活跃的配置文件路径"""
        if self.primary_config_path.exists():
            return self.primary_config_path
        elif self.fallback_config_path.exists():
            return self.fallback_config_path
        else:
            return self.primary_config_path  # 将要创建的路径

    def _load_config(self) -> AppConfig:
        """加载配置 - 简化版本，去除复杂的环境变量处理"""

        # 1. 尝试从主配置路径加载
        if self.primary_config_path.exists():
            try:
                return self._load_from_yaml(self.primary_config_path)
            except Exception as e:
                logger.error(f"Failed to load primary config: {e}")

        # 2. 尝试从项目根目录配置加载
        if self.fallback_config_path.exists():
            try:
                config = self._load_from_yaml(self.fallback_config_path)
                # 保存到主配置路径
                self._save_config(config, self.primary_config_path)
                logger.info("Migrated config from project root to user directory")
                return config
            except Exception as e:
                logger.error(f"Failed to load fallback config: {e}")

        # 3. 创建默认配置
        config = AppConfig()
        self._save_config(config, self.primary_config_path)
        logger.info("Created default configuration")
        return config

    def _load_from_yaml(self, config_path: Path) -> AppConfig:
        """从YAML文件加载配置 - 增强错误处理"""

        def load_operation():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    yaml_data = yaml.safe_load(f)

                if not yaml_data:
                    yaml_data = {}

                return self._dict_to_config(yaml_data)
            except FileNotFoundError:
                raise ConfigFileError(
                    file_path=str(config_path),
                    operation="read",
                    reason="File not found",
                )
            except yaml.YAMLError as e:
                raise ConfigFileError(
                    file_path=str(config_path),
                    operation="parse",
                    reason=f"Invalid YAML syntax: {e}",
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
                server=ServerConfig(**server_data),
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
        """保存配置文件 - 改进格式化"""
        config_dict = asdict(config)

        # 简化文件头
        yaml_content = f"""# Linch Mind Configuration
# Generated: {datetime.now(timezone.utc).isoformat()}

"""

        try:
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(yaml_content)
                yaml.dump(
                    config_dict,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    indent=2,
                )

            logger.info(f"Configuration saved to: {config_path}")
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

        # 环境特定的数据库配置
        if is_test_env:
            # 测试环境：强制使用内存数据库
            self.config.database.sqlite_url = "sqlite:///:memory:"
            self.config.database.chroma_persist_directory = ":memory:"
            logger.info("测试环境检测：使用内存数据库")
        else:
            # 使用环境管理器的数据库配置
            self.config.database.sqlite_url = self.env_manager.get_database_url()
            self.config.database.chroma_persist_directory = (
                self.env_manager.get_chroma_persist_directory()
            )

            logger.info(
                f"环境数据库配置 ({self.env_manager.current_environment.value})"
            )
            logger.info(f"  Database: {self.config.database.sqlite_url}")
            logger.info(f"  ChromaDB: {self.config.database.chroma_persist_directory}")

        # 设置存储目录路径 - 使用环境特定的数据目录
        if not self.config.storage.data_directory:
            self.config.storage.data_directory = str(self.data_dir)

        # 设置向量索引路径 - 环境隔离
        vector_index_path = self.env_manager.get_vector_index_path()
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
                env_connectors_dir = (
                    self.env_manager.current_config.base_path / "connectors"
                )
                env_connectors_dir.mkdir(exist_ok=True)
                self.config.connectors.config_dir = str(env_connectors_dir)
                logger.debug(f"使用环境connectors目录: {env_connectors_dir}")

        # 环境特定的调试配置
        if self.env_manager.is_debug_enabled():
            self.config.debug = True
            self.config.server.debug = True
            logger.debug(
                f"环境 {self.env_manager.current_environment.value} 启用调试模式"
            )

    def _apply_env_overrides(self):
        """应用环境变量覆盖 - 移除，环境变量处理过度复杂"""
        # 移除环境变量覆盖功能，简化配置管理

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
        """获取各种路径"""
        return {
            "app_data": self.app_data_dir,
            "config": self.config_dir,
            "data": self.data_dir,
            "logs": self.logs_dir,
            "database": self.db_dir,
            "primary_config": self.primary_config_path,
            "fallback_config": self.fallback_config_path,
        }

    def get_server_info(self) -> Dict[str, Any]:
        """获取服务器信息"""
        return {
            "app_name": self.config.app_name,
            "version": self.config.version,
            "host": self.config.server.host,
            "port": self.config.server.port,
            "debug": self.config.debug,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "config_source": str(self._get_active_config_path()),
        }

    def validate_config(self) -> List[str]:
        """验证配置完整性 - 使用统一验证器"""
        errors = []

        try:
            # 验证服务器配置 - 对于纯IPC架构跳过端口验证
            validate_required_field("server.host", self.config.server.host, str)
            # 注释掉端口验证，因为IPC模式使用port=0是合理的
            # validate_port_range("server.port", self.config.server.port)
        except ConfigValidationError as e:
            errors.append(str(e))

        try:
            # 验证连接器配置目录
            connectors_dir = Path(self.config.connectors.config_dir)
            if not connectors_dir.exists():
                logger.warning(
                    "Connectors directory missing, creating", path=str(connectors_dir)
                )
                try:
                    connectors_dir.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    errors.append(f"Cannot create connectors directory: {e}")
        except Exception as e:
            errors.append(f"Connectors directory validation failed: {e}")

        try:
            # 验证数据库配置
            validate_required_field(
                "database.sqlite_url", self.config.database.sqlite_url, str
            )
        except ConfigValidationError as e:
            errors.append(str(e))

        try:
            # 验证ChromaDB目录路径
            chroma_dir = Path(self.config.database.chroma_persist_directory)
            chroma_dir.mkdir(parents=True, exist_ok=True)
            logger.debug("ChromaDB directory validated", path=str(chroma_dir))
        except Exception as e:
            errors.append(f"Cannot create ChromaDB directory: {e}")

        # 记录验证结果
        if errors:
            logger.error("Configuration validation failed", error_count=len(errors))
            for error in errors:
                logger.error("Validation error", error=error)
        else:
            logger.info("Configuration validation passed")

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

        # 🆕 添加环境信息
        system_config["environment"] = self.env_manager.get_environment_summary()

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

    # 🆕 环境管理相关方法
    def get_environment_info(self) -> Dict[str, Any]:
        """获取当前环境信息"""
        return self.env_manager.get_environment_summary()

    def list_all_environments(self) -> List[Dict[str, Any]]:
        """列出所有可用环境"""
        return self.env_manager.list_environments()

    def switch_environment(self, env_name: str) -> bool:
        """切换到指定环境 (需要重启服务)"""
        try:
            from core.environment_manager import Environment

            target_env = Environment.from_string(env_name)
            return self.env_manager.permanently_switch_environment(target_env)
        except Exception as e:
            logger.error(f"切换环境失败 {env_name}: {e}")
            return False

    def get_environment_paths(self) -> Dict[str, str]:
        """获取当前环境的路径信息"""
        from core.environment_manager import get_environment_paths

        paths = get_environment_paths()
        return {key: str(path) for key, path in paths.items()}


# 全局单例
_core_config_manager = None


def get_core_config() -> CoreConfigManager:
    """获取核心配置管理器单例"""
    global _core_config_manager
    if _core_config_manager is None:
        _core_config_manager = CoreConfigManager()
    return _core_config_manager


# 便捷访问函数
def get_server_config() -> ServerConfig:
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
