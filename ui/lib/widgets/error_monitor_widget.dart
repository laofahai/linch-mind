import 'package:flutter/material.dart';
import 'dart:async';
import '../utils/error_monitor.dart';

/// 错误监控显示组件
/// 在调试模式下显示实时错误信息，帮助开发者快速定位问题
class ErrorMonitorWidget extends StatefulWidget {
  final Widget child;
  final bool showInRelease;

  const ErrorMonitorWidget({
    super.key,
    required this.child,
    this.showInRelease = false,
  });

  @override
  State<ErrorMonitorWidget> createState() => _ErrorMonitorWidgetState();
}

class _ErrorMonitorWidgetState extends State<ErrorMonitorWidget> {
  final ErrorMonitor _monitor = ErrorMonitor();
  StreamSubscription<ErrorReport>? _errorSubscription;
  final List<ErrorReport> _recentErrors = [];
  bool _showErrorPanel = false;

  @override
  void initState() {
    super.initState();

    // 只在调试模式或明确允许的情况下启用
    if (widget.showInRelease || _isDebugMode()) {
      _errorSubscription = _monitor.errorStream.listen(_onNewError);
    }
  }

  bool _isDebugMode() {
    bool debugMode = false;
    assert(debugMode = true);
    return debugMode;
  }

  void _onNewError(ErrorReport error) {
    setState(() {
      _recentErrors.insert(0, error);
      if (_recentErrors.length > 10) {
        _recentErrors.removeAt(_recentErrors.length - 1);
      }

      // 如果是关键错误，自动显示面板
      if (error.severity == ErrorSeverity.critical) {
        _showErrorPanel = true;
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
    if (!widget.showInRelease && !_isDebugMode()) {
      return widget.child;
    }

    return Stack(
      children: [
        widget.child,

        // 错误指示器
        if (_recentErrors.isNotEmpty)
          Positioned(
            top: 40,
            right: 16,
            child: _buildErrorIndicator(),
          ),

        // 错误面板
        if (_showErrorPanel)
          Positioned.fill(
            child: _buildErrorPanel(),
          ),
      ],
    );
  }

  Widget _buildErrorIndicator() {
    final criticalCount =
        _recentErrors.where((e) => e.severity == ErrorSeverity.critical).length;
    final highCount =
        _recentErrors.where((e) => e.severity == ErrorSeverity.high).length;

    Color indicatorColor;
    IconData indicatorIcon;
    String tooltip;

    if (criticalCount > 0) {
      indicatorColor = Colors.red;
      indicatorIcon = Icons.error;
      tooltip = '有 $criticalCount 个严重错误';
    } else if (highCount > 0) {
      indicatorColor = Colors.orange;
      indicatorIcon = Icons.warning;
      tooltip = '有 $highCount 个错误';
    } else {
      indicatorColor = Colors.yellow;
      indicatorIcon = Icons.info;
      tooltip = '有 ${_recentErrors.length} 个警告';
    }

    return GestureDetector(
      onTap: () => setState(() => _showErrorPanel = !_showErrorPanel),
      child: Tooltip(
        message: tooltip,
        child: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: indicatorColor,
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: indicatorColor.withValues(alpha: 0.3),
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                indicatorIcon,
                color: Colors.white,
                size: 16,
              ),
              const SizedBox(width: 4),
              Text(
                _recentErrors.length.toString(),
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildErrorPanel() {
    return Material(
      color: Colors.black.withValues(alpha: 0.5),
      child: Center(
        child: Container(
          width: MediaQuery.of(context).size.width * 0.8,
          height: MediaQuery.of(context).size.height * 0.7,
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surface,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.3),
                blurRadius: 20,
                offset: const Offset(0, 10),
              ),
            ],
          ),
          child: Column(
            children: [
              // 头部
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.primaryContainer,
                  borderRadius: const BorderRadius.only(
                    topLeft: Radius.circular(12),
                    topRight: Radius.circular(12),
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.bug_report,
                      color: Theme.of(context).colorScheme.onPrimaryContainer,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        '错误监控 (${_recentErrors.length} 个错误)',
                        style: TextStyle(
                          color:
                              Theme.of(context).colorScheme.onPrimaryContainer,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    IconButton(
                      icon: Icon(
                        Icons.close,
                        color: Theme.of(context).colorScheme.onPrimaryContainer,
                      ),
                      onPressed: () => setState(() => _showErrorPanel = false),
                    ),
                  ],
                ),
              ),

              // 错误列表
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _recentErrors.length,
                  itemBuilder: (context, index) {
                    return _buildErrorCard(_recentErrors[index]);
                  },
                ),
              ),

              // 底部操作
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  border: Border(
                    top: BorderSide(
                      color: Theme.of(context).dividerColor,
                    ),
                  ),
                ),
                child: Row(
                  children: [
                    ElevatedButton.icon(
                      onPressed: () {
                        setState(() {
                          _recentErrors.clear();
                        });
                        _monitor.clearHistory();
                      },
                      icon: const Icon(Icons.clear_all),
                      label: const Text('清除所有'),
                    ),
                    const SizedBox(width: 8),
                    ElevatedButton.icon(
                      onPressed: () => _exportErrorLog(),
                      icon: const Icon(Icons.download),
                      label: const Text('导出日志'),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildErrorCard(ErrorReport error) {
    Color severityColor;
    IconData severityIcon;
    String severityText;

    switch (error.severity) {
      case ErrorSeverity.low:
        severityColor = Colors.blue;
        severityIcon = Icons.info_outline;
        severityText = '信息';
        break;
      case ErrorSeverity.medium:
        severityColor = Colors.orange;
        severityIcon = Icons.warning_amber_outlined;
        severityText = '警告';
        break;
      case ErrorSeverity.high:
        severityColor = Colors.red[700]!;
        severityIcon = Icons.error_outline;
        severityText = '错误';
        break;
      case ErrorSeverity.critical:
        severityColor = Colors.red[900]!;
        severityIcon = Icons.dangerous_outlined;
        severityText = '严重';
        break;
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ExpansionTile(
        leading: Icon(severityIcon, color: severityColor),
        title: Text(
          error.message,
          style: const TextStyle(fontWeight: FontWeight.w500),
        ),
        subtitle: Text(
          '${error.module} • ${_formatTime(error.timestamp)} • $severityText',
          style: TextStyle(
            color: Theme.of(context).textTheme.bodySmall?.color,
          ),
        ),
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (error.context != null) ...[
                  const Text(
                    '上下文信息:',
                    style: TextStyle(fontWeight: FontWeight.w500),
                  ),
                  const SizedBox(height: 4),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.surfaceContainer,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      error.context.toString(),
                      style: const TextStyle(
                        fontFamily: 'monospace',
                        fontSize: 12,
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                ],
                if (error.exception != null) ...[
                  const Text(
                    '异常信息:',
                    style: TextStyle(fontWeight: FontWeight.w500),
                  ),
                  const SizedBox(height: 4),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.surfaceContainer,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      error.exception.toString(),
                      style: const TextStyle(
                        fontFamily: 'monospace',
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final diff = now.difference(time);

    if (diff.inSeconds < 60) {
      return '${diff.inSeconds}秒前';
    } else if (diff.inMinutes < 60) {
      return '${diff.inMinutes}分钟前';
    } else {
      return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
    }
  }

  void _exportErrorLog() {
    // TODO: 实现错误日志导出功能
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('错误日志导出功能待实现'),
      ),
    );
  }
}

/// 简单的错误状态显示组件
class ErrorIndicator extends StatelessWidget {
  final ErrorStats stats;
  final VoidCallback? onTap;

  const ErrorIndicator({
    super.key,
    required this.stats,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    if (stats.totalCount == 0) {
      return const SizedBox.shrink();
    }

    Color color;
    IconData icon;
    String text;

    if (stats.criticalCount > 0) {
      color = Colors.red;
      icon = Icons.error;
      text = '${stats.criticalCount} 严重';
    } else if (stats.highCount > 0) {
      color = Colors.orange;
      icon = Icons.warning;
      text = '${stats.highCount} 错误';
    } else {
      color = Colors.yellow[700]!;
      icon = Icons.info;
      text = '${stats.totalCount} 警告';
    }

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          border: Border.all(color: color, width: 1),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 14, color: color),
            const SizedBox(width: 4),
            Text(
              text,
              style: TextStyle(
                color: color,
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
