---
allowed-tools: [Bash, Glob, Read, LS, TodoWrite]
description: "AI Workflow Session 智能结束器 - 完整的 session 结束和清理工作流"
---

# 🔚 /end-session - AI Workflow Session 智能结束器

**完整的 Linch Mind AI Workflow Session 结束流程，包含智能清理和状态报告**

## 🎯 Session 结束流程概览

### 📊 Step 1: Session 状态收集
!`echo "🔍 收集 Session 状态..." && echo "Session ID: $(date +%Y%m%d-%H%M%S)" && echo "开始时间: $(date)" && echo "当前分支: $(git branch --show-current)" && echo "Git 状态: $(git status --porcelain | wc -l) 个文件待处理"`

### 📋 Step 2: 待办事项强制检查
!`echo "📋 检查待办事项完成情况..." && echo "正在分析当前 TodoList 状态..."`

**⚠️ 重要约束：Session 结束前的任务完成要求**

在继续 session 结束流程之前，**必须确保以下条件**：

1. **所有待办任务状态检查**：
   - 使用 TodoWrite 工具检查所有当前任务状态
   - **禁止条件**：任务状态为 `in_progress` 或 `pending` 时不得结束 session
   - **必须条件**：所有关键任务必须标记为 `completed`

2. **任务完成验证**：
   - 核实每个已完成任务确实已经实现
   - 检查代码变更是否与任务目标一致
   - 验证功能测试和质量检查是否通过

3. **强制性操作**：
   - 如发现未完成任务，**必须**先完成任务或将其合理转移到下一 session
   - **不允许**带着未完成的关键任务强制结束 session
   - 如有紧急情况需要结束，必须在 session 总结中详细说明原因和后续计划

**中文提示**：
```
🚨 Session 结束检查失败！
发现未完成的任务，请完成以下操作之一：
1. 完成所有 in_progress 和 pending 状态的任务
2. 将未完成任务合理转移并在总结中说明
3. 提供充分理由说明为何需要带着未完成任务结束 session
```

TodoWrite 将自动显示当前任务状态，**必须**全部为 `completed` 状态才能继续。

### 📝 Step 3: 生成 Session 总结文档
创建详细的session总结文档在 `docs/03_sessions/session_v[N]_summary.md`，包含：
- Session概要和目标
- 主要成果和交付物
- 关键技术实现
- 架构决策和优化
- 当前待办事项状态
- 关键洞察和经验教训
- 文件变更和新实现

### 🧹 Step 4: 智能清理系统

#### 4.1 执行完整的 cleanup 扫描
!`echo "🧹 启动智能清理系统..." && echo "执行 .claude 目录清理扫描..."`

#### 4.2 扫描 .claude 目录结构
使用 **Glob** 和 **LS** 工具扫描 `.claude` 目录：

!`echo "📁 扫描 .claude 目录结构..." && ls -la .claude/ 2>/dev/null | grep -E "^-" | wc -l | xargs -I {} echo "发现 {} 个文件"`

#### 4.3 识别清理目标文件
按照 cleanup 规则扫描各种临时文件：

**🧪 测试和调试文件**
!`echo "🔍 扫描测试和调试文件..." && find .claude -name "test-*.md" -o -name "test-*.ts" -o -name "debug-*.js" -o -name "temp-*.md" 2>/dev/null | head -10 || echo "未找到测试文件"`

**📦 版本化文件**  
!`echo "📦 扫描版本化文件..." && find .claude -name "*-v[0-9].*" -o -name "*-lite.*" -o -name "enhanced-*-v[0-9].*" 2>/dev/null | head -10 || echo "未找到版本化文件"`

**⏰ 临时文件**
!`echo "⏰ 扫描临时文件..." && find .claude -name "temp-*" -o -name "tmp-*" -o -name "example-*" 2>/dev/null | head -10 || echo "未找到临时文件"`

**📋 日志和缓存**
!`echo "📋 扫描日志和缓存..." && find .claude -name "*.log" -o -name "*.cache" -o -name "*.tmp" 2>/dev/null | head -10 || echo "未找到日志文件"`

**🗑️ 空文件和占位符**
!`echo "🗑️ 检查空文件..." && find .claude -type f -empty 2>/dev/null | head -5 || echo "未找到空文件"`

### 📊 Step 5: 生成清理建议报告

!`echo "📊 生成智能清理建议..." && echo "=== 清理建议报告 ===" && echo "扫描时间: $(date)" && echo "项目路径: $(pwd)"`

### 📈 Step 6: 深度评估与下一 Session 提示生成

#### 6.1 🔍 全面深度评估（必须步骤）
在生成下一个session prompt之前，必须进行完整的深度评估：

**📊 Session成果全面评估**
- 回顾当前session的所有代码变更
- 分析架构决策的影响和结果
- 评估实现质量和技术债务
- 检查是否达成了session目标

**📚 文档体系审查**
- 审查所有技术设计文档
- 检查架构决策记录
- 验证CLAUDE.md指导原则的遵循情况
- 确认文档与代码的一致性

**🔧 代码实现深度分析**
- 检查所有新增和修改的代码文件
- 评估代码质量和可维护性
- 识别潜在的性能问题和优化点
- 验证功能完整性和边界情况处理

**💭 战略思考与反思**
- 思考当前实现对整体架构的影响
- 评估技术选择的长期影响
- 反思开发过程中的经验教训
- 识别可以改进的开发模式

#### 6.2 📝 生成下一 Session 提示
基于深度评估结果，创建下一session的详细提示文档在 `docs/03_sessions/session_v[N+1]_prompt.md`，包括：
- 当前session的完整上下文总结
- 深度评估得出的关键洞察
- 剩余任务和调整后的优先级
- 技术约束和架构要求
- 明确的成功标准和目标
- 相关代码引用和当前状态
- 识别的风险和应对策略
- 具体的实施建议和路径

#### 6.3 🎯 Next Session 最佳实践指导（基于Session V42经验）

⚠️ **重要**: 基于Session V42重复造轮子的教训，每个新session都必须遵循以下最佳实践

##### 🔍 开发前强制检查清单（100%必须完成）
在开始任何开发工作之前，未来session必须严格按顺序完成：

```
□ 1. 阅读项目核心文档 (CLAUDE.md) - 了解项目当前状态和技术栈
□ 2. 查阅相关决策记录 (docs/02_decisions/) - 避免违背已明确的架构决策  
□ 3. 搜索现有实现 - 使用Grep/Glob工具避免重复造轮子
□ 4. 评估第三方成熟方案 - 优先使用成熟解决方案
□ 5. 确认用户价值和UI展现 - 确保技术实现转化为用户可感知价值
□ 6. 制定实施计划 - 明确的技术路径和里程碑
```

##### 🔎 现有实现调研指南（Session V42案例学习）
**关键教训**: 项目已有37,000+行代码，包括世界级的2.5D星云知识图谱

**调研流程**:
1. **功能关键词搜索**:
   ```bash
   rg -i "[功能关键词]" --type kotlin
   # 例如: rg -i "graph|图谱" --type kotlin
   ```

2. **核心架构文件必读**:
   ```
   src/commonMain/kotlin/tech/linch/mind/
   ├── AppScope.kt                    # 全局服务容器
   ├── intelligence/PersonalAssistant.kt    # 智能推荐核心
   ├── knowledge/KnowledgeService.kt        # 知识图谱服务
   ├── ui/services/AppServices.kt           # UI服务聚合器
   └── ai/LocalAIService.kt                # AI服务集成
   
   src/desktopMain/kotlin/tech/linch/mind/ui/components/
   └── KnowledgeGraphView.kt               # ⚠️ 2.5D星云图谱实现
   ```

3. **深度实现分析**:
   - 不只看文件名，必须阅读实现代码
   - 理解设计意图和注释说明
   - 评估现有实现是否已满足需求

##### 📋 项目决策记录强制遵循
**Session V42教训**: 差点违背"否决纯WebView方案"的明确决策

**关键决策摘要**（截至2025-07-28）:
- ✅ **Compose原生UI优先**: 保持Compose原生UI优势
- ❌ **纯WebView方案被否决**: 仅特殊场景使用WebView  
- ✅ **本地AI优先**: 云端AI作为可选扩展
- ❌ **硬件设备扩展推迟**: 推迟至V3阶段

**强制检查**: 任何技术选择都必须先查阅 `docs/02_decisions/` 相关决策记录

##### 🛡️ 风险规避机制（Session V42验证有效）

**1. 重复造轮子风险识别**
```
⚠️ 危险信号:
- 想要实现"新"功能前未搜索现有代码
- 考虑引入新技术栈解决已有功能
- 计划重新设计已有的核心组件

✅ 预防措施:
- 强制使用Grep/Glob搜索相关实现
- 优先扩展现有组件而非重新创建
- 新技术引入需要充分论证必要性
```

**2. 架构偏离预警**
```
⚠️ 危险信号:
- 违背明确的架构决策记录
- 引入与现有架构不一致的模式
- 绕过现有的服务层和接口

✅ 预防措施:
- 严格遵循现有的依赖注入模式
- 使用现有的服务聚合器 (AppServices)
- 保持与现有UI组件的设计一致性
```

**3. 用户价值迷失防范**
```
❌ Session V42反面教材:
技术实现 → 复杂的WebView图谱优化
用户感知 → "没有看到任何变化"

✅ 正确模式:
技术实现 → PersonalAssistant智能推荐展示
用户感知 → "系统很智能，推荐很有用"

强制要求: 每个技术实现都必须有对应的UI展现
```

##### 📚 Session V42 案例深度学习

**错误决策过程还原**:
1. ❌ 看到"升级交互式知识图谱可视化"任务
2. ❌ 直接考虑WebView+Cytoscape.js方案  
3. ❌ 未搜索现有的KnowledgeGraphView.kt实现
4. ❌ 未查阅WebView相关的架构决策记录
5. ❌ 开始增强graph-template.html

**正确决策过程**:
1. ✅ 先搜索现有图谱相关实现
2. ✅ 发现KnowledgeGraphView.kt - 2.5D星云图谱
3. ✅ 查阅架构决策 - WebView方案被明确否决  
4. ✅ 评估现有实现 - 已有世界级的Compose原生实现
5. ✅ 决定优化现有组件而非重新开发

**关键洞察**:
- **37,000行代码是巨大资产**: 必须先了解再创新
- **架构决策有深层原因**: 违背决策通常会引入技术债务
- **Compose原生 > WebView**: 性能更好，集成更简单
- **用户价值 > 技术炫技**: 技术实现必须转化为用户体验

##### 🎯 Next Session Prompt 增强格式

下一session的prompt必须包含以下最佳实践部分：

```markdown
## 🔍 开发前强制检查清单
在开始任何开发工作前，必须完成：
□ 已阅读CLAUDE.md项目总体情况  
□ 已查阅相关架构决策记录
□ 已搜索并评估现有实现 
□ 已评估第三方方案可行性
□ 已确认用户价值和UI展现方案
□ 已制定详细实施计划

## ⚠️ Session V42 风险规避提醒
1. **重复造轮子检查**: 项目已有37,000+行代码，包括2.5D星云图谱
2. **架构决策遵循**: 严禁违背docs/02_decisions/中的明确决策
3. **用户价值导向**: 所有技术实现必须有UI展现和用户感知价值

## 🎯 核心原则 (不可违背)
- 现有实现优先 - 利用现有代码资产
- 架构决策遵循 - 严格按照项目决策执行  
- 用户价值导向 - 技术必须转化为用户可感知价值
- Compose原生优先 - 避免不必要的WebView使用
```

### 🎯 下一 Session 提示格式
```
📋 Session V[N+1] 开发提示 - [Next Topic]

🎯 Session V[N] 重大成果回顾
[key achievements summary]

🔍 当前状态验证
[current system state]

🎯 Session V[N+1] 核心任务
[next session objectives]

🔧 实施计划
[detailed implementation plan]

💡 关键洞察应用
[lessons from previous session]

🎯 成功标志
[success criteria]
```

## 📄 Session 文档结构
```markdown
# Session V[N]: [Title]

## 📋 Session概要
- 目标: [main objectives]
- 基于: [previous work foundation]

## ✅ 主要成果
[detailed accomplishments]

## 🎯 核心技术亮点
[key technical achievements]

## 📊 成功指标达成情况
[metrics and goals achieved]

## 🔧 关键实现文件
[files created/modified]

## 🚀 架构优化亮点
[architectural improvements]

## 📈 下一阶段建议
[next steps and recommendations]
```

## 使用方法

输入 `/end-session` 即可开始session结束流程。