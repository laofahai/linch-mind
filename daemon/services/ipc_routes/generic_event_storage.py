"""
通用事件存储接口 - 与连接器类型完全无关
提供连接器无关的事件存储和处理机制，集成内容分析功能
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from core.service_facade import get_service
from models.database_models import ConnectorLog, EntityMetadata
from services.unified_database_service import UnifiedDatabaseService

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
                self._db_service = get_service(UnifiedDatabaseService)
            except Exception as e:
                logger.warning(f"Database service not available: {str(e)}")
                return None
        return self._db_service

    async def store_generic_event(
        self,
        connector_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        timestamp: str,
        metadata: Optional[Dict[str, Any]],
    ) -> bool:
        """
        存储通用连接器事件，并进行内容分析

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

            # 尝试进行内容分析
            content_analysis = await self._analyze_event_content(event_data, event_type)

            # 构建通用的存储结构，确保metadata不为None
            entity_properties = {
                "connector_id": connector_id,
                "event_type": event_type,
                "timestamp": timestamp,
                "event_data": event_data,  # 原始事件数据，不做任何解析
                "metadata": metadata or {},  # 确保不为None
                "processed_at": datetime.utcnow().isoformat(),
                "content_analysis": content_analysis,  # 添加内容分析结果
            }

            with self.db_service.get_session() as session:
                # 检查是否已存在相同事件
                existing = (
                    session.query(EntityMetadata).filter_by(entity_id=entity_id).first()
                )

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
                        access_count=1,
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
                        "timestamp": timestamp,
                    },
                )
                session.add(log_entry)

                session.commit()

            logger.info(f"✅ Stored generic event from {connector_id}: {event_type}")
            return True

        except Exception as e:
            logger.error(f"Failed to store generic event: {str(e)}")
            return False

    async def _analyze_event_content(
        self, event_data: Dict[str, Any], event_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        分析事件内容

        Args:
            event_data: 事件数据
            event_type: 事件类型

        Returns:
            内容分析结果
        """
        try:
            # 尝试导入内容分析服务
            from services.content_analysis_service import get_content_analysis_service

            analysis_service = get_content_analysis_service()

            # 尝试从事件数据中提取文本内容
            content = self._extract_content_from_event(event_data)
            if not content:
                return None

            # 确定内容类型
            content_type = self._determine_content_type(event_data, event_type)

            # 执行内容分析
            analysis_result = analysis_service.analyze_content(content, content_type)

            logger.debug(f"内容分析完成: {len(content)} 字符, 类型: {content_type}")
            return analysis_result

        except ImportError:
            logger.warning("内容分析服务不可用")
            return None
        except Exception as e:
            logger.error(f"内容分析失败: {e}")
            return None

    def _extract_content_from_event(self, event_data: Dict[str, Any]) -> Optional[str]:
        """从事件数据中提取文本内容"""
        # 常见的内容字段名
        content_fields = ["content", "text", "data", "message", "body", "value"]

        for field in content_fields:
            if field in event_data:
                content = event_data[field]
                if isinstance(content, str) and content.strip():
                    return content.strip()

        # 如果没有明确的内容字段，尝试转换整个事件数据为字符串
        if isinstance(event_data, dict) and len(event_data) == 1:
            # 单字段事件数据
            value = list(event_data.values())[0]
            if isinstance(value, str) and value.strip():
                return value.strip()

        return None

    def _determine_content_type(
        self, event_data: Dict[str, Any], event_type: str
    ) -> str:
        """确定内容类型"""
        # 基于事件类型推断
        if event_type in ["url_changed", "url_copied", "link_event"]:
            return "url"
        elif event_type in ["file_changed", "file_copied", "file_event"]:
            return "file_path"
        elif event_type in ["clipboard_changed", "content_changed"]:
            # 剪贴板事件，需要进一步分析内容
            content = self._extract_content_from_event(event_data)
            if content:
                # 简单启发式判断
                if content.startswith(("http://", "https://")):
                    return "url"
                elif "/" in content or "\\" in content:
                    return "file_path"
            return "text"

        # 基于事件数据推断
        content_type_field = event_data.get("content_type", event_data.get("type"))
        if content_type_field:
            return str(content_type_field)

        return "text"


# 单例模式
_generic_storage = None


def get_generic_event_storage() -> GenericEventStorage:
    """获取通用事件存储实例"""
    global _generic_storage
    if _generic_storage is None:
        _generic_storage = GenericEventStorage()
    return _generic_storage
