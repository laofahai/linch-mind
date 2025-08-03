#!/usr/bin/env python3
"""
简单的连接器注册表HTTP服务
用于开发和测试连接器远程安装功能
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import zipfile
import hashlib
from datetime import datetime
import tempfile
import shutil

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

app = FastAPI(
    title="Linch Mind Connector Registry",
    description="Simple connector registry for development",
    version="1.0.0",
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置
REGISTRY_FILE = project_root / "connectors" / "registry.json"
PACKAGES_DIR = project_root / "connectors" / "packages"
PACKAGES_DIR.mkdir(exist_ok=True)


class RegistryManager:
    """注册表管理器"""

    def __init__(self):
        self.registry_file = REGISTRY_FILE
        self.packages_dir = PACKAGES_DIR

    def load_registry(self) -> Dict[str, Any]:
        """加载注册表数据"""
        if not self.registry_file.exists():
            return self._create_empty_registry()

        with open(self.registry_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_registry(self, data: Dict[str, Any]):
        """保存注册表数据"""
        data["registry"]["updated_at"] = datetime.utcnow().isoformat() + "Z"
        data["stats"]["last_updated"] = data["registry"]["updated_at"]

        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _create_empty_registry(self) -> Dict[str, Any]:
        """创建空的注册表"""
        return {
            "registry": {
                "name": "Linch Mind Development Registry",
                "version": "1.0.0",
                "api_version": "v1",
                "base_url": "http://localhost:8001/v1",
                "updated_at": datetime.utcnow().isoformat() + "Z",
            },
            "connectors": {},
            "stats": {
                "total_connectors": 0,
                "total_downloads": 0,
                "last_updated": datetime.utcnow().isoformat() + "Z",
            },
        }

    def get_connector_info(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取连接器信息"""
        registry = self.load_registry()
        return registry["connectors"].get(connector_id)

    def list_connectors(self) -> Dict[str, Any]:
        """列出所有连接器"""
        registry = self.load_registry()
        return {
            "connectors": list(registry["connectors"].values()),
            "total": len(registry["connectors"]),
            "updated_at": registry["registry"]["updated_at"],
        }

    def validate_package(self, package_path: Path) -> Dict[str, Any]:
        """验证连接器包"""
        try:
            with zipfile.ZipFile(package_path, "r") as zf:
                # 检查必需文件
                files = zf.namelist()

                if "connector.json" not in files:
                    return {"valid": False, "error": "Missing connector.json"}

                if "README.md" not in files:
                    return {"valid": False, "error": "Missing README.md"}

                # 验证connector.json
                with zf.open("connector.json") as f:
                    connector_info = json.load(f)

                required_fields = ["id", "name", "version", "description"]
                for field in required_fields:
                    if field not in connector_info:
                        return {"valid": False, "error": f"Missing field: {field}"}

                # 检查可执行文件
                has_executable = any(
                    f.endswith((".py", ".exe")) or "main" in f for f in files
                )

                if not has_executable:
                    return {"valid": False, "error": "No executable file found"}

                return {"valid": True, "connector_info": connector_info, "files": files}

        except Exception as e:
            return {"valid": False, "error": f"Package validation failed: {e}"}

    def calculate_checksum(self, file_path: Path) -> str:
        """计算文件SHA256校验和"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return f"sha256:{sha256_hash.hexdigest()}"


registry_manager = RegistryManager()

# API路由


@app.get("/")
async def root():
    """根路径"""
    return {"message": "Linch Mind Connector Registry", "version": "1.0.0"}


@app.get("/v1/registry")
async def get_registry_info():
    """获取注册表信息"""
    registry = registry_manager.load_registry()
    return registry["registry"]


@app.get("/v1/connectors")
async def list_connectors():
    """列出所有连接器"""
    return registry_manager.list_connectors()


@app.get("/v1/connectors/{connector_id}")
async def get_connector(connector_id: str):
    """获取特定连接器信息"""
    connector_info = registry_manager.get_connector_info(connector_id)
    if not connector_info:
        raise HTTPException(status_code=404, detail="Connector not found")
    return connector_info


@app.get("/v1/connectors/{connector_id}/{version}/download")
async def download_connector(connector_id: str, version: str):
    """下载连接器包"""
    connector_info = registry_manager.get_connector_info(connector_id)
    if not connector_info:
        raise HTTPException(status_code=404, detail="Connector not found")

    if version not in connector_info["versions"]:
        raise HTTPException(status_code=404, detail="Version not found")

    # 查找包文件
    package_path = registry_manager.packages_dir / f"{connector_id}-{version}.zip"
    if not package_path.exists():
        raise HTTPException(status_code=404, detail="Package file not found")

    # 更新下载统计
    registry = registry_manager.load_registry()
    registry["stats"]["total_downloads"] += 1
    registry_manager.save_registry(registry)

    return FileResponse(
        package_path,
        media_type="application/zip",
        filename=f"{connector_id}-{version}.zip",
    )


@app.post("/v1/connectors/publish")
async def publish_connector(file: UploadFile = File(...)):
    """发布连接器到注册表"""
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are allowed")

    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_path = Path(tmp_file.name)

    try:
        # 验证包
        validation = registry_manager.validate_package(tmp_path)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["error"])

        connector_info = validation["connector_info"]
        connector_id = connector_info["id"]
        version = connector_info["version"]

        # 移动到packages目录
        package_path = registry_manager.packages_dir / f"{connector_id}-{version}.zip"
        shutil.move(str(tmp_path), str(package_path))

        # 计算校验和
        checksum = registry_manager.calculate_checksum(package_path)
        size = package_path.stat().st_size

        # 更新注册表
        registry = registry_manager.load_registry()

        if connector_id not in registry["connectors"]:
            registry["connectors"][connector_id] = {
                "id": connector_id,
                "name": connector_info["name"],
                "description": connector_info["description"],
                "author": connector_info.get("author", "Unknown"),
                "category": connector_info.get("category", "other"),
                "homepage": connector_info.get("homepage", ""),
                "versions": {},
                "latest": version,
                "deprecated": False,
            }

        # 添加版本信息
        version_info = {
            "version": version,
            "published_at": datetime.utcnow().isoformat() + "Z",
            "download_url": f"http://localhost:8001/v1/connectors/{connector_id}/{version}/download",
            "size": size,
            "checksum": checksum,
            "platforms": connector_info.get("platforms", {}).keys() or ["all"],
            "requires": connector_info.get("requires", {}),
            "permissions": connector_info.get("permissions", []),
            "changelog": connector_info.get("changelog", "No changelog provided"),
        }

        registry["connectors"][connector_id]["versions"][version] = version_info
        registry["connectors"][connector_id]["latest"] = version
        registry["stats"]["total_connectors"] = len(registry["connectors"])

        registry_manager.save_registry(registry)

        return {
            "message": f"Connector {connector_id} v{version} published successfully",
            "connector_id": connector_id,
            "version": version,
            "download_url": version_info["download_url"],
        }

    except Exception as e:
        # 清理临时文件
        if tmp_path.exists():
            tmp_path.unlink()
        raise HTTPException(status_code=500, detail=f"Publishing failed: {e}")


@app.delete("/v1/connectors/{connector_id}/{version}")
async def unpublish_connector(connector_id: str, version: str):
    """从注册表删除连接器版本"""
    registry = registry_manager.load_registry()

    if connector_id not in registry["connectors"]:
        raise HTTPException(status_code=404, detail="Connector not found")

    connector = registry["connectors"][connector_id]
    if version not in connector["versions"]:
        raise HTTPException(status_code=404, detail="Version not found")

    # 删除版本
    del connector["versions"][version]

    # 删除包文件
    package_path = registry_manager.packages_dir / f"{connector_id}-{version}.zip"
    if package_path.exists():
        package_path.unlink()

    # 如果没有版本了，删除整个连接器
    if not connector["versions"]:
        del registry["connectors"][connector_id]
    else:
        # 更新latest版本
        latest_version = max(connector["versions"].keys())
        connector["latest"] = latest_version

    registry["stats"]["total_connectors"] = len(registry["connectors"])
    registry_manager.save_registry(registry)

    return {"message": f"Connector {connector_id} v{version} unpublished"}


if __name__ == "__main__":
    print("🚀 Starting Linch Mind Connector Registry...")
    print(f"📁 Packages directory: {PACKAGES_DIR}")
    print(f"📄 Registry file: {REGISTRY_FILE}")
    print("🌐 Server will be available at: http://localhost:8001")

    uvicorn.run(
        "registry_server:app", host="0.0.0.0", port=8001, reload=True, log_level="info"
    )
