import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/ai_chat_models.dart';
import '../../utils/responsive_utils.dart';

/// AI智能推荐组件
class AIRecommendationWidget extends ConsumerWidget {
  final List<AIRecommendation> recommendations;
  final Function(AIRecommendation)? onRecommendationTap;
  final String title;

  const AIRecommendationWidget({
    super.key,
    required this.recommendations,
    this.onRecommendationTap,
    this.title = '基于你的习惯，为你推荐',
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (recommendations.isEmpty) {
      return const SizedBox.shrink();
    }

    final theme = Theme.of(context);

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: theme.colorScheme.primaryContainer,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.psychology,
                  size: 20,
                  color: theme.colorScheme.onPrimaryContainer,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.surfaceContainerHighest,
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.circular(16),
                      topRight: Radius.circular(16),
                      bottomLeft: Radius.circular(4),
                      bottomRight: Radius.circular(16),
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 12),
                      _buildRecommendationGrid(context, theme),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendationGrid(BuildContext context, ThemeData theme) {
    final columns = ResponsiveUtils.getRecommendationColumns(context);
    final maxItems = columns * 2; // 显示两行

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: columns,
        crossAxisSpacing: 8,
        mainAxisSpacing: 8,
        childAspectRatio: _getChildAspectRatio(context),
      ),
      itemCount: recommendations.take(maxItems).length,
      itemBuilder: (context, index) {
        final recommendation = recommendations[index];
        return _RecommendationCard(
          recommendation: recommendation,
          onTap: () => onRecommendationTap?.call(recommendation),
        );
      },
    );
  }

  double _getChildAspectRatio(BuildContext context) {
    final deviceType = ResponsiveUtils.getDeviceType(context);

    switch (deviceType) {
      case DeviceType.mobile:
        return 2.0; // 降低比例，增加卡片高度
      case DeviceType.tablet:
        return 2.2;
      case DeviceType.desktop:
        return 2.5;
    }
  }
}

/// 推荐卡片
class _RecommendationCard extends StatelessWidget {
  final AIRecommendation recommendation;
  final VoidCallback? onTap;

  const _RecommendationCard({
    required this.recommendation,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      margin: EdgeInsets.zero,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(6), // 减少内边距以增加内容空间
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(4),
                    decoration: BoxDecoration(
                      color: _getTypeColor(theme).withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Icon(
                      _getTypeIcon(),
                      size: 14,
                      color: _getTypeColor(theme),
                    ),
                  ),
                  const Spacer(),
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.secondaryContainer,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      '${(recommendation.confidence * 100).toInt()}%',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSecondaryContainer,
                        fontSize: 9,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min, // 防止Column溢出
                  children: [
                    Flexible(
                      child: Text(
                        recommendation.title,
                        style: theme.textTheme.bodySmall?.copyWith(
                          fontWeight: FontWeight.w500,
                        ),
                        maxLines: 2, // 增加标题行数
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Flexible(
                      child: Text(
                        recommendation.description,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                          fontSize: 10,
                        ),
                        maxLines: 2, // 增加描述行数
                        overflow: TextOverflow.ellipsis,
                      ),
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

  IconData _getTypeIcon() {
    switch (recommendation.type) {
      case RecommendationType.quickAccess:
        return Icons.flash_on;
      case RecommendationType.learningResource:
        return Icons.school;
      case RecommendationType.productivityTool:
        return Icons.build;
      case RecommendationType.recentItem:
        return Icons.history;
    }
  }

  Color _getTypeColor(ThemeData theme) {
    switch (recommendation.type) {
      case RecommendationType.quickAccess:
        return Colors.orange;
      case RecommendationType.learningResource:
        return Colors.blue;
      case RecommendationType.productivityTool:
        return Colors.green;
      case RecommendationType.recentItem:
        return Colors.purple;
    }
  }
}
