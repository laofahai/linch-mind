import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/daemon_lifecycle_service.dart';
import '../services/daemon_port_service.dart';

/// 应用初始化状态
enum InitializationState {
  checking,
  startingDaemon,
  connecting,
  ready,
  error,
}

/// 初始化状态提供者
final initializationStateProvider =
    StateNotifierProvider<InitializationNotifier, InitializationState>((ref) {
  return InitializationNotifier();
});

/// 初始化错误信息提供者
final initializationErrorProvider = StateProvider<String?>((ref) => null);

/// 初始化状态管理器
class InitializationNotifier extends StateNotifier<InitializationState> {
  InitializationNotifier() : super(InitializationState.checking);

  void setState(InitializationState newState) {
    state = newState;
  }
}

/// 应用初始化屏幕
class AppInitializationScreen extends ConsumerStatefulWidget {
  const AppInitializationScreen({super.key});

  @override
  ConsumerState<AppInitializationScreen> createState() =>
      _AppInitializationScreenState();
}

class _AppInitializationScreenState
    extends ConsumerState<AppInitializationScreen> {
  final DaemonLifecycleService _lifecycleService =
      DaemonLifecycleService.instance;

  @override
  void initState() {
    super.initState();
    _initializeApp();
  }

  /// 初始化应用
  Future<void> _initializeApp() async {
    try {
      // 1. 检查daemon状态
      ref
          .read(initializationStateProvider.notifier)
          .setState(InitializationState.checking);
      await Future.delayed(const Duration(milliseconds: 500)); // 让用户看到检查状态

      // 2. 确保daemon运行
      ref
          .read(initializationStateProvider.notifier)
          .setState(InitializationState.startingDaemon);
      final startResult = await _lifecycleService.ensureDaemonRunning();

      if (!startResult.success) {
        _setError(startResult.error ?? '启动daemon失败');
        return;
      }

      // 3. 验证连接
      ref
          .read(initializationStateProvider.notifier)
          .setState(InitializationState.connecting);
      await Future.delayed(const Duration(milliseconds: 500));

      final portService = DaemonPortService.instance;
      final isReachable = await portService.isDaemonReachable();

      if (!isReachable) {
        _setError('无法连接到daemon服务');
        return;
      }

      // 4. 初始化完成
      ref
          .read(initializationStateProvider.notifier)
          .setState(InitializationState.ready);

      // 延迟一下让用户看到成功状态
      await Future.delayed(const Duration(milliseconds: 1000));
    } catch (e) {
      _setError('初始化失败: $e');
    }
  }

  /// 设置错误状态
  void _setError(String error) {
    ref.read(initializationErrorProvider.notifier).state = error;
    ref
        .read(initializationStateProvider.notifier)
        .setState(InitializationState.error);
  }

  /// 重试初始化
  Future<void> _retry() async {
    ref.read(initializationErrorProvider.notifier).state = null;
    await _initializeApp();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(initializationStateProvider);
    final error = ref.watch(initializationErrorProvider);
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      backgroundColor: colorScheme.surface,
      body: Center(
        child: Card(
          margin: const EdgeInsets.all(32),
          child: Padding(
            padding: const EdgeInsets.all(48),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Logo/图标
                Icon(
                  Icons.psychology,
                  size: 64,
                  color: colorScheme.primary,
                ),
                const SizedBox(height: 24),

                // 应用标题
                Text(
                  'Linch Mind',
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        color: colorScheme.primary,
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 8),

                Text(
                  '个人AI生活助手',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: colorScheme.onSurface.withValues(alpha: 0.7),
                      ),
                ),
                const SizedBox(height: 32),

                // 状态指示器
                _buildStateIndicator(context, state),
                const SizedBox(height: 16),

                // 状态文本
                _buildStateText(context, state, error),
                const SizedBox(height: 32),

                // 错误重试按钮
                if (state == InitializationState.error)
                  Column(
                    children: [
                      ElevatedButton.icon(
                        onPressed: _retry,
                        icon: const Icon(Icons.refresh),
                        label: const Text('重试'),
                      ),
                      const SizedBox(height: 16),
                      TextButton(
                        onPressed: () => _showDebugInfo(context),
                        child: const Text('查看详细信息'),
                      ),
                    ],
                  ),

                // 运行模式指示
                _buildModeIndicator(context),
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// 构建状态指示器
  Widget _buildStateIndicator(BuildContext context, InitializationState state) {
    final colorScheme = Theme.of(context).colorScheme;

    switch (state) {
      case InitializationState.checking:
      case InitializationState.startingDaemon:
      case InitializationState.connecting:
        return SizedBox(
          width: 48,
          height: 48,
          child: CircularProgressIndicator(
            strokeWidth: 3,
            color: colorScheme.primary,
          ),
        );

      case InitializationState.ready:
        return Icon(
          Icons.check_circle,
          size: 48,
          color: colorScheme.primary,
        );

      case InitializationState.error:
        return Icon(
          Icons.error,
          size: 48,
          color: colorScheme.error,
        );
    }
  }

  /// 构建状态文本
  Widget _buildStateText(
      BuildContext context, InitializationState state, String? error) {
    final textStyle = Theme.of(context).textTheme.bodyLarge;
    final colorScheme = Theme.of(context).colorScheme;

    String text;
    Color? color;

    switch (state) {
      case InitializationState.checking:
        text = '检查系统状态...';
        break;
      case InitializationState.startingDaemon:
        text = '启动AI服务...';
        break;
      case InitializationState.connecting:
        text = '建立连接...';
        break;
      case InitializationState.ready:
        text = '准备就绪';
        color = colorScheme.primary;
        break;
      case InitializationState.error:
        text = error ?? '初始化失败';
        color = colorScheme.error;
        break;
    }

    return Text(
      text,
      style: textStyle?.copyWith(color: color),
      textAlign: TextAlign.center,
    );
  }

  /// 构建运行模式指示器
  Widget _buildModeIndicator(BuildContext context) {
    final mode = _lifecycleService.runMode;
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      margin: const EdgeInsets.only(top: 24),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: mode == RunMode.development
            ? colorScheme.primaryContainer
            : colorScheme.secondaryContainer,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Text(
        mode == RunMode.development ? '开发模式' : '生产模式',
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: mode == RunMode.development
                  ? colorScheme.onPrimaryContainer
                  : colorScheme.onSecondaryContainer,
              fontWeight: FontWeight.w500,
            ),
      ),
    );
  }

  /// 显示调试信息
  void _showDebugInfo(BuildContext context) async {
    final status = await _lifecycleService.getDaemonStatus();

    if (!mounted) return;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('系统状态'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildDebugItem('运行模式', status['mode']),
              _buildDebugItem('Daemon运行', status['running'].toString()),
              if (status['daemon_info'] != null) ...[
                _buildDebugItem(
                    'Socket路径', status['daemon_info']['socket_path']),
                _buildDebugItem('通信方式', status['daemon_info']['socket_type']),
                _buildDebugItem(
                    '进程ID', status['daemon_info']['pid'].toString()),
              ],
              _buildDebugItem(
                  '开发进程', status['development_process_running'].toString()),
              _buildDebugItem('健康检查', status['health_check_active'].toString()),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('关闭'),
          ),
        ],
      ),
    );
  }

  /// 构建调试信息项
  Widget _buildDebugItem(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          Expanded(
            child: Text(value),
          ),
        ],
      ),
    );
  }
}
