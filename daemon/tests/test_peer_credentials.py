#!/usr/bin/env python3
"""
测试跨平台Unix Domain Socket对等进程凭证获取功能
"""

import os
import platform
import socket
import struct
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock, patch

# 添加daemon目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ipc.peer_credentials import (
    PeerCredentials,
    SocketPeerResolver,
    discover_client_pid,
    get_socket_peer_credentials,
    get_socket_peer_pid,
)


class TestSocketPeerResolver(unittest.TestCase):
    """测试SocketPeerResolver类"""

    def setUp(self):
        """测试设置"""
        self.resolver = SocketPeerResolver()
        self.test_socket = None
        self.test_server = None
        self.temp_socket_path = None

    def tearDown(self):
        """测试清理"""
        if self.test_socket:
            try:
                self.test_socket.close()
            except:
                pass
        if self.test_server:
            try:
                self.test_server.close()
            except:
                pass
        if self.temp_socket_path and os.path.exists(self.temp_socket_path):
            try:
                os.unlink(self.temp_socket_path)
            except:
                pass

    def test_platform_initialization(self):
        """测试平台初始化"""
        resolver = SocketPeerResolver()

        if platform.system() == "Linux":
            self.assertEqual(resolver.SOL_SOCKET, socket.SOL_SOCKET)
            self.assertEqual(resolver.SO_PEERCRED, 17)
            self.assertEqual(resolver.credential_size, 12)
        elif platform.system() == "Darwin":
            self.assertEqual(resolver.SOL_LOCAL, 0)
            self.assertEqual(resolver.LOCAL_PEERPID, 2)
            self.assertEqual(resolver.LOCAL_PEERCRED, 1)

    def test_invalid_socket_handling(self):
        """测试无效socket处理"""
        # 测试空socket
        credentials = self.resolver.get_peer_credentials(None)
        self.assertEqual(credentials.source, "error")
        self.assertIsNone(credentials.pid)

    @unittest.skipIf(
        platform.system() == "Windows", "Unix socket test not supported on Windows"
    )
    def test_non_unix_socket(self):
        """测试非Unix socket处理"""
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            credentials = self.resolver.get_peer_credentials(tcp_socket)
            self.assertEqual(credentials.source, "error")
            self.assertIsNone(credentials.pid)
        finally:
            tcp_socket.close()

    @unittest.skipIf(platform.system() != "Linux", "Linux specific test")
    @patch("socket.socket.getsockopt")
    def test_linux_credentials_success(self, mock_getsockopt):
        """测试Linux SO_PEERCRED成功获取"""
        # 模拟SO_PEERCRED返回的数据：PID=1234, UID=1000, GID=1000
        mock_getsockopt.return_value = struct.pack("III", 1234, 1000, 1000)

        mock_socket = Mock(spec=socket.socket)
        mock_socket.family = socket.AF_UNIX
        mock_socket.getsockopt = mock_getsockopt

        credentials = self.resolver._get_linux_credentials(mock_socket)

        self.assertEqual(credentials.pid, 1234)
        self.assertEqual(credentials.uid, 1000)
        self.assertEqual(credentials.gid, 1000)
        self.assertEqual(credentials.source, "SO_PEERCRED")
        self.assertEqual(credentials.confidence, "high")

    @unittest.skipIf(platform.system() != "Linux", "Linux specific test")
    @patch("socket.socket.getsockopt")
    def test_linux_credentials_failure(self, mock_getsockopt):
        """测试Linux SO_PEERCRED获取失败"""
        mock_getsockopt.side_effect = OSError("Socket option not supported")

        mock_socket = Mock(spec=socket.socket)
        mock_socket.family = socket.AF_UNIX
        mock_socket.getsockopt = mock_getsockopt
        mock_socket.getpeername = Mock(return_value=None)
        mock_socket.getsockname = Mock(return_value=None)

        with patch("psutil.process_iter", return_value=[]):
            credentials = self.resolver._get_linux_credentials(mock_socket)

        self.assertEqual(credentials.source, "fallback_failed")
        self.assertIsNone(credentials.pid)

    @unittest.skipIf(platform.system() != "Darwin", "macOS specific test")
    @patch("socket.socket.getsockopt")
    def test_macos_credentials_success(self, mock_getsockopt):
        """测试macOS LOCAL_PEERPID成功获取"""
        # 模拟LOCAL_PEERPID返回的数据：PID=1234
        mock_getsockopt.return_value = struct.pack("I", 1234)

        mock_socket = Mock(spec=socket.socket)
        mock_socket.family = socket.AF_UNIX
        mock_socket.getsockopt = mock_getsockopt

        credentials = self.resolver._get_macos_credentials(mock_socket)

        self.assertEqual(credentials.pid, 1234)
        self.assertEqual(credentials.source, "LOCAL_PEERPID")
        self.assertEqual(credentials.confidence, "high")

    @unittest.skipIf(platform.system() != "Darwin", "macOS specific test")
    @patch("socket.socket.getsockopt")
    def test_macos_credentials_failure(self, mock_getsockopt):
        """测试macOS LOCAL_PEERPID获取失败"""
        mock_getsockopt.side_effect = OSError("Socket option not supported")

        mock_socket = Mock(spec=socket.socket)
        mock_socket.family = socket.AF_UNIX
        mock_socket.getsockopt = mock_getsockopt
        mock_socket.getpeername = Mock(return_value=None)
        mock_socket.getsockname = Mock(return_value=None)

        with patch("psutil.process_iter", return_value=[]):
            credentials = self.resolver._get_macos_credentials(mock_socket)

        self.assertEqual(credentials.source, "fallback_failed")
        self.assertIsNone(credentials.pid)

    @patch("psutil.process_iter")
    def test_fallback_credentials_success(self, mock_process_iter):
        """测试回退方法成功"""
        current_pid = os.getpid()
        mock_proc = Mock()
        mock_proc.info = {
            "pid": current_pid + 1,
            "connections": [Mock(family=socket.AF_UNIX, laddr="/tmp/test.sock")],
        }
        mock_process_iter.return_value = [mock_proc]

        mock_socket = Mock(spec=socket.socket)
        mock_socket.family = socket.AF_UNIX
        mock_socket.getpeername = Mock(return_value=None)
        mock_socket.getsockname = Mock(return_value=None)

        credentials = self.resolver._get_fallback_credentials(mock_socket)

        self.assertEqual(credentials.pid, current_pid + 1)
        self.assertEqual(credentials.source, "psutil_scan")
        self.assertEqual(credentials.confidence, "low")

    @patch("psutil.pid_exists")
    @patch("psutil.Process")
    def test_validate_credentials_success(self, mock_process, mock_pid_exists):
        """测试凭证验证成功"""
        mock_pid_exists.return_value = True
        mock_proc_instance = Mock()
        mock_proc_instance.name.return_value = "test_process"
        mock_process.return_value = mock_proc_instance

        credentials = PeerCredentials(pid=1234, source="SO_PEERCRED", confidence="high")

        result = self.resolver.validate_credentials(credentials)
        self.assertTrue(result)

    @patch("psutil.pid_exists")
    def test_validate_credentials_failure(self, mock_pid_exists):
        """测试凭证验证失败"""
        mock_pid_exists.return_value = False

        credentials = PeerCredentials(pid=1234, source="SO_PEERCRED", confidence="high")

        result = self.resolver.validate_credentials(credentials)
        self.assertFalse(result)

    def test_validate_credentials_empty(self):
        """测试空凭证验证"""
        credentials = PeerCredentials()
        result = self.resolver.validate_credentials(credentials)
        self.assertFalse(result)


class TestModuleFunctions(unittest.TestCase):
    """测试模块级函数"""

    @patch("services.ipc.peer_credentials.get_peer_resolver")
    def test_get_socket_peer_pid(self, mock_get_resolver):
        """测试获取socket对等PID函数"""
        mock_resolver = Mock()
        mock_resolver.get_peer_credentials.return_value = PeerCredentials(
            pid=1234, source="SO_PEERCRED", confidence="high"
        )
        mock_resolver.validate_credentials.return_value = True
        mock_get_resolver.return_value = mock_resolver

        mock_socket = Mock()
        pid = get_socket_peer_pid(mock_socket)

        self.assertEqual(pid, 1234)

    @patch("services.ipc.peer_credentials.get_peer_resolver")
    def test_get_socket_peer_pid_failure(self, mock_get_resolver):
        """测试获取socket对等PID失败"""
        mock_resolver = Mock()
        mock_resolver.get_peer_credentials.return_value = PeerCredentials(
            pid=1234, source="error", confidence="low"
        )
        mock_resolver.validate_credentials.return_value = False
        mock_get_resolver.return_value = mock_resolver

        mock_socket = Mock()
        pid = get_socket_peer_pid(mock_socket)

        self.assertIsNone(pid)

    @patch("services.ipc.peer_credentials.get_peer_resolver")
    def test_get_socket_peer_credentials(self, mock_get_resolver):
        """测试获取socket对等凭证函数"""
        expected_credentials = PeerCredentials(
            pid=1234, uid=1000, gid=1000, source="SO_PEERCRED", confidence="high"
        )
        mock_resolver = Mock()
        mock_resolver.get_peer_credentials.return_value = expected_credentials
        mock_get_resolver.return_value = mock_resolver

        mock_socket = Mock()
        credentials = get_socket_peer_credentials(mock_socket)

        self.assertEqual(credentials, expected_credentials)

    @patch("services.ipc.peer_credentials.get_socket_peer_pid")
    def test_discover_client_pid(self, mock_get_pid):
        """测试发现客户端PID函数（向后兼容）"""
        mock_get_pid.return_value = 1234

        mock_writer = Mock()
        mock_writer.get_extra_info.return_value = Mock()

        pid = discover_client_pid(mock_writer)
        self.assertEqual(pid, 1234)

    def test_discover_client_pid_no_socket(self):
        """测试发现客户端PID无socket情况"""
        mock_writer = Mock()
        mock_writer.get_extra_info.return_value = None

        pid = discover_client_pid(mock_writer)
        self.assertIsNone(pid)


class TestRealSocketConnections(unittest.TestCase):
    """测试真实socket连接（集成测试）"""

    @unittest.skipIf(
        platform.system() == "Windows", "Unix socket test not supported on Windows"
    )
    def test_real_unix_socket_connection(self):
        """测试真实Unix socket连接的PID获取"""
        # 创建临时socket路径
        with tempfile.NamedTemporaryFile(delete=False) as f:
            socket_path = f.name
        os.unlink(socket_path)  # 删除文件，只保留路径

        try:
            # 创建服务器socket
            server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            server_socket.bind(socket_path)
            server_socket.listen(1)

            # 在另一个线程中创建客户端连接
            client_pid = None
            server_peer_creds = None

            def client_thread():
                nonlocal client_pid
                client_pid = os.getpid()
                try:
                    client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    client_socket.connect(socket_path)
                    time.sleep(0.5)  # 保持连接
                    client_socket.close()
                except Exception as e:
                    print(f"Client error: {e}")

            def server_thread():
                nonlocal server_peer_creds
                try:
                    conn, addr = server_socket.accept()
                    resolver = SocketPeerResolver()
                    server_peer_creds = resolver.get_peer_credentials(conn)
                    time.sleep(0.3)
                    conn.close()
                except Exception as e:
                    print(f"Server error: {e}")

            # 启动线程
            client = threading.Thread(target=client_thread)
            server = threading.Thread(target=server_thread)

            client.start()
            time.sleep(0.1)  # 确保客户端先启动
            server.start()

            client.join(timeout=2.0)
            server.join(timeout=2.0)

            server_socket.close()

            # 验证结果
            if server_peer_creds:
                print(
                    f"获取的凭证: PID={server_peer_creds.pid}, 来源={server_peer_creds.source}, 可信度={server_peer_creds.confidence}"
                )

                # 由于在同一进程中运行，PID应该相同
                self.assertEqual(server_peer_creds.pid, os.getpid())

                # 检查来源是否为平台特定的高可信度来源
                if platform.system() == "Linux":
                    self.assertIn(
                        server_peer_creds.source,
                        ["SO_PEERCRED", "psutil_scan", "fallback_failed"],
                    )
                elif platform.system() == "Darwin":
                    self.assertIn(
                        server_peer_creds.source,
                        ["LOCAL_PEERPID", "psutil_scan", "fallback_failed"],
                    )
            else:
                self.fail("未能获取服务器端对等凭证")

        finally:
            try:
                os.unlink(socket_path)
            except:
                pass


if __name__ == "__main__":
    # 设置日志级别以便调试
    import logging

    logging.basicConfig(level=logging.DEBUG)

    unittest.main(verbosity=2)
