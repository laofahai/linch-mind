# Linch Mind Daemon 架构设计

**版本**: 1.0  
**状态**: 已批准  
**创建时间**: 2025-07-27

## 1. 概述

Linch Mind Daemon 是一个独立于主UI应用运行的后台核心服务。它负责所有持续的、异步的数据采集、处理和存储任务，是实现`Linch Mind`“非侵入式主动智能”愿景的技术基石。

### 1.1. 设计原则
- **解耦与隔离**: Daemon与UI是两个独立进程，生命周期完全分离。
- **健壮与容错**: 具备错误恢复、状态持久化和优雅降级能力。
- **安全第一**: 所有跨进程通信和数据访问都必须经过验证。
- **资源感知**: 智能调度任务，最大限度降低对用户前台体验的影响。
- **动态与灵活**: 无需重启即可响应配置变更。

## 2. 核心职责
- **持续运行**: 用户登录后自动启动，在后台持续运行。
- **数据流水线**: 执行完整的数据处理流程（监控、采集、解析、NER、向量化、存储）。
- **状态与控制**: 通过安全的IPC接口，向UI应用暴露其状态并接受控制命令。

## 3. 架构详解

### 3.1. 进程模型与IPC (进程间通信)

- **模型**: 采用独立的Daemon进程 + UI客户端进程模型。
- **IPC机制**: 本地安全的HTTP/REST API (基于Ktor)。
    - **地址与端口**: Daemon启动时尝试绑定预设端口（如`61424`）。若失败，则在备用范围内（如`61425-61430`）选择一个可用端口，并将最终地址写入锁定的状态文件 `~/.linch-mind/daemon.state`。UI应用通过读取此文件来发现服务地址。
    - **安全令牌**: Daemon启动时生成一个高熵随机令牌，并存入上述状态文件（设置严格的文件权限，仅用户可读写）。所有API请求必须在HTTP Header (`X-Auth-Token`)中携带此令牌，Daemon会对每个请求进行校验，防止未授权访问。
    - **API版本化**: API路径包含版本号（如`/api/v1/...`），便于未来进行非破坏性升级。

### 3.2. 数据库并发模型

- **模式**: 采用**单写多读**模式，并始终启用SQLite的**WAL (Write-Ahead Logging)**模式以最大化并发性能。
- **写入方 (Daemon)**:
    - 采用**批量、事务性写入**。例如，积累一定数量的文件处理结果后，在一次数据库事务中全部提交。
    - 使用独立的、具有更高优先级的写连接池。
- **读取方 (UI)**:
    - 查询操作应设置合理的超时和重试逻辑，以应对数据库可能出现的短暂繁忙状态。
    - 避免执行可能锁住全表的超长时间读事务。

### 3.3. 动态配置管理

- **统一配置源**: `~/.linch-mind/config.json`，包含版本号字段`"config_version"`。
- **热重载机制**:
    - Daemon内置`ConfigWatcher`，通过文件系统事件实时监听`config.json`的变更。
    - `ConfigurationManager`在检测到变更后，会**备份**当前配置文件，然后尝试解析新配置。解析成功后，通过Kotlin `StateFlow`以**原子性、非阻塞**的方式将新配置推送给所有订阅的服务。解析失败则记录错误，继续使用旧配置。
- **配置闭环**: UI应用通过`POST /api/v1/config`接口提交配置变更。Daemon接收到请求后，负责写入文件，从而触发自身的热重载流程。

### 3.4. 资源管理与智能调度

- **事件处理**: 对文件系统和配置文件的变更事件，采用**去抖动 (Debouncing)**机制。在短时间内（如500ms）将大量事件合并为单个批处理任务，避免CPU尖峰。
- **任务调度**:
    - 内置一个基于优先级的任务队列。
    - 实现一个`SystemObserver`，用于监测CPU负载、内存使用和电池状态。
    - 调度器根据`SystemObserver`的状态和用户在`config.json`中设定的性能模式（`eco`, `balanced`, `high_performance`），动态调整后台任务的并发数和执行频率。

### 3.5. 错误恢复与数据一致性

- **任务持久化**: 对每个需要处理的文件或数据源，在数据库中创建一个任务记录，并维护其状态（`PENDING`, `PROCESSING`, `DONE`, `FAILED`）。
- **事务性流水线**: 从数据采集到最终写入存储的整个过程，被包裹在一个完整的业务逻辑事务中。只有所有步骤成功，任务状态才被标记为`DONE`。任何一步失败都会导致事务回滚，并将任务标记为`FAILED`，等待后续重试。
- **启动自检**: Daemon启动时，会扫描任务列表，对所有处于`PROCESSING`状态的任务进行检查和恢复，对`FAILED`的任务根据重试策略进行处理。

### 3.6. 生命周期与更新

- **单实例保证**: Daemon启动时，在`~/.linch-mind/`目录下创建并锁定一个`daemon.pid`文件。这可以防止多个Daemon实例同时运行。
- **安装与注册**: 使用成熟的跨平台安装程序框架，在安装时将Daemon注册为系统服务/守护进程 (macOS `launchd`, Windows Service, Linux `systemd`)。
- **安全更新**: 应用的更新程序负责：
    1.  通过IPC API礼貌地请求Daemon关闭。
    2.  若无响应，则通过PID强制终止进程。
    3.  释放PID文件锁。
    4.  替换二进制文件。
    5.  启动新版Daemon。
- **配置迁移**: 更新后，新版Daemon启动时会检查`config.json`中的`config_version`。如果版本不匹配，会自动备份旧配置文件，并执行迁移逻辑，确保用户配置不丢失。

---

## 4. 架构最佳实践 (基于Session V12优化)

**更新时间**: 2025-07-27  
**基于**: Session V12架构分析和Gemini技术咨询

### 4.1. 混合职责边界模型

基于实际实施经验，发现纯粹的进程分离可能导致过度分离问题。最优架构应采用**混合职责边界模型**：

#### 核心原则调整
- **Daemon职责**: 专注于数据流水线和后台服务，提供BFF(Backend for Frontend)式的业务API
- **UI职责**: 增强为智能客户端，包含ViewModel层、本地状态管理和缓存
- **通信优化**: 从细粒度CRUD API转换为场景化业务API，减少网络往返

#### 架构对比

**之前的实现** (存在问题):
```
UI (瘦客户端) ←→ HTTP CRUD API ←→ Daemon (全功能后端)
- 问题：UI过于依赖API，每个操作都需要网络调用
- 性能：多次往返，累积延迟明显
```

**优化后的架构** (推荐):
```
UI (智能客户端) ←→ BFF业务API ←→ Daemon (核心引擎)
- 优势：UI有应用逻辑层，本地交互无延迟
- 性能：单次API调用获取完整业务数据
```

### 4.2. BFF API设计模式

#### 场景化API设计
```kotlin
// ✅ 推荐：面向业务场景的高阶API
POST /api/v1/views/graph-main
POST /api/v1/views/knowledge-browser  
POST /api/v1/views/ai-conversation

// ❌ 避免：暴露实现细节的低阶API
GET /api/v1/entities
GET /api/v1/relationships
POST /api/v1/search
```

#### 批量操作支持
```kotlin
// 将多个小操作合并为单次调用
POST /api/v1/batch {
  "operations": [
    {"type": "get_entity", "id": "entity1"},
    {"type": "get_relationships", "entityId": "entity1"},
    {"type": "get_neighbors", "entityId": "entity1"}
  ]
}
```

### 4.3. UI客户端架构增强

#### ViewModel层引入
```kotlin
class KnowledgeGraphViewModel(
    private val daemonClient: DaemonClient
) {
    // 本地状态管理
    private val _selectedNodes = MutableStateFlow<Set<String>>(emptySet())
    val selectedNodes: StateFlow<Set<String>> = _selectedNodes.asStateFlow()
    
    // 本地交互逻辑（无需API调用）
    fun selectNode(nodeId: String) {
        _selectedNodes.value = _selectedNodes.value + nodeId
        // 立即响应，无网络延迟
    }
    
    // 数据获取使用BFF API
    suspend fun loadMainGraphView() {
        val viewData = daemonClient.getGraphMainView(...)
        // 单次调用获取完整数据
    }
}
```

#### 缓存策略
- **UI层**: ViewModel状态缓存，避免重复API调用
- **客户端层**: DaemonClient响应缓存，提升重复请求性能
- **服务层**: Daemon业务逻辑缓存，减少计算开销

### 4.4. 性能优化指标

#### 关键性能目标
- **API响应时间**: < 200ms (vs 之前500ms+)
- **UI交互延迟**: < 16ms (60fps流畅度)
- **网络往返**: 主视图加载 ≤ 2次API调用
- **内存使用**: UI < 200MB, Daemon < 500MB

#### 实时通信支持
```kotlin
// WebSocket用于实时事件
class DaemonWebSocketClient {
    suspend fun subscribeToRecommendations(callback: (Recommendation) -> Unit)
    suspend fun subscribeToDataChanges(callback: (DataChangeEvent) -> Unit)
}
```

### 4.5. 迁移最佳实践

#### 渐进式迁移策略
1. **Phase 1**: 消除架构双轨制（统一入口点）
2. **Phase 2**: BFF API重构（场景化API）
3. **Phase 3**: UI客户端增强（ViewModel层）
4. **Phase 4**: 性能监控优化（WebSocket + 监控）

#### 风险缓解措施
- 保持向后兼容性，渐进式替换
- 建立性能基线，持续监控
- 详细文档和团队培训

### 4.6. 相关文档

- [Daemon架构最佳实践指南](daemon_architecture_best_practices.md) - 详细实施指南
- [Session V12架构优化决策](../02_decisions/daemon_architecture_optimization_session_v12.md) - 决策记录
- [Session V7架构决策](../02_decisions/daemon_architecture_decision_session_v7.md) - 原始架构决策

---

**重要提醒**: 架构设计需要在"分离"和"效率"之间找到平衡。过度分离会带来性能和开发效率问题，而不足的分离则无法解决原始的资源竞争问题。混合职责边界模型是当前的最优解。
