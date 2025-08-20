/// 球形宇宙配置 - 简单直接的配置管理
import 'package:flutter/material.dart';
import 'dart:math';

/// 球面点数据结构
class SphericalPoint {
  final double radius; // 距球心距离
  final double theta; // 水平角度 [0, 2π]
  final double phi; // 垂直角度 [0, π]
  final String id;
  final String type; // 数据类型：search, entity, graph, vector
  final Map<String, dynamic> data;
  final Color color;
  final double size;

  const SphericalPoint({
    required this.radius,
    required this.theta,
    required this.phi,
    required this.id,
    required this.type,
    required this.data,
    required this.color,
    this.size = 4.0,
  });

  /// 创建搜索数据点
  factory SphericalPoint.search({
    required String id,
    required Map<String, dynamic> data,
    required double theta,
    required double phi,
  }) {
    return SphericalPoint(
      id: id,
      type: 'search',
      data: data,
      radius: 300.0,
      theta: theta,
      phi: phi,
      color: const Color(0xFFFFD700), // 金色
      size: 5.0,
    );
  }

  /// 创建实体数据点
  factory SphericalPoint.entity({
    required String id,
    required Map<String, dynamic> data,
    required double theta,
    required double phi,
  }) {
    return SphericalPoint(
      id: id,
      type: 'entity',
      data: data,
      radius: 500.0,
      theta: theta,
      phi: phi,
      color: const Color(0xFF87CEEB), // 天蓝色
      size: 4.0,
    );
  }

  /// 创建图数据点
  factory SphericalPoint.graph({
    required String id,
    required Map<String, dynamic> data,
    required double theta,
    required double phi,
  }) {
    return SphericalPoint(
      id: id,
      type: 'graph',
      data: data,
      radius: 700.0,
      theta: theta,
      phi: phi,
      color: const Color(0xFF9370DB), // 紫色
      size: 6.0,
    );
  }

  /// 创建向量数据点
  factory SphericalPoint.vector({
    required String id,
    required Map<String, dynamic> data,
    required double theta,
    required double phi,
    double? radius,
  }) {
    return SphericalPoint(
      id: id,
      type: 'vector',
      data: data,
      radius: radius ?? (400.0 + Random().nextDouble() * 200),
      theta: theta,
      phi: phi,
      color: const Color(0xFFFF073A), // 红色
      size: 3.0,
    );
  }
}

/// 球形宇宙配置
class SphericalConfig {
  // 相机参数
  static const double defaultViewRadius = 500.0;
  static const double minViewRadius = 100.0;
  static const double maxViewRadius = 2000.0;
  static const double rotationSensitivity = 0.01;
  static const double zoomSensitivity = 0.1;

  // 渲染参数
  static const int maxVisiblePoints = 2000;
  static const double cullDistance = 1000.0;
  static const double minPointSize = 1.0;
  static const double maxPointSize = 12.0;

  // 数据分层半径
  static const double searchLayerRadius = 300.0;
  static const double entityLayerRadius = 500.0;
  static const double graphLayerRadius = 700.0;
  static const double vectorLayerMinRadius = 400.0;
  static const double vectorLayerMaxRadius = 600.0;

  // 颜色主题
  static const Color backgroundColor = Color(0xFF0B1426);
  static const Color backgroundAccent = Color(0xFF000000);

  // 数据类型颜色
  static const Map<String, Color> dataTypeColors = {
    'search': Color(0xFFFFD700), // 金色 - 搜索数据
    'entity': Color(0xFF87CEEB), // 天蓝色 - 实体数据
    'graph': Color(0xFF9370DB), // 紫色 - 图数据
    'vector': Color(0xFFFF073A), // 红色 - 向量数据
  };

  // 性能参数
  static const int targetFPS = 60;
  static const int pointsPerFrame = 500; // 分帧渲染
  static const Duration frameInterval = Duration(milliseconds: 16);
}

/// 2D向量工具类
class Vector2 {
  final double x;
  final double y;

  const Vector2(this.x, this.y);

  static const Vector2 zero = Vector2(0, 0);

  Vector2 operator +(Vector2 other) => Vector2(x + other.x, y + other.y);
  Vector2 operator -(Vector2 other) => Vector2(x - other.x, y - other.y);
  Vector2 operator *(double scalar) => Vector2(x * scalar, y * scalar);

  double get length => sqrt(x * x + y * y);

  Offset toOffset() => Offset(x, y);
}
