#!/usr/bin/env python3
"""
存储服务模块 - 三层数据存储架构

提供统一的数据存储和访问接口，支持：
- SQLite关系数据库 (元数据和结构化数据)
- NetworkX图数据库 (知识图谱和关系分析)
- FAISS向量数据库 (语义搜索和内容相似性)
- 智能数据生命周期管理
"""

from .data_lifecycle_manager import (
    DataHealthReport,
    DataLifecycleConfig,
    DataLifecycleManager,
    get_data_lifecycle_manager,
)
from .graph_service import (
    EntityNode,
    GraphMetrics,
    GraphService,
    RelationshipEdge,
    cleanup_graph_service,
    get_graph_service,
)
from .storage_orchestrator import (
    StorageMetrics,
    StorageOrchestrator,
    cleanup_storage_orchestrator,
    get_storage_orchestrator,
)
from .vector_service import (
    SearchResult,
    VectorDocument,
    VectorMetrics,
    VectorService,
    cleanup_vector_service,
    get_vector_service,
)

__all__ = [
    # 图服务
    "GraphService",
    "EntityNode",
    "RelationshipEdge",
    "GraphMetrics",
    "get_graph_service",
    "cleanup_graph_service",
    # 向量服务
    "VectorService",
    "VectorDocument",
    "SearchResult",
    "VectorMetrics",
    "get_vector_service",
    "cleanup_vector_service",
    # 存储编排器
    "StorageOrchestrator",
    "StorageMetrics",
    "get_storage_orchestrator",
    "cleanup_storage_orchestrator",
    # 数据生命周期管理
    "DataLifecycleManager",
    "DataLifecycleConfig",
    "DataHealthReport",
    "get_data_lifecycle_manager",
]


async def initialize_storage_system():
    """初始化整个存储系统"""
    try:
        # 按依赖顺序初始化
        await get_storage_orchestrator()
        await get_data_lifecycle_manager()

        return True
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"存储系统初始化失败: {e}")
        return False


async def cleanup_storage_system():
    """清理整个存储系统"""
    try:
        # 按相反顺序清理
        # await cleanup_lifecycle_manager()  # 函数不存在，注释掉
        await cleanup_storage_orchestrator()
        await cleanup_vector_service()
        await cleanup_graph_service()

    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"存储系统清理失败: {e}")


def get_storage_info():
    """获取存储系统信息"""
    return {
        "name": "Linch Mind三层存储架构",
        "version": "1.0.0",
        "components": {
            "relational": "SQLite + SQLAlchemy",
            "graph": "NetworkX内存图数据库",
            "vector": "FAISS向量搜索引擎",
            "orchestrator": "统一存储编排器",
            "lifecycle": "智能数据生命周期管理",
        },
        "features": [
            "35K-130K实体支持",
            "70K-400K关系支持",
            "10GB-50GB向量数据支持",
            "实时语义搜索",
            "图关系推荐",
            "智能数据清理",
            "性能监控和优化",
        ],
    }
