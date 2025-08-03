#!/usr/bin/env python3
"""
连接器管理路由 - 连接器类型和实例的完整管理
支持连接器市场、实例创建、配置管理等功能
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging
from pathlib import Path
import subprocess
import json
import uuid
import zipfile
import shutil
import tempfile
from datetime import datetime

from models.api_models import ApiResponse
from models.database_models import ConnectorType, ConnectorInstance
from services.database_service import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/connector-management", tags=["connector-management"])


@router.get("/types", response_model=List[dict])
async def list_connector_types(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取所有可用的连接器类型"""
    logger.info(f"获取连接器类型列表, 分类: {category}")
    
    query = db.query(ConnectorType).filter(ConnectorType.is_enabled == True)
    if category:
        query = query.filter(ConnectorType.category == category)
    
    types = query.all()
    
    return [
        {
            "type_id": t.type_id,
            "name": t.name,
            "description": t.description,
            "category": t.category,
            "icon": t.icon,
            "version": t.version,
            "config_schema": t.config_schema,
            "ui_schema": t.ui_schema,
            "default_config": t.default_config,
            "requirements": t.requirements
        }
        for t in types
    ]


@router.get("/types/{type_id}")
async def get_connector_type(
    type_id: str,
    db: Session = Depends(get_db)
):
    """获取特定连接器类型的详细信息"""
    logger.info(f"获取连接器类型详情: {type_id}")
    
    connector_type = db.query(ConnectorType).filter(
        ConnectorType.type_id == type_id
    ).first()
    
    if not connector_type:
        raise HTTPException(status_code=404, detail="连接器类型不存在")
    
    return {
        "type_id": connector_type.type_id,
        "name": connector_type.name,
        "description": connector_type.description,
        "category": connector_type.category,
        "executable_path": connector_type.executable_path,
        "icon": connector_type.icon,
        "config_schema": connector_type.config_schema,
        "ui_schema": connector_type.ui_schema,
        "default_config": connector_type.default_config,
        "requirements": connector_type.requirements,
        "version": connector_type.version
    }


@router.post("/instances")
async def create_connector_instance(
    instance_data: dict,
    db: Session = Depends(get_db)
):
    """创建新的连接器实例"""
    logger.info(f"创建连接器实例: {instance_data}")
    
    try:
        type_id = instance_data.get("type_id")
        display_name = instance_data.get("display_name")
        config = instance_data.get("config", {})
        auto_start = instance_data.get("auto_start", True)
        template_id = instance_data.get("template_id")  # 可选的配置模板
        
        # 验证连接器类型存在
        connector_type = db.query(ConnectorType).filter(
            ConnectorType.type_id == type_id
        ).first()
        
        if not connector_type:
            raise HTTPException(status_code=404, detail="连接器类型不存在")
        
        # 检查多实例支持
        if not connector_type.supports_multiple_instances:
            # 检查是否已存在实例
            existing_instance = db.query(ConnectorInstance).filter(
                ConnectorInstance.type_id == type_id
            ).first()
            
            if existing_instance:
                raise HTTPException(
                    status_code=400, 
                    detail=f"连接器类型 {type_id} 不支持多实例，已存在实例: {existing_instance.display_name}"
                )
        else:
            # 检查实例数量限制
            instance_count = db.query(ConnectorInstance).filter(
                ConnectorInstance.type_id == type_id
            ).count()
            
            if instance_count >= connector_type.max_instances_per_user:
                raise HTTPException(
                    status_code=400,
                    detail=f"已达到最大实例数限制 ({connector_type.max_instances_per_user})"
                )
        
        # 如果指定了模板，使用模板配置
        if template_id and connector_type.instance_templates:
            template = next(
                (t for t in connector_type.instance_templates if t.get("id") == template_id),
                None
            )
            if template:
                # 合并模板配置和用户配置
                template_config = template.get("config", {})
                config = {**template_config, **config}  # 用户配置覆盖模板配置
                logger.info(f"使用模板 {template_id} 创建实例")
        
        # 生成唯一的实例ID
        instance_id = f"{type_id}_{uuid.uuid4().hex[:8]}"
        
        # 验证配置（简化版本）
        required_fields = connector_type.config_schema.get("required", [])
        for field in required_fields:
            if field not in config:
                raise HTTPException(
                    status_code=400, 
                    detail=f"缺少必需配置字段: {field}"
                )
        
        # 创建实例记录
        instance = ConnectorInstance(
            instance_id=instance_id,
            display_name=display_name,
            type_id=type_id,
            config=config,
            auto_start=auto_start,
            status="stopped"
        )
        
        db.add(instance)
        db.commit()
        db.refresh(instance)
        
        # 如果设置为自动启动，则启动连接器
        if auto_start:
            success = await _start_connector_process(instance, connector_type, db)
            if not success:
                logger.warning(f"连接器实例 {instance_id} 创建成功但启动失败")
        
        return {
            "success": True,
            "message": "连接器实例创建成功",
            "instance_id": instance_id,
            "status": instance.status,
            "supports_multiple_instances": connector_type.supports_multiple_instances,
            "max_instances": connector_type.max_instances_per_user,
            "current_instances": instance_count + 1
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建连接器实例失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建连接器实例失败: {str(e)}")


@router.get("/instances")
async def list_connector_instances(
    type_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取所有连接器实例"""
    logger.info(f"获取连接器实例列表, 类型: {type_id}, 状态: {status}")
    
    query = db.query(ConnectorInstance)
    if type_id:
        query = query.filter(ConnectorInstance.type_id == type_id)
    if status:
        query = query.filter(ConnectorInstance.status == status)
    
    instances = query.all()
    
    return [
        {
            "instance_id": inst.instance_id,
            "display_name": inst.display_name,
            "type_id": inst.type_id,
            "status": inst.status,
            "data_count": inst.data_count,
            "auto_start": inst.auto_start,
            "last_heartbeat": inst.last_heartbeat,
            "error_message": inst.error_message,
            "created_at": inst.created_at,
            "connector_type_name": inst.connector_type.name if inst.connector_type else None
        }
        for inst in instances
    ]


@router.get("/instances/{instance_id}")
async def get_connector_instance(
    instance_id: str,
    db: Session = Depends(get_db)
):
    """获取特定连接器实例的详细信息"""
    logger.info(f"获取连接器实例详情: {instance_id}")
    
    instance = db.query(ConnectorInstance).filter(
        ConnectorInstance.instance_id == instance_id
    ).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="连接器实例不存在")
    
    return {
        "instance_id": instance.instance_id,
        "display_name": instance.display_name,
        "type_id": instance.type_id,
        "config": instance.config,
        "status": instance.status,
        "process_id": instance.process_id,
        "data_count": instance.data_count,
        "auto_start": instance.auto_start,
        "last_heartbeat": instance.last_heartbeat,
        "error_message": instance.error_message,
        "created_at": instance.created_at,
        "updated_at": instance.updated_at,
        "connector_type": {
            "name": instance.connector_type.name,
            "description": instance.connector_type.description,
            "category": instance.connector_type.category
        } if instance.connector_type else None
    }


@router.post("/instances/{instance_id}/start")
async def start_connector_instance(
    instance_id: str,
    db: Session = Depends(get_db)
):
    """启动连接器实例"""
    logger.info(f"启动连接器实例: {instance_id}")
    
    instance = db.query(ConnectorInstance).filter(
        ConnectorInstance.instance_id == instance_id
    ).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="连接器实例不存在")
    
    if instance.status == "running":
        return ApiResponse(success=True, message="连接器已在运行")
    
    connector_type = instance.connector_type
    success = await _start_connector_process(instance, connector_type, db)
    
    if success:
        return ApiResponse(success=True, message="连接器启动成功")
    else:
        raise HTTPException(status_code=500, detail="连接器启动失败")


@router.post("/instances/{instance_id}/stop")
async def stop_connector_instance(
    instance_id: str,
    db: Session = Depends(get_db)
):
    """停止连接器实例"""
    logger.info(f"停止连接器实例: {instance_id}")
    
    instance = db.query(ConnectorInstance).filter(
        ConnectorInstance.instance_id == instance_id
    ).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="连接器实例不存在")
    
    if instance.status != "running":
        return ApiResponse(success=True, message="连接器已停止")
    
    success = await _stop_connector_process(instance, db)
    
    if success:
        return ApiResponse(success=True, message="连接器停止成功")
    else:
        raise HTTPException(status_code=500, detail="连接器停止失败")


@router.put("/instances/{instance_id}/config")
async def update_connector_config(
    instance_id: str,
    new_config: dict,
    db: Session = Depends(get_db)
):
    """更新连接器实例配置"""
    logger.info(f"更新连接器实例配置: {instance_id}")
    
    try:
        instance = db.query(ConnectorInstance).filter(
            ConnectorInstance.instance_id == instance_id
        ).first()
        
        if not instance:
            raise HTTPException(status_code=404, detail="连接器实例不存在")
        
        connector_type = instance.connector_type
        
        # 验证配置
        required_fields = connector_type.config_schema.get("required", [])
        for field in required_fields:
            if field not in new_config:
                raise HTTPException(
                    status_code=400, 
                    detail=f"缺少必需配置字段: {field}"
                )
        
        # 更新配置
        instance.config = new_config
        instance.updated_at = datetime.utcnow()
        db.commit()
        
        # 如果连接器正在运行，通知重新加载配置
        if instance.status == "running":
            # TODO: 实现配置热重载通知机制
            logger.info(f"连接器 {instance_id} 正在运行，需要通知重新加载配置")
        
        return ApiResponse(success=True, message="配置更新成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


@router.delete("/instances/{instance_id}")
async def delete_connector_instance(
    instance_id: str,
    force: bool = False,
    db: Session = Depends(get_db)
):
    """删除连接器实例"""
    logger.info(f"删除连接器实例: {instance_id}")
    
    instance = db.query(ConnectorInstance).filter(
        ConnectorInstance.instance_id == instance_id
    ).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="连接器实例不存在")
    
    # 如果连接器正在运行，先停止它
    if instance.status == "running":
        if not force:
            raise HTTPException(
                status_code=400, 
                detail="连接器正在运行，请先停止或使用force=true强制删除"
            )
        await _stop_connector_process(instance, db)
    
    # 删除实例
    db.delete(instance)
    db.commit()
    
    return ApiResponse(success=True, message="连接器实例删除成功")


async def _start_connector_process(
    instance: ConnectorInstance, 
    connector_type: ConnectorType, 
    db: Session
) -> bool:
    """启动连接器进程"""
    try:
        # 更新状态为启动中
        instance.status = "starting"
        instance.error_message = None
        db.commit()
        
        # 准备环境变量
        env = {
            "DAEMON_URL": "http://localhost:8088",
            "CONNECTOR_INSTANCE_ID": instance.instance_id,
            "CONNECTOR_CONFIG": json.dumps(instance.config)
        }
        
        # 启动连接器进程
        executable_path = Path(connector_type.executable_path)
        if not executable_path.exists():
            raise Exception(f"连接器可执行文件不存在: {executable_path}")
        
        process = subprocess.Popen(
            ["python", str(executable_path)],
            env={**subprocess.os.environ, **env},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 更新实例状态
        instance.process_id = process.pid
        instance.status = "running"
        instance.last_heartbeat = datetime.utcnow()
        db.commit()
        
        logger.info(f"连接器 {instance.instance_id} 启动成功, PID: {process.pid}")
        return True
        
    except Exception as e:
        logger.error(f"启动连接器失败: {e}")
        instance.status = "error"
        instance.error_message = str(e)
        db.commit()
        return False


async def _stop_connector_process(instance: ConnectorInstance, db: Session) -> bool:
    """停止连接器进程"""
    try:
        if instance.process_id:
            import psutil
            try:
                process = psutil.Process(instance.process_id)
                process.terminate()
                process.wait(timeout=10)
            except psutil.NoSuchProcess:
                logger.warning(f"进程 {instance.process_id} 不存在，可能已经停止")
            except psutil.TimeoutExpired:
                logger.warning(f"进程 {instance.process_id} 未在超时时间内停止，强制终止")
                process.kill()
        
        # 更新状态
        instance.status = "stopped"
        instance.process_id = None
        instance.error_message = None
        db.commit()
        
        logger.info(f"连接器 {instance.instance_id} 停止成功")
        return True
        
    except Exception as e:
        logger.error(f"停止连接器失败: {e}")
        instance.status = "error"
        instance.error_message = str(e)
        db.commit()
        return False


@router.post("/discover-types")
async def discover_connector_types(db: Session = Depends(get_db)):
    """扫描并注册可用的连接器类型"""
    logger.info("开始扫描和注册连接器类型")
    
    try:
        connectors_dir = Path("connectors")
        if not connectors_dir.exists():
            raise HTTPException(status_code=404, detail="连接器目录不存在")
        
        discovered_count = 0
        
        for connector_path in connectors_dir.iterdir():
            if connector_path.is_dir() and connector_path.name != "shared":
                try:
                    # 尝试导入连接器模块并获取类型信息
                    type_info = await _discover_connector_type(connector_path)
                    if type_info:
                        # 创建或更新连接器类型
                        existing_type = db.query(ConnectorType).filter(
                            ConnectorType.type_id == type_info["type_id"]
                        ).first()
                        
                        if existing_type:
                            # 更新现有类型
                            for key, value in type_info.items():
                                setattr(existing_type, key, value)
                            existing_type.updated_at = datetime.utcnow()
                        else:
                            # 创建新类型
                            new_type = ConnectorType(**type_info)
                            db.add(new_type)
                        
                        discovered_count += 1
                        logger.info(f"发现连接器类型: {type_info['type_id']}")
                
                except Exception as e:
                    logger.error(f"处理连接器 {connector_path.name} 时出错: {e}")
        
        db.commit()
        
        return {
            "success": True,
            "message": f"扫描完成，发现 {discovered_count} 个连接器类型",
            "discovered_count": discovered_count
        }
        
    except Exception as e:
        logger.error(f"扫描连接器类型失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"扫描连接器类型失败: {str(e)}")


async def _discover_connector_type(connector_path: Path) -> Optional[dict]:
    """从连接器目录发现类型信息"""
    try:
        main_file = connector_path / "main.py"
        if not main_file.exists():
            return None
        
        # 这里简化实现，实际应该动态导入模块
        # 为演示目的，返回基于目录名的类型信息
        connector_name = connector_path.name
        
        if connector_name == "filesystem":
            return {
                "type_id": "filesystem",
                "name": "文件系统连接器",
                "description": "监控文件系统变化，实时索引文件内容",
                "category": "local_files",
                "executable_path": str(main_file),
                "icon": "folder",
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "watch_paths": {"type": "array", "items": {"type": "string"}},
                        "supported_extensions": {"type": "array", "items": {"type": "string"}},
                        "max_file_size": {"type": "integer"}
                    }
                },
                "ui_schema": {},
                "default_config": {
                    "watch_paths": ["~/Downloads", "~/Documents"],
                    "supported_extensions": [".txt", ".md", ".py"],
                    "max_file_size": 1
                },
                "requirements": {"python": ">=3.8"}
            }
        elif connector_name == "clipboard":
            return {
                "type_id": "clipboard",
                "name": "剪贴板连接器",
                "description": "监控剪贴板变化，索引复制的内容",
                "category": "system",
                "executable_path": str(main_file),
                "icon": "clipboard",
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "check_interval": {"type": "number"},
                        "max_content_length": {"type": "integer"}
                    }
                },
                "ui_schema": {},
                "default_config": {
                    "check_interval": 1.0,
                    "max_content_length": 10000
                },
                "requirements": {"python": ">=3.8"}
            }
        
        return None
        
    except Exception as e:
        logger.error(f"发现连接器类型时出错: {e}")
        return None


@router.post("/install-package")
async def install_connector_package(
    package_file: bytes,
    db: Session = Depends(get_db)
):
    """安装连接器包"""
    logger.info("开始安装连接器包")
    
    try:
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 保存上传的包文件
            package_path = temp_path / "connector-package.zip"
            with open(package_path, "wb") as f:
                f.write(package_file)
            
            # 验证并解压包
            extract_path = temp_path / "extracted"
            extract_path.mkdir()
            
            with zipfile.ZipFile(package_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            # 读取连接器元数据
            connector_json = extract_path / "connector.json"
            if not connector_json.exists():
                raise HTTPException(
                    status_code=400, 
                    detail="连接器包中缺少 connector.json 文件"
                )
            
            with open(connector_json, 'r', encoding='utf-8') as f:
                connector_metadata = json.load(f)
            
            # 验证元数据结构
            if "connector_info" not in connector_metadata:
                raise HTTPException(
                    status_code=400,
                    detail="connector.json 中缺少 connector_info 部分"
                )
            
            connector_info = connector_metadata["connector_info"]
            capabilities = connector_metadata.get("capabilities", {})
            system_requirements = connector_metadata.get("system_requirements", {})
            config_schema = connector_metadata.get("config_schema", {})
            ui_schema = connector_metadata.get("ui_schema", {})
            instance_templates = connector_metadata.get("instance_templates", [])
            
            type_id = connector_info["type_id"]
            
            # 检查连接器是否已存在
            existing_type = db.query(ConnectorType).filter(
                ConnectorType.type_id == type_id
            ).first()
            
            if existing_type:
                # 版本比较逻辑
                existing_version = existing_type.version
                new_version = connector_info["version"]
                
                if existing_version == new_version:
                    raise HTTPException(
                        status_code=400,
                        detail=f"连接器 {type_id} 版本 {new_version} 已安装"
                    )
                
                logger.info(f"升级连接器 {type_id} 从 {existing_version} 到 {new_version}")
            
            # 验证入口文件存在
            entry_point = connector_info.get("entry_point", "main.py")
            entry_file = extract_path / entry_point
            if not entry_file.exists():
                raise HTTPException(
                    status_code=400,
                    detail=f"连接器包中缺少入口文件: {entry_point}"
                )
            
            # 创建安装目录
            install_base = Path("connectors")
            install_base.mkdir(exist_ok=True)
            
            install_path = install_base / type_id
            
            # 如果已存在，备份旧版本
            if install_path.exists():
                backup_path = install_base / f"{type_id}_backup_{existing_type.version}"
                if backup_path.exists():
                    shutil.rmtree(backup_path)
                shutil.move(str(install_path), str(backup_path))
                logger.info(f"已备份旧版本到: {backup_path}")
            
            # 复制文件到安装目录
            shutil.copytree(extract_path, install_path)
            
            # 安装依赖 (如果有 requirements.txt)
            requirements_file = install_path / "requirements.txt"
            if requirements_file.exists():
                try:
                    subprocess.run([
                        "pip", "install", "-r", str(requirements_file)
                    ], check=True, capture_output=True)
                    logger.info(f"已安装依赖: {requirements_file}")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"安装依赖失败: {e}")
                    # 继续安装，但记录警告
            
            # 创建或更新数据库记录
            connector_data = {
                "type_id": type_id,
                "name": connector_info["name"],
                "display_name": connector_info.get("display_name", connector_info["name"]),
                "description": connector_info.get("description", ""),
                "category": connector_info.get("category", "other"),
                "executable_path": str(install_path / entry_point),
                "icon": connector_info.get("icon", "default"),
                "version": connector_info["version"],
                "author": connector_info.get("author", ""),
                "license": connector_info.get("license", ""),
                "homepage": connector_info.get("homepage", ""),
                
                # 能力配置
                "supports_multiple_instances": capabilities.get("supports_multiple_instances", False),
                "max_instances_per_user": capabilities.get("max_instances_per_user", 1),
                "instance_isolation": capabilities.get("instance_isolation", "process"),
                "auto_discovery": capabilities.get("auto_discovery", False),
                "hot_config_reload": capabilities.get("hot_config_reload", False),
                "health_check": capabilities.get("health_check", True),
                "metrics_reporting": capabilities.get("metrics_reporting", False),
                
                # 配置和模板
                "config_schema": config_schema,
                "ui_schema": ui_schema,
                "default_config": config_schema.get("properties", {}),
                "instance_templates": instance_templates,
                
                # 系统要求
                "system_requirements": system_requirements,
                "dependencies": connector_info.get("dependencies", []),
                
                # 安装信息
                "installation_path": str(install_path),
                "package_info": {
                    "install_method": "package_upload",
                    "install_time": datetime.utcnow().isoformat(),
                    "package_size": len(package_file),
                    "checksum": str(hash(package_file))
                }
            }
            
            if existing_type:
                # 更新现有记录
                for key, value in connector_data.items():
                    setattr(existing_type, key, value)
                existing_type.updated_at = datetime.utcnow()
                action = "升级"
            else:
                # 创建新记录
                new_type = ConnectorType(**connector_data)
                db.add(new_type)
                action = "安装"
            
            db.commit()
            
            return {
                "success": True,
                "message": f"连接器 {connector_info['name']} {action}成功",
                "connector_info": {
                    "type_id": type_id,
                    "name": connector_info["name"],
                    "version": connector_info["version"],
                    "supports_multiple_instances": capabilities.get("supports_multiple_instances", False),
                    "max_instances": capabilities.get("max_instances_per_user", 1)
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"安装连接器包失败: {e}")
        raise HTTPException(status_code=500, detail=f"安装连接器包失败: {str(e)}")


@router.delete("/types/{type_id}")
async def uninstall_connector_type(
    type_id: str,
    force: bool = False,
    db: Session = Depends(get_db)
):
    """卸载连接器类型"""
    logger.info(f"卸载连接器类型: {type_id}")
    
    try:
        connector_type = db.query(ConnectorType).filter(
            ConnectorType.type_id == type_id
        ).first()
        
        if not connector_type:
            raise HTTPException(status_code=404, detail="连接器类型不存在")
        
        # 检查是否有运行中的实例
        running_instances = db.query(ConnectorInstance).filter(
            ConnectorInstance.type_id == type_id,
            ConnectorInstance.status == "running"
        ).all()
        
        if running_instances and not force:
            raise HTTPException(
                status_code=400,
                detail=f"存在 {len(running_instances)} 个运行中的实例，请先停止或使用 force=true"
            )
        
        # 停止所有运行中的实例
        for instance in running_instances:
            await _stop_connector_process(instance, db)
        
        # 删除所有实例
        db.query(ConnectorInstance).filter(
            ConnectorInstance.type_id == type_id
        ).delete()
        
        # 删除安装文件
        if connector_type.installation_path:
            install_path = Path(connector_type.installation_path).parent
            if install_path.exists():
                shutil.rmtree(install_path)
                logger.info(f"已删除安装文件: {install_path}")
        
        # 删除数据库记录
        db.delete(connector_type)
        db.commit()
        
        return ApiResponse(
            success=True, 
            message=f"连接器类型 {connector_type.name} 卸载成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"卸载连接器类型失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"卸载连接器类型失败: {str(e)}")


@router.get("/types/{type_id}/templates")
async def get_connector_templates(
    type_id: str,
    db: Session = Depends(get_db)
):
    """获取连接器实例模板"""
    logger.info(f"获取连接器模板: {type_id}")
    
    connector_type = db.query(ConnectorType).filter(
        ConnectorType.type_id == type_id
    ).first()
    
    if not connector_type:
        raise HTTPException(status_code=404, detail="连接器类型不存在")
    
    return {
        "type_id": type_id,
        "supports_multiple_instances": connector_type.supports_multiple_instances,
        "max_instances": connector_type.max_instances_per_user,
        "templates": connector_type.instance_templates or []
    }