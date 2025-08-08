#!/usr/bin/env python3
"""
高性能SQLite连接池服务
专为大规模数据查询优化，支持读写分离和智能负载均衡
"""

import asyncio
import logging
import sqlite3
import threading
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from queue import Queue
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)


@dataclass
class ConnectionPoolMetrics:
    """连接池性能指标"""

    total_connections: int
    active_connections: int
    idle_connections: int
    read_connections: int
    write_connections: int
    total_queries: int
    avg_query_time_ms: float
    connection_wait_time_ms: float
    pool_utilization: float


class HighPerformanceConnectionPool:
    """高性能SQLite连接池

    特性：
    - 读写分离连接池
    - 智能负载均衡
    - 连接预热和回收
    - 查询性能监控
    - 自适应连接数调整
    """

    def __init__(
        self,
        database_path: str,
        read_pool_size: int = 8,
        write_pool_size: int = 2,
        max_overflow: int = 4,
        pool_timeout: int = 30,
        enable_wal: bool = True,
    ):
        self.database_path = Path(database_path)
        self.read_pool_size = read_pool_size
        self.write_pool_size = write_pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.enable_wal = enable_wal

        # 创建读写分离的数据库URL
        self.read_db_url = f"sqlite:///{self.database_path}"
        self.write_db_url = f"sqlite:///{self.database_path}"

        # 读写分离的连接池
        self.read_engine: Optional[Engine] = None
        self.write_engine: Optional[Engine] = None
        self.read_session_factory = None
        self.write_session_factory = None

        # 性能监控
        self.metrics = ConnectionPoolMetrics(
            total_connections=0,
            active_connections=0,
            idle_connections=0,
            read_connections=0,
            write_connections=0,
            total_queries=0,
            avg_query_time_ms=0.0,
            connection_wait_time_ms=0.0,
            pool_utilization=0.0,
        )

        # 查询统计
        self.query_times: List[float] = []
        self.connection_wait_times: List[float] = []
        self._stats_lock = threading.Lock()

        # 初始化连接池
        self._initialize_pools()

    def _initialize_pools(self):
        """初始化读写分离连接池"""

        def configure_sqlite_connection(dbapi_connection, connection_record):
            """SQLite连接优化配置"""
            # 针对大规模数据的激进优化
            dbapi_connection.execute("PRAGMA cache_size = -256000")  # 256MB缓存
            dbapi_connection.execute("PRAGMA temp_store = MEMORY")
            dbapi_connection.execute("PRAGMA mmap_size = 1073741824")  # 1GB内存映射
            dbapi_connection.execute("PRAGMA synchronous = NORMAL")
            dbapi_connection.execute("PRAGMA optimize")

            if self.enable_wal:
                dbapi_connection.execute("PRAGMA journal_mode = WAL")
                dbapi_connection.execute("PRAGMA wal_autocheckpoint = 5000")

            # 查询优化
            dbapi_connection.execute("PRAGMA analysis_limit = 5000")
            dbapi_connection.execute("PRAGMA automatic_index = OFF")

        # 创建读连接池 - 优化并发读取
        self.read_engine = create_engine(
            self.read_db_url,
            poolclass=QueuePool,
            pool_size=self.read_pool_size,
            max_overflow=self.max_overflow,
            pool_timeout=self.pool_timeout,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False,
            connect_args={
                "check_same_thread": False,
                "timeout": 30,
                "isolation_level": None,  # 自动提交模式用于读取
            },
        )

        # 创建写连接池 - 保证事务一致性
        self.write_engine = create_engine(
            self.write_db_url,
            poolclass=QueuePool,
            pool_size=self.write_pool_size,
            max_overflow=2,  # 写操作溢出较少
            pool_timeout=self.pool_timeout,
            pool_pre_ping=True,
            pool_recycle=1800,  # 写连接更频繁回收
            echo=False,
            connect_args={
                "check_same_thread": False,
                "timeout": 60,  # 写操作允许更长超时
            },
        )

        # 配置连接优化
        event.listen(self.read_engine, "connect", configure_sqlite_connection)
        event.listen(self.write_engine, "connect", configure_sqlite_connection)

        # 创建Session工厂
        self.read_session_factory = sessionmaker(
            bind=self.read_engine, autocommit=False, autoflush=False
        )

        self.write_session_factory = sessionmaker(
            bind=self.write_engine, autocommit=False, autoflush=False
        )

        logger.info(
            f"高性能连接池初始化完成 - "
            f"读连接池: {self.read_pool_size}, 写连接池: {self.write_pool_size}"
        )

    @asynccontextmanager
    async def get_read_session(self):
        """获取只读Session - 优化并发读取性能"""
        start_time = time.time()
        session = self.read_session_factory()

        try:
            # 记录连接等待时间
            wait_time = (time.time() - start_time) * 1000
            with self._stats_lock:
                self.connection_wait_times.append(wait_time)
                self.metrics.read_connections += 1

            yield session

        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
            with self._stats_lock:
                self.metrics.read_connections -= 1

    @asynccontextmanager
    async def get_write_session(self):
        """获取读写Session - 保证事务一致性"""
        start_time = time.time()
        session = self.write_session_factory()

        try:
            # 记录连接等待时间
            wait_time = (time.time() - start_time) * 1000
            with self._stats_lock:
                self.connection_wait_times.append(wait_time)
                self.metrics.write_connections += 1

            yield session
            session.commit()

        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
            with self._stats_lock:
                self.metrics.write_connections -= 1

    async def execute_optimized_query(
        self, query: str, params: Optional[Dict] = None, read_only: bool = True
    ) -> List[Dict[str, Any]]:
        """执行优化查询 - 自动选择最佳连接池"""
        start_time = time.time()

        try:
            session_manager = (
                self.get_read_session() if read_only else self.get_write_session()
            )

            async with session_manager as session:
                result = session.execute(text(query), params or {})

                if read_only:
                    # 只读查询返回结果
                    rows = result.fetchall()
                    return [dict(row._mapping) for row in rows]
                else:
                    # 写操作返回影响行数
                    return [{"affected_rows": result.rowcount}]

        finally:
            # 记录查询时间
            query_time = (time.time() - start_time) * 1000
            with self._stats_lock:
                self.query_times.append(query_time)
                self.metrics.total_queries += 1

    async def batch_execute(
        self,
        queries: List[tuple],  # [(query, params), ...]
        read_only: bool = True,
        batch_size: int = 100,
    ) -> List[List[Dict[str, Any]]]:
        """批量执行查询 - 优化大批量操作性能"""
        results = []

        for i in range(0, len(queries), batch_size):
            batch = queries[i : i + batch_size]
            batch_results = []

            session_manager = (
                self.get_read_session() if read_only else self.get_write_session()
            )

            async with session_manager as session:
                for query, params in batch:
                    result = session.execute(text(query), params or {})

                    if read_only:
                        rows = result.fetchall()
                        batch_results.append([dict(row._mapping) for row in rows])
                    else:
                        batch_results.append([{"affected_rows": result.rowcount}])

            results.extend(batch_results)

            # 批次间短暂休息，避免锁定数据库
            if not read_only and i + batch_size < len(queries):
                await asyncio.sleep(0.001)

        return results

    async def warm_up_connections(self):
        """预热连接池 - 提前建立连接减少首次查询延迟"""
        logger.info("开始预热连接池...")

        tasks = []

        # 预热读连接
        for _ in range(self.read_pool_size):
            tasks.append(self._warm_up_read_connection())

        # 预热写连接
        for _ in range(self.write_pool_size):
            tasks.append(self._warm_up_write_connection())

        await asyncio.gather(*tasks)
        logger.info("连接池预热完成")

    async def _warm_up_read_connection(self):
        """预热单个读连接"""
        try:
            async with self.get_read_session() as session:
                session.execute(text("SELECT 1"))
        except Exception as e:
            logger.warning(f"预热读连接失败: {e}")

    async def _warm_up_write_connection(self):
        """预热单个写连接"""
        try:
            async with self.get_write_session() as session:
                session.execute(text("SELECT 1"))
        except Exception as e:
            logger.warning(f"预热写连接失败: {e}")

    def get_pool_metrics(self) -> ConnectionPoolMetrics:
        """获取连接池性能指标"""
        with self._stats_lock:
            if self.query_times:
                self.metrics.avg_query_time_ms = sum(self.query_times[-1000:]) / len(
                    self.query_times[-1000:]
                )

            if self.connection_wait_times:
                self.metrics.connection_wait_time_ms = sum(
                    self.connection_wait_times[-1000:]
                ) / len(self.connection_wait_times[-1000:])

            # 更新连接池状态
            self.metrics.total_connections = (
                self.read_engine.pool.size() + self.write_engine.pool.size()
                if self.read_engine and self.write_engine
                else 0
            )

            self.metrics.pool_utilization = (
                self.metrics.read_connections + self.metrics.write_connections
            ) / max(self.metrics.total_connections, 1)

        return self.metrics

    async def optimize_pool_size(self):
        """自适应连接池大小优化"""
        metrics = self.get_pool_metrics()

        # 如果连接池利用率过高且等待时间长，建议增加连接数
        if metrics.pool_utilization > 0.8 and metrics.connection_wait_time_ms > 10:
            if self.read_pool_size < 16:
                logger.info("检测到高负载，建议增加读连接池大小")
            if self.write_pool_size < 4 and metrics.write_connections > 0:
                logger.info("检测到写操作瓶颈，建议增加写连接池大小")

        # 如果利用率长期过低，建议减少连接数节省资源
        elif metrics.pool_utilization < 0.3:
            logger.info("连接池利用率较低，可考虑减少连接数节省资源")

    async def health_check(self) -> Dict[str, Any]:
        """连接池健康检查"""
        try:
            read_check = await self._health_check_pool(self.get_read_session())
            write_check = await self._health_check_pool(self.get_write_session())

            return {
                "status": "healthy" if read_check and write_check else "unhealthy",
                "read_pool_healthy": read_check,
                "write_pool_healthy": write_check,
                "metrics": self.get_pool_metrics().__dict__,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _health_check_pool(self, session_manager) -> bool:
        """检查单个连接池健康状态"""
        try:
            async with session_manager as session:
                result = session.execute(text("SELECT 1 as health_check"))
                return result.fetchone()[0] == 1
        except Exception as e:
            logger.error(f"连接池健康检查失败: {e}")
            return False

    async def cleanup(self):
        """清理连接池资源"""
        try:
            if self.read_engine:
                self.read_engine.dispose()
            if self.write_engine:
                self.write_engine.dispose()
            logger.info("高性能连接池资源清理完成")
        except Exception as e:
            logger.error(f"连接池清理失败: {e}")


# 全局连接池实例
_connection_pool: Optional[HighPerformanceConnectionPool] = None


async def get_connection_pool() -> HighPerformanceConnectionPool:
    """获取全局连接池实例"""
    global _connection_pool
    if _connection_pool is None:
        from config.core_config import get_database_config

        db_config = get_database_config()
        database_path = db_config.sqlite_url.replace("sqlite:///", "")

        _connection_pool = HighPerformanceConnectionPool(
            database_path=database_path,
            read_pool_size=8,
            write_pool_size=2,
            max_overflow=4,
            pool_timeout=30,
            enable_wal=True,
        )

        # 预热连接池
        await _connection_pool.warm_up_connections()

    return _connection_pool


async def cleanup_connection_pool():
    """清理全局连接池"""
    global _connection_pool
    if _connection_pool:
        await _connection_pool.cleanup()
        _connection_pool = None
