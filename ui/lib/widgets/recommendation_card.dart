import 'package:flutter/material.dart';
import '../models/api_models.dart';

class RecommendationCard extends StatelessWidget {
  final AIRecommendation recommendation;

  const RecommendationCard({
    super.key,
    required this.recommendation,
  });

  // 加载状态的构造函数
  RecommendationCard.loading({super.key}) : recommendation = AIRecommendation(
    id: '',
    title: '',
    description: '',
    confidence: 0.0,
    createdAt: DateTime.fromMillisecondsSinceEpoch(0),
  );

  @override
  Widget build(BuildContext context) {
    // 如果是加载状态，显示骨架屏
    if (recommendation.id.isEmpty) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 标题骨架
              Container(
                height: 20,
                width: double.infinity * 0.7,
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
              const SizedBox(height: 12),
              // 描述骨架
              Container(
                height: 16,
                width: double.infinity,
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
              const SizedBox(height: 8),
              Container(
                height: 16,
                width: double.infinity * 0.8,
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
              const SizedBox(height: 12),
              // 置信度骨架
              Container(
                height: 14,
                width: 80,
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
            ],
          ),
        ),
      );
    }

    final confidenceColor = _getConfidenceColor(context, recommendation.confidence);
    final confidenceIcon = _getConfidenceIcon(recommendation.confidence);

    return Card(
      elevation: 2,
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => _onRecommendationTap(context),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 标题行
              Row(
                children: [
                  Icon(
                    Icons.lightbulb,
                    color: Theme.of(context).colorScheme.primary,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      recommendation.title,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  // 置信度指示器
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: confidenceColor.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: confidenceColor.withValues(alpha: 0.3)),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          confidenceIcon,
                          size: 12,
                          color: confidenceColor,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          '${(recommendation.confidence * 100).toInt()}%',
                          style: Theme.of(context).textTheme.labelSmall?.copyWith(
                            color: confidenceColor,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // 描述
              Text(
                recommendation.description,
                style: Theme.of(context).textTheme.bodyMedium,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
              
              if (recommendation.relatedItems.isNotEmpty) ...[
                const SizedBox(height: 12),
                // 相关项目标签
                Wrap(
                  spacing: 6,
                  runSpacing: 6,
                  children: recommendation.relatedItems.take(3).map((item) {
                    return Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Theme.of(context).colorScheme.secondaryContainer,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        item,
                        style: Theme.of(context).textTheme.labelSmall?.copyWith(
                          color: Theme.of(context).colorScheme.onSecondaryContainer,
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ],

              const SizedBox(height: 12),
              
              // 底部信息行
              Row(
                children: [
                  Icon(
                    Icons.schedule,
                    size: 14,
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    _formatTimeAgo(recommendation.createdAt),
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                  ),
                  const Spacer(),
                  // 操作按钮
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.share, size: 18),
                        onPressed: () => _shareRecommendation(context),
                        tooltip: 'Share',
                        visualDensity: VisualDensity.compact,
                      ),
                      IconButton(
                        icon: const Icon(Icons.bookmark_border, size: 18),
                        onPressed: () => _bookmarkRecommendation(context),
                        tooltip: 'Bookmark',
                        visualDensity: VisualDensity.compact,
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Color _getConfidenceColor(BuildContext context, double confidence) {
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
      return Icons.trending_up;
    } else if (confidence >= 0.6) {
      return Icons.trending_flat;
    } else {
      return Icons.trending_down;
    }
  }

  String _formatTimeAgo(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);
    
    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}h ago';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}d ago';
    } else {
      return '${dateTime.day}/${dateTime.month}/${dateTime.year}';
    }
  }

  void _onRecommendationTap(BuildContext context) {
    // 显示推荐详情对话框
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(recommendation.title),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(recommendation.description),
              if (recommendation.relatedItems.isNotEmpty) ...[
                const SizedBox(height: 16),
                Text(
                  'Related Items:',
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                const SizedBox(height: 8),
                ...recommendation.relatedItems.map((item) => Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Text('• $item'),
                )),
              ],
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
          FilledButton(
            onPressed: () {
              Navigator.of(context).pop();
              // TODO: 实现"应用推荐"功能
            },
            child: const Text('Apply'),
          ),
        ],
      ),
    );
  }

  void _shareRecommendation(BuildContext context) {
    // TODO: 实现分享功能
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Share functionality coming soon')),
    );
  }

  void _bookmarkRecommendation(BuildContext context) {
    // TODO: 实现书签功能
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Recommendation bookmarked')),
    );
  }
}