"""
数据洞察API服务 - 提供智能数据分析和查询功能
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import json
import re
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from core.service_facade import get_service
from models.database_models import EntityMetadata


class DataInsightsService:
    """数据洞察服务 - 提供智能分析数据的查询和聚合功能"""

    def __init__(self):
        # 使用UnifiedDatabaseService（已在容器中注册）
        from services.unified_database_service import UnifiedDatabaseService
        self.db_service = get_service(UnifiedDatabaseService)

    def get_dashboard_overview(self) -> Dict[str, Any]:
        """获取仪表板概览数据"""
        if self.db_service is None:
            raise ValueError("数据库服务未初始化")
        
        try:
            with self.db_service.get_session() as session:
                # 总实体数量
                total_entities = session.query(EntityMetadata).count()
                
                # 今日新增实体数量
                today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
                today_entities = session.query(EntityMetadata).filter(
                    EntityMetadata.created_at >= today
                ).count()
                
                # 按类型统计
                type_stats = {}
                entities = session.query(EntityMetadata).all()
                
                url_count = 0
                email_count = 0
                phone_count = 0
                file_count = 0
                keyword_count = 0
                
                for entity in entities:
                    try:
                        if entity and entity.properties and isinstance(entity.properties, dict):
                            content_analysis = entity.properties.get('content_analysis', {})
                            if content_analysis and isinstance(content_analysis, dict):
                                entities_data = content_analysis.get('entities', {})
                                if entities_data and isinstance(entities_data, dict):
                                    url_count += len(entities_data.get('urls', []))
                                    email_count += len(entities_data.get('emails', []))
                                    phone_count += len(entities_data.get('phones', []))
                                    file_count += len(entities_data.get('file_paths', []))
                                keywords = content_analysis.get('keywords', [])
                                if keywords and isinstance(keywords, list):
                                    keyword_count += len(keywords)
                    except Exception as e:
                        # 跳过有问题的实体，继续处理其他实体
                        continue
                
                return {
                    'total_entities': total_entities,
                    'today_entities': today_entities,
                    'growth_rate': round((today_entities / max(total_entities - today_entities, 1)) * 100, 1),
                    'entity_types': {
                        'urls': url_count,
                        'emails': email_count,
                        'phones': phone_count,
                        'files': file_count,
                        'keywords': keyword_count
                    },
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
        except Exception as e:
            # 详细错误记录
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"获取仪表板概览时出错: {e}", exc_info=True)
            raise

    def get_ai_insights(self) -> Dict[str, Any]:
        """获取AI智能洞察"""
        with self.db_service.get_session() as session:
            entities = session.query(EntityMetadata).order_by(desc(EntityMetadata.created_at)).limit(20).all()
            
            # 分析数据模式
            work_patterns = self._analyze_work_patterns(entities)
            content_categories = self._analyze_content_categories(entities)
            productivity_insights = self._analyze_productivity_patterns(entities)
            
            return {
                'work_patterns': work_patterns,
                'content_categories': content_categories,
                'productivity_insights': productivity_insights,
                'confidence_score': 0.85,  # AI分析置信度
                'last_analysis': datetime.now(timezone.utc).isoformat()
            }

    def get_entities_by_type(self, entity_type: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """按类型获取实体数据"""
        with self.db_service.get_session() as session:
            entities = session.query(EntityMetadata).order_by(desc(EntityMetadata.created_at)).offset(offset).limit(limit).all()
            
            filtered_entities = []
            
            for entity in entities:
                if entity.properties and isinstance(entity.properties, dict):
                    content_analysis = entity.properties.get('content_analysis', {})
                    entities_data = content_analysis.get('entities', {})
                    
                    # 根据类型筛选数据
                    if entity_type == 'urls' and entities_data.get('urls'):
                        for url in entities_data['urls']:
                            filtered_entities.append({
                                'id': f"{entity.entity_id}_url_{len(filtered_entities)}",
                                'type': 'url',
                                'content': url,
                                'source': 'clipboard',
                                'timestamp': entity.created_at.isoformat(),
                                'metadata': {
                                    'domain': self._extract_domain(url),
                                    'is_secure': url.startswith('https')
                                }
                            })
                    
                    elif entity_type == 'emails' and entities_data.get('emails'):
                        for email in entities_data['emails']:
                            filtered_entities.append({
                                'id': f"{entity.entity_id}_email_{len(filtered_entities)}",
                                'type': 'email',
                                'content': email,
                                'source': 'clipboard',
                                'timestamp': entity.created_at.isoformat(),
                                'metadata': {
                                    'domain': email.split('@')[1] if '@' in email else '',
                                    'is_business': self._is_business_email(email)
                                }
                            })
                    
                    elif entity_type == 'phones' and entities_data.get('phones'):
                        for phone in entities_data['phones']:
                            filtered_entities.append({
                                'id': f"{entity.entity_id}_phone_{len(filtered_entities)}",
                                'type': 'phone',
                                'content': phone,
                                'source': 'clipboard',
                                'timestamp': entity.created_at.isoformat(),
                                'metadata': {
                                    'formatted': self._format_phone(phone),
                                    'country_code': self._extract_country_code(phone)
                                }
                            })
                    
                    elif entity_type == 'files' and entities_data.get('file_paths'):
                        for file_path in entities_data['file_paths']:
                            if '/' in file_path or '\\' in file_path:  # 只包含真实文件路径
                                filtered_entities.append({
                                    'id': f"{entity.entity_id}_file_{len(filtered_entities)}",
                                    'type': 'file',
                                    'content': file_path,
                                    'source': 'clipboard',
                                    'timestamp': entity.created_at.isoformat(),
                                    'metadata': {
                                        'extension': self._extract_extension(file_path),
                                        'is_absolute': file_path.startswith('/') or (len(file_path) > 1 and file_path[1] == ':')
                                    }
                                })
            
            return {
                'entities': filtered_entities[:limit],
                'total': len(filtered_entities),
                'has_more': len(filtered_entities) > limit
            }

    def get_activity_timeline(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取活动时间线"""
        with self.db_service.get_session() as session:
            entities = session.query(EntityMetadata).order_by(desc(EntityMetadata.created_at)).limit(limit).all()
            
            timeline = []
            for entity in entities:
                if entity.properties and isinstance(entity.properties, dict):
                    content_analysis = entity.properties.get('content_analysis', {})
                    entities_data = content_analysis.get('entities', {})
                    
                    # 生成活动描述
                    activity_type = "数据采集"
                    description = "系统采集到新的内容"
                    details = []
                    
                    if entities_data.get('urls'):
                        details.append(f"{len(entities_data['urls'])} 个链接")
                    if entities_data.get('emails'):
                        details.append(f"{len(entities_data['emails'])} 个邮箱")
                    if entities_data.get('phones'):
                        details.append(f"{len(entities_data['phones'])} 个电话")
                    if entities_data.get('file_paths'):
                        details.append(f"{len(entities_data['file_paths'])} 个文件路径")
                    
                    if details:
                        description = f"智能识别: {', '.join(details)}"
                        activity_type = "智能分析"
                    
                    timeline.append({
                        'id': entity.entity_id,
                        'type': activity_type,
                        'description': description,
                        'timestamp': entity.created_at.isoformat(),
                        'source': 'clipboard_connector',
                        'metadata': {
                            'category': content_analysis.get('content_category', 'unknown'),
                            'entities_count': sum([
                                len(entities_data.get('urls', [])),
                                len(entities_data.get('emails', [])),
                                len(entities_data.get('phones', [])),
                                len(entities_data.get('file_paths', []))
                            ])
                        }
                    })
            
            return timeline

    def search_entities(self, query: str, entity_type: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索实体"""
        with self.db_service.get_session() as session:
            entities = session.query(EntityMetadata).order_by(desc(EntityMetadata.created_at)).limit(100).all()
            
            results = []
            query_lower = query.lower()
            
            for entity in entities:
                if entity.properties and isinstance(entity.properties, dict):
                    content_analysis = entity.properties.get('content_analysis', {})
                    entities_data = content_analysis.get('entities', {})
                    keywords = content_analysis.get('keywords', [])
                    
                    # 搜索匹配
                    matched = False
                    match_score = 0
                    
                    # 搜索关键词
                    for keyword in keywords:
                        if query_lower in keyword.lower():
                            matched = True
                            match_score += 10
                    
                    # 搜索实体内容
                    for entity_list in entities_data.values():
                        if isinstance(entity_list, list):
                            for item in entity_list:
                                if query_lower in str(item).lower():
                                    matched = True
                                    match_score += 20
                    
                    if matched:
                        results.append({
                            'id': entity.entity_id,
                            'content': str(entity.name)[:100] + "..." if len(str(entity.name)) > 100 else str(entity.name),
                            'type': entity.type,
                            'score': match_score,
                            'timestamp': entity.created_at.isoformat(),
                            'keywords': keywords[:5],  # 显示前5个关键词
                            'entities_summary': {
                                'urls': len(entities_data.get('urls', [])),
                                'emails': len(entities_data.get('emails', [])),
                                'phones': len(entities_data.get('phones', [])),
                                'files': len(entities_data.get('file_paths', []))
                            }
                        })
            
            # 按匹配分数排序
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:limit]

    def _analyze_work_patterns(self, entities: List[EntityMetadata]) -> Dict[str, Any]:
        """分析工作模式"""
        work_hours = {}
        content_categories = {}
        
        for entity in entities:
            if entity.properties and isinstance(entity.properties, dict):
                # 分析时间模式
                created_hour = entity.created_at.hour
                work_hours[created_hour] = work_hours.get(created_hour, 0) + 1
                
                # 分析内容类别
                content_analysis = entity.properties.get('content_analysis', {})
                category = content_analysis.get('content_category', 'unknown')
                content_categories[category] = content_categories.get(category, 0) + 1
        
        # 确定主要工作时间
        peak_hour = max(work_hours.items(), key=lambda x: x[1])[0] if work_hours else 9
        
        # 确定主要工作模式
        if content_categories.get('code_repository', 0) > 0:
            primary_mode = "开发工作"
        elif content_categories.get('file_path', 0) > 0:
            primary_mode = "文件管理"
        else:
            primary_mode = "常规办公"
        
        return {
            'primary_work_mode': primary_mode,
            'peak_activity_hour': peak_hour,
            'work_time_distribution': work_hours,
            'content_distribution': content_categories,
            'detected_patterns': [
                f"主要在 {peak_hour}:00 时段活跃",
                f"主要进行 {primary_mode} 相关活动"
            ]
        }

    def _analyze_content_categories(self, entities: List[EntityMetadata]) -> Dict[str, Any]:
        """分析内容类别"""
        categories = {}
        domains = {}
        
        for entity in entities:
            if entity.properties and isinstance(entity.properties, dict):
                content_analysis = entity.properties.get('content_analysis', {})
                entities_data = content_analysis.get('entities', {})
                
                # 统计URL域名
                for url in entities_data.get('urls', []):
                    domain = self._extract_domain(url)
                    if domain:
                        domains[domain] = domains.get(domain, 0) + 1
                
                # 统计内容类别
                category = content_analysis.get('content_category', 'unknown')
                categories[category] = categories.get(category, 0) + 1
        
        return {
            'content_categories': categories,
            'popular_domains': dict(sorted(domains.items(), key=lambda x: x[1], reverse=True)[:5]),
            'learning_topics': self._extract_learning_topics(domains),
            'productivity_focus': max(categories.items(), key=lambda x: x[1])[0] if categories else 'unknown'
        }

    def _analyze_productivity_patterns(self, entities: List[EntityMetadata]) -> Dict[str, Any]:
        """分析生产力模式"""
        daily_activity = {}
        efficiency_score = 0.7  # 模拟效率分数
        
        for entity in entities:
            day = entity.created_at.date()
            daily_activity[str(day)] = daily_activity.get(str(day), 0) + 1
        
        return {
            'daily_activity': daily_activity,
            'efficiency_score': efficiency_score,
            'productivity_trend': 'stable',  # 可以是 increasing, decreasing, stable
            'recommendations': [
                "保持当前的工作节奏",
                "建议在高峰时段专注重要任务",
                "可以考虑整理常用的链接和文件"
            ]
        }

    def _extract_domain(self, url: str) -> str:
        """提取URL域名"""
        match = re.search(r'://([^/]+)', url)
        return match.group(1) if match else ''

    def _is_business_email(self, email: str) -> bool:
        """判断是否为商务邮箱"""
        business_domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'qq.com', '163.com']
        domain = email.split('@')[1] if '@' in email else ''
        return domain not in business_domains

    def _format_phone(self, phone: str) -> str:
        """格式化电话号码"""
        digits = re.sub(r'\D', '', phone)
        if len(digits) == 11 and digits.startswith('1'):
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        elif len(digits) == 10:
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        return phone

    def _extract_country_code(self, phone: str) -> str:
        """提取国家代码"""
        if phone.startswith('+1'):
            return '+1'
        elif phone.startswith('+86'):
            return '+86'
        return ''

    def _extract_extension(self, file_path: str) -> str:
        """提取文件扩展名"""
        match = re.search(r'\.([^./\\]+)$', file_path)
        return match.group(1) if match else ''

    def _extract_learning_topics(self, domains: Dict[str, int]) -> List[str]:
        """提取学习主题"""
        learning_indicators = {
            'github.com': '代码开发',
            'stackoverflow.com': '编程问题',
            'docs.microsoft.com': '技术文档',
            'developer.mozilla.org': 'Web开发',
            'python.org': 'Python编程',
            'medium.com': '技术文章'
        }
        
        topics = []
        for domain, count in domains.items():
            if domain in learning_indicators:
                topics.append(learning_indicators[domain])
        
        return topics[:3]  # 返回前3个主题


# 服务实例化函数
def get_data_insights_service() -> DataInsightsService:
    """获取数据洞察服务实例"""
    try:
        # 直接创建实例，它会在__init__中通过ServiceFacade获取正确的数据库服务
        return DataInsightsService()
        
    except Exception as e:
        # 如果初始化失败，记录错误并抛出异常
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"DataInsightsService初始化失败: {e}")
        raise RuntimeError(f"数据洞察服务初始化失败: {e}") from e