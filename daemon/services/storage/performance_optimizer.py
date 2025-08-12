#!/usr/bin/env python3
"""
性能优化器
专门负责数据库性能优化相关功能
从data_lifecycle_manager.py中拆分出来
"""

import asyncio
import logging
import sqlite3
from datetime import datetime
from typing import Dict

from core.service_facade import get_database_service

logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """性能优化器"""

    def __init__(self, config):
        self.config = config
        self.db_service = None

    async def initialize(self):
        """初始化性能优化器"""
        try:
            self.db_service = get_database_service()
            logger.info("性能优化器初始化完成")
            return True
        except Exception as e:
            logger.error(f"性能优化器初始化失败: {e}")
            return False

    async def optimize_database_performance(self) -> Dict[str, bool]:
        """优化数据库性能"""
        optimization_results = {
            "vacuum": False,
            "analyze": False,
            "reindex": False,
            "pragma_optimization": False,
        }

        try:
            logger.info("开始数据库性能优化...")

            # 1. VACUUM - 回收空间和整理数据
            if self.config.auto_vacuum_enabled:
                optimization_results["vacuum"] = await self._vacuum_database()

            # 2. ANALYZE - 更新统计信息
            optimization_results["analyze"] = await self._analyze_database()

            # 3. REINDEX - 重建索引
            if self.config.index_optimization_enabled:
                optimization_results["reindex"] = await self._reindex_database()

            # 4. 优化PRAGMA设置
            optimization_results["pragma_optimization"] = await self._optimize_pragma_settings()

            logger.info(f"数据库性能优化完成: {optimization_results}")
            return optimization_results

        except Exception as e:
            logger.error(f"数据库性能优化失败: {e}")
            return optimization_results

    async def _vacuum_database(self) -> bool:
        """执行数据库VACUUM操作"""
        try:
            if not self.db_service:
                return False

            logger.info("执行数据库VACUUM操作...")

            # 获取VACUUM前的数据库大小
            db_stats = self.db_service.get_database_stats()
            database_path = db_stats.get("database_path", "")

            pre_size = 0
            if database_path and database_path.startswith("sqlite:///"):
                import os
                file_path = database_path.replace("sqlite:///", "")
                if os.path.exists(file_path):
                    pre_size = os.path.getsize(file_path)

            # 执行VACUUM
            with self.db_service.get_session() as session:
                session.execute("VACUUM;")
                session.commit()

            # 计算节省的空间
            post_size = 0
            if database_path and database_path.startswith("sqlite:///"):
                import os
                file_path = database_path.replace("sqlite:///", "")
                if os.path.exists(file_path):
                    post_size = os.path.getsize(file_path)

            saved_mb = (pre_size - post_size) / (1024 * 1024)
            logger.info(f"VACUUM完成，节省空间: {saved_mb:.2f}MB")
            
            return True

        except Exception as e:
            logger.error(f"VACUUM操作失败: {e}")
            return False

    async def _analyze_database(self) -> bool:
        """执行数据库ANALYZE操作"""
        try:
            if not self.db_service:
                return False

            logger.info("执行数据库ANALYZE操作...")

            with self.db_service.get_session() as session:
                # 更新所有表的统计信息
                session.execute("ANALYZE;")
                session.commit()

            logger.info("ANALYZE操作完成")
            return True

        except Exception as e:
            logger.error(f"ANALYZE操作失败: {e}")
            return False

    async def _reindex_database(self) -> bool:
        """重建数据库索引"""
        try:
            if not self.db_service:
                return False

            logger.info("重建数据库索引...")

            with self.db_service.get_session() as session:
                # 重建所有索引
                session.execute("REINDEX;")
                session.commit()

            logger.info("索引重建完成")
            return True

        except Exception as e:
            logger.error(f"索引重建失败: {e}")
            return False

    async def _optimize_pragma_settings(self) -> bool:
        """优化PRAGMA设置"""
        try:
            if not self.db_service:
                return False

            logger.info("优化PRAGMA设置...")

            with self.db_service.get_session() as session:
                # 优化性能相关的PRAGMA设置
                pragma_settings = [
                    "PRAGMA cache_size = -64000;",  # 64MB缓存
                    "PRAGMA temp_store = MEMORY;",  # 临时数据存储在内存
                    "PRAGMA journal_mode = WAL;",   # WAL模式
                    "PRAGMA synchronous = NORMAL;", # 平衡安全性和性能
                    "PRAGMA mmap_size = 268435456;", # 256MB内存映射
                ]

                for pragma in pragma_settings:
                    try:
                        session.execute(pragma)
                    except Exception as e:
                        logger.warning(f"PRAGMA设置失败 {pragma}: {e}")

                session.commit()

            logger.info("PRAGMA设置优化完成")
            return True

        except Exception as e:
            logger.error(f"PRAGMA设置优化失败: {e}")
            return False

    async def get_performance_metrics(self) -> Dict:
        """获取性能指标"""
        try:
            if not self.db_service:
                return {}

            metrics = {}

            with self.db_service.get_session() as session:
                # 获取数据库统计信息
                results = session.execute("PRAGMA database_list;").fetchall()
                for result in results:
                    db_name = result[1]
                    if db_name == "main":
                        # 获取页面统计
                        page_count = session.execute("PRAGMA page_count;").fetchone()[0]
                        page_size = session.execute("PRAGMA page_size;").fetchone()[0]
                        freelist_count = session.execute("PRAGMA freelist_count;").fetchone()[0]
                        
                        metrics.update({
                            "total_pages": page_count,
                            "page_size": page_size,
                            "free_pages": freelist_count,
                            "database_size_mb": (page_count * page_size) / (1024 * 1024),
                            "fragmentation_percentage": (freelist_count / max(page_count, 1)) * 100,
                        })

                # 获取缓存统计
                cache_stats = session.execute("PRAGMA cache_size;").fetchone()
                if cache_stats:
                    metrics["cache_size"] = abs(cache_stats[0])

                # 获取WAL信息
                try:
                    wal_checkpoint = session.execute("PRAGMA wal_checkpoint;").fetchone()
                    if wal_checkpoint:
                        metrics["wal_frames"] = wal_checkpoint[1]
                        metrics["wal_checkpointed"] = wal_checkpoint[2]
                except:
                    pass  # WAL可能未启用

            return metrics

        except Exception as e:
            logger.error(f"获取性能指标失败: {e}")
            return {}

    async def suggest_optimizations(self) -> Dict:
        """建议性能优化方案"""
        try:
            suggestions = {
                "vacuum_needed": False,
                "index_optimization_needed": False,
                "cache_adjustment_needed": False,
                "suggestions": []
            }

            metrics = await self.get_performance_metrics()
            
            if not metrics:
                return suggestions

            # 检查碎片化程度
            fragmentation = metrics.get("fragmentation_percentage", 0)
            if fragmentation > 15:
                suggestions["vacuum_needed"] = True
                suggestions["suggestions"].append(
                    f"数据库碎片化严重({fragmentation:.1f}%)，建议执行VACUUM操作"
                )

            # 检查数据库大小
            db_size_mb = metrics.get("database_size_mb", 0)
            if db_size_mb > 1000:  # >1GB
                suggestions["suggestions"].append(
                    "数据库较大，建议定期清理过期数据和归档"
                )

            # 检查缓存配置
            cache_size = metrics.get("cache_size", 0)
            if cache_size < 10000:  # <10MB
                suggestions["cache_adjustment_needed"] = True
                suggestions["suggestions"].append(
                    "数据库缓存较小，建议增加cache_size以提升性能"
                )

            # WAL模式检查
            if "wal_frames" not in metrics:
                suggestions["suggestions"].append(
                    "建议启用WAL模式以提升并发性能"
                )

            return suggestions

        except Exception as e:
            logger.error(f"生成优化建议失败: {e}")
            return {}

    async def benchmark_query_performance(self, test_queries: list = None) -> Dict:
        """基准测试查询性能"""
        try:
            if not self.db_service:
                return {}

            if not test_queries:
                # 默认测试查询
                test_queries = [
                    "SELECT COUNT(*) FROM connectors;",
                    "SELECT * FROM connectors LIMIT 10;",
                    "SELECT COUNT(*) FROM entity_metadata;",
                    "SELECT COUNT(*) FROM entity_relationships;",
                ]

            benchmark_results = {}

            for i, query in enumerate(test_queries):
                try:
                    start_time = datetime.utcnow()
                    
                    with self.db_service.get_session() as session:
                        result = session.execute(query).fetchall()
                    
                    end_time = datetime.utcnow()
                    duration_ms = (end_time - start_time).total_seconds() * 1000
                    
                    benchmark_results[f"query_{i+1}"] = {
                        "query": query,
                        "duration_ms": duration_ms,
                        "result_count": len(result),
                    }

                except Exception as e:
                    benchmark_results[f"query_{i+1}"] = {
                        "query": query,
                        "error": str(e),
                    }

            # 计算平均查询时间
            successful_queries = [
                r for r in benchmark_results.values() 
                if "duration_ms" in r
            ]
            
            if successful_queries:
                avg_duration = sum(r["duration_ms"] for r in successful_queries) / len(successful_queries)
                benchmark_results["average_query_time_ms"] = avg_duration

            return benchmark_results

        except Exception as e:
            logger.error(f"基准测试失败: {e}")
            return {}