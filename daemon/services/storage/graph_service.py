#!/usr/bin/env python3
"""
NetworkX图数据库服务 - 知识图谱核心引擎
支持35K-130K实体，70K-400K关系的大规模图计算
"""

import asyncio
import logging
import pickle
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx

from services.security.selective_encrypted_storage import (
    get_selective_encrypted_storage,
)

logger = logging.getLogger(__name__)


@dataclass
class GraphMetrics:
    """图数据库性能指标"""

    node_count: int
    edge_count: int
    avg_degree: float
    clustering_coefficient: float
    density: float
    memory_usage_mb: float
    last_updated: datetime


@dataclass
class EntityNode:
    """图中的实体节点"""

    id: str
    entity_type: str
    name: str
    attributes: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class RelationshipEdge:
    """图中的关系边"""

    source: str
    target: str
    relationship_type: str
    strength: float
    confidence: float
    attributes: Dict[str, Any]


class GraphService:
    """NetworkX图数据库服务 - 知识图谱的核心引擎"""

    def __init__(self, data_dir: Path, max_workers: int = 4, enable_cache: bool = True):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 图存储
        self.graph = nx.MultiDiGraph()  # 支持多重有向图
        self.graph_file = self.data_dir / "knowledge_graph.pkl"

        # 选择性加密存储
        self.selective_storage = get_selective_encrypted_storage()

        # 性能优化
        self.max_workers = max_workers
        self.enable_cache = enable_cache
        self._cache = {} if enable_cache else None
        self._cache_ttl = 300  # 5分钟缓存TTL
        self._cache_timestamps = {}

        # 统计信息
        self._metrics = GraphMetrics(
            node_count=0,
            edge_count=0,
            avg_degree=0.0,
            clustering_coefficient=0.0,
            density=0.0,
            memory_usage_mb=0.0,
            last_updated=datetime.utcnow(),
        )

        # 线程池用于计算密集型操作
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    async def initialize(self) -> bool:
        """初始化图服务"""
        try:
            # 尝试加载现有图数据 - 使用选择性加密存储
            loaded_graph = await self._load_graph_with_encryption()
            if loaded_graph is not None:
                self.graph = loaded_graph
                logger.info(
                    f"加载图数据成功: {self.graph.number_of_nodes()} 节点, {self.graph.number_of_edges()} 边"
                )
            else:
                logger.info("初始化空图数据库")

            await self._update_metrics()
            return True

        except Exception as e:
            logger.error(f"图服务初始化失败: {e}")
            return False

    async def close(self):
        """关闭图服务"""
        try:
            await self.save_graph()
            self._executor.shutdown(wait=True)
            logger.info("图服务已关闭")
        except Exception as e:
            logger.error(f"图服务关闭失败: {e}")

    # === 节点操作 ===

    async def add_entity(self, entity: EntityNode) -> bool:
        """添加实体节点"""
        try:
            self.graph.add_node(
                entity.id,
                entity_type=entity.entity_type,
                name=entity.name,
                attributes=entity.attributes,
                metadata=entity.metadata,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            self._invalidate_cache()
            logger.debug(f"添加实体节点: {entity.id}")
            return True

        except Exception as e:
            logger.error(f"添加实体节点失败 [{entity.id}]: {e}")
            return False

    async def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """更新实体节点"""
        try:
            if not self.graph.has_node(entity_id):
                logger.warning(f"实体节点不存在: {entity_id}")
                return False

            # 更新节点属性
            node_data = self.graph.nodes[entity_id]
            node_data.update(updates)
            node_data["updated_at"] = datetime.utcnow()

            self._invalidate_cache()
            logger.debug(f"更新实体节点: {entity_id}")
            return True

        except Exception as e:
            logger.error(f"更新实体节点失败 [{entity_id}]: {e}")
            return False

    async def remove_entity(self, entity_id: str) -> bool:
        """删除实体节点及其所有关系"""
        try:
            if not self.graph.has_node(entity_id):
                logger.warning(f"实体节点不存在: {entity_id}")
                return False

            self.graph.remove_node(entity_id)
            self._invalidate_cache()
            logger.debug(f"删除实体节点: {entity_id}")
            return True

        except Exception as e:
            logger.error(f"删除实体节点失败 [{entity_id}]: {e}")
            return False

    async def get_entity(self, entity_id: str) -> Optional[EntityNode]:
        """获取实体节点"""
        try:
            if not self.graph.has_node(entity_id):
                return None

            node_data = self.graph.nodes[entity_id]
            return EntityNode(
                id=entity_id,
                entity_type=node_data.get("entity_type", ""),
                name=node_data.get("name", ""),
                attributes=node_data.get("attributes", {}),
                metadata=node_data.get("metadata", {}),
            )

        except Exception as e:
            logger.error(f"获取实体节点失败 [{entity_id}]: {e}")
            return None

    # === 关系操作 ===

    async def add_relationship(self, relationship: RelationshipEdge) -> bool:
        """添加关系边"""
        try:
            # 确保源和目标节点存在
            if not self.graph.has_node(relationship.source):
                logger.warning(f"源节点不存在: {relationship.source}")
                return False
            if not self.graph.has_node(relationship.target):
                logger.warning(f"目标节点不存在: {relationship.target}")
                return False

            self.graph.add_edge(
                relationship.source,
                relationship.target,
                relationship_type=relationship.relationship_type,
                strength=relationship.strength,
                confidence=relationship.confidence,
                attributes=relationship.attributes,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            self._invalidate_cache()
            logger.debug(f"添加关系: {relationship.source} -> {relationship.target}")
            return True

        except Exception as e:
            logger.error(f"添加关系失败: {e}")
            return False

    async def remove_relationship(
        self, source: str, target: str, relationship_type: Optional[str] = None
    ) -> bool:
        """删除关系边"""
        try:
            if not self.graph.has_edge(source, target):
                logger.warning(f"关系不存在: {source} -> {target}")
                return False

            if relationship_type:
                # 删除特定类型的关系
                edges_to_remove = []
                if self.graph.has_edge(source, target):
                    edge_data = self.graph.get_edge_data(source, target)
                    for key, data in edge_data.items():
                        if data.get("relationship_type") == relationship_type:
                            edges_to_remove.append(key)

                for key in edges_to_remove:
                    self.graph.remove_edge(source, target, key)
            else:
                # 删除所有关系
                self.graph.remove_edge(source, target)

            self._invalidate_cache()
            logger.debug(f"删除关系: {source} -> {target}")
            return True

        except Exception as e:
            logger.error(f"删除关系失败: {e}")
            return False

    # === 图查询操作 ===

    async def find_neighbors(
        self,
        entity_id: str,
        max_depth: int = 1,
        relationship_filter: Optional[List[str]] = None,
    ) -> List[str]:
        """查找邻居节点"""
        cache_key = f"neighbors_{entity_id}_{max_depth}_{relationship_filter}"

        if self._is_cached(cache_key):
            return self._get_cache(cache_key)

        try:
            if not self.graph.has_node(entity_id):
                return []

            neighbors = set()
            current_level = {entity_id}

            for _depth in range(max_depth):
                next_level = set()
                for node in current_level:
                    # 出边邻居
                    for neighbor in self.graph.successors(node):
                        if self._filter_relationship(
                            node, neighbor, relationship_filter
                        ):
                            neighbors.add(neighbor)
                            next_level.add(neighbor)

                    # 入边邻居
                    for neighbor in self.graph.predecessors(node):
                        if self._filter_relationship(
                            neighbor, node, relationship_filter
                        ):
                            neighbors.add(neighbor)
                            next_level.add(neighbor)

                current_level = next_level
                if not current_level:
                    break

            result = list(neighbors)
            self._set_cache(cache_key, result)
            return result

        except Exception as e:
            logger.error(f"查找邻居失败 [{entity_id}]: {e}")
            return []

    async def find_shortest_path(self, source: str, target: str) -> Optional[List[str]]:
        """查找最短路径"""
        cache_key = f"path_{source}_{target}"

        if self._is_cached(cache_key):
            return self._get_cache(cache_key)

        try:
            if not self.graph.has_node(source) or not self.graph.has_node(target):
                return None

            # 将有向图转为无向图进行路径搜索
            undirected = self.graph.to_undirected()
            path = nx.shortest_path(undirected, source, target)

            self._set_cache(cache_key, path)
            return path

        except nx.NetworkXNoPath:
            logger.debug(f"无路径: {source} -> {target}")
            return None
        except Exception as e:
            logger.error(f"查找路径失败: {e}")
            return None

    async def get_subgraph(self, entity_ids: List[str]) -> Dict[str, Any]:
        """获取子图"""
        try:
            # 过滤存在的节点
            existing_nodes = [nid for nid in entity_ids if self.graph.has_node(nid)]

            if not existing_nodes:
                return {"nodes": [], "edges": []}

            subgraph = self.graph.subgraph(existing_nodes)

            # 转换为可序列化格式
            nodes = []
            for node_id in subgraph.nodes():
                node_data = subgraph.nodes[node_id]
                nodes.append(
                    {
                        "id": node_id,
                        "entity_type": node_data.get("entity_type", ""),
                        "name": node_data.get("name", ""),
                        "attributes": node_data.get("attributes", {}),
                        "metadata": node_data.get("metadata", {}),
                    }
                )

            edges = []
            for source, target, edge_data in subgraph.edges(data=True):
                edges.append(
                    {
                        "source": source,
                        "target": target,
                        "relationship_type": edge_data.get("relationship_type", ""),
                        "strength": edge_data.get("strength", 1.0),
                        "confidence": edge_data.get("confidence", 1.0),
                        "attributes": edge_data.get("attributes", {}),
                    }
                )

            return {"nodes": nodes, "edges": edges}

        except Exception as e:
            logger.error(f"获取子图失败: {e}")
            return {"nodes": [], "edges": []}

    # === 图分析操作 ===

    async def calculate_centrality(
        self, algorithm: str = "betweenness"
    ) -> Dict[str, float]:
        """计算节点中心性"""
        cache_key = f"centrality_{algorithm}"

        if self._is_cached(cache_key):
            return self._get_cache(cache_key)

        try:
            loop = asyncio.get_event_loop()

            if algorithm == "betweenness":
                centrality = await loop.run_in_executor(
                    self._executor, nx.betweenness_centrality, self.graph
                )
            elif algorithm == "closeness":
                centrality = await loop.run_in_executor(
                    self._executor, nx.closeness_centrality, self.graph
                )
            elif algorithm == "pagerank":
                centrality = await loop.run_in_executor(
                    self._executor, nx.pagerank, self.graph
                )
            else:
                logger.warning(f"不支持的中心性算法: {algorithm}")
                return {}

            self._set_cache(cache_key, centrality)
            return centrality

        except Exception as e:
            logger.error(f"计算中心性失败 [{algorithm}]: {e}")
            return {}

    async def detect_communities(self) -> Dict[str, int]:
        """检测社区结构"""
        cache_key = "communities"

        if self._is_cached(cache_key):
            return self._get_cache(cache_key)

        try:
            # 转换为无向图进行社区检测
            undirected = self.graph.to_undirected()

            loop = asyncio.get_event_loop()
            communities = await loop.run_in_executor(
                self._executor,
                nx.algorithms.community.greedy_modularity_communities,
                undirected,
            )

            # 将社区结果转换为节点->社区ID的映射
            community_map = {}
            for i, community in enumerate(communities):
                for node in community:
                    community_map[node] = i

            self._set_cache(cache_key, community_map)
            return community_map

        except Exception as e:
            logger.error(f"社区检测失败: {e}")
            return {}

    # === 推荐算法 ===

    async def recommend_entities(
        self,
        entity_id: str,
        max_recommendations: int = 10,
        algorithm: str = "collaborative",
    ) -> List[Tuple[str, float]]:
        """基于图结构的实体推荐"""
        cache_key = f"recommend_{entity_id}_{max_recommendations}_{algorithm}"

        if self._is_cached(cache_key):
            return self._get_cache(cache_key)

        try:
            if not self.graph.has_node(entity_id):
                return []

            if algorithm == "collaborative":
                recommendations = await self._collaborative_filtering(
                    entity_id, max_recommendations
                )
            elif algorithm == "content_based":
                recommendations = await self._content_based_filtering(
                    entity_id, max_recommendations
                )
            elif algorithm == "hybrid":
                recommendations = await self._hybrid_recommendation(
                    entity_id, max_recommendations
                )
            else:
                logger.warning(f"不支持的推荐算法: {algorithm}")
                return []

            self._set_cache(cache_key, recommendations)
            return recommendations

        except Exception as e:
            logger.error(f"实体推荐失败 [{entity_id}]: {e}")
            return []

    async def _collaborative_filtering(
        self, entity_id: str, max_recommendations: int
    ) -> List[Tuple[str, float]]:
        """协同过滤推荐"""
        # 基于图结构的协同过滤
        neighbors = list(self.graph.neighbors(entity_id))
        recommendations = {}

        for neighbor in neighbors:
            # 获取邻居的邻居
            second_level = list(self.graph.neighbors(neighbor))
            for candidate in second_level:
                if candidate != entity_id and candidate not in neighbors:
                    # 计算推荐分数（基于共同邻居数）
                    common_neighbors = len(
                        set(self.graph.neighbors(entity_id))
                        & set(self.graph.neighbors(candidate))
                    )
                    score = common_neighbors / (len(neighbors) + 1)
                    recommendations[candidate] = max(
                        recommendations.get(candidate, 0), score
                    )

        # 排序并返回top-k
        sorted_recommendations = sorted(
            recommendations.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_recommendations[:max_recommendations]

    async def _content_based_filtering(
        self, entity_id: str, max_recommendations: int
    ) -> List[Tuple[str, float]]:
        """基于内容的推荐"""
        if not self.graph.has_node(entity_id):
            return []

        entity_data = self.graph.nodes[entity_id]
        entity_type = entity_data.get("entity_type", "")

        recommendations = {}

        # 查找同类型实体
        for node_id, node_data in self.graph.nodes(data=True):
            if node_id != entity_id and node_data.get("entity_type") == entity_type:
                # 计算相似性分数（简化版本）
                score = 0.5  # 基础相似性分数

                # 如果有共同属性，增加分数
                entity_attrs = entity_data.get("attributes", {})
                candidate_attrs = node_data.get("attributes", {})

                common_keys = set(entity_attrs.keys()) & set(candidate_attrs.keys())
                if common_keys:
                    score += (
                        0.3
                        * len(common_keys)
                        / len(set(entity_attrs.keys()) | set(candidate_attrs.keys()))
                    )

                recommendations[node_id] = score

        sorted_recommendations = sorted(
            recommendations.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_recommendations[:max_recommendations]

    async def _hybrid_recommendation(
        self, entity_id: str, max_recommendations: int
    ) -> List[Tuple[str, float]]:
        """混合推荐算法"""
        collaborative = await self._collaborative_filtering(
            entity_id, max_recommendations * 2
        )
        content_based = await self._content_based_filtering(
            entity_id, max_recommendations * 2
        )

        # 合并两种推荐结果
        hybrid_scores = {}

        for entity, score in collaborative:
            hybrid_scores[entity] = score * 0.6  # 协同过滤权重

        for entity, score in content_based:
            hybrid_scores[entity] = (
                hybrid_scores.get(entity, 0) + score * 0.4
            )  # 内容推荐权重

        sorted_recommendations = sorted(
            hybrid_scores.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_recommendations[:max_recommendations]

    # === 数据持久化 ===

    async def save_graph(self) -> bool:
        """保存图数据到文件 - 使用选择性加密存储"""
        try:
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                self._executor,
                self.selective_storage.save_graph_data,
                self.graph,
                self.graph_file,
            )

            if success:
                # 获取存储信息用于日志
                storage_info = self.selective_storage.get_storage_info(self.graph_file)
                encryption_status = (
                    "加密" if storage_info.get("encryption_enabled") else "明文"
                )
                logger.info(f"图数据已保存: {self.graph_file} ({encryption_status})")

            return success

        except Exception as e:
            logger.error(f"保存图数据失败: {e}")
            return False

    async def _load_graph_with_encryption(self) -> Optional[nx.MultiDiGraph]:
        """加载图数据 - 使用选择性加密存储"""
        try:
            loop = asyncio.get_event_loop()
            graph_data = await loop.run_in_executor(
                self._executor, self.selective_storage.load_graph_data, self.graph_file
            )

            if graph_data is not None:
                # 获取存储信息用于日志
                storage_info = self.selective_storage.get_storage_info(self.graph_file)
                encryption_status = (
                    "加密" if storage_info.get("encryption_enabled") else "明文"
                )
                logger.info(f"图数据加载成功: {self.graph_file} ({encryption_status})")

            return graph_data

        except Exception as e:
            logger.error(f"加载图数据失败: {e}")
            return None

    # 保留原有方法用于向后兼容和迁移
    def _save_graph_sync(self):
        """同步保存图数据 - 原有方法，保留用于兼容"""
        with open(self.graph_file, "wb") as f:
            pickle.dump(self.graph, f, protocol=pickle.HIGHEST_PROTOCOL)

    def _load_graph_sync(self) -> nx.MultiDiGraph:
        """同步加载图数据 - 原有方法，保留用于兼容"""
        with open(self.graph_file, "rb") as f:
            return pickle.load(f)

    async def migrate_to_selective_encryption(self) -> bool:
        """迁移现有图数据到选择性加密存储格式"""
        try:
            # 检查是否需要迁移
            if not self.graph_file.exists():
                logger.info("没有需要迁移的图数据")
                return True

            # 检查是否已经是新格式
            storage_info = self.selective_storage.get_storage_info(self.graph_file)
            if "encryption_enabled" in storage_info:
                logger.info("图数据已经是选择性加密存储格式，无需迁移")
                return True

            logger.info("开始迁移图数据到选择性加密存储格式")

            # 备份原文件路径
            backup_file = self.graph_file.with_suffix(".backup.pkl")

            # 执行迁移
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                self._executor,
                self.selective_storage.migrate_existing_data,
                self.graph_file,
                self.graph_file,
            )

            if success:
                logger.info("图数据迁移成功")
            else:
                logger.error("图数据迁移失败")

            return success

        except Exception as e:
            logger.error(f"图数据迁移失败: {e}")
            return False

    # === 性能监控 ===

    async def get_metrics(self) -> GraphMetrics:
        """获取图数据库性能指标"""
        await self._update_metrics()
        return self._metrics

    async def _update_metrics(self):
        """更新性能指标"""
        try:
            pass

            import psutil

            self._metrics.node_count = self.graph.number_of_nodes()
            self._metrics.edge_count = self.graph.number_of_edges()

            if self._metrics.node_count > 0:
                total_degree = sum(dict(self.graph.degree()).values())
                self._metrics.avg_degree = total_degree / self._metrics.node_count

                # 计算聚类系数（小图才计算，避免性能问题）
                if self._metrics.node_count < 10000:
                    try:
                        # 将multigraph转换为简单图，合并重复边
                        simple_graph = nx.Graph()
                        simple_graph.add_nodes_from(self.graph.nodes())

                        # 添加边，忽略重复边和权重
                        for u, v in self.graph.edges():
                            simple_graph.add_edge(u, v)

                        self._metrics.clustering_coefficient = nx.average_clustering(
                            simple_graph
                        )
                    except Exception as e:
                        logger.warning(f"聚类系数计算失败: {e}")
                        self._metrics.clustering_coefficient = 0.0

                # 计算图密度
                max_edges = self._metrics.node_count * (self._metrics.node_count - 1)
                self._metrics.density = (
                    self._metrics.edge_count / max_edges if max_edges > 0 else 0
                )

            # 内存使用情况
            process = psutil.Process()
            self._metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024

            self._metrics.last_updated = datetime.utcnow()

        except Exception as e:
            logger.error(f"更新指标失败: {e}")

    # === 缓存管理 ===

    def _is_cached(self, key: str) -> bool:
        """检查缓存是否有效"""
        if not self.enable_cache or key not in self._cache:
            return False

        timestamp = self._cache_timestamps.get(key, 0)
        return (datetime.utcnow().timestamp() - timestamp) < self._cache_ttl

    def _get_cache(self, key: str) -> Any:
        """获取缓存值"""
        return self._cache.get(key)

    def _set_cache(self, key: str, value: Any):
        """设置缓存值"""
        if self.enable_cache:
            self._cache[key] = value
            self._cache_timestamps[key] = datetime.utcnow().timestamp()

    def _invalidate_cache(self):
        """清空缓存"""
        if self.enable_cache:
            self._cache.clear()
            self._cache_timestamps.clear()

    def _filter_relationship(
        self, source: str, target: str, relationship_filter: Optional[List[str]]
    ) -> bool:
        """过滤关系类型"""
        if not relationship_filter:
            return True

        if not self.graph.has_edge(source, target):
            return False

        edge_data = self.graph.get_edge_data(source, target)
        for data in edge_data.values():
            if data.get("relationship_type") in relationship_filter:
                return True

        return False


# 全局图服务实例
_graph_service: Optional[GraphService] = None


async def get_graph_service() -> GraphService:
    """获取图服务实例（单例模式）"""
    global _graph_service
    if _graph_service is None:
        from config.core_config import get_storage_config

        storage_config = get_storage_config()

        _graph_service = GraphService(
            data_dir=Path(storage_config.data_directory) / "graph",
            max_workers=storage_config.graph_max_workers,
            enable_cache=storage_config.graph_enable_cache,
        )
        await _graph_service.initialize()

    return _graph_service


async def cleanup_graph_service():
    """清理图服务"""
    global _graph_service
    if _graph_service:
        await _graph_service.close()
        _graph_service = None
