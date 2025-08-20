/// 球面交互处理 - 手势处理和数据点选择
import 'package:flutter/material.dart';
import 'spherical_config.dart';
import 'spherical_camera.dart';

/// 球面交互处理器
class SphericalInteractions {
  final SphericalCamera camera;
  final Function(String)? onPointSelected;
  final VoidCallback? onInteractionStart;
  final VoidCallback? onInteractionEnd;

  // 交互状态
  bool _isInteracting = false;
  Offset? _lastPanPosition;
  double _initialScale = 1.0;

  SphericalInteractions({
    required this.camera,
    this.onPointSelected,
    this.onInteractionStart,
    this.onInteractionEnd,
  });

  // 获取器
  bool get isInteracting => _isInteracting;

  /// 处理拖拽开始
  void handlePanStart(DragStartDetails details) {
    _isInteracting = true;
    _lastPanPosition = details.localPosition;
    onInteractionStart?.call();
  }

  /// 处理拖拽更新
  void handlePanUpdate(DragUpdateDetails details) {
    if (!_isInteracting || _lastPanPosition == null) return;

    final delta = details.localPosition - _lastPanPosition!;
    camera.rotate(delta);
    _lastPanPosition = details.localPosition;
  }

  /// 处理拖拽结束
  void handlePanEnd(DragEndDetails details) {
    _isInteracting = false;
    _lastPanPosition = null;
    onInteractionEnd?.call();
  }

  /// 处理缩放开始
  void handleScaleStart(ScaleStartDetails details) {
    _isInteracting = true;
    _initialScale = camera.viewRadius;
    onInteractionStart?.call();
  }

  /// 处理缩放更新
  void handleScaleUpdate(ScaleUpdateDetails details) {
    if (!_isInteracting) return;

    // 处理旋转
    if (details.pointerCount == 1) {
      // 单指拖拽旋转
      final delta = details.focalPointDelta;
      camera.rotate(delta);
    } else if (details.pointerCount >= 2) {
      // 双指缩放
      final scale = details.scale;
      if (scale != 1.0) {
        camera.zoom(scale);
      }
    }
  }

  /// 处理缩放结束
  void handleScaleEnd(ScaleEndDetails details) {
    _isInteracting = false;
    _initialScale = 1.0;
    onInteractionEnd?.call();
  }

  /// 处理点击
  void handleTap(
      TapUpDetails details, List<SphericalPoint> points, Size screenSize) {
    final hitPointId =
        camera.hitTest(details.localPosition, points, screenSize);

    if (hitPointId != null && onPointSelected != null) {
      onPointSelected!(hitPointId);
    }
  }

  /// 处理双击
  void handleDoubleTap(
      TapDownDetails details, List<SphericalPoint> points, Size screenSize) {
    final hitPointId =
        camera.hitTest(details.localPosition, points, screenSize);

    if (hitPointId != null) {
      // 双击聚焦到点
      final targetPoint = points.firstWhere(
        (point) => point.id == hitPointId,
        orElse: () => points.first,
      );

      camera.focusOnPoint(targetPoint);
      onPointSelected?.call(hitPointId);
    } else {
      // 双击空白区域重置相机
      camera.reset();
    }
  }

  /// 处理长按
  void handleLongPress(LongPressStartDetails details,
      List<SphericalPoint> points, Size screenSize) {
    final hitPointId =
        camera.hitTest(details.localPosition, points, screenSize);

    if (hitPointId != null) {
      // 长按显示详细信息
      onPointSelected?.call(hitPointId);

      // 可以触发震动反馈
      // HapticFeedback.mediumImpact();
    }
  }

  /// 处理鼠标滚轮缩放
  void handlePointerSignal(PointerSignalEvent event) {
    if (event is PointerScrollEvent) {
      final scrollDelta = event.scrollDelta.dy;
      final zoomFactor = scrollDelta > 0 ? 1.1 : 0.9;
      camera.zoom(zoomFactor);
    }
  }

  /// 获取手势识别器
  Map<Type, GestureRecognizerFactory> getGestureRecognizers(
    List<SphericalPoint> points,
    Size screenSize,
  ) {
    return <Type, GestureRecognizerFactory>{
      // 拖拽手势
      PanGestureRecognizer:
          GestureRecognizerFactoryWithHandlers<PanGestureRecognizer>(
        () => PanGestureRecognizer(),
        (PanGestureRecognizer instance) {
          instance
            ..onStart = handlePanStart
            ..onUpdate = handlePanUpdate
            ..onEnd = handlePanEnd;
        },
      ),

      // 缩放手势
      ScaleGestureRecognizer:
          GestureRecognizerFactoryWithHandlers<ScaleGestureRecognizer>(
        () => ScaleGestureRecognizer(),
        (ScaleGestureRecognizer instance) {
          instance
            ..onStart = handleScaleStart
            ..onUpdate = handleScaleUpdate
            ..onEnd = handleScaleEnd;
        },
      ),

      // 点击手势
      TapGestureRecognizer:
          GestureRecognizerFactoryWithHandlers<TapGestureRecognizer>(
        () => TapGestureRecognizer(),
        (TapGestureRecognizer instance) {
          instance.onTapUp =
              (details) => handleTap(details, points, screenSize);
        },
      ),

      // 双击手势
      DoubleTapGestureRecognizer:
          GestureRecognizerFactoryWithHandlers<DoubleTapGestureRecognizer>(
        () => DoubleTapGestureRecognizer(),
        (DoubleTapGestureRecognizer instance) {
          instance.onDoubleTapDown =
              (details) => handleDoubleTap(details, points, screenSize);
        },
      ),

      // 长按手势
      LongPressGestureRecognizer:
          GestureRecognizerFactoryWithHandlers<LongPressGestureRecognizer>(
        () => LongPressGestureRecognizer(),
        (LongPressGestureRecognizer instance) {
          instance.onLongPressStart =
              (details) => handleLongPress(details, points, screenSize);
        },
      ),
    };
  }

  /// 处理键盘快捷键
  bool handleKeyEvent(KeyEvent event, List<SphericalPoint> points) {
    if (event is KeyDownEvent) {
      switch (event.logicalKey) {
        case LogicalKeyboardKey.space:
          // 空格键重置相机
          camera.reset();
          return true;

        case LogicalKeyboardKey.arrowUp:
          // 上箭头向上旋转
          camera.rotate(const Offset(0, -50));
          return true;

        case LogicalKeyboardKey.arrowDown:
          // 下箭头向下旋转
          camera.rotate(const Offset(0, 50));
          return true;

        case LogicalKeyboardKey.arrowLeft:
          // 左箭头向左旋转
          camera.rotate(const Offset(-50, 0));
          return true;

        case LogicalKeyboardKey.arrowRight:
          // 右箭头向右旋转
          camera.rotate(const Offset(50, 0));
          return true;

        case LogicalKeyboardKey.equal:
        case LogicalKeyboardKey.numpadAdd:
          // 加号放大
          camera.zoom(0.9);
          return true;

        case LogicalKeyboardKey.minus:
        case LogicalKeyboardKey.numpadSubtract:
          // 减号缩小
          camera.zoom(1.1);
          return true;

        case LogicalKeyboardKey.digit1:
          // 1键聚焦搜索数据
          _focusOnDataType(points, 'search');
          return true;

        case LogicalKeyboardKey.digit2:
          // 2键聚焦实体数据
          _focusOnDataType(points, 'entity');
          return true;

        case LogicalKeyboardKey.digit3:
          // 3键聚焦图数据
          _focusOnDataType(points, 'graph');
          return true;

        case LogicalKeyboardKey.digit4:
          // 4键聚焦向量数据
          _focusOnDataType(points, 'vector');
          return true;
      }
    }

    return false;
  }

  /// 聚焦到特定数据类型
  void focusOnDataType(List<SphericalPoint> points, String type) {
    final typePoints = points.where((point) => point.type == type).toList();
    if (typePoints.isNotEmpty) {
      // 计算该类型数据的中心位置
      double avgTheta = 0;
      double avgPhi = 0;
      double avgRadius = 0;

      for (final point in typePoints) {
        avgTheta += point.theta;
        avgPhi += point.phi;
        avgRadius += point.radius;
      }

      avgTheta /= typePoints.length;
      avgPhi /= typePoints.length;
      avgRadius /= typePoints.length;

      // 创建虚拟中心点并聚焦
      final centerPoint = SphericalPoint(
        radius: avgRadius,
        theta: avgTheta,
        phi: avgPhi,
        id: 'center_$type',
        type: type,
        data: {},
        color: SphericalConfig.dataTypeColors[type] ?? Colors.white,
      );

      camera.focusOnPoint(centerPoint);
    }
  }

  /// 创建快捷键帮助文本
  List<String> getKeyboardShortcuts() {
    return [
      'Space - 重置相机',
      '方向键 - 旋转视角',
      '+/- - 缩放',
      '1-4 - 聚焦数据类型',
      '鼠标拖拽 - 旋转',
      '鼠标滚轮 - 缩放',
      '双击点 - 聚焦',
      '双击空白 - 重置',
    ];
  }

  /// 获取交互状态信息
  Map<String, dynamic> getInteractionState() {
    return {
      'isInteracting': _isInteracting,
      'cameraState': camera.getDebugInfo(),
      'supportedGestures': ['pan', 'scale', 'tap', 'doubleTap', 'longPress'],
      'keyboardShortcuts': getKeyboardShortcuts().length,
    };
  }
}
