#!/usr/bin/env python3
"""
简化的数据模型 - Session V65
移除实例概念，只保留必要的连接器类型和数据项模型
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class DataItem(Base):
    """数据项表 - 连接器收集的数据"""
    __tablename__ = "data_items"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)  # 数据标题
    content = Column(Text, nullable=False)  # 数据内容
    source_connector = Column(String, nullable=False)  # 来源连接器ID
    source_path = Column(String)  # 原始路径或标识
    content_type = Column(String, default="text")  # text, file, image, etc.
    item_metadata = Column(JSON)  # 额外的元数据
    file_size = Column(Integer)  # 文件大小（字节）
    checksum = Column(String)  # 文件校验和，用于检测变更
    
    # 时间戳
    collected_at = Column(DateTime, nullable=False)  # 收集时间
    modified_at = Column(DateTime)  # 原始文件修改时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 索引和状态
    indexed = Column(Boolean, default=False)  # 是否已建立索引
    active = Column(Boolean, default=True)  # 是否活跃（未删除）


class ConnectorType(Base):
    """连接器类型表 - 简化版本，只保留必要信息"""
    __tablename__ = "connector_types"
    
    type_id = Column(String, primary_key=True)  # filesystem, clipboard
    name = Column(String, nullable=False)
    description = Column(Text)
    executable_path = Column(String, nullable=False)  # 连接器可执行文件路径
    version = Column(String, default="1.0")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_enabled = Column(Boolean, default=True)


class ConnectorProcess(Base):
    """连接器进程表 - 简化的运行时状态管理"""
    __tablename__ = "connector_processes"
    
    connector_id = Column(String, primary_key=True)  # 对应ConnectorType.type_id
    process_id = Column(Integer)  # 系统进程ID
    status = Column(String, nullable=False, default="stopped")  # stopped, running, error
    
    # 基本运行时信息
    started_at = Column(DateTime)
    error_message = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


