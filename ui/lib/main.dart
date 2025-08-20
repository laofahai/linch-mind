import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:window_manager/window_manager.dart';
import 'screens/home_screen.dart';
import 'screens/starry_universe_screen.dart';
import 'screens/connector_management_screen.dart';
import 'screens/settings_screen.dart';
import 'providers/app_providers.dart';
// import 'providers/notification_provider.dart'; // 通知在overlay中处理
import 'widgets/unified_app_bar.dart';
import 'widgets/responsive_navigation.dart';
import 'widgets/smart_error_display.dart';
import 'widgets/system_health_indicator.dart';
import 'widgets/notification_overlay.dart';
import 'utils/app_logger.dart';
import 'utils/enhanced_error_handler.dart';
import 'config/app_constants.dart';
import 'core/service_initializer.dart';
import 'core/ui_service_facade.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // 初始化日志系统
  AppLogger.setDebugMode(kDebugMode);
  AppLogger.info('应用启动', module: 'Main');

  // 🚀 统一初始化所有服务 - 消除.instance调用
  initializeServices();

  // 🔧 设置全局错误处理器
  final errorHandler = getService<EnhancedErrorHandler>();

  // 处理Flutter框架错误
  FlutterError.onError = (FlutterErrorDetails details) {
    errorHandler.handleFlutterError(details);
  };

  // 处理异步错误和未捕获的错误
  PlatformDispatcher.instance.onError = (error, stack) {
    errorHandler.handleException(
      error,
      operation: 'Platform Dispatcher',
      stackTrace: stack,
    );
    return true;
  };

  // 只在桌面端配置窗口管理
  if (defaultTargetPlatform == TargetPlatform.macOS ||
      defaultTargetPlatform == TargetPlatform.windows ||
      defaultTargetPlatform == TargetPlatform.linux) {
    // 配置窗口管理
    await windowManager.ensureInitialized();

    WindowOptions windowOptions = const WindowOptions(
      size: AppWindowConstants.defaultSize,
      center: true,
      backgroundColor: Colors.transparent, // 使用透明背景减少闪烁
      skipTaskbar: false,
      titleBarStyle: TitleBarStyle.hidden, // 保持隐藏标题栏
      minimumSize: AppWindowConstants.minimumSize,
      alwaysOnTop: false,
      fullScreen: false,
    );

    windowManager.waitUntilReadyToShow(windowOptions, () async {
      // 优化窗口配置顺序，减少闪烁
      if (defaultTargetPlatform == TargetPlatform.macOS) {
        // 一次性配置所有属性，减少重绘次数
        await Future.wait([
          windowManager.setMovable(true),
          windowManager.setResizable(true),
          windowManager.setAsFrameless(),
          windowManager.setHasShadow(true),
        ]);
      }

      // 最后显示窗口
      await windowManager.show();
      await windowManager.focus();
    });
  }

  runApp(
    const ProviderScope(
      child: LinchMindApp(),
    ),
  );
}

class LinchMindApp extends ConsumerWidget {
  const LinchMindApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeModeProvider);

    return MaterialApp(
      title: 'Linch Mind',
      theme: _buildLightTheme(),
      darkTheme: _buildDarkTheme(),
      themeMode: themeMode,
      home: const NotificationOverlay(
        child: SmartErrorDisplay(
          child: AppInitializationWrapper(),
        ),
      ),
    );
  }

  ThemeData _buildLightTheme() {
    const seedColor = Color(0xFF2196F3); // 现代蓝色
    final colorScheme = ColorScheme.fromSeed(
      seedColor: seedColor,
      brightness: Brightness.light,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      cardTheme: CardThemeData(
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(
            color: colorScheme.outline.withValues(alpha: 0.2),
          ),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide:
              BorderSide(color: colorScheme.outline.withValues(alpha: 0.3)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide:
              BorderSide(color: colorScheme.outline.withValues(alpha: 0.3)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: colorScheme.primary, width: 2),
        ),
        filled: true,
        fillColor: colorScheme.surface,
      ),
    );
  }

  ThemeData _buildDarkTheme() {
    const seedColor = Color(0xFF2196F3); // 现代蓝色
    final colorScheme = ColorScheme.fromSeed(
      seedColor: seedColor,
      brightness: Brightness.dark,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      cardTheme: CardThemeData(
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(
            color: colorScheme.outline.withValues(alpha: 0.2),
          ),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide:
              BorderSide(color: colorScheme.outline.withValues(alpha: 0.3)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide:
              BorderSide(color: colorScheme.outline.withValues(alpha: 0.3)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: colorScheme.primary, width: 2),
        ),
        filled: true,
        fillColor: colorScheme.surface,
      ),
    );
  }
}

/// 主应用组件 - 响应式导航版本
class MainApp extends ConsumerStatefulWidget {
  const MainApp({super.key});

  @override
  ConsumerState<MainApp> createState() => _MainAppState();
}

class _MainAppState extends ConsumerState<MainApp> {
  int _currentIndex = 0; // 默认显示首页

  final List<Widget> _pages = const [
    HomeScreen(),
    StarryUniverseScreen(),
    ConnectorManagementScreen(),
    SettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return ResponsiveLayout(
      currentIndex: _currentIndex,
      onDestinationSelected: (index) {
        setState(() {
          _currentIndex = index;
        });
      },
      appBar: const UnifiedAppBar(
        title: 'Linch Mind', // 固定标题
      ),
      child: Scaffold(
        body: IndexedStack(
          index: _currentIndex,
          children: _pages,
        ),
        floatingActionButton: const SystemHealthFAB(),
      ),
    );
  }
}

/// 应用初始化包装器
class AppInitializationWrapper extends ConsumerWidget {
  const AppInitializationWrapper({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 启动后台daemon检查，但不阻塞UI
    ref.read(backgroundDaemonInitProvider);

    // 直接显示主应用，daemon状态通过状态指示器显示
    return const MainApp();
  }
}
