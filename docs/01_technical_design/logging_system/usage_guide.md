# 📚 日志系统使用指南

## 🚀 快速开始

### 1. 基础用法

```kotlin
import tech.linch.mind.logging.LoggerFactory

// 获取专用日志器
val collectorLogger = LoggerFactory.getCollectorLogger()
val parserLogger = LoggerFactory.getParserLogger()
val perfLogger = LoggerFactory.getPerformanceLogger()
```

### 2. 采集器日志记录

```kotlin
class FileSystemCollector {
    private val logger = LoggerFactory.getCollectorLogger()
    
    suspend fun processFile(filePath: String) {
        // 记录文件发现
        logger.logFileDiscovered(filePath, fileSize, "GENERAL_TEXT")
        
        // 记录处理开始
        val context = logger.logFileProcessingStart(filePath, "GENERAL_TEXT")
        
        try {
            // 文件处理逻辑
            val entities = parseFile(filePath)
            
            // 记录处理完成
            logger.logFileProcessingComplete(context, entities.size, "成功")
        } catch (e: Exception) {
            // 记录处理失败
            logger.logFileProcessingError(context, e)
        }
    }
}
```

### 3. 性能监控

```kotlin
suspend fun batchStoreEntities(entities: List<Entity>) {
    val perfLogger = LoggerFactory.getPerformanceLogger()
    
    val context = perfLogger.logOperationStart(
        "批量存储实体", 
        mapOf("entityCount" to entities.size)
    )
    
    try {
        // 执行存储操作
        storeEntities(entities)
        
        perfLogger.logOperationComplete(context, "成功")
        perfLogger.logSlowOperation(context, 1000) // 超过1秒警告
    } catch (e: Exception) {
        perfLogger.logOperationComplete(context, "失败: ${e.message}")
    }
}
```

### 4. 协程上下文追踪

```kotlin
suspend fun processFileWithContext(filePath: String) {
    LoggerFactory.withLoggingContext(mapOf(
        "fileId" to filePath.hashCode().toString(),
        "collectorId" to "filesystem_001",
        "sessionId" to getCurrentSessionId()
    )) {
        // 在这个作用域内的所有日志都会携带上下文信息
        logger.info { "开始处理文件: $filePath" }
        
        // 调用其他函数，上下文会自动传播
        parseFile(filePath)
        storeResults()
    }
}
```

## 🎯 专业使用场景

### 文件过滤调试

当需要调试为什么某些文件被跳过时：

```kotlin
fun shouldProcessFile(filePath: String): Boolean {
    val logger = LoggerFactory.getCollectorLogger()
    
    // 检查文件扩展名
    if (!filePath.endsWith(".md")) {
        logger.logFileFiltered(filePath, "不是Markdown文件", "扩展名过滤器")
        return false
    }
    
    // 检查排除模式
    if (filePath.contains(".obsidian")) {
        logger.logFileFiltered(filePath, "匹配排除模式 .obsidian/**", "路径过滤器")
        return false
    }
    
    // 检查文件大小
    val fileSize = File(filePath).length()
    if (fileSize > MAX_FILE_SIZE) {
        logger.logFileFiltered(filePath, "文件过大: ${fileSize}bytes", "大小过滤器")
        return false
    }
    
    logger.logFileDiscovered(filePath, fileSize, "GENERAL_TEXT")
    return true
}
```

### 批量处理统计

```kotlin
suspend fun processBatch(files: List<String>) {
    val logger = LoggerFactory.getCollectorLogger()
    val startTime = TimeSource.Monotonic.markNow()
    
    var successCount = 0
    var failureCount = 0
    var totalEntities = 0
    
    files.forEach { filePath ->
        try {
            val entities = processFile(filePath)
            successCount++
            totalEntities += entities.size
        } catch (e: Exception) {
            failureCount++
            logger.logFileProcessingError(
                ProcessingContext(filePath, TimeSource.Monotonic.markNow()), 
                e
            )
        }
    }
    
    val totalDuration = startTime.elapsedNow()
    logger.logBatchProcessingStats(
        batchSize = files.size,
        successCount = successCount,
        failureCount = failureCount,
        totalDuration = totalDuration,
        totalEntities = totalEntities
    )
}
```

### 存储操作记录

```kotlin
class HybridKnowledgeStorage {
    private val logger = LoggerFactory.getStorageLogger()
    
    suspend fun storeEntity(entity: KnowledgeEntity) {
        try {
            // 图存储
            graphStorage.store(entity)
            
            // 向量存储
            vectorStorage.index(entity)
            
            logger.logEntityStored(entity.id, entity.type, entity.sourcePath ?: "unknown")
        } catch (e: Exception) {
            logger.logStorageError(entity.id, e)
            throw e
        }
    }
    
    suspend fun batchStore(entities: List<KnowledgeEntity>) {
        logger.logBatchStoreStart(entities.size, "HybridStorage")
        val startTime = System.currentTimeMillis()
        
        var successCount = 0
        entities.forEach { entity ->
            try {
                storeEntity(entity)
                successCount++
            } catch (e: Exception) {
                // 错误已在storeEntity中记录
            }
        }
        
        val duration = System.currentTimeMillis() - startTime
        logger.logBatchStoreComplete(entities.size, successCount, duration)
    }
}
```

## 🔍 日志查看和分析

### 1. 实时监控

```bash
# 监控所有日志
tail -f ~/.linch-mind/logs/linch-mind.log

# 监控采集器日志
tail -f ~/.linch-mind/logs/collector.log

# 监控性能日志
tail -f ~/.linch-mind/logs/performance.log
```

### 2. 特定问题排查

```bash
# 查找文件过滤相关日志
grep "文件已过滤" ~/.linch-mind/logs/collector.log

# 查找慢操作
grep "慢操作警告" ~/.linch-mind/logs/performance.log

# 查找错误
grep "ERROR\|❌" ~/.linch-mind/logs/linch-mind.log
```

### 3. JSON日志分析

主日志文件为JSON格式，可使用jq工具分析：

```bash
# 提取所有错误消息
cat ~/.linch-mind/logs/linch-mind.log | jq 'select(.level=="ERROR") | .message'

# 统计各模块日志数量
cat ~/.linch-mind/logs/linch-mind.log | jq '.logger' | sort | uniq -c

# 查找特定时间段的日志
cat ~/.linch-mind/logs/linch-mind.log | jq 'select(.timestamp > "2025-01-26T10:00:00")'
```

## ⚙️ 配置调整

### 动态调整日志级别

修改 `src/desktopMain/resources/logback.xml`：

```xml
<!-- 调试采集器问题时，设置为TRACE -->
<logger name="tech.linch.mind.collector" level="TRACE" additivity="false">
    <appender-ref ref="COLLECTOR_FILE"/>
    <appender-ref ref="CONSOLE"/>
</logger>

<!-- 生产环境减少日志输出 -->
<logger name="tech.linch.mind.performance" level="WARN" additivity="false">
    <appender-ref ref="PERFORMANCE_FILE"/>
</logger>
```

### 调整文件轮转策略

```xml
<rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
    <!-- 每小时轮转 -->
    <fileNamePattern>~/.linch-mind/logs/collector.%d{yyyy-MM-dd-HH}.log</fileNamePattern>
    <!-- 保留24小时 -->
    <maxHistory>24</maxHistory>
</rollingPolicy>
```

## 🎯 最佳实践

### 1. 日志级别使用
- **TRACE**: 最详细的调试信息（通常关闭）
- **DEBUG**: 开发调试信息
- **INFO**: 重要业务操作
- **WARN**: 潜在问题
- **ERROR**: 错误和异常

### 2. 消息格式
```kotlin
// ✅ 好的日志消息
logger.info { "文件处理完成: $filePath (耗时: ${duration}ms, 实体: $count)" }

// ❌ 避免的日志消息
logger.info { "处理完成" } // 信息不足
logger.info { "File: $filePath, Duration: $duration, Count: $count" } // 格式不统一
```

### 3. 异常记录
```kotlin
// ✅ 完整的异常信息
logger.error(exception) { "文件解析失败: $filePath" }

// ❌ 丢失堆栈信息
logger.error { "解析失败: ${exception.message}" }
```

### 4. 性能敏感区域
```kotlin
// ✅ 使用lazy evaluation
logger.debug { "复杂计算结果: ${expensiveCalculation()}" }

// ❌ 总是执行计算
logger.debug("复杂计算结果: ${expensiveCalculation()}")
```

## 🚨 故障排查清单

当遇到采集问题时，按以下顺序检查日志：

1. **配置加载**: 查找 "⚙️ 配置已加载" 或 "❌ 配置错误"
2. **目录扫描**: 查找 "🔍 开始扫描目录" 和扫描结果
3. **文件过滤**: 查找 "🚫 文件已过滤" 了解跳过原因
4. **文件处理**: 查找 "🔄 开始处理文件" 和处理结果
5. **存储操作**: 查找 "💾 实体已存储" 确认存储成功

通过这些日志，可以精确定位问题所在的环节。