#!/usr/bin/env python3
"""
针对现实数据规模的SQLite优化服务
基于文档 data_storage_architecture.md 中的现实主义设计
"""

import logging
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.core_config import get_database_config
from models.database_models import Base
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)


class OptimizedSQLiteService:
    """针对现实数据规模的SQLite优化服务

    基于文档分析的现实数据规模：
    - 第1年: 8K-35K实体 + 15K-100K关系
    - 第5年稳态: 35K-130K实体 + 70K-400K关系
    - 存储需求: 10GB-50GB
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_config = get_database_config()

        # 使用提供的路径或配置的默认路径
        if db_path:
            self.database_url = (
                f"sqlite:///{db_path}"
                if db_path != ":memory:"
                else "sqlite:///:memory:"
            )
        else:
            self.database_url = self.db_config.sqlite_url

        # 创建优化的引擎
        self.engine = self._create_optimized_engine()
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        # 初始化数据库
        self._initialize_database()

        # 应用激进优化
        self._apply_aggressive_optimizations()

        logger.info(f"OptimizedSQLiteService 初始化完成: {self.database_url}")

    def _create_optimized_engine(self) -> Engine:
        """创建优化的SQLite引擎"""

        # 确保数据库目录存在
        if ":///" in self.database_url and not self.database_url.endswith(":memory:"):
            db_path = Path(self.database_url.split("///")[1])
            db_path.parent.mkdir(parents=True, exist_ok=True)

        # 创建引擎，针对现实数据规模优化
        engine = create_engine(
            self.database_url,
            echo=False,  # 生产环境关闭SQL日志
            pool_pre_ping=True,
            pool_recycle=3600,
            poolclass=StaticPool,  # SQLite使用静态连接池
            connect_args={
                "check_same_thread": False,
                "timeout": 30,  # 30秒超时
            },
        )

        # 配置SQLite优化参数
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """设置SQLite优化参数"""
            cursor = dbapi_connection.cursor()

            # 内存优化 - 针对现实数据规模
            cursor.execute("PRAGMA cache_size = -128000")  # 128MB缓存
            cursor.execute("PRAGMA temp_store = MEMORY")  # 临时表存内存
            cursor.execute("PRAGMA mmap_size = 536870912")  # 512MB内存映射

            # WAL模式优化 - 提升并发性能
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.execute("PRAGMA wal_autocheckpoint = 2000")
            cursor.execute("PRAGMA synchronous = NORMAL")

            # 查询优化
            cursor.execute("PRAGMA optimize")
            cursor.execute("PRAGMA analysis_limit = 2000")

            # 页面大小优化
            cursor.execute("PRAGMA page_size = 4096")

            # 关闭自动索引，使用手工优化的索引
            cursor.execute("PRAGMA automatic_index = OFF")

            cursor.close()

        return engine

    def _initialize_database(self):
        """初始化数据库表结构"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("数据库表结构初始化完成")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise

    def _apply_aggressive_optimizations(self):
        """应用激进的SQLite优化"""
        try:
            with self.engine.connect() as conn:
                # 创建基于现实查询模式的专用索引
                self._create_reality_based_indexes(conn)

                # 运行数据库分析
                conn.execute(text("ANALYZE"))

            logger.info("SQLite激进优化应用完成")
        except Exception as e:
            logger.warning(f"SQLite优化失败: {e}")

    def _create_reality_based_indexes(self, conn):
        """创建基于现实查询模式的索引"""

        # 基于真实查询模式的高效索引
        indexes = [
            # 实体查询优化 (最频繁)
            "CREATE INDEX IF NOT EXISTS idx_entity_type_updated ON entity_metadata(entity_type, updated_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_entity_access_frequency ON entity_metadata(access_count DESC, last_accessed DESC)",
            "CREATE INDEX IF NOT EXISTS idx_entity_name_search ON entity_metadata(name COLLATE NOCASE)",
            # 关系查询优化 (第二频繁)
            "CREATE INDEX IF NOT EXISTS idx_rel_source_type ON entity_relationships(source_entity, relationship_type)",
            "CREATE INDEX IF NOT EXISTS idx_rel_target_strength ON entity_relationships(target_entity, strength DESC)",
            "CREATE INDEX IF NOT EXISTS idx_rel_bidirectional ON entity_relationships(source_entity, target_entity)",
            # 行为分析优化
            "CREATE INDEX IF NOT EXISTS idx_behavior_recent ON user_behaviors(timestamp DESC) WHERE timestamp > date('now', '-30 days')",
            "CREATE INDEX IF NOT EXISTS idx_behavior_session_time ON user_behaviors(session_id, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_behavior_target_action ON user_behaviors(target_entity, action_type)",
            # 对话搜索优化 (如果有FTS支持)
            "CREATE INDEX IF NOT EXISTS idx_conversation_session_time ON ai_conversations(session_id, timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_conversation_recent ON ai_conversations(timestamp DESC) WHERE timestamp > date('now', '-7 days')",
        ]

        for index_sql in indexes:
            try:
                conn.execute(text(index_sql))
                logger.debug(
                    f"创建索引成功: {index_sql.split('idx_')[1].split(' ')[0]}"
                )
            except Exception as e:
                logger.warning(f"索引创建失败: {e}")

    @contextmanager
    def get_session(self):
        """获取数据库会话的上下文管理器"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取数据库性能统计"""
        try:
            with self.engine.connect() as conn:
                # 获取数据库大小
                size_result = conn.execute(
                    text(
                        "SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()"
                    )
                )
                db_size_bytes = size_result.fetchone()[0]

                # 获取WAL状态
                wal_result = conn.execute(text("PRAGMA journal_mode"))
                journal_mode = wal_result.fetchone()[0]

                # 获取缓存统计
                cache_result = conn.execute(text("PRAGMA cache_size"))
                cache_size = cache_result.fetchone()[0]

                # 获取表统计
                tables_result = conn.execute(
                    text(
                        """
                    SELECT name, 
                           (SELECT COUNT(*) FROM sqlite_master WHERE name = s.name) as count
                    FROM sqlite_master s 
                    WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                """
                    )
                )
                tables = dict(tables_result.fetchall())

                return {
                    "database_size_mb": round(db_size_bytes / (1024 * 1024), 2),
                    "journal_mode": journal_mode,
                    "cache_size_pages": cache_size,
                    "cache_size_mb": (
                        round(abs(cache_size) / 256, 2) if cache_size < 0 else "N/A"
                    ),
                    "tables": tables,
                    "optimizations_applied": True,
                }

        except Exception as e:
            logger.error(f"获取性能统计失败: {e}")
            return {"error": str(e)}

    def run_maintenance(self) -> Dict[str, Any]:
        """运行数据库维护任务"""
        results = {}

        try:
            with self.engine.connect() as conn:
                # 1. 运行VACUUM以整理数据库
                start_time = datetime.now()
                conn.execute(text("VACUUM"))
                vacuum_time = (datetime.now() - start_time).total_seconds()
                results["vacuum_time_seconds"] = round(vacuum_time, 2)

                # 2. 更新统计信息
                start_time = datetime.now()
                conn.execute(text("ANALYZE"))
                analyze_time = (datetime.now() - start_time).total_seconds()
                results["analyze_time_seconds"] = round(analyze_time, 2)

                # 3. 检查数据库完整性
                start_time = datetime.now()
                integrity_result = conn.execute(text("PRAGMA integrity_check"))
                integrity_status = integrity_result.fetchone()[0]
                integrity_time = (datetime.now() - start_time).total_seconds()

                results["integrity_check"] = integrity_status
                results["integrity_check_time_seconds"] = round(integrity_time, 2)

                # 4. 优化查询计划
                conn.execute(text("PRAGMA optimize"))

                results["status"] = "success"
                results["timestamp"] = datetime.now(timezone.utc).isoformat()

                logger.info(f"数据库维护完成: {results}")

        except Exception as e:
            logger.error(f"数据库维护失败: {e}")
            results["status"] = "error"
            results["error"] = str(e)

        return results

    def get_table_statistics(self) -> Dict[str, Any]:
        """获取详细的表统计信息"""
        try:
            with self.engine.connect() as conn:
                stats = {}

                # 获取所有用户表
                tables_result = conn.execute(
                    text(
                        """
                    SELECT name FROM sqlite_master 
                    WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                """
                    )
                )
                tables = [row[0] for row in tables_result.fetchall()]

                for table in tables:
                    try:
                        # 表记录数
                        count_result = conn.execute(
                            text(f"SELECT COUNT(*) FROM {table}")
                        )
                        count = count_result.fetchone()[0]

                        # 表大小估算（页数）
                        pages_result = conn.execute(
                            text(f"SELECT COUNT(*) FROM pragma_table_info('{table}')")
                        )
                        columns = pages_result.fetchone()[0]

                        stats[table] = {
                            "record_count": count,
                            "column_count": columns,
                            "estimated_size_records": count,
                        }

                    except Exception as e:
                        stats[table] = {"error": str(e)}

                return stats

        except Exception as e:
            logger.error(f"获取表统计失败: {e}")
            return {"error": str(e)}

    def cleanup(self):
        """清理资源"""
        try:
            if self.engine:
                self.engine.dispose()
                logger.info("OptimizedSQLiteService 连接已清理")
        except Exception as e:
            logger.error(f"OptimizedSQLiteService 清理失败: {e}")


# 全局优化数据库服务实例
_optimized_sqlite_service: Optional[OptimizedSQLiteService] = None


def get_optimized_sqlite_service() -> OptimizedSQLiteService:
    """获取优化SQLite服务实例（单例模式）"""
    global _optimized_sqlite_service
    if _optimized_sqlite_service is None:
        _optimized_sqlite_service = OptimizedSQLiteService()
    return _optimized_sqlite_service


def cleanup_optimized_sqlite_service():
    """清理优化SQLite服务"""
    global _optimized_sqlite_service
    if _optimized_sqlite_service:
        _optimized_sqlite_service.cleanup()
        _optimized_sqlite_service = None
