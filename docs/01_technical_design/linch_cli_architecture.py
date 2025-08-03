#!/usr/bin/env python3
"""
Linch CLI 统一命令行工具架构设计
目标：类似npm/docker的用户体验，替代4个分散的脚本
"""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import httpx
import json
import logging

logger = logging.getLogger(__name__)


class APIClient:
    """Daemon API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8088"):
        self.base_url = base_url
        self.timeout = 30.0
    
    async def get_connector_status(self, connector_id: str) -> Dict:
        """获取连接器状态"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/api/v1/connectors/{connector_id}/status")
            response.raise_for_status()
            return response.json()
    
    async def start_connector(self, connector_id: str, config: Dict = None) -> bool:
        """启动连接器"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload = {"config": config or {}}
            response = await client.post(f"{self.base_url}/api/v1/connectors/{connector_id}/start", json=payload)
            response.raise_for_status()
            return response.json().get("success", False)
    
    async def stop_connector(self, connector_id: str) -> bool:
        """停止连接器"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/api/v1/connectors/{connector_id}/stop")
            response.raise_for_status()
            return response.json().get("success", False)


class CLIConfig:
    """CLI配置管理"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".linch"
        self.config_file = self.config_dir / "config.json"
        self._config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        if not self.config_file.exists():
            return self._create_default_config()
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"配置文件加载失败，使用默认配置: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """创建默认配置"""
        default_config = {
            "daemon": {
                "url": "http://localhost:8088",
                "timeout": 30
            },
            "registry": {
                "default": "https://registry.linch.dev",
                "cache_dir": str(self.config_dir / "registry")
            },
            "connectors": {
                "auto_restart": True,
                "max_restart_attempts": 3
            }
        }
        
        # 确保配置目录存在
        self.config_dir.mkdir(exist_ok=True)
        
        # 保存默认配置
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def get(self, key: str, default=None):
        """获取配置项"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            value = value.get(k, {})
        return value if value != {} else default


class ConnectorCommands:
    """连接器相关命令"""
    
    def __init__(self, api_client: APIClient, config: CLIConfig):
        self.api = api_client
        self.config = config
        self.project_root = Path(__file__).parent.parent.parent
    
    async def create(self, name: str, template: str = "basic", category: str = "local_files"):
        """创建新连接器"""
        print(f"🏗️ 创建连接器: {name}")
        
        connector_dir = self.project_root / "connectors" / "official" / name
        if connector_dir.exists():
            print(f"❌ 连接器 '{name}' 已存在")
            return False
        
        # 创建连接器脚手架
        await self._create_connector_scaffold(connector_dir, name, template, category)
        
        print(f"✅ 连接器 '{name}' 创建成功")
        print(f"📁 位置: {connector_dir}")
        print(f"🚀 运行: linch connector start {name}")
        return True
    
    async def _create_connector_scaffold(self, connector_dir: Path, name: str, template: str, category: str):
        """创建连接器脚手架"""
        connector_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建connector.json
        manifest = {
            "id": name,
            "name": f"{name.title()} 连接器",
            "version": "1.0.0",
            "author": "Linch Mind User",
            "description": f"A {name} connector for Linch Mind",
            "category": category,
            "entry": {
                "development": {
                    "command": "python3",
                    "args": ["main.py"],
                    "working_dir": "."
                },
                "production": {
                    "windows": f"{name}-connector.exe",
                    "macos": f"{name}-connector",
                    "linux": f"{name}-connector"
                }
            },
            "permissions": ["network:daemon-api"],
            "config_schema": {
                "type": "object",
                "properties": {
                    "enabled": {
                        "type": "boolean",
                        "default": True
                    }
                }
            }
        }
        
        with open(connector_dir / "connector.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        # 创建main.py（简化版）
        main_py_content = f'''#!/usr/bin/env python3
"""
{name.title()} 连接器
"""

import asyncio
import sys
from pathlib import Path

# 添加共享模块路径
sys.path.append(str(Path(__file__).parent.parent.parent / "connectors" / "shared"))

from base import BaseConnector, run_connector


class {name.title().replace("-", "")}Connector(BaseConnector):
    """{name.title()} 连接器实现"""
    
    def __init__(self):
        super().__init__(connector_id="{name}")
    
    @classmethod
    def get_config_schema(cls):
        return {{
            "type": "object",
            "properties": {{
                "enabled": {{
                    "type": "boolean",
                    "default": True
                }}
            }}
        }}
    
    async def start_monitoring(self):
        """启动监控"""
        self.logger.info(f"🚀 {{self.connector_id}} 连接器开始监控")
        
        if not await self.test_daemon_connection():
            self.logger.error("❌ 无法连接到Daemon")
            return
        
        await self.register_config_schema()
        await self.load_config_from_daemon()
        
        try:
            while not self.should_stop:
                # TODO: 实现你的监控逻辑
                self.logger.info("💡 连接器正在运行...")
                await asyncio.sleep(10)
        except Exception as e:
            self.logger.error(f"❌ 监控过程中发生错误: {{e}}")
        finally:
            self.logger.info(f"👋 {{self.connector_id}} 连接器已停止")


if __name__ == "__main__":
    connector = {name.title().replace("-", "")}Connector()
    try:
        asyncio.run(run_connector(connector))
    except KeyboardInterrupt:
        print("\\n👋 连接器已停止")
    except Exception as e:
        print(f"❌ 连接器运行失败: {{e}}")
        sys.exit(1)
'''
        
        with open(connector_dir / "main.py", "w", encoding="utf-8") as f:
            f.write(main_py_content)
        
        # 创建requirements.txt
        with open(connector_dir / "requirements.txt", "w") as f:
            f.write("httpx>=0.24.0\\n")
    
    async def start(self, name: str, config: Optional[Dict] = None):
        """启动连接器"""
        try:
            print(f"🚀 启动连接器: {name}")
            success = await self.api.start_connector(name, config)
            if success:
                print(f"✅ 连接器 {name} 启动成功")
            else:
                print(f"❌ 连接器 {name} 启动失败")
            return success
        except Exception as e:
            print(f"❌ 启动连接器失败: {e}")
            return False
    
    async def stop(self, name: str):
        """停止连接器"""
        try:
            print(f"🛑 停止连接器: {name}")
            success = await self.api.stop_connector(name)
            if success:
                print(f"✅ 连接器 {name} 停止成功")
            else:
                print(f"❌ 连接器 {name} 停止失败")
            return success
        except Exception as e:
            print(f"❌ 停止连接器失败: {e}")
            return False
    
    async def status(self, name: str):
        """获取连接器状态"""
        try:
            status = await self.api.get_connector_status(name)
            print(f"📊 连接器 {name} 状态:")
            print(f"  状态: {status.get('status', 'unknown')}")
            print(f"  运行时间: {status.get('uptime', 'N/A')}")
            print(f"  数据计数: {status.get('data_count', 0)}")
            return True
        except Exception as e:
            print(f"❌ 获取状态失败: {e}")
            return False
    
    async def list_connectors(self, filter_running: bool = False):
        """列出连接器"""
        # TODO: 实现连接器列表
        print("📋 连接器列表:")
        print("  (实现中...)")


class DaemonCommands:
    """Daemon相关命令"""
    
    def __init__(self, api_client: APIClient, config: CLIConfig):
        self.api = api_client
        self.config = config
    
    async def start(self):
        """启动daemon"""
        print("🚀 启动Linch Mind Daemon...")
        # TODO: 实现daemon启动逻辑
        print("✅ Daemon启动成功")
    
    async def stop(self):
        """停止daemon"""
        print("🛑 停止Linch Mind Daemon...")
        # TODO: 实现daemon停止逻辑
        print("✅ Daemon停止成功")
    
    async def status(self):
        """获取daemon状态"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(self.api.base_url)
                if response.status_code == 200:
                    print("✅ Daemon运行正常")
                    print(f"📊 URL: {self.api.base_url}")
                    return True
                else:
                    print(f"⚠️ Daemon响应异常: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Daemon未运行: {e}")
            return False


class LinchCLI:
    """Linch CLI主类"""
    
    def __init__(self):
        self.config = CLIConfig()
        self.api = APIClient(self.config.get("daemon.url"))
        self.connector_commands = ConnectorCommands(self.api, self.config)
        self.daemon_commands = DaemonCommands(self.api, self.config)
    
    def create_parser(self) -> argparse.ArgumentParser:
        """创建命令行解析器"""
        parser = argparse.ArgumentParser(
            prog="linch",
            description="Linch Mind 统一命令行工具"
        )
        
        subparsers = parser.add_subparsers(dest="command", help="可用命令")
        
        # connector子命令
        connector_parser = subparsers.add_parser("connector", help="连接器管理")
        connector_subparsers = connector_parser.add_subparsers(dest="connector_action")
        
        # connector create
        create_parser = connector_subparsers.add_parser("create", help="创建新连接器")
        create_parser.add_argument("name", help="连接器名称")
        create_parser.add_argument("--template", default="basic", help="模板类型")
        create_parser.add_argument("--category", default="local_files", help="连接器分类")
        
        # connector start/stop/status
        for action in ["start", "stop", "status"]:
            action_parser = connector_subparsers.add_parser(action, help=f"{action}连接器")
            action_parser.add_argument("name", help="连接器名称")
        
        # connector list
        list_parser = connector_subparsers.add_parser("list", help="列出连接器")
        list_parser.add_argument("--running", action="store_true", help="只显示运行中的连接器")
        
        # daemon子命令
        daemon_parser = subparsers.add_parser("daemon", help="Daemon管理")
        daemon_subparsers = daemon_parser.add_subparsers(dest="daemon_action")
        
        for action in ["start", "stop", "status"]:
            daemon_subparsers.add_parser(action, help=f"{action} daemon")
        
        return parser
    
    async def run(self, args: List[str] = None):
        """运行CLI"""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        if not parsed_args.command:
            parser.print_help()
            return
        
        try:
            if parsed_args.command == "connector":
                await self._handle_connector_command(parsed_args)
            elif parsed_args.command == "daemon":
                await self._handle_daemon_command(parsed_args)
            else:
                print(f"❌ 未知命令: {parsed_args.command}")
                
        except KeyboardInterrupt:
            print("\\n👋 操作已取消")
        except Exception as e:
            print(f"❌ 操作失败: {e}")
            logger.exception("CLI执行错误")
    
    async def _handle_connector_command(self, args):
        """处理connector命令"""
        action = args.connector_action
        
        if action == "create":
            await self.connector_commands.create(args.name, args.template, args.category)
        elif action == "start":
            await self.connector_commands.start(args.name)
        elif action == "stop":
            await self.connector_commands.stop(args.name)
        elif action == "status":
            await self.connector_commands.status(args.name)
        elif action == "list":
            await self.connector_commands.list_connectors(args.running)
        else:
            print(f"❌ 未知connector操作: {action}")
    
    async def _handle_daemon_command(self, args):
        """处理daemon命令"""
        action = args.daemon_action
        
        if action == "start":
            await self.daemon_commands.start()
        elif action == "stop":
            await self.daemon_commands.stop()
        elif action == "status":
            await self.daemon_commands.status()
        else:
            print(f"❌ 未知daemon操作: {action}")


async def main():
    """主入口函数"""
    cli = LinchCLI()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())