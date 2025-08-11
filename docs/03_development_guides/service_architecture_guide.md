# 现代化服务架构使用指南

本指南详细说明Linch Mind项目的现代化服务架构使用方法，包括ServiceFacade统一服务管理、标准化错误处理框架和环境隔离系统。

## 📋 目录

- [ServiceFacade统一服务管理](#servicefacade统一服务管理)
- [标准化错误处理框架](#标准化错误处理框架)
- [环境隔离管理系统](#环境隔离管理系统)
- [DI容器增强功能](#di容器增强功能)
- [最佳实践和常见模式](#最佳实践和常见模式)

## ServiceFacade统一服务管理

### 🎯 核心价值

**问题解决**: 消除了91个重复的`get_*_service()`全局函数调用，将代码重复率从>60%降低到<5%。

### ✅ 正确使用方式

```python
# 统一服务获取facade模式
from core.service_facade import get_service, get_connector_manager, try_get_service

# 基础服务获取
connector_manager = get_service(ConnectorManager)
database_service = get_service(DatabaseService)
ipc_server = get_service(IPCServer)

# 专用快捷函数（推荐）
connector_manager = get_connector_manager()

# 安全的服务获取（不抛异常）
result = try_get_service(SomeService)
if result.is_success:
    service = result.service
else:
    logger.error(f"Service unavailable: {result.error_message}")
```

### ❌ 废弃的使用方式

```python
# 🚫 禁止 - 重复函数调用
from services.utils import get_connector_manager
from services.database_utils import get_database_service

# 🚫 禁止 - 双套依赖系统
@lru_cache(maxsize=1)
def get_some_service():
    return SomeService()
```

### 🔧 服务注册和管理

```python
# 服务注册（通常在应用启动时）
from core.container import register_service

register_service(ConnectorManager, connector_manager_instance)
register_service(DatabaseService, database_service_instance)

# 服务生命周期管理
from core.service_facade import get_container

container = get_container()
container.register_singleton(ServiceClass, lambda: ServiceClass())
```

## 标准化错误处理框架

### 🎯 核心价值

**问题解决**: 消除了424个相似错误处理模式，建立统一的异常管理和错误恢复机制。

### ✅ 装饰器模式使用

```python
from core.error_handling import handle_errors, ErrorSeverity, ErrorCategory

@handle_errors(
    severity=ErrorSeverity.HIGH,
    category=ErrorCategory.IPC_COMMUNICATION,
    user_message="连接器操作失败",
    recovery_suggestions="检查连接器状态并重试"
)
def connector_operation(connector_id: str):
    """执行连接器操作"""
    # 业务逻辑 - 任何异常都会被统一处理
    connector = get_service(ConnectorManager).get_connector(connector_id)
    return connector.execute()

@handle_errors(
    severity=ErrorSeverity.CRITICAL,
    category=ErrorCategory.DATABASE_OPERATION,
    user_message="数据库操作失败",
    recovery_suggestions="检查数据库连接和权限"
)
async def async_database_operation():
    """异步数据库操作"""
    database = get_service(DatabaseService)
    async with database.transaction() as tx:
        return await tx.execute_query("SELECT * FROM data")
```

### 🔧 上下文管理器模式

```python
from core.error_handling import error_context

def complex_operation():
    with error_context(
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.FILE_SYSTEM,
        user_message="文件处理操作失败"
    ):
        # 任何在此上下文中的异常都会被统一处理
        process_files()
        update_database()
```

### 📊 错误分类和严重性

```python
# 错误严重性级别
ErrorSeverity.LOW        # 可忽略错误，记录日志
ErrorSeverity.MEDIUM     # 需要注意，发送通知
ErrorSeverity.HIGH       # 严重错误，需要立即处理
ErrorSeverity.CRITICAL   # 致命错误，可能影响系统稳定性

# 错误分类
ErrorCategory.IPC_COMMUNICATION      # IPC通信错误
ErrorCategory.DATABASE_OPERATION     # 数据库操作错误
ErrorCategory.CONNECTOR_MANAGEMENT   # 连接器管理错误
ErrorCategory.FILE_SYSTEM           # 文件系统错误
ErrorCategory.CONFIGURATION         # 配置错误
ErrorCategory.SECURITY              # 安全相关错误
```

## 环境隔离管理系统

### 🎯 核心价值

**问题解决**: 提供完整的环境隔离，支持development/staging/production环境独立管理。

### ✅ 环境管理器使用

```python
from core.environment_manager import EnvironmentManager

# 获取当前环境管理器
env_manager = EnvironmentManager()

# 环境信息
print(f"当前环境: {env_manager.current_env}")
print(f"环境目录: {env_manager.env_dir}")
print(f"数据库路径: {env_manager.get_database_path()}")
print(f"日志路径: {env_manager.get_log_path()}")

# 环境配置
config = env_manager.get_config()
print(f"数据库URL: {config.database.url}")
```

### 🏗️ 环境目录结构

```
~/.linch-mind/
├── development/          # 开发环境
│   ├── database/        # 数据库文件
│   ├── logs/           # 日志文件
│   ├── cache/          # 缓存文件
│   └── config/         # 环境专用配置
├── staging/             # 预发环境
└── production/          # 生产环境（SQLCipher加密）
```

### 🔐 生产环境安全

```python
# 生产环境自动启用SQLCipher加密
if env_manager.is_production:
    database_url = env_manager.get_encrypted_database_url()
    # 自动使用加密数据库连接
```

## DI容器增强功能

### 🎯 核心价值

**问题解决**: 统一依赖注入管理，移除@lru_cache双套系统，提供更灵活的服务生命周期管理。

### ✅ 容器使用模式

```python
from core.container import get_container, register_service

# 获取容器实例
container = get_container()

# 单例注册
container.register_singleton(ServiceClass, lambda: ServiceClass())

# 工厂注册（每次调用创建新实例）
container.register_factory(TransientService, lambda: TransientService())

# 实例注册
container.register_instance(ConfigService, config_instance)

# 服务获取
service = container.get(ServiceClass)
```

## 最佳实践和常见模式

### 🏗️ 服务层设计模式

```python
from core.service_facade import get_service
from core.error_handling import handle_errors, ErrorSeverity, ErrorCategory

class ConnectorService:
    """连接器业务服务层"""

    def __init__(self):
        # 使用ServiceFacade获取依赖
        self.connector_manager = get_service(ConnectorManager)
        self.database = get_service(DatabaseService)

    @handle_errors(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.CONNECTOR_MANAGEMENT,
        user_message="连接器启动失败"
    )
    def start_connector(self, connector_id: str):
        """启动连接器的统一入口"""
        connector = self.connector_manager.get_connector(connector_id)

        # 更新数据库状态
        self.database.update_connector_status(connector_id, "starting")

        # 启动连接器
        result = connector.start()

        # 记录结果
        self.database.update_connector_status(
            connector_id,
            "running" if result.success else "failed"
        )

        return result
```

### 🔄 异步操作模式

```python
from core.error_handling import handle_errors, ErrorSeverity, ErrorCategory
import asyncio

class AsyncDataProcessor:
    """异步数据处理服务"""

    @handle_errors(
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.DATABASE_OPERATION,
        user_message="数据处理失败"
    )
    async def process_data_batch(self, data_items: list):
        """批量处理数据"""
        database = get_service(DatabaseService)

        async with database.transaction() as tx:
            tasks = []
            for item in data_items:
                task = self._process_single_item(tx, item)
                tasks.append(task)

            return await asyncio.gather(*tasks, return_exceptions=True)

    async def _process_single_item(self, tx, item):
        """处理单个数据项"""
        # 具体处理逻辑
        return await tx.execute_query("INSERT INTO ...", item)
```

### 🧪 测试支持模式

```python
import pytest
from unittest.mock import Mock
from core.container import get_container

@pytest.fixture
def mock_services():
    """测试用的模拟服务"""
    container = get_container()

    # 注册模拟服务
    mock_db = Mock()
    mock_connector = Mock()

    container.register_instance(DatabaseService, mock_db)
    container.register_instance(ConnectorManager, mock_connector)

    yield {
        'database': mock_db,
        'connector_manager': mock_connector
    }

    # 清理
    container.clear()

def test_service_operation(mock_services):
    """测试服务操作"""
    from core.service_facade import get_service

    # 使用模拟服务进行测试
    service = MyService()
    result = service.some_operation()

    # 验证模拟服务被正确调用
    mock_services['database'].update.assert_called_once()
```

## ⚠️ 迁移指南

### 从旧模式迁移到新架构

```python
# 🔄 迁移前（旧模式）
from services.utils import get_connector_manager
from functools import lru_cache

@lru_cache(maxsize=1)
def get_my_service():
    return MyService(get_connector_manager())

def some_function():
    try:
        service = get_my_service()
        return service.do_something()
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

# ✅ 迁移后（新架构）
from core.service_facade import get_service
from core.error_handling import handle_errors, ErrorSeverity, ErrorCategory

@handle_errors(
    severity=ErrorSeverity.MEDIUM,
    category=ErrorCategory.CONNECTOR_MANAGEMENT,
    user_message="操作失败"
)
def some_function():
    service = get_service(MyService)
    return service.do_something()
```

## 📈 性能和监控

### 服务性能监控

```python
from core.service_facade import get_service_metrics

# 获取服务使用统计
metrics = get_service_metrics()
print(f"服务调用次数: {metrics.total_calls}")
print(f"平均响应时间: {metrics.avg_response_time}ms")
print(f"错误率: {metrics.error_rate}%")
```

### 错误处理统计

```python
from core.error_handling import get_error_statistics

# 获取错误处理统计
stats = get_error_statistics()
print(f"总错误数: {stats.total_errors}")
print(f"按严重性分组: {stats.by_severity}")
print(f"按分类分组: {stats.by_category}")
```

---

*该架构指南涵盖了Linch Mind项目现代化服务架构的所有核心组件和使用模式，确保开发过程中严格遵循架构铁律和最佳实践。*
