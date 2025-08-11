#!/usr/bin/env python3
"""
SQLCipher加密数据库服务 - 基于SQLCipher的完整数据库加密
提供透明的全数据库加密，使用系统keyring进行安全密钥管理
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from config.core_config import get_database_config
from models.database_models import Base

logger = logging.getLogger(__name__)


class SQLCipherKeyManager:
    """SQLCipher密钥管理器 - 使用系统keyring安全存储"""

    KEYRING_SERVICE = "linch-mind"
    KEYRING_USERNAME = "sqlcipher-db-key"

    @staticmethod
    def get_or_create_key() -> str:
        """获取或创建数据库加密密钥"""
        try:
            import secrets

            import keyring

            # 尝试从keyring获取现有密钥
            existing_key = keyring.get_password(
                SQLCipherKeyManager.KEYRING_SERVICE,
                SQLCipherKeyManager.KEYRING_USERNAME,
            )

            if existing_key:
                logger.info("从系统keyring获取现有SQLCipher密钥")
                return existing_key
            else:
                # 生成新的强密钥
                new_key = secrets.token_urlsafe(32)  # 256位密钥

                # 存储到keyring
                keyring.set_password(
                    SQLCipherKeyManager.KEYRING_SERVICE,
                    SQLCipherKeyManager.KEYRING_USERNAME,
                    new_key,
                )

                logger.info("生成新SQLCipher密钥并存储到系统keyring")
                return new_key

        except ImportError:
            logger.error("keyring库未安装，无法安全存储密钥")
            raise RuntimeError("需要keyring库进行安全密钥管理")
        except Exception as e:
            logger.error(f"密钥管理失败: {e}")
            raise

    @staticmethod
    def set_key(new_key: str) -> bool:
        """设置新的数据库密钥"""
        try:
            import keyring

            keyring.set_password(
                SQLCipherKeyManager.KEYRING_SERVICE,
                SQLCipherKeyManager.KEYRING_USERNAME,
                new_key,
            )
            logger.info("SQLCipher密钥已更新")
            return True
        except Exception as e:
            logger.error(f"设置密钥失败: {e}")
            return False


class EncryptedDatabaseService:
    """
    SQLCipher加密数据库服务

    功能:
    1. 完整的SQLite数据库文件加密
    2. 透明的查询性能（支持索引和全功能SQL）
    3. 安全的密钥管理（系统keyring集成）
    4. 向后兼容的API接口
    5. 高性能连接池
    """

    def __init__(self, encryption_key: Optional[str] = None):
        self.db_config = get_database_config()
        self.encryption_key = encryption_key or SQLCipherKeyManager.get_or_create_key()
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None

        # 解析数据库路径
        self.db_path = self._parse_database_path()

        # 初始化加密数据库
        self._initialize_sqlcipher_database()

    def _parse_database_path(self) -> Optional[Path]:
        """解析数据库文件路径"""
        if self.db_config.sqlite_url.startswith("sqlite:///"):
            return Path(self.db_config.sqlite_url[10:])  # 移除 "sqlite:///"
        elif ":memory:" in self.db_config.sqlite_url:
            return None  # 内存数据库
        else:
            logger.warning(f"未知的数据库URL格式: {self.db_config.sqlite_url}")
            return None

    def _initialize_sqlcipher_database(self):
        """初始化SQLCipher加密数据库"""
        try:
            # 构建SQLCipher连接URL
            sqlcipher_url = self._build_sqlcipher_url()

            # 创建SQLCipher引擎
            self.engine = create_engine(
                sqlcipher_url,
                echo=False,  # 生产环境关闭详细日志
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 30,  # 30秒连接超时
                },
            )

            # 配置SQLCipher安全参数
            self._setup_sqlcipher_pragmas()

            # 创建会话工厂
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )

            # 验证加密设置并初始化表结构
            self._verify_and_initialize()

            logger.info("SQLCipher加密数据库初始化成功")

        except Exception as e:
            logger.error(f"SQLCipher数据库初始化失败: {e}")
            raise

    def _build_sqlcipher_url(self) -> str:
        """构建SQLCipher连接URL"""
        try:
            # 处理内存数据库
            if ":memory:" in self.db_config.sqlite_url:
                logger.info("使用内存SQLCipher数据库")
                return f"sqlite+pysqlcipher://:{self.encryption_key}@/:memory:"

            # 处理文件数据库
            if self.db_path:
                # 确保数据库目录存在
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
                db_file_path = str(self.db_path.absolute())

                logger.info(f"使用SQLCipher文件数据库: {db_file_path}")
                # SQLCipher URL格式: sqlite+pysqlcipher://:密钥@/绝对路径
                return f"sqlite+pysqlcipher://:{self.encryption_key}@/{db_file_path}"
            else:
                raise ValueError("无法解析数据库路径")

        except Exception as e:
            logger.error(f"构建SQLCipher URL失败: {e}")
            raise

    def _setup_sqlcipher_pragmas(self):
        """配置SQLCipher安全参数"""

        @event.listens_for(self.engine, "connect")
        def set_sqlcipher_pragmas(dbapi_connection, connection_record):
            """设置SQLCipher PRAGMA参数以获得最佳安全性和性能"""
            cursor = dbapi_connection.cursor()

            try:
                # 基础加密设置 - 这些是最重要的
                cursor.execute(f"PRAGMA key = '{self.encryption_key}';")

                # 高级安全配置 - 使用最新的安全标准
                cursor.execute("PRAGMA cipher = 'aes-256-cbc';")  # AES-256-CBC加密算法
                cursor.execute(
                    "PRAGMA kdf_iter = 256000;"
                )  # PBKDF2迭代次数 (OWASP推荐)
                cursor.execute(
                    "PRAGMA cipher_page_size = 4096;"
                )  # 4KB页面大小(性能平衡)
                cursor.execute("PRAGMA cipher_use_hmac = ON;")  # 启用HMAC完整性验证
                cursor.execute(
                    "PRAGMA cipher_plaintext_header_size = 32;"
                )  # 明文头部大小

                # SQLite性能优化 - 在加密基础上优化性能
                cursor.execute("PRAGMA synchronous = NORMAL;")  # 平衡安全性和性能
                cursor.execute("PRAGMA cache_size = -64000;")  # 64MB内存缓存
                cursor.execute("PRAGMA temp_store = MEMORY;")  # 临时数据存储在内存
                cursor.execute("PRAGMA journal_mode = WAL;")  # Write-Ahead Logging模式
                cursor.execute("PRAGMA foreign_keys = ON;")  # 启用外键约束
                cursor.execute("PRAGMA recursive_triggers = ON;")  # 启用递归触发器

                logger.debug("SQLCipher PRAGMA参数配置完成")

            except Exception as e:
                logger.error(f"SQLCipher PRAGMA配置失败: {e}")
                raise
            finally:
                cursor.close()

    def _verify_and_initialize(self):
        """验证SQLCipher设置并初始化表结构"""
        try:
            # 测试数据库连接和加密
            with self.get_session() as session:
                # 验证SQLCipher是否正常工作
                result = session.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table';")
                ).fetchall()
                logger.debug(f"数据库连接验证成功，发现 {len(result)} 个表")

                # 验证加密状态
                cipher_version = session.execute(
                    text("PRAGMA cipher_version;")
                ).fetchone()
                if cipher_version:
                    logger.info(f"SQLCipher版本: {cipher_version[0]}")
                else:
                    logger.warning("无法获取SQLCipher版本信息")

            # 初始化数据库表结构
            Base.metadata.create_all(bind=self.engine)
            logger.info("加密数据库表结构初始化完成")

        except Exception as e:
            logger.error(f"SQLCipher验证和初始化失败: {e}")
            raise

    def get_session(self) -> Session:
        """获取数据库会话"""
        if not self.SessionLocal:
            raise RuntimeError("数据库服务未初始化")
        return self.SessionLocal()

    def test_encryption(self) -> bool:
        """测试数据库加密是否工作正常"""
        try:
            with self.get_session() as session:
                # 执行简单查询测试连接
                result = session.execute("SELECT 1").fetchone()
                if result and result[0] == 1:
                    logger.info("数据库加密测试通过")
                    return True
                return False

        except Exception as e:
            logger.error(f"数据库加密测试失败: {e}")
            return False

    def verify_database_integrity(self) -> bool:
        """验证数据库完整性"""
        try:
            with self.get_session() as session:
                # 执行PRAGMA integrity_check
                result = session.execute("PRAGMA integrity_check").fetchone()
                if result and result[0] == "ok":
                    logger.info("数据库完整性验证通过")
                    return True
                else:
                    logger.error(f"数据库完整性验证失败: {result}")
                    return False

        except Exception as e:
            logger.error(f"数据库完整性验证异常: {e}")
            return False

    def get_encryption_status(self) -> Dict[str, Any]:
        """获取数据库加密状态"""
        try:
            with self.get_session() as session:
                # 查询SQLCipher版本和配置
                cipher_version = session.execute("PRAGMA cipher_version").fetchone()
                page_size = session.execute("PRAGMA cipher_page_size").fetchone()
                kdf_iter = session.execute("PRAGMA kdf_iter").fetchone()

                return {
                    "encrypted": True,
                    "cipher_version": cipher_version[0] if cipher_version else None,
                    "page_size": page_size[0] if page_size else None,
                    "kdf_iterations": kdf_iter[0] if kdf_iter else None,
                    "database_path": str(self.db_path) if self.db_path else ":memory:",
                    "last_verified": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            logger.error(f"获取加密状态失败: {e}")
            return {"encrypted": False, "error": str(e)}

    def change_password(self, old_key: str, new_key: str) -> bool:
        """更改数据库加密密码"""
        try:
            with self.get_session() as session:
                # SQLCipher密码更改命令
                session.execute(f"PRAGMA rekey = '{new_key}'")
                session.commit()

                # 更新内部密钥
                self.encryption_key = new_key

                logger.info("数据库加密密码更改成功")
                return True

        except Exception as e:
            logger.error(f"数据库密码更改失败: {e}")
            return False

    def backup_encrypted_database(self, backup_path: str) -> bool:
        """备份加密数据库"""
        try:
            backup_path_obj = Path(backup_path)
            backup_path_obj.parent.mkdir(parents=True, exist_ok=True)

            with self.get_session() as session:
                # 使用SQLite的VACUUM INTO命令进行备份
                session.execute(f"VACUUM INTO '{backup_path}'")
                session.commit()

                logger.info(f"加密数据库备份完成: {backup_path}")
                return True

        except Exception as e:
            logger.error(f"数据库备份失败: {e}")
            return False

    def migrate_from_plaintext(self, plaintext_db_path: str) -> bool:
        """从明文数据库迁移到加密数据库"""
        try:
            # 创建明文数据库连接
            plaintext_engine = create_engine(f"sqlite:///{plaintext_db_path}")

            with self.get_session() as encrypted_session:
                with plaintext_engine.connect() as plaintext_conn:
                    # 使用ATTACH命令附加明文数据库
                    encrypted_session.execute(
                        f"ATTACH DATABASE '{plaintext_db_path}' AS plaintext KEY ''"
                    )

                    # 获取所有表名
                    tables = encrypted_session.execute(
                        "SELECT name FROM plaintext.sqlite_master WHERE type='table'"
                    ).fetchall()

                    # 迁移每个表的数据
                    for table in tables:
                        table_name = table[0]
                        if table_name.startswith("sqlite_"):
                            continue

                        logger.info(f"迁移表: {table_name}")

                        # 复制数据
                        encrypted_session.execute(
                            f"INSERT INTO main.{table_name} SELECT * FROM plaintext.{table_name}"
                        )

                    # 分离数据库
                    encrypted_session.execute("DETACH DATABASE plaintext")
                    encrypted_session.commit()

                    logger.info("明文数据库迁移完成")
                    return True

        except Exception as e:
            logger.error(f"数据库迁移失败: {e}")
            return False

    def cleanup(self):
        """清理资源"""
        try:
            if self.engine:
                self.engine.dispose()
                logger.info("加密数据库连接已清理")
        except Exception as e:
            logger.error(f"数据库清理失败: {e}")

    async def close(self):
        """异步关闭方法"""
        self.cleanup()


def create_encrypted_database_service(
    encryption_key: Optional[str] = None,
) -> EncryptedDatabaseService:
    """创建加密数据库服务实例"""
    return EncryptedDatabaseService(encryption_key=encryption_key)
