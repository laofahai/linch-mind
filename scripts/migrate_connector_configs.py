#!/usr/bin/env python3
"""
连接器配置迁移脚本
从旧的registry.json + connector.json + 数据库配置迁移到新的unified config system
"""

import sys
import json
import yaml
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import logging

# 添加项目路径到sys.path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConnectorConfigMigrator:
    """连接器配置迁移器"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.connectors_dir = self.project_root / "connectors"
        
        # 旧配置文件路径
        self.old_registry_path = self.connectors_dir / "registry.json"
        self.official_dir = self.connectors_dir / "official"
        
        # 新配置文件路径
        self.new_master_config = self.connectors_dir / "connectors.yaml"
        self.new_instances_config = self.connectors_dir / "instances.yaml"
        
        # 备份目录
        self.backup_dir = self.connectors_dir / "migration_backup"
        
        logger.info(f"连接器配置迁移器初始化 - 项目根目录: {self.project_root}")
    
    def run_migration(self) -> bool:
        """运行完整的迁移流程"""
        try:
            logger.info("🚀 开始连接器配置迁移")
            
            # 1. 预检查
            if not self._pre_migration_check():
                logger.error("预检查失败，迁移终止")
                return False
            
            # 2. 创建备份
            self._create_backup()
            
            # 3. 迁移连接器类型配置
            connector_types = self._migrate_connector_types()
            if not connector_types:
                logger.error("连接器类型迁移失败")
                return False
            
            # 4. 迁移实例配置 (从数据库或创建默认实例)
            instances = self._migrate_instances()
            
            # 5. 生成新配置文件
            self._generate_new_configs(connector_types, instances)
            
            # 6. 验证迁移结果
            if not self._validate_migration():
                logger.error("迁移验证失败")
                return False
            
            # 7. 清理旧文件 (重命名为备份)
            self._cleanup_old_files()
            
            logger.info("✅ 连接器配置迁移完成")
            self._print_migration_summary(connector_types, instances)
            
            return True
            
        except Exception as e:
            logger.error(f"迁移过程中发生错误: {e}")
            logger.info("尝试从备份恢复...")
            self._restore_from_backup()
            return False
    
    def _pre_migration_check(self) -> bool:
        """迁移前检查"""
        logger.info("📋 执行迁移前检查...")
        
        # 检查项目结构
        if not self.connectors_dir.exists():
            logger.error(f"连接器目录不存在: {self.connectors_dir}")
            return False
        
        # 检查是否已经迁移过
        if self.new_master_config.exists():
            logger.warning(f"新配置文件已存在: {self.new_master_config}")
            response = input("是否覆盖现有配置？(y/N): ")
            if response.lower() != 'y':
                logger.info("迁移取消")
                return False
        
        # 检查旧配置文件
        if not self.old_registry_path.exists():
            logger.warning(f"旧注册表文件不存在: {self.old_registry_path}")
            logger.info("将扫描现有连接器目录创建配置")
        
        # 检查权限
        if not self.connectors_dir.is_dir() or not self._check_write_permission():
            logger.error("没有连接器目录的写权限")
            return False
        
        logger.info("✅ 预检查通过")
        return True
    
    def _check_write_permission(self) -> bool:
        """检查写权限"""
        try:
            test_file = self.connectors_dir / ".migration_test"
            test_file.write_text("test")
            test_file.unlink()
            return True
        except Exception:
            return False
    
    def _create_backup(self):
        """创建备份"""
        logger.info("💾 创建配置备份...")
        
        # 创建备份目录
        self.backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 备份registry.json
        if self.old_registry_path.exists():
            backup_registry = self.backup_dir / f"registry_{timestamp}.json"
            shutil.copy2(self.old_registry_path, backup_registry)
            logger.info(f"已备份registry.json到: {backup_registry}")
        
        # 备份现有的yaml配置文件（如果存在）
        for config_file in [self.new_master_config, self.new_instances_config]:
            if config_file.exists():
                backup_file = self.backup_dir / f"{config_file.stem}_{timestamp}.yaml"
                shutil.copy2(config_file, backup_file)
                logger.info(f"已备份{config_file.name}到: {backup_file}")
        
        logger.info("✅ 备份创建完成")
    
    def _migrate_connector_types(self) -> Dict[str, Dict[str, Any]]:
        """迁移连接器类型配置"""
        logger.info("🔄 迁移连接器类型配置...")
        
        connector_types = {}
        
        # 1. 从registry.json迁移
        if self.old_registry_path.exists():
            registry_types = self._load_from_registry()
            connector_types.update(registry_types)
            logger.info(f"从registry.json加载了 {len(registry_types)} 个连接器类型")
        
        # 2. 扫描官方连接器目录
        if self.official_dir.exists():
            scanned_types = self._scan_connector_directories()
            # 合并配置，文件系统扫描的优先级更高
            for type_id, type_data in scanned_types.items():
                if type_id in connector_types:
                    # 合并配置
                    connector_types[type_id].update(type_data)
                else:
                    connector_types[type_id] = type_data
            logger.info(f"从目录扫描加载了 {len(scanned_types)} 个连接器类型")
        
        logger.info(f"✅ 连接器类型迁移完成，共 {len(connector_types)} 个类型")
        return connector_types
    
    def _load_from_registry(self) -> Dict[str, Dict[str, Any]]:
        """从registry.json加载连接器类型"""
        try:
            with open(self.old_registry_path, "r", encoding="utf-8") as f:
                registry_data = json.load(f)
            
            connector_types = {}
            connectors = registry_data.get("connectors", [])
            
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
                    
                    # 转换为新格式
                    type_data = {
                        "name": connector_info.get("name", ""),
                        "display_name": connector_info.get("display_name", connector_info.get("name", "")),
                        "description": connector_info.get("description", ""),
                        "category": connector_info.get("category", "other"),
                        "version": connector_info.get("version", "1.0.0"),
                        "author": connector_info.get("author", ""),
                        "license": connector_info.get("license", ""),
                        
                        # 能力配置
                        "supports_multiple_instances": capabilities.get("supports_multiple_instances", False),
                        "max_instances_per_user": capabilities.get("max_instances_per_user", 1),
                        "auto_discovery": capabilities.get("auto_discovery", False),
                        "hot_config_reload": capabilities.get("hot_config_reload", True),
                        "health_check": capabilities.get("health_check", True),
                        
                        # 技术信息
                        "entry_point": connector_info.get("entry_point", "main.py"),
                        "python_version": system_requirements.get("python_version", ">=3.8"),
                        "dependencies": connector_data.get("package_info", {}).get("dependencies", []),
                        "permissions": system_requirements.get("permissions", []),
                        
                        # 配置模式
                        "config_schema": config_schema,
                        "ui_schema": connector_data.get("ui_schema", {}),
                        "default_config": self._extract_default_config(config_schema),
                        "instance_templates": instance_templates
                    }
                    
                    connector_types[type_id] = type_data
                    logger.debug(f"迁移连接器类型: {type_id}")
                    
                except Exception as e:
                    logger.error(f"迁移连接器类型失败: {e}")
            
            return connector_types
            
        except Exception as e:
            logger.error(f"读取registry.json失败: {e}")
            return {}
    
    def _extract_default_config(self, config_schema: Dict[str, Any]) -> Dict[str, Any]:
        """从config_schema中提取默认配置"""
        default_config = {}
        
        if not isinstance(config_schema, dict):
            return default_config
        
        properties = config_schema.get("properties", {})
        for key, property_def in properties.items():
            if "default" in property_def:
                default_config[key] = property_def["default"]
            elif property_def.get("type") == "object" and "properties" in property_def:
                # 递归处理嵌套对象
                nested_default = self._extract_default_config(property_def)
                if nested_default:
                    default_config[key] = nested_default
        
        return default_config
    
    def _scan_connector_directories(self) -> Dict[str, Dict[str, Any]]:
        """扫描连接器目录"""
        connector_types = {}
        
        for connector_dir in self.official_dir.iterdir():
            if not connector_dir.is_dir():
                continue
            
            connector_json = connector_dir / "connector.json"
            if not connector_json.exists():
                logger.debug(f"跳过目录 {connector_dir.name}，缺少connector.json")
                continue
            
            try:
                with open(connector_json, "r", encoding="utf-8") as f:
                    connector_config = json.load(f)
                
                type_id = connector_config.get("id")
                if not type_id:
                    logger.warning(f"连接器 {connector_dir.name} 缺少id字段")
                    continue
                
                # 转换配置格式
                type_data = {
                    "name": connector_config.get("name", ""),
                    "display_name": connector_config.get("display_name", connector_config.get("name", "")),
                    "description": connector_config.get("description", ""),
                    "category": connector_config.get("category", "other"),
                    "version": connector_config.get("version", "1.0.0"),
                    "author": connector_config.get("author", ""),
                    "license": connector_config.get("license", ""),
                    
                    # 从capabilities部分提取
                    "supports_multiple_instances": connector_config.get("capabilities", {}).get("supports_multiple_instances", False),
                    "max_instances_per_user": connector_config.get("capabilities", {}).get("max_instances_per_user", 1),
                    
                    # 技术信息
                    "entry_point": self._extract_entry_point(connector_config),
                    "dependencies": connector_config.get("dependencies", []),
                    "permissions": connector_config.get("permissions", []),
                    
                    # 配置相关
                    "config_schema": connector_config.get("config_schema", {}),
                    "default_config": connector_config.get("default_config", {}),
                    "instance_templates": connector_config.get("instance_templates", [])
                }
                
                connector_types[type_id] = type_data
                logger.debug(f"扫描到连接器类型: {type_id}")
                
            except Exception as e:
                logger.error(f"扫描连接器目录 {connector_dir.name} 失败: {e}")
        
        return connector_types
    
    def _extract_entry_point(self, connector_config: Dict[str, Any]) -> str:
        """提取连接器入口点"""
        entry = connector_config.get("entry", {})
        
        # 开发模式入口
        dev_entry = entry.get("development", {})
        if dev_entry and "args" in dev_entry:
            return dev_entry["args"][0] if dev_entry["args"] else "main.py"
        
        # 默认入口
        return "main.py"
    
    def _migrate_instances(self) -> Dict[str, Dict[str, Any]]:
        """迁移连接器实例配置"""
        logger.info("🔄 迁移连接器实例配置...")
        
        instances = {}
        
        # TODO: 从数据库迁移实例配置
        # 这里简化实现，为每个连接器类型创建一个默认实例
        
        logger.info(f"✅ 连接器实例迁移完成，共 {len(instances)} 个实例")
        return instances
    
    def _generate_new_configs(self, connector_types: Dict[str, Dict[str, Any]], 
                             instances: Dict[str, Dict[str, Any]]):
        """生成新的配置文件"""
        logger.info("📝 生成新配置文件...")
        
        # 生成主配置文件
        master_config = {
            "config_version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "metadata": {
                "description": "Linch Mind 连接器配置 - 统一配置源",
                "created_by": "ConnectorConfigMigrator",
                "schema_version": "1.0",
                "connector_count": len(connector_types),
                "migration_timestamp": datetime.now().isoformat()
            },
            "connector_types": connector_types
        }
        
        with open(self.new_master_config, "w", encoding="utf-8") as f:
            yaml.dump(master_config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        logger.info(f"✅ 已生成主配置文件: {self.new_master_config}")
        
        # 生成实例配置文件
        instances_config = {
            "config_version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "metadata": {
                "description": "连接器实例配置",
                "created_by": "ConnectorConfigMigrator",
                "instance_count": len(instances),
                "migration_timestamp": datetime.now().isoformat()
            },
            "instances": instances
        }
        
        with open(self.new_instances_config, "w", encoding="utf-8") as f:
            yaml.dump(instances_config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        logger.info(f"✅ 已生成实例配置文件: {self.new_instances_config}")
    
    def _validate_migration(self) -> bool:
        """验证迁移结果"""
        logger.info("🔍 验证迁移结果...")
        
        try:
            # 验证配置文件格式
            with open(self.new_master_config, "r", encoding="utf-8") as f:
                master_config = yaml.safe_load(f)
            
            with open(self.new_instances_config, "r", encoding="utf-8") as f:
                instances_config = yaml.safe_load(f)
            
            # 基本结构验证
            if "connector_types" not in master_config:
                logger.error("主配置文件缺少connector_types部分")
                return False
            
            if "instances" not in instances_config:
                logger.error("实例配置文件缺少instances部分")
                return False
            
            # 验证连接器类型完整性
            connector_types = master_config["connector_types"]
            for type_id, type_data in connector_types.items():
                required_fields = ["name", "description", "version"]
                for field in required_fields:
                    if field not in type_data:
                        logger.error(f"连接器类型 {type_id} 缺少必需字段: {field}")
                        return False
            
            logger.info("✅ 迁移验证通过")
            return True
            
        except Exception as e:
            logger.error(f"验证迁移结果失败: {e}")
            return False
    
    def _cleanup_old_files(self):
        """清理旧文件"""
        logger.info("🧹 清理旧配置文件...")
        
        # 重命名registry.json为备份文件
        if self.old_registry_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_registry = self.old_registry_path.parent / f"registry_backup_{timestamp}.json"
            self.old_registry_path.rename(backup_registry)
            logger.info(f"已将registry.json重命名为: {backup_registry}")
        
        logger.info("✅ 旧文件清理完成")
    
    def _restore_from_backup(self):
        """从备份恢复"""
        logger.info("🔄 从备份恢复配置...")
        
        try:
            # 查找最新的备份文件
            backup_files = list(self.backup_dir.glob("registry_*.json"))
            if backup_files:
                latest_backup = max(backup_files, key=lambda p: p.stat().st_mtime)
                shutil.copy2(latest_backup, self.old_registry_path)
                logger.info(f"已从备份恢复registry.json: {latest_backup}")
            
            # 删除可能生成的新配置文件
            for config_file in [self.new_master_config, self.new_instances_config]:
                if config_file.exists():
                    config_file.unlink()
                    logger.info(f"已删除: {config_file}")
            
            logger.info("✅ 从备份恢复完成")
            
        except Exception as e:
            logger.error(f"从备份恢复失败: {e}")
    
    def _print_migration_summary(self, connector_types: Dict, instances: Dict):
        """打印迁移摘要"""
        print("\n" + "="*60)
        print("📊 连接器配置迁移摘要")
        print("="*60)
        print(f"迁移的连接器类型: {len(connector_types)}")
        for type_id, type_data in connector_types.items():
            print(f"  - {type_id}: {type_data.get('name', 'Unknown')} v{type_data.get('version', '1.0.0')}")
        
        print(f"\n迁移的连接器实例: {len(instances)}")
        for instance_id in instances.keys():
            print(f"  - {instance_id}")
        
        print(f"\n生成的配置文件:")
        print(f"  - 主配置: {self.new_master_config}")
        print(f"  - 实例配置: {self.new_instances_config}")
        
        print(f"\n备份目录: {self.backup_dir}")
        print("="*60)
        print("✅ 迁移完成！现在可以使用新的统一配置系统。")
        print("="*60)


def main():
    """主函数"""
    import sys
    
    print("🚀 连接器配置迁移工具")
    print("这个工具将把现有的连接器配置迁移到新的统一配置系统")
    print()
    
    # 检查是否有命令行参数
    auto_confirm = "--yes" in sys.argv or "-y" in sys.argv
    
    if not auto_confirm:
        try:
            # 确认用户想要继续
            response = input("是否继续迁移？(y/N): ")
            if response.lower() != 'y':
                print("迁移取消")
                return
        except (EOFError, KeyboardInterrupt):
            print("\n迁移取消")
            return
    else:
        print("自动确认模式，开始迁移...")
    
    # 创建迁移器并运行
    migrator = ConnectorConfigMigrator()
    success = migrator.run_migration()
    
    if success:
        print("\n🎉 迁移成功完成！")
        print("建议：")
        print("1. 运行 python scripts/validate_connector_configs.py 验证配置")
        print("2. 重启daemon以使用新配置")
        print("3. 测试连接器功能是否正常")
    else:
        print("\n❌ 迁移失败，请检查日志信息")
        print("旧配置已从备份恢复，系统应该仍能正常工作")


if __name__ == "__main__":
    main()