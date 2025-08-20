#!/usr/bin/env python3
"""
IPC测试客户端 - 用于测试IPC通信
提供模拟的IPC服务器和测试客户端功能
"""

import asyncio
import json
import socket
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from unittest.mock import AsyncMock, Mock

from services.ipc.core.server import IPCServer


class IPCTestClient:
    """IPC测试客户端"""

    def __init__(self, socket_path: str):
        self.socket_path = socket_path
        self.connected = False

    async def connect(self):
        """连接到IPC服务器"""
        # 这是一个测试客户端，connect方法主要用于测试兼容性
        self.connected = True
        return True

    async def disconnect(self):
        """断开连接"""
        self.connected = False

    async def close(self):
        """关闭客户端连接"""
        await self.disconnect()
        
    async def send_message(self, message: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """发送消息（兼容接口）"""
        return await self.send_request(message, data)

    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """发送IPC请求"""
        try:
            # 连接到Unix socket
            reader, writer = await asyncio.open_unix_connection(self.socket_path)
            
            # 准备请求数据
            request_data = {
                "method": method,
                "params": params or {},
                "id": 1
            }
            
            # 发送请求
            request_json = json.dumps(request_data) + "\n"
            writer.write(request_json.encode())
            await writer.drain()
            
            # 读取响应
            response_line = await reader.readline()
            response_data = json.loads(response_line.decode().strip())
            
            # 关闭连接
            writer.close()
            await writer.wait_closed()
            
            return response_data
            
        except Exception as e:
            return {"error": str(e), "success": False}

    async def get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """模拟GET请求"""
        return await self.send_request(f"GET:{endpoint}", params)

    async def post(self, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """模拟POST请求"""
        return await self.send_request(f"POST:{endpoint}", data)

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return await self.send_request("health_check")


def create_mock_daemon_with_routes() -> Tuple[Mock, str]:
    """创建带路由的模拟daemon"""
    # 创建临时socket路径
    temp_dir = tempfile.mkdtemp()
    socket_path = str(Path(temp_dir) / "test_ipc.sock")
    
    # 创建模拟的IPC服务器
    mock_daemon = Mock()
    mock_daemon.socket_path = socket_path
    mock_daemon.is_running = True
    
    # 模拟启动和停止方法
    mock_daemon.start = AsyncMock()
    mock_daemon.stop = AsyncMock()
    mock_daemon.cleanup = AsyncMock()
    
    # 模拟服务器配置
    mock_daemon.server = Mock()
    mock_daemon.server.socket_path = socket_path
    
    return mock_daemon, socket_path


class MockIPCServer:
    """模拟IPC服务器用于测试"""
    
    def __init__(self, socket_path: str):
        self.socket_path = socket_path
        self.is_running = False
        self.server = None
        
    async def start(self):
        """启动模拟服务器"""
        self.server = await asyncio.start_unix_server(
            self.handle_client, 
            self.socket_path
        )
        self.is_running = True
        
    async def stop(self):
        """停止模拟服务器"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        self.is_running = False
        
    async def handle_client(self, reader, writer):
        """处理客户端连接"""
        try:
            # 读取请求
            request_line = await reader.readline()
            request_data = json.loads(request_line.decode().strip())
            
            # 模拟处理
            method = request_data.get("method", "")
            params = request_data.get("params", {})
            
            # 根据方法返回模拟响应
            if method == "health_check":
                response = {"success": True, "status": "healthy"}
            elif method.startswith("GET:"):
                response = {"success": True, "data": {"message": "Mock GET response"}}
            elif method.startswith("POST:"):
                response = {"success": True, "data": {"message": "Mock POST response"}}
            else:
                response = {"success": False, "error": "Unknown method"}
            
            # 发送响应
            response_json = json.dumps(response) + "\n"
            writer.write(response_json.encode())
            await writer.drain()
            
        except Exception as e:
            # 发送错误响应
            error_response = {"success": False, "error": str(e)}
            response_json = json.dumps(error_response) + "\n"
            writer.write(response_json.encode())
            await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()


async def create_test_ipc_server(socket_path: str) -> MockIPCServer:
    """创建测试用IPC服务器"""
    server = MockIPCServer(socket_path)
    await server.start()
    return server