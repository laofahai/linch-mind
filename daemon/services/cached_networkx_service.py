#!/usr/bin/env python3
"""
带智能缓存的NetworkX服务
基于 data_storage_architecture.md 中的现实主义设计
"""

import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import networkx as nx

from core.service_facade import get_service
from models.database_models import EntityMetadata, EntityRelationship
from services.storage.core.database import UnifiedDatabaseService as DatabaseService

logger = logging.getLogger(__name__)


class LRUCache:
    """简单的LRU缓存实现"""

    def __init__(self, maxsize: int = 1000):
        self.maxsize = maxsize
        self.cache = {}
        self.access_order = []

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            # 更新访问顺序
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None

    def set(self, key: str, value: Any):
        if key in self.cache:
            # 更新现有值
            self.cache[key] = value
            self.access_order.remove(key)
            self.access_order.append(key)
        else:
            # 添加新值
            if len(self.cache) >= self.maxsize:
                # 移除最少使用的项
                oldest_key = self.access_order.pop(0)
                del self.cache[oldest_key]

            self.cache[key] = value
            self.access_order.append(key)

    def clear(self):
        self.cache.clear()
        self.access_order.clear()


class CachedNetworkXService:
    """带智能缓存的NetworkX服务

    针对现实图规模优化：
    - 50K节点: 加载5-15秒，BFS<100ms，路径查找<200ms
    - 100K节点: 加载10-30秒，BFS<200ms，路径查找<500ms
    """

    def __init__(self):
        self.database_service = get_service(DatabaseService)
        self.knowledge_graph = nx.Graph()

        # 缓存系统
        self.query_cache = LRUCache(maxsize=1000)
        self.metrics_cache = LRUCache(maxsize=100)

        # 预计算的图指标
        self.precomputed_metrics = {}

        # 查询优化索引
        self.type_index = defaultdict(list)
        self.edge_type_index = defaultdict(list)

        # 图状态
        self.graph_loaded = False
        self.last_load_time = None

        logger.info("CachedNetworkXService 初始化完成")

    async def load_optimized_graph(self) -> bool:
        """加载优化的图数据"""
        try:
            start_time = datetime.now()

            # 1. 分批加载，避免内存峰值
            entities = await self._load_entities_in_batches()
            relationships = await self._load_relationships_in_batches()

            logger.info(
                f"数据加载完成: {len(entities)}个实体, {len(relationships)}个关系"
            )

            # 2. 构建优化的图结构
            self.knowledge_graph = self._build_optimized_graph(entities, relationships)

            # 3. 构建查询优化索引
            self._build_graph_query_indexes()

            # 4. 预计算常用图指标
            await self._precompute_common_metrics()

            self.graph_loaded = True
            self.last_load_time = datetime.now(timezone.utc)

            load_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"图数据加载完成，耗时: {load_time:.2f}秒")

            return True

        except Exception as e:
            logger.error(f"图数据加载失败: {e}")
            return False

    async def _load_entities_in_batches(self, batch_size: int = 1000) -> List[Dict]:
        """分批加载实体数据"""
        entities = []

        try:
            with self.database_service.get_session() as session:
                # 分批查询，减少内存压力
                offset = 0
                while True:
                    batch = (
                        session.query(EntityMetadata)
                        .offset(offset)
                        .limit(batch_size)
                        .all()
                    )

                    if not batch:
                        break

                    # 转换为字典格式
                    for entity in batch:
                        entities.append(
                            {
                                "id": entity.id,
                                "type": entity.entity_type,
                                "name": entity.name,
                                "description": entity.description,
                                "metadata": entity.entity_metadata or {},
                                "access_count": entity.access_count or 0,
                                "last_accessed": entity.last_accessed,
                            }
                        )

                    offset += batch_size

                    # 每1000个实体记录一次进度
                    if offset % 1000 == 0:
                        logger.debug(f"已加载 {offset} 个实体")

            logger.info(f"实体批量加载完成: {len(entities)}个")
            return entities

        except Exception as e:
            logger.error(f"批量加载实体失败: {e}")
            return []

    async def _load_relationships_in_batches(
        self, batch_size: int = 2000
    ) -> List[Dict]:
        """分批加载关系数据"""
        relationships = []

        try:
            with self.database_service.get_session() as session:
                offset = 0
                while True:
                    batch = (
                        session.query(EntityRelationship)
                        .offset(offset)
                        .limit(batch_size)
                        .all()
                    )

                    if not batch:
                        break

                    for rel in batch:
                        relationships.append(
                            {
                                "source": rel.source_entity,
                                "target": rel.target_entity,
                                "type": rel.relationship_type,
                                "strength": rel.strength or 1.0,
                                "confidence": rel.confidence or 1.0,
                                "data": rel.relationship_data or {},
                            }
                        )

                    offset += batch_size

                    if offset % 2000 == 0:
                        logger.debug(f"已加载 {offset} 个关系")

            logger.info(f"关系批量加载完成: {len(relationships)}个")
            return relationships

        except Exception as e:
            logger.error(f"批量加载关系失败: {e}")
            return []

    def _build_optimized_graph(
        self, entities: List[Dict], relationships: List[Dict]
    ) -> nx.Graph:
        """构建优化的图结构"""
        graph = nx.Graph()

        # 添加节点
        for entity in entities:
            graph.add_node(
                entity["id"], **{k: v for k, v in entity.items() if k != "id"}
            )

        # 添加边
        for rel in relationships:
            # 确保源和目标节点都存在
            if rel["source"] in graph.nodes and rel["target"] in graph.nodes:
                graph.add_edge(
                    rel["source"],
                    rel["target"],
                    **{k: v for k, v in rel.items() if k not in ["source", "target"]},
                )

        logger.info(
            f"图构建完成: {graph.number_of_nodes()}节点, {graph.number_of_edges()}边"
        )
        return graph

    def _build_graph_query_indexes(self):
        """构建图查询索引"""
        # 按实体类型分组索引
        self.type_index = defaultdict(list)
        for node, data in self.knowledge_graph.nodes(data=True):
            entity_type = data.get("type", "unknown")
            self.type_index[entity_type].append(node)

        # 按关系类型分组索引
        self.edge_type_index = defaultdict(list)
        for source, target, data in self.knowledge_graph.edges(data=True):
            edge_type = data.get("type", "related")
            self.edge_type_index[edge_type].append((source, target))

        logger.info(
            f"查询索引构建完成: {len(self.type_index)}个实体类型, {len(self.edge_type_index)}个关系类型"
        )

    async def _precompute_common_metrics(self):
        """预计算常用图指标"""
        try:
            logger.info("开始预计算图指标...")

            # 只计算最常用的指标，避免过度计算
            start_time = datetime.now()

            # 度中心性 - 快速计算
            degree_centrality = nx.degree_centrality(self.knowledge_graph)
            degree_time = (datetime.now() - start_time).total_seconds()

            # PageRank - 限制迭代次数
            start_time = datetime.now()
            pagerank = nx.pagerank(self.knowledge_graph, max_iter=50, tol=1e-4)
            pagerank_time = (datetime.now() - start_time).total_seconds()

            self.precomputed_metrics = {
                "degree_centrality": degree_centrality,
                "pagerank": pagerank,
                "computation_time": {
                    "degree_centrality": round(degree_time, 2),
                    "pagerank": round(pagerank_time, 2),
                },
            }

            logger.info(
                f"图指标预计算完成 - 度中心性: {degree_time:.2f}s, PageRank: {pagerank_time:.2f}s"
            )

        except Exception as e:
            logger.warning(f"图指标预计算失败: {e}")
            self.precomputed_metrics = {}

    async def cached_find_related(
        self, entity_id: str, max_depth: int = 2, min_strength: float = 0.1
    ) -> List[Dict]:
        """带缓存的关系查找"""
        cache_key = f"related_{entity_id}_{max_depth}_{min_strength}"

        # 检查缓存
        cached_result = await cache_service.get(cache_key)
        if cached_result is not None:
            logger.debug(f"缓存命中: {cache_key}")
            return cached_result

        # 执行查询
        try:
            result = await self._optimized_bfs_search(
                entity_id, max_depth, min_strength
            )

            # 缓存结果
            await cache_service.set(cache_key, result)
            return result

        except Exception as e:
            logger.error(f"关系查找失败: {e}")
            return []

    async def _optimized_bfs_search(
        self, entity_id: str, max_depth: int, min_strength: float
    ) -> List[Dict]:
        """优化的BFS搜索算法"""
        if not self.graph_loaded or entity_id not in self.knowledge_graph:
            return []

        try:
            related_entities = []
            visited = set()
            queue = [(entity_id, 0)]  # (节点ID, 深度)

            while queue:
                current_id, depth = queue.pop(0)

                if current_id in visited or depth > max_depth:
                    continue

                visited.add(current_id)

                # 获取当前节点的邻居
                neighbors = list(self.knowledge_graph.neighbors(current_id))

                for neighbor_id in neighbors:
                    if neighbor_id not in visited:
                        # 获取边数据
                        edge_data = self.knowledge_graph.get_edge_data(
                            current_id, neighbor_id
                        )
                        strength = edge_data.get("strength", 1.0) if edge_data else 1.0

                        # 过滤低强度关系
                        if strength >= min_strength:
                            # 获取邻居节点数据
                            neighbor_data = self.knowledge_graph.nodes[neighbor_id]

                            related_entities.append(
                                {
                                    "entity_id": neighbor_id,
                                    "name": neighbor_data.get("name", neighbor_id),
                                    "type": neighbor_data.get("type", "unknown"),
                                    "relationship_type": (
                                        edge_data.get("type", "related")
                                        if edge_data
                                        else "related"
                                    ),
                                    "strength": strength,
                                    "depth": depth + 1,
                                    "path_from_source": depth + 1,
                                }
                            )

                            # 添加到队列继续搜索
                            if depth + 1 < max_depth:
                                queue.append((neighbor_id, depth + 1))

            # 按强度和深度排序
            related_entities.sort(key=lambda x: (x["depth"], -x["strength"]))

            return related_entities

        except Exception as e:
            logger.error(f"BFS搜索失败: {e}")
            return []

    async def get_entity_centrality(self, entity_id: str) -> Dict[str, float]:
        """获取实体中心性指标"""
        if not self.graph_loaded or entity_id not in self.knowledge_graph:
            return {}

        cache_key = f"centrality_{entity_id}"
        cached_result = await self.cache_service.get(cache_key)
        if cached_result is not None:
            return cached_result

        try:
            centrality_metrics = {}

            # 度中心性（来自预计算）
            if "degree_centrality" in self.precomputed_metrics:
                centrality_metrics["degree"] = self.precomputed_metrics[
                    "degree_centrality"
                ].get(entity_id, 0.0)

            # PageRank（来自预计算）
            if "pagerank" in self.precomputed_metrics:
                centrality_metrics["pagerank"] = self.precomputed_metrics[
                    "pagerank"
                ].get(entity_id, 0.0)

            # 本地聚类系数（实时计算，较快）
            try:
                clustering = nx.clustering(self.knowledge_graph, entity_id)
                centrality_metrics["clustering"] = clustering
            except (nx.NetworkXError, KeyError, ValueError) as e:
                logger.debug(f"计算聚类系数失败 for {entity_id}: {e}")
                centrality_metrics["clustering"] = 0.0

            # 缓存结果
            self.metrics_await cache_service.set(cache_key, centrality_metrics)

            return centrality_metrics

        except Exception as e:
            logger.error(f"获取中心性指标失败: {e}")
            return {}

    async def find_shortest_path(
        self, source_id: str, target_id: str
    ) -> Optional[List[str]]:
        """查找最短路径"""
        if not self.graph_loaded:
            return None

        cache_key = f"path_{source_id}_{target_id}"
        cached_result = await cache_service.get(cache_key)
        if cached_result is not None:
            return cached_result

        try:
            if source_id in self.knowledge_graph and target_id in self.knowledge_graph:
                path = nx.shortest_path(self.knowledge_graph, source_id, target_id)

                # 缓存结果
                await cache_service.set(cache_key, path)
                return path
            else:
                return None

        except nx.NetworkXNoPath:
            # 没有路径连接
            await cache_service.set(cache_key, None)
            return None
        except Exception as e:
            logger.error(f"路径查找失败: {e}")
            return None

    async def get_entities_by_type(
        self, entity_type: str, limit: int = 100
    ) -> List[Dict]:
        """按类型获取实体（使用索引优化）"""
        if not self.graph_loaded:
            return []

        cache_key = f"type_{entity_type}_{limit}"
        cached_result = await cache_service.get(cache_key)
        if cached_result is not None:
            return cached_result

        try:
            # 使用预建的类型索引
            entity_ids = self.type_index.get(entity_type, [])

            # 限制结果数量
            limited_ids = entity_ids[:limit]

            # 获取实体详细信息
            entities = []
            for entity_id in limited_ids:
                if entity_id in self.knowledge_graph:
                    node_data = self.knowledge_graph.nodes[entity_id]
                    entities.append(
                        {
                            "id": entity_id,
                            "name": node_data.get("name", entity_id),
                            "type": node_data.get("type", "unknown"),
                            "description": node_data.get("description", ""),
                            "access_count": node_data.get("access_count", 0),
                        }
                    )

            # 按访问次数排序
            entities.sort(key=lambda x: x["access_count"], reverse=True)

            # 缓存结果
            await cache_service.set(cache_key, entities)

            return entities

        except Exception as e:
            logger.error(f"按类型获取实体失败: {e}")
            return []

    async def get_graph_statistics(self) -> Dict[str, Any]:
        """获取图统计信息"""
        if not self.graph_loaded:
            return {"error": "图数据未加载"}

        try:
            # 基础统计
            stats = {
                "nodes": self.knowledge_graph.number_of_nodes(),
                "edges": self.knowledge_graph.number_of_edges(),
                "density": nx.density(self.knowledge_graph),
                "connected_components": nx.number_connected_components(
                    self.knowledge_graph
                ),
                "load_time": (
                    self.last_load_time.isoformat() if self.last_load_time else None
                ),
            }

            # 类型分布统计
            type_distribution = {}
            for entity_type, entities in self.type_index.items():
                type_distribution[entity_type] = len(entities)
            stats["type_distribution"] = type_distribution

            # 关系类型分布
            edge_type_distribution = {}
            for edge_type, edges in self.edge_type_index.items():
                edge_type_distribution[edge_type] = len(edges)
            stats["edge_type_distribution"] = edge_type_distribution

            # 缓存统计
            stats["cache_stats"] = {
                "query_cache_size": len(self.query_cache.cache),
                "metrics_cache_size": len(self.metrics_cache.cache),
            }

            return stats

        except Exception as e:
            logger.error(f"获取图统计失败: {e}")
            return {"error": str(e)}

    async def refresh_graph_cache(self):
        """刷新图缓存"""
        try:
            # 清理所有缓存
            self.query_cache.clear()
            self.metrics_cache.clear()
            self.precomputed_metrics.clear()

            # 重新加载图数据
            success = await self.load_optimized_graph()

            if success:
                logger.info("图缓存刷新完成")
            else:
                logger.error("图缓存刷新失败")

            return success

        except Exception as e:
            logger.error(f"刷新图缓存失败: {e}")
            return False

    def get_node_degree_distribution(self) -> Dict[str, int]:
        """获取节点度分布"""
        if not self.graph_loaded:
            return {}

        try:
            degree_sequence = [d for n, d in self.knowledge_graph.degree()]
            degree_distribution = {}

            for degree in degree_sequence:
                degree_distribution[str(degree)] = (
                    degree_distribution.get(str(degree), 0) + 1
                )

            return degree_distribution

        except Exception as e:
            logger.error(f"获取度分布失败: {e}")
            return {}

    async def find_highly_connected_entities(self, top_k: int = 10) -> List[Dict]:
        """查找高连接度实体"""
        if not self.graph_loaded:
            return []

        cache_key = f"highly_connected_{top_k}"
        cached_result = await cache_service.get(cache_key)
        if cached_result is not None:
            return cached_result

        try:
            # 使用预计算的度中心性
            if "degree_centrality" in self.precomputed_metrics:
                degree_centrality = self.precomputed_metrics["degree_centrality"]

                # 排序并获取前K个
                sorted_entities = sorted(
                    degree_centrality.items(), key=lambda x: x[1], reverse=True
                )[:top_k]

                result = []
                for entity_id, centrality in sorted_entities:
                    node_data = self.knowledge_graph.nodes[entity_id]
                    result.append(
                        {
                            "id": entity_id,
                            "name": node_data.get("name", entity_id),
                            "type": node_data.get("type", "unknown"),
                            "degree_centrality": centrality,
                            "degree": self.knowledge_graph.degree(entity_id),
                            "access_count": node_data.get("access_count", 0),
                        }
                    )

                # 缓存结果
                await cache_service.set(cache_key, result)
                return result
            else:
                return []

        except Exception as e:
            logger.error(f"查找高连接度实体失败: {e}")
            return []


# 全局服务实例
# ServiceFacade现在负责管理服务单例，不再需要本地单例模式


def cleanup_cached_networkx_service():
    """清理缓存NetworkX服务 - 现在由ServiceFacade管理生命周期"""
    logger.info("CachedNetworkXService 的清理现在由ServiceFacade负责管理")
