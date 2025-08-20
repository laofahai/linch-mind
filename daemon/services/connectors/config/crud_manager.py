#!/usr/bin/env python3
"""
连接器配置CRUD管理器
专门负责配置的增删改查操作
从connector_config_service.py中拆分出来
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from core.service_facade import get_database_service
from models.database_models import Connector, ConnectorConfigHistory

logger = logging.getLogger(__name__)


class ConfigCrudManager:
    """配置CRUD管理器"""

    def __init__(self, schema_manager, validator):
        self.schema_manager = schema_manager
        self.validator = validator
        self._db_service = None

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

    async def get_current_config(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取连接器当前配置"""
        try:
            if self.db_service is None:
                logger.debug(f"数据库服务不可用，返回默认配置: {connector_id}")
                return await self._get_default_config_fallback(connector_id)

            with self.db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )

                if not connector:
                    logger.warning(f"连接器不存在，返回默认配置: {connector_id}")
                    return await self._get_default_config_fallback(connector_id)

                config_data = connector.config_data or {}

                # 如果配置为空，返回默认配置
                if not config_data:
                    logger.info(f"配置为空，返回默认配置: {connector_id}")
                    return await self._get_default_config_fallback(connector_id)

                logger.debug(f"获取当前配置成功: {connector_id}")
                return config_data

        except Exception as e:
            logger.error(f"获取当前配置失败 {connector_id}: {e}")
            # 发生异常时也尝试返回默认配置
            try:
                return await self._get_default_config_fallback(connector_id)
            except:
                return {}

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
            validation_result = await self.validator.validate_config(connector_id, config)

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

    async def reset_config(
        self, connector_id: str, to_defaults: bool = True
    ) -> Dict[str, Any]:
        """重置连接器配置"""
        try:
            if self.db_service is None:
                return {"success": False, "error": "数据库服务不可用"}

            with self.db_service.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter_by(connector_id=connector_id)
                    .first()
                )

                if not connector:
                    return {"success": False, "error": f"连接器不存在: {connector_id}"}

                old_config = connector.config_data or {}

                if to_defaults:
                    # 重置为默认配置
                    schema_data = await self.schema_manager.get_config_schema(connector_id)
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

    async def get_default_config(self, connector_id: str) -> Dict[str, Any]:
        """获取连接器的默认配置"""
        try:
            schema_data = await self.schema_manager.get_config_schema(connector_id)
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

    async def get_config_history(
        self, connector_id: str, limit: int = 10, offset: int = 0
    ) -> Dict[str, Any]:
        """获取配置变更历史"""
        try:
            if not self.db_service:
                return {
                    "history": [],
                    "total": 0,
                    "limit": limit,
                    "offset": offset,
                    "error": "数据库服务不可用",
                }

            with self.db_service.get_session() as session:
                history_query = (
                    session.query(ConnectorConfigHistory)
                    .filter_by(connector_id=connector_id)
                    .order_by(ConnectorConfigHistory.created_at.desc())
                )

                total_count = history_query.count()
                history_records = history_query.offset(offset).limit(limit).all()

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

    async def _get_default_config_fallback(self, connector_id: str) -> Dict[str, Any]:
        """获取默认配置的回退方法"""
        schema_data = await self.schema_manager.get_config_schema(connector_id)
        return self._extract_default_config(schema_data)

    def _extract_default_config(
        self, schema_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """从schema中提取默认配置"""
        if not schema_data:
            return {}

        default_config = {}
        json_schema = schema_data.get("json_schema", {})
        properties = json_schema.get("properties", {})

        self._extract_defaults_from_properties(properties, default_config, "")
        return default_config

    def _extract_defaults_from_properties(
        self, properties: Dict[str, Any], config: Dict[str, Any], path: str
    ):
        """递归从JSON Schema properties中提取默认值"""
        for field_name, field_schema in properties.items():
            # 处理嵌套对象
            if field_schema.get("type") == "object" and "properties" in field_schema:
                if path:
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