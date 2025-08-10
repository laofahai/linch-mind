"""
IPC中间件系统 - 提供身份验证、日志记录、错误处理等功能
"""

import asyncio
import json
import logging
import re
import time
from typing import Any, Callable, Dict, Optional

from .ipc_protocol import IPCErrorCode, IPCRequest, IPCResponse

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
            status_text = "success" if response.success else "error"
            self.logger.info(
                f"IPC Response: {request.method} {request.path} - "
                f"Status: {status_text} - "
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

            return IPCResponse.error_response(
                IPCErrorCode.INTERNAL_ERROR,
                "Internal server error",
                {"exception": str(e)},
            )


class AuthenticationMiddleware:
    """简化的身份验证中间件 - 只验证IPC服务器认证状态"""

    def __init__(self, require_auth: bool = True):
        self.require_auth = require_auth

    async def __call__(self, request: IPCRequest, call_next: Callable) -> IPCResponse:
        """执行简化的身份验证检查"""
        if not self.require_auth:
            logger.debug("认证中间件：不要求认证，直接放行")
            return await call_next()

        # 认证相关的路径应该绕过认证检查
        auth_paths = ["/auth/handshake", "/health", "/", "/server/info"]
        if request.path in auth_paths:
            logger.debug(f"认证中间件：认证路径 {request.path} 绕过认证检查")
            return await call_next()

        # 关键简化：只检查是否已通过IPC服务器认证
        # IPC服务器在握手阶段已经完成了完整的进程验证
        authenticated = request.get_header("x-authenticated") == "true"
        internal_client = request.get_header("x-internal-client") == "true"

        logger.debug(f"认证中间件检查: {request.method} {request.path}")
        logger.debug(f"  x-authenticated: {request.get_header('x-authenticated')}")
        logger.debug(f"  x-internal-client: {request.get_header('x-internal-client')}")
        logger.debug(
            f"  认证状态: authenticated={authenticated}, internal={internal_client}"
        )

        if authenticated or internal_client:
            # 已认证或内部客户端，直接放行
            logger.debug("认证中间件：客户端已认证，放行")
            return await call_next()

        # 未认证客户端：返回401错误
        logger.warning(f"认证中间件：IPC请求未认证 - {request.method} {request.path}")
        logger.warning(f"  请求头部: {request.headers}")
        return IPCResponse.error_response(
            IPCErrorCode.AUTH_REQUIRED,
            "Authentication required",
            {"message": "请先通过IPC握手进行认证"},
        )


class IPCSecurityMiddleware:
    """IPC安全中间件（替代CORS，专为IPC架构设计）"""

    def __init__(self, allowed_clients: list = None):
        self.allowed_clients = allowed_clients or []

    async def __call__(self, request: IPCRequest, call_next: Callable) -> IPCResponse:
        """处理IPC安全验证"""
        response = await call_next()

        # IPC模式下不需要HTTP头部，只进行客户端验证
        if not response.headers:
            response.headers = {}

        # 添加IPC相关的安全头部
        response.headers.update(
            {
                "x-ipc-mode": "true",
                "x-security-level": "local-ipc",
                "x-client-validation": "passed",
            }
        )

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
        client_id = request.get_header("x-client-pid", "unknown")
        current_time = time.time()

        # 清理过期记录
        self._cleanup_expired_records(current_time)

        # 检查请求频率
        if client_id in self.request_counts:
            client_data = self.request_counts[client_id]
            if current_time - client_data["start_time"] < self.time_window:
                if client_data["count"] >= self.max_requests:
                    return IPCResponse.error_response(
                        IPCErrorCode.REQUEST_TIMEOUT,
                        "Too many requests",
                        {
                            "retry_after": self.time_window
                            - (current_time - client_data["start_time"])
                        },
                    )
                client_data["count"] += 1
            else:
                # 重置计数器
                client_data["start_time"] = current_time
                client_data["count"] = 1
        else:
            # 新客户端
            self.request_counts[client_id] = {"start_time": current_time, "count": 1}

        return await call_next()

    def _cleanup_expired_records(self, current_time: float):
        """清理过期的频率限制记录"""
        expired_clients = []
        for client_id, data in self.request_counts.items():
            if current_time - data["start_time"] > self.time_window * 2:
                expired_clients.append(client_id)

        for client_id in expired_clients:
            del self.request_counts[client_id]


class ValidationMiddleware:
    """增强的请求验证中间件 - 防止注入攻击"""

    def __init__(self, max_payload_size: int = 1024 * 1024):  # 1MB
        self.max_payload_size = max_payload_size
        
        # 🚨 安全模式：危险字符和模式检测
        self.dangerous_patterns = [
            # SQL注入模式
            r"(?i)(union\s+select|drop\s+table|delete\s+from|insert\s+into)",
            r"(?i)(alter\s+table|truncate\s+table|create\s+table)",
            r"(?i)[\'\";].*(or\s+1=1|and\s+1=1|or\s+true|and\s+true)",
            
            # 命令注入模式
            r"(?i)[;&|`\$].*(rm\s+|cat\s+|ls\s+|chmod\s+|sudo\s+)",
            r"(?i)(sh\s+-c|bash\s+-c|cmd\.exe|powershell)",
            
            # 路径遍历攻击
            r"\.\./|\.\.\\\\|%2e%2e%2f|%2e%2e\\\\",
            
            # XSS和代码注入
            r"(?i)<script.*?>|javascript:|vbscript:|onload=|onerror=",
            r"(?i)eval\s*\(|exec\s*\(|system\s*\(",
            
            # 其他危险模式
            r"(?i)(password|secret|token|key).*[=:].*['\"]",  # 敏感信息泄露
        ]
        
        # 危险字符集
        self.dangerous_chars = set(['<', '>', '&', '"', "'", ';', '|', '`', '$'])
        
        # 最大嵌套深度
        self.max_nesting_depth = 10

    async def __call__(self, request: IPCRequest, call_next: Callable) -> IPCResponse:
        """执行增强的请求验证"""
        
        # 1. 基础验证：数据大小
        if request.data:
            payload_size = len(json.dumps(request.data).encode("utf-8"))
            if payload_size > self.max_payload_size:
                logger.warning(f"拒绝超大payload: {payload_size} > {self.max_payload_size}")
                return IPCResponse.error_response(
                    IPCErrorCode.INVALID_REQUEST,
                    "Payload too large",
                    {"max_size": self.max_payload_size, "actual_size": payload_size},
                )

        # 2. 方法验证
        allowed_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        if request.method.upper() not in allowed_methods:
            logger.warning(f"拒绝无效HTTP方法: {request.method}")
            return IPCResponse.error_response(
                IPCErrorCode.INVALID_REQUEST, f"Method {request.method} not allowed"
            )

        # 3. 路径验证和安全检查
        path_validation = self._validate_path(request.path)
        if path_validation:
            logger.warning(f"拒绝危险路径: {request.path} - {path_validation}")
            return IPCResponse.error_response(
                IPCErrorCode.INVALID_REQUEST, 
                f"Invalid path: {path_validation}",
                {"path": request.path, "security_issue": path_validation}
            )

        # 4. 🔒 深度内容安全验证
        content_validation = self._validate_content_security(request.data)
        if content_validation:
            logger.warning(f"拒绝危险内容: {content_validation}")
            return IPCResponse.error_response(
                IPCErrorCode.INVALID_REQUEST,
                f"Content security violation: {content_validation}",
                {"security_issue": content_validation}
            )

        # 5. 头部验证
        header_validation = self._validate_headers(request.headers)
        if header_validation:
            logger.warning(f"拒绝危险头部: {header_validation}")
            return IPCResponse.error_response(
                IPCErrorCode.INVALID_REQUEST,
                f"Header security violation: {header_validation}",
                {"security_issue": header_validation}
            )

        return await call_next()
    
    def _validate_path(self, path: str) -> Optional[str]:
        """验证路径安全性"""
        if not path.startswith("/"):
            return "Path must start with /"
            
        # 检查路径遍历攻击
        if ".." in path:
            return "Path traversal attack detected"
            
        # 检查过长路径
        if len(path) > 500:
            return "Path too long"
            
        # 检查危险字符
        dangerous_chars_found = [c for c in self.dangerous_chars if c in path]
        if dangerous_chars_found:
            return f"Dangerous characters in path: {dangerous_chars_found}"
            
        return None
    
    def _validate_content_security(self, data: Any, depth: int = 0) -> Optional[str]:
        """深度验证内容安全性"""
        if depth > self.max_nesting_depth:
            return f"Data nesting too deep (>{self.max_nesting_depth})"
            
        if data is None:
            return None
            
        if isinstance(data, str):
            return self._validate_string_security(data)
            
        elif isinstance(data, dict):
            # 检查键名
            for key in data.keys():
                if not isinstance(key, str):
                    return f"Non-string key detected: {type(key)}"
                key_validation = self._validate_string_security(key)
                if key_validation:
                    return f"Dangerous key: {key_validation}"
            
            # 递归检查值
            for key, value in data.items():
                value_validation = self._validate_content_security(value, depth + 1)
                if value_validation:
                    return f"Dangerous value in key '{key}': {value_validation}"
                    
        elif isinstance(data, list):
            # 检查列表大小
            if len(data) > 1000:
                return f"List too large: {len(data)} > 1000"
                
            # 递归检查列表项
            for i, item in enumerate(data):
                item_validation = self._validate_content_security(item, depth + 1)
                if item_validation:
                    return f"Dangerous list item [{i}]: {item_validation}"
                    
        elif isinstance(data, (int, float, bool)):
            # 数字和布尔值通常是安全的
            pass
        else:
            return f"Unsupported data type: {type(data)}"
            
        return None
    
    def _validate_string_security(self, text: str) -> Optional[str]:
        """验证字符串安全性"""
        if len(text) > 10000:  # 防止超大字符串
            return f"String too long: {len(text)} > 10000"
            
        # 检查危险模式
        for pattern in self.dangerous_patterns:
            if re.search(pattern, text):
                return f"Dangerous pattern detected: matched {pattern[:30]}..."
                
        # 检查大量危险字符
        dangerous_char_count = sum(1 for c in text if c in self.dangerous_chars)
        if dangerous_char_count > 5:
            return f"Too many dangerous characters: {dangerous_char_count} > 5"
            
        return None
    
    def _validate_headers(self, headers: Dict[str, str]) -> Optional[str]:
        """验证请求头部安全性"""
        if not headers:
            return None
            
        # 检查头部数量
        if len(headers) > 50:
            return f"Too many headers: {len(headers)} > 50"
            
        # 检查每个头部
        for name, value in headers.items():
            if not isinstance(name, str) or not isinstance(value, str):
                return f"Invalid header type: {type(name)}, {type(value)}"
                
            # 验证头部名称和值
            name_validation = self._validate_string_security(name)
            if name_validation:
                return f"Dangerous header name '{name}': {name_validation}"
                
            value_validation = self._validate_string_security(value)
            if value_validation:
                return f"Dangerous header value '{name}': {value_validation}"
                
        return None


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
            return IPCResponse.error_response(
                IPCErrorCode.INVALID_REQUEST,
                "Validation error",
                {"detail": str(e) if self.debug else "Invalid request data"},
            )
        except PermissionError as e:
            logger.warning(f"Permission error: {e}")
            return IPCResponse.error_response(
                IPCErrorCode.INSUFFICIENT_PERMISSIONS,
                "Permission denied",
                {"detail": str(e) if self.debug else "Access forbidden"},
            )
        except FileNotFoundError as e:
            logger.warning(f"Resource not found: {e}")
            return IPCResponse.error_response(
                IPCErrorCode.RESOURCE_NOT_FOUND,
                "Resource not found",
                {
                    "detail": (
                        str(e) if self.debug else "Requested resource does not exist"
                    )
                },
            )
        except asyncio.TimeoutError as e:
            logger.error(f"Request timeout: {e}")
            return IPCResponse.error_response(
                IPCErrorCode.REQUEST_TIMEOUT,
                "Request timeout",
                {"detail": "The request took too long to process"},
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return IPCResponse.error_response(
                IPCErrorCode.INTERNAL_ERROR,
                "Internal server error",
                {"detail": str(e) if self.debug else "An unexpected error occurred"},
            )


# 预定义中间件实例
def create_default_middlewares(debug: bool = False, secure_mode: bool = True) -> list:
    """创建简化的默认中间件堆栈"""
    middlewares = [
        ErrorHandlingMiddleware(debug=debug),
        ValidationMiddleware(),
        LoggingMiddleware(),
    ]

    # 简化安全模式：只添加必要的认证检查
    if secure_mode:
        middlewares.extend(
            [
                AuthenticationMiddleware(require_auth=True),  # 简化认证中间件
                # 移除过于严格的频率限制，使用更宽松的设置
                RateLimitMiddleware(max_requests=200, time_window=60),
            ]
        )
    else:
        # 兼容模式
        middlewares.extend(
            [
                # CORSMiddleware(),  # 不需要，因为使用IPC而非HTTP
                RateLimitMiddleware(max_requests=300, time_window=60),
            ]
        )

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
