#!/usr/bin/env python3
"""
MetricsCollector - 核心监控数据收集器
提供统一的性能指标收集、聚合和历史数据管理功能
"""

import asyncio
import json
import logging
import statistics
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union


class MetricType(Enum):
    """指标类型"""

    COUNTER = "counter"  # 单调递增计数器
    GAUGE = "gauge"  # 瞬时值测量
    HISTOGRAM = "histogram"  # 分布数据收集
    TIMER = "timer"  # 执行时间测量
    RATE = "rate"  # 速率测量


@dataclass
class MetricPoint:
    """单个指标数据点"""

    timestamp: float
    value: Union[float, int, Dict[str, Any]]
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "value": self.value,
            "labels": self.labels,
            "metadata": self.metadata,
        }


@dataclass
class Metric:
    """指标定义和数据容器"""

    name: str
    type: MetricType
    description: str
    unit: str = ""
    labels: Dict[str, str] = field(default_factory=dict)
    data_points: deque = field(default_factory=lambda: deque(maxlen=1000))
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)

    def add_point(
        self,
        value: Union[float, int, Dict[str, Any]],
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """添加数据点"""
        point = MetricPoint(
            timestamp=time.time(),
            value=value,
            labels=labels or {},
            metadata=metadata or {},
        )
        self.data_points.append(point)
        self.last_updated = point.timestamp

    def get_latest_value(self) -> Optional[Union[float, int, Dict[str, Any]]]:
        """获取最新值"""
        return self.data_points[-1].value if self.data_points else None

    def get_historical_data(
        self, duration_seconds: Optional[int] = None
    ) -> List[MetricPoint]:
        """获取历史数据"""
        if duration_seconds is None:
            return list(self.data_points)

        cutoff_time = time.time() - duration_seconds
        return [point for point in self.data_points if point.timestamp >= cutoff_time]

    def calculate_statistics(
        self, duration_seconds: Optional[int] = None
    ) -> Dict[str, float]:
        """计算统计数据"""
        data = self.get_historical_data(duration_seconds)
        if not data:
            return {}

        if self.type == MetricType.HISTOGRAM:
            # 直方图数据的特殊处理
            return self._calculate_histogram_stats(data)

        # 数值类型的统计
        values = [
            point.value for point in data if isinstance(point.value, (int, float))
        ]
        if not values:
            return {}

        return {
            "count": len(values),
            "sum": sum(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "p50": (
                statistics.quantiles(values, n=2)[0] if len(values) > 1 else values[0]
            ),
            "p95": (
                statistics.quantiles(values, n=20)[18]
                if len(values) > 20
                else max(values)
            ),
            "p99": (
                statistics.quantiles(values, n=100)[98]
                if len(values) > 100
                else max(values)
            ),
        }

    def _calculate_histogram_stats(self, data: List[MetricPoint]) -> Dict[str, float]:
        """计算直方图统计数据"""
        all_values = []
        for point in data:
            if isinstance(point.value, dict) and "buckets" in point.value:
                # 从直方图桶中提取值
                for bucket, count in point.value["buckets"].items():
                    try:
                        bucket_value = float(bucket)
                        all_values.extend([bucket_value] * count)
                    except ValueError:
                        continue

        if not all_values:
            return {}

        return {
            "count": len(all_values),
            "min": min(all_values),
            "max": max(all_values),
            "mean": statistics.mean(all_values),
            "p50": (
                statistics.quantiles(all_values, n=2)[0]
                if len(all_values) > 1
                else all_values[0]
            ),
            "p95": (
                statistics.quantiles(all_values, n=20)[18]
                if len(all_values) > 20
                else max(all_values)
            ),
            "p99": (
                statistics.quantiles(all_values, n=100)[98]
                if len(all_values) > 100
                else max(all_values)
            ),
        }


class MetricsCollector:
    """核心监控数据收集器"""

    def __init__(self, retention_seconds: int = 3600):
        """
        Args:
            retention_seconds: 数据保留时间（秒），默认1小时
        """
        self.retention_seconds = retention_seconds
        self.metrics: Dict[str, Metric] = {}
        self._lock = threading.RLock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
        self.logger = logging.getLogger(__name__)

        # 回调函数注册
        self._metric_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        self._threshold_alerts: Dict[str, Dict[str, Any]] = {}

    async def start(self):
        """启动监控收集器"""
        if self._running:
            return

        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.logger.info("✅ MetricsCollector 已启动")

    async def stop(self):
        """停止监控收集器"""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        self.logger.info("MetricsCollector 已停止")

    def register_metric(
        self,
        name: str,
        type: MetricType,
        description: str,
        unit: str = "",
        labels: Optional[Dict[str, str]] = None,
    ) -> Metric:
        """注册新指标"""
        with self._lock:
            if name in self.metrics:
                return self.metrics[name]

            metric = Metric(
                name=name,
                type=type,
                description=description,
                unit=unit,
                labels=labels or {},
            )
            self.metrics[name] = metric
            self.logger.debug(f"已注册指标: {name} ({type.value})")
            return metric

    def record_value(
        self,
        metric_name: str,
        value: Union[float, int, Dict[str, Any]],
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """记录指标值"""
        with self._lock:
            if metric_name not in self.metrics:
                self.logger.warning(f"未注册的指标: {metric_name}")
                return

            metric = self.metrics[metric_name]
            metric.add_point(value, labels, metadata)

            # 触发回调函数
            self._trigger_callbacks(metric_name, value, labels)

            # 检查阈值告警
            self._check_thresholds(metric_name, value, labels)

    def increment_counter(
        self,
        metric_name: str,
        amount: Union[float, int] = 1,
        labels: Optional[Dict[str, str]] = None,
    ):
        """增加计数器"""
        with self._lock:
            if metric_name not in self.metrics:
                self.logger.warning(f"未注册的指标: {metric_name}")
                return

            metric = self.metrics[metric_name]
            if metric.type != MetricType.COUNTER:
                self.logger.warning(f"指标 {metric_name} 不是计数器类型")
                return

            current_value = metric.get_latest_value() or 0
            new_value = current_value + amount
            metric.add_point(new_value, labels)

            self._trigger_callbacks(metric_name, new_value, labels)

    def record_gauge(
        self,
        metric_name: str,
        value: Union[float, int],
        labels: Optional[Dict[str, str]] = None,
    ):
        """记录测量值"""
        self.record_value(metric_name, value, labels)

    def record_histogram(
        self,
        metric_name: str,
        value: Union[float, int],
        buckets: Optional[List[float]] = None,
        labels: Optional[Dict[str, str]] = None,
    ):
        """记录直方图数据"""
        if buckets is None:
            buckets = [
                0.001,
                0.005,
                0.01,
                0.025,
                0.05,
                0.1,
                0.25,
                0.5,
                1.0,
                2.5,
                5.0,
                10.0,
            ]

        # 计算直方图桶分布
        bucket_counts = {}
        for bucket in buckets:
            if value <= bucket:
                bucket_counts[str(bucket)] = bucket_counts.get(str(bucket), 0) + 1

        histogram_data = {
            "value": value,
            "buckets": bucket_counts,
            "bucket_boundaries": buckets,
        }

        self.record_value(metric_name, histogram_data, labels)

    def time_function(self, metric_name: str, labels: Optional[Dict[str, str]] = None):
        """函数执行时间装饰器"""

        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    self.record_histogram(metric_name, duration, labels=labels)

            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    self.record_histogram(metric_name, duration, labels=labels)

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return wrapper

        return decorator

    def get_metric(self, name: str) -> Optional[Metric]:
        """获取指标"""
        with self._lock:
            return self.metrics.get(name)

    def get_all_metrics(self) -> Dict[str, Metric]:
        """获取所有指标"""
        with self._lock:
            return self.metrics.copy()

    def get_metrics_summary(
        self, duration_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取指标摘要"""
        with self._lock:
            summary = {}
            for name, metric in self.metrics.items():
                stats = metric.calculate_statistics(duration_seconds)
                summary[name] = {
                    "type": metric.type.value,
                    "description": metric.description,
                    "unit": metric.unit,
                    "labels": metric.labels,
                    "latest_value": metric.get_latest_value(),
                    "statistics": stats,
                    "data_point_count": len(metric.data_points),
                    "last_updated": metric.last_updated,
                }
            return summary

    def export_metrics(self, format: str = "json") -> str:
        """导出指标数据"""
        summary = self.get_metrics_summary()

        if format.lower() == "json":
            return json.dumps(summary, indent=2, default=str)
        elif format.lower() == "prometheus":
            return self._export_prometheus_format(summary)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_prometheus_format(self, summary: Dict[str, Any]) -> str:
        """导出Prometheus格式"""
        lines = []
        for name, data in summary.items():
            # 添加帮助信息
            lines.append(f"# HELP {name} {data['description']}")
            lines.append(f"# TYPE {name} {data['type']}")

            # 添加指标值
            latest_value = data["latest_value"]
            if isinstance(latest_value, (int, float)):
                labels_str = ",".join([f'{k}="{v}"' for k, v in data["labels"].items()])
                if labels_str:
                    lines.append(f"{name}{{{labels_str}}} {latest_value}")
                else:
                    lines.append(f"{name} {latest_value}")

        return "\n".join(lines)

    def register_callback(self, metric_name: str, callback: Callable):
        """注册指标回调函数"""
        with self._lock:
            self._metric_callbacks[metric_name].append(callback)

    def set_threshold_alert(
        self,
        metric_name: str,
        threshold_value: float,
        comparison: str = "greater",  # greater, less, equal
        callback: Optional[Callable] = None,
    ):
        """设置阈值告警"""
        with self._lock:
            self._threshold_alerts[metric_name] = {
                "threshold": threshold_value,
                "comparison": comparison,
                "callback": callback,
            }

    def _trigger_callbacks(
        self, metric_name: str, value: Any, labels: Optional[Dict[str, str]]
    ):
        """触发回调函数"""
        for callback in self._metric_callbacks.get(metric_name, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(metric_name, value, labels))
                else:
                    callback(metric_name, value, labels)
            except Exception as e:
                self.logger.error(f"指标回调函数执行失败 {metric_name}: {e}")

    def _check_thresholds(
        self, metric_name: str, value: Any, labels: Optional[Dict[str, str]]
    ):
        """检查阈值告警"""
        if metric_name not in self._threshold_alerts:
            return

        alert_config = self._threshold_alerts[metric_name]
        threshold = alert_config["threshold"]
        comparison = alert_config["comparison"]

        triggered = False
        if (
            comparison == "greater"
            and isinstance(value, (int, float))
            and value > threshold
        ):
            triggered = True
        elif (
            comparison == "less"
            and isinstance(value, (int, float))
            and value < threshold
        ):
            triggered = True
        elif comparison == "equal" and value == threshold:
            triggered = True

        if triggered and alert_config["callback"]:
            try:
                alert_config["callback"](metric_name, value, threshold, labels)
            except Exception as e:
                self.logger.error(f"阈值告警回调失败 {metric_name}: {e}")

    async def _cleanup_loop(self):
        """清理过期数据"""
        while self._running:
            try:
                await asyncio.sleep(60)  # 每分钟清理一次
                self._cleanup_old_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"数据清理失败: {e}")

    def _cleanup_old_data(self):
        """清理过期数据"""
        cutoff_time = time.time() - self.retention_seconds

        with self._lock:
            for metric in self.metrics.values():
                # 清理过期数据点
                while (
                    metric.data_points and metric.data_points[0].timestamp < cutoff_time
                ):
                    metric.data_points.popleft()


# 全局监控收集器实例
_global_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """获取全局监控收集器"""
    global _global_collector
    if _global_collector is None:
        _global_collector = MetricsCollector()
    return _global_collector


def initialize_metrics_collector(retention_seconds: int = 3600) -> MetricsCollector:
    """初始化全局监控收集器"""
    global _global_collector
    _global_collector = MetricsCollector(retention_seconds=retention_seconds)
    return _global_collector
