# Linch Mind 项目开发上下文

## 💀 CLAUDE 开发铁律 - 违者立即停工

### 💀 三个生死问题（每次修改前必答，答错=立即停工）
1. **用户问题**: 这解决了什么实际问题？**（答不出=伪需求=停工24小时）**
2. **最简方案**: 有更简单的实现方式吗？**（过度设计=停工72小时）**
3. **影响评估**: 会让系统更复杂吗？**（增加复杂度=架构破坏罪）**

### 🚨 工作启动前强制检查流程
```bash
# 💀 跳过任一检查项 = 立即停工
pre_work_mandatory_check() {
    echo "🔍 强制影响范围评估:"
    echo "修改文件数量: _____ 个"
    echo "涉及目录: daemon/ | connectors/ | ui/lib/ | other"
    echo "架构影响级别: 无 | 微调 | 重构 | 架构变更"
    
    # 自动判定必须咨询的sub-agent
    determine_required_consultations
    
    if [[ ${#REQUIRED_AGENTS[@]} -gt 0 ]]; then
        echo "🔴 以下sub-agent咨询为绝对强制，逃避=永久停工:"
        printf '💀 %s\n' "${REQUIRED_AGENTS[@]}"
    fi
}
```

### 💀 Sub-agent强制咨询铁律 - 逃避=永久停工

#### 🚨 **绝对禁止自作主张的红线领域**
```
⚠️  以下领域绝对禁止单独行动，发现未咨询=立即永久停工:
- daemon/、connectors/、ui/lib/ 任何目录的修改
- 超过3个文件的任何修改
- pyproject.toml、pubspec.yaml 的任何变动
- 任何架构、数据流、API的变更
```

#### 🏛️ **架构决策层 - 违者架构破坏罪**
- 💀 **绝对必须咨询 core-development-architect，逃避=永久停工**: 
  - 新增顶层模块或服务（daemon/、connectors/、ui/lib/等）
  - 修改超过3个文件的重构 **（一个都不能少地咨询）**
  - 改变核心数据流（daemon API、connector管理、Flutter UI交互）
  - 引入新的第三方依赖（pyproject.toml、pubspec.yaml修改）
  - 技术选型和架构决策
  
  **💀 咨询质量要求**: 详细问题描述≥100字 + 获得具体可执行建议
  **🚨 检测机制**: 自动扫描修改文件数量 + 强制咨询记录检查
  **⚡ 违规后果**: 立即停工72小时 + 架构理解重新考试

#### 🔬 **专业技术层 - 违者技术渎职罪**
- 💀 **绝对必须咨询 ai-ml-specialist，敷衍咨询=重度违规**:
  - 修改 daemon/models/, daemon/services/ 目录 **（一行代码都不能改）**
  - AI提供者集成和配置（AI服务接口、推荐算法）
  - 推荐算法优化（推荐引擎、智能分析）
  - 向量搜索和embedding（embedding服务、相似性计算）
  - 模型管理和性能调优

- 💀 **绝对必须咨询 ui-ux-specialist，界面破坏=用户体验犯罪**:
  - 修改 ui/lib/ 目录（Flutter应用界面） **（UI改动必须专业指导）**
  - 跨平台UI适配（Flutter widgets、screens）
  - 复杂交互设计（星云图谱、AI对话界面）
  - 用户体验流程优化
  - 界面性能问题

- 💀 **绝对必须咨询 data-architecture-specialist，数据破坏=项目毁灭**:
  - 修改 daemon/models/, daemon/services/ 目录 **（数据完整性至上）**
  - 数据库schema变更（SQLite模型、存储策略）
  - 数据同步和迁移策略
  - 图数据库查询优化
  - 大数据量处理性能

#### ⚡ **质量保证层 - 现升级为强制要求**
- 🔴 **强制咨询 performance-optimizer，性能问题=用户痛苦**:
  - 应用启动缓慢或内存泄漏问题 **（性能就是生命）**
  - 并发处理和协程优化
  - 大数据集处理性能
  - 跨平台性能差异

- 🔴 **强制咨询 security-privacy-specialist，安全问题=项目死刑**:
  - 用户数据加密和隐私保护 **（用户信任不可背叛）**
  - 第三方集成安全审查
  - 敏感数据处理逻辑
  - 权限管理和访问控制

- 💀 **绝对必须咨询 test-specialist，无测试=垃圾代码**:
  - 编写新功能的测试用例（daemon/tests/、ui/test/）
  - 设计测试策略和测试计划
  - 测试覆盖率分析和改进（目标>80%） **（达不到=重写）**
  - Mock策略和测试数据设计
  - CI/CD测试流程优化
  - 性能测试和压力测试方案
  - 处理flaky tests和测试稳定性

#### 📚 **文档管理层 - 无文档=工作无效**
- 💀 **绝对必须咨询 project-docs-manager，文档缺失=工作白做**:
  - 任何架构决策后的文档更新 **（决策无文档=决策无效）**
  - 新功能实现完成后
  - 重大bug修复后
  - API接口变更

#### 🚫 **自主决策严格限制（超出范围=立即违规）**
⚠️  **只有以下微调允许自主决策，任何扩大解释=违规**:
- 简单bug修复（**严格<5行代码，超出=必须咨询**）
- 代码格式化（**仅限空格/换行，逻辑修改=违规**）
- 明显错误修正（**typo级别，功能修改=违规**）
- **禁止项**: 配置文件修改、测试用例编写（必须咨询test-specialist）

### 💀 开发优先级铁序 - 颠倒优先级=项目灾难
1. **🚨 修复影响用户的问题** **（最高优先级，延误=用户流失=项目死亡）**
2. **🔥 提升用户体验** **（用户满意度=项目生死线）**
3. **⚡ 修复测试和构建** **（破坏CI/CD=开发停滞）**
4. **🧹 清理技术债务** **（债务积累=项目腐烂=未来埋雷）**

### 🚨 强制咨询记录要求
```markdown
## 💀 Sub-agent咨询记录模板 [强制填写，缺项=违规]

### 咨询基本信息 [必填]
- **咨询时间**: [精确到分钟]
- **咨询对象**: [specialist名称] 
- **工作类型**: [架构决策|技术实现|质量保证|文档管理]
- **紧急程度**: 高|中|低
- **影响范围**: [详细描述影响的模块和功能]

### 咨询详细内容 [必填，最少100字]
- **核心问题**: [具体要解决的技术问题]
- **上下文信息**: [完整的代码上下文和业务背景]
- **预期结果**: [希望从sub-agent获得什么具体帮助]

### 咨询结果记录 [必填]  
- **获得建议**: [sub-agent的完整建议和方案]
- **建议质量**: 优秀|良好|一般|需要重新咨询
- **采纳决策**: [具体采纳的实施方案]
- **偏离原因**: [如果偏离sub-agent建议的详细理由]

### 执行验证 [必填]
- **实施计划**: [具体的执行步骤和时间表]
- **风险评估**: [实施风险和预防措施]
- **成功标准**: [如何验证实施成功]
- **后续跟踪**: [是否需要进一步咨询]

---
💀 **咨询质量自检清单 [全部勾选才能提交]**:
- [ ] 问题描述详细具体 (≥100字)
- [ ] 获得了可执行的具体建议 (不是"看起来不错"这种废话)
- [ ] 记录了清晰的采纳理由或偏离原因
- [ ] 制定了明确的验证和跟踪计划
- [ ] 咨询质量达到"良好"以上标准

⚠️  **违规检测**: 随机抽查咨询记录完整性，发现敷衍=立即停工
```

## 项目概览
- **项目名称**: Linch Mind - 个人AI生活助手 (Personal AI Life Assistant)
- **核心定位**: 跨应用智能连接器 + 主动推荐引擎 + 个人数据洞察平台
- **当前阶段**: 本地AI驱动的用户体验优化
- **核心架构**: Flutter + Python Daemon + 连接器生态 + 非侵入式数据索引 + 跨设备同步
- **技术栈**: Flutter (跨平台UI), Python FastAPI (后端服务), SQLite, 多AI提供者集成

## 🎯 核心设计理念 (2025-07-25 重大升级)

### 战略定位转变
```
❌ 旧定位: 又一个知识管理工具
✅ 新定位: 真正的个人AI生活助手

目标: 成为用户数字生活的智能中枢，主动发现需求、连接信息、优化决策
```

### 核心价值主张
1. **非侵入式智能**: 数据保持在用户原有应用中，我们只做智能连接
2. **AI能力聚合**: 用户选择自己的AI，我们提供统一的智能交互层
3. **主动价值创造**: 系统主动推荐，而非被动响应查询
4. **跨应用洞察**: 发现用户在不同应用间的隐性关联和模式

## 🏗️ 架构设计

### 核心架构层次
```
┌─────────────────────────────────────────┐
│  用户交互层 (UI/UX)                      │
│  - 智能推荐优先界面                      │
│  - 简化的AI对话界面                      │
│  - 实时状态概览                          │
├─────────────────────────────────────────┤
│  AI插件化层                              │
│  - OpenAI/Claude/Ollama等插件            │
│  - 统一AI能力路由                        │
│  - 用户偏好AI选择                        │
├─────────────────────────────────────────┤
│  智能分析层 (我们的核心价值)              │
│  - 对话数据实时分析                      │
│  - 跨应用关联发现                        │
│  - 个人画像构建                          │
├─────────────────────────────────────────┤
│  非侵入式数据层                          │
│  - 外部应用数据索引                      │
│  - ActivityWatch/浏览器/文件系统连接器   │
│  - 智能同步和增量更新                    │
└─────────────────────────────────────────┘
```

### 数据流设计
```
外部数据源 → 智能索引 → 用户交互 → AI插件处理 → 洞察提取 → 推荐生成
     ↓         ↓         ↓         ↓         ↓         ↓
  ActivityWatch 语义分析   用户对话   AI响应   行为模式   主动推送
  邮件系统   关联发现   查询意图   内容生成  兴趣建模   任务建议
  文件系统   实时监控   上下文     多模态    工作流    学习路径
```

## 当前技术现状
### ✅ 已实现的基础设施
1. **Python Daemon服务**: FastAPI后端 + SQLite存储 + RESTful API
2. **连接器系统**: 文件系统连接器、剪贴板连接器，支持插件化扩展
3. **数据处理管道**: 数据摄取、存储、检索的完整流程
4. **Flutter跨平台UI**: 支持桌面、移动端的统一界面
5. **API客户端**: Flutter与Daemon的HTTP通信层
6. **配置管理**: 连接器配置、系统设置的管理机制

### 🔄 架构升级任务
1. **基础设施完善**: ✅ 日志系统 + 数据持久化 + 系统监控 (已完成)
2. **应用稳定性**: ✅ 启动流程 + 协程管理 + 模型加载机制优化 (已完成)
3. **知识浏览功能**: ✅ 图谱可视化 + 实体搜索 + 关系浏览 (已完成)
4. **采雈器架构优化**: ✅ 插件化设计 (已完成) + 📅 剪贴板采集器 + 浏览器插件 (待实现)
5. **数据源连接器**: 📅 ActivityWatch集成 + 浏览器插件 (计划中)
6. **推荐引擎优化**: ✅ 基于多源数据的推荐质量提升 (已实现行为驱动推荐)
7. **AI服务集成**: ✅ 在daemon中集成多AI提供者 (未来特性)
8. **~~硬件扩展支持~~**: ❌ **已决策推迟**

## 🎯 当前开发计划: 本地AI驱动的用户体验优化

### **核心战略转变 (基于Gemini深度协商)**
> **洞察**: Linch Mind 拥有世界级的技术引擎，但驾驶舱内的仪表盘是画上去的。当务之急是接通线路，让引擎的真实动力体现在用户能感知的驾驶体验上。

#### **战略重新定位**
- **产品定位**: 从技术展示 → 用户价值交付
- **AI策略**: 本地AI优先 + 云端AI可选
- **开发原则**: 最短价值路径 > 架构完美主义
- **交互重点**: 数据真实化 + AI自然语言化

### **Session V20 完成状态: "点亮仪表盘"计划已完成 ✅**

#### **✅ 第一阶段: 数据真实化 (已完成)**
- [x] **移除虚假数据**: 删除所有硬编码的统计数字 
- [x] **连接真实数据**: KnowledgeService → BFF → DaemonClient → UI数据流完全打通
- [x] **PersonalAssistant可见**: 推荐内容在界面正常显示
- [x] **真实统计展示**: 75个实体，263个关系的真实知识图谱

#### **✅ 第二阶段: 基础设施完善 (Session V23-V37 已完成)**
- [x] **日志系统**: Python logging + 结构化日志输出
- [x] **数据持久化**: SQLite数据库 + SQLAlchemy ORM + 完整数据模型
- [x] **行为追踪**: UserBehaviorTrackingService + BehaviorAnalysisEngine
- [x] **智能推荐**: 行为驱动的PersonalAssistant + 推荐质量监控

#### **✅ 智能推荐引擎优化 (Session V21-V37 已完成)**
基于Gemini战略协商，聚焦最大化75实体+263关系的价值：
- [x] **深度推荐算法**: 二度三度关系分析，多维权重计算 (已实现)
- [x] **推荐质量提升**: 行为驱动的个性化推荐 (已实现)
- [x] **用户行为分析**: 交互频率、访问模式、探索路径追踪 (BehaviorAnalysisEngine已实现)
- [x] **多样化推荐**: 基于兴趣、活动模式、探索风格的个性化推荐 (已实现)

#### **✅ Session V62 完成状态: "架构清理与UI集成"计划已完成**

#### **✅ 第四阶段: 架构清理与UI集成 (Session V62 已完成)**
- [x] **单一配置系统**: 移除双重配置系统，统一使用CoreConfigManager
- [x] **API导入修复**: 修复connector_lifecycle.py中的错误导入路径
- [x] **标准化命名**: 统一使用CoreConfigManager替代旧ConfigManager
- [x] **Flutter端口同步**: UI端口从8088修正为58471
- [x] **引用清理**: 清理所有对已删除配置文件的引用
- [x] **测试验证**: 运行测试套件，10/11通过

#### **❗ AI服务集成 (计划重新设计)**
- [ ] **AI API集成**: 在daemon中集成OpenAI/Claude/Ollama等服务
- [ ] **智能推荐**: AI驱动的内容发现和关联分析
- [ ] **模型管理**: 支持本地和云端AI模型的统一管理
- [ ] **对话界面**: Flutter中的AI对话交互体验

## 🤖 本地AI架构设计

### **基于现有Ollama基础设施的扩展**
```python
# 新架构设计 - Python Daemon AI服务
from abc import ABC, abstractmethod

class AIService(ABC):
    @abstractmethod
    async def generate_text(self, prompt: str, model: str) -> str:
        pass
    
    @abstractmethod
    async def analyze_content(self, content: str) -> dict:
        pass

class OpenAIService(AIService):
    # OpenAI API集成
    pass

class LocalLLMService(AIService):
    # 本地模型服务 (Ollama等)
    pass
```

### **模型管理系统设计**
```kotlin
// 模型管理界面和后端服务
class ModelManager {
    suspend fun listAvailableModels(): List<ModelInfo>
    suspend fun downloadModel(modelName: String): Flow<DownloadProgress>
    suspend fun setDefaultModel(modelName: String)
}
```

### **UI集成策略**
- **星云图谱**: hover和点击面板显示AI生成的自然语言描述
- **推荐系统**: PersonalAssistant结果通过AI转换为友好文本
- **模型选择**: 用户可在设置中选择本地模型

### 技术架构文档
- **Daemon架构**: `docs/01_technical_design/daemon_architecture.md` (✅ 已实现 - Python FastAPI架构)
- **Flutter架构**: `docs/01_technical_design/flutter_architecture_design.md` (✅ 已实现 - 跨平台UI架构)
- **连接器开发**: `docs/01_technical_design/connector_internal_management_standards.md` (✅ 已实现 - 开发标准)
- **API契约**: `docs/01_technical_design/api_contract_design.md` (✅ 已实现 - RESTful API规范)
- **日志系统**: `docs/01_technical_design/logging_system/` (✅ 已实现 - 结构化日志)

### 当前架构结构
```
linch-mind/
├── daemon/                      # Python FastAPI后端服务
│   ├── api/                     # API路由和接口
│   ├── models/                  # 数据模型定义
│   ├── services/                # 业务逻辑服务
│   └── config/                  # 配置管理
├── connectors/                  # Python连接器系统
│   ├── filesystem/              # 文件系统连接器
│   ├── clipboard/               # 剪贴板连接器
│   └── shared/                  # 公共基础类
├── ui/                          # Flutter跨平台应用
│   ├── lib/
│   │   ├── screens/             # 应用界面
│   │   ├── services/            # API客户端
│   │   ├── models/              # 数据模型
│   │   └── widgets/             # UI组件
│   └── pubspec.yaml             # Flutter依赖管理
└── docs/                        # 项目文档
    ├── 01_technical_design/
    └── 02_decisions/
```

### V1重构开发原则
1. **用户体验优先**: 每个改动都要提升用户价值感知
2. **非侵入式设计**: 尊重用户现有工作流，不强制迁移数据
3. **AI中立性**: 不偏向任何AI提供商，用户自主选择
4. **隐私优先**: 数据分析在本地进行，用户完全控制
5. **渐进式迭代**: 分阶段发布，持续收集用户反馈

### 成功指标 (V1)
- **用户价值感知**: 用户报告推荐内容的有用性 > 80%
- **AI插件采用**: 支持3+主流AI提供者，用户可自由切换
- **跨应用连接**: 成功连接2+外部数据源 (ActivityWatch + 浏览器/文件)
- **推荐精度**: 基于用户反馈的推荐准确率 > 70%
- **响应性能**: AI对话响应时间 < 3秒，推荐生成 < 1秒
- **多端体验**: 桌面+手机无缝切换，同步延迟 < 5秒

### 已完成的开发里程碑 (Session V20-V38)
1. **✅ Session V20**: 数据真实化 - “点亮仪表盘”计划
2. **✅ Session V21-V22**: 智能推荐引擎优化
3. **✅ Session V23-V27**: 日志系统 + 数据持久化架构
4. **✅ Session V28-V32**: 应用稳定性 + 协程管理
5. **✅ Session V33-V36**: 行为追踪系统 + 分析引擎
6. **✅ Session V37**: 基础设施修复与强化 - “技术债务清零”
7. **✅ Session V38**: 本地AI集成 + AI增强推荐

### 核心原则调整 (V4.0更新)
1. **用户价值优先**: 每个改动都要让用户立即感受到价值
2. **快速迭代验证**: 2周一个完整功能验证周期
3. **数据驱动决策**: 基于用户反馈而非技术完美主义
4. **简单开始**: 先把一个AI用好，再考虑多AI选择
5. **推荐至上**: 推荐质量是唯一重要的技术指标
6. **避免过早优化**: 遵循YAGNI原则，不实现未验证的需求

## 🚀 UI设计重构计划

### 首页布局新设计
```
┌─────────────────────────────────────────┐
│ 🏠 Linch Mind                    [⚙️]   │  <- 极简顶栏
├─────────────────────────────────────────┤
│ 🤖 AI发现新洞察...                       │  <- 智能推荐区(主要)
│ ┌─────────────────────────────────────┐   │
│ │ 💡 基于你最近的学习，我发现...        │   │
│ │ 🔗 这两个概念可能相关...             │   │
│ │ 📅 明天你可能需要处理...             │   │
│ └─────────────────────────────────────┘   │
├─────────────────────────────────────────┤
│ 🔍 有什么想了解的吗？                     │  <- AI对话框
│ [现代化全功能输入界面]                    │
├─────────────────────────────────────────┤
│ 📊 知识库状态    │ ⚡ 系统活动           │  <- 状态概览
│ 4,335个知识点   │ 3个采集器运行         │
│ 136个关联       │ 实时分析进行中        │
└─────────────────────────────────────────┘
```

### UI重构核心原则
1. **删除冗余元素**: 移除右上角会话/登录/设置按钮
2. **推荐优先**: 智能推荐占据页面主要区域
3. **状态透明**: 清晰展示系统在做什么
4. **交互简化**: 减少用户认知负荷

## 💾 数据架构重构

### 非侵入式存储策略
```
用户原始数据位置        │  Linch Mind智能索引
─────────────────────  │  ─────────────────────
~/.local/share/activitywatch/  │  → 活动数据索引
~/Documents/Projects/  │  → 跨文件关系图  
Gmail/Outlook 邮箱     │  → 任务和约会提取
浏览器书签/历史        │  → 兴趣模式分析
```

### 对话数据收集策略
- **实时保存**: 每次AI对话立即分析并存储洞察
- **用户画像**: 基于对话构建兴趣模型和行为模式
- **隐私保护**: 所有分析在本地进行，用户完全控制
- **推荐改进**: 数据用于持续改进推荐质量

## 🔍 系统基础设施问题

### ✅ 日志系统 (已解决)
**现状**: 完整的日志系统已实现
**已实现组件**:
```python
# 当前日志系统 - Python Logging
daemon/
├── api/main.py                 # FastAPI应用日志配置
├── services/                   # 各服务模块日志
└── config/settings.py          # 日志级别和输出配置

connectors/
├── filesystem/main.py          # 文件系统连接器日志
└── clipboard/main.py           # 剪贴板连接器日志
```

**功能特性**:
- ✅ 支持日志级别控制 (TRACE/DEBUG/INFO/WARN/ERROR)
- ✅ 模块化日志器，便于分类和过滤
- ✅ 结构化日志支持 (StructuredLogger接口)
- ✅ 上下文信息支持 (LogContext)

### ✅ 用户行为和对话数据持久化 (已解决)
**现状**: 完整的数据持久化架构已实现
**已实现组件**:
```python
# 当前数据持久化架构 - SQLAlchemy + SQLite
daemon/models/
├── database.py                 # ✅ 数据库连接和配置
├── database_models.py          # ✅ SQLAlchemy ORM模型
├── storage_models.py           # ✅ 数据传输对象
└── api_models.py               # ✅ API接口模型

daemon/services/
├── database_service.py         # ✅ 数据库操作服务
└── storage_strategy.py         # ✅ 数据存储策略
```

**功能特性**:
- ✅ SQLite数据库实现，真正的数据持久化
- ✅ 完整的行为追踪和分析系统
- ✅ 用户画像长期演进支持
- ✅ 历史数据查询和统计功能

### 数据持久化设计要求
1. **隐私优先**: 所有数据本地加密存储
2. **增量更新**: 支持增量数据写入和查询
3. **数据清理**: 定期清理过期数据，用户可控制保留期
4. **备份恢复**: 支持用户数据备份和恢复
5. **性能优化**: 异步写入，不影响UI响应

### 系统监控和诊断
**需要添加的监控能力**:
- 应用启动流程监控
- 模型加载状态追踪
- 协程生命周期监控
- 内存使用情况分析
- 推荐系统性能指标
- 用户交互行为统计

## 🔧 开发环境配置

### 🚀 项目启动命令
**启动daemon**: 使用项目根目录的`./linch-mind`脚本
```bash
./linch-mind  # 自动启动daemon服务
```

### 新增依赖和工具
```kotlin
// AI插件化支持
implementation("io.ktor:ktor-client-core:$ktor_version")
implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:$serialization_version")

// 数据连接器
implementation("com.google.api-client:google-api-client:$google_api_version")
implementation("com.microsoft.graph:microsoft-graph:$msgraph_version")

// 智能分析
implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:$coroutines_version")
implementation("org.jetbrains.kotlinx:kotlinx-datetime:$datetime_version")
```

### 重要配置提醒
- **AI插件配置**: 用户需配置API密钥 (OpenAI, Claude等)
- **ActivityWatch集成**: 需要配置AW API访问权限
- **邮件集成**: 需要OAuth2授权 (Gmail/Outlook)
- **隐私设置**: 用户可选择数据分析范围和保留期限

## 📋 当前任务追踪

### 待办事项追踪
使用TodoWrite工具追踪V1重构进度，重点关注：
1. AI插件化基础架构实现
2. 非侵入式数据连接器开发  
3. 智能推荐引擎构建
4. UI界面重构和用户体验优化

### 关键里程碑
- **Week 4**: AI插件化原型可用
- **Week 8**: 基础推荐功能上线
- **Week 12**: UI重构完成
- **Week 16**: 多端同步MVP发布

---

## 📋 重要决策记录

### 硬件扩展战略决策 (2025-07-25)
**决策**: 推迟硬件设备扩展至V3阶段，采用条件触发机制

**决策理由**:
1. **技术风险过高**: 40-70%失败概率，违反YAGNI原则
2. **市场需求未验证**: 可能是技术驱动的伪需求
3. **资源配置优化**: 聚焦V1桌面应用完善产生更大用户价值
4. **技术栈选择**: Flutter原生方案确定，专注核心功能开发

**V3实施条件** (全部满足才重新考虑):
- V1/V2用户满意度 > 85%
- 20+用户明确请求硬件功能  
- 架构自然演进支持服务化
- 团队具备多设备系统维护能力

**相关文档**:
- `docs/02_decisions/hardware_extension_decision_record.md` - 完整决策分析
- `docs/00_vision_and_strategy/product_vision_and_strategy.md` - 产品战略

### UI技术栈选择决策 (2025-07-25)
**决策**: 采用Flutter原生UI，移除WebView方案考虑
**理由**: Flutter提供原生级性能和优秀的跨平台一致性
**影响**: 图谱可视化等复杂交互使用Flutter原生组件实现

---

## 🛠️ Claude Code 工具集成

### 自定义Slash Commands
- `/arch-review` - 执行全面的架构审查
- `/feature-health <feature-name>` - 检查特定功能的健康状态
- `/quick-fix [issue-type]` - 快速修复常见问题

### Quality Hooks
- **Post-Edit Hook**: 编辑Python/Dart文件后自动运行质量检查
- **Pre-Write Hook**: 修改构建配置前显示警告
- **Pre-Edit Hook**: 编辑文件前显示准备信息

### 项目健康检查
运行 `.claude/project-health-check.sh` 获取项目健康报告：
- 编译状态、代码质量指标、架构健康度
- Git状态、依赖健康度、性能指标

### 提交前检查清单
- [ ] 代码能够编译通过？
- [ ] 是否引入了不必要的复杂性？
- [ ] 是否有更简单的实现方式？
- [ ] 是否解决了用户的实际问题？
- [ ] 是否需要咨询相应的Sub-agent？

---

## 💀 绝对强制技术铁律 - 违者立即永久停工

### 🚨 **自动化违规检测系统** (24/7监控，无处遁形)
```bash
#!/bin/bash
# Pre-commit强制检查脚本 (必须100%通过才能提交)

echo "💀 开始架构合规性扫描..."

# 1. HTTP API调用检测 (致命违规，零容忍)
if grep -r "http://localhost:58471\|curl.*58471\|fetch.*58471" . --exclude-dir=.git; then
    echo "🚫 致命违规: 检测到HTTP API调用！"
    echo "💀 这是架构破坏罪！立即永久停工！"
    echo "📋 违规行为已记录，申诉无效！"
    exit 1
fi

# 2. Poetry规范检测 (重度违规)
if grep -r "pip install\|python -m pip\|^python " . --exclude-dir=.git; then
    echo "🚫 重度违规: 检测到非Poetry命令！"
    echo "💀 立即停工72小时！必须重新培训！"
    echo "⚡ 违规积分+5，累计15分=永久禁入！"
    exit 1
fi

# 3. Sub-agent咨询证明检查 (中度违规)
if [[ $(git log -1 --pretty=format:"%B") != *"咨询"*"specialist"* ]]; then
    echo "⚠️  中度违规: 未发现Sub-agent咨询记录！"
    echo "🔴 停工24小时！必须补充咨询证明！"
    echo "📋 违规积分+3，小心累积后果！"
    exit 1
fi

# 4. 文件修改数量检查 (架构风险)
MODIFIED_FILES=$(git diff --cached --name-only | wc -l)
if [[ $MODIFIED_FILES -gt 3 ]]; then
    if [[ $(git log -1 --pretty=format:"%B") != *"core-development-architect"* ]]; then
        echo "🚫 架构风险: 修改超过3个文件未咨询架构师！"
        echo "💀 立即停工72小时+架构理解重新考试！"
        exit 1
    fi
fi

echo "✅ 架构合规性检查通过，允许提交"
```

### 💀 **绝对禁令条款** (违者无申诉权，立即永久停工)

#### **第一罪: HTTP API调用** (架构破坏罪，不可饶恕)
```
🚫 以下行为构成架构破坏罪，一经发现立即永久停工:
- 使用HTTP调用 (curl http://localhost:58471)
- 任何形式的REST API调用
- 绕过IPC协议的通信行为
- 破坏WebSocket IPC架构完整性

💀 自动检测: 24/7代码扫描 + pre-commit强制阻断
⚡ 立即后果: 永久撤销所有工作权限，无申诉渠道
📋 累犯记录: 永久黑名单，项目永久禁入
🔥 影响评估: 架构破坏=项目毁灭=不可原谅
```

#### **第二罪: Poetry规范违反** (依赖管理犯罪)
```
🚫 以下行为构成依赖管理犯罪:
- 使用 pip install 绕过Poetry
- 使用裸 python 命令而非 poetry run
- 私自修改依赖配置文件
- 破坏虚拟环境隔离性

💀 自动检测: 命令历史扫描 + 环境变量检测  
⚡ 立即后果: 停工72小时 + Poetry重新培训
📋 违规积分: +5分，累计15分永久禁入
🔄 恢复条件: 通过Poetry考试(≥95分) + 承诺书签署
```

### ⚡ **分级惩罚执行机制** (严进严出，违规必究)

#### 💀 **致命违规** (立即永久停工)
```
违规类型: HTTP API调用 | 架构完整性破坏 | 故意违规
立即后果: 永久撤销工作权限
申诉渠道: 无 (不可饶恕)
记录状态: 永久黑名单
```

#### 🔴 **重度违规** (停工72小时 + 重新资格审查)
```
违规类型: Poetry规范违反 | 重要文件未咨询架构师
立即后果: 停工72小时 + 积分+5
恢复条件: 
  1. 完成深度反思报告 (≥1000字)
  2. 通过技术规范考试 (≥95分)
  3. 签署更严格行为约束协议
  4. 接受2周加强监控
```

#### 🟡 **中度违规** (停工24小时 + 强制培训)
```
违规类型: 未咨询必须的sub-agent | 敷衍咨询质量
立即后果: 停工24小时 + 积分+3
恢复条件:
  1. 违规反思报告 (≥300字)
  2. 重新学习sub-agent协作流程
  3. 通过协作规范测试 (≥90分)
```

#### 🟢 **轻度违规** (警告 + 重新提交)
```
违规类型: 代码格式问题 | 文档记录不完整
立即后果: 强制重新提交 + 积分+1
恢复条件: 修正问题并重新提交
```

### 🔐 **技术约束执行细则** (必须100%遵守)

#### **Python开发铁律**
```bash
# ✅ 唯一允许的Python执行方式
poetry run python script.py
poetry run python -c "your_code_here"
poetry add package_name
poetry install
poetry shell

# 🚫 绝对禁止的违规行为
python script.py          # 💀 重度违规: 绕过Poetry
pip install package       # 💀 重度违规: 绕过依赖管理  
python -m pip install     # 💀 重度违规: 绕过虚拟环境
```

#### **IPC通信铁律**
```bash
# ✅ 唯一允许的daemon通信方式
poetry run python -c "
import asyncio
from daemon.services.ipc_client import IPCClient

async def main():
    client = IPCClient()
    result = await client.call('method_name', params)
    print(result)

asyncio.run(main())
"

# 🚫 绝对禁止的违规行为  
curl http://localhost:58471/api/...     # 💀 致命违规: HTTP调用
wget http://localhost:58471/...         # 💀 致命违规: HTTP调用
fetch('http://localhost:58471/...')     # 💀 致命违规: HTTP调用
```

### 🚨 **违规积分累积制** (永久记录，无法清除)
```
违规积分累积后果:
  1分: 口头警告记录
  3分: 停工24小时 + 强制培训
  5分: 停工72小时 + 资格重新审查
  10分: 停工一周 + 架构理解考试  
  15分: 项目参与资格全面Review
  20分: 永久禁止参与项目开发

清零政策: 违规记录永不清零 (诚信一旦破坏无法修复)
```

### 💀 **最终警告**
```
⚠️  最后通牒: 

如果你在看到这些铁律后仍然违规，说明：
1. 你根本没有理解Linch Mind架构的重要性
2. 你不尊重项目质量和团队协作规范  
3. 你不适合参与这个项目的开发工作

💀 违规无小事，架构无妥协！
🔥 项目质量高于一切，违规者必被严惩！
⚡ 这不是建议，这是命令！执行必须绝对！
```

---

*版本: v7.0 | 创建时间: 2025-07-25 | 最后更新: 2025-08-07*  
*💀 重大更新: 开发规范全面军事化管理 + 绝对强制性约束 + 违规零容忍*  
*🚨 Session V65 成果: 架构铁律确立 + 自动化违规检测 + 分级惩罚机制 + 威慑性语言全面升级*  
*⚡ 核心变化: Sub-agent咨询从"建议"升级为"强制" + HTTP API违规从"停工"升级为"永久禁入"*