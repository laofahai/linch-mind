import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/daemon_lifecycle_service.dart';
import '../services/daemon_port_service.dart';

/// Daemon状态数据类
class DaemonState {
  final bool isRunning;
  final RunMode mode;
  final DaemonInfo? daemonInfo;
  final String? error;
  final bool isLoading;

  const DaemonState({
    required this.isRunning,
    required this.mode,
    this.daemonInfo,
    this.error,
    this.isLoading = false,
  });

  DaemonState copyWith({
    bool? isRunning,
    RunMode? mode,
    DaemonInfo? daemonInfo,
    String? error,
    bool? isLoading,
  }) {
    return DaemonState(
      isRunning: isRunning ?? this.isRunning,
      mode: mode ?? this.mode,
      daemonInfo: daemonInfo ?? this.daemonInfo,
      error: error ?? this.error,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

/// Daemon状态管理器
class DaemonStateNotifier extends StateNotifier<DaemonState> {
  DaemonStateNotifier()
      : super(DaemonState(
          isRunning: false,
          mode: DaemonLifecycleService.instance.runMode,
        )) {
    _initialize();
  }

  final DaemonLifecycleService _lifecycleService =
      DaemonLifecycleService.instance;
  final DaemonPortService _portService = DaemonPortService.instance;

  /// 初始化状态
  Future<void> _initialize() async {
    await refreshStatus();
  }

  /// 刷新daemon状态
  Future<void> refreshStatus() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final daemonInfo = await _portService.discoverDaemon();
      final isRunning = daemonInfo?.isAccessible ?? false;

      state = state.copyWith(
        isRunning: isRunning,
        daemonInfo: daemonInfo,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isRunning: false,
        error: e.toString(),
        isLoading: false,
      );
    }
  }

  /// 启动daemon
  Future<bool> startDaemon() async {
    if (state.mode == RunMode.production) {
      state = state.copyWith(error: '生产模式下不支持手动启动daemon');
      return false;
    }

    state = state.copyWith(isLoading: true, error: null);

    try {
      final result = await _lifecycleService.ensureDaemonRunning();

      if (result.success) {
        state = state.copyWith(
          isRunning: true,
          daemonInfo: result.daemonInfo,
          isLoading: false,
        );
        return true;
      } else {
        state = state.copyWith(
          isRunning: false,
          error: result.error,
          isLoading: false,
        );
        return false;
      }
    } catch (e) {
      state = state.copyWith(
        isRunning: false,
        error: e.toString(),
        isLoading: false,
      );
      return false;
    }
  }

  /// 停止daemon
  Future<bool> stopDaemon() async {
    if (state.mode == RunMode.production) {
      state = state.copyWith(error: '生产模式下不支持手动停止daemon');
      return false;
    }

    state = state.copyWith(isLoading: true, error: null);

    try {
      final success = await _lifecycleService.stopDaemon();

      if (success) {
        state = state.copyWith(
          isRunning: false,
          daemonInfo: null,
          isLoading: false,
        );
        return true;
      } else {
        state = state.copyWith(
          error: '停止daemon失败',
          isLoading: false,
        );
        return false;
      }
    } catch (e) {
      state = state.copyWith(
        error: e.toString(),
        isLoading: false,
      );
      return false;
    }
  }

  /// 重启daemon
  Future<bool> restartDaemon() async {
    if (state.mode == RunMode.production) {
      state = state.copyWith(error: '生产模式下不支持重启daemon');
      return false;
    }

    state = state.copyWith(isLoading: true, error: null);

    try {
      final result = await _lifecycleService.restartDaemon();

      if (result.success) {
        state = state.copyWith(
          isRunning: true,
          daemonInfo: result.daemonInfo,
          isLoading: false,
        );
        return true;
      } else {
        state = state.copyWith(
          isRunning: false,
          error: result.error,
          isLoading: false,
        );
        return false;
      }
    } catch (e) {
      state = state.copyWith(
        isRunning: false,
        error: e.toString(),
        isLoading: false,
      );
      return false;
    }
  }

  /// 清除错误
  void clearError() {
    state = state.copyWith(error: null);
  }
}

/// Daemon状态provider
final daemonStateProvider =
    StateNotifierProvider<DaemonStateNotifier, DaemonState>((ref) {
  return DaemonStateNotifier();
});

/// 简化的状态访问器
final daemonRunningProvider = Provider<bool>((ref) {
  return ref.watch(daemonStateProvider).isRunning;
});

final daemonModeProvider = Provider<RunMode>((ref) {
  return ref.watch(daemonStateProvider).mode;
});

final daemonErrorProvider = Provider<String?>((ref) {
  return ref.watch(daemonStateProvider).error;
});
