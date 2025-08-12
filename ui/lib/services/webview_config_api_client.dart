import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/api_response.dart';
import 'ipc_api_adapter.dart';

/// WebView配置API客户端
class WebViewConfigApiClient {
  final IPCApiAdapter _ipcApi = IPCApiService.instance;

  WebViewConfigApiClient();

  /// 检查连接器是否支持WebView配置
  Future<APIResponse> checkWebViewSupport(String connectorId) async {
    try {
      final responseData = await _ipcApi.get(
        '/webview-config/check-support/$connectorId',
      );

      return APIResponse.fromJson(responseData);
    } catch (e) {
      return APIResponse(
        success: false,
        message: '检查WebView支持失败: $e',
        data: null,
      );
    }
  }

  /// 获取连接器WebView配置HTML URL
  /// 注意：IPC模式下此方法不直接提供URL，请使用getWebViewConfigHtml
  String getWebViewConfigUrl(String connectorId, {String? templateName}) {
    // IPC模式下无直接URL，返回占位符
    return 'ipc://webview-config/html/$connectorId${templateName != null ? '?template_name=$templateName' : ''}';
  }

  /// 获取连接器WebView配置HTML内容
  Future<String> getWebViewConfigHtml(String connectorId,
      {String? templateName}) async {
    try {
      final queryParams = templateName != null
          ? {'template_name': templateName}
          : <String, dynamic>{};
      final responseData = await _ipcApi.get(
        '/webview-config/html/$connectorId',
        queryParameters: queryParams,
      );

      // IPC返回的是JSON格式，提取HTML内容
      if (responseData case Map data when data['html'] != null) {
        return data['html'] as String;
      } else {
        return responseData.toString();
      }
    } catch (e) {
      throw Exception('获取WebView配置HTML失败: $e');
    }
  }

  /// 获取预览HTML内容
  Future<String> getPreviewHtml(String connectorId,
      {String? templateName}) async {
    try {
      final queryParams = templateName != null
          ? {'template_name': templateName}
          : <String, dynamic>{};
      final responseData = await _ipcApi.get(
        '/webview-config/preview/$connectorId',
        queryParameters: queryParams,
      );

      // IPC返回的是JSON格式，提取HTML内容
      if (responseData case Map data when data['html'] != null) {
        return data['html'] as String;
      } else {
        return responseData.toString();
      }
    } catch (e) {
      throw Exception('获取预览HTML失败: $e');
    }
  }

  /// 获取可用模板列表
  Future<APIResponse> getAvailableTemplates() async {
    try {
      final responseData = await _ipcApi.get(
        '/webview-config/templates',
      );

      return APIResponse.fromJson(responseData);
    } catch (e) {
      return APIResponse(
        success: false,
        message: '获取模板列表失败: $e',
        data: null,
      );
    }
  }

  /// 保存自定义模板
  Future<APIResponse> saveCustomTemplate(
    String templateName,
    String templateContent, {
    String? connectorId,
  }) async {
    try {
      final responseData = await _ipcApi.post(
        '/webview-config/templates/$templateName',
        data: {
          'content': templateContent,
          if (connectorId != null) 'connector_id': connectorId,
        },
      );

      return APIResponse.fromJson(responseData);
    } catch (e) {
      return APIResponse(
        success: false,
        message: '保存模板失败: $e',
        data: null,
      );
    }
  }

  /// 验证模板内容
  Future<APIResponse> validateTemplate(String templateContent) async {
    try {
      final responseData = await _ipcApi.post(
        '/webview-config/validate-template',
        data: {
          'content': templateContent,
        },
      );

      return APIResponse.fromJson(responseData);
    } catch (e) {
      return APIResponse(
        success: false,
        message: '验证模板失败: $e',
        data: null,
      );
    }
  }

  /// 清理资源
  void dispose() {
    // IPC适配器由IPCApiService统一管理
  }
}

/// WebView配置API客户端提供者
final webViewConfigApiClientProvider = Provider<WebViewConfigApiClient>((ref) {
  return WebViewConfigApiClient();
});

/// WebView支持检查提供者
final webViewSupportProvider =
    FutureProvider.family<bool, String>((ref, connectorId) async {
  final client = ref.read(webViewConfigApiClientProvider);
  final response = await client.checkWebViewSupport(connectorId);

  if (response.success && response.data != null) {
    final data = response.data as Map<String, dynamic>;
    return data['supports_webview'] as bool? ?? false;
  }

  return false;
});

/// 可用模板列表提供者
final availableTemplatesProvider =
    FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final client = ref.read(webViewConfigApiClientProvider);
  final response = await client.getAvailableTemplates();

  if (response.success && response.data != null) {
    return List<Map<String, dynamic>>.from(response.data as List);
  }

  return [];
});
