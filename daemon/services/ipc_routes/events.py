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
                if field not in data:
                    return IPCResponse.error_response(
                        "INVALID_REQUEST", f"Missing required field: {field}"
                    )

            connector_id = data["connector_id"]
            event_type = data["event_type"]
            event_data = data["event_data"]
            timestamp = data["timestamp"]
            metadata = data.get("metadata", {})

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

    return router
