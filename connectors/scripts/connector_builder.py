#!/usr/bin/env python3
"""
连接器构建脚本
用于GitHub Actions和本地开发
"""

import PyInstaller.__main__
import json
import sys
import os
import argparse
from pathlib import Path


def build_connector(connector_path: str, output_dir: str = "dist") -> bool:
    """
    构建单个连接器
    
    Args:
        connector_path: 连接器目录路径 (如 official/filesystem)
        output_dir: 输出目录
    
    Returns:
        构建是否成功
    """
    connector_dir = Path(connector_path)
    config_file = connector_dir / 'connector.json'
    main_script = connector_dir / 'main.py'
    
    if not config_file.exists():
        print(f"❌ {config_file} not found")
        return False
    
    if not main_script.exists():
        print(f"❌ {main_script} not found")
        return False
    
    # 读取配置
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    connector_name = config['id']
    print(f"🚀 Building connector: {connector_name}")
    
    # 切换到连接器目录
    original_dir = os.getcwd()
    os.chdir(connector_dir)
    
    try:
        # 构建参数
        args = [
            str(main_script.name),
            '--onefile',
            f'--name={connector_name}-connector',
            f'--distpath=../../{output_dir}',
            '--clean',
            '--noconfirm',
            '--hidden-import=watchdog',
            '--hidden-import=httpx', 
            '--hidden-import=pyperclip',
        ]
        
        print(f"🔧 PyInstaller args: {args}")
        PyInstaller.__main__.run(args)
        
        # 检查输出文件
        output_path = Path(f"../../{output_dir}")
        built_files = list(output_path.glob(f"{connector_name}-connector*"))
        
        if built_files:
            for built_file in built_files:
                size_mb = built_file.stat().st_size / 1024 / 1024
                print(f"📦 Built: {built_file.name} ({size_mb:.1f} MB)")
            print(f"✅ Successfully built {connector_name}")
            return True
        else:
            print(f"❌ No output files found for {connector_name}")
            return False
            
    except Exception as e:
        print(f"❌ Build failed for {connector_name}: {e}")
        return False
    finally:
        os.chdir(original_dir)


def main():
    parser = argparse.ArgumentParser(description='连接器构建工具')
    parser.add_argument('connector_path', help='连接器路径 (如 official/filesystem)')
    parser.add_argument('--output', default='dist', help='输出目录')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    if not Path(args.connector_path).exists():
        print(f"❌ 连接器目录不存在: {args.connector_path}")
        sys.exit(1)
    
    success = build_connector(args.connector_path, args.output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()