# NER系统架构设计 v2.0

## 🏗️ 整体架构：混合智能微模型系统

### 设计原则
1. **零硬编码** - 所有识别逻辑基于AI模型，无业务规则硬编码
2. **微模型分层** - 专用轻量级模型 + 通用语义模型的分层架构
3. **高性能优化** - 针对实时处理和跨平台一致性优化
4. **智能降级** - 模型失败时的优雅降级机制

### 核心接口设计

```kotlin
// 实体数据结构
data class ExtractedEntity(
    val text: String,              // 实体文本
    val type: EntityType,          // 实体类型（枚举）
    val confidence: Float,         // 置信度 [0.0, 1.0]
    val startOffset: Int,          // 在原文中的起始位置
    val endOffset: Int,            // 在原文中的结束位置
    val source: ProcessorSource,   // 来源处理器
    val metadata: Map<String, Any> = emptyMap() // 扩展元数据
)

// 处理器接口
interface EntityProcessor {
    val name: String
    val priority: Int              // 处理优先级
    
    suspend fun extract(
        text: String,
        context: ProcessingContext
    ): List<ExtractedEntity>
}

// 主服务接口
interface EntityExtractionService {
    suspend fun extractEntities(text: String): List<ExtractedEntity>
    fun registerProcessor(processor: EntityProcessor)
    fun getProcessorStats(): ProcessorStats
}
```

## 🧠 混合现实架构（基于可用模型）

### 1. 开源模型基础层 (Tier 1 - 立即可用)
- **多语言通用模型**: `multilingual-ner-140mb.onnx` (140MB量化后)
  - 基于xlm-roberta-base的开源NER模型
  - 支持中英文混合识别：PER, ORG, LOC, MISC
  - 准确率: ~87%, 推理延迟: ~200ms/1000字符
- **中文专用模型**: `chinese-ner-25mb.onnx` (25MB)
  - 基于HanLP的中文NER模型
  - 专门优化中文实体识别
  - 准确率: ~89%, 推理延迟: ~100ms/1000字符

### 2. 智能后处理层 (Tier 2 - 实体细分)
- **实体分类器**: `entity-classifier-5mb.onnx` (5MB)
  - 对MISC类型进行智能细分
  - 识别EMAIL, PHONE, URL, DATE, TIME等具体类型
  - 基于上下文的AI分类，零硬编码
- **置信度增强器**: 基于多模型一致性的置信度调整

### 3. 渐进式专用模型层 (Tier 3 - 未来升级)
- **联系信息微模型**: `contact-entities-5mb.onnx` (训练中)
- **时间实体微模型**: `temporal-entities-3mb.onnx` (训练中)  
- **数值实体微模型**: `numeric-entities-4mb.onnx` (训练中)
- **渐进替换机制**: 支持热替换，无需重启服务

### 4. 优雅降级层 (Tier 4 - 兜底保障)
- **基础文本分析器**: 当所有AI模型失败时的备选方案
- **统计模式检测**: 基于文本统计特征的实体候选识别
- **错误恢复机制**: 确保系统在任何情况下都能返回结果

## 🔄 处理流程

### 1. 预处理阶段
```kotlin
class TextPreprocessor {
    fun preprocess(text: String): ProcessedText {
        // 文本清洗
        // 句子分割
        // 基础标记化
        return ProcessedText(...)
    }
}
```

### 2. 现实模型处理阶段
```kotlin
class PragmaticModelProcessor {
    // 当前可用的开源模型
    private val multilingualModel = loadOpenSourceModel("multilingual-ner-140mb.onnx")
    private val chineseModel = loadOpenSourceModel("chinese-ner-25mb.onnx")
    private val entityClassifier = loadClassifier("entity-classifier-5mb.onnx")
    
    // 未来的专用微模型（可选）
    private val contactModel: OnnxModel? = tryLoadModel("contact-entities-5mb.onnx")
    private val temporalModel: OnnxModel? = tryLoadModel("temporal-entities-3mb.onnx")
    
    suspend fun process(text: String): List<ExtractedEntity> {
        // 优先使用专用微模型（如果可用）
        val specializedResults = trySpecializedModels(text)
        if (specializedResults.isNotEmpty()) {
            return specializedResults
        }
        
        // 否则使用开源模型组合
        val languageRatio = detectLanguageRatio(text)
        val baseResults = when {
            languageRatio.chinese > 0.7 -> chineseModel.predict(text)
            languageRatio.mixed > 0.3 -> multilingualModel.predict(text)
            else -> multilingualModel.predict(text)
        }
        
        // 智能后处理细分实体类型
        return baseResults.map { entity ->
            entity.copy(
                type = entityClassifier.refineType(entity.text, entity.type, text),
                confidence = adjustConfidence(entity, baseResults)
            )
        }
    }
    
    private suspend fun trySpecializedModels(text: String): List<ExtractedEntity> {
        val results = mutableListOf<ExtractedEntity>()
        
        // 逐个尝试可用的专用模型
        contactModel?.let { results.addAll(it.predict(text)) }
        temporalModel?.let { results.addAll(it.predict(text)) }
        
        return results
    }
}
```

### 3. 智能融合阶段
```kotlin
class IntelligentEntityMerger {
    fun merge(
        microResults: List<ExtractedEntity>,
        semanticResults: List<ExtractedEntity>
    ): List<ExtractedEntity> {
        return microResults.plus(semanticResults)
            .groupBy { it.textSpan }
            .map { (_, overlapping) ->
                // 使用贝叶斯融合而非硬编码优先级
                bayesianFusion(overlapping)
            }
            .filter { it.confidence > CONFIDENCE_THRESHOLD }
            .sortedBy { it.startOffset }
    }
    
    private fun bayesianFusion(candidates: List<ExtractedEntity>): ExtractedEntity {
        return candidates.maxByOrNull { 
            it.confidence * getPriorProbability(it.type, it.context)
        } ?: candidates.first()
    }
}
```

## 📦 资源管理

### 模型资源管理
```kotlin
// 跨平台资源管理
expect class ResourceManager {
    suspend fun loadModel(modelName: String): ByteArray
    suspend fun loadDictionary(dictName: String): List<String>
}

// 懒加载模型管理器
class ModelManager {
    private val models = mutableMapOf<String, OnnxModel>()
    
    suspend fun getModel(modelName: String): OnnxModel {
        return models.getOrPut(modelName) {
            loadAndInitializeModel(modelName)
        }
    }
}
```

### 缓存策略
```kotlin
class EntityCache {
    private val cache = LRUCache<String, List<ExtractedEntity>>(maxSize = 1000)
    
    fun get(textHash: String): List<ExtractedEntity>?
    fun put(textHash: String, entities: List<ExtractedEntity>)
    fun invalidate()
}
```

## 🎯 完全重构实现

### 零硬编码NER服务替换方案
```kotlin
// 完全基于AI模型的零硬编码NER服务
class ZeroHardcodeNERService : DataParser {
    private val microModelProcessor = MicroModelProcessor()
    private val fallbackProcessor = BasicTextAnalyzer() // 优雅降级
    
    override suspend fun parse(data: CollectedData): ParseResult {
        return try {
            val entities = microModelProcessor.process(data.content)
            ParseResult(
                success = true,
                parsedEntities = entities.map { it.toKnowledgeEntity() },
                processingMethod = "micro_model_ai"
            )
        } catch (modelException: ModelException) {
            // 模型失败时优雅降级到基础文本分析
            val basicEntities = fallbackProcessor.extractBasicEntities(data.content)
            ParseResult(
                success = true,
                parsedEntities = basicEntities,
                processingMethod = "fallback_basic",
                warning = "AI model unavailable, using basic analysis"
            )
        }
    }
}
```

## 🚀 扩展机制

### 插件接口
```kotlin
interface EntityProcessorPlugin {
    val metadata: PluginMetadata
    fun createProcessor(): EntityProcessor
    fun getConfigurationSchema(): JsonSchema
}

// 插件管理器
class PluginManager {
    fun loadPlugin(pluginPath: String): EntityProcessorPlugin
    fun registerPlugin(plugin: EntityProcessorPlugin)
    fun getAvailablePlugins(): List<PluginMetadata>
}
```

## ⚡ 性能优化

### 批处理支持
```kotlin
interface BatchEntityProcessor {
    suspend fun extractBatch(
        texts: List<String>
    ): List<List<ExtractedEntity>>
}
```

### 异步处理
```kotlin
class AsyncEntityService {
    suspend fun extractEntitiesAsync(
        text: String
    ): Deferred<List<ExtractedEntity>>
}
```

---

*该架构设计确保了系统的可扩展性、性能和与现有Linch Mind系统的无缝集成。*