# 错误处理架构改进方案

## 问题诊断

### 核心问题
UI端显示错误但控制台、调试模式、错误堆栈等完全看不到，导致调试困难。

### 根本原因
1. **错误信息传递链断裂**
   - UI层错误被过度简化
   - IPC传输丢失错误上下文
   - Daemon错误详情无法回传

2. **日志系统分离**
   - Flutter print和developer.log输出分离
   - 错误堆栈只在stderr，IDE看不到
   - 缺少统一的错误追踪ID

3. **错误处理不一致**
   - UI端使用简单try-catch
   - Daemon端有完善框架但未充分利用
   - IPC层缺少错误增强机制

## 改进方案

### 1. 增强IPC错误协议

#### 1.1 扩展IPCError结构
```dart
// ui/lib/models/ipc_protocol.dart
@freezed
class IPCError with _$IPCError {
  const factory IPCError({
    required String code,
    required String message,
    Map<String, dynamic>? details,
    
    // 新增调试信息
    String? stackTrace,        // 错误堆栈
    String? requestId,          // 请求追踪ID
    String? timestamp,          // 错误时间戳
    String? context,            // 错误上下文
    Map<String, dynamic>? debugInfo, // 调试信息
  }) = _IPCError;
}
```

#### 1.2 Daemon端错误增强
```python
# daemon/services/ipc_protocol.py
@dataclass
class IPCError:
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    
    # 新增调试字段
    stack_trace: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: Optional[str] = None
    context: Optional[str] = None
    debug_info: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_exception(cls, e: Exception, context: ErrorContext) -> "IPCError":
        """从异常创建详细的IPC错误"""
        return cls(
            code=context.category.value,
            message=str(e),
            details=context.to_dict(),
            stack_trace=traceback.format_exc(),
            timestamp=datetime.now().isoformat(),
            context=f"{context.module_name}.{context.function_name}",
            debug_info={
                "severity": context.severity.value,
                "recovery_suggestions": context.recovery_suggestions,
                "technical_details": context.technical_details
            }
        )
```

### 2. UI端错误处理增强

#### 2.1 创建统一错误处理器
```dart
// ui/lib/utils/error_handler.dart
import 'dart:developer' as developer;
import 'package:flutter/foundation.dart';
import 'app_logger.dart';
import '../models/ipc_protocol.dart';

class ErrorHandler {
  static final _errorStream = StreamController<UIError>.broadcast();
  static Stream<UIError> get errorStream => _errorStream.stream;
  
  /// 处理IPC错误响应
  static void handleIPCError(
    IPCError error, {
    required String operation,
    StackTrace? stackTrace,
  }) {
    // 构建完整错误信息
    final uiError = UIError(
      code: error.code,
      message: error.message,
      operation: operation,
      timestamp: error.timestamp ?? DateTime.now().toIso8601String(),
      requestId: error.requestId,
      details: error.details,
      stackTrace: error.stackTrace ?? stackTrace?.toString(),
      debugInfo: error.debugInfo,
    );
    
    // 发送到错误流供UI监听
    _errorStream.add(uiError);
    
    // 根据调试模式输出不同级别日志
    if (kDebugMode) {
      // 调试模式：完整输出到控制台
      print('═══════════════════════════════════════════');
      print('🔴 IPC ERROR: $operation');
      print('Code: ${error.code}');
      print('Message: ${error.message}');
      print('Request ID: ${error.requestId}');
      print('Timestamp: ${error.timestamp}');
      
      if (error.context != null) {
        print('Context: ${error.context}');
      }
      
      if (error.details != null) {
        print('Details: ${error.details}');
      }
      
      if (error.debugInfo != null) {
        print('Debug Info: ${error.debugInfo}');
      }
      
      if (error.stackTrace != null) {
        print('Server Stack Trace:');
        print(error.stackTrace);
      }
      
      if (stackTrace != null) {
        print('Client Stack Trace:');
        print(stackTrace);
      }
      print('═══════════════════════════════════════════');
    }
    
    // 同时记录到developer.log供生产环境分析
    developer.log(
      'IPC Error: ${error.message}',
      name: 'ErrorHandler',
      error: error.toJson(),
      stackTrace: stackTrace,
      level: 1000,
    );
    
    // 使用AppLogger记录
    AppLogger.error(
      'IPC操作失败: $operation',
      module: 'IPC',
      data: {
        'error_code': error.code,
        'request_id': error.requestId,
        'details': error.details,
      },
      exception: error.message,
      stackTrace: stackTrace,
    );
  }
  
  /// 处理异步操作错误
  static Future<T?> safeAsync<T>(
    Future<T> Function() operation, {
    required String context,
    T? fallback,
    bool showError = true,
  }) async {
    try {
      return await operation();
    } catch (e, stackTrace) {
      if (e is IPCError) {
        handleIPCError(e, operation: context, stackTrace: stackTrace);
      } else {
        // 处理非IPC错误
        final uiError = UIError(
          code: 'UNKNOWN_ERROR',
          message: e.toString(),
          operation: context,
          timestamp: DateTime.now().toIso8601String(),
          stackTrace: stackTrace.toString(),
        );
        
        _errorStream.add(uiError);
        
        if (kDebugMode) {
          print('═══════════════════════════════════════════');
          print('🔴 ERROR: $context');
          print('Exception: $e');
          print('Stack Trace:');
          print(stackTrace);
          print('═══════════════════════════════════════════');
        }
        
        AppLogger.error(
          '操作失败: $context',
          module: 'UI',
          exception: e,
          stackTrace: stackTrace,
        );
      }
      
      return fallback;
    }
  }
}

/// UI错误模型
class UIError {
  final String code;
  final String message;
  final String operation;
  final String timestamp;
  final String? requestId;
  final Map<String, dynamic>? details;
  final String? stackTrace;
  final Map<String, dynamic>? debugInfo;
  
  UIError({
    required this.code,
    required this.message,
    required this.operation,
    required this.timestamp,
    this.requestId,
    this.details,
    this.stackTrace,
    this.debugInfo,
  });
  
  bool get isNetworkError => code.contains('CONNECTION') || code.contains('TIMEOUT');
  bool get isAuthError => code.contains('AUTH');
  bool get isServerError => code.contains('INTERNAL') || code.contains('DATABASE');
}
```

#### 2.2 创建错误显示组件
```dart
// ui/lib/widgets/error_display.dart
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import '../utils/error_handler.dart';

class ErrorDisplay extends StatefulWidget {
  final Widget child;
  
  const ErrorDisplay({required this.child, super.key});
  
  @override
  State<ErrorDisplay> createState() => _ErrorDisplayState();
}

class _ErrorDisplayState extends State<ErrorDisplay> {
  UIError? _currentError;
  StreamSubscription? _errorSubscription;
  
  @override
  void initState() {
    super.initState();
    _errorSubscription = ErrorHandler.errorStream.listen((error) {
      if (mounted) {
        setState(() => _currentError = error);
        
        // 自动隐藏非严重错误
        if (!error.isServerError) {
          Future.delayed(const Duration(seconds: 5), () {
            if (mounted && _currentError == error) {
              setState(() => _currentError = null);
            }
          });
        }
      }
    });
  }
  
  @override
  void dispose() {
    _errorSubscription?.cancel();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        widget.child,
        if (_currentError != null)
          Positioned(
            bottom: 16,
            left: 16,
            right: 16,
            child: _buildErrorCard(_currentError!),
          ),
      ],
    );
  }
  
  Widget _buildErrorCard(UIError error) {
    final isExpanded = kDebugMode;
    
    return Card(
      color: error.isServerError 
        ? Colors.red.shade50 
        : Colors.orange.shade50,
      child: ExpansionTile(
        initiallyExpanded: isExpanded,
        leading: Icon(
          error.isNetworkError ? Icons.wifi_off :
          error.isAuthError ? Icons.lock_outline :
          Icons.error_outline,
          color: error.isServerError ? Colors.red : Colors.orange,
        ),
        title: Text(
          error.message,
          style: TextStyle(
            color: error.isServerError ? Colors.red.shade900 : Colors.orange.shade900,
          ),
        ),
        subtitle: Text(
          '${error.operation} • ${error.timestamp}',
          style: TextStyle(fontSize: 12),
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (error.requestId != null && kDebugMode)
              IconButton(
                icon: Icon(Icons.copy, size: 16),
                onPressed: () {
                  Clipboard.setData(ClipboardData(text: error.requestId!));
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Request ID已复制')),
                  );
                },
              ),
            IconButton(
              icon: Icon(Icons.close, size: 16),
              onPressed: () => setState(() => _currentError = null),
            ),
          ],
        ),
        children: [
          if (kDebugMode) ...[
            _buildDebugSection('错误代码', error.code),
            if (error.requestId != null)
              _buildDebugSection('请求ID', error.requestId!),
            if (error.details != null)
              _buildDebugSection('详情', error.details.toString()),
            if (error.debugInfo != null)
              _buildDebugSection('调试信息', error.debugInfo.toString()),
            if (error.stackTrace != null)
              _buildDebugSection('堆栈跟踪', error.stackTrace!, isCode: true),
          ],
        ],
      ),
    );
  }
  
  Widget _buildDebugSection(String title, String content, {bool isCode = false}) {
    return Padding(
      padding: EdgeInsets.all(8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: TextStyle(fontWeight: FontWeight.bold)),
          SizedBox(height: 4),
          Container(
            padding: EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.grey.shade100,
              borderRadius: BorderRadius.circular(4),
            ),
            child: SelectableText(
              content,
              style: TextStyle(
                fontFamily: isCode ? 'monospace' : null,
                fontSize: isCode ? 12 : 14,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
```

### 3. 应用错误处理增强

#### 3.1 修改主应用入口
```dart
// ui/lib/main.dart 
void main() async {
  // 设置全局错误处理
  FlutterError.onError = (details) {
    FlutterError.presentError(details);
    ErrorHandler.handleFlutterError(details);
  };
  
  // 捕获异步错误
  PlatformDispatcher.instance.onError = (error, stack) {
    ErrorHandler.handleAsyncError(error, stack);
    return true;
  };
  
  runApp(
    ProviderScope(
      child: ErrorDisplay(
        child: MyApp(),
      ),
    ),
  );
}
```

#### 3.2 修改API调用
```dart
// ui/lib/services/connector_lifecycle_api_client.dart
Future<ConnectorListResponse> getConnectors() async {
  return await ErrorHandler.safeAsync(
    () async {
      final response = await _apiAdapter.get('/connectors');
      // ... 处理响应
    },
    context: 'getConnectors',
    fallback: ConnectorListResponse(success: false, connectors: []),
  );
}
```

### 4. 调试工具增强

#### 4.1 创建错误监控面板
```dart
// ui/lib/widgets/debug_panel.dart
class DebugPanel extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    if (!kDebugMode) return SizedBox.shrink();
    
    return DraggableScrollableSheet(
      initialChildSize: 0.1,
      minChildSize: 0.1,
      maxChildSize: 0.9,
      builder: (context, scrollController) {
        return Container(
          color: Colors.black87,
          child: ListView(
            controller: scrollController,
            children: [
              // 错误日志
              StreamBuilder<UIError>(
                stream: ErrorHandler.errorStream,
                builder: (context, snapshot) {
                  // 显示错误历史
                },
              ),
              // IPC请求日志
              StreamBuilder<IPCRequest>(
                stream: IPCClient.requestStream,
                builder: (context, snapshot) {
                  // 显示请求历史
                },
              ),
            ],
          ),
        );
      },
    );
  }
}
```

### 5. 实施计划

#### 第一阶段：基础增强（1-2天）
1. 扩展IPC错误协议，增加调试字段
2. 实现UI端统一错误处理器
3. 增强AppLogger输出

#### 第二阶段：UI改进（2-3天）
1. 实现错误显示组件
2. 添加错误监控面板
3. 集成到现有界面

#### 第三阶段：完善优化（1-2天）
1. 添加错误重试机制
2. 实现错误上报功能
3. 优化错误提示文案

## 预期效果

1. **开发调试**
   - 控制台能看到完整错误信息
   - IDE调试器能捕获错误断点
   - 错误堆栈清晰可见

2. **用户体验**
   - 友好的错误提示
   - 可操作的恢复建议
   - 自动重试机制

3. **问题追踪**
   - 统一的请求ID追踪
   - 完整的错误上下文
   - 详细的调试信息

## 技术要点

1. **保持向后兼容**
   - 新字段都是可选的
   - 渐进式迁移

2. **性能考虑**
   - 生产环境减少日志输出
   - 调试信息按需开启

3. **安全性**
   - 生产环境不暴露敏感信息
   - 错误信息脱敏处理