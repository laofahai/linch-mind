#!/usr/bin/env python3
"""
重构后的数据生命周期管理器 - 简化版本
将原885行的巨型文件拆分为多个专门的组件
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from .data_cleanup_engine import DataCleanupEngine
from .data_archiver import DataArchiver
from .performance_optimizer import PerformanceOptimizer
from .data_health_monitor import DataHealthMonitor, DataHealthReport

logger = logging.getLogger(__name__)


@dataclass
class DataLifecycleConfig:
    """数据生命周期配置"""
    
    # 数据保留策略
    entity_retention_days: int = 90
    behavior_retention_days: int = 30
    conversation_retention_days: int = 60

    # 清理策略
    auto_cleanup_enabled: bool = True
    cleanup_interval_hours: int = 24
    max_storage_gb: float = 10.0

    # 归档策略
    archive_enabled: bool = True
    archive_threshold_days: int = 30
    compressed_archive: bool = True

    # 性能优化
    auto_vacuum_enabled: bool = True
    index_optimization_enabled: bool = True
    cache_cleanup_enabled: bool = True


class DataLifecycleManager:
    """重构后的数据生命周期管理器
    
    职责分离：
    - DataCleanupEngine: 处理数据清理
    - DataArchiver: 处理数据归档
    - PerformanceOptimizer: 处理性能优化
    - DataHealthMonitor: 处理健康监控
    """

    def __init__(self, config: Optional[DataLifecycleConfig] = None):
        self.config = config or DataLifecycleConfig()
        
        # 初始化各个专门的组件
        self.cleanup_engine = DataCleanupEngine(self.config)
        self.archiver = DataArchiver(self.config)
        self.performance_optimizer = PerformanceOptimizer(self.config)
        self.health_monitor = DataHealthMonitor(self.config)

        # 任务状态
        self._cleanup_task: Optional[asyncio.Task] = None
        self._optimization_task: Optional[asyncio.Task] = None
        self._running = False

    async def initialize(self) -> bool:
        """初始化数据生命周期管理器"""
        try:
            logger.info("初始化数据生命周期管理器...")

            # 初始化所有组件
            init_results = await asyncio.gather(
                self.cleanup_engine.initialize(),
                self.archiver.initialize(),
                self.performance_optimizer.initialize(),
                self.health_monitor.initialize(),
                return_exceptions=True
            )

            # 检查初始化结果
            failed_components = []
            for i, result in enumerate(init_results):
                if isinstance(result, Exception) or not result:
                    component_names = ["cleanup_engine", "archiver", "performance_optimizer", "health_monitor"]
                    failed_components.append(component_names[i])

            if failed_components:
                logger.warning(f"部分组件初始化失败: {failed_components}")

            # 启动自动任务
            if self.config.auto_cleanup_enabled:
                self._cleanup_task = asyncio.create_task(self._auto_cleanup_task())

            if (
                self.config.auto_vacuum_enabled
                or self.config.index_optimization_enabled
            ):
                self._optimization_task = asyncio.create_task(
                    self._auto_optimization_task()
                )

            self._running = True

            # 生成初始健康报告
            await self.generate_health_report()

            logger.info("数据生命周期管理器初始化完成")
            return True

        except Exception as e:
            logger.error(f"数据生命周期管理器初始化失败: {e}")
            return False

    async def close(self):
        """关闭数据生命周期管理器"""
        try:
            self._running = False

            # 取消自动任务
            if self._cleanup_task:
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass

            if self._optimization_task:
                self._optimization_task.cancel()
                try:
                    await self._optimization_task
                except asyncio.CancelledError:
                    pass

            logger.info("数据生命周期管理器已关闭")

        except Exception as e:
            logger.error(f"关闭数据生命周期管理器失败: {e}")

    # === 委托给专门组件的方法 ===

    async def cleanup_expired_data(self) -> Dict[str, int]:
        """清理过期数据"""
        return await self.cleanup_engine.cleanup_expired_data()

    async def cleanup_by_storage_limit(self) -> Dict[str, int]:
        """基于存储限制清理数据"""
        return await self.cleanup_engine.cleanup_by_storage_limit()

    async def archive_old_data(self) -> Dict[str, int]:
        """归档旧数据"""
        return await self.archiver.archive_old_data()

    async def list_archives(self):
        """列出所有归档"""
        return await self.archiver.list_archives()

    async def restore_archive(self, archive_id: str) -> bool:
        """恢复归档数据"""
        return await self.archiver.restore_archive(archive_id)

    async def delete_archive(self, archive_id: str) -> bool:
        """删除归档"""
        return await self.archiver.delete_archive(archive_id)

    async def optimize_database_performance(self) -> Dict[str, bool]:
        """优化数据库性能"""
        return await self.performance_optimizer.optimize_database_performance()

    async def get_performance_metrics(self) -> Dict:
        """获取性能指标"""
        return await self.performance_optimizer.get_performance_metrics()

    async def suggest_optimizations(self) -> Dict:
        """建议性能优化方案"""
        return await self.performance_optimizer.suggest_optimizations()

    async def benchmark_query_performance(self, test_queries: list = None) -> Dict:
        """基准测试查询性能"""
        return await self.performance_optimizer.benchmark_query_performance(test_queries)

    async def generate_health_report(self) -> DataHealthReport:
        """生成数据健康报告"""
        return await self.health_monitor.generate_health_report()

    def get_last_health_report(self) -> DataHealthReport:
        """获取上次的健康报告"""
        return self.health_monitor.get_last_report()

    async def get_health_summary(self) -> Dict:
        """获取健康状况摘要"""
        return await self.health_monitor.get_health_summary()

    # === 综合操作方法 ===

    async def full_maintenance(self) -> Dict:
        """执行完整维护操作"""
        try:
            logger.info("开始执行完整维护...")

            maintenance_results = {
                "cleanup_stats": {},
                "archive_stats": {},
                "optimization_results": {},
                "health_report": None,
                "duration_seconds": 0,
                "success": False
            }

            start_time = datetime.utcnow()

            try:
                # 1. 清理过期数据
                logger.info("步骤 1/4: 清理过期数据")
                maintenance_results["cleanup_stats"] = await self.cleanup_expired_data()

                # 2. 归档旧数据
                logger.info("步骤 2/4: 归档旧数据")
                maintenance_results["archive_stats"] = await self.archive_old_data()

                # 3. 优化数据库性能
                logger.info("步骤 3/4: 优化数据库性能")
                maintenance_results["optimization_results"] = await self.optimize_database_performance()

                # 4. 生成健康报告
                logger.info("步骤 4/4: 生成健康报告")
                maintenance_results["health_report"] = await self.generate_health_report()

                end_time = datetime.utcnow()
                maintenance_results["duration_seconds"] = (end_time - start_time).total_seconds()
                maintenance_results["success"] = True

                logger.info(f"完整维护完成，耗时: {maintenance_results['duration_seconds']:.2f}秒")

            except Exception as e:
                end_time = datetime.utcnow()
                maintenance_results["duration_seconds"] = (end_time - start_time).total_seconds()
                maintenance_results["error"] = str(e)
                logger.error(f"完整维护过程出错: {e}")

            return maintenance_results

        except Exception as e:
            logger.error(f"完整维护失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "duration_seconds": 0
            }

    # === 自动任务 ===

    async def _auto_cleanup_task(self):
        """自动清理任务"""
        while self._running:
            try:
                logger.info("执行自动清理任务...")
                
                # 清理过期数据
                cleanup_stats = await self.cleanup_expired_data()
                
                # 检查存储限制
                storage_cleanup_stats = await self.cleanup_by_storage_limit()
                
                # 合并统计
                total_cleaned = sum(cleanup_stats.values()) + sum(storage_cleanup_stats.values())
                
                if total_cleaned > 0:
                    logger.info(f"自动清理完成，清理项目: {total_cleaned}")
                else:
                    logger.debug("自动清理完成，无需清理")

                # 等待下次清理
                await asyncio.sleep(self.config.cleanup_interval_hours * 3600)

            except asyncio.CancelledError:
                logger.info("自动清理任务已取消")
                break
            except Exception as e:
                logger.error(f"自动清理任务出错: {e}")
                # 出错后等待较短时间再重试
                await asyncio.sleep(300)  # 5分钟

    async def _auto_optimization_task(self):
        """自动优化任务"""
        while self._running:
            try:
                logger.info("执行自动优化任务...")
                
                # 执行性能优化
                optimization_results = await self.optimize_database_performance()
                
                successful_ops = sum(optimization_results.values())
                logger.info(f"自动优化完成，成功操作: {successful_ops}")

                # 等待24小时后再次执行
                await asyncio.sleep(24 * 3600)

            except asyncio.CancelledError:
                logger.info("自动优化任务已取消")
                break
            except Exception as e:
                logger.error(f"自动优化任务出错: {e}")
                # 出错后等待较短时间再重试
                await asyncio.sleep(1800)  # 30分钟

    # === 状态查询 ===

    def is_running(self) -> bool:
        """检查管理器是否正在运行"""
        return self._running

    def get_task_status(self) -> Dict:
        """获取任务状态"""
        return {
            "running": self._running,
            "cleanup_task_active": self._cleanup_task is not None and not self._cleanup_task.done(),
            "optimization_task_active": self._optimization_task is not None and not self._optimization_task.done(),
            "auto_cleanup_enabled": self.config.auto_cleanup_enabled,
            "auto_optimization_enabled": (
                self.config.auto_vacuum_enabled or 
                self.config.index_optimization_enabled
            ),
        }

    def get_config(self) -> DataLifecycleConfig:
        """获取当前配置"""
        return self.config

    def update_config(self, new_config: DataLifecycleConfig):
        """更新配置"""
        self.config = new_config
        # 更新各个组件的配置
        self.cleanup_engine.config = new_config
        self.archiver.config = new_config
        self.performance_optimizer.config = new_config
        self.health_monitor.config = new_config
        logger.info("数据生命周期配置已更新")


# 兼容性函数
async def get_data_lifecycle_manager(
    config: Optional[DataLifecycleConfig] = None
) -> DataLifecycleManager:
    """获取数据生命周期管理器实例"""
    manager = DataLifecycleManager(config)
    await manager.initialize()
    return manager