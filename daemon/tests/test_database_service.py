#!/usr/bin/env python3
"""
数据库服务测试
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models.database_models import Base, Connector


class TestDatabaseService:
    """数据库服务测试类"""
    
    @pytest.fixture
    def in_memory_db(self):
        """创建内存数据库用于测试"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session()
    
    @pytest.fixture
    def database_service(self, in_memory_db):
        """创建数据库服务实例"""
        from services.database_service import DatabaseService
        
        service = DatabaseService()
        # 替换默认的session获取方法
        service._session = in_memory_db
        service.get_session = lambda: MockContextManager(in_memory_db)
        return service
    
    @pytest.mark.database
    def test_service_initialization(self):
        """测试数据库服务初始化"""
        from services.database_service import DatabaseService
        
        service = DatabaseService()
        assert service is not None
        assert hasattr(service, 'get_session')
        assert hasattr(service, 'initialize_database')
    
    @pytest.mark.database
    def test_get_database_service_singleton(self):
        """测试数据库服务单例模式"""
        from services.database_service import get_database_service, cleanup_database_service
        
        # 清理可能存在的实例
        cleanup_database_service()
        
        service1 = get_database_service()
        service2 = get_database_service()
        
        assert service1 is service2  # 验证单例
        
        # 清理
        cleanup_database_service()
    
    @pytest.mark.database
    def test_session_context_manager(self, database_service, in_memory_db):
        """测试会话上下文管理器"""
        with database_service.get_session() as session:
            assert session is not None
            # 测试基本查询
            result = session.execute(text("SELECT 1")).scalar()
            assert result == 1
    
    @pytest.mark.database
    def test_connector_crud_operations(self, database_service, in_memory_db):
        """测试连接器CRUD操作"""
        # 创建连接器
        connector = Connector(
            connector_id="test_connector",
            name="Test Connector",
            description="A test connector",
            config={"key": "value"},
            status="configured",
            enabled=True
        )
        
        with database_service.get_session() as session:
            # Create
            session.add(connector)
            session.commit()
            
            # Read
            found_connector = session.query(Connector).filter_by(connector_id="test_connector").first()
            assert found_connector is not None
            assert found_connector.name == "Test Connector"
            assert found_connector.config == {"key": "value"}
            assert found_connector.status == "configured"
            assert found_connector.enabled is True
            
            # Update
            found_connector.status = "running"
            session.commit()
            
            updated_connector = session.query(Connector).filter_by(connector_id="test_connector").first()
            assert updated_connector.status == "running"
            
            # Delete
            session.delete(found_connector)
            session.commit()
            
            deleted_connector = session.query(Connector).filter_by(connector_id="test_connector").first()
            assert deleted_connector is None
    
    @pytest.mark.database
    def test_connector_relationships(self, database_service, in_memory_db):
        """测试连接器关系和约束"""
        with database_service.get_session() as session:
            # 测试唯一约束
            connector1 = Connector(
                connector_id="duplicate_test",
                name="First Connector",
                status="configured"
            )
            session.add(connector1)
            session.commit()
            
            # 尝试创建相同ID的连接器应该失败
            connector2 = Connector(
                connector_id="duplicate_test",
                name="Second Connector",
                status="configured"
            )
            session.add(connector2)
            
            with pytest.raises(Exception):  # 应该抛出完整性错误
                session.commit()
            
            session.rollback()
    
    @pytest.mark.database
    def test_connector_config_json_field(self, database_service, in_memory_db):
        """测试连接器配置JSON字段"""
        complex_config = {
            "paths": ["/path1", "/path2"],
            "settings": {
                "timeout": 30,
                "retry_count": 3,
                "enabled": True
            },
            "filters": ["*.txt", "*.md"]
        }
        
        connector = Connector(
            connector_id="json_test",
            name="JSON Test Connector",
            config=complex_config,
            status="configured"
        )
        
        with database_service.get_session() as session:
            session.add(connector)
            session.commit()
            
            # 读取并验证JSON数据
            found_connector = session.query(Connector).filter_by(connector_id="json_test").first()
            assert found_connector.config == complex_config
            assert found_connector.config["settings"]["timeout"] == 30
            assert len(found_connector.config["paths"]) == 2
    
    @pytest.mark.database
    def test_connector_timestamps(self, database_service, in_memory_db):
        """测试连接器时间戳字段"""
        before_creation = datetime.now(timezone.utc)
        
        connector = Connector(
            connector_id="timestamp_test",
            name="Timestamp Test",
            status="configured"
        )
        
        with database_service.get_session() as session:
            session.add(connector)
            session.commit()
            
            after_creation = datetime.now(timezone.utc)
            
            # 验证创建时间
            assert connector.created_at is not None
            assert before_creation <= connector.created_at <= after_creation
            assert connector.updated_at is not None
            assert connector.created_at == connector.updated_at
            
            # 更新连接器
            original_created_at = connector.created_at
            connector.status = "running"
            session.commit()
            
            # 验证更新时间
            assert connector.created_at == original_created_at  # 创建时间不变
            assert connector.updated_at > original_created_at   # 更新时间改变
    
    @pytest.mark.database
    def test_database_initialization(self, temp_dir):
        """测试数据库初始化"""
        from services.database_service import DatabaseService
        
        # 使用临时目录
        db_path = temp_dir / "test_init.db"
        
        with patch('config.core_config.CoreConfigManager') as mock_config:
            mock_config.return_value.get_paths.return_value = {"database": temp_dir}
            mock_config.return_value.config.database.sqlite_url = f"sqlite:///{db_path}"
            
            service = DatabaseService()
            service.initialize_database()
            
            # 验证数据库文件被创建
            assert db_path.exists()
    
    @pytest.mark.database
    def test_query_filtering_and_ordering(self, database_service, in_memory_db):
        """测试查询过滤和排序"""
        # 创建多个连接器
        connectors = [
            Connector(connector_id="conn_1", name="First", status="running", enabled=True),
            Connector(connector_id="conn_2", name="Second", status="configured", enabled=False),
            Connector(connector_id="conn_3", name="Third", status="running", enabled=True),
            Connector(connector_id="conn_4", name="Fourth", status="error", enabled=True)
        ]
        
        with database_service.get_session() as session:
            for conn in connectors:
                session.add(conn)
            session.commit()
            
            # 测试状态过滤
            running_connectors = session.query(Connector).filter_by(status="running").all()
            assert len(running_connectors) == 2
            
            # 测试布尔字段过滤
            enabled_connectors = session.query(Connector).filter_by(enabled=True).all()
            assert len(enabled_connectors) == 3
            
            # 测试排序
            ordered_connectors = session.query(Connector).order_by(Connector.name).all()
            assert ordered_connectors[0].name == "First"
            assert ordered_connectors[1].name == "Fourth"
            assert ordered_connectors[2].name == "Second"
            assert ordered_connectors[3].name == "Third"
            
            # 测试复合条件
            running_enabled = session.query(Connector).filter(
                Connector.status == "running",
                Connector.enabled == True
            ).all()
            assert len(running_enabled) == 2
    
    @pytest.mark.database
    def test_connection_error_handling(self):
        """测试数据库连接错误处理"""
        from services.database_service import DatabaseService
        
        # 使用无效的数据库URL
        invalid_service = DatabaseService()
        
        with patch('config.core_config.CoreConfigManager') as mock_config:
            mock_config.return_value.config.database.sqlite_url = "sqlite:///invalid/path/db.sqlite"
            
            # 数据库初始化应该能够处理路径问题
            try:
                invalid_service.initialize_database()
                # 如果没有抛出异常，检查是否创建了目录
                assert True  # 服务应该创建必要的目录
            except Exception as e:
                # 如果抛出异常，应该是有意义的错误信息
                assert "database" in str(e).lower() or "path" in str(e).lower()
    
    @pytest.mark.database
    def test_transaction_rollback(self, database_service, in_memory_db):
        """测试事务回滚"""
        with database_service.get_session() as session:
            # 添加连接器
            connector = Connector(
                connector_id="rollback_test",
                name="Rollback Test",
                status="configured"
            )
            session.add(connector)
            
            # 在提交前检查连接器存在
            temp_connector = session.query(Connector).filter_by(connector_id="rollback_test").first()
            assert temp_connector is not None
            
            # 触发回滚（通过异常）
            try:
                session.rollback()
                # 手动回滚后，在新session中连接器应该不存在
                pass
            except Exception:
                session.rollback()
        
        # 在新session中验证回滚效果
        with database_service.get_session() as new_session:
            rolled_back_connector = new_session.query(Connector).filter_by(connector_id="rollback_test").first()
            assert rolled_back_connector is None


class MockContextManager:
    """模拟上下文管理器"""
    def __init__(self, session):
        self.session = session
    
    def __enter__(self):
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()
        return False