#!/usr/bin/env python3
"""
统一配置管理系统
支持分层配置、环境变量覆盖、热重载等功能
"""

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ConfigMetadata:
    """配置元数据"""

    source: str  # 配置来源文件路径
    loaded_at: datetime
    version: str = "1.0.0"
    checksum: Optional[str] = None


@dataclass
class ServerConfig:
    """服务器配置"""

    host: str = "localhost"
    port: int = 8000
    ipc_socket_path: str = "/tmp/linch-mind.sock"
    log_level: str = "INFO"
    debug: bool = False
    workers: int = 1
    timeout: int = 30


@dataclass
class DatabaseConfig:
    """数据库配置"""

    url: str = "sqlite:///~/.linch-mind/database.db"
    pool_size: int = 5
    echo: bool = False
    migrate_on_startup: bool = True


@dataclass
class StorageConfig:
    """存储配置"""

    data_dir: str = "~/.linch-mind/data"
    cache_dir: str = "~/.linch-mind/cache"
    backup_dir: str = "~/.linch-mind/backups"
    max_cache_size_mb: int = 1024
    enable_encryption: bool = False


@dataclass
class AIConfig:
    """AI服务配置"""

    embedding_model: str = "all-MiniLM-L6-v2"
    vector_dimension: int = 384
    faiss_index_type: str = "IndexFlatIP"
    max_graph_nodes: int = 10000
    similarity_threshold: float = 0.7


@dataclass
class ConnectorConfig:
    """连接器配置"""

    auto_start: bool = True
    health_check_interval: int = 30
    restart_on_failure: bool = True
    max_restart_attempts: int = 3
    enabled_connectors: List[str] = field(default_factory=list)


@dataclass
class SecurityConfig:
    """安全配置"""

    enable_authentication: bool = False
    jwt_secret: str = "change-me-in-production"
    token_expiry_hours: int = 24
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    allowed_clients: List[str] = field(default_factory=lambda: ["127.0.0.1"])


@dataclass
class UnifiedConfig:
    """统一配置类"""

    server: ServerConfig = field(default_factory=ServerConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    connectors: ConnectorConfig = field(default_factory=ConnectorConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)

    # 元数据
    _metadata: ConfigMetadata = field(
        default_factory=lambda: ConfigMetadata(
            source="default", loaded_at=datetime.now()
        )
    )


class ConfigFileWatcher(FileSystemEventHandler):
    """配置文件监控器"""

    def __init__(self, config_manager: "UnifiedConfigManager"):
        self.config_manager = config_manager

    def on_modified(self, event):
        """文件修改事件处理"""
        if (
            not event.is_directory
            and event.src_path in self.config_manager.watched_files
        ):
            logger.info(f"配置文件变更检测: {event.src_path}")
            self.config_manager.reload_config()


class UnifiedConfigManager:
    """统一配置管理器"""

    def __init__(self, app_name: str = "linch-mind"):
        self.app_name = app_name
        self.config_dir = Path.home() / f".{app_name}" / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 配置文件路径（按优先级排序）
        self.config_files = [
            self.config_dir / "config.yaml",
            self.config_dir / "config.json",
            Path.cwd() / "config.yaml",
            Path.cwd() / "config.json",
        ]

        self.watched_files = set()
        self.config = UnifiedConfig()
        self.file_watcher = None
        self.observer = None

        # 配置变更回调
        self.change_callbacks = []

    def load_config(self) -> UnifiedConfig:
        """加载配置（分层加载）"""
        logger.info("开始加载配置...")

        # 1. 从配置文件加载
        config_data = {}
        loaded_files = []

        for config_file in self.config_files:
            if config_file.exists():
                try:
                    file_data = self._load_config_file(config_file)
                    config_data.update(file_data)
                    loaded_files.append(str(config_file))
                    self.watched_files.add(str(config_file))
                    logger.info(f"已加载配置文件: {config_file}")
                except Exception as e:
                    logger.error(f"加载配置文件失败 {config_file}: {e}")

        # 2. 从环境变量覆盖
        env_overrides = self._load_from_environment()
        if env_overrides:
            config_data.update(env_overrides)
            logger.info(f"已应用环境变量覆盖: {len(env_overrides)} 项")

        # 3. 构建配置对象
        self.config = self._build_config(config_data)

        # 4. 设置元数据
        self.config._metadata = ConfigMetadata(
            source=", ".join(loaded_files) if loaded_files else "default",
            loaded_at=datetime.now(),
            version="1.0.0",
        )

        # 5. 验证配置
        self._validate_config()

        # 6. 启用热重载
        if loaded_files:
            self._setup_hot_reload()

        logger.info(f"配置加载完成，来源: {self.config._metadata.source}")
        return self.config

    def _load_config_file(self, file_path: Path) -> Dict[str, Any]:
        """加载单个配置文件"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if file_path.suffix.lower() in [".yaml", ".yml"]:
            return yaml.safe_load(content) or {}
        elif file_path.suffix.lower() == ".json":
            return json.loads(content) or {}
        else:
            raise ValueError(f"不支持的配置文件格式: {file_path}")

    def _load_from_environment(self) -> Dict[str, Any]:
        """从环境变量加载配置覆盖"""
        env_config = {}
        prefix = f"{self.app_name.upper().replace('-', '_')}_"

        # 定义环境变量映射
        env_mappings = {
            f"{prefix}SERVER_HOST": ("server", "host"),
            f"{prefix}SERVER_PORT": ("server", "port"),
            f"{prefix}SERVER_LOG_LEVEL": ("server", "log_level"),
            f"{prefix}SERVER_DEBUG": ("server", "debug"),
            f"{prefix}DATABASE_URL": ("database", "url"),
            f"{prefix}STORAGE_DATA_DIR": ("storage", "data_dir"),
            f"{prefix}AI_EMBEDDING_MODEL": ("ai", "embedding_model"),
            f"{prefix}CONNECTORS_AUTO_START": ("connectors", "auto_start"),
            f"{prefix}SECURITY_ENABLE_AUTH": ("security", "enable_authentication"),
        }

        for env_key, (section, key) in env_mappings.items():
            if env_key in os.environ:
                value = os.environ[env_key]

                # 类型转换
                if key in [
                    "port",
                    "workers",
                    "timeout",
                    "pool_size",
                    "max_cache_size_mb",
                    "vector_dimension",
                    "max_graph_nodes",
                    "health_check_interval",
                    "max_restart_attempts",
                    "token_expiry_hours",
                    "rate_limit_requests",
                    "rate_limit_window",
                ]:
                    value = int(value)
                elif key in [
                    "debug",
                    "echo",
                    "migrate_on_startup",
                    "enable_encryption",
                    "auto_start",
                    "restart_on_failure",
                    "enable_authentication",
                ]:
                    value = value.lower() in ("true", "1", "yes", "on")
                elif key in ["similarity_threshold"]:
                    value = float(value)

                # 设置嵌套配置
                if section not in env_config:
                    env_config[section] = {}
                env_config[section][key] = value

        return env_config

    def _build_config(self, config_data: Dict[str, Any]) -> UnifiedConfig:
        """构建配置对象"""
        config = UnifiedConfig()

        # 服务器配置
        if "server" in config_data:
            server_data = config_data["server"]
            config.server = ServerConfig(
                host=server_data.get("host", config.server.host),
                port=server_data.get("port", config.server.port),
                ipc_socket_path=server_data.get(
                    "ipc_socket_path", config.server.ipc_socket_path
                ),
                log_level=server_data.get("log_level", config.server.log_level),
                debug=server_data.get("debug", config.server.debug),
                workers=server_data.get("workers", config.server.workers),
                timeout=server_data.get("timeout", config.server.timeout),
            )

        # 数据库配置
        if "database" in config_data:
            db_data = config_data["database"]
            config.database = DatabaseConfig(
                url=db_data.get("url", config.database.url),
                pool_size=db_data.get("pool_size", config.database.pool_size),
                echo=db_data.get("echo", config.database.echo),
                migrate_on_startup=db_data.get(
                    "migrate_on_startup", config.database.migrate_on_startup
                ),
            )

        # 存储配置
        if "storage" in config_data:
            storage_data = config_data["storage"]
            config.storage = StorageConfig(
                data_dir=storage_data.get("data_dir", config.storage.data_dir),
                cache_dir=storage_data.get("cache_dir", config.storage.cache_dir),
                backup_dir=storage_data.get("backup_dir", config.storage.backup_dir),
                max_cache_size_mb=storage_data.get(
                    "max_cache_size_mb", config.storage.max_cache_size_mb
                ),
                enable_encryption=storage_data.get(
                    "enable_encryption", config.storage.enable_encryption
                ),
            )

        # AI配置
        if "ai" in config_data:
            ai_data = config_data["ai"]
            config.ai = AIConfig(
                embedding_model=ai_data.get(
                    "embedding_model", config.ai.embedding_model
                ),
                vector_dimension=ai_data.get(
                    "vector_dimension", config.ai.vector_dimension
                ),
                faiss_index_type=ai_data.get(
                    "faiss_index_type", config.ai.faiss_index_type
                ),
                max_graph_nodes=ai_data.get(
                    "max_graph_nodes", config.ai.max_graph_nodes
                ),
                similarity_threshold=ai_data.get(
                    "similarity_threshold", config.ai.similarity_threshold
                ),
            )

        # 连接器配置
        if "connectors" in config_data:
            conn_data = config_data["connectors"]
            config.connectors = ConnectorConfig(
                auto_start=conn_data.get("auto_start", config.connectors.auto_start),
                health_check_interval=conn_data.get(
                    "health_check_interval", config.connectors.health_check_interval
                ),
                restart_on_failure=conn_data.get(
                    "restart_on_failure", config.connectors.restart_on_failure
                ),
                max_restart_attempts=conn_data.get(
                    "max_restart_attempts", config.connectors.max_restart_attempts
                ),
                enabled_connectors=conn_data.get(
                    "enabled_connectors", config.connectors.enabled_connectors
                ),
            )

        # 安全配置
        if "security" in config_data:
            sec_data = config_data["security"]
            config.security = SecurityConfig(
                enable_authentication=sec_data.get(
                    "enable_authentication", config.security.enable_authentication
                ),
                jwt_secret=sec_data.get("jwt_secret", config.security.jwt_secret),
                token_expiry_hours=sec_data.get(
                    "token_expiry_hours", config.security.token_expiry_hours
                ),
                rate_limit_requests=sec_data.get(
                    "rate_limit_requests", config.security.rate_limit_requests
                ),
                rate_limit_window=sec_data.get(
                    "rate_limit_window", config.security.rate_limit_window
                ),
                allowed_clients=sec_data.get(
                    "allowed_clients", config.security.allowed_clients
                ),
            )

        return config

    def _validate_config(self):
        """验证配置有效性"""
        errors = []

        # 验证端口范围
        if not (1 <= self.config.server.port <= 65535):
            errors.append(f"无效的服务器端口: {self.config.server.port}")

        # 验证日志级别
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.config.server.log_level.upper() not in valid_log_levels:
            errors.append(f"无效的日志级别: {self.config.server.log_level}")

        # 验证目录权限
        for dir_path in [self.config.storage.data_dir, self.config.storage.cache_dir]:
            expanded_path = Path(dir_path).expanduser()
            try:
                expanded_path.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                errors.append(f"无权限创建目录: {dir_path}")

        # 验证AI配置
        if self.config.ai.vector_dimension <= 0:
            errors.append(f"无效的向量维度: {self.config.ai.vector_dimension}")

        if not (0.0 <= self.config.ai.similarity_threshold <= 1.0):
            errors.append(f"相似度阈值超出范围: {self.config.ai.similarity_threshold}")

        if errors:
            error_msg = "配置验证失败:\n" + "\n".join(
                f"  - {error}" for error in errors
            )
            raise ValueError(error_msg)

        logger.info("配置验证通过")

    def _setup_hot_reload(self):
        """设置配置热重载"""
        if self.observer:
            self.observer.stop()

        self.observer = Observer()
        self.file_watcher = ConfigFileWatcher(self)

        # 监控配置目录
        self.observer.schedule(self.file_watcher, str(self.config_dir), recursive=False)
        self.observer.start()

        logger.info("配置热重载已启用")

    def reload_config(self):
        """重新加载配置"""
        logger.info("重新加载配置...")
        try:
            old_config = self.config
            new_config = self.load_config()

            # 通知变更回调
            for callback in self.change_callbacks:
                try:
                    callback(old_config, new_config)
                except Exception as e:
                    logger.error(f"配置变更回调执行失败: {e}")

            logger.info("配置重新加载完成")

        except Exception as e:
            logger.error(f"配置重新加载失败: {e}")

    def add_change_callback(self, callback):
        """添加配置变更回调"""
        self.change_callbacks.append(callback)

    def validate_config(self) -> List[str]:
        """验证配置并返回错误列表"""
        errors = []

        try:
            self._validate_config()
        except ValueError as e:
            # 解析验证错误信息
            error_msg = str(e)
            if "配置验证失败:" in error_msg:
                error_lines = error_msg.split("\n")[1:]  # 跳过标题行
                errors = [line.strip("  - ") for line in error_lines if line.strip()]
        except Exception as e:
            errors.append(f"配置验证异常: {e}")

        return errors

    def get_paths(self) -> Dict[str, Path]:
        """获取所有路径配置"""
        app_data_dir = Path.home() / f".{self.app_name}"
        return {
            "app_data": app_data_dir,
            "data": Path(self.config.storage.data_dir).expanduser(),
            "cache": Path(self.config.storage.cache_dir).expanduser(),
            "backups": Path(self.config.storage.backup_dir).expanduser(),
            "logs": app_data_dir / "logs",
            "config": self.config_dir,
            "database": app_data_dir / "database",
            "primary_config": self.config_dir / "config.yaml",
        }

    def export_config(self, format: str = "yaml") -> str:
        """导出当前配置"""
        config_dict = {
            "server": {
                "host": self.config.server.host,
                "port": self.config.server.port,
                "ipc_socket_path": self.config.server.ipc_socket_path,
                "log_level": self.config.server.log_level,
                "debug": self.config.server.debug,
                "workers": self.config.server.workers,
                "timeout": self.config.server.timeout,
            },
            "database": {
                "url": self.config.database.url,
                "pool_size": self.config.database.pool_size,
                "echo": self.config.database.echo,
                "migrate_on_startup": self.config.database.migrate_on_startup,
            },
            "storage": {
                "data_dir": self.config.storage.data_dir,
                "cache_dir": self.config.storage.cache_dir,
                "backup_dir": self.config.storage.backup_dir,
                "max_cache_size_mb": self.config.storage.max_cache_size_mb,
                "enable_encryption": self.config.storage.enable_encryption,
            },
            "ai": {
                "embedding_model": self.config.ai.embedding_model,
                "vector_dimension": self.config.ai.vector_dimension,
                "faiss_index_type": self.config.ai.faiss_index_type,
                "max_graph_nodes": self.config.ai.max_graph_nodes,
                "similarity_threshold": self.config.ai.similarity_threshold,
            },
            "connectors": {
                "auto_start": self.config.connectors.auto_start,
                "health_check_interval": self.config.connectors.health_check_interval,
                "restart_on_failure": self.config.connectors.restart_on_failure,
                "max_restart_attempts": self.config.connectors.max_restart_attempts,
                "enabled_connectors": self.config.connectors.enabled_connectors,
            },
            "security": {
                "enable_authentication": self.config.security.enable_authentication,
                "token_expiry_hours": self.config.security.token_expiry_hours,
                "rate_limit_requests": self.config.security.rate_limit_requests,
                "rate_limit_window": self.config.security.rate_limit_window,
                "allowed_clients": self.config.security.allowed_clients,
            },
        }

        if format.lower() == "yaml":
            return yaml.dump(config_dict, default_flow_style=False, allow_unicode=True)
        elif format.lower() == "json":
            return json.dumps(config_dict, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"不支持的格式: {format}")

    def cleanup(self):
        """清理资源"""
        if self.observer:
            self.observer.stop()
            self.observer.join()


# 全局配置管理器实例
_config_manager = None


def get_config_manager() -> UnifiedConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = UnifiedConfigManager()
        _config_manager.load_config()
    return _config_manager


def get_config() -> UnifiedConfig:
    """便捷函数：获取当前配置"""
    return get_config_manager().config
