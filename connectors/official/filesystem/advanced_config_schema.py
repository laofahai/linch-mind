#!/usr/bin/env python3
"""
文件系统连接器高级配置Schema示例
展示如何使用新的配置系统支持复杂UI组件
"""

from daemon.services.connectors.connector_config_schema import (
    ConnectorConfigSchema,
    ConfigSectionSchema,
    ConfigFieldSchema,
    ConfigFieldType,
    ConfigUIWidget,
    ConfigValidationRule
)

def create_filesystem_advanced_schema() -> ConnectorConfigSchema:
    """创建文件系统连接器的高级配置Schema"""
    
    return ConnectorConfigSchema(
        connector_id="filesystem",
        connector_name="文件系统连接器",
        schema_version="2.0.0",
        supports_hot_reload=True,
        requires_restart_fields=["watch_paths", "file_indexing_mode"],
        
        sections={
            # 基本设置section
            "basic": ConfigSectionSchema(
                id="basic",
                title="基本设置",
                description="连接器的基础配置选项",
                icon="folder",
                order=0,
                fields={
                    "enabled": ConfigFieldSchema(
                        type=ConfigFieldType.BOOLEAN,
                        title="启用连接器",
                        description="是否启用文件系统监控",
                        default=True,
                        widget=ConfigUIWidget.SWITCH,
                        order=0
                    ),
                    "auto_start": ConfigFieldSchema(
                        type=ConfigFieldType.BOOLEAN,
                        title="自动启动",
                        description="系统启动时自动启动此连接器",
                        default=True,
                        widget=ConfigUIWidget.SWITCH,
                        order=1
                    ),
                    "log_level": ConfigFieldSchema(
                        type=ConfigFieldType.SELECT,
                        title="日志级别",
                        description="设置连接器的日志详细程度",
                        default="INFO",
                        widget=ConfigUIWidget.SELECT,
                        options=[
                            {"label": "TRACE", "value": "TRACE"},
                            {"label": "DEBUG", "value": "DEBUG"},
                            {"label": "INFO", "value": "INFO"},
                            {"label": "WARN", "value": "WARN"},
                            {"label": "ERROR", "value": "ERROR"}
                        ],
                        order=2
                    )
                }
            ),
            
            # 监控设置section
            "monitoring": ConfigSectionSchema(
                id="monitoring",
                title="监控设置",
                description="文件系统监控的详细配置",
                icon="visibility",
                order=1,
                fields={
                    "watch_paths": ConfigFieldSchema(
                        type=ConfigFieldType.ARRAY,
                        title="监控路径",
                        description="要监控的文件或目录路径列表",
                        widget=ConfigUIWidget.TAGS_INPUT,
                        items=ConfigFieldSchema(
                            type=ConfigFieldType.PATH,
                            widget=ConfigUIWidget.DIRECTORY_PICKER
                        ),
                        default=["~/Downloads", "~/Documents"],
                        min_items=1,
                        order=0,
                        help_text="点击添加按钮选择要监控的目录"
                    ),
                    "supported_extensions": ConfigFieldSchema(
                        type=ConfigFieldType.ARRAY,
                        title="支持的文件类型",
                        description="监控的文件扩展名",
                        widget=ConfigUIWidget.TAGS_INPUT,
                        items=ConfigFieldSchema(type=ConfigFieldType.STRING),
                        default=[".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".yaml"],
                        order=1,
                        help_text="输入文件扩展名，如 .txt, .py"
                    ),
                    "polling_interval": ConfigFieldSchema(
                        type=ConfigFieldType.INTEGER,
                        title="轮询间隔(秒)",
                        description="文件变化检查的时间间隔",
                        default=30,
                        minimum=5,
                        maximum=3600,
                        widget=ConfigUIWidget.SLIDER,
                        order=2
                    ),
                    "max_file_size": ConfigFieldSchema(
                        type=ConfigFieldType.INTEGER,
                        title="最大文件大小 (MB)",
                        description="超过此大小的文件将被忽略",
                        default=10,
                        minimum=1,
                        maximum=100,
                        widget=ConfigUIWidget.NUMBER_INPUT,
                        order=3
                    )
                }
            ),
            
            # 过滤规则section - 使用自定义组件
            "filtering": ConfigSectionSchema(
                id="filtering",
                title="过滤规则",
                description="文件过滤和忽略规则配置",
                icon="filter_list",
                order=2,
                fields={
                    "ignore_patterns": ConfigFieldSchema(
                        type=ConfigFieldType.ARRAY,
                        title="忽略模式",
                        description="忽略的文件模式",
                        widget=ConfigUIWidget.TAGS_INPUT,
                        items=ConfigFieldSchema(type=ConfigFieldType.STRING),
                        default=["*.tmp", ".*", "node_modules/*", "__pycache__/*", "*.log", ".git/*"],
                        order=0
                    ),
                    "custom_filter_rules": ConfigFieldSchema(
                        type=ConfigFieldType.OBJECT,
                        title="自定义过滤规则",
                        description="高级过滤规则配置",
                        widget=ConfigUIWidget.CUSTOM_WIDGET,
                        custom_component_name="FileFilterRulesEditor",
                        custom_widget_config={
                            "type": "filter_rules_editor",
                            "version": "1.0.0",
                            "template_path": "filter_rules_editor",
                            "validation": {
                                "required_fields": ["rules"],
                                "custom_validator": {
                                    "type": "script",
                                    "script_path": "validate_filter_rules.py"
                                }
                            },
                            "actions": {
                                "test_rules": {
                                    "type": "http",
                                    "method": "POST",
                                    "endpoint": "/api/v1/connectors/filesystem/test-filter-rules",
                                    "description": "测试过滤规则"
                                },
                                "import_rules": {
                                    "type": "file_upload",
                                    "accept": ".json,.yaml",
                                    "description": "导入规则文件"
                                }
                            }
                        },
                        default={
                            "rules": [],
                            "operator": "AND"
                        },
                        order=1
                    )
                }
            ),
            
            # 内容处理section
            "content_processing": ConfigSectionSchema(
                id="content_processing",
                title="内容处理",
                description="文件内容提取和处理配置",
                icon="transform",
                order=3,
                fields={
                    "max_content_length": ConfigFieldSchema(
                        type=ConfigFieldType.INTEGER,
                        title="最大内容长度",
                        description="文件内容截断长度（字符数）",
                        default=50000,
                        minimum=1000,
                        maximum=1000000,
                        widget=ConfigUIWidget.NUMBER_INPUT,
                        order=0
                    ),
                    "content_extraction_rules": ConfigFieldSchema(
                        type=ConfigFieldType.OBJECT,
                        title="内容提取规则",
                        description="针对不同文件类型的内容提取配置",
                        widget=ConfigUIWidget.DYNAMIC_FORM,
                        custom_widget_config={
                            "type": "dynamic_form",
                            "schema": {
                                "fields": {
                                    "text_files": {
                                        "type": "object",
                                        "title": "文本文件处理",
                                        "widget": "json_editor",
                                        "properties": {
                                            "encoding": {"type": "string", "default": "utf-8"},
                                            "remove_empty_lines": {"type": "boolean", "default": False}
                                        }
                                    },
                                    "code_files": {
                                        "type": "object", 
                                        "title": "代码文件处理",
                                        "widget": "json_editor",
                                        "properties": {
                                            "extract_comments": {"type": "boolean", "default": True},
                                            "extract_docstrings": {"type": "boolean", "default": True}
                                        }
                                    }
                                }
                            }
                        },
                        default={
                            "text_files": {"encoding": "utf-8", "remove_empty_lines": False},
                            "code_files": {"extract_comments": True, "extract_docstrings": True}
                        },
                        order=1
                    )
                }
            ),
            
            # 高级设置section - 包含代码编辑器和API配置
            "advanced": ConfigSectionSchema(
                id="advanced",
                title="高级设置",
                description="高级配置选项和自定义脚本",
                icon="settings_applications",
                order=4,
                collapsible=True,
                collapsed=True,
                fields={
                    "custom_processing_script": ConfigFieldSchema(
                        type=ConfigFieldType.STRING,
                        title="自定义处理脚本",
                        description="用于自定义文件处理的Python脚本",
                        widget=ConfigUIWidget.CODE_EDITOR,
                        code_language="python",
                        default="""# 自定义文件处理脚本
def process_file(file_path, content, metadata):
    \"\"\"
    自定义文件处理函数
    
    Args:
        file_path (str): 文件路径
        content (str): 文件内容
        metadata (dict): 文件元数据
    
    Returns:
        dict: 处理后的数据
    \"\"\"
    # 在这里添加自定义处理逻辑
    return {
        'processed_content': content,
        'custom_metadata': metadata
    }
""",
                        order=0,
                        help_text="编写Python代码来自定义文件处理逻辑"
                    ),
                    
                    "webhook_config": ConfigFieldSchema(
                        type=ConfigFieldType.OBJECT,
                        title="Webhook配置",
                        description="文件变化时调用的外部API配置",
                        widget=ConfigUIWidget.API_ENDPOINT_BUILDER,
                        default={
                            "enabled": False,
                            "method": "POST",
                            "url": "",
                            "headers": {},
                            "params": {}
                        },
                        order=1,
                        help_text="配置文件变化时要通知的外部服务"
                    ),
                    
                    "schedule_config": ConfigFieldSchema(
                        type=ConfigFieldType.STRING,
                        title="定时任务配置",
                        description="定时扫描的Cron表达式配置",
                        widget=ConfigUIWidget.CRON_EDITOR,
                        default="0 */6 * * *",  # 每6小时执行一次
                        order=2,
                        help_text="配置定时扫描任务的执行时间"
                    ),
                    
                    "performance_tuning": ConfigFieldSchema(
                        type=ConfigFieldType.OBJECT,
                        title="性能调优",
                        description="性能相关的配置参数",
                        widget=ConfigUIWidget.IFRAME_WIDGET,
                        iframe_src="/connector-ui/iframe-content/filesystem/performance_tuning",
                        custom_widget_config={
                            "type": "iframe",
                            "height": 400,
                            "template_path": "performance_tuning"
                        },
                        default={
                            "max_concurrent_files": 10,
                            "batch_size": 50,
                            "cache_enabled": True
                        },
                        order=3
                    )
                }
            )
        },
        
        # 预设配置模板
        presets={
            "lightweight": {
                "name": "轻量级监控",
                "description": "适合资源有限的环境",
                "config": {
                    "max_file_size": 5,
                    "max_content_length": 10000,
                    "polling_interval": 60,
                    "performance_tuning": {
                        "max_concurrent_files": 5,
                        "batch_size": 20
                    }
                }
            },
            "development": {
                "name": "开发环境",
                "description": "适合开发项目监控",
                "config": {
                    "watch_paths": ["~/Projects", "~/Development"],
                    "supported_extensions": [".py", ".js", ".ts", ".html", ".css", ".json", ".md"],
                    "ignore_patterns": ["node_modules/*", "__pycache__/*", ".git/*", "*.log", "*.tmp"],
                    "max_content_length": 100000
                }
            },
            "documentation": {
                "name": "文档监控",
                "description": "专注于文档文件监控",
                "config": {
                    "supported_extensions": [".md", ".txt", ".rst", ".doc", ".docx", ".pdf"],
                    "max_file_size": 20,
                    "content_extraction_rules": {
                        "text_files": {
                            "encoding": "utf-8",
                            "remove_empty_lines": True
                        }
                    }
                }
            }
        }
    )

# 导出函数供连接器使用
def get_filesystem_config_schema() -> dict:
    """获取文件系统连接器配置Schema的JSON格式"""
    schema_obj = create_filesystem_advanced_schema()
    return schema_obj.to_json_schema()

def get_filesystem_ui_schema() -> dict:
    """获取文件系统连接器UI Schema"""
    schema_obj = create_filesystem_advanced_schema()
    return schema_obj.to_ui_schema()

if __name__ == "__main__":
    # 测试schema生成
    import json
    
    schema_obj = create_filesystem_advanced_schema()
    
    print("=== JSON Schema ===")
    print(json.dumps(schema_obj.to_json_schema(), indent=2, ensure_ascii=False))
    
    print("\n=== UI Schema ===")
    print(json.dumps(schema_obj.to_ui_schema(), indent=2, ensure_ascii=False))