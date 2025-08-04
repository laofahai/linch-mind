from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class DataItem(Base):
    """数据项表"""
    __tablename__ = "data_items"
    
    id = Column(String, primary_key=True)
    content = Column(Text, nullable=False)
    source_connector = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    file_path = Column(String)
    meta_data = Column(JSON)
    storage_strategy = Column(String)  # 存储策略 (extract_semantics, summarize_only, full_content, etc.)
    original_size = Column(Integer)    # 原始文件大小
    processed_size = Column(Integer)   # 处理后大小
    processing_info = Column(JSON)     # 处理相关信息
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联到图节点
    graph_nodes = relationship("GraphNode", back_populates="source_data")


class ConnectorType(Base):
    """连接器类型表 - 注册所有可用的连接器类型"""
    __tablename__ = "connector_types"
    
    type_id = Column(String, primary_key=True)  # filesystem, clipboard, obsidian, etc.
    name = Column(String, nullable=False)
    display_name = Column(String, nullable=False)  # 用户友好的显示名称
    description = Column(Text)
    category = Column(String, nullable=False)  # local_files, cloud_services, communication, etc.
    executable_path = Column(String, nullable=False)  # 连接器可执行文件路径
    icon = Column(String)  # 图标路径或名称
    version = Column(String, default="1.0")
    author = Column(String)  # 连接器作者
    license = Column(String)  # 许可证
    homepage = Column(String)  # 主页链接
    
    # 连接器能力配置 (由连接器自己定义)
    supports_multiple_instances = Column(Boolean, default=False)  # 是否支持多实例
    max_instances_per_user = Column(Integer, default=1)  # 每用户最大实例数
    instance_isolation = Column(String, default="process")  # 实例隔离方式: process, thread, none
    auto_discovery = Column(Boolean, default=False)  # 是否支持自动发现配置
    hot_config_reload = Column(Boolean, default=False)  # 是否支持热重载配置
    health_check = Column(Boolean, default=True)  # 是否支持健康检查
    metrics_reporting = Column(Boolean, default=False)  # 是否支持指标上报
    
    # 配置Schema
    config_schema = Column(JSON, nullable=False)  # JSON Schema定义
    ui_schema = Column(JSON)  # UI渲染提示
    default_config = Column(JSON)  # 默认配置值
    instance_templates = Column(JSON)  # 实例模板 (预定义的配置模板)
    
    # 系统要求
    system_requirements = Column(JSON)  # 系统要求 (平台、内存、权限等)
    dependencies = Column(JSON)  # 依赖包列表
    
    # 管理信息
    is_enabled = Column(Boolean, default=True)
    installation_path = Column(String)  # 安装路径
    package_info = Column(JSON)  # 包信息 (安装来源、版本等)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConnectorInstance(Base):
    """连接器实例表 - 用户创建的连接器实例"""
    __tablename__ = "connector_instances"
    
    instance_id = Column(String, primary_key=True)  # 用户定义的实例ID
    display_name = Column(String, nullable=False)  # 用户友好的显示名称
    type_id = Column(String, ForeignKey("connector_types.type_id"), nullable=False)
    config = Column(JSON, nullable=False)  # 实例的具体配置
    status = Column(String, nullable=False, default="installed")  # installed, running, error
    process_id = Column(Integer)  # 连接器进程ID
    data_count = Column(Integer, default=0)
    last_heartbeat = Column(DateTime)
    error_message = Column(Text)
    auto_start = Column(Boolean, default=True)  # 是否自动启动
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联到连接器类型
    connector_type = relationship("ConnectorType")


class AIRecommendation(Base):
    """AI推荐表"""
    __tablename__ = "recommendations"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    confidence = Column(Float, nullable=False)
    related_items = Column(JSON)  # List[str]
    created_at = Column(DateTime, nullable=False)


class GraphNode(Base):
    """图节点表"""
    __tablename__ = "graph_nodes"
    
    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)  # person, document, concept, etc.
    label = Column(String, nullable=False)
    properties = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    source_data_id = Column(String, ForeignKey("data_items.id"))
    
    # 关系
    source_data = relationship("DataItem", back_populates="graph_nodes")
    outgoing_relationships = relationship("GraphRelationship", 
                                        foreign_keys="GraphRelationship.source_node_id",
                                        back_populates="source_node")
    incoming_relationships = relationship("GraphRelationship", 
                                        foreign_keys="GraphRelationship.target_node_id",
                                        back_populates="target_node")


class GraphRelationship(Base):
    """图关系表"""
    __tablename__ = "graph_relationships"
    
    id = Column(String, primary_key=True)
    source_node_id = Column(String, ForeignKey("graph_nodes.id"), nullable=False)
    target_node_id = Column(String, ForeignKey("graph_nodes.id"), nullable=False)
    relationship_type = Column(String, nullable=False)  # mentions, contains, related_to, etc.
    weight = Column(Float, default=1.0)
    properties = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    source_node = relationship("GraphNode", 
                              foreign_keys=[source_node_id],
                              back_populates="outgoing_relationships")
    target_node = relationship("GraphNode", 
                              foreign_keys=[target_node_id],
                              back_populates="incoming_relationships")