#!/usr/bin/env python3
"""
延迟配置加载器 - P0性能优化
显著减少启动时间，仅在需要时加载配置段
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, TYPE_CHECKING
from functools import lru_cache

if TYPE_CHECKING:
    from .config_context import ConfigContext
    from .core_config import AppConfig, IPCServerConfig, DatabaseConfig, StorageConfig

from .core_config import CoreConfigManager, AppConfig
from .error_handling import get_logger

logger = get_logger(__name__)


class LazyConfigManager:
    """延迟配置管理器 - 🚀 启动性能优化版本
    
    核心优化:
    - 延迟加载各配置段，仅在需要时加载
    - 使用LRU缓存避免重复加载
    - 最小启动时配置验证
    - 保持完整API兼容性
    """

    def __init__(
        self,
        config_context: Optional["ConfigContext"] = None,
        config_root: Optional[Path] = None,
        eager_load: bool = False,  # 🆕 控制是否立即加载
    ):
        """
        初始化延迟配置管理器
        
        Args:
            config_context: 配置上下文接口
            config_root: 配置根目录
            eager_load: 是否立即加载所有配置（默认延迟加载）
        """
        # 🚀 延迟初始化配置上下文
        self._config_context = config_context
        self._config_root = config_root
        
        # 🚀 延迟初始化的属性
        self._context = None
        self._config_dir = None
        self._data_dir = None
        self._logs_dir = None
        self._db_dir = None
        self._full_config = None  # 完整配置的延迟加载
        
        # 🚀 最小启动时配置
        self._core_paths = None  # 核心路径信息
        self._is_initialized = False
        
        logger.info("🚀 LazyConfigManager初始化 - 延迟加载模式")
        
        if eager_load:
            # 兼容模式：立即加载所有配置
            self._ensure_initialized()
            logger.info("⚡ 配置立即加载完成")

    @property
    def context(self) -> "ConfigContext":
        """延迟获取配置上下文"""
        if self._context is None:
            if self._config_context is not None:
                self._context = self._config_context
            else:
                from .config_context import create_config_context
                self._context = create_config_context(self._config_root)
            logger.debug("📂 配置上下文已加载")
        return self._context

    @property
    def config_dir(self) -> Path:
        """延迟获取配置目录"""
        if self._config_dir is None:
            self._config_dir = self.context.get_config_dir()
        return self._config_dir

    @property
    def data_dir(self) -> Path:
        """延迟获取数据目录"""
        if self._data_dir is None:
            self._data_dir = self.context.get_data_dir()
        return self._data_dir

    @property
    def logs_dir(self) -> Path:
        """延迟获取日志目录"""
        if self._logs_dir is None:
            self._logs_dir = self.context.get_logs_dir()
        return self._logs_dir

    @property
    def db_dir(self) -> Path:
        """延迟获取数据库目录"""
        if self._db_dir is None:
            self._db_dir = self.context.get_database_dir()
        return self._db_dir

    @property
    @lru_cache(maxsize=1)
    def config(self) -> "AppConfig":
        """延迟获取完整配置 - 使用LRU缓存"""
        if self._full_config is None:
            logger.debug("🔄 开始加载完整配置...")
            start_time = logger.debug and __import__('time').time()
            
            # 创建完整的CoreConfigManager来加载配置
            full_manager = CoreConfigManager(
                config_context=self.context,
                config_root=self._config_root
            )
            self._full_config = full_manager.config
            
            if hasattr(logger, 'isEnabledFor') and logger.isEnabledFor(logging.DEBUG) and start_time:
                end_time = __import__('time').time()
                logger.debug(f"✅ 完整配置加载完成，耗时: {(end_time - start_time) * 1000:.2f}ms")
        
        return self._full_config

    @lru_cache(maxsize=1)
    def get_core_paths(self) -> Dict[str, Path]:
        """获取核心路径 - 最小启动时需要的路径信息"""
        if self._core_paths is None:
            logger.debug("📍 加载核心路径信息...")
            
            # 仅加载启动时必需的路径
            self._core_paths = {
                "config": self.config_dir,
                "data": self.data_dir,
                "logs": self.logs_dir,
                "database": self.db_dir,
                "primary_config": self.config_dir / "app.yaml",
                "app_data": self.data_dir / "app_data",
            }
            
            logger.debug(f"✅ 核心路径加载完成: {len(self._core_paths)} 个路径")
        
        return self._core_paths

    def get_paths(self) -> Dict[str, Path]:
        """获取所有路径信息 - 兼容原API"""
        # 🚀 首先尝试返回核心路径（快速路径）
        try:
            return self.get_core_paths()
        except Exception:
            # 回退到完整配置加载
            logger.debug("核心路径加载失败，回退到完整配置")
            return self._get_full_paths()

    def _get_full_paths(self) -> Dict[str, Path]:
        """获取完整路径信息 - 需要完整配置的情况"""
        # 这里会触发完整配置加载
        config = self.config
        return {
            "config": self.config_dir,
            "data": self.data_dir,
            "logs": self.logs_dir,
            "database": self.db_dir,
            "primary_config": self.config_dir / "app.yaml",
            "app_data": self.data_dir / "app_data",
        }

    @lru_cache(maxsize=1)
    def get_server_config(self) -> "IPCServerConfig":
        """延迟获取服务器配置"""
        logger.debug("⚙️ 加载服务器配置...")
        return self.config.server

    @lru_cache(maxsize=1)
    def get_database_config(self) -> "DatabaseConfig":
        """延迟获取数据库配置"""
        logger.debug("🗄️ 加载数据库配置...")
        return self.config.database

    @lru_cache(maxsize=1)
    def get_storage_config(self) -> "StorageConfig":
        """延迟获取存储配置"""
        logger.debug("💾 加载存储配置...")
        return self.config.storage

    def validate_config(self) -> list:
        """验证配置 - 需要加载完整配置"""
        logger.debug("✅ 开始配置验证...")
        # 这里会触发完整配置加载
        config = self.config
        
        # 调用原配置管理器的验证逻辑
        if hasattr(config, 'validate'):
            return config.validate()
        
        # 基础验证
        errors = []
        if not config.app_name:
            errors.append("应用名称不能为空")
        
        logger.debug(f"配置验证完成，发现 {len(errors)} 个问题")
        return errors

    def _ensure_initialized(self):
        """确保配置已初始化 - 用于兼容性"""
        if not self._is_initialized:
            # 触发完整配置加载
            _ = self.config
            self._is_initialized = True
            logger.debug("✅ 配置初始化完成")

    def clear_cache(self):
        """清理配置缓存 - 调试和测试用"""
        self.config.cache_clear()
        self.get_core_paths.cache_clear()
        self.get_server_config.cache_clear()
        self.get_database_config.cache_clear()
        self.get_storage_config.cache_clear()
        
        self._full_config = None
        self._core_paths = None
        
        logger.info("🧹 配置缓存已清理")

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        return {
            "is_initialized": self._is_initialized,
            "full_config_loaded": self._full_config is not None,
            "core_paths_loaded": self._core_paths is not None,
            "cache_info": {
                "config": self.config.cache_info() if hasattr(self.config, 'cache_info') else None,
                "core_paths": self.get_core_paths.cache_info(),
                "server_config": self.get_server_config.cache_info(),
                "database_config": self.get_database_config.cache_info(),
                "storage_config": self.get_storage_config.cache_info(),
            }
        }


# 全局延迟配置管理器实例
_lazy_config_manager = None


def get_lazy_config_manager(**kwargs) -> LazyConfigManager:
    """获取全局延迟配置管理器实例"""
    global _lazy_config_manager
    
    if _lazy_config_manager is None:
        _lazy_config_manager = LazyConfigManager(**kwargs)
        logger.info("🚀 全局延迟配置管理器已创建")
    
    return _lazy_config_manager


def reset_lazy_config_manager():
    """重置全局延迟配置管理器 - 测试用"""
    global _lazy_config_manager
    
    if _lazy_config_manager:
        _lazy_config_manager.clear_cache()
    
    _lazy_config_manager = None
    logger.info("🔄 全局延迟配置管理器已重置")


# 兼容性函数 - 渐进式迁移
def create_optimized_config_manager(**kwargs) -> LazyConfigManager:
    """创建优化的配置管理器 - 替代CoreConfigManager"""
    return LazyConfigManager(**kwargs)