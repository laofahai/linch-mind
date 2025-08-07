"""
连接器状态枚举 - 修正版设计
分离基本状态和运行状态，更加清晰实用
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime


class ConnectorRunningState(Enum):
    """连接器运行状态"""
    STOPPED = "stopped"    # 已停止
    STARTING = "starting"  # 启动中  
    RUNNING = "running"    # 正在运行
    STOPPING = "stopping" # 停止中
    ERROR = "error"        # 错误状态
    
    @classmethod
    def from_string(cls, state: str) -> 'ConnectorRunningState':
        """从字符串创建状态"""
        try:
            return cls(state.lower())
        except ValueError:
            return cls.STOPPED


@dataclass
class ConnectorStatus:
    """
    连接器完整状态信息
    
    设计理念：
    - enabled: 基本状态，是否启用（决定是否自动启动）
    - running_state: 运行状态，表示实际运行情况
    - installed: 虚拟字段，通过数据库存在性计算
    """
    connector_id: str
    display_name: str
    enabled: bool = True                                    # 是否启用（基本状态）
    running_state: ConnectorRunningState = ConnectorRunningState.STOPPED  # 运行状态
    
    # 进程信息
    process_id: Optional[int] = None
    last_heartbeat: Optional[datetime] = None
    
    # 统计信息
    data_count: int = 0
    last_activity: Optional[str] = None
    
    # 错误信息
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    @property
    def is_installed(self) -> bool:
        """虚拟字段：是否已安装（通过数据库存在性判断）"""
        # 这个属性在实际使用时会被数据库服务层设置
        return True
    
    @property
    def is_healthy(self) -> bool:
        """是否健康"""
        return self.enabled and self.running_state == ConnectorRunningState.RUNNING
    
    @property
    def should_be_running(self) -> bool:
        """是否应该运行"""
        return self.enabled
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "connector_id": self.connector_id,
            "display_name": self.display_name,
            "enabled": self.enabled,
            "running_state": self.running_state.value,
            "is_installed": self.is_installed,
            "is_healthy": self.is_healthy,
            "should_be_running": self.should_be_running,
            "process_id": self.process_id,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "data_count": self.data_count,
            "last_activity": self.last_activity,
            "error_message": self.error_message,
            "error_code": self.error_code
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConnectorStatus':
        """从字典创建状态"""
        return cls(
            connector_id=data["connector_id"],
            display_name=data["display_name"],
            enabled=data.get("enabled", True),
            running_state=ConnectorRunningState.from_string(data.get("running_state", "stopped")),
            process_id=data.get("process_id"),
            last_heartbeat=datetime.fromisoformat(data["last_heartbeat"]) if data.get("last_heartbeat") else None,
            data_count=data.get("data_count", 0),
            last_activity=data.get("last_activity"),
            error_message=data.get("error_message"),
            error_code=data.get("error_code")
        )
    
    def set_error(self, error_message: str, error_code: Optional[str] = None):
        """设置错误状态"""
        self.running_state = ConnectorRunningState.ERROR
        self.error_message = error_message
        self.error_code = error_code
    
    def clear_error(self):
        """清除错误状态"""
        self.error_message = None
        self.error_code = None
        if self.running_state == ConnectorRunningState.ERROR:
            self.running_state = ConnectorRunningState.STOPPED
    
    def update_heartbeat(self):
        """更新心跳时间"""
        self.last_heartbeat = datetime.now()
        if self.running_state == ConnectorRunningState.STARTING:
            self.running_state = ConnectorRunningState.RUNNING


# 工厂函数

def create_new_connector_status(connector_id: str, display_name: str) -> ConnectorStatus:
    """创建新连接器的默认状态"""
    return ConnectorStatus(
        connector_id=connector_id,
        display_name=display_name,
        enabled=True,  # 新连接器默认启用
        running_state=ConnectorRunningState.STOPPED
    )

def create_disabled_connector_status(connector_id: str, display_name: str) -> ConnectorStatus:
    """创建禁用连接器状态"""
    return ConnectorStatus(
        connector_id=connector_id,
        display_name=display_name,
        enabled=False,
        running_state=ConnectorRunningState.STOPPED
    )