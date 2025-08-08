# IPC消息协议设计标准

**版本**: 2.0  
**状态**: 已实现  
**创建时间**: 2025-08-02  
**最新更新**: 2025-08-08  
**适用于**: 纯IPC架构 + 跨平台通信

## 🚀 重大协议升级 (v2.0)

**从HTTP REST到IPC消息协议的完全迁移**: 项目已完成协议栈的重大升级，从HTTP REST API转换为高性能IPC消息协议，实现更快速、更安全的本地进程间通信。

## 1. IPC协议设计原则

### 1.1 核心原则
- **消息优先**: 先设计消息协议，再开发实现
- **向后兼容**: 新版本消息格式兼容旧版本
- **语义化版本**: 使用semver (v2.0.0)
- **强类型定义**: Pydantic模型保证消息结构一致性
- **平台无关**: 统一消息格式，跨平台兼容
- **性能优先**: 二进制长度前缀+JSON，延迟<1ms

### 1.2 IPC消息协议规范

#### 消息传输格式

```
┌─────────────────────────────────────────────────────────────┐
│                    IPC消息传输格式                           │
├─────────────────────────────────────────────────────────────┤
│  消息长度 (4 bytes, big endian)  │  消息内容 (UTF-8 JSON)    │
│  0x00 0x00 0x01 0x2A            │  {"method": "GET", ...}   │
└─────────────────────────────────────────────────────────────┘
```

#### IPC请求消息格式

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum

class IPCRequest(BaseModel):
    """IPC请求消息格式"""
    method: str = Field(..., description="IPC方法 (GET/POST/PUT/DELETE)")
    path: str = Field(..., description="请求路径")
    data: Optional[Dict[str, Any]] = Field(None, description="请求数据")
    headers: Dict[str, str] = Field(default_factory=dict, description="请求头")
    query_params: Dict[str, Any] = Field(default_factory=dict, description="查询参数")
    
    class Config:
        schema_extra = {
            "example": {
                "method": "GET",
                "path": "/api/v1/entities/entity_123",
                "data": None,
                "headers": {"Content-Type": "application/json"},
                "query_params": {"include_relations": True}
            }
        }

class IPCResponse(BaseModel):
    """IPC响应消息格式"""
    status_code: int = Field(..., description="状态码")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    headers: Dict[str, str] = Field(default_factory=dict, description="响应头")
    
    class Config:
        schema_extra = {
            "example": {
                "status_code": 200,
                "data": {"id": "entity_123", "name": "example.txt"},
                "headers": {"Content-Type": "application/json"}
            }
        }
```

## 2. 核心数据模型

### 2.1 实体模型 (Entity)
```python
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class EntityType(str, Enum):
    """实体类型枚举"""
    FILE = "file"
    CLIPBOARD = "clipboard"
    URL = "url"
    NOTE = "note"
    EMAIL = "email"
    CHAT = "chat"

class Entity(BaseModel):
    """知识图谱实体模型"""
    id: str = Field(..., description="实体唯一标识", example="entity_abc123")
    type: EntityType = Field(..., description="实体类型")
    name: str = Field(..., max_length=255, description="实体名称")
    content: Optional[str] = Field(None, description="实体内容")
    summary: Optional[str] = Field(None, description="AI生成摘要")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="扩展元数据")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
```

### 2.2 推荐模型 (Recommendation)
```python
class RecommendationType(str, Enum):
    """推荐类型枚举"""
    RELATED_CONTENT = "related_content"
    TRENDING = "trending"
    PERSONAL = "personal"
    SMART_ACTION = "smart_action"

class Recommendation(BaseModel):
    """智能推荐模型"""
    id: str = Field(..., description="推荐唯一标识")
    title: str = Field(..., description="推荐标题")
    description: str = Field(..., description="推荐描述")
    type: RecommendationType = Field(..., description="推荐类型")
    score: float = Field(..., ge=0.0, le=1.0, description="推荐得分")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度")
    created_at: datetime = Field(default_factory=datetime.now, description="生成时间")
```

### 2.3 连接器模型 (ConnectorConfig)
```python
class ConnectorStatus(str, Enum):
    """连接器状态枚举"""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"

class ConnectorConfig(BaseModel):
    """连接器配置模型"""
    id: str = Field(..., description="连接器唯一标识")
    name: str = Field(..., description="连接器名称")
    type: str = Field(..., description="连接器类型")
    version: str = Field(..., description="版本号")
    status: ConnectorStatus = Field(..., description="运行状态")
    enabled: bool = Field(True, description="是否启用")
    config: Dict[str, Any] = Field(default_factory=dict, description="配置参数")
```

## 3. IPC路由处理器

### 3.1 实体管理路由

```python
# IPC路由处理器示例
from typing import List, Optional, Dict, Any

def handle_get_entities(
    type: Optional[str] = None,
    tags: Optional[List[str]] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """获取实体列表 - IPC处理器"""
    # IPC处理逻辑
    return {"status_code": 200, "data": []}

def handle_get_entity(entity_id: str) -> Dict[str, Any]:
    """获取指定实体 - IPC处理器"""
    return {"status_code": 200, "data": {}}

def handle_create_entity(entity_data: Dict[str, Any]) -> Dict[str, Any]:
    """创建新实体 - IPC处理器"""
    return {"status_code": 201, "data": {}}

def handle_update_entity(entity_id: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
    """更新实体 - IPC处理器"""
    return {"status_code": 200, "data": {}}

def handle_delete_entity(entity_id: str) -> Dict[str, Any]:
    """删除实体 - IPC处理器"""
    return {"status_code": 204, "data": None}

def handle_get_entity_relationships(entity_id: str) -> Dict[str, Any]:
    """获取实体关系 - IPC处理器"""
    return {"status_code": 200, "data": []}
```

### 3.2 推荐系统路由
```python
def handle_get_recommendations(
    type: Optional[str] = None,
    limit: int = 10,
    min_score: float = 0.0
) -> Dict[str, Any]:
    """获取推荐列表 - IPC处理器"""
    return {"status_code": 200, "data": []}

def handle_submit_recommendation_feedback(
    rec_id: str,
    feedback: Dict[str, Any]
) -> Dict[str, Any]:
    """提交推荐反馈 - IPC处理器"""
    return {"status_code": 200, "data": {"message": "反馈已记录"}}

def handle_generate_recommendations(
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """生成新推荐 - IPC处理器"""
    return {"status_code": 200, "data": []}
```

### 3.3 连接器管理路由
```python
def handle_get_connectors() -> Dict[str, Any]:
    """获取所有连接器 - IPC处理器"""
    return {"status_code": 200, "data": []}

def handle_get_connector(connector_id: str) -> Dict[str, Any]:
    """获取指定连接器 - IPC处理器"""
    return {"status_code": 200, "data": {}}

def handle_start_connector(connector_id: str) -> Dict[str, Any]:
    """启动连接器 - IPC处理器"""
    return {"status_code": 200, "data": {"message": "连接器启动成功"}}

def handle_stop_connector(connector_id: str) -> Dict[str, Any]:
    """停止连接器 - IPC处理器"""
    return {"status_code": 200, "data": {"message": "连接器停止成功"}}

def handle_update_connector_config(
    connector_id: str, 
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """更新连接器配置 - IPC处理器"""
    return {"status_code": 200, "data": {"message": "配置更新成功"}}

def handle_get_connector_logs(
    connector_id: str,
    lines: int = 100
) -> Dict[str, Any]:
    """获取连接器日志 - IPC处理器"""
    return {"status_code": 200, "data": {"logs": []}}
```

## 4. 响应格式标准

### 4.1 成功响应
```python
class APIResponse(BaseModel):
    """标准API响应格式"""
    success: bool = True
    data: Any = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": {"id": "entity_123", "name": "example.txt"},
                "message": "Entity created successfully",
                "timestamp": "2025-08-08T10:30:00Z"
            }
        }
```

### 4.2 错误响应
```python
class APIError(BaseModel):
    """标准错误响应格式"""
    success: bool = False
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "error_code": "ENTITY_NOT_FOUND",
                "error_message": "The requested entity does not exist",
                "details": {"entity_id": "entity_invalid123"},
                "timestamp": "2025-08-08T10:30:00Z"
            }
        }

# IPC状态码使用
IPC_STATUS_CODES = {
    200: "OK - 请求成功",
    201: "Created - 资源创建成功", 
    204: "No Content - 操作成功，无返回内容",
    400: "Bad Request - 请求参数错误",
    404: "Not Found - 资源不存在",
    409: "Conflict - 资源冲突",
    422: "Unprocessable Entity - 数据验证失败",
    500: "Internal Server Error - 服务器内部错误"
}
```

## 5. IPC客户端集成指南

详细的IPC客户端实现和使用指南，请参考：**[IPC客户端使用指南](./ipc_client_usage_guide.md)**

该指南包含：
- **Python IPC客户端**: 完整实现和使用示例
- **Flutter/Dart IPC客户端**: 跨平台UI集成方案
- **错误处理机制**: 自动重连和容错处理
- **性能优化**: 连接池和批量请求
- **跨平台支持**: Unix Socket + Windows Named Pipe
- **调试工具**: 监控和性能分析

## 6. Flutter数据模型映射

### 6.1 Dart模型定义
```dart
// lib/models/entity.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'entity.freezed.dart';
part 'entity.g.dart';

enum EntityType {
  @JsonValue('file')
  file,
  @JsonValue('clipboard')
  clipboard,
  @JsonValue('url')
  url,
  @JsonValue('note')
  note,
}

@freezed
class Entity with _$Entity {
  const factory Entity({
    required String id,
    required EntityType type,
    required String name,
    String? content,
    String? summary,
    @Default({}) Map<String, dynamic> metadata,
    @Default([]) List<String> tags,
    String? sourcePath,
    int? fileSize,
    String? mimeType,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _Entity;

  factory Entity.fromJson(Map<String, dynamic> json) => _$EntityFromJson(json);
}

@freezed
class Recommendation with _$Recommendation {
  const factory Recommendation({
    required String id,
    required String title,
    required String description,
    required RecommendationType type,
    required double score,
    required double confidence,
    required DateTime createdAt,
  }) = _Recommendation;

  factory Recommendation.fromJson(Map<String, dynamic> json) => 
    _$RecommendationFromJson(json);
}
```

### 6.2 IPC客户端服务

详细实现请参考 [IPC客户端使用指南](./ipc_client_usage_guide.md) 中的Flutter/Dart章节。

## 7. 性能基准与监控

### 7.1 性能指标

- **IPC连接建立**: < 5ms
- **消息序列化**: JSON编码/解码 < 0.1ms
- **Socket通信**: 往返时间 < 0.5ms  
- **总请求延迟**: < 1ms (vs HTTP的5-15ms)
- **并发处理**: 支持1000+并发连接

### 7.2 监控与调试

```python
# 启用IPC调试日志
import logging
logging.getLogger("ipc").setLevel(logging.DEBUG)

# 性能监控
from daemon.services.ipc_middleware import PerformanceMiddleware
```

## 8. 协议版本控制

### 8.1 版本管理策略

```python
# IPC协议版本管理
IPC_PROTOCOL_VERSION = "2.0.0"
SUPPORTED_VERSIONS = ["1.0.0", "2.0.0"]

class ProtocolVersioning:
    @staticmethod
    def negotiate_version(client_version: str) -> str:
        """协商协议版本"""
        if client_version in SUPPORTED_VERSIONS:
            return client_version
        return "1.0.0"  # 回退到兼容版本
```

### 8.2 向后兼容性

- **消息格式**: 新字段可选，旧字段保留
- **路径兼容**: 旧API路径继续支持  
- **渐进迁移**: 客户端可选择升级时机

---

**IPC消息协议设计完成**: 该文档提供了完整的IPC通信标准，实现高性能、安全的本地进程间通信。

**文档版本**: 2.0  
**创建时间**: 2025-08-02  
**最新更新**: 2025-08-08  
**维护团队**: IPC协议组