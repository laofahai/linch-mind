#!/usr/bin/env python3
"""
纯IPC主启动脚本 - 完全独立的IPC系统
完全移除FastAPI依赖，使用纯IPC架构
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "daemon"))

# 🚨 架构修复：移除对已删除函数的导入
from config.logging_config import get_logger, setup_global_logging

# 导入核心配置管理器
from config.core_config import get_core_config

# 导入纯IPC服务器
from services.ipc_server import start_ipc_server, stop_ipc_server

# 初始化配置和日志
config_manager = get_core_config()
config = config_manager.config

# 设置全局日志
setup_global_logging(
    level=config.server.log_level, console=config.server.debug, json_format=False
)

# 获取日志记录器
logger = get_logger(__name__)


async def auto_start_connectors():
    """daemon启动时自动启动所有连接器"""
    logger.info("🔌 开始启动连接器...")

    try:
        from pathlib import Path
        from core.container import get_container
        from config.core_config import get_connector_config
        from services.connectors.connector_manager import ConnectorManager

        # 🔧 使用DI容器获取连接器管理器
        container = get_container()
        manager = container.get_service(ConnectorManager)

        # 首先自动注册本地连接器（如果尚未注册）
        try:
            connector_config = get_connector_config()
            connectors_dir = Path(connector_config.config_dir)

            # 扫描并注册未注册的连接器
            discovered_connectors = manager.scan_directory_for_connectors(
                str(connectors_dir)
            )
            for connector in discovered_connectors:
                if not connector.get("is_registered", False):
                    logger.info(f"自动注册连接器: {connector['name']}")
                    connector_path = Path(connector["path"])
                    manager.register_connector_from_path(str(connector_path))
        except Exception as e:
            logger.warning(f"自动注册连接器时出现问题: {e}")

        # 启动所有已注册连接器
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
                    logger.info(f"  ✅ {connector['name']} (PID: {connector['process_id']})")
                else:
                    logger.warning(f"  ❌ {connector['name']} - {connector['status']}")

    except Exception as e:
        logger.error(f"❌ 启动连接器失败: {e}")
        import traceback

        logger.error(f"详细错误信息: {traceback.format_exc()}")


async def start_health_check_scheduler():
    """启动健康检查调度器"""
    from core.container import get_container
    from services.connectors.connector_manager import ConnectorManager

    async def health_check_loop():
        """定期健康检查循环"""
        # 🔧 使用DI容器获取连接器管理器
        container = get_container()
        manager = container.get_service(ConnectorManager)
        
        while True:
            try:
                await asyncio.sleep(30)  # 每30秒检查一次
                manager.health_check_all_connectors()
                logger.debug("健康检查完成")
            except Exception as e:
                logger.error(f"健康检查失败: {e}")

    # 启动后台任务
    asyncio.create_task(health_check_loop())
    logger.info("✅ 健康检查调度器已启动 (30秒间隔)")


def initialize_di_container():
    """🏗️ 初始化依赖注入容器并注册所有核心服务"""
    from core.container import get_container
    from services.ipc_security import IPCSecurityManager, create_security_manager
    from services.connectors.connector_manager import ConnectorManager
    from services.database_service import DatabaseService
    from config.core_config import CoreConfigManager
    
    container = get_container()
    
    # 🔐 安全服务
    container.register_singleton(IPCSecurityManager, create_security_manager)
    logger.debug("已注册: IPCSecurityManager")
    
    # 🗄️ 配置管理服务
    def create_config_manager():
        from config.core_config import get_core_config
        return get_core_config()
    
    container.register_singleton(CoreConfigManager, create_config_manager)
    logger.debug("已注册: CoreConfigManager")
    
    # 💾 数据库服务
    def create_database_service():
        from services.database_service import DatabaseService
        return DatabaseService()
    
    container.register_singleton(DatabaseService, create_database_service)
    logger.debug("已注册: DatabaseService")
    
    # 🔌 连接器管理服务
    def create_connector_manager():
        from services.connectors.connector_manager import ConnectorManager
        from config.core_config import get_connector_config
        connector_config = get_connector_config()
        # 将相对路径转换为项目根目录的绝对路径
        connectors_dir = project_root / connector_config.config_dir
        return ConnectorManager(connectors_dir=connectors_dir)
    
    container.register_singleton(ConnectorManager, create_connector_manager)
    logger.debug("已注册: ConnectorManager")
    
    # 🔧 连接器配置服务
    def create_connector_config_service():
        from services.connectors.connector_config_service import ConnectorConfigService
        from config.core_config import get_connector_config
        connector_config = get_connector_config()
        # 将相对路径转换为项目根目录的绝对路径
        connectors_dir = project_root / connector_config.config_dir
        return ConnectorConfigService(connectors_dir=connectors_dir)
    
    # 导入类型用于注册
    from services.connectors.connector_config_service import ConnectorConfigService
    container.register_singleton(ConnectorConfigService, create_connector_config_service)
    logger.debug("已注册: ConnectorConfigService")
    
    # 🗄️ 存储服务
    def create_vector_service():
        from services.storage.vector_service import VectorService
        from config.core_config import get_storage_config
        storage_config = get_storage_config()
        return VectorService(
            dimension=storage_config.vector_dimension,
            index_file=storage_config.vector_index_path,
            metric=storage_config.distance_metric
        )
    
    # 注册VectorService（如果需要）
    try:
        from services.storage.vector_service import VectorService
        container.register_singleton(VectorService, create_vector_service)
        logger.debug("已注册: VectorService")
    except ImportError:
        logger.debug("VectorService不可用，跳过注册")
    
    # 📊 服务注册完成统计
    registered_services = list(container.get_all_services().keys())
    logger.info("🏗️ 依赖注入容器初始化完成")
    logger.info(f"📦 已注册 {len(registered_services)} 个核心服务:")
    for i, service_name in enumerate(registered_services, 1):
        logger.info(f"    {i}. {service_name}")
    
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
    # 检查PID文件
    pid_file = config_manager.get_paths()["app_data"] / "daemon.pid"
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
        # 写入当前进程PID
        pid_file = config_manager.get_paths()["app_data"] / "daemon.pid"
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))

        # 验证配置
        config_errors = config_manager.validate_config()
        if config_errors:
            logger.warning(f"配置验证发现问题: {len(config_errors)} 个")
            for error in config_errors:
                logger.warning(f"  - {error}")

        # 显示启动信息
        paths = config_manager.get_paths()
        print(
            f"""
🚀 Linch Mind 纯IPC Daemon 启动中... (Session V67)

📍 服务信息:
   - 通信方式: 纯IPC (Unix Socket / Named Pipe)
   - 进程ID: {os.getpid()}
   - 架构: 完全独立于FastAPI的IPC系统

📁 数据目录:
   - 应用数据: {paths['app_data']}
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
        pid_file = config_manager.get_paths()["app_data"] / "daemon.pid"
        if pid_file.exists():
            try:
                pid_file.unlink()
            except Exception:
                pass


if __name__ == "__main__":
    main()
