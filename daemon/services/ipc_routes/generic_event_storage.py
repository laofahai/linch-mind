"""
通用事件存储接口 - 真正的连接器无关架构

重构说明 (2025-08-16):
- 移除了FastIndexStorageService的文件系统特定逻辑
- 使用UniversalIndexService支持所有连接器类型的快速搜索
- 保持Everything级别搜索性能，但扩展到任意连接器
- 集成智能AI处理和语义理解功能
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.service_facade import get_service
from models.database_models import ConnectorLog, EntityMetadata
from services.unified_database_service import UnifiedDatabaseService
from services.storage.universal_index_service import get_universal_index_service
from services.storage.intelligent_event_processor import get_intelligent_event_processor

logger = logging.getLogger(__name__)


class GenericEventStorage:
    """
    通用事件存储 - 真正的连接器无关架构

    核心功能：
    1. 通用索引：支持所有连接器的快速搜索 (文件、URL、邮箱等)
    2. AI处理：智能内容分析和语义理解
    3. 传统存储：兜底的数据持久化机制
    
    所有连接器使用完全相同的接口，无任何特定逻辑
    """

    def __init__(self):
        self._db_service = None
        self._universal_index_service = None
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
    def universal_index_service(self):
        """懒加载通用索引服务"""
        if self._universal_index_service is None:
            try:
                self._universal_index_service = get_universal_index_service()
            except Exception as e:
                logger.warning(f"Universal index service not available: {str(e)}")
                return None
        return self._universal_index_service
    
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
    
    def _should_use_intelligent_processing(
        self, 
        connector_id: str, 
        event_type: str, 
        event_data: Dict[str, Any]
    ) -> bool:
        """
        判断事件是否应该使用智能处理器
        
        原则：
        1. 基于事件内容特征，而非事件类型枚举
        2. 检查事件是否包含值得AI分析的文本内容
        3. 使用启发式规则，避免强耦合连接器
        """
        
        # 策略1: 检查事件数据结构特征
        if self._is_structured_metadata_event(event_data):
            # 结构化元数据事件（如文件索引）通常不需要AI分析
            return self._has_rich_text_content(event_data)
        
        # 策略2: 检查是否包含有意义的文本内容
        if self._has_meaningful_text_content(event_data):
            return True
        
        # 策略3: 基于事件类型的启发式规则
        return self._apply_heuristic_rules(connector_id, event_type, event_data)
    
    def _is_structured_metadata_event(self, event_data: Dict[str, Any]) -> bool:
        """
        检查是否为结构化元数据事件
        
        特征：
        - 包含路径、大小、时间戳等结构化字段
        - 主要用于索引和搜索，而非内容分析
        """
        # 元数据字段模式
        metadata_field_patterns = {
            "path", "size", "modified_time", "created_time", 
            "extension", "is_directory", "url", "email", 
            "phone", "contact_id", "file_id", "item_id"
        }
        
        # 安全检查：确保event_data不为None且为字典类型
        if event_data is None or not isinstance(event_data, dict):
            return False
        
        # 如果事件数据主要包含元数据字段，则认为是元数据事件
        data_fields = set(event_data.keys())
        metadata_fields = data_fields.intersection(metadata_field_patterns)
        
        # 如果元数据字段占比超过60%，认为是元数据事件
        if len(data_fields) > 0:
            metadata_ratio = len(metadata_fields) / len(data_fields)
            return metadata_ratio > 0.6
        
        return False
    
    def _apply_heuristic_rules(
        self, 
        connector_id: str, 
        event_type: str, 
        event_data: Dict[str, Any]
    ) -> bool:
        """
        应用启发式规则
        
        基于事件类型名称的语义判断，避免硬编码连接器类型
        """
        # 明确的索引相关事件类型
        index_keywords = {"indexed", "scan", "progress", "metadata", "catalog"}
        event_type_lower = event_type.lower()
        
        for keyword in index_keywords:
            if keyword in event_type_lower:
                return False  # 索引型事件，不需要AI处理
        
        # 明确的内容相关事件类型
        content_keywords = {"content", "text", "message", "document", "note"}
        
        for keyword in content_keywords:
            if keyword in event_type_lower:
                return True  # 内容型事件，需要AI处理
        
        # 默认：如果无法判断，检查是否有文本内容
        return self._has_minimal_text_content(event_data)
    
    def _has_minimal_text_content(self, event_data: Dict[str, Any]) -> bool:
        """检查是否包含最基本的文本内容（降低阈值）"""
        # 安全检查：确保event_data不为None且为字典类型
        if event_data is None or not isinstance(event_data, dict):
            return False
            
        content_fields = ["content", "text", "data", "message", "body", "value"]
        
        for field in content_fields:
            if field in event_data:
                content = event_data[field]
                if isinstance(content, str) and len(content.strip()) > 5:  # 降低阈值
                    return True
        
        return False
    
    def _has_rich_text_content(self, event_data: Dict[str, Any]) -> bool:
        """检查索引型事件是否包含丰富的文本内容值得AI分析"""
        # 安全检查：确保event_data不为None且为字典类型
        if event_data is None or not isinstance(event_data, dict):
            return False
            
        content_fields = ["content", "text", "description", "summary", "body"]
        
        for field in content_fields:
            if field in event_data:
                content = event_data[field]
                if isinstance(content, str) and len(content.strip()) > 50:  # 较高的文本长度阈值
                    return True
        return False
    
    def _has_meaningful_text_content(self, event_data: Dict[str, Any]) -> bool:
        """检查事件是否包含有意义的文本内容"""
        # 安全检查：确保event_data不为None且为字典类型
        if event_data is None or not isinstance(event_data, dict):
            return False
            
        content_fields = ["content", "text", "data", "message", "body", "value"]
        
        for field in content_fields:
            if field in event_data:
                content = event_data[field]
                if isinstance(content, str) and len(content.strip()) > 10:
                    return True
        
        # 检查单字段文本事件
        if isinstance(event_data, dict) and len(event_data) == 1:
            value = list(event_data.values())[0]
            if isinstance(value, str) and len(value.strip()) > 10:
                return True
        
        return False
    
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
            # 使用通用索引处理所有连接器事件（保持快速搜索能力）
            await self._handle_universal_index_event(
                connector_id, event_type, event_data, timestamp, metadata
            )

            # 判断是否应该进行智能处理（基于事件类型和内容）
            if self._should_use_intelligent_processing(connector_id, event_type, event_data):
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
            else:
                logger.debug(f"事件类型不适合智能处理: {connector_id}/{event_type}, 直接使用传统方式")

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

            # 🛡️ 增强的实体ID生成 - 防止空值导致的哈希冲突
            import hashlib
            
            # 确保关键字段不为空，使用默认值防止哈希冲突
            safe_connector_id = connector_id or "unknown_connector"
            safe_event_type = event_type or "unknown_event"
            safe_event_data = event_data if event_data is not None else {"empty": True}
            
            # 添加时间戳确保唯一性（对于相同内容的事件）
            content_key = f"{safe_connector_id}:{safe_event_type}:{json.dumps(safe_event_data, sort_keys=True)}:{timestamp}"
            content_hash = hashlib.sha256(content_key.encode()).hexdigest()[:16]
            entity_id = f"{safe_connector_id}_{safe_event_type}_{content_hash}"

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
                    # 发现重复事件，只更新访问计数和时间戳
                    existing.access_count += 1
                    existing.last_accessed = datetime.utcnow()
                    
                    # 检查是否需要更新时间戳（允许小范围时间差异）
                    existing_timestamp = existing.properties.get('timestamp', '')
                    if timestamp != existing_timestamp:
                        # 保留最新的时间戳
                        existing.properties['timestamp'] = timestamp
                        existing.properties['last_seen'] = datetime.utcnow().isoformat()
                        existing.updated_at = datetime.utcnow()
                    
                    logger.debug(f"Duplicate event detected, updated access count: {entity_id}")
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
                        "metadata_keys": list(metadata.keys()) if metadata is not None and isinstance(metadata, dict) else [],
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
            # 简化内容分析，避免循环导入
            content = self._extract_content_from_event(event_data)
            if not content:
                return None

            # 确定内容类型
            content_type = self._determine_content_type(event_data, event_type)

            # 基础内容分析（不依赖外部服务）
            analysis_result = {
                "content_length": len(content),
                "content_type": content_type,
                "word_count": len(content.split()) if content else 0,
                "analyzed_at": datetime.utcnow().isoformat(),
                "analysis_method": "basic_local"
            }

            logger.debug(f"基础内容分析完成: {len(content)} 字符, 类型: {content_type}")
            return analysis_result

        except Exception as e:
            logger.error(f"内容分析失败: {e}")
            return None

    def _extract_content_from_event(self, event_data: Dict[str, Any]) -> Optional[str]:
        """从事件数据中提取文本内容"""
        # 安全检查：确保event_data不为None且为字典类型
        if event_data is None or not isinstance(event_data, dict):
            return None
            
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

        # 基于事件数据推断（安全检查）
        if event_data is not None and isinstance(event_data, dict):
            content_type_field = event_data.get("content_type", event_data.get("type"))
            if content_type_field:
                return str(content_type_field)

        return "text"
    
    async def _handle_universal_index_event(
        self,
        connector_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        timestamp: str,
        metadata: Optional[Dict[str, Any]]
    ) -> bool:
        """
        处理通用索引事件 - 支持所有连接器类型
        
        Args:
            connector_id: 连接器ID
            event_type: 事件类型
            event_data: 事件数据
            timestamp: 时间戳
            metadata: 元数据
            
        Returns:
            bool: 处理是否成功
        """
        try:
            if self.universal_index_service is None:
                logger.warning("通用索引服务不可用，跳过索引处理")
                return False
            
            # 构建通用索引条目 - 安全处理None值
            index_entry = {
                'connector_id': connector_id,
                'event_type': event_type,
                'event_data': event_data if event_data is not None and isinstance(event_data, dict) else {},
                'timestamp': timestamp,
                'metadata': metadata if metadata is not None and isinstance(metadata, dict) else {}
            }
            
            # 批量存储（这里是单个条目，但使用批量接口以保持一致性）
            success = await self.universal_index_service.index_content_batch([index_entry])
            
            if success:
                logger.debug(f"✅ 通用索引条目已存储: {connector_id}/{event_type}")
            else:
                logger.warning(f"❌ 通用索引条目存储失败: {connector_id}/{event_type}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 处理通用索引事件失败: {e}")
            return False
    
    def search_universal_index(
        self,
        query: str,
        limit: int = 100,
        content_types: List[str] = None,
        connector_ids: List[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        通用索引搜索接口 - 支持所有连接器类型
        
        Args:
            query: 搜索查询
            limit: 结果限制
            content_types: 内容类型过滤 (如 ["file_path", "url"])
            connector_ids: 连接器过滤 (如 ["filesystem", "clipboard"])
            **kwargs: 其他搜索参数
            
        Returns:
            搜索结果列表
        """
        try:
            if self.universal_index_service is None:
                logger.warning("通用索引服务不可用")
                return []
            
            # 导入SearchQuery和ContentType
            from services.storage.universal_index_service import SearchQuery, ContentType
            
            # 转换内容类型
            content_type_enums = []
            if content_types:
                for ct in content_types:
                    try:
                        content_type_enums.append(ContentType(ct))
                    except ValueError:
                        logger.warning(f"未知内容类型: {ct}")
            
            # 构建搜索查询
            search_query = SearchQuery(
                text=query,
                content_types=content_type_enums,
                connector_ids=connector_ids or [],
                limit=limit,
                **kwargs
            )
            
            # 执行搜索
            search_results = self.universal_index_service.search(search_query)
            
            # 转换为字典格式
            results = []
            for result in search_results:
                results.append({
                    'id': result.entry.id,
                    'connector_id': result.entry.connector_id,
                    'content_type': result.entry.content_type.value,
                    'primary_key': result.entry.primary_key,
                    'display_name': result.entry.display_name,
                    'searchable_text': result.entry.searchable_text,
                    'score': result.score,
                    'structured_data': result.entry.structured_data,
                    'metadata': result.entry.metadata,
                    'last_modified': result.entry.last_modified.isoformat() if result.entry.last_modified else None
                })
            
            return results
            
        except Exception as e:
            logger.error(f"❌ 通用索引搜索失败: {e}")
            return []
    
    def get_universal_index_stats(self) -> Dict[str, Any]:
        """获取通用索引统计信息"""
        try:
            if self.universal_index_service is None:
                return {}
            
            return self.universal_index_service.get_stats()
            
        except Exception as e:
            logger.error(f"❌ 获取通用索引统计失败: {e}")
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
