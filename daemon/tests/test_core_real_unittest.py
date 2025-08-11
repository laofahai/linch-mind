#!/usr/bin/env python3
"""
真实有效的核心组件测试套件 - 使用unittest

测试实际的API和功能，确保所有测试都是真实有效的
"""

import os
import shutil
import sqlite3
import sys
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

# 添加daemon到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 实际导入
try:
    from core.container import (
        CircularDependencyError,
        ServiceContainer,
        ServiceLifecycle,
        ServiceNotRegisteredError,
        get_container,
    )
    from core.environment_manager import (
        Environment,
        EnvironmentConfig,
        EnvironmentManager,
        get_current_environment,
        get_database_url,
        get_environment_manager,
        reset_environment_manager,
    )
    from core.error_handling import (
        ErrorCategory,
        ErrorContext,
        ErrorSeverity,
        StandardizedError,
        error_context,
        get_error_handler,
        handle_errors,
    )
    from core.service_facade import (
        ServiceError,
        ServiceErrorType,
        ServiceFacade,
        ServiceResult,
        get_service,
        get_service_facade,
        try_get_service,
    )

    print("✅ 所有核心模块导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)


class TestEnvironmentManager(unittest.TestCase):
    """测试EnvironmentManager的真实功能"""

    def setUp(self):
        """每个测试前的设置"""
        self.test_dir = tempfile.mkdtemp()
        # 重置环境管理器单例
        reset_environment_manager()

        # 模拟HOME目录
        self.home_patcher = patch("pathlib.Path.home", return_value=Path(self.test_dir))
        self.home_patcher.start()

    def tearDown(self):
        """测试后清理"""
        self.home_patcher.stop()
        reset_environment_manager()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_environment_initialization(self):
        """测试环境管理器初始化"""
        env_manager = EnvironmentManager()

        # 检查基本属性
        self.assertTrue(hasattr(env_manager, "_current_env"))
        self.assertTrue(hasattr(env_manager, "_base_dir"))
        self.assertIn(
            env_manager._current_env,
            [Environment.DEVELOPMENT, Environment.STAGING, Environment.PRODUCTION],
        )
        self.assertIsInstance(env_manager._base_dir, Path)
        print("✅ 环境管理器初始化测试通过")

    def test_environment_detection(self):
        """测试环境检测逻辑"""
        # 测试LINCH_ENV环境变量
        with patch.dict(os.environ, {"LINCH_ENV": "production"}):
            env_manager = EnvironmentManager()
            self.assertEqual(env_manager.current_environment, Environment.PRODUCTION)

        # 测试默认环境
        with patch.dict(os.environ, {}, clear=True):
            reset_environment_manager()
            env_manager = EnvironmentManager()
            self.assertEqual(env_manager.current_environment, Environment.DEVELOPMENT)
        print("✅ 环境检测逻辑测试通过")

    def test_environment_enum(self):
        """测试Environment枚举"""
        self.assertEqual(Environment.DEVELOPMENT.value, "development")
        self.assertEqual(Environment.STAGING.value, "staging")
        self.assertEqual(Environment.PRODUCTION.value, "production")

        # 测试from_string方法
        self.assertEqual(
            Environment.from_string("development"), Environment.DEVELOPMENT
        )
        self.assertEqual(Environment.from_string("dev"), Environment.DEVELOPMENT)
        self.assertEqual(Environment.from_string("production"), Environment.PRODUCTION)

        with self.assertRaises(ValueError):
            Environment.from_string("invalid")
        print("✅ Environment枚举测试通过")

    def test_directory_creation(self):
        """测试目录创建"""
        env_manager = EnvironmentManager()
        config = env_manager.current_config

        # 验证基本目录存在
        self.assertTrue(config.base_path.exists())
        self.assertTrue(config.config_dir.exists())
        self.assertTrue(config.database_dir.exists())
        self.assertTrue(config.logs_dir.exists())
        print("✅ 目录创建测试通过")

    def test_database_url_generation(self):
        """测试数据库URL生成"""
        env_manager = EnvironmentManager()

        # 测试普通数据库URL
        url = env_manager.get_database_url()
        self.assertTrue(url.startswith("sqlite:///"))
        self.assertIn("linch_mind", url)

        # 测试内存数据库
        memory_url = env_manager.get_database_url(in_memory=True)
        self.assertEqual(memory_url, "sqlite:///:memory:")
        print("✅ 数据库URL生成测试通过")

    def test_environment_switching(self):
        """测试环境切换"""
        env_manager = EnvironmentManager()
        original_env = env_manager.current_environment

        # 测试临时环境切换
        target_env = (
            Environment.PRODUCTION
            if original_env != Environment.PRODUCTION
            else Environment.STAGING
        )

        with env_manager.switch_environment(target_env):
            self.assertEqual(env_manager.current_environment, target_env)

        # 确保切换后恢复
        self.assertEqual(env_manager.current_environment, original_env)
        print("✅ 环境切换测试通过")

    def test_global_functions(self):
        """测试全局便捷函数"""
        # 测试get_environment_manager单例
        manager1 = get_environment_manager()
        manager2 = get_environment_manager()
        self.assertIs(manager1, manager2)

        # 测试便捷函数
        current_env = get_current_environment()
        self.assertIsInstance(current_env, Environment)

        db_url = get_database_url()
        self.assertIsInstance(db_url, str)
        self.assertTrue(db_url.startswith("sqlite:///"))
        print("✅ 全局函数测试通过")


class TestServiceFacade(unittest.TestCase):
    """测试ServiceFacade真实功能"""

    def setUp(self):
        """测试前重置"""
        # 重置全局状态
        if hasattr(ServiceFacade, "_instance"):
            ServiceFacade._instance = None

    def test_service_facade_creation(self):
        """测试ServiceFacade创建"""
        facade = ServiceFacade()
        self.assertIsNotNone(facade)
        self.assertTrue(hasattr(facade, "container"))
        self.assertTrue(hasattr(facade, "_access_stats"))
        print("✅ ServiceFacade创建测试通过")

    def test_service_error_types(self):
        """测试ServiceError和相关枚举"""
        # 测试ServiceErrorType枚举
        self.assertEqual(ServiceErrorType.NOT_REGISTERED.value, "not_registered")
        self.assertEqual(
            ServiceErrorType.INITIALIZATION_FAILED.value, "initialization_failed"
        )

        # 测试ServiceError异常
        error = ServiceError(ServiceErrorType.NOT_REGISTERED, "Test error")
        self.assertEqual(error.error_type, ServiceErrorType.NOT_REGISTERED)
        self.assertEqual(str(error), "Test error")
        print("✅ ServiceError类型测试通过")

    def test_service_result(self):
        """测试ServiceResult封装"""
        # 测试成功结果
        success_result = ServiceResult(success=True, service="test_service")
        self.assertTrue(success_result.is_success)
        self.assertEqual(success_result.unwrap(), "test_service")

        # 测试失败结果
        fail_result = ServiceResult(
            success=False,
            error_type=ServiceErrorType.NOT_REGISTERED,
            error_message="Service not found",
        )
        self.assertFalse(fail_result.is_success)

        with self.assertRaises(ServiceError):
            fail_result.unwrap()
        print("✅ ServiceResult测试通过")

    def test_service_facade_container_integration(self):
        """测试ServiceFacade与Container的集成"""
        facade = ServiceFacade()
        container = facade.container

        self.assertIsNotNone(container)
        # container应该是ServiceContainer的实例
        self.assertTrue(hasattr(container, "get_all_services"))
        print("✅ ServiceFacade容器集成测试通过")

    def test_service_access_stats(self):
        """测试服务访问统计"""
        facade = ServiceFacade()

        # 初始统计应该为空
        stats = facade.get_service_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn("access_stats", stats)
        self.assertIn("registered_services", stats)
        print("✅ 服务访问统计测试通过")


class TestErrorHandling(unittest.TestCase):
    """测试错误处理框架的真实功能"""

    def test_error_enums(self):
        """测试错误相关枚举"""
        # 测试ErrorSeverity
        self.assertEqual(ErrorSeverity.LOW.value, "low")
        self.assertEqual(ErrorSeverity.MEDIUM.value, "medium")
        self.assertEqual(ErrorSeverity.HIGH.value, "high")
        self.assertEqual(ErrorSeverity.CRITICAL.value, "critical")

        # 测试ErrorCategory
        self.assertEqual(ErrorCategory.IPC_COMMUNICATION.value, "ipc_communication")
        self.assertEqual(ErrorCategory.DATABASE_OPERATION.value, "database_operation")
        self.assertEqual(
            ErrorCategory.CONNECTOR_MANAGEMENT.value, "connector_management"
        )
        print("✅ 错误枚举测试通过")

    def test_error_context(self):
        """测试ErrorContext数据类"""
        context = ErrorContext(
            function_name="test_function",
            module_name="test_module",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.DATABASE_OPERATION,
            user_message="Test error",
        )

        self.assertEqual(context.function_name, "test_function")
        self.assertEqual(context.severity, ErrorSeverity.HIGH)
        self.assertEqual(context.category, ErrorCategory.DATABASE_OPERATION)

        # 测试to_dict方法
        context_dict = context.to_dict()
        self.assertIsInstance(context_dict, dict)
        self.assertEqual(context_dict["function"], "test_function")
        self.assertEqual(context_dict["severity"], "high")
        print("✅ ErrorContext测试通过")

    def test_standardized_error(self):
        """测试StandardizedError异常"""
        context = ErrorContext(
            function_name="test",
            module_name="test",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.UNKNOWN,
        )

        error = StandardizedError("Test message", context)
        self.assertEqual(str(error), "Test message")
        self.assertEqual(error.context, context)
        self.assertIn("StandardizedError", repr(error))
        print("✅ StandardizedError测试通过")

    def test_handle_errors_decorator_success(self):
        """测试handle_errors装饰器正常执行"""

        @handle_errors(severity=ErrorSeverity.LOW, category=ErrorCategory.CONFIGURATION)
        def successful_function():
            return "success"

        result = successful_function()
        self.assertEqual(result, "success")
        print("✅ handle_errors装饰器成功执行测试通过")

    def test_error_handler_global_instance(self):
        """测试全局错误处理器"""
        handler = get_error_handler()
        self.assertIsNotNone(handler)

        stats = handler.get_error_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn("total_errors", stats)
        print("✅ 全局错误处理器测试通过")


class TestServiceContainer(unittest.TestCase):
    """测试ServiceContainer真实功能"""

    def setUp(self):
        """每个测试前创建新容器"""
        self.container = ServiceContainer()

    def test_container_creation(self):
        """测试容器创建"""
        self.assertIsNotNone(self.container)
        self.assertTrue(hasattr(self.container, "_services"))
        self.assertTrue(hasattr(self.container, "_instances"))
        print("✅ 容器创建测试通过")

    def test_singleton_registration(self):
        """测试单例服务注册"""

        class TestService:
            def __init__(self):
                self.value = 42

        # 注册单例
        self.container.register_singleton(TestService)

        # 验证注册成功
        self.assertTrue(self.container.is_registered(TestService))

        # 获取服务
        service1 = self.container.get_service(TestService)
        service2 = self.container.get_service(TestService)

        # 验证是同一个实例
        self.assertIs(service1, service2)
        self.assertEqual(service1.value, 42)
        print("✅ 单例注册测试通过")

    def test_transient_registration(self):
        """测试瞬态服务注册"""

        class TestService:
            def __init__(self):
                self.value = 42

        # 注册瞬态服务
        self.container.register_transient(TestService)

        # 获取服务
        service1 = self.container.get_service(TestService)
        service2 = self.container.get_service(TestService)

        # 验证是不同实例
        self.assertIsNot(service1, service2)
        self.assertEqual(service1.value, service2.value)
        print("✅ 瞬态注册测试通过")

    def test_service_not_registered_error(self):
        """测试未注册服务异常"""

        class UnregisteredService:
            pass

        with self.assertRaises(ServiceNotRegisteredError):
            self.container.get_service(UnregisteredService)
        print("✅ 未注册服务异常测试通过")

    def test_instance_registration(self):
        """测试实例注册"""

        class TestService:
            def __init__(self, value):
                self.value = value

        instance = TestService(99)
        self.container.register_instance(TestService, instance)

        retrieved = self.container.get_service(TestService)
        self.assertIs(retrieved, instance)
        self.assertEqual(retrieved.value, 99)
        print("✅ 实例注册测试通过")

    def test_service_info(self):
        """测试服务信息获取"""

        class TestService:
            pass

        self.container.register_singleton(TestService)

        info = self.container.get_service_info(TestService)
        self.assertTrue(info["registered"])
        self.assertEqual(info["lifecycle"], ServiceLifecycle.SINGLETON)

        # 获取所有服务信息
        all_services = self.container.get_all_services()
        self.assertIn("TestService", all_services)
        print("✅ 服务信息获取测试通过")

    def test_dependency_injection(self):
        """测试自动依赖注入"""

        class DatabaseService:
            def __init__(self):
                self.connected = True

        class UserService:
            def __init__(self, db_service: DatabaseService):
                self.db_service = db_service

        # 注册服务
        self.container.register_singleton(DatabaseService)
        self.container.register_singleton(UserService)

        # 获取服务并验证依赖注入
        user_service = self.container.get_service(UserService)
        self.assertIsNotNone(user_service.db_service)
        self.assertTrue(user_service.db_service.connected)
        print("✅ 依赖注入测试通过")

    def test_global_container(self):
        """测试全局容器"""
        global_container = get_container()
        self.assertIsNotNone(global_container)
        self.assertIsInstance(global_container, ServiceContainer)
        print("✅ 全局容器测试通过")


class TestPerformance(unittest.TestCase):
    """性能测试"""

    def test_environment_manager_performance(self):
        """测试环境管理器性能"""
        with tempfile.TemporaryDirectory() as test_dir:
            with patch("pathlib.Path.home", return_value=Path(test_dir)):
                start_time = time.time()

                # 创建多个环境管理器实例
                managers = []
                for _ in range(10):
                    reset_environment_manager()
                    managers.append(EnvironmentManager())

                elapsed = time.time() - start_time

                # 应该在1秒内完成
                self.assertLess(elapsed, 1.0)

                # 验证所有管理器都正常工作
                for manager in managers:
                    self.assertIn(
                        manager.current_environment,
                        [
                            Environment.DEVELOPMENT,
                            Environment.STAGING,
                            Environment.PRODUCTION,
                        ],
                    )
        print("✅ 环境管理器性能测试通过")

    def test_service_facade_performance(self):
        """测试服务门面性能"""
        facade = ServiceFacade()

        start_time = time.time()

        # 多次访问服务门面
        for _ in range(100):
            stats = facade.get_service_stats()
            self.assertIsInstance(stats, dict)

        elapsed = time.time() - start_time

        # 应该非常快
        self.assertLess(elapsed, 0.5)
        print("✅ 服务门面性能测试通过")

    def test_container_performance(self):
        """测试容器性能"""
        container = ServiceContainer()

        class TestService:
            def __init__(self):
                self.value = 42

        container.register_singleton(TestService)

        start_time = time.time()

        # 多次获取服务
        for _ in range(1000):
            service = container.get_service(TestService)
            self.assertEqual(service.value, 42)

        elapsed = time.time() - start_time

        # 由于缓存，应该很快
        self.assertLess(elapsed, 0.5)
        print("✅ 容器性能测试通过")


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def setUp(self):
        """设置集成测试环境"""
        self.test_dir = tempfile.mkdtemp()
        reset_environment_manager()

        # 模拟HOME目录
        self.home_patcher = patch("pathlib.Path.home", return_value=Path(self.test_dir))
        self.home_patcher.start()

    def tearDown(self):
        """清理集成测试"""
        self.home_patcher.stop()
        reset_environment_manager()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_environment_service_integration(self):
        """测试环境管理器与服务系统集成"""
        # 初始化环境管理器
        env_manager = EnvironmentManager()

        # 获取服务门面
        facade = ServiceFacade()

        # 两者应该能正常协作
        self.assertIsNotNone(env_manager.current_environment)
        self.assertIsNotNone(facade)

        # 获取数据库URL
        db_url = env_manager.get_database_url()
        self.assertIn("sqlite:///", db_url)
        print("✅ 环境管理器与服务系统集成测试通过")

    def test_error_handling_integration(self):
        """测试错误处理与其他组件的集成"""

        @handle_errors(
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.CONFIGURATION,
            reraise=False,
        )
        def integrated_operation():
            # 使用环境管理器
            env_manager = EnvironmentManager()
            summary = env_manager.get_environment_summary()
            return summary

        # 应该正常执行
        result = integrated_operation()
        self.assertIsInstance(result, dict)
        print("✅ 错误处理集成测试通过")

    def test_full_system_integration(self):
        """测试完整系统集成"""
        # 初始化所有核心组件
        env_manager = EnvironmentManager()
        facade = ServiceFacade()
        container = ServiceContainer()
        error_handler = get_error_handler()

        # 验证所有组件都正常工作
        self.assertIsNotNone(env_manager.current_environment)
        self.assertIsNotNone(facade)
        self.assertIsNotNone(container)
        self.assertIsNotNone(error_handler)

        # 测试组件间的交互
        env_summary = env_manager.get_environment_summary()
        service_stats = facade.get_service_stats()
        all_services = container.get_all_services()
        error_stats = error_handler.get_error_stats()

        # 验证返回数据的正确性
        self.assertIsInstance(env_summary, dict)
        self.assertIsInstance(service_stats, dict)
        self.assertIsInstance(all_services, dict)
        self.assertIsInstance(error_stats, dict)
        print("✅ 完整系统集成测试通过")


def run_test_suite():
    """运行完整测试套件"""
    print("🧪 开始运行Linch Mind核心组件真实测试套件")
    print("=" * 60)

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    test_classes = [
        TestEnvironmentManager,
        TestServiceFacade,
        TestErrorHandling,
        TestServiceContainer,
        TestPerformance,
        TestIntegration,
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    print("🎯 测试结果总结:")
    print(f"   总测试数: {result.testsRun}")
    print(f"   成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   失败: {len(result.failures)}")
    print(f"   错误: {len(result.errors)}")

    if result.failures:
        print("\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")

    if result.errors:
        print("\n💥 错误的测试:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")

    if result.wasSuccessful():
        print("\n🎉 所有测试通过！核心组件功能完整且正确。")
        return True
    else:
        print("\n⚠️  部分测试失败，需要检查代码实现。")
        return False


if __name__ == "__main__":
    success = run_test_suite()
    sys.exit(0 if success else 1)
