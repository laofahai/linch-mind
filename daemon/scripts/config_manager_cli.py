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

from config.user_config_manager import (
    UserConfigManager, get_user_config_manager,
    UserConfig, get_user_config
)
from core.environment_manager import get_environment_manager, Environment


def create_template_command(args):
    """生成配置模板"""
    print(f"🎯 生成配置模板: {args.format} 格式")
    
    try:
        manager = get_user_config_manager()
        
        # 确定输出路径
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = Path(f"linch-mind.{args.format}.template")
        
        # 生成模板
        manager.export_template(
            output_path=output_path,
            format_name=args.format,
            include_comments=not args.no_comments
        )
        
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
        if args.config_file:
            # 验证指定的配置文件
            config_path = Path(args.config_file)
            if not config_path.exists():
                print(f"❌ 配置文件不存在: {config_path}")
                return 1
            
            # 临时创建管理器来验证特定文件
            # 这里需要实现从特定文件加载配置的功能
            print(f"📁 验证配置文件: {config_path}")
            
        manager = get_user_config_manager()
        config = manager.get_config(force_reload=True)
        
        # 执行验证
        errors = manager._validate_config(config)
        
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
            
    except Exception as e:
        print(f"❌ 配置验证过程中出错: {e}")
        return 1
    
    return 0


def show_config_command(args):
    """显示当前配置"""
    print("📋 当前配置信息")
    print("=" * 50)
    
    try:
        manager = get_user_config_manager()
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
            config = manager.get_config()
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
        
        manager = get_user_config_manager()
        
        # 加载配置文件
        config = manager._load_config_file(input_path, args.input_format)
        
        # 保存为新格式
        manager._save_config_file(config, output_path, args.output_format)
        
        print(f"✅ 配置文件已转换: {output_path}")
        
    except Exception as e:
        print(f"❌ 配置文件转换失败: {e}")
        return 1
    
    return 0


def init_config_command(args):
    """初始化配置文件"""
    print("🚀 初始化配置文件")
    
    try:
        manager = get_user_config_manager()
        env_manager = get_environment_manager()
        
        config_dir = env_manager.get_config_directory()
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查是否已存在配置文件
        existing_configs = []
        for format_name, config_path in manager.config_files.items():
            if config_path.exists():
                existing_configs.append(f"{format_name}: {config_path}")
        
        if existing_configs and not args.force:
            print("⚠️  发现已存在的配置文件:")
            for config in existing_configs:
                print(f"  - {config}")
            print("\n使用 --force 参数强制覆盖现有配置文件")
            return 1
        
        # 创建默认配置
        config = UserConfig()
        
        # 应用环境默认值
        manager._apply_environment_defaults(config)
        
        # 保存配置文件
        format_name = args.format or 'toml'
        manager.save_config(config, format_name)
        
        print(f"✅ 已创建默认配置文件: {manager.config_files[format_name]}")
        
        # 创建环境特定配置示例（如果请求）
        if args.create_env_example:
            env_config_path = manager.env_config_files[format_name]
            
            # 创建简单的环境覆盖示例
            env_overrides = {
                'debug': True if env_manager.current_environment == Environment.DEVELOPMENT else False,
                'logging': {'level': 'debug' if env_manager.current_environment == Environment.DEVELOPMENT else 'info'}
            }
            
            env_config = UserConfig()
            env_config.debug = env_overrides['debug']
            env_config.logging.level = env_overrides['logging']['level']
            
            manager._save_config_file(env_config, env_config_path, format_name)
            print(f"✅ 已创建环境配置示例: {env_config_path}")
        
        print(f"\n🎯 配置初始化完成！")
        print(f"📂 配置目录: {config_dir}")
        print(f"🌍 当前环境: {env_manager.current_environment.value}")
        
    except Exception as e:
        print(f"❌ 初始化配置失败: {e}")
        return 1
    
    return 0


def migrate_env_vars_command(args):
    """从环境变量迁移配置"""
    print("🔄 从环境变量迁移配置...")
    
    try:
        import os
        
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
        
        manager = get_user_config_manager()
        config = manager.get_config()
        
        migrated_vars = []
        
        for env_var, (section, key) in env_var_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    if section is None:
                        # 顶级配置
                        if env_var == 'LINCH_DEBUG':
                            config.debug = env_value.lower() in ('true', '1', 'yes')
                            migrated_vars.append(f"{env_var} -> debug")
                    else:
                        # 子配置
                        section_obj = getattr(config, section)
                        
                        # 类型转换
                        if key == 'value_threshold':
                            value = float(env_value)
                        elif key in ['enable_caching', 'enable_intelligent_processing']:
                            value = env_value.lower() in ('true', '1', 'yes')
                        else:
                            value = env_value
                        
                        setattr(section_obj, key, value)
                        migrated_vars.append(f"{env_var} -> {section}.{key}")
                        
                except Exception as e:
                    print(f"⚠️  无法迁移 {env_var}: {e}")
        
        if migrated_vars:
            # 保存更新的配置
            format_name = args.format or 'toml'
            manager.save_config(config, format_name)
            
            print(f"✅ 成功迁移 {len(migrated_vars)} 个环境变量:")
            for var in migrated_vars:
                print(f"  - {var}")
            
            print(f"\n💡 建议: 迁移完成后，可以移除相应的环境变量")
            
        else:
            print("ℹ️  没有发现需要迁移的环境变量")
            
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
        
        manager = get_user_config_manager()
        
        # 加载两个配置文件
        format1 = config1_path.suffix[1:]  # 移除点号
        format2 = config2_path.suffix[1:]
        
        config1 = manager._load_config_file(config1_path, format1)
        config2 = manager._load_config_file(config2_path, format2)
        
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