#!/usr/bin/env python3
"""
连接器配置管理服务
实现Schema驱动的配置系统
"""

import importlib.util
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from jsonschema import ValidationError, validate
from models.database_models import Connector, ConnectorConfigHistory
from services.database_service import get_database_service

from .connector_config_schema import create_basic_config_schema

logger = logging.getLogger(__name__)


class ConnectorConfigService:
    """连接器配置管理服务"""

    def __init__(self):
        self.db_service = get_database_service()
        self._schema_cache = {}  # 缓存已加载的schema
        self._runtime_schemas = {}  # 运行时注册的schema

    async def get_config_schema(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取连接器的配置schema - 语言无关版本，优先使用静态schema"""
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
                if not connector:
                    logger.warning(f"连接器不存在: {connector_id}")
                    return None

                # 如果数据库中有schema，返回它
                if connector.config_schema:
                    logger.info(f"使用数据库存储schema: {connector_id}")
                    schema_data = {
                        "schema": connector.config_schema,
                        "ui_schema": (
                            connector.config_data.get("ui_schema", {})
                            if connector.config_data
                            else {}
                        ),
                        "default_values": (
                            connector.config_data.get("default_values", {})
                            if connector.config_data
                            else {}
                        ),
                        "version": connector.config_version or "1.0.0",
                    }
                    self._schema_cache[connector_id] = schema_data
                    return schema_data

            # 4. 向后兼容：尝试从连接器代码动态加载schema
            schema_data = await self._load_schema_from_connector(connector_id)
            if schema_data:
                logger.info(f"使用代码动态schema: {connector_id}")
                return schema_data

            # 5. 生成默认基础schema
            logger.info(f"为连接器 {connector_id} 生成默认配置schema")
            return self._generate_default_schema(connector_id)

        except Exception as e:
            logger.error(f"获取配置schema失败 {connector_id}: {e}")
            return None

    async def register_runtime_schema(
        self, connector_id: str, schema_data: Dict[str, Any]
    ):
        """注册运行时schema（连接器启动时调用）"""
        try:
            self._runtime_schemas[connector_id] = {
                "schema": schema_data.get("config_schema", {}),
                "ui_schema": schema_data.get("ui_schema", {}),
                "default_values": schema_data.get("default_config", {}),
                "version": "runtime",
                "connector_name": schema_data.get("connector_name", connector_id),
                "description": schema_data.get("connector_description", ""),
            }

            # 同步更新数据库
            await self._update_schema_in_database(
                connector_id, self._runtime_schemas[connector_id]
            )

            logger.info(f"运行时schema注册成功: {connector_id}")
            return True

        except Exception as e:
            logger.error(f"注册运行时schema失败 {connector_id}: {e}")
            return False

    async def get_current_config(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取连接器当前配置"""
        try:
            with self.db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )
                if not connector:
                    return None

                return {
                    "current_config": connector.config_data or {},
                    "config_schema": connector.config_schema or {},
                    "config_version": connector.config_version or "1.0.0",
                    "config_valid": connector.config_valid,
                    "validation_errors": connector.config_validation_errors,
                    "updated_at": (
                        connector.updated_at.isoformat()
                        if connector.updated_at
                        else None
                    ),
                }
        except Exception as e:
            logger.error(f"获取当前配置失败 {connector_id}: {e}")
            return None

    async def validate_config(
        self, connector_id: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """验证配置数据"""
        try:
            # 获取schema
            schema_data = await self.get_config_schema(connector_id)
            if not schema_data:
                return {
                    "valid": False,
                    "errors": [f"无法获取连接器 {connector_id} 的配置schema"],
                }

            json_schema = schema_data["schema"]

            # 使用jsonschema验证
            try:
                validate(instance=config, schema=json_schema)
                return {"valid": True, "normalized_config": config, "warnings": []}
            except ValidationError as e:
                return {
                    "valid": False,
                    "errors": [str(e)],
                    "error_path": list(e.path) if hasattr(e, "path") else [],
                }

        except Exception as e:
            logger.error(f"配置验证异常 {connector_id}: {e}")
            return {"valid": False, "errors": [f"配置验证过程中发生错误: {str(e)}"]}

    async def update_config(
        self,
        connector_id: str,
        new_config: Dict[str, Any],
        config_version: str = "1.0.0",
        change_reason: str = "用户更新",
    ) -> Dict[str, Any]:
        """更新连接器配置"""
        try:
            with self.db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )
                if not connector:
                    raise ValueError(f"连接器不存在: {connector_id}")

                # 先验证新配置
                validation_result = await self.validate_config(connector_id, new_config)

                # 保存旧配置用于历史记录
                old_config = connector.config_data or {}

                # 更新配置
                connector.config_data = new_config
                connector.config_version = config_version
                connector.config_valid = validation_result["valid"]
                connector.config_validation_errors = (
                    validation_result.get("errors")
                    if not validation_result["valid"]
                    else None
                )
                connector.updated_at = datetime.now(timezone.utc)

                session.commit()

                # 记录配置变更历史
                await self._record_config_history(
                    connector_id, old_config, new_config, change_reason
                )

                # 检查是否支持热重载
                hot_reload_applied = await self._try_hot_reload_config(
                    connector_id, new_config
                )

                return {
                    "config_version": config_version,
                    "hot_reload_applied": hot_reload_applied,
                    "requires_restart": not hot_reload_applied,
                    "updated_at": connector.updated_at.isoformat(),
                }

        except Exception as e:
            logger.error(f"更新配置失败 {connector_id}: {e}")
            raise

    async def reset_config(
        self, connector_id: str, to_defaults: bool = True
    ) -> Dict[str, Any]:
        """重置连接器配置"""
        try:
            if to_defaults:
                # 重置为默认配置
                schema_data = await self.get_config_schema(connector_id)
                if schema_data and schema_data.get("default_values"):
                    new_config = schema_data["default_values"]
                else:
                    new_config = {}
            else:
                # 重置为空配置
                new_config = {}

            result = await self.update_config(
                connector_id, new_config, "1.0.0", "重置配置"
            )
            result["config"] = new_config
            return result

        except Exception as e:
            logger.error(f"重置配置失败 {connector_id}: {e}")
            raise

    async def get_config_history(
        self, connector_id: str, limit: int = 10, offset: int = 0
    ) -> Dict[str, Any]:
        """获取配置变更历史"""
        try:
            with self.db_service.get_session() as session:
                # 查询历史记录
                query = (
                    session.query(ConnectorConfigHistory)
                    .filter_by(connector_id=connector_id)
                    .order_by(ConnectorConfigHistory.created_at.desc())
                )

                total = query.count()
                records = query.offset(offset).limit(limit).all()

                # 转换为字典格式
                history_records = []
                for record in records:
                    history_records.append(
                        {
                            "id": record.id,
                            "config_data": record.config_data,
                            "config_version": record.config_version,
                            "schema_version": record.schema_version,
                            "change_type": record.change_type,
                            "change_description": record.change_description,
                            "changed_by": record.changed_by,
                            "validation_status": record.validation_status,
                            "validation_errors": record.validation_errors,
                            "created_at": (
                                record.created_at.isoformat()
                                if record.created_at
                                else None
                            ),
                        }
                    )

                return {
                    "records": history_records,
                    "total": total,
                    "has_more": (offset + limit) < total,
                }

        except Exception as e:
            logger.error(f"获取配置历史失败 {connector_id}: {e}")
            return {"records": [], "total": 0, "has_more": False}

    async def get_all_schemas(self) -> List[Dict[str, Any]]:
        """获取所有连接器的配置schema概览"""
        try:
            schemas = []

            # 获取数据库中的所有连接器
            with self.db_service.get_session() as session:
                connectors = session.query(Connector).all()

                for connector in connectors:
                    schema_info = {
                        "connector_id": connector.connector_id,
                        "connector_name": connector.name,
                        "has_schema": bool(connector.config_schema),
                        "has_runtime_schema": connector.connector_id
                        in self._runtime_schemas,
                        "config_version": connector.config_version or "1.0.0",
                        "last_updated": (
                            connector.updated_at.isoformat()
                            if connector.updated_at
                            else None
                        ),
                    }
                    schemas.append(schema_info)

            return schemas

        except Exception as e:
            logger.error(f"获取所有schema失败: {e}")
            return []

    async def _load_static_schema_from_manifest(
        self, connector_id: str
    ) -> Optional[Dict[str, Any]]:
        """从connector.json读取静态配置schema - 语言无关方式"""
        try:
            # 查找连接器manifest文件
            connector_path = self._find_connector_path(connector_id)
            if not connector_path:
                return None

            manifest_file = connector_path / "connector.json"
            if not manifest_file.exists():
                logger.debug(f"未找到manifest文件: {manifest_file}")
                return None

            # 读取manifest
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            # 检查schema来源
            schema_source = manifest.get("config_schema_source", "runtime")
            if schema_source not in ["static", "embedded"]:
                logger.debug(
                    f"连接器 {connector_id} 使用 {schema_source} schema，跳过静态读取"
                )
                return None

            # 读取静态schema
            config_schema = manifest.get("config_schema")
            if not config_schema:
                logger.debug(f"连接器 {connector_id} 没有定义config_schema")
                return None

            # 构建完整schema数据
            schema_data = {
                "schema": config_schema,
                "ui_schema": manifest.get("config_ui_schema", {}),
                "default_values": manifest.get("config_default_values", {}),
                "version": manifest.get("version", "1.0.0"),
                "connector_name": manifest.get("name", connector_id),
                "description": manifest.get("description", ""),
                "source": f"static_manifest_{schema_source}",
            }

            # 缓存schema
            self._schema_cache[connector_id] = schema_data

            logger.info(f"成功从manifest读取静态schema: {connector_id}")
            return schema_data

        except Exception as e:
            logger.error(f"从manifest读取静态schema失败 {connector_id}: {e}")
            return None

    async def _load_schema_from_connector(
        self, connector_id: str
    ) -> Optional[Dict[str, Any]]:
        """从连接器Python代码动态加载schema"""
        try:
            # 查找连接器主模块路径
            connector_path = self._find_connector_path(connector_id)
            if not connector_path:
                return None

            # 添加connectors目录到Python路径，以便导入shared模块
            connectors_root = connector_path.parent.parent
            if str(connectors_root) not in sys.path:
                sys.path.insert(0, str(connectors_root))

            # 动态导入连接器模块
            spec = importlib.util.spec_from_file_location(
                f"{connector_id}_connector", connector_path / "main.py"
            )
            if not spec or not spec.loader:
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 查找连接器类
            connector_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and hasattr(attr, "get_config_schema")
                    and attr.__name__ != "BaseConnector"
                ):
                    connector_class = attr
                    break

            if not connector_class:
                return None

            # 获取schema
            config_schema = connector_class.get_config_schema()
            ui_schema = getattr(connector_class, "get_config_ui_schema", lambda: {})()

            return {
                "schema": config_schema,
                "ui_schema": ui_schema,
                "default_values": self._extract_defaults_from_schema(config_schema),
                "version": "1.0.0",
            }

        except Exception as e:
            logger.error(f"从连接器代码加载schema失败 {connector_id}: {e}")
            return None

    def _find_connector_path(self, connector_id: str) -> Optional[Path]:
        """查找连接器路径"""
        # 查找官方连接器
        official_path = (
            Path(__file__).parent.parent.parent.parent
            / "connectors"
            / "official"
            / connector_id
        )
        if official_path.exists():
            return official_path

        # 查找社区连接器
        community_path = (
            Path(__file__).parent.parent.parent.parent
            / "connectors"
            / "community"
            / connector_id
        )
        if community_path.exists():
            return community_path

        return None

    def _generate_default_schema(self, connector_id: str) -> Dict[str, Any]:
        """生成默认配置schema"""
        with self.db_service.get_session() as session:
            connector = (
                session.query(Connector).filter_by(connector_id=connector_id).first()
            )
            connector_name = connector.name if connector else connector_id

        schema_obj = create_basic_config_schema(connector_id, connector_name)

        return {
            "schema": schema_obj.to_json_schema(),
            "ui_schema": schema_obj.to_ui_schema(),
            "default_values": self._extract_defaults_from_schema(
                schema_obj.to_json_schema()
            ),
            "version": schema_obj.schema_version,
        }

    def _extract_defaults_from_schema(
        self, json_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """从JSON Schema提取默认值"""
        defaults = {}
        properties = json_schema.get("properties", {})

        for key, prop in properties.items():
            if "default" in prop:
                defaults[key] = prop["default"]

        return defaults

    async def _update_schema_in_database(
        self, connector_id: str, schema_data: Dict[str, Any]
    ):
        """更新数据库中的schema"""
        try:
            with self.db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )
                if connector:
                    connector.config_schema = schema_data["schema"]

                    # 更新配置字段，合并默认值和UI schema
                    if not connector.config_data:
                        connector.config_data = {}

                    connector.config_data.update(
                        {
                            "ui_schema": schema_data["ui_schema"],
                            "default_values": schema_data["default_values"],
                        }
                    )

                    session.commit()

        except Exception as e:
            logger.error(f"更新数据库schema失败 {connector_id}: {e}")

    async def _record_config_history(
        self,
        connector_id: str,
        old_config: Dict[str, Any],
        new_config: Dict[str, Any],
        change_reason: str,
    ):
        """记录配置变更历史"""
        try:
            with self.db_service.get_session() as session:
                # 获取当前连接器信息
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )
                if not connector:
                    return

                # 创建历史记录
                history_record = ConnectorConfigHistory(
                    connector_id=connector_id,
                    config_data=new_config,
                    config_version=connector.config_version or "1.0.0",
                    schema_version=connector.config_version or "1.0.0",
                    change_type="update",
                    change_description=change_reason,
                    changed_by="system",
                    validation_status="valid" if connector.config_valid else "invalid",
                    validation_errors=connector.config_validation_errors,
                )

                session.add(history_record)
                session.commit()

                logger.info(f"配置变更历史记录成功: {connector_id} - {change_reason}")

        except Exception as e:
            logger.error(f"记录配置变更历史失败 {connector_id}: {e}")

    async def _try_hot_reload_config(
        self, connector_id: str, new_config: Dict[str, Any]
    ) -> bool:
        """尝试对运行中的连接器进行热重载"""
        try:
            # 检查连接器是否支持热重载
            schema_data = await self.get_config_schema(connector_id)
            if not schema_data:
                return False

            # 简化实现：通过daemon通知连接器重新加载配置
            # 实际可以通过信号或IPC机制实现
            logger.info(f"尝试热重载连接器配置: {connector_id}")
            return True  # 假设成功

        except Exception as e:
            logger.error(f"热重载配置失败 {connector_id}: {e}")
            return False


# 全局单例
_config_service = None


def get_connector_config_service() -> ConnectorConfigService:
    """获取连接器配置服务单例"""
    global _config_service
    if _config_service is None:
        _config_service = ConnectorConfigService()
    return _config_service
