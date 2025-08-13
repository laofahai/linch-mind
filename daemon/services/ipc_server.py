"""
IPC服务器 - 完全独立的IPC通信系统
不依赖FastAPI，提供纯IPC的本地进程间通信
"""

import asyncio
import json
import logging
import os
import platform
import stat
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from .ipc_middleware import create_default_middlewares
from .ipc_protocol import IPCRequest
from .ipc_router import IPCApplication
from .ipc_routes import register_all_routes
from .ipc_security import (
    IPCSecurityManager,
    secure_socket_directory,
    secure_socket_file,
)

logger = logging.getLogger(__name__)


class IPCServer:
    """纯IPC服务器 - 完全独立于FastAPI"""

    def __init__(
        self, socket_path: Optional[str] = None, pipe_name: Optional[str] = None
    ):
        self.socket_path = socket_path
        self.pipe_name = pipe_name
        self.server = None
        self.is_running = False
        self.clients = set()
        self.client_connections = {}  # 存储客户端连接ID和安全上下文的映射

        # 使用纯IPC应用实例
        self.app = IPCApplication()

        # 添加默认中间件
        for middleware in create_default_middlewares(debug=False):
            self.app.add_middleware(middleware)

        # 注册所有路由
        register_all_routes(self.app)

        # 使用依赖注入获取安全管理器
        from core.container import get_container

        container = get_container()

        try:
            self.security_manager = container.get_service(IPCSecurityManager)
            logger.info("✅ 通过依赖注入获取IPC安全管理器成功")
        except Exception as e:
            logger.error(f"❌ 获取IPC安全管理器失败: {e}")
            # 临时回退到直接创建实例
            from .ipc_security import create_security_manager

            self.security_manager = create_security_manager()
            logger.warning("⚠️ 使用临时安全管理器实例")

        logger.info("IPC应用已初始化，所有路由和中间件已加载，安全管理器已启用")

    async def start(self):
        """启动IPC服务器"""
        if platform.system() == "Windows":
            await self._start_named_pipe()
        else:
            await self._start_unix_socket()

    async def _start_unix_socket(self):
        """启动Unix Domain Socket服务器"""
        if not self.socket_path:
            # 使用临时目录创建socket文件
            temp_dir = tempfile.gettempdir()
            self.socket_path = os.path.join(temp_dir, f"linch-mind-{os.getpid()}.sock")

        # 清理可能存在的旧socket文件
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)

        # 确保socket目录的安全性
        socket_dir = Path(self.socket_path).parent
        secure_socket_directory(socket_dir)

        # 创建Unix socket服务器
        self.server = await asyncio.start_unix_server(
            self._handle_client, path=self.socket_path
        )

        # 加固socket文件安全性
        secure_socket_file(self.socket_path)

        self.is_running = True
        logger.info(f"Unix Domain Socket服务器已启动: {self.socket_path}")

        # 写入socket路径到配置文件
        self._write_socket_info()

    async def _start_named_pipe(self):
        """启动Windows Named Pipe服务器"""
        if not self.pipe_name:
            self.pipe_name = f"linch-mind-{os.getpid()}"

        # Windows Named Pipe实现
        # 注意: 这需要Windows特定的实现，这里提供基础框架
        logger.info(f"Named Pipe服务器启动: \\\\.\\pipe\\{self.pipe_name}")

        # TODO: 实现Windows Named Pipe
        # 这里需要使用pywin32或其他Windows特定库

        self.is_running = True
        self._write_socket_info()

    def _write_socket_info(self):
        """写入socket信息到配置文件"""
        from config.dependencies import get_config_manager

        get_config_manager()

        # 准备socket信息
        socket_info = {
            "type": "unix_socket" if platform.system() != "Windows" else "named_pipe",
            "path": (
                self.socket_path
                if self.socket_path
                else f"\\\\.\\pipe\\{self.pipe_name}"
            ),
            "pid": os.getpid(),
            "protocol": "ipc",
        }

        # 🔧 修复：socket.info文件应该写到环境根目录，与daemon.socket和daemon.pid保持一致
        # UI期望在环境根目录找到此文件，而不是在data子目录
        # 获取环境根目录
        from core.environment_manager import get_environment_manager

        env_manager = get_environment_manager()
        env_root = env_manager.current_config.base_path
        socket_info_file = env_root / "daemon.socket.info"
        with open(socket_info_file, "w") as f:
            json.dump(socket_info, f, indent=2)

        # 设置文件权限
        if platform.system() != "Windows":
            os.chmod(socket_info_file, stat.S_IRUSR | stat.S_IWUSR)

        logger.info(f"Socket信息已写入: {socket_info_file}")

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        """处理客户端连接"""
        client_addr = writer.get_extra_info("peername")
        connection_id = f"{id(writer)}"
        logger.debug(f"新的IPC连接: {client_addr}, ID: {connection_id}")

        self.clients.add(writer)

        # 等待客户端发送认证信息
        authenticated = False

        try:
            while True:
                # 读取消息长度前缀 (4字节)
                length_data = await reader.readexactly(4)
                if not length_data:
                    break

                message_length = int.from_bytes(length_data, byteorder="big")

                # 读取完整消息
                message_data = await reader.readexactly(message_length)
                message_str = message_data.decode("utf-8")

                # 解析IPC消息
                try:
                    ipc_request = IPCRequest.from_json(message_str)
                    logger.debug(
                        f"收到IPC请求: {ipc_request.method} {ipc_request.path}"
                    )

                    # 检查是否为认证请求或已认证
                    if not authenticated and ipc_request.path == "/auth/handshake":
                        # 🔐 认证请求：注入真实客户端PID，防止PID欺骗
                        if not ipc_request.headers:
                            ipc_request.headers = {}

                        # 使用改进的跨平台PID获取机制
                        try:
                            from .ipc.peer_credentials import (
                                get_socket_peer_credentials,
                            )

                            sock = writer.get_extra_info("socket")
                            if sock:
                                credentials = get_socket_peer_credentials(sock)

                                if credentials.pid and credentials.confidence in [
                                    "high",
                                    "medium",
                                ]:
                                    # 注入验证过的真实PID到请求头
                                    ipc_request.headers["x-real-client-pid"] = str(
                                        credentials.pid
                                    )
                                    ipc_request.headers["x-pid-source"] = (
                                        credentials.source
                                    )
                                    ipc_request.headers["x-pid-confidence"] = (
                                        credentials.confidence
                                    )

                                    logger.debug(
                                        f"安全PID注入成功: PID={credentials.pid}, 来源={credentials.source}, 可信度={credentials.confidence}"
                                    )

                                elif (
                                    credentials.pid and credentials.confidence == "low"
                                ):
                                    # 低可信度时也注入，但标记
                                    ipc_request.headers["x-real-client-pid"] = str(
                                        credentials.pid
                                    )
                                    ipc_request.headers["x-pid-source"] = (
                                        credentials.source
                                    )
                                    ipc_request.headers["x-pid-confidence"] = (
                                        credentials.confidence
                                    )

                                    logger.debug(
                                        f"低可信度PID注入: PID={credentials.pid}, 来源={credentials.source}"
                                    )

                                else:
                                    # PID获取完全失败，但不输出警告（客户端声明的PID仍可用于基本验证）
                                    logger.debug(
                                        f"无法获取可靠的客户端PID: 来源={credentials.source}"
                                    )
                            else:
                                logger.debug("无法获取socket对象，跳过PID注入")

                        except Exception as e:
                            logger.debug(f"PID获取过程出错: {e}")  # 降级为debug级别

                        # 处理认证请求
                        response = await self._process_message(ipc_request)
                        # 使用IPC格式检查认证结果
                        authenticated = response.get("success") and response.get(
                            "data", {}
                        ).get("authenticated", False)
                        if authenticated:
                            # 记录认证信息到连接上下文
                            request_data = ipc_request.data or {}
                            client_pid = request_data.get("client_pid", 0)
                            server_pid = os.getpid()
                            is_internal = client_pid == server_pid
                            self.client_connections[connection_id] = {
                                "authenticated": True,
                                "client_pid": client_pid,
                                "internal": is_internal,
                            }
                            logger.info(
                                f"IPC客户端认证成功: {connection_id}, PID={client_pid}, internal={is_internal}"
                            )
                    elif not authenticated:
                        # 未认证的客户端只能访问认证端点 - 使用IPC格式响应
                        from .ipc_protocol import IPCErrorCode, IPCResponse

                        error_response = IPCResponse.error_response(
                            IPCErrorCode.AUTH_REQUIRED, "Authentication required"
                        )
                        response = error_response.to_dict()
                    else:
                        # 已认证客户端，添加认证信息并处理请求
                        if not ipc_request.headers:
                            ipc_request.headers = {}

                        client_info = self.client_connections.get(connection_id, {})
                        ipc_request.headers["x-client-pid"] = str(
                            client_info.get("client_pid", 0)
                        )
                        ipc_request.headers["x-authenticated"] = "true"

                        # 检查是否为内部客户端
                        if client_info.get("internal", False):
                            ipc_request.headers["x-internal-client"] = "true"

                        # 简化：只进行基本频率限制检查，移除复杂的安全验证
                        client_pid = client_info.get("client_pid", 0)
                        if self.security_manager.rate_limiter.is_allowed(client_pid):
                            response = await self._process_message(ipc_request)
                        else:
                            # 频率限制 - 使用IPC格式响应
                            from .ipc_protocol import IPCErrorCode, IPCResponse

                            rate_limit_response = IPCResponse.error_response(
                                IPCErrorCode.REQUEST_TIMEOUT,
                                "Too many requests - rate limited",
                            )
                            response = rate_limit_response.to_dict()

                    # 发送响应
                    await self._send_response(writer, response)

                except json.JSONDecodeError as e:
                    logger.error(f"IPC消息JSON解析失败: {e}")
                    # 使用IPC格式错误响应
                    from .ipc_protocol import IPCErrorCode, IPCResponse

                    json_error_response = IPCResponse.error_response(
                        IPCErrorCode.INVALID_REQUEST,
                        "Invalid JSON format",
                        {"parse_error": str(e)},
                    )
                    await self._send_response(writer, json_error_response.to_dict())

                except Exception as e:
                    logger.error(f"处理IPC消息时出错: {e}")
                    # 使用IPC格式错误响应
                    from .ipc_protocol import IPCErrorCode, IPCResponse

                    server_error_response = IPCResponse.error_response(
                        IPCErrorCode.INTERNAL_ERROR,
                        f"Internal server error: {str(e)}",
                        {"exception_type": type(e).__name__},
                    )
                    await self._send_response(writer, server_error_response.to_dict())

        except asyncio.IncompleteReadError:
            logger.debug(f"IPC客户端断开连接: {client_addr}")
        except Exception as e:
            logger.error(f"IPC连接处理出错: {e}")
        finally:
            # 清理连接
            self.clients.discard(writer)
            if connection_id in self.client_connections:
                self.security_manager.close_connection(connection_id)
                del self.client_connections[connection_id]

            # 安全关闭连接
            try:
                if not writer.is_closing():
                    writer.close()
                    await writer.wait_closed()
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                logger.debug("连接已断开，无需等待关闭")
            except Exception as e:
                logger.debug(f"关闭连接时出错: {e}")

    async def _process_message(self, request: IPCRequest) -> Dict[str, Any]:
        """处理IPC消息，使用纯IPC应用"""
        if not self.app:
            from .ipc_protocol import IPCErrorCode, IPCResponse

            error_response = IPCResponse.error_response(
                IPCErrorCode.SERVICE_UNAVAILABLE, "IPC app not configured"
            )
            return error_response.to_dict()

        try:
            # 直接使用IPC应用处理请求
            response = await self.app.handle_request(
                method=request.method,
                path=request.path,
                data=request.data,
                query_params=request.query_params,
                headers=request.headers,
                request_id=request.request_id,
            )

            return response.to_dict()

        except Exception as e:
            logger.error(f"IPC应用处理请求失败: {e}")
            from .ipc_protocol import IPCErrorCode, IPCResponse

            error_response = IPCResponse.error_response(
                IPCErrorCode.INTERNAL_ERROR,
                f"Internal server error: {str(e)}",
                {"exception_type": type(e).__name__},
            )
            return error_response.to_dict()

    def _discover_client_pid(self, writer: asyncio.StreamWriter) -> Optional[int]:
        """
        发现客户端进程PID（向后兼容方法，推荐使用peer_credentials模块）
        """
        try:
            from .ipc.peer_credentials import discover_client_pid

            return discover_client_pid(writer)
        except Exception as e:
            logger.debug(f"客户端PID发现失败: {e}")
            return None

    async def _send_response(
        self, writer: asyncio.StreamWriter, response: Dict[str, Any]
    ):
        """发送响应到客户端"""
        try:
            response_json = json.dumps(response)
            response_bytes = response_json.encode("utf-8")

            # 发送消息长度前缀
            length_bytes = len(response_bytes).to_bytes(4, byteorder="big")
            writer.write(length_bytes)

            # 发送消息内容
            writer.write(response_bytes)
            await writer.drain()

        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError) as e:
            logger.debug(f"客户端连接已断开，无法发送响应: {e}")
            # 连接已断开，不需要进一步处理
        except Exception as e:
            logger.error(f"发送IPC响应时出错: {e}")
            raise

    async def stop(self):
        """停止IPC服务器"""
        self.is_running = False

        # 关闭所有客户端连接
        for client in list(self.clients):
            client.close()
            await client.wait_closed()
        self.clients.clear()

        # 关闭服务器
        if self.server:
            self.server.close()
            await self.server.wait_closed()

        # 清理socket文件
        if self.socket_path and os.path.exists(self.socket_path):
            os.unlink(self.socket_path)

        # 清理socket信息文件
        try:
            from core.environment_manager import get_environment_manager
            env_manager = get_environment_manager()
            env_root = env_manager.current_config.base_path
            socket_info_file = env_root / "daemon.socket.info"
            if socket_info_file.exists():
                socket_info_file.unlink()
                logger.info(f"已清理socket信息文件: {socket_info_file}")
        except Exception as e:
            logger.warning(f"清理socket信息文件失败: {e}")
        
        # 清理配置文件
        from config.dependencies import get_config_manager

        get_config_manager()

        # 清理socket文件
        if self.socket_path:
            socket_file = Path(self.socket_path)
            if socket_file.exists():
                try:
                    os.unlink(socket_file)
                except OSError:
                    pass  # 忽略清理错误

        logger.info("IPC服务器已停止")

    async def start_unix_server(self, socket_path: Optional[str] = None):
        """别名方法 - 为了与测试兼容"""
        if socket_path:
            self.socket_path = socket_path
        return await self._start_unix_socket()

    def get_server_status(self) -> Dict[str, Any]:
        """获取服务器状态信息"""
        return {
            "is_running": self.is_running,
            "active_clients": len(self.clients),
            "authenticated_connections": len(self.client_connections),
            "socket_path": self.socket_path,
            "pipe_name": self.pipe_name,
            "server_pid": os.getpid(),
            "security_status": (
                self.security_manager.get_security_status()
                if self.security_manager
                else None
            ),
        }


# 全局IPC服务器实例
_ipc_server = None


def get_ipc_server() -> IPCServer:
    """获取全局IPC服务器实例"""
    global _ipc_server
    if _ipc_server is None:
        from config.dependencies import get_config_manager

        config_manager = get_config_manager()

        # 🔧 使用配置文件中的socket_path，遵循环境隔离原则
        configured_socket_path = config_manager.config.server.socket_path
        if configured_socket_path:
            # 展开波浪号路径
            from pathlib import Path

            socket_path = Path(configured_socket_path).expanduser()
            logger.info(f"✅ 使用配置的socket路径: {socket_path}")
        else:
            # 回退到默认路径（保持向后兼容）
            socket_path = config_manager.get_paths()["data"] / "daemon.socket"
            logger.warning(f"⚠️ 配置中未设置socket_path，使用默认路径: {socket_path}")

        _ipc_server = IPCServer(socket_path=str(socket_path))
    return _ipc_server


async def start_ipc_server():
    """启动IPC服务器"""
    ipc_server = get_ipc_server()
    await ipc_server.start()
    logger.info("纯IPC服务器已启动，无FastAPI依赖")
    return ipc_server


async def stop_ipc_server():
    """停止IPC服务器"""
    global _ipc_server
    if _ipc_server:
        await _ipc_server.stop()
        _ipc_server = None
