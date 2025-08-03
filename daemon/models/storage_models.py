#!/usr/bin/env python3
"""
存储相关数据模型
Session 5 架构重构 - 存储策略数据结构
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime


class StorageStrategy(Enum):
    """存储策略枚举"""
    EXTRACT_SEMANTICS = "extract_semantics"  # 图片: OCR + AI描述 + 缩略图
    SUMMARIZE_ONLY = "summarize_only"        # 大文件: AI摘要 + 关键信息
    FULL_CONTENT = "full_content"            # 小文本: 完整保存
    SMART_SAMPLE = "smart_sample"            # 其他: 智能采样 + 向量化
    SKIP = "skip"                            # 跳过处理


@dataclass
class StorageDecision:
    """存储决策结果"""
    strategy: StorageStrategy
    max_content_size: int  # 最大内容大小限制
    reason: str           # 决策理由
    metadata: Dict[str, Any]  # 额外元数据


@dataclass
class ProcessedContent:
    """处理后的内容"""
    content: str                    # 处理后的内容
    original_size: int             # 原始内容大小
    processed_size: int            # 处理后大小
    storage_strategy: str          # 使用的存储策略
    processing_reason: str         # 处理原因
    metadata: Dict[str, Any]       # 处理元数据
    processed_at: datetime         # 处理时间


@dataclass 
class FileAnalysis:
    """文件分析结果"""
    file_type: str                 # 文件类型
    language: Optional[str]        # 编程语言(如果是代码)
    is_sensitive: bool            # 是否为敏感文件
    is_binary: bool               # 是否为二进制文件
    size: int                     # 文件大小
    suggested_strategy: StorageStrategy  # 建议的存储策略


@dataclass
class StorageStats:
    """存储统计信息"""
    total_items: int              # 总项目数
    total_original_size: int      # 原始总大小
    total_stored_size: int        # 存储总大小
    compression_ratio: float      # 压缩比率
    strategy_counts: Dict[str, int]  # 各策略使用次数
    space_saved: int              # 节省的空间


@dataclass
class MediaProcessingResult:
    """媒体文件处理结果"""
    original_path: str            # 原始文件路径
    thumbnail_data: Optional[bytes]  # 缩略图数据
    extracted_text: str           # OCR提取的文本
    ai_description: str           # AI生成的描述
    processing_time: float        # 处理耗时
    success: bool                 # 处理是否成功
    error_message: Optional[str]  # 错误信息(如果有)
    

@dataclass
class ContentSample:
    """内容采样结果"""
    head_content: str             # 头部内容
    tail_content: str             # 尾部内容
    sample_method: str            # 采样方法
    total_lines: int              # 总行数
    sampled_lines: int            # 采样行数
    sample_ratio: float           # 采样比率


class ContentType(Enum):
    """内容类型枚举"""
    CODE = "code"
    TEXT = "text"
    MARKDOWN = "markdown"
    JSON = "json"
    XML = "xml"
    IMAGE = "image"
    BINARY = "binary"
    UNKNOWN = "unknown"


@dataclass
class ProcessingConfig:
    """处理配置"""
    max_full_content_size: int = 100 * 1024    # 100KB
    max_process_file_size: int = 10 * 1024 * 1024  # 10MB
    enable_ocr: bool = True                     # 启用OCR
    enable_ai_description: bool = True          # 启用AI描述
    sample_head_ratio: float = 0.4              # 头部采样比例
    sample_tail_ratio: float = 0.4              # 尾部采样比例
    preserve_structure: bool = True             # 保持结构化内容