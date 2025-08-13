#!/usr/bin/env python3
"""
连接器注册表发现服务 - 最佳实践版本
实现多源发现、智能缓存、容错降级
"""

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiofiles

logger = logging.getLogger(__name__)


class RegistrySourceType(Enum):
    """注册表源类型"""

    USER_CONFIGURED = "user_configured"
    GITHUB_LATEST = "github_latest"
    GITHUB_SPECIFIC = "github_specific"
    LOCAL_CACHE = "local_cache"
    BUILTIN_FALLBACK = "builtin_fallback"


@dataclass
class RegistrySource:
    """注册表源定义"""

    type: RegistrySourceType
    url: str
    priority: int
    timeout: int
    description: str
    enabled: bool = True


class RegistryDiscoveryService:
    """注册表发现服务 - 最佳实践实现"""

    def __init__(self):
        self.cache_dir = Path.home() / ".linch-mind" / "cache" / "registry"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 缓存配置
        self.cache_duration = timedelta(hours=6)  # 6小时缓存
        self.cache_file = self.cache_dir / "registry.json"
        self.cache_meta_file = self.cache_dir / "registry.meta.json"

        # 发现源配置
        self.sources = self._initialize_sources()

        # 运行时状态
        self._last_successful_source = None
        self._failure_count = {}

    def _initialize_sources(self) -> List[RegistrySource]:
        """初始化发现源列表"""
        sources = []

        # 1. 用户配置的URL (最高优先级)
        user_url = self._get_user_configured_url()
        if user_url:
            sources.append(
                RegistrySource(
                    type=RegistrySourceType.USER_CONFIGURED,
                    url=user_url,
                    priority=1,
                    timeout=30,
                    description="用户自定义注册表URL",
                )
            )

        # 2. GitHub Release Latest (推荐)
        sources.append(
            RegistrySource(
                type=RegistrySourceType.GITHUB_LATEST,
                url="https://github.com/laofahai/linch-mind/releases/latest/download/registry.json",
                priority=2,
                timeout=20,
                description="GitHub Release Latest",
            )
        )

        # 3. GitHub Release 特定版本 (备用)
        specific_tag = self._get_specific_tag()
        if specific_tag:
            sources.append(
                RegistrySource(
                    type=RegistrySourceType.GITHUB_SPECIFIC,
                    url=f"https://github.com/laofahai/linch-mind/releases/download/{specific_tag}/registry.json",
                    priority=3,
                    timeout=20,
                    description=f"GitHub Release {specific_tag}",
                )
            )

        # 4. 本地缓存 (离线支持)
        if self.cache_file.exists():
            sources.append(
                RegistrySource(
                    type=RegistrySourceType.LOCAL_CACHE,
                    url=f"file://{self.cache_file}",
                    priority=8,
                    timeout=5,
                    description="本地缓存",
                )
            )

        # 移除内置默认 - daemon应该保持架构纯净，不硬编码连接器信息

        # 按优先级排序
        sources.sort(key=lambda x: x.priority)
        return sources

    def _get_user_configured_url(self) -> Optional[str]:
        """获取用户配置的注册表URL"""
        # 1. 环境变量
        env_url = os.getenv("LINCH_REGISTRY_URL") or os.getenv("REGISTRY_URL")
        if env_url:
            logger.info(f"使用环境变量配置的注册表URL: {env_url}")
            return env_url

        # 2. 配置文件
        try:
            from config.core_config import get_core_config

            config = get_core_config()
            config_data = config.get_raw_config()

            if "connector_registry" in config_data:
                registry_config = config_data["connector_registry"]
                if "url" in registry_config:
                    url = registry_config["url"]
                    logger.info(f"使用配置文件中的注册表URL: {url}")
                    return url
        except Exception as e:
            logger.debug(f"读取配置文件失败: {e}")

        return None

    def _get_specific_tag(self) -> Optional[str]:
        """获取特定的发布标签"""
        # 可以从配置或环境变量获取
        return os.getenv("LINCH_REGISTRY_TAG")

    async def discover_registry(
        self, force_refresh: bool = False
    ) -> Tuple[Optional[Dict[str, Any]], Optional[RegistrySource]]:
        """
        发现并获取注册表
        返回: (注册表数据, 成功的源)
        """

        # 检查缓存
        if not force_refresh:
            cached_data = await self._load_from_cache()
            if cached_data:
                logger.info("使用有效缓存的注册表数据")
                return cached_data, None

        # 尝试各个源
        for source in self.sources:
            if not source.enabled:
                continue

            logger.info(f"尝试从 {source.description} 获取注册表...")

            try:
                registry_data = await self._fetch_from_source(source)
                if registry_data:
                    # 验证数据完整性
                    if self._validate_registry_data(registry_data):
                        # 保存到缓存
                        await self._save_to_cache(registry_data, source)

                        # 更新成功记录
                        self._last_successful_source = source
                        self._failure_count[source.type] = 0

                        logger.info(f"成功从 {source.description} 获取注册表")
                        return registry_data, source
                    else:
                        logger.warning(f"从 {source.description} 获取的数据验证失败")

            except Exception as e:
                # 记录失败次数
                self._failure_count[source.type] = (
                    self._failure_count.get(source.type, 0) + 1
                )
                logger.warning(f"从 {source.description} 获取注册表失败: {e}")

                # 如果某个源连续失败多次，临时禁用
                if self._failure_count[source.type] >= 3:
                    logger.warning(
                        f"源 {source.description} 连续失败 {self._failure_count[source.type]} 次，临时禁用"
                    )
                    source.enabled = False

        logger.error("所有注册表源都失败，无法获取注册表数据")
        return None, None

    async def refresh_cache(self, force: bool = False) -> bool:
        """刷新注册表缓存

        Args:
            force: 是否强制刷新，忽略缓存时间

        Returns:
            bool: 刷新是否成功
        """
        try:
            if force:
                # 强制刷新：删除现有缓存
                if self.cache_file.exists():
                    self.cache_file.unlink()
                    logger.debug("已删除现有缓存文件")
                if self.cache_meta_file.exists():
                    self.cache_meta_file.unlink()
                    logger.debug("已删除现有缓存元数据")

            # 重新获取注册表数据
            registry_data, source = await self.discover_registry(force_refresh=True)

            if registry_data and source:
                await self._save_to_cache(registry_data, source)
                logger.info(f"缓存刷新成功，来源：{source.description}")
                return True
            else:
                logger.warning("缓存刷新失败：无法获取注册表数据")
                return False

        except Exception as e:
            logger.error(f"缓存刷新失败: {e}")
            return False

    async def _fetch_from_source(
        self, source: RegistrySource
    ) -> Optional[Dict[str, Any]]:
        """从指定源获取注册表数据"""

        if source.type == RegistrySourceType.LOCAL_CACHE:
            return await self._load_from_cache()

        elif source.type == RegistrySourceType.BUILTIN_FALLBACK:
            # 架构纯净原则：daemon不应包含硬编码连接器信息
            raise Exception("Builtin fallback已移除，保持daemon架构纯净")

        else:
            # IPC架构模式：直接返回本地连接器发现结果
            logger.info(f"IPC架构模式：使用本地连接器发现，跳过HTTP源 {source.url}")
            return self._get_local_connectors_registry()

    def _get_local_connectors_registry(self) -> Optional[Dict[str, Any]]:
        """获取本地连接器注册表 (IPC架构模式的备用方案)

        扫描本地连接器目录，构建临时注册表
        遵循架构铁律：保持daemon架构纯净，动态发现而非硬编码
        """
        try:
            # 查找连接器目录 - 可能在当前目录或上级目录
            possible_connector_dirs = [
                Path("connectors"),
                Path("../connectors"),
                Path(__file__).parent.parent.parent
                / "connectors",  # 从daemon目录向上找
            ]

            connectors_base_dir = None
            for dir_path in possible_connector_dirs:
                if dir_path.exists():
                    connectors_base_dir = dir_path
                    logger.debug(f"找到连接器目录: {connectors_base_dir.resolve()}")
                    break

            if not connectors_base_dir:
                logger.warning("连接器目录不存在，返回空注册表")
                logger.debug(
                    f"搜索路径: {[str(p.resolve()) for p in possible_connector_dirs]}"
                )
                return {
                    "schema_version": "1.0.0",
                    "connectors": {},
                    "source": "local_discovery",
                }

            discovered_connectors = {}

            # 搜索official目录和根目录下的连接器
            search_paths = [connectors_base_dir / "official", connectors_base_dir]

            for search_path in search_paths:
                if not search_path.exists():
                    continue

                for item in search_path.iterdir():
                    if not item.is_dir():
                        continue

                    connector_json = item / "connector.json"
                    if connector_json.exists():
                        try:
                            with open(connector_json, "r", encoding="utf-8") as f:
                                connector_config = json.load(f)

                            connector_id = connector_config.get("id", item.name)

                            # 构建注册表格式的连接器信息
                            discovered_connectors[connector_id] = {
                                "id": connector_id,
                                "name": connector_config.get("name", connector_id),
                                "version": connector_config.get("version", "unknown"),
                                "description": connector_config.get("description", ""),
                                "category": connector_config.get("category", "system"),
                                "author": connector_config.get("author", ""),
                                "platforms": connector_config.get("platforms", {}),
                                "local_path": str(item),
                                "config_path": str(connector_json),
                            }

                            logger.debug(f"发现本地连接器: {connector_id} at {item}")

                        except Exception as e:
                            logger.warning(f"解析连接器配置失败 {connector_json}: {e}")

            registry_data = {
                "schema_version": "1.0.0",
                "connectors": discovered_connectors,
                "source": "local_discovery",
                "last_updated": datetime.now().isoformat(),
                "total": len(discovered_connectors),
            }

            logger.info(
                f"本地连接器发现完成，找到 {len(discovered_connectors)} 个连接器"
            )
            return registry_data

        except Exception as e:
            logger.error(f"本地连接器发现失败: {e}")
            # 返回空但有效的注册表结构，避免None值
            return {
                "schema_version": "1.0.0",
                "connectors": {},
                "source": "local_discovery_error",
                "error": str(e),
            }

    async def _load_from_cache(self) -> Optional[Dict[str, Any]]:
        """从本地缓存加载"""
        try:
            if not self.cache_file.exists() or not self.cache_meta_file.exists():
                return None

            # 检查缓存是否过期
            async with aiofiles.open(self.cache_meta_file, "r") as f:
                meta_content = await f.read()
                meta = json.loads(meta_content)

            cache_time = datetime.fromisoformat(meta["cached_at"])
            if datetime.now() - cache_time > self.cache_duration:
                logger.debug("本地缓存已过期")
                return None

            # 加载缓存数据
            async with aiofiles.open(self.cache_file, "r") as f:
                content = await f.read()
                return json.loads(content)

        except Exception as e:
            logger.debug(f"加载本地缓存失败: {e}")
            return None

    async def _save_to_cache(
        self, registry_data: Dict[str, Any], source: RegistrySource
    ):
        """保存到本地缓存"""
        try:
            # 保存注册表数据
            async with aiofiles.open(self.cache_file, "w") as f:
                await f.write(json.dumps(registry_data, indent=2, ensure_ascii=False))

            # 保存元数据
            meta = {
                "cached_at": datetime.now().isoformat(),
                "source_type": source.type.value,
                "source_url": source.url,
                "source_description": source.description,
                "data_hash": hashlib.md5(
                    json.dumps(registry_data, sort_keys=True).encode()
                ).hexdigest(),
                "total_connectors": len(registry_data.get("connectors", {})),
            }

            async with aiofiles.open(self.cache_meta_file, "w") as f:
                await f.write(json.dumps(meta, indent=2, ensure_ascii=False))

            logger.debug(f"注册表数据已缓存 ({meta['total_connectors']} 个连接器)")

        except Exception as e:
            logger.warning(f"保存缓存失败: {e}")

    def _validate_registry_data(self, data: Dict[str, Any]) -> bool:
        """验证注册表数据完整性"""
        try:
            # 基本结构检查
            if not isinstance(data, dict):
                return False

            required_fields = ["schema_version", "connectors"]
            for field in required_fields:
                if field not in data:
                    logger.warning(f"注册表缺少必需字段: {field}")
                    return False

            # 连接器数据检查
            connectors = data["connectors"]
            if not isinstance(connectors, dict) or len(connectors) == 0:
                logger.warning("注册表中没有有效的连接器数据")
                return False

            # 检查连接器基本字段
            for connector_id, connector_info in connectors.items():
                required_connector_fields = ["id", "name", "version"]
                for field in required_connector_fields:
                    if field not in connector_info:
                        logger.warning(f"连接器 {connector_id} 缺少字段: {field}")
                        return False

            logger.debug(f"注册表数据验证通过 ({len(connectors)} 个连接器)")
            return True

        except Exception as e:
            logger.warning(f"注册表数据验证异常: {e}")
            return False

    def get_discovery_status(self) -> Dict[str, Any]:
        """获取发现服务状态"""
        return {
            "sources": [
                {
                    "type": source.type.value,
                    "url": source.url,
                    "description": source.description,
                    "priority": source.priority,
                    "enabled": source.enabled,
                    "failure_count": self._failure_count.get(source.type, 0),
                }
                for source in self.sources
            ],
            "last_successful_source": (
                {
                    "type": self._last_successful_source.type.value,
                    "description": self._last_successful_source.description,
                }
                if self._last_successful_source
                else None
            ),
            "cache_info": {
                "cache_file": str(self.cache_file),
                "cache_exists": self.cache_file.exists(),
                "cache_size": (
                    self.cache_file.stat().st_size if self.cache_file.exists() else 0
                ),
            },
        }


# ServiceFacade现在负责管理服务单例，不再需要本地单例模式
