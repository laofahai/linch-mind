# IPC消息协议设计标准

**版本**: 2.0  
**状态**: 已实现  
**创建时间**: 2025-08-02  
**最新更新**: 2025-08-06  
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
    method: str = Field(..., description="HTTP方法 (GET/POST/PUT/DELETE)")
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
    status_code: int = Field(..., description="HTTP状态码")
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
    \"\"\"实体类型枚举\"\"\"
    FILE = \"file\"
    CLIPBOARD = \"clipboard\"
    URL = \"url\"
    NOTE = \"note\"
    EMAIL = \"email\"
    CHAT = \"chat\"

class Entity(LinchMindBaseModel):
    \"\"\"知识图谱实体模型\"\"\"
    id: str = Field(..., description=\"实体唯一标识\", example=\"entity_abc123\")
    type: EntityType = Field(..., description=\"实体类型\")
    name: str = Field(..., max_length=255, description=\"实体名称\")
    content: Optional[str] = Field(None, description=\"实体内容\")
    summary: Optional[str] = Field(None, max_length=500, description=\"AI生成摘要\")
    metadata: Dict[str, Any] = Field(default_factory=dict, description=\"扩展元数据\")
    tags: List[str] = Field(default_factory=list, description=\"标签列表\")
    source_path: Optional[str] = Field(None, description=\"来源路径\")
    file_size: Optional[int] = Field(None, ge=0, description=\"文件大小(字节)\")
    mime_type: Optional[str] = Field(None, description=\"MIME类型\")
    
    class Config:
        schema_extra = {
            \"example\": {
                \"id\": \"entity_doc123\",
                \"type\": \"file\",
                \"name\": \"project_proposal.md\",  
                \"content\": \"# Project Proposal\\n\\nThis document outlines...\",
                \"summary\": \"项目提案文档，包含目标、时间表和预算\",
                \"metadata\": {
                    \"file_path\": \"/Users/user/Documents/project_proposal.md\",
                    \"last_modified\": \"2025-08-02T10:30:00Z\",
                    \"word_count\": 1250
                },
                \"tags\": [\"project\", \"proposal\", \"business\"],
                \"source_path\": \"/Users/user/Documents/project_proposal.md\",
                \"file_size\": 5120,
                \"mime_type\": \"text/markdown\"
            }
        }

class EntityCreate(BaseModel):
    \"\"\"创建实体请求模型\"\"\"
    type: EntityType
    name: str = Field(..., max_length=255)
    content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    source_path: Optional[str] = None

class EntityUpdate(BaseModel):
    \"\"\"更新实体请求模型\"\"\"
    name: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    summary: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
```

### 2.2 关系模型 (Relationship)
```python
class RelationshipType(str, Enum):
    \"\"\"关系类型枚举\"\"\"
    REFERENCE = \"reference\"      # 引用关系
    SIMILARITY = \"similarity\"    # 相似关系  
    SEQUENCE = \"sequence\"        # 序列关系
    CATEGORY = \"category\"        # 分类关系
    DEPENDENCY = \"dependency\"    # 依赖关系
    AUTHORSHIP = \"authorship\"    # 作者关系

class Relationship(LinchMindBaseModel):
    \"\"\"实体关系模型\"\"\"
    id: str = Field(..., description=\"关系唯一标识\")
    source_id: str = Field(..., description=\"源实体ID\")
    target_id: str = Field(..., description=\"目标实体ID\")
    type: RelationshipType = Field(..., description=\"关系类型\")
    weight: float = Field(1.0, ge=0.0, le=1.0, description=\"关系权重\")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description=\"置信度\")
    metadata: Dict[str, Any] = Field(default_factory=dict, description=\"关系元数据\")
    
    class Config:
        schema_extra = {
            \"example\": {
                \"id\": \"rel_ref456\",
                \"source_id\": \"entity_doc123\", 
                \"target_id\": \"entity_doc789\",
                \"type\": \"reference\",
                \"weight\": 0.85,
                \"confidence\": 0.92,
                \"metadata\": {
                    \"extraction_method\": \"ai_analysis\",
                    \"context\": \"Both documents discuss the same project\"
                }
            }
        }
```

### 2.3 推荐模型 (Recommendation)
```python
class RecommendationType(str, Enum):
    \"\"\"推荐类型枚举\"\"\"
    SIMILAR_CONTENT = \"similar_content\"
    RELATED_TASK = \"related_task\"
    KNOWLEDGE_GAP = \"knowledge_gap\"
    WORKFLOW_OPTIMIZATION = \"workflow_optimization\"
    TRENDING_TOPIC = \"trending_topic\"

class Recommendation(LinchMindBaseModel):
    \"\"\"AI推荐模型\"\"\"
    id: str = Field(..., description=\"推荐ID\")
    title: str = Field(..., max_length=255, description=\"推荐标题\")
    description: str = Field(..., max_length=1000, description=\"推荐描述\")
    type: RecommendationType = Field(..., description=\"推荐类型\")
    score: float = Field(..., ge=0.0, le=1.0, description=\"推荐得分\")
    confidence: float = Field(..., ge=0.0, le=1.0, description=\"置信度\")
    reason: str = Field(..., description=\"推荐理由\")
    related_entities: List[str] = Field(default_factory=list, description=\"相关实体ID列表\")
    ai_explanation: Optional[str] = Field(None, description=\"AI生成解释\")
    action_url: Optional[str] = Field(None, description=\"操作链接\")
    priority: int = Field(1, ge=1, le=5, description=\"优先级(1-5)\")
    expires_at: Optional[datetime] = Field(None, description=\"过期时间\")
    
    class Config:
        schema_extra = {
            \"example\": {
                \"id\": \"rec_similar789\",
                \"title\": \"查看相关项目文档\",
                \"description\": \"基于您最近的工作，这些文档可能对您有帮助\",
                \"type\": \"similar_content\",
                \"score\": 0.87,
                \"confidence\": 0.82,
                \"reason\": \"检测到您在项目提案上的高频活动\",
                \"related_entities\": [\"entity_doc123\", \"entity_doc456\"],
                \"ai_explanation\": \"AI发现您正在处理项目相关文档，建议查看这些相关资料以获得更全面的视角\",
                \"action_url\": \"/entities/entity_doc456\",
                \"priority\": 3,
                \"expires_at\": \"2025-08-09T10:30:00Z\"
            }
        }
```

### 2.4 连接器模型 (Connector)
```python
class ConnectorStatus(str, Enum):
    \"\"\"连接器状态枚举\"\"\"
    STOPPED = \"stopped\"
    STARTING = \"starting\"
    RUNNING = \"running\"
    STOPPING = \"stopping\"
    ERROR = \"error\"
    MAINTENANCE = \"maintenance\"

class ConnectorType(str, Enum):
    \"\"\"连接器类型枚举\"\"\"
    FILESYSTEM = \"filesystem\"
    CLIPBOARD = \"clipboard\"
    BROWSER = \"browser\"
    EMAIL = \"email\"
    CHAT = \"chat\"
    DATABASE = \"database\"
    API = \"api\"

class ConnectorConfig(LinchMindBaseModel):
    \"\"\"连接器配置模型\"\"\"
    id: str = Field(..., description=\"连接器ID\")
    name: str = Field(..., max_length=255, description=\"连接器名称\")
    type: ConnectorType = Field(..., description=\"连接器类型\")
    version: str = Field(..., description=\"连接器版本\")
    description: Optional[str] = Field(None, max_length=500, description=\"描述\")
    enabled: bool = Field(False, description=\"是否启用\")
    status: ConnectorStatus = Field(ConnectorStatus.STOPPED, description=\"运行状态\")
    config: Dict[str, Any] = Field(default_factory=dict, description=\"配置参数\")
    statistics: Dict[str, Any] = Field(default_factory=dict, description=\"运行统计\")
    last_error: Optional[str] = Field(None, description=\"最后错误信息\")
    last_success_at: Optional[datetime] = Field(None, description=\"最后成功时间\")
    
    class Config:
        schema_extra = {
            \"example\": {
                \"id\": \"fs_connector_1\",
                \"name\": \"文件系统监控器\",
                \"type\": \"filesystem\",
                \"version\": \"1.0.0\",
                \"description\": \"监控指定目录的文件变化\",
                \"enabled\": True,
                \"status\": \"running\",
                \"config\": {
                    \"watch_paths\": [\"/Users/user/Documents\", \"/Users/user/Desktop\"],
                    \"file_extensions\": [\".md\", \".txt\", \".pdf\"],
                    \"ignore_patterns\": [\".*\", \"node_modules\", \".git\"],
                    \"scan_interval\": 5,
                    \"max_file_size\": 10485760
                },
                \"statistics\": {
                    \"files_monitored\": 150,
                    \"changes_detected\": 12,
                    \"errors_count\": 0,
                    \"uptime_seconds\": 86400,
                    \"data_collected_mb\": 2.5
                },
                \"last_success_at\": \"2025-08-02T10:25:00Z\"
            }
        }

class ConnectorCommand(BaseModel):
    \"\"\"连接器命令模型\"\"\"
    action: str = Field(..., description=\"操作类型\", example=\"start\")
    parameters: Dict[str, Any] = Field(default_factory=dict, description=\"操作参数\")
```

## 3. API端点设计

### 3.1 实体管理 API
```python
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

router = APIRouter(prefix=\"/api/v1/entities\", tags=[\"entities\"])

@router.get(\"/\", response_model=List[Entity])
async def get_entities(
    type: Optional[EntityType] = Query(None, description=\"按类型过滤\"),
    tags: Optional[List[str]] = Query(None, description=\"按标签过滤\"),
    search: Optional[str] = Query(None, description=\"搜索关键词\"),
    limit: int = Query(50, ge=1, le=100, description=\"返回数量限制\"),
    offset: int = Query(0, ge=0, description=\"偏移量\")
):
    \"\"\"获取实体列表\"\"\"
    pass

@router.get(\"/{entity_id}\", response_model=Entity)
async def get_entity(entity_id: str):
    \"\"\"获取指定实体\"\"\"
    pass

@router.post(\"/\", response_model=Entity, status_code=201)
async def create_entity(entity: EntityCreate):
    \"\"\"创建新实体\"\"\"
    pass

@router.put(\"/{entity_id}\", response_model=Entity)
async def update_entity(entity_id: str, entity: EntityUpdate):
    \"\"\"更新实体\"\"\"
    pass

@router.delete(\"/{entity_id}\", status_code=204)
async def delete_entity(entity_id: str):
    \"\"\"删除实体\"\"\"
    pass

@router.get(\"/{entity_id}/relationships\", response_model=List[Relationship])
async def get_entity_relationships(entity_id: str):
    \"\"\"获取实体关系\"\"\"
    pass
```

### 3.2 推荐系统 API
```python
@router.get(\"/api/v1/recommendations\", response_model=List[Recommendation])
async def get_recommendations(
    type: Optional[RecommendationType] = Query(None, description=\"推荐类型过滤\"),
    limit: int = Query(10, ge=1, le=50, description=\"返回数量\"),
    min_score: float = Query(0.0, ge=0.0, le=1.0, description=\"最低得分\")
):
    \"\"\"获取推荐列表\"\"\"
    pass

@router.post(\"/api/v1/recommendations/{rec_id}/feedback\")
async def submit_recommendation_feedback(
    rec_id: str,
    feedback: dict = Body(..., example={\"action\": \"liked\", \"comment\": \"很有帮助\"})
):
    \"\"\"提交推荐反馈\"\"\"
    pass

@router.post(\"/api/v1/recommendations/generate\")
async def generate_recommendations(
    user_context: dict = Body(..., example={\"recent_entities\": [\"entity_123\"]})
):
    \"\"\"生成新推荐\"\"\"
    pass
```

### 3.3 连接器管理 API
```python
@router.get(\"/api/v1/connectors\", response_model=List[ConnectorConfig])
async def get_connectors():
    \"\"\"获取所有连接器\"\"\"
    pass

@router.get(\"/api/v1/connectors/{connector_id}\", response_model=ConnectorConfig)
async def get_connector(connector_id: str):
    \"\"\"获取指定连接器\"\"\"
    pass

@router.post(\"/api/v1/connectors/{connector_id}/start\")
async def start_connector(connector_id: str):
    \"\"\"启动连接器\"\"\"
    pass

@router.post(\"/api/v1/connectors/{connector_id}/stop\")
async def stop_connector(connector_id: str):
    \"\"\"停止连接器\"\"\"
    pass

@router.put(\"/api/v1/connectors/{connector_id}/config\")
async def update_connector_config(
    connector_id: str, 
    config: Dict[str, Any] = Body(...)
):
    \"\"\"更新连接器配置\"\"\"
    pass

@router.get(\"/api/v1/connectors/{connector_id}/logs\")
async def get_connector_logs(
    connector_id: str,
    lines: int = Query(100, ge=1, le=1000, description=\"日志行数\")
):
    \"\"\"获取连接器日志\"\"\"
    pass
```

## 4. 响应格式标准

### 4.1 成功响应
```python
class APIResponse(BaseModel):
    \"\"\"标准API响应格式\"\"\"
    success: bool = True
    data: Any = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            \"example\": {
                \"success\": True,
                \"data\": {\"id\": \"entity_123\", \"name\": \"example.txt\"},
                \"message\": \"Entity created successfully\",
                \"timestamp\": \"2025-08-02T10:30:00Z\"
            }
        }
```

### 4.2 错误响应
```python
class APIError(BaseModel):
    \"\"\"标准错误响应格式\"\"\"
    success: bool = False
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            \"example\": {
                \"success\": False,
                \"error_code\": \"ENTITY_NOT_FOUND\",
                \"error_message\": \"The requested entity does not exist\",
                \"details\": {\"entity_id\": \"entity_invalid123\"},
                \"timestamp\": \"2025-08-02T10:30:00Z\"
            }
        }

# 标准HTTP状态码使用
HTTP_STATUS_CODES = {
    200: \"OK - 请求成功\",
    201: \"Created - 资源创建成功\", 
    204: \"No Content - 操作成功，无返回内容\",
    400: \"Bad Request - 请求参数错误\",
    401: \"Unauthorized - 未授权\",
    403: \"Forbidden - 禁止访问\",
    404: \"Not Found - 资源不存在\",
    409: \"Conflict - 资源冲突\",
    422: \"Unprocessable Entity - 数据验证失败\",
    500: \"Internal Server Error - 服务器内部错误\"
}
```

## 5. Mock服务实现

### 5.1 FastAPI Mock服务器
```python
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Optional

app = FastAPI(
    title=\"Linch Mind API\",
    description=\"个人AI生活助手 API\",
    version=\"1.0.0\",
    docs_url=\"/docs\",
    redoc_url=\"/redoc\"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[\"http://localhost:*\", \"http://127.0.0.1:*\"],
    allow_credentials=True,
    allow_methods=[\"*\"],
    allow_headers=[\"*\"],
)

# Mock数据生成器
class MockDataGenerator:
    def __init__(self):
        self.entities = self._generate_entities()
        self.recommendations = self._generate_recommendations()
        self.connectors = self._generate_connectors()
    
    def _generate_entities(self) -> List[Entity]:
        \"\"\"生成示例实体数据\"\"\"
        entities = []
        for i in range(20):
            entity = Entity(
                id=f\"entity_{i:03d}\",
                type=random.choice(list(EntityType)),
                name=f\"示例文档_{i}.md\",
                content=f\"这是第{i}个文档的内容...\",
                summary=f\"第{i}个文档的AI摘要\",
                metadata={
                    \"file_path\": f\"/Users/user/docs/doc_{i}.md\",
                    \"word_count\": random.randint(100, 2000),
                    \"last_accessed\": datetime.now().isoformat()
                },
                tags=[\"示例\", \"文档\", f\"类别{i%3}\"],
                file_size=random.randint(1024, 10240),
                mime_type=\"text/markdown\"
            )
            entities.append(entity)
        return entities
    
    def _generate_recommendations(self) -> List[Recommendation]:
        \"\"\"生成示例推荐数据\"\"\"
        recommendations = []
        for i in range(10):
            rec = Recommendation(
                id=f\"rec_{i:03d}\",
                title=f\"推荐项目 {i+1}\",
                description=f\"基于您的使用模式，推荐查看这个内容\",
                type=random.choice(list(RecommendationType)),
                score=random.uniform(0.6, 1.0),
                confidence=random.uniform(0.7, 0.95),
                reason=f\"检测到相关活动模式\",
                related_entities=[f\"entity_{random.randint(0,19):03d}\"],
                ai_explanation=f\"AI分析：这个推荐基于您最近的工作模式生成\",
                priority=random.randint(1, 5)
            )
            recommendations.append(rec)
        return recommendations
    
    def _generate_connectors(self) -> List[ConnectorConfig]:
        \"\"\"生成示例连接器数据\"\"\"
        connectors = [
            ConnectorConfig(
                id=\"filesystem_main\",
                name=\"文件系统监控\",
                type=ConnectorType.FILESYSTEM,
                version=\"1.0.0\",
                description=\"监控用户文档目录\",
                enabled=True,
                status=ConnectorStatus.RUNNING,
                config={
                    \"watch_paths\": [\"/Users/user/Documents\"],
                    \"file_extensions\": [\".md\", \".txt\"],
                    \"scan_interval\": 5
                },
                statistics={
                    \"files_monitored\": 150,
                    \"changes_detected\": 12,
                    \"uptime_seconds\": 86400
                }
            ),
            ConnectorConfig(
                id=\"clipboard_main\",
                name=\"剪贴板监控\",
                type=ConnectorType.CLIPBOARD,
                version=\"1.0.0\",
                description=\"监控剪贴板变化\",
                enabled=True,
                status=ConnectorStatus.RUNNING,
                config={\"history_size\": 100},
                statistics={
                    \"items_collected\": 45,
                    \"uptime_seconds\": 82800
                }
            )
        ]
        return connectors

# 创建Mock数据实例
mock_data = MockDataGenerator()

# API端点实现
@app.get(\"/api/v1/entities\", response_model=List[Entity])
async def get_entities(
    type: Optional[EntityType] = None,
    limit: int = 50,
    offset: int = 0
):
    \"\"\"获取实体列表\"\"\"
    await asyncio.sleep(0.1)  # 模拟网络延迟
    
    entities = mock_data.entities
    if type:
        entities = [e for e in entities if e.type == type]
    
    return entities[offset:offset+limit]

@app.get(\"/api/v1/entities/{entity_id}\", response_model=Entity)
async def get_entity(entity_id: str):
    \"\"\"获取指定实体\"\"\"
    await asyncio.sleep(0.05)
    
    entity = next((e for e in mock_data.entities if e.id == entity_id), None)
    if not entity:
        raise HTTPException(status_code=404, detail=\"Entity not found\")
    
    return entity

@app.get(\"/api/v1/recommendations\", response_model=List[Recommendation])
async def get_recommendations(
    limit: int = 10,
    min_score: float = 0.0
):
    \"\"\"获取推荐列表\"\"\"
    await asyncio.sleep(0.2)  # 模拟AI计算时间
    
    recs = [r for r in mock_data.recommendations if r.score >= min_score]
    return sorted(recs, key=lambda x: x.score, reverse=True)[:limit]

@app.get(\"/api/v1/connectors\", response_model=List[ConnectorConfig])
async def get_connectors():
    \"\"\"获取连接器列表\"\"\"
    await asyncio.sleep(0.1)
    return mock_data.connectors

@app.post(\"/api/v1/connectors/{connector_id}/start\")
async def start_connector(connector_id: str):
    \"\"\"启动连接器\"\"\"
    await asyncio.sleep(0.5)  # 模拟启动时间
    
    connector = next((c for c in mock_data.connectors if c.id == connector_id), None)
    if not connector:
        raise HTTPException(status_code=404, detail=\"Connector not found\")
    
    connector.status = ConnectorStatus.RUNNING
    connector.enabled = True
    
    return APIResponse(
        success=True,
        message=f\"Connector {connector_id} started successfully\"
    )

@app.get(\"/api/v1/health\")
async def health_check():
    \"\"\"健康检查\"\"\"
    return {
        \"status\": \"healthy\",
        \"timestamp\": datetime.now().isoformat(),
        \"version\": \"1.0.0\",
        \"mode\": \"mock\",
        \"services\": {
            \"api\": \"healthy\",
            \"database\": \"healthy\", 
            \"ai\": \"healthy\"
        }
    }

# 启动脚本
if __name__ == \"__main__\":
    import uvicorn
    uvicorn.run(
        app, 
        host=\"127.0.0.1\", 
        port=8000, 
        reload=True,
        log_level=\"info\"
    )
```

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
    required String type,
    required double score,
    required double confidence,
    required String reason,
    @Default([]) List<String> relatedEntities,
    String? aiExplanation,
    String? actionUrl,
    @Default(1) int priority,
    DateTime? expiresAt,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _Recommendation;

  factory Recommendation.fromJson(Map<String, dynamic> json) => 
      _$RecommendationFromJson(json);
}
```

### 6.2 HTTP客户端服务
```dart
// lib/services/daemon_client.dart
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/entity.dart';
import '../models/recommendation.dart';
import '../models/connector.dart';

class DaemonClient {
  final Dio _dio;
  
  DaemonClient({String baseUrl = 'http://127.0.0.1:8000'}) 
    : _dio = Dio(BaseOptions(
        baseUrl: '$baseUrl/api/v1',
        connectTimeout: const Duration(seconds: 5),
        receiveTimeout: const Duration(seconds: 10),
      )) {
    // 添加请求拦截器
    _dio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
    ));
  }

  // 实体相关API
  Future<List<Entity>> getEntities({
    EntityType? type,
    int limit = 50,
    int offset = 0,
  }) async {
    final response = await _dio.get('/entities', queryParameters: {
      if (type != null) 'type': type.name,
      'limit': limit,
      'offset': offset,
    });
    
    return (response.data as List)
        .map((json) => Entity.fromJson(json))
        .toList();
  }

  Future<Entity> getEntity(String id) async {
    final response = await _dio.get('/entities/$id');
    return Entity.fromJson(response.data);
  }

  // 推荐相关API
  Future<List<Recommendation>> getRecommendations({
    int limit = 10,
    double minScore = 0.0,
  }) async {
    final response = await _dio.get('/recommendations', queryParameters: {
      'limit': limit,
      'min_score': minScore,
    });
    
    return (response.data as List)
        .map((json) => Recommendation.fromJson(json))
        .toList();
  }

  // 连接器相关API
  Future<List<ConnectorConfig>> getConnectors() async {
    final response = await _dio.get('/connectors');
    return (response.data as List)
        .map((json) => ConnectorConfig.fromJson(json))
        .toList();
  }

  Future<void> startConnector(String connectorId) async {
    await _dio.post('/connectors/$connectorId/start');
  }

  Future<void> stopConnector(String connectorId) async {
    await _dio.post('/connectors/$connectorId/stop');
  }

  // 健康检查
  Future<Map<String, dynamic>> healthCheck() async {
    final response = await _dio.get('/health');
    return response.data;
  }
}

// Riverpod Provider
final daemonClientProvider = Provider<DaemonClient>((ref) {
  return DaemonClient();
});
```

## 7. IPC客户端集成

### 7.1 Dart/Flutter客户端

```dart
// lib/services/ipc_client.dart
import 'dart:io';
import 'dart:convert';
import 'dart:typed_data';

class IPCClient {
  Socket? _socket;
  String? _socketPath;
  
  Future<void> connect() async {
    // 发现daemon socket路径
    final configPath = '${Platform.environment['HOME']}/.linch-mind/daemon.info';
    final config = jsonDecode(await File(configPath).readAsString());
    _socketPath = config['socket_path'];
    
    // 连接Unix Socket
    _socket = await Socket.connect(
      InternetAddress(_socketPath!, type: InternetAddressType.unix),
      0,
    );
  }
  
  Future<Map<String, dynamic>> request(String method, String path, {
    Map<String, dynamic>? data,
    Map<String, String>? headers,
    Map<String, dynamic>? queryParams,
  }) async {
    final request = {
      'method': method,
      'path': path,
      'data': data,
      'headers': headers ?? {},
      'query_params': queryParams ?? {},
    };
    
    final jsonData = jsonEncode(request);
    final messageBytes = utf8.encode(jsonData);
    final lengthBytes = ByteData(4)..setUint32(0, messageBytes.length, Endian.big);
    
    // 发送消息
    _socket!.add(lengthBytes.buffer.asUint8List());
    _socket!.add(messageBytes);
    
    // 接收响应
    final response = await _readResponse();
    return response;
  }
}
```

### 7.2 Python客户端

```python
# 客户端示例
from daemon.services.ipc_client import IPCClient

async def main():
    async with IPCClient() as client:
        # GET请求
        response = await client.get("/api/v1/entities")
        print(f"Entities: {response['data']}")
        
        # POST请求  
        response = await client.post("/api/v1/entities", data={
            "type": "file",
            "name": "example.txt",
            "content": "Hello world"
        })
        print(f"Created: {response['data']}")
```

### 7.3 HTTP兼容层

```python
# 现有HTTP客户端代码无需修改
from daemon.services.compatibility_layer import get_http_client

async def legacy_code():
    # 这段代码完全不需要修改
    client = get_http_client()
    response = await client.get("/api/v1/entities")  
    data = response.json()
    # 底层自动使用IPC通信
```

## 8. 性能与监控

### 8.1 性能指标

- **消息序列化**: JSON编码/解码 < 0.1ms
- **Socket通信**: 往返时间 < 0.5ms  
- **总请求延迟**: < 1ms (vs HTTP的5-15ms)
- **并发处理**: 支持1000+并发连接

### 8.2 监控与调试

```python
# 启用IPC调试日志
import logging
logging.getLogger("ipc").setLevel(logging.DEBUG)

# 性能监控
from daemon.services.ipc_middleware import PerformanceMiddleware
app.add_middleware(PerformanceMiddleware())
```

## 9. 协议版本控制

### 9.1 版本管理策略

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

### 9.2 向后兼容性

- **消息格式**: 新字段可选，旧字段保留
- **路径兼容**: 旧API路径继续支持  
- **渐进迁移**: 客户端可选择升级时机

---

**IPC消息协议设计完成**: 该文档提供了完整的IPC通信标准，实现高性能、安全的本地进程间通信。

**文档版本**: 2.0  
**创建时间**: 2025-08-02  
**最新更新**: 2025-08-06  
**维护团队**: IPC协议组