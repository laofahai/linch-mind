"""
纯IPC通信协议 - 完全独立于HTTP概念
定义统一的数据交换格式和错误处理体系
"""

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union


class IPCErrorCode(Enum):
    """IPC特定错误码体系"""

    # 连接和认证错误
    CONNECTION_FAILED = "IPC_CONNECTION_FAILED"
    AUTH_REQUIRED = "IPC_AUTH_REQUIRED"
    AUTH_FAILED = "IPC_AUTH_FAILED"
    CLIENT_DISCONNECTED = "IPC_CLIENT_DISCONNECTED"

    # 请求处理错误
    INVALID_REQUEST = "IPC_INVALID_REQUEST"
    MISSING_PARAMETER = "IPC_MISSING_PARAMETER"
    INVALID_PARAMETER = "IPC_INVALID_PARAMETER"
    REQUEST_TIMEOUT = "IPC_REQUEST_TIMEOUT"

    # 连接器相关错误
    CONNECTOR_NOT_FOUND = "CONNECTOR_NOT_FOUND"
    CONNECTOR_CONFIG_INVALID = "CONNECTOR_CONFIG_INVALID"
    CONNECTOR_START_FAILED = "CONNECTOR_START_FAILED"
    CONNECTOR_STOP_FAILED = "CONNECTOR_STOP_FAILED"
    CONNECTOR_ALREADY_RUNNING = "CONNECTOR_ALREADY_RUNNING"
    CONNECTOR_NOT_RUNNING = "CONNECTOR_NOT_RUNNING"

    # 系统错误
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    DATABASE_ERROR = "DATABASE_ERROR"

    # 资源错误
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_LOCKED = "RESOURCE_LOCKED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"


@dataclass
class IPCMessage:
    """IPC基础消息类"""

    method: str
    path: str
    data: Dict[str, Any] = None
    headers: Dict[str, str] = None
    query_params: Dict[str, Any] = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.headers is None:
            self.headers = {}
        if self.query_params is None:
            self.query_params = {}

    def to_json(self) -> str:
        """序列化为JSON字符串"""
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "IPCMessage":
        """从JSON字符串反序列化"""
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class IPCError:
    """IPC错误信息"""

    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"code": self.code, "message": self.message}
        if self.details:
            result["details"] = self.details
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IPCError":
        return cls(
            code=data["code"], message=data["message"], details=data.get("details")
        )


@dataclass
class IPCMetadata:
    """IPC元数据"""

    timestamp: str
    request_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"timestamp": self.timestamp}
        if self.request_id:
            result["request_id"] = self.request_id
        return result

    @classmethod
    def create(cls, request_id: Optional[str] = None) -> "IPCMetadata":
        return cls(
            timestamp=datetime.now().isoformat(),
            request_id=request_id or str(uuid.uuid4()),
        )


@dataclass
class IPCResponse:
    """
    纯IPC响应格式 - 完全独立于HTTP概念

    标准格式:
    {
        "success": boolean,
        "data": object | null,
        "error": {
            "code": string,
            "message": string,
            "details": object | null
        } | null,
        "metadata": {
            "timestamp": string,
            "request_id": string | null
        }
    }
    """

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[IPCError] = None
    metadata: Optional[IPCMetadata] = None

    def __post_init__(self):
        """确保元数据存在"""
        if self.metadata is None:
            self.metadata = IPCMetadata.create()

    @classmethod
    def success_response(
        cls, data: Optional[Dict[str, Any]] = None, request_id: Optional[str] = None
    ) -> "IPCResponse":
        """创建成功响应"""
        return cls(
            success=True, data=data or {}, metadata=IPCMetadata.create(request_id)
        )

    @classmethod
    def error_response(
        cls,
        error_code: Union[str, IPCErrorCode],
        message: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> "IPCResponse":
        """创建错误响应"""
        error_code_str = (
            error_code.value if isinstance(error_code, IPCErrorCode) else error_code
        )

        return cls(
            success=False,
            error=IPCError(code=error_code_str, message=message, details=details),
            metadata=IPCMetadata.create(request_id),
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "success": self.success,
            "data": self.data,
            "metadata": self.metadata.to_dict() if self.metadata else {},
        }

        if self.error:
            result["error"] = self.error.to_dict()
        else:
            result["error"] = None

        return result

    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IPCResponse":
        """从字典创建响应"""
        error = None
        if data.get("error"):
            error = IPCError.from_dict(data["error"])

        metadata = None
        if data.get("metadata"):
            metadata = IPCMetadata(
                timestamp=data["metadata"]["timestamp"],
                request_id=data["metadata"].get("request_id"),
            )

        return cls(
            success=data["success"],
            data=data.get("data"),
            error=error,
            metadata=metadata,
        )

    @classmethod
    def from_json(cls, json_str: str) -> "IPCResponse":
        """从JSON字符串创建响应"""
        return cls.from_dict(json.loads(json_str))


@dataclass
class IPCRequest:
    """IPC请求对象"""

    method: str
    path: str
    data: Optional[Dict[str, Any]] = None
    query_params: Optional[Dict[str, Any]] = None
    path_params: Optional[Dict[str, str]] = None
    request_id: Optional[str] = None

    def __post_init__(self):
        """确保request_id和headers存在"""
        if self.request_id is None:
            self.request_id = str(uuid.uuid4())
        # 初始化headers属性
        if not hasattr(self, "_headers"):
            self._headers = {}

    @property
    def headers(self) -> Dict[str, str]:
        """获取请求头部"""
        return getattr(self, "_headers", {})

    def get_query(self, name: str, default: Any = None) -> Any:
        """获取查询参数"""
        if not self.query_params:
            return default
        return self.query_params.get(name, default)

    def get_header(self, name: str, default: Any = None) -> Any:
        """获取请求头部信息"""
        # 头部信息由IPC服务器设置在_headers属性中
        headers = getattr(self, "_headers", {})
        return headers.get(name, default)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "method": self.method,
            "path": self.path,
            "data": self.data,
            "query_params": self.query_params,
            "path_params": self.path_params,
            "request_id": self.request_id,
        }

    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IPCRequest":
        """从字典创建请求"""
        return cls(
            method=data["method"],
            path=data["path"],
            data=data.get("data"),
            query_params=data.get("query_params"),
            path_params=data.get("path_params"),
            request_id=data.get("request_id"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "IPCRequest":
        """从JSON字符串创建请求"""
        return cls.from_dict(json.loads(json_str))


# 常用的响应工厂函数


def success_response(
    data: Optional[Dict[str, Any]] = None, request_id: Optional[str] = None
) -> IPCResponse:
    """创建成功响应的便捷函数"""
    return IPCResponse.success_response(data, request_id)


def connection_failed_response(
    message: str, details: Optional[Dict[str, Any]] = None
) -> IPCResponse:
    """连接失败响应"""
    return IPCResponse.error_response(IPCErrorCode.CONNECTION_FAILED, message, details)


def auth_required_response(message: str = "Authentication required") -> IPCResponse:
    """认证要求响应"""
    return IPCResponse.error_response(IPCErrorCode.AUTH_REQUIRED, message)


def invalid_request_response(
    message: str, details: Optional[Dict[str, Any]] = None
) -> IPCResponse:
    """无效请求响应"""
    return IPCResponse.error_response(IPCErrorCode.INVALID_REQUEST, message, details)


def connector_not_found_response(connector_id: str) -> IPCResponse:
    """连接器未找到响应"""
    return IPCResponse.error_response(
        IPCErrorCode.CONNECTOR_NOT_FOUND,
        f"Connector '{connector_id}' not found",
        {"connector_id": connector_id},
    )


def internal_error_response(
    message: str, details: Optional[Dict[str, Any]] = None
) -> IPCResponse:
    """内部错误响应"""
    return IPCResponse.error_response(IPCErrorCode.INTERNAL_ERROR, message, details)


def resource_not_found_response(resource_type: str, resource_id: str) -> IPCResponse:
    """资源未找到响应"""
    return IPCResponse.error_response(
        IPCErrorCode.RESOURCE_NOT_FOUND,
        f"{resource_type} '{resource_id}' not found",
        {"resource_type": resource_type, "resource_id": resource_id},
    )
