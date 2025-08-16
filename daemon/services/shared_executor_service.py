#!/usr/bin/env python3
"""
共享线程池服务 - 消除6个重复ThreadPoolExecutor实现
统一管理IO、CPU、ML任务的线程池资源
"""

import asyncio
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Union
import queue
import os

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """任务类型枚举"""
    IO = "io"                    # IO密集型任务 (文件读写、网络请求)
    CPU = "cpu"                  # CPU密集型任务 (计算、数据处理)  
    ML = "ml"                    # 机器学习任务 (模型推理、训练)
    DATABASE = "database"        # 数据库操作
    COMPRESSION = "compression"  # 压缩/解压缩
    CRYPTO = "crypto"           # 加密/解密操作
    GENERAL = "general"         # 通用任务


class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class TaskInfo:
    """任务信息"""
    task_id: str
    task_type: TaskType
    priority: TaskPriority
    submitted_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    executor_name: str = ""
    duration_seconds: float = 0.0
    success: bool = True
    error: Optional[str] = None


@dataclass
class ExecutorStats:
    """执行器统计信息"""
    name: str
    task_type: TaskType
    max_workers: int
    active_tasks: int = 0
    queued_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_execution_time: float = 0.0
    avg_execution_time: float = 0.0
    peak_active_tasks: int = 0
    last_task_time: Optional[datetime] = None


@dataclass
class SystemStats:
    """系统统计信息"""
    total_executors: int = 0
    total_active_tasks: int = 0
    total_completed_tasks: int = 0
    total_failed_tasks: int = 0
    system_load: float = 0.0
    memory_usage_mb: float = 0.0
    uptime_seconds: float = 0.0


class PriorityQueue:
    """优先级任务队列"""
    
    def __init__(self):
        self._queue = queue.PriorityQueue()
        self._lock = threading.Lock()
        self._task_counter = 0
    
    def put(self, priority: TaskPriority, task: Callable, task_id: str):
        """添加任务到优先级队列"""
        with self._lock:
            self._task_counter += 1
            # 使用负优先级值来实现高优先级先执行
            priority_value = -priority.value
            item = (priority_value, self._task_counter, task, task_id)
            self._queue.put(item)
    
    def get(self):
        """获取下一个任务"""
        priority_value, counter, task, task_id = self._queue.get()
        return task, task_id
    
    def qsize(self):
        """获取队列大小"""
        return self._queue.qsize()
    
    def empty(self):
        """检查队列是否为空"""
        return self._queue.empty()


class SharedExecutorService:
    """共享线程池服务 - 消除6个重复ThreadPoolExecutor实现"""
    
    def __init__(
        self,
        io_workers: int = 8,           # IO密集型任务
        cpu_workers: int = 4,          # CPU密集型任务  
        ml_workers: int = 2,           # ML任务
        database_workers: int = 4,     # 数据库任务
        compression_workers: int = 2,  # 压缩任务
        crypto_workers: int = 2,       # 加密任务
        enable_monitoring: bool = True,
        task_timeout: int = 300        # 任务超时(秒)
    ):
        # 自动调整工作线程数量
        if cpu_workers == 4:  # 使用默认值时自动调整
            cpu_workers = max(2, os.cpu_count() or 4)
        
        # 创建专用线程池
        self.executors: Dict[TaskType, ThreadPoolExecutor] = {
            TaskType.IO: ThreadPoolExecutor(max_workers=io_workers, thread_name_prefix="io"),
            TaskType.CPU: ThreadPoolExecutor(max_workers=cpu_workers, thread_name_prefix="cpu"),
            TaskType.ML: ThreadPoolExecutor(max_workers=ml_workers, thread_name_prefix="ml"),
            TaskType.DATABASE: ThreadPoolExecutor(max_workers=database_workers, thread_name_prefix="db"),
            TaskType.COMPRESSION: ThreadPoolExecutor(max_workers=compression_workers, thread_name_prefix="compress"),
            TaskType.CRYPTO: ThreadPoolExecutor(max_workers=crypto_workers, thread_name_prefix="crypto"),
            TaskType.GENERAL: ThreadPoolExecutor(max_workers=io_workers, thread_name_prefix="general"),
        }
        
        # 统计信息
        self.executor_stats: Dict[TaskType, ExecutorStats] = {}
        for task_type, executor in self.executors.items():
            self.executor_stats[task_type] = ExecutorStats(
                name=f"{task_type.value}_executor",
                task_type=task_type,
                max_workers=executor._max_workers
            )
        
        self.system_stats = SystemStats(
            total_executors=len(self.executors),
            uptime_seconds=0.0
        )
        
        # 任务追踪
        self.active_tasks: Dict[str, TaskInfo] = {}
        self.completed_tasks: List[TaskInfo] = []
        self.task_counter = 0
        self.task_timeout = task_timeout
        
        # 监控和清理
        self.enable_monitoring = enable_monitoring
        self._start_time = time.time()
        self._monitor_task = None
        self._cleanup_task = None
        self._shutdown_event = threading.Event()
        
        # 优先级队列 (未来扩展)
        self._priority_queues: Dict[TaskType, PriorityQueue] = {
            task_type: PriorityQueue() for task_type in TaskType
        }
        
        logger.info(f"🚀 SharedExecutorService 初始化完成")
        logger.info(f"   IO工作者: {io_workers}, CPU工作者: {cpu_workers}")
        logger.info(f"   ML工作者: {ml_workers}, 数据库工作者: {database_workers}")
        
        # 启动监控 (延迟到事件循环可用时)
        if self.enable_monitoring:
            self._monitoring_enabled = True
        else:
            self._monitoring_enabled = False

    async def _ensure_monitoring_started(self):
        """确保监控已启动（如果启用）"""
        if self._monitoring_enabled and self._monitor_task is None:
            try:
                self._start_monitoring()
            except Exception as e:
                logger.warning(f"启动监控失败: {e}")

    async def submit(
        self,
        task: Callable,
        task_type: TaskType = TaskType.GENERAL,
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: Optional[int] = None,
        *args,
        **kwargs
    ) -> Any:
        """提交任务到适当的线程池"""
        
        # 确保监控已启动
        await self._ensure_monitoring_started()
        
        task_id = self._generate_task_id()
        task_info = TaskInfo(
            task_id=task_id,
            task_type=task_type,
            priority=priority,
            executor_name=self.executor_stats[task_type].name
        )
        
        try:
            # 选择合适的执行器
            executor = self.executors[task_type]
            
            # 创建包装任务
            wrapped_task = self._wrap_task(task, task_info, args, kwargs)
            
            # 提交任务
            future = executor.submit(wrapped_task)
            
            # 记录任务
            self.active_tasks[task_id] = task_info
            self.executor_stats[task_type].queued_tasks += 1
            
            # 等待结果（带超时）
            timeout_value = timeout or self.task_timeout
            
            try:
                result = await asyncio.wait_for(
                    asyncio.wrap_future(future),
                    timeout=timeout_value
                )
                
                # 标记成功
                task_info.success = True
                task_info.completed_at = datetime.utcnow()
                
                return result
                
            except asyncio.TimeoutError:
                logger.error(f"任务超时 [{task_type.value}]: {task_id}")
                task_info.success = False
                task_info.error = "Task timeout"
                future.cancel()
                raise
                
        except Exception as e:
            logger.error(f"任务执行失败 [{task_type.value}]: {e}")
            task_info.success = False
            task_info.error = str(e)
            raise
        
        finally:
            # 清理和统计
            self._finalize_task(task_id)

    async def submit_batch(
        self,
        tasks: List[Callable],
        task_type: TaskType = TaskType.GENERAL,
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: Optional[int] = None,
        max_concurrent: Optional[int] = None
    ) -> List[Any]:
        """批量提交任务"""
        
        if not tasks:
            return []
        
        # 限制并发数量
        if max_concurrent is None:
            max_concurrent = self.executors[task_type]._max_workers * 2
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def submit_single(task):
            async with semaphore:
                return await self.submit(task, task_type, priority, timeout)
        
        # 并发执行所有任务
        results = await asyncio.gather(
            *[submit_single(task) for task in tasks],
            return_exceptions=True
        )
        
        return results

    def submit_sync(
        self,
        task: Callable,
        task_type: TaskType = TaskType.GENERAL,
        timeout: Optional[int] = None,
        *args,
        **kwargs
    ) -> Any:
        """同步提交任务（非协程环境使用）"""
        
        executor = self.executors[task_type]
        future = executor.submit(task, *args, **kwargs)
        
        timeout_value = timeout or self.task_timeout
        
        try:
            return future.result(timeout=timeout_value)
        except Exception as e:
            logger.error(f"同步任务执行失败 [{task_type.value}]: {e}")
            raise

    # === 便捷方法 - 替代原有的各种线程池使用 ===
    
    async def run_io_task(self, task: Callable, *args, **kwargs) -> Any:
        """运行IO任务"""
        return await self.submit(task, TaskType.IO, *args, **kwargs)
    
    async def run_cpu_task(self, task: Callable, *args, **kwargs) -> Any:
        """运行CPU任务"""
        return await self.submit(task, TaskType.CPU, *args, **kwargs)
    
    async def run_ml_task(self, task: Callable, *args, **kwargs) -> Any:
        """运行ML任务"""
        return await self.submit(task, TaskType.ML, *args, **kwargs)
    
    async def run_db_task(self, task: Callable, *args, **kwargs) -> Any:
        """运行数据库任务"""
        return await self.submit(task, TaskType.DATABASE, *args, **kwargs)
    
    async def run_compression_task(self, task: Callable, *args, **kwargs) -> Any:
        """运行压缩任务"""
        return await self.submit(task, TaskType.COMPRESSION, *args, **kwargs)
    
    async def run_crypto_task(self, task: Callable, *args, **kwargs) -> Any:
        """运行加密任务"""
        return await self.submit(task, TaskType.CRYPTO, *args, **kwargs)

    # === 监控和统计 ===
    
    def get_executor_stats(self, task_type: Optional[TaskType] = None) -> Union[ExecutorStats, Dict[TaskType, ExecutorStats]]:
        """获取执行器统计信息"""
        if task_type:
            return self.executor_stats[task_type]
        return self.executor_stats.copy()
    
    def get_system_stats(self) -> SystemStats:
        """获取系统统计信息"""
        # 更新统计信息
        self.system_stats.uptime_seconds = time.time() - self._start_time
        self.system_stats.total_active_tasks = len(self.active_tasks)
        self.system_stats.total_completed_tasks = len(self.completed_tasks)
        
        # 计算系统负载
        total_active = sum(stats.active_tasks for stats in self.executor_stats.values())
        total_capacity = sum(stats.max_workers for stats in self.executor_stats.values())
        self.system_stats.system_load = total_active / total_capacity if total_capacity > 0 else 0.0
        
        # 获取内存使用情况
        try:
            import psutil
            process = psutil.Process()
            self.system_stats.memory_usage_mb = process.memory_info().rss / 1024 / 1024
        except:
            pass
        
        return self.system_stats
    
    def get_active_tasks(self, task_type: Optional[TaskType] = None) -> List[TaskInfo]:
        """获取活跃任务列表"""
        if task_type:
            return [task for task in self.active_tasks.values() if task.task_type == task_type]
        return list(self.active_tasks.values())
    
    def get_completed_tasks(
        self, 
        task_type: Optional[TaskType] = None,
        limit: int = 100
    ) -> List[TaskInfo]:
        """获取已完成任务列表"""
        tasks = self.completed_tasks[-limit:] if limit > 0 else self.completed_tasks
        
        if task_type:
            tasks = [task for task in tasks if task.task_type == task_type]
        
        return tasks

    # === 健康检查和管理 ===
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health_info = {
            "status": "healthy",
            "executors": {},
            "issues": []
        }
        
        for task_type, executor in self.executors.items():
            stats = self.executor_stats[task_type]
            
            # 检查执行器状态
            is_healthy = True
            if stats.active_tasks >= stats.max_workers:
                health_info["issues"].append(f"{task_type.value} executor at capacity")
                is_healthy = False
            
            if stats.failed_tasks > stats.completed_tasks * 0.1:  # 失败率>10%
                health_info["issues"].append(f"{task_type.value} executor high failure rate")
                is_healthy = False
            
            health_info["executors"][task_type.value] = {
                "healthy": is_healthy,
                "active_tasks": stats.active_tasks,
                "max_workers": stats.max_workers,
                "utilization": stats.active_tasks / stats.max_workers
            }
        
        if health_info["issues"]:
            health_info["status"] = "degraded"
        
        return health_info
    
    async def shutdown(self, wait: bool = True, timeout: float = 30.0):
        """关闭所有执行器"""
        logger.info("🛑 SharedExecutorService 开始关闭")
        
        # 停止监控
        self._shutdown_event.set()
        if self._monitor_task:
            self._monitor_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        # 关闭所有执行器
        shutdown_tasks = []
        for task_type, executor in self.executors.items():
            logger.info(f"关闭执行器: {task_type.value}")
            shutdown_tasks.append(
                asyncio.get_event_loop().run_in_executor(
                    None, 
                    executor.shutdown, 
                    wait
                )
            )
        
        try:
            await asyncio.wait_for(
                asyncio.gather(*shutdown_tasks, return_exceptions=True),
                timeout=timeout
            )
            logger.info("✅ 所有执行器已关闭")
        except asyncio.TimeoutError:
            logger.warning("⚠️ 执行器关闭超时")
        
        # 清理资源
        self.active_tasks.clear()
        self.completed_tasks.clear()

    # === 内部方法 ===
    
    def _generate_task_id(self) -> str:
        """生成任务ID"""
        self.task_counter += 1
        timestamp = int(time.time() * 1000)
        return f"task_{timestamp}_{self.task_counter}"
    
    def _wrap_task(self, task: Callable, task_info: TaskInfo, args, kwargs) -> Callable:
        """包装任务以添加监控"""
        def wrapped():
            try:
                # 记录开始时间
                task_info.started_at = datetime.utcnow()
                self.executor_stats[task_info.task_type].active_tasks += 1
                self.executor_stats[task_info.task_type].queued_tasks -= 1
                
                # 更新峰值
                current_active = self.executor_stats[task_info.task_type].active_tasks
                if current_active > self.executor_stats[task_info.task_type].peak_active_tasks:
                    self.executor_stats[task_info.task_type].peak_active_tasks = current_active
                
                # 执行任务
                if args or kwargs:
                    result = task(*args, **kwargs)
                else:
                    result = task()
                
                return result
                
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                logger.error(f"任务执行异常 [{task_info.task_id}]: {e}")
                logger.error(f"异常堆栈:\n{error_trace}")
                raise
            finally:
                # 清理活跃任务计数
                self.executor_stats[task_info.task_type].active_tasks -= 1
        
        return wrapped
    
    def _finalize_task(self, task_id: str):
        """完成任务处理"""
        if task_id not in self.active_tasks:
            return
        
        task_info = self.active_tasks.pop(task_id)
        
        # 计算执行时间
        if task_info.started_at and task_info.completed_at:
            task_info.duration_seconds = (
                task_info.completed_at - task_info.started_at
            ).total_seconds()
        
        # 更新统计信息
        stats = self.executor_stats[task_info.task_type]
        if task_info.success:
            stats.completed_tasks += 1
        else:
            stats.failed_tasks += 1
        
        stats.total_execution_time += task_info.duration_seconds
        if stats.completed_tasks > 0:
            stats.avg_execution_time = stats.total_execution_time / stats.completed_tasks
        
        stats.last_task_time = task_info.completed_at or datetime.utcnow()
        
        # 保存到历史记录
        self.completed_tasks.append(task_info)
        
        # 限制历史记录大小
        if len(self.completed_tasks) > 1000:
            self.completed_tasks = self.completed_tasks[-1000:]
    
    def _start_monitoring(self):
        """启动监控任务"""
        async def monitor():
            while not self._shutdown_event.is_set():
                try:
                    await asyncio.sleep(60)  # 每分钟监控一次
                    self._log_stats()
                    await self._cleanup_completed_tasks()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"监控任务异常: {e}")
        
        self._monitor_task = asyncio.create_task(monitor())
    
    def _log_stats(self):
        """记录统计信息"""
        system_stats = self.get_system_stats()
        
        logger.info(f"📊 系统负载: {system_stats.system_load:.1%}")
        logger.info(f"   活跃任务: {system_stats.total_active_tasks}")
        logger.info(f"   已完成: {system_stats.total_completed_tasks}")
        
        # 记录各执行器状态
        for task_type, stats in self.executor_stats.items():
            if stats.active_tasks > 0 or stats.completed_tasks > 0:
                logger.debug(
                    f"   {task_type.value}: "
                    f"活跃={stats.active_tasks}/{stats.max_workers}, "
                    f"已完成={stats.completed_tasks}, "
                    f"失败={stats.failed_tasks}"
                )
    
    async def _cleanup_completed_tasks(self):
        """清理旧的已完成任务记录"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        original_count = len(self.completed_tasks)
        
        self.completed_tasks = [
            task for task in self.completed_tasks 
            if task.completed_at and task.completed_at > cutoff_time
        ]
        
        cleaned_count = original_count - len(self.completed_tasks)
        if cleaned_count > 0:
            logger.debug(f"清理旧任务记录: {cleaned_count} 项")


# 全局实例管理
_shared_executor_service: Optional[SharedExecutorService] = None


def get_shared_executor_service(**kwargs) -> SharedExecutorService:
    """获取共享执行器服务实例"""
    global _shared_executor_service
    
    if _shared_executor_service is None:
        _shared_executor_service = SharedExecutorService(**kwargs)
    
    return _shared_executor_service


async def cleanup_shared_executor_service():
    """清理共享执行器服务"""
    global _shared_executor_service
    
    if _shared_executor_service:
        try:
            await _shared_executor_service.shutdown()
            logger.info("🚀 SharedExecutorService 已清理")
        except Exception as e:
            logger.error(f"清理SharedExecutorService失败: {e}")
        finally:
            _shared_executor_service = None