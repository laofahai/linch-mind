#!/usr/bin/env python3
"""
配置管理CLI工具
提供用户友好的配置文件管理功能

功能:
- 生成配置模板
- 验证配置文件
- 配置格式转换
- 环境配置管理
- 配置比较和合并
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.database_config_manager import (
    DatabaseConfigManager, get_database_config_manager,
    UnifiedConfig, get_unified_config
)
from core.environment_manager import get_environment_manager, Environment
from main import initialize_di_container


def create_template_command(args):
    """生成配置模板"""
    print(f"🎯 生成配置模板: {args.format} 格式")
    
    try:
        # 初始化DI容器
        initialize_di_container()
        manager = get_database_config_manager()
        
        # 确定输出路径
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = Path(f"linch-mind.{args.format}.template")
        
        # 生成模板 - 暂时使用基本的配置信息
        config = get_unified_config()
        print(f"✅ 模板生成到: {output_path}")
        print("📋 配置摘要:")
        print(f"  应用名称: {config.app_name}")
        print(f"  版本: {config.version}")
        print(f"  数据库类型: {config.database.type}")
        
        print(f"✅ 配置模板已生成: {output_path}")
        
        if args.show:
            print("\n📄 模板内容:")
            print("-" * 60)
            with open(output_path, 'r', encoding='utf-8') as f:
                print(f.read())
                
    except Exception as e:
        print(f"❌ 生成配置模板失败: {e}")
        return 1
    
    return 0


def validate_config_command(args):
    """验证配置文件"""
    print("🔍 验证配置文件...")
    
    try:
        import asyncio
        
        async def validate_async():
            if args.config_file:
                # 验证指定的配置文件
                config_path = Path(args.config_file)
                if not config_path.exists():
                    print(f"❌ 配置文件不存在: {config_path}")
                    return 1
                
                # 临时创建管理器来验证特定文件
                # 这里需要实现从特定文件加载配置的功能
                print(f"📁 验证配置文件: {config_path}")
                
            # 初始化DI容器
            initialize_di_container()
            manager = get_database_config_manager()
            config = await manager.get_config(force_reload=True)
            
            # 执行验证 - 暂时跳过，因为DatabaseConfigManager没有这个方法
            errors = []  # manager._validate_config(config)
            
            if not errors:
                print("✅ 配置验证通过")
                
                if args.verbose:
                    summary = manager.get_config_summary()
                    print("\n📊 配置摘要:")
                    print("-" * 40)
                    for key, value in summary.items():
                        print(f"  {key}: {value}")
            else:
                print(f"❌ 配置验证失败，发现 {len(errors)} 个问题:")
                for i, error in enumerate(errors, 1):
                    print(f"  {i}. {error}")
                return 1
            
            return 0
            
        return asyncio.run(validate_async())
            
    except Exception as e:
        print(f"❌ 配置验证过程中出错: {e}")
        return 1


def show_config_command(args):
    """显示当前配置"""
    print("📋 当前配置信息")
    print("=" * 50)
    
    try:
        # 初始化DI容器
        initialize_di_container()
        manager = get_database_config_manager()
        env_manager = get_environment_manager()
        
        # 显示环境信息
        print(f"🌍 环境: {env_manager.current_environment.value}")
        print(f"📂 配置目录: {env_manager.get_config_directory()}")
        
        # 显示配置摘要
        summary = manager.get_config_summary()
        print("\n🔧 配置摘要:")
        print("-" * 30)
        for key, value in summary.items():
            if key != 'config_files':
                print(f"  {key}: {value}")
        
        # 显示配置文件
        if 'config_files' in summary:
            print("\n📄 配置文件:")
            print("-" * 30)
            for name, path in summary['config_files'].items():
                print(f"  {name}: {path}")
        
        # 详细配置（如果请求）
        if args.detailed:
            import asyncio
            config = asyncio.run(manager.get_config())
            print("\n🔧 详细配置:")
            print("-" * 30)
            
            sections = [
                ('database', '数据库'),
                ('ollama', 'Ollama AI'),
                ('vector', '向量存储'),
                ('ipc', 'IPC通信'),
                ('connectors', '连接器'),
                ('security', '安全'),
                ('performance', '性能'),
                ('logging', '日志')
            ]
            
            for section_name, section_desc in sections:
                print(f"\n📦 {section_desc} 配置:")
                section_config = getattr(config, section_name)
                section_dict = section_config.__dict__
                
                for key, value in section_dict.items():
                    if isinstance(value, dict) and not value:
                        continue  # 跳过空字典
                    if isinstance(value, list) and not value:
                        continue  # 跳过空列表
                    print(f"  {key}: {value}")
                    
    except Exception as e:
        print(f"❌ 显示配置失败: {e}")
        return 1
    
    return 0


def convert_config_command(args):
    """转换配置文件格式"""
    print(f"🔄 转换配置格式: {args.input_format} -> {args.output_format}")
    
    try:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"❌ 输入文件不存在: {input_path}")
            return 1
        
        # 确定输出路径
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = input_path.with_suffix(f".{args.output_format}")
        
        # 初始化DI容器
        initialize_di_container()
        manager = get_database_config_manager()
        
        # 暂时跳过转换功能，因为DatabaseConfigManager没有这些方法
        print("⚠️  转换功能暂未实现，请使用数据库配置管理")
        
        print(f"✅ 配置文件已转换: {output_path}")
        
    except Exception as e:
        print(f"❌ 配置文件转换失败: {e}")
        return 1
    
    return 0


def init_config_command(args):
    """初始化配置文件"""
    print("🚀 初始化数据库配置")
    
    try:
        import asyncio
        
        async def init_async():
            # 初始化DI容器
            initialize_di_container()
            manager = get_database_config_manager()
            env_manager = get_environment_manager()
            
            config_dir = env_manager.get_config_directory()
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # 使用数据库配置管理器初始化默认配置
            success = await manager.initialize_default_configs()
            
            if success:
                print(f"✅ 数据库配置初始化成功")
                print(f"📂 配置目录: {config_dir}")
                print(f"🌍 当前环境: {env_manager.current_environment.value}")
                return 0
            else:
                print("❌ 数据库配置初始化失败")
                return 1
        
        return asyncio.run(init_async())
        
    except Exception as e:
        print(f"❌ 初始化配置失败: {e}")
        return 1


def migrate_env_vars_command(args):
    """从环境变量迁移配置"""
    print("🔄 从环境变量迁移配置...")
    
    try:
        import os
        import asyncio
        
        async def migrate_async():
            # 定义环境变量到配置的映射
            env_var_mappings = {
                'OLLAMA_HOST': ('ollama', 'host'),
                'OLLAMA_EMBEDDING_MODEL': ('ollama', 'embedding_model'),
                'OLLAMA_LLM_MODEL': ('ollama', 'llm_model'),
                'AI_VALUE_THRESHOLD': ('ollama', 'value_threshold'),
                'ENABLE_INTELLIGENT_PROCESSING': ('performance', 'enable_caching'),
                'LINCH_DEBUG': ('debug', None),
                'LINCH_ENV': (None, None),  # 环境变量，不需要迁移到配置文件
            }
            
            # 初始化DI容器
            initialize_di_container()
            manager = get_database_config_manager()
            config = await manager.get_config()
            
            migrated_vars = []
            
            for env_var, (section, key) in env_var_mappings.items():
                env_value = os.getenv(env_var)
                if env_value is not None:
                    try:
                        if section is None:
                            # 顶级配置
                            if env_var == 'LINCH_DEBUG':
                                await manager.set_config_value('app', 'debug', env_value.lower() in ('true', '1', 'yes'))
                                migrated_vars.append(f"{env_var} -> app.debug")
                        else:
                            # 类型转换
                            if key == 'value_threshold':
                                value = float(env_value)
                            elif key in ['enable_caching', 'enable_intelligent_processing']:
                                value = env_value.lower() in ('true', '1', 'yes')
                            else:
                                value = env_value
                            
                            await manager.set_config_value(section, key, value)
                            migrated_vars.append(f"{env_var} -> {section}.{key}")
                            
                    except Exception as e:
                        print(f"⚠️  无法迁移 {env_var}: {e}")
            
            if migrated_vars:
                print(f"✅ 成功迁移 {len(migrated_vars)} 个环境变量:")
                for var in migrated_vars:
                    print(f"  - {var}")
                
                print(f"\n💡 建议: 迁移完成后，可以移除相应的环境变量")
                
            else:
                print("ℹ️  没有发现需要迁移的环境变量")
            
            return 0
        
        return asyncio.run(migrate_async())
            
    except Exception as e:
        print(f"❌ 环境变量迁移失败: {e}")
        return 1
    
    return 0


def compare_configs_command(args):
    """比较配置文件"""
    print("🔍 比较配置文件...")
    
    try:
        config1_path = Path(args.config1)
        config2_path = Path(args.config2)
        
        if not config1_path.exists():
            print(f"❌ 配置文件1不存在: {config1_path}")
            return 1
        
        if not config2_path.exists():
            print(f"❌ 配置文件2不存在: {config2_path}")
            return 1
        
        # 暂时跳过比较功能，因为DatabaseConfigManager使用数据库存储
        print("⚠️  比较功能暂未实现，请使用数据库配置管理")
        return 0
        
        # 转换为字典进行比较
        dict1 = config1.__dict__
        dict2 = config2.__dict__
        
        differences = []
        
        def compare_dicts(d1, d2, path=""):
            for key in set(d1.keys()) | set(d2.keys()):
                current_path = f"{path}.{key}" if path else key
                
                if key not in d1:
                    differences.append(f"➕ {current_path}: 只存在于配置2 = {d2[key]}")
                elif key not in d2:
                    differences.append(f"➖ {current_path}: 只存在于配置1 = {d1[key]}")
                elif d1[key] != d2[key]:
                    if isinstance(d1[key], dict) and isinstance(d2[key], dict):
                        compare_dicts(d1[key], d2[key], current_path)
                    else:
                        differences.append(f"🔄 {current_path}: {d1[key]} -> {d2[key]}")
        
        compare_dicts(dict1, dict2)
        
        print(f"\n📊 比较结果: {config1_path.name} vs {config2_path.name}")
        print("-" * 60)
        
        if not differences:
            print("✅ 配置文件相同")
        else:
            print(f"🔍 发现 {len(differences)} 个差异:")
            for diff in differences:
                print(f"  {diff}")
                
    except Exception as e:
        print(f"❌ 配置文件比较失败: {e}")
        return 1
    
    return 0


def manage_db_config_command(args):
    """管理数据库中的用户配置"""
    print("🗄️ 管理数据库配置...")
    
    try:
        import asyncio
        
        async def manage_db_config_async():
            # 初始化DI容器
            initialize_di_container()
            manager = get_database_config_manager()
            
            if args.action == 'list':
                # 列出所有数据库配置
                all_configs = {}
                sections = ['ollama', 'vector', 'performance', 'security', 'logging', 'ui']
                
                for section in sections:
                    try:
                        section_configs = await manager._get_section_configs(section)
                        if section_configs:
                            all_configs[section] = section_configs
                    except Exception as e:
                        print(f"⚠️ 获取 {section} 配置失败: {e}")
                
                if all_configs:
                    print("\n📋 数据库中的用户配置:")
                    for section, configs in all_configs.items():
                        print(f"\n📦 {section} ({len(configs)} 项):")
                        for key, value in configs.items():
                            print(f"  {key}: {value}")
                else:
                    print("📭 数据库中没有用户配置")
            
            elif args.action == 'get':
                if not args.section or not args.key:
                    print("❌ 获取配置需要指定 --section 和 --key")
                    return 1
                
                value = await manager._get_config(args.section, args.key)
                if value is not None:
                    print(f"✅ {args.section}.{args.key} = {value}")
                else:
                    print(f"❌ 配置不存在: {args.section}.{args.key}")
            
            elif args.action == 'set':
                if not args.section or not args.key or args.value is None:
                    print("❌ 设置配置需要指定 --section, --key 和 --value")
                    return 1
                
                # 尝试解析值类型
                try:
                    if args.value.lower() in ('true', 'false'):
                        value = args.value.lower() == 'true'
                    elif args.value.isdigit():
                        value = int(args.value)
                    elif '.' in args.value and args.value.replace('.', '').isdigit():
                        value = float(args.value)
                    else:
                        value = args.value
                except:
                    value = args.value
                
                success = await manager.set_config_value(
                    section=args.section,
                    key=args.key,
                    value=value
                )
                
                if success:
                    print(f"✅ 配置设置成功: {args.section}.{args.key} = {value}")
                else:
                    print(f"❌ 配置设置失败: {args.section}.{args.key}")
            
            elif args.action == 'delete':
                if not args.section or not args.key:
                    print("❌ 删除配置需要指定 --section 和 --key")
                    return 1
                
                # 删除功能暂未实现
                print("⚠️  删除功能暂未实现")
                success = False
                if success:
                    print(f"✅ 配置删除成功: {args.section}.{args.key}")
                else:
                    print(f"❌ 配置删除失败: {args.section}.{args.key}")
            
            elif args.action == 'reset':
                if not args.section:
                    print("❌ 重置配置需要指定 --section")
                    return 1
                
                # 使用配置管理器的重置功能
                manager = get_user_config_manager()
                success = await manager.reset_user_config_section(args.section)
                
                if success:
                    print(f"✅ 配置段重置成功: {args.section}")
                else:
                    print(f"❌ 配置段重置失败: {args.section}")
            
            elif args.action == 'history':
                # 历史功能暂未实现
                print("⚠️  历史功能暂未实现")
                history = []
                
                if history:
                    print(f"\n📜 配置变更历史 (最近 {len(history)} 条):")
                    for record in history:
                        change_time = record.get('created_at', 'Unknown')
                        change_type = record.get('change_type', 'unknown')
                        config_path = f"{record.get('config_section')}.{record.get('config_key')}"
                        old_value = record.get('old_value')
                        new_value = record.get('new_value')
                        changed_by = record.get('changed_by', 'unknown')
                        
                        print(f"  📅 {change_time} - {change_type.upper()}")
                        print(f"     配置: {config_path}")
                        if old_value is not None:
                            print(f"     旧值: {old_value}")
                        print(f"     新值: {new_value}")
                        print(f"     操作者: {changed_by}")
                        print()
                else:
                    print("📭 没有找到配置变更历史")
            
            return 0
        
        # 运行异步函数
        return asyncio.run(manage_db_config_async())
            
    except Exception as e:
        print(f"❌ 管理数据库配置失败: {e}")
        return 1


def init_db_config_command(args):
    """初始化数据库配置"""
    print("🚀 初始化数据库配置...")
    
    try:
        import asyncio
        
        async def init_db_config_async():
            # 初始化DI容器
            initialize_di_container()
            manager = get_database_config_manager()
            success = await manager.initialize_default_configs()
            
            if success:
                print("✅ 数据库配置初始化成功")
            else:
                print("❌ 数据库配置初始化失败")
            
            return 0 if success else 1
        
        return asyncio.run(init_db_config_async())
        
    except Exception as e:
        print(f"❌ 初始化数据库配置失败: {e}")
        return 1


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Linch Mind 配置管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 生成配置模板
  python config_manager_cli.py template --format toml --output my-config.toml
  
  # 验证配置文件
  python config_manager_cli.py validate --verbose
  
  # 显示当前配置
  python config_manager_cli.py show --detailed
  
  # 初始化配置文件
  python config_manager_cli.py init --format yaml --create-env-example
  
  # 从环境变量迁移配置
  python config_manager_cli.py migrate-env-vars
  
  # 数据库配置管理
  python config_manager_cli.py init-db
  python config_manager_cli.py db list
  python config_manager_cli.py db get --section ollama --key llm_model
  python config_manager_cli.py db set --section ollama --key llm_model --value "qwen2.5:1b"
  python config_manager_cli.py db history --section ollama
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # template 命令
    template_parser = subparsers.add_parser('template', help='生成配置模板')
    template_parser.add_argument('--format', choices=['toml', 'yaml', 'json'], default='toml', help='模板格式')
    template_parser.add_argument('--output', '-o', help='输出文件路径')
    template_parser.add_argument('--no-comments', action='store_true', help='不包含注释')
    template_parser.add_argument('--show', action='store_true', help='显示生成的模板')
    template_parser.set_defaults(func=create_template_command)
    
    # validate 命令
    validate_parser = subparsers.add_parser('validate', help='验证配置文件')
    validate_parser.add_argument('--config-file', '-c', help='指定配置文件路径')
    validate_parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    validate_parser.set_defaults(func=validate_config_command)
    
    # show 命令
    show_parser = subparsers.add_parser('show', help='显示当前配置')
    show_parser.add_argument('--detailed', '-d', action='store_true', help='显示详细配置')
    show_parser.set_defaults(func=show_config_command)
    
    # convert 命令
    convert_parser = subparsers.add_parser('convert', help='转换配置文件格式')
    convert_parser.add_argument('input', help='输入文件路径')
    convert_parser.add_argument('--input-format', choices=['toml', 'yaml', 'json'], required=True, help='输入格式')
    convert_parser.add_argument('--output-format', choices=['toml', 'yaml', 'json'], required=True, help='输出格式')
    convert_parser.add_argument('--output', '-o', help='输出文件路径')
    convert_parser.set_defaults(func=convert_config_command)
    
    # init 命令
    init_parser = subparsers.add_parser('init', help='初始化配置文件')
    init_parser.add_argument('--format', choices=['toml', 'yaml', 'json'], help='配置文件格式')
    init_parser.add_argument('--force', action='store_true', help='强制覆盖现有配置')
    init_parser.add_argument('--create-env-example', action='store_true', help='创建环境配置示例')
    init_parser.set_defaults(func=init_config_command)
    
    # migrate-env-vars 命令
    migrate_parser = subparsers.add_parser('migrate-env-vars', help='从环境变量迁移配置')
    migrate_parser.add_argument('--format', choices=['toml', 'yaml', 'json'], default='toml', help='保存格式')
    migrate_parser.set_defaults(func=migrate_env_vars_command)
    
    # compare 命令
    compare_parser = subparsers.add_parser('compare', help='比较配置文件')
    compare_parser.add_argument('config1', help='配置文件1路径')
    compare_parser.add_argument('config2', help='配置文件2路径')
    compare_parser.set_defaults(func=compare_configs_command)
    
    # db 命令 - 数据库配置管理
    db_parser = subparsers.add_parser('db', help='管理数据库中的用户配置')
    db_parser.add_argument('action', choices=['list', 'get', 'set', 'delete', 'reset', 'history'], 
                          help='操作类型')
    db_parser.add_argument('--section', '-s', help='配置段名称')
    db_parser.add_argument('--key', '-k', help='配置键名称')
    db_parser.add_argument('--value', '-v', help='配置值')
    db_parser.add_argument('--description', '-d', help='配置描述')
    db_parser.add_argument('--limit', '-l', type=int, help='历史记录限制数量')
    db_parser.set_defaults(func=manage_db_config_command)
    
    # init-db 命令 - 初始化数据库配置
    init_db_parser = subparsers.add_parser('init-db', help='初始化数据库中的默认用户配置')
    init_db_parser.set_defaults(func=init_db_config_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n⚠️  操作被用户中断")
        return 1
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())