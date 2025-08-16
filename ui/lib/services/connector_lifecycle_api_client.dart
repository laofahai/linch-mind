import 'dart:async';
import '../models/connector_lifecycle_models.dart';
import '../utils/app_logger.dart';
import 'ipc_api_adapter.dart';
import 'response_parser.dart';

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

      // 使用ResponseParser统一解析
      if (!ResponseParser.isSuccess(responseData)) {
        final error = ResponseParser.getError(responseData) ?? 'Unknown error';
        throw ConnectorApiException('Discovery failed: $error');
      }

      final data = ResponseParser.extractData(responseData);
      final flatResponse = {
        'success': true,
        'message': ResponseParser.getMessage(responseData) ??
            'Connectors discovered successfully',
        'connectors': data['connectors'] ?? [],
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
          // 移除 auto_start 字段，因为数据库模型已经简化了逻辑
          if (request.templateId != null) 'template_id': request.templateId,
        },
      );
      // 从IPC响应中提取数据构造OperationResponse
      final data = responseData['data'] as Map<String, dynamic>? ?? {};
      final connector = data['connector'] as Map<String, dynamic>? ?? {};

      return OperationResponse(
        success: responseData['success'] ?? true,
        message: data['message'] ?? 'Connector created successfully',
        connectorId: connector['connector_id'] ?? request.connectorId,
        state: ConnectorState.values.firstWhere(
          (e) => e.name == (connector['state'] ?? 'stopped'),
          orElse: () => ConnectorState.stopped,
        ),
        hotReloadApplied: null,
        requiresRestart: null,
        wasRunning: null,
      );
    } catch (e, stackTrace) {
      print('创建连接器异常详情: $e');
      print('堆栈跟踪: $stackTrace');
      throw ConnectorApiException(
          'Failed to create connector: $e\nStack: $stackTrace');
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

      AppLogger.debug('开始请求getConnectors',
          module: 'ConnectorAPI', data: queryParams);

      final responseData = await _ipcApi.get(
        '/connector-lifecycle/connectors',
        queryParameters: queryParams,
      );

      AppLogger.debug('原始API响应',
          module: 'ConnectorAPI', data: {'response': responseData});

      // 检查响应数据结构
      AppLogger.debug('响应数据键值',
          module: 'ConnectorAPI', data: {'keys': responseData.keys.toList()});

      // 安全地转换嵌套的data结构为平铺结构
      // API返回格式: {success: true, data: {connectors: [...], total: N}, error: null}
      final data = responseData['data'] ?? responseData;
      AppLogger.debug('提取的data段',
          module: 'ConnectorAPI', data: {'extracted_data': data});

      final connectorsData = data['connectors'] ?? data['collectors'] ?? [];
      AppLogger.debug('连接器数据数组', module: 'ConnectorAPI', data: {
        'connectors_data': connectorsData,
        'type': connectorsData.runtimeType.toString(),
        'count': connectorsData is List ? connectorsData.length : 'not_list'
      });

      final flatResponse = {
        'success': responseData['success'] ?? true,
        'connectors': connectorsData,
        'total_count': data['total'] ?? 0,
      };

      AppLogger.debug('构造的flatResponse',
          module: 'ConnectorAPI', data: flatResponse);

      final result = ConnectorListResponse.fromJson(flatResponse);
      AppLogger.debug('解析后的结果', module: 'ConnectorAPI', data: {
        'success': result.success,
        'connectors_count': result.connectors.length
      });

      for (var i = 0; i < result.connectors.length; i++) {
        AppLogger.debug('连接器详情[$i]', module: 'ConnectorAPI', data: {
          'id': result.connectors[i].connectorId,
          'name': result.connectors[i].displayName,
          'state': result.connectors[i].state.toString()
        });
      }

      return result;
    } catch (e, stackTrace) {
      AppLogger.error('getConnectors异常',
          module: 'ConnectorAPI', exception: e, stackTrace: stackTrace);
      throw ConnectorApiException(
          'Failed to get connectors: $e\nStack: $stackTrace');
    }
  }

  /// 获取连接器详情
  Future<ConnectorDetailResponse> getConnector(String connectorId) async {
    try {
      final responseData =
          await _ipcApi.get('/connector-lifecycle/connectors/$connectorId');
      return ConnectorDetailResponse.fromJson(responseData);
    } catch (e) {
      throw ConnectorApiException('Failed to get connector $connectorId: $e');
    }
  }

  /// 启动连接器
  Future<OperationResponse> startConnector(String connectorId) async {
    try {
      final responseData = await _ipcApi
          .post('/connector-lifecycle/connectors/$connectorId/actions/start');

      // 处理嵌套响应结构
      final success = responseData['success'] ?? false;
      final data = responseData['data'] as Map<String, dynamic>? ?? {};
      final error = responseData['error'] as Map<String, dynamic>?;

      if (!success || error != null) {
        throw ConnectorApiException(
            'Failed to start connector: ${error?['message'] ?? 'Unknown error'}');
      }

      return OperationResponse(
        success: data['success'] ?? success,
        message: data['message'] ?? 'Connector started successfully',
        connectorId: data['connector_id'] ?? connectorId,
        state: ConnectorState.values.firstWhere(
          (e) => e.name == (data['state'] ?? 'running'),
          orElse: () => ConnectorState.running,
        ),
      );
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

      // 处理嵌套响应结构
      final success = responseData['success'] ?? false;
      final data = responseData['data'] as Map<String, dynamic>? ?? {};
      final error = responseData['error'] as Map<String, dynamic>?;

      if (!success || error != null) {
        throw ConnectorApiException(
            'Failed to stop connector: ${error?['message'] ?? 'Unknown error'}');
      }

      return OperationResponse(
        success: data['success'] ?? success,
        message: data['message'] ?? 'Connector stopped successfully',
        connectorId: data['connector_id'] ?? connectorId,
        state: ConnectorState.values.firstWhere(
          (e) => e.name == (data['state'] ?? 'stopped'),
          orElse: () => ConnectorState.stopped,
        ),
      );
    } catch (e) {
      throw ConnectorApiException('Failed to stop connector $connectorId: $e');
    }
  }

  /// 重启连接器
  Future<OperationResponse> restartConnector(String connectorId) async {
    try {
      final responseData = await _ipcApi
          .post('/connector-lifecycle/connectors/$connectorId/actions/restart');

      // 处理嵌套响应结构
      final success = responseData['success'] ?? false;
      final data = responseData['data'] as Map<String, dynamic>? ?? {};
      final error = responseData['error'] as Map<String, dynamic>?;

      if (!success || error != null) {
        throw ConnectorApiException(
            'Failed to restart connector: ${error?['message'] ?? 'Unknown error'}');
      }

      return OperationResponse(
        success: data['success'] ?? success,
        message: data['message'] ?? 'Connector restarted successfully',
        connectorId: data['connector_id'] ?? connectorId,
        state: ConnectorState.values.firstWhere(
          (e) => e.name == (data['state'] ?? 'running'),
          orElse: () => ConnectorState.running,
        ),
      );
    } catch (e) {
      throw ConnectorApiException(
          'Failed to restart connector $connectorId: $e');
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
      throw ConnectorApiException(
          'Failed to update connector config $connectorId: $e');
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

      // 处理响应结构 - 支持字符串和Map两种错误格式
      final success = responseData['success'] ?? false;
      final data = responseData['data'] as Map<String, dynamic>? ?? {};
      final error = responseData['error'];

      if (!success || error != null) {
        String errorMessage;
        if (error is Map<String, dynamic>) {
          errorMessage = error['message'] ?? 'Unknown error';
        } else if (error is String) {
          errorMessage = error;
        } else {
          errorMessage = 'Unknown error';
        }

        throw ConnectorApiException(
            'Failed to delete connector: $errorMessage');
      }

      return OperationResponse(
        success: data['success'] ?? success,
        message: data['message'] ?? 'Connector deleted successfully',
        connectorId: data['connector_id'] ?? connectorId,
        state: ConnectorState.values.firstWhere(
          (e) => e.name == (data['state'] ?? 'stopped'),
          orElse: () => ConnectorState.stopped,
        ),
      );
    } catch (e) {
      throw ConnectorApiException(
          'Failed to delete connector $connectorId: $e');
    }
  }

  /// 获取所有连接器状态概览
  Future<ConnectorStatesOverview> getStatesOverview() async {
    try {
      final responseData =
          await _ipcApi.get('/connector-lifecycle/system/states');
      return ConnectorStatesOverview.fromJson(responseData);
    } catch (e) {
      throw ConnectorApiException('Failed to get states overview: $e');
    }
  }

  /// 系统健康检查
  Future<ConnectorHealthResponse> getHealthCheck() async {
    try {
      final responseData =
          await _ipcApi.get('/connector-lifecycle/system/health');
      return ConnectorHealthResponse.fromJson(responseData);
    } catch (e) {
      throw ConnectorApiException('Failed to get health check: $e');
    }
  }

  /// 关闭所有连接器实例
  Future<ConnectorApiResponse> shutdownAllConnectors() async {
    try {
      final responseData =
          await _ipcApi.post('/connector-lifecycle/shutdown-all');
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

      // IPC可能返回扁平格式或嵌套格式的数据，自动检测并适配
      Map<String, dynamic> data;
      if (responseData.containsKey('data') && responseData['data'] is Map) {
        // 嵌套格式：数据在data字段中（这是实际情况）
        data = (responseData['data'] as Map<String, dynamic>?) ?? {};
      } else if (responseData.containsKey('connectors')) {
        // 扁平格式：直接包含业务数据
        data = responseData;
      } else {
        // 兜底：直接使用响应数据
        data = responseData;
      }

      // 检查响应是否成功
      final success = data['success'] ?? false;

      if (!success) {
        final error = data['error'] ?? 'Unknown error';
        throw ConnectorApiException('Scan failed: $error');
      }

      final flatResponse = {
        'success': success,
        'message': data['message'] ?? 'Directory scanned successfully',
        'connectors': data['connectors'] ?? [],
      };

      return DiscoveryResponse.fromJson(flatResponse);
    } on ConnectorApiException {
      rethrow;
    } catch (e) {
      if (e.toString().contains('type ')) {
        throw ConnectorApiException('数据格式错误: 请确保连接器配置文件格式正确');
      }
      throw ConnectorApiException('扫描目录失败: $e');
    }
  }

  /// 统一的连接器安装接口
  Future<OperationResponse> installConnector(
      InstallConnectorRequest request) async {
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
      // 移除 auto_start 字段，因为数据库模型已经简化了逻辑
      // if (request.autoStart) {
      //   data['auto_start'] = request.autoStart;
      // }
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
      throw ConnectorApiException(
          'Failed to install connector ${request.connectorId}: $e');
    }
  }

  /// 简化版本 - 从registry安装连接器
  Future<OperationResponse> installFromRegistry(String connectorId) async {
    return installConnector(InstallConnectorRequest(
      connectorId: connectorId,
      source: 'registry',
    ));
  }

  /// 切换连接器启用状态
  Future<OperationResponse> toggleConnectorEnabled(
      String connectorId, bool enabled) async {
    try {
      final responseData = await _ipcApi.put(
        '/connector-lifecycle/connectors/$connectorId/enabled',
        data: {'enabled': enabled},
      );

      // 处理嵌套响应结构
      final success = responseData['success'] ?? false;
      final data = responseData['data'] as Map<String, dynamic>? ?? {};
      final error = responseData['error'];

      if (!success || error != null) {
        String errorMessage;
        if (error is Map<String, dynamic>) {
          errorMessage = error['message'] ?? 'Unknown error';
        } else if (error is String) {
          errorMessage = error;
        } else {
          errorMessage = 'Unknown error';
        }

        throw ConnectorApiException(
            'Failed to toggle connector enabled: $errorMessage');
      }

      return OperationResponse(
        success: data['success'] ?? success,
        message:
            data['message'] ?? 'Connector enabled status updated successfully',
        connectorId: data['connector_id'] ?? connectorId,
        state: ConnectorState.values.firstWhere(
          (e) => e.name == (data['state'] ?? 'stopped'),
          orElse: () => ConnectorState.stopped,
        ),
      );
    } catch (e) {
      throw ConnectorApiException(
          'Failed to toggle connector enabled $connectorId: $e');
    }
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
