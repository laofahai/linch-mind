#!/usr/bin/env python3
"""
存储API - 三层存储架构的HTTP接口
提供实体管理、智能搜索、推荐等功能的RESTful API
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, HTTPException, Query
from pydantic import BaseModel, Field
from services.storage import (KnowledgeEntity, SmartRecommendation, StorageMetrics,
                              get_storage_orchestrator)

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/storage", tags=["storage"])


# ===== 请求/响应模型 =====


class CreateEntityRequest(BaseModel):
    """创建实体请求"""

    entity_id: str = Field(..., description="实体唯一标识")
    name: str = Field(..., description="实体名称")
    entity_type: str = Field(..., description="实体类型")
    description: Optional[str] = Field(None, description="实体描述")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="实体属性")
    source_path: Optional[str] = Field(None, description="源文件路径")
    content: Optional[str] = Field(None, description="文本内容")


class UpdateEntityRequest(BaseModel):
    """更新实体请求"""

    name: Optional[str] = None
    description: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None


class CreateRelationshipRequest(BaseModel):
    """创建关系请求"""

    source_entity: str = Field(..., description="源实体ID")
    target_entity: str = Field(..., description="目标实体ID")
    relationship_type: str = Field(..., description="关系类型")
    strength: float = Field(1.0, description="关系强度", ge=0.0, le=1.0)
    confidence: float = Field(1.0, description="置信度", ge=0.0, le=1.0)
    attributes: Dict[str, Any] = Field(default_factory=dict, description="关系属性")


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


class SearchResult(BaseModel):
    """搜索结果"""

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


class StorageStatsResponse(BaseModel):
    """存储统计响应"""

    total_entities: int
    total_relationships: int
    total_vectors: int
    total_behaviors: int
    total_conversations: int
    storage_usage_mb: float
    last_sync_time: datetime
    health_status: str


# ===== 实体管理API =====


@router.post("/entities", response_model=Dict[str, Any])
async def create_entity(request: CreateEntityRequest):
    """创建新实体"""
    try:
        orchestrator = await get_storage_orchestrator()

        # TODO: 如果有content，需要生成embedding
        embedding = None
        if request.content:
            # 这里需要集成embedding模型
            # embedding = await generate_embedding(request.content)
            pass

        success = await orchestrator.create_entity(
            entity_id=request.entity_id,
            name=request.name,
            entity_type=request.entity_type,
            description=request.description,
            attributes=request.attributes,
            source_path=request.source_path,
            content=request.content,
            embedding=embedding,
        )

        if success:
            return {"success": True, "entity_id": request.entity_id}
        else:
            raise HTTPException(status_code=400, detail="创建实体失败")

    except Exception as e:
        logger.error(f"创建实体API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entities/{entity_id}", response_model=EntityResponse)
async def get_entity(entity_id: str):
    """获取实体详情"""
    try:
        orchestrator = await get_storage_orchestrator()

        entity = await orchestrator.get_entity(entity_id)
        if not entity:
            raise HTTPException(status_code=404, detail="实体不存在")

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
        logger.error(f"获取实体API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/entities/{entity_id}", response_model=Dict[str, Any])
async def update_entity(entity_id: str, request: UpdateEntityRequest):
    """更新实体"""
    try:
        orchestrator = await get_storage_orchestrator()

        # 构建更新字典
        updates = {}
        if request.name is not None:
            updates["name"] = request.name
        if request.description is not None:
            updates["description"] = request.description
        if request.attributes is not None:
            updates["entity_metadata"] = {"attributes": request.attributes}

        if not updates:
            raise HTTPException(status_code=400, detail="没有提供更新数据")

        success = await orchestrator.update_entity(entity_id, updates)

        if success:
            return {"success": True, "entity_id": entity_id}
        else:
            raise HTTPException(status_code=400, detail="更新实体失败")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新实体API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/entities/{entity_id}", response_model=Dict[str, Any])
async def delete_entity(entity_id: str):
    """删除实体"""
    try:
        orchestrator = await get_storage_orchestrator()

        success = await orchestrator.delete_entity(entity_id)

        if success:
            return {"success": True, "entity_id": entity_id}
        else:
            raise HTTPException(status_code=400, detail="删除实体失败")

    except Exception as e:
        logger.error(f"删除实体API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== 关系管理API =====


@router.post("/relationships", response_model=Dict[str, Any])
async def create_relationship(request: CreateRelationshipRequest):
    """创建实体关系"""
    try:
        orchestrator = await get_storage_orchestrator()

        success = await orchestrator.create_relationship(
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
                "relationship": f"{request.source_entity} -> {request.target_entity}",
            }
        else:
            raise HTTPException(status_code=400, detail="创建关系失败")

    except Exception as e:
        logger.error(f"创建关系API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== 搜索API =====


@router.get("/search/semantic", response_model=List[SearchResult])
async def semantic_search(
    query: str = Query(..., description="搜索查询"),
    k: int = Query(10, description="返回结果数量", ge=1, le=100),
    entity_types: Optional[List[str]] = Query(None, description="实体类型过滤"),
):
    """语义搜索"""
    try:
        orchestrator = await get_storage_orchestrator()

        # TODO: 需要集成embedding模型
        # embedding_model = await get_embedding_model()
        embedding_model = None

        if not embedding_model:
            raise HTTPException(status_code=501, detail="语义搜索功能暂未启用")

        results = await orchestrator.semantic_search(
            query=query, k=k, entity_types=entity_types, embedding_model=embedding_model
        )

        return [
            SearchResult(
                id=result.id,
                content=result.content,
                score=result.score,
                metadata=result.metadata,
                entity_id=result.entity_id,
            )
            for result in results
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"语义搜索API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/graph/{entity_id}", response_model=List[str])
async def graph_search(
    entity_id: str,
    max_depth: int = Query(2, description="最大搜索深度", ge=1, le=5),
    relationship_types: Optional[List[str]] = Query(None, description="关系类型过滤"),
    max_results: int = Query(20, description="最大结果数", ge=1, le=100),
):
    """图关系搜索"""
    try:
        orchestrator = await get_storage_orchestrator()

        results = await orchestrator.graph_search(
            entity_id=entity_id,
            max_depth=max_depth,
            relationship_types=relationship_types,
            max_results=max_results,
        )

        return results

    except Exception as e:
        logger.error(f"图搜索API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== 推荐API =====


@router.get("/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations(
    max_recommendations: int = Query(10, description="最大推荐数量", ge=1, le=50),
    algorithm: str = Query(
        "hybrid", description="推荐算法", regex="^(hybrid|graph|vector|behavior)$"
    ),
    user_context: Optional[str] = Query(None, description="用户上下文JSON"),
):
    """获取智能推荐"""
    try:
        orchestrator = await get_storage_orchestrator()

        # 解析用户上下文
        context = {}
        if user_context:
            import json

            try:
                context = json.loads(user_context)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="用户上下文JSON格式错误")

        recommendations = await orchestrator.get_smart_recommendations(
            user_context=context,
            max_recommendations=max_recommendations,
            algorithm=algorithm,
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

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"推荐API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== 统计和监控API =====


@router.get("/stats", response_model=StorageStatsResponse)
async def get_storage_stats():
    """获取存储系统统计"""
    try:
        orchestrator = await get_storage_orchestrator()

        metrics = await orchestrator.get_metrics()

        return StorageStatsResponse(
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
        logger.error(f"获取存储统计API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync", response_model=Dict[str, Any])
async def trigger_sync():
    """触发数据同步"""
    try:
        orchestrator = await get_storage_orchestrator()

        success = await orchestrator.sync_all()

        return {
            "success": success,
            "sync_time": datetime.utcnow().isoformat(),
            "message": "数据同步完成" if success else "数据同步失败",
        }

    except Exception as e:
        logger.error(f"数据同步API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """存储系统健康检查"""
    try:
        orchestrator = await get_storage_orchestrator()

        # 获取各个服务的状态
        health_status = {
            "storage_orchestrator": "healthy",
            "graph_service": "unknown",
            "vector_service": "unknown",
            "database_service": "unknown",
        }

        try:
            # 检查图服务
            if orchestrator.graph_service:
                await orchestrator.graph_service.get_metrics()
                health_status["graph_service"] = "healthy"
        except Exception:
            health_status["graph_service"] = "error"

        try:
            # 检查向量服务
            if orchestrator.vector_service:
                await orchestrator.vector_service.get_metrics()
                health_status["vector_service"] = "healthy"
        except Exception:
            health_status["vector_service"] = "error"

        try:
            # 检查数据库服务
            if orchestrator.db_service:
                orchestrator.db_service.get_database_stats()
                health_status["database_service"] = "healthy"
        except Exception:
            health_status["database_service"] = "error"

        overall_status = (
            "healthy"
            if all(status == "healthy" for status in health_status.values())
            else "degraded"
        )

        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "services": health_status,
        }

    except Exception as e:
        logger.error(f"健康检查API错误: {e}")
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
        }


# ===== 数据生命周期管理API =====


@router.post("/cleanup", response_model=Dict[str, Any])
async def trigger_cleanup():
    """触发数据清理"""
    try:
        from services.storage import get_lifecycle_manager

        lifecycle_manager = await get_lifecycle_manager()
        cleanup_stats = await lifecycle_manager.cleanup_expired_data()

        return {
            "success": True,
            "cleanup_time": datetime.utcnow().isoformat(),
            "stats": cleanup_stats,
        }

    except Exception as e:
        logger.error(f"数据清理API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health-report", response_model=Dict[str, Any])
async def get_health_report():
    """获取数据健康报告"""
    try:
        from services.storage import get_lifecycle_manager

        lifecycle_manager = await get_lifecycle_manager()
        report = await lifecycle_manager.generate_health_report()

        return {
            "report_time": datetime.utcnow().isoformat(),
            "total_entities": report.total_entities,
            "total_relationships": report.total_relationships,
            "total_behaviors": report.total_behaviors,
            "total_conversations": report.total_conversations,
            "storage_usage_mb": report.storage_usage_mb,
            "storage_usage_percentage": report.storage_usage_percentage,
            "data_quality": {
                "orphaned_entities": report.orphaned_entities,
                "duplicate_relationships": report.duplicate_relationships,
                "invalid_vectors": report.invalid_vectors,
                "broken_references": report.broken_references,
            },
            "performance": {
                "avg_query_time_ms": report.avg_query_time_ms,
                "cache_hit_rate": report.cache_hit_rate,
                "index_efficiency": report.index_efficiency,
            },
            "cleanup_stats": {
                "cleaned_entities": report.cleaned_entities,
                "cleaned_behaviors": report.cleaned_behaviors,
                "cleaned_conversations": report.cleaned_conversations,
                "archived_items": report.archived_items,
            },
            "last_cleanup": (
                report.last_cleanup.isoformat() if report.last_cleanup else None
            ),
            "last_optimization": (
                report.last_optimization.isoformat()
                if report.last_optimization
                else None
            ),
            "health_score": report.health_score,
        }

    except Exception as e:
        logger.error(f"获取健康报告API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))
