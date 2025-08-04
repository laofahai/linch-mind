#!/usr/bin/env python3
"""
Linch Mind 剪贴板连接器
独立进程，监控剪贴板变化并推送数据到Daemon
Session 4 补充实现 - 重构版本

fix: 修复剪贴板监控的内存泄漏问题，优化资源管理
"""

import asyncio
import os
import sys
from typing import Dict, Any
import logging
import time

# 优雅处理pyperclip依赖
try:
    import pyperclip

    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False
    pyperclip = None


# 导入基类
from shared.base import BaseConnector, run_connector


class ClipboardConnector(BaseConnector):
    """剪贴板连接器 - 监控剪贴板变化并推送到Daemon"""

    @classmethod
    def get_required_dependencies(cls):
        """声明必需的依赖"""
        return ["pyperclip"]

    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """剪贴板连接器配置schema"""
        return {
            "type": "object",
            "title": "剪贴板连接器配置",
            "description": "配置剪贴板监控的检查间隔和内容过滤规则",
            "properties": {
                "check_interval": {
                    "type": "number",
                    "title": "检查间隔 (秒)",
                    "description": "剪贴板内容检查的间隔时间",
                    "default": 1.0,
                    "minimum": 0.5,
                    "maximum": 10.0,
                    "ui_component": "number_input",
                },
                "min_content_length": {
                    "type": "integer",
                    "title": "最小内容长度",
                    "description": "过滤掉短于此长度的剪贴板内容",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 100,
                    "ui_component": "number_input",
                },
                "max_content_length": {
                    "type": "integer",
                    "title": "最大内容长度",
                    "description": "超过此长度的内容将被截断",
                    "default": 50000,
                    "minimum": 1000,
                    "maximum": 100000,
                    "ui_component": "number_input",
                },
                "content_filters": {
                    "type": "object",
                    "title": "内容过滤设置",
                    "properties": {
                        "filter_urls": {
                            "type": "boolean",
                            "title": "过滤URL",
                            "description": "是否跳过纯URL内容",
                            "default": False,
                            "ui_component": "switch",
                        },
                        "filter_sensitive": {
                            "type": "boolean",
                            "title": "过滤敏感内容",
                            "description": "跳过可能包含密码或密钥的内容",
                            "default": True,
                            "ui_component": "switch",
                        },
                    },
                },
            },
            "required": ["check_interval", "min_content_length", "max_content_length"],
        }

    def __init__(self, daemon_url: str = None):
        super().__init__("clipboard", daemon_url)
        self.last_clipboard_content = ""
        self.check_interval = 1.0  # 将从配置加载

    async def _load_clipboard_config(self):
        """加载剪贴板特定配置"""
        await self.load_config_from_daemon()
        self.check_interval = self.get_config("check_interval", 1.0)
        self.logger.info(f"检查间隔: {self.check_interval}秒")

    async def _process_clipboard_change(self, content: str):
        """处理剪贴板变化"""
        try:
            # 过滤太短或太长的内容
            min_length = self.get_config("min_content_length", 5)
            if len(content.strip()) < min_length:
                self.logger.debug("跳过太短的剪贴板内容")
                return

            max_length = self.get_config("max_content_length", 50000)
            if len(content) > max_length:
                self.logger.debug("剪贴板内容过长，截断处理")
                content = content[:max_length] + "\n... (内容已截断)"

            # 构造数据项 - 使用基类方法
            metadata = {
                "content_length": len(content),
                "content_type": self._detect_content_type(content),
            }
            data_item = self.create_data_item(content, metadata)

            # 推送到Daemon - 使用基类方法
            success = await self.push_to_daemon(data_item)
            if success:
                self.logger.info(f"✅ 处理剪贴板变化: {len(content)} 字符")
            else:
                self.logger.error(f"❌ 推送剪贴板数据失败")

        except Exception as e:
            self._handle_error(e, "处理剪贴板变化失败")

    def _detect_content_type(self, content: str) -> str:
        """检测内容类型"""
        content_lower = content.lower().strip()

        if content_lower.startswith(("http://", "https://")):
            return "url"
        elif content_lower.startswith(("def ", "function ", "class ", "import ")):
            return "code"
        elif "@" in content and "." in content:
            return "email_or_contact"
        elif any(
            keyword in content_lower for keyword in ["todo", "task", "deadline", "截止"]
        ):
            return "task_or_reminder"
        else:
            return "text"

    async def start_monitoring(self):
        """启动剪贴板监控"""
        self.logger.info("启动剪贴板监控...")

        # 检查依赖
        dep_status = self.check_dependencies()
        if dep_status["status"] != "ok":
            self._handle_error(
                Exception(dep_status['message']),
                f"依赖检查失败，安装命令: {dep_status.get('install_command', 'pip install pyperclip')}",
                critical=True
            )
            return

        if not PYPERCLIP_AVAILABLE:
            self._handle_error(
                Exception("pyperclip库不可用"),
                "无法监控剪贴板，请运行: pip install pyperclip",
                critical=True
            )
            return

        # 加载配置
        await self._load_clipboard_config()

        # 测试Daemon连接
        await self.test_daemon_connection()

        # 启动配置监控任务
        config_monitor_task = asyncio.create_task(self.start_config_monitoring())

        # 获取初始剪贴板内容
        try:
            self.last_clipboard_content = pyperclip.paste()
            self.logger.info(f"初始剪贴板内容长度: {len(self.last_clipboard_content)}")
        except Exception as e:
            self.logger.error(f"获取初始剪贴板内容失败: {e}")
            self.last_clipboard_content = ""

        self.logger.info("剪贴板监控已启动")

        try:
            # 监控循环
            while not self.should_stop:
                try:
                    if not PYPERCLIP_AVAILABLE:
                        self.logger.error("pyperclip不可用，停止监控")
                        break

                    current_content = pyperclip.paste()

                    # 检查内容是否变化
                    if current_content != self.last_clipboard_content:
                        self.logger.info(
                            f"📋 检测到剪贴板变化: {len(current_content)} 字符"
                        )
                        await self._process_clipboard_change(current_content)
                        self.last_clipboard_content = current_content

                    await asyncio.sleep(self.check_interval)

                except Exception as e:
                    await self._handle_async_error(e, "监控剪贴板时发生错误", retry_delay=5.0)

        except KeyboardInterrupt:
            self.logger.info("收到中断信号")
        finally:
            self.logger.info("剪贴板监控已停止")
            config_monitor_task.cancel()


if __name__ == "__main__":
    try:
        # 创建连接器实例
        daemon_url = os.getenv("DAEMON_URL")  # None表示使用配置文件
        connector = ClipboardConnector(daemon_url)

        # 使用基类的运行方法
        asyncio.run(run_connector(connector))
    except KeyboardInterrupt:
        print("进程被中断")
    except Exception as e:
        print(f"连接器运行错误: {e}")
        sys.exit(1)
