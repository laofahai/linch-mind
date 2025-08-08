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
from .ipc_router import IPCApplication
from .ipc_routes import register_all_routes
from .ipc_security import (
    get_security_manager,
    secure_socket_directory,
    secure_socket_file,
)

logger = logging.getLogger(__name__)


class IPCMessage:
    """IPC消息格式定义"""

    def __init__(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ):
        self.method = method.upper()
        self.path = path
        self.data = data or {}
        self.headers = headers or {}
        self.query_params = query_params or {}

    def to_json(self) -> str:
        """序列化为JSON字符串"""
        return json.dumps(
            {
                "method": self.method,
                "path": self.path,
                "data": self.data,
                "headers": self.headers,
                "query_params": self.query_params,
            }
        )

    @classmethod
    def from_json(cls, json_str: str) -> "IPCMessage":
        """从JSON字符串反序列化"""
        data = json.loads(json_str)
        return cls(
            method=data["method"],
            path=data["path"],
            data=data.get("data"),
            headers=data.get("headers"),
            query_params=data.get("query_params"),
        )


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

        # 获取安全管理器
        self.security_manager = get_security_manager()

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

        config_manager = get_config_manager()

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

        # 写入主要的socket配置文件
        socket_file = config_manager.get_paths()["app_data"] / "daemon.socket"
        with open(socket_file, "w") as f:
            json.dump(socket_info, f, indent=2)

        # 设置文件权限
        if platform.system() != "Windows":
            os.chmod(socket_file, stat.S_IRUSR | stat.S_IWUSR)

        logger.info(f"Socket信息已写入: {socket_file}")

        # 向后兼容：同时写入daemon.port文件（供现有客户端使用）
        # 使用特殊端口0表示IPC模式
        port_file = config_manager.get_paths()["app_data"] / "daemon.port"
        try:
            with open(port_file, "w") as f:
                f.write(f"0:{os.getpid()}")

            if platform.system() != "Windows":
                os.chmod(port_file, stat.S_IRUSR | stat.S_IWUSR)

            logger.info(f"兼容性端口文件已写入: {port_file} (port=0表示IPC模式)")
        except Exception as e:
            logger.warning(f"写入兼容性端口文件失败: {e}")

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
                    ipc_message = IPCMessage.from_json(message_str)
                    logger.debug(
                        f"收到IPC请求: {ipc_message.method} {ipc_message.path}"
                    )

                    # 检查是否为认证请求或已认证
                    if not authenticated and ipc_message.path == "/auth/handshake":
                        # 认证请求：直接通过IPC应用处理
                        response = await self._process_message(ipc_message)
                        # 使用IPC格式检查认证结果
                        authenticated = response.get("success") and response.get(
                            "data", {}
                        ).get("authenticated", False)
                        if authenticated:
                            # 记录认证信息到连接上下文
                            client_pid = ipc_message.data.get("client_pid", 0)
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
                        if not ipc_message.headers:
                            ipc_message.headers = {}

                        client_info = self.client_connections.get(connection_id, {})
                        ipc_message.headers["x-client-pid"] = str(
                            client_info.get("client_pid", 0)
                        )
                        ipc_message.headers["x-authenticated"] = "true"

                        # 检查是否为内部客户端
                        if client_info.get("internal", False):
                            ipc_message.headers["x-internal-client"] = "true"

                        # 简化：只进行基本频率限制检查，移除复杂的安全验证
                        client_pid = client_info.get("client_pid", 0)
                        if self.security_manager.rate_limiter.is_allowed(client_pid):
                            response = await self._process_message(ipc_message)
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
            writer.close()
            await writer.wait_closed()

    async def _process_message(self, message: IPCMessage) -> Dict[str, Any]:
        """处理IPC消息，使用纯IPC应用"""
        if not self.app:
            from .ipc_protocol import IPCErrorCode, IPCResponse

            error_response = IPCResponse.error_response(
                IPCErrorCode.SERVICE_UNAVAILABLE, "IPC app not configured"
            )
            return error_response.to_dict()

        try:
            # 直接使用IPC应用处理请求，传递头部信息
            response = await self.app.handle_request(
                method=message.method,
                path=message.path,
                data=message.data,
                query_params=message.query_params,
                headers=message.headers,  # 传递头部信息
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

    async def _send_response(
        self, writer: asyncio.StreamWriter, response: Dict[str, Any]
    ):
        """发送响应到客户端"""
        response_json = json.dumps(response)
        response_bytes = response_json.encode("utf-8")

        # 发送消息长度前缀
        length_bytes = len(response_bytes).to_bytes(4, byteorder="big")
        writer.write(length_bytes)

        # 发送消息内容
        writer.write(response_bytes)
        await writer.drain()

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

        # 清理配置文件
        from config.dependencies import get_config_manager

        config_manager = get_config_manager()

        # 清理socket文件
        socket_file = config_manager.get_paths()["app_data"] / "daemon.socket"
        if socket_file.exists():
            os.unlink(socket_file)

        # 清理兼容性port文件
        port_file = config_manager.get_paths()["app_data"] / "daemon.port"
        if port_file.exists():
            os.unlink(port_file)

        logger.info("IPC服务器已停止")

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
        _ipc_server = IPCServer()
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
