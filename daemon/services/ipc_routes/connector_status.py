"""
连接器状态和心跳管理路由
处理连接器的状态更新和心跳请求
"""

import logging
from datetime import datetime, timezone

from core.service_facade import get_service
from models.database_models import Connector
from services.database_service import DatabaseService

from ..ipc_protocol import IPCRequest, IPCResponse
from ..ipc_router import IPCRouter

logger = logging.getLogger(__name__)


def create_connector_status_router() -> IPCRouter:
    """创建连接器状态管理路由"""
    router = IPCRouter(prefix="/connectors")

    @router.post("/{connector_id}/status")
    async def update_connector_status(request: IPCRequest) -> IPCResponse:
        """
        更新连接器状态

        请求格式：
        {
            "status": "starting|running|stopping|stopped|error",
            "message": "状态消息",
            "metadata": {}
        }
        """
        try:
            connector_id = request.path_params.get("connector_id")
            if not connector_id:
                return IPCResponse.error_response(
                    "INVALID_REQUEST", "Missing connector_id"
                )

            data = request.data or {}
            status = data.get("status", "unknown")
            message = data.get("message", "")
            data.get("metadata", {})

            db_service = get_service(DatabaseService)

            with db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )

                if not connector:
                    return IPCResponse.error_response(
                        "CONNECTOR_NOT_FOUND", f"Connector {connector_id} not found"
                    )

                # 更新连接器状态
                connector.status = status
                connector.last_activity = (
                    message if message else connector.last_activity
                )
                connector.updated_at = datetime.now(timezone.utc)

                # 如果包含错误信息
                if status == "error" and "error" in data:
                    connector.error_message = data["error"].get("message")
                    connector.error_code = data["error"].get("code")
                elif status != "error":
                    # 清除错误信息
                    connector.error_message = None
                    connector.error_code = None

                session.commit()

            logger.info(f"连接器状态已更新: {connector_id} -> {status}")

            return IPCResponse.success_response(
                {
                    "connector_id": connector_id,
                    "status": status,
                    "message": f"Status updated to {status}",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        except Exception as e:
            logger.error(f"更新连接器状态失败: {e}")
            return IPCResponse.error_response(
                "INTERNAL_ERROR", f"Failed to update status: {str(e)}"
            )

    @router.post("/{connector_id}/heartbeat")
    async def connector_heartbeat(request: IPCRequest) -> IPCResponse:
        """
        连接器心跳

        请求格式：
        {
            "timestamp": "2025-08-12T12:00:00Z",
            "status": "alive",
            "metadata": {}
        }
        """
        try:
            connector_id = request.path_params.get("connector_id")
            if not connector_id:
                return IPCResponse.error_response(
                    "INVALID_REQUEST", "Missing connector_id"
                )

            data = request.data or {}
            data.get("timestamp", datetime.now(timezone.utc).isoformat())
            data.get("status", "alive")
            data.get("metadata", {})

            db_service = get_service(DatabaseService)

            with db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )

                if not connector:
                    return IPCResponse.error_response(
                        "CONNECTOR_NOT_FOUND", f"Connector {connector_id} not found"
                    )

                # 更新心跳信息
                connector.last_heartbeat = datetime.now(timezone.utc)
                connector.updated_at = datetime.now(timezone.utc)

                # 如果连接器状态不是running，更新为running
                if connector.status in ["starting", "stopped"]:
                    connector.status = "running"

                session.commit()

            logger.debug(f"连接器心跳已记录: {connector_id}")

            return IPCResponse.success_response(
                {
                    "status": "alive",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "connector_id": connector_id,
                    "message": "Heartbeat received",
                }
            )

        except Exception as e:
            logger.error(f"连接器心跳处理失败: {e}")
            return IPCResponse.error_response(
                "INTERNAL_ERROR", f"Failed to process heartbeat: {str(e)}"
            )

    @router.get("/{connector_id}/status")
    async def get_connector_status(request: IPCRequest) -> IPCResponse:
        """获取连接器状态"""
        try:
            connector_id = request.path_params.get("connector_id")
            if not connector_id:
                return IPCResponse.error_response(
                    "INVALID_REQUEST", "Missing connector_id"
                )

            db_service = get_service(DatabaseService)

            with db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )

                if not connector:
                    return IPCResponse.error_response(
                        "CONNECTOR_NOT_FOUND", f"Connector {connector_id} not found"
                    )

                status_info = {
                    "connector_id": connector_id,
                    "name": connector.name,
                    "status": connector.status,
                    "enabled": connector.enabled,
                    "process_id": connector.process_id,
                    "last_heartbeat": (
                        connector.last_heartbeat.isoformat()
                        if connector.last_heartbeat
                        else None
                    ),
                    "last_activity": connector.last_activity,
                    "data_count": connector.data_count,
                    "error_message": connector.error_message,
                    "error_code": connector.error_code,
                    "updated_at": (
                        connector.updated_at.isoformat()
                        if connector.updated_at
                        else None
                    ),
                }

            return IPCResponse.success_response(status_info)

        except Exception as e:
            logger.error(f"获取连接器状态失败: {e}")
            return IPCResponse.error_response(
                "INTERNAL_ERROR", f"Failed to get status: {str(e)}"
            )

    return router
