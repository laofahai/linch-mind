"""
纯IPC路由系统 - 完全独立于FastAPI
支持路由注册、中间件、错误处理等功能
"""

import asyncio
import inspect
import json
import logging
import re
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from functools import wraps

logger = logging.getLogger(__name__)


@dataclass
class IPCRequest:
    """IPC请求对象"""
    method: str
    path: str
    data: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    query_params: Optional[Dict[str, Any]] = None
    path_params: Optional[Dict[str, str]] = None
    
    def get_header(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """获取请求头"""
        if not self.headers:
            return default
        return self.headers.get(name.lower(), default)
    
    def get_query(self, name: str, default: Any = None) -> Any:
        """获取查询参数"""
        if not self.query_params:
            return default
        return self.query_params.get(name, default)


@dataclass 
class IPCResponse:
    """IPC响应对象"""
    status_code: int = 200
    data: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'status_code': self.status_code,
            'data': self.data or {},
            'headers': self.headers or {}
        }


# 路由处理函数类型
RouteHandler = Callable[[IPCRequest], Awaitable[Union[IPCResponse, Dict[str, Any]]]]

# 中间件类型
Middleware = Callable[[IPCRequest, Callable], Awaitable[IPCResponse]]


class RoutePattern:
    """路由模式匹配器"""
    
    def __init__(self, pattern: str, method: str = "GET"):
        self.pattern = pattern
        self.method = method.upper()
        
        # 将路径模式转换为正则表达式
        # 例如: /users/{user_id} -> /users/(?P<user_id>[^/]+)
        regex_pattern = re.sub(r'\{([^}]+)\}', r'(?P<\1>[^/]+)', pattern)
        regex_pattern = f"^{regex_pattern}$"
        
        self.regex = re.compile(regex_pattern)
        
    def match(self, method: str, path: str) -> Optional[Dict[str, str]]:
        """匹配路径并返回路径参数"""
        if method.upper() != self.method:
            return None
            
        match = self.regex.match(path)
        if match:
            return match.groupdict()
        return None


class IPCRouter:
    """纯IPC路由器"""
    
    def __init__(self, prefix: str = ""):
        self.prefix = prefix.rstrip('/')
        self.routes: List[Tuple[RoutePattern, RouteHandler]] = []
        self.middlewares: List[Middleware] = []
        self.error_handlers: Dict[int, RouteHandler] = {}
        
    def add_middleware(self, middleware: Middleware):
        """添加中间件"""
        self.middlewares.append(middleware)
        
    def add_error_handler(self, status_code: int, handler: RouteHandler):
        """添加错误处理器"""
        self.error_handlers[status_code] = handler
    
    def route(self, path: str, methods: List[str] = None):
        """路由装饰器"""
        if methods is None:
            methods = ["GET"]
            
        def decorator(handler: RouteHandler):
            # 为每个HTTP方法注册路由
            for method in methods:
                full_path = f"{self.prefix}{path}"
                pattern = RoutePattern(full_path, method)
                self.routes.append((pattern, handler))
            return handler
        return decorator
    
    def get(self, path: str):
        """GET路由装饰器"""
        return self.route(path, ["GET"])
    
    def post(self, path: str):
        """POST路由装饰器"""
        return self.route(path, ["POST"])
    
    def put(self, path: str):
        """PUT路由装饰器"""
        return self.route(path, ["PUT"])
    
    def delete(self, path: str):
        """DELETE路由装饰器"""
        return self.route(path, ["DELETE"])
    
    def patch(self, path: str):
        """PATCH路由装饰器"""
        return self.route(path, ["PATCH"])
    
    async def handle_request(self, request: IPCRequest) -> IPCResponse:
        """处理请求"""
        try:
            # 查找匹配的路由
            handler, path_params = self._find_route(request.method, request.path)
            if not handler:
                return IPCResponse(
                    status_code=404,
                    data={"error": f"Route not found: {request.method} {request.path}"}
                )
            
            # 设置路径参数
            request.path_params = path_params
            
            # 应用中间件
            response = await self._apply_middlewares(request, handler)
            
            # 确保返回IPCResponse对象
            if isinstance(response, dict):
                response = IPCResponse(data=response)
            elif not isinstance(response, IPCResponse):
                response = IPCResponse(data={"result": response})
                
            return response
            
        except Exception as e:
            logger.error(f"处理请求时出错: {e}", exc_info=True)
            return await self._handle_error(500, request, str(e))
    
    def _find_route(self, method: str, path: str) -> Tuple[Optional[RouteHandler], Dict[str, str]]:
        """查找匹配的路由"""
        for pattern, handler in self.routes:
            path_params = pattern.match(method, path)
            if path_params is not None:
                return handler, path_params
        return None, {}
    
    async def _apply_middlewares(self, request: IPCRequest, handler: RouteHandler) -> IPCResponse:
        """应用中间件链"""
        async def next_middleware(middleware_index: int) -> IPCResponse:
            if middleware_index >= len(self.middlewares):
                # 执行实际的路由处理器
                return await handler(request)
            else:
                # 执行下一个中间件
                middleware = self.middlewares[middleware_index]
                return await middleware(request, lambda: next_middleware(middleware_index + 1))
        
        return await next_middleware(0)
    
    async def _handle_error(self, status_code: int, request: IPCRequest, error_message: str) -> IPCResponse:
        """处理错误"""
        if status_code in self.error_handlers:
            try:
                # 创建包含错误信息的临时请求
                error_request = IPCRequest(
                    method=request.method,
                    path=request.path,
                    data={"error": error_message, "status_code": status_code}
                )
                return await self.error_handlers[status_code](error_request)
            except Exception as e:
                logger.error(f"错误处理器执行失败: {e}")
        
        return IPCResponse(
            status_code=status_code,
            data={"error": error_message}
        )


class IPCApplication:
    """IPC应用程序主类"""
    
    def __init__(self):
        self.routers: List[IPCRouter] = []
        self.global_middlewares: List[Middleware] = []
        self.global_error_handlers: Dict[int, RouteHandler] = {}
        
    def add_middleware(self, middleware: Middleware):
        """添加全局中间件"""
        self.global_middlewares.append(middleware)
        
    def add_error_handler(self, status_code: int, handler: RouteHandler):
        """添加全局错误处理器"""
        self.global_error_handlers[status_code] = handler
    
    def include_router(self, router: IPCRouter):
        """包含路由器"""
        # 将全局中间件添加到路由器
        for middleware in self.global_middlewares:
            router.add_middleware(middleware)
        
        # 将全局错误处理器添加到路由器
        for status_code, handler in self.global_error_handlers.items():
            if status_code not in router.error_handlers:
                router.add_error_handler(status_code, handler)
        
        self.routers.append(router)
    
    async def handle_request(self, method: str, path: str, 
                           data: Optional[Dict[str, Any]] = None,
                           headers: Optional[Dict[str, str]] = None,
                           query_params: Optional[Dict[str, Any]] = None) -> IPCResponse:
        """处理请求"""
        request = IPCRequest(
            method=method,
            path=path,
            data=data,
            headers=headers,
            query_params=query_params
        )
        
        # 尝试每个路由器
        for router in self.routers:
            # 检查路径是否匹配路由器前缀
            if not path.startswith(router.prefix) and router.prefix:
                continue
                
            response = await router.handle_request(request)
            if response.status_code != 404:
                return response
        
        # 没有找到匹配的路由
        return IPCResponse(
            status_code=404,
            data={"error": f"Route not found: {method} {path}"}
        )


# 全局应用实例
ipc_app = IPCApplication()


# 便捷的装饰器函数
def ipc_route(path: str, methods: List[str] = None, prefix: str = ""):
    """创建IPC路由的便捷装饰器"""
    router = IPCRouter(prefix=prefix)
    
    def decorator(handler: RouteHandler):
        router.route(path, methods or ["GET"])(handler)
        ipc_app.include_router(router)
        return handler
    return decorator


def ipc_get(path: str, prefix: str = ""):
    """GET路由装饰器"""
    return ipc_route(path, ["GET"], prefix)


def ipc_post(path: str, prefix: str = ""):
    """POST路由装饰器"""
    return ipc_route(path, ["POST"], prefix)


def ipc_put(path: str, prefix: str = ""):
    """PUT路由装饰器"""
    return ipc_route(path, ["PUT"], prefix)


def ipc_delete(path: str, prefix: str = ""):
    """DELETE路由装饰器"""
    return ipc_route(path, ["DELETE"], prefix)