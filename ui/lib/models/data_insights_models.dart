// 数据洞察相关的数据模型
import 'package:freezed_annotation/freezed_annotation.dart';

part 'data_insights_models.freezed.dart';
part 'data_insights_models.g.dart';

/// 今日统计数据
@freezed
class TodayStats with _$TodayStats {
  const factory TodayStats({
    @Default(0) int newEntities,
    @Default(0) int activeConnectors,
    @Default(0) int aiAnalysisCompleted,
    @Default(0) int knowledgeConnections,
  }) = _TodayStats;

  factory TodayStats.fromJson(Map<String, dynamic> json) =>
      _$TodayStatsFromJson(json);
}

/// 实体类型分布
@freezed
class EntityBreakdown with _$EntityBreakdown {
  const factory EntityBreakdown({
    @Default(0) int url,
    @Default(0) int filePath,
    @Default(0) int email,
    @Default(0) int phone,
    @Default(0) int keyword,
    @Default(0) int other,
  }) = _EntityBreakdown;

  factory EntityBreakdown.fromJson(Map<String, dynamic> json) =>
      _$EntityBreakdownFromJson(json);
}

/// AI洞察项
@freezed
class AIInsight with _$AIInsight {
  const factory AIInsight({
    required String type,
    required String title,
    required String description,
    @Default(0.0) double confidence,
    @Default([]) List<String> entities,
    DateTime? detectedAt,
    String? iconName,
    String? actionLabel,
  }) = _AIInsight;

  factory AIInsight.fromJson(Map<String, dynamic> json) =>
      _$AIInsightFromJson(json);
}

/// 趋势实体
@freezed
class TrendingEntity with _$TrendingEntity {
  const factory TrendingEntity({
    required String name,
    required String type,
    @Default(0) int frequency,
    String? trend,
    double? trendValue,
    String? description,
  }) = _TrendingEntity;

  factory TrendingEntity.fromJson(Map<String, dynamic> json) =>
      _$TrendingEntityFromJson(json);
}

/// 实体详情
@freezed
class EntityDetail with _$EntityDetail {
  const factory EntityDetail({
    required String id,
    required String name,
    required String type,
    String? description,
    DateTime? createdAt,
    DateTime? lastAccessed,
    @Default(0) int accessCount,
    Map<String, dynamic>? properties,
    @Default([]) List<String> tags,
  }) = _EntityDetail;

  factory EntityDetail.fromJson(Map<String, dynamic> json) =>
      _$EntityDetailFromJson(json);
}

/// 活动时间线项
@freezed
class TimelineItem with _$TimelineItem {
  const factory TimelineItem({
    required String id,
    required String title,
    String? description,
    required DateTime timestamp,
    required String type, // 'entity_created', 'insight_generated', 'connector_activity'
    Map<String, dynamic>? metadata,
    String? iconName,
    String? connectorId,
  }) = _TimelineItem;

  factory TimelineItem.fromJson(Map<String, dynamic> json) =>
      _$TimelineItemFromJson(json);
}

/// 连接器状态
@freezed
class ConnectorStatus with _$ConnectorStatus {
  const factory ConnectorStatus({
    required String id,
    required String name,
    required String status, // 'running', 'stopped', 'error'
    @Default(true) bool enabled,
    @Default(0) int dataCount,
    DateTime? lastHeartbeat,
    String? errorMessage,
  }) = _ConnectorStatus;

  factory ConnectorStatus.fromJson(Map<String, dynamic> json) =>
      _$ConnectorStatusFromJson(json);
}

/// 数据洞察概览
@freezed
class DataInsightsOverview with _$DataInsightsOverview {
  const factory DataInsightsOverview({
    required TodayStats todayStats,
    required EntityBreakdown entityBreakdown,
    @Default([]) List<AIInsight> recentInsights,
    @Default([]) List<TrendingEntity> trendingEntities,
    @Default([]) List<TimelineItem> recentActivities,
    @Default([]) List<ConnectorStatus> connectorStatuses,
    DateTime? lastUpdated,
  }) = _DataInsightsOverview;

  factory DataInsightsOverview.fromJson(Map<String, dynamic> json) =>
      _$DataInsightsOverviewFromJson(json);
}

/// 筛选选项
@freezed
class FilterOptions with _$FilterOptions {
  const factory FilterOptions({
    @Default([]) List<String> entityTypes,
    @Default([]) List<String> connectorIds,
    DateTime? startDate,
    DateTime? endDate,
    String? searchQuery,
  }) = _FilterOptions;

  factory FilterOptions.fromJson(Map<String, dynamic> json) =>
      _$FilterOptionsFromJson(json);
}

/// 向量搜索结果
@freezed
class VectorSearchResult with _$VectorSearchResult {
  const factory VectorSearchResult({
    required String id,
    required String content,
    @Default(0.0) double similarity,
    Map<String, dynamic>? metadata,
    String? entityId,
    String? entityType,
    DateTime? timestamp,
    @Default([]) List<String> highlightedTerms,
  }) = _VectorSearchResult;

  factory VectorSearchResult.fromJson(Map<String, dynamic> json) =>
      _$VectorSearchResultFromJson(json);
}

/// 向量搜索查询参数
@freezed
class VectorSearchQuery with _$VectorSearchQuery {
  const factory VectorSearchQuery({
    required String query,
    @Default(10) int k,
    @Default(0.0) double threshold,
    @Default([]) List<String> entityTypes,
    @Default([]) List<String> tags,
    Map<String, dynamic>? metadata,
    DateTime? dateFrom,
    DateTime? dateTo,
  }) = _VectorSearchQuery;

  factory VectorSearchQuery.fromJson(Map<String, dynamic> json) =>
      _$VectorSearchQueryFromJson(json);
}

/// 相似性计算结果
@freezed
class SimilarityResult with _$SimilarityResult {
  const factory SimilarityResult({
    required String sourceId,
    required String targetId,
    @Default(0.0) double similarity,
    String? sourceContent,
    String? targetContent,
    Map<String, dynamic>? metadata,
  }) = _SimilarityResult;

  factory SimilarityResult.fromJson(Map<String, dynamic> json) =>
      _$SimilarityResultFromJson(json);
}

/// 聚类结果
@freezed
class ClusterResult with _$ClusterResult {
  const factory ClusterResult({
    required int clusterId,
    required String label,
    @Default([]) List<String> entityIds,
    @Default(0.0) double coherence,
    @Default([]) List<String> keywords,
    Map<String, dynamic>? metadata,
  }) = _ClusterResult;

  factory ClusterResult.fromJson(Map<String, dynamic> json) =>
      _$ClusterResultFromJson(json);
}

/// 向量数据库性能指标
@freezed
class VectorMetrics with _$VectorMetrics {
  const factory VectorMetrics({
    @Default(0) int totalVectors,
    @Default(0) int dimension,
    String? indexType,
    @Default(0.0) double memoryUsageMb,
    @Default(0.0) double searchTimeAvgMs,
    DateTime? lastUpdated,
  }) = _VectorMetrics;

  factory VectorMetrics.fromJson(Map<String, dynamic> json) =>
      _$VectorMetricsFromJson(json);
}

/// 搜索建议
@freezed
class SearchSuggestion with _$SearchSuggestion {
  const factory SearchSuggestion({
    required String text,
    @Default(0.0) double confidence,
    String? type,
    @Default([]) List<String> matchedTerms,
  }) = _SearchSuggestion;

  factory SearchSuggestion.fromJson(Map<String, dynamic> json) =>
      _$SearchSuggestionFromJson(json);
}

/// 搜索历史记录
@freezed
class SearchHistory with _$SearchHistory {
  const factory SearchHistory({
    required String id,
    required String query,
    required DateTime timestamp,
    @Default(0) int resultsCount,
    @Default(0.0) double searchTime,
  }) = _SearchHistory;

  factory SearchHistory.fromJson(Map<String, dynamic> json) =>
      _$SearchHistoryFromJson(json);
}