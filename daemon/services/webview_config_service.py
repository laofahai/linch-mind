#!/usr/bin/env python3
"""
WebView配置服务 - 为复杂连接器提供HTML配置界面
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import jinja2

from config.core_config import CoreConfigManager
from services.connectors.connector_config_service import ConnectorConfigService

logger = logging.getLogger(__name__)


class WebViewConfigService:
    """WebView配置服务"""

    def __init__(self, config_manager: CoreConfigManager):
        self.config_manager = config_manager
        self.connector_config_service = ConnectorConfigService()
        self.template_dirs = [
            Path(__file__).parent.parent / "templates" / "connector_config",
            Path(__file__).parent.parent.parent / "connectors" / "templates",
        ]
        self._setup_template_environment()

    def _setup_template_environment(self):
        """设置模板环境"""
        # 创建模板目录
        for template_dir in self.template_dirs:
            template_dir.mkdir(parents=True, exist_ok=True)

        # 设置Jinja2环境
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader([str(d) for d in self.template_dirs]),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # 注册自定义过滤器
        self._register_custom_filters()

    def _register_custom_filters(self):
        """注册自定义Jinja2过滤器"""

        def json_encode_filter(obj):
            return json.dumps(obj, ensure_ascii=False, indent=2)

        def field_type_to_input(field_type, field_schema):
            """将JSON Schema字段类型转换为HTML输入类型"""
            type_mapping = {
                "string": "text",
                "number": "number",
                "integer": "number",
                "boolean": "checkbox",
                "password": "password",
            }

            # 检查特殊格式
            if field_type == "string":
                field_format = field_schema.get("format", "")
                if field_format == "password":
                    return "password"
                elif field_format == "email":
                    return "email"
                elif field_format == "url":
                    return "url"
                elif field_format == "textarea":
                    return "textarea"
                elif field_schema.get("enum"):
                    return "select"

            return type_mapping.get(field_type, "text")

        def get_field_validation(field_name, field_schema, required_fields):
            """获取字段验证属性"""
            validation = {}

            if field_name in required_fields:
                validation["required"] = True

            if field_schema.get("minLength"):
                validation["minlength"] = field_schema["minLength"]
            if field_schema.get("maxLength"):
                validation["maxlength"] = field_schema["maxLength"]
            if field_schema.get("minimum"):
                validation["min"] = field_schema["minimum"]
            if field_schema.get("maximum"):
                validation["max"] = field_schema["maximum"]
            if field_schema.get("pattern"):
                validation["pattern"] = field_schema["pattern"]

            return validation

        # 注册过滤器到Jinja环境
        self.jinja_env.filters["json_encode"] = json_encode_filter
        self.jinja_env.filters["field_type_to_input"] = field_type_to_input
        self.jinja_env.filters["get_field_validation"] = get_field_validation

    async def generate_webview_html(
        self,
        connector_id: str,
        config_schema: Dict[str, Any],
        ui_schema: Dict[str, Any],
        current_config: Dict[str, Any],
        template_name: Optional[str] = None,
    ) -> str:
        """生成WebView配置HTML"""
        try:
            # 确定使用的模板
            if template_name:
                template_file = f"{template_name}.html"
            else:
                # 尝试查找连接器特定模板
                connector_template = f"{connector_id}_config.html"
                if self._template_exists(connector_template):
                    template_file = connector_template
                else:
                    template_file = "default_config.html"

            logger.info(f"为连接器 {connector_id} 使用模板: {template_file}")

            # 获取模板
            template = self.jinja_env.get_template(template_file)

            # 准备模板变量
            template_vars = {
                "connector_id": connector_id,
                "connector_name": self._get_connector_display_name(connector_id),
                "config_schema": config_schema,
                "ui_schema": ui_schema,
                "current_config": current_config,
                "properties": config_schema.get("properties", {}),
                "required_fields": config_schema.get("required", []),
                "sections": ui_schema.get("ui:sections", {}),
                "form_title": ui_schema.get("ui:title", f"{connector_id} 配置"),
                "form_description": ui_schema.get("ui:description", "配置连接器参数"),
                "timestamp": datetime.now().isoformat(),
                "debug_mode": os.environ.get("DEBUG", "").lower() == "true",
            }

            # 渲染模板
            html_content = template.render(**template_vars)

            logger.info(f"成功生成WebView HTML，长度: {len(html_content)} 字符")
            return html_content

        except jinja2.TemplateNotFound as e:
            logger.error(f"模板文件不存在: {e}")
            return self._generate_fallback_html(
                connector_id, config_schema, current_config
            )
        except Exception as e:
            logger.error(f"生成WebView HTML失败: {e}")
            return self._generate_error_html(str(e))

    def _template_exists(self, template_name: str) -> bool:
        """检查模板是否存在"""
        try:
            self.jinja_env.get_template(template_name)
            return True
        except jinja2.TemplateNotFound:
            return False

    def _get_connector_display_name(self, connector_id: str) -> str:
        """获取连接器显示名称"""
        # 可以从配置或连接器注册信息中获取
        display_names = {
            "filesystem": "文件系统连接器",
            "clipboard": "剪贴板连接器",
            "browser": "浏览器连接器",
            "email": "邮件连接器",
        }
        return display_names.get(connector_id, connector_id.title())

    def _generate_fallback_html(
        self,
        connector_id: str,
        config_schema: Dict[str, Any],
        current_config: Dict[str, Any],
    ) -> str:
        """生成后备HTML（当模板不存在时）"""
        properties = config_schema.get("properties", {})
        required_fields = config_schema.get("required", [])

        html_parts = [
            "<!DOCTYPE html>",
            '<html lang="zh-CN">',
            "<head>",
            '    <meta charset="UTF-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f"    <title>{connector_id} 配置</title>",
            "    <style>",
            self._get_default_css(),
            "    </style>",
            "</head>",
            "<body>",
            '    <div class="container">',
            '        <div class="header">',
            f"            <h1>{self._get_connector_display_name(connector_id)}</h1>",
            "            <p>配置连接器参数</p>",
            "        </div>",
            '        <form id="config-form" class="config-form">',
        ]

        # 生成表单字段
        for field_name, field_schema in properties.items():
            field_type = field_schema.get("type", "string")
            field_title = field_schema.get("title", field_name)
            field_description = field_schema.get("description", "")
            current_value = current_config.get(field_name, "")
            is_required = field_name in required_fields

            html_parts.extend(
                [
                    '            <div class="form-group">',
                    f'                <label for="{field_name}" class="form-label">',
                    f"                    {field_title}",
                    "                    "
                    + ('<span class="required">*</span>' if is_required else ""),
                    "                </label>",
                ]
            )

            # 根据类型生成输入控件
            if field_type == "boolean":
                checked = "checked" if current_value else ""
                html_parts.extend(
                    [
                        f'                <div class="checkbox-group">',
                        f'                    <input type="checkbox" id="{field_name}" name="{field_name}" {checked}>',
                        f'                    <label for="{field_name}">启用</label>',
                        f"                </div>",
                    ]
                )
            elif field_schema.get("enum"):
                html_parts.append(
                    f'                <select id="{field_name}" name="{field_name}" class="form-input">'
                )
                for option in field_schema["enum"]:
                    selected = "selected" if str(current_value) == str(option) else ""
                    html_parts.append(
                        f'                    <option value="{option}" {selected}>{option}</option>'
                    )
                html_parts.append("                </select>")
            else:
                input_type = "text"
                if field_type in ["number", "integer"]:
                    input_type = "number"
                elif field_schema.get("format") == "password":
                    input_type = "password"

                html_parts.append(
                    f'                <input type="{input_type}" id="{field_name}" '
                    f'name="{field_name}" class="form-input" value="{current_value}" '
                    f'{"required" if is_required else ""}>'
                )

            if field_description:
                html_parts.append(
                    f'                <div class="form-description">{field_description}</div>'
                )

            html_parts.append("            </div>")

        html_parts.extend(
            [
                "        </form>",
                '        <div class="actions">',
                '            <button type="button" onclick="resetForm()" class="btn btn-secondary">重置</button>',
                '            <button type="button" onclick="saveConfig()" class="btn btn-primary">保存配置</button>',
                "        </div>",
                "    </div>",
                "    <script>",
                self._get_default_javascript(config_schema, current_config),
                "    </script>",
                "</body>",
                "</html>",
            ]
        )

        return "\n".join(html_parts)

    def _generate_error_html(self, error_message: str) -> str:
        """生成错误页面HTML"""
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>配置加载错误</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: #f5f5f5;
            padding: 40px;
            text-align: center;
        }}
        .error {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            max-width: 500px;
            margin: 0 auto;
        }}
        .error h1 {{ color: #d73527; margin-bottom: 16px; }}
        .error p {{ color: #666; line-height: 1.5; }}
    </style>
</head>
<body>
    <div class="error">
        <h1>配置加载失败</h1>
        <p>{error_message}</p>
        <p>请联系管理员或检查连接器配置。</p>
    </div>
</body>
</html>
        """

    def _get_default_css(self) -> str:
        """获取默认CSS样式"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #fafafa;
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 24px;
        }

        .header h1 {
            font-size: 24px;
            margin-bottom: 8px;
        }

        .config-form {
            padding: 24px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }

        .required {
            color: #dc3545;
        }

        .form-input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.2s;
        }

        .form-input:focus {
            outline: none;
            border-color: #667eea;
        }

        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .form-description {
            font-size: 12px;
            color: #666;
            margin-top: 4px;
        }

        .actions {
            display: flex;
            gap: 12px;
            justify-content: flex-end;
            padding: 24px;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
        }

        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        """

    def _get_default_javascript(
        self, config_schema: Dict[str, Any], current_config: Dict[str, Any]
    ) -> str:
        """获取默认JavaScript代码"""
        return f"""
        const configSchema = {json.dumps(config_schema, ensure_ascii=False)};
        const initialConfig = {json.dumps(current_config, ensure_ascii=False)};

        function getFormData() {{
            const formData = {{}};
            const form = document.getElementById('config-form');
            const inputs = form.querySelectorAll('input, select, textarea');

            inputs.forEach(input => {{
                if (input.type === 'checkbox') {{
                    formData[input.name] = input.checked;
                }} else if (input.type === 'number') {{
                    formData[input.name] = input.value ? Number(input.value) : null;
                }} else {{
                    formData[input.name] = input.value;
                }}
            }});

            return formData;
        }}

        function resetForm() {{
            if (confirm('确定要重置为初始值吗？')) {{
                const form = document.getElementById('config-form');
                const inputs = form.querySelectorAll('input, select, textarea');

                inputs.forEach(input => {{
                    const fieldName = input.name;
                    const initialValue = initialConfig[fieldName];

                    if (input.type === 'checkbox') {{
                        input.checked = initialValue === true;
                    }} else {{
                        input.value = initialValue || '';
                    }}
                }});
            }}
        }}

        function saveConfig() {{
            const formData = getFormData();

            // 发送到Flutter
            if (window.FlutterConfigBridge) {{
                const message = JSON.stringify({{
                    action: 'saveConfig',
                    data: formData,
                    timestamp: Date.now()
                }});
                window.FlutterConfigBridge.postMessage(message);
            }}
        }}

        // 监听表单变化
        document.addEventListener('DOMContentLoaded', function() {{
            const form = document.getElementById('config-form');
            const inputs = form.querySelectorAll('input, select, textarea');

            inputs.forEach(input => {{
                input.addEventListener('change', function() {{
                    const formData = getFormData();

                    // 通知Flutter配置变化
                    if (window.FlutterConfigBridge) {{
                        const message = JSON.stringify({{
                            action: 'configChanged',
                            data: formData,
                            timestamp: Date.now()
                        }});
                        window.FlutterConfigBridge.postMessage(message);
                    }}
                }});
            }});
        }});
        """

    async def save_custom_template(
        self,
        connector_id: str,
        template_content: str,
        template_name: Optional[str] = None,
    ) -> bool:
        """保存自定义模板"""
        try:
            template_file = template_name or f"{connector_id}_config.html"
            template_path = self.template_dirs[0] / template_file

            # 确保目录存在
            template_path.parent.mkdir(parents=True, exist_ok=True)

            # 写入模板内容
            with open(template_path, "w", encoding="utf-8") as f:
                f.write(template_content)

            logger.info(f"保存自定义模板: {template_path}")
            return True

        except Exception as e:
            logger.error(f"保存自定义模板失败: {e}")
            return False

    async def get_available_templates(self) -> List[Dict[str, Any]]:
        """获取可用模板列表"""
        templates = []

        try:
            for template_dir in self.template_dirs:
                if template_dir.exists():
                    for template_file in template_dir.glob("*.html"):
                        template_info = {
                            "name": template_file.stem,
                            "filename": template_file.name,
                            "path": str(template_file),
                            "size": template_file.stat().st_size,
                            "modified": datetime.fromtimestamp(
                                template_file.stat().st_mtime
                            ).isoformat(),
                        }
                        templates.append(template_info)

        except Exception as e:
            logger.error(f"获取模板列表失败: {e}")

        return templates

    def validate_template(self, template_content: str) -> Dict[str, Any]:
        """验证模板内容"""
        try:
            # 尝试解析模板
            template = jinja2.Template(template_content)

            # 基本渲染测试
            test_vars = {
                "connector_id": "test",
                "connector_name": "Test Connector",
                "config_schema": {"properties": {}},
                "ui_schema": {},
                "current_config": {},
            }

            template.render(**test_vars)

            return {
                "valid": True,
                "message": "模板验证通过",
            }

        except jinja2.TemplateSyntaxError as e:
            return {
                "valid": False,
                "error_type": "syntax_error",
                "message": f"模板语法错误: {e}",
                "line_number": e.lineno,
            }
        except Exception as e:
            return {
                "valid": False,
                "error_type": "render_error",
                "message": f"模板渲染错误: {e}",
            }
