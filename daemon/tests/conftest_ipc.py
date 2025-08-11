#!/usr/bin/env python3
"""
IPC测试配置和共享fixtures - 纯IPC架构测试支持
替代基于FastAPI的测试架构
"""

import asyncio
import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

# 添加项目路径到系统路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.core_config import CoreConfigManager
from models.database_models import Base, Connector
from tests.ipc_test_client import IPCTestClient, create_mock_daemon_with_routes


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环用于异步测试"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_config_manager(temp_dir):
    """模拟配置管理器"""
    with patch("pathlib.Path.home") as mock_home:
        mock_home.return_value = temp_dir
        config_manager = CoreConfigManager()
        yield config_manager


@pytest.fixture
def test_database(temp_dir):
    """创建测试数据库"""
    db_path = temp_dir / "test.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
    engine.dispose()


@pytest.fixture
def mock_database_service(test_database):
    """模拟数据库服务"""
    from services.database_service import DatabaseService

    service = Mock(spec=DatabaseService)
    service.get_session.return_value.__enter__.return_value = test_database
    service.get_session.return_value.__exit__.return_value = None

    return service


@pytest.fixture
def sample_connector(test_database):
    """创建示例连接器数据"""
    connector = Connector(
        connector_id="test_connector",
        name="Test Connector",
        description="A test connector",
        config={"path": "/test/path", "entry_point": "main.py"},
        status="configured",
        enabled=True,
        auto_start=False,
    )
    test_database.add(connector)
    test_database.commit()
    return connector


@pytest.fixture
def mock_connector_manager():
    """模拟连接器管理器"""
    from services.connectors.connector_manager import ConnectorManager

    manager = Mock(spec=ConnectorManager)
    manager.list_connectors.return_value = [
        {
            "connector_id": "filesystem",
            "name": "FileSystem Connector",
            "status": "running",
            "pid": 1234,
        },
        {
            "connector_id": "clipboard",
            "name": "Clipboard Connector",
            "status": "configured",
            "pid": None,
        },
    ]
    manager.start_connector = AsyncMock(return_value=True)
    manager.stop_connector = AsyncMock(return_value=True)
    manager.scan_directory_for_connectors.return_value = []

    return manager


@pytest.fixture
def mock_process_manager():
    """模拟进程管理器"""
    from services.connectors.process_manager import ProcessManager

    manager = Mock(spec=ProcessManager)
    manager.start_process = AsyncMock(return_value=1234)
    manager.stop_process = AsyncMock(return_value=True)
    manager.get_process_info.return_value = {
        "pid": 1234,
        "status": "running",
        "cpu_percent": 1.5,
        "memory_percent": 2.0,
    }

    return manager


@pytest.fixture
async def mock_ipc_daemon():
    """创建模拟IPC daemon"""
    daemon, socket_path = create_mock_daemon_with_routes()
    await daemon.start()
    yield daemon, socket_path
    daemon.stop()


@pytest.fixture
async def ipc_client(mock_ipc_daemon):
    """创建IPC测试客户端"""
    daemon, socket_path = mock_ipc_daemon

    # 等待daemon启动
    await asyncio.sleep(0.1)

    client = IPCTestClient(socket_path)
    yield client
    client.close()


@pytest.fixture
def ipc_client_sync(ipc_client):
    """同步版本的IPC客户端（用于同步测试）"""
    return ipc_client


@pytest.fixture
def api_headers():
    """API请求头（IPC模式下保持兼容性）"""
    return {"Content-Type": "application/json", "Accept": "application/json"}


@pytest.fixture
def sample_connector_config():
    """示例连接器配置"""
    return {
        "connector_id": "test_connector",
        "display_name": "Test Connector",
        "config": {"watch_paths": ["/test/path"], "interval": 60},
        "auto_start": True,
    }


@pytest.fixture
def sample_connector_discovery_response():
    """示例连接器发现响应"""
    return {
        "success": True,
        "data": {
            "connectors": [
                {
                    "connector_id": "filesystem",
                    "name": "FileSystem Connector",
                    "display_name": "文件系统连接器",
                    "description": "监控文件系统变化的连接器",
                    "category": "official",
                    "version": "1.0.0",
                    "is_registered": False,
                }
            ],
            "total": 1,
        },
    }


@pytest.fixture
def mock_ipc_server():
    """模拟IPC服务器fixture"""
    from services.ipc_server import IPCServer

    server = Mock(spec=IPCServer)
    server.start = AsyncMock()
    server.stop = AsyncMock()
    server.is_running = True

    return server


@pytest.fixture
def pure_ipc_daemon(mock_config_manager, mock_database_service, mock_connector_manager):
    """创建纯IPC daemon测试实例"""
    # 设置测试环境变量
    os.environ["TESTING"] = "true"
    os.environ["IPC_ONLY"] = "true"

    # 模拟所有依赖
    with patch(
        "services.database_service.get_database_service",
        return_value=mock_database_service,
    ):
        with patch(
            "services.connectors.connector_manager.get_connector_manager",
            return_value=mock_connector_manager,
        ):
            from services.ipc_server import get_ipc_server

            # 创建模拟IPC服务器
            ipc_server = get_ipc_server()
            yield ipc_server

    # 清理环境变量
    os.environ.pop("TESTING", None)
    os.environ.pop("IPC_ONLY", None)


# 辅助函数
def create_test_connector(session, **kwargs):
    """创建测试连接器的辅助函数"""
    defaults = {
        "connector_id": "test_id",
        "name": "Test Name",
        "description": "Test Description",
        "config": {},
        "status": "configured",
        "enabled": True,
        "auto_start": False,
    }
    defaults.update(kwargs)

    connector = Connector(**defaults)
    session.add(connector)
    session.commit()
    return connector


# IPC专用的测试工具函数
async def wait_for_ipc_server(socket_path: str, timeout: float = 5.0) -> bool:
    """等待IPC服务器启动"""
    start_time = asyncio.get_event_loop().time()

    while asyncio.get_event_loop().time() - start_time < timeout:
        try:
            client = IPCTestClient(socket_path)
            if await client.connect():
                client.close()
                return True
        except Exception:
            pass
        await asyncio.sleep(0.1)

    return False


def create_ipc_test_environment(temp_dir: Path) -> dict:
    """创建IPC测试环境配置"""
    socket_path = temp_dir / "test_daemon.sock"

    return {
        "socket_path": str(socket_path),
        "app_data": temp_dir / "app_data",
        "config": temp_dir / "config",
        "logs": temp_dir / "logs",
        "database": temp_dir / "database",
    }
