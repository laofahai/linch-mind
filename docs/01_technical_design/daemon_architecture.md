# Linch Mind Python Daemon 架构设计

**版本**: 3.0  
**状态**: 已实现  
**创建时间**: 2025-08-03  
**最新更新**: 2025-08-06  
**技术栈**: 纯IPC架构 + SQLAlchemy + SQLite

## 🚀 重大架构升级 (v3.0)

**从HTTP到IPC的完全迁移**: 项目已完成从FastAPI+HTTP到纯IPC(进程间通信)架构的重大升级，显著提升性能、安全性和部署便利性。

## 1. 概述

Linch Mind Daemon 是基于纯IPC架构构建的后台服务，负责数据处理、AI服务集成和连接器管理。它通过高性能IPC通信为Flutter UI和连接器提供服务，实现"非侵入式主动智能"。

### 1.1. 设计原则
- **纯IPC通信**: 通过Unix Socket (Linux/macOS) 和 Named Pipe (Windows) 进行本地进程间通信
- **零网络暴露**: 完全本地通信，无网络安全风险
- **极致性能**: IPC通信延迟 < 1ms，RPS > 30,000
- **跨平台兼容**: 统一API接口，底层自适应不同操作系统
- **安全优先**: 进程身份验证、文件权限控制、频率限制
- **向后兼容**: 现有客户端代码无需修改

## 2. 核心职责
- **IPC服务**: 提供高性能IPC通信服务多客户端
- **数据处理**: 知识图谱构建、向量索引、智能推荐
- **连接器管理**: 管理和调度各类数据连接器
- **AI服务**: 集成多种AI提供者(OpenAI、Claude、本地模型)
- **安全管理**: 进程身份验证、访问控制、频率限制

## 3. 架构详解

### 3.1. 纯IPC架构概览

```
┌─────────────────────────────────────────┐
│         客户端应用 (Flutter/连接器)        │
├─────────────────────────────────────────┤
│       兼容层 (HTTP-to-IPC适配器)         │
├─────────────────────────────────────────┤
│       IPC客户端 (IPCClient)              │
├─────────────────────────────────────────┤
│    IPC通信层 (Unix Socket/Named Pipe)   │
├─────────────────────────────────────────┤
│       IPC服务器 (IPCServer)              │
├─────────────────────────────────────────┤
│     中间件系统 (认证/日志/限流)            │
├─────────────────────────────────────────┤
│     路由系统 (IPCApplication/Router)     │
├─────────────────────────────────────────┤
│      业务逻辑层 (Services/Controllers)    │
└─────────────────────────────────────────┘
```

### 3.2. 核心组件架构

```python
# 纯IPC架构组件
daemon/
├── ipc_main.py             # IPC应用入口
├── services/
│   ├── ipc_server.py       # IPC服务器
│   ├── ipc_router.py       # 路由系统
│   ├── ipc_middleware.py   # 中间件系统
│   ├── ipc_routes.py       # 路由定义
│   ├── ipc_security.py     # 安全管理
│   ├── ipc_client.py       # IPC客户端
│   ├── compatibility_layer.py  # HTTP兼容层
│   └── windows_ipc_server.py   # Windows Named Pipe
├── models/                  # 数据模型
│   ├── database_models.py  # SQLAlchemy ORM
│   └── api_models.py       # 数据传输对象
├── config/
│   └── ipc_security_config.py  # IPC安全配置
└── tests/
    ├── test_ipc_integration.py # IPC集成测试
    └── performance_benchmark.py # 性能基准
```

### 3.3. IPC通信协议

#### 消息格式
```json
{
    "method": "GET|POST|PUT|DELETE",
    "path": "/api/endpoint",
    "data": {...},
    "headers": {...},
    "query_params": {...}
}
```

#### 响应格式
```json
{
    "status_code": 200,
    "data": {...},
    "headers": {...}
}
```

#### 通信机制
- **消息长度前缀**: 4字节 (big endian)
- **消息编码**: UTF-8 JSON
- **连接复用**: 长连接支持多请求
- **异步处理**: 完全异步I/O

### 3.4. 跨平台支持

#### Unix系统 (Linux/macOS)
```python
# Unix Domain Socket
socket_path = f"/tmp/linch-mind-{os.getpid()}.sock"
server = await asyncio.start_unix_server(handler, socket_path)
# 文件权限设置为600 (仅owner可访问)
os.chmod(socket_path, 0o600)
```

#### Windows系统
```python
# Named Pipe
pipe_name = f"linch-mind-{os.getpid()}"
pipe_path = f"\\\\.\\pipe\\{pipe_name}"
# 使用Windows安全描述符控制访问权限
```

### 3.5. 数据库架构

- **数据库**: SQLite + SQLAlchemy ORM
- **连接池**: 支持并发访问
- **迁移**: 基于SQL脚本的数据库迁移
- **模型**: 图节点、关系、用户行为等完整数据模型

### 3.6. 安全配置管理

- **IPC安全配置**: 进程身份验证、频率限制、访问控制
- **文件权限管理**: Socket文件权限控制
- **配置文件**: YAML格式的配置文件
- **环境变量**: 支持环境变量覆盖
- **热重载**: 支持运行时配置更新

#### 安全配置示例
```python
# config/ipc_security_config.py
IPC_SECURITY_CONFIG = {
    "authentication": {
        "enabled": True,
        "allowed_processes": {"flutter_ui": True, "connector_*": True}
    },
    "rate_limiting": {
        "enabled": True,
        "max_requests_per_second": 100,
        "burst_limit": 200
    },
    "access_control": {
        "socket_permissions": 0o600,
        "require_same_user": True
    }
}
```

## 4. 性能基准与优化

### 4.1. IPC性能基准测试结果

基于实际测试的性能数据：

```
┌─────────────────────┬─────────────────┬─────────────────┬─────────────────┐
│      测试场景       │       RPS       │   平均延迟(ms)   │   成功率(%)     │
├─────────────────────┼─────────────────┼─────────────────┼─────────────────┤
│   单客户端基准      │     14,630      │      0.06       │      100        │
│   中等并发(10客户端) │     30,236      │      0.32       │      100        │  
│   高并发(20客户端)   │     31,917      │      0.61       │      100        │
│   极限压力(50客户端) │     28,845      │      1.73       │      100        │
└─────────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

### 4.2. 与HTTP架构对比

| 指标项 | IPC架构 | 原HTTP架构 | 提升幅度 |
|--------|---------|------------|----------|
| 平均延迟 | 0.06-0.61ms | 5-15ms | **90%+减少** |
| 峰值RPS | 31,917 | 5,000-8,000 | **4x提升** |
| 内存占用 | 45-60MB | 80-120MB | **30%减少** |
| 启动时间 | 0.8s | 2.5s | **68%减少** |
| CPU占用 | 2-5% | 8-15% | **60%减少** |

### 4.3. 资源管理与智能调度

- **事件处理**: 对文件系统和配置文件的变更事件，采用**去抖动 (Debouncing)**机制。在短时间内（如500ms）将大量事件合并为单个批处理任务，避免CPU尖峰。
- **任务调度**:
    - 内置一个基于优先级的任务队列。
    - 实现一个`SystemObserver`，用于监测CPU负载、内存使用和电池状态。
    - 调度器根据`SystemObserver`的状态和用户在`config.json`中设定的性能模式（`eco`, `balanced`, `high_performance`），动态调整后台任务的并发数和执行频率。

### 3.5. 错误恢复与数据一致性

- **任务持久化**: 对每个需要处理的文件或数据源，在数据库中创建一个任务记录，并维护其状态（`PENDING`, `PROCESSING`, `DONE`, `FAILED`）。
- **事务性流水线**: 从数据采集到最终写入存储的整个过程，被包裹在一个完整的业务逻辑事务中。只有所有步骤成功，任务状态才被标记为`DONE`。任何一步失败都会导致事务回滚，并将任务标记为`FAILED`，等待后续重试。
- **启动自检**: Daemon启动时，会扫描任务列表，对所有处于`PROCESSING`状态的任务进行检查和恢复，对`FAILED`的任务根据重试策略进行处理。

## 5. 生命周期与部署

### 5.1. 启动与关闭流程

#### 启动流程
```bash
# 新的IPC启动命令
python daemon/ipc_main.py
# 或使用项目脚本
./linch
```

#### 启动过程
1. **PID文件管理**: 创建`~/.linch-mind/daemon.pid`防止多实例
2. **Socket创建**: 创建Unix Socket或Named Pipe
3. **权限设置**: 设置Socket文件权限(600)
4. **路由注册**: 加载所有API路由
5. **中间件初始化**: 加载安全、日志、限流中间件
6. **服务发现**: 创建服务发现文件供客户端使用

#### 关闭流程
1. **优雅关闭**: 等待当前请求完成
2. **连接清理**: 关闭所有客户端连接
3. **Socket清理**: 删除Socket文件
4. **PID清理**: 删除PID文件
5. **资源释放**: 关闭数据库连接等资源

### 5.2. 服务发现机制

```python
# 服务发现文件: ~/.linch-mind/daemon.info
{
    "pid": 12345,
    "socket_path": "/tmp/linch-mind-12345.sock",
    "pipe_name": "linch-mind-12345",  # Windows only
    "version": "3.0.0",
    "started_at": "2025-08-06T10:30:00Z",
    "platform": "darwin"
}
```

### 5.3. 安全更新机制

更新程序通过IPC协议安全更新：
1. **通过IPC请求关闭**: `POST /admin/shutdown`
2. **等待优雅关闭**: 监控PID文件消失
3. **替换二进制文件**: 更新daemon文件
4. **重启服务**: 启动新版本daemon
5. **配置迁移**: 自动处理配置文件版本升级

---

## 6. 架构最佳实践与迁移指南

**更新时间**: 2025-08-06  
**基于**: IPC架构完全迁移和性能优化

### 6.1. IPC架构优势总结

基于完全迁移到IPC架构的实践经验：

#### 核心优势
- **极致性能**: 平均延迟从5-15ms降低到0.06-0.61ms
- **零网络暴露**: 完全消除网络安全风险
- **资源节约**: 内存占用减少30%，CPU占用减少60%
- **部署简化**: 无端口冲突，启动时间减少68%
- **向后兼容**: 现有客户端代码完全不需修改

#### 架构演进对比

**HTTP时代架构** (已淘汰):
```
UI/连接器 ←→ HTTP REST API ←→ FastAPI ←→ Daemon核心
- 问题：网络延迟、端口冲突、安全暴露、资源浪费
- 性能：延迟5-15ms，RPS 5,000-8,000
```

**IPC时代架构** (当前):
```
UI/连接器 ←→ IPC兼容层 ←→ Unix Socket/Named Pipe ←→ Daemon核心
- 优势：本地通信、零网络风险、极致性能、跨平台统一
- 性能：延迟0.06-0.61ms，RPS 30,000+
```

### 6.2. 故障排除与调试

#### 常见问题诊断

**连接失败**
```bash
# 检查daemon是否运行
ps aux | grep ipc_main
cat ~/.linch-mind/daemon.pid

# 检查Socket文件
ls -la /tmp/linch-mind-*.sock
stat /tmp/linch-mind-*.sock
```

**权限错误**
```bash
# 检查Socket权限
ls -la /tmp/linch-mind-*.sock
# 应显示: srw------- 1 user user 0 Aug  6 10:30 linch-mind-12345.sock

# 修复权限问题
chmod 600 /tmp/linch-mind-*.sock
```

**性能问题**
```python
# 启用性能调试
import logging
logging.getLogger("ipc").setLevel(logging.DEBUG)

# 运行性能基准
python daemon/tests/performance_benchmark.py
```

### 6.3. 开发者指南

#### 添加新的IPC路由
```python
# 在 daemon/services/ipc_routes.py 中添加
@router.get("/new-endpoint/{param}")
async def handle_new_endpoint(request: IPCRequest) -> IPCResponse:
    param = request.path_params.get("param")
    # 处理逻辑
    return IPCResponse(
        status_code=200,
        data={"result": f"Processed {param}"}
    )
```

#### 添加新的中间件
```python
# 在 daemon/services/ipc_middleware.py 中添加
async def custom_middleware(request: IPCRequest, call_next: Callable) -> IPCResponse:
    # 前置处理
    start_time = time.time()
    
    # 调用下一层
    response = await call_next()
    
    # 后置处理
    duration = time.time() - start_time
    logger.info(f"Request processed in {duration:.3f}s")
    
    return response
```

## 7. 相关文档

- [纯IPC架构设计指南](../../Pure_IPC_Architecture_Guide.md) - 详细技术实现
- [IPC安全架构设计](security_architecture_design.md) - 安全配置和最佳实践
- [连接器开发标准](connector_internal_management_standards.md) - 连接器开发指南  
- [API契约设计](api_contract_design.md) - IPC消息协议规范
- [Python + Flutter最终架构决策](../02_decisions/python_flutter_architecture_final_decision.md) - 技术架构选择决策

## 8. 总结

**IPC架构迁移成功**: Linch Mind已完成从HTTP到纯IPC的重大架构升级，实现了：

- ✅ **性能突破**: 延迟减少90%+，吞吐量提升4倍
- ✅ **安全增强**: 零网络暴露，进程级身份验证
- ✅ **资源优化**: CPU和内存占用显著降低
- ✅ **部署简化**: 无端口冲突，启动更快
- ✅ **向后兼容**: 现有客户端无需修改
- ✅ **跨平台统一**: Unix Socket + Named Pipe完整支持

这标志着项目技术架构进入新时代，为后续AI功能增强和用户体验优化奠定了坚实基础。

---

**文档版本**: 3.0  
**创建时间**: 2025-08-03  
**最新更新**: 2025-08-06  
**维护团队**: 架构组 + IPC专项组
