import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/api_models.dart';
import '../models/connector_lifecycle_models.dart';
import '../services/api_client.dart';
import '../services/connector_lifecycle_api_client.dart';

// API 客户端提供者
final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

// 连接器生命周期API客户端提供者
final connectorLifecycleApiProvider = Provider<ConnectorLifecycleApiClient>((ref) {
  return ConnectorLifecycleApiService.instance;
});

// 服务器信息提供者
final serverInfoProvider = FutureProvider<ServerInfo>((ref) async {
  final apiClient = ref.watch(apiClientProvider);
  return await apiClient.getServerInfo();
});

// 连接器类型提供者（新API）
final connectorTypesProvider = FutureProvider<List<ConnectorTypeInfo>>((ref) async {
  final apiClient = ref.watch(connectorLifecycleApiProvider);
  final response = await apiClient.discoverConnectorTypes();
  return response.connectorTypes;
});

// 连接器实例提供者（新API）
final connectorInstancesProvider = FutureProvider<List<ConnectorInstanceInfo>>((ref) async {
  final apiClient = ref.watch(connectorLifecycleApiProvider);
  final response = await apiClient.getConnectorInstances();
  return response.instances;
});

// 数据项列表提供者
final dataItemsProvider = FutureProvider.family<List<DataItem>, int?>((ref, limit) async {
  final apiClient = ref.watch(apiClientProvider);
  return await apiClient.getData(limit: limit);
});

// AI 推荐提供者
final recommendationsProvider = FutureProvider.family<List<AIRecommendation>, int?>((ref, limit) async {
  final apiClient = ref.watch(apiClientProvider);
  return await apiClient.getRecommendations(limit: limit);
});

// 图数据节点提供者
final graphNodesProvider = FutureProvider.family<List<GraphNode>, int?>((ref, limit) async {
  final apiClient = ref.watch(apiClientProvider);
  return await apiClient.getGraphNodes(limit: limit);
});

// 数据库统计提供者
final databaseStatsProvider = FutureProvider<DatabaseStats>((ref) async {
  final apiClient = ref.watch(apiClientProvider);
  return await apiClient.getDatabaseStats();
});

// 健康检查提供者
final healthCheckProvider = FutureProvider<bool>((ref) async {
  final apiClient = ref.watch(apiClientProvider);
  return await apiClient.healthCheck();
});

// 连接器系统健康检查提供者（新API）
final connectorHealthProvider = FutureProvider<ConnectorHealthResponse>((ref) async {
  final apiClient = ref.watch(connectorLifecycleApiProvider);
  return await apiClient.getHealthCheck();
});

// 系统诊断提供者
final systemDiagnosticsProvider = FutureProvider<SystemDiagnostics>((ref) async {
  final apiClient = ref.watch(apiClientProvider);
  return await apiClient.getSystemDiagnostics();
});

// 应用状态提供者
final appStateProvider = StateNotifierProvider<AppStateNotifier, AppState>((ref) {
  return AppStateNotifier();
});

// 应用状态数据类
class AppState {
  final bool isConnected;
  final String? errorMessage;
  final DateTime lastUpdate;

  AppState({
    required this.isConnected,
    this.errorMessage,
    required this.lastUpdate,
  });

  AppState copyWith({
    bool? isConnected,
    String? errorMessage,
    DateTime? lastUpdate,
  }) {
    return AppState(
      isConnected: isConnected ?? this.isConnected,
      errorMessage: errorMessage ?? this.errorMessage,
      lastUpdate: lastUpdate ?? this.lastUpdate,
    );
  }
}

// 应用状态通知器
class AppStateNotifier extends StateNotifier<AppState> {
  AppStateNotifier() : super(AppState(
    isConnected: false,
    lastUpdate: DateTime.now(),
  ));

  void setConnected(bool connected) {
    state = state.copyWith(
      isConnected: connected,
      errorMessage: connected ? null : 'Connection lost',
      lastUpdate: DateTime.now(),
    );
  }

  void setError(String error) {
    state = state.copyWith(
      isConnected: false,
      errorMessage: error,
      lastUpdate: DateTime.now(),
    );
  }

  void clearError() {
    state = state.copyWith(
      errorMessage: null,
      lastUpdate: DateTime.now(),
    );
  }
}

// 连接器实例状态管理提供者（新API）
final connectorInstanceStateProvider = StateNotifierProvider.family<ConnectorInstanceStateNotifier, ConnectorInstanceState, String>((ref, instanceId) {
  return ConnectorInstanceStateNotifier(ref.watch(connectorLifecycleApiProvider), instanceId);
});

class ConnectorInstanceState {
  final String instanceId;
  final ConnectorState state;
  final bool isLoading;
  final String? errorMessage;

  ConnectorInstanceState({
    required this.instanceId,
    required this.state,
    this.isLoading = false,
    this.errorMessage,
  });

  ConnectorInstanceState copyWith({
    ConnectorState? state,
    bool? isLoading,
    String? errorMessage,
  }) {
    return ConnectorInstanceState(
      instanceId: instanceId,
      state: state ?? this.state,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }
}

class ConnectorInstanceStateNotifier extends StateNotifier<ConnectorInstanceState> {
  final ConnectorLifecycleApiClient apiClient;
  final String instanceId;

  ConnectorInstanceStateNotifier(this.apiClient, this.instanceId) : super(ConnectorInstanceState(
    instanceId: instanceId,
    state: ConnectorState.configured,
  ));

  Future<void> startInstance() async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      await apiClient.startConnectorInstance(instanceId);
      state = state.copyWith(state: ConnectorState.running, isLoading: false);
    } catch (e) {
      state = state.copyWith(
        state: ConnectorState.error,
        isLoading: false,
        errorMessage: e.toString(),
      );
    }
  }

  Future<void> stopInstance() async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      await apiClient.stopConnectorInstance(instanceId);
      state = state.copyWith(state: ConnectorState.enabled, isLoading: false);
    } catch (e) {
      state = state.copyWith(
        state: ConnectorState.error,
        isLoading: false,
        errorMessage: e.toString(),
      );
    }
  }

  Future<void> restartInstance() async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      await apiClient.restartConnectorInstance(instanceId);
      state = state.copyWith(state: ConnectorState.running, isLoading: false);
    } catch (e) {
      state = state.copyWith(
        state: ConnectorState.error,
        isLoading: false,
        errorMessage: e.toString(),
      );
    }
  }
}