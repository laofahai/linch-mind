# Daemon 测试套件

## 📋 测试概览

本测试套件为 Linch Mind Daemon 提供全面的测试覆盖，确保代码质量和系统稳定性。

### 🎯 测试目标
- **覆盖率目标**: >80%
- **测试类型**: 单元测试 + 集成测试
- **测试框架**: pytest + asyncio support

## 📁 测试结构

```
tests/
├── conftest.py                    # pytest配置和共享fixtures
├── test_config_system.py          # ✅ 配置系统测试 (已存在)
├── test_connector_lifecycle_api.py # ✅ 连接器生命周期API测试
├── test_connector_config_api.py   # ✅ 连接器配置API测试  
├── test_connector_ui_api.py       # ✅ 连接器UI API测试
├── test_database_service.py       # ✅ 数据库服务测试
├── test_connector_manager.py      # ✅ 连接器管理器测试
└── test_process_manager.py        # ✅ 进程管理器测试
```

## 🧪 测试覆盖范围

### API 层测试
- **connector_lifecycle_api**: 连接器发现、启动、停止、重启、删除
- **connector_config_api**: 配置schema、验证、更新、历史记录
- **connector_ui_api**: 自定义UI组件、静态文件服务、动作执行

### 服务层测试  
- **database_service**: CRUD操作、事务管理、连接处理
- **connector_manager**: 连接器注册、进程管理、健康检查
- **process_manager**: 进程启动/停止、资源监控、系统统计

### 核心功能测试
- **配置系统**: YAML加载、环境变量、验证、热重载
- **数据模型**: SQLAlchemy ORM、JSON字段、时间戳、约束
- **错误处理**: 异常捕获、优雅降级、错误响应

## 🚀 运行测试

### 基本测试运行
```bash
# 运行所有测试
poetry run python -m pytest tests/ -v

# 运行特定测试文件
poetry run python -m pytest tests/test_connector_lifecycle_api.py -v

# 运行特定测试方法
poetry run python -m pytest tests/test_database_service.py::TestDatabaseService::test_connector_crud_operations -v
```

### 覆盖率测试
```bash
# 生成覆盖率报告
poetry run python -m pytest tests/ --cov=. --cov-report=html

# 查看HTML报告
open htmlcov/index.html
```

### 使用测试运行器
```bash
# 运行完整测试套件（推荐）
poetry run python run_tests.py
```

## 🏷️ 测试标记

使用pytest标记来分类和过滤测试：

```bash
# 只运行API测试
poetry run python -m pytest -m api

# 只运行数据库测试  
poetry run python -m pytest -m database

# 只运行连接器测试
poetry run python -m pytest -m connector

# 跳过慢速测试
poetry run python -m pytest -m "not slow"
```

## 🔧 Mock 策略

### 外部依赖Mock
- **数据库**: 使用内存SQLite进行隔离测试
- **进程管理**: Mock psutil和subprocess调用
- **文件系统**: 使用临时目录和Mock Path操作
- **网络请求**: Mock HTTP客户端和API调用

### 共享Fixtures
- `temp_dir`: 临时目录用于文件操作测试
- `mock_database_service`: 模拟数据库服务
- `mock_connector_manager`: 模拟连接器管理器
- `mock_process_manager`: 模拟进程管理器
- `client`: FastAPI测试客户端

## 📊 质量指标

### 当前状态
- ✅ **语法检查**: 所有测试文件通过语法检查
- ✅ **框架配置**: pytest, pytest-asyncio, pytest-cov 已配置
- ✅ **Mock基础设施**: 完整的mock和fixture体系
- ✅ **测试隔离**: 数据库和文件系统隔离

### 预期指标
- **代码覆盖率**: >80% (目标)
- **测试数量**: 100+ 测试用例
- **API覆盖**: 100% 端点覆盖
- **错误场景**: 边界条件和异常处理测试

## 🐛 调试指南

### 常见问题

1. **依赖导入错误**
   ```bash
   # 确保在虚拟环境中
   poetry shell
   poetry install
   ```

2. **数据库测试失败**
   ```bash
   # 检查SQLAlchemy版本兼容性
   poetry show sqlalchemy
   ```

3. **异步测试问题**
   ```bash
   # 确保使用正确的asyncio标记
   @pytest.mark.asyncio
   async def test_async_function():
   ```

### 调试技巧
```bash
# 详细输出和调试信息
poetry run python -m pytest tests/ -vvv --tb=long

# 停在第一个失败的测试
poetry run python -m pytest tests/ -x

# 运行最后失败的测试
poetry run python -m pytest tests/ --lf
```

## 🔄 持续集成

推荐的CI/CD测试流程：

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    poetry install
    poetry run python run_tests.py
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## 📈 测试最佳实践

1. **测试命名**: 使用描述性的测试方法名
2. **测试隔离**: 每个测试独立，无依赖关系  
3. **Mock使用**: 合理使用mock，避免过度mock
4. **边界测试**: 测试边界条件和异常情况
5. **文档同步**: 测试与代码文档保持同步

## 🎯 下一步计划

- [ ] 添加压力测试和性能基准测试
- [ ] 集成测试自动化到CI/CD流程
- [ ] 添加mutation testing以提高测试质量
- [ ] 实现测试数据工厂模式
- [ ] 添加API契约测试 (OpenAPI schema validation)