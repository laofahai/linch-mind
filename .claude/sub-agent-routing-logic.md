# Sub-Agent 智能路由逻辑

## 🧠 自动决策算法

### 路由决策树
```python
def route_task_to_specialist(context):
    """
    基于任务上下文智能选择最适合的specialist
    """
    
    # 1. 路径模式匹配
    if matches_path_pattern(context.files, ["src/vector/", "src/intelligence/", "src/ai/"]):
        return "ai-ml-specialist"
    
    if matches_path_pattern(context.files, ["ui/", "compose/", "theme/"]):
        return "ui-ux-specialist"
        
    if matches_path_pattern(context.files, ["storage/", "graph/", "persistence/"]):
        return "data-architecture-specialist"
    
    # 2. 文件名模式匹配
    if matches_file_pattern(context.files, ["*AIService.kt", "*Recommender.kt", "*Embedding*.kt"]):
        return "ai-ml-specialist"
        
    if matches_file_pattern(context.files, ["*Screen.kt", "*Composable.kt", "*Theme.kt"]):
        return "ui-ux-specialist"
        
    if matches_file_pattern(context.files, ["*Storage.kt", "*Repository.kt", "*Entity.kt"]):
        return "data-architecture-specialist"
    
    # 3. 关键词语义分析
    keywords = extract_keywords(context.description)
    
    ai_ml_keywords = ["AI提供者", "推荐算法", "向量搜索", "模型管理", "embedding", "ollama"]
    ui_ux_keywords = ["用户界面", "交互", "跨平台UI", "用户体验", "compose", "界面"]
    data_keywords = ["数据库", "schema", "数据同步", "图存储", "SQLite", "持久化"]
    performance_keywords = ["性能", "内存", "启动", "缓慢", "优化", "并发"]
    security_keywords = ["安全", "隐私", "加密", "权限", "GDPR", "敏感数据"]
    
    if has_keywords(keywords, ai_ml_keywords):
        return "ai-ml-specialist"
    elif has_keywords(keywords, ui_ux_keywords):
        return "ui-ux-specialist"
    elif has_keywords(keywords, data_keywords):
        return "data-architecture-specialist"
    elif has_keywords(keywords, performance_keywords):
        return "performance-optimizer"
    elif has_keywords(keywords, security_keywords):
        return "security-privacy-specialist"
    
    # 4. 任务复杂度评估
    complexity = assess_complexity(context)
    
    if complexity.affects_multiple_modules or complexity.changes_architecture:
        return "core-development-architect"
    
    # 5. 默认路由
    return "general-purpose"  # 兜底方案
```

## 🎯 专业领域定义

### AI/ML 专家领域
```yaml
ai-ml-specialist:
  paths:
    - "src/vector/"
    - "src/intelligence/" 
    - "src/ai/"
  file_patterns:
    - "*AIService.kt"
    - "*Provider.kt"
    - "*Recommender.kt"
    - "*Engine.kt"
    - "*Embedding*.kt"
    - "*Vector*.kt"
  keywords:
    - "AI提供者", "推荐算法", "向量搜索"
    - "模型管理", "embedding", "ollama"
    - "GraphRAG", "PersonalAssistant"
  expertise:
    - 多AI提供者集成架构
    - 向量搜索性能优化
    - 推荐算法调优
    - AI模型管理
    - Prompt工程优化
```

### UI/UX 专家领域
```yaml
ui-ux-specialist:
  paths:
    - "ui/"
    - "compose/"
    - "theme/"
  file_patterns:
    - "*Screen.kt"
    - "*Composable.kt"
    - "*Theme.kt"
    - "*Component.kt"
  keywords:
    - "用户界面", "交互", "跨平台UI"
    - "用户体验", "compose", "界面"
    - "星云图谱", "AI对话界面"
  expertise:
    - Compose Multiplatform跨平台适配
    - 复杂交互设计
    - 用户体验流程优化
    - 无障碍性设计
    - 响应式布局设计
```

### 数据架构专家领域
```yaml
data-architecture-specialist:
  paths:
    - "storage/"
    - "graph/"
    - "persistence/"
  file_patterns:
    - "*Storage.kt"
    - "*Repository.kt"
    - "*Entity.kt"
    - "*Schema.kt"
  keywords:
    - "数据库", "schema", "数据同步"
    - "图存储", "SQLite", "持久化"
    - "Neo4j", "GraphStorage"
  expertise:
    - 图数据库架构设计
    - 实时数据同步策略
    - 数据迁移和版本控制
    - 大规模数据处理优化
    - 数据一致性保证
```

## 🚦 任务复杂度评估

### 复杂度指标
```python
class TaskComplexity:
    def __init__(self, context):
        self.files_count = len(context.files)
        self.modules_affected = count_modules(context.files)
        self.architecture_impact = assess_architecture_impact(context)
        self.user_impact = assess_user_impact(context)
        
    @property
    def level(self):
        if self.files_count > 5 or self.modules_affected > 2:
            return "HIGH"
        elif self.files_count > 2 or self.architecture_impact:
            return "MEDIUM"
        else:
            return "LOW"
            
    @property
    def requires_architect_review(self):
        return (
            self.level == "HIGH" or
            self.architecture_impact or
            self.modules_affected > 2
        )
```

### 决策矩阵
```
┌─────────────────┬─────────────┬─────────────┬─────────────┐
│ 复杂度 \ 领域    │ 技术专业性   │ 架构影响     │ 推荐决策     │
├─────────────────┼─────────────┼─────────────┼─────────────┤
│ LOW + 专业      │ HIGH        │ LOW         │ 专业specialist│
│ LOW + 通用      │ LOW         │ LOW         │ 自主决策     │
│ MEDIUM + 专业   │ HIGH        │ MEDIUM      │ 专业+架构双重│
│ HIGH + 任何     │ ANY         │ HIGH        │ 必须architect │
└─────────────────┴─────────────┴─────────────┴─────────────┘
```

## 🔄 动态上下文适配

### 项目阶段感知
```python
class ProjectPhaseContext:
    def __init__(self):
        self.current_phase = detect_current_phase()
        
    def get_routing_strategy(self):
        if self.current_phase == "EMERGENCY_FIX":
            return EmergencyRoutingStrategy()  # 简化流程
        elif self.current_phase == "ARCHITECTURE_REFACTOR":
            return ArchitectureRoutingStrategy()  # 强化架构审查
        elif self.current_phase == "FEATURE_DEVELOPMENT":
            return StandardRoutingStrategy()  # 标准流程
        else:
            return StandardRoutingStrategy()
```

### 紧急情况处理
```python
class EmergencyRoutingStrategy:
    def route(self, context):
        # 紧急情况下优先快速修复
        if context.is_critical_bug:
            return "core-development-architect"  # 直接架构师处理
        elif context.affects_user_experience:
            specialist = get_primary_specialist(context)
            return specialist or "core-development-architect"
        else:
            return "general-purpose"  # 非紧急任务降级处理
```

## 📊 协作效率监控

### 决策质量追踪
```python
class RoutingDecisionTracker:
    def track_decision(self, context, chosen_agent, outcome):
        """追踪路由决策的效果"""
        decision_record = {
            "timestamp": now(),
            "context": context.to_dict(),
            "chosen_agent": chosen_agent,
            "task_completion_time": outcome.completion_time,
            "quality_score": outcome.quality_score,
            "user_satisfaction": outcome.user_satisfaction
        }
        
        self.save_decision_record(decision_record)
        self.update_routing_model(decision_record)
    
    def get_routing_performance(self):
        """获取路由性能统计"""
        return {
            "accuracy": self.calculate_routing_accuracy(),
            "efficiency": self.calculate_average_completion_time(),
            "specialist_utilization": self.get_specialist_usage_stats()
        }
```

### 自适应优化
```python
class AdaptiveRoutingOptimizer:
    def optimize_routing_rules(self):
        """基于历史数据优化路由规则"""
        performance_data = self.tracker.get_routing_performance()
        
        # 识别低效路由模式
        inefficient_patterns = self.identify_inefficient_patterns(performance_data)
        
        # 调整路由权重
        for pattern in inefficient_patterns:
            self.adjust_routing_weights(pattern)
        
        # 更新专家专业度评分
        self.update_specialist_expertise_scores()
```

## 🎯 实施建议

### 阶段性部署
1. **Phase 1**: 实施核心专家路由 (ai-ml, ui-ux, data-architecture)
2. **Phase 2**: 添加质量保证层专家 (performance, security)
3. **Phase 3**: 引入自适应优化和智能决策

### 监控指标
- 路由准确率 > 85%
- 平均任务完成时间减少 30%
- 专家利用率平衡（没有过载或闲置）
- 跨专家协作效率提升

### 回退机制
```python
class RoutingFallbackStrategy:
    def handle_routing_failure(self, context, failed_agent):
        """处理路由失败情况"""
        if failed_agent in ["ai-ml-specialist", "ui-ux-specialist", "data-architecture-specialist"]:
            return "core-development-architect"  # 升级到架构师
        else:
            return "general-purpose"  # 降级到通用agent
```

---

*该文档描述了Linch Mind项目的智能sub-agent路由系统，确保每个任务都能找到最适合的专业AI协作伙伴。*