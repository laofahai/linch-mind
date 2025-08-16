#!/usr/bin/env python3
"""
统一持久化服务 - 消除9个重复save/load实现
整合JSON、Pickle、加密存储为统一接口
"""

import asyncio
import json
import logging
import pickle
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
import tempfile

logger = logging.getLogger(__name__)


class StorageFormat(Enum):
    """存储格式枚举"""
    JSON = "json"
    PICKLE = "pickle"
    TEXT = "text"
    BINARY = "binary"
    ENCRYPTED = "encrypted"


class CompressionType(Enum):
    """压缩类型枚举"""
    NONE = "none"
    GZIP = "gzip"
    BZIP2 = "bzip2"
    LZMA = "lzma"


@dataclass
class StorageMetadata:
    """存储元数据"""
    key: str
    format: StorageFormat
    compression: CompressionType = CompressionType.NONE
    encrypted: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    size_bytes: int = 0
    checksum: Optional[str] = None
    backup_count: int = 0


@dataclass
class PersistenceStats:
    """持久化统计信息"""
    total_saves: int = 0
    total_loads: int = 0
    total_backups: int = 0
    failed_operations: int = 0
    data_size_bytes: int = 0
    last_operation: Optional[datetime] = None


class UnifiedPersistenceService:
    """统一持久化服务 - 消除9个重复save/load实现"""
    
    def __init__(
        self,
        base_dir: Optional[Path] = None,
        enable_backup: bool = True,
        max_backups: int = 5,
        enable_compression: bool = False,
        default_format: StorageFormat = StorageFormat.JSON,
        enable_checksum: bool = True
    ):
        # 基础配置
        self.base_dir = Path(base_dir) if base_dir else self._get_default_base_dir()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.enable_backup = enable_backup
        self.max_backups = max_backups
        self.enable_compression = enable_compression
        self.default_format = default_format
        self.enable_checksum = enable_checksum
        
        # 目录结构
        self.data_dir = self.base_dir / "data"
        self.backup_dir = self.base_dir / "backups"
        self.metadata_dir = self.base_dir / "metadata"
        
        for dir_path in [self.data_dir, self.backup_dir, self.metadata_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 统计信息
        self.stats = PersistenceStats()
        
        # 元数据缓存
        self._metadata_cache: Dict[str, StorageMetadata] = {}
        
        # 序列化器和压缩器
        self._serializers = {
            StorageFormat.JSON: self._serialize_json,
            StorageFormat.PICKLE: self._serialize_pickle,
            StorageFormat.TEXT: self._serialize_text,
            StorageFormat.BINARY: self._serialize_binary,
            StorageFormat.ENCRYPTED: self._serialize_encrypted,
        }
        
        self._deserializers = {
            StorageFormat.JSON: self._deserialize_json,
            StorageFormat.PICKLE: self._deserialize_pickle,
            StorageFormat.TEXT: self._deserialize_text,
            StorageFormat.BINARY: self._deserialize_binary,
            StorageFormat.ENCRYPTED: self._deserialize_encrypted,
        }
        
        self._compressors = {
            CompressionType.NONE: lambda x: x,
            CompressionType.GZIP: self._compress_gzip,
            CompressionType.BZIP2: self._compress_bzip2,
            CompressionType.LZMA: self._compress_lzma,
        }
        
        self._decompressors = {
            CompressionType.NONE: lambda x: x,
            CompressionType.GZIP: self._decompress_gzip,
            CompressionType.BZIP2: self._decompress_bzip2,
            CompressionType.LZMA: self._decompress_lzma,
        }
        
        logger.info(f"💾 UnifiedPersistenceService 初始化 (目录: {self.base_dir})")

    async def save(
        self,
        key: str,
        data: Any,
        format: Optional[StorageFormat] = None,
        compression: Optional[CompressionType] = None,
        encrypted: bool = False,
        create_backup: Optional[bool] = None
    ) -> bool:
        """统一保存接口 - 替代9个重复save实现"""
        try:
            if format is None:
                format = self.default_format
            
            if compression is None:
                compression = CompressionType.GZIP if self.enable_compression else CompressionType.NONE
            
            if create_backup is None:
                create_backup = self.enable_backup
            
            # 标准化键
            normalized_key = self._normalize_key(key)
            
            # 创建备份
            if create_backup:
                await self._create_backup(normalized_key)
            
            # 序列化数据
            serialized_data = await self._serialize_data(data, format)
            
            # 压缩数据
            compressed_data = await self._compress_data(serialized_data, compression)
            
            # 加密数据（如果需要）
            if encrypted:
                compressed_data = await self._encrypt_data(compressed_data)
            
            # 计算校验和
            checksum = None
            if self.enable_checksum:
                checksum = self._calculate_checksum(compressed_data)
            
            # 原子写入
            success = await self._atomic_write(normalized_key, compressed_data)
            
            if success:
                # 更新元数据
                metadata = StorageMetadata(
                    key=normalized_key,
                    format=format,
                    compression=compression,
                    encrypted=encrypted,
                    size_bytes=len(compressed_data),
                    checksum=checksum,
                    updated_at=datetime.utcnow()
                )
                
                await self._save_metadata(normalized_key, metadata)
                self._metadata_cache[normalized_key] = metadata
                
                # 更新统计
                self.stats.total_saves += 1
                self.stats.data_size_bytes += len(compressed_data)
                self.stats.last_operation = datetime.utcnow()
                
                logger.debug(f"保存成功 [{format.value}]: {key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"保存失败 [{key}]: {e}")
            self.stats.failed_operations += 1
            return False

    async def load(
        self,
        key: str,
        default: Any = None,
        verify_checksum: bool = True
    ) -> Any:
        """统一加载接口 - 替代9个重复load实现"""
        try:
            normalized_key = self._normalize_key(key)
            
            # 检查文件是否存在
            data_file = self._get_data_file_path(normalized_key)
            if not data_file.exists():
                logger.debug(f"文件不存在: {key}")
                return default
            
            # 加载元数据
            metadata = await self._load_metadata(normalized_key)
            if not metadata:
                logger.warning(f"元数据缺失，尝试自动检测格式: {key}")
                metadata = await self._auto_detect_format(normalized_key)
            
            # 读取数据
            with open(data_file, 'rb') as f:
                raw_data = f.read()
            
            # 校验数据完整性
            if verify_checksum and metadata.checksum and self.enable_checksum:
                current_checksum = self._calculate_checksum(raw_data)
                if current_checksum != metadata.checksum:
                    logger.error(f"数据完整性校验失败: {key}")
                    return default
            
            # 解密数据（如果需要）
            if metadata.encrypted:
                raw_data = await self._decrypt_data(raw_data)
            
            # 解压数据
            decompressed_data = await self._decompress_data(raw_data, metadata.compression)
            
            # 反序列化数据
            data = await self._deserialize_data(decompressed_data, metadata.format)
            
            # 更新统计
            self.stats.total_loads += 1
            self.stats.last_operation = datetime.utcnow()
            
            logger.debug(f"加载成功 [{metadata.format.value}]: {key}")
            return data
            
        except Exception as e:
            logger.error(f"加载失败 [{key}]: {e}")
            self.stats.failed_operations += 1
            return default

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        normalized_key = self._normalize_key(key)
        data_file = self._get_data_file_path(normalized_key)
        return data_file.exists()

    async def delete(self, key: str, create_backup: bool = True) -> bool:
        """删除数据"""
        try:
            normalized_key = self._normalize_key(key)
            
            if create_backup:
                await self._create_backup(normalized_key)
            
            # 删除数据文件
            data_file = self._get_data_file_path(normalized_key)
            if data_file.exists():
                data_file.unlink()
            
            # 删除元数据文件
            metadata_file = self._get_metadata_file_path(normalized_key)
            if metadata_file.exists():
                metadata_file.unlink()
            
            # 清除缓存
            self._metadata_cache.pop(normalized_key, None)
            
            logger.debug(f"删除成功: {key}")
            return True
            
        except Exception as e:
            logger.error(f"删除失败 [{key}]: {e}")
            return False

    async def list_keys(self, pattern: Optional[str] = None) -> List[str]:
        """列出所有键"""
        try:
            keys = []
            for data_file in self.data_dir.glob("*"):
                if data_file.is_file():
                    key = data_file.stem  # 移除扩展名
                    
                    if pattern:
                        import re
                        if not re.search(pattern, key):
                            continue
                    
                    keys.append(key)
            
            return sorted(keys)
            
        except Exception as e:
            logger.error(f"列出键失败: {e}")
            return []

    # === 备份和恢复 ===
    
    async def create_backup(self, key: str) -> Optional[str]:
        """创建备份"""
        return await self._create_backup(self._normalize_key(key))
    
    async def restore_from_backup(self, key: str, backup_timestamp: Optional[str] = None) -> bool:
        """从备份恢复"""
        try:
            normalized_key = self._normalize_key(key)
            
            # 找到备份文件
            if backup_timestamp:
                backup_file = self.backup_dir / f"{normalized_key}_{backup_timestamp}.bak"
            else:
                # 使用最新备份
                backup_files = list(self.backup_dir.glob(f"{normalized_key}_*.bak"))
                if not backup_files:
                    logger.error(f"没有找到备份文件: {key}")
                    return False
                
                backup_file = max(backup_files, key=lambda f: f.stat().st_mtime)
            
            if not backup_file.exists():
                logger.error(f"备份文件不存在: {backup_file}")
                return False
            
            # 恢复数据文件
            data_file = self._get_data_file_path(normalized_key)
            shutil.copy2(backup_file, data_file)
            
            logger.info(f"从备份恢复成功: {key}")
            return True
            
        except Exception as e:
            logger.error(f"从备份恢复失败 [{key}]: {e}")
            return False

    # === 批量操作 ===
    
    async def batch_save(self, items: Dict[str, Any], **kwargs) -> Dict[str, bool]:
        """批量保存"""
        results = {}
        for key, data in items.items():
            results[key] = await self.save(key, data, **kwargs)
        return results
    
    async def batch_load(self, keys: List[str], **kwargs) -> Dict[str, Any]:
        """批量加载"""
        results = {}
        for key in keys:
            results[key] = await self.load(key, **kwargs)
        return results

    # === 内部方法 ===
    
    def _get_default_base_dir(self) -> Path:
        """获取默认基础目录"""
        try:
            from core.environment_manager import get_environment_manager
            env_manager = get_environment_manager()
            return env_manager.get_data_dir() / "persistence"
        except:
            return Path.home() / ".linch-mind" / "persistence"
    
    def _normalize_key(self, key: str) -> str:
        """标准化键"""
        # 替换特殊字符以创建有效的文件名
        import re
        return re.sub(r'[^\w\-_.]', '_', key)
    
    def _get_data_file_path(self, key: str) -> Path:
        """获取数据文件路径"""
        return self.data_dir / f"{key}.dat"
    
    def _get_metadata_file_path(self, key: str) -> Path:
        """获取元数据文件路径"""
        return self.metadata_dir / f"{key}.meta"
    
    async def _create_backup(self, key: str) -> Optional[str]:
        """创建备份"""
        try:
            data_file = self._get_data_file_path(key)
            if not data_file.exists():
                return None
            
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"{key}_{timestamp}.bak"
            
            # 复制文件
            shutil.copy2(data_file, backup_file)
            
            # 清理旧备份
            await self._cleanup_old_backups(key)
            
            self.stats.total_backups += 1
            logger.debug(f"创建备份: {backup_file}")
            
            return timestamp
            
        except Exception as e:
            logger.error(f"创建备份失败 [{key}]: {e}")
            return None
    
    async def _cleanup_old_backups(self, key: str):
        """清理旧备份"""
        try:
            backup_files = sorted(
                self.backup_dir.glob(f"{key}_*.bak"),
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )
            
            # 保留最新的N个备份
            for backup_file in backup_files[self.max_backups:]:
                backup_file.unlink()
                
        except Exception as e:
            logger.error(f"清理备份失败 [{key}]: {e}")
    
    async def _atomic_write(self, key: str, data: bytes) -> bool:
        """原子写入"""
        try:
            data_file = self._get_data_file_path(key)
            
            # 使用临时文件确保原子操作
            with tempfile.NamedTemporaryFile(
                dir=self.data_dir,
                delete=False,
                suffix=".tmp"
            ) as tmp_file:
                tmp_file.write(data)
                tmp_file.flush()
                tmp_path = Path(tmp_file.name)
            
            # 原子移动
            tmp_path.rename(data_file)
            return True
            
        except Exception as e:
            logger.error(f"原子写入失败 [{key}]: {e}")
            return False
    
    async def _save_metadata(self, key: str, metadata: StorageMetadata):
        """保存元数据"""
        try:
            metadata_file = self._get_metadata_file_path(key)
            metadata_dict = {
                "key": metadata.key,
                "format": metadata.format.value,
                "compression": metadata.compression.value,
                "encrypted": metadata.encrypted,
                "created_at": metadata.created_at.isoformat(),
                "updated_at": metadata.updated_at.isoformat(),
                "size_bytes": metadata.size_bytes,
                "checksum": metadata.checksum,
                "backup_count": metadata.backup_count
            }
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata_dict, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"保存元数据失败 [{key}]: {e}")
    
    async def _load_metadata(self, key: str) -> Optional[StorageMetadata]:
        """加载元数据"""
        try:
            if key in self._metadata_cache:
                return self._metadata_cache[key]
            
            metadata_file = self._get_metadata_file_path(key)
            if not metadata_file.exists():
                return None
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata_dict = json.load(f)
            
            metadata = StorageMetadata(
                key=metadata_dict["key"],
                format=StorageFormat(metadata_dict["format"]),
                compression=CompressionType(metadata_dict["compression"]),
                encrypted=metadata_dict["encrypted"],
                created_at=datetime.fromisoformat(metadata_dict["created_at"]),
                updated_at=datetime.fromisoformat(metadata_dict["updated_at"]),
                size_bytes=metadata_dict["size_bytes"],
                checksum=metadata_dict.get("checksum"),
                backup_count=metadata_dict.get("backup_count", 0)
            )
            
            self._metadata_cache[key] = metadata
            return metadata
            
        except Exception as e:
            logger.error(f"加载元数据失败 [{key}]: {e}")
            return None
    
    async def _auto_detect_format(self, key: str) -> StorageMetadata:
        """自动检测数据格式"""
        try:
            data_file = self._get_data_file_path(key)
            with open(data_file, 'rb') as f:
                first_bytes = f.read(16)
            
            # 简单的格式检测
            if first_bytes.startswith(b'{') or first_bytes.startswith(b'['):
                format = StorageFormat.JSON
            elif first_bytes.startswith(b'\x80\x03') or first_bytes.startswith(b'\x80\x04'):
                format = StorageFormat.PICKLE
            else:
                format = StorageFormat.BINARY
            
            return StorageMetadata(
                key=key,
                format=format,
                compression=CompressionType.NONE,
                encrypted=False
            )
            
        except Exception as e:
            logger.error(f"自动检测格式失败 [{key}]: {e}")
            # 默认格式
            return StorageMetadata(
                key=key,
                format=self.default_format,
                compression=CompressionType.NONE,
                encrypted=False
            )
    
    # === 序列化器 ===
    
    async def _serialize_data(self, data: Any, format: StorageFormat) -> bytes:
        """序列化数据"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._serializers[format], data)
    
    async def _deserialize_data(self, data: bytes, format: StorageFormat) -> Any:
        """反序列化数据"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._deserializers[format], data)
    
    def _serialize_json(self, data: Any) -> bytes:
        """JSON序列化"""
        return json.dumps(data, ensure_ascii=False, default=str).encode('utf-8')
    
    def _deserialize_json(self, data: bytes) -> Any:
        """JSON反序列化"""
        return json.loads(data.decode('utf-8'))
    
    def _serialize_pickle(self, data: Any) -> bytes:
        """Pickle序列化"""
        return pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
    
    def _deserialize_pickle(self, data: bytes) -> Any:
        """Pickle反序列化"""
        return pickle.loads(data)
    
    def _serialize_text(self, data: Any) -> bytes:
        """文本序列化"""
        return str(data).encode('utf-8')
    
    def _deserialize_text(self, data: bytes) -> str:
        """文本反序列化"""
        return data.decode('utf-8')
    
    def _serialize_binary(self, data: Any) -> bytes:
        """二进制序列化"""
        if isinstance(data, bytes):
            return data
        elif isinstance(data, str):
            return data.encode('utf-8')
        else:
            return pickle.dumps(data)
    
    def _deserialize_binary(self, data: bytes) -> Any:
        """二进制反序列化"""
        try:
            return pickle.loads(data)
        except:
            return data
    
    def _serialize_encrypted(self, data: Any) -> bytes:
        """加密序列化"""
        # 先JSON序列化，然后加密
        json_data = self._serialize_json(data)
        return self._encrypt_data_sync(json_data)
    
    def _deserialize_encrypted(self, data: bytes) -> Any:
        """加密反序列化"""
        # 先解密，然后JSON反序列化
        decrypted_data = self._decrypt_data_sync(data)
        return self._deserialize_json(decrypted_data)
    
    # === 压缩器 ===
    
    async def _compress_data(self, data: bytes, compression: CompressionType) -> bytes:
        """压缩数据"""
        if compression == CompressionType.NONE:
            return data
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._compressors[compression], data)
    
    async def _decompress_data(self, data: bytes, compression: CompressionType) -> bytes:
        """解压数据"""
        if compression == CompressionType.NONE:
            return data
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._decompressors[compression], data)
    
    def _compress_gzip(self, data: bytes) -> bytes:
        """GZIP压缩"""
        import gzip
        return gzip.compress(data)
    
    def _decompress_gzip(self, data: bytes) -> bytes:
        """GZIP解压"""
        import gzip
        return gzip.decompress(data)
    
    def _compress_bzip2(self, data: bytes) -> bytes:
        """BZIP2压缩"""
        import bz2
        return bz2.compress(data)
    
    def _decompress_bzip2(self, data: bytes) -> bytes:
        """BZIP2解压"""
        import bz2
        return bz2.decompress(data)
    
    def _compress_lzma(self, data: bytes) -> bytes:
        """LZMA压缩"""
        import lzma
        return lzma.compress(data)
    
    def _decompress_lzma(self, data: bytes) -> bytes:
        """LZMA解压"""
        import lzma
        return lzma.decompress(data)
    
    # === 加密器 ===
    
    async def _encrypt_data(self, data: bytes) -> bytes:
        """异步加密数据"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._encrypt_data_sync, data)
    
    async def _decrypt_data(self, data: bytes) -> bytes:
        """异步解密数据"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._decrypt_data_sync, data)
    
    def _encrypt_data_sync(self, data: bytes) -> bytes:
        """同步加密数据"""
        try:
            from services.security.selective_encrypted_storage import get_selective_encrypted_storage
            storage = get_selective_encrypted_storage()
            return storage.encrypt_data(data)
        except Exception as e:
            logger.warning(f"加密失败，返回原始数据: {e}")
            return data
    
    def _decrypt_data_sync(self, data: bytes) -> bytes:
        """同步解密数据"""
        try:
            from services.security.selective_encrypted_storage import get_selective_encrypted_storage
            storage = get_selective_encrypted_storage()
            return storage.decrypt_data(data)
        except Exception as e:
            logger.warning(f"解密失败，返回原始数据: {e}")
            return data
    
    def _calculate_checksum(self, data: bytes) -> str:
        """计算校验和"""
        import hashlib
        return hashlib.sha256(data).hexdigest()
    
    def get_stats(self) -> PersistenceStats:
        """获取持久化统计信息"""
        # 更新磁盘使用统计
        try:
            total_size = 0
            for data_file in self.data_dir.glob("*.dat"):
                total_size += data_file.stat().st_size
            self.stats.data_size_bytes = total_size
        except Exception as e:
            logger.error(f"计算磁盘使用失败: {e}")
        
        return self.stats


# 全局实例管理
_unified_persistence_service: Optional[UnifiedPersistenceService] = None


def get_unified_persistence_service(
    base_dir: Optional[Path] = None,
    **kwargs
) -> UnifiedPersistenceService:
    """获取统一持久化服务实例"""
    global _unified_persistence_service
    
    if _unified_persistence_service is None:
        _unified_persistence_service = UnifiedPersistenceService(
            base_dir=base_dir,
            **kwargs
        )
    
    return _unified_persistence_service


async def cleanup_unified_persistence_service():
    """清理统一持久化服务"""
    global _unified_persistence_service
    
    if _unified_persistence_service:
        try:
            # 执行任何必要的清理
            logger.info("💾 UnifiedPersistenceService 已清理")
        except Exception as e:
            logger.error(f"清理UnifiedPersistenceService失败: {e}")
        finally:
            _unified_persistence_service = None