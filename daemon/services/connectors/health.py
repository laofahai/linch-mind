import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional

import psutil

from models.api_models import ConnectorStatus

logger = logging.getLogger(__name__)


class ConnectorHealthChecker:
    """连接器健康检查器 - 单一职责：监控和重启管理"""

    def __init__(self, runtime_manager):
        self.runtime_manager = runtime_manager

        # 重启管理
        self.restart_counts: Dict[str, int] = {}
        self.last_restart_times: Dict[str, datetime] = {}
        self.auto_restart_enabled: Dict[str, bool] = {}

        # 配置参数
        self.max_restart_attempts = 3
        self.restart_cooldown = 60  # 秒
        self.restart_interval = 5  # 秒
        self.health_check_interval = 10  # 秒

        # 监控任务
        self._health_monitor_task: Optional[asyncio.Task] = None

        logger.info(
            f"ConnectorHealthChecker初始化 - 检查间隔: {self.health_check_interval}秒"
        )

    async def start_monitoring(self):
        """启动健康监控"""
        if self._health_monitor_task and not self._health_monitor_task.done():
            logger.warning("健康监控已在运行")
            return

        self._health_monitor_task = asyncio.create_task(self._health_monitor_loop())
        logger.info("🏥 健康监控已启动")

    async def stop_monitoring(self):
        """停止健康监控"""
        if self._health_monitor_task:
            self._health_monitor_task.cancel()
            try:
                await self._health_monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("健康监控已停止")

    async def _health_monitor_loop(self):
        """健康监控循环"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_check()
            except asyncio.CancelledError:
                logger.info("健康监控循环被取消")
                break
            except Exception as e:
                logger.error(f"健康检查监控器错误: {e}")
                await asyncio.sleep(
                    self.health_check_interval * 2
                )  # 出错时等待双倍时间

    async def _perform_health_check(self):
        """执行健康检查"""
        running_connectors = self.runtime_manager.get_running_connectors()

        for connector_id in running_connectors:
            await self._check_connector_health(connector_id)

    async def _check_connector_health(self, connector_id: str):
        """检查单个连接器健康状态"""
        try:
            process_info = self.runtime_manager.get_process_info(connector_id)
            if not process_info:
                logger.debug(f"连接器 {connector_id} 无进程信息")
                return

            pid = process_info["pid"]

            # 使用psutil检查进程状态
            try:
                psutil_process = psutil.Process(pid)
                if not psutil_process.is_running():
                    logger.warning(
                        f"🔍 健康检查发现连接器 {connector_id} PID {pid} 已退出"
                    )
                    await self._handle_connector_failure(connector_id)
                else:
                    logger.debug(f"🔍 连接器 {connector_id} (PID: {pid}) 健康运行")
            except psutil.NoSuchProcess:
                logger.warning(f"🔍 健康检查发现连接器 {connector_id} PID {pid} 不存在")
                await self._handle_connector_failure(connector_id)

        except Exception as e:
            logger.error(f"检查连接器 {connector_id} 健康状态时出错: {e}")

    async def _handle_connector_failure(self, connector_id: str):
        """处理连接器失败"""
        # 检查是否启用自动重启
        if not self.auto_restart_enabled.get(connector_id, True):
            logger.info(f"连接器 {connector_id} 自动重启已禁用")
            return

        # 检查重启次数限制
        current_restart_count = self.restart_counts.get(connector_id, 0)
        if current_restart_count >= self.max_restart_attempts:
            logger.error(
                f"连接器 {connector_id} 已达到最大重启次数 ({self.max_restart_attempts})，停止自动重启"
            )
            return

        # 检查重启冷却时间
        last_restart = self.last_restart_times.get(connector_id)
        if last_restart:
            time_since_last = (datetime.now() - last_restart).total_seconds()
            if time_since_last < self.restart_cooldown:
                remaining_cooldown = self.restart_cooldown - time_since_last
                logger.warning(
                    f"连接器 {connector_id} 在冷却期内，还需等待 {remaining_cooldown:.1f} 秒后才能重启"
                )
                return

        # 执行重启
        await self._attempt_restart(connector_id)

    async def _attempt_restart(self, connector_id: str):
        """尝试重启连接器"""
        # 增加重启计数
        self.restart_counts[connector_id] = self.restart_counts.get(connector_id, 0) + 1
        self.last_restart_times[connector_id] = datetime.now()

        logger.info(
            f"准备重启连接器 {connector_id} (第 {self.restart_counts[connector_id]}/{self.max_restart_attempts} 次尝试)"
        )

        # 等待重启间隔
        await asyncio.sleep(self.restart_interval)

        # 这里需要通过回调或者事件通知主系统进行重启
        # 因为HealthChecker不应该直接依赖具体的连接器配置
        logger.info(f"触发连接器 {connector_id} 重启信号")
        # TODO: 实现重启信号机制

    def get_connector_status(self, connector_id: str) -> ConnectorStatus:
        """获取连接器状态"""
        if not self.runtime_manager.is_connector_running(connector_id):
            return ConnectorStatus.INSTALLED

        process_info = self.runtime_manager.get_process_info(connector_id)
        if not process_info:
            return ConnectorStatus.INSTALLED

        pid = process_info["pid"]

        try:
            psutil_process = psutil.Process(pid)
            if psutil_process.is_running():
                return ConnectorStatus.RUNNING
            else:
                return ConnectorStatus.INSTALLED
        except psutil.NoSuchProcess:
            return ConnectorStatus.INSTALLED
        except Exception:
            return ConnectorStatus.ERROR

    def enable_auto_restart(self, connector_id: str, enabled: bool = True):
        """启用/禁用连接器自动重启"""
        self.auto_restart_enabled[connector_id] = enabled
        logger.info(f"连接器 {connector_id} 自动重启 {'启用' if enabled else '禁用'}")

    def reset_restart_count(self, connector_id: str):
        """重置连接器重启计数"""
        self.restart_counts[connector_id] = 0
        self.last_restart_times.pop(connector_id, None)
        logger.info(f"已重置连接器 {connector_id} 的重启计数")

    def get_restart_stats(self, connector_id: str) -> dict:
        """获取连接器重启统计信息"""
        return {
            "restart_count": self.restart_counts.get(connector_id, 0),
            "max_restart_attempts": self.max_restart_attempts,
            "auto_restart_enabled": self.auto_restart_enabled.get(connector_id, True),
            "last_restart_time": self.last_restart_times.get(connector_id),
            "restart_cooldown": self.restart_cooldown,
            "restart_interval": self.restart_interval,
        }

    def get_health_stats(self) -> dict:
        """获取整体健康统计"""
        running_count = len(self.runtime_manager.get_running_connectors())
        total_restarts = sum(self.restart_counts.values())

        return {
            "running_connectors": running_count,
            "total_restarts": total_restarts,
            "health_check_interval": self.health_check_interval,
            "monitoring_active": self._health_monitor_task
            and not self._health_monitor_task.done(),
        }

    def update_config(self, config: dict):
        """更新健康检查配置"""
        if "max_restart_attempts" in config:
            self.max_restart_attempts = config["max_restart_attempts"]
        if "restart_cooldown" in config:
            self.restart_cooldown = config["restart_cooldown"]
        if "restart_interval" in config:
            self.restart_interval = config["restart_interval"]
        if "health_check_interval" in config:
            self.health_check_interval = config["health_check_interval"]

        logger.info(f"健康检查配置已更新: {config}")
