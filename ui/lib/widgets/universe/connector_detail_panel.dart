/// 连接器详情面板 - 显示选中连接器的详细信息和操作
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/connector_lifecycle_models.dart';
import '../../providers/universe_provider.dart';
import '../../services/universe_data_adapter.dart';
import '../../utils/app_logger.dart';

/// 连接器详情面板
class ConnectorDetailPanel extends ConsumerWidget {
  const ConnectorDetailPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedConnector = ref.watch(selectedConnectorProvider);
    final universeState = ref.watch(universeProvider);

    if (selectedConnector == null) {
      return _buildEmptyState(context);
    }

    return Container(
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.85),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white.withValues(alpha: 0.2)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.5),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(context, ref, selectedConnector),
          const Divider(color: Colors.white12, height: 1),
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                children: [
                  _buildBasicInfo(context, selectedConnector),
                  const Divider(color: Colors.white12, height: 1),
                  _buildStatusSection(context, selectedConnector),
                  const Divider(color: Colors.white12, height: 1),
                  _buildMetricsSection(context, selectedConnector),
                  const Divider(color: Colors.white12, height: 1),
                  _buildConfigSection(context, selectedConnector),
                  const Divider(color: Colors.white12, height: 1),
                  _buildPositionInfo(context, selectedConnector, universeState),
                ],
              ),
            ),
          ),
          const Divider(color: Colors.white12, height: 1),
          _buildActionButtons(context, ref, selectedConnector),
        ],
      ),
    );
  }

  /// 构建空状态
  Widget _buildEmptyState(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.8),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white.withValues(alpha: 0.2)),
      ),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.touch_app,
              size: 64,
              color: Colors.white.withValues(alpha: 0.3),
            ),
            const SizedBox(height: 16),
            Text(
              '点击天体查看详情',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Colors.white70,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              '在3D宇宙中点击任意连接器天体\n查看其详细信息和执行操作',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.white.withValues(alpha: 0.5),
                  ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  /// 构建头部
  Widget _buildHeader(
      BuildContext context, WidgetRef ref, ConnectorInfo connector) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(
              color: _getStateColor(connector.state),
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  connector.displayName,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 2),
                Text(
                  connector.connectorId,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.white.withValues(alpha: 0.6),
                        fontFamily: 'monospace',
                      ),
                ),
              ],
            ),
          ),
          IconButton(
            onPressed: () =>
                ref.read(universeProvider.notifier).selectConnector(null),
            icon: Icon(
              Icons.close,
              color: Colors.white.withValues(alpha: 0.7),
            ),
            tooltip: '关闭详情',
          ),
        ],
      ),
    );
  }

  /// 构建基本信息
  Widget _buildBasicInfo(BuildContext context, ConnectorInfo connector) {
    final displayInfo =
        UnifiedStarryDataAdapter.getConnectorDisplayInfo(connector);

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '基本信息',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: Colors.white70,
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 12),
          _buildInfoRow('状态', displayInfo['state_display'],
              _getStateColor(connector.state)),
          _buildInfoRow(
              '重要性', displayInfo['importance_display'], Colors.blue.shade400),
          _buildInfoRow(
              '层级', displayInfo['layer_display'], Colors.purple.shade400),
          _buildInfoRow('启用状态', connector.enabled ? '已启用' : '已禁用',
              connector.enabled ? Colors.green.shade400 : Colors.grey.shade400),
        ],
      ),
    );
  }

  /// 构建状态部分
  Widget _buildStatusSection(BuildContext context, ConnectorInfo connector) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '运行状态',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: Colors.white70,
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 12),
          _buildInfoRow('进程ID', connector.processId?.toString() ?? 'N/A',
              Colors.orange.shade400),
          _buildInfoRow('运行时间', connector.uptime?.toString() ?? 'N/A',
              Colors.cyan.shade400),
          if (connector.errorMessage != null)
            _buildInfoRow('错误信息', connector.errorMessage!, Colors.red.shade400),
        ],
      ),
    );
  }

  /// 构建指标部分
  Widget _buildMetricsSection(BuildContext context, ConnectorInfo connector) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '数据指标',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: Colors.white70,
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 12),
          _buildMetricCard('数据项数量', connector.dataCount.toString(),
              Colors.green.shade400, Icons.storage),
          const SizedBox(height: 8),
          if (connector.lastHeartbeat != null)
            _buildMetricCard('最后心跳', _formatDateTime(connector.lastHeartbeat!),
                Colors.pink.shade400, Icons.favorite),
        ],
      ),
    );
  }

  /// 构建配置部分
  Widget _buildConfigSection(BuildContext context, ConnectorInfo connector) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '配置信息',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: Colors.white70,
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 12),
          if (connector.config.isNotEmpty)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.05),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: connector.config.entries.take(5).map((entry) {
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 2),
                    child: Row(
                      children: [
                        Text(
                          '${entry.key}:',
                          style: TextStyle(
                            color: Colors.blue.shade300,
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            entry.value.toString(),
                            style: TextStyle(
                              color: Colors.white.withValues(alpha: 0.8),
                              fontSize: 12,
                              fontFamily: 'monospace',
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ),
            )
          else
            Text(
              '无配置信息',
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.5),
                fontSize: 12,
                fontStyle: FontStyle.italic,
              ),
            ),
        ],
      ),
    );
  }

  /// 构建位置信息
  Widget _buildPositionInfo(
      BuildContext context, ConnectorInfo connector, UniverseState state) {
    final celestialObject = state.celestialObjects
        .where((obj) => obj.id == connector.connectorId)
        .firstOrNull;

    if (celestialObject == null) return Container();

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '3D位置信息',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: Colors.white70,
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 12),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.05),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
            ),
            child: Column(
              children: [
                _buildPositionRow(
                    'X', celestialObject.position3D.x.toStringAsFixed(1)),
                _buildPositionRow(
                    'Y', celestialObject.position3D.y.toStringAsFixed(1)),
                _buildPositionRow(
                    'Z', celestialObject.position3D.z.toStringAsFixed(1)),
                _buildPositionRow(
                    '大小', celestialObject.size.toStringAsFixed(1)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 构建位置行
  Widget _buildPositionRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.7),
              fontSize: 12,
            ),
          ),
          Text(
            value,
            style: TextStyle(
              color: Colors.white,
              fontSize: 12,
              fontFamily: 'monospace',
            ),
          ),
        ],
      ),
    );
  }

  /// 构建操作按钮
  Widget _buildActionButtons(
      BuildContext context, WidgetRef ref, ConnectorInfo connector) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Row(
            children: [
              Expanded(
                child: _buildActionButton(
                  context,
                  label:
                      connector.state == ConnectorState.running ? '停止' : '启动',
                  icon: connector.state == ConnectorState.running
                      ? Icons.stop
                      : Icons.play_arrow,
                  color: connector.state == ConnectorState.running
                      ? Colors.orange.shade600
                      : Colors.green.shade600,
                  onPressed: () => _handleStartStopAction(ref, connector),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _buildActionButton(
                  context,
                  label: '重启',
                  icon: Icons.restart_alt,
                  color: Colors.blue.shade600,
                  onPressed: () => _handleRestartAction(ref, connector),
                  enabled: connector.state != ConnectorState.stopped,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          SizedBox(
            width: double.infinity,
            child: _buildActionButton(
              context,
              label: '删除连接器',
              icon: Icons.delete_outline,
              color: Colors.red.shade600,
              onPressed: () => _handleDeleteAction(context, ref, connector),
            ),
          ),
        ],
      ),
    );
  }

  /// 构建操作按钮
  Widget _buildActionButton(
    BuildContext context, {
    required String label,
    required IconData icon,
    required Color color,
    required VoidCallback onPressed,
    bool enabled = true,
  }) {
    return ElevatedButton.icon(
      onPressed: enabled ? onPressed : null,
      icon: Icon(icon, size: 18),
      label: Text(label),
      style: ElevatedButton.styleFrom(
        backgroundColor: enabled ? color : Colors.grey.shade800,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    );
  }

  /// 构建信息行
  Widget _buildInfoRow(String label, String value, Color valueColor) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.7),
              fontSize: 13,
            ),
          ),
          Text(
            value,
            style: TextStyle(
              color: valueColor,
              fontSize: 13,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  /// 构建指标卡片
  Widget _buildMetricCard(
      String label, String value, Color color, IconData icon) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  value,
                  style: TextStyle(
                    color: color,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  label,
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.7),
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 获取状态颜色
  Color _getStateColor(ConnectorState state) {
    switch (state) {
      case ConnectorState.running:
        return Colors.green.shade400;
      case ConnectorState.starting:
        return Colors.orange.shade400;
      case ConnectorState.stopping:
        return Colors.orange.shade600;
      case ConnectorState.stopped:
        return Colors.grey.shade400;
      case ConnectorState.error:
        return Colors.red.shade400;
      case ConnectorState.unknown:
        return Colors.purple.shade400;
    }
  }

  /// 格式化日期时间
  String _formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final diff = now.difference(dateTime);

    if (diff.inDays > 0) {
      return '${diff.inDays}天前';
    } else if (diff.inHours > 0) {
      return '${diff.inHours}小时前';
    } else if (diff.inMinutes > 0) {
      return '${diff.inMinutes}分钟前';
    } else {
      return '刚才';
    }
  }

  /// 处理启动/停止操作
  void _handleStartStopAction(WidgetRef ref, ConnectorInfo connector) {
    AppLogger.info('执行启动/停止操作', module: 'ConnectorDetail', data: {
      'connector_id': connector.connectorId,
      'current_state': connector.state.name,
    });

    if (connector.state == ConnectorState.running) {
      ref.read(universeProvider.notifier).stopConnector(connector.connectorId);
    } else {
      ref.read(universeProvider.notifier).startConnector(connector.connectorId);
    }
  }

  /// 处理重启操作
  void _handleRestartAction(WidgetRef ref, ConnectorInfo connector) {
    AppLogger.info('执行重启操作',
        module: 'ConnectorDetail',
        data: {'connector_id': connector.connectorId});

    ref.read(universeProvider.notifier).restartConnector(connector.connectorId);
  }

  /// 处理删除操作
  void _handleDeleteAction(
      BuildContext context, WidgetRef ref, ConnectorInfo connector) {
    showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('确认删除'),
        content: Text('确定要删除连接器 "${connector.displayName}" 吗？此操作不可恢复。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('删除'),
          ),
        ],
      ),
    ).then((confirmed) {
      if (confirmed == true) {
        AppLogger.info('确认删除连接器',
            module: 'ConnectorDetail',
            data: {'connector_id': connector.connectorId});

        ref
            .read(universeProvider.notifier)
            .deleteConnector(connector.connectorId);
      }
    });
  }
}
