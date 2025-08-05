# FAISS向量搜索服务设计

**版本**: 1.0 - 纯Python集成版  
**创建时间**: 2025-08-05  
**技术栈**: FAISS + SQLCipher + sentence-transformers

## 1. 概述

FAISS (Facebook AI Similarity Search) 是Meta开发的高性能向量搜索库，专为大规模相似性搜索和聚类优化。在Linch Mind的纯Python架构中，FAISS提供语义搜索能力，支持实体快速增长的需求。

### 1.1 选择FAISS的理由

```python
faiss_advantages = {
    "性能优势": "C++实现，比纯Python向量搜索快10-100倍",
    "打包友好": "CPU版本无复杂依赖，PyInstaller完美支持",
    "内存高效": "支持内存映射，大向量集省内存50%+",
    "算法丰富": "支持精确搜索、近似搜索、聚类等",
    "生产验证": "Meta生产环境验证，处理十亿级向量",
    "Python集成": "官方Python绑定，API简洁易用"
}
```

## 2. 架构设计

### 2.1 服务架构

```python
# daemon/services/faiss_vector_service.py
class FAISSVectorService:
    """FAISS向量搜索服务"""
    
    def __init__(self, data_dir: str, embedding_dim: int = 384):
        self.data_dir = Path(data_dir)
        self.embedding_dim = embedding_dim
        
        # FAISS索引
        self.faiss_index = None
        self.entity_mapping = {}  # FAISS ID -> Entity ID映射
        self.reverse_mapping = {}  # Entity ID -> FAISS ID映射
        
        # 嵌入模型
        self.embedding_model = None
        
        # 持久化
        self.index_file = self.data_dir / "faiss_index.bin"
        self.mapping_file = self.data_dir / "entity_mapping.json"
        
    async def initialize(self):
        """初始化FAISS向量服务"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. 初始化嵌入模型
        await self._initialize_embedding_model()
        
        # 2. 加载或创建FAISS索引
        await self._load_or_create_faiss_index()
        
        # 3. 加载实体映射
        self._load_entity_mapping()
        
        logger.info(f"FAISS向量服务初始化完成: {self.faiss_index.ntotal} 个向量")
    
    async def _initialize_embedding_model(self):
        """初始化嵌入模型"""
        try:
            from sentence_transformers import SentenceTransformer
            
            # 使用轻量级的多语言模型
            model_name = "all-MiniLM-L6-v2"  # 384维，22MB，支持中英文
            
            self.embedding_model = SentenceTransformer(model_name)
            self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
            
            logger.info(f"嵌入模型加载完成: {model_name}, 维度: {self.embedding_dim}")
            
        except ImportError:
            logger.warning("sentence-transformers未安装，使用简单TF-IDF嵌入")
            self.embedding_model = SimpleTFIDFEmbedding(self.embedding_dim)
    
    async def _load_or_create_faiss_index(self):
        """加载或创建FAISS索引"""
        if self.index_file.exists():
            # 加载现有索引
            import faiss
            self.faiss_index = faiss.read_index(str(self.index_file))
            logger.info(f"加载FAISS索引: {self.faiss_index.ntotal} 个向量")
        else:
            # 创建新索引
            await self._create_new_faiss_index()
    
    async def _create_new_faiss_index(self):
        """创建新的FAISS索引"""
        import faiss
        
        # 根据预期数据规模选择索引类型
        if self.embedding_dim == 384:
            # 小规模：使用精确搜索
            self.faiss_index = faiss.IndexFlatIP(self.embedding_dim)  # 内积相似度
        else:
            # 大规模：使用近似搜索
            nlist = 100  # 聚类中心数量
            self.faiss_index = faiss.IndexIVFFlat(
                faiss.IndexFlatIP(self.embedding_dim), 
                self.embedding_dim, 
                nlist
            )
        
        logger.info(f"创建FAISS索引: 维度{self.embedding_dim}")
    
    async def add_document_embedding(self, entity_id: str, content: str, metadata: dict = None):
        """添加文档向量到FAISS索引"""
        try:
            # 1. 生成向量
            embedding = await self._generate_embedding(content)
            
            # 2. 添加到FAISS索引
            import numpy as np
            embedding_array = np.array([embedding], dtype=np.float32)
            
            # 如果是IVF索引且未训练，需要先训练
            import faiss
            if isinstance(self.faiss_index, faiss.IndexIVFFlat) and not self.faiss_index.is_trained:
                if self.faiss_index.ntotal == 0:
                    # 第一个向量，暂存等待更多数据来训练
                    self._pending_vectors = [(entity_id, embedding, metadata)]
                    return
                
            self.faiss_index.add(embedding_array)
            
            # 3. 更新实体映射
            faiss_id = self.faiss_index.ntotal - 1
            self.entity_mapping[faiss_id] = {
                'entity_id': entity_id,
                'metadata': metadata or {},
                'content_preview': content[:200]  # 保存内容预览
            }
            self.reverse_mapping[entity_id] = faiss_id
            
            # 4. 定期持久化
            if self.faiss_index.ntotal % 100 == 0:
                await self._persist_index()
            
            logger.debug(f"添加向量到FAISS: {entity_id}")
            
        except Exception as e:
            logger.error(f"添加向量失败: {e}")
    
    async def semantic_search(self, query: str, top_k: int = 10) -> List[dict]:
        """语义搜索"""
        try:
            # 1. 生成查询向量
            query_embedding = await self._generate_embedding(query)
            
            # 2. FAISS搜索
            import numpy as np
            query_array = np.array([query_embedding], dtype=np.float32)
            
            distances, indices = self.faiss_index.search(query_array, top_k)
            
            # 3. 构建结果
            results = []
            for i, (distance, faiss_id) in enumerate(zip(distances[0], indices[0])):
                if faiss_id in self.entity_mapping:
                    entity_info = self.entity_mapping[faiss_id]
                    results.append({
                        'entity_id': entity_info['entity_id'],
                        'similarity_score': float(distance),
                        'rank': i + 1,
                        'metadata': entity_info['metadata'],
                        'content_preview': entity_info['content_preview']
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"语义搜索失败: {e}")
            return []
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """生成文本嵌入向量"""
        try:
            if hasattr(self.embedding_model, 'encode'):
                # sentence-transformers模型
                embedding = self.embedding_model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            else:
                # 简单TF-IDF模型
                return self.embedding_model.encode(text)
                
        except Exception as e:
            logger.error(f"生成嵌入向量失败: {e}")
            return [0.0] * self.embedding_dim
    
    async def _persist_index(self):
        """持久化FAISS索引"""
        try:
            import faiss
            import json
            
            # 保存FAISS索引
            faiss.write_index(self.faiss_index, str(self.index_file))
            
            # 保存实体映射
            with open(self.mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.entity_mapping, f, ensure_ascii=False, indent=2)
            
            logger.debug("FAISS索引持久化完成")
            
        except Exception as e:
            logger.error(f"FAISS索引持久化失败: {e}")
    
    def _load_entity_mapping(self):
        """加载实体映射"""
        try:
            if self.mapping_file.exists():
                import json
                with open(self.mapping_file, 'r', encoding='utf-8') as f:
                    mapping_data = json.load(f)
                
                # 转换键为整数
                self.entity_mapping = {int(k): v for k, v in mapping_data.items()}
                
                # 构建反向映射
                self.reverse_mapping = {
                    v['entity_id']: int(k) 
                    for k, v in self.entity_mapping.items()
                }
                
                logger.info(f"加载实体映射: {len(self.entity_mapping)} 个实体")
        
        except Exception as e:
            logger.warning(f"加载实体映射失败: {e}")
            self.entity_mapping = {}
            self.reverse_mapping = {}


class SimpleTFIDFEmbedding:
    """简单TF-IDF嵌入（备选方案）"""
    
    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.vectorizer = None
        
    def encode(self, text: str) -> List[float]:
        """编码文本为向量"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            import numpy as np
            
            if self.vectorizer is None:
                self.vectorizer = TfidfVectorizer(
                    max_features=self.embedding_dim,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                # 需要先fit，这里使用简单处理
                self.vectorizer.fit([text])
            
            vector = self.vectorizer.transform([text])
            dense_vector = vector.toarray()[0]
            
            # 确保维度正确
            if len(dense_vector) < self.embedding_dim:
                dense_vector = np.pad(dense_vector, (0, self.embedding_dim - len(dense_vector)))
            elif len(dense_vector) > self.embedding_dim:
                dense_vector = dense_vector[:self.embedding_dim]
            
            return dense_vector.tolist()
            
        except ImportError:
            # 如果sklearn也没有，使用最简单的哈希向量
            import hashlib
            hash_object = hashlib.md5(text.encode())
            hash_bytes = hash_object.digest()
            
            # 将hash转换为float向量
            vector = []
            for i in range(0, len(hash_bytes), 4):
                chunk = hash_bytes[i:i+4]
                if len(chunk) == 4:
                    value = int.from_bytes(chunk, byteorder='big') / (2**32)
                    vector.append(value)
            
            # 扩展到目标维度
            while len(vector) < self.embedding_dim:
                vector.extend(vector[:min(len(vector), self.embedding_dim - len(vector))])
            
            return vector[:self.embedding_dim]
```

## 3. 性能优化策略

### 3.1 索引优化

```python
class FAISSIndexOptimizer:
    """FAISS索引优化器"""
    
    @staticmethod
    def choose_optimal_index(vector_count: int, embedding_dim: int):
        """根据向量数量选择最优索引类型"""
        
        if vector_count < 1000:
            # 小规模：精确搜索
            return f"IndexFlatIP({embedding_dim})"
            
        elif vector_count < 10000:
            # 中规模：IVF索引
            nlist = min(vector_count // 100, 100)
            return f"IndexIVFFlat(IndexFlatIP({embedding_dim}), {embedding_dim}, {nlist})"
            
        elif vector_count < 100000:
            # 大规模：PQ压缩索引
            nlist = min(vector_count // 100, 1000)
            m = embedding_dim // 8  # PQ分段数
            return f"IndexIVFPQ(IndexFlatIP({embedding_dim}), {embedding_dim}, {nlist}, {m}, 8)"
            
        else:
            # 超大规模：HNSW索引
            return f"IndexHNSWFlat({embedding_dim}, 32)"
    
    @staticmethod
    def optimize_search_params(index, vector_count: int):
        """优化搜索参数"""
        import faiss
        
        if isinstance(index, faiss.IndexIVFFlat):
            # IVF索引：设置搜索的聚类数量
            nprobe = min(max(vector_count // 1000, 1), 20)
            index.nprobe = nprobe
            
        elif isinstance(index, faiss.IndexHNSWFlat):
            # HNSW索引：设置搜索精度
            index.hnsw.efSearch = 64
```

### 3.2 内存优化

```python
class FAISSMemoryOptimizer:
    """FAISS内存优化"""
    
    def __init__(self, faiss_service):
        self.faiss_service = faiss_service
        
    def enable_memory_mapping(self):
        """启用内存映射减少内存占用"""
        try:
            import faiss
            
            # 将索引切换到只读内存映射模式
            if hasattr(self.faiss_service.faiss_index, 'make_direct_map'):
                self.faiss_service.faiss_index.make_direct_map()
            
            logger.info("FAISS内存映射已启用")
            
        except Exception as e:
            logger.warning(f"内存映射启用失败: {e}")
    
    def compress_vectors(self):
        """压缩向量降低内存使用"""
        try:
            import faiss
            
            current_index = self.faiss_service.faiss_index
            vector_count = current_index.ntotal
            
            if vector_count > 10000:
                # 使用PQ压缩
                embedding_dim = current_index.d
                m = embedding_dim // 8
                
                # 创建PQ压缩索引
                compressed_index = faiss.IndexPQ(embedding_dim, m, 8)
                
                # 训练和添加向量
                all_vectors = current_index.reconstruct_n(0, vector_count)
                compressed_index.train(all_vectors)
                compressed_index.add(all_vectors)
                
                # 替换原索引
                self.faiss_service.faiss_index = compressed_index
                
                logger.info(f"向量压缩完成: {vector_count} 个向量")
                
        except Exception as e:
            logger.error(f"向量压缩失败: {e}")
```

## 4. 集成测试和基准

### 4.1 性能基准测试

```python
# tests/test_faiss_performance.py
import pytest
import time
import numpy as np
from daemon.services.faiss_vector_service import FAISSVectorService

class TestFAISSPerformance:
    """FAISS性能测试"""
    
    @pytest.fixture
    def faiss_service(self, tmp_path):
        """创建测试用FAISS服务"""
        service = FAISSVectorService(str(tmp_path))
        return service
    
    async def test_embedding_generation_speed(self, faiss_service):
        """测试嵌入生成速度"""
        await faiss_service.initialize()
        
        test_texts = [f"这是测试文本 {i}" for i in range(100)]
        
        start_time = time.time()
        for text in test_texts:
            await faiss_service._generate_embedding(text)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / len(test_texts)
        
        # 断言平均每个文本生成时间 < 50ms
        assert avg_time < 0.05, f"嵌入生成太慢: {avg_time:.3f}s"
        
        print(f"嵌入生成速度: {avg_time*1000:.1f}ms/文本")
    
    async def test_search_speed(self, faiss_service):
        """测试搜索速度"""
        await faiss_service.initialize()
        
        # 添加测试数据
        for i in range(1000):
            await faiss_service.add_document_embedding(
                f"entity_{i}",
                f"这是第{i}个测试文档，包含一些内容用于测试搜索性能。",
                {"index": i}
            )
        
        # 测试搜索速度
        search_queries = ["测试文档", "搜索性能", "向量检索", "语义匹配"]
        
        start_time = time.time()
        for query in search_queries:
            results = await faiss_service.semantic_search(query, top_k=10)
            assert len(results) > 0
        end_time = time.time()
        
        avg_search_time = (end_time - start_time) / len(search_queries)
        
        # 断言平均搜索时间 < 100ms
        assert avg_search_time < 0.1, f"搜索太慢: {avg_search_time:.3f}s"
        
        print(f"搜索速度: {avg_search_time*1000:.1f}ms/查询")
    
    async def test_memory_usage(self, faiss_service):
        """测试内存使用"""
        import psutil
        import os
        
        await faiss_service.initialize()
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 添加大量向量
        for i in range(5000):
            await faiss_service.add_document_embedding(
                f"entity_{i}",
                f"这是第{i}个测试文档" + "，内容较长" * 20,
                {"index": i}
            )
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # 每1000个向量的内存增长应该 < 50MB
        memory_per_1k = memory_increase / 5
        assert memory_per_1k < 50, f"内存使用过多: {memory_per_1k:.1f}MB/1k向量"
        
        print(f"内存使用: {memory_per_1k:.1f}MB/1k向量")
```

## 5. 部署和打包

### 5.1 PyInstaller集成

```python
# 在主要的linch_mind.spec中添加FAISS支持
hiddenimports=[
    # FAISS和相关库
    'faiss',
    'faiss._swigfaiss',
    'sentence_transformers',
    'transformers',
    'torch',  # sentence-transformers依赖
    'numpy',
    'scipy',
    # 备选TF-IDF支持
    'sklearn.feature_extraction.text',
    'sklearn.metrics.pairwise',
]

# 排除不需要的torch组件减小体积
excludes=[
    'torch.distributions',
    'torch.nn.modules.transformer',
    # 其他大型torch模块
]
```

### 5.2 模型文件处理

```python
# daemon/services/model_manager.py
class EmbeddingModelManager:
    """嵌入模型管理器"""
    
    def __init__(self):
        self.model_cache_dir = Path.home() / ".linch-mind" / "models"
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)
    
    def download_model_if_needed(self, model_name: str):
        """按需下载模型"""
        model_path = self.model_cache_dir / model_name
        
        if not model_path.exists():
            logger.info(f"首次使用，下载嵌入模型: {model_name}")
            
            try:
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer(model_name, cache_folder=str(self.model_cache_dir))
                logger.info(f"模型下载完成: {model_name}")
                return model
            except Exception as e:
                logger.warning(f"模型下载失败，使用备选方案: {e}")
                return None
        else:
            logger.info(f"加载缓存模型: {model_name}")
            from sentence_transformers import SentenceTransformer
            return SentenceTransformer(str(model_path))
```

## 6. 总结

FAISS向量搜索服务为Linch Mind提供了强大的语义搜索能力，关键优势：

1. **纯Python集成**: 无需外部服务，完美支持PyInstaller打包
2. **高性能**: C++实现，比纯Python方案快10-100倍
3. **内存高效**: 支持压缩和内存映射，适合大规模数据
4. **渐进式扩展**: 根据数据规模自动选择最优索引类型
5. **降级支持**: 提供TF-IDF备选方案，确保系统稳定性

预期性能：
- **向量生成**: <50ms/文档
- **语义搜索**: <100ms/查询（1万向量）
- **内存占用**: <30MB/1万向量
- **打包体积**: +25MB（FAISS库）

这个设计完美支持Linch Mind的快速增长需求，同时保持了纯Python架构的简洁性。