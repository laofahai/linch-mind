import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/app_providers.dart';
import '../providers/daemon_providers.dart';
import '../services/daemon_lifecycle_service.dart';
import 'registry_settings_screen.dart';

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
              _buildDaemonStatusTile(context, ref),
              _buildSettingsTile(
                context,
                title: '连接器管理',
                subtitle: '管理数据源连接器',
                leading: Icons.extension_outlined,
                onTap: () {
                  // TODO: 导航到连接器页面
                },
              ),
              _buildSettingsTile(
                context,
                title: 'Registry 设置',
                subtitle: '管理连接器注册中心配置',
                leading: Icons.hub_outlined,
                onTap: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (context) => const RegistrySettingsScreen(),
                    ),
                  );
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

  Widget _buildThemeSetting(
      BuildContext context, WidgetRef ref, ThemeMode currentThemeMode) {
    final theme = Theme.of(context);

    return ExpansionTile(
      leading: const Icon(Icons.brightness_6_outlined),
      title: const Text('主题模式'),
      subtitle: Text(_getThemeText(currentThemeMode)),
      children: [
        _buildThemeOption(
            context, ref, ThemeMode.light, '浅色主题', Icons.light_mode),
        _buildThemeOption(
            context, ref, ThemeMode.dark, '深色主题', Icons.dark_mode),
        _buildThemeOption(
            context, ref, ThemeMode.system, '跟随系统', Icons.brightness_auto),
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
      trailing:
          isSelected ? const Icon(Icons.check, color: Colors.green) : null,
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

  Widget _buildDaemonStatusTile(BuildContext context, WidgetRef ref) {
    final daemonState = ref.watch(daemonStateProvider);

    return ExpansionTile(
      leading: Icon(
        daemonState.isRunning
            ? Icons.cloud_done_outlined
            : Icons.cloud_off_outlined,
        color: daemonState.isRunning ? Colors.green : Colors.orange,
      ),
      title: const Text('Daemon 状态'),
      subtitle: Text(_getDaemonStatusText(daemonState)),
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 基本信息
              _buildInfoRow('运行模式', _getModeText(daemonState.mode)),
              _buildInfoRow('状态', daemonState.isRunning ? '运行中' : '未运行'),

              if (daemonState.daemonInfo != null) ...[
                _buildInfoRow('地址', daemonState.daemonInfo!.baseUrl),
                _buildInfoRow('进程ID', daemonState.daemonInfo!.pid.toString()),
              ],

              // 错误信息
              if (daemonState.error != null) ...[
                const SizedBox(height: 8),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.errorContainer,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    daemonState.error!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.onErrorContainer,
                    ),
                  ),
                ),
              ],

              // 控制按钮
              const SizedBox(height: 16),
              Row(
                children: [
                  // 刷新按钮
                  ElevatedButton.icon(
                    onPressed: daemonState.isLoading
                        ? null
                        : () {
                            ref
                                .read(daemonStateProvider.notifier)
                                .refreshStatus();
                          },
                    icon: daemonState.isLoading
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.refresh),
                    label: const Text('刷新'),
                  ),

                  const SizedBox(width: 8),

                  // 开发模式控制按钮
                  if (daemonState.mode == RunMode.development) ...[
                    if (!daemonState.isRunning) ...[
                      ElevatedButton.icon(
                        onPressed: daemonState.isLoading
                            ? null
                            : () async {
                                await ref
                                    .read(daemonStateProvider.notifier)
                                    .startDaemon();
                              },
                        icon: const Icon(Icons.play_arrow),
                        label: const Text('启动'),
                      ),
                    ] else ...[
                      ElevatedButton.icon(
                        onPressed: daemonState.isLoading
                            ? null
                            : () async {
                                await ref
                                    .read(daemonStateProvider.notifier)
                                    .stopDaemon();
                              },
                        icon: const Icon(Icons.stop),
                        label: const Text('停止'),
                      ),
                      const SizedBox(width: 8),
                      ElevatedButton.icon(
                        onPressed: daemonState.isLoading
                            ? null
                            : () async {
                                await ref
                                    .read(daemonStateProvider.notifier)
                                    .restartDaemon();
                              },
                        icon: const Icon(Icons.restart_alt),
                        label: const Text('重启'),
                      ),
                    ],
                  ],
                ],
              ),

              // 生产模式提示
              if (daemonState.mode == RunMode.production) ...[
                const SizedBox(height: 12),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.primaryContainer,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '生产模式下daemon作为系统服务运行，不支持手动控制。',
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.onPrimaryContainer,
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Expanded(
            child: Text(value),
          ),
        ],
      ),
    );
  }

  String _getDaemonStatusText(DaemonState state) {
    if (state.isLoading) return '检查中...';
    if (state.isRunning) return '服务正常运行';
    if (state.error != null) return '连接异常';
    return '服务未启动';
  }

  String _getModeText(RunMode mode) {
    switch (mode) {
      case RunMode.development:
        return '开发模式';
      case RunMode.production:
        return '生产模式';
    }
  }
}
