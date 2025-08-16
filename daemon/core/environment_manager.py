#!/usr/bin/env python3
"""
Environment Manager - Complete Environment Isolation System
核心环境管理器，提供完整的环境隔离和数据目录管理

核心功能:
- 环境检测和切换 (development/staging/production)
- 目录结构隔离 (~/.linch-mind/{env}/)
- 数据库隔离 (dev: unencrypted, prod: SQLCipher)
- 配置继承和环境特定配置
- 热环境切换支持
"""

import logging
import os
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class Environment(Enum):
    """支持的环境类型"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

    @classmethod
    def from_string(cls, env_str: str) -> "Environment":
        """从字符串创建环境类型"""
        env_str = env_str.lower().strip()
        for env in cls:
            if env.value == env_str:
                return env

        # 别名支持
        aliases = {
            "dev": cls.DEVELOPMENT,
            "develop": cls.DEVELOPMENT,
            "stage": cls.STAGING,
            "stg": cls.STAGING,
            "prod": cls.PRODUCTION,
            "production": cls.PRODUCTION,
        }

        if env_str in aliases:
            return aliases[env_str]

        raise ValueError(f"Unsupported environment: {env_str}")


@dataclass
class EnvironmentConfig:
    """环境配置数据类"""

    name: str
    display_name: str

    # 目录路径
    base_path: Path
    config_dir: Path
    data_dir: Path
    logs_dir: Path
    cache_dir: Path
    vectors_dir: Path
    database_dir: Path

    # 数据库配置
    use_encryption: bool
    database_suffix: str

    # 特性开关
    debug_enabled: bool
    performance_monitoring: bool
    auto_backup: bool

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "base_path": str(self.base_path),
            "config_dir": str(self.config_dir),
            "data_dir": str(self.data_dir),
            "logs_dir": str(self.logs_dir),
            "cache_dir": str(self.cache_dir),
            "vectors_dir": str(self.vectors_dir),
            "database_dir": str(self.database_dir),
            "use_encryption": self.use_encryption,
            "database_suffix": self.database_suffix,
            "debug_enabled": self.debug_enabled,
            "performance_monitoring": self.performance_monitoring,
            "auto_backup": self.auto_backup,
        }


class EnvironmentManager:
    """环境管理器 - 核心环境隔离服务

    该服务负责:
    1. 环境检测和切换
    2. 目录结构管理和隔离
    3. 数据库配置管理
    4. 环境特定配置加载
    5. 热环境切换支持
    """

    def __init__(self, base_dir: Optional[Path] = None):
        """初始化环境管理器

        Args:
            base_dir: 基础目录，默认为 ~/.linch-mind
        """
        self._lock = threading.RLock()
        self._base_dir = base_dir or Path.home() / ".linch-mind"
        self._current_env: Optional[Environment] = None
        self._env_configs: Dict[Environment, EnvironmentConfig] = {}
        self._shared_models_dir: Optional[Path] = None

        # 初始化环境
        self._detect_environment()
        self._initialize_environments()

        logger.info(
            f"EnvironmentManager initialized - Current: {self._current_env.value}"
        )

    def _detect_environment(self) -> Environment:
        """检测当前环境

        检测逻辑:
        1. LINCH_ENV环境变量
        2. PYTEST_CURRENT_TEST (测试环境)
        3. 其他测试环境指示器
        4. 默认为development
        """
        # 1. 显式环境变量
        env_var = os.getenv("LINCH_ENV", "").strip().lower()
        if env_var:
            try:
                detected_env = Environment.from_string(env_var)
                logger.info(
                    f"Environment detected from LINCH_ENV: {detected_env.value}"
                )
                self._current_env = detected_env
                return detected_env
            except ValueError as e:
                logger.warning(f"Invalid LINCH_ENV value '{env_var}': {e}")

        # 2. 测试环境检测
        test_indicators = [
            os.getenv("PYTEST_CURRENT_TEST"),
            os.getenv("TESTING") == "1",
            "test" in os.getenv("_", "").lower(),
            any("test" in arg.lower() for arg in os.sys.argv),
        ]

        if any(test_indicators):
            logger.info("Test environment detected")
            self._current_env = Environment.DEVELOPMENT
            return Environment.DEVELOPMENT

        # 3. 生产环境指示器
        if os.getenv("PRODUCTION") == "1" or os.getenv("NODE_ENV") == "production":
            logger.info("Production environment detected")
            self._current_env = Environment.PRODUCTION
            return Environment.PRODUCTION

        # 4. 默认开发环境
        logger.info("Using default development environment")
        self._current_env = Environment.DEVELOPMENT
        return Environment.DEVELOPMENT

    def _initialize_environments(self):
        """初始化所有环境配置"""
        with self._lock:
            # 共享模型目录
            self._shared_models_dir = self._base_dir / "shared" / "models"
            self._shared_models_dir.mkdir(parents=True, exist_ok=True)

            # 为每个环境创建配置
            for env in Environment:
                config = self._create_environment_config(env)
                self._env_configs[env] = config

                # 创建目录结构
                self._ensure_environment_directories(config)

            logger.info(
                f"Initialized {len(self._env_configs)} environment configurations"
            )

    def _create_environment_config(self, env: Environment) -> EnvironmentConfig:
        """为指定环境创建配置"""
        base_path = self._base_dir / env.value

        # 环境特定配置
        env_settings = {
            Environment.DEVELOPMENT: {
                "display_name": "Development",
                "use_encryption": False,
                "database_suffix": "_dev.db",
                "debug_enabled": True,
                "performance_monitoring": True,
                "auto_backup": False,
            },
            Environment.STAGING: {
                "display_name": "Staging",
                "use_encryption": True,
                "database_suffix": "_staging.db",
                "debug_enabled": True,
                "performance_monitoring": True,
                "auto_backup": True,
            },
            Environment.PRODUCTION: {
                "display_name": "Production",
                "use_encryption": True,
                "database_suffix": ".db",
                "debug_enabled": False,
                "performance_monitoring": False,
                "auto_backup": True,
            },
        }

        settings = env_settings[env]

        return EnvironmentConfig(
            name=env.value,
            display_name=settings["display_name"],
            base_path=base_path,
            config_dir=base_path / "config",
            data_dir=base_path / "data",
            logs_dir=base_path / "logs",
            cache_dir=base_path / "cache",
            vectors_dir=base_path / "vectors",
            database_dir=base_path / "database",
            use_encryption=settings["use_encryption"],
            database_suffix=settings["database_suffix"],
            debug_enabled=settings["debug_enabled"],
            performance_monitoring=settings["performance_monitoring"],
            auto_backup=settings["auto_backup"],
        )

    def _ensure_environment_directories(self, config: EnvironmentConfig):
        """确保环境目录结构存在"""
        directories = [
            config.base_path,
            config.config_dir,
            config.data_dir,
            config.logs_dir,
            config.cache_dir,
            config.vectors_dir,
            config.database_dir,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Environment directories ensured for {config.name}")

    @property
    def current_environment(self) -> Environment:
        """获取当前环境"""
        return self._current_env

    @property
    def current_config(self) -> EnvironmentConfig:
        """获取当前环境配置"""
        with self._lock:
            return self._env_configs[self._current_env]

    def get_environment_config(self, env: Environment) -> EnvironmentConfig:
        """获取指定环境的配置"""
        with self._lock:
            if env not in self._env_configs:
                raise ValueError(f"Environment not initialized: {env.value}")
            return self._env_configs[env]

    def list_environments(self) -> List[Dict[str, Any]]:
        """列出所有环境"""
        with self._lock:
            return [config.to_dict() for config in self._env_configs.values()]

    @contextmanager
    def switch_environment(self, env: Environment):
        """临时切换环境上下文管理器

        用于需要在特定环境下执行操作的场景
        """
        old_env = self._current_env
        try:
            with self._lock:
                self._current_env = env
                logger.info(f"Temporarily switched to environment: {env.value}")
            yield self.current_config
        finally:
            with self._lock:
                self._current_env = old_env
                logger.info(f"Restored environment: {old_env.value}")

    def permanently_switch_environment(self, env: Environment) -> bool:
        """永久切换环境

        这会更新环境变量和当前配置，需要重启服务生效
        """
        try:
            with self._lock:
                if env not in self._env_configs:
                    raise ValueError(f"Environment not available: {env.value}")

                old_env = self._current_env
                self._current_env = env

                # 设置环境变量 (当前进程)
                os.environ["LINCH_ENV"] = env.value

                logger.info(f"Environment switched: {old_env.value} -> {env.value}")
                logger.warning("Service restart required for full environment switch")

                return True

        except Exception as e:
            logger.error(f"Failed to switch environment to {env.value}: {e}")
            return False

    def get_database_url(self, in_memory: bool = False) -> str:
        """获取当前环境的数据库URL"""
        if in_memory:
            return "sqlite:///:memory:"

        config = self.current_config
        db_name = f"linch_mind{config.database_suffix}"
        db_path = config.database_dir / db_name

        return f"sqlite:///{db_path}"

    def get_vector_index_path(self) -> Path:
        """获取向量索引路径"""
        config = self.current_config
        return config.vectors_dir / "faiss_index.bin"

    def get_chroma_persist_directory(self) -> str:
        """获取ChromaDB持久化目录"""
        config = self.current_config
        chroma_dir = config.vectors_dir / "chromadb"
        chroma_dir.mkdir(exist_ok=True)
        return str(chroma_dir)

    def get_logs_directory(self) -> Path:
        """获取日志目录"""
        return self.current_config.logs_dir

    def get_config_directory(self) -> Path:
        """获取配置目录"""
        return self.current_config.config_dir

    def get_shared_models_directory(self) -> Path:
        """获取共享模型目录"""
        return self._shared_models_dir

    def get_cache_dir(self) -> Path:
        """获取缓存目录"""
        return self.current_config.cache_dir

    def get_data_dir(self) -> Path:
        """获取数据目录"""
        return self.current_config.data_dir

    def should_use_encryption(self) -> bool:
        """判断是否应该使用数据库加密"""
        return self.current_config.use_encryption

    def is_debug_enabled(self) -> bool:
        """判断是否启用调试模式"""
        return self.current_config.debug_enabled

    def get_environment_summary(self) -> Dict[str, Any]:
        """获取环境摘要信息"""
        config = self.current_config

        return {
            "current_environment": self._current_env.value,
            "display_name": config.display_name,
            "base_directory": str(config.base_path),
            "database_url": self.get_database_url(),
            "use_encryption": config.use_encryption,
            "debug_enabled": config.debug_enabled,
            "directories": {
                "config": str(config.config_dir),
                "data": str(config.data_dir),
                "logs": str(config.logs_dir),
                "cache": str(config.cache_dir),
                "vectors": str(config.vectors_dir),
                "database": str(config.database_dir),
            },
            "features": {
                "performance_monitoring": config.performance_monitoring,
                "auto_backup": config.auto_backup,
            },
        }

    def cleanup_environment(self, env: Environment, confirm: bool = False) -> bool:
        """清理指定环境的数据

        Args:
            env: 要清理的环境
            confirm: 确认执行清理操作

        Returns:
            是否成功清理
        """
        if not confirm:
            logger.warning(f"Cleanup for {env.value} requested but not confirmed")
            return False

        if env == self._current_env:
            logger.error("Cannot cleanup current active environment")
            return False

        try:
            config = self.get_environment_config(env)

            # 删除环境目录
            import shutil

            if config.base_path.exists():
                shutil.rmtree(config.base_path)
                logger.info(f"Environment {env.value} data cleaned up")

            # 重新创建目录结构
            self._ensure_environment_directories(config)

            return True

        except Exception as e:
            logger.error(f"Failed to cleanup environment {env.value}: {e}")
            return False


# 全局单例实例
_environment_manager: Optional[EnvironmentManager] = None
_manager_lock = threading.Lock()


def get_environment_manager() -> EnvironmentManager:
    """获取环境管理器单例"""
    global _environment_manager

    if _environment_manager is None:
        with _manager_lock:
            if _environment_manager is None:
                _environment_manager = EnvironmentManager()

    return _environment_manager


def reset_environment_manager():
    """重置环境管理器 (主要用于测试)"""
    global _environment_manager
    with _manager_lock:
        _environment_manager = None


# 便捷访问函数
def get_current_environment() -> Environment:
    """获取当前环境"""
    return get_environment_manager().current_environment


def get_current_environment_config() -> EnvironmentConfig:
    """获取当前环境配置"""
    return get_environment_manager().current_config


def get_database_url(in_memory: bool = False) -> str:
    """获取数据库URL"""
    return get_environment_manager().get_database_url(in_memory)


def get_environment_paths() -> Dict[str, Path]:
    """获取当前环境的所有路径"""
    config = get_current_environment_config()
    return {
        "base": config.base_path,
        "config": config.config_dir,
        "data": config.data_dir,
        "logs": config.logs_dir,
        "cache": config.cache_dir,
        "vectors": config.vectors_dir,
        "database": config.database_dir,
        "shared_models": get_environment_manager().get_shared_models_directory(),
    }


if __name__ == "__main__":
    # 测试环境管理器
    import json

    # 设置日志
    logging.basicConfig(level=logging.DEBUG)

    # 测试环境管理器
    env_manager = get_environment_manager()

    print("Environment Manager Test")
    print("=" * 50)

    # 显示当前环境信息
    summary = env_manager.get_environment_summary()
    print(json.dumps(summary, indent=2))

    # 列出所有环境
    print("\nAll Environments:")
    for env_info in env_manager.list_environments():
        print(f"- {env_info['display_name']}: {env_info['base_path']}")

    # 测试环境切换
    print("\nTesting temporary environment switch:")
    with env_manager.switch_environment(Environment.PRODUCTION):
        prod_config = env_manager.current_config
        print(f"Switched to: {prod_config.display_name}")
        print(f"Database URL: {env_manager.get_database_url()}")

    print(f"Back to: {env_manager.current_config.display_name}")
