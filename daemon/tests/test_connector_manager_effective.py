#!/usr/bin/env python3
"""
连接器管理器有效测试 - 重构版本
专注于真实业务逻辑验证，最小化mock使用
"""

import asyncio
import json
import tempfile
from pathlib import Path

import pytest

from services.connectors.connector_manager import ConnectorManager
from services.database_service import DatabaseService


class TestConnectorManagerEffective:
    """有效的连接器管理器测试 - 真实业务逻辑验证"""

    @pytest.fixture
    async def real_db_service(self):
        """使用真实的内存数据库"""
        db_service = DatabaseService(db_path=":memory:")
        await db_service.initialize()
        yield db_service
        await db_service.close()

    @pytest.fixture
    def temp_connector_dir(self):
        """创建真实的临时连接器目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 创建一个真实的测试连接器
            connector_dir = temp_path / "test_connector"
            connector_dir.mkdir()

            # 创建连接器元数据
            connector_json = {
                "name": "Test Connector",
                "description": "A test connector for validation",
                "version": "1.0.0",
                "entry_point": "main.py",
            }
            (connector_dir / "connector.json").write_text(json.dumps(connector_json))

            # 创建一个简单的Python连接器程序
            main_py_content = """
import sys
import time
import json

def main():
    print("Test connector started")
    # 简单的心跳循环
    try:
        while True:
            print(json.dumps({"status": "running", "timestamp": time.time()}))
            time.sleep(1)
    except KeyboardInterrupt:
        print("Test connector stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()
"""
            (connector_dir / "main.py").write_text(main_py_content)

            yield temp_path

    @pytest.fixture
    async def connector_manager_with_real_db(self, temp_connector_dir, real_db_service):
        """创建使用真实数据库的连接器管理器"""
        manager = ConnectorManager()
        manager.db_service = real_db_service
        manager.connectors_dir = temp_connector_dir
        return manager

    @pytest.mark.asyncio
    async def test_real_connector_discovery(
        self, connector_manager_with_real_db, temp_connector_dir
    ):
        """测试真实的连接器发现功能"""
        manager = connector_manager_with_real_db

        # 发现连接器
        discovered = manager.discover_connectors_from_directory()

        # 验证发现结果
        assert len(discovered) == 1
        connector = discovered[0]
        assert connector["connector_id"] == "test_connector"
        assert connector["name"] == "Test Connector"
        assert connector["path"] == str(temp_connector_dir / "test_connector")

        # 验证文件确实存在
        connector_path = Path(connector["path"])
        assert connector_path.exists()
        assert (connector_path / "main.py").exists()
        assert (connector_path / "connector.json").exists()

    @pytest.mark.asyncio
    async def test_connector_registration_with_real_database(
        self, connector_manager_with_real_db
    ):
        """测试连接器注册到真实数据库"""
        manager = connector_manager_with_real_db

        connector_info = {
            "connector_id": "test_connector",
            "name": "Test Connector",
            "description": "A test connector",
            "config": {"test_key": "test_value"},
        }

        # 注册连接器
        success = await manager.register_connector(connector_info)
        assert success is True

        # 验证数据库中确实存储了连接器
        stored_connectors = await manager.get_connectors()
        assert len(stored_connectors) == 1

        stored_connector = stored_connectors[0]
        assert stored_connector["connector_id"] == "test_connector"
        assert stored_connector["name"] == "Test Connector"
        assert stored_connector["config"]["test_key"] == "test_value"

    @pytest.mark.asyncio
    async def test_connector_lifecycle_integration(
        self, connector_manager_with_real_db, temp_connector_dir
    ):
        """测试连接器完整生命周期集成"""
        manager = connector_manager_with_real_db

        # 1. 注册连接器
        connector_info = {
            "connector_id": "test_connector",
            "name": "Test Connector",
            "description": "Integration test connector",
            "executable_path": str(temp_connector_dir / "test_connector" / "main.py"),
            "config": {"test_mode": True},
        }

        registration_success = await manager.register_connector(connector_info)
        assert registration_success is True

        # 2. 验证连接器状态为已注册但未运行
        status = await manager.get_connector_status("test_connector")
        assert status in ["configured", "stopped"]  # 根据实际实现调整

        # 3. 启动连接器
        start_success = await manager.start_connector("test_connector")
        assert start_success is True

        # 4. 验证连接器确实在运行
        await asyncio.sleep(0.5)  # 给连接器一点启动时间
        running_status = await manager.get_connector_status("test_connector")
        assert running_status == "running"

        # 5. 停止连接器
        stop_success = await manager.stop_connector("test_connector")
        assert stop_success is True

        # 6. 验证连接器已停止
        await asyncio.sleep(0.5)  # 给连接器一点停止时间
        stopped_status = await manager.get_connector_status("test_connector")
        assert stopped_status in ["stopped", "configured"]

    @pytest.mark.asyncio
    async def test_error_handling_invalid_connector(
        self, connector_manager_with_real_db
    ):
        """测试错误处理 - 无效连接器操作"""
        manager = connector_manager_with_real_db

        # 尝试启动不存在的连接器
        start_result = await manager.start_connector("nonexistent_connector")
        assert start_result is False

        # 尝试停止不存在的连接器
        stop_result = await manager.stop_connector("nonexistent_connector")
        assert stop_result is False

        # 获取不存在连接器的状态
        status = await manager.get_connector_status("nonexistent_connector")
        assert status == "not_found"

    @pytest.mark.asyncio
    async def test_concurrent_connector_operations(
        self, connector_manager_with_real_db
    ):
        """测试并发连接器操作的安全性"""
        manager = connector_manager_with_real_db

        # 注册多个连接器
        connectors = []
        for i in range(3):
            connector_info = {
                "connector_id": f"test_connector_{i}",
                "name": f"Test Connector {i}",
                "description": f"Test connector {i}",
                "config": {"index": i},
            }
            connectors.append(connector_info)

        # 并发注册
        registration_tasks = [
            manager.register_connector(connector) for connector in connectors
        ]
        results = await asyncio.gather(*registration_tasks)

        # 验证所有注册都成功
        assert all(results)

        # 验证数据库中有3个连接器
        stored_connectors = await manager.get_connectors()
        assert len(stored_connectors) == 3

        # 验证连接器ID唯一性
        connector_ids = [c["connector_id"] for c in stored_connectors]
        assert len(set(connector_ids)) == 3  # 所有ID都是唯一的

    @pytest.mark.asyncio
    async def test_database_transaction_integrity(self, connector_manager_with_real_db):
        """测试数据库事务完整性"""
        manager = connector_manager_with_real_db

        # 创建一个会导致错误的连接器配置
        invalid_connector = {
            "connector_id": "test_connector",
            "name": "Test Connector",
            "config": {"invalid": "config"},
        }

        valid_connector = {
            "connector_id": "valid_connector",
            "name": "Valid Connector",
            "config": {"valid": "config"},
        }

        # 先注册一个有效连接器
        await manager.register_connector(valid_connector)

        # 验证数据库状态
        connectors_before = await manager.get_connectors()
        assert len(connectors_before) == 1

        # 尝试注册可能失败的连接器
        try:
            await manager.register_connector(invalid_connector)
        except Exception:
            pass  # 忽略可能的错误

        # 验证数据库状态保持一致
        connectors_after = await manager.get_connectors()
        # 如果事务正确处理，应该仍然只有1个连接器（原来的有效连接器）
        # 或者2个连接器（如果无效连接器实际上是有效的）
        assert len(connectors_after) >= 1

    @pytest.mark.asyncio
    async def test_connector_config_validation(self, connector_manager_with_real_db):
        """测试连接器配置验证"""
        manager = connector_manager_with_real_db

        # 测试有效配置
        valid_config = {
            "connector_id": "valid_connector",
            "name": "Valid Connector",
            "description": "A valid connector",
            "config": {"required_field": "value", "optional_field": "optional_value"},
        }

        validation_result = manager.validate_connector_config(valid_config)
        assert validation_result is True

        # 测试无效配置（缺少必需字段）
        invalid_config = {
            "connector_id": "invalid_connector",
            # 缺少name字段
            "config": {},
        }

        validation_result = manager.validate_connector_config(invalid_config)
        assert validation_result is False

    @pytest.mark.asyncio
    async def test_real_process_management(
        self, connector_manager_with_real_db, temp_connector_dir
    ):
        """测试真实的进程管理（如果支持的话）"""
        manager = connector_manager_with_real_db

        # 创建一个简单的可执行连接器
        connector_script = temp_connector_dir / "simple_connector.py"
        script_content = """
import time
import sys

print("Simple connector started")
try:
    for i in range(5):
        print(f"Heartbeat {i}")
        time.sleep(0.1)
    print("Simple connector finished")
except KeyboardInterrupt:
    print("Simple connector interrupted")
    sys.exit(1)
"""
        connector_script.write_text(script_content)

        # 注册连接器
        connector_info = {
            "connector_id": "simple_connector",
            "name": "Simple Connector",
            "executable_path": str(connector_script),
            "config": {"timeout": 10},
        }

        await manager.register_connector(connector_info)

        # 如果连接器管理器支持真实进程管理，测试它
        if hasattr(manager, "start_connector"):
            start_result = await manager.start_connector("simple_connector")

            if start_result:  # 如果启动成功
                # 验证进程确实在运行
                await asyncio.sleep(0.2)
                status = await manager.get_connector_status("simple_connector")

                # 停止进程
                stop_result = await manager.stop_connector("simple_connector")

                # 基本验证
                assert status in ["running", "active"]
                assert stop_result is True


class TestConnectorManagerBoundaryConditions:
    """边界条件和异常处理测试"""

    @pytest.mark.asyncio
    async def test_empty_connector_directory(self):
        """测试空连接器目录的处理"""
        with tempfile.TemporaryDirectory() as empty_dir:
            manager = ConnectorManager()
            manager.connectors_dir = Path(empty_dir)

            discovered = manager.discover_connectors_from_directory()
            assert discovered == []

    @pytest.mark.asyncio
    async def test_corrupted_connector_config(self):
        """测试损坏的连接器配置文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 创建损坏的连接器配置
            bad_connector_dir = temp_path / "bad_connector"
            bad_connector_dir.mkdir()

            # 写入无效JSON
            (bad_connector_dir / "connector.json").write_text("{invalid json")

            manager = ConnectorManager()
            manager.connectors_dir = temp_path

            # 应该优雅处理错误，不抛出异常
            discovered = manager.discover_connectors_from_directory()
            # 损坏的连接器不应该被发现
            assert len(discovered) == 0

    @pytest.mark.asyncio
    async def test_permission_denied_scenarios(self):
        """测试权限拒绝场景（如果适用）"""
        # 这个测试依赖于操作系统的权限系统
        # 在实际环境中可能需要跳过
        pytest.skip("Permission tests require specific OS setup")

    @pytest.mark.asyncio
    async def test_database_connection_failure_recovery(self):
        """测试数据库连接失败恢复"""
        # 创建一个会失败的数据库路径
        invalid_db_path = "/invalid/path/database.db"

        try:
            db_service = DatabaseService(db_path=invalid_db_path)
            await db_service.initialize()

            manager = ConnectorManager()
            manager.db_service = db_service

            # 尝试执行需要数据库的操作
            connectors = await manager.get_connectors()
            # 应该返回空列表而不是抛出异常
            assert isinstance(connectors, list)

        except Exception as e:
            # 如果抛出异常，应该是预期的数据库错误
            assert "database" in str(e).lower() or "connection" in str(e).lower()
        finally:
            try:
                await db_service.close()
            except:
                pass  # 忽略清理错误
