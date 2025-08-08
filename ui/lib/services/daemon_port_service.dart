import 'dart:io';
import 'dart:async';
import 'dart:convert';

/// Daemon信息数据类 (纯IPC)
class DaemonInfo {
  final int pid;
  final String startedAt;
  final String socketPath;
  final String socketType; // 'unix' or 'windows'
  final bool isAccessible;

  const DaemonInfo({
    required this.pid,
    required this.startedAt,
    required this.socketPath,
    required this.socketType,
    this.isAccessible = false,
  });

  factory DaemonInfo.fromJson(Map<String, dynamic> json) {
    return DaemonInfo(
      pid: json['pid'] as int,
      startedAt: json['started_at'] as String,
      socketPath: json['path'] as String,
      socketType: json['type'] as String,
    );
  }
}

/// Daemon端口服务 - 安全地发现和连接daemon (纯IPC)
class DaemonPortService {
  static const String _socketFileName = 'daemon.socket';
  static const String _configDirName = '.linch-mind';

  static DaemonPortService? _instance;
  static DaemonPortService get instance => _instance ??= DaemonPortService._();

  DaemonPortService._();

  DaemonInfo? _cachedDaemonInfo;

  /// 发现daemon实例 (仅IPC)
  Future<DaemonInfo?> discoverDaemon() async {
    print('[DaemonPortService] discoverDaemon started');
    if (_cachedDaemonInfo != null) {
      print('[DaemonPortService] Found cached daemon info: $_cachedDaemonInfo');
      // 验证缓存的daemon是否仍然有效
      if (await _testDaemonConnection(_cachedDaemonInfo!)) {
        print('[DaemonPortService] Cached daemon is still valid');
        return _cachedDaemonInfo;
      } else {
        print('[DaemonPortService] Cached daemon is invalid, clearing cache');
        _cachedDaemonInfo = null;
      }
    }

    try {
      final socketFile = await _getSocketFile();
      print('[DaemonPortService] Socket file path: ${socketFile?.path}');
      if (socketFile == null || !await socketFile.exists()) {
        print('[DaemonPortService] Socket文件不存在');
        return null;
      }

      // 读取并解析socket文件
      final daemonInfo = await _readSocketFile(socketFile);
      print('[DaemonPortService] Parsed daemon info: $daemonInfo');
      if (daemonInfo == null) {
        return null;
      }

      // 测试连接性并更新缓存
      final isAccessible = await _testDaemonConnection(daemonInfo);
      print(
          '[DaemonPortService] Connection test result: isAccessible=$isAccessible');
      final accessibleDaemonInfo = DaemonInfo(
        pid: daemonInfo.pid,
        startedAt: daemonInfo.startedAt,
        socketPath: daemonInfo.socketPath,
        socketType: daemonInfo.socketType,
        isAccessible: isAccessible,
      );

      if (isAccessible) {
        _cachedDaemonInfo = accessibleDaemonInfo;
        print('[DaemonPortService] 发现可访问的IPC daemon (PID: ${daemonInfo.pid})');
      } else {
        print('[DaemonPortService] IPC daemon (PID: ${daemonInfo.pid}) 不可访问');
      }

      return accessibleDaemonInfo;
    } catch (e) {
      print('[DaemonPortService] 发现daemon时出错: $e');
      return null;
    }
  }

  Future<File?> _getSocketFile() async {
    final homeDir =
        Platform.environment['HOME'] ?? Platform.environment['USERPROFILE'];
    if (homeDir == null) {
      print('[DaemonPortService] 无法获取用户主目录');
      return null;
    }
    return File('$homeDir/$_configDirName/$_socketFileName');
  }

  /// 读取并解析socket文件
  Future<DaemonInfo?> _readSocketFile(File socketFile) async {
    try {
      // 检查文件权限（Unix系统）
      if (!Platform.isWindows) {
        final stat = await socketFile.stat();
        if ((stat.mode & 0x3F) != 0) {
          // 检查其他用户或组的权限
          print('[DaemonPortService] Socket文件权限不安全，忽略');
          return null;
        }
      }

      // 读取JSON内容
      final socketContent = await socketFile.readAsString();
      final Map<String, dynamic> socketData = json.decode(socketContent);

      final pid = socketData['pid'] as int?;
      final path = socketData['path'] as String?;
      final type = socketData['type'] as String?;

      if (pid == null || path == null || type == null) {
        print('[DaemonPortService] Socket文件格式无效');
        return null;
      }

      // 验证进程是否仍在运行
      if (!await _verifyDaemonProcess(pid)) {
        print('[DaemonPortService] Daemon进程 $pid 未运行，清理无效的socket文件');
        await socketFile.delete();
        return null;
      }

      return DaemonInfo(
        pid: pid,
        startedAt: DateTime.now().toIso8601String(), // 启动时间可以从文件元数据获取，但这里简化
        socketPath: path,
        socketType: type,
      );
    } catch (e) {
      print('[DaemonPortService] 读取socket文件失败: $e');
      return null;
    }
  }

  /// 清除缓存的daemon信息（用于重新发现）
  void clearCache() {
    _cachedDaemonInfo = null;
  }

  /// 检查daemon是否可访问
  Future<bool> isDaemonReachable() async {
    final daemonInfo = await discoverDaemon();
    print(
        '[DaemonPortService] isDaemonReachable: daemonInfo=$daemonInfo, isAccessible=${daemonInfo?.isAccessible}');
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
    if (pid <= 0) return false;
    try {
      if (Platform.isWindows) {
        final result = await Process.run('tasklist', ['/FI', 'PID eq $pid'],
            runInShell: true);
        return result.stdout.toString().contains(pid.toString());
      } else {
        final result =
            await Process.run('ps', ['-p', pid.toString()], runInShell: true);
        return result.exitCode == 0;
      }
    } catch (e) {
      print('[DaemonPortService] 进程验证失败: $e');
      return false;
    }
  }

  /// 测试daemon连接 (纯IPC)
  Future<bool> _testDaemonConnection(DaemonInfo daemonInfo) async {
    try {
      // 验证进程是否存在
      if (!await _verifyDaemonProcess(daemonInfo.pid)) {
        return false;
      }

      // 验证socket文件是否存在
      if (daemonInfo.socketType == 'unix_socket') {
        final socketFile = File(daemonInfo.socketPath);
        if (!await socketFile.exists()) {
          print(
              '[DaemonPortService] Unix socket文件不存在: ${daemonInfo.socketPath}');
          return false;
        }
      }

      // 如果进程存在且socket文件存在，认为daemon是可访问的
      // 实际的连接测试会在IPCClient中进行
      return true;
    } catch (e) {
      print('[DaemonPortService] IPC连接测试失败: $e');
      return false;
    }
  }
}
