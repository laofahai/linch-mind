import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import '../models/connector_lifecycle_models.dart';
import '../services/connector_lifecycle_api_client.dart';
import '../services/registry_api_client.dart';
import '../providers/app_error_provider.dart';
import '../widgets/connector_status_widget.dart';
import '../utils/app_logger.dart';
import 'connector_config_screen.dart';

/// 连接器管理主界面 - 工具箱+应用商店双重体验
class ConnectorManagementScreen extends ConsumerStatefulWidget {
  const ConnectorManagementScreen({super.key});

  @override
  ConsumerState<ConnectorManagementScreen> createState() =>
      _ConnectorManagementScreenState();
}

class _ConnectorManagementScreenState
    extends ConsumerState<ConnectorManagementScreen>
    with TickerProviderStateMixin {
  final _apiClient = ConnectorLifecycleApiService.instance;

  // Tab控制器
  late TabController _tabController;

  // 已安装连接器数据
  List<ConnectorInfo> _installedConnectors = [];
  bool _installedLoading = true;
  String? _installedErrorMessage;
  String _installedSearchQuery = '';

  // 市场连接器数据
  List<ConnectorDefinition> _marketConnectors = [];
  bool _marketLoading = false;
  String? _marketErrorMessage;
  String _marketSearchQuery = '';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    // 延迟加载以确保组件完全初始化
    Future.microtask(() => _loadInstalledConnectors());
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadInstalledConnectors() async {
    AppLogger.uiDebug('开始加载已安装连接器');
    
    if (!mounted) return;
    
    setState(() {
      _installedLoading = true;
      _installedErrorMessage = null;
    });

    try {
      // 只获取真正已安装的连接器（从数据库）
      AppLogger.uiDebug('调用getConnectors API');
      final connectorResponse = await _apiClient.getConnectors();
      AppLogger.uiDebug('API响应完成', data: {
        'success': connectorResponse.success,
        'count': connectorResponse.connectors.length
      });

      if (!mounted) return;

      setState(() {
        _installedConnectors = connectorResponse.connectors;
        _installedLoading = false;
      });
      AppLogger.uiDebug('UI状态更新完成',
          data: {'installed_connectors_length': _installedConnectors.length});
          
      // 如果加载成功但连接器列表为空，显示提示
      if (_installedConnectors.isEmpty) {
        AppLogger.uiInfo('已安装连接器列表为空');
      }
    } catch (e, stackTrace) {
      AppLogger.uiError('加载已安装连接器失败', exception: e, stackTrace: stackTrace);

      if (!mounted) return;

      // 添加到错误管理器
      ref.read(appErrorProvider.notifier).handleException(
            e,
            operation: '加载已安装连接器',
            stackTrace: stackTrace,
            retryCallback: () => _loadInstalledConnectors(),
          );

      setState(() {
        _installedErrorMessage = '加载连接器失败: $e';
        _installedLoading = false;
      });
    }
  }

  Future<void> _loadMarketConnectors() async {
    if (_marketConnectors.isNotEmpty) return; // 已加载过

    setState(() {
      _marketLoading = true;
      _marketErrorMessage = null;
    });

    try {
      // 从Registry API获取市场连接器，添加超时处理
      final marketConnectors = await RegistryApiClient.getMarketConnectors().timeout(
        const Duration(seconds: 15),
        onTimeout: () {
          throw Exception('加载市场连接器超时（15秒），请检查网络连接');
        },
      );

      if (mounted) {
        setState(() {
          _marketConnectors = marketConnectors;
          _marketLoading = false;
        });
      }
    } catch (e) {
      // 添加到错误管理器
      ref.read(appErrorProvider.notifier).handleException(
            e,
            operation: '加载市场连接器',
            retryCallback: () => _loadMarketConnectors(),
          );

      setState(() {
        _marketErrorMessage = '加载市场连接器失败: $e';
        _marketLoading = false;
      });
    }
  }

  Future<void> _refreshInstalledConnectors() async {
    await _loadInstalledConnectors();
  }

  Future<void> _refreshMarketConnectors() async {
    setState(() {
      _marketLoading = true;
      _marketConnectors = [];
      _marketErrorMessage = null;
    });

    try {
      await _loadMarketConnectors();
    } catch (e) {
      setState(() {
        _marketErrorMessage = '刷新市场连接器失败: $e';
        _marketLoading = false;
      });
    }
  }

  List<ConnectorInfo> get _filteredInstalledConnectors {
    var filtered = _installedConnectors.where((connector) {
      if (_installedSearchQuery.isNotEmpty) {
        final query = _installedSearchQuery.toLowerCase();
        if (!connector.displayName.toLowerCase().contains(query) &&
            !connector.connectorId.toLowerCase().contains(query)) {
          return false;
        }
      }
      return true;
    }).toList();

    filtered.sort((a, b) => a.displayName.compareTo(b.displayName));
    return filtered;
  }

  List<ConnectorDefinition> get _filteredMarketConnectors {
    var filtered = _marketConnectors.where((connector) {
      if (_marketSearchQuery.isNotEmpty) {
        final query = _marketSearchQuery.toLowerCase();
        if (!connector.displayName.toLowerCase().contains(query) &&
            !connector.description.toLowerCase().contains(query) &&
            !connector.category.toLowerCase().contains(query)) {
          return false;
        }
      }
      return true;
    }).toList();

    filtered.sort((a, b) => a.displayName.compareTo(b.displayName));
    return filtered;
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Tab导航
        Container(
          color: Theme.of(context).colorScheme.surfaceContainerLow,
          child: TabBar(
            controller: _tabController,
            onTap: (index) {
              if (index == 1 && _marketConnectors.isEmpty) {
                _loadMarketConnectors();
              }
            },
            tabs: const [
              Tab(
                icon: Icon(Icons.inventory_2),
                text: '我的连接器',
                iconMargin: EdgeInsets.only(bottom: 4),
              ),
              Tab(
                icon: Icon(Icons.store),
                text: '发现更多',
                iconMargin: EdgeInsets.only(bottom: 4),
              ),
            ],
          ),
        ),
        Expanded(
          child: TabBarView(
            controller: _tabController,
            children: [
              _buildInstalledConnectorsTab(),
              _buildMarketConnectorsTab(),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildInstalledConnectorsTab() {
    return Column(
      children: [
        _buildInstalledSearchAndFilter(),
        _buildInstalledStatusOverview(),
        Expanded(
          child: _buildInstalledContent(),
        ),
      ],
    );
  }

  Widget _buildMarketConnectorsTab() {
    return Column(
      children: [
        _buildMarketSearchAndCategory(),
        Expanded(
          child: _buildMarketContent(),
        ),
      ],
    );
  }

  Widget _buildInstalledSearchAndFilter() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        border: Border(
          bottom: BorderSide(
            color: Theme.of(context).colorScheme.outline.withValues(alpha: 0.1),
          ),
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              decoration: const InputDecoration(
                hintText: '搜索连接器...',
                prefixIcon: Icon(Icons.search),
                border: OutlineInputBorder(),
                isDense: true,
              ),
              onChanged: (value) {
                setState(() {
                  _installedSearchQuery = value;
                });
              },
            ),
          ),
          const SizedBox(width: 8),
          IconButton(
            icon: const Icon(Icons.add_circle_outline),
            onPressed: _showAddConnectorDialog,
            tooltip: '添加本地连接器',
          ),
          const SizedBox(width: 4),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _refreshInstalledConnectors,
            tooltip: '刷新',
          ),
        ],
      ),
    );
  }

  Widget _buildMarketSearchAndCategory() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        border: Border(
          bottom: BorderSide(
            color: Theme.of(context).colorScheme.outline.withValues(alpha: 0.1),
          ),
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              decoration: const InputDecoration(
                hintText: '搜索连接器...',
                prefixIcon: Icon(Icons.search),
                border: OutlineInputBorder(),
                isDense: true,
              ),
              onChanged: (value) {
                setState(() {
                  _marketSearchQuery = value;
                });
              },
            ),
          ),
          const SizedBox(width: 8),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _refreshMarketConnectors,
            tooltip: '刷新',
          ),
        ],
      ),
    );
  }

  Widget _buildInstalledStatusOverview() {
    if (_installedLoading || _installedConnectors.isEmpty) {
      return const SizedBox.shrink();
    }

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: ConnectorStatusOverview(
        connectors: _installedConnectors,
      ),
    );
  }


  Widget _buildInstalledContent() {
    if (_installedLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (_installedErrorMessage != null) {
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
              _installedErrorMessage!,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Theme.of(context).colorScheme.error,
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _refreshInstalledConnectors,
              child: const Text('重试'),
            ),
          ],
        ),
      );
    }

    final filteredConnectors = _filteredInstalledConnectors;

    if (filteredConnectors.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.inventory_2_outlined,
              size: 64,
              color: Theme.of(context).disabledColor,
            ),
            const SizedBox(height: 16),
            Text(
              _installedConnectors.isEmpty ? '还没有安装连接器' : '没有找到匹配的连接器',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Theme.of(context).disabledColor,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              _installedConnectors.isEmpty
                  ? '试试从"发现更多"中安装，或添加本地连接器'
                  : '调整搜索条件或筛选器',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).disabledColor,
                  ),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _installedConnectors.isEmpty
                  ? () => _tabController.animateTo(1)
                  : _refreshInstalledConnectors,
              icon: Icon(
                  _installedConnectors.isEmpty ? Icons.store : Icons.refresh),
              label: Text(_installedConnectors.isEmpty ? '发现连接器' : '刷新列表'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _refreshInstalledConnectors,
      child: LayoutBuilder(
        builder: (context, constraints) {
          // 根据屏幕宽度计算列数，每列最小宽度350px
          final crossAxisCount =
              (constraints.maxWidth / 350).floor().clamp(1, 4);

          return GridView.builder(
            padding: const EdgeInsets.all(16),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: crossAxisCount,
              childAspectRatio: 3.0, // 调整为更适合的高宽比，避免溢出
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
            ),
            itemCount: filteredConnectors.length,
            itemBuilder: (context, index) {
              final connector = filteredConnectors[index];
              return _buildInstalledConnectorCard(connector);
            },
          );
        },
      ),
    );
  }

  Widget _buildMarketContent() {
    if (_marketLoading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('正在加载市场连接器...'),
          ],
        ),
      );
    }

    if (_marketErrorMessage != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.cloud_off,
              size: 64,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              _marketErrorMessage!,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Theme.of(context).colorScheme.error,
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _refreshMarketConnectors,
              child: const Text('重试'),
            ),
          ],
        ),
      );
    }

    final filteredConnectors = _filteredMarketConnectors;

    if (filteredConnectors.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.store_outlined,
              size: 64,
              color: Theme.of(context).disabledColor,
            ),
            const SizedBox(height: 16),
            Text(
              '没有找到匹配的连接器',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Theme.of(context).disabledColor,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              '尝试调整搜索词或选择不同的分类',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).disabledColor,
                  ),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _refreshMarketConnectors,
      child: LayoutBuilder(
        builder: (context, constraints) {
          // 根据屏幕宽度计算列数，每列最小宽度380px（市场卡片信息更多）
          final crossAxisCount =
              (constraints.maxWidth / 380).floor().clamp(1, 3);

          return GridView.builder(
            padding: const EdgeInsets.all(16),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: crossAxisCount,
              childAspectRatio: 2.2, // 调整为垂直卡片布局
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
            ),
            itemCount: filteredConnectors.length,
            itemBuilder: (context, index) {
              final connector = filteredConnectors[index];
              return _buildMarketConnectorCard(connector);
            },
          );
        },
      ),
    );
  }

  Widget _buildInstalledConnectorCard(ConnectorInfo connector) {
    return ConnectorStatusWidget(
      connector: connector,
      onRefresh: () => _refreshConnectorStatus(connector),
      onRestart: () => _restartConnector(connector),
      onConfigure: () => _configureConnector(connector),
    );
  }

  /// 刷新连接器状态
  Future<void> _refreshConnectorStatus(ConnectorInfo connector) async {
    try {
      AppLogger.uiDebug('刷新连接器状态: ${connector.connectorId}');
      // 刷新整个连接器列表
      await _refreshInstalledConnectors();
    } catch (e) {
      ref.read(appErrorProvider.notifier).handleException(
            e,
            operation: '刷新连接器状态: ${connector.connectorId}',
            retryCallback: () => _refreshConnectorStatus(connector),
          );
    }
  }

  /// 重启连接器
  Future<void> _restartConnector(ConnectorInfo connector) async {
    try {
      AppLogger.uiInfo('重启连接器: ${connector.connectorId}');

      // 停止连接器
      if (connector.state == ConnectorState.running) {
        await _apiClient.stopConnector(connector.connectorId);
        await Future.delayed(const Duration(milliseconds: 500));
      }

      // 启动连接器
      await _apiClient.startConnector(connector.connectorId);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('已重启连接器: ${connector.displayName}'),
            backgroundColor: Colors.green,
          ),
        );
      }

      // 刷新状态
      await _refreshConnectorStatus(connector);
    } catch (e) {
      ref.read(appErrorProvider.notifier).handleException(
            e,
            operation: '重启连接器: ${connector.connectorId}',
            retryCallback: () => _restartConnector(connector),
          );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('重启连接器失败: ${connector.displayName}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  /// 配置连接器
  Future<void> _configureConnector(ConnectorInfo connector) async {
    if (mounted) {
      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (context) => ConnectorConfigScreen(
            connectorId: connector.connectorId,
            connectorName: connector.displayName,
          ),
        ),
      );
    }
  }


  Widget _buildMarketConnectorCard(ConnectorDefinition connector) {
    final isInstalled = connector.isRegistered ?? false;

    return Card(
      elevation: isInstalled ? 1 : 2,
      child: Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                // 图标
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: isInstalled
                        ? Theme.of(context).colorScheme.surfaceContainerHigh
                        : Theme.of(context).colorScheme.primaryContainer,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    _getCategoryIcon(connector.category),
                    size: 20,
                    color: isInstalled
                        ? Theme.of(context)
                            .colorScheme
                            .onSurface
                            .withValues(alpha: 0.6)
                        : Theme.of(context).colorScheme.onPrimaryContainer,
                  ),
                ),
                const SizedBox(width: 12),

                // 标题和标签
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              connector.displayName,
                              style: Theme.of(context)
                                  .textTheme
                                  .titleSmall
                                  ?.copyWith(
                                    fontWeight: FontWeight.w600,
                                    color: isInstalled
                                        ? Theme.of(context)
                                            .colorScheme
                                            .onSurface
                                            .withValues(alpha: 0.7)
                                        : null,
                                  ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          if (connector.author == 'Linch Mind Team') ...[
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: Theme.of(context)
                                    .colorScheme
                                    .secondaryContainer,
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Text(
                                '官方',
                                style: TextStyle(
                                  fontSize: 10,
                                  color: Theme.of(context)
                                      .colorScheme
                                      .onSecondaryContainer,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ),
                          ],
                        ],
                      ),
                      const SizedBox(height: 2),
                      Text(
                        connector.category,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Theme.of(context).colorScheme.primary,
                              fontSize: 11,
                              fontWeight: FontWeight.w500,
                            ),
                      ),
                    ],
                  ),
                ),
              ],
            ),

            const SizedBox(height: 12),

            // 描述
            Text(
              connector.description,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context)
                        .colorScheme
                        .onSurface
                        .withValues(alpha: 0.7),
                    fontSize: 13,
                    height: 1.4,
                  ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),

            const SizedBox(height: 16),

            // 底部操作区
            Row(
              children: [
                Text(
                  'v${connector.version}',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Theme.of(context).disabledColor,
                        fontSize: 10,
                      ),
                ),
                const Spacer(),
                if (isInstalled) ...[
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: Colors.green.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: Colors.green.withValues(alpha: 0.3),
                        width: 1,
                      ),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.check, size: 14, color: Colors.green),
                        const SizedBox(width: 4),
                        Text(
                          '已安装',
                          style: TextStyle(
                            color: Colors.green.shade700,
                            fontSize: 11,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                ] else ...[
                  FilledButton(
                    onPressed: () => _installMarketConnector(connector),
                    style: FilledButton.styleFrom(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 16, vertical: 8),
                      minimumSize: const Size(0, 32),
                    ),
                    child: const Text('安装', style: TextStyle(fontSize: 12)),
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }

  IconData _getCategoryIcon(String category) {
    switch (category.toLowerCase()) {
      case '文件':
      case '知识管理':
        return Icons.folder;
      case '浏览器':
        return Icons.web;
      case '通讯':
        return Icons.chat;
      case '自动化':
        return Icons.auto_awesome;
      case '开发':
        return Icons.code;
      case '效率':
        return Icons.trending_up;
      default:
        return Icons.extension;
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
              title: const Text('添加本地连接器'),
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
                                  ? Theme.of(context)
                                      .textTheme
                                      .bodyMedium
                                      ?.color
                                  : Theme.of(context).disabledColor,
                            ),
                          ),
                        ),
                        ElevatedButton(
                          onPressed: isScanning
                              ? null
                              : () async {
                                  try {
                                    String? directoryPath = await FilePicker
                                        .platform
                                        .getDirectoryPath(
                                      dialogTitle: '选择连接器目录（支持根目录或具体连接器目录）',
                                    );

                                    if (directoryPath != null) {
                                      setDialogState(() {
                                        selectedPath = directoryPath;
                                        errorMessage = null;
                                      });

                                      // 自动触发扫描
                                      if (selectedPath != null) {
                                        Future.delayed(
                                            const Duration(milliseconds: 100),
                                            () async {
                                          setDialogState(() {
                                            isScanning = true;
                                            errorMessage = null;
                                            availableConnectors = [];
                                          });

                                          try {
                                            // 添加超时处理，防止UI卡死
                                            final response = await _apiClient
                                                .scanConnectorDirectory(
                                                    selectedPath!)
                                                .timeout(
                                              const Duration(seconds: 15),
                                              onTimeout: () {
                                                throw Exception('扫描目录超时（15秒），请检查目录权限或选择较小的目录');
                                              },
                                            );
                                            
                                            if (mounted) {
                                              setDialogState(() {
                                                availableConnectors =
                                                    response.connectors;
                                                isScanning = false;
                                                if (availableConnectors.isEmpty) {
                                                  errorMessage =
                                                      '该目录中未发现有效的连接器。\n请确保所选目录包含 connector.json 文件，或选择包含连接器子目录的父目录。';
                                                }
                                              });
                                            }
                                          } catch (e) {
                                            if (mounted) {
                                              setDialogState(() {
                                                errorMessage = '扫描目录失败: $e';
                                                isScanning = false;
                                              });
                                            }
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
                    if (isScanning) ...[
                      const SizedBox(height: 16),
                      const Row(
                        children: [
                          SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          ),
                          SizedBox(width: 8),
                          Text('正在扫描连接器...'),
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
                                subtitle: Text(
                                    'ID: ${type.connectorId}\n版本: ${type.version}'),
                                trailing: ElevatedButton(
                                  onPressed: () =>
                                      _createConnectorInstance(type),
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
      final config = <String, dynamic>{};

      if (type.path != null) {
        config['path'] = type.path;
      }

      final request = CreateConnectorRequest(
        connectorId: type.connectorId,
        displayName: type.displayName,
        config: config,
        // 移除 autoStart 字段，连接器创建后默认启用
      );

      await _apiClient.createConnector(request);

      if (mounted) {
        Navigator.of(context).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('成功创建连接器: ${type.displayName}')),
        );
        // 刷新已安装连接器列表和市场状态
        await _refreshInstalledConnectors();
        await _refreshMarketConnectors();
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



  Future<void> _installMarketConnector(ConnectorDefinition connector) async {
    try {
      // 显示安装中状态
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('正在安装 ${connector.displayName}...'),
          duration: const Duration(seconds: 2),
        ),
      );

      // 调用安装API
      await _apiClient.installFromRegistry(connector.connectorId);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${connector.displayName} 安装成功'),
            backgroundColor: Colors.green,
          ),
        );

        // 刷新已安装连接器列表
        await _refreshInstalledConnectors();

        // 刷新市场连接器列表以更新安装状态
        await _refreshMarketConnectors();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('安装失败: $e'),
            backgroundColor: Theme.of(context).colorScheme.error,
            duration: const Duration(seconds: 4),
          ),
        );
      }
    }
  }




}
