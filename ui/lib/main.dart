import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'screens/home_screen.dart';
import 'screens/connector_management_screen.dart';
import 'screens/data_screen.dart';
import 'screens/graph_screen.dart';
import 'providers/app_providers.dart';
import 'widgets/status_indicator.dart';

void main() {
  runApp(
    const ProviderScope(
      child: LinchMindApp(),
    ),
  );
}

class LinchMindApp extends StatelessWidget {
  const LinchMindApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Linch Mind',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF6750A4),
          brightness: Brightness.light,
        ),
      ),
      darkTheme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF6750A4),
          brightness: Brightness.dark,
        ),
      ),
      routerConfig: _router,
    );
  }
}

final GoRouter _router = GoRouter(
  routes: [
    GoRoute(
      path: '/',
      pageBuilder: (context, state) => NoTransitionPage<void>(
        child: const MainApp(),
      ),
    ),
  ],
);

/// 主应用组件 - 管理所有导航，不使用路由切换
class MainApp extends ConsumerStatefulWidget {
  const MainApp({super.key});

  @override
  ConsumerState<MainApp> createState() => _MainAppState();
}

class _MainAppState extends ConsumerState<MainApp> {
  int _selectedIndex = 0;

  final List<Widget> _screens = const [
    HomeScreen(),
    ConnectorManagementScreen(),
    DataScreen(),
    GraphScreen(),
  ];

  final List<String> _titles = const [
    'Home',
    'Connectors',
    'Data',
    'Graph',
  ];

  void _onDestinationSelected(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth > 840) {
          return _buildDesktopLayout();
        } else {
          return _buildMobileLayout();
        }
      },
    );
  }

  Widget _buildDesktopLayout() {
    return Scaffold(
      body: Row(
        children: [
          // 固定的左侧导航栏
          NavigationRail(
            selectedIndex: _selectedIndex,
            onDestinationSelected: _onDestinationSelected,
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
          // 主内容区域 - 只有这部分会切换，无动画
          Expanded(
            child: _screens[_selectedIndex],
          ),
        ],
      ),
    );
  }

  Widget _buildMobileLayout() {
    final healthCheckAsync = ref.watch(healthCheckProvider);
    
    return Scaffold(
      // 固定的AppBar
      appBar: AppBar(
        title: Text('Linch Mind - ${_titles[_selectedIndex]}'),
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
      // 主内容区域 - 只有这部分会切换，无动画
      body: _screens[_selectedIndex],
      // 固定的底部导航栏
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: _onDestinationSelected,
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
      ),
    );
  }
}