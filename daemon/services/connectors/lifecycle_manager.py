#!/usr/bin/env python3
"""
连接器生命周期管理器 - 统一的状态转换和生命周期控制
替代原有的分散式管理，提供清晰的状态转换机制
"""

import asyncio
import subprocess
import psutil
import signal
import uuid
from pathlib import Path
from typing import Dict, Optional, List, Callable, Any
from datetime import datetime, timedelta
from enum import Enum
import logging

from .connector_type_config import (
    ConnectorTypeConfigManager, 
    ConnectorInstanceInfo, 
    ConnectorTypeInfo,
    get_connector_type_config_manager
)
from .process_manager import get_process_manager, ProcessManager

logger = logging.getLogger(__name__)


class ConnectorState(Enum):
    """连接器状态枚举 - 清晰的状态转换"""
    
    # 发现状态
    AVAILABLE = "available"        # 在registry中可见，可安装
    
    # 安装状态  
    INSTALLED = "installed"        # 已安装文件，可配置实例
    
    # 配置状态
    CONFIGURED = "configured"      # 已创建实例，有配置，但未启用
    
    # 运行状态
    ENABLED = "enabled"           # 已启用，但未运行
    RUNNING = "running"           # 正在运行
    
    # 错误状态
    ERROR = "error"               # 运行出错
    STOPPING = "stopping"        # 正在停止
    
    # 特殊状态
    UPDATING = "updating"         # 正在更新
    UNINSTALLING = "uninstalling" # 正在卸载


class StateTransitionError(Exception):
    """状态转换错误"""
    pass


class ConnectorLifecycleManager:
    """连接器生命周期管理器
    
    管理连接器从发现、安装、配置、启动到运行的完整生命周期
    提供清晰的状态转换和事件处理机制
    """
    
    def __init__(self, config_manager: ConnectorTypeConfigManager = None):
        self.config_manager = config_manager or get_connector_type_config_manager()
        self.process_manager = get_process_manager()
        
        # 运行时状态管理
        self._runtime_states: Dict[str, ConnectorState] = {}
        self._running_processes: Dict[str, subprocess.Popen] = {}
        self._process_monitors: Dict[str, asyncio.Task] = {}
        
        # 状态转换回调
        self._state_change_callbacks: List[Callable] = []
        
        # 健康检查和监控
        self._health_check_interval = 10  # 秒
        self._restart_attempts: Dict[str, int] = {}
        self._max_restart_attempts = 3
        self._restart_cooldown = 60  # 秒
        
        # 启动监控任务
        self._monitoring_task = None
        # 延迟启动监控任务，避免在非异步上下文中创建任务
        
        logger.info("连接器生命周期管理器初始化完成")
    
    def _start_monitoring(self):
        """启动后台监控任务"""
        try:
            if self._monitoring_task and not self._monitoring_task.done():
                self._monitoring_task.cancel()
            
            self._monitoring_task = asyncio.create_task(self._health_monitor_loop())
            logger.info("启动连接器健康监控")
        except RuntimeError as e:
            if "no running event loop" in str(e):
                logger.debug("没有运行的事件循环，延迟启动监控任务")
            else:
                raise
    
    async def ensure_monitoring_started(self):
        """确保监控任务已启动（在异步上下文中调用）"""
        if self._monitoring_task is None or self._monitoring_task.done():
            self._start_monitoring()
    
    async def _health_monitor_loop(self):
        """健康监控循环"""
        while True:
            try:
                await asyncio.sleep(self._health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                logger.info("健康监控任务被取消")
                break
            except Exception as e:
                logger.error(f"健康监控错误: {e}")
                await asyncio.sleep(self._health_check_interval * 2)
    
    async def _perform_health_checks(self):
        """执行健康检查"""
        for instance_id, process in list(self._running_processes.items()):
            try:
                if process.returncode is not None:
                    # 进程已退出
                    logger.warning(f"检测到连接器 {instance_id} 进程异常退出")
                    await self._handle_process_exit(instance_id, process.returncode)
                
                elif not self._is_process_healthy(process):
                    # 进程不健康
                    logger.warning(f"连接器 {instance_id} 健康检查失败")
                    await self._handle_unhealthy_process(instance_id)
                
            except Exception as e:
                logger.error(f"健康检查连接器 {instance_id} 时出错: {e}")
    
    def _is_process_healthy(self, process: subprocess.Popen) -> bool:
        """检查进程是否健康"""
        try:
            # 使用psutil进行更详细的健康检查
            ps_process = psutil.Process(process.pid)
            
            # 检查进程状态
            if ps_process.status() == psutil.STATUS_ZOMBIE:
                return False
            
            # 检查CPU和内存使用情况（可选）
            cpu_percent = ps_process.cpu_percent()
            memory_percent = ps_process.memory_percent()
            
            # 简单的健康检查：CPU使用率不超过80%，内存使用率不超过90%
            if cpu_percent > 80 or memory_percent > 90:
                logger.warning(f"进程 {process.pid} 资源使用异常: CPU {cpu_percent}%, 内存 {memory_percent}%")
                # 但不认为不健康，只是警告
            
            return True
            
        except psutil.NoSuchProcess:
            return False
        except Exception as e:
            logger.error(f"检查进程健康状态时出错: {e}")
            return False
    
    async def _handle_process_exit(self, instance_id: str, exit_code: int):
        """处理进程退出"""
        # 清理运行时状态
        self._cleanup_runtime_state(instance_id)
        
        if exit_code == 0:
            # 正常退出
            await self._transition_state(instance_id, ConnectorState.ENABLED)
            logger.info(f"连接器 {instance_id} 正常退出")
        else:
            # 异常退出，尝试重启
            await self._transition_state(instance_id, ConnectorState.ERROR)
            await self._attempt_restart(instance_id)
    
    async def _handle_unhealthy_process(self, instance_id: str):
        """处理不健康的进程"""
        logger.warning(f"连接器 {instance_id} 不健康，尝试重启")
        await self.stop_instance(instance_id, force=True)
        await self._attempt_restart(instance_id)
    
    async def _attempt_restart(self, instance_id: str):
        """尝试重启连接器"""
        attempt_count = self._restart_attempts.get(instance_id, 0)
        
        if attempt_count >= self._max_restart_attempts:
            logger.error(f"连接器 {instance_id} 已达到最大重启次数，停止自动重启")
            return
        
        # 等待冷却时间
        await asyncio.sleep(min(self._restart_cooldown, attempt_count * 10))
        
        self._restart_attempts[instance_id] = attempt_count + 1
        
        logger.info(f"尝试重启连接器 {instance_id} (第 {attempt_count + 1} 次)")
        
        success = await self.start_instance(instance_id)
        if success:
            logger.info(f"连接器 {instance_id} 重启成功")
            # 重置重启计数
            self._restart_attempts.pop(instance_id, None)
        else:
            logger.error(f"连接器 {instance_id} 重启失败")
    
    def _cleanup_runtime_state(self, instance_id: str):
        """清理运行时状态"""
        self._running_processes.pop(instance_id, None)
        
        # 取消进程监控任务
        monitor_task = self._process_monitors.pop(instance_id, None)
        if monitor_task and not monitor_task.done():
            monitor_task.cancel()
        
        # 获取实例信息以释放进程锁
        instance = self.config_manager.get_instance(instance_id)
        if instance:
            self.process_manager.release_lock(instance.type_id, instance_id)
    
    def register_state_change_callback(self, callback: Callable[[str, ConnectorState, ConnectorState], None]):
        """注册状态变化回调"""
        self._state_change_callbacks.append(callback)
    
    async def _transition_state(self, instance_id: str, new_state: ConnectorState):
        """状态转换"""
        old_state = self._runtime_states.get(instance_id, ConnectorState.CONFIGURED)
        
        # 验证状态转换的合法性
        if not self._is_valid_transition(old_state, new_state):
            raise StateTransitionError(f"非法状态转换: {old_state} -> {new_state}")
        
        # 更新运行时状态
        self._runtime_states[instance_id] = new_state
        
        # 更新配置中的状态
        self.config_manager.update_instance(instance_id, state=new_state.value)
        
        # 触发回调
        for callback in self._state_change_callbacks:
            try:
                await callback(instance_id, old_state, new_state)
            except Exception as e:
                logger.error(f"状态变化回调失败: {e}")
        
        logger.info(f"连接器 {instance_id} 状态转换: {old_state.value} -> {new_state.value}")
    
    def _is_valid_transition(self, from_state: ConnectorState, to_state: ConnectorState) -> bool:
        """验证状态转换是否合法"""
        # 相同状态转换总是合法的（幂等操作）
        if from_state == to_state:
            return True
            
        valid_transitions = {
            ConnectorState.AVAILABLE: [ConnectorState.INSTALLED],
            ConnectorState.INSTALLED: [ConnectorState.CONFIGURED, ConnectorState.UNINSTALLING],
            ConnectorState.CONFIGURED: [ConnectorState.ENABLED, ConnectorState.UNINSTALLING],
            ConnectorState.ENABLED: [ConnectorState.RUNNING, ConnectorState.CONFIGURED, ConnectorState.ERROR],
            ConnectorState.RUNNING: [ConnectorState.STOPPING, ConnectorState.ERROR, ConnectorState.UPDATING],
            ConnectorState.STOPPING: [ConnectorState.ENABLED, ConnectorState.ERROR],
            ConnectorState.ERROR: [ConnectorState.ENABLED, ConnectorState.CONFIGURED],
            ConnectorState.UPDATING: [ConnectorState.RUNNING, ConnectorState.ERROR],
            ConnectorState.UNINSTALLING: [ConnectorState.AVAILABLE]
        }
        
        allowed_states = valid_transitions.get(from_state, [])
        return to_state in allowed_states
    
    # === 公共API ===
    
    async def discover_connectors(self) -> List[ConnectorTypeInfo]:
        """发现可用的连接器"""
        logger.info("开始发现连接器")
        
        # 扫描连接器目录
        connectors_dir = self.config_manager.connectors_dir / "official"
        discovered_types = []
        
        if connectors_dir.exists():
            for connector_path in connectors_dir.iterdir():
                if connector_path.is_dir():
                    connector_type = await self._discover_connector_type(connector_path)
                    if connector_type:
                        discovered_types.append(connector_type)
                        
                        # 注册到配置管理器
                        self.config_manager.register_connector_type(connector_type)
        
        logger.info(f"发现 {len(discovered_types)} 个连接器类型")
        return discovered_types
    
    async def _discover_connector_type(self, connector_path: Path) -> Optional[ConnectorTypeInfo]:
        """发现单个连接器类型"""
        try:
            # 查找connector.json文件
            connector_json = connector_path / "connector.json"
            if not connector_json.exists():
                return None
            
            # 读取连接器元数据
            import json
            with open(connector_json, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            
            # 转换为ConnectorTypeInfo
            connector_type = ConnectorTypeInfo(
                type_id=metadata["id"],
                name=metadata["name"],
                display_name=metadata.get("display_name", metadata["name"]),
                description=metadata["description"],
                category=metadata.get("category", "other"),
                version=metadata["version"],
                author=metadata["author"],
                license=metadata.get("license", ""),
                
                supports_multiple_instances=metadata.get("capabilities", {}).get("supports_multiple_instances", False),
                max_instances_per_user=metadata.get("capabilities", {}).get("max_instances_per_user", 1),
                auto_discovery=metadata.get("capabilities", {}).get("auto_discovery", False),
                hot_config_reload=metadata.get("capabilities", {}).get("hot_config_reload", True),
                health_check=metadata.get("capabilities", {}).get("health_check", True),
                
                entry_point=metadata.get("entry", {}).get("development", {}).get("args", ["main.py"])[0],
                dependencies=metadata.get("dependencies", []),
                permissions=metadata.get("permissions", []),
                
                config_schema=metadata.get("config_schema", {}),
                default_config=metadata.get("default_config", {}),
                instance_templates=metadata.get("instance_templates", [])
            )
            
            return connector_type
            
        except Exception as e:
            logger.error(f"发现连接器类型失败 {connector_path}: {e}")
            return None
    
    async def install_connector(self, type_id: str) -> bool:
        """安装连接器"""
        logger.info(f"安装连接器: {type_id}")
        
        # 这里简化实现，实际中连接器已经在文件系统中
        # 只需要更新状态为已安装
        connector_type = self.config_manager.get_connector_type(type_id)
        if not connector_type:
            logger.error(f"连接器类型不存在: {type_id}")
            return False
        
        # 状态转换逻辑可以在这里扩展
        return True
    
    async def create_instance(self, type_id: str, display_name: str, config: Dict[str, Any], 
                            auto_start: bool = True, template_id: str = None) -> Optional[str]:
        """创建连接器实例"""
        logger.info(f"创建连接器实例: {type_id}")
        
        # 验证连接器类型存在
        connector_type = self.config_manager.get_connector_type(type_id)
        if not connector_type:
            logger.error(f"连接器类型不存在: {type_id}")
            return None
        
        # 检查多实例支持
        existing_instances = self.config_manager.list_instances(type_id=type_id)
        if not connector_type.supports_multiple_instances and existing_instances:
            logger.error(f"连接器类型 {type_id} 不支持多实例")
            return None
        
        if len(existing_instances) >= connector_type.max_instances_per_user:
            logger.error(f"已达到最大实例数限制: {connector_type.max_instances_per_user}")
            return None
        
        # 应用模板配置
        if template_id and connector_type.instance_templates:
            template = next((t for t in connector_type.instance_templates if t.get("id") == template_id), None)
            if template:
                template_config = template.get("config", {})
                config = {**template_config, **config}  # 用户配置覆盖模板配置
        
        # 生成实例ID
        instance_id = f"{type_id}_{uuid.uuid4().hex[:8]}"
        
        # 创建实例
        instance = ConnectorInstanceInfo(
            instance_id=instance_id,
            type_id=type_id,
            display_name=display_name,
            config=config,
            state=ConnectorState.CONFIGURED.value,
            auto_start=auto_start,
            enabled=auto_start
        )
        
        # 保存到配置
        success = self.config_manager.create_instance(instance)
        if not success:
            logger.error(f"保存连接器实例失败: {instance_id}")
            return None
        
        # 初始化运行时状态
        self._runtime_states[instance_id] = ConnectorState.CONFIGURED
        
        # 如果设置为自动启动，则启动
        if auto_start:
            await self.start_instance(instance_id)
        
        logger.info(f"连接器实例创建成功: {instance_id}")
        return instance_id
    
    async def start_instance(self, instance_id: str) -> bool:
        """启动连接器实例"""
        logger.info(f"启动连接器实例: {instance_id}")
        
        # 获取实例信息
        instance = self.config_manager.get_instance(instance_id)
        if not instance:
            logger.error(f"连接器实例不存在: {instance_id}")
            return False
        
        # 检查当前状态
        current_state = self._runtime_states.get(instance_id, ConnectorState.CONFIGURED)
        if current_state == ConnectorState.RUNNING:
            logger.warning(f"连接器实例已在运行: {instance_id}")
            return True
        
        if current_state not in [ConnectorState.CONFIGURED, ConnectorState.ENABLED]:
            logger.error(f"连接器实例状态不允许启动: {current_state}")
            return False
        
        # 获取连接器类型信息
        connector_type = self.config_manager.get_connector_type(instance.type_id)
        if not connector_type:
            logger.error(f"连接器类型不存在: {instance.type_id}")
            return False
        
        try:
            # 检查进程锁，防止重复启动
            if not self.process_manager.acquire_lock(instance.type_id, instance_id):
                logger.error(f"连接器实例已在运行或锁定: {instance_id}")
                return False
            
            # 转换为启用状态
            await self._transition_state(instance_id, ConnectorState.ENABLED)
            
            # 准备启动命令
            cmd, cwd, env = self._prepare_start_command(instance, connector_type)
            if not cmd:
                self.process_manager.release_lock(instance.type_id, instance_id)
                return False
            
            logger.info(f"启动命令: {' '.join(cmd)}")
            
            # 启动进程
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=cwd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # 记录进程
            self._running_processes[instance_id] = process
            
            # 更新实例信息
            self.config_manager.update_instance(
                instance_id,
                process_id=process.pid,
                last_heartbeat=datetime.now()
            )
            
            # 启动进程监控
            monitor_task = asyncio.create_task(self._monitor_process(instance_id, process))
            self._process_monitors[instance_id] = monitor_task
            
            # 转换为运行状态
            await self._transition_state(instance_id, ConnectorState.RUNNING)
            
            logger.info(f"连接器实例启动成功: {instance_id}, PID: {process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"启动连接器实例失败: {e}")
            self.process_manager.release_lock(instance.type_id, instance_id)
            await self._transition_state(instance_id, ConnectorState.ERROR)
            return False
    
    def _prepare_start_command(self, instance: ConnectorInstanceInfo, connector_type: ConnectorTypeInfo):
        """准备启动命令"""
        connectors_dir = self.config_manager.connectors_dir
        connector_dir = connectors_dir / "official" / instance.type_id
        
        # 开发模式启动命令（基于现有架构）
        cmd = [
            "poetry", "run", "python", 
            f"official/{instance.type_id}/{connector_type.entry_point}"
        ]
        cwd = str(connectors_dir)
        
        # 环境变量
        import os
        env = os.environ.copy()
        env.update({
            "LINCH_MIND_CONNECTOR_ID": instance.instance_id,
            "LINCH_MIND_DAEMON_URL": "http://localhost:58471",
            "LINCH_MIND_DEV_MODE": "true",
            "LINCH_MIND_CONNECTOR_CONFIG": self._serialize_config(instance.config)
        })
        
        return cmd, cwd, env
    
    def _serialize_config(self, config: Dict[str, Any]) -> str:
        """序列化配置为JSON字符串"""
        import json
        return json.dumps(config)
    
    async def _monitor_process(self, instance_id: str, process: subprocess.Popen):
        """监控进程"""
        try:
            return_code = await process.wait()
            logger.info(f"连接器进程退出: {instance_id}, 返回码: {return_code}")
            await self._handle_process_exit(instance_id, return_code)
        except Exception as e:
            logger.error(f"监控进程时出错: {e}")
    
    async def stop_instance(self, instance_id: str, force: bool = False) -> bool:
        """停止连接器实例"""
        logger.info(f"停止连接器实例: {instance_id}")
        
        # 获取进程
        process = self._running_processes.get(instance_id)
        if not process:
            logger.warning(f"连接器实例未运行: {instance_id}")
            return True
        
        try:
            # 转换为停止中状态
            await self._transition_state(instance_id, ConnectorState.STOPPING)
            
            # 优雅停止
            if not force:
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=10.0)
                except asyncio.TimeoutError:
                    logger.warning(f"连接器 {instance_id} 未在超时时间内停止，强制终止")
                    force = True
            
            # 强制停止
            if force:
                process.kill()
                await process.wait()
            
            # 清理状态
            self._cleanup_runtime_state(instance_id)
            
            # 更新实例信息
            self.config_manager.update_instance(
                instance_id,
                process_id=None,
                last_heartbeat=None
            )
            
            # 转换为启用状态
            await self._transition_state(instance_id, ConnectorState.ENABLED)
            
            logger.info(f"连接器实例停止成功: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"停止连接器实例失败: {e}")
            await self._transition_state(instance_id, ConnectorState.ERROR)
            return False
    
    async def restart_instance(self, instance_id: str) -> bool:
        """重启连接器实例"""
        logger.info(f"重启连接器实例: {instance_id}")
        
        # 先停止
        await self.stop_instance(instance_id)
        
        # 等待一秒
        await asyncio.sleep(1)
        
        # 再启动
        return await self.start_instance(instance_id)
    
    def get_instance_state(self, instance_id: str) -> ConnectorState:
        """获取连接器实例状态"""
        return self._runtime_states.get(instance_id, ConnectorState.CONFIGURED)
    
    def list_running_instances(self) -> List[str]:
        """列出所有运行中的连接器实例"""
        return [
            instance_id for instance_id, state in self._runtime_states.items()
            if state == ConnectorState.RUNNING
        ]
    
    async def shutdown_all(self):
        """关闭所有连接器实例"""
        logger.info("关闭所有连接器实例")
        
        shutdown_tasks = []
        for instance_id in list(self._running_processes.keys()):
            task = asyncio.create_task(self.stop_instance(instance_id))
            shutdown_tasks.append(task)
        
        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        # 取消监控任务
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
        
        logger.info("所有连接器实例已关闭")
    
    # === 连接器类型管理 ===
    
    async def get_connector_type(self, type_id: str):
        """获取连接器类型信息"""
        return self.config_manager.get_connector_type(type_id)
    
    async def register_connector_type(self, connector_type):
        """注册连接器类型"""
        return self.config_manager.register_connector_type(connector_type)
    
    async def unregister_connector_type(self, type_id: str):
        """注销连接器类型"""
        return self.config_manager.unregister_connector_type(type_id)
    
    async def is_connector_running(self, connector_id: str) -> bool:
        """检查连接器是否正在运行"""
        return connector_id in self._running_processes
    
    # Session V60: 移除临时兼容接口，统一使用 instance-based API
    # 所有外部调用应使用: start_instance(), stop_instance(), get_instance_state()


# 全局单例实例
_lifecycle_manager = None

def get_lifecycle_manager() -> ConnectorLifecycleManager:
    """获取生命周期管理器实例"""
    global _lifecycle_manager
    if _lifecycle_manager is None:
        _lifecycle_manager = ConnectorLifecycleManager()
    return _lifecycle_manager