"""
AI驱动的事件关联IPC路由

提供基于Ollama AI的智能事件关联服务：
- AI语义理解：动态识别事件含义，无需硬编码
- AI模式发现：智能识别跨连接器工作流
- AI学习改进：从用户反馈中持续学习  
- AI解释说明：自然语言解释关联原因
"""

import logging
from typing import Any, Dict

from services.event_correlation.ai_driven_correlator import get_ai_correlator

logger = logging.getLogger(__name__)


async def handle_ai_analyze_event(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """AI分析单个事件
    
    路由: /ai/analyze-event
    请求参数:
    - event_data: 事件数据
    - include_suggestions: 是否包含建议 (默认true)
    """
    try:
        event_data = request_data.get('event_data', {})
        include_suggestions = request_data.get('include_suggestions', True)
        
        if not event_data:
            return {
                "success": False,
                "error": "缺少事件数据",
                "analysis": None
            }
        
        ai_correlator = get_ai_correlator()
        
        # AI分析事件
        analysis_result = await ai_correlator.process_event(event_data)
        
        # 构建响应
        response = {
            "success": True,
            "analysis": {
                "semantic_tags": [
                    {
                        "key": tag.key,
                        "name": tag.name, 
                        "description": tag.description,
                        "confidence": tag.confidence,
                        "reasoning": tag.reasoning
                    } for tag in analysis_result.get('semantic_tags', [])
                ],
                "discovered_correlations": [
                    {
                        "pattern_name": corr.pattern_name,
                        "description": corr.pattern_description,
                        "confidence": corr.confidence,
                        "reasoning": corr.reasoning,
                        "related_events_count": len(corr.related_events),
                        "suggested_actions": corr.suggested_actions if include_suggestions else []
                    } for corr in analysis_result.get('correlations', [])
                ],
                "ai_insights_available": analysis_result.get('ai_insights', False),
                "processing_timestamp": analysis_result.get('processed_at')
            }
        }
        
        return response
        
    except Exception as e:
        logger.error(f"AI事件分析失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "analysis": None
        }


async def handle_ai_explain_pattern(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """AI解释关联模式
    
    路由: /ai/explain-pattern
    请求参数:
    - pattern_name: 模式名称
    - user_question: 用户问题 (可选)
    """
    try:
        pattern_name = request_data.get('pattern_name')
        user_question = request_data.get('user_question', '为什么这些事件是相关的？')
        
        if not pattern_name:
            return {
                "success": False,
                "error": "缺少模式名称",
                "explanation": ""
            }
        
        ai_correlator = get_ai_correlator()
        
        # AI解释模式
        explanation = await ai_correlator.explain_pattern(pattern_name, user_question)
        
        return {
            "success": True,
            "pattern_name": pattern_name,
            "user_question": user_question,
            "explanation": explanation,
            "explanation_type": "ai_generated"
        }
        
    except Exception as e:
        logger.error(f"AI模式解释失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "explanation": f"AI解释服务暂时不可用: {e}"
        }


async def handle_ai_learn_feedback(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """AI学习用户反馈
    
    路由: /ai/learn-feedback  
    请求参数:
    - pattern_name: 模式名称
    - feedback: 用户反馈文本
    - rating: 评分 (1-5)
    - improvement_suggestions: 用户改进建议 (可选)
    """
    try:
        pattern_name = request_data.get('pattern_name')
        feedback = request_data.get('feedback', '')
        rating = request_data.get('rating', 3.0)
        
        if not pattern_name:
            return {
                "success": False,
                "error": "缺少模式名称",
                "learning_result": None
            }
        
        # 验证评分范围
        rating = max(1.0, min(5.0, float(rating)))
        
        ai_correlator = get_ai_correlator()
        
        # AI学习处理
        learning_result = await ai_correlator.learn_from_feedback(pattern_name, feedback, rating)
        
        return {
            "success": True,
            "pattern_name": pattern_name,
            "feedback_processed": True,
            "learning_result": {
                "feedback_analysis": learning_result.get('feedback_analysis', ''),
                "improvement_suggestions": learning_result.get('improvement_suggestions', []),
                "pattern_adjustments": learning_result.get('pattern_adjustments', ''),
                "future_considerations": learning_result.get('future_considerations', [])
            },
            "ai_learning_status": "feedback_integrated"
        }
        
    except Exception as e:
        logger.error(f"AI学习反馈失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "learning_result": None
        }


async def handle_ai_behavior_insights(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """AI行为洞察分析
    
    路由: /ai/behavior-insights
    请求参数:
    - time_range_hours: 分析时间范围（小时，默认24）
    - insight_level: 洞察详细程度 (basic/detailed，默认basic)
    """
    try:
        time_range_hours = request_data.get('time_range_hours', 24)
        insight_level = request_data.get('insight_level', 'basic')
        
        # 验证参数
        time_range_hours = max(1, min(168, int(time_range_hours)))  # 1小时到1周
        
        ai_correlator = get_ai_correlator()
        
        # AI生成行为洞察
        insights = await ai_correlator.get_ai_insights(time_range_hours)
        
        return {
            "success": True,
            "analysis_period": {
                "hours": time_range_hours,
                "insight_level": insight_level
            },
            "insights": insights,
            "ai_analysis_timestamp": insights.get('generated_at'),
            "insights_available": len(insights.get('insights', [])) > 0
        }
        
    except Exception as e:
        logger.error(f"AI行为洞察失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "insights": {"summary": "AI洞察服务暂时不可用"},
            "insights_available": False
        }


async def handle_ai_pattern_discovery(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """AI模式发现
    
    路由: /ai/discover-patterns
    请求参数:
    - events: 事件列表 (可选，如不提供则使用缓冲区事件)
    - discovery_mode: 发现模式 (recent/custom，默认recent)
    - min_confidence: 最小置信度 (默认0.5)
    """
    try:
        events = request_data.get('events', [])
        discovery_mode = request_data.get('discovery_mode', 'recent')
        min_confidence = request_data.get('min_confidence', 0.5)
        
        ai_correlator = get_ai_correlator()
        
        if discovery_mode == 'recent' or not events:
            # 使用AI关联器缓冲区中的最近事件
            recent_events = ai_correlator.event_buffer[-20:] if ai_correlator.event_buffer else []
            events_to_analyze = recent_events
        else:
            # 使用用户提供的事件
            events_to_analyze = events
        
        if len(events_to_analyze) < 2:
            return {
                "success": True,
                "discovered_patterns": [],
                "message": "事件数据不足，无法发现模式",
                "events_analyzed": len(events_to_analyze)
            }
        
        # AI发现模式
        correlations = await ai_correlator.ai_service.discover_correlations(events_to_analyze)
        
        # 过滤低置信度模式
        filtered_patterns = [
            corr for corr in correlations 
            if corr.confidence >= min_confidence
        ]
        
        return {
            "success": True,
            "discovery_mode": discovery_mode,
            "events_analyzed": len(events_to_analyze),
            "discovered_patterns": [
                {
                    "pattern_name": pattern.pattern_name,
                    "description": pattern.pattern_description,
                    "confidence": pattern.confidence,
                    "reasoning": pattern.reasoning,
                    "related_events_count": len(pattern.related_events),
                    "suggested_actions": pattern.suggested_actions,
                    "is_learned": pattern.learned_from_context
                } for pattern in filtered_patterns
            ],
            "patterns_count": len(filtered_patterns),
            "ai_discovery_successful": True
        }
        
    except Exception as e:
        logger.error(f"AI模式发现失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "discovered_patterns": [],
            "ai_discovery_successful": False
        }


async def handle_ai_correlation_chat(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """AI关联对话 - 自然语言查询关联信息
    
    路由: /ai/correlation-chat
    请求参数:
    - user_message: 用户消息
    - context: 对话上下文 (可选)
    """
    try:
        user_message = request_data.get('user_message', '')
        context = request_data.get('context', {})
        
        if not user_message.strip():
            return {
                "success": False,
                "error": "缺少用户消息",
                "ai_response": ""
            }
        
        ai_correlator = get_ai_correlator()
        
        # 构建对话提示
        chat_prompt = f"""
用户正在询问关于事件关联和行为模式的问题。

用户消息: {user_message}

当前上下文信息:
- 最近分析的事件数量: {len(ai_correlator.event_buffer)}
- 已发现的模式数量: {len(ai_correlator.correlation_cache)}
- 对话上下文: {context}

请以AI助手的身份回答用户问题，重点解释：
1. 事件关联和模式识别的原理
2. 具体的分析结果和发现
3. 对用户行为的洞察和建议
4. 如何更好地利用关联信息

请用自然、友好的语言回复，避免技术术语。
"""
        
        # AI生成对话响应
        ai_response = await ai_correlator.ai_service._call_ollama(chat_prompt)
        
        # 确保响应是字符串格式
        if isinstance(ai_response, dict):
            ai_response = ai_response.get('response', str(ai_response))
        
        return {
            "success": True,
            "user_message": user_message,
            "ai_response": str(ai_response),
            "response_type": "conversational",
            "context_used": bool(context),
            "conversation_id": context.get('conversation_id', 'new')
        }
        
    except Exception as e:
        logger.error(f"AI关联对话失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "ai_response": f"抱歉，AI对话服务暂时不可用。错误: {e}"
        }


# 路由注册
def get_ai_correlation_routes() -> Dict[str, Any]:
    """获取AI关联路由映射"""
    return {
        "/ai/analyze-event": handle_ai_analyze_event,
        "/ai/explain-pattern": handle_ai_explain_pattern,
        "/ai/learn-feedback": handle_ai_learn_feedback,
        "/ai/behavior-insights": handle_ai_behavior_insights,
        "/ai/discover-patterns": handle_ai_pattern_discovery,
        "/ai/correlation-chat": handle_ai_correlation_chat,
    }


def create_ai_correlation_router():
    """创建AI关联路由器"""
    from services.ipc.core.router import IPCRouter, RoutePattern
    
    router = IPCRouter(prefix="/ai")
    
    # 注册AI关联路由
    routes_mapping = get_ai_correlation_routes()
    
    # 将字典路由转换为IPC路由
    for path, handler in routes_mapping.items():
        # 根据路径确定HTTP方法
        method = "POST"  # AI功能通常需要POST请求
        if "get" in path.lower() or "list" in path.lower():
            method = "GET"
            
        # 创建异步包装器以适配IPCRouter接口
        def create_handler(handler_func):
            async def ipc_handler(request):
                from services.ipc.core.protocol import IPCResponse
                try:
                    # 调用原有的handler
                    result = await handler_func(request.data or {})
                    return IPCResponse(
                        success=result.get("success", True),
                        data=result,
                        message=result.get("message", "AI关联操作完成")
                    )
                except Exception as e:
                    return IPCResponse.error_response(
                        "AI_CORRELATION_ERROR",
                        f"AI关联操作失败: {e}",
                        details={"error_type": type(e).__name__}
                    )
            return ipc_handler
        
        # 注册路由
        pattern = RoutePattern(path, method)
        router.routes.append((pattern, create_handler(handler)))
    
    logger.info(f"AI Correlation router created with {len(routes_mapping)} endpoints")
    return router