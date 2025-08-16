import 'package:flutter/material.dart';
import 'loading_state_wrapper.dart';

/// 通用空状态组件
class GenericEmptyState extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;
  final String? actionLabel;
  final VoidCallback? onAction;
  final Widget? illustration;
  final Color? iconColor;

  const GenericEmptyState({
    super.key,
    required this.icon,
    required this.title,
    required this.description,
    this.actionLabel,
    this.onAction,
    this.illustration,
    this.iconColor,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // 图标或插图
            if (illustration != null)
              illustration!
            else
              ScaleTransitionWrapper(
                beginScale: 0.5,
                child: Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    color: (iconColor ?? colorScheme.primary)
                        .withValues(alpha: 0.1),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    icon,
                    size: 40,
                    color: iconColor ?? colorScheme.primary,
                  ),
                ),
              ),

            const SizedBox(height: 24),

            // 标题
            FadeTransitionWrapper(
              child: Text(
                title,
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: colorScheme.onSurface,
                ),
                textAlign: TextAlign.center,
              ),
            ),

            const SizedBox(height: 12),

            // 描述
            FadeTransitionWrapper(
              child: Text(
                description,
                style: theme.textTheme.bodyLarge?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                ),
                textAlign: TextAlign.center,
                maxLines: 3,
              ),
            ),

            if (actionLabel != null && onAction != null) ...[
              const SizedBox(height: 32),
              SlideTransitionWrapper(
                beginOffset: const Offset(0, 0.2),
                child: FilledButton.icon(
                  onPressed: onAction,
                  icon: const Icon(Icons.add),
                  label: Text(actionLabel!),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// 无数据引导组件
class NoDataGuide extends StatelessWidget {
  final String dataType;
  final String? suggestion;
  final VoidCallback? onStartAction;

  const NoDataGuide({
    super.key,
    required this.dataType,
    this.suggestion,
    this.onStartAction,
  });

  @override
  Widget build(BuildContext context) {
    return GenericEmptyState(
      icon: Icons.storage_outlined,
      title: '暂无$dataType数据',
      description: suggestion ?? '开始使用连接器收集数据，让AI为你提供智能洞察',
      actionLabel: '开始收集数据',
      onAction: onStartAction,
      iconColor: Colors.blue,
    );
  }
}

/// 首次使用引导组件
class FirstTimeGuide extends StatelessWidget {
  final String feature;
  final List<String> steps;
  final VoidCallback? onGetStarted;

  const FirstTimeGuide({
    super.key,
    required this.feature,
    required this.steps,
    this.onGetStarted,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Center(
      child: Card(
        margin: const EdgeInsets.all(24),
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // 欢迎图标
              ScaleTransitionWrapper(
                child: Container(
                  width: 64,
                  height: 64,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        colorScheme.primary,
                        colorScheme.secondary,
                      ],
                    ),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.auto_awesome,
                    size: 32,
                    color: Colors.white,
                  ),
                ),
              ),

              const SizedBox(height: 24),

              // 标题
              FadeTransitionWrapper(
                child: Text(
                  '欢迎使用$feature',
                  style: theme.textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),

              const SizedBox(height: 16),

              // 步骤说明
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: steps.asMap().entries.map((entry) {
                  final index = entry.key;
                  final step = entry.value;

                  return SlideTransitionWrapper(
                    duration: Duration(milliseconds: 300 + (index * 100)),
                    beginOffset: const Offset(-0.1, 0),
                    child: Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: Row(
                        children: [
                          Container(
                            width: 24,
                            height: 24,
                            decoration: BoxDecoration(
                              color: colorScheme.primary,
                              shape: BoxShape.circle,
                            ),
                            child: Center(
                              child: Text(
                                '${index + 1}',
                                style: theme.textTheme.bodySmall?.copyWith(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Text(
                              step,
                              style: theme.textTheme.bodyLarge,
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ),

              if (onGetStarted != null) ...[
                const SizedBox(height: 32),
                SlideTransitionWrapper(
                  beginOffset: const Offset(0, 0.2),
                  child: FilledButton.icon(
                    onPressed: onGetStarted,
                    icon: const Icon(Icons.rocket_launch),
                    label: const Text('开始使用'),
                    style: FilledButton.styleFrom(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 24, vertical: 12),
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

/// AI洞察空状态
class AIInsightsEmptyState extends StatelessWidget {
  final VoidCallback? onRefresh;

  const AIInsightsEmptyState({super.key, this.onRefresh});

  @override
  Widget build(BuildContext context) {
    return FirstTimeGuide(
      feature: 'AI智能洞察',
      steps: const [
        '启动连接器开始收集数据',
        'AI会自动分析你的数据模式',
        '获得个性化的智能建议',
      ],
      onGetStarted: onRefresh,
    );
  }
}

/// 实体数据空状态
class EntitiesEmptyState extends StatelessWidget {
  final VoidCallback? onStartCollecting;

  const EntitiesEmptyState({super.key, this.onStartCollecting});

  @override
  Widget build(BuildContext context) {
    return NoDataGuide(
      dataType: '实体',
      suggestion: '启动连接器开始收集文件、链接、邮件等重要信息',
      onStartAction: onStartCollecting,
    );
  }
}

/// 时间线空状态
class TimelineEmptyState extends StatelessWidget {
  final VoidCallback? onStartActivity;

  const TimelineEmptyState({super.key, this.onStartActivity});

  @override
  Widget build(BuildContext context) {
    return NoDataGuide(
      dataType: '活动',
      suggestion: '开始使用Linch Mind，你的所有操作将自动记录在时间线中',
      onStartAction: onStartActivity,
    );
  }
}

/// 连接器空状态
class ConnectorsEmptyState extends StatelessWidget {
  final VoidCallback? onAddConnector;

  const ConnectorsEmptyState({super.key, this.onAddConnector});

  @override
  Widget build(BuildContext context) {
    return GenericEmptyState(
      icon: Icons.extension_outlined,
      title: '还没有安装连接器',
      description: '连接器帮助你从各种应用和服务中收集数据\n让AI为你提供更好的洞察',
      actionLabel: '浏览连接器',
      onAction: onAddConnector,
      iconColor: Colors.green,
    );
  }
}

/// 搜索无结果状态
class SearchEmptyState extends StatelessWidget {
  final String query;
  final VoidCallback? onClearSearch;

  const SearchEmptyState({
    super.key,
    required this.query,
    this.onClearSearch,
  });

  @override
  Widget build(BuildContext context) {
    return GenericEmptyState(
      icon: Icons.search_off,
      title: '没有找到相关结果',
      description: '试试其他关键词，或者清除搜索查看所有内容',
      actionLabel: '清除搜索',
      onAction: onClearSearch,
      iconColor: Colors.orange,
    );
  }
}

/// 网络错误状态
class NetworkErrorState extends StatelessWidget {
  final VoidCallback? onRetry;

  const NetworkErrorState({super.key, this.onRetry});

  @override
  Widget build(BuildContext context) {
    return GenericEmptyState(
      icon: Icons.wifi_off,
      title: '连接失败',
      description: '请检查网络连接或服务状态',
      actionLabel: '重试',
      onAction: onRetry,
      iconColor: Colors.red,
    );
  }
}

/// 权限错误状态
class PermissionErrorState extends StatelessWidget {
  final String permission;
  final VoidCallback? onGrantPermission;

  const PermissionErrorState({
    super.key,
    required this.permission,
    this.onGrantPermission,
  });

  @override
  Widget build(BuildContext context) {
    return GenericEmptyState(
      icon: Icons.lock_outlined,
      title: '需要$permission权限',
      description: '为了提供更好的服务，Linch Mind需要访问$permission',
      actionLabel: '授予权限',
      onAction: onGrantPermission,
      iconColor: Colors.amber,
    );
  }
}
