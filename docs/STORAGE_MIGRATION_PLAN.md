# Linch Mind 存储架构迁移计划

## 🎯 迁移目标

从**事件驱动的原始存储**迁移到**AI驱动的智能向量存储**

## 📊 当前问题分析

### 当前错误实现
```python
# ❌ GenericEventStorage.py 错误做法
entity_properties = {
    "event_data": event_data,  # 存储10KB原始数据
    "connector_id": connector_id,
    "event_type": event_type,
}
# 把事件当实体存储到entity_metadata表
```

### 数据库现状
```sql
-- 当前垃圾数据
sqlite3 ~/.linch-mind/development/database/linch_mind_dev.db
"SELECT COUNT(*) FROM entity_metadata;"  -- 8个无意义事件
"SELECT entity_id, LENGTH(properties) FROM entity_metadata;"  -- 每个10KB+
```

## 🚀 迁移实施计划

### Phase 1: 新架构实现 (优先级最高)

#### 1.1 创建新的Ollama集成服务
```python
# daemon/services/ai/ollama_service.py
class OllamaService:
    """本地AI服务集成"""
    
    def __init__(self):
        self.embedding_model = "nomic-embed-text"  # 384维
        self.llm_model = "llama3.2:3b"
        
    async def evaluate_content_value(self, content: str) -> float:
        """AI驱动的内容价值评估 0-1分"""
        prompt = f"""
        评估内容价值(0-1分):
        - 调试日志/垃圾信息: 0.0-0.2
        - 临时数据: 0.2-0.4  
        - 一般信息: 0.4-0.6
        - 有用信息: 0.6-0.8
        - 重要知识: 0.8-1.0
        
        内容: {content[:500]}
        
        只返回数字: 0.7
        """
        response = await self._chat(prompt)
        return float(response.strip())
    
    async def extract_semantic_summary(self, content: str) -> str:
        """提取语义摘要(100字以内)"""
        prompt = f"""
        将以下内容压缩为100字以内的语义摘要，保留核心信息:
        {content[:2000]}
        
        摘要:
        """
        return await self._chat(prompt)
    
    async def embed_text(self, text: str) -> List[float]:
        """本地向量化"""
        # 调用Ollama API进行向量化
        pass
```

#### 1.2 创建智能事件处理器
```python
# daemon/services/storage/intelligent_event_processor.py
class IntelligentEventProcessor:
    """AI驱动的智能事件处理"""
    
    def __init__(self):
        self.ollama = OllamaService()
        self.vector_store = FAISSVectorStore()
        
    async def process_connector_event(self, event: ConnectorEvent) -> bool:
        """智能事件处理流水线"""
        
        # 1. 价值评估
        value_score = await self.ollama.evaluate_content_value(event.content)
        if value_score < 0.3:
            logger.info(f"Discarding low-value content: {value_score}")
            return False  # 直接丢弃
            
        # 2. 语义摘要
        summary = await self.ollama.extract_semantic_summary(event.content)
        
        # 3. 向量化
        vector = await self.ollama.embed_text(summary)
        
        # 4. 存储到向量库
        doc_id = await self.vector_store.add_document(
            vector=vector,
            metadata={
                "summary": summary,  # 只存摘要，不存原文!
                "source": event.connector_id,
                "timestamp": event.timestamp,
                "value_score": value_score,
                "keywords": await self._extract_keywords(summary)
            }
        )
        
        # 5. 高价值内容才提取实体
        if value_score > 0.8:
            entities = await self._extract_valuable_entities(summary)
            await self._store_entities(entities, doc_id)
            
        return True
```

#### 1.3 创建FAISS向量存储
```python
# daemon/services/storage/faiss_vector_store.py
class FAISSVectorStore:
    """基于FAISS的向量存储"""
    
    def __init__(self):
        self.index_dir = Path("~/.linch-mind/knowledge/hot_index").expanduser()
        self.current_shard = self._load_current_shard()
        
    def _load_current_shard(self) -> FAISSIndex:
        """加载当前活跃分片"""
        shard_path = self.index_dir / f"current_{datetime.now():%Y_Q%q}"
        if not shard_path.exists():
            return self._create_new_shard(shard_path)
        return self._load_existing_shard(shard_path)
        
    async def add_document(self, vector: List[float], metadata: Dict) -> str:
        """添加文档到向量库"""
        # 压缩向量 (384维 -> 256维 + float16)
        compressed_vector = self._compress_vector(vector)
        
        # 添加到FAISS索引
        doc_id = f"doc_{uuid.uuid4().hex[:8]}"
        self.current_shard.add_with_ids([compressed_vector], [doc_id])
        
        # 存储元数据
        await self._store_metadata(doc_id, metadata)
        
        # 检查分片大小
        if self.current_shard.ntotal > self.MAX_SHARD_SIZE:
            await self._create_new_shard()
            
        return doc_id
```

### Phase 2: 替换现有实现

#### 2.1 修改GenericEventStorage
```python
# 修改 daemon/services/ipc_routes/generic_event_storage.py
class GenericEventStorage:
    def __init__(self):
        self.intelligent_processor = IntelligentEventProcessor()  # 新增
        # 保留原有实现作为fallback
        
    async def store_generic_event(self, ...):
        """新的智能存储逻辑"""
        try:
            # 使用新的智能处理器
            success = await self.intelligent_processor.process_connector_event(
                ConnectorEvent(
                    connector_id=connector_id,
                    event_type=event_type,
                    content=str(event_data),  # 转换为文本
                    timestamp=timestamp
                )
            )
            
            if success:
                logger.info(f"✅ Intelligently processed event from {connector_id}")
                return True
            else:
                logger.info(f"⚠️ Low-value event discarded from {connector_id}")
                return True  # 丢弃也算成功
                
        except Exception as e:
            logger.error(f"Intelligent processing failed, falling back: {e}")
            # Fallback到原有逻辑（临时）
            return await self._legacy_store_event(...)
```

### Phase 3: 数据清理和迁移

#### 3.1 清理当前垃圾数据
```python
# scripts/cleanup_legacy_data.py
class LegacyDataCleanup:
    """清理现有的垃圾数据"""
    
    async def cleanup_entity_metadata(self):
        """清理entity_metadata表中的事件数据"""
        
        with self.db.get_session() as session:
            # 查找所有connector_event类型的伪实体
            fake_entities = session.query(EntityMetadata).filter_by(
                type="connector_event"
            ).all()
            
            logger.info(f"Found {len(fake_entities)} fake entities to clean")
            
            for entity in fake_entities:
                # 检查是否值得迁移
                properties = entity.properties
                content = str(properties.get('event_data', ''))
                
                if len(content) > 1000:  # 大内容需要评估
                    value_score = await self.ollama.evaluate_content_value(content)
                    
                    if value_score > 0.5:  # 有价值的迁移到新系统
                        await self.intelligent_processor.process_connector_event(
                            ConnectorEvent(
                                connector_id=properties.get('connector_id'),
                                event_type=properties.get('event_type'),
                                content=content,
                                timestamp=properties.get('timestamp')
                            )
                        )
                        logger.info(f"Migrated valuable entity: {entity.entity_id}")
                    
                # 删除原始垃圾数据
                session.delete(entity)
                
            session.commit()
            logger.info("✅ Legacy data cleanup completed")
```

#### 3.2 迁移脚本
```bash
#!/bin/bash
# scripts/migrate_to_intelligent_storage.sh

echo "🚀 开始迁移到智能存储架构"

# 1. 备份当前数据库
cp ~/.linch-mind/development/database/linch_mind_dev.db \
   ~/.linch-mind/development/database/linch_mind_dev.backup.$(date +%Y%m%d_%H%M%S).db

# 2. 初始化Ollama模型
ollama pull nomic-embed-text
ollama pull llama3.2:3b

# 3. 创建新的存储目录结构
mkdir -p ~/.linch-mind/knowledge/{hot_index,warm_index,cold_archive,ollama_cache}

# 4. 运行数据清理和迁移
cd daemon && python -m scripts.cleanup_legacy_data

# 5. 更新代码到新实现
git checkout feature/intelligent-storage

echo "✅ 迁移完成"
```

## 📋 实施检查清单

### ✅ 准备阶段
- [ ] 安装Ollama并下载模型
- [ ] 备份当前数据库
- [ ] 创建新存储目录结构

### ✅ 开发阶段  
- [ ] 实现OllamaService
- [ ] 实现IntelligentEventProcessor
- [ ] 实现FAISSVectorStore
- [ ] 修改GenericEventStorage

### ✅ 测试阶段
- [ ] 单元测试新组件
- [ ] 集成测试智能处理流水线
- [ ] 性能测试向量检索

### ✅ 迁移阶段
- [ ] 清理现有垃圾数据
- [ ] 迁移有价值的历史数据
- [ ] 验证新系统工作正常

### ✅ 清理阶段
- [ ] 删除legacy代码
- [ ] 更新文档
- [ ] 性能优化

## 🎯 预期效果

### 存储优化
- **当前**: 8个事件 = ~80KB 垃圾数据
- **迁移后**: 2-3个有价值的向量化文档 = ~2KB

### 性能提升
- **检索速度**: 从SQL全表扫描 → FAISS向量检索
- **存储成本**: 95%+ 的空间节省
- **内容质量**: AI驱动的智能过滤

### 架构清理
- 移除事件存储的概念混乱
- 建立清晰的数据生命周期
- 实现真正的知识管理系统

---
*迁移计划版本: v1.0*  
*创建时间: 2025-08-15*  
*预计完成: 2周*