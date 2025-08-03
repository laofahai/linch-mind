# 智能推荐触发系统设计

**状态**: ✅ 核心功能已实现  
**最后更新**: 2025-07-28

## 实现状态

### ✅ 已实现组件
- **RecommendationTriggerManager**: 核心触发管理器，实现了：
  - 实时触发机制
  - 定时触发机制
  - 自适应触发机制
  - 触发统计和监控

### ⚡ 部分实现
- 文档中提及的完整触发系统架构（TriggerEngine, TriggerCondition等）在当前实现中被简化为RecommendationTriggerManager的内部功能

### ❌ 待实现组件
- **AppStateMonitor** - 应用状态监控
- **UserActivityDetector** - 用户活动检测器
- **独立的TriggerEngine** - 触发引擎
- **可扩展的TriggerCondition** - 触发条件接口

## 🎯 核心设计理念

智能推荐的核心价值在于**在用户需要的时候主动提供有价值的信息**。触发系统需要平衡主动性和非打扰性，确保推荐既及时又相关。

### 设计原则
1. **用户意图感知** - 基于用户行为推断当前需求
2. **上下文敏感** - 考虑当前工作环境和任务状态
3. **非打扰性** - 避免无关或频繁的推荐打断
4. **学习适应** - 基于用户反馈调整触发策略
5. **隐私保护** - 最小化数据收集，本地处理

## 🧠 触发场景分析

### 高价值触发场景

#### 1. 应用状态变化触发 🔄
**场景**: 用户切换应用、窗口焦点变化
**价值**: 推荐与新任务相关的知识和资源

```kotlin
// 应用状态变化触发器
class AppStateChangeTrigger : TriggerCondition {
    data class StateChangeEvent(
        val fromApp: String?,
        val toApp: String,
        val timestamp: Long,
        val duration: Long // 在前一个应用的停留时间
    )
    
    override suspend fun shouldTrigger(event: TriggerEvent): Boolean {
        return when (event) {
            is AppStateChangeEvent -> {
                // 切换到Linch Mind或相关应用时触发
                event.toApp == "Linch Mind" || 
                event.duration > 30_000L // 在其他应用停留超过30秒
            }
            else -> false
        }
    }
}
```

**触发时机**:
- 用户切换回Linch Mind应用
- 从长时间使用的应用切换出来 (工作模式转换)
- 打开新的工作应用 (IDE、文档编辑器、浏览器)

#### 2. 用户活动模式触发 📊
**场景**: 检测到用户进入特定的工作模式
**价值**: 基于工作模式推荐相关资源

```kotlin
// 工作模式检测触发器
class WorkModeDetectionTrigger : TriggerCondition {
    enum class WorkMode {
        DEEP_FOCUS,     // 深度专注 (长时间单应用使用)
        RESEARCH,       // 研究模式 (频繁搜索、打开多个文档)
        CODING,         // 编程模式 (IDE + 文档 + 搜索)
        MEETING,        // 会议模式 (日历事件 + 通讯应用)
        WRITING,        // 写作模式 (文档编辑器 + 参考资料)
        BREAK           // 休息模式 (无活动或娱乐应用)
    }
    
    override suspend fun shouldTrigger(event: TriggerEvent): Boolean {
        return when (val mode = detectCurrentWorkMode(event)) {
            WorkMode.DEEP_FOCUS -> {
                // 专注模式下，适时推荐相关深度资料
                getCurrentFocusSession().duration > 25 * 60 * 1000L // 25分钟番茄钟
            }
            WorkMode.RESEARCH -> {
                // 研究模式下，推荐相关知识和连接
                getRecentSearchCount() >= 3
            }
            else -> false
        }
    }
}
```

#### 3. 时间和习惯触发 ⏰
**场景**: 基于用户的时间习惯和工作节奏
**价值**: 在用户习惯的时间点推荐相关内容

```kotlin
// 时间习惯触发器
class TimeBasedHabitTrigger : TriggerCondition {
    data class UserTimePattern(
        val activeHours: List<IntRange>,        // 活跃时间段
        val workStartTime: Int,                 // 工作开始时间
        val focusIntervals: List<IntRange>,     // 专注时间段
        val breakTimes: List<Int>               // 休息时间点
    )
    
    override suspend fun shouldTrigger(event: TriggerEvent): Boolean {
        val now = getCurrentHour()
        val pattern = getUserTimePattern()
        
        return when {
            // 工作开始时推荐今日计划
            now == pattern.workStartTime -> true
            
            // 专注时段开始时推荐相关资源
            pattern.focusIntervals.any { now in it } -> true
            
            // 休息时间推荐轻松内容或总结
            now in pattern.breakTimes -> true
            
            else -> false
        }
    }
}
```

#### 4. 内容相关性触发 🔗
**场景**: 检测到用户正在处理的内容与知识库中内容高度相关
**价值**: 推荐相关联的知识和洞察

```kotlin
// 内容相关性触发器
class ContentRelevanceTrigger : TriggerCondition {
    override suspend fun shouldTrigger(event: TriggerEvent): Boolean {
        return when (event) {
            is ContentAccessEvent -> {
                val relevantItems = findRelevantKnowledge(event.content)
                relevantItems.isNotEmpty() && 
                relevantItems.maxOf { it.similarity } > 0.8f
            }
            is SearchQueryEvent -> {
                val relatedConcepts = extractConcepts(event.query)
                hasStrongConceptualConnections(relatedConcepts)
            }
            else -> false
        }
    }
}
```

#### 5. 学习和发现触发 🎓
**场景**: 检测到用户在学习新概念或探索新领域
**价值**: 推荐相关学习路径和深度资源

```kotlin
// 学习发现触发器
class LearningDiscoveryTrigger : TriggerCondition {
    override suspend fun shouldTrigger(event: TriggerEvent): Boolean {
        return when (event) {
            is NewConceptEncounterEvent -> {
                // 用户遇到新概念时
                !isKnownConcept(event.concept) && 
                hasRelatedKnowledge(event.concept)
            }
            is KnowledgeGapEvent -> {
                // 检测到知识空白时
                event.confidence < 0.3f && 
                hasFillingResources(event.topic)
            }
            else -> false
        }
    }
}
```

### 低干扰触发场景

#### 6. 空闲时间触发 😌
**场景**: 用户无活动或低活动期间
**价值**: 推荐知识回顾、总结或轻松内容

```kotlin
// 空闲时间触发器
class IdleTimeTrigger : TriggerCondition {
    override suspend fun shouldTrigger(event: TriggerEvent): Boolean {
        return when (event) {
            is UserIdleEvent -> {
                event.idleDuration > 10 * 60 * 1000L && // 空闲超过10分钟
                !isInMeetingOrCall() &&                  // 不在会议中
                isWorkingHours()                         // 工作时间内
            }
            else -> false
        }
    }
}
```

#### 7. 后台分析完成触发 🔍
**场景**: 系统完成新的分析或发现新的知识连接
**价值**: 分享新发现的洞察和连接

```kotlin
// 后台分析触发器
class BackgroundAnalysisTrigger : TriggerCondition {
    override suspend fun shouldTrigger(event: TriggerEvent): Boolean {
        return when (event) {
            is AnalysisCompleteEvent -> {
                event.newInsights.isNotEmpty() &&
                event.significance > 0.7f &&
                !isUserBusy()
            }
            is NewConnectionDiscoveredEvent -> {
                event.connectionStrength > 0.8f &&
                !hasRecentlyNotifiedSimilar(event.connection)
            }
            else -> false
        }
    }
}
```

## 🏗️ 技术架构设计

### 触发引擎核心架构

```kotlin
// 智能触发引擎
class IntelligentTriggerEngine(
    private val personalAssistant: PersonalAssistant,
    private val recommendationEngine: IntelligentRecommendationEngine,
    private val behaviorAnalyzer: BehaviorAnalyzer,
    private val activityDetector: UserActivityDetector
) {
    private val triggers = listOf(
        AppStateChangeTrigger(),
        WorkModeDetectionTrigger(),
        TimeBasedHabitTrigger(),
        ContentRelevanceTrigger(),
        LearningDiscoveryTrigger(),
        IdleTimeTrigger(),
        BackgroundAnalysisTrigger()
    )
    
    private val triggerHistory = mutableListOf<TriggerEvent>()
    private val cooldownManager = TriggerCooldownManager()
    
    suspend fun processEvent(event: TriggerEvent) {
        // 1. 检查冷却期
        if (cooldownManager.isInCooldown(event.type)) {
            return
        }
        
        // 2. 评估触发条件
        val activeTriggers = triggers.filter { it.shouldTrigger(event) }
        
        if (activeTriggers.isEmpty()) {
            return
        }
        
        // 3. 生成推荐
        val recommendations = generateContextualRecommendations(event, activeTriggers)
        
        // 4. 应用推荐策略
        val filteredRecommendations = applyRecommendationStrategy(recommendations, event)
        
        // 5. 触发推荐
        if (filteredRecommendations.isNotEmpty()) {
            triggerRecommendations(filteredRecommendations, event)
            cooldownManager.startCooldown(event.type)
            recordTriggerEvent(event, filteredRecommendations)
        }
    }
}
```

### 用户活动检测器

```kotlin
// 用户活动检测器
class UserActivityDetector(private val scope: CoroutineScope) {
    private val _activityEvents = MutableSharedFlow<ActivityEvent>()
    val activityEvents: SharedFlow<ActivityEvent> = _activityEvents.asSharedFlow()
    
    private var lastActiveApp: String? = null
    private var lastActivityTime: Long = 0L
    
    fun startMonitoring() {
        scope.launch {
            while (true) {
                try {
                    // 检测应用状态变化
                    val currentApp = getCurrentActiveApplication()
                    if (currentApp != lastActiveApp) {
                        _activityEvents.emit(
                            AppStateChangeEvent(
                                fromApp = lastActiveApp,
                                toApp = currentApp,
                                timestamp = System.currentTimeMillis()
                            )
                        )
                        lastActiveApp = currentApp
                    }
                    
                    // 检测用户空闲
                    val lastInput = getLastUserInputTime()
                    if (System.currentTimeMillis() - lastInput > 60_000L) {
                        _activityEvents.emit(
                            UserIdleEvent(
                                idleDuration = System.currentTimeMillis() - lastInput
                            )
                        )
                    }
                    
                    delay(1000L) // 每秒检测一次
                } catch (e: Exception) {
                    // 记录错误但继续监控
                    println("活动检测异常: ${e.message}")
                }
            }
        }
    }
}
```

### 应用状态监控器

```kotlin
// 应用状态监控器 (平台特定实现)
expect class AppStateMonitor {
    fun getCurrentActiveApplication(): String
    fun getApplicationUsageStats(): Map<String, Long>
    fun isApplicationInForeground(appName: String): Boolean
    fun getLastUserInputTime(): Long
}

// 桌面端实现示例
actual class AppStateMonitor {
    actual fun getCurrentActiveApplication(): String {
        // 使用JNA获取活跃窗口信息
        return getCurrentActiveWindow()?.processName ?: "Unknown"
    }
    
    actual fun getLastUserInputTime(): Long {
        // 获取系统最后输入时间
        return getSystemIdleTime()
    }
}
```

### 触发冷却管理器

```kotlin
// 触发冷却管理器 - 防止过于频繁的推荐
class TriggerCooldownManager {
    private val cooldowns = mutableMapOf<String, Long>()
    
    // 不同触发类型的冷却时间
    private val cooldownDurations = mapOf(
        "app_state_change" to 2 * 60 * 1000L,      // 2分钟
        "work_mode_detection" to 10 * 60 * 1000L,   // 10分钟
        "content_relevance" to 5 * 60 * 1000L,      // 5分钟
        "learning_discovery" to 15 * 60 * 1000L,    // 15分钟
        "idle_time" to 30 * 60 * 1000L,             // 30分钟
        "background_analysis" to 20 * 60 * 1000L    // 20分钟
    )
    
    fun isInCooldown(triggerType: String): Boolean {
        val lastTrigger = cooldowns[triggerType] ?: 0L
        val cooldownDuration = cooldownDurations[triggerType] ?: 5 * 60 * 1000L
        return System.currentTimeMillis() - lastTrigger < cooldownDuration
    }
    
    fun startCooldown(triggerType: String) {
        cooldowns[triggerType] = System.currentTimeMillis()
    }
    
    // 基于用户反馈动态调整冷却时间
    fun adjustCooldown(triggerType: String, userFeedback: TriggerFeedback) {
        val currentDuration = cooldownDurations[triggerType] ?: return
        val adjustment = when (userFeedback) {
            TriggerFeedback.TOO_FREQUENT -> 1.5f
            TriggerFeedback.TOO_RARE -> 0.7f
            TriggerFeedback.JUST_RIGHT -> 1.0f
        }
        
        cooldownDurations[triggerType] = (currentDuration * adjustment).toLong()
    }
}
```

## 🎛️ 推荐策略和过滤

### 上下文感知推荐策略

```kotlin
// 上下文感知推荐策略
class ContextAwareRecommendationStrategy {
    
    suspend fun generateContextualRecommendations(
        event: TriggerEvent,
        activeTriggers: List<TriggerCondition>
    ): List<SmartRecommendation> {
        val context = buildRecommendationContext(event)
        val baseRecommendations = mutableListOf<SmartRecommendation>()
        
        activeTriggers.forEach { trigger ->
            when (trigger) {
                is AppStateChangeTrigger -> {
                    baseRecommendations.addAll(
                        generateAppTransitionRecommendations(context)
                    )
                }
                is WorkModeDetectionTrigger -> {
                    baseRecommendations.addAll(
                        generateWorkModeRecommendations(context)
                    )
                }
                is ContentRelevanceTrigger -> {
                    baseRecommendations.addAll(
                        generateContentRelevanceRecommendations(context)
                    )
                }
                // ... 其他触发器
            }
        }
        
        return baseRecommendations
            .distinctBy { it.contentHash }
            .sortedByDescending { it.relevanceScore }
            .take(5) // 限制推荐数量
    }
    
    private suspend fun buildRecommendationContext(event: TriggerEvent): RecommendationContext {
        return RecommendationContext(
            currentApp = getCurrentActiveApplication(),
            workMode = detectCurrentWorkMode(),
            timeOfDay = getCurrentHour(),
            recentActivities = getRecentUserActivities(60), // 最近60分钟
            currentFocus = getCurrentFocusArea(),
            userPreferences = getUserPreferences()
        )
    }
}
```

### 推荐质量过滤

```kotlin
// 推荐质量过滤器
class RecommendationQualityFilter {
    
    fun applyRecommendationStrategy(
        recommendations: List<SmartRecommendation>,
        event: TriggerEvent
    ): List<SmartRecommendation> {
        return recommendations
            .filter { isHighQuality(it) }
            .filter { isRelevantToContext(it, event) }
            .filter { !isRecentlyShown(it) }
            .filter { matchesUserPreferences(it) }
            .take(3) // 最多3个推荐
    }
    
    private fun isHighQuality(recommendation: SmartRecommendation): Boolean {
        return recommendation.confidence > 0.6f &&
               recommendation.relevanceScore > 0.7f &&
               recommendation.content.isNotBlank()
    }
    
    private fun isRelevantToContext(
        recommendation: SmartRecommendation,
        event: TriggerEvent
    ): Boolean {
        // 基于当前上下文评估推荐相关性
        val contextScore = calculateContextRelevance(recommendation, event)
        return contextScore > 0.5f
    }
}
```

## 📊 用户反馈和学习机制

### 触发效果评估

```kotlin
// 触发效果评估器
class TriggerEffectivenessEvaluator {
    
    data class TriggerMetrics(
        val triggerType: String,
        val triggerCount: Int,
        val clickRate: Float,
        val dismissRate: Float,
        val userSatisfaction: Float,
        val averageRelevance: Float
    )
    
    suspend fun evaluateTriggerEffectiveness(): Map<String, TriggerMetrics> {
        return getTriggerHistory()
            .groupBy { it.triggerType }
            .mapValues { (type, events) ->
                TriggerMetrics(
                    triggerType = type,
                    triggerCount = events.size,
                    clickRate = events.count { it.userClicked } / events.size.toFloat(),
                    dismissRate = events.count { it.userDismissed } / events.size.toFloat(),
                    userSatisfaction = events.map { it.userRating }.average().toFloat(),
                    averageRelevance = events.map { it.relevanceScore }.average().toFloat()
                )
            }
    }
    
    suspend fun optimizeTriggerStrategies() {
        val metrics = evaluateTriggerEffectiveness()
        
        metrics.forEach { (triggerType, metric) ->
            when {
                metric.dismissRate > 0.7f -> {
                    // 过多被忽略，降低触发频率
                    adjustTriggerSensitivity(triggerType, -0.2f)
                }
                metric.clickRate > 0.8f && metric.userSatisfaction > 0.8f -> {
                    // 效果很好，可以适当增加频率
                    adjustTriggerSensitivity(triggerType, 0.1f)
                }
                metric.averageRelevance < 0.5f -> {
                    // 相关性不够，优化推荐算法
                    optimizeRecommendationAlgorithm(triggerType)
                }
            }
        }
    }
}
```

## 🔧 配置和个性化

### 用户触发偏好配置

```kotlin
// 用户触发偏好配置
data class UserTriggerPreferences(
    val enabledTriggers: Set<String> = setOf(
        "app_state_change",
        "content_relevance",
        "learning_discovery"
    ),
    val triggerSensitivity: Map<String, Float> = mapOf(
        "app_state_change" to 0.7f,
        "work_mode_detection" to 0.5f,
        "content_relevance" to 0.8f,
        "learning_discovery" to 0.6f,
        "idle_time" to 0.3f,
        "background_analysis" to 0.4f
    ),
    val quietHours: List<IntRange> = listOf(
        12..13, // 午休时间
        18..19  // 下班时间
    ),
    val maxRecommendationsPerHour: Int = 3,
    val preferredRecommendationTypes: Set<RecommendationType> = setOf(
        RecommendationType.LEARN,
        RecommendationType.CONNECT,
        RecommendationType.REVIEW
    )
)

// 个性化触发管理器
class PersonalizedTriggerManager(
    private val userPreferences: UserTriggerPreferences,
    private val triggerEngine: IntelligentTriggerEngine
) {
    
    fun shouldAllowTrigger(triggerType: String, currentHour: Int): Boolean {
        return triggerType in userPreferences.enabledTriggers &&
               currentHour !in userPreferences.quietHours.flatten() &&
               !exceedsHourlyLimit()
    }
    
    private fun exceedsHourlyLimit(): Boolean {
        val currentHour = getCurrentHour()
        val triggersThisHour = getTriggerCountForHour(currentHour)
        return triggersThisHour >= userPreferences.maxRecommendationsPerHour
    }
}
```

## 📋 实现路线图

### Phase 1: 基础触发系统 (Week 1-2)
- [x] 实现TriggerEngine核心架构 (已通过RecommendationTriggerManager实现)
- [ ] 实现UserActivityDetector和AppStateMonitor
- [x] 实现基础的AppStateChangeTrigger (已集成在RecommendationTriggerManager中)
- [x] 集成到现有的RecommendationTriggerManager

### Phase 2: 智能触发条件 (Week 3-4)
- [ ] 实现WorkModeDetectionTrigger
- [ ] 实现ContentRelevanceTrigger
- [x] 实现TimeBasedHabitTrigger (已通过定时触发机制实现)
- [x] 添加触发冷却管理机制 (已在RecommendationTriggerManager中实现)

### Phase 3: 高级触发和优化 (Week 5-6)
- [ ] 实现LearningDiscoveryTrigger
- [ ] 实现BackgroundAnalysisTrigger
- [ ] 添加用户反馈学习机制
- [ ] 实现个性化触发偏好

### Phase 4: 效果评估和优化 (Week 7-8)
- [ ] 实现触发效果评估系统
- [ ] 添加A/B测试框架
- [ ] 优化触发算法
- [ ] 完善用户配置界面

## 🎯 成功指标

### 触发系统效果指标
- **触发准确率**: 用户点击推荐的比例 > 60%
- **用户满意度**: 推荐有用性评分 > 4.0/5.0
- **非打扰性**: 用户主动关闭推荐的比例 < 20%
- **个性化程度**: 基于用户行为的推荐精度 > 75%
- **响应及时性**: 从触发到推荐显示 < 2秒

### 用户体验指标
- **推荐相关性**: 推荐内容与当前任务相关度 > 80%
- **发现价值**: 用户通过推荐发现新知识的频率 > 5次/周
- **工作流整合**: 推荐融入用户工作流的自然度 > 4.0/5.0
- **学习效果**: 基于推荐的学习和知识连接增长 > 20%

---
*文档版本: v1.0 | 创建时间: 2025-07-25 | 核心设计: 智能触发系统*