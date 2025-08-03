#!/usr/bin/env python3
"""
ConnectorRegistry 微服务设计示例
职责：连接器发现、注册、验证
目标：<150行代码，单一职责
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConnectorManifest:
    """连接器清单数据结构"""
    id: str
    name: str
    version: str
    author: str
    description: str
    category: str
    entry_points: Dict[str, str]
    permissions: List[str]
    config_schema: Dict
    
    @classmethod
    def from_file(cls, manifest_path: Path) -> 'ConnectorManifest':
        """从connector.json文件创建清单"""
        with open(manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls(
            id=data['id'],
            name=data['name'],
            version=data['version'],
            author=data['author'],
            description=data['description'],
            category=data.get('category', 'unknown'),
            entry_points=data['entry'],
            permissions=data['permissions'],
            config_schema=data.get('config_schema', {})
        )


@dataclass
class ConnectorInfo:
    """连接器信息"""
    manifest: ConnectorManifest
    source_path: Path
    discovered_at: datetime
    is_valid: bool
    validation_errors: List[str]


class ConnectorRegistry:
    """连接器注册和发现服务"""
    
    def __init__(self, base_paths: List[Path] = None):
        """
        初始化连接器注册表
        
        Args:
            base_paths: 连接器搜索路径列表，默认为项目内置路径
        """
        self.base_paths = base_paths or [
            Path(__file__).parent.parent.parent / "connectors" / "official",
            Path(__file__).parent.parent.parent / "connectors" / "community"
        ]
        self._connector_cache: Dict[str, ConnectorInfo] = {}
        self._last_scan_time: Optional[datetime] = None
    
    async def discover_connectors(self, force_rescan: bool = False) -> List[ConnectorInfo]:
        """
        发现所有可用连接器
        
        Args:
            force_rescan: 是否强制重新扫描
            
        Returns:
            连接器信息列表
        """
        if not force_rescan and self._connector_cache:
            return list(self._connector_cache.values())
        
        logger.info("开始扫描连接器...")
        discovered = {}
        
        for base_path in self.base_paths:
            if not base_path.exists():
                continue
                
            await self._scan_directory(base_path, discovered)
        
        self._connector_cache = discovered
        self._last_scan_time = datetime.now()
        
        logger.info(f"发现 {len(discovered)} 个连接器")
        return list(discovered.values())
    
    async def _scan_directory(self, directory: Path, discovered: Dict[str, ConnectorInfo]):
        """扫描单个目录"""
        for connector_dir in directory.iterdir():
            if not connector_dir.is_dir():
                continue
            
            manifest_path = connector_dir / "connector.json"
            if not manifest_path.exists():
                continue
            
            try:
                manifest = ConnectorManifest.from_file(manifest_path)
                validation_errors = await self._validate_manifest(manifest, connector_dir)
                
                connector_info = ConnectorInfo(
                    manifest=manifest,
                    source_path=connector_dir,
                    discovered_at=datetime.now(),
                    is_valid=len(validation_errors) == 0,
                    validation_errors=validation_errors
                )
                
                discovered[manifest.id] = connector_info
                
                if connector_info.is_valid:
                    logger.debug(f"✅ 发现有效连接器: {manifest.id} v{manifest.version}")
                else:
                    logger.warning(f"⚠️ 发现无效连接器: {manifest.id} - {validation_errors}")
                    
            except Exception as e:
                logger.error(f"❌ 解析连接器清单失败 {connector_dir.name}: {e}")
    
    async def _validate_manifest(self, manifest: ConnectorManifest, source_path: Path) -> List[str]:
        """验证连接器清单"""
        errors = []
        
        # 验证必需字段
        if not manifest.id or not manifest.id.replace('-', '').replace('_', '').isalnum():
            errors.append("连接器ID必须是有效的标识符")
        
        # 验证入口点存在
        dev_entry = manifest.entry_points.get('development', {})
        if dev_entry and 'args' in dev_entry:
            entry_file = source_path / dev_entry['args'][0]
            if not entry_file.exists():
                errors.append(f"开发模式入口文件不存在: {entry_file}")
        
        # 验证权限格式
        for permission in manifest.permissions:
            if ':' not in permission:
                errors.append(f"权限格式错误: {permission}")
        
        return errors
    
    async def get_connector(self, connector_id: str) -> Optional[ConnectorInfo]:
        """获取指定连接器信息"""
        if not self._connector_cache:
            await self.discover_connectors()
        
        return self._connector_cache.get(connector_id)
    
    async def register_connector(self, manifest_data: dict, source_path: Path) -> bool:
        """
        注册新连接器
        
        Args:
            manifest_data: 连接器清单数据
            source_path: 连接器源代码路径
            
        Returns:
            注册是否成功
        """
        try:
            # 创建清单对象
            manifest = ConnectorManifest(
                id=manifest_data['id'],
                name=manifest_data['name'],
                version=manifest_data['version'],
                author=manifest_data['author'],
                description=manifest_data['description'],
                category=manifest_data.get('category', 'unknown'),
                entry_points=manifest_data['entry'],
                permissions=manifest_data['permissions'],
                config_schema=manifest_data.get('config_schema', {})
            )
            
            # 验证清单
            validation_errors = await self._validate_manifest(manifest, source_path)
            if validation_errors:
                logger.error(f"连接器注册失败: {validation_errors}")
                return False
            
            # 检查ID冲突
            if manifest.id in self._connector_cache:
                logger.warning(f"连接器ID冲突，覆盖现有连接器: {manifest.id}")
            
            # 注册连接器
            connector_info = ConnectorInfo(
                manifest=manifest,
                source_path=source_path,
                discovered_at=datetime.now(),
                is_valid=True,
                validation_errors=[]
            )
            
            self._connector_cache[manifest.id] = connector_info
            logger.info(f"✅ 连接器注册成功: {manifest.id} v{manifest.version}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 连接器注册失败: {e}")
            return False
    
    def list_by_category(self, category: str) -> List[ConnectorInfo]:
        """按分类列出连接器"""
        return [
            info for info in self._connector_cache.values()
            if info.manifest.category == category and info.is_valid
        ]
    
    def get_registry_stats(self) -> Dict:
        """获取注册表统计信息"""
        total = len(self._connector_cache)
        valid = sum(1 for info in self._connector_cache.values() if info.is_valid)
        categories = {}
        
        for info in self._connector_cache.values():
            if info.is_valid:
                category = info.manifest.category
                categories[category] = categories.get(category, 0) + 1
        
        return {
            'total_connectors': total,
            'valid_connectors': valid,
            'invalid_connectors': total - valid,
            'categories': categories,
            'last_scan_time': self._last_scan_time
        }