#!/usr/bin/env python3
"""
ConfigManager - 简洁配置架构最佳实践
彻底重构，零兼容包袱，单一配置入口
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from functools import lru_cache

logger = logging.getLogger(__name__)


@dataclass
class AppPaths:
    """应用路径配置 - 基于约定优于配置"""
    # 环境相关根目录
    environment: str
    root_dir: Path
    config_dir: Path
    data_dir: Path
    logs_dir: Path
    
    # 核心文件路径
    database_file: Path
    socket_file: Path
    pid_file: Path
    
    # 应用数据目录
    vectors_dir: Path
    graph_dir: Path
    embeddings_dir: Path
    temp_dir: Path

    @classmethod
    def from_environment(cls, env: str = None) -> "AppPaths":
        """基于环境约定生成路径"""
        if env is None:
            env = os.getenv("LINCH_MIND_ENVIRONMENT", "development")
        
        # 约定路径结构: ~/.linch-mind/{env}/
        root_dir = Path.home() / ".linch-mind" / env
        config_dir = root_dir / "config"
        data_dir = root_dir / "data"
        logs_dir = root_dir / "logs"
        
        # 确保目录存在
        for directory in [root_dir, config_dir, data_dir, logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        return cls(
            environment=env,
            root_dir=root_dir,
            config_dir=config_dir,
            data_dir=data_dir,
            logs_dir=logs_dir,
            # 核心文件
            database_file=data_dir / "linch_mind.db",
            socket_file=data_dir / "daemon.socket",
            pid_file=data_dir / "daemon.pid",
            # 应用数据目录
            vectors_dir=data_dir / "vectors",
            graph_dir=data_dir / "graph", 
            embeddings_dir=data_dir / "embeddings",
            temp_dir=data_dir / "temp"
        )


@dataclass 
class AppConfig:
    """应用配置 - 扁平化结构，避免过度嵌套"""
    # 基础信息
    app_name: str = "Linch Mind"
    environment: str = "development"
    debug: bool = False
    
    # 数据库配置
    db_use_encryption: bool = False
    db_connection_pool_size: int = 10
    db_query_timeout: int = 30
    
    # IPC配置  
    ipc_auth_required: bool = True
    ipc_max_connections: int = 100
    ipc_timeout: int = 30
    
    # AI/向量配置
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:0.5b"
    vector_dimension: int = 384
    vector_index_type: str = "HNSW"
    
    # 性能配置
    max_workers: int = 4
    cache_size: int = 1000
    batch_size: int = 100
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "structured"
    log_max_files: int = 10


class ConfigManager:
    """统一配置管理器 - 简洁架构最佳实践
    
    设计原则:
    1. 单一入口：唯一的配置管理器
    2. 三层配置：环境变量 → 文件 → 数据库(可选)
    3. 约定优于配置：固定路径结构
    4. 零服务依赖：启动时不依赖任何服务
    5. 延迟数据库：数据库配置作为运行时特性
    """
    
    _instance: Optional["ConfigManager"] = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        
        # 1. 加载路径配置
        self.paths = AppPaths.from_environment()
        
        # 2. 加载基础配置 
        self.config = self._load_config()
        
        # 3. 数据库配置管理器(延迟初始化)
        self._db_config = None
        
        logger.info(f"✅ ConfigManager初始化完成 - environment={self.paths.environment}")

    def _load_config(self) -> AppConfig:
        """加载配置 - 环境变量优先"""
        config = AppConfig()
        
        # 设置环境信息
        config.environment = self.paths.environment
        config.debug = (self.paths.environment == "development")
        
        # 生产环境启用加密
        config.db_use_encryption = (self.paths.environment == "production")
        
        # 从环境变量覆盖配置
        config.ollama_host = os.getenv("OLLAMA_HOST", config.ollama_host)
        config.ollama_model = os.getenv("OLLAMA_MODEL", config.ollama_model) 
        config.log_level = os.getenv("LOG_LEVEL", "DEBUG" if config.debug else "INFO")
        
        # 数值类型转换
        if workers := os.getenv("MAX_WORKERS"):
            config.max_workers = int(workers)
        if dimension := os.getenv("VECTOR_DIMENSION"):
            config.vector_dimension = int(dimension)
            
        logger.debug(f"基础配置加载完成: debug={config.debug}, ollama_host={config.ollama_host}")
        return config

    # =================
    # 配置获取接口
    # =================
    
    def get(self, key: str, default: Any = None) -> Any:
        """通用配置获取接口
        
        支持点表示法: db.use_encryption, ipc.auth_required
        """
        if "." in key:
            section, field = key.split(".", 1)
            if section == "db":
                field = f"db_{field}"
            elif section == "ipc":  
                field = f"ipc_{field}"
            elif section == "vector":
                field = f"vector_{field}"
            elif section == "ollama":
                field = f"ollama_{field}"
            elif section == "log":
                field = f"log_{field}"
            else:
                field = key.replace(".", "_")
        else:
            field = key
            
        return getattr(self.config, field, default)
    
    def set(self, key: str, value: Any) -> bool:
        """设置配置值 - 优先写入数据库"""
        # 1. 更新内存配置
        if "." in key:
            section, field = key.split(".", 1)
            if section == "db":
                field = f"db_{field}"
            elif section == "ipc":
                field = f"ipc_{field}"
            elif section == "vector":
                field = f"vector_{field}"  
            elif section == "ollama":
                field = f"ollama_{field}"
            elif section == "log":
                field = f"log_{field}"
            else:
                field = key.replace(".", "_")
        else:
            field = key
            
        if hasattr(self.config, field):
            setattr(self.config, field, value)
        
        # 2. 尝试写入数据库(如果可用)
        if self._db_config is not None:
            try:
                return self._db_config.set_config_value(key.split(".")[0], key.split(".")[1], value)
            except Exception as e:
                logger.warning(f"数据库配置更新失败 {key}={value}: {e}")
                
        return True
    
    # =================
    # 路径获取接口
    # =================
    
    @lru_cache(maxsize=1)
    def get_paths(self) -> Dict[str, Path]:
        """获取所有路径信息"""
        return {
            "root": self.paths.root_dir,
            "config": self.paths.config_dir,
            "data": self.paths.data_dir,
            "logs": self.paths.logs_dir,
            "database": self.paths.database_file,
            "socket": self.paths.socket_file,
            "pid": self.paths.pid_file,
            "vectors": self.paths.vectors_dir,
            "graph": self.paths.graph_dir,
            "embeddings": self.paths.embeddings_dir,
            "temp": self.paths.temp_dir,
        }

    # =================
    # 数据库配置集成(可选)
    # =================
    
    def enable_database_config(self):
        """启用数据库配置 - 运行时调用"""
        if self._db_config is None:
            try:
                from config.database_config_manager import DatabaseConfigManager
                self._db_config = DatabaseConfigManager()
                
                # 从数据库加载配置覆盖
                self._load_database_overrides()
                logger.info("✅ 数据库配置已启用")
                
            except Exception as e:
                logger.warning(f"数据库配置启用失败: {e}")
    
    def _load_database_overrides(self):
        """从数据库加载配置覆盖"""
        if self._db_config is None:
            return
            
        # 批量加载主要配置
        overrides = {
            "ollama.host": "ollama_host",
            "ollama.model": "ollama_model", 
            "vector.dimension": "vector_dimension",
            "vector.index_type": "vector_index_type",
            "db.use_encryption": "db_use_encryption",
            "ipc.auth_required": "ipc_auth_required",
            "log.level": "log_level",
        }
        
        for db_key, config_attr in overrides.items():
            section, key = db_key.split(".")
            try:
                value = self._db_config.get_config_value(section, key)
                if value is not None:
                    setattr(self.config, config_attr, value)
                    logger.debug(f"数据库配置覆盖: {config_attr}={value}")
            except Exception:
                pass  # 忽略单个配置加载失败

    # =================
    # 便捷访问属性
    # =================
    
    @property
    def database_file(self) -> Path:
        return self.paths.database_file
        
    @property 
    def socket_file(self) -> Path:
        return self.paths.socket_file
        
    @property
    def is_debug(self) -> bool:
        return self.config.debug
        
    @property
    def is_production(self) -> bool:
        return self.paths.environment == "production"


# =================
# 全局访问接口
# =================

_config_manager: Optional[ConfigManager] = None

def get_config() -> ConfigManager:
    """获取全局配置管理器"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_config_value(key: str, default: Any = None) -> Any:
    """便捷配置获取函数"""
    return get_config().get(key, default)

def set_config_value(key: str, value: Any) -> bool:
    """便捷配置设置函数"""
    return get_config().set(key, value)

def get_app_paths() -> Dict[str, Path]:
    """便捷路径获取函数"""
    return get_config().get_paths()

def reset_config():
    """重置配置管理器 - 测试用"""
    global _config_manager
    _config_manager = None