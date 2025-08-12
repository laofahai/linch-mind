// 统计概览组件
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/data_insights_models.dart';
import '../../providers/data_insights_provider.dart';
import 'responsive_dashboard_layout.dart';

/// 统计概览组件
class StatsOverviewWidget extends ConsumerWidget {
  const StatsOverviewWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dataInsightsState = ref.watch(dataInsightsProvider);
    final stats = dataInsightsState.overview?.todayStats ?? const TodayStats();

    return RepaintBoundary( // 性能优化：避免不必要的重绘
      child: ResponsiveGrid(
        maxCrossAxisExtent: 280, // 减小最大宽度
        childAspectRatio: 3.2, // 调整宽高比，给内容更多垂直空间
        children: [
          StatCard(
          title: '新增实体',
          value: stats.newEntities.toString(),
          subtitle: '今日采集',
          icon: Icons.add_circle_outline,
          color: Colors.blue,
          trend: '+12%',
          trendUp: true,
        ),
        StatCard(
          title: '活跃连接器',
          value: stats.activeConnectors.toString(),
          subtitle: '正在运行',
          icon: Icons.sensors,
          color: Colors.green,
          trend: '100%',
          trendUp: true,
        ),
        StatCard(
          title: 'AI分析',
          value: stats.aiAnalysisCompleted.toString(),
          subtitle: '已完成',
          icon: Icons.psychology,
          color: Colors.purple,
          trend: '+8%',
          trendUp: true,
        ),
        StatCard(
          title: '知识连接',
          value: stats.knowledgeConnections.toString(),
          subtitle: '新建关联',
          icon: Icons.account_tree,
          color: Colors.orange,
          trend: '+15%',
          trendUp: true,
        ),
        ],
      ),
    );
  }
}

/// 统计卡片
class StatCard extends StatelessWidget {
  final String title;
  final String value;
  final String subtitle;
  final IconData icon;
  final Color color;
  final String? trend;
  final bool? trendUp;
  final VoidCallback? onTap;

  const StatCard({
    super.key,
    required this.title,
    required this.value,
    required this.subtitle,
    required this.icon,
    required this.color,
    this.trend,
    this.trendUp,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.all(16), // 减少padding避免溢出
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                color.withValues(alpha: 0.05),
                color.withValues(alpha: 0.02),
              ],
            ),
          ),
          child: LayoutBuilder(
            builder: (context, constraints) {
              // 动态计算可用高度，防止溢出
              final availableHeight = constraints.maxHeight.isFinite 
                  ? constraints.maxHeight 
                  : 120.0; // 默认最小高度
              
              return SizedBox(
                height: availableHeight.clamp(80.0, 120.0), // 限制高度范围
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: color.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      icon,
                      color: color,
                      size: 20,
                    ),
                  ),
                  const Spacer(),
                  if (trend != null)
                    TrendIndicator(
                      trend: trend!,
                      isUp: trendUp ?? true,
                    ),
                ],
              ),
                  const SizedBox(height: 8), // 减少间距
                  Flexible(
                    child: Text(
                      value,
                      style: theme.textTheme.headlineSmall?.copyWith( // 使用更小的字体
                        fontWeight: FontWeight.bold,
                        color: colorScheme.onSurface,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Flexible(
                    child: Text(
                      title,
                      style: theme.textTheme.bodyMedium?.copyWith( // 调整字体大小
                        color: colorScheme.onSurfaceVariant,
                        fontWeight: FontWeight.w500,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  const SizedBox(height: 1),
                  Flexible(
                    child: Text(
                      subtitle,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: colorScheme.onSurfaceVariant,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  ],
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}

/// 趋势指示器
class TrendIndicator extends StatelessWidget {
  final String trend;
  final bool isUp;

  const TrendIndicator({
    super.key,
    required this.trend,
    required this.isUp,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final color = isUp ? Colors.green : Colors.red;

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
            isUp ? Icons.trending_up : Icons.trending_down,
            size: 14,
            color: color,
          ),
          const SizedBox(width: 4),
          Text(
            trend,
            style: theme.textTheme.bodySmall?.copyWith(
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    ); // 关闭RepaintBoundary
  }
}

/// 实体类型分布图表
class EntityBreakdownChart extends ConsumerWidget {
  const EntityBreakdownChart({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dataInsightsState = ref.watch(dataInsightsProvider);
    final breakdown = dataInsightsState.overview?.entityBreakdown ?? const EntityBreakdown();
    final theme = Theme.of(context);

    final items = [
      _ChartItem('URL', breakdown.url, Colors.blue),
      _ChartItem('文件路径', breakdown.filePath, Colors.green),
      _ChartItem('邮箱', breakdown.email, Colors.orange),
      _ChartItem('电话', breakdown.phone, Colors.red),
      _ChartItem('关键词', breakdown.keyword, Colors.purple),
      _ChartItem('其他', breakdown.other, Colors.grey),
    ].where((item) => item.value > 0).toList();

    final total = items.fold<int>(0, (sum, item) => sum + item.value);

    return LayoutBuilder(
      builder: (context, constraints) {
        final availableHeight = constraints.maxHeight.isFinite 
            ? constraints.maxHeight.clamp(120.0, 300.0)
            : 200.0;
        final chartHeight = (availableHeight * 0.4).clamp(60.0, 120.0);
        
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16), // 减少padding
            child: SizedBox(
              height: availableHeight,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    '实体类型分布',
                    style: theme.textTheme.titleMedium?.copyWith( // 使用较小的标题
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 12), // 减少间距
                  if (total > 0) ...[
                    // 简化的饼图效果
                    Container(
                      height: chartHeight,
                      child: Row(
                        children: items.map((item) {
                          final ratio = item.value / total;
                          return Expanded(
                            flex: (ratio * 100).round().clamp(1, 100),
                            child: Container(
                              height: double.infinity,
                              decoration: BoxDecoration(
                                color: item.color.withValues(alpha: 0.8),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              margin: const EdgeInsets.symmetric(horizontal: 1),
                            ),
                          );
                        }).toList(),
                      ),
                    ),
                    const SizedBox(height: 12), // 减少间距
                    // 图例 - 使用Flexible避免溢出
                    Flexible(
                      child: Wrap(
                        spacing: 12,
                        runSpacing: 6,
                        children: items.map((item) => _buildLegendItem(context, item)).toList(),
                      ),
                    ),
                  ] else
                    Expanded(
                      child: Container(
                        alignment: Alignment.center,
                        child: Text(
                          '暂无数据',
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildLegendItem(BuildContext context, _ChartItem item) {
    final theme = Theme.of(context);
    
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: item.color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 6),
        Text(
          '${item.label} (${item.value})',
          style: theme.textTheme.bodySmall,
        ),
      ],
    );
  }
}

class _ChartItem {
  final String label;
  final int value;
  final Color color;

  _ChartItem(this.label, this.value, this.color);
}