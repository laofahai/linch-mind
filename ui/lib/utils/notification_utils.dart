import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/notification_provider.dart';

/// 显示成功通知
void showSuccessNotification(
  WidgetRef ref,
  String message, {
  Duration? duration,
  bool clearPrevious = true,
}) {
  if (clearPrevious) {
    ref.read(notificationProvider.notifier).clearAll();
  }
  ref.read(notificationProvider.notifier).showSuccess(message, duration: duration);
}

/// 显示错误通知
void showErrorNotification(
  WidgetRef ref,
  String message, {
  Duration? duration,
  bool clearPrevious = true,
}) {
  if (clearPrevious) {
    ref.read(notificationProvider.notifier).clearAll();
  }
  ref.read(notificationProvider.notifier).showError(message, duration: duration);
}

/// 显示警告通知
void showWarningNotification(
  WidgetRef ref,
  String message, {
  Duration? duration,
  bool clearPrevious = true,
}) {
  if (clearPrevious) {
    ref.read(notificationProvider.notifier).clearAll();
  }
  ref.read(notificationProvider.notifier).showWarning(message, duration: duration);
}

/// 显示信息通知
void showInfoNotification(
  WidgetRef ref,
  String message, {
  Duration? duration,
  bool clearPrevious = true,
}) {
  if (clearPrevious) {
    ref.read(notificationProvider.notifier).clearAll();
  }
  ref.read(notificationProvider.notifier).showInfo(message, duration: duration);
}

/// 通知工具类 - 提供便捷的通知方法
class NotificationUtils {
  /// 显示成功通知
  static void showSuccess(
    WidgetRef ref,
    String message, {
    Duration? duration,
    bool clearPrevious = true,
  }) {
    showSuccessNotification(ref, message, duration: duration, clearPrevious: clearPrevious);
  }

  /// 显示错误通知
  static void showError(
    WidgetRef ref,
    String message, {
    Duration? duration,
    bool clearPrevious = true,
  }) {
    showErrorNotification(ref, message, duration: duration, clearPrevious: clearPrevious);
  }

  /// 显示警告通知
  static void showWarning(
    WidgetRef ref,
    String message, {
    Duration? duration,
    bool clearPrevious = true,
  }) {
    showWarningNotification(ref, message, duration: duration, clearPrevious: clearPrevious);
  }

  /// 显示信息通知
  static void showInfo(
    WidgetRef ref,
    String message, {
    Duration? duration,
    bool clearPrevious = true,
  }) {
    showInfoNotification(ref, message, duration: duration, clearPrevious: clearPrevious);
  }

  /// 清除所有通知
  static void clearAll(WidgetRef ref) {
    ref.read(notificationProvider.notifier).clearAll();
  }
}

/// 在StatelessWidget中使用的通知扩展
extension NotificationExtensions on WidgetRef {
  void showSuccess(String message, {Duration? duration, bool clearPrevious = true}) {
    NotificationUtils.showSuccess(this, message, duration: duration, clearPrevious: clearPrevious);
  }

  void showError(String message, {Duration? duration, bool clearPrevious = true}) {
    NotificationUtils.showError(this, message, duration: duration, clearPrevious: clearPrevious);
  }

  void showWarning(String message, {Duration? duration, bool clearPrevious = true}) {
    NotificationUtils.showWarning(this, message, duration: duration, clearPrevious: clearPrevious);
  }

  void showInfo(String message, {Duration? duration, bool clearPrevious = true}) {
    NotificationUtils.showInfo(this, message, duration: duration, clearPrevious: clearPrevious);
  }

  void clearNotifications() {
    NotificationUtils.clearAll(this);
  }
}

/// 兼容旧的ScaffoldMessenger.showSnackBar调用的工具方法
/// 在迁移过程中使用，逐步替换为新的通知系统
@Deprecated('使用 NotificationUtils 替代')
void showSnackBarCompat(
  BuildContext context,
  WidgetRef ref,
  String message, {
  Color? backgroundColor,
  Duration? duration,
}) {
  if (backgroundColor != null) {
    // 根据背景色判断通知类型
    final theme = Theme.of(context);
    if (backgroundColor == Colors.green || backgroundColor == theme.colorScheme.primaryContainer) {
      NotificationUtils.showSuccess(ref, message, duration: duration);
    } else if (backgroundColor == Colors.red || backgroundColor == theme.colorScheme.errorContainer) {
      NotificationUtils.showError(ref, message, duration: duration);
    } else if (backgroundColor == Colors.orange || backgroundColor == theme.colorScheme.tertiaryContainer) {
      NotificationUtils.showWarning(ref, message, duration: duration);
    } else {
      NotificationUtils.showInfo(ref, message, duration: duration);
    }
  } else {
    NotificationUtils.showInfo(ref, message, duration: duration);
  }
}