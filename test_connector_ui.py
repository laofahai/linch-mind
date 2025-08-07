#!/usr/bin/env python3
"""
测试连接器UI交互的脚本
"""
import sys
import os
import json
import asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), 'daemon'))

async def test_ipc_connector_list():
    """测试IPC连接器列表功能"""
    try:
        from daemon.services.ipc_client import IPCClient
        from daemon.services.ipc_protocol import IPCRequest
        
        print("=== IPC 连接器列表测试 ===")
        
        # 创建IPC客户端
        client = IPCClient()
        await client.connect()
        print("✅ IPC客户端连接成功")
        
        # 测试获取连接器列表
        request = IPCRequest(
            method="GET",
            path="/connector-lifecycle/connectors",
            data=None
        )
        
        response = await client.send_request(request)
        print(f"📊 响应状态: {response.success}")
        
        if response.success and response.data:
            connectors = response.data.get("connectors", [])
            print(f"📊 连接器数量: {len(connectors)}")
            
            for connector in connectors:
                print(f"\n🔗 连接器信息:")
                print(f"   ID: {connector.get('connector_id')}")
                print(f"   名称: {connector.get('display_name')}")
                print(f"   状态: {connector.get('state')}")  # 注意这里是state不是status
                print(f"   启用: {connector.get('enabled')}")
                print(f"   数据条数: {connector.get('data_count')}")
                if connector.get('error_message'):
                    print(f"   错误信息: {connector.get('error_message')}")
        else:
            print(f"❌ 获取连接器列表失败: {response.error_message}")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ IPC连接器列表测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_connector_creation():
    """测试连接器创建"""
    try:
        from daemon.services.ipc_client import IPCClient
        from daemon.services.ipc_protocol import IPCRequest
        
        print("\n=== 连接器创建测试 ===")
        
        # 创建IPC客户端
        client = IPCClient()
        await client.connect()
        
        # 测试创建连接器
        create_data = {
            "connector_id": "test_clipboard",
            "display_name": "测试剪贴板连接器",
            "config": {
                "enabled": True
            }
        }
        
        request = IPCRequest(
            method="POST",
            path="/connector-lifecycle/connectors",
            data=create_data
        )
        
        response = await client.send_request(request)
        print(f"📊 创建响应状态: {response.success}")
        
        if response.success:
            print("✅ 连接器创建成功")
            if response.data and "connector" in response.data:
                connector = response.data["connector"]
                print(f"   新连接器ID: {connector.get('connector_id')}")
                print(f"   显示名称: {connector.get('display_name')}")
        else:
            print(f"❌ 连接器创建失败: {response.error_message}")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ 连接器创建测试失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """主测试函数"""
    print("🚀 开始连接器UI交互测试...\n")
    
    # 测试连接器列表
    await test_ipc_connector_list()
    
    # 测试连接器创建
    await test_connector_creation()
    
    # 再次测试连接器列表，验证创建是否成功
    print("\n=== 创建后验证连接器列表 ===")
    await test_ipc_connector_list()

if __name__ == "__main__":
    asyncio.run(main())