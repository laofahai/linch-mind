import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:async';

import '../models/connector_lifecycle_models.dart';

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

class _ConnectorStatusWidgetState extends ConsumerState<ConnectorStatusWidget> {
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
  ConnectorState get _connectorStatus {
    final connector = widget.connector;
    if (connector is ConnectorInfo) {
      return connector.state;
    }
    // 如果是其他类型，尝试获取status字段，默认为stopped
    return connector?.status ?? ConnectorState.stopped;
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
    if (connector is ConnectorInfo) {
      // 使用 ConnectorInfo 的扩展方法获取 uptime
      return connector.uptime;
    }
    return null;
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


  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final statusInfo = _getStatusInfo(_connectorStatus, theme);

    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      child: Padding(
        padding: const EdgeInsets.all(10),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
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

              const SizedBox(height: 6),

              // 状态描述
              Row(
                children: [
                  Icon(statusInfo.icon,
                      size: 14, color: statusInfo.color),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      statusInfo.description,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: statusInfo.color,
                        fontWeight: FontWeight.w500,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),

              // 统计信息
              const SizedBox(height: 6),
              _buildStatsRow(context),

              // 错误信息（如果有）
              if (_connectorStatus == ConnectorState.error &&
                  _lastError != null) ...[
                const SizedBox(height: 4),
                _buildCompactErrorInfo(context),
              ],
            ],
          ),
        ),
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
            icon: const Icon(Icons.settings, size: 16),
            tooltip: '配置',
            style: IconButton.styleFrom(
              padding: const EdgeInsets.all(4),
              minimumSize: const Size(24, 24),
            ),
          ),

        // 刷新按钮
        if (widget.onRefresh != null)
          IconButton(
            onPressed: widget.onRefresh,
            icon: const Icon(Icons.refresh, size: 16),
            tooltip: '刷新状态',
            style: IconButton.styleFrom(
              padding: const EdgeInsets.all(4),
              minimumSize: const Size(24, 24),
            ),
          ),

        // 重启按钮（仅在错误或停止状态）
        if ((_connectorStatus == ConnectorState.error ||
                _connectorStatus == ConnectorState.stopped) &&
            widget.onRestart != null)
          IconButton(
            onPressed: widget.onRestart,
            icon: const Icon(Icons.restart_alt, size: 16),
            tooltip: '重启连接器',
            style: IconButton.styleFrom(
              padding: const EdgeInsets.all(4),
              minimumSize: const Size(24, 24),
              foregroundColor: Colors.orange,
            ),
          ),
      ],
    );
  }

  Widget _buildStatsRow(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
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
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 12, color: theme.colorScheme.onSurfaceVariant),
        const SizedBox(height: 2),
        Text(
          value,
          style: theme.textTheme.bodySmall?.copyWith(
            fontWeight: FontWeight.w600,
            color: theme.colorScheme.onSurface,
            fontSize: 10,
          ),
          overflow: TextOverflow.ellipsis,
          maxLines: 1,
        ),
        Text(
          label,
          style: theme.textTheme.bodySmall?.copyWith(
            fontSize: 8,
            color: theme.colorScheme.onSurfaceVariant,
          ),
          overflow: TextOverflow.ellipsis,
          maxLines: 1,
        ),
      ],
    );
  }

  /// 构建紧凑的错误信息显示
  Widget _buildCompactErrorInfo(BuildContext context) {
    final theme = Theme.of(context);
    final error = _lastError!;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: Colors.red.shade200, width: 0.5),
      ),
      child: Row(
        children: [
          Icon(Icons.error_outline, size: 12, color: Colors.red.shade600),
          const SizedBox(width: 4),
          Expanded(
            child: Text(
              error.length > 30 ? '${error.substring(0, 30)}...' : error,
              style: theme.textTheme.bodySmall?.copyWith(
                color: Colors.red.shade700,
                fontSize: 9,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          if (widget.onRestart != null) ...[
            const SizedBox(width: 4),
            SizedBox(
              height: 20,
              child: TextButton(
                onPressed: widget.onRestart,
                style: TextButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  minimumSize: const Size(0, 20),
                  backgroundColor: Colors.orange.shade100,
                  foregroundColor: Colors.orange.shade800,
                ),
                child: Text(
                  '修复',
                  style: TextStyle(fontSize: 8),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  _StatusInfo _getStatusInfo(ConnectorState status, ThemeData theme) {
    switch (status) {
      case ConnectorState.running:
        return _StatusInfo(
          color: Colors.green,
          icon: Icons.play_circle_filled,
          description: '运行中',
        );
      case ConnectorState.starting:
        return _StatusInfo(
          color: Colors.orange,
          icon: Icons.pending,
          description: '启动中...',
        );
      case ConnectorState.stopping:
        return _StatusInfo(
          color: Colors.orange,
          icon: Icons.pending,
          description: '停止中...',
        );
      case ConnectorState.stopped:
        return _StatusInfo(
          color: Colors.grey,
          icon: Icons.stop_circle,
          description: '已停止',
        );
      case ConnectorState.error:
        return _StatusInfo(
          color: Colors.red,
          icon: Icons.error,
          description: '错误',
        );
      case ConnectorState.unknown:
        return _StatusInfo(
          color: Colors.grey[400]!,
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
      return c?.status == ConnectorState.running;
    }).length;

    final errorCount = connectors.where((c) {
      if (c is ConnectorInfo) {
        return c.state == ConnectorState.error;
      }
      return c?.status == ConnectorState.error;
    }).length;

    final stoppedCount = connectors.where((c) {
      if (c is ConnectorInfo) {
        return c.state == ConnectorState.stopped;
      }
      return c?.status == ConnectorState.stopped;
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
                  Icons.error,
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
            color: color.withValues(alpha: 0.1),
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
