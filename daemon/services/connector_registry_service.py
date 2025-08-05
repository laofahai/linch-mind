#!/usr/bin/env python3
"""
连接器注册表服务
从GitHub Release获取连接器市场信息
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
from config.core_config import get_core_config

logger = logging.getLogger(__name__)


class ConnectorRegistryService:
    """连接器注册表服务"""

    def __init__(self):
        self.config = get_core_config()
        self._cache = {}
        self._cache_expiry = None
        self._cache_duration = timedelta(hours=1)  # 缓存1小时

        # 从配置获取注册表URL，默认使用GitHub Release
        self.registry_url = self._get_registry_url()

    def _get_registry_url(self) -> str:
        """获取注册表URL配置"""
        # 优先级：环境变量 > 配置文件 > 默认值
        import os

        # 1. 环境变量
        if os.getenv("REGISTRY_URL"):
            return os.getenv("REGISTRY_URL")

        # 2. 配置文件
        try:
            return self.config.config.connector_registry.url
        except Exception as e:
            logger.warning(f"读取注册表配置失败: {e}")

        # 3. 默认GitHub Release
        return "https://github.com/laofahai/linch-mind/releases/latest/download/registry.json"

    async def fetch_registry(
        self, force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """获取连接器注册表"""
        try:
            # 检查缓存
            if not force_refresh and self._is_cache_valid():
                logger.info("使用缓存的注册表数据")
                return self._cache

            logger.info(f"从 {self.registry_url} 获取注册表...")

            async with aiohttp.ClientSession() as session:
                async with session.get(self.registry_url, timeout=30) as response:
                    if response.status == 200:
                        registry_data = await response.json()

                        # 更新缓存
                        self._cache = registry_data
                        self._cache_expiry = datetime.now() + self._cache_duration

                        logger.info(
                            f"成功获取注册表，包含 {len(registry_data.get('connectors', {}))} 个连接器"
                        )
                        return registry_data
                    else:
                        logger.error(f"获取注册表失败，HTTP状态码: {response.status}")
                        return None

        except asyncio.TimeoutError:
            logger.error("获取注册表超时")
            return None
        except Exception as e:
            logger.error(f"获取注册表异常: {e}")
            return None

    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        return (
            self._cache and self._cache_expiry and datetime.now() < self._cache_expiry
        )

    async def get_available_connectors(
        self, force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """获取可用连接器列表"""
        try:
            registry = await self.fetch_registry(force_refresh)
            if not registry:
                return []

            connectors = []
            for connector_id, connector_info in registry.get("connectors", {}).items():
                # 转换为UI需要的格式
                connector_data = {
                    "connector_id": connector_id,
                    "name": connector_info.get("name", connector_id),
                    "display_name": connector_info.get("name", connector_id),
                    "description": connector_info.get("description", ""),
                    "version": connector_info.get("version", "1.0.0"),
                    "author": connector_info.get("author", "Unknown"),
                    "category": connector_info.get("category", "other"),
                    "type": connector_info.get("type", "community"),
                    "platforms": connector_info.get("platforms", {}),
                    "download_url": connector_info.get("download_url"),
                    "capabilities": connector_info.get("capabilities", {}),
                    "permissions": connector_info.get("permissions", []),
                    "last_updated": connector_info.get("last_updated"),
                    "is_registered": True,
                }
                connectors.append(connector_data)

            # 按类型和名称排序
            connectors.sort(
                key=lambda x: (
                    0 if x["type"] == "official" else 1,  # 官方连接器优先
                    x["display_name"],
                )
            )

            return connectors

        except Exception as e:
            logger.error(f"获取可用连接器列表失败: {e}")
            return []

    async def get_connector_download_info(
        self, connector_id: str, platform: str = "linux-x64"
    ) -> Optional[Dict[str, Any]]:
        """获取连接器下载信息"""
        try:
            registry = await self.fetch_registry()
            if not registry:
                return None

            connector_info = registry.get("connectors", {}).get(connector_id)
            if not connector_info:
                logger.warning(f"连接器 {connector_id} 在注册表中不存在")
                return None

            # 检查平台支持
            platforms = connector_info.get("platforms", {})

            if platform in platforms:
                platform_info = platforms[platform]
                return {
                    "connector_id": connector_id,
                    "platform": platform,
                    "download_url": platform_info.get("download_url"),
                    "supported": platform_info.get("supported", True),
                    "last_updated": platform_info.get("last_updated"),
                    "version": connector_info.get("version"),
                    "size_estimate": platform_info.get("size_estimate", "Unknown"),
                }
            else:
                # 回退到默认下载URL
                return {
                    "connector_id": connector_id,
                    "platform": platform,
                    "download_url": connector_info.get("download_url"),
                    "supported": True,
                    "last_updated": connector_info.get("last_updated"),
                    "version": connector_info.get("version"),
                    "size_estimate": "Unknown",
                }

        except Exception as e:
            logger.error(f"获取连接器下载信息失败 {connector_id}: {e}")
            return None

    async def search_connectors(
        self, query: str, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """搜索连接器"""
        try:
            all_connectors = await self.get_available_connectors()

            # 搜索过滤
            filtered_connectors = []
            query_lower = query.lower() if query else ""

            for connector in all_connectors:
                # 类别过滤
                if category and category != "all":
                    if connector["category"] != category:
                        continue

                # 关键词搜索
                if query_lower:
                    searchable_text = " ".join(
                        [
                            connector["display_name"],
                            connector["description"],
                            connector["category"],
                            connector["connector_id"],
                        ]
                    ).lower()

                    if query_lower not in searchable_text:
                        continue

                filtered_connectors.append(connector)

            return filtered_connectors

        except Exception as e:
            logger.error(f"搜索连接器失败: {e}")
            return []

    async def get_registry_metadata(self) -> Optional[Dict[str, Any]]:
        """获取注册表元数据"""
        try:
            registry = await self.fetch_registry()
            if not registry:
                return None

            metadata = registry.get("metadata", {})
            return {
                "registry_url": self.registry_url,
                "schema_version": registry.get("schema_version", "1.0"),
                "last_updated": registry.get("last_updated"),
                "total_connectors": metadata.get("total_count", 0),
                "repository": metadata.get("repository", "laofahai/linch-mind"),
                "commit": metadata.get("commit", "unknown"),
                "release_tag": metadata.get("release_tag"),
                "cache_expires": (
                    self._cache_expiry.isoformat() if self._cache_expiry else None
                ),
            }

        except Exception as e:
            logger.error(f"获取注册表元数据失败: {e}")
            return None


# 全局单例
_registry_service = None


def get_connector_registry_service() -> ConnectorRegistryService:
    """获取连接器注册表服务单例"""
    global _registry_service
    if _registry_service is None:
        _registry_service = ConnectorRegistryService()
    return _registry_service
