#!/usr/bin/env python3
"""
配置上下文抽象 - 企业级最佳实践实现
实现依赖倒置和关注点分离
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class ConfigContext(ABC):
    """配置上下文抽象接口 - 定义配置系统需要的环境信息"""

    @abstractmethod
    def get_config_dir(self) -> Path:
        """获取配置文件目录"""

    @abstractmethod
    def get_data_dir(self) -> Path:
        """获取数据目录"""

    @abstractmethod
    def get_logs_dir(self) -> Path:
        """获取日志目录"""

    @abstractmethod
    def get_database_dir(self) -> Path:
        """获取数据库目录"""

    @abstractmethod
    def get_database_url(self) -> str:
        """获取数据库URL"""

    @abstractmethod
    def get_chroma_persist_directory(self) -> str:
        """获取ChromaDB持久化目录"""

    @abstractmethod
    def is_test_environment(self) -> bool:
        """是否为测试环境"""

    @abstractmethod
    def get_vector_index_path(self) -> str:
        """获取向量索引路径"""

    @abstractmethod
    def get_connectors_dir(self) -> Path:
        """获取连接器目录"""

    @abstractmethod
    def is_debug_enabled(self) -> bool:
        """是否启用调试模式"""

    @abstractmethod
    def get_environment_name(self) -> str:
        """获取当前环境名称"""


class ProductionConfigContext(ConfigContext):
    """生产环境配置上下文 - 使用EnvironmentManager"""

    def __init__(self):
        from core.environment_manager import get_environment_manager

        self.env_manager = get_environment_manager()
        self.env_config = self.env_manager.current_config

    def get_config_dir(self) -> Path:
        return self.env_config.config_dir

    def get_data_dir(self) -> Path:
        return self.env_config.data_dir

    def get_logs_dir(self) -> Path:
        return self.env_config.logs_dir

    def get_database_dir(self) -> Path:
        return self.env_config.database_dir

    def get_database_url(self) -> str:
        return self.env_manager.get_database_url()

    def get_chroma_persist_directory(self) -> str:
        return self.env_manager.get_chroma_persist_directory()

    def is_test_environment(self) -> bool:
        return False  # 生产环境

    def get_vector_index_path(self) -> str:
        return self.env_manager.get_vector_index_path()

    def get_connectors_dir(self) -> Path:
        return self.env_config.base_path / "connectors"

    def is_debug_enabled(self) -> bool:
        return self.env_manager.is_debug_enabled()

    def get_environment_name(self) -> str:
        return self.env_manager.current_environment.value


class TestConfigContext(ConfigContext):
    """测试环境配置上下文 - 使用提供的根目录"""

    def __init__(self, test_root: Path):
        self.test_root = test_root
        self.app_data_dir = test_root / ".linch-mind"

        # 确保测试目录存在
        for dir_path in [
            self.get_config_dir(),
            self.get_data_dir(),
            self.get_logs_dir(),
            self.get_database_dir(),
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def get_config_dir(self) -> Path:
        return self.app_data_dir / "config"

    def get_data_dir(self) -> Path:
        return self.app_data_dir / "data"

    def get_logs_dir(self) -> Path:
        return self.app_data_dir / "logs"

    def get_database_dir(self) -> Path:
        return self.app_data_dir / "database"

    def get_database_url(self) -> str:
        return "sqlite:///:memory:"  # 测试环境使用内存数据库

    def get_chroma_persist_directory(self) -> str:
        return ":memory:"  # 测试环境使用内存存储

    def is_test_environment(self) -> bool:
        return True  # 测试环境

    def get_vector_index_path(self) -> str:
        return str(self.get_data_dir() / "vectors" / "faiss_index.bin")

    def get_connectors_dir(self) -> Path:
        return self.test_root / "connectors"

    def is_debug_enabled(self) -> bool:
        return True  # 测试环境默认启用调试

    def get_environment_name(self) -> str:
        return "test"


def create_config_context(test_root: Optional[Path] = None) -> ConfigContext:
    """配置上下文工厂函数"""
    if test_root is not None:
        return TestConfigContext(test_root)
    else:
        return ProductionConfigContext()
