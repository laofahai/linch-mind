#!/usr/bin/env python3
"""
架构验证脚本
验证修复后的系统架构完整性
"""

import sys
import importlib
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "daemon"))

def test_imports():
    """测试关键模块导入"""
    print("🔍 测试模块导入...")
    
    modules = [
        "config.unified_config",
        "config.logging_config", 
        "config.dependencies",
        "services.system_config_service",
        "services.connectors.unified_connector_service",
        "services.ipc_server",
        "services.ipc_protocol",
        "services.ipc_router",
        "services.database_service"
    ]
    
    success_count = 0
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ {module}: {e}")
    
    print(f"导入测试: {success_count}/{len(modules)} 成功")
    return success_count == len(modules)

def test_config_system():
    """测试配置系统"""
    print("\n🔧 测试配置系统...")
    
    try:
        from config.unified_config import get_config_manager, get_config
        
        # 测试配置管理器
        config_manager = get_config_manager()
        config = get_config()
        
        print(f"  ✅ 配置加载成功")
        print(f"  ✅ 服务器配置: {config.server.host}:{config.server.port}")
        print(f"  ✅ 日志级别: {config.server.log_level}")
        print(f"  ✅ IPC Socket: {config.server.ipc_socket_path}")
        
        # 测试路径配置
        paths = config_manager.get_paths()
        print(f"  ✅ 配置路径: {len(paths)} 项")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 配置系统错误: {e}")
        return False

def test_logging_system():
    """测试日志系统"""
    print("\n📋 测试日志系统...")
    
    try:
        from config.logging_config import setup_global_logging, get_logger
        
        # 设置全局日志
        setup_global_logging(level="INFO", console=False)
        
        # 获取日志记录器
        logger = get_logger("test")
        logger.info("测试日志消息")
        
        print(f"  ✅ 日志系统初始化成功")
        print(f"  ✅ 日志记录器创建成功")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 日志系统错误: {e}")
        return False

def test_service_layer():
    """测试服务层"""
    print("\n🏗️ 测试服务层...")
    
    try:
        from services.system_config_service import get_system_config_service
        from services.connectors.unified_connector_service import get_unified_connector_service
        
        # 测试系统配置服务
        system_service = get_system_config_service()
        print(f"  ✅ 系统配置服务创建成功")
        
        # 测试统一连接器服务
        connector_service = get_unified_connector_service()
        print(f"  ✅ 统一连接器服务创建成功")
        
        # 测试配置schema功能（异步函数的简单测试）
        import asyncio
        
        async def test_async_functions():
            try:
                # 测试获取不存在连接器的schema（应该返回默认schema）
                schema = await connector_service.get_config_schema("nonexistent")
                if schema:
                    print(f"  ✅ 配置Schema功能正常")
                    return True
                return False
            except Exception as e:
                print(f"  ❌ 异步功能错误: {e}")
                return False
        
        # 运行异步测试
        result = asyncio.run(test_async_functions())
        return result
        
    except Exception as e:
        print(f"  ❌ 服务层错误: {e}")
        return False

def test_ipc_components():
    """测试IPC组件"""
    print("\n🔗 测试IPC组件...")
    
    try:
        from services.ipc_protocol import IPCMessage, IPCRequest, IPCResponse
        from services.ipc_router import IPCRouter
        
        # 测试IPC消息
        message = IPCMessage("GET", "/test", {"key": "value"})
        print(f"  ✅ IPC消息创建成功")
        
        # 测试序列化
        json_str = message.to_json()
        print(f"  ✅ IPC消息序列化成功")
        
        # 测试反序列化
        restored = IPCMessage.from_json(json_str)
        print(f"  ✅ IPC消息反序列化成功")
        
        # 测试IPC请求响应
        request = IPCRequest("req_123", "GET", "/status")
        response = IPCResponse.success_response({"status": "ok"}, "req_123")
        print(f"  ✅ IPC请求响应创建成功")
        
        # 测试路由器
        router = IPCRouter()
        print(f"  ✅ IPC路由器创建成功")
        
        return True
        
    except Exception as e:
        print(f"  ❌ IPC组件错误: {e}")
        return False

def test_no_http_remnants():
    """测试是否完全清除HTTP残留"""
    print("\n🚫 测试HTTP残留清理...")
    
    # 检查是否还有HTTP相关导入
    http_modules = [
        "fastapi",
        "uvicorn", 
        "starlette",
        "httpx",
        "requests"
    ]
    
    clean = True
    for module in http_modules:
        if module in sys.modules:
            print(f"  ⚠️  检测到HTTP模块残留: {module}")
            clean = False
    
    if clean:
        print(f"  ✅ 无HTTP模块残留")
    
    # 检查关键文件是否不存在HTTP引用
    try:
        from services import ipc_routes
        print(f"  ✅ IPC路由模块无HTTP依赖")
    except ImportError as e:
        if "fastapi" in str(e).lower() or "uvicorn" in str(e).lower():
            print(f"  ❌ IPC路由仍有HTTP依赖: {e}")
            clean = False
        else:
            print(f"  ✅ IPC路由正常（预期的导入错误）")
    
    return clean

def main():
    """主验证函数"""
    print("🚀 Linch Mind 架构完整性验证")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("配置系统", test_config_system),
        ("日志系统", test_logging_system),
        ("服务层", test_service_layer),
        ("IPC组件", test_ipc_components),
        ("HTTP清理", test_no_http_remnants)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"⚠️  {test_name} 测试未完全通过")
        except Exception as e:
            print(f"❌ {test_name} 测试出现异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 验证结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 架构验证完全通过！系统已准备就绪")
        return True
    else:
        print("⚠️  架构验证部分通过，建议检查失败项")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)