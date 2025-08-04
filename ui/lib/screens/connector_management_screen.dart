import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/connector_lifecycle_models.dart';
import '../services/connector_lifecycle_api_client.dart';

/// 连接器管理主界面 - 基于新的生命周期API
class ConnectorManagementScreen extends ConsumerStatefulWidget {
  const ConnectorManagementScreen({super.key});

  @override
  ConsumerState<ConnectorManagementScreen> createState() => _ConnectorManagementScreenState();
}

class _ConnectorManagementScreenState extends ConsumerState<ConnectorManagementScreen> {
  final _apiClient = ConnectorLifecycleApiService.instance;
  
  List<ConnectorTypeInfo> _connectorTypes = [];
  List<ConnectorInstanceInfo> _instances = [];
  bool _isLoading = true;
  String? _errorMessage;
  String _searchQuery = '';
  ConnectorState? _stateFilter;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      // 并行加载连接器类型和实例
      final futures = await Future.wait([
        _apiClient.discoverConnectorTypes(),
        _apiClient.getConnectorInstances(),
      ]);

      final discoveryResponse = futures[0] as DiscoveryResponse;
      final instanceResponse = futures[1] as InstanceListResponse;

      setState(() {
        _connectorTypes = discoveryResponse.connectorTypes;
        _instances = instanceResponse.instances;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = '加载数据失败: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _refreshData() async {
    await _loadData();
  }

  List<ConnectorInstanceInfo> get _filteredInstances {
    var filtered = _instances.where((instance) {
      // 搜索过滤
      if (_searchQuery.isNotEmpty) {
        final query = _searchQuery.toLowerCase();
        if (!instance.displayName.toLowerCase().contains(query) &&
            !instance.typeName.toLowerCase().contains(query)) {
          return false;
        }
      }
      
      // 状态过滤
      if (_stateFilter != null && instance.state != _stateFilter) {
        return false;
      }
      
      return true;
    }).toList();

    // 按状态排序：运行中 > 启用 > 配置 > 错误 > 其他
    filtered.sort((a, b) {
      const stateOrder = {
        ConnectorState.running: 0,
        ConnectorState.enabled: 1,
        ConnectorState.configured: 2,
        ConnectorState.error: 3,
      };
      
      final orderA = stateOrder[a.state] ?? 99;
      final orderB = stateOrder[b.state] ?? 99;
      
      if (orderA != orderB) {
        return orderA.compareTo(orderB);
      }
      
      return a.displayName.compareTo(b.displayName);
    });

    return filtered;
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // 顶部操作栏
        Container(
          padding: const EdgeInsets.all(16.0),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surfaceContainerLow,
            border: Border(
              bottom: BorderSide(
                color: Theme.of(context).colorScheme.outline.withValues(alpha: 0.2),
              ),
            ),
          ),
          child: Row(
            children: [
              Text(
                '连接器管理',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const Spacer(),
              IconButton(
                icon: const Icon(Icons.refresh),
                onPressed: _refreshData,
                tooltip: '刷新',
              ),
              IconButton(
                icon: const Icon(Icons.add),
                onPressed: _showCreateInstanceDialog,
                tooltip: '新建连接器实例',
              ),
            ],
          ),
        ),
        _buildSearchAndFilter(),
        Expanded(
          child: _buildContent(),
        ),
      ],
    );
  }

  Widget _buildSearchAndFilter() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          // 搜索框
          TextField(
            decoration: const InputDecoration(
              hintText: '搜索连接器...',
              prefixIcon: Icon(Icons.search),
              border: OutlineInputBorder(),
              isDense: true,
            ),
            onChanged: (value) {
              setState(() {
                _searchQuery = value;
              });
            },
          ),
          const SizedBox(height: 12),
          // 状态过滤器
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                const Text('状态: '),
                const SizedBox(width: 8),
                _buildStateFilterChip('全部', null),
                const SizedBox(width: 8),
                _buildStateFilterChip('运行中', ConnectorState.running),
                const SizedBox(width: 8),
                _buildStateFilterChip('已启用', ConnectorState.enabled),
                const SizedBox(width: 8),
                _buildStateFilterChip('已配置', ConnectorState.configured),
                const SizedBox(width: 8),
                _buildStateFilterChip('错误', ConnectorState.error),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStateFilterChip(String label, ConnectorState? state) {
    final isSelected = _stateFilter == state;
    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (selected) {
        setState(() {
          _stateFilter = selected ? state : null;
        });
      },
    );
  }

  Widget _buildContent() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (_errorMessage != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              _errorMessage!,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: Theme.of(context).colorScheme.error,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _refreshData,
              child: const Text('重试'),
            ),
          ],
        ),
      );
    }

    final filteredInstances = _filteredInstances;

    if (filteredInstances.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.extension_off,
              size: 64,
              color: Theme.of(context).disabledColor,
            ),
            const SizedBox(height: 16),
            Text(
              _instances.isEmpty ? '还没有连接器实例' : '没有找到匹配的连接器',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: Theme.of(context).disabledColor,
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _showCreateInstanceDialog,
              icon: const Icon(Icons.add),
              label: const Text('创建连接器实例'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _refreshData,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: filteredInstances.length,
        itemBuilder: (context, index) {
          final instance = filteredInstances[index];
          return _buildInstanceCard(instance);
        },
      ),
    );
  }

  Widget _buildInstanceCard(ConnectorInstanceInfo instance) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ExpansionTile(
        leading: _buildStateIndicator(instance.state),
        title: Text(
          instance.displayName,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('类型: ${instance.typeName}'),
            if (instance.errorMessage != null)
              Text(
                '错误: ${instance.errorMessage}',
                style: TextStyle(
                  color: Theme.of(context).colorScheme.error,
                  fontSize: 12,
                ),
              ),
          ],
        ),
        trailing: _buildInstanceActions(instance),
        children: [
          _buildInstanceDetails(instance),
        ],
      ),
    );
  }

  Widget _buildStateIndicator(ConnectorState state) {
    Color color;
    IconData icon;

    switch (state) {
      case ConnectorState.running:
        color = Colors.green;
        icon = Icons.play_circle_filled;
        break;
      case ConnectorState.enabled:
        color = Colors.blue;
        icon = Icons.check_circle;
        break;
      case ConnectorState.configured:
        color = Colors.orange;
        icon = Icons.settings;
        break;
      case ConnectorState.error:
        color = Colors.red;
        icon = Icons.error;
        break;
      case ConnectorState.stopping:
        color = Colors.grey;
        icon = Icons.stop_circle;
        break;
      default:
        color = Colors.grey;
        icon = Icons.help_outline;
    }

    return Icon(
      icon,
      color: color,
      size: 32,
    );
  }

  Widget _buildInstanceActions(ConnectorInstanceInfo instance) {
    return PopupMenuButton<String>(
      onSelected: (action) => _handleInstanceAction(instance, action),
      itemBuilder: (context) {
        final items = <PopupMenuEntry<String>>[];

        switch (instance.state) {
          case ConnectorState.running:
            items.addAll([
              const PopupMenuItem(value: 'stop', child: Text('停止')),
              const PopupMenuItem(value: 'restart', child: Text('重启')),
            ]);
            break;
          case ConnectorState.enabled:
          case ConnectorState.configured:
            items.add(const PopupMenuItem(value: 'start', child: Text('启动')));
            break;
          case ConnectorState.error:
            items.addAll([
              const PopupMenuItem(value: 'start', child: Text('重新启动')),
              const PopupMenuItem(value: 'stop', child: Text('强制停止')),
            ]);
            break;
          default:
            break;
        }

        items.addAll([
          const PopupMenuDivider(),
          const PopupMenuItem(value: 'edit', child: Text('编辑配置')),
          const PopupMenuItem(value: 'delete', child: Text('删除实例')),
        ]);

        return items;
      },
      child: const Icon(Icons.more_vert),
    );
  }

  Widget _buildInstanceDetails(ConnectorInstanceInfo instance) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildDetailRow('实例ID', instance.instanceId),
          _buildDetailRow('类型ID', instance.typeId),
          _buildDetailRow('状态', _getStateDisplayName(instance.state)),
          if (instance.processId != null)
            _buildDetailRow('进程ID', instance.processId.toString()),
          if (instance.lastHeartbeat != null)
            _buildDetailRow('最后心跳', _formatDateTime(instance.lastHeartbeat!)),
          _buildDetailRow('数据量', '${instance.dataCount} 条'),
          if (instance.createdAt != null)
            _buildDetailRow('创建时间', _formatDateTime(instance.createdAt!)),
          if (instance.updatedAt != null)
            _buildDetailRow('更新时间', _formatDateTime(instance.updatedAt!)),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          SizedBox(
            width: 80,
            child: Text(
              '$label:',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
        ],
      ),
    );
  }

  String _getStateDisplayName(ConnectorState state) {
    switch (state) {
      case ConnectorState.running:
        return '运行中';
      case ConnectorState.enabled:
        return '已启用';
      case ConnectorState.configured:
        return '已配置';
      case ConnectorState.error:
        return '错误';
      case ConnectorState.stopping:
        return '停止中';
      case ConnectorState.available:
        return '可用';
      case ConnectorState.installed:
        return '已安装';
      case ConnectorState.updating:
        return '更新中';
      case ConnectorState.uninstalling:
        return '卸载中';
    }
  }

  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.year}-${dateTime.month.toString().padLeft(2, '0')}-${dateTime.day.toString().padLeft(2, '0')} '
           '${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }

  Future<void> _handleInstanceAction(ConnectorInstanceInfo instance, String action) async {
    try {
      switch (action) {
        case 'start':
          await _apiClient.startConnectorInstance(instance.instanceId);
          break;
        case 'stop':
          await _apiClient.stopConnectorInstance(instance.instanceId);
          break;
        case 'restart':
          await _apiClient.restartConnectorInstance(instance.instanceId);
          break;
        case 'edit':
          await _showEditConfigDialog(instance);
          return; // 不刷新，让编辑对话框处理
        case 'delete':
          await _confirmAndDeleteInstance(instance);
          return; // 不刷新，让删除处理刷新
      }

      // 刷新数据
      await _refreshData();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('操作成功: $action')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('操作失败: $e'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }

  Future<void> _showCreateInstanceDialog() async {
    if (_connectorTypes.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('没有可用的连接器类型')),
      );
      return;
    }

    // TODO: 实现创建实例对话框
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('创建实例功能开发中...')),
    );
  }

  Future<void> _showEditConfigDialog(ConnectorInstanceInfo instance) async {
    // TODO: 实现配置编辑对话框
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('配置编辑功能开发中...')),
    );
  }

  Future<void> _confirmAndDeleteInstance(ConnectorInstanceInfo instance) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('确认删除'),
        content: Text('确定要删除连接器实例 "${instance.displayName}" 吗？\n\n此操作不可撤销。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: ElevatedButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
            child: const Text('删除'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      try {
        await _apiClient.deleteConnectorInstance(instance.instanceId);
        await _refreshData();
        
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('连接器实例已删除')),
          );
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('删除失败: $e'),
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
          );
        }
      }
    }
  }

  @override
  void dispose() {
    super.dispose();
  }
}