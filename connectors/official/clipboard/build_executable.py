#!/usr/bin/env python3
"""
剪贴板连接器打包脚本
使用PyInstaller将连接器打包为独立可执行文件
Session 4 部署优化
"""

import PyInstaller.__main__
import sys
from pathlib import Path

def build_clipboard_connector():
    """打包剪贴板连接器"""
    
    connector_dir = Path(__file__).parent
    main_script = connector_dir / "main.py"
    
    # PyInstaller参数
    pyinstaller_args = [
        str(main_script),
        '--onefile',  # 打包为单一可执行文件
        '--name=clipboard-connector',
        '--distpath=../dist',  # 输出到connectors/dist目录
        '--workpath=../build',  # 临时文件目录
        '--specpath=.',
        '--clean',
        '--noconfirm',
        # 隐藏控制台窗口 (可选，调试时注释掉)
        # '--windowed',
        # 添加必要的Python包
        '--hidden-import=pyperclip',
        '--hidden-import=httpx',
        '--hidden-import=asyncio',
    ]
    
    print("🚀 开始打包剪贴板连接器...")
    print(f"📁 源文件: {main_script}")
    print(f"📦 输出目录: {connector_dir.parent / 'dist'}")
    
    try:
        PyInstaller.__main__.run(pyinstaller_args)
        print("✅ 剪贴板连接器打包完成!")
        
        # 检查输出文件
        executable_path = connector_dir.parent / "dist" / "clipboard-connector"
        if executable_path.exists():
            print(f"📦 可执行文件: {executable_path}")
            print(f"📏 文件大小: {executable_path.stat().st_size / 1024 / 1024:.1f} MB")
        else:
            print("❌ 未找到输出文件")
            
    except Exception as e:
        print(f"❌ 打包失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_clipboard_connector()