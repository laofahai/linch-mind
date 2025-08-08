#!/usr/bin/env python3
"""
统一连接器服务测试
测试配置管理和UI管理的集成功能
"""

import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from services.connectors.unified_connector_service import UnifiedConnectorService


@pytest.fixture
def service():
    """创建测试用的统一连接器服务"""
    return UnifiedConnectorService()


@pytest.fixture
def mock_connector_data():
    """模拟连接器数据"""
    return {
        "id": "test-connector",
        "name": "Test Connector",
        "directory": "/fake/path/test-connector",
    }


@pytest.fixture
def sample_config_schema():
    """示例配置schema"""
    return {
        "type": "object",
        "properties": {
            "host": {"type": "string", "title": "主机地址", "default": "localhost"},
            "port": {
                "type": "integer",
                "title": "端口",
                "default": 8080,
                "minimum": 1,
                "maximum": 65535,
            },
            "enabled": {"type": "boolean", "title": "启用", "default": True},
        },
        "required": ["host", "port"],
    }


@pytest.fixture
def sample_widget_config():
    """示例组件配置"""
    return {
        "type": "form",
        "title": "Test Widget",
        "fields": [{"name": "input1", "type": "text", "label": "Input 1"}],
    }


class TestUnifiedConnectorService:
    """统一连接器服务测试类"""

    @pytest.mark.asyncio
    async def test_get_config_schema_from_cache(self, service, sample_config_schema):
        """测试从缓存获取配置schema"""
        # 设置缓存
        service._schema_cache["test-connector"] = sample_config_schema

        # 模拟_load_static_schema_from_manifest返回缓存的schema
        with patch.object(
            service,
            "_load_static_schema_from_manifest",
            return_value=sample_config_schema,
        ):
            result = await service.get_config_schema("test-connector")

        assert result == sample_config_schema

    @pytest.mark.asyncio
    async def test_get_config_schema_runtime(self, service, sample_config_schema):
        """测试从运行时注册获取schema"""
        service._runtime_schemas["test-connector"] = sample_config_schema

        with patch.object(
            service, "_load_static_schema_from_manifest", return_value=None
        ):
            result = await service.get_config_schema("test-connector")

        assert result == sample_config_schema

    @pytest.mark.asyncio
    async def test_validate_config_success(self, service, sample_config_schema):
        """测试配置验证成功"""
        service._schema_cache["test-connector"] = sample_config_schema

        valid_config = {"host": "example.com", "port": 9090, "enabled": True}

        with patch.object(
            service, "get_config_schema", return_value=sample_config_schema
        ):
            is_valid, error_msg = await service.validate_config(
                "test-connector", valid_config
            )

        assert is_valid is True
        assert error_msg is None

    @pytest.mark.asyncio
    async def test_validate_config_failure(self, service, sample_config_schema):
        """测试配置验证失败"""
        service._schema_cache["test-connector"] = sample_config_schema

        invalid_config = {
            "host": "example.com",
            "port": "invalid_port",  # 应该是整数
            "enabled": True,
        }

        with patch.object(
            service, "get_config_schema", return_value=sample_config_schema
        ):
            is_valid, error_msg = await service.validate_config(
                "test-connector", invalid_config
            )

        assert is_valid is False
        assert error_msg is not None
        assert "验证失败" in error_msg

    @pytest.mark.asyncio
    async def test_register_custom_widget_success(self, service, sample_widget_config):
        """测试成功注册自定义组件"""
        result = await service.register_custom_widget(
            "test-connector", "test-widget", sample_widget_config
        )

        assert result is True

        # 验证组件已注册
        widget_key = "test-connector:test-widget"
        assert widget_key in service._registered_widgets

        registered = service._registered_widgets[widget_key]
        assert registered["connector_id"] == "test-connector"
        assert registered["widget_name"] == "test-widget"
        assert registered["config"] == sample_widget_config

    @pytest.mark.asyncio
    async def test_register_custom_widget_invalid(self, service):
        """测试注册无效组件配置"""
        invalid_config = {
            "type": "invalid_type",  # 不支持的类型
            "title": "Invalid Widget",
        }

        result = await service.register_custom_widget(
            "test-connector", "invalid-widget", invalid_config
        )

        assert result is False

        # 验证组件未被注册
        widget_key = "test-connector:invalid-widget"
        assert widget_key not in service._registered_widgets

    @pytest.mark.asyncio
    async def test_register_iframe_widget(self, service):
        """测试注册iframe组件"""
        iframe_config = {
            "type": "iframe",
            "title": "Iframe Widget",
            "url": "https://example.com",
            "permissions": ["camera", "microphone"],
            "sandbox": True,
            "width": "800px",
            "height": "600px",
        }

        result = await service.register_custom_widget(
            "test-connector", "iframe-widget", iframe_config
        )

        assert result is True

        # 验证iframe处理器已注册
        handler_key = "test-connector:iframe-widget"
        assert handler_key in service._iframe_handlers

        handler = service._iframe_handlers[handler_key]
        assert handler["url"] == "https://example.com"
        assert handler["permissions"] == ["camera", "microphone"]
        assert handler["sandbox"] is True

    @pytest.mark.asyncio
    async def test_get_widget_config(self, service, sample_widget_config):
        """测试获取组件配置"""
        # 先注册组件
        await service.register_custom_widget(
            "test-connector", "test-widget", sample_widget_config
        )

        # 获取组件配置
        config = await service.get_widget_config("test-connector", "test-widget")

        assert config == sample_widget_config

    @pytest.mark.asyncio
    async def test_get_widget_config_not_found(self, service):
        """测试获取不存在的组件配置"""
        config = await service.get_widget_config("test-connector", "nonexistent")
        assert config is None

    @pytest.mark.asyncio
    async def test_list_connector_widgets(self, service):
        """测试列出连接器的所有组件"""
        # 注册多个组件
        widget1_config = {"type": "form", "title": "Widget 1"}
        widget2_config = {"type": "table", "title": "Widget 2"}

        await service.register_custom_widget(
            "test-connector", "widget1", widget1_config
        )
        await service.register_custom_widget(
            "test-connector", "widget2", widget2_config
        )
        await service.register_custom_widget(
            "other-connector", "widget3", widget1_config
        )

        # 列出test-connector的组件
        widgets = await service.list_connector_widgets("test-connector")

        assert len(widgets) == 2
        widget_names = [w["name"] for w in widgets]
        assert "widget1" in widget_names
        assert "widget2" in widget_names
        assert "widget3" not in widget_names  # 属于other-connector

    @pytest.mark.asyncio
    async def test_get_connector_info_integration(
        self, service, mock_connector_data, sample_config_schema
    ):
        """测试获取连接器完整信息的集成功能"""
        # 模拟连接器查找
        with patch.object(
            service, "_find_connector_by_id", return_value=mock_connector_data
        ):
            # 模拟schema获取
            with patch.object(
                service, "get_config_schema", return_value=sample_config_schema
            ):

                # 注册一个组件
                widget_config = {"type": "form", "title": "Test Widget"}
                await service.register_custom_widget(
                    "test-connector", "test-widget", widget_config
                )

                # 获取完整信息
                info = await service.get_connector_info("test-connector")

                assert info["id"] == "test-connector"
                assert info["name"] == "Test Connector"
                assert info["config_schema"] == sample_config_schema
                assert len(info["widgets"]) == 1
                assert info["has_custom_ui"] is True

    def test_validate_widget_config(self, service):
        """测试组件配置验证"""
        # 有效配置
        valid_config = {"type": "form", "title": "Valid Widget"}
        assert service._validate_widget_config(valid_config) is True

        # 缺少必需字段
        invalid_config1 = {"type": "form"}  # 缺少title
        assert service._validate_widget_config(invalid_config1) is False

        invalid_config2 = {"title": "No Type"}  # 缺少type
        assert service._validate_widget_config(invalid_config2) is False

        # 不支持的类型
        invalid_config3 = {"type": "unsupported", "title": "Unsupported"}
        assert service._validate_widget_config(invalid_config3) is False


@pytest.mark.integration
class TestUnifiedConnectorServiceIntegration:
    """统一连接器服务集成测试"""

    @pytest.mark.asyncio
    async def test_full_workflow(self, service):
        """测试完整的工作流程"""
        connector_id = "integration-test-connector"

        # 1. 注册schema
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string", "title": "Name"}},
            "required": ["name"],
        }
        service._runtime_schemas[connector_id] = schema

        # 2. 验证配置
        config = {"name": "Test Config"}
        is_valid, error = await service.validate_config(connector_id, config)
        assert is_valid is True

        # 3. 注册组件
        widget_config = {"type": "form", "title": "Config Form"}
        success = await service.register_custom_widget(
            connector_id, "config-form", widget_config
        )
        assert success is True

        # 4. 获取完整信息
        with patch.object(
            service,
            "_find_connector_by_id",
            return_value={"id": connector_id, "name": "Integration Test"},
        ):
            info = await service.get_connector_info(connector_id)

            assert info["id"] == connector_id
            assert info["config_schema"] == schema
            assert len(info["widgets"]) == 1
            assert info["has_custom_ui"] is True
