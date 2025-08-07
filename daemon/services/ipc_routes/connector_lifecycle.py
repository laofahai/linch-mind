"""
连接器生命周期管理路由

处理连接器的创建、启动、停止、删除等生命周期操作
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..ipc_router import IPCRouter
from ..ipc_protocol import (
    IPCRequest, IPCResponse, IPCErrorCode,
    connector_not_found_response, invalid_request_response, 
    internal_error_response, resource_not_found_response
)
from models.connector_status import ConnectorStatus, ConnectorRunningState

logger = logging.getLogger(__name__)


def create_connector_lifecycle_router() -> IPCRouter:
    """创建连接器生命周期管理路由 - 使用新状态模型"""
    router = IPCRouter(prefix="/connector-lifecycle")
    
    # ==================== 基础CRUD操作 ====================
    
    @router.get("/connectors")
    async def get_connectors(request: IPCRequest) -> IPCResponse:
        """获取连接器列表"""
        try:
            from daemon.services.connectors.connector_manager import get_connector_manager
            
            manager = get_connector_manager()
            connectors = manager.list_connectors()
            
            # 转换为UI端期待的格式 (ConnectorInfo)
            connector_infos = []
            for conn in connectors:
                # conn 是字典，需要使用字典访问方式
                # 状态映射：数据库的status字段 -> UI的state字段
                status = conn["status"]
                # 状态映射逻辑
                if status == "running":
                    ui_state = "running"
                elif status == "error":
                    ui_state = "error"
                elif status == "stopping":
                    ui_state = "stopping"
                elif status == "starting":
                    ui_state = "enabled"  # 启动中显示为已启用
                elif status == "stopped":
                    ui_state = "configured"
                else:
                    # enabled 状态映射为configured（已配置但未运行）
                    ui_state = "configured"
                
                connector_info = {
                    "connector_id": conn["connector_id"],
                    "display_name": conn["name"],
                    "state": ui_state,
                    "enabled": conn["enabled"],
                    "process_id": conn["pid"],
                    "data_count": conn["data_count"] or 0,
                    "error_message": conn["error_message"],
                    "config": {}  # 默认空配置，实际配置需要单独获取
                }
                connector_infos.append(connector_info)
            
            return IPCResponse.success_response(
                data={
                    "connectors": connector_infos,
                    "total": len(connector_infos)
                },
                request_id=request.request_id
            )
            
        except Exception as e:
            logger.error(f"获取连接器列表失败: {e}")
            return internal_error_response(
                f"Failed to get connectors: {str(e)}",
                {"operation": "get_connectors"}
            )
    
    @router.post("/connectors")
    async def create_connector(request: IPCRequest) -> IPCResponse:
        """创建连接器实例"""
        try:
            data = request.data
            if not data:
                return invalid_request_response(
                    "Request data is required",
                    {"required_fields": ["connector_id", "display_name"]}
                )
            
            connector_id = data.get("connector_id")
            display_name = data.get("display_name")
            config = data.get("config", {})
            
            if not connector_id:
                return invalid_request_response(
                    "connector_id is required",
                    {"missing_field": "connector_id"}
                )
            
            if not display_name:
                return invalid_request_response(
                    "display_name is required",
                    {"missing_field": "display_name"}
                )
            
            from daemon.services.connectors.connector_manager import get_connector_manager
            
            manager = get_connector_manager()
            
            # 创建连接器实例
            success = await manager.create_connector_instance(
                connector_id=connector_id,
                display_name=display_name,
                config=config
            )
            
            if success:
                # 创建状态对象
                status = ConnectorStatus(
                    connector_id=connector_id,
                    display_name=display_name,
                    enabled=True,
                    running_state=ConnectorRunningState.STOPPED
                )
                
                return IPCResponse.success_response(
                    data={
                        "connector": status.to_dict(),
                        "message": f"连接器 '{display_name}' 创建成功"
                    },
                    request_id=request.request_id
                )
            else:
                return IPCResponse.error_response(
                    IPCErrorCode.CONNECTOR_CONFIG_INVALID,
                    "连接器创建失败",
                    {"connector_id": connector_id},
                    request_id=request.request_id
                )
            
        except ValueError as e:
            logger.error(f"连接器配置错误: {e}")
            return invalid_request_response(
                f"连接器配置错误: {str(e)}",
                {"connector_id": connector_id}
            )
        except Exception as e:
            logger.error(f"创建连接器失败: {e}")
            return internal_error_response(
                f"创建连接器时发生错误: {str(e)}",
                {"operation": "create_connector"}
            )

    @router.delete("/connectors/{connector_id}")
    async def delete_connector(request: IPCRequest) -> IPCResponse:
        """删除连接器实例"""
        connector_id = request.path_params.get("connector_id")
        if not connector_id:
            return invalid_request_response(
                "Missing connector_id in path",
                {"required_param": "connector_id"}
            )
        
        force = request.query_params.get("force", False)
        if isinstance(force, str):
            force = force.lower() == "true"
        
        try:
            from daemon.services.connectors.connector_manager import get_connector_manager
            
            manager = get_connector_manager()
            
            # 执行删除操作
            success = await manager.delete_connector(connector_id, force=force)
            
            if success:
                return IPCResponse.success_response(
                    data={
                        "success": True,
                        "connector_id": connector_id,
                        "message": f"连接器 '{connector_id}' 删除成功",
                        "state": "uninstalling"  # 删除后的状态
                    },
                    request_id=request.request_id
                )
            else:
                return IPCResponse.error_response(
                    IPCErrorCode.CONNECTOR_NOT_FOUND,
                    f"连接器 '{connector_id}' 不存在或删除失败",
                    {"connector_id": connector_id},
                    request_id=request.request_id
                )
            
        except Exception as e:
            logger.error(f"删除连接器 {connector_id} 失败: {e}")
            return internal_error_response(
                f"Failed to delete connector: {str(e)}",
                {"connector_id": connector_id, "operation": "delete_connector"}
            )
    
    # ==================== 启动/停止/重启操作 ====================
    
    @router.post("/connectors/{connector_id}/actions/start")
    async def start_connector(request: IPCRequest) -> IPCResponse:
        """启动连接器"""
        connector_id = request.path_params.get("connector_id")
        if not connector_id:
            return invalid_request_response(
                "Missing connector_id in path",
                {"required_param": "connector_id"}
            )
        
        try:
            from daemon.services.connectors.connector_manager import get_connector_manager
            
            manager = get_connector_manager()
            result = await manager.start_connector(connector_id)
            
            if result:
                return IPCResponse.success_response(
                    data={
                        "success": True,
                        "connector_id": connector_id,
                        "state": "running",
                        "message": f"连接器 '{connector_id}' 启动成功"
                    },
                    request_id=request.request_id
                )
            else:
                return IPCResponse.error_response(
                    IPCErrorCode.CONNECTOR_START_FAILED,
                    f"Failed to start connector '{connector_id}'",
                    {"connector_id": connector_id},
                    request_id=request.request_id
                )
            
        except Exception as e:
            logger.error(f"启动连接器 {connector_id} 失败: {e}")
            return internal_error_response(
                f"Failed to start connector: {str(e)}",
                {"connector_id": connector_id, "operation": "start_connector"}
            )
    
    @router.post("/connectors/{connector_id}/actions/stop")
    async def stop_connector(request: IPCRequest) -> IPCResponse:
        """停止连接器"""
        connector_id = request.path_params.get("connector_id")
        if not connector_id:
            return invalid_request_response(
                "Missing connector_id in path",
                {"required_param": "connector_id"}
            )
        
        try:
            from daemon.services.connectors.connector_manager import get_connector_manager
            
            manager = get_connector_manager()
            result = await manager.stop_connector(connector_id)
            
            if result:
                return IPCResponse.success_response(
                    data={
                        "success": True,
                        "connector_id": connector_id,
                        "state": "configured",
                        "message": f"连接器 '{connector_id}' 停止成功"
                    },
                    request_id=request.request_id
                )
            else:
                return IPCResponse.error_response(
                    IPCErrorCode.CONNECTOR_STOP_FAILED,
                    f"Failed to stop connector '{connector_id}'",
                    {"connector_id": connector_id},
                    request_id=request.request_id
                )
            
        except Exception as e:
            logger.error(f"停止连接器 {connector_id} 失败: {e}")
            return internal_error_response(
                f"Failed to stop connector: {str(e)}",
                {"connector_id": connector_id, "operation": "stop_connector"}
            )
    
    @router.post("/connectors/{connector_id}/actions/restart")
    async def restart_connector(request: IPCRequest) -> IPCResponse:
        """重启连接器"""
        connector_id = request.path_params.get("connector_id")
        if not connector_id:
            return invalid_request_response(
                "Missing connector_id in path",
                {"required_param": "connector_id"}
            )
        
        try:
            from daemon.services.connectors.connector_manager import get_connector_manager
            
            manager = get_connector_manager()
            result = await manager.restart_connector(connector_id)
            
            if result:
                return IPCResponse.success_response(
                    data={
                        "success": True,
                        "connector_id": connector_id,
                        "state": "running",
                        "message": f"连接器 '{connector_id}' 重启成功"
                    },
                    request_id=request.request_id
                )
            else:
                return IPCResponse.error_response(
                    IPCErrorCode.CONNECTOR_START_FAILED,
                    f"Failed to restart connector '{connector_id}'",
                    {"connector_id": connector_id},
                    request_id=request.request_id
                )
            
        except Exception as e:
            logger.error(f"重启连接器 {connector_id} 失败: {e}")
            return internal_error_response(
                f"Failed to restart connector: {str(e)}",
                {"connector_id": connector_id, "operation": "restart_connector"}
            )
    
    # ==================== 状态管理和心跳 ====================
    
    @router.put("/connectors/{connector_id}/enabled")
    async def toggle_connector_enabled(request: IPCRequest) -> IPCResponse:
        """切换连接器启用/禁用状态"""
        connector_id = request.path_params.get("connector_id")
        if not connector_id:
            return invalid_request_response(
                "Missing connector_id in path",
                {"required_param": "connector_id"}
            )
        
        if not request.data or "enabled" not in request.data:
            return invalid_request_response(
                "Missing 'enabled' field in request data",
                {"required_field": "enabled"}
            )
        
        enabled = request.data["enabled"]
        if not isinstance(enabled, bool):
            return invalid_request_response(
                "'enabled' field must be boolean",
                {"provided_type": type(enabled).__name__}
            )
        
        try:
            from daemon.services.database_service import get_database_service
            
            with get_database_service().get_session() as session:
                from daemon.models.database_models import Connector
                
                connector = session.query(Connector).filter_by(connector_id=connector_id).first()
                if not connector:
                    return connector_not_found_response(connector_id)
                
                connector.enabled = enabled
                session.commit()
                
                return IPCResponse.success_response(
                    data={
                        "connector_id": connector_id,
                        "enabled": enabled,
                        "message": f"连接器 '{connector_id}' {'启用' if enabled else '禁用'}成功"
                    },
                    request_id=request.request_id
                )
            
        except Exception as e:
            logger.error(f"切换连接器启用状态失败 {connector_id}: {e}")
            return internal_error_response(
                f"Failed to toggle connector enabled status: {str(e)}",
                {"connector_id": connector_id, "operation": "toggle_enabled"}
            )
    
    @router.post("/heartbeat")
    async def connector_heartbeat(request: IPCRequest) -> IPCResponse:
        """接收连接器心跳"""
        try:
            data = request.data
            if not data:
                return invalid_request_response(
                    "Missing heartbeat data",
                    {"required_fields": ["connector_id", "process_id"]}
                )
            
            connector_id = data.get("connector_id")
            process_id = data.get("process_id")
            running_state = data.get("running_state", "running")
            data_count = data.get("data_count", 0)
            
            if not connector_id:
                return invalid_request_response(
                    "Missing connector_id",
                    {"missing_field": "connector_id"}
                )
            
            # 更新数据库中的心跳信息
            from daemon.services.database_service import get_database_service
            with get_database_service().get_session() as session:
                from daemon.models.database_models import Connector
                
                connector = session.query(Connector).filter_by(connector_id=connector_id).first()
                if connector:
                    connector.last_heartbeat = datetime.now(timezone.utc)
                    connector.process_id = process_id
                    connector.status = running_state
                    connector.data_count = data_count
                    session.commit()
                    
                    return IPCResponse.success_response(
                        data={"heartbeat_received": True},
                        request_id=request.request_id
                    )
                else:
                    return connector_not_found_response(connector_id)
            
        except Exception as e:
            logger.error(f"处理连接器心跳失败: {e}")
            return internal_error_response(
                f"处理心跳失败: {str(e)}",
                {"operation": "process_heartbeat"}
            )
    
    @router.post("/connectors/{connector_id}/status")
    async def update_connector_status(request: IPCRequest) -> IPCResponse:
        """更新连接器状态"""
        try:
            connector_id = request.path_params.get("connector_id")
            if not connector_id:
                return invalid_request_response(
                    "Missing connector_id in path",
                    {"required_param": "connector_id"}
                )
            
            data = request.data
            if not data:
                return invalid_request_response(
                    "Missing status data",
                    {"required_fields": ["running_state"]}
                )
            
            # 更新数据库中的连接器状态
            from daemon.services.database_service import get_database_service
            with get_database_service().get_session() as session:
                from daemon.models.database_models import Connector
                
                connector = session.query(Connector).filter_by(connector_id=connector_id).first()
                if connector:
                    # 更新所有提供的字段
                    if "running_state" in data:
                        connector.status = data["running_state"]
                    if "enabled" in data:
                        connector.enabled = data["enabled"]
                    if "process_id" in data:
                        connector.process_id = data["process_id"]
                    if "data_count" in data:
                        connector.data_count = data["data_count"]
                    if "error_message" in data:
                        connector.error_message = data["error_message"]
                    
                    connector.updated_at = datetime.now(timezone.utc)
                    session.commit()
                    
                    # 创建状态响应
                    status = ConnectorStatus(
                        connector_id=connector_id,
                        display_name=connector.name,
                        enabled=connector.enabled,
                        running_state=ConnectorRunningState.from_string(connector.status)
                    )
                    
                    return IPCResponse.success_response(
                        data={"connector_status": status.to_dict()},
                        request_id=request.request_id
                    )
                else:
                    return connector_not_found_response(connector_id)
            
        except Exception as e:
            logger.error(f"更新连接器状态失败: {e}")
            return internal_error_response(
                f"更新状态失败: {str(e)}",
                {"operation": "update_status"}
            )
    
    # ==================== 发现和扫描操作 ====================
    
    @router.get("/discovery")
    async def discover_connectors(request: IPCRequest) -> IPCResponse:
        """发现可用的连接器"""
        try:
            logger.info("发现本地连接器...")
            from daemon.services.connectors.connector_manager import get_connector_manager
            from pathlib import Path
            from daemon.config.core_config import get_connector_config
            
            manager = get_connector_manager()
            connector_config = get_connector_config()
            connectors_dir = Path(connector_config.config_dir)
            connectors = manager.scan_directory_for_connectors(str(connectors_dir))
            
            return IPCResponse.success_response(
                data={
                    "available_connectors": connectors,
                    "count": len(connectors),
                    "message": f"发现 {len(connectors)} 个可用连接器"
                },
                request_id=request.request_id
            )
        except Exception as e:
            logger.error(f"连接器发现失败: {e}")
            return internal_error_response(
                f"Connector discovery failed: {str(e)}",
                {"operation": "discover_connectors"}
            )
    
    @router.post("/dev/scan-directory")
    async def scan_connector_directory(request: IPCRequest) -> IPCResponse:
        """扫描指定目录寻找连接器 (开发用)"""
        try:
            data = request.data
            if not data:
                return invalid_request_response(
                    "Missing request data",
                    {"required_fields": ["directory_path"]}
                )
            
            directory_path = data.get("directory_path")
            if not directory_path:
                return invalid_request_response(
                    "Missing directory_path field",
                    {"missing_field": "directory_path"}
                )
            
            from daemon.services.connectors.connector_manager import get_connector_manager
            from pathlib import Path
            
            # 验证目录路径
            path = Path(directory_path)
            if not path.exists():
                return IPCResponse.error_response(
                    IPCErrorCode.RESOURCE_NOT_FOUND,
                    f"Directory not found: {directory_path}",
                    {"directory_path": directory_path},
                    request_id=request.request_id
                )
            
            if not path.is_dir():
                return invalid_request_response(
                    f"Path is not a directory: {directory_path}",
                    {"directory_path": directory_path}
                )
            
            manager = get_connector_manager()
            connectors = manager.scan_directory_for_connectors(str(path))
            
            return IPCResponse.success_response(
                data={
                    "success": True,
                    "connectors": connectors,
                    "count": len(connectors),
                    "directory_path": directory_path,
                    "message": f"扫描目录完成，发现 {len(connectors)} 个连接器"
                },
                request_id=request.request_id
            )
            
        except Exception as e:
            logger.error(f"扫描目录失败: {e}")
            return internal_error_response(
                f"Directory scan failed: {str(e)}",
                {"operation": "scan_directory", "directory_path": data.get("directory_path", "unknown")}
            )
    
    return router