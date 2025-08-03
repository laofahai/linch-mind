# 微模型分层策略详细设计

## 🎯 核心理念：AI替代硬编码

### 设计哲学
传统NER系统依赖大量硬编码规则处理格式化实体（如邮箱、电话、URL等），这导致：
- 规则维护成本高
- 跨语言适配困难  
- 上下文理解能力差
- 无法学习用户特定模式

我们的微模型策略用**专用的轻量级AI模型**完全替代硬编码规则，实现真正的零硬编码架构。

## 🧠 微模型架构设计

### 分层模型体系
```
├── Tier 1: 专用微模型层 (12MB总计)
│   ├── 联系信息模型 (5MB) → 邮箱、电话、URL、社交账号
│   ├── 时间实体模型 (3MB) → 日期、时间、时间段
│   └── 数值实体模型 (4MB) → 数字、货币、百分比、单位
│
├── Tier 2: 通用语义模型 (150MB)
│   └── 多语言NER模型 → 人名、地名、机构、概念、技术
│
└── Tier 3: 智能调度层
    ├── 覆盖度评估器 → 判断是否需要启用大模型
    ├── 置信度融合器 → 贝叶斯方法合并结果
    └── 优雅降级机制 → 模型失败时的备选方案
```

## 📦 专用微模型详细设计

### 1. 联系信息微模型 (ContactEntitiesModel)

**模型规格**：
- 文件大小：5MB
- 推理延迟：< 20ms/1000字符
- 准确率目标：> 95%

**识别能力**：
```kotlin
enum class ContactEntityType {
    EMAIL,           // user@domain.com
    PHONE,           // +86-138-1234-5678, (010)12345678
    URL,             // https://example.com, www.site.org
    SOCIAL_HANDLE,   // @username, #hashtag
    IP_ADDRESS,      // 192.168.1.1, 2001:db8::1
    DOMAIN          // example.com (不含协议)
}
```

**训练数据特征**：
- 多语言混合文本中的联系信息
- 各种格式变体（带/不带协议、不同分隔符等）
- 上下文理解（区分URL和相似文本）

**实现接口**：
```kotlin
class ContactEntitiesModel : MicroModel {
    override suspend fun predict(text: String): List<EntityPrediction> {
        // ONNX模型推理
        return onnxSession.run(preprocessText(text))
            .map { rawPrediction ->
                EntityPrediction(
                    text = rawPrediction.text,
                    type = mapToContactType(rawPrediction.label),
                    confidence = rawPrediction.confidence,
                    startOffset = rawPrediction.start,
                    endOffset = rawPrediction.end
                )
            }
    }
}
```

### 2. 时间实体微模型 (TemporalEntitiesModel)

**模型规格**：
- 文件大小：3MB
- 推理延迟：< 15ms/1000字符
- 准确率目标：> 92%

**识别能力**：
```kotlin
enum class TemporalEntityType {
    ABSOLUTE_DATE,    // 2025年7月25日, July 25, 2025
    RELATIVE_DATE,    // 昨天, 下周, last month
    TIME,            // 14:30, 下午2点半
    DURATION,        // 3小时, 2 weeks
    TIME_RANGE,      // 9:00-17:00, 2024-2025年
    RECURRING        // 每周一, every Monday
}
```

**多语言支持**：
- 中文：2025年7月25日、明天下午、三个小时
- 英文：July 25, 2025、tomorrow afternoon、3 hours
- 混合：2025年July、下午3 PM

### 3. 数值实体微模型 (NumericEntitiesModel)

**模型规格**：
- 文件大小：4MB
- 推理延迟：< 18ms/1000字符
- 准确率目标：> 94%

**识别能力**：
```kotlin
enum class NumericEntityType {
    CURRENCY,        // ¥100, $50.99, 100美元
    PERCENTAGE,      // 80%, 百分之八十
    MEASUREMENT,     // 1.8米, 50kg, 100MB
    PLAIN_NUMBER,    // 123, 一千二百三十
    ORDINAL,         // 第一, 3rd, 第100名
    RANGE           // 50-100, 10~20万
}
```

## 🔄 智能调度策略

### 覆盖度驱动的模型选择
```kotlin
class IntelligentModelScheduler {
    suspend fun extractEntities(text: String): List<ExtractedEntity> {
        // 第一阶段：并行运行所有微模型
        val microResults = runMicroModels(text) // ~50ms
        
        // 评估微模型覆盖度
        val coverage = calculateCoverage(microResults, text)
        
        return when {
            coverage > 0.8 -> {
                // 微模型覆盖度足够，直接返回
                microResults
            }
            text.length > 5000 -> {
                // 长文本：采样 + 微模型结果
                val sampledText = intelligentSample(text, 1000)
                val semanticResults = semanticModel.predict(sampledText)
                merge(microResults, semanticResults)
            }
            else -> {
                // 短文本：完整语义分析
                val semanticResults = semanticModel.predict(text) // ~200ms
                merge(microResults, semanticResults)
            }
        }
    }
    
    private fun calculateCoverage(results: List<ExtractedEntity>, text: String): Float {
        val coveredChars = results.sumOf { it.endOffset - it.startOffset }
        return coveredChars.toFloat() / text.length
    }
}
```

## ⚡ 性能优化策略

### 1. 模型量化
```kotlin
// 模型量化配置
data class ModelQuantizationConfig(
    val precision: Precision = Precision.INT8,  // FP32 -> INT8 (75%体积减少)
    val enableGPUAcceleration: Boolean = false, // 移动端关闭GPU
    val batchSize: Int = 1                      // 单句处理
)

// 量化后的模型规格
val quantizedModelSizes = mapOf(
    "contact-entities" to 1.2, // 5MB -> 1.2MB
    "temporal-entities" to 0.8, // 3MB -> 0.8MB  
    "numeric-entities" to 1.0,  // 4MB -> 1.0MB
    "multilingual-ner" to 38    // 150MB -> 38MB
)
```

### 2. 渐进式加载
```kotlin
class ProgressiveModelLoader {
    // 启动时仅加载最小集合
    private val coreModels = setOf("contact-entities", "temporal-entities")
    
    // 后台异步加载完整集合
    private val fullModels = setOf("numeric-entities", "multilingual-ner")
    
    suspend fun initialize() {
        // 阶段1：快速启动 (< 1秒)
        loadModels(coreModels)
        
        // 阶段2：后台完整加载 (< 5秒)
        GlobalScope.launch {
            loadModels(fullModels)
        }
    }
}
```

### 3. 智能缓存
```kotlin
class ModelResultCache {
    private val cache = LRUCache<String, CachedResult>(maxSize = 1000)
    
    suspend fun getCachedOrCompute(
        text: String,
        computeFn: suspend (String) -> List<ExtractedEntity>
    ): List<ExtractedEntity> {
        val textHash = text.sha256()
        
        return cache.get(textHash)?.let { cached ->
            if (cached.isValid()) cached.entities else null
        } ?: run {
            val entities = computeFn(text)
            cache.put(textHash, CachedResult(entities, System.currentTimeMillis()))
            entities
        }
    }
}
```

## ⚠️ 现实挑战：模型获取策略

### 核心问题
我们设计的专用微模型（`contact-entities-5mb.onnx`、`temporal-entities-3mb.onnx`等）**当前不存在**，面临以下现实挑战：

1. **训练成本高**：需要大量GPU资源和标注数据
2. **开发周期长**：从零训练到生产可用需要数周时间
3. **技术风险**：模型性能可能不达预期

### 🎯 务实解决方案：渐进式模型策略

#### 方案1：开源模型起步（立即可用）
```kotlin
// 使用现有开源NER模型作为基础
val availableModels = mapOf(
    "multilingual_ner" to ModelInfo(
        path = "bert-base-multilingual-cased-ner.onnx", 
        size = 50.MB,
        languages = setOf("zh", "en"),
        accuracy = 0.87f
    ),
    "chinese_ner" to ModelInfo(
        path = "hanlp-zh-ner.onnx",
        size = 25.MB, 
        languages = setOf("zh"),
        accuracy = 0.89f
    ),
    "english_ner" to ModelInfo(
        path = "spacy-en-core-web-sm.onnx",
        size = 15.MB,
        languages = setOf("en"), 
        accuracy = 0.91f
    )
)
```

#### 方案2：智能后处理替代专用模型
```kotlin
// 用后处理分类器替代专用微模型（零硬编码）
class IntelligentEntityClassifier(
    private val contextAnalyzer: ContextAnalyzer
) {
    suspend fun refineEntityType(
        text: String, 
        rawLabel: String,
        context: String
    ): EntityType {
        // 使用轻量级AI分类器而非硬编码规则
        return when (rawLabel) {
            "MISC" -> contextAnalyzer.classifyMiscEntity(text, context)
            "ORG" -> contextAnalyzer.distinguishOrgType(text, context)  
            else -> EntityType.fromBIOLabel(rawLabel)
        }
    }
}

class ContextAnalyzer(private val miniClassifier: OnnxModel) {
    // 用5MB的小型分类模型替代硬编码规则
    suspend fun classifyMiscEntity(text: String, context: String): EntityType {
        val features = extractFeatures(text, context)
        val prediction = miniClassifier.classify(features)
        
        return when (prediction.label) {
            "CONTACT" -> inferContactType(text)
            "TEMPORAL" -> inferTemporalType(text)
            "NUMERIC" -> inferNumericType(text)
            else -> EntityType.CONCEPT
        }
    }
}
```

#### 方案3：渐进式专用模型训练
```python
# 并行进行的训练数据收集与模型开发
class ProgressiveModelTraining:
    def __init__(self):
        # 阶段1：基于开源数据集
        self.public_datasets = [
            "CoNLL-2003",      # 通用NER
            "OntoNotes 5.0",   # 多语言实体
            "MSRA NER",        # 中文NER
            "Weibo NER"        # 中文社交媒体
        ]
        
        # 阶段2：合成数据生成
        self.synthetic_generators = {
            "contact": ContactDataGenerator(),
            "temporal": TemporalDataGenerator(), 
            "numeric": NumericDataGenerator()
        }
        
        # 阶段3：用户数据增强学习
        self.user_feedback_loop = UserFeedbackCollector()
    
    def generate_contact_training_data(self):
        """生成联系信息训练数据"""
        return [
            # 真实场景的合成数据
            ("发邮件到 john@company.com 确认", [("john@company.com", "EMAIL", 4, 20)]),
            ("访问API: https://api.service.com/v1", [("https://api.service.com/v1", "URL", 7, 32)]),
            ("手机号码是+86-138-1234-5678", [("+86-138-1234-5678", "PHONE", 5, 21)])
        ]
    
    def train_micro_model(self, domain: str, data: List[TrainingExample]):
        """训练专用微模型"""
        model = BertForTokenClassification.from_pretrained("bert-base-multilingual-cased")
        trainer = NERTrainer(model, data)
        
        # 训练并转换为ONNX
        trained_model = trainer.train(epochs=50)
        onnx_model = convert_to_onnx(trained_model, f"{domain}-entities-micro.onnx")
        
        return onnx_model
```

### 📋 现实实施时间表

#### 阶段1：开源模型集成 (Week 1-2)
```bash
# 下载现有ONNX模型
wget https://huggingface.co/wietsedv/xlm-roberta-base-ft-udpos28-en/resolve/main/model.onnx
wget https://github.com/hankcs/HanLP/releases/download/v2.1.0-beta.4/zh_ner.onnx

# 集成到KMP项目
cp *.onnx src/commonMain/resources/models/
```

#### 阶段2：智能后处理开发 (Week 3-4)  
```kotlin
// 实现零硬编码的后处理分类系统
class PragmaticNERService(
    private val backboneModel: OnnxModel,
    private val entityClassifier: IntelligentEntityClassifier
) {
    suspend fun extractEntities(text: String): List<ExtractedEntity> {
        // 使用现有通用模型
        val rawEntities = backboneModel.predict(text)
        
        // 智能后处理（替代专用微模型）
        return rawEntities.map { raw ->
            ExtractedEntity(
                text = raw.text,
                type = entityClassifier.refineEntityType(raw.text, raw.label, raw.context),
                confidence = raw.confidence * entityClassifier.getConfidenceBoost(raw),
                startOffset = raw.start,
                endOffset = raw.end,
                source = "BackboneModel+Classifier"
            )
        }
    }
}
```

#### 阶段3：专用模型训练 (Month 2-3)
```python
# 并行进行的模型训练流水线
training_pipeline = {
    "contact_model": {
        "data_collection": "Week 5-6",
        "model_training": "Week 7-8", 
        "onnx_conversion": "Week 9",
        "integration_testing": "Week 10"
    },
    "temporal_model": {
        "data_collection": "Week 6-7",
        "model_training": "Week 8-9",
        "onnx_conversion": "Week 10", 
        "integration_testing": "Week 11"
    }
}
```

### 🎯 现实版本的性能目标

#### 修正后的性能指标
```kotlin
data class RealisticPerformanceTargets(
    // 阶段1：开源模型基线
    val backboneModelLatency: Duration = 200.milliseconds,    // 50MB通用模型
    val classifierLatency: Duration = 50.milliseconds,        // 5MB分类器
    val totalLatency: Duration = 250.milliseconds,            // 组合处理
    val memoryUsage: Long = 80 * 1024 * 1024,                // 80MB RAM
    val accuracyGeneral: Float = 0.85f,                       // 通用实体85%
    val accuracyRefined: Float = 0.88f,                       // 后处理提升3%
    
    // 阶段2：专用模型目标（未来）
    val microModelLatency: Duration = 50.milliseconds,        // 理想微模型
    val microModelAccuracy: Float = 0.92f                     // 专用模型精度
)
```

### 💡 风险缓解策略

#### 模型获取失败的备选方案
```kotlin
class FallbackModelStrategy {
    private val modelPriority = listOf(
        "specialized_micro_models",    // 最佳：专用微模型
        "open_source_general_models",  // 良好：开源通用模型  
        "rule_based_classifiers",      // 可接受：基于规则的分类器
        "basic_text_analysis"          // 最低：基础文本分析
    )
    
    suspend fun getAvailableModel(): NERProcessor {
        return modelPriority.firstNotNullOfOrNull { strategy ->
            tryLoadModel(strategy)
        } ?: BasicTextAnalyzer() // 最后的兜底方案
    }
}

## 🔧 开发集成指南

### KMP项目集成
```kotlin
// commonMain/kotlin/ner/MicroModelNER.kt
expect class OnnxRuntime {
    suspend fun loadModel(modelPath: String): OnnxSession
}

// desktopMain/kotlin/ner/DesktopOnnxRuntime.kt  
actual class OnnxRuntime {
    actual suspend fun loadModel(modelPath: String): OnnxSession {
        return OrtSession.create(modelPath, OrtEnvironment.getEnvironment())
    }
}

// 使用示例
class NERService(private val runtime: OnnxRuntime) {
    private val microModels = MicroModelCollection(runtime)
    
    suspend fun extractEntities(text: String): List<ExtractedEntity> {
        return microModels.processText(text)
    }
}
```

### 资源管理
```kotlin
// 模型文件组织结构
src/
├── commonMain/resources/models/
│   ├── contact-entities-quantized.onnx      (1.2MB)
│   ├── temporal-entities-quantized.onnx     (0.8MB)  
│   ├── numeric-entities-quantized.onnx      (1.0MB)
│   └── multilingual-ner-quantized.onnx      (38MB)
└── commonMain/kotlin/ner/
    ├── MicroModelExtractor.kt
    ├── ModelScheduler.kt
    └── EntityMerger.kt
```

## 📊 性能基准测试

### 目标性能指标
```kotlin
data class PerformanceTargets(
    val microModelLatency: Duration = 50.milliseconds,    // 所有微模型并行
    val semanticModelLatency: Duration = 200.milliseconds, // 大模型单独
    val totalMemory: Long = 50 * 1024 * 1024,            // 50MB RAM
    val accuracyContact: Float = 0.95f,                   // 联系信息95%
    val accuracyTemporal: Float = 0.92f,                  // 时间实体92%
    val accuracyNumeric: Float = 0.94f,                   // 数值实体94%
    val accuracySemantic: Float = 0.85f                   // 语义实体85%
)
```

### 测试用例
```kotlin
val testCases = listOf(
    TestCase(
        input = "联系john@company.com获取2025年Q1的销售数据，预计需要3个工作日处理完成",
        expected = listOf(
            Entity("john@company.com", EMAIL, 2, 18),
            Entity("2025年Q1", DATE_RANGE, 19, 26),
            Entity("3个工作日", DURATION, 34, 39)
        )
    )
)
```

## 🚀 未来扩展方向

### 1. 用户个性化微调
```kotlin
// 用户可以训练个人化的微模型
class PersonalizedMicroModel {
    suspend fun learnFromUserCorrections(
        corrections: List<UserCorrection>
    ) {
        // 使用少样本学习微调模型
        fewShotLearner.finetune(corrections)
    }
}
```

### 2. 动态模型更新
```kotlin
// 支持在线模型更新，不影响运行
class ModelUpdateService {
    suspend fun updateModel(
        modelName: String,
        newModelUrl: String
    ) {
        // 热更新机制
        val newModel = downloadAndValidate(newModelUrl)
        atomicSwapModel(modelName, newModel)
    }
}
```

---

*微模型分层策略实现了真正的零硬编码架构，在保持高性能的同时提供了卓越的智能化实体识别能力。*