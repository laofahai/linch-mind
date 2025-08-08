#!/usr/bin/env python3
"""
统一日志配置系统
提供结构化JSON日志、多级别日志、文件轮转等功能
"""

import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class StructuredFormatter(logging.Formatter):
    """结构化JSON日志格式化器"""

    def __init__(self):
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为JSON"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加异常信息
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # 添加额外的上下文信息
        if hasattr(record, "extra_data"):
            log_entry["data"] = record.extra_data

        # 添加IPC相关信息
        if hasattr(record, "ipc_context"):
            log_entry["ipc"] = record.ipc_context

        # 添加连接器相关信息
        if hasattr(record, "connector_id"):
            log_entry["connector_id"] = record.connector_id

        # 添加性能信息
        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = record.duration_ms

        return json.dumps(log_entry, ensure_ascii=False)


class ColoredConsoleFormatter(logging.Formatter):
    """彩色控制台日志格式化器"""

    # ANSI颜色代码
    COLORS = {
        "DEBUG": "\033[36m",  # 青色
        "INFO": "\033[32m",  # 绿色
        "WARNING": "\033[33m",  # 黄色
        "ERROR": "\033[31m",  # 红色
        "CRITICAL": "\033[35m",  # 紫色
    }
    RESET = "\033[0m"

    def __init__(self):
        super().__init__(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def format(self, record: logging.LogRecord) -> str:
        """格式化带颜色的日志输出"""
        # 获取基础格式化文本
        log_text = super().format(record)

        # 添加颜色
        color = self.COLORS.get(record.levelname, "")
        if color:
            log_text = f"{color}{log_text}{self.RESET}"

        return log_text


class LoggingConfig:
    """统一日志配置管理"""

    def __init__(self, app_name: str = "linch-mind", log_dir: Optional[Path] = None):
        self.app_name = app_name
        self.log_dir = log_dir or Path.home() / ".linch-mind" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 日志文件路径
        self.main_log_file = self.log_dir / f"{app_name}.log"
        self.error_log_file = self.log_dir / f"{app_name}_errors.log"
        self.performance_log_file = self.log_dir / f"{app_name}_performance.log"

    def setup_logging(
        self,
        level: str = "INFO",
        console_output: bool = True,
        json_format: bool = False,
        file_rotation: bool = True,
    ) -> None:
        """设置统一日志配置"""

        # 转换日志级别
        log_level = getattr(logging, level.upper(), logging.INFO)

        # 获取根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # 清除现有处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # 1. 控制台处理器
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            if json_format:
                console_handler.setFormatter(StructuredFormatter())
            else:
                console_handler.setFormatter(ColoredConsoleFormatter())
            console_handler.setLevel(log_level)
            root_logger.addHandler(console_handler)

        # 2. 主日志文件处理器
        if file_rotation:
            file_handler = logging.handlers.RotatingFileHandler(
                self.main_log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding="utf-8",
            )
        else:
            file_handler = logging.FileHandler(self.main_log_file, encoding="utf-8")

        file_handler.setFormatter(StructuredFormatter())
        file_handler.setLevel(logging.DEBUG)  # 文件记录所有级别
        root_logger.addHandler(file_handler)

        # 3. 错误日志文件处理器
        error_handler = logging.FileHandler(self.error_log_file, encoding="utf-8")
        error_handler.setFormatter(StructuredFormatter())
        error_handler.setLevel(logging.ERROR)  # 只记录错误和严重错误
        root_logger.addHandler(error_handler)

        # 4. 性能日志处理器
        perf_handler = logging.FileHandler(self.performance_log_file, encoding="utf-8")
        perf_handler.setFormatter(StructuredFormatter())
        perf_handler.addFilter(self._performance_filter)
        root_logger.addHandler(perf_handler)

        # 设置第三方库日志级别
        self._configure_third_party_loggers()

    def _performance_filter(self, record: logging.LogRecord) -> bool:
        """性能日志过滤器"""
        return hasattr(record, "duration_ms") or "performance" in record.name.lower()

    def _configure_third_party_loggers(self):
        """配置第三方库日志级别"""
        third_party_loggers = {
            "urllib3": logging.WARNING,
            "requests": logging.WARNING,
            "sqlalchemy": logging.WARNING,
            "faiss": logging.WARNING,
            "sentence_transformers": logging.WARNING,
            "transformers": logging.WARNING,
        }

        for logger_name, level in third_party_loggers.items():
            logging.getLogger(logger_name).setLevel(level)

    def get_logger(self, name: str) -> logging.Logger:
        """获取命名日志记录器"""
        return logging.getLogger(name)

    def get_ipc_logger(self) -> logging.Logger:
        """获取IPC专用日志记录器"""
        logger = logging.getLogger("linch_mind.ipc")
        return logger

    def get_connector_logger(self, connector_id: str) -> logging.Logger:
        """获取连接器专用日志记录器"""
        logger = logging.getLogger(f"linch_mind.connector.{connector_id}")
        return logger

    def get_performance_logger(self) -> logging.Logger:
        """获取性能专用日志记录器"""
        logger = logging.getLogger("linch_mind.performance")
        return logger


class LogContext:
    """日志上下文管理器"""

    def __init__(self, logger: logging.Logger, **context):
        self.logger = logger
        self.context = context

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.error(f"Exception in context: {exc_val}", exc_info=True)

    def _log_with_context(self, level: int, message: str, **kwargs):
        """带上下文的日志记录"""
        record = self.logger.makeRecord(
            self.logger.name, level, "", 0, message, (), None
        )
        record.extra_data = {**self.context, **kwargs}
        self.logger.handle(record)

    def debug(self, message: str, **kwargs):
        self._log_with_context(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        self._log_with_context(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log_with_context(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log_with_context(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        self._log_with_context(logging.CRITICAL, message, **kwargs)


class PerformanceLogger:
    """性能日志记录器"""

    def __init__(self, logger: logging.Logger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None

    def __enter__(self):
        import time

        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            import time

            duration_ms = (time.time() - self.start_time) * 1000

            record = self.logger.makeRecord(
                self.logger.name,
                logging.INFO,
                "",
                0,
                f"Performance: {self.operation}",
                (),
                None,
            )
            record.duration_ms = duration_ms
            record.operation = self.operation

            if exc_type:
                record.success = False
                record.error = str(exc_val)
            else:
                record.success = True

            self.logger.handle(record)


# 全局日志配置实例
_logging_config = None


def get_logging_config() -> LoggingConfig:
    """获取全局日志配置实例"""
    global _logging_config
    if _logging_config is None:
        _logging_config = LoggingConfig()
    return _logging_config


def setup_global_logging(
    level: str = "INFO", console: bool = True, json_format: bool = False
):
    """设置全局日志配置"""
    config = get_logging_config()
    config.setup_logging(level=level, console_output=console, json_format=json_format)


def get_logger(name: str) -> logging.Logger:
    """便捷函数：获取命名日志记录器"""
    return get_logging_config().get_logger(name)


def log_performance(operation: str, logger: Optional[logging.Logger] = None):
    """便捷函数：创建性能日志上下文管理器"""
    if logger is None:
        logger = get_logging_config().get_performance_logger()
    return PerformanceLogger(logger, operation)


def log_context(logger: logging.Logger, **context):
    """便捷函数：创建日志上下文管理器"""
    return LogContext(logger, **context)
