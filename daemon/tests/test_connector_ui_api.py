#!/usr/bin/env python3
"""
连接器UI API测试
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import tempfile
import os


class TestConnectorUIAPI:
    """连接器UI API测试类"""
    
    @pytest.fixture
    def mock_ui_service(self):
        """模拟UI服务"""
        service = Mock()
        # 设置异步方法
        service.register_custom_widget = AsyncMock()
        service.get_custom_widget_config = AsyncMock()
        service.get_iframe_content = AsyncMock()
        service.get_static_file = AsyncMock()
        service.validate_custom_config = AsyncMock()
        service.get_available_widgets = AsyncMock()
        service.execute_widget_action = AsyncMock()
        return service
    
    @pytest.fixture
    def sample_widget_config(self):
        """示例组件配置"""
        return {
            "type": "chart",
            "title": "数据图表",
            "config": {
                "chart_type": "line",
                "data_source": "api",
                "refresh_interval": 60
            },
            "actions": ["refresh", "export"],
            "permissions": ["read_data"]
        }
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_register_custom_widget_success(self, client, mock_ui_service, sample_widget_config):
        """测试成功注册自定义组件"""
        mock_ui_service.register_custom_widget.return_value = True
        
        with patch('api.routers.connector_ui_api.get_ui_service', return_value=mock_ui_service):
            response = client.post("/connector-ui/register-custom-widget", json={
                "connector_id": "filesystem",
                "widget_name": "file_browser",
                "widget_config": sample_widget_config
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["connector_id"] == "filesystem"
        assert data["data"]["widget_name"] == "file_browser"
        assert data["data"]["registered"] is True
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_register_custom_widget_missing_params(self, client, mock_ui_service):
        """测试注册组件缺少必需参数"""
        with patch('api.routers.connector_ui_api.get_ui_service', return_value=mock_ui_service):
            response = client.post("/connector-ui/register-custom-widget", json={
                "connector_id": "filesystem"
                # 缺少widget_name
            })
        
        assert response.status_code == 400
        assert "required" in response.json()["detail"]
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_register_custom_widget_failure(self, client, mock_ui_service):
        """测试注册组件失败"""
        mock_ui_service.register_custom_widget.return_value = False
        
        with patch('api.routers.connector_ui_api.get_ui_service', return_value=mock_ui_service):
            response = client.post("/connector-ui/register-custom-widget", json={
                "connector_id": "filesystem",
                "widget_name": "failed_widget"
            })
        
        assert response.status_code == 500
        assert "Failed to register" in response.json()["detail"]
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_custom_widget_config_success(self, client, mock_ui_service, sample_widget_config):
        """测试成功获取自定义组件配置"""
        mock_ui_service.get_custom_widget_config.return_value = sample_widget_config
        
        with patch('api.routers.connector_ui_api.get_ui_service', return_value=mock_ui_service):
            response = client.get("/connector-ui/custom-widget/filesystem/file_browser")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["connector_id"] == "filesystem"
        assert data["data"]["widget_name"] == "file_browser"
        assert data["data"]["widget_config"] == sample_widget_config
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_custom_widget_config_not_found(self, client, mock_ui_service):
        """测试获取不存在的组件配置"""
        mock_ui_service.get_custom_widget_config.return_value = None
        
        with patch('api.routers.connector_ui_api.get_ui_service', return_value=mock_ui_service):
            response = client.get("/connector-ui/custom-widget/filesystem/nonexistent")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_serve_iframe_content_success(self, client, mock_ui_service):
        """测试成功提供iframe内容"""
        mock_content = {
            "content": "<html><body><h1>Test Content</h1></body></html>",
            "content_type": "text/html"
        }
        mock_ui_service.get_iframe_content.return_value = mock_content
        
        with patch('api.routers.connector_ui_api.get_ui_service', return_value=mock_ui_service):
            response = client.get("/connector-ui/iframe-content/filesystem/dashboard?param=value")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert "<h1>Test Content</h1>" in response.text
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_serve_iframe_content_not_found(self, client, mock_ui_service):
        """测试iframe内容不存在"""
        mock_ui_service.get_iframe_content.return_value = None
        
        with patch('api.routers.connector_ui_api.get_ui_service', return_value=mock_ui_service):
            response = client.get("/connector-ui/iframe-content/filesystem/nonexistent")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_serve_static_file_success(self, client, mock_ui_service, temp_dir):
        """测试成功提供静态文件"""
        # 创建测试文件
        test_file = temp_dir / "test.js"
        test_file.write_text("console.log('test');")
        
        mock_file_info = {
            "exists": True,
            "full_path": str(test_file)
        }
        mock_ui_service.get_static_file.return_value = mock_file_info
        
        with patch('api.routers.connector_ui_api.get_ui_service', return_value=mock_ui_service):
            response = client.get("/connector-ui/static/filesystem/js/test.js")
        
        assert response.status_code == 200
        assert "console.log('test');" in response.text
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_serve_static_file_not_found(self, client, mock_ui_service):
        """测试静态文件不存在"""
        mock_file_info = {
            "exists": False,
            "full_path": None
        }
        mock_ui_service.get_static_file.return_value = mock_file_info
        
        with patch('api.routers.connector_ui_api.get_ui_service', return_value=mock_ui_service):
            response = client.get("/connector-ui/static/filesystem/nonexistent.js")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_validate_custom_config_valid(self, client, mock_ui_service):
        """测试自定义配置验证通过"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": ["Minor warning about performance"]
        }
        mock_ui_service.validate_custom_config.return_value = validation_result
        
        with patch('api.routers.connector_ui_api.get_ui_service', return_value=mock_ui_service):
            response = client.post("/connector-ui/validate-custom-config", json={
                "connector_id": "filesystem",
                "widget_name": "file_browser",
                "config_data": {"path": "/test", "mode": "readonly"}
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["valid"] is True
        assert len(data["data"]["errors"]) == 0
        assert len(data["data"]["warnings"]) == 1
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_validate_custom_config_invalid(self, client, mock_ui_service):
        """测试自定义配置验证失败"""
        validation_result = {
            "valid": False,
            "errors": ["Invalid path specified", "Mode not supported"],
            "warnings": []
        }
        mock_ui_service.validate_custom_config.return_value = validation_result
        
        with patch('api.routers.connector_ui_api.get_ui_service', return_value=mock_ui_service):
            response = client.post("/connector-ui/validate-custom-config", json={
                "connector_id": "filesystem",
                "widget_name": "file_browser",
                "config_data": {"path": "", "mode": "invalid"}
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["data"]["valid"] is False
        assert len(data["data"]["errors"]) == 2
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_validate_custom_config_missing_params(self, client, mock_ui_service):
        """测试验证配置缺少必需参数"""
        with patch('api.routers.connector_ui_api.get_ui_service', return_value=mock_ui_service):
            response = client.post("/connector-ui/validate-custom-config", json={
                "connector_id": "filesystem"
                # 缺少widget_name
            })
        
        assert response.status_code == 400
        assert "required" in response.json()["detail"]
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_available_widgets_success(self, client, mock_ui_service):
        """测试成功获取可用组件列表"""
        available_widgets = [
            {
                "widget_name": "file_browser",
                "display_name": "文件浏览器",
                "description": "浏览和管理文件",
                "version": "1.0.0",
                "type": "component"
            },
            {
                "widget_name": "file_stats",
                "display_name": "文件统计",
                "description": "显示文件统计信息",
                "version": "1.0.0",
                "type": "chart"
            }
        ]
        mock_ui_service.get_available_widgets.return_value = available_widgets
        
        with patch('api.routers.connector_ui_api.get_ui_service', return_value=mock_ui_service):
            response = client.get("/connector-ui/available-widgets/filesystem")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["connector_id"] == "filesystem"
        assert len(data["data"]["widgets"]) == 2
        assert data["data"]["total_count"] == 2
        assert data["data"]["widgets"][0]["widget_name"] == "file_browser"
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_available_widgets_empty(self, client, mock_ui_service):
        """测试获取空的组件列表"""
        mock_ui_service.get_available_widgets.return_value = []
        
        with patch('api.routers.connector_ui_api.get_ui_service', return_value=mock_ui_service):
            response = client.get("/connector-ui/available-widgets/empty_connector")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["widgets"]) == 0
        assert data["data"]["total_count"] == 0
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_execute_widget_action_success(self, client, mock_ui_service):
        """测试成功执行组件动作"""
        action_result = {
            "success": True,
            "data": {
                "action": "refresh",
                "timestamp": "2025-01-01T10:00:00Z",
                "records_updated": 150
            },
            "message": "数据刷新成功"
        }
        mock_ui_service.execute_widget_action.return_value = action_result
        
        with patch('api.routers.connector_ui_api.get_ui_service', return_value=mock_ui_service):
            response = client.post("/connector-ui/execute-widget-action", json={
                "connector_id": "filesystem",
                "widget_name": "file_browser",
                "action_name": "refresh",
                "action_params": {"path": "/test"}
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["records_updated"] == 150
        assert "刷新成功" in data["message"]
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_execute_widget_action_failure(self, client, mock_ui_service):
        """测试执行组件动作失败"""
        action_result = {
            "success": False,
            "data": {"error_code": "PERMISSION_DENIED"},
            "message": "权限不足"
        }
        mock_ui_service.execute_widget_action.return_value = action_result
        
        with patch('api.routers.connector_ui_api.get_ui_service', return_value=mock_ui_service):
            response = client.post("/connector-ui/execute-widget-action", json={
                "connector_id": "filesystem",
                "widget_name": "file_browser",
                "action_name": "delete",
                "action_params": {"path": "/protected"}
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "权限不足" in data["message"]
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_execute_widget_action_missing_params(self, client, mock_ui_service):
        """测试执行动作缺少必需参数"""
        with patch('api.routers.connector_ui_api.get_ui_service', return_value=mock_ui_service):
            response = client.post("/connector-ui/execute-widget-action", json={
                "connector_id": "filesystem",
                "widget_name": "file_browser"
                # 缺少action_name
            })
        
        assert response.status_code == 400
        assert "required" in response.json()["detail"]
    
    @pytest.mark.api
    def test_get_ui_service_function(self):
        """测试UI服务获取函数"""
        from api.routers.connector_ui_api import get_ui_service
        from services.connectors.connector_ui_service import ConnectorUIService
        
        service = get_ui_service()
        assert isinstance(service, ConnectorUIService)
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_service_error_handling(self, client, mock_ui_service):
        """测试服务层错误处理"""
        # 模拟服务异常
        mock_ui_service.register_custom_widget.side_effect = Exception("Service error")
        
        with patch('api.routers.connector_ui_api.get_ui_service', return_value=mock_ui_service):
            response = client.post("/connector-ui/register-custom-widget", json={
                "connector_id": "filesystem",
                "widget_name": "error_widget"
            })
        
        assert response.status_code == 500
        assert "Service error" in response.json()["detail"]