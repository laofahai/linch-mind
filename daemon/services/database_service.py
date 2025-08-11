#!/usr/bin/env python3
"""
高性能数据库服务 - 集成优化连接池
使用读写分离和智能查询路由提升性能
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from config.core_config import get_database_config
from models.database_models import Base, Connector

from .optimized_connection_pool import (
    HighPerformanceConnectionPool,
    get_connection_pool,
)

logger = logging.getLogger(__name__)


class DatabaseService:
    """高性能数据库服务 - 集成优化连接池"""

    def __init__(self, db_path: Optional[str] = None):
        self.db_config = get_database_config()
        self.connection_pool: Optional[HighPerformanceConnectionPool] = None

        # 🆕 环境感知的数据库配置
        from core.environment_manager import get_environment_manager

        self.env_manager = get_environment_manager()

        # 数据库URL优先级：参数 > 环境管理器 > 配置
        if db_path:
            database_url = (
                f"sqlite:///{db_path}"
                if db_path != ":memory:"
                else "sqlite:///:memory:"
            )
        else:
            # 使用环境管理器提供的数据库URL
            database_url = self.env_manager.get_database_url()

        # 环境特定的引擎配置
        engine_config = {
            "echo": self.env_manager.is_debug_enabled(),  # 开发环境启用SQL日志
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        }

        # 生产环境的额外优化
        if not self.env_manager.is_debug_enabled():
            engine_config.update(
                {
                    "pool_size": 20,  # 生产环境更大的连接池
                    "max_overflow": 30,
                    "pool_timeout": 30,
                }
            )

        self.database_url = database_url
        self.engine = create_engine(database_url, **engine_config)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self._initialize_database()

    async def initialize(self):
        """异步初始化高性能连接池"""
        try:
            self.connection_pool = await get_connection_pool()
            logger.info("高性能连接池初始化完成")
        except Exception as e:
            logger.warning(f"高性能连接池初始化失败，使用传统连接: {e}")

    async def close(self):
        """异步关闭方法"""
        if self.connection_pool:
            await self.connection_pool.cleanup()
        self.cleanup()

    def _initialize_database(self):
        """初始化数据库表结构"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("数据库表结构初始化完成")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise

    def register_connector(self, connector_info: Dict[str, Any]) -> bool:
        """注册连接器"""
        try:
            with self.SessionLocal() as session:
                existing = (
                    session.query(Connector)
                    .filter(Connector.connector_id == connector_info["connector_id"])
                    .first()
                )

                if existing:
                    # 更新现有连接器信息
                    for key, value in connector_info.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                    logger.info(f"更新连接器: {connector_info['connector_id']}")
                else:
                    # 创建新连接器
                    connector = Connector(**connector_info)
                    session.add(connector)
                    logger.info(f"注册新连接器: {connector_info['connector_id']}")

                session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"注册连接器失败: {e}")
            return False

    def get_connectors(self) -> List[Connector]:
        """获取所有连接器"""
        try:
            with self.SessionLocal() as session:
                return session.query(Connector).all()
        except SQLAlchemyError as e:
            logger.error(f"获取连接器列表失败: {e}")
            return []

    def get_connector(self, connector_id: str) -> Optional[Connector]:
        """根据ID获取连接器"""
        try:
            with self.SessionLocal() as session:
                return (
                    session.query(Connector)
                    .filter(Connector.connector_id == connector_id)
                    .first()
                )
        except SQLAlchemyError as e:
            logger.error(f"获取连接器失败 [{connector_id}]: {e}")
            return None

    def update_connector_status(
        self, connector_id: str, status: str, process_id: Optional[int] = None
    ) -> bool:
        """更新连接器状态"""
        try:
            with self.SessionLocal() as session:
                connector = (
                    session.query(Connector)
                    .filter(Connector.connector_id == connector_id)
                    .first()
                )

                if connector:
                    connector.status = status
                    if process_id is not None:
                        connector.process_id = process_id
                    connector.updated_at = datetime.utcnow()
                    session.commit()
                    logger.info(f"更新连接器状态: {connector_id} -> {status}")
                    return True
                else:
                    logger.warning(f"连接器不存在: {connector_id}")
                    return False
        except SQLAlchemyError as e:
            logger.error(f"更新连接器状态失败 [{connector_id}]: {e}")
            return False

    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            with self.SessionLocal() as session:
                connectors_count = session.query(Connector).count()
                running_connectors_count = (
                    session.query(Connector)
                    .filter(Connector.status == "running")
                    .count()
                )

                return {
                    "connectors_count": connectors_count,
                    "running_connectors_count": running_connectors_count,
                    "database_path": self.database_url,  # 使用实际数据库URL
                    "environment": self.env_manager.current_environment.value,
                    "encrypted": self.env_manager.should_use_encryption(),
                }
        except SQLAlchemyError as e:
            logger.error(f"获取数据库统计失败: {e}")
            return {}

    def get_environment_database_info(self) -> Dict[str, Any]:
        """获取环境特定的数据库信息"""
        try:
            import os

            # 基础信息
            info = {
                "environment": self.env_manager.current_environment.value,
                "database_url": self.database_url,
                "use_encryption": self.env_manager.should_use_encryption(),
                "debug_enabled": self.env_manager.is_debug_enabled(),
                "environment_paths": self.env_manager.get_environment_summary()[
                    "directories"
                ],
            }

            # 数据库文件信息
            if not self.database_url.endswith(":memory:"):
                db_file_path = self.database_url.replace("sqlite:///", "")
                if os.path.exists(db_file_path):
                    stat = os.stat(db_file_path)
                    info.update(
                        {
                            "database_size_bytes": stat.st_size,
                            "database_size_mb": round(stat.st_size / (1024 * 1024), 2),
                            "last_modified": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                        }
                    )
                else:
                    info["database_exists"] = False
            else:
                info["database_type"] = "in_memory"

            return info

        except Exception as e:
            logger.error(f"获取环境数据库信息失败: {e}")
            return {"error": str(e)}

    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()

    def cleanup(self):
        """清理资源"""
        try:
            self.engine.dispose()
            logger.info("数据库连接已清理")
        except Exception as e:
            logger.error(f"数据库清理失败: {e}")


# 全局数据库服务实例
# 🔧 移除全局单例模式 - 现在由DI容器管理
# DatabaseService实例通过core.container获取，消除重复的get_database_service调用


def cleanup_database_service():
    """清理数据库服务 - 现在通过DI容器管理"""
    from core.container import get_container

    try:
        container = get_container()
        if container.is_registered(DatabaseService):
            service = container.get_service(DatabaseService)
            service.cleanup()
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"清理数据库服务失败: {e}")
