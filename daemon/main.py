#!/usr/bin/env python3
"""
纯IPC主启动脚本 - 完全独立的IPC系统
完全移除FastAPI依赖，使用纯IPC架构
"""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

# 使用标准Python包导入，无需动态路径添加

# 🚀 导入优化的延迟配置管理器
from config.lazy_config import get_lazy_config_manager
from config.core_config import get_core_config  # 保持兼容

# 🚨 架构修复：移除对已删除函数的导入
from config.logging_config import get_logger, setup_global_logging

# 导入纯IPC服务器
from services.ipc_server import start_ipc_server, stop_ipc_server

# 🚀 初始化延迟配置管理器 - 显著减少启动时间
lazy_config_manager = get_lazy_config_manager()
# 仅获取启动必需的服务器配置
server_config = lazy_config_manager.get_server_config()
# 获取核心路径，无需加载完整配置
core_paths = lazy_config_manager.get_core_paths()

# 🚀 设置全局日志 - 使用延迟加载的配置
setup_global_logging(
    level=server_config.log_level, console=server_config.debug, json_format=False
)

# 获取日志记录器
logger = get_logger(__name__)


async def auto_start_connectors():
    """daemon启动时启动已注册的连接器（环境感知但不自动发现）"""
    logger.info("🔌 环境感知连接器启动...")

    try:
        from core.container import get_container
        from core.environment_manager import EnvironmentManager
        from services.connectors.connector_manager import ConnectorManager

        # 🔧 使用DI容器获取服务
        container = get_container()
        env_manager = container.get_service(EnvironmentManager)
        manager = container.get_service(ConnectorManager)

        current_env = env_manager.current_environment
        logger.info(f"当前环境: {current_env.value}")

        # 启动所有已注册连接器（不做自动发现）
        await manager.start_all_registered_connectors()

        # 获取启动结果
        connectors = manager.list_connectors()
        running_count = len([c for c in connectors if c["status"] == "running"])

        logger.info(
            f"🎉 连接器启动完成: {running_count}/{len(connectors)} 个连接器正在运行"
        )

        if running_count > 0:
            for connector in connectors:
                if connector["status"] == "running":
                    logger.info(
                        f"  ✅ {connector['name']} (PID: {connector['process_id']})"
                    )
                else:
                    logger.warning(f"  ❌ {connector['name']} - {connector['status']}")

    except Exception as e:
        logger.error(f"❌ 启动连接器失败: {e}")
        import traceback

        logger.error(f"详细错误信息: {traceback.format_exc()}")


async def start_health_check_scheduler():
    """启动健康检查调度器"""
    from core.service_facade import get_service
    from services.connectors.health import ConnectorHealthChecker

    try:
        # 🏥 使用ServiceFacade获取健康检查器
        health_checker = get_service(ConnectorHealthChecker)

        # 启动专门的健康监控任务
        await health_checker.start_monitoring()

        logger.info("✅ 连接器健康检查服务已启动")

    except Exception as e:
        logger.error(f"❌ 启动健康检查服务失败: {e}")
        import traceback

        logger.error(f"详细错误信息: {traceback.format_exc()}")


def initialize_di_container():
    """🏗️ 初始化依赖注入容器并注册所有核心服务"""
    from config.core_config import CoreConfigManager
    from core.container import get_container
    from services.connectors.connector_manager import ConnectorManager
    from services.unified_database_service import UnifiedDatabaseService
    from services.ipc_security import IPCSecurityManager, create_security_manager

    container = get_container()

    # 🔐 安全服务
    container.register_singleton(IPCSecurityManager, create_security_manager)
    logger.debug("已注册: IPCSecurityManager")

    # 🆕 环境管理服务 (优先注册，其他服务依赖它)
    def create_environment_manager():
        from core.environment_manager import get_environment_manager

        return get_environment_manager()

    from core.environment_manager import EnvironmentManager

    container.register_singleton(EnvironmentManager, create_environment_manager)
    logger.debug("已注册: EnvironmentManager")

    # 🗄️ 配置管理服务
    def create_config_manager():
        # 🚀 使用延迟配置管理器
        return lazy_config_manager

    container.register_singleton(CoreConfigManager, create_config_manager)
    logger.debug("已注册: CoreConfigManager")

    # 💾 统一数据库服务
    def create_unified_database_service():
        from services.unified_database_service import UnifiedDatabaseService

        return UnifiedDatabaseService()

    container.register_singleton(UnifiedDatabaseService, create_unified_database_service)
    logger.debug("已注册: DatabaseService")

    # 🔧 连接器配置服务
    def create_connector_config_service():
        from config.core_config import get_connector_config
        from services.connectors.connector_config_service import ConnectorConfigService

        connector_config = get_connector_config()
        # 将相对路径转换为项目根目录的绝对路径
        connectors_dir = project_root / connector_config.config_dir
        return ConnectorConfigService(connectors_dir=connectors_dir)

    # 导入类型用于注册
    from services.connectors.connector_config_service import ConnectorConfigService

    container.register_singleton(
        ConnectorConfigService, create_connector_config_service
    )
    logger.debug("已注册: ConnectorConfigService")

    # 🔄 进程管理服务
    def create_process_manager():
        from services.connectors.process_manager import ProcessManager

        return ProcessManager()

    from services.connectors.process_manager import ProcessManager

    container.register_singleton(ProcessManager, create_process_manager)
    logger.debug("已注册: ProcessManager")

    # 📋 连接器注册服务
    def create_connector_registry_service():
        from services.connector_registry_service import ConnectorRegistryService

        return ConnectorRegistryService()

    from services.connector_registry_service import ConnectorRegistryService

    container.register_singleton(
        ConnectorRegistryService, create_connector_registry_service
    )
    logger.debug("已注册: ConnectorRegistryService")

    # 🔍 连接器发现服务
    def create_connector_discovery_service():
        from services.connectors.connector_discovery_service import ConnectorDiscoveryService
        
        return ConnectorDiscoveryService()

    from services.connectors.connector_discovery_service import ConnectorDiscoveryService

    container.register_singleton(
        ConnectorDiscoveryService, create_connector_discovery_service
    )
    logger.debug("已注册: ConnectorDiscoveryService")

    # 🔌 连接器管理服务
    def create_connector_manager():
        from config.core_config import get_connector_config
        from services.connectors.connector_manager import ConnectorManager

        connector_config = get_connector_config()
        # 将相对路径转换为项目根目录的绝对路径
        connectors_dir = project_root / connector_config.config_dir

        # 手动依赖注入，避免ServiceFacade循环问题
        db_service = container.get_service(UnifiedDatabaseService)
        process_manager = container.get_service(ProcessManager)
        config_service = container.get_service(ConnectorConfigService)
        registry_service = container.get_service(ConnectorRegistryService)
        config_manager = container.get_service(CoreConfigManager)

        return ConnectorManager(
            connectors_dir=connectors_dir,
            db_service=db_service,
            process_manager=process_manager,
            config_service=config_service,
            registry_service=registry_service,
            config_manager=config_manager,
        )

    container.register_singleton(ConnectorManager, create_connector_manager)
    logger.debug("已注册: ConnectorManager")

    # 🏥 连接器健康检查服务
    def create_connector_health_checker():
        from services.connectors.health import ConnectorHealthChecker

        # ConnectorHealthChecker将通过ServiceFacade自动获取ConnectorManager依赖
        return ConnectorHealthChecker()

    from services.connectors.health import ConnectorHealthChecker

    container.register_singleton(
        ConnectorHealthChecker, create_connector_health_checker
    )
    logger.debug("已注册: ConnectorHealthChecker")

    # 🛠️ 系统配置服务
    def create_system_config_service():
        from services.system_config_service import SystemConfigService

        return SystemConfigService()

    from services.system_config_service import SystemConfigService

    container.register_singleton(SystemConfigService, create_system_config_service)
    logger.debug("已注册: SystemConfigService")

    # 🗄️ 存储服务
    def create_vector_service():
        from config.core_config import get_storage_config
        from services.storage.vector_service import VectorService

        storage_config = get_storage_config()
        app_data_dir = core_paths["app_data"]
        return VectorService(
            data_dir=app_data_dir / "vectors",
            dimension=storage_config.vector_dimension,
            index_type=storage_config.vector_index_type,
            max_workers=storage_config.vector_max_workers,
        )

    # 注册VectorService（如果需要）
    try:
        from services.storage.vector_service import VectorService

        container.register_singleton(VectorService, create_vector_service)
        logger.debug("已注册: VectorService")
    except ImportError:
        logger.debug("VectorService不可用，跳过注册")

    # 🧠 智能处理服务
    def create_embedding_service():
        from services.storage.embedding_service import EmbeddingService

        app_data_dir = core_paths["app_data"]
        return EmbeddingService(
            model_name="all-MiniLM-L6-v2",
            cache_dir=app_data_dir / "embeddings",
            max_workers=2,
            enable_cache=True,
        )

    try:
        from services.storage.embedding_service import EmbeddingService

        container.register_singleton(EmbeddingService, create_embedding_service)
        logger.debug("已注册: EmbeddingService")
    except ImportError:
        logger.debug("EmbeddingService不可用，跳过注册")

    def create_graph_service():
        from services.storage.graph_service import GraphService

        app_data_dir = core_paths["app_data"]
        return GraphService(
            data_dir=app_data_dir / "graph", max_workers=4, enable_cache=True
        )

    try:
        from services.storage.graph_service import GraphService

        container.register_singleton(GraphService, create_graph_service)
        logger.debug("已注册: GraphService")
    except ImportError:
        logger.debug("GraphService不可用，跳过注册")

    def create_storage_orchestrator():
        from services.storage.storage_orchestrator import StorageOrchestrator

        return StorageOrchestrator()

    try:
        from services.storage.storage_orchestrator import StorageOrchestrator

        container.register_singleton(StorageOrchestrator, create_storage_orchestrator)
        logger.debug("已注册: StorageOrchestrator")
    except ImportError:
        logger.debug("StorageOrchestrator不可用，跳过注册")

    # 📊 服务注册完成统计
    registered_services = list(container.get_all_services().keys())
    logger.info("🏗️ 依赖注入容器初始化完成")
    logger.info(f"📦 已注册 {len(registered_services)} 个核心服务:")
    for i, service_name in enumerate(registered_services, 1):
        logger.info(f"    {i}. {service_name}")

    # 🔧 调试：验证容器实例一致性
    from core.service_facade import _service_facade

    facade_container = _service_facade.container
    logger.debug(
        f"Main容器ID: {id(container)}, ServiceFacade容器ID: {id(facade_container)}"
    )
    logger.debug(
        f"Main容器服务数: {len(container.get_all_services())}, Facade容器服务数: {len(facade_container.get_all_services())}"
    )

    # 🔧 重置ServiceFacade容器，确保获取最新的已注册服务
    from core.service_facade import reset_service_facade

    reset_service_facade()
    logger.debug("ServiceFacade已重置，确保获取最新容器")

    return container


@asynccontextmanager
async def ipc_lifespan():
    """纯IPC应用生命周期管理"""
    # 启动时的初始化
    logger.info("🚀 Linch Mind 纯IPC服务 启动中...")

    # 初始化依赖注入容器
    initialize_di_container()

    logger.info("✅ 依赖服务初始化完成")

    # 启动IPC服务器
    try:
        await start_ipc_server()
        logger.info("✅ 纯IPC服务器已启动 (无FastAPI依赖)")
    except Exception as e:
        logger.error(f"启动IPC服务器失败: {e}")

    # 自动启动连接器
    try:
        await auto_start_connectors()
    except Exception as e:
        logger.error(f"自动启动连接器失败: {e}")

    # 启动健康检查调度器
    try:
        await start_health_check_scheduler()
    except Exception as e:
        logger.error(f"启动健康检查调度器失败: {e}")

    yield

    # 关闭时的清理
    logger.info("🔄 应用关闭，清理资源...")

    # 停止IPC服务器
    try:
        await stop_ipc_server()
        logger.info("✅ IPC服务器已停止")
    except Exception as e:
        logger.error(f"停止IPC服务器时出错: {e}")

    # 🔧 使用DI容器进行服务清理
    try:
        from core.container import get_container
        from services.connectors.connector_manager import ConnectorManager

        container = get_container()

        # 清理连接器管理服务
        if container.is_registered(ConnectorManager):
            connector_manager = container.get_service(ConnectorManager)
            await connector_manager.stop_all_connectors()
            logger.info("✅ 连接器管理器已清理")

        # 释放DI容器资源
        await container.dispose_async()
        logger.info("✅ DI容器资源已释放")

    except Exception as e:
        logger.error(f"DI容器清理失败: {e}")

    logger.info("✅ 资源清理完成")


def check_existing_process():
    """检查是否已有进程在运行"""
    # 检查PID文件 - 使用管理脚本期望的位置
    runtime_dir = Path.home() / ".linch-mind"
    pid_file = runtime_dir / "daemon.pid"
    if pid_file.exists():
        try:
            with open(pid_file, "r") as f:
                old_pid = int(f.read().strip())

            # 检查进程是否仍在运行
            import psutil

            if psutil.pid_exists(old_pid):
                try:
                    proc = psutil.Process(old_pid)
                    if "python" in proc.name().lower() and (
                        "main" in " ".join(proc.cmdline())
                        or "linch-daemon" in " ".join(proc.cmdline())
                    ):
                        print(f"❌ Daemon 已在运行 (PID: {old_pid})")
                        print(f"   请先停止现有进程: kill {old_pid}")
                        return False
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # 清理无效的PID文件
            pid_file.unlink()
        except (ValueError, IOError):
            # PID文件无效，删除它
            pid_file.unlink()

    return True


def main():
    """主启动函数"""
    if not check_existing_process():
        return

    try:
        # 写入当前进程PID - 使用管理脚本期望的位置
        runtime_dir = Path.home() / ".linch-mind"
        runtime_dir.mkdir(exist_ok=True)
        pid_file = runtime_dir / "daemon.pid"
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))

        # 🚀 验证配置 - 仅在需要时加载完整配置
        try:
            config_errors = lazy_config_manager.validate_config()
            if config_errors:
                logger.warning(f"配置验证发现问题: {len(config_errors)} 个")
                for error in config_errors:
                    logger.warning(f"  - {error}")
        except Exception as e:
            logger.warning(f"配置验证跳过: {e}")

        # 显示启动信息 - 使用核心路径
        paths = core_paths
        print(
            f"""
🚀 Linch Mind 纯IPC Daemon 启动中... (Session V67)

📍 服务信息:
   - 通信方式: 纯IPC (Unix Socket / Named Pipe)
   - 进程ID: {os.getpid()}
   - 架构: 完全独立于FastAPI的IPC系统

📁 数据目录:
   - 应用数据: {paths['data']}
   - 配置文件: {paths['primary_config']}
   - 数据库: {paths['database']}/linch_mind.db
   - 日志: {paths['logs']}

🏗️ 架构特性:
   - ✅ 纯IPC安全通信
   - ✅ 本地进程验证
   - ✅ 跨平台兼容
   - ✅ 无HTTP暴露
   - ✅ 完全移除FastAPI依赖
   - ✅ 向后兼容API接口

⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        )

        # 启动纯IPC服务器
        async def run_ipc_service():
            # 手动触发应用的lifespan
            async with ipc_lifespan():
                # 保持服务运行
                while True:
                    await asyncio.sleep(1)

        asyncio.run(run_ipc_service())

    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务...")
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        raise
    finally:
        # 清理PID文件
        pid_file = core_paths["data"] / "daemon.pid"
        if pid_file.exists():
            try:
                pid_file.unlink()
            except Exception:
                pass  # nosec B110


if __name__ == "__main__":
    main()
