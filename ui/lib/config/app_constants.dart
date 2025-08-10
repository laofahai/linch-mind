import 'package:flutter/material.dart';

/// 窗口配置常量
class AppWindowConstants {
  /// 默认窗口大小
  static const Size defaultSize = Size(1200, 800);

  /// 最小窗口大小
  static const Size minimumSize = Size(800, 600);

  /// 窗口透明度
  static const double backgroundAlpha = 0.0; // Colors.transparent
}

/// UI布局常量
class AppLayoutConstants {
  /// 标准内边距
  static const double padding = 16.0;
  static const double paddingSmall = 8.0;
  static const double paddingLarge = 24.0;

  /// 标准间距
  static const double spacing = 16.0;
  static const double spacingSmall = 8.0;
  static const double spacingLarge = 24.0;

  /// 圆角半径
  static const double borderRadius = 8.0;
  static const double borderRadiusLarge = 16.0;

  /// 网格布局配置
  static const double gridItemMinWidth = 300.0;
  static const double gridItemMaxWidth = 350.0;
  static const double gridChildAspectRatio = 4.2;
  static const double marketGridChildAspectRatio = 0.8;
  static const double gridCrossAxisSpacing = 16.0;
  static const double gridMainAxisSpacing = 16.0;

  /// 网格列数限制
  static const int gridMinColumns = 1;
  static const int gridMaxColumns = 4;

  /// 图标尺寸
  static const double iconSizeSmall = 16.0;
  static const double iconSizeNormal = 20.0;
  static const double iconSizeLarge = 32.0;
  static const double iconSizeExtraLarge = 64.0;
}

/// 动画配置常量
class AppAnimationConstants {
  /// 脉冲动画配置
  static const Duration pulseDuration = Duration(seconds: 2);
  static const double pulseBegin = 0.8;
  static const double pulseEnd = 1.0;

  /// 标准动画时长
  static const Duration shortDuration = Duration(milliseconds: 150);
  static const Duration normalDuration = Duration(milliseconds: 300);
  static const Duration longDuration = Duration(milliseconds: 500);
}

/// 颜色和透明度配置常量
class AppColorConstants {
  /// 标准透明度值
  static const double alphaLight = 0.05;
  static const double alphaLow = 0.1;
  static const double alphaMedium = 0.2;
  static const double alphaHigh = 0.3;
  static const double alphaOverlay = 0.5;
  static const double alphaSelected = 0.7;

  /// 状态指示器默认尺寸
  static const double statusIndicatorSize = 8.0;
}

/// 响应式设计断点常量
class AppBreakpointConstants {
  static const double mobile = 600.0;
  static const double tablet = 1024.0;
  static const double desktop = 1200.0;
}

/// 字体大小常量
class AppFontSizeConstants {
  static const double small = 12.0;
  static const double normal = 14.0;
  static const double medium = 16.0;
  static const double large = 18.0;
  static const double extraLarge = 24.0;
}

/// 错误监控配置常量
class AppErrorMonitorConstants {
  /// 错误弹窗尺寸比例
  static const double dialogWidthRatio = 0.8;
  static const double dialogHeightRatio = 0.7;
}

/// 网络和API配置常量
class AppNetworkConstants {
  /// 连接超时时间
  static const Duration connectionTimeout = Duration(seconds: 10);

  /// 重试次数
  static const int maxRetryAttempts = 3;

  /// 重试间隔
  static const Duration retryDelay = Duration(seconds: 1);
}

/// 表单配置常量
class AppFormConstants {
  /// 输入框内边距
  static const EdgeInsets inputPadding = EdgeInsets.symmetric(
    horizontal: 16.0,
    vertical: 12.0,
  );

  /// 表单验证延迟
  static const Duration validationDelay = Duration(milliseconds: 500);
}

/// 扩展方法，提供便捷的访问方式
extension AppConstantsExtension on BuildContext {
  /// 获取屏幕尺寸
  Size get screenSize => MediaQuery.of(this).size;

  /// 检查是否为移动端
  bool get isMobile => screenSize.width < AppBreakpointConstants.mobile;

  /// 检查是否为平板端
  bool get isTablet =>
      screenSize.width >= AppBreakpointConstants.mobile &&
      screenSize.width < AppBreakpointConstants.desktop;

  /// 检查是否为桌面端
  bool get isDesktop => screenSize.width >= AppBreakpointConstants.desktop;

  /// 根据屏幕宽度计算网格列数
  int calculateGridColumns({
    double itemMinWidth = AppLayoutConstants.gridItemMinWidth,
  }) {
    return (screenSize.width / itemMinWidth).floor().clamp(
          AppLayoutConstants.gridMinColumns,
          AppLayoutConstants.gridMaxColumns,
        );
  }
}
