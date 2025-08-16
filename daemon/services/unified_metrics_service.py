#!/usr/bin/env python3
"""
统一监控服务 - 消除4个重复监控实现
整合性能指标、系统监控、业务监控为统一接口
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Union, Tuple
import threading
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """指标类型枚举"""
    COUNTER = "counter"         # 计数器 (累积值)
    GAUGE = "gauge"            # 仪表 (瞬时值)  
    HISTOGRAM = "histogram"    # 直方图 (分布统计)
    TIMER = "timer"           # 计时器 (执行时间)
    RATE = "rate"             # 速率 (每秒事件数)


class MetricUnit(Enum):
    """指标单位枚举"""
    COUNT = "count"
    BYTES = "bytes"
    MILLISECONDS = "ms"
    SECONDS = "s"
    PERCENT = "percent"
    REQUESTS_PER_SECOND = "rps"
    BYTES_PER_SECOND = "bps"


@dataclass
class MetricPoint:
    """指标数据点"""
    timestamp: float
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class MetricSeries:
    """指标时间序列"""
    name: str
    metric_type: MetricType
    unit: MetricUnit
    description: str
    labels: Dict[str, str] = field(default_factory=dict)
    points: deque = field(default_factory=lambda: deque(maxlen=1440))  # 24小时数据点
    
    def add_point(self, value: float, timestamp: Optional[float] = None, labels: Optional[Dict[str, str]] = None):
        """添加数据点"""
        if timestamp is None:
            timestamp = time.time()
        
        point_labels = self.labels.copy()
        if labels:
            point_labels.update(labels)
        
        point = MetricPoint(timestamp=timestamp, value=value, labels=point_labels)
        self.points.append(point)
    
    def get_latest(self) -> Optional[MetricPoint]:
        """获取最新数据点"""
        return self.points[-1] if self.points else None
    
    def get_average(self, duration_seconds: int = 300) -> float:
        """获取指定时间段内的平均值"""
        cutoff_time = time.time() - duration_seconds
        values = [p.value for p in self.points if p.timestamp > cutoff_time]
        return sum(values) / len(values) if values else 0.0
    
    def get_percentile(self, percentile: float, duration_seconds: int = 300) -> float:
        """获取百分位数"""
        cutoff_time = time.time() - duration_seconds
        values = sorted([p.value for p in self.points if p.timestamp > cutoff_time])
        if not values:
            return 0.0
        
        index = int((percentile / 100.0) * len(values))
        return values[min(index, len(values) - 1)]


@dataclass
class ServiceMetrics:
    """服务指标集合"""
    service_name: str
    metrics: Dict[str, MetricSeries] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def add_metric(self, metric: MetricSeries):
        """添加指标"""
        self.metrics[metric.name] = metric
        self.last_updated = datetime.utcnow()
    
    def get_metric(self, name: str) -> Optional[MetricSeries]:
        """获取指标"""
        return self.metrics.get(name)
    
    def record_value(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """记录指标值"""
        if metric_name in self.metrics:
            self.metrics[metric_name].add_point(value, labels=labels)
            self.last_updated = datetime.utcnow()


class UnifiedMetricsService:
    """统一监控服务 - 消除4个重复监控实现"""
    
    def __init__(
        self,
        retention_hours: int = 24,       # 数据保留时间
        collection_interval: int = 60,   # 采集间隔(秒)
        enable_system_metrics: bool = True,
        enable_export: bool = False,
        export_path: Optional[Path] = None
    ):
        # 配置参数
        self.retention_hours = retention_hours
        self.collection_interval = collection_interval
        self.enable_system_metrics = enable_system_metrics
        self.enable_export = enable_export
        self.export_path = export_path
        
        # 指标存储
        self.services: Dict[str, ServiceMetrics] = {}
        self.global_metrics: Dict[str, MetricSeries] = {}
        
        # 系统指标
        self._system_collectors: List[Callable] = []
        self._collection_task: Optional[asyncio.Task] = None
        self._export_task: Optional[asyncio.Task] = None
        
        # 线程安全
        self._lock = threading.Lock()
        
        # 性能计数器
        self._performance_counters: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # 预定义的常用指标
        self._initialize_common_metrics()
        
        logger.info(f"📊 UnifiedMetricsService 初始化完成")
        
        # 启动后台任务
        if self.enable_system_metrics:
            self._start_system_collection()
        
        if self.enable_export:
            self._start_export_task()

    def register_service(self, service_name: str) -> ServiceMetrics:
        """注册服务监控"""
        with self._lock:
            if service_name not in self.services:
                self.services[service_name] = ServiceMetrics(service_name=service_name)
                logger.info(f"📊 注册服务监控: {service_name}")
            
            return self.services[service_name]

    def create_metric(
        self,
        service_name: str,
        metric_name: str,
        metric_type: MetricType,
        unit: MetricUnit = MetricUnit.COUNT,
        description: str = "",
        labels: Optional[Dict[str, str]] = None
    ) -> MetricSeries:
        """创建新指标"""
        
        # 确保服务已注册
        service_metrics = self.register_service(service_name)
        
        # 创建指标
        metric = MetricSeries(
            name=metric_name,
            metric_type=metric_type,
            unit=unit,
            description=description,
            labels=labels or {}
        )
        
        service_metrics.add_metric(metric)
        
        logger.debug(f"📊 创建指标: {service_name}.{metric_name}")
        return metric

    # === 指标记录方法 - 替代原有各种监控代码 ===
    
    def record_counter(
        self,
        service_name: str,
        metric_name: str,
        increment: float = 1.0,
        labels: Optional[Dict[str, str]] = None
    ):
        """记录计数器指标"""
        metric = self._get_or_create_metric(
            service_name, metric_name, MetricType.COUNTER, MetricUnit.COUNT
        )
        
        # 计数器累积值
        current_value = metric.get_latest().value if metric.get_latest() else 0.0
        metric.add_point(current_value + increment, labels=labels)
    
    def record_gauge(
        self,
        service_name: str,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """记录仪表指标"""
        metric = self._get_or_create_metric(
            service_name, metric_name, MetricType.GAUGE, MetricUnit.COUNT
        )
        metric.add_point(value, labels=labels)
    
    def record_timer(
        self,
        service_name: str,
        metric_name: str,
        duration_ms: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """记录计时器指标"""
        metric = self._get_or_create_metric(
            service_name, metric_name, MetricType.TIMER, MetricUnit.MILLISECONDS
        )
        metric.add_point(duration_ms, labels=labels)
    
    def record_rate(
        self,
        service_name: str,
        metric_name: str,
        count: float,
        window_seconds: int = 60,
        labels: Optional[Dict[str, str]] = None
    ):
        """记录速率指标"""
        metric = self._get_or_create_metric(
            service_name, metric_name, MetricType.RATE, MetricUnit.REQUESTS_PER_SECOND
        )
        
        # 计算速率
        rate = count / window_seconds
        metric.add_point(rate, labels=labels)

    # === 便捷监控方法 ===
    
    def time_function(self, service_name: str, metric_name: str = None):
        """函数执行时间装饰器"""
        def decorator(func):
            nonlocal metric_name
            if metric_name is None:
                metric_name = f"{func.__name__}_duration"
            
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = (time.time() - start_time) * 1000  # 转换为毫秒
                    self.record_timer(service_name, metric_name, duration)
            
            return wrapper
        return decorator
    
    def count_calls(self, service_name: str, metric_name: str = None):
        """函数调用次数装饰器"""
        def decorator(func):
            nonlocal metric_name
            if metric_name is None:
                metric_name = f"{func.__name__}_calls"
            
            def wrapper(*args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                    self.record_counter(service_name, metric_name)
                    return result
                except Exception as e:
                    self.record_counter(service_name, f"{metric_name}_errors")
                    raise
            
            return wrapper
        return decorator
    
    class TimerContext:
        """计时器上下文管理器"""
        def __init__(self, metrics_service, service_name: str, metric_name: str):
            self.metrics_service = metrics_service
            self.service_name = service_name
            self.metric_name = metric_name
            self.start_time = None
        
        def __enter__(self):
            self.start_time = time.time()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.start_time:
                duration = (time.time() - self.start_time) * 1000
                self.metrics_service.record_timer(
                    self.service_name, self.metric_name, duration
                )
    
    def timer(self, service_name: str, metric_name: str):
        """创建计时器上下文管理器"""
        return self.TimerContext(self, service_name, metric_name)

    # === 标准化监控接口 - 替代原有各种监控方法 ===
    
    def record_search_time(self, service_name: str, search_type: str, duration_ms: float):
        """记录搜索时间"""
        self.record_timer(
            service_name, 
            "search_duration", 
            duration_ms,
            labels={"search_type": search_type}
        )
    
    def record_cache_hit(self, service_name: str, cache_type: str, hit: bool = True):
        """记录缓存命中"""
        metric_name = "cache_hits" if hit else "cache_misses"
        self.record_counter(
            service_name, 
            metric_name,
            labels={"cache_type": cache_type}
        )
    
    def record_encoding_time(self, service_name: str, model_name: str, duration_ms: float):
        """记录编码时间"""
        self.record_timer(
            service_name,
            "encoding_duration",
            duration_ms,
            labels={"model": model_name}
        )
    
    def record_storage_operation(self, service_name: str, operation: str, duration_ms: float, success: bool = True):
        """记录存储操作"""
        self.record_timer(
            service_name,
            "storage_duration",
            duration_ms,
            labels={"operation": operation, "status": "success" if success else "error"}
        )
        
        if success:
            self.record_counter(service_name, "storage_operations_success", labels={"operation": operation})
        else:
            self.record_counter(service_name, "storage_operations_error", labels={"operation": operation})

    # === 指标查询和聚合 ===
    
    def get_metric_value(self, service_name: str, metric_name: str) -> Optional[float]:
        """获取指标当前值"""
        service = self.services.get(service_name)
        if not service:
            return None
        
        metric = service.get_metric(metric_name)
        if not metric:
            return None
        
        latest = metric.get_latest()
        return latest.value if latest else None
    
    def get_metric_average(self, service_name: str, metric_name: str, duration_seconds: int = 300) -> float:
        """获取指标平均值"""
        service = self.services.get(service_name)
        if not service:
            return 0.0
        
        metric = service.get_metric(metric_name)
        if not metric:
            return 0.0
        
        return metric.get_average(duration_seconds)
    
    def get_metric_percentile(self, service_name: str, metric_name: str, percentile: float, duration_seconds: int = 300) -> float:
        """获取指标百分位数"""
        service = self.services.get(service_name)
        if not service:
            return 0.0
        
        metric = service.get_metric(metric_name)
        if not metric:
            return 0.0
        
        return metric.get_percentile(percentile, duration_seconds)
    
    def get_service_summary(self, service_name: str) -> Dict[str, Any]:
        """获取服务监控摘要"""
        service = self.services.get(service_name)
        if not service:
            return {}
        
        summary = {
            "service_name": service_name,
            "last_updated": service.last_updated.isoformat(),
            "metrics_count": len(service.metrics),
            "metrics": {}
        }
        
        for metric_name, metric in service.metrics.items():
            latest = metric.get_latest()
            summary["metrics"][metric_name] = {
                "type": metric.metric_type.value,
                "unit": metric.unit.value,
                "current_value": latest.value if latest else None,
                "avg_5min": metric.get_average(300),
                "p95_5min": metric.get_percentile(95, 300),
                "data_points": len(metric.points)
            }
        
        return summary
    
    def get_global_summary(self) -> Dict[str, Any]:
        """获取全局监控摘要"""
        summary = {
            "services_count": len(self.services),
            "total_metrics": sum(len(s.metrics) for s in self.services.values()),
            "collection_interval": self.collection_interval,
            "retention_hours": self.retention_hours,
            "services": {}
        }
        
        for service_name in self.services.keys():
            summary["services"][service_name] = self.get_service_summary(service_name)
        
        return summary

    # === 系统指标收集 ===
    
    def _initialize_common_metrics(self):
        """初始化常用指标"""
        # 全局系统指标
        system_service = self.register_service("system")
        
        self.create_metric("system", "cpu_usage", MetricType.GAUGE, MetricUnit.PERCENT, "CPU使用率")
        self.create_metric("system", "memory_usage", MetricType.GAUGE, MetricUnit.BYTES, "内存使用量")
        self.create_metric("system", "memory_usage_percent", MetricType.GAUGE, MetricUnit.PERCENT, "内存使用率")
        self.create_metric("system", "disk_usage", MetricType.GAUGE, MetricUnit.BYTES, "磁盘使用量")
        
        # 应用指标
        app_service = self.register_service("application")
        
        self.create_metric("application", "uptime", MetricType.GAUGE, MetricUnit.SECONDS, "应用运行时间")
        self.create_metric("application", "active_connections", MetricType.GAUGE, MetricUnit.COUNT, "活跃连接数")
        self.create_metric("application", "request_rate", MetricType.RATE, MetricUnit.REQUESTS_PER_SECOND, "请求速率")
    
    def _start_system_collection(self):
        """启动系统指标收集"""
        async def collect_system_metrics():
            while True:
                try:
                    await asyncio.sleep(self.collection_interval)
                    await self._collect_system_metrics()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"系统指标收集失败: {e}")
        
        self._collection_task = asyncio.create_task(collect_system_metrics())
    
    async def _collect_system_metrics(self):
        """收集系统指标"""
        try:
            import psutil
            
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_gauge("system", "cpu_usage", cpu_percent)
            
            # 内存使用
            memory = psutil.virtual_memory()
            self.record_gauge("system", "memory_usage", memory.used)
            self.record_gauge("system", "memory_usage_percent", memory.percent)
            
            # 磁盘使用
            disk = psutil.disk_usage('/')
            self.record_gauge("system", "disk_usage", disk.used)
            
            # 应用运行时间
            import os
            uptime = time.time() - psutil.Process(os.getpid()).create_time()
            self.record_gauge("application", "uptime", uptime)
            
        except Exception as e:
            logger.error(f"收集系统指标失败: {e}")
    
    def _start_export_task(self):
        """启动导出任务"""
        if not self.export_path:
            return
        
        async def export_metrics():
            while True:
                try:
                    await asyncio.sleep(300)  # 每5分钟导出一次
                    await self._export_metrics()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"指标导出失败: {e}")
        
        self._export_task = asyncio.create_task(export_metrics())
    
    async def _export_metrics(self):
        """导出指标到文件"""
        try:
            export_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "summary": self.get_global_summary()
            }
            
            export_file = self.export_path / f"metrics_{int(time.time())}.json"
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"指标导出完成: {export_file}")
            
        except Exception as e:
            logger.error(f"导出指标失败: {e}")

    # === 内部辅助方法 ===
    
    def _get_or_create_metric(
        self,
        service_name: str,
        metric_name: str,
        metric_type: MetricType,
        unit: MetricUnit
    ) -> MetricSeries:
        """获取或创建指标"""
        service = self.register_service(service_name)
        
        metric = service.get_metric(metric_name)
        if not metric:
            metric = self.create_metric(
                service_name, metric_name, metric_type, unit
            )
        
        return metric
    
    async def cleanup(self):
        """清理资源"""
        logger.info("📊 UnifiedMetricsService 开始清理")
        
        # 停止后台任务
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
        
        if self._export_task:
            self._export_task.cancel()
            try:
                await self._export_task
            except asyncio.CancelledError:
                pass
        
        # 最后一次导出
        if self.enable_export and self.export_path:
            try:
                await self._export_metrics()
            except Exception as e:
                logger.error(f"最终导出失败: {e}")
        
        logger.info("📊 UnifiedMetricsService 清理完成")


# 全局实例管理
_unified_metrics_service: Optional[UnifiedMetricsService] = None


def get_unified_metrics_service(**kwargs) -> UnifiedMetricsService:
    """获取统一监控服务实例"""
    global _unified_metrics_service
    
    if _unified_metrics_service is None:
        # 设置默认导出路径
        if 'export_path' not in kwargs:
            try:
                from core.environment_manager import get_environment_manager
                env_manager = get_environment_manager()
                kwargs['export_path'] = env_manager.get_logs_dir() / "metrics"
            except:
                pass
        
        _unified_metrics_service = UnifiedMetricsService(**kwargs)
    
    return _unified_metrics_service


async def cleanup_unified_metrics_service():
    """清理统一监控服务"""
    global _unified_metrics_service
    
    if _unified_metrics_service:
        try:
            await _unified_metrics_service.cleanup()
            logger.info("📊 UnifiedMetricsService 已清理")
        except Exception as e:
            logger.error(f"清理UnifiedMetricsService失败: {e}")
        finally:
            _unified_metrics_service = None