// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'vector_search_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$vectorSearchHash() => r'9b491318312c3bbf6a12e452f3bd57e46291eded';

/// 主向量搜索Provider
///
/// Copied from [VectorSearch].
@ProviderFor(VectorSearch)
final vectorSearchProvider =
    AutoDisposeNotifierProvider<VectorSearch, VectorSearchState>.internal(
  VectorSearch.new,
  name: r'vectorSearchProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$vectorSearchHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$VectorSearch = AutoDisposeNotifier<VectorSearchState>;
String _$similarityAnalysisHash() =>
    r'8f8ee5cca3afcc4cc009369ff91cca50dd4bcc06';

/// 相似性分析Provider
///
/// Copied from [SimilarityAnalysis].
@ProviderFor(SimilarityAnalysis)
final similarityAnalysisProvider =
    AutoDisposeNotifierProvider<SimilarityAnalysis, SimilarityState>.internal(
  SimilarityAnalysis.new,
  name: r'similarityAnalysisProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$similarityAnalysisHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$SimilarityAnalysis = AutoDisposeNotifier<SimilarityState>;
String _$clusteringAnalysisHash() =>
    r'8577ffff3d772b4b65fd1157003d44cb91f0a50d';

/// 聚类分析Provider
///
/// Copied from [ClusteringAnalysis].
@ProviderFor(ClusteringAnalysis)
final clusteringAnalysisProvider =
    AutoDisposeNotifierProvider<ClusteringAnalysis, ClusteringState>.internal(
  ClusteringAnalysis.new,
  name: r'clusteringAnalysisProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$clusteringAnalysisHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$ClusteringAnalysis = AutoDisposeNotifier<ClusteringState>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package
