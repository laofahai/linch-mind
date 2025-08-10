#!/usr/bin/env python3
"""
核心组件测试套件
全面测试重构后的架构组件
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sqlite3
import threading
import time
from contextlib import contextmanager
import sys
import os

# 添加daemon到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import (
    StructuredExceptionHandler,
    ServiceContainer,
    DatabaseManager,
    ErrorCode,
    create_error_response,
    get_error_info,
    handle_exceptions,
    safe_execute
)


class TestStructuredExceptionHandler:
    """结构化异常处理器测试"""
    
    def setup_method(self):
        """测试前设置"""
        self.handler = StructuredExceptionHandler()
        
    def test_exception_classification(self):
        """测试异常分类功能"""
        from core.exception_handler import ExceptionClassifier
        
        # 测试已知异常类型
        connection_error = ConnectionError("连接失败")
        classified = ExceptionClassifier.classify_exception(connection_error, "test_op")
        assert classified.error_code == ErrorCode.IPC_CONNECTION_FAILED
        
        # 测试未知异常类型
        value_error = ValueError("数值错误")
        classified = ExceptionClassifier.classify_exception(value_error, "test_op")
        assert classified.error_code == ErrorCode.UNKNOWN_ERROR
        
    def test_handle_exceptions_decorator(self):
        """测试异常处理装饰器"""
        @handle_exceptions("test_operation")
        def normal_function(x, y):
            return x + y
            
        @handle_exceptions("error_operation")  
        def error_function():
            raise ValueError("测试错误")
            
        # 正常执行
        result = normal_function(1, 2)
        assert result == 3
        
        # 异常执行
        result = error_function()
        assert result is None  # 默认返回None
        
    def test_safe_execute(self):
        """测试安全执行函数"""
        # 正常执行
        result = safe_execute(lambda: 42)
        assert result == 42
        
        # 异常执行
        result = safe_execute(lambda: 1/0, default="error")
        assert result == "error"
        
    def test_create_error_response_integration(self):
        """测试错误响应创建功能"""
        response = create_error_response(
            ErrorCode.DATABASE_CONNECTION_FAILED,
            details="连接超时",
            context={"host": "localhost", "port": 5432}
        )
        
        assert response["success"] is False
        assert response["error"]["code"] == ErrorCode.DATABASE_CONNECTION_FAILED
        assert "连接超时" in response["error"]["details"]
        assert "host" in response["error"]["context"]


class TestServiceContainer:
    """依赖注入容器测试"""
    
    def setup_method(self):
        """测试前设置"""
        self.container = ServiceContainer()
        
    def test_singleton_registration_and_resolution(self):
        """测试单例注册和解析"""
        class TestService:
            def __init__(self):
                self.value = 42
                
        # 注册单例服务
        self.container.register_singleton(TestService)
        
        # 解析服务
        service1 = self.container.get_service(TestService)
        service2 = self.container.get_service(TestService)
        
        # 验证是同一个实例
        assert service1 is service2
        assert service1.value == 42
        
    def test_transient_registration_and_resolution(self):
        """测试瞬态注册和解析"""
        class TestService:
            def __init__(self):
                self.value = 42
                
        # 注册瞬态服务
        self.container.register_transient(TestService)
        
        # 解析服务
        service1 = self.container.get_service(TestService)
        service2 = self.container.get_service(TestService)
        
        # 验证是不同的实例
        assert service1 is not service2
        assert service1.value == service2.value == 42
        
    def test_dependency_injection(self):
        """测试依赖注入功能"""
        class DatabaseService:
            def __init__(self):
                self.connected = True
                
        class UserService:
            def __init__(self, db_service: DatabaseService):
                self.db_service = db_service
                
        # 注册服务
        self.container.register_singleton(DatabaseService)
        self.container.register_transient(UserService)
        
        # 解析依赖服务
        user_service = self.container.get_service(UserService)
        
        # 验证依赖注入
        assert user_service.db_service is not None
        assert user_service.db_service.connected is True
        
    def test_circular_dependency_detection(self):
        """测试循环依赖检测"""
        class ServiceA:
            def __init__(self, service_b: 'ServiceB'):
                self.service_b = service_b
                
        class ServiceB:
            def __init__(self, service_a: ServiceA):
                self.service_a = service_a
                
        # 注册服务
        self.container.register_singleton(ServiceA)
        self.container.register_singleton(ServiceB)
        
        # 尝试解析应该检测到循环依赖
        with pytest.raises(Exception):  # 应该抛出CircularDependencyError
            self.container.get_service(ServiceA)
            
    def test_thread_safety(self):
        """测试线程安全性"""
        class ThreadSafeService:
            def __init__(self):
                self.value = threading.current_thread().ident
                
        self.container.register_singleton(ThreadSafeService)
        
        services = []
        
        def get_service():
            service = self.container.get_service(ThreadSafeService)
            services.append(service)
            
        # 创建多个线程同时获取服务
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=get_service)
            threads.append(thread)
            thread.start()
            
        # 等待所有线程完成
        for thread in threads:
            thread.join()
            
        # 验证所有服务实例都是同一个
        for service in services[1:]:
            assert service is services[0]


@pytest.mark.asyncio
class TestDatabaseManager:
    """数据库管理器测试"""
    
    async def test_database_manager_initialization(self):
        """测试数据库管理器初始化"""
        from core.database_manager import DatabaseConfig
        
        config = DatabaseConfig(
            database_url="sqlite:///:memory:",
            pool_size=5,
            max_overflow=10
        )
        
        manager = DatabaseManager(config)
        assert manager is not None
        
    def test_session_context_manager(self):
        """测试数据库会话上下文管理器"""
        from core.database_manager import DatabaseConfig
        
        config = DatabaseConfig(
            database_url="sqlite:///:memory:",
            pool_size=2,
            max_overflow=5
        )
        
        manager = DatabaseManager(config)
        
        # 测试正常会话使用
        with manager.get_session() as session:
            assert session is not None
            # 在这里session应该是活跃的
            
        # session应该已经关闭
        
    def test_transaction_rollback_on_error(self):
        """测试错误时的事务回滚"""
        from core.database_manager import DatabaseConfig
        from sqlalchemy import Column, Integer, String, create_engine
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker
        
        Base = declarative_base()
        
        class TestModel(Base):
            __tablename__ = 'test_model'
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
            
        # 创建内存数据库
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        
        config = DatabaseConfig(
            database_url="sqlite:///:memory:",
            pool_size=1,
            max_overflow=1
        )
        
        manager = DatabaseManager(config)
        
        # 测试事务回滚
        try:
            with manager.get_session() as session:
                # 模拟创建记录后出现错误
                record = TestModel(name="test")
                session.add(record)
                raise Exception("模拟错误")
        except:
            pass
            
        # 验证事务已回滚（这里需要实际的数据库验证）
        
    async def test_async_session_management(self):
        """测试异步会话管理"""
        # 跳过异步数据库测试，因为缺少aiosqlite依赖
        pytest.skip("异步数据库功能需要aiosqlite依赖")


class TestErrorCodeSystem:
    """错误码体系测试"""
    
    def test_error_code_enum(self):
        """测试错误码枚举"""
        # 测试基本错误码
        assert ErrorCode.SUCCESS == 0
        assert ErrorCode.IPC_CONNECTION_FAILED == 2000
        assert ErrorCode.DATABASE_CONNECTION_FAILED == 3000
        
    def test_error_info_retrieval(self):
        """测试错误信息获取"""
        error_info = get_error_info(ErrorCode.IPC_CONNECTION_FAILED)
        
        assert error_info.code == ErrorCode.IPC_CONNECTION_FAILED
        assert "IPC Connection Failed" in error_info.message
        assert error_info.category == "ipc"
        assert error_info.recoverable is True
        
    def test_create_error_response(self):
        """测试错误响应创建"""
        response = create_error_response(
            ErrorCode.DATABASE_CONNECTION_FAILED,
            details="连接超时",
            context={"host": "localhost"}
        )
        
        assert response["success"] is False
        assert response["error"]["code"] == ErrorCode.DATABASE_CONNECTION_FAILED
        assert response["error"]["details"] == "连接超时"
        assert response["error"]["context"]["host"] == "localhost"
        assert response["error"]["recoverable"] is False  # 数据库连接失败不可恢复
        
    def test_error_severity_classification(self):
        """测试错误严重程度分类"""
        critical_error = get_error_info(ErrorCode.DATABASE_CONNECTION_FAILED)
        warning_error = get_error_info(ErrorCode.RESOURCE_NOT_FOUND)
        
        assert critical_error.severity.name == "CRITICAL"
        assert warning_error.severity.name == "WARNING"
        
    def test_user_friendly_messages(self):
        """测试用户友好消息"""
        from core import get_user_friendly_message
        
        friendly_msg = get_user_friendly_message(ErrorCode.IPC_CONNECTION_FAILED)
        assert "服务" in friendly_msg and "连接" in friendly_msg
        
        friendly_msg2 = get_user_friendly_message(ErrorCode.DATABASE_CONNECTION_FAILED)
        assert "数据" in friendly_msg2


class TestIntegration:
    """集成测试"""
    
    def test_exception_handler_with_error_codes(self):
        """测试异常处理器与错误码系统集成"""
        @handle_exceptions("test_db_operation")
        def db_operation():
            # 模拟数据库连接错误
            raise ConnectionError("数据库连接失败")
            
        result = db_operation()
        assert result is None
        
        # 测试错误响应创建
        response = create_error_response(
            ErrorCode.DATABASE_CONNECTION_FAILED,
            details="集成测试错误"
        )
        assert response["error"]["code"] == ErrorCode.DATABASE_CONNECTION_FAILED
        
    def test_container_with_exception_handling(self):
        """测试依赖注入容器与异常处理集成"""
        container = ServiceContainer()
        
        class ErrorProneService:
            def __init__(self):
                # 模拟初始化可能失败
                if hasattr(self.__class__, '_should_fail'):
                    raise RuntimeError("服务初始化失败")
                self.initialized = True
                
        # 注册服务
        container.register_singleton(ErrorProneService)
        
        # 正常情况
        service = container.get_service(ErrorProneService)
        assert service.initialized is True
        
        # 测试错误情况
        ErrorProneService._should_fail = True
        with pytest.raises(Exception):
            container.get_service(ErrorProneService)


class TestPerformance:
    """性能测试"""
    
    def test_exception_handler_performance(self):
        """测试异常处理器性能"""
        handler = StructuredExceptionHandler()
        
        @handle_exceptions("perf_test")
        def fast_operation():
            return 42
            
        # 测量装饰器开销
        start_time = time.perf_counter()
        for _ in range(1000):
            result = fast_operation()
        end_time = time.perf_counter()
        
        avg_time = (end_time - start_time) / 1000 * 1000  # 转换为毫秒
        assert avg_time < 0.1  # 平均每次调用<0.1ms
        
    def test_container_resolution_performance(self):
        """测试容器解析性能"""
        container = ServiceContainer()
        
        class FastService:
            def __init__(self):
                self.value = 42
                
        container.register_singleton(FastService)
        
        # 预热
        container.get_service(FastService)
        
        # 测量解析性能
        start_time = time.perf_counter()
        for _ in range(1000):
            service = container.get_service(FastService)
        end_time = time.perf_counter()
        
        avg_time = (end_time - start_time) / 1000 * 1000  # 转换为毫秒
        assert avg_time < 1.0  # 平均每次解析<1ms


# 运行测试的主函数
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])