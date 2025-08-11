"""
健康检查路由

提供系统健康检查和基础服务信息
"""

import logging
from datetime import datetime

from ..ipc_protocol import IPCRequest, IPCResponse
from ..ipc_router import IPCRouter

logger = logging.getLogger(__name__)


def create_health_router() -> IPCRouter:
    """创建健康检查路由"""
    router = IPCRouter()

    @router.get("/")
    async def root(request: IPCRequest) -> IPCResponse:
        """根路径"""
        return IPCResponse.success_response(
            data={
                "message": "Linch Mind IPC Service V2",
                "version": "2.0.0",
                "status": "running",
                "protocol": "pure_ipc",
            },
            request_id=request.request_id,
        )

    @router.get("/health")
    async def health_check(request: IPCRequest) -> IPCResponse:
        """健康检查"""
        return IPCResponse.success_response(
            data={
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "linch-mind-daemon",
                "protocol_version": "2.0",
            },
            request_id=request.request_id,
        )

    @router.get("/server/info")
    async def server_info(request: IPCRequest) -> IPCResponse:
        """服务器信息"""
        import os
        import platform

        return IPCResponse.success_response(
            data={
                "pid": os.getpid(),
                "platform": platform.system(),
                "python_version": platform.python_version(),
                "architecture": platform.machine(),
                "communication": "Pure IPC",
                "protocol_version": "2.0",
            },
            request_id=request.request_id,
        )

    @router.post("/heartbeat")
    async def heartbeat(request: IPCRequest) -> IPCResponse:
        """连接器心跳检查"""
        try:
            data = request.data or {}
            connector_id = data.get("connector_id", "unknown")

            logger.debug(f"收到连接器心跳: {connector_id}")

            return IPCResponse.success_response(
                data={
                    "status": "alive",
                    "timestamp": datetime.now().isoformat(),
                    "connector_id": connector_id,
                    "message": "Heartbeat received",
                },
                request_id=request.request_id,
            )
        except Exception as e:
            logger.error(f"处理心跳请求时发生错误: {e}")
            return IPCResponse.error_response(
                error_code="INTERNAL_ERROR",
                message=f"Heartbeat processing failed: {str(e)}",
                request_id=request.request_id,
            )

    return router
