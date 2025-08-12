#!/usr/bin/env python3
"""
连接器配置环境管理器
专门负责环境特定的配置管理
从connector_config_service.py中拆分出来
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ConfigEnvironmentManager:
    """配置环境管理器"""

    def __init__(self, env_manager):
        self.env_manager = env_manager

    def get_environment_connector_config(self, connector_id: str) -> Dict[str, Any]:
        """获取连接器的环境特定配置"""
        try:
            current_env = self.env_manager.current_environment.value
            env_config_path = (
                self.env_manager.current_config.config_dir
                / "connectors"
                / f"{connector_id}.json"
            )

            if env_config_path.exists():
                with open(env_config_path, "r", encoding="utf-8") as f:
                    env_config = json.load(f)
                    logger.info(f"加载环境特定配置: {connector_id} ({current_env})")
                    return env_config
            else:
                logger.debug(f"环境特定配置不存在: {env_config_path}")
                return {}

        except Exception as e:
            logger.warning(f"加载环境特定配置失败 {connector_id}: {e}")
            return {}

    def save_environment_connector_config(
        self, connector_id: str, config: Dict[str, Any]
    ) -> bool:
        """保存连接器的环境特定配置"""
        try:
            current_env = self.env_manager.current_environment.value
            env_config_dir = self.env_manager.current_config.config_dir / "connectors"
            env_config_dir.mkdir(parents=True, exist_ok=True)

            env_config_path = env_config_dir / f"{connector_id}.json"

            config_with_meta = {
                **config,
                "_environment": current_env,
                "_updated_at": datetime.now(timezone.utc).isoformat(),
                "_created_by": "connector_config_service",
            }

            with open(env_config_path, "w", encoding="utf-8") as f:
                json.dump(config_with_meta, f, indent=2, ensure_ascii=False)

            logger.info(
                f"保存环境特定配置: {connector_id} ({current_env}) -> {env_config_path}"
            )
            return True

        except Exception as e:
            logger.error(f"保存环境特定配置失败 {connector_id}: {e}")
            return False

    async def get_merged_environment_config(
        self, connector_id: str, crud_manager, schema_manager
    ) -> Optional[Dict[str, Any]]:
        """获取合并的环境配置"""
        try:
            # 1. 获取默认配置
            default_result = await crud_manager.get_default_config(connector_id)
            default_config = default_result.get("default_config", {})

            # 2. 获取环境特定配置
            env_config = self.get_environment_connector_config(connector_id)

            # 3. 获取数据库中的当前配置
            current_config = await crud_manager.get_current_config(connector_id) or {}

            # 4. 合并配置
            merged_config = {}
            self._deep_merge(merged_config, default_config)
            self._deep_merge(merged_config, env_config)
            self._deep_merge(merged_config, current_config)

            # 添加环境元信息
            merged_config["_environment_info"] = {
                "current_environment": self.env_manager.current_environment.value,
                "has_env_config": bool(env_config),
                "has_db_config": bool(current_config),
                "config_source": "merged",
            }

            logger.debug(f"合并环境配置完成: {connector_id}")
            return merged_config

        except Exception as e:
            logger.error(f"合并环境配置失败 {connector_id}: {e}")
            return None

    def list_environment_connectors(self) -> List[Dict[str, Any]]:
        """列出当前环境的所有连接器配置"""
        try:
            connectors = []
            current_env = self.env_manager.current_environment.value
            env_config_dir = self.env_manager.current_config.config_dir / "connectors"

            if env_config_dir.exists():
                for config_file in env_config_dir.glob("*.json"):
                    connector_id = config_file.stem
                    try:
                        with open(config_file, "r", encoding="utf-8") as f:
                            config = json.load(f)

                        connectors.append(
                            {
                                "connector_id": connector_id,
                                "environment": config.get("_environment", current_env),
                                "updated_at": config.get("_updated_at"),
                                "config_file": str(config_file),
                                "has_config": True,
                            }
                        )

                    except Exception as e:
                        logger.warning(f"读取连接器配置失败 {config_file}: {e}")

            return connectors

        except Exception as e:
            logger.error(f"列出环境连接器配置失败: {e}")
            return []

    def cleanup_environment_configs(self, confirm: bool = False) -> bool:
        """清理当前环境的连接器配置"""
        if not confirm:
            logger.warning("清理环境配置需要确认 (confirm=True)")
            return False

        try:
            current_env = self.env_manager.current_environment.value
            env_config_dir = self.env_manager.current_config.config_dir / "connectors"

            if env_config_dir.exists():
                import shutil
                shutil.rmtree(env_config_dir)
                logger.info(f"清理环境配置完成: {current_env}")
                return True
            else:
                logger.info(f"环境配置目录不存在: {env_config_dir}")
                return True

        except Exception as e:
            logger.error(f"清理环境配置失败: {e}")
            return False

    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]):
        """深度合并字典"""
        for key, value in source.items():
            if key in target:
                if isinstance(target[key], dict) and isinstance(value, dict):
                    self._deep_merge(target[key], value)
                else:
                    target[key] = value
            else:
                target[key] = value