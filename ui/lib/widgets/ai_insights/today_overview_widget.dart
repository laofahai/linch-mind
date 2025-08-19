import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/ai_insight_models.dart';

/// 今日概览组件
class TodayOverviewWidget extends ConsumerWidget {
  final TodayOverview overview;

  const TodayOverviewWidget({
    super.key,
    required this.overview,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            colorScheme.primaryContainer,
            colorScheme.primaryContainer.withValues(alpha: 0.7),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.wb_sunny_outlined,
                color: colorScheme.onPrimaryContainer,
                size: 24,
              ),
              const SizedBox(width: 8),
              Text(
                '今日概览',
                style: theme.textTheme.titleLarge?.copyWith(
                  color: colorScheme.onPrimaryContainer,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _StatItem(
                  value: overview.newDataPoints,
                  label: '新数据点',
                  icon: Icons.fiber_new,
                  color: colorScheme.onPrimaryContainer,
                ),
              ),
              Expanded(
                child: _StatItem(
                  value: overview.aiProcessedItems,
                  label: 'AI处理',
                  icon: Icons.psychology,
                  color: colorScheme.onPrimaryContainer,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _StatItem(
                  value: overview.insightsGenerated,
                  label: '生成洞察',
                  icon: Icons.lightbulb,
                  color: colorScheme.onPrimaryContainer,
                ),
              ),
              Expanded(
                child: _StatItem(
                  value: overview.activeConnectors,
                  label: '活跃连接器',
                  icon: Icons.link,
                  color: colorScheme.onPrimaryContainer,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            '最后更新: ${_formatLastUpdate()}',
            style: theme.textTheme.bodySmall?.copyWith(
              color: colorScheme.onPrimaryContainer.withValues(alpha: 0.8),
            ),
          ),
        ],
      ),
    );
  }

  String _formatLastUpdate() {
    final now = DateTime.now();
    final diff = now.difference(overview.lastUpdate);
    
    if (diff.inMinutes < 1) {
      return '刚刚';
    } else if (diff.inMinutes < 60) {
      return '${diff.inMinutes}分钟前';
    } else {
      return '${overview.lastUpdate.hour}:${overview.lastUpdate.minute.toString().padLeft(2, '0')}';
    }
  }
}

/// 统计项目组件
class _StatItem extends StatelessWidget {
  final int value;
  final String label;
  final IconData icon;
  final Color color;

  const _StatItem({
    required this.value,
    required this.label,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(
              icon,
              size: 16,
              color: color.withValues(alpha: 0.8),
            ),
            const SizedBox(width: 4),
            Text(
              _formatValue(value),
              style: theme.textTheme.headlineSmall?.copyWith(
                color: color,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: theme.textTheme.bodySmall?.copyWith(
            color: color.withValues(alpha: 0.8),
          ),
        ),
      ],
    );
  }

  String _formatValue(int value) {
    if (value >= 1000) {
      return '${(value / 1000).toStringAsFixed(1)}k';
    }
    return value.toString();
  }
}