"""
Windows Named Pipe 实现
提供Windows系统下的进程间通信支持
"""

import asyncio
import json
import logging
import os
import platform
import queue
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional, Set

logger = logging.getLogger(__name__)

# Windows Named Pipe实现需要pywin32或其他Windows特定库
# 这里提供一个基础的跨平台兼容实现

if platform.system() == "Windows":
    try:
        import pywintypes
        import win32file
        import win32pipe

        WINDOWS_SUPPORT = True
    except ImportError:
        WINDOWS_SUPPORT = False
        logger.warning("pywin32未安装，Windows Named Pipe功能不可用")
else:
    WINDOWS_SUPPORT = False


class WindowsNamedPipeServer:
    """Windows Named Pipe服务器实现"""

    def __init__(self, pipe_name: str, max_clients: int = 10):
        self.pipe_name = pipe_name
        self.full_pipe_name = f"\\\\.\\pipe\\{pipe_name}"
        self.is_running = False
        self.clients: Set[threading.Thread] = set()
        self.app = None
        self.max_clients = max_clients
        self.executor = ThreadPoolExecutor(
            max_workers=max_clients, thread_name_prefix="NamedPipe"
        )
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._stats = {"total_requests": 0, "active_connections": 0, "error_count": 0}

    def set_ipc_app(self, app):
        """设置IPC应用实例 - 兼容纯IPC架构"""
        self.app = app
        # 设置事件循环引用
        try:
            self._loop = asyncio.get_event_loop()
        except RuntimeError:
            logger.warning("无法获取当前事件循环，异步处理将不可用")
            self._loop = None

    def _create_security_descriptor(self):
        """创建Windows安全描述符 - 增强版本"""
        if not WINDOWS_SUPPORT:
            return None

        try:
            import ntsecuritycon as con
            import win32api
            import win32security

            # 获取当前用户SID
            user_sid = win32security.GetTokenInformation(
                win32security.OpenProcessToken(
                    win32api.GetCurrentProcess(), win32security.TOKEN_QUERY
                ),
                win32security.TokenUser,
            )[0]

            # 获取管理员组SID
            admin_sid = win32security.CreateWellKnownSid(
                win32security.WinBuiltinAdministratorsSid
            )

            # 创建ACL
            acl = win32security.ACL()

            # 添加权限：当前用户拥有完全控制
            acl.AddAccessAllowedAce(
                win32security.ACL_REVISION, con.GENERIC_ALL, user_sid
            )

            # 添加权限：管理员组拥有完全控制
            acl.AddAccessAllowedAce(
                win32security.ACL_REVISION, con.GENERIC_ALL, admin_sid
            )

            # 创建安全描述符
            sd = win32security.SECURITY_DESCRIPTOR()
            sd.SetSecurityDescriptorDacl(1, acl, 0)
            sd.SetSecurityDescriptorOwner(user_sid, 0)

            # 创建安全属性结构
            sa = win32security.SECURITY_ATTRIBUTES()
            sa.SECURITY_DESCRIPTOR = sd
            sa.bInheritHandle = 0

            logger.info("创建了增强的Windows安全描述符（仅当前用户+管理员访问）")
            return sa

        except Exception as e:
            logger.warning(f"创建增强安全描述符失败，使用基础权限控制: {e}")
            try:
                # 回退到基础安全控制
                sd = win32security.SECURITY_DESCRIPTOR()
                sd.SetSecurityDescriptorDacl(1, None, 0)
                sa = win32security.SECURITY_ATTRIBUTES()
                sa.SECURITY_DESCRIPTOR = sd
                sa.bInheritHandle = 0
                return sa
            except:
                logger.warning("无法创建任何安全描述符，使用系统默认")
                return None

    def _verify_client_security(self, pipe_handle) -> bool:
        """验证客户端安全性"""
        if not WINDOWS_SUPPORT:
            return True

        try:
            # 获取客户端令牌
            client_token = win32pipe.GetNamedPipeClientProcessId(pipe_handle)
            logger.debug(f"客户端进程ID: {client_token}")

            # 这里可以添加更多安全检查，如：
            # 1. 检查客户端进程是否为可信进程
            # 2. 验证进程签名
            # 3. 检查进程完整性级别

            return True

        except Exception as e:
            logger.warning(f"客户端安全验证失败: {e}")
            return True  # 允许连接，但记录警告

    def get_stats(self) -> Dict[str, Any]:
        """获取服务器统计信息"""
        return {
            **self._stats,
            "is_running": self.is_running,
            "pipe_name": self.full_pipe_name,
            "max_clients": self.max_clients,
        }

    async def start(self):
        """启动Named Pipe服务器"""
        if not WINDOWS_SUPPORT:
            raise RuntimeError("Windows Named Pipe需要pywin32库支持")

        self.is_running = True

        # 创建事件循环并在线程中运行服务器
        server_thread = threading.Thread(target=self._run_server, daemon=True)
        server_thread.start()

        logger.info(f"Windows Named Pipe服务器已启动: {self.full_pipe_name}")

        # 写入pipe信息
        self._write_pipe_info()

    def _run_server(self):
        """在独立线程中运行Named Pipe服务器"""
        while self.is_running:
            try:
                # 创建命名管道
                pipe_handle = win32pipe.CreateNamedPipe(
                    self.full_pipe_name,
                    win32pipe.PIPE_ACCESS_DUPLEX | win32file.FILE_FLAG_WRITE_THROUGH,
                    win32pipe.PIPE_TYPE_MESSAGE
                    | win32pipe.PIPE_READMODE_MESSAGE
                    | win32pipe.PIPE_WAIT,
                    win32pipe.PIPE_UNLIMITED_INSTANCES,  # 支持多实例
                    1024 * 1024,  # 输出缓冲区1MB (性能优化)
                    1024 * 1024,  # 输入缓冲区1MB (性能优化)
                    100,  # 默认超时100ms (性能优化)
                    self._create_security_descriptor(),  # 安全属性
                )

                if pipe_handle == win32file.INVALID_HANDLE_VALUE:
                    logger.error("创建Named Pipe失败")
                    break

                # 等待客户端连接
                logger.debug("等待客户端连接Named Pipe...")
                win32pipe.ConnectNamedPipe(pipe_handle, None)

                # 处理客户端
                self._handle_client(pipe_handle)

            except pywintypes.error as e:
                if self.is_running:
                    logger.error(f"Named Pipe服务器错误: {e}")
                    time.sleep(1)  # 错误后等待重试

            except Exception as e:
                if self.is_running:
                    logger.error(f"Named Pipe服务器未知错误: {e}")
                    time.sleep(1)

    def _handle_client(self, pipe_handle):
        """处理单个客户端连接"""
        try:
            while self.is_running:
                # 读取消息
                try:
                    result, data = win32file.ReadFile(pipe_handle, 4096)
                    if result == 0 and data:
                        message_str = data.decode("utf-8")
                        logger.debug(f"收到Named Pipe消息: {message_str}")

                        # 处理消息
                        response = self._process_message_sync(message_str)

                        # 发送响应
                        win32file.WriteFile(pipe_handle, response.encode("utf-8"))

                    else:
                        break

                except pywintypes.error as e:
                    if e.winerror == 109:  # ERROR_BROKEN_PIPE
                        logger.debug("客户端断开连接")
                        break
                    else:
                        logger.error(f"读取Named Pipe数据失败: {e}")
                        break

        except Exception as e:
            logger.error(f"处理Named Pipe客户端时出错: {e}")

        finally:
            try:
                win32pipe.DisconnectNamedPipe(pipe_handle)
                win32file.CloseHandle(pipe_handle)
            except Exception as e:
                logger.error(f"关闭Named Pipe连接时出错: {e}")

    def _process_message_sync(self, message_str: str) -> str:
        """同步处理消息（Named Pipe在线程中运行）- 真正的IPC桥接版本"""
        try:
            from .ipc_protocol import IPCRequest, IPCResponse
            from .ipc_server import IPCMessage

            # 解析IPC消息
            message_data = json.loads(message_str)
            ipc_message = IPCMessage(
                method=message_data.get("method", "GET"),
                path=message_data.get("path", "/"),
                data=message_data.get("data", {}),
                headers=message_data.get("headers", {}),
                query_params=message_data.get("query_params", {}),
            )

            # 转换为IPC请求
            request = IPCRequest(
                method=ipc_message.method,
                path=ipc_message.path,
                data=ipc_message.data,
                headers=ipc_message.headers,
                query_params=ipc_message.query_params,
            )

            # 使用IPC应用处理请求 - 异步-同步桥接
            if self.app and hasattr(self.app, "handle_request"):
                try:
                    # 在主事件循环中执行异步处理
                    if (
                        hasattr(self, "_loop")
                        and self._loop
                        and not self._loop.is_closed()
                    ):
                        future = asyncio.run_coroutine_threadsafe(
                            self.app.handle_request(request), self._loop
                        )
                        # 设置超时避免阻塞
                        response = future.result(timeout=30.0)
                    else:
                        # 回退到同步模拟
                        logger.warning("事件循环不可用，使用模拟响应")
                        response_data = {
                            "message": "Windows Named Pipe IPC响应",
                            "method": request.method,
                            "path": request.path,
                            "timestamp": time.time(),
                            "warning": "事件循环不可用",
                        }
                        response = IPCResponse(status_code=200, data=response_data)

                except Exception as app_error:
                    logger.error(f"IPC应用处理失败: {app_error}")
                    response = IPCResponse(
                        status_code=500, data={"error": str(app_error)}
                    )
            else:
                response = IPCResponse(
                    status_code=500, data={"error": "IPC应用未设置或无效"}
                )

            return response.to_json()

        except Exception as e:
            logger.error(f"处理Named Pipe消息失败: {e}")
            from .ipc_protocol import IPCResponse

            error_response = IPCResponse(status_code=500, data={"error": str(e)})
            return error_response.to_json()

    def _write_pipe_info(self):
        """写入pipe信息到配置文件"""
        from config.dependencies import get_config_manager

        config_manager = get_config_manager()
        socket_info = {
            "type": "named_pipe",
            "path": self.full_pipe_name,
            "pid": os.getpid(),
        }

        # 写入到socket配置文件
        socket_file = config_manager.get_paths()["app_data"] / "daemon.socket"
        with open(socket_file, "w") as f:
            json.dump(socket_info, f)

        logger.info(f"Named Pipe信息已写入: {socket_file}")

    async def stop(self):
        """停止Named Pipe服务器"""
        self.is_running = False

        # 等待所有客户端处理完成
        if hasattr(self, "executor"):
            logger.info("等待所有Named Pipe客户端处理完成...")
            self.executor.shutdown(wait=True, timeout=10.0)

        # 清理socket信息文件
        try:
            from config.dependencies import get_config_manager

            config_manager = get_config_manager()
            socket_file = config_manager.get_paths()["app_data"] / "daemon.socket"
            if socket_file.exists():
                os.unlink(socket_file)
        except Exception as e:
            logger.warning(f"清理socket信息文件失败: {e}")

        logger.info(f"Windows Named Pipe服务器已停止，统计信息: {self.get_stats()}")


class CrossPlatformNamedPipeServer:
    """跨平台Named Pipe兼容实现"""

    def __init__(self, pipe_name: str):
        self.pipe_name = pipe_name
        self.server = None

    def set_ipc_app(self, app):
        """设置IPC应用实例 - 纯IPC版本"""
        if platform.system() == "Windows" and WINDOWS_SUPPORT:
            self.server = WindowsNamedPipeServer(self.pipe_name)
            self.server.set_ipc_app(app)
        else:
            # 在非Windows系统上，回退到Unix socket或抛出错误
            logger.warning("Named Pipe仅在Windows系统上支持，请使用Unix Domain Socket")

    async def start(self):
        """启动服务器"""
        if self.server:
            await self.server.start()
        else:
            raise RuntimeError("Named Pipe服务器未正确初始化")

    async def stop(self):
        """停止服务器"""
        if self.server:
            await self.server.stop()
