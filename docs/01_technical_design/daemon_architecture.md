# Linch Mind Python Daemon 架构设计

**版本**: 2.0  
**状态**: 已实现  
**创建时间**: 2025-08-03
**技术栈**: Python FastAPI + SQLAlchemy + SQLite

## 1. 概述

Linch Mind Daemon 是基于Python FastAPI构建的后台服务，负责数据处理、AI服务集成和连接器管理。它通过RESTful API为Flutter UI提供服务，实现"非侵入式主动智能"。

### 1.1. 设计原则
- **解耦与隔离**: Daemon与Flutter UI通过HTTP API通信
- **健壮与容错**: 基于SQLAlchemy的数据持久化和异常处理
- **安全第一**: API认证和数据保护
- **资源感知**: 异步处理，最小化性能影响
- **插件化**: 支持连接器插件动态加载

## 2. 核心职责
- **API服务**: 提供RESTful API服务Flutter客户端
- **数据处理**: 知识图谱构建、向量索引、智能推荐
- **连接器管理**: 管理和调度各类数据连接器
- **AI服务**: 集成多种AI提供者(OpenAI、Claude、本地模型)

## 3. 架构详解

### 3.1. FastAPI服务架构

```python
# 主要组件
daemon/
├── api/                     # API路由层
│   ├── main.py             # FastAPI应用入口
│   └── routers/            # 模块化路由
├── models/                  # 数据模型
│   ├── database_models.py  # SQLAlchemy ORM
│   └── api_models.py       # Pydantic API模型
└── services/               # 业务逻辑层
    ├── database_service.py # 数据服务
    └── connectors/         # 连接器服务
```

### 3.2. 数据库架构

- **数据库**: SQLite + SQLAlchemy ORM
- **连接池**: 支持并发访问
- **迁移**: 基于SQL脚本的数据库迁移
- **模型**: 图节点、关系、用户行为等完整数据模型

### 3.3. 配置管理

- **配置文件**: YAML格式的配置文件
- **环境变量**: 支持环境变量覆盖
- **热重载**: 支持运行时配置更新

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
