#!/usr/bin/env python3
"""
连接器批量打包脚本
将所有连接器打包为独立可执行文件，解决用户部署问题
Session 4 部署解决方案
"""

import subprocess
import sys
from pathlib import Path

def install_pyinstaller():
    """安装PyInstaller依赖"""
    try:
        import PyInstaller
        print("✅ PyInstaller 已安装")
        return True
    except ImportError:
        print("📦 安装 PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller 安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ PyInstaller 安装失败: {e}")
            return False

def build_connector(connector_name: str) -> bool:
    """打包指定连接器"""
    connector_dir = Path(__file__).parent / connector_name
    build_script = connector_dir / "build_executable.py"
    
    if not build_script.exists():
        print(f"❌ 打包脚本不存在: {build_script}")
        return False
    
    print(f"\n🚀 打包连接器: {connector_name}")
    try:
        subprocess.check_call([sys.executable, str(build_script)], cwd=connector_dir)
        print(f"✅ {connector_name} 连接器打包完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {connector_name} 连接器打包失败: {e}")
        return False

def main():
    """主函数"""
    print("🏗️  Linch Mind 连接器批量打包工具")
    print("=" * 50)
    
    # 检查并安装PyInstaller
    if not install_pyinstaller():
        sys.exit(1)
    
    # 要打包的连接器列表
    connectors = ["filesystem", "clipboard"]
    
    # 清理之前的构建结果
    dist_dir = Path(__file__).parent / "dist"
    build_dir = Path(__file__).parent / "build"
    
    if dist_dir.exists():
        import shutil
        shutil.rmtree(dist_dir)
        print("🧹 清理旧的构建结果")
    
    # 批量打包
    successful_builds = []
    failed_builds = []
    
    for connector in connectors:
        if build_connector(connector):
            successful_builds.append(connector)
        else:
            failed_builds.append(connector)
    
    # 构建报告
    print("\n" + "=" * 50)
    print("📊 构建结果报告:")
    
    if successful_builds:
        print(f"✅ 成功打包 ({len(successful_builds)}): {', '.join(successful_builds)}")
        
        # 显示可执行文件信息
        if dist_dir.exists():
            print(f"\n📦 可执行文件位置: {dist_dir}")
            for exe_file in dist_dir.glob("*"):
                if exe_file.is_file():
                    size_mb = exe_file.stat().st_size / 1024 / 1024
                    print(f"   - {exe_file.name}: {size_mb:.1f} MB")
    
    if failed_builds:
        print(f"❌ 失败 ({len(failed_builds)}): {', '.join(failed_builds)}")
    
    print("\n💡 部署说明:")
    print("   1. 将 dist/ 目录中的可执行文件复制到应用包中")
    print("   2. 连接器管理器会自动检测并使用可执行文件")
    print("   3. 用户无需安装Python环境")
    
    return len(failed_builds) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)