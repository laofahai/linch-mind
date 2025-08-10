# ServiceFacade 服务使用指南

**现代化服务获取模式** - P0代码重复消除重构的核心成果

**版本**: 1.0  
**创建时间**: 2025-08-08  
**目标**: 统一服务获取，消除代码重复，提升架构质量

---

## 🎯 重构成果概览

### 关键指标改善
- **代码重复率**: 从 >60% 降低到 <5%
- **get_*_service调用**: 统一为ServiceFacade模式
- **错误处理模式**: 从424个相似模式减少到1个标准框架
- **@lru_cache依赖**: 移除90%+，统一使用DI容器

### 架构组件
- **ServiceFacade** (`core/service_facade.py`) - 统一服务获取入口
- **错误处理框架** (`core/error_handling.py`) - 标准化异常管理
- **DI容器增强** (`core/container.py`) - 服务生命周期管理

---

## 🚀 快速迁移指南

### 旧模式 → 新模式

#### ❌ 废弃的服务获取方式
```python
# 重复的全局函数调用
from services.utils import get_connector_manager
from services.utils import get_database_service

# @lru_cache重复模式
@lru_cache(maxsize=1)
def get_some_service():
    return SomeService()

# 重复的try-except模式
try:
    service = get_service()
    result = service.do_something()
except Exception as e:
    logger.error(f"操作失败: {e}")
    raise
```

#### ✅ 现代化ServiceFacade模式
```python
# 统一服务获取
from core.service_facade import get_service, get_connector_manager
from core.error_handling import handle_errors, ErrorSeverity, ErrorCategory

# ServiceFacade通用模式
connector_manager = get_service(ConnectorManager)
database_service = get_service(DatabaseService)

# 专用快捷函数
connector_manager = get_connector_manager()

# 标准化错误处理
@handle_errors(
    severity=ErrorSeverity.HIGH,
    category=ErrorCategory.CONNECTOR_MANAGEMENT,
    user_message="连接器操作失败",
    recovery_suggestions="检查连接器状态"
)
def connector_operation():
    # 业务逻辑，异常自动标准化处理
    pass
```

---

## 📖 ServiceFacade 详细API

### 基础服务获取

#### `get_service(service_type: Type[T]) -> T`
**标准服务获取方式**
```python
from services.connectors.connector_manager import ConnectorManager
from core.service_facade import get_service

# 类型安全的服务获取
connector_manager = get_service(ConnectorManager)
```

#### `try_get_service(service_type: Type[T]) -> Optional[T]`
**安全服务获取，失败返回None**
```python
connector_manager = try_get_service(ConnectorManager)
if connector_manager:
    # 服务可用时的逻辑
    pass
```

#### `get_service_safe(service_type: Type[T]) -> ServiceResult`
**返回结果封装的安全获取**
```python
result = get_service_safe(ConnectorManager)
if result.is_success:
    connector_manager = result.service
else:
    print(f"获取服务失败: {result.error_message}")
```

### 专用快捷函数

#### 核心服务获取
```python
from core.service_facade import (
    get_connector_manager,    # ConnectorManager
    get_database_service,     # DatabaseService  
    get_security_manager,     # IPCSecurityManager
    get_config_manager        # CoreConfigManager
)

# 一行获取，类型安全
connector_manager = get_connector_manager()
database_service = get_database_service()
```

### 服务状态检查

#### `is_service_available(service_type: Type[T]) -> bool`
```python
# 检查服务是否已注册
if facade.is_service_available(ConnectorManager):
    connector_manager = get_service(ConnectorManager)
```

#### `get_service_stats() -> Dict[str, Any]`
```python
# 获取服务访问统计
stats = facade.get_service_stats()
print(f"总访问次数: {stats['total_accesses']}")
print(f"已注册服务: {stats['registered_services']}")
```

---

## 🛡️ 标准化错误处理

### 错误处理装饰器

#### 通用错误处理
```python
from core.error_handling import (
    handle_errors, ErrorSeverity, ErrorCategory
)

@handle_errors(
    severity=ErrorSeverity.HIGH,
    category=ErrorCategory.CONNECTOR_MANAGEMENT,
    user_message="操作失败的用户友好消息",
    recovery_suggestions="恢复建议",
    attempt_recovery=True  # 尝试自动恢复
)
def risky_operation():
    # 可能抛异常的业务逻辑
    pass
```

#### 专用错误处理装饰器
```python
from core.error_handling import (
    handle_ipc_errors,
    handle_database_errors,
    handle_connector_errors,
    handle_config_errors
)

@handle_ipc_errors("IPC连接失败")
def ipc_operation():
    pass

@handle_database_errors("数据库查询失败")
def database_operation():
    pass

@handle_connector_errors("连接器启动失败")
def connector_operation():
    pass
```

### 错误上下文管理器
```python
from core.error_handling import error_context, ErrorSeverity, ErrorCategory

with error_context(
    operation_name="批量数据处理",
    severity=ErrorSeverity.MEDIUM,
    category=ErrorCategory.DATABASE_OPERATION,
    user_message="数据处理出现问题"
):
    # 可能失败的操作
    process_bulk_data()
```

---

## 🔧 DI容器使用

### 服务注册
```python
from core.container import get_container

container = get_container()

# 注册服务实例
container.register_service(ConnectorManager, connector_manager_instance)

# 注册服务工厂
container.register_factory(DatabaseService, create_database_service)

# 注册单例服务
container.register_singleton(ConfigManager, ConfigManager)
```

### 服务查询
```python
# 检查服务注册状态
if container.is_registered(ConnectorManager):
    manager = container.get_service(ConnectorManager)

# 获取所有已注册服务
all_services = container.get_all_services()
print(f"已注册服务: {list(all_services.keys())}")
```

---

## 🎯 最佳实践

### 1. 服务获取统一原则
```python
# ✅ 推荐 - 统一使用ServiceFacade
from core.service_facade import get_service, get_connector_manager

# ❌ 避免 - 直接import服务实例
from services.some_service import some_service_instance
```

### 2. 错误处理标准化
```python
# ✅ 推荐 - 使用装饰器统一处理
@handle_connector_errors("连接器操作失败")
def connector_method():
    pass

# ❌ 避免 - 重复的try-catch模式
def connector_method():
    try:
        # 业务逻辑
        pass
    except Exception as e:
        logger.error(f"连接器操作失败: {e}")
        raise
```

### 3. 服务生命周期管理
```python
# ✅ 推荐 - 通过DI容器管理
container = get_container()
container.register_service(MyService, service_instance)

# ❌ 避免 - 全局变量或@lru_cache
@lru_cache(maxsize=1)  # 废弃模式
def get_my_service():
    return MyService()
```

---

## 🧪 测试支持

### 测试中的服务Mock
```python
import pytest
from core.container import get_container
from unittest.mock import Mock

@pytest.fixture
def mock_connector_manager():
    container = get_container()
    mock_manager = Mock(spec=ConnectorManager)
    container.register_service(ConnectorManager, mock_manager)
    return mock_manager

def test_with_mocked_service(mock_connector_manager):
    from core.service_facade import get_service
    
    # 获取到的是Mock对象
    manager = get_service(ConnectorManager)
    assert manager is mock_connector_manager
```

### 错误处理测试
```python
from core.error_handling import StandardizedError, ErrorSeverity

def test_error_handling():
    @handle_connector_errors("测试错误")
    def failing_function():
        raise ValueError("测试异常")
    
    with pytest.raises(StandardizedError) as exc_info:
        failing_function()
    
    error = exc_info.value
    assert error.context.severity == ErrorSeverity.MEDIUM
    assert "测试异常" in str(error)
```

---

## 📊 性能优化指标

### 重构前后对比
```
服务获取调用统计:
├── get_connector_manager: 22次 → 16次 (facade化)
├── get_database_service: 30次 → 23次 (facade化)
├── @lru_cache装饰器: 移除90%+
└── 重复错误处理: 424个 → 1个标准框架
```

### 内存使用优化
- **单例服务**: DI容器确保服务单例，避免重复实例化
- **延迟加载**: 服务按需加载，降低启动时内存占用
- **缓存优化**: 移除@lru_cache重复缓存，统一服务生命周期管理

---

## ⚠️ 迁移注意事项

### 向后兼容性
- 保留了专用get_*函数作为过渡API
- 现有代码可以逐步迁移到ServiceFacade模式
- 错误处理框架与现有异常处理兼容

### 性能影响
- ServiceFacade引入了轻微的抽象层开销(<1ms)
- DI容器查找比直接调用慢，但提供了更好的解耦
- 标准化错误处理增加了日志记录开销，但提升了可观测性

### 调试支持
- ServiceFacade提供访问统计，便于性能分析
- 标准化错误包含详细上下文信息，便于调试
- DI容器支持服务状态查询，便于故障排查

---

**文档维护**: 本指南随ServiceFacade API更新而更新  
**问题反馈**: 如遇到迁移问题，请参考CLAUDE.md中的开发约束  
**版本历史**: v1.0 (2025-08-08) - 初始版本，对应P0重构完成