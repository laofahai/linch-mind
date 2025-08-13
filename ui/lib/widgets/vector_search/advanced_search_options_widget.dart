// 高级搜索选项组件 - 精确控制搜索参数
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../models/data_insights_models.dart';
import '../../providers/vector_search_provider.dart';
import '../../utils/app_logger.dart';

/// 高级搜索选项组件
class AdvancedSearchOptionsWidget extends ConsumerStatefulWidget {
  final VoidCallback? onSearch;
  final VoidCallback? onReset;
  final bool isExpanded;

  const AdvancedSearchOptionsWidget({
    super.key,
    this.onSearch,
    this.onReset,
    this.isExpanded = true,
  });

  @override
  ConsumerState<AdvancedSearchOptionsWidget> createState() =>
      _AdvancedSearchOptionsWidgetState();
}

class _AdvancedSearchOptionsWidgetState
    extends ConsumerState<AdvancedSearchOptionsWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _expandAnimation;

  // 搜索参数
  final TextEditingController _queryController = TextEditingController();
  int _resultCount = 20;
  double _similarityThreshold = 0.1;
  final List<String> _selectedEntityTypes = [];
  final List<String> _selectedTags = [];
  DateTime? _dateFrom;
  DateTime? _dateTo;
  bool _enableSemanticBoost = true;
  bool _includeMetadata = false;

  // 可选的实体类型
  final List<String> _availableEntityTypes = [
    'url',
    'filePath',
    'email',
    'phone',
    'keyword',
    'document',
    'image',
    'other',
  ];

  // 常用标签
  final List<String> _availableTags = [
    'work',
    'personal',
    'important',
    'urgent',
    'archived',
    'favorite',
  ];

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _expandAnimation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    );

    if (widget.isExpanded) {
      _animationController.forward();
    }

    // 从现有搜索参数中初始化
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final currentParams = ref.read(advancedSearchParamsNotifierProvider);
      _initializeFromParams(currentParams);
    });
  }

  @override
  void dispose() {
    _animationController.dispose();
    _queryController.dispose();
    super.dispose();
  }

  void _initializeFromParams(AdvancedSearchParams params) {
    // 基于AdvancedSearchParams初始化界面
    _resultCount = params.maxResults;
    _similarityThreshold = params.similarityThreshold;
    _selectedEntityTypes.clear();
    _selectedEntityTypes.addAll(params.searchTypes);
    _selectedTags.clear();
    _selectedTags.addAll(params.connectorFilters);
    if (params.dateRange != null) {
      _dateFrom = params.dateRange!.start;
      _dateTo = params.dateRange!.end;
    }
  }

  void _performAdvancedSearch() {
    final query = _queryController.text.trim();
    if (query.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请输入搜索关键词')),
      );
      return;
    }

    // 构建高级搜索查询
    final searchQuery = VectorSearchQuery(
      query: query,
      k: _resultCount,
      threshold: _similarityThreshold,
      entityTypes: List.from(_selectedEntityTypes),
      tags: List.from(_selectedTags),
      dateFrom: _dateFrom,
      dateTo: _dateTo,
    );

    // 保存搜索参数到AdvancedSearchParams
    final advancedParams = AdvancedSearchParams(
      maxResults: _resultCount,
      similarityThreshold: _similarityThreshold,
      searchTypes: List.from(_selectedEntityTypes),
      connectorFilters: List.from(_selectedTags),
      dateRange: _dateFrom != null && _dateTo != null 
          ? DateTimeRange(start: _dateFrom!, end: _dateTo!) 
          : null,
      useSemanticSearch: _enableSemanticBoost,
    );
    ref.read(advancedSearchParamsNotifierProvider.notifier).updateParams(advancedParams);

    // 执行搜索
    ref.read(vectorSearchProvider.notifier).search(searchQuery);
    
    AppLogger.info('执行高级搜索: $query', module: 'AdvancedSearchOptions');
    widget.onSearch?.call();
  }

  void _resetSearchOptions() {
    setState(() {
      _queryController.clear();
      _resultCount = 20;
      _similarityThreshold = 0.1;
      _selectedEntityTypes.clear();
      _selectedTags.clear();
      _dateFrom = null;
      _dateTo = null;
      _enableSemanticBoost = true;
      _includeMetadata = false;
    });

    // 重置Provider状态
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(advancedSearchParamsNotifierProvider.notifier).reset();
    });
    
    widget.onReset?.call();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Theme.of(context).dividerColor,
          width: 1,
        ),
      ),
      child: Column(
        children: [
          // 标题栏
          _buildHeaderBar(),
          
          // 可展开内容
          AnimatedBuilder(
            animation: _expandAnimation,
            builder: (context, child) {
              return ClipRect(
                child: Align(
                  heightFactor: _expandAnimation.value,
                  child: child,
                ),
              );
            },
            child: _buildAdvancedOptions(),
          ),
        ],
      ),
    );
  }

  Widget _buildHeaderBar() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        border: widget.isExpanded ? Border(
          bottom: BorderSide(
            color: Theme.of(context).dividerColor,
            width: 1,
          ),
        ) : null,
      ),
      child: Row(
        children: [
          Icon(
            Icons.tune,
            color: Theme.of(context).primaryColor,
            size: 20,
          ),
          const SizedBox(width: 8),
          Text(
            '高级搜索选项',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: Theme.of(context).primaryColor,
            ),
          ),
          const Spacer(),
          
          // 预设按钮
          IconButton(
            icon: const Icon(Icons.bookmark, size: 20),
            tooltip: '搜索预设',
            onPressed: _showSearchPresets,
          ),
          
          // 展开/收起按钮
          IconButton(
            icon: AnimatedRotation(
              turns: _expandAnimation.value * 0.5,
              duration: const Duration(milliseconds: 300),
              child: const Icon(Icons.expand_more),
            ),
            onPressed: _toggleExpansion,
            tooltip: widget.isExpanded ? '收起' : '展开',
          ),
        ],
      ),
    );
  }

  Widget _buildAdvancedOptions() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 搜索查询输入
          _buildQueryInput(),
          const SizedBox(height: 16),
          
          // 搜索参数控制
          Row(
            children: [
              Expanded(child: _buildResultCountSlider()),
              const SizedBox(width: 16),
              Expanded(child: _buildSimilarityThresholdSlider()),
            ],
          ),
          const SizedBox(height: 16),
          
          // 实体类型筛选
          _buildEntityTypeFilters(),
          const SizedBox(height: 16),
          
          // 标签筛选
          _buildTagFilters(),
          const SizedBox(height: 16),
          
          // 时间范围筛选
          _buildDateRangeFilters(),
          const SizedBox(height: 16),
          
          // 高级选项
          _buildAdvancedToggleOptions(),
          const SizedBox(height: 24),
          
          // 操作按钮
          _buildActionButtons(),
        ],
      ),
    );
  }

  Widget _buildQueryInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '搜索关键词',
          style: TextStyle(
            fontWeight: FontWeight.w500,
            color: Theme.of(context).textTheme.titleSmall?.color,
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: _queryController,
          decoration: InputDecoration(
            hintText: '输入您要搜索的内容...',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
            ),
            prefixIcon: const Icon(Icons.search),
            suffixIcon: _queryController.text.isNotEmpty
                ? IconButton(
                    icon: const Icon(Icons.clear),
                    onPressed: () {
                      setState(() {
                        _queryController.clear();
                      });
                    },
                  )
                : null,
          ),
          onChanged: (value) => setState(() {}),
          textInputAction: TextInputAction.search,
          onSubmitted: (_) => _performAdvancedSearch(),
        ),
      ],
    );
  }

  Widget _buildResultCountSlider() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '结果数量: $_resultCount',
          style: TextStyle(
            fontWeight: FontWeight.w500,
            color: Theme.of(context).textTheme.titleSmall?.color,
          ),
        ),
        Slider(
          value: _resultCount.toDouble(),
          min: 5,
          max: 100,
          divisions: 19,
          onChanged: (value) {
            setState(() {
              _resultCount = value.round();
            });
          },
        ),
      ],
    );
  }

  Widget _buildSimilarityThresholdSlider() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '相似度阈值: ${_similarityThreshold.toStringAsFixed(2)}',
          style: TextStyle(
            fontWeight: FontWeight.w500,
            color: Theme.of(context).textTheme.titleSmall?.color,
          ),
        ),
        Slider(
          value: _similarityThreshold,
          min: 0.0,
          max: 1.0,
          divisions: 20,
          onChanged: (value) {
            setState(() {
              _similarityThreshold = value;
            });
          },
        ),
      ],
    );
  }

  Widget _buildEntityTypeFilters() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '实体类型',
          style: TextStyle(
            fontWeight: FontWeight.w500,
            color: Theme.of(context).textTheme.titleSmall?.color,
          ),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: _availableEntityTypes.map((type) {
            final isSelected = _selectedEntityTypes.contains(type);
            return FilterChip(
              label: Text(_getEntityTypeDisplayName(type)),
              selected: isSelected,
              onSelected: (selected) {
                setState(() {
                  if (selected) {
                    _selectedEntityTypes.add(type);
                  } else {
                    _selectedEntityTypes.remove(type);
                  }
                });
              },
              selectedColor: Theme.of(context).primaryColor.withValues(alpha: 0.2),
              checkmarkColor: Theme.of(context).primaryColor,
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildTagFilters() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '标签筛选',
          style: TextStyle(
            fontWeight: FontWeight.w500,
            color: Theme.of(context).textTheme.titleSmall?.color,
          ),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: _availableTags.map((tag) {
            final isSelected = _selectedTags.contains(tag);
            return FilterChip(
              label: Text(_getTagDisplayName(tag)),
              selected: isSelected,
              onSelected: (selected) {
                setState(() {
                  if (selected) {
                    _selectedTags.add(tag);
                  } else {
                    _selectedTags.remove(tag);
                  }
                });
              },
              selectedColor: Theme.of(context).primaryColor.withValues(alpha: 0.2),
              checkmarkColor: Theme.of(context).primaryColor,
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildDateRangeFilters() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '时间范围',
          style: TextStyle(
            fontWeight: FontWeight.w500,
            color: Theme.of(context).textTheme.titleSmall?.color,
          ),
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: OutlinedButton.icon(
                icon: const Icon(Icons.date_range),
                label: Text(_dateFrom != null
                    ? _formatDate(_dateFrom!)
                    : '开始日期'),
                onPressed: () async {
                  final date = await showDatePicker(
                    context: context,
                    initialDate: _dateFrom ?? DateTime.now(),
                    firstDate: DateTime(2020),
                    lastDate: DateTime.now(),
                  );
                  if (date != null) {
                    setState(() {
                      _dateFrom = date;
                    });
                  }
                },
              ),
            ),
            const SizedBox(width: 8),
            const Text('至'),
            const SizedBox(width: 8),
            Expanded(
              child: OutlinedButton.icon(
                icon: const Icon(Icons.date_range),
                label: Text(_dateTo != null
                    ? _formatDate(_dateTo!)
                    : '结束日期'),
                onPressed: () async {
                  final date = await showDatePicker(
                    context: context,
                    initialDate: _dateTo ?? DateTime.now(),
                    firstDate: _dateFrom ?? DateTime(2020),
                    lastDate: DateTime.now(),
                  );
                  if (date != null) {
                    setState(() {
                      _dateTo = date;
                    });
                  }
                },
              ),
            ),
            if (_dateFrom != null || _dateTo != null)
              IconButton(
                icon: const Icon(Icons.clear),
                onPressed: () {
                  setState(() {
                    _dateFrom = null;
                    _dateTo = null;
                  });
                },
                tooltip: '清除日期范围',
              ),
          ],
        ),
      ],
    );
  }

  Widget _buildAdvancedToggleOptions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '高级选项',
          style: TextStyle(
            fontWeight: FontWeight.w500,
            color: Theme.of(context).textTheme.titleSmall?.color,
          ),
        ),
        const SizedBox(height: 8),
        SwitchListTile(
          title: const Text('语义增强'),
          subtitle: const Text('使用AI增强搜索理解能力'),
          value: _enableSemanticBoost,
          onChanged: (value) {
            setState(() {
              _enableSemanticBoost = value;
            });
          },
          secondary: const Icon(Icons.psychology),
        ),
        SwitchListTile(
          title: const Text('包含元数据'),
          subtitle: const Text('在搜索结果中包含详细元数据信息'),
          value: _includeMetadata,
          onChanged: (value) {
            setState(() {
              _includeMetadata = value;
            });
          },
          secondary: const Icon(Icons.info_outline),
        ),
      ],
    );
  }

  Widget _buildActionButtons() {
    return Row(
      children: [
        Expanded(
          child: OutlinedButton.icon(
            icon: const Icon(Icons.refresh),
            label: const Text('重置'),
            onPressed: _resetSearchOptions,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          flex: 2,
          child: ElevatedButton.icon(
            icon: const Icon(Icons.search),
            label: const Text('高级搜索'),
            onPressed: _queryController.text.trim().isNotEmpty
                ? _performAdvancedSearch
                : null,
          ),
        ),
      ],
    );
  }

  void _toggleExpansion() {
    if (_animationController.isCompleted) {
      _animationController.reverse();
    } else {
      _animationController.forward();
    }
  }

  void _showSearchPresets() {
    showModalBottomSheet(
      context: context,
      builder: (context) => _SearchPresetsSheet(
        onPresetSelected: _applyPreset,
      ),
    );
  }

  void _applyPreset(SearchPreset preset) {
    setState(() {
      _queryController.text = preset.query;
      _resultCount = preset.resultCount;
      _similarityThreshold = preset.threshold;
      _selectedEntityTypes.clear();
      _selectedEntityTypes.addAll(preset.entityTypes);
      _selectedTags.clear();
      _selectedTags.addAll(preset.tags);
    });
    Navigator.of(context).pop();
  }

  // 辅助方法
  String _getEntityTypeDisplayName(String type) {
    switch (type) {
      case 'url': return 'URL链接';
      case 'filePath': return '文件路径';
      case 'email': return '邮箱地址';
      case 'phone': return '电话号码';
      case 'keyword': return '关键词';
      case 'document': return '文档';
      case 'image': return '图片';
      case 'other': return '其他';
      default: return type;
    }
  }

  String _getTagDisplayName(String tag) {
    switch (tag) {
      case 'work': return '工作';
      case 'personal': return '个人';
      case 'important': return '重要';
      case 'urgent': return '紧急';
      case 'archived': return '已归档';
      case 'favorite': return '收藏';
      default: return tag;
    }
  }

  String _formatDate(DateTime date) {
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  }
}

/// 搜索排序顺序
enum SearchSortOrder {
  similarity,
  time,
  relevance,
}

/// 搜索预设
class SearchPreset {
  final String name;
  final String description;
  final String query;
  final int resultCount;
  final double threshold;
  final List<String> entityTypes;
  final List<String> tags;

  const SearchPreset({
    required this.name,
    required this.description,
    required this.query,
    this.resultCount = 20,
    this.threshold = 0.1,
    this.entityTypes = const [],
    this.tags = const [],
  });
}

/// 搜索预设面板
class _SearchPresetsSheet extends StatelessWidget {
  final ValueChanged<SearchPreset> onPresetSelected;

  const _SearchPresetsSheet({
    required this.onPresetSelected,
  });

  static const List<SearchPreset> _presets = [
    SearchPreset(
      name: '工作文档',
      description: '搜索工作相关的文档和资料',
      query: '',
      entityTypes: ['filePath', 'document'],
      tags: ['work'],
      threshold: 0.3,
    ),
    SearchPreset(
      name: '重要链接',
      description: '查找重要的URL链接',
      query: '',
      entityTypes: ['url'],
      tags: ['important'],
      threshold: 0.2,
    ),
    SearchPreset(
      name: '联系信息',
      description: '搜索邮箱和电话号码',
      query: '',
      entityTypes: ['email', 'phone'],
      resultCount: 50,
    ),
    SearchPreset(
      name: '高相似度',
      description: '只显示高度相关的结果',
      query: '',
      threshold: 0.8,
      resultCount: 10,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            '搜索预设',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 16),
          ..._presets.map((preset) => ListTile(
            title: Text(preset.name),
            subtitle: Text(preset.description),
            leading: const Icon(Icons.bookmark_outline),
            onTap: () => onPresetSelected(preset),
          )),
        ],
      ),
    );
  }
}