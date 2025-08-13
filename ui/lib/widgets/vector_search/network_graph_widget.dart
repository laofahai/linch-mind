// NetworkX知识图谱可视化组件 - 简化核心版本
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/data_insights_models.dart';
import '../../providers/vector_search_provider.dart';

/// 简化的知识图谱可视化组件
class NetworkGraphWidget extends ConsumerStatefulWidget {
  final String? entityId;
  final Function(String)? onNodeTap;

  const NetworkGraphWidget({
    super.key,
    this.entityId,
    this.onNodeTap,
  });

  @override
  ConsumerState<NetworkGraphWidget> createState() => _NetworkGraphWidgetState();
}

class _NetworkGraphWidgetState extends ConsumerState<NetworkGraphWidget> {
  @override
  void initState() {
    super.initState();
    if (widget.entityId != null) {
      _loadSimilarities();
    }
  }

  void _loadSimilarities() {
    ref.read(similarityAnalysisProvider.notifier)
        .calculateSimilarity(widget.entityId!);
  }

  @override
  Widget build(BuildContext context) {
    final similarityState = ref.watch(similarityAnalysisProvider);
    final theme = Theme.of(context);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 标题栏
            Row(
              children: [
                Icon(Icons.account_tree, color: theme.primaryColor),
                const SizedBox(width: 8),
                Text(
                  '知识图谱',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                if (widget.entityId != null)
                  IconButton(
                    icon: const Icon(Icons.refresh),
                    onPressed: _loadSimilarities,
                    tooltip: '刷新',
                  ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // 图谱内容
            Expanded(
              child: _buildGraphContent(similarityState, theme),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGraphContent(SimilarityState state, ThemeData theme) {
    if (state.isLoading) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const CircularProgressIndicator(),
            const SizedBox(height: 16),
            Text(
              '正在构建知识图谱...',
              style: TextStyle(color: theme.hintColor),
            ),
          ],
        ),
      );
    }

    if (state.error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 48, color: theme.colorScheme.error),
            const SizedBox(height: 16),
            Text('图谱加载失败', style: TextStyle(color: theme.colorScheme.error)),
            const SizedBox(height: 8),
            Text(state.error!, style: TextStyle(color: theme.hintColor)),
          ],
        ),
      );
    }

    if (state.similarities.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.hub, size: 48, color: theme.hintColor),
            const SizedBox(height: 16),
            Text(
              widget.entityId != null ? '未找到相关联的实体' : '选择一个实体查看关联',
              style: TextStyle(color: theme.hintColor),
            ),
          ],
        ),
      );
    }

    // 简化的关系列表显示
    return ListView.builder(
      itemCount: state.similarities.length,
      itemBuilder: (context, index) {
        final similarity = state.similarities[index];
        return _buildRelationshipItem(similarity, theme);
      },
    );
  }

  Widget _buildRelationshipItem(SimilarityResult similarity, ThemeData theme) {
    final percentage = (similarity.similarity * 100).round();
    
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: _getSimilarityColor(similarity.similarity).withValues(alpha: 0.1),
            shape: BoxShape.circle,
          ),
          child: Icon(
            Icons.link,
            color: _getSimilarityColor(similarity.similarity),
            size: 20,
          ),
        ),
        title: Text(
          similarity.targetContent ?? similarity.targetId,
          style: theme.textTheme.bodyMedium,
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Text(
          '相似度: $percentage%',
          style: theme.textTheme.bodySmall,
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: _getSimilarityColor(similarity.similarity).withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            '$percentage%',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: _getSimilarityColor(similarity.similarity),
            ),
          ),
        ),
        onTap: () => widget.onNodeTap?.call(similarity.targetId),
      ),
    );
  }

  Color _getSimilarityColor(double similarity) {
    final percentage = (similarity * 100).round();
    if (percentage >= 80) {
      return Colors.green;
    } else if (percentage >= 60) {
      return Colors.orange;
    } else {
      return Colors.red;
    }
  }
}