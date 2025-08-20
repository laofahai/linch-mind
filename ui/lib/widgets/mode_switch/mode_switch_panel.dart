import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/mode_switch_provider.dart';
import 'mode_transition_animator.dart';

/// 模式切换面板
class ModeSwitchPanel extends ConsumerWidget {
  const ModeSwitchPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final modeSwitchState = ref.watch(modeSwitchProvider);
    final theme = Theme.of(context);

    return ModeTransitionAnimator(
      currentMode: modeSwitchState.currentMode,
      isTransitioning: modeSwitchState.isTransitioning,
      child: Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 面板标题
            _buildPanelHeader(context, theme),
            const SizedBox(height: 20),

            // 当前模式状态
            _buildCurrentModeStatus(context, theme, modeSwitchState),
            const SizedBox(height: 16),

            // 切换进度指示器
            ModeTransitionProgress(
              isTransitioning: modeSwitchState.isTransitioning,
              currentMode: modeSwitchState.currentMode,
            ),
            const SizedBox(height: 8),

            // 模式选择网格
            _buildModeGrid(context, theme, ref, modeSwitchState),
            const SizedBox(height: 24),

            // 快捷操作
            _buildQuickActions(context, theme, ref, modeSwitchState),
            const SizedBox(height: 24),

            // 模式统计
            _buildModeStats(context, theme, modeSwitchState),

            const Spacer(),

            // 智能建议
            _buildSmartSuggestions(context, theme, ref, modeSwitchState),
          ],
        ),
      ),
    );
  }

  Widget _buildPanelHeader(BuildContext context, ThemeData theme) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: theme.colorScheme.primaryContainer,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            Icons.tune,
            size: 20,
            color: theme.colorScheme.onPrimaryContainer,
          ),
        ),
        const SizedBox(width: 12),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '模式切换',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            Text(
              '智能适配',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
        const Spacer(),
        IconButton(
          onPressed: () {},
          icon: const Icon(Icons.more_vert, size: 18),
          tooltip: '更多选项',
        ),
      ],
    );
  }

  Widget _buildCurrentModeStatus(
    BuildContext context,
    ThemeData theme,
    ModeSwitchState state,
  ) {
    final currentMode = state.currentMode;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            currentMode.color.withValues(alpha: 0.1),
            currentMode.color.withValues(alpha: 0.05),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: currentMode.color.withValues(alpha: 0.2),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                currentMode.icon,
                color: currentMode.color,
                size: 24,
              ),
              const SizedBox(width: 12),
              Text(
                currentMode.statusText,
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: currentMode.color,
                ),
              ),
              const Spacer(),
              if (state.isTransitioning)
                SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation(currentMode.color),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            currentMode.description,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
              height: 1.4,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildModeGrid(
    BuildContext context,
    ThemeData theme,
    WidgetRef ref,
    ModeSwitchState state,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '选择模式',
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.w600,
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 12),
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 1.8,
          children: AppMode.values.map((mode) {
            final isSelected = mode == state.currentMode;
            final isDisabled = state.isTransitioning;

            return Material(
              color: Colors.transparent,
              child: InkWell(
                onTap: isDisabled
                    ? null
                    : () {
                        ref
                            .read(modeSwitchProvider.notifier)
                            .switchToMode(mode);
                      },
                borderRadius: BorderRadius.circular(8),
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: isSelected
                        ? mode.color.withValues(alpha: 0.1)
                        : theme.colorScheme.surfaceContainerHighest
                            .withValues(alpha: 0.3),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: isSelected
                          ? mode.color.withValues(alpha: 0.3)
                          : theme.colorScheme.outline.withValues(alpha: 0.2),
                      width: isSelected ? 1.5 : 1,
                    ),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      ModeIconAnimator(
                        mode: mode,
                        isSelected: isSelected,
                        isTransitioning: isDisabled,
                      ),
                      const SizedBox(height: 6),
                      Text(
                        mode.displayName,
                        style: theme.textTheme.bodySmall?.copyWith(
                          fontWeight:
                              isSelected ? FontWeight.w600 : FontWeight.w500,
                          color: isSelected
                              ? mode.color
                              : theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildQuickActions(
    BuildContext context,
    ThemeData theme,
    WidgetRef ref,
    ModeSwitchState state,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '快捷操作',
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.w600,
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            _buildActionChip(
              context,
              theme,
              icon: Icons.schedule,
              label: '自动切换',
              onTap: () {
                ref.read(modeSwitchProvider.notifier).autoSwitchMode();
              },
            ),
            _buildActionChip(
              context,
              theme,
              icon: Icons.settings,
              label: '模式设置',
              onTap: () {
                // TODO: 打开模式设置页面
              },
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildActionChip(
    BuildContext context,
    ThemeData theme, {
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: theme.colorScheme.surfaceContainerHighest
                .withValues(alpha: 0.5),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: theme.colorScheme.outline.withValues(alpha: 0.2),
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                icon,
                size: 14,
                color: theme.colorScheme.onSurfaceVariant,
              ),
              const SizedBox(width: 6),
              Text(
                label,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildModeStats(
    BuildContext context,
    ThemeData theme,
    ModeSwitchState state,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '今日使用',
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.w600,
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: theme.colorScheme.surfaceContainerHighest
                .withValues(alpha: 0.3),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            children: [
              Icon(
                Icons.timer_outlined,
                size: 16,
                color: theme.colorScheme.onSurfaceVariant,
              ),
              const SizedBox(width: 8),
              Text(
                '${state.currentMode.displayName}模式: 2小时15分钟',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildSmartSuggestions(
    BuildContext context,
    ThemeData theme,
    WidgetRef ref,
    ModeSwitchState state,
  ) {
    final recommendedMode =
        ref.read(modeSwitchProvider.notifier).getRecommendedNextMode();

    if (recommendedMode == null) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: recommendedMode.color.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: recommendedMode.color.withValues(alpha: 0.2),
        ),
      ),
      child: Row(
        children: [
          Icon(
            Icons.lightbulb_outline,
            size: 16,
            color: recommendedMode.color,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              '建议切换到${recommendedMode.displayName}模式',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ),
          TextButton(
            onPressed: () {
              ref
                  .read(modeSwitchProvider.notifier)
                  .switchToMode(recommendedMode);
            },
            child: Text(
              '切换',
              style: TextStyle(
                color: recommendedMode.color,
                fontSize: 12,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
