import 'dart:io';
import '../models/connector_lifecycle_models.dart';
import 'ipc_api_adapter.dart';

/// Registry API客户端 - 连接器市场数据获取
class RegistryApiClient {
  static final IPCApiAdapter _ipcApi = IPCApiService.instance;

  /// 自动检测当前平台
  static String _detectPlatform() {
    if (Platform.isWindows) {
      return 'windows-x64';
    } else if (Platform.isMacOS) {
      return 'macos-x64';
    } else if (Platform.isLinux) {
      return 'linux-x64';
    } else {
      return 'unknown';
    }
  }

  /// 获取市场连接器列表
  static Future<List<ConnectorDefinition>> getMarketConnectors({
    String? query,
    String? category,
  }) async {
    try {
      // 构建查询参数
      final queryParams = <String, dynamic>{};
      if (query != null && query.isNotEmpty) {
        queryParams['query'] = query;
      }
      if (category != null && category != 'all') {
        queryParams['category'] = category;
      }

      final responseData = await _ipcApi.get(
        '/system-config/registry/connectors',
        queryParameters: queryParams.isNotEmpty ? queryParams : null,
      );

      if (responseData['data'] != null) {
        final List<dynamic> data = responseData['data'] as List;
        return data.map((item) => ConnectorDefinition.fromJson(item)).toList();
      } else {
        return [];
      }
    } catch (e) {
      throw Exception('获取市场连接器失败: $e');
    }
  }

  /// 获取连接器下载信息
  static Future<Map<String, dynamic>?> getConnectorDownloadInfo(
    String connectorId, {
    String? platform, // 自动检测平台
  }) async {
    try {
      // 自动检测平台
      final detectedPlatform = platform ?? _detectPlatform();

      final responseData = await _ipcApi.get(
        '/system-config/registry/connectors/$connectorId/download',
        queryParameters: {'platform': detectedPlatform},
      );

      if (responseData['success'] == true) {
        return responseData['data'] as Map<String, dynamic>?;
      } else {
        return null; // 连接器不存在或其他错误
      }
    } catch (e) {
      throw Exception('获取下载信息失败: $e');
    }
  }

  /// 刷新注册表
  static Future<Map<String, dynamic>> refreshRegistry() async {
    try {
      final responseData = await _ipcApi.post('/system-config/registry/refresh');
      return responseData;
    } catch (e) {
      throw Exception('刷新注册表失败: $e');
    }
  }

  /// 获取注册表状态
  static Future<Map<String, dynamic>> getRegistryStatus() async {
    try {
      final responseData = await _ipcApi.get('/system-config/registry');
      return responseData;
    } catch (e) {
      throw Exception('获取注册表状态失败: $e');
    }
  }
}

/// 扩展ConnectorDefinition以支持从Registry JSON创建
extension ConnectorDefinitionRegistry on ConnectorDefinition {
  static ConnectorDefinition fromRegistryJson(Map<String, dynamic> json) {
    return ConnectorDefinition(
      connectorId: json['connector_id'] ?? '',
      name: json['name'] ?? json['connector_id'] ?? '',
      displayName:
          json['display_name'] ?? json['name'] ?? json['connector_id'] ?? '',
      description: json['description'] ?? '',
      version: json['version'] ?? '1.0.0',
      author: json['author'] ?? 'Unknown',
      category: json['category'] ?? 'other',
      isRegistered: true,
      path: null, // Registry中的连接器没有本地路径
      downloadUrl: json['download_url'],
      platforms: json['platforms'] ?? {},
      capabilities: json['capabilities'] ?? {},
      permissions:
          (json['permissions'] as List<dynamic>?)?.cast<String>() ?? [],
    );
  }
}
