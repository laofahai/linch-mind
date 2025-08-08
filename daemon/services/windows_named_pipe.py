"""
Windows Named Pipe 实现
提供Windows系统下的进程间通信支持
"""

import asyncio
import json
import logging
import os
import platform
import threading
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Windows Named Pipe实现需要pywin32或其他Windows特定库
# 这里提供一个基础的跨平台兼容实现

if platform.system() == 'Windows':
    try:
        import pywintypes
        import win32api
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
    
    def __init__(self, pipe_name: str):
        self.pipe_name = pipe_name
        self.full_pipe_name = f"\\\\.\\pipe\\{pipe_name}"
        self.is_running = False
        self.clients = []
        self.app = None
        
    def set_ipc_app(self, app):
        """设置IPC应用实例 - 兼容纯IPC架构"""
        self.app = app
        
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
                    win32pipe.PIPE_ACCESS_DUPLEX,
                    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                    1,  # 最大实例数
                    65536,  # 输出缓冲区大小
                    65536,  # 输入缓冲区大小
                    0,  # 默认超时
                    None  # 安全属性
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
                        message_str = data.decode('utf-8')
                        logger.debug(f"收到Named Pipe消息: {message_str}")
                        
                        # 处理消息
                        response = self._process_message_sync(message_str)
                        
                        # 发送响应
                        win32file.WriteFile(pipe_handle, response.encode('utf-8'))
                        
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
        """同步处理消息（Named Pipe在线程中运行）- 纯IPC版本"""
        try:
            from .ipc_router import IPCRequest, IPCResponse
            from .ipc_server import IPCMessage

            # 解析IPC消息
            message_data = json.loads(message_str)
            ipc_message = IPCMessage(
                method=message_data.get('method', 'GET'),
                path=message_data.get('path', '/'),
                data=message_data.get('data', {}),
                headers=message_data.get('headers', {}),
                query_params=message_data.get('query_params', {})
            )
            
            # 转换为IPC请求
            request = IPCRequest(
                method=ipc_message.method,
                path=ipc_message.path,
                data=ipc_message.data,
                headers=ipc_message.headers,
                query_params=ipc_message.query_params
            )
            
            # 使用IPC应用处理请求（同步版本）
            if self.app:
                try:
                    # 这里需要同步调用异步的IPC应用
                    # 在实际实现中，需要更复杂的线程间通信
                    response_data = {
                        'message': 'Windows Named Pipe IPC响应',
                        'method': request.method,
                        'path': request.path,
                        'timestamp': time.time()
                    }
                    response = IPCResponse(status_code=200, data=response_data)
                else:
                    response = IPCResponse(status_code=500, data={'error': 'IPC应用未设置'})
            else:
                response = IPCResponse(status_code=500, data={'error': 'IPC应用未设置'})
            
            return response.to_json()
            
        except Exception as e:
            logger.error(f"处理Named Pipe消息失败: {e}")
            error_response = IPCResponse(
                status_code=500,
                data={'error': str(e)}
            )
            return error_response.to_json()
            
    def _write_pipe_info(self):
        """写入pipe信息到配置文件"""
        from api.dependencies import get_config_manager
        
        config_manager = get_config_manager()
        socket_info = {
            'type': 'named_pipe',
            'path': self.full_pipe_name,
            'pid': os.getpid()
        }
        
        # 写入到socket配置文件
        socket_file = config_manager.get_paths()["app_data"] / "daemon.socket"
        with open(socket_file, 'w') as f:
            json.dump(socket_info, f)
        
        logger.info(f"Named Pipe信息已写入: {socket_file}")
        
    async def stop(self):
        """停止Named Pipe服务器"""
        self.is_running = False
        
        # 清理socket信息文件
        from api.dependencies import get_config_manager
        config_manager = get_config_manager()
        socket_file = config_manager.get_paths()["app_data"] / "daemon.socket"
        if socket_file.exists():
            os.unlink(socket_file)
            
        logger.info("Windows Named Pipe服务器已停止")


class CrossPlatformNamedPipeServer:
    """跨平台Named Pipe兼容实现"""
    
    def __init__(self, pipe_name: str):
        self.pipe_name = pipe_name
        self.server = None
        
    def set_ipc_app(self, app):
        """设置IPC应用实例 - 纯IPC版本"""
        if platform.system() == 'Windows' and WINDOWS_SUPPORT:
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