#!/usr/bin/env python3
"""
智能事件处理器 - AI驱动的事件处理流水线
替代GenericEventStorage，实现基于Ollama AI的智能内容过滤和存储
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from core.error_handling import handle_errors, ErrorSeverity, ErrorCategory
from core.service_facade import get_service
from services.ai.ollama_service import get_ollama_service, ContentEvaluation
from services.storage.faiss_vector_store import (
    get_faiss_vector_store, 
    VectorDocument,
    SearchResult
)
from services.unified_database_service import UnifiedDatabaseService
from models.database_models import EntityMetadata, ConnectorLog

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """事件处理结果"""
    accepted: bool
    value_score: float
    summary: str
    reasoning: str
    entities_created: int = 0
    vector_stored: bool = False
    database_stored: bool = False
    processing_time_ms: float = 0.0


@dataclass
class ProcessingMetrics:
    """处理性能指标"""
    total_events: int
    accepted_events: int
    rejected_events: int
    avg_processing_time_ms: float
    avg_value_score: float
    acceptance_rate: float
    entities_extracted: int
    storage_efficiency: float
    last_updated: datetime


class IntelligentEventProcessor:
    """AI驱动的智能事件处理器 - 核心组件"""

    def __init__(
        self,
        value_threshold: float = 0.3,
        entity_threshold: float = 0.8,
        max_content_length: int = 10000,
        enable_vector_storage: bool = True,
        enable_entity_extraction: bool = True,
    ):
        self.value_threshold = value_threshold
        self.entity_threshold = entity_threshold
        self.max_content_length = max_content_length
        self.enable_vector_storage = enable_vector_storage
        self.enable_entity_extraction = enable_entity_extraction
        
        # 服务依赖 - 懒加载
        self._ollama_service = None
        self._vector_store = None
        self._db_service = None
        
        # 性能监控
        self._processing_times: List[float] = []
        self._value_scores: List[float] = []
        self._max_history = 100
        
        self._metrics = ProcessingMetrics(
            total_events=0,
            accepted_events=0,
            rejected_events=0,
            avg_processing_time_ms=0.0,
            avg_value_score=0.0,
            acceptance_rate=0.0,
            entities_extracted=0,
            storage_efficiency=0.0,
            last_updated=datetime.utcnow(),
        )

    async def initialize(self) -> bool:
        """初始化智能事件处理器"""
        try:
            # 初始化Ollama服务
            self._ollama_service = await get_ollama_service()
            
            if self.enable_vector_storage:
                try:
                    self._vector_store = await get_faiss_vector_store()
                except Exception as e:
                    logger.warning(f"向量存储初始化失败，禁用向量存储功能: {e}")
                    self.enable_vector_storage = False
                    self._vector_store = None
            
            # 数据库服务
            self._db_service = get_service(UnifiedDatabaseService)
            
            logger.info(f"智能事件处理器初始化完成 - 阈值: {self.value_threshold}, 合并AI调用模式")
            return True
            
        except Exception as e:
            logger.error(f"智能事件处理器初始化失败: {e}")
            return False

    # === 核心处理流水线 ===

    @handle_errors(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.EVENT_PROCESSING,
        user_message="智能事件处理失败",
        recovery_suggestions="检查AI服务状态"
    )
    async def process_connector_event(
        self,
        connector_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        timestamp: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ProcessingResult:
        """
        智能处理连接器事件 - 严格按照设计流水线
        
        流程：
        1. 内容提取和预处理
        2. AI价值评估 (必须)
        3. 过滤决策 (score < 0.3 则丢弃)
        4. 语义摘要生成 (必须)
        5. 向量化存储 (必须)
        6. 实体提取 (条件：score > 0.8)
        7. 数据库存储
        """
        start_time = datetime.utcnow()
        
        try:
            # 1. 内容提取和预处理
            content = self._extract_content_from_event(event_data)
            if not content:
                logger.debug(f"事件无有效内容，跳过处理: {connector_id}/{event_type}")
                return ProcessingResult(
                    accepted=False,
                    value_score=0.0,
                    summary="",
                    reasoning="无有效内容"
                )
            
            # 内容长度限制
            if len(content) > self.max_content_length:
                content = content[:self.max_content_length] + "..."
                logger.debug(f"内容截断到 {self.max_content_length} 字符")
            
            # 2. 合并AI调用 - 一次性完成评估和摘要
            evaluation = await self._process_content_merged(content)
            
            # 3. 过滤决策
            if evaluation.value_score < self.value_threshold:
                logger.debug(f"内容价值不足，丢弃: {evaluation.value_score:.3f} < {self.value_threshold}")
                self._record_rejection(evaluation.value_score)
                return ProcessingResult(
                    accepted=False,
                    value_score=evaluation.value_score,
                    summary=evaluation.summary,
                    reasoning=f"价值评分过低: {evaluation.value_score:.3f}"
                )
            
            # 4. 构建向量文档
            doc_id = f"{connector_id}_{hash(content + timestamp) % 1000000}"
            
            vector_doc = None
            if self.enable_vector_storage and self._vector_store is not None:
                # 4. 向量化存储（单独调用）
                embedding = await self._ollama_service.embed_text(evaluation.summary)
                
                vector_doc = VectorDocument(
                    id=doc_id,
                    summary=evaluation.summary,
                    embedding=np.array(embedding, dtype=np.float32),
                    metadata={
                        "connector_id": connector_id,
                        "event_type": event_type,
                        "timestamp": timestamp,
                        "content_type": evaluation.content_type,
                        "keywords": evaluation.keywords,
                        "original_metadata": metadata or {},
                    },
                    entity_id=None,
                    timestamp=datetime.fromisoformat(timestamp) if timestamp else datetime.utcnow(),
                    content_type=evaluation.content_type,
                    value_score=evaluation.value_score,
                )
                
                # 存储到向量数据库
                vector_stored = await self._vector_store.add_document(vector_doc)
            else:
                vector_stored = False
            
            # 5. 实体提取（高价值内容）
            entities_created = 0
            if (self.enable_entity_extraction and 
                evaluation.value_score > self.entity_threshold and 
                evaluation.entities):
                entities_created = await self._create_valuable_entities(
                    evaluation.entities, doc_id, connector_id, metadata or {}
                )
            
            # 6. 数据库存储（元数据）
            database_stored = await self._store_event_metadata(
                doc_id, connector_id, event_type, evaluation, timestamp, metadata
            )
            
            # 记录成功处理
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._record_success(evaluation.value_score, processing_time)
            
            logger.info(f"✅ 合并AI调用完成: {doc_id}, 价值={evaluation.value_score:.3f}, 耗时={processing_time:.1f}ms, 实体={entities_created}")
            
            return ProcessingResult(
                accepted=True,
                value_score=evaluation.value_score,
                summary=evaluation.summary,
                reasoning=f"合并AI调用处理: {evaluation.value_score:.3f}",
                entities_created=entities_created,
                vector_stored=vector_stored,
                database_stored=database_stored,
                processing_time_ms=processing_time,
            )
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.error(f"智能事件处理失败: {e}")
            
            return ProcessingResult(
                accepted=False,
                value_score=0.0,
                summary="",
                reasoning=f"处理异常: {str(e)}"
            )

    # === 内容提取和预处理 ===

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
            value = list(event_data.values())[0]
            if isinstance(value, str) and value.strip():
                return value.strip()
        
        return None

    # === 合并AI调用优化 ===

    async def _process_content_merged(self, content: str) -> ContentEvaluation:
        """
        合并AI调用 - 一次性完成价值评估和语义摘要
        根据Gemini建议优化：将两个AI任务合并为一次调用
        """
        try:
            # 构建合并的prompt - 要求JSON格式输出
            merged_prompt = f"""分析以下内容，以JSON格式返回结果，包含两个字段：

内容：
\"\"\"
{content[:2000]}
\"\"\"

请返回JSON格式：
{{
    "value_score": <0-1之间的数字，表示内容重要性>,
    "summary": "<100字以内的简洁摘要>"
}}

评分标准：
- 0.0-0.2: 垃圾内容（广告、乱码、重复文本）
- 0.3-0.5: 低价值内容（临时信息、简单复制）
- 0.6-0.8: 有价值内容（有用信息、学习资料）
- 0.9-1.0: 高价值内容（重要文档、创作内容）

只返回JSON，不要其他文字："""

            # 调用LLM
            response = await self._ollama_service._call_llm(content, merged_prompt)
            
            # 解析JSON响应
            evaluation_data = self._parse_merged_response(response)
            
            # 构建ContentEvaluation对象
            return ContentEvaluation(
                value_score=evaluation_data.get("value_score", 0.0),
                confidence=0.8,  # 合并调用的置信度
                content_type="text",
                summary=evaluation_data.get("summary", content[:100]),
                keywords=[],  # 简化版本暂不提取关键词
                entities=[],  # 简化版本暂不提取实体
                reasoning=f"合并AI调用: score={evaluation_data.get('value_score', 0.0):.3f}"
            )
            
        except Exception as e:
            logger.error(f"合并AI调用失败: {e}")
            # 返回安全的默认值
            return ContentEvaluation(
                value_score=0.0,
                confidence=0.0,
                content_type="text",
                summary=content[:100],
                keywords=[],
                entities=[],
                reasoning=f"合并调用失败: {str(e)}"
            )

    def _parse_merged_response(self, response: str) -> dict:
        """解析合并AI调用的JSON响应"""
        try:
            import json
            import re
            
            # 尝试直接解析JSON
            try:
                return json.loads(response.strip())
            except json.JSONDecodeError:
                pass
            
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*?\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # 尝试提取数字和文本
            score_match = re.search(r'"?value_score"?\s*:\s*([0-9.]+)', response)
            summary_match = re.search(r'"?summary"?\s*:\s*"([^"]*)"', response)
            
            value_score = float(score_match.group(1)) if score_match else 0.0
            summary = summary_match.group(1) if summary_match else ""
            
            return {
                "value_score": max(0.0, min(1.0, value_score)),
                "summary": summary[:100] if summary else "解析失败"
            }
            
        except Exception as e:
            logger.error(f"解析AI响应失败: {e}")
            return {"value_score": 0.0, "summary": "解析失败"}

    # === 实体创建 ===

    async def _create_valuable_entities(
        self,
        entities: List[Dict[str, Any]],
        source_doc_id: str,
        connector_id: str,
        metadata: Dict[str, Any],
    ) -> int:
        """创建高价值实体"""
        try:
            created_count = 0
            
            for entity_data in entities:
                entity_id = f"entity_{hash(entity_data.get('name', '') + source_doc_id) % 1000000}"
                
                entity_properties = {
                    "source_document": source_doc_id,
                    "connector_id": connector_id,
                    "entity_type": entity_data.get("type", "unknown"),
                    "entity_name": entity_data.get("name", ""),
                    "context": entity_data.get("context", ""),
                    "extraction_confidence": 0.9,  # 高价值实体的置信度
                    "created_by": "ai_extraction",
                    "metadata": metadata,
                }
                
                # 存储实体到数据库
                with self._db_service.get_session() as session:
                    entity_record = EntityMetadata(
                        entity_id=entity_id,
                        name=entity_data.get("name", "AI提取的实体"),
                        type="ai_extracted_entity",
                        description=f"AI从高价值内容中提取的{entity_data.get('type', '实体')}",
                        properties=entity_properties,
                        access_count=1,
                    )
                    session.add(entity_record)
                    session.commit()
                    created_count += 1
                    
                    logger.debug(f"创建AI实体: {entity_id} - {entity_data.get('name', '')}")
            
            self._metrics.entities_extracted += created_count
            return created_count
            
        except Exception as e:
            logger.error(f"创建实体失败: {e}")
            return 0

    # === 数据库存储 ===

    async def _store_event_metadata(
        self,
        doc_id: str,
        connector_id: str,
        event_type: str,
        evaluation: ContentEvaluation,
        timestamp: str,
        metadata: Optional[Dict[str, Any]],
    ) -> bool:
        """存储事件元数据到数据库"""
        try:
            event_properties = {
                "connector_id": connector_id,
                "event_type": event_type,
                "timestamp": timestamp,
                "processed_at": datetime.utcnow().isoformat(),
                "ai_evaluation": {
                    "value_score": evaluation.value_score,
                    "content_type": evaluation.content_type,
                    "keywords": evaluation.keywords,
                    "confidence": evaluation.confidence,
                    "method": "merged_ai_call",
                },
                "summary": evaluation.summary,
                "metadata": metadata or {},
            }
            
            with self._db_service.get_session() as session:
                # 检查是否已存在
                existing = session.query(EntityMetadata).filter_by(entity_id=doc_id).first()
                
                if existing:
                    # 更新现有记录
                    existing.properties = event_properties
                    existing.updated_at = datetime.utcnow()
                    existing.access_count += 1
                else:
                    # 创建新记录
                    entity_record = EntityMetadata(
                        entity_id=doc_id,
                        name=f"智能处理_{connector_id}_{datetime.now().strftime('%H%M%S')}",
                        type="intelligent_event",
                        description=f"合并AI调用处理的{event_type}事件，价值评分: {evaluation.value_score:.3f}",
                        properties=event_properties,
                        access_count=1,
                    )
                    session.add(entity_record)
                
                # 记录连接器日志
                log_entry = ConnectorLog(
                    connector_id=connector_id,
                    level="INFO",
                    message=f"合并AI调用: {event_type}",
                    details={
                        "event_type": event_type,
                        "value_score": evaluation.value_score,
                        "content_type": evaluation.content_type,
                        "summary_length": len(evaluation.summary),
                        "entities_count": len(evaluation.entities) if evaluation.entities else 0,
                        "confidence": evaluation.confidence,
                        "timestamp": timestamp,
                        "method": "merged_ai_call",
                    },
                )
                session.add(log_entry)
                
                session.commit()
                
            return True
            
        except Exception as e:
            logger.error(f"存储事件元数据失败: {e}")
            return False

    # === 搜索和查询接口 ===

    async def search_intelligent_content(
        self,
        query: str,
        k: int = 10,
        min_value_score: float = 0.0,
        content_types: Optional[List[str]] = None,
        connector_ids: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        """智能内容搜索"""
        try:
            if not self.enable_vector_storage or not self._vector_store:
                logger.warning("向量存储未启用")
                return []
            
            # 构建搜索向量
            query_embedding = await self._ollama_service.embed_text(query)
            query_vector = np.array(query_embedding, dtype=np.float32)
            
            # 构建过滤条件
            filter_metadata = {}
            if min_value_score > 0:
                filter_metadata["value_score"] = {"min": min_value_score}
            if content_types:
                filter_metadata["content_type"] = content_types
            if connector_ids:
                filter_metadata["connector_id"] = connector_ids
            
            # 执行向量搜索
            results = await self._vector_store.search_similar(
                query_vector=query_vector,
                k=k,
                search_tiers=["hot", "warm"],  # 搜索热数据和温数据
                filter_metadata=filter_metadata if filter_metadata else None,
            )
            
            logger.debug(f"智能内容搜索完成: {len(results)} 结果")
            return results
            
        except Exception as e:
            logger.error(f"智能内容搜索失败: {e}")
            return []

    async def get_content_by_value_range(
        self,
        min_score: float,
        max_score: float = 1.0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """按价值评分范围获取内容"""
        try:
            filter_metadata = {
                "value_score": {"min": min_score, "max": max_score}
            }
            
            # 使用一个通用查询向量
            dummy_query = np.zeros(384, dtype=np.float32)
            
            results = await self._vector_store.search_similar(
                query_vector=dummy_query,
                k=limit,
                filter_metadata=filter_metadata,
            )
            
            # 转换为字典格式
            content_list = []
            for result in results:
                content_list.append({
                    "id": result.id,
                    "summary": result.summary,
                    "value_score": result.value_score,
                    "content_type": result.content_type,
                    "timestamp": result.timestamp.isoformat() if result.timestamp else None,
                    "metadata": result.metadata,
                })
            
            return content_list
            
        except Exception as e:
            logger.error(f"按价值范围获取内容失败: {e}")
            return []

    # === 统计和分析 ===

    async def get_content_statistics(self) -> Dict[str, Any]:
        """获取内容统计信息"""
        try:
            stats = {
                "processing_metrics": await self.get_metrics(),
                "value_score_distribution": {},
                "content_type_distribution": {},
                "connector_distribution": {},
            }
            
            # 获取不同价值区间的内容数量
            value_ranges = [
                ("premium", 0.8, 1.0),
                ("high", 0.6, 0.8),
                ("medium", 0.3, 0.6),
                ("low", 0.0, 0.3),
            ]
            
            for label, min_score, max_score in value_ranges:
                content = await self.get_content_by_value_range(min_score, max_score, 1000)
                stats["value_score_distribution"][label] = len(content)
                
                # 统计内容类型分布
                for item in content:
                    content_type = item.get("content_type", "unknown")
                    stats["content_type_distribution"][content_type] = \
                        stats["content_type_distribution"].get(content_type, 0) + 1
                    
                    # 统计连接器分布
                    connector_id = item.get("metadata", {}).get("connector_id", "unknown")
                    stats["connector_distribution"][connector_id] = \
                        stats["connector_distribution"].get(connector_id, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"获取内容统计失败: {e}")
            return {}

    # === 性能监控 ===

    def _record_success(self, value_score: float, processing_time: float):
        """记录成功处理"""
        self._metrics.total_events += 1
        self._metrics.accepted_events += 1
        
        self._processing_times.append(processing_time)
        self._value_scores.append(value_score)
        
        # 保持历史记录限制
        if len(self._processing_times) > self._max_history:
            self._processing_times = self._processing_times[-self._max_history:]
        if len(self._value_scores) > self._max_history:
            self._value_scores = self._value_scores[-self._max_history:]

    def _record_rejection(self, value_score: float):
        """记录拒绝处理"""
        self._metrics.total_events += 1
        self._metrics.rejected_events += 1
        self._value_scores.append(value_score)

    async def get_metrics(self) -> ProcessingMetrics:
        """获取处理性能指标"""
        await self._update_metrics()
        return self._metrics

    async def _update_metrics(self):
        """更新性能指标"""
        try:
            if self._processing_times:
                self._metrics.avg_processing_time_ms = np.mean(self._processing_times)
            
            if self._value_scores:
                self._metrics.avg_value_score = np.mean(self._value_scores)
            
            if self._metrics.total_events > 0:
                self._metrics.acceptance_rate = self._metrics.accepted_events / self._metrics.total_events
                
                # 计算存储效率 (压缩比)
                if self.enable_vector_storage and self._vector_store:
                    vector_metrics = await self._vector_store.get_metrics()
                    self._metrics.storage_efficiency = vector_metrics.compression_ratio
            
            self._metrics.last_updated = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"更新指标失败: {e}")

    # === 维护和清理 ===

    async def cleanup_low_value_content(self, min_age_days: int = 30) -> int:
        """清理低价值内容"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=min_age_days)
            
            # 获取低价值内容
            low_value_content = await self.get_content_by_value_range(0.0, self.value_threshold, 10000)
            
            cleanup_count = 0
            for item in low_value_content:
                if item.get("timestamp"):
                    item_date = datetime.fromisoformat(item["timestamp"])
                    if item_date < cutoff_date:
                        # 从数据库删除
                        with self._db_service.get_session() as session:
                            existing = session.query(EntityMetadata).filter_by(
                                entity_id=item["id"]
                            ).first()
                            if existing:
                                session.delete(existing)
                                session.commit()
                                cleanup_count += 1
            
            logger.info(f"清理低价值内容: {cleanup_count} 项")
            return cleanup_count
            
        except Exception as e:
            logger.error(f"清理低价值内容失败: {e}")
            return 0
    
    async def cleanup(self):
        """清理处理器资源"""
        try:
            # 输出最终统计
            metrics = await self.get_metrics()
            logger.info(f"智能处理器统计 - 总计: {metrics.total_events}, 接受: {metrics.accepted_events}, 接受率: {metrics.acceptance_rate:.2%}")
            
            # 清理ollama服务
            if hasattr(self, '_ollama_service') and self._ollama_service:
                await self._ollama_service.close()
                
            logger.info("智能事件处理器已清理")
            
        except Exception as e:
            logger.error(f"清理智能事件处理器失败: {e}")


# === 服务单例管理 ===

_intelligent_processor: Optional[IntelligentEventProcessor] = None

async def get_intelligent_event_processor() -> IntelligentEventProcessor:
    """获取智能事件处理器实例（单例模式）"""
    global _intelligent_processor
    if _intelligent_processor is None:
        _intelligent_processor = IntelligentEventProcessor()
        if not await _intelligent_processor.initialize():
            raise RuntimeError("智能事件处理器初始化失败")
    return _intelligent_processor

async def cleanup_intelligent_event_processor():
    """清理智能事件处理器"""
    global _intelligent_processor
    if _intelligent_processor:
        # 保存最终指标
        try:
            metrics = await _intelligent_processor.get_metrics()
            logger.info(f"智能处理器统计 - 总计: {metrics.total_events}, 接受: {metrics.accepted_events}, 接受率: {metrics.acceptance_rate:.2%}")
        except:
            pass
        
        _intelligent_processor = None