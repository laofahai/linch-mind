from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

Base = declarative_base()


class Connector(Base):
    """连接器表 - 匹配UI模型的完整版本"""
    __tablename__ = "connectors"
    
    # 基本信息
    connector_id = Column(String, primary_key=True)  # filesystem, clipboard等
    name = Column(String, nullable=False)  # 显示名称 (display_name)
    description = Column(Text)
    config = Column(JSON)  # 连接器配置，包含entry_point等信息
    
    # 配置管理 - 新增字段
    config_schema = Column(JSON)  # 连接器配置的JSON Schema定义
    config_version = Column(String, default="1.0.0")  # 配置版本号
    config_valid = Column(Boolean, default=True)  # 配置是否有效
    config_validation_errors = Column(JSON)  # 配置验证错误信息
    
    # 运行状态 - 匹配UI ConnectorState枚举
    status = Column(String, nullable=False, default="configured")  # configured, running, error, stopping
    enabled = Column(Boolean, nullable=False, default=True)  # 是否启用
    auto_start = Column(Boolean, nullable=False, default=True)  # 是否自动启动
    process_id = Column(Integer)  # 连接器进程ID
    
    # 错误和监控信息
    error_message = Column(Text)  # 错误信息
    last_heartbeat = Column(DateTime)  # 最后心跳时间
    data_count = Column(Integer, default=0)  # 数据量统计
    
    # 时间戳
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # 关系
    config_history = relationship("ConnectorConfigHistory", back_populates="connector", cascade="all, delete-orphan")


# ConnectorInstance表已删除 - 不再使用instance概念


class ConnectorConfigHistory(Base):
    """连接器配置历史表 - 追踪配置变更"""
    __tablename__ = "connector_config_history"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 关联连接器
    connector_id = Column(String, ForeignKey("connectors.connector_id"), nullable=False)
    
    # 配置信息
    config_data = Column(JSON, nullable=False)  # 配置内容快照
    config_version = Column(String, nullable=False)  # 配置版本
    schema_version = Column(String)  # Schema版本
    
    # 变更信息
    change_type = Column(String, nullable=False)  # create, update, delete, validate
    change_description = Column(Text)  # 变更描述
    changed_by = Column(String)  # 变更者(系统/用户)
    
    # 验证信息
    validation_status = Column(String, nullable=False, default="valid")  # valid, invalid, warning
    validation_errors = Column(JSON)  # 验证错误详细信息
    
    # 时间戳
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 关系
    connector = relationship("Connector", back_populates="config_history")


class ConnectorConfigTemplate(Base):
    """连接器配置模板表 - 用于快速创建配置"""
    __tablename__ = "connector_config_templates"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 模板信息
    name = Column(String, nullable=False)  # 模板名称
    description = Column(Text)  # 模板描述
    # 移除connector_type字段，不再依赖类型
    
    # 模板内容
    config_template = Column(JSON, nullable=False)  # 配置模板
    config_schema = Column(JSON, nullable=False)  # Schema定义
    
    # 分类和标签
    category = Column(String)  # 模板分类
    tags = Column(JSON)  # 标签列表
    
    # 使用统计
    usage_count = Column(Integer, default=0)  # 使用次数
    
    # 状态
    enabled = Column(Boolean, default=True)  # 是否启用
    
    # 时间戳
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class EntityMetadata(Base):
    """实体元数据表 - 知识图谱核心"""
    __tablename__ = "entity_metadata"
    
    id = Column(String, primary_key=True)
    entity_type = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    source_path = Column(String)  # 来源文件路径
    entity_metadata = Column(JSON)       # 扩展属性
    embedding_id = Column(String) # 对应向量ID
    
    # 时间戳
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_accessed = Column(DateTime)
    
    # 统计信息
    access_count = Column(Integer, default=0)
    relevance_score = Column(Float, default=0.0)
    
    def __repr__(self):
        return f"<EntityMetadata(id='{self.id}', name='{self.name}', type='{self.entity_type}')>"


class UserBehavior(Base):
    """用户行为追踪表 - 推荐算法基础"""
    __tablename__ = "user_behaviors"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String, nullable=False, index=True)
    action_type = Column(String, nullable=False)  # search, view, click, create
    target_entity = Column(String, index=True)
    context_data = Column(JSON)  # 上下文信息
    
    # 行为特征
    duration_ms = Column(Integer)
    scroll_depth = Column(Float)
    interaction_strength = Column(Float)
    
    # 时间信息
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<UserBehavior(id={self.id}, action='{self.action_type}', target='{self.target_entity}')>"


class EntityRelationship(Base):
    """实体关系表 - 知识图谱边"""
    __tablename__ = "entity_relationships"
    
    id = Column(Integer, primary_key=True)
    source_entity = Column(String, nullable=False, index=True)
    target_entity = Column(String, nullable=False, index=True)
    relationship_type = Column(String, nullable=False)
    
    # 关系属性
    strength = Column(Float, default=1.0)
    confidence = Column(Float, default=1.0)
    relationship_data = Column(JSON)
    
    # 时间信息
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<EntityRelationship(id={self.id}, {self.source_entity} -> {self.target_entity})>"


class AIConversation(Base):
    """AI对话历史表 - 极高敏感数据"""
    __tablename__ = "ai_conversations"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String, nullable=False, index=True)
    
    # 对话内容
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    context_entities = Column(JSON)  # 相关实体
    
    # 对话特征
    message_type = Column(String)  # question, command, chat
    satisfaction_rating = Column(Integer)  # 用户反馈
    processing_time_ms = Column(Integer)
    
    # 时间信息
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<AIConversation(id={self.id}, session='{self.session_id}', type='{self.message_type}')>"


