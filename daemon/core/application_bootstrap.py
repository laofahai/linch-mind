#!/usr/bin/env python3
"""
应用启动引导器 - main.py重构
职责清晰的模块化启动流程
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from config.config_manager import get_config
from config.logging_config import setup_global_logging

logger = logging.getLogger(__name__)


class ProcessManager:
    """进程管理器 - 处理PID文件和进程检查"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.pid_file = config_manager.paths.pid_file
    
    def check_existing_process(self) -> bool:
        """检查是否已有进程在运行"""
        if not self.pid_file.exists():
            return True
            
        try:
            with open(self.pid_file, "r") as f:
                old_pid = int(f.read().strip())
                
            # 检查进程是否仍在运行
            import psutil
            if psutil.pid_exists(old_pid):
                try:
                    proc = psutil.Process(old_pid)
                    if "python" in proc.name().lower() and (
                        "main" in " ".join(proc.cmdline()) or 
                        "linch-daemon" in " ".join(proc.cmdline())
                    ):
                        print(f"❌ Daemon 已在运行 (PID: {old_pid})")
                        print(f"   请先停止现有进程: kill {old_pid}")
                        return False
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # 清理无效PID文件
            self.pid_file.unlink()
            
        except (ValueError, IOError):
            # PID文件无效，删除它
            self.pid_file.unlink()
            
        return True
    
    def write_pid(self):
        """写入当前进程PID"""
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.pid_file, "w") as f:
            f.write(str(os.getpid()))
    
    def cleanup_pid(self):
        """清理PID文件"""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
        except Exception:
            pass


class StartupValidator:
    """启动验证器 - 验证配置和环境"""
    
    def __init__(self, config_manager):
        self.config = config_manager
    
    def validate_environment(self) -> list[str]:
        """验证环境配置"""
        errors = []
        
        # 检查关键路径
        if not self.config.paths.data_dir.exists():
            errors.append(f"数据目录不存在: {self.config.paths.data_dir}")
        
        if not self.config.paths.config_dir.exists():
            errors.append(f"配置目录不存在: {self.config.paths.config_dir}")
        
        # 检查权限
        try:
            test_file = self.config.paths.data_dir / "test_write"
            test_file.write_text("test")
            test_file.unlink()
        except Exception:
            errors.append(f"数据目录无写权限: {self.config.paths.data_dir}")
        
        # IPC模块检查已跳过 - 直接在运行时处理
        
        return errors
    
    def validate_config(self) -> list[str]:
        """验证配置"""
        errors = []
        
        config = self.config.config
        
        # 验证必需配置
        if not config.app_name:
            errors.append("应用名称未配置")
        
        if not config.ollama_host:
            errors.append("Ollama主机未配置")
        
        if config.vector_dimension <= 0:
            errors.append("向量维度配置无效")
        
        if config.max_workers <= 0:
            errors.append("最大工作线程数配置无效")
        
        return errors


class ServiceInitializer:
    """服务初始化器 - 统一服务启动逻辑"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        
    async def initialize_services(self):
        """初始化所有核心服务"""
        logger.info("🔧 开始初始化核心服务...")
        
        # 1. 初始化DI容器
        await self._initialize_di_container()
        
        # 2. 启用数据库配置
        await self._enable_database_config()
        
        # 3. 启动IPC服务器
        await self._start_ipc_server()
        
        # 4. 启动连接器系统
        await self._start_connectors()
        
        # 5. 启动健康检查
        await self._start_health_monitoring()
        
        logger.info("✅ 所有核心服务初始化完成")
    
    async def _initialize_di_container(self):
        """初始化依赖注入容器"""
        logger.info("🏗️ 初始化DI容器...")
        
        # 使用新的ServiceRegistry
        from core.service_registry import ServiceRegistry
        registry = ServiceRegistry(self.config)
        await registry.register_all_services()
        
        logger.info("✅ DI容器初始化完成")
    
    async def _enable_database_config(self):
        """启用数据库配置"""
        try:
            self.config.enable_database_config()
            logger.info("✅ 数据库配置已启用")
        except Exception as e:
            logger.warning(f"数据库配置启用失败: {e}")
    
    async def _start_ipc_server(self):
        """启动IPC服务器"""
        try:
            from services.ipc.core.server import start_ipc_server
            await start_ipc_server()
            logger.info("✅ IPC服务器已启动")
        except Exception as e:
            logger.error(f"IPC服务器启动失败: {e}")
            raise
    
    async def _start_connectors(self):
        """启动连接器系统"""
        try:
            from core.service_facade import get_service
            from services.connectors.connector_manager import ConnectorManager
            
            manager = get_service(ConnectorManager)
            await manager.start_all_registered_connectors()
            
            connectors = manager.list_connectors()
            running_count = len([c for c in connectors if c["status"] == "running"])
            logger.info(f"✅ 连接器启动: {running_count}/{len(connectors)} 个运行中")
            
        except Exception as e:
            logger.error(f"连接器启动失败: {e}")
    
    async def _start_health_monitoring(self):
        """启动健康监控"""
        try:
            from core.service_facade import get_service
            from services.connectors.health import ConnectorHealthChecker
            from services.connectors.resource_monitor import ResourceProtectionMonitor
            
            # 启动健康检查
            health_checker = get_service(ConnectorHealthChecker)
            await health_checker.start_monitoring()
            
            # 启动资源监控
            resource_monitor = get_service(ResourceProtectionMonitor)
            await resource_monitor.start_monitoring()
            
            logger.info("✅ 健康监控已启动")
            
        except Exception as e:
            logger.error(f"健康监控启动失败: {e}")


class ApplicationBootstrap:
    """应用启动引导器 - 统一启动流程"""
    
    def __init__(self):
        # 1. 初始化配置系统
        self.config = get_config()
        
        # 2. 设置日志系统
        self._setup_logging()
        
        # 3. 初始化组件
        self.process_manager = ProcessManager(self.config)
        self.validator = StartupValidator(self.config)
        self.service_initializer = ServiceInitializer(self.config)
        
        logger.info(f"🚀 ApplicationBootstrap初始化 - environment={self.config.paths.environment}")
    
    def _setup_logging(self):
        """设置日志系统"""
        setup_global_logging(
            level=self.config.config.log_level,
            console=self.config.is_debug,
            json_format=(self.config.config.log_format == "json")
        )
    
    def pre_startup_checks(self) -> bool:
        """启动前检查"""
        logger.info("🔍 执行启动前检查...")
        
        # 1. 检查已有进程
        if not self.process_manager.check_existing_process():
            return False
        
        # 2. 验证环境
        env_errors = self.validator.validate_environment()
        if env_errors:
            logger.error("环境验证失败:")
            for error in env_errors:
                logger.error(f"  - {error}")
            return False
        
        # 3. 验证配置
        config_errors = self.validator.validate_config()
        if config_errors:
            logger.warning("配置验证发现问题:")
            for error in config_errors:
                logger.warning(f"  - {error}")
        
        logger.info("✅ 启动前检查完成")
        return True
    
    def display_startup_info(self):
        """显示启动信息"""
        paths = self.config.get_paths()
        config = self.config.config
        
        print(f"""
🚀 Linch Mind 纯IPC Daemon 启动中... (Session V68-Optimized)

📍 服务信息:
   - 通信方式: 纯IPC (Unix Socket / Named Pipe)
   - 进程ID: {os.getpid()}
   - 环境: {self.config.paths.environment}
   - 调试模式: {config.debug}

📁 数据目录:
   - 根目录: {paths['root']}
   - 数据库: {paths['database']}
   - Socket: {paths['socket']}
   - 日志: {paths['logs']}

🔧 配置信息:
   - Ollama: {config.ollama_host} (model: {config.ollama_model})
   - 向量维度: {config.vector_dimension}
   - 最大工作线程: {config.max_workers}
   - 数据库加密: {config.db_use_encryption}

🏗️ 架构特性:
   - ✅ 纯IPC安全通信
   - ✅ 单一配置入口
   - ✅ 模块化服务注册
   - ✅ 零HTTP暴露风险
   - ✅ 环境隔离支持

⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """)
    
    @asynccontextmanager
    async def application_lifespan(self):
        """应用生命周期管理"""
        logger.info("🚀 应用启动中...")
        
        try:
            # 启动服务
            await self.service_initializer.initialize_services()
            
            logger.info("✅ 应用启动完成")
            yield
            
        finally:
            # 应用关闭清理
            logger.info("🔄 应用关闭，清理资源...")
            await self._cleanup_services()
            logger.info("✅ 资源清理完成")
    
    async def _cleanup_services(self):
        """清理服务"""
        try:
            # 停止IPC服务器
            from services.ipc.core.server import stop_ipc_server
            await stop_ipc_server()
            logger.info("✅ IPC服务器已停止")
            
            # 停止连接器
            from core.service_facade import get_service
            from services.connectors.connector_manager import ConnectorManager
            from core.container import get_container
            
            container = get_container()
            if container.is_registered(ConnectorManager):
                connector_manager = get_service(ConnectorManager)
                await connector_manager.stop_all_connectors()
                logger.info("✅ 连接器已停止")
            
            # 释放容器资源
            await container.dispose_async()
            logger.info("✅ 容器资源已释放")
            
        except Exception as e:
            logger.error(f"服务清理失败: {e}")
    
    async def run(self):
        """运行应用"""
        # 1. 启动前检查
        if not self.pre_startup_checks():
            return
        
        # 2. 写入PID文件
        self.process_manager.write_pid()
        
        try:
            # 3. 显示启动信息
            self.display_startup_info()
            
            # 4. 启动应用
            async with self.application_lifespan():
                # 保持服务运行
                while True:
                    await asyncio.sleep(1)
                    
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在关闭服务...")
        except Exception as e:
            logger.error(f"应用运行失败: {e}")
            raise
        finally:
            # 5. 清理PID文件
            self.process_manager.cleanup_pid()


# =================
# 便捷启动函数
# =================

async def start_application():
    """启动应用 - 供main.py调用"""
    bootstrap = ApplicationBootstrap()
    await bootstrap.run()

def main():
    """主函数 - 简化版main.py"""
    try:
        asyncio.run(start_application())
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        sys.exit(1)