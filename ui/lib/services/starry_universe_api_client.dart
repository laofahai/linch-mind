/// 星空宇宙API客户端 - 为星空可视化提供真实数据源
///
/// 通过IPC协议从daemon获取Entity、Graph、Vector、UniversalIndex数据
/// 替代原有的模拟数据，实现真实数据可视化
///
/// 作者: Linch Mind 开发团队
/// 创建: 2025-08-20
/// 版本: v1.0 (架构统一版)

import '../models/unified_data_models.dart';
import '../models/ipc_protocol.dart';
import 'ipc_client.dart';
import '../utils/app_logger.dart';

/// 星空宇宙数据API客户端
class StarryUniverseApiClient {
  static StarryUniverseApiClient? _instance;

  /// 获取单例实例
  static StarryUniverseApiClient get instance {
    _instance ??= StarryUniverseApiClient._internal();
    return _instance!;
  }

  StarryUniverseApiClient._internal();

  final IPCClient _ipcClient = IPCService.instance;

  // ================================
  // Entity 数据接口
  // ================================

  /// 获取实体数据 - 智慧星座可视化
  Future<EntityDataResponse> getEntities({
    int limit = 100,
    List<String>? entityTypes,
    bool includeRelationships = true,
    double importanceThreshold = 0.0,
  }) async {
    try {
      AppLogger.info('获取实体数据', module: 'StarryUniverseApi', data: {
        'limit': limit,
        'entity_types': entityTypes,
        'include_relationships': includeRelationships,
      });

      final request = IPCRequest(
        path: '/starry_universe/entities',
        method: 'GET',
        data: {
          'limit': limit,
          if (entityTypes != null) 'entity_types': entityTypes,
          'include_relationships': includeRelationships,
          'importance_threshold': importanceThreshold,
        },
      );

      final response = await _ipcClient.sendRequest(request);

      if (response.success) {
        AppLogger.info('实体数据获取成功', module: 'StarryUniverseApi', data: {
          'entities_count': response.data?['entities']?.length ?? 0,
          'relationships_count': response.data?['relationships']?.length ?? 0,
        });

        return EntityDataResponse.fromJson(response.data ?? {});
      } else {
        throw Exception('获取实体数据失败: ${response.error}');
      }
    } catch (e) {
      AppLogger.error('获取实体数据异常', module: 'StarryUniverseApi', exception: e);
      rethrow;
    }
  }

  /// 获取单个实体详情
  Future<EntityDetailResponse> getEntityDetails(String entityId) async {
    try {
      final request = IPCRequest(
        path: '/starry_universe/entities/$entityId',
        method: 'GET',
      );

      final response = await _ipcClient.sendRequest(request);

      if (response.success) {
        return EntityDetailResponse.fromJson(response.data ?? {});
      } else {
        throw Exception('获取实体详情失败: ${response.error}');
      }
    } catch (e) {
      AppLogger.error('获取实体详情异常', module: 'StarryUniverseApi', exception: e);
      rethrow;
    }
  }

  // ================================
  // Graph 数据接口
  // ================================

  /// 获取知识图谱数据 - 知识宇宙可视化
  Future<GraphDataResponse> getGraphData({
    int maxNodes = 500,
    int maxEdges = 1000,
    bool includeCentrality = true,
    bool includeClusters = true,
    List<String>? nodeTypes,
    double minEdgeWeight = 0.0,
  }) async {
    try {
      AppLogger.info('获取图谱数据', module: 'StarryUniverseApi', data: {
        'max_nodes': maxNodes,
        'max_edges': maxEdges,
        'include_centrality': includeCentrality,
      });

      final request = IPCRequest(
        path: '/starry_universe/graph',
        method: 'GET',
        data: {
          'max_nodes': maxNodes,
          'max_edges': maxEdges,
          'include_centrality': includeCentrality,
          'include_clusters': includeClusters,
          if (nodeTypes != null) 'node_types': nodeTypes,
          'min_edge_weight': minEdgeWeight,
        },
      );

      final response = await _ipcClient.sendRequest(request);

      if (response.success) {
        AppLogger.info('图谱数据获取成功', module: 'StarryUniverseApi', data: {
          'nodes_count': response.data?['nodes']?.length ?? 0,
          'edges_count': response.data?['edges']?.length ?? 0,
        });

        return GraphDataResponse.fromJson(response.data ?? {});
      } else {
        throw Exception('获取图谱数据失败: ${response.error}');
      }
    } catch (e) {
      AppLogger.error('获取图谱数据异常', module: 'StarryUniverseApi', exception: e);
      rethrow;
    }
  }

  // ================================
  // Vector 数据接口
  // ================================

  /// 获取向量数据 - 相似星云可视化
  Future<VectorDataResponse> getVectorData({
    int limit = 200,
    bool includeEmbeddings = false,
    int clusterCount = 10,
    double similarityThreshold = 0.7,
    List<String>? contentTypes,
  }) async {
    try {
      AppLogger.info('获取向量数据', module: 'StarryUniverseApi', data: {
        'limit': limit,
        'cluster_count': clusterCount,
        'similarity_threshold': similarityThreshold,
      });

      final request = IPCRequest(
        path: '/starry_universe/vectors',
        method: 'GET',
        data: {
          'limit': limit,
          'include_embeddings': includeEmbeddings,
          'cluster_count': clusterCount,
          'similarity_threshold': similarityThreshold,
          if (contentTypes != null) 'content_types': contentTypes,
        },
      );

      final response = await _ipcClient.sendRequest(request);

      if (response.success) {
        AppLogger.info('向量数据获取成功', module: 'StarryUniverseApi', data: {
          'documents_count': response.data?['documents']?.length ?? 0,
          'clusters_count': response.data?['clusters']?.length ?? 0,
        });

        return VectorDataResponse.fromJson(response.data ?? {});
      } else {
        throw Exception('获取向量数据失败: ${response.error}');
      }
    } catch (e) {
      AppLogger.error('获取向量数据异常', module: 'StarryUniverseApi', exception: e);
      rethrow;
    }
  }

  /// 向量语义搜索
  Future<VectorSearchResponse> searchVectors({
    required String query,
    int limit = 20,
    double similarityThreshold = 0.7,
  }) async {
    try {
      final request = IPCRequest(
        path: '/starry_universe/vectors/search',
        method: 'POST',
        data: {
          'query': query,
          'limit': limit,
          'similarity_threshold': similarityThreshold,
        },
      );

      final response = await _ipcClient.sendRequest(request);

      if (response.success) {
        return VectorSearchResponse.fromJson(response.data ?? {});
      } else {
        throw Exception('向量搜索失败: ${response.error}');
      }
    } catch (e) {
      AppLogger.error('向量搜索异常', module: 'StarryUniverseApi', exception: e);
      rethrow;
    }
  }

  // ================================
  // Universal Index 数据接口
  // ================================

  /// 通用索引搜索 - 搜索星河可视化
  Future<IndexSearchResponse> searchUniversalIndex({
    required String query,
    int limit = 100,
    List<String>? contentTypes,
    List<String>? connectorIds,
    List<String>? indexTiers,
    bool includeMetadata = false,
  }) async {
    try {
      AppLogger.info('执行通用索引搜索', module: 'StarryUniverseApi', data: {
        'query': query,
        'limit': limit,
      });

      final request = IPCRequest(
        path: '/search/universal',
        method: 'POST',
        data: {
          'query': query,
          'limit': limit,
          if (contentTypes != null) 'content_types': contentTypes,
          if (connectorIds != null) 'connector_ids': connectorIds,
          if (indexTiers != null) 'index_tiers': indexTiers,
          'include_metadata': includeMetadata,
        },
      );

      final response = await _ipcClient.sendRequest(request);

      if (response.success) {
        AppLogger.info('通用索引搜索成功', module: 'StarryUniverseApi', data: {
          'results_count': response.data?['results']?.length ?? 0,
          'search_time_ms': response.data?['search_time_ms'],
        });

        return IndexSearchResponse.fromJson(response.data ?? {});
      } else {
        throw Exception('通用索引搜索失败: ${response.error}');
      }
    } catch (e) {
      AppLogger.error('通用索引搜索异常', module: 'StarryUniverseApi', exception: e);
      rethrow;
    }
  }

  // ================================
  // 统一数据接口
  // ================================

  /// 获取星空宇宙统一数据 - 一次性获取所有数据类型
  Future<UnifiedStarryDataResponse> getUnifiedData({
    bool includeEntities = true,
    bool includeGraph = true,
    bool includeVectors = true,
    bool includeUniversalIndex = true,
    Map<String, int>? dataLimits,
  }) async {
    try {
      AppLogger.info('获取星空宇宙统一数据', module: 'StarryUniverseApi');

      final request = IPCRequest(
        path: '/starry_universe/unified',
        method: 'GET',
        data: {
          'include_entities': includeEntities,
          'include_graph': includeGraph,
          'include_vectors': includeVectors,
          'include_universal_index': includeUniversalIndex,
          if (dataLimits != null) 'data_limits': dataLimits,
        },
      );

      final response = await _ipcClient.sendRequest(request);

      if (response.success) {
        final summary = response.data?['data_summary'] ?? {};
        AppLogger.info('星空宇宙统一数据获取成功', module: 'StarryUniverseApi', data: {
          'fetch_time_ms': summary['fetch_time_ms'],
          'included_data_types': summary['included_data_types'],
        });

        return UnifiedStarryDataResponse.fromJson(response.data ?? {});
      } else {
        throw Exception('获取统一数据失败: ${response.error}');
      }
    } catch (e) {
      AppLogger.error('获取统一数据异常', module: 'StarryUniverseApi', exception: e);
      rethrow;
    }
  }

  // ================================
  // 数据统计接口
  // ================================

  /// 获取搜索统计信息
  Future<SearchStatsResponse> getSearchStats() async {
    try {
      final request = IPCRequest(
        path: '/search/stats',
        method: 'GET',
      );

      final response = await _ipcClient.sendRequest(request);

      if (response.success) {
        return SearchStatsResponse.fromJson(response.data ?? {});
      } else {
        throw Exception('获取搜索统计失败: ${response.error}');
      }
    } catch (e) {
      AppLogger.error('获取搜索统计异常', module: 'StarryUniverseApi', exception: e);
      rethrow;
    }
  }

  /// 获取性能指标
  Future<PerformanceMetricsResponse> getPerformanceMetrics() async {
    try {
      final request = IPCRequest(
        path: '/search/performance',
        method: 'GET',
      );

      final response = await _ipcClient.sendRequest(request);

      if (response.success) {
        return PerformanceMetricsResponse.fromJson(response.data ?? {});
      } else {
        throw Exception('获取性能指标失败: ${response.error}');
      }
    } catch (e) {
      AppLogger.error('获取性能指标异常', module: 'StarryUniverseApi', exception: e);
      rethrow;
    }
  }
}

// ================================
// 响应数据模型
// ================================

/// 实体数据响应
class EntityDataResponse {
  final List<UnifiedEntityMetadata> entities;
  final List<UnifiedEntityRelationship> relationships;
  final int totalCount;
  final Map<String, dynamic> stats;
  final Map<String, dynamic> queryInfo;

  EntityDataResponse({
    required this.entities,
    required this.relationships,
    required this.totalCount,
    required this.stats,
    required this.queryInfo,
  });

  factory EntityDataResponse.fromJson(Map<String, dynamic> json) {
    return EntityDataResponse(
      entities: (json['entities'] as List? ?? [])
          .map((e) => UnifiedEntityMetadata.fromJson(e))
          .toList(),
      relationships: (json['relationships'] as List? ?? [])
          .map((e) => UnifiedEntityRelationship.fromJson(e))
          .toList(),
      totalCount: json['total_count'] ?? 0,
      stats: json['stats'] ?? {},
      queryInfo: json['query_info'] ?? {},
    );
  }
}

/// 实体详情响应
class EntityDetailResponse {
  final UnifiedEntityMetadata entity;
  final List<UnifiedEntityRelationship> relationships;
  final List<UnifiedEntityMetadata> relatedEntities;
  final String entityId;

  EntityDetailResponse({
    required this.entity,
    required this.relationships,
    required this.relatedEntities,
    required this.entityId,
  });

  factory EntityDetailResponse.fromJson(Map<String, dynamic> json) {
    return EntityDetailResponse(
      entity: UnifiedEntityMetadata.fromJson(json['entity']),
      relationships: (json['relationships'] as List? ?? [])
          .map((e) => UnifiedEntityRelationship.fromJson(e))
          .toList(),
      relatedEntities: (json['related_entities'] as List? ?? [])
          .map((e) => UnifiedEntityMetadata.fromJson(e))
          .toList(),
      entityId: json['entity_id'] ?? '',
    );
  }
}

/// 图数据响应
class GraphDataResponse {
  final List<GraphNode> nodes;
  final List<GraphEdge> edges;
  final Map<String, List<String>> clusters;
  final Map<String, dynamic> graphMetrics;
  final Map<String, dynamic> centralityMetrics;
  final Map<String, dynamic> queryInfo;

  GraphDataResponse({
    required this.nodes,
    required this.edges,
    required this.clusters,
    required this.graphMetrics,
    required this.centralityMetrics,
    required this.queryInfo,
  });

  factory GraphDataResponse.fromJson(Map<String, dynamic> json) {
    return GraphDataResponse(
      nodes: (json['nodes'] as List? ?? [])
          .map((e) => GraphNode.fromJson(e))
          .toList(),
      edges: (json['edges'] as List? ?? [])
          .map((e) => GraphEdge.fromJson(e))
          .toList(),
      clusters: Map<String, List<String>>.from(json['clusters'] ?? {}),
      graphMetrics: json['graph_metrics'] ?? {},
      centralityMetrics: json['centrality_metrics'] ?? {},
      queryInfo: json['query_info'] ?? {},
    );
  }
}

/// 向量数据响应
class VectorDataResponse {
  final List<UnifiedVectorDocument> documents;
  final List<VectorCluster> clusters;
  final Map<String, Map<String, double>> similarityMatrix;
  final Map<String, dynamic> vectorStats;
  final Map<String, dynamic> queryInfo;

  VectorDataResponse({
    required this.documents,
    required this.clusters,
    required this.similarityMatrix,
    required this.vectorStats,
    required this.queryInfo,
  });

  factory VectorDataResponse.fromJson(Map<String, dynamic> json) {
    return VectorDataResponse(
      documents: (json['documents'] as List? ?? [])
          .map((e) => UnifiedVectorDocument.fromJson(e))
          .toList(),
      clusters: (json['clusters'] as List? ?? [])
          .map((e) => VectorCluster.fromJson(e))
          .toList(),
      similarityMatrix: _parseSimilarityMatrix(json['similarity_matrix']),
      vectorStats: json['vector_stats'] ?? {},
      queryInfo: json['query_info'] ?? {},
    );
  }

  static Map<String, Map<String, double>> _parseSimilarityMatrix(dynamic data) {
    if (data is! Map) return {};
    final result = <String, Map<String, double>>{};
    for (final entry in data.entries) {
      if (entry.value is Map) {
        result[entry.key] = Map<String, double>.from(entry.value);
      }
    }
    return result;
  }
}

/// 向量搜索响应
class VectorSearchResponse {
  final String query;
  final List<UnifiedVectorDocument> results;
  final int totalResults;
  final double similarityThreshold;

  VectorSearchResponse({
    required this.query,
    required this.results,
    required this.totalResults,
    required this.similarityThreshold,
  });

  factory VectorSearchResponse.fromJson(Map<String, dynamic> json) {
    return VectorSearchResponse(
      query: json['query'] ?? '',
      results: (json['results'] as List? ?? [])
          .map((e) => UnifiedVectorDocument.fromJson(e))
          .toList(),
      totalResults: json['total_results'] ?? 0,
      similarityThreshold: json['similarity_threshold']?.toDouble() ?? 0.0,
    );
  }
}

/// 索引搜索响应
class IndexSearchResponse {
  final List<UniversalIndexEntry> results;
  final int totalResults;
  final double searchTimeMs;
  final String performanceTier;
  final Map<String, dynamic> queryInfo;

  IndexSearchResponse({
    required this.results,
    required this.totalResults,
    required this.searchTimeMs,
    required this.performanceTier,
    required this.queryInfo,
  });

  factory IndexSearchResponse.fromJson(Map<String, dynamic> json) {
    return IndexSearchResponse(
      results: (json['results'] as List? ?? [])
          .map((e) => UniversalIndexEntry.fromJson(e))
          .toList(),
      totalResults: json['total_results'] ?? 0,
      searchTimeMs: json['search_time_ms']?.toDouble() ?? 0.0,
      performanceTier: json['performance_tier'] ?? '',
      queryInfo: json['query_info'] ?? {},
    );
  }
}

/// 统一星空数据响应
class UnifiedStarryDataResponse {
  final EntityDataResponse? entities;
  final GraphDataResponse? graph;
  final VectorDataResponse? vectors;
  final IndexSearchResponse? universalIndex;
  final Map<String, dynamic> dataSummary;

  UnifiedStarryDataResponse({
    this.entities,
    this.graph,
    this.vectors,
    this.universalIndex,
    required this.dataSummary,
  });

  factory UnifiedStarryDataResponse.fromJson(Map<String, dynamic> json) {
    return UnifiedStarryDataResponse(
      entities: json['entities'] != null
          ? EntityDataResponse.fromJson(json['entities'])
          : null,
      graph: json['graph'] != null
          ? GraphDataResponse.fromJson(json['graph'])
          : null,
      vectors: json['vectors'] != null
          ? VectorDataResponse.fromJson(json['vectors'])
          : null,
      universalIndex: json['universal_index'] != null
          ? IndexSearchResponse.fromJson(json['universal_index'])
          : null,
      dataSummary: json['data_summary'] ?? {},
    );
  }
}

/// 搜索统计响应
class SearchStatsResponse {
  final int totalEntries;
  final Map<String, int> entriesByTier;
  final Map<String, int> entriesByType;
  final Map<String, int> entriesByConnector;
  final int searchRequests;
  final double avgSearchTimeMs;
  final int databaseSize;

  SearchStatsResponse({
    required this.totalEntries,
    required this.entriesByTier,
    required this.entriesByType,
    required this.entriesByConnector,
    required this.searchRequests,
    required this.avgSearchTimeMs,
    required this.databaseSize,
  });

  factory SearchStatsResponse.fromJson(Map<String, dynamic> json) {
    return SearchStatsResponse(
      totalEntries: json['total_entries'] ?? 0,
      entriesByTier: Map<String, int>.from(json['entries_by_tier'] ?? {}),
      entriesByType: Map<String, int>.from(json['entries_by_type'] ?? {}),
      entriesByConnector:
          Map<String, int>.from(json['entries_by_connector'] ?? {}),
      searchRequests: json['search_requests'] ?? 0,
      avgSearchTimeMs: json['avg_search_time_ms']?.toDouble() ?? 0.0,
      databaseSize: json['database_size'] ?? 0,
    );
  }
}

/// 性能指标响应
class PerformanceMetricsResponse {
  final Map<String, dynamic> searchPerformance;
  final Map<String, dynamic> indexPerformance;
  final Map<String, dynamic> storageBreakdown;
  final Map<String, dynamic> systemHealth;

  PerformanceMetricsResponse({
    required this.searchPerformance,
    required this.indexPerformance,
    required this.storageBreakdown,
    required this.systemHealth,
  });

  factory PerformanceMetricsResponse.fromJson(Map<String, dynamic> json) {
    return PerformanceMetricsResponse(
      searchPerformance: json['search_performance'] ?? {},
      indexPerformance: json['index_performance'] ?? {},
      storageBreakdown: json['storage_breakdown'] ?? {},
      systemHealth: json['system_health'] ?? {},
    );
  }
}
