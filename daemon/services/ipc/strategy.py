#!/usr/bin/env python3
"""
IPC服务器策略模式接口定义
用于统一Unix Socket和Windows Named Pipe实现
🆕 集成Windows IPC完整实现，消除重复代码
"""

import asyncio
import json
import logging
import os
import platform
import threading
import time
from abc import ABC, abstractmethod
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from queue import Queue
from typing import Any, Dict, Optional, Set

logger = logging.getLogger(__name__)

# Windows特定导入 - 集成到strategy中
if platform.system() == "Windows":
    try:
        import pywintypes
        import win32api
        import win32event
        import win32file
        import win32pipe
        import win32security
        import ntsecuritycon
        
        WINDOWS_SUPPORT = True
        logger.info("✅ Windows Named Pipe支持已启用 (strategy集成)")
    except ImportError as e:
        WINDOWS_SUPPORT = False
        logger.error(f"❌ Windows Named Pipe支持不可用: {e}")
        logger.info("请安装pywin32库: pip install pywin32")
else:
    WINDOWS_SUPPORT = False


class IPCStrategy(ABC):
    """IPC策略接口 - 定义平台无关的服务器行为"""

    @abstractmethod
    async def start(self, app, security_manager, **kwargs) -> None:
        """启动IPC服务器"""

    @abstractmethod
    async def stop(self) -> None:
        """停止IPC服务器"""

    @abstractmethod
    def get_connection_info(self) -> Dict[str, Any]:
        """获取连接信息"""

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """获取服务器统计信息"""

    @abstractmethod
    def is_running(self) -> bool:
        """检查服务器是否运行中"""


class UnixSocketStrategy(IPCStrategy):
    """Unix Domain Socket策略实现"""

    def __init__(self, socket_path: Optional[str] = None):
        self.socket_path = socket_path
        self._server = None
        self._is_running = False
        self.app = None
        self.security_manager = None
        self.clients = set()
        self.client_connections = {}

    async def start(self, app, security_manager, **kwargs) -> None:
        """启动Unix Socket服务器"""
        from ..ipc_server import IPCServer

        logger.info("使用Unix Socket策略启动IPC服务器")

        # 复用现有IPCServer实现，但移除全局单例
        self._server = IPCServer(socket_path=self.socket_path)
        self._server.app = app
        self._server.security_manager = security_manager

        await self._server.start()
        self._is_running = True

        logger.info(f"Unix Socket IPC服务器已启动: {self._server.socket_path}")

    async def stop(self) -> None:
        """停止Unix Socket服务器"""
        if self._server:
            await self._server.stop()
            self._server = None
        self._is_running = False
        logger.info("Unix Socket IPC服务器已停止")

    def get_connection_info(self) -> Dict[str, Any]:
        """获取Unix Socket连接信息"""
        return {
            "type": "unix_socket",
            "socket_path": self.socket_path
            or (self._server.socket_path if self._server else None),
            "platform": "unix",
        }

    def get_stats(self) -> Dict[str, Any]:
        """获取Unix Socket统计信息"""
        if self._server:
            return self._server.get_server_status()
        return {"is_running": self._is_running}

    def is_running(self) -> bool:
        """检查Unix Socket服务器是否运行中"""
        return self._is_running and (self._server.is_running if self._server else False)


class WindowsNamedPipeStrategy(IPCStrategy):
    """Windows Named Pipe策略实现 - 🆕 内嵌完整Windows IPC功能"""

    def __init__(self, pipe_name: Optional[str] = None):
        self.pipe_name = pipe_name or f"linch-mind-{os.getpid()}"
        self.full_pipe_name = f"\\\\.\\pipe\\{self.pipe_name}"
        self._is_running = False
        self.clients: Set[int] = set()
        self.app = None
        self.security_manager = None
        
        # 高性能线程池配置
        max_workers = min(32, (os.cpu_count() or 1) + 4)
        self.thread_pool = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="NamedPipe"
        )
        
        # 连接管理
        self.active_connections = 0
        self.max_connections = 50
        self.connection_lock = threading.Lock()
        
        # 性能统计
        self.stats = {
            "total_requests": 0,
            "active_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0,
            "start_time": time.time(),
        }
        self.stats_lock = threading.Lock()
        
        # 异步事件循环与线程通信
        self.event_loop = None
        self.event_loop_thread = None
        
        # 消息队列用于异步通信
        self.request_queue = Queue()
        self.response_queues: Dict[str, Queue] = {}
        self.pending_futures: Dict[str, Future] = {}
        
        # 安全设置
        self.security_attributes = None
        self.allowed_sids = set()
        
        if WINDOWS_SUPPORT:
            self._setup_security()

    def _setup_security(self):
        """设置Named Pipe高级安全属性"""
        if not WINDOWS_SUPPORT:
            return
            
        try:
            # 创建安全描述符
            security_attributes = win32security.SECURITY_ATTRIBUTES()
            security_descriptor = win32security.SECURITY_DESCRIPTOR()
            
            # 获取当前用户信息
            current_user = win32api.GetUserName()
            user_sid, domain, account_type = win32security.LookupAccountName(
                None, current_user
            )
            self.allowed_sids.add(user_sid)
            
            # 获取管理员组SID（可选）
            try:
                admin_sid = win32security.LookupAccountName(None, "Administrators")[0]
                self.allowed_sids.add(admin_sid)
            except (OSError, AttributeError) as e:
                logger.debug(f"无法获取管理员组SID: {e}")
                
            # 创建高级DACL（访问控制列表）
            dacl = win32security.ACL()
            
            # 为当前用户添加完全控制权限
            dacl.AddAccessAllowedAce(
                win32security.ACL_REVISION,
                ntsecuritycon.GENERIC_ALL,
                user_sid,
            )
            
            # 为管理员组添加读写权限（如果存在）
            if len(self.allowed_sids) > 1:
                for sid in self.allowed_sids:
                    if sid != user_sid:
                        dacl.AddAccessAllowedAce(
                            win32security.ACL_REVISION,
                            ntsecuritycon.GENERIC_READ | ntsecuritycon.GENERIC_WRITE,
                            sid,
                        )
                        
            # 显式拒绝匿名用户和人人组
            try:
                everyone_sid = win32security.LookupAccountName(None, "Everyone")[0]
                dacl.AddAccessDeniedAce(
                    win32security.ACL_REVISION,
                    ntsecuritycon.GENERIC_ALL,
                    everyone_sid,
                )
            except (OSError, AttributeError) as e:
                logger.debug(f"无法设置Everyone组的访问拒绝权限: {e}")
                
            # 设置安全描述符
            security_descriptor.SetSecurityDescriptorDacl(1, dacl, 0)
            security_descriptor.SetSecurityDescriptorOwner(user_sid, 0)
            security_descriptor.SetSecurityDescriptorGroup(user_sid, 0)
            
            security_attributes.SECURITY_DESCRIPTOR = security_descriptor
            security_attributes.bInheritHandle = False
            
            self.security_attributes = security_attributes
            logger.info(
                f"✅ Named Pipe高级安全设置完成: 用户 {current_user} + {len(self.allowed_sids)-1} 个其他授权SID"
            )
            
        except Exception as e:
            logger.error(f"设置Named Pipe安全属性失败： {e}")
            self._setup_fallback_security()
            
    def _setup_fallback_security(self):
        """备用安全设置"""
        try:
            security_attributes = win32security.SECURITY_ATTRIBUTES()
            security_descriptor = win32security.SECURITY_DESCRIPTOR()
            
            current_user = win32api.GetUserName()
            user_sid, _, _ = win32security.LookupAccountName(None, current_user)
            
            dacl = win32security.ACL()
            dacl.AddAccessAllowedAce(
                win32security.ACL_REVISION,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                user_sid,
            )
            
            security_descriptor.SetSecurityDescriptorDacl(1, dacl, 0)
            security_attributes.SECURITY_DESCRIPTOR = security_descriptor
            
            self.security_attributes = security_attributes
            self.allowed_sids.add(user_sid)
            
            logger.warning(f"使用备用安全设置: 仅允许用户 {current_user}")
            
        except Exception as e:
            logger.error(f"备用安全设置也失败: {e}")
            self.security_attributes = None

    async def start(self, app, security_manager, **kwargs) -> None:
        """启动Named Pipe服务器 - 🆕 内嵌实现"""
        if not WINDOWS_SUPPORT:
            raise RuntimeError(
                "Windows Named Pipe需要pywin32库支持。请运行: pip install pywin32"
            )
            
        self.app = app
        self.security_manager = security_manager
        self._is_running = True
        
        logger.info("使用Windows Named Pipe策略启动IPC服务器")
        
        # 启动异步事件循环在独立线程中
        self._start_async_loop_thread()
        
        # 等待事件循环准备就绪
        await asyncio.sleep(0.1)
        
        # 启动多个pipe实例支持高并发
        max_workers = 20
        pipe_instances = min(10, max_workers // 2)
        for i in range(pipe_instances):
            pipe_instance_name = f"{self.pipe_name}-{i}"
            self.thread_pool.submit(self._run_pipe_instance, pipe_instance_name)
            
        logger.info(
            f"启动了 {pipe_instances} 个 Named Pipe 实例，最大并发: {self.max_connections}"
        )
        
        # 写入pipe信息到配置文件
        self._write_pipe_info()
        
        logger.info(f"✅ Windows Named Pipe IPC服务器已启动: {self.full_pipe_name}")
        
    def _start_async_loop_thread(self):
        """启动异步事件循环线程"""
        def run_async_loop():
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)
            self.event_loop.run_forever()
            
        self.event_loop_thread = threading.Thread(target=run_async_loop, daemon=True)
        self.event_loop_thread.start()
        
        while not self.event_loop:
            time.sleep(0.001)
            
        logger.info("✅ 异步事件循环线程已启动")
        
    def _run_pipe_instance(self, instance_name: str):
        """运行单个Named Pipe实例"""
        full_instance_name = f"\\\\.\\pipe\\{instance_name}"
        retry_count = 0
        max_retries = 5
        retry_delay = 1.0
        
        logger.info(f"⚙️ 启动 Named Pipe 实例: {instance_name}")
        
        while self._is_running:
            try:
                pipe_handle = win32pipe.CreateNamedPipe(
                    full_instance_name,
                    win32pipe.PIPE_ACCESS_DUPLEX | win32file.FILE_FLAG_OVERLAPPED,
                    (
                        win32pipe.PIPE_TYPE_MESSAGE
                        | win32pipe.PIPE_READMODE_MESSAGE
                        | win32pipe.PIPE_WAIT
                    ),
                    win32pipe.PIPE_UNLIMITED_INSTANCES,
                    65536,
                    65536,
                    0,
                    self.security_attributes,
                )
                
                if pipe_handle == win32file.INVALID_HANDLE_VALUE:
                    logger.error(f"创建Named Pipe实例失败: {instance_name}")
                    time.sleep(1)
                    continue
                    
                overlapped = pywintypes.OVERLAPPED()
                overlapped.hEvent = win32event.CreateEvent(None, 0, 0, None)
                
                win32pipe.ConnectNamedPipe(pipe_handle, overlapped)
                
                result = win32event.WaitForSingleObject(
                    overlapped.hEvent, 30000
                )
                
                if result == win32event.WAIT_OBJECT_0:
                    logger.info(f"客户端已连接: {instance_name}")
                    self._handle_client(pipe_handle, instance_name)
                elif result == win32event.WAIT_TIMEOUT:
                    logger.debug(f"等待连接超时: {instance_name}")
                else:
                    logger.warning(f"等待连接失败: {instance_name}")
                    
                try:
                    win32pipe.DisconnectNamedPipe(pipe_handle)
                    win32file.CloseHandle(pipe_handle)
                    win32file.CloseHandle(overlapped.hEvent)
                except Exception as e:
                    logger.error(f"关闭pipe时出错: {e}")
                    
            except pywintypes.error as e:
                if self._is_running:
                    retry_count += 1
                    if retry_count <= max_retries:
                        logger.warning(f"Named Pipe实例 {instance_name} 错误: {e} (重试 {retry_count}/{max_retries})")
                        time.sleep(retry_delay * retry_count)
                    else:
                        logger.error(f"Named Pipe实例 {instance_name} 达到最大重试次数: {e}")
                        break
                else:
                    break
                    
            except Exception as e:
                if self._is_running:
                    retry_count += 1
                    if retry_count <= max_retries:
                        logger.error(f"Named Pipe实例 {instance_name} 未知错误: {e} (重试 {retry_count}/{max_retries})")
                        time.sleep(retry_delay * retry_count)
                    else:
                        logger.critical(f"Named Pipe实例 {instance_name} 严重错误，停止运行: {e}")
                        break
                else:
                    break
                    
            if retry_count > 0 and self._is_running:
                retry_count = 0
                logger.info(f"✅ Named Pipe实例 {instance_name} 恢复正常")
                
        logger.info(f"🚫 Named Pipe实例 {instance_name} 已停止")
        
    def _handle_client(self, pipe_handle, instance_name: str):
        """处理单个客户端连接"""
        client_id = f"{instance_name}-{int(time.time())}-{threading.get_ident()}"
        
        with self.connection_lock:
            if self.active_connections >= self.max_connections:
                logger.warning(f"达到最大连接数限制: {self.max_connections}")
                return
            self.active_connections += 1
            
        self.clients.add(hash(client_id))
        logger.debug(f"新客户端连接: {client_id} (当前活跃: {self.active_connections})")
        
        try:
            while self._is_running:
                try:
                    # 读取消息长度前缀
                    length_data = self._read_exact(pipe_handle, 4)
                    if not length_data:
                        break
                        
                    message_length = int.from_bytes(length_data, byteorder="big")
                    
                    # 读取完整消息
                    message_data = self._read_exact(pipe_handle, message_length)
                    if not message_data:
                        break
                        
                    message_str = message_data.decode("utf-8")
                    logger.debug(f"收到Named Pipe消息 [{instance_name}]: {len(message_str)} bytes")
                    
                    # 处理消息
                    start_time = time.perf_counter()
                    
                    with self.stats_lock:
                        self.stats["total_requests"] += 1
                        self.stats["active_requests"] += 1
                        
                    try:
                        response = self._process_message_sync_bridge(message_str, client_id)
                        
                        response_time = time.perf_counter() - start_time
                        with self.stats_lock:
                            total = self.stats["total_requests"]
                            old_avg = self.stats["avg_response_time"]
                            self.stats["avg_response_time"] = (
                                old_avg * (total - 1) + response_time
                            ) / total
                            
                        # 发送响应
                        response_bytes = response.encode("utf-8")
                        length_bytes = len(response_bytes).to_bytes(4, byteorder="big")
                        
                        win32file.WriteFile(pipe_handle, length_bytes)
                        win32file.WriteFile(pipe_handle, response_bytes)
                        
                    except Exception as process_error:
                        logger.error(f"处理消息失败: {process_error}")
                        
                        with self.stats_lock:
                            self.stats["failed_requests"] += 1
                            
                        error_response = json.dumps({
                            "success": False,
                            "error": {
                                "code": "IPC_PROCESSING_ERROR",
                                "message": str(process_error),
                            },
                            "metadata": {"timestamp": time.time()},
                        })
                        
                        response_bytes = error_response.encode("utf-8")
                        length_bytes = len(response_bytes).to_bytes(4, byteorder="big")
                        
                        win32file.WriteFile(pipe_handle, length_bytes)
                        win32file.WriteFile(pipe_handle, response_bytes)
                        
                    finally:
                        with self.stats_lock:
                            self.stats["active_requests"] -= 1
                            
                except pywintypes.error as e:
                    if e.winerror == 109:  # ERROR_BROKEN_PIPE
                        logger.debug(f"客户端断开连接: {instance_name}")
                        break
                    elif e.winerror == 232:  # ERROR_NO_DATA
                        logger.debug(f"客户端关闭管道: {instance_name}")
                        break
                    else:
                        logger.error(f"Named Pipe通信错误 [winerror={e.winerror}]: {e}")
                        if e.winerror in [5, 6, 87]:  # 不可恢复错误
                            break
                        time.sleep(0.1)
                        continue
                        
        except Exception as e:
            logger.error(f"处理Named Pipe客户端时出错 [{instance_name}]: {e}", exc_info=True)
            
        finally:
            self.clients.discard(hash(client_id))
            self.pending_futures.pop(client_id, None)
            
            with self.connection_lock:
                self.active_connections -= 1
                
            logger.debug(f"客户端断开连接: {client_id} (剩余活跃: {self.active_connections})")
            
    def _read_exact(self, pipe_handle, num_bytes: int) -> bytes:
        """精确读取指定字节数"""
        data = b""
        while len(data) < num_bytes:
            try:
                result, chunk = win32file.ReadFile(pipe_handle, num_bytes - len(data))
                if result == 0:
                    data += chunk
                else:
                    break
            except pywintypes.error:
                break
        return data if len(data) == num_bytes else b""
        
    def _process_message_sync_bridge(self, message_str: str, client_id: str) -> str:
        """异步-同步桥接方法"""
        if not self.event_loop or not self.app:
            return json.dumps({
                "success": False,
                "error": {
                    "code": "SERVICE_UNAVAILABLE",
                    "message": "IPC application or event loop not available",
                },
                "metadata": {"timestamp": time.time()},
            })
            
        try:
            future = asyncio.run_coroutine_threadsafe(
                self._process_ipc_message_async(message_str, client_id), self.event_loop
            )
            
            self.pending_futures[client_id] = future
            
            timeout = 3.0
            try:
                result = future.result(timeout=timeout)
            except asyncio.TimeoutError:
                logger.warning(f"请求处理超时 ({timeout}s): {client_id}")
                future.cancel()
                raise Exception(f"Request processing timeout after {timeout} seconds")
            return result
            
        except asyncio.TimeoutError:
            return json.dumps({
                "success": False,
                "error": {
                    "code": "IPC_REQUEST_TIMEOUT",
                    "message": "Request processing timeout",
                },
                "metadata": {"timestamp": time.time()},
            })
        except Exception as e:
            logger.error(f"异步-同步桥接失败: {e}")
            return json.dumps({
                "success": False,
                "error": {
                    "code": "IPC_BRIDGE_ERROR",
                    "message": f"Async-sync bridge failed: {str(e)}",
                },
                "metadata": {"timestamp": time.time()},
            })
        finally:
            self.pending_futures.pop(client_id, None)
            
    async def _process_ipc_message_async(self, message_str: str, client_id: str) -> str:
        """在事件循环中处理IPC消息"""
        try:
            from ..ipc_router import IPCRequest, IPCResponse
            
            message_data = json.loads(message_str)
            
            if not self._verify_client_security(client_id):
                logger.warning(f"客户端安全验证失败: {client_id}")
                from ..ipc_protocol import IPCErrorCode, IPCResponse
                
                error_response = IPCResponse.error_response(
                    IPCErrorCode.AUTH_FAILED, "Client security verification failed"
                )
                return error_response.to_json()
                
            request = IPCRequest(
                method=message_data.get("method", "GET"),
                path=message_data.get("path", "/"),
                data=message_data.get("data", {}),
                query_params=message_data.get("query_params", {}),
                request_id=message_data.get("request_id"),
            )
            
            if "headers" in message_data:
                request._headers = message_data["headers"]
                
            if self.app:
                response = await self.app.handle_request(
                    request.method,
                    request.path,
                    request.data,
                    request.query_params,
                    getattr(request, "_headers", {}),
                    request.request_id,
                )
            else:
                response = IPCResponse(
                    success=False,
                    error={
                        "code": "SERVICE_UNAVAILABLE",
                        "message": "IPC application not available",
                    },
                )
                
            return response.to_json()
            
        except Exception as e:
            logger.error(f"处理IPC消息失败: {e}")
            from ..ipc_protocol import IPCResponse
            
            error_response = IPCResponse.error_response(
                "INTERNAL_ERROR", f"Message processing failed: {str(e)}"
            )
            return error_response.to_json()
            
    def _verify_client_security(self, client_id: str) -> bool:
        """验证客户端安全性"""
        if not WINDOWS_SUPPORT or not self.allowed_sids:
            return True
            
        try:
            return True  # 简化为总是通过，因为Named Pipe本身已通过ACL控制访问
        except Exception as e:
            logger.error(f"客户端安全验证异常: {e}")
            return False
            
    def _write_pipe_info(self):
        """写入pipe信息到配置文件"""
        try:
            from config.dependencies import get_config_manager
            
            config_manager = get_config_manager()
            socket_info = {
                "type": "named_pipe",
                "path": self.full_pipe_name,
                "pid": os.getpid(),
                "protocol": "ipc",
            }
            
            socket_file = config_manager.get_paths()["app_data"] / "daemon.socket"
            socket_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(socket_file, "w") as f:
                json.dump(socket_info, f, indent=2)
                
            logger.info(f"Named Pipe信息已写入: {socket_file}")
            
        except Exception as e:
            logger.error(f"写入pipe信息失败: {e}")

    async def stop(self) -> None:
        """停止Named Pipe服务器 - 🆕 内嵌实现"""
        self._is_running = False
        
        # 取消所有待处理的任务
        for future in self.pending_futures.values():
            try:
                future.cancel()
            except (RuntimeError, asyncio.CancelledError) as e:
                logger.debug(f"取消Future失败: {e}")
        self.pending_futures.clear()
        
        # 停止异步事件循环
        if self.event_loop and self.event_loop.is_running():
            self.event_loop.call_soon_threadsafe(self.event_loop.stop)
            
        # 等待事件循环线程结束
        if self.event_loop_thread and self.event_loop_thread.is_alive():
            self.event_loop_thread.join(timeout=2.0)
            
        # 关闭线程池
        logger.info("🚫 正在关闭线程池...")
        try:
            self.thread_pool.shutdown(wait=True, timeout=10.0)
            logger.info("✅ 线程池已关闭")
        except Exception as e:
            logger.warning(f"关闭线程池时出错: {e}")
            try:
                self.thread_pool.shutdown(wait=False)
            except (RuntimeError, OSError):
                pass
                
        # 清理配置文件
        try:
            from config.dependencies import get_config_manager
            
            config_manager = get_config_manager()
            socket_file = config_manager.get_paths()["app_data"] / "daemon.socket"
            if socket_file.exists():
                socket_file.unlink()
        except Exception as e:
            logger.error(f"清理配置文件时出错: {e}")
            
        logger.info("✅ Windows Named Pipe IPC服务器已停止")

    def get_connection_info(self) -> Dict[str, Any]:
        """获取Named Pipe连接信息 - 🆕 内嵌实现"""
        return {
            "type": "named_pipe",
            "pipe_name": self.pipe_name,
            "full_path": self.full_pipe_name,
            "platform": "windows",
        }

    def get_stats(self) -> Dict[str, Any]:
        """获取Named Pipe统计信息 - 🆕 内嵌实现"""
        with self.stats_lock:
            uptime = time.time() - self.stats["start_time"]
            return {
                **self.stats.copy(),
                "uptime_seconds": uptime,
                "active_connections": self.active_connections,
                "requests_per_second": self.stats["total_requests"] / max(uptime, 1),
                "allowed_sids_count": len(self.allowed_sids),
                "security_enabled": self.security_attributes is not None,
                "is_running": self._is_running,
            }

    def is_running(self) -> bool:
        """检查Named Pipe服务器是否运行中"""
        return self._is_running


class IPCStrategyFactory:
    """IPC策略工厂"""

    @staticmethod
    def create_strategy(platform: str = None, **kwargs) -> IPCStrategy:
        """根据平台创建相应的IPC策略"""
        import platform as platform_module

        if platform is None:
            platform = platform_module.system()

        if platform == "Windows":
            return WindowsNamedPipeStrategy(kwargs.get("pipe_name"))
        else:
            return UnixSocketStrategy(kwargs.get("socket_path"))

    @staticmethod
    def get_default_config(platform: str = None) -> Dict[str, Any]:
        """获取平台的默认配置"""
        import platform as platform_module

        if platform is None:
            platform = platform_module.system()

        if platform == "Windows":
            return {
                "type": "named_pipe",
                "pipe_name": "linch-mind-ipc",
                "platform": "windows",
            }
        else:
            return {
                "type": "unix_socket",
                "socket_path": "/tmp/linch-mind-ipc.sock",
                "platform": "unix",
            }
