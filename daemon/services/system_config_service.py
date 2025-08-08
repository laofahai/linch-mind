#!/usr/bin/env python3
"""
系统配置服务
统一处理系统级配置管理，包括连接器注册表等
替换原来的API路由实现，直接在服务层提供功能
"""

import logging
from typing import Any, Dict

from config.core_config import get_connector_config
from models.database_models import Connector
from services.database_service import get_database_service
from services.registry_discovery_service import RegistryDiscoveryService

logger = logging.getLogger(__name__)


class SystemConfigService:
    """系统配置服务"""

    def __init__(self):
        self.registry_service = RegistryDiscoveryService()
        self.db_service = get_database_service()
        self.config = get_connector_config()

    async def get_registry_connectors(self) -> Dict[str, Any]:
        """获取注册表中的连接器列表"""
        try:
            # 获取注册表数据
            registry_data = await self.registry_service.get_registry()

            if not registry_data or "connectors" not in registry_data:
                return {
                    "success": False,
                    "error": "Failed to fetch registry data",
                    "data": {"connectors": []},
                }

            connectors = registry_data["connectors"]

            # 增强连接器信息（添加本地安装状态）
            enhanced_connectors = []
            with self.db_service.get_session() as session:
                for connector_data in connectors:
                    connector_id = connector_data.get("id")

                    # 检查是否已安装
                    installed_connector = (
                        session.query(Connector)
                        .filter_by(connector_id=connector_id)
                        .first()
                    )

                    connector_data["is_installed"] = installed_connector is not None
                    if installed_connector:
                        connector_data["local_version"] = installed_connector.version
                        connector_data["status"] = installed_connector.status

                    enhanced_connectors.append(connector_data)

            return {
                "success": True,
                "data": {
                    "connectors": enhanced_connectors,
                    "total": len(enhanced_connectors),
                    "registry_source": registry_data.get("source", "unknown"),
                    "last_updated": registry_data.get("last_updated"),
                },
            }

        except Exception as e:
            logger.error(f"获取注册表连接器失败: {e}")
            return {
                "success": False,
                "error": f"Failed to get registry connectors: {str(e)}",
                "data": {"connectors": []},
            }

    async def get_connector_download_info(self, connector_id: str) -> Dict[str, Any]:
        """获取连接器下载信息"""
        try:
            registry_data = await self.registry_service.get_registry()

            if not registry_data or "connectors" not in registry_data:
                return {"success": False, "error": "Registry data not available"}

            # 查找指定连接器
            connector_info = None
            for connector in registry_data["connectors"]:
                if connector.get("id") == connector_id:
                    connector_info = connector
                    break

            if not connector_info:
                return {
                    "success": False,
                    "error": f"Connector '{connector_id}' not found in registry",
                }

            # 构造下载信息
            download_info = {
                "connector_id": connector_id,
                "name": connector_info.get("name"),
                "version": connector_info.get("version"),
                "description": connector_info.get("description"),
                "download_url": connector_info.get("download_url"),
                "checksum": connector_info.get("checksum"),
                "size": connector_info.get("size"),
                "requirements": connector_info.get("requirements", []),
                "platforms": connector_info.get("platforms", []),
            }

            return {"success": True, "data": download_info}

        except Exception as e:
            logger.error(f"获取连接器下载信息失败: {e}")
            return {"success": False, "error": f"Failed to get download info: {str(e)}"}

    async def refresh_registry(self, force: bool = False) -> Dict[str, Any]:
        """刷新注册表"""
        try:
            # 清除缓存并重新获取
            success = await self.registry_service.refresh_cache(force=force)

            if success:
                registry_data = await self.registry_service.get_registry()
                connector_count = len(registry_data.get("connectors", []))

                return {
                    "success": True,
                    "data": {
                        "message": "Registry refreshed successfully",
                        "connector_count": connector_count,
                        "last_updated": registry_data.get("last_updated"),
                        "source": registry_data.get("source"),
                    },
                }
            else:
                return {"success": False, "error": "Failed to refresh registry cache"}

        except Exception as e:
            logger.error(f"刷新注册表失败: {e}")
            return {"success": False, "error": f"Failed to refresh registry: {str(e)}"}

    async def get_registry_config(self) -> Dict[str, Any]:
        """获取注册表配置"""
        try:
            config_data = {
                "sources": [
                    {
                        "type": source.type.value,
                        "url": source.url,
                        "priority": source.priority,
                        "enabled": source.enabled,
                        "description": source.description,
                    }
                    for source in self.registry_service.sources
                ],
                "cache_duration_hours": self.registry_service.cache_duration.total_seconds()
                / 3600,
                "cache_directory": str(self.registry_service.cache_dir),
                "last_successful_source": self.registry_service._last_successful_source,
            }

            return {"success": True, "data": config_data}

        except Exception as e:
            logger.error(f"获取注册表配置失败: {e}")
            return {
                "success": False,
                "error": f"Failed to get registry config: {str(e)}",
            }


# 全局服务实例
_system_config_service = None


def get_system_config_service() -> SystemConfigService:
    """获取系统配置服务实例"""
    global _system_config_service
    if _system_config_service is None:
        _system_config_service = SystemConfigService()
    return _system_config_service
