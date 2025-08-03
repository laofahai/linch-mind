import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectorConfigManager:
    """连接器配置管理器 - 单一职责：配置管理和热重载"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.connectors_dir = self.project_root / "connectors"
        
        # 配置缓存
        self.system_config: dict = {}
        self.user_config: dict = {}
        self.connector_configs: Dict[str, dict] = {}
        
        # 配置文件路径
        self.system_config_path = self.connectors_dir / "system.config.json"
        self.user_config_path = self.connectors_dir / "user.config.json"
        
        logger.info("ConnectorConfigManager初始化")
        self._load_all_configs()
    
    def _load_all_configs(self):
        """加载所有配置"""
        self._load_system_config()
        self._load_user_config()
        logger.info("所有配置加载完成")
    
    def _load_system_config(self):
        """加载系统配置"""
        if self.system_config_path.exists():
            try:
                with open(self.system_config_path, "r", encoding="utf-8") as f:
                    self.system_config = json.load(f)
                logger.info(f"已加载系统配置: {self.system_config_path}")
            except Exception as e:
                logger.error(f"加载系统配置失败: {e}")
                self.system_config = {}
        else:
            # 创建默认系统配置
            self.system_config = self._get_default_system_config()
            self._save_system_config()
    
    def _load_user_config(self):
        """加载用户配置"""
        if self.user_config_path.exists():
            try:
                with open(self.user_config_path, "r", encoding="utf-8") as f:
                    self.user_config = json.load(f)
                logger.info(f"已加载用户配置: {self.user_config_path}")
            except Exception as e:
                logger.error(f"加载用户配置失败: {e}")
                self.user_config = {}
        else:
            # 创建默认用户配置
            self.user_config = self._get_default_user_config()
            self._save_user_config()
    
    def _get_default_system_config(self) -> dict:
        """获取默认系统配置"""
        return {
            "version": "1.0.0",
            "development_mode": self._detect_development_mode(),
            "connector_paths": [
                "official",
                "community",
                "third-party"
            ],
            "health_check": {
                "enabled": True,
                "interval": 10,
                "max_restart_attempts": 3,
                "restart_cooldown": 60,
                "restart_interval": 5
            },
            "logging": {
                "level": "INFO",
                "max_log_files": 10,
                "max_log_size_mb": 50
            },
            "updated_at": datetime.now().isoformat()
        }
    
    def _get_default_user_config(self) -> dict:
        """获取默认用户配置"""
        return {
            "version": "1.0.0",
            "auto_start_connectors": [],
            "connector_settings": {},
            "ui_preferences": {
                "show_debug_info": False,
                "auto_refresh_interval": 30
            },
            "updated_at": datetime.now().isoformat()
        }
    
    def _detect_development_mode(self) -> bool:
        """检测开发模式"""
        dev_indicators = [
            self.project_root / ".git",
            self.project_root / "pyproject.toml",
            self.project_root / "scripts/connector-dev.py",
        ]
        
        for indicator in dev_indicators:
            if indicator.exists():
                return True
        
        return os.getenv("LINCH_MIND_DEV_MODE", "false").lower() == "true"
    
    def get_system_config(self, key: str = None) -> Any:
        """获取系统配置"""
        if key is None:
            return self.system_config.copy()
        
        keys = key.split(".")
        value = self.system_config
        for k in keys:
            value = value.get(k)
            if value is None:
                return None
        return value
    
    def get_user_config(self, key: str = None) -> Any:
        """获取用户配置"""
        if key is None:
            return self.user_config.copy()
        
        keys = key.split(".")
        value = self.user_config
        for k in keys:
            value = value.get(k)
            if value is None:
                return None
        return value
    
    def set_system_config(self, key: str, value: Any, save: bool = True) -> bool:
        """设置系统配置"""
        try:
            keys = key.split(".")
            config = self.system_config
            
            # 导航到最后一层
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # 设置值
            config[keys[-1]] = value
            self.system_config["updated_at"] = datetime.now().isoformat()
            
            if save:
                self._save_system_config()
            
            logger.info(f"系统配置已更新: {key} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"设置系统配置失败: {e}")
            return False
    
    def set_user_config(self, key: str, value: Any, save: bool = True) -> bool:
        """设置用户配置"""
        try:
            keys = key.split(".")
            config = self.user_config
            
            # 导航到最后一层
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # 设置值
            config[keys[-1]] = value
            self.user_config["updated_at"] = datetime.now().isoformat()
            
            if save:
                self._save_user_config()
            
            logger.info(f"用户配置已更新: {key} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"设置用户配置失败: {e}")
            return False
    
    def _save_system_config(self) -> bool:
        """保存系统配置"""
        try:
            with open(self.system_config_path, "w", encoding="utf-8") as f:
                json.dump(self.system_config, f, indent=2, ensure_ascii=False)
            logger.debug(f"系统配置已保存: {self.system_config_path}")
            return True
        except Exception as e:
            logger.error(f"保存系统配置失败: {e}")
            return False
    
    def _save_user_config(self) -> bool:
        """保存用户配置"""
        try:
            with open(self.user_config_path, "w", encoding="utf-8") as f:
                json.dump(self.user_config, f, indent=2, ensure_ascii=False)
            logger.debug(f"用户配置已保存: {self.user_config_path}")
            return True
        except Exception as e:
            logger.error(f"保存用户配置失败: {e}")
            return False
    
    def get_connector_runtime_config(self, connector_id: str) -> dict:
        """获取连接器运行时配置"""
        # 合并系统配置和用户配置
        runtime_config = {}
        
        # 系统级配置
        system_connector_config = self.system_config.get("connector_settings", {}).get(connector_id, {})
        runtime_config.update(system_connector_config)
        
        # 用户级配置（覆盖系统配置）
        user_connector_config = self.user_config.get("connector_settings", {}).get(connector_id, {})
        runtime_config.update(user_connector_config)
        
        # 添加全局配置
        runtime_config["development_mode"] = self.get_system_config("development_mode")
        runtime_config["daemon_url"] = "http://localhost:58471"
        
        return runtime_config
    
    def set_connector_config(self, connector_id: str, config: dict, user_level: bool = True) -> bool:
        """设置连接器配置"""
        config_key = f"connector_settings.{connector_id}"
        
        if user_level:
            return self.set_user_config(config_key, config)
        else:
            return self.set_system_config(config_key, config)
    
    def get_auto_start_connectors(self) -> list:
        """获取自动启动的连接器列表"""
        return self.user_config.get("auto_start_connectors", [])
    
    def set_auto_start_connector(self, connector_id: str, auto_start: bool = True) -> bool:
        """设置连接器自动启动"""
        auto_start_list = self.get_auto_start_connectors()
        
        if auto_start:
            if connector_id not in auto_start_list:
                auto_start_list.append(connector_id)
        else:
            if connector_id in auto_start_list:
                auto_start_list.remove(connector_id)
        
        return self.set_user_config("auto_start_connectors", auto_start_list)
    
    def reload_configs(self) -> bool:
        """重新加载所有配置"""
        try:
            logger.info("重新加载配置")
            old_system_config = self.system_config.copy()
            old_user_config = self.user_config.copy()
            
            self._load_all_configs()
            
            # 检查是否有变化
            system_changed = old_system_config != self.system_config
            user_changed = old_user_config != self.user_config
            
            if system_changed:
                logger.info("系统配置已变更")
            if user_changed:
                logger.info("用户配置已变更")
            
            return True
        except Exception as e:
            logger.error(f"重新加载配置失败: {e}")
            return False
    
    def validate_config(self, config_type: str = "all") -> dict:
        """验证配置"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        if config_type in ["all", "system"]:
            # 验证系统配置
            if not isinstance(self.system_config.get("development_mode"), bool):
                validation_result["errors"].append("system.development_mode must be boolean")
            
            if not isinstance(self.system_config.get("connector_paths"), list):
                validation_result["errors"].append("system.connector_paths must be list")
        
        if config_type in ["all", "user"]:
            # 验证用户配置
            if not isinstance(self.user_config.get("auto_start_connectors"), list):
                validation_result["errors"].append("user.auto_start_connectors must be list")
        
        validation_result["valid"] = len(validation_result["errors"]) == 0
        return validation_result
    
    def export_config(self, include_user: bool = True) -> dict:
        """导出配置"""
        export_data = {
            "system_config": self.system_config,
            "export_time": datetime.now().isoformat()
        }
        
        if include_user:
            export_data["user_config"] = self.user_config
        
        return export_data
    
    def import_config(self, config_data: dict, overwrite: bool = False) -> bool:
        """导入配置"""
        try:
            if "system_config" in config_data:
                if overwrite or not self.system_config:
                    self.system_config = config_data["system_config"]
                    self._save_system_config()
            
            if "user_config" in config_data:
                if overwrite or not self.user_config:
                    self.user_config = config_data["user_config"]
                    self._save_user_config()
            
            logger.info("配置导入成功")
            return True
        except Exception as e:
            logger.error(f"配置导入失败: {e}")
            return False