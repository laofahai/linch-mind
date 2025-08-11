#!/usr/bin/env python3
"""
跨平台IPC统一接口抽象层
为Unix Socket和Windows Named Pipe提供统一的编程接口
"""

import asyncio
import logging
import platform
from typing import Any, Dict, Optional, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@runtime_checkable
class IPCServerProtocol(Protocol):
    """IPC服务器协议定义"""

    async def start(self) -> None:
        """启动IPC服务器"""
        ...

    async def stop(self) -> None:
        """停止IPC服务器"""
        ...

    def set_ipc_app(self, app) -> None:
        """设置IPC应用实例"""
        ...

    def get_stats(self) -> Dict[str, Any]:
        """获取服务器统计信息"""
        ...


@runtime_checkable
class IPCClientProtocol(Protocol):
    """IPC客户端协议定义"""

    def connect(self) -> bool:
        """连接到IPC服务器"""
        ...

    def send_request(
        self, method: str, path: str, data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """发送IPC请求并获取响应"""
        ...

    def disconnect(self) -> None:
        """断开与IPC服务器的连接"""
        ...


class CrossPlatformIPCServer:
    """跨平台IPC服务器统一接口"""

    def __init__(
        self,
        socket_path: Optional[str] = None,
        pipe_name: Optional[str] = None,
        max_clients: int = 10,
    ):
        self.socket_path = socket_path
        self.pipe_name = pipe_name
        self.max_clients = max_clients
        self._server: Optional[IPCServerProtocol] = None
        self._platform = platform.system()

        # 根据平台选择实现
        self._initialize_platform_server()

    def _initialize_platform_server(self):
        """根据平台初始化相应的服务器实现"""
        if self._platform == "Windows":
            self._initialize_windows_server()
        else:
            self._initialize_unix_server()

    def _initialize_windows_server(self):
        """初始化Windows Named Pipe服务器"""
        try:
            from .windows_named_pipe import WindowsNamedPipeServer

            pipe_name = self.pipe_name or "linch-mind-ipc"
            self._server = WindowsNamedPipeServer(pipe_name, self.max_clients)
            logger.info(f"初始化Windows Named Pipe服务器: {pipe_name}")

        except ImportError as e:
            logger.error(f"Windows Named Pipe服务器不可用: {e}")
            raise RuntimeError("Windows平台IPC服务器初始化失败")

    def _initialize_unix_server(self):
        """初始化Unix Socket服务器"""
        try:
            from .ipc_server import IPCServer

            socket_path = self.socket_path or "/tmp/linch-mind-ipc.sock"
            self._server = IPCServer(socket_path=socket_path)
            logger.info(f"初始化Unix Socket服务器: {socket_path}")

        except ImportError as e:
            logger.error(f"Unix Socket服务器不可用: {e}")
            raise RuntimeError("Unix平台IPC服务器初始化失败")

    async def start(self):
        """启动跨平台IPC服务器"""
        if not self._server:
            raise RuntimeError("IPC服务器未正确初始化")

        logger.info(f"启动{self._platform}平台IPC服务器...")
        await self._server.start()
        logger.info(f"{self._platform}平台IPC服务器启动成功")

    async def stop(self):
        """停止跨平台IPC服务器"""
        if not self._server:
            return

        logger.info(f"停止{self._platform}平台IPC服务器...")
        await self._server.stop()
        logger.info(f"{self._platform}平台IPC服务器已停止")

    def set_ipc_app(self, app):
        """设置IPC应用实例"""
        if not self._server:
            raise RuntimeError("IPC服务器未正确初始化")

        self._server.set_ipc_app(app)
        logger.info("IPC应用实例已设置")

    def get_stats(self) -> Dict[str, Any]:
        """获取服务器统计信息"""
        if not self._server:
            return {"error": "服务器未初始化"}

        base_stats = {
            "platform": self._platform,
            "socket_path": self.socket_path,
            "pipe_name": self.pipe_name,
            "max_clients": self.max_clients,
        }

        server_stats = self._server.get_stats()
        return {**base_stats, **server_stats}

    def get_connection_info(self) -> Dict[str, Any]:
        """获取连接信息"""
        if self._platform == "Windows":
            return {
                "type": "named_pipe",
                "pipe_name": self.pipe_name,
                "full_path": f"\\\\.\\pipe\\{self.pipe_name}",
            }
        else:
            return {"type": "unix_socket", "socket_path": self.socket_path}


class CrossPlatformIPCClient:
    """跨平台IPC客户端统一接口"""

    def __init__(
        self,
        socket_path: Optional[str] = None,
        pipe_name: Optional[str] = None,
        timeout: int = 30,
    ):
        self.socket_path = socket_path
        self.pipe_name = pipe_name
        self.timeout = timeout
        self._client: Optional[IPCClientProtocol] = None
        self._platform = platform.system()
        self._connected = False

        # 根据平台选择实现
        self._initialize_platform_client()

    def _initialize_platform_client(self):
        """根据平台初始化相应的客户端实现"""
        if self._platform == "Windows":
            self._initialize_windows_client()
        else:
            self._initialize_unix_client()

    def _initialize_windows_client(self):
        """初始化Windows Named Pipe客户端"""
        try:
            from .windows_named_pipe_client import WindowsNamedPipeClient

            pipe_name = self.pipe_name or "linch-mind-ipc"
            self._client = WindowsNamedPipeClient(pipe_name, self.timeout)
            logger.debug(f"初始化Windows Named Pipe客户端: {pipe_name}")

        except ImportError as e:
            logger.error(f"Windows Named Pipe客户端不可用: {e}")
            raise RuntimeError("Windows平台IPC客户端初始化失败")

    def _initialize_unix_client(self):
        """初始化Unix Socket客户端"""
        try:
            from .ipc_client import IPCClient

            socket_path = self.socket_path or "/tmp/linch-mind-ipc.sock"
            self._client = IPCClient(socket_path, self.timeout)
            logger.debug(f"初始化Unix Socket客户端: {socket_path}")

        except ImportError as e:
            logger.error(f"Unix Socket客户端不可用: {e}")
            raise RuntimeError("Unix平台IPC客户端初始化失败")

    def connect(self) -> bool:
        """连接到跨平台IPC服务器"""
        if not self._client:
            logger.error("IPC客户端未正确初始化")
            return False

        try:
            result = self._client.connect()
            self._connected = result

            if result:
                logger.info(f"已连接到{self._platform}平台IPC服务器")
            else:
                logger.error(f"连接{self._platform}平台IPC服务器失败")

            return result

        except Exception as e:
            logger.error(f"连接{self._platform}平台IPC服务器时出错: {e}")
            return False

    def send_request(
        self, method: str, path: str, data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """发送IPC请求并获取响应"""
        if not self._connected or not self._client:
            logger.error("未连接到IPC服务器")
            return None

        try:
            # 检查是否已有事件循环在运行
            try:
                loop = asyncio.get_running_loop()
                # 如果有循环在运行，创建任务
                task = loop.create_task(self._client.request(method, path, data=data))
                return loop.run_until_complete(task)
            except RuntimeError:
                # 没有运行中的循环，创建新的
                return asyncio.run(self._client.request(method, path, data=data))
        except Exception as e:
            logger.error(f"发送IPC请求时出错: {e}")
            return None

    def disconnect(self):
        """断开与跨平台IPC服务器的连接"""
        if self._client:
            try:
                # IPC客户端的disconnect是异步方法
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self._client.disconnect())
                finally:
                    loop.close()
                self._connected = False
                logger.info(f"已断开与{self._platform}平台IPC服务器的连接")
            except Exception as e:
                logger.error(f"断开连接时出错: {e}")

    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected

    def __enter__(self):
        """上下文管理器进入"""
        if self.connect():
            return self
        else:
            raise ConnectionError(f"无法连接到{self._platform}平台IPC服务器")

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.disconnect()


class IPCConnectionFactory:
    """IPC连接工厂类"""

    @staticmethod
    def create_server(
        socket_path: Optional[str] = None,
        pipe_name: Optional[str] = None,
        max_clients: int = 10,
    ) -> CrossPlatformIPCServer:
        """创建跨平台IPC服务器"""
        return CrossPlatformIPCServer(socket_path, pipe_name, max_clients)

    @staticmethod
    def create_client(
        socket_path: Optional[str] = None,
        pipe_name: Optional[str] = None,
        timeout: int = 30,
    ) -> CrossPlatformIPCClient:
        """创建跨平台IPC客户端"""
        return CrossPlatformIPCClient(socket_path, pipe_name, timeout)

    @staticmethod
    def get_default_connection_params() -> Dict[str, Any]:
        """获取默认连接参数"""
        if platform.system() == "Windows":
            return {"pipe_name": "linch-mind-ipc", "type": "named_pipe"}
        else:
            return {"socket_path": "/tmp/linch-mind-ipc.sock", "type": "unix_socket"}

    @staticmethod
    def detect_available_servers() -> list:
        """检测可用的IPC服务器"""
        available = []

        if platform.system() == "Windows":
            # 检测Windows Named Pipe
            try:
                import win32file

                pipe_name = r"\\.\pipe\linch-mind-ipc"
                try:
                    handle = win32file.CreateFile(
                        pipe_name,
                        win32file.GENERIC_READ,
                        0,
                        None,
                        win32file.OPEN_EXISTING,
                        0,
                        None,
                    )
                    if handle != win32file.INVALID_HANDLE_VALUE:
                        win32file.CloseHandle(handle)
                        available.append(
                            {
                                "type": "named_pipe",
                                "pipe_name": "linch-mind-ipc",
                                "available": True,
                            }
                        )
                except (OSError, RuntimeError) as e:
                    logger.debug(f"检查Named Pipe可用性失败: {e}")
            except ImportError:
                pass
        else:
            # 检测Unix Socket
            import socket

            socket_path = "/tmp/linch-mind-ipc.sock"

            try:
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.settimeout(1.0)
                result = sock.connect_ex(socket_path)
                sock.close()

                if result == 0:
                    available.append(
                        {
                            "type": "unix_socket",
                            "socket_path": socket_path,
                            "available": True,
                        }
                    )
            except (OSError, PermissionError) as e:
                logger.debug(f"检查Unix Socket可用性失败: {e}")

        return available


# 便捷函数
def create_ipc_server(**kwargs) -> CrossPlatformIPCServer:
    """创建IPC服务器的便捷函数"""
    return IPCConnectionFactory.create_server(**kwargs)


def create_ipc_client(**kwargs) -> CrossPlatformIPCClient:
    """创建IPC客户端的便捷函数"""
    return IPCConnectionFactory.create_client(**kwargs)


async def test_cross_platform_ipc():
    """测试跨平台IPC功能"""
    logger.info("开始跨平台IPC测试")

    # 获取默认连接参数
    conn_params = IPCConnectionFactory.get_default_connection_params()
    logger.info(f"使用连接参数: {conn_params}")

    # 检测可用服务器
    available_servers = IPCConnectionFactory.detect_available_servers()
    logger.info(f"发现可用IPC服务器: {available_servers}")

    if not available_servers:
        logger.warning("未找到可用的IPC服务器")
        return False

    # 测试客户端连接
    try:
        client = create_ipc_client(**conn_params)

        with client:
            # 发送测试请求
            response = client.send_request("GET", "/health")
            if response:
                logger.info(f"测试请求响应: {response}")
                return True
            else:
                logger.error("测试请求失败")
                return False

    except Exception as e:
        logger.error(f"跨平台IPC测试失败: {e}")
        return False


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # 运行测试
    result = asyncio.run(test_cross_platform_ipc())
    exit(0 if result else 1)
