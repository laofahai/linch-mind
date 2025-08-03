# NER系统实施路线图 v2.0

## 🎯 零硬编码微模型架构实施原则

1. **零硬编码** - 所有识别逻辑基于AI模型，无业务规则硬编码
2. **微模型优先** - 专用轻量级模型处理常见实体，通用模型处理复杂语义
3. **性能优化** - 智能模型调度，避免不必要的大模型推理
4. **优雅降级** - 模型失败时的基础文本分析备选方案

## 🚀 现实可行的实施路径（修正版）

### ⚠️ 关键调整：模型获取现实化
鉴于专用微模型需要从零训练，我们采用**渐进式策略**：
1. **阶段1-2**：基于开源模型构建可用系统 
2. **阶段3+**：并行训练专用模型逐步替换

### 阶段1：开源模型集成 (Week 1-2) 
**目标**: 基于现有开源NER模型建立可用系统

#### 1.1 开源模型下载与集成
```bash
# 下载现有开源NER模型
wget https://huggingface.co/wietsedv/xlm-roberta-base-ft-udpos28-en/resolve/main/model.onnx
wget https://github.com/hankcs/HanLP/releases/download/v2.1.0-beta.4/zh_ner.onnx

# 集成到KMP项目资源
mkdir -p src/commonMain/resources/models/
cp xlm-roberta-base-ft-udpos28-en.onnx src/commonMain/resources/models/multilingual-ner-50mb.onnx
cp zh_ner.onnx src/commonMain/resources/models/chinese-ner-25mb.onnx
```

#### 1.2 KMP ONNX运行时集成
```kotlin
// 现实版本：支持现有模型的管理器
expect class OnnxModelManager {
    suspend fun loadModel(modelPath: String): OnnxModel
    fun releaseModel(modelName: String)
    fun getSupportedModels(): List<ModelInfo>
}

data class ModelInfo(
    val name: String,
    val path: String,
    val sizeBytes: Long,
    val supportedLanguages: Set<String>,
    val entityTypes: Set<String>,
    val expectedAccuracy: Float
)
```

#### 1.2 微模型抽象接口
```kotlin
// 零硬编码的AI实体提取器
interface AIEntityExtractor {
    val modelName: String
    val modelSize: Long
    suspend fun extract(text: String): List<ExtractedEntity>
    suspend fun isModelReady(): Boolean
}

// 微模型实现基类
abstract class MicroModelExtractor(
    private val modelPath: String,
    private val modelManager: OnnxModelManager
) : AIEntityExtractor {
    
    private val model by lazy { 
        runBlocking { modelManager.loadModel(modelPath) }
    }
    
    override suspend fun extract(text: String): List<ExtractedEntity> {
        return model.predict(text).map { prediction ->
            ExtractedEntity(
                text = prediction.text,
                type = mapPredictionToEntityType(prediction.type),
                confidence = prediction.confidence,
                startOffset = prediction.startOffset,
                endOffset = prediction.endOffset,
                source = modelName
            )
        }
    }
    
    protected abstract fun mapPredictionToEntityType(modelType: String): EntityType
}
```

### 阶段2：智能后处理系统 (Week 3-4)
**目标**: 实现零硬编码的后处理分类系统（替代专用微模型）

#### 2.1 智能实体分类器（替代专用微模型）
```kotlin
// 使用轻量级AI分类器进行后处理，避免硬编码
class IntelligentEntityClassifier(
    private val contextAnalyzer: ContextAnalysisModel // 5MB小型分类模型
) {
    suspend fun refineEntityType(
        text: String,
        rawLabel: String, 
        context: String
    ): EntityType {
        // 零硬编码：完全基于AI模型分类
        return when (rawLabel) {
            "MISC" -> contextAnalyzer.classifyMiscEntity(text, context)
            "ORG" -> contextAnalyzer.distinguishOrgType(text, context)
            "PER" -> contextAnalyzer.refinePerson(text, context)
            else -> EntityType.fromBIOLabel(rawLabel)
        }
    }
}

class ContextAnalysisModel(
    private val miniClassifier: OnnxModel // 轻量级分类模型
) {
    suspend fun classifyMiscEntity(text: String, context: String): EntityType {
        val features = extractContextFeatures(text, context)
        val prediction = miniClassifier.predict(features)
        
        return when (prediction.label) {
            "CONTACT_INFO" -> inferContactSubtype(text, prediction.confidence)
            "TEMPORAL" -> inferTemporalSubtype(text, prediction.confidence)
            "NUMERIC" -> inferNumericSubtype(text, prediction.confidence)
            "TECHNOLOGY" -> EntityType.TECHNOLOGY
            else -> EntityType.CONCEPT
        }
    }
}
```

#### 2.2 现实版本的NER服务组合
```kotlin
// 基于开源模型 + 智能后处理的现实方案
class PragmaticNERService(
    private val backboneModel: OnnxModel,        // 50MB开源通用模型
    private val entityClassifier: IntelligentEntityClassifier  // 5MB分类器
) {
    suspend fun extractEntities(text: String): List<ExtractedEntity> {
        // 步骤1：使用开源通用模型获取基础识别结果
        val rawEntities = backboneModel.predict(text)
        
        // 步骤2：智能后处理分类（替代专用微模型）
        return rawEntities.map { raw ->
            ExtractedEntity(
                text = raw.text,
                type = entityClassifier.refineEntityType(
                    raw.text, 
                    raw.label, 
                    extractContext(text, raw.start, raw.end)
                ),
                confidence = calculateAdjustedConfidence(raw),
                startOffset = raw.start,
                endOffset = raw.end,
                source = "BackboneModel+IntelligentClassifier"
            )
        }
    }
}
```

#### 2.3 优雅降级机制
```kotlin
// 当AI模型不可用时的基础文本分析
class BasicTextAnalyzer {
    suspend fun extractBasicEntities(text: String): List<ExtractedEntity> {
        // 使用基础的文本分析技术（非硬编码正则）
        return listOf(
            extractByWordBoundaries(text),
            extractByCapitalization(text),
            extractByFormat(text)  // 基于通用格式特征，而非特定正则
        ).flatten()
    }
    
    private fun extractByFormat(text: String): List<ExtractedEntity> {
        // 基于统计特征而非硬编码规则
        return statisticalPatternDetector.findPotentialEntities(text)
    }
}
```
```

### 阶段3：专用模型训练启动 (Week 5-8)  
**目标**: 并行开展专用微模型训练，为渐进式替换做准备

#### 3.1 训练数据收集与准备
```python
# 专用微模型训练数据收集流水线
class MicroModelTrainingPipeline:
    def __init__(self):
        self.data_sources = {
            "public_datasets": [
                "CoNLL-2003",      # 通用NER数据
                "OntoNotes 5.0",   # 多语言实体
                "MSRA NER",        # 中文NER数据
                "Weibo NER"        # 中文社交媒体数据
            ],
            "synthetic_generators": {
                "contact": ContactDataGenerator(),
                "temporal": TemporalDataGenerator(),
                "numeric": NumericDataGenerator()
            }
        }
    
    def prepare_contact_training_data(self):
        """为联系信息微模型准备训练数据"""
        return [
            ("发邮件到 john@company.com 确认会议时间", [("john@company.com", "EMAIL", 4, 20)]),
            ("访问API接口 https://api.service.com/v1/users", [("https://api.service.com/v1/users", "URL", 7, 37)]),
            ("联系手机：+86-138-1234-5678", [("+86-138-1234-5678", "PHONE", 5, 21)]),
            ("关注Twitter @username", [("@username", "SOCIAL_HANDLE", 8, 17)])
        ]
        
    def prepare_temporal_training_data(self):
        """为时间实体微模型准备训练数据"""
        return [
            ("会议定在2025年7月25日下午3点", [("2025年7月25日", "DATE", 4, 15), ("下午3点", "TIME", 15, 19)]),
            ("任务预计需要3个工作日完成", [("3个工作日", "DURATION", 5, 9)]),
            ("每周一上午9点例会", [("每周一", "RECURRING", 0, 3), ("上午9点", "TIME", 3, 7)])
        ]
```

#### 3.2 微模型训练实施
```python
# 专用微模型训练脚本
class MicroModelTrainer:
    def __init__(self, domain: str):
        self.domain = domain
        self.base_model = "bert-base-multilingual-cased"
        self.training_config = {
            "epochs": 50,
            "batch_size": 16,
            "learning_rate": 2e-5,
            "max_length": 512
        }
    
    def train_contact_model(self, training_data: List[TrainingExample]):
        """训练联系信息专用模型"""
        model = AutoModelForTokenClassification.from_pretrained(
            self.base_model,
            num_labels=len(CONTACT_LABELS)  # EMAIL, PHONE, URL等
        )
        
        # 训练模型
        trainer = Trainer(model, training_data, self.training_config)
        trained_model = trainer.train()
        
        # 转换为ONNX并量化
        onnx_model = convert_to_onnx(trained_model, "contact-entities-5mb.onnx")
        quantized_model = quantize_model(onnx_model, precision="int8")
        
        return quantized_model
    
    def validate_model_performance(self, model, test_data):
        """验证模型性能是否达到预期"""
        predictions = model.predict(test_data)
        metrics = calculate_metrics(predictions, test_data.labels)
        
        return {
            "accuracy": metrics.accuracy,
            "precision": metrics.precision,
            "recall": metrics.recall,
            "f1_score": metrics.f1
        }
```

#### 3.3 渐进式模型替换策略
```kotlin
// 支持渐进式模型替换的架构
class ProgressiveModelManager {
    private val availableModels = mutableMapOf<String, ModelInfo>()
    private val modelPriority = listOf(
        "specialized_micro_models",  // 最优：训练好的专用微模型
        "general_with_classifier",   // 当前：通用模型+分类器
        "basic_text_analysis"        // 兜底：基础文本分析
    )
    
    suspend fun getBestAvailableModel(entityDomain: String): NERProcessor {
        return when (entityDomain) {
            "contact" -> tryLoadModel("contact-entities-5mb.onnx") 
                ?: fallbackToGeneralModel()
            "temporal" -> tryLoadModel("temporal-entities-3mb.onnx")
                ?: fallbackToGeneralModel() 
            "numeric" -> tryLoadModel("numeric-entities-4mb.onnx")
                ?: fallbackToGeneralModel()
            else -> fallbackToGeneralModel()
        }
    }
    
    private suspend fun fallbackToGeneralModel(): NERProcessor {
        // 降级到当前可用的通用模型+分类器方案
        return PragmaticNERService(backboneModel, entityClassifier)
    }
}
```

class PriorityAssignmentService {
    fun assignPriority(filePath: String, fileType: String): ProcessingPriority {
        return when {
            filePath.contains("node_modules") -> ProcessingPriority.IGNORE
            filePath.contains("/src/") -> ProcessingPriority.HIGH
            fileType in setOf("md", "kt", "java", "py") -> ProcessingPriority.HIGH
            else -> ProcessingPriority.MEDIUM
        }
    }
}
```

#### 3.2 容量控制与增量处理
```kotlin
class SmartDataProcessor : DataParser {
    private val priorityService = PriorityAssignmentService()
    private val incrementalProcessor = IncrementalProcessor()
    
    override suspend fun parse(data: CollectedData): ParseResult {
        // 1. 分配优先级
        val priority = priorityService.assignPriority(data.sourceInfo.path, data.type.name)
        
        // 2. 检查是否需要处理
        if (priority == ProcessingPriority.IGNORE) {
            return ParseResult.skipped()
        }
        
        // 3. 增量处理检查
        val processResult = incrementalProcessor.processIfChanged(data.sourceInfo.path)
        if (processResult.isSkipped) {
            return ParseResult.fromCache(processResult)
        }
        
        // 4. 容量控制处理
        return when {
            data.content.length > MAX_FILE_SIZE -> processLargeContent(data)
            priority == ProcessingPriority.HIGH -> processWithFullNER(data)
            else -> processWithBasicExtraction(data)
        }
    }
}
```

#### 3.3 用户配置机制
```kotlin
data class ProcessingConfig(
    val excludePatterns: List<String> = listOf(
        "**/node_modules/**", "**/build/**", "**/.git/**"
    ),
    val resourceLimits: ResourceLimits = ResourceLimits(
        maxFileSizeMb = 10,
        backgroundThreads = 4
    )
)
```

### 阶段4：智能调度与性能优化 (Week 7-8)
**目标**: 实现智能模型调度和性能优化机制

#### 4.1 核心多语言模型（Tier 1）
```kotlin
class CoreMultilingualProcessor : EntityExtractor {
    private val coreModel by lazy { 
        loadCoreModel("core-multilingual-ner.onnx") 
    }
    
    val supportedLanguages = setOf("zh", "en", "es", "fr", "de", "ja", "ko", "ru")
    
    override suspend fun extract(text: String): List<ExtractedEntity> {
        return coreModel.predict(text)
    }
}
```

#### 4.2 智能语言路由系统
```kotlin
class IntelligentLanguageRouter {
    private val languageDetector = FastLanguageDetector()
    private val coreProcessor = CoreMultilingualProcessor()
    private val specialistProcessors = mutableMapOf<String, SpecialistLanguageProcessor>()
    private val fallbackProcessor = LightweightRuleProcessor()
    
    suspend fun routeAndProcess(text: String): List<ExtractedEntity> {
        val detectedLanguage = languageDetector.detect(text)
        
        return when {
            specialistProcessors.containsKey(detectedLanguage.code) -> 
                specialistProcessors[detectedLanguage.code]!!.extract(text)
            coreProcessor.supportedLanguages.contains(detectedLanguage.code) -> 
                coreProcessor.extract(text)
            else -> {
                notifyLanguagePackAvailable(detectedLanguage.code)
                fallbackProcessor.extract(text)
            }
        }
    }
}
```

#### 4.3 动态模型管理
```kotlin
class LanguagePackManager {
    private val modelRegistry = ModelRegistry()
    private val modelCache = ModelCache(maxModelsInMemory = 3)
    
    suspend fun downloadLanguagePack(languageCode: String): DownloadResult {
        val modelInfo = modelRegistry.getModelInfo(languageCode)
        return downloadManager.download(modelInfo)
    }
    
    fun getAvailableLanguages(): List<LanguageInfo> {
        return modelRegistry.listAvailableModels()
    }
}
```

## ⚡ 性能优化策略

### 1. 延迟加载
- ONNX模型仅在首次使用时加载
- 词典文件按需加载
- 正则表达式预编译缓存

### 2. 文本长度限制
```kotlin
class TextProcessor {
    fun shouldProcess(text: String): Boolean {
        return text.length < 10000 // 超长文本跳过NER
    }
}
```

### 3. 简单缓存
```kotlin
class SimpleEntityCache {
    private val cache = LinkedHashMap<String, List<ExtractedEntity>>(100, 0.75f, true)
    
    fun get(textHash: String): List<ExtractedEntity>? = cache[textHash]
    fun put(textHash: String, entities: List<ExtractedEntity>) {
        if (cache.size >= 100) cache.remove(cache.keys.first())
        cache[textHash] = entities
    }
}
```

## 📊 修正后的成功指标

### 现实版本性能目标
- **处理速度**: < 250ms/1000字符（通用模型+分类器）< 50ms（未来专用微模型）
- **内存占用**: < 100MB（当前方案）< 300MB（完整微模型方案）
- **启动延迟**: < 5秒（开源模型加载）< 3秒（量化优化后）
- **准确率**: > 85%（通用实体）> 88%（后处理增强）> 92%（未来专用模型）

### 现实功能目标
- **零硬编码**: 所有识别逻辑基于AI模型（包括后处理分类器）
- **渐进式升级**: 从开源模型平滑过渡到专用微模型
- **中英混合**: 基于多语言预训练模型的混合文本处理
- **优雅降级**: 多层次备选方案确保系统可用性

## 🎯 下一阶段计划

### 性能优化阶段 (Month 2)
1. 批处理优化
2. 异步处理
3. 模型量化和优化

### 功能增强阶段 (Month 3)
1. 更多实体类型
2. 关系抽取
3. 上下文理解

## 💡 关键原则

1. **先跑起来** - 基础功能优先，完美主义后置
2. **性能导向** - 每个决策都考虑性能影响
3. **简单直接** - 避免过度抽象和复杂设计
4. **可观测性** - 添加基础监控，便于优化

---

*专注于V0 PoC的核心价值：让系统真正可用，为后续迭代奠定基础。*