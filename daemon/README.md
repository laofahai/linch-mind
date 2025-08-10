# Linch Mind Daemon

**高性能IPC后台服务** - Linch Mind个人AI生活助手的核心引擎

**版本**: 0.3.0  
**架构**: 纯IPC (Unix Socket/Named Pipe) + 现代化服务架构  
**技术栈**: Python 3.12 + SQLAlchemy + FAISS + NetworkX + ServiceFacade  
**状态**: 生产就绪 + P0重构完成

---

## 🚀 核心特性

### 🔥 纯IPC架构 (v2.0) + 现代化服务架构 (v3.0)
- **超高性能**: IPC延迟<1ms，相比HTTP提升90%+
- **零网络暴露**: Unix Socket/Named Pipe本地通信
- **自动重连**: 客户端断线自动恢复机制
- **跨平台支持**: macOS/Linux(Unix Socket) + Windows(Named Pipe)
- **ServiceFacade**: 统一服务获取，消除>90%代码重复
- **标准化错误处理**: 统一异常管理，提升系统稳定性

### 🧠 智能推荐引擎
- **知识图谱**: NetworkX图数据库，自动发现内容关联
- **向量搜索**: FAISS高性能向量索引，语义相似度匹配
- **机器学习**: scikit-learn驱动的个性化推荐算法
- **实时分析**: 基于用户行为的动态推荐更新

### 🔌 连接器生态系统
- **动态管理**: 连接器热插拔，无需重启服务
- **状态监控**: 实时监控连接器健康状态和性能
- **配置服务**: WebView配置界面，用户友好的参数设置
- **进程隔离**: 每个连接器独立进程，故障隔离

### 📊 三层存储架构
- **热数据层**: SQLite，高频访问数据，<10ms响应
- **温数据层**: 文件系统缓存，中频数据，<100ms响应
- **冷数据层**: 压缩存档，低频历史数据，<1s响应

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────┐
│         Linch Mind Daemon v3.0          │
├─────────────────────────────────────────┤
│  IPC Server (Unix Socket/Named Pipe)   │
│  ├─ 路由处理 (ipc_router.py)            │
│  ├─ 中间件 (ipc_middleware.py)          │
│  └─ 安全层 (ipc_security.py)            │
├─────────────────────────────────────────┤
│  现代化服务架构 (2025-08-08)             │
│  ├─ ServiceFacade (统一服务获取)        │
│  ├─ 标准化错误处理 (error_handling.py)  │
│  ├─ DI容器 (container.py)               │
│  └─ 异常管理 (exception_handler.py)     │
├─────────────────────────────────────────┤
│  核心业务服务                            │
│  ├─ 连接器管理 (connector_manager.py)   │
│  ├─ 推荐引擎 (cached_networkx_service)  │
│  ├─ 数据服务 (database_service.py)      │
│  └─ 存储编排 (storage_orchestrator.py)  │
├─────────────────────────────────────────┤
│  数据层                                  │
│  ├─ SQLite (结构化数据)                  │
│  ├─ FAISS (向量索引)                     │
│  └─ NetworkX (知识图谱)                  │
└─────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 环境要求
- **Python**: 3.12+
- **Poetry**: 1.4+ (依赖管理)
- **系统**: macOS/Linux/Windows

### 安装与启动

```bash
# 1. 安装依赖
poetry install

# 2. 启动IPC服务器
poetry run linch-daemon

# 或者直接运行
poetry run python ipc_main.py

# 3. 验证服务状态
./linch-mind status
```

### 配置文件
```bash
# 配置文件位置
~/.linch-mind/config.yaml

# 核心配置
ipc_socket_path: /tmp/linch-mind.sock  # Unix Socket路径
database_url: sqlite:///~/.linch-mind/linch.db
log_level: INFO
max_connections: 1000
```

---

## 📁 目录结构

```
daemon/
├── ipc_main.py              # 主入口 - IPC服务器启动
├── core/                    # 🆕 现代化核心架构 (2025-08-08)
│   ├── service_facade.py    # ServiceFacade - 统一服务获取
│   ├── error_handling.py    # 标准化错误处理框架
│   ├── container.py         # 增强DI容器
│   ├── exception_handler.py # 异常管理器
│   └── database_manager.py  # 数据库生命周期管理
├── config/                  # 配置管理
│   ├── core_config.py       # 核心配置加载
│   ├── error_handling.py    # 错误处理配置
│   └── ipc_security_config.py # IPC安全配置
├── services/                # 核心服务层
│   ├── ipc_server.py        # IPC服务器实现
│   ├── ipc_router.py        # 路由分发器
│   ├── ipc_middleware.py    # 中间件系统
│   ├── connector_manager.py # 连接器管理
│   ├── cached_networkx_service.py # 推荐引擎
│   └── storage/             # 存储服务
│       ├── storage_orchestrator.py # 存储编排
│       ├── vector_service.py    # FAISS向量服务
│       └── graph_service.py     # NetworkX图服务
├── models/                  # 数据模型
│   ├── database_models.py   # SQLAlchemy ORM模型
│   └── api_models.py        # Pydantic API模型
├── api/                     # IPC路由处理器
│   └── routers/             # 按功能分组的路由
└── tests/                   # 测试套件
    ├── test_ipc_integration.py # IPC集成测试
    └── test_storage_integration.py # 存储测试
```

---

## 🔧 开发指南

### 🆕 现代化开发模式 (2025-08-08)

#### ServiceFacade服务获取
```python
# ✅ 推荐方式 - 使用ServiceFacade
from core.service_facade import get_service, get_connector_manager

# 通用服务获取
connector_manager = get_service(ConnectorManager)
database_service = get_service(DatabaseService)

# 专用快捷函数
connector_manager = get_connector_manager()
```

#### 标准化错误处理
```python
# ✅ 统一错误处理装饰器
from core.error_handling import handle_errors, ErrorSeverity, ErrorCategory

@handle_errors(
    severity=ErrorSeverity.HIGH,
    category=ErrorCategory.CONNECTOR_MANAGEMENT,
    user_message="连接器启动失败",
    recovery_suggestions="检查连接器配置和依赖"
)
async def start_connector(connector_id: str):
    # 业务逻辑，异常会被自动捕获和标准化处理
    pass
```

#### 依赖注入容器
```python
# ✅ 服务注册
from core.container import get_container

container = get_container()
container.register_service(ConnectorManager, connector_manager_instance)

# ✅ 服务检查
if container.is_registered(DatabaseService):
    db_service = container.get_service(DatabaseService)
```

### IPC通信测试
```bash
# Python客户端测试
poetry run python tests/ipc_test_client.py

# 手动IPC测试 (Unix Socket)
echo '{"method":"GET","path":"/health"}' | nc -U /tmp/linch-mind.sock
```

### 性能基准测试
```bash
# 运行完整测试套件
poetry run pytest tests/

# 性能基准测试
poetry run pytest tests/test_ipc_integration.py -v
```

### 开发者工具
```bash
# 代码格式化
poetry run black .
poetry run isort .

# 代码质量检查
poetry run flake8
poetry run pytest --cov=. --cov-report=html
```

---

## 🔌 连接器开发

### 注册新连接器
```python
from services.connector_manager import register_connector

# 注册连接器配置
config = {
    "id": "my_connector",
    "name": "My Custom Connector", 
    "type": "data_source",
    "executable_path": "/path/to/connector",
    "config_schema": {...}
}

register_connector(config)
```

### 连接器API
- **启动**: `POST /connectors/{id}/start`
- **停止**: `POST /connectors/{id}/stop` 
- **状态**: `GET /connectors/{id}/status`
- **配置**: `PUT /connectors/{id}/config`

---

## 📊 监控与调试

### 日志系统
```python
# 日志配置
import logging
logging.getLogger("ipc").setLevel(logging.DEBUG)
logging.getLogger("connector").setLevel(logging.INFO)

# 日志文件位置
~/.linch-mind/logs/daemon.log
~/.linch-mind/logs/connectors/
```

### 性能监控
```python
# 启用性能中间件
from services.ipc_middleware import PerformanceMiddleware

# 关键指标
- IPC连接建立: <5ms
- 消息处理延迟: <1ms
- 并发连接数: 1000+
- 内存使用: <500MB
```

---

## 🔒 安全特性

### IPC安全
- **权限检查**: Unix Socket文件权限控制
- **进程验证**: 客户端进程身份验证
- **消息签名**: 防止消息篡改
- **速率限制**: 防止DOS攻击

### 数据安全
- **数据库加密**: SQLCipher可选加密
- **敏感数据清理**: 自动PII数据检测和清理
- **访问审计**: 完整的数据访问日志

---

## 🚀 性能优化

### 关键优化
- **连接池**: IPC连接复用，减少建立开销
- **批量处理**: 消息批量发送，提升吞吐量  
- **内存缓存**: 热数据内存缓存，减少IO
- **异步处理**: 全异步架构，高并发支持

### 基准数据
- **IPC延迟**: 0.5ms (vs HTTP 5-15ms)
- **RPS**: 30,000+ (vs HTTP 3,000)
- **内存使用**: 400MB (vs HTTP 800MB)
- **启动时间**: 2s (vs HTTP 5s)

---

## 🔗 相关文档

- **[IPC协议规范](../docs/01_technical_design/api_contract_design.md)**: 完整IPC消息格式
- **[IPC客户端指南](../docs/01_technical_design/ipc_client_usage_guide.md)**: 客户端集成文档
- **[存储架构设计](../docs/01_technical_design/data_storage_architecture.md)**: 三层存储架构
- **[连接器开发指南](../connectors/README.md)**: 连接器SDK文档

---

**Daemon服务状态**: ✅ 生产就绪 + P0重构完成  
**版本**: 0.3.0  
**代码重构**: 重复率从>60%降至<5%，架构现代化  
**最后更新**: 2025-08-08  
**维护团队**: Linch Mind Core Team