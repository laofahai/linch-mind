# AI驱动事件关联API参考

## 概述

AI驱动事件关联系统提供基于Ollama AI的智能事件分析服务，完全摆脱硬编码规则，实现真正的智能语义理解和工作流模式识别。

## 基础信息

- **API前缀**: `/ai/`
- **协议**: IPC (Unix Socket/Named Pipe)
- **AI引擎**: Ollama (默认模型: qwen2.5:0.5b)
- **响应格式**: JSON

## API端点

### 1. 事件AI分析

**端点**: `/ai/analyze-event`
**方法**: POST
**描述**: 使用AI分析单个事件的语义含义和特征

#### 请求参数
```json
{
  "event_data": {
    "event_type": "string",
    "connector_id": "string", 
    "timestamp": "ISO8601",
    "event_data": {
      "file_path": "string",
      "action": "string",
      "content": "string"
    }
  },
  "include_suggestions": true
}
```

#### 响应格式
```json
{
  "success": true,
  "semantic_tags": [
    {
      "key": "string",
      "name": "string",
      "description": "string", 
      "confidence": 0.85,
      "reasoning": "string"
    }
  ],
  "correlations": [
    {
      "pattern_name": "string",
      "pattern_description": "string",
      "confidence": 0.80,
      "reasoning": "string",
      "suggested_actions": ["string"]
    }
  ],
  "processing_success": true,
  "ai_insights": true
}
```

### 2. 行为洞察生成

**端点**: `/ai/behavior-insights`
**方法**: POST
**描述**: 生成基于历史事件的AI行为洞察报告

#### 请求参数
```json
{
  "time_range_hours": 24
}
```

#### 响应格式
```json
{
  "success": true,
  "insights": [
    {
      "category": "string",
      "description": "string",
      "confidence": 0.75
    }
  ],
  "summary": "string",
  "recommendations": ["string"]
}
```

### 3. 模式发现

**端点**: `/ai/discover-patterns`
**方法**: POST
**描述**: 发现指定时间窗口内的事件关联模式

#### 请求参数
```json
{
  "time_window_minutes": 10,
  "confidence_threshold": 0.7
}
```

#### 响应格式
```json
{
  "success": true,
  "patterns": [
    {
      "pattern_id": "string",
      "name": "string", 
      "description": "string",
      "confidence": 0.80,
      "event_count": 5,
      "time_span": "string"
    }
  ],
  "total_events_analyzed": 15
}
```

### 4. AI对话

**端点**: `/ai/correlation-chat`
**方法**: POST
**描述**: 与AI进行关于事件关联和模式的自然语言对话

#### 请求参数
```json
{
  "user_message": "string",
  "context": {
    "conversation_id": "string",
    "previous_patterns": ["string"]
  }
}
```

#### 响应格式
```json
{
  "success": true,
  "user_message": "string",
  "ai_response": "string",
  "response_type": "conversational",
  "context_used": true,
  "conversation_id": "string"
}
```

### 5. 模式解释

**端点**: `/ai/explain-pattern`
**方法**: POST
**描述**: AI解释特定关联模式的含义和价值

#### 请求参数
```json
{
  "pattern_name": "string",
  "user_question": "string"
}
```

#### 响应格式
```json
{
  "success": true,
  "explanation": "string",
  "pattern_found": true
}
```

### 6. 学习反馈

**端点**: `/ai/learn-feedback`
**方法**: POST
**描述**: 提供用户反馈，帮助AI改进模式识别

#### 请求参数
```json
{
  "pattern_name": "string",
  "feedback": "string",
  "rating": 4.5
}
```

#### 响应格式
```json
{
  "success": true,
  "learning_applied": true,
  "feedback_processed": true
}
```

## 错误处理

所有API端点都遵循统一的错误响应格式：

```json
{
  "success": false,
  "error": "错误描述",
  "error_code": "ERROR_CODE",
  "details": {
    "additional_info": "string"
  }
}
```

### 常见错误码

- `AI_SERVICE_UNAVAILABLE`: Ollama AI服务不可用
- `INVALID_EVENT_DATA`: 事件数据格式错误
- `PROCESSING_TIMEOUT`: AI处理超时
- `INSUFFICIENT_DATA`: 数据不足以进行分析
- `PATTERN_NOT_FOUND`: 未找到指定模式

## 性能特征

- **初始化时间**: <151ms
- **事件缓冲**: >200万事件/秒理论吞吐量
- **AI分析**: 1-3秒（取决于Ollama响应）
- **内存占用**: <200KB基础，扩展性良好

## 使用示例

### Python客户端示例

```python
import asyncio
from services.ipc_client import IPCClient

async def analyze_file_event():
    client = IPCClient()
    
    event_data = {
        "event_type": "file_operation",
        "connector_id": "filesystem",
        "timestamp": "2025-08-18T09:00:00Z",
        "event_data": {
            "file_path": "/project/main.py",
            "action": "modified",
            "content": "def hello(): print('Hello AI!')"
        }
    }
    
    response = await client.request('POST', '/ai/analyze-event', data={
        'event_data': event_data,
        'include_suggestions': True
    })
    
    if response.status_code == 200:
        analysis = response.data
        print(f"语义标签: {len(analysis['semantic_tags'])}")
        for tag in analysis['semantic_tags']:
            print(f"- {tag['name']}: {tag['confidence']:.2f}")
```

## 配置要求

1. **Ollama服务**: 必须运行在配置的主机上
2. **AI模型**: 需要下载指定的语言模型
3. **网络连接**: AI分析需要访问Ollama API
4. **缓冲区**: 可配置事件缓冲区大小（默认100）

## 最佳实践

1. **批量处理**: 对于大量事件，考虑批量提交以提高效率
2. **缓存策略**: AI分析结果可以缓存以避免重复计算
3. **降级处理**: 当AI服务不可用时，系统应有降级方案
4. **反馈循环**: 定期提供用户反馈以改进AI准确性

---

*更新时间: 2025-08-18*
*版本: v1.0*