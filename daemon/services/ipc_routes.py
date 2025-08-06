"""
IPC路由定义 - 将现有FastAPI路由转换为纯IPC处理
"""

import logging
from typing import Any, Dict, List, Optional

from .ipc_router import IPCRouter, IPCRequest, IPCResponse

logger = logging.getLogger(__name__)


def create_health_router() -> IPCRouter:
    """创建健康检查路由"""
    router = IPCRouter()
    
    @router.get("/")
    async def root(request: IPCRequest) -> IPCResponse:
        """根路径"""
        return IPCResponse(
            data={
                "message": "Linch Mind IPC Service",
                "version": "1.0.0",
                "status": "running"
            }
        )
    
    @router.get("/health")
    async def health_check(request: IPCRequest) -> IPCResponse:
        """健康检查"""
        return IPCResponse(
            data={
                "status": "healthy",
                "timestamp": __import__('datetime').datetime.now().isoformat(),
                "service": "linch-mind-daemon"
            }
        )
    
    @router.get("/server/info")
    async def server_info(request: IPCRequest) -> IPCResponse:
        """服务器信息"""
        import os
        import platform
        
        return IPCResponse(
            data={
                "pid": os.getpid(),
                "platform": platform.system(),
                "python_version": platform.python_version(),
                "architecture": platform.machine(),
                "communication": "IPC"
            }
        )
    
    return router


def create_connector_lifecycle_router() -> IPCRouter:
    """创建连接器生命周期管理路由"""
    router = IPCRouter(prefix="/connector-lifecycle")
    
    @router.get("/list")
    async def list_connectors(request: IPCRequest) -> IPCResponse:
        """列出所有连接器"""
        try:
            from services.connectors.connector_manager import get_connector_manager
            
            manager = get_connector_manager()
            connectors = manager.list_connectors()
            
            return IPCResponse(data={"connectors": connectors})
            
        except Exception as e:
            logger.error(f"列出连接器失败: {e}")
            return IPCResponse(
                status_code=500,
                data={"error": str(e)}
            )
    
    @router.post("/start/{connector_name}")
    async def start_connector(request: IPCRequest) -> IPCResponse:
        """启动指定连接器"""
        connector_name = request.path_params.get("connector_name")
        if not connector_name:
            return IPCResponse(
                status_code=400,
                data={"error": "Missing connector name"}
            )
        
        try:
            from services.connectors.connector_manager import get_connector_manager
            
            manager = get_connector_manager()
            result = await manager.start_connector(connector_name)
            
            return IPCResponse(data={"result": result})
            
        except Exception as e:
            logger.error(f"启动连接器 {connector_name} 失败: {e}")
            return IPCResponse(
                status_code=500,
                data={"error": str(e)}
            )
    
    @router.post("/stop/{connector_name}")
    async def stop_connector(request: IPCRequest) -> IPCResponse:
        """停止指定连接器"""
        connector_name = request.path_params.get("connector_name")
        if not connector_name:
            return IPCResponse(
                status_code=400,
                data={"error": "Missing connector name"}
            )
        
        try:
            from services.connectors.connector_manager import get_connector_manager
            
            manager = get_connector_manager()
            result = await manager.stop_connector(connector_name)
            
            return IPCResponse(data={"result": result})
            
        except Exception as e:
            logger.error(f"停止连接器 {connector_name} 失败: {e}")
            return IPCResponse(
                status_code=500,
                data={"error": str(e)}
            )
    
    @router.post("/restart/{connector_name}")
    async def restart_connector(request: IPCRequest) -> IPCResponse:
        """重启指定连接器"""
        connector_name = request.path_params.get("connector_name")
        if not connector_name:
            return IPCResponse(
                status_code=400,
                data={"error": "Missing connector name"}
            )
        
        try:
            from services.connectors.connector_manager import get_connector_manager
            
            manager = get_connector_manager()
            result = await manager.restart_connector(connector_name)
            
            return IPCResponse(data={"result": result})
            
        except Exception as e:
            logger.error(f"重启连接器 {connector_name} 失败: {e}")
            return IPCResponse(
                status_code=500,
                data={"error": str(e)}
            )
    
    @router.get("/status/{connector_name}")
    async def get_connector_status(request: IPCRequest) -> IPCResponse:
        """获取连接器状态"""
        connector_name = request.path_params.get("connector_name")
        if not connector_name:
            return IPCResponse(
                status_code=400,
                data={"error": "Missing connector name"}
            )
        
        try:
            from services.connectors.connector_manager import get_connector_manager
            
            manager = get_connector_manager()
            status = manager.get_connector_status(connector_name)
            
            if status is None:
                return IPCResponse(
                    status_code=404,
                    data={"error": f"Connector {connector_name} not found"}
                )
            
            return IPCResponse(data={"status": status})
            
        except Exception as e:
            logger.error(f"获取连接器状态失败: {e}")
            return IPCResponse(
                status_code=500,
                data={"error": str(e)}
            )
    
    return router


def create_connector_config_router() -> IPCRouter:
    """创建连接器配置管理路由"""
    router = IPCRouter(prefix="/connector-config")
    
    @router.get("/{connector_name}")
    async def get_connector_config(request: IPCRequest) -> IPCResponse:
        """获取连接器配置"""
        connector_name = request.path_params.get("connector_name")
        if not connector_name:
            return IPCResponse(
                status_code=400,
                data={"error": "Missing connector name"}
            )
        
        try:
            from api.dependencies import get_config_manager
            
            config_manager = get_config_manager()
            config = config_manager.get_connector_config(connector_name)
            
            if not config:
                return IPCResponse(
                    status_code=404,
                    data={"error": f"Config for connector {connector_name} not found"}
                )
            
            return IPCResponse(data={"config": config})
            
        except Exception as e:
            logger.error(f"获取连接器配置失败: {e}")
            return IPCResponse(
                status_code=500,
                data={"error": str(e)}
            )
    
    @router.put("/{connector_name}")
    async def update_connector_config(request: IPCRequest) -> IPCResponse:
        """更新连接器配置"""
        connector_name = request.path_params.get("connector_name")
        if not connector_name:
            return IPCResponse(
                status_code=400,
                data={"error": "Missing connector name"}
            )
        
        if not request.data or "config" not in request.data:
            return IPCResponse(
                status_code=400,
                data={"error": "Missing config data"}
            )
        
        try:
            from api.dependencies import get_config_manager
            
            config_manager = get_config_manager()
            config_manager.update_connector_config(connector_name, request.data["config"])
            
            return IPCResponse(data={"message": "Config updated successfully"})
            
        except Exception as e:
            logger.error(f"更新连接器配置失败: {e}")
            return IPCResponse(
                status_code=500,
                data={"error": str(e)}
            )
    
    return router


def create_storage_router() -> IPCRouter:
    """创建存储API路由"""
    router = IPCRouter(prefix="/storage")
    
    @router.get("/entities")
    async def get_entities(request: IPCRequest) -> IPCResponse:
        """获取实体列表"""
        try:
            from services.storage_service import get_storage_service
            
            # 解析查询参数
            limit = request.get_query("limit", 100)
            offset = request.get_query("offset", 0)
            search = request.get_query("search")
            
            storage_service = get_storage_service()
            entities = await storage_service.get_entities(
                limit=int(limit),
                offset=int(offset),
                search=search
            )
            
            return IPCResponse(data={"entities": entities})
            
        except Exception as e:
            logger.error(f"获取实体列表失败: {e}")
            return IPCResponse(
                status_code=500,
                data={"error": str(e)}
            )
    
    @router.get("/relationships")
    async def get_relationships(request: IPCRequest) -> IPCResponse:
        """获取关系列表"""
        try:
            from services.storage_service import get_storage_service
            
            # 解析查询参数
            limit = request.get_query("limit", 100)
            offset = request.get_query("offset", 0)
            entity_id = request.get_query("entity_id")
            
            storage_service = get_storage_service()
            relationships = await storage_service.get_relationships(
                limit=int(limit),
                offset=int(offset),
                entity_id=entity_id
            )
            
            return IPCResponse(data={"relationships": relationships})
            
        except Exception as e:
            logger.error(f"获取关系列表失败: {e}")
            return IPCResponse(
                status_code=500,
                data={"error": str(e)}
            )
    
    @router.get("/search")
    async def search_content(request: IPCRequest) -> IPCResponse:
        """搜索内容"""
        query = request.get_query("q")
        if not query:
            return IPCResponse(
                status_code=400,
                data={"error": "Missing search query"}
            )
        
        try:
            from services.storage_service import get_storage_service
            
            limit = request.get_query("limit", 50)
            
            storage_service = get_storage_service()
            results = await storage_service.search(
                query=query,
                limit=int(limit)
            )
            
            return IPCResponse(data={"results": results})
            
        except Exception as e:
            logger.error(f"搜索内容失败: {e}")
            return IPCResponse(
                status_code=500,
                data={"error": str(e)}
            )
    
    return router


def create_system_config_router() -> IPCRouter:
    """创建系统配置路由"""
    router = IPCRouter(prefix="/system-config")
    
    @router.get("/")
    async def get_system_config(request: IPCRequest) -> IPCResponse:
        """获取系统配置"""
        try:
            from api.dependencies import get_config_manager
            
            config_manager = get_config_manager()
            config = config_manager.get_system_config()
            
            return IPCResponse(data={"config": config})
            
        except Exception as e:
            logger.error(f"获取系统配置失败: {e}")
            return IPCResponse(
                status_code=500,
                data={"error": str(e)}
            )
    
    @router.put("/")
    async def update_system_config(request: IPCRequest) -> IPCResponse:
        """更新系统配置"""
        if not request.data or "config" not in request.data:
            return IPCResponse(
                status_code=400,
                data={"error": "Missing config data"}
            )
        
        try:
            from api.dependencies import get_config_manager
            
            config_manager = get_config_manager()
            config_manager.update_system_config(request.data["config"])
            
            return IPCResponse(data={"message": "System config updated successfully"})
            
        except Exception as e:
            logger.error(f"更新系统配置失败: {e}")
            return IPCResponse(
                status_code=500,
                data={"error": str(e)}
            )
    
    @router.get("/registry")
    async def get_connector_registry(request: IPCRequest) -> IPCResponse:
        """获取连接器注册表"""
        try:
            from services.connector_registry_service import get_connector_registry_service
            
            registry_service = get_connector_registry_service()
            registry = registry_service.get_registry()
            
            return IPCResponse(data={"registry": registry})
            
        except Exception as e:
            logger.error(f"获取连接器注册表失败: {e}")
            return IPCResponse(
                status_code=500,
                data={"error": str(e)}
            )
    
    return router


def create_webview_config_router() -> IPCRouter:
    """创建WebView配置路由"""
    router = IPCRouter(prefix="/webview-config")
    
    @router.get("/")
    async def get_webview_config(request: IPCRequest) -> IPCResponse:
        """获取WebView配置"""
        try:
            from services.webview_config_service import get_webview_config_service
            
            webview_service = get_webview_config_service()
            config = webview_service.get_config()
            
            return IPCResponse(data={"config": config})
            
        except Exception as e:
            logger.error(f"获取WebView配置失败: {e}")
            return IPCResponse(
                status_code=500,
                data={"error": str(e)}
            )
    
    @router.put("/")
    async def update_webview_config(request: IPCRequest) -> IPCResponse:
        """更新WebView配置"""
        if not request.data or "config" not in request.data:
            return IPCResponse(
                status_code=400,
                data={"error": "Missing config data"}
            )
        
        try:
            from services.webview_config_service import get_webview_config_service
            
            webview_service = get_webview_config_service()
            webview_service.update_config(request.data["config"])
            
            return IPCResponse(data={"message": "WebView config updated successfully"})
            
        except Exception as e:
            logger.error(f"更新WebView配置失败: {e}")
            return IPCResponse(
                status_code=500,
                data={"error": str(e)}
            )
    
    return router


def register_all_routes(app):
    """注册所有IPC路由"""
    # 注册各个路由器
    app.include_router(create_health_router())
    app.include_router(create_connector_lifecycle_router())
    app.include_router(create_connector_config_router())
    app.include_router(create_storage_router())
    app.include_router(create_system_config_router())
    app.include_router(create_webview_config_router())
    
    logger.info("所有IPC路由已注册完成")