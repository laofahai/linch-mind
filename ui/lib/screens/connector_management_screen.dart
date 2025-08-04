import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
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
  
  List<ConnectorInfo> _connectors = [];
  bool _isLoading = true;
  String? _errorMessage;
  String _searchQuery = '';

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
      // 加载连接器列表
      final connectorResponse = await _apiClient.getConnectors();

      setState(() {
        _connectors = connectorResponse.collectors;
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

  List<ConnectorInfo> get _filteredConnectors {
    var filtered = _connectors.where((connector) {
      // 搜索过滤
      if (_searchQuery.isNotEmpty) {
        final query = _searchQuery.toLowerCase();
        if (!connector.displayName.toLowerCase().contains(query) &&
            !connector.collectorId.toLowerCase().contains(query)) {
          return false;
        }
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
                onPressed: _showAddConnectorDialog,
                tooltip: '添加连接器',
              ),
              IconButton(
                icon: const Icon(Icons.settings),
                onPressed: _showConnectorSettings,
                tooltip: '连接器设置',
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
      child: TextField(
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

    final filteredConnectors = _filteredConnectors;

    if (filteredConnectors.isEmpty) {
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
              _connectors.isEmpty ? '还没有发现连接器' : '没有找到匹配的连接器',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: Theme.of(context).disabledColor,
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _refreshData,
              icon: const Icon(Icons.refresh),
              label: const Text('刷新连接器'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _refreshData,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: filteredConnectors.length,
        itemBuilder: (context, index) {
          final connector = filteredConnectors[index];
          return _buildConnectorCard(connector);
        },
      ),
    );
  }

  Widget _buildConnectorCard(ConnectorInfo connector) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ExpansionTile(
        leading: _buildStateIndicator(connector.state),
        title: Text(
          connector.displayName,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('ID: ${connector.collectorId}'),
            if (connector.errorMessage != null)
              Text(
                '错误: ${connector.errorMessage}',
                style: TextStyle(
                  color: Theme.of(context).colorScheme.error,
                  fontSize: 12,
                ),
              ),
          ],
        ),
        trailing: _buildConnectorActions(connector),
        children: [
          _buildConnectorDetails(connector),
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

  Widget _buildConnectorActions(ConnectorInfo connector) {
    return PopupMenuButton<String>(
      onSelected: (action) => _handleConnectorAction(connector, action),
      itemBuilder: (context) {
        final items = <PopupMenuEntry<String>>[];

        switch (connector.state) {
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
        ]);

        return items;
      },
      child: const Icon(Icons.more_vert),
    );
  }

  Widget _buildConnectorDetails(ConnectorInfo connector) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildDetailRow('连接器ID', connector.collectorId),
          _buildDetailRow('状态', _getStateDisplayName(connector.state)),
          if (connector.processId != null)
            _buildDetailRow('进程ID', connector.processId.toString()),
          if (connector.lastHeartbeat != null)
            _buildDetailRow('最后心跳', _formatDateTime(connector.lastHeartbeat!)),
          _buildDetailRow('数据量', '${connector.dataCount} 条'),
          if (connector.createdAt != null)
            _buildDetailRow('创建时间', _formatDateTime(connector.createdAt!)),
          if (connector.updatedAt != null)
            _buildDetailRow('更新时间', _formatDateTime(connector.updatedAt!)),
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

  Future<void> _handleConnectorAction(ConnectorInfo connector, String action) async {
    try {
      switch (action) {
        case 'start':
          await _apiClient.startConnector(connector.collectorId);
          break;
        case 'stop':
          await _apiClient.stopConnector(connector.collectorId);
          break;
        case 'restart':
          await _apiClient.restartConnector(connector.collectorId);
          break;
        case 'edit':
          await _showEditConfigDialog(connector);
          return; // 不刷新，让编辑对话框处理
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

  Future<void> _showAddConnectorDialog() async {
    String? selectedPath;
    bool isScanning = false;
    String? errorMessage;
    List<ConnectorDefinition> availableConnectors = [];

    await showDialog<void>(
      context: context,
      builder: (BuildContext context) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              title: const Text('添加连接器'),
              content: SizedBox(
                width: 500,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('选择连接器目录:'),
                    const SizedBox(height: 4),
                    Text(
                      '支持选择连接器根目录或具体连接器目录\n例如: connectors/ 或 connectors/official/filesystem',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Theme.of(context).disabledColor,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            selectedPath ?? '未选择目录',
                            style: TextStyle(
                              color: selectedPath != null 
                                ? Theme.of(context).textTheme.bodyMedium?.color 
                                : Theme.of(context).disabledColor,
                            ),
                          ),
                        ),
                        ElevatedButton(
                          onPressed: isScanning ? null : () async {
                            try {
                              String? directoryPath = await FilePicker.platform.getDirectoryPath(
                                dialogTitle: '选择连接器目录（支持根目录或具体连接器目录）',
                              );
                              
                              if (directoryPath != null) {
                                // 检查是否选择了具体的连接器目录
                                final dirName = directoryPath.split('/').last;
                                
                                // 验证目录是否包含连接器必要文件
                                // 这里可以根据实际需求添加更多验证
                                if (dirName.isEmpty) {
                                  setDialogState(() {
                                    errorMessage = '请选择具体的连接器目录，如: filesystem';
                                  });
                                  return;
                                }
                                
                                setDialogState(() {
                                  selectedPath = directoryPath;
                                  errorMessage = null;
                                });
                                
                                // 自动触发扫描
                                if (selectedPath != null) {
                                  // 延迟100ms执行扫描，让UI更新
                                  Future.delayed(const Duration(milliseconds: 100), () async {
                                    setDialogState(() {
                                      isScanning = true;
                                      errorMessage = null;
                                      availableConnectors = [];
                                    });

                                    try {
                                      final response = await _apiClient.scanConnectorDirectory(selectedPath!);
                                      setDialogState(() {
                                        availableConnectors = response.connectors;
                                        isScanning = false;
                                        if (availableConnectors.isEmpty) {
                                          errorMessage = '该目录中未发现有效的连接器。\n请确保所选目录包含 connector.json 文件，或选择包含连接器子目录的父目录。';
                                        }
                                      });
                                    } catch (e) {
                                      setDialogState(() {
                                        errorMessage = '扫描目录失败: $e';
                                        isScanning = false;
                                      });
                                    }
                                  });
                                }
                              }
                            } catch (e) {
                              setDialogState(() {
                                errorMessage = '选择目录失败: $e';
                              });
                            }
                          },
                          child: const Text('选择目录'),
                        ),
                      ],
                    ),
                    if (selectedPath != null && !isScanning && availableConnectors.isEmpty) ...[
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          ElevatedButton(
                            onPressed: () async {
                              setDialogState(() {
                                isScanning = true;
                                errorMessage = null;
                                availableConnectors = [];
                              });

                              try {
                                final response = await _apiClient.scanConnectorDirectory(selectedPath!);
                                setDialogState(() {
                                  availableConnectors = response.connectors;
                                  isScanning = false;
                                  if (availableConnectors.isEmpty) {
                                    errorMessage = '该目录中未发现有效的连接器。\n请确保所选目录包含 connector.json 文件，或选择包含连接器子目录的父目录。';
                                  }
                                });
                              } catch (e) {
                                setDialogState(() {
                                  errorMessage = '扫描目录失败: $e';
                                  isScanning = false;
                                });
                              }
                            },
                            child: const Text('重新扫描'),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            '未发现连接器，请重新扫描或选择其他目录',
                            style: TextStyle(
                              color: Theme.of(context).disabledColor,
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ],
                    if (isScanning) ...[
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          ),
                          const SizedBox(width: 8),
                          const Text('正在扫描连接器...'),
                        ],
                      ),
                    ],
                    if (errorMessage != null) ...[
                      const SizedBox(height: 8),
                      Text(
                        errorMessage!,
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.error,
                          fontSize: 12,
                        ),
                      ),
                    ],
                    if (availableConnectors.isNotEmpty) ...[
                      const SizedBox(height: 16),
                      const Text('发现的连接器:'),
                      const SizedBox(height: 8),
                      Container(
                        constraints: const BoxConstraints(maxHeight: 200),
                        child: ListView.builder(
                          shrinkWrap: true,
                          itemCount: availableConnectors.length,
                          itemBuilder: (context, index) {
                            final type = availableConnectors[index];
                            return Card(
                              child: ListTile(
                                title: Text(type.displayName),
                                subtitle: Text('ID: ${type.connectorId}\n版本: ${type.version}'),
                                trailing: ElevatedButton(
                                  onPressed: () => _createConnectorInstance(type),
                                  child: const Text('创建'),
                                ),
                              ),
                            );
                          },
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('取消'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _createConnectorInstance(ConnectorDefinition type) async {
    try {
      // 创建请求，包含连接器路径信息
      final config = <String, dynamic>{};
      
      // 如果type包含path信息，添加到config中
      if (type.path != null) {
        config['path'] = type.path;
      }
      
      final request = CreateConnectorRequest(
        connectorId: type.connectorId,
        displayName: type.displayName,
        config: config,
        autoStart: true,
      );

      await _apiClient.createConnector(request);
      
      if (mounted) {
        Navigator.of(context).pop(); // 关闭对话框
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('成功创建连接器: ${type.displayName}')),
        );
        await _refreshData(); // 刷新列表
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('创建连接器失败: $e'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }

  Future<void> _showConnectorSettings() async {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('连接器设置功能暂未实现')),
    );
  }

  Future<void> _showEditConfigDialog(ConnectorInfo connector) async {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('配置编辑功能暂未实现')),
    );
  }


  @override
  void dispose() {
    super.dispose();
  }
}