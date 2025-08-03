#!/usr/bin/env python3
"""
数据摄取路由 - 处理连接器推送的数据
Session 5 架构重构 - 智能存储策略集成
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from models.api_models import DataIngestionRequest, EntityRequest, RelationshipRequest, ApiResponse
from services.database_service import DatabaseService
from services.storage_strategy import SmartContentProcessor
from api.dependencies import get_db_service, get_processor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["ingestion"])


@router.post("/data/ingest")
async def ingest_data(
    data_item: DataIngestionRequest,
    db_service: DatabaseService = Depends(get_db_service),
    processor: SmartContentProcessor = Depends(get_processor)
):
    """
    智能数据摄取端点 - 连接器推送数据到 Daemon
    应用智能存储策略处理内容
    """
    logger.info(f"接收数据推送: {data_item.source_connector} - {data_item.id}")
    
    try:
        # 使用智能存储策略处理内容
        processed_item = processor.process_content(
            content=data_item.content,
            file_path=data_item.file_path or "",
            metadata={
                "connector": data_item.source_connector,
                **data_item.metadata
            }
        )
        
        # 更新基本信息
        processed_item.update({
            "id": data_item.id,
            "source_connector": data_item.source_connector,
            "timestamp": data_item.timestamp,
            "file_path": data_item.file_path
        })
        
        # SmartContentProcessor已返回DataItem兼容的结构，无需额外处理
        
        # 保存到数据库
        saved_id = db_service.save_data_item(processed_item)
        
        # 记录处理结果
        logger.info(f"数据处理完成: {processed_item['storage_strategy']} - {saved_id}")
        logger.info(f"原始大小: {processed_item['original_size']} 字节")
        logger.info(f"处理后大小: {processed_item['processed_size']} 字节")
        
        # TODO: 触发AI分析和推荐生成
        # await trigger_ai_analysis(saved_id)
        
        return ApiResponse(
            success=True, 
            message=f"数据智能处理完成: {saved_id}",
            data={
                "saved_id": saved_id,
                "storage_strategy": processed_item["storage_strategy"],
                "original_size": processed_item["original_size"],
                "processed_size": processed_item["processed_size"],
                "processing_reason": processed_item["processing_info"].get("storage_reason")
            }
        )
        
    except Exception as e:
        logger.error(f"数据摄取失败: {e}")
        raise HTTPException(status_code=500, detail=f"数据摄取失败: {str(e)}")


@router.post("/entities/ingest")
async def ingest_entities(
    entities: List[EntityRequest],
    db_service: DatabaseService = Depends(get_db_service)
):
    """连接器推送实体数据"""
    logger.info(f"接收实体推送: {len(entities)} 个实体")
    
    try:
        saved_entities = []
        for entity in entities:
            db_service.save_graph_node(
                node_id=entity.id,
                node_type=entity.type,
                label=entity.label,
                properties=entity.properties,
                source_data_id=entity.source_data_id
            )
            saved_entities.append(entity.id)
        
        return ApiResponse(
            success=True,
            message=f"实体接收成功: {len(saved_entities)} 个",
            data={"saved_entities": saved_entities}
        )
        
    except Exception as e:
        logger.error(f"实体接收失败: {e}")
        raise HTTPException(status_code=500, detail=f"实体接收失败: {str(e)}")


@router.post("/relationships/ingest")
async def ingest_relationships(
    relationships: List[RelationshipRequest],
    db_service: DatabaseService = Depends(get_db_service)
):
    """连接器推送关系数据"""
    logger.info(f"接收关系推送: {len(relationships)} 个关系")
    
    try:
        saved_relationships = []
        for rel in relationships:
            db_service.save_graph_relationship(
                rel_id=rel.id,
                source_node_id=rel.source_entity_id,
                target_node_id=rel.target_entity_id,
                relationship_type=rel.relationship_type,
                weight=rel.weight,
                properties=rel.properties
            )
            saved_relationships.append(rel.id)
        
        return ApiResponse(
            success=True,
            message=f"关系接收成功: {len(saved_relationships)} 个",
            data={"saved_relationships": saved_relationships}
        )
        
    except Exception as e:
        logger.error(f"关系接收失败: {e}")
        raise HTTPException(status_code=500, detail=f"关系接收失败: {str(e)}")


@router.get("/ingestion/stats")
async def get_ingestion_stats(db_service: DatabaseService = Depends(get_db_service)):
    """获取数据摄取统计信息"""
    logger.info("获取数据摄取统计信息")
    
    try:
        stats = db_service.get_database_stats()
        
        # 扩展统计信息
        stats.update({
            "storage_strategies": {
                "description": "各种存储策略的使用统计",
                "note": "功能开发中"
            },
            "processing_performance": {
                "description": "数据处理性能指标", 
                "note": "功能开发中"
            }
        })
        
        return stats
        
    except Exception as e:
        logger.error(f"获取摄取统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")