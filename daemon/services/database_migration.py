#!/usr/bin/env python3
"""
数据库迁移管理器
Session V47 实现 - 版本化schema管理，向前向后兼容
"""

import hashlib
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DatabaseMigration:
    """数据库迁移管理器"""

    def __init__(self, db_path: str, migrations_dir: Optional[str] = None):
        """
        初始化迁移管理器

        Args:
            db_path: 数据库文件路径
            migrations_dir: 迁移文件目录，默认为同级migrations/
        """
        self.db_path = Path(db_path)
        self.migrations_dir = (
            Path(migrations_dir)
            if migrations_dir
            else self.db_path.parent / "migrations"
        )
        self.migrations_dir.mkdir(exist_ok=True)

        # 确保迁移表存在
        self._ensure_migration_table()

        logger.info("数据库迁移管理器初始化完成")
        logger.info(f"数据库路径: {self.db_path}")
        logger.info(f"迁移目录: {self.migrations_dir}")

    def _ensure_migration_table(self):
        """确保迁移记录表存在"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version VARCHAR(255) NOT NULL UNIQUE,
                    name VARCHAR(255) NOT NULL,
                    checksum VARCHAR(64) NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    execution_time_ms INTEGER,
                    success BOOLEAN NOT NULL DEFAULT 1
                )
            """
            )
            conn.commit()
            logger.debug("迁移记录表检查完成")

    def get_current_version(self) -> str:
        """获取当前数据库版本"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT version FROM schema_migrations
                WHERE success = 1
                ORDER BY applied_at DESC
                LIMIT 1
            """
            )
            result = cursor.fetchone()
            return result[0] if result else "0000_initial"

    def get_applied_migrations(self) -> List[Dict[str, str]]:
        """获取已应用的迁移列表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT version, name, applied_at, success, execution_time_ms
                FROM schema_migrations
                ORDER BY applied_at
            """
            )

            migrations = []
            for row in cursor.fetchall():
                migrations.append(
                    {
                        "version": row[0],
                        "name": row[1],
                        "applied_at": row[2],
                        "success": bool(row[3]),
                        "execution_time_ms": row[4],
                    }
                )
            return migrations

    def discover_migrations(self) -> List[Dict[str, str]]:
        """发现所有可用的迁移文件"""
        migrations = []

        for migration_file in sorted(self.migrations_dir.glob("*.sql")):
            # 解析文件名：0001_add_storage_strategy.sql
            parts = migration_file.stem.split("_", 1)
            if len(parts) != 2:
                logger.warning(f"跳过无效迁移文件名: {migration_file.name}")
                continue

            version, name = parts
            migrations.append(
                {
                    "version": version,
                    "name": name,
                    "file_path": str(migration_file),
                    "checksum": self._calculate_file_checksum(migration_file),
                }
            )

        return migrations

    def _calculate_file_checksum(self, file_path: Path) -> str:
        """计算文件校验和"""
        content = file_path.read_text(encoding="utf-8")
        return hashlib.sha256(content.encode()).hexdigest()

    def get_pending_migrations(self) -> List[Dict[str, str]]:
        """获取待应用的迁移"""
        all_migrations = self.discover_migrations()
        applied_migrations = self.get_applied_migrations()
        applied_versions = {m["version"] for m in applied_migrations if m["success"]}

        pending = []
        for migration in all_migrations:
            if migration["version"] not in applied_versions:
                pending.append(migration)

        return pending

    def apply_migration(self, migration: Dict[str, str]) -> bool:
        """应用单个迁移"""
        start_time = datetime.now()
        logger.info(f"开始应用迁移: {migration['version']}_{migration['name']}")

        try:
            # 读取迁移SQL
            migration_sql = Path(migration["file_path"]).read_text(encoding="utf-8")

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 执行迁移
                cursor.executescript(migration_sql)

                # 记录迁移应用
                execution_time = int(
                    (datetime.now() - start_time).total_seconds() * 1000
                )
                cursor.execute(
                    """
                    INSERT INTO schema_migrations (version, name, checksum, execution_time_ms)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        migration["version"],
                        migration["name"],
                        migration["checksum"],
                        execution_time,
                    ),
                )

                conn.commit()
                logger.info(
                    f"✅ 迁移 {migration['version']} 应用成功 ({execution_time}ms)"
                )
                return True

        except Exception as e:
            logger.error(f"❌ 迁移 {migration['version']} 应用失败: {e}")

            # 记录失败的迁移
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    execution_time = int(
                        (datetime.now() - start_time).total_seconds() * 1000
                    )
                    cursor.execute(
                        """
                        INSERT INTO schema_migrations (version, name, checksum, execution_time_ms, success)
                        VALUES (?, ?, ?, ?, 0)
                    """,
                        (
                            migration["version"],
                            migration["name"],
                            migration["checksum"],
                            execution_time,
                        ),
                    )
                    conn.commit()
            except Exception:
                pass  # 忽略记录失败的错误

            return False

    def migrate_to_latest(self) -> Tuple[bool, List[str]]:
        """迁移到最新版本"""
        pending_migrations = self.get_pending_migrations()

        if not pending_migrations:
            logger.info("数据库已是最新版本")
            return True, []

        logger.info(f"发现 {len(pending_migrations)} 个待应用的迁移")

        applied_migrations = []
        for migration in pending_migrations:
            if self.apply_migration(migration):
                applied_migrations.append(f"{migration['version']}_{migration['name']}")
            else:
                logger.error(f"迁移失败，停止后续迁移")
                return False, applied_migrations

        logger.info(f"所有迁移应用完成: {len(applied_migrations)} 个")
        return True, applied_migrations

    def create_migration_template(self, name: str) -> Path:
        """创建迁移文件模板"""
        # 生成版本号（基于时间戳）
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        version = f"{timestamp}"

        # 清理名称
        clean_name = name.replace(" ", "_").replace("-", "_").lower()
        filename = f"{version}_{clean_name}.sql"

        migration_file = self.migrations_dir / filename

        # 创建模板内容
        template = f"""-- Migration: {name}
-- Created: {datetime.now().isoformat()}
-- Version: {version}

-- Add your migration SQL here
-- Example:
-- ALTER TABLE data_items ADD COLUMN new_field VARCHAR(255);

-- Remember to test your migration before applying!
"""

        migration_file.write_text(template, encoding="utf-8")
        logger.info(f"迁移模板已创建: {migration_file}")

        return migration_file

    def validate_migrations(self) -> Tuple[bool, List[str]]:
        """验证迁移完整性"""
        issues = []

        # 检查迁移文件是否存在
        all_migrations = self.discover_migrations()
        applied_migrations = self.get_applied_migrations()

        for applied in applied_migrations:
            if not applied["success"]:
                continue

            # 查找对应的迁移文件
            found = False
            for migration in all_migrations:
                if migration["version"] == applied["version"]:
                    # 检查校验和是否匹配
                    if migration["checksum"] != applied.get("checksum"):
                        issues.append(f"迁移 {applied['version']} 校验和不匹配")
                    found = True
                    break

            if not found:
                issues.append(f"迁移 {applied['version']} 对应的文件不存在")

        if issues:
            logger.warning(f"发现迁移验证问题: {len(issues)} 个")
            for issue in issues:
                logger.warning(f"  - {issue}")
            return False, issues
        else:
            logger.info("迁移验证通过")
            return True, []

    def get_migration_status(self) -> Dict[str, any]:
        """获取迁移状态报告"""
        current_version = self.get_current_version()
        pending_migrations = self.get_pending_migrations()
        applied_migrations = self.get_applied_migrations()

        return {
            "current_version": current_version,
            "pending_count": len(pending_migrations),
            "applied_count": len([m for m in applied_migrations if m["success"]]),
            "failed_count": len([m for m in applied_migrations if not m["success"]]),
            "pending_migrations": [
                f"{m['version']}_{m['name']}" for m in pending_migrations
            ],
            "last_migration": applied_migrations[-1] if applied_migrations else None,
        }


# 命令行工具
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python database_migration.py <command> [args...]")
        print("Commands:")
        print("  status - 显示迁移状态")
        print("  migrate - 迁移到最新版本")
        print("  create <name> - 创建迁移模板")
        print("  validate - 验证迁移完整性")
        sys.exit(1)

    # 使用默认数据库路径
    db_path = Path.home() / ".linch-mind" / "db" / "linch_mind.db"
    migration_manager = DatabaseMigration(str(db_path))

    command = sys.argv[1]

    if command == "status":
        status = migration_manager.get_migration_status()
        print(f"Current Version: {status['current_version']}")
        print(
            f"Applied: {status['applied_count']}, Pending: {status['pending_count']}, Failed: {status['failed_count']}"
        )

        if status["pending_migrations"]:
            print("Pending migrations:")
            for migration in status["pending_migrations"]:
                print(f"  - {migration}")

    elif command == "migrate":
        success, applied = migration_manager.migrate_to_latest()
        if success:
            print(f"Migration completed successfully. Applied: {len(applied)}")
        else:
            print("Migration failed")
            sys.exit(1)

    elif command == "create":
        if len(sys.argv) < 3:
            print("Usage: python database_migration.py create <migration_name>")
            sys.exit(1)

        name = " ".join(sys.argv[2:])
        template_file = migration_manager.create_migration_template(name)
        print(f"Migration template created: {template_file}")

    elif command == "validate":
        valid, issues = migration_manager.validate_migrations()
        if valid:
            print("All migrations are valid")
        else:
            print("Migration validation failed:")
            for issue in issues:
                print(f"  - {issue}")
            sys.exit(1)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
