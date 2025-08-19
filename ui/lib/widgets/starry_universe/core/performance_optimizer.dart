/// 性能优化器 - 智能优化星空渲染性能
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:vector_math/vector_math.dart' as vm;
import 'cosmic_theme.dart';
import 'starry_canvas.dart';
import 'particle_system.dart';

/// 性能级别枚举
enum PerformanceLevel {
  ultra,    // 超高质量
  high,     // 高质量
  medium,   // 中等质量
  low,      // 低质量
  potato,   // 极低质量（确保流畅）
}

/// LOD (Level of Detail) 管理器
class LODManager {
  final Map<String, int> _objectLODLevels = {};
  double _currentZoomLevel = 1.0;
  PerformanceLevel _performanceLevel = PerformanceLevel.high;
  
  /// 设置缩放级别
  void setZoomLevel(double zoomLevel) {
    _currentZoomLevel = zoomLevel;
    _updateLODLevels();
  }
  
  /// 设置性能级别
  void setPerformanceLevel(PerformanceLevel level) {
    _performanceLevel = level;
    _updateLODLevels();
  }
  
  /// 获取对象的LOD级别
  int getLODLevel(String objectId) {
    return _objectLODLevels[objectId] ?? 0;
  }
  
  /// 更新所有对象的LOD级别
  void _updateLODLevels() {
    // 根据缩放级别和性能设置确定LOD
    final baseLOD = _getBaseLODFromZoom(_currentZoomLevel);
    final performanceAdjustment = _getPerformanceAdjustment(_performanceLevel);
    
    // 这里可以根据具体对象类型设置不同的LOD
    _objectLODLevels.clear();
    _objectLODLevels['particles'] = (baseLOD + performanceAdjustment).clamp(0, 3);
    _objectLODLevels['stars'] = (baseLOD + performanceAdjustment).clamp(0, 3);
    _objectLODLevels['connections'] = (baseLOD + performanceAdjustment).clamp(0, 2);
  }
  
  /// 根据缩放级别获取基础LOD
  int _getBaseLODFromZoom(double zoom) {
    if (zoom < 0.25) return 0;  // 最远视图，最低细节
    if (zoom < 0.5) return 1;   // 远视图
    if (zoom < 2.0) return 2;   // 正常视图
    return 3;                   // 近视图，最高细节
  }
  
  /// 根据性能级别获取调整值
  int _getPerformanceAdjustment(PerformanceLevel level) {
    switch (level) {
      case PerformanceLevel.ultra:
        return 1;
      case PerformanceLevel.high:
        return 0;
      case PerformanceLevel.medium:
        return -1;
      case PerformanceLevel.low:
        return -2;
      case PerformanceLevel.potato:
        return -3;
    }
  }
  
  /// 检查对象是否应该渲染
  bool shouldRender(String objectType, vm.Vector2 position, Size viewport) {
    final lodLevel = getLODLevel(objectType);
    
    // 基于LOD级别决定渲染策略
    switch (lodLevel) {
      case 0: // 最低LOD - 只渲染关键对象
        return _isInViewportCenter(position, viewport);
      case 1: // 低LOD - 渲染可见区域的主要对象
        return _isInViewport(position, viewport, 1.2);
      case 2: // 中等LOD - 渲染可见区域及边界
        return _isInViewport(position, viewport, 1.5);
      case 3: // 高LOD - 渲染所有可能可见的对象
        return _isInViewport(position, viewport, 2.0);
      default:
        return false;
    }
  }
  
  /// 检查对象是否在视口中心区域
  bool _isInViewportCenter(vm.Vector2 position, Size viewport) {
    final centerX = viewport.width / 2;
    final centerY = viewport.height / 2;
    final distance = math.sqrt(
      math.pow(position.x - centerX, 2) + math.pow(position.y - centerY, 2)
    );
    return distance < math.min(viewport.width, viewport.height) * 0.25;
  }
  
  /// 检查对象是否在扩展视口内
  bool _isInViewport(vm.Vector2 position, Size viewport, double expansionFactor) {
    final expandedWidth = viewport.width * expansionFactor;
    final expandedHeight = viewport.height * expansionFactor;
    final offsetX = (expandedWidth - viewport.width) / 2;
    final offsetY = (expandedHeight - viewport.height) / 2;
    
    return position.x >= -offsetX &&
           position.x <= viewport.width + offsetX &&
           position.y >= -offsetY &&
           position.y <= viewport.height + offsetY;
  }
}

/// 空间索引 - 四叉树实现
class SpatialIndex {
  late QuadTreeNode _root;
  final List<CelestialObject> _allObjects = [];
  
  /// 初始化空间索引
  void initialize(Rect bounds) {
    _root = QuadTreeNode(bounds);
  }
  
  /// 添加对象到索引
  void addObject(CelestialObject object) {
    _allObjects.add(object);
    _root.insert(object);
  }
  
  /// 移除对象
  void removeObject(CelestialObject object) {
    _allObjects.remove(object);
    rebuild();
  }
  
  /// 查询指定区域内的对象
  List<CelestialObject> queryRegion(Rect region) {
    return _root.query(region);
  }
  
  /// 查询可见对象
  List<CelestialObject> queryVisible(Rect viewport) {
    return _root.query(viewport);
  }
  
  /// 重建索引
  void rebuild() {
    if (_allObjects.isEmpty) return;
    
    // 计算所有对象的边界
    double minX = double.infinity;
    double minY = double.infinity;
    double maxX = double.negativeInfinity;
    double maxY = double.negativeInfinity;
    
    for (final object in _allObjects) {
      minX = math.min(minX, object.position.x);
      minY = math.min(minY, object.position.y);
      maxX = math.max(maxX, object.position.x);
      maxY = math.max(maxY, object.position.y);
    }
    
    // 重新初始化根节点
    final bounds = Rect.fromLTRB(minX - 100, minY - 100, maxX + 100, maxY + 100);
    _root = QuadTreeNode(bounds);
    
    // 重新插入所有对象
    for (final object in _allObjects) {
      _root.insert(object);
    }
  }
  
  /// 清空索引
  void clear() {
    _allObjects.clear();
    _root = QuadTreeNode(Rect.zero);
  }
}

/// 四叉树节点
class QuadTreeNode {
  final Rect bounds;
  final List<CelestialObject> objects = [];
  List<QuadTreeNode>? children;
  
  static const int maxObjects = 10;
  static const int maxDepth = 8;
  int depth = 0;
  
  QuadTreeNode(this.bounds, [this.depth = 0]);
  
  /// 插入对象
  void insert(CelestialObject object) {
    if (!_containsPoint(object.position)) {
      return;
    }
    
    if (objects.length < maxObjects || depth >= maxDepth) {
      objects.add(object);
    } else {
      if (children == null) {
        _subdivide();
      }
      
      for (final child in children!) {
        child.insert(object);
      }
    }
  }
  
  /// 查询区域内的对象
  List<CelestialObject> query(Rect region) {
    final result = <CelestialObject>[];
    
    if (!bounds.overlaps(region)) {
      return result;
    }
    
    for (final object in objects) {
      if (region.contains(Offset(object.position.x, object.position.y))) {
        result.add(object);
      }
    }
    
    if (children != null) {
      for (final child in children!) {
        result.addAll(child.query(region));
      }
    }
    
    return result;
  }
  
  /// 细分节点
  void _subdivide() {
    final x = bounds.left;
    final y = bounds.top;
    final w = bounds.width / 2;
    final h = bounds.height / 2;
    
    children = [
      QuadTreeNode(Rect.fromLTWH(x, y, w, h), depth + 1),         // 左上
      QuadTreeNode(Rect.fromLTWH(x + w, y, w, h), depth + 1),     // 右上
      QuadTreeNode(Rect.fromLTWH(x, y + h, w, h), depth + 1),     // 左下
      QuadTreeNode(Rect.fromLTWH(x + w, y + h, w, h), depth + 1), // 右下
    ];
  }
  
  /// 检查点是否在边界内
  bool _containsPoint(vm.Vector2 point) {
    return bounds.contains(Offset(point.x, point.y));
  }
}

/// 性能监控器
class PerformanceMonitor {
  final List<double> _frameTimes = [];
  final int _maxSamples = 60;
  double _averageFPS = 60.0;
  double _averageFrameTime = 16.67; // ms
  int _frameCount = 0;
  DateTime? _lastFrameTime;
  
  // 性能阈值
  static const double targetFPS = 60.0;
  static const double minimumFPS = 30.0;
  static const double maxFrameTime = 33.33; // ms (30 FPS)
  
  /// 记录帧时间
  void recordFrame() {
    final now = DateTime.now();
    if (_lastFrameTime != null) {
      final frameTime = now.difference(_lastFrameTime!).inMicroseconds / 1000.0;
      _frameTimes.add(frameTime);
      
      if (_frameTimes.length > _maxSamples) {
        _frameTimes.removeAt(0);
      }
      
      _updateMetrics();
    }
    _lastFrameTime = now;
    _frameCount++;
  }
  
  /// 更新性能指标
  void _updateMetrics() {
    if (_frameTimes.isEmpty) return;
    
    _averageFrameTime = _frameTimes.reduce((a, b) => a + b) / _frameTimes.length;
    _averageFPS = 1000.0 / _averageFrameTime;
  }
  
  /// 获取当前FPS
  double get currentFPS => _averageFPS;
  
  /// 获取平均帧时间
  double get currentFrameTime => _averageFrameTime;
  
  /// 检查性能是否良好
  bool get isPerformanceGood => _averageFPS >= minimumFPS;
  
  /// 获取建议的性能级别
  PerformanceLevel getSuggestedPerformanceLevel() {
    if (_averageFPS >= 55) {
      return PerformanceLevel.ultra;
    } else if (_averageFPS >= 45) {
      return PerformanceLevel.high;
    } else if (_averageFPS >= 35) {
      return PerformanceLevel.medium;
    } else if (_averageFPS >= 25) {
      return PerformanceLevel.low;
    } else {
      return PerformanceLevel.potato;
    }
  }
  
  /// 重置统计
  void reset() {
    _frameTimes.clear();
    _frameCount = 0;
    _lastFrameTime = null;
    _averageFPS = 60.0;
    _averageFrameTime = 16.67;
  }
}

/// 自适应质量管理器
class AdaptiveQualityManager {
  final PerformanceMonitor _monitor = PerformanceMonitor();
  final LODManager _lodManager = LODManager();
  PerformanceLevel _currentLevel = PerformanceLevel.high;
  
  // 自适应参数
  int _poorPerformanceFrames = 0;
  int _goodPerformanceFrames = 0;
  static const int adjustmentThreshold = 30; // 连续帧数阈值
  
  PerformanceMonitor get monitor => _monitor;
  LODManager get lodManager => _lodManager;
  PerformanceLevel get currentLevel => _currentLevel;
  
  /// 更新性能监控
  void update() {
    _monitor.recordFrame();
    
    // 检查是否需要调整质量
    if (_monitor.isPerformanceGood) {
      _poorPerformanceFrames = 0;
      _goodPerformanceFrames++;
      
      if (_goodPerformanceFrames >= adjustmentThreshold) {
        _tryIncreaseQuality();
        _goodPerformanceFrames = 0;
      }
    } else {
      _goodPerformanceFrames = 0;
      _poorPerformanceFrames++;
      
      if (_poorPerformanceFrames >= adjustmentThreshold) {
        _decreaseQuality();
        _poorPerformanceFrames = 0;
      }
    }
  }
  
  /// 尝试提高质量
  void _tryIncreaseQuality() {
    final suggestedLevel = _monitor.getSuggestedPerformanceLevel();
    if (suggestedLevel.index > _currentLevel.index) {
      _currentLevel = PerformanceLevel.values[
        math.min(_currentLevel.index + 1, PerformanceLevel.values.length - 1)
      ];
      _lodManager.setPerformanceLevel(_currentLevel);
    }
  }
  
  /// 降低质量
  void _decreaseQuality() {
    _currentLevel = PerformanceLevel.values[
      math.max(_currentLevel.index - 1, 0)
    ];
    _lodManager.setPerformanceLevel(_currentLevel);
  }
  
  /// 手动设置质量级别
  void setQualityLevel(PerformanceLevel level) {
    _currentLevel = level;
    _lodManager.setPerformanceLevel(level);
    _poorPerformanceFrames = 0;
    _goodPerformanceFrames = 0;
  }
}

/// 内存管理器
class MemoryManager {
  final Map<String, dynamic> _cache = {};
  int _maxCacheSize = 100;
  int _cacheAccessCounter = 0;
  
  /// 设置最大缓存大小
  void setMaxCacheSize(int size) {
    _maxCacheSize = size;
    _evictIfNeeded();
  }
  
  /// 缓存对象
  void cache(String key, dynamic value) {
    _cache[key] = {
      'value': value,
      'accessTime': DateTime.now(),
      'accessCount': 1,
    };
    _evictIfNeeded();
  }
  
  /// 获取缓存对象
  T? getCached<T>(String key) {
    final entry = _cache[key];
    if (entry != null) {
      entry['accessTime'] = DateTime.now();
      entry['accessCount'] = (entry['accessCount'] as int) + 1;
      return entry['value'] as T?;
    }
    return null;
  }
  
  /// 检查是否有缓存
  bool hasCached(String key) {
    return _cache.containsKey(key);
  }
  
  /// 清除缓存
  void clearCache() {
    _cache.clear();
  }
  
  /// 必要时驱逐缓存项
  void _evictIfNeeded() {
    if (_cache.length <= _maxCacheSize) return;
    
    // LRU 驱逐策略
    final entries = _cache.entries.toList();
    entries.sort((a, b) {
      final aTime = a.value['accessTime'] as DateTime;
      final bTime = b.value['accessTime'] as DateTime;
      return aTime.compareTo(bTime);
    });
    
    // 移除最少使用的条目
    final toRemove = entries.length - _maxCacheSize;
    for (int i = 0; i < toRemove; i++) {
      _cache.remove(entries[i].key);
    }
  }
}

/// 批处理管理器
class BatchManager {
  final List<void Function()> _renderBatch = [];
  final List<void Function()> _updateBatch = [];
  
  /// 添加渲染任务到批处理
  void addRenderTask(void Function() task) {
    _renderBatch.add(task);
  }
  
  /// 添加更新任务到批处理
  void addUpdateTask(void Function() task) {
    _updateBatch.add(task);
  }
  
  /// 执行渲染批处理
  void executeRenderBatch() {
    for (final task in _renderBatch) {
      task();
    }
    _renderBatch.clear();
  }
  
  /// 执行更新批处理
  void executeUpdateBatch() {
    for (final task in _updateBatch) {
      task();
    }
    _updateBatch.clear();
  }
  
  /// 清空所有批处理
  void clearBatches() {
    _renderBatch.clear();
    _updateBatch.clear();
  }
}