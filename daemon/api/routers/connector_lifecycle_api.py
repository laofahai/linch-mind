#!/usr/bin/env python3
"""
连接器生命周期API路由 - 匹配Flutter UI期望的API
基于新的连接器管理器实现
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from services.connectors.connector_manager import get_connector_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/connector-lifecycle", tags=["connector-lifecycle"])


@router.get("/discovery")
async def discover_connectors():
    """发现可用的连接器 - 不再区分类型"""
    try:
        from services.database_service import get_database_service

        db_service = get_database_service()

        # 获取已注册的连接器（从数据库）
        registered_connectors = []
        with db_service.get_session() as session:
            from models.database_models import Connector

            connectors = session.query(Connector).all()

            for conn in connectors:
                config = conn.config or {}
                registered_connectors.append(
                    {
                        "connector_id": conn.connector_id,
                        "name": conn.name,
                        "display_name": conn.name,
                        "description": conn.description or "用户添加的连接器",
                        "category": "registered",
                        "version": config.get("version", "1.0.0"),
                        "author": config.get("author", "用户"),
                        "license": config.get("license", "MIT"),
                        "auto_discovery": False,
                        "hot_config_reload": True,
                        "health_check": True,
                        "entry_point": config.get("entry_point", "main.py"),
                        "dependencies": config.get("dependencies", []),
                        "permissions": config.get("permissions", []),
                        "config_schema": config.get("config_schema", {}),
                        "is_registered": True,
                    }
                )

        # 添加官方可用连接器（硬编码的可安装连接器）
        official_connectors = [
            {
                "connector_id": "filesystem",
                "name": "FileSystem Connector",
                "display_name": "文件系统连接器",
                "description": "监控文件系统变化的连接器",
                "category": "official",
                "version": "1.0.0",
                "author": "Linch Mind",
                "license": "MIT",
                "auto_discovery": False,
                "hot_config_reload": True,
                "health_check": True,
                "entry_point": "main.py",
                "dependencies": [],
                "permissions": ["file_system_read", "file_system_watch"],
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "watch_paths": {"type": "array", "items": {"type": "string"}},
                        "supported_extensions": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
                "is_registered": any(
                    c["connector_id"] == "filesystem" for c in registered_connectors
                ),
            },
            {
                "connector_id": "clipboard",
                "name": "Clipboard Connector",
                "display_name": "剪贴板连接器",
                "description": "监控剪贴板内容变化的连接器",
                "category": "official",
                "version": "1.0.0",
                "author": "Linch Mind",
                "license": "MIT",
                "auto_discovery": False,
                "hot_config_reload": True,
                "health_check": True,
                "entry_point": "main.py",
                "dependencies": [],
                "permissions": ["clipboard_read"],
                "config_schema": {"type": "object", "properties": {}},
                "is_registered": any(
                    c["connector_id"] == "clipboard" for c in registered_connectors
                ),
            },
        ]

        # 合并所有连接器，已注册的优先显示
        all_connectors = registered_connectors + [
            c for c in official_connectors if not c["is_registered"]
        ]

        return {
            "success": True,
            "data": {"connectors": all_connectors, "total": len(all_connectors)},
            "message": f"Found {len(all_connectors)} connectors ({len(registered_connectors)} registered, {len(official_connectors)} available)",
        }
    except Exception as e:
        logger.error(f"Failed to discover connectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collectors")
async def get_connectors(connector_id: str = None, state: str = None):
    """获取连接器列表 - 基于数据库驱动"""
    try:
        # 直接从数据库获取Connector对象
        from services.database_service import get_database_service

        db_service = get_database_service()

        with db_service.get_session() as session:
            from models.database_models import Connector

            query = session.query(Connector)

            # 应用过滤器
            if connector_id is not None:
                query = query.filter(Connector.connector_id == connector_id)
            if state is not None:
                # 需要反向映射state到数据库status
                db_status = _map_state_to_status(state)
                if db_status:
                    query = query.filter(Connector.status == db_status)

            connectors = query.all()

            # 使用统一的转换函数
            collectors = [_convert_connector_to_collector(conn) for conn in connectors]

        return {
            "success": True,
            "data": {"collectors": collectors, "total": len(collectors)},
            "message": f"Found {len(collectors)} connectors",
        }
    except Exception as e:
        logger.error(f"Failed to get connectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collectors/{collector_id}")
async def get_connector(collector_id: str):
    """获取连接器详情"""
    try:
        manager = get_connector_manager()
        connectors = manager.list_connectors()

        # 查找指定的连接器
        connector = next(
            (c for c in connectors if c["connector_id"] == collector_id), None
        )
        if not connector:
            raise HTTPException(
                status_code=404, detail=f"Connector {collector_id} not found"
            )

        collector = {
            "collector_id": connector["connector_id"],
            "display_name": connector["name"],
            "config": {},
            "state": _map_status_to_state(connector["status"]),
            "enabled": True,
            "auto_start": True,
            "process_id": connector.get("pid"),
            "last_heartbeat": None,
            "data_count": 0,
            "error_message": None,
            "created_at": None,
            "updated_at": None,
        }

        return {
            "success": True,
            "data": {"collector": collector},
            "message": f"Retrieved connector {collector_id}",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get connector {collector_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collectors/{collector_id}/start")
async def start_connector(collector_id: str):
    """启动连接器"""
    try:
        manager = get_connector_manager()
        success = await manager.start_connector(collector_id)

        if not success:
            raise HTTPException(
                status_code=400, detail=f"Failed to start connector: {collector_id}"
            )

        return {
            "success": True,
            "data": {"collector_id": collector_id, "state": "running"},
            "message": f"Connector {collector_id} started successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start connector {collector_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collectors/{collector_id}/stop")
async def stop_connector(collector_id: str, force: bool = False):
    """停止连接器"""
    try:
        manager = get_connector_manager()
        success = await manager.stop_connector(collector_id)

        if not success:
            raise HTTPException(
                status_code=400, detail=f"Failed to stop connector: {collector_id}"
            )

        return {
            "success": True,
            "data": {"collector_id": collector_id, "state": "stopped"},
            "message": f"Connector {collector_id} stopped successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop connector {collector_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collectors/{collector_id}/restart")
async def restart_connector(collector_id: str):
    """重启连接器"""
    try:
        manager = get_connector_manager()

        # 先停止再启动
        await manager.stop_connector(collector_id)
        success = await manager.start_connector(collector_id)

        if not success:
            raise HTTPException(
                status_code=400, detail=f"Failed to restart connector: {collector_id}"
            )

        return {
            "success": True,
            "data": {"collector_id": collector_id, "state": "running"},
            "message": f"Connector {collector_id} restarted successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to restart connector {collector_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/collectors/{collector_id}")
async def delete_connector(collector_id: str, force: bool = False):
    """删除连接器 - 暂未实现"""
    raise HTTPException(
        status_code=501, detail="Delete functionality not implemented yet"
    )


@router.get("/states")
async def get_states_overview():
    """获取所有连接器状态概览"""
    try:
        manager = get_connector_manager()
        connectors = manager.list_connectors()

        # 统计各种状态
        state_counts = {}
        for connector in connectors:
            state = _map_status_to_state(connector["status"])
            state_counts[state] = state_counts.get(state, 0) + 1

        return {
            "success": True,
            "data": {
                "total_collectors": len(connectors),
                "state_counts": state_counts,
                "summary": f"Total: {len(connectors)} connectors",
            },
            "message": "States overview retrieved successfully",
        }
    except Exception as e:
        logger.error(f"Failed to get states overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scan-directory")
async def scan_connector_directory(request: Dict[str, Any]):
    """扫描指定目录寻找连接器"""
    try:
        directory_path = request.get("directory_path")
        if not directory_path:
            raise HTTPException(status_code=400, detail="directory_path is required")

        manager = get_connector_manager()
        discovered_connectors = manager.scan_directory_for_connectors(directory_path)

        # 转换为UI期望的格式
        connector_definitions = []
        for connector in discovered_connectors:
            connector_def = {
                "connector_id": connector["connector_id"],
                "name": connector["name"],
                "display_name": connector["name"],
                "description": connector["description"],
                "category": "custom",
                "version": connector.get("version", "1.0.0"),
                "author": "User",
                "license": "MIT",
                "auto_discovery": False,
                "hot_config_reload": True,
                "health_check": True,
                "entry_point": connector.get("entry_point", "main.py"),
                "dependencies": [],
                "permissions": ["file_system_read", "file_system_watch"],
                "config_schema": {"type": "object", "properties": {}},
                "path": connector["path"],
                "is_registered": connector.get("is_registered", False),
            }
            connector_definitions.append(connector_def)

        return {
            "success": True,
            "data": {
                "connectors": connector_definitions,
                "total": len(connector_definitions),
            },
            "message": f"Scanned directory and found {len(connector_definitions)} connectors",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to scan directory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collectors")
async def create_connector(request: Dict[str, Any]):
    """创建连接器 - 简化版本"""
    try:
        connector_id = request.get("connector_id")
        display_name = request.get("display_name")
        config = request.get("config", {})
        auto_start = request.get("auto_start", False)

        if not connector_id or not display_name:
            raise HTTPException(
                status_code=400, detail="connector_id and display_name are required"
            )

        from services.database_service import get_database_service

        db_service = get_database_service()

        # 检查连接器是否已存在
        with db_service.get_session() as session:
            from models.database_models import Connector

            existing = (
                session.query(Connector).filter_by(connector_id=connector_id).first()
            )
            if existing:
                raise HTTPException(
                    status_code=409, detail=f"Connector {connector_id} already exists"
                )

        # 为官方连接器设置默认路径
        if connector_id in ["filesystem", "clipboard"]:
            config["path"] = f"../connectors/official/{connector_id}"
            config["entry_point"] = "main.py"
            config["executable_path"] = f"../connectors/official/{connector_id}/main.py"

        # 直接创建数据库记录
        with db_service.get_session() as session:
            connector = Connector(
                connector_id=connector_id,
                name=display_name,
                description=f"{display_name} - 通过UI创建",
                config=config,
                status="configured",
                enabled=True,
                auto_start=auto_start,
            )
            session.add(connector)
            session.commit()

            # 如果需要自动启动
            if auto_start:
                manager = get_connector_manager()
                success = await manager.start_connector(connector_id)
                if success:
                    connector.status = "running"
                    session.commit()

        return {
            "success": True,
            "data": {
                "collector_id": connector_id,
                "display_name": display_name,
                "state": "running" if auto_start else "configured",
            },
            "message": f"Connector {display_name} created successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create connector: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def get_health_check():
    """系统健康检查"""
    try:
        manager = get_connector_manager()

        # 执行健康检查
        manager.health_check_all_connectors()

        # 获取最新状态
        connectors = manager.list_connectors()

        running_count = sum(1 for c in connectors if c["status"] == "running")
        error_count = sum(1 for c in connectors if c["status"] == "error")

        # 判断系统健康状态
        system_status = "healthy"
        if error_count > 0:
            system_status = "degraded" if running_count > 0 else "unhealthy"

        return {
            "success": True,
            "data": {
                "system_status": system_status,
                "total_connectors": len(connectors),
                "running_connectors": running_count,
                "error_connectors": error_count,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            "message": f"System is {system_status}",
        }
    except Exception as e:
        logger.error(f"Failed to get health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 统一的状态枚举定义 - 匹配UI ConnectorState
CONNECTOR_STATES = {
    "available": "available",  # 可用但未安装
    "installed": "installed",  # 已安装但未配置
    "configured": "configured",  # 已配置但未启用
    "enabled": "enabled",  # 已启用但未运行
    "running": "running",  # 正在运行
    "error": "error",  # 错误状态
    "stopping": "stopping",  # 正在停止
    "updating": "updating",  # 正在更新
    "uninstalling": "uninstalling",  # 正在卸载
}


def _map_status_to_state(status: str) -> str:
    """将数据库状态映射到UI期望的状态"""
    # 数据库状态到UI状态的精确映射
    status_mapping = {
        "configured": "configured",  # 已配置但未启用
        "running": "running",  # 正在运行
        "error": "error",  # 错误状态
        "stopping": "stopping",  # 正在停止
        "stopped": "configured",  # 已停止=已配置状态
    }
    return status_mapping.get(status, "configured")


def _map_state_to_status(state: str) -> str:
    """将UI状态反向映射到数据库状态"""
    # UI状态到数据库状态的反向映射
    state_mapping = {
        "configured": "configured",  # 已配置
        "running": "running",  # 正在运行
        "error": "error",  # 错误状态
        "stopping": "stopping",  # 正在停止
        "enabled": "configured",  # 已启用=已配置
        "stopped": "configured",  # 已停止=已配置
    }
    return state_mapping.get(state, "configured")


def _convert_connector_to_collector(connector_db) -> Dict[str, Any]:
    """将数据库Connector模型转换为UI期望的CollectorInfo格式"""
    return {
        "collector_id": connector_db.connector_id,
        "display_name": connector_db.name,
        "config": connector_db.config or {},
        "state": _map_status_to_state(connector_db.status),
        "enabled": connector_db.enabled if hasattr(connector_db, "enabled") else True,
        "auto_start": (
            connector_db.auto_start if hasattr(connector_db, "auto_start") else True
        ),
        "process_id": connector_db.process_id,
        "last_heartbeat": (
            connector_db.last_heartbeat.isoformat()
            if getattr(connector_db, "last_heartbeat", None)
            else None
        ),
        "data_count": getattr(connector_db, "data_count", 0),
        "error_message": getattr(connector_db, "error_message", None),
        "created_at": (
            connector_db.created_at.isoformat() if connector_db.created_at else None
        ),
        "updated_at": (
            connector_db.updated_at.isoformat() if connector_db.updated_at else None
        ),
    }
