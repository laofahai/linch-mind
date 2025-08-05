#!/usr/bin/env python3
"""
进程管理器测试
"""

import asyncio
from unittest.mock import Mock, patch

import psutil
import pytest


class TestProcessManager:
    """进程管理器测试类"""

    @pytest.fixture
    def mock_psutil_process(self):
        """模拟psutil进程对象"""
        process = Mock(spec=psutil.Process)
        process.pid = 12345
        process.name.return_value = "python"
        process.status.return_value = psutil.STATUS_RUNNING
        process.cpu_percent.return_value = 1.5
        process.memory_percent.return_value = 2.0
        process.memory_info.return_value = Mock(rss=1024 * 1024 * 50)  # 50MB
        process.create_time.return_value = 1640995200.0  # 2022-01-01 00:00:00
        process.cmdline.return_value = ["python", "main.py"]
        process.cwd.return_value = "/path/to/connector"
        process.terminate = Mock()
        process.kill = Mock()
        process.wait = Mock(return_value=0)
        process.is_running.return_value = True
        return process

    @pytest.fixture
    def process_manager(self):
        """创建进程管理器实例"""
        from services.connectors.process_manager import ProcessManager

        return ProcessManager()

    @pytest.mark.asyncio
    async def test_start_process_success(self, process_manager, temp_dir):
        """测试成功启动进程"""
        # 创建测试脚本
        test_script = temp_dir / "test_script.py"
        test_script.write_text(
            """
import time
import sys
print("Process started")
sys.stdout.flush()
while True:
    time.sleep(1)
"""
        )

        with patch("subprocess.Popen") as mock_popen:
            mock_process = Mock()
            mock_process.pid = 12345
            mock_process.poll.return_value = None  # Process is running
            mock_popen.return_value = mock_process

            pid = await process_manager.start_process(
                connector_id="test_connector",
                executable_path=str(test_script),
                working_dir=str(temp_dir),
            )

            assert pid == 12345
            mock_popen.assert_called_once()
            assert "test_connector" in process_manager.running_processes

    @pytest.mark.asyncio
    async def test_start_process_invalid_executable(self, process_manager):
        """测试启动无效可执行文件的进程"""
        with patch("subprocess.Popen") as mock_popen:
            mock_popen.side_effect = FileNotFoundError("Executable not found")

            pid = await process_manager.start_process(
                connector_id="invalid_connector",
                executable_path="/nonexistent/file",
                working_dir="/tmp",
            )

            assert pid is None

    @pytest.mark.asyncio
    async def test_stop_process_success(self, process_manager, mock_psutil_process):
        """测试成功停止进程"""
        # 先添加一个运行中的进程
        process_manager.running_processes["test_connector"] = {
            "pid": 12345,
            "process": mock_psutil_process,
        }

        with patch("psutil.Process", return_value=mock_psutil_process):
            success = await process_manager.stop_process(12345)

            assert success is True
            mock_psutil_process.terminate.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_process_force_kill(self, process_manager, mock_psutil_process):
        """测试强制杀死进程"""
        # 模拟进程不响应terminate
        mock_psutil_process.wait.side_effect = psutil.TimeoutExpired(12345)

        process_manager.running_processes["test_connector"] = {
            "pid": 12345,
            "process": mock_psutil_process,
        }

        with patch("psutil.Process", return_value=mock_psutil_process):
            success = await process_manager.stop_process(12345, timeout=1)

            assert success is True
            mock_psutil_process.terminate.assert_called_once()
            mock_psutil_process.kill.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_nonexistent_process(self, process_manager):
        """测试停止不存在的进程"""
        with patch("psutil.Process") as mock_psutil:
            mock_psutil.side_effect = psutil.NoSuchProcess(99999)

            success = await process_manager.stop_process(99999)

            assert success is False

    def test_get_process_info_success(self, process_manager, mock_psutil_process):
        """测试成功获取进程信息"""
        with patch("psutil.Process", return_value=mock_psutil_process):
            info = process_manager.get_process_info(12345)

            assert info is not None
            assert info["pid"] == 12345
            assert info["name"] == "python"
            assert info["status"] == psutil.STATUS_RUNNING
            assert info["cpu_percent"] == 1.5
            assert info["memory_percent"] == 2.0
            assert "memory_mb" in info
            assert "cmdline" in info
            assert "cwd" in info

    def test_get_process_info_not_found(self, process_manager):
        """测试获取不存在进程的信息"""
        with patch("psutil.Process") as mock_psutil:
            mock_psutil.side_effect = psutil.NoSuchProcess(99999)

            info = process_manager.get_process_info(99999)

            assert info is None

    def test_is_process_running_true(self, process_manager, mock_psutil_process):
        """测试进程正在运行"""
        with patch("psutil.Process", return_value=mock_psutil_process):
            is_running = process_manager.is_process_running(12345)

            assert is_running is True

    def test_is_process_running_false(self, process_manager):
        """测试进程未运行"""
        with patch("psutil.Process") as mock_psutil:
            mock_psutil.side_effect = psutil.NoSuchProcess(99999)

            is_running = process_manager.is_process_running(99999)

            assert is_running is False

    def test_is_process_running_zombie(self, process_manager, mock_psutil_process):
        """测试僵尸进程"""
        mock_psutil_process.status.return_value = psutil.STATUS_ZOMBIE

        with patch("psutil.Process", return_value=mock_psutil_process):
            is_running = process_manager.is_process_running(12345)

            assert is_running is False

    def test_list_all_processes(self, process_manager):
        """测试列出所有进程"""
        # 添加一些测试进程
        process_manager.running_processes = {
            "connector1": {"pid": 123, "start_time": "2025-01-01T10:00:00Z"},
            "connector2": {"pid": 456, "start_time": "2025-01-01T10:01:00Z"},
        }

        processes = process_manager.list_all_processes()

        assert len(processes) == 2
        assert any(p["connector_id"] == "connector1" for p in processes)
        assert any(p["connector_id"] == "connector2" for p in processes)

    def test_get_process_by_connector_id(self, process_manager):
        """测试通过连接器ID获取进程"""
        process_manager.running_processes["test_connector"] = {
            "pid": 12345,
            "start_time": "2025-01-01T10:00:00Z",
        }

        process_info = process_manager.get_process_by_connector_id("test_connector")

        assert process_info is not None
        assert process_info["pid"] == 12345

        # 测试不存在的连接器
        nonexistent = process_manager.get_process_by_connector_id("nonexistent")
        assert nonexistent is None

    @pytest.mark.asyncio
    async def test_restart_process(
        self, process_manager, mock_psutil_process, temp_dir
    ):
        """测试重启进程"""
        # 创建测试脚本
        test_script = temp_dir / "test_script.py"
        test_script.write_text("print('Hello')")

        # 先添加运行中的进程
        process_manager.running_processes["test_connector"] = {
            "pid": 12345,
            "process": mock_psutil_process,
            "executable_path": str(test_script),
            "working_dir": str(temp_dir),
        }

        with patch("psutil.Process", return_value=mock_psutil_process):
            with patch("subprocess.Popen") as mock_popen:
                mock_new_process = Mock()
                mock_new_process.pid = 54321
                mock_popen.return_value = mock_new_process

                new_pid = await process_manager.restart_process("test_connector")

                assert new_pid == 54321
                mock_psutil_process.terminate.assert_called_once()

    @pytest.mark.asyncio
    async def test_restart_nonexistent_process(self, process_manager):
        """测试重启不存在的进程"""
        new_pid = await process_manager.restart_process("nonexistent")

        assert new_pid is None

    def test_cleanup_dead_processes(self, process_manager):
        """测试清理死进程"""
        # 添加一些进程，包括死进程
        process_manager.running_processes = {
            "alive_connector": {"pid": 123},
            "dead_connector": {"pid": 999},
        }

        with patch("psutil.Process") as mock_psutil:

            def mock_process_init(pid):
                if pid == 999:
                    raise psutil.NoSuchProcess(pid)
                mock_proc = Mock()
                mock_proc.is_running.return_value = True
                return mock_proc

            mock_psutil.side_effect = mock_process_init

            process_manager.cleanup_dead_processes()

            # 死进程应该被清理
            assert "alive_connector" in process_manager.running_processes
            assert "dead_connector" not in process_manager.running_processes

    def test_get_system_stats(self, process_manager):
        """测试获取系统统计信息"""
        with patch("psutil.cpu_percent", return_value=15.5):
            with patch("psutil.virtual_memory") as mock_memory:
                mock_memory.return_value.percent = 45.2
                mock_memory.return_value.total = 8 * 1024 * 1024 * 1024  # 8GB
                mock_memory.return_value.available = 4 * 1024 * 1024 * 1024  # 4GB

                stats = process_manager.get_system_stats()

                assert stats["cpu_percent"] == 15.5
                assert stats["memory_percent"] == 45.2
                assert stats["memory_total_gb"] == 8.0
                assert stats["memory_available_gb"] == 4.0
                assert "active_processes" in stats

    def test_monitor_process_resources(self, process_manager, mock_psutil_process):
        """测试监控进程资源使用"""
        process_manager.running_processes["test_connector"] = {
            "pid": 12345,
            "process": mock_psutil_process,
        }

        with patch("psutil.Process", return_value=mock_psutil_process):
            resources = process_manager.monitor_process_resources("test_connector")

            assert resources is not None
            assert resources["cpu_percent"] == 1.5
            assert resources["memory_percent"] == 2.0
            assert "memory_mb" in resources

    def test_monitor_nonexistent_process_resources(self, process_manager):
        """测试监控不存在进程的资源"""
        resources = process_manager.monitor_process_resources("nonexistent")

        assert resources is None

    @pytest.mark.asyncio
    async def test_kill_all_processes(self, process_manager, mock_psutil_process):
        """测试杀死所有进程"""
        # 添加多个进程
        process_manager.running_processes = {
            "connector1": {"pid": 123, "process": mock_psutil_process},
            "connector2": {"pid": 456, "process": mock_psutil_process},
        }

        with patch("psutil.Process", return_value=mock_psutil_process):
            killed_count = await process_manager.kill_all_processes()

            assert killed_count == 2
            assert len(process_manager.running_processes) == 0

    def test_get_process_manager_singleton(self):
        """测试进程管理器单例模式"""
        from services.connectors.process_manager import get_process_manager

        manager1 = get_process_manager()
        manager2 = get_process_manager()

        assert manager1 is manager2  # 验证单例

    @pytest.mark.asyncio
    async def test_process_environment_variables(self, process_manager, temp_dir):
        """测试进程环境变量设置"""
        test_script = temp_dir / "env_test.py"
        test_script.write_text(
            """
import os
print(f"CONNECTOR_ID={os.getenv('CONNECTOR_ID', 'NOT_SET')}")
"""
        )

        env_vars = {"CONNECTOR_ID": "test_connector", "DEBUG": "true"}

        with patch("subprocess.Popen") as mock_popen:
            mock_process = Mock()
            mock_process.pid = 12345
            mock_popen.return_value = mock_process

            pid = await process_manager.start_process(
                connector_id="test_connector",
                executable_path=str(test_script),
                working_dir=str(temp_dir),
                env_vars=env_vars,
            )

            assert pid == 12345
            # 验证环境变量被传递
            call_args = mock_popen.call_args
            assert "CONNECTOR_ID" in call_args.kwargs.get("env", {})

    def test_process_output_capture(self, process_manager):
        """测试进程输出捕获"""
        # 这个测试需要实际的子进程，所以使用mock
        with patch("subprocess.Popen") as mock_popen:
            mock_process = Mock()
            mock_process.pid = 12345
            mock_process.stdout = Mock()
            mock_process.stderr = Mock()
            mock_popen.return_value = mock_process

            # 测试输出捕获配置
            asyncio.run(
                process_manager.start_process(
                    connector_id="output_test",
                    executable_path="python",
                    working_dir="/tmp",
                    capture_output=True,
                )
            )

            # 验证stdout和stderr被正确配置
            call_args = mock_popen.call_args
            assert call_args.kwargs.get("stdout") is not None
            assert call_args.kwargs.get("stderr") is not None
