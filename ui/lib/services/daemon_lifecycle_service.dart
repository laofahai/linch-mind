import 'dart:io';
import 'dart:async';
import 'package:flutter/foundation.dart';
import 'daemon_port_service.dart';

/// 运行模式枚举
enum RunMode {
  development,
  production,
}

/// Daemon启动结果
class DaemonStartResult {
  final bool success;
  final String? error;
  final DaemonInfo? daemonInfo;
  final Process? process; // 开发模式下的进程引用
  
  const DaemonStartResult({
    required this.success,
    this.error,
    this.daemonInfo,
    this.process,
  });
  
  factory DaemonStartResult.success(DaemonInfo daemonInfo, {Process? process}) {
    return DaemonStartResult(
      success: true,
      daemonInfo: daemonInfo,
      process: process,
    );
  }
  
  factory DaemonStartResult.failure(String error) {
    return DaemonStartResult(
      success: false,
      error: error,
    );
  }
}

/// Daemon生命周期管理服务
class DaemonLifecycleService {
  static const Duration _startupTimeout = Duration(seconds: 30);
  static const Duration _healthCheckInterval = Duration(seconds: 5);
  
  static DaemonLifecycleService? _instance;
  static DaemonLifecycleService get instance => _instance ??= DaemonLifecycleService._();
  
  DaemonLifecycleService._();
  
  final DaemonPortService _portService = DaemonPortService.instance;
  Process? _developmentProcess;
  Timer? _healthCheckTimer;
  
  /// 检测当前运行模式
  RunMode get runMode {
    // 在debug模式下默认为开发模式
    if (kDebugMode) {
      return RunMode.development;
    }
    
    // 检查环境变量
    final envMode = Platform.environment['LINCH_MIND_MODE'];
    if (envMode == 'production') {
      return RunMode.production;
    }
    
    // 检查是否存在开发环境标识文件或目录
    final devIndicators = [
      'daemon/pyproject.toml',
      'connectors/pyproject.toml',
      '.git',
    ];
    
    for (final indicator in devIndicators) {
      if (File(indicator).existsSync() || Directory(indicator).existsSync()) {
        return RunMode.development;
      }
    }
    
    return RunMode.production;
  }
  
  /// 确保daemon运行
  Future<DaemonStartResult> ensureDaemonRunning() async {
    print('[DaemonLifecycle] 检查daemon状态 (模式: ${runMode.name})');
    
    // 首先检查daemon是否已经运行
    final existingDaemon = await _portService.discoverDaemon();
    if (existingDaemon != null && existingDaemon.isAccessible) {
      print('[DaemonLifecycle] Daemon已运行: ${existingDaemon.baseUrl}');
      return DaemonStartResult.success(existingDaemon);
    }
    
    // 清除旧的缓存信息
    _portService.clearCache();
    
    // 根据运行模式启动daemon
    switch (runMode) {
      case RunMode.development:
        return await _startDevelopmentDaemon();
      case RunMode.production:
        return await _startProductionDaemon();
    }
  }
  
  /// 开发模式启动daemon
  Future<DaemonStartResult> _startDevelopmentDaemon() async {
    print('[DaemonLifecycle] 开发模式启动daemon');
    
    try {
      // 检查可执行文件
      final executables = await _findExecutables();
      final poetryPath = executables['poetry'];
      final pythonPath = executables['python'];
      
      if (poetryPath == null && pythonPath == null) {
        return DaemonStartResult.failure('未找到Python或Poetry环境');
      }
      
      // 检查daemon目录
      final daemonDir = Directory('daemon');
      if (!daemonDir.existsSync()) {
        return DaemonStartResult.failure('未找到daemon目录');
      }
      
      Process process;
      
      // 优先使用Poetry，回退到直接Python
      if (poetryPath != null) {
        print('[DaemonLifecycle] 使用Poetry启动daemon: poetry run linch-daemon');
        process = await Process.start(
          poetryPath,
          ['run', 'linch-daemon'],
          workingDirectory: 'daemon',
          environment: {
            ...Platform.environment,
            'LINCH_MIND_MODE': 'development',
          },
        );
      } else {
        print('[DaemonLifecycle] 使用Python直接启动daemon: python -m api.main');
        process = await Process.start(
          pythonPath!,
          ['-m', 'api.main'],
          workingDirectory: 'daemon',
          environment: {
            ...Platform.environment,
            'PYTHONPATH': '.',
            'LINCH_MIND_MODE': 'development',
          },
        );
      }
      
      _developmentProcess = process;
      
      // 监听进程输出
      process.stdout.transform(const SystemEncoding().decoder).listen((data) {
        print('[Daemon stdout] $data');
      });
      
      process.stderr.transform(const SystemEncoding().decoder).listen((data) {
        print('[Daemon stderr] $data');
      });
      
      // 等待daemon启动
      final daemonInfo = await _portService.waitForDaemon(timeout: _startupTimeout);
      if (daemonInfo == null) {
        process.kill();
        return DaemonStartResult.failure('Daemon启动超时');
      }
      
      // 启动健康检查
      _startHealthCheck();
      
      print('[DaemonLifecycle] 开发模式daemon启动成功: ${daemonInfo.baseUrl}');
      return DaemonStartResult.success(daemonInfo, process: process);
      
    } catch (e) {
      print('[DaemonLifecycle] 开发模式启动失败: $e');
      return DaemonStartResult.failure('启动失败: $e');
    }
  }
  
  /// 生产模式启动daemon（作为系统服务）
  Future<DaemonStartResult> _startProductionDaemon() async {
    print('[DaemonLifecycle] 生产模式检查daemon');
    
    try {
      // 在生产模式下，daemon应该作为系统服务运行
      // 我们只检查服务状态，不直接启动
      
      // 尝试通过systemctl检查服务状态（Linux）
      if (Platform.isLinux) {
        final result = await _checkSystemdService();
        if (result != null) {
          return result;
        }
      }
      
      // 尝试通过launchctl检查服务状态（macOS）
      if (Platform.isMacOS) {
        final result = await _checkLaunchdService();
        if (result != null) {
          return result;
        }
      }
      
      // Windows服务检查
      if (Platform.isWindows) {
        final result = await _checkWindowsService();
        if (result != null) {
          return result;
        }
      }
      
      // 如果服务未运行，等待一段时间看是否有daemon启动
      print('[DaemonLifecycle] 等待系统服务启动daemon');
      final daemonInfo = await _portService.waitForDaemon(
        timeout: const Duration(seconds: 10),
      );
      
      if (daemonInfo != null && daemonInfo.isAccessible) {
        return DaemonStartResult.success(daemonInfo);
      }
      
      return DaemonStartResult.failure(
        '生产模式下daemon未运行。请确保Linch Mind系统服务已启动。'
      );
      
    } catch (e) {
      print('[DaemonLifecycle] 生产模式检查失败: $e');
      return DaemonStartResult.failure('检查daemon服务失败: $e');
    }
  }
  
  /// 查找Python和Poetry可执行文件
  Future<Map<String, String?>> _findExecutables() async {
    final result = <String, String?>{};
    
    // 查找Poetry
    try {
      final poetryResult = await Process.run('which', ['poetry']);
      if (poetryResult.exitCode == 0) {
        result['poetry'] = poetryResult.stdout.toString().trim();
        print('[DaemonLifecycle] 找到Poetry: ${result['poetry']}');
      }
    } catch (e) {
      // Poetry不可用
    }
    
    // 查找Python
    final candidates = ['python3', 'python', 'py'];
    for (final candidate in candidates) {
      try {
        final pythonResult = await Process.run('which', [candidate]);
        if (pythonResult.exitCode == 0) {
          result['python'] = pythonResult.stdout.toString().trim();
          print('[DaemonLifecycle] 找到Python: ${result['python']}');
          break;
        }
      } catch (e) {
        // 继续尝试下一个候选
      }
    }
    
    return result;
  }
  
  /// 检查systemd服务状态（Linux）
  Future<DaemonStartResult?> _checkSystemdService() async {
    try {
      final result = await Process.run('systemctl', ['is-active', 'linch-mind-daemon']);
      if (result.exitCode == 0 && result.stdout.toString().trim() == 'active') {
        print('[DaemonLifecycle] systemd服务运行中');
        final daemonInfo = await _portService.waitForDaemon(timeout: const Duration(seconds: 5));
        if (daemonInfo != null) {
          return DaemonStartResult.success(daemonInfo);
        }
      }
    } catch (e) {
      print('[DaemonLifecycle] systemd检查失败: $e');
    }
    return null;
  }
  
  /// 检查launchd服务状态（macOS）
  Future<DaemonStartResult?> _checkLaunchdService() async {
    try {
      final result = await Process.run('launchctl', ['list', 'com.laofahai.linch-mind-daemon']);
      if (result.exitCode == 0) {
        print('[DaemonLifecycle] launchd服务运行中');
        final daemonInfo = await _portService.waitForDaemon(timeout: const Duration(seconds: 5));
        if (daemonInfo != null) {
          return DaemonStartResult.success(daemonInfo);
        }
      }
    } catch (e) {
      print('[DaemonLifecycle] launchd检查失败: $e');
    }
    return null;
  }
  
  /// 检查Windows服务状态
  Future<DaemonStartResult?> _checkWindowsService() async {
    try {
      final result = await Process.run('sc', ['query', 'LinchMindDaemon']);
      if (result.exitCode == 0 && result.stdout.toString().contains('RUNNING')) {
        print('[DaemonLifecycle] Windows服务运行中');
        final daemonInfo = await _portService.waitForDaemon(timeout: const Duration(seconds: 5));
        if (daemonInfo != null) {
          return DaemonStartResult.success(daemonInfo);
        }
      }
    } catch (e) {
      print('[DaemonLifecycle] Windows服务检查失败: $e');
    }
    return null;
  }
  
  /// 启动健康检查定时器
  void _startHealthCheck() {
    _healthCheckTimer?.cancel();
    _healthCheckTimer = Timer.periodic(_healthCheckInterval, (timer) async {
      final isReachable = await _portService.isDaemonReachable();
      if (!isReachable) {
        print('[DaemonLifecycle] Daemon健康检查失败，清除缓存');
        _portService.clearCache();
        
        // 如果是开发模式且进程已停止，清理引用
        if (runMode == RunMode.development && _developmentProcess != null) {
          try {
            _developmentProcess!.kill();
          } catch (e) {
            // 忽略kill错误
          }
          _developmentProcess = null;
        }
        
        timer.cancel();
      }
    });
  }
  
  /// 停止daemon（仅开发模式）
  Future<bool> stopDaemon() async {
    if (runMode == RunMode.production) {
      print('[DaemonLifecycle] 生产模式不支持停止daemon');
      return false;
    }
    
    _healthCheckTimer?.cancel();
    
    if (_developmentProcess != null) {
      try {
        print('[DaemonLifecycle] 停止开发模式daemon进程');
        _developmentProcess!.kill();
        final exitCode = await _developmentProcess!.exitCode;
        print('[DaemonLifecycle] Daemon进程已停止，退出码: $exitCode');
        _developmentProcess = null;
        _portService.clearCache();
        return true;
      } catch (e) {
        print('[DaemonLifecycle] 停止daemon失败: $e');
        return false;
      }
    }
    
    return false;
  }
  
  /// 重启daemon（仅开发模式）
  Future<DaemonStartResult> restartDaemon() async {
    if (runMode == RunMode.production) {
      return DaemonStartResult.failure('生产模式不支持重启daemon');
    }
    
    print('[DaemonLifecycle] 重启daemon');
    await stopDaemon();
    await Future.delayed(const Duration(seconds: 2));
    return await ensureDaemonRunning();
  }
  
  /// 获取daemon状态信息
  Future<Map<String, dynamic>> getDaemonStatus() async {
    final daemonInfo = await _portService.discoverDaemon();
    
    return {
      'mode': runMode.name,
      'running': daemonInfo?.isAccessible ?? false,
      'daemon_info': daemonInfo != null ? {
        'host': daemonInfo.host,
        'port': daemonInfo.port,
        'pid': daemonInfo.pid,
        'started_at': daemonInfo.startedAt,
        'base_url': daemonInfo.baseUrl,
      } : null,
      'development_process_running': _developmentProcess != null,
      'health_check_active': _healthCheckTimer?.isActive ?? false,
    };
  }
  
  /// 清理资源
  void dispose() {
    _healthCheckTimer?.cancel();
    if (runMode == RunMode.development && _developmentProcess != null) {
      _developmentProcess!.kill();
    }
  }
}