"""
向后兼容层 - 将IPC系统包装成类似FastAPI的接口
确保现有代码可以无缝迁移到纯IPC系统
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass

from .ipc_client import IPCClient, get_ipc_client

logger = logging.getLogger(__name__)


@dataclass
class MockResponse:
    """模拟HTTP响应对象"""
    status_code: int
    data: Dict[str, Any]
    headers: Dict[str, str]
    
    def json(self) -> Dict[str, Any]:
        """返回JSON数据"""
        return self.data
    
    @property
    def text(self) -> str:
        """返回文本内容"""
        import json
        return json.dumps(self.data)


class MockHTTPClient:
    """模拟HTTP客户端 - 实际使用IPC通信"""
    
    def __init__(self, base_url: str = ""):
        self.base_url = base_url.rstrip('/')
        self._session = None
    
    async def _get_session(self):
        """获取IPC会话"""
        if self._session is None:
            self._session = await get_ipc_client()
        return self._session
    
    async def get(self, path: str, params: Optional[Dict[str, Any]] = None,
                 headers: Optional[Dict[str, str]] = None, **kwargs) -> MockResponse:
        """GET请求"""
        session = await self._get_session()
        try:
            response_data = await session.get(path, params=params, headers=headers)
            return MockResponse(
                status_code=response_data.get('status_code', 200),
                data=response_data.get('data', {}),
                headers=response_data.get('headers', {})
            )
        except Exception as e:
            logger.error(f"IPC GET request failed: {e}")
            return MockResponse(
                status_code=500,
                data={'error': str(e)},
                headers={}
            )
    
    async def post(self, path: str, json: Optional[Dict[str, Any]] = None,
                  data: Optional[Dict[str, Any]] = None,
                  headers: Optional[Dict[str, str]] = None, **kwargs) -> MockResponse:
        """POST请求"""
        session = await self._get_session()
        request_data = json or data
        try:
            response_data = await session.post(path, data=request_data, headers=headers)
            return MockResponse(
                status_code=response_data.get('status_code', 200),
                data=response_data.get('data', {}),
                headers=response_data.get('headers', {})
            )
        except Exception as e:
            logger.error(f"IPC POST request failed: {e}")
            return MockResponse(
                status_code=500,
                data={'error': str(e)},
                headers={}
            )
    
    async def put(self, path: str, json: Optional[Dict[str, Any]] = None,
                 data: Optional[Dict[str, Any]] = None,
                 headers: Optional[Dict[str, str]] = None, **kwargs) -> MockResponse:
        """PUT请求"""
        session = await self._get_session()
        request_data = json or data
        try:
            response_data = await session.put(path, data=request_data, headers=headers)
            return MockResponse(
                status_code=response_data.get('status_code', 200),
                data=response_data.get('data', {}),
                headers=response_data.get('headers', {})
            )
        except Exception as e:
            logger.error(f"IPC PUT request failed: {e}")
            return MockResponse(
                status_code=500,
                data={'error': str(e)},
                headers={}
            )
    
    async def delete(self, path: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> MockResponse:
        """DELETE请求"""
        session = await self._get_session()
        try:
            response_data = await session.delete(path, headers=headers)
            return MockResponse(
                status_code=response_data.get('status_code', 200),
                data=response_data.get('data', {}),
                headers=response_data.get('headers', {})
            )
        except Exception as e:
            logger.error(f"IPC DELETE request failed: {e}")
            return MockResponse(
                status_code=500,
                data={'error': str(e)},
                headers={}
            )


# 全局HTTP客户端实例（实际使用IPC）
_http_client: Optional[MockHTTPClient] = None


def get_http_client() -> MockHTTPClient:
    """获取HTTP客户端（实际返回IPC客户端）"""
    global _http_client
    if _http_client is None:
        _http_client = MockHTTPClient()
    return _http_client


class RequestsCompatibility:
    """requests库兼容层"""
    
    @staticmethod
    async def get(url: str, **kwargs) -> MockResponse:
        """GET请求"""
        client = get_http_client()
        # 从URL提取路径
        path = url.replace('http://localhost:8080', '').replace('http://127.0.0.1:8080', '')
        if not path.startswith('/'):
            path = '/' + path
        return await client.get(path, **kwargs)
    
    @staticmethod
    async def post(url: str, **kwargs) -> MockResponse:
        """POST请求"""
        client = get_http_client()
        path = url.replace('http://localhost:8080', '').replace('http://127.0.0.1:8080', '')
        if not path.startswith('/'):
            path = '/' + path
        return await client.post(path, **kwargs)
    
    @staticmethod
    async def put(url: str, **kwargs) -> MockResponse:
        """PUT请求"""
        client = get_http_client()
        path = url.replace('http://localhost:8080', '').replace('http://127.0.0.1:8080', '')
        if not path.startswith('/'):
            path = '/' + path
        return await client.put(path, **kwargs)
    
    @staticmethod
    async def delete(url: str, **kwargs) -> MockResponse:
        """DELETE请求"""
        client = get_http_client()
        path = url.replace('http://localhost:8080', '').replace('http://127.0.0.1:8080', '')
        if not path.startswith('/'):
            path = '/' + path
        return await client.delete(path, **kwargs)


# 为向后兼容，提供requests风格的接口
async_requests = RequestsCompatibility()


class FastAPICompatibilityRequest:
    """FastAPI Request对象兼容层"""
    
    def __init__(self, method: str, path: str, data: Optional[Dict[str, Any]] = None,
                 headers: Optional[Dict[str, str]] = None, 
                 query_params: Optional[Dict[str, Any]] = None):
        self.method = method
        self.url = type('MockURL', (), {'path': path})()
        self.headers = headers or {}
        self.query_params = query_params or {}
        self._json_data = data
    
    async def json(self) -> Dict[str, Any]:
        """返回JSON数据"""
        return self._json_data or {}
    
    async def body(self) -> bytes:
        """返回请求体"""
        import json
        if self._json_data:
            return json.dumps(self._json_data).encode('utf-8')
        return b''


def create_mock_request(method: str, path: str, **kwargs) -> FastAPICompatibilityRequest:
    """创建模拟的FastAPI请求对象"""
    return FastAPICompatibilityRequest(method, path, **kwargs)


class HealthChecker:
    """健康检查器 - 使用IPC通信"""
    
    @staticmethod
    async def check_daemon_health() -> bool:
        """检查daemon健康状态"""
        try:
            client = get_http_client()
            response = await client.get('/health')
            return response.status_code == 200 and response.data.get('status') == 'healthy'
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    @staticmethod
    async def get_server_info() -> Optional[Dict[str, Any]]:
        """获取服务器信息"""
        try:
            client = get_http_client()
            response = await client.get('/server/info')
            if response.status_code == 200:
                return response.data
            return None
        except Exception as e:
            logger.error(f"Get server info failed: {e}")
            return None


# 向后兼容的工具函数
async def wait_for_daemon(timeout: float = 30.0) -> bool:
    """等待daemon启动"""
    import time
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if await HealthChecker.check_daemon_health():
            return True
        await asyncio.sleep(1)
    
    return False


def is_daemon_running() -> bool:
    """检查daemon是否在运行（同步版本）"""
    try:
        # 检查socket文件或PID文件
        from api.dependencies import get_config_manager
        config_manager = get_config_manager()
        
        socket_file = config_manager.get_paths()["app_data"] / "daemon.socket"
        port_file = config_manager.get_paths()["app_data"] / "daemon.port"
        
        return socket_file.exists() or port_file.exists()
    except Exception:
        return False


# 导出兼容性接口
__all__ = [
    'MockResponse',
    'MockHTTPClient', 
    'get_http_client',
    'RequestsCompatibility',
    'async_requests',
    'FastAPICompatibilityRequest',
    'create_mock_request',
    'HealthChecker',
    'wait_for_daemon',
    'is_daemon_running'
]