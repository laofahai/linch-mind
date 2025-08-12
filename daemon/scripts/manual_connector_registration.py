#!/usr/bin/env python3
"""
手动连接器注册脚本
用于诊断和修复连接器注册机制问题
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "daemon"))

from config.core_config import CoreConfigManager
from config.logging_config import setup_global_logging
from core.container import get_container
from services.connector_registry_service import ConnectorRegistryService
from services.connectors.connector_config_service import ConnectorConfigService
from services.connectors.connector_manager import ConnectorManager
from services.connectors.process_manager import ProcessManager
from services.database_service import DatabaseService

# 设置日志
setup_global_logging(level="INFO", console=True)
logger = logging.getLogger(__name__)


def register_all_services():
    """注册所有必需的服务"""
    container = get_container()

    # 注册所有依赖服务
    services_to_register = [
        (DatabaseService, DatabaseService),
        (ProcessManager, ProcessManager),
        (ConnectorConfigService, ConnectorConfigService),
        (ConnectorRegistryService, ConnectorRegistryService),
        (CoreConfigManager, CoreConfigManager),
        (ConnectorManager, ConnectorManager),
    ]

    for service_type, service_impl in services_to_register:
        if not container.is_registered(service_type):
            container.register_singleton(service_type, service_impl)
            logger.info(f"注册服务: {service_type.__name__}")


async def discover_and_register_connectors():
    """发现并注册所有连接器"""
    logger.info("🔍 开始发现和注册连接器...")

    # 注册所有服务
    register_all_services()

    # 获取连接器管理器
    container = get_container()
    manager = container.get_service(ConnectorManager)

    # 获取连接器目录
    connectors_base_dir = Path(__file__).parent.parent.parent / "connectors"
    logger.info(f"连接器基础目录: {connectors_base_dir}")

    if not connectors_base_dir.exists():
        logger.error(f"连接器目录不存在: {connectors_base_dir}")
        return False

    # 扫描连接器
    discovered = manager.scan_directory_for_connectors(str(connectors_base_dir))
    logger.info(f"发现 {len(discovered)} 个连接器")

    registration_results = []

    for connector_info in discovered:
        connector_id = connector_info["connector_id"]
        name = connector_info["name"]
        is_registered = connector_info["is_registered"]
        executable_path = connector_info.get("path", "")

        logger.info(f"处理连接器: {connector_id}")
        logger.info(f"  名称: {name}")
        logger.info(f"  可执行文件: {executable_path}")
        logger.info(f"  已注册: {is_registered}")

        if not executable_path:
            logger.warning(f"  ❌ 跳过 - 未找到可执行文件")
            registration_results.append(
                {
                    "connector_id": connector_id,
                    "status": "skipped",
                    "reason": "no_executable",
                }
            )
            continue

        if not Path(executable_path).exists():
            logger.warning(f"  ❌ 跳过 - 可执行文件不存在: {executable_path}")
            registration_results.append(
                {
                    "connector_id": connector_id,
                    "status": "skipped",
                    "reason": "executable_not_found",
                }
            )
            continue

        try:
            # 注册连接器
            success = await manager.register_connector(
                connector_id=connector_id,
                name=name,
                description=connector_info.get("description", ""),
                enabled=True,
            )

            if success:
                logger.info(f"  ✅ 注册成功")
                registration_results.append(
                    {
                        "connector_id": connector_id,
                        "status": "registered",
                        "executable_path": executable_path,
                    }
                )
            else:
                logger.error(f"  ❌ 注册失败")
                registration_results.append(
                    {
                        "connector_id": connector_id,
                        "status": "failed",
                        "reason": "registration_error",
                    }
                )

        except Exception as e:
            logger.error(f"  ❌ 注册异常: {e}")
            registration_results.append(
                {"connector_id": connector_id, "status": "error", "error": str(e)}
            )

    # 显示注册结果摘要
    successful = [r for r in registration_results if r["status"] == "registered"]
    failed = [r for r in registration_results if r["status"] in ["failed", "error"]]
    skipped = [r for r in registration_results if r["status"] == "skipped"]

    logger.info(f"📊 注册结果摘要:")
    logger.info(f"  ✅ 成功注册: {len(successful)}")
    logger.info(f"  ❌ 注册失败: {len(failed)}")
    logger.info(f"  ⏭️  跳过: {len(skipped)}")

    if successful:
        logger.info("成功注册的连接器:")
        for result in successful:
            logger.info(f"  - {result['connector_id']}")

    if failed:
        logger.warning("注册失败的连接器:")
        for result in failed:
            logger.warning(
                f"  - {result['connector_id']}: {result.get('reason', result.get('error', 'unknown'))}"
            )

    # 验证数据库中的连接器
    logger.info("🗄️  验证数据库中的连接器...")
    all_connectors = manager.list_connectors()
    logger.info(f"数据库中共有 {len(all_connectors)} 个连接器:")

    for connector in all_connectors:
        logger.info(
            f"  - {connector['connector_id']}: {connector['name']} ({connector['status']})"
        )
        if connector.get("path"):
            logger.info(f"    路径: {connector['path']}")

    return len(successful) > 0


async def test_connector_launch(connector_id: str):
    """测试启动指定连接器"""
    logger.info(f"🚀 测试启动连接器: {connector_id}")

    register_all_services()

    container = get_container()
    manager = container.get_service(ConnectorManager)

    try:
        success = await manager.start_connector(connector_id)

        if success:
            logger.info(f"✅ 连接器启动成功: {connector_id}")

            # 检查状态
            connector_info = manager.get_connector_by_id(connector_id)
            if connector_info:
                logger.info(f"  状态: {connector_info['status']}")
                if connector_info.get("process_id"):
                    logger.info(f"  PID: {connector_info['process_id']}")
        else:
            logger.error(f"❌ 连接器启动失败: {connector_id}")

    except Exception as e:
        logger.error(f"❌ 启动连接器异常 {connector_id}: {e}")
        import traceback

        logger.error(traceback.format_exc())


async def main():
    """主函数"""
    logger.info("🔌 Linch Mind 连接器注册诊断工具")
    logger.info("=" * 50)

    # 1. 发现并注册所有连接器
    success = await discover_and_register_connectors()

    if not success:
        logger.error("❌ 没有成功注册任何连接器")
        return

    # 2. 测试启动已注册的连接器
    logger.info("\n" + "=" * 50)
    logger.info("🧪 测试连接器启动...")

    register_all_services()
    container = get_container()
    manager = container.get_service(ConnectorManager)

    all_connectors = manager.list_connectors()
    for connector in all_connectors:
        if connector["status"] == "stopped" and connector.get("path"):
            await test_connector_launch(connector["connector_id"])

    logger.info("🎉 连接器注册诊断完成!")


if __name__ == "__main__":
    asyncio.run(main())
