#!/usr/bin/env python3
"""
IPC连接池管理器 - P0性能优化
支持动态扩展、连接复用、负载均衡
"""

import asyncio
import logging
import time
import weakref
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """连接状态"""
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    CLOSED = "closed"


@dataclass
class ConnectionMetrics:
    """连接性能指标"""
    created_at: float
    last_used_at: float
    request_count: int = 0
    error_count: int = 0
    total_response_time: float = 0.0
    
    @property
    def avg_response_time(self) -> float:
        return self.total_response_time / max(self.request_count, 1)
    
    @property
    def error_rate(self) -> float:
        return self.error_count / max(self.request_count, 1)


class IPCConnection:
    """IPC连接封装"""
    
    def __init__(self, connection_id: str, handler: Callable):
        self.id = connection_id
        self.handler = handler
        self.state = ConnectionState.IDLE
        self.metrics = ConnectionMetrics(
            created_at=time.time(),
            last_used_at=time.time()
        )
        self._lock = asyncio.Lock()
        self._current_task: Optional[asyncio.Task] = None

    async def execute_request(self, method: str, path: str, data: Any = None) -> Any:
        """执行请求"""
        async with self._lock:
            if self.state == ConnectionState.ERROR:
                raise RuntimeError(f"连接 {self.id} 处于错误状态")
            
            self.state = ConnectionState.BUSY
            start_time = time.time()
            
            try:
                # 执行实际请求
                result = await self.handler(method, path, data)
                
                # 更新性能指标
                response_time = time.time() - start_time
                self.metrics.request_count += 1
                self.metrics.total_response_time += response_time
                self.metrics.last_used_at = time.time()
                
                self.state = ConnectionState.IDLE
                return result
                
            except Exception as e:
                self.metrics.error_count += 1
                self.state = ConnectionState.ERROR
                logger.error(f"连接 {self.id} 请求失败: {e}")
                raise
    
    def close(self):
        """关闭连接"""
        self.state = ConnectionState.CLOSED
        if self._current_task:
            self._current_task.cancel()
        logger.debug(f"连接 {self.id} 已关闭")


class DynamicConnectionPool:
    """动态IPC连接池
    
    🚀 核心优化特性:
    - 动态扩展：根据负载自动调整连接数
    - 连接复用：高效的连接生命周期管理
    - 负载均衡：智能请求分发
    - 性能监控：实时连接性能指标
    """
    
    def __init__(
        self,
        min_connections: int = 2,
        max_connections: int = 20,
        connection_factory: Callable = None,
        idle_timeout: float = 300.0,  # 5分钟空闲超时
        scale_threshold: float = 0.8,  # 80%使用率时扩展
    ):
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.connection_factory = connection_factory
        self.idle_timeout = idle_timeout
        self.scale_threshold = scale_threshold
        
        # 连接管理
        self._connections: Dict[str, IPCConnection] = {}
        self._idle_connections: deque[str] = deque()
        self._active_connections: Set[str] = set()
        
        # 性能监控
        self._total_requests = 0
        self._total_errors = 0
        self._pool_metrics_start = time.time()
        
        # 同步控制
        self._pool_lock = asyncio.Lock()
        self._expansion_lock = asyncio.Lock()
        
        # 监控任务
        self._monitor_task: Optional[asyncio.Task] = None
        self._is_running = False
        
        logger.info(f"🏊 动态连接池初始化 - 范围: {min_connections}-{max_connections}")

    async def start(self):
        """启动连接池"""
        async with self._pool_lock:
            if self._is_running:
                return
            
            logger.info("🚀 启动动态连接池...")
            
            # 创建初始连接
            for i in range(self.min_connections):
                await self._create_connection(f"conn_{i}")
            
            # 启动监控任务
            self._monitor_task = asyncio.create_task(self._monitor_pool())
            self._is_running = True
            
            logger.info(f"✅ 连接池启动完成，初始连接数: {len(self._connections)}")

    async def stop(self):
        """停止连接池"""
        async with self._pool_lock:
            if not self._is_running:
                return
            
            logger.info("🛑 停止动态连接池...")
            self._is_running = False
            
            # 取消监控任务
            if self._monitor_task:
                self._monitor_task.cancel()
                try:
                    await self._monitor_task
                except asyncio.CancelledError:
                    pass
            
            # 关闭所有连接
            for connection in list(self._connections.values()):
                connection.close()
            
            self._connections.clear()
            self._idle_connections.clear()
            self._active_connections.clear()
            
            logger.info("✅ 连接池已停止")

    @asynccontextmanager
    async def get_connection(self):
        """获取连接的异步上下文管理器"""
        connection = await self._acquire_connection()
        try:
            yield connection
        finally:
            await self._release_connection(connection.id)

    async def _acquire_connection(self) -> IPCConnection:
        """获取连接"""
        async with self._pool_lock:
            # 尝试获取空闲连接
            if self._idle_connections:
                connection_id = self._idle_connections.popleft()
                connection = self._connections[connection_id]
                self._active_connections.add(connection_id)
                connection.state = ConnectionState.ACTIVE
                logger.debug(f"📡 复用连接: {connection_id}")
                return connection
            
            # 检查是否需要扩展连接池
            if len(self._connections) < self.max_connections:
                connection_id = f"conn_{len(self._connections)}"
                await self._create_connection(connection_id)
                connection = self._connections[connection_id]
                self._active_connections.add(connection_id)
                connection.state = ConnectionState.ACTIVE
                logger.info(f"🆕 创建新连接: {connection_id}")
                return connection
            
            # 连接池已满，等待连接释放
            logger.warning("⏳ 连接池已满，等待连接释放...")
            while not self._idle_connections and self._is_running:
                await asyncio.sleep(0.01)  # 10ms检查间隔
            
            if not self._is_running:
                raise RuntimeError("连接池已停止")
            
            # 递归获取连接
            return await self._acquire_connection()

    async def _release_connection(self, connection_id: str):
        """释放连接"""
        async with self._pool_lock:
            if connection_id not in self._connections:
                return
            
            connection = self._connections[connection_id]
            
            if connection.state == ConnectionState.ERROR:
                # 移除错误连接
                await self._remove_connection(connection_id)
                # 如果连接数低于最小值，创建新连接
                if len(self._connections) < self.min_connections:
                    new_id = f"conn_{int(time.time() * 1000) % 10000}"
                    await self._create_connection(new_id)
                return
            
            # 将连接返回空闲池
            self._active_connections.discard(connection_id)
            self._idle_connections.append(connection_id)
            connection.state = ConnectionState.IDLE
            logger.debug(f"🔄 释放连接: {connection_id}")

    async def _create_connection(self, connection_id: str):
        """创建新连接"""
        if self.connection_factory is None:
            raise RuntimeError("连接工厂未设置")
        
        try:
            handler = await self.connection_factory()
            connection = IPCConnection(connection_id, handler)
            self._connections[connection_id] = connection
            self._idle_connections.append(connection_id)
            logger.debug(f"✨ 连接已创建: {connection_id}")
            
        except Exception as e:
            logger.error(f"❌ 创建连接失败 {connection_id}: {e}")
            raise

    async def _remove_connection(self, connection_id: str):
        """移除连接"""
        if connection_id in self._connections:
            connection = self._connections[connection_id]
            connection.close()
            del self._connections[connection_id]
            
            self._active_connections.discard(connection_id)
            try:
                self._idle_connections.remove(connection_id)
            except ValueError:
                pass  # 连接可能不在空闲队列中
            
            logger.debug(f"🗑️ 连接已移除: {connection_id}")

    async def _monitor_pool(self):
        """监控连接池状态"""
        logger.info("👁️ 连接池监控任务启动")
        
        try:
            while self._is_running:
                await asyncio.sleep(30)  # 30秒监控间隔
                
                current_time = time.time()
                
                # 清理空闲超时的连接
                expired_connections = []
                for connection_id in list(self._idle_connections):
                    connection = self._connections[connection_id]
                    if current_time - connection.metrics.last_used_at > self.idle_timeout:
                        if len(self._connections) > self.min_connections:
                            expired_connections.append(connection_id)
                
                for connection_id in expired_connections:
                    await self._remove_connection(connection_id)
                    logger.info(f"⏰ 移除超时空闲连接: {connection_id}")
                
                # 输出监控统计
                stats = await self.get_stats()
                logger.debug(f"📊 连接池状态: {stats}")
                
        except asyncio.CancelledError:
            logger.info("👁️ 连接池监控任务已取消")
        except Exception as e:
            logger.error(f"❌ 连接池监控异常: {e}")

    async def get_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息"""
        current_time = time.time()
        uptime = current_time - self._pool_metrics_start
        
        # 计算连接指标
        total_requests = sum(conn.metrics.request_count for conn in self._connections.values())
        total_errors = sum(conn.metrics.error_count for conn in self._connections.values())
        avg_response_time = sum(conn.metrics.avg_response_time for conn in self._connections.values()) / max(len(self._connections), 1)
        
        return {
            "pool_status": {
                "is_running": self._is_running,
                "uptime_seconds": uptime,
                "total_connections": len(self._connections),
                "idle_connections": len(self._idle_connections),
                "active_connections": len(self._active_connections),
                "utilization_rate": len(self._active_connections) / max(len(self._connections), 1),
            },
            "performance": {
                "total_requests": total_requests,
                "total_errors": total_errors,
                "error_rate": total_errors / max(total_requests, 1),
                "avg_response_time_ms": avg_response_time * 1000,
                "requests_per_second": total_requests / max(uptime, 1),
            },
            "configuration": {
                "min_connections": self.min_connections,
                "max_connections": self.max_connections,
                "idle_timeout": self.idle_timeout,
                "scale_threshold": self.scale_threshold,
            },
            "connections": {
                conn_id: {
                    "state": conn.state.value,
                    "request_count": conn.metrics.request_count,
                    "error_count": conn.metrics.error_count,
                    "avg_response_time_ms": conn.metrics.avg_response_time * 1000,
                    "last_used_ago": current_time - conn.metrics.last_used_at,
                }
                for conn_id, conn in self._connections.items()
            }
        }

    def set_connection_factory(self, factory: Callable):
        """设置连接工厂"""
        self.connection_factory = factory
        logger.info("🏭 连接工厂已设置")

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        stats = await self.get_stats()
        
        # 健康检查标准
        is_healthy = (
            stats["pool_status"]["is_running"] and
            stats["pool_status"]["total_connections"] >= self.min_connections and
            stats["performance"]["error_rate"] < 0.1  # 错误率<10%
        )
        
        return {
            "healthy": is_healthy,
            "timestamp": time.time(),
            "stats": stats,
            "checks": {
                "pool_running": stats["pool_status"]["is_running"],
                "min_connections_met": stats["pool_status"]["total_connections"] >= self.min_connections,
                "low_error_rate": stats["performance"]["error_rate"] < 0.1,
            }
        }


# 全局连接池实例
_global_connection_pool: Optional[DynamicConnectionPool] = None


def get_connection_pool() -> DynamicConnectionPool:
    """获取全局连接池实例"""
    global _global_connection_pool
    
    if _global_connection_pool is None:
        _global_connection_pool = DynamicConnectionPool()
        logger.info("🌍 全局连接池已创建")
    
    return _global_connection_pool


async def initialize_connection_pool(**kwargs) -> DynamicConnectionPool:
    """初始化全局连接池"""
    pool = get_connection_pool()
    
    # 更新配置
    for key, value in kwargs.items():
        if hasattr(pool, key):
            setattr(pool, key, value)
    
    await pool.start()
    return pool


async def cleanup_connection_pool():
    """清理全局连接池"""
    global _global_connection_pool
    
    if _global_connection_pool:
        await _global_connection_pool.stop()
        _global_connection_pool = None
        logger.info("🧹 全局连接池已清理")