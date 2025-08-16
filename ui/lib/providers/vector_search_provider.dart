// 向量搜索状态管理 - Riverpod Provider
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../models/data_insights_models.dart';
import '../services/data_insights_service.dart';
import '../utils/app_logger.dart';
import 'data_insights_provider.dart';

part 'vector_search_provider.g.dart';

/// 搜索模式枚举
enum SearchMode {
  simple, // 简单搜索
  advanced, // 高级搜索
  similarity, // 相似性搜索
  clustering, // 聚类分析
}

/// 向量搜索状态
class VectorSearchState {
  final List<VectorSearchResult> results;
  final List<SearchSuggestion> suggestions;
  final List<SearchHistory> history;
  final bool isLoading;
  final String? error;
  final SearchMode searchMode;
  final VectorSearchQuery? currentQuery;
  final VectorMetrics? metrics;
  final double? lastSearchDuration;
  final DateTime? lastSearchTime;

  const VectorSearchState({
    this.results = const [],
    this.suggestions = const [],
    this.history = const [],
    this.isLoading = false,
    this.error,
    this.searchMode = SearchMode.simple,
    this.currentQuery,
    this.metrics,
    this.lastSearchDuration,
    this.lastSearchTime,
  });

  VectorSearchState copyWith({
    List<VectorSearchResult>? results,
    List<SearchSuggestion>? suggestions,
    List<SearchHistory>? history,
    bool? isLoading,
    String? error,
    SearchMode? searchMode,
    VectorSearchQuery? currentQuery,
    VectorMetrics? metrics,
    double? lastSearchDuration,
    DateTime? lastSearchTime,
  }) {
    return VectorSearchState(
      results: results ?? this.results,
      suggestions: suggestions ?? this.suggestions,
      history: history ?? this.history,
      isLoading: isLoading ?? this.isLoading,
      error: error, // 始终重置error为传入值
      searchMode: searchMode ?? this.searchMode,
      currentQuery: currentQuery ?? this.currentQuery,
      metrics: metrics ?? this.metrics,
      lastSearchDuration: lastSearchDuration ?? this.lastSearchDuration,
      lastSearchTime: lastSearchTime ?? this.lastSearchTime,
    );
  }
}

/// 主向量搜索Provider
@riverpod
class VectorSearch extends _$VectorSearch {
  late final DataInsightsService _dataService;
  Timer? _suggestionDebounceTimer;
  static const _maxHistorySize = 50;

  @override
  VectorSearchState build() {
    _dataService = ref.read(dataInsightsServiceProvider);
    _loadMetrics(); // 初始化时加载指标
    return const VectorSearchState();
  }

  /// 执行向量搜索
  Future<void> search(VectorSearchQuery query) async {
    final searchStartTime = DateTime.now();
    final stopwatch = Stopwatch()..start();

    state = state.copyWith(isLoading: true, error: null);

    try {
      AppLogger.info('执行向量搜索: ${query.query}', module: 'VectorSearchProvider');

      // 执行搜索
      final results = await _dataService.vectorSearch(query);

      stopwatch.stop();
      final searchDuration = stopwatch.elapsedMilliseconds / 1000.0;

      // 记录搜索历史
      final historyItem = SearchHistory(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        query: query.query,
        timestamp: searchStartTime,
        resultsCount: results.length,
        searchTime: searchDuration,
      );

      final newHistory = [historyItem, ...state.history];
      if (newHistory.length > _maxHistorySize) {
        newHistory.removeRange(_maxHistorySize, newHistory.length);
      }

      state = state.copyWith(
        results: results,
        history: newHistory,
        currentQuery: query,
        lastSearchDuration: searchDuration,
        lastSearchTime: searchStartTime,
        isLoading: false,
      );

      AppLogger.info('向量搜索完成，找到 ${results.length} 个结果',
          module: 'VectorSearchProvider');
    } catch (e) {
      AppLogger.error('向量搜索失败: $e', module: 'VectorSearchProvider');
      state = state.copyWith(
        isLoading: false,
        error: '搜索失败: ${e.toString()}',
      );
    }
  }

  /// 获取搜索建议（防抖处理）
  Future<void> getSuggestions(String query) async {
    if (query.trim().isEmpty) {
      state = state.copyWith(suggestions: []);
      return;
    }

    // 取消之前的定时器
    _suggestionDebounceTimer?.cancel();

    // 设置新的防抖定时器
    _suggestionDebounceTimer =
        Timer(const Duration(milliseconds: 500), () async {
      try {
        final suggestions = await _dataService.getSearchSuggestions(query);

        state = state.copyWith(suggestions: suggestions);
      } catch (e) {
        AppLogger.error('获取搜索建议失败: $e', module: 'VectorSearchProvider');
        // 建议失败不影响主要功能，只记录日志
      }
    });
  }

  /// 设置搜索模式
  void setSearchMode(SearchMode mode) {
    state = state.copyWith(searchMode: mode);
  }

  /// 清除搜索结果
  void clearResults() {
    state = state.copyWith(
      results: [],
      currentQuery: null,
      error: null,
    );
  }

  /// 清除搜索历史
  void clearHistory() {
    state = state.copyWith(history: []);
  }

  /// 从历史记录重新搜索
  Future<void> searchFromHistory(SearchHistory historyItem) async {
    final query = VectorSearchQuery(query: historyItem.query);
    await search(query);
  }

  /// 加载向量数据库指标
  Future<void> _loadMetrics() async {
    try {
      final metrics = await _dataService.getVectorMetrics();
      state = state.copyWith(metrics: metrics);
    } catch (e) {
      AppLogger.error('加载向量指标失败: $e', module: 'VectorSearchProvider');
      // 指标加载失败不影响主要功能
    }
  }

  /// 刷新指标
  Future<void> refreshMetrics() async {
    await _loadMetrics();
  }

  /// 清除搜索历史
  void clearSearchHistory() {
    clearHistory();
  }

  /// 快速搜索（使用预设查询）
  Future<void> quickSearch(String query) async {
    final searchQuery = VectorSearchQuery(query: query);
    await search(searchQuery);
  }

  void dispose() {
    _suggestionDebounceTimer?.cancel();
  }
}

/// 相似性分析状态
class SimilarityState {
  final List<SimilarityResult> similarities;
  final List<SimilarityResult> results; // 添加results属性以兼容现有代码
  final bool isLoading;
  final String? error;
  final String? currentEntityId;

  const SimilarityState({
    this.similarities = const [],
    this.isLoading = false,
    this.error,
    this.currentEntityId,
  }) : results = similarities; // results指向similarities

  SimilarityState copyWith({
    List<SimilarityResult>? similarities,
    bool? isLoading,
    String? error,
    String? currentEntityId,
  }) {
    return SimilarityState(
      similarities: similarities ?? this.similarities,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      currentEntityId: currentEntityId ?? this.currentEntityId,
    );
  }
}

/// 相似性分析Provider
@riverpod
class SimilarityAnalysis extends _$SimilarityAnalysis {
  late final DataInsightsService _dataService;

  @override
  SimilarityState build() {
    _dataService = ref.read(dataInsightsServiceProvider);
    return const SimilarityState();
  }

  /// 计算实体相似性
  Future<void> calculateSimilarity(String entityId, {int limit = 10}) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      AppLogger.info('计算实体相似性: $entityId', module: 'SimilarityProvider');

      final similarities =
          await _dataService.calculateSimilarity(entityId, limit: limit);

      state = state.copyWith(
        similarities: similarities,
        currentEntityId: entityId,
        isLoading: false,
      );

      AppLogger.info('相似性计算完成，找到 ${similarities.length} 个相似实体',
          module: 'SimilarityProvider');
    } catch (e) {
      AppLogger.error('相似性计算失败: $e', module: 'SimilarityProvider');
      state = state.copyWith(
        isLoading: false,
        error: '相似性计算失败: ${e.toString()}',
      );
    }
  }

  /// 清除结果
  void clearSimilarities() {
    state = state.copyWith(
      similarities: [],
      currentEntityId: null,
      error: null,
    );
  }
}

/// 聚类分析状态
class ClusteringState {
  final List<ClusterResult> clusters;
  final bool isLoading;
  final String? error;
  final int numClusters;

  const ClusteringState({
    this.clusters = const [],
    this.isLoading = false,
    this.error,
    this.numClusters = 10,
  });

  ClusteringState copyWith({
    List<ClusterResult>? clusters,
    bool? isLoading,
    String? error,
    int? numClusters,
  }) {
    return ClusteringState(
      clusters: clusters ?? this.clusters,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      numClusters: numClusters ?? this.numClusters,
    );
  }
}

/// 聚类分析Provider
@riverpod
class ClusteringAnalysis extends _$ClusteringAnalysis {
  late final DataInsightsService _dataService;

  @override
  ClusteringState build() {
    _dataService = ref.read(dataInsightsServiceProvider);
    return const ClusteringState();
  }

  /// 执行聚类分析
  Future<void> analyzeClusters({int? numClusters}) async {
    final clusters = numClusters ?? state.numClusters;
    state = state.copyWith(isLoading: true, error: null, numClusters: clusters);

    try {
      AppLogger.info('执行聚类分析，聚类数: $clusters', module: 'ClusteringProvider');

      final results =
          await _dataService.getContentClusters(numClusters: clusters);

      state = state.copyWith(
        clusters: results,
        isLoading: false,
      );

      AppLogger.info('聚类分析完成，生成 ${results.length} 个聚类',
          module: 'ClusteringProvider');
    } catch (e) {
      AppLogger.error('聚类分析失败: $e', module: 'ClusteringProvider');
      state = state.copyWith(
        isLoading: false,
        error: '聚类分析失败: ${e.toString()}',
      );
    }
  }

  /// 设置聚类数量
  void setNumClusters(int numClusters) {
    state = state.copyWith(numClusters: numClusters);
  }

  /// 清除聚类结果
  void clearClusters() {
    state = state.copyWith(
      clusters: [],
      error: null,
    );
  }
}

/// 高级搜索参数状态
class AdvancedSearchParams {
  final double similarityThreshold;
  final int maxResults;
  final List<String> searchTypes;
  final List<String> connectorFilters;
  final DateTimeRange? dateRange;
  final bool useSemanticSearch;

  const AdvancedSearchParams({
    this.similarityThreshold = 0.7,
    this.maxResults = 20,
    this.searchTypes = const [],
    this.connectorFilters = const [],
    this.dateRange,
    this.useSemanticSearch = true,
  });

  AdvancedSearchParams copyWith({
    double? similarityThreshold,
    int? maxResults,
    List<String>? searchTypes,
    List<String>? connectorFilters,
    DateTimeRange? dateRange,
    bool? useSemanticSearch,
  }) {
    return AdvancedSearchParams(
      similarityThreshold: similarityThreshold ?? this.similarityThreshold,
      maxResults: maxResults ?? this.maxResults,
      searchTypes: searchTypes ?? this.searchTypes,
      connectorFilters: connectorFilters ?? this.connectorFilters,
      dateRange: dateRange ?? this.dateRange,
      useSemanticSearch: useSemanticSearch ?? this.useSemanticSearch,
    );
  }
}

/// 高级搜索参数Provider
class AdvancedSearchParamsNotifier extends StateNotifier<AdvancedSearchParams> {
  AdvancedSearchParamsNotifier() : super(const AdvancedSearchParams());

  void updateSimilarityThreshold(double threshold) {
    state = state.copyWith(similarityThreshold: threshold);
  }

  void updateMaxResults(int maxResults) {
    state = state.copyWith(maxResults: maxResults);
  }

  void updateSearchTypes(List<String> types) {
    state = state.copyWith(searchTypes: types);
  }

  void updateConnectorFilters(List<String> filters) {
    state = state.copyWith(connectorFilters: filters);
  }

  void updateDateRange(DateTimeRange? dateRange) {
    state = state.copyWith(dateRange: dateRange);
  }

  void updateSemanticSearch(bool useSemanticSearch) {
    state = state.copyWith(useSemanticSearch: useSemanticSearch);
  }

  void updateParams(AdvancedSearchParams params) {
    state = params;
  }

  void reset() {
    state = const AdvancedSearchParams();
  }
}

/// 高级搜索参数Provider实例
final advancedSearchParamsNotifierProvider =
    StateNotifierProvider<AdvancedSearchParamsNotifier, AdvancedSearchParams>(
  (ref) => AdvancedSearchParamsNotifier(),
);

// 使用现有的数据洞察服务提供者（在data_insights_provider.dart中定义）
