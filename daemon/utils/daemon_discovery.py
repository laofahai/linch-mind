#!/usr/bin/env python3
"""
Daemon发现工具 - 供UI安全地发现daemon端口
提供安全的端口发现机制，避免直接暴露端口文件
"""

import logging
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class DaemonInfo:
    """Daemon信息"""

    host: str
    port: int
    pid: int
    started_at: str
    is_accessible: bool = False


class DaemonDiscovery:
    """Daemon发现服务"""

    def __init__(self, app_data_dir: Optional[Path] = None):
        self.app_data_dir = app_data_dir or Path.home() / ".linch-mind"
        self.port_file = self.app_data_dir / "daemon.port"

    def discover_daemon(self) -> Optional[DaemonInfo]:
        """发现运行中的daemon实例

        Returns:
            Optional[DaemonInfo]: daemon信息，如果未发现则返回None
        """
        # 1. 读取端口文件
        port_data = self._read_port_file()
        if not port_data:
            logger.debug("No valid daemon port file found")
            return None

        # 2. 验证进程是否运行
        if not self._verify_daemon_process(port_data["pid"]):
            logger.warning(f"Daemon process {port_data['pid']} is not running")
            self._cleanup_port_file()
            return None

        # 3. 创建daemon信息
        daemon_info = DaemonInfo(
            host=port_data["host"],
            port=port_data["port"],
            pid=port_data["pid"],
            started_at=port_data["started_at"],
        )

        # 4. 测试连接性
        daemon_info.is_accessible = self._test_daemon_connection(
            daemon_info.host, daemon_info.port
        )

        if daemon_info.is_accessible:
            logger.info(
                f"Discovered accessible daemon at {daemon_info.host}:{daemon_info.port}"
            )
        else:
            logger.warning(
                f"Daemon found but not accessible at {daemon_info.host}:{daemon_info.port}"
            )

        return daemon_info

    def _read_port_file(self) -> Optional[Dict[str, Any]]:
        """读取简化端口文件"""
        if not self.port_file.exists():
            return None

        try:
            with open(self.port_file, "r") as f:
                content = f.read().strip()

            # 解析格式: port:pid
            if ":" not in content:
                logger.warning("Port file format invalid, expected 'port:pid'")
                return None

            port_str, pid_str = content.split(":", 1)
            port = int(port_str)
            pid = int(pid_str)

            return {
                "port": port,
                "pid": pid,
                "host": "127.0.0.1",
                "started_at": "unknown",
            }

        except (ValueError, IOError) as e:
            logger.warning(f"Failed to read port file: {e}")
            return None

    def _verify_daemon_process(self, pid: int) -> bool:
        """验证daemon进程是否仍在运行"""
        try:
            import psutil

            if not psutil.pid_exists(pid):
                return False

            proc = psutil.Process(pid)
            # 检查是否是python进程且包含daemon相关关键字
            if "python" in proc.name().lower():
                cmdline = " ".join(proc.cmdline())
                if any(
                    keyword in cmdline.lower()
                    for keyword in ["api/main", "daemon", "linch-mind", "uvicorn"]
                ):
                    return True

            return False
        except (psutil.NoSuchProcess, psutil.AccessDenied, ImportError):
            return False

    def _test_daemon_connection(
        self, host: str, port: int, timeout: float = 3.0
    ) -> bool:
        """测试daemon连接性"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                return result == 0
        except Exception as e:
            logger.debug(f"Connection test failed: {e}")
            return False

    def _cleanup_port_file(self):
        """清理无效的端口文件"""
        if self.port_file.exists():
            try:
                self.port_file.unlink()
                logger.debug("Cleaned up invalid port file")
            except Exception as e:
                logger.warning(f"Failed to cleanup port file: {e}")

    def wait_for_daemon(
        self, timeout: float = 30.0, check_interval: float = 1.0
    ) -> Optional[DaemonInfo]:
        """等待daemon启动

        Args:
            timeout: 最大等待时间（秒）
            check_interval: 检查间隔（秒）

        Returns:
            Optional[DaemonInfo]: daemon信息，如果超时则返回None
        """
        import time

        start_time = time.time()
        while time.time() - start_time < timeout:
            daemon_info = self.discover_daemon()
            if daemon_info and daemon_info.is_accessible:
                return daemon_info

            time.sleep(check_interval)

        logger.warning(f"Daemon discovery timed out after {timeout}s")
        return None


def discover_daemon() -> Optional[DaemonInfo]:
    """便捷函数：发现daemon实例"""
    discovery = DaemonDiscovery()
    return discovery.discover_daemon()


def wait_for_daemon(timeout: float = 30.0) -> Optional[DaemonInfo]:
    """便捷函数：等待daemon启动"""
    discovery = DaemonDiscovery()
    return discovery.wait_for_daemon(timeout)


if __name__ == "__main__":
    # 测试用例
    logging.basicConfig(level=logging.DEBUG)

    print("正在发现daemon...")
    daemon_info = discover_daemon()

    if daemon_info:
        print(f"✅ 发现daemon:")
        print(f"   地址: {daemon_info.host}:{daemon_info.port}")
        print(f"   PID: {daemon_info.pid}")
        print(f"   启动时间: {daemon_info.started_at}")
        print(f"   可访问: {daemon_info.is_accessible}")
    else:
        print("❌ 未发现运行中的daemon")
