"""
Process manager for connector processes with lock mechanism.
Prevents duplicate process spawning and manages process lifecycle.
"""

import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

logger = logging.getLogger(__name__)


class ProcessManager:
    """Unified process manager to prevent duplicate process spawning."""

    def __init__(self):
        self.lock_dir = Path.home() / ".linch-mind" / "locks"
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        self.running_processes = {}  # 存储运行中的进程信息
        logger.info(f"ProcessManager initialized with lock directory: {self.lock_dir}")

    def acquire_lock(
        self, connector_id: str, instance_id: Optional[str] = None
    ) -> bool:
        """
        Acquire process lock to prevent duplicate processes.

        Args:
            connector_id: The connector type ID
            instance_id: Optional instance ID for multiple instances

        Returns:
            True if lock acquired, False if process already running
        """
        lock_name = f"{connector_id}_{instance_id}" if instance_id else connector_id
        lock_file = self.lock_dir / f"{lock_name}.lock"

        # Check if lock file exists
        if lock_file.exists():
            try:
                pid = int(lock_file.read_text())
                if self._is_process_running(pid):
                    logger.warning(
                        f"Process already running for {lock_name} (PID: {pid})"
                    )
                    return False
                # Process is dead, clean up lock file
                logger.info(f"Cleaning up stale lock for {lock_name} (PID: {pid})")
                lock_file.unlink()
            except (ValueError, OSError) as e:
                logger.error(f"Error reading lock file for {lock_name}: {e}")
                lock_file.unlink()

        # Create new lock
        current_pid = os.getpid()
        lock_file.write_text(str(current_pid))
        logger.info(f"Lock acquired for {lock_name} (PID: {current_pid})")
        return True

    def release_lock(self, connector_id: str, instance_id: Optional[str] = None):
        """Release process lock."""
        lock_name = f"{connector_id}_{instance_id}" if instance_id else connector_id
        lock_file = self.lock_dir / f"{lock_name}.lock"

        if lock_file.exists():
            try:
                lock_file.unlink()
                logger.info(f"Lock released for {lock_name}")
            except OSError as e:
                logger.error(f"Error releasing lock for {lock_name}: {e}")

    def is_locked(self, connector_id: str, instance_id: Optional[str] = None) -> bool:
        """Check if a connector is locked (running)."""
        lock_name = f"{connector_id}_{instance_id}" if instance_id else connector_id
        lock_file = self.lock_dir / f"{lock_name}.lock"

        if not lock_file.exists():
            return False

        try:
            pid = int(lock_file.read_text())
            return self._is_process_running(pid)
        except (ValueError, OSError):
            return False

    def get_running_pid(
        self, connector_id: str, instance_id: Optional[str] = None
    ) -> Optional[int]:
        """Get PID of running connector process."""
        lock_name = f"{connector_id}_{instance_id}" if instance_id else connector_id
        lock_file = self.lock_dir / f"{lock_name}.lock"

        if not lock_file.exists():
            return None

        try:
            pid = int(lock_file.read_text())
            if self._is_process_running(pid):
                return pid
        except (ValueError, OSError):
            pass

        return None

    def cleanup_zombies(self):
        """Clean up all zombie processes and stale locks."""
        cleaned_count = 0

        for lock_file in self.lock_dir.glob("*.lock"):
            try:
                pid = int(lock_file.read_text())
                if not self._is_process_running(pid):
                    lock_file.unlink()
                    logger.info(f"Cleaned up stale lock: {lock_file.name} (PID: {pid})")
                    cleaned_count += 1
            except (ValueError, OSError) as e:
                logger.error(f"Error cleaning up lock {lock_file.name}: {e}")
                try:
                    lock_file.unlink()
                    cleaned_count += 1
                except OSError:
                    pass

        logger.info(f"Cleaned up {cleaned_count} stale locks")
        return cleaned_count

    def _is_process_running(self, pid: int) -> bool:
        """Check if a process with given PID is running."""
        try:
            process = psutil.Process(pid)
            # Check if process is running (support both Python and C++ connectors)
            if not process.is_running():
                return False

            process_name = process.name().lower()
            # Support both Python and C++ connectors
            return (
                "python" in process_name
                or "linch-mind" in process_name
                or process_name.endswith((".exe", ".out"))
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    def kill_process(
        self, connector_id: str, instance_id: Optional[str] = None
    ) -> bool:
        """
        Kill a running connector process.

        Returns:
            True if process was killed, False if not found
        """
        pid = self.get_running_pid(connector_id, instance_id)
        if not pid:
            return False

        try:
            process = psutil.Process(pid)
            process.terminate()
            logger.info(f"Terminated process for {connector_id} (PID: {pid})")

            # Wait for process to terminate
            try:
                process.wait(timeout=5)
            except psutil.TimeoutExpired:
                # Force kill if not terminated
                process.kill()
                logger.warning(f"Force killed process for {connector_id} (PID: {pid})")

            # Release lock
            self.release_lock(connector_id, instance_id)
            return True

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Error killing process for {connector_id}: {e}")
            # Clean up lock anyway
            self.release_lock(connector_id, instance_id)
            return False

    def list_running_connectors(self) -> list[dict]:
        """List all running connector processes."""
        running = []

        for lock_file in self.lock_dir.glob("*.lock"):
            try:
                pid = int(lock_file.read_text())
                if self._is_process_running(pid):
                    # Parse connector info from lock filename
                    lock_name = lock_file.stem
                    parts = lock_name.split("_", 1)
                    connector_id = parts[0]
                    instance_id = parts[1] if len(parts) > 1 else None

                    # Get process info
                    process = psutil.Process(pid)

                    running.append(
                        {
                            "connector_id": connector_id,
                            "instance_id": instance_id,
                            "pid": pid,
                            "create_time": process.create_time(),
                            "memory_info": process.memory_info()._asdict(),
                            "cpu_percent": process.cpu_percent(interval=0.1),
                        }
                    )
            except (ValueError, OSError, psutil.Error) as e:
                logger.error(f"Error checking lock {lock_file.name}: {e}")

        return running

    async def start_process(
        self,
        connector_id: str,
        command: List[str],
        working_dir: Optional[str] = None,
        env_vars: Optional[Dict[str, str]] = None,
        capture_output: bool = True,
        startup_timeout: int = 30,
    ) -> Optional[subprocess.Popen]:
        """
        启动连接器进程 - 原子级单例保护机制

        Args:
            connector_id: 连接器ID
            command: 启动命令
            working_dir: 工作目录
            env_vars: 环境变量
            capture_output: 是否捕获输出

        Returns:
            启动的进程对象，失败返回None
        """
        
        # 🚀 修复关键问题：将imports移到方法开始处，避免异步执行时的导入问题
        import fcntl
        import asyncio
        
        # 1. 首先执行基础检查 - 在获取锁之前快速失败
        if not command or not command[0]:
            logger.error(f"❌ 启动命令为空: {connector_id}")
            return None
        
        # 验证可执行文件存在
        from pathlib import Path
        if not Path(command[0]).exists():
            logger.error(f"❌ 可执行文件不存在: {command[0]}")
            return None
        
        # 创建启动锁文件（不同于运行状态锁文件）
        startup_lock_file = self.lock_dir / f"{connector_id}.startup.lock"
        startup_fd = None
        
        try:
            # 1. 获取启动锁（原子操作） - 添加详细日志
            logger.info(f"🔄 尝试获取启动锁: {connector_id} -> {startup_lock_file}")
            startup_fd = open(startup_lock_file, 'w')
            try:
                # 非阻塞获取独占锁，如果失败立即返回
                fcntl.flock(startup_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                logger.info(f"✅ 获得启动锁: {connector_id}")
            except (IOError, OSError) as e:
                logger.warning(f"⚠️  启动锁竞争失败，另一个进程正在启动 {connector_id}: {e}")
                startup_fd.close()
                return None
            
            # 2. 在启动锁保护下，再次检查运行状态（双重检查模式）
            existing_pid = self.get_running_pid(connector_id)
            if existing_pid:
                # 双重检查：锁文件存在，再确认进程是否真的在运行
                if self._is_process_running(existing_pid):
                    logger.warning(
                        f"🔒 连接器 {connector_id} 已经在运行 (PID: {existing_pid})，跳过启动"
                    )
                    # 如果内存中没有记录，同步状态
                    if connector_id not in self.running_processes:
                        try:
                            process = psutil.Process(existing_pid).as_dict()
                            self.running_processes[connector_id] = {
                                "pid": existing_pid,
                                "process": None,  # 无法恢复subprocess对象
                                "command": command,
                                "working_dir": working_dir,
                                "start_time": datetime.now().isoformat(),
                            }
                            logger.info(
                                f"🔄 同步已存在进程到内存: {connector_id} (PID: {existing_pid})"
                            )
                        except Exception as e:
                            logger.debug(f"同步进程状态失败: {e}")
                    return None  # 已在运行
                else:
                    # 锁文件存在但进程已死，清理陈旧的锁文件
                    logger.warning(f"🧹 发现陈旧的锁文件: {connector_id} (PID: {existing_pid})，正在清理...")
                    lock_file = self.lock_dir / f"{connector_id}.lock"
                    if lock_file.exists():
                        lock_file.unlink()
                        logger.info(f"✅ 已清理陈旧的锁文件: {connector_id}")

            # 3. 清理可能存在的陈旧状态
            self._cleanup_stale_state(connector_id)

            # 4. 设置环境变量
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)

            # 5. 启动进程 - 使用 /dev/null 避免 PIPE 缓冲区阻塞
            if capture_output:
                # 使用 /dev/null 重定向而不是 PIPE，避免缓冲区满导致进程阻塞
                devnull = open(os.devnull, 'w')
                process = subprocess.Popen(
                    command,
                    cwd=working_dir,
                    env=env,
                    stdout=devnull,
                    stderr=devnull,
                    start_new_session=True,  # 创建新的进程组
                )
                # 将 devnull 对象存储，以便后续关闭
                process._devnull = devnull
            else:
                process = subprocess.Popen(
                    command,
                    cwd=working_dir,
                    env=env,
                    stdout=None,
                    stderr=None,
                    start_new_session=True,  # 创建新的进程组
                )

            # 6. 验证进程启动成功（等待短暂时间确保进程真的启动了）
            await asyncio.sleep(0.2)  # 等待200ms确保进程稳定
            
            try:
                # 检查进程是否还在运行
                psutil_process = psutil.Process(process.pid)
                if not psutil_process.is_running():
                    logger.error(f"❌ 进程启动后立即退出: {connector_id}")
                    return None
            except psutil.NoSuchProcess:
                logger.error(f"❌ 进程启动失败或立即退出: {connector_id}")
                return None

            # 7. 统一状态管理：同时更新内存和锁文件（原子操作）
            self.running_processes[connector_id] = {
                "pid": process.pid,
                "process": process,
                "command": command,
                "working_dir": working_dir,
                "start_time": datetime.now().isoformat(),
                "startup_protected": True,  # 标记为启动保护状态
            }

            # 创建运行状态锁文件 - 添加错误处理
            lock_file = self.lock_dir / f"{connector_id}.lock"
            try:
                lock_file.write_text(str(process.pid))
                logger.info(f"📝 创建运行状态锁文件: {lock_file} -> PID {process.pid}")
            except Exception as lock_error:
                logger.error(f"❌ 创建锁文件失败 {connector_id}: {lock_error}")
                # 锁文件创建失败是严重问题，需要终止进程
                try:
                    process.terminate()
                    logger.warning(f"🛑 因锁文件创建失败，已终止进程: {connector_id}")
                except Exception:
                    pass
                return None

            logger.info(f"✅ 连接器进程启动成功: {connector_id} (PID: {process.pid})")
            return process

        except Exception as e:
            logger.error(f"❌ 启动连接器进程失败 {connector_id}: {e}")
            # 出错时清理状态
            self._cleanup_stale_state(connector_id)
            return None
            
        finally:
            # 8. 清理启动锁（确保始终释放）
            if startup_fd:
                try:
                    fcntl.flock(startup_fd.fileno(), fcntl.LOCK_UN)
                    startup_fd.close()
                    # 删除启动锁文件
                    if startup_lock_file.exists():
                        startup_lock_file.unlink()
                    logger.debug(f"🔓 释放启动锁: {connector_id}")
                except Exception as e:
                    logger.warning(f"释放启动锁失败: {e}")

    async def stop_process(self, connector_id: str, timeout: int = 10) -> bool:
        """
        停止连接器进程

        Args:
            connector_id: 连接器ID
            timeout: 等待进程退出的超时时间（秒）

        Returns:
            是否成功停止
        """
        try:
            if connector_id not in self.running_processes:
                # 尝试从锁文件中获取PID信息
                pid = self.get_running_pid(connector_id)
                if pid:
                    logger.info(
                        f"从锁文件发现连接器 {connector_id} 进程 (PID: {pid}), 尝试停止"
                    )
                    return self.kill_process(connector_id)
                logger.info(f"连接器 {connector_id} 没有运行中的进程，跳过停止操作")
                return True  # 进程不存在视为停止成功

            process_info = self.running_processes[connector_id]
            pid = process_info.get("pid")
            process_info.get("process")

            if not pid:
                logger.warning(f"连接器 {connector_id} 没有有效的PID")
                return False

            try:
                psutil_process = psutil.Process(pid)

                # 优雅退出
                psutil_process.terminate()
                logger.info(f"发送终止信号给连接器 {connector_id} (PID: {pid})")

                # 等待进程退出
                try:
                    psutil_process.wait(timeout=timeout)
                    logger.info(f"连接器进程优雅退出: {connector_id}")
                except psutil.TimeoutExpired:
                    # 强制杀死
                    psutil_process.kill()
                    logger.warning(f"强制杀死连接器进程: {connector_id} (PID: {pid})")

                # 统一清理状态：内存和锁文件
                self._cleanup_stale_state(connector_id)
                return True

            except psutil.NoSuchProcess:
                logger.info(f"连接器进程已不存在: {connector_id} (PID: {pid})")
                self._cleanup_stale_state(connector_id)
                return True

        except Exception as e:
            logger.error(f"停止连接器进程失败 {connector_id}: {e}")
            # 即使出现异常，也尝试清理进程记录
            self.cleanup_process(connector_id)
            return False

    def get_process_status(self, connector_id: str) -> Dict[str, Any]:
        """
        获取连接器进程状态

        Args:
            connector_id: 连接器ID

        Returns:
            进程状态信息
        """
        try:
            # 先检查运行中的进程记录
            if connector_id not in self.running_processes:
                # 检查是否有锁文件存在
                pid = self.get_running_pid(connector_id)
                if pid:
                    # 发现进程但未在记录中，同步状态
                    logger.warning(
                        f"发现进程状态不同步，连接器 {connector_id} PID {pid} 存在但未在记录中"
                    )
                    try:
                        psutil_process = psutil.Process(pid)
                        if psutil_process.is_running():
                            return {
                                "connector_id": connector_id,
                                "status": "running",
                                "pid": pid,
                                "cpu_percent": psutil_process.cpu_percent(),
                                "memory_percent": psutil_process.memory_percent(),
                                "memory_info": psutil_process.memory_info()._asdict(),
                                "create_time": psutil_process.create_time(),
                                "note": "process_found_via_lock",
                            }
                    except psutil.NoSuchProcess:
                        # 锁文件存在但进程不存在，清理锁文件
                        self.release_lock(connector_id)
                        logger.info(f"清理无效锁文件: {connector_id}")

                return {
                    "connector_id": connector_id,
                    "status": "not_running",
                    "pid": None,
                }

            process_info = self.running_processes[connector_id]
            pid = process_info.get("pid")

            if not pid:
                return {"connector_id": connector_id, "status": "invalid", "pid": None}

            try:
                psutil_process = psutil.Process(pid)

                return {
                    "connector_id": connector_id,
                    "status": "running" if psutil_process.is_running() else "stopped",
                    "pid": pid,
                    "cpu_percent": psutil_process.cpu_percent(),
                    "memory_percent": psutil_process.memory_percent(),
                    "memory_info": psutil_process.memory_info()._asdict(),
                    "create_time": psutil_process.create_time(),
                    "start_time": process_info.get("start_time"),
                    "command": process_info.get("command"),
                }

            except psutil.NoSuchProcess:
                # 进程已不存在，统一清理状态
                self._cleanup_stale_state(connector_id)
                return {"connector_id": connector_id, "status": "dead", "pid": pid}

        except Exception as e:
            logger.error(f"获取连接器进程状态失败 {connector_id}: {e}")
            return {"connector_id": connector_id, "status": "error", "error": str(e)}

    def cleanup_process(self, connector_id: str) -> bool:
        """
        清理连接器进程记录

        Args:
            connector_id: 连接器ID

        Returns:
            是否成功清理
        """
        return self._cleanup_stale_state(connector_id)

    def _cleanup_stale_state(self, connector_id: str) -> bool:
        """
        统一清理进程状态 - 内存记录和锁文件

        Args:
            connector_id: 连接器ID

        Returns:
            是否成功清理
        """
        try:
            cleaned = False

            # 清理内存记录
            if connector_id in self.running_processes:
                process_info = self.running_processes[connector_id]
                process = process_info.get("process")
                
                # 关闭 devnull 文件句柄（如果存在）
                if process and hasattr(process, '_devnull'):
                    try:
                        process._devnull.close()
                        logger.debug(f"关闭devnull文件句柄: {connector_id}")
                    except Exception as e:
                        logger.warning(f"关闭devnull文件句柄失败 {connector_id}: {e}")
                
                del self.running_processes[connector_id]
                logger.debug(f"清理内存中的进程记录: {connector_id}")
                cleaned = True

            # 清理锁文件
            lock_file = self.lock_dir / f"{connector_id}.lock"
            if lock_file.exists():
                try:
                    lock_file.unlink()
                    logger.debug(f"清理锁文件: {connector_id}")
                    cleaned = True
                except OSError as e:
                    logger.error(f"删除锁文件失败 {connector_id}: {e}")

            if cleaned:
                logger.info(f"清理连接器状态完成: {connector_id}")

            return True

        except Exception as e:
            logger.error(f"清理连接器状态失败 {connector_id}: {e}")
            return False


# Global instance
_process_manager = None


def get_process_manager() -> ProcessManager:
    """Get or create the global ProcessManager instance."""
    global _process_manager
    if _process_manager is None:
        _process_manager = ProcessManager()
        # Clean up any stale locks on initialization
        _process_manager.cleanup_zombies()
    return _process_manager
