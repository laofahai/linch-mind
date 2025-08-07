"""
IPC客户端库 - 提供与IPC服务器通信的客户端接口
用于替代HTTP客户端，保持API兼容性
"""

import asyncio
import json
import logging
import os
import platform
import socket
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class IPCConnectionError(Exception):
    """IPC连接错误"""
    pass


class IPCTimeoutError(Exception):
    """IPC超时错误"""
    pass


class IPCClient:
    """IPC客户端"""
    
    def __init__(self, socket_path: Optional[str] = None, timeout: float = 30.0):
        self.socket_path = socket_path
        self.timeout = timeout
        self.reader = None
        self.writer = None
        
    async def connect(self):
        """连接到IPC服务器并自动认证（内部客户端）"""
        if not self.socket_path:
            # 自动发现socket路径
            self.socket_path = await self._discover_socket_path()
        
        if platform.system() == 'Windows':
            raise NotImplementedError("Windows Named Pipe support not implemented yet")
        else:
            await self._connect_unix_socket()
            # 内部客户端自动进行认证握手
            await self._perform_internal_authentication()
    
    async def _discover_socket_path(self) -> str:
        """自动发现socket路径"""
        # 尝试从配置文件读取
        try:
            from api.dependencies import get_config_manager
            config_manager = get_config_manager()
            
            # 检查daemon.socket文件
            socket_file = config_manager.get_paths()["app_data"] / "daemon.socket"
            if socket_file.exists():
                with open(socket_file, 'r') as f:
                    socket_info = json.load(f)
                    if socket_info.get('type') == 'unix_socket':
                        return socket_info['path']
            
            # 检查daemon.port文件（兼容性）
            port_file = config_manager.get_paths()["app_data"] / "daemon.port"
            if port_file.exists():
                with open(port_file, 'r') as f:
                    content = f.read().strip()
                    if content.startswith('0:'):  # port=0表示IPC模式
                        pid = content.split(':')[1]
                        # 构造socket路径
                        import tempfile
                        return os.path.join(tempfile.gettempdir(), f"linch-mind-{pid}.sock")
            
            raise IPCConnectionError("Could not discover IPC socket path")
            
        except Exception as e:
            raise IPCConnectionError(f"Failed to discover socket path: {e}")
    
    async def _connect_unix_socket(self):
        """连接Unix Domain Socket"""
        try:
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_unix_connection(self.socket_path),
                timeout=self.timeout
            )
            logger.debug(f"Connected to IPC server: {self.socket_path}")
        except asyncio.TimeoutError:
            raise IPCTimeoutError(f"Connection timeout to {self.socket_path}")
        except Exception as e:
            raise IPCConnectionError(f"Failed to connect to {self.socket_path}: {e}")
    
    async def disconnect(self):
        """断开连接"""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            self.reader = None
            self.writer = None
    
    async def request(self, method: str, path: str, data: Optional[Dict[str, Any]] = None,
                     headers: Optional[Dict[str, str]] = None, 
                     query_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送IPC请求"""
        if not self.writer:
            await self.connect()
        
        # 添加客户端进程ID到headers
        if not headers:
            headers = {}
        headers['x-client-pid'] = str(os.getpid())
        
        # 构造请求消息
        message = {
            'method': method.upper(),
            'path': path,
            'data': data or {},
            'headers': headers,
            'query_params': query_params or {}
        }
        
        # 发送请求
        try:
            await self._send_message(message)
            response = await self._receive_response()
            return response
        except Exception as e:
            # 连接可能断开，尝试重连一次
            logger.warning(f"IPC request failed, trying to reconnect: {e}")
            await self.disconnect()
            await self.connect()
            await self._send_message(message)
            response = await self._receive_response()
            return response
    
    async def _send_message(self, message: Dict[str, Any]):
        """发送消息到服务器"""
        message_json = json.dumps(message)
        message_bytes = message_json.encode('utf-8')
        
        # 发送消息长度前缀
        length_bytes = len(message_bytes).to_bytes(4, byteorder='big')
        self.writer.write(length_bytes)
        
        # 发送消息内容
        self.writer.write(message_bytes)
        await self.writer.drain()
    
    async def _receive_response(self) -> Dict[str, Any]:
        """接收服务器响应"""
        try:
            # 读取响应长度
            length_data = await asyncio.wait_for(
                self.reader.readexactly(4), 
                timeout=self.timeout
            )
            response_length = int.from_bytes(length_data, byteorder='big')
            
            # 读取响应内容
            response_data = await asyncio.wait_for(
                self.reader.readexactly(response_length),
                timeout=self.timeout
            )
            
            response_str = response_data.decode('utf-8')
            return json.loads(response_str)
            
        except asyncio.TimeoutError:
            raise IPCTimeoutError("Response timeout")
        except asyncio.IncompleteReadError:
            raise IPCConnectionError("Connection closed by server")
        except json.JSONDecodeError as e:
            raise IPCConnectionError(f"Invalid response format: {e}")
    
    async def _perform_internal_authentication(self):
        """内部客户端自动认证握手"""
        try:
            # 构造认证消息
            auth_message = {
                'method': 'POST',
                'path': '/auth/handshake',
                'data': {
                    'client_pid': os.getpid(),
                    'client_type': 'internal_daemon_client'
                },
                'headers': {
                    'x-client-pid': str(os.getpid()),
                    'x-internal-client': 'true'
                },
                'query_params': {}
            }
            
            # 发送认证请求
            await self._send_message(auth_message)
            response = await self._receive_response()
            
            if response.get('status_code') == 200:
                logger.info("内部客户端认证成功")
            else:
                error = response.get('data', {}).get('error', 'Unknown error')
                logger.error(f"内部客户端认证失败: {error}")
                raise IPCConnectionError(f"Authentication failed: {error}")
                
        except Exception as e:
            logger.error(f"内部客户端认证过程失败: {e}")
            raise IPCConnectionError(f"Internal authentication failed: {e}")
    
    # HTTP风格的便捷方法
    async def get(self, path: str, params: Optional[Dict[str, Any]] = None, 
                 headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """GET请求"""
        # 为daemon内部请求添加认证头部
        if not headers:
            headers = {}
        headers['x-client-pid'] = str(os.getpid())
        headers['x-internal-client'] = 'true'
        return await self.request('GET', path, query_params=params, headers=headers)
    
    async def post(self, path: str, data: Optional[Dict[str, Any]] = None,
                  headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """POST请求"""
        # 为daemon内部请求添加认证头部
        if not headers:
            headers = {}
        headers['x-client-pid'] = str(os.getpid())
        headers['x-internal-client'] = 'true'
        return await self.request('POST', path, data=data, headers=headers)
    
    async def put(self, path: str, data: Optional[Dict[str, Any]] = None,
                 headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """PUT请求"""
        # 为daemon内部请求添加认证头部
        if not headers:
            headers = {}
        headers['x-client-pid'] = str(os.getpid())
        headers['x-internal-client'] = 'true'
        return await self.request('PUT', path, data=data, headers=headers)
    
    async def delete(self, path: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """DELETE请求"""
        # 为daemon内部请求添加认证头部
        if not headers:
            headers = {}
        headers['x-client-pid'] = str(os.getpid())
        headers['x-internal-client'] = 'true'
        return await self.request('DELETE', path, headers=headers)
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.disconnect()


class IPCClientSession:
    """IPC客户端会话 - 保持连接的长期会话"""
    
    def __init__(self, timeout: float = 30.0):
        self.client = IPCClient(timeout=timeout)
        self._connected = False
    
    async def start(self):
        """启动会话"""
        if not self._connected:
            await self.client.connect()
            self._connected = True
    
    async def stop(self):
        """停止会话"""
        if self._connected:
            await self.client.disconnect()
            self._connected = False
    
    async def request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """发送请求"""
        if not self._connected:
            await self.start()
        return await self.client.request(method, path, **kwargs)
    
    async def get(self, path: str, **kwargs) -> Dict[str, Any]:
        """GET请求"""
        return await self.request('GET', path, **kwargs)
    
    async def post(self, path: str, **kwargs) -> Dict[str, Any]:
        """POST请求"""
        return await self.request('POST', path, **kwargs)
    
    async def put(self, path: str, **kwargs) -> Dict[str, Any]:
        """PUT请求"""
        return await self.request('PUT', path, **kwargs)
    
    async def delete(self, path: str, **kwargs) -> Dict[str, Any]:
        """DELETE请求"""
        return await self.request('DELETE', path, **kwargs)


# 全局客户端会话实例
_global_session: Optional[IPCClientSession] = None


async def get_ipc_client() -> IPCClientSession:
    """获取全局IPC客户端会话"""
    global _global_session
    if _global_session is None:
        _global_session = IPCClientSession()
    
    if not _global_session._connected:
        await _global_session.start()
    
    return _global_session


async def cleanup_ipc_client():
    """清理全局IPC客户端"""
    global _global_session
    if _global_session:
        await _global_session.stop()
        _global_session = None


# 便捷的全局函数
async def ipc_get(path: str, **kwargs) -> Dict[str, Any]:
    """全局GET请求"""
    client = await get_ipc_client()
    return await client.get(path, **kwargs)


async def ipc_post(path: str, **kwargs) -> Dict[str, Any]:
    """全局POST请求"""
    client = await get_ipc_client()
    return await client.post(path, **kwargs)


async def ipc_put(path: str, **kwargs) -> Dict[str, Any]:
    """全局PUT请求"""
    client = await get_ipc_client()
    return await client.put(path, **kwargs)


async def ipc_delete(path: str, **kwargs) -> Dict[str, Any]:
    """全局DELETE请求"""
    client = await get_ipc_client()
    return await client.delete(path, **kwargs)