#!/usr/bin/env python3
"""
Linch Mind Connector Build System
多平台连接器构建和打包工具
"""

import json
import sys
import os
import shutil
import zipfile
import platform
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
CONNECTORS_DIR = ROOT_DIR / "connectors"
OFFICIAL_DIR = CONNECTORS_DIR / "official"
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"

class PlatformInfo:
    """平台信息管理"""
    
    @staticmethod
    def get_current_platform() -> str:
        """获取当前平台标识"""
        system = platform.system().lower()
        if system == "windows":
            return "windows"
        elif system == "darwin":
            return "macos"
        elif system == "linux":
            return "linux"
        else:
            return "unknown"
    
    @staticmethod
    def get_executable_suffix(target_platform: str = None) -> str:
        """获取可执行文件后缀"""
        if target_platform is None:
            target_platform = PlatformInfo.get_current_platform()
        
        if target_platform == "windows":
            return ".exe"
        elif target_platform == "macos":
            return "-macos"
        else:
            return "-linux"
    
    @staticmethod
    def get_supported_platforms() -> List[str]:
        """获取支持的平台列表"""
        return ["windows", "macos", "linux"]

class ConnectorBuilder:
    """连接器构建器"""
    
    def __init__(self):
        self.build_dir = BUILD_DIR
        self.dist_dir = DIST_DIR
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保构建目录存在"""
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        (self.dist_dir / "connectors").mkdir(exist_ok=True)
    
    def discover_connectors(self) -> List[Dict]:
        """发现所有可构建的连接器"""
        connectors = []
        
        if not OFFICIAL_DIR.exists():
            logger.warning(f"Official connectors directory not found: {OFFICIAL_DIR}")
            return connectors
        
        for connector_dir in OFFICIAL_DIR.iterdir():
            if not connector_dir.is_dir() or connector_dir.name.startswith('.'):
                continue
            
            config_file = connector_dir / "connector.json"
            main_file = connector_dir / "main.py"
            
            if not config_file.exists() or not main_file.exists():
                logger.warning(f"Skipping {connector_dir.name}: missing required files")
                continue
            
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                connector_info = {
                    "id": config["id"],
                    "name": config["name"],
                    "version": config["version"],
                    "description": config["description"],
                    "path": connector_dir,
                    "config": config
                }
                
                connectors.append(connector_info)
                
            except Exception as e:
                logger.error(f"Failed to load config for {connector_dir.name}: {e}")
        
        return sorted(connectors, key=lambda x: x["id"])
    
    def install_dependencies(self, connector_path: Path) -> bool:
        """安装连接器依赖"""
        requirements_file = connector_path / "requirements.txt"
        
        if not requirements_file.exists():
            logger.info(f"No requirements.txt found for {connector_path.name}")
            return True
        
        logger.info(f"Installing dependencies for {connector_path.name}...")
        
        try:
            # 创建临时虚拟环境或直接安装
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True, capture_output=True, text=True)
            
            logger.info("✅ Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
            return False
    
    def build_connector(self, connector: Dict, target_platform: str = None) -> bool:
        """构建单个连接器"""
        if target_platform is None:
            target_platform = PlatformInfo.get_current_platform()
        
        connector_id = connector["id"]
        connector_path = connector["path"]
        
        logger.info(f"Building {connector_id} for {target_platform}...")
        
        # 安装依赖
        if not self.install_dependencies(connector_path):
            return False
        
        # 构建可执行文件
        executable_suffix = PlatformInfo.get_executable_suffix(target_platform)
        output_name = f"main{executable_suffix}"
        
        build_work_dir = self.build_dir / connector_id
        build_work_dir.mkdir(exist_ok=True)
        
        try:
            # 使用PyInstaller构建
            pyinstaller_args = [
                "pyinstaller",
                "--onefile",
                "--name", output_name.replace(executable_suffix, ""),
                "--distpath", str(connector_path),
                "--workpath", str(build_work_dir),
                "--specpath", str(build_work_dir),
                str(connector_path / "main.py")
            ]
            
            # 添加平台特定选项
            if target_platform == "windows":
                pyinstaller_args.extend(["--noconsole"])
            
            subprocess.run(pyinstaller_args, check=True, capture_output=True, text=True, cwd=str(connector_path))
            
            # 验证输出文件
            output_file = connector_path / output_name
            if not output_file.exists():
                logger.error(f"Build failed: {output_name} not found")
                return False
            
            # 获取文件大小
            file_size = output_file.stat().st_size
            size_mb = file_size / (1024 * 1024)
            
            logger.info(f"✅ Built {output_name} ({size_mb:.2f} MB)")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"PyInstaller build failed: {e}")
            if e.stdout:
                logger.error(f"stdout: {e.stdout}")
            if e.stderr:
                logger.error(f"stderr: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Unexpected build error: {e}")
            return False
    
    def package_connector(self, connector: Dict, target_platform: str = None) -> Optional[Path]:
        """打包连接器"""
        if target_platform is None:
            target_platform = PlatformInfo.get_current_platform()
        
        connector_id = connector["id"]
        connector_path = connector["path"]
        version = connector["version"]
        
        logger.info(f"Packaging {connector_id} v{version} for {target_platform}...")
        
        # 确定文件名
        executable_suffix = PlatformInfo.get_executable_suffix(target_platform)
        executable_name = f"main{executable_suffix}"
        package_name = f"{connector_id}-{version}-{target_platform}"
        
        # 创建包目录
        package_dir = self.dist_dir / "connectors" / package_name
        if package_dir.exists():
            shutil.rmtree(package_dir)
        package_dir.mkdir(parents=True)
        
        try:
            # 复制文件
            files_to_copy = [
                (connector_path / executable_name, package_dir / executable_name),
                (connector_path / "connector.json", package_dir / "connector.json"),
                (connector_path / "README.md", package_dir / "README.md")
            ]
            
            for src, dst in files_to_copy:
                if src.exists():
                    shutil.copy2(src, dst)
                    logger.debug(f"Copied {src.name}")
                else:
                    logger.warning(f"File not found: {src}")
            
            # 创建安装脚本
            self._create_install_script(package_dir, connector, target_platform)
            
            # 创建ZIP包
            zip_path = self.dist_dir / f"{package_name}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in package_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = str(file_path.relative_to(package_dir))
                        zipf.write(file_path, arcname)
            
            # 计算ZIP文件大小
            zip_size = zip_path.stat().st_size
            size_mb = zip_size / (1024 * 1024)
            
            logger.info(f"✅ Created package: {zip_path.name} ({size_mb:.2f} MB)")
            
            # 清理临时目录
            shutil.rmtree(package_dir)
            
            return zip_path
            
        except Exception as e:
            logger.error(f"Packaging failed: {e}")
            return None
    
    def _create_install_script(self, package_dir: Path, connector: Dict, target_platform: str):
        """创建安装脚本"""
        connector_id = connector["id"]
        
        if target_platform == "windows":
            # Windows批处理脚本
            script_content = f"""@echo off
echo Installing {connector['name']} ({connector_id})...
copy main.exe "%LINCH_MIND_HOME%\\connectors\\{connector_id}\\"
copy connector.json "%LINCH_MIND_HOME%\\connectors\\{connector_id}\\"
echo Installation complete!
pause
"""
            script_path = package_dir / "install.bat"
        else:
            # Unix shell脚本
            script_content = f"""#!/bin/bash
echo "Installing {connector['name']} ({connector_id})..."
mkdir -p "$LINCH_MIND_HOME/connectors/{connector_id}"
cp main* "$LINCH_MIND_HOME/connectors/{connector_id}/"
cp connector.json "$LINCH_MIND_HOME/connectors/{connector_id}/"
chmod +x "$LINCH_MIND_HOME/connectors/{connector_id}/main*"
echo "Installation complete!"
"""
            script_path = package_dir / "install.sh"
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 设置执行权限（Unix系统）
        if target_platform != "windows":
            script_path.chmod(0o755)
    
    def build_all(self, target_platforms: List[str] = None) -> Dict[str, Dict[str, bool]]:
        """构建所有连接器"""
        if target_platforms is None:
            target_platforms = [PlatformInfo.get_current_platform()]
        
        connectors = self.discover_connectors()
        if not connectors:
            logger.warning("No connectors found to build")
            return {}
        
        results = {}
        
        for connector in connectors:
            connector_id = connector["id"]
            results[connector_id] = {}
            
            for platform in target_platforms:
                logger.info(f"\n--- Building {connector_id} for {platform} ---")
                success = self.build_connector(connector, platform)
                results[connector_id][platform] = success
                
                if success:
                    # 尝试打包
                    package_path = self.package_connector(connector, platform)
                    if package_path:
                        results[connector_id][f"{platform}_package"] = str(package_path)
        
        return results
    
    def clean_build_artifacts(self):
        """清理构建产物"""
        logger.info("Cleaning build artifacts...")
        
        # 清理全局构建目录
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            self.build_dir.mkdir()
        
        # 清理连接器目录中的构建产物
        for connector_dir in OFFICIAL_DIR.iterdir():
            if not connector_dir.is_dir():
                continue
            
            # 清理PyInstaller产物
            for pattern in ["*.exe", "*-macos", "*-linux", "build", "*.spec"]:
                for item in connector_dir.glob(pattern):
                    if item.is_file():
                        item.unlink()
                        logger.debug(f"Removed {item}")
                    elif item.is_dir():
                        shutil.rmtree(item)
                        logger.debug(f"Removed directory {item}")
        
        logger.info("✅ Build artifacts cleaned")

class ConnectorPackageManager:
    """连接器包管理器"""
    
    def __init__(self):
        self.dist_dir = DIST_DIR
    
    def list_packages(self) -> List[Dict]:
        """列出所有构建的包"""
        packages = []
        
        if not self.dist_dir.exists():
            return packages
        
        for zip_file in self.dist_dir.glob("*.zip"):
            try:
                # 解析文件名: connector-version-platform.zip
                name_parts = zip_file.stem.split('-')
                if len(name_parts) >= 3:
                    connector_id = name_parts[0]
                    version = name_parts[1]
                    platform = name_parts[2]
                    
                    file_size = zip_file.stat().st_size
                    modified_time = datetime.fromtimestamp(zip_file.stat().st_mtime)
                    
                    packages.append({
                        "connector_id": connector_id,
                        "version": version,
                        "platform": platform,
                        "file_path": zip_file,
                        "file_size": file_size,
                        "modified_time": modified_time.isoformat()
                    })
            except Exception as e:
                logger.warning(f"Failed to parse package {zip_file.name}: {e}")
        
        return sorted(packages, key=lambda x: (x["connector_id"], x["version"], x["platform"]))
    
    def print_packages(self):
        """打印包列表"""
        packages = self.list_packages()
        
        if not packages:
            print("No packages found.")
            return
        
        print(f"\n📦 Found {len(packages)} packages:\n")
        
        current_connector = None
        for package in packages:
            if package["connector_id"] != current_connector:
                current_connector = package["connector_id"]
                print(f"🔌 {current_connector}")
            
            size_mb = package["file_size"] / (1024 * 1024)
            print(f"   {package['version']}-{package['platform']}: {size_mb:.2f} MB ({package['modified_time'][:19]})")
        
        print()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Linch Mind Connector Build System")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # build命令
    build_parser = subparsers.add_parser("build", help="Build specific connector")
    build_parser.add_argument("connector", help="Connector ID to build")
    build_parser.add_argument("--platform", choices=PlatformInfo.get_supported_platforms(), 
                             help="Target platform (default: current)")
    
    # build-all命令
    build_all_parser = subparsers.add_parser("build-all", help="Build all connectors")
    build_all_parser.add_argument("--platforms", nargs="+", 
                                 choices=PlatformInfo.get_supported_platforms(),
                                 help="Target platforms (default: current)")
    
    # package命令
    package_parser = subparsers.add_parser("package", help="Package built connectors")
    package_parser.add_argument("connector", nargs="?", help="Specific connector to package")
    package_parser.add_argument("--platform", choices=PlatformInfo.get_supported_platforms(),
                               help="Target platform (default: current)")
    
    # list命令
    list_parser = subparsers.add_parser("list", help="List built packages")
    
    # clean命令
    clean_parser = subparsers.add_parser("clean", help="Clean build artifacts")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        builder = ConnectorBuilder()
        
        if args.command == "build":
            # 构建指定连接器
            connectors = builder.discover_connectors()
            target_connector = next((c for c in connectors if c["id"] == args.connector), None)
            
            if not target_connector:
                logger.error(f"Connector not found: {args.connector}")
                return 1
            
            success = builder.build_connector(target_connector, args.platform)
            return 0 if success else 1
        
        elif args.command == "build-all":
            # 构建所有连接器
            platforms = args.platforms or [PlatformInfo.get_current_platform()]
            results = builder.build_all(platforms)
            
            # 统计结果
            total_builds = sum(len(platform_results) for platform_results in results.values())
            successful_builds = sum(1 for platform_results in results.values() 
                                  for success in platform_results.values() if success is True)
            
            logger.info(f"\n📊 Build Summary: {successful_builds}/{total_builds} successful")
            
            # 显示失败的构建
            failed_builds = []
            for connector_id, platform_results in results.items():
                for platform, success in platform_results.items():
                    if success is False:
                        failed_builds.append(f"{connector_id}-{platform}")
            
            if failed_builds:
                logger.warning(f"Failed builds: {', '.join(failed_builds)}")
                return 1
            
            return 0
        
        elif args.command == "package":
            # 打包连接器
            if args.connector:
                connectors = builder.discover_connectors()
                target_connector = next((c for c in connectors if c["id"] == args.connector), None)
                
                if not target_connector:
                    logger.error(f"Connector not found: {args.connector}")
                    return 1
                
                package_path = builder.package_connector(target_connector, args.platform)
                return 0 if package_path else 1
            else:
                # 打包所有已构建的连接器
                connectors = builder.discover_connectors()
                platform = args.platform or PlatformInfo.get_current_platform()
                
                success_count = 0
                for connector in connectors:
                    package_path = builder.package_connector(connector, platform)
                    if package_path:
                        success_count += 1
                
                logger.info(f"📦 Packaged {success_count}/{len(connectors)} connectors")
                return 0
        
        elif args.command == "list":
            # 列出构建的包
            manager = ConnectorPackageManager()
            manager.print_packages()
            return 0
        
        elif args.command == "clean":
            # 清理构建产物
            builder.clean_build_artifacts()
            return 0
        
        else:
            parser.print_help()
            return 1
    
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())