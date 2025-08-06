#!/usr/bin/env python3
"""
Windows IPC服务器 - 使用Named Pipe的完整IPC实现
为Windows系统提供与Unix Socket等价的功能
"""

import asyncio
import json
import logging
import os
import platform
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, Set
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Windows特定导入
if platform.system() == 'Windows':
    try:
        import win32pipe
        import win32file
        import win32api
        import win32event
        import pywintypes
        import win32security
        WINDOWS_SUPPORT = True
        logger.info("✅ Windows Named Pipe支持已启用")
    except ImportError as e:
        WINDOWS_SUPPORT = False
        logger.error(f"❌ Windows Named Pipe支持不可用: {e}")
        logger.info("请安装pywin32库: pip install pywin32")
else:
    WINDOWS_SUPPORT = False


class WindowsIPCServer:
    """Windows IPC服务器 - 基于Named Pipe的完整实现"""
    
    def __init__(self, pipe_name: Optional[str] = None):
        self.pipe_name = pipe_name or f"linch-mind-{os.getpid()}"
        self.full_pipe_name = f"\\\\.\\pipe\\{self.pipe_name}"
        self.is_running = False
        self.clients: Set[int] = set()
        self.app = None
        self.security_manager = None
        
        # 线程池用于处理多个并发连接
        self.thread_pool = ThreadPoolExecutor(max_workers=10, thread_name_prefix="NamedPipe")
        
        # 消息队列用于异步通信
        self.request_queue = Queue()
        self.response_queues = {}
        
        # 安全设置
        self._setup_security()
    
    def _setup_security(self):
        """设置Named Pipe安全属性"""
        if not WINDOWS_SUPPORT:
            return
            
        try:
            # 创建安全描述符，只允许当前用户访问
            security_attributes = win32security.SECURITY_ATTRIBUTES()
            security_descriptor = win32security.SECURITY_DESCRIPTOR()
            
            # 获取当前用户SID
            current_user = win32api.GetUserName()
            user_sid, domain, account_type = win32security.LookupAccountName(None, current_user)
            
            # 创建DACL（访问控制列表）
            dacl = win32security.ACL()
            dacl.AddAccessAllowedAce(
                win32security.ACL_REVISION, 
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                user_sid
            )
            
            security_descriptor.SetSecurityDescriptorDacl(1, dacl, 0)
            security_attributes.SECURITY_DESCRIPTOR = security_descriptor
            
            self.security_attributes = security_attributes
            logger.info(f"Windows Named Pipe安全设置完成: 仅允许用户 {current_user} 访问")
            
        except Exception as e:
            logger.warning(f"设置Named Pipe安全属性失败，使用默认设置: {e}")
            self.security_attributes = None
    
    def set_ipc_app(self, app):
        """设置IPC应用实例"""
        self.app = app
        
    def set_security_manager(self, security_manager):
        """设置安全管理器"""
        self.security_manager = security_manager
    
    async def start(self):
        """启动Windows IPC服务器"""
        if not WINDOWS_SUPPORT:
            raise RuntimeError(
                "Windows Named Pipe需要pywin32库支持。"
                "请运行: pip install pywin32"
            )
        
        self.is_running = True
        
        # 在线程池中启动多个pipe实例
        for i in range(3):  # 允许3个并发连接
            pipe_instance_name = f"{self.pipe_name}-{i}"
            self.thread_pool.submit(self._run_pipe_instance, pipe_instance_name)
        
        # 启动消息处理循环
        asyncio.create_task(self._process_message_queue())
        
        # 写入pipe信息到配置文件
        self._write_pipe_info()
        
        logger.info(f"✅ Windows IPC服务器已启动: {self.full_pipe_name}")
    
    def _run_pipe_instance(self, instance_name: str):
        """运行单个Named Pipe实例"""
        full_instance_name = f"\\\\.\\pipe\\{instance_name}"
        
        while self.is_running:
            try:
                # 创建Named Pipe实例
                pipe_handle = win32pipe.CreateNamedPipe(
                    full_instance_name,
                    win32pipe.PIPE_ACCESS_DUPLEX | win32file.FILE_FLAG_OVERLAPPED,
                    (win32pipe.PIPE_TYPE_MESSAGE | 
                     win32pipe.PIPE_READMODE_MESSAGE | 
                     win32pipe.PIPE_WAIT),
                    win32pipe.PIPE_UNLIMITED_INSTANCES,
                    65536,  # 输出缓冲区大小
                    65536,  # 输入缓冲区大小
                    0,      # 默认超时
                    self.security_attributes  # 安全属性
                )
                
                if pipe_handle == win32file.INVALID_HANDLE_VALUE:
                    logger.error(f"创建Named Pipe实例失败: {instance_name}")
                    time.sleep(1)
                    continue
                
                # 等待客户端连接
                logger.debug(f"等待客户端连接: {instance_name}")
                
                # 创建重叠结构用于异步操作
                overlapped = pywintypes.OVERLAPPED()
                overlapped.hEvent = win32event.CreateEvent(None, 0, 0, None)
                
                # 异步等待连接
                win32pipe.ConnectNamedPipe(pipe_handle, overlapped)
                
                # 等待连接建立或超时
                result = win32event.WaitForSingleObject(overlapped.hEvent, 30000)  # 30秒超时
                
                if result == win32event.WAIT_OBJECT_0:
                    # 连接成功，处理客户端
                    logger.info(f"客户端已连接: {instance_name}")
                    self._handle_client(pipe_handle, instance_name)
                elif result == win32event.WAIT_TIMEOUT:
                    logger.debug(f"等待连接超时: {instance_name}")
                else:
                    logger.warning(f"等待连接失败: {instance_name}")
                
                # 断开并关闭pipe
                try:
                    win32pipe.DisconnectNamedPipe(pipe_handle)
                    win32file.CloseHandle(pipe_handle)
                    win32file.CloseHandle(overlapped.hEvent)
                except Exception as e:
                    logger.error(f"关闭pipe时出错: {e}")
                    
            except pywintypes.error as e:
                if self.is_running:
                    logger.error(f"Named Pipe实例 {instance_name} 错误: {e}")
                    time.sleep(1)
                    
            except Exception as e:
                if self.is_running:
                    logger.error(f"Named Pipe实例 {instance_name} 未知错误: {e}")
                    time.sleep(1)
    
    def _handle_client(self, pipe_handle, instance_name: str):
        """处理单个客户端连接"""
        client_id = f"{instance_name}-{int(time.time())}"
        self.clients.add(hash(client_id))
        
        try:
            while self.is_running:
                try:
                    # 读取消息长度前缀
                    length_data = self._read_exact(pipe_handle, 4)
                    if not length_data:
                        break
                    
                    message_length = int.from_bytes(length_data, byteorder='big')
                    
                    # 读取完整消息
                    message_data = self._read_exact(pipe_handle, message_length)
                    if not message_data:
                        break
                    
                    message_str = message_data.decode('utf-8')
                    logger.debug(f"收到Named Pipe消息 [{instance_name}]: {len(message_str)} bytes")
                    
                    # 将消息放入处理队列
                    response_queue = Queue()
                    self.response_queues[client_id] = response_queue
                    
                    self.request_queue.put({
                        'client_id': client_id,
                        'message': message_str,
                        'timestamp': time.time()
                    })
                    
                    # 等待响应（最多5秒）
                    try:
                        response = response_queue.get(timeout=5.0)
                        
                        # 发送响应
                        response_bytes = response.encode('utf-8')
                        length_bytes = len(response_bytes).to_bytes(4, byteorder='big')
                        
                        win32file.WriteFile(pipe_handle, length_bytes)
                        win32file.WriteFile(pipe_handle, response_bytes)
                        
                    except Empty:
                        logger.error(f"处理消息超时: {client_id}")
                        error_response = json.dumps({
                            'status_code': 408,
                            'data': {'error': 'Request timeout'},
                            'headers': {}
                        })
                        response_bytes = error_response.encode('utf-8')
                        length_bytes = len(response_bytes).to_bytes(4, byteorder='big')
                        
                        win32file.WriteFile(pipe_handle, length_bytes)
                        win32file.WriteFile(pipe_handle, response_bytes)
                    
                    # 清理响应队列
                    self.response_queues.pop(client_id, None)
                    
                except pywintypes.error as e:
                    if e.winerror == 109:  # ERROR_BROKEN_PIPE
                        logger.debug(f"客户端断开连接: {instance_name}")
                        break
                    else:
                        logger.error(f"Named Pipe通信错误: {e}")
                        break
                        
        except Exception as e:
            logger.error(f"处理Named Pipe客户端时出错 [{instance_name}]: {e}")
            
        finally:
            self.clients.discard(hash(client_id))
            self.response_queues.pop(client_id, None)
    
    def _read_exact(self, pipe_handle, num_bytes: int) -> bytes:
        """精确读取指定字节数"""
        data = b''
        while len(data) < num_bytes:
            try:
                result, chunk = win32file.ReadFile(pipe_handle, num_bytes - len(data))
                if result == 0:
                    data += chunk
                else:
                    break
            except pywintypes.error:
                break
        return data if len(data) == num_bytes else b''
    
    async def _process_message_queue(self):
        """处理消息队列"""
        while self.is_running:
            try:
                # 检查是否有待处理的请求
                try:
                    request_data = self.request_queue.get_nowait()
                except Empty:
                    await asyncio.sleep(0.01)  # 短暂等待
                    continue
                
                client_id = request_data['client_id']
                message_str = request_data['message']
                
                # 处理消息
                response = await self._process_ipc_message(message_str, client_id)
                
                # 将响应放入对应的响应队列
                response_queue = self.response_queues.get(client_id)
                if response_queue:
                    response_queue.put(response)
                
            except Exception as e:
                logger.error(f"处理消息队列时出错: {e}")
                await asyncio.sleep(0.1)
    
    async def _process_ipc_message(self, message_str: str, client_id: str) -> str:
        """处理IPC消息"""
        try:
            from .ipc_server import IPCMessage
            from .ipc_router import IPCRequest, IPCResponse
            
            # 解析消息
            message_data = json.loads(message_str)
            
            # 安全验证
            if self.security_manager:
                # 这里可以添加客户端验证逻辑
                pass
            
            # 创建IPC请求
            request = IPCRequest(
                method=message_data.get('method', 'GET'),
                path=message_data.get('path', '/'),
                data=message_data.get('data', {}),
                headers=message_data.get('headers', {}),
                query_params=message_data.get('query_params', {})
            )
            
            # 使用IPC应用处理请求
            if self.app:
                response = await self.app.handle_request(request)
            else:
                response = IPCResponse(
                    status_code=503,
                    data={'error': 'IPC application not available'}
                )
            
            return response.to_json()
            
        except Exception as e:
            logger.error(f"处理IPC消息失败: {e}")
            error_response = IPCResponse(
                status_code=500,
                data={'error': f'Internal server error: {str(e)}'}
            )
            return error_response.to_json()
    
    def _write_pipe_info(self):
        """写入pipe信息到配置文件"""
        try:
            from api.dependencies import get_config_manager
            
            config_manager = get_config_manager()
            socket_info = {
                'type': 'named_pipe',
                'path': self.full_pipe_name,
                'pid': os.getpid(),
                'protocol': 'ipc'
            }
            
            # 写入到socket配置文件
            socket_file = config_manager.get_paths()["app_data"] / "daemon.socket"
            socket_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(socket_file, 'w') as f:
                json.dump(socket_info, f, indent=2)
            
            # 设置文件权限（Windows上使用ACL）
            self._secure_config_file(socket_file)
            
            logger.info(f"Named Pipe信息已写入: {socket_file}")
            
        except Exception as e:
            logger.error(f"写入pipe信息失败: {e}")
    
    def _secure_config_file(self, file_path: Path):
        """保护配置文件安全"""
        try:
            if WINDOWS_SUPPORT:
                # Windows: 设置文件ACL，只允许当前用户访问
                import win32security
                import ntsecuritycon
                
                # 获取当前用户
                current_user = win32api.GetUserName()
                user_sid, domain, account_type = win32security.LookupAccountName(None, current_user)
                
                # 创建安全描述符
                sd = win32security.SECURITY_DESCRIPTOR()
                dacl = win32security.ACL()
                
                # 添加用户的完全控制权限
                dacl.AddAccessAllowedAce(
                    win32security.ACL_REVISION,
                    ntsecuritycon.FILE_ALL_ACCESS,
                    user_sid
                )
                
                sd.SetSecurityDescriptorDacl(1, dacl, 0)
                
                # 应用安全描述符
                win32security.SetFileSecurity(
                    str(file_path),
                    win32security.DACL_SECURITY_INFORMATION,
                    sd
                )
                
                logger.debug(f"配置文件安全权限已设置: {file_path}")
                
        except Exception as e:
            logger.warning(f"设置配置文件安全权限失败: {e}")
    
    async def stop(self):
        """停止Windows IPC服务器"""
        self.is_running = False
        
        # 关闭线程池
        self.thread_pool.shutdown(wait=True, timeout=5.0)
        
        # 清理配置文件
        try:
            from api.dependencies import get_config_manager
            config_manager = get_config_manager()
            socket_file = config_manager.get_paths()["app_data"] / "daemon.socket"
            if socket_file.exists():
                socket_file.unlink()
        except Exception as e:
            logger.error(f"清理配置文件时出错: {e}")
        
        logger.info("✅ Windows IPC服务器已停止")


def check_windows_ipc_support() -> bool:
    """检查Windows IPC支持"""
    if platform.system() != 'Windows':
        return False
    
    return WINDOWS_SUPPORT


def install_windows_dependencies():
    """安装Windows依赖的帮助函数"""
    if platform.system() != 'Windows':
        print("此功能仅在Windows系统上可用")
        return
    
    if not WINDOWS_SUPPORT:
        print("需要安装Windows依赖:")
        print("pip install pywin32")
        print()
        print("安装完成后请重启应用")
    else:
        print("✅ Windows IPC支持已可用")


if __name__ == "__main__":
    # 测试Windows IPC支持
    print("=== Windows IPC支持检查 ===")
    if check_windows_ipc_support():
        print("✅ Windows Named Pipe支持可用")
    else:
        install_windows_dependencies()