#!/usr/bin/env python3
"""
Linch Mind 统一错误码体系
定义所有系统错误代码和消息，确保错误处理的一致性
"""

from enum import IntEnum
from typing import Dict, Optional


class ErrorCode(IntEnum):
    """系统错误代码枚举"""

    # 成功代码
    SUCCESS = 0

    # 通用错误 (1000-1999)
    UNKNOWN_ERROR = 1000
    INVALID_REQUEST = 1001
    INVALID_PARAMETER = 1002
    INSUFFICIENT_PERMISSION = 1003
    RESOURCE_NOT_FOUND = 1004
    RESOURCE_ALREADY_EXISTS = 1005
    OPERATION_TIMEOUT = 1006
    OPERATION_CANCELLED = 1007
    RATE_LIMIT_EXCEEDED = 1008

    # IPC通信错误 (2000-2999)
    IPC_CONNECTION_FAILED = 2000
    IPC_CONNECTION_LOST = 2001
    IPC_PROTOCOL_ERROR = 2002
    IPC_TIMEOUT = 2003
    IPC_AUTHENTICATION_FAILED = 2004
    IPC_PERMISSION_DENIED = 2005
    IPC_MESSAGE_TOO_LARGE = 2006
    IPC_INVALID_MESSAGE_FORMAT = 2007
    IPC_SERVER_UNAVAILABLE = 2008
    IPC_CLIENT_DISCONNECTED = 2009

    # 数据库错误 (3000-3999)
    DATABASE_CONNECTION_FAILED = 3000
    DATABASE_QUERY_FAILED = 3001
    DATABASE_TRANSACTION_FAILED = 3002
    DATABASE_CONSTRAINT_VIOLATION = 3003
    DATABASE_DEADLOCK = 3004
    DATABASE_CORRUPTION = 3005
    DATABASE_MIGRATION_FAILED = 3006
    DATABASE_BACKUP_FAILED = 3007
    DATABASE_RESTORE_FAILED = 3008
    DATABASE_DISK_FULL = 3009

    # 连接器错误 (4000-4999)
    CONNECTOR_NOT_FOUND = 4000
    CONNECTOR_STARTUP_FAILED = 4001
    CONNECTOR_SHUTDOWN_FAILED = 4002
    CONNECTOR_CONFIGURATION_INVALID = 4003
    CONNECTOR_PROCESS_CRASHED = 4004
    CONNECTOR_COMMUNICATION_FAILED = 4005
    CONNECTOR_PERMISSION_DENIED = 4006
    CONNECTOR_RESOURCE_EXHAUSTED = 4007
    CONNECTOR_INCOMPATIBLE_VERSION = 4008
    CONNECTOR_DEPENDENCY_MISSING = 4009

    # 配置错误 (5000-5999)
    CONFIG_FILE_NOT_FOUND = 5000
    CONFIG_FILE_INVALID = 5001
    CONFIG_PARSE_ERROR = 5002
    CONFIG_VALIDATION_FAILED = 5003
    CONFIG_UPDATE_FAILED = 5004
    CONFIG_BACKUP_FAILED = 5005
    CONFIG_RESTORE_FAILED = 5006
    CONFIG_ACCESS_DENIED = 5007
    CONFIG_SCHEMA_MISMATCH = 5008
    CONFIG_ENCRYPTION_FAILED = 5009

    # 服务错误 (6000-6999)
    SERVICE_NOT_AVAILABLE = 6000
    SERVICE_STARTUP_FAILED = 6001
    SERVICE_SHUTDOWN_FAILED = 6002
    SERVICE_INITIALIZATION_FAILED = 6003
    SERVICE_DEPENDENCY_MISSING = 6004
    SERVICE_CIRCULAR_DEPENDENCY = 6005
    SERVICE_LIFECYCLE_ERROR = 6006
    SERVICE_HEALTH_CHECK_FAILED = 6007
    SERVICE_OVERLOADED = 6008
    SERVICE_MAINTENANCE_MODE = 6009

    # 存储错误 (7000-7999)
    STORAGE_READ_FAILED = 7000
    STORAGE_WRITE_FAILED = 7001
    STORAGE_DELETE_FAILED = 7002
    STORAGE_DISK_FULL = 7003
    STORAGE_PERMISSION_DENIED = 7004
    STORAGE_CORRUPTION = 7005
    STORAGE_ENCRYPTION_FAILED = 7006
    STORAGE_DECRYPTION_FAILED = 7007
    STORAGE_QUOTA_EXCEEDED = 7008
    STORAGE_BACKUP_FAILED = 7009

    # 网络和AI服务错误 (8000-8999)
    NETWORK_CONNECTION_FAILED = 8000
    NETWORK_TIMEOUT = 8001
    NETWORK_DNS_RESOLUTION_FAILED = 8002
    AI_SERVICE_UNAVAILABLE = 8003
    AI_SERVICE_QUOTA_EXCEEDED = 8004
    AI_SERVICE_AUTHENTICATION_FAILED = 8005
    AI_SERVICE_RATE_LIMITED = 8006
    AI_SERVICE_INVALID_RESPONSE = 8007
    AI_SERVICE_MODEL_NOT_FOUND = 8008
    AI_SERVICE_PROCESSING_FAILED = 8009

    # 系统资源错误 (9000-9999)
    MEMORY_ALLOCATION_FAILED = 9000
    CPU_OVERLOAD = 9001
    DISK_SPACE_INSUFFICIENT = 9002
    FILE_SYSTEM_ERROR = 9003
    PROCESS_LIMIT_EXCEEDED = 9004
    THREAD_LIMIT_EXCEEDED = 9005
    HANDLE_LIMIT_EXCEEDED = 9006
    SYSTEM_SHUTDOWN = 9007
    SYSTEM_RESTART_REQUIRED = 9008
    SYSTEM_MAINTENANCE = 9009


class ErrorSeverity(IntEnum):
    """错误严重程度"""

    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class ErrorCategory:
    """错误类别常量"""

    GENERAL = "general"
    IPC = "ipc"
    DATABASE = "database"
    CONNECTOR = "connector"
    CONFIG = "config"
    SERVICE = "service"
    STORAGE = "storage"
    NETWORK = "network"
    SYSTEM = "system"


class ErrorCodeInfo:
    """错误代码信息类"""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        description: str,
        category: str,
        severity: ErrorSeverity,
        recoverable: bool = True,
        user_friendly_message: Optional[str] = None,
    ):
        self.code = code
        self.message = message
        self.description = description
        self.category = category
        self.severity = severity
        self.recoverable = recoverable
        self.user_friendly_message = user_friendly_message or message

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "code": self.code,
            "message": self.message,
            "description": self.description,
            "category": self.category,
            "severity": self.severity,
            "recoverable": self.recoverable,
            "user_friendly_message": self.user_friendly_message,
        }


# 错误码信息映射
ERROR_CODE_MAP: Dict[ErrorCode, ErrorCodeInfo] = {
    # 成功
    ErrorCode.SUCCESS: ErrorCodeInfo(
        ErrorCode.SUCCESS,
        "Success",
        "操作成功完成",
        ErrorCategory.GENERAL,
        ErrorSeverity.INFO,
    ),
    # 通用错误
    ErrorCode.UNKNOWN_ERROR: ErrorCodeInfo(
        ErrorCode.UNKNOWN_ERROR,
        "Unknown Error",
        "未知错误",
        ErrorCategory.GENERAL,
        ErrorSeverity.ERROR,
        user_friendly_message="发生了未知错误，请稍后重试",
    ),
    ErrorCode.INVALID_REQUEST: ErrorCodeInfo(
        ErrorCode.INVALID_REQUEST,
        "Invalid Request",
        "无效的请求格式或参数",
        ErrorCategory.GENERAL,
        ErrorSeverity.WARNING,
        user_friendly_message="请求格式不正确",
    ),
    ErrorCode.RESOURCE_NOT_FOUND: ErrorCodeInfo(
        ErrorCode.RESOURCE_NOT_FOUND,
        "Resource Not Found",
        "请求的资源不存在",
        ErrorCategory.GENERAL,
        ErrorSeverity.WARNING,
        user_friendly_message="未找到请求的资源",
    ),
    # IPC错误
    ErrorCode.IPC_CONNECTION_FAILED: ErrorCodeInfo(
        ErrorCode.IPC_CONNECTION_FAILED,
        "IPC Connection Failed",
        "IPC连接建立失败",
        ErrorCategory.IPC,
        ErrorSeverity.ERROR,
        user_friendly_message="无法连接到服务，请检查服务状态",
    ),
    ErrorCode.IPC_CONNECTION_LOST: ErrorCodeInfo(
        ErrorCode.IPC_CONNECTION_LOST,
        "IPC Connection Lost",
        "IPC连接意外断开",
        ErrorCategory.IPC,
        ErrorSeverity.ERROR,
        user_friendly_message="与服务的连接已断开，正在尝试重新连接",
    ),
    ErrorCode.IPC_TIMEOUT: ErrorCodeInfo(
        ErrorCode.IPC_TIMEOUT,
        "IPC Timeout",
        "IPC操作超时",
        ErrorCategory.IPC,
        ErrorSeverity.WARNING,
        user_friendly_message="操作超时，请稍后重试",
    ),
    # 数据库错误
    ErrorCode.DATABASE_CONNECTION_FAILED: ErrorCodeInfo(
        ErrorCode.DATABASE_CONNECTION_FAILED,
        "Database Connection Failed",
        "数据库连接失败",
        ErrorCategory.DATABASE,
        ErrorSeverity.CRITICAL,
        recoverable=False,
        user_friendly_message="数据存储服务不可用",
    ),
    ErrorCode.DATABASE_QUERY_FAILED: ErrorCodeInfo(
        ErrorCode.DATABASE_QUERY_FAILED,
        "Database Query Failed",
        "数据库查询失败",
        ErrorCategory.DATABASE,
        ErrorSeverity.ERROR,
        user_friendly_message="数据查询失败，请稍后重试",
    ),
    # 连接器错误
    ErrorCode.CONNECTOR_NOT_FOUND: ErrorCodeInfo(
        ErrorCode.CONNECTOR_NOT_FOUND,
        "Connector Not Found",
        "指定的连接器不存在",
        ErrorCategory.CONNECTOR,
        ErrorSeverity.WARNING,
        user_friendly_message="未找到指定的连接器",
    ),
    ErrorCode.CONNECTOR_STARTUP_FAILED: ErrorCodeInfo(
        ErrorCode.CONNECTOR_STARTUP_FAILED,
        "Connector Startup Failed",
        "连接器启动失败",
        ErrorCategory.CONNECTOR,
        ErrorSeverity.ERROR,
        user_friendly_message="连接器启动失败，请检查配置",
    ),
    # 服务错误
    ErrorCode.SERVICE_NOT_AVAILABLE: ErrorCodeInfo(
        ErrorCode.SERVICE_NOT_AVAILABLE,
        "Service Not Available",
        "服务不可用",
        ErrorCategory.SERVICE,
        ErrorSeverity.ERROR,
        user_friendly_message="服务暂时不可用，请稍后重试",
    ),
    ErrorCode.SERVICE_DEPENDENCY_MISSING: ErrorCodeInfo(
        ErrorCode.SERVICE_DEPENDENCY_MISSING,
        "Service Dependency Missing",
        "服务依赖缺失",
        ErrorCategory.SERVICE,
        ErrorSeverity.CRITICAL,
        recoverable=False,
        user_friendly_message="系统配置不完整，请联系管理员",
    ),
}


def get_error_info(error_code: ErrorCode) -> ErrorCodeInfo:
    """获取错误代码信息"""
    return ERROR_CODE_MAP.get(error_code, ERROR_CODE_MAP[ErrorCode.UNKNOWN_ERROR])


def is_recoverable(error_code: ErrorCode) -> bool:
    """判断错误是否可恢复"""
    return get_error_info(error_code).recoverable


def get_user_friendly_message(error_code: ErrorCode) -> str:
    """获取用户友好的错误消息"""
    return get_error_info(error_code).user_friendly_message


def get_error_category(error_code: ErrorCode) -> str:
    """获取错误类别"""
    return get_error_info(error_code).category


def get_error_severity(error_code: ErrorCode) -> ErrorSeverity:
    """获取错误严重程度"""
    return get_error_info(error_code).severity


def create_error_response(
    error_code: ErrorCode, details: Optional[str] = None, context: Optional[Dict] = None
) -> Dict:
    """创建标准错误响应格式"""
    error_info = get_error_info(error_code)

    response = {
        "success": False,
        "error": {
            "code": error_code,
            "message": error_info.message,
            "category": error_info.category,
            "severity": error_info.severity.name,
            "recoverable": error_info.recoverable,
            "user_message": error_info.user_friendly_message,
        },
    }

    if details:
        response["error"]["details"] = details

    if context:
        response["error"]["context"] = context

    return response


# 导出常用函数
__all__ = [
    "ErrorCode",
    "ErrorSeverity",
    "ErrorCategory",
    "ErrorCodeInfo",
    "get_error_info",
    "is_recoverable",
    "get_user_friendly_message",
    "get_error_category",
    "get_error_severity",
    "create_error_response",
]
