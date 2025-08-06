#!/usr/bin/env python3
"""
存储API路由 - 三层存储架构的HTTP接口
提供实体管理、智能搜索、推荐和数据迁移功能
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from services.storage.data_migration import DataMigrationService, get_migration_service
from services.storage.storage_orchestrator import (StorageOrchestrator,
                                                   get_storage_orchestrator)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/storage", tags=["storage"])


# === Pydantic模型 ===


class EntityCreateRequest(BaseModel):
    """创建实体请求"""

    entity_id: str = Field(..., description="实体ID", min_length=1, max_length=255)
    name: str = Field(..., description="实体名称", min_length=1, max_length=255)
    entity_type: str = Field(..., description="实体类型", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="实体描述", max_length=2000)
    attributes: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="实体属性"
    )
    source_path: Optional[str] = Field(None, description="源文件路径", max_length=500)
    content: Optional[str] = Field(None, description="实体内容", max_length=10000)
    auto_embed: bool = Field(True, description="是否自动生成向量嵌入")


class EntityUpdateRequest(BaseModel):
    """更新实体请求"""

    name: Optional[str] = Field(
        None, description="实体名称", min_length=1, max_length=255
    )
    description: Optional[str] = Field(None, description="实体描述", max_length=2000)
    attributes: Optional[Dict[str, Any]] = Field(None, description="实体属性")


class RelationshipCreateRequest(BaseModel):
    """创建关系请求"""

    source_entity: str = Field(
        ..., description="源实体ID", min_length=1, max_length=255
    )
    target_entity: str = Field(
        ..., description="目标实体ID", min_length=1, max_length=255
    )
    relationship_type: str = Field(
        ..., description="关系类型", min_length=1, max_length=100
    )
    strength: float = Field(1.0, description="关系强度", ge=0.0, le=1.0)
    confidence: float = Field(1.0, description="关系置信度", ge=0.0, le=1.0)
    attributes: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="关系属性"
    )


class SemanticSearchRequest(BaseModel):
    """语义搜索请求"""

    query: str = Field(..., description="搜索查询", min_length=1, max_length=500)
    k: int = Field(10, description="返回结果数量", ge=1, le=100)
    entity_types: Optional[List[str]] = Field(None, description="实体类型过滤")


class GraphSearchRequest(BaseModel):
    """图搜索请求"""

    entity_id: str = Field(..., description="起始实体ID", min_length=1, max_length=255)
    max_depth: int = Field(2, description="最大搜索深度", ge=1, le=5)
    relationship_types: Optional[List[str]] = Field(None, description="关系类型过滤")
    max_results: int = Field(20, description="最大结果数量", ge=1, le=100)


class RecommendationRequest(BaseModel):
    """推荐请求"""

    user_context: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="用户上下文"
    )
    max_recommendations: int = Field(10, description="最大推荐数量", ge=1, le=50)
    algorithm: str = Field(
        "hybrid", description="推荐算法", pattern="^(hybrid|graph|vector|behavior)$"
    )


class MigrationRequest(BaseModel):
    """数据迁移请求"""

    force_rebuild: bool = Field(False, description="是否强制重建")
    batch_size: int = Field(100, description="批处理大小", ge=10, le=1000)
    auto_embed: bool = Field(True, description="是否自动生成向量嵌入")


class EntityResponse(BaseModel):
    """实体响应"""

    id: str
    name: str
    entity_type: str
    description: Optional[str]
    attributes: Dict[str, Any]
    metadata: Dict[str, Any]
    embedding_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_accessed: Optional[datetime]
    access_count: int
    relevance_score: float


class SearchResultResponse(BaseModel):
    """搜索结果响应"""

    id: str
    content: str
    score: float
    metadata: Dict[str, Any]
    entity_id: Optional[str]


class RecommendationResponse(BaseModel):
    """推荐响应"""

    entity_id: str
    entity_name: str
    entity_type: str
    score: float
    reason: str
    source: str
    related_entities: List[str]
    confidence: float


class StorageMetricsResponse(BaseModel):
    """存储指标响应"""

    total_entities: int
    total_relationships: int
    total_vectors: int
    total_behaviors: int
    total_conversations: int
    storage_usage_mb: float
    last_sync_time: datetime
    health_status: str


# === 依赖注入 ===


async def get_storage_service() -> StorageOrchestrator:
    """获取存储服务依赖"""
    try:
        return await get_storage_orchestrator()
    except Exception as e:
        logger.error(f"获取存储服务失败: {e}")
        raise HTTPException(status_code=500, detail="存储服务不可用")


async def get_migration_service_dep() -> DataMigrationService:
    """获取迁移服务依赖"""
    try:
        return await get_migration_service()
    except Exception as e:
        logger.error(f"获取迁移服务失败: {e}")
        raise HTTPException(status_code=500, detail="迁移服务不可用")


# === 实体管理API ===


@router.post("/entities", response_model=Dict[str, Any])
async def create_entity(
    request: EntityCreateRequest,
    storage: StorageOrchestrator = Depends(get_storage_service),
):
    """创建知识实体"""
    try:
        success = await storage.create_entity(
            entity_id=request.entity_id,
            name=request.name,
            entity_type=request.entity_type,
            description=request.description,
            attributes=request.attributes,
            source_path=request.source_path,
            content=request.content,
            auto_embed=request.auto_embed,
        )

        if success:
            return {
                "success": True,
                "message": f"实体 {request.entity_id} 创建成功",
                "entity_id": request.entity_id,
            }
        else:
            raise HTTPException(status_code=400, detail="实体创建失败")

    except Exception as e:
        logger.error(f"创建实体失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entities/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: str, storage: StorageOrchestrator = Depends(get_storage_service)
):
    """获取知识实体"""
    try:
        entity = await storage.get_entity(entity_id)

        if not entity:
            raise HTTPException(status_code=404, detail=f"实体 {entity_id} 不存在")

        return EntityResponse(
            id=entity.id,
            name=entity.name,
            entity_type=entity.entity_type,
            description=entity.description,
            attributes=entity.attributes,
            metadata=entity.metadata,
            embedding_id=entity.embedding_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            last_accessed=entity.last_accessed,
            access_count=entity.access_count,
            relevance_score=entity.relevance_score,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取实体失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/entities/{entity_id}", response_model=Dict[str, Any])
async def update_entity(
    entity_id: str,
    request: EntityUpdateRequest,
    storage: StorageOrchestrator = Depends(get_storage_service),
):
    """更新知识实体"""
    try:
        # 构建更新字典，过滤None值
        updates = {}
        if request.name is not None:
            updates["name"] = request.name
        if request.description is not None:
            updates["description"] = request.description
        if request.attributes is not None:
            updates["attributes"] = request.attributes

        if not updates:
            raise HTTPException(status_code=400, detail="没有提供更新字段")

        success = await storage.update_entity(entity_id, updates)

        if success:
            return {
                "success": True,
                "message": f"实体 {entity_id} 更新成功",
                "entity_id": entity_id,
            }
        else:
            raise HTTPException(status_code=404, detail=f"实体 {entity_id} 不存在")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新实体失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/entities/{entity_id}", response_model=Dict[str, Any])
async def delete_entity(
    entity_id: str, storage: StorageOrchestrator = Depends(get_storage_service)
):
    """删除知识实体"""
    try:
        success = await storage.delete_entity(entity_id)

        if success:
            return {
                "success": True,
                "message": f"实体 {entity_id} 删除成功",
                "entity_id": entity_id,
            }
        else:
            raise HTTPException(status_code=404, detail=f"实体 {entity_id} 不存在")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除实体失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === 关系管理API ===


@router.post("/relationships", response_model=Dict[str, Any])
async def create_relationship(
    request: RelationshipCreateRequest,
    storage: StorageOrchestrator = Depends(get_storage_service),
):
    """创建实体关系"""
    try:
        success = await storage.create_relationship(
            source_entity=request.source_entity,
            target_entity=request.target_entity,
            relationship_type=request.relationship_type,
            strength=request.strength,
            confidence=request.confidence,
            attributes=request.attributes,
        )

        if success:
            return {
                "success": True,
                "message": f"关系创建成功: {request.source_entity} -> {request.target_entity}",
                "relationship": {
                    "source": request.source_entity,
                    "target": request.target_entity,
                    "type": request.relationship_type,
                },
            }
        else:
            raise HTTPException(status_code=400, detail="关系创建失败")

    except Exception as e:
        logger.error(f"创建关系失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === 智能搜索API ===


@router.post("/search/semantic", response_model=List[SearchResultResponse])
async def semantic_search(
    request: SemanticSearchRequest,
    storage: StorageOrchestrator = Depends(get_storage_service),
):
    """语义搜索"""
    try:
        results = await storage.semantic_search(
            query=request.query, k=request.k, entity_types=request.entity_types
        )

        return [
            SearchResultResponse(
                id=result.id,
                content=result.content,
                score=result.score,
                metadata=result.metadata,
                entity_id=result.entity_id,
            )
            for result in results
        ]

    except Exception as e:
        logger.error(f"语义搜索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/graph", response_model=List[str])
async def graph_search(
    request: GraphSearchRequest,
    storage: StorageOrchestrator = Depends(get_storage_service),
):
    """图结构搜索"""
    try:
        results = await storage.graph_search(
            entity_id=request.entity_id,
            max_depth=request.max_depth,
            relationship_types=request.relationship_types,
            max_results=request.max_results,
        )

        return results

    except Exception as e:
        logger.error(f"图搜索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === 智能推荐API ===


@router.post("/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations(
    request: RecommendationRequest,
    storage: StorageOrchestrator = Depends(get_storage_service),
):
    """获取智能推荐"""
    try:
        recommendations = await storage.get_smart_recommendations(
            user_context=request.user_context,
            max_recommendations=request.max_recommendations,
            algorithm=request.algorithm,
        )

        return [
            RecommendationResponse(
                entity_id=rec.entity_id,
                entity_name=rec.entity_name,
                entity_type=rec.entity_type,
                score=rec.score,
                reason=rec.reason,
                source=rec.source,
                related_entities=rec.related_entities,
                confidence=rec.confidence,
            )
            for rec in recommendations
        ]

    except Exception as e:
        logger.error(f"获取推荐失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === 系统监控API ===


@router.get("/metrics", response_model=StorageMetricsResponse)
async def get_storage_metrics(
    storage: StorageOrchestrator = Depends(get_storage_service),
):
    """获取存储系统指标"""
    try:
        metrics = await storage.get_metrics()

        return StorageMetricsResponse(
            total_entities=metrics.total_entities,
            total_relationships=metrics.total_relationships,
            total_vectors=metrics.total_vectors,
            total_behaviors=metrics.total_behaviors,
            total_conversations=metrics.total_conversations,
            storage_usage_mb=metrics.storage_usage_mb,
            last_sync_time=metrics.last_sync_time,
            health_status=metrics.health_status,
        )

    except Exception as e:
        logger.error(f"获取存储指标失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync", response_model=Dict[str, Any])
async def sync_storage(storage: StorageOrchestrator = Depends(get_storage_service)):
    """手动同步所有存储层"""
    try:
        success = await storage.sync_all()

        return {
            "success": success,
            "message": "存储同步完成" if success else "存储同步失败",
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"存储同步失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === 数据迁移API ===


@router.get("/migration/status", response_model=Dict[str, Any])
async def get_migration_status(
    migration: DataMigrationService = Depends(get_migration_service_dep),
):
    """获取数据迁移状态"""
    try:
        status = await migration.check_migration_status()
        return status

    except Exception as e:
        logger.error(f"获取迁移状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/migration/full", response_model=Dict[str, Any])
async def migrate_all_data(
    request: MigrationRequest,
    migration: DataMigrationService = Depends(get_migration_service_dep),
):
    """执行完整数据迁移"""
    try:
        logger.info("开始完整数据迁移...")

        stats = await migration.migrate_all_data(
            force_rebuild=request.force_rebuild,
            batch_size=request.batch_size,
            auto_embed=request.auto_embed,
        )

        return {
            "success": True,
            "message": "数据迁移完成",
            "stats": {
                "total_entities": stats.total_entities,
                "migrated_entities": stats.migrated_entities,
                "failed_entities": stats.failed_entities,
                "total_relationships": stats.total_relationships,
                "migrated_relationships": stats.migrated_relationships,
                "failed_relationships": stats.failed_relationships,
                "total_embeddings": stats.total_embeddings,
                "migrated_embeddings": stats.migrated_embeddings,
                "duration_seconds": stats.duration_seconds,
                "entity_success_rate": stats.entity_success_rate,
                "relationship_success_rate": stats.relationship_success_rate,
            },
        }

    except Exception as e:
        logger.error(f"数据迁移失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/migration/incremental", response_model=Dict[str, Any])
async def migrate_incremental_data(
    since: Optional[str] = Query(None, description="起始时间 (ISO格式)"),
    auto_embed: bool = Query(True, description="是否自动生成向量嵌入"),
    migration: DataMigrationService = Depends(get_migration_service_dep),
):
    """执行增量数据迁移"""
    try:
        since_datetime = None
        if since:
            since_datetime = datetime.fromisoformat(since.replace("Z", "+00:00"))

        logger.info("开始增量数据迁移...")

        stats = await migration.migrate_incremental(
            since=since_datetime, auto_embed=auto_embed
        )

        return {
            "success": True,
            "message": "增量迁移完成",
            "stats": {
                "total_entities": stats.total_entities,
                "migrated_entities": stats.migrated_entities,
                "failed_entities": stats.failed_entities,
                "total_relationships": stats.total_relationships,
                "migrated_relationships": stats.migrated_relationships,
                "failed_relationships": stats.failed_relationships,
                "duration_seconds": stats.duration_seconds,
            },
        }

    except Exception as e:
        logger.error(f"增量迁移失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
