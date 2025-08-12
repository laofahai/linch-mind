#!/usr/bin/env python3
"""
连接器配置Schema管理器
专门负责配置schema的获取、生成和管理
从connector_config_service.py中拆分出来
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from core.service_facade import get_database_service
from models.database_models import Connector
from utils.config_loader import ConfigLoader, ConfigLoadError

from .connector_config_schema import create_basic_config_schema

logger = logging.getLogger(__name__)


class ConfigSchemaManager:
    """配置Schema管理器"""

    def __init__(self, connectors_dir: Optional[Path] = None):
        self._db_service = None
        self.connectors_dir = connectors_dir

    @property
    def db_service(self):
        """延迟获取数据库服务"""
        if self._db_service is None:
            try:
                self._db_service = get_database_service()
            except Exception as e:
                logger.warning(f"数据库服务暂不可用: {e}")
                return None
        return self._db_service

    async def get_config_schema(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取连接器的配置schema"""
        try:
            # 首先尝试从连接器目录加载schema文件
            schema_data = self._load_schema_from_file(connector_id)

            if schema_data:
                logger.debug(f"使用连接器自定义schema: {connector_id}")
                return schema_data

            # 检查是否应该返回空schema
            if self._should_return_empty_schema(connector_id):
                logger.debug(f"连接器无需配置: {connector_id}")
                return self._create_empty_schema(connector_id)

            # 生成基础schema
            schema_data = self._generate_basic_schema(connector_id)
            logger.debug(f"使用生成的基础schema: {connector_id}")
            return schema_data

        except Exception as e:
            logger.error(f"获取配置schema失败 {connector_id}: {e}")
            return None

    def _load_schema_from_file(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """从文件加载schema"""
        try:
            # 尝试从独立的schema文件加载
            potential_schema_paths = [
                self.connectors_dir / "official" / connector_id / "config_schema.json",
                self.connectors_dir / "official" / connector_id / "schema.json",
                self.connectors_dir / connector_id / "config_schema.json",
            ]

            for schema_path in potential_schema_paths:
                if schema_path.exists():
                    with open(schema_path, "r", encoding="utf-8") as f:
                        schema_data = json.load(f)
                    logger.debug(f"从独立文件加载schema: {schema_path}")
                    return schema_data

            # 尝试从connector配置中提取schema
            return self._extract_schema_from_connector_config(connector_id)

        except Exception as e:
            logger.warning(f"从文件加载schema失败 {connector_id}: {e}")
            return None

    def _extract_schema_from_connector_config(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """从connector.json中提取schema"""
        try:
            search_dirs = [
                self.connectors_dir / "official" / connector_id,
                self.connectors_dir / connector_id,
            ]

            connector_config = ConfigLoader.load_with_fallback("connector", search_dirs)
            
            if not connector_config:
                return None

            config_schema = connector_config.get("config_schema")
            config_ui_schema = connector_config.get("config_ui_schema", {})

            if config_schema:
                logger.debug(f"从connector.json中提取schema: {connector_id}")
                return {
                    "json_schema": config_schema,
                    "ui_schema": config_ui_schema,
                    "metadata": {
                        "schema_version": connector_config.get("version", "1.0.0"),
                        "connector_id": connector_id,
                        "connector_name": connector_config.get("name", connector_id),
                        "generated": False,
                    },
                }

            return None

        except ConfigLoadError:
            return None

    def _should_return_empty_schema(self, connector_id: str) -> bool:
        """检查是否应该返回空schema"""
        try:
            search_dirs = [
                self.connectors_dir / "official" / connector_id,
                self.connectors_dir / connector_id,
            ]

            connector_config = ConfigLoader.load_with_fallback("connector", search_dirs)
            return (
                connector_config 
                and connector_config.get("config_schema_source") == "none"
            )

        except ConfigLoadError:
            return False

    def _create_empty_schema(self, connector_id: str) -> Dict[str, Any]:
        """创建空schema"""
        return {
            "json_schema": {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            "ui_schema": {},
            "metadata": {
                "schema_version": "1.0.0",
                "connector_id": connector_id,
                "no_config_needed": True,
            },
        }

    def _generate_basic_schema(self, connector_id: str) -> Dict[str, Any]:
        """生成基础的配置schema"""
        try:
            connector_name = self._get_connector_name(connector_id)
            basic_schema = create_basic_config_schema(connector_id, connector_name)

            return {
                "json_schema": basic_schema.to_json_schema(),
                "ui_schema": basic_schema.to_ui_schema(),
                "metadata": {
                    "schema_version": basic_schema.schema_version,
                    "connector_id": connector_id,
                    "connector_name": connector_name,
                    "generated": True,
                },
            }

        except Exception as e:
            logger.error(f"生成基础schema失败 {connector_id}: {e}")
            return self._create_fallback_schema(connector_id)

    def _get_connector_name(self, connector_id: str) -> str:
        """获取连接器名称"""
        connector_name = connector_id  # 默认值

        if self.db_service is not None:
            try:
                with self.db_service.get_session() as session:
                    connector = (
                        session.query(Connector)
                        .filter_by(connector_id=connector_id)
                        .first()
                    )
                    if connector:
                        connector_name = connector.name
            except Exception as e:
                logger.warning(f"从数据库获取连接器信息失败 {connector_id}: {e}")
        
        return connector_name

    def _create_fallback_schema(self, connector_id: str) -> Dict[str, Any]:
        """创建回退schema"""
        return {
            "json_schema": {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {},
                "additionalProperties": True,
            },
            "ui_schema": {},
            "metadata": {
                "schema_version": "1.0.0",
                "connector_id": connector_id,
                "error": "Failed to generate schema",
            },
        }

    async def get_all_schemas(self) -> Dict[str, Any]:
        """获取所有连接器的配置Schema概览"""
        try:
            if not self.db_service:
                return {"schemas": {}, "total": 0, "error": "数据库服务不可用"}

            with self.db_service.get_session() as session:
                connectors = session.query(Connector).all()

                schemas = {}
                for connector in connectors:
                    schema_data = await self.get_config_schema(connector.connector_id)
                    if schema_data:
                        schemas[connector.connector_id] = {
                            "connector_id": connector.connector_id,
                            "connector_name": connector.name,
                            "schema_version": schema_data.get("metadata", {}).get(
                                "schema_version", "1.0.0"
                            ),
                            "has_custom_schema": not schema_data.get(
                                "metadata", {}
                            ).get("generated", False),
                            "field_count": len(
                                schema_data.get("json_schema", {}).get("properties", {})
                            ),
                        }

                logger.debug(f"获取所有schema成功，共 {len(schemas)} 个连接器")
                return {"schemas": schemas, "total": len(schemas)}

        except Exception as e:
            logger.error(f"获取所有schema失败: {e}")
            return {"schemas": {}, "total": 0, "error": str(e)}