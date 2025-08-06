import 'dart:async';
import '../models/connector_lifecycle_models.dart';
import 'ipc_api_adapter.dart';

/// 专门的连接器生命周期API客户端
/// 对应 daemon 的 /connector-lifecycle 端点
class ConnectorLifecycleApiClient {
  final IPCApiAdapter _ipcApi = IPCApiService.instance;

  ConnectorLifecycleApiClient();

  /// 清理资源
  void dispose() {
    // IPC适配器由IPCApiService统一管理
  }

  /// 发现可用的连接器
  Future<DiscoveryResponse> discoverConnectors() async {
    try {
      final responseData = await _ipcApi.get('/connector-lifecycle/discovery');

      // 转换嵌套的data结构为平铺结构
      final data = responseData['data'] as Map<String, dynamic>;

      final flatResponse = {
        'success': responseData['success'],
        'message': responseData['message'],
        'connectors': data['connectors'],
      };

      return DiscoveryResponse.fromJson(flatResponse);
    } catch (e) {
      throw ConnectorApiException('Failed to discover connectors: $e');
    }
  }

  /// 创建连接器
  Future<OperationResponse> createConnector(
      CreateConnectorRequest request) async {
    try {
      final responseData = await _ipcApi.post(
        '/connector-lifecycle/connectors',
        data: {
          'connector_id': request.connectorId,
          'display_name': request.displayName,
          'config': request.config,
          'auto_start': request.autoStart,
          if (request.templateId != null) 'template_id': request.templateId,
        },
      );
      return OperationResponse.fromJson(responseData);
    } catch (e) {
      throw ConnectorApiException('Failed to create connector: $e');
    }
  }

  /// 获取连接器列表
  Future<ConnectorListResponse> getConnectors({
    String? connectorId,
    String? state,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (connectorId != null) queryParams['connector_id'] = connectorId;
      if (state != null) queryParams['state'] = state;

      final responseData = await _ipcApi.get(
        '/connector-lifecycle/connectors',
        queryParameters: queryParams,
      );

      // 转换嵌套的data结构为平铺结构
      final data = responseData['data'] as Map<String, dynamic>;

      final flatResponse = {
        'success': responseData['success'],
        'collectors': data['collectors'],
        'total_count': data['total'],
      };

      return ConnectorListResponse.fromJson(flatResponse);
    } catch (e) {
      throw ConnectorApiException('Failed to get connectors: $e');
    }
  }

  /// 获取连接器详情
  Future<ConnectorDetailResponse> getConnector(String connectorId) async {
    try {
      final responseData = await _ipcApi.get('/connector-lifecycle/connectors/$connectorId');
      return ConnectorDetailResponse.fromJson(responseData);
    } catch (e) {
      throw ConnectorApiException('Failed to get connector $connectorId: $e');
    }
  }

  /// 启动连接器
  Future<OperationResponse> startConnector(String connectorId) async {
    try {
      final responseData = await _ipcApi.post('/connector-lifecycle/connectors/$connectorId/actions/start');
      return OperationResponse.fromJson(responseData);
    } catch (e) {
      throw ConnectorApiException('Failed to start connector $connectorId: $e');
    }
  }

  /// 停止连接器
  Future<OperationResponse> stopConnector(String connectorId,
      {bool force = false}) async {
    try {
      final queryParams = force ? {'force': 'true'} : <String, dynamic>{};
      final responseData = await _ipcApi.post(
        '/connector-lifecycle/connectors/$connectorId/actions/stop',
        queryParameters: queryParams,
      );
      return OperationResponse.fromJson(responseData);
    } catch (e) {
      throw ConnectorApiException('Failed to stop connector $connectorId: $e');
    }
  }

  /// 重启连接器
  Future<OperationResponse> restartConnector(String connectorId) async {
    try {
      final responseData = await _ipcApi.post('/connector-lifecycle/connectors/$connectorId/actions/restart');
      return OperationResponse.fromJson(responseData);
    } catch (e) {
      throw ConnectorApiException('Failed to restart connector $connectorId: $e');
    }
  }

  /// 更新连接器配置
  Future<OperationResponse> updateConnectorConfig(
      String connectorId, UpdateConfigRequest request) async {
    try {
      final responseData = await _ipcApi.put(
        '/connector-lifecycle/connectors/$connectorId/config',
        data: {'config': request.config},
      );
      return OperationResponse.fromJson(responseData);
    } catch (e) {
      throw ConnectorApiException('Failed to update connector config $connectorId: $e');
    }
  }

  /// 删除连接器
  Future<OperationResponse> deleteConnector(String connectorId,
      {bool force = false}) async {
    try {
      final queryParams = force ? {'force': 'true'} : <String, dynamic>{};
      final responseData = await _ipcApi.delete(
        '/connector-lifecycle/connectors/$connectorId',
        queryParameters: queryParams,
      );
      return OperationResponse.fromJson(responseData);
    } catch (e) {
      throw ConnectorApiException('Failed to delete connector $connectorId: $e');
    }
  }

  /// 获取所有连接器状态概览
  Future<ConnectorStatesOverview> getStatesOverview() async {
    try {
      final responseData = await _ipcApi.get('/connector-lifecycle/system/states');
      return ConnectorStatesOverview.fromJson(responseData);
    } catch (e) {
      throw ConnectorApiException('Failed to get states overview: $e');
    }
  }

  /// 系统健康检查
  Future<ConnectorHealthResponse> getHealthCheck() async {
    try {
      final responseData = await _ipcApi.get('/connector-lifecycle/system/health');
      return ConnectorHealthResponse.fromJson(responseData);
    } catch (e) {
      throw ConnectorApiException('Failed to get health check: $e');
    }
  }

  /// 关闭所有连接器实例
  Future<ConnectorApiResponse> shutdownAllConnectors() async {
    try {
      final responseData = await _ipcApi.post('/connector-lifecycle/shutdown-all');
      return ConnectorApiResponse.fromJson(responseData);
    } catch (e) {
      throw ConnectorApiException('Failed to shutdown all connectors: $e');
    }
  }

  /// 扫描指定目录寻找连接器
  Future<DiscoveryResponse> scanConnectorDirectory(String directoryPath) async {
    try {
      final responseData = await _ipcApi.post(
        '/connector-lifecycle/dev/scan-directory',
        data: {'directory_path': directoryPath},
      );

      // 转换嵌套的data结构为平铺结构
      final data = responseData['data'] as Map<String, dynamic>;

      final flatResponse = {
        'success': responseData['success'],
        'message': responseData['message'],
        'connectors': data['connectors'],
      };

      return DiscoveryResponse.fromJson(flatResponse);
    } catch (e) {
      throw ConnectorApiException('Failed to scan directory $directoryPath: $e');
    }
  }

  /// 统一的连接器安装接口
  Future<OperationResponse> installConnector(InstallConnectorRequest request) async {
    try {
      final data = <String, dynamic>{
        'connector_id': request.connectorId,
        'source': request.source,
      };
      
      // 根据安装源添加额外字段
      if (request.displayName != null) {
        data['display_name'] = request.displayName;
      }
      if (request.config.isNotEmpty) {
        data['config'] = request.config;
      }
      if (request.autoStart) {
        data['auto_start'] = request.autoStart;
      }
      if (request.path != null) {
        data['path'] = request.path;
      }
      if (request.description != null) {
        data['description'] = request.description;
      }
      
      final responseData = await _ipcApi.post(
        '/connector-lifecycle/connectors',
        data: data,
      );
      return OperationResponse.fromJson(responseData);
    } catch (e) {
      throw ConnectorApiException('Failed to install connector ${request.connectorId}: $e');
    }
  }
  
  /// 简化版本 - 从registry安装连接器
  Future<OperationResponse> installFromRegistry(String connectorId) async {
    return installConnector(InstallConnectorRequest(
      connectorId: connectorId,
      source: 'registry',
    ));
  }

  /// 监听连接器事件流 (Server-Sent Events) - 简化版本
  /// TODO: 完整的SSE实现
  Stream<ConnectorEvent> watchConnectorEvents() async* {
    // 暂时返回空流，避免编译错误
    // 实际实现需要处理SSE格式
    yield* Stream<ConnectorEvent>.empty();
  }

  /// 关闭客户端连接
  void close() {
    // IPC适配器由IPCApiService统一管理，无需手动关闭
  }
}

/// 连接器API异常
class ConnectorApiException implements Exception {
  final String message;

  ConnectorApiException(this.message);

  @override
  String toString() => 'ConnectorApiException: $message';
}

/// 连接器生命周期API客户端单例
class ConnectorLifecycleApiService {
  static ConnectorLifecycleApiClient? _instance;

  static ConnectorLifecycleApiClient get instance {
    return _instance ??= ConnectorLifecycleApiClient();
  }

  static void dispose() {
    _instance?.dispose();
    _instance = null;
  }
}
