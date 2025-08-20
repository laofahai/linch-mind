import 'package:flutter/material.dart';

class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  static const Duration _defaultDuration = Duration(seconds: 3);
  static const Duration _longDuration = Duration(seconds: 5);

  void showSuccess(
    BuildContext context,
    String message, {
    Duration? duration,
    bool dismissPrevious = true,
  }) {
    _showSnackBar(
      context,
      message,
      backgroundColor: Theme.of(context).colorScheme.primaryContainer,
      textColor: Theme.of(context).colorScheme.onPrimaryContainer,
      icon: Icons.check_circle_outline,
      duration: duration ?? _defaultDuration,
      dismissPrevious: dismissPrevious,
    );
  }

  void showError(
    BuildContext context,
    String message, {
    Duration? duration,
    bool dismissPrevious = true,
  }) {
    _showSnackBar(
      context,
      message,
      backgroundColor: Theme.of(context).colorScheme.errorContainer,
      textColor: Theme.of(context).colorScheme.onErrorContainer,
      icon: Icons.error_outline,
      duration: duration ?? _longDuration,
      dismissPrevious: dismissPrevious,
    );
  }

  void showWarning(
    BuildContext context,
    String message, {
    Duration? duration,
    bool dismissPrevious = true,
  }) {
    _showSnackBar(
      context,
      message,
      backgroundColor: Theme.of(context).colorScheme.tertiaryContainer,
      textColor: Theme.of(context).colorScheme.onTertiaryContainer,
      icon: Icons.warning_amber_outlined,
      duration: duration ?? _defaultDuration,
      dismissPrevious: dismissPrevious,
    );
  }

  void showInfo(
    BuildContext context,
    String message, {
    Duration? duration,
    bool dismissPrevious = true,
  }) {
    _showSnackBar(
      context,
      message,
      backgroundColor: Theme.of(context).colorScheme.secondaryContainer,
      textColor: Theme.of(context).colorScheme.onSecondaryContainer,
      icon: Icons.info_outline,
      duration: duration ?? _defaultDuration,
      dismissPrevious: dismissPrevious,
    );
  }

  void _showSnackBar(
    BuildContext context,
    String message, {
    required Color backgroundColor,
    required Color textColor,
    required IconData icon,
    required Duration duration,
    required bool dismissPrevious,
  }) {
    if (dismissPrevious) {
      ScaffoldMessenger.of(context).clearSnackBars();
    }

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(
              icon,
              color: textColor,
              size: 20,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                message,
                style: TextStyle(
                  color: textColor,
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ],
        ),
        backgroundColor: backgroundColor,
        duration: duration,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        margin: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        action: SnackBarAction(
          label: '关闭',
          textColor: textColor.withValues(alpha: 0.8),
          onPressed: () {
            ScaffoldMessenger.of(context).hideCurrentSnackBar();
          },
        ),
      ),
    );
  }

  void clearAll(BuildContext context) {
    ScaffoldMessenger.of(context).clearSnackBars();
  }
}
