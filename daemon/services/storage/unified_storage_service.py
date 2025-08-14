#!/usr/bin/env python3
"""
统一存储服务 - P1优化重构
将12个存储文件合并为统一接口，保留AI能力的同时大幅简化复杂度
"""

import asyncio
import logging
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

# 核心依赖
from core.service_facade import get_service
from services.unified_database_service import UnifiedDatabaseService

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """搜索结果统一格式"""
    entity_id: str
    score: float
    content: str
    entity_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    

@dataclass
class StorageMetrics:
    """存储性能指标"""
    total_entities: int = 0
    total_relationships: int = 0
    search_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_search_time_ms: float = 0.0
    last_updated: float = field(default_factory=time.time)
    
    @property
    def cache_hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / max(total, 1)


class SmartCache:
    """智能分层缓存系统 - 🚀 内存优化核心"""
    
    def __init__(self, hot_size: int = 100, warm_size: int = 1000):
        """
        三层缓存架构:
        - Hot: 最热门数据，常驻内存
        - Warm: 次热门数据，LRU管理
        - Cold: SQLite数据库，按需加载
        """
        from functools import lru_cache
        
        self.hot_cache: Dict[str, Any] = {}  # 热数据缓存
        self.warm_cache = {}  # 使用简单字典+LRU逻辑
        self.warm_access_order = []  # LRU访问顺序
        
        self.hot_size = hot_size
        self.warm_size = warm_size
        
        # 访问统计
        self.access_stats = {}
        self.hit_counts = {"hot": 0, "warm": 0, "miss": 0}
        
        logger.info(f"🧠 智能缓存初始化 - 热数据: {hot_size}, 温数据: {warm_size}")
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        # L1: 热缓存
        if key in self.hot_cache:
            self.hit_counts["hot"] += 1
            self._update_access_stats(key)
            return self.hot_cache[key]
        
        # L2: 温缓存
        if key in self.warm_cache:
            self.hit_counts["warm"] += 1
            self._promote_to_hot(key)
            return self.warm_cache[key]
        
        # Cache miss
        self.hit_counts["miss"] += 1
        return None
    
    def set(self, key: str, value: Any):
        """设置缓存数据"""
        # 直接放入温缓存，让热度统计决定是否提升
        self.warm_cache[key] = value
        self._update_warm_lru(key)
        self._update_access_stats(key)
        
        # 检查温缓存大小
        if len(self.warm_cache) > self.warm_size:
            self._evict_from_warm()
    
    def _promote_to_hot(self, key: str):
        """提升到热缓存"""
        if len(self.hot_cache) >= self.hot_size:
            # 热缓存满了，移除最少访问的
            least_accessed = min(self.hot_cache.keys(), 
                                key=lambda k: self.access_stats.get(k, 0))
            self.hot_cache.pop(least_accessed)
        
        self.hot_cache[key] = self.warm_cache[key]
        self._update_warm_lru(key)
        
    def _update_warm_lru(self, key: str):
        """更新温缓存LRU顺序"""
        if key in self.warm_access_order:
            self.warm_access_order.remove(key)
        self.warm_access_order.append(key)
    
    def _evict_from_warm(self):
        """从温缓存中驱逐最久未访问的数据"""
        if self.warm_access_order:
            oldest_key = self.warm_access_order.pop(0)
            self.warm_cache.pop(oldest_key, None)
    
    def _update_access_stats(self, key: str):
        """更新访问统计"""
        self.access_stats[key] = self.access_stats.get(key, 0) + 1
    
    def clear(self):
        """清理所有缓存"""
        cleared = len(self.hot_cache) + len(self.warm_cache)
        self.hot_cache.clear()
        self.warm_cache.clear()
        self.warm_access_order.clear()
        self.access_stats.clear()
        self.hit_counts = {"hot": 0, "warm": 0, "miss": 0}
        logger.info(f"🧹 缓存已清理，移除 {cleared} 个项目")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total_hits = self.hit_counts["hot"] + self.hit_counts["warm"]
        total_requests = total_hits + self.hit_counts["miss"]
        
        return {
            "hot_cache_size": len(self.hot_cache),
            "warm_cache_size": len(self.warm_cache),
            "total_requests": total_requests,
            "cache_hit_rate": total_hits / max(total_requests, 1),
            "hit_distribution": self.hit_counts,
            "top_accessed": sorted(self.access_stats.items(), 
                                 key=lambda x: x[1], reverse=True)[:10]
        }


class UnifiedStorageService:
    """统一存储服务 - 🚀 存储层重构核心
    
    合并功能:
    - ✅ 基础CRUD操作 (simplified_storage_service)
    - ✅ 搜索服务 (vector_service + sqlite FTS)
    - ✅ 关系管理 (graph_service 简化版)
    - ✅ 智能缓存 (多层缓存优化)
    - ✅ 数据生命周期 (简化数据管理)
    - ✅ 基础性能监控
    
    移除的复杂性:
    - ❌ 复杂的图算法 (保留基础关系查询)
    - ❌ 高维向量计算 (用SQLite FTS替代)
    - ❌ 复杂的数据迁移 (简化为基础同步)
    """
    
    def __init__(self, cache_config: Optional[Dict] = None):
        """初始化统一存储服务"""
        # 核心依赖
        self.db_service = get_service(UnifiedDatabaseService)
        
        # 智能缓存
        cache_config = cache_config or {}
        self.cache = SmartCache(
            hot_size=cache_config.get("hot_size", 100),
            warm_size=cache_config.get("warm_size", 1000)
        )
        
        # 性能指标
        self.metrics = StorageMetrics()
        
        # 异步执行器
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="storage")
        
        # FTS索引状态
        self._fts_initialized = False
        
        logger.info("🏪 统一存储服务初始化完成")
    
    async def initialize(self):
        """初始化存储服务"""
        try:
            # 初始化FTS全文搜索
            await self._initialize_fts()
            
            # 加载基础统计
            await self._load_metrics()
            
            logger.info("✅ 统一存储服务初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 统一存储服务初始化失败: {e}")
            raise
    
    # =============================================================================
    # 核心CRUD操作
    # =============================================================================
    
    async def create_entity(self, entity_data: Dict[str, Any]) -> bool:
        """创建实体"""
        entity_id = entity_data.get("entity_id")
        if not entity_id:
            raise ValueError("entity_id是必需的")
        
        try:
            loop = asyncio.get_event_loop()
            
            def _create():
                with self.db_service.get_session() as session:
                    # 插入到entities表
                    session.execute("""
                        INSERT OR REPLACE INTO entities 
                        (entity_id, entity_type, display_name, description, content, properties, tags)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        entity_id,
                        entity_data.get("entity_type", "unknown"),
                        entity_data.get("name", ""),
                        entity_data.get("description", ""),
                        entity_data.get("content", ""),
                        str(entity_data.get("properties", {})),
                        str(entity_data.get("tags", []))
                    ))
                    
                    # 插入到FTS表用于搜索
                    if self._fts_initialized:
                        session.execute("""
                            INSERT OR REPLACE INTO entities_fts 
                            (entity_id, content)
                            VALUES (?, ?)
                        """, (
                            entity_id,
                            f"{entity_data.get('name', '')} {entity_data.get('description', '')} {entity_data.get('content', '')}"
                        ))
                    
                    session.commit()
                    return True
            
            result = await loop.run_in_executor(self.executor, _create)
            
            # 更新缓存
            self.cache.set(f"entity:{entity_id}", entity_data)
            self.metrics.total_entities += 1
            
            logger.debug(f"✅ 实体创建成功: {entity_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 创建实体失败 {entity_id}: {e}")
            return False
    
    async def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """获取实体"""
        cache_key = f"entity:{entity_id}"
        
        # 尝试从缓存获取
        cached = self.cache.get(cache_key)
        if cached:
            self.metrics.cache_hits += 1
            return cached
        
        self.metrics.cache_misses += 1
        
        try:
            loop = asyncio.get_event_loop()
            
            def _get():
                with self.db_service.get_session() as session:
                    result = session.execute("""
                        SELECT entity_id, entity_type, display_name, description, 
                               content, properties, tags, created_at, updated_at
                        FROM entities WHERE entity_id = ?
                    """, (entity_id,)).fetchone()
                    
                    if result:
                        return {
                            "entity_id": result[0],
                            "entity_type": result[1],
                            "name": result[2],
                            "description": result[3],
                            "content": result[4],
                            "properties": eval(result[5]) if result[5] else {},
                            "tags": eval(result[6]) if result[6] else [],
                            "created_at": result[7],
                            "updated_at": result[8]
                        }
                    return None
            
            entity = await loop.run_in_executor(self.executor, _get)
            
            # 缓存结果
            if entity:
                self.cache.set(cache_key, entity)
                logger.debug(f"📦 实体已缓存: {entity_id}")
            
            return entity
            
        except Exception as e:
            logger.error(f"❌ 获取实体失败 {entity_id}: {e}")
            return None
    
    async def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """更新实体"""
        try:
            loop = asyncio.get_event_loop()
            
            def _update():
                with self.db_service.get_session() as session:
                    # 构建UPDATE语句
                    set_clauses = []
                    values = []
                    
                    for key, value in updates.items():
                        if key == "entity_id":
                            continue  # 不允许更新ID
                        
                        if key in ["entity_type", "name", "description", "content"]:
                            set_clauses.append(f"{key} = ?")
                            values.append(value)
                        elif key in ["properties", "tags"]:
                            set_clauses.append(f"{key} = ?")
                            values.append(str(value))
                    
                    if not set_clauses:
                        return False
                    
                    set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                    values.append(entity_id)
                    
                    sql = f"UPDATE entities SET {', '.join(set_clauses)} WHERE entity_id = ?"
                    session.execute(sql, values)
                    session.commit()
                    
                    return session.rowcount > 0
            
            result = await loop.run_in_executor(self.executor, _update)
            
            # 清除缓存，强制重新加载
            cache_key = f"entity:{entity_id}"
            self.cache.set(cache_key, None)  # 标记为需要重新加载
            
            if result:
                logger.debug(f"✅ 实体更新成功: {entity_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 更新实体失败 {entity_id}: {e}")
            return False
    
    async def delete_entity(self, entity_id: str) -> bool:
        """删除实体"""
        try:
            loop = asyncio.get_event_loop()
            
            def _delete():
                with self.db_service.get_session() as session:
                    # 删除实体
                    session.execute("DELETE FROM entities WHERE entity_id = ?", (entity_id,))
                    
                    # 删除相关关系
                    session.execute("""
                        DELETE FROM entity_relationships 
                        WHERE source_entity_id = ? OR target_entity_id = ?
                    """, (entity_id, entity_id))
                    
                    # 删除FTS索引
                    if self._fts_initialized:
                        session.execute("DELETE FROM entities_fts WHERE entity_id = ?", (entity_id,))
                    
                    session.commit()
                    return session.rowcount > 0
            
            result = await loop.run_in_executor(self.executor, _delete)
            
            # 清除缓存
            cache_key = f"entity:{entity_id}"
            self.cache.set(cache_key, None)
            
            if result:
                self.metrics.total_entities -= 1
                logger.debug(f"🗑️ 实体删除成功: {entity_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 删除实体失败 {entity_id}: {e}")
            return False
    
    # =============================================================================
    # 搜索功能 - 简化但有效
    # =============================================================================
    
    async def search_entities(
        self, 
        query: str, 
        entity_type: Optional[str] = None,
        limit: int = 20
    ) -> List[SearchResult]:
        """搜索实体 - 使用SQLite FTS"""
        if not query.strip():
            return []
        
        start_time = time.time()
        
        try:
            loop = asyncio.get_event_loop()
            
            def _search():
                with self.db_service.get_session() as session:
                    # 构建搜索SQL
                    if self._fts_initialized:
                        # 使用FTS搜索
                        base_sql = """
                            SELECT e.entity_id, e.entity_type, e.display_name, e.content, 
                                   fts.rank
                            FROM entities_fts fts
                            JOIN entities e ON fts.entity_id = e.entity_id
                            WHERE entities_fts MATCH ?
                        """
                        params = [query]
                        
                        if entity_type:
                            base_sql += " AND e.entity_type = ?"
                            params.append(entity_type)
                        
                        base_sql += " ORDER BY fts.rank DESC LIMIT ?"
                        params.append(limit)
                        
                    else:
                        # 回退到LIKE搜索
                        base_sql = """
                            SELECT entity_id, entity_type, display_name, content, 1.0 as rank
                            FROM entities 
                            WHERE (display_name LIKE ? OR content LIKE ?)
                        """
                        params = [f"%{query}%", f"%{query}%"]
                        
                        if entity_type:
                            base_sql += " AND entity_type = ?"
                            params.append(entity_type)
                        
                        base_sql += " LIMIT ?"
                        params.append(limit)
                    
                    results = session.execute(base_sql, params).fetchall()
                    
                    return [
                        SearchResult(
                            entity_id=row[0],
                            entity_type=row[1],
                            content=f"{row[2]} {row[3]}"[:200],
                            score=float(row[4])
                        )
                        for row in results
                    ]
            
            results = await loop.run_in_executor(self.executor, _search)
            
            # 更新指标
            search_time = (time.time() - start_time) * 1000
            self.metrics.search_requests += 1
            self.metrics.avg_search_time_ms = (
                (self.metrics.avg_search_time_ms * (self.metrics.search_requests - 1) + search_time)
                / self.metrics.search_requests
            )
            
            logger.debug(f"🔍 搜索完成: {len(results)} 个结果，耗时 {search_time:.2f}ms")
            return results
            
        except Exception as e:
            logger.error(f"❌ 搜索失败: {e}")
            return []
    
    # =============================================================================
    # 关系管理 - 简化版
    # =============================================================================
    
    async def create_relationship(
        self, 
        source_id: str, 
        target_id: str, 
        relationship_type: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """创建实体关系"""
        try:
            loop = asyncio.get_event_loop()
            
            def _create_rel():
                with self.db_service.get_session() as session:
                    session.execute("""
                        INSERT OR REPLACE INTO entity_relationships
                        (source_entity_id, target_entity_id, relationship_type, metadata)
                        VALUES (?, ?, ?, ?)
                    """, (source_id, target_id, relationship_type, str(metadata or {})))
                    
                    session.commit()
                    return True
            
            result = await loop.run_in_executor(self.executor, _create_rel)
            
            if result:
                self.metrics.total_relationships += 1
                logger.debug(f"🔗 关系创建成功: {source_id} -> {target_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 创建关系失败: {e}")
            return False
    
    async def get_related_entities(self, entity_id: str, relationship_type: Optional[str] = None) -> List[Dict]:
        """获取相关实体"""
        try:
            loop = asyncio.get_event_loop()
            
            def _get_related():
                with self.db_service.get_session() as session:
                    sql = """
                        SELECT e.entity_id, e.entity_type, e.display_name, r.relationship_type
                        FROM entity_relationships r
                        JOIN entities e ON (r.target_entity_id = e.entity_id OR r.source_entity_id = e.entity_id)
                        WHERE (r.source_entity_id = ? OR r.target_entity_id = ?) 
                        AND e.entity_id != ?
                    """
                    params = [entity_id, entity_id, entity_id]
                    
                    if relationship_type:
                        sql += " AND r.relationship_type = ?"
                        params.append(relationship_type)
                    
                    results = session.execute(sql, params).fetchall()
                    
                    return [
                        {
                            "entity_id": row[0],
                            "entity_type": row[1],
                            "name": row[2],
                            "relationship_type": row[3]
                        }
                        for row in results
                    ]
            
            return await loop.run_in_executor(self.executor, _get_related)
            
        except Exception as e:
            logger.error(f"❌ 获取相关实体失败: {e}")
            return []
    
    # =============================================================================
    # 系统管理功能
    # =============================================================================
    
    async def _initialize_fts(self):
        """初始化FTS全文搜索"""
        try:
            loop = asyncio.get_event_loop()
            
            def _create_fts():
                with self.db_service.get_session() as session:
                    # 创建FTS表
                    session.execute("""
                        CREATE VIRTUAL TABLE IF NOT EXISTS entities_fts 
                        USING fts5(entity_id, content, tokenize='simple')
                    """)
                    
                    # 检查是否需要初始化数据
                    count = session.execute("SELECT COUNT(*) FROM entities_fts").fetchone()[0]
                    if count == 0:
                        # 从现有实体初始化FTS
                        session.execute("""
                            INSERT INTO entities_fts (entity_id, content)
                            SELECT entity_id, display_name || ' ' || COALESCE(description, '') || ' ' || COALESCE(content, '')
                            FROM entities
                        """)
                    
                    session.commit()
            
            await loop.run_in_executor(self.executor, _create_fts)
            self._fts_initialized = True
            logger.info("✅ FTS全文搜索已初始化")
            
        except Exception as e:
            logger.warning(f"⚠️ FTS初始化失败，将使用LIKE搜索: {e}")
            self._fts_initialized = False
    
    async def _load_metrics(self):
        """加载基础指标"""
        try:
            loop = asyncio.get_event_loop()
            
            def _load():
                with self.db_service.get_session() as session:
                    # 统计实体数量
                    entity_count = session.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
                    
                    # 统计关系数量
                    rel_count = session.execute("SELECT COUNT(*) FROM entity_relationships").fetchone()[0]
                    
                    return entity_count, rel_count
            
            entity_count, rel_count = await loop.run_in_executor(self.executor, _load)
            
            self.metrics.total_entities = entity_count
            self.metrics.total_relationships = rel_count
            
            logger.info(f"📊 存储指标加载完成 - 实体: {entity_count}, 关系: {rel_count}")
            
        except Exception as e:
            logger.error(f"❌ 加载存储指标失败: {e}")
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        cache_stats = self.cache.get_stats()
        
        return {
            "metrics": {
                "total_entities": self.metrics.total_entities,
                "total_relationships": self.metrics.total_relationships,
                "search_requests": self.metrics.search_requests,
                "avg_search_time_ms": self.metrics.avg_search_time_ms,
                "cache_hit_rate": self.metrics.cache_hit_rate,
            },
            "cache": cache_stats,
            "features": {
                "fts_enabled": self._fts_initialized,
                "smart_cache_enabled": True,
                "relationship_support": True,
            },
            "performance": {
                "executor_threads": self.executor._max_workers,
                "last_updated": self.metrics.last_updated,
            }
        }
    
    async def optimize_storage(self):
        """优化存储性能"""
        try:
            loop = asyncio.get_event_loop()
            
            def _optimize():
                with self.db_service.get_session() as session:
                    # VACUUM数据库
                    session.execute("VACUUM")
                    
                    # 分析表统计信息
                    session.execute("ANALYZE")
                    
                    # 优化FTS索引
                    if self._fts_initialized:
                        session.execute("INSERT INTO entities_fts(entities_fts) VALUES('optimize')")
                    
                    session.commit()
            
            await loop.run_in_executor(self.executor, _optimize)
            
            # 清理缓存，释放内存
            self.cache.clear()
            
            logger.info("🚀 存储优化完成")
            
        except Exception as e:
            logger.error(f"❌ 存储优化失败: {e}")
    
    async def cleanup(self):
        """清理资源"""
        try:
            if self.executor:
                self.executor.shutdown(wait=True)
            
            self.cache.clear()
            logger.info("🧹 统一存储服务已清理")
            
        except Exception as e:
            logger.error(f"❌ 清理存储服务失败: {e}")


# 全局统一存储服务实例
# ServiceFacade现在负责管理服务单例，不再需要本地单例模式


async def initialize_unified_storage(**kwargs) -> UnifiedStorageService:
    """初始化统一存储服务 - 现在通过ServiceFacade管理"""
    from core.service_facade import get_service
    service = get_service(UnifiedStorageService)
    await service.initialize()
    return service


async def cleanup_unified_storage():
    """清理统一存储服务 - 现在由ServiceFacade管理生命周期"""
    logger.info("🧹 统一存储服务的清理现在由ServiceFacade负责管理")