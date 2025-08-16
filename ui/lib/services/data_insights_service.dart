// 数据洞察服务 - 纯UI数据获取层（零业务逻辑）
import 'dart:async';
import '../models/data_insights_models.dart';
import '../models/ipc_protocol.dart';
import 'ipc_client.dart';
import '../utils/app_logger.dart';

/// 纯UI数据服务 - 仅负责IPC通信和数据缓存
/// 所有业务逻辑已迁移到daemon端处理
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

  /// 获取数据洞察概览 - 纯数据获取，无业务逻辑
  Future<DataInsightsOverview> getOverview() async {
    try {
      AppLogger.info('获取数据洞察概览', module: 'DataInsightsService');

      // 直接从daemon获取完整的概览数据
      final request = IPCRequest(
        method: 'GET',
        path: '/insights/overview',
        requestId: 'overview_${DateTime.now().millisecondsSinceEpoch}',
      );

      final response = await _ipcClient.sendRequest(request);
      final data = _ensureStringDynamicMap(response.data ?? {});

      // 直接构建概览数据，无任何业务逻辑处理
      final overview = _buildOverviewFromCompleteApiData(data);

      // 更新流
      _overviewController.add(overview);

      return overview;
    } catch (e) {
      AppLogger.error('获取数据洞察概览失败: $e', module: 'DataInsightsService');
      rethrow; // 不再使用Mock数据，直接抛出错误
    }
  }

  /// 获取实体详情列表 - 纯数据获取
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
      rethrow; // 不再使用Mock数据
    }
  }

  /// 获取时间线活动 - 纯数据获取
  Future<List<TimelineItem>> getTimeline({
    DateTime? startDate,
    DateTime? endDate,
    int limit = 100,
  }) async {
    try {
      final request = IPCRequest(
        method: 'GET',
        path: '/data/timeline',
        requestId: 'timeline_${DateTime.now().millisecondsSinceEpoch}',
        queryParams: {'limit': limit.toString()},
      );

      final response = await _ipcClient.sendRequest(request);
      final data = _ensureStringDynamicMap(response.data ?? {});
      final timelineList = data['timeline'] as List<dynamic>? ?? [];

      final timeline =
          timelineList.map((item) => _parseTimelineItem(item)).toList();
      _timelineController.add(timeline);
      return timeline;
    } catch (e) {
      AppLogger.error('获取时间线失败: $e', module: 'DataInsightsService');
      rethrow;
    }
  }

  /// 搜索实体 - 纯数据获取
  Future<List<EntityDetail>> searchEntities(String query) async {
    try {
      final request = IPCRequest(
        method: 'POST',
        path: '/data/search',
        requestId: 'search_${DateTime.now().millisecondsSinceEpoch}',
        data: {'query': query, 'limit': 20},
      );

      final response = await _ipcClient.sendRequest(request);
      final data = _ensureStringDynamicMap(response.data ?? {});
      final resultsList = data['results'] as List<dynamic>? ?? [];

      return resultsList.map((entity) => _parseEntityDetail(entity)).toList();
    } catch (e) {
      AppLogger.error('搜索实体失败: $e', module: 'DataInsightsService');
      rethrow;
    }
  }

  /// 获取连接器状态 - 暂时不实现，由overview接口返回
  Future<List<ConnectorStatus>> getConnectorStatuses() async {
    try {
      // 连接器状态现在由/insights/overview接口统一返回
      final overview = await getOverview();
      return overview.connectorStatuses;
    } catch (e) {
      AppLogger.error('获取连接器状态失败: $e', module: 'DataInsightsService');
      rethrow;
    }
  }

  /// 向量语义搜索
  Future<List<VectorSearchResult>> vectorSearch(VectorSearchQuery query) async {
    try {
      AppLogger.info('执行向量搜索: ${query.query}', module: 'DataInsightsService');

      final request = IPCRequest(
        method: 'POST',
        path: '/search/vector',
        requestId: 'vector_search_${DateTime.now().millisecondsSinceEpoch}',
        data: query.toJson(),
      );

      final response = await _ipcClient.sendRequest(request);
      final data = _ensureStringDynamicMap(response.data ?? {});
      final resultsList = data['results'] as List<dynamic>? ?? [];

      return resultsList
          .map((result) => _parseVectorSearchResult(result))
          .toList();
    } catch (e) {
      AppLogger.error('向量搜索失败: $e', module: 'DataInsightsService');
      rethrow;
    }
  }

  /// 获取搜索建议
  Future<List<SearchSuggestion>> getSearchSuggestions(String query) async {
    try {
      final request = IPCRequest(
        method: 'POST',
        path: '/search/suggestions',
        requestId: 'suggestions_${DateTime.now().millisecondsSinceEpoch}',
        data: {'query': query},
      );

      final response = await _ipcClient.sendRequest(request);
      final data = _ensureStringDynamicMap(response.data ?? {});
      final suggestionsList = data['suggestions'] as List<dynamic>? ?? [];

      return suggestionsList
          .map((suggestion) => _parseSearchSuggestion(suggestion))
          .toList();
    } catch (e) {
      AppLogger.error('获取搜索建议失败: $e', module: 'DataInsightsService');
      return [];
    }
  }

  /// 计算实体相似性
  Future<List<SimilarityResult>> calculateSimilarity(String entityId,
      {int limit = 10}) async {
    try {
      final request = IPCRequest(
        method: 'POST',
        path: '/similarity/calculate',
        requestId: 'similarity_${DateTime.now().millisecondsSinceEpoch}',
        data: {
          'entity_id': entityId,
          'limit': limit,
        },
      );

      final response = await _ipcClient.sendRequest(request);
      final data = _ensureStringDynamicMap(response.data ?? {});
      final resultsList = data['similarities'] as List<dynamic>? ?? [];

      return resultsList
          .map((result) => _parseSimilarityResult(result))
          .toList();
    } catch (e) {
      AppLogger.error('计算相似性失败: $e', module: 'DataInsightsService');
      rethrow;
    }
  }

  /// 获取内容聚类结果
  Future<List<ClusterResult>> getContentClusters({int numClusters = 10}) async {
    try {
      final request = IPCRequest(
        method: 'POST',
        path: '/clustering/analyze',
        requestId: 'clustering_${DateTime.now().millisecondsSinceEpoch}',
        data: {
          'num_clusters': numClusters,
        },
      );

      final response = await _ipcClient.sendRequest(request);
      final data = _ensureStringDynamicMap(response.data ?? {});
      final clustersList = data['clusters'] as List<dynamic>? ?? [];

      return clustersList
          .map((cluster) => _parseClusterResult(cluster))
          .toList();
    } catch (e) {
      AppLogger.error('获取聚类结果失败: $e', module: 'DataInsightsService');
      rethrow;
    }
  }

  /// 获取向量数据库指标
  Future<VectorMetrics> getVectorMetrics() async {
    try {
      final request = IPCRequest(
        method: 'GET',
        path: '/vector/metrics',
        requestId: 'metrics_${DateTime.now().millisecondsSinceEpoch}',
      );

      final response = await _ipcClient.sendRequest(request);
      final data = _ensureStringDynamicMap(response.data ?? {});

      return _parseVectorMetrics(data);
    } catch (e) {
      AppLogger.error('获取向量指标失败: $e', module: 'DataInsightsService');
      rethrow;
    }
  }

  /// 清理资源
  void dispose() {
    _overviewController.close();
    _timelineController.close();
  }

  // 数据转换方法 - 纯数据映射，无业务逻辑

  /// 从完整的API数据构建概览对象
  DataInsightsOverview _buildOverviewFromCompleteApiData(
      Map<String, dynamic> data) {
    final todayStatsData = data['todayStats'] as Map<String, dynamic>? ?? {};
    final entityBreakdownData =
        data['entityBreakdown'] as Map<String, dynamic>? ?? {};
    final recentInsightsList = data['recentInsights'] as List<dynamic>? ?? [];
    final trendingEntitiesList =
        data['trendingEntities'] as List<dynamic>? ?? [];
    final recentActivitiesList =
        data['recentActivities'] as List<dynamic>? ?? [];
    final connectorStatusesList =
        data['connectorStatuses'] as List<dynamic>? ?? [];

    return DataInsightsOverview(
      todayStats: TodayStats(
        newEntities: todayStatsData['newEntities'] as int? ?? 0,
        activeConnectors: todayStatsData['activeConnectors'] as int? ?? 0,
        aiAnalysisCompleted: todayStatsData['aiAnalysisCompleted'] as int? ?? 0,
        knowledgeConnections:
            todayStatsData['knowledgeConnections'] as int? ?? 0,
      ),
      entityBreakdown: EntityBreakdown(
        url: entityBreakdownData['url'] as int? ?? 0,
        filePath: entityBreakdownData['filePath'] as int? ?? 0,
        email: entityBreakdownData['email'] as int? ?? 0,
        phone: entityBreakdownData['phone'] as int? ?? 0,
        keyword: entityBreakdownData['keyword'] as int? ?? 0,
        other: entityBreakdownData['other'] as int? ?? 0,
      ),
      recentInsights:
          recentInsightsList.map((item) => _parseAIInsight(item)).toList(),
      trendingEntities: trendingEntitiesList
          .map((item) => _parseTrendingEntity(item))
          .toList(),
      recentActivities:
          recentActivitiesList.map((item) => _parseTimelineItem(item)).toList(),
      connectorStatuses: connectorStatusesList
          .map((item) => _parseConnectorStatus(item))
          .toList(),
      lastUpdated: DateTime.tryParse(data['lastUpdated']?.toString() ?? '') ??
          DateTime.now(),
    );
  }

  /// 解析AI洞察数据
  AIInsight _parseAIInsight(Map<String, dynamic> data) {
    return AIInsight(
      type: data['type']?.toString() ?? '',
      title: data['title']?.toString() ?? '',
      description: data['description']?.toString() ?? '',
      confidence: (data['confidence'] as num?)?.toDouble() ?? 0.0,
      entities: (data['entities'] as List<dynamic>?)?.cast<String>() ?? [],
      detectedAt: DateTime.tryParse(data['detectedAt']?.toString() ?? '') ??
          DateTime.now(),
      iconName: data['iconName']?.toString() ?? 'info',
      actionLabel: data['actionLabel']?.toString() ?? '',
    );
  }

  /// 解析趋势实体数据
  TrendingEntity _parseTrendingEntity(Map<String, dynamic> data) {
    return TrendingEntity(
      name: data['name']?.toString() ?? '',
      type: data['type']?.toString() ?? '',
      frequency: data['frequency'] as int? ?? 0,
      trend: data['trend']?.toString() ?? '',
      trendValue: (data['trendValue'] as num?)?.toDouble() ?? 0.0,
      description: data['description']?.toString() ?? '',
    );
  }

  /// 解析连接器状态数据
  ConnectorStatus _parseConnectorStatus(Map<String, dynamic> data) {
    return ConnectorStatus(
      id: data['id']?.toString() ?? '',
      name: data['name']?.toString() ?? '',
      status: data['status']?.toString() ?? '',
      enabled: data['enabled'] as bool? ?? false,
      dataCount: data['dataCount'] as int? ?? 0,
      lastHeartbeat: data['lastHeartbeat'] != null
          ? DateTime.tryParse(data['lastHeartbeat'].toString())
          : null,
    );
  }

  // 简化的数据解析方法（仅用于字段解析，无业务逻辑）

  /// 解析时间线项目数据
  TimelineItem _parseTimelineItem(Map<String, dynamic> item) {
    return TimelineItem(
      id: item['id']?.toString() ?? '',
      title: item['type']?.toString() ?? '',
      description: item['description']?.toString() ?? '',
      timestamp: DateTime.tryParse(item['timestamp']?.toString() ?? '') ??
          DateTime.now(),
      type: item['type']?.toString() ?? 'system_activity',
      iconName: _getTimelineIcon(item['type']?.toString()),
      connectorId: item['source']?.toString(),
      metadata: item['metadata'] as Map<String, dynamic>?,
    );
  }

  /// 获取时间线图标
  String _getTimelineIcon(String? type) {
    switch (type) {
      case '数据采集':
        return 'sensors';
      case '智能分析':
        return 'analytics';
      default:
        return 'info';
    }
  }

  /// 解析实体详情数据
  EntityDetail _parseEntityDetail(Map<String, dynamic> entity) {
    final metadata = entity['metadata'] as Map<String, dynamic>? ?? {};
    return EntityDetail(
      id: entity['id']?.toString() ?? '',
      name: entity['content']?.toString() ?? '',
      type: entity['type']?.toString() ?? '',
      description: entity['description']?.toString() ?? '智能识别的实体',
      createdAt: DateTime.tryParse(entity['timestamp']?.toString() ?? ''),
      lastAccessed: DateTime.tryParse(entity['lastAccessed']?.toString() ?? ''),
      accessCount: entity['accessCount'] as int? ?? 0,
      properties: metadata,
      tags: (entity['tags'] as List<dynamic>?)?.cast<String>() ?? [],
    );
  }

  /// 解析向量搜索结果
  VectorSearchResult _parseVectorSearchResult(Map<String, dynamic> data) {
    return VectorSearchResult(
      id: data['id']?.toString() ?? '',
      content: data['content']?.toString() ?? '',
      similarity: (data['similarity'] as num?)?.toDouble() ?? 0.0,
      metadata: data['metadata'] as Map<String, dynamic>?,
      entityId: data['entity_id']?.toString(),
      entityType: data['entity_type']?.toString(),
      timestamp: DateTime.tryParse(data['timestamp']?.toString() ?? ''),
      highlightedTerms:
          (data['highlighted_terms'] as List<dynamic>?)?.cast<String>() ?? [],
    );
  }

  /// 解析搜索建议
  SearchSuggestion _parseSearchSuggestion(Map<String, dynamic> data) {
    return SearchSuggestion(
      text: data['text']?.toString() ?? '',
      confidence: (data['confidence'] as num?)?.toDouble() ?? 0.0,
      type: data['type']?.toString(),
      matchedTerms:
          (data['matched_terms'] as List<dynamic>?)?.cast<String>() ?? [],
    );
  }

  /// 解析相似性结果
  SimilarityResult _parseSimilarityResult(Map<String, dynamic> data) {
    return SimilarityResult(
      sourceId: data['source_id']?.toString() ?? '',
      targetId: data['target_id']?.toString() ?? '',
      similarity: (data['similarity'] as num?)?.toDouble() ?? 0.0,
      sourceContent: data['source_content']?.toString(),
      targetContent: data['target_content']?.toString(),
      metadata: data['metadata'] as Map<String, dynamic>?,
    );
  }

  /// 解析聚类结果
  ClusterResult _parseClusterResult(Map<String, dynamic> data) {
    return ClusterResult(
      clusterId: data['cluster_id'] as int? ?? 0,
      label: data['label']?.toString() ?? '',
      entityIds: (data['entity_ids'] as List<dynamic>?)?.cast<String>() ?? [],
      coherence: (data['coherence'] as num?)?.toDouble() ?? 0.0,
      keywords: (data['keywords'] as List<dynamic>?)?.cast<String>() ?? [],
      metadata: data['metadata'] as Map<String, dynamic>?,
    );
  }

  /// 解析向量指标
  VectorMetrics _parseVectorMetrics(Map<String, dynamic> data) {
    return VectorMetrics(
      totalVectors: data['total_vectors'] as int? ?? 0,
      dimension: data['dimension'] as int? ?? 0,
      indexType: data['index_type']?.toString(),
      memoryUsageMb: (data['memory_usage_mb'] as num?)?.toDouble() ?? 0.0,
      searchTimeAvgMs: (data['search_time_avg_ms'] as num?)?.toDouble() ?? 0.0,
      lastUpdated: DateTime.tryParse(data['last_updated']?.toString() ?? ''),
    );
  }

  /// 确保 Map是 String -> dynamic 类型
  Map<String, dynamic> _ensureStringDynamicMap(Map<dynamic, dynamic> input) {
    return input.map((key, value) => MapEntry(key.toString(), value));
  }
}
