#!/usr/bin/env python3
"""
测试连接器数据库状态的脚本
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'daemon'))

def test_connector_database():
    """测试连接器数据库状态"""
    try:
        from daemon.services.database_service import get_database_service
        from daemon.models.database_models import Connector
        
        print("=== 连接器数据库测试 ===")
        
        # 获取数据库服务
        db_service = get_database_service()
        print(f"✅ 数据库服务初始化成功")
        print(f"   数据库配置: {hasattr(db_service, 'db_config')}")
        if hasattr(db_service, 'db_config'):
            print(f"   SQLite URL: {db_service.db_config.sqlite_url}")
        
        # 查询连接器数据
        with db_service.get_session() as session:
            connectors = session.query(Connector).all()
            print(f"\n📊 数据库中的连接器数量: {len(connectors)}")
            
            if connectors:
                print("\n🔗 已注册的连接器:")
                for connector in connectors:
                    print(f"   - ID: {connector.connector_id}")
                    print(f"     名称: {connector.name}")
                    print(f"     状态: {connector.status}")
                    print(f"     启用: {connector.enabled}")
                    print(f"     数据条数: {connector.data_count}")
                    print(f"     创建时间: {connector.created_at}")
                    if connector.error_message:
                        print(f"     错误信息: {connector.error_message}")
                    print()
            else:
                print("\n⚠️  数据库中没有找到任何连接器记录")
                print("   这可能是问题的原因：创建连接器后没有正确保存到数据库")
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_connector_manager():
    """测试连接器管理器"""
    try:
        from daemon.services.connectors.connector_manager import get_connector_manager
        
        print("\n=== 连接器管理器测试 ===")
        
        manager = get_connector_manager()
        print("✅ 连接器管理器初始化成功")
        
        # 列出连接器
        connectors = manager.list_connectors()
        print(f"\n📊 管理器中的连接器数量: {len(connectors)}")
        
        if connectors:
            print("\n🔗 管理器中的连接器:")
            for connector in connectors:
                print(f"   - ID: {connector.get('connector_id')}")
                print(f"     名称: {connector.get('name')}")
                print(f"     状态: {connector.get('status')}")
                print(f"     启用: {connector.get('enabled')}")
                print()
        else:
            print("\n⚠️  管理器中没有找到任何连接器")
        
    except Exception as e:
        print(f"❌ 连接器管理器测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connector_database()
    test_connector_manager()