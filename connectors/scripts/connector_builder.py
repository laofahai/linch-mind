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
import zipfile
import shutil
from pathlib import Path


def build_connector(connector_path: str, output_dir: str = "dist", create_zip: bool = True) -> bool:
    """
    构建单个连接器
    
    Args:
        connector_path: 连接器目录路径 (如 official/filesystem)
        output_dir: 输出目录
        create_zip: 是否创建ZIP包
    
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
        # 构建参数 - 优化文件大小
        args = [
            str(main_script.name),
            '--onefile',
            f'--name={connector_name}-connector',
            f'--distpath=../../{output_dir}',
            '--clean',
            '--noconfirm',
            '--strip',  # 去除调试信息
            '--optimize=2',  # Python字节码优化
            '--noupx',  # 禁用UPX压缩以避免兼容性问题
            
            # 必要的隐藏导入
            '--hidden-import=watchdog',
            '--hidden-import=httpx', 
            '--hidden-import=pyperclip',
            
            # 排除不必要的模块以减小文件大小
            '--exclude-module=PIL',
            '--exclude-module=matplotlib',
            '--exclude-module=numpy',
            '--exclude-module=pandas',
            '--exclude-module=scipy',
            '--exclude-module=sklearn',
            '--exclude-module=tensorflow',
            '--exclude-module=torch',
            '--exclude-module=cv2',
            '--exclude-module=tkinter',
            '--exclude-module=PyQt5',
            '--exclude-module=PyQt6',
            '--exclude-module=PySide2',
            '--exclude-module=PySide6',
            '--exclude-module=wx',
            '--exclude-module=kivy',
            '--exclude-module=django',
            '--exclude-module=flask',
            '--exclude-module=fastapi',
            '--exclude-module=jupyter',
            '--exclude-module=ipython',
            '--exclude-module=notebook',
            '--exclude-module=pytest',
            '--exclude-module=unittest',
            '--exclude-module=doctest',
            '--exclude-module=pdb',
            '--exclude-module=cProfile',
            '--exclude-module=profile',
            
            # 排除测试和开发工具
            '--exclude-module=test',
            '--exclude-module=tests',
            '--exclude-module=distutils',
            '--exclude-module=setuptools',
            '--exclude-module=pip',
            '--exclude-module=wheel',
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
            
            # 创建ZIP包
            if create_zip:
                # 获取原始配置文件路径（相对于当前工作目录）
                original_config = Path(f"../../{connector_path}/connector.json")
                success = create_connector_zip(
                    connector_name, 
                    original_config, 
                    built_files[0], 
                    output_path
                )
                if not success:
                    print(f"⚠️ ZIP creation failed for {connector_name}, but binary build succeeded")
            
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


def create_connector_zip(connector_name: str, config_file: Path, executable_file: Path, output_dir: Path) -> bool:
    """
    创建连接器ZIP包，包含可执行文件和配置文件
    
    Args:
        connector_name: 连接器名称
        config_file: connector.json文件路径
        executable_file: 可执行文件路径
        output_dir: 输出目录
    
    Returns:
        创建是否成功
    """
    try:
        zip_filename = f"{connector_name}-connector.zip"
        zip_path = output_dir / zip_filename
        
        print(f"📦 Creating ZIP package: {zip_filename}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 添加可执行文件
            zipf.write(executable_file, executable_file.name)
            print(f"   ✅ Added: {executable_file.name}")
            
            # 添加connector.json配置文件
            zipf.write(config_file, 'connector.json')
            print(f"   ✅ Added: connector.json")
            
            # 检查是否有README文件
            readme_file = config_file.parent / 'README.md'
            if readme_file.exists():
                zipf.write(readme_file, 'README.md')
                print(f"   ✅ Added: README.md")
        
        # 检查ZIP文件大小
        zip_size_mb = zip_path.stat().st_size / 1024 / 1024
        print(f"📋 ZIP package created: {zip_filename} ({zip_size_mb:.1f} MB)")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create ZIP package: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='连接器构建工具')
    parser.add_argument('connector_path', help='连接器路径 (如 official/filesystem)')
    parser.add_argument('--output', default='dist', help='输出目录')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    parser.add_argument('--no-zip', action='store_true', help='不创建ZIP包')
    
    args = parser.parse_args()
    
    if not Path(args.connector_path).exists():
        print(f"❌ 连接器目录不存在: {args.connector_path}")
        sys.exit(1)
    
    success = build_connector(args.connector_path, args.output, create_zip=not args.no_zip)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()