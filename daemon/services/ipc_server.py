"""
IPC服务器 - 完全独立的IPC通信系统
不依赖FastAPI，提供纯IPC的本地进程间通信
"""

import asyncio
import json
import logging
import os
import platform
import socket
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Union
import stat

from .ipc_router import IPCApplication
from .ipc_middleware import create_default_middlewares
from .ipc_routes import register_all_routes

logger = logging.getLogger(__name__)


class IPCMessage:
    """IPC消息格式定义"""
    
    def __init__(self, method: str, path: str, data: Optional[Dict[str, Any]] = None, 
                 headers: Optional[Dict[str, str]] = None, query_params: Optional[Dict[str, Any]] = None):
        self.method = method.upper()
        self.path = path
        self.data = data or {}
        self.headers = headers or {}
        self.query_params = query_params or {}
    
    def to_json(self) -> str:
        """序列化为JSON字符串"""
        return json.dumps({
            'method': self.method,
            'path': self.path,
            'data': self.data,
            'headers': self.headers,
            'query_params': self.query_params
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'IPCMessage':
        """从JSON字符串反序列化"""
        data = json.loads(json_str)
        return cls(
            method=data['method'],
            path=data['path'],
            data=data.get('data'),
            headers=data.get('headers'),
            query_params=data.get('query_params')
        )


class IPCServer:
    """纯IPC服务器 - 完全独立于FastAPI"""
    
    def __init__(self, socket_path: Optional[str] = None, pipe_name: Optional[str] = None):
        self.socket_path = socket_path
        self.pipe_name = pipe_name
        self.server = None
        self.is_running = False
        self.clients = set()
        
        # 使用纯IPC应用实例
        self.app = IPCApplication()
        
        # 添加默认中间件
        for middleware in create_default_middlewares(debug=False):
            self.app.add_middleware(middleware)
        
        # 注册所有路由
        register_all_routes(self.app)
        
        logger.info("IPC应用已初始化，所有路由和中间件已加载")
        
    async def start(self):
        """启动IPC服务器"""
        if platform.system() == 'Windows':
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
        
        # 创建Unix socket服务器
        self.server = await asyncio.start_unix_server(
            self._handle_client,
            path=self.socket_path
        )
        
        # 设置socket文件权限为仅owner可访问
        os.chmod(self.socket_path, stat.S_IRUSR | stat.S_IWUSR)
        
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
        from api.dependencies import get_config_manager
        
        config_manager = get_config_manager()
        
        # 准备socket信息
        socket_info = {
            'type': 'unix_socket' if platform.system() != 'Windows' else 'named_pipe',
            'path': self.socket_path if self.socket_path else f"\\\\.\\pipe\\{self.pipe_name}",
            'pid': os.getpid(),
            'protocol': 'ipc'
        }
        
        # 写入主要的socket配置文件
        socket_file = config_manager.get_paths()["app_data"] / "daemon.socket"
        with open(socket_file, 'w') as f:
            json.dump(socket_info, f, indent=2)
        
        # 设置文件权限
        if platform.system() != 'Windows':
            os.chmod(socket_file, stat.S_IRUSR | stat.S_IWUSR)
        
        logger.info(f"Socket信息已写入: {socket_file}")
        
        # 向后兼容：同时写入daemon.port文件（供现有客户端使用）
        # 使用特殊端口0表示IPC模式
        port_file = config_manager.get_paths()["app_data"] / "daemon.port"
        try:
            with open(port_file, 'w') as f:
                f.write(f"0:{os.getpid()}")
            
            if platform.system() != 'Windows':
                os.chmod(port_file, stat.S_IRUSR | stat.S_IWUSR)
            
            logger.info(f"兼容性端口文件已写入: {port_file} (port=0表示IPC模式)")
        except Exception as e:
            logger.warning(f"写入兼容性端口文件失败: {e}")
        
    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """处理客户端连接"""
        client_addr = writer.get_extra_info('peername')
        logger.debug(f"新的IPC连接: {client_addr}")
        
        self.clients.add(writer)
        
        try:
            while True:
                # 读取消息长度前缀 (4字节)
                length_data = await reader.readexactly(4)
                if not length_data:
                    break
                    
                message_length = int.from_bytes(length_data, byteorder='big')
                
                # 读取完整消息
                message_data = await reader.readexactly(message_length)
                message_str = message_data.decode('utf-8')
                
                # 解析IPC消息
                try:
                    ipc_message = IPCMessage.from_json(message_str)
                    logger.debug(f"收到IPC请求: {ipc_message.method} {ipc_message.path}")
                    
                    # 处理消息
                    response = await self._process_message(ipc_message)
                    
                    # 发送响应
                    await self._send_response(writer, response)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"IPC消息JSON解析失败: {e}")
                    error_response = {
                        'status_code': 400, 
                        'data': {'error': 'Invalid JSON format'},
                        'headers': {}
                    }
                    await self._send_response(writer, error_response)
                    
                except Exception as e:
                    logger.error(f"处理IPC消息时出错: {e}")
                    error_response = {
                        'status_code': 500,
                        'data': {'error': str(e)},
                        'headers': {}
                    }
                    await self._send_response(writer, error_response)
                    
        except asyncio.IncompleteReadError:
            logger.debug(f"IPC客户端断开连接: {client_addr}")
        except Exception as e:
            logger.error(f"IPC连接处理出错: {e}")
        finally:
            self.clients.discard(writer)
            writer.close()
            await writer.wait_closed()
            
    async def _process_message(self, message: IPCMessage) -> Dict[str, Any]:
        """处理IPC消息，使用纯IPC应用"""
        if not self.app:
            return {
                'status_code': 500,
                'data': {'error': 'IPC app not configured'},
                'headers': {}
            }
        
        try:
            # 直接使用IPC应用处理请求
            response = await self.app.handle_request(
                method=message.method,
                path=message.path,
                data=message.data,
                headers=message.headers,
                query_params=message.query_params
            )
            
            return response.to_dict()
            
        except Exception as e:
            logger.error(f"IPC应用处理请求失败: {e}")
            return {
                'status_code': 500,
                'data': {'error': f'Internal server error: {str(e)}'},
                'headers': {}
            }
    
    async def _send_response(self, writer: asyncio.StreamWriter, response: Dict[str, Any]):
        """发送响应到客户端"""
        response_json = json.dumps(response)
        response_bytes = response_json.encode('utf-8')
        
        # 发送消息长度前缀
        length_bytes = len(response_bytes).to_bytes(4, byteorder='big')
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
        from api.dependencies import get_config_manager
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