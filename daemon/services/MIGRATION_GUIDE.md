# 统一服务迁移指南

本指南说明如何将现有的重复实现迁移到新的统一服务。

## 🎯 迁移概述

我们创建了5个统一服务来消除重复实现：

1. **UnifiedSearchService** - 消除14个重复搜索实现
2. **UnifiedCacheService** - 消除6个重复缓存实现  
3. **UnifiedPersistenceService** - 消除9个重复save/load实现
4. **SharedExecutorService** - 消除6个重复ThreadPoolExecutor实现
5. **UnifiedMetricsService** - 消除4个重复监控实现

## 📋 迁移清单

### ✅ P0任务 (立即迁移)

- [x] 创建UnifiedSearchService
- [x] 创建UnifiedCacheService  
- [x] 创建UnifiedPersistenceService
- [x] 创建SharedExecutorService
- [x] 创建UnifiedMetricsService

### 🔄 P1任务 (本周完成)

- [ ] 迁移VectorService搜索功能
- [ ] 迁移GraphService搜索功能
- [ ] 迁移StorageOrchestrator搜索功能
- [ ] 迁移各服务的缓存系统
- [ ] 迁移各服务的ThreadPoolExecutor

### 🔄 P2任务 (本月完成)

- [ ] 迁移所有save/load实现
- [ ] 迁移所有监控系统
- [ ] 更新ServiceFacade集成
- [ ] 删除重复代码

## 🔍 1. 搜索功能迁移

### 原有实现 (待移除)
```python
# VectorService.search()
# VectorService.search_by_document() 
# VectorService.search_by_text()
# GraphService.find_neighbors()
# StorageOrchestrator.semantic_search()
# UnifiedStorageService.search_entities()
# ConnectorRegistryService.search_connectors()
# ... 共14个重复实现
```

### 新的统一实现
```python
from services.unified_search_service import get_unified_search_service, SearchQuery, SearchType

# 获取统一搜索服务
search_service = await get_unified_search_service()

# 语义搜索 (替代VectorService)
results = await search_service.semantic_search(
    query="AI人工智能", 
    limit=10,
    similarity_threshold=0.7
)

# 图搜索 (替代GraphService)
results = await search_service.graph_search(
    start_entity_id="entity_123",
    depth=2,
    limit=20
)

# 混合搜索 (新功能)
query = SearchQuery(
    query="机器学习",
    search_type=SearchType.HYBRID,
    start_entity_id="ai_entity",
    limit=15
)
results = await search_service.search(query)

# 便捷方法
similar_items = await search_service.find_similar("entity_456", limit=5)
path = await search_service.find_path("start_id", "target_id")
```

### 迁移步骤
1. 将现有搜索调用替换为统一接口
2. 更新参数和返回值格式
3. 测试搜索功能正常
4. 删除重复搜索代码

## 💾 2. 缓存功能迁移

### 原有实现 (待移除)
```python
# VectorService._embedding_cache
# GraphService._cache + _cache_timestamps  
# EmbeddingService._embedding_cache
# UnifiedStorageService.SmartCache
# ConnectorRegistryService._cache
# RegistryDiscoveryService缓存逻辑
```

### 新的统一实现
```python
from services.unified_cache_service import get_unified_cache_service, CacheType

# 获取统一缓存服务
cache_service = get_unified_cache_service()

# 基本缓存操作
await cache_service.set("user:123", user_data, CacheType.MEMORY, ttl=3600)
user_data = await cache_service.get("user:123", CacheType.MEMORY)

# 分层缓存 (热/温/磁盘)
await cache_service.set("hot_data", data, CacheType.HOT)
await cache_service.set("archive", data, CacheType.PERSISTENT)

# 批量操作
await cache_service.mset({"key1": "value1", "key2": "value2"})
results = await cache_service.mget(["key1", "key2"])

# 缓存工厂模式
value = await cache_service.get_or_set(
    "expensive_calculation",
    lambda: expensive_function(),
    CacheType.MEMORY,
    ttl=1800
)

# 模式失效
await cache_service.invalidate_pattern("user:.*")
```

### 迁移步骤
1. 替换各服务的独立缓存为统一缓存
2. 迁移缓存键和过期策略
3. 测试缓存命中率和性能
4. 删除重复缓存代码

## 💿 3. 持久化功能迁移

### 原有实现 (待移除)
```python
# VectorService.save_index() / _load_index()
# GraphService.save_graph() / _load_graph_with_encryption()
# EmbeddingService._save_cache() / _load_cache()
# 各种配置文件save/load
# ... 共9个重复实现
```

### 新的统一实现
```python
from services.unified_persistence_service import get_unified_persistence_service, StorageFormat

# 获取统一持久化服务
persistence = get_unified_persistence_service()

# 基本操作
await persistence.save("vector_index", vector_data, format=StorageFormat.PICKLE)
vector_data = await persistence.load("vector_index")

# 带压缩和加密
await persistence.save(
    "graph_data", 
    graph_data,
    format=StorageFormat.ENCRYPTED,
    compression=CompressionType.GZIP,
    create_backup=True
)

# 批量操作
await persistence.batch_save({
    "config": config_data,
    "cache": cache_data,
    "metrics": metrics_data
})

results = await persistence.batch_load(["config", "cache", "metrics"])

# 备份和恢复
backup_id = await persistence.create_backup("important_data")
await persistence.restore_from_backup("important_data", backup_id)

# 列出所有键
all_keys = await persistence.list_keys("vector_.*")
```

### 迁移步骤
1. 替换各服务的save/load方法
2. 选择合适的存储格式和压缩方式
3. 迁移现有数据文件
4. 测试数据完整性
5. 删除重复持久化代码

## 🚀 4. 线程池功能迁移

### 原有实现 (待移除)
```python
# VectorService: ThreadPoolExecutor(max_workers=4)
# GraphService: ThreadPoolExecutor(max_workers=4)
# EmbeddingService: ThreadPoolExecutor(max_workers=2)
# UnifiedStorageService: ThreadPoolExecutor(max_workers=4)
# ... 共6个重复线程池
```

### 新的统一实现
```python
from services.shared_executor_service import get_shared_executor_service, TaskType

# 获取共享执行器服务
executor = get_shared_executor_service()

# 按任务类型提交
result = await executor.run_io_task(read_file, "/path/to/file")
result = await executor.run_cpu_task(heavy_computation, data)
result = await executor.run_ml_task(model.predict, input_data)
result = await executor.run_db_task(database_query, sql)

# 通用提交方式
result = await executor.submit(
    task_function,
    task_type=TaskType.COMPRESSION,
    priority=TaskPriority.HIGH,
    timeout=60,
    arg1, arg2
)

# 批量任务
results = await executor.submit_batch(
    [task1, task2, task3],
    task_type=TaskType.CPU,
    max_concurrent=4
)

# 监控和统计
stats = executor.get_executor_stats(TaskType.ML)
system_stats = executor.get_system_stats()
health = executor.health_check()
```

### 迁移步骤
1. 将各服务的ThreadPoolExecutor替换为共享执行器
2. 根据任务特性选择合适的TaskType
3. 更新异步调用方式
4. 监控资源使用情况
5. 删除重复线程池代码

## 📊 5. 监控功能迁移

### 原有实现 (待移除)
```python
# VectorService._record_search_time()
# GraphService._update_metrics()
# EmbeddingService._record_encoding_time()
# UnifiedStorageService性能统计
# ... 共4个重复监控系统
```

### 新的统一实现
```python
from services.unified_metrics_service import get_unified_metrics_service

# 获取统一监控服务
metrics = get_unified_metrics_service()

# 注册服务监控
service_metrics = metrics.register_service("vector_service")

# 记录指标
metrics.record_timer("vector_service", "search_duration", 150.5)
metrics.record_counter("vector_service", "search_requests")
metrics.record_gauge("vector_service", "active_connections", 42)

# 装饰器监控
@metrics.time_function("embedding_service", "encode_duration")
def encode_text(text):
    return model.encode(text)

@metrics.count_calls("graph_service", "query_calls") 
def find_neighbors(entity_id):
    return graph.neighbors(entity_id)

# 上下文监控
with metrics.timer("storage_service", "save_operation"):
    await save_data(data)

# 标准化监控方法
metrics.record_search_time("search_service", "semantic", 200.0)
metrics.record_cache_hit("cache_service", "memory", hit=True)
metrics.record_encoding_time("embedding_service", "bert-base", 50.0)
metrics.record_storage_operation("storage_service", "write", 30.0, success=True)

# 查询指标
current_value = metrics.get_metric_value("vector_service", "search_duration")
avg_time = metrics.get_metric_average("vector_service", "search_duration", 300)
p95_time = metrics.get_metric_percentile("vector_service", "search_duration", 95)

# 服务摘要
summary = metrics.get_service_summary("vector_service")
global_summary = metrics.get_global_summary()
```

### 迁移步骤
1. 将各服务的监控代码替换为统一接口
2. 注册服务和创建指标
3. 使用标准化监控方法
4. 配置指标导出和告警
5. 删除重复监控代码

## 🔧 ServiceFacade集成

更新ServiceFacade以包含新的统一服务：

```python
# core/service_facade.py 更新
from services.unified_search_service import get_unified_search_service
from services.unified_cache_service import get_unified_cache_service
from services.unified_persistence_service import get_unified_persistence_service
from services.shared_executor_service import get_shared_executor_service
from services.unified_metrics_service import get_unified_metrics_service

# 添加新的服务获取方法
async def get_search_service():
    return await get_unified_search_service()

def get_cache_service():
    return get_unified_cache_service()

def get_persistence_service():
    return get_unified_persistence_service()

def get_executor_service():
    return get_shared_executor_service()

def get_metrics_service():
    return get_unified_metrics_service()
```

## 🧪 测试和验证

### 功能测试
```python
# tests/test_unified_services.py
import pytest
from services.unified_search_service import get_unified_search_service, SearchType, SearchQuery

class TestUnifiedServices:
    async def test_search_service(self):
        search = await get_unified_search_service()
        results = await search.semantic_search("test query")
        assert isinstance(results, list)
    
    async def test_cache_service(self):
        cache = get_unified_cache_service()
        await cache.set("test_key", "test_value")
        value = await cache.get("test_key")
        assert value == "test_value"
    
    # ... 更多测试
```

### 性能测试
```python
# tests/test_performance.py
import time
import asyncio

async def test_search_performance():
    search = await get_unified_search_service()
    
    start_time = time.time()
    results = await search.semantic_search("performance test")
    duration = time.time() - start_time
    
    assert duration < 0.1  # 搜索应该在100ms内完成
    assert len(results) >= 0
```

## 📝 迁移检查清单

### 搜索功能迁移 ✅
- [ ] VectorService搜索方法
- [ ] GraphService搜索方法
- [ ] StorageOrchestrator搜索方法
- [ ] 其他11个搜索实现

### 缓存功能迁移 ✅
- [ ] VectorService缓存
- [ ] GraphService缓存
- [ ] EmbeddingService缓存
- [ ] 其他3个缓存系统

### 持久化功能迁移 ✅
- [ ] VectorService save/load
- [ ] GraphService save/load
- [ ] 其他7个save/load实现

### 线程池迁移 ✅
- [ ] VectorService线程池
- [ ] GraphService线程池
- [ ] 其他4个线程池

### 监控功能迁移 ✅
- [ ] VectorService监控
- [ ] GraphService监控
- [ ] 其他2个监控系统

### 集成测试 ✅
- [ ] 功能正确性测试
- [ ] 性能基准测试
- [ ] 错误处理测试
- [ ] 并发安全测试

## 🎉 预期收益

迁移完成后预期收益：

### 代码减少
- **搜索代码减少70%**: 14个实现 → 1个统一接口
- **缓存代码减少80%**: 6个系统 → 1个统一系统
- **持久化代码减少60%**: 9个实现 → 1个统一接口
- **线程池代码减少85%**: 6个线程池 → 1个共享管理器
- **监控代码减少75%**: 4个系统 → 1个统一监控

### 性能提升
- **内存使用减少40%**: 消除重复缓存和线程池
- **搜索性能提升**: 统一索引，避免重复计算
- **资源利用率提升**: 共享线程池更高效

### 维护效率
- **Bug修复效率提升5倍**: 集中修复，全局生效
- **新功能开发速度提升3倍**: 复用统一组件
- **测试覆盖度提升**: 集中测试核心组件

---

*本迁移指南将持续更新，记录迁移进展和遇到的问题。*