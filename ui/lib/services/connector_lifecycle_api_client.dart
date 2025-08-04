import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import 'dart:async';
import 'dart:io';
import '../models/connector_lifecycle_models.dart';
import 'daemon_port_service.dart';

/// 专门的连接器生命周期API客户端
/// 对应 daemon 的 /connector-lifecycle 端点
class ConnectorLifecycleApiClient {
  Dio? _dio;
  bool _isInitialized = false;

  ConnectorLifecycleApiClient();

  /// 清理资源
  void dispose() {
    _dio?.close();
    _dio = null;
    _isInitialized = false;
  }

  /// 异步初始化客户端（读取动态端口）
  Future<void> _ensureInitialized() async {
    if (_isInitialized && _dio != null) return;
    
    final baseUrl = await DaemonPortService.instance.getDaemonBaseUrl();
    
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
      },
    ));
    
    // 禁用代理 - 直连本地服务
    (_dio!.httpClientAdapter as IOHttpClientAdapter).createHttpClient = () {
      final client = HttpClient();
      client.findProxy = (uri) => 'DIRECT';
      return client;
    };

    // 添加拦截器用于日志和错误处理
    _dio!.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
      error: true,
      logPrint: (obj) => print('[ConnectorLifecycleAPI] $obj'),
    ));

    _dio!.interceptors.add(InterceptorsWrapper(
      onError: (error, handler) {
        print('[ConnectorLifecycleAPI] Error: ${error.message}');
        if (error.response?.data != null) {
          print('[ConnectorLifecycleAPI] Error response: ${error.response?.data}');
        }
        
        // 包装API错误为更友好的消息
        String friendlyMessage = _getFriendlyErrorMessage(error);
        DioException wrappedError = DioException(
          requestOptions: error.requestOptions,
          response: error.response,
          type: error.type,
          error: friendlyMessage,
          message: friendlyMessage,
        );
        
        handler.next(wrappedError);
      },
    ));
    
    _isInitialized = true;
  }

  /// 获取已初始化的Dio实例
  Dio get dio {
    if (_dio == null) {
      throw Exception('ConnectorLifecycleApiClient not initialized. Call _ensureInitialized() first.');
    }
    return _dio!;
  }

  /// 获取友好的错误消息
  String _getFriendlyErrorMessage(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return '连接超时，请检查网络连接或重试';
      case DioExceptionType.connectionError:
        return 'daemon服务未启动或无法连接，请启动后端服务';
      case DioExceptionType.badResponse:
        if (error.response?.statusCode == 404) {
          return '请求的资源不存在';
        } else if (error.response?.statusCode == 500) {
          return '服务器内部错误，请查看daemon日志';
        } else if (error.response?.statusCode == 409) {
          return '资源冲突，可能已存在相同名称的连接器';
        }
        return '服务器返回错误: ${error.response?.statusCode}';
      case DioExceptionType.cancel:
        return '请求已取消';
      case DioExceptionType.unknown:
      default:
        return error.message ?? '未知错误';
    }
  }

  /// 发现可用的连接器
  Future<DiscoveryResponse> discoverConnectors() async {
    await _ensureInitialized();
    try {
      final response = await dio.get('/connector-lifecycle/discovery');
      
      // 转换嵌套的data结构为平铺结构
      final responseData = response.data as Map<String, dynamic>;
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
  Future<OperationResponse> createConnector(CreateConnectorRequest request) async {
    await _ensureInitialized();
    try {
      final response = await dio.post(
        '/connector-lifecycle/collectors',
        data: {
          'connector_id': request.connectorId,
          'display_name': request.displayName,
          'config': request.config,
          'auto_start': request.autoStart,
          if (request.templateId != null) 'template_id': request.templateId,
        },
      );
      return OperationResponse.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to create connector: $e');
    }
  }

  /// 获取连接器列表
  Future<ConnectorListResponse> getConnectors({
    String? connectorId,
    String? state,
  }) async {
    await _ensureInitialized();
    try {
      final queryParams = <String, dynamic>{};
      if (connectorId != null) queryParams['connector_id'] = connectorId;
      if (state != null) queryParams['state'] = state;
      
      final response = await dio.get(
        '/connector-lifecycle/collectors',
        queryParameters: queryParams,
      );
      
      // 转换嵌套的data结构为平铺结构
      final responseData = response.data as Map<String, dynamic>;
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
  Future<ConnectorDetailResponse> getConnector(String collectorId) async {
    await _ensureInitialized();
    try {
      final response = await dio.get('/connector-lifecycle/collectors/$collectorId');
      return ConnectorDetailResponse.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to get connector $collectorId: $e');
    }
  }

  /// 启动连接器
  Future<OperationResponse> startConnector(String collectorId) async {
    await _ensureInitialized();
    try {
      final response = await dio.post('/connector-lifecycle/collectors/$collectorId/start');
      return OperationResponse.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to start connector $collectorId: $e');
    }
  }

  /// 停止连接器
  Future<OperationResponse> stopConnector(String collectorId, {bool force = false}) async {
    await _ensureInitialized();
    try {
      final queryParams = force ? {'force': 'true'} : <String, String>{};
      final response = await dio.post(
        '/connector-lifecycle/collectors/$collectorId/stop',
        queryParameters: queryParams,
      );
      return OperationResponse.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to stop connector $collectorId: $e');
    }
  }

  /// 重启连接器
  Future<OperationResponse> restartConnector(String collectorId) async {
    await _ensureInitialized();
    try {
      final response = await dio.post('/connector-lifecycle/collectors/$collectorId/restart');
      return OperationResponse.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to restart connector $collectorId: $e');
    }
  }

  /// 更新连接器配置
  Future<OperationResponse> updateConnectorConfig(String collectorId, UpdateConfigRequest request) async {
    try {
      final response = await dio.put(
        '/connector-lifecycle/collectors/$collectorId/config',
        data: {'config': request.config},
      );
      return OperationResponse.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to update connector config $collectorId: $e');
    }
  }

  /// 删除连接器
  Future<OperationResponse> deleteConnector(String collectorId, {bool force = false}) async {
    try {
      final queryParams = force ? {'force': 'true'} : <String, String>{};
      final response = await dio.delete(
        '/connector-lifecycle/collectors/$collectorId',
        queryParameters: queryParams,
      );
      return OperationResponse.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to delete connector $collectorId: $e');
    }
  }

  /// 获取所有连接器状态概览
  Future<ConnectorStatesOverview> getStatesOverview() async {
    try {
      final response = await dio.get('/connector-lifecycle/states');
      return ConnectorStatesOverview.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to get states overview: $e');
    }
  }

  /// 系统健康检查
  Future<ConnectorHealthResponse> getHealthCheck() async {
    await _ensureInitialized();
    try {
      final response = await dio.get('/connector-lifecycle/health');
      return ConnectorHealthResponse.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to get health check: $e');
    }
  }

  /// 关闭所有连接器实例
  Future<ConnectorApiResponse> shutdownAllConnectors() async {
    try {
      final response = await dio.post('/connector-lifecycle/shutdown-all');
      return ConnectorApiResponse.fromJson(response.data);
    } catch (e) {
      throw ConnectorApiException('Failed to shutdown all connectors: $e');
    }
  }

  /// 扫描指定目录寻找连接器
  Future<DiscoveryResponse> scanConnectorDirectory(String directoryPath) async {
    try {
      final response = await dio.post(
        '/connector-lifecycle/scan-directory',
        data: {'directory_path': directoryPath},
      );
      
      // 转换嵌套的data结构为平铺结构
      final responseData = response.data as Map<String, dynamic>;
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

  /// 监听连接器事件流 (Server-Sent Events) - 简化版本
  /// TODO: 完整的SSE实现
  Stream<ConnectorEvent> watchConnectorEvents() async* {
    // 暂时返回空流，避免编译错误
    // 实际实现需要处理SSE格式
    yield* Stream<ConnectorEvent>.empty();
  }

  /// 关闭客户端连接 - 已在第17行定义，删除重复声明
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