// 搜索体验优化组件 - 搜索历史、快捷操作、智能建议
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../models/data_insights_models.dart';
import '../../providers/vector_search_provider.dart';
import '../../utils/app_logger.dart';

/// 搜索体验增强组件
class SearchExperienceWidget extends ConsumerStatefulWidget {
  final bool showHistory;
  final bool showQuickActions;
  final bool showMetrics;

  const SearchExperienceWidget({
    super.key,
    this.showHistory = true,
    this.showQuickActions = true,
    this.showMetrics = true,
  });

  @override
  ConsumerState<SearchExperienceWidget> createState() =>
      _SearchExperienceWidgetState();
}

class _SearchExperienceWidgetState extends ConsumerState<SearchExperienceWidget>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final PageController _pageController = PageController();

  @override
  void initState() {
    super.initState();
    _tabController = TabController(
      length: 3,
      vsync: this,
    );
  }

  @override
  void dispose() {
    _tabController.dispose();
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Theme.of(context).dividerColor,
        ),
      ),
      child: Column(
        children: [
          // 标签栏
          _buildTabBar(),
          
          // 内容区域
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                if (widget.showHistory) _buildHistoryTab(),
                if (widget.showQuickActions) _buildQuickActionsTab(),
                if (widget.showMetrics) _buildMetricsTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTabBar() {
    final tabs = <Widget>[];
    
    if (widget.showHistory) {
      tabs.add(const Tab(
        icon: Icon(Icons.history),
        text: '搜索历史',
      ));
    }
    
    if (widget.showQuickActions) {
      tabs.add(const Tab(
        icon: Icon(Icons.flash_on),
        text: '快捷操作',
      ));
    }
    
    if (widget.showMetrics) {
      tabs.add(const Tab(
        icon: Icon(Icons.analytics),
        text: '性能指标',
      ));
    }

    return Container(
      decoration: BoxDecoration(
        border: Border(
          bottom: BorderSide(
            color: Theme.of(context).dividerColor,
            width: 1,
          ),
        ),
      ),
      child: TabBar(
        controller: _tabController,
        tabs: tabs,
        labelColor: Theme.of(context).primaryColor,
        unselectedLabelColor: Theme.of(context).hintColor,
        indicatorColor: Theme.of(context).primaryColor,
      ),
    );
  }

  Widget _buildHistoryTab() {
    final searchState = ref.watch(vectorSearchProvider);
    
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 历史记录标题和操作
          Row(
            children: [
              const Icon(Icons.history, size: 20),
              const SizedBox(width: 8),
              Text(
                '搜索历史',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: Theme.of(context).primaryColor,
                ),
              ),
              const Spacer(),
              if (searchState.history.isNotEmpty)
                IconButton(
                  icon: const Icon(Icons.clear_all),
                  tooltip: '清除历史',
                  onPressed: _clearSearchHistory,
                ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          // 历史记录列表
          Expanded(
            child: _buildHistoryList(searchState.history),
          ),
        ],
      ),
    );
  }

  Widget _buildHistoryList(List<SearchHistory> history) {
    if (history.isEmpty) {
      return _buildEmptyHistoryState();
    }

    return ListView.builder(
      itemCount: history.length,
      itemBuilder: (context, index) {
        final item = history[index];
        return _buildHistoryItem(item);
      },
    );
  }

  Widget _buildHistoryItem(SearchHistory item) {
    return ListTile(
      leading: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: Theme.of(context).primaryColor.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(
          Icons.search,
          color: Theme.of(context).primaryColor,
          size: 20,
        ),
      ),
      title: Text(
        item.query,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
        style: const TextStyle(fontWeight: FontWeight.w500),
      ),
      subtitle: Row(
        children: [
          Text(_formatTimestamp(item.timestamp)),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: _getResultCountColor(item.resultsCount).withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              '${item.resultsCount}条结果',
              style: TextStyle(
                fontSize: 12,
                color: _getResultCountColor(item.resultsCount),
              ),
            ),
          ),
          const SizedBox(width: 8),
          Text(
            '${item.searchTime.toStringAsFixed(2)}s',
            style: TextStyle(
              fontSize: 12,
              color: Theme.of(context).hintColor,
            ),
          ),
        ],
      ),
      trailing: PopupMenuButton<String>(
        onSelected: (action) => _handleHistoryAction(action, item),
        itemBuilder: (context) => [
          const PopupMenuItem(
            value: 'search',
            child: ListTile(
              leading: Icon(Icons.search),
              title: Text('重新搜索'),
              contentPadding: EdgeInsets.zero,
            ),
          ),
          const PopupMenuItem(
            value: 'copy',
            child: ListTile(
              leading: Icon(Icons.copy),
              title: Text('复制查询'),
              contentPadding: EdgeInsets.zero,
            ),
          ),
          const PopupMenuItem(
            value: 'delete',
            child: ListTile(
              leading: Icon(Icons.delete),
              title: Text('删除'),
              contentPadding: EdgeInsets.zero,
            ),
          ),
        ],
      ),
      onTap: () => _repeatSearch(item),
    );
  }

  Widget _buildEmptyHistoryState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.history,
            size: 64,
            color: Theme.of(context).hintColor,
          ),
          const SizedBox(height: 16),
          Text(
            '暂无搜索历史',
            style: TextStyle(
              fontSize: 16,
              color: Theme.of(context).hintColor,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '开始搜索后，历史记录将出现在这里',
            style: TextStyle(
              fontSize: 14,
              color: Theme.of(context).hintColor,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActionsTab() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 快捷操作标题
          Row(
            children: [
              const Icon(Icons.flash_on, size: 20),
              const SizedBox(width: 8),
              Text(
                '快捷操作',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: Theme.of(context).primaryColor,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // 快速搜索模板
          _buildQuickSearchTemplates(),
          
          const SizedBox(height: 16),
          
          // 搜索技巧
          _buildSearchTips(),
          
          const SizedBox(height: 16),
          
          // 批量操作
          _buildBatchOperations(),
        ],
      ),
    );
  }

  Widget _buildQuickSearchTemplates() {
    final templates = [
      QuickSearchTemplate(
        title: '今天的文件',
        query: '今天创建的文档',
        icon: Icons.today,
        color: Colors.blue,
      ),
      QuickSearchTemplate(
        title: '重要邮件',
        query: '重要邮件地址',
        icon: Icons.email,
        color: Colors.orange,
      ),
      QuickSearchTemplate(
        title: '工作链接',
        query: '工作相关链接',
        icon: Icons.work,
        color: Colors.green,
      ),
      QuickSearchTemplate(
        title: '代码片段',
        query: '编程代码',
        icon: Icons.code,
        color: Colors.purple,
      ),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '快速搜索模板',
          style: TextStyle(
            fontWeight: FontWeight.w500,
            color: Theme.of(context).textTheme.titleSmall?.color,
          ),
        ),
        const SizedBox(height: 8),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            crossAxisSpacing: 8,
            mainAxisSpacing: 8,
            childAspectRatio: 2.5,
          ),
          itemCount: templates.length,
          itemBuilder: (context, index) {
            final template = templates[index];
            return _buildTemplateCard(template);
          },
        ),
      ],
    );
  }

  Widget _buildTemplateCard(QuickSearchTemplate template) {
    return Card(
      elevation: 1,
      child: InkWell(
        onTap: () => _useTemplate(template),
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              Container(
                width: 32,
                height: 32,
                decoration: BoxDecoration(
                  color: template.color.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  template.icon,
                  color: template.color,
                  size: 16,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      template.title,
                      style: const TextStyle(
                        fontWeight: FontWeight.w500,
                        fontSize: 13,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    Text(
                      template.query,
                      style: TextStyle(
                        fontSize: 11,
                        color: Theme.of(context).hintColor,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSearchTips() {
    final tips = [
      '使用自然语言描述您要查找的内容',
      '添加上下文信息可以提高搜索精度',
      '尝试同义词和相关词汇扩大搜索范围',
      '调整相似度阈值以获得更精确的结果',
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '搜索技巧',
          style: TextStyle(
            fontWeight: FontWeight.w500,
            color: Theme.of(context).textTheme.titleSmall?.color,
          ),
        ),
        const SizedBox(height: 8),
        ...tips.map((tip) => Padding(
          padding: const EdgeInsets.only(bottom: 4),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                margin: const EdgeInsets.only(top: 6),
                width: 4,
                height: 4,
                decoration: BoxDecoration(
                  color: Theme.of(context).primaryColor,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  tip,
                  style: TextStyle(
                    fontSize: 14,
                    color: Theme.of(context).textTheme.bodyMedium?.color,
                  ),
                ),
              ),
            ],
          ),
        )),
      ],
    );
  }

  Widget _buildBatchOperations() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '批量操作',
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
                icon: const Icon(Icons.refresh),
                label: const Text('刷新索引'),
                onPressed: _refreshVectorIndex,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: OutlinedButton.icon(
                icon: const Icon(Icons.download),
                label: const Text('导出结果'),
                onPressed: _exportSearchResults,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildMetricsTab() {
    final searchState = ref.watch(vectorSearchProvider);
    
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 性能指标标题
          Row(
            children: [
              const Icon(Icons.analytics, size: 20),
              const SizedBox(width: 8),
              Text(
                '性能指标',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: Theme.of(context).primaryColor,
                ),
              ),
              const Spacer(),
              IconButton(
                icon: const Icon(Icons.refresh),
                tooltip: '刷新指标',
                onPressed: () {
                  ref.read(vectorSearchProvider.notifier).refreshMetrics();
                },
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // 指标内容
          Expanded(
            child: _buildMetricsContent(searchState.metrics),
          ),
        ],
      ),
    );
  }

  Widget _buildMetricsContent(VectorMetrics? metrics) {
    if (metrics == null) {
      return _buildMetricsLoadingState();
    }

    return SingleChildScrollView(
      child: Column(
        children: [
          // 基本指标
          _buildMetricsGrid([
            MetricItem(
              title: '向量总数',
              value: metrics.totalVectors.toString(),
              icon: Icons.storage,
              color: Colors.blue,
            ),
            MetricItem(
              title: '向量维度',
              value: metrics.dimension.toString(),
              icon: Icons.view_in_ar,
              color: Colors.green,
            ),
            MetricItem(
              title: '内存使用',
              value: '${metrics.memoryUsageMb.toStringAsFixed(1)} MB',
              icon: Icons.memory,
              color: Colors.orange,
            ),
            MetricItem(
              title: '平均搜索时间',
              value: '${metrics.searchTimeAvgMs.toStringAsFixed(1)} ms',
              icon: Icons.speed,
              color: Colors.purple,
            ),
          ]),
          
          const SizedBox(height: 16),
          
          // 索引信息
          _buildIndexInfo(metrics),
          
          const SizedBox(height: 16),
          
          // 搜索统计
          _buildSearchStats(ref.watch(vectorSearchProvider)),
        ],
      ),
    );
  }

  Widget _buildMetricsGrid(List<MetricItem> items) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: 1.5,
      ),
      itemCount: items.length,
      itemBuilder: (context, index) {
        final item = items[index];
        return _buildMetricCard(item);
      },
    );
  }

  Widget _buildMetricCard(MetricItem item) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 32,
                  height: 32,
                  decoration: BoxDecoration(
                    color: item.color.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    item.icon,
                    color: item.color,
                    size: 16,
                  ),
                ),
                const Spacer(),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              item.value,
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: item.color,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              item.title,
              style: TextStyle(
                fontSize: 12,
                color: Theme.of(context).hintColor,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildIndexInfo(VectorMetrics metrics) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '索引信息',
              style: TextStyle(
                fontWeight: FontWeight.w600,
                color: Theme.of(context).primaryColor,
              ),
            ),
            const SizedBox(height: 12),
            _buildInfoRow('索引类型', metrics.indexType ?? '未知'),
            _buildInfoRow('最后更新', _formatTimestamp(metrics.lastUpdated ?? DateTime.now())),
            _buildInfoRow('存储效率', '${((metrics.totalVectors * metrics.dimension * 4) / 1024 / 1024 / metrics.memoryUsageMb * 100).toStringAsFixed(1)}%'),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Text(
            label,
            style: TextStyle(
              color: Theme.of(context).hintColor,
            ),
          ),
          const Spacer(),
          Text(
            value,
            style: const TextStyle(
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchStats(VectorSearchState searchState) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '搜索统计',
              style: TextStyle(
                fontWeight: FontWeight.w600,
                color: Theme.of(context).primaryColor,
              ),
            ),
            const SizedBox(height: 12),
            _buildInfoRow('历史搜索', '${searchState.history.length}次'),
            _buildInfoRow('当前结果', '${searchState.results.length}条'),
            if (searchState.lastSearchDuration != null)
              _buildInfoRow('上次搜索用时', '${searchState.lastSearchDuration!.toStringAsFixed(3)}s'),
            if (searchState.lastSearchTime != null)
              _buildInfoRow('最近搜索', _formatTimestamp(searchState.lastSearchTime!)),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricsLoadingState() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(),
          SizedBox(height: 16),
          Text('加载性能指标...'),
        ],
      ),
    );
  }

  // 事件处理方法
  void _clearSearchHistory() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('清除搜索历史'),
        content: const Text('确定要清除所有搜索历史吗？此操作无法撤销。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              ref.read(vectorSearchProvider.notifier).clearSearchHistory();
              Navigator.of(context).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('搜索历史已清除')),
              );
            },
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }

  void _handleHistoryAction(String action, SearchHistory item) {
    switch (action) {
      case 'search':
        _repeatSearch(item);
        break;
      case 'copy':
        // TODO: 复制到剪贴板
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('已复制: ${item.query}')),
        );
        break;
      case 'delete':
        // TODO: 删除单个历史记录
        break;
    }
  }

  void _repeatSearch(SearchHistory item) {
    ref.read(vectorSearchProvider.notifier).searchFromHistory(item);
    AppLogger.info('重新执行搜索: ${item.query}', module: 'SearchExperience');
  }

  void _useTemplate(QuickSearchTemplate template) {
    ref.read(vectorSearchProvider.notifier).quickSearch(template.query);
    AppLogger.info('使用搜索模板: ${template.title}', module: 'SearchExperience');
  }

  void _refreshVectorIndex() {
    // TODO: 调用向量索引刷新API
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('正在刷新向量索引...')),
    );
  }

  void _exportSearchResults() {
    // TODO: 导出搜索结果
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('导出功能开发中...')),
    );
  }

  // 辅助方法
  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);
    
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

  Color _getResultCountColor(int count) {
    if (count >= 20) return Colors.green;
    if (count >= 10) return Colors.orange;
    if (count >= 5) return Colors.blue;
    return Colors.grey;
  }
}

/// 快速搜索模板
class QuickSearchTemplate {
  final String title;
  final String query;
  final IconData icon;
  final Color color;

  const QuickSearchTemplate({
    required this.title,
    required this.query,
    required this.icon,
    required this.color,
  });
}

/// 性能指标项
class MetricItem {
  final String title;
  final String value;
  final IconData icon;
  final Color color;

  const MetricItem({
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
  });
}