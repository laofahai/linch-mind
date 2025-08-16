// 时间线展示组件
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/data_insights_models.dart';
import '../../providers/data_insights_provider.dart';
import 'responsive_dashboard_layout.dart';

/// 活动时间线组件
class TimelineWidget extends ConsumerWidget {
  final int? maxItems;
  final bool showFilters;

  const TimelineWidget({
    super.key,
    this.maxItems,
    this.showFilters = true,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final timelineState = ref.watch(timelineProvider);

    return CollapsibleCard(
      title: '活动时间线',
      subtitle: '系统采集和分析活动的实时记录',
      trailing: _buildTimelineActions(context, ref),
      child: Column(
        children: [
          if (showFilters) ...[
            TimelineFilters(),
            const SizedBox(height: 16),
          ],
          _buildTimelineContent(context, timelineState),
        ],
      ),
    );
  }

  Widget _buildTimelineActions(BuildContext context, WidgetRef ref) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        IconButton(
          icon: const Icon(Icons.refresh),
          onPressed: () => ref.read(timelineProvider.notifier).loadTimeline(),
          tooltip: '刷新时间线',
        ),
        PopupMenuButton<String>(
          icon: const Icon(Icons.more_vert),
          onSelected: (value) => _handleMenuAction(context, ref, value),
          itemBuilder: (context) => [
            const PopupMenuItem(value: 'export', child: Text('导出时间线')),
            const PopupMenuItem(value: 'clear', child: Text('清除历史')),
            const PopupMenuItem(value: 'settings', child: Text('时间线设置')),
          ],
        ),
      ],
    );
  }

  Widget _buildTimelineContent(BuildContext context, TimelineState state) {
    if (state.isLoading) {
      return const SizedBox(
        height: 300,
        child: Center(child: CircularProgressIndicator()),
      );
    }

    if (state.error != null) {
      return Container(
        height: 300,
        alignment: Alignment.center,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 48,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(height: 12),
            Text('加载时间线失败'),
            const SizedBox(height: 8),
            TextButton(
              onPressed: () {}, // TODO: 重试
              child: const Text('重试'),
            ),
          ],
        ),
      );
    }

    if (state.items.isEmpty) {
      return _buildEmptyTimeline(context);
    }

    final displayItems =
        maxItems != null ? state.items.take(maxItems!).toList() : state.items;

    return Container(
      constraints: const BoxConstraints(maxHeight: 500),
      child: ListView.separated(
        shrinkWrap: true,
        physics: const ClampingScrollPhysics(), // 性能优化：更流畅的滚动
        itemCount: displayItems.length,
        separatorBuilder: (context, index) => const SizedBox(height: 12),
        itemBuilder: (context, index) {
          final item = displayItems[index];
          final isLast = index == displayItems.length - 1;
          return RepaintBoundary(
            // 性能优化：减少不必要的重绘
            child: TimelineItemWidget(
              item: item,
              isLast: isLast,
            ),
          );
        },
      ),
    );
  }

  Widget _buildEmptyTimeline(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      height: 300,
      alignment: Alignment.center,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.timeline,
            size: 48,
            color: theme.colorScheme.onSurfaceVariant,
          ),
          const SizedBox(height: 16),
          Text(
            '暂无活动记录',
            style: theme.textTheme.titleMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '当连接器开始采集数据时，活动记录将出现在这里',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  void _handleMenuAction(BuildContext context, WidgetRef ref, String action) {
    switch (action) {
      case 'export':
        // TODO: 导出时间线
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('导出功能开发中...')),
        );
        break;
      case 'clear':
        _showClearConfirmation(context);
        break;
      case 'settings':
        // TODO: 打开时间线设置
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('设置功能开发中...')),
        );
        break;
    }
  }

  void _showClearConfirmation(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('清除时间线'),
        content: const Text('确定要清除所有时间线记录吗？此操作不可撤销。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              // TODO: 清除时间线
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
            child: const Text('清除'),
          ),
        ],
      ),
    );
  }
}

/// 时间线筛选器
class TimelineFilters extends ConsumerWidget {
  const TimelineFilters({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Expanded(
            child: DropdownButtonFormField<String>(
              decoration: const InputDecoration(
                labelText: '活动类型',
                isDense: true,
                border: OutlineInputBorder(),
              ),
              items: const [
                DropdownMenuItem(value: null, child: Text('全部类型')),
                DropdownMenuItem(value: 'entity_created', child: Text('实体创建')),
                DropdownMenuItem(
                    value: 'insight_generated', child: Text('洞察生成')),
                DropdownMenuItem(
                    value: 'connector_activity', child: Text('连接器活动')),
                DropdownMenuItem(
                    value: 'analysis_completed', child: Text('分析完成')),
              ],
              onChanged: (value) {
                // TODO: 筛选时间线
              },
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: DropdownButtonFormField<String>(
              decoration: const InputDecoration(
                labelText: '时间范围',
                isDense: true,
                border: OutlineInputBorder(),
              ),
              items: const [
                DropdownMenuItem(value: 'today', child: Text('今天')),
                DropdownMenuItem(value: 'week', child: Text('本周')),
                DropdownMenuItem(value: 'month', child: Text('本月')),
                DropdownMenuItem(value: 'all', child: Text('全部')),
              ],
              onChanged: (value) {
                // TODO: 筛选时间线
              },
            ),
          ),
        ],
      ),
    );
  }
}

/// 时间线项目组件
class TimelineItemWidget extends StatelessWidget {
  final TimelineItem item;
  final bool isLast;

  const TimelineItemWidget({
    super.key,
    required this.item,
    this.isLast = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return SizedBox(
      height: 90.0, // 固定高度避免IntrinsicHeight约束问题
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 时间线指示器
          SizedBox(
            width: 32,
            child: Column(
              children: [
                Container(
                  width: 32,
                  height: 32,
                  decoration: BoxDecoration(
                    color: _getActivityColor(item.type).withValues(alpha: 0.1),
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: _getActivityColor(item.type),
                      width: 2,
                    ),
                  ),
                  child: Icon(
                    _getActivityIcon(item.type),
                    size: 16,
                    color: _getActivityColor(item.type),
                  ),
                ),
                if (!isLast)
                  Expanded(
                    child: Container(
                      width: 2,
                      margin: const EdgeInsets.symmetric(vertical: 8),
                      decoration: BoxDecoration(
                        color: colorScheme.outline.withValues(alpha: 0.3),
                      ),
                    ),
                  ),
              ],
            ),
          ),

          const SizedBox(width: 16),

          // 内容
          Expanded(
            child: Card(
              elevation: 0,
              margin: EdgeInsets.zero,
              color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            item.title,
                            style: theme.textTheme.titleSmall?.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        Text(
                          _formatTimestamp(item.timestamp),
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ),

                    if (item.description != null) ...[
                      const SizedBox(height: 4),
                      Flexible(
                        child: Text(
                          item.description!,
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: colorScheme.onSurfaceVariant,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],

                    // 连接器标识
                    if (item.connectorId != null) ...[
                      const SizedBox(height: 4),
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: _getActivityColor(item.type)
                              .withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          item.connectorId!,
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: _getActivityColor(item.type),
                            fontWeight: FontWeight.w500,
                            fontSize: 10,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  IconData _getActivityIcon(String type) {
    switch (type) {
      case 'entity_created':
        return Icons.add_circle;
      case 'insight_generated':
        return Icons.psychology;
      case 'connector_activity':
        return Icons.sensors;
      case 'analysis_completed':
        return Icons.analytics;
      default:
        return Icons.info;
    }
  }

  Color _getActivityColor(String type) {
    switch (type) {
      case 'entity_created':
        return Colors.green;
      case 'insight_generated':
        return Colors.purple;
      case 'connector_activity':
        return Colors.blue;
      case 'analysis_completed':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);

    if (difference.inMinutes < 1) {
      return '刚刚';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}分钟前';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}小时前';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}天前';
    } else {
      return '${timestamp.month}/${timestamp.day}';
    }
  }
}

/// 趋势实体展示组件
class TrendingEntitiesWidget extends ConsumerWidget {
  const TrendingEntitiesWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dataInsightsState = ref.watch(dataInsightsProvider);
    final trendingEntities = dataInsightsState.overview?.trendingEntities ?? [];

    // 性能优化：限制显示数量，避免溢出
    final limitedEntities = trendingEntities.take(4).toList();

    return CollapsibleCard(
      title: '趋势实体',
      subtitle: '当前最活跃和增长最快的数据实体',
      child: LayoutBuilder(
        builder: (context, constraints) {
          final maxHeight = constraints.maxHeight.isFinite
              ? constraints.maxHeight.clamp(100.0, 300.0)
              : 250.0;

          return SizedBox(
            height: maxHeight,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (limitedEntities.isEmpty)
                  Expanded(child: _buildEmptyTrending(context))
                else
                  Expanded(
                    child: ListView.separated(
                      shrinkWrap: true,
                      physics: const ClampingScrollPhysics(),
                      itemCount: limitedEntities.length,
                      separatorBuilder: (context, index) =>
                          const SizedBox(height: 6),
                      itemBuilder: (context, index) => TrendingEntityCard(
                        entity: limitedEntities[index],
                      ),
                    ),
                  ),
                if (trendingEntities.length > 4)
                  Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: TextButton(
                      onPressed: () {}, // TODO: 显示更多
                      child: Text('查看全部 (${trendingEntities.length})'),
                    ),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildEmptyTrending(BuildContext context) {
    final theme = Theme.of(context);

    return LayoutBuilder(
      builder: (context, constraints) {
        final maxHeight = constraints.maxHeight.isFinite
            ? constraints.maxHeight.clamp(80.0, 180.0)
            : 120.0;

        return Container(
          height: maxHeight,
          alignment: Alignment.center,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.trending_up,
                size: (maxHeight * 0.25).clamp(20.0, 36.0),
                color: theme.colorScheme.onSurfaceVariant,
              ),
              SizedBox(height: (maxHeight * 0.08).clamp(4.0, 12.0)),
              Flexible(
                child: Text(
                  '暂无趋势数据',
                  style: theme.textTheme.titleSmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

/// 趋势实体卡片
class TrendingEntityCard extends StatelessWidget {
  final TrendingEntity entity;

  const TrendingEntityCard({
    super.key,
    required this.entity,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return ConstrainedBox(
      constraints: const BoxConstraints(
        minHeight: 45.0,
        maxHeight: 60.0,
      ),
      child: Card(
        elevation: 0,
        margin: EdgeInsets.zero,
        color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.2),
        child: Padding(
          padding: const EdgeInsets.all(8), // 减少padding
          child: Row(
            children: [
              // 实体类型图标
              Container(
                padding: const EdgeInsets.all(4), // 减少padding
                decoration: BoxDecoration(
                  color: _getEntityTypeColor().withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Icon(
                  _getEntityTypeIcon(),
                  size: 14, // 减小图标尺寸
                  color: _getEntityTypeColor(),
                ),
              ),

              const SizedBox(width: 8), // 减少间距

              // 实体信息
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.center,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Flexible(
                      child: Text(
                        entity.name,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    if (entity.description != null) ...[
                      const SizedBox(height: 1),
                      Flexible(
                        child: Text(
                          entity.description!,
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: colorScheme.onSurfaceVariant,
                            fontSize: 10, // 减小字体
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ],
                ),
              ),

              const SizedBox(width: 8),

              // 频次和趋势
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                mainAxisAlignment: MainAxisAlignment.center,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Flexible(
                    child: Text(
                      '${entity.frequency}',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  if (entity.trend != null)
                    Container(
                      margin: const EdgeInsets.only(top: 1),
                      padding: const EdgeInsets.symmetric(
                          horizontal: 4, vertical: 1),
                      decoration: BoxDecoration(
                        color: _getTrendColor().withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        entity.trend!,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: _getTrendColor(),
                          fontWeight: FontWeight.w600,
                          fontSize: 9,
                        ),
                      ),
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  IconData _getEntityTypeIcon() {
    switch (entity.type) {
      case 'project':
        return Icons.folder_special;
      case 'skill':
        return Icons.star;
      case 'topic':
        return Icons.topic;
      default:
        return Icons.label;
    }
  }

  Color _getEntityTypeColor() {
    switch (entity.type) {
      case 'project':
        return Colors.blue;
      case 'skill':
        return Colors.green;
      case 'topic':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }

  Color _getTrendColor() {
    final trendValue = entity.trendValue ?? 0;
    return trendValue > 0 ? Colors.green : Colors.red;
  }
}
