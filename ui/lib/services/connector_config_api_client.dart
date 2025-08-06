import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/connector_lifecycle_models.dart';
import 'ipc_api_adapter.dart';

/// 连接器配置API客户端
class ConnectorConfigApiClient {
  final IPCApiAdapter _ipcApi = IPCApiService.instance;

  ConnectorConfigApiClient();

  /// 获取连接器配置Schema
  Future<ConnectorApiResponse> getConfigSchema(String connectorId) async {
    try {
      final responseData = await _ipcApi.get('/connector-config/schema/$connectorId');
      return ConnectorApiResponse.fromJson(responseData);
    } catch (e) {
      return ConnectorApiResponse(
        success: false,
        message: '获取配置Schema失败: $e',
        error: e.toString(),
      );
    }
  }

  /// 获取当前配置
  Future<ConnectorApiResponse> getCurrentConfig(String connectorId) async {
    try {
      final responseData = await _ipcApi.get('/connector-config/current/$connectorId');
      return ConnectorApiResponse.fromJson(responseData);
    } catch (e) {
      return ConnectorApiResponse(
        success: false,
        message: '获取当前配置失败: $e',
        error: e.toString(),
      );
    }
  }

  /// 验证配置
  Future<ConnectorApiResponse> validateConfig(
    String connectorId,
    Map<String, dynamic> config,
  ) async {
    try {
      final responseData = await _ipcApi.post(
        '/connector-config/validate',
        data: {
          'connector_id': connectorId,
          'config': config,
        },
      );
      return ConnectorApiResponse.fromJson(responseData);
    } catch (e) {
      return ConnectorApiResponse(
        success: false,
        message: '验证配置失败: $e',
        error: e.toString(),
      );
    }
  }

  /// 更新配置
  Future<ConnectorApiResponse> updateConfig(
    String connectorId,
    Map<String, dynamic> config, {
    String configVersion = '1.0.0',
    String changeReason = '用户更新',
  }) async {
    try {
      final responseData = await _ipcApi.put(
        '/connector-config/update',
        data: {
          'connector_id': connectorId,
          'config': config,
          'config_version': configVersion,
          'change_reason': changeReason,
        },
      );
      return ConnectorApiResponse.fromJson(responseData);
    } catch (e) {
      return ConnectorApiResponse(
        success: false,
        message: '更新配置失败: $e',
        error: e.toString(),
      );
    }
  }

  /// 重置配置
  Future<ConnectorApiResponse> resetConfig(
    String connectorId, {
    bool toDefaults = true,
  }) async {
    try {
      final responseData = await _ipcApi.post(
        '/connector-config/reset',
        data: {
          'connector_id': connectorId,
          'to_defaults': toDefaults,
        },
      );
      return ConnectorApiResponse.fromJson(responseData);
    } catch (e) {
      return ConnectorApiResponse(
        success: false,
        message: '重置配置失败: $e',
        error: e.toString(),
      );
    }
  }

  /// 获取配置历史
  Future<ConnectorApiResponse> getConfigHistory(
    String connectorId, {
    int limit = 10,
    int offset = 0,
  }) async {
    try {
      final responseData = await _ipcApi.get(
        '/connector-config/history/$connectorId',
        queryParameters: {
          'limit': limit,
          'offset': offset,
        },
      );
      return ConnectorApiResponse.fromJson(responseData);
    } catch (e) {
      return ConnectorApiResponse(
        success: false,
        message: '获取配置历史失败: $e',
        error: e.toString(),
      );
    }
  }

  /// 获取所有连接器的配置Schema概览
  Future<ConnectorApiResponse> getAllSchemas() async {
    try {
      final responseData = await _ipcApi.get('/connector-config/all-schemas');
      return ConnectorApiResponse.fromJson(responseData);
    } catch (e) {
      return ConnectorApiResponse(
        success: false,
        message: '获取所有Schema失败: $e',
        error: e.toString(),
      );
    }
  }

  /// 注册自定义UI组件
  Future<ConnectorApiResponse> registerCustomWidget(
    String connectorId,
    String widgetName,
    Map<String, dynamic> widgetConfig,
  ) async {
    try {
      final responseData = await _ipcApi.post(
        '/connector-ui/register-custom-widget',
        data: {
          'connector_id': connectorId,
          'widget_name': widgetName,
          'widget_config': widgetConfig,
        },
      );
      return ConnectorApiResponse.fromJson(responseData);
    } catch (e) {
      return ConnectorApiResponse(
        success: false,
        message: '注册自定义组件失败: $e',
        error: e.toString(),
      );
    }
  }

  /// 获取自定义组件配置
  Future<ConnectorApiResponse> getCustomWidgetConfig(
    String connectorId,
    String widgetName,
  ) async {
    try {
      final responseData = await _ipcApi.get(
        '/connector-ui/custom-widget/$connectorId/$widgetName',
      );
      return ConnectorApiResponse.fromJson(responseData);
    } catch (e) {
      return ConnectorApiResponse(
        success: false,
        message: '获取自定义组件配置失败: $e',
        error: e.toString(),
      );
    }
  }

  /// 验证自定义组件配置
  Future<ConnectorApiResponse> validateCustomConfig(
    String connectorId,
    String widgetName,
    Map<String, dynamic> configData,
  ) async {
    try {
      final responseData = await _ipcApi.post(
        '/connector-ui/validate-custom-config',
        data: {
          'connector_id': connectorId,
          'widget_name': widgetName,
          'config_data': configData,
        },
      );
      return ConnectorApiResponse.fromJson(responseData);
    } catch (e) {
      return ConnectorApiResponse(
        success: false,
        message: '验证自定义组件配置失败: $e',
        error: e.toString(),
      );
    }
  }

  /// 获取连接器可用的自定义组件
  Future<ConnectorApiResponse> getAvailableWidgets(String connectorId) async {
    try {
      final responseData = await _ipcApi.get(
        '/connector-ui/available-widgets/$connectorId',
      );
      return ConnectorApiResponse.fromJson(responseData);
    } catch (e) {
      return ConnectorApiResponse(
        success: false,
        message: '获取可用组件失败: $e',
        error: e.toString(),
      );
    }
  }

  /// 执行自定义组件动作
  Future<ConnectorApiResponse> executeWidgetAction(
    String connectorId,
    String widgetName,
    String actionName,
    Map<String, dynamic> actionParams,
  ) async {
    try {
      final responseData = await _ipcApi.post(
        '/connector-ui/execute-widget-action',
        data: {
          'connector_id': connectorId,
          'widget_name': widgetName,
          'action_name': actionName,
          'action_params': actionParams,
        },
      );
      return ConnectorApiResponse.fromJson(responseData);
    } catch (e) {
      return ConnectorApiResponse(
        success: false,
        message: '执行组件动作失败: $e',
        error: e.toString(),
      );
    }
  }

  /// 清理资源
  void dispose() {
    // IPC适配器由IPCApiService统一管理
  }
}

/// 连接器配置API客户端Provider
final connectorConfigApiClientProvider =
    Provider<ConnectorConfigApiClient>((ref) {
  return ConnectorConfigApiClient();
});

/// 配置Schema状态管理
class ConfigSchemaNotifier
    extends StateNotifier<AsyncValue<Map<String, dynamic>>> {
  final ConnectorConfigApiClient _apiClient;

  ConfigSchemaNotifier(this._apiClient) : super(const AsyncValue.loading());

  Future<void> loadSchema(String connectorId) async {
    state = const AsyncValue.loading();

    try {
      final response = await _apiClient.getConfigSchema(connectorId);
      if (response.success) {
        state = AsyncValue.data(response.data as Map<String, dynamic>? ?? {});
      } else {
        state = AsyncValue.error(response.message, StackTrace.current);
      }
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
    }
  }
}

/// 配置Schema Provider
final configSchemaProvider = StateNotifierProvider.family<ConfigSchemaNotifier,
    AsyncValue<Map<String, dynamic>>, String>((ref, connectorId) {
  final apiClient = ref.watch(connectorConfigApiClientProvider);
  final notifier = ConfigSchemaNotifier(apiClient);
  notifier.loadSchema(connectorId);
  return notifier;
});

/// 当前配置状态管理
class CurrentConfigNotifier
    extends StateNotifier<AsyncValue<Map<String, dynamic>>> {
  final ConnectorConfigApiClient _apiClient;

  CurrentConfigNotifier(this._apiClient) : super(const AsyncValue.loading());

  Future<void> loadConfig(String connectorId) async {
    state = const AsyncValue.loading();

    try {
      final response = await _apiClient.getCurrentConfig(connectorId);
      if (response.success) {
        final data = response.data as Map<String, dynamic>? ?? {};
        state = AsyncValue.data(data['config'] as Map<String, dynamic>? ?? {});
      } else {
        state = AsyncValue.error(response.message, StackTrace.current);
      }
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
    }
  }

  Future<bool> updateConfig(
      String connectorId, Map<String, dynamic> config) async {
    try {
      final response = await _apiClient.updateConfig(connectorId, config);
      if (response.success) {
        state = AsyncValue.data(config);
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }
}

/// 当前配置Provider
final currentConfigProvider = StateNotifierProvider.family<
    CurrentConfigNotifier,
    AsyncValue<Map<String, dynamic>>,
    String>((ref, connectorId) {
  final apiClient = ref.watch(connectorConfigApiClientProvider);
  final notifier = CurrentConfigNotifier(apiClient);
  notifier.loadConfig(connectorId);
  return notifier;
});
