#!/usr/bin/env python3
"""
核心配置管理 - Session V61 简化重构
简化环境变量处理，移除复杂的正则表达式，专注稳定性
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

from .error_handling import (
    get_logger, 
    ConfigFileError, 
    ConfigValidationError,
    DependencyError,
    safe_operation,
    validate_required_field,
    validate_port_range
)

logger = get_logger(__name__)


@dataclass
class ServerConfig:
    """服务器配置"""
    host: str = "0.0.0.0"
    port: int = 50001
    port_range: List[int] = field(default_factory=lambda: [50001, 51000])
    reload: bool = True
    log_level: str = "info"


@dataclass 
class DatabaseConfig:
    """数据库配置"""
    sqlite_url: str = ""
    chroma_persist_directory: str = ""
    embedding_model: str = "all-MiniLM-L6-v2"
    vector_dimension: int = 384


@dataclass
class ConnectorConfig:
    """连接器配置"""
    config_dir: str = "connectors"
    filesystem_enabled: bool = True
    clipboard_enabled: bool = False


@dataclass
class AIConfig:
    """AI配置"""
    default_embedding_model: str = "all-MiniLM-L6-v2"
    max_search_results: int = 10
    recommendation_threshold: float = 0.7
    providers: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AppConfig:
    """应用配置 - 核心配置入口"""
    app_name: str = "Linch Mind"
    version: str = "0.1.0"
    description: str = "Personal AI Life Assistant API"
    debug: bool = False
    
    # 子配置
    server: ServerConfig = field(default_factory=ServerConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    connectors: ConnectorConfig = field(default_factory=ConnectorConfig)
    ai: AIConfig = field(default_factory=AIConfig)


class CoreConfigManager:
    """核心配置管理器
    
    Session V61 简化原则:
    1. 移除复杂的环境变量正则处理
    2. 使用标准的 os.getenv() 处理环境变量
    3. 单一配置文件路径策略
    4. 清晰的错误处理和日志记录
    """
    
    def __init__(self, config_root: Optional[Path] = None):
        self.config_root = config_root or Path(__file__).parent.parent.parent
        
        # 应用数据目录 - 统一使用用户目录
        self.app_data_dir = Path.home() / ".linch-mind"
        self.app_data_dir.mkdir(exist_ok=True)
        
        # 子目录
        self.config_dir = self.app_data_dir / "config"
        self.data_dir = self.app_data_dir / "data"
        self.logs_dir = self.app_data_dir / "logs"
        self.db_dir = self.app_data_dir / "db"
        
        for dir_path in [self.config_dir, self.data_dir, self.logs_dir, self.db_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # 配置文件路径 - 优先级明确
        self.primary_config_path = self.config_dir / "app.yaml"
        self.fallback_config_path = self.config_root / "linch-mind.config.yaml"
        
        # 加载配置
        self.config = self._load_config()
        self._setup_dynamic_paths()
        self._apply_env_overrides()
        
        logger.info(f"Core config loaded from: {self._get_active_config_path()}")
    
    def _get_active_config_path(self) -> Path:
        """获取当前活跃的配置文件路径"""
        if self.primary_config_path.exists():
            return self.primary_config_path
        elif self.fallback_config_path.exists():
            return self.fallback_config_path
        else:
            return self.primary_config_path  # 将要创建的路径
    
    def _load_config(self) -> AppConfig:
        """加载配置 - 简化版本，去除复杂的环境变量处理"""
        
        # 1. 尝试从主配置路径加载
        if self.primary_config_path.exists():
            try:
                return self._load_from_yaml(self.primary_config_path)
            except Exception as e:
                logger.error(f"Failed to load primary config: {e}")
        
        # 2. 尝试从项目根目录配置加载
        if self.fallback_config_path.exists():
            try:
                config = self._load_from_yaml(self.fallback_config_path)
                # 保存到主配置路径
                self._save_config(config, self.primary_config_path)
                logger.info("Migrated config from project root to user directory")
                return config
            except Exception as e:
                logger.error(f"Failed to load fallback config: {e}")
        
        # 3. 创建默认配置
        config = AppConfig()
        self._save_config(config, self.primary_config_path)
        logger.info("Created default configuration")
        return config
    
    def _load_from_yaml(self, config_path: Path) -> AppConfig:
        """从YAML文件加载配置 - 增强错误处理"""
        def load_operation():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    yaml_data = yaml.safe_load(f)
                
                if not yaml_data:
                    yaml_data = {}
                
                return self._dict_to_config(yaml_data)
            except FileNotFoundError:
                raise ConfigFileError(
                    file_path=str(config_path),
                    operation="read",
                    reason="File not found"
                )
            except yaml.YAMLError as e:
                raise ConfigFileError(
                    file_path=str(config_path),
                    operation="parse",
                    reason=f"Invalid YAML syntax: {e}"
                )
            except PermissionError:
                raise ConfigFileError(
                    file_path=str(config_path),
                    operation="read",
                    reason="Permission denied"
                )
        
        return safe_operation(
            operation_name=f"load_config_from_{config_path.name}",
            operation_func=load_operation,
            logger=logger,
            error_type=ConfigFileError,
            reraise=True
        )
    
    def _dict_to_config(self, data: Dict[str, Any]) -> AppConfig:
        """将字典转换为配置对象 - 增强错误处理"""
        try:
            # 处理嵌套配置，确保都是字典类型
            server_data = data.get("server", {})
            database_data = data.get("database", {})
            connectors_data = data.get("connectors", {})
            ai_data = data.get("ai", {})
            
            # 类型检查和修正
            if not isinstance(server_data, dict):
                server_data = {}
            if not isinstance(database_data, dict):
                database_data = {}
            if not isinstance(connectors_data, dict):
                connectors_data = {}
            if not isinstance(ai_data, dict):
                ai_data = {}
            
            return AppConfig(
                app_name=data.get("app_name", "Linch Mind"),
                version=data.get("version", "0.1.0"),
                description=data.get("description", "Personal AI Life Assistant API"),
                debug=bool(data.get("debug", False)),
                
                server=ServerConfig(**server_data),
                database=DatabaseConfig(**database_data),
                connectors=ConnectorConfig(**connectors_data),
                ai=AIConfig(**ai_data)
            )
        except Exception as e:
            logger.error(f"Failed to parse config dict: {e}")
            logger.warning("Using default configuration due to parsing error")
            return AppConfig()
    
    def _save_config(self, config: AppConfig, config_path: Path):
        """保存配置文件 - 改进格式化"""
        config_dict = asdict(config)
        
        # 简化文件头
        yaml_content = f"""# Linch Mind Configuration
# Generated: {datetime.now(timezone.utc).isoformat()}

"""
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(yaml_content)
                yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            logger.info(f"Configuration saved to: {config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise
    
    def _setup_dynamic_paths(self):
        """设置动态路径配置 - 简化版本"""
        # 设置数据库路径
        self.config.database.sqlite_url = f"sqlite:///{self.db_dir}/linch_mind.db"
        self.config.database.chroma_persist_directory = str(self.db_dir / "chromadb")
        
        # 设置连接器目录路径 - 使用用户目录
        if self.config.connectors.config_dir == "connectors":
            user_connectors_dir = self.app_data_dir / "connectors"
            user_connectors_dir.mkdir(exist_ok=True)
            self.config.connectors.config_dir = str(user_connectors_dir)
    
    def _apply_env_overrides(self):
        """应用环境变量覆盖 - 移除，环境变量处理过度复杂"""
        # 移除环境变量覆盖功能，简化配置管理
        pass
    
    def save_config(self):
        """保存当前配置"""
        self._save_config(self.config, self.primary_config_path)
    
    def reload_config(self) -> bool:
        """重新加载配置"""
        try:
            old_config = self.config
            self.config = self._load_config()
            self._setup_dynamic_paths()
            self._apply_env_overrides()
            logger.info("Configuration reloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
            self.config = old_config  # 恢复旧配置
            return False
    
    def get_paths(self) -> Dict[str, Path]:
        """获取各种路径"""
        return {
            "app_data": self.app_data_dir,
            "config": self.config_dir,
            "data": self.data_dir,
            "logs": self.logs_dir,
            "database": self.db_dir,
            "primary_config": self.primary_config_path,
            "fallback_config": self.fallback_config_path
        }
    
    def get_server_info(self) -> Dict[str, Any]:
        """获取服务器信息"""
        return {
            "app_name": self.config.app_name,
            "version": self.config.version,
            "host": self.config.server.host,
            "port": self.config.server.port,
            "debug": self.config.debug,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "config_source": str(self._get_active_config_path())
        }
    
    def validate_config(self) -> List[str]:
        """验证配置完整性 - 使用统一验证器"""
        errors = []
        
        try:
            # 验证服务器配置
            validate_port_range("server.port", self.config.server.port)
            validate_required_field("server.host", self.config.server.host, str)
        except ConfigValidationError as e:
            errors.append(str(e))
        
        try:
            # 验证连接器配置目录
            connectors_dir = Path(self.config.connectors.config_dir)
            if not connectors_dir.exists():
                logger.warning(
                    "Connectors directory missing, creating",
                    path=str(connectors_dir)
                )
                try:
                    connectors_dir.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    errors.append(f"Cannot create connectors directory: {e}")
        except Exception as e:
            errors.append(f"Connectors directory validation failed: {e}")
        
        try:
            # 验证数据库配置
            validate_required_field("database.sqlite_url", self.config.database.sqlite_url, str)
        except ConfigValidationError as e:
            errors.append(str(e))
        
        try:
            # 验证ChromaDB目录路径
            chroma_dir = Path(self.config.database.chroma_persist_directory)
            chroma_dir.mkdir(parents=True, exist_ok=True)
            logger.debug("ChromaDB directory validated", path=str(chroma_dir))
        except Exception as e:
            errors.append(f"Cannot create ChromaDB directory: {e}")
        
        # 记录验证结果
        if errors:
            logger.error("Configuration validation failed", error_count=len(errors))
            for error in errors:
                logger.error("Validation error", error=error)
        else:
            logger.info("Configuration validation passed")
        
        return errors
    
    
    def _is_port_available(self, port: int) -> bool:
        """检查端口是否可用"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def get_available_port(self) -> int:
        """获取可用端口，自动处理端口冲突
        
        Returns:
            int: 可用的端口号
        """
        # 首先尝试配置的端口
        preferred_port = self.config.server.port
        if self._is_port_available(preferred_port):
            # 写入端口文件
            self._write_port_file(preferred_port)
            logger.info(f"Using preferred port: {preferred_port}")
            return preferred_port
        
        # 如果配置端口不可用，在端口范围内查找
        port_range = self.config.server.port_range
        start_port, end_port = port_range[0], port_range[1]
        
        logger.warning(f"Preferred port {preferred_port} is not available, searching in range {start_port}-{end_port}")
        
        for port in range(start_port, end_port + 1):
            if self._is_port_available(port):
                # 更新配置中的端口
                self.config.server.port = port
                # 写入端口文件
                self._write_port_file(port)
                logger.info(f"Found available port: {port}")
                return port
        
        # 如果范围内没有可用端口，使用系统分配
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 0))
            dynamic_port = s.getsockname()[1]
            
        # 更新配置
        self.config.server.port = dynamic_port
        # 写入端口文件
        self._write_port_file(dynamic_port)
        logger.warning(f"Using system-assigned port: {dynamic_port}")
        return dynamic_port
    
    def _write_port_file(self, port: int):
        """写入端口文件供其他组件读取"""
        port_file = self.app_data_dir / "daemon.port"
        try:
            with open(port_file, 'w') as f:
                f.write(str(port))
            logger.debug(f"Port file written: {port_file} -> {port}")
        except Exception as e:
            logger.error(f"Failed to write port file: {e}")
    
    def read_port_file(self) -> Optional[int]:
        """读取端口文件
        
        Returns:
            Optional[int]: 端口号，如果文件不存在或无效则返回None
        """
        port_file = self.app_data_dir / "daemon.port"
        if not port_file.exists():
            return None
        
        try:
            with open(port_file, 'r') as f:
                port = int(f.read().strip())
            logger.debug(f"Read port from file: {port}")
            return port
        except (ValueError, IOError) as e:
            logger.warning(f"Failed to read port file: {e}")
            return None
    
    def cleanup_port_file(self):
        """清理端口文件"""
        port_file = self.app_data_dir / "daemon.port"
        if port_file.exists():
            try:
                port_file.unlink()
                logger.debug("Port file cleaned up")
            except Exception as e:
                logger.warning(f"Failed to cleanup port file: {e}")
    
    def get_port(self) -> int:
        """获取配置的端口"""
        return self.config.server.port


# 全局单例
_core_config_manager = None

def get_core_config() -> CoreConfigManager:
    """获取核心配置管理器单例"""
    global _core_config_manager
    if _core_config_manager is None:
        _core_config_manager = CoreConfigManager()
    return _core_config_manager


# 便捷访问函数
def get_server_config() -> ServerConfig:
    """获取服务器配置"""
    return get_core_config().config.server


def get_database_config() -> DatabaseConfig:
    """获取数据库配置"""
    return get_core_config().config.database


def get_connector_config() -> ConnectorConfig:
    """获取连接器配置"""
    return get_core_config().config.connectors


def get_ai_config() -> AIConfig:
    """获取AI配置"""
    return get_core_config().config.ai