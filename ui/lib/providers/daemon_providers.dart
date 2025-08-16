import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/daemon_lifecycle_service.dart';
import '../services/daemon_port_service.dart';
import '../core/ui_service_facade.dart';
import 'base_state_notifier.dart';

/// Daemon状态数据类
class DaemonState implements BaseState {
  final bool isRunning;
  final RunMode mode;
  final DaemonInfo? daemonInfo;
  final String? error;
  @override
  final bool isLoading;
  @override
  final DateTime lastUpdate;

  const DaemonState({
    required this.isRunning,
    required this.mode,
    this.daemonInfo,
    this.error,
    this.isLoading = false,
    required this.lastUpdate,
  });

  @override
  String? get errorMessage => error;

  @override
  bool get hasError => error != null;

  DaemonState copyWith({
    bool? isRunning,
    RunMode? mode,
    DaemonInfo? daemonInfo,
    String? error,
    bool? isLoading,
    DateTime? lastUpdate,
    bool clearError = false,
  }) {
    return DaemonState(
      isRunning: isRunning ?? this.isRunning,
      mode: mode ?? this.mode,
      daemonInfo: daemonInfo ?? this.daemonInfo,
      error: clearError ? null : (error ?? this.error),
      isLoading: isLoading ?? this.isLoading,
      lastUpdate: lastUpdate ?? this.lastUpdate,
    );
  }
}

/// Daemon状态管理器
class DaemonStateNotifier extends BaseStateNotifier<DaemonState> {
  DaemonStateNotifier()
      : super(DaemonState(
          isRunning: false,
          mode: getService<DaemonLifecycleService>().runMode,
          lastUpdate: DateTime.now(),
        )) {
    _initialize();
  }

  final DaemonLifecycleService _lifecycleService =
      getService<DaemonLifecycleService>();
  final DaemonPortService _portService = getService<DaemonPortService>();

  /// 初始化状态
  Future<void> _initialize() async {
    await refreshStatus();
  }

  /// 刷新daemon状态
  Future<void> refreshStatus() async {
    setLoading(true);
    clearError();

    try {
      final daemonInfo = await _portService.discoverDaemon();
      final isRunning = daemonInfo?.isAccessible ?? false;

      state = state.copyWith(
        isRunning: isRunning,
        daemonInfo: daemonInfo,
        isLoading: false,
        lastUpdate: DateTime.now(),
      );
    } catch (e) {
      state = state.copyWith(
        isRunning: false,
        isLoading: false,
        lastUpdate: DateTime.now(),
      );
      handleError(e.toString());
    }
  }

  /// 启动daemon
  Future<bool> startDaemon() async {
    if (state.mode == RunMode.production) {
      handleError('生产模式下不支持手动启动daemon');
      return false;
    }

    setLoading(true);
    clearError();

    try {
      final result = await _lifecycleService.ensureDaemonRunning();

      if (result.success) {
        state = state.copyWith(
          isRunning: true,
          daemonInfo: result.daemonInfo,
          isLoading: false,
          lastUpdate: DateTime.now(),
        );
        return true;
      } else {
        state = state.copyWith(
          isRunning: false,
          isLoading: false,
          lastUpdate: DateTime.now(),
        );
        handleError(result.error ?? 'Daemon启动失败');
        return false;
      }
    } catch (e) {
      state = state.copyWith(
        isRunning: false,
        isLoading: false,
        lastUpdate: DateTime.now(),
      );
      handleError(e.toString());
      return false;
    }
  }

  /// 停止daemon
  Future<bool> stopDaemon() async {
    if (state.mode == RunMode.production) {
      handleError('生产模式下不支持手动停止daemon');
      return false;
    }

    setLoading(true);
    clearError();

    try {
      final success = await _lifecycleService.stopDaemon();

      if (success) {
        state = state.copyWith(
          isRunning: false,
          daemonInfo: null,
          isLoading: false,
          lastUpdate: DateTime.now(),
        );
        return true;
      } else {
        state = state.copyWith(
          isLoading: false,
          lastUpdate: DateTime.now(),
        );
        handleError('停止daemon失败');
        return false;
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        lastUpdate: DateTime.now(),
      );
      handleError(e.toString());
      return false;
    }
  }

  /// 重启daemon
  Future<bool> restartDaemon() async {
    if (state.mode == RunMode.production) {
      handleError('生产模式下不支持重启daemon');
      return false;
    }

    setLoading(true);
    clearError();

    try {
      final result = await _lifecycleService.restartDaemon();

      if (result.success) {
        state = state.copyWith(
          isRunning: true,
          daemonInfo: result.daemonInfo,
          isLoading: false,
          lastUpdate: DateTime.now(),
        );
        return true;
      } else {
        state = state.copyWith(
          isRunning: false,
          isLoading: false,
          lastUpdate: DateTime.now(),
        );
        handleError(result.error ?? '重启daemon失败');
        return false;
      }
    } catch (e) {
      state = state.copyWith(
        isRunning: false,
        isLoading: false,
        lastUpdate: DateTime.now(),
      );
      handleError(e.toString());
      return false;
    }
  }

  @override
  DaemonState updateStateWithError(String error) {
    return state.copyWith(
      error: error,
      isLoading: false,
      lastUpdate: DateTime.now(),
    );
  }

  @override
  DaemonState updateStateWithClearError() {
    return state.copyWith(
      clearError: true,
      lastUpdate: DateTime.now(),
    );
  }

  @override
  DaemonState updateStateWithLoading(bool loading) {
    return state.copyWith(
      isLoading: loading,
      lastUpdate: DateTime.now(),
    );
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
