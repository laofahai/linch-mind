import 'ipc_client.dart';

/// IPC API适配器，提供HTTP风格的接口
/// 将原有的HTTP API调用转换为IPC调用
class IPCApiAdapter {
  final IPCClient _ipcClient = IPCService.instance;
  bool _isInitialized = false;

  /// 确保IPC连接已建立
  Future<void> _ensureInitialized() async {
    if (_isInitialized) return;
    
    final connected = await _ipcClient.connect();
    if (!connected) {
      throw Exception('无法连接到daemon IPC服务');
    }
    
    _isInitialized = true;
  }

  /// 清理资源
  void dispose() {
    _ipcClient.disconnect();
    _isInitialized = false;
  }

  /// GET请求
  Future<Map<String, dynamic>> get(String path, {Map<String, dynamic>? queryParameters}) async {
    await _ensureInitialized();
    
    final response = await _ipcClient.get(path, queryParams: queryParameters);
    
    if (response.statusCode >= 400) {
      throw IPCApiException('GET $path 失败: ${response.data}');
    }
    
    return response.data;
  }

  /// POST请求
  Future<Map<String, dynamic>> post(String path, {Map<String, dynamic>? data, Map<String, dynamic>? queryParameters}) async {
    await _ensureInitialized();
    
    final message = IPCMessage(
      method: 'POST',
      path: path,
      data: data ?? {},
      queryParams: queryParameters ?? {},
    );
    
    final response = await _ipcClient.sendRequest(message);
    
    if (response.statusCode >= 400) {
      throw IPCApiException('POST $path 失败: ${response.data}');
    }
    
    return response.data;
  }

  /// PUT请求
  Future<Map<String, dynamic>> put(String path, {Map<String, dynamic>? data}) async {
    await _ensureInitialized();
    
    final response = await _ipcClient.put(path, data: data);
    
    if (response.statusCode >= 400) {
      throw IPCApiException('PUT $path 失败: ${response.data}');
    }
    
    return response.data;
  }

  /// DELETE请求
  Future<Map<String, dynamic>> delete(String path, {Map<String, dynamic>? queryParameters}) async {
    await _ensureInitialized();
    
    final message = IPCMessage(
      method: 'DELETE',
      path: path,
      queryParams: queryParameters ?? {},
    );
    
    final response = await _ipcClient.sendRequest(message);
    
    if (response.statusCode >= 400) {
      throw IPCApiException('DELETE $path 失败: ${response.data}');
    }
    
    return response.data;
  }
}

/// IPC API异常
class IPCApiException implements Exception {
  final String message;

  IPCApiException(this.message);

  @override
  String toString() => 'IPCApiException: $message';
}

/// 全局IPC API适配器单例
class IPCApiService {
  static IPCApiAdapter? _instance;

  static IPCApiAdapter get instance {
    return _instance ??= IPCApiAdapter();
  }

  static void dispose() {
    _instance?.dispose();
    _instance = null;
  }
}