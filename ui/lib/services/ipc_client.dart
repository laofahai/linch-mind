import 'dart:io' as io;
import 'dart:convert';
import 'dart:async';
import 'dart:typed_data';
import 'dart:developer' as developer;
import '../models/ipc_protocol.dart';
import '../utils/app_logger.dart';

/// 纯IPC客户端 - 使用统一的IPC协议
/// 完全摒弃HTTP概念，使用IPC特定的成功/失败响应格式
class IPCClient {
  io.Socket? _socket;
  io.Process? _namedPipeProcess;
  bool _isConnected = false;
  bool _isAuthenticated = false;
  final String? _socketPath;
  final String? _pipeName;
  StreamSubscription? _socketSubscription;
  final Map<String, Completer<IPCResponse>> _pendingRequests = {};
  int _requestCounter = 0;

  IPCClient({String? socketPath, String? pipeName})
      : _socketPath = socketPath,
        _pipeName = pipeName;

  /// 生成唯一请求ID
  String _generateRequestId() {
    return 'req_${DateTime.now().millisecondsSinceEpoch}_${_requestCounter++}';
  }

  /// 连接到daemon
  Future<bool> connect({int maxRetries = 3}) async {
    if (_isConnected && _isAuthenticated) return true;

    for (int attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        AppLogger.ipcDebug('IPC V2连接尝试 $attempt/$maxRetries', data: {'attempt': attempt, 'maxRetries': maxRetries});
        
        bool connected = false;
        if (io.Platform.isWindows) {
          connected = await _connectNamedPipe();
        } else {
          connected = await _connectUnixSocket();
        }
        
        if (connected) {
          AppLogger.ipcDebug('Socket连接成功，开始认证...');
          // 连接成功后进行认证握手
          if (await _performAuthentication(maxRetries: 2)) {
            AppLogger.ipcInfo('认证成功，连接完成', data: {'isConnected': _isConnected, 'isAuthenticated': _isAuthenticated});
            return true;
          } else {
            print('[DEBUG] 认证失败，断开连接准备重试');
            // 认证失败，断开连接准备重试
            await _disconnectWithoutCleanup();
          }
        } else {
          print('[DEBUG] Socket连接失败');
        }
        
        if (attempt < maxRetries) {
          await Future.delayed(Duration(milliseconds: 500 * attempt));
        }
      } catch (e) {
        developer.log('IPC V2连接尝试 $attempt 失败: $e', name: 'IPCClient', level: 1000);
        if (attempt < maxRetries) {
          await Future.delayed(Duration(milliseconds: 500 * attempt));
        }
      }
    }
    
    developer.log('IPC V2连接失败，已尝试 $maxRetries 次', name: 'IPCClient', level: 1000);
    print('[DEBUG] IPC V2连接最终失败，已尝试 $maxRetries 次。_isConnected=$_isConnected, _isAuthenticated=$_isAuthenticated');
    return false;
  }

  /// 连接Unix Domain Socket
  Future<bool> _connectUnixSocket() async {
    String socketPath = _socketPath ?? await _discoverSocketPath();
    
    if (socketPath.isEmpty) {
      developer.log('无法找到socket路径', name: 'IPCClient', level: 1000);
      return false;
    }

    try {
      final address = io.InternetAddress(socketPath, type: io.InternetAddressType.unix);
      _socket = await io.Socket.connect(address, 0);
      
      _setupSocketListener();
      
      _isConnected = true;
      developer.log('已连接到Unix socket: $socketPath', name: 'IPCClient', level: 800);
      print('[DEBUG] IPC V2已连接到Unix socket: $socketPath');
      return true;
    } catch (e) {
      developer.log('Unix socket连接失败: $e', name: 'IPCClient', level: 1000);
      return false;
    }
  }

  /// 连接Windows Named Pipe
  Future<bool> _connectNamedPipe() async {
    String pipeName = _pipeName ?? await _discoverPipeName();
    
    if (pipeName.isEmpty) {
      developer.log('无法找到pipe名称', name: 'IPCClient', level: 1000);
      return false;
    }
    
    try {
      final pipeFile = io.File('\\\\.\\pipe\\$pipeName');
      
      if (await pipeFile.exists()) {
        _isConnected = true;
        developer.log('已连接到Named Pipe: $pipeName', name: 'IPCClient', level: 800);
        return true;
      } else {
        developer.log('Named Pipe不存在: $pipeName', name: 'IPCClient', level: 1000);
        return false;
      }
    } catch (e) {
      developer.log('Named Pipe连接失败: $e', name: 'IPCClient', level: 1000);
      return false;
    }
  }
  
  /// 设置socket监听器 - 解析IPC协议响应
  void _setupSocketListener() {
    if (_socket == null || _socketSubscription != null) return;
    
    final buffer = <int>[];
    bool readingLength = true;
    int expectedLength = 4;
    int responseLength = 0;
    
    _socketSubscription = _socket!.listen(
      (data) {
        buffer.addAll(data);
        
        while (true) {
          if (readingLength && buffer.length >= 4) {
            // 读取响应长度
            final lengthBuffer = Uint8List.fromList(buffer.take(4).toList());
            responseLength = lengthBuffer.buffer.asByteData().getUint32(0, Endian.big);
            expectedLength = responseLength;
            buffer.removeRange(0, 4);
            readingLength = false;
          }
          
          if (!readingLength && buffer.length >= expectedLength) {
            // 读取响应内容
            final responseBytes = Uint8List.fromList(buffer.take(expectedLength).toList());
            final responseJson = utf8.decode(responseBytes);
            buffer.removeRange(0, expectedLength);
            
            // 解析IPC协议响应
            try {
              final jsonData = jsonDecode(responseJson) as Map<String, dynamic>;
              final response = IPCResponse.fromJson(jsonData);
              
              // 根据request_id匹配对应的请求
              String? requestId = response.metadata?.requestId;
              if (requestId != null && _pendingRequests.containsKey(requestId)) {
                final completer = _pendingRequests.remove(requestId);
                completer?.complete(response);
              } else {
                // 如果没有request_id或找不到对应请求，完成第一个等待的请求
                if (_pendingRequests.isNotEmpty) {
                  final completer = _pendingRequests.remove(_pendingRequests.keys.first);
                  completer?.complete(response);
                }
              }
            } catch (e) {
              AppLogger.ipcError('解析IPC响应失败', exception: e, data: {'responseJson': responseJson});
              // 对于解析失败的响应，创建错误响应
              final errorResponse = IPCResponse.failure(
                errorCode: IPCErrorCode.internalError,
                message: '响应解析失败: $e',
              );
              if (_pendingRequests.isNotEmpty) {
                final completer = _pendingRequests.remove(_pendingRequests.keys.first);
                completer?.complete(errorResponse);
              }
            }
            
            // 重置状态以读取下一个响应
            readingLength = true;
            expectedLength = 4;
          } else {
            break; // 没有足够数据，等待更多数据
          }
        }
      },
      onError: (error) {
        AppLogger.ipcError('Socket连接错误', exception: error);
        // 完成所有等待的请求，返回连接错误
        final errorResponse = IPCResponse.failure(
          errorCode: IPCErrorCode.connectionFailed,
          message: 'Socket连接错误: $error',
        );
        for (final completer in _pendingRequests.values) {
          if (!completer.isCompleted) {
            completer.complete(errorResponse);
          }
        }
        _pendingRequests.clear();
      },
    );
  }

  /// 发现socket路径
  Future<String> _discoverSocketPath() async {
    try {
      final socketInfo = await _readSocketInfo();
      if (socketInfo != null && socketInfo['type'] == 'unix_socket') {
        return socketInfo['path'] ?? '';
      }
    } catch (e) {
      AppLogger.ipcError('读取socket信息失败', exception: e);
    }
    return '';
  }

  /// 发现pipe名称
  Future<String> _discoverPipeName() async {
    try {
      final socketInfo = await _readSocketInfo();
      if (socketInfo != null && socketInfo['type'] == 'named_pipe') {
        String fullPath = socketInfo['path'] ?? '';
        if (fullPath.startsWith('\\\\.\\pipe\\')) {
          return fullPath.substring('\\\\.\\pipe\\'.length);
        }
      }
    } catch (e) {
      developer.log('读取pipe信息失败: $e', name: 'IPCClient', level: 1000);
    }
    return '';
  }

  /// 执行认证握手 - 使用IPC协议
  Future<bool> _performAuthentication({int maxRetries = 2}) async {
    for (int attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        developer.log('IPC V2认证尝试 $attempt/$maxRetries', name: 'IPCClient', level: 800);
        
        final authRequest = IPCRequest.post(
          path: '/auth/handshake',
          data: {
            'client_pid': io.pid,
            'client_type': 'flutter_ui_v2',
            'timestamp': DateTime.now().millisecondsSinceEpoch,
            'attempt': attempt,
            'protocol_version': '2.0',
          },
        );

        final response = await sendRequest(authRequest);
        
        print('[DEBUG] IPC V2认证响应 (尝试 $attempt): success=${response.success}, data=${response.data}, error=${response.error}');
        
        if (response.success && response.data?['authenticated'] == true) {
          _isAuthenticated = true;
          developer.log('IPC V2认证成功 (尝试 $attempt)', name: 'IPCClient', level: 800);
          print('[DEBUG] IPC V2认证成功 (尝试 $attempt)');
          return true;
        } else {
          final errorMsg = response.error?.message ?? 'Unknown authentication error';
          developer.log('IPC V2认证失败 (尝试 $attempt): $errorMsg', name: 'IPCClient', level: 1000);
          print('[DEBUG] IPC V2认证失败 (尝试 $attempt): $errorMsg');
          
          // 检查是否是可重试的错误
          if (!response.success && response.error?.code == IPCErrorCode.internalError && attempt < maxRetries) {
            await Future.delayed(Duration(milliseconds: 200 * attempt));
            continue;
          } else {
            _isAuthenticated = false;
            return false;
          }
        }
      } catch (e) {
        developer.log('认证握手失败 (尝试 $attempt): $e', name: 'IPCClient', level: 1000);
        if (attempt < maxRetries) {
          await Future.delayed(Duration(milliseconds: 200 * attempt));
        }
      }
    }
    
    _isAuthenticated = false;
    return false;
  }

  /// 读取socket信息文件
  Future<Map<String, dynamic>?> _readSocketInfo() async {
    try {
      final homeDir = io.Platform.environment['HOME'] ?? io.Platform.environment['USERPROFILE'];
      if (homeDir == null) return null;
      
      final socketFile = io.File('$homeDir/.linch-mind/daemon.socket');
      if (!await socketFile.exists()) return null;
      
      final content = await socketFile.readAsString();
      return jsonDecode(content);
    } catch (e) {
      developer.log('读取socket信息文件失败: $e', name: 'IPCClient', level: 1000);
      return null;
    }
  }

  /// 发送IPC请求
  Future<IPCResponse> sendRequest(IPCRequest request) async {
    if (!_isConnected) {
      return IPCResponse.failure(
        errorCode: IPCErrorCode.connectionFailed,
        message: 'IPC客户端未连接',
      );
    }

    // 认证请求不需要检查认证状态
    final isAuthRequest = request.path == '/auth/handshake';
    if (!_isAuthenticated && !isAuthRequest) {
      return IPCResponse.failure(
        errorCode: IPCErrorCode.authRequired,
        message: 'IPC客户端未认证',
      );
    }

    if (io.Platform.isWindows) {
      return await _sendNamedPipeRequest(request);
    } else {
      return await _sendUnixSocketRequest(request);
    }
  }

  /// 通过Unix Socket发送请求 - 使用IPC协议
  Future<IPCResponse> _sendUnixSocketRequest(IPCRequest request) async {
    if (_socket == null) {
      return IPCResponse.failure(
        errorCode: IPCErrorCode.connectionFailed,
        message: 'Unix socket未连接',
      );
    }

    // 确保request有ID
    String requestId = request.requestId ?? _generateRequestId();
    final requestWithId = request.copyWith(requestId: requestId);
    
    final messageJson = jsonEncode(requestWithId.toJson());
    final messageBytes = utf8.encode(messageJson);
    
    developer.log('发送IPC V2请求: ${request.method} ${request.path}', name: 'IPCClient', level: 800);

    // 创建一个completer来等待响应
    final completer = Completer<IPCResponse>();
    _pendingRequests[requestId] = completer;

    try {
      // 发送消息长度前缀 (4字节)
      final lengthBytes = Uint8List(4);
      lengthBytes.buffer.asByteData().setUint32(0, messageBytes.length, Endian.big);
      _socket!.add(lengthBytes);

      // 发送消息内容
      _socket!.add(messageBytes);

      // 设置请求超时
      final timeoutFuture = Future.delayed(
        const Duration(seconds: 10),
        () => IPCResponse.failure(
          errorCode: IPCErrorCode.requestTimeout,
          message: 'Request timeout',
          requestId: requestId,
        ),
      );

      return Future.any([completer.future, timeoutFuture]);
    } catch (e) {
      _pendingRequests.remove(requestId);
      developer.log('发送IPC V2请求失败: $e', name: 'IPCClient', level: 1000);
      return IPCResponse.failure(
        errorCode: IPCErrorCode.internalError,
        message: '发送请求失败: $e',
        requestId: requestId,
      );
    }
  }

  /// 通过Named Pipe发送请求
  Future<IPCResponse> _sendNamedPipeRequest(IPCRequest request) async {
    // Windows Named Pipe客户端请求实现
    try {
      // 模拟Named Pipe通信 - 实际实现需要使用FFI或其他方式
      return IPCResponse.success(
        data: {'message': 'Named Pipe响应 (模拟)', 'protocol': 'IPC V2'},
        requestId: request.requestId,
      );
    } catch (e) {
      return IPCResponse.failure(
        errorCode: IPCErrorCode.connectionFailed,
        message: 'Named Pipe请求失败: $e',
        requestId: request.requestId,
      );
    }
  }

  /// HTTP风格的GET请求 - 返回IPC响应
  Future<IPCResponse> get(String path, {Map<String, dynamic>? queryParams}) async {
    final request = IPCRequest.get(
      path: path,
      queryParams: queryParams,
      requestId: _generateRequestId(),
    );
    return await sendRequest(request);
  }

  /// HTTP风格的POST请求 - 返回IPC响应
  Future<IPCResponse> post(String path, {Map<String, dynamic>? data}) async {
    final request = IPCRequest.post(
      path: path,
      data: data,
      requestId: _generateRequestId(),
    );
    return await sendRequest(request);
  }

  /// HTTP风格的PUT请求 - 返回IPC响应
  Future<IPCResponse> put(String path, {Map<String, dynamic>? data}) async {
    final request = IPCRequest.put(
      path: path,
      data: data,
      requestId: _generateRequestId(),
    );
    return await sendRequest(request);
  }

  /// 断开连接
  Future<void> disconnect() async {
    _isConnected = false;
    _isAuthenticated = false;

    // 取消socket监听
    if (_socketSubscription != null) {
      await _socketSubscription!.cancel();
      _socketSubscription = null;
    }

    // 完成所有等待中的请求
    final disconnectResponse = IPCResponse.failure(
      errorCode: IPCErrorCode.connectionFailed,
      message: '连接已断开',
    );
    for (final completer in _pendingRequests.values) {
      if (!completer.isCompleted) {
        completer.complete(disconnectResponse);
      }
    }
    _pendingRequests.clear();

    if (_socket != null) {
      await _socket!.close();
      _socket = null;
    }

    if (_namedPipeProcess != null) {
      _namedPipeProcess!.kill();
      _namedPipeProcess = null;
    }

    developer.log('IPC V2连接已断开', name: 'IPCClient', level: 800);
  }

  /// 内部断开连接（不清理状态，用于重连）
  Future<void> _disconnectWithoutCleanup() async {
    try {
      if (_socketSubscription != null) {
        await _socketSubscription!.cancel();
        _socketSubscription = null;
      }

      if (_socket != null) {
        await _socket!.close();
        _socket = null;
      }

      if (_namedPipeProcess != null) {
        _namedPipeProcess!.kill();
        _namedPipeProcess = null;
      }

      _isConnected = false;
      _isAuthenticated = false;
    } catch (e) {
      developer.log('内部断开连接时出错: $e', name: 'IPCClient', level: 1000);
    }
  }

  /// 检查连接和认证状态
  bool get isConnectedAndAuthenticated => _isConnected && _isAuthenticated;

  /// 获取连接状态信息
  Map<String, dynamic> getConnectionStatus() {
    return {
      'connected': _isConnected,
      'authenticated': _isAuthenticated,
      'pending_requests': _pendingRequests.length,
      'socket_available': _socket != null,
      'protocol_version': '2.0',
    };
  }
}

/// IPC客户端单例服务
class IPCService {
  static IPCClient? _instance;

  static IPCClient get instance {
    return _instance ??= IPCClient();
  }

  static Future<void> dispose() async {
    if (_instance != null) {
      await _instance!.disconnect();
      _instance = null;
    }
  }
}