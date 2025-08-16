// 响应式仪表板布局组件
import 'package:flutter/material.dart';

/// 响应式仪表板布局
class ResponsiveDashboardLayout extends StatelessWidget {
  final Widget header;
  final Widget statsOverview;
  final Widget mainContent;
  final Widget? sidebar;
  final Widget? bottomContent;
  final EdgeInsets? padding;
  final double? maxWidth;

  const ResponsiveDashboardLayout({
    super.key,
    required this.header,
    required this.statsOverview,
    required this.mainContent,
    this.sidebar,
    this.bottomContent,
    this.padding,
    this.maxWidth,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints:
          maxWidth != null ? BoxConstraints(maxWidth: maxWidth!) : null,
      padding: padding ?? _getDefaultPadding(context),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final screenWidth = constraints.maxWidth;
          final isDesktop = screenWidth >= 1200;
          final isTablet = screenWidth >= 768 && screenWidth < 1200;
          final isMobile = screenWidth < 768;

          final availableHeight = constraints.maxHeight.isFinite
              ? constraints.maxHeight
              : MediaQuery.of(context).size.height;

          return SingleChildScrollView(
            child: ConstrainedBox(
              constraints: BoxConstraints(
                minHeight: availableHeight,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 头部区域
                  header,
                  const SizedBox(height: 16), // 减少间距

                  // 统计概览
                  statsOverview,
                  const SizedBox(height: 20), // 减少间距

                  // 主要内容区域 - 修复布局约束
                  ConstrainedBox(
                    constraints: BoxConstraints(
                      minHeight: 250,
                      maxHeight: (availableHeight * 0.6).clamp(250.0, 600.0),
                    ),
                    child: _buildContentArea(
                        context, isDesktop, isTablet, isMobile),
                  ),

                  // 底部内容（可选）
                  if (bottomContent != null) ...[
                    const SizedBox(height: 16),
                    bottomContent!,
                  ],
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildContentArea(
    BuildContext context,
    bool isDesktop,
    bool isTablet,
    bool isMobile,
  ) {
    if (isDesktop && sidebar != null) {
      // 桌面端：主内容 + 侧边栏
      return Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            flex: 7,
            child: mainContent,
          ),
          const SizedBox(width: 24),
          Expanded(
            flex: 3,
            child: sidebar!,
          ),
        ],
      );
    } else if (isTablet && sidebar != null) {
      // 平板端：主内容在上，侧边栏在下 - 修复布局约束
      return Column(
        children: [
          Flexible(
            flex: 2,
            child: Container(
              constraints: const BoxConstraints(minHeight: 200),
              child: mainContent,
            ),
          ),
          const SizedBox(height: 24),
          Flexible(
            flex: 1,
            child: Container(
              constraints: const BoxConstraints(minHeight: 100),
              child: sidebar!,
            ),
          ),
        ],
      );
    } else {
      // 移动端或无侧边栏：仅主内容
      return mainContent;
    }
  }

  EdgeInsets _getDefaultPadding(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;

    if (screenWidth >= 1200) {
      return const EdgeInsets.all(32);
    } else if (screenWidth >= 768) {
      return const EdgeInsets.all(24);
    } else {
      return const EdgeInsets.all(16);
    }
  }
}

/// 网格布局组件 - 优化版本，解决viewport约束问题
class ResponsiveGrid extends StatelessWidget {
  final List<Widget> children;
  final double spacing;
  final double runSpacing;
  final int? maxCrossAxisCount;
  final double? childAspectRatio;
  final double? maxCrossAxisExtent;
  final EdgeInsets? padding; // 新增padding支持

  const ResponsiveGrid({
    super.key,
    required this.children,
    this.spacing = 16,
    this.runSpacing = 16,
    this.maxCrossAxisCount,
    this.childAspectRatio,
    this.maxCrossAxisExtent,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;

    // 根据屏幕宽度自动调整列数
    int crossAxisCount;
    if (maxCrossAxisCount != null) {
      crossAxisCount = maxCrossAxisCount!;
    } else {
      if (screenWidth >= 1200) {
        crossAxisCount = 4;
      } else if (screenWidth >= 768) {
        crossAxisCount = 3;
      } else if (screenWidth >= 480) {
        crossAxisCount = 2;
      } else {
        crossAxisCount = 1;
      }
    }

    // 确保不超过子组件数量
    crossAxisCount = crossAxisCount.clamp(1, children.length);

    // 使用Wrap替代GridView来解决viewport内在尺寸问题
    if (children.isEmpty) {
      return const SizedBox.shrink();
    }

    // 计算每个子项的期望宽度
    final availableWidth = screenWidth - (padding?.horizontal ?? 32);

    double itemWidth;
    if (maxCrossAxisExtent != null) {
      itemWidth = maxCrossAxisExtent!;
    } else {
      itemWidth = (availableWidth / crossAxisCount) - spacing;
    }

    final itemHeight = itemWidth / (childAspectRatio ?? 1.0);

    return Wrap(
      spacing: spacing,
      runSpacing: runSpacing,
      alignment: WrapAlignment.start,
      children: children
          .map((child) => SizedBox(
                width: itemWidth.clamp(200.0, maxCrossAxisExtent ?? 400.0),
                height: itemHeight.clamp(60.0, 150.0), // 限制高度范围
                child: child,
              ))
          .toList(),
    );
  }
}

/// 可折叠的卡片容器
class CollapsibleCard extends StatefulWidget {
  final String title;
  final Widget child;
  final String? subtitle;
  final Widget? trailing;
  final bool initiallyExpanded;
  final Color? backgroundColor;
  final EdgeInsets? padding;

  const CollapsibleCard({
    super.key,
    required this.title,
    required this.child,
    this.subtitle,
    this.trailing,
    this.initiallyExpanded = true,
    this.backgroundColor,
    this.padding,
  });

  @override
  State<CollapsibleCard> createState() => _CollapsibleCardState();
}

class _CollapsibleCardState extends State<CollapsibleCard>
    with SingleTickerProviderStateMixin {
  late bool _isExpanded;
  late AnimationController _animationController;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _isExpanded = widget.initiallyExpanded;
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _animation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    );

    if (_isExpanded) {
      _animationController.value = 1.0;
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _toggle() {
    setState(() {
      _isExpanded = !_isExpanded;
      if (_isExpanded) {
        _animationController.forward();
      } else {
        _animationController.reverse();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      color: widget.backgroundColor,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          InkWell(
            onTap: _toggle,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          widget.title,
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        if (widget.subtitle != null) ...[
                          const SizedBox(height: 4),
                          Text(
                            widget.subtitle!,
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: theme.colorScheme.onSurfaceVariant,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                  if (widget.trailing != null) ...[
                    const SizedBox(width: 8),
                    widget.trailing!,
                  ],
                  const SizedBox(width: 8),
                  AnimatedRotation(
                    turns: _isExpanded ? 0.5 : 0,
                    duration: const Duration(milliseconds: 300),
                    child: Icon(
                      Icons.expand_more,
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ),
          ),
          SizeTransition(
            sizeFactor: _animation,
            child: LayoutBuilder(
              builder: (context, constraints) {
                return Container(
                  constraints: BoxConstraints(
                    maxHeight: constraints.maxHeight.isFinite
                        ? constraints.maxHeight.clamp(0.0, double.infinity)
                        : 400.0,
                  ),
                  child: SingleChildScrollView(
                    child: Padding(
                      padding: widget.padding ??
                          const EdgeInsets.fromLTRB(16, 0, 16, 16),
                      child: widget.child,
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

/// 快速操作按钮组
class QuickActionGroup extends StatelessWidget {
  final List<QuickAction> actions;
  final Axis direction;
  final double spacing;

  const QuickActionGroup({
    super.key,
    required this.actions,
    this.direction = Axis.horizontal,
    this.spacing = 8,
  });

  @override
  Widget build(BuildContext context) {
    if (direction == Axis.horizontal) {
      return Wrap(
        spacing: spacing,
        runSpacing: spacing,
        children: actions
            .map((action) => _buildActionButton(context, action))
            .toList(),
      );
    } else {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: actions
            .map((action) => Padding(
                  padding: EdgeInsets.only(bottom: spacing),
                  child: _buildActionButton(context, action),
                ))
            .toList(),
      );
    }
  }

  Widget _buildActionButton(BuildContext context, QuickAction action) {
    return OutlinedButton.icon(
      onPressed: action.onPressed,
      icon: Icon(action.icon, size: 16),
      label: Text(action.label),
      style: OutlinedButton.styleFrom(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      ),
    );
  }
}

/// 快速操作定义
class QuickAction {
  final String label;
  final IconData icon;
  final VoidCallback onPressed;

  const QuickAction({
    required this.label,
    required this.icon,
    required this.onPressed,
  });
}
