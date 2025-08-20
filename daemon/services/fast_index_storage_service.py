#!/usr/bin/env python3
"""
快速索引存储服务
专门处理来自文件系统连接器的快速索引事件，提供Everything级别的搜索性能
"""

import logging
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from core.service_facade import get_service
from models.database_models import EntityMetadata
from services.storage.core.database import UnifiedDatabaseService

logger = logging.getLogger(__name__)


@dataclass
class FastIndexEntry:
    """快速索引条目"""
    path: str
    name: str
    size: int
    is_directory: bool
    extension: str
    last_modified: datetime
    priority: int
    indexed_at: datetime


class FastIndexStorageService:
    """
    快速索引存储服务
    
    使用专门优化的数据结构存储文件系统快速索引，支持：
    - 极速文件名搜索（类似Everything）
    - 路径前缀匹配
    - 扩展名过滤
    - 大小和时间范围查询
    """
    
    def __init__(self):
        self._db_service = None
        self._fast_db_path = None
        self._fast_db_connection = None
        self._db_lock = threading.RLock()
        self._initialized = False
        self._stats = {
            'total_entries': 0,
            'last_update': None,
            'index_start_time': None,
            'index_completion_time': None
        }
        
    @property
    def db_service(self):
        """懒加载数据库服务"""
        if self._db_service is None:
            try:
                self._db_service = get_service(UnifiedDatabaseService)
            except Exception as e:
                logger.warning(f"Database service not available: {str(e)}")
                return None
        return self._db_service
    
    def initialize(self) -> bool:
        """初始化快速索引存储"""
        if self._initialized:
            return True
            
        try:
            # 获取数据库路径
            if self.db_service and hasattr(self.db_service, 'database_url'):
                db_dir = Path(self.db_service.database_url).parent
                self._fast_db_path = db_dir / "fast_index.db"
            else:
                # 回退路径
                from core.environment_manager import EnvironmentManager
                env_manager = EnvironmentManager()
                self._fast_db_path = env_manager.current_config.data_dir / "fast_index.db"
            
            # 创建快速索引数据库
            self._create_fast_index_database()
            self._initialized = True
            
            logger.info(f"🚀 快速索引存储服务初始化完成: {self._fast_db_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 快速索引存储服务初始化失败: {e}")
            return False
    
    def _create_fast_index_database(self):
        """创建快速索引数据库"""
        with self._db_lock:
            try:
                self._fast_db_connection = sqlite3.connect(
                    str(self._fast_db_path),
                    check_same_thread=False,
                    timeout=30.0
                )
                
                # 启用性能优化
                self._fast_db_connection.execute("PRAGMA journal_mode=WAL")
                self._fast_db_connection.execute("PRAGMA synchronous=NORMAL")
                self._fast_db_connection.execute("PRAGMA cache_size=10000")
                self._fast_db_connection.execute("PRAGMA temp_store=MEMORY")
                
                # 创建快速索引表
                self._fast_db_connection.execute("""
                    CREATE TABLE IF NOT EXISTS fast_index (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        path TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        name_lower TEXT NOT NULL,  -- 小写文件名用于快速搜索
                        parent_path TEXT NOT NULL,
                        size INTEGER DEFAULT 0,
                        is_directory BOOLEAN DEFAULT 0,
                        extension TEXT DEFAULT '',
                        last_modified INTEGER NOT NULL,  -- Unix时间戳
                        priority INTEGER DEFAULT 2,
                        indexed_at INTEGER NOT NULL,
                        UNIQUE(path)
                    )
                """)
                
                # 创建优化索引
                indices = [
                    "CREATE INDEX IF NOT EXISTS idx_name_lower ON fast_index(name_lower)",
                    "CREATE INDEX IF NOT EXISTS idx_parent_path ON fast_index(parent_path)",
                    "CREATE INDEX IF NOT EXISTS idx_extension ON fast_index(extension)",
                    "CREATE INDEX IF NOT EXISTS idx_size ON fast_index(size)",
                    "CREATE INDEX IF NOT EXISTS idx_last_modified ON fast_index(last_modified)",
                    "CREATE INDEX IF NOT EXISTS idx_is_directory ON fast_index(is_directory)",
                    "CREATE INDEX IF NOT EXISTS idx_priority ON fast_index(priority)",
                    # 复合索引用于复杂查询
                    "CREATE INDEX IF NOT EXISTS idx_name_ext ON fast_index(name_lower, extension)",
                    "CREATE INDEX IF NOT EXISTS idx_parent_name ON fast_index(parent_path, name_lower)"
                ]
                
                for idx_sql in indices:
                    self._fast_db_connection.execute(idx_sql)
                
                # 创建统计表
                self._fast_db_connection.execute("""
                    CREATE TABLE IF NOT EXISTS index_stats (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at INTEGER NOT NULL
                    )
                """)
                
                self._fast_db_connection.commit()
                logger.info("✅ 快速索引数据库表创建完成")
                
            except Exception as e:
                logger.error(f"❌ 创建快速索引数据库失败: {e}")
                raise
    
    async def store_fast_index_batch(self, entries: List[Dict[str, Any]]) -> bool:
        """
        批量存储快速索引条目
        
        Args:
            entries: 快速索引条目列表
            
        Returns:
            bool: 存储是否成功
        """
        if not self._initialized:
            if not self.initialize():
                return False
        
        if not entries:
            return True
            
        try:
            with self._db_lock:
                cursor = self._fast_db_connection.cursor()
                
                # 准备批量插入数据
                insert_data = []
                current_time = int(datetime.utcnow().timestamp())
                
                for entry in entries:
                    path = entry.get('path', '')
                    name = entry.get('name', '')
                    
                    if not path or not name:
                        continue
                    
                    # 解析路径信息
                    path_obj = Path(path)
                    parent_path = str(path_obj.parent)
                    name_lower = name.lower()
                    extension = entry.get('extension', path_obj.suffix.lower())
                    
                    # 处理修改时间
                    last_modified = entry.get('last_modified', current_time)
                    if isinstance(last_modified, float):
                        last_modified = int(last_modified)
                    elif isinstance(last_modified, str):
                        try:
                            last_modified = int(datetime.fromisoformat(last_modified).timestamp())
                        except:
                            last_modified = current_time
                    
                    insert_data.append((
                        path,
                        name,
                        name_lower,
                        parent_path,
                        entry.get('size', 0),
                        entry.get('is_directory', False),
                        extension,
                        last_modified,
                        entry.get('priority', 2),
                        current_time
                    ))
                
                if not insert_data:
                    return True
                
                # 使用 REPLACE 进行批量插入（更新已存在的条目）
                cursor.executemany("""
                    REPLACE INTO fast_index (
                        path, name, name_lower, parent_path, size, 
                        is_directory, extension, last_modified, priority, indexed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, insert_data)
                
                # 更新统计信息
                total_count = cursor.execute("SELECT COUNT(*) FROM fast_index").fetchone()[0]
                self._update_stats(total_count, current_time)
                
                self._fast_db_connection.commit()
                
                logger.info(f"✅ 批量存储快速索引: {len(insert_data)} 条目，总计: {total_count}")
                return True
                
        except Exception as e:
            logger.error(f"❌ 批量存储快速索引失败: {e}")
            if self._fast_db_connection:
                self._fast_db_connection.rollback()
            return False
    
    def search_files(
        self,
        query: str,
        limit: int = 100,
        extension_filter: Optional[str] = None,
        directory_only: bool = False,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        快速文件搜索（类似Everything）
        
        Args:
            query: 搜索查询（支持通配符）
            limit: 结果限制
            extension_filter: 扩展名过滤
            directory_only: 仅搜索目录
            min_size: 最小文件大小
            max_size: 最大文件大小
            
        Returns:
            搜索结果列表
        """
        if not self._initialized:
            if not self.initialize():
                return []
        
        try:
            with self._db_lock:
                cursor = self._fast_db_connection.cursor()
                
                # 构建查询条件
                conditions = []
                params = []
                
                # 文件名搜索（支持通配符）
                if query.strip():
                    query_lower = query.lower().replace('*', '%').replace('?', '_')
                    if '%' in query_lower or '_' in query_lower:
                        conditions.append("name_lower LIKE ?")
                    else:
                        conditions.append("name_lower LIKE ?")
                        query_lower = f"%{query_lower}%"
                    params.append(query_lower)
                
                # 扩展名过滤
                if extension_filter:
                    if not extension_filter.startswith('.'):
                        extension_filter = '.' + extension_filter
                    conditions.append("extension = ?")
                    params.append(extension_filter.lower())
                
                # 目录过滤
                if directory_only:
                    conditions.append("is_directory = 1")
                else:
                    # 默认不仅限于目录
                    pass
                
                # 文件大小过滤
                if min_size is not None:
                    conditions.append("size >= ?")
                    params.append(min_size)
                
                if max_size is not None:
                    conditions.append("size <= ?")
                    params.append(max_size)
                
                # 构建完整查询
                where_clause = " AND ".join(conditions) if conditions else "1=1"
                sql = f"""
                    SELECT path, name, size, is_directory, extension, 
                           last_modified, priority, parent_path
                    FROM fast_index 
                    WHERE {where_clause}
                    ORDER BY priority ASC, name_lower ASC
                    LIMIT ?
                """
                params.append(limit)
                
                cursor.execute(sql, params)
                results = cursor.fetchall()
                
                # 转换结果格式
                search_results = []
                for row in results:
                    search_results.append({
                        'path': row[0],
                        'name': row[1],
                        'size': row[2],
                        'is_directory': bool(row[3]),
                        'extension': row[4],
                        'last_modified': datetime.fromtimestamp(row[5]),
                        'priority': row[6],
                        'parent_path': row[7]
                    })
                
                logger.debug(f"🔍 快速搜索完成: 查询='{query}', 结果={len(search_results)}")
                return search_results
                
        except Exception as e:
            logger.error(f"❌ 快速搜索失败: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        if not self._initialized:
            return self._stats.copy()
        
        try:
            with self._db_lock:
                cursor = self._fast_db_connection.cursor()
                
                # 获取总条目数
                total_count = cursor.execute("SELECT COUNT(*) FROM fast_index").fetchone()[0]
                
                # 获取按类型统计
                type_stats = cursor.execute("""
                    SELECT is_directory, COUNT(*) 
                    FROM fast_index 
                    GROUP BY is_directory
                """).fetchall()
                
                files_count = 0
                dirs_count = 0
                for is_dir, count in type_stats:
                    if is_dir:
                        dirs_count = count
                    else:
                        files_count = count
                
                # 获取最近更新时间
                last_update = cursor.execute("""
                    SELECT MAX(indexed_at) FROM fast_index
                """).fetchone()[0]
                
                if last_update:
                    last_update = datetime.fromtimestamp(last_update)
                
                return {
                    'total_entries': total_count,
                    'files_count': files_count,
                    'directories_count': dirs_count,
                    'last_update': last_update,
                    'database_size': self._fast_db_path.stat().st_size if self._fast_db_path.exists() else 0,
                    'index_start_time': self._stats.get('index_start_time'),
                    'index_completion_time': self._stats.get('index_completion_time')
                }
                
        except Exception as e:
            logger.error(f"❌ 获取统计信息失败: {e}")
            return self._stats.copy()
    
    def _update_stats(self, total_count: int, timestamp: int):
        """更新统计信息"""
        try:
            cursor = self._fast_db_connection.cursor()
            
            stats_data = [
                ('total_entries', str(total_count), timestamp),
                ('last_update', str(timestamp), timestamp)
            ]
            
            cursor.executemany("""
                REPLACE INTO index_stats (key, value, updated_at) 
                VALUES (?, ?, ?)
            """, stats_data)
            
            self._stats['total_entries'] = total_count
            self._stats['last_update'] = datetime.fromtimestamp(timestamp)
            
        except Exception as e:
            logger.error(f"❌ 更新统计信息失败: {e}")
    
    def clear_index(self) -> bool:
        """清空快速索引"""
        if not self._initialized:
            return True
            
        try:
            with self._db_lock:
                cursor = self._fast_db_connection.cursor()
                cursor.execute("DELETE FROM fast_index")
                cursor.execute("DELETE FROM index_stats")
                self._fast_db_connection.commit()
                
                self._stats = {
                    'total_entries': 0,
                    'last_update': None,
                    'index_start_time': None,
                    'index_completion_time': None
                }
                
                logger.info("🧹 快速索引已清空")
                return True
                
        except Exception as e:
            logger.error(f"❌ 清空快速索引失败: {e}")
            return False
    
    def close(self):
        """关闭服务"""
        if self._fast_db_connection:
            self._fast_db_connection.close()
            self._fast_db_connection = None
        self._initialized = False
        logger.info("📦 快速索引存储服务已关闭")