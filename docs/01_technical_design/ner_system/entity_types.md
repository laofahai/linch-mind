# 实体分类体系设计

## 🎯 设计原则

1. **层次化** - 支持父子类型关系
2. **可扩展** - 易于添加新的实体类型
3. **语义化** - 类型名称直观易懂
4. **国际化** - 支持中英文混合识别

## 📊 实体类型枚举

```kotlin
enum class EntityType(
    val parent: EntityType? = null,
    val displayName: String,
    val description: String
) {
    // 根类型
    ROOT(null, "根", "所有实体的根类型"),

    // === 主要分类 ===
    PERSON(ROOT, "人物", "人物相关实体"),
    ORGANIZATION(ROOT, "组织机构", "各类组织机构"),
    LOCATION(ROOT, "地理位置", "地理位置相关"),
    CONCEPT(ROOT, "概念", "抽象概念和思想"),
    TECHNOLOGY(ROOT, "技术", "技术和工具相关"),
    ACADEMIC(ROOT, "学术", "学术和研究相关"),
    TEMPORAL(ROOT, "时间", "时间和日期相关"),
    QUANTITY(ROOT, "数量", "数量和单位"),
    WORK(ROOT, "作品", "创作作品"),
    EVENT(ROOT, "事件", "事件和活动"),

    // === 人物子类型 ===
    PERSON_NAME(PERSON, "人名", "具体的人物姓名"),
    PERSON_TITLE(PERSON, "职称", "职业称谓和头衔"),
    PERSON_ROLE(PERSON, "角色", "社会角色和身份"),

    // === 组织机构子类型 ===
    COMPANY(ORGANIZATION, "公司", "商业公司和企业"),
    INSTITUTION(ORGANIZATION, "机构", "政府和公共机构"),
    UNIVERSITY(ORGANIZATION, "大学", "高等教育机构"),
    SCHOOL(ORGANIZATION, "学校", "教育机构"),
    TEAM(ORGANIZATION, "团队", "工作团队和小组"),

    // === 地理位置子类型 ===
    COUNTRY(LOCATION, "国家", "国家和地区"),
    CITY(LOCATION, "城市", "城市和城镇"),
    BUILDING(LOCATION, "建筑", "建筑物和场所"),
    GEOGRAPHIC_FEATURE(LOCATION, "地理特征", "山川河流等自然地理"),

    // === 概念子类型 ===
    ABSTRACT_CONCEPT(CONCEPT, "抽象概念", "抽象的思想和理念"),
    DOMAIN_CONCEPT(CONCEPT, "领域概念", "特定领域的专业概念"),
    METHODOLOGY(CONCEPT, "方法论", "方法和流程"),

    // === 技术子类型 ===
    PROGRAMMING_LANGUAGE(TECHNOLOGY, "编程语言", "编程语言"),
    FRAMEWORK(TECHNOLOGY, "框架", "软件框架和库"),
    TOOL(TECHNOLOGY, "工具", "开发工具和软件"),
    ALGORITHM(TECHNOLOGY, "算法", "算法和数学模型"),
    PROTOCOL(TECHNOLOGY, "协议", "通信协议和标准"),

    // === 学术子类型 ===
    FIELD_OF_STUDY(ACADEMIC, "研究领域", "学科和研究方向"),
    JOURNAL(ACADEMIC, "期刊", "学术期刊和出版物"),
    CONFERENCE(ACADEMIC, "会议", "学术会议和活动"),
    THEORY(ACADEMIC, "理论", "学术理论和假说"),
    RESEARCH_METHOD(ACADEMIC, "研究方法", "研究方法和技术"),

    // === 时间子类型 ===
    DATE(TEMPORAL, "日期", "具体日期"),
    TIME_PERIOD(TEMPORAL, "时间段", "时间范围和周期"),
    HISTORICAL_PERIOD(TEMPORAL, "历史时期", "历史时代和阶段"),

    // === 数量子类型 ===
    NUMBER(QUANTITY, "数字", "具体数值"),
    UNIT(QUANTITY, "单位", "度量单位"),
    PERCENTAGE(QUANTITY, "百分比", "百分比数值"),
    CURRENCY(QUANTITY, "货币", "货币金额"),

    // === 作品子类型 ===
    BOOK(WORK, "书籍", "图书和出版物"),
    ARTICLE(WORK, "文章", "文章和论文"),
    SOFTWARE(WORK, "软件", "软件产品"),
    DOCUMENT(WORK, "文档", "文档和资料"),

    // === 事件子类型 ===
    MEETING(EVENT, "会议", "会议和讨论"),
    PROJECT(EVENT, "项目", "项目和任务"),
    MILESTONE(EVENT, "里程碑", "重要节点和成就");

    // 获取所有子类型
    fun getChildren(): List<EntityType> {
        return values().filter { it.parent == this }
    }

    // 获取完整路径
    fun getPath(): List<EntityType> {
        val path = mutableListOf<EntityType>()
        var current: EntityType? = this
        while (current != null) {
            path.add(0, current)
            current = current.parent
        }
        return path
    }

    // 判断是否为某类型的子类型
    fun isChildOf(ancestor: EntityType): Boolean {
        var current = this.parent
        while (current != null) {
            if (current == ancestor) return true
            current = current.parent
        }
        return false
    }
}
```

## 🔍 微模型映射策略

### 专用微模型输出映射
```kotlin
// 联系信息微模型映射
class ContactModelMapper {
    fun mapContactType(modelOutput: String): EntityType {
        return when (modelOutput) {
            "EMAIL" -> EntityType.EMAIL
            "PHONE" -> EntityType.PHONE  
            "URL" -> EntityType.URL
            "SOCIAL_HANDLE" -> EntityType.SOCIAL_HANDLE
            "IP_ADDRESS" -> EntityType.NETWORK_ADDRESS
            else -> EntityType.CONTACT_INFO
        }
    }
}

// 时间实体微模型映射
class TemporalModelMapper {
    fun mapTemporalType(modelOutput: String): EntityType {
        return when (modelOutput) {
            "DATE" -> EntityType.DATE
            "TIME" -> EntityType.TIME
            "DURATION" -> EntityType.TIME_PERIOD
            "RELATIVE_TIME" -> EntityType.TEMPORAL
            "RECURRING" -> EntityType.RECURRING_EVENT
            else -> EntityType.TEMPORAL
        }
    }
}

// 数值实体微模型映射
class NumericModelMapper {
    fun mapNumericType(modelOutput: String): EntityType {
        return when (modelOutput) {
            "MONEY" -> EntityType.CURRENCY
            "PERCENT" -> EntityType.PERCENTAGE
            "NUMBER" -> EntityType.NUMBER
            "MEASUREMENT" -> EntityType.UNIT
            "ORDER" -> EntityType.ORDINAL
            else -> EntityType.QUANTITY
        }
    }
}
```

### 模型训练数据结构
```kotlin
data class TrainingExample(
    val text: String,
    val entities: List<AnnotatedEntity>
)

data class AnnotatedEntity(
    val text: String,
    val type: EntityType,
    val startOffset: Int,
    val endOffset: Int,
    val context: String? = null
)

// 训练数据来源 - 无硬编码词典
class TrainingDataGenerator {
    // 从真实用户数据中学习，而非预定义词典
    suspend fun generateFromUserData(userTexts: List<String>): List<TrainingExample> {
        // 使用弱监督学习生成训练数据
        return weakSupervisionPipeline.process(userTexts)
    }
    
    // 增量学习新实体类型
    suspend fun learnNewEntityType(
        examples: List<String>,
        entityType: EntityType
    ): ModelUpdate {
        return incrementalLearner.learn(examples, entityType)
    }
}
```

### 动态类型发现（自学习）
```kotlin
class DynamicEntityTypeDiscovery {
    // 从用户使用模式中发现新的实体类型
    suspend fun discoverNewTypes(userInteractions: List<UserInteraction>): List<EntityTypeCandidate> {
        return patternMiner.findFrequentPatterns(userInteractions)
            .filter { it.confidence > MIN_CONFIDENCE_THRESHOLD }
            .map { pattern ->
                EntityTypeCandidate(
                    suggestedType = generateEntityType(pattern),
                    examples = pattern.examples,
                    confidence = pattern.confidence
                )
            }
    }
    
    // 用户确认后自动扩展类型系统
    fun confirmNewEntityType(candidate: EntityTypeCandidate): EntityType {
        val newType = EntityType.createDynamic(candidate.suggestedType)
        trainingPipeline.retrain(candidate.examples, newType)
        return newType
    }
}

## 🎯 动态扩展机制

### 类型扩展接口
```kotlin
interface EntityTypeExtension {
    val customTypes: List<CustomEntityType>
    fun getTypeFor(text: String, context: String): EntityType?
}

data class CustomEntityType(
    val name: String,
    val parent: EntityType,
    val displayName: String,
    val description: String,
    val patterns: List<Regex> = emptyList(),
    val keywords: List<String> = emptyList()
)
```

### 配置化类型定义
```kotlin
// 支持从配置文件加载自定义类型
class ConfigurableEntityTypes {
    fun loadFromConfig(configPath: String): List<CustomEntityType> {
        // 从JSON/YAML配置加载自定义实体类型
    }
    
    fun mergeWithBuiltinTypes(
        customTypes: List<CustomEntityType>
    ): EntityTypeRegistry {
        // 合并内置类型和自定义类型
    }
}
```

## 📊 使用示例

### 测试用例分析
**输入文本**: "北京大学的张教授在研究人工智能深度学习算法，发表在Nature期刊上"

**预期识别结果**:
```kotlin
listOf(
    ExtractedEntity("北京大学", EntityType.UNIVERSITY, 0.95f, 0, 3),
    ExtractedEntity("张教授", EntityType.PERSON_NAME, 0.90f, 5, 7),
    ExtractedEntity("人工智能", EntityType.FIELD_OF_STUDY, 0.85f, 10, 13),
    ExtractedEntity("深度学习", EntityType.ALGORITHM, 0.88f, 13, 17),
    ExtractedEntity("算法", EntityType.ALGORITHM, 0.80f, 17, 19),
    ExtractedEntity("Nature", EntityType.JOURNAL, 0.92f, 23, 29)
)
```

## 🔄 版本演进策略

### 向后兼容
```kotlin
// 保持与现有EntityType枚举的兼容性
enum class LegacyEntityType {
    DOCUMENT, CONCEPT, KEYWORD;
    
    fun toNewEntityType(): EntityType = when(this) {
        DOCUMENT -> EntityType.DOCUMENT
        CONCEPT -> EntityType.CONCEPT
        KEYWORD -> EntityType.DOMAIN_CONCEPT
    }
}
```

### 渐进式迁移
1. **阶段1**: 新旧类型并存，优先使用新类型
2. **阶段2**: 提供迁移工具，批量转换历史数据
3. **阶段3**: 完全切换到新类型系统

---

*该实体分类体系设计为Linch Mind的智能理解能力提供了坚实的语义基础。*