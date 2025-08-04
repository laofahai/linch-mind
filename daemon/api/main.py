#!/usr/bin/env python3
"""
简化的Linch Mind API服务器 - Session V65
移除复杂的实例管理，使用简化的连接器管理器
"""

import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime
import logging
import uvicorn

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 导入依赖管理和路由
from api.dependencies import get_config_manager, cleanup_services
from api.routers import health
from api.routers.connector_lifecycle_api import router as connector_lifecycle_router
from api.routers.connector_config_api import router as connector_config_router

# 初始化配置和日志
config_manager = get_config_manager()
settings = config_manager.config

log_file = config_manager.get_paths()["logs"] / f"daemon-{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=getattr(logging, settings.server.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def auto_start_connectors():
    """daemon启动时自动启动所有连接器"""
    logger.info("🔌 开始启动连接器...")
    
    try:
        from services.connectors.connector_manager import get_connector_manager
        
        # 获取简化连接器管理器
        manager = get_connector_manager()
        
        # 启动所有已注册连接器
        await manager.start_all_registered_connectors()
        
        # 获取启动结果
        connectors = manager.list_connectors()
        running_count = len([c for c in connectors if c["status"] == "running"])
        
        logger.info(f"🎉 连接器启动完成: {running_count}/{len(connectors)} 个连接器正在运行")
        
        if running_count > 0:
            for connector in connectors:
                if connector["status"] == "running":
                    logger.info(f"  ✅ {connector['name']} (PID: {connector['pid']})")
                else:
                    logger.warning(f"  ❌ {connector['name']} - {connector['status']}")
        
    except Exception as e:
        logger.error(f"❌ 启动连接器失败: {e}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")


async def start_health_check_scheduler():
    """启动健康检查调度器"""
    import asyncio
    from services.connectors.connector_manager import get_connector_manager
    
    async def health_check_loop():
        """定期健康检查循环"""
        manager = get_connector_manager()
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


# 应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时的初始化
    logger.info("🚀 Linch Mind API 启动中... (简化版)")
    logger.info("✅ 依赖服务初始化完成")
    
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
    
    try:
        from services.connectors.connector_manager import get_connector_manager
        manager = get_connector_manager()
        await manager.stop_all_connectors()
        logger.info("✅ 所有连接器已停止")
    except Exception as e:
        logger.error(f"关闭连接器时出错: {e}")
    
    # 清理端口文件
    try:
        config_manager.cleanup_port_file()
        logger.info("✅ 端口文件已清理")
    except Exception as e:
        logger.error(f"清理端口文件时出错: {e}")
    
    await cleanup_services()
    logger.info("✅ 资源清理完成")


# 创建FastAPI应用
def create_app() -> FastAPI:
    """创建和配置FastAPI应用"""
    app = FastAPI(
        title=settings.app_name,
        description=settings.description + " (简化版)",
        version=settings.version,
        debug=settings.debug,
        lifespan=lifespan
    )

    # 配置CORS - 只允许本地访问，防止恶意网站SSRF攻击
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|(\[::1\])):\d+$",
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # 注册路由模块
    app.include_router(health.router)
    app.include_router(connector_lifecycle_router)  # 连接器生命周期API
    app.include_router(connector_config_router)     # 连接器配置管理API
    
    logger.info("📍 路由注册完成:")
    logger.info("   - Health: / /health /server/info")
    logger.info("   - Connector Lifecycle: /connector-lifecycle/*")
    logger.info("   - Connector Config: /connector-config/*")

    return app


# 创建应用实例
app = create_app()


def check_existing_process():
    """检查是否已有进程在运行"""
    pid_file = config_manager.get_paths()["app_data"] / "daemon.pid"
    
    if pid_file.exists():
        try:
            with open(pid_file, 'r') as f:
                old_pid = int(f.read().strip())
            
            # 检查进程是否仍在运行
            import psutil
            if psutil.pid_exists(old_pid):
                try:
                    proc = psutil.Process(old_pid)
                    if 'python' in proc.name().lower() and ('main' in ' '.join(proc.cmdline()) or 'simple_main' in ' '.join(proc.cmdline())):
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
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))
        
        # 获取可用端口
        port = config_manager.get_available_port()
        
        # 验证配置
        config_errors = config_manager.validate_config()
        if config_errors:
            logger.warning(f"配置验证发现问题: {len(config_errors)} 个")
            for error in config_errors:
                logger.warning(f"  - {error}")
        
        # 显示启动信息
        paths = config_manager.get_paths()
        print(f"""
🚀 Linch Mind Daemon 启动中... (简化版 - Session V65)
    
📍 服务信息:
   - API地址: http://localhost:{port}
   - API文档: http://localhost:{port}/docs
   - 进程ID: {os.getpid()}
   
📁 数据目录:
   - 应用数据: {paths['app_data']}
   - 配置文件: {paths['primary_config']}
   - 数据库: {paths['database']}/linch_mind.db
   - 日志: {paths['logs']}
   
🏗️ 架构特性:
   - ✅ 简化连接器管理
   - ✅ 移除实例概念
   - ✅ 直接进程管理
   - ✅ 清晰职责分离
   
⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """)
        
        # 启动服务器
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=port, 
            reload=False,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        raise
    finally:
        # 清理PID文件和端口文件
        pid_file = config_manager.get_paths()["app_data"] / "daemon.pid"
        if pid_file.exists():
            try:
                pid_file.unlink()
            except:
                pass
        
        # 清理端口文件
        config_manager.cleanup_port_file()


if __name__ == "__main__":
    main()