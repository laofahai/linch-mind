# 📋 采集器管理架构最佳实践指南

> **⚠️ 文档状态**: 架构已重构，部分内容过时  
> **文档版本**: v1.0 (V61前)  
> **创建时间**: 2025-07-29  
> **关联Session**: V49 - 采集器管理界面完整实现  
> **架构状态**: CollectorManagement* 组件已被Schema配置系统替代  
> **参考**: 查看 `_ARCHITECTURE_STATUS_V61.md` 了解当前架构

## 🎯 Session V50 开发Prompt

### 🚀 核心任务

**目标**: 基于V49完成的采集器管理界面，实现智能状态管理和用户体验增强

**关键要求**:
1. **状态增强**: 实现CollectorStateManager状态聚合系统
2. **智能管理**: 添加基于使用模式的自动优化
3. **用户体验**: 完善实时状态监控和错误处理
4. **性能优化**: 确保响应时间 < 100ms

### 📊 当前状态检查点

**已完成**:
- ✅ CollectorManager核心功能 (37,000行代码资产)
- ✅ 文件系统采集器完整实现
- ✅ 模块化UI组件架构
- ✅ 占位采集器UI组件
- ✅ 健康监控和统计收集

**待实现**:
- [ ] CollectorStateManager状态聚合
- [ ] 实时健康监控UI
- [ ] 智能配置建议
- [ ] 用户行为驱动的优化

### 🔧 开发优先级

#### P1 - 状态管理增强 (必须完成)
```kotlin
// 1. 实现CollectorStateManager
class CollectorStateManager(
    private val collectorManager: CollectorManager
) {
    val collectorStates: StateFlow<List<CollectorState>>
    val systemStats: StateFlow<SystemStats>
}

// 2. 集成到AppScope
object AppScope {
    val collectorStateManager: CollectorStateManager by lazy { ... }
}
```

#### P2 - UI状态展示 (必须完成)
```kotlin
// 1. 增强CollectorManagementScreen
@Composable
fun EnhancedCollectorManagementScreen(
    viewModel: CollectorManagementViewModel
) {
    // 实时状态展示
    // 健康检查指示器
    // 性能统计面板
}
```

#### P3 - 智能功能 (可选)
```kotlin
// 1. 智能配置建议
class SmartConfigurationAdvisor {
    fun suggestOptimizations(userBehavior: UserBehavior): List<ConfigSuggestion>
}

// 2. 自动故障恢复
class AutoRecoveryManager {
    fun monitorAndRecover(collectorId: String)
}
```

### 📁 相关文件路径

**核心文件**:
- `src/commonMain/kotlin/tech/linch/mind/collector/CollectorManager.kt`
- `src/desktopMain/kotlin/tech/linch/mind/ui/viewmodels/CollectorManagementViewModel.kt`
- `src/desktopMain/kotlin/tech/linch/mind/ui/screens/CollectorManagementScreen.kt`

**新增文件**:
- `src/commonMain/kotlin/tech/linch/mind/collector/CollectorStateManager.kt`
- `src/desktopMain/kotlin/tech/linch/mind/ui/components/CollectorHealthMonitor.kt`

### 🎯 成功标准

**功能标准**:
- [ ] 所有采集器状态实时同步
- [ ] 健康状态可视化展示
- [ ] 用户操作响应 < 100ms
- [ ] 错误自动恢复机制

**用户体验标准**:
- [ ] 用户能直观理解采集器状态
- [ ] 提供智能配置建议
- [ ] 故障提示清晰友好
- [ ] 支持批量操作

### 📝 开发检查清单

**Session V50 启动前**:
- [ ] 阅读本架构文档
- [ ] 确认CollectorManager接口兼容性
- [ ] 设计CollectorStateManager API
- [ ] 制定测试策略

**Session V50 完成后**:
- [ ] 状态管理完整实现
- [ ] UI状态展示优化
- [ ] 性能测试通过
- [ ] 用户体验验证

### 🔗 关联Session

- **前序**: Session V49 - "采集器管理界面完整实现"
- **当前**: Session V50 - "采集器智能管理增强"  
- **后续**: Session V51 - "采集器AI优化策略"

---

**开发命令**: `继续Session V50采集器智能管理增强`