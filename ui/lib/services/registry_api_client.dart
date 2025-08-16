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
      print('[DEBUG] 开始获取市场连接器列表...');

      // 构建查询参数
      final queryParams = <String, dynamic>{};
      if (query != null && query.isNotEmpty) {
        queryParams['query'] = query;
      }
      if (category != null && category != 'all') {
        queryParams['category'] = category;
      }

      print('[DEBUG] 查询参数: $queryParams');

      // 添加超时处理，防止UI卡死
      final responseData = await _ipcApi
          .get(
        '/system-config/registry/connectors',
        queryParameters: queryParams.isNotEmpty ? queryParams : null,
      )
          .timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('获取市场连接器超时（10秒）');
        },
      );

      print('[DEBUG] API响应: ${responseData.keys}');

      if (responseData['data'] != null) {
        final dynamic dataField = responseData['data'];

        // 处理不同的数据结构
        List<dynamic> data;
        if (dataField is List) {
          data = dataField;
        } else if (dataField is Map<String, dynamic>) {
          // 如果返回的是Map，可能包含connectors字段
          if (dataField.containsKey('connectors')) {
            final connectorsField = dataField['connectors'];
            if (connectorsField is List) {
              data = connectorsField;
            } else {
              print(
                  '[WARNING] connectors字段不是List类型: ${connectorsField.runtimeType}');
              return [];
            }
          } else {
            print('[WARNING] Map数据中未找到connectors字段: ${dataField.keys}');
            return [];
          }
        } else {
          print('[WARNING] 意外的数据类型: ${dataField.runtimeType}');
          return [];
        }

        return data
            .map((item) {
              // 安全地处理可能为null的item
              if (item == null) {
                print('[DEBUG] 跳过null连接器项');
                return null;
              }

              try {
                // 首先尝试使用标准fromJson
                if (item is Map<String, dynamic>) {
                  print(
                      '[DEBUG] 解析连接器: ${item['connector_id'] ?? item['name'] ?? 'unknown'}');
                  return ConnectorDefinition.fromJson(item);
                } else {
                  print('[WARNING] 跳过非Map类型的连接器项: ${item.runtimeType} - $item');
                  return null;
                }
              } catch (e) {
                print('[WARNING] 标准fromJson失败: $e, 尝试Registry解析');
                // 如果标准fromJson失败，尝试使用Registry专用的解析
                try {
                  if (item is Map<String, dynamic>) {
                    return ConnectorDefinitionRegistry.fromRegistryJson(item);
                  } else {
                    print(
                        '[ERROR] Registry解析失败：item不是Map类型: ${item.runtimeType}');
                    return null;
                  }
                } catch (e2) {
                  print('[ERROR] Registry解析连接器定义失败: $e2');
                  print('[ERROR] 原始数据: $item');
                  print('[ERROR] 数据类型: ${item.runtimeType}');
                  return null;
                }
              }
            })
            .where((item) => item != null)
            .cast<ConnectorDefinition>()
            .toList();
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
      final responseData =
          await _ipcApi.post('/system-config/registry/refresh');
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
      isRegistered: json['is_registered'] ?? false, // 从后端数据获取实际状态
      path: null, // Registry中的连接器没有本地路径
      downloadUrl: json['download_url'],
      platforms: json['platforms'] ?? {},
      capabilities: json['capabilities'] ?? {},
      permissions:
          (json['permissions'] as List<dynamic>?)?.cast<String>() ?? [],
    );
  }
}
