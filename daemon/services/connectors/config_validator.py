#!/usr/bin/env python3
"""
连接器配置验证器
专门负责配置数据的验证逻辑
从connector_config_service.py中拆分出来
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ConfigValidator:
    """配置验证器"""

    def __init__(self, schema_manager):
        self.schema_manager = schema_manager

    async def validate_config(
        self, connector_id: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """验证配置数据"""
        try:
            schema_data = await self.schema_manager.get_config_schema(connector_id)

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

            # 值域验证
            validation_errors = self._validate_field_constraints(config, properties)
            errors.extend(validation_errors)

            is_valid = len(errors) == 0

            logger.debug(f"配置验证完成: {connector_id}, valid={is_valid}")

            return {
                "valid": is_valid,
                "errors": errors,
                "warnings": [],
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

    def _validate_field_constraints(
        self, config: Dict[str, Any], properties: Dict[str, Any]
    ) -> list:
        """验证字段约束"""
        errors = []

        for field_name, field_value in config.items():
            if field_name not in properties:
                continue

            field_schema = properties[field_name]

            # 检查枚举值
            if "enum" in field_schema:
                if field_value not in field_schema["enum"]:
                    errors.append(
                        {
                            "field": field_name,
                            "message": f"字段 '{field_name}' 的值不在允许范围内: {field_schema['enum']}",
                        }
                    )

            # 检查字符串长度
            if field_schema.get("type") == "string":
                if "minLength" in field_schema and len(field_value) < field_schema["minLength"]:
                    errors.append(
                        {
                            "field": field_name,
                            "message": f"字段 '{field_name}' 长度不能小于 {field_schema['minLength']}",
                        }
                    )

                if "maxLength" in field_schema and len(field_value) > field_schema["maxLength"]:
                    errors.append(
                        {
                            "field": field_name,
                            "message": f"字段 '{field_name}' 长度不能大于 {field_schema['maxLength']}",
                        }
                    )

            # 检查数字范围
            if field_schema.get("type") in ["integer", "number"]:
                if "minimum" in field_schema and field_value < field_schema["minimum"]:
                    errors.append(
                        {
                            "field": field_name,
                            "message": f"字段 '{field_name}' 不能小于 {field_schema['minimum']}",
                        }
                    )

                if "maximum" in field_schema and field_value > field_schema["maximum"]:
                    errors.append(
                        {
                            "field": field_name,
                            "message": f"字段 '{field_name}' 不能大于 {field_schema['maximum']}",
                        }
                    )

            # 检查正则表达式
            if "pattern" in field_schema and isinstance(field_value, str):
                import re
                try:
                    if not re.match(field_schema["pattern"], field_value):
                        errors.append(
                            {
                                "field": field_name,
                                "message": f"字段 '{field_name}' 格式不正确",
                            }
                        )
                except re.error:
                    # 正则表达式错误，跳过验证
                    pass

        return errors