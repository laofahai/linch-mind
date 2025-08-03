#!/usr/bin/env python3
"""
连接器基础类 - 仅抽取公共方法
"""

import asyncio
import logging
import httpx
import time
import signal
import os
import importlib
import subprocess
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from .config import get_daemon_url


class BaseConnector(ABC):
    """连接器基类 - 仅抽取公共方法"""
    
    def __init__(self, connector_id: str, daemon_url: str = None):
        self.connector_id = connector_id
        self.daemon_url = daemon_url or get_daemon_url()
        self.should_stop = False
        self.logger = self._setup_logger()
        self.config = self._load_config()
        
        self.logger.info(f"{connector_id}连接器初始化完成")
        self.logger.info(f"Daemon URL: {self.daemon_url}")
    
    def _load_config(self) -> Dict[str, Any]:
        """初始化默认配置，实际配置从daemon获取"""
        return {}
    
    async def load_config_from_daemon(self) -> Dict[str, Any]:
        """从daemon加载连接器配置"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.daemon_url}/api/v1/connectors/{self.connector_id}/config")
                if response.status_code == 200:
                    config = response.json()
                    old_config = self.config.copy()
                    self.config.update(config)
                    self.logger.info(f"已从daemon加载配置: {len(config)}项")
                    
                    # 检查配置是否有变化
                    if old_config != self.config:
                        await self._handle_config_change(old_config, self.config)
                    
                    return config
                else:
                    self.logger.warning(f"获取配置失败: {response.status_code}")
                    return {}
        except Exception as e:
            self.logger.error(f"从daemon加载配置失败: {e}")
            return {}
    
    async def _handle_config_change(self, old_config: Dict[str, Any], new_config: Dict[str, Any]):
        """处理配置变更 - 子类可覆盖"""
        self.logger.info("配置已更新，需要重新加载连接器")
        # 默认实现：标记需要重启
        # 子类可以覆盖此方法实现热重载
        pass
    
    async def start_config_monitoring(self, check_interval: float = 30.0):
        """启动配置监控 - 定期检查配置变更"""
        while not self.should_stop:
            try:
                await self.load_config_from_daemon()
                await asyncio.sleep(check_interval)
            except Exception as e:
                self.logger.error(f"配置监控错误: {e}")
                await asyncio.sleep(check_interval)
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.config.get(key, default)
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志器"""
        logger = logging.getLogger(f'{self.connector_id}-connector')
        
        # 只在没有配置时设置基本配置
        if not logging.getLogger().handlers:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        return logger
    
    def create_data_item(self, content: str, metadata: Dict[str, Any], file_path: Optional[str] = None) -> Dict[str, Any]:
        """创建数据项 - 统一格式"""
        return {
            "id": f"{self.connector_id}_{int(time.time() * 1000)}_{hash(content) % 10000}",
            "content": content,
            "source_connector": self.connector_id,
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "metadata": metadata
        }
    
    async def push_to_daemon(self, data_item: Dict[str, Any]) -> bool:
        """推送数据到Daemon"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.daemon_url}/api/v1/data/ingest",
                    json=data_item,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("success", False)
                else:
                    self.logger.error(f"HTTP错误: {response.status_code} - {response.text}")
                    return False
                    
        except httpx.ConnectError:
            self.logger.error("无法连接到Daemon，请确保Daemon正在运行")
            return False
        except Exception as e:
            self.logger.error(f"推送数据到Daemon失败: {e}")
            return False
    
    async def test_daemon_connection(self) -> bool:
        """测试Daemon连接"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.daemon_url}/")
                if response.status_code == 200:
                    self.logger.info("✅ Daemon连接正常")
                    return True
                else:
                    self.logger.warning(f"⚠️ Daemon响应异常: {response.status_code}")
                    return False
        except Exception as e:
            self.logger.error(f"❌ 无法连接到Daemon: {e}")
            return False
    
    def stop(self):
        """停止连接器"""
        self.logger.info(f"停止{self.connector_id}连接器...")
        self.should_stop = True
    
    @classmethod
    def get_required_dependencies(cls) -> List[str]:
        """返回连接器必需的Python包依赖列表 - 子类可覆盖"""
        return []
    
    @classmethod
    def check_dependencies(cls) -> Dict[str, Any]:
        """检查连接器依赖是否满足"""
        dependencies = cls.get_required_dependencies()
        if not dependencies:
            return {"status": "ok", "message": "无需额外依赖"}
        
        missing_deps = []
        available_deps = []
        
        for dep in dependencies:
            try:
                importlib.import_module(dep)
                available_deps.append(dep)
            except ImportError:
                missing_deps.append(dep)
        
        if missing_deps:
            return {
                "status": "error",
                "message": f"缺少必需依赖: {', '.join(missing_deps)}",
                "missing_dependencies": missing_deps,
                "available_dependencies": available_deps,
                "install_command": f"pip install {' '.join(missing_deps)}"
            }
        else:
            return {
                "status": "ok", 
                "message": "所有依赖已满足",
                "available_dependencies": available_deps
            }
    
    @classmethod
    @abstractmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """返回连接器的配置schema - 子类必须实现"""
        pass
    
    @classmethod
    def get_config_ui_schema(cls) -> Dict[str, Any]:
        """返回UI渲染提示 - 可选覆盖"""
        return {}
    
    async def register_config_schema(self):
        """向daemon注册配置schema"""
        try:
            schema = self.get_config_schema()
            ui_schema = self.get_config_ui_schema()
            
            payload = {
                "connector_id": self.connector_id,
                "config_schema": schema,
                "ui_schema": ui_schema,
                "connector_name": self.__class__.__name__,
                "connector_description": self.__class__.__doc__ or ""
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.daemon_url}/api/v1/connectors/{self.connector_id}/schema",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    self.logger.info("✅ 配置schema注册成功")
                    return True
                else:
                    self.logger.error(f"❌ 配置schema注册失败: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"❌ 注册配置schema时发生错误: {e}")
            return False
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置是否符合schema"""
        try:
            schema = self.get_config_schema()
            # 这里可以使用jsonschema库进行验证
            # 目前简化实现，检查必需字段
            required_fields = schema.get("required", [])
            for field in required_fields:
                if field not in config:
                    self.logger.error(f"配置验证失败: 缺少必需字段 {field}")
                    return False
            return True
        except Exception as e:
            self.logger.error(f"配置验证错误: {e}")
            return False
    
    @abstractmethod
    async def start_monitoring(self):
        """启动监控 - 子类必须实现"""
        pass


def setup_signal_handlers(connector: BaseConnector):
    """设置信号处理器 - 通用实现"""
    def signal_handler(signum, frame):
        connector.logger.info(f"收到信号 {signum}")
        connector.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def run_connector(connector: BaseConnector):
    """运行连接器 - 通用主循环"""
    connector.logger.info(f"🚀 启动Linch Mind {connector.connector_id}连接器")
    
    setup_signal_handlers(connector)
    
    try:
        # 启动时自动注册配置schema
        connector.logger.info("🔧 注册配置schema...")
        await connector.register_config_schema()
        
        await connector.start_monitoring()
    except KeyboardInterrupt:
        connector.logger.info("进程被中断")
    except Exception as e:
        connector.logger.error(f"连接器运行错误: {e}")
        raise
    finally:
        connector.logger.info(f"{connector.connector_id}连接器已退出")