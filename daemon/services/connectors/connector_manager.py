#!/usr/bin/env python3
"""
简化的连接器管理器 - Session V65 架构简化
移除实例概念，daemon只负责连接器启动停止，内部逻辑由连接器自管理
"""

import asyncio
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectorState(Enum):
    """简化的连接器状态"""
    STOPPED = "stopped"
    RUNNING = "running"
    ERROR = "error"


class ConnectorInfo:
    """连接器基本信息"""
    def __init__(self, 
                 connector_id: str,
                 name: str,
                 description: str,
                 path: Path,
                 entry_point: str = "main.py"):
        self.connector_id = connector_id
        self.name = name
        self.description = description
        self.path = path
        self.entry_point = entry_point
        self.state = ConnectorState.STOPPED
        self.process: Optional[subprocess.Popen] = None
        self.pid: Optional[int] = None
        self.started_at: Optional[datetime] = None
        self.error_message: Optional[str] = None


class ConnectorManager:
    """简化的连接器管理器
    
    核心职责：
    1. 手动注册连接器 - 不再自动发现
    2. 启动连接器 - 作为独立进程启动
    3. 停止连接器 - 安全停止进程
    4. 监控状态 - 基本的进程状态检查
    
    不再管理：
    - 自动连接器发现
    - 复杂的实例概念
    - 详细的状态同步
    - 配置热重载
    - 生命周期复杂状态转换
    """
    
    def __init__(self, connectors_dir: Path):
        self.connectors_dir = Path(connectors_dir)
        self.connectors: Dict[str, ConnectorInfo] = {}
        
        logger.info(f"连接器管理器初始化完成")
    
    def register_connector(self, connector_id: str, name: str, description: str, path: Path):
        """手动注册连接器（替代自动发现）"""
        try:
            connector_info = ConnectorInfo(
                connector_id=connector_id,
                name=name,
                description=description,
                path=path
            )
            
            self.connectors[connector_id] = connector_info
            logger.info(f"注册连接器: {connector_id} - {name}")
            
        except Exception as e:
            logger.error(f"注册连接器失败 {connector_id}: {e}")
    
    async def start_connector(self, connector_id: str) -> bool:
        """启动连接器"""
        if connector_id not in self.connectors:
            logger.error(f"连接器不存在: {connector_id}")
            return False
        
        connector = self.connectors[connector_id]
        
        if connector.state == ConnectorState.RUNNING:
            logger.warning(f"连接器已在运行: {connector_id}")
            return True
        
        try:
            # 构建启动命令
            entry_script = connector.path / connector.entry_point
            if not entry_script.exists():
                logger.error(f"连接器入口脚本不存在: {entry_script}")
                return False
            
            # 启动进程
            process = subprocess.Popen(
                ["python", str(entry_script)],
                cwd=str(connector.path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 更新连接器状态
            connector.process = process
            connector.pid = process.pid
            connector.state = ConnectorState.RUNNING
            connector.started_at = datetime.now()
            connector.error_message = None
            
            logger.info(f"连接器启动成功: {connector_id} (PID: {process.pid})")
            return True
            
        except Exception as e:
            connector.state = ConnectorState.ERROR
            connector.error_message = str(e)
            logger.error(f"启动连接器失败 {connector_id}: {e}")
            return False
    
    async def stop_connector(self, connector_id: str) -> bool:
        """停止连接器"""
        if connector_id not in self.connectors:
            logger.error(f"连接器不存在: {connector_id}")
            return False
        
        connector = self.connectors[connector_id]
        
        if connector.state != ConnectorState.RUNNING or not connector.process:
            logger.warning(f"连接器未运行: {connector_id}")
            connector.state = ConnectorState.STOPPED
            return True
        
        try:
            # 尝试优雅停止
            connector.process.terminate()
            
            # 等待进程结束
            try:
                connector.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # 强制停止
                logger.warning(f"连接器 {connector_id} 未响应终止信号，强制停止")
                connector.process.kill()
                connector.process.wait()
            
            # 更新状态
            connector.state = ConnectorState.STOPPED
            connector.process = None
            connector.pid = None
            connector.error_message = None
            
            logger.info(f"连接器停止成功: {connector_id}")
            return True
            
        except Exception as e:
            connector.state = ConnectorState.ERROR
            connector.error_message = str(e)
            logger.error(f"停止连接器失败 {connector_id}: {e}")
            return False
    
    async def restart_connector(self, connector_id: str) -> bool:
        """重启连接器"""
        logger.info(f"重启连接器: {connector_id}")
        
        # 先停止
        await self.stop_connector(connector_id)
        
        # 等待一秒
        await asyncio.sleep(1)
        
        # 再启动
        return await self.start_connector(connector_id)
    
    def get_connector_status(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取连接器状态"""
        if connector_id not in self.connectors:
            return None
        
        connector = self.connectors[connector_id]
        
        return {
            "connector_id": connector.connector_id,
            "name": connector.name,
            "description": connector.description,
            "state": connector.state.value,
            "pid": connector.pid,
            "started_at": connector.started_at.isoformat() if connector.started_at else None,
            "error_message": connector.error_message
        }
    
    def list_connectors(self) -> List[Dict[str, Any]]:
        """列出所有连接器"""
        return [self.get_connector_status(cid) for cid in self.connectors.keys()]
    
    async def check_health(self):
        """检查所有连接器健康状态"""
        for connector_id, connector in self.connectors.items():
            if connector.state == ConnectorState.RUNNING and connector.process:
                # 检查进程是否还在运行
                if connector.process.poll() is not None:
                    # 进程已退出
                    logger.warning(f"检测到连接器进程退出: {connector_id}")
                    connector.state = ConnectorState.ERROR
                    connector.error_message = "进程意外退出"
                    connector.process = None
                    connector.pid = None
    
    async def start_all_registered_connectors(self):
        """启动所有已注册的连接器"""
        for connector_id in self.connectors.keys():
            await self.start_connector(connector_id)
    
    async def stop_all_connectors(self):
        """停止所有连接器"""
        tasks = []
        for connector_id in self.connectors.keys():
            if self.connectors[connector_id].state == ConnectorState.RUNNING:
                tasks.append(self.stop_connector(connector_id))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.info("所有连接器已停止")


# 全局单例
_simple_connector_manager = None

def get_connector_manager(connectors_dir: Path = None) -> ConnectorManager:
    """获取连接器管理器单例"""
    global _simple_connector_manager
    if _simple_connector_manager is None:
        if connectors_dir is None:
            # 使用默认路径
            from config.core_config import get_connector_config
            connector_config = get_connector_config()
            connectors_dir = Path(connector_config.config_dir)
        
        _simple_connector_manager = ConnectorManager(connectors_dir)
        
        # 手动注册已知连接器
        _register_known_connectors(_simple_connector_manager, connectors_dir)
    
    return _simple_connector_manager

def _register_known_connectors(manager: ConnectorManager, connectors_dir: Path):
    """扫描并注册已安装的连接器"""
    import json
    
    # 支持的连接器目录类型
    connector_dirs = ["official", "community"]
    
    for dir_type in connector_dirs:
        connector_type_dir = connectors_dir / dir_type
        if not connector_type_dir.exists():
            logger.debug(f"{dir_type}连接器目录不存在: {connector_type_dir}")
            continue
        
        # 遍历每个连接器目录
        for connector_path in connector_type_dir.iterdir():
            if not connector_path.is_dir():
                continue
                
            # 读取 connector.json 配置文件
            config_file = connector_path / "connector.json"
            if not config_file.exists():
                logger.debug(f"连接器配置文件不存在: {config_file}")
                continue
                
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 注册连接器
                manager.register_connector(
                    config["id"],
                    config["name"], 
                    config["description"],
                    connector_path
                )
                logger.info(f"已注册{dir_type}连接器: {config['id']} - {config['name']}")
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"读取连接器配置失败 {config_file}: {e}")
                continue