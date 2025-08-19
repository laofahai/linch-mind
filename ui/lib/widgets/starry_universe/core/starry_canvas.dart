/// StarryCanvas基础渲染器 - 统一的Canvas绘制引擎
import 'dart:math' as math;
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:vector_math/vector_math.dart' as vm;
import 'cosmic_theme.dart';
import 'particle_system.dart';

/// 天体对象基类
abstract class CelestialObject {
  vm.Vector2 position;
  double size;
  Color color;
  String id;
  Map<String, dynamic> metadata;
  
  CelestialObject({
    required this.position,
    required this.size,
    required this.color,
    required this.id,
    this.metadata = const {},
  });
  
  /// 绘制天体对象
  void draw(Canvas canvas, Paint paint);
  
  /// 更新天体对象状态
  void update(double deltaTime);
  
  /// 检查点是否在天体对象内
  bool containsPoint(vm.Vector2 point);
}

/// 恒星对象
class Star extends CelestialObject {
  double pulsePhase;
  double intensity;
  bool isSelected;
  
  Star({
    required super.position,
    required super.size,
    required super.color,
    required super.id,
    super.metadata,
    this.pulsePhase = 0.0,
    this.intensity = 1.0,
    this.isSelected = false,
  });
  
  @override
  void draw(Canvas canvas, Paint paint) {
    // 计算脉动效果
    final pulseFactor = 1.0 + math.sin(pulsePhase) * 0.2;
    final currentSize = size * pulseFactor;
    
    // 绘制星体光晕
    paint.color = color.withOpacity(intensity * 0.3);
    paint.maskFilter = const MaskFilter.blur(BlurStyle.normal, 4.0);
    canvas.drawCircle(
      Offset(position.x, position.y),
      currentSize * 2,
      paint,
    );
    
    // 绘制星体核心
    paint.color = color.withOpacity(intensity);
    paint.maskFilter = null;
    canvas.drawCircle(
      Offset(position.x, position.y),
      currentSize,
      paint,
    );
    
    // 选中状态的额外效果
    if (isSelected) {
      paint.color = Colors.white.withOpacity(0.5);
      paint.style = PaintingStyle.stroke;
      paint.strokeWidth = 2.0;
      canvas.drawCircle(
        Offset(position.x, position.y),
        currentSize * 1.5,
        paint,
      );
      paint.style = PaintingStyle.fill;
    }
  }
  
  @override
  void update(double deltaTime) {
    pulsePhase += deltaTime * 2.0; // 脉动速度
    if (pulsePhase > 2 * math.pi) {
      pulsePhase -= 2 * math.pi;
    }
  }
  
  @override
  bool containsPoint(vm.Vector2 point) {
    final distance = (point - position).length;
    return distance <= size;
  }
}

/// 星系连接线
class StarConnection {
  final String fromStarId;
  final String toStarId;
  final double strength;
  final Color color;
  final bool animated;
  
  double animationPhase = 0.0;
  
  StarConnection({
    required this.fromStarId,
    required this.toStarId,
    required this.strength,
    required this.color,
    this.animated = false,
  });
  
  void draw(Canvas canvas, Paint paint, vm.Vector2 start, vm.Vector2 end) {
    paint.color = color.withOpacity(strength);
    paint.strokeWidth = strength * 2;
    paint.style = PaintingStyle.stroke;
    
    if (animated) {
      // 绘制流动的连接线
      _drawAnimatedLine(canvas, paint, start, end);
    } else {
      // 绘制静态连接线
      canvas.drawLine(
        Offset(start.x, start.y),
        Offset(end.x, end.y),
        paint,
      );
    }
  }
  
  void _drawAnimatedLine(Canvas canvas, Paint paint, vm.Vector2 start, vm.Vector2 end) {
    final path = Path();
    path.moveTo(start.x, start.y);
    path.lineTo(end.x, end.y);
    
    // 创建虚线效果
    final dashPattern = [10.0, 5.0];
    paint.strokeWidth = strength * 3;
    
    // 使用PathEffect创建流动效果
    canvas.drawPath(path, paint);
  }
  
  void update(double deltaTime) {
    if (animated) {
      animationPhase += deltaTime;
      if (animationPhase > 1.0) {
        animationPhase -= 1.0;
      }
    }
  }
}

/// 星空Canvas绘制器
class StarryCanvasPainter extends CustomPainter {
  final OptimizedParticleSystem particleSystem;
  final List<CelestialObject> celestialObjects;
  final List<StarConnection> connections;
  final AnimationController? animationController;
  final vm.Vector2? focusPoint;
  final double zoomLevel;
  final bool showDebugInfo;
  
  // 背景星点缓存
  static List<vm.Vector2>? _backgroundStars;
  static Size? _lastSize;
  
  StarryCanvasPainter({
    required this.particleSystem,
    this.celestialObjects = const [],
    this.connections = const [],
    this.animationController,
    this.focusPoint,
    this.zoomLevel = 1.0,
    this.showDebugInfo = false,
  });
  
  @override
  void paint(Canvas canvas, Size size) {
    // 设置粒子系统边界
    particleSystem.setBounds(size);
    
    // 绘制深空背景
    _drawStarryBackground(canvas, size);
    
    // 绘制背景星点
    _drawBackgroundStars(canvas, size);
    
    // 绘制连接线
    _drawConnections(canvas);
    
    // 绘制粒子效果
    _drawParticles(canvas);
    
    // 绘制天体对象
    _drawCelestialObjects(canvas);
    
    // 绘制调试信息
    if (showDebugInfo) {
      _drawDebugInfo(canvas, size);
    }
  }
  
  /// 绘制星空背景
  void _drawStarryBackground(Canvas canvas, Size size) {
    final paint = Paint();
    final gradient = CosmicTheme.createCosmicBackground();
    
    paint.shader = gradient.createShader(Rect.fromLTWH(0, 0, size.width, size.height));
    canvas.drawRect(Offset.zero & size, paint);
  }
  
  /// 绘制背景星点
  void _drawBackgroundStars(Canvas canvas, Size size) {
    // 缓存背景星点以提高性能
    if (_backgroundStars == null || _lastSize != size) {
      _generateBackgroundStars(size);
      _lastSize = size;
    }
    
    final paint = Paint()..color = Colors.white.withOpacity(0.3);
    
    for (final star in _backgroundStars!) {
      final opacity = math.Random(star.hashCode).nextDouble() * 0.5 + 0.2;
      paint.color = Colors.white.withOpacity(opacity);
      
      canvas.drawCircle(
        Offset(star.x, star.y),
        math.Random(star.hashCode).nextDouble() * 1.5 + 0.5,
        paint,
      );
    }
  }
  
  /// 生成背景星点
  void _generateBackgroundStars(Size size) {
    _backgroundStars = [];
    final random = math.Random(42); // 固定种子保证一致性
    
    for (int i = 0; i < CosmicAnimationConfig.maxBackgroundStars; i++) {
      _backgroundStars!.add(vm.Vector2(
        random.nextDouble() * size.width,
        random.nextDouble() * size.height,
      ));
    }
  }
  
  /// 绘制连接线
  void _drawConnections(Canvas canvas) {
    final paint = Paint();
    
    for (final connection in connections) {
      // 查找连接的星体
      final fromStar = celestialObjects.firstWhere(
        (obj) => obj.id == connection.fromStarId,
        orElse: () => Star(
          position: vm.Vector2.zero(),
          size: 0,
          color: Colors.transparent,
          id: '',
        ),
      );
      final toStar = celestialObjects.firstWhere(
        (obj) => obj.id == connection.toStarId,
        orElse: () => Star(
          position: vm.Vector2.zero(),
          size: 0,
          color: Colors.transparent,
          id: '',
        ),
      );
      
      if (fromStar.id.isNotEmpty && toStar.id.isNotEmpty) {
        connection.draw(canvas, paint, fromStar.position, toStar.position);
      }
    }
  }
  
  /// 绘制粒子效果
  void _drawParticles(Canvas canvas) {
    final paint = Paint();
    
    for (final particle in particleSystem.particles) {
      paint.color = particle.color.withOpacity(particle.intensity);
      
      // 根据粒子大小选择绘制方式
      if (particle.size <= 2.0) {
        // 小粒子绘制为点
        canvas.drawCircle(
          Offset(particle.position.x, particle.position.y),
          particle.size,
          paint,
        );
      } else {
        // 大粒子绘制为带光晕的星点
        // 绘制光晕
        paint.maskFilter = const MaskFilter.blur(BlurStyle.normal, 2.0);
        paint.color = particle.color.withOpacity(particle.intensity * 0.3);
        canvas.drawCircle(
          Offset(particle.position.x, particle.position.y),
          particle.size * 1.5,
          paint,
        );
        
        // 绘制核心
        paint.maskFilter = null;
        paint.color = particle.color.withOpacity(particle.intensity);
        canvas.drawCircle(
          Offset(particle.position.x, particle.position.y),
          particle.size,
          paint,
        );
      }
    }
  }
  
  /// 绘制天体对象
  void _drawCelestialObjects(Canvas canvas) {
    final paint = Paint();
    
    for (final object in celestialObjects) {
      object.draw(canvas, paint);
    }
  }
  
  /// 绘制调试信息
  void _drawDebugInfo(Canvas canvas, Size size) {
    final textPainter = TextPainter(
      textDirection: TextDirection.ltr,
    );
    
    final debugInfo = [
      'Particles: ${particleSystem.particleCount}',
      'FPS: ${particleSystem.fps.toStringAsFixed(1)}',
      'Objects: ${celestialObjects.length}',
      'Zoom: ${zoomLevel.toStringAsFixed(2)}x',
    ];
    
    for (int i = 0; i < debugInfo.length; i++) {
      textPainter.text = TextSpan(
        text: debugInfo[i],
        style: const TextStyle(
          color: Colors.white,
          fontSize: 12,
          fontFamily: 'monospace',
        ),
      );
      textPainter.layout();
      textPainter.paint(canvas, Offset(10, 10 + i * 20));
    }
  }
  
  @override
  bool shouldRepaint(covariant StarryCanvasPainter oldDelegate) {
    return oldDelegate.particleSystem != particleSystem ||
           oldDelegate.celestialObjects != celestialObjects ||
           oldDelegate.connections != connections ||
           oldDelegate.zoomLevel != zoomLevel ||
           oldDelegate.focusPoint != focusPoint;
  }
}

/// 星空Canvas组件
class StarryCanvas extends StatefulWidget {
  final OptimizedParticleSystem particleSystem;
  final List<CelestialObject> celestialObjects;
  final List<StarConnection> connections;
  final Function(vm.Vector2)? onTap;
  final Function(CelestialObject)? onObjectTap;
  final bool enableGestures;
  final bool showDebugInfo;
  
  const StarryCanvas({
    super.key,
    required this.particleSystem,
    this.celestialObjects = const [],
    this.connections = const [],
    this.onTap,
    this.onObjectTap,
    this.enableGestures = true,
    this.showDebugInfo = false,
  });
  
  @override
  State<StarryCanvas> createState() => _StarryCanvasState();
}

class _StarryCanvasState extends State<StarryCanvas>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  vm.Vector2? _focusPoint;
  double _zoomLevel = 1.0;
  
  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(seconds: 1),
      vsync: this,
    )..repeat();
  }
  
  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: widget.enableGestures ? _handleTapDown : null,
      onScaleUpdate: widget.enableGestures ? _handleScaleUpdate : null,
      child: AnimatedBuilder(
        animation: _animationController,
        builder: (context, child) {
          // 更新粒子系统
          widget.particleSystem.update(1 / 60.0); // 假设60FPS
          
          // 更新天体对象
          for (final object in widget.celestialObjects) {
            object.update(1 / 60.0);
          }
          
          // 更新连接线
          for (final connection in widget.connections) {
            connection.update(1 / 60.0);
          }
          
          return CustomPaint(
            painter: StarryCanvasPainter(
              particleSystem: widget.particleSystem,
              celestialObjects: widget.celestialObjects,
              connections: widget.connections,
              animationController: _animationController,
              focusPoint: _focusPoint,
              zoomLevel: _zoomLevel,
              showDebugInfo: widget.showDebugInfo,
            ),
            size: Size.infinite,
          );
        },
      ),
    );
  }
  
  void _handleTapDown(TapDownDetails details) {
    final tapPosition = vm.Vector2(details.localPosition.dx, details.localPosition.dy);
    
    // 检查是否点击了天体对象
    CelestialObject? tappedObject;
    for (final object in widget.celestialObjects) {
      if (object.containsPoint(tapPosition)) {
        tappedObject = object;
        break;
      }
    }
    
    if (tappedObject != null) {
      widget.onObjectTap?.call(tappedObject);
    } else {
      widget.onTap?.call(tapPosition);
    }
    
    // 更新焦点
    setState(() {
      _focusPoint = tapPosition;
    });
  }
  
  void _handleScaleUpdate(ScaleUpdateDetails details) {
    setState(() {
      _zoomLevel = (_zoomLevel * details.scale).clamp(0.1, 5.0);
    });
  }
}