#!/usr/bin/env python3
"""
用户个性化配置数据库服务
专门管理用户个性化调优参数的数据库CRUD操作

核心功能:
- 用户配置的增删改查
- 配置验证和类型检查
- 配置历史记录
- 默认配置初始化
- 配置迁移支持
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from core.service_facade import get_database_service
from core.error_handling import handle_errors, ErrorSeverity, ErrorCategory
from models.database_models import UserConfigEntry, UserConfigHistory

logger = logging.getLogger(__name__)


class UserConfigDbService:
    """用户配置数据库服务"""

    def __init__(self):
        self._db_service = None

    @property
    def db_service(self):
        """延迟获取数据库服务"""
        if self._db_service is None:
            try:
                self._db_service = get_database_service()
            except Exception as e:
                logger.warning(f"数据库服务暂不可用: {e}")
                return None
        return self._db_service

    @handle_errors(
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.DATABASE_OPERATION,
        user_message="获取用户配置失败"
    )
    async def get_config_value(
        self, 
        section: str, 
        key: str, 
        user_id: str = "default"  # 固定使用default用户，简化当前实现
    ) -> Optional[Any]:
        """获取配置值
        
        Args:
            section: 配置段 (ollama, vector, security等)
            key: 配置键
            user_id: 用户ID
            
        Returns:
            配置值，如果不存在返回None
        """
        if not self.db_service:
            logger.warning("数据库服务不可用，无法获取配置")
            return None

        try:
            with self.db_service.get_session() as session:
                config_entry = (
                    session.query(UserConfigEntry)
                    .filter_by(
                        user_id=user_id,
                        config_section=section,
                        config_key=key
                    )
                    .first()
                )

                if config_entry:
                    # 更新访问统计
                    config_entry.access_count += 1
                    config_entry.last_accessed = datetime.now(timezone.utc)
                    session.commit()
                    
                    logger.debug(f"获取配置成功: {section}.{key} = {config_entry.config_value}")
                    return config_entry.config_value

                logger.debug(f"配置不存在: {section}.{key}")
                return None

        except Exception as e:
            logger.error(f"获取配置失败 {section}.{key}: {e}")
            return None

    @handle_errors(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.DATABASE_OPERATION,
        user_message="设置用户配置失败"
    )
    async def set_config_value(
        self,
        section: str,
        key: str,
        value: Any,
        user_id: str = "default",
        config_type: str = "user_preference",
        description: str = None,
        is_sensitive: bool = False,
        requires_restart: bool = False,
        changed_by: str = "user"
    ) -> bool:
        """设置配置值
        
        Args:
            section: 配置段
            key: 配置键
            value: 配置值
            user_id: 用户ID
            config_type: 配置类型
            description: 配置描述
            is_sensitive: 是否敏感信息
            requires_restart: 是否需要重启生效
            changed_by: 变更者
            
        Returns:
            是否设置成功
        """
        if not self.db_service:
            logger.error("数据库服务不可用，无法设置配置")
            return False

        try:
            # 验证配置值
            validation_result = self._validate_config_value(section, key, value)
            if not validation_result["valid"]:
                logger.warning(f"配置验证失败 {section}.{key}: {validation_result['errors']}")
                return False

            # 推断值类型
            value_type = self._infer_value_type(value)

            with self.db_service.get_session() as session:
                # 查找现有配置
                existing_config = (
                    session.query(UserConfigEntry)
                    .filter_by(
                        user_id=user_id,
                        config_section=section,
                        config_key=key
                    )
                    .first()
                )

                old_value = None
                change_type = "create"

                if existing_config:
                    # 更新现有配置
                    old_value = existing_config.config_value
                    change_type = "update"
                    
                    existing_config.config_value = value
                    existing_config.value_type = value_type
                    existing_config.is_sensitive = is_sensitive
                    existing_config.requires_restart = requires_restart
                    existing_config.last_modified_by = changed_by
                    existing_config.updated_at = datetime.now(timezone.utc)
                    
                    if description:
                        existing_config.description = description

                    config_entry = existing_config
                else:
                    # 创建新配置
                    config_entry = UserConfigEntry(
                        user_id=user_id,
                        config_section=section,
                        config_key=key,
                        config_value=value,
                        config_type=config_type,
                        value_type=value_type,
                        is_sensitive=is_sensitive,
                        description=description,
                        requires_restart=requires_restart,
                        last_modified_by=changed_by
                    )
                    session.add(config_entry)

                # 保存变更历史
                if old_value != value:  # 只有值真正改变时才记录历史
                    history_entry = UserConfigHistory(
                        config_entry_id=config_entry.id,
                        user_id=user_id,
                        config_section=section,
                        config_key=key,
                        old_value=old_value,
                        new_value=value,
                        change_type=change_type,
                        change_reason=f"配置更新: {description or key}",
                        changed_by=changed_by,
                        validation_status="valid"
                    )
                    session.add(history_entry)

                session.commit()
                
                logger.info(f"配置设置成功: {section}.{key} = {value}")
                return True

        except Exception as e:
            logger.error(f"设置配置失败 {section}.{key}: {e}")
            return False

    @handle_errors(
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.DATABASE_OPERATION,
        user_message="获取配置段失败"
    )
    async def get_section_configs(
        self, 
        section: str, 
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """获取整个配置段的所有配置
        
        Args:
            section: 配置段名称
            user_id: 用户ID
            
        Returns:
            配置字典
        """
        if not self.db_service:
            logger.warning("数据库服务不可用，返回空配置")
            return {}

        try:
            with self.db_service.get_session() as session:
                config_entries = (
                    session.query(UserConfigEntry)
                    .filter_by(user_id=user_id, config_section=section)
                    .all()
                )

                configs = {}
                for entry in config_entries:
                    configs[entry.config_key] = entry.config_value
                    
                    # 更新访问统计
                    entry.access_count += 1
                    entry.last_accessed = datetime.now(timezone.utc)

                session.commit()
                
                logger.debug(f"获取配置段成功: {section}, {len(configs)} 个配置项")
                return configs

        except Exception as e:
            logger.error(f"获取配置段失败 {section}: {e}")
            return {}

    @handle_errors(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.DATABASE_OPERATION,
        user_message="批量设置配置失败"
    )
    async def set_section_configs(
        self,
        section: str,
        configs: Dict[str, Any],
        user_id: str = "default",
        config_type: str = "user_preference",
        changed_by: str = "user"
    ) -> bool:
        """批量设置配置段的配置
        
        Args:
            section: 配置段名称
            configs: 配置字典
            user_id: 用户ID
            config_type: 配置类型
            changed_by: 变更者
            
        Returns:
            是否设置成功
        """
        try:
            success_count = 0
            for key, value in configs.items():
                if await self.set_config_value(
                    section=section,
                    key=key,
                    value=value,
                    user_id=user_id,
                    config_type=config_type,
                    changed_by=changed_by
                ):
                    success_count += 1

            logger.info(f"批量配置设置完成: {section}, {success_count}/{len(configs)} 成功")
            return success_count == len(configs)

        except Exception as e:
            logger.error(f"批量配置设置失败 {section}: {e}")
            return False

    @handle_errors(
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.DATABASE_OPERATION,
        user_message="删除配置失败"
    )
    async def delete_config(
        self,
        section: str,
        key: str,
        user_id: str = "default",
        changed_by: str = "user"
    ) -> bool:
        """删除配置
        
        Args:
            section: 配置段
            key: 配置键
            user_id: 用户ID
            changed_by: 变更者
            
        Returns:
            是否删除成功
        """
        if not self.db_service:
            logger.error("数据库服务不可用，无法删除配置")
            return False

        try:
            with self.db_service.get_session() as session:
                config_entry = (
                    session.query(UserConfigEntry)
                    .filter_by(
                        user_id=user_id,
                        config_section=section,
                        config_key=key
                    )
                    .first()
                )

                if not config_entry:
                    logger.warning(f"配置不存在，无法删除: {section}.{key}")
                    return False

                old_value = config_entry.config_value

                # 记录删除历史
                history_entry = UserConfigHistory(
                    config_entry_id=config_entry.id,
                    user_id=user_id,
                    config_section=section,
                    config_key=key,
                    old_value=old_value,
                    new_value=None,
                    change_type="delete",
                    change_reason=f"配置删除: {key}",
                    changed_by=changed_by,
                    validation_status="valid"
                )
                session.add(history_entry)

                # 删除配置
                session.delete(config_entry)
                session.commit()

                logger.info(f"配置删除成功: {section}.{key}")
                return True

        except Exception as e:
            logger.error(f"删除配置失败 {section}.{key}: {e}")
            return False

    @handle_errors(
        severity=ErrorSeverity.LOW,
        category=ErrorCategory.DATABASE_OPERATION,
        user_message="获取配置历史失败"
    )
    async def get_config_history(
        self,
        section: str = None,
        key: str = None,
        user_id: str = "default",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取配置变更历史
        
        Args:
            section: 配置段（可选）
            key: 配置键（可选）
            user_id: 用户ID
            limit: 返回记录数限制
            
        Returns:
            历史记录列表
        """
        if not self.db_service:
            logger.warning("数据库服务不可用，返回空历史")
            return []

        try:
            with self.db_service.get_session() as session:
                query = session.query(UserConfigHistory).filter_by(user_id=user_id)
                
                if section:
                    query = query.filter_by(config_section=section)
                if key:
                    query = query.filter_by(config_key=key)
                
                history_records = (
                    query.order_by(UserConfigHistory.created_at.desc())
                    .limit(limit)
                    .all()
                )

                return [record.to_dict() for record in history_records]

        except Exception as e:
            logger.error(f"获取配置历史失败: {e}")
            return []

    @handle_errors(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.DATABASE_OPERATION,
        user_message="初始化默认配置失败"
    )
    async def initialize_default_configs(self, user_id: str = "default") -> bool:
        """初始化默认用户配置
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否初始化成功
        """
        logger.info(f"开始初始化用户默认配置: {user_id}")

        # 定义需要迁移到数据库的个性化配置
        default_configs = {
            # Ollama AI 个性化配置
            "ollama": {
                "llm_model": "qwen2.5:0.5b",
                "embedding_model": "nomic-embed-text:latest", 
                "value_threshold": 0.3,
                "entity_threshold": 0.8,
                "request_timeout": 30,
                "enable_cache": True,
                "cache_ttl_seconds": 3600,
            },
            
            # 向量搜索个性化配置
            "vector": {
                "vector_dimension": 384,
                "compressed_dimension": 256,
                "max_search_results": 10,
                "search_timeout": 5,
                "compression_method": "PQ",
                "index_type": "HNSW",
            },
            
            # 性能调优配置
            "performance": {
                "enable_caching": True,
                "cache_size_mb": 512,
                "cache_ttl_seconds": 3600,
                "max_workers": 4,
                "max_concurrent_requests": 100,
                "auto_cleanup": True,
                "cleanup_interval_hours": 24,
            },
            
            # 用户界面个性化配置
            "ui": {
                "theme": "auto",
                "language": "zh-CN",
                "layout_density": "comfortable",
                "enable_animations": True,
                "sidebar_collapsed": False,
                "show_advanced_options": False,
            },
            
            # 智能推荐个性化配置
            "recommendation": {
                "enable_smart_suggestions": True,
                "suggestion_threshold": 0.7,
                "max_suggestions": 5,
                "learning_rate": 0.1,
                "enable_context_awareness": True,
            },
            
            # 搜索个性化配置
            "search": {
                "enable_fuzzy_search": True,
                "fuzzy_threshold": 0.8,
                "max_search_history": 100,
                "enable_search_suggestions": True,
                "search_result_grouping": "category",
            }
        }

        try:
            success_count = 0
            total_count = 0
            
            for section, section_configs in default_configs.items():
                for key, default_value in section_configs.items():
                    total_count += 1
                    
                    # 检查配置是否已存在
                    existing_value = await self.get_config_value(section, key, user_id)
                    if existing_value is not None:
                        logger.debug(f"配置已存在，跳过: {section}.{key}")
                        success_count += 1
                        continue
                    
                    # 根据配置类型确定元数据
                    config_meta = self._get_config_metadata(section, key)
                    
                    # 设置默认配置
                    if await self.set_config_value(
                        section=section,
                        key=key,
                        value=default_value,
                        user_id=user_id,
                        config_type=config_meta["config_type"],
                        description=config_meta["description"],
                        is_sensitive=config_meta["is_sensitive"],
                        requires_restart=config_meta["requires_restart"],
                        changed_by="system_init"
                    ):
                        success_count += 1
                        logger.debug(f"默认配置初始化成功: {section}.{key} = {default_value}")
                    else:
                        logger.warning(f"默认配置初始化失败: {section}.{key}")

            logger.info(f"默认配置初始化完成: {success_count}/{total_count} 成功")
            return success_count == total_count

        except Exception as e:
            logger.error(f"初始化默认配置失败: {e}")
            return False

    def _validate_config_value(self, section: str, key: str, value: Any) -> Dict[str, Any]:
        """验证配置值
        
        Args:
            section: 配置段
            key: 配置键
            value: 配置值
            
        Returns:
            验证结果字典
        """
        errors = []

        # 基本验证规则
        validation_rules = {
            ("ollama", "value_threshold"): {"type": float, "min": 0.0, "max": 1.0},
            ("ollama", "entity_threshold"): {"type": float, "min": 0.0, "max": 1.0},
            ("ollama", "request_timeout"): {"type": int, "min": 1, "max": 300},
            ("performance", "cache_size_mb"): {"type": int, "min": 64, "max": 4096},
            ("performance", "max_workers"): {"type": int, "min": 1, "max": 32},
            ("vector", "vector_dimension"): {"type": int, "min": 64, "max": 2048},
            ("vector", "max_search_results"): {"type": int, "min": 1, "max": 100},
        }

        rule_key = (section, key)
        if rule_key in validation_rules:
            rule = validation_rules[rule_key]
            
            # 类型验证
            if not isinstance(value, rule["type"]):
                try:
                    value = rule["type"](value)  # 尝试类型转换
                except (ValueError, TypeError):
                    errors.append(f"配置值类型错误，期望 {rule['type'].__name__}")
                    
            # 范围验证
            if "min" in rule and value < rule["min"]:
                errors.append(f"配置值过小，最小值为 {rule['min']}")
            if "max" in rule and value > rule["max"]:
                errors.append(f"配置值过大，最大值为 {rule['max']}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "normalized_value": value
        }

    def _infer_value_type(self, value: Any) -> str:
        """推断配置值类型
        
        Args:
            value: 配置值
            
        Returns:
            值类型字符串
        """
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "number"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        else:
            return "string"  # 默认为字符串

    def _get_config_metadata(self, section: str, key: str) -> Dict[str, Any]:
        """获取配置元数据
        
        Args:
            section: 配置段
            key: 配置键
            
        Returns:
            配置元数据
        """
        # 配置元数据定义
        metadata_map = {
            # Ollama 配置
            ("ollama", "llm_model"): {
                "config_type": "user_preference",
                "description": "用户首选的LLM模型",
                "is_sensitive": False,
                "requires_restart": False,
            },
            ("ollama", "embedding_model"): {
                "config_type": "user_preference", 
                "description": "用户首选的嵌入模型",
                "is_sensitive": False,
                "requires_restart": False,
            },
            ("ollama", "value_threshold"): {
                "config_type": "system_tuning",
                "description": "AI价值判断阈值",
                "is_sensitive": False,
                "requires_restart": False,
            },
            
            # 性能配置
            ("performance", "cache_size_mb"): {
                "config_type": "system_tuning",
                "description": "缓存大小限制",
                "is_sensitive": False,
                "requires_restart": True,
            },
            ("performance", "max_workers"): {
                "config_type": "system_tuning",
                "description": "最大工作线程数",
                "is_sensitive": False,
                "requires_restart": True,
            },
            
            # UI 配置
            ("ui", "theme"): {
                "config_type": "ui_setting",
                "description": "界面主题",
                "is_sensitive": False,
                "requires_restart": False,
            },
            ("ui", "language"): {
                "config_type": "ui_setting",
                "description": "界面语言",
                "is_sensitive": False,
                "requires_restart": False,
            },
        }

        return metadata_map.get((section, key), {
            "config_type": "user_preference",
            "description": f"{section} 配置项: {key}",
            "is_sensitive": False,
            "requires_restart": False,
        })


# 全局单例
_user_config_db_service: Optional[UserConfigDbService] = None


def get_user_config_db_service() -> UserConfigDbService:
    """获取用户配置数据库服务单例"""
    global _user_config_db_service
    if _user_config_db_service is None:
        _user_config_db_service = UserConfigDbService()
    return _user_config_db_service