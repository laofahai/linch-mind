import 'dart:io';
import 'dart:async';
import 'dart:convert';

/// Daemon信息数据类
class DaemonInfo {
  final String host;
  final int port;
  final int pid;
  final String startedAt;
  final bool isAccessible;

  const DaemonInfo({
    required this.host,
    required this.port,
    required this.pid,
    required this.startedAt,
    this.isAccessible = false,
  });

  factory DaemonInfo.fromJson(Map<String, dynamic> json) {
    return DaemonInfo(
      host: json['host'] as String,
      port: json['port'] as int,
      pid: json['pid'] as int,
      startedAt: json['started_at'] as String,
    );
  }

  String get baseUrl => 'http://$host:$port';
}

/// Daemon端口服务 - 安全地发现和连接daemon
class DaemonPortService {
  static const String _socketFilePath = '.linch-mind/daemon.socket';
  static const String _portFilePath = '.linch-mind/daemon.port';
  static const int _defaultPort = 50001;
  static const String _defaultHost = '127.0.0.1';

  static DaemonPortService? _instance;
  static DaemonPortService get instance => _instance ??= DaemonPortService._();

  DaemonPortService._();

  DaemonInfo? _cachedDaemonInfo;

  /// 发现daemon实例
  Future<DaemonInfo?> discoverDaemon() async {
    if (_cachedDaemonInfo != null) {
      // 验证缓存的daemon是否仍然有效
      if (await _testDaemonConnection(_cachedDaemonInfo!)) {
        return _cachedDaemonInfo;
      } else {
        _cachedDaemonInfo = null;
      }
    }

    try {
      final homeDir =
          Platform.environment['HOME'] ?? Platform.environment['USERPROFILE'];
      if (homeDir == null) {
        print('[DaemonPortService] 无法获取用户主目录');
        return null;
      }

      // 优先尝试读取socket文件（IPC模式）
      final socketFile = File('$homeDir/$_socketFilePath');
      if (await socketFile.exists()) {
        final daemonInfo = await _readSocketFile(socketFile, homeDir);
        if (daemonInfo != null) {
          return daemonInfo;
        }
      }

      // 回退到端口文件（HTTP模式）
      final portFile = File('$homeDir/$_portFilePath');
      if (!await portFile.exists()) {
        print('[DaemonPortService] 配置文件不存在: socket=${socketFile.path}, port=${portFile.path}');
        return null;
      }
      
      return await _readPortFile(portFile, homeDir);

    } catch (e) {
      print('[DaemonPortService] 发现daemon时出错: $e');
      return null;
    }
  }
  
  /// 读取socket文件（IPC模式）
  Future<DaemonInfo?> _readSocketFile(File socketFile, String homeDir) async {
    try {
      // 检查文件权限（Unix系统）
      if (!Platform.isWindows) {
        final stat = await socketFile.stat();
        final mode = stat.mode;
        if ((mode & 0x3F) != 0) {
          print('[DaemonPortService] socket文件权限不安全，忽略');
          return null;
        }
      }
      
      // 读取JSON内容
      final socketContent = await socketFile.readAsString();
      final Map<String, dynamic> socketData = json.decode(socketContent);
      
      // 解析socket信息
      final String socketType = socketData['type'] ?? '';
      final String socketPath = socketData['path'] ?? '';
      final int pid = socketData['pid'] ?? 0;
      
      if (socketType.isEmpty || socketPath.isEmpty) {
        print('[DaemonPortService] socket文件格式无效');
        return null;
      }
      
      print('[DaemonPortService] 检测到IPC模式: $socketType, path: $socketPath');
      
      // 注意：Flutter端目前还是使用HTTP模式，这里返回null让其回退到HTTP
      // TODO: 在未来的版本中，这里应该返回一个标识IPC模式的DaemonInfo
      return null;
      
    } catch (e) {
      print('[DaemonPortService] 读取socket文件失败: $e');
      return null;
    }
  }
  
  /// 读取端口文件（HTTP模式）
  Future<DaemonInfo?> _readPortFile(File portFile, String homeDir) async {
    try {
      // 检查文件权限（Unix系统）
      if (!Platform.isWindows) {
        final stat = await portFile.stat();
        final mode = stat.mode;
        if ((mode & 0x3F) != 0) {
          print('[DaemonPortService] 端口文件权限不安全，忽略');
          return null;
        }
      }

      final portContent = await portFile.readAsString();

      // 解析格式: port:pid
      try {
        final parts = portContent.split(':');
        if (parts.length != 2) {
          print('[DaemonPortService] 端口文件格式无效，期望 "port:pid"');
          return null;
        }

        final port = int.parse(parts[0]);
        final pid = int.parse(parts[1]);

        final portData = {
          'host': _defaultHost,
          'port': port,
          'pid': pid,
          'started_at': DateTime.now().toIso8601String(),
        };

        final daemonInfo = DaemonInfo.fromJson(portData);

        // 验证进程是否运行（如果有PID）
        if (daemonInfo.pid > 0 && !await _verifyDaemonProcess(daemonInfo.pid)) {
          print('[DaemonPortService] Daemon进程 ${daemonInfo.pid} 未运行');
          return null;
        }

        // 测试连接性
        final isAccessible = await _testDaemonConnection(daemonInfo);
        final accessibleDaemonInfo = DaemonInfo(
          host: daemonInfo.host,
          port: daemonInfo.port,
          pid: daemonInfo.pid,
          startedAt: daemonInfo.startedAt,
          isAccessible: isAccessible,
        );

        if (isAccessible) {
          _cachedDaemonInfo = accessibleDaemonInfo;
          print(
              '[DaemonPortService] 发现可访问的daemon: ${daemonInfo.host}:${daemonInfo.port}');
        } else {
          print(
              '[DaemonPortService] Daemon不可访问: ${daemonInfo.host}:${daemonInfo.port}');
        }

        return accessibleDaemonInfo;
      } catch (e) {
        print('[DaemonPortService] 解析端口文件失败: $e');
        return null;
      }
    } catch (e) {
      print('[DaemonPortService] 发现daemon时出错: $e');
      return null;
    }
  }

  /// 获取daemon的基础URL（兼容旧接口）
  Future<String> getDaemonBaseUrl() async {
    final daemonInfo = await discoverDaemon();
    if (daemonInfo != null && daemonInfo.isAccessible) {
      return daemonInfo.baseUrl;
    }

    // 回退到默认配置
    print('[DaemonPortService] 使用默认端口配置');
    return 'http://$_defaultHost:$_defaultPort';
  }

  /// 获取daemon端口（仅端口号）
  Future<int> getDaemonPort() async {
    final daemonInfo = await discoverDaemon();
    return daemonInfo?.port ?? _defaultPort;
  }

  /// 清除缓存的daemon信息（用于重新发现）
  void clearCache() {
    _cachedDaemonInfo = null;
  }

  /// 检查daemon是否可访问（兼容旧接口）
  Future<bool> isDaemonReachable() async {
    final daemonInfo = await discoverDaemon();
    return daemonInfo?.isAccessible ?? false;
  }

  /// 等待daemon启动
  Future<DaemonInfo?> waitForDaemon({
    Duration timeout = const Duration(seconds: 30),
    Duration checkInterval = const Duration(seconds: 1),
  }) async {
    final startTime = DateTime.now();

    while (DateTime.now().difference(startTime) < timeout) {
      final daemonInfo = await discoverDaemon();
      if (daemonInfo != null && daemonInfo.isAccessible) {
        return daemonInfo;
      }

      await Future.delayed(checkInterval);
    }

    print('[DaemonPortService] Daemon发现超时');
    return null;
  }

  /// 验证daemon进程是否运行
  Future<bool> _verifyDaemonProcess(int pid) async {
    if (Platform.isWindows) {
      // Windows系统的进程验证
      try {
        final result = await Process.run('tasklist', ['/FI', 'PID eq $pid'],
            runInShell: true);
        return result.stdout.toString().contains(pid.toString());
      } catch (e) {
        print('[DaemonPortService] Windows进程验证失败: $e');
        return false;
      }
    } else {
      // Unix系统的进程验证
      try {
        final result =
            await Process.run('ps', ['-p', pid.toString()], runInShell: true);
        return result.exitCode == 0;
      } catch (e) {
        print('[DaemonPortService] Unix进程验证失败: $e');
        return false;
      }
    }
  }

  /// 测试daemon连接 (使用IPC)
  Future<bool> _testDaemonConnection(DaemonInfo daemonInfo,
      {Duration timeout = const Duration(seconds: 3)}) async {
    try {
      // 如果检测到IPC模式，则使用IPC连接测试
      if (daemonInfo.host == '127.0.0.1' && daemonInfo.port == 0) {
        return await _testIPCConnection();
      } else {
        // 备用HTTP测试（仅用于向后兼容）
        return await _testHTTPConnection(daemonInfo, timeout: timeout);
      }
    } catch (e) {
      print('[DaemonPortService] 连接测试失败: $e');
      return false;
    }
  }
  
  /// 测试IPC连接
  Future<bool> _testIPCConnection() async {
    try {
      // 简单的IPC连接测试
      final homeDir = Platform.environment['HOME'] ?? Platform.environment['USERPROFILE'];
      if (homeDir == null) return false;
      
      final socketFile = File('$homeDir/.linch-mind/daemon.socket');
      if (!await socketFile.exists()) return false;
      
      // 检查socket文件是否有效（包含有效JSON）
      final content = await socketFile.readAsString();
      final socketData = json.decode(content);
      
      return socketData['type'] != null && socketData['path'] != null;
    } catch (e) {
      print('[DaemonPortService] IPC连接测试失败: $e');
      return false;
    }
  }
  
  /// 测试HTTP连接（向后兼容）
  Future<bool> _testHTTPConnection(DaemonInfo daemonInfo, {Duration? timeout}) async {
    try {
      final client = HttpClient();
      client.connectionTimeout = timeout ?? const Duration(seconds: 3);

      final uri = Uri.parse('${daemonInfo.baseUrl}/health');
      final request = await client.getUrl(uri);
      final response = await request.close();

      client.close();
      return response.statusCode == 200;
    } catch (e) {
      print('[DaemonPortService] HTTP连接测试失败: $e');
      return false;
    }
  }
}
