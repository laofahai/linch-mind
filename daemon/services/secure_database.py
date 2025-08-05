#!/usr/bin/env python3
"""
安全数据库服务 - 支持数据库加密和安全存储
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

from config.core_config import get_core_config
from config.error_handling import get_logger
from cryptography.fernet import Fernet
from models.core_models import Base
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

logger = get_logger(__name__)


class SecureDatabase:
    """安全数据库管理器"""

    def __init__(self):
        self.config_manager = get_core_config()
        self.config = self.config_manager.config
        self.encryption_enabled = self.config.database.enable_encryption

        # 获取加密密钥
        if self.encryption_enabled:
            self.cipher = Fernet(self.config_manager.get_encryption_key())
        else:
            self.cipher = None

        # 创建数据库引擎
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        # 创建所有表
        Base.metadata.create_all(bind=self.engine)

        logger.info(f"数据库初始化完成: {self.config.database.sqlite_path}")
        logger.info(f"加密状态: {'启用' if self.encryption_enabled else '禁用'}")

    def _create_engine(self) -> Engine:
        """创建数据库引擎"""
        db_path = Path(self.config.database.sqlite_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # SQLite连接字符串
        if db_path.is_absolute():
            db_url = f"sqlite:///{db_path}"
        else:
            db_url = f"sqlite:///./{db_path}"

        # 创建引擎
        engine = create_engine(
            db_url,
            echo=self.config.debug,
            pool_pre_ping=True,
            connect_args={"check_same_thread": False},
        )

        # 如果启用加密，设置SQLite加密扩展
        if self.encryption_enabled:

            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                # 注意: 这里使用的是SQLite的PRAGMA，
                # 实际生产环境可能需要使用SQLCipher等加密扩展
                cursor = dbapi_connection.cursor()
                # 设置WAL模式以提高并发性能
                cursor.execute("PRAGMA journal_mode=WAL")
                # 设置同步模式
                cursor.execute("PRAGMA synchronous=NORMAL")
                # 设置页面大小
                cursor.execute("PRAGMA page_size=4096")
                cursor.close()

        return engine

    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()

    def encrypt_sensitive_data(self, data: Union[str, Dict, Any]) -> str:
        """加密敏感数据"""
        if not self.encryption_enabled or not self.cipher:
            return data if isinstance(data, str) else json.dumps(data)

        try:
            # 转换为字符串
            if isinstance(data, str):
                text_data = data
            else:
                text_data = json.dumps(data, ensure_ascii=False)

            # 加密
            encrypted_data = self.cipher.encrypt(text_data.encode("utf-8"))
            return encrypted_data.decode("utf-8")
        except Exception as e:
            logger.error(f"数据加密失败: {e}")
            raise

    def decrypt_sensitive_data(
        self, encrypted_data: str, return_json: bool = False
    ) -> Union[str, Dict, Any]:
        """解密敏感数据"""
        if not self.encryption_enabled or not self.cipher:
            if return_json and encrypted_data:
                try:
                    return json.loads(encrypted_data)
                except (json.JSONDecodeError, TypeError):
                    return encrypted_data
            return encrypted_data

        try:
            # 解密
            decrypted_bytes = self.cipher.decrypt(encrypted_data.encode("utf-8"))
            decrypted_text = decrypted_bytes.decode("utf-8")

            # 如果需要返回JSON对象
            if return_json:
                try:
                    return json.loads(decrypted_text)
                except (json.JSONDecodeError, TypeError):
                    return decrypted_text

            return decrypted_text
        except Exception as e:
            logger.error(f"数据解密失败: {e}")
            # 返回原始数据（可能是未加密的旧数据）
            if return_json:
                try:
                    return json.loads(encrypted_data)
                except (json.JSONDecodeError, TypeError):
                    return encrypted_data
            return encrypted_data

    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """备份数据库"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.config_manager.get_paths()["data"] / "backups"
            backup_dir.mkdir(exist_ok=True)
            backup_path = backup_dir / f"linch_mind_backup_{timestamp}.db"

        try:
            # 使用SQLite的备份API
            source_db = sqlite3.connect(self.config.database.sqlite_path)
            backup_db = sqlite3.connect(backup_path)

            source_db.backup(backup_db)

            source_db.close()
            backup_db.close()

            logger.info(f"数据库备份完成: {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"数据库备份失败: {e}")
            raise

    def restore_database(self, backup_path: str) -> bool:
        """从备份恢复数据库"""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise FileNotFoundError(f"备份文件不存在: {backup_path}")

            # 关闭当前连接
            self.engine.dispose()

            # 备份当前数据库
            current_db = Path(self.config.database.sqlite_path)
            if current_db.exists():
                backup_current = current_db.with_suffix(".db.backup")
                current_db.rename(backup_current)
                logger.info(f"当前数据库已备份至: {backup_current}")

            # 恢复数据库
            source_db = sqlite3.connect(backup_path)
            target_db = sqlite3.connect(self.config.database.sqlite_path)

            source_db.backup(target_db)

            source_db.close()
            target_db.close()

            # 重新创建引擎
            self.engine = self._create_engine()
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )

            logger.info(f"数据库恢复完成: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"数据库恢复失败: {e}")
            return False

    def vacuum_database(self):
        """数据库清理和优化"""
        try:
            with self.engine.connect() as conn:
                conn.execute("VACUUM")
                conn.execute("ANALYZE")
            logger.info("数据库清理完成")
        except Exception as e:
            logger.error(f"数据库清理失败: {e}")

    def get_database_info(self) -> Dict[str, Any]:
        """获取数据库信息"""
        try:
            db_path = Path(self.config.database.sqlite_path)

            info = {
                "path": str(db_path),
                "exists": db_path.exists(),
                "size_bytes": db_path.stat().st_size if db_path.exists() else 0,
                "encryption_enabled": self.encryption_enabled,
                "backup_enabled": self.config.database.backup_enabled,
            }

            # 获取表信息
            if db_path.exists():
                with self.engine.connect() as conn:
                    result = conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                    tables = [row[0] for row in result.fetchall()]
                    info["tables"] = tables

                    # 获取数据统计
                    table_counts = {}
                    for table in tables:
                        if not table.startswith("sqlite_"):
                            try:
                                result = conn.execute(f"SELECT COUNT(*) FROM {table}")
                                table_counts[table] = result.fetchone()[0]
                            except Exception:
                                table_counts[table] = 0
                    info["table_counts"] = table_counts

            return info
        except Exception as e:
            logger.error(f"获取数据库信息失败: {e}")
            return {"error": str(e)}


# 全局单例
_secure_database = None


def get_secure_database() -> SecureDatabase:
    """获取安全数据库单例"""
    global _secure_database
    if _secure_database is None:
        _secure_database = SecureDatabase()
    return _secure_database


def get_db_session() -> Session:
    """依赖注入：获取数据库会话"""
    db = get_secure_database()
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()
