# 🎯 Linch Mind 日志系统架构设计

## 📖 概述

基于Gemini协商结果，为Linch Mind项目设计的模块化、协程友好的日志系统。

## 🏗️ 技术选型

### 核心依赖
- **SLF4J + Logback**: 成熟稳定的日志框架
- **Kotlin Logging**: Kotlin原生API，提供lazy evaluation
- **Logstash Encoder**: 结构化JSON日志输出
- **Coroutines SLF4J**: 协程上下文传播支持

### 模块化设计

```
tech.linch.mind.logging/
├── LoggerFactory.kt          # 统一日志工厂
├── CollectorLogger.kt        # 采集器专用日志
├── ParserLogger.kt           # 解析器专用日志
├── StorageLogger.kt          # 存储专用日志
├── PerformanceLogger.kt      # 性能监控日志
└── IntelligenceLogger.kt     # 智能分析日志
```

## 🔧 核心特性

### 1. 协程友好
- MDC上下文自动传播
- 协程追踪ID支持
- 异步操作链路追踪

### 2. 结构化日志
- JSON格式输出
- 自动字段提取
- 便于机器分析

### 3. 模块化配置
- 独立的日志级别
- 按模块分文件存储
- 动态配置支持

### 4. 性能监控
- 自动耗时统计
- 慢操作告警
- 内存使用追踪

## 📁 日志文件组织

```
~/.linch-mind/logs/
├── linch-mind.log           # 主日志文件（JSON格式）
├── collector.log            # 采集器专用日志
├── performance.log          # 性能监控日志
└── linch-mind.2025-01-26.log # 按日期轮转
```

## 🎛️ 配置说明

### 日志级别
- **DEBUG**: 详细的内部状态信息
- **INFO**: 重要的业务操作记录
- **WARN**: 潜在问题警告
- **ERROR**: 错误和异常

### 模块配置
- `tech.linch.mind.collector`: DEBUG级别，单独文件
- `tech.linch.mind.parser`: DEBUG级别，主文件
- `tech.linch.mind.performance`: INFO级别，性能文件

## 🚀 使用示例

### 采集器日志
```kotlin
val logger = LoggerFactory.getCollectorLogger()
val context = logger.logFileProcessingStart("/path/to/file.md", "GENERAL_TEXT")
// ... 处理逻辑
logger.logFileProcessingComplete(context, entityCount, "成功")
```

### 性能监控
```kotlin
val perfLogger = LoggerFactory.getPerformanceLogger()
val context = perfLogger.logOperationStart("批量实体存储", mapOf("batchSize" to 100))
// ... 操作逻辑
perfLogger.logOperationComplete(context, "成功")
```

### 协程上下文
```kotlin
LoggerFactory.withLoggingContext(mapOf(
    "collectorId" to "filesystem_001",
    "sessionId" to UUID.randomUUID().toString()
)) {
    // 所有日志都会携带上下文信息
    logger.info { "处理文件" }
}
```

## 🔍 故障排查能力

### 当前问题诊断
针对"采集器过度采集JS文件"问题，日志系统提供：

1. **文件发现透明化**
   ```
   📄 发现文件: /path/.obsidian/main.js (大小: 500KB, 策略: GENERAL_TEXT)
   ```

2. **过滤决策记录**
   ```
   🚫 文件已过滤: /path/.obsidian/main.js (原因: 匹配排除模式 .obsidian/**, 过滤器: 路径过滤器)
   ```

3. **策略选择追踪**
   ```
   🎯 策略选择: /path/file.md -> GENERAL_TEXT (原因: 文件扩展名匹配)
   ```

4. **处理链路完整记录**
   ```
   🔄 开始处理文件: /path/file.md (策略: GENERAL_TEXT)
   ✅ 文件处理完成: /path/file.md (耗时: 150ms, 实体: 5, 结果: 成功)
   ```

## 🎯 解决的痛点

### 之前的问题
- ❌ 只使用println，信息散乱
- ❌ 无法区分模块来源
- ❌ 协程异步操作难以追踪
- ❌ 缺乏性能监控

### 现在的能力
- ✅ 结构化日志，便于分析
- ✅ 模块化日志，清晰分工
- ✅ 协程上下文传播
- ✅ 自动性能监控
- ✅ 故障定位精确

## 🔄 持续优化

### 短期目标
- [x] 集成现有采集器代码 (LoggerFactory和各模块Logger已实现)
- [ ] 添加实时日志监控界面
- [ ] 完善错误恢复机制

### 长期规划
- [ ] 分布式追踪支持
- [ ] 日志聚合分析
- [ ] 智能告警系统