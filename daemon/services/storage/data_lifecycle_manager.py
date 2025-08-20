#!/usr/bin/env python3
"""
数据生命周期管理器 - 自动化数据维护、归档和清理
实现分层存储的自动化管理：热数据→温数据→冷数据→清理
"""

import asyncio
import logging
import shutil
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.error_handling import handle_errors, ErrorSeverity, ErrorCategory
from core.service_facade import get_service
from config.intelligent_storage import get_intelligent_storage_config
from services.ai.ollama_service import get_ollama_service
from services.storage.faiss_vector_store import get_faiss_vector_store
from services.storage.core.database import UnifiedDatabaseService
from models.database_models import EntityMetadata
from services.shared_executor_service import get_shared_executor_service

logger = logging.getLogger(__name__)


@dataclass
class LifecycleMetrics:
    """生命周期管理指标"""
    total_processed: int
    hot_to_warm_migrations: int
    warm_to_cold_migrations: int
    cold_cleanups: int
    storage_reclaimed_mb: float
    index_optimizations: int
    backup_operations: int
    last_maintenance: datetime
    next_scheduled: datetime


@dataclass
class MaintenanceTask:
    """维护任务"""
    task_id: str
    task_type: str  # daily/weekly/monthly/quarterly
    description: str
    function_name: str
    schedule: str
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    enabled: bool = True


class DataLifecycleManager:
    """数据生命周期管理器 - 自动化维护系统"""

    def __init__(self):
        self.config = get_intelligent_storage_config()
        self.lifecycle_config = self.config.lifecycle
        
        # 服务依赖 - 懒加载
        self._ollama_service = None
        self._vector_store = None
        self._db_service = None
        
        # 任务调度
        self._executor = get_shared_executor_service()
        self._maintenance_tasks: List[MaintenanceTask] = []
        self._is_running = False
        self._maintenance_lock = asyncio.Lock()
        
        # 性能指标
        self._metrics = LifecycleMetrics(
            total_processed=0,
            hot_to_warm_migrations=0,
            warm_to_cold_migrations=0,
            cold_cleanups=0,
            storage_reclaimed_mb=0.0,
            index_optimizations=0,
            backup_operations=0,
            last_maintenance=datetime.utcnow(),
            next_scheduled=datetime.utcnow() + timedelta(days=1),
        )
        
        # 初始化维护任务
        self._setup_maintenance_tasks()

    async def initialize(self) -> bool:
        """初始化生命周期管理器"""
        try:
            # 获取服务依赖
            self._ollama_service = await get_ollama_service()
            self._vector_store = await get_faiss_vector_store()
            self._db_service = get_service(UnifiedDatabaseService)
            
            # 创建必要目录
            await self._ensure_directories()
            
            # 启动后台维护任务
            if self.lifecycle_config.auto_cleanup or self.lifecycle_config.auto_archival:
                await self._start_maintenance_scheduler()
            
            logger.info(f"数据生命周期管理器初始化完成 - 自动清理: {self.lifecycle_config.auto_cleanup}")
            return True
            
        except Exception as e:
            logger.error(f"数据生命周期管理器初始化失败: {e}")
            return False

    async def close(self):
        """关闭生命周期管理器"""
        try:
            self._is_running = False
            await self._save_maintenance_state()
            logger.info("数据生命周期管理器已关闭")
        except Exception as e:
            logger.error(f"关闭生命周期管理器失败: {e}")

    # === 维护任务调度 ===

    def _setup_maintenance_tasks(self):
        """设置维护任务"""
        self._maintenance_tasks = [
            # 每日任务
            MaintenanceTask(
                task_id="daily_incremental_merge",
                task_type="daily",
                description="每日增量合并和索引优化",
                function_name="_daily_maintenance",
                schedule="02:00",  # 凌晨2点
            ),
            
            # 每周任务
            MaintenanceTask(
                task_id="weekly_index_rebuild",
                task_type="weekly",
                description="每周索引重建和压缩",
                function_name="_weekly_optimization",
                schedule="Sun 03:00",  # 周日凌晨3点
            ),
            
            # 每月任务
            MaintenanceTask(
                task_id="monthly_tier_migration",
                task_type="monthly",
                description="每月冷热数据迁移",
                function_name="_monthly_archival",
                schedule="1st 04:00",  # 每月1号凌晨4点
            ),
            
            # 季度任务
            MaintenanceTask(
                task_id="quarterly_deep_clean",
                task_type="quarterly",
                description="季度价值重评估和深度清理",
                function_name="_quarterly_deep_clean",
                schedule="1st Jan/Apr/Jul/Oct 05:00",  # 季度首月1号凌晨5点
            ),
        ]

    async def _start_maintenance_scheduler(self):
        """启动维护任务调度器"""
        self._is_running = True
        
        # 计算下次执行时间
        for task in self._maintenance_tasks:
            task.next_run = self._calculate_next_run(task)
        
        # 启动后台调度循环
        asyncio.create_task(self._maintenance_loop())
        logger.info("维护任务调度器已启动")

    async def _maintenance_loop(self):
        """维护任务循环"""
        while self._is_running:
            try:
                await asyncio.sleep(60)  # 每分钟检查一次
                
                current_time = datetime.utcnow()
                for task in self._maintenance_tasks:
                    if (task.enabled and 
                        task.next_run and 
                        current_time >= task.next_run):
                        
                        await self._execute_maintenance_task(task)
                        task.last_run = current_time
                        task.next_run = self._calculate_next_run(task)
                        
            except Exception as e:
                logger.error(f"维护循环异常: {e}")
                await asyncio.sleep(300)  # 异常时等待5分钟

    async def _execute_maintenance_task(self, task: MaintenanceTask):
        """执行维护任务"""
        async with self._maintenance_lock:
            try:
                logger.info(f"开始执行维护任务: {task.description}")
                start_time = datetime.utcnow()
                
                # 根据函数名调用对应的维护方法
                if hasattr(self, task.function_name):
                    maintenance_func = getattr(self, task.function_name)
                    await maintenance_func()
                else:
                    logger.error(f"维护函数不存在: {task.function_name}")
                    return
                
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.info(f"维护任务完成: {task.description}, 耗时 {duration:.2f}s")
                
            except Exception as e:
                logger.error(f"维护任务执行失败 [{task.task_id}]: {e}")

    def _calculate_next_run(self, task: MaintenanceTask) -> datetime:
        """计算下次执行时间"""
        now = datetime.utcnow()
        
        if task.task_type == "daily":
            # 每日任务 - 下一个指定时间
            next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run
            
        elif task.task_type == "weekly":
            # 每周任务 - 下一个周日
            days_until_sunday = (6 - now.weekday()) % 7
            if days_until_sunday == 0 and now.hour >= 3:
                days_until_sunday = 7
            next_run = now + timedelta(days=days_until_sunday)
            return next_run.replace(hour=3, minute=0, second=0, microsecond=0)
            
        elif task.task_type == "monthly":
            # 每月任务 - 下月1号
            if now.day == 1 and now.hour < 4:
                next_run = now.replace(hour=4, minute=0, second=0, microsecond=0)
            else:
                if now.month == 12:
                    next_run = now.replace(year=now.year+1, month=1, day=1, hour=4, minute=0, second=0, microsecond=0)
                else:
                    next_run = now.replace(month=now.month+1, day=1, hour=4, minute=0, second=0, microsecond=0)
            return next_run
            
        elif task.task_type == "quarterly":
            # 季度任务 - 下一季度首月1号
            quarter_months = [1, 4, 7, 10]
            current_quarter = (now.month - 1) // 3
            next_quarter_month = quarter_months[(current_quarter + 1) % 4]
            
            if next_quarter_month <= now.month:
                next_year = now.year + 1
            else:
                next_year = now.year
                
            return datetime(next_year, next_quarter_month, 1, 5, 0, 0)
        
        # 默认1天后
        return now + timedelta(days=1)

    # === 维护操作实现 ===

    @handle_errors(
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.MAINTENANCE_OPERATION,
        user_message="每日维护失败"
    )
    async def _daily_maintenance(self):
        """每日维护：增量合并和索引优化"""
        try:
            logger.info("开始每日维护...")
            
            # 1. 保存当前分片索引
            if self._vector_store and self._vector_store.current_shard:
                await self._vector_store._save_current_shard()
                logger.debug("当前分片索引已保存")
            
            # 2. 清理过期临时文件
            temp_dir = self.config.temp_dir
            if temp_dir and temp_dir.exists():
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                await self._cleanup_temp_files(temp_dir, cutoff_time)
            
            # 3. 更新统计指标
            await self._update_storage_metrics()
            
            # 4. 检查存储空间
            await self._check_storage_space()
            
            self._metrics.last_maintenance = datetime.utcnow()
            logger.info("每日维护完成")
            
        except Exception as e:
            logger.error(f"每日维护失败: {e}")

    @handle_errors(
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.MAINTENANCE_OPERATION,
        user_message="每周优化失败"
    )
    async def _weekly_optimization(self):
        """每周优化：索引重建和压缩"""
        try:
            logger.info("开始每周优化...")
            
            # 1. 优化FAISS索引
            if self._vector_store:
                # 重建索引以提高查询性能
                await self._optimize_vector_indices()
                self._metrics.index_optimizations += 1
            
            # 2. 数据库维护
            await self._optimize_database()
            
            # 3. 压缩日志文件
            await self._compress_old_logs()
            
            # 4. 备份关键数据
            if self.lifecycle_config.backup_before_cleanup:
                await self._backup_critical_data()
                self._metrics.backup_operations += 1
            
            logger.info("每周优化完成")
            
        except Exception as e:
            logger.error(f"每周优化失败: {e}")

    @handle_errors(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.MAINTENANCE_OPERATION,
        user_message="每月归档失败"
    )
    async def _monthly_archival(self):
        """每月归档：冷热数据迁移"""
        try:
            logger.info("开始每月归档...")
            
            # 1. 热数据→温数据迁移
            hot_migrated = await self._migrate_hot_to_warm()
            self._metrics.hot_to_warm_migrations += hot_migrated
            
            # 2. 温数据→冷数据迁移
            warm_migrated = await self._migrate_warm_to_cold()
            self._metrics.warm_to_cold_migrations += warm_migrated
            
            # 3. 更新分片层级
            await self._update_shard_tiers()
            
            # 4. 优化存储布局
            reclaimed = await self._optimize_storage_layout()
            self._metrics.storage_reclaimed_mb += reclaimed
            
            logger.info(f"每月归档完成 - 热→温: {hot_migrated}, 温→冷: {warm_migrated}")
            
        except Exception as e:
            logger.error(f"每月归档失败: {e}")

    @handle_errors(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.MAINTENANCE_OPERATION,
        user_message="季度深度清理失败"
    )
    async def _quarterly_deep_clean(self):
        """季度深度清理：价值重评估和清理"""
        try:
            logger.info("开始季度深度清理...")
            
            # 1. 重新评估内容价值
            reevaluated = await self._reevaluate_content_value()
            
            # 2. 清理低价值内容
            cleaned = await self._deep_clean_low_value_content()
            self._metrics.cold_cleanups += cleaned
            
            # 3. 归档超期数据
            archived = await self._archive_expired_data()
            
            # 4. 重建索引结构
            await self._rebuild_index_structure()
            
            # 5. 生成清理报告
            await self._generate_cleanup_report(reevaluated, cleaned, archived)
            
            logger.info(f"季度深度清理完成 - 重评估: {reevaluated}, 清理: {cleaned}, 归档: {archived}")
            
        except Exception as e:
            logger.error(f"季度深度清理失败: {e}")

    # === 具体操作实现 ===

    async def _cleanup_temp_files(self, temp_dir: Path, cutoff_time: datetime):
        """清理临时文件"""
        try:
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_time:
                        file_path.unlink()
                        logger.debug(f"删除临时文件: {file_path.name}")
        except Exception as e:
            logger.error(f"清理临时文件失败: {e}")

    async def _optimize_vector_indices(self):
        """优化向量索引"""
        try:
            if not self._vector_store:
                return
            
            # 对于活跃分片进行索引优化
            for shard_id, shard_info in self._vector_store.shards.items():
                if shard_info.tier == "hot" and shard_info.document_count > 1000:
                    # 重建索引以提高查询性能
                    index = self._vector_store.active_indices.get(shard_id)
                    if index and hasattr(index, 'optimize'):
                        await asyncio.get_event_loop().run_in_executor(
                            self._executor, index.optimize
                        )
                        logger.debug(f"优化分片索引: {shard_id}")
                        
        except Exception as e:
            logger.error(f"优化向量索引失败: {e}")

    async def _optimize_database(self):
        """优化数据库"""
        try:
            with self._db_service.get_session() as session:
                # SQLite VACUUM操作
                session.execute("VACUUM")
                session.execute("ANALYZE")
                logger.debug("数据库优化完成")
        except Exception as e:
            logger.error(f"数据库优化失败: {e}")

    async def _migrate_hot_to_warm(self) -> int:
        """热数据迁移到温数据"""
        try:
            if not self._vector_store:
                return 0
            
            cutoff_date = datetime.utcnow() - timedelta(days=self.lifecycle_config.hot_retention_days)
            migrated_count = 0
            
            for shard_id, shard_info in self._vector_store.shards.items():
                if (shard_info.tier == "hot" and 
                    shard_info.last_updated < cutoff_date and
                    not shard_info.is_active):
                    
                    # 迁移到温存储目录
                    warm_dir = self.config.storage_dir / "warm_index" / shard_id
                    warm_dir.mkdir(parents=True, exist_ok=True)
                    
                    # 移动文件
                    if shard_info.index_file.exists():
                        new_index_file = warm_dir / shard_info.index_file.name
                        shutil.move(str(shard_info.index_file), str(new_index_file))
                        shard_info.index_file = new_index_file
                    
                    if shard_info.metadata_file.exists():
                        new_metadata_file = warm_dir / shard_info.metadata_file.name
                        shutil.move(str(shard_info.metadata_file), str(new_metadata_file))
                        shard_info.metadata_file = new_metadata_file
                    
                    # 更新分片层级
                    shard_info.tier = "warm"
                    migrated_count += 1
                    
                    logger.info(f"分片迁移到温存储: {shard_id}")
            
            return migrated_count
            
        except Exception as e:
            logger.error(f"热数据迁移失败: {e}")
            return 0

    async def _migrate_warm_to_cold(self) -> int:
        """温数据迁移到冷数据"""
        try:
            if not self._vector_store:
                return 0
            
            cutoff_date = datetime.utcnow() - timedelta(days=self.lifecycle_config.warm_retention_days)
            migrated_count = 0
            
            for shard_id, shard_info in self._vector_store.shards.items():
                if (shard_info.tier == "warm" and 
                    shard_info.last_updated < cutoff_date):
                    
                    # 压缩并迁移到冷存储
                    cold_dir = self.config.storage_dir / "cold_archive"
                    cold_dir.mkdir(parents=True, exist_ok=True)
                    
                    # 压缩分片数据
                    archive_file = cold_dir / f"{shard_id}.tar.gz"
                    await self._compress_shard_data(shard_info, archive_file)
                    
                    # 删除原始文件
                    if shard_info.index_file.exists():
                        shard_info.index_file.unlink()
                    if shard_info.metadata_file.exists():
                        shard_info.metadata_file.unlink()
                    
                    # 更新分片信息
                    shard_info.tier = "cold"
                    shard_info.index_file = archive_file
                    migrated_count += 1
                    
                    logger.info(f"分片迁移到冷存储: {shard_id}")
            
            return migrated_count
            
        except Exception as e:
            logger.error(f"温数据迁移失败: {e}")
            return 0

    async def _reevaluate_content_value(self) -> int:
        """重新评估内容价值"""
        try:
            if not self._ollama_service:
                return 0
            
            reevaluated_count = 0
            
            # 获取所有智能处理的内容
            with self._db_service.get_session() as session:
                intelligent_events = session.query(EntityMetadata).filter(
                    EntityMetadata.type == "intelligent_event"
                ).all()
                
                for event in intelligent_events:
                    properties = event.properties or {}
                    ai_evaluation = properties.get("ai_evaluation", {})
                    original_score = ai_evaluation.get("value_score", 0.0)
                    
                    # 获取原始摘要重新评估
                    summary = properties.get("summary", "")
                    if summary:
                        new_score = await self._ollama_service.evaluate_content_value(summary)
                        
                        # 如果评分变化超过阈值，更新记录
                        if abs(new_score - original_score) > 0.1:
                            ai_evaluation["value_score"] = new_score
                            ai_evaluation["reevaluated_at"] = datetime.utcnow().isoformat()
                            properties["ai_evaluation"] = ai_evaluation
                            event.properties = properties
                            reevaluated_count += 1
                
                session.commit()
            
            return reevaluated_count
            
        except Exception as e:
            logger.error(f"重新评估内容价值失败: {e}")
            return 0

    # === 工具方法 ===

    async def _ensure_directories(self):
        """确保必要目录存在"""
        directories = [
            self.config.storage_dir / "hot_index",
            self.config.storage_dir / "warm_index",
            self.config.storage_dir / "cold_archive",
            self.config.temp_dir,
            self.config.cache_dir,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    async def _compress_shard_data(self, shard_info, archive_path: Path):
        """压缩分片数据"""
        import tarfile
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self._executor,
            self._compress_shard_sync,
            shard_info,
            archive_path
        )

    def _compress_shard_sync(self, shard_info, archive_path: Path):
        """同步压缩分片数据"""
        import tarfile
        
        with tarfile.open(archive_path, "w:gz") as tar:
            if shard_info.index_file.exists():
                tar.add(shard_info.index_file, arcname=shard_info.index_file.name)
            if shard_info.metadata_file.exists():
                tar.add(shard_info.metadata_file, arcname=shard_info.metadata_file.name)

    # === 手动维护接口 ===

    async def force_maintenance(self, task_type: str = "all") -> Dict[str, Any]:
        """强制执行维护任务"""
        try:
            results = {}
            
            if task_type in ("all", "daily"):
                await self._daily_maintenance()
                results["daily"] = "completed"
            
            if task_type in ("all", "weekly"):
                await self._weekly_optimization()
                results["weekly"] = "completed"
            
            if task_type in ("all", "monthly"):
                migrated = await self._monthly_archival()
                results["monthly"] = f"completed - migrated: {migrated}"
            
            if task_type in ("all", "quarterly"):
                await self._quarterly_deep_clean()
                results["quarterly"] = "completed"
            
            return results
            
        except Exception as e:
            logger.error(f"强制维护失败: {e}")
            return {"error": str(e)}

    async def get_lifecycle_metrics(self) -> LifecycleMetrics:
        """获取生命周期指标"""
        return self._metrics

    async def _save_maintenance_state(self):
        """保存维护状态"""
        # 这里可以实现状态持久化
        pass


# === 服务单例管理 ===

_lifecycle_manager: Optional[DataLifecycleManager] = None

async def get_data_lifecycle_manager() -> DataLifecycleManager:
    """获取数据生命周期管理器实例（单例模式）"""
    global _lifecycle_manager
    if _lifecycle_manager is None:
        _lifecycle_manager = DataLifecycleManager()
        if not await _lifecycle_manager.initialize():
            raise RuntimeError("数据生命周期管理器初始化失败")
    return _lifecycle_manager

async def cleanup_data_lifecycle_manager():
    """清理数据生命周期管理器"""
    global _lifecycle_manager
    if _lifecycle_manager:
        await _lifecycle_manager.close()
        _lifecycle_manager = None