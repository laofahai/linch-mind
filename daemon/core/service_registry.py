#!/usr/bin/env python3
"""
服务注册表 - 模块化服务注册系统
将main.py中400+行的initialize_di_container()拆分为模块化组件
"""

import logging
from pathlib import Path
from typing import Dict, Type, Any, Optional, Union

from core.container import get_container

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """模块化服务注册表
    
    职责:
    1. 分模块注册服务到DI容器
    2. 管理服务依赖关系
    3. 提供服务注册状态监控
    4. 支持按需注册和延迟注册
    """
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.container = get_container()
        self.registered_services: Dict[str, bool] = {}
        
        logger.info("🏗️ ServiceRegistry初始化")
    
    async def register_all_services(self):
        """注册所有核心服务"""
        logger.info("📦 开始注册所有核心服务...")
        
        # 按依赖关系顺序注册
        await self._register_core_services()
        await self._register_security_services()
        await self._register_environment_services()
        await self._register_config_services()
        await self._register_database_services()
        await self._register_connector_services()
        await self._register_storage_services()
        await self._register_ai_services()  # 重新启用AI服务注册
        await self._register_monitoring_services()
        
        # 输出注册统计
        registered_count = len(self.registered_services)
        logger.info(f"✅ 服务注册完成: {registered_count} 个服务已注册")
        
        for service_name, status in self.registered_services.items():
            if status:
                logger.debug(f"  ✅ {service_name}")
            else:
                logger.warning(f"  ❌ {service_name} (注册失败)")
    
    async def _register_core_services(self):
        """注册核心基础服务"""
        logger.debug("📦 注册核心基础服务...")
        
        # 配置管理器(已初始化)
        self._register_singleton(
            "ConfigManager",
            self.config.__class__,
            lambda: self.config
        )
    
    async def _register_security_services(self):
        """注册安全相关服务"""
        logger.debug("🔐 注册安全服务...")
        
        # IPC安全管理器
        self._register_singleton(
            "IPCSecurityManager",
            "services.ipc.core.security.IPCSecurityManager",
            "services.ipc.core.security.create_security_manager"
        )
        
        # 字段加密管理器
        self._register_singleton(
            "FieldEncryptionManager",
            "services.security.field_encryption.FieldEncryptionManager",
            "services.security.field_encryption.get_encryption_manager"
        )
    
    async def _register_environment_services(self):
        """注册环境管理服务"""
        logger.debug("🌍 注册环境管理服务...")
        
        self._register_singleton(
            "EnvironmentManager",
            "core.environment_manager.EnvironmentManager",
            "core.environment_manager.get_environment_manager"
        )
    
    async def _register_config_services(self):
        """注册配置相关服务"""
        logger.debug("⚙️ 注册配置服务...")
        
        # 数据库配置管理器
        self._register_singleton(
            "DatabaseConfigManager",
            "config.database_config_manager.DatabaseConfigManager",
            lambda: self._create_database_config_manager()
        )
        
        # 系统配置服务
        self._register_singleton(
            "SystemConfigService",
            "services.system_config_service.SystemConfigService",
            "services.system_config_service.SystemConfigService"
        )
        
        # WebView配置服务
        self._register_singleton(
            "WebViewConfigService",
            "services.webview_config_service.WebViewConfigService",
            "services.webview_config_service.WebViewConfigService",
            optional=True
        )
    
    async def _register_database_services(self):
        """注册数据库相关服务"""
        logger.debug("🗄️ 注册数据库服务...")
        
        # 统一数据库服务
        self._register_singleton(
            "UnifiedDatabaseService",
            "services.storage.core.database.UnifiedDatabaseService",
            "services.storage.core.database.UnifiedDatabaseService"
        )
        
        # 数据库管理器
        self._register_singleton(
            "DatabaseManager",
            "core.database_manager.DatabaseManager",
            "core.database_manager.get_database_manager"
        )
    
    async def _register_connector_services(self):
        """注册连接器相关服务"""
        logger.debug("🔌 注册连接器服务...")
        
        # 连接器配置服务
        self._register_singleton(
            "ConnectorConfigService",
            "services.connectors.config.service.ConnectorConfigService",
            lambda: self._create_connector_config_service()
        )
        
        # 进程管理器
        self._register_singleton(
            "ProcessManager",
            "services.connectors.process_manager.ProcessManager",
            "services.connectors.process_manager.get_process_manager"
        )
        
        # 连接器注册服务
        self._register_singleton(
            "ConnectorRegistryService",
            "services.connector_registry_service.ConnectorRegistryService",
            "services.connector_registry_service.ConnectorRegistryService"
        )
        
        # 连接器发现服务
        self._register_singleton(
            "ConnectorDiscoveryService",
            "services.connectors.connector_discovery_service.ConnectorDiscoveryService",
            "services.connectors.connector_discovery_service.ConnectorDiscoveryService"
        )
        
        # 连接器管理器(核心)
        self._register_singleton(
            "ConnectorManager",
            "services.connectors.connector_manager.ConnectorManager",
            lambda: self._create_connector_manager()
        )
    
    async def _register_storage_services(self):
        """注册存储相关服务"""
        logger.debug("💾 注册存储服务...")
        
        # 向量服务
        self._register_singleton(
            "VectorService",
            "services.storage.vector_service.VectorService",
            lambda: self._create_vector_service(),
            optional=True
        )
        
        # 图服务
        self._register_singleton(
            "GraphService",
            "services.storage.graph_service.GraphService",
            lambda: self._create_graph_service(),
            optional=True
        )
        
        # 嵌入服务
        self._register_singleton(
            "EmbeddingService",
            "services.storage.embedding_service.EmbeddingService",
            lambda: self._create_embedding_service(),
            optional=True
        )
        
        # 存储编排器
        self._register_singleton(
            "StorageOrchestrator",
            "services.storage.storage_orchestrator.StorageOrchestrator",
            "services.storage.storage_orchestrator.StorageOrchestrator",
            optional=True
        )
        
        # 缓存NetworkX服务
        self._register_singleton(
            "CachedNetworkXService",
            "services.cached_networkx_service.CachedNetworkXService",
            "services.cached_networkx_service.CachedNetworkXService",
            optional=True
        )
    
    async def _register_ai_services(self):
        """注册AI相关服务"""
        logger.debug("🧠 注册AI服务...")
        
        # Ollama服务
        self._register_singleton(
            "OllamaService",
            "services.ai.ollama_service.OllamaService",
            "services.ai.ollama_service.OllamaService"
        )
        
        # 内容分析服务
        self._register_singleton(
            "ContentAnalysisService",
            "services.content_analysis_service.ContentAnalysisService",
            "services.content_analysis_service.ContentAnalysisService"
        )
        
        # 数据洞察服务
        self._register_singleton(
            "DataInsightsService",
            "services.api.data_insights_service.DataInsightsService",
            "services.api.data_insights_service.DataInsightsService"
        )
    
    async def _register_monitoring_services(self):
        """注册监控相关服务"""
        logger.debug("📊 注册监控服务...")
        
        # 连接器健康检查
        self._register_singleton(
            "ConnectorHealthChecker",
            "services.connectors.health.ConnectorHealthChecker",
            "services.connectors.health.ConnectorHealthChecker"
        )
        
        # 资源保护监控
        self._register_singleton(
            "ResourceProtectionMonitor",
            "services.connectors.resource_monitor.ResourceProtectionMonitor",
            "services.connectors.resource_monitor.ResourceProtectionMonitor"
        )
        
        # 共享执行器服务
        self._register_singleton(
            "SharedExecutorService",
            "services.shared_executor_service.SharedExecutorService",
            "services.shared_executor_service.get_shared_executor_service"
        )
    
    # =================
    # 服务创建工厂方法
    # =================
    
    def _create_database_config_manager(self):
        """创建数据库配置管理器"""
        from config.database_config_manager import DatabaseConfigManager
        return DatabaseConfigManager()
    
    def _create_connector_config_service(self):
        """创建连接器配置服务"""
        from services.connectors.config.service import ConnectorConfigService
        
        # 获取连接器目录
        connectors_dir = self.config.get_paths()["data"] / "connectors"
        return ConnectorConfigService(connectors_dir=connectors_dir)
    
    def _create_connector_manager(self):
        """创建连接器管理器"""
        from services.connectors.connector_manager import ConnectorManager
        from services.storage.core.database import UnifiedDatabaseService
        from services.connectors.process_manager import ProcessManager
        from services.connectors.config.service import ConnectorConfigService
        from services.connector_registry_service import ConnectorRegistryService
        
        # 手动依赖注入
        db_service = self.container.get_service(UnifiedDatabaseService)
        process_manager = self.container.get_service(ProcessManager)
        config_service = self.container.get_service(ConnectorConfigService)
        registry_service = self.container.get_service(ConnectorRegistryService)
        
        # 使用项目连接器目录作为默认
        project_root = Path(__file__).parent.parent.parent
        default_connectors_dir = project_root / "connectors"
        
        return ConnectorManager(
            connectors_dir=default_connectors_dir,
            db_service=db_service,
            process_manager=process_manager,
            config_service=config_service,
            registry_service=registry_service,
            config_manager=self.config
        )
    
    def _create_vector_service(self):
        """创建向量服务"""
        from services.storage.vector_service import VectorService
        
        config = self.config.config
        vectors_dir = self.config.get_paths()["vectors"]
        
        return VectorService(
            data_dir=vectors_dir,
            dimension=config.vector_dimension,
            index_type=config.vector_index_type,
            max_workers=config.max_workers
        )
    
    def _create_graph_service(self):
        """创建图服务"""
        from services.storage.graph_service import GraphService
        
        graph_dir = self.config.get_paths()["graph"]
        
        return GraphService(
            data_dir=graph_dir,
            max_workers=self.config.config.max_workers,
            enable_cache=True
        )
    
    def _create_embedding_service(self):
        """创建嵌入服务"""
        from services.storage.embedding_service import EmbeddingService
        
        embeddings_dir = self.config.get_paths()["embeddings"]
        
        return EmbeddingService(
            model_name="all-MiniLM-L6-v2",
            cache_dir=embeddings_dir,
            max_workers=2,
            enable_cache=True
        )
    
    # =================
    # 辅助方法
    # =================
    
    def _register_singleton(self, 
                          service_name: str,
                          service_type: Union[str, Type],
                          factory_func: Union[str, callable],
                          optional: bool = False):
        """注册单例服务
        
        Args:
            service_name: 服务名称(用于日志)
            service_type: 服务类型(可以是字符串或类型)
            factory_func: 工厂函数(可以是字符串路径或callable)
            optional: 是否为可选服务
        """
        try:
            # 动态导入服务类型
            if isinstance(service_type, str):
                service_class = self._import_class(service_type)
            else:
                service_class = service_type
            
            # 创建工厂函数
            if isinstance(factory_func, str):
                factory = self._import_function(factory_func)
            else:
                factory = factory_func
            
            # 注册到容器
            self.container.register_singleton(service_class, factory)
            self.registered_services[service_name] = True
            logger.debug(f"  ✅ {service_name}")
            
        except Exception as e:
            self.registered_services[service_name] = False
            if optional:
                logger.debug(f"  ⚠️ {service_name} (可选服务，跳过)")
            else:
                logger.error(f"  ❌ {service_name}: {e}")
                raise
    
    def _import_class(self, class_path: str) -> Type:
        """动态导入类"""
        module_path, class_name = class_path.rsplit(".", 1)
        module = __import__(module_path, fromlist=[class_name])
        return getattr(module, class_name)
    
    def _import_function(self, func_path: str) -> callable:
        """动态导入函数"""
        module_path, func_name = func_path.rsplit(".", 1)
        module = __import__(module_path, fromlist=[func_name])
        return getattr(module, func_name)
    
    def get_registration_status(self) -> Dict[str, bool]:
        """获取服务注册状态"""
        return self.registered_services.copy()
    
    def is_service_registered(self, service_name: str) -> bool:
        """检查服务是否已注册"""
        return self.registered_services.get(service_name, False)