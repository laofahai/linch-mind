#!/usr/bin/env python3
"""
智能存储配置管理
定义基于Ollama本地AI + FAISS向量库 + 分层存储的智能知识管理系统配置
"""

import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any

from core.environment_manager import get_environment_manager


@dataclass
class OllamaConfig:
    """Ollama AI配置"""
    host: str = "http://localhost:11434"
    embedding_model: str = "nomic-embed-text:latest"
    llm_model: str = "qwen2.5:0.5b"
    value_threshold: float = 0.3
    entity_threshold: float = 0.8
    max_content_length: int = 10000
    request_timeout: int = 30
    connection_timeout: int = 5


@dataclass
class FAISSConfig:
    """FAISS向量存储配置"""
    vector_dim: int = 384
    compressed_dim: int = 256
    shard_size_limit: int = 100000
    compression_method: str = "PQ"  # PQ/SQ/HNSW
    index_type: str = "HNSW"  # HNSW/IVF/Flat
    max_memory_mb: int = 1024
    preload_hot_shards: bool = True


@dataclass
class LifecycleConfig:
    """数据生命周期管理配置"""
    hot_retention_days: int = 90
    warm_retention_days: int = 365
    cold_retention_days: int = 1095  # 3年
    cleanup_schedule: str = "quarterly"  # daily/weekly/monthly/quarterly
    auto_archival: bool = True
    auto_cleanup: bool = True
    backup_before_cleanup: bool = True


@dataclass
class ProcessingConfig:
    """事件处理配置"""
    enable_intelligent_processing: bool = True
    enable_vector_storage: bool = True
    enable_entity_extraction: bool = True
    enable_traditional_fallback: bool = True
    batch_processing_size: int = 100
    max_workers: int = 4
    processing_timeout: int = 60


@dataclass
class MonitoringConfig:
    """监控配置"""
    enable_metrics: bool = True
    metrics_retention_days: int = 30
    performance_alerts: bool = True
    storage_alerts: bool = True
    ai_accuracy_threshold: float = 0.85
    compression_ratio_threshold: float = 5.0


@dataclass
class SecurityConfig:
    """安全配置"""
    encrypt_vectors: bool = False  # 暂时关闭，影响性能
    encrypt_metadata: bool = True
    anonymize_content: bool = False
    audit_logging: bool = True
    access_control: bool = True


@dataclass
class IntelligentStorageConfig:
    """智能存储完整配置"""
    ollama: OllamaConfig
    faiss: FAISSConfig
    lifecycle: LifecycleConfig
    processing: ProcessingConfig
    monitoring: MonitoringConfig
    security: SecurityConfig
    
    # 存储路径配置
    storage_dir: Optional[Path] = None
    cache_dir: Optional[Path] = None
    temp_dir: Optional[Path] = None
    
    # 环境配置
    environment: str = "development"
    debug: bool = False


class IntelligentStorageConfigManager:
    """智能存储配置管理器"""
    
    def __init__(self):
        self.env_manager = get_environment_manager()
        self._config: Optional[IntelligentStorageConfig] = None
    
    def get_config(self) -> IntelligentStorageConfig:
        """获取配置（懒加载）"""
        if self._config is None:
            self._config = self._load_config()
        return self._config
    
    def _load_config(self) -> IntelligentStorageConfig:
        """加载配置"""
        # 基础配置
        base_config = self._get_default_config()
        
        # 环境特定配置
        env_config = self._get_environment_config()
        
        # 合并配置
        merged_config = self._merge_configs(base_config, env_config)
        
        # 设置路径
        merged_config.storage_dir = self._get_storage_dir()
        merged_config.cache_dir = self._get_cache_dir()
        merged_config.temp_dir = self._get_temp_dir()
        
        # 设置环境信息
        merged_config.environment = self.env_manager.current_environment
        merged_config.debug = self.env_manager.current_environment.value == "development"
        
        return merged_config
    
    def _get_default_config(self) -> IntelligentStorageConfig:
        """获取默认配置"""
        return IntelligentStorageConfig(
            ollama=OllamaConfig(),
            faiss=FAISSConfig(),
            lifecycle=LifecycleConfig(),
            processing=ProcessingConfig(),
            monitoring=MonitoringConfig(),
            security=SecurityConfig(),
        )
    
    def _get_environment_config(self) -> Dict[str, Any]:
        """获取环境特定配置"""
        env = self.env_manager.current_environment
        
        if env == "development":
            return {
                "ollama": {
                    "value_threshold": 0.2,  # 开发环境接受更多内容
                    "entity_threshold": 0.7,
                },
                "faiss": {
                    "shard_size_limit": 10000,  # 小分片便于测试
                },
                "processing": {
                    "max_workers": 2,
                },
                "monitoring": {
                    "performance_alerts": False,  # 关闭开发环境告警
                },
                "security": {
                    "encrypt_metadata": False,  # 开发环境不加密
                    "audit_logging": False,
                },
            }
        
        elif env == "staging":
            return {
                "ollama": {
                    "value_threshold": 0.25,
                },
                "faiss": {
                    "shard_size_limit": 50000,
                },
                "lifecycle": {
                    "hot_retention_days": 30,
                    "warm_retention_days": 180,
                },
                "security": {
                    "encrypt_metadata": True,
                    "audit_logging": True,
                },
            }
        
        elif env == "production":
            return {
                "ollama": {
                    "value_threshold": 0.3,  # 生产环境严格过滤
                    "entity_threshold": 0.8,
                },
                "faiss": {
                    "shard_size_limit": 100000,
                    "max_memory_mb": 2048,
                },
                "lifecycle": {
                    "auto_cleanup": True,
                    "backup_before_cleanup": True,
                },
                "processing": {
                    "max_workers": 4,
                },
                "monitoring": {
                    "performance_alerts": True,
                    "storage_alerts": True,
                },
                "security": {
                    "encrypt_metadata": True,
                    "audit_logging": True,
                    "access_control": True,
                },
            }
        
        else:
            return {}
    
    def _merge_configs(
        self, 
        base_config: IntelligentStorageConfig, 
        env_overrides: Dict[str, Any]
    ) -> IntelligentStorageConfig:
        """合并配置"""
        config_dict = asdict(base_config)
        
        # 深度合并环境配置
        for section, overrides in env_overrides.items():
            if section in config_dict:
                if isinstance(config_dict[section], dict):
                    config_dict[section].update(overrides)
                else:
                    # 对于dataclass对象，需要特殊处理
                    section_obj = getattr(base_config, section)
                    for key, value in overrides.items():
                        if hasattr(section_obj, key):
                            setattr(section_obj, key, value)
        
        return base_config
    
    def _get_storage_dir(self) -> Path:
        """获取存储目录"""
        data_dir = self.env_manager.current_config.data_dir
        storage_dir = data_dir / "knowledge"
        storage_dir.mkdir(parents=True, exist_ok=True)
        return storage_dir
    
    def _get_cache_dir(self) -> Path:
        """获取缓存目录"""
        storage_dir = self._get_storage_dir()
        cache_dir = storage_dir / "ollama_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    
    def _get_temp_dir(self) -> Path:
        """获取临时目录"""
        storage_dir = self._get_storage_dir()
        temp_dir = storage_dir / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir
    
    def get_ollama_host(self) -> str:
        """获取Ollama主机地址（从配置文件读取）"""
        # 尝试从用户配置获取，如果没有则使用智能存储配置
        try:
            from .user_config_manager import get_user_config
            user_config = get_user_config()
            return user_config.ollama.host
        except Exception:
            # 回退到智能存储配置
            return self.get_config().ollama.host
    
    def get_embedding_model(self) -> str:
        """获取嵌入模型名称（从配置文件读取）"""
        try:
            from .user_config_manager import get_user_config
            user_config = get_user_config()
            return user_config.ollama.embedding_model
        except Exception:
            return self.get_config().ollama.embedding_model
    
    def get_llm_model(self) -> str:
        """获取LLM模型名称（从配置文件读取）"""
        try:
            from .user_config_manager import get_user_config
            user_config = get_user_config()
            return user_config.ollama.llm_model
        except Exception:
            return self.get_config().ollama.llm_model
    
    def is_intelligent_processing_enabled(self) -> bool:
        """检查是否启用智能处理（从配置文件读取）"""
        try:
            from .user_config_manager import get_user_config
            user_config = get_user_config()
            return user_config.performance.enable_caching
        except Exception:
            return self.get_config().processing.enable_intelligent_processing
    
    def get_value_threshold(self) -> float:
        """获取价值阈值（从配置文件读取）"""
        try:
            from .user_config_manager import get_user_config
            user_config = get_user_config()
            return user_config.ollama.value_threshold
        except Exception:
            return self.get_config().ollama.value_threshold
    
    def validate_config(self) -> List[str]:
        """验证配置"""
        errors = []
        config = self.get_config()
        
        # 验证Ollama配置
        if not config.ollama.host:
            errors.append("Ollama host不能为空")
        
        if not config.ollama.embedding_model:
            errors.append("嵌入模型名称不能为空")
        
        if not config.ollama.llm_model:
            errors.append("LLM模型名称不能为空")
        
        if not (0 <= config.ollama.value_threshold <= 1):
            errors.append("价值阈值必须在0-1之间")
        
        # 验证FAISS配置
        if config.faiss.vector_dim <= 0:
            errors.append("向量维度必须大于0")
        
        if config.faiss.compressed_dim > config.faiss.vector_dim:
            errors.append("压缩维度不能大于原始维度")
        
        if config.faiss.shard_size_limit <= 0:
            errors.append("分片大小限制必须大于0")
        
        # 验证生命周期配置
        if config.lifecycle.hot_retention_days <= 0:
            errors.append("热数据保留天数必须大于0")
        
        if config.lifecycle.warm_retention_days <= config.lifecycle.hot_retention_days:
            errors.append("温数据保留天数必须大于热数据保留天数")
        
        # 验证存储路径
        if not config.storage_dir or not config.storage_dir.exists():
            errors.append(f"存储目录不存在: {config.storage_dir}")
        
        return errors
    
    def save_config_template(self, output_path: Path):
        """保存配置模板"""
        config = self._get_default_config()
        config_dict = asdict(config)
        
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=2)
    
    def export_current_config(self, output_path: Path):
        """导出当前配置"""
        config = self.get_config()
        config_dict = asdict(config)
        
        # 转换Path对象为字符串
        if config_dict.get('storage_dir'):
            config_dict['storage_dir'] = str(config_dict['storage_dir'])
        if config_dict.get('cache_dir'):
            config_dict['cache_dir'] = str(config_dict['cache_dir'])
        if config_dict.get('temp_dir'):
            config_dict['temp_dir'] = str(config_dict['temp_dir'])
        
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=2)


# 全局配置管理器实例
_config_manager: Optional[IntelligentStorageConfigManager] = None

def get_intelligent_storage_config() -> IntelligentStorageConfig:
    """获取智能存储配置"""
    global _config_manager
    if _config_manager is None:
        _config_manager = IntelligentStorageConfigManager()
    return _config_manager.get_config()

def get_config_manager() -> IntelligentStorageConfigManager:
    """获取配置管理器"""
    global _config_manager
    if _config_manager is None:
        _config_manager = IntelligentStorageConfigManager()
    return _config_manager


# 常用配置常量
DEFAULT_STORAGE_CONFIG = {
    "ollama": {
        "host": "http://localhost:11434",
        "embedding_model": "nomic-embed-text:latest",
        "llm_model": "qwen2.5:0.5b",
        "value_threshold": 0.3,
        "entity_threshold": 0.8
    },
    "faiss": {
        "vector_dim": 384,
        "compressed_dim": 256,
        "shard_size_limit": 100000,
        "compression_method": "PQ"
    },
    "lifecycle": {
        "hot_retention_days": 90,
        "warm_retention_days": 365,
        "cleanup_schedule": "quarterly"
    }
}