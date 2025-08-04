#!/usr/bin/env python3
"""
连接器生命周期API测试
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone
from models.database_models import Connector


class TestConnectorLifecycleAPI:
    """连接器生命周期API测试类"""
    
    @pytest.mark.api
    def test_discover_connectors_success(self, client, mock_database_service, sample_connector):
        """测试成功发现连接器"""
        # 设置mock返回值
        mock_database_service.get_session.return_value.__enter__.return_value.query.return_value.all.return_value = [sample_connector]
        
        response = client.get("/connector-lifecycle/discovery")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "connectors" in data["data"]
        assert data["data"]["total"] >= 2  # 至少有官方的filesystem和clipboard
        
        # 验证官方连接器存在
        connector_ids = [c["connector_id"] for c in data["data"]["connectors"]]
        assert "filesystem" in connector_ids or any(c["connector_id"] == "filesystem" for c in data["data"]["connectors"])
        assert "clipboard" in connector_ids or any(c["connector_id"] == "clipboard" for c in data["data"]["connectors"])
    
    @pytest.mark.api
    def test_discover_connectors_empty(self, client, mock_database_service):
        """测试没有注册连接器时的发现"""
        # 设置空的返回值
        mock_database_service.get_session.return_value.__enter__.return_value.query.return_value.all.return_value = []
        
        response = client.get("/connector-lifecycle/discovery")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] == 2  # 只有官方的两个连接器
    
    @pytest.mark.api
    def test_get_connectors_all(self, client, test_database, sample_connector):
        """测试获取所有连接器"""
        response = client.get("/connector-lifecycle/collectors")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "collectors" in data["data"]
        assert isinstance(data["data"]["collectors"], list)
    
    @pytest.mark.api
    def test_get_connectors_by_id(self, client, test_database, sample_connector):
        """测试按ID获取连接器"""
        response = client.get("/connector-lifecycle/collectors?connector_id=test_connector")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        collectors = data["data"]["collectors"]
        assert all(c["collector_id"] == "test_connector" for c in collectors)
    
    @pytest.mark.api
    def test_get_connectors_by_state(self, client, test_database):
        """测试按状态过滤连接器"""
        # 创建不同状态的连接器
        from tests.conftest import create_test_connector
        create_test_connector(test_database, connector_id="running_conn", status="running")
        create_test_connector(test_database, connector_id="error_conn", status="error")
        
        # 测试获取运行中的连接器
        response = client.get("/connector-lifecycle/collectors?state=running")
        
        assert response.status_code == 200
        data = response.json()
        collectors = data["data"]["collectors"]
        assert all(c["state"] == "running" for c in collectors)
    
    @pytest.mark.api
    def test_get_connector_detail(self, client, mock_connector_manager):
        """测试获取连接器详情"""
        response = client.get("/connector-lifecycle/collectors/filesystem")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["collector"]["collector_id"] == "filesystem"
        assert "state" in data["data"]["collector"]
    
    @pytest.mark.api
    def test_get_connector_not_found(self, client, mock_connector_manager):
        """测试获取不存在的连接器"""
        mock_connector_manager.list_connectors.return_value = []
        
        response = client.get("/connector-lifecycle/collectors/nonexistent")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_start_connector_success(self, client, mock_connector_manager):
        """测试成功启动连接器"""
        response = client.post("/connector-lifecycle/collectors/filesystem/start")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["state"] == "running"
        mock_connector_manager.start_connector.assert_called_once_with("filesystem")
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_start_connector_failure(self, client, mock_connector_manager):
        """测试启动连接器失败"""
        mock_connector_manager.start_connector.return_value = False
        
        response = client.post("/connector-lifecycle/collectors/filesystem/start")
        
        assert response.status_code == 400
        assert "Failed to start" in response.json()["detail"]
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_stop_connector_success(self, client, mock_connector_manager):
        """测试成功停止连接器"""
        response = client.post("/connector-lifecycle/collectors/filesystem/stop")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["state"] == "stopped"
        mock_connector_manager.stop_connector.assert_called_once_with("filesystem")
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_restart_connector_success(self, client, mock_connector_manager):
        """测试成功重启连接器"""
        response = client.post("/connector-lifecycle/collectors/filesystem/restart")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["state"] == "running"
        
        # 验证先停止后启动
        assert mock_connector_manager.stop_connector.call_count == 1
        assert mock_connector_manager.start_connector.call_count == 1
    
    @pytest.mark.api
    def test_delete_connector_not_implemented(self, client):
        """测试删除连接器（未实现）"""
        response = client.delete("/connector-lifecycle/collectors/filesystem")
        
        assert response.status_code == 501
        assert "not implemented" in response.json()["detail"].lower()
    
    @pytest.mark.api
    def test_get_states_overview(self, client, mock_connector_manager):
        """测试获取状态概览"""
        response = client.get("/connector-lifecycle/states")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total_collectors" in data["data"]
        assert "state_counts" in data["data"]
        assert data["data"]["total_collectors"] == 2
    
    @pytest.mark.api
    def test_scan_directory_success(self, client, mock_connector_manager):
        """测试扫描目录寻找连接器"""
        mock_connector_manager.scan_directory_for_connectors.return_value = [
            {
                "connector_id": "custom_connector",
                "name": "Custom Connector",
                "description": "A custom connector",
                "path": "/test/path/custom"
            }
        ]
        
        response = client.post("/connector-lifecycle/scan-directory", json={
            "directory_path": "/test/path"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["connectors"]) == 1
        assert data["data"]["connectors"][0]["connector_id"] == "custom_connector"
    
    @pytest.mark.api
    def test_scan_directory_missing_path(self, client):
        """测试扫描目录缺少路径参数"""
        response = client.post("/connector-lifecycle/scan-directory", json={})
        
        assert response.status_code == 400
        assert "directory_path is required" in response.json()["detail"]
    
    @pytest.mark.api
    def test_create_connector_success(self, client, mock_database_service, mock_connector_manager):
        """测试成功创建连接器"""
        # Mock数据库查询返回None（不存在）
        mock_session = Mock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_database_service.get_session.return_value.__enter__.return_value = mock_session
        
        response = client.post("/connector-lifecycle/collectors", json={
            "connector_id": "new_connector",
            "display_name": "New Connector",
            "config": {"test": "value"},
            "auto_start": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["collector_id"] == "new_connector"
        assert data["data"]["state"] == "running"  # 因为auto_start=True
    
    @pytest.mark.api
    def test_create_connector_already_exists(self, client, mock_database_service):
        """测试创建已存在的连接器"""
        # Mock数据库查询返回存在的连接器
        mock_session = Mock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = Mock()
        mock_database_service.get_session.return_value.__enter__.return_value = mock_session
        
        response = client.post("/connector-lifecycle/collectors", json={
            "connector_id": "existing",
            "display_name": "Existing Connector"
        })
        
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]
    
    @pytest.mark.api
    def test_create_connector_missing_params(self, client):
        """测试创建连接器缺少必需参数"""
        response = client.post("/connector-lifecycle/collectors", json={
            "connector_id": "new_connector"
            # 缺少display_name
        })
        
        assert response.status_code == 400
        assert "required" in response.json()["detail"]
    
    @pytest.mark.api
    def test_health_check(self, client, mock_connector_manager):
        """测试健康检查"""
        mock_connector_manager.health_check_all_connectors = Mock()
        
        response = client.get("/connector-lifecycle/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "system_status" in data["data"]
        assert data["data"]["system_status"] in ["healthy", "degraded", "unhealthy"]
        assert "total_connectors" in data["data"]
        assert "timestamp" in data["data"]
    
    @pytest.mark.api
    def test_state_mapping_functions(self):
        """测试状态映射函数"""
        from api.routers.connector_lifecycle_api import _map_status_to_state, _map_state_to_status
        
        # 测试status到state的映射
        assert _map_status_to_state("running") == "running"
        assert _map_status_to_state("configured") == "configured"
        assert _map_status_to_state("error") == "error"
        assert _map_status_to_state("stopped") == "configured"
        assert _map_status_to_state("unknown") == "configured"  # 默认值
        
        # 测试state到status的反向映射
        assert _map_state_to_status("running") == "running"
        assert _map_state_to_status("configured") == "configured"
        assert _map_state_to_status("error") == "error"
        assert _map_state_to_status("enabled") == "configured"
        assert _map_state_to_status("unknown") == "configured"  # 默认值
    
    @pytest.mark.api
    def test_convert_connector_to_collector(self):
        """测试连接器模型转换"""
        from api.routers.connector_lifecycle_api import _convert_connector_to_collector
        from datetime import datetime
        
        # 创建模拟的连接器对象
        mock_connector = Mock()
        mock_connector.connector_id = "test_id"
        mock_connector.name = "Test Name"
        mock_connector.config = {"key": "value"}
        mock_connector.status = "running"
        mock_connector.enabled = True
        mock_connector.auto_start = True
        mock_connector.process_id = 1234
        mock_connector.last_heartbeat = datetime.now(timezone.utc)
        mock_connector.data_count = 100
        mock_connector.error_message = None
        mock_connector.created_at = datetime.now(timezone.utc)
        mock_connector.updated_at = datetime.now(timezone.utc)
        
        result = _convert_connector_to_collector(mock_connector)
        
        assert result["collector_id"] == "test_id"
        assert result["display_name"] == "Test Name"
        assert result["config"] == {"key": "value"}
        assert result["state"] == "running"
        assert result["enabled"] is True
        assert result["auto_start"] is True
        assert result["process_id"] == 1234
        assert result["data_count"] == 100
        assert result["last_heartbeat"] is not None
        assert result["created_at"] is not None
        assert result["updated_at"] is not None