#!/usr/bin/env python3
"""
配置系统验收测试 - Session V61
验证重构后的配置系统功能完整性和稳定性
"""

import pytest
import tempfile
import shutil
import os
import yaml
from pathlib import Path
from unittest.mock import patch

# 添加项目路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.core_config import CoreConfigManager, AppConfig
from config.error_handling import ConfigValidationError, ConfigFileError


class TestCoreConfigManager:
    """核心配置管理器测试"""
    
    @pytest.fixture
    def temp_config_root(self):
        """临时配置根目录"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_config_data(self):
        """示例配置数据"""
        return {
            "app_name": "Test Linch Mind",
            "version": "0.2.0",
            "debug": True,
            "server": {
                "host": "127.0.0.1",
                "port": 8080,
                "reload": False
            },
            "database": {
                "sqlite_url": "sqlite:///test.db",
                "embedding_model": "test-model"
            },
            "connectors": {
                "registry_url": "http://test.registry.com",
                "config_dir": "/test/connectors"
            }
        }
    
    def test_default_config_creation(self, temp_config_root):
        """测试默认配置创建"""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = temp_config_root
            
            config_manager = CoreConfigManager()
            
            # 验证默认配置
            assert config_manager.config.app_name == "Linch Mind"
            assert config_manager.config.version == "0.1.0"
            assert config_manager.config.server.port == 58471
            assert config_manager.config.debug is False
            
            # 验证配置文件创建
            assert config_manager.primary_config_path.exists()
    
    def test_yaml_config_loading(self, temp_config_root, sample_config_data):
        """测试YAML配置加载"""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = temp_config_root
            
            # 创建配置文件
            config_dir = temp_config_root / ".linch-mind" / "config"
            config_dir.mkdir(parents=True)
            config_file = config_dir / "app.yaml"
            
            with open(config_file, 'w') as f:
                yaml.dump(sample_config_data, f)
            
            config_manager = CoreConfigManager()
            
            # 验证配置加载
            assert config_manager.config.app_name == "Test Linch Mind"
            assert config_manager.config.version == "0.2.0"
            assert config_manager.config.debug is True
            assert config_manager.config.server.host == "127.0.0.1"
            assert config_manager.config.server.port == 8080
    
    def test_fallback_config_migration(self, temp_config_root, sample_config_data):
        """测试项目根目录配置迁移"""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = temp_config_root
            
            # 在项目根目录创建配置文件
            project_config = temp_config_root / "linch-mind.config.yaml"
            with open(project_config, 'w') as f:
                yaml.dump(sample_config_data, f)
            
            # 模拟项目根目录
            with patch.object(CoreConfigManager, '_CoreConfigManager__init__') as mock_init:
                def mock_init_func(self, config_root=None):
                    self.config_root = temp_config_root
                    self.app_data_dir = temp_config_root / ".linch-mind"
                    self.app_data_dir.mkdir(exist_ok=True)
                    
                    self.config_dir = self.app_data_dir / "config"
                    self.data_dir = self.app_data_dir / "data"
                    self.logs_dir = self.app_data_dir / "logs"
                    self.db_dir = self.app_data_dir / "db"
                    
                    for dir_path in [self.config_dir, self.data_dir, self.logs_dir, self.db_dir]:
                        dir_path.mkdir(exist_ok=True)
                    
                    self.primary_config_path = self.config_dir / "app.yaml"
                    self.fallback_config_path = self.config_root / "linch-mind.config.yaml"
                    
                    self.config = self._load_config()
                    self._setup_dynamic_paths()
                    self._apply_env_overrides()
                
                mock_init.side_effect = mock_init_func
                config_manager = CoreConfigManager()
                
                # 验证迁移成功
                assert config_manager.config.app_name == "Test Linch Mind"
                assert config_manager.primary_config_path.exists()
    
    def test_environment_variable_overrides(self, temp_config_root):
        """测试环境变量覆盖"""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = temp_config_root
            
            # 设置环境变量
            env_vars = {
                'LINCH_SERVER_PORT': '9999',
                'LINCH_SERVER_HOST': 'test.host',
                'LINCH_DEBUG': 'true',
                'REGISTRY_URL': 'http://test.override.com'
            }
            
            with patch.dict(os.environ, env_vars):
                config_manager = CoreConfigManager()
                
                # 验证环境变量覆盖
                assert config_manager.config.server.port == 9999
                assert config_manager.config.server.host == "test.host"
                assert config_manager.config.debug is True
                assert config_manager.config.connectors.registry_url == "http://test.override.com"
    
    def test_config_validation(self, temp_config_root):
        """测试配置验证"""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = temp_config_root
            
            config_manager = CoreConfigManager()
            
            # 测试有效配置
            errors = config_manager.validate_config()
            assert len(errors) == 0
            
            # 测试无效端口
            config_manager.config.server.port = 99999
            errors = config_manager.validate_config()
            assert len(errors) > 0
            assert any("port" in error.lower() for error in errors)
    
    def test_config_reload(self, temp_config_root, sample_config_data):
        """测试配置重载"""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = temp_config_root
            
            config_manager = CoreConfigManager()
            original_app_name = config_manager.config.app_name
            
            # 修改配置文件
            with open(config_manager.primary_config_path, 'w') as f:
                yaml.dump(sample_config_data, f)
            
            # 重载配置
            success = config_manager.reload_config()
            assert success
            assert config_manager.config.app_name != original_app_name
            assert config_manager.config.app_name == "Test Linch Mind"
    
    def test_invalid_yaml_handling(self, temp_config_root):
        """测试无效YAML处理"""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = temp_config_root
            
            # 创建无效YAML文件
            config_dir = temp_config_root / ".linch-mind" / "config"
            config_dir.mkdir(parents=True)
            config_file = config_dir / "app.yaml"
            
            with open(config_file, 'w') as f:
                f.write("invalid: yaml: content: [")
            
            # 应该降级到默认配置
            config_manager = CoreConfigManager()
            assert config_manager.config.app_name == "Linch Mind"  # 默认值
    
    def test_path_setup(self, temp_config_root):
        """测试路径设置"""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = temp_config_root
            
            config_manager = CoreConfigManager()
            paths = config_manager.get_paths()
            
            # 验证所有必需路径存在
            required_paths = ["app_data", "config", "data", "logs", "database"]
            for path_name in required_paths:
                assert path_name in paths
                assert paths[path_name].exists()
    
    def test_server_info(self, temp_config_root):
        """测试服务器信息"""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = temp_config_root
            
            config_manager = CoreConfigManager()
            server_info = config_manager.get_server_info()
            
            # 验证服务器信息
            required_fields = ["app_name", "version", "host", "port", "started_at", "config_source"]
            for field in required_fields:
                assert field in server_info
            
            assert server_info["app_name"] == "Linch Mind"
            assert server_info["port"] == 58471


class TestConfigValidation:
    """配置验证测试"""
    
    def test_port_validation(self):
        """测试端口验证"""
        from config.error_handling import validate_port_range
        
        # 有效端口
        assert validate_port_range("test_port", 8080) == 8080
        
        # 无效端口
        with pytest.raises(ConfigValidationError):
            validate_port_range("test_port", 80)  # 太小
        
        with pytest.raises(ConfigValidationError):
            validate_port_range("test_port", 99999)  # 太大
        
        with pytest.raises(ConfigValidationError):
            validate_port_range("test_port", "invalid")  # 非整数
    
    def test_required_field_validation(self):
        """测试必需字段验证"""
        from config.error_handling import validate_required_field
        
        # 有效值
        assert validate_required_field("test_field", "value") == "value"
        assert validate_required_field("test_field", 123, int) == 123
        
        # 无效值
        with pytest.raises(ConfigValidationError):
            validate_required_field("test_field", None)
        
        with pytest.raises(ConfigValidationError):
            validate_required_field("test_field", "")
        
        with pytest.raises(ConfigValidationError):
            validate_required_field("test_field", "value", int)  # 类型不匹配


if __name__ == "__main__":
    pytest.main([__file__, "-v"])