/// 球面相机 - 处理观察角度、缩放和坐标转换
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'spherical_config.dart';

/// 球面相机系统
class SphericalCamera extends ChangeNotifier {
  double _viewRadius = SphericalConfig.defaultViewRadius;
  double _rotationTheta = 0.0; // 水平旋转角度
  double _rotationPhi = 0.0; // 垂直旋转角度

  // 获取器
  double get viewRadius => _viewRadius;
  double get rotationTheta => _rotationTheta;
  double get rotationPhi => _rotationPhi;

  /// 旋转相机
  void rotate(Offset delta) {
    _rotationTheta += delta.dx * SphericalConfig.rotationSensitivity;
    _rotationPhi += delta.dy * SphericalConfig.rotationSensitivity;

    // 限制垂直旋转防止翻转
    _rotationPhi = _rotationPhi.clamp(-math.pi / 2, math.pi / 2);

    // 水平旋转可以无限制（360度滚动）
    _rotationTheta = _rotationTheta % (2 * math.pi);

    notifyListeners();
  }

  /// 缩放相机（改变观察半径）
  void zoom(double scale) {
    _viewRadius = (_viewRadius / scale).clamp(
      SphericalConfig.minViewRadius,
      SphericalConfig.maxViewRadius,
    );
    notifyListeners();
  }

  /// 直接设置缩放级别
  void setZoom(double zoom) {
    _viewRadius = zoom.clamp(
      SphericalConfig.minViewRadius,
      SphericalConfig.maxViewRadius,
    );
    notifyListeners();
  }

  /// 重置相机到默认位置
  void reset() {
    _viewRadius = SphericalConfig.defaultViewRadius;
    _rotationTheta = 0.0;
    _rotationPhi = 0.0;
    notifyListeners();
  }

  /// 球面点转换为屏幕坐标
  Vector2? pointToScreen(SphericalPoint point, Size screenSize) {
    // 计算相对于相机的角度
    final relativeTheta = point.theta - _rotationTheta;
    final relativePhi = point.phi - _rotationPhi;

    // 球面坐标转直角坐标
    final x = point.radius * math.sin(relativePhi) * math.cos(relativeTheta);
    final y = point.radius * math.sin(relativePhi) * math.sin(relativeTheta);
    final z = point.radius * math.cos(relativePhi);

    // 视锥剔除：z < 0的点在相机后面，不渲染
    if (z < 0) return null;

    // 距离剔除：距离观察半径太远的点不渲染
    final distance = (point.radius - _viewRadius).abs();
    if (distance > SphericalConfig.cullDistance) return null;

    // 转换到屏幕坐标
    final screenX = screenSize.width * 0.5 + x * (_viewRadius / point.radius);
    final screenY = screenSize.height * 0.5 - y * (_viewRadius / point.radius);

    // 边界检查
    if (screenX < -50 ||
        screenX > screenSize.width + 50 ||
        screenY < -50 ||
        screenY > screenSize.height + 50) {
      return null;
    }

    return Vector2(screenX, screenY);
  }

  /// 计算点的可见性权重（用于透明度和大小）
  double calculateVisibilityWeight(SphericalPoint point) {
    final distance = (point.radius - _viewRadius).abs();
    final weight =
        (1.0 - distance / SphericalConfig.cullDistance).clamp(0.0, 1.0);
    return weight;
  }

  /// 计算点的屏幕大小
  double calculatePointSize(SphericalPoint point) {
    final weight = calculateVisibilityWeight(point);
    final baseSize = point.size;
    final scaledSize = baseSize * weight * (_viewRadius / point.radius);

    return scaledSize.clamp(
      SphericalConfig.minPointSize,
      SphericalConfig.maxPointSize,
    );
  }

  /// 获取可见点列表（按深度排序）
  List<SphericalPoint> getVisiblePoints(
    List<SphericalPoint> allPoints,
    Size screenSize,
  ) {
    final visiblePoints = <SphericalPoint>[];

    for (final point in allPoints) {
      final screenPos = pointToScreen(point, screenSize);
      if (screenPos != null) {
        visiblePoints.add(point);
      }
    }

    // 按z深度排序（远的先画，近的后画）
    visiblePoints.sort((a, b) {
      final aDistance = (a.radius - _viewRadius).abs();
      final bDistance = (b.radius - _viewRadius).abs();
      return bDistance.compareTo(aDistance);
    });

    // 限制可见点数量以保证性能
    if (visiblePoints.length > SphericalConfig.maxVisiblePoints) {
      return visiblePoints.take(SphericalConfig.maxVisiblePoints).toList();
    }

    return visiblePoints;
  }

  /// 检查点击位置是否命中数据点
  String? hitTest(
    Offset tapPosition,
    List<SphericalPoint> points,
    Size screenSize,
  ) {
    const hitRadius = 30.0; // 点击检测半径
    String? nearestPointId;
    double minDistance = double.infinity;

    for (final point in points) {
      final screenPos = pointToScreen(point, screenSize);
      if (screenPos == null) continue;

      final distance = (tapPosition - screenPos.toOffset()).distance;
      if (distance < hitRadius && distance < minDistance) {
        minDistance = distance;
        nearestPointId = point.id;
      }
    }

    return nearestPointId;
  }

  /// 聚焦到指定数据点
  void focusOnPoint(SphericalPoint point, {Duration? duration}) {
    // 计算相机需要旋转到的角度
    final targetTheta = point.theta;
    final targetPhi = point.phi;

    // 简单的直接跳转（可以后续添加动画）
    _rotationTheta = targetTheta;
    _rotationPhi = targetPhi;

    // 调整观察半径使点清晰可见
    _viewRadius = point.radius * 1.2;
    _viewRadius = _viewRadius.clamp(
      SphericalConfig.minViewRadius,
      SphericalConfig.maxViewRadius,
    );

    notifyListeners();
  }

  /// 获取相机状态信息（用于调试）
  Map<String, dynamic> getDebugInfo() {
    return {
      'viewRadius': _viewRadius.toStringAsFixed(1),
      'rotationTheta': (_rotationTheta * 180 / math.pi).toStringAsFixed(1),
      'rotationPhi': (_rotationPhi * 180 / math.pi).toStringAsFixed(1),
      'zoomLevel':
          (SphericalConfig.defaultViewRadius / _viewRadius).toStringAsFixed(2),
    };
  }
}
