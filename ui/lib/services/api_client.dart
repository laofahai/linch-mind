import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import '../models/api_models.dart';

/// 通用API客户端 - 处理非连接器相关的API
/// 连接器管理API已迁移到 ConnectorLifecycleApiClient
class ApiClient {
  static const String baseUrl = 'http://127.0.0.1:50001';
  
  late final Dio _dio;

  ApiClient() {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 10),
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
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onError: (error, handler) {
        print('API Error: ${error.message}');
        handler.next(error);
      },
    ));
  }

  // 服务器信息
  Future<ServerInfo> getServerInfo() async {
    try {
      final response = await _dio.get('/');
      return ServerInfo.fromJson(response.data);
    } catch (e) {
      throw ApiException('Failed to get server info: $e');
    }
  }

  // 数据管理
  Future<List<DataItem>> getData({int? limit, String? connectorId}) async {
    try {
      final queryParams = <String, dynamic>{};
      if (limit != null) queryParams['limit'] = limit;
      if (connectorId != null) queryParams['connector_id'] = connectorId;

      final response = await _dio.get('/data', queryParameters: queryParams);
      if (response.data is List) {
        return (response.data as List)
            .map((json) => DataItem.fromJson(json))
            .toList();
      }
      return [];
    } catch (e) {
      throw ApiException('Failed to get data: $e');
    }
  }

  Future<DataItem> getDataItem(String itemId) async {
    try {
      final response = await _dio.get('/data/$itemId');
      return DataItem.fromJson(response.data);
    } catch (e) {
      throw ApiException('Failed to get data item $itemId: $e');
    }
  }

  // AI 推荐
  Future<List<AIRecommendation>> getRecommendations({int? limit}) async {
    try {
      final queryParams = <String, dynamic>{};
      if (limit != null) queryParams['limit'] = limit;

      final response = await _dio.get('/recommendations', queryParameters: queryParams);
      if (response.data is List) {
        return (response.data as List)
            .map((json) => AIRecommendation.fromJson(json))
            .toList();
      }
      return [];
    } catch (e) {
      throw ApiException('Failed to get recommendations: $e');
    }
  }

  // 图数据
  Future<List<GraphNode>> getGraphNodes({int? limit}) async {
    try {
      final queryParams = <String, dynamic>{};
      if (limit != null) queryParams['limit'] = limit;

      final response = await _dio.get('/graph/nodes', queryParameters: queryParams);
      if (response.data is List) {
        return (response.data as List)
            .map((json) => GraphNode.fromJson(json))
            .toList();
      }
      return [];
    } catch (e) {
      throw ApiException('Failed to get graph nodes: $e');
    }
  }

  Future<List<GraphEdge>> getGraphEdges({String? nodeId, int? limit}) async {
    try {
      final queryParams = <String, dynamic>{};
      if (nodeId != null) queryParams['node_id'] = nodeId;
      if (limit != null) queryParams['limit'] = limit;

      final response = await _dio.get('/graph/edges', queryParameters: queryParams);
      if (response.data is List) {
        return (response.data as List)
            .map((json) => GraphEdge.fromJson(json))
            .toList();
      }
      return [];
    } catch (e) {
      throw ApiException('Failed to get graph edges: $e');
    }
  }

  // 数据库统计
  Future<DatabaseStats> getDatabaseStats() async {
    try {
      final response = await _dio.get('/data/stats');
      return DatabaseStats.fromJson(response.data);
    } catch (e) {
      throw ApiException('Failed to get database stats: $e');
    }
  }

  // 图统计
  Future<Map<String, dynamic>> getGraphStats() async {
    try {
      final response = await _dio.get('/graph/stats');
      return response.data as Map<String, dynamic>;
    } catch (e) {
      throw ApiException('Failed to get graph stats: $e');
    }
  }

  // 健康检查
  Future<bool> healthCheck() async {
    try {
      final response = await _dio.get('/health');
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  // 系统诊断
  Future<SystemDiagnostics> getSystemDiagnostics() async {
    try {
      final response = await _dio.get('/diagnostics');
      return SystemDiagnostics.fromJson(response.data);
    } catch (e) {
      throw ApiException('Failed to get system diagnostics: $e');
    }
  }
}

class ApiException implements Exception {
  final String message;
  
  ApiException(this.message);
  
  @override
  String toString() => 'ApiException: $message';
}