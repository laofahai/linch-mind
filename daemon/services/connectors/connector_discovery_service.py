"""
连接器元数据服务 - 从数据库查询已注册连接器

注：已移除文件系统自动扫描功能，只查询数据库中已注册的连接器
新连接器需要通过手动注册或从注册表下载的方式添加
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from threading import RLock
import time

from core.error_handling import (
    ErrorCategory,
    ErrorSeverity,
    handle_errors,
)
from config.config_manager import ConfigManager
from core.service_facade import get_service

logger = logging.getLogger(__name__)


@dataclass
class ConnectorMetadata:
    """连接器元数据"""
    id: str
    name: str
    description: str
    version: str
    author: str
    category: str
    icon: str = "extension"
    capabilities: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    platforms: Dict[str, Any] = field(default_factory=dict)
    config_schema: Optional[Dict[str, Any]] = None
    config_ui_schema: Optional[Dict[str, Any]] = None
    config_default_values: Dict[str, Any] = field(default_factory=dict)
    path: Optional[str] = None
    enabled: bool = False
    
    @classmethod
    def from_config(cls, config: Dict[str, Any], path: str) -> "ConnectorMetadata":
        """从connector.toml配置创建元数据"""
        # 从 TOML 结构中提取元数据（metadata 部分）
        metadata = config.get("metadata", config)  # 兼容扁平结构
        
        return cls(
            id=metadata.get("id", ""),
            name=metadata.get("name", ""),
            description=metadata.get("description", ""),
            version=metadata.get("version", "1.0.0"),
            author=metadata.get("author", "Unknown"),
            category=metadata.get("category", "other"),
            icon=metadata.get("icon", "extension"),
            capabilities=config.get("capabilities", {}),
            permissions=config.get("permissions", []),
            platforms=config.get("platforms", {}),
            config_schema=config.get("config_schema"),
            config_ui_schema=config.get("config_ui_schema"),
            config_default_values=config.get("config_default_values", {}),
            path=path,
            enabled=False  # 默认禁用，由配置管理器决定启用状态
        )


class ConnectorDiscoveryService:
    """
    连接器发现服务
    
    职责：
    1. 扫描连接器目录，发现可用连接器
    2. 加载connector.toml配置文件
    3. 维护连接器元数据缓存
    4. 提供连接器查询和过滤能力
    """

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.config_manager = config_manager or get_service(ConfigManager)
        self._metadata_cache: Dict[str, ConnectorMetadata] = {}
        self._cache_lock = RLock()
        self._last_scan_time = 0
        self._cache_ttl = 300  # 5分钟缓存过期时间

    @handle_errors(
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.CONNECTOR_DISCOVERY,
        user_message="连接器查询失败",
        recovery_suggestions="检查数据库连接是否正常"
    )
    def discover_connectors(self, force_refresh: bool = False) -> Dict[str, ConnectorMetadata]:
        """
        从数据库获取所有已注册的连接器
        
        注：已移除自动扫描功能，只查询数据库中已注册的连接器
        
        Args:
            force_refresh: 强制刷新缓存
            
        Returns:
            连接器ID到元数据的映射
        """
        current_time = time.time()
        
        # 检查缓存有效性
        if not force_refresh and self._metadata_cache and (current_time - self._last_scan_time) < self._cache_ttl:
            return self._metadata_cache.copy()
        
        with self._cache_lock:
            logger.info("从数据库查询已注册连接器...")
            discovered_connectors = {}
            
            # 从数据库获取已注册的连接器
            from services.storage.core.database import UnifiedDatabaseService
            from models.database_models import Connector
            
            try:
                db_service = get_service(UnifiedDatabaseService)
                with db_service.get_session() as session:
                    connectors = session.query(Connector).all()
                    
                    for connector in connectors:
                        metadata = ConnectorMetadata(
                            id=connector.connector_id,
                            name=connector.name or connector.connector_id,
                            description=connector.description or "",
                            version=connector.version or "0.0.0",
                            author="",  # 数据库中没有author字段
                            category="general",  # 默认分类
                            path=connector.path,
                            enabled=connector.enabled
                        )
                        discovered_connectors[connector.connector_id] = metadata
                        
            except Exception as e:
                logger.error(f"查询数据库连接器失败: {e}")
            
            self._metadata_cache = discovered_connectors
            self._last_scan_time = current_time
            
            logger.info(f"数据库查询完成，共有 {len(discovered_connectors)} 个已注册连接器")
            return discovered_connectors.copy()


    def get_connector_metadata(self, connector_id: str) -> Optional[ConnectorMetadata]:
        """获取指定连接器的元数据"""
        connectors = self.discover_connectors()
        return connectors.get(connector_id)

    def get_enabled_connectors(self) -> Dict[str, ConnectorMetadata]:
        """获取所有启用的连接器"""
        all_connectors = self.discover_connectors()
        return {
            connector_id: metadata 
            for connector_id, metadata in all_connectors.items() 
            if metadata.enabled
        }

    def get_connectors_by_category(self, category: str) -> Dict[str, ConnectorMetadata]:
        """按类别获取连接器"""
        all_connectors = self.discover_connectors()
        return {
            connector_id: metadata 
            for connector_id, metadata in all_connectors.items() 
            if metadata.category == category
        }

    def search_connectors(self, query: str) -> Dict[str, ConnectorMetadata]:
        """搜索连接器（按名称、描述或ID）"""
        all_connectors = self.discover_connectors()
        query_lower = query.lower()
        
        return {
            connector_id: metadata 
            for connector_id, metadata in all_connectors.items() 
            if (query_lower in metadata.name.lower() or 
                query_lower in metadata.description.lower() or 
                query_lower in metadata.id.lower())
        }

    def get_connector_display_names(self) -> Dict[str, str]:
        """获取所有连接器的显示名称映射"""
        all_connectors = self.discover_connectors()
        return {
            connector_id: metadata.name 
            for connector_id, metadata in all_connectors.items()
        }

    def get_available_connector_ids(self) -> Set[str]:
        """获取所有可用连接器的ID集合"""
        return set(self.discover_connectors().keys())

    def invalidate_cache(self) -> None:
        """使缓存失效，强制下次重新扫描"""
        with self._cache_lock:
            self._metadata_cache.clear()
            self._last_scan_time = 0
            
    def refresh_cache(self) -> None:
        """主动刷新缓存"""
        self.discover_connectors(force_refresh=True)