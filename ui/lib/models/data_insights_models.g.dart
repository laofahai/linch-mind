// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'data_insights_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$TodayStatsImpl _$$TodayStatsImplFromJson(Map<String, dynamic> json) =>
    _$TodayStatsImpl(
      newEntities: (json['newEntities'] as num?)?.toInt() ?? 0,
      activeConnectors: (json['activeConnectors'] as num?)?.toInt() ?? 0,
      aiAnalysisCompleted: (json['aiAnalysisCompleted'] as num?)?.toInt() ?? 0,
      knowledgeConnections:
          (json['knowledgeConnections'] as num?)?.toInt() ?? 0,
    );

Map<String, dynamic> _$$TodayStatsImplToJson(_$TodayStatsImpl instance) =>
    <String, dynamic>{
      'newEntities': instance.newEntities,
      'activeConnectors': instance.activeConnectors,
      'aiAnalysisCompleted': instance.aiAnalysisCompleted,
      'knowledgeConnections': instance.knowledgeConnections,
    };

_$EntityBreakdownImpl _$$EntityBreakdownImplFromJson(
        Map<String, dynamic> json) =>
    _$EntityBreakdownImpl(
      url: (json['url'] as num?)?.toInt() ?? 0,
      filePath: (json['filePath'] as num?)?.toInt() ?? 0,
      email: (json['email'] as num?)?.toInt() ?? 0,
      phone: (json['phone'] as num?)?.toInt() ?? 0,
      keyword: (json['keyword'] as num?)?.toInt() ?? 0,
      other: (json['other'] as num?)?.toInt() ?? 0,
    );

Map<String, dynamic> _$$EntityBreakdownImplToJson(
        _$EntityBreakdownImpl instance) =>
    <String, dynamic>{
      'url': instance.url,
      'filePath': instance.filePath,
      'email': instance.email,
      'phone': instance.phone,
      'keyword': instance.keyword,
      'other': instance.other,
    };

_$AIInsightImpl _$$AIInsightImplFromJson(Map<String, dynamic> json) =>
    _$AIInsightImpl(
      type: json['type'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      entities: (json['entities'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      detectedAt: json['detectedAt'] == null
          ? null
          : DateTime.parse(json['detectedAt'] as String),
      iconName: json['iconName'] as String?,
      actionLabel: json['actionLabel'] as String?,
    );

Map<String, dynamic> _$$AIInsightImplToJson(_$AIInsightImpl instance) =>
    <String, dynamic>{
      'type': instance.type,
      'title': instance.title,
      'description': instance.description,
      'confidence': instance.confidence,
      'entities': instance.entities,
      'detectedAt': instance.detectedAt?.toIso8601String(),
      'iconName': instance.iconName,
      'actionLabel': instance.actionLabel,
    };

_$TrendingEntityImpl _$$TrendingEntityImplFromJson(Map<String, dynamic> json) =>
    _$TrendingEntityImpl(
      name: json['name'] as String,
      type: json['type'] as String,
      frequency: (json['frequency'] as num?)?.toInt() ?? 0,
      trend: json['trend'] as String?,
      trendValue: (json['trendValue'] as num?)?.toDouble(),
      description: json['description'] as String?,
    );

Map<String, dynamic> _$$TrendingEntityImplToJson(
        _$TrendingEntityImpl instance) =>
    <String, dynamic>{
      'name': instance.name,
      'type': instance.type,
      'frequency': instance.frequency,
      'trend': instance.trend,
      'trendValue': instance.trendValue,
      'description': instance.description,
    };

_$EntityDetailImpl _$$EntityDetailImplFromJson(Map<String, dynamic> json) =>
    _$EntityDetailImpl(
      id: json['id'] as String,
      name: json['name'] as String,
      type: json['type'] as String,
      description: json['description'] as String?,
      createdAt: json['createdAt'] == null
          ? null
          : DateTime.parse(json['createdAt'] as String),
      lastAccessed: json['lastAccessed'] == null
          ? null
          : DateTime.parse(json['lastAccessed'] as String),
      accessCount: (json['accessCount'] as num?)?.toInt() ?? 0,
      properties: json['properties'] as Map<String, dynamic>?,
      tags:
          (json['tags'] as List<dynamic>?)?.map((e) => e as String).toList() ??
              const [],
    );

Map<String, dynamic> _$$EntityDetailImplToJson(_$EntityDetailImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'type': instance.type,
      'description': instance.description,
      'createdAt': instance.createdAt?.toIso8601String(),
      'lastAccessed': instance.lastAccessed?.toIso8601String(),
      'accessCount': instance.accessCount,
      'properties': instance.properties,
      'tags': instance.tags,
    };

_$TimelineItemImpl _$$TimelineItemImplFromJson(Map<String, dynamic> json) =>
    _$TimelineItemImpl(
      id: json['id'] as String,
      title: json['title'] as String,
      description: json['description'] as String?,
      timestamp: DateTime.parse(json['timestamp'] as String),
      type: json['type'] as String,
      metadata: json['metadata'] as Map<String, dynamic>?,
      iconName: json['iconName'] as String?,
      connectorId: json['connectorId'] as String?,
    );

Map<String, dynamic> _$$TimelineItemImplToJson(_$TimelineItemImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'title': instance.title,
      'description': instance.description,
      'timestamp': instance.timestamp.toIso8601String(),
      'type': instance.type,
      'metadata': instance.metadata,
      'iconName': instance.iconName,
      'connectorId': instance.connectorId,
    };

_$ConnectorStatusImpl _$$ConnectorStatusImplFromJson(
        Map<String, dynamic> json) =>
    _$ConnectorStatusImpl(
      id: json['id'] as String,
      name: json['name'] as String,
      status: json['status'] as String,
      enabled: json['enabled'] as bool? ?? true,
      dataCount: (json['dataCount'] as num?)?.toInt() ?? 0,
      lastHeartbeat: json['lastHeartbeat'] == null
          ? null
          : DateTime.parse(json['lastHeartbeat'] as String),
      errorMessage: json['errorMessage'] as String?,
    );

Map<String, dynamic> _$$ConnectorStatusImplToJson(
        _$ConnectorStatusImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'status': instance.status,
      'enabled': instance.enabled,
      'dataCount': instance.dataCount,
      'lastHeartbeat': instance.lastHeartbeat?.toIso8601String(),
      'errorMessage': instance.errorMessage,
    };

_$DataInsightsOverviewImpl _$$DataInsightsOverviewImplFromJson(
        Map<String, dynamic> json) =>
    _$DataInsightsOverviewImpl(
      todayStats:
          TodayStats.fromJson(json['todayStats'] as Map<String, dynamic>),
      entityBreakdown: EntityBreakdown.fromJson(
          json['entityBreakdown'] as Map<String, dynamic>),
      recentInsights: (json['recentInsights'] as List<dynamic>?)
              ?.map((e) => AIInsight.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      trendingEntities: (json['trendingEntities'] as List<dynamic>?)
              ?.map((e) => TrendingEntity.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      recentActivities: (json['recentActivities'] as List<dynamic>?)
              ?.map((e) => TimelineItem.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      connectorStatuses: (json['connectorStatuses'] as List<dynamic>?)
              ?.map((e) => ConnectorStatus.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      lastUpdated: json['lastUpdated'] == null
          ? null
          : DateTime.parse(json['lastUpdated'] as String),
    );

Map<String, dynamic> _$$DataInsightsOverviewImplToJson(
        _$DataInsightsOverviewImpl instance) =>
    <String, dynamic>{
      'todayStats': instance.todayStats,
      'entityBreakdown': instance.entityBreakdown,
      'recentInsights': instance.recentInsights,
      'trendingEntities': instance.trendingEntities,
      'recentActivities': instance.recentActivities,
      'connectorStatuses': instance.connectorStatuses,
      'lastUpdated': instance.lastUpdated?.toIso8601String(),
    };

_$FilterOptionsImpl _$$FilterOptionsImplFromJson(Map<String, dynamic> json) =>
    _$FilterOptionsImpl(
      entityTypes: (json['entityTypes'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      connectorIds: (json['connectorIds'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      startDate: json['startDate'] == null
          ? null
          : DateTime.parse(json['startDate'] as String),
      endDate: json['endDate'] == null
          ? null
          : DateTime.parse(json['endDate'] as String),
      searchQuery: json['searchQuery'] as String?,
    );

Map<String, dynamic> _$$FilterOptionsImplToJson(_$FilterOptionsImpl instance) =>
    <String, dynamic>{
      'entityTypes': instance.entityTypes,
      'connectorIds': instance.connectorIds,
      'startDate': instance.startDate?.toIso8601String(),
      'endDate': instance.endDate?.toIso8601String(),
      'searchQuery': instance.searchQuery,
    };

_$VectorSearchResultImpl _$$VectorSearchResultImplFromJson(
        Map<String, dynamic> json) =>
    _$VectorSearchResultImpl(
      id: json['id'] as String,
      content: json['content'] as String,
      similarity: (json['similarity'] as num?)?.toDouble() ?? 0.0,
      metadata: json['metadata'] as Map<String, dynamic>?,
      entityId: json['entityId'] as String?,
      entityType: json['entityType'] as String?,
      timestamp: json['timestamp'] == null
          ? null
          : DateTime.parse(json['timestamp'] as String),
      highlightedTerms: (json['highlightedTerms'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$VectorSearchResultImplToJson(
        _$VectorSearchResultImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'content': instance.content,
      'similarity': instance.similarity,
      'metadata': instance.metadata,
      'entityId': instance.entityId,
      'entityType': instance.entityType,
      'timestamp': instance.timestamp?.toIso8601String(),
      'highlightedTerms': instance.highlightedTerms,
    };

_$VectorSearchQueryImpl _$$VectorSearchQueryImplFromJson(
        Map<String, dynamic> json) =>
    _$VectorSearchQueryImpl(
      query: json['query'] as String,
      k: (json['k'] as num?)?.toInt() ?? 10,
      threshold: (json['threshold'] as num?)?.toDouble() ?? 0.0,
      entityTypes: (json['entityTypes'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      tags:
          (json['tags'] as List<dynamic>?)?.map((e) => e as String).toList() ??
              const [],
      metadata: json['metadata'] as Map<String, dynamic>?,
      dateFrom: json['dateFrom'] == null
          ? null
          : DateTime.parse(json['dateFrom'] as String),
      dateTo: json['dateTo'] == null
          ? null
          : DateTime.parse(json['dateTo'] as String),
    );

Map<String, dynamic> _$$VectorSearchQueryImplToJson(
        _$VectorSearchQueryImpl instance) =>
    <String, dynamic>{
      'query': instance.query,
      'k': instance.k,
      'threshold': instance.threshold,
      'entityTypes': instance.entityTypes,
      'tags': instance.tags,
      'metadata': instance.metadata,
      'dateFrom': instance.dateFrom?.toIso8601String(),
      'dateTo': instance.dateTo?.toIso8601String(),
    };

_$SimilarityResultImpl _$$SimilarityResultImplFromJson(
        Map<String, dynamic> json) =>
    _$SimilarityResultImpl(
      sourceId: json['sourceId'] as String,
      targetId: json['targetId'] as String,
      similarity: (json['similarity'] as num?)?.toDouble() ?? 0.0,
      sourceContent: json['sourceContent'] as String?,
      targetContent: json['targetContent'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$SimilarityResultImplToJson(
        _$SimilarityResultImpl instance) =>
    <String, dynamic>{
      'sourceId': instance.sourceId,
      'targetId': instance.targetId,
      'similarity': instance.similarity,
      'sourceContent': instance.sourceContent,
      'targetContent': instance.targetContent,
      'metadata': instance.metadata,
    };

_$ClusterResultImpl _$$ClusterResultImplFromJson(Map<String, dynamic> json) =>
    _$ClusterResultImpl(
      clusterId: (json['clusterId'] as num).toInt(),
      label: json['label'] as String,
      entityIds: (json['entityIds'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      coherence: (json['coherence'] as num?)?.toDouble() ?? 0.0,
      keywords: (json['keywords'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$ClusterResultImplToJson(_$ClusterResultImpl instance) =>
    <String, dynamic>{
      'clusterId': instance.clusterId,
      'label': instance.label,
      'entityIds': instance.entityIds,
      'coherence': instance.coherence,
      'keywords': instance.keywords,
      'metadata': instance.metadata,
    };

_$VectorMetricsImpl _$$VectorMetricsImplFromJson(Map<String, dynamic> json) =>
    _$VectorMetricsImpl(
      totalVectors: (json['totalVectors'] as num?)?.toInt() ?? 0,
      dimension: (json['dimension'] as num?)?.toInt() ?? 0,
      indexType: json['indexType'] as String?,
      memoryUsageMb: (json['memoryUsageMb'] as num?)?.toDouble() ?? 0.0,
      searchTimeAvgMs: (json['searchTimeAvgMs'] as num?)?.toDouble() ?? 0.0,
      lastUpdated: json['lastUpdated'] == null
          ? null
          : DateTime.parse(json['lastUpdated'] as String),
    );

Map<String, dynamic> _$$VectorMetricsImplToJson(_$VectorMetricsImpl instance) =>
    <String, dynamic>{
      'totalVectors': instance.totalVectors,
      'dimension': instance.dimension,
      'indexType': instance.indexType,
      'memoryUsageMb': instance.memoryUsageMb,
      'searchTimeAvgMs': instance.searchTimeAvgMs,
      'lastUpdated': instance.lastUpdated?.toIso8601String(),
    };

_$SearchSuggestionImpl _$$SearchSuggestionImplFromJson(
        Map<String, dynamic> json) =>
    _$SearchSuggestionImpl(
      text: json['text'] as String,
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      type: json['type'] as String?,
      matchedTerms: (json['matchedTerms'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$SearchSuggestionImplToJson(
        _$SearchSuggestionImpl instance) =>
    <String, dynamic>{
      'text': instance.text,
      'confidence': instance.confidence,
      'type': instance.type,
      'matchedTerms': instance.matchedTerms,
    };

_$SearchHistoryImpl _$$SearchHistoryImplFromJson(Map<String, dynamic> json) =>
    _$SearchHistoryImpl(
      id: json['id'] as String,
      query: json['query'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      resultsCount: (json['resultsCount'] as num?)?.toInt() ?? 0,
      searchTime: (json['searchTime'] as num?)?.toDouble() ?? 0.0,
    );

Map<String, dynamic> _$$SearchHistoryImplToJson(_$SearchHistoryImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'query': instance.query,
      'timestamp': instance.timestamp.toIso8601String(),
      'resultsCount': instance.resultsCount,
      'searchTime': instance.searchTime,
    };
