# 智能数据处理策略

## 🎯 核心问题

不同类型的数据有不同的特点和处理需求，需要智能化的差异化处理策略，避免资源浪费，确保高效运行。

## 📊 数据类型特征分析

### 静态大容量数据
- **代码库**: 几GB大小，很少删除，但不同文件价值差异巨大
- **依赖目录**: node_modules、vendor等，巨大但低价值
- **历史归档**: 旧文档、备份文件，很少查询

### 动态高价值数据  
- **用户文档**: 笔记、工作日志，经常查询和修改
- **通信记录**: 邮件、消息，高价值且需要实时处理
- **浏览历史**: 动态更新，中等价值

## 🏗️ 智能处理架构

### 1. 数据分类与优先级

```kotlin
enum class ProcessingPriority {
    REALTIME,    // P0: 用户正在交互的内容
    HIGH,        // P1: 源码、文档等高价值内容  
    MEDIUM,      // P2: 配置、测试等中等价值
    LOW,         // P3: 大型库文件等低价值
    IGNORE       // P4: 依赖目录、编译产物等
}

class PriorityAssignmentService {
    fun assignPriority(filePath: String, fileType: String): ProcessingPriority {
        return when {
            // 路径规则
            filePath.contains("node_modules") -> ProcessingPriority.IGNORE
            filePath.contains("/src/") -> ProcessingPriority.HIGH
            filePath.contains("/docs/") -> ProcessingPriority.HIGH
            filePath.contains("/test/") -> ProcessingPriority.MEDIUM
            
            // 文件类型规则
            fileType in setOf("md", "txt", "kt", "java", "py") -> ProcessingPriority.HIGH
            fileType in setOf("json", "yml", "xml") -> ProcessingPriority.MEDIUM
            fileType in setOf("png", "jpg", "mp4") -> ProcessingPriority.IGNORE
            
            else -> ProcessingPriority.LOW
        }
    }
}
```

### 2. 容量控制策略

```kotlin
class CapacityControlledProcessor {
    companion object {
        const val MAX_FILE_SIZE_MB = 5
        const val MAX_CHUNK_SIZE_KB = 256
        const val MAX_LINES_PER_CHUNK = 500
    }
    
    suspend fun processLargeFile(filePath: String): List<ExtractedEntity> {
        val fileSize = File(filePath).length()
        
        return if (fileSize > MAX_FILE_SIZE_MB * 1024 * 1024) {
            // 大文件分块处理
            processInChunks(filePath)
        } else {
            // 小文件直接处理
            processFully(filePath)
        }
    }
    
    private suspend fun processInChunks(filePath: String): List<ExtractedEntity> {
        val entities = mutableListOf<ExtractedEntity>()
        
        File(filePath).useLines { lines ->
            lines.chunked(MAX_LINES_PER_CHUNK).forEach { chunk ->
                val chunkText = chunk.joinToString("\n")
                entities.addAll(nerService.extractEntities(chunkText))
            }
        }
        
        return entities
    }
}
```

### 3. 增量处理策略

```kotlin
data class FileMetadata(
    val filePath: String,
    val lastModified: Long,
    val contentHash: String,
    val processingStatus: ProcessingStatus,
    val lastProcessedTime: Long
)

enum class ProcessingStatus {
    SUCCEEDED, FAILED, PENDING, SKIPPED
}

class IncrementalProcessor {
    private val metadataStore = FileMetadataStore()
    
    suspend fun processIfChanged(filePath: String): ProcessResult {
        val currentFile = File(filePath)
        val storedMetadata = metadataStore.get(filePath)
        
        // 检查是否需要处理
        val needsProcessing = when {
            storedMetadata == null -> true // 新文件
            storedMetadata.lastModified != currentFile.lastModified() -> {
                // 文件修改时间变化，检查内容hash
                val currentHash = calculateFileHash(currentFile)
                currentHash != storedMetadata.contentHash
            }
            else -> false // 未变化
        }
        
        return if (needsProcessing) {
            val result = doProcessing(filePath)
            // 更新元数据
            metadataStore.update(FileMetadata(
                filePath = filePath,
                lastModified = currentFile.lastModified(),
                contentHash = calculateFileHash(currentFile),
                processingStatus = if (result.success) ProcessingStatus.SUCCEEDED else ProcessingStatus.FAILED,
                lastProcessedTime = System.currentTimeMillis()
            ))
            result
        } else {
            ProcessResult.skipped("File unchanged")
        }
    }
}
```

### 4. 资源调度策略

```kotlin
class SmartResourceScheduler {
    private val taskQueue = PriorityBlockingQueue<ProcessingTask>()
    private var isUserActive = true
    private var backgroundThreadPool: ExecutorService? = null
    
    fun scheduleTask(task: ProcessingTask) {
        when (task.priority) {
            ProcessingPriority.REALTIME -> {
                // 实时任务立即处理
                processImmediately(task)
            }
            ProcessingPriority.HIGH -> {
                // 高优先级任务加入队列前部
                taskQueue.put(task)
            }
            else -> {
                // 其他任务加入队列，等待空闲时处理
                taskQueue.put(task)
            }
        }
    }
    
    fun onUserIdleDetected() {
        isUserActive = false
        startBackgroundProcessing()
    }
    
    fun onUserActivityDetected() {
        isUserActive = true
        throttleBackgroundProcessing()
    }
    
    private fun startBackgroundProcessing() {
        val cores = Runtime.getRuntime().availableProcessors()
        backgroundThreadPool = Executors.newFixedThreadPool(cores / 2)
        
        repeat(cores / 2) {
            backgroundThreadPool?.submit {
                while (!isUserActive && !taskQueue.isEmpty()) {
                    val task = taskQueue.poll()
                    if (task != null && task.priority != ProcessingPriority.REALTIME) {
                        processTask(task)
                    }
                }
            }
        }
    }
}
```

### 5. 智能自动化处理机制

```kotlin
class IntelligentAutoProcessor {
    private val projectDetector = ProjectTypeDetector()
    private val behaviorAnalyzer = UserBehaviorAnalyzer()
    private val resourceMonitor = SystemResourceMonitor()
    
    // 自动项目类型检测和规则适配
    fun autoConfigureForProject(projectPath: String): ProcessingStrategy {
        val projectType = projectDetector.detectProjectType(projectPath)
        
        return when (projectType) {
            ProjectType.KOTLIN_MULTIPLATFORM -> KmpProcessingStrategy()
            ProjectType.NODE_JS -> NodeJsProcessingStrategy() 
            ProjectType.PYTHON -> PythonProcessingStrategy()
            ProjectType.DOCUMENTATION -> DocsProcessingStrategy()
            ProjectType.MIXED -> MixedContentStrategy()
            else -> GeneralProcessingStrategy()
        }
    }
    
    // 基于用户行为的动态优先级调整
    fun adaptPriorityBasedOnBehavior(filePath: String): ProcessingPriority {
        val userStats = behaviorAnalyzer.getFileAccessStats(filePath)
        val baselinePriority = getDefaultPriority(filePath)
        
        return when {
            userStats.accessedInLast24Hours -> ProcessingPriority.HIGH
            userStats.neverAccessed && userStats.ageInDays > 30 -> ProcessingPriority.LOW
            userStats.frequentlyModified -> ProcessingPriority.HIGH
            else -> baselinePriority
        }
    }
    
    // 系统资源自适应调度
    fun getOptimalProcessingMode(): ProcessingMode {
        val resources = resourceMonitor.getCurrentResources()
        
        return when {
            resources.availableMemoryMB < 1000 -> ProcessingMode.LIGHTWEIGHT
            resources.cpuUsagePercent > 80 -> ProcessingMode.BACKGROUND_ONLY
            resources.batteryLevel < 20 -> ProcessingMode.POWER_SAVING
            resources.isOnBattery -> ProcessingMode.BALANCED
            else -> ProcessingMode.FULL_PERFORMANCE
        }
    }
}

// 项目类型自动检测
class ProjectTypeDetector {
    fun detectProjectType(projectPath: String): ProjectType {
        val indicators = scanProjectIndicators(projectPath)
        
        return when {
            indicators.hasFile("build.gradle.kts") && 
            indicators.hasDirectory("src/commonMain") -> ProjectType.KOTLIN_MULTIPLATFORM
            
            indicators.hasFile("package.json") && 
            indicators.hasDirectory("node_modules") -> ProjectType.NODE_JS
            
            indicators.hasFile("requirements.txt") || 
            indicators.hasFile("pyproject.toml") -> ProjectType.PYTHON
            
            indicators.hasDirectory("docs") && 
            indicators.fileCount < 100 -> ProjectType.DOCUMENTATION
            
            else -> ProjectType.MIXED
        }
    }
}

// 用户行为分析
class UserBehaviorAnalyzer {
    private val accessLog = FileAccessLog()
    
    fun getFileAccessStats(filePath: String): FileAccessStats {
        return FileAccessStats(
            accessedInLast24Hours = accessLog.wasAccessedRecently(filePath, 24.hours),
            frequentlyModified = accessLog.getModificationFrequency(filePath) > 5,
            neverAccessed = accessLog.hasNeverBeenAccessed(filePath),
            ageInDays = accessLog.getFileAge(filePath).inWholeDays.toInt()
        )
    }
}

// 智能处理策略（零配置）
abstract class ProcessingStrategy {
    abstract fun shouldProcess(filePath: String): Boolean
    abstract fun getPriority(filePath: String): ProcessingPriority
    abstract fun getProcessingMode(fileSize: Long): ProcessingMode
}

class KmpProcessingStrategy : ProcessingStrategy() {
    override fun shouldProcess(filePath: String): Boolean = when {
        filePath.contains("build/") -> false
        filePath.contains(".gradle/") -> false
        filePath.endsWith(".kt") -> true
        filePath.endsWith(".md") -> true
        filePath.contains("resources/") -> true
        else -> false
    }
    
    override fun getPriority(filePath: String): ProcessingPriority = when {
        filePath.contains("commonMain") -> ProcessingPriority.HIGH
        filePath.contains("src/") && filePath.endsWith(".kt") -> ProcessingPriority.HIGH
        filePath.endsWith("README.md") -> ProcessingPriority.HIGH
        filePath.contains("test/") -> ProcessingPriority.MEDIUM
        else -> ProcessingPriority.LOW
    }
    
    override fun getProcessingMode(fileSize: Long): ProcessingMode = when {
        fileSize > 10.MB -> ProcessingMode.CHUNKED_SAMPLING
        fileSize > 1.MB -> ProcessingMode.STREAMING
        else -> ProcessingMode.FULL_CONTENT
    }
}

// 高级配置（可选，隐藏在高级设置中）
data class AdvancedProcessingConfig(
    val customExcludePatterns: List<String> = emptyList(),
    val customIncludePatterns: List<String> = emptyList(), 
    val forceProcessingFor: List<String> = emptyList(),
    val resourceOverrides: ResourceOverrides? = null,
    val enableExpertMode: Boolean = false
) {
    companion object {
        val DEFAULT = AdvancedProcessingConfig()
        
        // 仅在高级模式下才使用用户配置
        fun getEffectiveConfig(userConfig: AdvancedProcessingConfig?): AdvancedProcessingConfig {
            return if (userConfig?.enableExpertMode == true) {
                userConfig
            } else {
                DEFAULT // 使用智能默认配置
            }
        }
    }
}
```

## 📊 具体处理策略

### 代码库处理策略
```kotlin
class CodebaseProcessor {
    fun processCodebase(projectPath: String): ProcessingPlan {
        return ProcessingPlan(
            // 高价值：源代码和文档
            highPriority = listOf(
                "src/**/*.kt", "src/**/*.java", "src/**/*.py",
                "docs/**/*.md", "README*", "CHANGELOG*"
            ),
            
            // 中等价值：配置和测试
            mediumPriority = listOf(
                "*.json", "*.yml", "*.xml", "*.properties",
                "test/**/*", "spec/**/*"
            ),
            
            // 忽略：依赖和生成文件
            ignored = listOf(
                "node_modules/**", "build/**", ".git/**",
                "vendor/**", "__pycache__/**", "*.class"
            )
        )
    }
}
```

### 大文件智能处理
```kotlin
class LargeFileHandler {
    suspend fun handleLargeFile(filePath: String, size: Long): ProcessResult {
        return when {
            size > 100.MB -> {
                // 超大文件：仅提取基础元数据
                extractMetadataOnly(filePath)
            }
            size > 10.MB -> {
                // 大文件：智能采样处理
                extractWithSampling(filePath)
            }
            else -> {
                // 正常文件：完整处理
                extractFully(filePath)
            }
        }
    }
    
    private suspend fun extractWithSampling(filePath: String): ProcessResult {
        // 只处理文件开头、结尾和随机采样的部分
        val samples = listOf(
            readFileSegment(filePath, 0, 1024),      // 开头1KB
            readFileSegment(filePath, -1024, -1),    // 结尾1KB  
            readRandomSamples(filePath, 5, 512)      // 5个随机512B片段
        ).flatten()
        
        return ProcessResult(
            entities = samples.flatMap { nerService.extractEntities(it) },
            metadata = mapOf("processing_method" to "sampling")
        )
    }
}
```

## 🎯 性能目标

### 处理速度
- **实时任务**: < 100ms响应
- **普通文件**: < 1s处理时间  
- **大文件**: 分块处理，不阻塞UI

### 资源使用
- **内存占用**: < 500MB（包含模型）
- **CPU使用**: 空闲时< 20%，忙时< 80%
- **存储增长**: 智能控制索引大小

### 用户体验
- **UI响应**: 始终保持流畅
- **后台处理**: 不影响正常使用
- **进度反馈**: 清晰的处理状态提示

## 💡 实施要点

1. **渐进式实施** - 从基础规则开始，逐步添加智能特性
2. **可观测性** - 添加详细的处理日志和性能监控
3. **用户控制** - 提供直观的配置界面和实时控制
4. **故障恢复** - 处理失败时的优雅降级和重试机制

这套智能数据处理策略确保了系统能够高效处理各种复杂的数据场景，既最大化价值提取，又避免资源浪费。

---

*专为V0 PoC设计的实用智能数据处理方案*