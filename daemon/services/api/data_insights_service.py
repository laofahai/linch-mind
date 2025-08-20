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

    # 实体类型处理配置 - 支持扩展
    ENTITY_TYPE_CONFIG = {
        'urls': {
            'data_key': 'urls',
            'type_name': 'url',
            'metadata_extractor': '_extract_url_metadata'
        },
        'emails': {
            'data_key': 'emails',
            'type_name': 'email',
            'metadata_extractor': '_extract_email_metadata'
        },
        'phones': {
            'data_key': 'phones',
            'type_name': 'phone',
            'metadata_extractor': '_extract_phone_metadata'
        },
        'files': {
            'data_key': 'file_paths',
            'type_name': 'file',
            'metadata_extractor': '_extract_file_metadata',
            'content_filter': lambda content: '/' in content or '\\' in content
        }
    }

    def __init__(self):
        # 使用UnifiedDatabaseService（已在容器中注册）
        from services.storage.core.database import UnifiedDatabaseService
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

    def get_complete_insights_overview(self) -> Dict[str, Any]:
        """获取完整的数据洞察概览 - 整合所有UI层需要的数据"""
        try:
            with self.db_service.get_session() as session:
                # 获取基础数据
                dashboard_data = self.get_dashboard_overview()
                ai_insights_data = self.get_ai_insights()
                timeline_data = self.get_activity_timeline(10)
                
                # 构建UI层期望的完整概览结构
                overview = {
                    "todayStats": {
                        "newEntities": dashboard_data.get("today_entities", 0),
                        "activeConnectors": 2,  # 硬编码，从连接器状态获取
                        "aiAnalysisCompleted": dashboard_data.get("total_entities", 0),
                        "knowledgeConnections": int(dashboard_data.get("total_entities", 0) * 0.3)
                    },
                    "entityBreakdown": {
                        "url": dashboard_data.get("entity_types", {}).get("urls", 0),
                        "filePath": dashboard_data.get("entity_types", {}).get("files", 0),
                        "email": dashboard_data.get("entity_types", {}).get("emails", 0),
                        "phone": dashboard_data.get("entity_types", {}).get("phones", 0),
                        "keyword": dashboard_data.get("entity_types", {}).get("keywords", 0),
                        "other": 0
                    },
                    "recentInsights": self._generate_ai_insights(ai_insights_data),
                    "trendingEntities": self._generate_trending_entities(ai_insights_data),
                    "recentActivities": timeline_data,
                    "connectorStatuses": self._get_connector_statuses(),
                    "lastUpdated": datetime.now(timezone.utc).isoformat()
                }
                
                return overview
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"获取完整洞察概览时出错: {e}", exc_info=True)
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
                    
                    # 使用配置驱动的方式处理实体类型筛选
                    type_config = self.ENTITY_TYPE_CONFIG.get(entity_type)
                    if type_config and entities_data.get(type_config['data_key']):
                        entity_items = entities_data[type_config['data_key']]
                        
                        for item in entity_items:
                            # 应用内容过滤器（如果配置了）
                            if 'content_filter' in type_config:
                                if not type_config['content_filter'](item):
                                    continue
                            
                            # 提取元数据
                            metadata = self._extract_entity_metadata(item, type_config['metadata_extractor'])
                            
                            filtered_entities.append({
                                'id': f"{entity.entity_id}_{type_config['type_name']}_{len(filtered_entities)}",
                                'type': type_config['type_name'],
                                'content': item,
                                'source': 'clipboard',
                                'timestamp': entity.created_at.isoformat(),
                                'metadata': metadata
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
                    
                    # 从数据库中动态获取数据源，而不是硬编码连接器名称
                    data_source = entity.properties.get('source_type', 'unknown') if entity.properties else 'unknown'
                    
                    timeline.append({
                        'id': entity.entity_id,
                        'type': activity_type,
                        'description': description,
                        'timestamp': entity.created_at.isoformat(),
                        'source': data_source,
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

    def _extract_entity_metadata(self, content: str, extractor_method: str) -> Dict[str, Any]:
        """通用实体元数据提取器"""
        if hasattr(self, extractor_method):
            return getattr(self, extractor_method)(content)
        return {}
    
    def _extract_url_metadata(self, url: str) -> Dict[str, Any]:
        """提取URL元数据"""
        return {
            'domain': self._extract_domain(url),
            'is_secure': url.startswith('https')
        }
    
    def _extract_email_metadata(self, email: str) -> Dict[str, Any]:
        """提取邮箱元数据"""
        return {
            'domain': email.split('@')[1] if '@' in email else '',
            'is_business': self._is_business_email(email)
        }
    
    def _extract_phone_metadata(self, phone: str) -> Dict[str, Any]:
        """提取电话号码元数据"""
        return {
            'formatted': self._format_phone(phone),
            'country_code': self._extract_country_code(phone)
        }
    
    def _extract_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """提取文件路径元数据"""
        return {
            'extension': self._extract_extension(file_path),
            'is_absolute': file_path.startswith('/') or (len(file_path) > 1 and file_path[1] == ':')
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

    def _generate_ai_insights(self, ai_insights_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成AI洞察列表 - 从UI层迁移的业务逻辑"""
        insights = []
        now = datetime.now(timezone.utc)
        
        work_patterns = ai_insights_data.get('work_patterns', {})
        content_categories = ai_insights_data.get('content_categories', {})
        productivity_insights = ai_insights_data.get('productivity_insights', {})
        
        # 工作模式洞察
        primary_work_mode = work_patterns.get('primary_work_mode', '常规办公')
        detected_patterns = work_patterns.get('detected_patterns', [])
        
        if primary_work_mode != '常规办公':
            insights.append({
                "type": "pattern_detection",
                "title": f"检测到工作模式: {primary_work_mode}",
                "description": detected_patterns[0] if detected_patterns else "分析了你的工作习惯和内容偏好",
                "confidence": 0.85,
                "entities": [primary_work_mode],
                "detectedAt": (now - timedelta(minutes=15)).isoformat(),
                "iconName": "trending_up",
                "actionLabel": "查看详情"
            })
        
        # 内容类别洞察
        learning_topics = content_categories.get('learning_topics', [])
        if learning_topics:
            insights.append({
                "type": "content_analysis",
                "title": "发现学习主题",
                "description": f"检测到你在关注: {', '.join(learning_topics)}",
                "confidence": 0.78,
                "entities": learning_topics,
                "detectedAt": (now - timedelta(hours=1)).isoformat(),
                "iconName": "lightbulb",
                "actionLabel": "探索更多"
            })
        
        # 生产力洞察
        efficiency_score = productivity_insights.get('efficiency_score', 0.7)
        recommendations = productivity_insights.get('recommendations', [])
        
        if efficiency_score > 0.7 and recommendations:
            insights.append({
                "type": "productivity_insight", 
                "title": "生产力分析",
                "description": recommendations[0] if recommendations else "分析了你的效率模式",
                "confidence": efficiency_score,
                "entities": ["工作效率", "时间管理"],
                "detectedAt": (now - timedelta(hours=2)).isoformat(),
                "iconName": "schedule",
                "actionLabel": "查看建议"
            })
        
        return insights

    def _generate_trending_entities(self, ai_insights_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成趋势实体列表 - 从UI层迁移的业务逻辑"""
        entities = []
        content_categories = ai_insights_data.get('content_categories', {})
        popular_domains = content_categories.get('popular_domains', {})
        learning_topics = content_categories.get('learning_topics', [])
        
        # 将域名转换为趋势实体
        for domain, count in popular_domains.items():
            if count > 1:
                entities.append({
                    "name": domain,
                    "type": "domain",
                    "frequency": count,
                    "trend": f"+{int(count * 5)}%",
                    "trendValue": float(count * 5),
                    "description": "经常访问的网站"
                })
        
        # 将学习主题转换为趋势实体
        for i, topic in enumerate(learning_topics[:3]):
            entities.append({
                "name": topic,
                "type": "topic", 
                "frequency": 10 + i * 5,
                "trend": f"+{5 + i * 2}%",
                "trendValue": float(5 + i * 2),
                "description": "学习兴趣主题"
            })
        
        return entities

    def _get_connector_statuses(self) -> List[Dict[str, Any]]:
        """获取连接器状态列表 - 动态从连接器管理器获取"""
        try:
            from services.connectors.connector_discovery_service import ConnectorDiscoveryService
            from core.service_facade import get_service, get_connector_manager
            
            # 获取连接器发现服务和管理器
            discovery_service = get_service(ConnectorDiscoveryService)
            connector_manager = get_connector_manager()
            
            # 获取所有发现的连接器
            discovered_connectors = discovery_service.discover_connectors()
            
            # 获取连接器运行状态
            registered_connectors = connector_manager.get_all_connectors()
            
            # 构建状态映射
            status_map = {c["connector_id"]: c for c in registered_connectors}
            
            connector_statuses = []
            now = datetime.now(timezone.utc)
            
            for connector_id, metadata in discovered_connectors.items():
                # 获取运行时状态
                runtime_info = status_map.get(connector_id, {})
                
                # 获取数据计数（这里可以扩展为实际查询数据库）
                data_count = self._get_connector_data_count(connector_id)
                
                # 确定连接器状态
                status = runtime_info.get("status", "stopped")
                enabled = metadata.enabled
                
                # 构建状态信息
                connector_status = {
                    "id": connector_id,
                    "name": metadata.name,
                    "status": status,
                    "enabled": enabled,
                    "dataCount": data_count,
                    "lastHeartbeat": None
                }
                
                # 如果连接器正在运行，添加心跳时间
                if status == "running":
                    connector_status["lastHeartbeat"] = (now - timedelta(seconds=30)).isoformat()
                
                connector_statuses.append(connector_status)
            
            return connector_statuses
            
        except Exception as e:
            logger.error(f"获取连接器状态失败: {e}")
            # 回退到空列表
            return []

    def _get_connector_data_count(self, connector_id: str) -> int:
        """获取指定连接器的数据计数"""
        try:
            # 查询数据库中该连接器的数据数量
            # 这里可以根据实际的数据模型进行查询
            with self.db_service.get_session() as session:
                from models.database_models import EventData
                count = session.query(EventData).filter_by(connector_id=connector_id).count()
                return count
        except Exception as e:
            logger.warning(f"获取连接器数据计数失败 {connector_id}: {e}")
            return 0


# ServiceFacade现在负责管理服务单例，不再需要本地单例模式