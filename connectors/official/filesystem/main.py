#!/usr/bin/env python3
"""
Linch Mind 文件系统连接器
独立进程，监控文件系统变化并推送数据到Daemon
Session 3 核心实现 - 重构版本
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent
import time
import logging
from queue import Queue


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

        # 使用队列进行线程安全的事件处理
        self.event_queue = Queue()

        # 配置将从daemon加载
        self.watch_paths = []
        self.supported_extensions = set()
        self.max_file_size = 0
        self.ignore_patterns = []

    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """文件系统连接器配置schema - 支持目录级别配置"""
        return {
            "type": "object",
            "title": "文件系统连接器配置",
            "description": "配置文件系统监控的路径、文件类型和过滤规则，支持目录级别的个性化配置",
            "properties": {
                "global_config": {
                    "type": "object",
                    "title": "全局默认配置",
                    "description": "所有监控目录的默认配置，可被目录特定配置覆盖",
                    "properties": {
                        "default_extensions": {
                            "type": "array",
                            "title": "默认文件类型",
                            "description": "默认监控的文件扩展名",
                            "items": {"type": "string"},
                            "default": [
                                ".txt",
                                ".md",
                                ".py",
                                ".js",
                                ".html",
                                ".css",
                                ".json",
                                ".yaml",
                            ],
                            "ui_component": "chip_input",
                            "predefined_options": [
                                ".txt",
                                ".md",
                                ".py",
                                ".js",
                                ".ts",
                                ".html",
                                ".css",
                                ".json",
                                ".yaml",
                                ".yml",
                                ".java",
                                ".kt",
                                ".go",
                                ".rs",
                                ".cpp",
                                ".c",
                                ".h",
                                ".xml",
                                ".sql",
                                ".sh",
                            ],
                        },
                        "max_file_size": {
                            "type": "integer",
                            "title": "默认最大文件大小 (MB)",
                            "description": "超过此大小的文件将被忽略",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 1000,
                            "ui_component": "slider",
                        },
                        "max_content_length": {
                            "type": "integer",
                            "title": "默认最大内容长度",
                            "description": "文件内容截断长度（字符数）",
                            "default": 50000,
                            "minimum": 1000,
                            "maximum": 500000,
                            "ui_component": "number_input",
                        },
                        "default_ignore_patterns": {
                            "type": "array",
                            "title": "默认忽略模式",
                            "description": "全局忽略的文件模式",
                            "items": {"type": "string"},
                            "default": [
                                "*.tmp",
                                ".*",
                                "node_modules/*",
                                "__pycache__/*",
                                "*.log",
                                ".git/*",
                            ],
                            "ui_component": "tag_input",
                        },
                    },
                    "required": ["default_extensions", "max_file_size"],
                },
                "directory_configs": {
                    "type": "array",
                    "title": "目录特定配置",
                    "description": "为特定目录定制的监控配置，会覆盖全局默认配置",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "title": "监控路径",
                                "description": "要监控的目录路径",
                                "ui_component": "directory_picker",
                            },
                            "display_name": {
                                "type": "string",
                                "title": "显示名称",
                                "description": "此监控配置的友好名称",
                                "default": "",
                            },
                            "extensions": {
                                "type": "array",
                                "title": "文件类型",
                                "description": "此目录特定的文件扩展名（留空使用全局默认）",
                                "items": {"type": "string"},
                                "ui_component": "chip_input_optional",
                            },
                            "max_file_size": {
                                "type": "integer",
                                "title": "最大文件大小 (MB)",
                                "description": "此目录的文件大小限制（留空使用全局默认）",
                                "minimum": 1,
                                "maximum": 1000,
                                "ui_component": "slider_optional",
                            },
                            "ignore_patterns": {
                                "type": "array",
                                "title": "额外忽略模式",
                                "description": "此目录额外的忽略模式（会添加到全局忽略模式）",
                                "items": {"type": "string"},
                                "ui_component": "tag_input",
                            },
                            "priority": {
                                "type": "string",
                                "title": "优先级",
                                "description": "此目录的处理优先级",
                                "enum": ["high", "normal", "low"],
                                "default": "normal",
                                "ui_component": "select",
                            },
                            "recursive": {
                                "type": "boolean",
                                "title": "递归监控",
                                "description": "是否监控子目录",
                                "default": true,
                                "ui_component": "switch",
                            },
                            "enabled": {
                                "type": "boolean",
                                "title": "启用监控",
                                "description": "是否启用此目录的监控",
                                "default": true,
                                "ui_component": "switch",
                            },
                        },
                        "required": ["path"],
                    },
                    "default": [
                        {
                            "path": "~/Downloads",
                            "display_name": "下载文件夹",
                            "priority": "low",
                            "recursive": false,
                        },
                        {
                            "path": "~/Documents",
                            "display_name": "文档文件夹",
                            "priority": "normal",
                            "recursive": true,
                        },
                    ],
                    "ui_component": "dynamic_list",
                },
                "advanced_settings": {
                    "type": "object",
                    "title": "高级设置",
                    "properties": {
                        "check_interval": {
                            "type": "number",
                            "title": "配置检查间隔 (秒)",
                            "description": "检查配置变更的间隔时间",
                            "default": 30.0,
                            "minimum": 10.0,
                            "maximum": 300.0,
                            "ui_component": "number_input",
                        },
                        "batch_processing": {
                            "type": "boolean",
                            "title": "批量处理",
                            "description": "启用批量处理以提高性能",
                            "default": true,
                            "ui_component": "switch",
                        },
                        "batch_size": {
                            "type": "integer",
                            "title": "批量大小",
                            "description": "批量处理的文件数量",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 100,
                            "ui_component": "number_input",
                        },
                    },
                },
            },
            "required": ["global_config", "directory_configs"],
        }

    @classmethod
    def get_config_ui_schema(cls) -> Dict[str, Any]:
        """UI渲染提示 - 支持层次化配置界面"""
        return {
            "ui_layout": "tabs",  # 使用标签页布局
            "tabs": [
                {
                    "id": "global",
                    "title": "全局默认",
                    "icon": "settings",
                    "description": "设置所有目录的默认监控规则",
                    "fields": ["global_config"],
                },
                {
                    "id": "directories",
                    "title": "目录配置",
                    "icon": "folder",
                    "description": "为特定目录定制监控规则",
                    "fields": ["directory_configs"],
                },
                {
                    "id": "advanced",
                    "title": "高级设置",
                    "icon": "gear",
                    "description": "性能和高级选项",
                    "fields": ["advanced_settings"],
                },
            ],
            "field_components": {
                "global_config": {"component": "group", "layout": "grid", "columns": 2},
                "directory_configs": {
                    "component": "dynamic_list",
                    "add_button_text": "添加监控目录",
                    "empty_message": "还没有配置监控目录",
                    "item_template": {
                        "layout": "card",
                        "show_preview": True,
                        "preview_fields": ["path", "display_name", "priority"],
                    },
                },
                "advanced_settings": {"component": "group", "layout": "form"},
            },
            "validation_rules": {
                "directory_configs": {
                    "min_items": 1,
                    "unique_paths": True,
                    "path_exists": True,
                }
            },
            "help_text": {
                "global_config": "这些设置将作为所有监控目录的默认值。目录特定配置可以覆盖这些默认值。",
                "directory_configs": "为每个目录单独配置监控规则。留空的字段将使用全局默认值。",
                "advanced_settings": "这些设置影响连接器的整体性能和行为。",
            },
            "examples": {
                "directory_configs": [
                    {
                        "title": "开发项目目录",
                        "config": {
                            "path": "~/Projects",
                            "display_name": "我的项目",
                            "extensions": [".py", ".js", ".ts", ".md"],
                            "priority": "high",
                            "recursive": True,
                        },
                    },
                    {
                        "title": "下载文件夹（仅文档）",
                        "config": {
                            "path": "~/Downloads",
                            "display_name": "下载的文档",
                            "extensions": [".pdf", ".txt", ".md"],
                            "max_file_size": 50,
                            "recursive": False,
                        },
                    },
                ]
            },
        }

    async def _load_filesystem_config(self):
        """加载文件系统特定配置"""
        await self.load_config_from_daemon()

        # 获取配置或使用默认值
        self.watch_paths = self.get_config(
            "watch_paths", self._get_default_watch_paths()
        )
        self.supported_extensions = set(
            self.get_config(
                "supported_extensions",
                [
                    ".txt",
                    ".md",
                    ".py",
                    ".js",
                    ".html",
                    ".css",
                    ".json",
                    ".yaml",
                    ".yml",
                ],
            )
        )
        self.max_file_size = (
            self.get_config("max_file_size", 1) * 1024 * 1024
        )  # 转换为字节
        self.ignore_patterns = self.get_config(
            "ignore_patterns",
            ["*.tmp", ".*", "node_modules/*", "__pycache__/*", "*.log"],
        )

        self.logger.info(f"监控路径: {self.watch_paths}")
        self.logger.info(f"支持的文件类型: {self.supported_extensions}")
        self.logger.info(f"最大文件大小: {self.max_file_size / 1024 / 1024:.1f}MB")

    def _get_default_watch_paths(self) -> List[str]:
        """获取默认监控路径"""
        default_paths = [
            str(Path.home() / "Downloads"),
            str(Path.home() / "Documents"),
        ]
        # 过滤存在的路径
        return [path for path in default_paths if Path(path).exists()]

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
            self.event_queue.put_nowait(
                {
                    "event_type": event_type,
                    "file_path": file_path,
                    "timestamp": time.time(),
                }
            )
            self.logger.debug(f"文件事件已加入队列: {event_type} - {file_path}")
        except Exception as e:
            self.logger.error(f"将文件事件加入队列失败: {e}")

    async def _process_file_event(self, event_type: str, file_path: str):
        """处理文件事件"""
        try:
            file_path_obj = Path(file_path)

            # 检查文件扩展名
            if file_path_obj.suffix.lower() not in self.supported_extensions:
                self.logger.debug(f"跳过不支持的文件类型: {file_path}")
                return

            # 检查文件大小
            if file_path_obj.stat().st_size > self.max_file_size:
                self.logger.debug(f"跳过过大文件: {file_path}")
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
            }
            data_item = self.create_data_item(content, metadata, str(file_path))

            # 推送到Daemon - 使用基类方法
            success = await self.push_to_daemon(data_item)
            if success:
                self.logger.info(
                    f"✅ 处理文件事件: {event_type} - {file_path_obj.name}"
                )
            else:
                self.logger.error(f"❌ 推送失败: {file_path_obj.name}")

        except Exception as e:
            self.logger.error(f"处理文件事件失败 {file_path}: {e}")

    async def _event_processor(self):
        """异步事件处理器 - 消费队列中的文件事件"""
        self.logger.info("启动异步事件处理器...")

        while not self.should_stop:
            try:
                # 非阻塞获取队列中的事件
                if not self.event_queue.empty():
                    event_data = self.event_queue.get_nowait()
                    await self._process_file_event(
                        event_data["event_type"], event_data["file_path"]
                    )
                    self.event_queue.task_done()
                else:
                    # 短暂等待，避免CPU繁忙等待
                    await asyncio.sleep(0.1)

            except Exception as e:
                self.logger.error(f"事件处理器错误: {e}")
                await asyncio.sleep(1)  # 错误恢复延迟

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
