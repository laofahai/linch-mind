"""
系统资源保护监控器 - 防止连接器进程CPU风暴和系统调用失控
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

import psutil

from core.service_facade import get_service

logger = logging.getLogger(__name__)


@dataclass
class ResourceThreshold:
    """资源阈值配置"""
    cpu_warning: float = 80.0      # CPU使用率警告阈值 (%)
    cpu_critical: float = 95.0     # CPU使用率危险阈值 (%)
    memory_warning: float = 70.0   # 内存使用率警告阈值 (%)
    memory_critical: float = 90.0  # 内存使用率危险阈值 (%)
    syscall_rate_warning: int = 1000  # 系统调用速率警告阈值 (次/秒)
    syscall_rate_critical: int = 5000  # 系统调用速率危险阈值 (次/秒)


@dataclass
class ProcessResourceUsage:
    """进程资源使用情况"""
    pid: int
    connector_id: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    syscall_rate: float
    timestamp: datetime
    
    
class ResourceProtectionMonitor:
    """系统资源保护监控器"""
    
    def __init__(self):
        self.thresholds = ResourceThreshold()
        
        # 监控状态
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        
        # 资源历史记录
        self._resource_history: Dict[str, List[ProcessResourceUsage]] = {}
        self._history_max_size = 60  # 保持60次记录（约5分钟历史）
        
        # 违规记录
        self._violation_counts: Dict[str, int] = {}
        self._last_violation_times: Dict[str, datetime] = {}
        
        # 紧急停止状态
        self._emergency_stopped: Set[str] = set()
        
        # 监控参数
        self.monitor_interval = 5.0  # 5秒监控间隔
        self.violation_threshold = 3  # 连续违规3次触发保护动作
        self.protection_cooldown = 300  # 保护动作冷却期5分钟
        
        logger.info("系统资源保护监控器初始化完成")
    
    async def start_monitoring(self):
        """启动资源监控"""
        if self._monitoring:
            logger.warning("资源监控已在运行")
            return
            
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("🛡️  系统资源保护监控已启动")
    
    async def stop_monitoring(self):
        """停止资源监控"""
        if not self._monitoring:
            return
            
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("系统资源保护监控已停止")
    
    async def _monitor_loop(self):
        """监控循环"""
        while self._monitoring:
            try:
                await self._perform_resource_check()
                await asyncio.sleep(self.monitor_interval)
            except asyncio.CancelledError:
                logger.info("资源监控循环被取消")
                break
            except Exception as e:
                logger.error(f"资源监控异常: {e}")
                await asyncio.sleep(self.monitor_interval * 2)
    
    async def _perform_resource_check(self):
        """执行资源检查"""
        from services.connectors.connector_manager import ConnectorManager
        
        try:
            connector_manager = get_service(ConnectorManager)
            running_connectors = connector_manager.get_running_connectors()
            
            for connector_id in running_connectors:
                await self._check_connector_resources(connector_id, connector_manager)
                
        except Exception as e:
            logger.error(f"资源检查失败: {e}")
    
    async def _check_connector_resources(self, connector_id: str, connector_manager):
        """检查单个连接器的资源使用"""
        try:
            process_info = connector_manager.get_process_info(connector_id)
            if not process_info or not process_info.get("pid"):
                return
                
            pid = process_info["pid"]
            
            try:
                process = psutil.Process(pid)
                
                # 获取资源使用情况
                cpu_percent = process.cpu_percent(interval=0.1)
                memory_info = process.memory_info()
                memory_percent = process.memory_percent()
                memory_mb = memory_info.rss / 1024 / 1024
                
                # 计算系统调用速率（如果可用）
                syscall_rate = 0.0
                try:
                    # macOS 上系统调用信息可能不直接可用
                    io_counters = process.io_counters()
                    if hasattr(io_counters, 'other_count'):
                        # 估算系统调用速率
                        syscall_rate = io_counters.other_count / max(time.time() - process.create_time(), 1)
                except (AttributeError, psutil.AccessDenied):
                    pass
                
                # 记录资源使用情况
                usage = ProcessResourceUsage(
                    pid=pid,
                    connector_id=connector_id,
                    cpu_percent=cpu_percent,
                    memory_percent=memory_percent,
                    memory_mb=memory_mb,
                    syscall_rate=syscall_rate,
                    timestamp=datetime.now()
                )
                
                self._record_usage(connector_id, usage)
                
                # 检查是否超过阈值
                await self._check_thresholds(usage, connector_manager)
                
            except psutil.NoSuchProcess:
                logger.debug(f"连接器 {connector_id} 进程已不存在")
                self._clear_history(connector_id)
            except psutil.AccessDenied:
                logger.debug(f"无法访问连接器 {connector_id} 进程信息")
                
        except Exception as e:
            logger.error(f"检查连接器 {connector_id} 资源使用失败: {e}")
    
    def _record_usage(self, connector_id: str, usage: ProcessResourceUsage):
        """记录资源使用历史"""
        if connector_id not in self._resource_history:
            self._resource_history[connector_id] = []
            
        history = self._resource_history[connector_id]
        history.append(usage)
        
        # 保持历史记录大小限制
        if len(history) > self._history_max_size:
            history.pop(0)
    
    async def _check_thresholds(self, usage: ProcessResourceUsage, connector_manager):
        """检查资源使用阈值"""
        connector_id = usage.connector_id
        violations = []
        
        # 检查CPU使用率
        if usage.cpu_percent > self.thresholds.cpu_critical:
            violations.append(f"CPU使用率危险: {usage.cpu_percent:.1f}%")
        elif usage.cpu_percent > self.thresholds.cpu_warning:
            logger.warning(f"⚠️  连接器 {connector_id} CPU使用率较高: {usage.cpu_percent:.1f}%")
        
        # 检查内存使用率
        if usage.memory_percent > self.thresholds.memory_critical:
            violations.append(f"内存使用率危险: {usage.memory_percent:.1f}% ({usage.memory_mb:.1f}MB)")
        elif usage.memory_percent > self.thresholds.memory_warning:
            logger.warning(f"⚠️  连接器 {connector_id} 内存使用率较高: {usage.memory_percent:.1f}%")
        
        # 检查系统调用速率
        if usage.syscall_rate > self.thresholds.syscall_rate_critical:
            violations.append(f"系统调用速率危险: {usage.syscall_rate:.0f}/s")
        elif usage.syscall_rate > self.thresholds.syscall_rate_warning:
            logger.warning(f"⚠️  连接器 {connector_id} 系统调用速率较高: {usage.syscall_rate:.0f}/s")
        
        # 如果有违规行为
        if violations:
            await self._handle_violations(connector_id, violations, connector_manager)
        else:
            # 清除违规记录
            self._violation_counts.pop(connector_id, None)
    
    async def _handle_violations(self, connector_id: str, violations: List[str], connector_manager):
        """处理资源违规"""
        
        # 增加违规计数
        self._violation_counts[connector_id] = self._violation_counts.get(connector_id, 0) + 1
        violation_count = self._violation_counts[connector_id]
        
        violation_msg = "; ".join(violations)
        logger.error(
            f"🚨 连接器 {connector_id} 资源违规 (第{violation_count}次): {violation_msg}"
        )
        
        # 连续违规达到阈值，采取保护动作
        if violation_count >= self.violation_threshold:
            await self._take_protection_action(connector_id, connector_manager)
    
    async def _take_protection_action(self, connector_id: str, connector_manager):
        """采取资源保护动作"""
        
        # 检查冷却期
        last_action_time = self._last_violation_times.get(connector_id)
        if last_action_time:
            elapsed = (datetime.now() - last_action_time).total_seconds()
            if elapsed < self.protection_cooldown:
                logger.info(f"连接器 {connector_id} 在保护动作冷却期内")
                return
        
        self._last_violation_times[connector_id] = datetime.now()
        
        logger.error(f"🛑 对连接器 {connector_id} 采取紧急资源保护动作：强制重启")
        
        try:
            # 标记为紧急停止状态
            self._emergency_stopped.add(connector_id)
            
            # 强制重启连接器
            success = await connector_manager.restart_connector(connector_id)
            
            if success:
                logger.info(f"✅ 连接器 {connector_id} 紧急重启成功")
                # 清除违规记录
                self._violation_counts.pop(connector_id, None)
                self._clear_history(connector_id)
            else:
                logger.error(f"❌ 连接器 {connector_id} 紧急重启失败")
                
        except Exception as e:
            logger.error(f"对连接器 {connector_id} 执行保护动作失败: {e}")
        finally:
            # 移除紧急停止标记
            self._emergency_stopped.discard(connector_id)
    
    def _clear_history(self, connector_id: str):
        """清理连接器历史记录"""
        self._resource_history.pop(connector_id, None)
        self._violation_counts.pop(connector_id, None)
    
    def get_resource_stats(self, connector_id: str) -> Dict:
        """获取连接器资源统计"""
        history = self._resource_history.get(connector_id, [])
        if not history:
            return {"status": "no_data"}
        
        latest = history[-1]
        
        # 计算平均值（最近10个记录）
        recent_history = history[-10:]
        avg_cpu = sum(r.cpu_percent for r in recent_history) / len(recent_history)
        avg_memory = sum(r.memory_percent for r in recent_history) / len(recent_history)
        
        return {
            "status": "active",
            "latest": {
                "cpu_percent": latest.cpu_percent,
                "memory_percent": latest.memory_percent,
                "memory_mb": latest.memory_mb,
                "syscall_rate": latest.syscall_rate,
                "timestamp": latest.timestamp.isoformat()
            },
            "averages": {
                "cpu_percent": avg_cpu,
                "memory_percent": avg_memory
            },
            "violations": {
                "count": self._violation_counts.get(connector_id, 0),
                "last_violation": self._last_violation_times.get(connector_id)
            },
            "emergency_stopped": connector_id in self._emergency_stopped
        }
    
    def get_system_protection_stats(self) -> Dict:
        """获取系统保护统计"""
        return {
            "monitoring_active": self._monitoring,
            "monitor_interval": self.monitor_interval,
            "thresholds": {
                "cpu_warning": self.thresholds.cpu_warning,
                "cpu_critical": self.thresholds.cpu_critical,
                "memory_warning": self.thresholds.memory_warning,
                "memory_critical": self.thresholds.memory_critical,
                "syscall_rate_warning": self.thresholds.syscall_rate_warning,
                "syscall_rate_critical": self.thresholds.syscall_rate_critical
            },
            "protected_connectors": len(self._resource_history),
            "total_violations": sum(self._violation_counts.values()),
            "emergency_stopped_count": len(self._emergency_stopped)
        }
    
    def update_thresholds(self, **kwargs):
        """更新保护阈值"""
        for key, value in kwargs.items():
            if hasattr(self.thresholds, key):
                setattr(self.thresholds, key, value)
                logger.info(f"更新保护阈值 {key} = {value}")