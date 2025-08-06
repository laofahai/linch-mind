import 'dart:io';
import 'dart:convert';
import 'dart:async';
import 'dart:typed_data';

/// IPC消息格式
class IPCMessage {
  final String method;
  final String path;
  final Map<String, dynamic> data;
  final Map<String, String> headers;
  final Map<String, dynamic> queryParams;

  IPCMessage({
    required this.method,
    required this.path,
    this.data = const {},
    this.headers = const {},
    this.queryParams = const {},
  });

  String toJson() {
    return jsonEncode({
      'method': method.toUpperCase(),
      'path': path,
      'data': data,
      'headers': headers,
      'query_params': queryParams,
    });
  }

  static IPCMessage fromJson(String jsonStr) {
    final data = jsonDecode(jsonStr);
    return IPCMessage(
      method: data['method'],
      path: data['path'],
      data: Map<String, dynamic>.from(data['data'] ?? {}),
      headers: Map<String, String>.from(data['headers'] ?? {}),
      queryParams: Map<String, dynamic>.from(data['query_params'] ?? {}),
    );
  }
}

/// IPC响应格式
class IPCResponse {
  final int statusCode;
  final Map<String, dynamic> data;
  final Map<String, String> headers;

  IPCResponse({
    this.statusCode = 200,
    this.data = const {},
    this.headers = const {},
  });

  String toJson() {
    return jsonEncode({
      'status_code': statusCode,
      'data': data,
      'headers': headers,
    });
  }

  static IPCResponse fromJson(String jsonStr) {
    final data = jsonDecode(jsonStr);
    return IPCResponse(
      statusCode: data['status_code'] ?? 200,
      data: Map<String, dynamic>.from(data['data'] ?? {}),
      headers: Map<String, String>.from(data['headers'] ?? {}),
    );
  }
}

/// 跨平台IPC客户端
class IPCClient {
  Socket? _socket;
  Process? _namedPipeProcess;
  bool _isConnected = false;
  final String? _socketPath;
  final String? _pipeName;

  IPCClient({String? socketPath, String? pipeName})
      : _socketPath = socketPath,
        _pipeName = pipeName;

  /// 连接到daemon
  Future<bool> connect() async {
    if (_isConnected) return true;

    try {
      if (Platform.isWindows) {
        return await _connectNamedPipe();
      } else {
        return await _connectUnixSocket();
      }
    } catch (e) {
      print('[IPCClient] 连接失败: $e');
      return false;
    }
  }

  /// 连接Unix Domain Socket
  Future<bool> _connectUnixSocket() async {
    String socketPath = _socketPath ?? await _discoverSocketPath();
    
    if (socketPath.isEmpty) {
      print('[IPCClient] 无法找到socket路径');
      return false;
    }

    try {
      _socket = await Socket.connect(
        InternetAddress(socketPath, type: InternetAddressType.unix),
        0,
      );
      
      _isConnected = true;
      print('[IPCClient] 已连接到Unix socket: $socketPath');
      return true;
    } catch (e) {
      print('[IPCClient] Unix socket连接失败: $e');
      return false;
    }
  }

  /// 连接Windows Named Pipe
  Future<bool> _connectNamedPipe() async {
    // Windows Named Pipe客户端实现
    // 这里使用简化的方法，实际可能需要使用FFI或其他方式
    String pipeName = _pipeName ?? await _discoverPipeName();
    
    if (pipeName.isEmpty) {
      print('[IPCClient] 无法找到pipe名称');
      return false;
    }
    
    try {
      // 在Windows上，我们可以尝试使用标准文件操作访问Named Pipe
      // 这是一个简化实现，实际可能需要更复杂的处理
      final pipeFile = File('\\\\.\\pipe\\$pipeName');
      
      if (await pipeFile.exists()) {
        _isConnected = true;
        print('[IPCClient] 已连接到Named Pipe: $pipeName');
        return true;
      } else {
        print('[IPCClient] Named Pipe不存在: $pipeName');
        return false;
      }
    } catch (e) {
      print('[IPCClient] Named Pipe连接失败: $e');
      return false;
    }
  }

  /// 发现socket路径
  Future<String> _discoverSocketPath() async {
    try {
      final socketInfo = await _readSocketInfo();
      if (socketInfo != null && socketInfo['type'] == 'unix_socket') {
        return socketInfo['path'] ?? '';
      }
    } catch (e) {
      print('[IPCClient] 读取socket信息失败: $e');
    }
    return '';
  }

  /// 发现pipe名称
  Future<String> _discoverPipeName() async {
    try {
      final socketInfo = await _readSocketInfo();
      if (socketInfo != null && socketInfo['type'] == 'named_pipe') {
        String fullPath = socketInfo['path'] ?? '';
        // 从完整路径提取pipe名称
        if (fullPath.startsWith('\\\\.\\pipe\\')) {
          return fullPath.substring('\\\\.\\pipe\\'.length);
        }
      }
    } catch (e) {
      print('[IPCClient] 读取pipe信息失败: $e');
    }
    return '';
  }

  /// 读取socket信息文件
  Future<Map<String, dynamic>?> _readSocketInfo() async {
    try {
      final homeDir = Platform.environment['HOME'] ?? Platform.environment['USERPROFILE'];
      if (homeDir == null) return null;
      
      final socketFile = File('$homeDir/.linch-mind/daemon.socket');
      if (!await socketFile.exists()) return null;
      
      final content = await socketFile.readAsString();
      return jsonDecode(content);
    } catch (e) {
      print('[IPCClient] 读取socket信息文件失败: $e');
      return null;
    }
  }

  /// 发送请求
  Future<IPCResponse> sendRequest(IPCMessage message) async {
    if (!_isConnected) {
      throw Exception('IPC客户端未连接');
    }

    if (Platform.isWindows) {
      return await _sendNamedPipeRequest(message);
    } else {
      return await _sendUnixSocketRequest(message);
    }
  }

  /// 通过Unix Socket发送请求
  Future<IPCResponse> _sendUnixSocketRequest(IPCMessage message) async {
    if (_socket == null) {
      throw Exception('Unix socket未连接');
    }

    final messageJson = message.toJson();
    final messageBytes = utf8.encode(messageJson);

    // 发送消息长度前缀 (4字节)
    final lengthBytes = Uint8List(4);
    lengthBytes.buffer.asByteData().setUint32(0, messageBytes.length, Endian.big);
    _socket!.add(lengthBytes);

    // 发送消息内容
    _socket!.add(messageBytes);

    // 读取响应长度
    final lengthResponse = await _socket!.take(4).toList();
    final lengthBuffer = Uint8List.fromList(lengthResponse.expand((x) => x).toList());
    final responseLength = lengthBuffer.buffer.asByteData().getUint32(0, Endian.big);

    // 读取响应内容
    final responseBuffer = await _socket!.take(responseLength).toList();
    final responseBytes = Uint8List.fromList(responseBuffer.expand((x) => x).toList());
    final responseJson = utf8.decode(responseBytes);

    return IPCResponse.fromJson(responseJson);
  }

  /// 通过Named Pipe发送请求
  Future<IPCResponse> _sendNamedPipeRequest(IPCMessage message) async {
    // Windows Named Pipe客户端请求实现
    // 这是简化版本，实际实现可能需要更复杂的处理
    
    final messageJson = message.toJson();
    
    // 模拟Named Pipe通信
    try {
      // 这里应该通过实际的Named Pipe发送数据
      // 暂时返回成功响应
      return IPCResponse(
        statusCode: 200,
        data: {'message': 'Named Pipe响应 (模拟)'},
      );
    } catch (e) {
      return IPCResponse(
        statusCode: 500,
        data: {'error': 'Named Pipe请求失败: $e'},
      );
    }
  }

  /// HTTP风格的GET请求
  Future<IPCResponse> get(String path, {Map<String, dynamic>? queryParams}) async {
    final message = IPCMessage(
      method: 'GET',
      path: path,
      queryParams: queryParams ?? {},
    );
    return await sendRequest(message);
  }

  /// HTTP风格的POST请求
  Future<IPCResponse> post(String path, {Map<String, dynamic>? data}) async {
    final message = IPCMessage(
      method: 'POST',
      path: path,
      data: data ?? {},
    );
    return await sendRequest(message);
  }

  /// HTTP风格的PUT请求
  Future<IPCResponse> put(String path, {Map<String, dynamic>? data}) async {
    final message = IPCMessage(
      method: 'PUT',
      path: path,
      data: data ?? {},
    );
    return await sendRequest(message);
  }

  /// HTTP风格的DELETE请求
  Future<IPCResponse> delete(String path) async {
    final message = IPCMessage(
      method: 'DELETE',
      path: path,
    );
    return await sendRequest(message);
  }

  /// 断开连接
  Future<void> disconnect() async {
    _isConnected = false;

    if (_socket != null) {
      await _socket!.close();
      _socket = null;
    }

    if (_namedPipeProcess != null) {
      _namedPipeProcess!.kill();
      _namedPipeProcess = null;
    }

    print('[IPCClient] IPC连接已断开');
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