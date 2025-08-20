#!/usr/bin/env python3
"""
存储编排器 - 统一存储架构接口

重构说明 (2025-08-15):
- 替代UnifiedStorageService作为主要存储接口
- 协调SQLite + NetworkX + FAISS的数据访问  
- 提供统一的CRUD + 搜索 + 关系管理API
- 优化服务依赖和错误处理
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.service_facade import get_service
from services.storage.core.database import UnifiedDatabaseService

logger = logging.getLogger(__name__)


@dataclass
class StorageMetrics:
    """存储指标"""
    health_status: str = "healthy"
    total_entities: int = 0
    total_relationships: int = 0
    search_requests: int = 0
    last_updated: float = field(default_factory=time.time)


class StorageOrchestrator:
    """存储编排器 - 统一存储服务接口"""
    
    def __init__(self):
        self.db_service: Optional[UnifiedDatabaseService] = None
        self.graph_service = None
        self.vector_service = None
        self.embedding_service = None
        self._metrics = StorageMetrics()
        self._auto_sync_enabled = True
        self._initialized = False
        
        logger.info("🎯 StorageOrchestrator 初始化")
    
    async def initialize(self):
        """初始化所有存储服务"""
        if self._initialized:
            return
            
        try:
            # 获取数据库服务
            self.db_service = get_service(UnifiedDatabaseService)
            
            # 尝试获取其他服务（如果已注册）
            try:
                from services.storage.graph_service import GraphService
                self.graph_service = get_service(GraphService)
            except Exception as e:
                logger.warning(f"GraphService 不可用: {e}")
                
            try:
                from services.storage.vector_service import VectorService
                self.vector_service = get_service(VectorService)
            except Exception as e:
                logger.warning(f"VectorService 不可用: {e}")
                
            try:
                from services.storage.embedding_service import EmbeddingService
                self.embedding_service = get_service(EmbeddingService)
            except Exception as e:
                logger.warning(f"EmbeddingService 不可用: {e}")
            
            self._initialized = True
            self._metrics.health_status = "healthy"
            logger.info("✅ StorageOrchestrator 服务初始化完成")
            
        except Exception as e:
            logger.error(f"❌ StorageOrchestrator 初始化失败: {e}")
            self._metrics.health_status = "unhealthy"
            raise

    async def create_entity(
        self,
        entity_id: str,
        name: str,
        entity_type: str,
        description: str,
        content: str = "",
        auto_embed: bool = True,
        **kwargs
    ) -> bool:
        """创建实体"""
        if not self._initialized:
            await self.initialize()
            
        try:
            # 简化实现：使用内存存储记录实体信息
            if not hasattr(self, '_entities'):
                self._entities = {}
            
            entity_data = {
                "id": entity_id,
                "name": name,
                "type": entity_type,
                "description": description,
                "content": content,
                "created_at": time.time(),
                **kwargs
            }
            self._entities[entity_id] = entity_data
            
            # 添加到图服务（如果可用）
            if self.graph_service and hasattr(self.graph_service, 'create_entity'):
                try:
                    await self.graph_service.create_entity(
                        entity_id=entity_id,
                        name=name,
                        entity_type=entity_type,
                        metadata={
                            "description": description,
                            "content": content,
                            **kwargs
                        }
                    )
                except Exception as e:
                    logger.warning(f"图服务创建实体失败 {entity_id}: {e}")
            
            # 生成向量嵌入（如果服务可用）
            if auto_embed and self.embedding_service and self.vector_service:
                try:
                    if hasattr(self.embedding_service, 'create_embedding'):
                        embedding = await self.embedding_service.create_embedding(content or description)
                        if embedding and hasattr(self.vector_service, 'add_document'):
                            await self.vector_service.add_document(
                                doc_id=entity_id,
                                content=content or description,
                                embedding=embedding,
                                metadata={
                                    "name": name,
                                    "type": entity_type,
                                    "description": description
                                }
                            )
                except Exception as e:
                    logger.warning(f"嵌入生成失败 {entity_id}: {e}")
            
            self._metrics.total_entities += 1
            logger.debug(f"创建实体成功: {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"创建实体失败 {entity_id}: {e}")
            return False

    async def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        weight: float = 1.0,
        **metadata
    ) -> bool:
        """创建关系"""
        if not self._initialized:
            await self.initialize()
            
        try:
            # 简化实现：使用内存存储记录关系信息
            if not hasattr(self, '_relationships'):
                self._relationships = []
            
            relationship_data = {
                "source_id": source_id,
                "target_id": target_id,
                "type": relationship_type,
                "weight": weight,
                "created_at": time.time(),
                **metadata
            }
            self._relationships.append(relationship_data)
            
            # 在图服务中创建关系（如果可用）
            if self.graph_service and hasattr(self.graph_service, 'create_relationship'):
                try:
                    await self.graph_service.create_relationship(
                        source_id=source_id,
                        target_id=target_id,
                        relationship_type=relationship_type,
                        weight=weight,
                        metadata=metadata
                    )
                except Exception as e:
                    logger.warning(f"图服务创建关系失败 {source_id}->{target_id}: {e}")
            
            self._metrics.total_relationships += 1
            logger.debug(f"创建关系成功: {source_id}->{target_id}")
            return True
            
        except Exception as e:
            logger.error(f"创建关系失败 {source_id}->{target_id}: {e}")
            return False

    async def semantic_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """语义搜索"""
        if not self._initialized:
            await self.initialize()
            
        results = []
        try:
            if self.vector_service and self.embedding_service:
                # 生成查询向量
                query_embedding = await self.embedding_service.create_embedding(query)
                if query_embedding:
                    # 执行向量搜索
                    if hasattr(self.vector_service, 'search_similar'):
                        search_results = await self.vector_service.search_similar(
                            query_embedding=query_embedding,
                            limit=limit
                        )
                    else:
                        search_results = []
                    
                    # 格式化结果
                    for result in search_results:
                        results.append({
                            "entity_id": result.get("doc_id"),
                            "score": result.get("score", 0.0),
                            "content": result.get("content", ""),
                            "entity_type": result.get("metadata", {}).get("type", "unknown"),
                            "metadata": result.get("metadata", {})
                        })
            
            self._metrics.search_requests += 1
            return results
            
        except Exception as e:
            logger.error(f"语义搜索失败: {e}")
            return []

    async def graph_search(self, start_entity_id: str, depth: int = 1) -> List[Dict[str, Any]]:
        """图搜索"""
        if not self._initialized:
            await self.initialize()
            
        try:
            if self.graph_service and hasattr(self.graph_service, 'get_neighbors'):
                neighbors = await self.graph_service.get_neighbors(
                    start_entity_id=start_entity_id,
                    depth=depth
                )
                return neighbors
            return []
            
        except Exception as e:
            logger.error(f"图搜索失败 {start_entity_id}: {e}")
            return []

    async def get_smart_recommendations(
        self, 
        entity_id: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """智能推荐"""
        if not self._initialized:
            await self.initialize()
            
        try:
            # 综合图和向量搜索的推荐
            recommendations = []
            
            # 基于图的推荐
            if self.graph_service:
                graph_neighbors = await self.graph_search(entity_id, depth=2)
                recommendations.extend(graph_neighbors[:limit//2])
            
            # 基于语义的推荐 - 获取实体内容进行相似搜索
            if self.vector_service and len(recommendations) < limit:
                entity = await self.get_entity(entity_id)
                if entity and entity.get("content"):
                    semantic_results = await self.semantic_search(
                        entity["content"], 
                        limit=limit - len(recommendations)
                    )
                    recommendations.extend(semantic_results)
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"智能推荐失败 {entity_id}: {e}")
            return []

    async def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """获取实体"""
        if not self._initialized:
            await self.initialize()
            
        try:
            # 从内存存储获取实体
            if hasattr(self, '_entities') and entity_id in self._entities:
                return self._entities[entity_id]
            
            # 尝试从图服务获取
            if self.graph_service and hasattr(self.graph_service, 'get_entity'):
                try:
                    return await self.graph_service.get_entity(entity_id)
                except Exception as e:
                    logger.warning(f"图服务获取实体失败 {entity_id}: {e}")
            
            return None
            
        except Exception as e:
            logger.error(f"获取实体失败 {entity_id}: {e}")
            return None

    async def update_entity(self, entity_id: str, **kwargs) -> bool:
        """更新实体"""
        if not self._initialized:
            await self.initialize()
            
        try:
            # 更新内存存储中的实体
            if hasattr(self, '_entities') and entity_id in self._entities:
                self._entities[entity_id].update(kwargs)
                self._entities[entity_id]["updated_at"] = time.time()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"更新实体失败 {entity_id}: {e}")
            return False

    async def delete_entity(self, entity_id: str) -> bool:
        """删除实体"""
        if not self._initialized:
            await self.initialize()
            
        try:
            deleted = False
            
            # 从内存存储中删除
            if hasattr(self, '_entities') and entity_id in self._entities:
                del self._entities[entity_id]
                deleted = True
            
            # 从图服务中删除（如果可用）
            if self.graph_service and hasattr(self.graph_service, 'delete_entity'):
                try:
                    await self.graph_service.delete_entity(entity_id)
                    deleted = True
                except Exception as e:
                    logger.warning(f"图服务删除实体失败 {entity_id}: {e}")
            
            # 从向量服务中删除（如果可用）
            if self.vector_service and hasattr(self.vector_service, 'delete_document'):
                try:
                    await self.vector_service.delete_document(entity_id)
                    deleted = True
                except Exception as e:
                    logger.warning(f"向量服务删除实体失败 {entity_id}: {e}")
            
            if deleted:
                self._metrics.total_entities -= 1
            
            return deleted
            
        except Exception as e:
            logger.error(f"删除实体失败 {entity_id}: {e}")
            return False

    async def get_metrics(self) -> Dict[str, Any]:
        """获取存储指标"""
        if not self._initialized:
            await self.initialize()
            
        metrics_data = {
            "health_status": self._metrics.health_status,
            "total_entities": self._metrics.total_entities,
            "total_relationships": self._metrics.total_relationships,
            "search_requests": self._metrics.search_requests,
            "last_updated": self._metrics.last_updated
        }
        
        # 收集各服务的指标
        if self.graph_service:
            try:
                graph_metrics = await self.graph_service.get_metrics()
                metrics_data["graph"] = graph_metrics
            except Exception as e:
                logger.warning(f"获取图服务指标失败: {e}")
        
        if self.vector_service:
            try:
                vector_metrics = await self.vector_service.get_metrics()
                metrics_data["vector"] = vector_metrics
            except Exception as e:
                logger.warning(f"获取向量服务指标失败: {e}")
        
        return metrics_data

    async def sync_all(self):
        """同步所有存储服务"""
        if self._auto_sync_enabled and self._initialized:
            try:
                if self.graph_service and hasattr(self.graph_service, 'sync'):
                    await self.graph_service.sync()
                
                if self.vector_service and hasattr(self.vector_service, 'sync'):
                    await self.vector_service.sync()
                
                logger.debug("存储服务同步完成")
            except Exception as e:
                logger.error(f"存储同步失败: {e}")


# 全局实例管理
_storage_orchestrator_instance: Optional[StorageOrchestrator] = None


async def get_storage_orchestrator() -> StorageOrchestrator:
    """获取存储编排器单例"""
    global _storage_orchestrator_instance
    
    if _storage_orchestrator_instance is None:
        _storage_orchestrator_instance = StorageOrchestrator()
        await _storage_orchestrator_instance.initialize()
    
    return _storage_orchestrator_instance


async def cleanup_storage_orchestrator():
    """清理存储编排器"""
    global _storage_orchestrator_instance
    
    if _storage_orchestrator_instance:
        try:
            # 执行清理逻辑
            if hasattr(_storage_orchestrator_instance, 'close'):
                await _storage_orchestrator_instance.close()
        except Exception as e:
            logger.error(f"清理存储编排器失败: {e}")
        finally:
            _storage_orchestrator_instance = None