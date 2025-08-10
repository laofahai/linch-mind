#!/usr/bin/env python3
"""
智能健康检查工具 - 提供完整的系统状态诊断
解决了"服务未注册"的误报问题，提供准确的系统状态
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "daemon"))

from config.core_config import get_core_config
from services.ipc_client import IPCClient


async def check_daemon_health():
    """通过IPC检查daemon健康状态（正确方式）"""
    print("🔍 检查Linch Mind系统健康状态...\n")
    
    try:
        # 1. 检查IPC连接
        client = IPCClient()
        connected = await client.connect()
        
        if not connected:
            print("❌ IPC连接失败 - Daemon未运行或IPC服务异常")
            return False
            
        print("✅ IPC连接正常")
        
        # 2. 通过IPC获取连接器状态
        try:
            response = await client.get("/api/connectors/status")
            if response.success:
                connectors = response.data.get("connectors", [])
                print(f"📊 发现 {len(connectors)} 个连接器:")
                
                healthy_count = 0
                for connector in connectors:
                    status = connector.get("running_state", "unknown")
                    health = connector.get("is_healthy", False)
                    name = connector.get("connector_id", "unknown")
                    
                    icon = "✅" if health else "❌"
                    print(f"  {icon} {name} - {status}")
                    
                    if health:
                        healthy_count += 1
                
                print(f"\n📈 系统健康度: {healthy_count}/{len(connectors)} 连接器正常")
                
            else:
                print(f"⚠️ 获取连接器状态失败: {response.error}")
                
        except Exception as e:
            print(f"⚠️ 连接器状态检查异常: {e}")
        
        # 3. 检查配置
        try:
            response = await client.get("/api/system/config")
            if response.success:
                print("✅ 系统配置正常")
            else:
                print("⚠️ 系统配置检查失败")
        except Exception as e:
            print(f"⚠️ 配置检查异常: {e}")
            
        await client.disconnect()
        print("\n🎉 健康检查完成")
        return True
        
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(check_daemon_health())