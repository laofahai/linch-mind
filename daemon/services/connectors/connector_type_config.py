#!/usr/bin/env python3
"""
连接器类型与实例配置管理
专门负责连接器的类型定义和实例管理，区别于daemon全局配置
重命名为 connector_type_config.py 以避免命名冲突
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConnectorTypeInfo:
    """连接器类型信息"""
    type_id: str
    name: str
    display_name: str
    description: str
    category: str
    version: str
    author: str
    license: str
    
    # 能力声明
    supports_multiple_instances: bool = False
    max_instances_per_user: int = 1
    auto_discovery: bool = False
    hot_config_reload: bool = True
    health_check: bool = True
    
    # 技术信息
    entry_point: str = "main.py"
    python_version: str = ">=3.8"
    dependencies: List[str] = None
    permissions: List[str] = None
    
    # 配置模式
    config_schema: Dict[str, Any] = None
    ui_schema: Dict[str, Any] = None
    default_config: Dict[str, Any] = None
    instance_templates: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.permissions is None:
            self.permissions = []
        if self.config_schema is None:
            self.config_schema = {}
        if self.ui_schema is None:
            self.ui_schema = {}
        if self.default_config is None:
            self.default_config = {}
        if self.instance_templates is None:
            self.instance_templates = []


@dataclass
class ConnectorInstanceInfo:
    """连接器实例信息"""
    instance_id: str
    type_id: str
    display_name: str
    config: Dict[str, Any]
    
    # 状态信息
    state: str = "configured"
    auto_start: bool = True
    enabled: bool = False
    
    # 运行时信息
    process_id: Optional[int] = None
    last_heartbeat: Optional[datetime] = None
    error_message: Optional[str] = None
    data_count: int = 0
    
    # 元数据
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


class ConnectorTypeConfigManager:
    """连接器类型与实例配置管理器
    
    专门负责:
    1. 连接器类型定义和注册
    2. 连接器实例配置管理
    3. 替代registry.json的功能
    
    不负责daemon全局配置（由daemon/config/unified_settings.py处理）
    """
    
    def __init__(self, config_root: Path = None):
        self.config_root = config_root or Path(__file__).parent.parent.parent.parent
        self.connectors_dir = self.config_root / "connectors"
        
        # 统一配置文件路径
        self.master_config_path = self.connectors_dir / "connectors.yaml"
        self.instances_config_path = self.connectors_dir / "instances.yaml"
        
        # 内存中的配置缓存
        self._connector_types: Dict[str, ConnectorTypeInfo] = {}
        self._connector_instances: Dict[str, ConnectorInstanceInfo] = {}
        
        # 配置版本管理
        self._config_version = 0
        self._last_reload = None
        
        # 初始化
        self._ensure_config_structure()
        self.reload_all_configs()
    
    def _ensure_config_structure(self):
        """确保配置文件结构存在"""
        self.connectors_dir.mkdir(exist_ok=True)
        
        # 创建主配置文件（如果不存在）
        if not self.master_config_path.exists():
            self._create_initial_master_config()
        
        # 创建实例配置文件（如果不存在）
        if not self.instances_config_path.exists():
            self._create_initial_instances_config()
    
    def _create_initial_master_config(self):
        """创建初始的主配置文件"""
        initial_config = {
            "config_version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "metadata": {
                "description": "Linch Mind 连接器配置 - 统一配置源",
                "created_by": "CoreConfigManager",
                "schema_version": "1.0"
            },
            "connector_types": {}
        }
        
        with open(self.master_config_path, "w", encoding="utf-8") as f:
            yaml.dump(initial_config, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"创建初始主配置文件: {self.master_config_path}")
    
    def _create_initial_instances_config(self):
        """创建初始的实例配置文件"""
        initial_config = {
            "config_version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "metadata": {
                "description": "连接器实例配置",
                "created_by": "CoreConfigManager"
            },
            "instances": {}
        }
        
        with open(self.instances_config_path, "w", encoding="utf-8") as f:
            yaml.dump(initial_config, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"创建初始实例配置文件: {self.instances_config_path}")
    
    def reload_all_configs(self):
        """重新加载所有配置"""
        logger.info("重新加载连接器配置")
        
        try:
            # 加载连接器类型配置
            self._load_connector_types()
            
            # 从现有registry.json迁移（如果存在）
            self._migrate_from_registry_json()
            
            # 加载实例配置
            self._load_instances()
            
            # 从数据库迁移实例配置
            self._migrate_instances_from_database()
            
            self._config_version += 1
            self._last_reload = datetime.now()
            
            logger.info(f"配置重新加载完成 - 版本: {self._config_version}")
            logger.info(f"已加载连接器类型: {len(self._connector_types)}")
            logger.info(f"已加载连接器实例: {len(self._connector_instances)}")
            
        except Exception as e:
            logger.error(f"重新加载配置失败: {e}")
            raise
    
    def _load_connector_types(self):
        """加载连接器类型配置"""
        try:
            with open(self.master_config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            
            connector_types = config.get("connector_types", {})
            
            for type_id, type_data in connector_types.items():
                try:
                    connector_type = ConnectorTypeInfo(
                        type_id=type_id,
                        **type_data
                    )
                    self._connector_types[type_id] = connector_type
                    logger.debug(f"加载连接器类型: {type_id}")
                except Exception as e:
                    logger.error(f"加载连接器类型 {type_id} 失败: {e}")
        
        except FileNotFoundError:
            logger.warning(f"主配置文件不存在: {self.master_config_path}")
        except Exception as e:
            logger.error(f"加载主配置失败: {e}")
    
    def _migrate_from_registry_json(self):
        """从旧的registry.json迁移配置"""
        old_registry = self.connectors_dir / "registry.json"
        if not old_registry.exists():
            return
        
        logger.info("从registry.json迁移配置...")
        
        try:
            with open(old_registry, "r", encoding="utf-8") as f:
                registry_data = json.load(f)
            
            connectors = registry_data.get("connectors", [])
            migrated_count = 0
            
            for connector_data in connectors:
                try:
                    connector_info = connector_data.get("connector_info", {})
                    capabilities = connector_data.get("capabilities", {})
                    system_requirements = connector_data.get("system_requirements", {})
                    config_schema = connector_data.get("config_schema", {})
                    instance_templates = connector_data.get("instance_templates", [])
                    
                    type_id = connector_info.get("type_id")
                    if not type_id:
                        continue
                    
                    # 如果已存在，跳过
                    if type_id in self._connector_types:
                        continue
                    
                    connector_type = ConnectorTypeInfo(
                        type_id=type_id,
                        name=connector_info.get("name", ""),
                        display_name=connector_info.get("display_name", connector_info.get("name", "")),
                        description=connector_info.get("description", ""),
                        category=connector_info.get("category", "other"),
                        version=connector_info.get("version", "1.0.0"),
                        author=connector_info.get("author", ""),
                        license=connector_info.get("license", ""),
                        
                        supports_multiple_instances=capabilities.get("supports_multiple_instances", False),
                        max_instances_per_user=capabilities.get("max_instances_per_user", 1),
                        auto_discovery=capabilities.get("auto_discovery", False),
                        hot_config_reload=capabilities.get("hot_config_reload", True),
                        health_check=capabilities.get("health_check", True),
                        
                        entry_point=connector_info.get("entry_point", "main.py"),
                        python_version=system_requirements.get("python_version", ">=3.8"),
                        dependencies=connector_data.get("package_info", {}).get("dependencies", []),
                        permissions=system_requirements.get("permissions", []),
                        
                        config_schema=config_schema,
                        ui_schema=connector_data.get("ui_schema", {}),
                        default_config=config_schema.get("properties", {}),
                        instance_templates=instance_templates
                    )
                    
                    self._connector_types[type_id] = connector_type
                    migrated_count += 1
                    logger.debug(f"迁移连接器类型: {type_id}")
                    
                except Exception as e:
                    logger.error(f"迁移连接器数据失败: {e}")
            
            # 保存迁移后的配置
            if migrated_count > 0:
                self.save_connector_types()
                logger.info(f"成功迁移 {migrated_count} 个连接器类型")
                
                # 备份旧文件
                backup_path = old_registry.parent / f"registry_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                old_registry.rename(backup_path)
                logger.info(f"已备份旧registry.json到: {backup_path}")
        
        except Exception as e:
            logger.error(f"迁移registry.json失败: {e}")
    
    def _load_instances(self):
        """加载连接器实例配置"""
        try:
            with open(self.instances_config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            
            instances = config.get("instances", {})
            
            for instance_id, instance_data in instances.items():
                try:
                    instance = ConnectorInstanceInfo(
                        instance_id=instance_id,
                        **instance_data
                    )
                    self._connector_instances[instance_id] = instance
                    logger.debug(f"加载连接器实例: {instance_id}")
                except Exception as e:
                    logger.error(f"加载连接器实例 {instance_id} 失败: {e}")
        
        except FileNotFoundError:
            logger.warning(f"实例配置文件不存在: {self.instances_config_path}")
        except Exception as e:
            logger.error(f"加载实例配置失败: {e}")
    
    def _migrate_instances_from_database(self):
        """从数据库迁移实例配置"""
        # TODO: 实现从数据库迁移实例配置的逻辑
        # 这需要与现有的数据库服务集成
        pass
    
    def save_connector_types(self):
        """保存连接器类型配置"""
        try:
            config = {
                "config_version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "metadata": {
                    "description": "Linch Mind 连接器配置 - 统一配置源",
                    "created_by": "CoreConfigManager",
                    "schema_version": "1.0",
                    "connector_count": len(self._connector_types)
                },
                "connector_types": {}
            }
            
            for type_id, connector_type in self._connector_types.items():
                # 转换为字典，排除None值
                type_data = asdict(connector_type)
                del type_data["type_id"]  # type_id作为key，不需要在value中重复
                
                # 清理None值
                type_data = {k: v for k, v in type_data.items() if v is not None}
                
                # 转换datetime为ISO字符串
                for key, value in type_data.items():
                    if isinstance(value, datetime):
                        type_data[key] = value.isoformat()
                
                config["connector_types"][type_id] = type_data
            
            with open(self.master_config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"已保存连接器类型配置: {len(self._connector_types)} 个类型")
            
        except Exception as e:
            logger.error(f"保存连接器类型配置失败: {e}")
            raise
    
    def save_instances(self):
        """保存连接器实例配置"""
        try:
            config = {
                "config_version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "metadata": {
                    "description": "连接器实例配置",
                    "created_by": "CoreConfigManager",
                    "instance_count": len(self._connector_instances)
                },
                "instances": {}
            }
            
            for instance_id, instance in self._connector_instances.items():
                # 转换为字典，排除None值
                instance_data = asdict(instance)
                del instance_data["instance_id"]  # instance_id作为key
                
                # 清理None值
                instance_data = {k: v for k, v in instance_data.items() if v is not None}
                
                # 转换datetime为ISO字符串
                for key, value in instance_data.items():
                    if isinstance(value, datetime):
                        instance_data[key] = value.isoformat()
                
                config["instances"][instance_id] = instance_data
            
            with open(self.instances_config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"已保存连接器实例配置: {len(self._connector_instances)} 个实例")
            
        except Exception as e:
            logger.error(f"保存连接器实例配置失败: {e}")
            raise
    
    # === 连接器类型管理 ===
    
    def register_connector_type(self, connector_type: ConnectorTypeInfo) -> bool:
        """注册连接器类型"""
        try:
            self._connector_types[connector_type.type_id] = connector_type
            self.save_connector_types()
            logger.info(f"注册连接器类型: {connector_type.type_id}")
            return True
        except Exception as e:
            logger.error(f"注册连接器类型失败: {e}")
            return False
    
    def get_connector_type(self, type_id: str) -> Optional[ConnectorTypeInfo]:
        """获取连接器类型信息"""
        return self._connector_types.get(type_id)
    
    def list_connector_types(self, category: str = None) -> List[ConnectorTypeInfo]:
        """列出连接器类型"""
        types = list(self._connector_types.values())
        if category:
            types = [t for t in types if t.category == category]
        return types
    
    def unregister_connector_type(self, type_id: str) -> bool:
        """注销连接器类型"""
        try:
            if type_id in self._connector_types:
                del self._connector_types[type_id]
                self.save_connector_types()
                logger.info(f"注销连接器类型: {type_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"注销连接器类型失败: {e}")
            return False
    
    # === 连接器实例管理 ===
    
    def create_instance(self, instance: ConnectorInstanceInfo) -> bool:
        """创建连接器实例"""
        try:
            self._connector_instances[instance.instance_id] = instance
            self.save_instances()
            logger.info(f"创建连接器实例: {instance.instance_id}")
            return True
        except Exception as e:
            logger.error(f"创建连接器实例失败: {e}")
            return False
    
    def get_instance(self, instance_id: str) -> Optional[ConnectorInstanceInfo]:
        """获取连接器实例信息"""
        return self._connector_instances.get(instance_id)
    
    def list_instances(self, type_id: str = None, state: str = None) -> List[ConnectorInstanceInfo]:
        """列出连接器实例"""
        instances = list(self._connector_instances.values())
        
        if type_id:
            instances = [i for i in instances if i.type_id == type_id]
        
        if state:
            instances = [i for i in instances if i.state == state]
        
        return instances
    
    def update_instance(self, instance_id: str, **updates) -> bool:
        """更新连接器实例"""
        try:
            instance = self._connector_instances.get(instance_id)
            if not instance:
                return False
            
            for key, value in updates.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            instance.updated_at = datetime.now()
            self.save_instances()
            logger.debug(f"更新连接器实例: {instance_id}")
            return True
        except Exception as e:
            logger.error(f"更新连接器实例失败: {e}")
            return False
    
    def delete_instance(self, instance_id: str) -> bool:
        """删除连接器实例"""
        try:
            if instance_id in self._connector_instances:
                del self._connector_instances[instance_id]
                self.save_instances()
                logger.info(f"删除连接器实例: {instance_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"删除连接器实例失败: {e}")
            return False
    
    # === 配置管理工具 ===
    
    def get_config_version(self) -> int:
        """获取配置版本号"""
        return self._config_version
    
    def get_last_reload_time(self) -> Optional[datetime]:
        """获取最后重载时间"""
        return self._last_reload
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        return {
            "config_version": self._config_version,
            "last_reload": self._last_reload,
            "connector_types_count": len(self._connector_types),
            "instances_count": len(self._connector_instances),
            "config_files": {
                "master_config": str(self.master_config_path),
                "instances_config": str(self.instances_config_path)
            }
        }
    
    def validate_all_configs(self) -> Dict[str, List[str]]:
        """验证所有配置的完整性"""
        errors = {
            "connector_types": [],
            "instances": []
        }
        
        # 验证连接器类型
        for type_id, connector_type in self._connector_types.items():
            try:
                # 验证必需字段
                required_fields = ["name", "description", "category", "version"]
                for field in required_fields:
                    if not getattr(connector_type, field):
                        errors["connector_types"].append(f"{type_id}: 缺少必需字段 {field}")
                
                # 验证配置模式
                if connector_type.config_schema:
                    # TODO: 使用jsonschema验证
                    pass
                
            except Exception as e:
                errors["connector_types"].append(f"{type_id}: 验证失败 - {e}")
        
        # 验证连接器实例
        for instance_id, instance in self._connector_instances.items():
            try:
                # 验证类型存在
                if instance.type_id not in self._connector_types:
                    errors["instances"].append(f"{instance_id}: 引用的连接器类型不存在 - {instance.type_id}")
                
                # 验证配置符合模式
                connector_type = self._connector_types.get(instance.type_id)
                if connector_type and connector_type.config_schema:
                    # TODO: 验证实例配置符合类型配置模式
                    pass
                
            except Exception as e:
                errors["instances"].append(f"{instance_id}: 验证失败 - {e}")
        
        return errors


# 全局单例实例
_connector_type_config_manager = None

def get_connector_type_config_manager() -> ConnectorTypeConfigManager:
    """获取连接器类型配置管理器实例"""
    global _connector_type_config_manager
    if _connector_type_config_manager is None:
        _connector_type_config_manager = ConnectorTypeConfigManager()
    return _connector_type_config_manager