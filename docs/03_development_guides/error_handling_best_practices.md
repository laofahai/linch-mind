# 错误处理架构最佳实践方案 v2.0

## 概述

基于深入评估和业界最佳实践，本方案提供一个**安全、健壮、高性能**的错误处理架构。

## 核心原则

1. **安全第一**：生产环境绝不暴露敏感信息
2. **用户友好**：提供清晰、可操作的错误提示
3. **自动恢复**：尽可能自动处理可恢复错误
4. **性能优化**：防止错误风暴影响系统性能
5. **可追溯性**：每个错误都可追踪和分析

## 架构设计

### 1. 分层错误处理

```
┌─────────────────────────────────────────┐
│            Flutter UI层                 │
│  - 友好错误展示                          │
│  - 重试机制                             │
│  - 错误去重/限流                         │
├─────────────────────────────────────────┤
│            IPC传输层                     │
│  - 错误ID生成                           │
│  - 安全信息过滤                          │
│  - 请求追踪                             │
├─────────────────────────────────────────┤
│          Python Daemon层                 │
│  - 详细日志记录                          │
│  - 错误聚合                             │
│  - 监控指标收集                          │
└─────────────────────────────────────────┘
```

### 2. 错误信息流

```
异常发生 → 后端捕获 → 生成ErrorID → 记录详情到日志 → 返回安全响应 → UI展示
```

## 详细实现

### 1. 后端错误处理（Python）

#### 1.1 增强错误处理框架
```python
# daemon/core/error_handling.py

import uuid
import hashlib
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime, timedelta

@dataclass
class ProcessedError:
    """处理后的错误信息"""
    error_id: str
    code: str
    message: str
    user_message: str
    is_recoverable: bool
    can_retry: bool
    retry_after: Optional[int] = None  # 重试延迟（秒）
    context: Optional[Dict[str, Any]] = None
    
    def to_safe_dict(self) -> Dict[str, Any]:
        """转换为安全的字典（用于IPC传输）"""
        return {
            "error_id": self.error_id,
            "code": self.code,
            "message": self.user_message,  # 只返回用户友好消息
            "is_recoverable": self.is_recoverable,
            "can_retry": self.can_retry,
            "retry_after": self.retry_after,
            # 不包含敏感的context信息
        }

class EnhancedErrorHandler(ErrorHandler):
    """增强的错误处理器"""
    
    def __init__(self):
        super().__init__()
        self._error_log_buffer = deque(maxlen=1000)  # 错误日志缓冲
        self._error_signatures = {}  # 错误签名缓存
        self._rate_limiter = ErrorRateLimiter()
        
    def process_error(
        self,
        exception: Exception,
        context: ErrorContext,
        request_id: Optional[str] = None
    ) -> ProcessedError:
        """处理错误并返回安全的错误信息"""
        
        # 生成唯一错误ID
        error_id = str(uuid.uuid4())
        
        # 生成错误签名（用于去重）
        signature = self._generate_signature(exception, context)
        
        # 检查是否需要限流
        if self._rate_limiter.should_throttle(signature):
            # 返回限流错误
            return ProcessedError(
                error_id=error_id,
                code="ERROR_THROTTLED",
                message="Too many errors",
                user_message="系统繁忙，请稍后重试",
                is_recoverable=True,
                can_retry=True,
                retry_after=5
            )
        
        # 记录详细错误信息到日志
        self._log_detailed_error(
            error_id=error_id,
            exception=exception,
            context=context,
            request_id=request_id
        )
        
        # 创建安全的错误响应
        processed = ProcessedError(
            error_id=error_id,
            code=self._get_error_code(exception, context),
            message=str(exception),  # 内部消息
            user_message=self._get_user_message(exception, context),
            is_recoverable=self._is_recoverable(exception, context),
            can_retry=self._can_retry(exception, context),
            retry_after=self._get_retry_delay(exception, context),
            context={"request_id": request_id} if request_id else None
        )
        
        # 缓存错误信息
        self._error_log_buffer.append({
            "error_id": error_id,
            "timestamp": datetime.now().isoformat(),
            "signature": signature,
            "code": processed.code
        })
        
        return processed
    
    def _generate_signature(self, exception: Exception, context: ErrorContext) -> str:
        """生成错误签名用于去重"""
        content = f"{context.category.value}:{type(exception).__name__}:{context.function_name}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_user_message(self, exception: Exception, context: ErrorContext) -> str:
        """获取用户友好的错误消息"""
        messages = {
            ErrorCategory.IPC_COMMUNICATION: "连接出现问题，正在重试",
            ErrorCategory.DATABASE_OPERATION: "数据操作失败，请稍后重试",
            ErrorCategory.CONNECTOR_MANAGEMENT: "连接器操作失败",
            ErrorCategory.CONFIGURATION: "配置错误，请检查设置",
            ErrorCategory.SECURITY: "安全验证失败",
            ErrorCategory.NETWORK: "网络连接异常",
        }
        return messages.get(context.category, "操作失败，请稍后重试")
    
    def _is_recoverable(self, exception: Exception, context: ErrorContext) -> bool:
        """判断错误是否可恢复"""
        recoverable_categories = {
            ErrorCategory.IPC_COMMUNICATION,
            ErrorCategory.NETWORK,
            ErrorCategory.DATABASE_OPERATION,
        }
        return context.category in recoverable_categories
    
    def _can_retry(self, exception: Exception, context: ErrorContext) -> bool:
        """判断是否可以重试"""
        non_retryable = {
            ErrorCategory.CONFIGURATION,
            ErrorCategory.SECURITY,
        }
        return context.category not in non_retryable
    
    def _get_retry_delay(self, exception: Exception, context: ErrorContext) -> Optional[int]:
        """获取重试延迟（秒）"""
        if not self._can_retry(exception, context):
            return None
        
        # 根据错误类型返回不同的延迟
        delays = {
            ErrorCategory.IPC_COMMUNICATION: 1,
            ErrorCategory.NETWORK: 3,
            ErrorCategory.DATABASE_OPERATION: 2,
        }
        return delays.get(context.category, 5)
    
    def _log_detailed_error(
        self,
        error_id: str,
        exception: Exception,
        context: ErrorContext,
        request_id: Optional[str]
    ):
        """记录详细错误信息（仅在后端）"""
        import traceback
        
        detailed_log = {
            "error_id": error_id,
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "context": context.to_dict(),
            "exception": {
                "type": type(exception).__name__,
                "message": str(exception),
                "traceback": traceback.format_exc()
            },
            "system": {
                "python_version": sys.version,
                "platform": platform.platform()
            }
        }
        
        # 记录到结构化日志
        self.logger.error(f"Error {error_id}", extra={"structured": detailed_log})
        
        # TODO: 集成到外部日志系统（Sentry/Datadog/ELK）
        # self._send_to_monitoring(detailed_log)

class ErrorRateLimiter:
    """错误限流器"""
    
    def __init__(self, max_errors_per_minute: int = 10):
        self.max_errors = max_errors_per_minute
        self.error_counts: Dict[str, deque] = {}
        
    def should_throttle(self, signature: str) -> bool:
        """检查是否需要限流"""
        now = time.time()
        minute_ago = now - 60
        
        if signature not in self.error_counts:
            self.error_counts[signature] = deque()
        
        # 清理过期记录
        errors = self.error_counts[signature]
        while errors and errors[0] < minute_ago:
            errors.popleft()
        
        # 检查是否超过限制
        if len(errors) >= self.max_errors:
            return True
        
        # 记录新错误
        errors.append(now)
        return False
```

#### 1.2 IPC错误响应
```python
# daemon/services/ipc_protocol.py

@dataclass
class IPCResponse:
    """安全的IPC响应格式"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None  # 只包含安全信息
    metadata: Optional[IPCMetadata] = None
    
    @classmethod
    def from_error(cls, processed_error: ProcessedError, request_id: str) -> "IPCResponse":
        """从处理后的错误创建响应"""
        return cls(
            success=False,
            error=processed_error.to_safe_dict(),
            metadata=IPCMetadata.create(request_id=request_id)
        )
```

### 2. UI端错误处理（Flutter）

#### 2.1 增强的错误处理器
```dart
// ui/lib/utils/enhanced_error_handler.dart

import 'dart:async';
import 'dart:collection';
import 'package:rxdart/rxdart.dart';
import 'package:flutter/foundation.dart';

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
      .distinct((a, b) => _isDuplicate(a, b))  // 去重
      .throttleTime(const Duration(seconds: 1)); // 限流
  
  /// 处理IPC错误
  void handleIPCError(
    Map<String, dynamic> errorData, {
    required String operation,
    StackTrace? stackTrace,
  }) {
    final error = UIError.fromIPCError(
      errorData: errorData,
      operation: operation,
      stackTrace: kDebugMode ? stackTrace : null, // 仅调试模式保留堆栈
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
      // 开发模式：详细输出
      FlutterError.presentError(details);
    } else {
      // 生产模式：静默处理
      final error = UIError(
        errorId: _generateErrorId(),
        code: 'FLUTTER_ERROR',
        message: details.exceptionAsString(),
        operation: 'Flutter Framework',
        timestamp: DateTime.now(),
        isRecoverable: false,
        canRetry: false,
      );
      _addError(error);
    }
  }
  
  /// 安全执行异步操作
  Future<T?> safeAsync<T>(
    Future<T> Function() operation, {
    required String context,
    T? fallback,
    int maxRetries = 3,
  }) async {
    int attempts = 0;
    
    while (attempts < maxRetries) {
      try {
        return await operation();
      } catch (e, stackTrace) {
        attempts++;
        
        if (attempts >= maxRetries) {
          final error = UIError(
            errorId: _generateErrorId(),
            code: 'ASYNC_ERROR',
            message: e.toString(),
            operation: context,
            timestamp: DateTime.now(),
            isRecoverable: false,
            canRetry: attempts < maxRetries,
            stackTrace: kDebugMode ? stackTrace.toString() : null,
          );
          
          _addError(error);
          return fallback;
        }
        
        // 指数退避
        await Future.delayed(Duration(seconds: attempts * attempts));
      }
    }
    
    return fallback;
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
    
    // 开发模式额外输出
    if (kDebugMode) {
      _printDebugError(error);
    }
  }
  
  bool _isDuplicate(UIError a, UIError b) {
    return a.signature == b.signature;
  }
  
  String _generateErrorId() {
    return 'ui_${DateTime.now().millisecondsSinceEpoch}';
  }
  
  void _printDebugError(UIError error) {
    final buffer = StringBuffer();
    buffer.writeln('╔════════════════════════════════════════════════════════════');
    buffer.writeln('║ 🔴 ERROR: ${error.operation}');
    buffer.writeln('║ ID: ${error.errorId}');
    buffer.writeln('║ Code: ${error.code}');
    buffer.writeln('║ Message: ${error.message}');
    buffer.writeln('║ Time: ${error.timestamp}');
    
    if (error.canRetry) {
      buffer.writeln('║ Retry: Available${error.retryAfter != null ? ' (after ${error.retryAfter}s)' : ''}');
    }
    
    if (error.stackTrace != null) {
      buffer.writeln('║ Stack Trace:');
      for (final line in error.stackTrace!.split('\n')) {
        buffer.writeln('║   $line');
      }
    }
    
    buffer.writeln('╚════════════════════════════════════════════════════════════');
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
    
    debugPrint('⚡ Auto-recovery scheduled for ${error.code} in ${delay.inSeconds}s (attempt $attempts)');
  }
  
  void _performRecovery(UIError error) {
    // 根据错误类型执行恢复操作
    switch (error.code) {
      case 'IPC_CONNECTION_FAILED':
        // 重新连接IPC
        IPCService.instance.connect();
        break;
      case 'IPC_AUTH_FAILED':
        // 重新认证
        IPCService.instance.reconnect();
        break;
      default:
        // 通用恢复：触发重试
        if (error.retryCallback != null) {
          error.retryCallback!();
        }
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

/// UI错误模型
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
  
  factory UIError.fromIPCError({
    required Map<String, dynamic> errorData,
    required String operation,
    StackTrace? stackTrace,
  }) {
    return UIError(
      errorId: errorData['error_id'] ?? 'unknown',
      code: errorData['code'] ?? 'UNKNOWN_ERROR',
      message: errorData['message'] ?? 'Unknown error',
      operation: operation,
      timestamp: DateTime.now(),
      isRecoverable: errorData['is_recoverable'] ?? false,
      canRetry: errorData['can_retry'] ?? false,
      retryAfter: errorData['retry_after'],
      stackTrace: stackTrace?.toString(),
    );
  }
  
  /// 错误签名（用于去重）
  String get signature => '$code:$operation';
  
  /// 是否为网络相关错误
  bool get isNetworkError => 
    code.contains('CONNECTION') || 
    code.contains('TIMEOUT') || 
    code.contains('NETWORK');
    
  /// 是否为认证错误
  bool get isAuthError => code.contains('AUTH');
  
  /// 是否为严重错误
  bool get isCritical => 
    code.contains('CRITICAL') || 
    code.contains('FATAL');
}
```

#### 2.2 错误显示组件
```dart
// ui/lib/widgets/smart_error_display.dart

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../utils/enhanced_error_handler.dart';

class SmartErrorDisplay extends StatefulWidget {
  final Widget child;
  
  const SmartErrorDisplay({
    required this.child,
    super.key,
  });
  
  @override
  State<SmartErrorDisplay> createState() => _SmartErrorDisplayState();
}

class _SmartErrorDisplayState extends State<SmartErrorDisplay> 
    with SingleTickerProviderStateMixin {
  final _errorHandler = EnhancedErrorHandler();
  StreamSubscription<UIError>? _errorSubscription;
  final _displayedErrors = <UIError>[];
  late AnimationController _animationController;
  
  @override
  void initState() {
    super.initState();
    
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    
    // 订阅错误流
    _errorSubscription = _errorHandler.errorStream.listen(_onError);
  }
  
  @override
  void dispose() {
    _errorSubscription?.cancel();
    _animationController.dispose();
    super.dispose();
  }
  
  void _onError(UIError error) {
    if (!mounted) return;
    
    setState(() {
      // 移除相同类型的旧错误
      _displayedErrors.removeWhere((e) => e.code == error.code);
      // 添加新错误
      _displayedErrors.add(error);
      // 限制显示数量
      if (_displayedErrors.length > 3) {
        _displayedErrors.removeAt(0);
      }
    });
    
    _animationController.forward();
    
    // 非严重错误自动消失
    if (!error.isCritical && !error.canRetry) {
      Future.delayed(const Duration(seconds: 5), () {
        if (mounted) {
          _dismissError(error);
        }
      });
    }
  }
  
  void _dismissError(UIError error) {
    setState(() {
      _displayedErrors.remove(error);
    });
    
    if (_displayedErrors.isEmpty) {
      _animationController.reverse();
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        widget.child,
        if (_displayedErrors.isNotEmpty)
          Positioned(
            bottom: 16,
            left: 16,
            right: 16,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: _displayedErrors
                  .map((error) => _buildErrorCard(error))
                  .toList(),
            ),
          ),
      ],
    );
  }
  
  Widget _buildErrorCard(UIError error) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    
    Color backgroundColor;
    Color iconColor;
    IconData icon;
    
    if (error.isCritical) {
      backgroundColor = isDark ? Colors.red.shade900 : Colors.red.shade50;
      iconColor = Colors.red;
      icon = Icons.error;
    } else if (error.isNetworkError) {
      backgroundColor = isDark ? Colors.orange.shade900 : Colors.orange.shade50;
      iconColor = Colors.orange;
      icon = Icons.wifi_off;
    } else if (error.isAuthError) {
      backgroundColor = isDark ? Colors.amber.shade900 : Colors.amber.shade50;
      iconColor = Colors.amber;
      icon = Icons.lock_outline;
    } else {
      backgroundColor = isDark ? Colors.grey.shade800 : Colors.grey.shade100;
      iconColor = Colors.grey;
      icon = Icons.info_outline;
    }
    
    return Card(
      color: backgroundColor,
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            Icon(icon, color: iconColor),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    error.message,
                    style: TextStyle(
                      color: isDark ? Colors.white : Colors.black87,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'ID: ${error.errorId}',
                    style: TextStyle(
                      fontSize: 12,
                      color: isDark ? Colors.white70 : Colors.black54,
                    ),
                  ),
                ],
              ),
            ),
            if (error.canRetry)
              TextButton(
                onPressed: () {
                  error.retryCallback?.call();
                  _dismissError(error);
                },
                child: Text(
                  error.retryAfter != null 
                    ? '${error.retryAfter}s'
                    : '重试',
                ),
              ),
            if (kDebugMode)
              IconButton(
                icon: const Icon(Icons.copy, size: 16),
                onPressed: () {
                  Clipboard.setData(ClipboardData(text: error.errorId));
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('错误ID已复制'),
                      duration: Duration(seconds: 1),
                    ),
                  );
                },
              ),
            IconButton(
              icon: const Icon(Icons.close, size: 16),
              onPressed: () => _dismissError(error),
            ),
          ],
        ),
      ),
    );
  }
}
```

### 3. 集成步骤

#### 3.1 修改主入口
```dart
// ui/lib/main.dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // 设置全局错误处理
  final errorHandler = EnhancedErrorHandler();
  
  FlutterError.onError = errorHandler.handleFlutterError;
  
  PlatformDispatcher.instance.onError = (error, stack) {
    errorHandler.handleError(error, stack);
    return true;
  };
  
  runApp(
    ProviderScope(
      child: SmartErrorDisplay(
        child: MyApp(),
      ),
    ),
  );
}
```

#### 3.2 修改API调用
```dart
// ui/lib/services/ipc_api_adapter.dart
Future<Map<String, dynamic>> get(String path) async {
  return await EnhancedErrorHandler().safeAsync(
    () async {
      await _ensureInitialized();
      final response = await _ipcClient.get(path);
      
      if (!response.success && response.error != null) {
        EnhancedErrorHandler().handleIPCError(
          response.error!,
          operation: 'GET $path',
        );
      }
      
      return _createStandardResponse(response);
    },
    context: 'API GET $path',
    maxRetries: 3,
  );
}
```

## 优势对比

| 特性 | 原方案 | 优化方案 |
|-----|-------|---------|
| **安全性** | ❌ 暴露堆栈 | ✅ 仅传输安全信息 |
| **去重** | ❌ 无 | ✅ 5秒窗口去重 |
| **限流** | ❌ 无 | ✅ 1秒限流 |
| **自动恢复** | ❌ 无 | ✅ 指数退避重试 |
| **用户体验** | ⚠️ 基础 | ✅ 友好提示+重试 |
| **调试** | ⚠️ 有限 | ✅ 完整调试信息 |
| **性能** | ⚠️ 一般 | ✅ 优化 |
| **内存管理** | ❌ 风险 | ✅ 严格控制 |

## 监控集成（可选）

### 后端日志聚合
```python
# 集成Sentry示例
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    environment="production",
    before_send=lambda event, hint: filter_sensitive_data(event)
)

def _send_to_monitoring(self, detailed_log):
    sentry_sdk.capture_message(
        f"Error: {detailed_log['error_id']}",
        level="error",
        extras=detailed_log
    )
```

## 总结

这个优化方案通过以下关键改进，提供了工业级的错误处理能力：

1. **安全性保证**：生产环境绝不暴露敏感信息
2. **智能去重限流**：防止错误风暴
3. **自动恢复机制**：提升系统韧性
4. **用户友好体验**：清晰的错误提示和操作建议
5. **完整的可追溯性**：每个错误都有唯一ID可追踪

这套方案完全符合现代分布式应用的错误处理最佳实践。