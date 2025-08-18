#!/usr/bin/env python3
"""
统一数据库服务
整合DatabaseService、EncryptedDatabaseService和OptimizedConnectionPool
解决数据库层冗余问题
"""

import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from config.bootstrap_config import get_bootstrap_config
from models.database_models import Base, Connector

logger = logging.getLogger(__name__)


class UnifiedDatabaseService:
    """统一数据库服务
    
    特性:
    - 自动加密检测（生产环境使用SQLCipher）
    - 统一连接池管理
    - 环境感知配置
    - 单一API接口
    - 使用Bootstrap配置避免循环依赖
    """

    def __init__(self, db_path: Optional[str] = None, force_encryption: Optional[bool] = None):
        # 使用Bootstrap配置，避免循环依赖
        bootstrap = get_bootstrap_config()
        self.db_config = bootstrap.get_database_config()
        self.environment = bootstrap.get_environment()
        self.data_dir = bootstrap.get_data_dir()
        
        self._session_local = None
        self._engine = None

        # 确定是否使用加密
        self.use_encryption = self._should_use_encryption(force_encryption)
        
        # 初始化数据库
        self._initialize_database(db_path)

    def _should_use_encryption(self, force_encryption: Optional[bool]) -> bool:
        """确定是否应该使用加密"""
        if force_encryption is not None:
            return force_encryption
        
        # 根据环境自动决定（使用Bootstrap配置）
        return self.environment == "production" or self.db_config.use_encryption

    def _initialize_database(self, db_path: Optional[str] = None):
        """初始化数据库连接"""
        try:
            # 构建数据库URL
            database_url = self._build_database_url(db_path)
            
            # 创建引擎配置
            engine_config = self._build_engine_config()
            
            # 创建引擎
            self._engine = create_engine(database_url, **engine_config)
            
            # 如果使用加密，设置SQLCipher参数
            if self.use_encryption:
                self._setup_encryption_pragmas()
            else:
                self._setup_standard_pragmas()

            # 创建会话工厂
            self._session_local = sessionmaker(
                autocommit=False, 
                autoflush=False, 
                bind=self._engine
            )

            # 创建表结构
            Base.metadata.create_all(bind=self._engine)
            
            # 验证连接
            self._verify_connection()

            logger.info(f"统一数据库服务初始化完成 (加密: {self.use_encryption})")

        except Exception as e:
            logger.error(f"统一数据库服务初始化失败: {e}")
            raise

    def _build_database_url(self, db_path: Optional[str] = None) -> str:
        """构建数据库连接URL"""
        if db_path:
            if db_path == ":memory:":
                base_url = "sqlite:///:memory:"
            else:
                base_url = f"sqlite:///{db_path}"
        else:
            # 使用Bootstrap配置构建URL
            db_file = self.data_dir / "database" / self.db_config.sqlite_file
            db_file.parent.mkdir(parents=True, exist_ok=True)
            base_url = f"sqlite:///{db_file}"

        # 如果使用加密，修改URL
        if self.use_encryption:
            if base_url.startswith("sqlite:///"):
                # 替换为SQLCipher URL格式
                encryption_key = self._get_encryption_key()
                if base_url == "sqlite:///:memory:":
                    return f"sqlite+pysqlcipher://:{encryption_key}@/:memory:"
                else:
                    db_file_path = base_url.replace("sqlite:///", "")
                    return f"sqlite+pysqlcipher://:{encryption_key}@/{db_file_path}"
            
        return base_url

    def _get_encryption_key(self) -> str:
        """获取加密密钥"""
        try:
            import secrets
            import keyring

            service_name = "linch-mind"
            username = "unified-db-key"

            # 尝试从keyring获取现有密钥
            existing_key = keyring.get_password(service_name, username)
            
            if existing_key:
                return existing_key
            else:
                # 生成新密钥
                new_key = secrets.token_urlsafe(32)  # 256位密钥
                keyring.set_password(service_name, username, new_key)
                logger.info("生成新的数据库加密密钥")
                return new_key

        except ImportError:
            logger.error("keyring库未安装，无法安全存储密钥")
            raise RuntimeError("需要keyring库进行安全密钥管理")

    def _build_engine_config(self) -> Dict[str, Any]:
        """构建引擎配置"""
        config = {
            "echo": False,  # 禁用SQL日志输出，避免日志污染
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        }

        # 生产环境优化（SQLCipher不支持连接池参数）
        is_debug = (self.environment == "development")
        if not is_debug and not self.use_encryption:
            config.update({
                "pool_size": 20,
                "max_overflow": 30,
                "pool_timeout": 30,
            })

        # 加密数据库需要特殊连接参数
        if self.use_encryption:
            config["connect_args"] = {
                "check_same_thread": False,
                "timeout": 30,
            }

        return config

    def _setup_encryption_pragmas(self):
        """设置SQLCipher加密参数"""
        from sqlalchemy import event

        @event.listens_for(self._engine, "connect")
        def set_sqlcipher_pragmas(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            try:
                # 基础加密设置
                encryption_key = self._get_encryption_key()
                cursor.execute(f"PRAGMA key = '{encryption_key}';")

                # 高级安全配置
                cursor.execute("PRAGMA cipher = 'aes-256-cbc';")
                cursor.execute("PRAGMA kdf_iter = 256000;")
                cursor.execute("PRAGMA cipher_page_size = 4096;")
                cursor.execute("PRAGMA cipher_use_hmac = ON;")

                # 性能优化
                cursor.execute("PRAGMA synchronous = NORMAL;")
                cursor.execute("PRAGMA cache_size = -64000;")  # 64MB
                cursor.execute("PRAGMA temp_store = MEMORY;")
                cursor.execute("PRAGMA journal_mode = WAL;")
                cursor.execute("PRAGMA foreign_keys = ON;")

            except Exception as e:
                logger.error(f"SQLCipher PRAGMA配置失败: {e}")
                raise
            finally:
                cursor.close()

    def _setup_standard_pragmas(self):
        """设置标准SQLite优化参数"""
        from sqlalchemy import event

        @event.listens_for(self._engine, "connect")
        def set_sqlite_pragmas(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            try:
                # 性能优化设置
                cursor.execute("PRAGMA synchronous = NORMAL;")
                cursor.execute("PRAGMA cache_size = -64000;")  # 64MB
                cursor.execute("PRAGMA temp_store = MEMORY;")
                cursor.execute("PRAGMA journal_mode = WAL;")
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute("PRAGMA mmap_size = 268435456;")  # 256MB内存映射

            except Exception as e:
                logger.warning(f"SQLite PRAGMA配置失败: {e}")
            finally:
                cursor.close()

    def _verify_connection(self):
        """验证数据库连接"""
        try:
            with self.get_session() as session:
                result = session.execute(text("SELECT 1")).fetchone()
                if result and result[0] == 1:
                    logger.debug("数据库连接验证成功")
                else:
                    raise RuntimeError("数据库连接验证失败")

                # 如果使用加密，验证加密状态
                if self.use_encryption:
                    try:
                        cipher_version = session.execute(text("PRAGMA cipher_version;")).fetchone()
                        if cipher_version:
                            logger.info(f"SQLCipher版本: {cipher_version[0]}")
                        else:
                            logger.warning("无法获取SQLCipher版本信息")
                    except:
                        pass  # 加密验证失败不阻断启动

        except Exception as e:
            logger.error(f"数据库连接验证失败: {e}")
            raise

    @contextmanager
    def get_session(self):
        """获取数据库会话（上下文管理器）"""
        if not self._session_local:
            raise RuntimeError("数据库服务未初始化")
        
        session = self._session_local()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    # === 连接器管理方法 (兼容原DatabaseService接口) ===

    def register_connector(self, connector_info: Dict[str, Any]) -> bool:
        """注册连接器"""
        try:
            with self.get_session() as session:
                existing = (
                    session.query(Connector)
                    .filter(Connector.connector_id == connector_info["connector_id"])
                    .first()
                )

                if existing:
                    # 更新现有连接器
                    for key, value in connector_info.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                    logger.info(f"更新连接器: {connector_info['connector_id']}")
                else:
                    # 创建新连接器
                    connector = Connector(**connector_info)
                    session.add(connector)
                    logger.info(f"注册新连接器: {connector_info['connector_id']}")

                session.commit()
                return True

        except SQLAlchemyError as e:
            logger.error(f"注册连接器失败: {e}")
            return False

    def get_connectors(self) -> List[Connector]:
        """获取所有连接器"""
        try:
            with self.get_session() as session:
                return session.query(Connector).all()
        except SQLAlchemyError as e:
            logger.error(f"获取连接器列表失败: {e}")
            return []

    def get_connector(self, connector_id: str) -> Optional[Connector]:
        """根据ID获取连接器"""
        try:
            with self.get_session() as session:
                return (
                    session.query(Connector)
                    .filter(Connector.connector_id == connector_id)
                    .first()
                )
        except SQLAlchemyError as e:
            logger.error(f"获取连接器失败 [{connector_id}]: {e}")
            return None

    def update_connector_status(
        self, connector_id: str, status: str, process_id: Optional[int] = None
    ) -> bool:
        """更新连接器状态"""
        try:
            with self.get_session() as session:
                connector = (
                    session.query(Connector)
                    .filter(Connector.connector_id == connector_id)
                    .first()
                )

                if connector:
                    connector.status = status
                    if process_id is not None:
                        connector.process_id = process_id
                    connector.updated_at = datetime.utcnow()
                    session.commit()
                    logger.info(f"更新连接器状态: {connector_id} -> {status}")
                    return True
                else:
                    logger.warning(f"连接器不存在: {connector_id}")
                    return False

        except SQLAlchemyError as e:
            logger.error(f"更新连接器状态失败 [{connector_id}]: {e}")
            return False

    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            with self.get_session() as session:
                connectors_count = session.query(Connector).count()
                running_connectors_count = (
                    session.query(Connector)
                    .filter(Connector.status == "running")
                    .count()
                )

                # 获取数据库URL（用于统计）
                db_url = self._build_database_url()

                return {
                    "connectors_count": connectors_count,
                    "running_connectors_count": running_connectors_count,
                    "database_path": db_url,
                    "environment": self.environment,
                    "encrypted": self.use_encryption,
                    "encryption_type": "SQLCipher" if self.use_encryption else "none",
                }

        except SQLAlchemyError as e:
            logger.error(f"获取数据库统计失败: {e}")
            return {}

    def get_encryption_status(self) -> Dict[str, Any]:
        """获取加密状态信息"""
        try:
            if not self.use_encryption:
                return {
                    "encrypted": False,
                    "encryption_type": "none",
                    "database_path": self._build_database_url(),
                }

            with self.get_session() as session:
                try:
                    cipher_version = session.execute(text("PRAGMA cipher_version;")).fetchone()
                    page_size = session.execute(text("PRAGMA cipher_page_size;")).fetchone()
                    kdf_iter = session.execute(text("PRAGMA kdf_iter;")).fetchone()

                    return {
                        "encrypted": True,
                        "encryption_type": "SQLCipher",
                        "cipher_version": cipher_version[0] if cipher_version else None,
                        "page_size": page_size[0] if page_size else None,
                        "kdf_iterations": kdf_iter[0] if kdf_iter else None,
                        "database_path": self._build_database_url(),
                        "last_verified": datetime.utcnow().isoformat(),
                    }
                except:
                    return {
                        "encrypted": True,
                        "encryption_type": "SQLCipher",
                        "error": "无法获取加密参数",
                        "database_path": self._build_database_url(),
                    }

        except Exception as e:
            logger.error(f"获取加密状态失败: {e}")
            return {"encrypted": self.use_encryption, "error": str(e)}

    @property
    def engine(self):
        """获取数据库引擎（兼容性属性）"""
        return self._engine

    @property
    def SessionLocal(self):
        """获取SessionLocal（兼容性属性）"""
        return self._session_local

    async def initialize(self):
        """异步初始化方法（兼容接口）"""
        # 主要初始化已在__init__中完成
        logger.debug("统一数据库服务异步初始化完成")

    async def close(self):
        """异步关闭方法"""
        self.cleanup()

    def cleanup(self):
        """清理资源"""
        try:
            if self._engine:
                self._engine.dispose()
                logger.info("统一数据库连接已清理")
        except Exception as e:
            logger.error(f"数据库清理失败: {e}")

    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            with self.get_session() as session:
                result = session.execute(text("SELECT 1")).fetchone()
                return result is not None and result[0] == 1
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False

    def get_performance_info(self) -> Dict[str, Any]:
        """获取性能信息"""
        try:
            with self.get_session() as session:
                # 获取基本统计
                stats = {}

                # 数据库大小信息
                try:
                    page_count = session.execute(text("PRAGMA page_count;")).fetchone()[0]
                    page_size = session.execute(text("PRAGMA page_size;")).fetchone()[0]
                    stats.update({
                        "total_pages": page_count,
                        "page_size": page_size,
                        "database_size_mb": (page_count * page_size) / (1024 * 1024),
                    })
                except:
                    pass

                # 缓存信息
                try:
                    cache_size = session.execute(text("PRAGMA cache_size;")).fetchone()[0]
                    stats["cache_size"] = abs(cache_size)
                except:
                    pass

                return stats

        except Exception as e:
            logger.error(f"获取性能信息失败: {e}")
            return {}
    
    def get_environment_database_info(self) -> Dict[str, Any]:
        """获取环境数据库信息
        
        Returns:
            包含数据库配置信息的字典
        """
        import os
        
        # 获取数据库URL
        database_url = self.db_config.sqlite_url
        if not database_url:
            database_url = self._build_database_url()
        
        # 检查数据库文件是否存在
        database_exists = False
        if database_url and not database_url.endswith(":memory:"):
            db_path = database_url.replace("sqlite:///", "")
            database_exists = os.path.exists(db_path)
        
        return {
            "database_url": database_url,
            "use_encryption": self.use_encryption,
            "database_exists": database_exists,
            "environment": self.environment,
            "config_root": str(self.data_dir.parent),
        }


# 兼容性函数
def create_unified_database_service(
    db_path: Optional[str] = None, 
    force_encryption: Optional[bool] = None
) -> UnifiedDatabaseService:
    """创建统一数据库服务实例"""
    return UnifiedDatabaseService(db_path, force_encryption)