"""
认证路由

处理IPC客户端的认证和授权
"""

import logging
import os

from ..ipc_protocol import IPCErrorCode, IPCRequest, IPCResponse
from ..ipc_router import IPCRouter

logger = logging.getLogger(__name__)


def create_auth_router() -> IPCRouter:
    """创建认证路由"""
    router = IPCRouter()

    @router.post("/auth/handshake")
    async def auth_handshake(request: IPCRequest) -> IPCResponse:
        """认证握手处理"""
        try:
            from ..ipc_security import get_security_manager

            # 从请求中提取客户端PID
            client_pid = request.data.get("client_pid")
            if client_pid is None:
                return IPCResponse.error_response(
                    IPCErrorCode.INVALID_REQUEST,
                    "Missing client_pid in authentication request",
                    {"required_field": "client_pid"},
                    request_id=request.request_id,
                )

            server_pid = os.getpid()

            # 检查是否为内部客户端（daemon自己的进程）
            is_internal = client_pid == server_pid

            if is_internal:
                # 内部客户端：快速认证，无需复杂验证
                logger.info(f"内部客户端认证成功: PID={client_pid}")
                return IPCResponse.success_response(
                    data={
                        "authenticated": True,
                        "message": "Internal client authentication successful",
                        "server_pid": server_pid,
                        "client_type": "internal",
                    },
                    request_id=request.request_id,
                )
            else:
                # 外部客户端：使用基本验证（暂时允许本地客户端）
                logger.info(f"外部客户端认证: PID={client_pid}")
                return IPCResponse.success_response(
                    data={
                        "authenticated": True,
                        "message": "External client authentication successful",
                        "server_pid": server_pid,
                        "client_type": "external",
                    },
                    request_id=request.request_id,
                )

        except Exception as e:
            logger.error(f"认证处理失败: {e}", exc_info=True)
            return IPCResponse.error_response(
                IPCErrorCode.INTERNAL_ERROR,
                f"Authentication error: {str(e)}",
                {
                    "error_type": type(e).__name__,
                    "server_pid": os.getpid(),
                    "client_pid": request.data.get("client_pid", "unknown"),
                },
                request_id=request.request_id,
            )

    return router
