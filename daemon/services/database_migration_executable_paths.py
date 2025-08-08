#!/usr/bin/env python3
"""
数据库迁移脚本: 更新连接器executable_path配置

更新现有连接器的executable_path配置，使其使用新的统一命名格式:
bin/release/linch-mind-{connector-id}

使用方法:
    poetry run python services/database_migration_executable_paths.py --dry-run  # 预览更改
    poetry run python services/database_migration_executable_paths.py --apply    # 应用更改
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

from database_service import DatabaseService

from models.database_models import Connector

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ExecutablePathMigrator:
    """连接器可执行路径迁移器"""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.base_path = Path(__file__).parent.parent.parent / "connectors" / "official"

    def get_new_executable_path(self, connector_id: str) -> Optional[str]:
        """
        获取连接器的新可执行路径

        Args:
            connector_id: 连接器ID

        Returns:
            新的可执行路径，如果文件不存在则返回None
        """
        new_path = (
            self.base_path
            / connector_id
            / "bin"
            / "release"
            / f"linch-mind-{connector_id}"
        )

        if new_path.exists():
            return str(new_path)

        # 检查是否存在其他可能的路径
        alternative_paths = [
            self.base_path / connector_id / f"linch-mind-{connector_id}",
            self.base_path
            / connector_id
            / "dist"
            / "bin"
            / f"linch-mind-{connector_id}",
            self.base_path / connector_id / "build" / f"linch-mind-{connector_id}",
        ]

        for alt_path in alternative_paths:
            if alt_path.exists():
                logger.warning(
                    f"连接器 {connector_id} 的可执行文件存在于替代路径: {alt_path}"
                )
                logger.warning(f"建议移动到标准路径: {new_path}")
                return str(alt_path)

        logger.error(f"连接器 {connector_id} 的可执行文件不存在于任何已知路径")
        return None

    def analyze_current_state(self) -> List[Dict]:
        """
        分析当前数据库中的连接器状态

        Returns:
            连接器状态分析结果列表
        """
        results = []

        with self.db_service.get_session() as session:
            connectors = session.query(Connector).all()

            for connector in connectors:
                current_path = None
                if connector.config_data and "executable_path" in connector.config_data:
                    current_path = connector.config_data["executable_path"]

                new_path = self.get_new_executable_path(connector.connector_id)

                results.append(
                    {
                        "connector_id": connector.connector_id,
                        "name": connector.name,
                        "current_path": current_path,
                        "new_path": new_path,
                        "needs_update": current_path != new_path
                        and new_path is not None,
                        "file_exists": new_path is not None,
                    }
                )

        return results

    def preview_changes(self) -> None:
        """预览将要进行的更改"""
        logger.info("=" * 80)
        logger.info("连接器可执行路径迁移预览")
        logger.info("=" * 80)

        analysis = self.analyze_current_state()

        updates_needed = 0
        missing_files = 0

        for result in analysis:
            logger.info(f"\n连接器: {result['connector_id']} ({result['name']})")
            logger.info(f"  当前路径: {result['current_path']}")
            logger.info(f"  新路径:   {result['new_path']}")

            if not result["file_exists"]:
                logger.error(f"  状态:     ❌ 可执行文件不存在")
                missing_files += 1
            elif result["needs_update"]:
                logger.info(f"  状态:     🔄 需要更新")
                updates_needed += 1
            else:
                logger.info(f"  状态:     ✅ 无需更新")

        logger.info("\n" + "=" * 80)
        logger.info(f"迁移摘要:")
        logger.info(f"  总连接器数量: {len(analysis)}")
        logger.info(f"  需要更新: {updates_needed}")
        logger.info(f"  缺少文件: {missing_files}")

        if missing_files > 0:
            logger.warning(f"\n⚠️  有 {missing_files} 个连接器的可执行文件不存在")
            logger.warning("请先构建这些连接器，然后再运行迁移")

        return updates_needed, missing_files

    def apply_migration(self, force: bool = False) -> bool:
        """
        应用迁移

        Args:
            force: 是否强制应用（即使有缺失文件）

        Returns:
            是否成功应用迁移
        """
        updates_needed, missing_files = self.preview_changes()

        if missing_files > 0 and not force:
            logger.error("存在缺失的可执行文件，请先构建连接器或使用 --force 强制应用")
            return False

        if updates_needed == 0:
            logger.info("没有需要更新的连接器")
            return True

        logger.info(f"\n开始应用迁移，将更新 {updates_needed} 个连接器...")

        with self.db_service.get_session() as session:
            analysis = self.analyze_current_state()
            updated_count = 0

            for result in analysis:
                if result["needs_update"] and result["file_exists"]:
                    connector = (
                        session.query(Connector)
                        .filter_by(connector_id=result["connector_id"])
                        .first()
                    )

                    if connector:
                        # 更新config_data中的executable_path
                        if connector.config_data is None:
                            connector.config_data = {}

                        old_path = connector.config_data.get("executable_path")
                        connector.config_data["executable_path"] = result["new_path"]

                        # 明确标记config_data字段已修改（SQLAlchemy JSON字段需要）
                        from sqlalchemy.orm.attributes import flag_modified

                        flag_modified(connector, "config_data")

                        logger.info(
                            f"✅ 更新 {result['connector_id']}: {old_path} -> {result['new_path']}"
                        )
                        updated_count += 1

            try:
                session.commit()
                logger.info(
                    f"\n🎉 迁移成功完成! 更新了 {updated_count} 个连接器的可执行路径"
                )
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"❌ 迁移失败: {e}")
                return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="更新连接器executable_path配置")
    parser.add_argument(
        "--dry-run", action="store_true", help="预览更改，不实际修改数据库"
    )
    parser.add_argument("--apply", action="store_true", help="应用更改到数据库")
    parser.add_argument(
        "--force", action="store_true", help="强制应用更改（即使有缺失文件）"
    )

    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        parser.error("请指定 --dry-run 或 --apply")

    # 初始化数据库服务
    db_service = DatabaseService()
    migrator = ExecutablePathMigrator(db_service)

    try:
        if args.dry_run:
            logger.info("🔍 运行预览模式...")
            migrator.preview_changes()
        elif args.apply:
            logger.info("🚀 应用迁移...")
            success = migrator.apply_migration(force=args.force)
            sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"迁移过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
