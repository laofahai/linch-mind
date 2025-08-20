"""
AI Services Module

提供基于本地AI模型的智能服务：
- Ollama集成服务
- 内容价值评估
- 语义摘要提取
- 文本向量化
- 实体识别
"""

from .ollama_service import OllamaService, cleanup_ollama_service

__all__ = [
    "OllamaService",
    "cleanup_ollama_service",
]