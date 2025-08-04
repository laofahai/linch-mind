"""
统一配置管理 - 从$HOME/.linch-mind/config.json读取配置
"""

import json
import os
import threading
from pathlib import Path
from typing import Dict, Any, Optional


class LinchConfig:
    """Linch Mind 统一配置管理"""

    _instance: Optional["LinchConfig"] = None
    _config_cache: Optional[Dict[str, Any]] = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return

        self.config_dir = Path.home() / ".linch-mind"
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_exists()
        self._initialized = True

    def _ensure_config_exists(self):
        """确保配置文件存在"""
        self.config_dir.mkdir(exist_ok=True)

        if not self.config_file.exists():
            default_config = {
                "daemon": {
                    "url": "http://localhost:58471",
                    "host": "localhost",
                    "port": 58471,
                },
                "connectors": {
                    "auto_reconnect": True,
                    "max_retry_attempts": 3,
                    "retry_delay": 5,
                },
                "development": {"debug_mode": False, "log_level": "INFO"},
            }

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)

    def get_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        if self._config_cache is None:
            with self._lock:
                if self._config_cache is None:
                    with open(self.config_file, "r", encoding="utf-8") as f:
                        self._config_cache = json.load(f)
        return self._config_cache

    def get_daemon_url(self) -> str:
        """获取daemon URL"""
        # 环境变量优先级最高
        env_url = os.getenv("LINCH_MIND_DAEMON_URL")
        if env_url:
            return env_url

        # 从配置文件读取
        config = self.get_config()
        return config.get("daemon", {}).get("url", "http://localhost:58471")

    def get_daemon_port(self) -> int:
        """获取daemon端口"""
        env_port = os.getenv("LINCH_MIND_DAEMON_PORT")
        if env_port:
            return int(env_port)

        config = self.get_config()
        return config.get("daemon", {}).get("port", 58471)

    def get_daemon_host(self) -> str:
        """获取daemon主机"""
        env_host = os.getenv("LINCH_MIND_DAEMON_HOST")
        if env_host:
            return env_host

        config = self.get_config()
        return config.get("daemon", {}).get("host", "localhost")

    def get_connector_config(self, key: str = None) -> Any:
        """获取连接器配置"""
        config = self.get_config()
        connector_config = config.get("connectors", {})

        if key is None:
            return connector_config

        return connector_config.get(key)

    def update_config(self, key_path: str, value: Any):
        """更新配置"""
        config = self.get_config()

        # 支持嵌套key，如 "daemon.port"
        keys = key_path.split(".")
        target = config

        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]

        target[keys[-1]] = value

        # 保存到文件
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        # 清除缓存
        self._config_cache = None

    def reload_config(self):
        """重新加载配置"""
        with self._lock:
            self._config_cache = None


# 全局配置实例
config = LinchConfig()


# 便捷函数
def get_daemon_url() -> str:
    """获取daemon URL的便捷函数"""
    return config.get_daemon_url()


def get_daemon_port() -> int:
    """获取daemon端口的便捷函数"""
    return config.get_daemon_port()


def get_daemon_host() -> str:
    """获取daemon主机的便捷函数"""
    return config.get_daemon_host()
