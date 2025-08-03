#!/usr/bin/env python3
"""
连接器安装器服务
负责从远程注册表下载、验证、安装连接器
"""

import asyncio
import hashlib
import json
import logging
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx

from config.core_config import get_core_config
from models.database_models import ConnectorType, ConnectorInstance
from services.connectors.lifecycle_manager import ConnectorLifecycleManager

logger = logging.getLogger(__name__)

class ConnectorInstaller:
    """连接器安装器"""
    
    def __init__(self, lifecycle_manager: ConnectorLifecycleManager):
        self.lifecycle_manager = lifecycle_manager
        
        # Session V60: 使用统一配置系统，消除硬编码
        core_config = get_core_config()
        
        self.registry_url = core_config.config.connectors.registry_url
        self.connectors_dir = Path(core_config.config.connectors.install_dir)
        self.connectors_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"连接器安装器初始化 - Registry: {self.registry_url}, Dir: {self.connectors_dir}")
    
    async def list_available_connectors(self) -> Dict[str, Any]:
        """列出注册表中可用的连接器"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.registry_url}/connectors")
                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception(f"Registry request failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to fetch connector list: {e}")
            return {"connectors": [], "total": 0, "error": str(e)}
    
    async def get_connector_info(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取特定连接器的详细信息"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.registry_url}/connectors/{connector_id}")
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                else:
                    raise Exception(f"Registry request failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to get connector info for {connector_id}: {e}")
            return None
    
    async def install_connector(self, connector_id: str, version: str = "latest") -> Dict[str, Any]:
        """安装连接器"""
        logger.info(f"开始安装连接器: {connector_id} v{version}")
        
        try:
            # 1. 获取连接器信息
            connector_info = await self.get_connector_info(connector_id)
            if not connector_info:
                return {"success": False, "error": f"Connector {connector_id} not found"}
            
            # 解析版本
            if version == "latest":
                version = connector_info["latest"]
            
            if version not in connector_info["versions"]:
                return {"success": False, "error": f"Version {version} not found"}
            
            version_info = connector_info["versions"][version]
            
            # 2. 检查是否已安装
            existing_connector = await self.lifecycle_manager.get_connector_type(connector_id)
            if existing_connector:
                return {"success": False, "error": f"Connector {connector_id} is already installed"}
            
            # 3. 下载连接器包
            download_result = await self._download_connector(connector_id, version, version_info)
            if not download_result["success"]:
                return download_result
            
            package_path = download_result["package_path"]
            
            # 4. 验证包
            validation_result = self._validate_package(package_path, version_info)
            if not validation_result["valid"]:
                package_path.unlink()  # 删除无效包
                return {"success": False, "error": validation_result["error"]}
            
            # 5. 解压和安装
            install_result = await self._extract_and_install(package_path, connector_info, version_info)
            
            # 6. 清理临时文件
            if package_path.exists():
                package_path.unlink()
            
            if install_result["success"]:
                logger.info(f"✅ 连接器 {connector_id} v{version} 安装成功")
                
                # 7. 注册到生命周期管理器
                await self._register_connector_type(connector_info, version)
                
            return install_result
            
        except Exception as e:
            logger.error(f"安装连接器失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def uninstall_connector(self, connector_id: str, force: bool = False) -> Dict[str, Any]:
        """卸载连接器"""
        logger.info(f"开始卸载连接器: {connector_id}")
        
        try:
            # 1. 检查连接器是否存在
            connector_type = await self.lifecycle_manager.get_connector_type(connector_id)
            if not connector_type:
                return {"success": False, "error": f"Connector {connector_id} is not installed"}
            
            # 2. 检查连接器是否正在运行
            is_running = await self.lifecycle_manager.is_connector_running(connector_id)
            
            if is_running and not force:
                return {
                    "success": False, 
                    "error": f"Connector {connector_id} is currently running. Use force=True to stop it."
                }
            
            # 3. 停止连接器（如果正在运行）
            if is_running:
                await self.lifecycle_manager.stop_instance(connector_id)
            
            # 4. 删除连接器文件
            connector_dir = self.connectors_dir / connector_id
            if connector_dir.exists():
                shutil.rmtree(connector_dir)
            
            # 5. 从配置中删除
            await self.lifecycle_manager.unregister_connector_type(connector_id)
            
            logger.info(f"✅ 连接器 {connector_id} 卸载成功")
            return {"success": True, "message": f"Connector {connector_id} uninstalled successfully"}
            
        except Exception as e:
            logger.error(f"卸载连接器失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_connector(self, connector_id: str, target_version: str = "latest") -> Dict[str, Any]:
        """更新连接器"""
        logger.info(f"开始更新连接器: {connector_id} -> {target_version}")
        
        try:
            # 1. 检查当前版本
            connector_type = await self.lifecycle_manager.get_connector_type(connector_id)
            if not connector_type:
                return {"success": False, "error": f"Connector {connector_id} is not installed"}
            
            current_version = connector_type.version
            
            # 2. 获取目标版本信息
            connector_info = await self.get_connector_info(connector_id)
            if not connector_info:
                return {"success": False, "error": f"Connector {connector_id} not found in registry"}
            
            if target_version == "latest":
                target_version = connector_info["latest"]
            
            if target_version == current_version:
                return {"success": False, "error": f"Already on version {current_version}"}
            
            # 3. 备份当前版本
            backup_result = await self._backup_connector(connector_id, current_version)
            if not backup_result["success"]:
                return backup_result
            
            # 4. 卸载当前版本
            uninstall_result = await self.uninstall_connector(connector_id, force=True)
            if not uninstall_result["success"]:
                # 恢复备份
                await self._restore_connector(connector_id, current_version)
                return uninstall_result
            
            # 5. 安装新版本
            install_result = await self.install_connector(connector_id, target_version)
            if not install_result["success"]:
                # 恢复备份
                await self._restore_connector(connector_id, current_version)
                return install_result
            
            # 6. 删除备份
            await self._cleanup_backup(connector_id, current_version)
            
            logger.info(f"✅ 连接器 {connector_id} 更新成功: {current_version} -> {target_version}")
            return {
                "success": True, 
                "message": f"Connector {connector_id} updated from {current_version} to {target_version}"
            }
            
        except Exception as e:
            logger.error(f"更新连接器失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def _download_connector(self, connector_id: str, version: str, version_info: Dict[str, Any]) -> Dict[str, Any]:
        """下载连接器包"""
        download_url = version_info["download_url"]
        expected_size = version_info.get("size", 0)
        
        logger.info(f"下载连接器包: {download_url}")
        
        try:
            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            package_path = Path(temp_file.name)
            
            async with httpx.AsyncClient(timeout=300.0) as client:  # 5分钟超时
                async with client.stream('GET', download_url) as response:
                    if response.status_code != 200:
                        return {"success": False, "error": f"Download failed: {response.status_code}"}
                    
                    downloaded_size = 0
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        temp_file.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 简单的下载进度日志
                        if downloaded_size % (1024 * 1024) == 0:  # 每MB
                            logger.info(f"已下载: {downloaded_size // (1024 * 1024)}MB")
            
            temp_file.close()
            
            # 验证文件大小
            actual_size = package_path.stat().st_size
            if expected_size > 0 and actual_size != expected_size:
                package_path.unlink()
                return {
                    "success": False, 
                    "error": f"Size mismatch: expected {expected_size}, got {actual_size}"
                }
            
            logger.info(f"下载完成: {actual_size} bytes")
            return {"success": True, "package_path": package_path}
            
        except Exception as e:
            if package_path.exists():
                package_path.unlink()
            return {"success": False, "error": f"Download error: {e}"}
    
    def _validate_package(self, package_path: Path, version_info: Dict[str, Any]) -> Dict[str, Any]:
        """验证连接器包"""
        try:
            # 验证校验和
            expected_checksum = version_info.get("checksum")
            if expected_checksum:
                actual_checksum = self._calculate_checksum(package_path)
                if actual_checksum != expected_checksum:
                    return {
                        "valid": False,
                        "error": f"Checksum mismatch: expected {expected_checksum}, got {actual_checksum}"
                    }
            
            # 验证ZIP结构
            with zipfile.ZipFile(package_path, 'r') as zf:
                files = zf.namelist()
                
                # 检查必需文件
                if 'connector.json' not in files:
                    return {"valid": False, "error": "Missing connector.json"}
                
                # 验证connector.json
                with zf.open('connector.json') as f:
                    connector_info = json.load(f)
                
                required_fields = ['id', 'name', 'version', 'entry']
                for field in required_fields:
                    if field not in connector_info:
                        return {"valid": False, "error": f"Missing field in connector.json: {field}"}
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {e}"}
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """计算文件SHA256校验和"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return f"sha256:{sha256_hash.hexdigest()}"
    
    async def _extract_and_install(self, package_path: Path, connector_info: Dict[str, Any], version_info: Dict[str, Any]) -> Dict[str, Any]:
        """解压和安装连接器"""
        connector_id = connector_info["id"]
        install_dir = self.connectors_dir / connector_id
        
        try:
            # 创建安装目录
            install_dir.mkdir(parents=True, exist_ok=True)
            
            # 解压包
            with zipfile.ZipFile(package_path, 'r') as zf:
                zf.extractall(install_dir)
            
            logger.info(f"连接器已解压到: {install_dir}")
            
            # 验证解压后的文件
            connector_json_path = install_dir / "connector.json"
            if not connector_json_path.exists():
                shutil.rmtree(install_dir)
                return {"success": False, "error": "connector.json not found after extraction"}
            
            # 设置可执行权限（Unix系统）
            for file_path in install_dir.rglob("*"):
                if file_path.is_file() and (file_path.suffix in ['.py', ''] or 'main' in file_path.name):
                    file_path.chmod(0o755)
            
            return {"success": True, "install_dir": str(install_dir)}
            
        except Exception as e:
            if install_dir.exists():
                shutil.rmtree(install_dir)
            return {"success": False, "error": f"Installation error: {e}"}
    
    async def _register_connector_type(self, connector_info: Dict[str, Any], version: str):
        """向生命周期管理器注册连接器类型"""
        connector_id = connector_info["id"]
        install_dir = self.connectors_dir / connector_id
        
        # 读取connector.json
        with open(install_dir / "connector.json", 'r', encoding='utf-8') as f:
            connector_config = json.load(f)
        
        # 创建ConnectorType
        connector_type = ConnectorType(
            id=connector_id,
            name=connector_info["name"],
            description=connector_info["description"],
            version=version,
            author=connector_info.get("author", "Unknown"),
            install_path=str(install_dir),
            entry_point=connector_config["entry"],
            config_schema=connector_config.get("config_schema", {}),
            permissions=connector_config.get("permissions", []),
            capabilities=connector_config.get("capabilities", {}),
            created_at=datetime.utcnow(),
            is_enabled=True
        )
        
        # 注册到生命周期管理器
        await self.lifecycle_manager.register_connector_type(connector_type)
    
    async def _backup_connector(self, connector_id: str, version: str) -> Dict[str, Any]:
        """备份连接器"""
        # 简化版：暂时跳过备份
        logger.info(f"备份连接器 {connector_id} v{version} (暂时跳过)")
        return {"success": True}
    
    async def _restore_connector(self, connector_id: str, version: str) -> Dict[str, Any]:
        """恢复连接器"""
        # 简化版：暂时跳过恢复
        logger.info(f"恢复连接器 {connector_id} v{version} (暂时跳过)")
        return {"success": True}
    
    async def _cleanup_backup(self, connector_id: str, version: str):
        """清理备份"""
        # 简化版：暂时跳过清理
        logger.info(f"清理备份 {connector_id} v{version} (暂时跳过)")
        pass