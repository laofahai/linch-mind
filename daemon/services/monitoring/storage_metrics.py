#!/usr/bin/env python3
"""
存储性能监控系统 - 智能存储架构的全面监控
监控压缩比、AI准确性、存储使用情况和系统性能
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import psutil

from core.error_handling import handle_errors, ErrorSeverity, ErrorCategory
from core.service_facade import get_service
from config.intelligent_storage import get_intelligent_storage_config
from services.ai.ollama_service import get_ollama_service
from services.storage.faiss_vector_store import get_faiss_vector_store
from services.storage.intelligent_event_processor import get_intelligent_event_processor
from services.storage.data_lifecycle_manager import get_data_lifecycle_manager
from services.storage.core.database import UnifiedDatabaseService
from models.database_models import EntityMetadata

logger = logging.getLogger(__name__)


@dataclass
class StorageMetrics:
    """存储性能指标"""
    # 基础指标
    timestamp: datetime
    total_documents: int
    total_shards: int
    storage_size_mb: float
    memory_usage_mb: float
    
    # 压缩指标
    compression_ratio: float
    storage_efficiency: float
    
    # AI指标
    ai_accuracy_rate: float
    content_acceptance_rate: float
    avg_value_score: float
    
    # 性能指标
    avg_processing_time_ms: float
    avg_search_time_ms: float
    avg_embedding_time_ms: float
    
    # 分层存储指标
    hot_data_percentage: float
    warm_data_percentage: float
    cold_data_percentage: float
    
    # 系统健康指标
    ollama_status: str
    vector_store_status: str
    database_status: str
    
    # 错误和警告
    error_count_24h: int
    warning_count_24h: int


@dataclass
class AlertRule:
    """告警规则"""
    rule_id: str
    metric_name: str
    threshold: float
    operator: str  # gt/lt/eq
    severity: str  # critical/warning/info
    description: str
    enabled: bool = True


@dataclass
class Alert:
    """告警事件"""
    alert_id: str
    rule_id: str
    metric_name: str
    current_value: float
    threshold: float
    severity: str
    description: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class StorageMetricsCollector:
    """存储指标收集器"""
    
    def __init__(self):
        self.config = get_intelligent_storage_config()
        
        # 服务依赖
        self._ollama_service = None
        self._vector_store = None
        self._intelligent_processor = None
        self._lifecycle_manager = None
        self._db_service = None
        
        # 指标历史
        self._metrics_history: List[StorageMetrics] = []
        self._max_history = 1000  # 保留最近1000个指标点
        
        # 告警系统
        self._alert_rules: List[AlertRule] = []
        self._active_alerts: List[Alert] = []
        
        # 性能监控
        self._is_collecting = False
        self._collection_interval = 60  # 60秒收集一次
        
        # 文件路径
        self.metrics_dir = self.config.storage_dir / "metrics"
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化告警规则
        self._setup_default_alert_rules()

    async def initialize(self) -> bool:
        """初始化指标收集器"""
        try:
            # 获取服务依赖
            self._ollama_service = await get_ollama_service()
            self._vector_store = await get_faiss_vector_store()
            self._intelligent_processor = await get_intelligent_event_processor()
            self._lifecycle_manager = await get_data_lifecycle_manager()
            self._db_service = get_service(UnifiedDatabaseService)
            
            # 加载历史指标
            await self._load_metrics_history()
            
            # 启动后台收集
            if self.config.monitoring.enable_metrics:
                await self._start_metrics_collection()
            
            logger.info("存储指标收集器初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"存储指标收集器初始化失败: {e}")
            return False

    async def close(self):
        """关闭指标收集器"""
        try:
            self._is_collecting = False
            await self._save_metrics_history()
            logger.info("存储指标收集器已关闭")
        except Exception as e:
            logger.error(f"关闭指标收集器失败: {e}")

    # === 指标收集 ===

    async def collect_current_metrics(self) -> StorageMetrics:
        """收集当前指标"""
        try:
            # 并行收集各项指标
            tasks = [
                self._collect_basic_metrics(),
                self._collect_compression_metrics(),
                self._collect_ai_metrics(),
                self._collect_performance_metrics(),
                self._collect_tier_metrics(),
                self._collect_health_metrics(),
                self._collect_error_metrics(),
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 合并指标
            metrics = StorageMetrics(
                timestamp=datetime.utcnow(),
                total_documents=0,
                total_shards=0,
                storage_size_mb=0.0,
                memory_usage_mb=0.0,
                compression_ratio=1.0,
                storage_efficiency=0.0,
                ai_accuracy_rate=0.0,
                content_acceptance_rate=0.0,
                avg_value_score=0.0,
                avg_processing_time_ms=0.0,
                avg_search_time_ms=0.0,
                avg_embedding_time_ms=0.0,
                hot_data_percentage=0.0,
                warm_data_percentage=0.0,
                cold_data_percentage=0.0,
                ollama_status="unknown",
                vector_store_status="unknown",
                database_status="unknown",
                error_count_24h=0,
                warning_count_24h=0,
            )
            
            # 合并结果
            for i, result in enumerate(results):
                if not isinstance(result, Exception):
                    if i == 0:  # 基础指标
                        metrics.total_documents = result.get("total_documents", 0)
                        metrics.total_shards = result.get("total_shards", 0)
                        metrics.storage_size_mb = result.get("storage_size_mb", 0.0)
                        metrics.memory_usage_mb = result.get("memory_usage_mb", 0.0)
                    elif i == 1:  # 压缩指标
                        metrics.compression_ratio = result.get("compression_ratio", 1.0)
                        metrics.storage_efficiency = result.get("storage_efficiency", 0.0)
                    elif i == 2:  # AI指标
                        metrics.ai_accuracy_rate = result.get("ai_accuracy_rate", 0.0)
                        metrics.content_acceptance_rate = result.get("content_acceptance_rate", 0.0)
                        metrics.avg_value_score = result.get("avg_value_score", 0.0)
                    elif i == 3:  # 性能指标
                        metrics.avg_processing_time_ms = result.get("avg_processing_time_ms", 0.0)
                        metrics.avg_search_time_ms = result.get("avg_search_time_ms", 0.0)
                        metrics.avg_embedding_time_ms = result.get("avg_embedding_time_ms", 0.0)
                    elif i == 4:  # 分层指标
                        metrics.hot_data_percentage = result.get("hot_data_percentage", 0.0)
                        metrics.warm_data_percentage = result.get("warm_data_percentage", 0.0)
                        metrics.cold_data_percentage = result.get("cold_data_percentage", 0.0)
                    elif i == 5:  # 健康指标
                        metrics.ollama_status = result.get("ollama_status", "unknown")
                        metrics.vector_store_status = result.get("vector_store_status", "unknown")
                        metrics.database_status = result.get("database_status", "unknown")
                    elif i == 6:  # 错误指标
                        metrics.error_count_24h = result.get("error_count_24h", 0)
                        metrics.warning_count_24h = result.get("warning_count_24h", 0)
            
            return metrics
            
        except Exception as e:
            logger.error(f"收集指标失败: {e}")
            # 返回默认指标
            return StorageMetrics(
                timestamp=datetime.utcnow(),
                total_documents=0, total_shards=0, storage_size_mb=0.0,
                memory_usage_mb=0.0, compression_ratio=1.0, storage_efficiency=0.0,
                ai_accuracy_rate=0.0, content_acceptance_rate=0.0, avg_value_score=0.0,
                avg_processing_time_ms=0.0, avg_search_time_ms=0.0, avg_embedding_time_ms=0.0,
                hot_data_percentage=0.0, warm_data_percentage=0.0, cold_data_percentage=0.0,
                ollama_status="error", vector_store_status="error", database_status="error",
                error_count_24h=1, warning_count_24h=0,
            )

    async def _collect_basic_metrics(self) -> Dict[str, Any]:
        """收集基础指标"""
        metrics = {}
        
        try:
            # 向量存储指标
            if self._vector_store:
                vector_metrics = await self._vector_store.get_metrics()
                metrics["total_documents"] = vector_metrics.total_documents
                metrics["total_shards"] = vector_metrics.total_shards
                metrics["storage_size_mb"] = vector_metrics.storage_size_mb
            
            # 内存使用
            process = psutil.Process()
            metrics["memory_usage_mb"] = process.memory_info().rss / 1024 / 1024
            
        except Exception as e:
            logger.error(f"收集基础指标失败: {e}")
        
        return metrics

    async def _collect_compression_metrics(self) -> Dict[str, Any]:
        """收集压缩指标"""
        metrics = {}
        
        try:
            if self._vector_store:
                vector_metrics = await self._vector_store.get_metrics()
                metrics["compression_ratio"] = vector_metrics.compression_ratio
                
                # 计算存储效率
                if vector_metrics.total_documents > 0:
                    original_size = vector_metrics.total_documents * 384 * 4  # float32
                    compressed_size = vector_metrics.storage_size_mb * 1024 * 1024
                    metrics["storage_efficiency"] = original_size / compressed_size if compressed_size > 0 else 0
                else:
                    metrics["storage_efficiency"] = 0.0
        
        except Exception as e:
            logger.error(f"收集压缩指标失败: {e}")
        
        return metrics

    async def _collect_ai_metrics(self) -> Dict[str, Any]:
        """收集AI指标"""
        metrics = {}
        
        try:
            if self._intelligent_processor:
                processor_metrics = await self._intelligent_processor.get_metrics()
                
                metrics["content_acceptance_rate"] = processor_metrics.acceptance_rate
                metrics["avg_value_score"] = processor_metrics.avg_value_score
                
                # AI准确性评估（基于接受率和平均分数）
                accuracy = (processor_metrics.acceptance_rate + processor_metrics.avg_value_score) / 2
                metrics["ai_accuracy_rate"] = accuracy
        
        except Exception as e:
            logger.error(f"收集AI指标失败: {e}")
        
        return metrics

    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """收集性能指标"""
        metrics = {}
        
        try:
            # 智能处理器性能
            if self._intelligent_processor:
                processor_metrics = await self._intelligent_processor.get_metrics()
                metrics["avg_processing_time_ms"] = processor_metrics.avg_processing_time_ms
            
            # 向量搜索性能
            if self._vector_store:
                vector_metrics = await self._vector_store.get_metrics()
                metrics["avg_search_time_ms"] = vector_metrics.avg_search_time_ms
            
            # Ollama性能
            if self._ollama_service:
                ollama_metrics = await self._ollama_service.get_metrics()
                metrics["avg_embedding_time_ms"] = ollama_metrics.avg_embedding_time_ms
        
        except Exception as e:
            logger.error(f"收集性能指标失败: {e}")
        
        return metrics

    async def _collect_tier_metrics(self) -> Dict[str, Any]:
        """收集分层存储指标"""
        metrics = {}
        
        try:
            if self._vector_store:
                vector_metrics = await self._vector_store.get_metrics()
                total_shards = vector_metrics.total_shards
                
                if total_shards > 0:
                    metrics["hot_data_percentage"] = (vector_metrics.hot_shards / total_shards) * 100
                    metrics["warm_data_percentage"] = (vector_metrics.warm_shards / total_shards) * 100
                    metrics["cold_data_percentage"] = (vector_metrics.cold_shards / total_shards) * 100
                else:
                    metrics["hot_data_percentage"] = 0.0
                    metrics["warm_data_percentage"] = 0.0
                    metrics["cold_data_percentage"] = 0.0
        
        except Exception as e:
            logger.error(f"收集分层指标失败: {e}")
        
        return metrics

    async def _collect_health_metrics(self) -> Dict[str, Any]:
        """收集健康状态指标"""
        metrics = {}
        
        try:
            # Ollama状态
            if self._ollama_service:
                try:
                    await self._ollama_service.embed_text("health check")
                    metrics["ollama_status"] = "healthy"
                except:
                    metrics["ollama_status"] = "unhealthy"
            else:
                metrics["ollama_status"] = "unavailable"
            
            # 向量存储状态
            if self._vector_store:
                try:
                    vector_metrics = await self._vector_store.get_metrics()
                    metrics["vector_store_status"] = "healthy" if vector_metrics.total_shards >= 0 else "unhealthy"
                except:
                    metrics["vector_store_status"] = "unhealthy"
            else:
                metrics["vector_store_status"] = "unavailable"
            
            # 数据库状态
            if self._db_service:
                try:
                    with self._db_service.get_session() as session:
                        session.execute("SELECT 1")
                    metrics["database_status"] = "healthy"
                except:
                    metrics["database_status"] = "unhealthy"
            else:
                metrics["database_status"] = "unavailable"
        
        except Exception as e:
            logger.error(f"收集健康指标失败: {e}")
        
        return metrics

    async def _collect_error_metrics(self) -> Dict[str, Any]:
        """收集错误指标"""
        metrics = {}
        
        try:
            # 从日志文件中统计错误
            log_dir = self.config.storage_dir / "logs"
            if log_dir.exists():
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                
                error_count = 0
                warning_count = 0
                
                for log_file in log_dir.glob("*.log"):
                    try:
                        if log_file.stat().st_mtime > cutoff_time.timestamp():
                            with open(log_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                error_count += content.count("ERROR")
                                warning_count += content.count("WARNING")
                    except:
                        pass
                
                metrics["error_count_24h"] = error_count
                metrics["warning_count_24h"] = warning_count
            else:
                metrics["error_count_24h"] = 0
                metrics["warning_count_24h"] = 0
        
        except Exception as e:
            logger.error(f"收集错误指标失败: {e}")
        
        return metrics

    # === 后台收集 ===

    async def _start_metrics_collection(self):
        """启动后台指标收集"""
        self._is_collecting = True
        asyncio.create_task(self._metrics_collection_loop())
        logger.info("后台指标收集已启动")

    async def _metrics_collection_loop(self):
        """指标收集循环"""
        while self._is_collecting:
            try:
                # 收集指标
                metrics = await self.collect_current_metrics()
                
                # 添加到历史记录
                self._metrics_history.append(metrics)
                
                # 限制历史记录大小
                if len(self._metrics_history) > self._max_history:
                    self._metrics_history = self._metrics_history[-self._max_history:]
                
                # 检查告警
                await self._check_alerts(metrics)
                
                # 定期保存
                if len(self._metrics_history) % 10 == 0:
                    await self._save_metrics_history()
                
                # 等待下次收集
                await asyncio.sleep(self._collection_interval)
                
            except Exception as e:
                logger.error(f"指标收集循环异常: {e}")
                await asyncio.sleep(60)  # 异常时等待1分钟

    # === 告警系统 ===

    def _setup_default_alert_rules(self):
        """设置默认告警规则"""
        self._alert_rules = [
            # 压缩比告警
            AlertRule(
                rule_id="compression_ratio_low",
                metric_name="compression_ratio",
                threshold=self.config.monitoring.compression_ratio_threshold,
                operator="lt",
                severity="warning",
                description="存储压缩比过低",
            ),
            
            # AI准确性告警
            AlertRule(
                rule_id="ai_accuracy_low",
                metric_name="ai_accuracy_rate",
                threshold=self.config.monitoring.ai_accuracy_threshold,
                operator="lt",
                severity="critical",
                description="AI评估准确性过低",
            ),
            
            # 内存使用告警
            AlertRule(
                rule_id="memory_usage_high",
                metric_name="memory_usage_mb",
                threshold=1024.0,  # 1GB
                operator="gt",
                severity="warning",
                description="内存使用过高",
            ),
            
            # 错误率告警
            AlertRule(
                rule_id="error_rate_high",
                metric_name="error_count_24h",
                threshold=50.0,
                operator="gt",
                severity="critical",
                description="24小时错误数过多",
            ),
            
            # 服务健康告警
            AlertRule(
                rule_id="ollama_unhealthy",
                metric_name="ollama_status",
                threshold=0.0,  # 用于字符串比较
                operator="eq",
                severity="critical",
                description="Ollama服务不健康",
            ),
        ]

    async def _check_alerts(self, metrics: StorageMetrics):
        """检查告警"""
        if not self.config.monitoring.performance_alerts:
            return
        
        current_time = datetime.utcnow()
        
        for rule in self._alert_rules:
            if not rule.enabled:
                continue
            
            try:
                # 获取指标值
                metric_value = getattr(metrics, rule.metric_name, None)
                if metric_value is None:
                    continue
                
                # 字符串类型特殊处理
                if isinstance(metric_value, str):
                    if rule.operator == "eq" and metric_value == "unhealthy":
                        await self._trigger_alert(rule, metric_value, current_time)
                    continue
                
                # 数值类型比较
                triggered = False
                if rule.operator == "gt" and metric_value > rule.threshold:
                    triggered = True
                elif rule.operator == "lt" and metric_value < rule.threshold:
                    triggered = True
                elif rule.operator == "eq" and metric_value == rule.threshold:
                    triggered = True
                
                if triggered:
                    await self._trigger_alert(rule, metric_value, current_time)
                else:
                    await self._resolve_alert(rule.rule_id, current_time)
                    
            except Exception as e:
                logger.error(f"检查告警规则失败 [{rule.rule_id}]: {e}")

    async def _trigger_alert(self, rule: AlertRule, current_value: Any, timestamp: datetime):
        """触发告警"""
        # 检查是否已有活跃告警
        existing_alert = next((a for a in self._active_alerts 
                             if a.rule_id == rule.rule_id and not a.resolved), None)
        
        if existing_alert:
            # 更新现有告警
            existing_alert.current_value = current_value
            existing_alert.timestamp = timestamp
        else:
            # 创建新告警
            alert = Alert(
                alert_id=f"{rule.rule_id}_{int(timestamp.timestamp())}",
                rule_id=rule.rule_id,
                metric_name=rule.metric_name,
                current_value=current_value,
                threshold=rule.threshold,
                severity=rule.severity,
                description=rule.description,
                timestamp=timestamp,
            )
            
            self._active_alerts.append(alert)
            logger.warning(f"🚨 触发告警: {rule.description} - 当前值: {current_value}, 阈值: {rule.threshold}")

    async def _resolve_alert(self, rule_id: str, timestamp: datetime):
        """解决告警"""
        for alert in self._active_alerts:
            if alert.rule_id == rule_id and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = timestamp
                logger.info(f"✅ 告警已解决: {alert.description}")

    # === 数据持久化 ===

    async def _save_metrics_history(self):
        """保存指标历史"""
        try:
            # 按日期分组保存
            today = datetime.utcnow().strftime("%Y-%m-%d")
            metrics_file = self.metrics_dir / f"metrics_{today}.json"
            
            # 转换为JSON可序列化格式
            metrics_data = []
            for metric in self._metrics_history:
                metric_dict = asdict(metric)
                metric_dict["timestamp"] = metric.timestamp.isoformat()
                metrics_data.append(metric_dict)
            
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"保存指标历史失败: {e}")

    async def _load_metrics_history(self):
        """加载指标历史"""
        try:
            # 加载最近7天的指标
            for i in range(7):
                date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
                metrics_file = self.metrics_dir / f"metrics_{date}.json"
                
                if metrics_file.exists():
                    with open(metrics_file, 'r', encoding='utf-8') as f:
                        metrics_data = json.load(f)
                    
                    for metric_dict in metrics_data:
                        metric_dict["timestamp"] = datetime.fromisoformat(metric_dict["timestamp"])
                        metrics = StorageMetrics(**metric_dict)
                        self._metrics_history.append(metrics)
            
            # 按时间排序
            self._metrics_history.sort(key=lambda x: x.timestamp)
            
            # 限制大小
            if len(self._metrics_history) > self._max_history:
                self._metrics_history = self._metrics_history[-self._max_history:]
                
        except Exception as e:
            logger.error(f"加载指标历史失败: {e}")

    # === 公共接口 ===

    async def get_current_metrics(self) -> StorageMetrics:
        """获取当前指标"""
        return await self.collect_current_metrics()

    async def get_metrics_history(self, hours: int = 24) -> List[StorageMetrics]:
        """获取指标历史"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [m for m in self._metrics_history if m.timestamp >= cutoff_time]

    async def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        return [a for a in self._active_alerts if not a.resolved]

    async def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """获取指标摘要"""
        history = await self.get_metrics_history(hours)
        
        if not history:
            return {"error": "无历史数据"}
        
        # 计算统计值
        latest = history[-1]
        
        # 趋势分析
        if len(history) > 1:
            first = history[0]
            document_growth = latest.total_documents - first.total_documents
            storage_growth = latest.storage_size_mb - first.storage_size_mb
        else:
            document_growth = 0
            storage_growth = 0.0
        
        return {
            "current": asdict(latest),
            "trends": {
                "document_growth": document_growth,
                "storage_growth_mb": storage_growth,
                "avg_compression_ratio": sum(m.compression_ratio for m in history) / len(history),
                "avg_ai_accuracy": sum(m.ai_accuracy_rate for m in history) / len(history),
            },
            "health": {
                "ollama_uptime_percentage": len([m for m in history if m.ollama_status == "healthy"]) / len(history) * 100,
                "error_trend": "increasing" if latest.error_count_24h > 10 else "stable",
            },
            "active_alerts": len(await self.get_active_alerts()),
        }


# === 服务单例管理 ===

_storage_metrics: Optional[StorageMetricsCollector] = None

async def get_storage_metrics_collector() -> StorageMetricsCollector:
    """获取存储指标收集器实例（单例模式）"""
    global _storage_metrics
    if _storage_metrics is None:
        _storage_metrics = StorageMetricsCollector()
        if not await _storage_metrics.initialize():
            raise RuntimeError("存储指标收集器初始化失败")
    return _storage_metrics

async def cleanup_storage_metrics():
    """清理存储指标收集器"""
    global _storage_metrics
    if _storage_metrics:
        await _storage_metrics.close()
        _storage_metrics = None