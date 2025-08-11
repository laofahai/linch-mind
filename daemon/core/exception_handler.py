#!/usr/bin/env python3
"""
结构化异常处理框架
替换裸露的 except: 和 except Exception: 语句
提供统一的异常处理、日志记录和错误响应机制
"""

import asyncio
import functools
import logging
import time
from contextlib import contextmanager
from typing import Any, Callable, Dict, Optional, TypeVar

# 类型变量
T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


class LinchMindException(Exception):
    """Linch Mind基础异常类"""

    def __init__(
        self, message: str, error_code: str = "UNKNOWN_ERROR", details: Dict = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = time.time()


class IPCConnectionError(LinchMindException):
    """IPC连接相关异常"""


class DatabaseError(LinchMindException):
    """数据库操作异常"""


class ConnectorError(LinchMindException):
    """连接器相关异常"""


class ServiceUnavailableError(LinchMindException):
    """服务不可用异常"""


class ConfigurationError(LinchMindException):
    """配置错误异常"""


class ValidationError(LinchMindException):
    """数据验证异常"""


class ExceptionClassifier:
    """异常分类器 - 将通用异常转换为具体的业务异常"""

    IPC_KEYWORDS = ["socket", "pipe", "ipc", "connection", "timeout"]
    DB_KEYWORDS = ["database", "sql", "session", "transaction", "query"]
    CONNECTOR_KEYWORDS = ["connector", "plugin", "execution", "process"]
    CONFIG_KEYWORDS = ["config", "setting", "parameter", "environment"]

    @classmethod
    def classify_exception(
        cls, exc: Exception, context: str = ""
    ) -> LinchMindException:
        """将通用异常分类为具体的业务异常"""
        message = str(exc).lower()
        context = context.lower()

        # IPC相关异常
        if any(
            keyword in message or keyword in context for keyword in cls.IPC_KEYWORDS
        ):
            return IPCConnectionError(
                str(exc), "IPC_ERROR", {"original_type": type(exc).__name__}
            )

        # 数据库相关异常
        if any(keyword in message or keyword in context for keyword in cls.DB_KEYWORDS):
            return DatabaseError(
                str(exc), "DATABASE_ERROR", {"original_type": type(exc).__name__}
            )

        # 连接器相关异常
        if any(
            keyword in message or keyword in context
            for keyword in cls.CONNECTOR_KEYWORDS
        ):
            return ConnectorError(
                str(exc), "CONNECTOR_ERROR", {"original_type": type(exc).__name__}
            )

        # 配置相关异常
        if any(
            keyword in message or keyword in context for keyword in cls.CONFIG_KEYWORDS
        ):
            return ConfigurationError(
                str(exc), "CONFIG_ERROR", {"original_type": type(exc).__name__}
            )

        # 默认为通用LinchMind异常
        return LinchMindException(
            str(exc), "UNKNOWN_ERROR", {"original_type": type(exc).__name__}
        )


class StructuredExceptionHandler:
    """结构化异常处理器"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.error_counts = {}  # 错误计数器
        self.last_errors = {}  # 最后错误时间

    def handle_with_logging(
        self, operation: str, reraise: bool = True, classify: bool = True
    ):
        """装饰器：为函数添加结构化异常处理

        Args:
            operation: 操作描述
            reraise: 是否重新抛出异常
            classify: 是否对异常进行分类
        """

        def decorator(func: F) -> F:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except LinchMindException:
                    # 已经是结构化异常，直接记录并传播
                    if reraise:
                        raise
                except Exception as e:
                    # 转换为结构化异常
                    if classify:
                        structured_exc = ExceptionClassifier.classify_exception(
                            e, operation
                        )
                    else:
                        structured_exc = LinchMindException(
                            str(e),
                            "OPERATION_ERROR",
                            {"operation": operation, "original_type": type(e).__name__},
                        )

                    self._log_exception(structured_exc, operation, exc_info=True)

                    if reraise:
                        raise structured_exc
                    return None

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except LinchMindException:
                    if reraise:
                        raise
                except Exception as e:
                    if classify:
                        structured_exc = ExceptionClassifier.classify_exception(
                            e, operation
                        )
                    else:
                        structured_exc = LinchMindException(
                            str(e),
                            "OPERATION_ERROR",
                            {"operation": operation, "original_type": type(e).__name__},
                        )

                    self._log_exception(structured_exc, operation, exc_info=True)

                    if reraise:
                        raise structured_exc
                    return None

            # 检查是否为异步函数
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    def _log_exception(
        self, exc: LinchMindException, operation: str, exc_info: bool = False
    ):
        """记录结构化异常"""
        error_key = f"{operation}:{exc.error_code}"

        # 更新错误统计
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        self.last_errors[error_key] = exc.timestamp

        # 构建日志消息
        log_data = {
            "operation": operation,
            "error_code": exc.error_code,
            "message": exc.message,
            "count": self.error_counts[error_key],
            "details": exc.details,
        }

        # 根据异常类型选择日志级别
        if isinstance(exc, (ServiceUnavailableError, ConfigurationError)):
            self.logger.critical(
                f"严重错误 in {operation}: {exc.message}",
                extra=log_data,
                exc_info=exc_info,
            )
        elif isinstance(exc, (DatabaseError, IPCConnectionError)):
            self.logger.error(
                f"操作失败 in {operation}: {exc.message}",
                extra=log_data,
                exc_info=exc_info,
            )
        elif isinstance(exc, (ValidationError, ConnectorError)):
            self.logger.warning(
                f"业务异常 in {operation}: {exc.message}", extra=log_data
            )
        else:
            self.logger.error(
                f"未知错误 in {operation}: {exc.message}",
                extra=log_data,
                exc_info=exc_info,
            )

    @contextmanager
    def handle_context(self, operation: str, reraise: bool = True):
        """上下文管理器：处理代码块中的异常"""
        try:
            yield
        except LinchMindException:
            if reraise:
                raise
        except Exception as e:
            structured_exc = ExceptionClassifier.classify_exception(e, operation)
            self._log_exception(structured_exc, operation, exc_info=True)

            if reraise:
                raise structured_exc

    def get_error_summary(self) -> Dict[str, Any]:
        """获取错误统计摘要"""
        return {
            "total_error_types": len(self.error_counts),
            "error_counts": self.error_counts.copy(),
            "recent_errors": {
                k: v
                for k, v in self.last_errors.items()
                if time.time() - v < 3600  # 最近1小时的错误
            },
        }


# 全局异常处理器实例
_global_handler = StructuredExceptionHandler()


def get_exception_handler(
    logger: Optional[logging.Logger] = None,
) -> StructuredExceptionHandler:
    """获取异常处理器实例

    Args:
        logger: 可选的日志记录器，如果不提供则使用全局实例
    """
    if logger:
        return StructuredExceptionHandler(logger)
    return _global_handler


# 便捷装饰器函数
def handle_exceptions(
    operation: str,
    reraise: bool = True,
    classify: bool = True,
    logger: logging.Logger = None,
):
    """便捷的异常处理装饰器"""
    handler = get_exception_handler(logger)
    return handler.handle_with_logging(operation, reraise, classify)


def safe_execute(
    func: Callable[..., T],
    *args,
    default: T = None,
    logger: logging.Logger = None,
    **kwargs,
) -> T:
    """安全执行函数，捕获所有异常并返回默认值"""
    handler = get_exception_handler(logger)

    try:
        return func(*args, **kwargs)
    except Exception as e:
        structured_exc = ExceptionClassifier.classify_exception(e, func.__name__)
        handler._log_exception(structured_exc, func.__name__)
        return default


async def safe_execute_async(
    func: Callable[..., T],
    *args,
    default: T = None,
    logger: logging.Logger = None,
    **kwargs,
) -> T:
    """安全执行异步函数，捕获所有异常并返回默认值"""
    handler = get_exception_handler(logger)

    try:
        return await func(*args, **kwargs)
    except Exception as e:
        structured_exc = ExceptionClassifier.classify_exception(e, func.__name__)
        handler._log_exception(structured_exc, func.__name__)
        return default


# 异常转换辅助函数
def ensure_structured_exception(
    exc: Exception, context: str = ""
) -> LinchMindException:
    """确保异常是结构化异常"""
    if isinstance(exc, LinchMindException):
        return exc
    return ExceptionClassifier.classify_exception(exc, context)


def create_error_response(exc: Exception, request_id: str = None) -> Dict[str, Any]:
    """为API响应创建错误信息"""
    structured_exc = ensure_structured_exception(exc)

    return {
        "success": False,
        "error": {
            "code": structured_exc.error_code,
            "message": structured_exc.message,
            "details": structured_exc.details,
        },
        "request_id": request_id,
        "timestamp": structured_exc.timestamp,
    }


if __name__ == "__main__":
    # 测试异常处理框架
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    handler = StructuredExceptionHandler(logger)

    @handler.handle_with_logging("test_operation")
    def test_function():
        raise ValueError("测试异常")

    try:
        test_function()
    except LinchMindException as e:
        print(f"捕获结构化异常: {e.error_code} - {e.message}")

    # 测试异常统计
    summary = handler.get_error_summary()
    print(f"错误统计: {summary}")
