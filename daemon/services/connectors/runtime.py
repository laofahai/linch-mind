import asyncio
import logging
import platform
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime
import subprocess

logger = logging.getLogger(__name__)


class ConnectorRuntime:
    """连接器运行时 - 单一职责：进程生命周期管理"""
    
    def __init__(self, development_mode: bool = False):
        self.development_mode = development_mode
        
        # 进程管理核心数据
        self.running_processes: Dict[str, subprocess.Popen] = {}
        self.process_start_times: Dict[str, datetime] = {}
        
        logger.info(f"ConnectorRuntime初始化 - 模式: {'开发' if development_mode else '生产'}")
    
    async def start_connector(self, connector_id: str, connector_config: dict, runtime_config: dict = None) -> bool:
        """启动连接器进程"""
        logger.info(f"启动连接器: {connector_id}")
        
        if connector_id in self.running_processes:
            logger.warning(f"连接器 {connector_id} 已在运行")
            return True
        
        try:
            cmd, cwd = self._build_start_command(connector_config)
            if not cmd:
                return False
            
            env = self._build_environment(connector_id, runtime_config)
            
            logger.info(f"启动命令: {' '.join(cmd)}")
            logger.debug(f"工作目录: {cwd}")
            
            # 启动进程
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            self.running_processes[connector_id] = process
            self.process_start_times[connector_id] = datetime.now()
            
            logger.info(f"连接器 {connector_id} 启动成功，PID: {process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"启动连接器 {connector_id} 失败: {e}")
            return False
    
    async def stop_connector(self, connector_id: str) -> bool:
        """停止连接器进程"""
        logger.info(f"停止连接器: {connector_id}")
        
        process = self.running_processes.get(connector_id)
        if not process:
            logger.warning(f"连接器 {connector_id} 未在运行")
            return True
        
        try:
            # 优雅关闭
            process.terminate()
            
            # 等待进程结束，最多等待5秒
            try:
                await asyncio.wait_for(process.wait(), timeout=5.0)
                logger.info(f"连接器 {connector_id} 优雅停止")
            except asyncio.TimeoutError:
                # 强制杀死
                process.kill()
                await process.wait()
                logger.warning(f"连接器 {connector_id} 强制停止")
            
            # 清理状态
            self._cleanup_process(connector_id)
            return True
            
        except Exception as e:
            logger.error(f"停止连接器 {connector_id} 失败: {e}")
            return False
    
    async def restart_connector(self, connector_id: str, connector_config: dict, runtime_config: dict = None) -> bool:
        """重启连接器"""
        logger.info(f"重启连接器: {connector_id}")
        
        # 先停止
        await self.stop_connector(connector_id)
        
        # 等待一秒
        await asyncio.sleep(1)
        
        # 再启动
        return await self.start_connector(connector_id, connector_config, runtime_config)
    
    def _build_start_command(self, connector_config: dict) -> tuple[List[str], Optional[str]]:
        """构建启动命令"""
        connector_id = connector_config["id"]
        entry = connector_config["entry"]
        runtime = connector_config["_runtime"]
        connector_dir = Path(runtime["connector_dir"])
        
        if self.development_mode:
            # 开发模式：使用Poetry运行Python脚本
            dev_entry = entry["development"]
            args = dev_entry["args"]
            
            # 检查入口文件
            main_file = connector_dir / args[0] if args else connector_dir / "main.py"
            if not main_file.exists():
                logger.error(f"连接器入口文件不存在: {main_file}")
                return None, None
            
            # 使用相对路径
            relative_path = f"official/{connector_id}/{args[0]}"
            cmd = ["poetry", "run", "python", relative_path]
            cwd = str(Path(runtime["base_dir"]).parent)  # connectors目录
            
        else:
            # 生产模式：使用编译后的可执行文件
            prod_entry = entry["production"]
            platform_name = self._get_platform()
            
            if platform_name not in prod_entry:
                logger.error(f"连接器 {connector_id} 不支持平台: {platform_name}")
                return None, None
            
            executable_name = prod_entry[platform_name]
            executable_path = self._find_executable(connector_dir, executable_name)
            
            if not executable_path:
                logger.error(f"连接器 {connector_id} 可执行文件不存在: {executable_name}")
                return None, None
            
            cmd = [str(executable_path)]
            cwd = str(executable_path.parent)
        
        return cmd, cwd
    
    def _build_environment(self, connector_id: str, runtime_config: dict = None) -> dict:
        """构建环境变量"""
        import os
        import json
        
        # 基础环境变量
        env = {
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", ""),
            "USER": os.environ.get("USER", ""),
            "SHELL": os.environ.get("SHELL", ""),
            "LANG": os.environ.get("LANG", ""),
        }
        
        # 连接器专用环境变量
        env["LINCH_MIND_CONNECTOR_ID"] = connector_id
        env["LINCH_MIND_DAEMON_URL"] = "http://localhost:58471"
        env["LINCH_MIND_DEV_MODE"] = "true" if self.development_mode else "false"
        
        # 运行时配置
        if runtime_config:
            env["LINCH_MIND_CONNECTOR_CONFIG"] = json.dumps(runtime_config)
        
        return env
    
    def _get_platform(self) -> str:
        """获取当前平台标识"""
        system = platform.system().lower()
        if system == "windows":
            return "windows"
        elif system == "darwin":
            return "macos"
        else:
            return "linux"
    
    def _find_executable(self, connector_dir: Path, executable_name: str) -> Optional[Path]:
        """查找可执行文件"""
        possible_paths = [
            connector_dir / "dist" / executable_name,
            connector_dir / executable_name
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def _cleanup_process(self, connector_id: str):
        """清理进程状态"""
        self.running_processes.pop(connector_id, None)
        self.process_start_times.pop(connector_id, None)
    
    def get_running_connectors(self) -> List[str]:
        """获取正在运行的连接器ID列表"""
        return list(self.running_processes.keys())
    
    def is_connector_running(self, connector_id: str) -> bool:
        """检查连接器是否正在运行"""
        process = self.running_processes.get(connector_id)
        if not process:
            return False
        
        # 检查进程是否还在运行
        return process.returncode is None
    
    def get_process_info(self, connector_id: str) -> Optional[dict]:
        """获取进程信息"""
        process = self.running_processes.get(connector_id)
        if not process:
            return None
        
        return {
            "pid": process.pid,
            "start_time": self.process_start_times.get(connector_id),
            "return_code": process.returncode
        }
    
    async def shutdown_all(self):
        """关闭所有连接器"""
        logger.info("关闭所有连接器")
        
        shutdown_tasks = []
        for connector_id in list(self.running_processes.keys()):
            task = asyncio.create_task(self.stop_connector(connector_id))
            shutdown_tasks.append(task)
        
        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        logger.info("所有连接器已关闭")