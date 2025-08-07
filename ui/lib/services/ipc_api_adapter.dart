import 'ipc_client.dart';
import '../models/ipc_protocol.dart';

/// IPC API适配器，提供HTTP风格的接口
/// 将原有的HTTP API调用转换为IPC调用
class IPCApiAdapter {
  
  /// 适配IPC响应数据为Map格式
  Map<String, dynamic> _adaptResponseData(dynamic data) {
    if (data is Map<String, dynamic>) {
      return data;
    } else if (data is List) {
      // 如果是List，包装成Map返回
      return {'data': data};
    } else {
      return data != null ? {'data': data} : {};
    }
  }
  final IPCClient _ipcClient = IPCService.instance;
  bool _isInitialized = false;

  /// 确保IPC连接已建立
  Future<void> _ensureInitialized() async {
    if (_isInitialized) return;
    
    final connected = await _ipcClient.connect();
    print('[DEBUG] IPC连接结果: connected=$connected');
    
    if (!connected) {
      print('[ERROR] IPC连接失败，无法继续');
      throw Exception('无法连接到daemon IPC服务，请确保daemon正在运行');
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
    
    // 返回标准化的响应格式，包含success字段
    return {
      'success': response.success,
      'data': response.success ? _adaptResponseData(response.data) : null,
      'error': response.success ? null : {
        'message': response.error?.message ?? 'Unknown error',
        'code': response.error?.code.toString() ?? 'unknown',
      },
    };
  }

  /// POST请求
  Future<Map<String, dynamic>> post(String path, {Map<String, dynamic>? data, Map<String, dynamic>? queryParameters}) async {
    await _ensureInitialized();
    
    final response = await _ipcClient.post(path, data: data);
    
    // 返回标准化的响应格式，包含success字段
    return {
      'success': response.success,
      'data': response.success ? _adaptResponseData(response.data) : null,
      'error': response.success ? null : {
        'message': response.error?.message ?? 'Unknown error',
        'code': response.error?.code.toString() ?? 'unknown',
      },
    };
  }

  /// PUT请求
  Future<Map<String, dynamic>> put(String path, {Map<String, dynamic>? data}) async {
    await _ensureInitialized();
    
    final response = await _ipcClient.put(path, data: data);
    
    // 返回标准化的响应格式，包含success字段
    return {
      'success': response.success,
      'data': response.success ? _adaptResponseData(response.data) : null,
      'error': response.success ? null : {
        'message': response.error?.message ?? 'Unknown error',
        'code': response.error?.code.toString() ?? 'unknown',
      },
    };
  }

  /// DELETE请求
  Future<Map<String, dynamic>> delete(String path, {Map<String, dynamic>? queryParameters}) async {
    await _ensureInitialized();
    
    final request = IPCRequest(
      method: 'DELETE',
      path: path,
      queryParams: queryParameters ?? {},
    );
    
    final response = await _ipcClient.sendRequest(request);
    
    // 返回标准化的响应格式，包含success字段
    return {
      'success': response.success,
      'data': response.success ? _adaptResponseData(response.data) : null,
      'error': response.success ? null : {
        'message': response.error?.message ?? 'Unknown error',
        'code': response.error?.code.toString() ?? 'unknown',
      },
    };
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