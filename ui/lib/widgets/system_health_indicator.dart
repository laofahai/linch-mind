import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:async';
import 'dart:math' as math;

import '../providers/app_error_provider.dart';
import '../utils/notification_utils.dart';

/// 系统健康度级别
enum SystemHealthLevel {
  excellent, // 优秀 (绿色)
  good, // 良好 (浅绿)
  warning, // 警告 (橙色)
  critical, // 严重 (红色)
  unknown, // 未知 (灰色)
}

/// 系统健康度指示器
class SystemHealthIndicator extends ConsumerStatefulWidget {
  final bool showDetails;
  final VoidCallback? onTap;

  const SystemHealthIndicator({
    this.showDetails = false,
    this.onTap,
    super.key,
  });

  @override
  ConsumerState<SystemHealthIndicator> createState() =>
      _SystemHealthIndicatorState();
}

class _SystemHealthIndicatorState extends ConsumerState<SystemHealthIndicator>
    with TickerProviderStateMixin {
  late AnimationController _pulseController;
  late AnimationController _rotationController;
  late Animation<double> _pulseAnimation;
  late Animation<double> _rotationAnimation;

  Timer? _healthCheckTimer;
  SystemHealthLevel _currentHealth = SystemHealthLevel.unknown;
  String _healthMessage = '检查系统状态...';

  @override
  void initState() {
    super.initState();

    // 脉冲动画
    _pulseController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );
    _pulseAnimation = Tween<double>(begin: 0.8, end: 1.2).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    // 旋转动画（检查状态时使用）
    _rotationController = AnimationController(
      duration: const Duration(seconds: 1),
      vsync: this,
    );
    _rotationAnimation = Tween<double>(begin: 0, end: 2 * math.pi).animate(
      CurvedAnimation(parent: _rotationController, curve: Curves.linear),
    );

    _startHealthMonitoring();
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _rotationController.dispose();
    _healthCheckTimer?.cancel();
    super.dispose();
  }

  void _startHealthMonitoring() {
    // 立即检查一次
    _checkSystemHealth();

    // 定期检查
    _healthCheckTimer = Timer.periodic(
      const Duration(seconds: 10),
      (_) => _checkSystemHealth(),
    );
  }

  void _checkSystemHealth() {
    if (!mounted) return;

    // 开始检查动画
    _rotationController.repeat();

    final errorState = ref.read(appErrorProvider);
    final ipcConnection = ref.read(ipcConnectionProvider);

    // 计算健康度
    final health = _calculateHealth(errorState, ipcConnection.value);

    setState(() {
      _currentHealth = health.level;
      _healthMessage = health.message;
    });

    // 停止检查动画
    _rotationController.stop();
    _rotationController.reset();

    // 根据健康状态启动相应动画
    switch (_currentHealth) {
      case SystemHealthLevel.excellent:
        _pulseController.repeat(reverse: true);
        break;
      case SystemHealthLevel.critical:
        _pulseController.repeat(reverse: true);
        break;
      default:
        _pulseController.stop();
        _pulseController.reset();
    }
  }

  _HealthResult _calculateHealth(
      AppErrorState errorState, bool? isIPCConnected) {
    // IPC连接检查
    if (isIPCConnected == false) {
      return _HealthResult(
        level: SystemHealthLevel.critical,
        message: '无法连接到后端服务',
      );
    }

    // 严重错误检查
    if (errorState.hasCritical) {
      return _HealthResult(
        level: SystemHealthLevel.critical,
        message: '系统存在严重错误',
      );
    }

    // 网络和IPC错误检查
    if (errorState.hasNetwork || errorState.hasIPC) {
      return _HealthResult(
        level: SystemHealthLevel.warning,
        message: '网络连接不稳定',
      );
    }

    // 一般错误检查
    if (errorState.hasErrors) {
      final errorCount = errorState.activeErrors.length;
      if (errorCount > 5) {
        return _HealthResult(
          level: SystemHealthLevel.warning,
          message: '系统错误较多 ($errorCount 个)',
        );
      } else {
        return _HealthResult(
          level: SystemHealthLevel.good,
          message: '系统运行良好，有少量错误',
        );
      }
    }

    // 所有检查通过
    return _HealthResult(
      level: SystemHealthLevel.excellent,
      message: '系统运行正常',
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final healthInfo = _getHealthInfo(_currentHealth, theme);

    if (!widget.showDetails) {
      return _buildCompactIndicator(healthInfo);
    }

    return _buildDetailedIndicator(context, healthInfo);
  }

  Widget _buildCompactIndicator(_HealthInfo healthInfo) {
    return GestureDetector(
      onTap: widget.onTap,
      child: AnimatedBuilder(
        animation: Listenable.merge([_pulseAnimation, _rotationAnimation]),
        builder: (context, child) {
          return Transform.rotate(
            angle:
                _rotationController.isAnimating ? _rotationAnimation.value : 0,
            child: Transform.scale(
              scale: _pulseController.isAnimating ? _pulseAnimation.value : 1.0,
              child: Container(
                width: 24,
                height: 24,
                decoration: BoxDecoration(
                  color: healthInfo.color,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: healthInfo.color.withValues(alpha: 0.4),
                      blurRadius: 8,
                      spreadRadius: 2,
                    ),
                  ],
                ),
                child: Icon(
                  healthInfo.icon,
                  color: Colors.white,
                  size: 14,
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildDetailedIndicator(BuildContext context, _HealthInfo healthInfo) {
    final theme = Theme.of(context);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                AnimatedBuilder(
                  animation:
                      Listenable.merge([_pulseAnimation, _rotationAnimation]),
                  builder: (context, child) {
                    return Transform.rotate(
                      angle: _rotationController.isAnimating
                          ? _rotationAnimation.value
                          : 0,
                      child: Transform.scale(
                        scale: _pulseController.isAnimating
                            ? _pulseAnimation.value
                            : 1.0,
                        child: Container(
                          width: 32,
                          height: 32,
                          decoration: BoxDecoration(
                            color: healthInfo.color,
                            shape: BoxShape.circle,
                            boxShadow: [
                              BoxShadow(
                                color: healthInfo.color.withValues(alpha: 0.4),
                                blurRadius: 8,
                                spreadRadius: 2,
                              ),
                            ],
                          ),
                          child: Icon(
                            healthInfo.icon,
                            color: Colors.white,
                            size: 18,
                          ),
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        healthInfo.title,
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                          color: healthInfo.color,
                        ),
                      ),
                      Text(
                        _healthMessage,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ],
                  ),
                ),
                _buildQuickActions(),
              ],
            ),

            const SizedBox(height: 12),

            // 系统统计
            Consumer(
              builder: (context, ref, child) {
                final errorStats = ref.watch(errorStatsProvider);
                return _buildSystemStats(context, errorStats);
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActions() {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        // 刷新按钮
        IconButton(
          onPressed: _checkSystemHealth,
          icon: const Icon(Icons.refresh, size: 18),
          tooltip: '刷新系统状态',
          style: IconButton.styleFrom(
            padding: const EdgeInsets.all(8),
            minimumSize: const Size(32, 32),
          ),
        ),

        // 清理错误按钮
        Consumer(
          builder: (context, ref, child) {
            final hasErrors = ref.watch(appErrorProvider).hasErrors;
            return IconButton(
              onPressed: hasErrors
                  ? () {
                      ref.read(appErrorProvider.notifier).clearAllErrors();
                      showSuccessNotification(ref, '已清除所有错误');
                    }
                  : null,
              icon: Icon(
                Icons.clear_all,
                size: 18,
                color: hasErrors ? null : Colors.grey.shade400,
              ),
              tooltip: '清除所有错误',
              style: IconButton.styleFrom(
                padding: const EdgeInsets.all(8),
                minimumSize: const Size(32, 32),
              ),
            );
          },
        ),
      ],
    );
  }

  Widget _buildSystemStats(BuildContext context, Map<String, dynamic> stats) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: [
        _buildStatItem(
          context,
          '活跃错误',
          stats['total_errors'].toString(),
          Icons.error_outline,
          stats['total_errors'] > 0 ? Colors.orange : Colors.green,
        ),
        _buildStatItem(
          context,
          '严重问题',
          stats['critical_errors'].toString(),
          Icons.warning,
          stats['critical_errors'] > 0 ? Colors.red : Colors.green,
        ),
        _buildStatItem(
          context,
          '网络问题',
          stats['network_errors'].toString(),
          Icons.wifi_off,
          stats['network_errors'] > 0 ? Colors.orange : Colors.green,
        ),
      ],
    );
  }

  Widget _buildStatItem(
    BuildContext context,
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    final theme = Theme.of(context);

    return Column(
      children: [
        Icon(icon, size: 16, color: color),
        const SizedBox(height: 4),
        Text(
          value,
          style: theme.textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.w600,
            color: color,
          ),
        ),
        Text(
          label,
          style: theme.textTheme.bodySmall?.copyWith(
            fontSize: 10,
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
      ],
    );
  }

  _HealthInfo _getHealthInfo(SystemHealthLevel level, ThemeData theme) {
    switch (level) {
      case SystemHealthLevel.excellent:
        return _HealthInfo(
          color: Colors.green,
          icon: Icons.check_circle,
          title: '系统正常',
        );
      case SystemHealthLevel.good:
        return _HealthInfo(
          color: Colors.lightGreen,
          icon: Icons.check_circle_outline,
          title: '运行良好',
        );
      case SystemHealthLevel.warning:
        return _HealthInfo(
          color: Colors.orange,
          icon: Icons.warning,
          title: '需要注意',
        );
      case SystemHealthLevel.critical:
        return _HealthInfo(
          color: Colors.red,
          icon: Icons.error,
          title: '严重问题',
        );
      case SystemHealthLevel.unknown:
        return _HealthInfo(
          color: Colors.grey,
          icon: Icons.help_outline,
          title: '检查中...',
        );
    }
  }
}

class _HealthResult {
  final SystemHealthLevel level;
  final String message;

  _HealthResult({
    required this.level,
    required this.message,
  });
}

class _HealthInfo {
  final Color color;
  final IconData icon;
  final String title;

  _HealthInfo({
    required this.color,
    required this.icon,
    required this.title,
  });
}

/// 系统健康度悬浮按钮
class SystemHealthFAB extends ConsumerWidget {
  final VoidCallback? onTap;

  const SystemHealthFAB({
    this.onTap,
    super.key,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final errorState = ref.watch(appErrorProvider);

    // 如果没有错误，不显示FAB
    if (!errorState.hasErrors) return const SizedBox.shrink();

    return FloatingActionButton.small(
      heroTag: "systemHealthFAB",
      onPressed: onTap ?? () => _showHealthDetails(context, ref),
      backgroundColor: errorState.hasCritical ? Colors.red : Colors.orange,
      child: const SystemHealthIndicator(showDetails: false),
    );
  }

  void _showHealthDetails(BuildContext context, WidgetRef ref) {
    showBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: const SystemHealthIndicator(showDetails: true),
      ),
    );
  }
}
