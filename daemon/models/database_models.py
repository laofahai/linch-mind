"""
数据库模型 - 使用清晰的连接器状态设计
分离基本状态(enabled)和运行状态(running_state)
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from sqlalchemy import (JSON, Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .connector_status import ConnectorRunningState

Base = declarative_base()


class Connector(Base):
    """
    连接器模型 - 使用清晰的状态设计

    状态字段说明：
    - enabled: 是否启用（基本状态），决定是否自动启动
    - status: 运行状态字符串，对应 ConnectorRunningState 枚举
    - 移除 auto_start 字段，简化逻辑
    """

    __tablename__ = "connectors"

    # 基本信息
    id = Column(Integer, primary_key=True, autoincrement=True)
    connector_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)  # display_name
    description = Column(Text, nullable=True)

    # 状态管理 - 新设计
    enabled = Column(Boolean, default=True, nullable=False)  # 是否启用（基本状态）
    status = Column(String(50), default="stopped", nullable=False)  # 运行状态

    # 进程信息
    process_id = Column(Integer, nullable=True)
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)

    # 统计信息
    data_count = Column(Integer, default=0, nullable=False)
    last_activity = Column(String(500), nullable=True)

    # 错误信息
    error_message = Column(Text, nullable=True)
    error_code = Column(String(100), nullable=True)

    # 配置和元数据
    config_data = Column(JSON, nullable=True)
    config_schema = Column(JSON, nullable=True)  # 配置Schema
    config_version = Column(String(50), nullable=True)  # 配置版本
    config_valid = Column(Boolean, default=True)  # 配置是否有效
    config_validation_errors = Column(JSON, nullable=True)  # 验证错误信息
    connector_metadata = Column(JSON, nullable=True)

    # 时间戳
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    last_run_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def running_state(self) -> ConnectorRunningState:
        """获取运行状态枚举"""
        return ConnectorRunningState.from_string(self.status)

    @running_state.setter
    def running_state(self, state: ConnectorRunningState):
        """设置运行状态枚举"""
        if isinstance(state, ConnectorRunningState):
            self.status = state.value
        else:
            self.status = str(state)

    @property
    def is_installed(self) -> bool:
        """虚拟字段：是否已安装（数据库中存在即为已安装）"""
        return True

    @property
    def is_healthy(self) -> bool:
        """是否健康"""
        return self.enabled and self.status == "running"

    @property
    def should_be_running(self) -> bool:
        """是否应该运行"""
        return self.enabled

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典 - 用于API响应"""
        return {
            "id": self.id,
            "connector_id": self.connector_id,
            "display_name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "running_state": self.status,
            "is_installed": self.is_installed,
            "is_healthy": self.is_healthy,
            "should_be_running": self.should_be_running,
            "process_id": self.process_id,
            "last_heartbeat": (
                self.last_heartbeat.isoformat() if self.last_heartbeat else None
            ),
            "data_count": self.data_count,
            "last_activity": self.last_activity,
            "error_message": self.error_message,
            "error_code": self.error_code,
            "config_data": self.config_data,
            "connector_metadata": self.connector_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
        }

    def set_error(self, message: str, code: Optional[str] = None):
        """设置错误状态"""
        self.status = "error"
        self.error_message = message
        self.error_code = code
        self.updated_at = datetime.now(timezone.utc)

    def clear_error(self):
        """清除错误状态"""
        if self.status == "error":
            self.status = "stopped"
        self.error_message = None
        self.error_code = None
        self.updated_at = datetime.now(timezone.utc)

    def update_heartbeat(self, process_id: Optional[int] = None):
        """更新心跳信息"""
        self.last_heartbeat = datetime.now(timezone.utc)
        if process_id:
            self.process_id = process_id
        # 如果是启动中状态，心跳后变为运行状态
        if self.status == "starting":
            self.status = "running"
        self.updated_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return f"<Connector(id={self.id}, connector_id='{self.connector_id}', enabled={self.enabled}, status='{self.status}')>"


class ConnectorLog(Base):
    """连接器日志记录"""

    __tablename__ = "connector_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    connector_id = Column(
        String(255), ForeignKey("connectors.connector_id"), nullable=False
    )
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # 关系
    connector = relationship("Connector", backref="logs")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "connector_id": self.connector_id,
            "level": self.level,
            "message": self.message,
            "details": self.details,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ConnectorStats(Base):
    """连接器统计信息（按天聚合）"""

    __tablename__ = "connector_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    connector_id = Column(
        String(255), ForeignKey("connectors.connector_id"), nullable=False
    )
    date = Column(DateTime(timezone=True), nullable=False)

    # 统计指标
    uptime_seconds = Column(Integer, default=0)  # 运行时间（秒）
    data_processed = Column(Integer, default=0)  # 处理的数据条数
    errors_count = Column(Integer, default=0)  # 错误次数
    restarts_count = Column(Integer, default=0)  # 重启次数

    # 时间戳
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # 关系
    connector = relationship("Connector", backref="stats")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "connector_id": self.connector_id,
            "date": self.date.isoformat() if self.date else None,
            "uptime_seconds": self.uptime_seconds,
            "data_processed": self.data_processed,
            "errors_count": self.errors_count,
            "restarts_count": self.restarts_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ConnectorConfigHistory(Base):
    """
    连接器配置历史记录模型

    记录配置的变更历史，用于审计和回滚
    """

    __tablename__ = "connector_config_history"

    # 基本信息
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 配置信息
    config_data = Column(JSON, nullable=True)
    config_version = Column(String(50), nullable=True)
    schema_version = Column(String(50), nullable=True)

    # 变更信息
    change_type = Column(String(50), nullable=False)  # create, update, delete, reset
    change_description = Column(Text, nullable=True)
    changed_by = Column(String(255), nullable=True)

    # 验证信息
    validation_status = Column(String(50), nullable=True)  # valid, invalid
    validation_errors = Column(JSON, nullable=True)

    # 时间戳
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # 外键和关系
    connector_id = Column(
        String(255), ForeignKey("connectors.connector_id"), nullable=False, index=True
    )

    # 关系
    connector = relationship(
        "Connector", backref="config_history", foreign_keys=[connector_id]
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "connector_id": self.connector_id,
            "config_data": self.config_data,
            "config_version": self.config_version,
            "schema_version": self.schema_version,
            "change_type": self.change_type,
            "change_description": self.change_description,
            "changed_by": self.changed_by,
            "validation_status": self.validation_status,
            "validation_errors": self.validation_errors,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# 数据模型类

class EntityMetadata(Base):
    """实体元数据模型"""
    __tablename__ = "entity_metadata"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False)
    type = Column(String(100), nullable=False)  # file, person, concept等
    description = Column(Text, nullable=True)
    
    # 元数据
    properties = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)  # 标签列表
    
    # 统计信息
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "properties": self.properties,
            "tags": self.tags,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class EntityRelationship(Base):
    """实体关系模型"""
    __tablename__ = "entity_relationships"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_entity_id = Column(String(255), ForeignKey("entity_metadata.entity_id"), nullable=False)
    target_entity_id = Column(String(255), ForeignKey("entity_metadata.entity_id"), nullable=False)
    
    relationship_type = Column(String(100), nullable=False)  # related_to, contains, depends_on等
    strength = Column(Integer, default=1, nullable=False)  # 关系强度 1-10
    description = Column(Text, nullable=True)
    
    # 元数据
    properties = Column(JSON, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    source_entity = relationship("EntityMetadata", foreign_keys=[source_entity_id])
    target_entity = relationship("EntityMetadata", foreign_keys=[target_entity_id])
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_entity_id": self.source_entity_id,
            "target_entity_id": self.target_entity_id,
            "relationship_type": self.relationship_type,
            "strength": self.strength,
            "description": self.description,
            "properties": self.properties,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class UserBehavior(Base):
    """用户行为记录模型"""
    __tablename__ = "user_behaviors"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), nullable=True)  # 会话ID
    
    # 行为信息
    action_type = Column(String(100), nullable=False)  # view, search, click, etc.
    target_entity_id = Column(String(255), ForeignKey("entity_metadata.entity_id"), nullable=True)
    context = Column(JSON, nullable=True)  # 上下文信息
    
    # 时间和位置
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    duration = Column(Integer, nullable=True)  # 持续时间（毫秒）
    
    # 关系
    target_entity = relationship("EntityMetadata", foreign_keys=[target_entity_id])
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "action_type": self.action_type,
            "target_entity_id": self.target_entity_id,
            "context": self.context,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "duration": self.duration,
        }


class AIConversation(Base):
    """AI对话记录模型"""
    __tablename__ = "ai_conversations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), nullable=False, index=True)
    
    # 对话内容
    user_input = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    
    # 元数据
    model_name = Column(String(100), nullable=True)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    context = Column(JSON, nullable=True)
    
    # 相关实体
    mentioned_entities = Column(JSON, nullable=True)  # 对话中提到的实体ID列表
    
    # 时间戳
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_input": self.user_input,
            "ai_response": self.ai_response,
            "model_name": self.model_name,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "context": self.context,
            "mentioned_entities": self.mentioned_entities,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


# 工厂函数


def create_new_connector(
    connector_id: str,
    name: str,
    description: Optional[str] = None,
    config_data: Optional[Dict[str, Any]] = None,
) -> Connector:
    """创建新连接器实例"""
    return Connector(
        connector_id=connector_id,
        name=name,
        description=description,
        enabled=True,  # 新连接器默认启用
        status="stopped",  # 初始状态为停止
        config_data=config_data or {},
        connector_metadata={},
    )


def create_disabled_connector(
    connector_id: str, name: str, description: Optional[str] = None
) -> Connector:
    """创建禁用连接器实例"""
    return Connector(
        connector_id=connector_id,
        name=name,
        description=description,
        enabled=False,  # 禁用状态
        status="stopped",
        config_data={},
        connector_metadata={},
    )
