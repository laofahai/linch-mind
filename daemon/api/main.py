#!/usr/bin/env python3
"""
Linch Mind API 服务器 - 重构版
Session 5 架构重构 - 精简的应用入口，职责分离
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
from api.dependencies import get_config_manager, cleanup_services, get_connectors, get_db
from api.routers import health, data, ingestion, graph, websocket, connector_lifecycle, connector_installer
from models.database_models import ConnectorInstance
from sqlalchemy.orm import Session

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
    """daemon启动时自动启动已启用的连接器"""
    logger.info("🔌 开始启动已启用的连接器...")
    
    try:
        # 获取新的连接器生命周期管理器
        from services.connectors.lifecycle_manager import get_lifecycle_manager
        lifecycle_manager = get_lifecycle_manager()
        
        # 确保监控任务已启动
        await lifecycle_manager.ensure_monitoring_started()
        
        # 发现可用的连接器类型
        connector_types = await lifecycle_manager.discover_connectors()
        
        if not connector_types:
            logger.info("📝 没有发现连接器类型")
            return
            
        logger.info(f"🔍 发现 {len(connector_types)} 个连接器类型")
        
        # 创建默认实例（如果不存在）
        for connector_type in connector_types:
            type_id = connector_type.type_id
            existing_instances = lifecycle_manager.config_manager.list_instances(type_id=type_id)
            
            if not existing_instances:
                logger.info(f"🔧 为连接器类型 {type_id} 创建默认实例")
                instance_id = await lifecycle_manager.create_instance(
                    type_id=type_id,
                    display_name=f"{connector_type.display_name} 默认实例", 
                    config=connector_type.default_config,
                    auto_start=True
                )
                
                if instance_id:
                    logger.info(f"✅ 默认实例创建成功: {instance_id}")
                else:
                    logger.error(f"❌ 创建默认实例失败: {type_id}")
        
        # 获取所有启用的连接器实例
        all_instances = lifecycle_manager.config_manager.list_instances()
        enabled_instances = [i for i in all_instances if i.enabled and i.auto_start]
        
        if not enabled_instances:
            logger.info("📝 没有启用自动启动的连接器实例")
            return
            
        logger.info(f"🔍 发现 {len(enabled_instances)} 个启用的连接器实例")
        
        # 启动所有启用的连接器实例
        started_count = 0
        failed_count = 0
        
        for instance in enabled_instances:
            instance_id = instance.instance_id
            
            try:
                logger.info(f"▶️  启动连接器实例: {instance_id} ({instance.display_name})")
                
                # 检查实例是否已在运行
                current_state = lifecycle_manager.get_instance_state(instance_id)
                if current_state.value == "running":
                    logger.info(f"⚠️  连接器实例 {instance_id} 已在运行，跳过")
                    started_count += 1  # 算作成功
                    continue
                
                # 启动连接器实例
                success = await lifecycle_manager.start_instance(instance_id)
                
                if success:
                    logger.info(f"✅ 连接器实例 {instance_id} 启动成功")
                    started_count += 1
                else:
                    logger.error(f"❌ 连接器实例 {instance_id} 启动失败")
                    failed_count += 1
                        
            except Exception as e:
                logger.error(f"❌ 启动连接器实例 {instance_id} 时发生异常: {e}")
                failed_count += 1
        
        # 总结启动结果
        logger.info(f"📊 连接器启动完成: 成功 {started_count} 个, 失败 {failed_count} 个")
        
        if failed_count > 0:
            logger.warning(f"⚠️  有 {failed_count} 个连接器启动失败，请检查配置和日志")
        
        if started_count > 0:
            logger.info(f"🎉 系统已启动 {started_count} 个连接器，可以开始收集数据")
                
    except Exception as e:
        logger.error(f"❌ 启动连接器过程中发生异常: {e}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")


# 应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时的初始化
    logger.info("🚀 Linch Mind API 启动中...")
    logger.info("✅ 依赖服务初始化完成")
    
    # 自动启动配置的连接器
    try:
        await auto_start_connectors()
    except Exception as e:
        logger.error(f"自动启动连接器失败: {e}")
    
    yield
    
    # 关闭时的清理
    logger.info("🔄 应用关闭，清理资源...")
    
    # 使用新的生命周期管理器进行清理
    try:
        from services.connectors.lifecycle_manager import get_lifecycle_manager
        lifecycle_manager = get_lifecycle_manager()
        await lifecycle_manager.shutdown_all()
    except Exception as e:
        logger.error(f"关闭连接器时出错: {e}")
    
    await cleanup_services()
    logger.info("✅ 资源清理完成")


# 创建FastAPI应用
def create_app() -> FastAPI:
    """创建和配置FastAPI应用"""
    app = FastAPI(
        title=settings.app_name,
        description=settings.description,
        version=settings.version,
        debug=settings.debug,
        lifespan=lifespan
    )

    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 开发环境，生产环境需要限制
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由模块
    app.include_router(health.router)
    app.include_router(connector_lifecycle.router)  # 新的生命周期管理API
    app.include_router(connector_installer.router)  # 连接器安装管理API
    app.include_router(data.router)
    app.include_router(ingestion.router)
    app.include_router(graph.router)
    app.include_router(websocket.router)
    
    # 添加推荐API别名路由供Flutter调用
    @app.get("/recommendations")
    async def get_recommendations_alias(limit: int = 10):
        """推荐API别名 - 兼容Flutter客户端"""
        from api.routers.data import get_recommendations
        return await get_recommendations(limit)
    
    logger.info("📍 路由注册完成:")
    logger.info("   - Health: / /health /server/info")
    logger.info("   - Connector Lifecycle: /connector-lifecycle/*")
    logger.info("   - Connector Installer: /api/v1/connectors/*")
    logger.info("   - Data: /data/*")
    logger.info("   - Ingestion: /api/v1/*")
    logger.info("   - Graph: /graph/*")
    logger.info("   - WebSocket: /ws/*")

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
                    if 'python' in proc.name().lower() and 'main' in ' '.join(proc.cmdline()):
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
        port = config_manager.config.server.port
        
        # 显示启动信息
        paths = config_manager.get_paths()
        print(f"""
🚀 Linch Mind Daemon 启动中... (重构版)
    
📍 服务信息:
   - API地址: http://localhost:{port}
   - API文档: http://localhost:{port}/docs
   - 进程ID: {os.getpid()}
   
📁 数据目录:
   - 应用数据: {paths['app_data']}
   - 配置文件: {paths['config_file']}
   - 数据库: {paths['database']}/linch_mind.db
   - 日志: {paths['logs']}
   
🏗️ 架构特性:
   - ✅ 模块化路由架构
   - ✅ 智能存储策略
   - ✅ 依赖注入管理
   - ✅ 服务生命周期管理
   
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
        # 清理PID文件
        pid_file = config_manager.get_paths()["app_data"] / "daemon.pid"
        if pid_file.exists():
            try:
                pid_file.unlink()
            except:
                pass


if __name__ == "__main__":
    main()