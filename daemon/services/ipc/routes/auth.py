"""
认证路由

处理IPC客户端的认证和授权
"""

import logging
import os

from ..core.protocol import IPCErrorCode, IPCRequest, IPCResponse
from ..core.router import IPCRouter

logger = logging.getLogger(__name__)


def create_auth_router() -> IPCRouter:
    """创建认证路由"""
    router = IPCRouter()

    @router.post("/auth/handshake")
    async def auth_handshake(request: IPCRequest) -> IPCResponse:
        """安全认证握手处理 - 修复认证绕过漏洞"""
        try:
            # 🔐 获取IPC安全管理器进行真正的身份验证
            from core.container import get_container

            from ..core.security import IPCSecurityManager

            container = get_container()
            security_manager = container.get_service(IPCSecurityManager)

            # 从请求中提取客户端声明的PID
            claimed_client_pid = request.data.get("client_pid")
            if claimed_client_pid is None:
                logger.warning("认证请求缺少client_pid字段")
                return IPCResponse.error_response(
                    IPCErrorCode.INVALID_REQUEST,
                    "Missing client_pid in authentication request",
                    {"required_field": "client_pid"},
                    request_id=request.request_id,
                )

            # 🚨 获取PID验证信息 - 使用增强的可信度评估机制
            real_client_pid_str = request.get_header("x-real-client-pid")
            pid_source = request.get_header("x-pid-source", "client_declared")
            pid_confidence = request.get_header("x-pid-confidence", "unknown")

            if real_client_pid_str:
                # 有服务器验证的真实PID
                try:
                    real_client_pid = int(real_client_pid_str)

                    # 检查客户端声明的PID与服务器验证的PID是否一致
                    if claimed_client_pid != real_client_pid:
                        # 如果是高可信度来源，这表明可能存在PID欺骗
                        if pid_confidence in ["high", "medium"]:
                            logger.error(
                                f"高可信度PID欺骗检测: 声明={claimed_client_pid}, 验证={real_client_pid}, 来源={pid_source}"
                            )
                            return IPCResponse.error_response(
                                IPCErrorCode.AUTH_REQUIRED,
                                "Client PID mismatch - potential spoofing attack detected",
                                {
                                    "claimed_pid": claimed_client_pid,
                                    "verified_pid": real_client_pid,
                                    "pid_source": pid_source,
                                    "confidence": pid_confidence,
                                    "security_issue": "High confidence PID verification failed",
                                },
                                request_id=request.request_id,
                            )
                        else:
                            # 低可信度时，记录warning但允许继续（使用验证的PID）
                            logger.warning(
                                f"低可信度PID不一致: 声明={claimed_client_pid}, 验证={real_client_pid}, 来源={pid_source}"
                            )

                    # 使用服务器验证的PID
                    authenticated_pid = real_client_pid

                except ValueError:
                    logger.error(f"无效的客户端PID格式: {real_client_pid_str}")
                    return IPCResponse.error_response(
                        IPCErrorCode.INVALID_REQUEST,
                        "Invalid verified client PID format",
                        request_id=request.request_id,
                    )
            else:
                # 服务器无法验证PID，使用客户端声明的PID进行基本验证
                logger.debug(f"使用客户端声明的PID进行基本验证: {claimed_client_pid}")

                # 基本验证：检查进程是否存在
                try:
                    import psutil

                    if not psutil.pid_exists(claimed_client_pid):
                        logger.error(f"声明的客户端PID不存在: {claimed_client_pid}")
                        return IPCResponse.error_response(
                            IPCErrorCode.AUTH_REQUIRED,
                            "Claimed client process does not exist",
                            {"claimed_pid": claimed_client_pid},
                            request_id=request.request_id,
                        )
                except ImportError:
                    logger.debug("psutil不可用，跳过PID存在性检查")

                # 使用声明的PID，但标记为低可信度
                authenticated_pid = claimed_client_pid
                pid_confidence = "low"
                pid_source = "client_declared"

            # ✅ 使用增强的安全管理器进行进程身份验证
            connection_id = f"auth_{authenticated_pid}_{request.request_id}"
            authenticated = security_manager.authenticate_connection(
                connection_id, authenticated_pid, pid_confidence, pid_source
            )

            if authenticated:
                server_pid = os.getpid()
                is_internal = authenticated_pid == server_pid

                # 确定安全级别
                if pid_confidence in ["high", "medium"] and pid_source in [
                    "SO_PEERCRED",
                    "LOCAL_PEERPID",
                ]:
                    security_level = "verified"
                elif pid_confidence == "low" or pid_source in [
                    "client_declared",
                    "psutil_scan",
                ]:
                    security_level = "basic"
                else:
                    security_level = "unknown"

                logger.info(
                    f"✅ IPC客户端认证成功: PID={authenticated_pid}, internal={is_internal}, 安全级别={security_level}, 来源={pid_source}"
                )
                return IPCResponse.success_response(
                    data={
                        "authenticated": True,
                        "message": "Secure authentication successful",
                        "server_pid": server_pid,
                        "client_type": "internal" if is_internal else "external",
                        "security_level": security_level,
                        "pid_source": pid_source,
                        "pid_confidence": pid_confidence,
                        "verified_pid": authenticated_pid,
                    },
                    request_id=request.request_id,
                )
            else:
                logger.warning(
                    f"❌ IPC客户端认证失败: PID={authenticated_pid}, 来源={pid_source}, 可信度={pid_confidence}"
                )
                return IPCResponse.error_response(
                    IPCErrorCode.AUTH_REQUIRED,
                    "Authentication failed - unable to verify client process",
                    {
                        "client_pid": authenticated_pid,
                        "pid_source": pid_source,
                        "pid_confidence": pid_confidence,
                        "security_check": "Process verification failed",
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
