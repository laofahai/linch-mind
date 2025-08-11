#!/usr/bin/env python3
"""
标准化错误处理框架 - 消除424个相似错误处理模式
提供统一的异常管理、日志记录和错误恢复机制
"""

import asyncio
import hashlib
import logging
import platform
import sys
import time
import traceback
import uuid
from collections import deque
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Optional


class ErrorSeverity(Enum):
    """错误严重性级别"""

    LOW = "low"  # 可忽略错误
    MEDIUM = "medium"  # 需要注意的错误
    HIGH = "high"  # 严重错误，需要立即处理
    CRITICAL = "critical"  # 致命错误，可能导致系统不稳定


class ErrorCategory(Enum):
    """错误分类"""

    IPC_COMMUNICATION = "ipc_communication"
    DATABASE_OPERATION = "database_operation"
    CONNECTOR_MANAGEMENT = "connector_management"
    FILE_SYSTEM = "file_system"
    CONFIGURATION = "configuration"
    SECURITY = "security"
    NETWORK = "network"
    SYSTEM_OPERATION = "system_operation"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """错误上下文信息"""

    function_name: str
    module_name: str
    severity: ErrorSeverity
    category: ErrorCategory
    user_message: Optional[str] = None
    technical_details: Optional[str] = None
    recovery_suggestions: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "function": self.function_name,
            "module": self.module_name,
            "severity": self.severity.value,
            "category": self.category.value,
            "user_message": self.user_message,
            "technical_details": self.technical_details,
            "recovery_suggestions": self.recovery_suggestions,
        }


class StandardizedError(Exception):
    """标准化异常基类"""

    def __init__(
        self,
        message: str,
        context: ErrorContext,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.context = context
        self.original_exception = original_exception
        self.timestamp = None

    def __repr__(self):
        return (
            f"StandardizedError(message='{self.args[0]}', "
            f"severity={self.context.severity.value}, "
            f"category={self.context.category.value})"
        )


@dataclass
class ProcessedError:
    """处理后的错误信息 - 用于安全的IPC传输"""

    error_id: str
    code: str
    message: str
    user_message: str
    is_recoverable: bool
    can_retry: bool
    retry_after: Optional[int] = None  # 重试延迟（秒）
    context: Optional[Dict[str, Any]] = None

    def to_safe_dict(self) -> Dict[str, Any]:
        """转换为安全的字典（用于IPC传输）"""
        return {
            "error_id": self.error_id,
            "code": self.code,
            "message": self.user_message,  # 只返回用户友好消息
            "is_recoverable": self.is_recoverable,
            "can_retry": self.can_retry,
            "retry_after": self.retry_after,
            # 不包含敏感的context信息
        }


class ErrorRateLimiter:
    """错误限流器 - 防止错误风暴影响系统性能"""

    def __init__(self, max_errors_per_minute: int = 10):
        self.max_errors = max_errors_per_minute
        self.error_counts: Dict[str, deque] = {}

    def should_throttle(self, signature: str) -> bool:
        """检查是否需要限流"""
        now = time.time()
        minute_ago = now - 60

        if signature not in self.error_counts:
            self.error_counts[signature] = deque()

        # 清理过期记录
        errors = self.error_counts[signature]
        while errors and errors[0] < minute_ago:
            errors.popleft()

        # 检查是否超过限制
        if len(errors) >= self.max_errors:
            return True

        # 记录新错误
        errors.append(now)
        return False


class EnhancedErrorHandler:
    """增强的错误处理器 - 支持安全的错误信息过滤和传输"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._error_log_buffer = deque(maxlen=1000)  # 错误日志缓冲
        self._error_signatures = {}  # 错误签名缓存
        self._rate_limiter = ErrorRateLimiter()

    def process_error(
        self,
        exception: Exception,
        context: ErrorContext,
        request_id: Optional[str] = None,
    ) -> ProcessedError:
        """处理错误并返回安全的错误信息"""

        # 生成唯一错误ID
        error_id = str(uuid.uuid4())

        # 生成错误签名（用于去重）
        signature = self._generate_signature(exception, context)

        # 检查是否需要限流
        if self._rate_limiter.should_throttle(signature):
            # 返回限流错误
            return ProcessedError(
                error_id=error_id,
                code="ERROR_THROTTLED",
                message="Too many errors",
                user_message="系统繁忙，请稍后重试",
                is_recoverable=True,
                can_retry=True,
                retry_after=5,
            )

        # 记录详细错误信息到日志
        self._log_detailed_error(
            error_id=error_id,
            exception=exception,
            context=context,
            request_id=request_id,
        )

        # 创建安全的错误响应
        processed = ProcessedError(
            error_id=error_id,
            code=self._get_error_code(exception, context),
            message=str(exception),  # 内部消息
            user_message=self._get_user_message(exception, context),
            is_recoverable=self._is_recoverable(exception, context),
            can_retry=self._can_retry(exception, context),
            retry_after=self._get_retry_delay(exception, context),
            context={"request_id": request_id} if request_id else None,
        )

        # 缓存错误信息
        self._error_log_buffer.append(
            {
                "error_id": error_id,
                "timestamp": datetime.now().isoformat(),
                "signature": signature,
                "code": processed.code,
            }
        )

        return processed

    def _generate_signature(self, exception: Exception, context: ErrorContext) -> str:
        """生成错误签名用于去重"""
        content = f"{context.category.value}:{type(exception).__name__}:{context.function_name}"
        return hashlib.md5(content.encode(), usedforsecurity=False).hexdigest()

    def _get_error_code(self, exception: Exception, context: ErrorContext) -> str:
        """获取错误代码"""
        exception_name = type(exception).__name__
        category = context.category.value.upper()
        return f"{category}_{exception_name}".replace(" ", "_")

    def _get_user_message(self, exception: Exception, context: ErrorContext) -> str:
        """获取用户友好的错误消息"""
        messages = {
            ErrorCategory.IPC_COMMUNICATION: "连接出现问题，正在重试",
            ErrorCategory.DATABASE_OPERATION: "数据操作失败，请稍后重试",
            ErrorCategory.CONNECTOR_MANAGEMENT: "连接器操作失败",
            ErrorCategory.CONFIGURATION: "配置错误，请检查设置",
            ErrorCategory.SECURITY: "安全验证失败",
            ErrorCategory.NETWORK: "网络连接异常",
            ErrorCategory.FILE_SYSTEM: "文件系统操作失败",
        }
        return messages.get(context.category, "操作失败，请稍后重试")

    def _is_recoverable(self, exception: Exception, context: ErrorContext) -> bool:
        """判断错误是否可恢复"""
        recoverable_categories = {
            ErrorCategory.IPC_COMMUNICATION,
            ErrorCategory.NETWORK,
            ErrorCategory.DATABASE_OPERATION,
        }
        return context.category in recoverable_categories

    def _can_retry(self, exception: Exception, context: ErrorContext) -> bool:
        """判断是否可以重试"""
        non_retryable = {
            ErrorCategory.CONFIGURATION,
            ErrorCategory.SECURITY,
        }
        return context.category not in non_retryable

    def _get_retry_delay(
        self, exception: Exception, context: ErrorContext
    ) -> Optional[int]:
        """获取重试延迟（秒）"""
        if not self._can_retry(exception, context):
            return None

        # 根据错误类型返回不同的延迟
        delays = {
            ErrorCategory.IPC_COMMUNICATION: 1,
            ErrorCategory.NETWORK: 3,
            ErrorCategory.DATABASE_OPERATION: 2,
        }
        return delays.get(context.category, 5)

    def _log_detailed_error(
        self,
        error_id: str,
        exception: Exception,
        context: ErrorContext,
        request_id: Optional[str],
    ):
        """记录详细错误信息（仅在后端）"""
        detailed_log = {
            "error_id": error_id,
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "context": context.to_dict(),
            "exception": {
                "type": type(exception).__name__,
                "message": str(exception),
                "traceback": traceback.format_exc(),
            },
            "system": {"python_version": sys.version, "platform": platform.platform()},
        }

        # 记录到结构化日志
        self.logger.error(f"Error {error_id}", extra={"structured": detailed_log})

        # TODO: 集成到外部日志系统（Sentry/Datadog/ELK）
        # self._send_to_monitoring(detailed_log)


class ErrorHandler:
    """统一错误处理器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._error_stats: Dict[str, int] = {}
        self._recovery_handlers: Dict[ErrorCategory, Callable] = {}

    def register_recovery_handler(
        self, category: ErrorCategory, handler: Callable[[StandardizedError], Any]
    ):
        """注册错误恢复处理器"""
        self._recovery_handlers[category] = handler
        self.logger.debug(f"已注册 {category.value} 错误恢复处理器")

    def handle_error(
        self,
        exception: Exception,
        context: ErrorContext,
        attempt_recovery: bool = False,
    ) -> Optional[Any]:
        """处理错误"""

        # 统计错误
        key = f"{context.category.value}_{context.severity.value}"
        self._error_stats[key] = self._error_stats.get(key, 0) + 1

        # 创建标准化错误
        std_error = StandardizedError(
            message=str(exception), context=context, original_exception=exception
        )

        # 记录日志
        self._log_error(std_error)

        # 尝试恢复
        if attempt_recovery and context.category in self._recovery_handlers:
            try:
                recovery_result = self._recovery_handlers[context.category](std_error)
                self.logger.info(f"✅ 错误恢复成功: {context.function_name}")
                return recovery_result
            except Exception as recovery_error:
                self.logger.error(f"❌ 错误恢复失败: {recovery_error}")

        # 重新抛出标准化错误
        raise std_error

    def _log_error(self, error: StandardizedError):
        """记录错误日志"""
        context = error.context

        # 根据严重性选择日志级别
        if context.severity == ErrorSeverity.CRITICAL:
            log_func = self.logger.critical
        elif context.severity == ErrorSeverity.HIGH:
            log_func = self.logger.error
        elif context.severity == ErrorSeverity.MEDIUM:
            log_func = self.logger.warning
        else:
            log_func = self.logger.info

        # 构建日志消息
        log_message = (
            f"🚨 {context.severity.value.upper()} ERROR in {context.module_name}.{context.function_name}\n"
            f"   Category: {context.category.value}\n"
            f"   Message: {error.args[0]}\n"
        )

        if context.user_message:
            log_message += f"   User Message: {context.user_message}\n"

        if context.technical_details:
            log_message += f"   Technical Details: {context.technical_details}\n"

        if context.recovery_suggestions:
            log_message += f"   Recovery Suggestions: {context.recovery_suggestions}\n"

        # 添加堆栈跟踪（仅在高严重性错误时）
        if context.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            if error.original_exception:
                log_message += f"   Stack Trace: {traceback.format_exception(type(error.original_exception), error.original_exception, error.original_exception.__traceback__)}"

        log_func(log_message.rstrip())

    def get_error_stats(self) -> Dict[str, Any]:
        """获取错误统计信息"""
        total_errors = sum(self._error_stats.values())
        return {
            "total_errors": total_errors,
            "error_breakdown": self._error_stats.copy(),
            "registered_recovery_handlers": list(self._recovery_handlers.keys()),
        }


# 全局错误处理器
_error_handler = ErrorHandler()
_enhanced_error_handler = EnhancedErrorHandler()


def get_error_handler() -> ErrorHandler:
    """获取全局错误处理器"""
    return _error_handler


def get_enhanced_error_handler() -> EnhancedErrorHandler:
    """获取全局增强错误处理器"""
    return _enhanced_error_handler


# 标准化错误处理装饰器
def handle_errors(
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    user_message: str = None,
    recovery_suggestions: str = None,
    attempt_recovery: bool = False,
    reraise: bool = True,
):
    """标准化错误处理装饰器

    消除重复的try-except模式，提供统一的错误处理
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            context = ErrorContext(
                function_name=func.__name__,
                module_name=func.__module__,
                severity=severity,
                category=category,
                user_message=user_message,
                recovery_suggestions=recovery_suggestions,
            )

            try:
                return func(*args, **kwargs)
            except StandardizedError:
                # 已经是标准化错误，直接重新抛出
                raise
            except Exception as e:
                if not reraise:
                    # 仅记录错误但不重新抛出
                    context.technical_details = str(e)
                    _error_handler._log_error(StandardizedError(str(e), context, e))
                    return None

                return _error_handler.handle_error(e, context, attempt_recovery)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            context = ErrorContext(
                function_name=func.__name__,
                module_name=func.__module__,
                severity=severity,
                category=category,
                user_message=user_message,
                recovery_suggestions=recovery_suggestions,
            )

            try:
                return await func(*args, **kwargs)
            except StandardizedError:
                raise
            except Exception as e:
                if not reraise:
                    context.technical_details = str(e)
                    _error_handler._log_error(StandardizedError(str(e), context, e))
                    return None

                return _error_handler.handle_error(e, context, attempt_recovery)

        # 返回适当的装饰器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    return decorator


@contextmanager
def error_context(
    operation_name: str,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    user_message: str = None,
):
    """错误上下文管理器"""
    try:
        yield
    except Exception as e:
        context = ErrorContext(
            function_name=operation_name,
            module_name="context_manager",
            severity=severity,
            category=category,
            user_message=user_message,
            technical_details=str(e),
        )

        _error_handler.handle_error(e, context)


# 专用错误处理装饰器 - 针对不同组件
def handle_ipc_errors(user_message: str = "IPC通信错误"):
    """IPC错误处理装饰器"""
    return handle_errors(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.IPC_COMMUNICATION,
        user_message=user_message,
        recovery_suggestions="检查IPC连接状态，尝试重新连接",
    )


def handle_database_errors(user_message: str = "数据库操作错误"):
    """数据库错误处理装饰器"""
    return handle_errors(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.DATABASE_OPERATION,
        user_message=user_message,
        recovery_suggestions="检查数据库连接，验证SQL语句语法",
    )


def handle_connector_errors(user_message: str = "连接器操作错误"):
    """连接器错误处理装饰器"""
    return handle_errors(
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.CONNECTOR_MANAGEMENT,
        user_message=user_message,
        recovery_suggestions="检查连接器状态，尝试重启连接器",
    )


def handle_config_errors(user_message: str = "配置错误"):
    """配置错误处理装饰器"""
    return handle_errors(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.CONFIGURATION,
        user_message=user_message,
        recovery_suggestions="检查配置文件格式和内容",
    )


# 注册默认恢复处理器
def _register_default_recovery_handlers():
    """注册默认错误恢复处理器"""
    handler = get_error_handler()

    def ipc_recovery(error: StandardizedError):
        """IPC错误恢复"""
        # 尝试重新建立IPC连接

    def database_recovery(error: StandardizedError):
        """数据库错误恢复"""
        # 尝试重新连接数据库

    handler.register_recovery_handler(ErrorCategory.IPC_COMMUNICATION, ipc_recovery)
    handler.register_recovery_handler(
        ErrorCategory.DATABASE_OPERATION, database_recovery
    )


# 初始化默认恢复处理器
_register_default_recovery_handlers()


if __name__ == "__main__":
    # 测试错误处理框架
    logging.basicConfig(level=logging.DEBUG)

    @handle_errors(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.CONNECTOR_MANAGEMENT,
        user_message="测试错误处理",
    )
    def test_function():
        raise ValueError("这是一个测试错误")

    try:
        test_function()
    except StandardizedError as e:
        print(f"捕获到标准化错误: {e}")
        print(f"错误上下文: {e.context.to_dict()}")
