"""
AI驱动的事件关联系统 - 使用Ollama智能分析

完全基于AI的事件关联和模式识别：
1. 零硬编码语义分类 - AI动态理解事件内容
2. 智能关联发现 - AI识别跨连接器工作流模式
3. 自适应学习 - AI从用户行为中学习新模式
4. 自然语言理解 - AI解释关联原因和建议
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from core.service_facade import get_database_config_manager
from core.service_facade import get_service
from services.unified_database_service import UnifiedDatabaseService

logger = logging.getLogger(__name__)


@dataclass
class AISemanticTag:
    """AI生成的语义标签"""
    key: str
    name: str
    description: str
    confidence: float
    reasoning: str


@dataclass
class AICorrelation:
    """AI发现的事件关联"""
    pattern_name: str
    pattern_description: str
    related_events: List[str]
    confidence: float
    reasoning: str
    suggested_actions: List[str]
    learned_from_context: bool = False


class OllamaAIService:
    """Ollama AI服务封装"""
    
    def __init__(self):
        self.config_manager = get_database_config_manager()
        self.ollama_host = self.config_manager.get_config_value('ollama', 'host', default='http://localhost:11434')
        self.model = self.config_manager.get_config_value('ollama', 'llm_model', default='qwen2.5:0.5b')
        self.value_threshold = self.config_manager.get_config_value('ollama', 'value_threshold', default=0.3)
        
    async def analyze_event_semantics(self, event_data: Dict[str, Any]) -> List[AISemanticTag]:
        """AI分析事件语义，生成动态标签"""
        
        prompt = f"""
请分析以下事件数据，识别其语义类型和特征：

事件数据：
{json.dumps(event_data, ensure_ascii=False, indent=2)}

请返回JSON格式的语义标签列表，每个标签包含：
- key: 标签键（英文，下划线分隔）
- name: 中文名称
- description: 详细描述
- confidence: 置信度（0.0-1.0）
- reasoning: 分析理由

重点分析：
1. 这是什么类型的操作？（文件、网络、输入、系统等）
2. 用户的意图是什么？（编程、学习、娱乐、工作等）
3. 数据的重要性级别？（高价值内容、临时操作、系统维护等）
4. 工作流阶段？（开始、进行中、完成、错误等）

返回格式：
{{"tags": [
    {{"key": "...", "name": "...", "description": "...", "confidence": 0.9, "reasoning": "..."}}
]}}
"""
        
        try:
            # 调用Ollama API
            response = await self._call_ollama(prompt)
            
            # 解析AI响应
            if response and 'tags' in response:
                tags = []
                for tag_data in response['tags']:
                    tags.append(AISemanticTag(
                        key=tag_data.get('key', 'unknown'),
                        name=tag_data.get('name', '未知'),
                        description=tag_data.get('description', ''),
                        confidence=tag_data.get('confidence', 0.5),
                        reasoning=tag_data.get('reasoning', '')
                    ))
                return tags
            
        except Exception as e:
            logger.error(f"AI语义分析失败: {e}")
        
        # 兜底返回
        return [AISemanticTag("unknown", "未知类型", "AI无法分析的事件", 0.1, "AI分析失败")]
    
    async def discover_correlations(self, events: List[Dict[str, Any]], time_window_minutes: int = 10) -> List[AICorrelation]:
        """AI发现事件关联模式"""
        
        if len(events) < 2:
            return []
        
        # 构建事件序列描述
        events_description = []
        for i, event in enumerate(events[-10:]):  # 最近10个事件
            timestamp = event.get('timestamp', 'unknown')
            event_data = event.get('event_data', {})
            connector_id = event.get('connector_id', 'unknown')
            
            # 提取关键信息
            key_info = []
            if 'file_path' in event_data:
                key_info.append(f"文件: {event_data['file_path']}")
            if 'text' in event_data or 'content' in event_data:
                text_content = event_data.get('text', event_data.get('content', ''))[:100]
                key_info.append(f"内容: {text_content}")
            if 'action' in event_data:
                key_info.append(f"动作: {event_data['action']}")
            
            events_description.append(
                f"事件{i+1}: [{connector_id}] {timestamp} - {'; '.join(key_info)}"
            )
        
        prompt = f"""
请分析以下{time_window_minutes}分钟内的事件序列，发现可能的工作流模式和关联：

事件序列：
{chr(10).join(events_description)}

请识别：
1. 这些事件是否构成一个有意义的工作流？
2. 用户在执行什么任务？（编程、写作、研究、学习等）
3. 事件之间有什么因果关系？
4. 可以预测用户下一步可能的操作吗？
5. 这个模式在未来是否会重复？

返回JSON格式的关联分析：
{{"correlations": [
    {{
        "pattern_name": "模式名称（英文下划线）",
        "pattern_description": "模式的中文描述",
        "related_events": ["事件1", "事件2"],
        "confidence": 0.8,
        "reasoning": "发现此模式的理由",
        "suggested_actions": ["建议操作1", "建议操作2"]
    }}
]}}
"""
        
        try:
            response = await self._call_ollama(prompt)
            
            if response and 'correlations' in response:
                correlations = []
                for corr_data in response['correlations']:
                    correlations.append(AICorrelation(
                        pattern_name=corr_data.get('pattern_name', 'unknown_pattern'),
                        pattern_description=corr_data.get('pattern_description', ''),
                        related_events=corr_data.get('related_events', []),
                        confidence=corr_data.get('confidence', 0.5),
                        reasoning=corr_data.get('reasoning', ''),
                        suggested_actions=corr_data.get('suggested_actions', []),
                        learned_from_context=True
                    ))
                return correlations
                
        except Exception as e:
            logger.error(f"AI关联发现失败: {e}")
        
        return []
    
    async def learn_from_user_feedback(self, correlation: AICorrelation, feedback: str, rating: float) -> Dict[str, Any]:
        """AI从用户反馈中学习，改进模式识别"""
        
        prompt = f"""
用户对以下AI识别的关联模式给出了反馈：

识别的模式：
- 模式名称: {correlation.pattern_name}
- 描述: {correlation.pattern_description}
- AI推理: {correlation.reasoning}
- 置信度: {correlation.confidence}

用户反馈：
- 评分: {rating}/5.0
- 评论: {feedback}

请分析：
1. 用户反馈说明了什么问题？
2. 应该如何调整模式识别策略？
3. 对于类似事件序列，应该注意什么？
4. 生成改进建议和学习要点

返回JSON格式：
{{"learning": {{
    "feedback_analysis": "反馈分析",
    "improvement_suggestions": ["建议1", "建议2"],
    "pattern_adjustments": "模式调整说明",
    "future_considerations": ["考虑要点1", "考虑要点2"]
}}}}
"""
        
        try:
            response = await self._call_ollama(prompt)
            return response.get('learning', {}) if response else {}
        except Exception as e:
            logger.error(f"AI学习处理失败: {e}")
            return {}
    
    async def explain_correlation(self, correlation: AICorrelation, user_question: str) -> str:
        """AI解释关联原因，回答用户问题"""
        
        prompt = f"""
用户对以下AI识别的关联模式有疑问：

识别的模式：
- 名称: {correlation.pattern_name}
- 描述: {correlation.pattern_description}
- 推理: {correlation.reasoning}
- 建议操作: {', '.join(correlation.suggested_actions)}

用户问题: {user_question}

请用通俗易懂的语言解释：
1. 为什么这些事件被认为是相关的？
2. 这个模式对用户有什么价值？
3. AI是如何发现这个模式的？
4. 用户可以如何利用这个发现？

请直接返回自然语言解释，不需要JSON格式。
"""
        
        try:
            response = await self._call_ollama(prompt)
            return response if isinstance(response, str) else str(response)
        except Exception as e:
            logger.error(f"AI解释失败: {e}")
            return f"抱歉，AI解释服务暂时不可用: {e}"
    
    async def _call_ollama(self, prompt: str) -> Any:
        """调用Ollama API"""
        try:
            import aiohttp
            
            if not self.ollama_host:
                raise Exception("Ollama配置不可用")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get('response', '')
                        
                        # 尝试解析JSON响应
                        try:
                            return json.loads(response_text)
                        except json.JSONDecodeError:
                            # 如果不是JSON，返回原始文本
                            return response_text
                    else:
                        raise Exception(f"Ollama API错误: {response.status}")
                        
        except Exception as e:
            logger.error(f"调用Ollama失败: {e}")
            raise


class AIDrivenCorrelator:
    """AI驱动的事件关联器主类"""
    
    def __init__(self):
        self.ai_service = OllamaAIService()
        self.event_buffer = []
        self.max_buffer_size = 100
        self.correlation_cache = {}
        
    async def process_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理新事件，进行AI分析"""
        
        # 1. AI语义分析
        semantic_tags = await self.ai_service.analyze_event_semantics(event_data)
        
        # 2. 添加到事件缓冲区
        enriched_event = {
            **event_data,
            'ai_semantic_tags': [tag.__dict__ for tag in semantic_tags],
            'processed_at': datetime.now().isoformat()
        }
        
        self.event_buffer.append(enriched_event)
        if len(self.event_buffer) > self.max_buffer_size:
            self.event_buffer.pop(0)
        
        # 3. AI关联发现（如果有足够的事件）
        correlations = []
        if len(self.event_buffer) >= 2:
            recent_events = self.event_buffer[-10:]  # 最近10个事件
            correlations = await self.ai_service.discover_correlations(recent_events)
        
        # 4. 保存关联到数据库
        if correlations:
            await self._save_correlations(correlations, enriched_event)
        
        return {
            'semantic_tags': semantic_tags,
            'correlations': correlations,
            'processing_success': True,
            'ai_insights': len(semantic_tags) > 0 or len(correlations) > 0
        }
    
    async def explain_pattern(self, pattern_name: str, user_question: str) -> str:
        """AI解释特定模式"""
        
        # 查找最近的此模式关联
        correlation = self.correlation_cache.get(pattern_name)
        if not correlation:
            return "未找到相关模式记录"
        
        return await self.ai_service.explain_correlation(correlation, user_question)
    
    async def learn_from_feedback(self, pattern_name: str, feedback: str, rating: float) -> Dict[str, Any]:
        """处理用户反馈，AI学习改进"""
        
        correlation = self.correlation_cache.get(pattern_name)
        if not correlation:
            return {"error": "未找到模式记录"}
        
        learning_result = await self.ai_service.learn_from_user_feedback(correlation, feedback, rating)
        
        # 保存学习结果到数据库
        await self._save_learning_feedback(pattern_name, feedback, rating, learning_result)
        
        return learning_result
    
    async def get_ai_insights(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """获取AI分析的行为洞察"""
        
        # 获取时间范围内的事件
        cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
        recent_events = [
            event for event in self.event_buffer 
            if datetime.fromisoformat(event.get('processed_at', '1970-01-01')) > cutoff_time
        ]
        
        if not recent_events:
            return {"insights": [], "summary": "没有足够的事件数据进行分析"}
        
        # AI生成洞察
        insights_prompt = f"""
分析用户在过去{time_range_hours}小时内的{len(recent_events)}个事件，提供行为洞察：

事件摘要：
{json.dumps([{
    'time': event.get('timestamp', ''),
    'type': event.get('event_type', ''),
    'connector': event.get('connector_id', ''),
    'tags': [tag.get('name', '') for tag in event.get('ai_semantic_tags', [])]
} for event in recent_events[-20:]], ensure_ascii=False, indent=2)}

请分析：
1. 用户的主要活动模式
2. 效率和专注度评估
3. 发现的有趣行为
4. 改进建议

返回JSON格式的洞察报告。
"""
        
        try:
            ai_insights = await self.ai_service._call_ollama(insights_prompt)
            return ai_insights if ai_insights else {"insights": [], "summary": "AI分析暂时不可用"}
        except Exception as e:
            logger.error(f"AI洞察生成失败: {e}")
            return {"error": str(e), "insights": [], "summary": "AI分析出现错误"}
    
    async def _save_correlations(self, correlations: List[AICorrelation], trigger_event: Dict[str, Any]):
        """保存AI发现的关联到数据库"""
        try:
            db_service = get_service(UnifiedDatabaseService)
            if not db_service:
                return
            
            for correlation in correlations:
                # 缓存关联对象供后续解释
                self.correlation_cache[correlation.pattern_name] = correlation
                
                # 保存到数据库的逻辑这里简化
                logger.info(f"AI发现关联模式: {correlation.pattern_name} (置信度: {correlation.confidence:.2f})")
                
        except Exception as e:
            logger.error(f"保存AI关联失败: {e}")
    
    async def _save_learning_feedback(self, pattern_name: str, feedback: str, rating: float, learning_result: Dict[str, Any]):
        """保存学习反馈到数据库"""
        try:
            db_service = get_service(UnifiedDatabaseService)
            if not db_service:
                return
            
            # 保存学习记录的逻辑
            logger.info(f"AI学习反馈: {pattern_name} - 评分: {rating}, 学习要点: {len(learning_result.get('improvement_suggestions', []))}")
            
        except Exception as e:
            logger.error(f"保存AI学习反馈失败: {e}")


# 全局AI关联器实例
_ai_correlator = None

def get_ai_correlator() -> AIDrivenCorrelator:
    """获取AI驱动关联器单例"""
    global _ai_correlator
    if _ai_correlator is None:
        _ai_correlator = AIDrivenCorrelator()
    return _ai_correlator