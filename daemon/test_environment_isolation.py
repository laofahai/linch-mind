#!/usr/bin/env python3
"""
Environment Isolation Test - 环境隔离系统测试
验证完整的环境隔离机制是否正常工作
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# 添加daemon目录到Python路径
daemon_dir = Path(__file__).parent
sys.path.insert(0, str(daemon_dir))


def setup_logging():
    """设置测试日志"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


async def test_environment_manager():
    """测试环境管理器核心功能"""
    print("=" * 60)
    print("测试 1: 环境管理器核心功能")
    print("=" * 60)

    try:
        from core.environment_manager import get_environment_manager

        # 获取环境管理器
        env_manager = get_environment_manager()
        print(f"✅ 环境管理器初始化成功")

        # 检查当前环境
        current_env = env_manager.current_environment
        print(f"✅ 当前环境: {current_env.value}")

        # 获取环境摘要
        summary = env_manager.get_environment_summary()
        print(f"✅ 环境摘要获取成功")
        print(f"   数据库URL: {summary['database_url']}")
        print(f"   加密状态: {summary['use_encryption']}")
        print(f"   调试模式: {summary['debug_enabled']}")

        # 列出所有环境
        envs = env_manager.list_environments()
        print(f"✅ 发现 {len(envs)} 个环境:")
        for env in envs:
            marker = " (当前)" if env["name"] == current_env.value else ""
            print(f"   - {env['display_name']} ({env['name']}){marker}")

        return True

    except Exception as e:
        print(f"❌ 环境管理器测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_config_integration():
    """测试配置管理器集成"""
    print("\n" + "=" * 60)
    print("测试 2: 配置管理器环境集成")
    print("=" * 60)

    try:
        from config.core_config import get_core_config

        # 获取配置管理器
        config_manager = get_core_config()
        print(f"✅ 配置管理器初始化成功")

        # 获取环境信息
        env_info = config_manager.get_environment_info()
        print(f"✅ 环境信息获取成功: {env_info['current_environment']}")

        # 获取环境路径
        paths = config_manager.get_environment_paths()
        print(f"✅ 环境路径获取成功:")
        for name, path in paths.items():
            print(f"   {name}: {path}")

        # 获取系统配置 (包含环境信息)
        system_config = config_manager.get_system_config()
        env_section = system_config.get("environment", {})
        print(
            f"✅ 系统配置包含环境信息: {env_section.get('current_environment', 'unknown')}"
        )

        return True

    except Exception as e:
        print(f"❌ 配置管理器集成测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_database_service():
    """测试数据库服务环境集成"""
    print("\n" + "=" * 60)
    print("测试 3: 数据库服务环境集成")
    print("=" * 60)

    try:
        # 初始化DI容器 (模拟主程序的初始化)
        from core.container import get_container
        from services.database_service import DatabaseService

        container = get_container()

        # 注册数据库服务 (使用正确的方法名)
        if not container.is_registered(DatabaseService):

            def create_database_service():
                return DatabaseService()

            container.register_singleton(DatabaseService, create_database_service)

        # 获取数据库服务
        db_service = container.get_service(DatabaseService)
        print(f"✅ 数据库服务初始化成功")

        # 获取环境数据库信息
        db_info = db_service.get_environment_database_info()
        print(f"✅ 环境数据库信息:")
        print(f"   环境: {db_info['environment']}")
        print(f"   数据库URL: {db_info['database_url']}")
        print(f"   加密: {db_info['use_encryption']}")
        print(f"   调试: {db_info['debug_enabled']}")

        # 初始化数据库
        await db_service.initialize()
        print(f"✅ 数据库初始化成功")

        # 获取数据库统计
        stats = db_service.get_database_stats()
        print(f"✅ 数据库统计:")
        print(f"   连接器数量: {stats.get('connectors_count', 0)}")
        print(f"   运行中连接器: {stats.get('running_connectors_count', 0)}")

        return True

    except Exception as e:
        print(f"❌ 数据库服务测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_service_facade():
    """测试ServiceFacade环境管理器集成"""
    print("\n" + "=" * 60)
    print("测试 4: ServiceFacade环境管理器集成")
    print("=" * 60)

    try:
        # 先注册EnvironmentManager到DI容器
        from core.container import get_container
        from core.environment_manager import EnvironmentManager

        container = get_container()
        if not container.is_registered(EnvironmentManager):

            def create_environment_manager():
                from core.environment_manager import get_environment_manager

                return get_environment_manager()

            container.register_singleton(EnvironmentManager, create_environment_manager)

        from core.service_facade import (
            get_environment_manager as facade_get_env_manager,
        )
        from core.service_facade import get_service_facade

        # 通过ServiceFacade获取环境管理器
        env_manager = facade_get_env_manager()
        print(f"✅ 通过ServiceFacade获取环境管理器成功")

        # 验证是同一个实例
        from core.environment_manager import get_environment_manager

        direct_manager = get_environment_manager()

        if env_manager is direct_manager:
            print(f"✅ ServiceFacade返回正确的单例实例")
        else:
            print(f"⚠️  ServiceFacade返回的不是同一个实例")

        # 测试服务统计
        facade = get_service_facade()
        stats = facade.get_service_stats()
        print(f"✅ ServiceFacade统计:")
        print(f"   已注册服务: {len(stats['registered_services'])}")
        print(f"   总访问次数: {stats['total_accesses']}")

        return True

    except Exception as e:
        print(f"❌ ServiceFacade测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_initialization_system():
    """测试环境初始化系统"""
    print("\n" + "=" * 60)
    print("测试 5: 环境初始化系统")
    print("=" * 60)

    try:
        from scripts.initialize_environment import EnvironmentInitializer

        # 创建初始化器
        initializer = EnvironmentInitializer()
        print(f"✅ 环境初始化器创建成功")

        # 执行轻量级初始化 (跳过模型和连接器)
        success = await initializer.initialize_current_environment(
            skip_models=True, skip_connectors=True
        )

        if success:
            print(f"✅ 环境初始化成功")

            # 显示初始化步骤
            print(f"初始化步骤:")
            for step in initializer.initialization_steps:
                status_icon = "✅" if step["status"] == "completed" else "❌"
                print(f"   {status_icon} {step['step']}")
        else:
            print(f"❌ 环境初始化失败")

        return success

    except Exception as e:
        print(f"❌ 初始化系统测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_environment_switching():
    """测试环境切换功能"""
    print("\n" + "=" * 60)
    print("测试 6: 环境切换功能")
    print("=" * 60)

    try:
        from core.environment_manager import Environment, get_environment_manager

        env_manager = get_environment_manager()
        original_env = env_manager.current_environment
        print(f"✅ 原始环境: {original_env.value}")

        # 测试临时环境切换
        target_env = (
            Environment.PRODUCTION
            if original_env != Environment.PRODUCTION
            else Environment.STAGING
        )

        print(f"测试临时切换到: {target_env.value}")
        with env_manager.switch_environment(target_env):
            switched_env = env_manager.current_environment
            print(f"✅ 临时切换成功: {switched_env.value}")

            # 验证配置也切换了
            config = env_manager.current_config
            print(f"✅ 配置已更新: {config.display_name}")

        # 验证环境已恢复
        restored_env = env_manager.current_environment
        print(f"✅ 环境已恢复: {restored_env.value}")

        if restored_env == original_env:
            print(f"✅ 临时环境切换测试通过")
            return True
        else:
            print(f"❌ 环境未正确恢复")
            return False

    except Exception as e:
        print(f"❌ 环境切换测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """执行完整的环境隔离系统测试"""
    setup_logging()

    print("🚀 Linch Mind Environment Isolation System Test")
    print(f"Python: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    print()

    # 执行所有测试
    tests = [
        ("环境管理器核心功能", test_environment_manager),
        ("配置管理器集成", test_config_integration),
        ("数据库服务集成", test_database_service),
        ("ServiceFacade集成", test_service_facade),
        ("初始化系统", test_initialization_system),
        ("环境切换功能", test_environment_switching),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            success = await test_func()
            if success:
                passed += 1
                print(f"✅ {test_name} - 通过")
            else:
                failed += 1
                print(f"❌ {test_name} - 失败")
        except Exception as e:
            failed += 1
            print(f"💥 {test_name} - 异常: {e}")

    # 测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"📊 总计: {passed + failed}")

    if failed == 0:
        print("🎉 所有测试通过！环境隔离系统运行正常")
        return True
    else:
        print(f"⚠️  有 {failed} 个测试失败，请检查系统配置")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
