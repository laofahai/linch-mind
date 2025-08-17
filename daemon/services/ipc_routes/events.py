"""
通用事件处理路由 - 与连接器类型无关的事件API
所有连接器使用相同的通用事件接口
"""

import asyncio
import logging
from datetime import datetime

from ..ipc_protocol import IPCRequest, IPCResponse
from ..ipc_router import IPCRouter
from .generic_event_storage import get_generic_event_storage
from .event_validator import get_event_validator, ValidationSeverity

logger = logging.getLogger(__name__)


def create_events_router() -> IPCRouter:
    """创建通用事件处理路由"""
    router = IPCRouter(prefix="/events")

    @router.post("/submit")
    async def handle_generic_event(request: IPCRequest) -> IPCResponse:
        """
        处理通用连接器事件 - 与连接器类型无关

        请求格式：
        {
            "connector_id": "any_connector_id",
            "event_type": "任意事件类型",
            "event_data": {
                "任意键值对数据": "连接器自定义格式"
            },
            "timestamp": "2025-08-10T19:00:00Z",
            "metadata": {
                "任意元数据": "连接器自定义"
            }
        }
        """
        try:
            data = request.data or {}

            # 验证必需字段（通用字段）
            required_fields = ["connector_id", "event_type", "event_data", "timestamp"]
            for field in required_fields:
                if field not in data or data[field] is None:
                    return IPCResponse.error_response(
                        "INVALID_REQUEST", f"Missing or null required field: {field}"
                    )
            
            connector_id = data["connector_id"]
            event_type = data["event_type"] 
            event_data = data["event_data"]
            timestamp = data["timestamp"]
            metadata = data.get("metadata", {})
            
            # 🛡️ 深度验证机制：使用专用验证器
            validator = get_event_validator()
            validation_result = validator.validate_event(
                connector_id, event_type, event_data, timestamp, metadata
            )
            
            if not validation_result.is_valid:
                if validation_result.severity == ValidationSeverity.ERROR:
                    return IPCResponse.error_response(
                        validation_result.error_code, 
                        f"{validation_result.message}. Suggestions: {'; '.join(validation_result.suggestions)}"
                    )
                elif validation_result.severity == ValidationSeverity.WARNING:
                    logger.warning(f"事件验证警告: {validation_result.message} - {connector_id}/{event_type}")
                # CRITICAL级别的错误也拒绝处理
                elif validation_result.severity == ValidationSeverity.CRITICAL:
                    logger.error(f"严重验证错误: {validation_result.message} - {connector_id}/{event_type}")
                    return IPCResponse.error_response(
                        validation_result.error_code,
                        f"Critical validation error: {validation_result.message}"
                    )

            logger.info(
                f"📡 Processing generic event from {connector_id}: {event_type}"
            )

            # 使用通用存储处理（连接器无关）
            storage = get_generic_event_storage()
            asyncio.create_task(
                storage.store_generic_event(
                    connector_id, event_type, event_data, timestamp, metadata
                )
            )

            return IPCResponse.success_response(
                {
                    "message": "Event queued for processing",
                    "event_id": f"{connector_id}_{datetime.now().isoformat()}_{hash(str(event_data)) % 10000}",
                }
            )

        except Exception as e:
            logger.error(f"Error handling generic event: {str(e)}")
            return IPCResponse.error_response(
                "INTERNAL_ERROR", f"Failed to process event: {str(e)}"
            )

    @router.post("/submit_batch")
    async def handle_generic_batch_events(request: IPCRequest) -> IPCResponse:
        """
        处理通用连接器批量事件 - 与连接器类型无关
        
        请求格式：
        {
            "connector_id": "any_connector_id", 
            "events": [
                {
                    "event_type": "事件类型",
                    "event_data": {"数据": "值"},
                    "timestamp": "2025-08-15T19:00:00Z",
                    "metadata": {"额外元数据": "值"}
                },
                // ... 更多事件
            ]
        }
        """
        try:
            data = request.data or {}
            
            # 验证必需字段
            if "connector_id" not in data:
                return IPCResponse.error_response(
                    "INVALID_REQUEST", "Missing required field: connector_id"
                )
            
            if "events" not in data or not isinstance(data["events"], list):
                return IPCResponse.error_response(
                    "INVALID_REQUEST", "Missing or invalid events array"
                )
            
            connector_id = data["connector_id"]
            events = data["events"]
            
            if not events:
                return IPCResponse.success_response({
                    "message": "No events to process",
                    "processed_count": 0
                })
            
            logger.info(f"📦 Processing batch of {len(events)} events from {connector_id}")
            
            # 获取存储服务
            storage = get_generic_event_storage()
            processed_count = 0
            
            # 处理每个事件
            for event in events:
                try:
                    # 验证单个事件的必需字段
                    required_fields = ["event_type", "event_data", "timestamp"]
                    for field in required_fields:
                        if field not in event:
                            logger.warning(f"Skipping event missing field: {field}")
                            continue
                    
                    event_type = event["event_type"]
                    event_data = event["event_data"] 
                    timestamp = event["timestamp"]
                    metadata = event.get("metadata", {})
                    
                    # 异步存储事件
                    asyncio.create_task(
                        storage.store_generic_event(
                            connector_id, event_type, event_data, timestamp, metadata
                        )
                    )
                    processed_count += 1
                    
                except Exception as e:
                    logger.warning(f"Error processing individual event: {str(e)}")
                    continue
            
            return IPCResponse.success_response({
                "message": f"Batch processed: {processed_count}/{len(events)} events queued",
                "processed_count": processed_count,
                "total_count": len(events)
            })
            
        except Exception as e:
            logger.error(f"Error handling batch events: {str(e)}")
            return IPCResponse.error_response(
                "INTERNAL_ERROR", f"Failed to process batch events: {str(e)}"
            )

    return router
