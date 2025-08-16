import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/ui_error.dart';
import '../utils/enhanced_error_handler.dart';
import '../services/ipc_client.dart';
import '../core/ui_service_facade.dart';

/// 应用错误状态
class AppErrorState {
  final List<UIError> activeErrors;
  final Map<String, int> errorCounts;
  final bool hasNetwork;
  final bool hasIPC;
  final bool hasCritical;
  final DateTime lastUpdated;

  const AppErrorState({
    this.activeErrors = const [],
    this.errorCounts = const {},
    this.hasNetwork = false,
    this.hasIPC = false,
    this.hasCritical = false,
    required this.lastUpdated,
  });

  AppErrorState copyWith({
    List<UIError>? activeErrors,
    Map<String, int>? errorCounts,
    bool? hasNetwork,
    bool? hasIPC,
    bool? hasCritical,
    DateTime? lastUpdated,
  }) {
    return AppErrorState(
      activeErrors: activeErrors ?? this.activeErrors,
      errorCounts: errorCounts ?? this.errorCounts,
      hasNetwork: hasNetwork ?? this.hasNetwork,
      hasIPC: hasIPC ?? this.hasIPC,
      hasCritical: hasCritical ?? this.hasCritical,
      lastUpdated: lastUpdated ?? this.lastUpdated,
    );
  }

  bool get hasErrors => activeErrors.isNotEmpty;
  bool get hasRecoverableErrors =>
      activeErrors.any((error) => error.isRecoverable);
  bool get canRetryAny => activeErrors.any((error) => error.canRetry);

  /// 获取最高优先级的错误
  UIError? get primaryError {
    if (activeErrors.isEmpty) return null;

    // 优先级：严重 > 网络 > 认证 > 其他
    for (final error in activeErrors) {
      if (error.isCritical) return error;
    }
    for (final error in activeErrors) {
      if (error.isNetworkError) return error;
    }
    for (final error in activeErrors) {
      if (error.isAuthError) return error;
    }
    return activeErrors.first;
  }
}

/// 应用错误监控管理器
class AppErrorNotifier extends StateNotifier<AppErrorState> {
  AppErrorNotifier() : super(AppErrorState(lastUpdated: DateTime.now())) {
    _init();
  }

  final _errorHandler = EnhancedErrorHandler();
  final _activeErrors = <String, UIError>{};
  final _errorCounts = <String, int>{};

  StreamSubscription<UIError>? _errorSubscription;
  Timer? _cleanupTimer;

  void _init() {
    // 监听错误流
    _errorSubscription = _errorHandler.errorStream.listen(_onNewError);

    // 定期清理过期错误
    _cleanupTimer = Timer.periodic(
      const Duration(seconds: 30),
      (_) => _cleanupExpiredErrors(),
    );
  }

  void _onNewError(UIError error) {
    // 更新活跃错误列表
    _activeErrors[error.signature] = error;

    // 更新错误计数
    _errorCounts[error.typeDescription] =
        (_errorCounts[error.typeDescription] ?? 0) + 1;

    // 限制活跃错误数量
    if (_activeErrors.length > 10) {
      final firstKey = _activeErrors.keys.first;
      _activeErrors.remove(firstKey);
    }

    _updateState();
  }

  void _cleanupExpiredErrors() {
    final now = DateTime.now();
    final expiredKeys = <String>[];

    for (final entry in _activeErrors.entries) {
      final error = entry.value;
      final age = now.difference(error.timestamp);

      // 非严重错误5分钟后过期
      if (!error.isCritical && age.inMinutes > 5) {
        expiredKeys.add(entry.key);
      }
      // 严重错误30分钟后过期
      else if (error.isCritical && age.inMinutes > 30) {
        expiredKeys.add(entry.key);
      }
    }

    for (final key in expiredKeys) {
      _activeErrors.remove(key);
    }

    if (expiredKeys.isNotEmpty) {
      _updateState();
    }
  }

  void _updateState() {
    final errors = _activeErrors.values.toList();

    state = state.copyWith(
      activeErrors: errors,
      errorCounts: Map.from(_errorCounts),
      hasNetwork: errors.any((e) => e.isNetworkError),
      hasIPC: errors.any((e) => e.code.contains('IPC')),
      hasCritical: errors.any((e) => e.isCritical),
      lastUpdated: DateTime.now(),
    );
  }

  /// 手动添加错误
  void addError(UIError error) {
    _onNewError(error);
  }

  /// 处理IPC错误
  void handleIPCError(
    Map<String, dynamic> errorData, {
    required String operation,
    VoidCallback? retryCallback,
  }) {
    _errorHandler.handleIPCError(
      errorData,
      operation: operation,
      retryCallback: retryCallback,
    );
  }

  /// 处理异常
  void handleException(
    dynamic exception, {
    required String operation,
    StackTrace? stackTrace,
    VoidCallback? retryCallback,
  }) {
    _errorHandler.handleException(
      exception,
      operation: operation,
      stackTrace: stackTrace,
      retryCallback: retryCallback,
    );
  }

  /// 清除指定错误
  void clearError(String signature) {
    if (_activeErrors.remove(signature) != null) {
      _updateState();
    }
  }

  /// 清除所有错误
  void clearAllErrors() {
    _activeErrors.clear();
    _updateState();
  }

  /// 重试所有可重试的错误
  void retryAllErrors() {
    final retryableErrors = _activeErrors.values
        .where((error) => error.canRetry && error.retryCallback != null);

    for (final error in retryableErrors) {
      error.retryCallback?.call();
      _activeErrors.remove(error.signature);
    }

    if (retryableErrors.isNotEmpty) {
      _updateState();
    }
  }

  @override
  void dispose() {
    _errorSubscription?.cancel();
    _cleanupTimer?.cancel();
    super.dispose();
  }
}

/// 提供应用错误状态的Provider
final appErrorProvider = StateNotifierProvider<AppErrorNotifier, AppErrorState>(
  (ref) => AppErrorNotifier(),
);

/// 用于监控和处理IPC连接状态的Provider
final ipcConnectionProvider = StreamProvider<bool>((ref) {
  return getService<IPCClient>()
      .connectionStream
      .map((status) =>
          status == ConnectionStatus.connected ||
          status == ConnectionStatus.authenticated)
      .handleError((error) {
    // IPC连接错误自动添加到错误管理器
    ref.read(appErrorProvider.notifier).handleException(
          error,
          operation: 'IPC连接监控',
          retryCallback: () => getService<IPCClient>().connect(),
        );
    return false;
  });
});

/// 提供主要错误信息的Provider
final primaryErrorProvider = Provider<UIError?>((ref) {
  final errorState = ref.watch(appErrorProvider);
  return errorState.primaryError;
});

/// 提供错误统计信息的Provider
final errorStatsProvider = Provider<Map<String, dynamic>>((ref) {
  final errorState = ref.watch(appErrorProvider);
  return {
    'total_errors': errorState.activeErrors.length,
    'critical_errors':
        errorState.activeErrors.where((e) => e.isCritical).length,
    'network_errors':
        errorState.activeErrors.where((e) => e.isNetworkError).length,
    'recoverable_errors':
        errorState.activeErrors.where((e) => e.isRecoverable).length,
    'error_types': errorState.errorCounts,
    'has_connectivity_issues': errorState.hasNetwork || errorState.hasIPC,
  };
});
