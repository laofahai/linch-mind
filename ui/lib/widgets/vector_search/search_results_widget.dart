// 搜索结果展示组件 - 支持多种显示模式和排序方式
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/data_insights_models.dart';
import '../../providers/vector_search_provider.dart';

/// 显示模式枚举
enum DisplayMode {
  list,     // 列表模式
  grid,     // 网格模式
  compact,  // 紧凑模式
}

/// 排序方式枚举
enum SortOrder {
  similarity,    // 按相似度排序
  timestamp,     // 按时间排序
  relevance,     // 按相关性排序
  entityType,    // 按实体类型排序
}

/// 搜索结果展示组件
class SearchResultsWidget extends ConsumerStatefulWidget {
  final EdgeInsetsGeometry? padding;
  final Function(VectorSearchResult)? onResultTap;
  final Function(String)? onSimilarityTap;

  const SearchResultsWidget({
    super.key,
    this.padding,
    this.onResultTap,
    this.onSimilarityTap,
  });

  @override
  ConsumerState<SearchResultsWidget> createState() => _SearchResultsWidgetState();
}

class _SearchResultsWidgetState extends ConsumerState<SearchResultsWidget> {
  DisplayMode _displayMode = DisplayMode.list;
  SortOrder _sortOrder = SortOrder.similarity;
  bool _showFilters = false;
  final Set<String> _selectedEntityTypes = {};
  double _minSimilarity = 0.0;

  @override
  Widget build(BuildContext context) {
    final searchState = ref.watch(vectorSearchProvider);
    final theme = Theme.of(context);

    return Container(
      padding: widget.padding ?? const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // 控制栏
          _buildControlBar(searchState, theme),
          
          // 筛选面板
          if (_showFilters)
            _buildFilterPanel(searchState, theme),
          
          const SizedBox(height: 16),
          
          // 结果展示
          Expanded(
            child: _buildResultsDisplay(searchState, theme),
          ),
        ],
      ),
    );
  }

  /// 构建控制栏
  Widget _buildControlBar(VectorSearchState searchState, ThemeData theme) {
    final filteredResults = _getFilteredResults(searchState.results);
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            // 结果统计
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '找到 ${filteredResults.length} 个结果',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  if (searchState.currentQuery != null)
                    Text(
                      '查询: "${searchState.currentQuery!.query}"',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.hintColor,
                      ),
                    ),
                ],
              ),
            ),
            
            // 显示模式切换
            SegmentedButton<DisplayMode>(
              segments: const [
                ButtonSegment(
                  value: DisplayMode.list,
                  icon: Icon(Icons.view_list),
                  tooltip: '列表模式',
                ),
                ButtonSegment(
                  value: DisplayMode.grid,
                  icon: Icon(Icons.view_module),
                  tooltip: '网格模式',
                ),
                ButtonSegment(
                  value: DisplayMode.compact,
                  icon: Icon(Icons.view_headline),
                  tooltip: '紧凑模式',
                ),
              ],
              selected: {_displayMode},
              onSelectionChanged: (Set<DisplayMode> selection) {
                setState(() {
                  _displayMode = selection.first;
                });
              },
              style: SegmentedButton.styleFrom(
                visualDensity: VisualDensity.compact,
              ),
            ),
            
            const SizedBox(width: 12),
            
            // 排序下拉菜单
            PopupMenuButton<SortOrder>(
              icon: Icon(Icons.sort, color: theme.primaryColor),
              tooltip: '排序方式',
              onSelected: (SortOrder order) {
                setState(() {
                  _sortOrder = order;
                });
              },
              itemBuilder: (context) => [
                PopupMenuItem(
                  value: SortOrder.similarity,
                  child: Row(
                    children: const [
                      Icon(Icons.trending_up, size: 16),
                      SizedBox(width: 8),
                      Text('相似度'),
                    ],
                  ),
                ),
                PopupMenuItem(
                  value: SortOrder.timestamp,
                  child: Row(
                    children: const [
                      Icon(Icons.access_time, size: 16),
                      SizedBox(width: 8),
                      Text('时间'),
                    ],
                  ),
                ),
                PopupMenuItem(
                  value: SortOrder.relevance,
                  child: Row(
                    children: const [
                      Icon(Icons.star, size: 16),
                      SizedBox(width: 8),
                      Text('相关性'),
                    ],
                  ),
                ),
                PopupMenuItem(
                  value: SortOrder.entityType,
                  child: Row(
                    children: const [
                      Icon(Icons.category, size: 16),
                      SizedBox(width: 8),
                      Text('类型'),
                    ],
                  ),
                ),
              ],
            ),
            
            // 筛选按钮
            IconButton(
              icon: Icon(
                _showFilters ? Icons.filter_list_off : Icons.filter_list,
                color: _showFilters ? theme.primaryColor : theme.hintColor,
              ),
              onPressed: () {
                setState(() {
                  _showFilters = !_showFilters;
                });
              },
              tooltip: '筛选选项',
            ),
          ],
        ),
      ),
    );
  }

  /// 构建筛选面板
  Widget _buildFilterPanel(VectorSearchState searchState, ThemeData theme) {
    final entityTypes = searchState.results
        .map((r) => r.entityType ?? '未知')
        .toSet()
        .toList()..sort();

    return Card(
      margin: const EdgeInsets.only(top: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '筛选选项',
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            
            // 实体类型筛选
            if (entityTypes.isNotEmpty) ...[
              Text(
                '实体类型',
                style: theme.textTheme.bodySmall,
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 4,
                children: entityTypes.map((type) {
                  final isSelected = _selectedEntityTypes.contains(type);
                  return FilterChip(
                    label: Text(type),
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
                  );
                }).toList(),
              ),
              const SizedBox(height: 16),
            ],
            
            // 相似度阈值
            Row(
              children: [
                Text(
                  '最低相似度: ${_minSimilarity.toStringAsFixed(2)}',
                  style: theme.textTheme.bodySmall,
                ),
                Expanded(
                  child: Slider(
                    value: _minSimilarity,
                    min: 0.0,
                    max: 1.0,
                    divisions: 20,
                    onChanged: (value) {
                      setState(() {
                        _minSimilarity = value;
                      });
                    },
                  ),
                ),
              ],
            ),
            
            // 清除筛选按钮
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: () {
                    setState(() {
                      _selectedEntityTypes.clear();
                      _minSimilarity = 0.0;
                    });
                  },
                  child: const Text('清除筛选'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  /// 构建结果显示
  Widget _buildResultsDisplay(VectorSearchState searchState, ThemeData theme) {
    if (searchState.isLoading) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const CircularProgressIndicator(),
            const SizedBox(height: 16),
            Text(
              '正在搜索...',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.hintColor,
              ),
            ),
          ],
        ),
      );
    }

    if (searchState.error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 48,
              color: theme.colorScheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              '搜索出错',
              style: theme.textTheme.titleMedium?.copyWith(
                color: theme.colorScheme.error,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              searchState.error!,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.hintColor,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () {
                if (searchState.currentQuery != null) {
                  ref.read(vectorSearchProvider.notifier)
                      .search(searchState.currentQuery!);
                }
              },
              icon: const Icon(Icons.refresh),
              label: const Text('重试'),
            ),
          ],
        ),
      );
    }

    final results = _getSortedResults(_getFilteredResults(searchState.results));

    if (results.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.search_off,
              size: 48,
              color: theme.hintColor,
            ),
            const SizedBox(height: 16),
            Text(
              searchState.currentQuery != null ? '未找到匹配结果' : '请输入搜索关键词',
              style: theme.textTheme.titleMedium?.copyWith(
                color: theme.hintColor,
              ),
            ),
            if (searchState.currentQuery != null) ...[
              const SizedBox(height: 8),
              Text(
                '尝试使用不同的关键词或调整搜索条件',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.hintColor,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ],
        ),
      );
    }

    switch (_displayMode) {
      case DisplayMode.list:
        return _buildListView(results, theme);
      case DisplayMode.grid:
        return _buildGridView(results, theme);
      case DisplayMode.compact:
        return _buildCompactView(results, theme);
    }
  }

  /// 构建列表视图
  Widget _buildListView(List<VectorSearchResult> results, ThemeData theme) {
    return ListView.separated(
      itemCount: results.length,
      separatorBuilder: (context, index) => const Divider(height: 1),
      itemBuilder: (context, index) {
        final result = results[index];
        return _buildResultCard(result, theme, isCompact: false);
      },
    );
  }

  /// 构建网格视图
  Widget _buildGridView(List<VectorSearchResult> results, ThemeData theme) {
    return GridView.builder(
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
        childAspectRatio: 1.2,
      ),
      itemCount: results.length,
      itemBuilder: (context, index) {
        final result = results[index];
        return _buildResultCard(result, theme, isGrid: true);
      },
    );
  }

  /// 构建紧凑视图
  Widget _buildCompactView(List<VectorSearchResult> results, ThemeData theme) {
    return ListView.builder(
      itemCount: results.length,
      itemBuilder: (context, index) {
        final result = results[index];
        return _buildResultCard(result, theme, isCompact: true);
      },
    );
  }

  /// 构建结果卡片
  Widget _buildResultCard(
    VectorSearchResult result, 
    ThemeData theme, {
    bool isCompact = false,
    bool isGrid = false,
  }) {
    return Card(
      margin: isCompact 
          ? const EdgeInsets.symmetric(horizontal: 4, vertical: 2)
          : const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      elevation: isGrid ? 2 : 1,
      child: InkWell(
        onTap: () => widget.onResultTap?.call(result),
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: EdgeInsets.all(isCompact ? 8 : 12),
          child: isGrid 
              ? _buildGridItemContent(result, theme)
              : _buildListItemContent(result, theme, isCompact),
        ),
      ),
    );
  }

  /// 构建列表项内容
  Widget _buildListItemContent(
    VectorSearchResult result, 
    ThemeData theme, 
    bool isCompact,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 头部信息
        Row(
          children: [
            // 实体类型图标
            _buildEntityTypeIcon(result.entityType, theme),
            const SizedBox(width: 8),
            
            // 相似度评分
            _buildSimilarityScore(result.similarity, theme),
            
            const Spacer(),
            
            // 时间戳
            if (result.timestamp != null)
              Text(
                _formatDateTime(result.timestamp!),
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.hintColor,
                ),
              ),
          ],
        ),
        
        const SizedBox(height: 8),
        
        // 内容文本
        Text(
          result.content,
          style: theme.textTheme.bodyMedium,
          maxLines: isCompact ? 2 : 3,
          overflow: TextOverflow.ellipsis,
        ),
        
        // 高亮词汇
        if (result.highlightedTerms.isNotEmpty && !isCompact) ...[
          const SizedBox(height: 8),
          Wrap(
            spacing: 4,
            runSpacing: 2,
            children: result.highlightedTerms.take(3).map((term) {
              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: theme.primaryColor.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  term,
                  style: TextStyle(
                    fontSize: 10,
                    color: theme.primaryColor,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              );
            }).toList(),
          ),
        ],
        
        // 操作按钮
        if (!isCompact) ...[
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              TextButton.icon(
                onPressed: () => widget.onSimilarityTap?.call(result.id),
                icon: const Icon(Icons.compare, size: 16),
                label: const Text('相似分析'),
                style: TextButton.styleFrom(
                  visualDensity: VisualDensity.compact,
                ),
              ),
            ],
          ),
        ],
      ],
    );
  }

  /// 构建网格项内容
  Widget _buildGridItemContent(VectorSearchResult result, ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 头部
        Row(
          children: [
            _buildEntityTypeIcon(result.entityType, theme),
            const Spacer(),
            _buildSimilarityScore(result.similarity, theme),
          ],
        ),
        
        const SizedBox(height: 12),
        
        // 内容
        Expanded(
          child: Text(
            result.content,
            style: theme.textTheme.bodyMedium,
            maxLines: 4,
            overflow: TextOverflow.ellipsis,
          ),
        ),
        
        // 底部信息
        if (result.timestamp != null)
          Text(
            _formatDateTime(result.timestamp!),
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.hintColor,
            ),
          ),
      ],
    );
  }

  /// 构建实体类型图标
  Widget _buildEntityTypeIcon(String? entityType, ThemeData theme) {
    IconData icon;
    Color color;
    
    switch (entityType) {
      case 'url':
        icon = Icons.link;
        color = Colors.blue;
        break;
      case 'filePath':
        icon = Icons.folder;
        color = Colors.orange;
        break;
      case 'email':
        icon = Icons.email;
        color = Colors.green;
        break;
      case 'phone':
        icon = Icons.phone;
        color = Colors.purple;
        break;
      case 'keyword':
        icon = Icons.label;
        color = Colors.red;
        break;
      default:
        icon = Icons.article;
        color = theme.hintColor;
    }
    
    return Container(
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        shape: BoxShape.circle,
      ),
      child: Icon(
        icon,
        size: 16,
        color: color,
      ),
    );
  }

  /// 构建相似度评分
  Widget _buildSimilarityScore(double similarity, ThemeData theme) {
    final percentage = (similarity * 100).round();
    Color color;
    
    if (percentage >= 80) {
      color = Colors.green;
    } else if (percentage >= 60) {
      color = Colors.orange;
    } else {
      color = Colors.red;
    }
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        '$percentage%',
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.bold,
          color: color,
        ),
      ),
    );
  }

  /// 获取筛选后的结果
  List<VectorSearchResult> _getFilteredResults(List<VectorSearchResult> results) {
    return results.where((result) {
      // 实体类型筛选
      if (_selectedEntityTypes.isNotEmpty) {
        final entityType = result.entityType ?? '未知';
        if (!_selectedEntityTypes.contains(entityType)) {
          return false;
        }
      }
      
      // 相似度筛选
      if (result.similarity < _minSimilarity) {
        return false;
      }
      
      return true;
    }).toList();
  }

  /// 获取排序后的结果
  List<VectorSearchResult> _getSortedResults(List<VectorSearchResult> results) {
    final sortedResults = List<VectorSearchResult>.from(results);
    
    switch (_sortOrder) {
      case SortOrder.similarity:
        sortedResults.sort((a, b) => b.similarity.compareTo(a.similarity));
        break;
      case SortOrder.timestamp:
        sortedResults.sort((a, b) {
          final aTime = a.timestamp ?? DateTime.fromMillisecondsSinceEpoch(0);
          final bTime = b.timestamp ?? DateTime.fromMillisecondsSinceEpoch(0);
          return bTime.compareTo(aTime);
        });
        break;
      case SortOrder.relevance:
        // 结合相似度和高亮词汇数量
        sortedResults.sort((a, b) {
          final aRelevance = a.similarity + (a.highlightedTerms.length * 0.1);
          final bRelevance = b.similarity + (b.highlightedTerms.length * 0.1);
          return bRelevance.compareTo(aRelevance);
        });
        break;
      case SortOrder.entityType:
        sortedResults.sort((a, b) {
          final aType = a.entityType ?? '';
          final bType = b.entityType ?? '';
          return aType.compareTo(bType);
        });
        break;
    }
    
    return sortedResults;
  }

  /// 格式化日期时间
  String _formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);
    
    if (difference.inDays > 0) {
      return '${difference.inDays}天前';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}小时前';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}分钟前';
    } else {
      return '刚刚';
    }
  }
}