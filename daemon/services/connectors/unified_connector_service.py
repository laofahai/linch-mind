#!/usr/bin/env python3
"""
统一连接器服务
合并ConnectorConfigService和ConnectorUIService的功能，简化架构
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from jsonschema import ValidationError, validate

from models.database_models import Connector, ConnectorConfigHistory
from services.connectors.connector_config_schema import create_basic_config_schema
from services.database_service import get_database_service

logger = logging.getLogger(__name__)


class UnifiedConnectorService:
    """统一连接器服务 - 整合配置管理和UI管理功能"""

    def __init__(self):
        self.db_service = get_database_service()

        # 配置管理相关
        self._schema_cache = {}  # 缓存已加载的schema
        self._runtime_schemas = {}  # 运行时注册的schema

        # UI管理相关
        self._registered_widgets = {}  # 注册的自定义组件
        self._iframe_handlers = {}  # iframe处理器
        self._widget_actions = {}  # 组件动作处理器

    # ======================== 配置管理功能 ========================

    async def get_config_schema(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取连接器的配置schema"""
        try:
            # 1. 优先从connector.json读取静态schema（推荐方式）
            static_schema = await self._load_static_schema_from_manifest(connector_id)
            if static_schema:
                return static_schema

            # 2. 向后兼容：使用运行时注册的schema
            if connector_id in self._runtime_schemas:
                logger.info(f"使用运行时schema: {connector_id}")
                return self._runtime_schemas[connector_id]

            # 3. 从数据库获取存储的schema
            with self.db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )

                if connector and connector.config_schema:
                    try:
                        return json.loads(connector.config_schema)
                    except json.JSONDecodeError as e:
                        logger.error(f"解析存储的schema失败: {e}")

            # 4. 使用基础默认schema
            logger.info(f"使用默认schema: {connector_id}")
            schema = create_basic_config_schema(
                connector_id, f"Connector {connector_id}"
            )
            return schema.to_json_schema()

        except Exception as e:
            logger.error(f"获取配置schema失败 ({connector_id}): {e}")
            schema = create_basic_config_schema(
                connector_id, f"Connector {connector_id}"
            )
            return schema.to_json_schema()

    async def _load_static_schema_from_manifest(
        self, connector_id: str
    ) -> Optional[Dict[str, Any]]:
        """从connector.json加载静态schema"""
        try:
            # 查找连接器目录
            connector = await self._find_connector_by_id(connector_id)
            if not connector:
                return None

            connector_dir = Path(connector["directory"])
            manifest_file = connector_dir / "connector.json"

            if not manifest_file.exists():
                return None

            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            config_schema = manifest.get("config_schema")
            if config_schema:
                self._schema_cache[connector_id] = config_schema
                logger.debug(f"从manifest加载schema成功: {connector_id}")
                return config_schema

        except Exception as e:
            logger.debug(f"从manifest加载schema失败 ({connector_id}): {e}")

        return None

    async def _find_connector_by_id(
        self, connector_id: str
    ) -> Optional[Dict[str, Any]]:
        """查找连接器信息"""
        with self.db_service.get_session() as session:
            connector = (
                session.query(Connector).filter_by(connector_id=connector_id).first()
            )

            if connector:
                return {
                    "id": connector.connector_id,
                    "directory": connector.connector_path,
                    "name": connector.name,
                }
        return None

    async def validate_config(
        self, connector_id: str, config: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """验证连接器配置"""
        try:
            schema = await self.get_config_schema(connector_id)
            if not schema:
                return False, "无法获取配置schema"

            validate(instance=config, schema=schema)
            return True, None

        except ValidationError as e:
            return False, f"配置验证失败: {e.message}"
        except Exception as e:
            return False, f"验证过程出错: {str(e)}"

    async def save_config(
        self, connector_id: str, config: Dict[str, Any], user_id: str = "system"
    ) -> bool:
        """保存连接器配置"""
        try:
            # 验证配置
            is_valid, error_msg = await self.validate_config(connector_id, config)
            if not is_valid:
                logger.error(f"配置无效 ({connector_id}): {error_msg}")
                return False

            with self.db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )

                if not connector:
                    logger.error(f"连接器不存在: {connector_id}")
                    return False

                # 保存配置历史
                old_config = connector.config or "{}"
                config_history = ConnectorConfigHistory(
                    connector_id=connector_id,
                    old_config=old_config,
                    new_config=json.dumps(config, ensure_ascii=False),
                    changed_by=user_id,
                    changed_at=datetime.now(timezone.utc),
                )
                session.add(config_history)

                # 更新连接器配置
                connector.config = json.dumps(config, ensure_ascii=False)
                connector.updated_at = datetime.now(timezone.utc)

                session.commit()
                logger.info(f"配置保存成功: {connector_id}")
                return True

        except Exception as e:
            logger.error(f"保存配置失败 ({connector_id}): {e}")
            return False

    # ======================== UI管理功能 ========================

    async def register_custom_widget(
        self, connector_id: str, widget_name: str, widget_config: Dict[str, Any]
    ) -> bool:
        """注册自定义UI组件"""
        try:
            widget_key = f"{connector_id}:{widget_name}"

            # 验证组件配置
            if not self._validate_widget_config(widget_config):
                logger.error(f"无效的组件配置: {widget_key}")
                return False

            # 注册组件
            self._registered_widgets[widget_key] = {
                "connector_id": connector_id,
                "widget_name": widget_name,
                "config": widget_config,
                "registered_at": asyncio.get_event_loop().time(),
            }

            # 如果是iframe组件，注册处理器
            if widget_config.get("type") == "iframe":
                await self._register_iframe_handler(
                    connector_id, widget_name, widget_config
                )

            logger.info(f"组件注册成功: {widget_key}")
            return True

        except Exception as e:
            logger.error(f"注册组件失败 ({connector_id}:{widget_name}): {e}")
            return False

    def _validate_widget_config(self, widget_config: Dict[str, Any]) -> bool:
        """验证组件配置"""
        required_fields = ["type", "title"]
        for field in required_fields:
            if field not in widget_config:
                return False

        # 验证组件类型
        supported_types = ["form", "iframe", "chart", "table", "custom"]
        if widget_config["type"] not in supported_types:
            return False

        return True

    async def _register_iframe_handler(
        self, connector_id: str, widget_name: str, config: Dict[str, Any]
    ):
        """注册iframe处理器"""
        handler_key = f"{connector_id}:{widget_name}"

        self._iframe_handlers[handler_key] = {
            "url": config.get("url"),
            "permissions": config.get("permissions", []),
            "sandbox": config.get("sandbox", True),
            "width": config.get("width", "100%"),
            "height": config.get("height", "400px"),
        }

    async def get_widget_config(
        self, connector_id: str, widget_name: str
    ) -> Optional[Dict[str, Any]]:
        """获取组件配置"""
        widget_key = f"{connector_id}:{widget_name}"
        widget_info = self._registered_widgets.get(widget_key)

        if widget_info:
            return widget_info["config"]

        return None

    async def list_connector_widgets(self, connector_id: str) -> List[Dict[str, Any]]:
        """列出连接器的所有组件"""
        widgets = []
        for _widget_key, widget_info in self._registered_widgets.items():
            if widget_info["connector_id"] == connector_id:
                widgets.append(
                    {
                        "name": widget_info["widget_name"],
                        "config": widget_info["config"],
                        "registered_at": widget_info["registered_at"],
                    }
                )

        return widgets

    # ======================== 统一接口 ========================

    async def get_connector_info(self, connector_id: str) -> Dict[str, Any]:
        """获取连接器完整信息（配置+UI）"""
        try:
            connector_data = await self._find_connector_by_id(connector_id)
            if not connector_data:
                return {"error": "连接器不存在"}

            config_schema = await self.get_config_schema(connector_id)
            widgets = await self.list_connector_widgets(connector_id)

            return {
                "id": connector_id,
                "name": connector_data.get("name"),
                "directory": connector_data.get("directory"),
                "config_schema": config_schema,
                "widgets": widgets,
                "has_custom_ui": len(widgets) > 0,
            }

        except Exception as e:
            logger.error(f"获取连接器信息失败 ({connector_id}): {e}")
            return {"error": str(e)}


# 全局服务实例
_unified_connector_service = None


def get_unified_connector_service() -> UnifiedConnectorService:
    """获取统一连接器服务实例"""
    global _unified_connector_service
    if _unified_connector_service is None:
        _unified_connector_service = UnifiedConnectorService()
    return _unified_connector_service
