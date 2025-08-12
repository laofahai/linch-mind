#!/usr/bin/env python3
"""
配置文件格式迁移脚本
将JSON、YAML配置文件自动转换为TOML格式
"""

import argparse
import logging
import shutil
import sys
from pathlib import Path
from typing import List

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config_loader import ConfigLoader, ConfigWriter

logger = logging.getLogger(__name__)


class ConfigMigrator:
    """配置文件迁移器"""

    def __init__(self, backup: bool = True, dry_run: bool = False):
        self.backup = backup
        self.dry_run = dry_run
        self.migrated_files: List[Path] = []

    def migrate_file(self, source_path: Path, target_path: Path = None) -> bool:
        """迁移单个配置文件到TOML格式

        Args:
            source_path: 源配置文件路径
            target_path: 目标TOML文件路径（可选，默认同名.toml）

        Returns:
            迁移是否成功
        """
        if not source_path.exists():
            logger.error(f"源文件不存在: {source_path}")
            return False

        # 如果已经是TOML格式，跳过
        if source_path.suffix.lower() == ".toml":
            logger.info(f"跳过TOML文件: {source_path}")
            return True

        # 确定目标路径
        if target_path is None:
            target_path = source_path.with_suffix(".toml")

        logger.info(f"迁移 {source_path} -> {target_path}")

        if self.dry_run:
            logger.info(f"[DRY-RUN] 将迁移: {source_path} -> {target_path}")
            return True

        try:
            # 加载源配置
            config_data = ConfigLoader.load_config(source_path)

            # 备份原文件
            if self.backup and not self.dry_run:
                backup_path = source_path.with_suffix(f"{source_path.suffix}.backup")
                shutil.copy2(source_path, backup_path)
                logger.info(f"已备份到: {backup_path}")

            # 保存为TOML格式
            ConfigWriter.save_config(config_data, target_path)

            # 添加迁移注释
            self._add_migration_header(target_path, source_path)

            self.migrated_files.append(target_path)
            logger.info(f"✅ 迁移成功: {target_path}")
            return True

        except Exception as e:
            logger.error(f"迁移失败 {source_path}: {e}")
            return False

    def _add_migration_header(self, toml_path: Path, source_path: Path):
        """为迁移后的TOML文件添加注释头"""
        content = toml_path.read_text(encoding="utf-8")

        header = f"""# 此文件由配置迁移脚本自动生成
# 源文件: {source_path}
# 迁移时间: {__import__('datetime').datetime.now().isoformat()}
# TOML格式支持注释和更好的可读性

"""

        toml_path.write_text(header + content, encoding="utf-8")

    def migrate_directory(self, directory: Path, recursive: bool = True) -> int:
        """迁移目录中的所有配置文件

        Args:
            directory: 要迁移的目录
            recursive: 是否递归子目录

        Returns:
            成功迁移的文件数量
        """
        if not directory.exists():
            logger.error(f"目录不存在: {directory}")
            return 0

        success_count = 0
        config_extensions = [".json", ".yaml", ".yml"]

        # 获取配置文件列表
        pattern = "**/*" if recursive else "*"
        for file_path in directory.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in config_extensions:

                if self.migrate_file(file_path):
                    success_count += 1

        return success_count

    def migrate_connector_configs(self, connectors_dir: Path = None) -> int:
        """专门迁移连接器配置文件

        Args:
            connectors_dir: 连接器目录路径

        Returns:
            成功迁移的连接器配置数量
        """
        if connectors_dir is None:
            # 查找连接器目录
            possible_dirs = [
                Path("connectors"),
                Path("../connectors"),
                Path(__file__).parent.parent.parent / "connectors",
            ]

            connectors_dir = None
            for dir_path in possible_dirs:
                if dir_path.exists():
                    connectors_dir = dir_path
                    break

            if not connectors_dir:
                logger.error("未找到连接器目录")
                return 0

        logger.info(f"迁移连接器配置: {connectors_dir}")

        success_count = 0

        # 查找所有connector.json或connector.yaml文件
        for config_file in connectors_dir.rglob("connector.json"):
            if self.migrate_file(config_file):
                success_count += 1

        for config_file in connectors_dir.rglob("connector.yaml"):
            if self.migrate_file(config_file):
                success_count += 1

        return success_count


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="配置文件格式迁移工具 - 将JSON/YAML转换为TOML"
    )

    parser.add_argument("path", nargs="?", help="要迁移的文件或目录路径")

    parser.add_argument("--connectors", action="store_true", help="迁移连接器配置文件")

    parser.add_argument("--no-backup", action="store_true", help="不备份原文件")

    parser.add_argument(
        "--dry-run", action="store_true", help="演练模式，不实际执行迁移"
    )

    parser.add_argument("--recursive", "-r", action="store_true", help="递归处理子目录")

    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    # 配置日志
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    # 创建迁移器
    migrator = ConfigMigrator(backup=not args.no_backup, dry_run=args.dry_run)

    success_count = 0

    try:
        if args.connectors:
            # 迁移连接器配置
            success_count = migrator.migrate_connector_configs()

        elif args.path:
            path = Path(args.path)

            if path.is_file():
                # 迁移单个文件
                if migrator.migrate_file(path):
                    success_count = 1
            elif path.is_dir():
                # 迁移目录
                success_count = migrator.migrate_directory(path, args.recursive)
            else:
                logger.error(f"路径不存在: {path}")
                return 1
        else:
            # 默认迁移当前项目的配置
            logger.info("自动检测并迁移项目配置...")

            # 迁移daemon配置
            daemon_config_dir = Path("config")
            if daemon_config_dir.exists():
                success_count += migrator.migrate_directory(daemon_config_dir)

            # 迁移连接器配置
            success_count += migrator.migrate_connector_configs()

        # 显示结果
        if args.dry_run:
            logger.info(f"[DRY-RUN] 将迁移 {success_count} 个配置文件")
        else:
            logger.info(f"成功迁移 {success_count} 个配置文件到TOML格式")

        if migrator.migrated_files:
            logger.info("迁移的文件:")
            for file_path in migrator.migrated_files:
                logger.info(f"  - {file_path}")

        return 0

    except KeyboardInterrupt:
        logger.info("用户取消迁移")
        return 1
    except Exception as e:
        logger.error(f"迁移过程出错: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
