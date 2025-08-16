#!/usr/bin/env python3
"""
环境管理CLI工具
提供便捷的环境切换、状态查看和配置管理功能
"""

import argparse
import os
import sys
from pathlib import Path

# 添加daemon目录到Python路径
daemon_dir = Path(__file__).parent.parent
sys.path.insert(0, str(daemon_dir))

from core.environment_manager import get_environment_manager, Environment
from config.intelligent_storage import get_config_manager


def show_current_status():
    """显示当前环境状态"""
    env_mgr = get_environment_manager()
    config_mgr = get_config_manager()
    
    print("=== 当前环境状态 ===")
    print(f"环境: {env_mgr.current_environment.value}")
    print(f"调试模式: {env_mgr.is_debug_enabled()}")
    print(f"数据加密: {env_mgr.should_use_encryption()}")
    print(f"配置目录: {env_mgr.get_config_directory()}")
    print(f"数据库: {env_mgr.get_database_url()}")
    
    print("\n=== AI模型配置 ===")
    print(f"Ollama主机: {config_mgr.get_ollama_host()}")
    print(f"嵌入模型: {config_mgr.get_embedding_model()}")
    print(f"LLM模型: {config_mgr.get_llm_model()}")
    print(f"价值阈值: {config_mgr.get_value_threshold()}")
    
    print("\n=== 环境变量覆盖 ===")
    env_vars = [
        ('LINCH_MIND_ENVIRONMENT', '指定环境'),
        ('OLLAMA_HOST', 'Ollama服务地址'),
        ('OLLAMA_LLM_MODEL', 'LLM模型名称'),
        ('OLLAMA_EMBEDDING_MODEL', '嵌入模型名称'),
        ('AI_VALUE_THRESHOLD', 'AI价值阈值'),
        ('ENABLE_INTELLIGENT_PROCESSING', '启用智能处理'),
    ]
    
    for var, desc in env_vars:
        value = os.getenv(var)
        status = f"✅ {value}" if value else "❌ 未设置"
        print(f"  {var}: {status} ({desc})")


def list_environments():
    """列出所有可用环境"""
    env_mgr = get_environment_manager()
    envs = env_mgr.list_environments()
    
    print("=== 可用环境 ===")
    current = env_mgr.current_environment.value
    
    for env_info in envs:
        name = env_info['name']
        display_name = env_info['display_name']
        encrypted = "🔒" if env_info['use_encryption'] else "🔓"
        debug = "🐛" if env_info['debug_enabled'] else "🚀"
        current_mark = " ← 当前" if name == current else ""
        
        print(f"  {name:12} | {display_name:12} | {encrypted} {debug} | {env_info['base_path']}{current_mark}")


def switch_environment(env_name: str, permanent: bool = False):
    """切换环境"""
    env_mgr = get_environment_manager()
    
    try:
        if permanent:
            print(f"永久切换到环境: {env_name}")
            env_mgr.permanently_switch_environment(Environment.from_string(env_name))
            print("✅ 永久切换完成，重启应用后生效")
        else:
            print(f"临时切换到环境: {env_name} (仅当前会话)")
            # 这里应该有临时切换的逻辑，但当前API有问题
            print("⚠️  临时切换功能需要修复")
            
    except Exception as e:
        print(f"❌ 切换失败: {e}")


def set_environment_variable(var_name: str, value: str):
    """设置环境变量"""
    print(f"设置环境变量: {var_name}={value}")
    
    # 对于用户shell，建议添加到配置文件
    shell = os.getenv('SHELL', '/bin/bash')
    
    if 'zsh' in shell:
        config_file = '~/.zshrc'
    elif 'bash' in shell:
        config_file = '~/.bashrc'
    else:
        config_file = '~/.profile'
    
    print(f"建议添加到 {config_file}:")
    print(f"export {var_name}='{value}'")
    
    # 当前会话设置
    os.environ[var_name] = value
    print(f"✅ 当前会话已设置")


def generate_ide_config(ide_type: str):
    """生成IDE配置文件"""
    env_mgr = get_environment_manager()
    config_mgr = get_config_manager()
    
    if ide_type.lower() == 'vscode':
        # VS Code配置
        config = {
            "python.defaultInterpreterPath": "./daemon/.venv/bin/python",
            "python.terminal.activateEnvironment": True,
            "terminal.integrated.env.osx": {
                "LINCH_MIND_ENVIRONMENT": env_mgr.current_environment.value,
                "OLLAMA_HOST": config_mgr.get_ollama_host(),
                "PYTHONPATH": "${workspaceFolder}/daemon"
            },
            "terminal.integrated.env.linux": {
                "LINCH_MIND_ENVIRONMENT": env_mgr.current_environment.value,
                "OLLAMA_HOST": config_mgr.get_ollama_host(),
                "PYTHONPATH": "${workspaceFolder}/daemon"
            }
        }
        
        vscode_dir = Path('.vscode')
        vscode_dir.mkdir(exist_ok=True)
        
        settings_file = vscode_dir / 'settings.json'
        import json
        with open(settings_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ VS Code配置已生成: {settings_file}")
        
    elif ide_type.lower() == 'pycharm':
        print("PyCharm配置:")
        print("1. 设置Python解释器: ./daemon/.venv/bin/python")
        print("2. 设置工作目录: ./daemon")
        print("3. 添加环境变量:")
        print(f"   LINCH_MIND_ENVIRONMENT={env_mgr.current_environment.value}")
        print(f"   OLLAMA_HOST={config_mgr.get_ollama_host()}")
        print("   PYTHONPATH=./daemon")
        
    else:
        print(f"❌ 不支持的IDE类型: {ide_type}")
        print("支持的IDE: vscode, pycharm")


def main():
    parser = argparse.ArgumentParser(description='Linch Mind环境管理工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 状态命令
    status_parser = subparsers.add_parser('status', help='显示当前环境状态')
    
    # 列表命令
    list_parser = subparsers.add_parser('list', help='列出所有环境')
    
    # 切换命令
    switch_parser = subparsers.add_parser('switch', help='切换环境')
    switch_parser.add_argument('environment', choices=['development', 'staging', 'production'])
    switch_parser.add_argument('--permanent', action='store_true', help='永久切换')
    
    # 环境变量命令
    env_parser = subparsers.add_parser('env', help='设置环境变量')
    env_parser.add_argument('variable', help='变量名')
    env_parser.add_argument('value', help='变量值')
    
    # IDE配置命令
    ide_parser = subparsers.add_parser('ide', help='生成IDE配置')
    ide_parser.add_argument('type', choices=['vscode', 'pycharm'], help='IDE类型')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        show_current_status()
    elif args.command == 'list':
        list_environments()
    elif args.command == 'switch':
        switch_environment(args.environment, args.permanent)
    elif args.command == 'env':
        set_environment_variable(args.variable, args.value)
    elif args.command == 'ide':
        generate_ide_config(args.type)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()