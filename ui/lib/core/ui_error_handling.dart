/// UI错误处理框架 - 极简设计
/// 对标daemon/core/error_handling.py
/// 统一UI层错误处理模式
library;

import 'dart:async';
import 'dart:developer' as developer;

/// UI错误严重级别
enum UIErrorSeverity { low, medium, high, critical }

/// UI错误分类
enum UIErrorCategory { 
  ipcCommunication,
  dataProcessing, 
  uiRendering,
  serviceUnavailable,
}

/// UI错误处理装饰器
/// 
/// 使用示例:
/// ```dart
/// @UIErrorHandler(
///   severity: UIErrorSeverity.high,
///   category: UIErrorCategory.ipc_communication,
/// )
/// Future<void> connectToService() async {
///   // 业务逻辑
/// }
/// ```
class UIErrorHandler {
  final UIErrorSeverity severity;
  final UIErrorCategory category;
  final String? userMessage;
  
  const UIErrorHandler({
    required this.severity,
    required this.category,
    this.userMessage,
  });
}

/// 错误处理工具函数
Future<T> handleUIErrors<T>(
  Future<T> Function() operation, {
  UIErrorSeverity severity = UIErrorSeverity.medium,
  UIErrorCategory category = UIErrorCategory.dataProcessing,
  String? userMessage,
}) async {
  try {
    return await operation();
  } catch (e, stackTrace) {
    final errorMsg = userMessage ?? '操作失败: $e';
    
    // 简单日志记录
    developer.log(
      '❌ UI错误[${severity.name}][${category.name}]: $errorMsg',
      name: 'UIErrorHandler',
      error: e,
      stackTrace: stackTrace,
    );
    
    // 重新抛出，让调用者决定如何处理
    rethrow;
  }
}

/// 同步版本错误处理
T handleUIErrorsSync<T>(
  T Function() operation, {
  UIErrorSeverity severity = UIErrorSeverity.medium,
  UIErrorCategory category = UIErrorCategory.dataProcessing,
  String? userMessage,
}) {
  try {
    return operation();
  } catch (e, stackTrace) {
    final errorMsg = userMessage ?? '操作失败: $e';
    
    developer.log(
      '❌ UI错误[${severity.name}][${category.name}]: $errorMsg',
      name: 'UIErrorHandler',
      error: e,
      stackTrace: stackTrace,
    );
    
    rethrow;
  }
}