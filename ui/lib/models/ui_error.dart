import 'package:flutter/foundation.dart';

/// UI错误模型 - 用于统一的错误处理和显示
class UIError {
  final String errorId;
  final String code;
  final String message;
  final String operation;
  final DateTime timestamp;
  final bool isRecoverable;
  final bool canRetry;
  final int? retryAfter;
  final String? stackTrace;
  final VoidCallback? retryCallback;

  UIError({
    required this.errorId,
    required this.code,
    required this.message,
    required this.operation,
    required this.timestamp,
    required this.isRecoverable,
    required this.canRetry,
    this.retryAfter,
    this.stackTrace,
    this.retryCallback,
  });

  /// 从IPC错误数据创建UIError
  factory UIError.fromIPCError({
    required Map<String, dynamic> errorData,
    required String operation,
    StackTrace? stackTrace,
    VoidCallback? retryCallback,
  }) {
    // 处理嵌套的details结构
    final details = errorData['details'] as Map<String, dynamic>? ?? {};
    
    return UIError(
      errorId: details['error_id'] ?? errorData['error_id'] ?? 'unknown',
      code: errorData['code'] ?? 'UNKNOWN_ERROR',
      message: errorData['message'] ?? 'Unknown error',
      operation: operation,
      timestamp: DateTime.now(),
      isRecoverable: details['is_recoverable'] ?? errorData['is_recoverable'] ?? false,
      canRetry: details['can_retry'] ?? errorData['can_retry'] ?? false,
      retryAfter: details['retry_after'] ?? errorData['retry_after'],
      stackTrace: kDebugMode ? stackTrace?.toString() : null,
      retryCallback: retryCallback,
    );
  }

  /// 从Flutter异常创建UIError
  factory UIError.fromException({
    required dynamic exception,
    required String operation,
    StackTrace? stackTrace,
    VoidCallback? retryCallback,
  }) {
    return UIError(
      errorId: 'flutter_${DateTime.now().millisecondsSinceEpoch}',
      code: 'FLUTTER_ERROR',
      message: exception.toString(),
      operation: operation,
      timestamp: DateTime.now(),
      isRecoverable: false,
      canRetry: false,
      stackTrace: kDebugMode ? stackTrace?.toString() : null,
      retryCallback: retryCallback,
    );
  }

  /// 错误签名（用于去重）
  String get signature => '$code:$operation';

  /// 是否为网络相关错误
  bool get isNetworkError =>
      code.contains('CONNECTION') ||
      code.contains('TIMEOUT') ||
      code.contains('NETWORK') ||
      code.contains('IPC');

  /// 是否为认证错误
  bool get isAuthError => 
      code.contains('AUTH') || 
      code.contains('PERMISSION');

  /// 是否为严重错误
  bool get isCritical =>
      code.contains('CRITICAL') ||
      code.contains('FATAL') ||
      code.contains('FLUTTER_ERROR');

  /// 是否为用户输入错误
  bool get isInputError =>
      code.contains('VALIDATION') ||
      code.contains('INVALID_PARAMETER') ||
      code.contains('MISSING_PARAMETER');

  /// 是否为系统配置错误  
  bool get isConfigError =>
      code.contains('CONFIGURATION') ||
      code.contains('CONFIG');

  /// 获取错误类型的用户友好描述
  String get typeDescription {
    if (isNetworkError) return '网络连接';
    if (isAuthError) return '身份验证';
    if (isCritical) return '严重错误';
    if (isInputError) return '输入错误';
    if (isConfigError) return '配置错误';
    return '系统错误';
  }

  /// 获取建议的用户操作
  String get suggestedAction {
    if (isNetworkError && canRetry) return '检查网络连接，然后重试';
    if (isAuthError) return '请重新登录';
    if (isInputError) return '请检查输入内容';
    if (isConfigError) return '请检查系统配置';
    if (canRetry) return '稍后重试';
    return '请联系技术支持';
  }

  @override
  String toString() {
    return 'UIError(id: $errorId, code: $code, message: $message, operation: $operation)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is UIError && other.signature == signature;
  }

  @override
  int get hashCode => signature.hashCode;
}