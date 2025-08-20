import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// AI智能洞察面板 - 多时间维度
class AIInsightsPanel extends ConsumerWidget {
  final Function(String prompt)? onPromptTap;

  const AIInsightsPanel({
    super.key,
    this.onPromptTap,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 面板标题
          Row(
            children: [
              Icon(
                Icons.psychology,
                size: 20,
                color: theme.colorScheme.primary,
              ),
              const SizedBox(width: 8),
              Text(
                'AI智能洞察',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const Spacer(),
              IconButton(
                onPressed: () {},
                icon: const Icon(Icons.unfold_less, size: 16),
                tooltip: '折叠面板',
              ),
            ],
          ),
          const SizedBox(height: 16),

          // 滚动内容区域
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 实时观察
                  _buildInsightSection(
                    context,
                    title: '⏱️ 实时观察',
                    items: [
                      _InsightItem(
                        title: '正在编辑 home_screen.dart',
                        description: '检测到布局相关代码修改',
                        time: '刚刚',
                        prompt: '帮我分析当前编辑的布局文件',
                        isActive: true,
                      ),
                      _InsightItem(
                        title: '剪贴板更新3次',
                        description: '包含错误信息和代码片段',
                        time: '2分钟前',
                        prompt: '基于我的剪贴板历史分析问题',
                      ),
                    ],
                  ),

                  const SizedBox(height: 20),

                  // 今日模式
                  _buildInsightSection(
                    context,
                    title: '📅 今日模式',
                    items: [
                      _InsightItem(
                        title: '主要处理UI优化问题',
                        description: '编辑了5个Flutter组件文件',
                        time: '今天',
                        prompt: '总结我今天的UI优化工作',
                        confidence: 0.92,
                      ),
                      _InsightItem(
                        title: '搜索了7次Flutter布局',
                        description: '专注学习响应式设计',
                        time: '今天',
                        prompt: '基于今天的搜索帮我制定学习计划',
                        confidence: 0.87,
                      ),
                      _InsightItem(
                        title: '工作专注度较高',
                        description: '连续编码3.5小时，休息2次',
                        time: '今天',
                        prompt: '分析我今天的工作节奏',
                        confidence: 0.78,
                      ),
                    ],
                  ),

                  const SizedBox(height: 20),

                  // 趋势发现
                  _buildInsightSection(
                    context,
                    title: '📈 趋势发现',
                    items: [
                      _InsightItem(
                        title: 'Flutter技能持续提升',
                        description: '本周解决复杂布局问题增加40%',
                        time: '本周',
                        prompt: '评估我的Flutter技能成长轨迹',
                        confidence: 0.85,
                        isImportant: true,
                      ),
                      _InsightItem(
                        title: '工作效率稳步上升',
                        description: '平均每日完成任务数提升15%',
                        time: '近期',
                        prompt: '分析我的工作效率提升原因',
                        confidence: 0.73,
                      ),
                    ],
                  ),

                  const SizedBox(height: 20),

                  // 预测建议
                  _buildInsightSection(
                    context,
                    title: '🔮 智能预测',
                    items: [
                      _InsightItem(
                        title: '建议重构组件架构',
                        description: '基于代码复杂度分析',
                        time: '建议',
                        prompt: '帮我制定组件架构重构方案',
                        confidence: 0.68,
                        isImportant: true,
                      ),
                      _InsightItem(
                        title: '可能需要学习状态管理',
                        description: '根据项目发展趋势预测',
                        time: '建议',
                        prompt: '为我推荐适合的状态管理方案',
                        confidence: 0.71,
                      ),
                    ],
                  ),

                  const SizedBox(height: 80),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInsightSection(
    BuildContext context, {
    required String title,
    required List<_InsightItem> items,
  }) {
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.w600,
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 8),
        ...items.map((item) => _buildInsightCard(context, item)),
      ],
    );
  }

  Widget _buildInsightCard(BuildContext context, _InsightItem item) {
    final theme = Theme.of(context);

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () => onPromptTap?.call(item.prompt),
          borderRadius: BorderRadius.circular(8),
          child: Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: item.isActive
                  ? theme.colorScheme.primaryContainer.withValues(alpha: 0.5)
                  : theme.colorScheme.surfaceContainerHighest
                      .withValues(alpha: 0.3),
              borderRadius: BorderRadius.circular(8),
              border: item.isImportant
                  ? Border.all(
                      color: theme.colorScheme.primary.withValues(alpha: 0.3))
                  : null,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        item.title,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.w500,
                          color: item.isActive
                              ? theme.colorScheme.onPrimaryContainer
                              : null,
                        ),
                      ),
                    ),
                    if (item.confidence != null) ...[
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 6,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: _getConfidenceColor(theme, item.confidence!),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          '${(item.confidence! * 100).toInt()}%',
                          style: theme.textTheme.bodySmall?.copyWith(
                            fontSize: 10,
                            color: Colors.white,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  item.description,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    Text(
                      item.time,
                      style: theme.textTheme.bodySmall?.copyWith(
                        fontSize: 11,
                        color: theme.colorScheme.onSurfaceVariant
                            .withValues(alpha: 0.7),
                      ),
                    ),
                    const Spacer(),
                    Icon(
                      Icons.arrow_forward_ios,
                      size: 12,
                      color: theme.colorScheme.onSurfaceVariant
                          .withValues(alpha: 0.5),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Color _getConfidenceColor(ThemeData theme, double confidence) {
    if (confidence >= 0.8) return Colors.green;
    if (confidence >= 0.6) return Colors.orange;
    return Colors.grey;
  }
}

/// 洞察项目数据模型（临时）
class _InsightItem {
  final String title;
  final String description;
  final String time;
  final String prompt;
  final double? confidence;
  final bool isActive;
  final bool isImportant;

  const _InsightItem({
    required this.title,
    required this.description,
    required this.time,
    required this.prompt,
    this.confidence,
    this.isActive = false,
    this.isImportant = false,
  });
}
