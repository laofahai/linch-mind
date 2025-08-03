#!/usr/bin/env python3
"""
连接器管理路由 - 连接器生命周期管理
Session 5 架构重构 - 模块化路由
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging
from datetime import datetime

from models.api_models import ConnectorInfo, ApiResponse
from models.database_models import ConnectorConfigSchema
from services.connector_manager import ConnectorManager
from api.dependencies import get_connectors, get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/connectors", tags=["connectors"])


@router.get("/", response_model=List[ConnectorInfo])
async def list_connectors(
    connector_manager: ConnectorManager = Depends(get_connectors)
):
    """获取所有连接器状态"""
    logger.info("获取连接器列表")
    # 将可用连接器转换为ConnectorInfo格式
    available = connector_manager.list_available_connectors()
    running = connector_manager.list_running_connectors()
    
    # 创建完整的连接器信息列表
    result = []
    for connector_data in available:
        connector_id = connector_data['id']
        # 检查是否在运行中
        running_info = next((r for r in running if r.id == connector_id), None)
        
        connector_info = ConnectorInfo(
            id=connector_id,
            name=connector_data['name'],
            description=connector_data['description'],
            status=running_info.status if running_info else connector_manager.get_connector_status(connector_id),
            data_count=running_info.data_count if running_info else 0,
            last_update=running_info.last_update if running_info else datetime.now(),
            config=connector_data.get('capabilities', {})
        )
        result.append(connector_info)
    
    return result


@router.post("/{connector_id}/start")
async def start_connector(
    connector_id: str,
    connector_manager: ConnectorManager = Depends(get_connectors)
):
    """启动指定连接器"""
    logger.info(f"启动连接器: {connector_id}")
    
    success = await connector_manager.start_connector(connector_id)
    if success:
        return ApiResponse(success=True, message=f"连接器 {connector_id} 已启动")
    else:
        raise HTTPException(status_code=500, detail=f"启动连接器 {connector_id} 失败")


@router.post("/{connector_id}/stop")
async def stop_connector(
    connector_id: str,
    connector_manager: ConnectorManager = Depends(get_connectors)
):
    """停止指定连接器"""
    logger.info(f"停止连接器: {connector_id}")
    
    success = await connector_manager.stop_connector(connector_id)
    if success:
        return ApiResponse(success=True, message=f"连接器 {connector_id} 已停止")
    else:
        raise HTTPException(status_code=500, detail=f"停止连接器 {connector_id} 失败")


@router.get("/{connector_id}/status")
async def get_connector_status(
    connector_id: str,
    connector_manager: ConnectorManager = Depends(get_connectors)
):
    """获取特定连接器状态"""
    logger.info(f"获取连接器状态: {connector_id}")
    
    connector_info = connector_manager.get_connector_info(connector_id)
    if connector_info:
        return connector_info
    
    raise HTTPException(status_code=404, detail=f"连接器 {connector_id} 不存在")


@router.post("/{connector_id}/schema")
async def register_connector_schema(
    connector_id: str,
    schema_data: dict,
    db: Session = Depends(get_db)
):
    """注册连接器配置schema"""
    logger.info(f"注册连接器配置schema: {connector_id}")
    
    try:
        # 提取schema数据
        config_schema = schema_data.get("config_schema", {})
        ui_schema = schema_data.get("ui_schema", {})
        connector_name = schema_data.get("connector_name", connector_id)
        connector_description = schema_data.get("connector_description", "")
        
        # 提取默认配置
        default_config = {}
        if "properties" in config_schema:
            for key, prop in config_schema["properties"].items():
                if "default" in prop:
                    default_config[key] = prop["default"]
        
        # 创建或更新配置schema记录
        existing_schema = db.query(ConnectorConfigSchema).filter(
            ConnectorConfigSchema.connector_id == connector_id
        ).first()
        
        if existing_schema:
            # 更新现有记录
            existing_schema.connector_name = connector_name
            existing_schema.connector_description = connector_description
            existing_schema.config_schema = config_schema
            existing_schema.ui_schema = ui_schema
            existing_schema.default_config = default_config
            # 如果当前配置为空，使用默认配置
            if not existing_schema.current_config:
                existing_schema.current_config = default_config
        else:
            # 创建新记录
            new_schema = ConnectorConfigSchema(
                connector_id=connector_id,
                connector_name=connector_name,
                connector_description=connector_description,
                config_schema=config_schema,
                ui_schema=ui_schema,
                current_config=default_config,
                default_config=default_config
            )
            db.add(new_schema)
        
        db.commit()
        
        return ApiResponse(success=True, message="配置schema注册成功")
        
    except Exception as e:
        logger.error(f"注册配置schema失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"注册配置schema失败: {str(e)}")


@router.get("/{connector_id}/schema")
async def get_connector_schema(
    connector_id: str,
    db: Session = Depends(get_db)
):
    """获取连接器配置schema"""
    logger.info(f"获取连接器配置schema: {connector_id}")
    
    schema = db.query(ConnectorConfigSchema).filter(
        ConnectorConfigSchema.connector_id == connector_id
    ).first()
    
    if not schema:
        raise HTTPException(status_code=404, detail="连接器配置schema不存在")
    
    return {
        "connector_id": schema.connector_id,
        "connector_name": schema.connector_name,
        "connector_description": schema.connector_description,
        "config_schema": schema.config_schema,
        "ui_schema": schema.ui_schema,
        "current_config": schema.current_config,
        "default_config": schema.default_config,
        "schema_version": schema.schema_version
    }


@router.get("/{connector_id}/config")
async def get_connector_config(
    connector_id: str,
    db: Session = Depends(get_db)
):
    """获取连接器当前配置"""
    logger.info(f"获取连接器配置: {connector_id}")
    
    schema = db.query(ConnectorConfigSchema).filter(
        ConnectorConfigSchema.connector_id == connector_id
    ).first()
    
    if not schema:
        # 如果schema不存在，返回空配置
        return {}
    
    return schema.current_config or {}


@router.put("/{connector_id}/config")
async def update_connector_config(
    connector_id: str,
    new_config: dict,
    db: Session = Depends(get_db)
):
    """更新连接器配置"""
    logger.info(f"更新连接器配置: {connector_id}")
    
    try:
        schema = db.query(ConnectorConfigSchema).filter(
            ConnectorConfigSchema.connector_id == connector_id
        ).first()
        
        if not schema:
            raise HTTPException(status_code=404, detail="连接器配置schema不存在")
        
        # 简单验证：检查必需字段
        required_fields = schema.config_schema.get("required", [])
        for field in required_fields:
            if field not in new_config:
                raise HTTPException(
                    status_code=400, 
                    detail=f"缺少必需字段: {field}"
                )
        
        # 更新配置
        from datetime import datetime
        schema.current_config = new_config
        schema.last_config_update = datetime.utcnow()
        db.commit()
        
        logger.info(f"连接器 {connector_id} 配置更新成功")
        
        # TODO: 通知正在运行的连接器配置已变更
        # await notify_connector_config_change(connector_id, new_config)
        
        return ApiResponse(success=True, message="配置更新成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


@router.get("/schemas")
async def list_connector_schemas(db: Session = Depends(get_db)):
    """获取所有连接器的配置schema列表"""
    logger.info("获取所有连接器配置schema")
    
    schemas = db.query(ConnectorConfigSchema).all()
    
    return [
        {
            "connector_id": schema.connector_id,
            "connector_name": schema.connector_name,
            "connector_description": schema.connector_description,
            "schema_version": schema.schema_version,
            "has_config": bool(schema.current_config),
            "last_config_update": schema.last_config_update
        }
        for schema in schemas
    ]


@router.post("/{connector_id}/restart")
async def restart_connector(
    connector_id: str,
    connector_manager: ConnectorManager = Depends(get_connectors)
):
    """手动重启指定连接器"""
    logger.info(f"手动重启连接器: {connector_id}")
    
    # 先停止连接器
    await connector_manager.stop_connector(connector_id)
    
    # 重置重启计数（手动重启不计入自动重启限制）
    connector_manager.reset_restart_count(connector_id)
    
    # 等待1秒确保进程完全停止
    import asyncio
    await asyncio.sleep(1)
    
    # 重新启动
    success = await connector_manager.start_connector(connector_id)
    if success:
        return ApiResponse(success=True, message=f"连接器 {connector_id} 重启成功")
    else:
        raise HTTPException(status_code=500, detail=f"重启连接器 {connector_id} 失败")


@router.get("/{connector_id}/health")
async def get_connector_health(
    connector_id: str,
    connector_manager: ConnectorManager = Depends(get_connectors)
):
    """获取连接器健康状态和重启统计"""
    logger.info(f"获取连接器健康状态: {connector_id}")
    
    stats = connector_manager.get_restart_stats(connector_id)
    running_connectors = connector_manager.list_running_connectors()
    is_running = any(r.id == connector_id for r in running_connectors)
    
    return {
        "connector_id": connector_id,
        "is_running": is_running,
        "restart_stats": stats,
        "health_status": "healthy" if is_running else "stopped"
    }


@router.put("/{connector_id}/auto-restart")
async def configure_auto_restart(
    connector_id: str,
    config: dict,
    connector_manager: ConnectorManager = Depends(get_connectors)
):
    """配置连接器自动重启设置"""
    logger.info(f"配置连接器自动重启: {connector_id}")
    
    enabled = config.get("enabled", True)
    reset_count = config.get("reset_restart_count", False)
    
    # 设置自动重启状态
    connector_manager.enable_auto_restart(connector_id, enabled)
    
    # 可选：重置重启计数
    if reset_count:
        connector_manager.reset_restart_count(connector_id)
    
    return ApiResponse(
        success=True, 
        message=f"连接器 {connector_id} 自动重启{'启用' if enabled else '禁用'}"
    )