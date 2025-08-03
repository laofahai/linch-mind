# 数据处理策略设计

## 🎯 核心问题

**是否所有采集器的数据都需要经过NER系统处理？**

答案是：**不是，需要基于数据类型进行智能路由**

## 🚦 数据处理路由策略

### 1. 文本内容 - 完整NER处理
**适用数据类型**:
- `TEXT_CONTENT` - 纯文本内容
- `DOCUMENT_METADATA` - 文档元数据中的文本字段
- `COMMUNICATION` - 邮件、消息等通信内容
- `CLIPBOARD_CONTENT` - 剪贴板文本内容

**处理流程**:
```
文本数据 → NER系统 → 实体提取 → 知识图谱构建
```

### 2. 结构化数据 - 轻量级处理
**适用数据类型**:
- `BROWSER_HISTORY` - 浏览器历史(仅URL、标题)
- `APPLICATION_USAGE` - 应用使用记录
- `CALENDAR_EVENTS` - 日历事件
- `SYSTEM_METRICS` - 系统指标

**处理策略**:
```kotlin
// 仅对特定字段进行NER处理
class StructuredDataProcessor {
    fun process(data: CollectedData): List<KnowledgeEntity> {
        return when(data.type) {
            DataType.BROWSER_HISTORY -> {
                // 仅对页面标题进行NER
                val title = extractTitle(data.content)
                nerService.extractEntities(title)
            }
            DataType.CALENDAR_EVENTS -> {
                // 仅对事件标题和描述进行NER
                val eventText = extractEventText(data.content)
                nerService.extractEntities(eventText)
            }
            else -> emptyList()
        }
    }
}
```

### 3. 媒体内容 - 跳过NER处理
**适用数据类型**:
- `IMAGE_CONTENT` - 图像内容
- `AUDIO_CONTENT` - 音频内容  
- `VIDEO_CONTENT` - 视频内容

**处理策略**:
```kotlin
// 直接转换为KnowledgeEntity，不进行NER
class MediaDataProcessor {
    fun process(data: CollectedData): List<KnowledgeEntity> {
        return listOf(
            KnowledgeEntity(
                id = data.id,
                type = EntityType.WORK, // 直接分类为作品
                title = extractMediaTitle(data),
                content = data.content,
                // ... 其他字段
            )
        )
    }
}
```

## 🏗️ 微模型架构重构方案

### 零硬编码数据处理路由器
```kotlin
interface AIDataProcessor {
    val supportedDataTypes: Set<DataType>
    suspend fun process(data: CollectedData): List<KnowledgeEntity>
    suspend fun canHandle(data: CollectedData): Float // 返回置信度而非布尔值
}

class IntelligentDataRouter {
    private val microModelProcessor = MicroModelNERProcessor()
    private val basicAnalyzer = BasicTextAnalyzer() // 降级处理器
    
    suspend fun route(data: CollectedData): AIDataProcessor {
        return when {
            // 文本内容：使用微模型NER处理
            data.type in setOf(
                DataType.TEXT_CONTENT,
                DataType.DOCUMENT_METADATA, 
                DataType.COMMUNICATION,
                DataType.CLIPBOARD_CONTENT
            ) -> microModelProcessor
            
            // 结构化数据：智能字段提取
            data.type in setOf(
                DataType.BROWSER_HISTORY,
                DataType.APPLICATION_USAGE,
                DataType.CALENDAR_EVENTS
            ) -> StructuredFieldProcessor(microModelProcessor)
            
            // 媒体内容：元数据提取
            data.type in setOf(
                DataType.IMAGE_CONTENT,
                DataType.AUDIO_CONTENT,
                DataType.VIDEO_CONTENT  
            ) -> MediaMetadataProcessor()
            
            else -> basicAnalyzer
        }
    }
}
```

### 更新后的TextParser
```kotlin
class EnhancedTextParser : DataParser {
    private val nerService = EntityExtractionService()
    private val processingRouter = DataProcessingRouter()
    
    override suspend fun parse(data: CollectedData): ParseResult {
        val processor = processingRouter.route(data)
        
        return try {
            val entities = processor.process(data)
            ParseResult(
                success = true,
                parsedEntities = entities,
                // ...
            )
        } catch (e: Exception) {
            ParseResult(
                success = false,
                error = "Processing failed: ${e.message}"
            )
        }
    }
}
```

## 📊 性能影响分析

### 处理量估算
假设日均数据采集：
- **文本内容**: 1000条 → 需要完整NER (高CPU)
- **浏览器历史**: 5000条 → 仅标题NER (中CPU)  
- **应用使用**: 10000条 → 跳过NER (低CPU)
- **媒体文件**: 100条 → 跳过NER (低CPU)

### 性能收益
通过智能路由：
- **CPU使用降低**: 约60%的数据跳过完整NER处理
- **内存占用减少**: 媒体文件不占用NER模型内存
- **响应速度提升**: 非文本数据快速处理

## 🎯 配置化路由策略

### 用户可配置处理级别
```kotlin
enum class ProcessingLevel {
    MINIMAL,    // 仅基础信息提取
    STANDARD,   // 文本内容NER处理
    INTENSIVE,  // 所有内容深度分析
    CUSTOM      // 用户自定义规则
}

data class ProcessingConfig(
    val level: ProcessingLevel = ProcessingLevel.STANDARD,
    val customRules: Map<DataType, ProcessorType> = emptyMap(),
    val enableNerFor: Set<DataType> = defaultNerTypes
)
```

### 动态处理策略
```kotlin
class AdaptiveProcessingStrategy {
    fun determineProcessingLevel(
        data: CollectedData,
        systemLoad: SystemLoad,
        userPreferences: ProcessingConfig
    ): ProcessorType {
        // 基于系统负载和用户偏好动态决定处理策略
        return when {
            systemLoad.cpuUsage > 80 -> ProcessorType.DIRECT
            data.content.length > 100000 -> ProcessorType.STRUCTURED  
            userPreferences.level == ProcessingLevel.MINIMAL -> ProcessorType.DIRECT
            else -> ProcessorType.NER
        }
    }
}
```

## 🔄 直接重构策略

### 全面替换方案
1. **完全删除** 现有 `TextParser.kt` 
2. **直接实现** 新的 `EntityAwareDataParser`
3. **一次性切换** 到智能路由架构

### 重构优势
- **更清晰的架构** - 没有历史包袱
- **更高的性能** - 专门优化的处理流程
- **更好的可维护性** - 统一的设计原则

## 💡 总结

**不是所有数据都需要完整NER处理**。通过智能路由策略：

1. **文本内容** → 完整NER系统
2. **结构化数据** → 选择性NER处理  
3. **媒体内容** → 直接转换为实体
4. **系统数据** → 最小化处理

这样既保证了文本内容的智能处理质量，又避免了不必要的计算开销，是最优的架构方案。

---

*该策略确保NER系统专注于最有价值的文本内容，同时保持整体系统的高效运行。*