/// 球面渲染器 - 直接绘制，不搞复杂东西
import 'dart:math' as math;
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'spherical_config.dart';
import 'spherical_camera.dart';

/// 球面渲染器 - CustomPaint直接绘制
class SphericalRenderer extends CustomPainter {
  final SphericalCamera camera;
  final List<SphericalPoint> points;
  final String? selectedPointId;
  final bool showDebugInfo;
  final VoidCallback? onRepaintNeeded;

  SphericalRenderer({
    required this.camera,
    required this.points,
    this.selectedPointId,
    this.showDebugInfo = false,
    this.onRepaintNeeded,
  });

  @override
  void paint(Canvas canvas, Size size) {
    // 绘制背景
    _drawBackground(canvas, size);

    // 获取可见点并按深度排序
    final visiblePoints = camera.getVisiblePoints(points, size);

    // 绘制连接线（如果需要）
    _drawConnections(canvas, size, visiblePoints);

    // 绘制数据点
    _drawPoints(canvas, size, visiblePoints);

    // 绘制选中状态
    if (selectedPointId != null) {
      _drawSelection(canvas, size, visiblePoints);
    }

    // 绘制调试信息
    if (showDebugInfo) {
      _drawDebugInfo(canvas, size, visiblePoints);
    }
  }

  /// 绘制星空背景
  void _drawBackground(Canvas canvas, Size size) {
    // 径向渐变背景
    final paint = Paint()
      ..shader = ui.Gradient.radial(
        Offset(size.width * 0.5, size.height * 0.5),
        size.width * 0.6,
        [
          SphericalConfig.backgroundColor,
          SphericalConfig.backgroundAccent,
        ],
        [0.0, 1.0],
      );

    canvas.drawRect(Offset.zero & size, paint);

    // 可选：绘制星星背景
    _drawStarField(canvas, size);
  }

  /// 绘制星星背景
  void _drawStarField(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.1)
      ..strokeWidth = 1.0;

    final random = math.Random(12345); // 固定种子

    // 绘制背景星星
    for (int i = 0; i < 100; i++) {
      final x = random.nextDouble() * size.width;
      final y = random.nextDouble() * size.height;
      final opacity = 0.1 + random.nextDouble() * 0.3;

      paint.color = Colors.white.withOpacity(opacity);
      canvas.drawCircle(Offset(x, y), 0.5, paint);
    }
  }

  /// 绘制数据点之间的连接线
  void _drawConnections(
      Canvas canvas, Size size, List<SphericalPoint> visiblePoints) {
    if (visiblePoints.length < 2) return;

    final paint = Paint()
      ..color = Colors.white.withOpacity(0.1)
      ..strokeWidth = 1.0
      ..style = PaintingStyle.stroke;

    // 只为图数据绘制连接线
    final graphPoints = visiblePoints.where((p) => p.type == 'graph').toList();

    for (int i = 0; i < graphPoints.length - 1; i++) {
      final pointA = graphPoints[i];
      final pointB = graphPoints[i + 1];

      final screenA = camera.pointToScreen(pointA, size);
      final screenB = camera.pointToScreen(pointB, size);

      if (screenA != null && screenB != null) {
        final distance = (screenA - screenB).length;

        // 只连接近距离的点
        if (distance < 100) {
          final opacity = (1.0 - distance / 100).clamp(0.0, 0.3);
          paint.color = Colors.white.withOpacity(opacity);

          canvas.drawLine(
            screenA.toOffset(),
            screenB.toOffset(),
            paint,
          );
        }
      }
    }
  }

  /// 绘制数据点
  void _drawPoints(
      Canvas canvas, Size size, List<SphericalPoint> visiblePoints) {
    final paint = Paint()..style = PaintingStyle.fill;

    for (final point in visiblePoints) {
      final screenPos = camera.pointToScreen(point, size);
      if (screenPos == null) continue;

      // 计算点的可见性权重
      final weight = camera.calculateVisibilityWeight(point);
      if (weight <= 0) continue;

      // 计算点的大小和透明度
      final pointSize = camera.calculatePointSize(point);
      final alpha = (weight * 0.8 + 0.2).clamp(0.0, 1.0);

      // 设置颜色和透明度
      paint.color = point.color.withOpacity(alpha);

      // 绘制光晕效果
      if (pointSize > 3) {
        final glowPaint = Paint()
          ..color = point.color.withOpacity(alpha * 0.3)
          ..style = PaintingStyle.fill;

        canvas.drawCircle(
          screenPos.toOffset(),
          pointSize * 2,
          glowPaint,
        );
      }

      // 绘制主点
      canvas.drawCircle(
        screenPos.toOffset(),
        pointSize,
        paint,
      );

      // 高亮搜索数据（脉动效果）
      if (point.type == 'search' && pointSize > 2) {
        _drawPulsingEffect(
            canvas, screenPos.toOffset(), pointSize, point.color, alpha);
      }
    }
  }

  /// 绘制脉动效果
  void _drawPulsingEffect(
      Canvas canvas, Offset center, double size, Color color, double alpha) {
    final time = DateTime.now().millisecondsSinceEpoch / 1000.0;
    final pulse = (math.sin(time * 3) * 0.5 + 0.5);

    final pulsePaint = Paint()
      ..color = color.withOpacity(alpha * 0.3 * pulse)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.0;

    canvas.drawCircle(
      center,
      size + pulse * 5,
      pulsePaint,
    );
  }

  /// 绘制选中状态
  void _drawSelection(
      Canvas canvas, Size size, List<SphericalPoint> visiblePoints) {
    final selectedPoint = visiblePoints.firstWhere(
      (point) => point.id == selectedPointId,
      orElse: () => visiblePoints.isNotEmpty
          ? visiblePoints.first
          : SphericalPoint(
              radius: 0,
              theta: 0,
              phi: 0,
              id: '',
              type: '',
              data: {},
              color: Colors.white),
    );

    if (selectedPoint.id.isEmpty) return;

    final screenPos = camera.pointToScreen(selectedPoint, size);
    if (screenPos == null) return;

    // 选中圆环
    final selectionPaint = Paint()
      ..color = Colors.yellowAccent.withOpacity(0.8)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;

    final pointSize = camera.calculatePointSize(selectedPoint);

    canvas.drawCircle(
      screenPos.toOffset(),
      pointSize + 8,
      selectionPaint,
    );

    // 选中动画效果
    final time = DateTime.now().millisecondsSinceEpoch / 200.0;
    final animationRadius = pointSize + 15 + math.sin(time) * 5;

    final animationPaint = Paint()
      ..color = Colors.yellowAccent.withOpacity(0.4)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5;

    canvas.drawCircle(
      screenPos.toOffset(),
      animationRadius,
      animationPaint,
    );
  }

  /// 绘制调试信息
  void _drawDebugInfo(
      Canvas canvas, Size size, List<SphericalPoint> visiblePoints) {
    final debugPaint = Paint()
      ..color = Colors.green
      ..style = PaintingStyle.fill;

    final textPainter = TextPainter(
      textDirection: TextDirection.ltr,
    );

    // 相机信息
    final cameraInfo = camera.getDebugInfo();
    final debugText = [
      'Points: ${visiblePoints.length}/${points.length}',
      'Camera: θ=${cameraInfo['rotationTheta']}° φ=${cameraInfo['rotationPhi']}°',
      'Radius: ${cameraInfo['viewRadius']}',
      'Zoom: ${cameraInfo['zoomLevel']}x',
    ];

    double yOffset = 20;
    for (final line in debugText) {
      textPainter.text = TextSpan(
        text: line,
        style: const TextStyle(
          color: Colors.green,
          fontSize: 12,
          fontFamily: 'monospace',
        ),
      );

      textPainter.layout();
      textPainter.paint(canvas, Offset(10, yOffset));
      yOffset += 16;
    }

    // 数据类型统计
    final typeStats = <String, int>{};
    for (final point in visiblePoints) {
      typeStats[point.type] = (typeStats[point.type] ?? 0) + 1;
    }

    yOffset += 10;
    for (final entry in typeStats.entries) {
      final color = SphericalConfig.dataTypeColors[entry.key] ?? Colors.white;
      textPainter.text = TextSpan(
        text: '${entry.key}: ${entry.value}',
        style: TextStyle(
          color: color,
          fontSize: 11,
          fontFamily: 'monospace',
        ),
      );

      textPainter.layout();
      textPainter.paint(canvas, Offset(10, yOffset));
      yOffset += 14;
    }
  }

  /// 计算性能指标
  Map<String, dynamic> getPerformanceMetrics(Size size) {
    final visiblePoints = camera.getVisiblePoints(points, size);

    return {
      'totalPoints': points.length,
      'visiblePoints': visiblePoints.length,
      'cullRatio':
          ((points.length - visiblePoints.length) / points.length * 100)
              .round(),
      'cameraDistance': camera.viewRadius.round(),
      'screenSize': '${size.width.round()}x${size.height.round()}',
    };
  }

  @override
  bool shouldRepaint(covariant SphericalRenderer oldDelegate) {
    return oldDelegate.camera != camera ||
        oldDelegate.points != points ||
        oldDelegate.selectedPointId != selectedPointId ||
        oldDelegate.showDebugInfo != showDebugInfo;
  }

  /// 获取边界框（用于优化）
  Rect? getBoundingBox(Size size) {
    if (points.isEmpty) return null;

    double minX = double.infinity;
    double minY = double.infinity;
    double maxX = -double.infinity;
    double maxY = -double.infinity;

    for (final point in points) {
      final screenPos = camera.pointToScreen(point, size);
      if (screenPos != null) {
        minX = math.min(minX, screenPos.x);
        minY = math.min(minY, screenPos.y);
        maxX = math.max(maxX, screenPos.x);
        maxY = math.max(maxY, screenPos.y);
      }
    }

    if (minX.isInfinite) return null;

    return Rect.fromLTRB(
      minX - 50,
      minY - 50,
      maxX + 50,
      maxY + 50,
    );
  }
}
