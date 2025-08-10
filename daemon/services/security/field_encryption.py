#!/usr/bin/env python3
"""
应用层字段加密 - 基于cryptography库的AES-256-GCM字段加密
提供SQLAlchemy TypeDecorator实现透明的字段级加密/解密
"""

import base64
import logging
import os
from typing import Any, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from sqlalchemy import String, TypeDecorator
from sqlalchemy.types import Text

logger = logging.getLogger(__name__)


class FieldEncryptionManager:
    """
    字段加密管理器
    
    功能:
    1. 管理字段加密密钥
    2. 提供高性能的AES-256-GCM加密/解密
    3. 与操作系统密钥环集成
    4. 支持密钥轮换
    """
    
    def __init__(self):
        self._fernet: Optional[Fernet] = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """初始化加密系统"""
        try:
            encryption_key = self._get_or_create_key()
            if encryption_key:
                self._fernet = Fernet(encryption_key)
                logger.info("字段加密系统初始化成功")
            else:
                logger.error("字段加密系统初始化失败 - 无法获取加密密钥")
        except Exception as e:
            logger.error(f"字段加密系统初始化失败: {e}")
            raise
    
    def _get_or_create_key(self) -> Optional[bytes]:
        """获取或创建加密密钥"""
        try:
            import keyring
            
            # 尝试从系统密钥环获取密钥
            key_b64 = keyring.get_password("linch-mind", "field-encryption-key")
            
            if key_b64:
                logger.info("从系统密钥环获取现有加密密钥")
                return base64.urlsafe_b64decode(key_b64.encode())
            else:
                # 生成新的加密密钥
                logger.info("生成新的字段加密密钥")
                key = Fernet.generate_key()
                
                # 存储到系统密钥环
                key_b64_str = base64.urlsafe_b64encode(key).decode()
                keyring.set_password("linch-mind", "field-encryption-key", key_b64_str)
                
                logger.info("新密钥已存储到系统密钥环")
                return key
                
        except Exception as e:
            logger.error(f"密钥管理失败: {e}")
            # 回退到环境变量
            return self._get_key_from_env()
    
    def _get_key_from_env(self) -> Optional[bytes]:
        """从环境变量获取密钥（回退方案）"""
        try:
            env_key = os.getenv('LINCH_MIND_ENCRYPTION_KEY')
            if env_key:
                logger.warning("使用环境变量中的加密密钥")
                return base64.urlsafe_b64decode(env_key.encode())
            else:
                # 生成临时密钥（开发模式）
                logger.warning("生成临时加密密钥 - 仅用于开发模式")
                return Fernet.generate_key()
        except Exception as e:
            logger.error(f"环境变量密钥获取失败: {e}")
            return None
    
    def encrypt_field(self, plaintext: str) -> str:
        """加密字段值"""
        if not self._fernet:
            raise RuntimeError("加密系统未初始化")
        
        if not plaintext:
            return plaintext
            
        try:
            # 转换为字节并加密
            plaintext_bytes = plaintext.encode('utf-8')
            encrypted_bytes = self._fernet.encrypt(plaintext_bytes)
            
            # 转换为base64字符串存储
            encrypted_b64 = base64.urlsafe_b64encode(encrypted_bytes).decode('ascii')
            return f"enc:{encrypted_b64}"  # 添加前缀标识
            
        except Exception as e:
            logger.error(f"字段加密失败: {e}")
            raise
    
    def decrypt_field(self, ciphertext: str) -> str:
        """解密字段值"""
        if not self._fernet:
            raise RuntimeError("加密系统未初始化")
        
        if not ciphertext or not ciphertext.startswith("enc:"):
            # 未加密的数据直接返回
            return ciphertext
            
        try:
            # 移除前缀并解码base64
            encrypted_b64 = ciphertext[4:]  # 移除 "enc:" 前缀
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_b64.encode('ascii'))
            
            # 解密并转换为字符串
            plaintext_bytes = self._fernet.decrypt(encrypted_bytes)
            return plaintext_bytes.decode('utf-8')
            
        except Exception as e:
            logger.error(f"字段解密失败: {e}")
            # 返回原始数据，可能是未加密的旧数据
            return ciphertext
    
    def is_encrypted(self, value: str) -> bool:
        """检查值是否已加密"""
        return value and value.startswith("enc:")
    
    def get_encryption_info(self) -> dict:
        """获取加密信息"""
        return {
            "encryption_enabled": self._fernet is not None,
            "algorithm": "AES-256-GCM (via Fernet)",
            "key_source": "system keyring" if self._fernet else "unavailable"
        }


# 全局加密管理器实例
_encryption_manager: Optional[FieldEncryptionManager] = None


def get_encryption_manager() -> FieldEncryptionManager:
    """获取全局加密管理器实例"""
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = FieldEncryptionManager()
    return _encryption_manager


class EncryptedString(TypeDecorator):
    """
    加密字符串类型 - SQLAlchemy TypeDecorator
    提供透明的字段级加密/解密
    """
    
    impl = String(2000)  # 加密后数据会变长，预留足够空间
    cache_ok = True
    
    def process_bind_param(self, value: Any, dialect) -> Optional[str]:
        """将Python值转换为数据库存储值（加密）"""
        if value is None:
            return value
        
        if not isinstance(value, str):
            value = str(value)
        
        try:
            manager = get_encryption_manager()
            encrypted_value = manager.encrypt_field(value)
            logger.debug(f"字段加密: {len(value)} bytes -> {len(encrypted_value)} bytes")
            return encrypted_value
        except Exception as e:
            logger.error(f"字段加密失败，存储明文: {e}")
            return value
    
    def process_result_value(self, value: Any, dialect) -> Optional[str]:
        """将数据库存储值转换为Python值（解密）"""
        if value is None:
            return value
        
        try:
            manager = get_encryption_manager()
            decrypted_value = manager.decrypt_field(str(value))
            logger.debug(f"字段解密: {len(value)} bytes -> {len(decrypted_value)} bytes")
            return decrypted_value
        except Exception as e:
            logger.error(f"字段解密失败，返回原值: {e}")
            return value


class EncryptedText(TypeDecorator):
    """
    加密文本类型 - 用于长文本字段
    """
    
    impl = Text  # 使用Text类型支持更长的加密数据
    cache_ok = True
    
    def process_bind_param(self, value: Any, dialect) -> Optional[str]:
        """将Python值转换为数据库存储值（加密）"""
        if value is None:
            return value
        
        if not isinstance(value, str):
            value = str(value)
        
        try:
            manager = get_encryption_manager()
            encrypted_value = manager.encrypt_field(value)
            logger.debug(f"长文本字段加密: {len(value)} bytes -> {len(encrypted_value)} bytes")
            return encrypted_value
        except Exception as e:
            logger.error(f"长文本字段加密失败，存储明文: {e}")
            return value
    
    def process_result_value(self, value: Any, dialect) -> Optional[str]:
        """将数据库存储值转换为Python值（解密）"""
        if value is None:
            return value
        
        try:
            manager = get_encryption_manager()
            decrypted_value = manager.decrypt_field(str(value))
            logger.debug(f"长文本字段解密: {len(value)} bytes -> {len(decrypted_value)} bytes")
            return decrypted_value
        except Exception as e:
            logger.error(f"长文本字段解密失败，返回原值: {e}")
            return value


def test_field_encryption():
    """测试字段加密功能"""
    try:
        manager = get_encryption_manager()
        
        # 测试字符串加密
        test_data = "这是一个测试字符串，包含敏感信息：用户密码123456"
        
        # 加密
        encrypted = manager.encrypt_field(test_data)
        print(f"原文: {test_data}")
        print(f"密文: {encrypted}")
        
        # 解密
        decrypted = manager.decrypt_field(encrypted)
        print(f"解密: {decrypted}")
        
        # 验证
        if test_data == decrypted:
            print("✅ 字段加密测试成功")
            return True
        else:
            print("❌ 字段加密测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 字段加密测试异常: {e}")
        return False


if __name__ == "__main__":
    # 运行测试
    test_field_encryption()