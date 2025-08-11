#!/usr/bin/env python3
"""
IPC服务器策略模式接口定义
用于统一Unix Socket和Windows Named Pipe实现
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class IPCStrategy(ABC):
    """IPC策略接口 - 定义平台无关的服务器行为"""

    @abstractmethod
    async def start(self, app, security_manager, **kwargs) -> None:
        """启动IPC服务器"""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """停止IPC服务器"""
        pass

    @abstractmethod
    def get_connection_info(self) -> Dict[str, Any]:
        """获取连接信息"""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """获取服务器统计信息"""
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """检查服务器是否运行中"""
        pass


class UnixSocketStrategy(IPCStrategy):
    """Unix Domain Socket策略实现"""

    def __init__(self, socket_path: Optional[str] = None):
        self.socket_path = socket_path
        self._server = None
        self._is_running = False
        self.app = None
        self.security_manager = None
        self.clients = set()
        self.client_connections = {}

    async def start(self, app, security_manager, **kwargs) -> None:
        """启动Unix Socket服务器"""
        from ..ipc_server import IPCServer

        logger.info("使用Unix Socket策略启动IPC服务器")

        # 复用现有IPCServer实现，但移除全局单例
        self._server = IPCServer(socket_path=self.socket_path)
        self._server.app = app
        self._server.security_manager = security_manager

        await self._server.start()
        self._is_running = True

        logger.info(f"Unix Socket IPC服务器已启动: {self._server.socket_path}")

    async def stop(self) -> None:
        """停止Unix Socket服务器"""
        if self._server:
            await self._server.stop()
            self._server = None
        self._is_running = False
        logger.info("Unix Socket IPC服务器已停止")

    def get_connection_info(self) -> Dict[str, Any]:
        """获取Unix Socket连接信息"""
        return {
            "type": "unix_socket",
            "socket_path": self.socket_path
            or (self._server.socket_path if self._server else None),
            "platform": "unix",
        }

    def get_stats(self) -> Dict[str, Any]:
        """获取Unix Socket统计信息"""
        if self._server:
            return self._server.get_server_status()
        return {"is_running": self._is_running}

    def is_running(self) -> bool:
        """检查Unix Socket服务器是否运行中"""
        return self._is_running and (self._server.is_running if self._server else False)


class WindowsNamedPipeStrategy(IPCStrategy):
    """Windows Named Pipe策略实现"""

    def __init__(self, pipe_name: Optional[str] = None):
        self.pipe_name = pipe_name
        self._server = None
        self._is_running = False

    async def start(self, app, security_manager, **kwargs) -> None:
        """启动Named Pipe服务器"""
        try:
            from ..windows_ipc_server import WindowsIPCServer

            logger.info("使用Windows Named Pipe策略启动IPC服务器")

            self._server = WindowsIPCServer(pipe_name=self.pipe_name)
            self._server.set_ipc_app(app)
            self._server.set_security_manager(security_manager)

            await self._server.start()
            self._is_running = True

            logger.info(
                f"Windows Named Pipe IPC服务器已启动: {self._server.full_pipe_name}"
            )

        except ImportError as e:
            logger.error(f"Windows Named Pipe不可用: {e}")
            raise RuntimeError("Windows平台IPC服务器初始化失败，请安装pywin32")

    async def stop(self) -> None:
        """停止Named Pipe服务器"""
        if self._server:
            await self._server.stop()
            self._server = None
        self._is_running = False
        logger.info("Windows Named Pipe IPC服务器已停止")

    def get_connection_info(self) -> Dict[str, Any]:
        """获取Named Pipe连接信息"""
        pipe_name = self.pipe_name or (self._server.pipe_name if self._server else None)
        return {
            "type": "named_pipe",
            "pipe_name": pipe_name,
            "full_path": f"\\\\.\\pipe\\{pipe_name}" if pipe_name else None,
            "platform": "windows",
        }

    def get_stats(self) -> Dict[str, Any]:
        """获取Named Pipe统计信息"""
        if self._server:
            return self._server.get_stats()
        return {"is_running": self._is_running}

    def is_running(self) -> bool:
        """检查Named Pipe服务器是否运行中"""
        return self._is_running


class IPCStrategyFactory:
    """IPC策略工厂"""

    @staticmethod
    def create_strategy(platform: str = None, **kwargs) -> IPCStrategy:
        """根据平台创建相应的IPC策略"""
        import platform as platform_module

        if platform is None:
            platform = platform_module.system()

        if platform == "Windows":
            return WindowsNamedPipeStrategy(kwargs.get("pipe_name"))
        else:
            return UnixSocketStrategy(kwargs.get("socket_path"))

    @staticmethod
    def get_default_config(platform: str = None) -> Dict[str, Any]:
        """获取平台的默认配置"""
        import platform as platform_module

        if platform is None:
            platform = platform_module.system()

        if platform == "Windows":
            return {
                "type": "named_pipe",
                "pipe_name": "linch-mind-ipc",
                "platform": "windows",
            }
        else:
            return {
                "type": "unix_socket",
                "socket_path": "/tmp/linch-mind-ipc.sock",
                "platform": "unix",
            }
