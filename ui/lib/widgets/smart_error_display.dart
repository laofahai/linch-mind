import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../models/ui_error.dart';
import '../utils/enhanced_error_handler.dart';

/// 智能错误显示组件 - 提供统一的错误展示和交互
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

    // 非严重错误和非重试错误自动消失
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

    // 根据错误类型确定颜色和图标
    final errorTheme = _getErrorTheme(error, isDark);

    return Card(
      color: errorTheme.backgroundColor,
      margin: const EdgeInsets.only(bottom: 8),
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 错误主要信息
            Row(
              children: [
                Icon(errorTheme.icon, color: errorTheme.iconColor, size: 20),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        error.message,
                        style: TextStyle(
                          color: errorTheme.textColor,
                          fontWeight: FontWeight.w500,
                          fontSize: 14,
                        ),
                      ),
                      if (error.operation.isNotEmpty) ...[
                        const SizedBox(height: 2),
                        Text(
                          '操作: ${error.operation}',
                          style: TextStyle(
                            fontSize: 12,
                            color: errorTheme.subtitleColor,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
                // 操作按钮
                _buildActionButtons(error, errorTheme),
              ],
            ),

            // 建议的用户操作
            if (error.suggestedAction.isNotEmpty) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: errorTheme.suggestionBackgroundColor,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.lightbulb_outline,
                      size: 16,
                      color: errorTheme.subtitleColor,
                    ),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        error.suggestedAction,
                        style: TextStyle(
                          fontSize: 12,
                          color: errorTheme.subtitleColor,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],

            // 调试信息（仅开发模式）
            if (kDebugMode) ...[
              const SizedBox(height: 8),
              _buildDebugInfo(error, errorTheme),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildActionButtons(UIError error, _ErrorTheme errorTheme) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        // 重试按钮
        if (error.canRetry)
          _buildRetryButton(error, errorTheme),
        
        // 复制错误ID按钮（调试模式）
        if (kDebugMode)
          _buildCopyButton(error, errorTheme),
        
        // 关闭按钮
        _buildCloseButton(error, errorTheme),
      ],
    );
  }

  Widget _buildRetryButton(UIError error, _ErrorTheme errorTheme) {
    return TextButton.icon(
      onPressed: () {
        error.retryCallback?.call();
        _dismissError(error);
      },
      icon: Icon(
        Icons.refresh,
        size: 16,
        color: errorTheme.actionColor,
      ),
      label: Text(
        error.retryAfter != null ? '${error.retryAfter}s' : '重试',
        style: TextStyle(
          fontSize: 12,
          color: errorTheme.actionColor,
        ),
      ),
      style: TextButton.styleFrom(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        minimumSize: Size.zero,
        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
      ),
    );
  }

  Widget _buildCopyButton(UIError error, _ErrorTheme errorTheme) {
    return IconButton(
      onPressed: () {
        Clipboard.setData(ClipboardData(
          text: 'Error ID: ${error.errorId}\nCode: ${error.code}\nMessage: ${error.message}',
        ));
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('错误信息已复制'),
            duration: Duration(seconds: 1),
          ),
        );
      },
      icon: Icon(
        Icons.copy,
        size: 16,
        color: errorTheme.actionColor,
      ),
      style: IconButton.styleFrom(
        padding: const EdgeInsets.all(4),
        minimumSize: Size.zero,
        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
      ),
    );
  }

  Widget _buildCloseButton(UIError error, _ErrorTheme errorTheme) {
    return IconButton(
      onPressed: () => _dismissError(error),
      icon: Icon(
        Icons.close,
        size: 16,
        color: errorTheme.subtitleColor,
      ),
      style: IconButton.styleFrom(
        padding: const EdgeInsets.all(4),
        minimumSize: Size.zero,
        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
      ),
    );
  }

  Widget _buildDebugInfo(UIError error, _ErrorTheme errorTheme) {
    return ExpansionTile(
      title: Text(
        '调试信息',
        style: TextStyle(
          fontSize: 12,
          color: errorTheme.subtitleColor,
        ),
      ),
      tilePadding: EdgeInsets.zero,
      childrenPadding: const EdgeInsets.only(left: 16, bottom: 8),
      children: [
        _buildDebugItem('错误ID', error.errorId, errorTheme),
        _buildDebugItem('错误代码', error.code, errorTheme),
        _buildDebugItem('时间', error.timestamp.toString(), errorTheme),
        _buildDebugItem('可恢复', error.isRecoverable.toString(), errorTheme),
        if (error.stackTrace != null)
          _buildDebugItem('堆栈跟踪', error.stackTrace!, errorTheme, maxLines: 3),
      ],
    );
  }

  Widget _buildDebugItem(String label, String value, _ErrorTheme errorTheme, {int maxLines = 1}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              '$label:',
              style: TextStyle(
                fontSize: 10,
                color: errorTheme.subtitleColor,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: TextStyle(
                fontSize: 10,
                color: errorTheme.textColor,
                fontFamily: 'monospace',
              ),
              maxLines: maxLines,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  _ErrorTheme _getErrorTheme(UIError error, bool isDark) {
    if (error.isCritical) {
      return _ErrorTheme(
        backgroundColor: isDark ? Colors.red.shade900.withOpacity(0.8) : Colors.red.shade50,
        iconColor: Colors.red,
        icon: Icons.error,
        textColor: isDark ? Colors.red.shade100 : Colors.red.shade800,
        subtitleColor: isDark ? Colors.red.shade300 : Colors.red.shade600,
        actionColor: isDark ? Colors.red.shade200 : Colors.red.shade700,
        suggestionBackgroundColor: isDark ? Colors.red.shade800 : Colors.red.shade100,
      );
    } else if (error.isNetworkError) {
      return _ErrorTheme(
        backgroundColor: isDark ? Colors.orange.shade900.withOpacity(0.8) : Colors.orange.shade50,
        iconColor: Colors.orange,
        icon: Icons.wifi_off,
        textColor: isDark ? Colors.orange.shade100 : Colors.orange.shade800,
        subtitleColor: isDark ? Colors.orange.shade300 : Colors.orange.shade600,
        actionColor: isDark ? Colors.orange.shade200 : Colors.orange.shade700,
        suggestionBackgroundColor: isDark ? Colors.orange.shade800 : Colors.orange.shade100,
      );
    } else if (error.isAuthError) {
      return _ErrorTheme(
        backgroundColor: isDark ? Colors.amber.shade900.withOpacity(0.8) : Colors.amber.shade50,
        iconColor: Colors.amber.shade700,
        icon: Icons.lock_outline,
        textColor: isDark ? Colors.amber.shade100 : Colors.amber.shade800,
        subtitleColor: isDark ? Colors.amber.shade300 : Colors.amber.shade600,
        actionColor: isDark ? Colors.amber.shade200 : Colors.amber.shade700,
        suggestionBackgroundColor: isDark ? Colors.amber.shade800 : Colors.amber.shade100,
      );
    } else if (error.isInputError) {
      return _ErrorTheme(
        backgroundColor: isDark ? Colors.blue.shade900.withOpacity(0.8) : Colors.blue.shade50,
        iconColor: Colors.blue,
        icon: Icons.info_outline,
        textColor: isDark ? Colors.blue.shade100 : Colors.blue.shade800,
        subtitleColor: isDark ? Colors.blue.shade300 : Colors.blue.shade600,
        actionColor: isDark ? Colors.blue.shade200 : Colors.blue.shade700,
        suggestionBackgroundColor: isDark ? Colors.blue.shade800 : Colors.blue.shade100,
      );
    } else {
      return _ErrorTheme(
        backgroundColor: isDark ? Colors.grey.shade800.withOpacity(0.9) : Colors.grey.shade100,
        iconColor: Colors.grey.shade600,
        icon: Icons.warning_outlined,
        textColor: isDark ? Colors.grey.shade100 : Colors.grey.shade800,
        subtitleColor: isDark ? Colors.grey.shade400 : Colors.grey.shade600,
        actionColor: isDark ? Colors.grey.shade300 : Colors.grey.shade700,
        suggestionBackgroundColor: isDark ? Colors.grey.shade700 : Colors.grey.shade200,
      );
    }
  }
}

/// 错误主题配置
class _ErrorTheme {
  final Color backgroundColor;
  final Color iconColor;
  final IconData icon;
  final Color textColor;
  final Color subtitleColor;
  final Color actionColor;
  final Color suggestionBackgroundColor;

  _ErrorTheme({
    required this.backgroundColor,
    required this.iconColor,
    required this.icon,
    required this.textColor,
    required this.subtitleColor,
    required this.actionColor,
    required this.suggestionBackgroundColor,
  });
}