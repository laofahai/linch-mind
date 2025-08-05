import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/connector_lifecycle_models.dart';
import 'daemon_port_service.dart';

/// Registry API客户端 - 连接器市场数据获取
class RegistryApiClient {
  static final DaemonPortService _portService = DaemonPortService.instance;

  static Future<String> get baseUrl async {
    return await _portService.getDaemonBaseUrl();
  }

  /// 获取市场连接器列表
  static Future<List<ConnectorDefinition>> getMarketConnectors({
    String? query,
    String? category,
  }) async {
    try {
      // 构建查询参数
      final queryParams = <String, String>{};
      if (query != null && query.isNotEmpty) {
        queryParams['query'] = query;
      }
      if (category != null && category != 'all') {
        queryParams['category'] = category;
      }

      // 构建URL
      final daemonBaseUrl = await baseUrl;
      final uri = Uri.parse('$daemonBaseUrl/api/system/config/registry/connectors')
          .replace(
              queryParameters: queryParams.isNotEmpty ? queryParams : null);

      final response = await http.get(
        uri,
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data
            .map((item) => ConnectorDefinition.fromJson(item))
            .toList();
      } else {
        throw Exception('获取市场连接器失败: HTTP ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('获取市场连接器失败: $e');
    }
  }

  /// 获取连接器下载信息
  static Future<Map<String, dynamic>?> getConnectorDownloadInfo(
    String connectorId, {
    String platform = 'macos-x64', // 默认当前平台
  }) async {
    try {
      final daemonBaseUrl = await baseUrl;
      final response = await http.get(
        Uri.parse(
            '$daemonBaseUrl/api/system/config/registry/connectors/$connectorId/download?platform=$platform'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else if (response.statusCode == 404) {
        return null; // 连接器不存在
      } else {
        throw Exception('获取下载信息失败: HTTP ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('获取下载信息失败: $e');
    }
  }

  /// 刷新注册表
  static Future<Map<String, dynamic>> refreshRegistry() async {
    try {
      final daemonBaseUrl = await baseUrl;
      final response = await http.post(
        Uri.parse('$daemonBaseUrl/api/system/config/registry/refresh'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('刷新注册表失败: HTTP ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('刷新注册表失败: $e');
    }
  }

  /// 获取注册表状态
  static Future<Map<String, dynamic>> getRegistryStatus() async {
    try {
      final daemonBaseUrl = await baseUrl;
      final response = await http.get(
        Uri.parse('$daemonBaseUrl/api/system/config/registry'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('获取注册表状态失败: HTTP ${response.statusCode}');
      }
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
