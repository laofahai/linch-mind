import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:window_manager/window_manager.dart';
import '../providers/app_providers.dart';
import 'status_indicator.dart';

class UnifiedAppBar extends ConsumerWidget implements PreferredSizeWidget {
  final String title;
  final bool showBackButton;

  const UnifiedAppBar({
    super.key,
    required this.title,
    this.showBackButton = false,
  });

  bool get _isDesktop {
    if (kIsWeb) return false;
    return defaultTargetPlatform == TargetPlatform.macOS ||
        defaultTargetPlatform == TargetPlatform.windows ||
        defaultTargetPlatform == TargetPlatform.linux;
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appState = ref.watch(appStateProvider);
    final currentThemeMode = ref.watch(themeModeProvider);
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    final statusWidget = ResponsiveStatusIndicator(
      isConnected: appState.isConnected,
      customMessage: appState.errorMessage,
      onTap: () {
        // 刷新后台daemon状态
        ref.refresh(backgroundDaemonInitProvider);
      },
    );

    if (_isDesktop) {
      return _buildDesktopTitleBar(
          context, statusWidget, currentThemeMode, theme, isDark);
    } else {
      return _buildMobileAppBar(
          context, statusWidget, currentThemeMode, theme, ref);
    }
  }

  Widget _buildDesktopTitleBar(BuildContext context, Widget statusWidget,
      ThemeMode currentThemeMode, ThemeData theme, bool isDark) {
    return Container(
      height: preferredSize.height,
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
          // 拖拽区域 + 应用标题
          Expanded(
            child: GestureDetector(
              behavior: HitTestBehavior.translucent,
              onPanStart: (details) {
                windowManager.startDragging();
              },
              onDoubleTap: () async {
                try {
                  if (await windowManager.isMaximized()) {
                    await windowManager.unmaximize();
                  } else {
                    await windowManager.maximize();
                  }
                } catch (e) {
                  debugPrint('Error toggling window state: $e');
                }
              },
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
                      title,
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

          // 状态指示器
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: statusWidget,
          ),

          // 主题切换按钮
          _ThemeToggleButton(currentThemeMode: currentThemeMode),

          // 窗口控制按钮
          _WindowControls(),
        ],
      ),
    );
  }

  Widget _buildMobileAppBar(BuildContext context, Widget statusWidget,
      ThemeMode currentThemeMode, ThemeData theme, WidgetRef ref) {
    return AppBar(
      title: Text(title),
      automaticallyImplyLeading: showBackButton,
      backgroundColor: theme.colorScheme.surface,
      surfaceTintColor: theme.colorScheme.surfaceTint,
      actions: [
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

  @override
  Size get preferredSize => const Size.fromHeight(50);
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
            child: Icon(
              getThemeIcon(),
              size: 20,
              color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
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

class _WindowControls extends StatefulWidget {
  @override
  __WindowControlsState createState() => __WindowControlsState();
}

class __WindowControlsState extends State<_WindowControls> with WindowListener {
  bool _isMaximized = false;

  @override
  void initState() {
    super.initState();
    _checkMaximizedState();
    windowManager.addListener(this);
  }

  @override
  void dispose() {
    windowManager.removeListener(this);
    super.dispose();
  }

  @override
  void onWindowMaximize() {
    setState(() {
      _isMaximized = true;
    });
  }

  @override
  void onWindowUnmaximize() {
    setState(() {
      _isMaximized = false;
    });
  }

  void _checkMaximizedState() async {
    final isMaximized = await windowManager.isMaximized();
    if (mounted) {
      setState(() {
        _isMaximized = isMaximized;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        // 最小化按钮
        _WindowButton(
          icon: Icons.remove,
          onPressed: () => windowManager.minimize(),
          hoverColor: theme.colorScheme.primary.withValues(alpha: 0.1),
        ),

        // 最大化/还原按钮
        _WindowButton(
          icon: _isMaximized ? Icons.crop_square : Icons.crop_din,
          onPressed: () async {
            if (_isMaximized) {
              await windowManager.unmaximize();
            } else {
              await windowManager.maximize();
            }
            _checkMaximizedState();
          },
          hoverColor: theme.colorScheme.primary.withValues(alpha: 0.1),
        ),

        // 关闭按钮
        _WindowButton(
          icon: Icons.close,
          onPressed: () => windowManager.close(),
          hoverColor: Colors.red.withValues(alpha: 0.1),
          iconColorOnHover: Colors.red,
        ),
      ],
    );
  }
}

class _WindowButton extends StatefulWidget {
  final IconData icon;
  final VoidCallback onPressed;
  final Color? hoverColor;
  final Color? iconColorOnHover;

  const _WindowButton({
    required this.icon,
    required this.onPressed,
    this.hoverColor,
    this.iconColorOnHover,
  });

  @override
  __WindowButtonState createState() => __WindowButtonState();
}

class __WindowButtonState extends State<_WindowButton> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: GestureDetector(
        onTap: widget.onPressed,
        child: Container(
          width: 56,
          height: 50,
          decoration: BoxDecoration(
            color: _isHovered
                ? (widget.hoverColor ??
                    theme.colorScheme.primary.withValues(alpha: 0.1))
                : Colors.transparent,
          ),
          child: Icon(
            widget.icon,
            size: 20,
            color: _isHovered && widget.iconColorOnHover != null
                ? widget.iconColorOnHover
                : theme.colorScheme.onSurface.withValues(alpha: 0.7),
          ),
        ),
      ),
    );
  }
}
