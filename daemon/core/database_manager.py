#!/usr/bin/env python3
"""
统一数据库管理器
替换分散的数据库Session操作，提供统一的事务管理和连接池
"""

import asyncio
import logging
import threading
from contextlib import asynccontextmanager, contextmanager
from functools import wraps
from typing import Any, Dict, Generator, Optional, Type, TypeVar, Union

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from .exception_handler import DatabaseError, handle_exceptions

logger = logging.getLogger(__name__)

T = TypeVar('T')


class DatabaseConfig:
    """数据库配置"""
    
    def __init__(
        self,
        database_url: str,
        async_database_url: str = None,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        echo: bool = False,
        enable_async: bool = False
    ):
        self.database_url = database_url
        self.async_database_url = async_database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.echo = echo
        self.enable_async = enable_async


class DatabaseManager:
    """统一数据库管理器
    
    功能特性:
    - 统一的连接池管理
    - 自动事务处理
    - 同步和异步支持
    - 连接健康检查
    - 性能监控
    - 异常处理集成
    """
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._engine = None
        self._async_engine = None
        self._session_factory = None
        self._async_session_factory = None
        self._lock = threading.Lock()
        
        # 统计信息
        self._stats = {
            "connections_created": 0,
            "connections_closed": 0,
            "transactions_committed": 0,
            "transactions_rolled_back": 0,
            "active_connections": 0,
            "failed_connections": 0
        }
        
        self._initialize_engines()
        
    def _initialize_engines(self):
        """初始化数据库引擎和会话工厂"""
        try:
            # 同步引擎
            self._engine = create_engine(
                self.config.database_url,
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                echo=self.config.echo,
                echo_pool=False,  # 避免连接池日志过多
            )
            
            # 添加连接事件监听器
            event.listen(self._engine, 'connect', self._on_connect)
            event.listen(self._engine, 'close', self._on_close)
            
            # 同步会话工厂
            self._session_factory = sessionmaker(
                bind=self._engine,
                expire_on_commit=False,
                autocommit=False,
                autoflush=True
            )
            
            logger.info(f"同步数据库引擎初始化完成: {self.config.database_url}")
            
            # 异步引擎（如果启用）
            if self.config.enable_async and self.config.async_database_url:
                self._async_engine = create_async_engine(
                    self.config.async_database_url,
                    pool_size=self.config.pool_size,
                    max_overflow=self.config.max_overflow,
                    pool_timeout=self.config.pool_timeout,
                    pool_recycle=self.config.pool_recycle,
                    echo=self.config.echo
                )
                
                self._async_session_factory = async_sessionmaker(
                    self._async_engine,
                    expire_on_commit=False,
                    autocommit=False,
                    autoflush=True
                )
                
                logger.info(f"异步数据库引擎初始化完成: {self.config.async_database_url}")
                
        except Exception as e:
            logger.error(f"数据库引擎初始化失败: {e}")
            raise DatabaseError(f"数据库初始化失败: {e}", "DB_INIT_ERROR")
    
    def _on_connect(self, dbapi_connection, connection_record):
        """连接建立事件处理"""
        with self._lock:
            self._stats["connections_created"] += 1
            self._stats["active_connections"] += 1
        logger.debug("数据库连接已建立")
    
    def _on_close(self, dbapi_connection, connection_record):
        """连接关闭事件处理"""
        with self._lock:
            self._stats["connections_closed"] += 1
            self._stats["active_connections"] -= 1
        logger.debug("数据库连接已关闭")
    
    @contextmanager
    @handle_exceptions("database_session", reraise=True)
    def get_session(self) -> Generator[Session, None, None]:
        """获取数据库会话（上下文管理器）"""
        if not self._session_factory:
            raise DatabaseError("数据库会话工厂未初始化", "SESSION_FACTORY_ERROR")
        
        session = self._session_factory()
        try:
            logger.debug("创建数据库会话")
            yield session
            session.commit()
            
            with self._lock:
                self._stats["transactions_committed"] += 1
            logger.debug("数据库事务已提交")
            
        except Exception as e:
            session.rollback()
            with self._lock:
                self._stats["transactions_rolled_back"] += 1
            
            logger.error(f"数据库事务回滚: {e}")
            raise DatabaseError(f"数据库操作失败: {e}", "TRANSACTION_ERROR")
        finally:
            session.close()
            logger.debug("数据库会话已关闭")
    
    @asynccontextmanager
    @handle_exceptions("async_database_session", reraise=True)
    async def get_async_session(self) -> AsyncSession:
        """获取异步数据库会话（异步上下文管理器）"""
        if not self._async_session_factory:
            raise DatabaseError("异步数据库会话工厂未初始化", "ASYNC_SESSION_FACTORY_ERROR")
        
        async with self._async_session_factory() as session:
            try:
                logger.debug("创建异步数据库会话")
                yield session
                await session.commit()
                
                with self._lock:
                    self._stats["transactions_committed"] += 1
                logger.debug("异步数据库事务已提交")
                
            except Exception as e:
                await session.rollback()
                with self._lock:
                    self._stats["transactions_rolled_back"] += 1
                
                logger.error(f"异步数据库事务回滚: {e}")
                raise DatabaseError(f"异步数据库操作失败: {e}", "ASYNC_TRANSACTION_ERROR")
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> Any:
        """执行查询"""
        with self.get_session() as session:
            result = session.execute(query, params or {})
            return result.fetchall()
    
    async def execute_query_async(self, query: str, params: Dict[str, Any] = None) -> Any:
        """执行异步查询"""
        async with self.get_async_session() as session:
            result = await session.execute(query, params or {})
            return result.fetchall()
    
    @handle_exceptions("database_health_check", reraise=True)
    def health_check(self) -> Dict[str, Any]:
        """数据库健康检查"""
        try:
            with self.get_session() as session:
                # 执行简单查询测试连接
                result = session.execute("SELECT 1").fetchone()
                
                pool = self._engine.pool
                pool_status = {
                    "pool_size": pool.size(),
                    "checked_in": pool.checkedin(),
                    "checked_out": pool.checkedout(),
                    "overflow": pool.overflow(),
                    "invalid": pool.invalid()
                }
                
                return {
                    "healthy": True,
                    "connection_test": result[0] == 1,
                    "pool_status": pool_status,
                    "stats": self.get_stats()
                }
                
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            with self._lock:
                self._stats["failed_connections"] += 1
            
            return {
                "healthy": False,
                "error": str(e),
                "stats": self.get_stats()
            }
    
    async def health_check_async(self) -> Dict[str, Any]:
        """异步数据库健康检查"""
        if not self.config.enable_async:
            return {"healthy": False, "error": "异步支持未启用"}
        
        try:
            async with self.get_async_session() as session:
                result = await session.execute("SELECT 1")
                row = result.fetchone()
                
                return {
                    "healthy": True,
                    "connection_test": row[0] == 1,
                    "async_enabled": True,
                    "stats": self.get_stats()
                }
                
        except Exception as e:
            logger.error(f"异步数据库健康检查失败: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "async_enabled": True,
                "stats": self.get_stats()
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        with self._lock:
            return self._stats.copy()
    
    def reset_stats(self):
        """重置统计信息"""
        with self._lock:
            self._stats = {key: 0 for key in self._stats}
        logger.info("数据库统计信息已重置")
    
    def close(self):
        """关闭数据库连接"""
        logger.info("开始关闭数据库连接...")
        
        try:
            if self._engine:
                self._engine.dispose()
                logger.info("同步数据库引擎已关闭")
            
            if self._async_engine:
                # 异步引擎需要在事件循环中关闭
                asyncio.create_task(self._async_engine.dispose())
                logger.info("异步数据库引擎关闭任务已创建")
                
        except Exception as e:
            logger.error(f"关闭数据库连接时出错: {e}")
        
        logger.info("数据库连接关闭完成")
    
    async def close_async(self):
        """异步关闭数据库连接"""
        logger.info("开始异步关闭数据库连接...")
        
        try:
            if self._async_engine:
                await self._async_engine.dispose()
                logger.info("异步数据库引擎已关闭")
            
            if self._engine:
                self._engine.dispose()
                logger.info("同步数据库引擎已关闭")
                
        except Exception as e:
            logger.error(f"异步关闭数据库连接时出错: {e}")
        
        logger.info("异步数据库连接关闭完成")


# 装饰器支持
def with_database_session(manager: DatabaseManager):
    """数据库会话装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with manager.get_session() as session:
                return func(session, *args, **kwargs)
        return wrapper
    return decorator


def with_async_database_session(manager: DatabaseManager):
    """异步数据库会话装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with manager.get_async_session() as session:
                return await func(session, *args, **kwargs)
        return wrapper
    return decorator


# 全局数据库管理器（延迟初始化）
_global_database_manager: Optional[DatabaseManager] = None


def initialize_database_manager(config: DatabaseConfig) -> DatabaseManager:
    """初始化全局数据库管理器"""
    global _global_database_manager
    
    if _global_database_manager:
        logger.warning("数据库管理器已初始化，将关闭现有实例")
        _global_database_manager.close()
    
    _global_database_manager = DatabaseManager(config)
    logger.info("全局数据库管理器初始化完成")
    return _global_database_manager


def get_database_manager() -> DatabaseManager:
    """获取全局数据库管理器"""
    if not _global_database_manager:
        raise DatabaseError("数据库管理器未初始化，请先调用 initialize_database_manager()", "MANAGER_NOT_INITIALIZED")
    
    return _global_database_manager


# 便捷函数
def get_database_session():
    """获取数据库会话的便捷函数"""
    return get_database_manager().get_session()


def get_async_database_session():
    """获取异步数据库会话的便捷函数"""  
    return get_database_manager().get_async_session()


if __name__ == "__main__":
    # 测试数据库管理器
    logging.basicConfig(level=logging.INFO)
    
    # 创建测试配置
    config = DatabaseConfig(
        database_url="sqlite:///test.db",
        pool_size=5,
        echo=False
    )
    
    # 初始化管理器
    manager = DatabaseManager(config)
    
    # 测试健康检查
    health = manager.health_check()
    print(f"数据库健康检查: {health}")
    
    # 测试会话
    with manager.get_session() as session:
        result = session.execute("SELECT 'Hello Database!' as message").fetchone()
        print(f"查询结果: {result[0]}")
    
    # 查看统计信息
    stats = manager.get_stats()
    print(f"数据库统计: {stats}")
    
    # 关闭
    manager.close()