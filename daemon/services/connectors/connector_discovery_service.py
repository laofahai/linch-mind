"""
连接器发现服务 - 动态发现和加载连接器配置

实现完全配置驱动的连接器系统，消除硬编码依赖
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
from config.core_config import CoreConfigManager
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
        """从connector.json配置创建元数据"""
        return cls(
            id=config.get("id", ""),
            name=config.get("name", ""),
            description=config.get("description", ""),
            version=config.get("version", "1.0.0"),
            author=config.get("author", "Unknown"),
            category=config.get("category", "other"),
            icon=config.get("icon", "extension"),
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
    2. 加载connector.json配置文件
    3. 维护连接器元数据缓存
    4. 提供连接器查询和过滤能力
    """

    def __init__(self, config_manager: Optional[CoreConfigManager] = None):
        self.config_manager = config_manager or get_service(CoreConfigManager)
        self._metadata_cache: Dict[str, ConnectorMetadata] = {}
        self._cache_lock = RLock()
        self._last_scan_time = 0
        self._cache_ttl = 300  # 5分钟缓存过期时间
        
        # 连接器目录路径
        self._connector_base_paths = [
            "connectors/official",
            "connectors/third-party",
            # 支持绝对路径配置
        ]

    @handle_errors(
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.CONNECTOR_DISCOVERY,
        user_message="连接器发现失败",
        recovery_suggestions="检查连接器目录是否存在且可读"
    )
    def discover_connectors(self, force_refresh: bool = False) -> Dict[str, ConnectorMetadata]:
        """
        发现所有可用连接器
        
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
            logger.info("开始发现连接器配置...")
            discovered_connectors = {}
            
            # 获取项目根目录
            project_root = Path(__file__).parent.parent.parent.parent
            
            # 扫描所有连接器目录
            for base_path in self._connector_base_paths:
                connector_dir = project_root / base_path
                if not connector_dir.exists():
                    logger.debug(f"连接器目录不存在: {connector_dir}")
                    continue
                
                # 扫描连接器
                for connector_path in connector_dir.iterdir():
                    if not connector_path.is_dir():
                        continue
                    
                    config_file = connector_path / "connector.json"
                    if not config_file.exists():
                        logger.debug(f"连接器配置文件不存在: {config_file}")
                        continue
                    
                    try:
                        # 加载连接器配置
                        metadata = self._load_connector_metadata(config_file, str(connector_path))
                        if metadata and metadata.id:
                            # 应用启用状态配置
                            metadata.enabled = self._is_connector_enabled(metadata.id)
                            discovered_connectors[metadata.id] = metadata
                            logger.debug(f"发现连接器: {metadata.id} ({metadata.name})")
                        
                    except Exception as e:
                        logger.warning(f"加载连接器配置失败 {config_file}: {e}")
                        continue
            
            self._metadata_cache = discovered_connectors
            self._last_scan_time = current_time
            
            logger.info(f"连接器发现完成，共发现 {len(discovered_connectors)} 个连接器")
            return discovered_connectors.copy()

    def _load_connector_metadata(self, config_file: Path, connector_path: str) -> Optional[ConnectorMetadata]:
        """加载单个连接器的元数据"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 验证必要字段
            required_fields = ['id', 'name', 'version']
            for field in required_fields:
                if not config.get(field):
                    logger.warning(f"连接器配置缺少必要字段 {field}: {config_file}")
                    return None
            
            return ConnectorMetadata.from_config(config, connector_path)
            
        except json.JSONDecodeError as e:
            logger.error(f"连接器配置JSON解析失败 {config_file}: {e}")
            return None
        except Exception as e:
            logger.error(f"加载连接器元数据失败 {config_file}: {e}")
            return None

    def _is_connector_enabled(self, connector_id: str) -> bool:
        """检查连接器是否在配置中启用"""
        try:
            # 从配置管理器获取连接器启用状态
            connector_config = self.config_manager.config.connectors
            
            # 使用配置类的新方法来检查启用状态
            return connector_config.is_connector_enabled(connector_id)
            
        except Exception as e:
            logger.warning(f"检查连接器启用状态失败 {connector_id}: {e}")
            return False

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