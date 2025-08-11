#!/usr/bin/env python3
"""
连接器配置服务
提供连接器配置的schema获取、验证、更新等功能
替代已删除的unified_connector_service
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.service_facade import get_database_service
from models.database_models import Connector, ConnectorConfigHistory

from .connector_config_schema import create_basic_config_schema

logger = logging.getLogger(__name__)


class ConnectorConfigService:
    """连接器配置服务

    提供配置相关的核心功能：
    - 配置schema获取和管理
    - 配置验证和更新
    - 配置历史记录
    - 连接器配置文件读取
    - 默认配置管理和应用
    - 配置重置和合并
    """

    def __init__(self, connectors_dir: Optional[Path] = None):
        # 延迟初始化数据库服务，避免循环依赖
        self._db_service = None

        # 🆕 环境感知的连接器配置
        from core.environment_manager import get_environment_manager

        self.env_manager = get_environment_manager()

        # 智能查找connectors目录 - 环境特定配置
        if connectors_dir:
            self.connectors_dir = connectors_dir
        else:
            possible_dirs = [
                Path("connectors"),
                Path("../connectors"),
                Path(__file__).parent.parent.parent.parent
                / "connectors",  # 从daemon/services/connectors向上找
                self.env_manager.current_config.base_path
                / "connectors",  # 环境特定连接器目录
            ]

            self.connectors_dir = None
            for dir_path in possible_dirs:
                if dir_path.exists():
                    self.connectors_dir = dir_path
                    break

            # 如果都找不到，使用默认值
            if not self.connectors_dir:
                self.connectors_dir = Path("connectors")

    @property
    def db_service(self):
        """延迟获取数据库服务，避免初始化时的循环依赖"""
        if self._db_service is None:
            try:
                self._db_service = get_database_service()
            except Exception as e:
                logger.warning(f"数据库服务暂不可用: {e}")
                return None
        return self._db_service

    def get_connector_config(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取连接器配置文件内容 (connector.json)

        此方法修复了 'ConnectorConfigService' object has no attribute 'get_connector_config' 错误
        """
        try:
            # 查找connector.json文件的可能路径
            potential_paths = [
                self.connectors_dir / "official" / connector_id / "connector.json",
                self.connectors_dir / connector_id / "connector.json",
                Path("connectors") / "official" / connector_id / "connector.json",
                Path("connectors") / connector_id / "connector.json",
            ]

            for config_path in potential_paths:
                if config_path.exists():
                    with open(config_path, "r", encoding="utf-8") as f:
                        config_data = json.load(f)

                    logger.debug(f"成功加载连接器配置: {config_path}")
                    return config_data

            logger.warning(f"未找到连接器配置文件: {connector_id}")
            logger.debug(f"搜索路径: {[str(p) for p in potential_paths]}")
            return None

        except Exception as e:
            logger.error(f"读取连接器配置失败 {connector_id}: {e}")
            return None

    async def get_config_schema(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取连接器的配置schema"""
        try:
            # 首先尝试从连接器目录加载schema文件
            schema_data = self._load_schema_from_file(connector_id)

            if schema_data:
                # 如果找到了连接器自定义的schema，直接返回
                logger.debug(f"使用连接器自定义schema: {connector_id}")
                return schema_data

            # 如果没有找到自定义schema，检查是否应该返回空schema而不是基础schema
            # 这样可以避免显示不必要的默认配置项
            connector_config = self.get_connector_config(connector_id)
            if (
                connector_config
                and connector_config.get("config_schema_source") == "none"
            ):
                # 连接器明确表示不需要配置
                logger.debug(f"连接器无需配置: {connector_id}")
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

            # 否则生成基础schema（带默认的三个配置项）
            schema_data = self._generate_basic_schema(connector_id)
            logger.debug(f"使用生成的基础schema: {connector_id}")
            return schema_data

        except Exception as e:
            logger.error(f"获取配置schema失败 {connector_id}: {e}")
            return None

    def _load_schema_from_file(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """从文件加载schema"""
        try:
            # 1. 首先尝试从独立的schema文件加载
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

            # 2. 如果没有独立schema文件，尝试从connector.json中提取schema
            connector_config = self.get_connector_config(connector_id)
            if connector_config:
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
                            "connector_name": connector_config.get(
                                "name", connector_id
                            ),
                            "generated": False,
                        },
                    }

            return None

        except Exception as e:
            logger.warning(f"从文件加载schema失败 {connector_id}: {e}")
            return None

    def _generate_basic_schema(self, connector_id: str) -> Dict[str, Any]:
        """生成基础的配置schema"""
        try:
            connector_name = connector_id  # 默认值

            # 尝试从数据库获取连接器信息
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
            else:
                logger.debug(f"数据库服务不可用，使用默认连接器名称: {connector_id}")

            # 创建基础schema
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
            # 返回最小schema
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

    async def get_current_config(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取连接器当前配置

        修复UI配置显示问题：
        - 如果数据库中配置为空，自动返回默认配置
        - 这样UI就能显示正确的配置项而不是空白
        """
        try:
            if self.db_service is None:
                logger.debug(f"数据库服务不可用，返回默认配置: {connector_id}")
                # 数据库不可用时返回默认配置而不是空配置
                schema_data = await self.get_config_schema(connector_id)
                default_config = self._extract_default_config(schema_data)
                logger.debug(f"使用默认配置: {default_config}")
                return default_config

            with self.db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )

                if not connector:
                    logger.warning(f"连接器不存在，返回默认配置: {connector_id}")
                    # 连接器不存在时返回默认配置
                    schema_data = await self.get_config_schema(connector_id)
                    default_config = self._extract_default_config(schema_data)
                    logger.debug(f"使用默认配置: {default_config}")
                    return default_config

                # 获取数据库中的配置数据
                config_data = connector.config_data or {}

                # 关键修复：如果配置为空，返回默认配置
                if not config_data or len(config_data) == 0:
                    logger.info(f"配置为空，返回默认配置: {connector_id}")
                    schema_data = await self.get_config_schema(connector_id)
                    default_config = self._extract_default_config(schema_data)
                    logger.debug(f"使用默认配置: {default_config}")
                    return default_config

                logger.debug(f"获取当前配置成功: {connector_id}")
                return config_data

        except Exception as e:
            logger.error(f"获取当前配置失败 {connector_id}: {e}")
            # 发生异常时也尝试返回默认配置
            try:
                schema_data = await self.get_config_schema(connector_id)
                default_config = self._extract_default_config(schema_data)
                logger.debug(f"异常时使用默认配置: {default_config}")
                return default_config
            except:
                return {}

    async def validate_config(
        self, connector_id: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """验证配置数据"""
        try:
            # 获取schema进行验证
            schema_data = await self.get_config_schema(connector_id)

            if not schema_data:
                return {"valid": False, "errors": [{"message": "无法获取配置schema"}]}

            json_schema = schema_data.get("json_schema", {})

            # 基础验证：检查必需字段
            errors = []
            required_fields = json_schema.get("required", [])

            for field in required_fields:
                if field not in config:
                    errors.append(
                        {"field": field, "message": f"必需字段 '{field}' 缺失"}
                    )

            # 类型验证
            properties = json_schema.get("properties", {})
            for field_name, field_value in config.items():
                if field_name in properties:
                    field_schema = properties[field_name]
                    field_type = field_schema.get("type", "string")

                    if not self._validate_field_type(field_value, field_type):
                        errors.append(
                            {
                                "field": field_name,
                                "message": f"字段 '{field_name}' 类型错误，期望 {field_type}",
                            }
                        )

            is_valid = len(errors) == 0

            logger.debug(f"配置验证完成: {connector_id}, valid={is_valid}")

            return {
                "valid": is_valid,
                "errors": errors,
                "warnings": [],  # 可以添加警告信息
            }

        except Exception as e:
            logger.error(f"配置验证失败 {connector_id}: {e}")
            return {"valid": False, "errors": [{"message": f"验证过程出错: {str(e)}"}]}

    def _validate_field_type(self, value: Any, expected_type: str) -> bool:
        """验证字段类型"""
        try:
            if expected_type == "string":
                return isinstance(value, str)
            elif expected_type == "integer":
                return isinstance(value, int)
            elif expected_type == "number":
                return isinstance(value, (int, float))
            elif expected_type == "boolean":
                return isinstance(value, bool)
            elif expected_type == "array":
                return isinstance(value, list)
            elif expected_type == "object":
                return isinstance(value, dict)
            else:
                return True  # 未知类型，假设有效
        except:
            return False

    async def update_config(
        self,
        connector_id: str,
        config: Dict[str, Any],
        config_version: str = "1.0.0",
        change_reason: str = "用户更新",
    ) -> Dict[str, Any]:
        """更新连接器配置"""
        try:
            # 首先验证配置
            validation_result = await self.validate_config(connector_id, config)

            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": "配置验证失败",
                    "validation_errors": validation_result["errors"],
                }

            if self.db_service is None:
                logger.error(f"数据库服务不可用，无法更新配置: {connector_id}")
                return {"success": False, "error": "数据库服务不可用，无法更新配置"}

            with self.db_service.get_session() as session:
                # 获取连接器
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )

                if not connector:
                    return {"success": False, "error": f"连接器不存在: {connector_id}"}

                # 保存旧配置到历史记录
                old_config = connector.config_data or {}

                if old_config != config:
                    self._save_config_history(
                        session=session,
                        connector_id=connector_id,
                        old_config=old_config,
                        new_config=config,
                        config_version=config_version,
                        change_reason=change_reason,
                    )

                # 更新连接器配置
                connector.config_data = config
                connector.updated_at = datetime.now(timezone.utc)
                session.commit()

                logger.info(f"配置更新成功: {connector_id}")

                return {
                    "success": True,
                    "message": "配置更新成功",
                    "config_version": config_version,
                }

        except Exception as e:
            logger.error(f"更新配置失败 {connector_id}: {e}")
            return {"success": False, "error": f"更新配置时出错: {str(e)}"}

    def _save_config_history(
        self,
        session,
        connector_id: str,
        old_config: Dict[str, Any],
        new_config: Dict[str, Any],
        config_version: str,
        change_reason: str,
    ):
        """保存配置历史记录"""
        try:
            history_record = ConnectorConfigHistory(
                connector_id=connector_id,
                config_data=new_config,
                config_version=config_version,
                schema_version="1.0.0",
                change_type="update",
                change_description=change_reason,
                changed_by="user",
                validation_status="valid",
            )

            session.add(history_record)
            logger.debug(f"配置历史记录已保存: {connector_id}")

        except Exception as e:
            logger.warning(f"保存配置历史失败 {connector_id}: {e}")

    async def reset_config(
        self, connector_id: str, to_defaults: bool = True
    ) -> Dict[str, Any]:
        """重置连接器配置"""
        try:
            with self.db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )

                if not connector:
                    return {"success": False, "error": f"连接器不存在: {connector_id}"}

                # 保存旧配置到历史记录
                old_config = connector.config_data or {}

                if to_defaults:
                    # 重置为默认配置
                    schema_data = await self.get_config_schema(connector_id)
                    default_config = self._extract_default_config(schema_data)
                    change_reason = "重置为默认配置"
                else:
                    # 重置为空配置
                    default_config = {}
                    change_reason = "重置为空配置"

                # 保存历史记录
                if old_config != default_config:
                    self._save_config_history(
                        session=session,
                        connector_id=connector_id,
                        old_config=old_config,
                        new_config=default_config,
                        config_version="1.0.0",
                        change_reason=change_reason,
                    )

                # 更新连接器配置
                connector.config_data = default_config
                connector.updated_at = datetime.now(timezone.utc)
                session.commit()

                logger.info(f"配置重置成功: {connector_id}, to_defaults={to_defaults}")

                return {
                    "success": True,
                    "message": f"配置{'重置为默认值' if to_defaults else '重置为空'}成功",
                    "config": default_config,
                    "reset_to_defaults": to_defaults,
                }

        except Exception as e:
            logger.error(f"重置配置失败 {connector_id}: {e}")
            return {"success": False, "error": f"重置配置时出错: {str(e)}"}

    def _extract_default_config(
        self, schema_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """从schema中提取默认配置

        优先级顺序:
        1. connector.json中的config_default_values (最高优先级)
        2. JSON Schema中properties的default值
        3. 基础模板的默认值
        """
        if not schema_data:
            return {}

        default_config = {}

        # 1. 首先尝试从connector.json的config_default_values中提取默认值（最高优先级）
        try:
            connector_id = schema_data.get("metadata", {}).get("connector_id")
            if connector_id:
                connector_config = self.get_connector_config(connector_id)
                if connector_config and "config_default_values" in connector_config:
                    default_values = connector_config["config_default_values"]
                    logger.debug(f"从connector.json加载默认值: {connector_id}")
                    # 深拷贝嵌套对象，避免引用问题
                    default_config = self._deep_copy_config(default_values)
        except Exception as e:
            logger.warning(f"从connector.json提取默认值失败: {e}")

        # 2. 从JSON Schema的properties中提取默认值（作为补充）
        json_schema = schema_data.get("json_schema", {})
        properties = json_schema.get("properties", {})

        self._extract_defaults_from_properties(properties, default_config, "")

        # 3. 不再添加通用的基础模板默认值
        # enabled, auto_start, log_level 这些应该在UI层面处理，不在连接器配置中

        logger.debug(f"提取的默认配置: {default_config}")
        return default_config

    def _deep_copy_config(self, config: Any) -> Any:
        """深拷贝配置对象，处理嵌套结构"""
        import copy

        return copy.deepcopy(config)

    def _extract_defaults_from_properties(
        self, properties: Dict[str, Any], config: Dict[str, Any], path: str
    ):
        """递归从JSON Schema properties中提取默认值"""
        for field_name, field_schema in properties.items():
            f"{path}.{field_name}" if path else field_name

            # 处理嵌套对象
            if field_schema.get("type") == "object" and "properties" in field_schema:
                # 确保父对象存在
                if path:
                    # 处理嵌套路径，如 "content_filters.filter_sensitive"
                    keys = path.split(".")
                    current = config
                    for key in keys:
                        if key not in current:
                            current[key] = {}
                        current = current[key]
                    if field_name not in current:
                        current[field_name] = {}
                    self._extract_defaults_from_properties(
                        field_schema["properties"], current[field_name], ""
                    )
                else:
                    if field_name not in config:
                        config[field_name] = {}
                    self._extract_defaults_from_properties(
                        field_schema["properties"], config[field_name], ""
                    )

            # 处理基本类型的默认值
            elif "default" in field_schema:
                if path:
                    # 处理嵌套路径
                    keys = path.split(".")
                    current = config
                    for key in keys:
                        if key not in current:
                            current[key] = {}
                        current = current[key]
                    if field_name not in current:
                        current[field_name] = field_schema["default"]
                else:
                    if field_name not in config:
                        config[field_name] = field_schema["default"]

    async def get_config_history(
        self, connector_id: str, limit: int = 10, offset: int = 0
    ) -> Dict[str, Any]:
        """获取配置变更历史"""
        try:
            with self.db_service.get_session() as session:
                # 查询历史记录
                history_query = (
                    session.query(ConnectorConfigHistory)
                    .filter_by(connector_id=connector_id)
                    .order_by(ConnectorConfigHistory.created_at.desc())
                )

                total_count = history_query.count()
                history_records = history_query.offset(offset).limit(limit).all()

                # 转换为字典格式
                history_data = []
                for record in history_records:
                    history_data.append(
                        {
                            "id": record.id,
                            "connector_id": record.connector_id,
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

                logger.debug(
                    f"获取配置历史成功: {connector_id}, {len(history_data)} 条记录"
                )

                return {
                    "history": history_data,
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                }

        except Exception as e:
            logger.error(f"获取配置历史失败 {connector_id}: {e}")
            return {
                "history": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "error": str(e),
            }

    async def get_all_schemas(self) -> Dict[str, Any]:
        """获取所有连接器的配置Schema概览"""
        try:
            with self.db_service.get_session() as session:
                # 获取所有连接器
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

    async def get_default_config(self, connector_id: str) -> Dict[str, Any]:
        """获取连接器的默认配置

        此方法专门用于获取默认配置，不会查询数据库中的当前配置
        """
        try:
            schema_data = await self.get_config_schema(connector_id)
            default_config = self._extract_default_config(schema_data)

            logger.debug(f"获取默认配置成功: {connector_id}")
            return {
                "success": True,
                "default_config": default_config,
                "connector_id": connector_id,
            }

        except Exception as e:
            logger.error(f"获取默认配置失败 {connector_id}: {e}")
            return {
                "success": False,
                "error": f"获取默认配置时出错: {str(e)}",
                "default_config": {},
                "connector_id": connector_id,
            }

    async def apply_defaults_to_config(
        self, connector_id: str, current_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """将默认值应用到现有配置中

        合并策略:
        1. 保留现有配置的所有值
        2. 添加缺失的默认值
        3. 不覆盖已存在的配置
        """
        try:
            if current_config is None:
                current_config = await self.get_current_config(connector_id) or {}

            schema_data = await self.get_config_schema(connector_id)
            default_config = self._extract_default_config(schema_data)

            # 合并配置：保留现有值，填充默认值
            merged_config = self._merge_configs(default_config, current_config)

            logger.debug(f"应用默认值到配置成功: {connector_id}")
            return {
                "success": True,
                "merged_config": merged_config,
                "applied_defaults": True,
            }

        except Exception as e:
            logger.error(f"应用默认值失败 {connector_id}: {e}")
            return {
                "success": False,
                "error": f"应用默认值时出错: {str(e)}",
                "merged_config": current_config or {},
                "applied_defaults": False,
            }

    def _merge_configs(
        self, default_config: Dict[str, Any], current_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """递归合并配置，保留现有值，填充默认值"""
        import copy

        merged = copy.deepcopy(default_config)

        def merge_recursive(target: Dict[str, Any], source: Dict[str, Any]):
            for key, value in source.items():
                if key in target:
                    if isinstance(target[key], dict) and isinstance(value, dict):
                        # 递归合并嵌套对象
                        merge_recursive(target[key], value)
                    else:
                        # 用现有值覆盖默认值
                        target[key] = value
                else:
                    # 添加新的现有值
                    target[key] = value

        merge_recursive(merged, current_config)
        return merged

    # 🆕 环境特定的配置方法
    def get_environment_connector_config(self, connector_id: str) -> Dict[str, Any]:
        """获取连接器的环境特定配置"""
        try:
            current_env = self.env_manager.current_environment.value
            env_config_path = (
                self.env_manager.current_config.config_dir
                / "connectors"
                / f"{connector_id}.json"
            )

            # 检查环境特定配置文件是否存在
            if env_config_path.exists():
                with open(env_config_path, "r", encoding="utf-8") as f:
                    env_config = json.load(f)
                    logger.info(f"加载环境特定配置: {connector_id} ({current_env})")
                    return env_config
            else:
                logger.debug(f"环境特定配置不存在: {env_config_path}")
                return {}

        except Exception as e:
            logger.warning(f"加载环境特定配置失败 {connector_id}: {e}")
            return {}

    def save_environment_connector_config(
        self, connector_id: str, config: Dict[str, Any]
    ) -> bool:
        """保存连接器的环境特定配置"""
        try:
            current_env = self.env_manager.current_environment.value
            env_config_dir = self.env_manager.current_config.config_dir / "connectors"
            env_config_dir.mkdir(parents=True, exist_ok=True)

            env_config_path = env_config_dir / f"{connector_id}.json"

            # 添加环境标识和时间戳
            config_with_meta = {
                **config,
                "_environment": current_env,
                "_updated_at": datetime.now(timezone.utc).isoformat(),
                "_created_by": "connector_config_service",
            }

            with open(env_config_path, "w", encoding="utf-8") as f:
                json.dump(config_with_meta, f, indent=2, ensure_ascii=False)

            logger.info(
                f"保存环境特定配置: {connector_id} ({current_env}) -> {env_config_path}"
            )
            return True

        except Exception as e:
            logger.error(f"保存环境特定配置失败 {connector_id}: {e}")
            return False

    async def get_merged_environment_config(
        self, connector_id: str
    ) -> Optional[Dict[str, Any]]:
        """获取合并的环境配置 (默认配置 + 环境特定配置 + 数据库配置)"""
        try:
            # 1. 获取默认配置
            default_config = await self.get_default_config(connector_id)

            # 2. 获取环境特定配置
            env_config = self.get_environment_connector_config(connector_id)

            # 3. 获取数据库中的当前配置
            current_config = await self.get_current_config(connector_id) or {}

            # 4. 合并配置 (优先级: 数据库配置 > 环境配置 > 默认配置)
            merged_config = {}

            # 合并函数
            def deep_merge(base: dict, override: dict):
                for key, value in override.items():
                    if (
                        key in base
                        and isinstance(base[key], dict)
                        and isinstance(value, dict)
                    ):
                        deep_merge(base[key], value)
                    else:
                        base[key] = value

            # 按优先级合并
            deep_merge(merged_config, default_config)
            deep_merge(merged_config, env_config)
            deep_merge(merged_config, current_config)

            # 添加环境元信息
            merged_config["_environment_info"] = {
                "current_environment": self.env_manager.current_environment.value,
                "has_env_config": bool(env_config),
                "has_db_config": bool(current_config),
                "config_source": "merged",
            }

            logger.debug(f"合并环境配置完成: {connector_id}")
            return merged_config

        except Exception as e:
            logger.error(f"合并环境配置失败 {connector_id}: {e}")
            return None

    def list_environment_connectors(self) -> List[Dict[str, Any]]:
        """列出当前环境的所有连接器配置"""
        try:
            connectors = []
            current_env = self.env_manager.current_environment.value
            env_config_dir = self.env_manager.current_config.config_dir / "connectors"

            if env_config_dir.exists():
                for config_file in env_config_dir.glob("*.json"):
                    connector_id = config_file.stem
                    try:
                        with open(config_file, "r", encoding="utf-8") as f:
                            config = json.load(f)

                        connectors.append(
                            {
                                "connector_id": connector_id,
                                "environment": config.get("_environment", current_env),
                                "updated_at": config.get("_updated_at"),
                                "config_file": str(config_file),
                                "has_config": True,
                            }
                        )

                    except Exception as e:
                        logger.warning(f"读取连接器配置失败 {config_file}: {e}")

            return connectors

        except Exception as e:
            logger.error(f"列出环境连接器配置失败: {e}")
            return []

    def cleanup_environment_configs(self, confirm: bool = False) -> bool:
        """清理当前环境的连接器配置"""
        if not confirm:
            logger.warning("清理环境配置需要确认 (confirm=True)")
            return False

        try:
            current_env = self.env_manager.current_environment.value
            env_config_dir = self.env_manager.current_config.config_dir / "connectors"

            if env_config_dir.exists():
                import shutil

                shutil.rmtree(env_config_dir)
                logger.info(f"清理环境配置完成: {current_env}")
                return True
            else:
                logger.info(f"环境配置目录不存在: {env_config_dir}")
                return True

        except Exception as e:
            logger.error(f"清理环境配置失败: {e}")
            return False


# 全局服务实例获取函数
def get_connector_config_service(
    connectors_dir: Optional[Path] = None,
) -> ConnectorConfigService:
    """获取连接器配置服务实例"""
    return ConnectorConfigService(connectors_dir)
