"""
数据库模型 - 使用清晰的连接器状态设计
分离基本状态(enabled)和运行状态(running_state)
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship
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
    version = Column(String(50), nullable=True)  # 连接器版本
    path = Column(String(500), nullable=True)  # 可执行文件路径

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
            "version": self.version,
            "path": self.path,
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
        String(255),
        ForeignKey("connectors.connector_id", ondelete="CASCADE"),
        nullable=False,
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
        String(255),
        ForeignKey("connectors.connector_id", ondelete="CASCADE"),
        nullable=False,
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
        String(255),
        ForeignKey("connectors.connector_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
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


# 用户配置模型类


class SystemConfigEntry(Base):
    """
    系统配置条目模型 - 统一的数据库配置存储
    替代大部分配置文件，支持环境隔离和动态配置
    """

    __tablename__ = "system_config_entries"

    # 基本信息
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 环境和作用域
    environment = Column(String(50), default="default", nullable=False, index=True)  # development, staging, production, default
    scope = Column(String(50), default="system", nullable=False, index=True)  # system, user, connector
    
    # 配置分类和键值
    config_section = Column(String(100), nullable=False, index=True)  # database, ollama, vector, ipc, security等
    config_key = Column(String(255), nullable=False, index=True)
    config_value = Column(JSON, nullable=False)  # 支持各种数据类型
    
    # 配置元数据
    config_type = Column(String(50), nullable=False)  # system_setting, user_preference, runtime_config, environment_config
    value_type = Column(String(50), nullable=False)  # string, number, boolean, array, object
    is_sensitive = Column(Boolean, default=False, nullable=False)  # 敏感信息标记
    
    # 描述和验证
    description = Column(Text, nullable=True)
    validation_rule = Column(JSON, nullable=True)  # 验证规则
    default_value = Column(JSON, nullable=True)  # 默认值
    
    # 访问控制和行为
    is_readonly = Column(Boolean, default=False, nullable=False)  # 只读配置
    requires_restart = Column(Boolean, default=False, nullable=False)  # 是否需要重启生效
    priority = Column(Integer, default=100, nullable=False)  # 配置优先级（数字越小优先级越高）
    
    # 配置来源和分组
    source = Column(String(100), nullable=True)  # migration, user_input, system_init, import
    config_group = Column(String(100), nullable=True)  # 配置分组，便于批量管理
    tags = Column(JSON, nullable=True)  # 配置标签，便于搜索和过滤
    
    # 统计信息
    access_count = Column(Integer, default=0, nullable=False)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    last_modified_by = Column(String(255), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 唯一约束：作用域+配置段+配置键（环境隔离通过目录实现）
    __table_args__ = (
        UniqueConstraint('scope', 'config_section', 'config_key', name='uq_system_config'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "environment": self.environment,
            "scope": self.scope,
            "config_section": self.config_section,
            "config_key": self.config_key,
            "config_value": self.config_value,
            "config_type": self.config_type,
            "value_type": self.value_type,
            "is_sensitive": self.is_sensitive,
            "description": self.description,
            "validation_rule": self.validation_rule,
            "default_value": self.default_value,
            "is_readonly": self.is_readonly,
            "requires_restart": self.requires_restart,
            "priority": self.priority,
            "source": self.source,
            "config_group": self.config_group,
            "tags": self.tags,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "last_modified_by": self.last_modified_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class SystemConfigHistory(Base):
    """
    系统配置变更历史记录模型
    记录所有配置的变更历史，支持审计和回滚
    """

    __tablename__ = "system_config_history"

    # 基本信息
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 关联配置
    config_entry_id = Column(Integer, ForeignKey("system_config_entries.id", ondelete="CASCADE"), nullable=False, index=True)
    scope = Column(String(50), nullable=False)
    config_section = Column(String(100), nullable=False)
    config_key = Column(String(255), nullable=False)
    
    # 变更信息
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=False)
    change_type = Column(String(50), nullable=False)  # create, update, delete, reset, migrate
    change_reason = Column(Text, nullable=True)
    changed_by = Column(String(255), nullable=True)  # user, system, migration, import
    
    # 变更上下文
    change_context = Column(JSON, nullable=True)  # 变更时的额外上下文信息
    batch_id = Column(String(100), nullable=True)  # 批量操作ID
    
    # 验证信息
    validation_status = Column(String(50), default="valid", nullable=False)  # valid, invalid, warning
    validation_errors = Column(JSON, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 关系
    config_entry = relationship("SystemConfigEntry", backref="history")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "config_entry_id": self.config_entry_id,
            "scope": self.scope,
            "config_section": self.config_section,
            "config_key": self.config_key,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "change_type": self.change_type,
            "change_reason": self.change_reason,
            "changed_by": self.changed_by,
            "change_context": self.change_context,
            "batch_id": self.batch_id,
            "validation_status": self.validation_status,
            "validation_errors": self.validation_errors,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# UserConfigEntry 和 UserConfigHistory 已废弃并删除
# 现在统一使用 SystemConfigEntry 和 SystemConfigHistory


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
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

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
            "last_accessed": (
                self.last_accessed.isoformat() if self.last_accessed else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class EntityRelationship(Base):
    """实体关系模型"""

    __tablename__ = "entity_relationships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_entity_id = Column(
        String(255), ForeignKey("entity_metadata.entity_id"), nullable=False
    )
    target_entity_id = Column(
        String(255), ForeignKey("entity_metadata.entity_id"), nullable=False
    )

    relationship_type = Column(
        String(100), nullable=False
    )  # related_to, contains, depends_on等
    strength = Column(Integer, default=1, nullable=False)  # 关系强度 1-10
    description = Column(Text, nullable=True)

    # 元数据
    properties = Column(JSON, nullable=True)

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
    target_entity_id = Column(
        String(255), ForeignKey("entity_metadata.entity_id"), nullable=True
    )
    context = Column(JSON, nullable=True)  # 上下文信息

    # 时间和位置
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
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
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

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


class EventCorrelation(Base):
    """事件关联记录模型"""
    
    __tablename__ = "event_correlations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 关联信息
    pattern_name = Column(String(255), nullable=False, index=True)  # 关联模式名称
    confidence_score = Column(Integer, nullable=False)  # 置信度分数(0-100)
    time_window_seconds = Column(Integer, nullable=False)  # 时间窗口(秒)
    
    # 事件标识
    primary_event_id = Column(String(255), nullable=False)  # 主要事件ID
    related_event_ids = Column(JSON, nullable=False)  # 关联事件ID列表
    
    # 语义信息  
    semantic_tags = Column(JSON, nullable=False)  # 涉及的语义标签
    correlation_context = Column(JSON, nullable=True)  # 关联上下文信息
    
    # 统计信息
    events_count = Column(Integer, default=1)  # 包含的事件数量
    duration_seconds = Column(Integer, nullable=True)  # 总持续时间
    
    # 时间戳
    started_at = Column(DateTime(timezone=True), nullable=False)  # 开始时间
    ended_at = Column(DateTime(timezone=True), nullable=True)  # 结束时间
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "pattern_name": self.pattern_name,
            "confidence_score": self.confidence_score,
            "time_window_seconds": self.time_window_seconds,
            "primary_event_id": self.primary_event_id,
            "related_event_ids": self.related_event_ids,
            "semantic_tags": self.semantic_tags,
            "correlation_context": self.correlation_context,
            "events_count": self.events_count,
            "duration_seconds": self.duration_seconds,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SemanticTagUsage(Base):
    """语义标签使用统计模型"""
    
    __tablename__ = "semantic_tag_usage"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 标签信息
    tag_key = Column(String(255), nullable=False, index=True)  # 标签键
    tag_name = Column(String(255), nullable=False)  # 标签名称
    
    # 统计信息
    usage_count = Column(Integer, default=1)  # 使用次数
    confidence_sum = Column(Integer, default=0)  # 置信度总和
    avg_confidence = Column(Integer, default=0)  # 平均置信度
    
    # 关联信息
    connector_ids = Column(JSON, nullable=True)  # 相关连接器ID列表
    event_types = Column(JSON, nullable=True)  # 相关事件类型
    
    # 时间信息
    date = Column(DateTime(timezone=True), nullable=False, index=True)  # 统计日期
    last_used_at = Column(DateTime(timezone=True), nullable=False)  # 最后使用时间
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "tag_key": self.tag_key,
            "tag_name": self.tag_name,
            "usage_count": self.usage_count,
            "confidence_sum": self.confidence_sum,
            "avg_confidence": self.avg_confidence,
            "connector_ids": self.connector_ids,
            "event_types": self.event_types,
            "date": self.date.isoformat() if self.date else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CorrelationPattern(Base):
    """关联模式定义模型"""
    
    __tablename__ = "correlation_patterns"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 模式定义
    pattern_name = Column(String(255), unique=True, nullable=False, index=True)
    pattern_description = Column(Text, nullable=True)
    
    # 配置参数
    time_window_seconds = Column(Integer, nullable=False, default=300)  # 时间窗口
    confidence_threshold = Column(Integer, nullable=False, default=70)  # 置信度阈值(0-100)
    min_events_count = Column(Integer, nullable=False, default=2)  # 最少事件数量
    
    # 语义约束
    required_tags = Column(JSON, nullable=True)  # 必需的语义标签
    optional_tags = Column(JSON, nullable=True)  # 可选的语义标签
    excluded_tags = Column(JSON, nullable=True)  # 排除的语义标签
    
    # 模式规则
    pattern_rules = Column(JSON, nullable=True)  # 自定义模式规则
    
    # 状态管理
    enabled = Column(Boolean, default=True, nullable=False)  # 是否启用
    priority = Column(Integer, default=5, nullable=False)  # 优先级(1-10)
    
    # 统计信息
    match_count = Column(Integer, default=0)  # 匹配次数
    last_matched_at = Column(DateTime(timezone=True), nullable=True)  # 最后匹配时间
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "pattern_name": self.pattern_name,
            "pattern_description": self.pattern_description,
            "time_window_seconds": self.time_window_seconds,
            "confidence_threshold": self.confidence_threshold,
            "min_events_count": self.min_events_count,
            "required_tags": self.required_tags,
            "optional_tags": self.optional_tags,
            "excluded_tags": self.excluded_tags,
            "pattern_rules": self.pattern_rules,
            "enabled": self.enabled,
            "priority": self.priority,
            "match_count": self.match_count,
            "last_matched_at": self.last_matched_at.isoformat() if self.last_matched_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# 工厂函数


def create_new_connector(
    connector_id: str,
    name: str,
    description: Optional[str] = None,
    version: Optional[str] = None,
    path: Optional[str] = None,
    config_data: Optional[Dict[str, Any]] = None,
) -> Connector:
    """创建新连接器实例"""
    return Connector(
        connector_id=connector_id,
        name=name,
        description=description,
        version=version,
        path=path,
        enabled=True,  # 新连接器默认启用
        status="stopped",  # 初始状态为停止
        config_data=config_data or {},
        connector_metadata={},
    )


def create_disabled_connector(
    connector_id: str,
    name: str,
    description: Optional[str] = None,
    version: Optional[str] = None,
    path: Optional[str] = None,
) -> Connector:
    """创建禁用连接器实例"""
    return Connector(
        connector_id=connector_id,
        name=name,
        description=description,
        version=version,
        path=path,
        enabled=False,  # 禁用状态
        status="stopped",
        config_data={},
        connector_metadata={},
    )
