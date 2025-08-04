#!/usr/bin/env python3
"""
Linch Mind 文件系统连接器
独立进程，监控文件系统变化并推送数据到Daemon
Session 3 核心实现 - 重构版本

feat: 增加文件类型过滤功能，提升监控效率
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent
import time
import logging

# 支持的文件类型扩展名（新增功能）
SUPPORTED_EXTENSIONS = {'.txt', '.md', '.py', '.js', '.json', '.yaml', '.yml', '.html', '.css'}


# 导入基类
from shared.base import BaseConnector, run_connector


class FileSystemConnector(BaseConnector, FileSystemEventHandler):
    """文件系统连接器 - 监控文件变化并推送到Daemon

    功能特性:
    - 实时监控指定目录的文件变化
    - 支持多种文件格式的内容提取
    - 可配置的文件大小和类型过滤
    - 智能忽略临时文件和系统文件
    """

    def __init__(self, daemon_url: str = None):
        BaseConnector.__init__(self, "filesystem", daemon_url)
        FileSystemEventHandler.__init__(self)

        # 使用异步队列进行事件处理
        self.event_queue = asyncio.Queue()

        # 配置将从daemon加载
        self.global_settings = {}
        self.watch_directories = []
        self.effective_configs = {}  # 缓存每个目录的有效配置

    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """文件系统连接器配置schema - 完整示例版本"""
        return {
            "type": "object",
            "title": "文件系统连接器配置",
            "description": "配置文件系统监控的全部参数，展示连接器配置系统的强大功能",
            "properties": {
                # 基础配置
                "global_settings": {
                    "type": "object",
                    "title": "全局配置",
                    "description": "应用于所有监控目录的默认配置",
                    "properties": {
                        "supported_extensions": {
                            "type": "array",
                            "title": "默认支持的文件类型",
                            "description": "所有目录默认监控的文件扩展名",
                            "items": {"type": "string"},
                            "default": [".txt", ".md", ".rtf", ".doc", ".docx"],
                            "widget": "tag_input",
                            "widget_config": {
                                "predefined_tags": [".txt", ".md", ".rtf", ".doc", ".docx", ".pdf", ".odt", ".csv"],
                                "allow_custom": True
                            }
                        },
                        "max_file_size": {
                            "type": "integer",
                            "title": "默认最大文件大小 (MB)",
                            "description": "默认文件大小限制",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 100
                        },
                        "ignore_patterns": {
                            "type": "array",
                            "title": "默认忽略模式",
                            "description": "默认忽略的文件模式",
                            "items": {"type": "string"},
                            "default": ["*.tmp", ".*", "node_modules/*", "__pycache__/*", "*.log", ".git/*"]
                        }
                    }
                },
                "watch_directories": {
                    "type": "array",
                    "title": "监控目录配置",
                    "description": "每个目录的详细监控配置",
                    "widget": "dynamic_list",
                    "widget_config": {
                        "add_button_text": "添加监控目录",
                        "remove_button_text": "删除",
                        "allow_reorder": true,
                        "min_items": 1,
                        "max_items": 20,
                        "item_title_template": "{{name || path || '新目录'}}",
                        "item_subtitle_template": "{{path}}",
                        "collapse_items": true,
                        "show_item_index": false
                    },
                    "items": {
                        "type": "object",
                        "title": "目录配置",
                        "properties": {
                            "path": {
                                "type": "string",
                                "title": "目录路径",
                                "description": "要监控的目录路径",
                                "widget": "directory_picker",
                                "widget_config": {
                                    "show_hidden": false,
                                    "allow_manual_input": true
                                }
                            },
                            "name": {
                                "type": "string",
                                "title": "配置名称",
                                "description": "此目录配置的显示名称（可选）",
                                "default": ""
                            },
                            "enabled": {
                                "type": "boolean",
                                "title": "启用监控",
                                "description": "是否监控此目录",
                                "default": true,
                                "widget": "switch"
                            },
                            "recursive": {
                                "type": "boolean",
                                "title": "递归监控",
                                "description": "是否监控子目录",
                                "default": true,
                                "widget": "switch"
                            },
                            "use_custom_config": {
                                "type": "boolean",
                                "title": "使用自定义配置",
                                "description": "是否为此目录使用单独的配置，关闭则使用全局配置",
                                "default": false,
                                "widget": "switch"
                            },
                            "custom_config": {
                                "type": "object",
                                "title": "自定义配置",
                                "description": "此目录的专用配置（仅当启用自定义配置时生效）",
                                "widget": "conditional_section",
                                "widget_config": {
                                    "condition": {
                                        "field": "use_custom_config",
                                        "operator": "equals",
                                        "value": true
                                    },
                                    "collapse_when_hidden": true
                                },
                                "properties": {
                                    "supported_extensions": {
                                        "type": "array",
                                        "title": "支持的文件类型",
                                        "description": "此目录监控的文件扩展名",
                                        "items": {"type": "string"},
                                        "default": [],
                                        "widget": "tag_input",
                                        "widget_config": {
                                            "predefined_tags": [".txt", ".md", ".rtf", ".doc", ".docx", ".pdf", ".odt", ".csv"],
                                            "allow_custom": True,
                                            "placeholder": "留空使用全局配置"
                                        }
                                    },
                                    "max_file_size": {
                                        "type": "integer",
                                        "title": "最大文件大小 (MB)",
                                        "description": "此目录的文件大小限制，0表示使用全局配置",
                                        "default": 0,
                                        "minimum": 0,
                                        "maximum": 100,
                                        "widget": "slider",
                                        "widget_config": {
                                            "show_value": true,
                                            "unit": "MB",
                                            "special_values": {
                                                "0": "使用全局配置"
                                            }
                                        }
                                    },
                                    "ignore_patterns": {
                                        "type": "array",
                                        "title": "额外忽略模式",
                                        "description": "在全局忽略模式基础上，此目录额外忽略的文件模式",
                                        "items": {"type": "string"},
                                        "default": [],
                                        "widget": "tag_input",
                                        "widget_config": {
                                            "placeholder": "此目录特有的忽略模式"
                                        }
                                    },
                                    "priority": {
                                        "type": "integer",
                                        "title": "处理优先级",
                                        "description": "此目录文件的处理优先级 (1-10，数字越大优先级越高)",
                                        "default": 5,
                                        "minimum": 1,
                                        "maximum": 10,
                                        "widget": "slider"
                                    }
                                }
                            }
                        },
                        "required": ["path"]
                    },
                    "default": [
                        {
                            "path": "~/Downloads",
                            "name": "下载目录",
                            "enabled": true,
                            "recursive": true,
                            "use_custom_config": false,
                            "custom_config": {}
                        },
                        {
                            "path": "~/Documents",
                            "name": "文档目录",
                            "enabled": true,
                            "recursive": true,
                            "use_custom_config": false,
                            "custom_config": {}
                        }
                    ],
                },
                
                # 文件过滤配置
                "max_content_length": {
                    "type": "integer",
                    "title": "最大内容长度",
                    "description": "文件内容截断长度（字符数）",
                    "default": 50000,
                    "minimum": 1000,
                    "maximum": 100000,
                    "widget": "number_input",
                    "widget_config": {
                        "step": 1000,
                        "format": "###,###"
                    }
                },
                
                # 高级配置
                "monitoring_enabled": {
                    "type": "boolean",
                    "title": "启用监控",
                    "description": "是否启用文件系统监控",
                    "default": True,
                    "widget": "switch"
                },
                "real_time_processing": {
                    "type": "boolean",
                    "title": "实时处理",
                    "description": "是否实时处理文件变化",
                    "default": True,
                    "widget": "switch"
                },
                "batch_processing": {
                    "type": "object",
                    "title": "批处理配置",
                    "description": "批量处理文件变化的配置",
                    "properties": {
                        "enabled": {
                            "type": "boolean",
                            "title": "启用批处理",
                            "default": False,
                            "widget": "checkbox"
                        },
                        "batch_size": {
                            "type": "integer",
                            "title": "批处理大小",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 100
                        },
                        "batch_timeout": {
                            "type": "integer",
                            "title": "批处理超时 (秒)",
                            "default": 30,
                            "minimum": 5,
                            "maximum": 300
                        }
                    }
                },
                
                # 调度配置 - 使用Cron编辑器
                "scan_schedule": {
                    "type": "string",
                    "title": "扫描调度",
                    "description": "定期扫描文件的Cron表达式",
                    "default": "0 */6 * * *",
                    "widget": "cron_editor",
                    "widget_config": {
                        "show_preview": True,
                        "presets": {
                            "每小时": "0 * * * *",
                            "每6小时": "0 */6 * * *",
                            "每天凌晨": "0 0 * * *",
                            "工作日": "0 9 * * 1-5"
                        }
                    }
                },
                
                # 内容处理配置
                "content_processing": {
                    "type": "object",
                    "title": "内容处理",
                    "description": "文件内容处理相关配置",
                    "properties": {
                        "extract_metadata": {
                            "type": "boolean",
                            "title": "提取元数据",
                            "description": "是否提取文件元数据",
                            "default": True
                        },
                        "content_hash": {
                            "type": "boolean",
                            "title": "计算内容哈希",
                            "description": "是否计算文件内容哈希",
                            "default": False
                        },
                        "encoding_detection": {
                            "type": "boolean",
                            "title": "编码检测",
                            "description": "是否自动检测文件编码",
                            "default": True
                        },
                        "preprocessing_script": {
                            "type": "string",
                            "title": "预处理脚本",
                            "description": "文件内容预处理的Python脚本",
                            "default": "# 预处理脚本示例\ndef preprocess(content, metadata):\n    # 在这里添加预处理逻辑\n    return content",
                            "widget": "code_editor",
                            "widget_config": {
                                "language": "python",
                                "height": 200,
                                "show_line_numbers": True
                            }
                        }
                    }
                },
                
                # API集成配置 - 使用API端点构建器
                "webhook_config": {
                    "type": "object",
                    "title": "Webhook配置",
                    "description": "文件变化时调用的Webhook配置",
                    "widget": "api_endpoint_builder",
                    "widget_config": {
                        "default_method": "POST",
                        "show_test_button": True,
                        "support_auth": True
                    },
                    "properties": {
                        "enabled": {
                            "type": "boolean",
                            "title": "启用Webhook",
                            "default": False
                        },
                        "url": {
                            "type": "string",
                            "title": "Webhook URL",
                            "format": "uri"
                        },
                        "method": {
                            "type": "string",
                            "title": "HTTP方法",
                            "enum": ["GET", "POST", "PUT", "PATCH"],
                            "default": "POST"
                        },
                        "headers": {
                            "type": "object",
                            "title": "请求头",
                            "default": {
                                "Content-Type": "application/json"
                            }
                        },
                        "timeout": {
                            "type": "integer",
                            "title": "超时时间 (秒)",
                            "default": 30,
                            "minimum": 1,
                            "maximum": 300
                        }
                    }
                },
                
                # 通知配置 - 动态表单示例
                "notifications": {
                    "type": "object",
                    "title": "通知配置",
                    "description": "文件变化通知设置",
                    "widget": "dynamic_form",
                    "widget_config": {
                        "template": "notification_config",
                        "allow_add_fields": True
                    },
                    "properties": {
                        "email_enabled": {
                            "type": "boolean",
                            "title": "启用邮件通知",
                            "default": False
                        },
                        "email_recipients": {
                            "type": "array",
                            "title": "邮件接收者",
                            "items": {"type": "string", "format": "email"},
                            "default": []
                        },
                        "notification_threshold": {
                            "type": "integer",
                            "title": "通知阈值",
                            "description": "当文件变化数量超过此值时发送通知",
                            "default": 10,
                            "minimum": 1
                        }
                    }
                }
            },
            "required": ["global_settings", "watch_directories", "monitoring_enabled"],
            "dependencies": {
                "batch_processing": {
                    "properties": {
                        "real_time_processing": {"const": False}
                    }
                },
                "webhook_config": {
                    "properties": {
                        "webhook_config.enabled": {"const": True}
                    },
                    "required": ["webhook_config.url"]
                }
            }
        }

    @classmethod
    def get_config_ui_schema(cls) -> Dict[str, Any]:
        """UI渲染提示 - 完整分节示例"""
        return {
            "ui_layout": "sections",
            "ui:sections": {
                "basic_config": {
                    "ui:title": "基础配置",
                    "ui:description": "文件系统监控的基本设置",
                    "ui:icon": "folder_open",
                    "ui:collapsible": False,
                    "ui:fields": {
                        "watch_paths": {
                            "ui:help": "选择要监控的目录，支持多选",
                            "ui:placeholder": "点击选择目录..."
                        },
                        "supported_extensions": {
                            "ui:help": "选择要监控的文件类型，也可以添加自定义类型",
                            "ui:placeholder": "输入文件扩展名..."
                        },
                        "monitoring_enabled": {
                            "ui:help": "总开关，关闭后停止所有监控活动"
                        }
                    }
                },
                "filtering_config": {
                    "ui:title": "文件过滤",
                    "ui:description": "配置文件大小和内容过滤规则",
                    "ui:icon": "filter_alt",
                    "ui:collapsible": True,
                    "ui:collapsed": False,
                    "ui:fields": {
                        "max_file_size": {
                            "ui:help": "文件大小超过此值将被忽略，避免处理大文件"
                        },
                        "max_content_length": {
                            "ui:help": "文件内容超过此长度将被截断"
                        },
                        "ignore_patterns": {
                            "ui:help": "每行一个忽略模式，支持通配符 * 和 ?",
                            "ui:placeholder": "例如: *.tmp\n.*\nnode_modules/*"
                        }
                    }
                },
                "processing_config": {
                    "ui:title": "处理方式",
                    "ui:description": "配置文件变化的处理方式",
                    "ui:icon": "settings",
                    "ui:collapsible": True,
                    "ui:collapsed": True,
                    "ui:fields": {
                        "real_time_processing": {
                            "ui:help": "开启后立即处理文件变化，关闭后使用批处理"
                        },
                        "batch_processing": {
                            "ui:help": "批处理可以减少系统负载，适合大量文件变化的场景",
                            "ui:conditional": {
                                "show_when": {
                                    "real_time_processing": False
                                }
                            }
                        },
                        "scan_schedule": {
                            "ui:help": "定期扫描所有监控目录，发现遗漏的文件变化"
                        }
                    }
                },
                "content_processing": {
                    "ui:title": "内容处理",
                    "ui:description": "文件内容分析和预处理设置",
                    "ui:icon": "code",
                    "ui:collapsible": True,
                    "ui:collapsed": True,
                    "ui:fields": {
                        "content_processing.extract_metadata": {
                            "ui:help": "提取文件的创建时间、修改时间、大小等元数据"
                        },
                        "content_processing.content_hash": {
                            "ui:help": "计算文件内容的MD5哈希值，用于去重"
                        },
                        "content_processing.encoding_detection": {
                            "ui:help": "自动检测文件编码，提高非UTF-8文件的处理准确性"
                        },
                        "content_processing.preprocessing_script": {
                            "ui:help": "自定义Python脚本对文件内容进行预处理",
                            "ui:advanced": True
                        }
                    }
                },
                "integration_config": {
                    "ui:title": "集成配置",
                    "ui:description": "外部系统集成和通知设置",
                    "ui:icon": "integration_instructions",
                    "ui:collapsible": True,
                    "ui:collapsed": True,
                    "ui:fields": {
                        "webhook_config": {
                            "ui:help": "配置Webhook在文件变化时调用外部API",
                            "ui:advanced": True
                        },
                        "notifications": {
                            "ui:help": "配置文件变化通知方式"
                        }
                    }
                }
            },
            "ui:order": [
                "basic_config",
                "filtering_config", 
                "processing_config",
                "content_processing",
                "integration_config"
            ],
            "ui:layout_config": {
                "show_section_icons": True,
                "compact_mode": False,
                "enable_search": True,
                "show_progress": True
            }
        }

    async def _load_filesystem_config(self):
        """加载文件系统特定配置"""
        await self.load_config_from_daemon()

        # 加载全局设置
        self.global_settings = self.get_config("global_settings", {
            "supported_extensions": [".txt", ".md", ".rtf", ".doc", ".docx"],
            "max_file_size": 10,
            "ignore_patterns": ["*.tmp", ".*", "node_modules/*", "__pycache__/*", "*.log", ".git/*"]
        })

        # 加载监控目录配置
        self.watch_directories = self.get_config("watch_directories", self._get_default_watch_directories())
        
        # 为每个目录计算有效配置
        self._compute_effective_configs()

        self.logger.info(f"全局配置: {self.global_settings}")
        self.logger.info(f"监控目录数量: {len(self.watch_directories)}")
        for i, dir_config in enumerate(self.watch_directories):
            if dir_config.get('enabled', True):
                self.logger.info(f"  目录 {i+1}: {dir_config['path']} (递归: {dir_config.get('recursive', True)})")
                if dir_config.get('use_custom_config', False):
                    self.logger.info(f"    使用自定义配置: {dir_config.get('custom_config', {})}")
                else:
                    self.logger.info(f"    使用全局配置")

    def _get_default_watch_directories(self) -> List[Dict[str, Any]]:
        """获取默认监控目录配置"""
        default_dirs = [
            {
                "path": str(Path.home() / "Downloads"),
                "name": "下载目录",
                "enabled": True,
                "recursive": True,
                "use_custom_config": False,
                "custom_config": {}
            },
            {
                "path": str(Path.home() / "Documents"),
                "name": "文档目录",
                "enabled": True,
                "recursive": True,
                "use_custom_config": False,
                "custom_config": {}
            }
        ]
        # 过滤存在的路径
        return [dir_config for dir_config in default_dirs if Path(dir_config["path"]).exists()]

    def _compute_effective_configs(self):
        """计算每个目录的有效配置"""
        self.effective_configs = {}
        
        for dir_config in self.watch_directories:
            path = dir_config["path"]
            
            if dir_config.get("use_custom_config", False):
                # 使用自定义配置，未设置的项使用全局配置
                custom_config = dir_config.get("custom_config", {})
                effective_config = {
                    "supported_extensions": custom_config.get("supported_extensions") or self.global_settings.get("supported_extensions", []),
                    "max_file_size": (custom_config.get("max_file_size") or self.global_settings.get("max_file_size", 10)) * 1024 * 1024,  # 转换为字节
                    "ignore_patterns": self.global_settings.get("ignore_patterns", []) + custom_config.get("ignore_patterns", []),
                    "priority": custom_config.get("priority", 5)
                }
            else:
                # 使用全局配置
                effective_config = {
                    "supported_extensions": self.global_settings.get("supported_extensions", []),
                    "max_file_size": self.global_settings.get("max_file_size", 10) * 1024 * 1024,  # 转换为字节
                    "ignore_patterns": self.global_settings.get("ignore_patterns", []),
                    "priority": 5
                }
            
            # 转换为set便于快速查找
            effective_config["supported_extensions"] = set(effective_config["supported_extensions"])
            
            self.effective_configs[path] = effective_config

    def _get_effective_config_for_path(self, file_path: str) -> Dict[str, Any]:
        """根据文件路径获取相应的有效配置"""
        file_path_obj = Path(file_path).resolve()
        
        # 查找匹配的目录配置
        for dir_config in self.watch_directories:
            if not dir_config.get("enabled", True):
                continue
                
            dir_path = Path(dir_config["path"]).resolve()
            
            try:
                # 检查文件是否在此目录下
                if dir_config.get("recursive", True):
                    # 递归模式：检查是否为子路径
                    file_path_obj.relative_to(dir_path)
                else:
                    # 非递归模式：只检查直接父目录
                    if file_path_obj.parent == dir_path:
                        pass  # 匹配
                    else:
                        continue  # 不匹配
                
                return self.effective_configs.get(dir_config["path"], {})
            except ValueError:
                # 不是子路径，继续检查下一个
                continue
        
        # 如果没有找到匹配的目录配置，使用第一个启用的目录的配置作为默认
        for dir_config in self.watch_directories:
            if dir_config.get("enabled", True):
                return self.effective_configs.get(dir_config["path"], {})
        
        # 最后的备用方案：使用全局配置
        return {
            "supported_extensions": set(self.global_settings.get("supported_extensions", [])),
            "max_file_size": self.global_settings.get("max_file_size", 10) * 1024 * 1024,
            "ignore_patterns": self.global_settings.get("ignore_patterns", []),
            "priority": 5
        }

    def on_modified(self, event):
        """文件修改事件"""
        if not event.is_directory:
            self.logger.info(f"🔄 检测到文件修改: {event.src_path}")
            self._queue_file_event("modified", event.src_path)

    def on_created(self, event):
        """文件创建事件"""
        if not event.is_directory:
            self.logger.info(f"🆕 检测到文件创建: {event.src_path}")
            self._queue_file_event("created", event.src_path)

    def _queue_file_event(self, event_type: str, file_path: str):
        """将文件事件加入队列"""
        try:
            # 使用线程安全的方式将事件放入异步队列
            event_data = {
                "event_type": event_type,
                "file_path": file_path,
                "timestamp": time.time(),
            }
            # 如果有事件循环在运行，则放入队列
            try:
                loop = asyncio.get_running_loop()
                asyncio.run_coroutine_threadsafe(
                    self.event_queue.put(event_data), loop
                )
            except RuntimeError:
                # 没有运行的事件循环，创建一个临时的
                self.logger.warning("没有运行的事件循环，跳过此事件")
            self.logger.debug(f"文件事件已加入队列: {event_type} - {file_path}")
        except Exception as e:
            self.logger.error(f"将文件事件加入队列失败: {e}")

    async def _process_file_event(self, event_type: str, file_path: str):
        """处理文件事件"""
        try:
            file_path_obj = Path(file_path)
            
            # 获取此文件的有效配置
            effective_config = self._get_effective_config_for_path(file_path)
            if not effective_config:
                self.logger.debug(f"无法获取文件配置，跳过: {file_path}")
                return

            # 检查文件扩展名
            if file_path_obj.suffix.lower() not in effective_config.get("supported_extensions", set()):
                self.logger.debug(f"跳过不支持的文件类型: {file_path} (扩展名: {file_path_obj.suffix})")
                return

            # 检查文件大小
            file_size = file_path_obj.stat().st_size
            max_file_size = effective_config.get("max_file_size", 10 * 1024 * 1024)
            if file_size > max_file_size:
                self.logger.debug(f"跳过过大文件: {file_path} ({file_size / 1024 / 1024:.1f}MB > {max_file_size / 1024 / 1024:.1f}MB)")
                return
            
            # 检查忽略模式
            ignore_patterns = effective_config.get("ignore_patterns", [])
            if self._should_ignore_file(file_path, ignore_patterns):
                self.logger.debug(f"文件匹配忽略模式，跳过: {file_path}")
                return

            # 读取文件内容
            try:
                content = file_path_obj.read_text(encoding="utf-8", errors="ignore")
            except Exception as e:
                self.logger.error(f"读取文件失败 {file_path}: {e}")
                return

            # 限制内容长度
            max_content = self.get_config("max_content_length", 50000)
            if len(content) > max_content:
                content = content[:max_content] + "\n... (内容已截断)"

            # 构造数据项 - 使用基类方法
            metadata = {
                "event_type": event_type,
                "file_size": len(content),
                "file_extension": file_path_obj.suffix,
                "file_name": file_path_obj.name,
                "directory": str(file_path_obj.parent),
                "priority": effective_config.get("priority", 5),
                "config_source": "custom" if self._is_using_custom_config(file_path) else "global"
            }
            data_item = self.create_data_item(content, metadata, str(file_path))

            # 推送到Daemon - 使用基类方法
            success = await self.push_to_daemon(data_item)
            if success:
                config_info = f"(优先级: {metadata['priority']}, 配置: {metadata['config_source']})"
                self.logger.info(
                    f"✅ 处理文件事件: {event_type} - {file_path_obj.name} {config_info}"
                )
            else:
                self.logger.error(f"❌ 推送失败: {file_path_obj.name}")

        except Exception as e:
            self._handle_error(e, f"处理文件事件失败 {file_path}")
    
    def _should_ignore_file(self, file_path: str, ignore_patterns: List[str]) -> bool:
        """检查文件是否应该被忽略"""
        import fnmatch
        
        file_path_obj = Path(file_path)
        file_name = file_path_obj.name
        relative_path = str(file_path_obj)
        
        for pattern in ignore_patterns:
            # 检查文件名匹配
            if fnmatch.fnmatch(file_name, pattern):
                return True
            # 检查相对路径匹配
            if fnmatch.fnmatch(relative_path, pattern):
                return True
            # 检查路径包含匹配
            if pattern.endswith('/*') and pattern[:-2] in str(file_path_obj.parent):
                return True
        
        return False
    
    def _is_using_custom_config(self, file_path: str) -> bool:
        """检查文件是否使用自定义配置"""
        file_path_obj = Path(file_path).resolve()
        
        for dir_config in self.watch_directories:
            if not dir_config.get("enabled", True):
                continue
                
            dir_path = Path(dir_config["path"]).resolve()
            
            try:
                if dir_config.get("recursive", True):
                    file_path_obj.relative_to(dir_path)
                else:
                    if file_path_obj.parent != dir_path:
                        continue
                
                return dir_config.get("use_custom_config", False)
            except ValueError:
                continue
        
        return False

    async def _event_processor(self):
        """异步事件处理器 - 消费队列中的文件事件"""
        self.logger.info("启动异步事件处理器...")

        while not self.should_stop:
            try:
                # 等待队列中的事件，避免忙等待
                try:
                    event_data = await asyncio.wait_for(
                        self.event_queue.get(), timeout=1.0
                    )
                    await self._process_file_event(
                        event_data["event_type"], event_data["file_path"]
                    )
                    self.event_queue.task_done()
                except asyncio.TimeoutError:
                    # 超时是正常的，继续循环
                    continue

            except Exception as e:
                await self._handle_async_error(e, "事件处理器错误", retry_delay=1.0)

        self.logger.info("异步事件处理器已停止")

    async def start_monitoring(self):
        """启动文件监控"""
        self.logger.info("启动文件系统监控...")

        # 加载配置
        await self._load_filesystem_config()

        if not self.watch_paths:
            self.logger.error("没有可监控的路径")
            return

        # 测试Daemon连接
        await self.test_daemon_connection()

        # 启动配置监控任务
        config_monitor_task = asyncio.create_task(self.start_config_monitoring())

        # 启动异步事件处理器
        event_processor_task = asyncio.create_task(self._event_processor())
        self.logger.info("异步事件处理器已启动")

        # 启动文件监控
        observer = Observer()

        for watch_path in self.watch_paths:
            try:
                observer.schedule(self, watch_path, recursive=True)
                self.logger.info(f"🔍 监控路径: {watch_path}")
            except Exception as e:
                self.logger.error(f"无法监控路径 {watch_path}: {e}")

        observer.start()
        self.logger.info("文件系统监控已启动")

        try:
            # 保持进程运行
            while not self.should_stop:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("收到中断信号")
        finally:
            self.logger.info("停止文件监控...")
            self.should_stop = True

            # 停止文件监控
            observer.stop()
            observer.join()

            # 停止任务
            config_monitor_task.cancel()
            if not event_processor_task.done():
                await event_processor_task

            self.logger.info("文件系统连接器已完全停止")


if __name__ == "__main__":
    try:
        # 创建连接器实例
        daemon_url = os.getenv("DAEMON_URL")  # None表示使用配置文件
        connector = FileSystemConnector(daemon_url)

        # 使用基类的运行方法
        asyncio.run(run_connector(connector))
    except KeyboardInterrupt:
        print("进程被中断")
    except Exception as e:
        print(f"连接器运行错误: {e}")
        sys.exit(1)
