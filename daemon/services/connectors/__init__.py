"""
连接器微服务架构
将原来735行的ConnectorManager拆分为4个单一职责的微服务：
- ConnectorRegistry: 连接器发现和注册
- ConnectorRuntime: 进程生命周期管理  
- ConnectorHealthChecker: 健康监控和重启管理
- ConnectorConfigManager: 配置管理和热重载
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .registry import ConnectorRegistry
from .runtime import ConnectorRuntime  
from .health import ConnectorHealthChecker
from .config import ConnectorConfigManager
from models.api_models import ConnectorStatus, ConnectorInfo

logger = logging.getLogger(__name__)


class ConnectorManager:
    """重构后的连接器管理器 - 微服务架构统一接口"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        
        # 初始化4个微服务
        self.config = ConnectorConfigManager(project_root)
        self.registry = ConnectorRegistry(project_root)
        self.runtime = ConnectorRuntime(
            development_mode=self.config.get_system_config("development_mode")
        )
        self.health = ConnectorHealthChecker(self.runtime)
        
        logger.info("ConnectorManager微服务架构初始化完成")
        
        # 启动健康监控
        asyncio.create_task(self._initialize_async_components())
    
    async def _initialize_async_components(self):
        """初始化异步组件"""
        await self.health.start_monitoring()
        
        # 自动启动配置的连接器
        auto_start_connectors = self.config.get_auto_start_connectors()
        for connector_id in auto_start_connectors:
            logger.info(f"自动启动连接器: {connector_id}")
            await self.start_connector(connector_id)
    
    # === 连接器生命周期管理 API ===
    
    async def start_connector(self, connector_id: str, config: dict = None) -> bool:
        """启动连接器"""
        connector_config = self.registry.get_connector_config(connector_id)
        if not connector_config:
            logger.error(f"未知连接器: {connector_id}")
            return False
        
        # 获取运行时配置
        runtime_config = self.config.get_connector_runtime_config(connector_id)
        if config:
            runtime_config.update(config)
        
        # 验证权限
        if not self.registry.validate_connector_permissions(connector_id):
            logger.error(f"连接器 {connector_id} 权限验证失败")
            return False
        
        # 执行启动前置检查
        if not await self._preflight_check(connector_id, connector_config):
            logger.error(f"连接器 {connector_id} 预检查失败")
            return False
        
        # 启动连接器
        success = await self.runtime.start_connector(connector_id, connector_config, runtime_config)
        if success:
            # 重置重启计数
            self.health.reset_restart_count(connector_id)
        
        return success
    
    async def stop_connector(self, connector_id: str) -> bool:
        """停止连接器"""
        return await self.runtime.stop_connector(connector_id)
    
    async def restart_connector(self, connector_id: str, config: dict = None) -> bool:
        """重启连接器"""
        connector_config = self.registry.get_connector_config(connector_id)
        if not connector_config:
            logger.error(f"未知连接器: {connector_id}")
            return False
        
        runtime_config = self.config.get_connector_runtime_config(connector_id)
        if config:
            runtime_config.update(config)
        
        return await self.runtime.restart_connector(connector_id, connector_config, runtime_config)
    
    async def _preflight_check(self, connector_id: str, connector_config: dict) -> bool:
        """连接器启动前置检查"""
        logger.info(f"🔍 执行连接器 {connector_id} 预检查...")
        
        try:
            # 检查入口文件是否存在
            entry = connector_config["entry"]
            runtime = connector_config["_runtime"]
            connector_dir = Path(runtime["connector_dir"])
            
            development_mode = self.config.get_system_config("development_mode")
            
            if development_mode:
                dev_entry = entry["development"]
                args = dev_entry["args"]
                main_file = connector_dir / args[0] if args else connector_dir / "main.py"
                
                if not main_file.exists():
                    logger.error(f"❌ 连接器入口文件不存在: {main_file}")
                    return False
                logger.info(f"✅ 入口文件检查通过: {main_file}")
            
            logger.info(f"🎉 连接器 {connector_id} 预检查全部通过")
            return True
            
        except Exception as e:
            logger.error(f"❌ 预检查过程中发生错误: {e}")
            return False
    
    # === 连接器状态查询 API ===
    
    def get_connector_status(self, connector_id: str) -> ConnectorStatus:
        """获取连接器状态"""
        if not self.registry.is_connector_available(connector_id):
            return ConnectorStatus.ERROR
        
        return self.health.get_connector_status(connector_id)
    
    def get_connector_info(self, connector_id: str) -> Optional[ConnectorInfo]:
        """获取连接器详细信息"""
        connector_config = self.registry.get_connector_config(connector_id)
        if not connector_config:
            return None
        
        status = self.get_connector_status(connector_id)
        
        # 获取进程信息
        data_count = 0
        if status == ConnectorStatus.RUNNING:
            data_count = 1  # TODO: 实现真实的数据计数
        
        return ConnectorInfo(
            id=connector_id,
            name=connector_config["name"],
            description=connector_config["description"],
            status=status,
            data_count=data_count,
            last_update=datetime.now(),
            config=connector_config.get("config_schema", {})
        )
    
    def list_available_connectors(self) -> List[dict]:
        """列出所有可用连接器"""
        connectors = self.registry.list_all_connectors()
        
        # 添加状态信息
        for connector in connectors:
            connector["status"] = self.get_connector_status(connector["id"]).value
        
        return connectors
    
    def list_running_connectors(self) -> List[ConnectorInfo]:
        """列出所有运行中的连接器"""
        running_ids = self.runtime.get_running_connectors()
        connectors = []
        
        for connector_id in running_ids:
            info = self.get_connector_info(connector_id)
            if info and info.status == ConnectorStatus.RUNNING:
                connectors.append(info)
        
        return connectors
    
    # === 连接器管理 API ===
    
    def reload_connectors(self):
        """重新加载连接器配置"""
        self.registry.reload_connectors()
        self.config.reload_configs()
    
    def validate_connector_permissions(self, connector_id: str) -> bool:
        """验证连接器权限"""
        return self.registry.validate_connector_permissions(connector_id)
    
    # === 健康管理 API ===
    
    def enable_auto_restart(self, connector_id: str, enabled: bool = True):
        """启用/禁用连接器自动重启"""
        self.health.enable_auto_restart(connector_id, enabled)
    
    def reset_restart_count(self, connector_id: str):
        """重置连接器重启计数"""
        self.health.reset_restart_count(connector_id)
    
    def get_restart_stats(self, connector_id: str) -> dict:
        """获取连接器重启统计信息"""
        return self.health.get_restart_stats(connector_id)
    
    # === 配置管理 API ===
    
    def get_connector_config(self, connector_id: str, key: str = None):
        """获取连接器配置"""
        runtime_config = self.config.get_connector_runtime_config(connector_id)
        
        if key is None:
            return runtime_config
        
        keys = key.split(".")
        value = runtime_config
        for k in keys:
            value = value.get(k)
            if value is None:
                return None
        return value
    
    def set_connector_config(self, connector_id: str, key: str, value, save: bool = True) -> bool:
        """设置连接器配置"""
        config_key = f"connector_settings.{connector_id}.{key}"
        return self.config.set_user_config(config_key, value, save)
    
    # === 系统管理 API ===
    
    async def shutdown_all(self):
        """关闭所有连接器和服务"""
        logger.info("关闭连接器管理系统")
        
        # 停止健康监控
        await self.health.stop_monitoring()
        
        # 关闭所有连接器
        await self.runtime.shutdown_all()
        
        logger.info("连接器管理系统已关闭")
    
    def get_system_stats(self) -> dict:
        """获取系统统计信息"""
        return {
            "total_connectors": self.registry.get_connector_count(),
            "running_connectors": len(self.runtime.get_running_connectors()),
            "health_stats": self.health.get_health_stats(),
            "development_mode": self.config.get_system_config("development_mode"),
            "auto_start_connectors": self.config.get_auto_start_connectors()
        }


# 向后兼容性别名
ConnectorLifecycleManager = ConnectorManager

__all__ = [
    "ConnectorManager",
    "ConnectorLifecycleManager",
    "ConnectorRegistry", 
    "ConnectorRuntime",
    "ConnectorHealthChecker",
    "ConnectorConfigManager"
]