#!/usr/bin/env python3
"""
统一配置管理器
整合分散的配置加载系统：
- ConfigLoader (通用配置加载)
- CoreConfigManager (应用配置管理) 
- 各种专门配置管理器
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from enum import Enum

logger = logging.getLogger(__name__)


class ConfigFormat(Enum):
    """配置文件格式"""
    TOML = "toml"
    JSON = "json"
    YAML = "yaml"
    AUTO = "auto"


class ConfigSource(Enum):
    """配置来源"""
    FILE = "file"
    ENVIRONMENT = "environment"
    DATABASE = "database"
    DEFAULT = "default"


@dataclass
class ConfigEntry:
    """配置条目"""
    key: str
    value: Any
    source: ConfigSource
    file_path: Optional[str] = None
    last_updated: Optional[str] = None


@dataclass 
class ConfigProfile:
    """配置档案"""
    name: str
    entries: Dict[str, ConfigEntry] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class UnifiedConfigManager:
    """统一配置管理器
    
    功能:
    - 统一配置加载 (TOML/JSON/YAML)
    - 多源配置合并 (文件/环境变量/数据库/默认值)
    - 配置验证和回退
    - 配置热重载
    - 环境感知配置
    """

    def __init__(self, config_root: Optional[Path] = None):
        # 配置根目录
        if config_root:
            self.config_root = Path(config_root)
        else:
            # 环境感知的配置根目录
            from core.environment_manager import get_environment_manager
            env_manager = get_environment_manager()
            self.config_root = env_manager.current_config.config_dir

        # 配置档案存储
        self._profiles: Dict[str, ConfigProfile] = {}
        self._default_profile = "default"
        self._active_profile = "default"

        # 缓存和状态
        self._config_cache: Dict[str, Any] = {}
        self._file_watchers: Dict[str, float] = {}  # 文件路径 -> 修改时间
        self._initialized = False

    def initialize(self) -> bool:
        """初始化配置管理器"""
        try:
            # 确保配置根目录存在
            self.config_root.mkdir(parents=True, exist_ok=True)

            # 创建默认配置档案
            self._profiles[self._default_profile] = ConfigProfile(name=self._default_profile)

            # 加载默认配置
            self._load_default_configurations()

            # 加载环境特定配置
            self._load_environment_configurations()

            self._initialized = True
            logger.info(f"统一配置管理器初始化完成: {self.config_root}")
            return True

        except Exception as e:
            logger.error(f"统一配置管理器初始化失败: {e}")
            return False

    def _load_default_configurations(self):
        """加载默认配置"""
        default_configs = {
            # 应用基础配置
            "app.name": "Linch Mind",
            "app.version": "1.0.0",
            "app.debug": False,
            
            # 数据库配置
            "database.type": "sqlite",
            "database.timeout": 30,
            "database.pool_size": 10,
            
            # IPC配置
            "ipc.timeout": 30,
            "ipc.max_connections": 100,
            "ipc.buffer_size": 8192,
            
            # 日志配置
            "logging.level": "INFO",
            "logging.format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            
            # 连接器配置
            "connectors.auto_discovery": True,
            "connectors.health_check_interval": 60,
            "connectors.max_retry_attempts": 3,
        }

        profile = self._profiles[self._default_profile]
        for key, value in default_configs.items():
            profile.entries[key] = ConfigEntry(
                key=key,
                value=value,
                source=ConfigSource.DEFAULT
            )

    def _load_environment_configurations(self):
        """加载环境特定配置"""
        try:
            # 检查常见配置文件
            config_files = [
                self.config_root / "config.toml",
                self.config_root / "config.json", 
                self.config_root / "config.yaml",
                self.config_root / "config.yml",
            ]

            for config_file in config_files:
                if config_file.exists():
                    self.load_config_file(config_file)
                    break
            else:
                logger.info("未找到环境配置文件，使用默认配置")

        except Exception as e:
            logger.warning(f"加载环境配置失败: {e}")

    def load_config_file(
        self, 
        file_path: Union[str, Path], 
        profile_name: Optional[str] = None,
        format: ConfigFormat = ConfigFormat.AUTO
    ) -> bool:
        """加载配置文件"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.warning(f"配置文件不存在: {file_path}")
                return False

            # 确定配置格式
            if format == ConfigFormat.AUTO:
                format = self._detect_format(file_path)

            # 加载配置内容
            config_data = self._load_file_by_format(file_path, format)
            if not config_data:
                return False

            # 确定配置档案
            if not profile_name:
                profile_name = self._active_profile

            if profile_name not in self._profiles:
                self._profiles[profile_name] = ConfigProfile(name=profile_name)

            # 将配置数据展平并存储
            flat_config = self._flatten_config(config_data)
            profile = self._profiles[profile_name]
            
            for key, value in flat_config.items():
                profile.entries[key] = ConfigEntry(
                    key=key,
                    value=value,
                    source=ConfigSource.FILE,
                    file_path=str(file_path),
                    last_updated=self._get_file_mtime(file_path)
                )

            # 记录文件监控
            self._file_watchers[str(file_path)] = file_path.stat().st_mtime

            logger.info(f"配置文件加载成功: {file_path} -> {profile_name}")
            return True

        except Exception as e:
            logger.error(f"加载配置文件失败 [{file_path}]: {e}")
            return False

    def _detect_format(self, file_path: Path) -> ConfigFormat:
        """检测配置文件格式"""
        suffix = file_path.suffix.lower()
        if suffix == '.toml':
            return ConfigFormat.TOML
        elif suffix == '.json':
            return ConfigFormat.JSON
        elif suffix in ['.yaml', '.yml']:
            return ConfigFormat.YAML
        else:
            # 尝试通过内容检测
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('{'):
                        return ConfigFormat.JSON
                    elif '=' in first_line or '[' in first_line:
                        return ConfigFormat.TOML
                    else:
                        return ConfigFormat.YAML
            except:
                return ConfigFormat.JSON  # 默认

    def _load_file_by_format(self, file_path: Path, format: ConfigFormat) -> Optional[Dict[str, Any]]:
        """根据格式加载文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if format == ConfigFormat.TOML:
                    import tomllib
                    with open(file_path, 'rb') as fb:
                        return tomllib.load(fb)
                elif format == ConfigFormat.JSON:
                    return json.load(f)
                elif format == ConfigFormat.YAML:
                    import yaml
                    return yaml.safe_load(f)
                else:
                    raise ValueError(f"不支持的配置格式: {format}")

        except ImportError as e:
            logger.error(f"缺少必要的库来解析 {format} 格式: {e}")
            return None
        except Exception as e:
            logger.error(f"解析配置文件失败 [{file_path}]: {e}")
            return None

    def _flatten_config(self, config: Dict[str, Any], prefix: str = '') -> Dict[str, Any]:
        """展平嵌套配置"""
        flat = {}
        
        for key, value in config.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                # 递归处理嵌套字典
                nested_flat = self._flatten_config(value, full_key)
                flat.update(nested_flat)
            else:
                flat[full_key] = value
        
        return flat

    def _get_file_mtime(self, file_path: Path) -> str:
        """获取文件修改时间"""
        try:
            from datetime import datetime
            mtime = file_path.stat().st_mtime
            return datetime.fromtimestamp(mtime).isoformat()
        except:
            return ""

    def get_config(
        self, 
        key: str, 
        default: Any = None, 
        profile_name: Optional[str] = None
    ) -> Any:
        """获取配置值"""
        try:
            if not profile_name:
                profile_name = self._active_profile

            # 检查缓存
            cache_key = f"{profile_name}:{key}"
            if cache_key in self._config_cache:
                return self._config_cache[cache_key]

            # 从档案中获取
            if profile_name in self._profiles:
                profile = self._profiles[profile_name]
                if key in profile.entries:
                    value = profile.entries[key].value
                    self._config_cache[cache_key] = value
                    return value

            # 回退到默认档案
            if profile_name != self._default_profile and self._default_profile in self._profiles:
                default_profile = self._profiles[self._default_profile]
                if key in default_profile.entries:
                    value = default_profile.entries[key].value
                    self._config_cache[cache_key] = value
                    return value

            # 返回默认值
            return default

        except Exception as e:
            logger.error(f"获取配置失败 [{key}]: {e}")
            return default

    def set_config(
        self, 
        key: str, 
        value: Any, 
        profile_name: Optional[str] = None,
        source: ConfigSource = ConfigSource.DATABASE
    ):
        """设置配置值"""
        try:
            if not profile_name:
                profile_name = self._active_profile

            if profile_name not in self._profiles:
                self._profiles[profile_name] = ConfigProfile(name=profile_name)

            profile = self._profiles[profile_name]
            profile.entries[key] = ConfigEntry(
                key=key,
                value=value,
                source=source,
                last_updated=self._get_current_time()
            )

            # 清除缓存
            cache_key = f"{profile_name}:{key}"
            self._config_cache.pop(cache_key, None)

            logger.debug(f"设置配置: {key} = {value} (profile: {profile_name})")

        except Exception as e:
            logger.error(f"设置配置失败 [{key}]: {e}")

    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

    def get_all_configs(self, profile_name: Optional[str] = None) -> Dict[str, Any]:
        """获取所有配置"""
        try:
            if not profile_name:
                profile_name = self._active_profile

            configs = {}

            # 首先加载默认配置
            if self._default_profile in self._profiles:
                default_profile = self._profiles[self._default_profile]
                for key, entry in default_profile.entries.items():
                    configs[key] = entry.value

            # 然后覆盖特定档案配置
            if profile_name != self._default_profile and profile_name in self._profiles:
                profile = self._profiles[profile_name]
                for key, entry in profile.entries.items():
                    configs[key] = entry.value

            return configs

        except Exception as e:
            logger.error(f"获取所有配置失败: {e}")
            return {}

    def reload_configs(self) -> bool:
        """重新加载配置"""
        try:
            # 清除缓存
            self._config_cache.clear()

            # 检查文件变化
            files_changed = []
            for file_path, old_mtime in self._file_watchers.items():
                try:
                    current_mtime = Path(file_path).stat().st_mtime
                    if current_mtime > old_mtime:
                        files_changed.append(file_path)
                        self._file_watchers[file_path] = current_mtime
                except:
                    # 文件可能被删除
                    pass

            # 重新加载变化的文件
            for file_path in files_changed:
                self.load_config_file(file_path)
                logger.info(f"配置文件已重新加载: {file_path}")

            return True

        except Exception as e:
            logger.error(f"重新加载配置失败: {e}")
            return False

    def validate_config(self, key: str, value: Any, validation_rules: Optional[Dict] = None) -> bool:
        """验证配置值"""
        try:
            if not validation_rules:
                return True

            # 基本验证规则
            if 'type' in validation_rules:
                expected_type = validation_rules['type']
                if not isinstance(value, expected_type):
                    logger.error(f"配置类型错误 [{key}]: 期望 {expected_type}, 实际 {type(value)}")
                    return False

            if 'min' in validation_rules and hasattr(value, '__lt__'):
                if value < validation_rules['min']:
                    logger.error(f"配置值过小 [{key}]: {value} < {validation_rules['min']}")
                    return False

            if 'max' in validation_rules and hasattr(value, '__gt__'):
                if value > validation_rules['max']:
                    logger.error(f"配置值过大 [{key}]: {value} > {validation_rules['max']}")
                    return False

            if 'choices' in validation_rules:
                if value not in validation_rules['choices']:
                    logger.error(f"配置值不在允许范围 [{key}]: {value} not in {validation_rules['choices']}")
                    return False

            return True

        except Exception as e:
            logger.error(f"配置验证失败 [{key}]: {e}")
            return False

    def export_config(self, profile_name: Optional[str] = None, format: ConfigFormat = ConfigFormat.JSON) -> Optional[str]:
        """导出配置"""
        try:
            configs = self.get_all_configs(profile_name)
            
            if format == ConfigFormat.JSON:
                return json.dumps(configs, indent=2, ensure_ascii=False)
            elif format == ConfigFormat.YAML:
                import yaml
                return yaml.dump(configs, default_flow_style=False, allow_unicode=True)
            elif format == ConfigFormat.TOML:
                import tomli_w
                return tomli_w.dumps(configs)
            else:
                return str(configs)

        except Exception as e:
            logger.error(f"导出配置失败: {e}")
            return None

    def get_config_info(self, key: str, profile_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取配置详细信息"""
        try:
            if not profile_name:
                profile_name = self._active_profile

            if profile_name in self._profiles:
                profile = self._profiles[profile_name]
                if key in profile.entries:
                    entry = profile.entries[key]
                    return {
                        "key": entry.key,
                        "value": entry.value,
                        "source": entry.source.value,
                        "file_path": entry.file_path,
                        "last_updated": entry.last_updated,
                        "profile": profile_name,
                    }

            return None

        except Exception as e:
            logger.error(f"获取配置信息失败 [{key}]: {e}")
            return None

    def list_profiles(self) -> List[str]:
        """列出所有配置档案"""
        return list(self._profiles.keys())

    def switch_profile(self, profile_name: str) -> bool:
        """切换配置档案"""
        try:
            if profile_name not in self._profiles:
                logger.warning(f"配置档案不存在: {profile_name}")
                return False

            self._active_profile = profile_name
            self._config_cache.clear()  # 清除缓存
            logger.info(f"配置档案已切换: {profile_name}")
            return True

        except Exception as e:
            logger.error(f"切换配置档案失败: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """获取配置管理器状态"""
        return {
            "initialized": self._initialized,
            "config_root": str(self.config_root),
            "active_profile": self._active_profile,
            "total_profiles": len(self._profiles),
            "total_configs": sum(len(profile.entries) for profile in self._profiles.values()),
            "cache_size": len(self._config_cache),
            "watched_files": len(self._file_watchers),
        }


# 全局实例
_unified_config_manager = None


def get_unified_config_manager(config_root: Optional[Path] = None) -> UnifiedConfigManager:
    """获取统一配置管理器实例"""
    global _unified_config_manager
    
    if _unified_config_manager is None:
        _unified_config_manager = UnifiedConfigManager(config_root)
        _unified_config_manager.initialize()
    
    return _unified_config_manager


def cleanup_unified_config_manager():
    """清理统一配置管理器"""
    global _unified_config_manager
    _unified_config_manager = None