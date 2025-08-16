// AI洞察展示组件
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/data_insights_models.dart';
import '../../providers/data_insights_provider.dart';
import '../skeleton/empty_state_widgets.dart';
import 'responsive_dashboard_layout.dart';

/// AI洞察展示组件 - 性能优化版本
class AIInsightsWidget extends ConsumerWidget {
  const AIInsightsWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dataInsightsState = ref.watch(dataInsightsProvider);
    final insights = dataInsightsState.overview?.recentInsights ?? [];

    // 性能优化：限制显示的洞察数量
    final limitedInsights = insights.take(5).toList();

    return CollapsibleCard(
      title: 'AI智能洞察',
      subtitle: '基于你的数据发现的智能模式和建议',
      trailing: _buildMoreButton(context),
      child: Column(
        children: [
          if (limitedInsights.isEmpty)
            AIInsightsEmptyState(
              onRefresh: () =>
                  ref.read(dataInsightsProvider.notifier).refresh(),
            )
          else
            // 性能优化：使用ListView.builder替代Column+map
            LayoutBuilder(
              builder: (context, constraints) {
                final maxHeight = constraints.maxHeight.isFinite
                    ? constraints.maxHeight.clamp(200.0, 350.0)
                    : 300.0;

                return SizedBox(
                  height: maxHeight,
                  child: ListView.separated(
                    shrinkWrap: true,
                    physics: const ClampingScrollPhysics(),
                    itemCount: limitedInsights.length,
                    separatorBuilder: (context, index) =>
                        const SizedBox(height: 12),
                    itemBuilder: (context, index) => AIInsightCard(
                      insight: limitedInsights[index],
                    ),
                  ),
                );
              },
            ),

          const SizedBox(height: 8),

          // 查看更多按钮
          if (insights.isNotEmpty)
            TextButton(
              onPressed: () => _showAllInsights(context, insights),
              child: Text(insights.length > 5
                  ? '查看所有洞察 (${insights.length})'
                  : '查看所有洞察'),
            ),
        ],
      ),
    );
  }

  Widget _buildMoreButton(BuildContext context) {
    return IconButton(
      icon: const Icon(Icons.more_vert),
      onPressed: () => _showInsightMenu(context),
      tooltip: '更多选项',
    );
  }

  void _showInsightMenu(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.refresh),
              title: const Text('刷新洞察'),
              onTap: () {
                Navigator.pop(context);
                // TODO: 刷新洞察数据
              },
            ),
            ListTile(
              leading: const Icon(Icons.settings),
              title: const Text('洞察设置'),
              onTap: () {
                Navigator.pop(context);
                // TODO: 打开洞察设置
              },
            ),
            ListTile(
              leading: const Icon(Icons.history),
              title: const Text('历史洞察'),
              onTap: () {
                Navigator.pop(context);
                // TODO: 查看历史洞察
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showAllInsights(BuildContext context, List<AIInsight> insights) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        child: Container(
          width: 600,
          height: 500,
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(
                    '所有AI洞察',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
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
              Expanded(
                child: ListView.separated(
                  itemCount: insights.length,
                  separatorBuilder: (context, index) =>
                      const SizedBox(height: 16),
                  itemBuilder: (context, index) {
                    return AIInsightCard(insight: insights[index]);
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// AI洞察卡片
class AIInsightCard extends StatelessWidget {
  final AIInsight insight;

  const AIInsightCard({
    super.key,
    required this.insight,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Card(
      elevation: 0,
      margin: EdgeInsets.zero,
      color: _getInsightColor(insight.type).withValues(alpha: 0.05),
      child: InkWell(
        onTap: () => _showInsightDetails(context),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  // 洞察类型图标
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color:
                          _getInsightColor(insight.type).withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      _getInsightIcon(insight.type),
                      size: 20,
                      color: _getInsightColor(insight.type),
                    ),
                  ),
                  const SizedBox(width: 12),

                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          insight.title,
                          style: theme.textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        if (insight.detectedAt != null)
                          Text(
                            _formatDateTime(insight.detectedAt!),
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: colorScheme.onSurfaceVariant,
                            ),
                          ),
                      ],
                    ),
                  ),

                  // 置信度指示器
                  ConfidenceIndicator(confidence: insight.confidence),
                ],
              ),

              const SizedBox(height: 12),

              // 洞察描述
              Text(
                insight.description,
                style: theme.textTheme.bodyMedium,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),

              // 相关实体
              if (insight.entities.isNotEmpty) ...[
                const SizedBox(height: 12),
                Wrap(
                  spacing: 6,
                  runSpacing: 4,
                  children: insight.entities
                      .take(5)
                      .map((entity) => Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: _getInsightColor(insight.type)
                                  .withValues(alpha: 0.1),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              entity,
                              style: theme.textTheme.bodySmall?.copyWith(
                                color: _getInsightColor(insight.type),
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ))
                      .toList(),
                ),
              ],

              const SizedBox(height: 12),

              // 操作按钮
              Row(
                children: [
                  const Spacer(),
                  if (insight.actionLabel != null)
                    TextButton(
                      onPressed: () => _performInsightAction(context),
                      child: Text(insight.actionLabel!),
                    ),
                  TextButton(
                    onPressed: () => _showInsightDetails(context),
                    child: const Text('详情'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  IconData _getInsightIcon(String type) {
    switch (type) {
      case 'pattern_detection':
        return Icons.trending_up;
      case 'content_analysis':
        return Icons.lightbulb;
      case 'productivity_insight':
        return Icons.schedule;
      case 'recommendation':
        return Icons.recommend;
      case 'anomaly_detection':
        return Icons.warning;
      default:
        return Icons.psychology;
    }
  }

  Color _getInsightColor(String type) {
    switch (type) {
      case 'pattern_detection':
        return Colors.blue;
      case 'content_analysis':
        return Colors.amber;
      case 'productivity_insight':
        return Colors.green;
      case 'recommendation':
        return Colors.purple;
      case 'anomaly_detection':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }

  String _formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inMinutes < 1) {
      return '刚刚';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}分钟前';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}小时前';
    } else {
      return '${difference.inDays}天前';
    }
  }

  void _performInsightAction(BuildContext context) {
    // TODO: 实现洞察操作
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('执行操作: ${insight.actionLabel}')),
    );
  }

  void _showInsightDetails(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AIInsightDetailDialog(insight: insight),
    );
  }
}

/// 置信度指示器
class ConfidenceIndicator extends StatelessWidget {
  final double confidence;

  const ConfidenceIndicator({
    super.key,
    required this.confidence,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final percentage = (confidence * 100).round();
    final color = _getConfidenceColor(confidence);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            _getConfidenceIcon(confidence),
            size: 12,
            color: color,
          ),
          const SizedBox(width: 4),
          Text(
            '$percentage%',
            style: theme.textTheme.bodySmall?.copyWith(
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Color _getConfidenceColor(double confidence) {
    if (confidence >= 0.8) {
      return Colors.green;
    } else if (confidence >= 0.6) {
      return Colors.orange;
    } else {
      return Colors.red;
    }
  }

  IconData _getConfidenceIcon(double confidence) {
    if (confidence >= 0.8) {
      return Icons.check_circle;
    } else if (confidence >= 0.6) {
      return Icons.help;
    } else {
      return Icons.error;
    }
  }
}

/// AI洞察详情对话框
class AIInsightDetailDialog extends StatelessWidget {
  final AIInsight insight;

  const AIInsightDetailDialog({
    super.key,
    required this.insight,
  });

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
                Icon(
                  Icons.psychology,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  '洞察详情',
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

            // 洞察标题
            Text(
              insight.title,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),

            const SizedBox(height: 8),

            // 置信度和时间
            Row(
              children: [
                ConfidenceIndicator(confidence: insight.confidence),
                const Spacer(),
                if (insight.detectedAt != null)
                  Text(
                    '检测时间: ${_formatDateTime(insight.detectedAt!)}',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
              ],
            ),

            const SizedBox(height: 16),

            // 洞察描述
            Text(
              insight.description,
              style: theme.textTheme.bodyMedium,
            ),

            // 相关实体
            if (insight.entities.isNotEmpty) ...[
              const SizedBox(height: 20),
              Text(
                '相关实体',
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: insight.entities
                    .map((entity) => Chip(
                          label: Text(entity),
                          backgroundColor:
                              theme.colorScheme.surfaceContainerHighest,
                        ))
                    .toList(),
              ),
            ],

            const SizedBox(height: 24),

            // 操作按钮
            Row(
              children: [
                const Spacer(),
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('关闭'),
                ),
                if (insight.actionLabel != null) ...[
                  const SizedBox(width: 12),
                  ElevatedButton(
                    onPressed: () {
                      Navigator.of(context).pop();
                      // TODO: 执行洞察操作
                    },
                    child: Text(insight.actionLabel!),
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.year}/${dateTime.month}/${dateTime.day} ${dateTime.hour}:${dateTime.minute.toString().padLeft(2, '0')}';
  }
}
