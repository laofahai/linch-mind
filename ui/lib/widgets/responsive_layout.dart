import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/app_providers.dart';
import '../widgets/status_indicator.dart';

/// 响应式布局组件 - 统一导航和AppBar管理
/// 小屏幕：底部导航栏 + 顶部AppBar
/// 大屏幕：左侧导航栏 + 无独立AppBar
class ResponsiveLayout extends ConsumerWidget {
  final Widget child;
  final int selectedIndex;

  const ResponsiveLayout({
    required this.child,
    required this.selectedIndex,
    super.key,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return LayoutBuilder(
      builder: (context, constraints) {
        // 大屏幕布局：宽度 > 840px 使用左侧导航栏
        if (constraints.maxWidth > 840) {
          return DesktopLayout(
            selectedIndex: selectedIndex,
            child: child,
          );
        } else {
          // 小屏幕布局：底部导航栏 + 顶部AppBar
          return MobileLayout(
            selectedIndex: selectedIndex,
            child: child,
          );
        }
      },
    );
  }
}

/// 桌面布局 - 侧边栏导航
class DesktopLayout extends StatelessWidget {
  final Widget child;
  final int selectedIndex;

  const DesktopLayout({
    required this.child,
    required this.selectedIndex,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          // 左侧导航栏
          NavigationRail(
            selectedIndex: selectedIndex,
            onDestinationSelected: (index) => _navigateTo(context, index),
            labelType: NavigationRailLabelType.all,
            backgroundColor: Theme.of(context).colorScheme.surfaceContainerLow,
            destinations: const [
              NavigationRailDestination(
                icon: Icon(Icons.home_outlined),
                selectedIcon: Icon(Icons.home),
                label: Text('Home'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.cable_outlined),
                selectedIcon: Icon(Icons.cable),
                label: Text('Connectors'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.storage_outlined),
                selectedIcon: Icon(Icons.storage),
                label: Text('Data'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.account_tree_outlined),
                selectedIcon: Icon(Icons.account_tree),
                label: Text('Graph'),
              ),
            ],
          ),
          // 分隔线
          const VerticalDivider(thickness: 1, width: 1),
          // 主内容区域
          Expanded(child: child),
        ],
      ),
    );
  }

  void _navigateTo(BuildContext context, int index) {
    // 使用GoRouter的静态方法导航
    switch (index) {
      case 0:
        context.go('/');
        break;
      case 1:
        context.go('/connectors');
        break;
      case 2:
        context.go('/data');
        break;
      case 3:
        context.go('/graph');
        break;
    }
  }
}

/// 移动布局 - 底部导航 + 顶部AppBar
class MobileLayout extends ConsumerWidget {
  final Widget child;
  final int selectedIndex;

  const MobileLayout({
    required this.child,
    required this.selectedIndex,
    super.key,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final healthCheckAsync = ref.watch(healthCheckProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Linch Mind'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          healthCheckAsync.when(
            data: (isHealthy) => StatusIndicator(
              isConnected: isHealthy,
              onTap: () => ref.refresh(healthCheckProvider),
            ),
            loading: () => const CircularProgressIndicator(),
            error: (_, __) => StatusIndicator(
              isConnected: false,
              onTap: () => ref.refresh(healthCheckProvider),
            ),
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: selectedIndex,
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.cable_outlined),
            selectedIcon: Icon(Icons.cable),
            label: 'Connectors',
          ),
          NavigationDestination(
            icon: Icon(Icons.storage_outlined),
            selectedIcon: Icon(Icons.storage),
            label: 'Data',
          ),
          NavigationDestination(
            icon: Icon(Icons.account_tree_outlined),
            selectedIcon: Icon(Icons.account_tree),
            label: 'Graph',
          ),
        ],
        onDestinationSelected: (index) => _navigateTo(context, index),
      ),
    );
  }

  void _navigateTo(BuildContext context, int index) {
    switch (index) {
      case 0:
        context.go('/');
        break;
      case 1:
        context.go('/connectors');
        break;
      case 2:
        context.go('/data');
        break;
      case 3:
        context.go('/graph');
        break;
    }
  }
}

/// 导航服务 - 全局导航状态管理
class NavigationService {
  static final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();
  
  static int getIndexFromPath(String path) {
    switch (path) {
      case '/':
        return 0;
      case '/connectors':
        return 1;
      case '/data':
        return 2;
      case '/graph':
        return 3;
      default:
        return 0;
    }
  }
}

/// 响应式应用包装器
class ResponsiveApp extends StatelessWidget {
  final Widget child;
  final String currentPath;

  const ResponsiveApp({
    required this.child,
    required this.currentPath,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final selectedIndex = NavigationService.getIndexFromPath(currentPath);
    
    return ResponsiveLayout(
      selectedIndex: selectedIndex,
      child: child,
    );
  }
}