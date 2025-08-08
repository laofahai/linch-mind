# IPC协议完整规范

**版本**: 2.1.0  
**状态**: 生产就绪  
**创建时间**: 2025-08-08  
**适用于**: Linch Mind纯IPC架构完整技术规范

---

## 📋 文档概览

本文档定义了Linch Mind系统中daemon与客户端(UI/连接器)之间的完整IPC通信协议规范，包括：

- **传输层协议**: Unix Socket/Named Pipe通信机制
- **消息格式**: 二进制长度前缀+JSON载荷格式
- **API契约**: 完整的请求/响应接口定义
- **错误处理**: 标准化错误码和异常处理
- **性能规范**: 延迟、吞吐量等性能要求
- **安全机制**: 进程身份验证和权限控制

---

## 🏗️ 1. IPC架构设计

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    IPC通信架构图                             │
├─────────────────────────────────────────────────────────────┤
│  Flutter UI Client                                         │
│  ├─ Dart IPC Client                                        │
│  ├─ Unix Socket连接 (macOS/Linux)                           │
│  └─ Named Pipe连接 (Windows)                               │
├─────────────────────────────────────────────────────────────┤
│  C++ Connector Client                                      │
│  ├─ libcurl HTTP客户端                                      │
│  ├─ daemon发现机制                                           │
│  └─ 配置热重载                                               │
├─────────────────────────────────────────────────────────────┤
│                    IPC传输层                                │
│  ├─ 消息长度前缀 (4 bytes big endian)                       │
│  ├─ JSON消息载荷 (UTF-8编码)                                 │
│  └─ 双向通信管道                                             │
├─────────────────────────────────────────────────────────────┤
│                 Python Daemon Server                       │
│  ├─ IPC服务器 (ipc_server.py)                               │
│  ├─ 路由分发器 (ipc_router.py)                               │
│  ├─ 中间件系统 (ipc_middleware.py)                           │
│  └─ 业务服务层                                               │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 通信模式

- **请求-响应模式**: 客户端发起请求，服务端返回响应
- **同步处理**: 单连接单请求，简化错误处理
- **连接复用**: 支持连接池，提升并发性能
- **优雅关闭**: 支持连接正确关闭和资源清理

---

## 🔗 2. 传输层协议

### 2.1 连接建立

#### Unix Socket (macOS/Linux)
```bash
# Socket文件路径
~/.linch-mind/daemon.sock

# 权限设置
owner: rw (读写权限)
group: r-- (只读权限)  
other: --- (无权限)
```

#### Named Pipe (Windows)
```bash
# Pipe名称
\\.\pipe\linch_mind_daemon

# 安全设置
ACL: 仅允许当前用户访问
```

### 2.2 消息传输格式

```
┌─────────────────────────────────────────────────────────────┐
│                    IPC消息传输格式                           │
├─────────────────────────────────────────────────────────────┤
│  消息长度头部 (4 bytes)    │     消息载荷 (variable)        │
│  Big Endian Uint32        │     UTF-8 JSON                 │
│  0x00 0x00 0x01 0x2A      │     {"method": "GET", ...}     │
└─────────────────────────────────────────────────────────────┘
```

#### 消息长度头部规范
- **字节序**: Big Endian (网络字节序)
- **数据类型**: 32位无符号整数
- **最大消息长度**: 4GB (实际建议限制为16MB)

#### JSON载荷规范
- **编码**: UTF-8
- **格式**: 标准JSON，无压缩
- **最大嵌套深度**: 32层
- **键名规范**: snake_case风格

---

## 📨 3. 消息格式规范

### 3.1 IPC请求消息

```python
class IPCRequest(BaseModel):
    """IPC请求消息标准格式"""
    method: str = Field(..., description="HTTP方法 (GET/POST/PUT/DELETE)")
    path: str = Field(..., description="API路径", regex=r"^/api/v\d+/.*")
    data: Optional[Dict[str, Any]] = Field(None, description="请求数据")
    headers: Dict[str, str] = Field(default_factory=dict, description="请求头")
    query_params: Dict[str, Any] = Field(default_factory=dict, description="查询参数")
    request_id: Optional[str] = Field(None, description="请求追踪ID")
    timeout: Optional[int] = Field(30, description="超时时间(秒)", ge=1, le=300)
    
    class Config:
        schema_extra = {
            "example": {
                "method": "GET",
                "path": "/api/v1/entities",
                "data": None,
                "headers": {
                    "Content-Type": "application/json",
                    "User-Agent": "LinchMind-UI/1.0.0"
                },
                "query_params": {
                    "type": "file",
                    "limit": 50,
                    "offset": 0
                },
                "request_id": "req_8f7e9d12_001",
                "timeout": 30
            }
        }
```

### 3.2 IPC响应消息

```python
class IPCResponse(BaseModel):
    """IPC响应消息标准格式"""
    status_code: int = Field(..., description="HTTP状态码")
    data: Optional[Union[Dict[str, Any], List[Any]]] = Field(None, description="响应数据")
    headers: Dict[str, str] = Field(default_factory=dict, description="响应头")
    error: Optional[Dict[str, Any]] = Field(None, description="错误信息")
    request_id: Optional[str] = Field(None, description="对应的请求ID")
    processing_time: Optional[float] = Field(None, description="处理时间(毫秒)")
    
    class Config:
        schema_extra = {
            "example": {
                "status_code": 200,
                "data": {
                    "entities": [
                        {
                            "id": "entity_abc123",
                            "type": "file",
                            "name": "example.txt",
                            "created_at": "2025-08-08T10:30:00Z"
                        }
                    ],
                    "total": 1,
                    "page": 0
                },
                "headers": {
                    "Content-Type": "application/json",
                    "X-RateLimit-Remaining": "999"
                },
                "error": None,
                "request_id": "req_8f7e9d12_001",
                "processing_time": 1.23
            }
        }
```

### 3.3 错误响应格式

```python
class IPCError(BaseModel):
    """标准IPC错误响应"""
    error_code: str = Field(..., description="错误代码")
    error_message: str = Field(..., description="错误描述")
    error_type: str = Field(..., description="错误类型")
    details: Optional[Dict[str, Any]] = Field(None, description="详细错误信息")
    stack_trace: Optional[str] = Field(None, description="调试堆栈(仅开发模式)")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间")
    
    class Config:
        schema_extra = {
            "example": {
                "error_code": "ENTITY_NOT_FOUND",
                "error_message": "指定的实体不存在或已被删除",
                "error_type": "ResourceNotFoundError",
                "details": {
                    "entity_id": "entity_invalid123",
                    "resource_type": "Entity",
                    "suggestion": "请检查实体ID是否正确"
                },
                "stack_trace": None,
                "timestamp": "2025-08-08T10:30:00Z"
            }
        }
```

---

## 🛣️ 4. API路由规范

### 4.1 实体管理API

```python
# GET /api/v1/entities - 获取实体列表
{
    "method": "GET",
    "path": "/api/v1/entities",
    "query_params": {
        "type": "file|clipboard|url|note",  # 可选，实体类型过滤
        "tags": ["tag1", "tag2"],           # 可选，标签过滤
        "search": "搜索关键词",               # 可选，全文搜索
        "limit": 50,                        # 可选，返回数量限制 (1-1000)
        "offset": 0,                        # 可选，分页偏移
        "sort_by": "created_at|updated_at|name", # 可选，排序字段
        "sort_order": "asc|desc"            # 可选，排序方向
    }
}

# POST /api/v1/entities - 创建新实体
{
    "method": "POST",
    "path": "/api/v1/entities",
    "data": {
        "type": "file",
        "name": "example.txt",
        "content": "文件内容文本",
        "metadata": {
            "file_path": "/path/to/file",
            "file_size": 1024,
            "mime_type": "text/plain"
        },
        "tags": ["重要", "工作"]
    }
}

# PUT /api/v1/entities/{entity_id} - 更新实体
{
    "method": "PUT", 
    "path": "/api/v1/entities/entity_abc123",
    "data": {
        "name": "新的文件名.txt",
        "tags": ["更新", "标签"],
        "metadata": {
            "updated_reason": "用户手动更新"
        }
    }
}

# DELETE /api/v1/entities/{entity_id} - 删除实体
{
    "method": "DELETE",
    "path": "/api/v1/entities/entity_abc123"
}

# GET /api/v1/entities/{entity_id}/relationships - 获取关联实体
{
    "method": "GET",
    "path": "/api/v1/entities/entity_abc123/relationships",
    "query_params": {
        "relationship_type": "similar|related|referenced", # 关系类型
        "limit": 10                                       # 返回数量
    }
}
```

### 4.2 推荐系统API

```python
# GET /api/v1/recommendations - 获取推荐列表
{
    "method": "GET",
    "path": "/api/v1/recommendations",
    "query_params": {
        "type": "related_content|trending|personal|smart_action",
        "limit": 10,                    # 推荐数量 (1-50)
        "min_score": 0.7,              # 最低推荐分数
        "context_entity_id": "entity_xyz", # 上下文实体ID
        "user_preferences": {           # 用户偏好
            "categories": ["技术", "学习"],
            "exclude_types": ["clipboard"]
        }
    }
}

# POST /api/v1/recommendations/feedback - 提交推荐反馈
{
    "method": "POST",
    "path": "/api/v1/recommendations/feedback",
    "data": {
        "recommendation_id": "rec_12345",
        "feedback_type": "positive|negative|neutral",
        "user_action": "clicked|dismissed|shared",
        "rating": 4,                    # 1-5星评分
        "comment": "这个推荐很有用"      # 可选文本反馈
    }
}

# POST /api/v1/recommendations/generate - 生成新推荐
{
    "method": "POST",
    "path": "/api/v1/recommendations/generate",
    "data": {
        "user_context": {
            "current_activity": "writing",
            "active_entities": ["entity_abc123", "entity_def456"],
            "time_of_day": "morning",
            "user_location": "office"
        },
        "recommendation_count": 5,
        "algorithm": "neural_cf|content_based|hybrid"
    }
}
```

### 4.3 连接器管理API

```python
# GET /api/v1/connectors - 获取连接器列表
{
    "method": "GET",
    "path": "/api/v1/connectors",
    "query_params": {
        "status": "running|stopped|error|all", # 状态过滤
        "type": "filesystem|clipboard",        # 类型过滤
        "include_config": true                 # 是否包含配置详情
    }
}

# POST /api/v1/connectors/{connector_id}/start - 启动连接器
{
    "method": "POST",
    "path": "/api/v1/connectors/filesystem_001/start",
    "data": {
        "startup_timeout": 30,          # 启动超时(秒)
        "wait_for_health_check": true   # 是否等待健康检查
    }
}

# POST /api/v1/connectors/{connector_id}/stop - 停止连接器
{
    "method": "POST",
    "path": "/api/v1/connectors/filesystem_001/stop",
    "data": {
        "graceful_shutdown": true,      # 优雅关闭
        "shutdown_timeout": 10          # 关闭超时(秒)
    }
}

# PUT /api/v1/connectors/{connector_id}/config - 更新配置
{
    "method": "PUT",
    "path": "/api/v1/connectors/filesystem_001/config",
    "data": {
        "global_config": {
            "check_interval": 2.0,
            "max_file_size": 20
        },
        "directory_configs": [
            {
                "path": "~/Documents",
                "display_name": "文档目录",
                "priority": "high"
            }
        ],
        "hot_reload": true              # 是否热重载配置
    }
}

# GET /api/v1/connectors/{connector_id}/logs - 获取连接器日志
{
    "method": "GET",
    "path": "/api/v1/connectors/filesystem_001/logs",
    "query_params": {
        "lines": 100,                   # 日志行数
        "level": "info|debug|warning|error", # 日志级别
        "since": "2025-08-08T09:00:00Z", # 起始时间
        "follow": false                 # 是否持续跟踪
    }
}
```

### 4.4 系统管理API

```python
# GET /api/v1/system/health - 系统健康检查
{
    "method": "GET",
    "path": "/api/v1/system/health",
    "query_params": {
        "include_components": true,     # 包含组件详情
        "check_connections": true       # 检查外部连接
    }
}

# GET /api/v1/system/stats - 系统统计信息
{
    "method": "GET",
    "path": "/api/v1/system/stats",
    "query_params": {
        "metrics": "performance|storage|connections", # 指标类型
        "time_range": "1h|24h|7d|30d"  # 时间范围
    }
}

# POST /api/v1/system/config/reload - 重载系统配置
{
    "method": "POST",
    "path": "/api/v1/system/config/reload",
    "data": {
        "config_sections": ["logging", "storage", "security"],
        "restart_services": false       # 是否重启相关服务
    }
}
```

---

## 📊 5. 性能规范

### 5.1 性能指标要求

| 指标 | 要求 | 优秀 | 测试方法 |
|------|------|------|----------|
| **IPC连接建立** | <5ms | <2ms | 客户端连接测试 |
| **消息往返时间** | <1ms | <0.5ms | ping-pong测试 |
| **JSON序列化** | <0.1ms | <0.05ms | 大对象序列化测试 |
| **并发连接数** | >100 | >1000 | 并发压力测试 |
| **吞吐量(RPS)** | >10,000 | >30,000 | 持续负载测试 |
| **内存使用** | <100MB | <50MB | 内存监控测试 |
| **CPU使用** | <5% | <2% | CPU监控测试 |

### 5.2 性能优化建议

#### 客户端优化
```python
# 1. 连接复用
class ConnectionPool:
    def __init__(self, max_connections=10):
        self._pool = Queue(maxsize=max_connections)
    
    @contextmanager
    async def get_connection(self):
        client = await self._pool.get()
        try:
            yield client
        finally:
            await self._pool.put(client)

# 2. 批量请求
async def batch_requests(requests: List[IPCRequest]):
    """批量发送请求，减少连接开销"""
    async with pool.get_connection() as client:
        tasks = [client.send_request(req) for req in requests]
        return await asyncio.gather(*tasks)

# 3. 请求缓存
@lru_cache(maxsize=128)
def cached_request(method: str, path: str, cache_key: str):
    """缓存GET请求结果"""
    return send_ipc_request(method, path)
```

#### 服务端优化
```python
# 1. 异步处理
async def handle_request(request: IPCRequest) -> IPCResponse:
    """异步请求处理，支持高并发"""
    async with request_semaphore:  # 限制并发数
        return await process_request(request)

# 2. 响应压缩
def compress_response(data: dict) -> bytes:
    """大响应数据压缩"""
    if len(json.dumps(data)) > 1024:  # 1KB阈值
        return gzip.compress(json.dumps(data).encode())
    return json.dumps(data).encode()

# 3. 预处理缓存
@functools.lru_cache(maxsize=1000)
def get_cached_entities(query_hash: str):
    """查询结果缓存，减少数据库访问"""
    return database.query_entities(query_hash)
```

---

## 🔒 6. 安全机制

### 6.1 进程身份验证

```python
class IPCSecurity:
    """IPC安全机制"""
    
    @staticmethod
    def verify_client_process(connection) -> bool:
        """验证客户端进程身份"""
        try:
            # Unix Socket - 获取对端进程信息
            peer_cred = connection.getsockopt(
                socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize('3i')
            )
            pid, uid, gid = struct.unpack('3i', peer_cred)
            
            # 验证UID是否为当前用户
            if uid != os.getuid():
                return False
                
            # 验证进程是否存在且有效
            if not psutil.pid_exists(pid):
                return False
                
            process = psutil.Process(pid)
            return process.username() == getpass.getuser()
            
        except Exception as e:
            logger.warning(f"进程验证失败: {e}")
            return False
```

### 6.2 权限控制

```python
class PermissionManager:
    """权限管理器"""
    
    PERMISSIONS = {
        "read_entities": ["ui", "connector"],
        "write_entities": ["ui"],
        "manage_connectors": ["ui"],
        "system_admin": ["ui"]
    }
    
    def check_permission(self, client_type: str, action: str) -> bool:
        """检查客户端权限"""
        allowed_clients = self.PERMISSIONS.get(action, [])
        return client_type in allowed_clients
    
    def get_client_type(self, process_info: dict) -> str:
        """根据进程信息确定客户端类型"""
        exe_path = process_info.get("executable", "")
        
        if "flutter" in exe_path or "linch-mind-ui" in exe_path:
            return "ui"
        elif "connector" in exe_path:
            return "connector"
        else:
            return "unknown"
```

### 6.3 数据保护

```python
class DataProtection:
    """敏感数据保护"""
    
    SENSITIVE_FIELDS = [
        "password", "token", "key", "secret", 
        "email", "phone", "ssn", "credit_card"
    ]
    
    def sanitize_response(self, data: dict) -> dict:
        """清理响应中的敏感信息"""
        if isinstance(data, dict):
            for key in list(data.keys()):
                if any(field in key.lower() for field in self.SENSITIVE_FIELDS):
                    data[key] = "[REDACTED]"
                elif isinstance(data[key], (dict, list)):
                    data[key] = self.sanitize_response(data[key])
        elif isinstance(data, list):
            return [self.sanitize_response(item) for item in data]
        
        return data
```

---

## 🔧 7. 错误处理规范

### 7.1 标准错误码

```python
class IPCErrorCodes:
    """IPC错误码定义"""
    
    # 客户端错误 (4xx)
    BAD_REQUEST = "BAD_REQUEST_400"
    UNAUTHORIZED = "UNAUTHORIZED_401" 
    FORBIDDEN = "FORBIDDEN_403"
    NOT_FOUND = "NOT_FOUND_404"
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED_405"
    CONFLICT = "CONFLICT_409"
    VALIDATION_ERROR = "VALIDATION_ERROR_422"
    RATE_LIMITED = "RATE_LIMITED_429"
    
    # 服务器错误 (5xx)
    INTERNAL_ERROR = "INTERNAL_ERROR_500"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED_501"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE_503"
    TIMEOUT = "TIMEOUT_504"
    
    # IPC特定错误 (6xx)
    CONNECTION_LOST = "CONNECTION_LOST_600"
    PROTOCOL_ERROR = "PROTOCOL_ERROR_601"
    MESSAGE_TOO_LARGE = "MESSAGE_TOO_LARGE_602"
    SERIALIZATION_ERROR = "SERIALIZATION_ERROR_603"
```

### 7.2 错误处理策略

```python
class IPCErrorHandler:
    """统一错误处理器"""
    
    def handle_exception(self, e: Exception, request: IPCRequest) -> IPCResponse:
        """统一异常处理"""
        if isinstance(e, ValidationError):
            return self._create_error_response(
                status_code=422,
                error_code=IPCErrorCodes.VALIDATION_ERROR,
                error_message="请求数据验证失败",
                details={"validation_errors": e.errors()},
                request_id=request.request_id
            )
        elif isinstance(e, ResourceNotFoundError):
            return self._create_error_response(
                status_code=404,
                error_code=IPCErrorCodes.NOT_FOUND,
                error_message=str(e),
                request_id=request.request_id
            )
        elif isinstance(e, TimeoutError):
            return self._create_error_response(
                status_code=504,
                error_code=IPCErrorCodes.TIMEOUT,
                error_message="请求处理超时",
                request_id=request.request_id
            )
        else:
            # 未知错误，记录详细日志
            logger.exception(f"未处理异常: {e}")
            return self._create_error_response(
                status_code=500,
                error_code=IPCErrorCodes.INTERNAL_ERROR,
                error_message="服务器内部错误",
                request_id=request.request_id
            )
```

---

## 🧪 8. 测试与验证

### 8.1 协议兼容性测试

```python
class IPCProtocolTest:
    """IPC协议测试套件"""
    
    async def test_message_format(self):
        """测试消息格式兼容性"""
        # 测试各种请求格式
        test_requests = [
            {"method": "GET", "path": "/api/v1/health"},
            {"method": "POST", "path": "/api/v1/entities", "data": {"test": True}},
            {"method": "GET", "path": "/api/v1/entities", "query_params": {"limit": 10}}
        ]
        
        for request in test_requests:
            response = await self.client.send_request(**request)
            assert "status_code" in response
            assert "data" in response or "error" in response
    
    async def test_performance_requirements(self):
        """测试性能要求"""
        # 延迟测试
        start_time = time.time()
        await self.client.send_request("GET", "/api/v1/health")
        latency = (time.time() - start_time) * 1000
        assert latency < 1.0, f"延迟超标: {latency}ms"
        
        # 并发测试
        tasks = [
            self.client.send_request("GET", "/api/v1/health")
            for _ in range(100)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        assert success_count >= 98, f"并发成功率过低: {success_count}/100"
```

### 8.2 集成测试

```bash
#!/bin/bash
# IPC集成测试脚本

# 启动测试环境
./scripts/start_test_daemon.sh

# 运行协议测试
python -m pytest tests/test_ipc_protocol.py -v

# 运行性能测试  
python -m pytest tests/test_ipc_performance.py -v

# 运行安全测试
python -m pytest tests/test_ipc_security.py -v

# 清理测试环境
./scripts/cleanup_test_daemon.sh
```

---

## 📖 9. 客户端集成指南

### 9.1 Python客户端实现

请参考 **[IPC客户端使用指南](./ipc_client_usage_guide.md)** 中的完整Python客户端实现，包括：

- 基础连接和请求处理
- 错误处理和自动重连
- 连接池管理
- 跨平台支持
- 性能优化
- 调试和监控

### 9.2 Flutter/Dart客户端实现

请参考 **[IPC客户端使用指南](./ipc_client_usage_guide.md)** 中的Dart客户端实现，包括：

- Unix Socket连接
- 异步消息处理
- 错误处理机制
- Riverpod集成
- 平台适配

### 9.3 C++客户端实现

```cpp
// 基于shared库的C++连接器客户端
#include <linch_connector/daemon_discovery.hpp>
#include <linch_connector/http_client.hpp>

using namespace linch_connector;

class IPCConnectorClient {
private:
    std::unique_ptr<HttpClient> httpClient;
    std::string daemonBaseUrl;

public:
    bool initialize() {
        // 发现daemon服务
        DaemonDiscovery discovery;
        auto daemonInfo = discovery.waitForDaemon(std::chrono::seconds(30));
        
        if (!daemonInfo) {
            return false;
        }
        
        daemonBaseUrl = daemonInfo->getBaseUrl();
        httpClient = std::make_unique<HttpClient>();
        httpClient->addHeader("Content-Type", "application/json");
        
        return true;
    }
    
    std::optional<nlohmann::json> sendRequest(
        const std::string& method,
        const std::string& path,
        const nlohmann::json& data = nullptr
    ) {
        std::string url = daemonBaseUrl + path;
        HttpResponse response;
        
        if (method == "GET") {
            response = httpClient->get(url);
        } else if (method == "POST") {
            response = httpClient->post(url, data.dump());
        }
        
        if (response.success) {
            return nlohmann::json::parse(response.body);
        }
        
        return std::nullopt;
    }
};
```

---

## 🔄 10. 协议版本管理

### 10.1 版本控制策略

```python
class ProtocolVersionManager:
    """IPC协议版本管理"""
    
    CURRENT_VERSION = "2.1.0"
    SUPPORTED_VERSIONS = ["1.0.0", "2.0.0", "2.1.0"]
    MIN_COMPATIBLE_VERSION = "2.0.0"
    
    @classmethod
    def negotiate_version(cls, client_version: str) -> str:
        """协商协议版本"""
        if client_version in cls.SUPPORTED_VERSIONS:
            return client_version
        
        # 查找最高兼容版本
        compatible_versions = [
            v for v in cls.SUPPORTED_VERSIONS 
            if cls._is_compatible(client_version, v)
        ]
        
        if compatible_versions:
            return max(compatible_versions)
        
        return cls.MIN_COMPATIBLE_VERSION
    
    @classmethod
    def _is_compatible(cls, client_ver: str, server_ver: str) -> bool:
        """检查版本兼容性"""
        client_major = int(client_ver.split('.')[0])
        server_major = int(server_ver.split('.')[0])
        
        # 主版本必须相同
        return client_major == server_major
```

### 10.2 向后兼容性保证

- **消息格式**: 新字段使用可选字段，旧字段保持不变
- **API路径**: 旧版本API路径继续支持
- **错误码**: 错误码保持稳定，新增错误使用新编号
- **数据结构**: 数据结构只能添加字段，不能删除或修改现有字段

---

## 🔗 11. 相关文档

- **[API契约设计](./api_contract_design.md)**: IPC消息协议和数据模型
- **[IPC客户端使用指南](./ipc_client_usage_guide.md)**: 完整的客户端实现示例
- **[Daemon架构设计](./daemon_architecture.md)**: 服务端实现架构
- **[Flutter架构设计](./flutter_architecture_design.md)**: UI客户端架构

---

**IPC协议规范完成**: 本文档提供了Linch Mind IPC通信的完整技术规范，确保客户端和服务端的标准化实现。

**文档版本**: 2.1.0  
**创建时间**: 2025-08-08  
**维护团队**: IPC协议组