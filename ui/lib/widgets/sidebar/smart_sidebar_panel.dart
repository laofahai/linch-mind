import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../mode_switch/mode_switch_panel.dart';
import '../ai_insights/ai_insights_panel.dart';

/// 智能侧边栏面板类型
enum SidebarPanelType {
  modeSwitch('模式切换', Icons.tune),
  aiInsights('AI洞察', Icons.psychology),
  systemStatus('系统状态', Icons.monitor_heart),
  shortcuts('快捷操作', Icons.flash_on);

  const SidebarPanelType(this.title, this.icon);
  final String title;
  final IconData icon;
}

/// 当前选中的侧边栏面板
final selectedSidebarPanelProvider = StateProvider<SidebarPanelType>(
  (ref) => SidebarPanelType.modeSwitch,
);

/// 智能侧边栏面板 - 多功能集成
class SmartSidebarPanel extends ConsumerWidget {
  final Function(String prompt)? onPromptTap;

  const SmartSidebarPanel({
    super.key,
    this.onPromptTap,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedPanel = ref.watch(selectedSidebarPanelProvider);
    final theme = Theme.of(context);

    return Container(
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        border: Border(
          left: BorderSide(
            color: theme.colorScheme.outline.withValues(alpha: 0.2),
          ),
        ),
      ),
      child: Column(
        children: [
          // 顶部导航标签
          _buildTabNavigation(context, theme, ref, selectedPanel),

          // 内容区域
          Expanded(
            child: _buildPanelContent(context, ref, selectedPanel),
          ),
        ],
      ),
    );
  }

  Widget _buildTabNavigation(
    BuildContext context,
    ThemeData theme,
    WidgetRef ref,
    SidebarPanelType selectedPanel,
  ) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 12),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
        border: Border(
          bottom: BorderSide(
            color: theme.colorScheme.outline.withValues(alpha: 0.2),
          ),
        ),
      ),
      child: Row(
        children: SidebarPanelType.values.map((panelType) {
          final isSelected = panelType == selectedPanel;

          return Expanded(
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                onTap: () {
                  ref.read(selectedSidebarPanelProvider.notifier).state =
                      panelType;
                },
                borderRadius: BorderRadius.circular(6),
                child: Container(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  decoration: BoxDecoration(
                    color: isSelected
                        ? theme.colorScheme.primaryContainer
                            .withValues(alpha: 0.5)
                        : Colors.transparent,
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        panelType.icon,
                        size: 18,
                        color: isSelected
                            ? theme.colorScheme.onPrimaryContainer
                            : theme.colorScheme.onSurfaceVariant,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        panelType.title,
                        style: theme.textTheme.bodySmall?.copyWith(
                          fontSize: 10,
                          fontWeight:
                              isSelected ? FontWeight.w600 : FontWeight.w400,
                          color: isSelected
                              ? theme.colorScheme.onPrimaryContainer
                              : theme.colorScheme.onSurfaceVariant,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildPanelContent(
    BuildContext context,
    WidgetRef ref,
    SidebarPanelType selectedPanel,
  ) {
    switch (selectedPanel) {
      case SidebarPanelType.modeSwitch:
        return const ModeSwitchPanel();

      case SidebarPanelType.aiInsights:
        return AIInsightsPanel(onPromptTap: onPromptTap);

      case SidebarPanelType.systemStatus:
        return _SystemStatusPanel();

      case SidebarPanelType.shortcuts:
        return _ShortcutsPanel();
    }
  }
}

/// 系统状态面板
class _SystemStatusPanel extends ConsumerWidget {
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
                Icons.monitor_heart,
                size: 20,
                color: theme.colorScheme.primary,
              ),
              const SizedBox(width: 8),
              Text(
                '系统状态',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),

          // 服务状态
          _buildStatusSection(
            context,
            title: '核心服务',
            items: [
              _StatusItem('IPC 守护进程', true, '正常运行'),
              _StatusItem('AI 聊天服务', true, '连接正常'),
              _StatusItem('数据同步', true, '实时同步'),
            ],
          ),

          const SizedBox(height: 16),

          // 连接器状态
          _buildStatusSection(
            context,
            title: '连接器',
            items: [
              _StatusItem('文件系统', true, '3个文件夹监控中'),
              _StatusItem('剪贴板', true, '已捕获12次'),
              _StatusItem('浏览器', false, '未连接'),
            ],
          ),

          const SizedBox(height: 16),

          // 性能指标
          _buildPerformanceMetrics(context, theme),
        ],
      ),
    );
  }

  Widget _buildStatusSection(
    BuildContext context, {
    required String title,
    required List<_StatusItem> items,
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
        ...items.map((item) => _buildStatusItem(context, item)),
      ],
    );
  }

  Widget _buildStatusItem(BuildContext context, _StatusItem item) {
    final theme = Theme.of(context);

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: item.isOnline ? Colors.green : Colors.orange,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.name,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w500,
                  ),
                ),
                Text(
                  item.status,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPerformanceMetrics(BuildContext context, ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '性能指标',
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.w600,
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: theme.colorScheme.surfaceContainerHighest
                .withValues(alpha: 0.3),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            children: [
              _buildMetricRow(context, '内存使用', '245 MB', 0.6),
              const SizedBox(height: 8),
              _buildMetricRow(context, 'CPU 使用', '12%', 0.12),
              const SizedBox(height: 8),
              _buildMetricRow(context, 'IPC 延迟', '< 1ms', 0.1),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMetricRow(
    BuildContext context,
    String label,
    String value,
    double progress,
  ) {
    final theme = Theme.of(context);

    return Row(
      children: [
        Expanded(
          child: Text(
            label,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
        ),
        Text(
          value,
          style: theme.textTheme.bodySmall?.copyWith(
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }
}

/// 快捷操作面板
class _ShortcutsPanel extends ConsumerWidget {
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
                Icons.flash_on,
                size: 20,
                color: theme.colorScheme.primary,
              ),
              const SizedBox(width: 8),
              Text(
                '快捷操作',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),

          // 快捷按钮网格
          GridView.count(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisCount: 2,
            mainAxisSpacing: 12,
            crossAxisSpacing: 12,
            childAspectRatio: 1.2,
            children: [
              _buildShortcutButton(
                context,
                icon: Icons.refresh,
                label: '刷新数据',
                onTap: () {},
              ),
              _buildShortcutButton(
                context,
                icon: Icons.cleaning_services,
                label: '清理缓存',
                onTap: () {},
              ),
              _buildShortcutButton(
                context,
                icon: Icons.backup,
                label: '数据备份',
                onTap: () {},
              ),
              _buildShortcutButton(
                context,
                icon: Icons.settings,
                label: '系统设置',
                onTap: () {},
              ),
            ],
          ),

          const SizedBox(height: 20),

          // 最近操作
          _buildRecentActions(context, theme),
        ],
      ),
    );
  }

  Widget _buildShortcutButton(
    BuildContext context, {
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    final theme = Theme.of(context);

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: theme.colorScheme.surfaceContainerHighest
                .withValues(alpha: 0.3),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: theme.colorScheme.outline.withValues(alpha: 0.2),
            ),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                size: 24,
                color: theme.colorScheme.onSurfaceVariant,
              ),
              const SizedBox(height: 8),
              Text(
                label,
                style: theme.textTheme.bodySmall?.copyWith(
                  fontWeight: FontWeight.w500,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRecentActions(BuildContext context, ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '最近操作',
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.w600,
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: theme.colorScheme.surfaceContainerHighest
                .withValues(alpha: 0.3),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            children: [
              _buildActionItem(context, '切换到专注模式', '2分钟前'),
              const Divider(height: 16),
              _buildActionItem(context, '清理系统缓存', '15分钟前'),
              const Divider(height: 16),
              _buildActionItem(context, '备份用户数据', '1小时前'),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildActionItem(BuildContext context, String action, String time) {
    final theme = Theme.of(context);

    return Row(
      children: [
        Expanded(
          child: Text(
            action,
            style: theme.textTheme.bodySmall?.copyWith(
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
        Text(
          time,
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
            fontSize: 11,
          ),
        ),
      ],
    );
  }
}

/// 状态项数据模型
class _StatusItem {
  final String name;
  final bool isOnline;
  final String status;

  const _StatusItem(this.name, this.isOnline, this.status);
}
