#!/usr/bin/env python3
"""
⚠️ 此文件已废弃 - 用户配置迁移工具

新的配置系统直接使用数据库存储，无需迁移旧配置文件。
请使用以下命令初始化新配置：

    python scripts/config_manager_cli.py init-db

废弃原因：现在使用DatabaseConfigManager统一管理所有配置。
"""

print("⚠️ 此迁移工具已废弃")
print("请使用: python scripts/config_manager_cli.py init-db")
exit(1)

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 旧版配置迁移工具已废弃，使用新的数据库配置系统
# from config.user_config_manager import get_user_config_manager, UserConfig
# from services.user_config_db_service import get_user_config_db_service
from config.database_config_manager import get_database_config_manager
from services.user_config_db_service import get_user_config_db_service
from core.environment_manager import get_environment_manager

logger = logging.getLogger(__name__)


class UserConfigMigrationTool:
    """用户配置迁移工具"""

    def __init__(self):
        self.config_manager = get_user_config_manager()
        self.db_service = get_user_config_db_service()
        self.env_manager = get_environment_manager()
        
        # 定义需要迁移到数据库的个性化配置
        self.personalizable_configs = {
            "ollama": {
                "llm_model": "用户首选的LLM模型",
                "embedding_model": "用户首选的嵌入模型",
                "value_threshold": "AI价值判断阈值",
                "entity_threshold": "实体识别阈值",
                "request_timeout": "请求超时时间",
                "enable_cache": "是否启用缓存",
                "cache_ttl_seconds": "缓存过期时间",
            },
            
            "vector": {
                "vector_dimension": "向量维度",
                "compressed_dimension": "压缩后维度",
                "max_search_results": "最大搜索结果数",
                "search_timeout": "搜索超时时间",
                "compression_method": "压缩方法",
                "index_type": "索引类型",
            },
            
            "performance": {
                "enable_caching": "是否启用缓存",
                "cache_size_mb": "缓存大小",
                "cache_ttl_seconds": "缓存TTL",
                "max_workers": "最大工作线程数",
                "max_concurrent_requests": "最大并发请求数",
                "auto_cleanup": "是否自动清理",
                "cleanup_interval_hours": "清理间隔小时",
            },
            
            "security": {
                "encrypt_vectors": "是否加密向量",
                "encrypt_logs": "是否加密日志",
                "session_timeout_minutes": "会话超时分钟数",
            },
            
            "logging": {
                "level": "日志级别",
                "enable_console": "是否启用控制台输出",
                "enable_file": "是否启用文件输出",
                "max_file_size_mb": "最大文件大小",
                "backup_count": "备份文件数量",
            },
        }

    async def analyze_current_config(self) -> Dict[str, Any]:
        """分析当前配置，识别可迁移的个性化设置"""
        logger.info("🔍 分析当前配置...")
        
        # 获取当前完整配置
        current_config = self.config_manager.get_config()
        
        # 分析个性化配置
        personalizable_found = {}
        
        for section_name, config_keys in self.personalizable_configs.items():
            section_obj = getattr(current_config, section_name, None)
            if not section_obj:
                continue
                
            section_configs = {}
            for key, description in config_keys.items():
                if hasattr(section_obj, key):
                    value = getattr(section_obj, key)
                    section_configs[key] = {
                        "value": value,
                        "description": description,
                        "is_default": self._is_default_value(section_name, key, value)
                    }
            
            if section_configs:
                personalizable_found[section_name] = section_configs
        
        return personalizable_found

    async def check_existing_db_configs(self) -> Dict[str, Set[str]]:
        """检查数据库中已存在的配置"""
        logger.info("📋 检查数据库中已存在的配置...")
        
        existing_configs = {}
        
        for section_name in self.personalizable_configs.keys():
            try:
                section_configs = await self.db_service.get_section_configs(section_name)
                if section_configs:
                    existing_configs[section_name] = set(section_configs.keys())
                else:
                    existing_configs[section_name] = set()
            except Exception as e:
                logger.warning(f"检查数据库配置失败 {section_name}: {e}")
                existing_configs[section_name] = set()
        
        return existing_configs

    async def migrate_configs(
        self,
        configs_to_migrate: Dict[str, Any],
        force_overwrite: bool = False,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """迁移配置到数据库
        
        Args:
            configs_to_migrate: 要迁移的配置
            force_overwrite: 是否强制覆盖已存在的配置
            dry_run: 是否只是演练，不实际执行
            
        Returns:
            迁移结果
        """
        logger.info(f"🚀 开始迁移配置 (dry_run={dry_run})...")
        
        migration_results = {
            "successful": [],
            "skipped": [],
            "failed": [],
            "total": 0
        }
        
        # 检查已存在的配置
        existing_configs = await self.check_existing_db_configs()
        
        for section_name, section_configs in configs_to_migrate.items():
            for key, config_info in section_configs.items():
                migration_results["total"] += 1
                
                # 检查是否已存在
                if key in existing_configs.get(section_name, set()) and not force_overwrite:
                    migration_results["skipped"].append(f"{section_name}.{key}")
                    logger.info(f"⏭️ 跳过已存在的配置: {section_name}.{key}")
                    continue
                
                if not dry_run:
                    # 执行迁移
                    try:
                        success = await self.db_service.set_config_value(
                            section=section_name,
                            key=key,
                            value=config_info["value"],
                            config_type="user_preference",
                            description=config_info["description"],
                            changed_by="migration_tool"
                        )
                        
                        if success:
                            migration_results["successful"].append(f"{section_name}.{key}")
                            logger.info(f"✅ 迁移成功: {section_name}.{key} = {config_info['value']}")
                        else:
                            migration_results["failed"].append(f"{section_name}.{key}")
                            logger.error(f"❌ 迁移失败: {section_name}.{key}")
                            
                    except Exception as e:
                        migration_results["failed"].append(f"{section_name}.{key}")
                        logger.error(f"❌ 迁移异常 {section_name}.{key}: {e}")
                else:
                    # 演练模式
                    migration_results["successful"].append(f"{section_name}.{key}")
                    logger.info(f"🎭 演练迁移: {section_name}.{key} = {config_info['value']}")
        
        return migration_results

    async def verify_migration(self, migrated_configs: List[str]) -> Dict[str, Any]:
        """验证迁移结果"""
        logger.info("🔍 验证迁移结果...")
        
        verification_results = {
            "verified": [],
            "failed": [],
            "total": len(migrated_configs)
        }
        
        for config_path in migrated_configs:
            try:
                section, key = config_path.split(".", 1)
                
                # 从数据库读取配置值
                db_value = await self.db_service.get_config_value(section, key)
                
                if db_value is not None:
                    verification_results["verified"].append(config_path)
                    logger.debug(f"✅ 验证成功: {config_path}")
                else:
                    verification_results["failed"].append(config_path)
                    logger.warning(f"❌ 验证失败: {config_path} 在数据库中不存在")
                    
            except Exception as e:
                verification_results["failed"].append(config_path)
                logger.error(f"❌ 验证异常 {config_path}: {e}")
        
        return verification_results

    def _is_default_value(self, section: str, key: str, value: Any) -> bool:
        """判断是否为默认值"""
        # 创建默认配置对象
        default_config = UserConfig()
        
        try:
            section_obj = getattr(default_config, section)
            default_value = getattr(section_obj, key)
            return value == default_value
        except AttributeError:
            return False

    async def create_migration_report(
        self,
        analysis_result: Dict[str, Any],
        migration_result: Dict[str, Any],
        verification_result: Dict[str, Any]
    ) -> str:
        """创建迁移报告"""
        report_lines = [
            "# 用户配置迁移报告",
            f"迁移时间: {self.env_manager.current_environment.value} 环境",
            "",
            "## 配置分析结果",
        ]
        
        total_personalizable = sum(len(configs) for configs in analysis_result.values())
        report_lines.append(f"发现可个性化配置: {total_personalizable} 项")
        
        for section, configs in analysis_result.items():
            report_lines.append(f"### {section} ({len(configs)} 项)")
            for key, info in configs.items():
                status = "默认值" if info["is_default"] else "已自定义"
                report_lines.append(f"- {key}: {info['value']} ({status})")
            report_lines.append("")
        
        report_lines.extend([
            "## 迁移结果",
            f"总配置数: {migration_result['total']}",
            f"成功迁移: {len(migration_result['successful'])}",
            f"跳过配置: {len(migration_result['skipped'])}",
            f"失败配置: {len(migration_result['failed'])}",
            "",
        ])
        
        if migration_result["successful"]:
            report_lines.append("### 成功迁移的配置:")
            for config in migration_result["successful"]:
                report_lines.append(f"- ✅ {config}")
            report_lines.append("")
        
        if migration_result["skipped"]:
            report_lines.append("### 跳过的配置:")
            for config in migration_result["skipped"]:
                report_lines.append(f"- ⏭️ {config}")
            report_lines.append("")
        
        if migration_result["failed"]:
            report_lines.append("### 失败的配置:")
            for config in migration_result["failed"]:
                report_lines.append(f"- ❌ {config}")
            report_lines.append("")
        
        report_lines.extend([
            "## 验证结果",
            f"验证通过: {len(verification_result['verified'])}/{verification_result['total']}",
            f"验证失败: {len(verification_result['failed'])}/{verification_result['total']}",
        ])
        
        if verification_result["failed"]:
            report_lines.append("### 验证失败的配置:")
            for config in verification_result["failed"]:
                report_lines.append(f"- ❌ {config}")
        
        return "\n".join(report_lines)


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="用户配置迁移工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 分析可迁移的配置
  python migrate_user_config.py analyze
  
  # 演练迁移（不实际执行）
  python migrate_user_config.py migrate --dry-run
  
  # 执行迁移
  python migrate_user_config.py migrate
  
  # 强制覆盖已存在的配置
  python migrate_user_config.py migrate --force
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析可迁移的配置')
    analyze_parser.add_argument('--output', '-o', help='保存分析结果到文件')
    
    # migrate 命令
    migrate_parser = subparsers.add_parser('migrate', help='执行配置迁移')
    migrate_parser.add_argument('--dry-run', action='store_true', help='演练模式，不实际执行')
    migrate_parser.add_argument('--force', action='store_true', help='强制覆盖已存在的配置')
    migrate_parser.add_argument('--report', '-r', help='保存迁移报告到文件')
    
    # verify 命令
    verify_parser = subparsers.add_parser('verify', help='验证已迁移的配置')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        migration_tool = UserConfigMigrationTool()
        
        if args.command == 'analyze':
            print("🔍 分析可迁移的配置...")
            analysis_result = await migration_tool.analyze_current_config()
            
            total_configs = sum(len(configs) for configs in analysis_result.values())
            print(f"\n📊 分析结果: 发现 {total_configs} 个可个性化配置项")
            
            for section, configs in analysis_result.items():
                print(f"\n📦 {section} ({len(configs)} 项):")
                for key, info in configs.items():
                    status = "默认值" if info["is_default"] else "已自定义"
                    print(f"  - {key}: {info['value']} ({status})")
                    print(f"    描述: {info['description']}")
            
            if args.output:
                output_path = Path(args.output)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(analysis_result, f, ensure_ascii=False, indent=2)
                print(f"\n💾 分析结果已保存到: {output_path}")
        
        elif args.command == 'migrate':
            print("🚀 开始配置迁移...")
            
            # 分析配置
            analysis_result = await migration_tool.analyze_current_config()
            
            # 执行迁移
            migration_result = await migration_tool.migrate_configs(
                analysis_result,
                force_overwrite=args.force,
                dry_run=args.dry_run
            )
            
            # 验证迁移（如果不是演练模式）
            if not args.dry_run and migration_result["successful"]:
                verification_result = await migration_tool.verify_migration(
                    migration_result["successful"]
                )
            else:
                verification_result = {"verified": [], "failed": [], "total": 0}
            
            # 显示结果
            print(f"\n📊 迁移结果:")
            print(f"  总配置数: {migration_result['total']}")
            print(f"  成功迁移: {len(migration_result['successful'])}")
            print(f"  跳过配置: {len(migration_result['skipped'])}")
            print(f"  失败配置: {len(migration_result['failed'])}")
            
            if not args.dry_run and verification_result["total"] > 0:
                print(f"\n✅ 验证结果:")
                print(f"  验证通过: {len(verification_result['verified'])}/{verification_result['total']}")
                print(f"  验证失败: {len(verification_result['failed'])}/{verification_result['total']}")
            
            # 生成报告
            if args.report:
                report_content = await migration_tool.create_migration_report(
                    analysis_result, migration_result, verification_result
                )
                report_path = Path(args.report)
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                print(f"\n📋 迁移报告已保存到: {report_path}")
            
            if args.dry_run:
                print("\n💡 这是演练模式，没有实际修改配置。使用 --dry-run=false 执行真实迁移。")
        
        elif args.command == 'verify':
            print("🔍 验证已迁移的配置...")
            
            # 获取所有已迁移的配置
            migrated_configs = []
            for section_name in migration_tool.personalizable_configs.keys():
                try:
                    section_configs = await migration_tool.db_service.get_section_configs(section_name)
                    for key in section_configs.keys():
                        migrated_configs.append(f"{section_name}.{key}")
                except Exception as e:
                    logger.warning(f"获取配置段失败 {section_name}: {e}")
            
            if not migrated_configs:
                print("❌ 没有发现已迁移的配置")
                return 1
            
            verification_result = await migration_tool.verify_migration(migrated_configs)
            
            print(f"\n✅ 验证结果:")
            print(f"  验证通过: {len(verification_result['verified'])}/{verification_result['total']}")
            print(f"  验证失败: {len(verification_result['failed'])}/{verification_result['total']}")
            
            if verification_result["failed"]:
                print("\n❌ 验证失败的配置:")
                for config in verification_result["failed"]:
                    print(f"  - {config}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ 操作被用户中断")
        return 1
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        logger.exception("详细错误信息:")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))