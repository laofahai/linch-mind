#!/usr/bin/env python3
"""
连接器管理器 - 使用数据库持久化，无instance概念
"""

import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from models.database_models import Connector
from services.database_service import get_database_service

logger = logging.getLogger(__name__)


class ConnectorManager:
    """连接器管理器 - 使用数据库持久化"""

    def __init__(self, connectors_dir: Path):
        self.connectors_dir = Path(connectors_dir)
        self.db_service = get_database_service()
        self.active_processes: Dict[str, subprocess.Popen] = {}  # 内存中的进程引用

        # 初始化时恢复进程引用
        self._recover_running_processes()

        logger.info(f"连接器管理器初始化完成，数据库连接已建立")

    def _recover_running_processes(self):
        """恢复运行中的进程引用"""
        try:
            import psutil

            with self.db_service.get_session() as session:
                running_connectors = (
                    session.query(Connector).filter_by(status="running").all()
                )

                for connector in running_connectors:
                    if connector.process_id:
                        try:
                            # 检查进程是否仍在运行
                            if psutil.pid_exists(connector.process_id):
                                process = psutil.Process(connector.process_id)
                                # 简单验证：检查进程是否是Python进程
                                if "python" in process.name().lower():
                                    logger.info(
                                        f"恢复连接器进程引用: {connector.connector_id} (PID: {connector.process_id})"
                                    )
                                    # 注意：这里我们不能完全恢复subprocess.Popen对象
                                    # 但我们可以记录PID以便后续管理
                                    continue

                            # 进程不存在，更新状态
                            logger.warning(
                                f"连接器进程已退出: {connector.connector_id} (PID: {connector.process_id})"
                            )
                            connector.status = "error"
                            connector.process_id = None
                            connector.error_message = "进程异常退出，需要重新启动"

                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            # 进程不存在或无权限访问，更新状态
                            connector.status = "error"
                            connector.process_id = None
                            connector.error_message = "进程异常退出，需要重新启动"

                session.commit()

        except ImportError:
            logger.warning("psutil未安装，跳过进程恢复。建议安装psutil以支持进程管理")
        except Exception as e:
            logger.error(f"恢复进程引用失败: {e}")

    def register_connector(
        self, connector_id: str, name: str, description: str, path: Path
    ):
        """注册连接器到数据库"""
        try:
            # 检查并读取连接器配置
            config_file = path / "connector.json"
            if not config_file.exists():
                raise ValueError(f"连接器配置文件不存在: {config_file}")

            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)

            # 获取正确的入口点
            entry_point = self._find_entry_point(config, path)
            config["entry_point"] = entry_point

            # 设置路径信息
            config["path"] = str(path)
            config["executable_path"] = str(path / entry_point)

            with self.db_service.get_session() as session:
                # 检查是否已存在
                existing = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )
                if existing:
                    logger.info(f"连接器已存在，更新信息: {connector_id}")
                    existing.name = name
                    existing.description = description
                    existing.config = config
                    existing.updated_at = datetime.now(timezone.utc)
                else:
                    # 创建新连接器
                    connector = Connector(
                        connector_id=connector_id,
                        name=name,
                        description=description,
                        config=config,
                        status="stopped",
                    )
                    session.add(connector)

                session.commit()
                logger.info(f"注册连接器: {connector_id} - {name}")

        except Exception as e:
            logger.error(f"注册连接器失败 {connector_id}: {e}")

    async def start_connector(self, connector_id: str) -> bool:
        """启动连接器"""
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

                if connector.status == "running":
                    logger.warning(f"连接器已在运行: {connector_id}")
                    return True

                # 从配置中获取可执行路径
                if not connector.config or not connector.config.get("executable_path"):
                    logger.error(f"连接器配置无效: {connector_id}")
                    connector.status = "error"
                    session.commit()
                    return False

                entry_script = Path(connector.config["executable_path"])
                if not entry_script.exists():
                    logger.error(f"连接器入口脚本不存在: {entry_script}")
                    connector.status = "error"
                    session.commit()
                    return False

                # 检测是否为可执行文件还是Python脚本
                if entry_script.suffix == ".py":
                    # Python脚本
                    cmd = ["python", str(entry_script)]
                else:
                    # 可执行文件（如C++编译的连接器）
                    cmd = [str(entry_script)]
                    
                # 启动进程
                process = subprocess.Popen(
                    cmd,
                    cwd=entry_script.parent,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                # 更新数据库状态
                connector.status = "running"
                connector.process_id = process.pid
                session.commit()

                # 保存进程引用
                self.active_processes[connector_id] = process

                logger.info(f"连接器启动成功: {connector_id} (PID: {process.pid})")
                return True

        except Exception as e:
            logger.error(f"启动连接器失败 {connector_id}: {e}")
            # 更新错误状态
            try:
                with self.db_service.get_session() as session:
                    connector = (
                        session.query(Connector)
                        .filter_by(connector_id=connector_id)
                        .first()
                    )
                    if connector:
                        connector.status = "error"
                        connector.process_id = None
                        session.commit()
            except:
                pass
            return False

    async def stop_connector(self, connector_id: str) -> bool:
        """停止连接器"""
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

                if connector.status != "running":
                    logger.warning(f"连接器未运行: {connector_id}")
                    return True

                # 尝试停止进程
                success = False

                # 方法1: 使用内存中的进程引用
                process = self.active_processes.get(connector_id)
                if process:
                    try:
                        process.terminate()
                        try:
                            process.wait(timeout=10)
                            success = True
                        except subprocess.TimeoutExpired:
                            logger.warning(
                                f"连接器 {connector_id} 未响应终止信号，强制停止"
                            )
                            process.kill()
                            process.wait()
                            success = True
                    except Exception as e:
                        logger.error(f"通过进程引用停止失败: {e}")
                    finally:
                        # 移除进程引用
                        del self.active_processes[connector_id]

                # 方法2: 如果没有进程引用，尝试通过PID停止
                elif connector.process_id:
                    try:
                        import psutil

                        if psutil.pid_exists(connector.process_id):
                            process = psutil.Process(connector.process_id)
                            process.terminate()
                            try:
                                process.wait(timeout=10)
                                success = True
                            except psutil.TimeoutExpired:
                                logger.warning(
                                    f"连接器 {connector_id} 未响应终止信号，强制停止"
                                )
                                process.kill()
                                success = True
                        else:
                            # 进程已经不存在
                            success = True
                    except ImportError:
                        logger.warning(
                            f"psutil未安装，无法通过PID停止进程 {connector.process_id}"
                        )
                    except Exception as e:
                        logger.error(f"通过PID停止进程失败: {e}")
                else:
                    # 没有进程信息，直接标记为停止
                    success = True

                # 更新数据库状态
                connector.status = "stopped" if success else "error"
                connector.process_id = None
                if success:
                    connector.error_message = None
                else:
                    connector.error_message = "停止进程失败"
                session.commit()

                if success:
                    logger.info(f"连接器停止成功: {connector_id}")
                else:
                    logger.error(f"连接器停止失败: {connector_id}")
                return success

        except Exception as e:
            logger.error(f"停止连接器失败 {connector_id}: {e}")
            return False

    def get_connector_status(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取连接器状态"""
        try:
            with self.db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )
                if not connector:
                    return None

                return {
                    "connector_id": connector.connector_id,
                    "name": connector.name,
                    "description": connector.description,
                    "status": connector.status,
                    "pid": connector.process_id,
                    "created_at": (
                        connector.created_at.isoformat()
                        if connector.created_at
                        else None
                    ),
                }
        except Exception as e:
            logger.error(f"获取连接器状态失败 {connector_id}: {e}")
            return None

    def list_connectors(self) -> List[Dict[str, Any]]:
        """列出所有连接器"""
        try:
            with self.db_service.get_session() as session:
                connectors = session.query(Connector).all()
                return [
                    {
                        "connector_id": c.connector_id,
                        "name": c.name,
                        "description": c.description,
                        "status": c.status,
                        "pid": c.process_id,
                    }
                    for c in connectors
                ]
        except Exception as e:
            logger.error(f"列出连接器失败: {e}")
            return []

    async def start_all_registered_connectors(self):
        """启动所有已注册的连接器"""
        try:
            with self.db_service.get_session() as session:
                connectors = session.query(Connector).all()
                for connector in connectors:
                    await self.start_connector(connector.connector_id)
        except Exception as e:
            logger.error(f"启动所有连接器失败: {e}")

    async def stop_all_connectors(self):
        """停止所有连接器"""
        try:
            with self.db_service.get_session() as session:
                running_connectors = (
                    session.query(Connector).filter_by(status="running").all()
                )
                for connector in running_connectors:
                    await self.stop_connector(connector.connector_id)
        except Exception as e:
            logger.error(f"停止所有连接器失败: {e}")

    def scan_directory_for_connectors(
        self, directory_path: str
    ) -> List[Dict[str, Any]]:
        """扫描指定目录中的连接器 - 支持递归深度扫描"""
        discovered_connectors = []
        try:
            scan_path = Path(directory_path)
            if not scan_path.exists() or not scan_path.is_dir():
                logger.warning(f"指定的目录不存在或不是目录: {directory_path}")
                return discovered_connectors

            # 递归扫描函数
            def _scan_recursive(path: Path, max_depth: int = 3, current_depth: int = 0):
                if current_depth > max_depth:
                    return

                # 检查当前目录是否包含connector.json
                config_file = path / "connector.json"
                if config_file.exists():
                    try:
                        with open(config_file, "r", encoding="utf-8") as f:
                            config = json.load(f)

                        connector_info = {
                            "path": str(path),
                            "connector_id": config.get("id", path.name),
                            "name": config.get("name", path.name),
                            "description": config.get("description", ""),
                            "version": config.get("version", "1.0.0"),
                            "entry_point": self._find_entry_point(config, path),
                            "is_registered": self._is_connector_registered(
                                config.get("id", path.name)
                            ),
                        }
                        discovered_connectors.append(connector_info)
                        logger.info(f"发现连接器: {connector_info['name']} at {path}")
                        return  # 如果找到connector.json，就不再深入子目录
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"解析连接器配置失败 {config_file}: {e}")

                # 如果当前目录不是连接器，则递归查找子目录
                try:
                    for item in path.iterdir():
                        if item.is_dir() and not item.name.startswith("."):
                            # 跳过常见的非连接器目录
                            if item.name in [
                                "__pycache__",
                                "node_modules",
                                ".git",
                                "venv",
                                ".venv",
                            ]:
                                continue
                            _scan_recursive(item, max_depth, current_depth + 1)
                except PermissionError:
                    logger.warning(f"没有权限访问目录: {path}")
                except Exception as e:
                    logger.warning(f"扫描目录时出错 {path}: {e}")

            # 开始递归扫描
            _scan_recursive(scan_path)

        except Exception as e:
            logger.error(f"扫描目录失败 {directory_path}: {e}")

        return discovered_connectors

    def _find_entry_point(self, config: Dict[str, Any], path: Path) -> str:
        """从配置中查找入口点"""
        # 检查配置中的 entry 字段
        if "entry" in config:
            entry = config["entry"]
            if isinstance(entry, dict):
                # 对于C++/编译型连接器，优先使用 production 入口
                if "production" in entry:
                    prod_entry = entry["production"]
                    if isinstance(prod_entry, dict):
                        # 根据平台选择
                        import platform

                        system = platform.system().lower()
                        if system == "darwin":
                            system = "macos"
                        return prod_entry.get(system, "main.py")
                    else:
                        return prod_entry
                # 对于Python连接器，使用 development 入口
                elif "development" in entry and isinstance(entry["development"], dict):
                    dev_entry = entry["development"]
                    # 如果是Python脚本直接执行的情况
                    if "command" in dev_entry and dev_entry["command"] == "python":
                        if "args" in dev_entry and dev_entry["args"]:
                            return dev_entry["args"][0]

        # 默认返回 main.py
        return config.get("entry_point", "main.py")

    def _is_connector_registered(self, connector_id: str) -> bool:
        """检查连接器是否已注册"""
        try:
            with self.db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )
                return connector is not None
        except Exception:
            return False

    def health_check_all_connectors(self):
        """健康检查所有运行中的连接器"""
        try:
            import psutil

            with self.db_service.get_session() as session:
                running_connectors = (
                    session.query(Connector).filter_by(status="running").all()
                )

                for connector in running_connectors:
                    health_status = self._check_connector_health(connector)
                    
                    if health_status["healthy"]:
                        # 进程正常运行，更新心跳时间
                        connector.last_heartbeat = datetime.now(timezone.utc)
                        connector.error_message = None
                    else:
                        # 进程异常，更新状态
                        logger.warning(
                            f"检测到连接器异常: {connector.connector_id} - {health_status['error']}"
                        )
                        connector.status = "error"
                        connector.process_id = None
                        connector.error_message = health_status["error"]

                        # 清理内存中的进程引用
                        if connector.connector_id in self.active_processes:
                            del self.active_processes[connector.connector_id]

                session.commit()

        except ImportError:
            logger.debug("psutil未安装，跳过健康检查")
        except Exception as e:
            logger.error(f"健康检查失败: {e}")

    def _check_connector_health(self, connector) -> Dict[str, Any]:
        """检查单个连接器的健康状态"""
        try:
            import psutil
            
            if not connector.process_id:
                return {"healthy": False, "error": "无进程ID"}
            
            # 检查进程是否存在
            if not psutil.pid_exists(connector.process_id):
                return {"healthy": False, "error": "进程不存在"}
            
            try:
                process = psutil.Process(connector.process_id)
                
                # 检查进程状态
                if process.status() == psutil.STATUS_ZOMBIE:
                    return {"healthy": False, "error": "进程为僵尸状态"}
                
                # 检查进程是否响应（简单的存活检查）
                if "python" in process.name().lower() or connector.connector_id in process.cmdline():
                    # 检查心跳超时
                    if connector.last_heartbeat:
                        time_since_heartbeat = datetime.now(timezone.utc) - connector.last_heartbeat
                        if time_since_heartbeat.total_seconds() > 300:  # 5分钟超时
                            return {"healthy": False, "error": "心跳超时"}
                    
                    return {"healthy": True, "error": None}
                else:
                    return {"healthy": False, "error": "进程名称不匹配"}
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                return {"healthy": False, "error": f"无法访问进程: {str(e)}"}
                
        except ImportError:
            # 如果没有psutil，只能基于心跳时间判断
            if connector.last_heartbeat:
                time_since_heartbeat = datetime.now(timezone.utc) - connector.last_heartbeat
                if time_since_heartbeat.total_seconds() > 600:  # 10分钟超时
                    return {"healthy": False, "error": "心跳超时"}
                return {"healthy": True, "error": None}
            else:
                return {"healthy": False, "error": "无心跳记录"}
        except Exception as e:
            return {"healthy": False, "error": f"健康检查异常: {str(e)}"}

    def get_detailed_connector_status(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取连接器详细状态信息"""
        try:
            with self.db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )
                if not connector:
                    return None

                # 基本状态信息
                status_info = {
                    "connector_id": connector.connector_id,
                    "name": connector.name,
                    "description": connector.description,
                    "status": connector.status,
                    "process_id": connector.process_id,
                    "created_at": connector.created_at.isoformat() if connector.created_at else None,
                    "updated_at": connector.updated_at.isoformat() if connector.updated_at else None,
                    "last_heartbeat": connector.last_heartbeat.isoformat() if connector.last_heartbeat else None,
                    "error_message": connector.error_message,
                    "config": connector.config,
                }

                # 健康检查信息
                if connector.status == "running":
                    health_status = self._check_connector_health(connector)
                    status_info["health"] = health_status
                    
                    # 进程详细信息
                    if connector.process_id:
                        process_info = self._get_process_info(connector.process_id)
                        status_info["process_info"] = process_info

                # 统计信息
                statistics = self._get_connector_statistics(connector_id)
                status_info["statistics"] = statistics

                return status_info
                
        except Exception as e:
            logger.error(f"获取连接器详细状态失败 {connector_id}: {e}")
            return None

    def _get_process_info(self, process_id: int) -> Dict[str, Any]:
        """获取进程详细信息"""
        try:
            import psutil
            
            if not psutil.pid_exists(process_id):
                return {"exists": False}
            
            process = psutil.Process(process_id)
            
            return {
                "exists": True,
                "pid": process_id,
                "name": process.name(),
                "status": process.status(),
                "create_time": datetime.fromtimestamp(process.create_time()).isoformat(),
                "cpu_percent": process.cpu_percent(),
                "memory_info": {
                    "rss": process.memory_info().rss,
                    "vms": process.memory_info().vms,
                    "percent": process.memory_percent()
                },
                "num_threads": process.num_threads(),
                "cmdline": process.cmdline(),
            }
            
        except ImportError:
            return {"exists": "unknown", "error": "psutil not available"}
        except Exception as e:
            return {"exists": False, "error": str(e)}

    def _get_connector_statistics(self, connector_id: str) -> Dict[str, Any]:
        """获取连接器统计信息"""
        try:
            with self.db_service.get_session() as session:
                from models.database_models import DataSource, Entity
                
                # 数据源统计
                data_sources = session.query(DataSource).filter_by(connector_id=connector_id).all()
                data_source_count = len(data_sources)
                
                # 实体统计
                if data_sources:
                    data_source_ids = [ds.id for ds in data_sources]
                    entity_count = session.query(Entity).filter(
                        Entity.data_source_id.in_(data_source_ids)
                    ).count()
                else:
                    entity_count = 0
                
                return {
                    "data_sources": data_source_count,
                    "entities": entity_count,
                    "last_data_update": None,  # 可以从实体的最新创建时间获取
                    "total_uptime": None,  # 可以从创建时间计算
                }
                
        except Exception as e:
            logger.error(f"获取连接器统计信息失败: {e}")
            return {
                "data_sources": 0,
                "entities": 0,
                "error": str(e)
            }

    def get_system_health_overview(self) -> Dict[str, Any]:
        """获取连接器系统整体健康状况"""
        try:
            with self.db_service.get_session() as session:
                all_connectors = session.query(Connector).all()
                
                # 状态统计
                status_counts = {}
                healthy_count = 0
                total_entities = 0
                total_data_sources = 0
                
                for connector in all_connectors:
                    status = connector.status
                    status_counts[status] = status_counts.get(status, 0) + 1
                    
                    # 健康检查
                    if status == "running":
                        health_status = self._check_connector_health(connector)
                        if health_status["healthy"]:
                            healthy_count += 1
                    
                    # 统计数据
                    stats = self._get_connector_statistics(connector.connector_id)
                    total_entities += stats.get("entities", 0)
                    total_data_sources += stats.get("data_sources", 0)
                
                total_connectors = len(all_connectors)
                running_connectors = status_counts.get("running", 0)
                
                # 计算健康度
                if total_connectors == 0:
                    health_score = 0
                else:
                    health_score = (healthy_count / total_connectors) * 100
                
                # 确定整体状态
                if health_score >= 90:
                    overall_status = "healthy"
                elif health_score >= 70:
                    overall_status = "warning" 
                elif health_score >= 50:
                    overall_status = "degraded"
                else:
                    overall_status = "critical"
                
                return {
                    "overall_status": overall_status,
                    "health_score": round(health_score, 1),
                    "total_connectors": total_connectors,
                    "running_connectors": running_connectors,
                    "healthy_connectors": healthy_count,
                    "status_breakdown": status_counts,
                    "total_entities": total_entities,
                    "total_data_sources": total_data_sources,
                    "last_check": datetime.now(timezone.utc).isoformat(),
                }
                
        except Exception as e:
            logger.error(f"获取系统健康概览失败: {e}")
            return {
                "overall_status": "error",
                "health_score": 0,
                "error": str(e),
                "last_check": datetime.now(timezone.utc).isoformat(),
            }

    async def auto_restart_failed_connectors(self) -> List[Dict[str, Any]]:
        """自动重启失败的连接器"""
        restart_results = []
        
        try:
            with self.db_service.get_session() as session:
                failed_connectors = session.query(Connector).filter_by(status="error").all()
                
                for connector in failed_connectors:
                    if connector.auto_start:  # 只重启设置了自动启动的连接器
                        try:
                            logger.info(f"尝试自动重启失败的连接器: {connector.connector_id}")
                            success = await self.start_connector(connector.connector_id)
                            
                            restart_results.append({
                                "connector_id": connector.connector_id,
                                "success": success,
                                "reason": "auto_restart_after_failure"
                            })
                            
                        except Exception as e:
                            logger.error(f"自动重启连接器失败 {connector.connector_id}: {e}")
                            restart_results.append({
                                "connector_id": connector.connector_id,
                                "success": False,
                                "error": str(e),
                                "reason": "auto_restart_failed"
                            })
        
        except Exception as e:
            logger.error(f"自动重启失败连接器过程失败: {e}")
        
        return restart_results

    def register_connector_from_path(self, connector_path: str) -> Dict[str, Any]:
        """从指定路径注册连接器"""
        try:
            path = Path(connector_path)
            config_file = path / "connector.json"

            if not config_file.exists():
                raise ValueError(f"连接器配置文件不存在: {config_file}")

            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)

            connector_id = config.get("id")
            name = config.get("name")
            description = config.get("description", "")

            if not connector_id or not name:
                raise ValueError("连接器配置缺少必要字段: id 或 name")

            # 注册连接器
            self.register_connector(connector_id, name, description, path)

            return {
                "success": True,
                "connector_id": connector_id,
                "name": name,
                "path": str(path),
            }

        except Exception as e:
            logger.error(f"从路径注册连接器失败 {connector_path}: {e}")
            return {"success": False, "error": str(e)}


# 全局单例
_connector_manager = None


def get_connector_manager(connectors_dir: Path = None) -> ConnectorManager:
    """获取连接器管理器单例"""
    global _connector_manager
    if _connector_manager is None:
        if connectors_dir is None:
            from config.core_config import get_connector_config

            connector_config = get_connector_config()
            connectors_dir = Path(connector_config.config_dir)

        _connector_manager = ConnectorManager(connectors_dir)

        # 连接器需要手动注册，不再自动扫描

    return _connector_manager


# 自动发现功能已移除，使用手动注册
