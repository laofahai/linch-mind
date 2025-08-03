#!/usr/bin/env python3
"""
Linch Mind 统一CLI工具
替换分散的脚本：dev.sh, connector-dev.py, package-connector.py, build-connectors.py

使用示例:
  linch connector list                     # 列出所有连接器
  linch connector create obsidian          # 创建新连接器
  linch connector start filesystem         # 启动连接器
  linch connector stop filesystem          # 停止连接器
  linch connector logs filesystem          # 查看连接器日志
  linch daemon start                       # 启动daemon
  linch daemon status                      # 查看daemon状态
  linch dev start                          # 开发模式启动
"""

import asyncio
import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import List, Optional
import aiohttp
import time

# 设置项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 导入统一配置
sys.path.insert(0, str(PROJECT_ROOT / "connectors"))
from shared.config import get_daemon_url, get_daemon_port

DAEMON_URL = get_daemon_url()

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LinchCLI:
    """Linch Mind 统一CLI工具"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.connectors_dir = self.project_root / "connectors"
        self.daemon_dir = self.project_root / "daemon"
    
    async def main(self):
        """主入口"""
        parser = self._create_parser()
        args = parser.parse_args()
        
        if hasattr(args, 'func'):
            try:
                await args.func(args)
            except KeyboardInterrupt:
                print("\n🛑 操作被用户取消")
                sys.exit(1)
            except Exception as e:
                logger.error(f"执行失败: {e}")
                sys.exit(1)
        else:
            parser.print_help()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """创建命令行解析器"""
        parser = argparse.ArgumentParser(
            prog='linch',
            description='Linch Mind 统一CLI工具',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  linch connector list
  linch connector start filesystem
  linch connector logs filesystem --follow
  linch daemon start
  linch dev start
            """
        )
        
        parser.add_argument('--version', action='version', version='linch 1.0.0')
        parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
        
        subparsers = parser.add_subparsers(dest='command', help='可用命令')
        
        # 连接器管理命令
        self._add_connector_commands(subparsers)
        
        # Daemon管理命令
        self._add_daemon_commands(subparsers)
        
        # 开发工具命令
        self._add_dev_commands(subparsers)
        
        # 配置管理命令
        self._add_config_commands(subparsers)
        
        return parser
    
    def _add_connector_commands(self, subparsers):
        """添加连接器管理命令"""
        connector_parser = subparsers.add_parser('connector', help='连接器管理')
        connector_subparsers = connector_parser.add_subparsers(dest='connector_action')
        
        # list - 列出连接器
        list_parser = connector_subparsers.add_parser('list', help='列出所有连接器')
        list_parser.add_argument('--running', action='store_true', help='只显示运行中的连接器')
        list_parser.set_defaults(func=self.cmd_connector_list)
        
        # start - 启动连接器
        start_parser = connector_subparsers.add_parser('start', help='启动连接器')
        start_parser.add_argument('connector_id', help='连接器ID')
        start_parser.add_argument('--config', help='配置文件路径')
        start_parser.set_defaults(func=self.cmd_connector_start)
        
        # stop - 停止连接器
        stop_parser = connector_subparsers.add_parser('stop', help='停止连接器')
        stop_parser.add_argument('connector_id', help='连接器ID')
        stop_parser.set_defaults(func=self.cmd_connector_stop)
        
        # restart - 重启连接器
        restart_parser = connector_subparsers.add_parser('restart', help='重启连接器')
        restart_parser.add_argument('connector_id', help='连接器ID')
        restart_parser.set_defaults(func=self.cmd_connector_restart)
        
        # status - 连接器状态
        status_parser = connector_subparsers.add_parser('status', help='查看连接器状态')
        status_parser.add_argument('connector_id', nargs='?', help='连接器ID（可选）')
        status_parser.set_defaults(func=self.cmd_connector_status)
        
        # logs - 查看日志
        logs_parser = connector_subparsers.add_parser('logs', help='查看连接器日志')
        logs_parser.add_argument('connector_id', help='连接器ID')
        logs_parser.add_argument('--follow', '-f', action='store_true', help='实时跟踪日志')
        logs_parser.add_argument('--lines', '-n', type=int, default=50, help='显示行数')
        logs_parser.set_defaults(func=self.cmd_connector_logs)
        
        # create - 创建连接器
        create_parser = connector_subparsers.add_parser('create', help='创建新连接器')
        create_parser.add_argument('connector_id', help='连接器ID')
        create_parser.add_argument('--template', default='basic', help='模板类型')
        create_parser.add_argument('--author', help='作者名称')
        create_parser.set_defaults(func=self.cmd_connector_create)
    
    def _add_daemon_commands(self, subparsers):
        """添加Daemon管理命令"""
        daemon_parser = subparsers.add_parser('daemon', help='Daemon管理')
        daemon_subparsers = daemon_parser.add_subparsers(dest='daemon_action')
        
        # start - 启动daemon
        start_parser = daemon_subparsers.add_parser('start', help='启动daemon')
        start_parser.add_argument('--port', type=int, default=get_daemon_port(), help='端口号')
        start_parser.add_argument('--background', '-d', action='store_true', help='后台运行')
        start_parser.set_defaults(func=self.cmd_daemon_start)
        
        # stop - 停止daemon
        stop_parser = daemon_subparsers.add_parser('stop', help='停止daemon')
        stop_parser.set_defaults(func=self.cmd_daemon_stop)
        
        # status - daemon状态
        status_parser = daemon_subparsers.add_parser('status', help='查看daemon状态')
        status_parser.set_defaults(func=self.cmd_daemon_status)
        
        # restart - 重启daemon
        restart_parser = daemon_subparsers.add_parser('restart', help='重启daemon')
        restart_parser.set_defaults(func=self.cmd_daemon_restart)
    
    def _add_dev_commands(self, subparsers):
        """添加开发工具命令"""
        dev_parser = subparsers.add_parser('dev', help='开发工具')
        dev_subparsers = dev_parser.add_subparsers(dest='dev_action')
        
        # start - 开发模式启动
        start_parser = dev_subparsers.add_parser('start', help='开发模式启动')
        start_parser.add_argument('--connector', help='指定启动的连接器')
        start_parser.set_defaults(func=self.cmd_dev_start)
        
        # test - 运行测试
        test_parser = dev_subparsers.add_parser('test', help='运行测试')
        test_parser.add_argument('--connector', help='测试指定连接器')
        test_parser.set_defaults(func=self.cmd_dev_test)
        
        # build - 构建连接器
        build_parser = dev_subparsers.add_parser('build', help='构建连接器')
        build_parser.add_argument('connector_id', nargs='?', help='连接器ID（可选）')
        build_parser.set_defaults(func=self.cmd_dev_build)
    
    def _add_config_commands(self, subparsers):
        """添加配置管理命令"""
        config_parser = subparsers.add_parser('config', help='配置管理')
        config_subparsers = config_parser.add_subparsers(dest='config_action')
        
        # show - 显示配置
        show_parser = config_subparsers.add_parser('show', help='显示配置')
        show_parser.set_defaults(func=self.cmd_config_show)
        
        # set - 设置配置
        set_parser = config_subparsers.add_parser('set', help='设置配置')
        set_parser.add_argument('key', help='配置项（如：daemon.port）')
        set_parser.add_argument('value', help='配置值')
        set_parser.set_defaults(func=self.cmd_config_set)
        
        # init - 初始化配置
        init_parser = config_subparsers.add_parser('init', help='初始化配置文件')
        init_parser.add_argument('--force', action='store_true', help='强制重写现有配置')
        init_parser.set_defaults(func=self.cmd_config_init)
    
    # === Connector Commands ===
    
    async def cmd_connector_list(self, args):
        """列出连接器"""
        try:
            async with aiohttp.ClientSession() as session:
                if args.running:
                    url = f"{DAEMON_URL}/api/v1/connectors/running"
                else:
                    url = f"{DAEMON_URL}/api/v1/connectors/"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        connectors = await response.json()
                        self._print_connector_table(connectors, args.running)
                    else:
                        print(f"❌ 获取连接器列表失败: {response.status}")
        except aiohttp.ClientError:
            print("❌ 无法连接到daemon，请先启动daemon")
    
    async def cmd_connector_start(self, args):
        """启动连接器"""
        config = {}
        if args.config:
            with open(args.config) as f:
                config = json.load(f)
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{DAEMON_URL}/api/v1/connectors/{args.connector_id}/start"
                async with session.post(url, json=config) as response:
                    if response.status == 200:
                        print(f"✅ 连接器 {args.connector_id} 启动成功")
                    else:
                        result = await response.json()
                        print(f"❌ 启动失败: {result.get('detail', 'Unknown error')}")
        except aiohttp.ClientError:
            print("❌ 无法连接到daemon")
    
    async def cmd_connector_stop(self, args):
        """停止连接器"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{DAEMON_URL}/api/v1/connectors/{args.connector_id}/stop"
                async with session.post(url) as response:
                    if response.status == 200:
                        print(f"✅ 连接器 {args.connector_id} 停止成功")
                    else:
                        result = await response.json()
                        print(f"❌ 停止失败: {result.get('detail', 'Unknown error')}")
        except aiohttp.ClientError:
            print("❌ 无法连接到daemon")
    
    async def cmd_connector_restart(self, args):
        """重启连接器"""
        print(f"🔄 重启连接器 {args.connector_id}...")
        await self.cmd_connector_stop(args)
        await asyncio.sleep(1)
        await self.cmd_connector_start(args)
    
    async def cmd_connector_status(self, args):
        """查看连接器状态"""
        try:
            async with aiohttp.ClientSession() as session:
                if args.connector_id:
                    url = f"{DAEMON_URL}/api/v1/connectors/{args.connector_id}/status"
                    async with session.get(url) as response:
                        if response.status == 200:
                            connector = await response.json()
                            self._print_connector_detail(connector)
                        else:
                            print(f"❌ 连接器 {args.connector_id} 不存在")
                else:
                    url = f"{DAEMON_URL}/api/v1/connectors/"
                    async with session.get(url) as response:
                        connectors = await response.json()
                        self._print_connector_table(connectors, False)
        except aiohttp.ClientError:
            print("❌ 无法连接到daemon")
    
    async def cmd_connector_logs(self, args):
        """查看连接器日志"""
        # TODO: 实现日志查看功能
        print(f"📄 查看连接器 {args.connector_id} 日志")
        print("（日志功能开发中...）")
    
    async def cmd_connector_create(self, args):
        """创建新连接器"""
        connector_dir = self.connectors_dir / "official" / args.connector_id
        
        if connector_dir.exists():
            print(f"❌ 连接器 {args.connector_id} 已存在")
            return
        
        # 创建连接器目录和基础文件
        connector_dir.mkdir(parents=True)
        
        # 创建connector.json
        config = {
            "id": args.connector_id,
            "name": args.connector_id.title(),
            "version": "1.0.0",
            "author": args.author or "Unknown",
            "description": f"{args.connector_id} connector",
            "category": "general",
            "entry": {
                "development": {
                    "args": ["main.py"],
                    "working_dir": "."
                },
                "production": {
                    "linux": f"{args.connector_id}",
                    "macos": f"{args.connector_id}",
                    "windows": f"{args.connector_id}.exe"
                }
            },
            "permissions": [
                "filesystem:read",
                "network:request"
            ],
            "config_schema": {},
            "capabilities": {}
        }
        
        with open(connector_dir / "connector.json", "w") as f:
            json.dump(config, f, indent=2)
        
        # 创建main.py模板
        main_template = f'''"""
{args.connector_id.title()} Connector for Linch Mind
"""

import asyncio
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class {args.connector_id.title()}Connector:
    """{ args.connector_id.title() } 连接器"""
    
    def __init__(self):
        self.connector_id = os.getenv("LINCH_MIND_CONNECTOR_ID", "{args.connector_id}")
        self.daemon_url = os.getenv("LINCH_MIND_DAEMON_URL") or get_daemon_url()
        
        logger.info(f"{ args.connector_id.title() }Connector 初始化完成")
    
    async def start(self):
        """启动连接器"""
        logger.info(f"启动 {args.connector_id} 连接器")
        
        # TODO: 实现连接器逻辑
        while True:
            await asyncio.sleep(10)
            logger.info(f"{args.connector_id} 连接器运行中...")
    
    async def stop(self):
        """停止连接器"""
        logger.info(f"停止 {args.connector_id} 连接器")


async def main():
    """主函数"""
    logging.basicConfig(level=logging.INFO)
    
    connector = {args.connector_id.title()}Connector()
    
    try:
        await connector.start()
    except KeyboardInterrupt:
        await connector.stop()
        logger.info("连接器已停止")


if __name__ == "__main__":
    asyncio.run(main())
'''
        
        with open(connector_dir / "main.py", "w") as f:
            f.write(main_template)
        
        print(f"✅ 连接器 {args.connector_id} 创建成功")
        print(f"📁 位置: {connector_dir}")
        print(f"📝 配置文件: {connector_dir / 'connector.json'}")
        print(f"🐍 主文件: {connector_dir / 'main.py'}")
    
    # === Daemon Commands ===
    
    async def cmd_daemon_start(self, args):
        """启动daemon"""
        print("🚀 启动Linch Mind Daemon...")
        
        cmd = [
            "poetry", "run", "python", "-m", "uvicorn",
            "api.main:app",
            "--host", "0.0.0.0",
            "--port", str(args.port),
            "--reload"
        ]
        
        if args.background:
            # 后台运行
            process = subprocess.Popen(
                cmd,
                cwd=self.daemon_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"✅ Daemon已在后台启动 (PID: {process.pid})")
        else:
            # 前台运行
            subprocess.run(cmd, cwd=self.daemon_dir)
    
    async def cmd_daemon_stop(self, args):
        """停止daemon"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{DAEMON_URL}/shutdown"
                async with session.post(url) as response:
                    if response.status == 200:
                        print("✅ Daemon已停止")
                    else:
                        print("❌ 停止Daemon失败")
        except aiohttp.ClientError:
            print("❌ Daemon未运行或无法连接")
    
    async def cmd_daemon_status(self, args):
        """查看daemon状态"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{DAEMON_URL}/health"
                async with session.get(url) as response:
                    if response.status == 200:
                        health = await response.json()
                        print("✅ Daemon运行正常")
                        print(f"📊 状态: {health}")
                    else:
                        print("❌ Daemon运行异常")
        except aiohttp.ClientError:
            print("❌ Daemon未运行")
    
    async def cmd_daemon_restart(self, args):
        """重启daemon"""
        print("🔄 重启Daemon...")
        await self.cmd_daemon_stop(args)
        await asyncio.sleep(2)
        await self.cmd_daemon_start(args)
    
    # === Dev Commands ===
    
    async def cmd_dev_start(self, args):
        """开发模式启动"""
        print("🛠️ 启动开发模式...")
        
        # 启动daemon
        daemon_process = subprocess.Popen([
            "poetry", "run", "python", "-m", "uvicorn",
            "api.main:app", "--reload", "--port", str(get_daemon_port())
        ], cwd=self.daemon_dir)
        
        # 等待daemon启动
        await asyncio.sleep(3)
        
        # 如果指定了连接器，启动它
        if args.connector:
            await self.cmd_connector_start(type('Args', (), {'connector_id': args.connector, 'config': None})())
        
        try:
            daemon_process.wait()
        except KeyboardInterrupt:
            daemon_process.terminate()
            print("\n🛑 开发模式已停止")
    
    async def cmd_dev_test(self, args):
        """运行测试"""
        print("🧪 运行测试...")
        
        if args.connector:
            # 测试指定连接器
            test_cmd = ["poetry", "run", "pytest", f"tests/test_{args.connector}.py", "-v"]
        else:
            # 运行所有测试
            test_cmd = ["poetry", "run", "pytest", "tests/", "-v"]
        
        subprocess.run(test_cmd, cwd=self.project_root)
    
    async def cmd_dev_build(self, args):
        """构建连接器"""
        if args.connector_id:
            print(f"🔨 构建连接器 {args.connector_id}...")
            # TODO: 实现单个连接器构建
        else:
            print("🔨 构建所有连接器...")
            # TODO: 实现批量构建
        
        print("（构建功能开发中...）")
    
    # === Config Commands ===
    
    async def cmd_config_show(self, args):
        """显示配置"""
        from shared.config import LinchConfig
        config_manager = LinchConfig()
        config = config_manager.get_config()
        
        print("📋 Linch Mind 配置:")
        print(f"📁 配置文件位置: {config_manager.config_file}")
        print()
        print("🔧 当前配置:")
        print(json.dumps(config, indent=2, ensure_ascii=False))
    
    async def cmd_config_set(self, args):
        """设置配置"""
        from shared.config import LinchConfig
        config_manager = LinchConfig()
        
        # 处理数值类型
        value = args.value
        if value.isdigit():
            value = int(value)
        elif value.lower() in ['true', 'false']:
            value = value.lower() == 'true'
        
        config_manager.update_config(args.key, value)
        print(f"✅ 配置已更新: {args.key} = {value}")
    
    async def cmd_config_init(self, args):
        """初始化配置文件"""
        from shared.config import LinchConfig
        config_manager = LinchConfig()
        
        if config_manager.config_file.exists() and not args.force:
            print(f"❌ 配置文件已存在: {config_manager.config_file}")
            print("使用 --force 强制重写")
            return
        
        # 重新创建配置文件
        if config_manager.config_file.exists():
            config_manager.config_file.unlink()
        
        config_manager._ensure_config_exists()
        print(f"✅ 配置文件已初始化: {config_manager.config_file}")
        print("🔧 默认配置:")
        await self.cmd_config_show(args)
    
    # === Helper Methods ===
    
    def _print_connector_table(self, connectors: List[dict], running_only: bool = False):
        """打印连接器表格"""
        if not connectors:
            print("📭 没有找到连接器")
            return
        
        # 表头
        print(f"{'ID':<15} {'名称':<20} {'状态':<15} {'数据量':<10}")
        print("-" * 60)
        
        # 内容
        for connector in connectors:
            status = connector.get('status', 'unknown')
            status_icon = {
                'running': '🟢',
                'stopped': '🔴',
                'error': '🟠'
            }.get(status, '⚪')
            
            data_count = connector.get('data_count', 0)
            print(f"{connector['id']:<15} {connector['name']:<20} {status_icon}{status:<14} {data_count:<10}")
    
    def _print_connector_detail(self, connector: dict):
        """打印连接器详细信息"""
        print(f"📋 连接器详情: {connector['id']}")
        print(f"   名称: {connector['name']}")
        print(f"   描述: {connector['description']}")
        print(f"   状态: {connector.get('status', 'unknown')}")
        print(f"   数据量: {connector.get('data_count', 0)}")


def main():
    """CLI入口点"""
    cli = LinchCLI()
    asyncio.run(cli.main())


if __name__ == "__main__":
    main()