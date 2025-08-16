"""
通用事件存储接口 - 与连接器类型完全无关
提供连接器无关的事件存储和处理机制，集成内容分析功能和快速索引
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.service_facade import get_service
from models.database_models import ConnectorLog, EntityMetadata
from services.unified_database_service import UnifiedDatabaseService
from services.fast_index_storage_service import FastIndexStorageService
from services.storage.intelligent_event_processor import get_intelligent_event_processor

logger = logging.getLogger(__name__)


class GenericEventStorage:
    """
    通用事件存储 - 与连接器类型完全无关

    所有连接器使用相同的存储接口，不关心具体的事件内容或格式
    """

    def __init__(self):
        self._db_service = None
        self._fast_index_service = None
        self._intelligent_processor = None

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
    
    @property
    def fast_index_service(self):
        """懒加载快速索引服务"""
        if self._fast_index_service is None:
            try:
                self._fast_index_service = FastIndexStorageService()
                self._fast_index_service.initialize()
            except Exception as e:
                logger.warning(f"Fast index service not available: {str(e)}")
                return None
        return self._fast_index_service
    
    @property
    def intelligent_processor(self):
        """懒加载智能事件处理器"""
        if self._intelligent_processor is None:
            try:
                # 注意：这里是异步获取，需要在异步上下文中初始化
                # 在实际调用时会通过 await 初始化
                return None
            except Exception as e:
                logger.warning(f"Intelligent processor not available: {str(e)}")
                return None
        return self._intelligent_processor
    
    async def _ensure_intelligent_processor(self):
        """确保智能处理器已初始化"""
        if self._intelligent_processor is None:
            try:
                self._intelligent_processor = await get_intelligent_event_processor()
                logger.info("智能事件处理器已初始化")
            except Exception as e:
                logger.error(f"智能事件处理器初始化失败: {e}")
                self._intelligent_processor = None
        return self._intelligent_processor

    async def store_generic_event(
        self,
        connector_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        timestamp: str,
        metadata: Optional[Dict[str, Any]],
    ) -> bool:
        """
        存储通用连接器事件，优先使用智能AI处理

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
            # 处理快速索引事件（优先处理，不经过AI）
            if event_type == "file_indexed" and event_data.get("source") == "fast_indexer":
                await self._handle_fast_index_event(event_data)
                return True

            # 尝试使用智能处理器（AI驱动）
            processor = await self._ensure_intelligent_processor()
            if processor:
                try:
                    result = await processor.process_connector_event(
                        connector_id, event_type, event_data, timestamp, metadata
                    )
                    
                    if result.accepted:
                        logger.info(f"🚀 优化处理成功: {connector_id}/{event_type}, 价值={result.value_score:.3f}, 耗时={result.processing_time_ms:.1f}ms")
                        return True
                    else:
                        logger.debug(f"🗑️  优化过滤拒绝: {connector_id}/{event_type}, 原因={result.reasoning}")
                        return True  # 拒绝也是成功的处理结果
                        
                except Exception as e:
                    logger.warning(f"智能处理失败，回退到传统方式: {e}")
                    # 继续执行传统处理方式
            else:
                logger.debug("智能处理器不可用，使用传统方式")

            # 回退到传统处理方式
            return await self._store_generic_event_traditional(
                connector_id, event_type, event_data, timestamp, metadata
            )

        except Exception as e:
            logger.error(f"Failed to store generic event: {str(e)}")
            return False

    async def _store_generic_event_traditional(
        self,
        connector_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        timestamp: str,
        metadata: Optional[Dict[str, Any]],
    ) -> bool:
        """
        传统事件存储方式（回退机制）
        """
        try:
            if self.db_service is None:
                logger.error("Database service is not available")
                return False

            # 生成通用实体ID（不依赖事件内容）
            entity_id = f"{connector_id}_{hash(str(event_data) + str(timestamp)) % 1000000}"

            # 尝试进行传统内容分析
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
                "processing_mode": "traditional",  # 标记处理模式
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
                    message=f"Event processed (traditional): {event_type}",
                    details={
                        "event_type": event_type,
                        "event_size": len(str(event_data)),
                        "metadata_keys": list((metadata or {}).keys()),
                        "timestamp": timestamp,
                        "processing_mode": "traditional",
                    },
                )
                session.add(log_entry)

                session.commit()

            logger.info(f"✅ Stored generic event (traditional) from {connector_id}: {event_type}")
            return True

        except Exception as e:
            logger.error(f"Failed to store generic event (traditional): {str(e)}")
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
            from core.service_facade import get_content_analysis_service

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
    
    async def _handle_fast_index_event(self, event_data: Dict[str, Any]) -> bool:
        """
        处理快速索引事件
        
        Args:
            event_data: 快速索引事件数据
            
        Returns:
            bool: 处理是否成功
        """
        try:
            if self.fast_index_service is None:
                logger.warning("快速索引服务不可用，跳过快速索引处理")
                return False
            
            # 提取快速索引所需的字段
            required_fields = ['path', 'name']
            if not all(field in event_data for field in required_fields):
                logger.warning(f"快速索引事件缺少必需字段: {required_fields}")
                return False
            
            # 构建快速索引条目
            index_entry = {
                'path': event_data.get('path'),
                'name': event_data.get('name'),
                'size': event_data.get('size', 0),
                'is_directory': event_data.get('is_directory', False),
                'extension': event_data.get('extension', ''),
                'last_modified': event_data.get('last_modified'),
                'priority': event_data.get('priority', 2)
            }
            
            # 批量存储（这里是单个条目，但使用批量接口以保持一致性）
            success = await self.fast_index_service.store_fast_index_batch([index_entry])
            
            if success:
                logger.debug(f"✅ 快速索引条目已存储: {event_data.get('path')}")
            else:
                logger.warning(f"❌ 快速索引条目存储失败: {event_data.get('path')}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 处理快速索引事件失败: {e}")
            return False
    
    def search_fast_index(
        self,
        query: str,
        limit: int = 100,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        快速索引搜索接口
        
        Args:
            query: 搜索查询
            limit: 结果限制
            **kwargs: 其他搜索参数
            
        Returns:
            搜索结果列表
        """
        try:
            if self.fast_index_service is None:
                logger.warning("快速索引服务不可用")
                return []
            
            return self.fast_index_service.search_files(query, limit, **kwargs)
            
        except Exception as e:
            logger.error(f"❌ 快速索引搜索失败: {e}")
            return []
    
    def get_fast_index_stats(self) -> Dict[str, Any]:
        """获取快速索引统计信息"""
        try:
            if self.fast_index_service is None:
                return {}
            
            return self.fast_index_service.get_stats()
            
        except Exception as e:
            logger.error(f"❌ 获取快速索引统计失败: {e}")
            return {}

    # === 智能搜索接口 ===

    async def search_intelligent_content(
        self,
        query: str,
        k: int = 10,
        min_value_score: float = 0.0,
        content_types: Optional[List[str]] = None,
        connector_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        智能内容搜索接口
        
        Args:
            query: 搜索查询
            k: 返回结果数量
            min_value_score: 最小价值评分
            content_types: 内容类型过滤
            connector_ids: 连接器ID过滤
            
        Returns:
            搜索结果列表
        """
        try:
            processor = await self._ensure_intelligent_processor()
            if processor:
                results = await processor.search_intelligent_content(
                    query=query,
                    k=k,
                    min_value_score=min_value_score,
                    content_types=content_types,
                    connector_ids=connector_ids,
                )
                
                # 转换为字典格式
                search_results = []
                for result in results:
                    search_results.append({
                        "id": result.id,
                        "summary": result.summary,
                        "score": result.score,
                        "value_score": result.value_score,
                        "content_type": result.content_type,
                        "timestamp": result.timestamp.isoformat() if result.timestamp else None,
                        "metadata": result.metadata,
                        "entity_id": result.entity_id,
                    })
                
                logger.info(f"智能搜索完成: {len(search_results)} 结果")
                return search_results
            else:
                logger.warning("智能处理器不可用，无法执行智能搜索")
                return []
                
        except Exception as e:
            logger.error(f"智能搜索失败: {e}")
            return []

    async def get_content_statistics(self) -> Dict[str, Any]:
        """
        获取内容统计信息
        
        Returns:
            统计信息字典
        """
        try:
            processor = await self._ensure_intelligent_processor()
            if processor:
                return await processor.get_content_statistics()
            else:
                return {"error": "智能处理器不可用"}
                
        except Exception as e:
            logger.error(f"获取内容统计失败: {e}")
            return {"error": str(e)}

    async def get_high_value_content(
        self,
        min_score: float = 0.8,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        获取高价值内容
        
        Args:
            min_score: 最小价值评分
            limit: 结果数量限制
            
        Returns:
            高价值内容列表
        """
        try:
            processor = await self._ensure_intelligent_processor()
            if processor:
                return await processor.get_content_by_value_range(
                    min_score=min_score,
                    max_score=1.0,
                    limit=limit
                )
            else:
                return []
                
        except Exception as e:
            logger.error(f"获取高价值内容失败: {e}")
            return []

    async def cleanup_low_value_content(self, min_age_days: int = 30) -> int:
        """
        清理低价值内容
        
        Args:
            min_age_days: 最小年龄（天）
            
        Returns:
            清理的内容数量
        """
        try:
            processor = await self._ensure_intelligent_processor()
            if processor:
                cleaned_count = await processor.cleanup_low_value_content(min_age_days)
                logger.info(f"清理低价值内容: {cleaned_count} 项")
                return cleaned_count
            else:
                return 0
                
        except Exception as e:
            logger.error(f"清理低价值内容失败: {e}")
            return 0

    async def get_processing_metrics(self) -> Dict[str, Any]:
        """
        获取处理性能指标
        
        Returns:
            性能指标字典
        """
        try:
            processor = await self._ensure_intelligent_processor()
            if processor:
                metrics = await processor.get_metrics()
                return {
                    "total_events": metrics.total_events,
                    "accepted_events": metrics.accepted_events,
                    "rejected_events": metrics.rejected_events,
                    "acceptance_rate": metrics.acceptance_rate,
                    "avg_processing_time_ms": metrics.avg_processing_time_ms,
                    "avg_value_score": metrics.avg_value_score,
                    "entities_extracted": metrics.entities_extracted,
                    "storage_efficiency": metrics.storage_efficiency,
                    "last_updated": metrics.last_updated.isoformat(),
                }
            else:
                return {"error": "智能处理器不可用"}
                
        except Exception as e:
            logger.error(f"获取处理指标失败: {e}")
            return {"error": str(e)}


# 单例模式
_generic_storage = None


def get_generic_event_storage() -> GenericEventStorage:
    """获取通用事件存储实例"""
    global _generic_storage
    if _generic_storage is None:
        _generic_storage = GenericEventStorage()
    return _generic_storage
