import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import '../models/connector_lifecycle_models.dart';
import '../services/connector_lifecycle_api_client.dart';
import '../services/registry_api_client.dart';
import 'connector_config_screen.dart';

// 已安装连接器筛选枚举
enum InstalledConnectorFilter {
  all,
  running,
  stopped,
  error,
  highActivity,
  noData,
}

// 已安装连接器排序枚举
enum InstalledConnectorSort {
  status,
  activity,
  dataCount,
  lastHeartbeat,
}

// 市场连接器分类枚举
enum MarketConnectorCategory {
  all,
  filesystem,
  communication,
  automation,
  development,
  productivity,
}

// 市场连接器排序枚举
enum MarketConnectorSort {
  recommended,
  newest,
  popular,
  rating,
}

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

  // 筛选器
  InstalledConnectorFilter _installedFilter = InstalledConnectorFilter.all;
  InstalledConnectorSort _installedSort = InstalledConnectorSort.status;
  MarketConnectorCategory _marketCategory = MarketConnectorCategory.all;
  MarketConnectorSort _marketSort = MarketConnectorSort.recommended;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadInstalledConnectors();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadInstalledConnectors() async {
    setState(() {
      _installedLoading = true;
      _installedErrorMessage = null;
    });

    try {
      final connectorResponse = await _apiClient.getConnectors();
      setState(() {
        _installedConnectors = connectorResponse.collectors;
        _installedLoading = false;
      });
    } catch (e) {
      setState(() {
        _installedErrorMessage = '加载已安装连接器失败: $e';
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
      // 使用真实的Registry API
      final registryConnectors = await RegistryApiClient.getMarketConnectors();
      
      setState(() {
        _marketConnectors = registryConnectors;
        _marketLoading = false;
      });
    } catch (e) {
      setState(() {
        _marketErrorMessage = '加载市场连接器失败: $e';
        _marketLoading = false;
      });
    }
  }

  List<ConnectorDefinition> _generateMockMarketConnectors() {
    return [
      const ConnectorDefinition(
        connectorId: 'obsidian-vault',
        name: 'Obsidian Vault',
        displayName: 'Obsidian 知识库',
        description: '连接你的 Obsidian 知识库，智能索引笔记和双链关系',
        category: '知识管理',
        version: '1.2.0',
        author: 'Linch Mind Team',
        isRegistered: true,
      ),
      const ConnectorDefinition(
        connectorId: 'browser-bookmarks',
        name: 'Browser Bookmarks',
        displayName: '浏览器书签',
        description: '同步浏览器书签，发现你的兴趣模式和知识图谱',
        category: '浏览器',
        version: '1.0.5',
        author: 'Community',
        isRegistered: true,
      ),
      const ConnectorDefinition(
        connectorId: 'email-insights',
        name: 'Email Insights',
        displayName: '邮件洞察',
        description: '分析邮件内容，提取任务、约会和重要信息',
        category: '通讯',
        version: '2.1.0',
        author: 'Linch Mind Team',
        isRegistered: true,
      ),
      const ConnectorDefinition(
        connectorId: 'github-activity',
        name: 'GitHub Activity',
        displayName: 'GitHub 活动',
        description: '跟踪GitHub活动，分析代码提交和项目协作模式',
        category: '开发',
        version: '1.3.2',
        author: 'Community',
        isRegistered: true,
      ),
      const ConnectorDefinition(
        connectorId: 'notion-workspace',
        name: 'Notion Workspace',
        displayName: 'Notion 工作空间',
        description: '连接Notion工作空间，整合笔记、任务和项目信息',
        category: '效率',
        version: '2.0.1',
        author: 'Linch Mind Team',
        isRegistered: true,
      ),
    ];
  }

  Future<void> _refreshInstalledConnectors() async {
    await _loadInstalledConnectors();
  }

  Future<void> _refreshMarketConnectors() async {
    try {
      // 先刷新注册表
      await RegistryApiClient.refreshRegistry();
      
      // 清空缓存并重新加载
      _marketConnectors.clear();
      await _loadMarketConnectors();
    } catch (e) {
      setState(() {
        _marketErrorMessage = '刷新市场连接器失败: $e';
      });
    }
  }

  List<ConnectorInfo> get _filteredInstalledConnectors {
    var filtered = _installedConnectors.where((connector) {
      // 搜索过滤
      if (_installedSearchQuery.isNotEmpty) {
        final query = _installedSearchQuery.toLowerCase();
        if (!connector.displayName.toLowerCase().contains(query) &&
            !connector.collectorId.toLowerCase().contains(query)) {
          return false;
        }
      }

      // 状态过滤
      switch (_installedFilter) {
        case InstalledConnectorFilter.running:
          if (connector.state != ConnectorState.running) return false;
          break;
        case InstalledConnectorFilter.stopped:
          if (connector.state != ConnectorState.configured &&
              connector.state != ConnectorState.enabled) {
            return false;
          }
          break;
        case InstalledConnectorFilter.error:
          if (connector.state != ConnectorState.error) return false;
          break;
        case InstalledConnectorFilter.highActivity:
          if (connector.dataCount < 100) return false;
          break;
        case InstalledConnectorFilter.noData:
          if (connector.dataCount > 0) return false;
          break;
        case InstalledConnectorFilter.all:
          break;
      }

      return true;
    }).toList();

    // 排序
    filtered.sort((a, b) {
      switch (_installedSort) {
        case InstalledConnectorSort.status:
          const stateOrder = {
            ConnectorState.error: 0, // 错误优先
            ConnectorState.running: 1,
            ConnectorState.enabled: 2,
            ConnectorState.configured: 3,
          };
          final orderA = stateOrder[a.state] ?? 99;
          final orderB = stateOrder[b.state] ?? 99;
          if (orderA != orderB) return orderA.compareTo(orderB);
          break;
        case InstalledConnectorSort.activity:
          final result = b.dataCount.compareTo(a.dataCount);
          if (result != 0) return result;
          break;
        case InstalledConnectorSort.dataCount:
          final result = b.dataCount.compareTo(a.dataCount);
          if (result != 0) return result;
          break;
        case InstalledConnectorSort.lastHeartbeat:
          final aTime = a.lastHeartbeat ?? DateTime(1970);
          final bTime = b.lastHeartbeat ?? DateTime(1970);
          final result = bTime.compareTo(aTime);
          if (result != 0) return result;
          break;
      }

      return a.displayName.compareTo(b.displayName);
    });

    return filtered;
  }

  List<ConnectorDefinition> get _filteredMarketConnectors {
    var filtered = _marketConnectors.where((connector) {
      // 搜索过滤
      if (_marketSearchQuery.isNotEmpty) {
        final query = _marketSearchQuery.toLowerCase();
        if (!connector.displayName.toLowerCase().contains(query) &&
            !connector.description.toLowerCase().contains(query) &&
            !connector.category.toLowerCase().contains(query)) {
          return false;
        }
      }

      // 分类过滤
      if (_marketCategory != MarketConnectorCategory.all) {
        final categoryName = _getMarketCategoryName(_marketCategory);
        if (!connector.category
            .toLowerCase()
            .contains(categoryName.toLowerCase())) {
          return false;
        }
      }

      return true;
    }).toList();

    // 排序 (简化版，实际应该根据服务端数据)
    filtered.sort((a, b) {
      switch (_marketSort) {
        case MarketConnectorSort.recommended:
          // Mock: 官方的排前面
          if (a.author == 'Linch Mind Team' && b.author != 'Linch Mind Team')
            return -1;
          if (b.author == 'Linch Mind Team' && a.author != 'Linch Mind Team')
            return 1;
          break;
        case MarketConnectorSort.newest:
          // Mock: 按版本号排序
          return b.version.compareTo(a.version);
        case MarketConnectorSort.popular:
        case MarketConnectorSort.rating:
          // Mock: 按名称排序
          break;
      }
      return a.displayName.compareTo(b.displayName);
    });

    return filtered;
  }

  String _getMarketCategoryName(MarketConnectorCategory category) {
    switch (category) {
      case MarketConnectorCategory.filesystem:
        return '文件';
      case MarketConnectorCategory.communication:
        return '通讯';
      case MarketConnectorCategory.automation:
        return '自动化';
      case MarketConnectorCategory.development:
        return '开发';
      case MarketConnectorCategory.productivity:
        return '效率';
      case MarketConnectorCategory.all:
        return '';
    }
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
        _buildMarketCategoryNavigation(),
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
            flex: 2,
            child: TextField(
              decoration: const InputDecoration(
                hintText: '搜索运行中的连接器...',
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
          const SizedBox(width: 12),
          DropdownButton<InstalledConnectorFilter>(
            value: _installedFilter,
            hint: const Text('状态'),
            items: InstalledConnectorFilter.values.map((filter) {
              return DropdownMenuItem(
                value: filter,
                child: Text(_getInstalledFilterName(filter)),
              );
            }).toList(),
            onChanged: (filter) {
              if (filter != null) {
                setState(() {
                  _installedFilter = filter;
                });
              }
            },
          ),
          const SizedBox(width: 8),
          DropdownButton<InstalledConnectorSort>(
            value: _installedSort,
            hint: const Text('排序'),
            items: InstalledConnectorSort.values.map((sort) {
              return DropdownMenuItem(
                value: sort,
                child: Text(_getInstalledSortName(sort)),
              );
            }).toList(),
            onChanged: (sort) {
              if (sort != null) {
                setState(() {
                  _installedSort = sort;
                });
              }
            },
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
            flex: 2,
            child: TextField(
              decoration: const InputDecoration(
                hintText: '发现连接器...',
                prefixIcon: Icon(Icons.explore),
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
          const SizedBox(width: 12),
          DropdownButton<MarketConnectorCategory>(
            value: _marketCategory,
            hint: const Text('分类'),
            items: MarketConnectorCategory.values.map((category) {
              return DropdownMenuItem(
                value: category,
                child: Text(_getMarketCategoryDisplayName(category)),
              );
            }).toList(),
            onChanged: (category) {
              if (category != null) {
                setState(() {
                  _marketCategory = category;
                });
              }
            },
          ),
          const SizedBox(width: 8),
          DropdownButton<MarketConnectorSort>(
            value: _marketSort,
            hint: const Text('排序'),
            items: MarketConnectorSort.values.map((sort) {
              return DropdownMenuItem(
                value: sort,
                child: Text(_getMarketSortName(sort)),
              );
            }).toList(),
            onChanged: (sort) {
              if (sort != null) {
                setState(() {
                  _marketSort = sort;
                });
              }
            },
          ),
        ],
      ),
    );
  }

  Widget _buildInstalledStatusOverview() {
    if (_installedLoading || _installedConnectors.isEmpty) {
      return const SizedBox.shrink();
    }

    final runningCount = _installedConnectors
        .where((c) => c.state == ConnectorState.running)
        .length;
    final errorCount = _installedConnectors
        .where((c) => c.state == ConnectorState.error)
        .length;
    final stoppedCount = _installedConnectors
        .where((c) =>
            c.state == ConnectorState.configured ||
            c.state == ConnectorState.enabled)
        .length;

    return Container(
      padding: const EdgeInsets.all(16),
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.primaryContainer,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildStatusIndicator(
            icon: Icons.play_circle_filled,
            label: '$runningCount个运行中',
            color: Colors.green,
          ),
          if (errorCount > 0)
            _buildStatusIndicator(
              icon: Icons.error,
              label: '$errorCount个异常',
              color: Colors.red,
            ),
          _buildStatusIndicator(
            icon: Icons.pause_circle,
            label: '$stoppedCount个已停止',
            color: Colors.orange,
          ),
        ],
      ),
    );
  }

  Widget _buildStatusIndicator(
      {required IconData icon, required String label, required Color color}) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(width: 4),
        Text(
          label,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w500,
              ),
        ),
      ],
    );
  }

  Widget _buildMarketCategoryNavigation() {
    final categories = [
      (MarketConnectorCategory.all, Icons.apps, '全部'),
      (MarketConnectorCategory.filesystem, Icons.folder, '文件'),
      (MarketConnectorCategory.communication, Icons.chat, '通讯'),
      (MarketConnectorCategory.automation, Icons.auto_awesome, '自动化'),
      (MarketConnectorCategory.development, Icons.code, '开发'),
      (MarketConnectorCategory.productivity, Icons.trending_up, '效率'),
    ];

    return Container(
      height: 60,
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: categories.length,
        itemBuilder: (context, index) {
          final (category, icon, label) = categories[index];
          final isSelected = _marketCategory == category;

          return Padding(
            padding: const EdgeInsets.only(right: 12),
            child: FilterChip(
              avatar: Icon(icon, size: 18),
              label: Text(label),
              selected: isSelected,
              onSelected: (selected) {
                setState(() {
                  _marketCategory = category;
                });
              },
            ),
          );
        },
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
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: filteredConnectors.length,
        itemBuilder: (context, index) {
          final connector = filteredConnectors[index];
          return _buildInstalledConnectorCard(connector);
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
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: filteredConnectors.length,
        itemBuilder: (context, index) {
          final connector = filteredConnectors[index];
          return _buildMarketConnectorCard(connector);
        },
      ),
    );
  }

  Widget _buildInstalledConnectorCard(ConnectorInfo connector) {
    final isRunning = connector.state == ConnectorState.running;
    final hasError = connector.state == ConnectorState.error;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            // 状态指示器
            Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: hasError
                    ? Colors.red
                    : (isRunning ? Colors.green : Colors.grey),
              ),
            ),
            const SizedBox(width: 16),

            // 连接器信息
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    connector.displayName,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    _getConnectorDescription(connector),
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Theme.of(context)
                              .textTheme
                              .bodySmall
                              ?.color
                              ?.withValues(alpha: 0.7),
                        ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  if (hasError && connector.errorMessage != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      '错误: ${connector.errorMessage}',
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.error,
                        fontSize: 12,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ],
              ),
            ),

            const SizedBox(width: 16),

            // 快速启动/停用开关
            Switch(
              value: isRunning,
              onChanged: hasError
                  ? null
                  : (enabled) => _toggleConnector(connector, enabled),
            ),

            const SizedBox(width: 8),

            // 设置按钮
            IconButton(
              icon: const Icon(Icons.settings),
              onPressed: () => _showAdvancedConfigDialog(connector),
              tooltip: '高级配置',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMarketConnectorCard(ConnectorDefinition connector) {
    final isInstalled =
        _installedConnectors.any((c) => c.collectorId == connector.connectorId);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.primaryContainer,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    _getCategoryIcon(connector.category),
                    size: 24,
                    color: Theme.of(context).colorScheme.onPrimaryContainer,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        connector.displayName,
                        style:
                            Theme.of(context).textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.w600,
                                ),
                      ),
                      Text(
                        '${connector.category} • v${connector.version}',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Theme.of(context).disabledColor,
                            ),
                      ),
                    ],
                  ),
                ),
                if (connector.author == 'Linch Mind Team')
                  Chip(
                    label: const Text('官方', style: TextStyle(fontSize: 12)),
                    backgroundColor:
                        Theme.of(context).colorScheme.secondaryContainer,
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              connector.description,
              style: Theme.of(context).textTheme.bodyMedium,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Text(
                  'by ${connector.author}',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Theme.of(context).disabledColor,
                      ),
                ),
                const Spacer(),
                if (isInstalled) ...[
                  Icon(
                    Icons.check_circle,
                    size: 16,
                    color: Colors.green,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '已安装',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.green,
                        ),
                  ),
                ] else ...[
                  TextButton(
                    onPressed: () => _showMarketConnectorDetails(connector),
                    child: const Text('查看详情'),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton(
                    onPressed: () => _installMarketConnector(connector),
                    child: const Text('安装'),
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

  String _getInstalledFilterName(InstalledConnectorFilter filter) {
    switch (filter) {
      case InstalledConnectorFilter.all:
        return '全部';
      case InstalledConnectorFilter.running:
        return '运行中';
      case InstalledConnectorFilter.stopped:
        return '已停止';
      case InstalledConnectorFilter.error:
        return '异常';
      case InstalledConnectorFilter.highActivity:
        return '高活跃度';
      case InstalledConnectorFilter.noData:
        return '无数据';
    }
  }

  String _getInstalledSortName(InstalledConnectorSort sort) {
    switch (sort) {
      case InstalledConnectorSort.status:
        return '按状态';
      case InstalledConnectorSort.activity:
        return '按活跃度';
      case InstalledConnectorSort.dataCount:
        return '按数据量';
      case InstalledConnectorSort.lastHeartbeat:
        return '按最后活跃';
    }
  }

  String _getMarketCategoryDisplayName(MarketConnectorCategory category) {
    switch (category) {
      case MarketConnectorCategory.all:
        return '全部';
      case MarketConnectorCategory.filesystem:
        return '文件系统';
      case MarketConnectorCategory.communication:
        return '通讯工具';
      case MarketConnectorCategory.automation:
        return '自动化';
      case MarketConnectorCategory.development:
        return '开发工具';
      case MarketConnectorCategory.productivity:
        return '效率工具';
    }
  }

  String _getMarketSortName(MarketConnectorSort sort) {
    switch (sort) {
      case MarketConnectorSort.recommended:
        return '推荐';
      case MarketConnectorSort.newest:
        return '最新';
      case MarketConnectorSort.popular:
        return '最受欢迎';
      case MarketConnectorSort.rating:
        return '评分最高';
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
                                            final response = await _apiClient
                                                .scanConnectorDirectory(
                                                    selectedPath!);
                                            setDialogState(() {
                                              availableConnectors =
                                                  response.connectors;
                                              isScanning = false;
                                              if (availableConnectors.isEmpty) {
                                                errorMessage =
                                                    '该目录中未发现有效的连接器。\n请确保所选目录包含 connector.json 文件，或选择包含连接器子目录的父目录。';
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
        autoStart: true,
      );

      await _apiClient.createConnector(request);

      if (mounted) {
        Navigator.of(context).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('成功创建连接器: ${type.displayName}')),
        );
        await _refreshInstalledConnectors();
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

  Future<void> _showMarketConnectorDetails(
      ConnectorDefinition connector) async {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('${connector.displayName} 详情功能开发中...')),
    );
  }

  Future<void> _installMarketConnector(ConnectorDefinition connector) async {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('安装 ${connector.displayName} 功能开发中...')),
    );
  }

  String _getConnectorDescription(ConnectorInfo connector) {
    // 根据连接器类型返回简介
    switch (connector.collectorId) {
      case 'filesystem':
        return '监控文件系统变化，自动索引文档和代码文件';
      case 'clipboard':
        return '监控剪贴板内容，收集复制的文本和链接';
      default:
        return '${connector.collectorId} 连接器 - ${connector.dataCount} 条数据';
    }
  }

  Future<void> _toggleConnector(ConnectorInfo connector, bool enabled) async {
    try {
      if (enabled) {
        await _apiClient.startConnector(connector.collectorId);
      } else {
        await _apiClient.stopConnector(connector.collectorId);
      }

      // 刷新数据
      await _refreshInstalledConnectors();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${connector.displayName} 已${enabled ? "启动" : "停止"}'),
            duration: const Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('操作失败: $e'),
            backgroundColor: Theme.of(context).colorScheme.error,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    }
  }

  Future<void> _showAdvancedConfigDialog(ConnectorInfo connector) async {
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ConnectorConfigScreen(
          connectorId: connector.collectorId,
          connectorName: connector.displayName,
        ),
      ),
    );

    // 配置界面返回后刷新连接器列表
    await _refreshInstalledConnectors();
  }
}
