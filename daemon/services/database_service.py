#!/usr/bin/env python3
"""
简化的数据库服务 - Session V65
使用简化的数据模型，移除复杂的实例管理
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from config.core_config import get_database_config
from models.core_models import Base, DataItem, ConnectorType, ConnectorProcess

logger = logging.getLogger(__name__)


class DatabaseService:
    """简化的数据库服务"""
    
    def __init__(self):
        self.db_config = get_database_config()
        self.engine = create_engine(
            self.db_config.sqlite_url,
            echo=False,  # 生产环境关闭SQL日志
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        # 创建数据表
        Base.metadata.create_all(self.engine)
        
        # 创建会话工厂
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        logger.info("数据库服务初始化完成")
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()
    
    # 连接器类型管理
    def register_connector_type(self, connector_info: Dict[str, Any]) -> bool:
        """注册连接器类型"""
        try:
            with self.get_session() as session:
                # 检查是否已存在
                existing = session.query(ConnectorType).filter(
                    ConnectorType.type_id == connector_info["type_id"]
                ).first()
                
                if existing:
                    # 更新现有记录
                    for key, value in connector_info.items():
                        setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                else:
                    # 创建新记录
                    connector_type = ConnectorType(**connector_info)
                    session.add(connector_type)
                
                session.commit()
                logger.info(f"连接器类型注册成功: {connector_info['type_id']}")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"注册连接器类型失败: {e}")
            return False
    
    def get_connector_types(self) -> List[ConnectorType]:
        """获取所有连接器类型"""
        try:
            with self.get_session() as session:
                return session.query(ConnectorType).filter(
                    ConnectorType.is_enabled == True
                ).all()
        except SQLAlchemyError as e:
            logger.error(f"获取连接器类型失败: {e}")
            return []
    
    def get_connector_type(self, type_id: str) -> Optional[ConnectorType]:
        """获取指定连接器类型"""
        try:
            with self.get_session() as session:
                return session.query(ConnectorType).filter(
                    ConnectorType.type_id == type_id
                ).first()
        except SQLAlchemyError as e:
            logger.error(f"获取连接器类型失败 {type_id}: {e}")
            return None
    
    # 连接器进程管理
    def update_connector_process(self, connector_id: str, process_info: Dict[str, Any]) -> bool:
        """更新连接器进程信息"""
        try:
            with self.get_session() as session:
                process = session.query(ConnectorProcess).filter(
                    ConnectorProcess.connector_id == connector_id
                ).first()
                
                if process:
                    # 更新现有记录
                    for key, value in process_info.items():
                        setattr(process, key, value)
                    process.updated_at = datetime.utcnow()
                else:
                    # 创建新记录
                    process_info["connector_id"] = connector_id
                    process = ConnectorProcess(**process_info)
                    session.add(process)
                
                session.commit()
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"更新连接器进程信息失败: {e}")
            return False
    
    def get_connector_process(self, connector_id: str) -> Optional[ConnectorProcess]:
        """获取连接器进程信息"""
        try:
            with self.get_session() as session:
                return session.query(ConnectorProcess).filter(
                    ConnectorProcess.connector_id == connector_id
                ).first()
        except SQLAlchemyError as e:
            logger.error(f"获取连接器进程信息失败 {connector_id}: {e}")
            return None
    
    def get_all_connector_processes(self) -> List[ConnectorProcess]:
        """获取所有连接器进程信息"""
        try:
            with self.get_session() as session:
                return session.query(ConnectorProcess).all()
        except SQLAlchemyError as e:
            logger.error(f"获取所有连接器进程信息失败: {e}")
            return []
    
    # 数据项管理
    def store_data_item(self, data_item: Dict[str, Any]) -> bool:
        """存储数据项"""
        try:
            with self.get_session() as session:
                # 检查是否已存在（基于checksum或source_path）
                existing = None
                if data_item.get("checksum"):
                    existing = session.query(DataItem).filter(
                        and_(
                            DataItem.source_connector == data_item["source_connector"],
                            DataItem.checksum == data_item["checksum"]
                        )
                    ).first()
                elif data_item.get("source_path"):
                    existing = session.query(DataItem).filter(
                        and_(
                            DataItem.source_connector == data_item["source_connector"],
                            DataItem.source_path == data_item["source_path"]
                        )
                    ).first()
                
                if existing:
                    # 更新现有数据项
                    for key, value in data_item.items():
                        setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                    logger.debug(f"数据项更新: {existing.id}")
                else:
                    # 创建新数据项
                    if "id" not in data_item:
                        import uuid
                        data_item["id"] = str(uuid.uuid4())
                    
                    item = DataItem(**data_item)
                    session.add(item)
                    logger.debug(f"数据项创建: {item.id}")
                
                session.commit()
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"存储数据项失败: {e}")
            return False
    
    def get_data_items(self, 
                      connector_id: Optional[str] = None, 
                      limit: int = 100, 
                      offset: int = 0) -> List[DataItem]:
        """获取数据项"""
        try:
            with self.get_session() as session:
                query = session.query(DataItem).filter(DataItem.active == True)
                
                if connector_id:
                    query = query.filter(DataItem.source_connector == connector_id)
                
                return query.order_by(DataItem.created_at.desc()).offset(offset).limit(limit).all()
                
        except SQLAlchemyError as e:
            logger.error(f"获取数据项失败: {e}")
            return []
    
    def count_data_items(self, connector_id: Optional[str] = None) -> int:
        """统计数据项数量"""
        try:
            with self.get_session() as session:
                query = session.query(DataItem).filter(DataItem.active == True)
                
                if connector_id:
                    query = query.filter(DataItem.source_connector == connector_id)
                
                return query.count()
                
        except SQLAlchemyError as e:
            logger.error(f"统计数据项失败: {e}")
            return 0
    
    # 系统统计
    
    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            with self.get_session() as session:
                connector_types_count = session.query(ConnectorType).count()
                active_connectors_count = session.query(ConnectorProcess).filter(
                    ConnectorProcess.status == "running"
                ).count()
                data_items_count = session.query(DataItem).filter(DataItem.active == True).count()
                return {
                    "connector_types": connector_types_count,
                    "active_connectors": active_connectors_count,
                    "data_items": data_items_count,
                    "database_path": self.db_config.sqlite_url
                }
                
        except SQLAlchemyError as e:
            logger.error(f"获取数据库统计失败: {e}")
            return {}


# 全局单例
_simple_database_service = None

def get_database_service() -> DatabaseService:
    """获取数据库服务单例"""
    global _simple_database_service
    if _simple_database_service is None:
        _simple_database_service = DatabaseService()
    return _simple_database_service