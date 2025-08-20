/// 统一数据模型 - 从daemon层同步的真实数据结构
///
/// 此文件包含所有星空可视化需要的真实数据模型
/// 保持与daemon/models和daemon/services中的数据结构一致
///
/// 作者: Linch Mind 开发团队
/// 创建: 2025-08-20
/// 版本: v1.0 (统一重构版)

import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:flutter/foundation.dart';

part 'unified_data_models.freezed.dart';
part 'unified_data_models.g.dart';

/// =================================
/// Universal Index 数据模型
/// =================================

/// 内容类型枚举 - 对应daemon.services.storage.universal_index_service.ContentType
enum UniversalContentType {
  @JsonValue('file_path')
  filePath('文件路径'),
  @JsonValue('url')
  url('网址'),
  @JsonValue('email')
  email('邮箱'),
  @JsonValue('phone')
  phone('电话'),
  @JsonValue('text')
  text('文本'),
  @JsonValue('contact')
  contact('联系人'),
  @JsonValue('document')
  document('文档'),
  @JsonValue('image')
  image('图片'),
  @JsonValue('audio')
  audio('音频'),
  @JsonValue('video')
  video('视频'),
  @JsonValue('code')
  code('代码'),
  @JsonValue('other')
  other('其他');

  const UniversalContentType(this.displayName);
  final String displayName;
}

/// 索引层级 - 对应daemon.services.storage.universal_index_service.IndexTier
enum IndexTier {
  @JsonValue('hot')
  hot('极速搜索'),
  @JsonValue('warm')
  warm('标准搜索'),
  @JsonValue('cold')
  cold('语义搜索');

  const IndexTier(this.displayName);
  final String displayName;
}

/// 通用索引条目 - 对应daemon.services.storage.universal_index_service.UniversalIndexEntry
@freezed
class UniversalIndexEntry with _$UniversalIndexEntry {
  const factory UniversalIndexEntry({
    required String id,
    required String connectorId,
    required UniversalContentType contentType,
    required String primaryKey,
    required String searchableText,
    required String displayName,
    required IndexTier indexTier,
    @Default(5) int priority,
    required DateTime indexedAt,
    DateTime? lastModified,
    DateTime? lastAccessed,
    @Default({}) Map<String, dynamic> structuredData,
    @Default({}) Map<String, dynamic> metadata,
    @Default([]) List<String> keywords,
    @Default([]) List<String> tags,
    // 搜索相关字段
    @Default(0.0) double score,
    String? snippet,
    // 扩展方法需要的字段
    @Default('') String title,
    String? summary,
    String? content,
  }) = _UniversalIndexEntry;

  factory UniversalIndexEntry.fromJson(Map<String, dynamic> json) =>
      _$UniversalIndexEntryFromJson(json);
}

/// 索引搜索结果
@freezed
class IndexSearchResult with _$IndexSearchResult {
  const factory IndexSearchResult({
    required String query,
    required List<UniversalIndexEntry> results,
    required int totalCount,
    required Duration searchTime,
    Map<String, int>? facets,
  }) = _IndexSearchResult;

  factory IndexSearchResult.fromJson(Map<String, dynamic> json) =>
      _$IndexSearchResultFromJson(json);
}

/// =================================
/// Entity 数据模型
/// =================================

/// 实体类型枚举 - 对应daemon数据库模型
enum UnifiedEntityType {
  @JsonValue('file')
  file('文件', 'document'),
  @JsonValue('person')
  person('人物', 'person'),
  @JsonValue('concept')
  concept('概念', 'concept'),
  @JsonValue('project')
  project('项目', 'project'),
  @JsonValue('reference')
  reference('引用', 'reference'),
  @JsonValue('unknown')
  unknown('未知', 'unknown');

  const UnifiedEntityType(this.displayName, this.category);

  final String displayName;
  final String category;
}

/// 实体元数据 - 对应daemon.models.database_models.EntityMetadata
@freezed
class UnifiedEntityMetadata with _$UnifiedEntityMetadata {
  const factory UnifiedEntityMetadata({
    required String entityId,
    required String name,
    required UnifiedEntityType type,
    String? description,
    Map<String, dynamic>? properties,
    @Default([]) List<String> tags,
    @Default(0) int accessCount,
    DateTime? lastAccessed,
    required DateTime createdAt,
    required DateTime updatedAt,
    // 扩展字段用于星空可视化
    String? entityType,
    String? displayName,
    @Default(0.0) double importance,
  }) = _UnifiedEntityMetadata;

  factory UnifiedEntityMetadata.fromJson(Map<String, dynamic> json) =>
      _$UnifiedEntityMetadataFromJson(json);
}

/// 实体关系 - 对应daemon.models.database_models.EntityRelationship
@freezed
class UnifiedEntityRelationship with _$UnifiedEntityRelationship {
  const factory UnifiedEntityRelationship({
    required String sourceEntityId,
    required String targetEntityId,
    required String relationshipType,
    @Default(1) int strength,
    String? description,
    Map<String, dynamic>? properties,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _UnifiedEntityRelationship;

  factory UnifiedEntityRelationship.fromJson(Map<String, dynamic> json) =>
      _$UnifiedEntityRelationshipFromJson(json);
}

/// =================================
/// Graph 数据模型
/// =================================

/// 图节点 - NetworkX节点的表示
@freezed
class GraphNode with _$GraphNode {
  const factory GraphNode({
    required String id,
    required String label,
    String? nodeType,
    Map<String, dynamic>? attributes,
    @Default(1.0) double weight,
    @Default(1.0) double importance,
    @Default(0.0) double centralityScore,
  }) = _GraphNode;

  factory GraphNode.fromJson(Map<String, dynamic> json) =>
      _$GraphNodeFromJson(json);
}

/// 图边 - NetworkX边的表示
@freezed
class GraphEdge with _$GraphEdge {
  const factory GraphEdge({
    required String source,
    required String target,
    String? edgeType,
    @Default(1.0) double weight,
    Map<String, dynamic>? attributes,
  }) = _GraphEdge;

  factory GraphEdge.fromJson(Map<String, dynamic> json) =>
      _$GraphEdgeFromJson(json);
}

/// 图数据 - 完整的NetworkX图谱
@freezed
class UnifiedGraphData with _$UnifiedGraphData {
  const factory UnifiedGraphData({
    required List<GraphNode> nodes,
    required List<GraphEdge> edges,
    Map<String, dynamic>? graphAttributes,
    String? graphType,
    @Default(false) bool isDirected,
    required DateTime lastUpdated,
    Map<String, List<String>>? clusters,
    Map<String, double>? centrality,
  }) = _UnifiedGraphData;

  factory UnifiedGraphData.fromJson(Map<String, dynamic> json) =>
      _$UnifiedGraphDataFromJson(json);
}

/// =================================
/// Vector 数据模型
/// =================================

/// 向量文档 - 对应daemon.services.storage.faiss_vector_store.VectorDocument
@freezed
class UnifiedVectorDocument with _$UnifiedVectorDocument {
  const factory UnifiedVectorDocument({
    required String documentId,
    required String content,
    String? title,
    String? contentType,
    Map<String, dynamic>? metadata,
    required List<double> embedding,
    @Default(0.0) double score,
    String? sourceConnector,
    String? sourcePath,
    required DateTime timestamp,
  }) = _UnifiedVectorDocument;

  factory UnifiedVectorDocument.fromJson(Map<String, dynamic> json) =>
      _$UnifiedVectorDocumentFromJson(json);
}

/// 向量搜索结果
@freezed
class VectorSearchResult with _$VectorSearchResult {
  const factory VectorSearchResult({
    required String query,
    required List<double> queryEmbedding,
    required List<UnifiedVectorDocument> results,
    required int totalCount,
    required Duration searchTime,
    @Default('cosine') String similarityMetric,
  }) = _VectorSearchResult;

  factory VectorSearchResult.fromJson(Map<String, dynamic> json) =>
      _$VectorSearchResultFromJson(json);
}

/// 向量聚类结果
@freezed
class VectorCluster with _$VectorCluster {
  const factory VectorCluster({
    required String clusterId,
    required List<String> documentIds,
    required List<double> centroid,
    @Default(0.0) double cohesion,
    String? topic,
    List<String>? keywords,
  }) = _VectorCluster;

  factory VectorCluster.fromJson(Map<String, dynamic> json) =>
      _$VectorClusterFromJson(json);
}

/// =================================
/// 统一响应包装
/// =================================

/// API响应基类
@freezed
class UnifiedApiResponse with _$UnifiedApiResponse {
  const factory UnifiedApiResponse({
    required bool success,
    Map<String, dynamic>? data,
    String? error,
    String? message,
    Map<String, dynamic>? metadata,
    required DateTime timestamp,
  }) = _UnifiedApiResponse;

  factory UnifiedApiResponse.fromJson(Map<String, dynamic> json) =>
      _$UnifiedApiResponseFromJson(json);
}

/// =================================
/// 数据统计模型
/// =================================

/// 数据源统计
@freezed
class DataSourceStats with _$DataSourceStats {
  const factory DataSourceStats({
    required String dataType,
    required int totalCount,
    required int activeCount,
    required DateTime lastUpdated,
    Map<String, int>? breakdown,
    Map<String, dynamic>? metrics,
  }) = _DataSourceStats;

  factory DataSourceStats.fromJson(Map<String, dynamic> json) =>
      _$DataSourceStatsFromJson(json);
}

/// =================================
/// 辅助扩展方法
/// =================================

extension UniversalIndexEntryExtensions on UniversalIndexEntry {
  /// 获取显示标题
  String get displayTitle => title.isNotEmpty ? title : id;

  /// 获取显示摘要
  String get displaySummary => snippet ?? summary ?? content ?? '';

  /// 是否高质量结果
  bool get isHighQuality => score >= 0.8;

  /// 获取内容类型显示名
  String get contentTypeDisplay {
    return contentType.displayName;
  }
}

extension UnifiedEntityMetadataExtensions on UnifiedEntityMetadata {
  /// 获取重要性分数
  double get importanceScore {
    final baseScore = accessCount > 0 ? 0.3 : 0.1;
    final activityScore = lastAccessed != null ? 0.3 : 0.0;
    final ageScore = _calculateAgeScore();
    return (baseScore + activityScore + ageScore).clamp(0.0, 1.0);
  }

  double _calculateAgeScore() {
    final now = DateTime.now();
    final daysSinceCreated = now.difference(createdAt).inDays;
    if (daysSinceCreated < 7) return 0.4;
    if (daysSinceCreated < 30) return 0.3;
    if (daysSinceCreated < 90) return 0.2;
    return 0.1;
  }

  /// 获取活跃度
  bool get isActive =>
      lastAccessed != null &&
      DateTime.now().difference(lastAccessed!).inDays < 30;
}

extension UnifiedGraphDataExtensions on UnifiedGraphData {
  /// 获取节点数量
  int get nodeCount => nodes.length;

  /// 获取边数量
  int get edgeCount => edges.length;

  /// 获取图密度
  double get density {
    if (nodeCount <= 1) return 0.0;
    final maxEdges = isDirected
        ? nodeCount * (nodeCount - 1)
        : nodeCount * (nodeCount - 1) / 2;
    return edgeCount / maxEdges;
  }

  /// 获取平均度数
  double get averageDegree {
    if (nodeCount == 0) return 0.0;
    return (2 * edgeCount) / nodeCount;
  }
}

extension UnifiedVectorDocumentExtensions on UnifiedVectorDocument {
  /// 获取嵌入维度
  int get embeddingDimension => embedding.length;

  /// 获取内容长度
  int get contentLength => content.length;

  /// 是否高相似度结果
  bool get isHighSimilarity => score >= 0.8;

  /// 获取内容预览
  String getContentPreview([int maxLength = 100]) {
    if (content.length <= maxLength) return content;
    return '${content.substring(0, maxLength)}...';
  }
}
