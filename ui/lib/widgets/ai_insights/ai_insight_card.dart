import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/ai_insight_models.dart';

/// AI洞察卡片组件
class AIInsightCardWidget extends ConsumerWidget {
  final AIInsightCard insight;
  final VoidCallback? onTap;
  final Function(AIInsightAction)? onActionTap;
  final VoidCallback? onDismiss;

  const AIInsightCardWidget({
    super.key,
    required this.insight,
    this.onTap,
    this.onActionTap,
    this.onDismiss,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Dismissible(
      key: Key(insight.id),
      direction: DismissDirection.endToStart,
      onDismissed: (_) => onDismiss?.call(),
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 16),
        decoration: BoxDecoration(
          color: colorScheme.errorContainer,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Icon(
          Icons.delete_outline,
          color: colorScheme.onErrorContainer,
        ),
      ),
      child: Card(
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHeader(context),
                const SizedBox(height: 12),
                _buildContent(context),
                if (insight.entities.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  _buildEntities(context),
                ],
                if (insight.actions.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  _buildActions(context),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: _getTypeColor(context).withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            _getTypeIcon(),
            size: 20,
            color: _getTypeColor(context),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                insight.title,
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 2),
              Row(
                children: [
                  Text(
                    _formatTimestamp(),
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: colorScheme.secondaryContainer,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      '${(insight.confidence * 100).toInt()}%',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: colorScheme.onSecondaryContainer,
                        fontSize: 10,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        if (!insight.isRead)
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: colorScheme.primary,
              shape: BoxShape.circle,
            ),
          ),
      ],
    );
  }

  Widget _buildContent(BuildContext context) {
    final theme = Theme.of(context);
    
    return Text(
      insight.message,
      style: theme.textTheme.bodyMedium?.copyWith(
        height: 1.4,
      ),
    );
  }

  Widget _buildEntities(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Wrap(
      spacing: 6,
      runSpacing: 6,
      children: insight.entities.take(3).map((entity) {
        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: colorScheme.surfaceContainerHighest,
            borderRadius: BorderRadius.circular(6),
          ),
          child: Text(
            entity,
            style: theme.textTheme.bodySmall?.copyWith(
              color: colorScheme.onSurfaceVariant,
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildActions(BuildContext context) {
    return Wrap(
      spacing: 8,
      children: insight.actions.map((action) {
        return _ActionButton(
          action: action,
          onTap: () => onActionTap?.call(action),
        );
      }).toList(),
    );
  }

  IconData _getTypeIcon() {
    switch (insight.type) {
      case 'discovery':
        return Icons.lightbulb_outline;
      case 'suggestion':
        return Icons.tips_and_updates_outlined;
      case 'pattern':
        return Icons.trending_up;
      case 'alert':
        return Icons.notification_important_outlined;
      default:
        return Icons.info_outline;
    }
  }

  Color _getTypeColor(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    switch (insight.type) {
      case 'discovery':
        return colorScheme.primary;
      case 'suggestion':
        return Colors.green;
      case 'pattern':
        return Colors.orange;
      case 'alert':
        return colorScheme.error;
      default:
        return colorScheme.onSurfaceVariant;
    }
  }

  String _formatTimestamp() {
    final now = DateTime.now();
    final diff = now.difference(insight.timestamp);
    
    if (diff.inMinutes < 1) {
      return '刚刚';
    } else if (diff.inMinutes < 60) {
      return '${diff.inMinutes}分钟前';
    } else if (diff.inHours < 24) {
      return '${diff.inHours}小时前';
    } else {
      return '${diff.inDays}天前';
    }
  }
}

/// 操作按钮组件
class _ActionButton extends StatelessWidget {
  final AIInsightAction action;
  final VoidCallback? onTap;

  const _ActionButton({
    required this.action,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    final isPrimary = action.type == 'primary';
    
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isPrimary ? colorScheme.primary : Colors.transparent,
          border: isPrimary ? null : Border.all(
            color: colorScheme.outline.withValues(alpha: 0.5),
          ),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Text(
          action.label,
          style: theme.textTheme.bodySmall?.copyWith(
            color: isPrimary 
                ? colorScheme.onPrimary 
                : colorScheme.onSurfaceVariant,
            fontWeight: isPrimary ? FontWeight.w500 : FontWeight.normal,
          ),
        ),
      ),
    );
  }
}