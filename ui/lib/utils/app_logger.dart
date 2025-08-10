import 'dart:developer' as developer;
import 'dart:io';

/// 应用程序统一日志系统
/// 提供分级日志、错误追踪和调试信息
class AppLogger {
  static const String _appName = 'LinchMind';
  static bool _debugMode = true;

  /// 日志级别
  static const int _levelTrace = 500;
  static const int _levelDebug = 700;
  static const int _levelInfo = 800;
  static const int _levelWarn = 900;
  static const int _levelError = 1000;
  static const int _levelCritical = 1200;

  /// 设置调试模式
  static void setDebugMode(bool enabled) {
    _debugMode = enabled;
  }

  /// TRACE级别日志 - 最详细的执行流程
  static void trace(String message,
      {String? module, Map<String, dynamic>? data}) {
    if (!_debugMode) return;
    _log(_levelTrace, 'TRACE', message, module: module, data: data);
  }

  /// DEBUG级别日志 - 调试信息
  static void debug(String message,
      {String? module, Map<String, dynamic>? data}) {
    if (!_debugMode) return;
    _log(_levelDebug, 'DEBUG', message, module: module, data: data);
  }

  /// INFO级别日志 - 一般信息
  static void info(String message,
      {String? module, Map<String, dynamic>? data}) {
    _log(_levelInfo, 'INFO', message, module: module, data: data);
  }

  /// WARN级别日志 - 警告信息
  static void warn(String message,
      {String? module, Map<String, dynamic>? data}) {
    _log(_levelWarn, 'WARN', message, module: module, data: data);
  }

  /// ERROR级别日志 - 错误信息
  static void error(String message,
      {String? module,
      Map<String, dynamic>? data,
      dynamic exception,
      StackTrace? stackTrace}) {
    _log(_levelError, 'ERROR', message,
        module: module,
        data: data,
        exception: exception,
        stackTrace: stackTrace);
  }

  /// CRITICAL级别日志 - 严重错误
  static void critical(String message,
      {String? module,
      Map<String, dynamic>? data,
      dynamic exception,
      StackTrace? stackTrace}) {
    _log(_levelCritical, 'CRITICAL', message,
        module: module,
        data: data,
        exception: exception,
        stackTrace: stackTrace);
  }

  /// 内部日志记录方法
  static void _log(
    int level,
    String levelName,
    String message, {
    String? module,
    Map<String, dynamic>? data,
    dynamic exception,
    StackTrace? stackTrace,
  }) {
    final timestamp = DateTime.now().toIso8601String();
    final moduleStr = module ?? 'App';

    // 构建日志消息
    final logMessage = StringBuffer();
    logMessage.write('[$levelName] [$moduleStr] $message');

    // 添加数据信息
    if (data != null && data.isNotEmpty) {
      logMessage.write(' | Data: ${data.toString()}');
    }

    // 添加异常信息
    if (exception != null) {
      logMessage.write(' | Exception: $exception');
    }

    // 🔧 调试优化：分离控制台输出和IDE调试输出
    if (_debugMode) {
      // IDE调试器专用：使用原始print保证stackTrace正确显示
      if (level >= _levelError) {
        print('🔴 ERROR: $message');
        if (exception != null) print('Exception: $exception');
        if (stackTrace != null) print('StackTrace:\n$stackTrace');
      } else if (level >= _levelWarn) {
        print('🟡 WARN: $message');
      } else {
        print('🔵 [$moduleStr] $message');
      }
    }

    // 生产环境：使用developer.log
    developer.log(
      logMessage.toString(),
      time: DateTime.now(),
      level: level,
      name: '$_appName.$moduleStr',
      error: exception,
      stackTrace: stackTrace,
    );

    // 错误级别同时输出到stderr确保可见性
    if (level >= _levelError) {
      final consoleMessage = '[$timestamp] ${logMessage.toString()}';
      stderr.writeln(consoleMessage);
      if (stackTrace != null) {
        stderr.writeln('StackTrace:\n$stackTrace');
      }
    }
  }

  /// IPC相关日志
  static void ipcTrace(String message, {Map<String, dynamic>? data}) {
    trace(message, module: 'IPC', data: data);
  }

  static void ipcDebug(String message, {Map<String, dynamic>? data}) {
    debug(message, module: 'IPC', data: data);
  }

  static void ipcInfo(String message, {Map<String, dynamic>? data}) {
    info(message, module: 'IPC', data: data);
  }

  static void ipcWarn(String message, {Map<String, dynamic>? data}) {
    warn(message, module: 'IPC', data: data);
  }

  static void ipcError(String message,
      {Map<String, dynamic>? data, dynamic exception, StackTrace? stackTrace}) {
    error(message,
        module: 'IPC',
        data: data,
        exception: exception,
        stackTrace: stackTrace);
  }

  /// Daemon相关日志
  static void daemonTrace(String message, {Map<String, dynamic>? data}) {
    trace(message, module: 'Daemon', data: data);
  }

  static void daemonDebug(String message, {Map<String, dynamic>? data}) {
    debug(message, module: 'Daemon', data: data);
  }

  static void daemonInfo(String message, {Map<String, dynamic>? data}) {
    info(message, module: 'Daemon', data: data);
  }

  static void daemonWarn(String message, {Map<String, dynamic>? data}) {
    warn(message, module: 'Daemon', data: data);
  }

  static void daemonError(String message,
      {Map<String, dynamic>? data, dynamic exception, StackTrace? stackTrace}) {
    error(message,
        module: 'Daemon',
        data: data,
        exception: exception,
        stackTrace: stackTrace);
  }

  /// UI相关日志
  static void uiTrace(String message, {Map<String, dynamic>? data}) {
    trace(message, module: 'UI', data: data);
  }

  static void uiDebug(String message, {Map<String, dynamic>? data}) {
    debug(message, module: 'UI', data: data);
  }

  static void uiInfo(String message, {Map<String, dynamic>? data}) {
    info(message, module: 'UI', data: data);
  }

  static void uiWarn(String message, {Map<String, dynamic>? data}) {
    warn(message, module: 'UI', data: data);
  }

  static void uiError(String message,
      {Map<String, dynamic>? data, dynamic exception, StackTrace? stackTrace}) {
    error(message,
        module: 'UI', data: data, exception: exception, stackTrace: stackTrace);
  }
}

/// 异常处理工具类
class ErrorHandler {
  /// 处理并记录异常
  static void handleException(
    String context,
    dynamic exception, {
    StackTrace? stackTrace,
    String? module,
    Map<String, dynamic>? additionalData,
    bool critical = false,
  }) {
    final data = <String, dynamic>{
      'context': context,
      if (additionalData != null) ...additionalData,
    };

    if (critical) {
      AppLogger.critical(
        'Unhandled exception in $context',
        module: module,
        data: data,
        exception: exception,
        stackTrace: stackTrace ?? StackTrace.current,
      );
    } else {
      AppLogger.error(
        'Exception in $context',
        module: module,
        data: data,
        exception: exception,
        stackTrace: stackTrace ?? StackTrace.current,
      );
    }
  }

  /// 安全执行异步操作
  static Future<T?> safeAsync<T>(
    Future<T> Function() operation, {
    required String context,
    String? module,
    T? fallback,
    Map<String, dynamic>? additionalData,
  }) async {
    try {
      return await operation();
    } catch (e, stackTrace) {
      handleException(
        context,
        e,
        stackTrace: stackTrace,
        module: module,
        additionalData: additionalData,
      );
      return fallback;
    }
  }

  /// 安全执行同步操作
  static T? safeSync<T>(
    T Function() operation, {
    required String context,
    String? module,
    T? fallback,
    Map<String, dynamic>? additionalData,
  }) {
    try {
      return operation();
    } catch (e, stackTrace) {
      handleException(
        context,
        e,
        stackTrace: stackTrace,
        module: module,
        additionalData: additionalData,
      );
      return fallback;
    }
  }
}
