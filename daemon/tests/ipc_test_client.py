#!/usr/bin/env python3
"""
IPC测试客户端 - 用于纯IPC架构的测试支持
提供模拟daemon和测试客户端功能
"""

import asyncio
import json
import socket
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from services.ipc_protocol import IPCRequest, IPCResponse
from services.ipc_router import IPCRouter


class IPCTestClient:
    """IPC测试客户端"""

    def __init__(self, socket_path: str):
        self.socket_path = socket_path
        self.socket: Optional[socket.socket] = None

    async def connect(self) -> bool:
        """连接到IPC socket"""
        try:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.connect(self.socket_path)
            return True
        except Exception:
            return False

    async def send_message(
        self, method: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """发送IPC消息"""
        if not self.socket:
            raise RuntimeError("Not connected to IPC server")

        message = IPCRequest(
            method="POST",  # HTTP方法
            path=f"/{method}",  # 路径
            data=params or {},  # 数据负载
            request_id="test_request_" + str(asyncio.get_event_loop().time()),
        )

        # 发送消息
        data = json.dumps(message.to_dict()).encode()
        self.socket.sendall(len(data).to_bytes(4, "big"))
        self.socket.sendall(data)

        # 接收响应
        length_bytes = self.socket.recv(4)
        if not length_bytes:
            raise RuntimeError("Connection closed")

        length = int.from_bytes(length_bytes, "big")
        response_data = self.socket.recv(length)

        return json.loads(response_data.decode())

    def close(self):
        """关闭连接"""
        if self.socket:
            self.socket.close()
            self.socket = None


class MockIPCDaemon:
    """模拟IPC daemon用于测试"""

    def __init__(self, socket_path: str):
        self.socket_path = socket_path
        self.socket: Optional[socket.socket] = None
        self.router = IPCRouter()
        self.running = False

    def register_route(self, method: str, handler):
        """注册路由处理器"""
        self.router.register_route(method, handler)

    async def start(self):
        """启动模拟daemon"""
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            # 清理可能存在的socket文件
            Path(self.socket_path).unlink(missing_ok=True)
            self.socket.bind(self.socket_path)
            self.socket.listen(1)
            self.running = True
        except Exception as e:
            raise RuntimeError(f"Failed to start mock daemon: {e}")

    def stop(self):
        """停止模拟daemon"""
        self.running = False
        if self.socket:
            self.socket.close()
            self.socket = None
        Path(self.socket_path).unlink(missing_ok=True)

    async def handle_client(self, client_socket: socket.socket):
        """处理客户端连接"""
        try:
            while self.running:
                # 接收消息长度
                length_bytes = client_socket.recv(4)
                if not length_bytes:
                    break

                length = int.from_bytes(length_bytes, "big")
                data = client_socket.recv(length)

                if not data:
                    break

                # 解析消息
                message_data = json.loads(data.decode())
                message = IPCRequest.from_dict(message_data)

                # 路由处理
                try:
                    result = await self.router.handle_request(
                        message.method, message.params
                    )
                    response = IPCResponse.success_response(
                        data=result, request_id=message.request_id
                    )
                except Exception as e:
                    response = IPCResponse.error_response(
                        error_code="INTERNAL_ERROR",
                        message=str(e),
                        request_id=message.request_id,
                    )

                # 发送响应
                response_data = json.dumps(response.to_dict()).encode()
                client_socket.sendall(len(response_data).to_bytes(4, "big"))
                client_socket.sendall(response_data)

        except Exception:
            pass
        finally:
            client_socket.close()


def create_mock_daemon_with_routes() -> Tuple[MockIPCDaemon, str]:
    """创建带有模拟路由的daemon"""
    temp_dir = tempfile.mkdtemp()
    socket_path = str(Path(temp_dir) / "test_daemon.sock")

    daemon = MockIPCDaemon(socket_path)

    # 注册模拟路由
    async def mock_health(params: Dict[str, Any]):
        return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

    async def mock_connector_list(params: Dict[str, Any]):
        return {
            "connectors": [
                {
                    "connector_id": "filesystem",
                    "name": "FileSystem Connector",
                    "status": "running",
                    "pid": 1234,
                }
            ]
        }

    async def mock_connector_start(params: Dict[str, Any]):
        connector_id = params.get("connector_id")
        return {"success": True, "connector_id": connector_id, "pid": 1234}

    async def mock_connector_stop(params: Dict[str, Any]):
        connector_id = params.get("connector_id")
        return {"success": True, "connector_id": connector_id}

    async def mock_system_config_get(params: Dict[str, Any]):
        return {"daemon_port": 58471, "log_level": "INFO", "max_connections": 100}

    async def mock_system_config_update(params: Dict[str, Any]):
        return {"success": True, "updated_config": params.get("config", {})}

    # 注册所有模拟路由
    daemon.register_route("health.check", mock_health)
    daemon.register_route("connector.list", mock_connector_list)
    daemon.register_route("connector.start", mock_connector_start)
    daemon.register_route("connector.stop", mock_connector_stop)
    daemon.register_route("system_config.get", mock_system_config_get)
    daemon.register_route("system_config.update", mock_system_config_update)

    return daemon, socket_path


# 测试工具函数
async def create_test_ipc_environment() -> Tuple[MockIPCDaemon, IPCTestClient]:
    """创建完整的测试IPC环境"""
    daemon, socket_path = create_mock_daemon_with_routes()
    await daemon.start()

    client = IPCTestClient(socket_path)
    await client.connect()

    return daemon, client


def create_mock_ipc_response(
    success: bool = True, data: Any = None, error: str = None
) -> Dict[str, Any]:
    """创建模拟IPC响应"""
    if success:
        response = IPCResponse.success_response(data=data, request_id="test_request")
    else:
        response = IPCResponse.error_response(
            error_code="TEST_ERROR",
            message=error or "Test error",
            request_id="test_request",
        )
    return response.to_dict()
