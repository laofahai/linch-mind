#!/usr/bin/env python3
"""
统一数据库服务 - 支持加密和明文数据库的统一接口
根据配置自动选择使用加密或明文数据库
"""

import logging
from typing import Any, Dict, List, Optional, Type, Union

from sqlalchemy.orm import Session

from config.core_config import get_database_config
from models.database_models import Base, Connector
from services.database_service import DatabaseService
from services.encrypted_database_service import EncryptedDatabaseService
from services.security.key_manager import KeyManager

logger = logging.getLogger(__name__)


class UnifiedDatabaseService:
    """
    统一数据库服务

    功能:
    1. 自动检测是否启用加密
    2. 提供统一的数据库操作接口
    3. 透明切换加密/明文模式
    4. 向后兼容现有代码
    """

    def __init__(self, db_path: Optional[str] = None, force_encryption: bool = False):
        self.db_config = get_database_config()
        self.key_manager = KeyManager()
        self.force_encryption = force_encryption

        # 实际数据库服务实例
        self._service: Union[DatabaseService, EncryptedDatabaseService] = None
        self._encryption_enabled = False

        self._initialize_service(db_path)

    def _initialize_service(self, db_path: Optional[str] = None):
        """初始化适当的数据库服务"""
        try:
            # 检查是否应该启用加密
            should_encrypt = self._should_enable_encryption()

            if should_encrypt:
                logger.info("初始化加密数据库服务")
                encryption_key = self._get_encryption_key()

                if encryption_key:
                    self._service = EncryptedDatabaseService(
                        encryption_key=encryption_key
                    )
                    self._encryption_enabled = True
                    logger.info("加密数据库服务初始化成功")
                else:
                    logger.warning("无法获取加密密钥，回退到明文数据库")
                    self._service = DatabaseService(db_path=db_path)
                    self._encryption_enabled = False
            else:
                logger.info("初始化明文数据库服务")
                self._service = DatabaseService(db_path=db_path)
                self._encryption_enabled = False

        except Exception as e:
            logger.error(f"数据库服务初始化失败: {e}")
            # 回退到明文数据库
            logger.info("回退到明文数据库服务")
            self._service = DatabaseService(db_path=db_path)
            self._encryption_enabled = False

    def _should_enable_encryption(self) -> bool:
        """判断是否应该启用数据库加密"""
        if self.force_encryption:
            return True

        # 检查是否存在密钥配置
        if self.key_manager.has_existing_key():
            logger.info("检测到现有加密密钥配置")
            return True

        # 检查环境变量
        import os

        if os.getenv("LINCH_MIND_ENCRYPT_DB", "").lower() in ("true", "1", "yes"):
            logger.info("通过环境变量启用数据库加密")
            return True

        # 默认不启用加密（向后兼容）
        return False

    def _get_encryption_key(self) -> Optional[str]:
        """获取数据库加密密钥"""
        try:
            # 尝试从环境变量获取密码
            import os

            user_password = os.getenv("LINCH_MIND_DB_PASSWORD")

            if user_password:
                keys = self.key_manager.derive_key_from_password(user_password)
                if keys:
                    return keys.encryption_key

            # 如果没有密码，使用自动生成的密钥（开发模式）
            if not self.key_manager.has_existing_key():
                logger.info("生成新的自动加密密钥")
                keys = self.key_manager.generate_master_key()
                return keys.encryption_key

            logger.warning("需要密码来解锁现有加密数据库")
            return None

        except Exception as e:
            logger.error(f"获取加密密钥失败: {e}")
            return None

    @property
    def is_encrypted(self) -> bool:
        """返回数据库是否加密"""
        return self._encryption_enabled

    def get_session(self) -> Session:
        """获取数据库会话"""
        return self._service.get_session()

    def register_connector(self, connector_info: Dict[str, Any]) -> bool:
        """注册连接器"""
        return self._service.register_connector(connector_info)

    def get_connectors(self) -> List[Connector]:
        """获取所有连接器"""
        return self._service.get_connectors()

    def get_connector(self, connector_id: str) -> Optional[Connector]:
        """根据ID获取连接器"""
        return self._service.get_connector(connector_id)

    def update_connector_status(
        self, connector_id: str, status: str, process_id: Optional[int] = None
    ) -> bool:
        """更新连接器状态"""
        return self._service.update_connector_status(connector_id, status, process_id)

    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        stats = self._service.get_database_stats()
        stats["encryption_enabled"] = self._encryption_enabled

        if self._encryption_enabled:
            # 添加加密状态信息
            if hasattr(self._service, "get_encryption_status"):
                encryption_status = self._service.get_encryption_status()
                stats.update(encryption_status)

        return stats

    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            if self._encryption_enabled and hasattr(self._service, "test_encryption"):
                return self._service.test_encryption()
            else:
                # 对于明文数据库，执行简单查询测试
                with self.get_session() as session:
                    result = session.execute("SELECT 1").fetchone()
                    return result and result[0] == 1
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False

    def get_security_info(self) -> Dict[str, Any]:
        """获取数据库安全信息"""
        info = {
            "encryption_enabled": self._encryption_enabled,
            "service_type": type(self._service).__name__,
        }

        if self._encryption_enabled:
            # 获取密钥管理器的安全信息
            key_info = self.key_manager.get_security_info()
            info.update(key_info)

            # 获取数据库加密状态
            if hasattr(self._service, "get_encryption_status"):
                encryption_status = self._service.get_encryption_status()
                info.update(encryption_status)

        return info

    async def initialize(self):
        """异步初始化"""
        if hasattr(self._service, "initialize"):
            await self._service.initialize()

    async def close(self):
        """异步关闭"""
        if hasattr(self._service, "close"):
            await self._service.close()
        else:
            self.cleanup()

    def cleanup(self):
        """清理资源"""
        if hasattr(self._service, "cleanup"):
            self._service.cleanup()


# 向后兼容的工厂函数
def create_database_service(db_path: Optional[str] = None) -> UnifiedDatabaseService:
    """创建统一数据库服务实例"""
    return UnifiedDatabaseService(db_path=db_path)


def create_encrypted_database_service(
    encryption_key: Optional[str] = None,
) -> UnifiedDatabaseService:
    """强制创建加密数据库服务实例"""
    service = UnifiedDatabaseService(force_encryption=True)
    return service
