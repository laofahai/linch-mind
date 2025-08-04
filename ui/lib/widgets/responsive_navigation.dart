import 'package:flutter/material.dart';

class ResponsiveNavigation extends StatelessWidget {
  final int currentIndex;
  final Function(int) onDestinationSelected;
  final bool isDesktop;

  const ResponsiveNavigation({
    super.key,
    required this.currentIndex,
    required this.onDestinationSelected,
    required this.isDesktop,
  });

  static const List<NavigationDestination> destinations = [
    NavigationDestination(
      icon: Icon(Icons.psychology_outlined),
      selectedIcon: Icon(Icons.psychology),
      label: 'My Mind',
    ),
    NavigationDestination(
      icon: Icon(Icons.scatter_plot_outlined),
      selectedIcon: Icon(Icons.scatter_plot),
      label: '知识星云',
    ),
    NavigationDestination(
      icon: Icon(Icons.extension_outlined),
      selectedIcon: Icon(Icons.extension),
      label: '连接器',
    ),
    NavigationDestination(
      icon: Icon(Icons.settings_outlined),
      selectedIcon: Icon(Icons.settings),
      label: '设置',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    if (isDesktop) {
      return _buildSideNavigation(context);
    } else {
      return _buildBottomNavigation(context);
    }
  }

  Widget _buildSideNavigation(BuildContext context) {
    final theme = Theme.of(context);
    
    return Container(
      width: 80,
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        border: Border(
          right: BorderSide(
            color: theme.colorScheme.outline.withValues(alpha: 0.2),
            width: 1,
          ),
        ),
      ),
      child: Column(
        children: [
          // 导航项
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(vertical: 8),
              itemCount: destinations.length - 1, // 设置项单独处理
              itemBuilder: (context, index) {
                final destination = destinations[index];
                final isSelected = currentIndex == index;
                
                return _buildSideNavigationItem(
                  context,
                  destination,
                  isSelected,
                  () => onDestinationSelected(index),
                );
              },
            ),
          ),
          
          // 设置项放在底部
          const Divider(height: 1),
          _buildSideNavigationItem(
            context,
            destinations.last, // 设置项
            currentIndex == destinations.length - 1,
            () => onDestinationSelected(destinations.length - 1),
          ),
          const SizedBox(height: 8),
        ],
      ),
    );
  }

  Widget _buildSideNavigationItem(
    BuildContext context,
    NavigationDestination destination,
    bool isSelected,
    VoidCallback onTap,
  ) {
    final theme = Theme.of(context);
    
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: Container(
            padding: const EdgeInsets.symmetric(vertical: 12),
            decoration: BoxDecoration(
              color: isSelected 
                ? theme.colorScheme.secondaryContainer
                : Colors.transparent,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                IconTheme(
                  data: IconThemeData(
                    color: isSelected 
                      ? theme.colorScheme.onSecondaryContainer
                      : theme.colorScheme.onSurfaceVariant,
                    size: 24,
                  ),
                  child: isSelected 
                    ? (destination.selectedIcon ?? destination.icon)
                    : destination.icon,
                ),
                const SizedBox(height: 4),
                Text(
                  destination.label,
                  style: theme.textTheme.labelSmall?.copyWith(
                    color: isSelected 
                      ? theme.colorScheme.onSecondaryContainer
                      : theme.colorScheme.onSurfaceVariant,
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                  ),
                  textAlign: TextAlign.center,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildBottomNavigation(BuildContext context) {
    return NavigationBar(
      selectedIndex: currentIndex,
      onDestinationSelected: onDestinationSelected,
      destinations: destinations,
      animationDuration: const Duration(milliseconds: 300),
    );
  }
}

// 响应式布局组件，结合导航栏和内容
class ResponsiveLayout extends StatelessWidget {
  final int currentIndex;
  final Function(int) onDestinationSelected;
  final Widget child;
  final Widget? appBar;

  const ResponsiveLayout({
    super.key,
    required this.currentIndex,
    required this.onDestinationSelected,
    required this.child,
    this.appBar,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isDesktop = constraints.maxWidth >= 800;
        
        if (isDesktop) {
          // 桌面端：侧边导航
          return Scaffold(
            appBar: appBar != null ? appBar as PreferredSizeWidget : null,
            body: Row(
              children: [
                ResponsiveNavigation(
                  currentIndex: currentIndex,
                  onDestinationSelected: onDestinationSelected,
                  isDesktop: true,
                ),
                Expanded(child: child),
              ],
            ),
          );
        } else {
          // 移动端：底部导航
          return Scaffold(
            appBar: appBar != null ? appBar as PreferredSizeWidget : null,
            body: child,
            bottomNavigationBar: ResponsiveNavigation(
              currentIndex: currentIndex,
              onDestinationSelected: onDestinationSelected,
              isDesktop: false,
            ),
          );
        }
      },
    );
  }
}