import 'dart:async';
import 'app_logger.dart';

/// 全局错误监控器
/// 负责监控应用中的关键错误和异常，提供实时诊断能力
class ErrorMonitor {
  static final ErrorMonitor _instance = ErrorMonitor._internal();
  factory ErrorMonitor() => _instance;
  ErrorMonitor._internal();

  final StreamController<ErrorReport> _errorStreamController = 
      StreamController<ErrorReport>.broadcast();
  
  Stream<ErrorReport> get errorStream => _errorStreamController.stream;
  
  final List<ErrorReport> _errorHistory = [];
  int _maxHistorySize = 100;
  
  /// 报告错误
  void reportError(ErrorReport report) {
    // 记录到历史
    _errorHistory.add(report);
    if (_errorHistory.length > _maxHistorySize) {
      _errorHistory.removeAt(0);
    }
    
    // 根据严重程度记录日志
    switch (report.severity) {
      case ErrorSeverity.low:
        AppLogger.info(report.message, 
          module: report.module, 
          data: report.context
        );
        break;
      case ErrorSeverity.medium:
        AppLogger.warn(report.message, 
          module: report.module, 
          data: report.context
        );
        break;
      case ErrorSeverity.high:
        AppLogger.error(report.message, 
          module: report.module, 
          data: report.context,
          exception: report.exception,
          stackTrace: report.stackTrace
        );
        break;
      case ErrorSeverity.critical:
        AppLogger.critical(report.message, 
          module: report.module, 
          data: report.context,
          exception: report.exception,
          stackTrace: report.stackTrace
        );
        break;
    }
    
    // 发送到流
    _errorStreamController.add(report);
  }
  
  /// 获取最近的错误
  List<ErrorReport> getRecentErrors({int? limit}) {
    if (limit == null) return List.from(_errorHistory);
    return _errorHistory.take(limit).toList();
  }
  
  /// 获取特定模块的错误
  List<ErrorReport> getErrorsByModule(String module, {int? limit}) {
    final filtered = _errorHistory.where((e) => e.module == module).toList();
    if (limit == null) return filtered;
    return filtered.take(limit).toList();
  }
  
  /// 获取特定严重程度的错误
  List<ErrorReport> getErrorsBySeverity(ErrorSeverity severity, {int? limit}) {
    final filtered = _errorHistory.where((e) => e.severity == severity).toList();
    if (limit == null) return filtered;
    return filtered.take(limit).toList();
  }
  
  /// 清除错误历史
  void clearHistory() {
    _errorHistory.clear();
  }
  
  /// 设置历史记录最大大小
  void setMaxHistorySize(int size) {
    _maxHistorySize = size;
    if (_errorHistory.length > size) {
      _errorHistory.removeRange(0, _errorHistory.length - size);
    }
  }
  
  /// 检查是否有关键错误
  bool hasCriticalErrors({Duration? within}) {
    if (within == null) {
      return _errorHistory.any((e) => e.severity == ErrorSeverity.critical);
    }
    
    final cutoff = DateTime.now().subtract(within);
    return _errorHistory.any((e) => 
      e.severity == ErrorSeverity.critical && 
      e.timestamp.isAfter(cutoff)
    );
  }
  
  /// 获取错误统计
  ErrorStats getStats({Duration? within}) {
    List<ErrorReport> relevantErrors = _errorHistory;
    
    if (within != null) {
      final cutoff = DateTime.now().subtract(within);
      relevantErrors = _errorHistory
          .where((e) => e.timestamp.isAfter(cutoff))
          .toList();
    }
    
    final stats = ErrorStats();
    for (final error in relevantErrors) {
      stats.totalCount++;
      switch (error.severity) {
        case ErrorSeverity.low:
          stats.lowCount++;
          break;
        case ErrorSeverity.medium:
          stats.mediumCount++;
          break;
        case ErrorSeverity.high:
          stats.highCount++;
          break;
        case ErrorSeverity.critical:
          stats.criticalCount++;
          break;
      }
    }
    
    return stats;
  }
  
  void dispose() {
    _errorStreamController.close();
  }
}

/// 错误严重程度
enum ErrorSeverity {
  low,      // 信息性质，不影响功能
  medium,   // 警告，可能影响用户体验
  high,     // 错误，影响功能但不致命
  critical, // 严重错误，可能导致应用崩溃
}

/// 错误报告
class ErrorReport {
  final String message;
  final String module;
  final ErrorSeverity severity;
  final DateTime timestamp;
  final Map<String, dynamic>? context;
  final dynamic exception;
  final StackTrace? stackTrace;
  final String? userId; // 用于多用户场景
  
  ErrorReport({
    required this.message,
    required this.module,
    required this.severity,
    DateTime? timestamp,
    this.context,
    this.exception,
    this.stackTrace,
    this.userId,
  }) : timestamp = timestamp ?? DateTime.now();
  
  Map<String, dynamic> toJson() {
    return {
      'message': message,
      'module': module,
      'severity': severity.toString(),
      'timestamp': timestamp.toIso8601String(),
      'context': context,
      'exception': exception?.toString(),
      'hasStackTrace': stackTrace != null,
      'userId': userId,
    };
  }
}

/// 错误统计
class ErrorStats {
  int totalCount = 0;
  int lowCount = 0;
  int mediumCount = 0;
  int highCount = 0;
  int criticalCount = 0;
  
  double get criticalRate => totalCount == 0 ? 0.0 : criticalCount / totalCount;
  double get highRate => totalCount == 0 ? 0.0 : highCount / totalCount;
  bool get hasIssues => criticalCount > 0 || highCount > 0;
  
  Map<String, dynamic> toJson() {
    return {
      'totalCount': totalCount,
      'lowCount': lowCount,
      'mediumCount': mediumCount,
      'highCount': highCount,
      'criticalCount': criticalCount,
      'criticalRate': criticalRate,
      'highRate': highRate,
      'hasIssues': hasIssues,
    };
  }
}

/// 便捷的错误报告工具类
class AppErrorReporter {
  static final _monitor = ErrorMonitor();
  
  /// 报告信息
  static void info(String message, {String? module, Map<String, dynamic>? context}) {
    _monitor.reportError(ErrorReport(
      message: message,
      module: module ?? 'Unknown',
      severity: ErrorSeverity.low,
      context: context,
    ));
  }
  
  /// 报告警告
  static void warn(String message, {String? module, Map<String, dynamic>? context}) {
    _monitor.reportError(ErrorReport(
      message: message,
      module: module ?? 'Unknown',
      severity: ErrorSeverity.medium,
      context: context,
    ));
  }
  
  /// 报告错误
  static void error(String message, {
    String? module, 
    Map<String, dynamic>? context,
    dynamic exception,
    StackTrace? stackTrace,
  }) {
    _monitor.reportError(ErrorReport(
      message: message,
      module: module ?? 'Unknown',
      severity: ErrorSeverity.high,
      context: context,
      exception: exception,
      stackTrace: stackTrace ?? StackTrace.current,
    ));
  }
  
  /// 报告严重错误
  static void critical(String message, {
    String? module, 
    Map<String, dynamic>? context,
    dynamic exception,
    StackTrace? stackTrace,
  }) {
    _monitor.reportError(ErrorReport(
      message: message,
      module: module ?? 'Unknown',
      severity: ErrorSeverity.critical,
      context: context,
      exception: exception,
      stackTrace: stackTrace ?? StackTrace.current,
    ));
  }
  
  /// 获取错误监控器实例
  static ErrorMonitor get monitor => _monitor;
}