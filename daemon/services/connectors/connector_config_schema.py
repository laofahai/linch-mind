#!/usr/bin/env python3
"""
连接器配置Schema规范定义
基于JSON Schema + UI Schema的配置系统
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ConfigFieldType(str, Enum):
    """配置字段类型枚举"""

    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    PATH = "path"  # 文件/目录路径
    EMAIL = "email"
    URL = "url"
    DATETIME = "datetime"
    SELECT = "select"  # 单选下拉
    MULTISELECT = "multiselect"  # 多选


class ConfigUIWidget(str, Enum):
    """UI组件类型枚举"""

    # 基础组件
    TEXT_INPUT = "text_input"
    TEXT_AREA = "text_area"
    NUMBER_INPUT = "number_input"
    SWITCH = "switch"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    SELECT = "select"
    MULTISELECT = "multiselect"
    FILE_PICKER = "file_picker"
    DIRECTORY_PICKER = "directory_picker"
    COLOR_PICKER = "color_picker"
    SLIDER = "slider"
    DATE_PICKER = "date_picker"
    TIME_PICKER = "time_picker"
    TAGS_INPUT = "tags_input"
    JSON_EDITOR = "json_editor"
    KEY_VALUE_EDITOR = "key_value_editor"

    # 通用复杂组件
    DYNAMIC_LIST = "dynamic_list"  # 动态列表编辑器
    CONDITIONAL_SECTION = "conditional_section"  # 条件显示区域
    TABBED_SECTION = "tabbed_section"  # 标签页区域
    COLLAPSIBLE_SECTION = "collapsible_section"  # 可折叠区域
    NESTED_OBJECT = "nested_object"  # 嵌套对象编辑器

    # 高级自定义组件
    CUSTOM_WIDGET = "custom_widget"  # 自定义组件
    IFRAME_WIDGET = "iframe_widget"  # 内嵌网页组件
    DYNAMIC_FORM = "dynamic_form"  # 动态表单
    TREE_SELECT = "tree_select"  # 树形选择器
    CRON_EDITOR = "cron_editor"  # Cron表达式编辑器
    CODE_EDITOR = "code_editor"  # 代码编辑器
    MARKDOWN_EDITOR = "markdown_editor"  # Markdown编辑器
    CHART_CONFIG = "chart_config"  # 图表配置器
    API_ENDPOINT_BUILDER = "api_endpoint_builder"  # API端点构建器
    SQL_QUERY_BUILDER = "sql_query_builder"  # SQL查询构建器


class ConfigValidationRule(BaseModel):
    """配置验证规则"""

    rule_type: str  # required, min_length, max_length, pattern, custom
    value: Any = None
    message: Optional[str] = None


class ConfigFieldSchema(BaseModel):
    """配置字段Schema定义"""

    # 基本属性
    type: ConfigFieldType
    title: str
    description: Optional[str] = None
    default: Any = None

    # UI属性
    widget: Optional[ConfigUIWidget] = None
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    order: int = 0  # 字段显示顺序

    # 验证规则
    required: bool = False
    validation_rules: List[ConfigValidationRule] = Field(default_factory=list)

    # 条件显示
    depends_on: Optional[str] = None  # 依赖其他字段
    show_when: Optional[Dict[str, Any]] = None  # 显示条件

    # 选择类型特有属性
    options: Optional[List[Dict[str, Any]]] = None  # 选项列表
    multiple: bool = False  # 是否多选

    # 数值类型特有属性
    minimum: Optional[Union[int, float]] = None
    maximum: Optional[Union[int, float]] = None
    step: Optional[Union[int, float]] = None

    # 字符串类型特有属性
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None  # 正则表达式

    # 数组类型特有属性
    items: Optional["ConfigFieldSchema"] = None
    min_items: Optional[int] = None
    max_items: Optional[int] = None

    # 自定义组件配置
    custom_widget_config: Optional[Dict[str, Any]] = None  # 自定义组件配置
    custom_component_name: Optional[str] = None  # 自定义Flutter组件名称
    custom_validation_endpoint: Optional[str] = None  # 自定义验证端点
    iframe_src: Optional[str] = None  # iframe源地址
    code_language: Optional[str] = None  # 代码语言(用于代码编辑器)


class ConfigSectionSchema(BaseModel):
    """配置分组Schema"""

    id: str
    title: str
    description: Optional[str] = None
    icon: Optional[str] = None
    order: int = 0
    collapsible: bool = True
    collapsed: bool = False
    fields: Dict[str, ConfigFieldSchema]


class ConnectorConfigSchema(BaseModel):
    """连接器配置Schema完整定义"""

    # 基本信息
    schema_version: str = "1.0.0"
    connector_id: str
    connector_name: str

    # Schema定义
    sections: Dict[str, ConfigSectionSchema] = Field(default_factory=dict)

    # 全局设置
    supports_hot_reload: bool = True
    requires_restart_fields: List[str] = Field(default_factory=list)

    # 预设配置模板
    presets: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

    def to_json_schema(self) -> Dict[str, Any]:
        """转换为标准JSON Schema格式"""
        properties = {}
        required_fields = []

        for section in self.sections.values():
            for field_name, field_schema in section.fields.items():
                properties[field_name] = self._field_to_json_schema(field_schema)
                if field_schema.required:
                    required_fields.append(field_name)

        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": properties,
            "required": required_fields,
            "additionalProperties": False,
        }

    def to_ui_schema(self) -> Dict[str, Any]:
        """生成UI Schema用于前端渲染"""
        ui_schema = {"ui:order": [], "ui:sections": {}}

        # 按section组织UI
        for section_id, section in sorted(
            self.sections.items(), key=lambda x: x[1].order
        ):
            ui_schema["ui:sections"][section_id] = {
                "ui:title": section.title,
                "ui:description": section.description,
                "ui:icon": section.icon,
                "ui:collapsible": section.collapsible,
                "ui:collapsed": section.collapsed,
                "ui:fields": {},
            }

            # 字段UI配置
            for field_name, field_schema in sorted(
                section.fields.items(), key=lambda x: x[1].order
            ):
                field_ui = {
                    "ui:widget": (
                        field_schema.widget.value if field_schema.widget else None
                    ),
                    "ui:placeholder": field_schema.placeholder,
                    "ui:help": field_schema.help_text,
                    "ui:order": field_schema.order,
                }

                if field_schema.depends_on:
                    field_ui["ui:depends_on"] = field_schema.depends_on
                    field_ui["ui:show_when"] = field_schema.show_when

                if field_schema.options:
                    field_ui["ui:options"] = field_schema.options

                ui_schema["ui:sections"][section_id]["ui:fields"][field_name] = field_ui

        return ui_schema

    def _field_to_json_schema(self, field: ConfigFieldSchema) -> Dict[str, Any]:
        """将字段schema转换为JSON Schema格式"""
        json_field = {
            "type": field.type.value,
            "title": field.title,
            "description": field.description,
        }

        if field.default is not None:
            json_field["default"] = field.default

        # 数值范围
        if field.minimum is not None:
            json_field["minimum"] = field.minimum
        if field.maximum is not None:
            json_field["maximum"] = field.maximum

        # 字符串长度和模式
        if field.min_length is not None:
            json_field["minLength"] = field.min_length
        if field.max_length is not None:
            json_field["maxLength"] = field.max_length
        if field.pattern:
            json_field["pattern"] = field.pattern

        # 数组配置
        if field.type == ConfigFieldType.ARRAY:
            if field.items:
                json_field["items"] = self._field_to_json_schema(field.items)
            if field.min_items is not None:
                json_field["minItems"] = field.min_items
            if field.max_items is not None:
                json_field["maxItems"] = field.max_items

        # 选项枚举
        if field.options:
            json_field["enum"] = [opt["value"] for opt in field.options]

        return json_field


# 预定义的常用字段Schema模板
# 注意：enabled, auto_start, log_level 不再作为连接器配置项
# 这些应该在UI层面处理（连接器列表的启用/禁用控制）
COMMON_FIELD_TEMPLATES = {
    "polling_interval": ConfigFieldSchema(
        type=ConfigFieldType.INTEGER,
        title="轮询间隔(秒)",
        description="数据检查的时间间隔",
        default=30,
        minimum=1,
        maximum=3600,
        widget=ConfigUIWidget.SLIDER,
        order=20,
    ),
    "watch_paths": ConfigFieldSchema(
        type=ConfigFieldType.ARRAY,
        title="监控路径",
        description="要监控的文件或目录路径列表",
        widget=ConfigUIWidget.TAGS_INPUT,
        items=ConfigFieldSchema(
            type=ConfigFieldType.PATH,
            title="路径",
            widget=ConfigUIWidget.DIRECTORY_PICKER,
        ),
        min_items=1,
        order=30,
    ),
}


def create_basic_config_schema(
    connector_id: str, connector_name: str
) -> ConnectorConfigSchema:
    """创建基础配置Schema模板

    注意：不再包含enabled, auto_start, log_level等通用字段
    这些应该在UI层面处理，不属于连接器特定的配置
    """
    return ConnectorConfigSchema(
        connector_id=connector_id,
        connector_name=connector_name,
        sections={
            "basic": ConfigSectionSchema(
                id="basic",
                title="基本设置",
                description="连接器的基本配置选项",
                icon="settings",
                order=0,
                fields={
                    # 基础模板现在为空，由具体连接器定义自己的配置项
                },
            )
        },
    )
