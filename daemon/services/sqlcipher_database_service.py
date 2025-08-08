#!/usr/bin/env python3
"""
SQLCipher加密数据库服务
实现基于安全架构设计的加密数据存储
"""

import base64
import hashlib
import json
import logging
import platform
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from models.database_models import (
    AIConversation,
    Base,
    EntityMetadata,
    EntityRelationship,
    UserBehavior,
)

logger = logging.getLogger(__name__)


class SQLCipherDatabaseService:
    """SQLCipher加密数据库服务"""

    def __init__(self, db_path: str, master_password: str):
        self.db_path = db_path
        self.master_password = master_password
        self.engine = None
        self.session_factory = None
        self._initialized = False

    def initialize_database(self):
        """初始化SQLCipher加密数据库"""
        try:
            # 确保数据库目录存在
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

            # 生成设备指纹
            device_fingerprint = self._get_device_fingerprint()

            # 派生数据库密钥
            db_key = self._derive_database_key(self.master_password, device_fingerprint)

            # 创建SQLCipher引擎
            connection_string = f"sqlite+pysqlcipher://:{db_key}@/{self.db_path}"

            self.engine = create_engine(
                connection_string,
                connect_args={
                    "check_same_thread": False,  # SQLite特定设置
                },
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False,  # 生产环境关闭SQL日志
            )

            # 设置SQLCipher参数
            self._configure_sqlcipher()

            # 创建所有表
            Base.metadata.create_all(self.engine)

            # 应用性能优化
            self._optimize_database_performance()

            # 创建Session工厂
            self.session_factory = sessionmaker(bind=self.engine)

            self._initialized = True
            logger.info("SQLCipher数据库初始化完成")

        except Exception as e:
            logger.error(f"SQLCipher数据库初始化失败: {e}")
            raise

    def _configure_sqlcipher(self):
        """配置SQLCipher加密参数"""
        with self.engine.connect() as conn:
            # 设置SQLCipher配置
            conn.execute(text("PRAGMA cipher = 'aes-256-gcm'"))  # AES-256-GCM认证加密
            conn.execute(text("PRAGMA kdf_iter = 256000"))  # OWASP推荐的PBKDF2迭代次数
            conn.execute(text("PRAGMA cipher_page_size = 4096"))  # 优化SSD性能
            conn.execute(
                text("PRAGMA cipher_memory_security = ON")
            )  # 防止内存中密钥泄露
            conn.execute(text("PRAGMA cipher_use_hmac = ON"))  # 数据完整性验证

    def _derive_database_key(self, password: str, device_id: str) -> str:
        """派生数据库加密密钥"""
        key_material = f"{password}:{device_id}:linch-mind-db-v3"
        derived_key = hashlib.pbkdf2_hmac(
            "sha256",
            key_material.encode("utf-8"),
            b"linch-mind-salt-v3",
            100000,  # 足够的迭代次数，平衡安全性和性能
        )
        return base64.urlsafe_b64encode(derived_key).decode("utf-8")

    def _get_device_fingerprint(self) -> str:
        """生成设备指纹 (防止密码被盗用)"""
        # 基于硬件和系统特征生成稳定的设备ID
        machine_info = {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "mac_address": ":".join(
                [
                    "{:02x}".format((uuid.getnode() >> i) & 0xFF)
                    for i in range(0, 8 * 6, 8)
                ][::-1]
            ),
        }

        fingerprint_data = json.dumps(machine_info, sort_keys=True)
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]

    def _optimize_database_performance(self):
        """优化SQLCipher性能"""
        try:
            with self.engine.connect() as conn:
                # 缓存设置
                conn.execute(text("PRAGMA cache_size = -64000"))  # 64MB缓存

                # WAL模式 - 提升并发性能
                conn.execute(text("PRAGMA journal_mode = WAL"))

                # 同步模式优化
                conn.execute(text("PRAGMA synchronous = NORMAL"))

                # 临时存储优化
                conn.execute(text("PRAGMA temp_store = MEMORY"))

                # 内存映射
                conn.execute(text("PRAGMA mmap_size = 268435456"))  # 256MB

                # 自动分析
                conn.execute(text("PRAGMA optimize"))

            # 创建性能索引
            self._create_performance_indexes()

        except Exception as e:
            logger.warning(f"数据库性能优化失败: {e}")

    def _create_performance_indexes(self):
        """创建查询性能索引"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_entity_type_name ON entity_metadata(entity_type, name)",
            "CREATE INDEX IF NOT EXISTS idx_entity_updated ON entity_metadata(updated_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_entity_access_count ON entity_metadata(access_count DESC)",
            "CREATE INDEX IF NOT EXISTS idx_behavior_timestamp ON user_behaviors(timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_behavior_session ON user_behaviors(session_id, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_behavior_entity ON user_behaviors(target_entity)",
            "CREATE INDEX IF NOT EXISTS idx_relationship_source ON entity_relationships(source_entity)",
            "CREATE INDEX IF NOT EXISTS idx_relationship_target ON entity_relationships(target_entity)",
            "CREATE INDEX IF NOT EXISTS idx_relationship_type ON entity_relationships(relationship_type)",
            "CREATE INDEX IF NOT EXISTS idx_conversation_session ON ai_conversations(session_id, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_conversation_timestamp ON ai_conversations(timestamp DESC)",
        ]

        with self.engine.connect() as conn:
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                except Exception as e:
                    logger.warning(f"创建索引失败: {e}")

    def get_session(self) -> Session:
        """获取数据库会话"""
        if not self._initialized:
            raise RuntimeError("数据库未初始化")
        return self.session_factory()

    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            session = self.get_session()
            session.execute(text("SELECT 1"))
            session.close()
            return True
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False

    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            session = self.get_session()

            # 基础统计
            entity_count = session.query(EntityMetadata).count()
            relationship_count = session.query(EntityRelationship).count()
            behavior_count = session.query(UserBehavior).count()
            conversation_count = session.query(AIConversation).count()

            # 数据库文件大小
            db_file = Path(self.db_path)
            file_size_mb = (
                db_file.stat().st_size / (1024 * 1024) if db_file.exists() else 0
            )

            session.close()

            return {
                "database_path": self.db_path,
                "file_size_mb": round(file_size_mb, 2),
                "entities": entity_count,
                "relationships": relationship_count,
                "behaviors": behavior_count,
                "conversations": conversation_count,
                "total_records": entity_count
                + relationship_count
                + behavior_count
                + conversation_count,
                "encrypted": True,
                "cipher": "AES-256-GCM",
            }

        except Exception as e:
            logger.error(f"获取数据库统计失败: {e}")
            return {"error": str(e)}

    def backup_to_file(self, backup_path: str) -> bool:
        """备份数据库到文件"""
        try:
            backup_file = Path(backup_path)
            backup_file.parent.mkdir(parents=True, exist_ok=True)

            # 使用SQLite的VACUUM INTO命令创建备份
            with self.engine.connect() as conn:
                conn.execute(text(f"VACUUM INTO '{backup_path}'"))

            logger.info(f"数据库备份完成: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"数据库备份失败: {e}")
            return False

    def close(self):
        """关闭数据库连接"""
        try:
            if self.engine:
                self.engine.dispose()
                self._initialized = False
                logger.info("SQLCipher数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {e}")


# 全局数据库服务实例
_sqlcipher_service: Optional[SQLCipherDatabaseService] = None


def initialize_sqlcipher_service(
    db_path: str, master_password: str
) -> SQLCipherDatabaseService:
    """初始化SQLCipher服务"""
    global _sqlcipher_service
    if _sqlcipher_service is None:
        _sqlcipher_service = SQLCipherDatabaseService(db_path, master_password)
        _sqlcipher_service.initialize_database()
    return _sqlcipher_service


def get_sqlcipher_service() -> Optional[SQLCipherDatabaseService]:
    """获取SQLCipher服务实例"""
    return _sqlcipher_service


def cleanup_sqlcipher_service():
    """清理SQLCipher服务"""
    global _sqlcipher_service
    if _sqlcipher_service:
        _sqlcipher_service.close()
        _sqlcipher_service = None
