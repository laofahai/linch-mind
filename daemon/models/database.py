import sqlite3
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from .api_models import DataItem, ConnectorInfo, AIRecommendation


class Database:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            # 基本数据表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS data_items (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    source_connector TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    file_path TEXT,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 连接器配置表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS connectors (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    data_count INTEGER DEFAULT 0,
                    last_update TEXT NOT NULL,
                    config TEXT,
                    error_message TEXT
                )
            ''')
            
            # AI推荐表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS recommendations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    confidence REAL NOT NULL,
                    related_items TEXT,
                    created_at TEXT NOT NULL
                )
            ''')
            
            # 图数据 - 节点表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS graph_nodes (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,           -- 节点类型：person, document, concept, etc.
                    label TEXT NOT NULL,         -- 节点显示名称
                    properties TEXT,             -- JSON格式的节点属性
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    source_data_id TEXT,         -- 关联的源数据ID
                    FOREIGN KEY (source_data_id) REFERENCES data_items(id)
                )
            ''')
            
            # 图数据 - 关系表  
            conn.execute('''
                CREATE TABLE IF NOT EXISTS graph_relationships (
                    id TEXT PRIMARY KEY,
                    source_node_id TEXT NOT NULL,
                    target_node_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,  -- 关系类型：mentions, contains, related_to, etc.
                    weight REAL DEFAULT 1.0,          -- 关系权重
                    properties TEXT,                  -- JSON格式的关系属性
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_node_id) REFERENCES graph_nodes(id),
                    FOREIGN KEY (target_node_id) REFERENCES graph_nodes(id)
                )
            ''')
            
            # 向量数据表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS vectors (
                    id TEXT PRIMARY KEY,
                    entity_id TEXT NOT NULL,     -- 关联的实体ID（可以是data_item或graph_node）
                    entity_type TEXT NOT NULL,   -- 实体类型：data_item, graph_node
                    vector_data BLOB NOT NULL,   -- numpy数组序列化后的向量数据
                    embedding_model TEXT,        -- 使用的embedding模型
                    dimension INTEGER,           -- 向量维度
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引提升查询性能
            conn.execute('CREATE INDEX IF NOT EXISTS idx_data_items_timestamp ON data_items(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_graph_nodes_type ON graph_nodes(type)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_graph_relationships_source ON graph_relationships(source_node_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_graph_relationships_target ON graph_relationships(target_node_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_vectors_entity ON vectors(entity_id, entity_type)')
            
            conn.commit()
    
    def save_data_item(self, item: DataItem):
        """保存数据项"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO data_items 
                (id, content, source_connector, timestamp, file_path, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                item.id,
                item.content,
                item.source_connector,
                item.timestamp.isoformat(),
                item.file_path,
                json.dumps(item.metadata)
            ))
            conn.commit()
    
    def get_data_items(self, limit: int = 100) -> List[DataItem]:
        """获取数据项"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT id, content, source_connector, timestamp, file_path, metadata
                FROM data_items
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            items = []
            for row in cursor.fetchall():
                items.append(DataItem(
                    id=row[0],
                    content=row[1],
                    source_connector=row[2],
                    timestamp=datetime.fromisoformat(row[3]),
                    file_path=row[4],
                    metadata=json.loads(row[5]) if row[5] else {}
                ))
            
            return items
    
    def save_recommendation(self, rec: AIRecommendation):
        """保存推荐"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO recommendations
                (id, title, description, confidence, related_items, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                rec.id,
                rec.title,
                rec.description,
                rec.confidence,
                json.dumps(rec.related_items),
                rec.created_at.isoformat()
            ))
            conn.commit()
    
    def get_recommendations(self, limit: int = 10) -> List[AIRecommendation]:
        """获取推荐"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT id, title, description, confidence, related_items, created_at
                FROM recommendations
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            recommendations = []
            for row in cursor.fetchall():
                recommendations.append(AIRecommendation(
                    id=row[0],
                    title=row[1],
                    description=row[2],
                    confidence=row[3],
                    related_items=json.loads(row[4]) if row[4] else [],
                    created_at=datetime.fromisoformat(row[5])
                ))
            
            return recommendations
    
    # 图数据操作方法
    def save_graph_node(self, node_id: str, node_type: str, label: str, 
                       properties: Dict[str, Any] = None, source_data_id: str = None):
        """保存图节点"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO graph_nodes 
                (id, type, label, properties, source_data_id, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                node_id,
                node_type,
                label,
                json.dumps(properties) if properties else None,
                source_data_id
            ))
            conn.commit()
    
    def save_graph_relationship(self, rel_id: str, source_node_id: str, target_node_id: str,
                               relationship_type: str, weight: float = 1.0, 
                               properties: Dict[str, Any] = None):
        """保存图关系"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO graph_relationships
                (id, source_node_id, target_node_id, relationship_type, weight, properties, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                rel_id,
                source_node_id,
                target_node_id,
                relationship_type,
                weight,
                json.dumps(properties) if properties else None
            ))
            conn.commit()
    
    def get_graph_nodes(self, node_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取图节点"""
        with sqlite3.connect(self.db_path) as conn:
            if node_type:
                cursor = conn.execute('''
                    SELECT id, type, label, properties, created_at, updated_at, source_data_id
                    FROM graph_nodes WHERE type = ?
                    ORDER BY updated_at DESC LIMIT ?
                ''', (node_type, limit))
            else:
                cursor = conn.execute('''
                    SELECT id, type, label, properties, created_at, updated_at, source_data_id
                    FROM graph_nodes
                    ORDER BY updated_at DESC LIMIT ?
                ''', (limit,))
            
            nodes = []
            for row in cursor.fetchall():
                nodes.append({
                    'id': row[0],
                    'type': row[1],
                    'label': row[2],
                    'properties': json.loads(row[3]) if row[3] else {},
                    'created_at': row[4],
                    'updated_at': row[5],
                    'source_data_id': row[6]
                })
            
            return nodes
    
    def get_graph_relationships(self, source_node_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取图关系"""
        with sqlite3.connect(self.db_path) as conn:
            if source_node_id:
                cursor = conn.execute('''
                    SELECT id, source_node_id, target_node_id, relationship_type, weight, properties, created_at
                    FROM graph_relationships WHERE source_node_id = ?
                    ORDER BY created_at DESC LIMIT ?
                ''', (source_node_id, limit))
            else:
                cursor = conn.execute('''
                    SELECT id, source_node_id, target_node_id, relationship_type, weight, properties, created_at
                    FROM graph_relationships
                    ORDER BY created_at DESC LIMIT ?
                ''', (limit,))
            
            relationships = []
            for row in cursor.fetchall():
                relationships.append({
                    'id': row[0],
                    'source_node_id': row[1],
                    'target_node_id': row[2],
                    'relationship_type': row[3],
                    'weight': row[4],
                    'properties': json.loads(row[5]) if row[5] else {},
                    'created_at': row[6]
                })
            
            return relationships
    
    # 向量数据操作方法
    def save_vector(self, vector_id: str, entity_id: str, entity_type: str, 
                   vector_data: np.ndarray, embedding_model: str = None):
        """保存向量数据"""
        with sqlite3.connect(self.db_path) as conn:
            # 将numpy数组序列化为bytes
            vector_bytes = vector_data.tobytes()
            dimension = vector_data.shape[0]
            
            conn.execute('''
                INSERT OR REPLACE INTO vectors
                (id, entity_id, entity_type, vector_data, embedding_model, dimension)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                vector_id,
                entity_id,
                entity_type,
                vector_bytes,
                embedding_model,
                dimension
            ))
            conn.commit()
    
    def get_vector(self, entity_id: str, entity_type: str) -> Optional[np.ndarray]:
        """获取向量数据"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT vector_data, dimension FROM vectors
                WHERE entity_id = ? AND entity_type = ?
            ''', (entity_id, entity_type))
            
            row = cursor.fetchone()
            if row:
                # 从bytes反序列化为numpy数组
                vector_bytes, dimension = row
                vector_data = np.frombuffer(vector_bytes, dtype=np.float32)
                return vector_data.reshape(-1)
            
            return None
    
    def search_similar_vectors(self, query_vector: np.ndarray, entity_type: str = None, 
                              limit: int = 10) -> List[Tuple[str, float]]:
        """搜索相似向量（简单的欧几里德距离，生产环境建议使用专门的向量数据库）"""
        with sqlite3.connect(self.db_path) as conn:
            if entity_type:
                cursor = conn.execute('''
                    SELECT entity_id, vector_data, dimension FROM vectors
                    WHERE entity_type = ?
                ''', (entity_type,))
            else:
                cursor = conn.execute('SELECT entity_id, vector_data, dimension FROM vectors')
            
            similarities = []
            for row in cursor.fetchall():
                entity_id, vector_bytes, dimension = row
                stored_vector = np.frombuffer(vector_bytes, dtype=np.float32)
                
                # 计算余弦相似度
                dot_product = np.dot(query_vector, stored_vector)
                norm_query = np.linalg.norm(query_vector)
                norm_stored = np.linalg.norm(stored_vector)
                
                if norm_query > 0 and norm_stored > 0:
                    similarity = dot_product / (norm_query * norm_stored)
                    similarities.append((entity_id, float(similarity)))
            
            # 按相似度排序并返回top-k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:limit]
    
    def get_database_stats(self) -> Dict[str, int]:
        """获取数据库统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            tables = ['data_items', 'graph_nodes', 'graph_relationships', 'vectors', 'recommendations']
            for table in tables:
                cursor = conn.execute(f'SELECT COUNT(*) FROM {table}')
                stats[table] = cursor.fetchone()[0]
            
            return stats