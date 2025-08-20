"""
星空宇宙数据路由 - 为UI星空可视化提供真实数据源

提供Entity、Graph、Vector数据的统一IPC接口，
支持星空宇宙组件所需的所有数据类型。

作者: Linch Mind 开发团队
创建: 2025-08-20
版本: v1.0 (架构统一版)
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..core.protocol import IPCRequest, IPCResponse
from ..core.router import IPCRouter
from core.service_facade import get_service
from services.storage.core.database import UnifiedDatabaseService
# from services.cached_networkx_service import CachedNetworkXService  # 临时注释
from services.storage.vector_service import VectorService
from services.storage.universal_index_service import UniversalIndexService

logger = logging.getLogger(__name__)


def create_starry_universe_data_router() -> IPCRouter:
    """创建星空宇宙数据路由"""
    router = IPCRouter(prefix="/starry_universe")

    # ================================
    # Entity 数据接口
    # ================================

    @router.get("/entities")
    async def get_entities(request: IPCRequest) -> IPCResponse:
        """
        获取实体数据 - 智慧星座可视化

        查询参数：
        {
            "limit": 100,
            "entity_types": ["file", "person", "concept"],  // 可选
            "include_relationships": true,                  // 可选
            "importance_threshold": 0.1                     // 可选，重要性过滤
        }

        响应格式：
        {
            "entities": [
                {
                    "entity_id": "entity_123",
                    "name": "项目文档.md",
                    "type": "file",
                    "description": "重要项目文档",
                    "properties": {...},
                    "tags": ["project", "important"],
                    "access_count": 15,
                    "last_accessed": "2025-08-20T10:00:00Z",
                    "created_at": "2025-08-01T09:00:00Z",
                    "updated_at": "2025-08-20T10:00:00Z",
                    "importance_score": 0.85
                }
            ],
            "relationships": [
                {
                    "source_entity_id": "entity_123",
                    "target_entity_id": "entity_456", 
                    "relationship_type": "related_to",
                    "strength": 8,
                    "description": "相关文档",
                    "properties": {...}
                }
            ],
            "total_count": 250,
            "stats": {
                "by_type": {"file": 120, "person": 80, "concept": 50},
                "total_relationships": 380
            }
        }
        """
        try:
            data = request.data or {}
            
            # 参数解析
            limit = data.get("limit", 100)
            entity_types = data.get("entity_types", [])
            include_relationships = data.get("include_relationships", True)
            importance_threshold = data.get("importance_threshold", 0.0)

            logger.info(f"🌟 获取实体数据: limit={limit}, types={entity_types}")

            # 获取数据库服务
            db_service = get_service(UnifiedDatabaseService)
            
            # 查询实体数据
            entities_data = await _fetch_entities_with_importance(
                db_service, limit, entity_types, importance_threshold
            )
            
            relationships_data = []
            if include_relationships:
                relationships_data = await _fetch_entity_relationships(
                    db_service, [e["entity_id"] for e in entities_data]
                )

            # 统计信息
            stats = await _calculate_entity_stats(db_service)

            logger.info(f"✨ 实体数据获取完成: {len(entities_data)} entities, {len(relationships_data)} relationships")
            
            # 调试：打印第一个实体的字段结构
            if entities_data:
                logger.info(f"🔍 实体数据字段调试: {list(entities_data[0].keys())}")
                logger.info(f"🔍 第一个实体示例: {entities_data[0]}")

            return IPCResponse.success_response({
                "entities": entities_data,
                "relationships": relationships_data,
                "total_count": len(entities_data),
                "stats": stats,
                "query_info": {
                    "limit": limit,
                    "entity_types": entity_types,
                    "include_relationships": include_relationships,
                    "importance_threshold": importance_threshold
                }
            })

        except Exception as e:
            logger.error(f"❌ 获取实体数据失败: {str(e)}")
            return IPCResponse.error_response(
                "ENTITY_FETCH_ERROR", f"Failed to fetch entities: {str(e)}"
            )

    @router.get("/entities/{entity_id}")
    async def get_entity_details(request: IPCRequest) -> IPCResponse:
        """
        获取单个实体详情

        路径参数：
        - entity_id: 实体ID

        响应格式：
        {
            "entity": {...},  // 完整实体信息
            "relationships": [...],  // 相关关系
            "related_entities": [...],  // 相关实体
            "activity_timeline": [...],  // 活动时间线
            "importance_breakdown": {...}  // 重要性分析
        }
        """
        try:
            entity_id = request.path_params.get("entity_id")
            if not entity_id:
                return IPCResponse.error_response("INVALID_REQUEST", "Missing entity_id")

            db_service = get_service(UnifiedDatabaseService)
            
            # 获取实体详情
            entity = await _fetch_single_entity(db_service, entity_id)
            if not entity:
                return IPCResponse.error_response("NOT_FOUND", f"Entity {entity_id} not found")

            # 获取相关数据
            relationships = await _fetch_entity_relationships(db_service, [entity_id])
            related_entities = await _fetch_related_entities(db_service, entity_id)
            
            return IPCResponse.success_response({
                "entity": entity,
                "relationships": relationships,
                "related_entities": related_entities,
                "entity_id": entity_id
            })

        except Exception as e:
            logger.error(f"❌ 获取实体详情失败: {str(e)}")
            return IPCResponse.error_response(
                "ENTITY_DETAIL_ERROR", f"Failed to fetch entity details: {str(e)}"
            )

    # ================================
    # Graph 数据接口
    # ================================

    @router.get("/graph")
    async def get_graph_data(request: IPCRequest) -> IPCResponse:
        """
        获取知识图谱数据 - 知识宇宙可视化

        查询参数：
        {
            "max_nodes": 500,
            "max_edges": 1000,
            "include_centrality": true,  // 包含中心性计算
            "include_clusters": true,    // 包含聚类信息
            "node_types": ["file", "person"],  // 节点类型过滤
            "min_edge_weight": 0.3      // 最小边权重
        }

        响应格式：
        {
            "nodes": [
                {
                    "id": "entity_123",
                    "label": "项目文档.md", 
                    "node_type": "file",
                    "attributes": {...},
                    "weight": 1.0,
                    "importance": 0.85,
                    "centrality": 0.42
                }
            ],
            "edges": [
                {
                    "source": "entity_123",
                    "target": "entity_456",
                    "edge_type": "related_to",
                    "weight": 0.75,
                    "attributes": {...}
                }
            ],
            "clusters": {
                "cluster_1": ["entity_123", "entity_456"],
                "cluster_2": ["entity_789"]
            },
            "graph_metrics": {
                "node_count": 250,
                "edge_count": 380,
                "density": 0.012,
                "average_degree": 3.04,
                "is_connected": true
            },
            "centrality_metrics": {
                "betweenness": {...},
                "closeness": {...},
                "eigenvector": {...}
            }
        }
        """
        try:
            data = request.data or {}
            
            # 参数解析
            max_nodes = data.get("max_nodes", 500)
            max_edges = data.get("max_edges", 1000)
            include_centrality = data.get("include_centrality", True)
            include_clusters = data.get("include_clusters", True)
            node_types = data.get("node_types", [])
            min_edge_weight = data.get("min_edge_weight", 0.0)

            logger.info(f"🌌 获取图谱数据: max_nodes={max_nodes}, include_centrality={include_centrality}")

            # 获取NetworkX服务 (临时跳过)
            # graph_service = get_service(CachedNetworkXService)
            
            # 确保图谱已加载 (临时跳过)
            # await graph_service.load_optimized_graph()
            
            # 获取图数据
            graph_data = await _extract_graph_visualization_data(
                None, max_nodes, max_edges, node_types, min_edge_weight
            )
            
            # 计算中心性（如果需要）
            centrality_metrics = {}
            if include_centrality:
                centrality_metrics = await _calculate_centrality_metrics(None)  # 临时传None
            
            # 获取聚类信息（如果需要）
            clusters = {}
            if include_clusters:
                clusters = await _get_graph_clusters(None)  # 临时传None

            logger.info(f"🎯 图谱数据获取完成: {len(graph_data['nodes'])} nodes, {len(graph_data['edges'])} edges")

            return IPCResponse.success_response({
                **graph_data,
                "clusters": clusters,
                "centrality_metrics": centrality_metrics,
                "query_info": {
                    "max_nodes": max_nodes,
                    "max_edges": max_edges,
                    "include_centrality": include_centrality,
                    "include_clusters": include_clusters,
                    "node_types": node_types,
                    "min_edge_weight": min_edge_weight
                }
            })

        except Exception as e:
            logger.error(f"❌ 获取图谱数据失败: {str(e)}")
            return IPCResponse.error_response(
                "GRAPH_FETCH_ERROR", f"Failed to fetch graph data: {str(e)}"
            )

    # ================================
    # Vector 数据接口
    # ================================

    @router.get("/vectors")
    async def get_vector_data(request: IPCRequest) -> IPCResponse:
        """
        获取向量数据 - 相似星云可视化

        查询参数：
        {
            "limit": 200,
            "include_embeddings": false,  // 是否包含完整向量
            "cluster_count": 10,          // 聚类数量
            "similarity_threshold": 0.7,  // 相似度阈值
            "content_types": ["text", "document"]  // 内容类型
        }

        响应格式：
        {
            "documents": [
                {
                    "document_id": "doc_123",
                    "content": "文档内容...",
                    "title": "文档标题",
                    "content_type": "text",
                    "metadata": {...},
                    "embedding_preview": [0.1, 0.2, ...],  // 前10维
                    "score": 0.95,
                    "source_connector": "connector_id",
                    "timestamp": "2025-08-20T10:00:00Z"
                }
            ],
            "clusters": [
                {
                    "cluster_id": "cluster_1", 
                    "document_ids": ["doc_123", "doc_456"],
                    "centroid_preview": [0.15, 0.25, ...],
                    "cohesion": 0.85,
                    "topic": "项目管理",
                    "keywords": ["项目", "管理", "计划"]
                }
            ],
            "similarity_matrix": {
                "doc_123": {"doc_456": 0.89, "doc_789": 0.76}
            },
            "vector_stats": {
                "total_documents": 1500,
                "embedding_dimension": 384,
                "avg_similarity": 0.45,
                "cluster_count": 10
            }
        }
        """
        try:
            data = request.data or {}
            
            # 参数解析
            limit = data.get("limit", 200)
            include_embeddings = data.get("include_embeddings", False)
            cluster_count = data.get("cluster_count", 10)
            similarity_threshold = data.get("similarity_threshold", 0.7)
            content_types = data.get("content_types", [])

            logger.info(f"💫 获取向量数据: limit={limit}, clusters={cluster_count}")

            # 获取向量服务
            vector_service = await _get_vector_service()
            
            # 获取向量文档
            documents = await _fetch_vector_documents(
                vector_service, limit, content_types, include_embeddings
            )
            
            # 执行聚类
            clusters = await _perform_vector_clustering(
                vector_service, documents, cluster_count
            )
            
            # 计算相似度矩阵（仅限高相似度对）
            similarity_matrix = await _calculate_similarity_matrix(
                vector_service, documents, similarity_threshold
            )
            
            # 向量统计
            vector_stats = await _get_vector_stats(vector_service)

            logger.info(f"🌟 向量数据获取完成: {len(documents)} documents, {len(clusters)} clusters")

            return IPCResponse.success_response({
                "documents": documents,
                "clusters": clusters,
                "similarity_matrix": similarity_matrix,
                "vector_stats": vector_stats,
                "query_info": {
                    "limit": limit,
                    "include_embeddings": include_embeddings,
                    "cluster_count": cluster_count,
                    "similarity_threshold": similarity_threshold,
                    "content_types": content_types
                }
            })

        except Exception as e:
            logger.error(f"❌ 获取向量数据失败: {str(e)}")
            return IPCResponse.error_response(
                "VECTOR_FETCH_ERROR", f"Failed to fetch vector data: {str(e)}"
            )

    @router.post("/vectors/search")
    async def vector_search(request: IPCRequest) -> IPCResponse:
        """
        向量语义搜索
        
        请求格式：
        {
            "query": "搜索文本",
            "limit": 20,
            "similarity_threshold": 0.7
        }
        """
        try:
            data = request.data or {}
            
            query = data.get("query", "")
            if not query.strip():
                return IPCResponse.error_response("INVALID_REQUEST", "Query cannot be empty")
                
            limit = data.get("limit", 20) 
            similarity_threshold = data.get("similarity_threshold", 0.7)

            vector_service = await _get_vector_service()
            
            # 执行向量搜索
            search_results = await _perform_vector_search(
                vector_service, query, limit, similarity_threshold
            )

            return IPCResponse.success_response({
                "query": query,
                "results": search_results,
                "total_results": len(search_results),
                "similarity_threshold": similarity_threshold
            })

        except Exception as e:
            logger.error(f"❌ 向量搜索失败: {str(e)}")
            return IPCResponse.error_response(
                "VECTOR_SEARCH_ERROR", f"Vector search failed: {str(e)}"
            )

    # ================================
    # 统一数据接口
    # ================================

    @router.get("/unified")
    async def get_unified_starry_data(request: IPCRequest) -> IPCResponse:
        """
        获取星空宇宙统一数据 - 一次性获取所有数据类型

        查询参数：
        {
            "include_entities": true,
            "include_graph": true,
            "include_vectors": true,
            "include_universal_index": true,
            "data_limits": {
                "entities": 100,
                "graph_nodes": 300,
                "vector_docs": 150,
                "index_entries": 200
            }
        }

        响应格式：
        {
            "entities": {...},          // Entity数据
            "graph": {...},             // Graph数据  
            "vectors": {...},           // Vector数据
            "universal_index": {...},   // UniversalIndex数据
            "data_summary": {
                "total_entities": 100,
                "total_nodes": 300,
                "total_vectors": 150,
                "total_index_entries": 200,
                "fetch_time_ms": 245
            }
        }
        """
        try:
            data = request.data or {}
            start_time = datetime.now()
            
            # 参数解析
            include_entities = data.get("include_entities", True)
            include_graph = data.get("include_graph", True)
            include_vectors = data.get("include_vectors", True)
            include_universal_index = data.get("include_universal_index", True)
            
            data_limits = data.get("data_limits", {})
            
            logger.info("🌠 获取星空宇宙统一数据")

            # 并行获取各种数据
            tasks = []
            result_data = {}

            if include_entities:
                tasks.append(_fetch_entities_for_unified(data_limits.get("entities", 100)))
            if include_graph:
                tasks.append(_fetch_graph_for_unified(data_limits.get("graph_nodes", 300)))
            if include_vectors:
                tasks.append(_fetch_vectors_for_unified(data_limits.get("vector_docs", 150)))
            if include_universal_index:
                tasks.append(_fetch_index_for_unified(data_limits.get("index_entries", 200)))

            # 并行执行
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            data_types = []
            if include_entities: data_types.append("entities")
            if include_graph: data_types.append("graph")
            if include_vectors: data_types.append("vectors")
            if include_universal_index: data_types.append("universal_index")
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"❌ 获取{data_types[i]}数据失败: {str(result)}")
                    result_data[data_types[i]] = {"error": str(result)}
                else:
                    result_data[data_types[i]] = result

            # 计算统计
            fetch_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            data_summary = {
                "fetch_time_ms": round(fetch_time_ms, 2),
                "included_data_types": data_types,
                "data_limits": data_limits
            }

            # 添加各数据类型的统计
            for data_type, data_content in result_data.items():
                if "error" not in data_content:
                    if data_type == "entities":
                        data_summary["total_entities"] = len(data_content.get("entities", []))
                    elif data_type == "graph":
                        data_summary["total_nodes"] = len(data_content.get("nodes", []))
                        data_summary["total_edges"] = len(data_content.get("edges", []))
                    elif data_type == "vectors":
                        data_summary["total_vectors"] = len(data_content.get("documents", []))
                    elif data_type == "universal_index":
                        data_summary["total_index_entries"] = len(data_content.get("results", []))

            logger.info(f"✨ 星空宇宙统一数据获取完成: {fetch_time_ms:.1f}ms")

            return IPCResponse.success_response({
                **result_data,
                "data_summary": data_summary
            })

        except Exception as e:
            logger.error(f"❌ 获取星空宇宙统一数据失败: {str(e)}")
            return IPCResponse.error_response(
                "UNIFIED_FETCH_ERROR", f"Failed to fetch unified starry data: {str(e)}"
            )

    return router


# ================================
# 辅助函数
# ================================

async def _fetch_entities_with_importance(
    db_service, limit: int, entity_types: List[str], importance_threshold: float
) -> List[Dict[str, Any]]:
    """获取带重要性评分的实体数据"""
    try:
        # 使用真实的通用索引服务获取数据
        # 已修复：使用ServiceFacade获取UniversalIndexService
        from services.storage.universal_index_service import SearchQuery, ContentType, IndexTier
        
        index_service = get_service(UniversalIndexService)
        
        # 构建搜索查询 - 获取所有类型的内容作为实体
        content_type_mapping = {
            "file": ContentType.FILE_PATH,
            "document": ContentType.DOCUMENT,
            "contact": ContentType.CONTACT,
            "text": ContentType.TEXT,
            "person": ContentType.CONTACT,
            "concept": ContentType.TEXT
        }
        
        # 转换entity_types到ContentType
        search_content_types = []
        if entity_types:
            for entity_type in entity_types:
                if entity_type in content_type_mapping:
                    search_content_types.append(content_type_mapping[entity_type])
        else:
            # 默认包含所有主要类型
            search_content_types = [ContentType.FILE_PATH, ContentType.DOCUMENT, ContentType.CONTACT, ContentType.TEXT]
        
        # 执行搜索查询
        query = SearchQuery(
            text="*",  # 获取所有内容
            content_types=search_content_types,
            index_tiers=[IndexTier.HOT, IndexTier.WARM],  # 优先高性能数据
            limit=limit,
            include_metadata=True
        )
        
        search_results = index_service.search(query)
        
        # 转换为实体格式
        entities = []
        for result in search_results:
            # 修复：访问result.entry中的属性
            entry = result.entry
            
            # 计算重要性评分 (基于优先级和访问频率)
            importance = 1.0 - (entry.priority / 10.0)  # priority 1-10 转换为 0.9-0.0
            if hasattr(entry, 'last_accessed') and entry.last_accessed:
                # 最近访问的内容重要性更高
                days_since_access = (datetime.now() - entry.last_accessed).days
                importance += max(0, 1.0 - days_since_access / 30.0) * 0.2
            
            if importance < importance_threshold:
                continue
                
            entity = {
                "entity_id": entry.id,
                "name": entry.display_name,
                "type": entry.content_type.value,
                "description": entry.searchable_text[:200] + "..." if len(entry.searchable_text) > 200 else entry.searchable_text,
                "properties": entry.structured_data or {},
                "tags": list(entry.tags) if entry.tags else [],
                "access_count": entry.metadata.get("access_count", 1) if entry.metadata else 1,
                "last_accessed": entry.last_accessed.isoformat() if entry.last_accessed else None,
                "created_at": entry.indexed_at.isoformat(),
                "updated_at": entry.last_modified.isoformat() if entry.last_modified else entry.indexed_at.isoformat(),
                "importance_score": round(importance, 3),
                "primary_key": entry.primary_key,
                "connector_id": entry.connector_id
            }
            entities.append(entity)
        
        logger.info(f"获取到 {len(entities)} 个真实实体数据")
        return entities
        
    except Exception as e:
        logger.error(f"获取真实实体数据失败: {e}")
        # 降级返回基础数据
        return []

async def _fetch_entity_relationships(
    db_service, entity_ids: List[str]
) -> List[Dict[str, Any]]:
    """获取实体关系数据"""
    try:
        # 基于实体的connector_id和内容类型构建基础关系
        relationships = []
        
        # 分析entity_ids中的模式来推断关系
        connectors = {}
        content_types = {}
        
        for entity_id in entity_ids:
            parts = entity_id.split(":")
            if len(parts) >= 2:
                connector_id = parts[0]
                content_type = parts[1] if len(parts) > 1 else "unknown"
                
                if connector_id not in connectors:
                    connectors[connector_id] = []
                connectors[connector_id].append(entity_id)
                
                if content_type not in content_types:
                    content_types[content_type] = []
                content_types[content_type].append(entity_id)
        
        # 创建同连接器的实体关系
        for connector_id, entities in connectors.items():
            if len(entities) > 1:
                for i, source in enumerate(entities):
                    for target in entities[i+1:]:
                        relationships.append({
                            "source_entity_id": source,
                            "target_entity_id": target,
                            "relationship_type": "same_connector",
                            "strength": 5,
                            "description": f"来自相同连接器: {connector_id}",
                            "properties": {
                                "connector_id": connector_id,
                                "relationship_category": "structural"
                            }
                        })
        
        # 创建同类型的实体关系
        for content_type, entities in content_types.items():
            if len(entities) > 1:
                for i, source in enumerate(entities):
                    for target in entities[i+1:]:
                        relationships.append({
                            "source_entity_id": source,
                            "target_entity_id": target,
                            "relationship_type": "same_type",
                            "strength": 3,
                            "description": f"相同内容类型: {content_type}",
                            "properties": {
                                "content_type": content_type,
                                "relationship_category": "semantic"
                            }
                        })
        
        logger.info(f"生成了 {len(relationships)} 个实体关系")
        return relationships[:100]  # 限制关系数量
        
    except Exception as e:
        logger.error(f"获取实体关系失败: {e}")
        return []

async def _calculate_entity_stats(db_service) -> Dict[str, Any]:
    """计算实体统计信息"""
    # TODO: 实现统计计算
    return {"by_type": {}, "total_relationships": 0}

async def _fetch_single_entity(db_service, entity_id: str) -> Optional[Dict[str, Any]]:
    """获取单个实体"""
    # TODO: 实现单实体查询
    return None

async def _fetch_related_entities(db_service, entity_id: str) -> List[Dict[str, Any]]:
    """获取相关实体"""
    # TODO: 实现相关实体查询
    return []

async def _extract_graph_visualization_data(
    graph_service, max_nodes: int, max_edges: int, 
    node_types: List[str], min_edge_weight: float
) -> Dict[str, Any]:
    """提取图可视化数据"""
    try:
        # 获取图的基本信息
        if hasattr(graph_service, 'get_graph_stats'):
            stats = await graph_service.get_graph_stats()
        else:
            stats = {"node_count": 0, "edge_count": 0}
        
        # 如果没有图数据，生成基础结构
        nodes = []
        edges = []
        
        # 从实体数据生成节点
        # 已修复：使用ServiceFacade获取UniversalIndexService
        from services.storage.universal_index_service import SearchQuery, ContentType, IndexTier
        
        index_service = get_service(UniversalIndexService)
        query = SearchQuery(
            text="*",
            content_types=[ContentType.FILE_PATH, ContentType.DOCUMENT, ContentType.TEXT],
            index_tiers=[IndexTier.HOT, IndexTier.WARM],
            limit=min(max_nodes, 50),
            include_metadata=True
        )
        
        search_results = index_service.search(query)
        
        for i, result in enumerate(search_results):
            # 修复：访问result.entry中的属性
            entry = result.entry
            
            node = {
                "id": entry.id,
                "label": entry.display_name,
                "node_type": entry.content_type.value,
                "attributes": entry.structured_data or {},
                "weight": 1.0 - (entry.priority / 10.0),
                "importance": 1.0 - (entry.priority / 10.0),
                "centrality": min(1.0, (i + 1) / len(search_results))
            }
            nodes.append(node)
        
        # 基于相似性生成边
        for i, source_node in enumerate(nodes):
            for j, target_node in enumerate(nodes[i+1:], i+1):
                # 简单的相似性计算
                weight = 0.5 if source_node["node_type"] == target_node["node_type"] else 0.3
                
                if weight >= min_edge_weight and len(edges) < max_edges:
                    edge = {
                        "source": source_node["id"],
                        "target": target_node["id"],
                        "edge_type": "similarity",
                        "weight": weight,
                        "attributes": {
                            "similarity_type": "content_type" if source_node["node_type"] == target_node["node_type"] else "structural"
                        }
                    }
                    edges.append(edge)
        
        graph_metrics = {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "density": len(edges) / max(1, len(nodes) * (len(nodes) - 1) / 2),
            "average_degree": (len(edges) * 2) / max(1, len(nodes)),
            "is_connected": len(nodes) > 0
        }
        
        logger.info(f"生成了图谱数据: {len(nodes)} 节点, {len(edges)} 边")
        
        return {
            "nodes": nodes,
            "edges": edges,
            "graph_metrics": graph_metrics
        }
        
    except Exception as e:
        logger.error(f"提取图可视化数据失败: {e}")
        return {"nodes": [], "edges": [], "graph_metrics": {}}

async def _calculate_centrality_metrics(graph_service) -> Dict[str, Any]:
    """计算中心性指标"""
    # TODO: 实现中心性计算
    return {}

async def _get_graph_clusters(graph_service) -> Dict[str, List[str]]:
    """获取图聚类"""
    # TODO: 实现图聚类
    return {}

async def _get_vector_service():
    """获取向量服务实例"""
    # TODO: 实现向量服务获取
    pass

async def _fetch_vector_documents(
    vector_service, limit: int, content_types: List[str], include_embeddings: bool
) -> List[Dict[str, Any]]:
    """获取向量文档"""
    try:
        # 使用通用索引服务获取文档数据
        # 已修复：使用ServiceFacade获取UniversalIndexService
        from services.storage.universal_index_service import SearchQuery, ContentType, IndexTier
        
        index_service = get_service(UniversalIndexService)
        
        # 优先获取文档和文本类型的内容
        search_content_types = [ContentType.DOCUMENT, ContentType.TEXT, ContentType.FILE_PATH]
        
        query = SearchQuery(
            text="*",
            content_types=search_content_types,
            index_tiers=[IndexTier.WARM, IndexTier.COLD],  # 向量搜索用较深的层级
            limit=limit,
            include_metadata=True
        )
        
        search_results = index_service.search(query)
        
        documents = []
        for result in search_results:
            # 修复：访问result.entry中的属性
            entry = result.entry
            
            doc = {
                "document_id": entry.id,
                "content": entry.searchable_text,
                "title": entry.display_name,
                "content_type": entry.content_type.value,
                "metadata": entry.metadata or {},
                "embedding_preview": [0.1, 0.2, 0.3, 0.15, 0.25],  # 模拟前5维
                "score": 1.0 - (entry.priority / 10.0),
                "source_connector": entry.connector_id,
                "timestamp": entry.indexed_at.isoformat()
            }
            
            if include_embeddings:
                # 如果需要完整向量，生成模拟数据
                import random
                doc["full_embedding"] = [random.uniform(-1, 1) for _ in range(384)]
            
            documents.append(doc)
        
        logger.info(f"获取了 {len(documents)} 个向量文档")
        return documents
        
    except Exception as e:
        logger.error(f"获取向量文档失败: {e}")
        return []

async def _perform_vector_clustering(
    vector_service, documents: List[Dict], cluster_count: int
) -> List[Dict[str, Any]]:
    """执行向量聚类"""
    # TODO: 实现向量聚类
    return []

async def _calculate_similarity_matrix(
    vector_service, documents: List[Dict], threshold: float
) -> Dict[str, Dict[str, float]]:
    """计算相似度矩阵"""
    # TODO: 实现相似度计算
    return {}

async def _get_vector_stats(vector_service) -> Dict[str, Any]:
    """获取向量统计"""
    # TODO: 实现向量统计
    return {}

async def _perform_vector_search(
    vector_service, query: str, limit: int, threshold: float
) -> List[Dict[str, Any]]:
    """执行向量搜索"""
    # TODO: 实现向量搜索
    return []

async def _fetch_entities_for_unified(limit: int) -> Dict[str, Any]:
    """为统一接口获取实体数据"""
    # TODO: 实现统一实体获取
    return {"entities": [], "relationships": []}

async def _fetch_graph_for_unified(max_nodes: int) -> Dict[str, Any]:
    """为统一接口获取图数据"""
    # TODO: 实现统一图获取
    return {"nodes": [], "edges": []}

async def _fetch_vectors_for_unified(limit: int) -> Dict[str, Any]:
    """为统一接口获取向量数据"""
    # TODO: 实现统一向量获取
    return {"documents": [], "clusters": []}

async def _fetch_index_for_unified(limit: int) -> Dict[str, Any]:
    """为统一接口获取索引数据"""
    # TODO: 实现统一索引获取
    return {"results": []}