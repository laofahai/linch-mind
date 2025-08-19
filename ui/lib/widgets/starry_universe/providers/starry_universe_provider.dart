/// 星空宇宙数据提供者 - 集成IPC数据源和状态管理
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:vector_math/vector_math.dart' as vm;
import '../../../core/ui_service_facade.dart';
import '../../../services/ipc_client.dart';
import '../../../models/api_response.dart';
import '../../../models/ipc_protocol.dart';
import '../core/starry_canvas.dart';
import '../core/particle_system.dart';
import '../core/data_mappers.dart';
import '../core/cosmic_animations.dart';

/// 星空数据状态
@immutable
class StarryUniverseState {
  final List<CelestialObject> celestialObjects;
  final List<StarConnection> connections;
  final List<NebulaCluster> nebulaClusters;
  final UniverseLayout? universeLayout;
  final bool isLoading;
  final String? error;
  final String currentMode;
  final DateTime lastUpdated;

  const StarryUniverseState({
    this.celestialObjects = const [],
    this.connections = const [],
    this.nebulaClusters = const [],
    this.universeLayout,
    this.isLoading = false,
    this.error,
    this.currentMode = 'search',
    required this.lastUpdated,
  });

  StarryUniverseState copyWith({
    List<CelestialObject>? celestialObjects,
    List<StarConnection>? connections,
    List<NebulaCluster>? nebulaClusters,
    UniverseLayout? universeLayout,
    bool? isLoading,
    String? error,
    String? currentMode,
    DateTime? lastUpdated,
  }) {
    return StarryUniverseState(
      celestialObjects: celestialObjects ?? this.celestialObjects,
      connections: connections ?? this.connections,
      nebulaClusters: nebulaClusters ?? this.nebulaClusters,
      universeLayout: universeLayout ?? this.universeLayout,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
      currentMode: currentMode ?? this.currentMode,
      lastUpdated: lastUpdated ?? this.lastUpdated,
    );
  }
}

/// 星空宇宙数据提供者
class StarryUniverseNotifier extends StateNotifier<StarryUniverseState> {
  late final IPCClient _ipcClient;
  
  StarryUniverseNotifier() : super(StarryUniverseState(
    lastUpdated: DateTime.now(),
  )) {
    _initializeServices();
  }

  /// 初始化服务
  void _initializeServices() {
    try {
      _ipcClient = getService<IPCClient>();
    } catch (e) {
      debugPrint('Failed to initialize StarryUniverseNotifier services: $e');
    }
  }

  /// 切换显示模式
  Future<void> switchMode(String mode) async {
    state = state.copyWith(
      currentMode: mode,
      isLoading: true,
      error: null,
    );

    try {
      switch (mode) {
        case 'search':
          await _loadSearchData();
          break;
        case 'constellation':
          await _loadEntityData();
          break;
        case 'universe':
          await _loadGraphData();
          break;
        case 'nebula':
          await _loadVectorData();
          break;
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: '加载数据失败: $e',
      );
    }
  }

  /// 加载搜索数据 - 搜索星河
  Future<void> _loadSearchData() async {
    try {
      // 获取最近的搜索历史或默认搜索
      final request = IPCRequest(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        route: '/api/search/recent',
        method: 'GET',
        payload: {},
      );
      final response = await _ipcClient.sendRequest(request);

      if (response.isSuccess && response.data != null) {
        final searchResults = response.data['results'] as List<dynamic>? ?? [];
        final searchData = searchResults.map((item) => item as Map<String, dynamic>).toList();
        
        final stars = SearchStarMapper.mapSearchResultsToStars(
          searchData,
          Size(800, 600),
        );

        state = state.copyWith(
          celestialObjects: stars,
          connections: [], // 搜索模式不显示连接
          isLoading: false,
          lastUpdated: DateTime.now(),
        );
      } else {
        // 使用模拟数据
        await _loadDemoSearchData();
      }
    } catch (e) {
      debugPrint('Failed to load search data: $e');
      await _loadDemoSearchData();
    }
  }

  /// 加载实体数据 - 智慧星座
  Future<void> _loadEntityData() async {
    try {
      // 获取实体元数据
      final entitiesRequest = IPCRequest(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        route: '/api/entities',
        method: 'GET',
        payload: {'limit': 50, 'include_relationships': true},
      );
      final entitiesResponse = await _ipcClient.sendRequest(entitiesRequest);

      // 获取实体关系
      final relationshipsRequest = IPCRequest(
        id: (DateTime.now().millisecondsSinceEpoch + 1).toString(),
        route: '/api/relationships',
        method: 'GET',
        payload: {'limit': 100},
      );
      final relationshipsResponse = await _ipcClient.sendRequest(relationshipsRequest);

      if (entitiesResponse.isSuccess && relationshipsResponse.isSuccess) {
        final entities = (entitiesResponse.data['entities'] as List<dynamic>?)
            ?.map((item) => item as Map<String, dynamic>)
            .toList() ?? [];
        
        final relationships = (relationshipsResponse.data['relationships'] as List<dynamic>?)
            ?.map((item) => item as Map<String, dynamic>)
            .toList() ?? [];

        final stars = ConstellationMapper.mapEntitiesToStars(
          entities,
          Size(800, 600),
        );

        final connections = ConstellationMapper.generateEntityConnections(
          relationships,
          stars,
        );

        state = state.copyWith(
          celestialObjects: stars,
          connections: connections,
          isLoading: false,
          lastUpdated: DateTime.now(),
        );
      } else {
        await _loadDemoEntityData();
      }
    } catch (e) {
      debugPrint('Failed to load entity data: $e');
      await _loadDemoEntityData();
    }
  }

  /// 加载图数据 - 知识宇宙
  Future<void> _loadGraphData() async {
    try {
      final request = IPCRequest(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        route: '/api/graph/knowledge',
        method: 'GET',
        payload: {'format': 'networkx'},
      );
      final response = await _ipcClient.sendRequest(request);

      if (response.isSuccess && response.data != null) {
        final graphData = response.data as Map<String, dynamic>;
        
        final universeLayout = UniverseMapper.mapGraphToUniverse(
          graphData,
          Size(800, 600),
        );

        // 将星系中的所有星体合并到celestialObjects
        final allStars = <CelestialObject>[];
        final galaxyConnections = <StarConnection>[];

        for (final galaxy in universeLayout.galaxies) {
          allStars.addAll(galaxy.stars);
          
          // 为星系内的星体生成连接
          for (int i = 0; i < galaxy.stars.length; i++) {
            for (int j = i + 1; j < galaxy.stars.length; j++) {
              final star1 = galaxy.stars[i];
              final star2 = galaxy.stars[j];
              final distance = (star1.position - star2.position).length;
              
              if (distance < 100) { // 只连接近距离的星体
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
          universeLayout: universeLayout,
          isLoading: false,
          lastUpdated: DateTime.now(),
        );
      } else {
        await _loadDemoGraphData();
      }
    } catch (e) {
      debugPrint('Failed to load graph data: $e');
      await _loadDemoGraphData();
    }
  }

  /// 加载向量数据 - 相似星云
  Future<void> _loadVectorData() async {
    try {
      final request = IPCRequest(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        route: '/api/vectors/documents',
        method: 'GET',
        payload: {'limit': 100, 'include_embeddings': false},
      );
      final response = await _ipcClient.sendRequest(request);

      if (response.isSuccess && response.data != null) {
        final documents = (response.data['documents'] as List<dynamic>?)
            ?.map((item) => item as Map<String, dynamic>)
            .toList() ?? [];

        final nebulaClusters = NebulaMapper.mapVectorsToNebulae(
          documents,
          Size(800, 600),
        );

        // 从星云聚类生成粒子效果的星体
        final nebulaStars = <CelestialObject>[];
        for (final cluster in nebulaClusters) {
          // 为每个文档在聚类中心附近创建一个小星体
          for (int i = 0; i < cluster.documents.length; i++) {
            final doc = cluster.documents[i];
            final angle = (i / cluster.documents.length) * 2 * 3.14159;
            final radius = cluster.radius * 0.8;
            final position = cluster.center + vm.Vector2(
              radius * 0.5 * (1 + 0.5 * (i / cluster.documents.length)) * vm.Vector2(1, 0).dot(vm.Vector2(angle, 0)),
              radius * 0.5 * (1 + 0.5 * (i / cluster.documents.length)) * vm.Vector2(0, 1).dot(vm.Vector2(0, angle)),
            );

            nebulaStars.add(Star(
              position: position,
              size: 2.0,
              color: cluster.color.withValues(alpha: 0.8),
              id: 'nebula_${cluster.id}_doc_$i',
              metadata: doc,
            ));
          }
        }

        state = state.copyWith(
          celestialObjects: nebulaStars,
          connections: [], // 星云模式主要显示粒子效果
          nebulaClusters: nebulaClusters,
          isLoading: false,
          lastUpdated: DateTime.now(),
        );
      } else {
        await _loadDemoVectorData();
      }
    } catch (e) {
      debugPrint('Failed to load vector data: $e');
      await _loadDemoVectorData();
    }
  }

  /// 加载演示搜索数据
  Future<void> _loadDemoSearchData() async {
    final demoData = [
      {
        'id': 'demo_doc_1',
        'title': '机器学习基础',
        'type': 'document',
        'score': 0.95,
        'snippet': '介绍机器学习的基本概念和算法...',
      },
      {
        'id': 'demo_img_1',
        'title': '神经网络架构图',
        'type': 'image',
        'score': 0.88,
        'snippet': '展示不同类型的神经网络结构...',
      },
      {
        'id': 'demo_code_1',
        'title': 'PyTorch教程',
        'type': 'code',
        'score': 0.82,
        'snippet': 'PyTorch深度学习框架使用示例...',
      },
    ];

    final stars = SearchStarMapper.mapSearchResultsToStars(
      demoData,
      Size(800, 600),
    );

    state = state.copyWith(
      celestialObjects: stars,
      connections: [],
      isLoading: false,
      lastUpdated: DateTime.now(),
    );
  }

  /// 加载演示实体数据
  Future<void> _loadDemoEntityData() async {
    final demoEntities = [
      {
        'entity_id': 'demo_entity_1',
        'name': '人工智能',
        'type': 'concept',
        'access_count': 50,
        'relationship_count': 15,
      },
      {
        'entity_id': 'demo_entity_2',
        'name': '机器学习',
        'type': 'concept',
        'access_count': 35,
        'relationship_count': 12,
      },
      {
        'entity_id': 'demo_entity_3',
        'name': 'Geoffrey Hinton',
        'type': 'person',
        'access_count': 20,
        'relationship_count': 8,
      },
    ];

    final demoRelationships = [
      {
        'source_entity_id': 'demo_entity_1',
        'target_entity_id': 'demo_entity_2',
        'strength': 0.9,
      },
      {
        'source_entity_id': 'demo_entity_2',
        'target_entity_id': 'demo_entity_3',
        'strength': 0.7,
      },
    ];

    final stars = ConstellationMapper.mapEntitiesToStars(
      demoEntities,
      Size(800, 600),
    );

    final connections = ConstellationMapper.generateEntityConnections(
      demoRelationships,
      stars,
    );

    state = state.copyWith(
      celestialObjects: stars,
      connections: connections,
      isLoading: false,
      lastUpdated: DateTime.now(),
    );
  }

  /// 加载演示图数据
  Future<void> _loadDemoGraphData() async {
    // 创建演示图数据
    final demoGraphData = {
      'nodes': [
        {'id': 'node_1', 'type': 'concept', 'weight': 1.5},
        {'id': 'node_2', 'type': 'document', 'weight': 1.0},
        {'id': 'node_3', 'type': 'person', 'weight': 2.0},
        {'id': 'node_4', 'type': 'project', 'weight': 1.2},
      ],
      'edges': [
        {'source': 'node_1', 'target': 'node_2', 'weight': 0.8},
        {'source': 'node_2', 'target': 'node_3', 'weight': 0.6},
        {'source': 'node_3', 'target': 'node_4', 'weight': 0.9},
      ],
    };

    final universeLayout = UniverseMapper.mapGraphToUniverse(
      demoGraphData,
      Size(800, 600),
    );

    final allStars = <CelestialObject>[];
    for (final galaxy in universeLayout.galaxies) {
      allStars.addAll(galaxy.stars);
    }

    state = state.copyWith(
      celestialObjects: allStars,
      connections: [],
      universeLayout: universeLayout,
      isLoading: false,
      lastUpdated: DateTime.now(),
    );
  }

  /// 加载演示向量数据
  Future<void> _loadDemoVectorData() async {
    final demoDocuments = [
      {'id': 'vec_doc_1', 'type': 'document', 'title': 'AI论文1'},
      {'id': 'vec_doc_2', 'type': 'document', 'title': 'AI论文2'},
      {'id': 'vec_img_1', 'type': 'image', 'title': '图表1'},
      {'id': 'vec_img_2', 'type': 'image', 'title': '图表2'},
    ];

    final nebulaClusters = NebulaMapper.mapVectorsToNebulae(
      demoDocuments,
      Size(800, 600),
    );

    state = state.copyWith(
      celestialObjects: [],
      connections: [],
      nebulaClusters: nebulaClusters,
      isLoading: false,
      lastUpdated: DateTime.now(),
    );
  }

  /// 搜索数据
  Future<void> searchData(String query) async {
    if (query.isEmpty) return;

    state = state.copyWith(isLoading: true, error: null);

    try {
      final request = IPCRequest(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        route: '/api/search',
        method: 'POST',
        payload: {'query': query, 'limit': 20},
      );
      final response = await _ipcClient.sendRequest(request);

      if (response.isSuccess && response.data != null) {
        final searchResults = (response.data['results'] as List<dynamic>?)
            ?.map((item) => item as Map<String, dynamic>)
            .toList() ?? [];

        final stars = SearchStarMapper.mapSearchResultsToStars(
          searchResults,
          Size(800, 600),
        );

        state = state.copyWith(
          celestialObjects: stars,
          connections: [],
          currentMode: 'search',
          isLoading: false,
          lastUpdated: DateTime.now(),
        );
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: '搜索失败: $e',
      );
    }
  }

  /// 刷新当前模式的数据
  Future<void> refreshData() async {
    await switchMode(state.currentMode);
  }

  /// 清除错误状态
  void clearError() {
    state = state.copyWith(error: null);
  }
}

/// 星空宇宙状态提供者
final starryUniverseProvider = StateNotifierProvider<StarryUniverseNotifier, StarryUniverseState>(
  (ref) => StarryUniverseNotifier(),
);

/// 粒子系统提供者
final particleSystemProvider = Provider<OptimizedParticleSystem>((ref) {
  return OptimizedParticleSystem(
    maxParticles: 1000,
    spawnRate: 30.0,
  );
});

/// 动画控制器提供者
final cosmicAnimationProvider = Provider<CosmicAnimationController>((ref) {
  return CosmicAnimationController();
});