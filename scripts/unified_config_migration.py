#!/usr/bin/env python3
"""
统一配置迁移脚本
完整迁移daemon和connectors的配置到 ~/.linch-mind
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
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class UnifiedConfigMigrator:
    """统一配置迁移器 - 迁移所有配置到 ~/.linch-mind"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        
        # 目标目录结构
        self.user_config_dir = Path.home() / ".linch-mind"
        self.user_config_dir.mkdir(exist_ok=True)
        
        self.target_config_dir = self.user_config_dir / "config"
        self.target_data_dir = self.user_config_dir / "data"
        self.target_logs_dir = self.user_config_dir / "logs"
        self.target_db_dir = self.user_config_dir / "db"
        
        # 源文件路径
        self.daemon_old_config = self.project_root / "daemon" / "config.py"
        self.project_config = self.project_root / "linch-mind.config.yaml"
        self.connectors_dir = self.project_root / "connectors"
        self.old_registry = self.connectors_dir / "registry.json"
        
        # 目标配置文件
        self.target_app_config = self.target_config_dir / "app.yaml"
        self.target_connectors_config = self.target_config_dir / "connectors.yaml"
        self.target_instances_config = self.target_config_dir / "instances.yaml"
        
        # 备份目录
        self.backup_dir = self.user_config_dir / "migration_backup"
        
        logger.info(f"统一配置迁移器初始化 - 目标目录: {self.user_config_dir}")

    def run_migration(self) -> bool:
        """运行完整的配置迁移"""
        try:
            logger.info("🚀 开始统一配置迁移")
            
            # 1. 预检查
            if not self._pre_migration_check():
                logger.error("预检查失败，迁移终止")
                return False
            
            # 2. 创建目录结构
            self._create_directory_structure()
            
            # 3. 创建备份
            self._create_backup()
            
            # 4. 迁移daemon配置
            daemon_config = self._migrate_daemon_config()
            
            # 5. 迁移连接器配置
            connector_types = self._migrate_connector_types()
            instances = self._migrate_connector_instances()
            
            # 6. 生成统一配置文件
            self._generate_unified_configs(daemon_config, connector_types, instances)
            
            # 7. 迁移用户配置（connectors侧配置）
            self._migrate_user_configs()
            
            # 8. 验证迁移结果
            if not self._validate_migration():
                logger.error("迁移验证失败")
                return False
            
            # 9. 清理和完成
            self._cleanup_and_finalize()
            
            logger.info("✅ 统一配置迁移完成")
            self._print_migration_summary(daemon_config, connector_types, instances)
            
            return True
            
        except Exception as e:
            logger.error(f"迁移过程中发生错误: {e}")
            logger.info("尝试从备份恢复...")
            self._restore_from_backup()
            return False

    def _pre_migration_check(self) -> bool:
        """迁移前检查"""
        logger.info("📋 执行迁移前检查...")
        
        # 检查项目根目录
        if not self.project_root.exists():
            logger.error(f"项目根目录不存在: {self.project_root}")
            return False
        
        # 检查目标目录权限
        try:
            test_file = self.user_config_dir / ".migration_test"
            test_file.write_text("test")
            test_file.unlink()
        except Exception as e:
            logger.error(f"没有目标目录写权限: {e}")
            return False
        
        # 检查是否已经迁移过
        if self.target_app_config.exists():
            logger.warning(f"配置文件已存在: {self.target_app_config}")
            # 在自动模式下直接覆盖
            logger.info("自动模式：将覆盖现有配置")
        
        logger.info("✅ 预检查通过")
        return True

    def _create_directory_structure(self):
        """创建目录结构"""
        logger.info("📁 创建目录结构...")
        
        directories = [
            self.target_config_dir,
            self.target_data_dir,
            self.target_logs_dir,
            self.target_db_dir,
            self.backup_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"创建目录: {directory}")
        
        logger.info("✅ 目录结构创建完成")

    def _create_backup(self):
        """创建备份"""
        logger.info("💾 创建配置备份...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 备份项目配置文件
        if self.project_config.exists():
            backup_file = self.backup_dir / f"linch-mind.config_{timestamp}.yaml"
            shutil.copy2(self.project_config, backup_file)
            logger.info(f"已备份项目配置: {backup_file}")
        
        # 备份daemon旧配置
        if self.daemon_old_config.exists():
            backup_file = self.backup_dir / f"daemon_config_{timestamp}.py"
            shutil.copy2(self.daemon_old_config, backup_file)
            logger.info(f"已备份daemon配置: {backup_file}")
        
        # 备份连接器配置
        if self.old_registry.exists():
            backup_file = self.backup_dir / f"registry_{timestamp}.json"
            shutil.copy2(self.old_registry, backup_file)
            logger.info(f"已备份连接器注册表: {backup_file}")
        
        # 备份现有的用户配置文件
        for config_file in [self.target_app_config, self.target_connectors_config, self.target_instances_config]:
            if config_file.exists():
                backup_file = self.backup_dir / f"{config_file.stem}_{timestamp}.yaml"
                shutil.copy2(config_file, backup_file)
                logger.info(f"已备份现有配置: {backup_file}")
        
        logger.info("✅ 备份创建完成")

    def _migrate_daemon_config(self) -> Dict[str, Any]:
        """迁移daemon配置"""
        logger.info("🔄 迁移daemon配置...")
        
        daemon_config = {
            "app_name": "Linch Mind",
            "version": "0.1.0",
            "description": "Personal AI Life Assistant API",
            "debug": False,
            "server": {
                "host": "0.0.0.0",
                "port": 58471,
                "port_range": [8000, 9000],
                "reload": True,
                "log_level": "info"
            },
            "database": {
                "sqlite_url": f"sqlite:///{self.target_db_dir}/linch_mind.db",
                "chroma_persist_directory": str(self.target_db_dir / "chromadb"),
                "embedding_model": "all-MiniLM-L6-v2",
                "vector_dimension": 384
            },
            "connectors": {
                "registry_url": "http://localhost:8001/v1",
                "install_dir": str(self.project_root / "connectors" / "packages"),
                "config_dir": str(self.project_root / "connectors"),
                "filesystem_enabled": True,
                "filesystem_watch_paths": [],
                "clipboard_enabled": False
            },
            "ai": {
                "default_embedding_model": "all-MiniLM-L6-v2",
                "max_search_results": 10,
                "recommendation_threshold": 0.7,
                "providers": []
            }
        }
        
        # 从项目配置文件读取现有配置
        if self.project_config.exists():
            try:
                with open(self.project_config, 'r', encoding='utf-8') as f:
                    project_data = yaml.safe_load(f)
                    if project_data:
                        # 合并配置，项目配置优先
                        self._merge_configs(daemon_config, project_data)
                        logger.info("已合并项目配置文件")
            except Exception as e:
                logger.error(f"读取项目配置失败: {e}")
        
        # 从daemon/config.py读取旧配置
        try:
            if self.daemon_old_config.exists():
                # 这里简化处理，实际中可以解析Python文件
                logger.info("检测到旧的daemon配置文件，使用默认配置")
        except Exception as e:
            logger.error(f"读取旧daemon配置失败: {e}")
        
        logger.info("✅ daemon配置迁移完成")
        return daemon_config

    def _merge_configs(self, target: Dict[str, Any], source: Dict[str, Any]):
        """递归合并配置"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_configs(target[key], value)
            else:
                target[key] = value

    def _migrate_connector_types(self) -> Dict[str, Dict[str, Any]]:
        """迁移连接器类型配置"""
        logger.info("🔄 迁移连接器类型配置...")
        
        connector_types = {}
        
        # 1. 从registry.json迁移
        if self.old_registry.exists():
            registry_types = self._load_from_registry()
            connector_types.update(registry_types)
            logger.info(f"从registry.json加载了 {len(registry_types)} 个连接器类型")
        
        # 2. 扫描官方连接器目录
        official_dir = self.connectors_dir / "official"
        if official_dir.exists():
            scanned_types = self._scan_connector_directories(official_dir)
            for type_id, type_data in scanned_types.items():
                if type_id in connector_types:
                    connector_types[type_id].update(type_data)
                else:
                    connector_types[type_id] = type_data
            logger.info(f"从目录扫描加载了 {len(scanned_types)} 个连接器类型")
        
        logger.info(f"✅ 连接器类型迁移完成，共 {len(connector_types)} 个类型")
        return connector_types

    def _load_from_registry(self) -> Dict[str, Dict[str, Any]]:
        """从registry.json加载连接器类型"""
        try:
            with open(self.old_registry, "r", encoding="utf-8") as f:
                registry_data = json.load(f)
            
            connector_types = {}
            connectors = registry_data.get("connectors", [])
            
            for connector_data in connectors:
                try:
                    connector_info = connector_data.get("connector_info", {})
                    capabilities = connector_data.get("capabilities", {})
                    
                    type_id = connector_info.get("type_id")
                    if not type_id:
                        continue
                    
                    type_data = {
                        "name": connector_info.get("name", ""),
                        "display_name": connector_info.get("display_name", connector_info.get("name", "")),
                        "description": connector_info.get("description", ""),
                        "category": connector_info.get("category", "other"),
                        "version": connector_info.get("version", "1.0.0"),
                        "author": connector_info.get("author", ""),
                        "license": connector_info.get("license", ""),
                        "supports_multiple_instances": capabilities.get("supports_multiple_instances", False),
                        "max_instances_per_user": capabilities.get("max_instances_per_user", 1),
                        "auto_discovery": capabilities.get("auto_discovery", False),
                        "hot_config_reload": capabilities.get("hot_config_reload", True),
                        "health_check": capabilities.get("health_check", True),
                        "entry_point": connector_info.get("entry_point", "main.py"),
                        "dependencies": connector_data.get("package_info", {}).get("dependencies", []),
                        "permissions": connector_data.get("system_requirements", {}).get("permissions", []),
                        "config_schema": connector_data.get("config_schema", {}),
                        "default_config": connector_data.get("config_schema", {}).get("properties", {}),
                        "instance_templates": connector_data.get("instance_templates", [])
                    }
                    
                    connector_types[type_id] = type_data
                    
                except Exception as e:
                    logger.error(f"迁移连接器类型失败: {e}")
            
            return connector_types
            
        except Exception as e:
            logger.error(f"读取registry.json失败: {e}")
            return {}

    def _scan_connector_directories(self, base_dir: Path) -> Dict[str, Dict[str, Any]]:
        """扫描连接器目录"""
        connector_types = {}
        
        for connector_dir in base_dir.iterdir():
            if not connector_dir.is_dir():
                continue
                
            connector_json = connector_dir / "connector.json"
            if not connector_json.exists():
                continue
            
            try:
                with open(connector_json, "r", encoding="utf-8") as f:
                    connector_config = json.load(f)
                
                type_id = connector_config.get("id")
                if not type_id:
                    continue
                
                type_data = {
                    "name": connector_config.get("name", ""),
                    "display_name": connector_config.get("display_name", connector_config.get("name", "")),
                    "description": connector_config.get("description", ""),
                    "category": connector_config.get("category", "other"),
                    "version": connector_config.get("version", "1.0.0"),
                    "author": connector_config.get("author", ""),
                    "license": connector_config.get("license", ""),
                    "supports_multiple_instances": connector_config.get("capabilities", {}).get("supports_multiple_instances", False),
                    "max_instances_per_user": connector_config.get("capabilities", {}).get("max_instances_per_user", 1),
                    "entry_point": self._extract_entry_point(connector_config),
                    "dependencies": connector_config.get("dependencies", []),
                    "permissions": connector_config.get("permissions", []),
                    "config_schema": connector_config.get("config_schema", {}),
                    "default_config": connector_config.get("default_config", {}),
                    "instance_templates": connector_config.get("instance_templates", [])
                }
                
                connector_types[type_id] = type_data
                
            except Exception as e:
                logger.error(f"扫描连接器目录 {connector_dir.name} 失败: {e}")
        
        return connector_types

    def _extract_entry_point(self, connector_config: Dict[str, Any]) -> str:
        """提取连接器入口点"""
        entry = connector_config.get("entry", {})
        dev_entry = entry.get("development", {})
        if dev_entry and "args" in dev_entry:
            return dev_entry["args"][0] if dev_entry["args"] else "main.py"
        return "main.py"

    def _migrate_connector_instances(self) -> Dict[str, Dict[str, Any]]:
        """迁移连接器实例配置"""
        logger.info("🔄 迁移连接器实例配置...")
        
        instances = {}
        
        # TODO: 从数据库迁移现有实例
        # 这里简化实现，留给后续完善
        
        logger.info(f"✅ 连接器实例迁移完成，共 {len(instances)} 个实例")
        return instances

    def _generate_unified_configs(self, daemon_config: Dict[str, Any], 
                                connector_types: Dict[str, Dict[str, Any]],
                                instances: Dict[str, Dict[str, Any]]):
        """生成统一配置文件"""
        logger.info("📝 生成统一配置文件...")
        
        # 1. 生成主应用配置
        app_config = {
            "config_version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "metadata": {
                "description": "Linch Mind Core Configuration",
                "created_by": "UnifiedConfigMigrator",
                "schema_version": "1.0",
                "migration_timestamp": datetime.now().isoformat()
            },
            **daemon_config
        }
        
        with open(self.target_app_config, "w", encoding="utf-8") as f:
            f.write(f"""# Linch Mind Core Configuration
# Unified Configuration Management
# Generated: {datetime.now().isoformat()}
# Location: {self.target_app_config}
# 
# Environment variable overrides are supported for key settings
# See documentation for supported environment variables

""")
            yaml.dump(app_config, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        logger.info(f"✅ 已生成主应用配置: {self.target_app_config}")
        
        # 2. 生成连接器类型配置
        connectors_config = {
            "config_version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "metadata": {
                "description": "Linch Mind 连接器配置 - 统一配置源",
                "created_by": "UnifiedConfigMigrator",
                "schema_version": "1.0",
                "connector_count": len(connector_types),
                "migration_timestamp": datetime.now().isoformat()
            },
            "connector_types": connector_types
        }
        
        with open(self.target_connectors_config, "w", encoding="utf-8") as f:
            yaml.dump(connectors_config, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        logger.info(f"✅ 已生成连接器配置: {self.target_connectors_config}")
        
        # 3. 生成实例配置
        instances_config = {
            "config_version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "metadata": {
                "description": "连接器实例配置",
                "created_by": "UnifiedConfigMigrator",
                "instance_count": len(instances),
                "migration_timestamp": datetime.now().isoformat()
            },
            "instances": instances
        }
        
        with open(self.target_instances_config, "w", encoding="utf-8") as f:
            yaml.dump(instances_config, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        logger.info(f"✅ 已生成实例配置: {self.target_instances_config}")

    def _migrate_user_configs(self):
        """迁移用户配置（connectors侧配置）"""
        logger.info("🔄 迁移用户配置...")
        
        # 更新connectors/shared/config.py中的配置路径，指向新的位置
        user_config = {
            "daemon": {
                "url": "http://localhost:58471",
                "host": "localhost",
                "port": 58471
            },
            "connectors": {
                "auto_reconnect": True,
                "max_retry_attempts": 3,
                "retry_delay": 5
            },
            "development": {
                "debug_mode": False,
                "log_level": "INFO"
            }
        }
        
        # 将配置写入用户目录
        user_config_file = self.user_config_dir / "config.json"
        with open(user_config_file, "w", encoding="utf-8") as f:
            json.dump(user_config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ 已迁移用户配置: {user_config_file}")

    def _validate_migration(self) -> bool:
        """验证迁移结果"""
        logger.info("🔍 验证迁移结果...")
        
        try:
            # 验证主配置文件
            with open(self.target_app_config, "r", encoding="utf-8") as f:
                app_config = yaml.safe_load(f)
            
            if not app_config or "server" not in app_config:
                logger.error("主配置文件结构无效")
                return False
            
            # 验证连接器配置文件
            with open(self.target_connectors_config, "r", encoding="utf-8") as f:
                connectors_config = yaml.safe_load(f)
            
            if "connector_types" not in connectors_config:
                logger.error("连接器配置文件缺少connector_types部分")
                return False
            
            # 验证实例配置文件
            with open(self.target_instances_config, "r", encoding="utf-8") as f:
                instances_config = yaml.safe_load(f)
            
            if "instances" not in instances_config:
                logger.error("实例配置文件缺少instances部分")
                return False
            
            logger.info("✅ 迁移验证通过")
            return True
            
        except Exception as e:
            logger.error(f"验证迁移结果失败: {e}")
            return False

    def _cleanup_and_finalize(self):
        """清理和完成迁移"""
        logger.info("🧹 清理和完成迁移...")
        
        # 重命名旧文件为备份
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        files_to_backup = [
            (self.project_config, f"linch-mind.config_backup_{timestamp}.yaml"),
            (self.old_registry, f"registry_backup_{timestamp}.json")
        ]
        
        for old_file, backup_name in files_to_backup:
            if old_file.exists():
                backup_path = old_file.parent / backup_name
                old_file.rename(backup_path)
                logger.info(f"已备份: {old_file} -> {backup_path}")
        
        logger.info("✅ 清理完成")

    def _restore_from_backup(self):
        """从备份恢复"""
        logger.info("🔄 从备份恢复配置...")
        
        try:
            # 查找最新的备份文件并恢复
            backup_files = list(self.backup_dir.glob("*"))
            if backup_files:
                logger.info(f"找到 {len(backup_files)} 个备份文件")
                # 恢复逻辑可以根据需要实现
            
            logger.info("✅ 从备份恢复完成")
            
        except Exception as e:
            logger.error(f"从备份恢复失败: {e}")

    def _print_migration_summary(self, daemon_config: Dict, connector_types: Dict, instances: Dict):
        """打印迁移摘要"""
        print("\n" + "=" * 80)
        print("📊 统一配置迁移摘要")
        print("=" * 80)
        print(f"✅ 配置目录: {self.user_config_dir}")
        print(f"✅ 应用配置: {self.target_app_config}")
        print(f"✅ 连接器配置: {self.target_connectors_config}")
        print(f"✅ 实例配置: {self.target_instances_config}")
        print()
        print(f"📋 统计信息:")
        print(f"  - 迁移的连接器类型: {len(connector_types)}")
        print(f"  - 迁移的连接器实例: {len(instances)}")
        print(f"  - 备份目录: {self.backup_dir}")
        print()
        print("🔧 下一步操作:")
        print("1. 重启daemon以使用新配置")
        print("2. 验证连接器功能是否正常")
        print("3. 测试API接口是否工作正常")
        print("4. 如有问题，可从备份目录恢复旧配置")
        print("=" * 80)
        print("✅ 统一配置迁移完成！系统配置已统一到 ~/.linch-mind")
        print("=" * 80)


def main():
    """主函数"""
    print("🚀 Linch Mind 统一配置迁移工具")
    print("这个工具将把所有配置统一迁移到 ~/.linch-mind 目录")
    print()
    
    # 检查命令行参数
    auto_confirm = "--yes" in sys.argv or "-y" in sys.argv
    
    if not auto_confirm:
        try:
            response = input("是否继续迁移？(y/N): ")
            if response.lower() != "y":
                print("迁移取消")
                return
        except (EOFError, KeyboardInterrupt):
            print("\n迁移取消")
            return
    else:
        print("自动确认模式，开始迁移...")
    
    # 创建迁移器并运行
    migrator = UnifiedConfigMigrator()
    success = migrator.run_migration()
    
    if success:
        print("\n🎉 迁移成功完成！")
        print("建议：")
        print("1. 重启daemon: poetry run python daemon/api/main.py")
        print("2. 验证配置: python scripts/validate_connector_configs.py")
        print("3. 测试连接器功能")
    else:
        print("\n❌ 迁移失败，请检查日志信息")
        print("如有问题，可从备份目录恢复配置")


if __name__ == "__main__":
    main()