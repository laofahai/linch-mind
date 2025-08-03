from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from pathlib import Path
from typing import List, Dict, Any, Optional
# import chromadb  # TODO: Add when needed
# import networkx as nx  # TODO: Add when needed
# from sentence_transformers import SentenceTransformer  # TODO: Add when needed
from models.database_models import Base, DataItem, Connector, AIRecommendation, GraphNode, GraphRelationship
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


class DatabaseService:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_url = f"sqlite:///{db_path}/linch_mind.db"
        
        # SQLAlchemy 引擎
        self.engine = create_engine(self.db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # 延迟初始化向量和图服务，避免启动时过于耗时
        self.chroma_client = None
        self.collection = None
        # TODO: Replace with networkx when needed
        self.graph = {"nodes": {}, "edges": {}}
        self.embedding_model = None
        
        # 初始化数据库
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("数据库初始化完成")
        
        # 延迟加载图数据
        # self._load_graph_data()
    
    def _load_graph_data(self):
        return  # TODO: Enable when networkx is available
        """从数据库加载图数据到NetworkX"""
        with self.SessionLocal() as session:
            # 加载节点
            nodes = session.query(GraphNode).all()
            for node in nodes:
                self.graph.add_node(node.id, 
                                  type=node.type, 
                                  label=node.label, 
                                  properties=node.properties or {})
            
            # 加载边
            relationships = session.query(GraphRelationship).all()
            for rel in relationships:
                self.graph.add_edge(rel.source_node_id, 
                                  rel.target_node_id,
                                  type=rel.relationship_type,
                                  weight=rel.weight,
                                  properties=rel.properties or {})
        
        logger.info(f"加载图数据: {len(self.graph.nodes)} 节点, {len(self.graph.edges)} 边")
    
    def _init_vector_service(self):
        """延迟初始化向量服务"""
        if self.chroma_client is None:
            logger.info("初始化向量服务...")
            try:
                # chromadb已在模块顶部导入
                chroma_dir = self.db_path / "chromadb"
                chroma_dir.mkdir(parents=True, exist_ok=True)
                
                # TODO: Implement when chromadb is needed
                # self.chroma_client = chromadb.PersistentClient(path=str(chroma_dir))
                # self.collection = self.chroma_client.get_or_create_collection(
                #     name="linch_mind_vectors",
                #     metadata={"hnsw:space": "cosine"}
                # )
                # self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.warning("向量数据库初始化已被跳过 - chromadb未安装")
                logger.info("向量服务初始化完成")
            except ImportError as e:
                logger.error(f"向量服务依赖缺失: {e}")
                logger.error("请运行: pip install chromadb sentence-transformers")
            except Exception as e:
                logger.warning(f"向量服务初始化失败: {e}")
    
    def _init_graph_service(self):
        """延迟初始化图服务"""
        if len(self.graph["nodes"]) == 0:
            logger.info("初始化图服务...")
            self._load_graph_data()
    
    # 基本数据操作
    def save_data_item(self, item_data: dict) -> str:
        """保存数据项"""
        with self.SessionLocal() as session:
            item = DataItem(**item_data)
            session.add(item)
            session.commit()
            
            # 创建向量嵌入（如果向量服务可用）
            try:
                self._create_embedding(item.id, item.content, "data_item")
            except Exception as e:
                logger.debug(f"跳过向量嵌入创建: {e}")
            
            return item.id
    
    def get_data_items(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取数据项"""
        with self.SessionLocal() as session:
            items = session.query(DataItem).order_by(DataItem.timestamp.desc()).limit(limit).all()
            return [self._data_item_to_dict(item) for item in items]
    
    def _data_item_to_dict(self, item: DataItem) -> Dict[str, Any]:
        """转换DataItem到字典"""
        return {
            "id": item.id,
            "content": item.content,
            "source_connector": item.source_connector,
            "timestamp": item.timestamp.isoformat(),
            "file_path": item.file_path,
            "metadata": item.meta_data or {},
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat()
        }
    
    # 图数据操作
    def save_graph_node(self, node_id: str, node_type: str, label: str, 
                       properties: Dict[str, Any] = None, source_data_id: str = None):
        """保存图节点"""
        with self.SessionLocal() as session:
            node = GraphNode(
                id=node_id,
                type=node_type,
                label=label,
                properties=properties,
                source_data_id=source_data_id
            )
            session.merge(node)  # 使用merge而不是add，支持更新
            session.commit()
            
            # 更新NetworkX图
            self.graph.add_node(node_id, 
                              type=node_type, 
                              label=label, 
                              properties=properties or {})
            
            # 创建向量嵌入
            self._create_embedding(node_id, label, "graph_node")
    
    def save_graph_relationship(self, rel_id: str, source_node_id: str, target_node_id: str,
                               relationship_type: str, weight: float = 1.0, 
                               properties: Dict[str, Any] = None):
        """保存图关系"""
        with self.SessionLocal() as session:
            rel = GraphRelationship(
                id=rel_id,
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                relationship_type=relationship_type,
                weight=weight,
                properties=properties
            )
            session.merge(rel)
            session.commit()
            
            # 更新NetworkX图
            self.graph.add_edge(source_node_id, target_node_id,
                              type=relationship_type,
                              weight=weight,
                              properties=properties or {})
    
    def get_graph_nodes(self, node_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取图节点"""
        with self.SessionLocal() as session:
            query = session.query(GraphNode)
            if node_type:
                query = query.filter(GraphNode.type == node_type)
            
            nodes = query.order_by(GraphNode.updated_at.desc()).limit(limit).all()
            return [self._graph_node_to_dict(node) for node in nodes]
    
    def _graph_node_to_dict(self, node: GraphNode) -> Dict[str, Any]:
        """转换GraphNode到字典"""
        return {
            "id": node.id,
            "type": node.type,
            "label": node.label,
            "properties": node.properties or {},
            "created_at": node.created_at.isoformat(),
            "updated_at": node.updated_at.isoformat(),
            "source_data_id": node.source_data_id
        }
    
    def get_graph_relationships(self, source_node_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取图关系"""
        with self.SessionLocal() as session:
            query = session.query(GraphRelationship)
            if source_node_id:
                query = query.filter(GraphRelationship.source_node_id == source_node_id)
            
            relationships = query.order_by(GraphRelationship.created_at.desc()).limit(limit).all()
            return [self._graph_relationship_to_dict(rel) for rel in relationships]
    
    def _graph_relationship_to_dict(self, rel: GraphRelationship) -> Dict[str, Any]:
        """转换GraphRelationship到字典"""
        return {
            "id": rel.id,
            "source_node_id": rel.source_node_id,
            "target_node_id": rel.target_node_id,
            "relationship_type": rel.relationship_type,
            "weight": rel.weight,
            "properties": rel.properties or {},
            "created_at": rel.created_at.isoformat(),
            "updated_at": rel.updated_at.isoformat()
        }
    
    # 向量搜索操作
    def _create_embedding(self, entity_id: str, text: str, entity_type: str):
        """创建文本嵌入"""
        try:
            # 初始化向量服务
            self._init_vector_service()
            
            if self.embedding_model is None or self.collection is None:
                raise Exception("向量服务未初始化")
            
            # 生成向量
            embedding = self.embedding_model.encode(text).tolist()
            
            # 保存到ChromaDB
            self.collection.upsert(
                ids=[f"{entity_type}:{entity_id}"],
                embeddings=[embedding],
                metadatas=[{"entity_id": entity_id, "entity_type": entity_type, "text": text}],
                documents=[text]
            )
        except Exception as e:
            logger.error(f"创建嵌入失败: {e}")
            raise
    
    def search_similar(self, query_text: str, n_results: int = 10, entity_type: str = None) -> List[Dict[str, Any]]:
        """语义搜索"""
        try:
            # 初始化向量服务
            self._init_vector_service()
            
            if self.embedding_model is None or self.collection is None:
                return []
            
            # 生成查询向量
            query_embedding = self.embedding_model.encode(query_text).tolist()
            
            # 准备过滤条件
            where_filter = {}
            if entity_type:
                where_filter = {"entity_type": entity_type}
            
            # 搜索相似项
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter if where_filter else None
            )
            
            # 格式化结果
            formatted_results = []
            if results['ids']:
                for i, doc_id in enumerate(results['ids'][0]):
                    formatted_results.append({
                        "id": doc_id,
                        "score": 1 - results['distances'][0][i],  # 转换距离为相似度
                        "metadata": results['metadatas'][0][i],
                        "document": results['documents'][0][i]
                    })
            
            return formatted_results
        except Exception as e:
            logger.error(f"语义搜索失败: {e}")
            return []
    
    # 图分析操作
    def get_node_neighbors(self, node_id: str, max_depth: int = 2) -> Dict[str, Any]:
        """获取节点的邻居"""
        if node_id not in self.graph:
            return {"neighbors": [], "relationships": []}
        
        # 获取指定深度内的邻居
        neighbors = []
        relationships = []
        
        # BFS遍历
        visited = set()
        queue = [(node_id, 0)]
        visited.add(node_id)
        
        while queue:
            current_node, depth = queue.pop(0)
            if depth >= max_depth:
                continue
                
            # 获取邻居节点
            for neighbor in self.graph.neighbors(current_node):
                if neighbor not in visited:
                    neighbors.append({
                        "id": neighbor,
                        "depth": depth + 1,
                        **self.graph.nodes[neighbor]
                    })
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))
                
                # 记录边关系
                edge_data = self.graph.edges[current_node, neighbor]
                relationships.append({
                    "source": current_node,
                    "target": neighbor,
                    "type": edge_data.get("type", "related"),
                    "weight": edge_data.get("weight", 1.0)
                })
        
        return {"neighbors": neighbors, "relationships": relationships}
    
    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        stats = {}
        
        with self.SessionLocal() as session:
            stats["data_items"] = session.query(DataItem).count()
            stats["graph_nodes"] = session.query(GraphNode).count()
            stats["graph_relationships"] = session.query(GraphRelationship).count()
            stats["recommendations"] = session.query(AIRecommendation).count()
        
        # ChromaDB统计
        try:
            stats["vectors"] = self.collection.count()
        except:
            stats["vectors"] = 0
        
        # NetworkX图统计
        stats["graph_analysis"] = {
            "nodes": len(self.graph.nodes),
            "edges": len(self.graph.edges),
            "density": nx.density(self.graph) if len(self.graph.nodes) > 1 else 0,
            "is_connected": nx.is_connected(self.graph.to_undirected()) if len(self.graph.nodes) > 0 else False
        }
        
        return stats