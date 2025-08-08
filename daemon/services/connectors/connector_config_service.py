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

from models.database_models import Connector, ConnectorConfigHistory
from core.service_facade import get_database_service
from .connector_config_schema import (
    ConnectorConfigSchema,
    create_basic_config_schema,
    COMMON_FIELD_TEMPLATES,
)

logger = logging.getLogger(__name__)


class ConnectorConfigService:
    """连接器配置服务
    
    提供配置相关的核心功能：
    - 配置schema获取和管理
    - 配置验证和更新
    - 配置历史记录
    """

    def __init__(self, connectors_dir: Optional[Path] = None):
        self.db_service = get_database_service()
        self.connectors_dir = connectors_dir or Path("connectors")
        
    async def get_config_schema(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取连接器的配置schema"""
        try:
            # 首先尝试从连接器目录加载schema文件
            schema_data = self._load_schema_from_file(connector_id)
            
            if not schema_data:
                # 如果没有schema文件，生成基础schema
                schema_data = self._generate_basic_schema(connector_id)
            
            logger.debug(f"获取配置schema成功: {connector_id}")
            return schema_data
            
        except Exception as e:
            logger.error(f"获取配置schema失败 {connector_id}: {e}")
            return None

    def _load_schema_from_file(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """从文件加载schema"""
        try:
            # 查找schema文件的多个可能路径
            potential_paths = [
                self.connectors_dir / "official" / connector_id / "config_schema.json",
                self.connectors_dir / "official" / connector_id / "schema.json",
                self.connectors_dir / connector_id / "config_schema.json",
            ]
            
            for schema_path in potential_paths:
                if schema_path.exists():
                    with open(schema_path, 'r', encoding='utf-8') as f:
                        schema_data = json.load(f)
                    
                    logger.debug(f"从文件加载schema: {schema_path}")
                    return schema_data
            
            return None
            
        except Exception as e:
            logger.warning(f"从文件加载schema失败 {connector_id}: {e}")
            return None

    def _generate_basic_schema(self, connector_id: str) -> Dict[str, Any]:
        """生成基础的配置schema"""
        try:
            # 从数据库获取连接器信息
            with self.db_service.get_session() as session:
                connector = session.query(Connector).filter_by(
                    connector_id=connector_id
                ).first()
                
                connector_name = connector.name if connector else connector_id
            
            # 创建基础schema
            basic_schema = create_basic_config_schema(connector_id, connector_name)
            
            return {
                "json_schema": basic_schema.to_json_schema(),
                "ui_schema": basic_schema.to_ui_schema(),
                "metadata": {
                    "schema_version": basic_schema.schema_version,
                    "connector_id": connector_id,
                    "connector_name": connector_name,
                    "generated": True
                }
            }
            
        except Exception as e:
            logger.error(f"生成基础schema失败 {connector_id}: {e}")
            # 返回最小schema
            return {
                "json_schema": {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {},
                    "additionalProperties": True
                },
                "ui_schema": {},
                "metadata": {
                    "schema_version": "1.0.0",
                    "connector_id": connector_id,
                    "error": "Failed to generate schema"
                }
            }

    async def get_current_config(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取连接器当前配置"""
        try:
            with self.db_service.get_session() as session:
                connector = session.query(Connector).filter_by(
                    connector_id=connector_id
                ).first()
                
                if not connector:
                    logger.warning(f"连接器不存在: {connector_id}")
                    return None
                
                # 返回配置数据，如果为空则返回空字典
                config_data = connector.config_data or {}
                logger.debug(f"获取当前配置成功: {connector_id}")
                return config_data
                
        except Exception as e:
            logger.error(f"获取当前配置失败 {connector_id}: {e}")
            return None

    async def validate_config(self, connector_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证配置数据"""
        try:
            # 获取schema进行验证
            schema_data = await self.get_config_schema(connector_id)
            
            if not schema_data:
                return {
                    "valid": False,
                    "errors": [{"message": "无法获取配置schema"}]
                }
            
            json_schema = schema_data.get("json_schema", {})
            
            # 基础验证：检查必需字段
            errors = []
            required_fields = json_schema.get("required", [])
            
            for field in required_fields:
                if field not in config:
                    errors.append({
                        "field": field,
                        "message": f"必需字段 '{field}' 缺失"
                    })
            
            # 类型验证
            properties = json_schema.get("properties", {})
            for field_name, field_value in config.items():
                if field_name in properties:
                    field_schema = properties[field_name]
                    field_type = field_schema.get("type", "string")
                    
                    if not self._validate_field_type(field_value, field_type):
                        errors.append({
                            "field": field_name,
                            "message": f"字段 '{field_name}' 类型错误，期望 {field_type}"
                        })
            
            is_valid = len(errors) == 0
            
            logger.debug(f"配置验证完成: {connector_id}, valid={is_valid}")
            
            return {
                "valid": is_valid,
                "errors": errors,
                "warnings": []  # 可以添加警告信息
            }
            
        except Exception as e:
            logger.error(f"配置验证失败 {connector_id}: {e}")
            return {
                "valid": False,
                "errors": [{"message": f"验证过程出错: {str(e)}"}]
            }

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
        change_reason: str = "用户更新"
    ) -> Dict[str, Any]:
        """更新连接器配置"""
        try:
            # 首先验证配置
            validation_result = await self.validate_config(connector_id, config)
            
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": "配置验证失败",
                    "validation_errors": validation_result["errors"]
                }
            
            with self.db_service.get_session() as session:
                # 获取连接器
                connector = session.query(Connector).filter_by(
                    connector_id=connector_id
                ).first()
                
                if not connector:
                    return {
                        "success": False,
                        "error": f"连接器不存在: {connector_id}"
                    }
                
                # 保存旧配置到历史记录
                old_config = connector.config_data or {}
                
                if old_config != config:
                    self._save_config_history(
                        session=session,
                        connector_id=connector_id,
                        old_config=old_config,
                        new_config=config,
                        config_version=config_version,
                        change_reason=change_reason
                    )
                
                # 更新连接器配置
                connector.config_data = config
                connector.updated_at = datetime.now(timezone.utc)
                session.commit()
                
                logger.info(f"配置更新成功: {connector_id}")
                
                return {
                    "success": True,
                    "message": "配置更新成功",
                    "config_version": config_version
                }
                
        except Exception as e:
            logger.error(f"更新配置失败 {connector_id}: {e}")
            return {
                "success": False,
                "error": f"更新配置时出错: {str(e)}"
            }

    def _save_config_history(
        self, 
        session, 
        connector_id: str, 
        old_config: Dict[str, Any],
        new_config: Dict[str, Any],
        config_version: str,
        change_reason: str
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
                validation_status="valid"
            )
            
            session.add(history_record)
            logger.debug(f"配置历史记录已保存: {connector_id}")
            
        except Exception as e:
            logger.warning(f"保存配置历史失败 {connector_id}: {e}")

    async def reset_config(self, connector_id: str, to_defaults: bool = True) -> Dict[str, Any]:
        """重置连接器配置"""
        try:
            with self.db_service.get_session() as session:
                connector = session.query(Connector).filter_by(
                    connector_id=connector_id
                ).first()
                
                if not connector:
                    return {
                        "success": False,
                        "error": f"连接器不存在: {connector_id}"
                    }
                
                # 保存旧配置到历史记录
                old_config = connector.config_data or {}
                
                if to_defaults:
                    # 重置为默认配置
                    schema_data = await self.get_config_schema(connector_id)
                    default_config = self._extract_default_config(schema_data)
                else:
                    # 重置为空配置
                    default_config = {}
                
                # 保存历史记录
                if old_config != default_config:
                    self._save_config_history(
                        session=session,
                        connector_id=connector_id,
                        old_config=old_config,
                        new_config=default_config,
                        config_version="1.0.0",
                        change_reason="重置配置"
                    )
                
                # 更新连接器配置
                connector.config_data = default_config
                connector.updated_at = datetime.now(timezone.utc)
                session.commit()
                
                logger.info(f"配置重置成功: {connector_id}")
                
                return {
                    "success": True,
                    "message": "配置重置成功",
                    "config": default_config
                }
                
        except Exception as e:
            logger.error(f"重置配置失败 {connector_id}: {e}")
            return {
                "success": False,
                "error": f"重置配置时出错: {str(e)}"
            }

    def _extract_default_config(self, schema_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """从schema中提取默认配置"""
        if not schema_data:
            return {}
        
        json_schema = schema_data.get("json_schema", {})
        properties = json_schema.get("properties", {})
        
        default_config = {}
        for field_name, field_schema in properties.items():
            if "default" in field_schema:
                default_config[field_name] = field_schema["default"]
        
        return default_config

    async def get_config_history(
        self, 
        connector_id: str, 
        limit: int = 10, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """获取配置变更历史"""
        try:
            with self.db_service.get_session() as session:
                # 查询历史记录
                history_query = session.query(ConnectorConfigHistory).filter_by(
                    connector_id=connector_id
                ).order_by(ConnectorConfigHistory.created_at.desc())
                
                total_count = history_query.count()
                history_records = history_query.offset(offset).limit(limit).all()
                
                # 转换为字典格式
                history_data = []
                for record in history_records:
                    history_data.append({
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
                        "created_at": record.created_at.isoformat() if record.created_at else None
                    })
                
                logger.debug(f"获取配置历史成功: {connector_id}, {len(history_data)} 条记录")
                
                return {
                    "history": history_data,
                    "total": total_count,
                    "limit": limit,
                    "offset": offset
                }
                
        except Exception as e:
            logger.error(f"获取配置历史失败 {connector_id}: {e}")
            return {
                "history": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "error": str(e)
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
                            "schema_version": schema_data.get("metadata", {}).get("schema_version", "1.0.0"),
                            "has_custom_schema": not schema_data.get("metadata", {}).get("generated", False),
                            "field_count": len(schema_data.get("json_schema", {}).get("properties", {}))
                        }
                
                logger.debug(f"获取所有schema成功，共 {len(schemas)} 个连接器")
                
                return {
                    "schemas": schemas,
                    "total": len(schemas)
                }
                
        except Exception as e:
            logger.error(f"获取所有schema失败: {e}")
            return {
                "schemas": {},
                "total": 0,
                "error": str(e)
            }


# 全局服务实例获取函数
def get_connector_config_service(connectors_dir: Optional[Path] = None) -> ConnectorConfigService:
    """获取连接器配置服务实例"""
    return ConnectorConfigService(connectors_dir)