# Linch Mind 数据存储架构设计

**版本**: 2.0 - 实用主义版  
**状态**: 设计完成  
**创建时间**: 2025-08-04  
**最后更新**: 2025-08-04  
**技术栈**: SQLCipher + ChromaDB + NetworkX + Python

## 1. 概述

Linch Mind作为"隐私至上"的个人AI助手，需要处理用户最敏感的个人数据。本文档设计了一个**实用主义**的数据存储架构，在保证数据安全的前提下，优化性能和开发复杂度。

### 1.1 设计原则

- **安全至上**: 所有敏感数据采用SQLCipher加密存储
- **本地优先**: 100%本地存储，用户完全控制数据
- **轻量高效**: 零配置部署，最小化系统资源占用
- **智能索引**: 支持语义搜索、关系推理、行为分析
- **简化架构**: 避免过度复杂的多层存储设计
- **渐进增强**: 支持从基础功能向高级特性演进

## 2. 存储需求分析

### 2.1 数据类型与敏感性分级

```
🔴 极高敏感 (SECRET) - 必须加密
├── AI对话历史: 用户完整思考过程、价值观
├── 个人知识图谱: 认知指纹、兴趣模型  
├── 跨应用行为: 数字生活轨迹、使用模式
└── 用户生成内容: 笔记、想法、创意

🟡 高敏感 (PRIVATE) - 建议加密
├── 文件内容索引: 工作文档、研究成果
├── 通信数据分析: 邮件语义、社交关系
└── 个人偏好配置: 推荐设置、界面偏好

🟢 中等敏感 (INTERNAL) - 可选加密
├── 系统配置: 连接器设置、API配置
├── 使用统计: 功能使用频率、性能指标
└── 缓存数据: 临时计算结果、预处理数据
```

### 2.2 数据规模预估

```
个人用户典型数据规模:
├── AI对话记录: 1K - 10K 条 (SQLite存储)
├── 知识实体: 5K - 50K 个 (SQLite存储)
├── 实体关系: 10K - 100K 条 (SQLite存储)
├── 文档向量: 1K - 10K 个 (ChromaDB存储)
├── 用户行为: 50K - 500K 条 (SQLite存储)
└── 图数据: 1K - 10K 节点 (NetworkX + SQLite)

性能目标:
├── 查询响应: < 100ms (90%查询)
├── 向量搜索: < 200ms (语义检索)
├── 图算法: < 500ms (关系推理)
└── 数据写入: < 10ms (单条记录)
```

## 3. 存储架构设计

### 3.1 简化的三层架构

```python
# 实用主义存储架构
class LinchMindDataStack:
    """
    三层存储架构 - 简化版本
    避免过度复杂的多层设计
    """
    
    # Layer 1: 主存储层 (SQLCipher)
    primary_storage: SQLCipherDatabase
    
    # Layer 2: 向量搜索层 (ChromaDB)  
    vector_storage: ChromaDatabaseLocal
    
    # Layer 3: 图分析层 (NetworkX + SQLite持久化)
    graph_storage: NetworkXGraphDatabase
```

### 3.2 SQLCipher主存储层 (核心)

**技术选择**: SQLCipher + SQLAlchemy 2.0

**选择理由**:
- ✅ 文件级AES-256加密，安全性经过验证
- ✅ 透明加密，应用层无需特殊处理
- ✅ 成熟的ORM支持，开发效率高
- ✅ 跨平台兼容，支持所有目标设备
- ✅ 性能开销可控 (~15%)
- ✅ 支持完整的SQL功能和事务

**数据模型设计**:

```python
# daemon/models/database_models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class EntityMetadata(Base):
    """实体元数据表 - 知识图谱核心"""
    __tablename__ = "entity_metadata"
    
    id = Column(String, primary_key=True)
    entity_type = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    source_path = Column(String)  # 来源文件路径
    metadata = Column(JSON)       # 扩展属性
    embedding_id = Column(String) # 对应向量ID
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = Column(DateTime)
    
    # 统计信息
    access_count = Column(Integer, default=0)
    relevance_score = Column(Float, default=0.0)

class UserBehavior(Base):
    """用户行为追踪表 - 推荐算法基础"""
    __tablename__ = "user_behaviors"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String, nullable=False, index=True)
    action_type = Column(String, nullable=False)  # search, view, click, create
    target_entity = Column(String, index=True)
    context_data = Column(JSON)  # 上下文信息
    
    # 行为特征
    duration_ms = Column(Integer)
    scroll_depth = Column(Float)
    interaction_strength = Column(Float)
    
    # 时间信息
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class EntityRelationship(Base):
    """实体关系表 - 知识图谱边"""
    __tablename__ = "entity_relationships"
    
    id = Column(Integer, primary_key=True)
    source_entity = Column(String, nullable=False, index=True)
    target_entity = Column(String, nullable=False, index=True)
    relationship_type = Column(String, nullable=False)
    
    # 关系属性
    strength = Column(Float, default=1.0)
    confidence = Column(Float, default=1.0)
    relationship_data = Column(JSON)
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AIConversation(Base):
    """AI对话历史表 - 极高敏感数据"""
    __tablename__ = "ai_conversations"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String, nullable=False, index=True)
    
    # 对话内容
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    context_entities = Column(JSON)  # 相关实体
    
    # 对话特征
    message_type = Column(String)  # question, command, chat
    satisfaction_rating = Column(Integer)  # 用户反馈
    processing_time_ms = Column(Integer)
    
    # 时间信息
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ConnectorConfiguration(Base):
    """连接器配置表"""
    __tablename__ = "connector_configurations"
    
    id = Column(String, primary_key=True)
    connector_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    
    # 配置信息
    configuration = Column(JSON, nullable=False)
    credentials = Column(JSON)  # 加密存储的凭据
    
    # 状态信息
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime)
    sync_status = Column(String)
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**SQLCipher集成实现**:

```python
# daemon/services/database_service.py
class SQLCipherDatabaseService:
    """SQLCipher加密数据库服务"""
    
    def __init__(self, db_path: str, master_password: str):
        self.db_path = db_path
        self.master_password = master_password
        self.engine = None
        self.session_factory = None
        
    def initialize_database(self):
        """初始化SQLCipher加密数据库"""
        # 生成设备指纹
        device_fingerprint = self._get_device_fingerprint()
        
        # 派生数据库密钥
        db_key = self._derive_database_key(self.master_password, device_fingerprint)
        
        # 创建SQLCipher引擎
        connection_string = f"sqlite+pysqlcipher://:{db_key}@/{self.db_path}"
        
        self.engine = create_engine(
            connection_string,
            connect_args={
                "cipher": "aes-256-gcm",
                "kdf_iter": 256000,
                "cipher_page_size": 4096,
                "cipher_memory_security": True,
                "cipher_use_hmac": True,
            },
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False  # 生产环境关闭SQL日志
        )
        
        # 创建所有表
        Base.metadata.create_all(self.engine)
        
        # 应用性能优化
        self._optimize_database_performance()
        
        # 创建Session工厂
        self.session_factory = sessionmaker(bind=self.engine)
        
        logger.info("SQLCipher数据库初始化完成")
    
    def _derive_database_key(self, password: str, device_id: str) -> str:
        """派生数据库加密密钥"""
        import hashlib
        import base64
        
        key_material = f"{password}:{device_id}:linch-mind-db-v2"
        derived_key = hashlib.pbkdf2_hmac(
            'sha256',
            key_material.encode('utf-8'),
            b'linch-mind-salt-v2',
            100000  # 足够的迭代次数
        )
        return base64.urlsafe_b64encode(derived_key).decode('utf-8')
    
    def _optimize_database_performance(self):
        """优化SQLCipher性能"""
        with self.engine.connect() as conn:
            # 缓存设置
            conn.execute("PRAGMA cache_size = -64000")  # 64MB缓存
            
            # WAL模式 - 提升并发性能
            conn.execute("PRAGMA journal_mode = WAL")
            
            # 同步模式优化
            conn.execute("PRAGMA synchronous = NORMAL")
            
            # 临时存储优化
            conn.execute("PRAGMA temp_store = MEMORY")
            
            # 内存映射
            conn.execute("PRAGMA mmap_size = 268435456")  # 256MB
            
            # 自动分析
            conn.execute("PRAGMA optimize")
            
        # 创建性能索引
        self._create_performance_indexes()
    
    def _create_performance_indexes(self):
        """创建查询性能索引"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_entity_type_name ON entity_metadata(entity_type, name)",
            "CREATE INDEX IF NOT EXISTS idx_entity_updated ON entity_metadata(updated_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_entity_access_count ON entity_metadata(access_count DESC)",
            
            "CREATE INDEX IF NOT EXISTS idx_behavior_timestamp ON user_behaviors(timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_behavior_session ON user_behaviors(session_id, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_behavior_entity ON user_behaviors(target_entity)",
            
            "CREATE INDEX IF NOT EXISTS idx_relationship_source ON entity_relationships(source_entity)",
            "CREATE INDEX IF NOT EXISTS idx_relationship_target ON entity_relationships(target_entity)",
            "CREATE INDEX IF NOT EXISTS idx_relationship_type ON entity_relationships(relationship_type)",
            
            "CREATE INDEX IF NOT EXISTS idx_conversation_session ON ai_conversations(session_id, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_conversation_timestamp ON ai_conversations(timestamp DESC)"
        ]
        
        with self.engine.connect() as conn:
            for index_sql in indexes:
                try:
                    conn.execute(index_sql)
                except Exception as e:
                    logger.warning(f"创建索引失败: {e}")
    
    def get_session(self):
        """获取数据库会话"""
        return self.session_factory()
    
    def close(self):
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
```

### 3.3 ChromaDB向量存储层

**技术选择**: ChromaDB本地部署

**选择理由**:
- ✅ Python原生，无额外服务依赖
- ✅ 本地文件存储，数据完全可控
- ✅ 支持多种embedding模型
- ✅ 内置相似性搜索功能
- ✅ 轻量级，适合个人应用

**实现设计**:

```python
# daemon/services/vector_storage_service.py
class ChromaVectorStorageService:
    """ChromaDB向量存储服务"""
    
    def __init__(self, persist_directory: str):
        self.persist_directory = persist_directory
        self.client = None
        self.collections = {}
        
    def initialize_vector_storage(self):
        """初始化ChromaDB向量存储"""
        import chromadb
        from chromadb.config import Settings
        
        # 创建本地持久化客户端
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=self.persist_directory,
            anonymized_telemetry=False  # 关闭遥测
        ))
        
        # 创建集合
        self.collections = {
            "documents": self._get_or_create_collection(
                "documents", 
                metadata={"description": "文档内容向量"}
            ),
            "entities": self._get_or_create_collection(
                "entities",
                metadata={"description": "实体语义向量"}
            ),
            "conversations": self._get_or_create_collection(
                "conversations",
                metadata={"description": "对话内容向量"}
            )
        }
        
        logger.info("ChromaDB向量存储初始化完成")
    
    def _get_or_create_collection(self, name: str, metadata: dict = None):
        """获取或创建集合"""
        try:
            return self.client.get_collection(name)
        except:
            return self.client.create_collection(
                name=name,
                metadata=metadata or {}
            )
    
    async def add_document_embedding(self, doc_id: str, content: str, 
                                   metadata: dict = None):
        """添加文档向量"""
        try:
            # 生成embedding (这里需要集成实际的embedding模型)
            embedding = await self._generate_embedding(content)
            
            self.collections["documents"].add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata or {}]
            )
            
            logger.debug(f"添加文档向量: {doc_id}")
            
        except Exception as e:
            logger.error(f"添加文档向量失败: {e}")
    
    async def semantic_search(self, query: str, collection_name: str = "documents", 
                            n_results: int = 10) -> List[dict]:
        """语义搜索"""
        try:
            # 生成查询向量
            query_embedding = await self._generate_embedding(query)
            
            # 执行相似性搜索
            results = self.collections[collection_name].query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # 格式化结果
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"语义搜索失败: {e}")
            return []
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """生成文本embedding"""
        # 这里需要集成实际的embedding模型
        # 比如 sentence-transformers, OpenAI embedding API 等
        
        # 示例：使用简单的TF-IDF (实际应用中替换为更好的模型)
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        # 临时实现，实际应该使用预训练的语义模型
        vectorizer = TfidfVectorizer(max_features=384)  # 384维向量
        try:
            tfidf_matrix = vectorizer.fit_transform([text])
            return tfidf_matrix.toarray()[0].tolist()
        except:
            # 如果出错，返回零向量
            return [0.0] * 384
    
    def persist(self):
        """持久化数据到磁盘"""
        if self.client:
            self.client.persist()
```

### 3.4 NetworkX图分析层

**技术选择**: NetworkX + SQLite持久化

**选择理由**:
- ✅ 丰富的图算法库 (200+ 算法)
- ✅ 纯Python实现，无外部依赖
- ✅ 与SQLite结合，数据持久化简单
- ✅ 灵活的图数据结构
- ✅ 与pandas/numpy无缝集成

**实现设计**:

```python
# daemon/services/graph_storage_service.py
class NetworkXGraphStorageService:
    """NetworkX图存储服务"""
    
    def __init__(self, database_service: SQLCipherDatabaseService):
        self.database_service = database_service
        self.knowledge_graph = nx.DiGraph()
        self.user_interest_graph = nx.Graph()
        self.loaded = False
        
    def initialize_graph_storage(self):
        """初始化图存储"""
        # 从数据库加载图数据
        self._load_graphs_from_database()
        self.loaded = True
        logger.info("NetworkX图存储初始化完成")
    
    def _load_graphs_from_database(self):
        """从SQLite数据库加载图数据"""
        session = self.database_service.get_session()
        try:
            # 加载实体作为节点
            entities = session.query(EntityMetadata).all()
            for entity in entities:
                self.knowledge_graph.add_node(
                    entity.id,
                    name=entity.name,
                    type=entity.entity_type,
                    metadata=entity.metadata or {},
                    access_count=entity.access_count,
                    relevance_score=entity.relevance_score
                )
            
            # 加载关系作为边
            relationships = session.query(EntityRelationship).all()
            for rel in relationships:
                self.knowledge_graph.add_edge(
                    rel.source_entity,
                    rel.target_entity,
                    type=rel.relationship_type,
                    strength=rel.strength,
                    confidence=rel.confidence,
                    data=rel.relationship_data or {}
                )
            
            logger.info(f"加载知识图谱: {len(self.knowledge_graph.nodes)} 节点, "
                       f"{len(self.knowledge_graph.edges)} 边")
                       
        except Exception as e:
            logger.error(f"加载图数据失败: {e}")
        finally:
            session.close()
    
    def add_entity(self, entity_id: str, name: str, entity_type: str, 
                   metadata: dict = None):
        """添加实体节点"""
        self.knowledge_graph.add_node(
            entity_id,
            name=name,
            type=entity_type,
            metadata=metadata or {},
            access_count=0,
            relevance_score=0.0
        )
    
    def add_relationship(self, source_id: str, target_id: str, 
                        relationship_type: str, strength: float = 1.0,
                        confidence: float = 1.0, data: dict = None):
        """添加实体关系"""
        self.knowledge_graph.add_edge(
            source_id,
            target_id,
            type=relationship_type,
            strength=strength,
            confidence=confidence,
            data=data or {}
        )
    
    def find_related_entities(self, entity_id: str, max_depth: int = 2, 
                            min_strength: float = 0.1) -> List[dict]:
        """查找相关实体"""
        if entity_id not in self.knowledge_graph:
            return []
        
        related_entities = []
        
        try:
            # 使用广度优先搜索查找相关实体
            for neighbor in nx.bfs_tree(self.knowledge_graph, entity_id, depth_limit=max_depth):
                if neighbor == entity_id:
                    continue
                
                # 计算关系路径
                try:
                    path = nx.shortest_path(self.knowledge_graph, entity_id, neighbor)
                    path_strength = self._calculate_path_strength(path)
                    
                    if path_strength >= min_strength:
                        node_data = self.knowledge_graph.nodes[neighbor]
                        related_entities.append({
                            'entity_id': neighbor,
                            'name': node_data.get('name', ''),
                            'type': node_data.get('type', ''),
                            'path_strength': path_strength,
                            'path_length': len(path) - 1,
                            'metadata': node_data.get('metadata', {})
                        })
                        
                except nx.NetworkXNoPath:
                    continue
                    
            # 按关系强度排序
            related_entities.sort(key=lambda x: x['path_strength'], reverse=True)
            
        except Exception as e:
            logger.error(f"查找相关实体失败: {e}")
        
        return related_entities
    
    def _calculate_path_strength(self, path: List[str]) -> float:
        """计算路径强度"""
        if len(path) < 2:
            return 0.0
        
        total_strength = 1.0
        for i in range(len(path) - 1):
            edge_data = self.knowledge_graph.get_edge_data(path[i], path[i + 1])
            if edge_data:
                edge_strength = edge_data.get('strength', 1.0)
                total_strength *= edge_strength
            else:
                total_strength *= 0.1  # 默认较低强度
        
        # 路径长度衰减
        decay_factor = 0.8 ** (len(path) - 2)
        return total_strength * decay_factor
    
    def get_graph_statistics(self) -> dict:
        """获取图统计信息"""
        return {
            'total_nodes': len(self.knowledge_graph.nodes),
            'total_edges': len(self.knowledge_graph.edges),
            'average_degree': sum(dict(self.knowledge_graph.degree()).values()) / len(self.knowledge_graph.nodes) if self.knowledge_graph.nodes else 0,
            'connected_components': nx.number_weakly_connected_components(self.knowledge_graph),
            'density': nx.density(self.knowledge_graph)
        }
    
    def persist_graphs_to_database(self):
        """将图数据持久化到SQLite数据库"""
        session = self.database_service.get_session()
        try:
            # 同步节点数据到EntityMetadata表
            for node_id, node_data in self.knowledge_graph.nodes(data=True):
                entity = session.query(EntityMetadata).filter_by(id=node_id).first()
                if entity:
                    # 更新现有实体的图相关属性
                    entity.access_count = node_data.get('access_count', 0)
                    entity.relevance_score = node_data.get('relevance_score', 0.0)
                else:
                    # 创建新实体
                    entity = EntityMetadata(
                        id=node_id,
                        name=node_data.get('name', ''),
                        entity_type=node_data.get('type', 'unknown'),
                        metadata=node_data.get('metadata', {}),
                        access_count=node_data.get('access_count', 0),
                        relevance_score=node_data.get('relevance_score', 0.0)
                    )
                    session.add(entity)
            
            # 同步边数据到EntityRelationship表
            for source, target, edge_data in self.knowledge_graph.edges(data=True):
                # 检查关系是否已存在
                existing_rel = session.query(EntityRelationship).filter_by(
                    source_entity=source,
                    target_entity=target,
                    relationship_type=edge_data.get('type', 'related')
                ).first()
                
                if existing_rel:
                    # 更新现有关系
                    existing_rel.strength = edge_data.get('strength', 1.0)
                    existing_rel.confidence = edge_data.get('confidence', 1.0)
                    existing_rel.relationship_data = edge_data.get('data', {})
                    existing_rel.updated_at = datetime.utcnow()
                else:
                    # 创建新关系
                    new_rel = EntityRelationship(
                        source_entity=source,
                        target_entity=target,
                        relationship_type=edge_data.get('type', 'related'),
                        strength=edge_data.get('strength', 1.0),
                        confidence=edge_data.get('confidence', 1.0),
                        relationship_data=edge_data.get('data', {})
                    )
                    session.add(new_rel)
            
            session.commit()
            logger.info("图数据持久化完成")
            
        except Exception as e:
            session.rollback()
            logger.error(f"图数据持久化失败: {e}")
        finally:
            session.close()
```

## 4. 数据管理服务层

### 4.1 统一数据管理器

```python
# daemon/services/unified_data_manager.py
class UnifiedDataManager:
    """统一数据管理器 - 协调三个存储层"""
    
    def __init__(self, config: dict):
        self.config = config
        
        # 初始化三个存储服务
        self.database_service = None
        self.vector_service = None
        self.graph_service = None
        
        # 数据同步状态
        self.sync_status = {
            'last_sync': None,
            'sync_in_progress': False,
            'sync_errors': []
        }
    
    async def initialize_all_storage(self, master_password: str):
        """初始化所有存储服务"""
        try:
            # 1. 初始化SQLCipher数据库
            db_path = Path(self.config['data_directory']) / "linch_mind.db"
            self.database_service = SQLCipherDatabaseService(str(db_path), master_password)
            self.database_service.initialize_database()
            
            # 2. 初始化ChromaDB向量存储
            vector_path = Path(self.config['data_directory']) / "vectors"
            self.vector_service = ChromaVectorStorageService(str(vector_path))
            self.vector_service.initialize_vector_storage()
            
            # 3. 初始化NetworkX图存储
            self.graph_service = NetworkXGraphStorageService(self.database_service)
            self.graph_service.initialize_graph_storage()
            
            logger.info("所有存储服务初始化完成")
            
        except Exception as e:
            logger.error(f"存储服务初始化失败: {e}")
            raise
    
    async def add_knowledge_entity(self, entity_data: dict) -> str:
        """添加知识实体 - 跨存储层操作"""
        entity_id = entity_data.get('id') or self._generate_entity_id()
        
        try:
            # 1. 添加到SQLite主存储
            session = self.database_service.get_session()
            entity = EntityMetadata(
                id=entity_id,
                name=entity_data['name'],
                entity_type=entity_data['type'],
                description=entity_data.get('description', ''),
                source_path=entity_data.get('source_path'),
                metadata=entity_data.get('metadata', {})
            )
            session.add(entity)
            session.commit()
            session.close()
            
            # 2. 添加到向量存储 (如果有内容)
            if 'content' in entity_data:
                await self.vector_service.add_document_embedding(
                    entity_id,
                    entity_data['content'],
                    {
                        'name': entity_data['name'],
                        'type': entity_data['type'],
                        'source': entity_data.get('source_path', '')
                    }
                )
            
            # 3. 添加到图存储
            self.graph_service.add_entity(
                entity_id,
                entity_data['name'],
                entity_data['type'],
                entity_data.get('metadata', {})
            )
            
            logger.info(f"添加知识实体成功: {entity_id}")
            return entity_id
            
        except Exception as e:
            logger.error(f"添加知识实体失败: {e}")
            raise
    
    async def semantic_search_entities(self, query: str, limit: int = 10) -> List[dict]:
        """语义搜索实体"""
        try:
            # 1. 向量搜索
            vector_results = await self.vector_service.semantic_search(
                query, "entities", limit * 2
            )
            
            # 2. 从数据库获取完整实体信息
            entity_ids = [result['id'] for result in vector_results]
            
            session = self.database_service.get_session()
            entities = session.query(EntityMetadata).filter(
                EntityMetadata.id.in_(entity_ids)
            ).all()
            session.close()
            
            # 3. 合并结果并排序
            results = []
            for entity in entities:
                # 找到对应的向量搜索结果
                vector_result = next(
                    (r for r in vector_results if r['id'] == entity.id), 
                    None
                )
                
                if vector_result:
                    results.append({
                        'id': entity.id,
                        'name': entity.name,
                        'type': entity.entity_type,
                        'description': entity.description,
                        'relevance_score': 1.0 - vector_result['distance'],  # 转换为相关性分数
                        'metadata': entity.metadata
                    })
            
            # 按相关性排序
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"语义搜索失败: {e}")
            return []
    
    async def find_related_entities(self, entity_id: str, max_results: int = 10) -> List[dict]:
        """查找相关实体 - 结合图分析和语义搜索"""
        try:
            # 1. 使用图算法查找相关实体
            graph_related = self.graph_service.find_related_entities(
                entity_id, max_depth=2, min_strength=0.1
            )
            
            # 2. 获取源实体信息用于语义搜索
            session = self.database_service.get_session()
            source_entity = session.query(EntityMetadata).filter_by(id=entity_id).first()
            
            if source_entity:
                # 3. 基于实体描述进行语义搜索
                semantic_query = f"{source_entity.name} {source_entity.description or ''}"
                semantic_related = await self.semantic_search_entities(
                    semantic_query, max_results
                )
                
                # 4. 合并和去重结果
                combined_results = {}
                
                # 添加图相关结果 (权重更高)
                for item in graph_related:
                    combined_results[item['entity_id']] = {
                        **item,
                        'relation_type': 'graph',
                        'final_score': item['path_strength'] * 1.2  # 图关系权重更高
                    }
                
                # 添加语义相关结果
                for item in semantic_related:
                    if item['id'] != entity_id:  # 排除自己
                        if item['id'] in combined_results:
                            # 如果已存在，增加分数
                            combined_results[item['id']]['final_score'] += item['relevance_score'] * 0.8
                            combined_results[item['id']]['relation_type'] = 'hybrid'
                        else:
                            combined_results[item['id']] = {
                                'entity_id': item['id'],
                                'name': item['name'],
                                'type': item['type'],
                                'metadata': item['metadata'],
                                'relation_type': 'semantic',
                                'final_score': item['relevance_score'] * 0.8
                            }
                
                # 5. 排序并返回结果
                final_results = list(combined_results.values())
                final_results.sort(key=lambda x: x['final_score'], reverse=True)
                
                session.close()
                return final_results[:max_results]
            
            session.close()
            return []
            
        except Exception as e:
            logger.error(f"查找相关实体失败: {e}")
            return []
    
    async def get_storage_statistics(self) -> dict:
        """获取存储统计信息"""
        try:
            # SQLite统计
            session = self.database_service.get_session()
            entity_count = session.query(EntityMetadata).count()
            relationship_count = session.query(EntityRelationship).count()
            behavior_count = session.query(UserBehavior).count()
            conversation_count = session.query(AIConversation).count()
            session.close()
            
            # 图统计
            graph_stats = self.graph_service.get_graph_statistics()
            
            return {
                'database': {
                    'entities': entity_count,
                    'relationships': relationship_count,
                    'behaviors': behavior_count,
                    'conversations': conversation_count
                },
                'graph': graph_stats,
                'vector': {
                    'collections': len(self.vector_service.collections),
                    'status': 'active' if self.vector_service.client else 'inactive'
                },
                'sync_status': self.sync_status
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
```

## 5. 性能优化策略

### 5.1 查询优化

```python
# daemon/services/query_optimizer.py
class QueryOptimizer:
    """查询性能优化器"""
    
    def __init__(self, data_manager: UnifiedDataManager):
        self.data_manager = data_manager
        self.query_cache = {}
        self.cache_ttl = 300  # 5分钟缓存
    
    async def optimized_entity_search(self, query: str, search_type: str = "hybrid") -> List[dict]:
        """优化的实体搜索"""
        cache_key = f"{search_type}:{hashlib.md5(query.encode()).hexdigest()}"
        
        # 检查缓存
        if cache_key in self.query_cache:
            cached_result, timestamp = self.query_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_result
        
        # 执行搜索
        if search_type == "semantic":
            results = await self.data_manager.semantic_search_entities(query)
        elif search_type == "graph":
            # 首先找到最相关的实体，然后查找其关联
            semantic_results = await self.data_manager.semantic_search_entities(query, 1)
            if semantic_results:
                results = await self.data_manager.find_related_entities(semantic_results[0]['id'])
            else:
                results = []
        else:  # hybrid
            results = await self._hybrid_search(query)
        
        # 缓存结果
        self.query_cache[cache_key] = (results, time.time())
        
        return results
    
    async def _hybrid_search(self, query: str) -> List[dict]:
        """混合搜索策略"""
        # 1. 语义搜索获取候选
        semantic_results = await self.data_manager.semantic_search_entities(query, 5)
        
        # 2. 为每个候选查找关联实体
        all_results = {}
        
        for result in semantic_results:
            # 添加直接匹配结果
            all_results[result['id']] = {
                **result,
                'match_type': 'direct',
                'final_score': result['relevance_score']
            }
            
            # 添加关联实体
            related = await self.data_manager.find_related_entities(result['id'], 3)
            for rel in related:
                if rel['entity_id'] not in all_results:
                    all_results[rel['entity_id']] = {
                        **rel,
                        'match_type': 'related',
                        'final_score': rel['final_score'] * 0.7  # 关联实体降权
                    }
        
        # 3. 排序并返回
        final_results = list(all_results.values())
        final_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        return final_results[:10]
```

### 5.2 数据同步优化

```python
# daemon/services/data_sync_optimizer.py
class DataSyncOptimizer:
    """数据同步优化器"""
    
    def __init__(self, data_manager: UnifiedDataManager):
        self.data_manager = data_manager
        self.sync_batch_size = 100
        self.sync_interval = 60  # 1分钟同步间隔
    
    async def incremental_sync(self):
        """增量数据同步"""
        try:
            # 1. 获取需要同步的数据
            session = self.data_manager.database_service.get_session()
            
            # 查找最近更新的实体
            recent_entities = session.query(EntityMetadata).filter(
                EntityMetadata.updated_at > self.data_manager.sync_status.get('last_sync', datetime.min)
            ).limit(self.sync_batch_size).all()
            
            # 2. 批量更新向量存储
            for entity in recent_entities:
                if entity.description:
                    await self.data_manager.vector_service.add_document_embedding(
                        entity.id,
                        f"{entity.name} {entity.description}",
                        {
                            'name': entity.name,
                            'type': entity.entity_type,
                            'updated_at': entity.updated_at.isoformat()
                        }
                    )
            
            # 3. 同步图数据
            self.data_manager.graph_service.persist_graphs_to_database()
            
            # 4. 更新同步状态
            self.data_manager.sync_status['last_sync'] = datetime.utcnow()
            self.data_manager.sync_status['sync_in_progress'] = False
            
            session.close()
            logger.info(f"增量同步完成: {len(recent_entities)} 个实体")
            
        except Exception as e:
            logger.error(f"增量同步失败: {e}")
            self.data_manager.sync_status['sync_errors'].append(str(e))
```

## 6. 监控和维护

### 6.1 存储健康监控

```python
# daemon/services/storage_monitor.py
class StorageHealthMonitor:
    """存储健康状态监控"""
    
    def __init__(self, data_manager: UnifiedDataManager):
        self.data_manager = data_manager
        self.health_metrics = {}
        
    async def check_storage_health(self) -> dict:
        """检查存储系统健康状态"""
        health_report = {
            'overall_status': 'healthy',
            'database': await self._check_database_health(),
            'vector_storage': await self._check_vector_health(),
            'graph_storage': await self._check_graph_health(),
            'performance': await self._check_performance_metrics()
        }
        
        # 评估整体状态
        component_statuses = [
            health_report['database']['status'],
            health_report['vector_storage']['status'],
            health_report['graph_storage']['status']
        ]
        
        if 'error' in component_statuses:
            health_report['overall_status'] = 'error'
        elif 'warning' in component_statuses:
            health_report['overall_status'] = 'warning'
        
        return health_report
    
    async def _check_database_health(self) -> dict:
        """检查数据库健康状态"""
        try:
            session = self.data_manager.database_service.get_session()
            
            # 检查连接
            session.execute("SELECT 1")
            
            # 检查数据完整性
            entity_count = session.query(EntityMetadata).count()
            relationship_count = session.query(EntityRelationship).count()
            
            session.close()
            
            return {
                'status': 'healthy',
                'entity_count': entity_count,
                'relationship_count': relationship_count,
                'connection': 'active'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'connection': 'failed'
            }
    
    async def _check_performance_metrics(self) -> dict:
        """检查性能指标"""
        try:
            # 测试查询性能
            start_time = time.time()
            
            # 执行一个简单的查询
            session = self.data_manager.database_service.get_session()
            session.query(EntityMetadata).limit(10).all()
            session.close()
            
            query_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            # 评估性能状态
            if query_time < 100:
                performance_status = 'excellent'
            elif query_time < 500:
                performance_status = 'good'
            elif query_time < 1000:
                performance_status = 'fair'
            else:
                performance_status = 'poor'
            
            return {
                'status': performance_status,
                'query_time_ms': query_time,
                'memory_usage': self._get_memory_usage()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _get_memory_usage(self) -> dict:
        """获取内存使用情况"""
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024
        }
```

## 7. 实施路线图

### 7.1 Phase 1: 核心存储基础 (2-3周)

```
✅ 优先级: 最高
📅 预计工期: 2-3周

核心任务:
├── SQLCipherDatabaseService 实现
├── 基础数据模型创建 (EntityMetadata, UserBehavior等)
├── 数据库初始化和迁移机制
├── 基础CRUD操作接口
├── 性能索引创建
└── 单元测试覆盖
```

### 7.2 Phase 2: 向量和图存储集成 (2-3周)

```
✅ 优先级: 高
📅 预计工期: 2-3周

核心任务:
├── ChromaVectorStorageService 实现
├── NetworkXGraphStorageService 实现
├── UnifiedDataManager 统一接口
├── 跨存储层数据同步
├── 语义搜索和图算法集成
└── 集成测试和性能调优
```

### 7.3 Phase 3: 优化和监控 (1-2周)

```
🟡 优先级: 中等
📅 预计工期: 1-2周

核心任务:
├── QueryOptimizer 查询优化
├── DataSyncOptimizer 同步优化
├── StorageHealthMonitor 健康监控
├── 性能基准测试
├── 错误处理和恢复机制
└── 文档和用户指南
```

## 8. 总结

### 8.1 架构优势

- **安全可靠**: SQLCipher AES-256加密，保护用户隐私数据
- **简化设计**: 三层架构避免过度复杂，开发维护成本可控
- **性能优化**: 针对个人应用场景的查询和存储优化
- **扩展性强**: 模块化设计支持功能扩展和技术升级
- **标准兼容**: 使用成熟的开源技术栈，避免供应商锁定

### 8.2 关键创新

1. **统一数据管理**: UnifiedDataManager协调三个存储层，提供一致的API
2. **混合搜索策略**: 结合语义搜索和图算法，提升搜索准确性
3. **增量同步机制**: 优化数据同步性能，减少系统开销
4. **健康监控体系**: 实时监控存储状态，预防和快速定位问题
5. **查询优化器**: 智能缓存和批处理，提升查询响应速度

### 8.3 成功指标

- **安全性**: 100%数据加密存储，符合隐私保护要求
- **性能**: 90%查询在100ms内完成，支持10K+实体规模
- **可靠性**: 99.9%系统可用性，数据零丢失
- **可扩展性**: 支持100K+实体和1M+关系的规模扩展
- **开发效率**: 统一API减少50%的数据访问代码

本架构为Linch Mind提供了安全、高效、可扩展的数据存储解决方案，在保护用户隐私的同时，支持智能推荐和知识图谱等高级功能的实现。

---

**文档版本**: 2.0 - 实用主义版  
**创建时间**: 2025-08-04  
**最后更新**: 2025-08-04  
**相关文档**: 
- [安全架构设计](security_architecture_design.md)
- [Daemon架构设计](daemon_architecture.md)
- [产品愿景与战略](../00_vision_and_strategy/product_vision_and_strategy.md)