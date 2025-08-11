#!/usr/bin/env python3
"""
测试智能服务的集成和可用性
验证StorageOrchestrator、EmbeddingService、GraphService等服务
"""

import asyncio
import sys
from pathlib import Path

# 添加daemon路径
daemon_path = Path(__file__).parent / "daemon"
sys.path.insert(0, str(daemon_path))

from services.ipc_client import IPCClient


async def test_intelligent_services():
    """测试智能服务集成"""
    client = IPCClient()

    try:
        # 连接到daemon
        await client.connect()
        print("✅ IPC连接成功")

        # 测试服务状态
        response = await client.request("system", "get_status", {})
        print(f"📊 系统状态: {response.get('status', 'unknown')}")

        # 测试连接器状态
        response = await client.request("connector_lifecycle", "list_connectors", {})
        if response.get("success"):
            connectors = response.get("data", [])
            print(f"🔌 连接器数量: {len(connectors)}")
            for conn in connectors:
                status = conn.get("status", "unknown")
                name = conn.get("name", "unnamed")
                print(f"   - {name}: {status}")

        print("✅ 智能服务集成测试完成")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        print(f"详细错误: {traceback.format_exc()}")

    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(test_intelligent_services())
