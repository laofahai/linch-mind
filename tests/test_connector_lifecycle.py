#!/usr/bin/env python3
"""
连接器生命周期管理测试

测试连接器的安装、卸载、数据交互、配置管理等功能
"""

import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from daemon.services.connectors.connector_manager import ConnectorManager


class TestConnectorLifecycle(unittest.TestCase):
    """连接器生命周期测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        self.connectors_dir = Path(self.temp_dir) / "connectors"
        self.connectors_dir.mkdir()
        
        # Mock数据库服务
        self.mock_db_service = MagicMock()
        self.mock_session = MagicMock()
        self.mock_db_service.get_session.return_value.__enter__ = MagicMock(return_value=self.mock_session)
        self.mock_db_service.get_session.return_value.__exit__ = MagicMock(return_value=False)
        
        # 创建连接器管理器实例
        with patch('daemon.services.connectors.connector_manager.get_database_service') as mock_get_db:
            mock_get_db.return_value = self.mock_db_service
            self.manager = ConnectorManager(self.connectors_dir)

    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_connector_registration(self):
        """测试连接器注册功能"""
        # 创建测试连接器目录和配置文件
        test_connector_dir = self.connectors_dir / "test_connector"
        test_connector_dir.mkdir()
        
        config_data = {
            "id": "test_connector",
            "name": "测试连接器",
            "description": "用于测试的连接器",
            "version": "1.0.0",
            "entry_point": "main.py"
        }
        
        config_file = test_connector_dir / "connector.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f)
        
        # 创建入口文件
        main_file = test_connector_dir / "main.py"
        main_file.write_text("print('Hello from test connector')")
        
        # 测试注册
        self.manager.register_connector(
            "test_connector",
            "测试连接器", 
            "用于测试的连接器",
            test_connector_dir
        )
        
        # 验证注册调用
        self.mock_session.add.assert_called()
        self.mock_session.commit.assert_called()

    @patch('daemon.services.connectors.connector_manager.subprocess.Popen')
    @patch('daemon.services.connectors.connector_manager.psutil')
    async def test_connector_start_stop(self, mock_psutil, mock_popen):
        """测试连接器启动和停止"""
        # Mock连接器对象
        mock_connector = MagicMock()
        mock_connector.connector_id = "test_connector"
        mock_connector.status = "stopped"
        mock_connector.config = {
            "executable_path": str(self.connectors_dir / "test_connector" / "main.py")
        }
        
        # Mock查询结果
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = mock_connector
        
        # Mock进程
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        # 创建测试文件
        test_dir = self.connectors_dir / "test_connector"
        test_dir.mkdir()
        test_file = test_dir / "main.py"
        test_file.write_text("print('test')")
        
        # 测试启动
        success = await self.manager.start_connector("test_connector")
        
        self.assertTrue(success)
        self.assertEqual(mock_connector.status, "running")
        self.assertEqual(mock_connector.process_id, 12345)
        mock_popen.assert_called_once()
        
        # 测试停止
        mock_connector.status = "running"
        mock_connector.process_id = 12345
        
        success = await self.manager.stop_connector("test_connector")
        
        self.assertTrue(success)
        mock_process.terminate.assert_called_once()

    def test_connector_health_check(self):
        """测试连接器健康检查"""
        with patch('daemon.services.connectors.connector_manager.psutil') as mock_psutil:
            # Mock连接器对象
            mock_connector = MagicMock()
            mock_connector.connector_id = "test_connector"
            mock_connector.process_id = 12345
            mock_connector.last_heartbeat = None
            
            # Mock psutil
            mock_psutil.pid_exists.return_value = True
            mock_process = MagicMock()
            mock_process.status.return_value = "running"
            mock_process.name.return_value = "python"
            mock_process.cmdline.return_value = ["python", "main.py"]
            mock_psutil.Process.return_value = mock_process
            
            # 测试健康检查
            health_status = self.manager._check_connector_health(mock_connector)
            
            self.assertTrue(health_status["healthy"])
            self.assertIsNone(health_status["error"])

    def test_connector_statistics(self):
        """测试连接器统计信息获取"""
        # Mock数据源和实体查询
        mock_data_sources = [MagicMock()]
        mock_data_sources[0].id = "ds1"
        
        self.mock_session.query.return_value.filter_by.return_value.all.return_value = mock_data_sources
        self.mock_session.query.return_value.filter.return_value.count.return_value = 5
        
        # 测试统计信息获取
        stats = self.manager._get_connector_statistics("test_connector")
        
        self.assertEqual(stats["data_sources"], 1)
        self.assertEqual(stats["entities"], 5)

    def test_system_health_overview(self):
        """测试系统健康概览"""
        with patch('daemon.services.connectors.connector_manager.psutil'):
            # Mock连接器列表
            mock_connectors = [
                MagicMock(status="running", connector_id="conn1", process_id=123),
                MagicMock(status="error", connector_id="conn2", process_id=None),
                MagicMock(status="stopped", connector_id="conn3", process_id=None),
            ]
            
            self.mock_session.query.return_value.all.return_value = mock_connectors
            
            # Mock健康检查结果
            with patch.object(self.manager, '_check_connector_health') as mock_health_check:
                mock_health_check.return_value = {"healthy": True, "error": None}
                
                with patch.object(self.manager, '_get_connector_statistics') as mock_stats:
                    mock_stats.return_value = {"entities": 10, "data_sources": 2}
                    
                    # 测试系统健康概览
                    overview = self.manager.get_system_health_overview()
                    
                    self.assertEqual(overview["total_connectors"], 3)
                    self.assertEqual(overview["healthy_connectors"], 1)  # 只有running的会检查健康状态
                    self.assertIn("overall_status", overview)
                    self.assertIn("health_score", overview)

    async def test_auto_restart_failed_connectors(self):
        """测试自动重启失败的连接器"""
        # Mock失败的连接器
        mock_failed_connector = MagicMock()
        mock_failed_connector.connector_id = "failed_connector"
        mock_failed_connector.auto_start = True
        
        self.mock_session.query.return_value.filter_by.return_value.all.return_value = [mock_failed_connector]
        
        # Mock启动连接器
        with patch.object(self.manager, 'start_connector', new_callable=AsyncMock) as mock_start:
            mock_start.return_value = True
            
            # 测试自动重启
            results = await self.manager.auto_restart_failed_connectors()
            
            self.assertEqual(len(results), 1)
            self.assertTrue(results[0]["success"])
            self.assertEqual(results[0]["connector_id"], "failed_connector")
            mock_start.assert_called_once_with("failed_connector")


class TestConnectorDataInteraction(unittest.TestCase):
    """连接器数据交互测试类"""

    def setUp(self):
        """测试前准备"""
        self.mock_db_service = MagicMock()
        self.mock_session = MagicMock()
        self.mock_db_service.get_session.return_value.__enter__ = MagicMock(return_value=self.mock_session)
        self.mock_db_service.get_session.return_value.__exit__ = MagicMock(return_value=False)

    @patch('daemon.api.routers.connector_data_api.get_database_service')
    async def test_connector_heartbeat(self, mock_get_db):
        """测试连接器心跳接口"""
        from daemon.api.routers.connector_data_api import connector_heartbeat
        from daemon.api.routers.connector_data_api import ConnectorHeartbeatRequest
        
        mock_get_db.return_value = self.mock_db_service
        
        # Mock连接器对象
        mock_connector = MagicMock()
        mock_connector.connector_id = "test_connector"
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = mock_connector
        
        # 创建心跳请求
        heartbeat_request = ConnectorHeartbeatRequest(
            connector_id="test_connector",
            status="running",
            process_id=12345,
            metadata={"version": "1.0.0"}
        )
        
        # 测试心跳处理
        response = await connector_heartbeat(heartbeat_request)
        
        self.assertTrue(response["success"])
        self.assertIsNotNone(mock_connector.last_heartbeat)
        self.assertEqual(mock_connector.status, "running")
        self.assertEqual(mock_connector.process_id, 12345)

    @patch('daemon.api.routers.connector_data_api.get_database_service')
    @patch('daemon.api.routers.connector_data_api.get_storage_orchestrator')
    async def test_data_batch_processing(self, mock_get_storage, mock_get_db):
        """测试数据批次处理"""
        from daemon.api.routers.connector_data_api import receive_data_batch
        from daemon.api.routers.connector_data_api import ConnectorDataBatch
        
        mock_get_db.return_value = self.mock_db_service
        mock_storage = AsyncMock()
        mock_get_storage.return_value = mock_storage
        
        # Mock连接器对象
        mock_connector = MagicMock()
        mock_connector.connector_id = "test_connector"
        mock_connector.status = "running"
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = mock_connector
        
        # 创建数据批次
        data_batch = ConnectorDataBatch(
            connector_id="test_connector",
            data_source_id="source1",
            entities=[
                {
                    "entity_id": "entity1",
                    "name": "测试实体",
                    "entity_type": "document",
                    "content": "测试内容"
                }
            ],
            relationships=[
                {
                    "source_entity": "entity1",
                    "target_entity": "entity2", 
                    "relationship_type": "references"
                }
            ]
        )
        
        # Mock后台任务
        mock_background_tasks = MagicMock()
        
        # 测试数据批次接收
        response = await receive_data_batch(data_batch, mock_background_tasks)
        
        self.assertTrue(response["success"])
        self.assertIn("batch_id", response)
        mock_background_tasks.add_task.assert_called_once()


class TestConnectorConfiguration(unittest.TestCase):
    """连接器配置管理测试类"""

    def setUp(self):
        """测试前准备"""
        self.mock_config_service = MagicMock()

    @patch('daemon.api.routers.connector_config_api.get_connector_config_service')
    async def test_config_validation(self, mock_get_service):
        """测试配置验证"""
        from daemon.api.routers.connector_config_api import validate_config
        from daemon.api.routers.connector_config_api import ValidateConfigRequest
        
        mock_get_service.return_value = self.mock_config_service
        
        # Mock验证结果
        self.mock_config_service.validate_config.return_value = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "normalized_config": {"key": "value"}
        }
        
        # 创建验证请求
        validate_request = ValidateConfigRequest(
            connector_id="test_connector",
            config={"key": "value"}
        )
        
        # 测试配置验证
        response = await validate_config(validate_request, self.mock_config_service)
        
        self.assertTrue(response.success)
        self.assertTrue(response.data["valid"])
        self.mock_config_service.validate_config.assert_called_once()

    @patch('daemon.api.routers.connector_config_api.get_connector_config_service')
    async def test_hot_reload_config(self, mock_get_service):
        """测试配置热重载"""
        from daemon.api.routers.connector_config_api import hot_reload_config
        
        mock_get_service.return_value = self.mock_config_service
        
        # Mock热重载结果
        self.mock_config_service.trigger_hot_reload.return_value = {
            "success": True,
            "hot_reload_supported": True,
            "reload_triggered": True,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # 测试热重载
        response = await hot_reload_config("test_connector", self.mock_config_service)
        
        self.assertTrue(response.success)
        self.assertTrue(response.data["hot_reload_supported"])
        self.mock_config_service.trigger_hot_reload.assert_called_once_with("test_connector")


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)