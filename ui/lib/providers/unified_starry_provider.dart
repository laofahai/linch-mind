/// 统一星空宇宙提供者 - 合并UniverseProvider和StarryUniverseProvider
///
/// 基于真实IPC数据源，提供4种星空可视化模式的统一状态管理
/// 替代原有的双重架构，实现真实数据驱动的星空体验
///
/// 作者: Linch Mind 开发团队
/// 创建: 2025-08-20
/// 版本: v1.0 (架构统一版)

import 'dart:async';
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
// import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:vector_math/vector_math.dart' as vm;
import '../models/unified_data_models.dart';
import '../models/connector_lifecycle_models.dart';
import '../widgets/starry_universe/core/starry_canvas.dart';
import '../widgets/starry_universe/core/data_mappers.dart' as data_mappers;
import '../services/universe_data_adapter.dart';
import '../services/connector_lifecycle_api_client.dart';
import '../services/ipc_client.dart';
import '../utils/app_logger.dart';

// part 'unified_starry_provider.freezed.dart';

/// 宇宙数据层级显示模式
enum UniverseViewMode {
  all('all', '完整宇宙'),
  search('search', '搜索焦点'),
  entities('entities', '实体关系'),
  graph('graph', '知识图谱'),
  vectors('vectors', '语义聚类');

  const UniverseViewMode(this.key, this.displayName);
  final String key;
  final String displayName;
}

/// 统一星空状态
class UnifiedStarryState {
  // 当前视图模式
  final UniverseViewMode currentViewMode;

  // 数据加载状态
  final bool isLoading;
  final String? error;
  final DateTime? lastUpdated;

  // 球形宇宙数据（所有数据在同一个3D球面空间）
  final List<CelestialObject> celestialObjects; // 所有天体对象
  final List<StarConnection> connections; // 所有连接关系
  final List<data_mappers.NebulaCluster> nebulaClusters; // 星云区域
  final List<data_mappers.Galaxy> galaxies; // 星系聚类

  // 数据分层标识（用于过滤和高亮）
  final Set<String> searchResultIds; // 搜索结果的对象ID
  final Set<String> entityIds; // 实体对象的ID
  final Set<String> graphNodeIds; // 图节点对象的ID
  final Set<String> vectorDocIds; // 向量文档对象的ID

  // 连接器数据（兼容性）
  final List<ConnectorInfo> connectors;
  final String? selectedConnectorId;
  final Map<String, dynamic>? selectedConnectorInfo;

  // 统计信息
  final int totalConnectors;
  final int runningConnectors;
  final int errorConnectors;
  final int totalConnections;

  // 搜索相关
  final String? currentQuery;
  final List<UniversalIndexEntry> searchResults;

  // 实体相关
  final List<UnifiedEntityMetadata> entities;
  final List<UnifiedEntityRelationship> relationships;

  // 图谱相关
  final List<GraphNode> graphNodes;
  final List<GraphEdge> graphEdges;
  final Map<String, List<String>> graphClusters;

  // 向量相关
  final List<UnifiedVectorDocument> vectorDocuments;
  final List<VectorCluster> vectorClusters;

  // 交互状态
  final String? selectedObjectId;
  final Map<String, dynamic>? selectedObjectInfo;
  final double zoomLevel;
  final Map<String, dynamic> viewportInfo;

  const UnifiedStarryState({
    this.currentViewMode = UniverseViewMode.all,
    this.isLoading = false,
    this.error,
    this.lastUpdated,
    this.celestialObjects = const [],
    this.connections = const [],
    this.nebulaClusters = const [],
    this.galaxies = const [],
    this.searchResultIds = const {},
    this.entityIds = const {},
    this.graphNodeIds = const {},
    this.vectorDocIds = const {},
    this.connectors = const [],
    this.selectedConnectorId,
    this.selectedConnectorInfo,
    this.totalConnectors = 0,
    this.runningConnectors = 0,
    this.errorConnectors = 0,
    this.totalConnections = 0,
    this.currentQuery,
    this.searchResults = const [],
    this.entities = const [],
    this.relationships = const [],
    this.graphNodes = const [],
    this.graphEdges = const [],
    this.graphClusters = const {},
    this.vectorDocuments = const [],
    this.vectorClusters = const [],
    this.selectedObjectId,
    this.selectedObjectInfo,
    this.zoomLevel = 1.0,
    this.viewportInfo = const {},
  });

  UnifiedStarryState copyWith({
    UniverseViewMode? currentViewMode,
    bool? isLoading,
    String? error,
    DateTime? lastUpdated,
    List<CelestialObject>? celestialObjects,
    List<StarConnection>? connections,
    List<data_mappers.NebulaCluster>? nebulaClusters,
    List<data_mappers.Galaxy>? galaxies,
    Set<String>? searchResultIds,
    Set<String>? entityIds,
    Set<String>? graphNodeIds,
    Set<String>? vectorDocIds,
    List<ConnectorInfo>? connectors,
    String? selectedConnectorId,
    Map<String, dynamic>? selectedConnectorInfo,
    int? totalConnectors,
    int? runningConnectors,
    int? errorConnectors,
    int? totalConnections,
    String? currentQuery,
    List<UniversalIndexEntry>? searchResults,
    List<UnifiedEntityMetadata>? entities,
    List<UnifiedEntityRelationship>? relationships,
    List<GraphNode>? graphNodes,
    List<GraphEdge>? graphEdges,
    Map<String, List<String>>? graphClusters,
    List<UnifiedVectorDocument>? vectorDocuments,
    List<VectorCluster>? vectorClusters,
    String? selectedObjectId,
    Map<String, dynamic>? selectedObjectInfo,
    double? zoomLevel,
    Map<String, dynamic>? viewportInfo,
  }) {
    return UnifiedStarryState(
      currentViewMode: currentViewMode ?? this.currentViewMode,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
      lastUpdated: lastUpdated ?? this.lastUpdated,
      celestialObjects: celestialObjects ?? this.celestialObjects,
      connections: connections ?? this.connections,
      nebulaClusters: nebulaClusters ?? this.nebulaClusters,
      galaxies: galaxies ?? this.galaxies,
      searchResultIds: searchResultIds ?? this.searchResultIds,
      entityIds: entityIds ?? this.entityIds,
      graphNodeIds: graphNodeIds ?? this.graphNodeIds,
      vectorDocIds: vectorDocIds ?? this.vectorDocIds,
      connectors: connectors ?? this.connectors,
      selectedConnectorId: selectedConnectorId ?? this.selectedConnectorId,
      selectedConnectorInfo:
          selectedConnectorInfo ?? this.selectedConnectorInfo,
      totalConnectors: totalConnectors ?? this.totalConnectors,
      runningConnectors: runningConnectors ?? this.runningConnectors,
      errorConnectors: errorConnectors ?? this.errorConnectors,
      totalConnections: totalConnections ?? this.totalConnections,
      currentQuery: currentQuery ?? this.currentQuery,
      searchResults: searchResults ?? this.searchResults,
      entities: entities ?? this.entities,
      relationships: relationships ?? this.relationships,
      graphNodes: graphNodes ?? this.graphNodes,
      graphEdges: graphEdges ?? this.graphEdges,
      graphClusters: graphClusters ?? this.graphClusters,
      vectorDocuments: vectorDocuments ?? this.vectorDocuments,
      vectorClusters: vectorClusters ?? this.vectorClusters,
      selectedObjectId: selectedObjectId ?? this.selectedObjectId,
      selectedObjectInfo: selectedObjectInfo ?? this.selectedObjectInfo,
      zoomLevel: zoomLevel ?? this.zoomLevel,
      viewportInfo: viewportInfo ?? this.viewportInfo,
    );
  }
}

/// 统一星空数据提供者
class UnifiedStarryNotifier extends StateNotifier<UnifiedStarryState> {
  UnifiedStarryNotifier() : super(const UnifiedStarryState()) {
    _initialize();
  }

  final ConnectorLifecycleApiClient _connectorApi =
      ConnectorLifecycleApiService.instance;
  Timer? _refreshTimer;

  /// 初始化
  Future<void> _initialize() async {
    AppLogger.info('初始化统一球形宇宙提供者', module: 'UnifiedStarryProvider');

    // 等待IPC连接建立
    await _ensureIPCConnection();

    // 加载完整的球形宇宙数据
    await loadCompleteUniverse();
    _startPeriodicRefresh();
  }

  /// 确保IPC连接已建立
  Future<void> _ensureIPCConnection() async {
    final ipcClient = IPCService.instance;

    // 检查连接状态
    if (ipcClient.currentStatus == ConnectionStatus.authenticated) {
      AppLogger.info('IPC连接已建立', module: 'UnifiedStarryProvider');
      return;
    }

    AppLogger.info('等待IPC连接建立...', module: 'UnifiedStarryProvider');

    // 如果未连接，尝试连接
    if (ipcClient.currentStatus == ConnectionStatus.disconnected) {
      await ipcClient.connect(maxRetries: 3);
    }

    // 等待连接完成（最长等待10秒）
    await ipcClient.connectionStream
        .where((status) =>
            status == ConnectionStatus.authenticated ||
            status == ConnectionStatus.failed)
        .timeout(const Duration(seconds: 10))
        .first;

    if (ipcClient.currentStatus != ConnectionStatus.authenticated) {
      throw Exception('IPC连接失败，无法加载宇宙数据');
    }

    AppLogger.info('IPC连接已建立，可以开始加载数据', module: 'UnifiedStarryProvider');
  }

  /// 开始定期刷新
  void _startPeriodicRefresh() {
    _refreshTimer?.cancel();
    _refreshTimer = Timer.periodic(const Duration(seconds: 60), (_) {
      refreshCurrentMode();
    });
    AppLogger.debug('启动定期数据刷新 (60秒)', module: 'UnifiedStarryProvider');
  }

  // ================================
  // 球形宇宙数据加载核心方法
  // ================================

  /// 加载完整的球形宇宙数据
  Future<void> loadCompleteUniverse() async {
    AppLogger.info('加载完整球形宇宙数据', module: 'UnifiedStarryProvider');

    state = state.copyWith(
      isLoading: true,
      error: null,
    );

    try {
      final canvasSize = Size(1000, 1000); // 球面映射尺寸

      // 并行加载所有数据类型
      final futures = await Future.wait([
        _loadAllSearchData(canvasSize),
        _loadAllEntityData(canvasSize),
        _loadAllGraphData(canvasSize),
        _loadAllVectorData(canvasSize),
      ]);

      // 合并所有天体对象到同一个球面空间
      final allObjects = <CelestialObject>[];
      final allConnections = <StarConnection>[];
      final searchIds = <String>{};
      final entityIds = <String>{};
      final graphIds = <String>{};
      final vectorIds = <String>{};

      // 添加搜索数据（在球面上层）
      final searchData = futures[0] as List<CelestialObject>;
      allObjects.addAll(searchData);
      searchIds.addAll(searchData.map((obj) => obj.id));

      // 添加实体数据（在球面中层）
      final entityData = futures[1] as StarConstellationData;
      allObjects.addAll(entityData.stars);
      allConnections.addAll(entityData.connections);
      entityIds.addAll(entityData.stars.map((obj) => obj.id));

      // 添加图数据（在球面深层）
      final graphData = futures[2] as UniverseGalaxyData;
      for (final galaxy in graphData.galaxies) {
        allObjects.addAll(galaxy.stars);
        graphIds.addAll(galaxy.stars.map((obj) => obj.id));
      }

      // 添加向量数据（作为星云区域）
      final vectorData = futures[3] as NebulaClusterData;
      for (final cluster in vectorData.clusters) {
        // 为每个文档在星云内创建小星体（使用球面内层坐标）
        for (int i = 0; i < cluster.documents.length; i++) {
          final doc = cluster.documents[i];

          // 使用黄金角度在星云内分布
          final phi = (math.pi * (3.0 - math.sqrt(5.0))) * i;
          final localRadius =
              cluster.radius * math.sqrt(i / cluster.documents.length) * 0.8;
          final position = cluster.center +
              vm.Vector2(
                localRadius * math.cos(phi),
                localRadius * math.sin(phi),
              );

          final vectorStar = Star(
            position: position,
            size: 1.5,
            color: cluster.color.withValues(alpha: 0.7),
            id: 'vector_${cluster.id}_${doc['documentId'] ?? doc['id']}',
            metadata: {
              'document': doc,
              'cluster': cluster.id,
              'type': 'vector',
              'layer': 'vector_inner'
            },
          );

          allObjects.add(vectorStar);
          vectorIds.add(vectorStar.id);
        }
      }

      state = state.copyWith(
        isLoading: false,
        lastUpdated: DateTime.now(),
        celestialObjects: allObjects,
        connections: allConnections,
        nebulaClusters: vectorData.clusters,
        galaxies: graphData.galaxies.cast<data_mappers.Galaxy>(),
        searchResultIds: searchIds,
        entityIds: entityIds,
        graphNodeIds: graphIds,
        vectorDocIds: vectorIds,
      );

      AppLogger.info('球形宇宙数据加载完成', module: 'UnifiedStarryProvider', data: {
        'total_objects': allObjects.length,
        'total_connections': allConnections.length,
        'search_objects': searchIds.length,
        'entity_objects': entityIds.length,
        'graph_objects': graphIds.length,
        'vector_objects': vectorIds.length,
      });
    } catch (e, stackTrace) {
      AppLogger.error('加载球形宇宙数据失败',
          module: 'UnifiedStarryProvider',
          exception: e,
          stackTrace: stackTrace);

      state = state.copyWith(
        isLoading: false,
        error: '加载宇宙数据失败: $e',
      );
    }
  }

  /// 切换视图模式（不重新加载数据，只改变显示层级）
  void switchViewMode(UniverseViewMode mode) {
    AppLogger.info('切换宇宙视图模式', module: 'UnifiedStarryProvider', data: {
      'from': state.currentViewMode.key,
      'to': mode.key,
    });

    state = state.copyWith(currentViewMode: mode);
  }

  /// 刷新当前模式
  Future<void> refreshCurrentMode() async {
    if (state.isLoading) return;
    await loadCompleteUniverse();
  }

  /// 刷新宇宙数据
  Future<void> refreshUniverse() async {
    if (state.isLoading) return;
    await loadCompleteUniverse();
  }

  // ================================
  // 具体数据加载方法
  // ================================

  /// 加载所有搜索数据（球面上层）
  Future<List<CelestialObject>> _loadAllSearchData(Size canvasSize) async {
    try {
      return await UnifiedStarryDataAdapter.getSearchStarRiver('*', canvasSize);
    } catch (e) {
      AppLogger.error('加载搜索数据失败',
          module: 'UnifiedStarryProvider', exception: e);
      return [];
    }
  }

  /// 加载所有实体数据（球面中层）
  Future<StarConstellationData> _loadAllEntityData(Size canvasSize) async {
    try {
      return await UnifiedStarryDataAdapter.getWisdomConstellation(canvasSize);
    } catch (e) {
      AppLogger.error('加载实体数据失败',
          module: 'UnifiedStarryProvider', exception: e);
      return StarConstellationData(stars: [], connections: [], metadata: {});
    }
  }

  /// 加载所有图数据（球面深层）
  Future<UniverseGalaxyData> _loadAllGraphData(Size canvasSize) async {
    try {
      return await UnifiedStarryDataAdapter.getKnowledgeUniverse(canvasSize);
    } catch (e) {
      AppLogger.error('加载图数据失败', module: 'UnifiedStarryProvider', exception: e);
      return UniverseGalaxyData(galaxies: [], metrics: {});
    }
  }

  /// 加载所有向量数据（星云区域）
  Future<NebulaClusterData> _loadAllVectorData(Size canvasSize) async {
    try {
      return await UnifiedStarryDataAdapter.getSimilarityNebula(canvasSize);
    } catch (e) {
      AppLogger.error('加载向量数据失败',
          module: 'UnifiedStarryProvider', exception: e);
      return NebulaClusterData(clusters: [], documents: []);
    }
  }

  // ================================
  // 具体模式加载方法
  // ================================

  /// 加载知识宇宙
  Future<void> _loadKnowledgeUniverse() async {
    final canvasSize = Size(800, 600);
    final universeData =
        await UnifiedStarryDataAdapter.getKnowledgeUniverse(canvasSize);

    // 将星系中的所有星体合并到celestialObjects
    final allStars = <CelestialObject>[];
    final galaxyConnections = <StarConnection>[];

    for (final galaxy in universeData.galaxies) {
      allStars.addAll(galaxy.stars);

      // 为星系内的星体生成连接
      for (int i = 0; i < galaxy.stars.length; i++) {
        for (int j = i + 1; j < galaxy.stars.length; j++) {
          final star1 = galaxy.stars[i];
          final star2 = galaxy.stars[j];
          final distance = (star1.position - star2.position).length;

          if (distance < 100) {
            galaxyConnections.add(StarConnection(
              fromStarId: star1.id,
              toStarId: star2.id,
              strength: (100 - distance) / 100,
              color: Colors.white.withValues(alpha: 0.3),
            ));
          }
        }
      }
    }

    state = state.copyWith(
      celestialObjects: allStars,
      connections: galaxyConnections,
      nebulaClusters: [],
      galaxies: universeData.galaxies.cast<data_mappers.Galaxy>(),
      graphNodes: [],
      graphEdges: [],
    );
  }

  /// 加载相似星云
  Future<void> _loadSimilarityNebula() async {
    final canvasSize = Size(800, 600);
    final nebulaData =
        await UnifiedStarryDataAdapter.getSimilarityNebula(canvasSize);

    // 从星云聚类生成粒子效果的星体
    final nebulaStars = <CelestialObject>[];
    for (final cluster in nebulaData.clusters) {
      for (int i = 0; i < cluster.documents.length; i++) {
        final doc = cluster.documents[i];
        final angle = (i / cluster.documents.length) * 2 * 3.14159;
        final radius = cluster.radius * 0.8;
        final position = cluster.center +
            vm.Vector2(
              radius *
                  0.5 *
                  (1 + 0.5 * (i / cluster.documents.length)) *
                  vm.Vector2(1, 0).dot(vm.Vector2(angle, 0)),
              radius *
                  0.5 *
                  (1 + 0.5 * (i / cluster.documents.length)) *
                  vm.Vector2(0, 1).dot(vm.Vector2(0, angle)),
            );

        nebulaStars.add(Star(
          position: position,
          size: 2.0,
          color: cluster.color.withValues(alpha: 0.8),
          id: 'nebula_${cluster.id}_doc_$i',
          metadata: {'document': doc},
        ));
      }
    }

    state = state.copyWith(
      celestialObjects: nebulaStars,
      connections: [], // 星云模式主要显示粒子效果
      nebulaClusters: nebulaData.clusters,
      galaxies: [],
      vectorDocuments: nebulaData.documents,
      vectorClusters: [], // TODO: 从adapter获取原始聚类数据
    );
  }

  /// 加载连接器星球（兼容性保留）
  Future<void> _loadConnectorSphere() async {
    try {
      final response = await _connectorApi.getConnectors();

      if (!response.success) {
        throw Exception('获取连接器数据失败: ${response.connectors}');
      }

      final connectors = response.connectors;
      final celestialObjects =
          UnifiedStarryDataAdapter.convertConnectorsToStars(connectors);
      final connections =
          UnifiedStarryDataAdapter.convertRelationshipsToConnections(
              connectors, {});

      // 计算统计信息
      final stats = _calculateConnectorStatistics(connectors, connections);

      state = state.copyWith(
        celestialObjects: celestialObjects,
        connections: connections,
        nebulaClusters: [],
        galaxies: [],
        connectors: connectors,
        totalConnectors: stats['totalConnectors'] ?? 0,
        runningConnectors: stats['runningConnectors'] ?? 0,
        errorConnectors: stats['errorConnectors'] ?? 0,
        totalConnections: stats['totalConnections'] ?? 0,
      );
    } catch (e) {
      AppLogger.error('加载连接器数据失败',
          module: 'UnifiedStarryProvider', exception: e);
      rethrow;
    }
  }

  // ================================
  // 搜索和交互方法
  // ================================

  /// 执行搜索
  Future<void> searchData(String query) async {
    if (query.isEmpty) return;

    AppLogger.info('执行星空搜索',
        module: 'UnifiedStarryProvider', data: {'query': query});

    state = state.copyWith(
      currentQuery: query,
      isLoading: true,
      error: null,
    );

    // 切换到搜索视图模式
    switchViewMode(UniverseViewMode.search);
    await refreshUniverse();
  }

  /// 选择天体对象
  void selectObject(String? objectId) {
    AppLogger.debug('选择天体对象',
        module: 'UnifiedStarryProvider', data: {'id': objectId});

    Map<String, dynamic>? objectInfo;
    if (objectId != null) {
      final object = state.celestialObjects.firstWhere(
        (obj) => obj.id == objectId,
        orElse: () => throw StateError('天体对象不存在: $objectId'),
      );
      objectInfo = _getObjectDisplayInfo(object);
    }

    state = state.copyWith(
      selectedObjectId: objectId,
      selectedObjectInfo: objectInfo,
    );
  }

  /// 选择连接器（兼容性保留）
  void selectConnector(String? connectorId) {
    AppLogger.debug('选择连接器',
        module: 'UnifiedStarryProvider', data: {'id': connectorId});

    Map<String, dynamic>? connectorInfo;
    if (connectorId != null) {
      final connector = state.connectors.firstWhere(
        (c) => c.connectorId == connectorId,
        orElse: () => throw StateError('连接器不存在: $connectorId'),
      );
      connectorInfo =
          UnifiedStarryDataAdapter.getConnectorDisplayInfo(connector);
    }

    state = state.copyWith(
      selectedConnectorId: connectorId,
      selectedConnectorInfo: connectorInfo,
    );
  }

  /// 更新视图状态
  void updateViewport({
    double? zoomLevel,
    Map<String, dynamic>? viewportInfo,
  }) {
    state = state.copyWith(
      zoomLevel: zoomLevel ?? state.zoomLevel,
      viewportInfo: viewportInfo ?? state.viewportInfo,
    );
  }

  // ================================
  // 连接器操作方法（兼容性保留）
  // ================================

  /// 启动连接器
  Future<void> startConnector(String connectorId) async {
    try {
      final response = await _connectorApi.startConnector(connectorId);
      if (response.success) {
        await refreshCurrentMode();
      } else {
        throw Exception(response.message);
      }
    } catch (e) {
      AppLogger.error('启动连接器失败',
          module: 'UnifiedStarryProvider',
          exception: e,
          data: {'id': connectorId});
      rethrow;
    }
  }

  /// 停止连接器
  Future<void> stopConnector(String connectorId) async {
    try {
      final response = await _connectorApi.stopConnector(connectorId);
      if (response.success) {
        await refreshCurrentMode();
      } else {
        throw Exception(response.message);
      }
    } catch (e) {
      AppLogger.error('停止连接器失败',
          module: 'UnifiedStarryProvider',
          exception: e,
          data: {'id': connectorId});
      rethrow;
    }
  }

  /// 重启连接器
  Future<void> restartConnector(String connectorId) async {
    try {
      final response = await _connectorApi.restartConnector(connectorId);
      if (response.success) {
        await refreshCurrentMode();
      } else {
        throw Exception(response.message);
      }
    } catch (e) {
      AppLogger.error('重启连接器失败',
          module: 'UnifiedStarryProvider',
          exception: e,
          data: {'id': connectorId});
      rethrow;
    }
  }

  /// 删除连接器
  Future<void> deleteConnector(String connectorId) async {
    try {
      final response = await _connectorApi.deleteConnector(connectorId);
      if (response.success) {
        await refreshCurrentMode();
      } else {
        throw Exception(response.message);
      }
    } catch (e) {
      AppLogger.error('删除连接器失败',
          module: 'UnifiedStarryProvider',
          exception: e,
          data: {'id': connectorId});
      rethrow;
    }
  }

  // ================================
  // 私有辅助方法
  // ================================

  /// 计算连接器统计信息
  Map<String, int> _calculateConnectorStatistics(
    List<ConnectorInfo> connectors,
    List<StarConnection> connections,
  ) {
    int runningCount = 0;
    int errorCount = 0;

    for (final connector in connectors) {
      switch (connector.state) {
        case ConnectorState.running:
          runningCount++;
          break;
        case ConnectorState.error:
          errorCount++;
          break;
        default:
          break;
      }
    }

    return {
      'totalConnectors': connectors.length,
      'runningConnectors': runningCount,
      'errorConnectors': errorCount,
      'totalConnections': connections.length,
    };
  }

  /// 获取天体对象显示信息
  Map<String, dynamic> _getObjectDisplayInfo(CelestialObject object) {
    return {
      'id': object.id,
      'position':
          '(${object.position.x.toStringAsFixed(1)}, ${object.position.y.toStringAsFixed(1)})',
      'size': object.size,
      'color': object.color.toString(),
      'metadata': object.metadata,
      'type': object.runtimeType.toString(),
    };
  }

  /// 清除错误状态
  void clearError() {
    state = state.copyWith(error: null);
  }

  /// 强制刷新
  Future<void> forceRefresh() async {
    AppLogger.info('强制刷新星空数据', module: 'UnifiedStarryProvider');
    await refreshCurrentMode();
  }

  /// 切换自动刷新
  void toggleAutoRefresh(bool enabled) {
    if (enabled) {
      _startPeriodicRefresh();
      AppLogger.info('启用自动刷新', module: 'UnifiedStarryProvider');
    } else {
      _refreshTimer?.cancel();
      _refreshTimer = null;
      AppLogger.info('禁用自动刷新', module: 'UnifiedStarryProvider');
    }
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }
}

// ================================
// Provider实例和便捷访问器
// ================================

/// 统一星空状态提供者
final unifiedStarryProvider =
    StateNotifierProvider<UnifiedStarryNotifier, UnifiedStarryState>(
  (ref) => UnifiedStarryNotifier(),
);

/// 当前视图模式提供者
final currentUniverseViewModeProvider = Provider<UniverseViewMode>((ref) {
  return ref
      .watch(unifiedStarryProvider.select((state) => state.currentViewMode));
});

/// 加载状态提供者
final isStarryLoadingProvider = Provider<bool>((ref) {
  return ref.watch(unifiedStarryProvider.select((state) => state.isLoading));
});

/// 错误状态提供者
final starryErrorProvider = Provider<String?>((ref) {
  return ref.watch(unifiedStarryProvider.select((state) => state.error));
});

/// 天体对象提供者
final celestialObjectsProvider = Provider<List<CelestialObject>>((ref) {
  return ref
      .watch(unifiedStarryProvider.select((state) => state.celestialObjects));
});

/// 连接线提供者
final starConnectionsProvider = Provider<List<StarConnection>>((ref) {
  return ref.watch(unifiedStarryProvider.select((state) => state.connections));
});

/// 星云聚类提供者
final nebulaClusterProvider = Provider<List<data_mappers.NebulaCluster>>((ref) {
  return ref
      .watch(unifiedStarryProvider.select((state) => state.nebulaClusters));
});

/// 选中对象提供者
final selectedObjectProvider = Provider<String?>((ref) {
  return ref
      .watch(unifiedStarryProvider.select((state) => state.selectedObjectId));
});

/// 连接器统计提供者（兼容性保留）
final connectorStatsProvider = Provider<Map<String, int>>((ref) {
  final state = ref.watch(unifiedStarryProvider);
  return {
    'total': state.totalConnectors,
    'running': state.runningConnectors,
    'error': state.errorConnectors,
    'connections': state.totalConnections,
  };
});
