"""
IPC中间件系统 - 提供身份验证、日志记录、错误处理等功能
"""

import asyncio
import json
import logging
import time
from typing import Any, Callable, Dict, Optional
from datetime import datetime

from .ipc_router import IPCRequest, IPCResponse, Middleware

logger = logging.getLogger(__name__)


class LoggingMiddleware:
    """请求日志中间件"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("ipc.requests")
    
    async def __call__(self, request: IPCRequest, call_next: Callable) -> IPCResponse:
        """执行日志中间件"""
        start_time = time.time()
        
        # 记录请求开始
        self.logger.info(
            f"IPC Request: {request.method} {request.path} - "
            f"Data size: {len(json.dumps(request.data or {}))} bytes"
        )
        
        try:
            # 执行下一个中间件或路由处理器
            response = await call_next()
            
            # 计算处理时间
            duration = time.time() - start_time
            
            # 记录响应
            self.logger.info(
                f"IPC Response: {request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.3f}s"
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(
                f"IPC Error: {request.method} {request.path} - "
                f"Error: {str(e)} - "
                f"Duration: {duration:.3f}s"
            )
            
            return IPCResponse(
                status_code=500,
                data={"error": "Internal server error"}
            )


class AuthenticationMiddleware:
    """身份验证中间件"""
    
    def __init__(self, require_auth: bool = True, allowed_processes: Optional[Dict[int, str]] = None):
        self.require_auth = require_auth
        self.allowed_processes = allowed_processes or {}
    
    async def __call__(self, request: IPCRequest, call_next: Callable) -> IPCResponse:
        """执行身份验证"""
        if not self.require_auth:
            return await call_next()
        
        # 获取进程验证信息
        auth_header = request.get_header('authorization')
        client_pid = request.get_header('x-client-pid')
        
        if not client_pid:
            return IPCResponse(
                status_code=401,
                data={"error": "Missing client process ID"}
            )
        
        try:
            pid = int(client_pid)
            
            # 验证进程是否存在且符合要求
            if not self._validate_process(pid, auth_header):
                return IPCResponse(
                    status_code=403,
                    data={"error": "Unauthorized process"}
                )
            
            # 将进程信息添加到请求中
            if not request.headers:
                request.headers = {}
            request.headers['x-validated-pid'] = str(pid)
            
            return await call_next()
            
        except ValueError:
            return IPCResponse(
                status_code=401,
                data={"error": "Invalid client process ID"}
            )
    
    def _validate_process(self, pid: int, auth_header: Optional[str]) -> bool:
        """验证进程身份"""
        import psutil
        
        try:
            # 检查进程是否存在
            if not psutil.pid_exists(pid):
                return False
            
            # 获取进程信息
            process = psutil.Process(pid)
            
            # 检查是否为本地进程（简单的安全检查）
            if process.ppid() == 0:  # 不允许系统进程
                return False
            
            # 如果有允许的进程列表，检查是否在列表中
            if self.allowed_processes:
                process_name = process.name()
                return pid in self.allowed_processes or process_name in self.allowed_processes.values()
            
            # 基本验证：检查进程是否为Python进程
            process_name = process.name().lower()
            if 'python' not in process_name and 'flutter' not in process_name:
                return False
            
            return True
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False


class CORSMiddleware:
    """跨域请求中间件（IPC环境下主要用于兼容性）"""
    
    def __init__(self, allow_origins: list = None):
        self.allow_origins = allow_origins or ["*"]
    
    async def __call__(self, request: IPCRequest, call_next: Callable) -> IPCResponse:
        """处理CORS"""
        response = await call_next()
        
        # 添加CORS头部
        if not response.headers:
            response.headers = {}
        
        response.headers.update({
            'access-control-allow-origin': '*',
            'access-control-allow-methods': 'GET, POST, PUT, DELETE, PATCH',
            'access-control-allow-headers': 'Content-Type, Authorization, X-Client-PID'
        })
        
        return response


class RateLimitMiddleware:
    """请求频率限制中间件"""
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_counts: Dict[str, Dict[str, Any]] = {}
    
    async def __call__(self, request: IPCRequest, call_next: Callable) -> IPCResponse:
        """执行频率限制检查"""
        # 获取客户端标识（使用PID）
        client_id = request.get_header('x-client-pid', 'unknown')
        current_time = time.time()
        
        # 清理过期记录
        self._cleanup_expired_records(current_time)
        
        # 检查请求频率
        if client_id in self.request_counts:
            client_data = self.request_counts[client_id]
            if current_time - client_data['start_time'] < self.time_window:
                if client_data['count'] >= self.max_requests:
                    return IPCResponse(
                        status_code=429,
                        data={
                            "error": "Too many requests",
                            "retry_after": self.time_window - (current_time - client_data['start_time'])
                        }
                    )
                client_data['count'] += 1
            else:
                # 重置计数器
                client_data['start_time'] = current_time
                client_data['count'] = 1
        else:
            # 新客户端
            self.request_counts[client_id] = {
                'start_time': current_time,
                'count': 1
            }
        
        return await call_next()
    
    def _cleanup_expired_records(self, current_time: float):
        """清理过期的频率限制记录"""
        expired_clients = []
        for client_id, data in self.request_counts.items():
            if current_time - data['start_time'] > self.time_window * 2:
                expired_clients.append(client_id)
        
        for client_id in expired_clients:
            del self.request_counts[client_id]


class ValidationMiddleware:
    """请求验证中间件"""
    
    def __init__(self, max_payload_size: int = 1024 * 1024):  # 1MB
        self.max_payload_size = max_payload_size
    
    async def __call__(self, request: IPCRequest, call_next: Callable) -> IPCResponse:
        """执行请求验证"""
        # 检查请求数据大小
        if request.data:
            payload_size = len(json.dumps(request.data).encode('utf-8'))
            if payload_size > self.max_payload_size:
                return IPCResponse(
                    status_code=413,
                    data={
                        "error": "Payload too large",
                        "max_size": self.max_payload_size,
                        "actual_size": payload_size
                    }
                )
        
        # 验证请求方法
        allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        if request.method.upper() not in allowed_methods:
            return IPCResponse(
                status_code=405,
                data={"error": f"Method {request.method} not allowed"}
            )
        
        # 验证路径格式
        if not request.path.startswith('/'):
            return IPCResponse(
                status_code=400,
                data={"error": "Invalid path format"}
            )
        
        return await call_next()


class ErrorHandlingMiddleware:
    """错误处理中间件"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
    
    async def __call__(self, request: IPCRequest, call_next: Callable) -> IPCResponse:
        """处理错误"""
        try:
            return await call_next()
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return IPCResponse(
                status_code=400,
                data={
                    "error": "Validation error",
                    "detail": str(e) if self.debug else "Invalid request data"
                }
            )
        except PermissionError as e:
            logger.warning(f"Permission error: {e}")
            return IPCResponse(
                status_code=403,
                data={
                    "error": "Permission denied",
                    "detail": str(e) if self.debug else "Access forbidden"
                }
            )
        except FileNotFoundError as e:
            logger.warning(f"Resource not found: {e}")
            return IPCResponse(
                status_code=404,
                data={
                    "error": "Resource not found",
                    "detail": str(e) if self.debug else "Requested resource does not exist"
                }
            )
        except asyncio.TimeoutError as e:
            logger.error(f"Request timeout: {e}")
            return IPCResponse(
                status_code=408,
                data={
                    "error": "Request timeout",
                    "detail": "The request took too long to process"
                }
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return IPCResponse(
                status_code=500,
                data={
                    "error": "Internal server error",
                    "detail": str(e) if self.debug else "An unexpected error occurred"
                }
            )


# 预定义中间件实例
def create_default_middlewares(debug: bool = False, secure_mode: bool = True) -> list:
    """创建默认中间件堆栈 - 已启用安全模式"""
    middlewares = [
        ErrorHandlingMiddleware(debug=debug),
        ValidationMiddleware(),
        LoggingMiddleware(),
    ]
    
    if secure_mode:
        # 安全模式：启用身份验证和更严格的频率限制
        middlewares.extend([
            AuthenticationMiddleware(require_auth=True),  # ✅ 启用身份验证
            RateLimitMiddleware(max_requests=100, time_window=60),  # 更严格的频率限制
        ])
    else:
        # 兼容模式：保持原有配置
        middlewares.extend([
            CORSMiddleware(),
            RateLimitMiddleware(max_requests=200, time_window=60),
        ])
    
    return middlewares


def create_production_middlewares() -> list:
    """创建生产环境中间件堆栈 - 最高安全级别"""
    return [
        ErrorHandlingMiddleware(debug=False),
        ValidationMiddleware(),
        AuthenticationMiddleware(require_auth=True),  # 强制身份验证
        RateLimitMiddleware(max_requests=50, time_window=60),  # 严格频率限制
        LoggingMiddleware(),  # 详细日志记录
    ]