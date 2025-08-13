import 'ipc_client.dart';
import '../core/ui_service_facade.dart';
import '../models/ipc_protocol.dart';
import '../utils/enhanced_error_handler.dart';
import 'response_parser.dart';

/// IPC API适配器，提供HTTP风格的接口
/// 将原有的HTTP API调用转换为IPC调用
class IPCApiAdapter {
  /// 创建标准化响应格式
  Map<String, dynamic> _createStandardResponse(IPCResponse response) {
    if (response.success) {
      return ResponseParser.createSuccessResponse(
        data: ResponseParser.adaptResponseData(response.data),
      );
    } else {
      return ResponseParser.createErrorResponse(
        error: response.error?.message ?? 'Unknown error',
        data: {
          'code': response.error?.code.toString() ?? 'unknown',
        },
      );
    }
  }

  final IPCClient _ipcClient = getService<IPCClient>();
  final _errorHandler = getService<EnhancedErrorHandler>();
  bool _isInitialized = false;

  /// 确保IPC连接已建立
  Future<void> _ensureInitialized() async {
    if (_isInitialized) return;

    final connected = await _ipcClient.connect();
    
    if (!connected) {
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
  Future<Map<String, dynamic>> get(String path,
      {Map<String, dynamic>? queryParameters}) async {
    return await _errorHandler.safeAsync(
          () async {
            await _ensureInitialized();
            final request = IPCRequest.get(path: path, queryParams: queryParameters);
            final response = await _ipcClient.sendRequest(request);

            // 处理IPC错误
            if (!response.success && response.error != null) {
              _errorHandler.handleIPCError(
                response.error!.toJson(),
                operation: 'GET $path',
              );
            }

            return _createStandardResponse(response);
          },
          context: 'IPC GET $path',
          fallback: ResponseParser.createErrorResponse(
            error: 'Connection failed',
            data: {'path': path, 'operation': 'GET'},
          ),
        ) ??
        ResponseParser.createErrorResponse(
          error: 'Request failed',
          data: {'path': path, 'operation': 'GET'},
        );
  }

  /// POST请求
  Future<Map<String, dynamic>> post(String path,
      {Map<String, dynamic>? data,
      Map<String, dynamic>? queryParameters}) async {
    return await _errorHandler.safeAsync(
          () async {
            await _ensureInitialized();
            final request = IPCRequest.post(path: path, data: data);
            final response = await _ipcClient.sendRequest(request);

            // 处理IPC错误
            if (!response.success && response.error != null) {
              _errorHandler.handleIPCError(
                response.error!.toJson(),
                operation: 'POST $path',
              );
            }

            return _createStandardResponse(response);
          },
          context: 'IPC POST $path',
          fallback: ResponseParser.createErrorResponse(
            error: 'Connection failed',
            data: {'path': path, 'operation': 'POST'},
          ),
        ) ??
        ResponseParser.createErrorResponse(
          error: 'Request failed',
          data: {'path': path, 'operation': 'POST'},
        );
  }

  /// PUT请求
  Future<Map<String, dynamic>> put(String path,
      {Map<String, dynamic>? data}) async {
    return await _errorHandler.safeAsync(
          () async {
            await _ensureInitialized();
            final request = IPCRequest.put(path: path, data: data);
            final response = await _ipcClient.sendRequest(request);

            // 处理IPC错误
            if (!response.success && response.error != null) {
              _errorHandler.handleIPCError(
                response.error!.toJson(),
                operation: 'PUT $path',
              );
            }

            return _createStandardResponse(response);
          },
          context: 'IPC PUT $path',
          fallback: ResponseParser.createErrorResponse(
            error: 'Connection failed',
            data: {'path': path, 'operation': 'PUT'},
          ),
        ) ??
        ResponseParser.createErrorResponse(
          error: 'Request failed',
          data: {'path': path, 'operation': 'PUT'},
        );
  }

  /// DELETE请求
  Future<Map<String, dynamic>> delete(String path,
      {Map<String, dynamic>? queryParameters}) async {
    return await _errorHandler.safeAsync(
          () async {
            await _ensureInitialized();
            final request = IPCRequest.delete(path: path, queryParams: queryParameters);
            final response = await _ipcClient.sendRequest(request);

            // 处理IPC错误
            if (!response.success && response.error != null) {
              _errorHandler.handleIPCError(
                response.error!.toJson(),
                operation: 'DELETE $path',
              );
            }

            return _createStandardResponse(response);
          },
          context: 'IPC DELETE $path',
          fallback: ResponseParser.createErrorResponse(
            error: 'Connection failed',
            data: {'path': path, 'operation': 'DELETE'},
          ),
        ) ??
        ResponseParser.createErrorResponse(
          error: 'Request failed',
          data: {'path': path, 'operation': 'DELETE'},
        );
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
