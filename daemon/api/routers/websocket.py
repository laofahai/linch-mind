#!/usr/bin/env python3
"""
WebSocket实时通信路由 - 连接器状态和数据变更的实时推送
Session V48 新增 - 实时通信基础框架
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List, Set
import logging
import json
import asyncio
from datetime import datetime

from services.connectors.lifecycle_manager import ConnectorLifecycleManager
from services.database_service import DatabaseService
from api.dependencies import get_lifecycle, get_db_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ws", tags=["websocket"])

class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_info: Dict[WebSocket, dict] = {}  # 存储连接信息
    
    async def connect(self, websocket: WebSocket, client_info: dict = None):
        """接受WebSocket连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_info[websocket] = client_info or {}
        logger.info(f"WebSocket连接建立，当前连接数: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            self.connection_info.pop(websocket, None)
            logger.info(f"WebSocket连接断开，当前连接数: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送消息给特定客户端"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"发送WebSocket消息失败: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """广播消息给所有客户端"""
        if not self.active_connections:
            return
            
        disconnect_list = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"广播WebSocket消息失败: {e}")
                disconnect_list.append(connection)
        
        # 清理断开的连接
        for connection in disconnect_list:
            self.disconnect(connection)

# 全局连接管理器
manager = ConnectionManager()

@router.websocket("/status")
async def websocket_status_endpoint(
    websocket: WebSocket,
    lifecycle_manager: ConnectorLifecycleManager = Depends(get_lifecycle),
    db_service: DatabaseService = Depends(get_db_service)
):
    """WebSocket端点 - 实时状态更新"""
    await manager.connect(websocket, {"type": "status", "connected_at": datetime.now()})
    
    try:
        # 发送初始状态
        initial_status = await get_current_status(lifecycle_manager, db_service)
        await manager.send_personal_message({
            "type": "initial_status",
            "data": initial_status,
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        # 保持连接，处理客户端消息
        while True:
            try:
                # 等待客户端消息（心跳包或请求）
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    # 响应心跳包
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                elif message.get("type") == "request_status":
                    # 客户端请求状态更新
                    current_status = await get_current_status(lifecycle_manager, db_service)
                    await manager.send_personal_message({
                        "type": "status_update",
                        "data": current_status,
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                    
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.now().isoformat()
                }, websocket)
            except Exception as e:
                logger.error(f"WebSocket消息处理错误: {e}")
                await manager.send_personal_message({
                    "type": "error", 
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("客户端主动断开WebSocket连接")
    except Exception as e:
        logger.error(f"WebSocket连接异常: {e}")
        manager.disconnect(websocket)

async def get_current_status(lifecycle_manager: ConnectorLifecycleManager, db_service: DatabaseService) -> dict:
    """获取当前系统状态"""
    try:
        # 获取所有连接器实例
        all_instances = lifecycle_manager.config_manager.list_instances()
        running_instances = lifecycle_manager.list_running_instances()
        
        connector_status = []
        for instance in all_instances:
            instance_id = instance.instance_id
            is_running = instance_id in running_instances
            state = lifecycle_manager.get_instance_state(instance_id)
            
            connector_status.append({
                "id": instance_id,
                "name": instance.display_name,
                "type": instance.type_id,
                "status": state.value,
                "data_count": instance.data_count if hasattr(instance, 'data_count') else 0,
                "last_update": instance.last_heartbeat.isoformat() if instance.last_heartbeat else None
            })
        
        # 获取数据库统计
        stats = db_service.get_database_stats()
        
        return {
            "connectors": connector_status,
            "database_stats": stats,
            "system_health": "healthy",  # 简化版健康状态
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        return {
            "connectors": [],
            "database_stats": {},
            "system_health": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# 广播状态更新的辅助函数（供其他模块调用）
async def broadcast_status_update(update_data: dict):
    """广播状态更新给所有WebSocket客户端"""
    message = {
        "type": "status_update",
        "data": update_data,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(message)

async def broadcast_connector_event(connector_id: str, event_type: str, details: dict = None):
    """广播连接器事件"""
    message = {
        "type": "connector_event",
        "connector_id": connector_id,
        "event_type": event_type,  # started, stopped, error, restarted
        "details": details or {},
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(message)

async def broadcast_data_update(data_type: str, count: int, details: dict = None):
    """广播数据更新事件"""
    message = {
        "type": "data_update", 
        "data_type": data_type,  # data_items, graph_nodes, recommendations
        "count": count,
        "details": details or {},
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(message)