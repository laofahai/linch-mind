import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/ai_chat_models.dart';
import '../../utils/responsive_utils.dart';

/// AI聊天消息组件
class AIChatMessageWidget extends ConsumerWidget {
  final AIChatMessage message;
  final Function(MessageAction)? onActionTap;
  final VoidCallback? onTap;

  const AIChatMessageWidget({
    super.key,
    required this.message,
    this.onActionTap,
    this.onTap,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final isAI = _isAIMessage(message.type);
    final maxWidth = ResponsiveUtils.getMessageMaxWidth(context);
    final pagePadding = ResponsiveUtils.getPagePadding(context);

    return Container(
      margin: EdgeInsets.symmetric(
        horizontal: pagePadding.horizontal,
        vertical: 8,
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (isAI) ...[
            _buildAvatar(context, isAI: true),
            const SizedBox(width: 12),
          ],
          Expanded(
            child: Column(
              crossAxisAlignment:
                  isAI ? CrossAxisAlignment.start : CrossAxisAlignment.end,
              children: [
                Container(
                  constraints: BoxConstraints(maxWidth: maxWidth),
                  child: _buildMessageBubble(context, theme, isAI),
                ),
                if (message.actions.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Container(
                    constraints: BoxConstraints(maxWidth: maxWidth),
                    child: _buildActions(context, theme),
                  ),
                ],
                const SizedBox(height: 4),
                _buildTimestamp(context, theme, isAI),
              ],
            ),
          ),
          if (!isAI) ...[
            const SizedBox(width: 12),
            _buildAvatar(context, isAI: false),
          ],
        ],
      ),
    );
  }

  Widget _buildAvatar(BuildContext context, {required bool isAI}) {
    final theme = Theme.of(context);

    return Container(
      width: 36,
      height: 36,
      decoration: BoxDecoration(
        color: isAI
            ? theme.colorScheme.primaryContainer
            : theme.colorScheme.secondaryContainer,
        shape: BoxShape.circle,
      ),
      child: Icon(
        isAI ? Icons.psychology : Icons.person,
        size: 20,
        color: isAI
            ? theme.colorScheme.onPrimaryContainer
            : theme.colorScheme.onSecondaryContainer,
      ),
    );
  }

  Widget _buildMessageBubble(BuildContext context, ThemeData theme, bool isAI) {
    final backgroundColor = isAI
        ? theme.colorScheme.surfaceContainerHighest
        : theme.colorScheme.primaryContainer;

    final textColor = isAI
        ? theme.colorScheme.onSurfaceVariant
        : theme.colorScheme.onPrimaryContainer;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: backgroundColor,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft:
                isAI ? const Radius.circular(4) : const Radius.circular(16),
            bottomRight:
                isAI ? const Radius.circular(16) : const Radius.circular(4),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (_shouldShowTypeLabel()) ...[
              _buildTypeLabel(context, theme),
              const SizedBox(height: 8),
            ],
            Text(
              message.content,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: textColor,
                height: 1.4,
              ),
            ),
            if (message.status == MessageStatus.sending) ...[
              const SizedBox(height: 8),
              _buildThinkingIndicator(context, theme),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildTypeLabel(BuildContext context, ThemeData theme) {
    String label;
    IconData icon;
    Color color;

    switch (message.type) {
      case MessageType.aiInsight:
        label = '💡 洞察发现';
        icon = Icons.lightbulb_outline;
        color = Colors.amber;
        break;
      case MessageType.aiRecommendation:
        label = '🎯 智能推荐';
        icon = Icons.recommend;
        color = Colors.blue;
        break;
      case MessageType.aiQuestion:
        label = '❓ AI询问';
        icon = Icons.help_outline;
        color = Colors.purple;
        break;
      case MessageType.systemUpdate:
        label = '📡 系统更新';
        icon = Icons.info_outline;
        color = Colors.green;
        break;
      default:
        return const SizedBox.shrink();
    }

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 16, color: color),
        const SizedBox(width: 4),
        Text(
          label,
          style: theme.textTheme.bodySmall?.copyWith(
            color: color,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Widget _buildActions(BuildContext context, ThemeData theme) {
    return Wrap(
      spacing: 8,
      runSpacing: 6,
      children: message.actions
          .map((action) => _ActionChip(
                action: action,
                onTap: () => onActionTap?.call(action),
              ))
          .toList(),
    );
  }

  Widget _buildTimestamp(BuildContext context, ThemeData theme, bool isAI) {
    return Padding(
      padding: EdgeInsets.only(left: isAI ? 0 : 48, right: isAI ? 48 : 0),
      child: Text(
        _formatTimestamp(message.timestamp),
        style: theme.textTheme.bodySmall?.copyWith(
          color: theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.6),
          fontSize: 11,
        ),
        textAlign: isAI ? TextAlign.left : TextAlign.right,
      ),
    );
  }

  Widget _buildThinkingIndicator(BuildContext context, ThemeData theme) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: 16,
          height: 16,
          child: CircularProgressIndicator(
            strokeWidth: 2,
            valueColor: AlwaysStoppedAnimation(
              theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.6),
            ),
          ),
        ),
        const SizedBox(width: 8),
        Text(
          'AI正在思考...',
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.6),
            fontStyle: FontStyle.italic,
          ),
        ),
      ],
    );
  }

  bool _isAIMessage(MessageType type) {
    return [
      MessageType.aiGreeting,
      MessageType.aiInsight,
      MessageType.aiRecommendation,
      MessageType.aiQuestion,
      MessageType.systemUpdate,
    ].contains(type);
  }

  bool _shouldShowTypeLabel() {
    return [
      MessageType.aiInsight,
      MessageType.aiRecommendation,
      MessageType.aiQuestion,
      MessageType.systemUpdate,
    ].contains(message.type);
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final diff = now.difference(timestamp);

    if (diff.inMinutes < 1) {
      return '刚刚';
    } else if (diff.inMinutes < 60) {
      return '${diff.inMinutes}分钟前';
    } else if (diff.inHours < 24) {
      return '${diff.inHours}小时前';
    } else if (diff.inDays < 7) {
      return '${diff.inDays}天前';
    } else {
      return '${timestamp.month}/${timestamp.day}';
    }
  }
}

/// 操作芯片组件
class _ActionChip extends StatelessWidget {
  final MessageAction action;
  final VoidCallback? onTap;

  const _ActionChip({
    required this.action,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isPrimary = action.type == ActionType.quickReply;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isPrimary
              ? theme.colorScheme.primary
              : theme.colorScheme.outline.withValues(alpha: 0.1),
          border: isPrimary
              ? null
              : Border.all(
                  color: theme.colorScheme.outline.withValues(alpha: 0.3),
                ),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Text(
          action.label,
          style: theme.textTheme.bodySmall?.copyWith(
            color: isPrimary
                ? theme.colorScheme.onPrimary
                : theme.colorScheme.onSurfaceVariant,
            fontWeight: isPrimary ? FontWeight.w500 : FontWeight.normal,
          ),
        ),
      ),
    );
  }
}
