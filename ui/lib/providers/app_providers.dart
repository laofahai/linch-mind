import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/connector_lifecycle_models.dart';
import '../services/connector_lifecycle_api_client.dart';
import '../services/daemon_lifecycle_service.dart';

// 主题管理提供者
final themeModeProvider =
    StateNotifierProvider<ThemeModeNotifier, ThemeMode>((ref) {
  return ThemeModeNotifier();
});

class ThemeModeNotifier extends StateNotifier<ThemeMode> {
  ThemeModeNotifier() : super(ThemeMode.system);

  void setThemeMode(ThemeMode mode) {
    state = mode;
  }

  void toggleTheme() {
    switch (state) {
      case ThemeMode.light:
        state = ThemeMode.dark;
        break;
      case ThemeMode.dark:
        state = ThemeMode.system;
        break;
      case ThemeMode.system:
        state = ThemeMode.light;
        break;
    }
  }
}

// 连接器生命周期API客户端提供者
final connectorLifecycleApiProvider =
    Provider<ConnectorLifecycleApiClient>((ref) {
  return ConnectorLifecycleApiService.instance;
});

// 连接器定义提供者
final connectorDefinitionsProvider =
    FutureProvider<List<ConnectorDefinition>>((ref) async {
  final apiClient = ref.watch(connectorLifecycleApiProvider);
  final response = await apiClient.discoverConnectors();
  return response.connectors;
});

// 连接器提供者
final connectorsProvider = FutureProvider<List<ConnectorInfo>>((ref) async {
  final apiClient = ref.watch(connectorLifecycleApiProvider);
  final response = await apiClient.getConnectors();
  return response.connectors;
});

// 后台daemon初始化提供者 - 不阻塞UI启动
final backgroundDaemonInitProvider = FutureProvider<bool>((ref) async {
  try {
    final daemonService = DaemonLifecycleService.instance;
    print('[BackgroundInit] 开始后台daemon初始化');

    final result = await daemonService.ensureDaemonRunning();
    if (result.success) {
      print('[BackgroundInit] Daemon启动成功');
      // 更新应用状态
      ref.read(appStateProvider.notifier).setConnected(true);
      return true;
    } else {
      print('[BackgroundInit] Daemon启动失败: ${result.error}');
      ref
          .read(appStateProvider.notifier)
          .setError(result.error ?? 'Daemon启动失败');
      return false;
    }
  } catch (e) {
    print('[BackgroundInit] 后台初始化异常: $e');
    ref.read(appStateProvider.notifier).setError('后台初始化失败: $e');
    return false;
  }
});

// 健康检查提供者 - 简化版本，直接检查API连通性
final healthCheckProvider = FutureProvider<bool>((ref) async {
  try {
    final apiClient = ref.watch(connectorLifecycleApiProvider);
    // 使用简单的连接器列表API来检查连通性，避免复杂的健康检查模型解析
    final response = await apiClient.getConnectors();
    print(
        '[HealthCheck] Success: ${response.success}, Connectors: ${response.connectors.length}');
    return response.success;
  } catch (e) {
    print('[HealthCheck] Error: $e');
    return false;
  }
});

// 应用状态提供者
final appStateProvider =
    StateNotifierProvider<AppStateNotifier, AppState>((ref) {
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

  bool get hasError => errorMessage != null;

  AppState copyWith({
    bool? isConnected,
    String? errorMessage,
    DateTime? lastUpdate,
    bool clearError = false,
  }) {
    return AppState(
      isConnected: isConnected ?? this.isConnected,
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
      lastUpdate: lastUpdate ?? this.lastUpdate,
    );
  }
}

// 应用状态通知器
class AppStateNotifier extends StateNotifier<AppState> {
  AppStateNotifier()
      : super(AppState(
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
      clearError: true,
      lastUpdate: DateTime.now(),
    );
  }
}

// 连接器实例状态管理提供者
final connectorInstanceStateProvider = StateNotifierProvider.family<
    ConnectorInstanceStateNotifier,
    ConnectorInstanceState,
    String>((ref, instanceId) {
  return ConnectorInstanceStateNotifier(
      ref.watch(connectorLifecycleApiProvider), instanceId);
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
    bool clearError = false,
  }) {
    return ConnectorInstanceState(
      instanceId: instanceId,
      state: state ?? this.state,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
    );
  }
}

class ConnectorInstanceStateNotifier
    extends StateNotifier<ConnectorInstanceState> {
  final ConnectorLifecycleApiClient apiClient;
  final String instanceId;

  ConnectorInstanceStateNotifier(this.apiClient, this.instanceId)
      : super(ConnectorInstanceState(
          instanceId: instanceId,
          state: ConnectorState.configured,
        ));

  Future<void> startInstance() async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      await apiClient.startConnector(instanceId);
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
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      await apiClient.stopConnector(instanceId);
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
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      await apiClient.restartConnector(instanceId);
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
