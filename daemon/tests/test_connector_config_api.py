#!/usr/bin/env python3
"""
连接器配置管理API测试
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone


class TestConnectorConfigAPI:
    """连接器配置管理API测试类"""
    
    @pytest.fixture
    def mock_config_service(self):
        """模拟配置服务"""
        service = Mock()
        # 设置异步方法
        service.get_config_schema = AsyncMock()
        service.get_current_config = AsyncMock()
        service.validate_config = AsyncMock()
        service.update_config = AsyncMock()
        service.reset_config = AsyncMock()
        service.get_config_history = AsyncMock()
        service.get_all_schemas = AsyncMock()
        service.register_runtime_schema = AsyncMock()
        return service
    
    @pytest.fixture
    def sample_config_schema(self):
        """示例配置schema"""
        return {
            "schema": {
                "type": "object",
                "properties": {
                    "watch_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "title": "监控路径"
                    },
                    "interval": {
                        "type": "integer",
                        "minimum": 1,
                        "default": 60,
                        "title": "检查间隔(秒)"
                    }
                },
                "required": ["watch_paths"]
            },
            "ui_schema": {
                "watch_paths": {"ui:widget": "textarea"},
                "interval": {"ui:widget": "updown"}
            },
            "default_values": {
                "watch_paths": ["/home/user/documents"],
                "interval": 60
            },
            "version": "1.0.0"
        }
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_config_schema_success(self, client, mock_config_service, sample_config_schema):
        """测试成功获取配置schema"""
        mock_config_service.get_config_schema.return_value = sample_config_schema
        
        with patch('api.routers.connector_config_api.get_connector_config_service', return_value=mock_config_service):
            response = client.get("/connector-config/schema/filesystem")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["connector_id"] == "filesystem"
        assert "schema" in data["data"]
        assert "ui_schema" in data["data"]
        assert "default_values" in data["data"]
        assert data["data"]["schema_version"] == "1.0.0"
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_config_schema_not_found(self, client, mock_config_service):
        """测试获取不存在的配置schema"""
        mock_config_service.get_config_schema.return_value = None
        
        with patch('api.routers.connector_config_api.get_connector_config_service', return_value=mock_config_service):
            response = client.get("/connector-config/schema/nonexistent")
        
        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_current_config_success(self, client, mock_config_service):
        """测试成功获取当前配置"""
        current_config_data = {
            "current_config": {"watch_paths": ["/test"], "interval": 30},
            "config_schema": {"type": "object"},
            "config_version": "1.0.0",
            "config_valid": True,
            "validation_errors": [],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        mock_config_service.get_current_config.return_value = current_config_data
        
        with patch('api.routers.connector_config_api.get_connector_config_service', return_value=mock_config_service):
            response = client.get("/connector-config/current/filesystem")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["connector_id"] == "filesystem"
        assert data["data"]["config"] == {"watch_paths": ["/test"], "interval": 30}
        assert data["data"]["config_valid"] is True
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_current_config_not_found(self, client, mock_config_service):
        """测试获取不存在连接器的配置"""
        mock_config_service.get_current_config.return_value = None
        
        with patch('api.routers.connector_config_api.get_connector_config_service', return_value=mock_config_service):
            response = client.get("/connector-config/current/nonexistent")
        
        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_validate_config_valid(self, client, mock_config_service):
        """测试配置验证通过"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "normalized_config": {"watch_paths": ["/test"], "interval": 60}
        }
        mock_config_service.validate_config.return_value = validation_result
        
        with patch('api.routers.connector_config_api.get_connector_config_service', return_value=mock_config_service):
            response = client.post("/connector-config/validate", json={
                "connector_id": "filesystem",
                "config": {"watch_paths": ["/test"], "interval": 60}
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["valid"] is True
        assert len(data["data"]["errors"]) == 0
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_validate_config_invalid(self, client, mock_config_service):
        """测试配置验证失败"""
        validation_result = {
            "valid": False,
            "errors": ["watch_paths is required", "interval must be positive"],
            "warnings": [],
            "normalized_config": {}
        }
        mock_config_service.validate_config.return_value = validation_result
        
        with patch('api.routers.connector_config_api.get_connector_config_service', return_value=mock_config_service):
            response = client.post("/connector-config/validate", json={
                "connector_id": "filesystem",
                "config": {"interval": -1}
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["data"]["valid"] is False
        assert len(data["data"]["errors"]) == 2
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_update_config_success(self, client, mock_config_service):
        """测试成功更新配置"""
        # 验证成功
        validation_result = {
            "valid": True,
            "errors": [],
            "normalized_config": {"watch_paths": ["/new/path"], "interval": 120}
        }
        mock_config_service.validate_config.return_value = validation_result
        
        # 更新成功
        update_result = {
            "config_version": "1.0.1",
            "hot_reload_applied": True,
            "requires_restart": False,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        mock_config_service.update_config.return_value = update_result
        
        with patch('api.routers.connector_config_api.get_connector_config_service', return_value=mock_config_service):
            response = client.put("/connector-config/update", json={
                "connector_id": "filesystem",
                "config": {"watch_paths": ["/new/path"], "interval": 120},
                "config_version": "1.0.1",
                "change_reason": "用户更新路径"
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["config_version"] == "1.0.1"
        assert data["data"]["hot_reload_applied"] is True
        assert data["data"]["requires_restart"] is False
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_update_config_validation_failed(self, client, mock_config_service):
        """测试更新配置时验证失败"""
        validation_result = {
            "valid": False,
            "errors": ["Invalid configuration"],
            "normalized_config": {}
        }
        mock_config_service.validate_config.return_value = validation_result
        
        with patch('api.routers.connector_config_api.get_connector_config_service', return_value=mock_config_service):
            response = client.put("/connector-config/update", json={
                "connector_id": "filesystem",
                "config": {"invalid": "config"}
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "验证失败" in data["message"]
        assert len(data["data"]["errors"]) > 0
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_reset_config_to_defaults(self, client, mock_config_service):
        """测试重置配置到默认值"""
        reset_result = {
            "config": {"watch_paths": ["/default/path"], "interval": 60},
            "requires_restart": True
        }
        mock_config_service.reset_config.return_value = reset_result
        
        with patch('api.routers.connector_config_api.get_connector_config_service', return_value=mock_config_service):
            response = client.post("/connector-config/reset", json={
                "connector_id": "filesystem",
                "to_defaults": True
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["reset_to"] == "defaults"
        assert data["data"]["requires_restart"] is True
        assert "config" in data["data"]
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_reset_config_to_empty(self, client, mock_config_service):
        """测试重置配置到空"""
        reset_result = {
            "config": {},
            "requires_restart": False
        }
        mock_config_service.reset_config.return_value = reset_result
        
        with patch('api.routers.connector_config_api.get_connector_config_service', return_value=mock_config_service):
            response = client.post("/connector-config/reset", json={
                "connector_id": "filesystem",
                "to_defaults": False
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["reset_to"] == "empty"
        assert data["data"]["config"] == {}
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_config_history(self, client, mock_config_service):
        """测试获取配置历史"""
        history_data = {
            "records": [
                {
                    "version": "1.0.2",
                    "config": {"watch_paths": ["/new"], "interval": 120},
                    "change_reason": "用户更新",
                    "changed_at": "2025-01-01T10:00:00Z",
                    "changed_by": "user"
                },
                {
                    "version": "1.0.1",
                    "config": {"watch_paths": ["/old"], "interval": 60},
                    "change_reason": "初始配置",
                    "changed_at": "2025-01-01T09:00:00Z",
                    "changed_by": "system"
                }
            ],
            "total": 2,
            "has_more": False
        }
        mock_config_service.get_config_history.return_value = history_data
        
        with patch('api.routers.connector_config_api.get_connector_config_service', return_value=mock_config_service):
            response = client.get("/connector-config/history/filesystem?limit=10&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["history"]) == 2
        assert data["data"]["total_count"] == 2
        assert data["data"]["has_more"] is False
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_all_schemas(self, client, mock_config_service):
        """测试获取所有配置schema"""
        all_schemas = [
            {
                "connector_id": "filesystem",
                "connector_name": "文件系统连接器",
                "schema_version": "1.0.0",
                "has_ui_schema": True,
                "registered_at": "2025-01-01T10:00:00Z"
            },
            {
                "connector_id": "clipboard",
                "connector_name": "剪贴板连接器",
                "schema_version": "1.0.0",
                "has_ui_schema": False,
                "registered_at": "2025-01-01T10:05:00Z"
            }
        ]
        mock_config_service.get_all_schemas.return_value = all_schemas
        
        with patch('api.routers.connector_config_api.get_connector_config_service', return_value=mock_config_service):
            response = client.get("/connector-config/all-schemas")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["schemas"]) == 2
        assert data["data"]["total_count"] == 2
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_register_schema_success(self, client, mock_config_service):
        """测试成功注册schema"""
        mock_config_service.register_runtime_schema.return_value = True
        
        schema_data = {
            "config_schema": {
                "type": "object",
                "properties": {"test": {"type": "string"}}
            },
            "ui_schema": {"test": {"ui:widget": "text"}},
            "connector_name": "测试连接器",
            "connector_description": "用于测试的连接器",
            "schema_source": "runtime"
        }
        
        with patch('api.routers.connector_config_api.get_connector_config_service', return_value=mock_config_service):
            response = client.post("/connector-config/register-schema/test_connector", json=schema_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["connector_id"] == "test_connector"
        assert data["data"]["schema_registered"] is True
        assert data["data"]["schema_source"] == "runtime"
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_register_schema_failure(self, client, mock_config_service):
        """测试注册schema失败"""
        mock_config_service.register_runtime_schema.return_value = False
        
        schema_data = {
            "config_schema": {"type": "object"},
            "ui_schema": {},
            "connector_name": "失败连接器",
            "schema_source": "runtime"
        }
        
        with patch('api.routers.connector_config_api.get_connector_config_service', return_value=mock_config_service):
            response = client.post("/connector-config/register-schema/fail_connector", json=schema_data)
        
        assert response.status_code == 500
        assert "注册失败" in response.json()["detail"]
    
    @pytest.mark.api
    def test_request_models_validation(self):
        """测试请求模型的验证"""
        from api.routers.connector_config_api import (
            GetConfigSchemaRequest, UpdateConfigRequest, 
            ValidateConfigRequest, ResetConfigRequest, RegisterSchemaRequest
        )
        
        # 测试UpdateConfigRequest
        valid_request = UpdateConfigRequest(
            connector_id="test",
            config={"key": "value"},
            config_version="1.0.0",
            change_reason="测试"
        )
        assert valid_request.connector_id == "test"
        assert valid_request.config == {"key": "value"}
        
        # 测试ValidateConfigRequest
        validate_request = ValidateConfigRequest(
            connector_id="test",
            config={"test": True}
        )
        assert validate_request.connector_id == "test"
        assert validate_request.config == {"test": True}
        
        # 测试ResetConfigRequest
        reset_request = ResetConfigRequest(
            connector_id="test",
            to_defaults=True
        )
        assert reset_request.to_defaults is True
        
        # 测试RegisterSchemaRequest
        register_request = RegisterSchemaRequest(
            connector_id="test",
            config_schema={"type": "object"},
            ui_schema={},
            connector_name="Test",
            schema_source="runtime"
        )
        assert register_request.connector_id == "test"
        assert register_request.schema_source == "runtime"