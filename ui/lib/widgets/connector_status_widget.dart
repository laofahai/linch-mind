import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:async';

import '../models/connector_lifecycle_models.dart';
import '../providers/app_error_provider.dart';

/// 连接器状态可视化组件
class ConnectorStatusWidget extends ConsumerStatefulWidget {
  final dynamic connector; // 支持ConnectorInfo或其他连接器模型
  final VoidCallback? onRefresh;
  final VoidCallback? onRestart;
  final VoidCallback? onConfigure;

  const ConnectorStatusWidget({
    required this.connector,
    this.onRefresh,
    this.onRestart,
    this.onConfigure,
    super.key,
  });

  @override
  ConsumerState<ConnectorStatusWidget> createState() =>
      _ConnectorStatusWidgetState();
}

class _ConnectorStatusWidgetState extends ConsumerState<ConnectorStatusWidget>
    with TickerProviderStateMixin {
  // 适配器方法：获取连接器名称
  String get _connectorName {
    final connector = widget.connector;
    if (connector is ConnectorInfo) {
      return connector.displayName;
    }
    // 如果是其他类型，尝试获取name字段
    return connector?.name ?? connector?.displayName ?? 'Unknown';
  }

  // 适配器方法：获取连接器状态
  ConnectorStatus get _connectorStatus {
    final connector = widget.connector;
    if (connector is ConnectorInfo) {
      // 将ConnectorState映射到ConnectorStatus
      switch (connector.state) {
        case ConnectorState.running:
          return ConnectorStatus.running;
        case ConnectorState.stopped:
          return ConnectorStatus.stopped;
        case ConnectorState.error:
          return ConnectorStatus.error;
        case ConnectorState.available:
          return ConnectorStatus.stopped;
        default:
          return ConnectorStatus.stopped;
      }
    }
    // 如果是其他类型，尝试获取status字段
    return connector?.status ?? ConnectorStatus.stopped;
  }

  // 适配器方法：获取错误信息
  String? get _lastError {
    final connector = widget.connector;
    if (connector is ConnectorInfo) {
      return connector.errorMessage;
    }
    return connector?.lastError;
  }

  // 适配器方法：获取运行时间
  Duration? get _uptime {
    final connector = widget.connector;
    if (connector is ConnectorInfo && connector.lastHeartbeat != null) {
      return DateTime.now().difference(connector.lastHeartbeat!);
    }
    return connector?.uptime;
  }

  // 适配器方法：获取数据计数
  int? get _dataCount {
    final connector = widget.connector;
    if (connector is ConnectorInfo) {
      return connector.dataCount;
    }
    return connector?.dataCount;
  }

  // 适配器方法：获取最后更新时间
  DateTime? get _lastUpdate {
    final connector = widget.connector;
    if (connector is ConnectorInfo) {
      return connector.updatedAt;
    }
    return connector?.lastUpdate;
  }

  late AnimationController _pulseController;
  late AnimationController _errorShakeController;
  late Animation<double> _pulseAnimation;
  late Animation<double> _shakeAnimation;

  Timer? _statusCheckTimer;

  @override
  void initState() {
    super.initState();

    // 脉冲动画（运行状态）
    _pulseController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );
    _pulseAnimation = Tween<double>(begin: 0.8, end: 1.0).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    // 震动动画（错误状态）
    _errorShakeController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _shakeAnimation = Tween<double>(begin: 0, end: 10).animate(
      CurvedAnimation(
        parent: _errorShakeController,
        curve: Curves.elasticIn,
      ),
    );

    _startStatusCheck();
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _errorShakeController.dispose();
    _statusCheckTimer?.cancel();
    super.dispose();
  }

  void _startStatusCheck() {
    // 如果连接器正在运行，启动脉冲动画
    if (_connectorStatus == ConnectorStatus.running) {
      _pulseController.repeat(reverse: true);
    }

    // 定期检查状态变化
    _statusCheckTimer = Timer.periodic(
      const Duration(seconds: 3),
      (_) => _checkStatusChange(),
    );
  }

  void _checkStatusChange() {
    final currentStatus = _connectorStatus;

    if (currentStatus == ConnectorStatus.running) {
      if (!_pulseController.isAnimating) {
        _pulseController.repeat(reverse: true);
      }
    } else {
      _pulseController.stop();
      _pulseController.reset();
    }

    // 错误状态触发震动
    if (currentStatus == ConnectorStatus.error) {
      _errorShakeController.forward().then((_) {
        _errorShakeController.reset();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final statusInfo = _getStatusInfo(_connectorStatus, theme);

    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      child: AnimatedBuilder(
        animation: Listenable.merge([_pulseAnimation, _shakeAnimation]),
        builder: (context, child) {
          return Transform.translate(
            offset: Offset(_shakeAnimation.value, 0),
            child: Transform.scale(
              scale: _connectorStatus == ConnectorStatus.running
                  ? _pulseAnimation.value
                  : 1.0,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 连接器名称和状态指示器
                    Row(
                      children: [
                        // 状态指示器
                        Container(
                          width: 12,
                          height: 12,
                          decoration: BoxDecoration(
                            color: statusInfo.color,
                            shape: BoxShape.circle,
                            boxShadow: _connectorStatus ==
                                    ConnectorStatus.running
                                ? [
                                    BoxShadow(
                                      color: statusInfo.color.withOpacity(0.6),
                                      blurRadius: 8,
                                      spreadRadius: 2,
                                    )
                                  ]
                                : null,
                          ),
                        ),
                        const SizedBox(width: 12),

                        // 连接器名称
                        Expanded(
                          child: Text(
                            _connectorName,
                            style: theme.textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),

                        // 操作按钮
                        _buildActionButtons(statusInfo),
                      ],
                    ),

                    const SizedBox(height: 12),

                    // 状态描述
                    Row(
                      children: [
                        Icon(statusInfo.icon,
                            size: 16, color: statusInfo.color),
                        const SizedBox(width: 6),
                        Text(
                          statusInfo.description,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: statusInfo.color,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),

                    // 错误信息（如果有）
                    if (_connectorStatus == ConnectorStatus.error &&
                        _lastError != null) ...[
                      const SizedBox(height: 8),
                      _buildErrorInfo(context),
                    ],

                    // 统计信息
                    const SizedBox(height: 12),
                    _buildStatsRow(context),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildActionButtons(_StatusInfo statusInfo) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        // 配置按钮
        if (widget.onConfigure != null)
          IconButton(
            onPressed: widget.onConfigure,
            icon: const Icon(Icons.settings, size: 18),
            tooltip: '配置',
            style: IconButton.styleFrom(
              padding: const EdgeInsets.all(8),
              minimumSize: const Size(32, 32),
            ),
          ),

        // 刷新按钮
        if (widget.onRefresh != null)
          IconButton(
            onPressed: widget.onRefresh,
            icon: const Icon(Icons.refresh, size: 18),
            tooltip: '刷新状态',
            style: IconButton.styleFrom(
              padding: const EdgeInsets.all(8),
              minimumSize: const Size(32, 32),
            ),
          ),

        // 重启按钮（仅在错误或停止状态）
        if ((_connectorStatus == ConnectorStatus.error ||
                _connectorStatus == ConnectorStatus.stopped) &&
            widget.onRestart != null)
          IconButton(
            onPressed: widget.onRestart,
            icon: const Icon(Icons.restart_alt, size: 18),
            tooltip: '重启连接器',
            style: IconButton.styleFrom(
              padding: const EdgeInsets.all(8),
              minimumSize: const Size(32, 32),
              foregroundColor: Colors.orange,
            ),
          ),
      ],
    );
  }

  Widget _buildErrorInfo(BuildContext context) {
    final theme = Theme.of(context);
    final error = _lastError!;

    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: Colors.red.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.error_outline, size: 16, color: Colors.red.shade600),
              const SizedBox(width: 6),
              Text(
                '错误详情',
                style: theme.textTheme.bodySmall?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: Colors.red.shade800,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            error,
            style: theme.textTheme.bodySmall?.copyWith(
              color: Colors.red.shade700,
            ),
          ),

          // 错误恢复建议
          if (widget.onRestart != null) ...[
            const SizedBox(height: 8),
            ElevatedButton.icon(
              onPressed: () {
                // 添加到错误管理器并触发重启
                ref.read(appErrorProvider.notifier).handleException(
                      Exception(error),
                      operation: '连接器: ${_connectorName}',
                      retryCallback: widget.onRestart,
                    );
                widget.onRestart?.call();
              },
              icon: const Icon(Icons.healing, size: 16),
              label: const Text('尝试修复'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.orange.shade100,
                foregroundColor: Colors.orange.shade800,
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                minimumSize: const Size(0, 32),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildStatsRow(BuildContext context) {
    final theme = Theme.of(context);

    return Row(
      children: [
        Expanded(
          child: _buildStatItem(
            context,
            '运行时间',
            _formatDuration(_uptime),
            Icons.schedule,
          ),
        ),
        Expanded(
          child: _buildStatItem(
            context,
            '数据条目',
            _dataCount?.toString() ?? '0',
            Icons.data_usage,
          ),
        ),
        Expanded(
          child: _buildStatItem(
            context,
            '最后更新',
            _formatLastUpdate(_lastUpdate),
            Icons.update,
          ),
        ),
      ],
    );
  }

  Widget _buildStatItem(
    BuildContext context,
    String label,
    String value,
    IconData icon,
  ) {
    final theme = Theme.of(context);

    return Column(
      children: [
        Icon(icon, size: 14, color: theme.colorScheme.onSurfaceVariant),
        const SizedBox(height: 2),
        Text(
          value,
          style: theme.textTheme.bodySmall?.copyWith(
            fontWeight: FontWeight.w600,
            color: theme.colorScheme.onSurface,
          ),
        ),
        Text(
          label,
          style: theme.textTheme.bodySmall?.copyWith(
            fontSize: 10,
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
      ],
    );
  }

  _StatusInfo _getStatusInfo(ConnectorStatus status, ThemeData theme) {
    switch (status) {
      case ConnectorStatus.running:
        return _StatusInfo(
          color: Colors.green,
          icon: Icons.play_circle_filled,
          description: '运行中',
        );
      case ConnectorStatus.stopped:
        return _StatusInfo(
          color: Colors.grey,
          icon: Icons.stop_circle,
          description: '已停止',
        );
      case ConnectorStatus.error:
        return _StatusInfo(
          color: Colors.red,
          icon: Icons.error_circle,
          description: '错误',
        );
      case ConnectorStatus.starting:
        return _StatusInfo(
          color: Colors.orange,
          icon: Icons.pending,
          description: '启动中...',
        );
      case ConnectorStatus.stopping:
        return _StatusInfo(
          color: Colors.orange,
          icon: Icons.pending,
          description: '停止中...',
        );
      default:
        return _StatusInfo(
          color: Colors.grey,
          icon: Icons.help_outline,
          description: '未知状态',
        );
    }
  }

  String _formatDuration(Duration? duration) {
    if (duration == null) return '0s';

    if (duration.inDays > 0) {
      return '${duration.inDays}d ${duration.inHours % 24}h';
    } else if (duration.inHours > 0) {
      return '${duration.inHours}h ${duration.inMinutes % 60}m';
    } else if (duration.inMinutes > 0) {
      return '${duration.inMinutes}m ${duration.inSeconds % 60}s';
    } else {
      return '${duration.inSeconds}s';
    }
  }

  String _formatLastUpdate(DateTime? lastUpdate) {
    if (lastUpdate == null) return '从未';

    final now = DateTime.now();
    final diff = now.difference(lastUpdate);

    if (diff.inDays > 0) {
      return '${diff.inDays}天前';
    } else if (diff.inHours > 0) {
      return '${diff.inHours}小时前';
    } else if (diff.inMinutes > 0) {
      return '${diff.inMinutes}分钟前';
    } else {
      return '刚刚';
    }
  }
}

class _StatusInfo {
  final Color color;
  final IconData icon;
  final String description;

  _StatusInfo({
    required this.color,
    required this.icon,
    required this.description,
  });
}

/// 连接器状态总览组件
class ConnectorStatusOverview extends ConsumerWidget {
  final List<dynamic> connectors; // 支持ConnectorInfo或其他连接器模型

  const ConnectorStatusOverview({
    required this.connectors,
    super.key,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);

    // 统计各种状态
    final runningCount = connectors.where((c) {
      if (c is ConnectorInfo) {
        return c.state == ConnectorState.running;
      }
      return c?.status == ConnectorStatus.running;
    }).length;

    final errorCount = connectors.where((c) {
      if (c is ConnectorInfo) {
        return c.state == ConnectorState.error;
      }
      return c?.status == ConnectorStatus.error;
    }).length;

    final stoppedCount = connectors.where((c) {
      if (c is ConnectorInfo) {
        return c.state == ConnectorState.stopped ||
            c.state == ConnectorState.available;
      }
      return c?.status == ConnectorStatus.stopped;
    }).length;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '连接器状态总览',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildOverviewItem(
                  context,
                  '运行中',
                  runningCount,
                  Colors.green,
                  Icons.play_circle_filled,
                ),
                _buildOverviewItem(
                  context,
                  '错误',
                  errorCount,
                  Colors.red,
                  Icons.error_circle,
                ),
                _buildOverviewItem(
                  context,
                  '已停止',
                  stoppedCount,
                  Colors.grey,
                  Icons.stop_circle,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOverviewItem(
    BuildContext context,
    String label,
    int count,
    Color color,
    IconData icon,
  ) {
    final theme = Theme.of(context);

    return Column(
      children: [
        Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(24),
          ),
          child: Icon(
            icon,
            color: color,
            size: 24,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          count.toString(),
          style: theme.textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
      ],
    );
  }
}
