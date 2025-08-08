#!/usr/bin/env python3
"""
ConnectorManager V2 - 逐步重构版本
遵循最佳实践：依赖注入、错误处理、职责分离
保持向后兼容的API
"""

import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

from models.database_models import Connector
from services.database_service import get_database_service

# from .unified_connector_service import get_unified_connector_service  # 暂时移除以避免依赖问题

logger = logging.getLogger(__name__)


class ProcessManager(Protocol):
    """进程管理接口"""

    def start_process(
        self, connector_id: str, command: List[str]
    ) -> Optional[subprocess.Popen]:
        """启动进程"""
        ...

    def stop_process(self, connector_id: str) -> bool:
        """停止进程"""
        ...

    def get_process_status(self, connector_id: str) -> Dict[str, Any]:
        """获取进程状态"""
        ...


class ConfigManager(Protocol):
    """配置管理接口"""

    def find_connector_path(self, connector_id: str) -> Optional[Path]:
        """查找连接器路径"""
        ...

    def register_connector(
        self, connector_id: str, name: str, description: str, path: Path
    ) -> bool:
        """注册连接器"""
        ...


class ConnectorManager:
    """
    ConnectorManager V2 - 重构版本

    重构原则：
    1. 依赖注入 - 便于测试和扩展
    2. 错误处理 - 健壮的异常处理机制
    3. 职责分离 - 核心逻辑与具体实现分离
    4. 向后兼容 - 保持原有API
    """

    def __init__(
        self,
        connectors_dir: Path,
        process_manager: Optional[ProcessManager] = None,
        config_manager: Optional[ConfigManager] = None,
    ):
        self.connectors_dir = Path(connectors_dir)
        self.db_service = get_database_service()
        # self.unified_service = get_unified_connector_service()  # 暂时移除

        # 使用依赖注入，提供默认实现
        self.process_manager = process_manager or DefaultProcessManager()
        self.config_manager = config_manager or DefaultConfigManager(connectors_dir)

        # 保持向后兼容
        self.active_processes: Dict[str, subprocess.Popen] = {}

        # 初始化时恢复进程引用
        self._recover_running_processes()

        logger.info("ConnectorManager (重构版本) initialized successfully")

    def _recover_running_processes(self) -> None:
        """恢复运行中的进程引用"""
        try:
            import psutil

            with self.db_service.get_session() as session:
                running_connectors = (
                    session.query(Connector).filter_by(status="running").all()
                )

                recovered_count = 0
                for connector in running_connectors:
                    if connector.process_id and psutil.pid_exists(connector.process_id):
                        try:
                            process = psutil.Process(connector.process_id)
                            # 简化验证：只检查进程是否存活
                            if process.is_running():
                                self.active_processes[connector.connector_id] = process
                                recovered_count += 1
                        except psutil.NoSuchProcess:
                            # 进程已不存在，更新数据库状态
                            connector.status = "stopped"
                            connector.process_id = None
                            session.commit()

                logger.info(f"恢复了 {recovered_count} 个运行中的连接器进程")

        except ImportError:
            logger.warning("psutil未安装，无法恢复进程引用")
        except Exception as e:
            logger.error(f"恢复进程时出错: {e}")

    async def start_connector(self, connector_id: str) -> bool:
        """启动连接器 - 简化版本，专注核心逻辑"""
        try:
            # 1. 验证连接器存在
            with self.db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )

                if not connector:
                    logger.error(f"连接器不存在: {connector_id}")
                    return False

                if connector.status == "running":
                    logger.info(f"连接器已在运行: {connector_id}")
                    return True

            # 2. 查找连接器路径
            connector_path = self.config_manager.find_connector_path(connector_id)
            if not connector_path:
                logger.error(f"找不到连接器路径: {connector_id}")
                return False

            # 3. 构建启动命令
            command = [str(connector_path)]

            # 4. 启动进程
            process = self.process_manager.start_process(connector_id, command)
            if not process:
                logger.error(f"启动进程失败: {connector_id}")
                return False

            # 5. 更新数据库状态
            with self.db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )
                if connector:
                    connector.status = "running"
                    connector.process_id = process.pid
                    connector.updated_at = datetime.now(timezone.utc)
                    session.commit()

            # 6. 保存进程引用
            self.active_processes[connector_id] = process

            logger.info(f"连接器启动成功: {connector_id} (PID: {process.pid})")
            return True

        except Exception as e:
            logger.error(f"启动连接器时出错 {connector_id}: {e}")
            return False

    async def stop_connector(self, connector_id: str) -> bool:
        """停止连接器"""
        try:
            # 使用进程管理器停止进程
            success = self.process_manager.stop_process(connector_id)

            if success:
                # 更新数据库状态
                with self.db_service.get_session() as session:
                    connector = (
                        session.query(Connector)
                        .filter_by(connector_id=connector_id)
                        .first()
                    )
                    if connector:
                        connector.status = "stopped"
                        connector.process_id = None
                        connector.updated_at = datetime.now(timezone.utc)
                        session.commit()

                # 移除进程引用
                self.active_processes.pop(connector_id, None)

                logger.info(f"连接器停止成功: {connector_id}")
                return True
            else:
                logger.error(f"停止连接器失败: {connector_id}")
                return False

        except Exception as e:
            logger.error(f"停止连接器时出错 {connector_id}: {e}")
            return False

    def list_connectors(self) -> List[Dict[str, Any]]:
        """列出所有连接器"""
        try:
            with self.db_service.get_session() as session:
                connectors = session.query(Connector).all()

                result = []
                for conn in connectors:
                    # 获取实时进程状态
                    process_status = self.process_manager.get_process_status(
                        conn.connector_id
                    )

                    result.append(
                        {
                            "connector_id": conn.connector_id,
                            "name": conn.name,
                            "description": conn.description,
                            "status": conn.status,
                            "enabled": conn.enabled,
                            "process_id": conn.process_id,
                            "process_status": process_status,
                            "created_at": (
                                conn.created_at.isoformat() if conn.created_at else None
                            ),
                            "updated_at": (
                                conn.updated_at.isoformat() if conn.updated_at else None
                            ),
                        }
                    )

                return result

        except Exception as e:
            logger.error(f"列出连接器时出错: {e}")
            return []

    # 保持向后兼容的方法委托
    def register_connector(
        self, connector_id: str, name: str, description: str, path: Path
    ) -> bool:
        """注册连接器 - 委托给配置管理器"""
        return self.config_manager.register_connector(
            connector_id, name, description, path
        )

    def get_connector_status(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取连接器状态"""
        return self.process_manager.get_process_status(connector_id)


class DefaultProcessManager:
    """默认进程管理器实现"""

    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}

    def start_process(
        self, connector_id: str, command: List[str]
    ) -> Optional[subprocess.Popen]:
        """启动进程"""
        try:
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            self.processes[connector_id] = process
            return process
        except Exception as e:
            logger.error(f"启动进程失败 {connector_id}: {e}")
            return None

    def stop_process(self, connector_id: str) -> bool:
        """停止进程"""
        try:
            process = self.processes.get(connector_id)
            if process:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

                self.processes.pop(connector_id, None)
                return True
            return False
        except Exception as e:
            logger.error(f"停止进程失败 {connector_id}: {e}")
            return False

    def get_process_status(self, connector_id: str) -> Dict[str, Any]:
        """获取进程状态"""
        process = self.processes.get(connector_id)
        if process:
            return {
                "pid": process.pid,
                "running": process.poll() is None,
                "returncode": process.returncode,
            }
        return {"running": False}


class DefaultConfigManager:
    """默认配置管理器实现"""

    def __init__(self, connectors_dir: Path):
        self.connectors_dir = Path(connectors_dir)
        self.db_service = get_database_service()

    def find_connector_path(self, connector_id: str) -> Optional[Path]:
        """查找连接器路径"""
        # 查找连接器的多种可能路径
        potential_paths = [
            # 直接在connectors目录
            self.connectors_dir / connector_id,
            self.connectors_dir / f"{connector_id}.exe",
            # 在official目录中的标准结构
            self.connectors_dir
            / "official"
            / connector_id
            / f"linch-mind-{connector_id}",
            self.connectors_dir
            / "official"
            / connector_id
            / "bin"
            / "release"
            / f"linch-mind-{connector_id}",
            # Windows可执行文件
            self.connectors_dir
            / "official"
            / connector_id
            / "bin"
            / "release"
            / f"linch-mind-{connector_id}.exe",
        ]

        for path in potential_paths:
            if path.exists() and path.is_file():
                logger.info(f"找到连接器路径: {connector_id} -> {path}")
                return path

        logger.error(f"找不到连接器路径: {connector_id}")
        logger.debug(f"尝试过的路径: {[str(p) for p in potential_paths]}")
        return None

    def register_connector(
        self, connector_id: str, name: str, description: str, path: Path
    ) -> bool:
        """注册连接器"""
        try:
            with self.db_service.get_session() as session:
                existing = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )

                if existing:
                    existing.name = name
                    existing.description = description
                    existing.updated_at = datetime.now(timezone.utc)
                else:
                    connector = Connector(
                        connector_id=connector_id,
                        name=name,
                        description=description,
                        status="stopped",
                        enabled=True,
                    )
                    session.add(connector)

                session.commit()
                return True

        except Exception as e:
            logger.error(f"注册连接器失败 {connector_id}: {e}")
            return False


# 工厂函数，保持向后兼容
def get_connector_manager(connectors_dir: Path = None) -> ConnectorManager:
    """获取ConnectorManager实例"""
    if connectors_dir is None:
        # 使用项目根目录的connectors路径
        # 从daemon目录向上一级到项目根目录
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        connectors_dir = project_root / "connectors"

        logger.info(f"使用默认connectors目录: {connectors_dir}")

    return ConnectorManager(connectors_dir)
