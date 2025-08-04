import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/app_providers.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final currentThemeMode = ref.watch(themeModeProvider);
    
    return Scaffold(
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // 外观设置
          _buildSettingsSection(
            context,
            title: '外观',
            icon: Icons.palette_outlined,
            children: [
              _buildThemeSetting(context, ref, currentThemeMode),
            ],
          ),
          
          const SizedBox(height: 24),
          
          // 连接设置
          _buildSettingsSection(
            context,
            title: '连接',
            icon: Icons.link_outlined,
            children: [
              _buildSettingsTile(
                context,
                title: 'Daemon 状态',
                subtitle: '查看后端服务连接状态',
                leading: Icons.cloud_outlined,
                onTap: () {
                  // TODO: 显示详细的连接状态
                },
              ),
              _buildSettingsTile(
                context,
                title: '连接器管理',
                subtitle: '管理数据源连接器',
                leading: Icons.extension_outlined,
                onTap: () {
                  // TODO: 导航到连接器页面
                },
              ),
            ],
          ),
          
          const SizedBox(height: 24),
          
          // 数据设置
          _buildSettingsSection(
            context,
            title: '数据',
            icon: Icons.storage_outlined,
            children: [
              _buildSettingsTile(
                context,
                title: '数据同步',
                subtitle: '管理数据同步设置',
                leading: Icons.sync_outlined,
                onTap: () {
                  // TODO: 数据同步设置
                },
              ),
              _buildSettingsTile(
                context,
                title: '缓存管理',
                subtitle: '清理应用缓存',
                leading: Icons.cleaning_services_outlined,
                onTap: () {
                  // TODO: 缓存管理
                },
              ),
            ],
          ),
          
          const SizedBox(height: 24),
          
          // 关于
          _buildSettingsSection(
            context,
            title: '关于',
            icon: Icons.info_outlined,
            children: [
              _buildSettingsTile(
                context,
                title: 'Linch Mind',
                subtitle: '版本 1.0.0',
                leading: Icons.psychology_outlined,
                onTap: () {
                  // TODO: 显示关于信息
                },
              ),
              _buildSettingsTile(
                context,
                title: '帮助与反馈',
                subtitle: '获取帮助或提供反馈',
                leading: Icons.help_outline,
                onTap: () {
                  // TODO: 帮助页面
                },
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSettingsSection(
    BuildContext context, {
    required String title,
    required IconData icon,
    required List<Widget> children,
  }) {
    final theme = Theme.of(context);
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 16, bottom: 8),
          child: Row(
            children: [
              Icon(
                icon,
                size: 20,
                color: theme.colorScheme.primary,
              ),
              const SizedBox(width: 8),
              Text(
                title,
                style: theme.textTheme.titleMedium?.copyWith(
                  color: theme.colorScheme.primary,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
        Card(
          child: Column(
            children: children,
          ),
        ),
      ],
    );
  }

  Widget _buildSettingsTile(
    BuildContext context, {
    required String title,
    required String subtitle,
    required IconData leading,
    VoidCallback? onTap,
    Widget? trailing,
  }) {
    return ListTile(
      leading: Icon(leading),
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: trailing ?? const Icon(Icons.arrow_forward_ios, size: 16),
      onTap: onTap,
    );
  }

  Widget _buildThemeSetting(BuildContext context, WidgetRef ref, ThemeMode currentThemeMode) {
    final theme = Theme.of(context);
    
    return ExpansionTile(
      leading: const Icon(Icons.brightness_6_outlined),
      title: const Text('主题模式'),
      subtitle: Text(_getThemeText(currentThemeMode)),
      children: [
        _buildThemeOption(context, ref, ThemeMode.light, '浅色主题', Icons.light_mode),
        _buildThemeOption(context, ref, ThemeMode.dark, '深色主题', Icons.dark_mode),
        _buildThemeOption(context, ref, ThemeMode.system, '跟随系统', Icons.brightness_auto),
      ],
    );
  }

  Widget _buildThemeOption(
    BuildContext context,
    WidgetRef ref,
    ThemeMode mode,
    String title,
    IconData icon,
  ) {
    final currentThemeMode = ref.watch(themeModeProvider);
    final isSelected = currentThemeMode == mode;
    
    return ListTile(
      leading: Icon(icon),
      title: Text(title),
      trailing: isSelected ? const Icon(Icons.check, color: Colors.green) : null,
      onTap: () {
        ref.read(themeModeProvider.notifier).setThemeMode(mode);
      },
    );
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
}