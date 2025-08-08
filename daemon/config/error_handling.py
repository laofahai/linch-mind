#!/usr/bin/env python3
"""
统一错误处理和日志记录 - Session V61 代码质量提升
标准化错误处理模式，统一日志记录格式
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Type


class ErrorLevel(Enum):
    """错误级别枚举"""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ConfigError(Exception):
    """配置相关错误基类"""

    def __init__(
        self, message: str, error_code: str = None, details: Dict[str, Any] = None
    ):
        self.message = message
        self.error_code = error_code or "CONFIG_ERROR"
        self.details = details or {}
        self.timestamp = datetime.now()
        super().__init__(self.message)


class ConfigValidationError(ConfigError):
    """配置验证错误"""

    def __init__(self, field: str, value: Any, reason: str):
        self.field = field
        self.value = value
        self.reason = reason
        message = f"Configuration validation failed for '{field}': {reason}"
        super().__init__(
            message=message,
            error_code="CONFIG_VALIDATION_ERROR",
            details={"field": field, "value": str(value), "reason": reason},
        )


class ConfigFileError(ConfigError):
    """配置文件错误"""

    def __init__(self, file_path: str, operation: str, reason: str):
        self.file_path = file_path
        self.operation = operation
        self.reason = reason
        message = f"Configuration file {operation} failed for '{file_path}': {reason}"
        super().__init__(
            message=message,
            error_code="CONFIG_FILE_ERROR",
            details={"file_path": file_path, "operation": operation, "reason": reason},
        )


class DependencyError(ConfigError):
    """依赖错误"""

    def __init__(self, dependency: str, reason: str, solution: str = None):
        self.dependency = dependency
        self.reason = reason
        self.solution = solution
        message = f"Dependency '{dependency}' error: {reason}"
        if solution:
            message += f" Solution: {solution}"
        super().__init__(
            message=message,
            error_code="DEPENDENCY_ERROR",
            details={"dependency": dependency, "reason": reason, "solution": solution},
        )


class StandardLogger:
    """标准化日志记录器"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.module_name = name

    def _format_message(self, message: str, **kwargs) -> str:
        """格式化日志消息"""
        if kwargs:
            context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
            return f"{message} | {context}"
        return message

    def debug(self, message: str, **kwargs):
        """调试日志"""
        self.logger.debug(self._format_message(message, **kwargs))

    def info(self, message: str, **kwargs):
        """信息日志"""
        self.logger.info(self._format_message(message, **kwargs))

    def warning(self, message: str, **kwargs):
        """警告日志"""
        self.logger.warning(self._format_message(message, **kwargs))

    def error(self, message: str, **kwargs):
        """错误日志"""
        self.logger.error(self._format_message(message, **kwargs))

    def critical(self, message: str, **kwargs):
        """严重错误日志"""
        self.logger.critical(self._format_message(message, **kwargs))

    def exception(self, message: str, **kwargs):
        """异常日志（包含堆栈信息）"""
        self.logger.exception(self._format_message(message, **kwargs))

    def log_config_change(
        self, operation: str, target: str, old_value: Any = None, new_value: Any = None
    ):
        """记录配置变更"""
        details = {"operation": operation, "target": target}
        if old_value is not None:
            details["old_value"] = str(old_value)
        if new_value is not None:
            details["new_value"] = str(new_value)

        self.info(f"Configuration {operation}: {target}", **details)

    def log_dependency_status(self, dependency: str, status: str, details: str = None):
        """记录依赖状态"""
        kwargs = {"dependency": dependency, "status": status}
        if details:
            kwargs["details"] = details

        level = self.info if status == "ok" else self.warning
        level(f"Dependency status: {dependency} = {status}", **kwargs)

    def log_error_with_solution(self, error: ConfigError):
        """记录错误及解决方案"""
        self.error(
            error.message,
            error_code=error.error_code,
            timestamp=error.timestamp.isoformat(),
            **error.details,
        )


def get_logger(name: str) -> StandardLogger:
    """获取标准化日志记录器"""
    return StandardLogger(name)


def safe_operation(
    operation_name: str,
    operation_func,
    logger: StandardLogger,
    error_type: Type[ConfigError] = ConfigError,
    default_return: Any = None,
    reraise: bool = False,
):
    """安全执行操作，统一错误处理"""
    try:
        logger.debug(f"Starting operation: {operation_name}")
        result = operation_func()
        logger.debug(f"Operation completed: {operation_name}")
        return result
    except Exception as e:
        error_msg = f"Operation failed: {operation_name} - {str(e)}"

        if isinstance(e, ConfigError):
            logger.log_error_with_solution(e)
        else:
            logger.exception(error_msg)

        if reraise:
            if isinstance(e, ConfigError):
                raise
            else:
                raise error_type(error_msg) from e

        return default_return


def validate_required_field(
    field_name: str, value: Any, field_type: Type = None
) -> Any:
    """验证必需字段"""
    if value is None or value == "":
        raise ConfigValidationError(
            field=field_name, value=value, reason="Field is required but not provided"
        )

    if field_type and not isinstance(value, field_type):
        raise ConfigValidationError(
            field=field_name,
            value=value,
            reason=f"Expected type {field_type.__name__}, got {type(value).__name__}",
        )

    return value


def validate_path_exists(field_name: str, path_value: str) -> str:
    """验证路径存在"""
    from pathlib import Path

    if not path_value:
        raise ConfigValidationError(
            field=field_name, value=path_value, reason="Path is empty"
        )

    path = Path(path_value)
    if not path.exists():
        raise ConfigValidationError(
            field=field_name, value=path_value, reason=f"Path does not exist: {path}"
        )

    return path_value


def validate_port_range(field_name: str, port: int) -> int:
    """验证端口范围"""
    if not isinstance(port, int):
        raise ConfigValidationError(
            field=field_name, value=port, reason="Port must be an integer"
        )

    # 端口0表示IPC模式，不使用HTTP端口
    if port == 0:
        return port

    if not (1024 <= port <= 65535):
        raise ConfigValidationError(
            field=field_name,
            value=port,
            reason="Port must be between 1024 and 65535 (or 0 for IPC mode)",
        )

    return port


# 全局日志记录器实例
config_logger = get_logger("config")
dependency_logger = get_logger("dependency")
