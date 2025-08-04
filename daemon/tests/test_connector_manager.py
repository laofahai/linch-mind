#!/usr/bin/env python3
"""
连接器管理器测试
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path
import tempfile
import shutil
import json
from datetime import datetime, timezone


class TestConnectorManager:
    """连接器管理器测试类"""
    
    @pytest.fixture
    def connectors_dir(self, temp_dir):
        """创建临时连接器目录"""
        connectors_path = temp_dir / "connectors"
        connectors_path.mkdir()
        
        # 创建示例连接器
        fs_connector = connectors_path / "filesystem"
        fs_connector.mkdir()
        (fs_connector / "main.py").write_text("# Filesystem connector")
        (fs_connector / "config.yaml").write_text("""
name: "FileSystem Connector"
description: "Monitors filesystem changes"
version: "1.0.0"
""")
        
        return connectors_path
    
    @pytest.fixture
    def mock_database_service(self):
        """模拟数据库服务"""
        service = Mock()
        mock_session = Mock()
        service.get_session.return_value.__enter__.return_value = mock_session
        service.get_session.return_value.__exit__.return_value = None
        return service, mock_session
    
    @pytest.fixture
    def mock_process_manager(self):
        """模拟进程管理器"""
        manager = Mock()
        manager.start_process = AsyncMock(return_value=12345)
        manager.stop_process = AsyncMock(return_value=True)
        manager.get_process_info.return_value = {
            "pid": 12345,
            "status": "running",
            "cpu_percent": 1.5,
            "memory_percent": 2.0
        }
        manager.is_process_running.return_value = True
        return manager
    
    @pytest.fixture
    def connector_manager(self, connectors_dir, mock_database_service, mock_process_manager):
        """创建连接器管理器实例"""
        from services.connectors.connector_manager import ConnectorManager
        
        db_service, mock_session = mock_database_service
        
        with patch('services.connectors.connector_manager.get_database_service', return_value=db_service):
            with patch('services.connectors.connector_manager.get_process_manager', return_value=mock_process_manager):
                manager = ConnectorManager(connectors_dir=connectors_dir)
                manager.db_service = db_service
                manager.process_manager = mock_process_manager
                return manager
    
    @pytest.mark.connector
    def test_manager_initialization(self, connectors_dir):
        """测试连接器管理器初始化"""
        from services.connectors.connector_manager import ConnectorManager
        
        manager = ConnectorManager(connectors_dir=connectors_dir)
        
        assert manager.connectors_dir == connectors_dir
        assert hasattr(manager, 'registered_connectors')
        assert hasattr(manager, 'running_processes')
    
    @pytest.mark.connector
    def test_get_connector_manager_singleton(self, connectors_dir):
        """测试连接器管理器单例模式"""
        from services.connectors.connector_manager import get_connector_manager
        
        with patch('pathlib.Path') as mock_path:
            mock_path.return_value = connectors_dir
            
            manager1 = get_connector_manager(connectors_dir)
            manager2 = get_connector_manager(connectors_dir)
            
            assert manager1 is manager2  # 验证单例
    
    @pytest.mark.connector
    def test_discover_connectors_from_directory(self, connector_manager, connectors_dir):
        """测试从目录发现连接器"""
        discovered = connector_manager.discover_connectors_from_directory()
        
        assert len(discovered) >= 1
        filesystem_connector = next((c for c in discovered if c["connector_id"] == "filesystem"), None)
        assert filesystem_connector is not None
        assert filesystem_connector["name"] == "FileSystem Connector"
        assert filesystem_connector["path"] == str(connectors_dir / "filesystem")
    
    @pytest.mark.connector
    def test_scan_directory_for_connectors(self, connector_manager, temp_dir):
        """测试扫描指定目录寻找连接器"""
        # 创建测试连接器目录
        test_dir = temp_dir / "test_connectors"
        test_dir.mkdir()
        
        custom_connector = test_dir / "custom"
        custom_connector.mkdir()
        (custom_connector / "main.py").write_text("# Custom connector")
        (custom_connector / "connector.json").write_text(json.dumps({
            "name": "Custom Connector",
            "description": "A custom connector",
            "version": "1.0.0"
        }))
        
        connectors = connector_manager.scan_directory_for_connectors(str(test_dir))
        
        assert len(connectors) >= 1
        custom = next((c for c in connectors if c["connector_id"] == "custom"), None)
        assert custom is not None
        assert custom["name"] == "Custom Connector"
    
    @pytest.mark.connector
    def test_list_connectors(self, connector_manager, mock_database_service):
        """测试列出连接器"""
        db_service, mock_session = mock_database_service
        
        # 模拟数据库中的连接器
        from models.database_models import Connector
        mock_connectors = [
            Mock(spec=Connector, connector_id="filesystem", name="FileSystem", status="running", process_id=123),
            Mock(spec=Connector, connector_id="clipboard", name="Clipboard", status="configured", process_id=None)
        ]
        mock_session.query.return_value.all.return_value = mock_connectors
        
        connectors = connector_manager.list_connectors()
        
        assert len(connectors) == 2
        assert connectors[0]["connector_id"] == "filesystem"
        assert connectors[0]["status"] == "running"
        assert connectors[1]["connector_id"] == "clipboard"
        assert connectors[1]["status"] == "configured"
    
    @pytest.mark.connector
    @pytest.mark.asyncio
    async def test_start_connector_success(self, connector_manager, mock_database_service, mock_process_manager):
        """测试成功启动连接器"""
        db_service, mock_session = mock_database_service
        
        # 模拟数据库中的连接器
        from models.database_models import Connector
        mock_connector = Mock(spec=Connector)
        mock_connector.connector_id = "filesystem"
        mock_connector.name = "FileSystem"
        mock_connector.status = "configured"
        mock_connector.config = {"path": "../connectors/filesystem", "entry_point": "main.py"}
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_connector
        
        success = await connector_manager.start_connector("filesystem")
        
        assert success is True
        mock_process_manager.start_process.assert_called_once()
        assert mock_connector.status == "running"
        assert mock_connector.process_id == 12345
    
    @pytest.mark.connector
    @pytest.mark.asyncio
    async def test_start_connector_not_found(self, connector_manager, mock_database_service):
        """测试启动不存在的连接器"""
        db_service, mock_session = mock_database_service
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        
        success = await connector_manager.start_connector("nonexistent")
        
        assert success is False
    
    @pytest.mark.connector
    @pytest.mark.asyncio
    async def test_stop_connector_success(self, connector_manager, mock_database_service, mock_process_manager):
        """测试成功停止连接器"""
        db_service, mock_session = mock_database_service
        
        # 模拟数据库中的运行连接器
        from models.database_models import Connector
        mock_connector = Mock(spec=Connector)
        mock_connector.connector_id = "filesystem"
        mock_connector.name = "FileSystem"
        mock_connector.status = "running"
        mock_connector.process_id = 12345
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_connector
        
        success = await connector_manager.stop_connector("filesystem")
        
        assert success is True
        mock_process_manager.stop_process.assert_called_once_with(12345)
        assert mock_connector.status == "configured"
        assert mock_connector.process_id is None
    
    @pytest.mark.connector
    @pytest.mark.asyncio
    async def test_stop_connector_not_running(self, connector_manager, mock_database_service):
        """测试停止未运行的连接器"""
        db_service, mock_session = mock_database_service
        
        # 模拟数据库中的已配置连接器
        from models.database_models import Connector
        mock_connector = Mock(spec=Connector)
        mock_connector.connector_id = "filesystem"
        mock_connector.status = "configured"
        mock_connector.process_id = None
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_connector
        
        success = await connector_manager.stop_connector("filesystem")
        
        assert success is False  # 不能停止未运行的连接器
    
    @pytest.mark.connector
    def test_get_connector_info(self, connector_manager, mock_database_service):
        """测试获取连接器信息"""
        db_service, mock_session = mock_database_service
        
        from models.database_models import Connector
        mock_connector = Mock(spec=Connector)
        mock_connector.connector_id = "filesystem"
        mock_connector.name = "FileSystem"
        mock_connector.description = "File system connector"
        mock_connector.status = "running"
        mock_connector.config = {"path": "/test"}
        mock_connector.process_id = 12345
        mock_connector.created_at = datetime.now(timezone.utc)
        mock_connector.updated_at = datetime.now(timezone.utc)
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_connector
        
        info = connector_manager.get_connector_info("filesystem")
        
        assert info is not None
        assert info["connector_id"] == "filesystem"
        assert info["name"] == "FileSystem"
        assert info["status"] == "running"
        assert info["process_id"] == 12345
    
    @pytest.mark.connector
    def test_get_connector_info_not_found(self, connector_manager, mock_database_service):
        """测试获取不存在连接器的信息"""
        db_service, mock_session = mock_database_service
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        
        info = connector_manager.get_connector_info("nonexistent")
        
        assert info is None
    
    @pytest.mark.connector
    def test_health_check_all_connectors(self, connector_manager, mock_database_service, mock_process_manager):
        """测试所有连接器健康检查"""
        db_service, mock_session = mock_database_service
        
        # 模拟数据库中的连接器
        from models.database_models import Connector
        mock_connectors = [
            Mock(spec=Connector, connector_id="running", process_id=123, status="running"),
            Mock(spec=Connector, connector_id="configured", process_id=None, status="configured")
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = mock_connectors
        
        # 模拟进程检查
        def mock_is_running(pid):
            return pid == 123  # 只有PID 123的进程在运行
        
        mock_process_manager.is_process_running.side_effect = mock_is_running
        
        connector_manager.health_check_all_connectors()
        
        # 验证健康检查逻辑
        assert mock_process_manager.is_process_running.call_count >= 1
    
    @pytest.mark.connector
    def test_register_connector(self, connector_manager, mock_database_service):
        """测试注册连接器"""
        db_service, mock_session = mock_database_service
        
        connector_info = {
            "connector_id": "new_connector",
            "name": "New Connector",
            "description": "A new connector",
            "path": "/path/to/connector",
            "config": {"key": "value"}
        }
        
        success = connector_manager.register_connector(connector_info)
        
        assert success is True
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @pytest.mark.connector
    def test_unregister_connector(self, connector_manager, mock_database_service):
        """测试注销连接器"""
        db_service, mock_session = mock_database_service
        
        # 模拟存在的连接器
        from models.database_models import Connector
        mock_connector = Mock(spec=Connector)
        mock_connector.connector_id = "to_remove"
        mock_connector.status = "configured"
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_connector
        
        success = connector_manager.unregister_connector("to_remove")
        
        assert success is True
        mock_session.delete.assert_called_once_with(mock_connector)
        mock_session.commit.assert_called_once()
    
    @pytest.mark.connector
    def test_unregister_running_connector(self, connector_manager, mock_database_service):
        """测试注销运行中的连接器（应该失败）"""
        db_service, mock_session = mock_database_service
        
        # 模拟运行中的连接器
        from models.database_models import Connector
        mock_connector = Mock(spec=Connector)
        mock_connector.connector_id = "running_connector"
        mock_connector.status = "running"
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_connector
        
        success = connector_manager.unregister_connector("running_connector")
        
        assert success is False  # 不能注销运行中的连接器
        mock_session.delete.assert_not_called()
    
    @pytest.mark.connector
    def test_validate_connector_config(self, connector_manager):
        """测试验证连接器配置"""
        valid_config = {
            "path": "/valid/path",
            "entry_point": "main.py",
            "timeout": 30
        }
        
        invalid_config = {
            "entry_point": "main.py"
            # 缺少必需的path
        }
        
        assert connector_manager.validate_connector_config("test", valid_config) is True
        assert connector_manager.validate_connector_config("test", invalid_config) is False
    
    @pytest.mark.connector
    def test_get_connector_logs(self, connector_manager, temp_dir):
        """测试获取连接器日志"""
        # 创建测试日志文件
        log_dir = temp_dir / "logs"
        log_dir.mkdir()
        log_file = log_dir / "filesystem.log"
        log_content = """
2025-01-01 10:00:00 INFO Starting connector
2025-01-01 10:00:01 DEBUG Processing file change
2025-01-01 10:00:02 INFO Connector ready
"""
        log_file.write_text(log_content.strip())
        
        with patch.object(connector_manager, '_get_log_file_path', return_value=log_file):
            logs = connector_manager.get_connector_logs("filesystem", lines=10)
        
        assert logs is not None
        assert "Starting connector" in logs
        assert "Connector ready" in logs
    
    @pytest.mark.connector
    def test_get_connector_logs_not_found(self, connector_manager):
        """测试获取不存在的连接器日志"""
        with patch.object(connector_manager, '_get_log_file_path', return_value=Path("/nonexistent/log.txt")):
            logs = connector_manager.get_connector_logs("nonexistent")
        
        assert logs == ""  # 应该返回空字符串
    
    @pytest.mark.connector
    def test_connector_stats(self, connector_manager, mock_database_service):
        """测试连接器统计信息"""
        db_service, mock_session = mock_database_service
        
        # 模拟不同状态的连接器
        from models.database_models import Connector
        mock_connectors = [
            Mock(spec=Connector, status="running"),
            Mock(spec=Connector, status="running"),
            Mock(spec=Connector, status="configured"),
            Mock(spec=Connector, status="error")
        ]
        mock_session.query.return_value.all.return_value = mock_connectors
        
        stats = connector_manager.get_connector_stats()
        
        assert stats["total"] == 4
        assert stats["running"] == 2
        assert stats["configured"] == 1
        assert stats["error"] == 1
        assert stats["stopped"] == 0
    
    @pytest.mark.connector
    @pytest.mark.asyncio
    async def test_batch_operations(self, connector_manager, mock_database_service):
        """测试批量操作"""
        db_service, mock_session = mock_database_service
        
        # 模拟多个连接器
        from models.database_models import Connector
        mock_connectors = [
            Mock(spec=Connector, connector_id="conn1", status="configured"),
            Mock(spec=Connector, connector_id="conn2", status="configured")
        ]
        
        def mock_filter_by(connector_id):
            connector = next((c for c in mock_connectors if c.connector_id == connector_id), None)
            mock_query = Mock()
            mock_query.first.return_value = connector
            return mock_query
        
        mock_session.query.return_value.filter_by.side_effect = mock_filter_by
        
        # 批量启动
        connector_ids = ["conn1", "conn2"]
        results = await connector_manager.batch_start_connectors(connector_ids)
        
        assert len(results) == 2
        assert all(result["success"] for result in results.values())
    
    @pytest.mark.connector
    def test_error_handling(self, connector_manager, mock_database_service):
        """测试错误处理"""
        db_service, mock_session = mock_database_service
        
        # 模拟数据库错误
        mock_session.query.side_effect = Exception("Database error")
        
        connectors = connector_manager.list_connectors()
        
        # 应该返回空列表而不是抛出异常
        assert connectors == []