import 'package:flutter/foundation.dart';

/// 调试辅助工具类 - 专门用于IDEA/PyCharm调试优化
class DebugHelper {
  /// 断点友好的错误记录
  /// 在IDEA中设置断点时，这个方法会暂停执行
  static void debugBreakpoint(String message, {dynamic data}) {
    if (kDebugMode) {
      // 这行专门用于设置断点
      print('🔴 BREAKPOINT: $message'); // <-- 在这里设置断点
      if (data != null) {
        print('Data: $data');
      }
    }
  }

  /// 简化的错误打印，保持原始堆栈跟踪
  static void simpleError(String message, dynamic error, StackTrace? stackTrace) {
    if (kDebugMode) {
      print('🔴 ERROR: $message');
      print('Exception: $error');
      if (stackTrace != null) {
        print('StackTrace:');
        print(stackTrace.toString());
      }
    }
  }

  /// IPC通信调试专用
  static void ipcDebug(String operation, {dynamic request, dynamic response, dynamic error}) {
    if (kDebugMode) {
      print('📡 IPC [$operation]');
      if (request != null) print('  Request: $request');
      if (response != null) print('  Response: $response');
      if (error != null) {
        print('  🔴 Error: $error');
        debugBreakpoint('IPC Error in $operation', data: error);
      }
    }
  }

  /// Widget生命周期调试
  static void widgetLifecycle(String widgetName, String event, {dynamic data}) {
    if (kDebugMode) {
      print('🎨 WIDGET [$widgetName] $event');
      if (data != null) print('  Data: $data');
    }
  }

  /// Provider状态变更调试
  static void providerState(String providerName, String event, {dynamic oldState, dynamic newState}) {
    if (kDebugMode) {
      print('🔄 PROVIDER [$providerName] $event');
      if (oldState != null) print('  Old: $oldState');
      if (newState != null) print('  New: $newState');
    }
  }
}

/// 快捷调试宏
void debugBreak(String message, {dynamic data}) => DebugHelper.debugBreakpoint(message, data: data);
void debugError(String message, dynamic error, [StackTrace? stackTrace]) => DebugHelper.simpleError(message, error, stackTrace);
void debugIPC(String operation, {dynamic request, dynamic response, dynamic error}) => DebugHelper.ipcDebug(operation, request: request, response: response, error: error);