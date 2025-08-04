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
        self.watch_paths = []
        self.supported_extensions = set()
        self.max_file_size = 0
        self.ignore_patterns = []

    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """文件系统连接器配置schema - 简化版本"""
        return {
            "type": "object",
            "title": "文件系统连接器配置",
            "description": "配置文件系统监控的基本参数",
            "properties": {
                "watch_paths": {
                    "type": "array",
                    "title": "监控路径",
                    "description": "要监控的目录路径列表",
                    "items": {"type": "string"},
                    "default": ["~/Downloads", "~/Documents"],
                },
                "supported_extensions": {
                    "type": "array",
                    "title": "支持的文件类型",
                    "description": "监控的文件扩展名",
                    "items": {"type": "string"},
                    "default": [".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".yaml"],
                },
                "max_file_size": {
                    "type": "integer",
                    "title": "最大文件大小 (MB)",
                    "description": "超过此大小的文件将被忽略",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 100,
                },
                "max_content_length": {
                    "type": "integer",
                    "title": "最大内容长度",
                    "description": "文件内容截断长度（字符数）",
                    "default": 50000,
                    "minimum": 1000,
                    "maximum": 100000,
                },
                "ignore_patterns": {
                    "type": "array",
                    "title": "忽略模式",
                    "description": "忽略的文件模式",
                    "items": {"type": "string"},
                    "default": ["*.tmp", ".*", "node_modules/*", "__pycache__/*", "*.log", ".git/*"],
                },
            },
            "required": ["watch_paths", "supported_extensions"],
        }

    @classmethod
    def get_config_ui_schema(cls) -> Dict[str, Any]:
        """UI渲染提示 - 简化版本"""
        return {
            "ui_layout": "form",
            "help_text": {
                "watch_paths": "输入要监控的目录路径，每行一个",
                "supported_extensions": "输入要监控的文件扩展名，如 .txt, .py",
                "max_file_size": "超过此大小的文件将被忽略",
                "ignore_patterns": "文件匹配这些模式时将被忽略",
            },
        }

    async def _load_filesystem_config(self):
        """加载文件系统特定配置"""
        await self.load_config_from_daemon()

        # 获取配置或使用默认值
        self.watch_paths = self.get_config("watch_paths", self._get_default_watch_paths())
        self.supported_extensions = set(
            self.get_config(
                "supported_extensions",
                [".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".yaml"],
            )
        )
        self.max_file_size = self.get_config("max_file_size", 10) * 1024 * 1024  # 转换为字节
        self.ignore_patterns = self.get_config(
            "ignore_patterns",
            ["*.tmp", ".*", "node_modules/*", "__pycache__/*", "*.log", ".git/*"],
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
            self._handle_error(e, f"处理文件事件失败 {file_path}")

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
