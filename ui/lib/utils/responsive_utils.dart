import 'package:flutter/material.dart';

/// 响应式设计工具类
class ResponsiveUtils {
  /// 屏幕断点
  static const double mobileBreakpoint = 600;
  static const double tabletBreakpoint = 900;
  static const double desktopBreakpoint = 1200;

  /// 获取设备类型
  static DeviceType getDeviceType(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    
    if (width < mobileBreakpoint) {
      return DeviceType.mobile;
    } else if (width < tabletBreakpoint) {
      return DeviceType.tablet;
    } else {
      return DeviceType.desktop;
    }
  }

  /// 获取消息最大宽度
  static double getMessageMaxWidth(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final deviceType = getDeviceType(context);
    
    switch (deviceType) {
      case DeviceType.mobile:
        return screenWidth * 0.85; // 85%的屏幕宽度
      case DeviceType.tablet:
        return screenWidth * 0.7;  // 70%的屏幕宽度
      case DeviceType.desktop:
        return 600; // 固定最大宽度600px
    }
  }

  /// 获取推荐网格列数
  static int getRecommendationColumns(BuildContext context) {
    final deviceType = getDeviceType(context);
    
    switch (deviceType) {
      case DeviceType.mobile:
        return 2;
      case DeviceType.tablet:
        return 3;
      case DeviceType.desktop:
        return 4;
    }
  }

  /// 获取页面边距
  static EdgeInsets getPagePadding(BuildContext context) {
    final deviceType = getDeviceType(context);
    
    switch (deviceType) {
      case DeviceType.mobile:
        return const EdgeInsets.symmetric(horizontal: 16);
      case DeviceType.tablet:
        return const EdgeInsets.symmetric(horizontal: 32);
      case DeviceType.desktop:
        return const EdgeInsets.symmetric(horizontal: 64);
    }
  }

  /// 获取聊天区域约束
  static BoxConstraints getChatConstraints(BuildContext context) {
    final deviceType = getDeviceType(context);
    
    switch (deviceType) {
      case DeviceType.mobile:
        return const BoxConstraints(maxWidth: double.infinity);
      case DeviceType.tablet:
        return const BoxConstraints(maxWidth: 700);
      case DeviceType.desktop:
        return const BoxConstraints(maxWidth: 800);
    }
  }

  /// 是否显示侧边栏
  static bool shouldShowSidebar(BuildContext context) {
    return getDeviceType(context) == DeviceType.desktop;
  }

  /// 获取字体缩放因子
  static double getFontScale(BuildContext context) {
    final deviceType = getDeviceType(context);
    
    switch (deviceType) {
      case DeviceType.mobile:
        return 1.0;
      case DeviceType.tablet:
        return 1.1;
      case DeviceType.desktop:
        return 1.2;
    }
  }
}

/// 设备类型枚举
enum DeviceType {
  mobile,
  tablet,
  desktop,
}

/// 响应式包装器组件
class ResponsiveWrapper extends StatelessWidget {
  final Widget mobile;
  final Widget? tablet;
  final Widget? desktop;

  const ResponsiveWrapper({
    super.key,
    required this.mobile,
    this.tablet,
    this.desktop,
  });

  @override
  Widget build(BuildContext context) {
    final deviceType = ResponsiveUtils.getDeviceType(context);
    
    switch (deviceType) {
      case DeviceType.mobile:
        return mobile;
      case DeviceType.tablet:
        return tablet ?? mobile;
      case DeviceType.desktop:
        return desktop ?? tablet ?? mobile;
    }
  }
}

/// 响应式值获取器
class ResponsiveValue<T> {
  final T mobile;
  final T? tablet;
  final T? desktop;

  const ResponsiveValue({
    required this.mobile,
    this.tablet,
    this.desktop,
  });

  T getValue(BuildContext context) {
    final deviceType = ResponsiveUtils.getDeviceType(context);
    
    switch (deviceType) {
      case DeviceType.mobile:
        return mobile;
      case DeviceType.tablet:
        return tablet ?? mobile;
      case DeviceType.desktop:
        return desktop ?? tablet ?? mobile;
    }
  }
}