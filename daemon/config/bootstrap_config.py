#!/usr/bin/env python3
"""
Bootstrap配置层 - 零依赖的基础配置
解决循环依赖的根本方案

这是系统的第一层配置，完全不依赖任何服务或DI容器
只从文件读取最基本的启动配置
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class BootstrapDatabaseConfig:
    """数据库启动配置"""
    type: str = "sqlite"
    sqlite_file: str = "linch_mind.db"
    use_encryption: bool = False


@dataclass
class BootstrapIPCConfig:
    """IPC启动配置"""
    socket_path: Optional[str] = None
    pipe_name: Optional[str] = None
    max_connections: int = 100
    auth_required: bool = True


@dataclass 
class BootstrapConfig:
    """Bootstrap配置 - 系统启动的最小配置集"""
    environment: str = "development"
    debug: bool = False
    database: BootstrapDatabaseConfig = None
    ipc: BootstrapIPCConfig = None
    
    def __post_init__(self):
        if self.database is None:
            self.database = BootstrapDatabaseConfig()
        if self.ipc is None:
            self.ipc = BootstrapIPCConfig()


class BootstrapConfigManager:
    """
    Bootstrap配置管理器
    
    特性：
    - 零依赖：不依赖任何服务或DI容器
    - 只读取文件配置
    - 提供系统启动的最小配置集
    - 单例模式但不通过DI容器
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.config = self._load_bootstrap_config()
        
    def _load_bootstrap_config(self) -> BootstrapConfig:
        """加载Bootstrap配置"""
        # 1. 从环境变量获取环境
        environment = os.getenv("LINCH_MIND_ENVIRONMENT", "development")
        
        # 2. 构建配置路径
        home_dir = Path.home()
        config_dir = home_dir / ".linch-mind" / environment / "config"
        
        # 3. 创建基础配置
        config = BootstrapConfig(
            environment=environment,
            debug=(environment == "development")
        )
        
        # 4. 设置数据库配置（固化路径）
        config.database.use_encryption = (environment == "production")
        data_dir = home_dir / ".linch-mind" / environment / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        config.database.sqlite_file = str(data_dir / "linch_mind.db")
        
        # 5. 设置IPC配置（固化路径）
        config.ipc.socket_path = str(data_dir / "daemon.socket")
            
        logger.info(f"Bootstrap配置加载完成: environment={environment}, socket_path={config.ipc.socket_path}")
        
        return config
    
    def get_database_config(self) -> BootstrapDatabaseConfig:
        """获取数据库启动配置"""
        return self.config.database
    
    def get_ipc_config(self) -> BootstrapIPCConfig:
        """获取IPC启动配置"""
        return self.config.ipc
    
    def get_environment(self) -> str:
        """获取当前环境"""
        return self.config.environment
    
    def get_data_dir(self) -> Path:
        """获取数据目录"""
        home_dir = Path.home()
        return home_dir / ".linch-mind" / self.config.environment / "data"
    
    def get_config_dir(self) -> Path:
        """获取配置目录"""
        home_dir = Path.home()
        return home_dir / ".linch-mind" / self.config.environment / "config"


# 全局单例函数（不通过DI容器）
def get_bootstrap_config() -> BootstrapConfigManager:
    """获取Bootstrap配置管理器"""
    return BootstrapConfigManager()