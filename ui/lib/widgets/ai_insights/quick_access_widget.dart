import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/ai_insight_models.dart';

/// 快速访问组件
class QuickAccessWidget extends ConsumerWidget {
  final List<QuickAccessItem> items;
  final Function(QuickAccessItem)? onItemTap;

  const QuickAccessWidget({
    super.key,
    required this.items,
    this.onItemTap,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);

    if (items.isEmpty) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            children: [
              Icon(
                Icons.flash_on,
                size: 20,
                color: theme.colorScheme.primary,
              ),
              const SizedBox(width: 8),
              Text(
                '快速访问',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        SizedBox(
          height: 100,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            itemCount: items.length,
            itemBuilder: (context, index) {
              final item = items[index];
              return _QuickAccessCard(
                item: item,
                onTap: () => onItemTap?.call(item),
              );
            },
          ),
        ),
      ],
    );
  }
}

/// 快速访问卡片
class _QuickAccessCard extends StatelessWidget {
  final QuickAccessItem item;
  final VoidCallback? onTap;

  const _QuickAccessCard({
    required this.item,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Container(
      width: 140,
      margin: const EdgeInsets.only(right: 12),
      child: Card(
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(
                        color: _getTypeColor(colorScheme).withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Icon(
                        _getTypeIcon(),
                        size: 16,
                        color: _getTypeColor(colorScheme),
                      ),
                    ),
                    const Spacer(),
                    Icon(
                      Icons.arrow_forward_ios,
                      size: 12,
                      color: colorScheme.onSurfaceVariant,
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item.title,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.w500,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 2),
                      Text(
                        item.subtitle,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: colorScheme.onSurfaceVariant,
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
      ),
    );
  }

  IconData _getTypeIcon() {
    switch (item.type) {
      case 'url':
        return Icons.link;
      case 'file':
        return Icons.description;
      case 'contact':
        return Icons.person;
      case 'note':
        return Icons.note;
      default:
        return Icons.info;
    }
  }

  Color _getTypeColor(ColorScheme colorScheme) {
    switch (item.type) {
      case 'url':
        return Colors.blue;
      case 'file':
        return Colors.orange;
      case 'contact':
        return Colors.green;
      case 'note':
        return Colors.purple;
      default:
        return colorScheme.primary;
    }
  }
}