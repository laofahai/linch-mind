// 搜索和筛选功能组件
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/data_insights_models.dart';
import '../../models/connector_lifecycle_models.dart';
import '../../providers/data_insights_provider.dart';
import '../../services/connector_lifecycle_api_client.dart';

/// 智能搜索组件
class SmartSearchWidget extends ConsumerStatefulWidget {
  final String? placeholder;
  final VoidCallback? onSearchFocus;
  final bool showFilters;

  const SmartSearchWidget({
    super.key,
    this.placeholder,
    this.onSearchFocus,
    this.showFilters = true,
  });

  @override
  ConsumerState<SmartSearchWidget> createState() => _SmartSearchWidgetState();
}

class _SmartSearchWidgetState extends ConsumerState<SmartSearchWidget> {
  late final TextEditingController _searchController;
  late final FocusNode _searchFocusNode;
  bool _isSearchFocused = false;
  String _lastQuery = '';

  @override
  void initState() {
    super.initState();
    _searchController = TextEditingController();
    _searchFocusNode = FocusNode();

    _searchFocusNode.addListener(() {
      setState(() {
        _isSearchFocused = _searchFocusNode.hasFocus;
      });
      if (_isSearchFocused && widget.onSearchFocus != null) {
        widget.onSearchFocus!();
      }
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    _searchFocusNode.dispose();
    super.dispose();
  }

  void _performSearch(String query) {
    if (query.trim().isEmpty) {
      ref.read(entityListProvider.notifier).clearSearch();
      return;
    }

    if (query != _lastQuery) {
      _lastQuery = query;
      ref.read(entityListProvider.notifier).searchEntities(query);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final searchQuery = ref.watch(searchQueryProvider);

    return Column(
      children: [
        // 搜索框
        Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            color: theme.colorScheme.surfaceContainerHighest
                .withValues(alpha: 0.3),
            border: _isSearchFocused
                ? Border.all(color: theme.colorScheme.primary, width: 2)
                : null,
          ),
          child: TextField(
            controller: _searchController,
            focusNode: _searchFocusNode,
            onChanged: (query) {
              ref.read(searchQueryProvider.notifier).state = query;
              _performSearch(query);
            },
            decoration: InputDecoration(
              hintText: widget.placeholder ?? '搜索实体、洞察或活动...',
              prefixIcon: Icon(
                Icons.search,
                color: _isSearchFocused
                    ? theme.colorScheme.primary
                    : theme.colorScheme.onSurfaceVariant,
              ),
              suffixIcon: searchQuery.isNotEmpty
                  ? Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        // 搜索建议按钮
                        IconButton(
                          icon: const Icon(Icons.auto_awesome),
                          onPressed: () => _showSearchSuggestions(context),
                          tooltip: '智能建议',
                        ),
                        // 清除按钮
                        IconButton(
                          icon: const Icon(Icons.clear),
                          onPressed: () {
                            _searchController.clear();
                            ref.read(searchQueryProvider.notifier).state = '';
                            ref.read(entityListProvider.notifier).clearSearch();
                          },
                          tooltip: '清除搜索',
                        ),
                      ],
                    )
                  : null,
              border: InputBorder.none,
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 16,
                vertical: 16,
              ),
            ),
          ),
        ),

        if (widget.showFilters) ...[
          const SizedBox(height: 16),
          FilterChipsWidget(),
        ],

        // 搜索结果提示
        if (searchQuery.isNotEmpty) ...[
          const SizedBox(height: 12),
          SearchResultsHeader(),
        ],
      ],
    );
  }

  void _showSearchSuggestions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => SearchSuggestionsSheet(),
    );
  }
}

/// 筛选标签组件
class FilterChipsWidget extends ConsumerWidget {
  const FilterChipsWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedType = ref.watch(selectedEntityTypeProvider);

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        // 实体类型筛选
        FilterChip(
          label: const Text('URL'),
          selected: selectedType == 'url',
          onSelected: (selected) {
            ref.read(selectedEntityTypeProvider.notifier).state =
                selected ? 'url' : null;
            _applyEntityTypeFilter(ref, selected ? 'url' : null);
          },
        ),
        FilterChip(
          label: const Text('文件路径'),
          selected: selectedType == 'file_path',
          onSelected: (selected) {
            ref.read(selectedEntityTypeProvider.notifier).state =
                selected ? 'file_path' : null;
            _applyEntityTypeFilter(ref, selected ? 'file_path' : null);
          },
        ),
        FilterChip(
          label: const Text('邮箱'),
          selected: selectedType == 'email',
          onSelected: (selected) {
            ref.read(selectedEntityTypeProvider.notifier).state =
                selected ? 'email' : null;
            _applyEntityTypeFilter(ref, selected ? 'email' : null);
          },
        ),
        FilterChip(
          label: const Text('关键词'),
          selected: selectedType == 'keyword',
          onSelected: (selected) {
            ref.read(selectedEntityTypeProvider.notifier).state =
                selected ? 'keyword' : null;
            _applyEntityTypeFilter(ref, selected ? 'keyword' : null);
          },
        ),

        // 时间筛选
        ActionChip(
          label: const Text('今天'),
          onPressed: () => _applyTimeFilter(ref, 'today'),
        ),
        ActionChip(
          label: const Text('本周'),
          onPressed: () => _applyTimeFilter(ref, 'week'),
        ),

        // 更多筛选选项
        ActionChip(
          avatar: const Icon(Icons.tune, size: 16),
          label: const Text('高级筛选'),
          onPressed: () => _showAdvancedFilters(context, ref),
        ),
      ],
    );
  }

  void _applyEntityTypeFilter(WidgetRef ref, String? type) {
    ref.read(entityListProvider.notifier).loadEntities(
          type: type,
          refresh: true,
        );
  }

  void _applyTimeFilter(WidgetRef ref, String timeRange) {
    // TODO: 实现时间筛选逻辑
  }

  void _showAdvancedFilters(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (context) => AdvancedFiltersDialog(),
    );
  }
}

/// 搜索结果头部
class SearchResultsHeader extends ConsumerWidget {
  const SearchResultsHeader({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final entityListState = ref.watch(entityListProvider);
    final searchQuery = ref.watch(searchQueryProvider);
    final theme = Theme.of(context);

    if (searchQuery.isEmpty) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: theme.colorScheme.primaryContainer.withValues(alpha: 0.3),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(
            Icons.search,
            size: 16,
            color: theme.colorScheme.onPrimaryContainer,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              entityListState.isLoading
                  ? '正在搜索 "$searchQuery"...'
                  : '找到 ${entityListState.entities.length} 个结果: "$searchQuery"',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onPrimaryContainer,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          TextButton(
            onPressed: () {
              ref.read(searchQueryProvider.notifier).state = '';
              ref.read(entityListProvider.notifier).clearSearch();
            },
            child: const Text('清除'),
          ),
        ],
      ),
    );
  }
}

/// 搜索建议面板
class SearchSuggestionsSheet extends ConsumerWidget {
  const SearchSuggestionsSheet({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '智能搜索建议',
            style: theme.textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 16),

          // 快速搜索建议
          Text(
            '快速搜索',
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _buildSuggestionChip(context, ref, 'github.com', Icons.link),
              _buildSuggestionChip(context, ref, '今天的文件', Icons.today),
              _buildSuggestionChip(context, ref, 'Python项目', Icons.code),
              _buildSuggestionChip(context, ref, '设计相关', Icons.design_services),
            ],
          ),

          const SizedBox(height: 20),

          // 搜索技巧
          Text(
            '搜索技巧',
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          _buildSearchTip('使用引号搜索精确匹配: "Flutter项目"'),
          _buildSearchTip('按类型搜索: type:url github'),
          _buildSearchTip('按日期搜索: today:, week:, month:'),
          _buildSearchTip('组合搜索: Flutter AND UI'),

          const SizedBox(height: 20),

          // 关闭按钮
          Center(
            child: TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('关闭'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSuggestionChip(
      BuildContext context, WidgetRef ref, String label, IconData icon) {
    return ActionChip(
      avatar: Icon(icon, size: 16),
      label: Text(label),
      onPressed: () {
        ref.read(searchQueryProvider.notifier).state = label;
        ref.read(entityListProvider.notifier).searchEntities(label);
        Navigator.of(context).pop();
      },
    );
  }

  Widget _buildSearchTip(String tip) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          const Icon(Icons.lightbulb_outline, size: 16),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              tip,
              style: const TextStyle(fontSize: 13),
            ),
          ),
        ],
      ),
    );
  }
}

/// 高级筛选对话框
class AdvancedFiltersDialog extends ConsumerStatefulWidget {
  const AdvancedFiltersDialog({super.key});

  @override
  ConsumerState<AdvancedFiltersDialog> createState() =>
      _AdvancedFiltersDialogState();
}

class _AdvancedFiltersDialogState extends ConsumerState<AdvancedFiltersDialog> {
  DateTime? _startDate;
  DateTime? _endDate;
  final List<String> _selectedTypes = [];
  final List<String> _selectedConnectors = [];
  List<ConnectorDefinition> _availableConnectors = [];
  bool _isLoadingConnectors = true;

  @override
  void initState() {
    super.initState();
    _loadAvailableConnectors();
  }

  Future<void> _loadAvailableConnectors() async {
    try {
      final client = ConnectorLifecycleApiClient();
      final response = await client.discoverConnectors();
      if (response.success && response.connectors.isNotEmpty) {
        setState(() {
          _availableConnectors = response.connectors;
          _isLoadingConnectors = false;
        });
      } else {
        setState(() {
          _isLoadingConnectors = false;
        });
      }
    } catch (e) {
      debugPrint('[DEBUG] Failed to load connectors: $e');
      setState(() {
        _isLoadingConnectors = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Dialog(
      child: Container(
        width: 500,
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(
                  '高级筛选',
                  style: theme.textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const Spacer(),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.of(context).pop(),
                ),
              ],
            ),

            const SizedBox(height: 20),

            // 日期范围筛选
            Text(
              '日期范围',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => _selectStartDate(context),
                    child: Text(_startDate?.toString().split(' ')[0] ?? '开始日期'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => _selectEndDate(context),
                    child: Text(_endDate?.toString().split(' ')[0] ?? '结束日期'),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 20),

            // 实体类型筛选
            Text(
              '实体类型',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children:
                  ['url', 'file_path', 'email', 'phone', 'keyword'].map((type) {
                return FilterChip(
                  label: Text(_getTypeLabel(type)),
                  selected: _selectedTypes.contains(type),
                  onSelected: (selected) {
                    setState(() {
                      if (selected) {
                        _selectedTypes.add(type);
                      } else {
                        _selectedTypes.remove(type);
                      }
                    });
                  },
                );
              }).toList(),
            ),

            const SizedBox(height: 20),

            // 连接器筛选
            Text(
              '数据来源',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 12),
            _isLoadingConnectors
                ? const CircularProgressIndicator()
                : Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: _availableConnectors.map((connector) {
                      return FilterChip(
                        label: Text(connector.displayName.isNotEmpty
                            ? connector.displayName
                            : connector.name),
                        selected:
                            _selectedConnectors.contains(connector.connectorId),
                        onSelected: (selected) {
                          setState(() {
                            if (selected) {
                              _selectedConnectors.add(connector.connectorId);
                            } else {
                              _selectedConnectors.remove(connector.connectorId);
                            }
                          });
                        },
                      );
                    }).toList(),
                  ),

            const SizedBox(height: 30),

            // 操作按钮
            Row(
              children: [
                TextButton(
                  onPressed: () => _resetFilters(),
                  child: const Text('重置'),
                ),
                const Spacer(),
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('取消'),
                ),
                const SizedBox(width: 12),
                ElevatedButton(
                  onPressed: () => _applyFilters(),
                  child: const Text('应用筛选'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _selectStartDate(BuildContext context) async {
    final date = await showDatePicker(
      context: context,
      initialDate:
          _startDate ?? DateTime.now().subtract(const Duration(days: 30)),
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
    );
    if (date != null) {
      setState(() => _startDate = date);
    }
  }

  Future<void> _selectEndDate(BuildContext context) async {
    final date = await showDatePicker(
      context: context,
      initialDate: _endDate ?? DateTime.now(),
      firstDate: _startDate ?? DateTime(2020),
      lastDate: DateTime.now(),
    );
    if (date != null) {
      setState(() => _endDate = date);
    }
  }

  void _resetFilters() {
    setState(() {
      _startDate = null;
      _endDate = null;
      _selectedTypes.clear();
      _selectedConnectors.clear();
    });
  }

  void _applyFilters() {
    final filterOptions = FilterOptions(
      entityTypes: _selectedTypes,
      connectorIds: _selectedConnectors,
      startDate: _startDate,
      endDate: _endDate,
    );

    ref.read(filterOptionsProvider.notifier).state = filterOptions;

    // TODO: 应用筛选到数据加载

    Navigator.of(context).pop();
  }

  String _getTypeLabel(String type) {
    switch (type) {
      case 'url':
        return 'URL';
      case 'file_path':
        return '文件路径';
      case 'email':
        return '邮箱';
      case 'phone':
        return '电话';
      case 'keyword':
        return '关键词';
      default:
        return type;
    }
  }
}
