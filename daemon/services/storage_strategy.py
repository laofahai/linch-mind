#!/usr/bin/env python3
"""
智能存储策略引擎
Session 5 核心实现 - 分层存储策略，避免存储爆炸
"""

import os
import mimetypes
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List
from datetime import datetime
import hashlib
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


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


class StorageDecisionEngine:
    """存储决策引擎 - 根据内容类型和大小决定存储策略"""
    
    def __init__(self):
        # 文件大小阈值
        self.MAX_FULL_CONTENT_SIZE = 100 * 1024  # 100KB
        self.MAX_PROCESS_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        
        # 图片文件扩展名
        self.IMAGE_EXTENSIONS = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
            '.webp', '.ico', '.svg', '.heic', '.heif'
        }
        
        # 代码和文本文件扩展名
        self.CODE_TEXT_EXTENSIONS = {
            '.py', '.js', '.ts', '.html', '.css', '.scss', '.less',
            '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.php',
            '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.md', '.txt', '.json', '.yaml', '.yml', '.xml',
            '.cfg', '.conf', '.ini', '.env', '.gitignore',
            '.dockerfile', '.sql', '.sh', '.bash', '.zsh'
        }
        
        # 敏感文件扩展名 (跳过处理)
        self.SENSITIVE_EXTENSIONS = {
            '.key', '.pem', '.p12', '.keystore', '.jks',
            '.password', '.passwd', '.secret'
        }
        
        # 二进制文件扩展名 (跳过处理)
        self.BINARY_EXTENSIONS = {
            '.exe', '.dll', '.so', '.dylib', '.bin', '.dmg',
            '.zip', '.tar', '.gz', '.rar', '.7z', '.deb', '.rpm'
        }
        
        logger.info("存储决策引擎初始化完成")
    
    def decide_storage_strategy(self, content: str, file_path: str, 
                              metadata: Dict[str, Any] = None) -> StorageDecision:
        """
        决定存储策略
        
        Args:
            content: 文件内容
            file_path: 文件路径
            metadata: 额外元数据
        
        Returns:
            StorageDecision: 存储决策结果
        """
        file_path_obj = Path(file_path)
        file_extension = file_path_obj.suffix.lower()
        content_size = len(content.encode('utf-8'))
        
        # 检查是否为敏感文件
        if self._is_sensitive_file(file_path, file_extension):
            return StorageDecision(
                strategy=StorageStrategy.SKIP,
                max_content_size=0,
                reason="敏感文件，跳过处理",
                metadata={"security": "sensitive_file"}
            )
        
        # 检查是否为二进制文件
        if self._is_binary_file(file_path, file_extension):
            return StorageDecision(
                strategy=StorageStrategy.SKIP,
                max_content_size=0,
                reason="二进制文件，跳过处理",
                metadata={"file_type": "binary"}
            )
        
        # 检查文件大小是否超过处理限制
        if content_size > self.MAX_PROCESS_FILE_SIZE:
            return StorageDecision(
                strategy=StorageStrategy.SKIP,
                max_content_size=0,
                reason=f"文件过大 ({content_size/1024/1024:.1f}MB)，跳过处理",
                metadata={"file_size": content_size}
            )
        
        # 图片文件策略
        if self._is_image_file(file_extension):
            return StorageDecision(
                strategy=StorageStrategy.EXTRACT_SEMANTICS,
                max_content_size=10 * 1024,  # 10KB (OCR文本 + AI描述)
                reason="图片文件，提取语义信息",
                metadata={
                    "file_type": "image",
                    "original_size": content_size,
                    "needs_ocr": True,
                    "needs_ai_description": True,
                    "needs_thumbnail": True
                }
            )
        
        # 大文件策略
        if content_size > self.MAX_FULL_CONTENT_SIZE:
            return StorageDecision(
                strategy=StorageStrategy.SUMMARIZE_ONLY,
                max_content_size=5 * 1024,  # 5KB (AI摘要)
                reason=f"大文件 ({content_size/1024:.1f}KB)，生成摘要",
                metadata={
                    "file_type": "large_text",
                    "original_size": content_size,
                    "needs_ai_summary": True,
                    "needs_entity_extraction": True
                }
            )
        
        # 代码和文本文件策略
        if self._is_code_or_text_file(file_extension):
            return StorageDecision(
                strategy=StorageStrategy.FULL_CONTENT,
                max_content_size=content_size,
                reason="代码/文本文件，完整保存",
                metadata={
                    "file_type": "code_text",
                    "language": self._detect_language(file_extension),
                    "needs_syntax_analysis": True
                }
            )
        
        # 默认策略：智能采样
        return StorageDecision(
            strategy=StorageStrategy.SMART_SAMPLE,
            max_content_size=self.MAX_FULL_CONTENT_SIZE // 2,  # 50KB
            reason="未知文件类型，智能采样",
            metadata={
                "file_type": "unknown",
                "sample_method": "head_tail",
                "needs_content_analysis": True
            }
        )
    
    def _is_sensitive_file(self, file_path: str, extension: str) -> bool:
        """检查是否为敏感文件"""
        if extension in self.SENSITIVE_EXTENSIONS:
            return True
        
        # 检查文件名模式
        filename = Path(file_path).name.lower()
        sensitive_patterns = [
            'password', 'secret', 'private', 'key', 'token',
            'credential', 'auth', '.env'
        ]
        
        return any(pattern in filename for pattern in sensitive_patterns)
    
    def _is_binary_file(self, file_path: str, extension: str) -> bool:
        """检查是否为二进制文件"""
        if extension in self.BINARY_EXTENSIONS:
            return True
        
        # 使用mimetypes检查
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type and not mime_type.startswith('text/'):
            return True
        
        return False
    
    def _is_image_file(self, extension: str) -> bool:
        """检查是否为图片文件"""
        return extension in self.IMAGE_EXTENSIONS
    
    def _is_code_or_text_file(self, extension: str) -> bool:
        """检查是否为代码或文本文件"""
        return extension in self.CODE_TEXT_EXTENSIONS
    
    def _detect_language(self, extension: str) -> str:
        """根据扩展名检测编程语言"""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.md': 'markdown',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.xml': 'xml',
            '.sql': 'sql',
            '.sh': 'bash',
            '.bash': 'bash'
        }
        return language_map.get(extension, 'text')


class SmartContentProcessor:
    """智能内容处理器 - 根据存储策略处理内容"""
    
    def __init__(self):
        self.decision_engine = StorageDecisionEngine()
        logger.info("智能内容处理器初始化完成")
    
    def process_content(self, content: str, file_path: str, 
                       metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理内容
        
        Args:
            content: 原始内容
            file_path: 文件路径
            metadata: 额外元数据
        
        Returns:
            Dict: 处理后的数据项
        """
        # 获取存储决策
        decision = self.decision_engine.decide_storage_strategy(
            content, file_path, metadata
        )
        
        # 生成唯一ID
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
        item_id = f"smart_{int(datetime.now().timestamp() * 1000)}_{content_hash}"
        
        # 基础数据项 - 匹配DataItem模型字段
        original_size = len(content.encode('utf-8'))
        data_item = {
            "id": item_id,
            "source_connector": metadata.get("connector", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "storage_strategy": decision.strategy.value,
            "original_size": original_size,
            "meta_data": {**(metadata or {}), **decision.metadata},
            "processing_info": {
                "storage_reason": decision.reason,
                "decision_metadata": decision.metadata
            }
        }
        
        # 根据策略处理内容
        if decision.strategy == StorageStrategy.SKIP:
            processed_content = ""
            processing_success = False
            
        elif decision.strategy == StorageStrategy.EXTRACT_SEMANTICS:
            # 图片文件处理 (后续实现)
            processed_content = self._process_image_placeholder(content, file_path)
            processing_success = True
            
        elif decision.strategy == StorageStrategy.SUMMARIZE_ONLY:
            # 大文件摘要处理 (后续实现)
            processed_content = self._process_large_file_placeholder(content)
            processing_success = True
            
        elif decision.strategy == StorageStrategy.FULL_CONTENT:
            # 完整内容保存
            processed_content = content[:decision.max_content_size]
            processing_success = True
            
        elif decision.strategy == StorageStrategy.SMART_SAMPLE:
            # 智能采样
            processed_content = self._smart_sample_content(content, decision.max_content_size)
            processing_success = True
        else:
            processed_content = content
            processing_success = False
        
        # 设置处理后的内容和大小
        data_item["content"] = processed_content
        data_item["processed_size"] = len(processed_content.encode('utf-8'))
        data_item["processing_info"]["processing_success"] = processing_success
        data_item["processing_info"]["processing_timestamp"] = datetime.now().isoformat()
        
        logger.info(f"内容处理完成: {decision.strategy.value} - {Path(file_path).name}")
        return data_item
    
    def _process_image_placeholder(self, content: str, file_path: str) -> str:
        """图片处理占位符 (后续实现OCR和AI描述)"""
        return f"[图片文件] {Path(file_path).name} - 等待语义提取"
    
    def _process_large_file_placeholder(self, content: str) -> str:
        """大文件处理占位符 (后续实现AI摘要)"""
        # 简单的头尾采样作为临时方案
        head = content[:2000]
        tail = content[-2000:] if len(content) > 4000 else ""
        return f"{head}\n\n... [内容已截断] ...\n\n{tail}"
    
    def _smart_sample_content(self, content: str, max_size: int) -> str:
        """智能内容采样"""
        if len(content) <= max_size:
            return content
        
        # 头尾采样策略
        head_size = max_size // 2
        tail_size = max_size - head_size - 50  # 预留分隔符空间
        
        head = content[:head_size]
        tail = content[-tail_size:] if tail_size > 0 else ""
        
        return f"{head}\n\n... [智能采样，中间内容已省略] ...\n\n{tail}"


# 使用示例和测试
if __name__ == "__main__":
    # 初始化处理器
    processor = SmartContentProcessor()
    
    # 测试不同类型的文件
    test_cases = [
        # 小文本文件
        ("Hello world!", "test.txt", {"connector": "filesystem"}),
        # 大文本文件
        ("x" * 200000, "large.md", {"connector": "filesystem"}),
        # 图片文件
        ("binary_image_content", "image.jpg", {"connector": "filesystem"}),
        # 代码文件
        ("def hello():\n    print('Hello')", "script.py", {"connector": "filesystem"}),
        # 敏感文件
        ("secret_key=123", "secret.key", {"connector": "filesystem"})
    ]
    
    for content, file_path, metadata in test_cases:
        result = processor.process_content(content, file_path, metadata)
        print(f"\n文件: {file_path}")
        print(f"策略: {result['storage_strategy']}")
        print(f"原因: {result['storage_reason']}")
        print(f"内容长度: {len(result['content'])}")
        print(f"处理状态: {result['processed']}")