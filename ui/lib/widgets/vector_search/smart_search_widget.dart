// 智能搜索框组件 - 支持实时建议和语义搜索
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/data_insights_models.dart';
import '../../providers/vector_search_provider.dart';

/// 智能搜索框组件
class SmartSearchWidget extends ConsumerStatefulWidget {
  final String hintText;
  final VoidCallback? onAdvancedSearch;
  final Function(String)? onSearchSubmitted;
  final EdgeInsetsGeometry? margin;
  final bool showVectorStatus;

  const SmartSearchWidget({
    super.key,
    this.hintText = '智能语义搜索...',
    this.onAdvancedSearch,
    this.onSearchSubmitted,
    this.margin,
    this.showVectorStatus = true,
  });

  @override
  ConsumerState<SmartSearchWidget> createState() => _SmartSearchWidgetState();
}

class _SmartSearchWidgetState extends ConsumerState<SmartSearchWidget>
    with SingleTickerProviderStateMixin {
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focusNode = FocusNode();
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  bool _isExpanded = false;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 200),
      vsync: this,
    );
    _scaleAnimation = Tween<double>(begin: 1.0, end: 1.02).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );

    _focusNode.addListener(() {
      setState(() {
        _isExpanded = _focusNode.hasFocus;
      });
      if (_focusNode.hasFocus) {
        _animationController.forward();
      } else {
        _animationController.reverse();
      }
    });

    _controller.addListener(() {
      final query = _controller.text.trim();
      if (query.isNotEmpty) {
        ref.read(vectorSearchProvider.notifier).getSuggestions(query);
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final searchState = ref.watch(vectorSearchProvider);
    final theme = Theme.of(context);

    return Container(
      margin: widget.margin ?? const EdgeInsets.all(16),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // 主搜索框
          AnimatedBuilder(
            animation: _scaleAnimation,
            builder: (context, child) {
              return Transform.scale(
                scale: _scaleAnimation.value,
                child: Card(
                  elevation: _isExpanded ? 8 : 4,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                    side: BorderSide(
                      color: _isExpanded 
                          ? theme.primaryColor 
                          : theme.dividerColor,
                      width: _isExpanded ? 2 : 1,
                    ),
                  ),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    child: Row(
                      children: [
                        // AI 图标指示器
                        _buildAIIndicator(searchState),
                        const SizedBox(width: 12),
                        
                        // 搜索输入框
                        Expanded(
                          child: TextField(
                            controller: _controller,
                            focusNode: _focusNode,
                            decoration: InputDecoration(
                              hintText: widget.hintText,
                              border: InputBorder.none,
                              hintStyle: TextStyle(
                                color: theme.hintColor,
                                fontSize: 16,
                              ),
                            ),
                            style: const TextStyle(fontSize: 16),
                            textInputAction: TextInputAction.search,
                            onSubmitted: (value) => _handleSearch(value.trim()),
                          ),
                        ),
                        
                        // 搜索按钮
                        if (_controller.text.isNotEmpty) ...[
                          IconButton(
                            icon: Icon(Icons.clear, 
                                     color: theme.hintColor),
                            onPressed: () {
                              _controller.clear();
                              ref.read(vectorSearchProvider.notifier).clearResults();
                            },
                          ),
                        ],
                        
                        // 搜索按钮
                        Container(
                          margin: const EdgeInsets.only(left: 8),
                          child: IconButton(
                            icon: searchState.isLoading
                                ? SizedBox(
                                    width: 20,
                                    height: 20,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      valueColor: AlwaysStoppedAnimation<Color>(
                                        theme.primaryColor,
                                      ),
                                    ),
                                  )
                                : Icon(Icons.search, color: theme.primaryColor),
                            onPressed: searchState.isLoading
                                ? null
                                : () => _handleSearch(_controller.text.trim()),
                          ),
                        ),
                        
                        // 高级搜索按钮
                        if (widget.onAdvancedSearch != null)
                          IconButton(
                            icon: Icon(Icons.tune, color: theme.primaryColor),
                            onPressed: widget.onAdvancedSearch,
                            tooltip: '高级搜索选项',
                          ),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
          
          // 搜索建议下拉列表
          if (_isExpanded && searchState.suggestions.isNotEmpty)
            _buildSuggestionsDropdown(searchState.suggestions, theme),
          
          // 向量数据库状态指示器
          if (widget.showVectorStatus && searchState.metrics != null)
            _buildVectorStatusBar(searchState.metrics!, theme),
          
          // 搜索模式指示器
          _buildSearchModeIndicator(searchState.searchMode, theme),
        ],
      ),
    );
  }

  /// 构建AI指示器
  Widget _buildAIIndicator(VectorSearchState searchState) {
    final theme = Theme.of(context);
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: theme.primaryColor.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.psychology,
            size: 16,
            color: theme.primaryColor,
          ),
          const SizedBox(width: 4),
          Text(
            'AI',
            style: TextStyle(
              color: theme.primaryColor,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  /// 构建搜索建议下拉列表
  Widget _buildSuggestionsDropdown(List<SearchSuggestion> suggestions, ThemeData theme) {
    return Card(
      margin: const EdgeInsets.only(top: 4),
      elevation: 8,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: suggestions.take(5).map((suggestion) {
          return InkWell(
            onTap: () => _handleSuggestionTap(suggestion),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              child: Row(
                children: [
                  Icon(
                    _getSuggestionIcon(suggestion.type),
                    size: 16,
                    color: theme.hintColor,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: RichText(
                      text: TextSpan(
                        style: TextStyle(color: theme.textTheme.bodyMedium?.color),
                        children: _buildHighlightedText(
                          suggestion.text,
                          suggestion.matchedTerms,
                          theme,
                        ),
                      ),
                    ),
                  ),
                  if (suggestion.confidence > 0.8)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: Colors.green.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        '精确',
                        style: TextStyle(
                          color: Colors.green,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                ],
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  /// 构建向量数据库状态栏
  Widget _buildVectorStatusBar(VectorMetrics metrics, ThemeData theme) {
    return Container(
      margin: const EdgeInsets.only(top: 8),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: theme.cardColor,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: theme.dividerColor),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.storage,
            size: 14,
            color: theme.primaryColor,
          ),
          const SizedBox(width: 6),
          Text(
            '向量库: ${_formatNumber(metrics.totalVectors)}条',
            style: TextStyle(
              fontSize: 12,
              color: theme.textTheme.bodySmall?.color,
            ),
          ),
          const SizedBox(width: 12),
          Icon(
            Icons.speed,
            size: 14,
            color: Colors.green,
          ),
          const SizedBox(width: 4),
          Text(
            '${metrics.searchTimeAvgMs.toStringAsFixed(1)}ms',
            style: TextStyle(
              fontSize: 12,
              color: theme.textTheme.bodySmall?.color,
            ),
          ),
        ],
      ),
    );
  }

  /// 构建搜索模式指示器
  Widget _buildSearchModeIndicator(SearchMode mode, ThemeData theme) {
    final modeInfo = _getSearchModeInfo(mode);
    
    return Container(
      margin: const EdgeInsets.only(top: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: modeInfo['color'].withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  modeInfo['icon'],
                  size: 14,
                  color: modeInfo['color'],
                ),
                const SizedBox(width: 4),
                Text(
                  modeInfo['label'],
                  style: TextStyle(
                    color: modeInfo['color'],
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 处理搜索提交
  void _handleSearch(String query) {
    if (query.isEmpty) return;
    
    _focusNode.unfocus();
    
    final searchQuery = VectorSearchQuery(
      query: query,
      k: 20, // 默认返回20个结果
      threshold: 0.3, // 相似度阈值
    );
    
    ref.read(vectorSearchProvider.notifier).search(searchQuery);
    
    if (widget.onSearchSubmitted != null) {
      widget.onSearchSubmitted!(query);
    }
  }

  /// 处理建议点击
  void _handleSuggestionTap(SearchSuggestion suggestion) {
    _controller.text = suggestion.text;
    _handleSearch(suggestion.text);
  }

  /// 获取建议图标
  IconData _getSuggestionIcon(String? type) {
    switch (type) {
      case 'entity':
        return Icons.account_box;
      case 'keyword':
        return Icons.label;
      case 'content':
        return Icons.article;
      default:
        return Icons.search;
    }
  }

  /// 构建高亮文本
  List<TextSpan> _buildHighlightedText(
    String text, 
    List<String> matchedTerms, 
    ThemeData theme,
  ) {
    if (matchedTerms.isEmpty) {
      return [TextSpan(text: text)];
    }
    
    final spans = <TextSpan>[];
    var remaining = text;
    
    for (final term in matchedTerms) {
      final index = remaining.toLowerCase().indexOf(term.toLowerCase());
      if (index != -1) {
        if (index > 0) {
          spans.add(TextSpan(text: remaining.substring(0, index)));
        }
        spans.add(TextSpan(
          text: remaining.substring(index, index + term.length),
          style: TextStyle(
            backgroundColor: theme.primaryColor.withValues(alpha: 0.2),
            fontWeight: FontWeight.bold,
          ),
        ));
        remaining = remaining.substring(index + term.length);
      }
    }
    
    if (remaining.isNotEmpty) {
      spans.add(TextSpan(text: remaining));
    }
    
    return spans;
  }

  /// 获取搜索模式信息
  Map<String, dynamic> _getSearchModeInfo(SearchMode mode) {
    switch (mode) {
      case SearchMode.simple:
        return {
          'label': '智能搜索',
          'icon': Icons.search,
          'color': Colors.blue,
        };
      case SearchMode.advanced:
        return {
          'label': '高级搜索',
          'icon': Icons.tune,
          'color': Colors.purple,
        };
      case SearchMode.similarity:
        return {
          'label': '相似性分析',
          'icon': Icons.compare,
          'color': Colors.orange,
        };
      case SearchMode.clustering:
        return {
          'label': '聚类分析',
          'icon': Icons.scatter_plot,
          'color': Colors.green,
        };
    }
  }

  /// 格式化数字显示
  String _formatNumber(int number) {
    if (number >= 1000000) {
      return '${(number / 1000000).toStringAsFixed(1)}M';
    } else if (number >= 1000) {
      return '${(number / 1000).toStringAsFixed(1)}K';
    } else {
      return number.toString();
    }
  }
}