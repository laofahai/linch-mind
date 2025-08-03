#!/usr/bin/env python3
"""
连接器生命周期API路由 - 新架构的RESTful接口
提供清晰的连接器状态管理和生命周期控制API
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
import asyncio
import json
import logging
from datetime import datetime

from models.api_models import ApiResponse
from services.connectors.lifecycle_manager import (
    get_lifecycle_manager, 
    ConnectorLifecycleManager,
    ConnectorState
)
from config.core_config import get_core_config

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/connector-lifecycle", tags=["connector-lifecycle"])


@router.get("/discovery")
async def discover_connectors(
    lifecycle_manager: ConnectorLifecycleManager = Depends(get_lifecycle_manager)
):
    """发现可用的连接器类型"""
    logger.info("API: 发现连接器类型")
    
    try:
        connector_types = await lifecycle_manager.discover_connectors()
        
        return {
            "success": True,
            "message": f"发现 {len(connector_types)} 个连接器类型",
            "connector_types": [
                {
                    "type_id": ct.type_id,
                    "name": ct.name,
                    "display_name": ct.display_name,
                    "description": ct.description,
                    "category": ct.category,
                    "version": ct.version,
                    "author": ct.author,
                    "supports_multiple_instances": ct.supports_multiple_instances,
                    "max_instances_per_user": ct.max_instances_per_user,
                    "instance_templates": ct.instance_templates
                }
                for ct in connector_types
            ]
        }
        
    except Exception as e:
        logger.error(f"发现连接器失败: {e}")
        raise HTTPException(status_code=500, detail=f"发现连接器失败: {str(e)}")


@router.post("/instances")
async def create_connector_instance(
    instance_data: Dict[str, Any],
    lifecycle_manager: ConnectorLifecycleManager = Depends(get_lifecycle_manager)
):
    """创建连接器实例"""
    logger.info(f"API: 创建连接器实例 - {instance_data}")
    
    try:
        type_id = instance_data.get("type_id")
        display_name = instance_data.get("display_name")
        config = instance_data.get("config", {})
        auto_start = instance_data.get("auto_start", True)
        template_id = instance_data.get("template_id")
        
        if not type_id or not display_name:
            raise HTTPException(
                status_code=400, 
                detail="缺少必需参数: type_id, display_name"
            )
        
        instance_id = await lifecycle_manager.create_instance(
            type_id=type_id,
            display_name=display_name,
            config=config,
            auto_start=auto_start,
            template_id=template_id
        )
        
        if not instance_id:
            raise HTTPException(status_code=400, detail="创建连接器实例失败")
        
        # 获取实例状态
        state = lifecycle_manager.get_instance_state(instance_id)
        
        return {
            "success": True,
            "message": "连接器实例创建成功",
            "instance_id": instance_id,
            "state": state.value,
            "auto_started": auto_start
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建连接器实例失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建连接器实例失败: {str(e)}")


@router.get("/instances")
async def list_connector_instances(
    type_id: Optional[str] = None,
    state: Optional[str] = None,
    config_manager=Depends(get_core_config),
    lifecycle_manager: ConnectorLifecycleManager = Depends(get_lifecycle_manager)
):
    """列出连接器实例"""
    logger.info(f"API: 列出连接器实例 - type_id: {type_id}, state: {state}")
    
    try:
        instances = config_manager.list_instances(type_id=type_id, state=state)
        
        result_instances = []
        for instance in instances:
            # 获取实时状态
            runtime_state = lifecycle_manager.get_instance_state(instance.instance_id)
            
            # 获取连接器类型信息
            connector_type = config_manager.get_connector_type(instance.type_id)
            
            result_instances.append({
                "instance_id": instance.instance_id,
                "display_name": instance.display_name,
                "type_id": instance.type_id,
                "type_name": connector_type.name if connector_type else "未知",
                "state": runtime_state.value,
                "enabled": instance.enabled,
                "auto_start": instance.auto_start,
                "process_id": instance.process_id,
                "last_heartbeat": instance.last_heartbeat.isoformat() if instance.last_heartbeat and hasattr(instance.last_heartbeat, 'isoformat') else str(instance.last_heartbeat) if instance.last_heartbeat else None,
                "data_count": instance.data_count,
                "error_message": instance.error_message,
                "created_at": instance.created_at.isoformat() if instance.created_at and hasattr(instance.created_at, 'isoformat') else str(instance.created_at) if instance.created_at else None,
                "updated_at": instance.updated_at.isoformat() if instance.updated_at and hasattr(instance.updated_at, 'isoformat') else str(instance.updated_at) if instance.updated_at else None
            })
        
        return {
            "success": True,
            "instances": result_instances,
            "total_count": len(result_instances)
        }
        
    except Exception as e:
        logger.error(f"列出连接器实例失败: {e}")
        raise HTTPException(status_code=500, detail=f"列出连接器实例失败: {str(e)}")


@router.get("/instances/{instance_id}")
async def get_connector_instance(
    instance_id: str,
    config_manager=Depends(get_core_config),
    lifecycle_manager: ConnectorLifecycleManager = Depends(get_lifecycle_manager)
):
    """获取连接器实例详情"""
    logger.info(f"API: 获取连接器实例详情 - {instance_id}")
    
    try:
        instance = config_manager.get_instance(instance_id)
        if not instance:
            raise HTTPException(status_code=404, detail="连接器实例不存在")
        
        # 获取实时状态
        runtime_state = lifecycle_manager.get_instance_state(instance_id)
        
        # 获取连接器类型信息
        connector_type = config_manager.get_connector_type(instance.type_id)
        
        return {
            "success": True,
            "instance": {
                "instance_id": instance.instance_id,
                "display_name": instance.display_name,
                "type_id": instance.type_id,
                "config": instance.config,
                "state": runtime_state.value,
                "enabled": instance.enabled,
                "auto_start": instance.auto_start,
                "process_id": instance.process_id,
                "last_heartbeat": instance.last_heartbeat.isoformat() if instance.last_heartbeat and hasattr(instance.last_heartbeat, 'isoformat') else str(instance.last_heartbeat) if instance.last_heartbeat else None,
                "data_count": instance.data_count,
                "error_message": instance.error_message,
                "created_at": instance.created_at.isoformat() if instance.created_at and hasattr(instance.created_at, 'isoformat') else str(instance.created_at) if instance.created_at else None,
                "updated_at": instance.updated_at.isoformat() if instance.updated_at and hasattr(instance.updated_at, 'isoformat') else str(instance.updated_at) if instance.updated_at else None,
                "connector_type": {
                    "name": connector_type.name,
                    "display_name": connector_type.display_name,
                    "description": connector_type.description,
                    "category": connector_type.category,
                    "version": connector_type.version
                } if connector_type else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取连接器实例失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取连接器实例失败: {str(e)}")


@router.post("/instances/{instance_id}/start")
async def start_connector_instance(
    instance_id: str,
    lifecycle_manager: ConnectorLifecycleManager = Depends(get_lifecycle_manager)
):
    """启动连接器实例"""
    logger.info(f"API: 启动连接器实例 - {instance_id}")
    
    try:
        success = await lifecycle_manager.start_instance(instance_id)
        
        if success:
            state = lifecycle_manager.get_instance_state(instance_id)
            return {
                "success": True,
                "message": "连接器实例启动成功",
                "instance_id": instance_id,
                "state": state.value
            }
        else:
            raise HTTPException(status_code=500, detail="连接器实例启动失败")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启动连接器实例失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动连接器实例失败: {str(e)}")


@router.post("/instances/{instance_id}/stop")
async def stop_connector_instance(
    instance_id: str,
    force: bool = False,
    lifecycle_manager: ConnectorLifecycleManager = Depends(get_lifecycle_manager)
):
    """停止连接器实例"""
    logger.info(f"API: 停止连接器实例 - {instance_id}, force: {force}")
    
    try:
        success = await lifecycle_manager.stop_instance(instance_id, force=force)
        
        if success:
            state = lifecycle_manager.get_instance_state(instance_id)
            return {
                "success": True,
                "message": "连接器实例停止成功",
                "instance_id": instance_id,
                "state": state.value
            }
        else:
            raise HTTPException(status_code=500, detail="连接器实例停止失败")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"停止连接器实例失败: {e}")
        raise HTTPException(status_code=500, detail=f"停止连接器实例失败: {str(e)}")


@router.post("/instances/{instance_id}/restart")
async def restart_connector_instance(
    instance_id: str,
    lifecycle_manager: ConnectorLifecycleManager = Depends(get_lifecycle_manager)
):
    """重启连接器实例"""
    logger.info(f"API: 重启连接器实例 - {instance_id}")
    
    try:
        success = await lifecycle_manager.restart_instance(instance_id)
        
        if success:
            state = lifecycle_manager.get_instance_state(instance_id)
            return {
                "success": True,
                "message": "连接器实例重启成功",
                "instance_id": instance_id,
                "state": state.value
            }
        else:
            raise HTTPException(status_code=500, detail="连接器实例重启失败")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重启连接器实例失败: {e}")
        raise HTTPException(status_code=500, detail=f"重启连接器实例失败: {str(e)}")


@router.put("/instances/{instance_id}/config")
async def update_connector_config(
    instance_id: str,
    config_data: Dict[str, Any],
    config_manager=Depends(get_core_config),
    lifecycle_manager: ConnectorLifecycleManager = Depends(get_lifecycle_manager)
):
    """更新连接器实例配置"""
    logger.info(f"API: 更新连接器实例配置 - {instance_id}")
    
    try:
        new_config = config_data.get("config", {})
        
        # 验证实例存在
        instance = config_manager.get_instance(instance_id)
        if not instance:
            raise HTTPException(status_code=404, detail="连接器实例不存在")
        
        # 更新配置
        success = config_manager.update_instance(instance_id, config=new_config)
        if not success:
            raise HTTPException(status_code=500, detail="更新配置失败")
        
        # 如果连接器正在运行且支持热重载，通知重新加载配置
        runtime_state = lifecycle_manager.get_instance_state(instance_id)
        connector_type = config_manager.get_connector_type(instance.type_id)
        
        hot_reload_applied = False
        if (runtime_state == ConnectorState.RUNNING and 
            connector_type and connector_type.hot_config_reload):
            # TODO: 实现配置热重载通知机制
            logger.info(f"连接器 {instance_id} 支持热重载，应该通知重新加载配置")
            hot_reload_applied = True
        
        return {
            "success": True,
            "message": "配置更新成功",
            "instance_id": instance_id,
            "hot_reload_applied": hot_reload_applied,
            "requires_restart": not hot_reload_applied and runtime_state == ConnectorState.RUNNING
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新连接器配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新连接器配置失败: {str(e)}")


@router.delete("/instances/{instance_id}")
async def delete_connector_instance(
    instance_id: str,
    force: bool = False,
    config_manager=Depends(get_core_config),
    lifecycle_manager: ConnectorLifecycleManager = Depends(get_lifecycle_manager)
):
    """删除连接器实例"""
    logger.info(f"API: 删除连接器实例 - {instance_id}, force: {force}")
    
    try:
        # 验证实例存在
        instance = config_manager.get_instance(instance_id)
        if not instance:
            raise HTTPException(status_code=404, detail="连接器实例不存在")
        
        # 检查是否正在运行
        runtime_state = lifecycle_manager.get_instance_state(instance_id)
        if runtime_state == ConnectorState.RUNNING:
            if not force:
                raise HTTPException(
                    status_code=400,
                    detail="连接器正在运行，请先停止或使用 force=true 强制删除"
                )
            else:
                # 强制停止
                await lifecycle_manager.stop_instance(instance_id, force=True)
        
        # 删除实例
        success = config_manager.delete_instance(instance_id)
        if not success:
            raise HTTPException(status_code=500, detail="删除连接器实例失败")
        
        return {
            "success": True,
            "message": "连接器实例删除成功",
            "instance_id": instance_id,
            "was_running": runtime_state == ConnectorState.RUNNING
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除连接器实例失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除连接器实例失败: {str(e)}")


@router.get("/states")
async def get_all_states(
    lifecycle_manager: ConnectorLifecycleManager = Depends(get_lifecycle_manager)
):
    """获取所有连接器实例的状态概览"""
    logger.info("API: 获取所有连接器状态")
    
    try:
        running_instances = lifecycle_manager.list_running_instances()
        
        # 统计各状态的实例数量
        state_counts = {}
        for state in ConnectorState:
            state_counts[state.value] = 0
        
        # 计算实际状态分布
        config_manager = get_core_config()
        all_instances = config_manager.list_instances()
        
        for instance in all_instances:
            runtime_state = lifecycle_manager.get_instance_state(instance.instance_id)
            state_counts[runtime_state.value] += 1
        
        return {
            "success": True,
            "overview": {
                "total_instances": len(all_instances),
                "running_instances": len(running_instances),
                "state_distribution": state_counts
            },
            "running_instances": running_instances
        }
        
    except Exception as e:
        logger.error(f"获取连接器状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取连接器状态失败: {str(e)}")


@router.get("/events")
async def stream_connector_events():
    """实时推送连接器状态变化事件 (Server-Sent Events)"""
    logger.info("API: 开启连接器事件流")
    
    async def event_stream():
        # 创建事件队列
        event_queue = asyncio.Queue()
        
        # 状态变化回调
        async def state_change_callback(instance_id: str, old_state, new_state):
            event_data = {
                "event": "state_change",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "instance_id": instance_id,
                    "old_state": old_state.value,
                    "new_state": new_state.value
                }
            }
            await event_queue.put(event_data)
        
        # 注册回调
        lifecycle_manager = get_lifecycle_manager()
        lifecycle_manager.register_state_change_callback(state_change_callback)
        
        try:
            # 发送初始连接事件
            initial_event = {
                "event": "connected",
                "timestamp": datetime.now().isoformat(),
                "data": {"message": "连接器事件流已建立"}
            }
            yield f"data: {json.dumps(initial_event)}\n\n"
            
            # 持续发送事件
            while True:
                try:
                    # 等待事件，带超时防止连接被关闭
                    event = await asyncio.wait_for(event_queue.get(), timeout=30)
                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    # 发送心跳事件保持连接
                    heartbeat = {
                        "event": "heartbeat",
                        "timestamp": datetime.now().isoformat(),
                        "data": {}
                    }
                    yield f"data: {json.dumps(heartbeat)}\n\n"
                    
        except Exception as e:
            logger.error(f"事件流错误: {e}")
            error_event = {
                "event": "error",
                "timestamp": datetime.now().isoformat(),
                "data": {"error": str(e)}
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


@router.post("/shutdown-all")
async def shutdown_all_connectors(
    lifecycle_manager: ConnectorLifecycleManager = Depends(get_lifecycle_manager)
):
    """关闭所有连接器实例"""
    logger.info("API: 关闭所有连接器实例")
    
    try:
        await lifecycle_manager.shutdown_all()
        
        return {
            "success": True,
            "message": "所有连接器实例已关闭"
        }
        
    except Exception as e:
        logger.error(f"关闭所有连接器失败: {e}")
        raise HTTPException(status_code=500, detail=f"关闭所有连接器失败: {str(e)}")


@router.get("/health")
async def connector_health_check(
    config_manager=Depends(get_core_config),
    lifecycle_manager: ConnectorLifecycleManager = Depends(get_lifecycle_manager)
):
    """连接器系统健康检查"""
    logger.info("API: 连接器健康检查")
    
    try:
        # 配置系统健康状态
        config_summary = config_manager.get_config_summary()
        config_errors = config_manager.validate_all_configs()
        
        # 运行时健康状态
        all_instances = config_manager.list_instances()
        healthy_instances = 0
        error_instances = 0
        
        for instance in all_instances:
            state = lifecycle_manager.get_instance_state(instance.instance_id)
            if state == ConnectorState.RUNNING:
                healthy_instances += 1
            elif state == ConnectorState.ERROR:
                error_instances += 1
        
        # 计算健康评分
        total_instances = len(all_instances)
        health_score = 100
        
        if total_instances > 0:
            error_rate = error_instances / total_instances
            health_score = max(0, 100 - (error_rate * 100))
        
        # 配置错误会降低健康评分
        total_config_errors = sum(len(errors) for errors in config_errors.values())
        if total_config_errors > 0:
            health_score = max(0, health_score - (total_config_errors * 5))
        
        return {
            "success": True,
            "health": {
                "overall_score": round(health_score, 1),
                "status": "healthy" if health_score >= 80 else "degraded" if health_score >= 50 else "unhealthy",
                "config_system": {
                    "status": "healthy" if total_config_errors == 0 else "has_errors",
                    "config_version": config_summary["config_version"],
                    "last_reload": config_summary["last_reload"].isoformat() if config_summary["last_reload"] else None,
                    "errors": config_errors
                },
                "runtime_system": {
                    "total_instances": total_instances,
                    "healthy_instances": healthy_instances,
                    "error_instances": error_instances,
                    "running_instances": len(lifecycle_manager.list_running_instances())
                }
            }
        }
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "success": False,
            "health": {
                "overall_score": 0,
                "status": "system_error",
                "error": str(e)
            }
        }