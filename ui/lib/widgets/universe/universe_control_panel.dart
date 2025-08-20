/// 球形宇宙控制面板 - 连接器管理和过滤控制
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/connector_lifecycle_models.dart';
import '../../providers/universe_provider.dart';
import '../../services/universe_data_adapter.dart';
import '../../utils/app_logger.dart';

/// 宇宙控制面板
class UniverseControlPanel extends ConsumerStatefulWidget {
  const UniverseControlPanel({super.key});

  @override
  ConsumerState<UniverseControlPanel> createState() =>
      _UniverseControlPanelState();
}

class _UniverseControlPanelState extends ConsumerState<UniverseControlPanel> {
  ConnectorState? _filterState;
  String _searchQuery = '';
  bool _autoRefreshEnabled = true;

  @override
  Widget build(BuildContext context) {
    final universeState = ref.watch(universeProvider);
    final stats = ref.watch(universeStatsProvider);

    return Container(
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.8),
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
          _buildHeader(context),
          const Divider(color: Colors.white12, height: 1),
          _buildStatsSection(context, stats),
          const Divider(color: Colors.white12, height: 1),
          _buildFilterSection(context),
          const Divider(color: Colors.white12, height: 1),
          Expanded(child: _buildConnectorList(context, universeState)),
          const Divider(color: Colors.white12, height: 1),
          _buildActionSection(context),
        ],
      ),
    );
  }

  /// 构建头部
  Widget _buildHeader(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Icon(
            Icons.control_point,
            color: Colors.blue.shade400,
            size: 24,
          ),
          const SizedBox(width: 12),
          Text(
            '宇宙控制中心',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
          ),
          const Spacer(),
          Switch(
            value: _autoRefreshEnabled,
            onChanged: (value) {
              setState(() => _autoRefreshEnabled = value);
              ref.read(universeProvider.notifier).toggleAutoRefresh(value);
              AppLogger.info('切换自动刷新',
                  module: 'UniverseControl', data: {'enabled': value});
            },
            activeColor: Colors.green.shade400,
          ),
        ],
      ),
    );
  }

  /// 构建统计区域
  Widget _buildStatsSection(BuildContext context, Map<String, int> stats) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '实时统计',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: Colors.white70,
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _buildStatCard('总数', stats['total'] ?? 0, Colors.blue.shade400),
              _buildStatCard(
                  '运行', stats['running'] ?? 0, Colors.green.shade400),
              _buildStatCard('错误', stats['error'] ?? 0, Colors.red.shade400),
              _buildStatCard(
                  '连接', stats['connections'] ?? 0, Colors.purple.shade400),
            ],
          ),
        ],
      ),
    );
  }

  /// 构建统计卡片
  Widget _buildStatCard(String label, int value, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            value.toString(),
            style: TextStyle(
              color: color,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            label,
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  /// 构建过滤区域
  Widget _buildFilterSection(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '过滤器',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: Colors.white70,
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 12),

          // 搜索框
          TextField(
            onChanged: (value) =>
                setState(() => _searchQuery = value.toLowerCase()),
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              hintText: '搜索连接器...',
              hintStyle: TextStyle(color: Colors.white.withValues(alpha: 0.5)),
              prefixIcon: Icon(Icons.search,
                  color: Colors.white.withValues(alpha: 0.7)),
              suffixIcon: _searchQuery.isNotEmpty
                  ? IconButton(
                      icon: Icon(Icons.clear,
                          color: Colors.white.withValues(alpha: 0.7)),
                      onPressed: () => setState(() => _searchQuery = ''),
                    )
                  : null,
              filled: true,
              fillColor: Colors.white.withValues(alpha: 0.1),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide:
                    BorderSide(color: Colors.white.withValues(alpha: 0.3)),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide:
                    BorderSide(color: Colors.white.withValues(alpha: 0.3)),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide(color: Colors.blue.shade400),
              ),
              contentPadding:
                  const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            ),
          ),

          const SizedBox(height: 12),

          // 状态过滤器
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildStateFilter('全部', null),
                const SizedBox(width: 8),
                _buildStateFilter('运行中', ConnectorState.running),
                const SizedBox(width: 8),
                _buildStateFilter('错误', ConnectorState.error),
                const SizedBox(width: 8),
                _buildStateFilter('已停止', ConnectorState.stopped),
                const SizedBox(width: 8),
                _buildStateFilter('启动中', ConnectorState.starting),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 构建状态过滤器
  Widget _buildStateFilter(String label, ConnectorState? state) {
    final isSelected = _filterState == state;
    final color = _getStateColor(state);

    return GestureDetector(
      onTap: () => setState(() => _filterState = state),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isSelected
              ? color.withValues(alpha: 0.3)
              : Colors.white.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected ? color : Colors.white.withValues(alpha: 0.3),
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: isSelected ? color : Colors.white70,
            fontSize: 12,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
          ),
        ),
      ),
    );
  }

  /// 获取状态颜色
  Color _getStateColor(ConnectorState? state) {
    switch (state) {
      case ConnectorState.running:
        return Colors.green.shade400;
      case ConnectorState.error:
        return Colors.red.shade400;
      case ConnectorState.stopped:
        return Colors.grey.shade400;
      case ConnectorState.starting:
        return Colors.orange.shade400;
      default:
        return Colors.blue.shade400;
    }
  }

  /// 构建连接器列表
  Widget _buildConnectorList(BuildContext context, UniverseState state) {
    final filteredConnectors = _getFilteredConnectors(state.connectors);

    if (filteredConnectors.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.search_off,
              size: 48,
              color: Colors.white.withValues(alpha: 0.3),
            ),
            const SizedBox(height: 16),
            Text(
              '没有找到匹配的连接器',
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.7),
                fontSize: 14,
              ),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      itemCount: filteredConnectors.length,
      itemBuilder: (context, index) {
        final connector = filteredConnectors[index];
        final isSelected = state.selectedConnectorId == connector.connectorId;

        return _buildConnectorItem(context, connector, isSelected);
      },
    );
  }

  /// 获取过滤后的连接器列表
  List<ConnectorInfo> _getFilteredConnectors(List<ConnectorInfo> connectors) {
    var filtered = connectors.where((connector) {
      // 状态过滤
      if (_filterState != null && connector.state != _filterState) {
        return false;
      }

      // 搜索过滤
      if (_searchQuery.isNotEmpty) {
        final query = _searchQuery.toLowerCase();
        return connector.displayName.toLowerCase().contains(query) ||
            connector.connectorId.toLowerCase().contains(query);
      }

      return true;
    }).toList();

    // 按重要性排序
    filtered.sort((a, b) {
      final aImportance = _calculateConnectorImportance(a);
      final bImportance = _calculateConnectorImportance(b);
      return bImportance.compareTo(aImportance);
    });

    return filtered;
  }

  /// 计算连接器重要性
  double _calculateConnectorImportance(ConnectorInfo connector) {
    double score = 0.0;

    switch (connector.state) {
      case ConnectorState.running:
        score += 0.4;
        break;
      case ConnectorState.error:
        score += 0.35;
        break;
      case ConnectorState.starting:
        score += 0.3;
        break;
      default:
        score += 0.1;
        break;
    }

    if (connector.dataCount > 0) {
      score += 0.3 * (connector.dataCount / 10000).clamp(0.0, 1.0);
    }

    if (connector.enabled) score += 0.1;

    return score;
  }

  /// 构建连接器项
  Widget _buildConnectorItem(
      BuildContext context, ConnectorInfo connector, bool isSelected) {
    final displayInfo =
        UnifiedStarryDataAdapter.getConnectorDisplayInfo(connector);

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () {
            ref
                .read(universeProvider.notifier)
                .selectConnector(connector.connectorId);
            AppLogger.debug('从控制面板选中连接器',
                module: 'UniverseControl', data: {'id': connector.connectorId});
          },
          borderRadius: BorderRadius.circular(8),
          child: Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: isSelected
                  ? Colors.blue.shade400.withValues(alpha: 0.2)
                  : Colors.white.withValues(alpha: 0.05),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: isSelected
                    ? Colors.blue.shade400.withValues(alpha: 0.5)
                    : Colors.white.withValues(alpha: 0.1),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      width: 8,
                      height: 8,
                      decoration: BoxDecoration(
                        color: _getStateColor(connector.state),
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        connector.displayName,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: _getStateColor(connector.state)
                            .withValues(alpha: 0.2),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        displayInfo['importance_display'],
                        style: TextStyle(
                          color: _getStateColor(connector.state),
                          fontSize: 10,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Icon(
                      Icons.storage,
                      size: 12,
                      color: Colors.white.withValues(alpha: 0.6),
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '${connector.dataCount} 数据项',
                      style: TextStyle(
                        color: Colors.white.withValues(alpha: 0.6),
                        fontSize: 11,
                      ),
                    ),
                    const Spacer(),
                    Text(
                      displayInfo['state_display'],
                      style: TextStyle(
                        color: _getStateColor(connector.state),
                        fontSize: 11,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// 构建操作区域
  Widget _buildActionSection(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Expanded(
            child: ElevatedButton.icon(
              onPressed: () =>
                  ref.read(universeProvider.notifier).forceRefresh(),
              icon: const Icon(Icons.refresh, size: 18),
              label: const Text('刷新宇宙'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue.shade600,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
