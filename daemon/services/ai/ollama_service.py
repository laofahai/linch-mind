#!/usr/bin/env python3
"""
Ollama本地AI服务 - 内容价值评估和语义理解
使用本地Ollama模型实现AI驱动的智能存储过滤
"""

import asyncio
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import numpy as np

from core.error_handling import handle_errors, ErrorSeverity, ErrorCategory
from services.shared_executor_service import get_shared_executor_service
from config.intelligent_storage import get_config_manager

logger = logging.getLogger(__name__)


@dataclass
class ContentEvaluation:
    """内容评估结果"""
    value_score: float  # 0-1分，内容价值评分
    confidence: float   # 0-1分，评估可信度
    content_type: str   # 内容类型
    summary: str        # 100字摘要
    keywords: List[str] # 关键词列表
    entities: List[Dict[str, Any]]  # 提取的实体
    reasoning: str      # 评估推理过程


@dataclass
class OllamaMetrics:
    """Ollama服务性能指标"""
    total_evaluations: int
    avg_evaluation_time_ms: float
    avg_summary_time_ms: float
    avg_embedding_time_ms: float
    value_score_distribution: Dict[str, int]  # 分数区间分布
    content_type_distribution: Dict[str, int]
    memory_usage_mb: float
    last_updated: datetime


class OllamaService:
    """Ollama本地AI服务 - 智能内容评估和处理"""

    def __init__(
        self,
        ollama_host: Optional[str] = None,
        embedding_model: Optional[str] = None,
        llm_model: Optional[str] = None,
        value_threshold: Optional[float] = None,
        entity_threshold: Optional[float] = None,
        max_workers: int = 2,
    ):
        # 获取配置管理器
        config_manager = get_config_manager()
        
        # 使用配置系统 (参数 > 环境变量 > 配置文件)
        self.ollama_host = (ollama_host or config_manager.get_ollama_host()).rstrip('/')
        self.embedding_model = embedding_model or config_manager.get_embedding_model()
        self.llm_model = llm_model or config_manager.get_llm_model()
        self.value_threshold = value_threshold if value_threshold is not None else config_manager.get_value_threshold()
        self.entity_threshold = entity_threshold if entity_threshold is not None else config_manager.get_config().ollama.entity_threshold
        
        # 线程池管理
        self._executor = get_shared_executor_service()
        
        # HTTP客户端会话
        self._session: Optional[aiohttp.ClientSession] = None
        
        # 性能监控
        self._evaluation_times: List[float] = []
        self._summary_times: List[float] = []
        self._embedding_times: List[float] = []
        self._max_history = 100
        
        # 统计数据
        self._metrics = OllamaMetrics(
            total_evaluations=0,
            avg_evaluation_time_ms=0.0,
            avg_summary_time_ms=0.0,
            avg_embedding_time_ms=0.0,
            value_score_distribution={},
            content_type_distribution={},
            memory_usage_mb=0.0,
            last_updated=datetime.utcnow(),
        )
        
        # 服务可用性状态
        self._is_available = False

    async def initialize(self) -> bool:
        """初始化Ollama服务"""
        try:
            # 创建HTTP会话
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30, connect=5)
            )
            
            # 检查Ollama连接
            if not await self._check_ollama_connection():
                logger.error("无法连接到Ollama服务")
                return False
            
            # 检查模型可用性
            if not await self._check_models_available():
                logger.error("必需的Ollama模型不可用")
                return False
            
            # 预热模型
            await self._warmup_models()
            
            # 标记服务为可用
            self._is_available = True
            
            logger.info(f"Ollama服务初始化完成 - LLM: {self.llm_model}, Embedding: {self.embedding_model}")
            return True
            
        except Exception as e:
            logger.error(f"Ollama服务初始化失败: {e}")
            self._is_available = False
            return False

    async def close(self):
        """关闭Ollama服务"""
        try:
            if self._session:
                await self._session.close()
            self._is_available = False
            logger.info("Ollama服务已关闭")
        except Exception as e:
            logger.error(f"关闭Ollama服务失败: {e}")
            self._is_available = False

    def is_available(self) -> bool:
        """检查Ollama服务是否可用"""
        return self._is_available
    
    async def health_check(self) -> bool:
        """健康检查并更新可用性状态"""
        try:
            if not self._session:
                self._is_available = False
                return False
            
            # 检查连接状态
            is_healthy = await self._check_ollama_connection()
            self._is_available = is_healthy
            return is_healthy
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            self._is_available = False
            return False
    
    # === 连接和健康检查 ===

    async def _check_ollama_connection(self) -> bool:
        """检查Ollama服务连接"""
        try:
            async with self._session.get(f"{self.ollama_host}/api/tags") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Ollama连接检查失败: {e}")
            return False

    async def _check_models_available(self) -> bool:
        """检查必需模型是否可用"""
        try:
            async with self._session.get(f"{self.ollama_host}/api/tags") as response:
                if response.status != 200:
                    return False
                
                data = await response.json()
                available_models = {model["name"] for model in data.get("models", [])}
                
                # 检查必需模型
                required_models = {self.embedding_model, self.llm_model}
                missing_models = required_models - available_models
                
                if missing_models:
                    logger.error(f"缺少必需模型: {missing_models}")
                    logger.info(f"可用模型: {available_models}")
                    return False
                
                logger.info(f"已验证必需模型: {required_models}")
                return True
                
        except Exception as e:
            logger.error(f"模型可用性检查失败: {e}")
            return False

    async def _warmup_models(self):
        """预热模型"""
        try:
            logger.info("开始预热Ollama模型...")
            
            # 预热LLM模型
            await self._call_llm("预热测试", "请简短回复'模型已就绪'")
            
            # 预热嵌入模型
            await self.embed_text("预热测试文本")
            
            logger.info("模型预热完成")
            
        except Exception as e:
            logger.warning(f"模型预热失败: {e}")

    # === 核心AI功能 ===

    @handle_errors(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.AI_PROCESSING,
        user_message="内容价值评估失败",
        recovery_suggestions="检查Ollama服务状态"
    )
    async def evaluate_content_value(self, content: str) -> float:
        """
        AI驱动的内容价值评估
        
        Args:
            content: 待评估内容
            
        Returns:
            float: 0-1分，内容价值评分
        """
        if not content or not content.strip():
            return 0.0
        
        try:
            start_time = datetime.utcnow()
            
            # 构建评估提示词
            prompt = self._build_evaluation_prompt(content)
            
            # 调用LLM进行评估
            response = await self._call_llm(content, prompt)
            
            # 解析评估结果
            value_score = self._parse_value_score(response)
            
            # 记录性能
            evaluation_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._record_evaluation_time(evaluation_time)
            
            # 更新统计
            self._metrics.total_evaluations += 1
            self._update_score_distribution(value_score)
            
            logger.debug(f"内容价值评估完成: {value_score:.3f}, 耗时 {evaluation_time:.2f}ms")
            return value_score
            
        except Exception as e:
            logger.error(f"内容价值评估失败: {e}")
            return 0.0

    @handle_errors(
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.AI_PROCESSING,
        user_message="语义摘要提取失败"
    )
    async def extract_semantic_summary(self, content: str, max_length: int = 100) -> str:
        """
        提取语义摘要（替代原文存储）
        
        Args:
            content: 原始内容
            max_length: 最大摘要长度
            
        Returns:
            str: 100字以内的语义摘要
        """
        if not content or not content.strip():
            return ""
        
        try:
            start_time = datetime.utcnow()
            
            # 构建摘要提示词
            prompt = self._build_summary_prompt(content, max_length)
            
            # 调用LLM生成摘要
            summary = await self._call_llm(content, prompt)
            
            # 清理和验证摘要
            summary = self._clean_summary(summary, max_length)
            
            # 记录性能
            summary_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._record_summary_time(summary_time)
            
            logger.debug(f"语义摘要提取完成: {len(summary)} 字符, 耗时 {summary_time:.2f}ms")
            return summary
            
        except Exception as e:
            logger.error(f"语义摘要提取失败: {e}")
            # 返回截断的原文作为备用
            return content[:max_length] + "..." if len(content) > max_length else content

    @handle_errors(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.AI_PROCESSING,
        user_message="文本向量化失败"
    )
    async def embed_text(self, text: str) -> List[float]:
        """
        文本向量化（使用nomic-embed-text）
        
        Args:
            text: 待向量化文本
            
        Returns:
            List[float]: 384维向量
        """
        if not text or not text.strip():
            return [0.0] * 384  # 返回零向量
        
        try:
            start_time = datetime.utcnow()
            
            # 调用Ollama嵌入接口
            async with self._session.post(
                f"{self.ollama_host}/api/embeddings",
                json={
                    "model": self.embedding_model,
                    "prompt": text.strip()
                }
            ) as response:
                if response.status != 200:
                    logger.error(f"嵌入请求失败: HTTP {response.status}")
                    return [0.0] * 384
                
                data = await response.json()
                embedding = data.get("embedding", [])
                
                if not embedding:
                    logger.error("空的嵌入结果")
                    return [0.0] * 384
                
                # 记录性能
                embedding_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                self._record_embedding_time(embedding_time)
                
                logger.debug(f"文本向量化完成: {len(embedding)}维, 耗时 {embedding_time:.2f}ms")
                return embedding
                
        except Exception as e:
            logger.error(f"文本向量化失败: {e}")
            return [0.0] * 384

    @handle_errors(
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.AI_PROCESSING,
        user_message="实体提取失败"
    )
    async def extract_valuable_entities(self, content: str) -> List[Dict[str, Any]]:
        """
        提取高价值实体（仅在score>0.8时执行）
        
        Args:
            content: 原始内容
            
        Returns:
            List[Dict]: 实体列表
        """
        if not content or not content.strip():
            return []
        
        try:
            # 构建实体提取提示词
            prompt = self._build_entity_extraction_prompt(content)
            
            # 调用LLM提取实体
            response = await self._call_llm(content, prompt)
            
            # 解析实体结果
            entities = self._parse_entities(response)
            
            logger.debug(f"实体提取完成: {len(entities)} 个实体")
            return entities
            
        except Exception as e:
            logger.error(f"实体提取失败: {e}")
            return []

    # === 综合内容处理 ===

    async def process_content_comprehensive(self, content: str) -> ContentEvaluation:
        """
        综合内容处理 - 一次性完成所有评估
        
        Args:
            content: 原始内容
            
        Returns:
            ContentEvaluation: 完整的评估结果
        """
        if not content or not content.strip():
            return ContentEvaluation(
                value_score=0.0,
                confidence=1.0,
                content_type="empty",
                summary="",
                keywords=[],
                entities=[],
                reasoning="空内容"
            )
        
        try:
            # 并行执行多项任务
            tasks = [
                self.evaluate_content_value(content),
                self.extract_semantic_summary(content),
                self._detect_content_type(content),
                self._extract_keywords(content),
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            value_score = results[0] if not isinstance(results[0], Exception) else 0.0
            summary = results[1] if not isinstance(results[1], Exception) else content[:100]
            content_type = results[2] if not isinstance(results[2], Exception) else "text"
            keywords = results[3] if not isinstance(results[3], Exception) else []
            
            # 仅对高价值内容提取实体
            entities = []
            if value_score > self.entity_threshold:
                entities = await self.extract_valuable_entities(content)
            
            # 计算置信度
            confidence = min(1.0, 0.7 + (value_score * 0.3))
            
            return ContentEvaluation(
                value_score=value_score,
                confidence=confidence,
                content_type=content_type,
                summary=summary,
                keywords=keywords,
                entities=entities,
                reasoning=f"AI评估: 价值={value_score:.3f}, 类型={content_type}"
            )
            
        except Exception as e:
            logger.error(f"综合内容处理失败: {e}")
            return ContentEvaluation(
                value_score=0.0,
                confidence=0.0,
                content_type="error",
                summary=content[:100],
                keywords=[],
                entities=[],
                reasoning=f"处理失败: {str(e)}"
            )

    # === LLM调用接口 ===

    async def _call_llm(self, content: str, prompt: str) -> str:
        """调用LLM模型"""
        try:
            async with self._session.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.llm_model,
                    "prompt": prompt,
                    "system": "你是一个专业的内容分析AI，请严格按照要求格式回复。",
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # 低温度保证一致性
                        "top_p": 0.9,
                        "num_predict": 500,  # 限制输出长度
                    }
                }
            ) as response:
                if response.status != 200:
                    logger.error(f"LLM请求失败: HTTP {response.status}")
                    return ""
                
                data = await response.json()
                return data.get("response", "").strip()
                
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            return ""

    # === 提示词构建 ===

    def _build_evaluation_prompt(self, content: str) -> str:
        """构建内容价值评估提示词"""
        return f"""请对以下内容进行价值评估，评分范围0-1：

内容：
{content[:2000]}

评估标准：
- 0.0-0.2: 垃圾内容（广告、乱码、重复文本、无意义字符）
- 0.3-0.5: 低价值内容（临时信息、简单复制）
- 0.6-0.8: 有价值内容（有用信息、学习资料、工作相关）
- 0.9-1.0: 高价值内容（重要文档、创作内容、深度思考）

请只回复一个0-1之间的数字，不要解释。"""

    def _build_summary_prompt(self, content: str, max_length: int) -> str:
        """构建摘要提示词"""
        return f"""请为以下内容生成简洁的语义摘要，最多{max_length}字符：

内容：
{content[:3000]}

要求：
1. 保留核心信息和关键概念
2. 语言简洁精确
3. 不超过{max_length}字符
4. 只回复摘要内容，不要前缀

摘要："""

    def _build_entity_extraction_prompt(self, content: str) -> str:
        """构建实体提取提示词"""
        return f"""请从以下内容中提取重要实体，以JSON格式返回：

内容：
{content[:2000]}

提取类型：人名、地名、机构、技术术语、重要概念

格式：[{{"type": "实体类型", "name": "实体名称", "context": "上下文"}}]

只回复JSON数组，不要解释："""

    # === 结果解析 ===

    def _parse_value_score(self, response: str) -> float:
        """解析价值评分"""
        try:
            # 提取数字
            numbers = re.findall(r'(\d+\.?\d*)', response)
            if numbers:
                score = float(numbers[0])
                # 确保在0-1范围内
                if score > 1.0:
                    score = score / 10.0  # 可能是10分制
                return max(0.0, min(1.0, score))
            return 0.0
        except:
            return 0.0

    def _clean_summary(self, summary: str, max_length: int) -> str:
        """清理和验证摘要"""
        if not summary:
            return ""
        
        # 移除常见前缀
        prefixes = ["摘要：", "总结：", "概要：", "Summary:", "摘要:", "概要:"]
        for prefix in prefixes:
            if summary.startswith(prefix):
                summary = summary[len(prefix):].strip()
        
        # 截断到指定长度
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        return summary.strip()

    def _parse_entities(self, response: str) -> List[Dict[str, Any]]:
        """解析实体提取结果"""
        try:
            # 尝试解析JSON
            json_match = re.search(r'\[(.*?)\]', response, re.DOTALL)
            if json_match:
                json_str = f"[{json_match.group(1)}]"
                entities = json.loads(json_str)
                return entities if isinstance(entities, list) else []
            return []
        except:
            return []

    # === 辅助功能 ===

    async def _detect_content_type(self, content: str) -> str:
        """检测内容类型"""
        content_lower = content.lower()
        
        if re.match(r'^https?://', content):
            return "url"
        elif '/' in content or '\\' in content:
            return "file_path"
        elif '@' in content and '.' in content:
            return "email"
        elif re.search(r'\d{4}-\d{2}-\d{2}', content):
            return "date_info"
        elif len(content) > 1000:
            return "document"
        else:
            return "text"

    async def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词"""
        try:
            # 简单的关键词提取（可以后续用LLM优化）
            import re
            words = re.findall(r'\b\w{3,}\b', content.lower())
            # 简单频率统计
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # 返回前5个高频词
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in sorted_words[:5] if freq > 1]
        except:
            return []

    # === 性能监控 ===

    def _record_evaluation_time(self, time_ms: float):
        """记录评估时间"""
        self._evaluation_times.append(time_ms)
        if len(self._evaluation_times) > self._max_history:
            self._evaluation_times = self._evaluation_times[-self._max_history:]

    def _record_summary_time(self, time_ms: float):
        """记录摘要时间"""
        self._summary_times.append(time_ms)
        if len(self._summary_times) > self._max_history:
            self._summary_times = self._summary_times[-self._max_history:]

    def _record_embedding_time(self, time_ms: float):
        """记录嵌入时间"""
        self._embedding_times.append(time_ms)
        if len(self._embedding_times) > self._max_history:
            self._embedding_times = self._embedding_times[-self._max_history:]

    def _update_score_distribution(self, score: float):
        """更新分数分布统计"""
        if score < 0.3:
            bucket = "low"
        elif score < 0.6:
            bucket = "medium"
        elif score < 0.8:
            bucket = "high"
        else:
            bucket = "premium"
        
        self._metrics.value_score_distribution[bucket] = \
            self._metrics.value_score_distribution.get(bucket, 0) + 1

    async def get_metrics(self) -> OllamaMetrics:
        """获取性能指标"""
        await self._update_metrics()
        return self._metrics

    async def _update_metrics(self):
        """更新性能指标"""
        try:
            if self._evaluation_times:
                self._metrics.avg_evaluation_time_ms = np.mean(self._evaluation_times)
            if self._summary_times:
                self._metrics.avg_summary_time_ms = np.mean(self._summary_times)
            if self._embedding_times:
                self._metrics.avg_embedding_time_ms = np.mean(self._embedding_times)
            
            # 内存使用情况
            import psutil
            process = psutil.Process()
            self._metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024
            
            self._metrics.last_updated = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"更新指标失败: {e}")


# === 服务单例管理 ===

_ollama_service: Optional[OllamaService] = None

# 已删除：get_ollama_service() - 违反ServiceFacade统一服务获取铁律
# 请使用：from core.service_facade import get_service; get_service(OllamaService)

async def cleanup_ollama_service():
    """清理Ollama服务"""
    global _ollama_service
    if _ollama_service:
        await _ollama_service.close()
        _ollama_service = None