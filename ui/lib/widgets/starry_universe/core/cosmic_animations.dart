/// 宇宙动画协调系统 - 管理多个动画控制器的同步和协调
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:vector_math/vector_math.dart' as vm;
import 'cosmic_theme.dart';

/// 数据变化事件类型
enum DataChangeType {
  newEntity,           // 新实体创建
  entityUpdate,        // 实体更新
  strongConnection,    // 强连接形成
  clusterFormation,    // 聚类形成
  searchQuery,         // 搜索查询
  userInteraction,     // 用户交互
}

/// 数据变化事件
class DataChangeEvent {
  final DataChangeType type;
  final String? entityId;
  final Map<String, dynamic> metadata;
  final vm.Vector2? position;
  
  const DataChangeEvent({
    required this.type,
    this.entityId,
    this.metadata = const {},
    this.position,
  });
}

/// 宇宙动画控制器 - 协调多个动画
class CosmicAnimationController extends ChangeNotifier {
  // 主要动画控制器
  late AnimationController _starPulseController;
  late AnimationController _orbitController;
  late AnimationController _nebulaFlowController;
  late AnimationController _cameraController;
  
  // 动画值
  late Animation<double> _starPulse;
  late Animation<double> _orbitRotation;
  late Animation<double> _nebulaFlow;
  late Animation<Offset> _cameraPosition;
  
  // 状态
  bool _isInitialized = false;
  double _globalTimeScale = 1.0;
  vm.Vector2 _focusPoint = vm.Vector2.zero();
  
  // 获取器
  bool get isInitialized => _isInitialized;
  double get starPulseValue => _starPulse.value;
  double get orbitRotationValue => _orbitRotation.value;
  double get nebulaFlowValue => _nebulaFlow.value;
  Offset get cameraPositionValue => _cameraPosition.value;
  double get globalTimeScale => _globalTimeScale;
  vm.Vector2 get focusPoint => _focusPoint;
  
  /// 初始化动画控制器
  void initialize(TickerProvider vsync) {
    if (_isInitialized) return;
    
    // 星体脉动动画
    _starPulseController = AnimationController(
      duration: CosmicAnimationConfig.starPulseDuration,
      vsync: vsync,
    );
    _starPulse = Tween<double>(
      begin: 0.0,
      end: 2 * math.pi,
    ).animate(CurvedAnimation(
      parent: _starPulseController,
      curve: CosmicAnimationConfig.starPulseCurve,
    ));
    
    // 轨道旋转动画
    _orbitController = AnimationController(
      duration: CosmicAnimationConfig.orbitDuration,
      vsync: vsync,
    );
    _orbitRotation = Tween<double>(
      begin: 0.0,
      end: 2 * math.pi,
    ).animate(CurvedAnimation(
      parent: _orbitController,
      curve: CosmicAnimationConfig.orbitCurve,
    ));
    
    // 星云流动动画
    _nebulaFlowController = AnimationController(
      duration: CosmicAnimationConfig.nebulaDrift,
      vsync: vsync,
    );
    _nebulaFlow = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _nebulaFlowController,
      curve: CosmicAnimationConfig.nebulaFlowCurve,
    ));
    
    // 相机移动动画
    _cameraController = AnimationController(
      duration: const Duration(seconds: 3),
      vsync: vsync,
    );
    _cameraPosition = Tween<Offset>(
      begin: Offset.zero,
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _cameraController,
      curve: Curves.easeInOutCubic,
    ));
    
    // 启动循环动画
    _starPulseController.repeat();
    _orbitController.repeat();
    _nebulaFlowController.repeat();
    
    _isInitialized = true;
    notifyListeners();
  }
  
  /// 设置全局时间缩放
  void setTimeScale(double scale) {
    _globalTimeScale = scale.clamp(0.1, 5.0);
    
    // 应用时间缩放到所有动画
    if (_isInitialized) {
      _starPulseController.duration = Duration(
        milliseconds: (CosmicAnimationConfig.starPulseDuration.inMilliseconds / scale).round(),
      );
      _orbitController.duration = Duration(
        milliseconds: (CosmicAnimationConfig.orbitDuration.inMilliseconds / scale).round(),
      );
      _nebulaFlowController.duration = Duration(
        milliseconds: (CosmicAnimationConfig.nebulaDrift.inMilliseconds / scale).round(),
      );
    }
    
    notifyListeners();
  }
  
  /// 设置焦点位置
  void setFocusPoint(vm.Vector2 point) {
    _focusPoint = point;
    notifyListeners();
  }
  
  /// 相机移动到指定位置
  void moveCameraTo(Offset target, {Duration? duration}) {
    if (!_isInitialized) return;
    
    _cameraController.duration = duration ?? const Duration(seconds: 2);
    _cameraPosition = Tween<Offset>(
      begin: _cameraPosition.value,
      end: target,
    ).animate(CurvedAnimation(
      parent: _cameraController,
      curve: Curves.easeInOutCubic,
    ));
    
    _cameraController.forward(from: 0.0);
  }
  
  /// 响应数据变化事件
  void respondToDataChange(DataChangeEvent event) {
    switch (event.type) {
      case DataChangeType.newEntity:
        _triggerStarBirth(event.position);
        break;
      case DataChangeType.strongConnection:
        _triggerBinaryStarFormation();
        break;
      case DataChangeType.clusterFormation:
        _triggerGalaxyFormation();
        break;
      case DataChangeType.searchQuery:
        _triggerSearchAnimation();
        break;
      case DataChangeType.userInteraction:
        _triggerInteractionFeedback(event.position);
        break;
      case DataChangeType.entityUpdate:
        _triggerEntityUpdateAnimation();
        break;
    }
  }
  
  /// 触发星体诞生动画
  void _triggerStarBirth(vm.Vector2? position) {
    if (position != null) {
      setFocusPoint(position);
    }
    
    // 短暂加速脉动
    setTimeScale(2.0);
    Future.delayed(const Duration(seconds: 2), () {
      setTimeScale(1.0);
    });
  }
  
  /// 触发双星系统形成动画
  void _triggerBinaryStarFormation() {
    // 加速轨道动画
    setTimeScale(1.5);
    Future.delayed(const Duration(seconds: 3), () {
      setTimeScale(1.0);
    });
  }
  
  /// 触发星系形成动画
  void _triggerGalaxyFormation() {
    // 相机后退以显示更大范围
    moveCameraTo(const Offset(0, -100), duration: const Duration(seconds: 4));
    
    // 减慢所有动画以显示形成过程
    setTimeScale(0.5);
    Future.delayed(const Duration(seconds: 5), () {
      setTimeScale(1.0);
      moveCameraTo(Offset.zero);
    });
  }
  
  /// 触发搜索动画
  void _triggerSearchAnimation() {
    // 快速脉动表示搜索活动
    setTimeScale(3.0);
    Future.delayed(const Duration(milliseconds: 500), () {
      setTimeScale(1.0);
    });
  }
  
  /// 触发交互反馈动画
  void _triggerInteractionFeedback(vm.Vector2? position) {
    if (position != null) {
      setFocusPoint(position);
    }
    
    // 短暂的脉动反馈
    setTimeScale(1.5);
    Future.delayed(const Duration(milliseconds: 300), () {
      setTimeScale(1.0);
    });
  }
  
  /// 触发实体更新动画
  void _triggerEntityUpdateAnimation() {
    // 轻微的星云流动变化
    setTimeScale(1.2);
    Future.delayed(const Duration(seconds: 1), () {
      setTimeScale(1.0);
    });
  }
  
  /// 同步所有动画
  void synchronizeAnimations() {
    if (!_isInitialized) return;
    
    final mainBeat = _starPulse.value;
    
    // 所有动画基于主节拍同步
    // 轨道动画是脉动的两倍速度
    if (_orbitController.status == AnimationStatus.forward) {
      final expectedOrbitValue = (mainBeat * 2) % (2 * math.pi);
      // 这里可以添加同步逻辑，但通常让AnimationController自然运行更好
    }
    
    // 星云流动基于脉动创建波动效果
    final nebulaPhase = math.sin(mainBeat);
    // 可以通过自定义Animation或直接在绘制时使用这个值
  }
  
  /// 暂停所有动画
  void pauseAll() {
    if (!_isInitialized) return;
    
    _starPulseController.stop();
    _orbitController.stop();
    _nebulaFlowController.stop();
    _cameraController.stop();
  }
  
  /// 恢复所有动画
  void resumeAll() {
    if (!_isInitialized) return;
    
    _starPulseController.repeat();
    _orbitController.repeat();
    _nebulaFlowController.repeat();
  }
  
  /// 重置所有动画
  void resetAll() {
    if (!_isInitialized) return;
    
    _starPulseController.reset();
    _orbitController.reset();
    _nebulaFlowController.reset();
    _cameraController.reset();
    
    _focusPoint = vm.Vector2.zero();
    _globalTimeScale = 1.0;
    
    notifyListeners();
  }
  
  /// 释放资源
  @override
  void dispose() {
    if (_isInitialized) {
      _starPulseController.dispose();
      _orbitController.dispose();
      _nebulaFlowController.dispose();
      _cameraController.dispose();
    }
    super.dispose();
  }
}

/// 预定义动画序列
class CosmicAnimationSequences {
  /// 应用启动动画序列
  static Future<void> playStartupSequence(CosmicAnimationController controller) async {
    // 1. 宇宙大爆炸效果
    controller.setTimeScale(0.1);
    await Future.delayed(const Duration(milliseconds: 500));
    
    // 2. 快速展开
    controller.setTimeScale(5.0);
    await Future.delayed(const Duration(milliseconds: 800));
    
    // 3. 稳定状态
    controller.setTimeScale(1.0);
  }
  
  /// 搜索动画序列
  static Future<void> playSearchSequence(CosmicAnimationController controller, vm.Vector2 searchCenter) async {
    // 1. 聚焦搜索区域
    controller.setFocusPoint(searchCenter);
    controller.moveCameraTo(Offset(searchCenter.x, searchCenter.y));
    
    // 2. 快速脉动表示搜索进行中
    controller.setTimeScale(3.0);
    await Future.delayed(const Duration(milliseconds: 1000));
    
    // 3. 恢复正常
    controller.setTimeScale(1.0);
  }
  
  /// 发现新连接动画序列
  static Future<void> playDiscoverySequence(CosmicAnimationController controller, List<vm.Vector2> connectionPoints) async {
    // 1. 高亮显示连接点
    for (final point in connectionPoints) {
      controller.setFocusPoint(point);
      controller.setTimeScale(2.0);
      await Future.delayed(const Duration(milliseconds: 300));
    }
    
    // 2. 形成连接动画
    controller.setTimeScale(0.8);
    await Future.delayed(const Duration(milliseconds: 2000));
    
    // 3. 恢复
    controller.setTimeScale(1.0);
  }
  
  /// 数据更新动画序列
  static Future<void> playDataUpdateSequence(CosmicAnimationController controller) async {
    // 温和的脉动表示数据刷新
    controller.setTimeScale(1.3);
    await Future.delayed(const Duration(milliseconds: 1500));
    controller.setTimeScale(1.0);
  }
}

/// 动画事件监听器
mixin CosmicAnimationListener {
  /// 当动画状态改变时调用
  void onAnimationStateChanged(AnimationStatus status) {}
  
  /// 当焦点改变时调用
  void onFocusPointChanged(vm.Vector2 newFocus) {}
  
  /// 当时间缩放改变时调用
  void onTimeScaleChanged(double newScale) {}
  
  /// 当相机位置改变时调用
  void onCameraPositionChanged(Offset newPosition) {}
}

/// 性能监控的动画控制器包装器
class PerformanceAwareAnimationController extends CosmicAnimationController {
  double _lastFrameTime = 0.0;
  double _frameTimeSum = 0.0;
  int _frameCount = 0;
  double _averageFPS = 60.0;
  
  double get averageFPS => _averageFPS;
  
  @override
  void setTimeScale(double scale) {
    // 根据性能动态调整时间缩放
    final adjustedScale = _performanceAdjustedScale(scale);
    super.setTimeScale(adjustedScale);
  }
  
  double _performanceAdjustedScale(double requestedScale) {
    // 如果FPS低于30，减少动画复杂度
    if (_averageFPS < 30) {
      return requestedScale * 0.5;
    }
    // 如果FPS高于55，可以提高动画质量
    else if (_averageFPS > 55) {
      return requestedScale * 1.1;
    }
    return requestedScale;
  }
  
  void updatePerformanceMetrics(double currentFrameTime) {
    _frameCount++;
    _frameTimeSum += currentFrameTime;
    
    // 每60帧计算一次平均FPS
    if (_frameCount >= 60) {
      _averageFPS = 60.0 / (_frameTimeSum / _frameCount);
      _frameCount = 0;
      _frameTimeSum = 0.0;
    }
  }
}