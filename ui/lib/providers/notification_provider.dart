import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/material.dart';

enum NotificationType { success, error, warning, info }

class NotificationMessage {
  final String id;
  final String message;
  final NotificationType type;
  final DateTime timestamp;
  final Duration duration;

  const NotificationMessage({
    required this.id,
    required this.message,
    required this.type,
    required this.timestamp,
    this.duration = const Duration(seconds: 3),
  });

  IconData get icon {
    switch (type) {
      case NotificationType.success:
        return Icons.check_circle_outline;
      case NotificationType.error:
        return Icons.error_outline;
      case NotificationType.warning:
        return Icons.warning_amber_outlined;
      case NotificationType.info:
        return Icons.info_outline;
    }
  }

  Color getBackgroundColor(ColorScheme colorScheme) {
    switch (type) {
      case NotificationType.success:
        return colorScheme.primaryContainer;
      case NotificationType.error:
        return colorScheme.errorContainer;
      case NotificationType.warning:
        return colorScheme.tertiaryContainer;
      case NotificationType.info:
        return colorScheme.secondaryContainer;
    }
  }

  Color getTextColor(ColorScheme colorScheme) {
    switch (type) {
      case NotificationType.success:
        return colorScheme.onPrimaryContainer;
      case NotificationType.error:
        return colorScheme.onErrorContainer;
      case NotificationType.warning:
        return colorScheme.onTertiaryContainer;
      case NotificationType.info:
        return colorScheme.onSecondaryContainer;
    }
  }
}

class NotificationState {
  final List<NotificationMessage> notifications;
  final NotificationMessage? currentNotification;

  const NotificationState({
    this.notifications = const [],
    this.currentNotification,
  });

  NotificationState copyWith({
    List<NotificationMessage>? notifications,
    NotificationMessage? currentNotification,
  }) {
    return NotificationState(
      notifications: notifications ?? this.notifications,
      currentNotification: currentNotification ?? this.currentNotification,
    );
  }
}

class NotificationNotifier extends StateNotifier<NotificationState> {
  NotificationNotifier() : super(const NotificationState());

  void showNotification(
    String message,
    NotificationType type, {
    Duration? duration,
    bool clearPrevious = true,
  }) {
    final notification = NotificationMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      message: message,
      type: type,
      timestamp: DateTime.now(),
      duration: duration ?? const Duration(seconds: 3),
    );

    if (clearPrevious) {
      state = NotificationState(
        notifications: [notification],
        currentNotification: notification,
      );
    } else {
      state = state.copyWith(
        notifications: [...state.notifications, notification],
        currentNotification: notification,
      );
    }

    // 自动移除通知
    Future.delayed(notification.duration, () {
      removeNotification(notification.id);
    });
  }

  void removeNotification(String id) {
    final updatedNotifications = state.notifications.where((n) => n.id != id).toList();
    
    state = state.copyWith(
      notifications: updatedNotifications,
      currentNotification: updatedNotifications.isNotEmpty ? updatedNotifications.last : null,
    );
  }

  void clearAll() {
    state = const NotificationState();
  }

  // 便捷方法
  void showSuccess(String message, {Duration? duration, bool clearPrevious = true}) {
    showNotification(message, NotificationType.success, duration: duration, clearPrevious: clearPrevious);
  }

  void showError(String message, {Duration? duration, bool clearPrevious = true}) {
    showNotification(message, NotificationType.error, duration: duration, clearPrevious: clearPrevious);
  }

  void showWarning(String message, {Duration? duration, bool clearPrevious = true}) {
    showNotification(message, NotificationType.warning, duration: duration, clearPrevious: clearPrevious);
  }

  void showInfo(String message, {Duration? duration, bool clearPrevious = true}) {
    showNotification(message, NotificationType.info, duration: duration, clearPrevious: clearPrevious);
  }
}

final notificationProvider = StateNotifierProvider<NotificationNotifier, NotificationState>((ref) {
  return NotificationNotifier();
});

// 便捷的全局通知方法
void showSuccessNotification(WidgetRef ref, String message, {Duration? duration, bool clearPrevious = true}) {
  ref.read(notificationProvider.notifier).showSuccess(message, duration: duration, clearPrevious: clearPrevious);
}

void showErrorNotification(WidgetRef ref, String message, {Duration? duration, bool clearPrevious = true}) {
  ref.read(notificationProvider.notifier).showError(message, duration: duration, clearPrevious: clearPrevious);
}

void showWarningNotification(WidgetRef ref, String message, {Duration? duration, bool clearPrevious = true}) {
  ref.read(notificationProvider.notifier).showWarning(message, duration: duration, clearPrevious: clearPrevious);
}

void showInfoNotification(WidgetRef ref, String message, {Duration? duration, bool clearPrevious = true}) {
  ref.read(notificationProvider.notifier).showInfo(message, duration: duration, clearPrevious: clearPrevious);
}