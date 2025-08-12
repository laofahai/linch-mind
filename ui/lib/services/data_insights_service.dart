// 数据洞察服务 - 通过IPC获取智能分析数据
import 'dart:async';
import '../models/data_insights_models.dart';
import '../models/ipc_protocol.dart';
import 'ipc_client.dart';
import '../utils/app_logger.dart';

class DataInsightsService {
  final IPCClient _ipcClient;
  late final StreamController<DataInsightsOverview> _overviewController;
  late final StreamController<List<TimelineItem>> _timelineController;

  DataInsightsService(this._ipcClient) {
    _overviewController = StreamController<DataInsightsOverview>.broadcast();
    _timelineController = StreamController<List<TimelineItem>>.broadcast();
  }

  // 流式数据
  Stream<DataInsightsOverview> get overviewStream => _overviewController.stream;
  Stream<List<TimelineItem>> get timelineStream => _timelineController.stream;

  /// 获取数据洞察概览
  Future<DataInsightsOverview> getOverview() async {
    try {
      AppLogger.info('获取数据洞察概览', module: 'DataInsightsService');

      // 通过IPC获取真实数据
      final dashboardRequest = IPCRequest(
        method: 'GET',
        path: '/data/dashboard',
        requestId: 'dashboard_${DateTime.now().millisecondsSinceEpoch}',
      );

      final insightsRequest = IPCRequest(
        method: 'GET',
        path: '/data/insights',
        requestId: 'insights_${DateTime.now().millisecondsSinceEpoch}',
      );

      final timelineRequest = IPCRequest(
        method: 'GET',
        path: '/data/timeline',
        requestId: 'timeline_${DateTime.now().millisecondsSinceEpoch}',
        queryParams: {'limit': '10'},
      );

      // 并行请求所有数据
      final results = await Future.wait([
        _ipcClient.sendRequest(dashboardRequest),
        _ipcClient.sendRequest(insightsRequest),
        _ipcClient.sendRequest(timelineRequest),
      ]);

      final dashboardResponse = results[0];
      final insightsResponse = results[1];
      final timelineResponse = results[2];

      // 解析响应数据 - 修复类型转换问题
      final dashboardData = _ensureStringDynamicMap(dashboardResponse.data ?? {});
      final insightsData = _ensureStringDynamicMap(insightsResponse.data ?? {});
      final timelineData = _ensureStringDynamicMap(timelineResponse.data ?? {});

      // 构建概览数据
      final overview = _buildOverviewFromApiData(
        dashboardData,
        insightsData,
        timelineData,
      );
      
      // 更新流
      _overviewController.add(overview);
      
      return overview;
    } catch (e) {
      AppLogger.error('获取数据洞察概览失败: $e', module: 'DataInsightsService');
      
      // 降级到模拟数据
      final mockOverview = _createMockOverview();
      _overviewController.add(mockOverview);
      return mockOverview;
    }
  }

  /// 获取实体详情列表
  Future<List<EntityDetail>> getEntities({
    String? type,
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final request = IPCRequest(
        method: 'GET',
        path: '/data/entities',
        requestId: 'entities_${DateTime.now().millisecondsSinceEpoch}',
        queryParams: {
          if (type != null) 'type': type,
          'limit': limit.toString(),
          'offset': offset.toString(),
        },
      );

      final response = await _ipcClient.sendRequest(request);
      final data = _ensureStringDynamicMap(response.data ?? {});
      final entitiesList = data['entities'] as List<dynamic>? ?? [];

      return entitiesList.map((entity) => _parseEntityDetail(entity)).toList();
    } catch (e) {
      AppLogger.error('获取实体列表失败: $e', module: 'DataInsightsService');
      // 降级到模拟数据
      return _createMockEntities(type: type, limit: limit);
    }
  }

  /// 获取时间线活动
  Future<List<TimelineItem>> getTimeline({
    DateTime? startDate,
    DateTime? endDate,
    int limit = 100,
  }) async {
    try {
      final timeline = _createMockTimeline(limit: limit);
      _timelineController.add(timeline);
      return timeline;
    } catch (e) {
      AppLogger.error('获取时间线失败: $e', module: 'DataInsightsService');
      return [];
    }
  }

  /// 搜索实体
  Future<List<EntityDetail>> searchEntities(String query) async {
    try {
      // TODO: 实现真实的搜索API
      return _createMockEntities(searchQuery: query);
    } catch (e) {
      AppLogger.error('搜索实体失败: $e', module: 'DataInsightsService');
      return [];
    }
  }

  /// 获取连接器状态
  Future<List<ConnectorStatus>> getConnectorStatuses() async {
    try {
      // TODO: 集成真实的连接器状态API
      return _createMockConnectorStatuses();
    } catch (e) {
      AppLogger.error('获取连接器状态失败: $e', module: 'DataInsightsService');
      return [];
    }
  }

  /// 清理资源
  void dispose() {
    _overviewController.close();
    _timelineController.close();
  }

  // Mock数据生成方法

  DataInsightsOverview _createMockOverview() {
    final now = DateTime.now();
    return DataInsightsOverview(
      todayStats: const TodayStats(
        newEntities: 127,
        activeConnectors: 2,
        aiAnalysisCompleted: 89,
        knowledgeConnections: 34,
      ),
      entityBreakdown: const EntityBreakdown(
        url: 45,
        filePath: 23,
        email: 12,
        phone: 8,
        keyword: 39,
        other: 15,
      ),
      recentInsights: [
        AIInsight(
          type: 'pattern_detection',
          title: '检测到开发工作模式',
          description: '过去2小时集中访问代码文件和技术文档',
          confidence: 0.87,
          entities: const ['Python文件', 'Flutter项目', 'GitHub链接'],
          detectedAt: now.subtract(const Duration(minutes: 15)),
          iconName: 'trending_up',
          actionLabel: '查看详情',
        ),
        AIInsight(
          type: 'content_analysis',
          title: '发现新的学习主题',
          description: 'UI/UX设计相关内容增加显著',
          confidence: 0.73,
          entities: const ['设计系统', 'Material Design', '用户体验'],
          detectedAt: now.subtract(const Duration(hours: 1)),
          iconName: 'lightbulb',
          actionLabel: '探索更多',
        ),
        AIInsight(
          type: 'productivity_insight',
          title: '高效工作时段识别',
          description: '检测到你在上午10-12点最为专注',
          confidence: 0.91,
          entities: const ['代码编辑', '文档阅读', '问题解决'],
          detectedAt: now.subtract(const Duration(hours: 2)),
          iconName: 'schedule',
          actionLabel: '优化日程',
        ),
      ],
      trendingEntities: [
        const TrendingEntity(
          name: 'Linch Mind项目',
          type: 'project',
          frequency: 42,
          trend: '+15%',
          trendValue: 15.0,
          description: '个人AI生活助手项目',
        ),
        const TrendingEntity(
          name: 'Flutter开发',
          type: 'skill',
          frequency: 28,
          trend: '+8%',
          trendValue: 8.0,
          description: '跨平台UI开发框架',
        ),
        const TrendingEntity(
          name: 'AI界面设计',
          type: 'topic',
          frequency: 19,
          trend: '+12%',
          trendValue: 12.0,
          description: '人工智能用户界面设计',
        ),
      ],
      recentActivities: _createMockTimeline(limit: 10),
      connectorStatuses: _createMockConnectorStatuses(),
      lastUpdated: now,
    );
  }

  List<EntityDetail> _createMockEntities({
    String? type,
    String? searchQuery,
    int limit = 50,
  }) {
    final now = DateTime.now();
    final entities = <EntityDetail>[];

    // 根据类型或搜索查询生成不同的实体
    if (type == 'url' || searchQuery?.contains('github') == true) {
      entities.addAll([
        EntityDetail(
          id: 'url_1',
          name: 'https://github.com/flutter/flutter',
          type: 'url',
          description: 'Flutter框架GitHub仓库',
          createdAt: now.subtract(const Duration(hours: 2)),
          lastAccessed: now.subtract(const Duration(minutes: 30)),
          accessCount: 15,
          tags: const ['开发', 'Flutter', 'GitHub'],
        ),
        EntityDetail(
          id: 'url_2',
          name: 'https://material.io/design',
          type: 'url',
          description: 'Material Design设计系统',
          createdAt: now.subtract(const Duration(hours: 4)),
          lastAccessed: now.subtract(const Duration(hours: 1)),
          accessCount: 8,
          tags: const ['设计', 'UI', 'Material Design'],
        ),
      ]);
    }

    if (type == 'file_path' || searchQuery?.contains('项目') == true) {
      entities.addAll([
        EntityDetail(
          id: 'file_1',
          name: '/Users/developer/workspace/linch-mind/ui/lib/main.dart',
          type: 'file_path',
          description: '主应用入口文件',
          createdAt: now.subtract(const Duration(hours: 1)),
          lastAccessed: now.subtract(const Duration(minutes: 10)),
          accessCount: 23,
          tags: const ['Flutter', '代码', '入口文件'],
        ),
        EntityDetail(
          id: 'file_2',
          name: '/Users/developer/workspace/linch-mind/daemon/main.py',
          type: 'file_path',
          description: 'Python后端服务主文件',
          createdAt: now.subtract(const Duration(hours: 3)),
          lastAccessed: now.subtract(const Duration(minutes: 45)),
          accessCount: 18,
          tags: const ['Python', '后端', '服务'],
        ),
      ]);
    }

    // 添加更多模拟数据
    for (int i = entities.length; i < limit; i++) {
      entities.add(EntityDetail(
        id: 'entity_$i',
        name: '实体 $i',
        type: ['url', 'file_path', 'keyword', 'email'][i % 4],
        description: '这是第 $i 个实体的描述',
        createdAt: now.subtract(Duration(hours: i)),
        lastAccessed: now.subtract(Duration(minutes: i * 5)),
        accessCount: (limit - i),
        tags: ['标签${i % 3}', '类别${i % 2}'],
      ));
    }

    return entities;
  }

  List<TimelineItem> _createMockTimeline({int limit = 100}) {
    final now = DateTime.now();
    final activities = <TimelineItem>[];

    final activityTypes = [
      'entity_created',
      'insight_generated',
      'connector_activity',
      'analysis_completed',
    ];

    for (int i = 0; i < limit; i++) {
      final type = activityTypes[i % activityTypes.length];
      final timestamp = now.subtract(Duration(minutes: i * 5));

      activities.add(TimelineItem(
        id: 'timeline_$i',
        title: _getActivityTitle(type, i),
        description: _getActivityDescription(type, i),
        timestamp: timestamp,
        type: type,
        iconName: _getActivityIcon(type),
        connectorId: type == 'connector_activity' ? 'clipboard' : null,
        metadata: {
          'index': i,
          'priority': i < 10 ? 'high' : 'normal',
        },
      ));
    }

    return activities;
  }

  List<ConnectorStatus> _createMockConnectorStatuses() {
    final now = DateTime.now();
    return [
      ConnectorStatus(
        id: 'clipboard',
        name: '剪贴板连接器',
        status: 'running',
        enabled: true,
        dataCount: 156,
        lastHeartbeat: now.subtract(const Duration(seconds: 30)),
      ),
      ConnectorStatus(
        id: 'filesystem',
        name: '文件系统连接器',
        status: 'stopped',
        enabled: false,
        dataCount: 0,
        lastHeartbeat: null,
      ),
    ];
  }

  String _getActivityTitle(String type, int index) {
    switch (type) {
      case 'entity_created':
        return '新实体创建';
      case 'insight_generated':
        return 'AI洞察生成';
      case 'connector_activity':
        return '连接器活动';
      case 'analysis_completed':
        return '内容分析完成';
      default:
        return '系统活动 $index';
    }
  }

  String _getActivityDescription(String type, int index) {
    switch (type) {
      case 'entity_created':
        return '检测到新的URL实体并完成分析';
      case 'insight_generated':
        return '识别出新的工作模式和行为趋势';
      case 'connector_activity':
        return '剪贴板连接器采集了新的内容';
      case 'analysis_completed':
        return '完成对文档内容的智能分析';
      default:
        return '系统执行了第 $index 个活动';
    }
  }

  String _getActivityIcon(String type) {
    switch (type) {
      case 'entity_created':
        return 'add_circle';
      case 'insight_generated':
        return 'psychology';
      case 'connector_activity':
        return 'sensors';
      case 'analysis_completed':
        return 'analytics';
      default:
        return 'info';
    }
  }

  // 真实API数据解析方法

  DataInsightsOverview _buildOverviewFromApiData(
    Map<String, dynamic> dashboardData,
    Map<String, dynamic> insightsData,
    Map<String, dynamic> timelineData,
  ) {
    final now = DateTime.now();
    
    // 解析仪表板数据
    final entityTypes = dashboardData['entity_types'] as Map<String, dynamic>? ?? {};
    final totalEntities = dashboardData['total_entities'] as int? ?? 0;
    final todayEntities = dashboardData['today_entities'] as int? ?? 0;

    // 解析AI洞察数据
    final workPatterns = insightsData['work_patterns'] as Map<String, dynamic>? ?? {};
    final contentCategories = insightsData['content_categories'] as Map<String, dynamic>? ?? {};
    final productivityInsights = insightsData['productivity_insights'] as Map<String, dynamic>? ?? {};

    // 解析时间线数据
    final timelineList = timelineData['timeline'] as List<dynamic>? ?? [];

    return DataInsightsOverview(
      todayStats: TodayStats(
        newEntities: todayEntities,
        activeConnectors: 2, // 硬编码，未来从连接器状态获取
        aiAnalysisCompleted: totalEntities,
        knowledgeConnections: (totalEntities * 0.3).round(),
      ),
      entityBreakdown: EntityBreakdown(
        url: entityTypes['urls'] as int? ?? 0,
        filePath: entityTypes['files'] as int? ?? 0,
        email: entityTypes['emails'] as int? ?? 0,
        phone: entityTypes['phones'] as int? ?? 0,
        keyword: entityTypes['keywords'] as int? ?? 0,
        other: 0,
      ),
      recentInsights: _parseAIInsights(workPatterns, contentCategories, productivityInsights),
      trendingEntities: _parseTrendingEntities(contentCategories),
      recentActivities: timelineList.map((item) => _parseTimelineItem(item)).toList(),
      connectorStatuses: _createMockConnectorStatuses(), // 暂时使用模拟数据
      lastUpdated: now,
    );
  }

  List<AIInsight> _parseAIInsights(
    Map<String, dynamic> workPatterns,
    Map<String, dynamic> contentCategories,
    Map<String, dynamic> productivityInsights,
  ) {
    final insights = <AIInsight>[];
    final now = DateTime.now();

    // 解析工作模式洞察
    final primaryWorkMode = workPatterns['primary_work_mode'] as String? ?? '常规办公';
    final detectedPatterns = workPatterns['detected_patterns'] as List<dynamic>? ?? [];

    if (primaryWorkMode != '常规办公') {
      insights.add(AIInsight(
        type: 'pattern_detection',
        title: '检测到工作模式: $primaryWorkMode',
        description: detectedPatterns.isNotEmpty 
            ? detectedPatterns.first.toString() 
            : '分析了你的工作习惯和内容偏好',
        confidence: 0.85,
        entities: [primaryWorkMode],
        detectedAt: now.subtract(const Duration(minutes: 15)),
        iconName: 'trending_up',
        actionLabel: '查看详情',
      ));
    }

    // 解析内容类别洞察
    final learningTopics = contentCategories['learning_topics'] as List<dynamic>? ?? [];

    if (learningTopics.isNotEmpty) {
      insights.add(AIInsight(
        type: 'content_analysis',
        title: '发现学习主题',
        description: '检测到你在关注: ${learningTopics.join(', ')}',
        confidence: 0.78,
        entities: learningTopics.cast<String>(),
        detectedAt: now.subtract(const Duration(hours: 1)),
        iconName: 'lightbulb',
        actionLabel: '探索更多',
      ));
    }

    // 解析生产力洞察
    final efficiencyScore = productivityInsights['efficiency_score'] as double? ?? 0.7;
    final recommendations = productivityInsights['recommendations'] as List<dynamic>? ?? [];

    if (efficiencyScore > 0.7 && recommendations.isNotEmpty) {
      insights.add(AIInsight(
        type: 'productivity_insight',
        title: '生产力分析',
        description: recommendations.isNotEmpty 
            ? recommendations.first.toString()
            : '分析了你的效率模式',
        confidence: efficiencyScore,
        entities: const ['工作效率', '时间管理'],
        detectedAt: now.subtract(const Duration(hours: 2)),
        iconName: 'schedule',
        actionLabel: '查看建议',
      ));
    }

    return insights;
  }

  List<TrendingEntity> _parseTrendingEntities(Map<String, dynamic> contentCategories) {
    final entities = <TrendingEntity>[];
    final popularDomains = contentCategories['popular_domains'] as Map<String, dynamic>? ?? {};
    final learningTopics = contentCategories['learning_topics'] as List<dynamic>? ?? [];

    // 将域名转换为趋势实体
    popularDomains.forEach((domain, count) {
      if (count is int && count > 1) {
        entities.add(TrendingEntity(
          name: domain,
          type: 'domain',
          frequency: count,
          trend: '+${(count * 5).toStringAsFixed(0)}%',
          trendValue: count * 5.0,
          description: '经常访问的网站',
        ));
      }
    });

    // 将学习主题转换为趋势实体
    for (int i = 0; i < learningTopics.length && i < 3; i++) {
      final topic = learningTopics[i].toString();
      entities.add(TrendingEntity(
        name: topic,
        type: 'topic',
        frequency: 10 + i * 5,
        trend: '+${5 + i * 2}%',
        trendValue: 5.0 + i * 2,
        description: '学习兴趣主题',
      ));
    }

    return entities;
  }

  TimelineItem _parseTimelineItem(Map<String, dynamic> item) {
    return TimelineItem(
      id: item['id']?.toString() ?? '',
      title: item['description']?.toString() ?? '',
      description: _getTimelineDescription(item),
      timestamp: DateTime.tryParse(item['timestamp']?.toString() ?? '') ?? DateTime.now(),
      type: item['type']?.toString() ?? 'system_activity',
      iconName: _getTimelineIcon(item['type']?.toString() ?? ''),
      metadata: item['metadata'] as Map<String, dynamic>?,
    );
  }

  String _getTimelineDescription(Map<String, dynamic> item) {
    final metadata = item['metadata'] as Map<String, dynamic>? ?? {};
    final entitiesCount = metadata['entities_count'] as int? ?? 0;
    
    if (entitiesCount > 0) {
      return '智能识别了 $entitiesCount 个实体';
    }
    
    return item['description']?.toString() ?? '系统活动';
  }

  String _getTimelineIcon(String type) {
    switch (type) {
      case '数据采集':
        return 'sensors';
      case '智能分析':
        return 'analytics';
      default:
        return 'info';
    }
  }

  EntityDetail _parseEntityDetail(Map<String, dynamic> entity) {
    return EntityDetail(
      id: entity['id']?.toString() ?? '',
      name: entity['content']?.toString() ?? '',
      type: entity['type']?.toString() ?? '',
      description: _getEntityDescription(entity),
      createdAt: DateTime.tryParse(entity['timestamp']?.toString() ?? ''),
      properties: entity['metadata'] as Map<String, dynamic>?,
      tags: _getEntityTags(entity),
    );
  }

  String _getEntityDescription(Map<String, dynamic> entity) {
    final type = entity['type']?.toString() ?? '';
    final content = entity['content']?.toString() ?? '';
    
    switch (type) {
      case 'url':
        return 'Web链接: ${Uri.tryParse(content)?.host ?? content}';
      case 'email':
        return '邮箱地址';
      case 'phone':
        return '电话号码';
      case 'file':
        return '文件路径';
      default:
        return '智能识别的实体';
    }
  }

  List<String> _getEntityTags(Map<String, dynamic> entity) {
    final type = entity['type']?.toString() ?? '';
    final metadataRaw = entity['metadata'];
    final metadata = _ensureStringDynamicMap(metadataRaw is Map ? metadataRaw.cast<String, dynamic>() : {});
    final tags = <String>[type];
    
    if (metadata['domain'] != null) {
      tags.add(metadata['domain'].toString());
    }
    
    if (metadata['is_secure'] == true) {
      tags.add('安全连接');
    }
    
    return tags;
  }

  /// 确保 Map是 String -> dynamic 类型
  Map<String, dynamic> _ensureStringDynamicMap(Map<dynamic, dynamic> input) {
    return input.map((key, value) => MapEntry(key.toString(), value));
  }
}