# Linch Mind 配置系统

全新的用户友好配置文件系统，完全替代环境变量依赖。

## 概述

Linch Mind 现在使用基于配置文件的配置系统，支持多种格式（TOML、YAML、JSON），并提供环境特定的配置覆盖机制。

### 核心特性

- 🎯 **用户友好**: 直观的配置文件格式，支持注释和文档
- 🔧 **多格式支持**: TOML（推荐）、YAML、JSON 格式
- 🌍 **环境感知**: 自动环境检测和环境特定配置覆盖
- 🔒 **零环境变量**: 完全基于配置文件，无需设置环境变量
- 🚀 **即插即用**: 自动配置生成和模板支持
- 🔄 **向后兼容**: 平滑从旧配置系统迁移

## 配置文件结构

### 配置文件位置

配置文件位于环境特定的目录中：

```
~/.linch-mind/{environment}/config/
├── linch-mind.toml          # 主配置文件
├── linch-mind.yaml          # YAML格式配置（可选）
├── linch-mind.json          # JSON格式配置（可选）
├── linch-mind.{env}.toml    # 环境特定覆盖配置
└── templates/               # 配置模板
    ├── linch-mind.toml.template
    ├── linch-mind.yaml.template
    ├── linch-mind.development.yaml.template
    └── linch-mind.production.yaml.template
```

### 配置优先级

1. **环境特定配置** (`linch-mind.{environment}.toml`)
2. **主配置文件** (`linch-mind.toml` > `linch-mind.yaml` > `linch-mind.json`)
3. **环境默认值** (基于当前环境自动应用)
4. **系统默认值** (内置默认配置)

## 配置文件格式

### TOML格式 (推荐)

```toml
# Linch Mind Configuration File
app_name = "Linch Mind"
version = "0.1.0"
debug = false

# 数据库配置
[database]
type = "sqlite"
sqlite_file = "linch_mind.db"
use_encryption = true
max_connections = 20
connection_timeout = 30

# Ollama AI服务配置
[ollama]
host = "http://localhost:11434"
embedding_model = "nomic-embed-text:latest"
llm_model = "qwen2.5:0.5b"
value_threshold = 0.3
entity_threshold = 0.8
max_content_length = 10000
request_timeout = 30
connection_timeout = 5
enable_cache = true
cache_ttl_seconds = 3600

# 向量数据库配置
[vector]
provider = "faiss"
vector_dimension = 384
compressed_dimension = 256
shard_size_limit = 100000
compression_method = "PQ"
index_type = "HNSW"
max_memory_mb = 1024
preload_hot_shards = true
max_search_results = 10
search_timeout = 5

# IPC通信配置
[ipc]
socket_path = ""              # 空字符串表示自动生成
socket_permissions = "0600"
pipe_name = ""               # Windows Named Pipe名称
max_connections = 100
connection_timeout = 30
auth_required = true
buffer_size = 8192
enable_compression = false

# 连接器配置
[connectors]
config_directory = "connectors"
binary_directory = "connectors/bin"
enabled_connectors = {}      # 启用的连接器列表
auto_start = true
restart_on_failure = true
max_restart_attempts = 3
restart_delay_seconds = 5
health_check_interval = 30
log_level = "info"

# 安全配置
[security]
encrypt_database = true
encrypt_vectors = false      # 性能考虑，默认关闭
encrypt_logs = false
enable_access_control = true
allowed_processes = []
enable_audit_logging = true
audit_log_retention_days = 90
require_authentication = true
session_timeout_minutes = 60

# 性能配置
[performance]
enable_caching = true
cache_size_mb = 512
cache_ttl_seconds = 3600
max_workers = 4
max_concurrent_requests = 100
max_memory_gb = 2.0
max_storage_gb = 10.0
auto_cleanup = true
cleanup_interval_hours = 24

# 日志配置
[logging]
level = "info"
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
enable_console = true
enable_file = true
log_file = "linch-mind.log"
max_file_size_mb = 10
backup_count = 5
component_levels = {}        # 组件特定日志级别
```

## 环境特定配置

### 开发环境 (development)

```yaml
# linch-mind.development.yaml
debug: true

database:
  use_encryption: false
  sqlite_file: "linch_mind_dev.db"

ollama:
  value_threshold: 0.2  # 接受更多内容用于测试

security:
  encrypt_database: false
  enable_audit_logging: false
  require_authentication: false

logging:
  level: debug
  enable_console: true
```

### 生产环境 (production)

```yaml
# linch-mind.production.yaml
debug: false

database:
  use_encryption: true
  sqlite_file: "linch_mind_prod.db"
  max_connections: 50

ollama:
  value_threshold: 0.35  # 更严格的过滤
  entity_threshold: 0.85

security:
  encrypt_database: true
  encrypt_vectors: true
  enable_access_control: true
  enable_audit_logging: true
  require_authentication: true
  session_timeout_minutes: 30

performance:
  max_workers: 8
  max_concurrent_requests: 200
  max_memory_gb: 4.0
  max_storage_gb: 50.0

logging:
  level: warning
  enable_console: false
  max_file_size_mb: 50
  backup_count: 10
```

## 使用指南

### 1. 初始化配置

```bash
# 进入daemon目录
cd daemon

# 初始化默认配置文件
python scripts/config_manager_cli.py init --format toml

# 创建环境特定配置示例
python scripts/config_manager_cli.py init --format toml --create-env-example
```

### 2. 验证配置

```bash
# 验证当前配置
python scripts/config_manager_cli.py validate --verbose

# 验证特定配置文件
python scripts/config_manager_cli.py validate --config-file ~/.linch-mind/development/config/linch-mind.toml
```

### 3. 查看配置

```bash
# 显示配置摘要
python scripts/config_manager_cli.py show

# 显示详细配置
python scripts/config_manager_cli.py show --detailed
```

### 4. 生成配置模板

```bash
# 生成TOML模板
python scripts/config_manager_cli.py template --format toml --output my-config.toml

# 生成YAML模板并显示
python scripts/config_manager_cli.py template --format yaml --show
```

### 5. 环境变量迁移

```bash
# 从环境变量迁移配置
python scripts/config_manager_cli.py migrate-env-vars

# 指定保存格式
python scripts/config_manager_cli.py migrate-env-vars --format yaml
```

### 6. 格式转换

```bash
# 转换配置文件格式
python scripts/config_manager_cli.py convert config.yaml --input-format yaml --output-format toml
```

### 7. 配置比较

```bash
# 比较两个配置文件
python scripts/config_manager_cli.py compare config1.toml config2.toml
```

## 编程接口

### 使用新的配置系统

```python
from config.user_config_manager import get_user_config

# 获取完整配置
config = get_user_config()

# 访问特定配置段
database_config = config.database
ollama_config = config.ollama
ipc_config = config.ipc

# 使用配置值
print(f"Database type: {database_config.type}")
print(f"Ollama host: {ollama_config.host}")
print(f"IPC max connections: {ipc_config.max_connections}")
```

### 使用配置桥接器 (兼容性)

```python
from config.config_bridge import get_config_bridge

bridge = get_config_bridge()

# 获取各种配置
db_config = bridge.get_database_config()
ollama_config = bridge.get_ollama_config()
ipc_config = bridge.get_ipc_config()
security_config = bridge.get_security_config()
```

### 便捷访问函数

```python
from config.user_config_manager import (
    get_user_database_config,
    get_user_ollama_config,
    get_user_ipc_config,
    get_user_security_config
)

# 直接获取特定配置段
db_config = get_user_database_config()
ollama_config = get_user_ollama_config()
```

## 配置项详解

### 数据库配置 (database)

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `type` | string | "sqlite" | 数据库类型 (sqlite/postgresql/mysql) |
| `host` | string | "localhost" | 数据库主机 |
| `port` | int | 5432 | 数据库端口 |
| `database` | string | "linch_mind" | 数据库名称 |
| `sqlite_file` | string | "linch_mind.db" | SQLite文件名 |
| `use_encryption` | bool | true | 是否使用加密 |
| `max_connections` | int | 20 | 最大连接数 |
| `connection_timeout` | int | 30 | 连接超时时间 |

### Ollama配置 (ollama)

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `host` | string | "http://localhost:11434" | Ollama服务地址 |
| `embedding_model` | string | "nomic-embed-text:latest" | 嵌入模型 |
| `llm_model` | string | "qwen2.5:0.5b" | 语言模型 |
| `value_threshold` | float | 0.3 | 价值阈值 |
| `entity_threshold` | float | 0.8 | 实体阈值 |
| `max_content_length` | int | 10000 | 最大内容长度 |
| `request_timeout` | int | 30 | 请求超时时间 |
| `connection_timeout` | int | 5 | 连接超时时间 |
| `enable_cache` | bool | true | 是否启用缓存 |
| `cache_ttl_seconds` | int | 3600 | 缓存TTL |

### 向量配置 (vector)

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `provider` | string | "faiss" | 向量数据库提供者 |
| `vector_dimension` | int | 384 | 向量维度 |
| `compressed_dimension` | int | 256 | 压缩维度 |
| `shard_size_limit` | int | 100000 | 分片大小限制 |
| `compression_method` | string | "PQ" | 压缩方法 |
| `index_type` | string | "HNSW" | 索引类型 |
| `max_memory_mb` | int | 1024 | 最大内存使用 |
| `preload_hot_shards` | bool | true | 预加载热分片 |
| `max_search_results` | int | 10 | 最大搜索结果数 |
| `search_timeout` | int | 5 | 搜索超时时间 |

### IPC配置 (ipc)

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `socket_path` | string | "" | Unix Socket路径 (空=自动) |
| `socket_permissions` | string | "0600" | Socket权限 |
| `pipe_name` | string | "" | Windows管道名 (空=自动) |
| `max_connections` | int | 100 | 最大连接数 |
| `connection_timeout` | int | 30 | 连接超时时间 |
| `auth_required` | bool | true | 是否需要认证 |
| `buffer_size` | int | 8192 | 缓冲区大小 |
| `enable_compression` | bool | false | 是否启用压缩 |

### 安全配置 (security)

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `encrypt_database` | bool | true | 数据库加密 |
| `encrypt_vectors` | bool | false | 向量加密 |
| `encrypt_logs` | bool | false | 日志加密 |
| `enable_access_control` | bool | true | 访问控制 |
| `allowed_processes` | list | [] | 允许的进程列表 |
| `enable_audit_logging` | bool | true | 审计日志 |
| `audit_log_retention_days` | int | 90 | 审计日志保留天数 |
| `require_authentication` | bool | true | 需要认证 |
| `session_timeout_minutes` | int | 60 | 会话超时时间 |

## 迁移指南

### 从环境变量迁移

如果你之前使用环境变量配置 Linch Mind，可以使用迁移工具：

```bash
# 自动迁移环境变量到配置文件
python scripts/config_manager_cli.py migrate-env-vars

# 检查迁移结果
python scripts/config_manager_cli.py show --detailed
```

### 支持的环境变量迁移

| 环境变量 | 配置路径 | 说明 |
|----------|----------|------|
| `OLLAMA_HOST` | `ollama.host` | Ollama服务地址 |
| `OLLAMA_EMBEDDING_MODEL` | `ollama.embedding_model` | 嵌入模型 |
| `OLLAMA_LLM_MODEL` | `ollama.llm_model` | 语言模型 |
| `AI_VALUE_THRESHOLD` | `ollama.value_threshold` | AI价值阈值 |
| `ENABLE_INTELLIGENT_PROCESSING` | `performance.enable_caching` | 智能处理开关 |
| `LINCH_DEBUG` | `debug` | 调试模式 |

### 手动迁移步骤

1. **备份现有环境变量**
   ```bash
   env | grep -E "(OLLAMA|LINCH|AI)_" > backup_env_vars.txt
   ```

2. **初始化配置文件**
   ```bash
   python scripts/config_manager_cli.py init --format toml
   ```

3. **编辑配置文件**
   根据环境变量值编辑配置文件

4. **验证配置**
   ```bash
   python scripts/config_manager_cli.py validate --verbose
   ```

5. **移除环境变量**
   从 shell 配置文件中移除相关环境变量

## 故障排除

### 常见问题

1. **配置文件未找到**
   ```bash
   # 检查配置目录
   python scripts/config_manager_cli.py show
   
   # 重新初始化
   python scripts/config_manager_cli.py init --force
   ```

2. **配置验证失败**
   ```bash
   # 详细验证信息
   python scripts/config_manager_cli.py validate --verbose
   
   # 使用默认配置
   python scripts/config_manager_cli.py init --force --format toml
   ```

3. **格式错误**
   ```bash
   # 转换为正确格式
   python scripts/config_manager_cli.py convert broken-config.yaml --input-format yaml --output-format toml
   ```

4. **权限问题**
   ```bash
   # 检查配置目录权限
   ls -la ~/.linch-mind/*/config/
   
   # 修复权限
   chmod 755 ~/.linch-mind/*/config/
   chmod 644 ~/.linch-mind/*/config/*.toml
   ```

### 调试配置加载

```python
import logging

# 启用配置调试日志
logging.getLogger('config').setLevel(logging.DEBUG)

from config.user_config_manager import get_user_config_manager

# 获取配置管理器并查看加载过程
manager = get_user_config_manager()
config = manager.get_config(force_reload=True)

# 查看配置摘要
summary = manager.get_config_summary()
print(json.dumps(summary, indent=2))
```

## 最佳实践

### 1. 配置文件管理

- **使用 TOML 格式**: 推荐使用 TOML 格式，支持注释和更好的可读性
- **环境隔离**: 为不同环境创建专门的配置覆盖文件
- **版本控制**: 将配置模板加入版本控制，但不要提交包含敏感信息的实际配置
- **配置验证**: 定期验证配置文件的正确性

### 2. 安全考虑

- **敏感信息**: 不要在配置文件中包含密码等敏感信息
- **文件权限**: 确保配置文件有适当的权限设置
- **加密配置**: 在生产环境中启用数据库加密
- **审计日志**: 启用审计日志记录配置变更

### 3. 性能优化

- **缓存配置**: 启用配置缓存以提高性能
- **合理的阈值**: 根据实际需求调整各种阈值参数
- **资源限制**: 设置合理的内存和存储限制
- **清理策略**: 配置自动清理以维护系统性能

## 开发者指南

### 添加新的配置项

1. **更新数据类**
   ```python
   # 在 user_config_manager.py 中添加新的配置项
   @dataclass
   class UserNewFeatureConfig:
       new_setting: str = "default_value"
       enable_feature: bool = True
   ```

2. **更新主配置类**
   ```python
   @dataclass
   class UserConfig:
       # 现有配置...
       new_feature: UserNewFeatureConfig = field(default_factory=UserNewFeatureConfig)
   ```

3. **更新模板**
   在配置模板中添加新的配置段

4. **更新文档**
   在本文档中添加新配置项的说明

### 扩展配置桥接器

```python
# 在 config_bridge.py 中添加新的配置获取方法
def get_new_feature_config(self) -> Dict[str, Any]:
    """获取新功能配置"""
    cache_key = "new_feature_config"
    if cache_key in self._config_cache:
        return self._config_cache[cache_key]
    
    try:
        if self.user_config_manager:
            user_config = self.user_config_manager.get_config()
            config = {
                "new_setting": user_config.new_feature.new_setting,
                "enable_feature": user_config.new_feature.enable_feature,
            }
            self._config_cache[cache_key] = config
            return config
    except Exception as e:
        logger.warning(f"Failed to get new feature config: {e}")
    
    # 默认值
    default_config = {
        "new_setting": "default_value",
        "enable_feature": True,
    }
    self._config_cache[cache_key] = default_config
    return default_config
```

## 更新日志

### v2.0.0 (当前版本)
- 🆕 全新的配置文件系统
- 🔧 支持 TOML、YAML、JSON 格式
- 🌍 环境特定配置覆盖
- 🚀 配置管理 CLI 工具
- 🔄 从环境变量的无缝迁移
- 🛡️ 配置桥接器确保向后兼容

### v1.x (传统版本)
- 基于环境变量的配置系统
- 有限的配置验证
- 手动配置管理