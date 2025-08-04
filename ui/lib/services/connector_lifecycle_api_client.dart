import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import 'dart:async';
import '../models/connector_lifecycle_models.dart';

/// 专门的连接器生命周期API客户端
/// 对应 daemon 的 /connector-lifecycle 端点
class ConnectorLifecycleApiClient {
  static const String baseUrl = 'http://127.0.0.1:58471';
  
  late final Dio _dio;

  ConnectorLifecycleApiClient() {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
      },
    ));
    
    // 禁用代理 - 直连本地服务
    (_dio.httpClientAdapter as DefaultHttpClientAdapter).onHttpClientCreate = (client) {
      client.findProxy = (uri) => 'DIRECT';
      return client;
    };

    // 添加拦截器用于日志和错误处理
    _dio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
      error: true,
      logPrint: (obj) => print('[ConnectorLifecycleAPI] $obj'),
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onError: (error, handler) {
        print('[ConnectorLifecycleAPI] Error: ${error.message}');
        if (error.response?.data != null) {
          print('[ConnectorLifecycleAPI] Error response: ${error.response?.data}');
        }
        handler.next(error);
      },
    ));
  }

  /// 发现可用的连接器类型
  Future<DiscoveryResponse> discoverConnectorTypes() async {
    try {
      final response = await _dio.get('/connector-lifecycle/discovery');
      return DiscoveryResponse.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to discover connector types: $e');
    }
  }

  /// 创建连接器实例
  Future<OperationResponse> createConnectorInstance(CreateInstanceRequest request) async {
    try {
      final response = await _dio.post(
        '/connector-lifecycle/instances',
        data: {
          'type_id': request.typeId,
          'display_name': request.displayName,
          'config': request.config,
          'auto_start': request.autoStart,
          if (request.templateId != null) 'template_id': request.templateId,
        },
      );
      return OperationResponse.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to create connector instance: $e');
    }
  }

  /// 获取连接器实例列表
  Future<InstanceListResponse> getConnectorInstances({
    String? typeId,
    String? state,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (typeId != null) queryParams['type_id'] = typeId;
      if (state != null) queryParams['state'] = state;
      
      final response = await _dio.get(
        '/connector-lifecycle/instances',
        queryParameters: queryParams,
      );
      return InstanceListResponse.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to get connector instances: $e');
    }
  }

  /// 获取连接器实例详情
  Future<InstanceDetailResponse> getConnectorInstance(String instanceId) async {
    try {
      final response = await _dio.get('/connector-lifecycle/instances/$instanceId');
      return InstanceDetailResponse.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to get connector instance $instanceId: $e');
    }
  }

  /// 启动连接器实例
  Future<OperationResponse> startConnectorInstance(String instanceId) async {
    try {
      final response = await _dio.post('/connector-lifecycle/instances/$instanceId/start');
      return OperationResponse.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to start connector instance $instanceId: $e');
    }
  }

  /// 停止连接器实例
  Future<OperationResponse> stopConnectorInstance(String instanceId, {bool force = false}) async {
    try {
      final queryParams = force ? {'force': 'true'} : <String, String>{};
      final response = await _dio.post(
        '/connector-lifecycle/instances/$instanceId/stop',
        queryParameters: queryParams,
      );
      return OperationResponse.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to stop connector instance $instanceId: $e');
    }
  }

  /// 重启连接器实例
  Future<OperationResponse> restartConnectorInstance(String instanceId) async {
    try {
      final response = await _dio.post('/connector-lifecycle/instances/$instanceId/restart');
      return OperationResponse.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to restart connector instance $instanceId: $e');
    }
  }

  /// 更新连接器实例配置
  Future<OperationResponse> updateConnectorConfig(String instanceId, UpdateConfigRequest request) async {
    try {
      final response = await _dio.put(
        '/connector-lifecycle/instances/$instanceId/config',
        data: {'config': request.config},
      );
      return OperationResponse.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to update connector config $instanceId: $e');
    }
  }

  /// 删除连接器实例
  Future<OperationResponse> deleteConnectorInstance(String instanceId, {bool force = false}) async {
    try {
      final queryParams = force ? {'force': 'true'} : <String, String>{};
      final response = await _dio.delete(
        '/connector-lifecycle/instances/$instanceId',
        queryParameters: queryParams,
      );
      return OperationResponse.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to delete connector instance $instanceId: $e');
    }
  }

  /// 获取所有连接器状态概览
  Future<ConnectorStatesOverview> getStatesOverview() async {
    try {
      final response = await _dio.get('/connector-lifecycle/states');
      return ConnectorStatesOverview.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to get states overview: $e');
    }
  }

  /// 系统健康检查
  Future<ConnectorHealthResponse> getHealthCheck() async {
    try {
      final response = await _dio.get('/connector-lifecycle/health');
      return ConnectorHealthResponse.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to get health check: $e');
    }
  }

  /// 关闭所有连接器实例
  Future<ConnectorApiResponse> shutdownAllConnectors() async {
    try {
      final response = await _dio.post('/connector-lifecycle/shutdown-all');
      return ConnectorApiResponse.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to shutdown all connectors: $e');
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
  void dispose() {
    _dio.close();
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