#!/usr/bin/env python3
"""
重构后的连接器配置服务 - 简化版本
将原964行的巨型文件拆分为多个专门的管理器
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.config_loader import ConfigLoader, ConfigLoadError

from .config_schema_manager import ConfigSchemaManager
from .config_validator import ConfigValidator
from .config_crud_manager import ConfigCrudManager
from .config_environment_manager import ConfigEnvironmentManager

logger = logging.getLogger(__name__)


class ConnectorConfigService:
    """重构后的连接器配置服务
    
    职责分离：
    - ConfigSchemaManager: 处理配置schema
    - ConfigValidator: 处理配置验证
    - ConfigCrudManager: 处理配置CRUD操作
    - ConfigEnvironmentManager: 处理环境特定配置
    """

    def __init__(self, connectors_dir: Optional[Path] = None):
        # 智能查找connectors目录
        self.connectors_dir = self._find_connectors_directory(connectors_dir)
        
        # 环境管理器
        from core.environment_manager import get_environment_manager
        self.env_manager = get_environment_manager()

        # 初始化各个专门的管理器
        self.schema_manager = ConfigSchemaManager(self.connectors_dir)
        self.validator = ConfigValidator(self.schema_manager)
        self.crud_manager = ConfigCrudManager(self.schema_manager, self.validator)
        self.env_manager_config = ConfigEnvironmentManager(self.env_manager)

    def _find_connectors_directory(self, connectors_dir: Optional[Path]) -> Path:
        """智能查找connectors目录"""
        if connectors_dir:
            return connectors_dir

        # 环境感知的连接器配置
        from core.environment_manager import get_environment_manager
        env_manager = get_environment_manager()

        possible_dirs = [
            Path("connectors"),
            Path("../connectors"),
            Path(__file__).parent.parent.parent.parent / "connectors",
            env_manager.current_config.base_path / "connectors",
        ]

        for dir_path in possible_dirs:
            if dir_path.exists():
                return dir_path

        # 如果都找不到，使用默认值
        return Path("connectors")

    def get_connector_config(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取连接器配置文件内容"""
        try:
            search_dirs = [
                self.connectors_dir / "official" / connector_id,
                self.connectors_dir / connector_id,
                Path("connectors") / "official" / connector_id,
                Path("connectors") / connector_id,
            ]

            config_data = ConfigLoader.load_with_fallback("connector", search_dirs)
            logger.debug(f"成功加载连接器配置: {connector_id}")
            return config_data

        except ConfigLoadError:
            logger.warning(f"未找到连接器配置文件: {connector_id}")
            return None
        except Exception as e:
            logger.error(f"读取连接器配置失败 {connector_id}: {e}")
            return None

    # Schema相关方法委托给ConfigSchemaManager
    async def get_config_schema(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取连接器的配置schema"""
        return await self.schema_manager.get_config_schema(connector_id)

    async def get_all_schemas(self) -> Dict[str, Any]:
        """获取所有连接器的配置Schema概览"""
        return await self.schema_manager.get_all_schemas()

    # CRUD相关方法委托给ConfigCrudManager
    async def get_current_config(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """获取连接器当前配置"""
        return await self.crud_manager.get_current_config(connector_id)

    async def update_config(
        self,
        connector_id: str,
        config: Dict[str, Any],
        config_version: str = "1.0.0",
        change_reason: str = "用户更新",
    ) -> Dict[str, Any]:
        """更新连接器配置"""
        return await self.crud_manager.update_config(
            connector_id, config, config_version, change_reason
        )

    async def reset_config(
        self, connector_id: str, to_defaults: bool = True
    ) -> Dict[str, Any]:
        """重置连接器配置"""
        return await self.crud_manager.reset_config(connector_id, to_defaults)

    async def get_default_config(self, connector_id: str) -> Dict[str, Any]:
        """获取连接器的默认配置"""
        return await self.crud_manager.get_default_config(connector_id)

    async def get_config_history(
        self, connector_id: str, limit: int = 10, offset: int = 0
    ) -> Dict[str, Any]:
        """获取配置变更历史"""
        return await self.crud_manager.get_config_history(connector_id, limit, offset)

    # 验证相关方法委托给ConfigValidator
    async def validate_config(
        self, connector_id: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """验证配置数据"""
        return await self.validator.validate_config(connector_id, config)

    # 环境相关方法委托给ConfigEnvironmentManager
    def get_environment_connector_config(self, connector_id: str) -> Dict[str, Any]:
        """获取连接器的环境特定配置"""
        return self.env_manager_config.get_environment_connector_config(connector_id)

    def save_environment_connector_config(
        self, connector_id: str, config: Dict[str, Any]
    ) -> bool:
        """保存连接器的环境特定配置"""
        return self.env_manager_config.save_environment_connector_config(
            connector_id, config
        )

    async def get_merged_environment_config(
        self, connector_id: str
    ) -> Optional[Dict[str, Any]]:
        """获取合并的环境配置"""
        return await self.env_manager_config.get_merged_environment_config(
            connector_id, self.crud_manager, self.schema_manager
        )

    def list_environment_connectors(self) -> List[Dict[str, Any]]:
        """列出当前环境的所有连接器配置"""
        return self.env_manager_config.list_environment_connectors()

    def cleanup_environment_configs(self, confirm: bool = False) -> bool:
        """清理当前环境的连接器配置"""
        return self.env_manager_config.cleanup_environment_configs(confirm)

    # 实用方法
    async def apply_defaults_to_config(
        self, connector_id: str, current_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """将默认值应用到现有配置中"""
        try:
            if current_config is None:
                current_config = await self.get_current_config(connector_id) or {}

            default_result = await self.get_default_config(connector_id)
            default_config = default_result.get("default_config", {})

            # 合并配置：保留现有值，填充默认值
            merged_config = self._merge_configs(default_config, current_config)

            logger.debug(f"应用默认值到配置成功: {connector_id}")
            return {
                "success": True,
                "merged_config": merged_config,
                "applied_defaults": True,
            }

        except Exception as e:
            logger.error(f"应用默认值失败 {connector_id}: {e}")
            return {
                "success": False,
                "error": f"应用默认值时出错: {str(e)}",
                "merged_config": current_config or {},
                "applied_defaults": False,
            }

    def _merge_configs(
        self, default_config: Dict[str, Any], current_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """递归合并配置，保留现有值，填充默认值"""
        import copy

        merged = copy.deepcopy(default_config)

        def merge_recursive(target: Dict[str, Any], source: Dict[str, Any]):
            for key, value in source.items():
                if key in target:
                    if isinstance(target[key], dict) and isinstance(value, dict):
                        merge_recursive(target[key], value)
                    else:
                        target[key] = value
                else:
                    target[key] = value

        merge_recursive(merged, current_config)
        return merged


# 兼容性函数
def get_connector_config_service(
    connectors_dir: Optional[Path] = None,
) -> ConnectorConfigService:
    """获取连接器配置服务实例"""
    return ConnectorConfigService(connectors_dir)