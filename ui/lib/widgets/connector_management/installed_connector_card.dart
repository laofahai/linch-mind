import 'package:flutter/material.dart';
import '../../models/connector_lifecycle_models.dart';

/// 已安装连接器卡片组件
class InstalledConnectorCard extends StatelessWidget {
  final ConnectorInfo connector;
  final VoidCallback onRefresh;

  const InstalledConnectorCard({
    super.key,
    required this.connector,
    required this.onRefresh,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            _buildStatusIcon(),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    connector.displayName,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                  Text(
                    connector.connectorId,
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 12,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                  Text(
                    _getStateText(),
                    style: TextStyle(
                      color: _getStateColor(),
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
            _buildActionButtons(),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusIcon() {
    IconData iconData;
    Color color;

    switch (connector.state) {
      case ConnectorState.running:
        iconData = Icons.play_circle_filled;
        color = Colors.green;
        break;
      case ConnectorState.stopped:
        // 区分用户禁用和启动失败
        if (connector.enabled) {
          iconData = Icons.error_outline; // 启动失败
          color = Colors.red;
        } else {
          iconData = Icons.pause_circle_filled; // 用户禁用
          color = Colors.grey;
        }
        break;
      case ConnectorState.starting:
        iconData = Icons.sync; // 启动中的旋转图标
        color = Colors.orange;
        break;
      case ConnectorState.stopping:
        iconData = Icons.stop_circle;
        color = Colors.orange;
        break;
      case ConnectorState.error:
        iconData = Icons.error;
        color = Colors.red;
        break;
      default:
        iconData = Icons.help_outline;
        color = Colors.grey;
    }

    // 为启动中和停止中状态添加旋转动画提示
    Widget icon = Icon(iconData, color: color, size: 32);
    if (connector.state == ConnectorState.starting ||
        connector.state == ConnectorState.stopping) {
      // TODO: 添加旋转动画 - 需要在父组件中实现AnimationController
      return icon;
    }

    return icon;
  }

  String _getStateText() {
    switch (connector.state) {
      case ConnectorState.running:
        return '运行中${connector.processId != null ? ' (PID: ${connector.processId})' : ''}';
      case ConnectorState.stopped:
        // 区分用户禁用和启动失败
        if (connector.enabled) {
          return '启动失败';
        } else {
          return '已停止';
        }
      case ConnectorState.starting:
        return '启动中...';
      case ConnectorState.stopping:
        return '停止中...';
      case ConnectorState.error:
        return '错误${connector.errorMessage != null ? ': ${connector.errorMessage}' : ''}';
      default:
        return '未知状态';
    }
  }

  Color _getStateColor() {
    switch (connector.state) {
      case ConnectorState.running:
        return Colors.green;
      case ConnectorState.stopped:
        // 区分用户禁用和启动失败
        if (connector.enabled) {
          return Colors.red; // 启动失败
        } else {
          return Colors.grey; // 用户禁用
        }
      case ConnectorState.starting:
        return Colors.orange;
      case ConnectorState.stopping:
        return Colors.orange;
      case ConnectorState.error:
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  Widget _buildActionButtons() {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        IconButton(
          icon: const Icon(Icons.settings, size: 20),
          onPressed: () {
            // TODO: 实现设置功能
          },
          tooltip: '设置',
        ),
        IconButton(
          icon: const Icon(Icons.more_vert, size: 20),
          onPressed: () {
            // TODO: 实现更多操作菜单
          },
          tooltip: '更多操作',
        ),
      ],
    );
  }
}
