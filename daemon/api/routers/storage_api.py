"""
存储API路由 - 三层存储架构的纯IPC接口
"""

import logging
from datetime import datetime

from services.ipc_router import IPCRequest, IPCResponse
from services.storage.data_migration import get_migration_service
from services.storage.storage_orchestrator import get_storage_orchestrator

logger = logging.getLogger(__name__)

# === 实体管理API ===

async def create_entity(request: IPCRequest) -> IPCResponse:
    """创建知识实体"""
    try:
        body = await request.json()
        storage = await get_storage_orchestrator()
        success = await storage.create_entity(
            entity_id=body['entity_id'],
            name=body['name'],
            entity_type=body['entity_type'],
            description=body.get('description'),
            attributes=body.get('attributes', {}),
            source_path=body.get('source_path'),
            content=body.get('content'),
            auto_embed=body.get('auto_embed', True),
        )
        if success:
            return IPCResponse(data={
                "success": True,
                "message": f"实体 {body['entity_id']} 创建成功",
                "entity_id": body['entity_id'],
            })
        return IPCResponse(status_code=400, data={"error": "实体创建失败"})
    except Exception as e:
        logger.error(f"创建实体失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})

async def get_entity(request: IPCRequest) -> IPCResponse:
    """获取知识实体"""
    entity_id = request.path_params.get("entity_id")
    try:
        storage = await get_storage_orchestrator()
        entity = await storage.get_entity(entity_id)
        if not entity:
            return IPCResponse(status_code=404, data={"error": f"实体 {entity_id} 不存在"})
        return IPCResponse(data=entity.to_dict()) # 假设Entity有一个to_dict方法
    except Exception as e:
        logger.error(f"获取实体失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})

async def update_entity(request: IPCRequest) -> IPCResponse:
    """更新知识实体"""
    entity_id = request.path_params.get("entity_id")
    try:
        updates = await request.json()
        if not updates:
            return IPCResponse(status_code=400, data={"error": "没有提供更新字段"})
        
        storage = await get_storage_orchestrator()
        success = await storage.update_entity(entity_id, updates)
        if success:
            return IPCResponse(data={
                "success": True,
                "message": f"实体 {entity_id} 更新成功",
                "entity_id": entity_id,
            })
        return IPCResponse(status_code=404, data={"error": f"实体 {entity_id} 不存在或更新失败"})
    except Exception as e:
        logger.error(f"更新实体失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})

async def delete_entity(request: IPCRequest) -> IPCResponse:
    """删除知识实体"""
    entity_id = request.path_params.get("entity_id")
    try:
        storage = await get_storage_orchestrator()
        success = await storage.delete_entity(entity_id)
        if success:
            return IPCResponse(data={
                "success": True,
                "message": f"实体 {entity_id} 删除成功",
                "entity_id": entity_id,
            })
        return IPCResponse(status_code=404, data={"error": f"实体 {entity_id} 不存在"})
    except Exception as e:
        logger.error(f"删除实体失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})

# === 关系管理API ===

async def create_relationship(request: IPCRequest) -> IPCResponse:
    """创建实体关系"""
    try:
        body = await request.json()
        storage = await get_storage_orchestrator()
        success = await storage.create_relationship(
            source_entity=body['source_entity'],
            target_entity=body['target_entity'],
            relationship_type=body['relationship_type'],
            strength=body.get('strength', 1.0),
            confidence=body.get('confidence', 1.0),
            attributes=body.get('attributes', {}),
        )
        if success:
            return IPCResponse(data={
                "success": True,
                "message": f"关系创建成功: {body['source_entity']} -> {body['target_entity']}",
            })
        return IPCResponse(status_code=400, data={"error": "关系创建失败"})
    except Exception as e:
        logger.error(f"创建关系失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})

# === 智能搜索API ===

async def semantic_search(request: IPCRequest) -> IPCResponse:
    """语义搜索"""
    try:
        body = await request.json()
        storage = await get_storage_orchestrator()
        results = await storage.semantic_search(
            query=body['query'],
            k=body.get('k', 10),
            entity_types=body.get('entity_types')
        )
        # 假设result对象有to_dict方法
        return IPCResponse(data=[res.to_dict() for res in results])
    except Exception as e:
        logger.error(f"语义搜索失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})

async def graph_search(request: IPCRequest) -> IPCResponse:
    """图结构搜索"""
    try:
        body = await request.json()
        storage = await get_storage_orchestrator()
        results = await storage.graph_search(
            entity_id=body['entity_id'],
            max_depth=body.get('max_depth', 2),
            relationship_types=body.get('relationship_types'),
            max_results=body.get('max_results', 20),
        )
        return IPCResponse(data=results)
    except Exception as e:
        logger.error(f"图搜索失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})

# === 智能推荐API ===

async def get_recommendations(request: IPCRequest) -> IPCResponse:
    """获取智能推荐"""
    try:
        body = await request.json()
        storage = await get_storage_orchestrator()
        recommendations = await storage.get_smart_recommendations(
            user_context=body.get('user_context', {}),
            max_recommendations=body.get('max_recommendations', 10),
            algorithm=body.get('algorithm', 'hybrid'),
        )
        # 假设recommendation对象有to_dict方法
        return IPCResponse(data=[rec.to_dict() for rec in recommendations])
    except Exception as e:
        logger.error(f"获取推荐失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})

# === 系统监控API ===

async def get_storage_metrics(request: IPCRequest) -> IPCResponse:
    """获取存储系统指标"""
    try:
        storage = await get_storage_orchestrator()
        metrics = await storage.get_metrics()
        # 假设metrics对象有to_dict方法
        return IPCResponse(data=metrics.to_dict())
    except Exception as e:
        logger.error(f"获取存储指标失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})

async def sync_storage(request: IPCRequest) -> IPCResponse:
    """手动同步所有存储层"""
    try:
        storage = await get_storage_orchestrator()
        success = await storage.sync_all()
        return IPCResponse(data={
            "success": success,
            "message": "存储同步完成" if success else "存储同步失败",
            "timestamp": datetime.utcnow().isoformat(),
        })
    except Exception as e:
        logger.error(f"存储同步失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})

# === 数据迁移API ===

async def get_migration_status(request: IPCRequest) -> IPCResponse:
    """获取数据迁移状态"""
    try:
        migration = await get_migration_service()
        status = await migration.check_migration_status()
        return IPCResponse(data=status)
    except Exception as e:
        logger.error(f"获取迁移状态失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})

async def migrate_all_data(request: IPCRequest) -> IPCResponse:
    """执行完整数据迁移"""
    try:
        body = await request.json()
        migration = await get_migration_service()
        logger.info("开始完整数据迁移...")
        stats = await migration.migrate_all_data(
            force_rebuild=body.get('force_rebuild', False),
            batch_size=body.get('batch_size', 100),
            auto_embed=body.get('auto_embed', True),
        )
        return IPCResponse(data={
            "success": True,
            "message": "数据迁移完成",
            "stats": stats.to_dict() # 假设stats对象有to_dict方法
        })
    except Exception as e:
        logger.error(f"数据迁移失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})

async def migrate_incremental_data(request: IPCRequest) -> IPCResponse:
    """执行增量数据迁移"""
    try:
        since_str = request.query_params.get("since")
        auto_embed = request.query_params.get("auto_embed", "true").lower() == "true"
        
        since_datetime = None
        if since_str:
            since_datetime = datetime.fromisoformat(since_str.replace("Z", "+00:00"))

        migration = await get_migration_service()
        logger.info("开始增量数据迁移...")
        stats = await migration.migrate_incremental(
            since=since_datetime, auto_embed=auto_embed
        )
        return IPCResponse(data={
            "success": True,
            "message": "增量迁移完成",
            "stats": stats.to_dict() # 假设stats对象有to_dict方法
        })
    except Exception as e:
        logger.error(f"增量迁移失败: {e}")
        return IPCResponse(status_code=500, data={"error": str(e)})

# 注意：这个文件现在只包含处理函数。
# 路由注册已移至 services/ipc_routes.py
