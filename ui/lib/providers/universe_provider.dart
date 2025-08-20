/// 球形宇宙数据提供者 - 管理真实数据到3D可视化的状态
import 'dart:async';
import 'dart:math' as math;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import '../models/connector_lifecycle_models.dart';
import '../widgets/starry_universe/core/starry_canvas.dart';
import '../services/connector_lifecycle_api_client.dart';
import '../services/universe_data_adapter.dart';
import '../utils/app_logger.dart';

part 'universe_provider.freezed.dart';

/// 球形宇宙状态
@freezed
class UniverseState with _$UniverseState {
  const factory UniverseState({
    // 数据加载状态
    @Default(false) bool isLoading,
    String? error,

    // 原始数据
    @Default([]) List<ConnectorInfo> connectors,
    @Default({}) Map<String, dynamic> relationshipData,

    // 转换后的3D对象
    @Default([]) List<CelestialObject> celestialObjects,
    @Default([]) List<StarConnection> connections,

    // 统计信息
    @Default(0) int totalConnectors,
    @Default(0) int runningConnectors,
    @Default(0) int errorConnectors,
    @Default(0) int totalConnections,

    // 最后更新时间
    DateTime? lastUpdated,

    // 选中状态
    String? selectedConnectorId,
    Map<String, dynamic>? selectedConnectorInfo,
  }) = _UniverseState;
}

/// 球形宇宙数据提供者
class UniverseNotifier extends StateNotifier<UniverseState> {
  UniverseNotifier() : super(const UniverseState()) {
    _initialize();
  }

  final ConnectorLifecycleApiClient _apiClient =
      ConnectorLifecycleApiService.instance;
  Timer? _refreshTimer;

  /// 初始化
  Future<void> _initialize() async {
    AppLogger.info('初始化球形宇宙数据提供者', module: 'UniverseProvider');
    await refreshData();
    _startPeriodicRefresh();
  }

  /// 开始定期刷新
  void _startPeriodicRefresh() {
    _refreshTimer?.cancel();
    _refreshTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      refreshData();
    });
    AppLogger.debug('启动定期数据刷新 (30秒)', module: 'UniverseProvider');
  }

  /// 刷新数据
  Future<void> refreshData() async {
    if (state.isLoading) return; // 防止重复加载

    AppLogger.info('开始刷新球形宇宙数据', module: 'UniverseProvider');

    state = state.copyWith(isLoading: true, error: null);

    try {
      // 1. 获取连接器数据
      final connectorResponse = await _apiClient.getConnectors();

      if (!connectorResponse.success) {
        throw Exception('获取连接器数据失败: ${connectorResponse.connectors}');
      }

      final connectors = connectorResponse.connectors;
      AppLogger.info('获取到连接器数据',
          module: 'UniverseProvider', data: {'count': connectors.length});

      // 2. 转换为3D对象
      final celestialObjects =
          UnifiedStarryDataAdapter.convertConnectorsToStars(connectors);

      // 3. 生成连接关系 (暂时使用模拟数据，后续可接入真实关系数据)
      final connections =
          UnifiedStarryDataAdapter.convertRelationshipsToConnections(
              connectors, {} // TODO: 接入真实的NetworkX关系数据
              );

      // 4. 计算统计信息
      final stats = _calculateStatistics(connectors, connections);

      // 5. 更新状态
      state = state.copyWith(
        isLoading: false,
        error: null,
        connectors: connectors,
        celestialObjects: celestialObjects,
        connections: connections,
        totalConnectors: stats['totalConnectors'] ?? 0,
        runningConnectors: stats['runningConnectors'] ?? 0,
        errorConnectors: stats['errorConnectors'] ?? 0,
        totalConnections: stats['totalConnections'] ?? 0,
        lastUpdated: DateTime.now(),
      );

      AppLogger.info('球形宇宙数据刷新完成', module: 'UniverseProvider', data: {
        'connectors': connectors.length,
        'celestial_objects': celestialObjects.length,
        'connections': connections.length,
        'running': stats['runningConnectors'],
        'errors': stats['errorConnectors'],
      });
    } catch (e, stackTrace) {
      AppLogger.error('刷新球形宇宙数据失败',
          module: 'UniverseProvider', exception: e, stackTrace: stackTrace);

      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// 计算统计信息
  Map<String, int> _calculateStatistics(
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

  /// 选中连接器
  void selectConnector(String? connectorId) {
    AppLogger.debug('选中连接器',
        module: 'UniverseProvider', data: {'id': connectorId});

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

  /// 启动连接器
  Future<void> startConnector(String connectorId) async {
    AppLogger.info('启动连接器',
        module: 'UniverseProvider', data: {'id': connectorId});

    try {
      final response = await _apiClient.startConnector(connectorId);
      if (response.success) {
        AppLogger.info('连接器启动成功',
            module: 'UniverseProvider', data: {'id': connectorId});
        await refreshData(); // 刷新数据以反映状态变化
      } else {
        throw Exception(response.message);
      }
    } catch (e) {
      AppLogger.error('启动连接器失败',
          module: 'UniverseProvider', exception: e, data: {'id': connectorId});

      // 可以选择显示错误通知
      rethrow;
    }
  }

  /// 停止连接器
  Future<void> stopConnector(String connectorId) async {
    AppLogger.info('停止连接器',
        module: 'UniverseProvider', data: {'id': connectorId});

    try {
      final response = await _apiClient.stopConnector(connectorId);
      if (response.success) {
        AppLogger.info('连接器停止成功',
            module: 'UniverseProvider', data: {'id': connectorId});
        await refreshData();
      } else {
        throw Exception(response.message);
      }
    } catch (e) {
      AppLogger.error('停止连接器失败',
          module: 'UniverseProvider', exception: e, data: {'id': connectorId});
      rethrow;
    }
  }

  /// 重启连接器
  Future<void> restartConnector(String connectorId) async {
    AppLogger.info('重启连接器',
        module: 'UniverseProvider', data: {'id': connectorId});

    try {
      final response = await _apiClient.restartConnector(connectorId);
      if (response.success) {
        AppLogger.info('连接器重启成功',
            module: 'UniverseProvider', data: {'id': connectorId});
        await refreshData();
      } else {
        throw Exception(response.message);
      }
    } catch (e) {
      AppLogger.error('重启连接器失败',
          module: 'UniverseProvider', exception: e, data: {'id': connectorId});
      rethrow;
    }
  }

  /// 删除连接器
  Future<void> deleteConnector(String connectorId) async {
    AppLogger.info('删除连接器',
        module: 'UniverseProvider', data: {'id': connectorId});

    try {
      final response = await _apiClient.deleteConnector(connectorId);
      if (response.success) {
        AppLogger.info('连接器删除成功',
            module: 'UniverseProvider', data: {'id': connectorId});
        await refreshData();
      } else {
        throw Exception(response.message);
      }
    } catch (e) {
      AppLogger.error('删除连接器失败',
          module: 'UniverseProvider', exception: e, data: {'id': connectorId});
      rethrow;
    }
  }

  /// 强制立即刷新
  Future<void> forceRefresh() async {
    AppLogger.info('强制刷新球形宇宙数据', module: 'UniverseProvider');
    await refreshData();
  }

  /// 切换自动刷新
  void toggleAutoRefresh(bool enabled) {
    if (enabled) {
      _startPeriodicRefresh();
      AppLogger.info('启用自动刷新', module: 'UniverseProvider');
    } else {
      _refreshTimer?.cancel();
      _refreshTimer = null;
      AppLogger.info('禁用自动刷新', module: 'UniverseProvider');
    }
  }

  /// 获取连接器详细信息
  ConnectorInfo? getConnectorById(String connectorId) {
    try {
      return state.connectors.firstWhere((c) => c.connectorId == connectorId);
    } catch (e) {
      return null;
    }
  }

  /// 按状态过滤连接器
  List<ConnectorInfo> getConnectorsByState(ConnectorState targetState) {
    return state.connectors.where((c) => c.state == targetState).toList();
  }

  /// 获取高重要性连接器
  List<ConnectorInfo> getHighImportanceConnectors({int limit = 10}) {
    final connectorsWithImportance = state.connectors.map((c) {
      final importance = _calculateConnectorImportance(c);
      return {'connector': c, 'importance': importance};
    }).toList();

    connectorsWithImportance.sort((a, b) =>
        (b['importance'] as double).compareTo(a['importance'] as double));

    return connectorsWithImportance
        .take(limit)
        .map((item) => item['connector'] as ConnectorInfo)
        .toList();
  }

  /// 计算连接器重要性（内部方法）
  double _calculateConnectorImportance(ConnectorInfo connector) {
    // 使用适配器的重要性计算逻辑
    double score = 0.0;

    switch (connector.state) {
      case ConnectorState.running:
        score += 0.4;
        break;
      case ConnectorState.starting:
        score += 0.3;
        break;
      case ConnectorState.error:
        score += 0.25;
        break;
      default:
        score += 0.1;
        break;
    }

    if (connector.dataCount > 0) {
      final logDataCount = math.log(connector.dataCount + 1) / math.log(10000);
      score += 0.3 * logDataCount.clamp(0.0, 1.0);
    }

    if (connector.enabled) score += 0.1;

    return score.clamp(0.0, 1.0);
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }
}

// Provider实例
final universeProvider = StateNotifierProvider<UniverseNotifier, UniverseState>(
  (ref) => UniverseNotifier(),
);

// 便捷访问器
final selectedConnectorProvider = Provider<ConnectorInfo?>((ref) {
  final state = ref.watch(universeProvider);
  if (state.selectedConnectorId == null) return null;

  try {
    return state.connectors.firstWhere(
      (c) => c.connectorId == state.selectedConnectorId,
    );
  } catch (e) {
    return null;
  }
});

final universeStatsProvider = Provider<Map<String, int>>((ref) {
  final state = ref.watch(universeProvider);
  return {
    'total': state.totalConnectors,
    'running': state.runningConnectors,
    'error': state.errorConnectors,
    'connections': state.totalConnections,
  };
});

final isUniverseLoadingProvider = Provider<bool>((ref) {
  return ref.watch(universeProvider.select((state) => state.isLoading));
});

final universeErrorProvider = Provider<String?>((ref) {
  return ref.watch(universeProvider.select((state) => state.error));
});
