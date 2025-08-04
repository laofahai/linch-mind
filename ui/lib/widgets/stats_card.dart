import 'package:flutter/material.dart';

class StatsCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color? color;
  final VoidCallback? onTap;

  const StatsCard({
    super.key,
    required this.title,
    required this.value,
    required this.icon,
    this.color,
    this.onTap,
  });

  // 加载状态构造函数
  const StatsCard.loading({
    super.key,
  }) : title = '',
        value = '',
        icon = Icons.help_outline,
        color = null,
        onTap = null;

  @override
  Widget build(BuildContext context) {
    final cardColor = color ?? Theme.of(context).colorScheme.primary;
    final isLoading = title.isEmpty && value.isEmpty;

    return Card(
      elevation: 2,
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: isLoading 
                          ? Theme.of(context).colorScheme.surfaceContainerHighest
                          : cardColor.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      isLoading ? Icons.help_outline : icon,
                      color: isLoading 
                          ? Theme.of(context).colorScheme.onSurfaceVariant
                          : cardColor,
                      size: 20,
                    ),
                  ),
                  const Spacer(),
                  if (!isLoading && onTap != null)
                    Icon(
                      Icons.arrow_forward_ios,
                      size: 14,
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                ],
              ),
              const SizedBox(height: 12),
              
              // 数值
              if (isLoading) ...[
                Container(
                  height: 28,
                  width: 60,
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
              ] else ...[
                Text(
                  value,
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: cardColor,
                  ),
                ),
              ],
              
              const SizedBox(height: 4),
              
              // 标题
              if (isLoading) ...[
                Container(
                  height: 14,
                  width: double.infinity * 0.8,
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
              ] else ...[
                Text(
                  title,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                    fontWeight: FontWeight.w500,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

// 特殊的趋势统计卡片
class TrendStatsCard extends StatelessWidget {
  final String title;
  final String value;
  final String? previousValue;
  final IconData icon;
  final Color? color;
  final VoidCallback? onTap;

  const TrendStatsCard({
    super.key,
    required this.title,
    required this.value,
    this.previousValue,
    required this.icon,
    this.color,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final cardColor = color ?? Theme.of(context).colorScheme.primary;
    
    // 计算趋势
    double? trendPercentage;
    bool isPositiveTrend = true;
    if (previousValue != null) {
      final current = double.tryParse(value) ?? 0;
      final previous = double.tryParse(previousValue!) ?? 0;
      if (previous > 0) {
        trendPercentage = ((current - previous) / previous) * 100;
        isPositiveTrend = trendPercentage >= 0;
      }
    }

    return Card(
      elevation: 2,
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: cardColor.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      icon,
                      color: cardColor,
                      size: 20,
                    ),
                  ),
                  const Spacer(),
                  if (trendPercentage != null) ...[
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: (isPositiveTrend ? Colors.green : Colors.red).withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            isPositiveTrend ? Icons.trending_up : Icons.trending_down,
                            size: 12,
                            color: isPositiveTrend ? Colors.green : Colors.red,
                          ),
                          const SizedBox(width: 2),
                          Text(
                            '${trendPercentage.abs().toStringAsFixed(1)}%',
                            style: Theme.of(context).textTheme.labelSmall?.copyWith(
                              color: isPositiveTrend ? Colors.green : Colors.red,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
              const SizedBox(height: 12),
              
              // 数值
              Text(
                value,
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: cardColor,
                ),
              ),
              
              const SizedBox(height: 4),
              
              // 标题
              Text(
                title,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                  fontWeight: FontWeight.w500,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// 快速操作统计卡片
class ActionStatsCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final String actionLabel;
  final VoidCallback onActionPressed;
  final Color? color;

  const ActionStatsCard({
    super.key,
    required this.title,
    required this.value,
    required this.icon,
    required this.actionLabel,
    required this.onActionPressed,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final cardColor = color ?? Theme.of(context).colorScheme.primary;

    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: cardColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    icon,
                    color: cardColor,
                    size: 20,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            
            // 数值
            Text(
              value,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: cardColor,
              ),
            ),
            
            const SizedBox(height: 4),
            
            // 标题
            Text(
              title,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
                fontWeight: FontWeight.w500,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            
            const SizedBox(height: 12),
            
            // 操作按钮
            SizedBox(
              width: double.infinity,
              child: FilledButton.tonal(
                onPressed: onActionPressed,
                style: FilledButton.styleFrom(
                  backgroundColor: cardColor.withValues(alpha: 0.1),
                  foregroundColor: cardColor,
                  visualDensity: VisualDensity.compact,
                ),
                child: Text(
                  actionLabel,
                  style: const TextStyle(fontSize: 12),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}