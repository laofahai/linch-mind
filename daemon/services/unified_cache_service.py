#!/usr/bin/env python3
"""
统一缓存服务 - 消除6个重复缓存实现
整合内存缓存、磁盘缓存、分层缓存为统一接口
"""

import asyncio
import json
import logging
import pickle
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)


class CacheType(Enum):
    """缓存类型枚举"""
    MEMORY = "memory"           # 内存缓存
    DISK = "disk"              # 磁盘缓存  
    HYBRID = "hybrid"          # 混合缓存(内存+磁盘)
    HOT = "hot"                # 热缓存(最近访问)
    WARM = "warm"              # 温缓存(较少访问)
    PERSISTENT = "persistent"   # 持久化缓存


class SerializationFormat(Enum):
    """序列化格式枚举"""
    JSON = "json"
    PICKLE = "pickle"
    RAW = "raw"                # 原始数据(不序列化)


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    ttl: Optional[float] = None          # 生存时间(秒)
    access_count: int = 0                # 访问次数
    size_bytes: int = 0                  # 数据大小
    cache_type: CacheType = CacheType.MEMORY
    format: SerializationFormat = SerializationFormat.RAW


@dataclass
class CacheStats:
    """缓存统计信息"""
    total_entries: int = 0
    memory_entries: int = 0
    disk_entries: int = 0
    total_hits: int = 0
    total_misses: int = 0
    total_evictions: int = 0
    memory_usage_bytes: int = 0
    disk_usage_bytes: int = 0
    hit_rate: float = 0.0
    last_cleanup: Optional[datetime] = None


class UnifiedCacheService:
    """统一缓存服务 - 消除6个重复缓存实现"""
    
    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        memory_limit: int = 1000,      # 内存缓存条目限制
        hot_cache_size: int = 100,     # 热缓存大小
        warm_cache_size: int = 500,    # 温缓存大小
        default_ttl: int = 3600,       # 默认TTL(秒)
        cleanup_interval: int = 300    # 清理间隔(秒)
    ):
        # 缓存存储
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.hot_cache: Dict[str, CacheEntry] = {}    # 最近访问
        self.warm_cache: Dict[str, CacheEntry] = {}   # 较少访问
        
        # 配置参数
        self.memory_limit = memory_limit
        self.hot_cache_size = hot_cache_size
        self.warm_cache_size = warm_cache_size
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval
        
        # 磁盘缓存目录
        self.cache_dir = cache_dir
        if self.cache_dir:
            self.cache_dir = Path(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 统计信息
        self.stats = CacheStats()
        
        # 访问频率跟踪
        self._access_order: List[str] = []  # LRU顺序
        self._last_cleanup = time.time()
        
        # 序列化器映射
        self._serializers: Dict[SerializationFormat, Callable] = {
            SerializationFormat.JSON: self._json_serialize,
            SerializationFormat.PICKLE: self._pickle_serialize,
            SerializationFormat.RAW: self._raw_serialize,
        }
        
        self._deserializers: Dict[SerializationFormat, Callable] = {
            SerializationFormat.JSON: self._json_deserialize,
            SerializationFormat.PICKLE: self._pickle_deserialize,
            SerializationFormat.RAW: self._raw_deserialize,
        }
        
        logger.info(f"💾 UnifiedCacheService 初始化 (内存限制: {memory_limit}, 热缓存: {hot_cache_size})")

    async def get(
        self, 
        key: str, 
        cache_type: CacheType = CacheType.MEMORY,
        default: Any = None
    ) -> Any:
        """统一缓存获取接口"""
        try:
            # 生成标准化键
            cache_key = self._normalize_key(key)
            
            # 首先检查热缓存
            if cache_key in self.hot_cache:
                entry = self.hot_cache[cache_key]
                if not self._is_expired(entry):
                    self._update_access(entry)
                    self.stats.total_hits += 1
                    logger.debug(f"缓存命中 (热): {cache_key}")
                    return entry.value
                else:
                    # 过期项目清理
                    del self.hot_cache[cache_key]
            
            # 检查内存缓存
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                if not self._is_expired(entry):
                    self._update_access(entry)
                    # 提升到热缓存
                    self._promote_to_hot(cache_key, entry)
                    self.stats.total_hits += 1
                    logger.debug(f"缓存命中 (内存): {cache_key}")
                    return entry.value
                else:
                    del self.memory_cache[cache_key]
            
            # 检查温缓存
            if cache_key in self.warm_cache:
                entry = self.warm_cache[cache_key]
                if not self._is_expired(entry):
                    self._update_access(entry)
                    # 提升到内存缓存
                    self._promote_to_memory(cache_key, entry)
                    self.stats.total_hits += 1
                    logger.debug(f"缓存命中 (温): {cache_key}")
                    return entry.value
                else:
                    del self.warm_cache[cache_key]
            
            # 检查磁盘缓存
            if cache_type in [CacheType.DISK, CacheType.HYBRID, CacheType.PERSISTENT]:
                disk_value = await self._load_from_disk(cache_key)
                if disk_value is not None:
                    # 加载到内存缓存
                    await self.set(cache_key, disk_value, CacheType.MEMORY, ttl=self.default_ttl)
                    self.stats.total_hits += 1
                    logger.debug(f"缓存命中 (磁盘): {cache_key}")
                    return disk_value
            
            # 缓存未命中
            self.stats.total_misses += 1
            logger.debug(f"缓存未命中: {cache_key}")
            return default
            
        except Exception as e:
            logger.error(f"缓存获取失败 [{key}]: {e}")
            return default

    async def set(
        self,
        key: str,
        value: Any,
        cache_type: CacheType = CacheType.MEMORY,
        ttl: Optional[int] = None,
        format: SerializationFormat = SerializationFormat.RAW
    ) -> bool:
        """统一缓存设置接口"""
        try:
            cache_key = self._normalize_key(key)
            
            if ttl is None:
                ttl = self.default_ttl
            
            # 创建缓存条目
            entry = CacheEntry(
                key=cache_key,
                value=value,
                ttl=ttl,
                cache_type=cache_type,
                format=format,
                size_bytes=self._estimate_size(value)
            )
            
            # 根据缓存类型存储
            if cache_type == CacheType.HOT:
                await self._set_hot_cache(cache_key, entry)
                
            elif cache_type == CacheType.WARM:
                await self._set_warm_cache(cache_key, entry)
                
            elif cache_type == CacheType.DISK:
                await self._save_to_disk(cache_key, entry)
                
            elif cache_type == CacheType.PERSISTENT:
                await self._save_to_disk(cache_key, entry)
                await self._set_memory_cache(cache_key, entry)
                
            elif cache_type == CacheType.HYBRID:
                await self._set_memory_cache(cache_key, entry)
                await self._save_to_disk(cache_key, entry)
                
            else:  # CacheType.MEMORY
                await self._set_memory_cache(cache_key, entry)
            
            # 更新统计
            self.stats.total_entries = (
                len(self.memory_cache) + 
                len(self.hot_cache) + 
                len(self.warm_cache)
            )
            
            # 定期清理
            await self._maybe_cleanup()
            
            logger.debug(f"缓存设置成功 [{cache_type.value}]: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"缓存设置失败 [{key}]: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存项"""
        try:
            cache_key = self._normalize_key(key)
            deleted = False
            
            # 从所有缓存中删除
            if cache_key in self.hot_cache:
                del self.hot_cache[cache_key]
                deleted = True
            
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
                deleted = True
            
            if cache_key in self.warm_cache:
                del self.warm_cache[cache_key]
                deleted = True
            
            # 从访问记录中删除
            if cache_key in self._access_order:
                self._access_order.remove(cache_key)
            
            # 删除磁盘文件
            if self.cache_dir:
                disk_file = self.cache_dir / f"{cache_key}.cache"
                if disk_file.exists():
                    disk_file.unlink()
                    deleted = True
            
            if deleted:
                logger.debug(f"缓存删除成功: {cache_key}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"缓存删除失败 [{key}]: {e}")
            return False

    async def clear(self, cache_type: Optional[CacheType] = None):
        """清空缓存"""
        try:
            if cache_type is None:
                # 清空所有缓存
                self.memory_cache.clear()
                self.hot_cache.clear()
                self.warm_cache.clear()
                self._access_order.clear()
                
                # 清空磁盘缓存
                if self.cache_dir and self.cache_dir.exists():
                    for cache_file in self.cache_dir.glob("*.cache"):
                        cache_file.unlink()
                
            elif cache_type == CacheType.HOT:
                self.hot_cache.clear()
            elif cache_type == CacheType.WARM:
                self.warm_cache.clear()
            elif cache_type == CacheType.MEMORY:
                self.memory_cache.clear()
            elif cache_type == CacheType.DISK:
                if self.cache_dir and self.cache_dir.exists():
                    for cache_file in self.cache_dir.glob("*.cache"):
                        cache_file.unlink()
            
            # 重置统计
            self.stats = CacheStats()
            
            logger.info(f"缓存已清空 [{cache_type.value if cache_type else 'all'}]")
            
        except Exception as e:
            logger.error(f"清空缓存失败: {e}")

    async def invalidate_pattern(self, pattern: str):
        """按模式失效缓存"""
        try:
            import re
            pattern_re = re.compile(pattern)
            
            keys_to_delete = []
            
            # 查找匹配的键
            for cache_dict in [self.hot_cache, self.memory_cache, self.warm_cache]:
                for key in cache_dict.keys():
                    if pattern_re.search(key):
                        keys_to_delete.append(key)
            
            # 删除匹配的键
            for key in keys_to_delete:
                await self.delete(key)
            
            logger.info(f"模式失效完成 [{pattern}]: {len(keys_to_delete)} 项")
            
        except Exception as e:
            logger.error(f"模式失效失败 [{pattern}]: {e}")

    # === 便捷方法 - 替代原有各种缓存API ===
    
    async def get_or_set(
        self,
        key: str,
        factory: Callable,
        cache_type: CacheType = CacheType.MEMORY,
        ttl: Optional[int] = None
    ) -> Any:
        """获取缓存或设置新值"""
        value = await self.get(key, cache_type)
        if value is None:
            # 生成新值
            if asyncio.iscoroutinefunction(factory):
                value = await factory()
            else:
                value = factory()
            
            # 缓存新值
            await self.set(key, value, cache_type, ttl)
        
        return value
    
    async def mget(self, keys: List[str], cache_type: CacheType = CacheType.MEMORY) -> Dict[str, Any]:
        """批量获取缓存"""
        results = {}
        for key in keys:
            results[key] = await self.get(key, cache_type)
        return results
    
    async def mset(self, items: Dict[str, Any], cache_type: CacheType = CacheType.MEMORY, ttl: Optional[int] = None) -> bool:
        """批量设置缓存"""
        try:
            for key, value in items.items():
                await self.set(key, value, cache_type, ttl)
            return True
        except Exception as e:
            logger.error(f"批量设置缓存失败: {e}")
            return False

    # === 内部方法 ===
    
    def _normalize_key(self, key: str) -> str:
        """标准化缓存键"""
        # 使用MD5哈希确保键的一致性
        return hashlib.md5(key.encode('utf-8')).hexdigest()
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """检查缓存条目是否过期"""
        if entry.ttl is None:
            return False
        return (time.time() - entry.created_at) > entry.ttl
    
    def _update_access(self, entry: CacheEntry):
        """更新访问信息"""
        entry.accessed_at = time.time()
        entry.access_count += 1
        
        # 更新LRU顺序
        if entry.key in self._access_order:
            self._access_order.remove(entry.key)
        self._access_order.append(entry.key)
    
    def _promote_to_hot(self, key: str, entry: CacheEntry):
        """提升到热缓存"""
        if len(self.hot_cache) >= self.hot_cache_size:
            # 移除最少使用的项
            self._evict_from_hot()
        
        self.hot_cache[key] = entry
        
        # 从其他缓存中移除
        self.memory_cache.pop(key, None)
        self.warm_cache.pop(key, None)
    
    def _promote_to_memory(self, key: str, entry: CacheEntry):
        """提升到内存缓存"""
        if len(self.memory_cache) >= self.memory_limit:
            self._evict_from_memory()
        
        self.memory_cache[key] = entry
        self.warm_cache.pop(key, None)
    
    async def _set_hot_cache(self, key: str, entry: CacheEntry):
        """设置热缓存"""
        if len(self.hot_cache) >= self.hot_cache_size:
            self._evict_from_hot()
        
        self.hot_cache[key] = entry
        self.stats.memory_entries += 1
    
    async def _set_memory_cache(self, key: str, entry: CacheEntry):
        """设置内存缓存"""
        if len(self.memory_cache) >= self.memory_limit:
            self._evict_from_memory()
        
        self.memory_cache[key] = entry
        self.stats.memory_entries += 1
    
    async def _set_warm_cache(self, key: str, entry: CacheEntry):
        """设置温缓存"""
        if len(self.warm_cache) >= self.warm_cache_size:
            self._evict_from_warm()
        
        self.warm_cache[key] = entry
    
    def _evict_from_hot(self):
        """从热缓存中淘汰"""
        if not self.hot_cache:
            return
        
        # 找到最少使用的项
        lru_key = min(
            self.hot_cache.keys(),
            key=lambda k: self.hot_cache[k].accessed_at
        )
        
        # 移动到内存缓存
        entry = self.hot_cache.pop(lru_key)
        if len(self.memory_cache) < self.memory_limit:
            self.memory_cache[lru_key] = entry
        else:
            self.stats.total_evictions += 1
    
    def _evict_from_memory(self):
        """从内存缓存中淘汰"""
        if not self.memory_cache:
            return
        
        lru_key = min(
            self.memory_cache.keys(),
            key=lambda k: self.memory_cache[k].accessed_at
        )
        
        # 移动到温缓存
        entry = self.memory_cache.pop(lru_key)
        if len(self.warm_cache) < self.warm_cache_size:
            self.warm_cache[lru_key] = entry
        else:
            self.stats.total_evictions += 1
    
    def _evict_from_warm(self):
        """从温缓存中淘汰"""
        if not self.warm_cache:
            return
        
        lru_key = min(
            self.warm_cache.keys(),
            key=lambda k: self.warm_cache[k].accessed_at
        )
        
        self.warm_cache.pop(lru_key)
        self.stats.total_evictions += 1
    
    async def _save_to_disk(self, key: str, entry: CacheEntry):
        """保存到磁盘"""
        if not self.cache_dir:
            return
        
        try:
            disk_file = self.cache_dir / f"{key}.cache"
            serialized_data = self._serializers[entry.format](entry.value)
            
            # 保存元数据和数据
            cache_data = {
                "value": serialized_data,
                "created_at": entry.created_at,
                "ttl": entry.ttl,
                "format": entry.format.value
            }
            
            with open(disk_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            self.stats.disk_entries += 1
            
        except Exception as e:
            logger.error(f"保存磁盘缓存失败 [{key}]: {e}")
    
    async def _load_from_disk(self, key: str) -> Optional[Any]:
        """从磁盘加载"""
        if not self.cache_dir:
            return None
        
        try:
            disk_file = self.cache_dir / f"{key}.cache"
            if not disk_file.exists():
                return None
            
            with open(disk_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # 检查是否过期
            if cache_data.get("ttl"):
                if (time.time() - cache_data["created_at"]) > cache_data["ttl"]:
                    disk_file.unlink()
                    return None
            
            # 反序列化数据
            format_enum = SerializationFormat(cache_data.get("format", "raw"))
            value = self._deserializers[format_enum](cache_data["value"])
            
            return value
            
        except Exception as e:
            logger.error(f"加载磁盘缓存失败 [{key}]: {e}")
            return None
    
    def _estimate_size(self, value: Any) -> int:
        """估算数据大小"""
        try:
            return len(pickle.dumps(value))
        except:
            return 0
    
    # === 序列化器 ===
    
    def _json_serialize(self, value: Any) -> str:
        """JSON序列化"""
        return json.dumps(value, ensure_ascii=False)
    
    def _json_deserialize(self, data: str) -> Any:
        """JSON反序列化"""
        return json.loads(data)
    
    def _pickle_serialize(self, value: Any) -> bytes:
        """Pickle序列化"""
        return pickle.dumps(value)
    
    def _pickle_deserialize(self, data: bytes) -> Any:
        """Pickle反序列化"""
        return pickle.loads(data)
    
    def _raw_serialize(self, value: Any) -> Any:
        """原始数据(不序列化)"""
        return value
    
    def _raw_deserialize(self, data: Any) -> Any:
        """原始数据(不反序列化)"""
        return data
    
    async def _maybe_cleanup(self):
        """定期清理过期项"""
        now = time.time()
        if (now - self._last_cleanup) > self.cleanup_interval:
            await self._cleanup_expired()
            self._last_cleanup = now
    
    async def _cleanup_expired(self):
        """清理过期项"""
        try:
            expired_keys = []
            
            # 检查所有缓存中的过期项
            for cache_dict in [self.hot_cache, self.memory_cache, self.warm_cache]:
                for key, entry in cache_dict.items():
                    if self._is_expired(entry):
                        expired_keys.append(key)
            
            # 删除过期项
            for key in expired_keys:
                await self.delete(key)
            
            if expired_keys:
                logger.debug(f"清理过期缓存项: {len(expired_keys)} 个")
            
            self.stats.last_cleanup = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"清理过期缓存失败: {e}")
    
    def get_stats(self) -> CacheStats:
        """获取缓存统计信息"""
        # 更新统计信息
        self.stats.memory_entries = len(self.memory_cache) + len(self.hot_cache)
        self.stats.total_entries = self.stats.memory_entries + len(self.warm_cache)
        
        # 计算命中率
        total_requests = self.stats.total_hits + self.stats.total_misses
        if total_requests > 0:
            self.stats.hit_rate = self.stats.total_hits / total_requests
        
        # 计算内存使用
        memory_usage = 0
        for cache_dict in [self.hot_cache, self.memory_cache, self.warm_cache]:
            for entry in cache_dict.values():
                memory_usage += entry.size_bytes
        self.stats.memory_usage_bytes = memory_usage
        
        return self.stats


# 全局实例管理
_unified_cache_service: Optional[UnifiedCacheService] = None


def get_unified_cache_service(
    cache_dir: Optional[Path] = None,
    **kwargs
) -> UnifiedCacheService:
    """获取统一缓存服务实例"""
    global _unified_cache_service
    
    if _unified_cache_service is None:
        from core.environment_manager import get_environment_manager
        
        # 如果没有指定缓存目录，使用环境管理器的缓存目录
        if cache_dir is None:
            env_manager = get_environment_manager()
            cache_dir = env_manager.get_cache_dir()
        
        _unified_cache_service = UnifiedCacheService(
            cache_dir=cache_dir,
            **kwargs
        )
    
    return _unified_cache_service


async def cleanup_unified_cache_service():
    """清理统一缓存服务"""
    global _unified_cache_service
    
    if _unified_cache_service:
        try:
            await _unified_cache_service.clear()
            logger.info("💾 UnifiedCacheService 已清理")
        except Exception as e:
            logger.error(f"清理UnifiedCacheService失败: {e}")
        finally:
            _unified_cache_service = None