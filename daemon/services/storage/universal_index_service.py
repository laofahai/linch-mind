#!/usr/bin/env python3
"""
通用索引服务 - 真正连接器无关的搜索索引架构

重构目标：
- 替代FastIndexStorageService的文件系统特定实现
- 支持任意连接器的快速搜索需求 (文件、邮件、网页、联系人等)
- 保持Everything级别的搜索性能 (< 5ms)
- 基于内容类型的智能索引策略
"""

import asyncio
import logging
import sqlite3
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass
from enum import Enum

from core.service_facade import get_service
from core.environment_manager import EnvironmentManager
from services.unified_database_service import UnifiedDatabaseService

logger = logging.getLogger(__name__)


class IndexTier(Enum):
    """索引层级 - 根据性能需求分层处理"""
    HOT = "hot"      # 极速搜索，类似Everything (< 5ms)
    WARM = "warm"    # 标准搜索，平衡性能和功能 (< 50ms)  
    COLD = "cold"    # 语义搜索，功能丰富但较慢 (< 500ms)


class ContentType(Enum):
    """通用内容类型 - 连接器无关"""
    FILE_PATH = "file_path"      # 文件路径
    URL = "url"                  # 网址
    EMAIL = "email"              # 邮箱地址
    PHONE = "phone"              # 电话号码
    TEXT = "text"                # 纯文本
    CONTACT = "contact"          # 联系人
    DOCUMENT = "document"        # 文档内容
    IMAGE = "image"              # 图片
    AUDIO = "audio"              # 音频
    VIDEO = "video"              # 视频
    CODE = "code"                # 代码
    OTHER = "other"              # 其他类型


@dataclass
class UniversalIndexEntry:
    """通用索引条目 - 支持所有连接器类型"""
    # 核心字段 (所有条目必需)
    id: str                      # 唯一标识符
    connector_id: str            # 连接器ID
    content_type: ContentType    # 内容类型
    primary_key: str             # 主键 (如文件路径、URL等)
    searchable_text: str         # 统一搜索文本
    display_name: str            # 显示名称
    
    # 性能优化字段
    index_tier: IndexTier        # 索引层级
    priority: int                # 搜索优先级 (1-10, 越小越优先)
    
    # 时间字段
    indexed_at: datetime         # 索引时间
    last_modified: Optional[datetime] = None  # 内容修改时间
    last_accessed: Optional[datetime] = None  # 最后访问时间
    
    # 扩展字段 (连接器特定)
    structured_data: Dict[str, Any] = None  # 结构化数据
    metadata: Dict[str, Any] = None         # 元数据
    
    # 搜索优化字段
    keywords: Set[str] = None               # 关键词集合
    tags: Set[str] = None                   # 标签集合
    
    def __post_init__(self):
        if self.structured_data is None:
            self.structured_data = {}
        if self.metadata is None:
            self.metadata = {}
        if self.keywords is None:
            self.keywords = set()
        if self.tags is None:
            self.tags = set()


@dataclass 
class SearchQuery:
    """通用搜索查询"""
    text: str                           # 搜索文本
    content_types: List[ContentType] = None  # 内容类型过滤
    connector_ids: List[str] = None     # 连接器过滤
    index_tiers: List[IndexTier] = None # 索引层级过滤
    limit: int = 100                    # 结果限制
    min_priority: int = 1               # 最小优先级
    max_priority: int = 10              # 最大优先级
    include_metadata: bool = False      # 是否包含元数据
    
    def __post_init__(self):
        if self.content_types is None:
            self.content_types = []
        if self.connector_ids is None:
            self.connector_ids = []
        if self.index_tiers is None:
            self.index_tiers = [IndexTier.HOT, IndexTier.WARM, IndexTier.COLD]


@dataclass
class SearchResult:
    """搜索结果"""
    entry: UniversalIndexEntry
    score: float                        # 搜索相关性评分
    highlights: List[str] = None        # 高亮片段
    
    def __post_init__(self):
        if self.highlights is None:
            self.highlights = []


class IndexingStrategy:
    """索引策略管理器"""
    
    def __init__(self):
        # 根据内容类型决定索引层级 - 不依赖具体连接器ID
        # 将来应从连接器元数据动态获取其特性和优先级
        self._tier_rules = {
            # 基于内容类型的通用规则
            
            # 默认规则
            ("*", ContentType.FILE_PATH): IndexTier.HOT,
            ("*", ContentType.URL): IndexTier.WARM,
            ("*", ContentType.EMAIL): IndexTier.WARM,
            ("*", ContentType.PHONE): IndexTier.WARM,
            ("*", ContentType.TEXT): IndexTier.COLD,
        }
    
    def get_index_tier(self, connector_id: str, content_type: ContentType) -> IndexTier:
        """获取索引层级"""
        # 精确匹配
        key = (connector_id, content_type)
        if key in self._tier_rules:
            return self._tier_rules[key]
        
        # 通配符匹配
        wildcard_key = ("*", content_type)
        if wildcard_key in self._tier_rules:
            return self._tier_rules[wildcard_key]
        
        # 默认为冷层
        return IndexTier.COLD
    
    def get_priority(self, connector_id: str, content_type: ContentType) -> int:
        """获取搜索优先级"""
        tier = self.get_index_tier(connector_id, content_type)
        
        if tier == IndexTier.HOT:
            return 1  # 最高优先级
        elif tier == IndexTier.WARM:
            return 5  # 中等优先级
        else:
            return 8  # 较低优先级


class ContentTypeDetector:
    """内容类型检测器"""
    
    @staticmethod
    def detect_content_type(
        connector_id: str,
        event_type: str, 
        event_data: Dict[str, Any]
    ) -> ContentType:
        """
        智能检测内容类型
        
        Args:
            connector_id: 连接器ID
            event_type: 事件类型
            event_data: 事件数据
            
        Returns:
            检测到的内容类型
        """
        # 1. 基于事件类型判断（不依赖具体连接器ID）
        if "file" in event_type.lower():
            return ContentType.FILE_PATH
        elif "url" in event_type.lower() or "link" in event_type.lower():
            return ContentType.URL
        elif "email" in event_type.lower():
            return ContentType.EMAIL
        elif "phone" in event_type.lower():
            return ContentType.PHONE
        elif "contact" in event_type.lower():
            return ContentType.CONTACT
        
        # 3. 基于数据内容启发式判断
        content = ContentTypeDetector._extract_content(event_data)
        if content:
            content_lower = content.lower()
            
            # URL检测
            if content.startswith(("http://", "https://", "ftp://", "file://")):
                return ContentType.URL
            
            # 文件路径检测
            if ("/" in content or "\\" in content) and any(
                content.endswith(ext) for ext in [
                    ".txt", ".doc", ".pdf", ".jpg", ".png", ".mp4", ".mp3"
                ]
            ):
                return ContentType.FILE_PATH
            
            # 邮箱检测
            if "@" in content and "." in content.split("@")[-1]:
                return ContentType.EMAIL
            
            # 电话号码检测 (简单匹配)
            if len(content.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")) >= 10:
                digits = sum(c.isdigit() for c in content)
                if digits >= 7:  # 至少7个数字
                    return ContentType.PHONE
        
        # 4. 默认为文本
        return ContentType.TEXT
    
    @staticmethod
    def _extract_content(event_data: Dict[str, Any]) -> Optional[str]:
        """从事件数据中提取内容用于检测"""
        # 常见内容字段
        for field in ["path", "url", "content", "text", "data", "value", "name"]:
            if field in event_data:
                value = event_data[field]
                if isinstance(value, str) and value.strip():
                    return value.strip()
        return None


class UniversalIndexService:
    """
    通用索引服务 - 真正的连接器无关架构
    
    核心功能：
    1. 支持任意连接器的快速搜索需求
    2. 基于内容类型的智能索引分层
    3. 保持Everything级别搜索性能
    4. 完全替代FastIndexStorageService
    """
    
    def __init__(self):
        self._db_service = None
        self._universal_db_path = None
        self._universal_db_connection = None
        self._db_lock = threading.RLock()
        self._initialized = False
        
        # 策略组件
        self._indexing_strategy = IndexingStrategy()
        self._content_detector = ContentTypeDetector()
        
        # 统计信息
        self._stats = {
            'total_entries': 0,
            'entries_by_tier': {tier.value: 0 for tier in IndexTier},
            'entries_by_type': {ct.value: 0 for ct in ContentType},
            'entries_by_connector': {},
            'last_update': None,
            'search_requests': 0,
            'avg_search_time_ms': 0.0
        }
        
        logger.info("🌟 UniversalIndexService 初始化")
    
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
        """初始化通用索引服务"""
        if self._initialized:
            return True
            
        try:
            # 获取数据库路径
            if self.db_service and hasattr(self.db_service, 'database_url'):
                db_dir = Path(self.db_service.database_url).parent
                self._universal_db_path = db_dir / "universal_index.db"
            else:
                # 回退路径
                env_manager = EnvironmentManager()
                self._universal_db_path = env_manager.current_config.data_dir / "universal_index.db"
            
            # 创建通用索引数据库
            self._create_universal_database()
            self._initialized = True
            
            logger.info(f"🚀 通用索引服务初始化完成: {self._universal_db_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 通用索引服务初始化失败: {e}")
            return False
    
    def _create_universal_database(self):
        """创建通用索引数据库"""
        with self._db_lock:
            try:
                self._universal_db_connection = sqlite3.connect(
                    str(self._universal_db_path),
                    check_same_thread=False,
                    timeout=30.0
                )
                
                # 启用性能优化
                self._universal_db_connection.execute("PRAGMA journal_mode=WAL")
                self._universal_db_connection.execute("PRAGMA synchronous=NORMAL")
                self._universal_db_connection.execute("PRAGMA cache_size=20000")
                self._universal_db_connection.execute("PRAGMA temp_store=MEMORY")
                self._universal_db_connection.execute("PRAGMA optimize")
                
                # 创建通用索引表 - 支持所有连接器类型
                self._universal_db_connection.execute("""
                    CREATE TABLE IF NOT EXISTS universal_index (
                        id TEXT PRIMARY KEY,
                        connector_id TEXT NOT NULL,
                        content_type TEXT NOT NULL,
                        primary_key TEXT NOT NULL,
                        primary_key_lower TEXT NOT NULL,  -- 小写主键用于快速搜索
                        searchable_text TEXT NOT NULL,
                        searchable_text_lower TEXT NOT NULL,  -- 小写搜索文本
                        display_name TEXT NOT NULL,
                        display_name_lower TEXT NOT NULL,  -- 小写显示名称
                        
                        -- 性能分层
                        index_tier TEXT NOT NULL,
                        priority INTEGER NOT NULL DEFAULT 5,
                        
                        -- 时间字段
                        indexed_at INTEGER NOT NULL,
                        last_modified INTEGER,
                        last_accessed INTEGER,
                        
                        -- 结构化数据 (JSON)
                        structured_data TEXT,  -- JSON格式
                        metadata TEXT,         -- JSON格式
                        
                        -- 搜索优化
                        keywords TEXT,         -- 逗号分隔的关键词
                        tags TEXT,             -- 逗号分隔的标签
                        
                        UNIQUE(connector_id, primary_key)
                    )
                """)
                
                # 创建高性能索引 - 针对不同搜索场景优化
                indices = [
                    # 主搜索索引 (按层级优化)
                    "CREATE INDEX IF NOT EXISTS idx_hot_search ON universal_index(index_tier, priority, searchable_text_lower) WHERE index_tier = 'hot'",
                    "CREATE INDEX IF NOT EXISTS idx_warm_search ON universal_index(index_tier, priority, searchable_text_lower) WHERE index_tier = 'warm'", 
                    "CREATE INDEX IF NOT EXISTS idx_cold_search ON universal_index(index_tier, searchable_text_lower) WHERE index_tier = 'cold'",
                    
                    # 显示名称搜索
                    "CREATE INDEX IF NOT EXISTS idx_display_name ON universal_index(display_name_lower)",
                    "CREATE INDEX IF NOT EXISTS idx_primary_key ON universal_index(primary_key_lower)",
                    
                    # 分类搜索
                    "CREATE INDEX IF NOT EXISTS idx_connector_type ON universal_index(connector_id, content_type)",
                    "CREATE INDEX IF NOT EXISTS idx_content_type ON universal_index(content_type, priority)",
                    "CREATE INDEX IF NOT EXISTS idx_connector_id ON universal_index(connector_id, priority)",
                    
                    # 时间范围搜索
                    "CREATE INDEX IF NOT EXISTS idx_last_modified ON universal_index(last_modified)",
                    "CREATE INDEX IF NOT EXISTS idx_indexed_at ON universal_index(indexed_at)",
                    
                    # 复合索引 (高频查询优化)
                    "CREATE INDEX IF NOT EXISTS idx_connector_search ON universal_index(connector_id, searchable_text_lower, priority)",
                    "CREATE INDEX IF NOT EXISTS idx_type_search ON universal_index(content_type, searchable_text_lower, priority)",
                ]
                
                for idx_sql in indices:
                    self._universal_db_connection.execute(idx_sql)
                
                # 创建统计表
                self._universal_db_connection.execute("""
                    CREATE TABLE IF NOT EXISTS index_stats (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at INTEGER NOT NULL
                    )
                """)
                
                # 创建搜索日志表 (性能监控)
                self._universal_db_connection.execute("""
                    CREATE TABLE IF NOT EXISTS search_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        query_text TEXT NOT NULL,
                        content_types TEXT,  -- JSON array
                        connector_ids TEXT,  -- JSON array
                        result_count INTEGER NOT NULL,
                        search_time_ms REAL NOT NULL,
                        timestamp INTEGER NOT NULL
                    )
                """)
                
                self._universal_db_connection.commit()
                logger.info("✅ 通用索引数据库表创建完成")
                
            except Exception as e:
                logger.error(f"❌ 创建通用索引数据库失败: {e}")
                raise
    
    async def index_content_batch(self, entries: List[Dict[str, Any]]) -> bool:
        """
        批量索引内容 - 通用接口支持所有连接器
        
        Args:
            entries: 通用索引条目列表，格式：
            [
                {
                    "connector_id": "filesystem",
                    "event_type": "file_indexed", 
                    "event_data": {...},
                    "timestamp": "2025-08-15T19:00:00Z",
                    "metadata": {...}
                },
                ...
            ]
            
        Returns:
            bool: 索引是否成功
        """
        if not self._initialized:
            if not self.initialize():
                return False
        
        if not entries:
            return True
            
        try:
            with self._db_lock:
                cursor = self._universal_db_connection.cursor()
                
                # 准备批量插入数据
                insert_data = []
                current_time = int(datetime.utcnow().timestamp())
                
                for entry_data in entries:
                    try:
                        # 转换为通用索引条目
                        index_entry = self._convert_to_index_entry(entry_data, current_time)
                        if index_entry:
                            insert_data.append(self._prepare_db_row(index_entry))
                    except Exception as e:
                        logger.warning(f"处理索引条目失败: {e}")
                        continue
                
                if not insert_data:
                    return True
                
                # 使用 REPLACE 进行批量插入（更新已存在的条目）
                cursor.executemany("""
                    REPLACE INTO universal_index (
                        id, connector_id, content_type, primary_key, primary_key_lower,
                        searchable_text, searchable_text_lower, display_name, display_name_lower,
                        index_tier, priority, indexed_at, last_modified, last_accessed,
                        structured_data, metadata, keywords, tags
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, insert_data)
                
                # 更新统计信息
                self._update_stats_batch(insert_data, current_time)
                
                self._universal_db_connection.commit()
                
                logger.info(f"✅ 批量索引内容: {len(insert_data)} 条目")
                return True
                
        except Exception as e:
            logger.error(f"❌ 批量索引内容失败: {e}")
            if self._universal_db_connection:
                self._universal_db_connection.rollback()
            return False
    
    def _convert_to_index_entry(self, entry_data: Dict[str, Any], current_time: int) -> Optional[UniversalIndexEntry]:
        """将通用事件数据转换为索引条目"""
        try:
            connector_id = entry_data.get("connector_id", "")
            event_type = entry_data.get("event_type", "")
            event_data = entry_data.get("event_data", {})
            metadata = entry_data.get("metadata", {})
            
            if not connector_id or not event_data:
                return None
            
            # 智能检测内容类型
            content_type = self._content_detector.detect_content_type(
                connector_id, event_type, event_data
            )
            
            # 提取主键和显示名称
            primary_key = self._extract_primary_key(content_type, event_data)
            if not primary_key:
                return None
            
            display_name = self._extract_display_name(content_type, event_data, primary_key)
            searchable_text = self._extract_searchable_text(content_type, event_data, display_name)
            
            # 确定索引策略
            index_tier = self._indexing_strategy.get_index_tier(connector_id, content_type)
            priority = self._indexing_strategy.get_priority(connector_id, content_type)
            
            # 生成唯一ID
            entry_id = f"{connector_id}:{content_type.value}:{hash(primary_key) % 1000000}"
            
            # 处理时间戳
            last_modified = self._extract_timestamp(event_data.get("last_modified") or event_data.get("modified_time"))
            
            # 提取关键词和标签
            keywords = self._extract_keywords(searchable_text, event_data)
            tags = self._extract_tags(content_type, event_data, metadata)
            
            return UniversalIndexEntry(
                id=entry_id,
                connector_id=connector_id,
                content_type=content_type,
                primary_key=primary_key,
                searchable_text=searchable_text,
                display_name=display_name,
                index_tier=index_tier,
                priority=priority,
                indexed_at=datetime.fromtimestamp(current_time),
                last_modified=last_modified,
                structured_data=event_data,
                metadata=metadata,
                keywords=keywords,
                tags=tags
            )
            
        except Exception as e:
            logger.error(f"转换索引条目失败: {e}")
            return None
    
    def _extract_primary_key(self, content_type: ContentType, event_data: Dict[str, Any]) -> Optional[str]:
        """提取主键"""
        if content_type == ContentType.FILE_PATH:
            return event_data.get("path")
        elif content_type == ContentType.URL:
            return event_data.get("url") or event_data.get("content")
        elif content_type == ContentType.EMAIL:
            return event_data.get("email") or event_data.get("content")
        elif content_type == ContentType.PHONE:
            return event_data.get("phone") or event_data.get("content")
        else:
            # 通用情况：尝试多个字段
            for field in ["path", "url", "content", "text", "data", "value", "id"]:
                if field in event_data and event_data[field]:
                    return str(event_data[field])
        return None
    
    def _extract_display_name(self, content_type: ContentType, event_data: Dict[str, Any], primary_key: str) -> str:
        """提取显示名称"""
        # 优先使用明确的名称字段
        if "name" in event_data and event_data["name"]:
            return str(event_data["name"])
        
        # 根据内容类型智能提取
        if content_type == ContentType.FILE_PATH:
            return Path(primary_key).name if primary_key else "Unknown File"
        elif content_type == ContentType.URL:
            # 提取域名作为显示名称
            try:
                from urllib.parse import urlparse
                parsed = urlparse(primary_key)
                return parsed.netloc or primary_key
            except:
                return primary_key
        else:
            # 截断长文本
            display = primary_key if primary_key else "Unknown"
            return display[:100] + "..." if len(display) > 100 else display
    
    def _extract_searchable_text(self, content_type: ContentType, event_data: Dict[str, Any], display_name: str) -> str:
        """提取可搜索文本"""
        text_parts = [display_name]
        
        # 添加内容字段
        for field in ["content", "text", "description", "title", "body"]:
            if field in event_data and event_data[field]:
                text_parts.append(str(event_data[field]))
        
        # 对于文件路径，添加路径组件
        if content_type == ContentType.FILE_PATH:
            path = event_data.get("path", "")
            if path:
                # 添加目录名
                text_parts.extend(Path(path).parts)
        
        return " ".join(text_parts)
    
    def _extract_timestamp(self, timestamp_data: Any) -> Optional[datetime]:
        """提取时间戳"""
        if not timestamp_data:
            return None
            
        try:
            if isinstance(timestamp_data, (int, float)):
                return datetime.fromtimestamp(timestamp_data)
            elif isinstance(timestamp_data, str):
                return datetime.fromisoformat(timestamp_data.replace('Z', '+00:00'))
            else:
                return None
        except:
            return None
    
    def _extract_keywords(self, searchable_text: str, event_data: Dict[str, Any]) -> Set[str]:
        """提取关键词"""
        keywords = set()
        
        # 从搜索文本中提取
        if searchable_text:
            # 简单分词 (可以后续使用更复杂的NLP)
            words = searchable_text.lower().split()
            keywords.update(word.strip(".,!?;:\"'()[]{}") for word in words if len(word) >= 3)
        
        # 从扩展名提取 (文件系统)
        if "extension" in event_data and event_data["extension"]:
            ext = str(event_data["extension"]).lower().lstrip(".")
            keywords.add(ext)
        
        return keywords
    
    def _extract_tags(self, content_type: ContentType, event_data: Dict[str, Any], metadata: Dict[str, Any]) -> Set[str]:
        """提取标签"""
        tags = set()
        
        # 内容类型标签
        tags.add(content_type.value)
        
        # 从元数据提取
        if metadata:
            for key, value in metadata.items():
                if isinstance(value, str) and len(value) < 50:
                    tags.add(f"{key}:{value}")
        
        # 文件特定标签
        if content_type == ContentType.FILE_PATH:
            if event_data.get("is_directory"):
                tags.add("directory")
            else:
                tags.add("file")
                
            # 文件大小标签
            size = event_data.get("size", 0)
            if isinstance(size, (int, float)):
                if size < 1024:
                    tags.add("size:tiny")
                elif size < 1024 * 1024:
                    tags.add("size:small") 
                elif size < 1024 * 1024 * 10:
                    tags.add("size:medium")
                else:
                    tags.add("size:large")
        
        return tags
    
    def _prepare_db_row(self, entry: UniversalIndexEntry) -> tuple:
        """准备数据库行数据"""
        import json
        
        return (
            entry.id,
            entry.connector_id,
            entry.content_type.value,
            entry.primary_key,
            entry.primary_key.lower(),
            entry.searchable_text,
            entry.searchable_text.lower(),
            entry.display_name,
            entry.display_name.lower(),
            entry.index_tier.value,
            entry.priority,
            int(entry.indexed_at.timestamp()),
            int(entry.last_modified.timestamp()) if entry.last_modified else None,
            int(entry.last_accessed.timestamp()) if entry.last_accessed else None,
            json.dumps(entry.structured_data) if entry.structured_data else "{}",
            json.dumps(entry.metadata) if entry.metadata else "{}",
            ",".join(entry.keywords) if entry.keywords else "",
            ",".join(entry.tags) if entry.tags else ""
        )
    
    def _update_stats_batch(self, insert_data: List[tuple], timestamp: int):
        """批量更新统计信息"""
        try:
            # 更新基础统计
            total_count = len(insert_data)
            self._stats['total_entries'] += total_count
            self._stats['last_update'] = datetime.fromtimestamp(timestamp)
            
            # 更新分层统计
            for row in insert_data:
                tier = row[9]  # index_tier
                content_type = row[2]  # content_type
                connector_id = row[1]  # connector_id
                
                self._stats['entries_by_tier'][tier] = self._stats['entries_by_tier'].get(tier, 0) + 1
                self._stats['entries_by_type'][content_type] = self._stats['entries_by_type'].get(content_type, 0) + 1
                self._stats['entries_by_connector'][connector_id] = self._stats['entries_by_connector'].get(connector_id, 0) + 1
            
        except Exception as e:
            logger.error(f"更新统计信息失败: {e}")
    
    def search(self, query: SearchQuery) -> List[SearchResult]:
        """
        通用搜索接口 - 支持所有连接器类型
        
        Args:
            query: 搜索查询
            
        Returns:
            搜索结果列表
        """
        if not self._initialized:
            if not self.initialize():
                return []
        
        start_time = time.time()
        
        try:
            with self._db_lock:
                cursor = self._universal_db_connection.cursor()
                
                # 构建查询条件
                conditions = []
                params = []
                
                # 文本搜索
                if query.text.strip():
                    query_lower = query.text.lower().replace('*', '%').replace('?', '_')
                    if '%' in query_lower or '_' in query_lower:
                        conditions.append("(searchable_text_lower LIKE ? OR display_name_lower LIKE ? OR primary_key_lower LIKE ?)")
                        params.extend([query_lower, query_lower, query_lower])
                    else:
                        conditions.append("(searchable_text_lower LIKE ? OR display_name_lower LIKE ? OR primary_key_lower LIKE ?)")
                        query_pattern = f"%{query_lower}%"
                        params.extend([query_pattern, query_pattern, query_pattern])
                
                # 内容类型过滤
                if query.content_types:
                    type_placeholders = ",".join("?" * len(query.content_types))
                    conditions.append(f"content_type IN ({type_placeholders})")
                    params.extend([ct.value for ct in query.content_types])
                
                # 连接器过滤
                if query.connector_ids:
                    connector_placeholders = ",".join("?" * len(query.connector_ids))
                    conditions.append(f"connector_id IN ({connector_placeholders})")
                    params.extend(query.connector_ids)
                
                # 索引层级过滤
                if query.index_tiers:
                    tier_placeholders = ",".join("?" * len(query.index_tiers))
                    conditions.append(f"index_tier IN ({tier_placeholders})")
                    params.extend([tier.value for tier in query.index_tiers])
                
                # 优先级过滤
                conditions.append("priority BETWEEN ? AND ?")
                params.extend([query.min_priority, query.max_priority])
                
                # 构建完整查询
                where_clause = " AND ".join(conditions) if conditions else "1=1"
                
                # 根据索引层级优化排序策略
                if IndexTier.HOT in query.index_tiers:
                    # 热层优先，极速响应
                    order_by = "index_tier ASC, priority ASC, display_name_lower ASC"
                else:
                    # 标准排序
                    order_by = "priority ASC, index_tier ASC, last_modified DESC"
                
                if query.include_metadata:
                    select_fields = "*"
                else:
                    select_fields = "id, connector_id, content_type, primary_key, searchable_text, display_name, index_tier, priority, indexed_at, last_modified"
                
                sql = f"""
                    SELECT {select_fields}
                    FROM universal_index 
                    WHERE {where_clause}
                    ORDER BY {order_by}
                    LIMIT ?
                """
                params.append(query.limit)
                
                cursor.execute(sql, params)
                results = cursor.fetchall()
                
                # 转换结果格式
                search_results = []
                for row in results:
                    try:
                        result = self._convert_db_row_to_result(row, query.include_metadata)
                        if result:
                            search_results.append(result)
                    except Exception as e:
                        logger.warning(f"转换搜索结果失败: {e}")
                        continue
                
                # 记录搜索性能
                search_time_ms = (time.time() - start_time) * 1000
                self._record_search_performance(query, len(search_results), search_time_ms)
                
                logger.debug(f"🔍 通用搜索完成: 查询='{query.text}', 结果={len(search_results)}, 耗时={search_time_ms:.1f}ms")
                return search_results
                
        except Exception as e:
            logger.error(f"❌ 通用搜索失败: {e}")
            return []
    
    def _convert_db_row_to_result(self, row: tuple, include_metadata: bool) -> Optional[SearchResult]:
        """将数据库行转换为搜索结果"""
        try:
            import json
            
            if include_metadata:
                # 完整数据
                (id, connector_id, content_type, primary_key, _, searchable_text, _, 
                 display_name, _, index_tier, priority, indexed_at, last_modified, 
                 last_accessed, structured_data, metadata, keywords, tags) = row
                
                structured_data_dict = json.loads(structured_data) if structured_data else {}
                metadata_dict = json.loads(metadata) if metadata else {}
                keywords_set = set(keywords.split(",")) if keywords else set()
                tags_set = set(tags.split(",")) if tags else set()
            else:
                # 基础数据
                (id, connector_id, content_type, primary_key, searchable_text,
                 display_name, index_tier, priority, indexed_at, last_modified) = row
                
                structured_data_dict = {}
                metadata_dict = {}
                keywords_set = set()
                tags_set = set()
                last_accessed = None
            
            entry = UniversalIndexEntry(
                id=id,
                connector_id=connector_id,
                content_type=ContentType(content_type),
                primary_key=primary_key,
                searchable_text=searchable_text,
                display_name=display_name,
                index_tier=IndexTier(index_tier),
                priority=priority,
                indexed_at=datetime.fromtimestamp(indexed_at),
                last_modified=datetime.fromtimestamp(last_modified) if last_modified else None,
                last_accessed=datetime.fromtimestamp(last_accessed) if last_accessed else None,
                structured_data=structured_data_dict,
                metadata=metadata_dict,
                keywords=keywords_set,
                tags=tags_set
            )
            
            # 计算简单的相关性评分 (可以后续优化)
            score = 10.0 - priority  # 优先级越低，分数越高
            
            return SearchResult(entry=entry, score=score)
            
        except Exception as e:
            logger.error(f"转换搜索结果失败: {e}")
            return None
    
    def _record_search_performance(self, query: SearchQuery, result_count: int, search_time_ms: float):
        """记录搜索性能"""
        try:
            import json
            
            self._stats['search_requests'] += 1
            
            # 更新平均搜索时间
            current_avg = self._stats['avg_search_time_ms']
            request_count = self._stats['search_requests']
            self._stats['avg_search_time_ms'] = (current_avg * (request_count - 1) + search_time_ms) / request_count
            
            # 记录详细日志 (采样记录，避免日志过多)
            if self._stats['search_requests'] % 100 == 0:  # 每100次记录一次
                with self._db_lock:
                    cursor = self._universal_db_connection.cursor()
                    cursor.execute("""
                        INSERT INTO search_log (
                            query_text, content_types, connector_ids, 
                            result_count, search_time_ms, timestamp
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        query.text,
                        json.dumps([ct.value for ct in query.content_types]),
                        json.dumps(query.connector_ids),
                        result_count,
                        search_time_ms,
                        int(time.time())
                    ))
                    self._universal_db_connection.commit()
            
        except Exception as e:
            logger.warning(f"记录搜索性能失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        if not self._initialized:
            return self._stats.copy()
        
        try:
            with self._db_lock:
                cursor = self._universal_db_connection.cursor()
                
                # 获取实时总数
                total_count = cursor.execute("SELECT COUNT(*) FROM universal_index").fetchone()[0]
                
                # 更新统计
                updated_stats = self._stats.copy()
                updated_stats['total_entries'] = total_count
                updated_stats['database_size'] = self._universal_db_path.stat().st_size if self._universal_db_path.exists() else 0
                
                return updated_stats
                
        except Exception as e:
            logger.error(f"❌ 获取统计信息失败: {e}")
            return self._stats.copy()
    
    def clear_index(self, connector_id: Optional[str] = None) -> bool:
        """清空索引 (可指定连接器)"""
        if not self._initialized:
            return True
            
        try:
            with self._db_lock:
                cursor = self._universal_db_connection.cursor()
                
                if connector_id:
                    cursor.execute("DELETE FROM universal_index WHERE connector_id = ?", (connector_id,))
                    logger.info(f"🧹 清空连接器索引: {connector_id}")
                else:
                    cursor.execute("DELETE FROM universal_index")
                    cursor.execute("DELETE FROM index_stats") 
                    cursor.execute("DELETE FROM search_log")
                    logger.info("🧹 清空全部索引")
                
                self._universal_db_connection.commit()
                
                # 重置统计
                if not connector_id:
                    self._stats = {
                        'total_entries': 0,
                        'entries_by_tier': {tier.value: 0 for tier in IndexTier},
                        'entries_by_type': {ct.value: 0 for ct in ContentType},
                        'entries_by_connector': {},
                        'last_update': None,
                        'search_requests': 0,
                        'avg_search_time_ms': 0.0
                    }
                
                return True
                
        except Exception as e:
            logger.error(f"❌ 清空索引失败: {e}")
            return False
    
    def close(self):
        """关闭服务"""
        if self._universal_db_connection:
            self._universal_db_connection.close()
            self._universal_db_connection = None
        self._initialized = False
        logger.info("📦 通用索引服务已关闭")


# 全局实例管理
_universal_index_service: Optional[UniversalIndexService] = None


def get_universal_index_service() -> UniversalIndexService:
    """获取通用索引服务单例"""
    global _universal_index_service
    
    if _universal_index_service is None:
        _universal_index_service = UniversalIndexService()
        _universal_index_service.initialize()
    
    return _universal_index_service


def cleanup_universal_index_service():
    """清理通用索引服务"""
    global _universal_index_service
    
    if _universal_index_service:
        try:
            _universal_index_service.close()
        except Exception as e:
            logger.error(f"清理通用索引服务失败: {e}")
        finally:
            _universal_index_service = None