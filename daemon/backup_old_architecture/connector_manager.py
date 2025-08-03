import asyncio
import json
import subprocess
import platform
import psutil
import threading
from pathlib import Path
from typing import Dict, Optional, List, Any, Set
from datetime import datetime
from models.api_models import ConnectorStatus, ConnectorInfo
import logging

logger = logging.getLogger(__name__)


class ConnectorManager:
    """连接器管理器 - 支持开发/生产模式的新架构"""
    
    def __init__(self, project_root: Optional[Path] = None):
        """初始化连接器管理器"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.connectors_dir = self.project_root / "connectors"
        self.registry_path = self.connectors_dir / "registry.json"
        self.schema_path = self.connectors_dir / "connector.schema.json"
        
        # 进程管理的核心数据结构
        self.running_processes: Dict[str, subprocess.Popen] = {}
        self.process_pids: Dict[str, int] = {}  # 新增：跟踪进程PID
        self.process_start_times: Dict[str, datetime] = {}  # 新增：跟踪进程启动时间
        self.connector_configs: Dict[str, dict] = {}
        self.development_mode = self._detect_development_mode()
        
        # 线程安全保护
        self._process_lock = threading.Lock()  # 新增：保护进程状态的锁
        
        # 健康检查和重启管理
        self.restart_counts: Dict[str, int] = {}
        self.last_restart_times: Dict[str, datetime] = {}
        self.auto_restart_enabled: Dict[str, bool] = {}
        self.max_restart_attempts = 3  # 最大重启次数
        self.restart_cooldown = 60  # 重启冷却时间（秒）
        self.restart_interval = 5   # 重启间隔（秒）
        self.health_check_interval = 10  # 健康检查间隔（秒）- 从30秒优化到10秒
        
        logger.info(f"连接器管理器初始化 - 模式: {'开发' if self.development_mode else '生产'}")
        
        # 加载连接器配置
        self._load_connectors()
        
        # 启动健康检查任务
        asyncio.create_task(self._start_health_monitor())
    
    def _detect_development_mode(self) -> bool:
        """检测是否为开发模式"""
        # 检查是否存在开发环境的标志
        dev_indicators = [
            self.project_root / ".git",  # Git仓库
            self.project_root / "pyproject.toml",  # Poetry项目
            self.project_root / "scripts/connector-dev.py",  # 开发工具
        ]
        
        for indicator in dev_indicators:
            if indicator.exists():
                return True
        
        # 检查环境变量
        import os
        return os.getenv("LINCH_MIND_DEV_MODE", "false").lower() == "true"
    
    def _get_platform(self) -> str:
        """获取当前平台标识"""
        system = platform.system().lower()
        if system == "windows":
            return "windows"
        elif system == "darwin":
            return "macos"
        else:
            return "linux"
    
    def _load_connectors(self):
        """加载所有连接器配置"""
        self.connector_configs = {}
        
        # 扫描官方连接器
        official_dir = self.connectors_dir / "official"
        if official_dir.exists():
            self._scan_connector_directory(official_dir)
        
        # 扫描社区连接器
        community_dir = self.connectors_dir / "community"
        if community_dir.exists():
            self._scan_connector_directory(community_dir)
        
        logger.info(f"已加载 {len(self.connector_configs)} 个连接器")
    
    def _scan_connector_directory(self, base_dir: Path):
        """扫描连接器目录"""
        for connector_dir in base_dir.iterdir():
            if not connector_dir.is_dir():
                continue
            
            connector_json_path = connector_dir / "connector.json"
            if not connector_json_path.exists():
                continue
            
            try:
                with open(connector_json_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                # 验证基本字段
                if not self._validate_connector_config(config):
                    logger.warning(f"连接器配置无效: {connector_dir.name}")
                    continue
                
                # 添加运行时信息
                config["_runtime"] = {
                    "base_dir": str(base_dir),
                    "connector_dir": str(connector_dir),
                    "config_path": str(connector_json_path)
                }
                
                self.connector_configs[config["id"]] = config
                logger.debug(f"已加载连接器: {config['id']} v{config['version']}")
                
            except Exception as e:
                logger.error(f"加载连接器配置失败 {connector_dir.name}: {e}")
    
    def _validate_connector_config(self, config: dict) -> bool:
        """验证连接器配置"""
        required_fields = ["id", "name", "version", "author", "description", "entry", "permissions"]
        
        for field in required_fields:
            if field not in config:
                logger.error(f"连接器配置缺少必需字段: {field}")
                return False
        
        # 验证entry结构
        entry = config.get("entry", {})
        if "development" not in entry or "production" not in entry:
            logger.error("连接器配置缺少entry.development或entry.production")
            return False
        
        return True
    
    async def _preflight_check(self, connector_id: str, connector_config: dict) -> bool:
        """连接器启动前置检查"""
        logger.info(f"🔍 执行连接器 {connector_id} 预检查...")
        
        try:
            # 1. 检查入口文件是否存在
            entry = connector_config["entry"]
            runtime = connector_config["_runtime"]
            connector_dir = Path(runtime["connector_dir"])
            
            if self.development_mode:
                dev_entry = entry["development"]
                args = dev_entry["args"]
                main_file = connector_dir / args[0] if args else connector_dir / "main.py"
                
                if not main_file.exists():
                    logger.error(f"❌ 连接器入口文件不存在: {main_file}")
                    return False
                logger.info(f"✅ 入口文件检查通过: {main_file}")
            
            # 2. 检查Python环境和依赖
            if self.development_mode:
                try:
                    # 测试poetry环境是否可用
                    result = await asyncio.create_subprocess_exec(
                        "poetry", "run", "python", "-c", "import sys; print('Python OK')",
                        cwd=self.connectors_dir,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await result.communicate()
                    
                    if result.returncode != 0:
                        logger.error(f"❌ Poetry环境检查失败: {stderr.decode()}")
                        return False
                    logger.info("✅ Poetry环境检查通过")
                    
                    # 简化的依赖检查：只检查基础的Poetry环境，信任pyproject.toml中的依赖声明
                    logger.info("✅ 跳过详细依赖检查，信任pyproject.toml依赖声明")
                    
                except Exception as e:
                    logger.error(f"❌ 环境检查过程中出错: {e}")
                    return False
            
            # 3. 简化权限检查：clipboard连接器会在启动时自行检查权限
            if connector_id == "clipboard":
                logger.info("✅ 剪贴板权限检查交由连接器自行处理")
            
            logger.info(f"🎉 连接器 {connector_id} 预检查全部通过")
            return True
            
        except Exception as e:
            logger.error(f"❌ 预检查过程中发生未知错误: {e}")
            return False
    
    async def start_connector(self, connector_id: str, config: dict = None) -> bool:
        """启动连接器进程"""
        logger.info(f"启动连接器: {connector_id}")
        
        if connector_id in self.running_processes:
            logger.warning(f"连接器 {connector_id} 已在运行")
            return True
        
        connector_config = self.connector_configs.get(connector_id)
        if not connector_config:
            logger.error(f"未知连接器: {connector_id}")
            return False
        
        # 执行启动前置检查
        preflight_result = await self._preflight_check(connector_id, connector_config)
        if not preflight_result:
            logger.error(f"连接器 {connector_id} 预检查失败，取消启动")
            return False
        
        try:
            # 准备启动命令
            cmd, cwd = self._prepare_start_command(connector_config)
            if not cmd:
                return False
            
            # 准备环境变量
            env = self._prepare_environment(connector_id, config)
            
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
            logger.info(f"连接器 {connector_id} 启动成功，PID: {process.pid}")
            
            # 记录进程信息（线程安全）
            with self._process_lock:
                self.process_pids[connector_id] = process.pid
                self.process_start_times[connector_id] = datetime.now()
            
            # 启动进程监控任务
            asyncio.create_task(self._monitor_process(connector_id, process))
            
            return True
            
        except Exception as e:
            logger.error(f"启动连接器 {connector_id} 失败: {e}")
            return False
    
    def _prepare_start_command(self, connector_config: dict) -> tuple[List[str], Optional[str]]:
        """准备启动命令"""
        connector_id = connector_config["id"]
        entry = connector_config["entry"]
        runtime = connector_config["_runtime"]
        connector_dir = Path(runtime["connector_dir"])
        
        if self.development_mode:
            # 开发模式：使用Poetry运行Python脚本（与dev.sh保持一致）
            dev_entry = entry["development"]
            args = dev_entry["args"]
            working_dir = dev_entry.get("working_dir", ".")
            
            # 检查入口文件是否存在
            main_file = connector_dir / args[0] if args else connector_dir / "main.py"
            if not main_file.exists():
                logger.error(f"连接器入口文件不存在: {main_file}")
                return None, None
            
            # 使用poetry运行，相对路径基于connectors目录
            relative_path = f"official/{connector_id}/{args[0]}"
            cmd = ["poetry", "run", "python", relative_path]
            cwd = self.connectors_dir  # 工作目录是connectors根目录
            
        else:
            # 生产模式：使用编译后的可执行文件
            prod_entry = entry["production"]
            platform_name = self._get_platform()
            
            if platform_name not in prod_entry:
                logger.error(f"连接器 {connector_id} 不支持平台: {platform_name}")
                return None, None
            
            executable_name = prod_entry[platform_name]
            
            # 查找可执行文件（优先级：dist目录 -> 连接器目录）
            possible_paths = [
                self.project_root / "dist" / "connectors" / connector_id / platform_name / executable_name,
                connector_dir / "dist" / executable_name,
                connector_dir / executable_name
            ]
            
            executable_path = None
            for path in possible_paths:
                if path.exists():
                    executable_path = path
                    break
            
            if not executable_path:
                logger.error(f"连接器 {connector_id} 可执行文件不存在: {executable_name}")
                return None, None
            
            cmd = [str(executable_path)]
            cwd = executable_path.parent
        
        return cmd, str(cwd)
    
    def _create_clean_connector_env(self) -> dict:
        """创建干净的环境变量，确保子进程使用connectors的Poetry虚拟环境
        
        核心问题：daemon运行在自己的Poetry虚拟环境中，子进程会继承这个环境上下文。
        解决方案：清理所有Poetry相关环境变量，让子进程在connectors目录下重新激活Poetry环境。
        """
        import os
        
        # 从基础系统环境开始，避免继承daemon的Poetry虚拟环境
        env = {}
        
        # 保留必要的系统环境变量
        essential_vars = [
            'PATH', 'HOME', 'USER', 'SHELL', 'LANG', 'LC_ALL', 'LC_CTYPE',
            'TMPDIR', 'TMP', 'TEMP'  # 临时目录相关
        ]
        
        for var in essential_vars:
            if var in os.environ:
                env[var] = os.environ[var]
        
        # 明确清理Poetry和Python虚拟环境相关变量
        poetry_vars_to_clear = [
            'VIRTUAL_ENV', 'VIRTUAL_ENV_PROMPT', 'POETRY_ACTIVE',
            'POETRY_VENV_PATH', 'POETRY_VENV_IN_PROJECT',
            'PYTHONHOME'  # 这个很重要，清理Python home路径
        ]
        
        # macOS特定环境变量
        if 'DYLD_LIBRARY_PATH' in os.environ:
            env['DYLD_LIBRARY_PATH'] = os.environ['DYLD_LIBRARY_PATH']
        
        # 设置connectors专用的环境变量
        env["PYTHONPATH"] = str(self.connectors_dir)
        env["PWD"] = str(self.connectors_dir)
        
        return env
    
    def _prepare_environment(self, connector_id: str, config: dict = None) -> dict:
        """准备环境变量"""
        # 使用干净的环境作为基础
        env = self._create_clean_connector_env()
        
        # 添加connector专用的环境变量
        env["LINCH_MIND_CONNECTOR_ID"] = connector_id
        env["LINCH_MIND_DAEMON_URL"] = "http://localhost:58471"
        env["LINCH_MIND_DEV_MODE"] = "true" if self.development_mode else "false"
        
        # 配置信息（如果有）
        if config:
            env["LINCH_MIND_CONNECTOR_CONFIG"] = json.dumps(config)
        
        return env
    
    async def stop_connector(self, connector_id: str) -> bool:
        """停止连接器进程 - 改进版，线程安全"""
        logger.info(f"停止连接器: {connector_id}")
        
        with self._process_lock:
            process = self.running_processes.get(connector_id)
            recorded_pid = self.process_pids.get(connector_id)
        
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
            
            # 线程安全地清理状态
            with self._process_lock:
                self._cleanup_dead_process(connector_id)
            
            return True
            
        except Exception as e:
            logger.error(f"停止连接器 {connector_id} 失败: {e}")
            return False
    
    async def restart_connector(self, connector_id: str, config: dict = None) -> bool:
        """重启连接器"""
        logger.info(f"重启连接器: {connector_id}")
        
        # 先停止
        await self.stop_connector(connector_id)
        
        # 等待一秒
        await asyncio.sleep(1)
        
        # 再启动
        return await self.start_connector(connector_id, config)
    
    async def _monitor_process(self, connector_id: str, process: subprocess.Popen):
        """监控进程状态 - 改进版，避免状态不一致问题"""
        original_pid = process.pid
        try:
            return_code = await process.wait()
            logger.warning(f"连接器 {connector_id} 进程退出，PID: {original_pid}, 返回码: {return_code}")
            
            # 收集进程输出用于诊断
            stdout_data = ""
            stderr_data = ""
            try:
                if process.stdout:
                    stdout_bytes = await process.stdout.read()
                    stdout_data = stdout_bytes.decode('utf-8', errors='ignore')
                if process.stderr:
                    stderr_bytes = await process.stderr.read()
                    stderr_data = stderr_bytes.decode('utf-8', errors='ignore')
            except Exception as e:
                logger.warning(f"读取连接器 {connector_id} 输出失败: {e}")
            
            # 详细记录退出信息
            if stdout_data:
                logger.info(f"连接器 {connector_id} STDOUT:\n{stdout_data[-1000:]}")  # 最后1000字符
            if stderr_data:
                logger.error(f"连接器 {connector_id} STDERR:\n{stderr_data[-1000:]}")  # 最后1000字符
            
            # 线程安全地处理进程状态清理
            with self._process_lock:
                # 关键修复：只有当前监控的进程PID与记录的PID一致时才清理
                current_recorded_pid = self.process_pids.get(connector_id)
                if current_recorded_pid == original_pid:
                    # 这是我们记录的当前进程，可以安全清理
                    if connector_id in self.running_processes:
                        del self.running_processes[connector_id]
                    if connector_id in self.process_pids:
                        del self.process_pids[connector_id]
                    if connector_id in self.process_start_times:
                        del self.process_start_times[connector_id]
                    logger.info(f"已清理连接器 {connector_id} 的进程记录 (PID: {original_pid})")
                else:
                    # 这不是当前活跃的进程，可能是旧的监控任务
                    logger.info(f"跳过清理连接器 {connector_id}：监控的PID {original_pid} != 当前PID {current_recorded_pid}")
                    return  # 不处理重启逻辑
            
            # 记录退出原因并处理重启
            if return_code != 0:
                logger.error(f"连接器 {connector_id} 异常退出，返回码: {return_code}")
                # 如果有错误输出，也记录到错误日志中
                if stderr_data:
                    logger.error(f"连接器 {connector_id} 错误详情: {stderr_data.strip()}")
                await self._handle_connector_failure(connector_id)
            else:
                logger.info(f"连接器 {connector_id} 正常退出")
                # 重置重启计数器（正常退出不计入重启次数）
                self.restart_counts[connector_id] = 0
            
        except Exception as e:
            logger.error(f"监控连接器 {connector_id} 时发生错误: {e}")
    
    async def _handle_connector_failure(self, connector_id: str):
        """处理连接器失败和自动重启"""
        # 检查是否启用自动重启
        if not self.auto_restart_enabled.get(connector_id, True):
            logger.info(f"连接器 {connector_id} 自动重启已禁用")
            return
        
        # 检查重启次数限制
        current_restart_count = self.restart_counts.get(connector_id, 0)
        if current_restart_count >= self.max_restart_attempts:
            logger.error(f"连接器 {connector_id} 已达到最大重启次数 ({self.max_restart_attempts})，停止自动重启")
            return
        
        # 检查重启冷却时间
        last_restart = self.last_restart_times.get(connector_id)
        if last_restart:
            time_since_last = (datetime.now() - last_restart).total_seconds()
            if time_since_last < self.restart_cooldown:
                remaining_cooldown = self.restart_cooldown - time_since_last
                logger.warning(f"连接器 {connector_id} 在冷却期内，还需等待 {remaining_cooldown:.1f} 秒后才能重启")
                return
        
        # 增加重启计数
        self.restart_counts[connector_id] = current_restart_count + 1
        self.last_restart_times[connector_id] = datetime.now()
        
        logger.info(f"准备重启连接器 {connector_id} (第 {self.restart_counts[connector_id]}/{self.max_restart_attempts} 次尝试)")
        
        # 等待重启间隔
        await asyncio.sleep(self.restart_interval)
        
        # 尝试重启
        success = await self.start_connector(connector_id)
        if success:
            logger.info(f"✅ 连接器 {connector_id} 自动重启成功")
        else:
            logger.error(f"❌ 连接器 {connector_id} 自动重启失败")
    
    async def _start_health_monitor(self):
        """启动健康检查监控器"""
        logger.info(f"🏥 启动连接器健康检查监控器 (间隔: {self.health_check_interval}秒)")
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_check()
            except Exception as e:
                logger.error(f"健康检查监控器错误: {e}")
                await asyncio.sleep(self.health_check_interval * 2)  # 出错时等待双倍时间
    
    async def _perform_health_check(self):
        """执行健康检查 - 改进版，减少竞态条件"""
        # 获取当前运行连接器的快照
        with self._process_lock:
            connector_snapshot = dict(self.running_processes)
            pid_snapshot = dict(self.process_pids)
        
        for connector_id, process in connector_snapshot.items():
            if process is None:
                continue
                
            recorded_pid = pid_snapshot.get(connector_id)
            if not recorded_pid:
                continue
            
            try:
                # 使用psutil进行更可靠的进程检查
                try:
                    psutil_process = psutil.Process(recorded_pid)
                    if not psutil_process.is_running():
                        logger.warning(f"🔍 健康检查发现连接器 {connector_id} PID {recorded_pid} 已退出")
                        with self._process_lock:
                            self._cleanup_dead_process(connector_id)
                        # 触发重启逻辑（假设异常退出）
                        await self._handle_connector_failure(connector_id)
                    else:
                        # 进程健康运行 - 使用debug级别避免日志爆炸
                        logger.debug(f"🔍 连接器 {connector_id} (PID: {recorded_pid}) 进程健康")
                except psutil.NoSuchProcess:
                    logger.warning(f"🔍 健康检查发现连接器 {connector_id} PID {recorded_pid} 不存在")
                    with self._process_lock:
                        self._cleanup_dead_process(connector_id)
                    await self._handle_connector_failure(connector_id)
                
            except Exception as e:
                logger.error(f"检查连接器 {connector_id} 健康状态时出错: {e}")
    
    def enable_auto_restart(self, connector_id: str, enabled: bool = True):
        """启用/禁用连接器自动重启"""
        self.auto_restart_enabled[connector_id] = enabled
        logger.info(f"连接器 {connector_id} 自动重启 {'启用' if enabled else '禁用'}")
    
    def reset_restart_count(self, connector_id: str):
        """重置连接器重启计数"""
        self.restart_counts[connector_id] = 0
        self.last_restart_times.pop(connector_id, None)
        logger.info(f"已重置连接器 {connector_id} 的重启计数")
    
    def get_restart_stats(self, connector_id: str) -> Dict[str, Any]:
        """获取连接器重启统计信息"""
        return {
            "restart_count": self.restart_counts.get(connector_id, 0),
            "max_restart_attempts": self.max_restart_attempts,
            "auto_restart_enabled": self.auto_restart_enabled.get(connector_id, True),
            "last_restart_time": self.last_restart_times.get(connector_id),
            "restart_cooldown": self.restart_cooldown,
            "restart_interval": self.restart_interval
        }
    
    def _cleanup_dead_process(self, connector_id: str):
        """清理死进程的状态信息（必须在锁内调用）"""
        if connector_id in self.running_processes:
            del self.running_processes[connector_id]
        if connector_id in self.process_pids:
            del self.process_pids[connector_id]
        if connector_id in self.process_start_times:
            del self.process_start_times[connector_id]

    def get_connector_status(self, connector_id: str) -> ConnectorStatus:
        """获取连接器状态 - 改进版，支持多层验证"""
        if connector_id not in self.connector_configs:
            return ConnectorStatus.ERROR
        
        with self._process_lock:
            process = self.running_processes.get(connector_id)
            recorded_pid = self.process_pids.get(connector_id)
            
            if not process or not recorded_pid:
                return ConnectorStatus.STOPPED
            
            # 第一层：检查subprocess对象状态
            try:
                if process.returncode is None:
                    # 第二层：通过psutil验证进程实际存在
                    try:
                        psutil_process = psutil.Process(recorded_pid)
                        if psutil_process.is_running():
                            return ConnectorStatus.RUNNING
                        else:
                            logger.warning(f"连接器 {connector_id} PID {recorded_pid} 进程已不存在，清理状态")
                            self._cleanup_dead_process(connector_id)
                            return ConnectorStatus.STOPPED
                    except psutil.NoSuchProcess:
                        logger.warning(f"连接器 {connector_id} PID {recorded_pid} 不存在，清理状态")
                        self._cleanup_dead_process(connector_id)
                        return ConnectorStatus.STOPPED
                    except Exception as e:
                        logger.error(f"psutil检查进程 {connector_id} 时出错: {e}")
                        return ConnectorStatus.ERROR
                else:
                    # 进程已退出，清理状态
                    logger.info(f"连接器 {connector_id} 进程已退出，清理状态")
                    self._cleanup_dead_process(connector_id)
                    return ConnectorStatus.STOPPED
            except Exception as e:
                logger.error(f"检查连接器 {connector_id} 状态时出错: {e}")
                return ConnectorStatus.ERROR
    
    def get_connector_info(self, connector_id: str) -> Optional[ConnectorInfo]:
        """获取连接器详细信息"""
        connector_config = self.connector_configs.get(connector_id)
        if not connector_config:
            return None
        
        status = self.get_connector_status(connector_id)
        
        # 获取进程信息
        process = self.running_processes.get(connector_id)
        data_count = 0
        if process and status == ConnectorStatus.RUNNING:
            # TODO: 实现真实的数据计数
            data_count = 1  # 占位符
        
        return ConnectorInfo(
            id=connector_id,
            name=connector_config["name"],
            description=connector_config["description"],
            status=status,
            data_count=data_count,
            last_update=datetime.now(),
            config=connector_config.get("config_schema", {})
        )
    
    def list_available_connectors(self) -> List[dict]:
        """列出所有可用连接器（包括未运行的）"""
        connectors = []
        for connector_id, config in self.connector_configs.items():
            connector_info = {
                "id": connector_id,
                "name": config["name"],
                "version": config["version"],
                "description": config["description"],
                "author": config["author"],
                "category": config.get("category", "unknown"),
                "status": self.get_connector_status(connector_id).value,
                "capabilities": config.get("capabilities", {}),
                "permissions": config.get("permissions", [])
            }
            connectors.append(connector_info)
        return connectors
    
    def list_running_connectors(self) -> List[ConnectorInfo]:
        """列出所有运行中的连接器 - 改进版，实时状态验证"""
        connectors = []
        # 先获取所有可能运行的连接器ID列表（避免在迭代时修改字典）
        with self._process_lock:
            connector_ids = list(self.running_processes.keys())
        
        for connector_id in connector_ids:
            info = self.get_connector_info(connector_id)
            if info and info.status == ConnectorStatus.RUNNING:
                connectors.append(info)
        return connectors
    
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
    
    def reload_connectors(self):
        """重新加载连接器配置"""
        logger.info("重新加载连接器配置")
        old_count = len(self.connector_configs)
        self._load_connectors()
        new_count = len(self.connector_configs)
        logger.info(f"连接器配置重新加载完成: {old_count} -> {new_count}")
    
    def validate_connector_permissions(self, connector_id: str) -> bool:
        """验证连接器权限声明"""
        connector_config = self.connector_configs.get(connector_id)
        if not connector_config:
            return False
        
        permissions = connector_config.get("permissions", [])
        
        # 基础权限验证
        valid_categories = ["filesystem", "network", "system", "process"]
        for permission in permissions:
            if ":" not in permission:
                logger.error(f"权限格式错误: {permission}")
                return False
            
            category, action = permission.split(":", 1)
            if category not in valid_categories:
                logger.error(f"未知权限类别: {category}")
                return False
        
        return True


# 兼容性别名
ConnectorLifecycleManager = ConnectorManager