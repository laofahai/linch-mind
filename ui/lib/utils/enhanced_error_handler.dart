import 'dart:async';
import 'dart:collection';
import 'package:flutter/foundation.dart';
import 'package:rxdart/rxdart.dart';

import '../models/ui_error.dart';
import '../services/ipc_client.dart';
import 'app_logger.dart';

/// 增强的错误处理器 - 提供智能去重、限流和自动恢复
class EnhancedErrorHandler {
  // 单例模式
  static final _instance = EnhancedErrorHandler._internal();
  factory EnhancedErrorHandler() => _instance;
  EnhancedErrorHandler._internal();

  // 错误流（使用RxDart增强）
  final _errorSubject = PublishSubject<UIError>();

  // 去重缓存
  final _recentErrors = LinkedHashMap<String, DateTime>();
  static const _dedupeWindowSeconds = 5;
  static const _maxCacheSize = 20;

  // 自动恢复管理
  final _recoveryManager = RecoveryManager();

  // 公开的错误流（经过去重和限流）
  Stream<UIError> get errorStream => _errorSubject
      .distinct((a, b) => _isDuplicate(a, b)) // 去重
      .throttleTime(const Duration(seconds: 1)); // 限流

  /// 处理IPC错误
  void handleIPCError(
    Map<String, dynamic> errorData, {
    required String operation,
    StackTrace? stackTrace,
    VoidCallback? retryCallback,
  }) {
    final error = UIError.fromIPCError(
      errorData: errorData,
      operation: operation,
      stackTrace: kDebugMode ? stackTrace : null,
      retryCallback: retryCallback,
    );

    // 检查是否可自动恢复
    if (error.isRecoverable && _recoveryManager.canRecover(error)) {
      _recoveryManager.attemptRecovery(error);
      return;
    }

    // 添加到错误流
    _addError(error);
  }

  /// 处理Flutter错误
  void handleFlutterError(FlutterErrorDetails details) {
    if (kDebugMode) {
      // 开发模式：详细输出到控制台
      _printDebugError(UIError.fromException(
        exception: details.exception,
        operation: 'Flutter Framework',
        stackTrace: details.stack,
      ));
      
      // 同时使用Flutter默认处理器确保IDE能看到
      FlutterError.presentError(details);
    } else {
      // 生产模式：静默处理
      final error = UIError.fromException(
        exception: details.exception,
        operation: 'Flutter Framework',
        stackTrace: details.stack,
      );
      _addError(error);
    }
  }

  /// 处理一般异常
  void handleException(
    dynamic exception, {
    required String operation,
    StackTrace? stackTrace,
    VoidCallback? retryCallback,
  }) {
    final error = UIError.fromException(
      exception: exception,
      operation: operation,
      stackTrace: stackTrace,
      retryCallback: retryCallback,
    );

    // 开发模式直接打印到控制台
    if (kDebugMode) {
      _printDebugError(error);
    }

    _addError(error);
  }

  /// 安全执行异步操作
  Future<T?> safeAsync<T>(
    Future<T> Function() operation, {
    required String context,
    T? fallback,
    int maxRetries = 3,
    VoidCallback? retryCallback,
  }) async {
    int attempts = 0;

    while (attempts < maxRetries) {
      try {
        return await operation();
      } catch (e, stackTrace) {
        attempts++;

        if (attempts >= maxRetries) {
          final error = UIError.fromException(
            exception: e,
            operation: context,
            stackTrace: stackTrace,
            retryCallback: retryCallback,
          );

          // 开发模式打印详细信息
          if (kDebugMode) {
            _printDebugError(error);
          }

          _addError(error);
          return fallback;
        }

        // 指数退避
        await Future.delayed(Duration(seconds: attempts * attempts));
      }
    }

    return fallback;
  }

  /// 安全执行同步操作
  T? safeSync<T>(
    T Function() operation, {
    required String context,
    T? fallback,
    VoidCallback? retryCallback,
  }) {
    try {
      return operation();
    } catch (e, stackTrace) {
      final error = UIError.fromException(
        exception: e,
        operation: context,
        stackTrace: stackTrace,
        retryCallback: retryCallback,
      );

      // 开发模式打印详细信息
      if (kDebugMode) {
        _printDebugError(error);
      }

      _addError(error);
      return fallback;
    }
  }

  void _addError(UIError error) {
    // 去重检查
    final signature = error.signature;
    final now = DateTime.now();

    if (_recentErrors.containsKey(signature)) {
      final lastOccurrence = _recentErrors[signature]!;
      if (now.difference(lastOccurrence).inSeconds < _dedupeWindowSeconds) {
        // 重复错误，忽略
        return;
      }
    }

    // 更新缓存
    _recentErrors[signature] = now;

    // 限制缓存大小
    if (_recentErrors.length > _maxCacheSize) {
      _recentErrors.remove(_recentErrors.keys.first);
    }

    // 发送到流
    _errorSubject.add(error);

    // 记录到日志系统
    AppLogger.error(
      'UI Error: ${error.message}',
      module: 'ErrorHandler',
      data: {
        'error_id': error.errorId,
        'code': error.code,
        'operation': error.operation,
        'is_recoverable': error.isRecoverable,
        'can_retry': error.canRetry,
      },
      exception: error.message,
      stackTrace: error.stackTrace != null 
          ? StackTrace.fromString(error.stackTrace!) 
          : null,
    );
  }

  bool _isDuplicate(UIError a, UIError b) {
    return a.signature == b.signature;
  }

  void _printDebugError(UIError error) {
    final buffer = StringBuffer();
    buffer.writeln('╔════════════════════════════════════════════════════════════');
    buffer.writeln('║ 🔴 ERROR: ${error.operation}');
    buffer.writeln('║ ID: ${error.errorId}');
    buffer.writeln('║ Code: ${error.code}');
    buffer.writeln('║ Message: ${error.message}');
    buffer.writeln('║ Time: ${error.timestamp}');
    buffer.writeln('║ Type: ${error.typeDescription}');

    if (error.canRetry) {
      buffer.writeln('║ Retry: Available${error.retryAfter != null ? ' (after ${error.retryAfter}s)' : ''}');
    }

    if (error.isRecoverable) {
      buffer.writeln('║ Recovery: ${error.suggestedAction}');
    }

    if (error.stackTrace != null && kDebugMode) {
      buffer.writeln('║ Stack Trace:');
      final lines = error.stackTrace!.split('\n');
      for (int i = 0; i < lines.length && i < 10; i++) {
        buffer.writeln('║   ${lines[i]}');
      }
      if (lines.length > 10) {
        buffer.writeln('║   ... (${lines.length - 10} more lines)');
      }
    }

    buffer.writeln('╚════════════════════════════════════════════════════════════');
    
    // 使用print确保在所有平台都能看到
    debugPrint(buffer.toString());
  }

  void dispose() {
    _errorSubject.close();
    _recoveryManager.dispose();
  }
}

/// 自动恢复管理器
class RecoveryManager {
  final Map<String, Timer> _recoveryTimers = {};
  final Map<String, int> _recoveryAttempts = {};
  static const _maxRecoveryAttempts = 3;

  bool canRecover(UIError error) {
    if (!error.isRecoverable) return false;

    final attempts = _recoveryAttempts[error.code] ?? 0;
    return attempts < _maxRecoveryAttempts;
  }

  void attemptRecovery(UIError error) {
    final attempts = (_recoveryAttempts[error.code] ?? 0) + 1;
    _recoveryAttempts[error.code] = attempts;

    // 计算退避延迟
    final delay = Duration(seconds: attempts * 2);

    // 取消之前的定时器
    _recoveryTimers[error.code]?.cancel();

    // 设置新的恢复定时器
    _recoveryTimers[error.code] = Timer(delay, () {
      _performRecovery(error);
    });

    if (kDebugMode) {
      debugPrint('⚡ Auto-recovery scheduled for ${error.code} in ${delay.inSeconds}s (attempt $attempts)');
    }
  }

  void _performRecovery(UIError error) {
    // 根据错误类型执行恢复操作
    switch (error.code) {
      case 'IPC_CONNECTION_FAILED':
      case 'CONNECTION_FAILED':
        // 重新连接IPC
        IPCService.instance.connect();
        break;
      case 'IPC_AUTH_FAILED':
      case 'AUTH_FAILED':
        // 重新认证：先断开再重连
        IPCService.instance.disconnect().then((_) {
          IPCService.instance.connect();
        });
        break;
      default:
        // 通用恢复：触发重试
        if (error.retryCallback != null) {
          error.retryCallback!();
        }
    }

    if (kDebugMode) {
      debugPrint('🔄 Recovery attempted for ${error.code}');
    }
  }

  void dispose() {
    for (final timer in _recoveryTimers.values) {
      timer.cancel();
    }
    _recoveryTimers.clear();
    _recoveryAttempts.clear();
  }
}