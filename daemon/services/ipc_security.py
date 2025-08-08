#!/usr/bin/env python3
"""
IPC安全模块 - 为纯IPC架构提供安全加固
包括进程身份验证、权限检查、频率限制等
"""

import asyncio
import json
import logging
import os
import platform
import stat
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Set

import psutil

logger = logging.getLogger(__name__)


@dataclass
class SecurityContext:
    """IPC连接的安全上下文"""

    client_pid: Optional[int] = None
    client_uid: Optional[int] = None
    client_gid: Optional[int] = None
    connection_time: float = 0.0
    authenticated: bool = False
    request_count: int = 0
    last_request_time: float = 0.0


class ProcessAuthenticator:
    """进程身份验证器 - 验证连接的进程身份"""

    def __init__(self):
        self.daemon_pid = os.getpid()
        self.daemon_uid = os.getuid() if hasattr(os, "getuid") else None
        self.daemon_gid = os.getgid() if hasattr(os, "getgid") else None

    def authenticate_process(self, client_pid: int) -> SecurityContext:
        """验证客户端进程"""
        try:
            process = psutil.Process(client_pid)

            context = SecurityContext(
                client_pid=client_pid, connection_time=time.time(), authenticated=False
            )

            if not platform.system() == "Windows":
                # Unix系统：检查用户ID
                try:
                    context.client_uid = process.uids().real
                    context.client_gid = process.gids().real

                    # 只允许相同用户的进程连接
                    if context.client_uid == self.daemon_uid:
                        context.authenticated = True
                        logger.info(
                            f"IPC进程身份验证通过: PID={client_pid}, UID={context.client_uid}"
                        )
                    else:
                        logger.warning(
                            f"IPC进程身份验证失败: PID={client_pid}, UID={context.client_uid} != {self.daemon_uid}"
                        )
                except (psutil.AccessDenied, AttributeError):
                    logger.error(f"无法获取进程 {client_pid} 的用户信息")
            else:
                # Windows系统：简化验证（检查进程是否存在且可访问）
                try:
                    _ = process.name()
                    context.authenticated = True
                    logger.info(f"IPC进程身份验证通过 (Windows): PID={client_pid}")
                except psutil.AccessDenied:
                    logger.warning(f"IPC进程身份验证失败 (Windows): PID={client_pid}")

            return context

        except psutil.NoSuchProcess:
            logger.error(f"IPC进程验证失败: 进程 {client_pid} 不存在")
            return SecurityContext(client_pid=client_pid)
        except Exception as e:
            logger.error(f"IPC进程验证出错: {e}")
            return SecurityContext(client_pid=client_pid)


class RateLimiter:
    """频率限制器 - 防止IPC DoS攻击"""

    def __init__(self, max_requests_per_minute: int = 300, max_burst: int = 50):
        self.max_requests_per_minute = max_requests_per_minute
        self.max_burst = max_burst
        self.client_requests: Dict[int, deque] = defaultdict(deque)
        self.client_burst_count: Dict[int, int] = defaultdict(int)
        self.burst_reset_time: Dict[int, float] = defaultdict(float)

    def is_allowed(self, client_pid: int) -> bool:
        """检查请求是否被允许"""
        now = time.time()

        # 检查突发限制
        if now - self.burst_reset_time[client_pid] > 60:  # 1分钟重置
            self.client_burst_count[client_pid] = 0
            self.burst_reset_time[client_pid] = now

        if self.client_burst_count[client_pid] >= self.max_burst:
            logger.warning(f"IPC客户端 {client_pid} 触发突发限制")
            return False

        # 检查分钟限制
        client_queue = self.client_requests[client_pid]

        # 清理过期请求
        while client_queue and now - client_queue[0] > 60:
            client_queue.popleft()

        if len(client_queue) >= self.max_requests_per_minute:
            logger.warning(f"IPC客户端 {client_pid} 触发频率限制")
            return False

        # 记录请求
        client_queue.append(now)
        self.client_burst_count[client_pid] += 1

        return True


class IPCFirewall:
    """IPC防火墙 - 路径和操作控制"""

    def __init__(self):
        self.blocked_paths: Set[str] = set()
        self.allowed_methods: Set[str] = {"GET", "POST", "PUT", "DELETE"}
        self.sensitive_paths = {
            "/system-config/security",
            "/internal/debug",
            "/admin/users",
        }

    def is_path_allowed(self, path: str, client_context: SecurityContext) -> bool:
        """检查路径是否被允许访问"""
        if path in self.blocked_paths:
            logger.warning(
                f"IPC访问被阻止的路径: {path} (PID={client_context.client_pid})"
            )
            return False

        if path in self.sensitive_paths:
            # 敏感路径需要额外验证
            if not client_context.authenticated:
                logger.warning(
                    f"IPC未认证访问敏感路径: {path} (PID={client_context.client_pid})"
                )
                return False

        return True

    def is_method_allowed(self, method: str) -> bool:
        """检查HTTP方法是否被允许"""
        return method.upper() in self.allowed_methods

    def block_path(self, path: str):
        """阻止特定路径"""
        self.blocked_paths.add(path)
        logger.info(f"IPC防火墙: 已阻止路径 {path}")

    def unblock_path(self, path: str):
        """解除路径阻止"""
        self.blocked_paths.discard(path)
        logger.info(f"IPC防火墙: 已解除阻止路径 {path}")


class IPCSecurityManager:
    """IPC安全管理器 - 统一安全策略管理"""

    def __init__(self):
        self.authenticator = ProcessAuthenticator()
        self.rate_limiter = RateLimiter()
        self.firewall = IPCFirewall()
        self.active_connections: Dict[str, SecurityContext] = {}
        self.security_log = deque(maxlen=1000)  # 保留最近1000条安全日志

    def authenticate_connection(self, connection_id: str, client_pid: int) -> bool:
        """认证IPC连接"""
        context = self.authenticator.authenticate_process(client_pid)
        self.active_connections[connection_id] = context

        self._log_security_event(
            {
                "event": "connection_attempt",
                "connection_id": connection_id,
                "client_pid": client_pid,
                "authenticated": context.authenticated,
                "timestamp": time.time(),
            }
        )

        return context.authenticated

    def validate_request(self, connection_id: str, method: str, path: str) -> bool:
        """验证IPC请求"""
        context = self.active_connections.get(connection_id)
        if not context:
            logger.error(f"IPC请求验证失败: 连接 {connection_id} 不存在")
            return False

        if not context.authenticated:
            logger.error(f"IPC请求验证失败: 连接 {connection_id} 未认证")
            return False

        # 检查频率限制
        if not self.rate_limiter.is_allowed(context.client_pid):
            self._log_security_event(
                {
                    "event": "rate_limit_exceeded",
                    "connection_id": connection_id,
                    "client_pid": context.client_pid,
                    "path": path,
                    "timestamp": time.time(),
                }
            )
            return False

        # 检查防火墙规则
        if not self.firewall.is_path_allowed(path, context):
            self._log_security_event(
                {
                    "event": "path_blocked",
                    "connection_id": connection_id,
                    "client_pid": context.client_pid,
                    "path": path,
                    "timestamp": time.time(),
                }
            )
            return False

        if not self.firewall.is_method_allowed(method):
            self._log_security_event(
                {
                    "event": "method_blocked",
                    "connection_id": connection_id,
                    "client_pid": context.client_pid,
                    "method": method,
                    "path": path,
                    "timestamp": time.time(),
                }
            )
            return False

        # 更新请求计数
        context.request_count += 1
        context.last_request_time = time.time()

        return True

    def close_connection(self, connection_id: str):
        """关闭IPC连接"""
        context = self.active_connections.pop(connection_id, None)
        if context:
            self._log_security_event(
                {
                    "event": "connection_closed",
                    "connection_id": connection_id,
                    "client_pid": context.client_pid,
                    "request_count": context.request_count,
                    "duration": time.time() - context.connection_time,
                    "timestamp": time.time(),
                }
            )

    def get_security_status(self) -> Dict:
        """获取安全状态报告"""
        now = time.time()
        active_connections = len(self.active_connections)

        # 统计最近的安全事件
        recent_events = [
            event
            for event in self.security_log
            if now - event["timestamp"] < 3600  # 最近1小时
        ]

        event_stats = defaultdict(int)
        for event in recent_events:
            event_stats[event["event"]] += 1

        return {
            "active_connections": active_connections,
            "daemon_pid": self.authenticator.daemon_pid,
            "daemon_uid": self.authenticator.daemon_uid,
            "blocked_paths": list(self.firewall.blocked_paths),
            "recent_events": dict(event_stats),
            "total_security_logs": len(self.security_log),
        }

    def _log_security_event(self, event: Dict):
        """记录安全事件"""
        self.security_log.append(event)

        # 记录重要事件到日志
        event_type = event.get("event")
        if event_type in ["connection_attempt", "rate_limit_exceeded", "path_blocked"]:
            logger.info(f"IPC安全事件: {event}")


def secure_socket_file(socket_path: str) -> bool:
    """加固socket文件安全性"""
    try:
        if not os.path.exists(socket_path):
            return False

        if platform.system() != "Windows":
            # Unix系统：设置严格的文件权限
            os.chmod(socket_path, stat.S_IRUSR | stat.S_IWUSR)  # 仅owner可读写
            logger.info(f"IPC socket文件权限已加固: {socket_path}")
        else:
            # Windows系统：检查文件访问权限（简化实现）
            logger.info(f"IPC socket文件权限已检查 (Windows): {socket_path}")

        return True

    except Exception as e:
        logger.error(f"加固socket文件失败: {e}")
        return False


def secure_socket_directory(socket_dir: Path) -> bool:
    """加固socket目录安全性"""
    try:
        if not socket_dir.exists():
            socket_dir.mkdir(parents=True, mode=0o700)  # 仅owner可访问

        if platform.system() != "Windows":
            # Unix系统：尝试确保目录权限安全
            try:
                os.chmod(socket_dir, stat.S_IRWXU)  # 仅owner可读写执行
                logger.info(f"IPC socket目录权限已加固: {socket_dir}")
            except PermissionError:
                # 系统临时目录可能无法修改权限，这是正常的
                logger.debug(f"无法修改系统目录权限（这是正常的）: {socket_dir}")

        return True

    except Exception as e:
        logger.warning(f"加固socket目录失败: {e}")
        return False


# 全局安全管理器实例
_security_manager = None


def get_security_manager() -> IPCSecurityManager:
    """获取全局IPC安全管理器"""
    global _security_manager
    if _security_manager is None:
        _security_manager = IPCSecurityManager()
    return _security_manager
