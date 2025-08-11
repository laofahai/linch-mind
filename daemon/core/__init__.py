#!/usr/bin/env python3
"""
Linch Mind Daemon 核心模块

提供统一的架构组件:
- 异常处理框架 (exception_handler)
- 依赖注入容器 (container)  
- 数据库管理器 (database_manager)

这些模块旨在替换分散的全局单例和裸露异常处理，
提供一致、可测试、高性能的基础设施。
"""

# 依赖注入容器
from .container import (
    CircularDependencyError,
    ServiceContainer,
    ServiceDescriptor,
    ServiceLifecycle,
    ServiceLifecycleError,
    ServiceNotRegisteredError,
    get_container,
    inject,
    injectable,
    register_scoped,
    register_singleton,
    register_transient,
)

# 数据库管理
from .database_manager import (
    DatabaseConfig,
    DatabaseManager,
    get_async_database_session,
    get_database_manager,
    get_database_session,
    initialize_database_manager,
    with_async_database_session,
    with_database_session,
)

# 错误代码体系
from .error_codes import (
    ErrorCategory,
    ErrorCode,
    ErrorCodeInfo,
    ErrorSeverity,
    create_error_response,
    get_error_category,
    get_error_info,
    get_error_severity,
    get_user_friendly_message,
    is_recoverable,
)

# 异常处理
from .exception_handler import (
    ConfigurationError,
    ConnectorError,
    DatabaseError,
    ExceptionClassifier,
    IPCConnectionError,
    LinchMindException,
    ServiceUnavailableError,
    StructuredExceptionHandler,
    ValidationError,
    create_error_response,
    get_exception_handler,
    handle_exceptions,
    safe_execute,
    safe_execute_async,
)

__all__ = [
    # 异常处理
    "LinchMindException",
    "IPCConnectionError",
    "DatabaseError",
    "ConnectorError",
    "ServiceUnavailableError",
    "ConfigurationError",
    "ValidationError",
    "StructuredExceptionHandler",
    "ExceptionClassifier",
    "get_exception_handler",
    "handle_exceptions",
    "safe_execute",
    "safe_execute_async",
    "create_error_response",
    # 依赖注入
    "ServiceContainer",
    "ServiceLifecycle",
    "ServiceDescriptor",
    "ServiceNotRegisteredError",
    "CircularDependencyError",
    "ServiceLifecycleError",
    "get_container",
    "inject",
    "injectable",
    "register_singleton",
    "register_transient",
    "register_scoped",
    # 数据库管理
    "DatabaseConfig",
    "DatabaseManager",
    "initialize_database_manager",
    "get_database_manager",
    "get_database_session",
    "get_async_database_session",
    "with_database_session",
    "with_async_database_session",
    # 错误代码体系
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

# 版本信息
__version__ = "1.0.0"
__author__ = "Linch Mind Team"
__description__ = "Core infrastructure components for Linch Mind Daemon"
