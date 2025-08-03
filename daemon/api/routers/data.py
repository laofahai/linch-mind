#!/usr/bin/env python3
"""
数据查询路由 - 数据检索和推荐
Session 5 架构重构 - 模块化路由
"""

from fastapi import APIRouter, Depends
from typing import List
from datetime import datetime
import logging

from models.api_models import DataItem, AIRecommendation
from services.database_service import DatabaseService
from api.dependencies import get_db_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/data", tags=["data"])

# 真实推荐数据将来自AI推荐服务


@router.get("/", response_model=List[DataItem])
async def get_collected_data(
    limit: int = 100,
    db_service: DatabaseService = Depends(get_db_service)
):
    """获取收集的数据"""
    logger.info(f"获取收集数据，限制: {limit}")
    
    # 直接获取数据库中的真实数据项
    data_items = db_service.get_data_items(limit)
    
    # 转换返回格式以匹配API模型
    return [DataItem(
        id=item["id"],
        content=item["content"],
        source_connector=item["source_connector"],
        timestamp=datetime.fromisoformat(item["timestamp"]),
        file_path=item.get("file_path"),
        metadata=item.get("metadata", {}),
        storage_strategy=item.get("storage_strategy"),
        storage_reason=item.get("storage_reason"),
        original_content_size=item.get("original_content_size"),
        processed=item.get("processed")
    ) for item in data_items]


@router.get("/recommendations", response_model=List[AIRecommendation])
async def get_recommendations(limit: int = 10):
    """获取AI推荐"""
    logger.info(f"获取AI推荐，限制: {limit}")
    
    # TODO: 集成真实AI推荐服务
    # 暂时返回空列表，等待AI推荐引擎实现
    return []


@router.get("/search")
async def search_data(
    query: str,
    limit: int = 50,
    db_service: DatabaseService = Depends(get_db_service)
):
    """搜索数据内容"""
    logger.info(f"搜索数据: {query}, 限制: {limit}")
    
    # TODO: 实现全文搜索功能
    # 这里可以集成向量搜索或全文索引
    
    return {
        "query": query,
        "results": [],
        "total": 0,
        "message": "搜索功能正在开发中"
    }


@router.get("/stats")
async def get_data_stats(db_service: DatabaseService = Depends(get_db_service)):
    """获取数据统计信息"""
    logger.info("获取数据统计信息")
    
    stats = db_service.get_database_stats()
    
    # 扩展统计信息，包括存储策略相关数据
    stats.update({
        "storage_efficiency": {
            "description": "存储效率统计",
            "total_original_size": "未统计",
            "total_stored_size": "未统计", 
            "compression_ratio": "待计算",
            "note": "功能开发中"
        },
        "content_types": {
            "description": "内容类型分布",
            "note": "功能开发中"
        }
    })
    
    return stats