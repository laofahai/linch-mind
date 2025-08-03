# 决策记录-002: Daemon架构实施决策 (Session V7)

**状态**: 已决策  
**日期**: 2025-07-27  
**决策者**: 开发团队 + Gemini技术咨询  
**背景**: 基于实际代码复杂度和系统问题的daemon架构需求评估

## 决策背景

在Session V7开发过程中，遇到了严重的系统架构问题：
- `LockObtainFailedException: Lock held by another program` 导致应用无法启动
- 用户完全无法使用应用，现有数据无法访问
- 需要从实际需要和现有实现角度重新评估daemon架构

## 实际问题分析

### 当前系统复杂度
- **代码规模**: 119个Kotlin文件，45,031行代码
- **技术栈**: Kotlin Multiplatform + Compose + SQLite + Lucene + AI服务
- **服务耦合**: UI完全依赖后台服务初始化成功

### 根本问题
1. **文件锁冲突**: Lucene IndexWriter锁被占用，整个应用启动失败
2. **进程内资源竞争**: 多个组件无序争抢独占性资源
3. **生命周期耦合**: 一个服务失败导致整个应用无法使用
4. **重复初始化开销**: 每次重启都要重新加载AI模型、重建索引

## Gemini技术咨询分析

### 核心洞察
- **45K行代码已超出单进程舒适区上限** - 这是架构复杂性达到临界点的典型信号
- **LockObtainFailedException不是偶然** - 而是多组件无序争抢独占资源的必然结果
- **当前不是"是否需要"的问题** - 而是"何时实施"的问题

### 方案对比

#### 方案A: 修复当前架构 (战术修复)
**优点**:
- 快速见效，1-2天解决紧急问题
- 资源投入少，风险可控

**缺点**:
- 治标不治本，技术债务累积
- 锁重试只是推迟问题
- 无法支撑未来扩展需求
- 45K行代码单进程管理已达极限

#### 方案B: Daemon架构 (战略重构)
**优点**:
- 根除问题：进程隔离避免锁冲突
- 生命周期解耦：UI和服务独立运行
- 提升稳定性：一方崩溃不影响另一方
- 为未来铺路：API驱动，支持多客户端和插件化

**缺点**:
- 开发成本高，2-3周投入
- 引入IPC通信复杂性
- 需要进程管理和API设计

## 决策结果

**选择方案**: 混合策略 - 紧急止血 + 战略重构

### 实施计划

#### Phase 1: 紧急止血 (1-2天)
```kotlin
// 最小修复：只添加Lucene锁重试
private suspend fun initializeWithRetry() {
    repeat(3) { attempt ->
        try {
            indexWriter = IndexWriter(directory, config)
            return
        } catch (e: LockObtainFailedException) {
            if (attempt < 2) {
                delay(5000) // 等待5秒
                cleanupStaleLocks()
            } else throw e
        }
    }
}
```

#### Phase 2: 架构重构 (2-3周)
- 实施完整的Daemon架构
- 使用Ktor构建HTTP/REST API
- 进程分离：UI客户端 + 数据服务Daemon
- 技术选型：
  - 通信框架：Ktor Server
  - 数据格式：JSON + kotlinx.serialization
  - 进程管理：系统服务注册

## 决策理由

1. **技术必然性**: 45K行代码的复杂应用已超出单进程管理能力
2. **用户体验**: 当前架构导致应用完全无法启动，用户无法使用
3. **未来扩展**: AI插件化、多设备同步等需求需要架构支撑
4. **投资回报**: 2-3周投入换来长期稳定性和可扩展性

## 决策后果

### 积极影响
- ✅ **根除问题**: 彻底解决文件锁和服务耦合问题
- ✅ **提升稳定性**: 进程隔离大幅提升系统健壮性
- ✅ **加速开发**: 架构成型后新功能开发更快
- ✅ **支撑未来**: 为AI插件化和多端扩展奠定基础

### 潜在风险
- ⚠️ **开发成本**: 2-3周的投入对小团队是挑战
- ⚠️ **新复杂性**: IPC通信和进程管理需要学习成本
- ⚠️ **过渡期**: 重构期间功能开发会暂停

## 技术实施要点

### Daemon架构设计
```
┌─────────────────┐    HTTP/REST API    ┌─────────────────┐
│   UI Client     │ ←───────────────→   │  Data Daemon    │
│  (Compose UI)   │     JSON/Ktor       │  (Background)   │
│                 │                     │                 │
│ - User Interface│                     │ - SQLite        │
│ - AI Chat       │                     │ - Lucene Index  │
│ - Visualization │                     │ - AI Models     │
│ - Settings      │                     │ - Data Collect  │
└─────────────────┘                     └─────────────────┘
```

### API设计原则
- RESTful设计，版本化URL (`/api/v1/...`)
- 安全认证：随机令牌 + HTTPS
- 错误处理：统一错误响应格式
- 异步支持：长时间操作返回任务ID

## 下一步行动

1. **立即实施Phase 1**: 修复Lucene锁问题，让应用能启动
2. **规划Phase 2**: 设计Daemon API和数据流
3. **团队对齐**: 确保团队理解架构重构的必要性和价值
4. **用户沟通**: 告知用户即将进行的重大改进

---

**备注**: 本决策基于实际代码复杂度分析（119文件，45K行）和Gemini专业技术咨询，推翻了V4文档中"daemon为未来特性"的标记，认为daemon架构是当前技术必需而非未来特性。

**相关文档**: 
- `daemon_architecture.md` - 完整技术设计
- `session_v7_hover_fixes.md` - 本次session的其他技术改进