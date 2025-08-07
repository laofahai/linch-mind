#!/usr/bin/env python3
"""
连接器配置系统修复验证测试脚本

验证修复的问题：
1. WebView配置路由是否正确注册
2. IPC路由是否完整
3. 连接器配置服务方法是否正常工作
4. 连接器启动逻辑是否正确
5. 数据库一致性是否正常
"""

import asyncio
import sys
import logging
from pathlib import Path

# 添加daemon目录到Python路径
daemon_root = Path(__file__).parent / "daemon"
sys.path.insert(0, str(daemon_root))

from services.database_service import get_database_service
from services.connectors.connector_manager import get_connector_manager
from services.connectors.connector_config_service import get_connector_config_service
from services.ipc_routes import register_all_routes
from services.ipc_router import ipc_app
from config.core_config import get_core_config_manager
from models.database_models import Connector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_database_connectivity():
    """测试数据库连接"""
    print("🔗 测试数据库连接...")
    try:
        db_service = get_database_service()
        with db_service.get_session() as session:
            connectors = session.query(Connector).all()
            print(f"✅ 数据库连接正常，找到 {len(connectors)} 个连接器")
            return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


async def test_ipc_routes_registration():
    """测试IPC路由注册"""
    print("\n🛣️  测试IPC路由注册...")
    try:
        # 清空现有路由
        ipc_app.routers.clear()
        
        # 注册所有路由
        register_all_routes(ipc_app)
        
        route_count = len(ipc_app.routers)
        print(f"✅ IPC路由注册成功，共注册 {route_count} 个路由器")
        
        # 检查是否包含WebView配置路由
        webview_router_found = any(
            router.prefix == "/webview-config" 
            for router in ipc_app.routers
        )
        
        if webview_router_found:
            print("✅ WebView配置路由已正确注册")
        else:
            print("❌ WebView配置路由未找到")
            return False
            
        return True
    except Exception as e:
        print(f"❌ IPC路由注册失败: {e}")
        return False


async def test_connector_config_service():
    """测试连接器配置服务"""
    print("\n⚙️  测试连接器配置服务...")
    try:
        config_service = get_connector_config_service()
        
        # 测试获取配置Schema
        try:
            schema = await config_service.get_config_schema("filesystem")
            if schema:
                print("✅ 文件系统连接器配置Schema获取成功")
                print(f"   Schema source: {schema.get('source', 'unknown')}")
                print(f"   Schema keys: {list(schema.keys())}")
            else:
                print("❌ 文件系统连接器配置Schema获取失败")
                return False
        except Exception as e:
            print(f"❌ 获取配置Schema失败: {e}")
            return False
        
        # 测试获取当前配置
        try:
            current_config = await config_service.get_current_config("filesystem")
            print(f"✅ 当前配置获取成功，配置项数量: {len(current_config) if current_config else 0}")
        except Exception as e:
            print(f"❌ 获取当前配置失败: {e}")
            return False
        
        # 测试获取所有Schema
        try:
            all_schemas = await config_service.get_all_schemas()
            print(f"✅ 所有Schema获取成功，共 {len(all_schemas)} 个")
        except Exception as e:
            print(f"❌ 获取所有Schema失败: {e}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ 连接器配置服务测试失败: {e}")
        return False


async def test_webview_config_service():
    """测试WebView配置服务"""
    print("\n🌐 测试WebView配置服务...")
    try:
        from services.webview_config_service import WebViewConfigService
        
        config_manager = get_core_config_manager()
        webview_service = WebViewConfigService(config_manager)
        
        # 测试模板验证
        test_template = "<html><head><title>Test</title></head><body>{{ connector_name }}</body></html>"
        validation_result = webview_service.validate_template(test_template)
        
        if validation_result.get("valid"):
            print("✅ 模板验证功能正常")
        else:
            print(f"❌ 模板验证失败: {validation_result.get('message')}")
            return False
        
        # 测试获取可用模板
        try:
            templates = await webview_service.get_available_templates()
            print(f"✅ 模板列表获取成功，共 {len(templates)} 个模板")
        except Exception as e:
            print(f"❌ 获取模板列表失败: {e}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ WebView配置服务测试失败: {e}")
        return False


async def test_connector_startup_logic():
    """测试连接器启动逻辑"""
    print("\n🚀 测试连接器启动逻辑...")
    try:
        db_service = get_database_service()
        connector_manager = get_connector_manager()
        
        # 检查数据库中已启用的连接器
        with db_service.get_session() as session:
            enabled_connectors = session.query(Connector).filter_by(enabled=True).all()
            print(f"✅ 数据库中有 {len(enabled_connectors)} 个已启用的连接器")
            
            for connector in enabled_connectors:
                print(f"   - {connector.connector_id}: {connector.name}")
        
        # 检查连接器管理器是否能正确识别已启用的连接器
        try:
            registered_connectors = await connector_manager.get_all_connectors()
            print(f"✅ 连接器管理器识别到 {len(registered_connectors)} 个注册连接器")
        except Exception as e:
            print(f"❌ 连接器管理器获取连接器列表失败: {e}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ 连接器启动逻辑测试失败: {e}")
        return False


async def test_ipc_endpoints():
    """测试IPC端点"""
    print("\n🔌 测试IPC端点...")
    try:
        from services.ipc_protocol import IPCRequest
        
        # 测试连接器配置路由
        test_cases = [
            ("GET", "/connector-config/schema/filesystem", None),
            ("GET", "/connector-config/current/filesystem", None),
            ("GET", "/connector-config/all-schemas", None),
            ("GET", "/webview-config/check-support/filesystem", None),
            ("GET", "/webview-config/templates", None),
        ]
        
        success_count = 0
        for method, path, data in test_cases:
            try:
                request = IPCRequest(method=method, path=path, data=data)
                response = await ipc_app.handle_request(
                    method=method, 
                    path=path, 
                    data=data,
                    request_id="test-" + path.replace("/", "-")
                )
                
                if response.success or (response.error and response.error.code != "RESOURCE_NOT_FOUND"):
                    print(f"✅ {method} {path} - 响应正常")
                    success_count += 1
                else:
                    print(f"❌ {method} {path} - 未找到路由")
            except Exception as e:
                print(f"❌ {method} {path} - 测试失败: {e}")
        
        print(f"✅ IPC端点测试完成，{success_count}/{len(test_cases)} 个端点正常")
        return success_count == len(test_cases)
    except Exception as e:
        print(f"❌ IPC端点测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🧪 开始连接器配置系统修复验证测试\n")
    
    tests = [
        ("数据库连接", test_database_connectivity),
        ("IPC路由注册", test_ipc_routes_registration),
        ("连接器配置服务", test_connector_config_service),
        ("WebView配置服务", test_webview_config_service),
        ("连接器启动逻辑", test_connector_startup_logic),
        ("IPC端点", test_ipc_endpoints),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            failed += 1
    
    print(f"\n📊 测试结果汇总:")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"📈 通过率: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 所有测试通过！连接器配置系统修复成功。")
        return 0
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，需要进一步检查。")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)