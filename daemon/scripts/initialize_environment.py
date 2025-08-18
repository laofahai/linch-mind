#!/usr/bin/env python3
"""
Environment Initialization System - 智能环境初始化
自动化环境设置：目录、数据库、模型、连接器

核心功能:
- 环境感知的初始化流程
- 数据库Schema自动创建和迁移
- 模型文件下载和配置
- 连接器自动注册和配置
- 健康检查和验证
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# 添加daemon目录到Python路径
daemon_dir = Path(__file__).parent.parent
sys.path.insert(0, str(daemon_dir))

from config.core_config import get_core_config
from core.container import get_container
from core.environment_manager import get_environment_manager
from core.service_facade import get_service, reset_service_facade

logger = logging.getLogger(__name__)


class EnvironmentInitializer:
    """环境初始化器 - 智能自动化设置"""

    def __init__(self):
        self.env_manager = get_environment_manager()
        self.config_manager = get_core_config()
        self.initialization_steps: List[Dict[str, Any]] = []

        logger.info(
            f"Environment Initializer - Target: {self.env_manager.current_environment.value}"
        )

    async def initialize_current_environment(
        self,
        force_reinit: bool = False,
        skip_models: bool = False,
        skip_connectors: bool = False,
    ) -> bool:
        """初始化当前环境

        Args:
            force_reinit: 强制重新初始化
            skip_models: 跳过模型下载
            skip_connectors: 跳过连接器设置

        Returns:
            是否成功初始化
        """
        try:
            logger.info("=" * 60)
            logger.info(f"开始初始化环境: {self.env_manager.current_environment.value}")
            logger.info("=" * 60)

            # 步骤1: 验证目录结构
            await self._ensure_directory_structure()

            # 步骤2: 初始化数据库
            await self._initialize_database(force_reinit)

            # 步骤2.5: 初始化Universal Index服务
            await self._initialize_universal_index()

            # 步骤2.6: 验证AI关联服务配置
            await self._validate_ai_correlation_config()

            # 步骤3: 设置模型文件 (可选)
            if not skip_models:
                await self._setup_models()

            # 步骤4: 配置连接器 (可选)
            if not skip_connectors:
                await self._setup_connectors()

            # 步骤5: 运行健康检查
            health_ok = await self._run_health_checks()

            # 步骤6: 生成初始化报告
            await self._generate_initialization_report()

            if health_ok:
                logger.info("✅ 环境初始化成功完成")
                return True
            else:
                logger.warning("⚠️  环境初始化完成，但存在一些问题")
                return False

        except Exception as e:
            logger.error(f"❌ 环境初始化失败: {e}")
            import traceback

            logger.error(f"错误详情: {traceback.format_exc()}")
            return False

    async def _ensure_directory_structure(self):
        """确保目录结构完整"""
        logger.info("📁 检查目录结构...")

        config = self.env_manager.current_config
        required_dirs = [
            ("基础目录", config.base_path),
            ("配置目录", config.config_dir),
            ("数据目录", config.data_dir),
            ("日志目录", config.logs_dir),
            ("缓存目录", config.cache_dir),
            ("向量目录", config.vectors_dir),
            ("数据库目录", config.database_dir),
        ]

        created_dirs = []
        for name, path in required_dirs:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                created_dirs.append((name, str(path)))
                logger.info(f"  ✅ 创建 {name}: {path}")
            else:
                logger.debug(f"  📁 {name} 已存在: {path}")

        # 共享模型目录
        shared_models = self.env_manager.get_shared_models_directory()
        if not shared_models.exists():
            shared_models.mkdir(parents=True, exist_ok=True)
            created_dirs.append(("共享模型目录", str(shared_models)))
            logger.info(f"  ✅ 创建共享模型目录: {shared_models}")

        self.initialization_steps.append(
            {
                "step": "directory_structure",
                "status": "completed",
                "created_directories": created_dirs,
            }
        )

        logger.info(f"📁 目录结构检查完成 - 创建了 {len(created_dirs)} 个目录")

    async def _initialize_database(self, force_reinit: bool = False):
        """初始化数据库"""
        logger.info("🗄️  初始化数据库...")

        try:
            # 获取数据库服务 (通过DI容器)
            from services.unified_database_service import UnifiedDatabaseService as DatabaseService

            container = get_container()

            # 注册数据库服务 (如果尚未注册)
            if not container.is_registered(DatabaseService):

                def create_database_service():
                    return DatabaseService()

                container.register_singleton(DatabaseService, create_database_service)

            db_service = container.get_service(DatabaseService)

            # 获取数据库信息
            db_info = db_service.get_environment_database_info()
            logger.info(f"数据库URL: {db_info['database_url']}")
            logger.info(f"加密: {db_info['use_encryption']}")

            # 检查数据库是否已存在
            db_exists = db_info.get("database_exists", True)

            if (
                force_reinit
                and db_exists
                and not db_info["database_url"].endswith(":memory:")
            ):
                logger.warning("🔄 强制重新初始化 - 删除现有数据库")
                db_file_path = db_info["database_url"].replace("sqlite:///", "")
                if os.path.exists(db_file_path):
                    os.remove(db_file_path)
                    logger.info("  ✅ 现有数据库已删除")

            # 初始化数据库Schema
            await db_service.initialize()

            # 验证数据库
            stats = db_service.get_database_stats()
            logger.info(
                f"  ✅ 数据库初始化完成 - 连接器表: {stats.get('connectors_count', 0)} 条记录"
            )

            self.initialization_steps.append(
                {
                    "step": "database_initialization",
                    "status": "completed",
                    "database_info": db_info,
                    "stats": stats,
                }
            )

        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            self.initialization_steps.append(
                {"step": "database_initialization", "status": "failed", "error": str(e)}
            )
            raise

    async def _initialize_universal_index(self):
        """初始化Universal Index服务"""
        logger.info("🔍 初始化Universal Index服务...")

        try:
            from services.storage.universal_index_service import UniversalIndexService

            container = get_container()

            # 注册Universal Index服务 (如果尚未注册)
            if not container.is_registered(UniversalIndexService):
                def create_universal_index_service():
                    return UniversalIndexService()
                container.register_singleton(UniversalIndexService, create_universal_index_service)

            # 获取并初始化服务
            universal_index = container.get_service(UniversalIndexService)
            
            # 初始化服务 (创建数据库和表结构)
            success = universal_index.initialize()
            
            if success:
                logger.info("  ✅ Universal Index服务初始化成功")
                
                # 获取统计信息
                stats = universal_index.get_statistics()
                logger.info(f"  📊 索引统计: {stats.get('total_items', 0)} 项")
                
                self.initialization_steps.append({
                    "step": "universal_index_initialization",
                    "status": "completed",
                    "stats": stats
                })
            else:
                raise Exception("Universal Index服务初始化失败")

        except Exception as e:
            logger.error(f"Universal Index初始化失败: {e}")
            self.initialization_steps.append({
                "step": "universal_index_initialization", 
                "status": "failed", 
                "error": str(e)
            })
            # 不抛出异常，Universal Index失败不应阻止整个初始化
            logger.warning("Universal Index初始化失败，但继续其他初始化步骤")
    
    async def _validate_ai_correlation_config(self):
        """验证AI关联服务配置 - 确保AI驱动的事件分析可用"""
        logger.info("🤖 验证AI关联服务配置...")
        
        try:
            # 验证Ollama配置
            from config.database_config_manager import get_unified_config
            config = get_unified_config()
            
            if config and hasattr(config, 'ollama') and config.ollama:
                ollama_config = config.ollama
                logger.info(f"  ✅ Ollama配置已找到: {ollama_config.host}")
                logger.info(f"  📝 AI模型: {ollama_config.llm_model}")
                
                # 验证AI关联器服务
                correlator_status = "unknown"
                buffer_size = 0
                try:
                    from services.event_correlation.ai_driven_correlator import get_ai_correlator
                    correlator = get_ai_correlator()
                    buffer_size = correlator.max_buffer_size
                    logger.info("  🔗 AI驱动关联器初始化成功")
                    logger.info(f"  📊 事件缓冲区容量: {buffer_size}")
                    correlator_status = "ready"
                    
                    # 验证AI服务连通性
                    try:
                        import aiohttp
                        async with aiohttp.ClientSession() as session:
                            async with session.get(f"{ollama_config.host}/api/tags", timeout=aiohttp.ClientTimeout(total=5)) as response:
                                if response.status == 200:
                                    logger.info("  🌐 Ollama服务连通性: ✅ 正常")
                                else:
                                    logger.warning(f"  🌐 Ollama服务响应异常: {response.status}")
                    except Exception as conn_e:
                        logger.warning(f"  🌐 Ollama服务连通性检查失败: {conn_e}")
                        
                except Exception as e:
                    logger.warning(f"  ⚠️ AI关联器初始化警告: {e}")
                    correlator_status = "error"
                
                self.initialization_steps.append({
                    "step": "ai_correlation_config",
                    "status": "completed",
                    "ollama_host": ollama_config.host,
                    "ai_model": ollama_config.llm_model,
                    "ai_driven": True,
                    "correlator_status": correlator_status,
                    "buffer_capacity": buffer_size,
                    "features": [
                        "semantic_analysis",
                        "pattern_discovery", 
                        "behavior_insights",
                        "learning_feedback",
                        "conversational_ai"
                    ]
                })
            else:
                logger.warning("  ⚠️ Ollama配置未找到，AI关联功能将使用降级模式")
                self.initialization_steps.append({
                    "step": "ai_correlation_config",
                    "status": "warning",
                    "ai_driven": False,
                    "fallback_mode": True
                })
            
        except Exception as e:
            logger.error(f"AI关联配置验证失败: {e}")
            self.initialization_steps.append({
                "step": "ai_correlation_config", 
                "status": "failed", 
                "error": str(e)
            })
            # 不抛出异常，配置失败不应阻止整个初始化
            logger.warning("AI关联配置验证失败，但继续其他初始化步骤")

    async def _setup_models(self):
        """设置AI模型文件"""
        logger.info("🤖 设置AI模型...")

        try:
            from config.core_config import get_ai_config

            ai_config = get_ai_config()
            shared_models_dir = self.env_manager.get_shared_models_directory()

            # 检查默认嵌入模型
            default_model = ai_config.default_embedding_model
            logger.info(f"默认嵌入模型: {default_model}")

            # 这里可以添加模型下载逻辑
            # 暂时只记录模型配置
            model_info = {
                "default_embedding_model": default_model,
                "models_directory": str(shared_models_dir),
                "model_providers": len(ai_config.providers),
            }

            self.initialization_steps.append(
                {"step": "model_setup", "status": "completed", "model_info": model_info}
            )

            logger.info("🤖 AI模型设置完成")

        except Exception as e:
            logger.error(f"模型设置失败: {e}")
            self.initialization_steps.append(
                {"step": "model_setup", "status": "failed", "error": str(e)}
            )

    async def _setup_connectors(self):
        """设置连接器基础环境"""
        logger.info("🔌 设置连接器基础环境...")

        try:
            # 仅验证连接器目录存在，不注册服务
            project_root = Path(__file__).parent.parent.parent
            connectors_dir = project_root / "connectors"
            
            if not connectors_dir.exists():
                logger.warning(f"连接器目录不存在: {connectors_dir}")
            
            # 检查官方连接器目录
            official_dir = connectors_dir / "official"
            if official_dir.exists():
                official_connectors = list(official_dir.glob("*/"))
                logger.info(f"  📦 发现 {len(official_connectors)} 个官方连接器目录")
            else:
                logger.info("  📦 官方连接器目录不存在")

            self.initialization_steps.append({
                "step": "connector_setup",
                "status": "completed", 
                "message": "连接器基础环境验证完成"
            })

            logger.info("🔌 连接器基础环境设置完成")

        except Exception as e:
            logger.error(f"连接器环境设置失败: {e}")
            self.initialization_steps.append(
                {"step": "connector_setup", "status": "failed", "error": str(e)}
            )

    async def _auto_discover_connectors(self, connector_manager):
        """自动发现项目中的连接器"""
        from config.core_config import get_connector_config

        connector_config = get_connector_config()
        connectors_dir = Path(connector_config.config_dir)

        if not connectors_dir.exists():
            logger.warning(f"连接器目录不存在: {connectors_dir}")
            return

        # 查找官方连接器
        official_dir = connectors_dir / "official"
        if official_dir.exists():
            for connector_path in official_dir.iterdir():
                if connector_path.is_dir():
                    connector_toml = connector_path / "connector.toml"
                    if connector_toml.exists():
                        try:
                            await self._register_connector(
                                connector_manager, connector_toml
                            )
                        except Exception as e:
                            logger.warning(f"注册连接器失败 {connector_path.name}: {e}")

    async def _register_connector(self, connector_manager, connector_toml_path: Path):
        """注册单个连接器"""
        import tomllib

        with open(connector_toml_path, "rb") as f:
            connector_info = tomllib.load(f)

        # 基础连接器信息
        connector_data = {
            "connector_id": connector_info.get("id", connector_toml_path.parent.name),
            "name": connector_info.get("name", "未知连接器"),
            "version": connector_info.get("version", "1.0.0"),
            "description": connector_info.get("description", ""),
            "executable_path": str(
                connector_toml_path.parent
                / "bin"
                / "release"
                / connector_info.get(
                    "executable", f"linch-mind-{connector_json_path.parent.name}"
                )
            ),
            "config_schema": connector_info.get("config_schema", {}),
            "metadata": connector_info,
        }

        # 检查可执行文件是否存在
        if not Path(connector_data["executable_path"]).exists():
            logger.warning(
                f"连接器可执行文件不存在: {connector_data['executable_path']}"
            )
            return

        # 注册连接器
        success = connector_manager.register_connector(connector_data)
        if success:
            logger.info(f"  ✅ 注册连接器: {connector_data['name']}")
        else:
            logger.warning(f"  ❌ 注册连接器失败: {connector_data['name']}")

    async def _run_health_checks(self) -> bool:
        """运行健康检查"""
        logger.info("🏥 运行健康检查...")

        checks_passed = 0
        total_checks = 0
        health_results = []

        try:
            # 检查1: 目录结构
            total_checks += 1
            config = self.env_manager.current_config
            dirs_ok = all(
                d.exists()
                for d in [
                    config.base_path,
                    config.config_dir,
                    config.data_dir,
                    config.logs_dir,
                    config.cache_dir,
                    config.vectors_dir,
                    config.database_dir,
                ]
            )

            if dirs_ok:
                checks_passed += 1
                health_results.append(("目录结构", "✅", "所有目录存在"))
            else:
                health_results.append(("目录结构", "❌", "部分目录缺失"))

            # 检查2: 数据库连接
            total_checks += 1
            try:
                from services.unified_database_service import UnifiedDatabaseService as DatabaseService

                db_service = get_service(DatabaseService)
                stats = db_service.get_database_stats()
                checks_passed += 1
                health_results.append(
                    (
                        "数据库连接",
                        "✅",
                        f"连接正常 - {stats.get('connectors_count', 0)} 个连接器",
                    )
                )
            except Exception as e:
                health_results.append(("数据库连接", "❌", f"连接失败: {e}"))

            # 检查3: 环境配置
            total_checks += 1
            env_summary = self.env_manager.get_environment_summary()
            if env_summary:
                checks_passed += 1
                health_results.append(
                    ("环境配置", "✅", f"环境: {env_summary['current_environment']}")
                )
            else:
                health_results.append(("环境配置", "❌", "环境配置异常"))

            # 健康检查报告
            logger.info(f"🏥 健康检查完成: {checks_passed}/{total_checks} 项通过")
            for name, status, details in health_results:
                logger.info(f"  {status} {name}: {details}")

            self.initialization_steps.append(
                {
                    "step": "health_checks",
                    "status": "completed",
                    "checks_passed": checks_passed,
                    "total_checks": total_checks,
                    "results": health_results,
                }
            )

            return checks_passed == total_checks

        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            self.initialization_steps.append(
                {"step": "health_checks", "status": "failed", "error": str(e)}
            )
            return False

    async def _generate_initialization_report(self):
        """生成初始化报告"""
        logger.info("📊 生成初始化报告...")

        try:
            config = self.env_manager.current_config
            report_path = (
                config.logs_dir
                / f"initialization-{self.env_manager.current_environment.value}.json"
            )

            report = {
                "environment": self.env_manager.current_environment.value,
                "initialized_at": str(datetime.now()),
                "initialization_steps": self.initialization_steps,
                "environment_summary": self.env_manager.get_environment_summary(),
                "config_info": self.config_manager.get_environment_info(),
            }

            import json

            # 保存报告
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"📊 初始化报告已保存: {report_path}")

            # 显示摘要
            successful_steps = [
                s for s in self.initialization_steps if s["status"] == "completed"
            ]
            failed_steps = [
                s for s in self.initialization_steps if s["status"] == "failed"
            ]

            logger.info("初始化摘要:")
            logger.info(f"  ✅ 成功步骤: {len(successful_steps)}")
            logger.info(f"  ❌ 失败步骤: {len(failed_steps)}")

            if failed_steps:
                logger.warning("失败步骤:")
                for step in failed_steps:
                    logger.warning(
                        f"  - {step['step']}: {step.get('error', '未知错误')}"
                    )

        except Exception as e:
            logger.error(f"生成初始化报告失败: {e}")


async def initialize_environment(
    env_name: Optional[str] = None,
    force_reinit: bool = False,
    skip_models: bool = False,
    skip_connectors: bool = False,
) -> bool:
    """初始化指定环境

    Args:
        env_name: 环境名称，None表示当前环境
        force_reinit: 强制重新初始化
        skip_models: 跳过模型设置
        skip_connectors: 跳过连接器设置

    Returns:
        是否初始化成功
    """
    try:
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # 如果指定了环境名称，先切换环境
        if env_name:
            env_manager = get_environment_manager()
            from core.environment_manager import Environment

            target_env = Environment.from_string(env_name)

            if target_env != env_manager.current_environment:
                logger.info(f"切换到目标环境: {target_env.value}")
                env_manager.permanently_switch_environment(target_env)

                # 重置服务facade以使用新环境
                reset_service_facade()

        # 创建初始化器并执行初始化
        initializer = EnvironmentInitializer()
        success = await initializer.initialize_current_environment(
            force_reinit=force_reinit,
            skip_models=skip_models,
            skip_connectors=skip_connectors,
        )

        return success

    except Exception as e:
        logger.error(f"环境初始化失败: {e}")
        import traceback

        logger.error(f"详细错误: {traceback.format_exc()}")
        return False


async def main():
    """CLI主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Linch Mind Environment Initializer")
    parser.add_argument("--env", "-e", help="目标环境 (development/staging/production)")
    parser.add_argument("--force", "-f", action="store_true", help="强制重新初始化")
    parser.add_argument("--skip-models", action="store_true", help="跳过模型设置")
    parser.add_argument("--skip-connectors", action="store_true", help="跳过连接器设置")
    parser.add_argument("--list-envs", action="store_true", help="列出所有环境")

    args = parser.parse_args()

    if args.list_envs:
        env_manager = get_environment_manager()
        envs = env_manager.list_environments()

        print("可用环境:")
        for env in envs:
            marker = (
                " (当前)"
                if env["name"] == env_manager.current_environment.value
                else ""
            )
            print(f"  - {env['display_name']} ({env['name']}){marker}")
            print(f"    路径: {env['base_path']}")
        return

    # 执行初始化
    success = await initialize_environment(
        env_name=args.env,
        force_reinit=args.force,
        skip_models=args.skip_models,
        skip_connectors=args.skip_connectors,
    )

    if success:
        print("✅ 环境初始化成功完成")
        sys.exit(0)
    else:
        print("❌ 环境初始化失败")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
