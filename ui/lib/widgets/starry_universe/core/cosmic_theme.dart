/// 宇宙主题配置 - 定义星空可视化的颜色系统和视觉参数
import 'package:flutter/material.dart';

class CosmicTheme {
  // 深空背景色彩
  static const Color primaryCosmic = Color(0xFF0B1426);
  static const Color secondaryCosmic = Color(0xFF1A237E);
  static const Color deepSpace = Color(0xFF000511);
  
  // 星体颜色系统
  static const Color starGold = Color(0xFFFFD700);      // 文档数据 - 主序星
  static const Color starBlue = Color(0xFF87CEEB);      // 人物数据 - 蓝巨星
  static const Color starPurple = Color(0xFF9370DB);    // 概念数据 - 紫色恒星
  static const Color starWhite = Color(0xFFF8F8FF);     // 关系数据 - 白矮星
  static const Color starRed = Color(0xFFFF6B6B);       // 重要数据 - 红巨星
  
  // 星云色彩系统
  static const Color nebulaRed = Color(0xFFFF073A);     // 发射星云 - 热门内容
  static const Color nebulaBlue = Color(0xFF40E0D0);    // 反射星云 - 引用内容
  static const Color nebulaPurple = Color(0xFF9B59B6);  // 行星状星云 - 完整内容
  static const Color nebulaDark = Color(0xFF2C3E50);    // 暗星云 - 稀有内容
  
  // 连接线色彩 - 表示关系强度
  static const Color connectionWeak = Color(0x33FFFFFF);    // 弱连接
  static const Color connectionMedium = Color(0x66FFFFFF);  // 中等连接
  static const Color connectionStrong = Color(0xFFFFFFFF);  // 强连接
  
  // 数据类型颜色映射
  static const Map<String, Color> dataTypeColors = {
    'document': starGold,
    'image': starBlue,
    'code': starPurple,
    'person': starBlue,
    'concept': starPurple,
    'relationship': starWhite,
    'file': starGold,
    'default': starWhite,
  };
  
  // 重要性级别颜色
  static const Map<String, Color> importanceColors = {
    'critical': starRed,
    'high': starGold,
    'medium': starBlue,
    'low': starWhite,
  };
  
  /// 根据数据类型获取对应的星体颜色
  static Color getStarColor(String dataType) {
    return dataTypeColors[dataType.toLowerCase()] ?? dataTypeColors['default']!;
  }
  
  /// 根据重要性获取颜色
  static Color getImportanceColor(String importance) {
    return importanceColors[importance.toLowerCase()] ?? starWhite;
  }
  
  /// 根据相关度分数生成颜色亮度
  static Color getScoreBasedColor(Color baseColor, double score) {
    // score 范围 0.0-1.0，用于调节颜色亮度
    final opacity = (score * 0.8 + 0.2).clamp(0.2, 1.0);
    return baseColor.withOpacity(opacity);
  }
  
  /// 生成背景渐变
  static LinearGradient createCosmicBackground() {
    return const LinearGradient(
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
      colors: [
        deepSpace,
        primaryCosmic,
        secondaryCosmic,
      ],
      stops: [0.0, 0.5, 1.0],
    );
  }
  
  /// 生成星云粒子渐变
  static RadialGradient createNebulaGradient(Color centerColor) {
    return RadialGradient(
      colors: [
        centerColor.withOpacity(0.8),
        centerColor.withOpacity(0.4),
        centerColor.withOpacity(0.1),
        Colors.transparent,
      ],
      stops: const [0.0, 0.3, 0.7, 1.0],
    );
  }
}

/// 宇宙动画配置参数
class CosmicAnimationConfig {
  // 基础动画时长
  static const Duration starPulseDuration = Duration(seconds: 2);
  static const Duration orbitDuration = Duration(seconds: 10);
  static const Duration nebulaDrift = Duration(seconds: 15);
  static const Duration particleLifetime = Duration(seconds: 5);
  
  // 动画曲线
  static const Curve starPulseCurve = Curves.easeInOutSine;
  static const Curve orbitCurve = Curves.linear;
  static const Curve nebulaFlowCurve = Curves.easeInOutQuart;
  
  // 粒子系统参数
  static const int maxParticlesPerNebula = 1000;
  static const int maxBackgroundStars = 200;
  static const double particleSpeed = 50.0; // 像素/秒
  static const double baseStarSize = 2.0;
  static const double maxStarSize = 8.0;
}

/// 性能优化配置
class CosmicPerformanceConfig {
  static const int maxParticles = 5000;      // 最大粒子数
  static const int maxNodes = 1000;          // 最大节点数  
  static const int targetFPS = 60;           // 目标帧率
  static const double lodThreshold = 0.5;    // LOD切换阈值
  static const int maxVisibleStars = 300;    // 最大可见星体数
  static const double minStarSize = 1.0;     // 最小星体尺寸
  static const double cullingDistance = 1000.0; // 剔除距离
}