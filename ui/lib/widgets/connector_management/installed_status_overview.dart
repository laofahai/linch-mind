import 'package:flutter/material.dart';
import '../../models/connector_lifecycle_models.dart';

/// 已安装连接器的状态概览组件
class InstalledStatusOverview extends StatelessWidget {
  final List<ConnectorInfo> connectors;

  const InstalledStatusOverview({
    super.key,
    required this.connectors,
  });

  @override
  Widget build(BuildContext context) {
    final runningCount = connectors.where((c) => c.state == ConnectorState.running).length;
    final startingCount = connectors.where((c) => c.state == ConnectorState.starting).length;
    final stoppedCount = connectors.where((c) => c.state == ConnectorState.stopped).length;
    final errorCount = connectors.where((c) => c.state == ConnectorState.error).length;
    final installedCount = connectors.where((c) => c.state == ConnectorState.installed).length;
    final stoppingCount = connectors.where((c) => c.state == ConnectorState.stopping).length;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Wrap(
        spacing: 16,
        runSpacing: 8,
        children: [
          _buildStatusIndicator(
            Icons.play_circle_filled,
            Colors.green,
            '运行中',
            runningCount,
          ),
          if (startingCount > 0)
            _buildStatusIndicator(
              Icons.sync,
              Colors.orange,
              '启动中',
              startingCount,
            ),
          if (stoppedCount > 0)
            _buildStatusIndicator(
              Icons.pause_circle,
              Colors.grey,
              '已停止',
              stoppedCount,
            ),
          if (stoppingCount > 0)
            _buildStatusIndicator(
              Icons.stop_circle,
              Colors.orange,
              '停止中',
              stoppingCount,
            ),
          if (errorCount > 0)
            _buildStatusIndicator(
              Icons.error_outline,
              Colors.red,
              '错误',
              errorCount,
            ),
          if (installedCount > 0)
            _buildStatusIndicator(
              Icons.get_app,
              Colors.blue,
              '已安装',
              installedCount,
            ),
        ],
      ),
    );
  }

  Widget _buildStatusIndicator(
    IconData icon,
    Color color,
    String label,
    int count,
  ) {
    return Row(
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(width: 4),
        Text('$label: $count'),
      ],
    );
  }
}