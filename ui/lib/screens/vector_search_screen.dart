// 向量搜索界面 - 简化版本
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../widgets/vector_search/smart_search_widget.dart';
import '../widgets/vector_search/search_results_widget.dart';
import '../utils/app_logger.dart';

class VectorSearchScreen extends ConsumerWidget {
  const VectorSearchScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    
    AppLogger.info('向量搜索页面访问', module: 'VectorSearchScreen');

    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 页面标题
            _buildHeader(theme),
            const SizedBox(height: 24),
            
            // 搜索框
            SmartSearchWidget(
              onSearchSubmitted: (query) {
                AppLogger.info('搜索查询: $query', module: 'VectorSearchScreen');
              },
            ),
            const SizedBox(height: 24),

            // 搜索结果区域
            Expanded(
              child: SearchResultsWidget(
                onResultTap: (result) {
                  AppLogger.info('搜索结果点击: ${result.entityId}', module: 'VectorSearchScreen');
                },
                onSimilarityTap: (entityId) {
                  AppLogger.info('相似性搜索: $entityId', module: 'VectorSearchScreen');
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(ThemeData theme) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: theme.colorScheme.primaryContainer,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(
            Icons.search_outlined,
            color: theme.colorScheme.onPrimaryContainer,
            size: 24,
          ),
        ),
        const SizedBox(width: 16),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '智能语义搜索',
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w600,
                color: theme.colorScheme.onSurface,
              ),
            ),
            Text(
              '基于向量搜索的语义匹配',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      ],
    );
  }
}