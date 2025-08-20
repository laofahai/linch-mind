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
# 移除已删除的unified_server导入

__all__ = [
    # 策略相关
    "IPCStrategy",
    "IPCStrategyFactory",
    "UnixSocketStrategy",
    "WindowsNamedPipeStrategy",
]

# 版本信息
__version__ = "1.0.0"
__author__ = "Linch Mind Team"
__description__ = "Unified cross-platform IPC solution"
