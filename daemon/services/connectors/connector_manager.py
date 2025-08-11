"""
连接器管理服务 - 统一管理所有连接器的生命周期
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.core_config import CoreConfigManager
from core.service_facade import get_service
from models.database_models import Connector
from services.connector_registry_service import ConnectorRegistryService
from services.connectors.connector_config_service import ConnectorConfigService
from services.connectors.process_manager import ProcessManager
from services.database_service import DatabaseService

logger = logging.getLogger(__name__)


class ConnectorManager:
    """连接器管理器 - 统一管理连接器的注册、启动、停止等生命周期"""

    def __init__(
        self,
        connectors_dir=None,
        db_service=None,
        process_manager=None,
        config_service=None,
        registry_service=None,
        config_manager=None,
    ):
        # 优先使用依赖注入参数，fallback到ServiceFacade
        self.db_service = db_service or get_service(DatabaseService)
        self.process_manager = process_manager or get_service(ProcessManager)
        self.config_service = config_service or get_service(ConnectorConfigService)
        self.registry_service = registry_service or get_service(
            ConnectorRegistryService
        )
        self.config_manager = config_manager or get_service(CoreConfigManager)
        self.active_processes = {}  # 存储活动的进程引用
        self.connectors_dir = connectors_dir  # 保持向后兼容

    def get_all_connectors(self) -> List[Dict[str, Any]]:
        """获取所有已注册的连接器"""
        try:
            with self.db_service.get_session() as session:
                connectors = session.query(Connector).all()
                return [
                    {
                        "connector_id": c.connector_id,
                        "name": c.name,
                        "description": c.description,
                        "version": c.version,
                        "status": c.status,
                        "enabled": c.enabled,
                        "path": c.path,
                        "process_id": c.process_id,
                        "created_at": (
                            c.created_at.isoformat() if c.created_at else None
                        ),
                        "updated_at": (
                            c.updated_at.isoformat() if c.updated_at else None
                        ),
                    }
                    for c in connectors
                ]
        except Exception as e:
            logger.error(f"获取连接器列表失败: {e}")
            return []

    def list_connectors(self) -> List[Dict[str, Any]]:
        """获取所有已注册的连接器 (别名方法，保持API兼容性)"""
        return self.get_all_connectors()

    def get_connector_by_id(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取连接器信息"""
        try:
            with self.db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )

                if connector:
                    return {
                        "connector_id": connector.connector_id,
                        "name": connector.name,
                        "description": connector.description,
                        "version": connector.version,
                        "status": connector.status,
                        "enabled": connector.enabled,
                        "path": connector.path,
                        "process_id": connector.process_id,
                        "created_at": (
                            connector.created_at.isoformat()
                            if connector.created_at
                            else None
                        ),
                        "updated_at": (
                            connector.updated_at.isoformat()
                            if connector.updated_at
                            else None
                        ),
                    }
                return None
        except Exception as e:
            logger.error(f"获取连接器信息失败 {connector_id}: {e}")
            return None

    async def register_connector(
        self,
        connector_id: str,
        name: str = None,
        description: str = None,
        enabled: bool = True,
    ) -> bool:
        """
        注册一个新的连接器

        Args:
            connector_id: 连接器ID
            name: 显示名称（如果为None，将从connector.json读取）
            description: 描述（如果为None，将从connector.json读取）
            enabled: 是否启用
        """
        try:
            # 验证连接器是否存在于文件系统中
            connector_config = self.config_service.get_connector_config(connector_id)
            if not connector_config:
                logger.error(f"连接器配置文件不存在: {connector_id}")
                return False

            # 从配置文件读取默认信息
            config_name = connector_config.get("name", connector_id)
            config_description = connector_config.get("description", "")
            config_version = connector_config.get("version", "1.0.0")

            # 使用参数覆盖配置文件信息（如果提供）
            final_name = name or config_name
            final_description = description or config_description

            with self.db_service.get_session() as session:
                # 检查是否已存在
                existing = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )

                if existing:
                    # 更新现有连接器
                    existing.name = final_name
                    existing.description = final_description
                    existing.version = config_version
                    existing.enabled = enabled
                    existing.updated_at = datetime.now(timezone.utc)

                    # 更新路径信息（如果配置中有entry信息）
                    if "entry" in connector_config:
                        existing.path = self._resolve_connector_executable_path(
                            connector_id, connector_config
                        )

                    logger.info(f"更新连接器: {connector_id}")
                else:
                    # 创建新连接器并设置可执行文件路径
                    executable_path = self._resolve_connector_executable_path(
                        connector_id, connector_config
                    )

                    connector = Connector(
                        connector_id=connector_id,
                        name=final_name,
                        description=final_description,
                        version=config_version,
                        status="stopped",
                        enabled=enabled,
                        path=executable_path,
                    )
                    session.add(connector)
                    logger.info(
                        f"注册新连接器: {connector_id}, 可执行文件: {executable_path}"
                    )

                session.commit()
                return True

        except Exception as e:
            logger.error(f"注册连接器失败 {connector_id}: {e}")
            return False

    async def unregister_connector(self, connector_id: str) -> bool:
        """注销连接器"""
        try:
            # 如果连接器正在运行，先停止它
            connector_info = self.get_connector_by_id(connector_id)
            if connector_info and connector_info.get("status") == "running":
                await self.stop_connector(connector_id)

            # 从数据库删除
            with self.db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )

                if connector:
                    session.delete(connector)
                    session.commit()
                    logger.info(f"注销连接器: {connector_id}")
                    return True
                else:
                    logger.warning(f"连接器不存在: {connector_id}")
                    return False

        except Exception as e:
            logger.error(f"注销连接器失败 {connector_id}: {e}")
            return False

    async def start_connector(self, connector_id: str) -> bool:
        """启动连接器"""
        try:
            # 1. 获取连接器信息
            connector_info = self.get_connector_by_id(connector_id)
            if not connector_info:
                logger.error(f"连接器不存在: {connector_id}")
                return False

            # 2. 获取连接器路径 (从数据库中已存储的路径)
            connector_path = connector_info.get("path")
            if not connector_path:
                logger.error(f"连接器路径未配置: {connector_id}")
                return False

            # 3. 验证路径是否存在
            from pathlib import Path

            if not Path(connector_path).exists():
                logger.error(f"连接器路径不存在: {connector_path}")
                return False

            # 4. 构建启动命令
            command = [str(connector_path)]

            # 5. 启动进程
            process = await self.process_manager.start_process(connector_id, command)
            if not process:
                logger.error(f"启动进程失败: {connector_id}")
                return False

            # 6. 更新数据库状态
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

            # 7. 保存进程引用
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
            success = await self.process_manager.stop_process(connector_id)

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
                logger.warning(f"停止连接器失败: {connector_id}")
                return False

        except Exception as e:
            logger.error(f"停止连接器时出错 {connector_id}: {e}")
            return False

    async def update_connector_config(
        self, connector_id: str, updates: Dict[str, Any]
    ) -> bool:
        """更新连接器配置"""
        try:
            with self.db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )

                if not connector:
                    logger.error(f"连接器不存在: {connector_id}")
                    return False

                # 更新允许的字段
                allowed_fields = ["name", "description", "version", "enabled"]
                for field in allowed_fields:
                    if field in updates:
                        setattr(connector, field, updates[field])

                connector.updated_at = datetime.now(timezone.utc)
                session.commit()

                logger.info(f"更新连接器配置成功: {connector_id}")
                return True

        except Exception as e:
            logger.error(f"更新连接器配置失败 {connector_id}: {e}")
            return False

    def get_connector_status(self, connector_id: str) -> Dict[str, Any]:
        """获取连接器运行状态"""
        return self.process_manager.get_process_status(connector_id)

    def scan_directory_for_connectors(
        self, connectors_dir: str
    ) -> List[Dict[str, Any]]:
        """递归扫描目录中的所有connector.json文件"""
        try:
            import os

            discovered = []
            base_path = Path(connectors_dir)

            logger.info(f"开始扫描目录: {base_path.resolve()}")

            if not base_path.exists():
                logger.warning(f"目录不存在: {base_path}")
                return discovered

            # 递归查找所有的 connector.json 文件
            config_files = list(base_path.rglob("connector.json"))
            logger.info(f"找到 {len(config_files)} 个 connector.json 文件")

            for config_file in config_files:
                try:
                    connector_dir = config_file.parent

                    # 读取配置文件
                    with open(config_file, "r", encoding="utf-8") as f:
                        config = json.load(f)

                    # 从配置或目录名获取连接器ID
                    connector_id = config.get("id", connector_dir.name)

                    # 查找可执行文件
                    potential_names = [
                        f"linch-mind-{connector_id}",
                        f"linch-mind-{connector_id}.exe",
                        connector_id,
                        f"{connector_id}.exe",
                    ]

                    executable_path = None
                    # 在连接器目录及其子目录中查找可执行文件
                    for name in potential_names:
                        # 先在当前目录找
                        exe_path = connector_dir / name
                        if exe_path.exists() and exe_path.is_file():
                            executable_path = str(exe_path)
                            break
                        # 在bin/release目录找
                        exe_path = connector_dir / "bin" / "release" / name
                        if exe_path.exists() and exe_path.is_file():
                            executable_path = str(exe_path)
                            break
                        # 在bin目录找
                        exe_path = connector_dir / "bin" / name
                        if exe_path.exists() and exe_path.is_file():
                            executable_path = str(exe_path)
                            break

                    logger.info(f"发现连接器: {connector_id} at {connector_dir}")
                    if executable_path:
                        logger.info(f"  - 可执行文件: {executable_path}")
                    else:
                        logger.warning(f"  - 未找到可执行文件")

                    # 检查是否已注册
                    with self.db_service.get_session() as session:
                        existing = (
                            session.query(Connector)
                            .filter_by(connector_id=connector_id)
                            .first()
                        )
                        is_registered = existing is not None

                    discovered.append(
                        {
                            "connector_id": connector_id,
                            "name": config.get("name", connector_id),
                            "description": config.get("description", ""),
                            "version": config.get("version", "unknown"),
                            "type": config.get("type", "unknown"),
                            "path": executable_path if executable_path else "",
                            "config_path": str(config_file),
                            "is_registered": is_registered,
                            "config": config,
                        }
                    )

                except Exception as e:
                    logger.error(f"处理配置文件失败 {config_file}: {e}")

            logger.info(f"扫描完成，发现 {len(discovered)} 个连接器")
            return discovered

        except Exception as e:
            logger.error(f"扫描连接器目录失败: {e}")
            return []

    def register_connector_from_path(self, connector_path: str) -> bool:
        """从路径注册连接器"""
        try:
            path = Path(connector_path)

            # 查找对应的connector.json
            connector_dir = path.parent
            while connector_dir != connector_dir.parent:
                config_file = connector_dir / "connector.json"
                if config_file.exists():
                    break
                connector_dir = connector_dir.parent
            else:
                logger.error(f"找不到连接器配置文件: {connector_path}")
                return False

            # 读取配置
            with open(config_file) as f:
                config = json.load(f)

            connector_id = config.get("id", connector_dir.name)
            name = config.get("name", connector_id)
            description = config.get("description", "")
            version = config.get("version", "unknown")

            # 注册连接器
            asyncio.run(
                self.register_connector(
                    connector_id=connector_id,
                    name=name,
                    path=str(path),
                    description=description,
                    version=version,
                )
            )

            return True

        except Exception as e:
            logger.error(f"从路径注册连接器失败 {connector_path}: {e}")
            return False

    async def start_all_registered_connectors(self) -> None:
        """启动所有已注册的连接器"""
        try:
            with self.db_service.get_session() as session:
                # 获取所有启用的连接器
                enabled_connectors = (
                    session.query(Connector).filter_by(enabled=True).all()
                )

            start_tasks = []
            for connector in enabled_connectors:
                if connector.status != "running":
                    logger.info(
                        f"启动连接器: {connector.name} ({connector.connector_id})"
                    )
                    # 注意：这里我们直接调用start_connector，而不是创建异步任务
                    # 因为start_connector已经是异步方法
                    success = await self.start_connector(connector.connector_id)
                    if not success:
                        logger.error(f"启动连接器失败: {connector.connector_id}")
                else:
                    # 验证数据库显示"运行中"的连接器实际进程状态
                    logger.info(f"验证连接器状态: {connector.name}")

                    # 检查实际进程状态
                    actual_pid = self.process_manager.get_running_pid(
                        connector.connector_id
                    )
                    if actual_pid:
                        # 进程确实存在，同步到ProcessManager内存
                        if (
                            connector.connector_id
                            not in self.process_manager.running_processes
                        ):
                            try:
                                # 同步现有进程到内存状态
                                self.process_manager.running_processes[
                                    connector.connector_id
                                ] = {
                                    "pid": actual_pid,
                                    "process": None,  # 无法恢复subprocess对象
                                    "command": None,
                                    "working_dir": None,
                                    "start_time": None,
                                    "note": "recovered_on_startup",
                                }
                                logger.info(
                                    f"连接器已在运行，已同步到内存: {connector.name} (PID: {actual_pid})"
                                )
                            except Exception as e:
                                logger.error(
                                    f"同步连接器状态到内存失败 {connector.connector_id}: {e}"
                                )
                        else:
                            logger.info(
                                f"连接器已在运行: {connector.name} (PID: {actual_pid})"
                            )
                    else:
                        # 数据库显示运行但进程不存在，修正数据库状态
                        logger.warning(
                            f"连接器 {connector.name} 数据库显示运行但进程不存在，修正状态"
                        )
                        with self.db_service.get_session() as session:
                            connector_in_db = (
                                session.query(Connector)
                                .filter_by(connector_id=connector.connector_id)
                                .first()
                            )
                            if connector_in_db:
                                connector_in_db.status = "stopped"
                                connector_in_db.process_id = None
                                connector_in_db.updated_at = datetime.now(timezone.utc)
                                session.commit()
                                logger.info(
                                    f"已修正连接器 {connector.name} 数据库状态为 stopped"
                                )

        except Exception as e:
            logger.error(f"启动所有连接器失败: {e}")

    async def restart_connector(self, connector_id: str) -> bool:
        """重启连接器"""
        try:
            # 先停止连接器
            await self.stop_connector(connector_id)
            # 等待一小段时间确保进程完全退出
            import asyncio

            await asyncio.sleep(0.5)
            # 重新启动连接器
            return await self.start_connector(connector_id)
        except Exception as e:
            logger.error(f"重启连接器失败 {connector_id}: {e}")
            return False

    async def stop_all_connectors(self) -> None:
        """停止所有连接器"""
        try:
            with self.db_service.get_session() as session:
                # 获取所有运行中的连接器
                running_connectors = (
                    session.query(Connector).filter_by(status="running").all()
                )

            for connector in running_connectors:
                logger.info(f"停止连接器: {connector.name} ({connector.connector_id})")
                success = await self.stop_connector(connector.connector_id)
                if not success:
                    logger.error(f"停止连接器失败: {connector.connector_id}")

        except Exception as e:
            logger.error(f"停止所有连接器失败: {e}")

    async def delete_connector(self, connector_id: str, force: bool = False) -> bool:
        """删除/卸载连接器"""
        try:
            # 1. 检查连接器是否存在
            with self.db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )

                if not connector:
                    logger.warning(f"尝试删除不存在的连接器: {connector_id}")
                    return False

                # 2. 如果连接器正在运行，先停止
                if connector.status == "running":
                    logger.info(f"连接器正在运行，先停止: {connector_id}")
                    stop_success = await self.stop_connector(connector_id)
                    if not stop_success and not force:
                        logger.error(f"无法停止连接器，删除失败: {connector_id}")
                        return False

                # 3. 从数据库中删除记录
                session.delete(connector)
                session.commit()
                logger.info(f"连接器已从数据库中删除: {connector_id}")

            # 4. 清理进程管理器中的记录
            if connector_id in self.active_processes:
                del self.active_processes[connector_id]

            # 5. 通知进程管理器清理
            self.process_manager.cleanup_process(connector_id)

            logger.info(f"连接器删除成功: {connector_id}")
            return True

        except Exception as e:
            logger.error(f"删除连接器失败 {connector_id}: {e}")
            return False

    def _resolve_connector_executable_path(
        self, connector_id: str, connector_config: Dict[str, Any]
    ) -> Optional[str]:
        """解析连接器的可执行文件路径

        根据connector.json中的entry配置和平台信息，确定可执行文件的实际路径
        修复路径未设置导致的启动失败问题
        """
        try:
            import platform

            # 确定当前平台
            system = platform.system().lower()
            platform_map = {"darwin": "macos", "linux": "linux", "windows": "windows"}
            current_platform = platform_map.get(system, system)

            # 从配置中获取entry信息
            entry_config = connector_config.get("entry", {})

            # 查找连接器根目录 - 支持多种路径
            possible_base_dirs = [
                Path("connectors"),
                Path("../connectors"),
                Path(__file__).parent.parent.parent.parent
                / "connectors",  # 从daemon/services/connectors向上找
            ]

            connector_base_dirs = []
            for base in possible_base_dirs:
                if base.exists():
                    connector_base_dirs.extend(
                        [base / "official" / connector_id, base / connector_id]
                    )
                    break

            connector_dir = None
            for base_dir in connector_base_dirs:
                if base_dir.exists():
                    connector_dir = base_dir
                    break

            if not connector_dir:
                logger.error(f"找不到连接器目录: {connector_id}")
                return None

            # 1. 首先尝试production配置中的平台特定路径
            if "production" in entry_config:
                production_config = entry_config["production"]
                if current_platform in production_config:
                    rel_path = production_config[current_platform]
                    executable_path = connector_dir / rel_path

                    if executable_path.exists():
                        logger.debug(f"使用production路径: {executable_path}")
                        return str(executable_path.resolve())

            # 2. 搜索常见的可执行文件名
            potential_names = [
                f"linch-mind-{connector_id}",
                f"linch-mind-{connector_id}.exe",
                connector_id,
                f"{connector_id}.exe",
            ]

            # 搜索目录
            search_dirs = [
                connector_dir / "bin" / "release",
                connector_dir / "bin" / "debug",
                connector_dir / "bin",
                connector_dir,
            ]

            for search_dir in search_dirs:
                if not search_dir.exists():
                    continue

                for exe_name in potential_names:
                    exe_path = search_dir / exe_name
                    if exe_path.exists() and exe_path.is_file():
                        logger.debug(f"找到可执行文件: {exe_path}")
                        return str(exe_path.resolve())

            logger.warning(f"未找到连接器 {connector_id} 的可执行文件")
            logger.debug(f"搜索路径: {[str(d) for d in search_dirs]}")
            logger.debug(f"搜索文件名: {potential_names}")

            return None

        except Exception as e:
            logger.error(f"解析连接器路径失败 {connector_id}: {e}")
            return None

    # ===== 健康检查支持方法 =====

    def get_running_connectors(self) -> List[str]:
        """获取所有运行中的连接器ID列表"""
        try:
            with self.db_service.get_session() as session:
                running_connectors = (
                    session.query(Connector).filter_by(status="running").all()
                )
                return [c.connector_id for c in running_connectors]
        except Exception as e:
            logger.error(f"获取运行中连接器列表失败: {e}")
            return []

    def is_connector_running(self, connector_id: str) -> bool:
        """检查指定连接器是否正在运行"""
        try:
            with self.db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id, status="running")
                    .first()
                )
                return connector is not None
        except Exception as e:
            logger.error(f"检查连接器运行状态失败 {connector_id}: {e}")
            return False

    def get_process_info(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取连接器的进程信息"""
        try:
            # 先从进程管理器获取实时状态
            process_status = self.process_manager.get_process_status(connector_id)

            # 获取数据库中的连接器信息
            with self.db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )

                if not connector:
                    return None

                # 如果进程状态为运行中，但数据库显示停止，同步状态
                if (
                    process_status.get("status") == "running"
                    and connector.status != "running"
                ):
                    logger.info(
                        f"同步连接器状态: {connector_id} 数据库状态更新为 running"
                    )
                    connector.status = "running"
                    connector.process_id = process_status.get("pid")
                    connector.updated_at = datetime.now(timezone.utc)
                    session.commit()

                # 如果进程已停止但数据库显示运行中，同步状态
                elif (
                    process_status.get("status") in ["not_running", "dead"]
                    and connector.status == "running"
                ):
                    logger.info(
                        f"同步连接器状态: {connector_id} 数据库状态更新为 stopped"
                    )
                    connector.status = "stopped"
                    connector.process_id = None
                    connector.updated_at = datetime.now(timezone.utc)
                    session.commit()

                # 返回统一的进程信息
                return {
                    "connector_id": connector_id,
                    "pid": process_status.get("pid") or connector.process_id,
                    "status": process_status.get("status", "unknown"),
                    "name": connector.name,
                    "path": connector.path,
                    "db_status": connector.status,
                    "process_status": process_status,
                }

        except Exception as e:
            logger.error(f"获取连接器进程信息失败 {connector_id}: {e}")
            return None
