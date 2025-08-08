"""
连接器生命周期管理API - 纯IPC实现
"""

import logging

from services.connectors.connector_manager import get_connector_manager
from services.ipc_router import IPCRequest, IPCResponse

logger = logging.getLogger(__name__)


async def discover_connectors(request: IPCRequest) -> IPCResponse:
    """发现可用的连接器"""
    try:
        logger.info("发现本地连接器...")
        manager = get_connector_manager()
        # 使用scan_directory_for_connectors替代discover_local_connectors
        from pathlib import Path

        from config.core_config import get_connector_config

        connector_config = get_connector_config()
        connectors_dir = Path(connector_config.config_dir)
        connectors = manager.scan_directory_for_connectors(str(connectors_dir))

        return IPCResponse(
            success=True,
            data={"connectors": connectors},
            message=f"发现 {len(connectors)} 个本地连接器",
        )
    except Exception as e:
        logger.error(f"连接器发现失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})


async def list_collectors(request: IPCRequest) -> IPCResponse:
    """列出所有连接器实例"""
    try:
        logger.info("获取连接器列表...")
        manager = get_connector_manager()
        connectors = manager.list_connectors()
        return IPCResponse(
            success=True,
            data={"collectors": connectors},
            message=f"找到 {len(connectors)} 个连接器实例",
        )
    except Exception as e:
        logger.error(f"获取连接器列表失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})


async def get_collector_status(request: IPCRequest) -> IPCResponse:
    """获取连接器状态"""
    collector_id = request.path_params.get("collector_id")
    if not collector_id:
        return IPCResponse(status_code=400, data={"error": "Missing collector_id"})

    try:
        logger.info(f"获取连接器 {collector_id} 状态...")
        manager = get_connector_manager()
        status = manager.get_connector_status(collector_id)
        if not status:
            return IPCResponse(
                status_code=404, data={"error": f"连接器 {collector_id} 不存在"}
            )
        return IPCResponse(
            success=True,
            data={"collector": status},
            message=f"成功获取 {collector_id} 状态",
        )
    except Exception as e:
        logger.error(f"获取连接器状态失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})


async def start_collector(request: IPCRequest) -> IPCResponse:
    """启动连接器"""
    collector_id = request.path_params.get("collector_id")
    if not collector_id:
        return IPCResponse(status_code=400, data={"error": "Missing collector_id"})

    try:
        logger.info(f"启动连接器 {collector_id}...")
        manager = get_connector_manager()
        success = await manager.start_connector(collector_id)
        return IPCResponse(
            success=success,
            message=f"{'成功' if success else '失败'}启动连接器 {collector_id}",
        )
    except Exception as e:
        logger.error(f"启动连接器失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})


async def stop_collector(request: IPCRequest) -> IPCResponse:
    """停止连接器"""
    collector_id = request.path_params.get("collector_id")
    if not collector_id:
        return IPCResponse(status_code=400, data={"error": "Missing collector_id"})

    try:
        logger.info(f"停止连接器 {collector_id}...")
        manager = get_connector_manager()
        success = await manager.stop_connector(collector_id)
        return IPCResponse(
            success=success,
            message=f"{'成功' if success else '失败'}停止连接器 {collector_id}",
        )
    except Exception as e:
        logger.error(f"停止连接器失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})


async def restart_collector(request: IPCRequest) -> IPCResponse:
    """重启连接器"""
    collector_id = request.path_params.get("collector_id")
    if not collector_id:
        return IPCResponse(status_code=400, data={"error": "Missing collector_id"})

    try:
        logger.info(f"重启连接器 {collector_id}...")
        manager = get_connector_manager()
        success = await manager.restart_connector(collector_id)
        return IPCResponse(
            success=success,
            message=f"{'成功' if success else '失败'}重启连接器 {collector_id}",
        )
    except Exception as e:
        logger.error(f"重启连接器失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})


async def install_connector(request: IPCRequest) -> IPCResponse:
    """安装连接器"""
    body = await request.json()
    connector_id = body.get("connector_id")
    source = body.get("source")
    config = body.get("config")

    if not connector_id:
        return IPCResponse(status_code=400, data={"error": "Missing connector_id"})

    try:
        logger.info(f"安装连接器 {connector_id}...")
        manager = get_connector_manager()
        success = await manager.install_connector(connector_id, source, config)
        return IPCResponse(
            success=success,
            message=f"{'成功' if success else '失败'}安装连接器 {connector_id}",
        )
    except Exception as e:
        logger.error(f"安装连接器失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})


async def system_health(request: IPCRequest) -> IPCResponse:
    """系统健康检查"""
    try:
        logger.info("执行系统健康检查...")
        manager = get_connector_manager()
        connectors = manager.list_connectors()
        running_count = len([c for c in connectors if c.get("status") == "running"])
        total_count = len(connectors)

        health_data = {
            "total_connectors": total_count,
            "running_connectors": running_count,
            "healthy": running_count > 0,
            "timestamp": manager.get_current_timestamp(),
        }

        return IPCResponse(
            success=True,
            data=health_data,
            message=f"系统健康，{running_count}/{total_count} 个连接器运行中",
        )
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})


# 注意：这个文件现在只包含处理函数。
# 路由注册已移至 services/ipc_routes.py
