import 'dart:developer' as developer;
import 'package:flutter/foundation.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:window_manager/window_manager.dart';
import '../providers/app_providers.dart';
import '../providers/app_error_provider.dart';
import '../utils/notification_utils.dart';
import 'status_indicator.dart';
import 'system_health_indicator.dart';

class UnifiedAppBar extends ConsumerStatefulWidget
    implements PreferredSizeWidget {
  final String title;
  final bool showBackButton;

  const UnifiedAppBar({
    super.key,
    required this.title,
    this.showBackButton = false,
  });

  @override
  ConsumerState<UnifiedAppBar> createState() => _UnifiedAppBarState();

  @override
  Size get preferredSize => const Size.fromHeight(50);
}

class _UnifiedAppBarState extends ConsumerState<UnifiedAppBar> {
  bool get _isDesktop {
    if (kIsWeb) return false;
    return defaultTargetPlatform == TargetPlatform.macOS ||
        defaultTargetPlatform == TargetPlatform.windows ||
        defaultTargetPlatform == TargetPlatform.linux;
  }

  @override
  Widget build(BuildContext context) {
    final appState = ref.watch(appStateProvider);
    final currentThemeMode = ref.watch(themeModeProvider);
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    final statusWidget = ResponsiveStatusIndicator(
      isConnected: appState.isConnected,
      customMessage: appState.errorMessage,
      onTap: () {
        // 刷新后台daemon状态
        final _ = ref.refresh(backgroundDaemonInitProvider);
      },
    );

    if (_isDesktop) {
      return _buildDesktopTitleBar(
          context, statusWidget, currentThemeMode, theme, isDark);
    } else {
      return _buildMobileAppBar(context, statusWidget, currentThemeMode, theme);
    }
  }

  Widget _buildDesktopTitleBar(BuildContext context, Widget statusWidget,
      ThemeMode currentThemeMode, ThemeData theme, bool isDark) {
    return Container(
      height: widget.preferredSize.height,
      decoration: BoxDecoration(
        color: isDark
            ? theme.colorScheme.surface.withValues(alpha: 0.95)
            : theme.colorScheme.surface.withValues(alpha: 0.98),
        border: Border(
          bottom: BorderSide(
            color: theme.colorScheme.outline.withValues(alpha: 0.2),
            width: 1,
          ),
        ),
        boxShadow: [
          BoxShadow(
            color: theme.shadowColor.withValues(alpha: 0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          // 可拖动的标题区域
          Expanded(
            child: _DraggableTitleBar(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Row(
                  children: [
                    // 应用图标
                    Container(
                      width: 24,
                      height: 24,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            theme.colorScheme.primary,
                            theme.colorScheme.secondary,
                          ],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Icon(
                        Icons.psychology_outlined,
                        size: 16,
                        color: theme.colorScheme.onPrimary,
                      ),
                    ),
                    const SizedBox(width: 12),
                    // 应用标题
                    Text(
                      'Linch Mind',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                        color: theme.colorScheme.onSurface,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

          // 系统健康度指示器
          Consumer(
            builder: (context, ref, child) {
              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 4),
                child: SystemHealthIndicator(
                  showDetails: false,
                  onTap: () => _showSystemHealthDetails(context, ref),
                ),
              );
            },
          ),

          // 状态指示器
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: statusWidget,
          ),

          // 主题切换按钮
          _ThemeToggleButton(currentThemeMode: currentThemeMode),

          // 窗口控制按钮
          Padding(
            padding: const EdgeInsets.only(right: 8),
            child: _WindowControls(),
          ),
        ],
      ),
    );
  }

  Widget _buildMobileAppBar(BuildContext context, Widget statusWidget,
      ThemeMode currentThemeMode, ThemeData theme) {
    return AppBar(
      title: Text(widget.title),
      automaticallyImplyLeading: widget.showBackButton,
      backgroundColor: theme.colorScheme.surface,
      surfaceTintColor: theme.colorScheme.surfaceTint,
      actions: [
        // 系统健康度指示器
        Consumer(
          builder: (context, ref, child) {
            return SystemHealthIndicator(
              showDetails: false,
              onTap: () => _showSystemHealthDetails(context, ref),
            );
          },
        ),
        const SizedBox(width: 8),
        statusWidget,
        const SizedBox(width: 8),
        _MobileMenuButton(
          currentThemeMode: currentThemeMode,
          onThemeChanged: (mode) =>
              ref.read(themeModeProvider.notifier).setThemeMode(mode),
        ),
        const SizedBox(width: 16),
      ],
    );
  }

  /// 显示系统健康详情
  void _showSystemHealthDetails(BuildContext context, WidgetRef ref) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.6,
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surface,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
        ),
        child: Column(
          children: [
            // 顶部拖拽指示器
            Container(
              width: 40,
              height: 4,
              margin: const EdgeInsets.symmetric(vertical: 8),
              decoration: BoxDecoration(
                color: Theme.of(context)
                    .colorScheme
                    .onSurfaceVariant
                    .withValues(alpha: 0.3),
                borderRadius: BorderRadius.circular(2),
              ),
            ),

            // 系统健康详情
            const Expanded(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: SystemHealthIndicator(showDetails: true),
              ),
            ),

            // 快捷操作按钮
            Consumer(
              builder: (context, ref, child) {
                final errorState = ref.watch(appErrorProvider);
                return Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      ElevatedButton.icon(
                        onPressed: errorState.canRetryAny
                            ? () {
                                ref
                                    .read(appErrorProvider.notifier)
                                    .retryAllErrors();
                                Navigator.pop(context);
                                showInfoNotification(ref, '正在重试所有失败的操作');
                              }
                            : null,
                        icon: const Icon(Icons.refresh),
                        label: const Text('重试全部'),
                      ),
                      ElevatedButton.icon(
                        onPressed: errorState.hasErrors
                            ? () {
                                ref
                                    .read(appErrorProvider.notifier)
                                    .clearAllErrors();
                                Navigator.pop(context);
                                showSuccessNotification(ref, '已清除所有错误');
                              }
                            : null,
                        icon: const Icon(Icons.clear_all),
                        label: const Text('清除全部'),
                        style: ElevatedButton.styleFrom(
                          foregroundColor: Colors.orange,
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _DraggableTitleBar extends StatefulWidget {
  final Widget child;

  const _DraggableTitleBar({required this.child});

  @override
  State<_DraggableTitleBar> createState() => _DraggableTitleBarState();
}

class _DraggableTitleBarState extends State<_DraggableTitleBar> {
  @override
  Widget build(BuildContext context) {
    return Listener(
      // 使用Listener来捕获原始指针事件，更好地处理macOS手势
      onPointerDown: (event) {
        // 对于macOS，让系统处理三指拖动，我们只处理鼠标左键拖动
        if (defaultTargetPlatform == TargetPlatform.macOS) {
          if (event.kind == PointerDeviceKind.mouse && event.buttons == 1) {
            windowManager.startDragging();
          }
        } else {
          // 其他平台保持原有逻辑
          windowManager.startDragging();
        }
      },
      child: GestureDetector(
        onDoubleTap: () async {
          final isMaximized = await windowManager.isMaximized();
          if (isMaximized) {
            await windowManager.unmaximize();
          } else {
            await windowManager.maximize();
          }
        },
        behavior: HitTestBehavior.translucent,
        child: MouseRegion(
          cursor: SystemMouseCursors.move,
          child: widget.child,
        ),
      ),
    );
  }
}

class _WindowControls extends StatefulWidget {
  const _WindowControls();

  @override
  State<_WindowControls> createState() => _WindowControlsState();
}

class _WindowControlsState extends State<_WindowControls> with WindowListener {
  bool _isMaximized = false;

  @override
  void initState() {
    super.initState();
    windowManager.addListener(this);
    _checkMaximizeState();
  }

  @override
  void dispose() {
    windowManager.removeListener(this);
    super.dispose();
  }

  @override
  void onWindowMaximize() {
    _checkMaximizeState();
  }

  @override
  void onWindowUnmaximize() {
    _checkMaximizeState();
  }

  Future<void> _checkMaximizeState() async {
    try {
      final isMaximized = await windowManager.isMaximized();
      if (mounted) {
        setState(() {
          _isMaximized = isMaximized;
        });
      }
    } catch (e) {
      developer.log('Failed to check window maximize state: $e');
    }
  }

  Future<void> _safeWindowOperation(Future<void> Function() operation) async {
    try {
      await operation();
    } catch (e) {
      developer.log('Window operation failed: $e');
    }
  }

  Future<void> _safeToggleMaximize() async {
    try {
      if (_isMaximized) {
        await windowManager.unmaximize();
      } else {
        await windowManager.maximize();
      }
      await _checkMaximizeState();
    } catch (e) {
      developer.log('Failed to toggle window maximize state: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final buttonColor = theme.colorScheme.onSurface.withValues(alpha: 0.6);
    const buttonSize = 32.0;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        // 最小化按钮
        _WindowControlButton(
          icon: Icons.remove,
          color: buttonColor,
          size: buttonSize,
          onPressed: () => _safeWindowOperation(windowManager.minimize),
          tooltip: '最小化',
        ),

        // 最大化/还原按钮
        _WindowControlButton(
          icon: _isMaximized ? Icons.fullscreen_exit : Icons.fullscreen,
          color: buttonColor,
          size: buttonSize,
          onPressed: () => _safeToggleMaximize(),
          tooltip: _isMaximized ? '还原' : '最大化',
        ),

        // 关闭按钮
        _WindowControlButton(
          icon: Icons.close,
          color: buttonColor,
          size: buttonSize,
          onPressed: () => _safeWindowOperation(windowManager.close),
          tooltip: '关闭',
          isCloseButton: true,
        ),
      ],
    );
  }
}

class _WindowControlButton extends StatefulWidget {
  final IconData icon;
  final Color color;
  final double size;
  final VoidCallback onPressed;
  final String tooltip;
  final bool isCloseButton;

  const _WindowControlButton({
    required this.icon,
    required this.color,
    required this.size,
    required this.onPressed,
    required this.tooltip,
    this.isCloseButton = false,
  });

  @override
  State<_WindowControlButton> createState() => _WindowControlButtonState();
}

class _WindowControlButtonState extends State<_WindowControlButton> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: GestureDetector(
        onTap: widget.onPressed,
        child: Tooltip(
          message: widget.tooltip,
          child: Container(
            width: widget.size,
            height: widget.size,
            decoration: BoxDecoration(
              color: _isHovered
                  ? (widget.isCloseButton
                      ? Colors.red.withValues(alpha: 0.9)
                      : theme.colorScheme.primary.withValues(alpha: 0.1))
                  : Colors.transparent,
              borderRadius: BorderRadius.circular(4),
            ),
            child: Icon(
              widget.icon,
              size: 16,
              color: _isHovered && widget.isCloseButton
                  ? Colors.white
                  : widget.color,
            ),
          ),
        ),
      ),
    );
  }
}

class _ThemeToggleButton extends ConsumerStatefulWidget {
  final ThemeMode currentThemeMode;

  const _ThemeToggleButton({required this.currentThemeMode});

  @override
  ConsumerState<_ThemeToggleButton> createState() => _ThemeToggleButtonState();
}

class _ThemeToggleButtonState extends ConsumerState<_ThemeToggleButton> {
  bool _isHovered = false;

  IconData getThemeIcon() {
    switch (widget.currentThemeMode) {
      case ThemeMode.light:
        return Icons.light_mode;
      case ThemeMode.dark:
        return Icons.dark_mode;
      case ThemeMode.system:
        return Icons.brightness_auto;
    }
  }

  String getTooltipText() {
    switch (widget.currentThemeMode) {
      case ThemeMode.light:
        return '浅色主题 (点击切换到深色)';
      case ThemeMode.dark:
        return '深色主题 (点击切换到跟随系统)';
      case ThemeMode.system:
        return '跟随系统 (点击切换到浅色)';
    }
  }

  ThemeMode getNextThemeMode() {
    switch (widget.currentThemeMode) {
      case ThemeMode.light:
        return ThemeMode.dark;
      case ThemeMode.dark:
        return ThemeMode.system;
      case ThemeMode.system:
        return ThemeMode.light;
    }
  }

  void _toggleTheme() {
    final nextMode = getNextThemeMode();
    ref.read(themeModeProvider.notifier).setThemeMode(nextMode);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: _toggleTheme,
        child: Tooltip(
          message: getTooltipText(),
          child: Container(
            width: 56,
            height: 50,
            decoration: BoxDecoration(
              color: _isHovered
                  ? theme.colorScheme.primary.withValues(alpha: 0.1)
                  : Colors.transparent,
            ),
            child: AnimatedSwitcher(
              duration: const Duration(milliseconds: 300),
              transitionBuilder: (child, animation) {
                return ScaleTransition(
                  scale: animation,
                  child: FadeTransition(
                    opacity: animation,
                    child: child,
                  ),
                );
              },
              child: Icon(
                getThemeIcon(),
                key: ValueKey(widget.currentThemeMode),
                size: 20,
                color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _MobileMenuButton extends StatelessWidget {
  final ThemeMode currentThemeMode;
  final Function(ThemeMode) onThemeChanged;

  const _MobileMenuButton({
    required this.currentThemeMode,
    required this.onThemeChanged,
  });

  IconData _getThemeIcon(ThemeMode mode) {
    switch (mode) {
      case ThemeMode.light:
        return Icons.light_mode;
      case ThemeMode.dark:
        return Icons.dark_mode;
      case ThemeMode.system:
        return Icons.brightness_auto;
    }
  }

  String _getThemeText(ThemeMode mode) {
    switch (mode) {
      case ThemeMode.light:
        return '浅色主题';
      case ThemeMode.dark:
        return '深色主题';
      case ThemeMode.system:
        return '跟随系统';
    }
  }

  ThemeMode _getNextThemeMode() {
    switch (currentThemeMode) {
      case ThemeMode.light:
        return ThemeMode.dark;
      case ThemeMode.dark:
        return ThemeMode.system;
      case ThemeMode.system:
        return ThemeMode.light;
    }
  }

  @override
  Widget build(BuildContext context) {
    return PopupMenuButton<String>(
      icon: const Icon(Icons.more_vert),
      tooltip: '更多选项',
      itemBuilder: (BuildContext context) => [
        PopupMenuItem<String>(
          value: 'theme',
          child: Row(
            children: [
              Icon(_getThemeIcon(currentThemeMode), size: 20),
              const SizedBox(width: 12),
              Text(_getThemeText(currentThemeMode)),
              const Spacer(),
              Icon(Icons.arrow_forward_ios, size: 16, color: Colors.grey[600]),
            ],
          ),
        ),
        const PopupMenuDivider(),
        const PopupMenuItem<String>(
          value: 'settings',
          child: Row(
            children: [
              Icon(Icons.settings, size: 20),
              SizedBox(width: 12),
              Text('设置'),
            ],
          ),
        ),
      ],
      onSelected: (String value) {
        switch (value) {
          case 'theme':
            onThemeChanged(_getNextThemeMode());
            break;
          case 'settings':
            // TODO: 导航到设置页面
            break;
        }
      },
    );
  }
}
