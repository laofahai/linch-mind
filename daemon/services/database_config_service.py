#!/usr/bin/env python3
"""
数据库配置服务 - 完全基于数据库的配置管理
替代原有的文件配置系统，统一使用数据库存储所有非构建相关配置

核心设计理念:
- 所有应用配置都存储在数据库中
- 支持环境隔离 (development/staging/production)  
- 支持作用域管理 (system/user/connector)
- 配置优先级和继承
- 实时配置更新，无需重启
- 完整的配置历史和审计
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from core.service_facade import get_database_service
from core.environment_manager import get_environment_manager
from core.error_handling import handle_errors, ErrorSeverity, ErrorCategory
from models.database_models import SystemConfigEntry, SystemConfigHistory

logger = logging.getLogger(__name__)


class DatabaseConfigService:
    """数据库配置服务 - 完全基于数据库的配置管理"""

    def __init__(self):
        self._db_service = None
        self._env_manager = None
        self._config_cache = {}  # 简单的配置缓存

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

    @property 
    def env_manager(self):
        """延迟获取环境管理器"""
        if self._env_manager is None:
            try:
                self._env_manager = get_environment_manager()
            except Exception as e:
                logger.warning(f"环境管理器暂不可用: {e}")
                return None
        return self._env_manager

    def _get_current_environment(self) -> str:
        """获取当前环境"""
        if self.env_manager:
            return self.env_manager.current_environment.value
        return "default"

    @handle_errors(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.DATABASE_OPERATION,
        user_message="获取配置失败"
    )
    async def get_config(
        self,
        section: str,
        key: str,
        environment: str = None,
        scope: str = "system",
        default_value: Any = None
    ) -> Any:
        """获取配置值，支持环境和作用域

        Args:
            section: 配置段
            key: 配置键
            environment: 环境（默认当前环境）
            scope: 作用域（默认system）
            default_value: 默认值

        Returns:
            配置值
        """
        if not self.db_service:
            logger.warning("数据库服务不可用，返回默认值")
            return default_value

        if environment is None:
            environment = self._get_current_environment()

        # 检查缓存
        cache_key = f"{environment}:{scope}:{section}:{key}"
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]

        try:
            with self.db_service.get_session() as session:
                # 按优先级查找配置：当前环境 -> default环境
                environments_to_check = [environment]
                if environment != "default":
                    environments_to_check.append("default")

                for env in environments_to_check:
                    config_entry = (
                        session.query(SystemConfigEntry)
                        .filter_by(
                            environment=env,
                            scope=scope,
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

                        # 缓存配置值
                        self._config_cache[cache_key] = config_entry.config_value
                        
                        logger.debug(f"获取配置成功: {section}.{key} = {config_entry.config_value} (env: {env})")
                        return config_entry.config_value

                logger.debug(f"配置不存在: {section}.{key} (env: {environment}, scope: {scope})")
                return default_value

        except Exception as e:
            logger.error(f"获取配置失败 {section}.{key}: {e}")
            return default_value

    @handle_errors(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.DATABASE_OPERATION,
        user_message="设置配置失败"
    )
    async def set_config(
        self,
        section: str,
        key: str,
        value: Any,
        environment: str = None,
        scope: str = "system",
        config_type: str = "system_setting",
        description: str = None,
        is_sensitive: bool = False,
        requires_restart: bool = False,
        priority: int = 100,
        changed_by: str = "system",
        tags: List[str] = None
    ) -> bool:
        """设置配置值

        Args:
            section: 配置段
            key: 配置键
            value: 配置值
            environment: 环境
            scope: 作用域
            config_type: 配置类型
            description: 描述
            is_sensitive: 是否敏感
            requires_restart: 是否需重启
            priority: 优先级
            changed_by: 变更者
            tags: 标签

        Returns:
            是否设置成功
        """
        if not self.db_service:
            logger.error("数据库服务不可用，无法设置配置")
            return False

        if environment is None:
            environment = self._get_current_environment()

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
                    session.query(SystemConfigEntry)
                    .filter_by(
                        environment=environment,
                        scope=scope,
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
                    existing_config.priority = priority
                    existing_config.last_modified_by = changed_by
                    existing_config.updated_at = datetime.now(timezone.utc)
                    
                    if description:
                        existing_config.description = description
                    if tags:
                        existing_config.tags = tags

                    config_entry = existing_config
                else:
                    # 创建新配置
                    config_entry = SystemConfigEntry(
                        environment=environment,
                        scope=scope,
                        config_section=section,
                        config_key=key,
                        config_value=value,
                        config_type=config_type,
                        value_type=value_type,
                        is_sensitive=is_sensitive,
                        description=description,
                        requires_restart=requires_restart,
                        priority=priority,
                        source="api",
                        last_modified_by=changed_by,
                        tags=tags
                    )
                    session.add(config_entry)

                # 刷新以获取ID（针对新条目）
                session.flush()

                # 保存变更历史
                if old_value != value:
                    history_entry = SystemConfigHistory(
                        config_entry_id=config_entry.id,
                        environment=environment,
                        scope=scope,
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

                # 清除缓存
                cache_key = f"{environment}:{scope}:{section}:{key}"
                self._config_cache.pop(cache_key, None)
                
                logger.info(f"配置设置成功: {section}.{key} = {value} (env: {environment})")
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
        environment: str = None,
        scope: str = "system",
        include_sensitive: bool = False
    ) -> Dict[str, Any]:
        """获取整个配置段的所有配置

        Args:
            section: 配置段名称
            environment: 环境
            scope: 作用域
            include_sensitive: 是否包含敏感配置

        Returns:
            配置字典
        """
        if not self.db_service:
            logger.warning("数据库服务不可用，返回空配置")
            return {}

        if environment is None:
            environment = self._get_current_environment()

        try:
            with self.db_service.get_session() as session:
                # 按优先级查找配置：当前环境 -> default环境
                environments_to_check = [environment]
                if environment != "default":
                    environments_to_check.append("default")

                configs = {}
                processed_keys = set()

                for env in environments_to_check:
                    query = (
                        session.query(SystemConfigEntry)
                        .filter_by(environment=env, scope=scope, config_section=section)
                        .order_by(SystemConfigEntry.priority)
                    )

                    if not include_sensitive:
                        query = query.filter_by(is_sensitive=False)

                    config_entries = query.all()

                    for entry in config_entries:
                        # 只处理尚未处理的键（优先级较高的环境覆盖较低的）
                        if entry.config_key not in processed_keys:
                            configs[entry.config_key] = entry.config_value
                            processed_keys.add(entry.config_key)
                            
                            # 更新访问统计
                            entry.access_count += 1
                            entry.last_accessed = datetime.now(timezone.utc)

                session.commit()
                
                logger.debug(f"获取配置段成功: {section}, {len(configs)} 个配置项 (env: {environment})")
                return configs

        except Exception as e:
            logger.error(f"获取配置段失败 {section}: {e}")
            return {}

    @handle_errors(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.DATABASE_OPERATION,
        user_message="初始化系统配置失败"
    )
    async def initialize_all_configs(self, environment: str = None) -> bool:
        """初始化所有系统配置

        Args:
            environment: 环境名称

        Returns:
            是否初始化成功
        """
        if environment is None:
            environment = self._get_current_environment()

        logger.info(f"开始初始化所有系统配置: {environment}")

        # 定义完整的系统配置，替代原有的文件配置
        all_configs = {
            # 应用基础配置
            "app": {
                "name": "Linch Mind",
                "version": "0.1.0",
                "debug": environment == "development",
                "environment": environment,
            },

            # 数据库配置
            "database": {
                "type": "sqlite",
                "host": "localhost",
                "port": 5432,
                "database": "linch_mind",
                "username": "",
                "password": "",
                "sqlite_file": "linch_mind.db",
                "use_encryption": environment == "production",
                "max_connections": 20,
                "connection_timeout": 30,
            },

            # Ollama AI配置
            "ollama": {
                "host": "http://localhost:11434",
                "embedding_model": "nomic-embed-text:latest",
                "llm_model": "qwen2.5:0.5b",
                "value_threshold": 0.3,
                "entity_threshold": 0.8,
                "max_content_length": 10000,
                "request_timeout": 30,
                "connection_timeout": 5,
                "enable_cache": True,
                "cache_ttl_seconds": 3600,
            },

            # 向量存储配置
            "vector": {
                "provider": "faiss",
                "vector_dimension": 384,
                "compressed_dimension": 256,
                "shard_size_limit": 100000,
                "compression_method": "PQ",
                "index_type": "HNSW",
                "max_memory_mb": 1024,
                "preload_hot_shards": True,
                "max_search_results": 10,
                "search_timeout": 5,
            },

            # IPC通信配置
            "ipc": {
                "socket_path": "",
                "socket_permissions": "0600",
                "pipe_name": "",
                "max_connections": 100,
                "connection_timeout": 30,
                "auth_required": True,
                "buffer_size": 8192,
                "enable_compression": False,
            },

            # 安全配置
            "security": {
                "encrypt_database": environment == "production",
                "encrypt_vectors": False,
                "encrypt_logs": False,
                "enable_access_control": True,
                "allowed_processes": [],
                "enable_audit_logging": environment != "development",
                "audit_log_retention_days": 90,
                "require_authentication": True,
                "session_timeout_minutes": 60,
            },

            # 性能配置
            "performance": {
                "enable_caching": True,
                "cache_size_mb": 512,
                "cache_ttl_seconds": 3600,
                "max_workers": 4,
                "max_concurrent_requests": 100,
                "max_memory_gb": 2.0,
                "max_storage_gb": 10.0,
                "auto_cleanup": environment != "development",
                "cleanup_interval_hours": 24,
            },

            # 日志配置
            "logging": {
                "level": self._get_default_log_level(environment),
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "enable_console": True,
                "enable_file": True,
                "log_file": "linch-mind.log",
                "max_file_size_mb": 10,
                "backup_count": 5,
                "component_levels": {},
            },

            # 连接器配置
            "connectors": {
                "config_directory": "connectors",
                "binary_directory": "connectors/bin",
                "enabled_connectors": {},
                "auto_start": True,
                "restart_on_failure": True,
                "max_restart_attempts": 3,
                "restart_delay_seconds": 5,
                "health_check_interval": 30,
                "log_level": "info",
            },

            # 用户界面配置
            "ui": {
                "theme": "auto",
                "language": "zh-CN",
                "layout_density": "comfortable",
                "enable_animations": True,
                "sidebar_collapsed": False,
                "show_advanced_options": False,
                "max_recent_items": 10,
                "auto_save_interval": 30,
            },

            # AI推荐配置
            "recommendation": {
                "enable_smart_suggestions": True,
                "suggestion_threshold": 0.7,
                "max_suggestions": 5,
                "learning_rate": 0.1,
                "enable_context_awareness": True,
                "update_frequency_hours": 24,
            },

            # 搜索配置
            "search": {
                "enable_fuzzy_search": True,
                "fuzzy_threshold": 0.8,
                "max_search_history": 100,
                "enable_search_suggestions": True,
                "search_result_grouping": "category",
                "index_update_interval": 300,
            },
        }

        try:
            success_count = 0
            total_count = 0

            for section, section_configs in all_configs.items():
                for key, default_value in section_configs.items():
                    total_count += 1

                    # 检查配置是否已存在
                    existing_value = await self.get_config(section, key, environment)
                    if existing_value is not None:
                        logger.debug(f"配置已存在，跳过: {section}.{key}")
                        success_count += 1
                        continue

                    # 获取配置元数据
                    config_meta = self._get_config_metadata(section, key, environment)

                    # 设置默认配置
                    if await self.set_config(
                        section=section,
                        key=key,
                        value=default_value,
                        environment=environment,
                        scope="system",
                        config_type=config_meta["config_type"],
                        description=config_meta["description"],
                        is_sensitive=config_meta["is_sensitive"],
                        requires_restart=config_meta["requires_restart"],
                        priority=config_meta["priority"],
                        changed_by="system_init"
                    ):
                        success_count += 1
                        logger.debug(f"系统配置初始化成功: {section}.{key} = {default_value}")
                    else:
                        logger.warning(f"系统配置初始化失败: {section}.{key}")

            logger.info(f"系统配置初始化完成: {success_count}/{total_count} 成功 (env: {environment})")
            return success_count == total_count

        except Exception as e:
            logger.error(f"初始化系统配置失败: {e}")
            return False

    def _get_default_log_level(self, environment: str) -> str:
        """根据环境获取默认日志级别"""
        env_log_levels = {
            "development": "debug",
            "staging": "info", 
            "production": "warning",
            "default": "info"
        }
        return env_log_levels.get(environment, "info")

    def _get_config_metadata(self, section: str, key: str, environment: str) -> Dict[str, Any]:
        """获取配置元数据"""
        # 敏感配置标记
        sensitive_configs = {
            ("database", "password"),
            ("database", "username"),
            ("ollama", "api_key"),
            ("security", "secret_key"),
        }

        # 需要重启的配置
        restart_required_configs = {
            ("database", "type"),
            ("database", "host"),
            ("database", "port"),
            ("ipc", "socket_path"),
            ("ipc", "pipe_name"),
            ("performance", "max_workers"),
        }

        # 配置类型映射
        config_type_map = {
            "app": "system_setting",
            "database": "system_setting",
            "ipc": "system_setting",
            "security": "system_setting",
            "connectors": "system_setting",
            "ollama": "user_preference",
            "vector": "user_preference", 
            "performance": "user_preference",
            "logging": "user_preference",
            "ui": "ui_setting",
            "recommendation": "user_preference",
            "search": "user_preference",
        }

        is_sensitive = (section, key) in sensitive_configs
        requires_restart = (section, key) in restart_required_configs
        config_type = config_type_map.get(section, "system_setting")

        # 根据环境确定优先级
        priority = 100
        if environment == "production":
            priority = 10  # 生产环境配置优先级最高
        elif environment == "staging":
            priority = 50
        elif environment == "development":
            priority = 80

        return {
            "config_type": config_type,
            "description": f"{section} 配置项: {key}",
            "is_sensitive": is_sensitive,
            "requires_restart": requires_restart,
            "priority": priority,
        }

    def _validate_config_value(self, section: str, key: str, value: Any) -> Dict[str, Any]:
        """验证配置值"""
        errors = []

        # 基本验证规则
        validation_rules = {
            ("database", "port"): {"type": int, "min": 1, "max": 65535},
            ("database", "max_connections"): {"type": int, "min": 1, "max": 1000},
            ("ollama", "value_threshold"): {"type": float, "min": 0.0, "max": 1.0},
            ("ollama", "entity_threshold"): {"type": float, "min": 0.0, "max": 1.0},
            ("ollama", "request_timeout"): {"type": int, "min": 1, "max": 300},
            ("performance", "cache_size_mb"): {"type": int, "min": 64, "max": 4096},
            ("performance", "max_workers"): {"type": int, "min": 1, "max": 32},
            ("vector", "vector_dimension"): {"type": int, "min": 64, "max": 2048},
            ("vector", "max_search_results"): {"type": int, "min": 1, "max": 100},
            ("ipc", "max_connections"): {"type": int, "min": 1, "max": 1000},
            ("security", "session_timeout_minutes"): {"type": int, "min": 1, "max": 1440},
            ("ui", "max_recent_items"): {"type": int, "min": 1, "max": 100},
            ("recommendation", "max_suggestions"): {"type": int, "min": 1, "max": 20},
            ("search", "max_search_history"): {"type": int, "min": 10, "max": 1000},
        }

        rule_key = (section, key)
        if rule_key in validation_rules:
            rule = validation_rules[rule_key]
            
            # 类型验证
            if not isinstance(value, rule["type"]):
                try:
                    value = rule["type"](value)
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
        """推断配置值类型"""
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
            return "string"

    def clear_cache(self):
        """清除配置缓存"""
        self._config_cache.clear()
        logger.debug("配置缓存已清除")


# 已删除：get_database_config_service() - 违反ServiceFacade统一服务获取铁律
# 请使用：from core.service_facade import get_service; get_service(DatabaseConfigService)