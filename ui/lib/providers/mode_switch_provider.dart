import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'mode_switch_provider.freezed.dart';

/// 应用模式枚举
enum AppMode {
  daily('日常', '平衡工作与生活，智能安排任务，轻松高效的日常节奏。', Colors.blue),
  focus('专注', '屏蔽干扰，专心致志，进入深度工作状态，高效完成重要任务。', Colors.orange),
  rest('休息', '放松身心，缓解疲劳，智能提醒活动，保持健康作息。', Colors.green),
  evening('晚间', '温和护眼，智能调节，为您营造舒适的夜间使用环境。', Colors.indigo);

  const AppMode(this.displayName, this.description, this.color);
  
  final String displayName;
  final String description;
  final Color color;

  /// 获取模式图标
  IconData get icon {
    switch (this) {
      case AppMode.daily:
        return Icons.wb_sunny_outlined;
      case AppMode.focus:
        return Icons.center_focus_strong;
      case AppMode.rest:
        return Icons.spa_outlined;
      case AppMode.evening:
        return Icons.dark_mode_outlined;
    }
  }

  /// 获取模式状态文本
  String get statusText => '${displayName}模式已激活';
}

/// 模式切换状态
@freezed
class ModeSwitchState with _$ModeSwitchState {
  const factory ModeSwitchState({
    @Default(AppMode.daily) AppMode currentMode,
    @Default(false) bool isTransitioning,
    DateTime? lastSwitchTime,
    Map<AppMode, DateTime>? modeUsageStats,
  }) = _ModeSwitchState;
}

/// 模式切换 Provider
final modeSwitchProvider = StateNotifierProvider<ModeSwitchNotifier, ModeSwitchState>(
  (ref) => ModeSwitchNotifier(),
);

/// 模式切换状态管理器
class ModeSwitchNotifier extends StateNotifier<ModeSwitchState> {
  ModeSwitchNotifier() : super(const ModeSwitchState()) {
    _initializeMode();
  }

  /// 初始化模式（根据时间自动判断）
  void _initializeMode() {
    final now = DateTime.now();
    final hour = now.hour;
    
    AppMode initialMode;
    if (hour >= 6 && hour < 12) {
      initialMode = AppMode.daily;
    } else if (hour >= 12 && hour < 18) {
      initialMode = AppMode.focus;
    } else if (hour >= 18 && hour < 22) {
      initialMode = AppMode.rest;
    } else {
      initialMode = AppMode.evening;
    }
    
    state = state.copyWith(
      currentMode: initialMode,
      lastSwitchTime: now,
    );
  }

  /// 切换到指定模式
  Future<void> switchToMode(AppMode mode) async {
    if (state.currentMode == mode || state.isTransitioning) return;

    state = state.copyWith(isTransitioning: true);
    
    // 模拟切换过程
    await Future.delayed(const Duration(milliseconds: 800));
    
    final now = DateTime.now();
    final updatedStats = Map<AppMode, DateTime>.from(state.modeUsageStats ?? {});
    updatedStats[mode] = now;
    
    state = state.copyWith(
      currentMode: mode,
      isTransitioning: false,
      lastSwitchTime: now,
      modeUsageStats: updatedStats,
    );
  }

  /// 获取模式使用统计
  Duration getModeUsageDuration(AppMode mode) {
    final stats = state.modeUsageStats;
    if (stats == null || !stats.containsKey(mode)) {
      return Duration.zero;
    }
    
    return DateTime.now().difference(stats[mode]!);
  }

  /// 自动切换模式（基于时间）
  void autoSwitchMode() {
    final now = DateTime.now();
    final hour = now.hour;
    
    AppMode suggestedMode;
    if (hour >= 6 && hour < 12) {
      suggestedMode = AppMode.daily;
    } else if (hour >= 12 && hour < 18) {
      suggestedMode = AppMode.focus;
    } else if (hour >= 18 && hour < 22) {
      suggestedMode = AppMode.rest;
    } else {
      suggestedMode = AppMode.evening;
    }
    
    if (suggestedMode != state.currentMode) {
      switchToMode(suggestedMode);
    }
  }

  /// 获取推荐的下一个模式
  AppMode? getRecommendedNextMode() {
    final now = DateTime.now();
    final hour = now.hour;
    final currentMode = state.currentMode;
    
    // 基于时间和当前模式推荐下一个模式
    switch (currentMode) {
      case AppMode.daily:
        if (hour >= 12) return AppMode.focus;
        break;
      case AppMode.focus:
        if (hour >= 18) return AppMode.rest;
        break;
      case AppMode.rest:
        if (hour >= 22) return AppMode.evening;
        break;
      case AppMode.evening:
        if (hour >= 6 && hour < 12) return AppMode.daily;
        break;
    }
    
    return null;
  }
}