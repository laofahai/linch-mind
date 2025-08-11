#!/usr/bin/env python3
"""
IPC服务模块 - 统一的进程间通信解决方案

提供跨平台的IPC服务器和客户端实现:
- Unix Domain Socket (Linux/macOS)
- Windows Named Pipe (Windows)

主要组件:
- UnifiedIPCServer: 统一的IPC服务器
- IPCStrategy: 策略模式接口
- IPCStrategyFactory: 策略工厂
"""

from .strategy import (
    IPCStrategy,
    IPCStrategyFactory,
    UnixSocketStrategy,
    WindowsNamedPipeStrategy,
)
from .unified_server import UnifiedIPCServer, create_unified_ipc_server

__all__ = [
    # 核心类
    "UnifiedIPCServer",
    # 策略相关
    "IPCStrategy",
    "IPCStrategyFactory",
    "UnixSocketStrategy",
    "WindowsNamedPipeStrategy",
    # 便捷函数
    "create_unified_ipc_server",
]

# 版本信息
__version__ = "1.0.0"
__author__ = "Linch Mind Team"
__description__ = "Unified cross-platform IPC solution"
