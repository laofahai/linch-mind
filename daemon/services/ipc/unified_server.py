#!/usr/bin/env python3
"""
统一IPC服务器 - 使用策略模式实现跨平台支持
消除重复代码，提供一致的API接口
"""

import asyncio
import logging
import platform
from typing import Any, Dict, Optional

from .strategy import IPCStrategy, IPCStrategyFactory

logger = logging.getLogger(__name__)


class UnifiedIPCServer:
    """统一的IPC服务器实现
    
    使用策略模式处理平台差异，提供一致的API接口
    消除Unix Socket和Windows Named Pipe的重复实现
    """

    def __init__(
        self,
        socket_path: Optional[str] = None,
        pipe_name: Optional[str] = None,
        auto_detect_platform: bool = True
    ):
        """初始化统一IPC服务器
        
        Args:
            socket_path: Unix socket路径（Unix平台使用）
            pipe_name: Named pipe名称（Windows平台使用）
            auto_detect_platform: 是否自动检测平台
        """
        self.socket_path = socket_path
        self.pipe_name = pipe_name
        self.auto_detect_platform = auto_detect_platform
        
        # 根据平台创建策略
        self._strategy = self._create_strategy()
        
        # IPC应用和安全管理器
        self.app = None
        self.security_manager = None
        
        # 服务器状态
        self._is_initialized = False
        
        logger.info(f"统一IPC服务器初始化完成 - 策略: {type(self._strategy).__name__}")

    def _create_strategy(self) -> IPCStrategy:
        """根据配置创建相应的IPC策略"""
        if self.auto_detect_platform:
            # 自动检测平台
            return IPCStrategyFactory.create_strategy(
                socket_path=self.socket_path,
                pipe_name=self.pipe_name
            )
        else:
            # 手动指定平台
            current_platform = platform.system()
            return IPCStrategyFactory.create_strategy(
                platform=current_platform,
                socket_path=self.socket_path,
                pipe_name=self.pipe_name
            )

    def set_ipc_app(self, app):
        """设置IPC应用实例"""
        self.app = app
        logger.info("IPC应用实例已设置")

    def set_security_manager(self, security_manager):
        """设置安全管理器"""
        self.security_manager = security_manager
        logger.info("IPC安全管理器已设置")

    async def start(self) -> None:
        """启动IPC服务器"""
        if not self.app:
            raise RuntimeError("IPC应用未设置，请先调用set_ipc_app()")
        
        if not self.security_manager:
            logger.warning("安全管理器未设置，将使用默认安全配置")
        
        logger.info("启动统一IPC服务器...")
        
        try:
            # 使用策略启动服务器
            await self._strategy.start(
                app=self.app,
                security_manager=self.security_manager
            )
            
            self._is_initialized = True
            logger.info("✅ 统一IPC服务器启动成功")
            
            # 记录连接信息
            conn_info = self.get_connection_info()
            logger.info(f"连接信息: {conn_info}")
            
        except Exception as e:
            logger.error(f"统一IPC服务器启动失败: {e}")
            raise

    async def stop(self) -> None:
        """停止IPC服务器"""
        if not self._is_initialized:
            logger.warning("IPC服务器未启动，无需停止")
            return
        
        logger.info("停止统一IPC服务器...")
        
        try:
            await self._strategy.stop()
            self._is_initialized = False
            logger.info("✅ 统一IPC服务器已停止")
            
        except Exception as e:
            logger.error(f"停止IPC服务器时出错: {e}")
            raise

    def get_connection_info(self) -> Dict[str, Any]:
        """获取连接信息"""
        base_info = {
            "server_type": "unified_ipc",
            "platform": platform.system(),
            "strategy": type(self._strategy).__name__,
            "is_running": self.is_running()
        }
        
        # 合并策略特定的连接信息
        strategy_info = self._strategy.get_connection_info()
        return {**base_info, **strategy_info}

    def get_server_status(self) -> Dict[str, Any]:
        """获取详细的服务器状态信息"""
        base_status = {
            "is_initialized": self._is_initialized,
            "is_running": self.is_running(),
            "app_configured": self.app is not None,
            "security_configured": self.security_manager is not None,
            "platform": platform.system(),
            "strategy_type": type(self._strategy).__name__
        }
        
        # 合并策略特定的统计信息
        strategy_stats = self._strategy.get_stats()
        return {**base_status, **strategy_stats}

    def is_running(self) -> bool:
        """检查服务器是否运行中"""
        return self._is_initialized and self._strategy.is_running()

    async def restart(self) -> None:
        """重启IPC服务器"""
        logger.info("重启统一IPC服务器...")
        
        if self.is_running():
            await self.stop()
        
        # 重新创建策略以确保清理状态
        self._strategy = self._create_strategy()
        
        await self.start()
        logger.info("✅ 统一IPC服务器重启完成")

    def switch_strategy(self, new_strategy: IPCStrategy) -> None:
        """切换IPC策略（仅在停止状态下）"""
        if self.is_running():
            raise RuntimeError("无法在运行时切换策略，请先停止服务器")
        
        old_strategy_name = type(self._strategy).__name__
        self._strategy = new_strategy
        new_strategy_name = type(self._strategy).__name__
        
        logger.info(f"IPC策略已切换: {old_strategy_name} -> {new_strategy_name}")

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            status = self.get_server_status()
            
            # 基本健康检查
            is_healthy = (
                status["is_initialized"] and 
                status["is_running"] and
                status["app_configured"]
            )
            
            return {
                "healthy": is_healthy,
                "timestamp": asyncio.get_event_loop().time(),
                "status": status,
                "checks": {
                    "initialized": status["is_initialized"],
                    "running": status["is_running"],
                    "app_configured": status["app_configured"],
                    "security_configured": status["security_configured"]
                }
            }
            
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }

    async def __aenter__(self):
        """异步上下文管理器 - 进入"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器 - 退出"""
        await self.stop()


# 便捷函数
def create_unified_ipc_server(**kwargs) -> UnifiedIPCServer:
    """创建统一IPC服务器的便捷函数
    
    支持的参数:
    - socket_path: Unix socket路径
    - pipe_name: Windows pipe名称  
    - auto_detect_platform: 是否自动检测平台
    """
    return UnifiedIPCServer(**kwargs)


async def test_unified_server():
    """测试统一IPC服务器"""
    logger.info("开始测试统一IPC服务器")
    
    try:
        # 创建服务器实例
        server = create_unified_ipc_server()
        
        # 模拟设置应用（实际使用中会是真实的IPC应用）
        class MockApp:
            async def handle_request(self, method, path, data, query_params, headers, request_id=None):
                return {"success": True, "message": "Mock response"}
        
        server.set_ipc_app(MockApp())
        
        # 获取连接信息
        conn_info = server.get_connection_info()
        logger.info(f"连接配置: {conn_info}")
        
        # 健康检查
        health = await server.health_check()
        logger.info(f"启动前健康检查: {health}")
        
        logger.info("统一IPC服务器测试完成")
        return True
        
    except Exception as e:
        logger.error(f"统一IPC服务器测试失败: {e}")
        return False


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    result = asyncio.run(test_unified_server())
    exit(0 if result else 1)