"""
通用事件存储接口 - 与连接器类型完全无关
提供连接器无关的事件存储和处理机制
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from core.service_facade import get_service
from services.database_service import DatabaseService
from models.database_models import EntityMetadata, ConnectorLog

logger = logging.getLogger(__name__)


class GenericEventStorage:
    """
    通用事件存储 - 与连接器类型完全无关
    
    所有连接器使用相同的存储接口，不关心具体的事件内容或格式
    """
    
    def __init__(self):
        self._db_service = None
    
    @property
    def db_service(self):
        """懒加载数据库服务"""
        if self._db_service is None:
            try:
                self._db_service = get_service(DatabaseService)
            except Exception as e:
                logger.warning(f"Database service not available: {str(e)}")
                return None
        return self._db_service
    
    async def store_generic_event(self, connector_id: str, event_type: str, 
                                event_data: Dict[str, Any], timestamp: str, 
                                metadata: Optional[Dict[str, Any]]) -> bool:
        """
        存储通用连接器事件
        
        Args:
            connector_id: 连接器ID（任意字符串）
            event_type: 事件类型（任意字符串）
            event_data: 事件数据（任意JSON对象）
            timestamp: 时间戳
            metadata: 元数据（任意JSON对象，可选）
        
        Returns:
            bool: 存储是否成功
        """
        try:
            if self.db_service is None:
                logger.error("Database service is not available")
                return False
            
            # 生成通用实体ID（不依赖事件内容）
            entity_id = f"{connector_id}_{hash(str(event_data) + timestamp) % 1000000}"
            
            # 构建通用的存储结构，确保metadata不为None
            entity_properties = {
                "connector_id": connector_id,
                "event_type": event_type,
                "timestamp": timestamp,
                "event_data": event_data,  # 原始事件数据，不做任何解析
                "metadata": metadata or {},  # 确保不为None
                "processed_at": datetime.utcnow().isoformat()
            }
            
            with self.db_service.get_session() as session:
                # 检查是否已存在相同事件
                existing = session.query(EntityMetadata).filter_by(entity_id=entity_id).first()
                
                if existing:
                    # 更新现有记录
                    existing.properties = entity_properties
                    existing.updated_at = datetime.utcnow()
                    existing.access_count += 1
                    existing.last_accessed = datetime.utcnow()
                    logger.debug(f"Updated existing event: {entity_id}")
                else:
                    # 创建新记录 - 使用通用命名
                    entity_record = EntityMetadata(
                        entity_id=entity_id,
                        name=f"{connector_id}_{event_type}_{datetime.now().strftime('%H%M%S')}",
                        type="connector_event",  # 通用类型
                        description=f"Event from connector {connector_id}",
                        properties=entity_properties,
                        access_count=1
                    )
                    session.add(entity_record)
                    logger.debug(f"Created new event record: {entity_id}")
                
                # 记录连接器日志
                log_entry = ConnectorLog(
                    connector_id=connector_id,
                    level="INFO",
                    message=f"Event processed: {event_type}",
                    details={
                        "event_type": event_type,
                        "event_size": len(str(event_data)),
                        "metadata_keys": list((metadata or {}).keys()),
                        "timestamp": timestamp
                    }
                )
                session.add(log_entry)
                
                session.commit()
            
            logger.info(f"✅ Stored generic event from {connector_id}: {event_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store generic event: {str(e)}")
            return False


# 单例模式
_generic_storage = None

def get_generic_event_storage() -> GenericEventStorage:
    """获取通用事件存储实例"""
    global _generic_storage
    if _generic_storage is None:
        _generic_storage = GenericEventStorage()
    return _generic_storage