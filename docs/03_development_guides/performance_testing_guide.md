# 性能基准与测试指南

本指南详细说明Linch Mind项目的性能基准测试、质量控制和持续集成测试流程。

## 📋 目录

- [性能基准要求](#性能基准要求)
- [测试框架和工具](#测试框架和工具)
- [运行测试指南](#运行测试指南)
- [性能基准测试](#性能基准测试)
- [代码覆盖率要求](#代码覆盖率要求)
- [CI/CD集成](#cicd集成)

## 性能基准要求

### 🎯 核心性能指标

根据项目的技术铁律，以下是必须满足的性能基准：

#### IPC通信性能
- **延迟要求**: < 5ms (平均响应时间)
- **吞吐量要求**: > 10,000 RPS
- **并发连接**: 支持 > 1000 并发客户端
- **内存使用**: IPC服务器 < 50MB 峰值内存

#### 应用启动性能
- **冷启动时间**: < 3 秒（从命令执行到服务就绪）
- **热启动时间**: < 1 秒（daemon已运行，启动UI）
- **环境初始化**: < 5 秒（首次环境设置）

#### 内存使用限制
- **Daemon峰值内存**: < 500MB
- **UI峰值内存**: < 200MB
- **连接器内存**: < 50MB per connector

#### 数据库性能
- **SQLite查询**: < 10ms（简单查询）
- **批量插入**: > 1000 records/s
- **FAISS向量搜索**: < 50ms（10k向量）
- **NetworkX图查询**: < 100ms（1k节点）

## 测试框架和工具

### 🔧 Python测试栈

```bash
# 主要测试工具
pytest ^8.0.0              # 测试框架
pytest-asyncio ^0.24.0     # 异步测试支持
pytest-cov ^6.0.0          # 代码覆盖率
pytest-mock ^3.14.0        # Mock支持
pytest-xdist ^3.6.0        # 并行测试

# 性能测试
pytest-benchmark            # 性能基准测试
memory-profiler            # 内存使用分析
```

### 📁 测试目录结构

```
daemon/tests/
├── conftest.py                          # 测试配置和固件
├── conftest_ipc.py                      # IPC测试专用配置
├── test_architecture_performance.py     # 架构性能测试
├── test_core_components.py              # 核心组件测试
├── test_ipc_integration.py              # IPC集成测试
├── test_ipc_integration_comprehensive.py # 全面IPC测试
├── test_database_service_effective.py   # 数据库服务测试
├── test_connector_manager_effective.py  # 连接器管理测试
├── test_storage_integration.py          # 存储集成测试
└── ipc_test_client.py                   # IPC测试客户端
```

### ⚙️ 测试配置（pytest.ini）

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# 测试选项
addopts = -v --tb=short --strict-markers --asyncio-mode=auto --cov=core --cov=services/ipc --cov-report=term-missing --cov-fail-under=80

# 测试标记
markers =
    unit: 单元测试
    integration: 集成测试
    slow: 运行缓慢的测试
    performance: 性能测试
    database: 数据库相关测试
    connector: 连接器相关测试
```

## 运行测试指南

### 🚀 基础测试命令

```bash
# 进入daemon目录
cd daemon

# 运行所有测试
poetry run pytest

# 运行特定类型的测试
poetry run pytest -m unit          # 单元测试
poetry run pytest -m integration   # 集成测试
poetry run pytest -m performance   # 性能测试

# 运行特定测试文件
poetry run pytest tests/test_core_components.py

# 运行并行测试（加速）
poetry run pytest -n auto

# 详细输出
poetry run pytest -v -s
```

### 📊 代码覆盖率测试

```bash
# 生成覆盖率报告
poetry run pytest --cov=core --cov=services --cov-report=html

# 查看详细覆盖率
poetry run pytest --cov=core --cov-report=term-missing

# 设置覆盖率失败阈值
poetry run pytest --cov-fail-under=80
```

### ⚡ 性能基准测试

```bash
# 运行架构性能测试
poetry run pytest tests/test_architecture_performance.py -v

# 运行IPC性能测试
poetry run pytest tests/test_ipc_integration_comprehensive.py::test_ipc_performance -v

# 运行内存使用测试
poetry run pytest tests/test_architecture_performance.py::test_memory_usage -v

# 使用基准测试工具
poetry run pytest --benchmark-only tests/
```

## 性能基准测试

### 🔥 IPC性能测试

```python
# 示例：IPC延迟测试
@pytest.mark.performance
async def test_ipc_latency():
    """测试IPC响应延迟"""
    client = IPCTestClient()

    # 预热
    for _ in range(10):
        await client.send_request("ping", {})

    # 测量延迟
    latencies = []
    for _ in range(1000):
        start_time = time.perf_counter()
        response = await client.send_request("ping", {})
        end_time = time.perf_counter()

        latency_ms = (end_time - start_time) * 1000
        latencies.append(latency_ms)

    # 验证性能指标
    avg_latency = statistics.mean(latencies)
    p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

    assert avg_latency < 5.0, f"平均延迟 {avg_latency:.2f}ms 超过 5ms 要求"
    assert p95_latency < 10.0, f"P95延迟 {p95_latency:.2f}ms 超过 10ms 要求"
```

### 📈 吞吐量测试

```python
@pytest.mark.performance
async def test_ipc_throughput():
    """测试IPC吞吐量"""
    client = IPCTestClient()

    # 并发连接数
    concurrent_clients = 100
    requests_per_client = 100

    async def client_worker():
        responses = []
        for _ in range(requests_per_client):
            response = await client.send_request("echo", {"data": "test"})
            responses.append(response)
        return responses

    # 测量吞吐量
    start_time = time.perf_counter()

    tasks = [client_worker() for _ in range(concurrent_clients)]
    results = await asyncio.gather(*tasks)

    end_time = time.perf_counter()

    total_requests = concurrent_clients * requests_per_client
    duration = end_time - start_time
    rps = total_requests / duration

    assert rps > 10000, f"吞吐量 {rps:.0f} RPS 低于 10,000 RPS 要求"
```

### 💾 内存使用测试

```python
@pytest.mark.performance
def test_memory_usage():
    """测试内存使用限制"""
    import psutil
    import os

    process = psutil.Process(os.getpid())

    # 基础内存使用
    baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

    # 执行典型操作
    service_container = get_container()
    database_service = service_container.get(DatabaseService)

    # 执行一些数据库操作
    for _ in range(1000):
        database_service.get_all_connectors()

    # 测量内存增长
    current_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_growth = current_memory - baseline_memory

    assert current_memory < 500, f"内存使用 {current_memory:.1f}MB 超过 500MB 限制"
    assert memory_growth < 50, f"内存增长 {memory_growth:.1f}MB 过大"
```

## 代码覆盖率要求

### 📊 覆盖率目标

- **核心模块**: ≥ 90% (core/*)
- **服务层**: ≥ 85% (services/*)
- **IPC组件**: ≥ 95% (services/ipc/*)
- **整体项目**: ≥ 80%

### 🎯 覆盖率分析

```bash
# 生成HTML覆盖率报告
poetry run pytest --cov=core --cov=services --cov-report=html

# 查看具体文件覆盖情况
poetry run pytest --cov=core --cov-report=term-missing

# 覆盖率配置示例
[coverage:run]
source = .
omit =
    */tests/*
    */test_*
    */__pycache__/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## CI/CD集成

### 🔄 自动化测试流程

```bash
#!/bin/bash
# scripts/run_tests.sh

set -e

echo "🧪 运行Linch Mind测试套件"

# 环境检查
echo "📋 检查测试环境..."
poetry install --only=dev

# 代码质量检查
echo "🔍 代码质量检查..."
poetry run black --check .
poetry run isort --check .
poetry run flake8 .
poetry run mypy .

# 安全扫描
echo "🛡️ 安全扫描..."
poetry run bandit -r . --exclude ./tests
poetry run safety check

# 单元测试
echo "🏃 运行单元测试..."
poetry run pytest tests/ -m "unit" --cov=core --cov=services --cov-fail-under=80

# 集成测试
echo "🔗 运行集成测试..."
poetry run pytest tests/ -m "integration" -v

# 性能测试
echo "⚡ 运行性能基准测试..."
poetry run pytest tests/ -m "performance" --benchmark-only

echo "✅ 所有测试通过"
```

### 🎛️ GitHub Actions配置

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.13]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install Poetry
      uses: snok/install-poetry@v1
      with:
        version: latest
        virtualenvs-create: true
        virtualenvs-in-project: true

    - name: Install dependencies
      working-directory: ./daemon
      run: |
        poetry install --only=dev

    - name: Run tests
      working-directory: ./daemon
      run: |
        chmod +x ../scripts/run_tests.sh
        ../scripts/run_tests.sh

    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./daemon/coverage.xml
```

### 📈 性能回归检测

```bash
# 性能基准比较
poetry run pytest tests/test_architecture_performance.py --benchmark-compare

# 生成性能报告
poetry run pytest tests/ --benchmark-json=performance_report.json

# 性能趋势分析
python scripts/analyze_performance_trends.py
```

## 🛠️ 测试最佳实践

### ✅ 测试编写指南

1. **测试命名**: 使用描述性的测试名称
2. **AAA模式**: Arrange-Act-Assert
3. **隔离性**: 每个测试独立运行
4. **模拟外部依赖**: 使用mock避免外部依赖
5. **性能敏感**: 标记性能测试并设置合理阈值

### 🏗️ 测试固件示例

```python
# conftest.py
import pytest
import tempfile
from core.container import ServiceContainer

@pytest.fixture
def temp_database():
    """临时数据库固件"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=True) as tmp:
        yield tmp.name

@pytest.fixture
async def ipc_server():
    """IPC服务器测试固件"""
    from services.ipc import UnifiedIPCServer

    server = UnifiedIPCServer()
    await server.start()

    yield server

    await server.stop()

@pytest.fixture
def mock_services():
    """模拟服务固件"""
    container = ServiceContainer()

    # 注册模拟服务
    mock_db = Mock()
    container.register_singleton(DatabaseService, lambda: mock_db)

    yield container

    container.clear()
```

### 📝 测试报告

```bash
# 生成综合测试报告
poetry run pytest --html=test_report.html --self-contained-html

# 性能基准报告
poetry run pytest --benchmark-histogram=benchmark_histogram

# 覆盖率徽章生成
coverage-badge -o coverage.svg
```

---

*该测试指南确保Linch Mind项目在所有开发阶段都保持高质量标准和性能要求，通过自动化测试流程确保架构铁律的严格执行。*
