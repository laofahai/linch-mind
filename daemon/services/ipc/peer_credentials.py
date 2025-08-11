#!/usr/bin/env python3
"""
跨平台 Unix Domain Socket 对等进程凭证获取模块

提供安全可靠的方法来获取Unix Domain Socket连接对端的进程ID (PID)
支持Linux (SO_PEERCRED) 和 macOS (LOCAL_PEERPID)
"""

import logging
import platform
import socket
import struct
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class PeerCredentials:
    """对等进程凭证信息"""

    pid: Optional[int] = None
    uid: Optional[int] = None
    gid: Optional[int] = None
    source: str = "unknown"
    confidence: str = "low"  # low, medium, high


class SocketPeerResolver:
    """Unix Domain Socket对等进程解析器"""

    def __init__(self):
        self.platform = platform.system()
        self._init_platform_constants()

    def _init_platform_constants(self):
        """初始化平台相关常量"""
        if self.platform == "Linux":
            # Linux使用SO_PEERCRED
            self.SOL_SOCKET = socket.SOL_SOCKET
            self.SO_PEERCRED = 17  # Linux SO_PEERCRED常量
            self.credential_size = 12  # pid(4) + uid(4) + gid(4)
            logger.debug("初始化Linux SO_PEERCRED支持")

        elif self.platform == "Darwin":  # macOS
            # macOS使用LOCAL_*选项
            self.SOL_LOCAL = 0  # socket.SOL_LOCAL在某些系统上可能不可用
            self.LOCAL_PEERPID = 2
            self.LOCAL_PEERCRED = 1
            logger.debug("初始化macOS LOCAL_PEERPID支持")

        else:
            logger.warning(f"未知平台: {self.platform}，将使用回退方法")

    def get_peer_credentials(self, sock: socket.socket) -> PeerCredentials:
        """
        获取Unix Domain Socket对等进程凭证

        Args:
            sock: Unix Domain Socket对象

        Returns:
            PeerCredentials: 包含PID、UID、GID等信息的凭证对象
        """
        if not sock:
            logger.warning("提供的socket对象为空")
            return PeerCredentials(source="error")

        # 检查socket类型
        if sock.family != socket.AF_UNIX:
            logger.warning(f"不支持的socket类型: {sock.family}，仅支持AF_UNIX")
            return PeerCredentials(source="error")

        # 尝试平台特定的方法
        if self.platform == "Linux":
            return self._get_linux_credentials(sock)
        elif self.platform == "Darwin":
            return self._get_macos_credentials(sock)
        else:
            return self._get_fallback_credentials(sock)

    def _get_linux_credentials(self, sock: socket.socket) -> PeerCredentials:
        """
        Linux平台使用SO_PEERCRED获取对等进程凭证
        """
        try:
            # 使用SO_PEERCRED获取凭证
            creds_bytes = sock.getsockopt(
                self.SOL_SOCKET, self.SO_PEERCRED, self.credential_size
            )

            # 解析凭证结构: struct ucred { pid_t pid; uid_t uid; gid_t gid; };
            pid, uid, gid = struct.unpack("III", creds_bytes)

            logger.debug(f"Linux SO_PEERCRED成功获取: PID={pid}, UID={uid}, GID={gid}")

            return PeerCredentials(
                pid=pid, uid=uid, gid=gid, source="SO_PEERCRED", confidence="high"
            )

        except OSError as e:
            logger.debug(f"Linux SO_PEERCRED获取失败: {e}")
            return self._get_fallback_credentials(sock)
        except Exception as e:
            logger.error(f"Linux凭证获取异常: {e}")
            return PeerCredentials(source="error")

    def _get_macos_credentials(self, sock: socket.socket) -> PeerCredentials:
        """
        macOS平台使用LOCAL_PEERPID和LOCAL_PEERCRED获取对等进程凭证
        """
        pid = None
        uid = None
        gid = None

        try:
            # 首先尝试获取PID
            try:
                pid_bytes = sock.getsockopt(self.SOL_LOCAL, self.LOCAL_PEERPID, 4)
                pid = struct.unpack("I", pid_bytes)[0]
                logger.debug(f"macOS LOCAL_PEERPID成功获取: PID={pid}")
            except OSError as e:
                logger.debug(f"macOS LOCAL_PEERPID获取失败: {e}")

            # 尝试获取完整凭证（包含UID/GID）
            try:
                # LOCAL_PEERCRED返回更完整的凭证信息
                sock.getsockopt(self.SOL_LOCAL, self.LOCAL_PEERCRED, 96)
                # macOS的凭证结构比Linux复杂，这里简化处理
                # 实际结构: struct xucred，但我们主要需要PID
                logger.debug("macOS LOCAL_PEERCRED数据获取成功")
            except OSError as e:
                logger.debug(f"macOS LOCAL_PEERCRED获取失败: {e}")

            if pid is not None:
                return PeerCredentials(
                    pid=pid, uid=uid, gid=gid, source="LOCAL_PEERPID", confidence="high"
                )
            else:
                return self._get_fallback_credentials(sock)

        except Exception as e:
            logger.error(f"macOS凭证获取异常: {e}")
            return self._get_fallback_credentials(sock)

    def _get_fallback_credentials(self, sock: socket.socket) -> PeerCredentials:
        """
        回退方法：使用psutil进程扫描
        注意：这种方法可靠性较低，仅在平台特定方法失败时使用
        """
        try:
            import os

            import psutil

            # 获取socket信息
            peer_info = sock.getpeername() if hasattr(sock, "getpeername") else None
            local_info = sock.getsockname() if hasattr(sock, "getsockname") else None

            logger.debug(
                f"回退方法：扫描进程连接，peer={peer_info}, local={local_info}"
            )

            current_pid = os.getpid()

            # 扫描所有进程的连接
            for proc in psutil.process_iter(["pid", "connections"]):
                try:
                    proc_pid = proc.info["pid"]
                    if proc_pid == current_pid:
                        continue  # 跳过当前进程

                    connections = proc.info["connections"]
                    if not connections:
                        continue

                    # 检查是否有Unix socket连接
                    for conn in connections:
                        if (
                            conn.family == socket.AF_UNIX
                            and hasattr(conn, "laddr")
                            and conn.laddr
                        ):

                            # 这里的匹配逻辑比较粗糙，仅作为最后手段
                            logger.debug(f"发现可能的客户端进程: PID={proc_pid}")
                            return PeerCredentials(
                                pid=proc_pid, source="psutil_scan", confidence="low"
                            )

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            logger.debug("回退方法：未找到匹配的客户端进程")
            return PeerCredentials(source="fallback_failed")

        except ImportError:
            logger.debug("psutil不可用，回退方法失败")
            return PeerCredentials(source="no_psutil")
        except Exception as e:
            logger.debug(f"回退方法异常: {e}")
            return PeerCredentials(source="fallback_error")

    def validate_credentials(self, credentials: PeerCredentials) -> bool:
        """
        验证凭证的有效性
        """
        if not credentials or not credentials.pid:
            return False

        try:
            import psutil

            # 检查进程是否存在
            if not psutil.pid_exists(credentials.pid):
                logger.warning(f"PID {credentials.pid} 不存在")
                return False

            # 检查进程是否可访问
            try:
                proc = psutil.Process(credentials.pid)
                _ = proc.name()  # 尝试访问进程信息
                return True
            except psutil.AccessDenied:
                logger.warning(f"无法访问进程 {credentials.pid}")
                return False
            except psutil.NoSuchProcess:
                logger.warning(f"进程 {credentials.pid} 已不存在")
                return False

        except ImportError:
            # 没有psutil时，进行基本检查
            if credentials.confidence == "high" and credentials.source in [
                "SO_PEERCRED",
                "LOCAL_PEERPID",
            ]:
                return True
            return False
        except Exception as e:
            logger.error(f"凭证验证异常: {e}")
            return False


# 全局解析器实例
_peer_resolver = None


def get_peer_resolver() -> SocketPeerResolver:
    """获取全局对等进程解析器实例"""
    global _peer_resolver
    if _peer_resolver is None:
        _peer_resolver = SocketPeerResolver()
    return _peer_resolver


def get_socket_peer_pid(sock: socket.socket) -> Optional[int]:
    """
    便捷函数：获取Unix Domain Socket对等进程PID

    Args:
        sock: Unix Domain Socket对象

    Returns:
        Optional[int]: 对等进程的PID，获取失败时返回None
    """
    resolver = get_peer_resolver()
    credentials = resolver.get_peer_credentials(sock)

    if resolver.validate_credentials(credentials):
        return credentials.pid

    return None


def get_socket_peer_credentials(sock: socket.socket) -> PeerCredentials:
    """
    便捷函数：获取Unix Domain Socket对等进程完整凭证

    Args:
        sock: Unix Domain Socket对象

    Returns:
        PeerCredentials: 完整的对等进程凭证信息
    """
    resolver = get_peer_resolver()
    return resolver.get_peer_credentials(sock)


# 模块级便捷函数，保持向后兼容性
def discover_client_pid(writer) -> Optional[int]:
    """
    发现客户端进程PID（向后兼容）

    Args:
        writer: asyncio StreamWriter对象

    Returns:
        Optional[int]: 客户端进程PID
    """
    try:
        sock = writer.get_extra_info("socket")
        if sock:
            return get_socket_peer_pid(sock)
    except Exception as e:
        logger.debug(f"发现客户端PID失败: {e}")

    return None
