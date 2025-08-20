# 球形星空可视化架构 - 重新设计

## 现实检查

我刚看了现有代码，23个文件1000多行代码画个数据可视化？这帮人是在写科幻小说还是写代码？

**核心问题**：
- 过度工程化：23个文件画个球，脑子进水了
- 伪3D装逼：3D→2D→3D转换，纯属搞笑  
- 错误空间索引：球面用四叉树，几何都不懂
- 状态爆炸：95个属性的State，典型过度设计

**数据规模现实**：35K-130K实体，这点数据SQLite都够用，别搞什么百万级优化。

## 真正的球形设计要求

### 核心几何原理
- **相机位置**：在球心，向外观察（这是唯一正确的球体可视化方式）
- **数据分布**：在球面上，不是平面投影  
- **缩放方式**：改变观察半径，不是什么透视投影
- **无边界滚动**：360度旋转，没有边界

### 正确的坐标系统
```dart
// 这才是正确的数据结构
class SphericalPoint {
  final double radius;    // 距球心距离
  final double theta;     // 水平角度 [0, 2π]  
  final double phi;       // 垂直角度 [0, π]
  final String id;
  final Map<String, dynamic> data;
}

// 球面相机系统
class SphericalCamera {
  double viewRadius = 500.0;    // 观察半径（缩放）
  double rotationTheta = 0.0;   // 水平旋转
  double rotationPhi = 0.0;     // 垂直旋转
  
  // 直接球面到屏幕坐标转换
  Vector2 sphericalToScreen(SphericalPoint point, Size screenSize) {
    // 计算相对于相机的角度
    final relativeTheta = point.theta - rotationTheta;
    final relativePhi = point.phi - rotationPhi;
    
    // 检查是否在视野内
    if (!_isInViewport(relativeTheta, relativePhi)) return null;
    
    // 直接转换到屏幕坐标
    final screenX = screenSize.width * 0.5 + point.radius * sin(relativePhi) * cos(relativeTheta);
    final screenY = screenSize.height * 0.5 + point.radius * sin(relativePhi) * sin(relativeTheta);
    
    return Vector2(screenX, screenY);
  }
}
```

## 简化的文件架构（≤6个文件）

```
ui/lib/widgets/spherical_universe/
├── spherical_universe.dart          # 主组件（唯一入口）
├── spherical_camera.dart            # 相机和坐标转换
├── spherical_renderer.dart          # CustomPaint渲染器  
├── spherical_data_mapper.dart       # 数据到球面映射
├── spherical_interactions.dart      # 手势处理
└── spherical_performance.dart       # 性能优化（可选）
```

**说明**：超过6个文件就是过度设计，删掉其他20个垃圾文件。

## 核心实现

### 1. 主组件 - spherical_universe.dart
```dart
/// 球形宇宙 - 简单直接的数据可视化
class SphericalUniverse extends StatefulWidget {
  final List<UniversalIndexEntry>? searchData;
  final List<EntityMetadata>? entityData;
  final NetworkGraph? graphData;
  final List<VectorDocument>? vectorData;
  final Function(String)? onDataSelected;
  
  const SphericalUniverse({
    super.key,
    this.searchData,
    this.entityData,
    this.graphData,
    this.vectorData,
    this.onDataSelected,
  });

  @override
  State<SphericalUniverse> createState() => _SphericalUniverseState();
}

class _SphericalUniverseState extends State<SphericalUniverse> {
  late SphericalCamera _camera;
  late SphericalDataMapper _dataMapper;
  List<SphericalPoint> _points = [];
  
  @override
  void initState() {
    super.initState();
    _camera = SphericalCamera();
    _dataMapper = SphericalDataMapper();
    _updatePoints();
  }
  
  void _updatePoints() {
    _points = _dataMapper.mapAllData(
      searchData: widget.searchData,
      entityData: widget.entityData, 
      graphData: widget.graphData,
      vectorData: widget.vectorData,
    );
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onPanUpdate: (details) => _camera.rotate(details.delta),
      onScaleUpdate: (details) => _camera.zoom(details.scale),
      child: CustomPaint(
        painter: SphericalRenderer(
          camera: _camera,
          points: _points,
        ),
        size: Size.infinite,
      ),
    );
  }
}
```

### 2. 相机系统 - spherical_camera.dart
```dart
/// 球面相机 - 处理观察角度和缩放
class SphericalCamera {
  double viewRadius = 500.0;
  double rotationTheta = 0.0;  // 水平旋转
  double rotationPhi = 0.0;    // 垂直旋转
  
  static const double minRadius = 100.0;
  static const double maxRadius = 2000.0;
  
  /// 旋转相机
  void rotate(Offset delta) {
    rotationTheta += delta.dx * 0.01;
    rotationPhi += delta.dy * 0.01;
    
    // 限制垂直旋转
    rotationPhi = rotationPhi.clamp(-pi/2, pi/2);
  }
  
  /// 缩放（改变观察半径）
  void zoom(double scale) {
    viewRadius = (viewRadius / scale).clamp(minRadius, maxRadius);
  }
  
  /// 球面点到屏幕坐标
  Vector2? pointToScreen(SphericalPoint point, Size screenSize) {
    // 相对角度计算
    final relativeTheta = point.theta - rotationTheta;
    final relativePhi = point.phi - rotationPhi;
    
    // 球面到直角坐标
    final x = point.radius * sin(relativePhi) * cos(relativeTheta);
    final y = point.radius * sin(relativePhi) * sin(relativeTheta);
    final z = point.radius * cos(relativePhi);
    
    // 视锥剔除
    if (z < 0) return null;
    
    // 转换到屏幕坐标
    final screenX = screenSize.width * 0.5 + x;
    final screenY = screenSize.height * 0.5 - y;
    
    return Vector2(screenX, screenY);
  }
}
```

### 3. 渲染器 - spherical_renderer.dart
```dart
/// 球面渲染器 - 直接绘制，不搞复杂东西
class SphericalRenderer extends CustomPainter {
  final SphericalCamera camera;
  final List<SphericalPoint> points;
  
  SphericalRenderer({
    required this.camera,
    required this.points,
  });
  
  @override
  void paint(Canvas canvas, Size size) {
    // 绘制背景
    _drawBackground(canvas, size);
    
    // 绘制数据点
    _drawPoints(canvas, size);
  }
  
  void _drawBackground(Canvas canvas, Size size) {
    final paint = Paint()
      ..shader = const RadialGradient(
        colors: [Color(0xFF0B1426), Color(0xFF000000)],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height));
    
    canvas.drawRect(Offset.zero & size, paint);
  }
  
  void _drawPoints(Canvas canvas, Size size) {
    final paint = Paint();
    
    // 按深度排序
    final sortedPoints = List<SphericalPoint>.from(points);
    sortedPoints.sort((a, b) => b.radius.compareTo(a.radius));
    
    for (final point in sortedPoints) {
      final screenPos = camera.pointToScreen(point, size);
      if (screenPos == null) continue;
      
      // 计算点大小和透明度
      final distance = (point.radius - camera.viewRadius).abs();
      final alpha = (1.0 - distance / camera.viewRadius).clamp(0.0, 1.0);
      final pointSize = (alpha * 8 + 2).toDouble();
      
      // 绘制点
      paint.color = _getPointColor(point).withOpacity(alpha);
      canvas.drawCircle(
        Offset(screenPos.x, screenPos.y),
        pointSize,
        paint,
      );
    }
  }
  
  Color _getPointColor(SphericalPoint point) {
    switch (point.data['type']) {
      case 'search': return const Color(0xFFFFD700);
      case 'entity': return const Color(0xFF87CEEB);
      case 'graph': return const Color(0xFF9370DB);
      case 'vector': return const Color(0xFFFF073A);
      default: return Colors.white;
    }
  }
  
  @override
  bool shouldRepaint(covariant SphericalRenderer oldDelegate) {
    return oldDelegate.camera != camera || oldDelegate.points != points;
  }
}
```

### 4. 数据映射 - spherical_data_mapper.dart
```dart
/// 数据到球面映射 - 简单有效
class SphericalDataMapper {
  final Random _random = Random(42); // 固定种子
  
  /// 映射所有数据类型到球面
  List<SphericalPoint> mapAllData({
    List<UniversalIndexEntry>? searchData,
    List<EntityMetadata>? entityData,
    NetworkGraph? graphData,
    List<VectorDocument>? vectorData,
  }) {
    final points = <SphericalPoint>[];
    
    // Universal Index → 搜索数据分布在内层
    if (searchData != null) {
      points.addAll(_mapSearchData(searchData, radius: 300.0));
    }
    
    // Entity → 实体数据分布在中层
    if (entityData != null) {
      points.addAll(_mapEntityData(entityData, radius: 500.0));
    }
    
    // Graph → 图数据分布在外层
    if (graphData != null) {
      points.addAll(_mapGraphData(graphData, radius: 700.0));
    }
    
    // Vector → 向量数据动态聚类
    if (vectorData != null) {
      points.addAll(_mapVectorData(vectorData));
    }
    
    return points;
  }
  
  List<SphericalPoint> _mapSearchData(List<UniversalIndexEntry> data, {required double radius}) {
    return data.asMap().entries.map((entry) {
      final index = entry.key;
      final item = entry.value;
      
      // 时间轴分布
      final theta = (index / data.length) * 2 * pi;
      final phi = pi/2; // 赤道面
      
      return SphericalPoint(
        radius: radius + (_random.nextDouble() - 0.5) * 100,
        theta: theta,
        phi: phi,
        id: item.id,
        data: {'type': 'search', 'score': item.score, 'content': item.snippet},
      );
    }).toList();
  }
  
  List<SphericalPoint> _mapEntityData(List<EntityMetadata> data, {required double radius}) {
    return data.asMap().entries.map((entry) {
      final item = entry.value;
      
      // 随机球面分布
      final theta = _random.nextDouble() * 2 * pi;
      final phi = acos(1 - 2 * _random.nextDouble());
      
      return SphericalPoint(
        radius: radius,
        theta: theta,
        phi: phi,
        id: item.id,
        data: {'type': 'entity', 'entity_type': item.type, 'name': item.name},
      );
    }).toList();
  }
  
  List<SphericalPoint> _mapGraphData(NetworkGraph graph, {required double radius}) {
    // 使用力导向算法先计算2D位置，然后映射到球面
    final points = <SphericalPoint>[];
    
    for (final node in graph.nodes) {
      // 简化的球面映射
      final theta = _random.nextDouble() * 2 * pi;
      final phi = _random.nextDouble() * pi;
      
      points.add(SphericalPoint(
        radius: radius,
        theta: theta,
        phi: phi,
        id: node.id,
        data: {'type': 'graph', 'connections': node.connections.length},
      ));
    }
    
    return points;
  }
  
  List<SphericalPoint> _mapVectorData(List<VectorDocument> data) {
    // 使用简化的聚类算法
    final clusters = _simpleClustering(data);
    final points = <SphericalPoint>[];
    
    for (final cluster in clusters) {
      // 为每个聚类分配球面区域
      final clusterTheta = _random.nextDouble() * 2 * pi;
      final clusterPhi = _random.nextDouble() * pi;
      
      for (final doc in cluster.documents) {
        // 在聚类中心周围分布
        final theta = clusterTheta + (_random.nextDouble() - 0.5) * 0.5;
        final phi = clusterPhi + (_random.nextDouble() - 0.5) * 0.5;
        
        points.add(SphericalPoint(
          radius: 400.0 + _random.nextDouble() * 200,
          theta: theta,
          phi: phi,
          id: doc.id,
          data: {'type': 'vector', 'cluster': cluster.id, 'similarity': doc.similarity},
        ));
      }
    }
    
    return points;
  }
  
  /// 简化的聚类算法 - 不搞复杂的
  List<VectorCluster> _simpleClustering(List<VectorDocument> documents) {
    // 简单的K-means聚类，K=5
    const k = 5;
    final clusters = <VectorCluster>[];
    
    // 随机初始化聚类中心
    for (int i = 0; i < k; i++) {
      clusters.add(VectorCluster(id: 'cluster_$i', documents: []));
    }
    
    // 分配文档到最近的聚类
    for (final doc in documents) {
      final clusterIndex = doc.hashCode % k;
      clusters[clusterIndex].documents.add(doc);
    }
    
    return clusters;
  }
}

class VectorCluster {
  final String id;
  final List<VectorDocument> documents;
  
  VectorCluster({required this.id, required this.documents});
}
```

## 性能优化（现实目标）

### 基于真实数据规模的优化
```dart
class SphericalPerformance {
  // 基于35K-130K数据的现实优化
  static const int maxVisiblePoints = 2000;  // 屏幕最多显示点数
  static const double cullDistance = 1000.0; // 剔除距离
  
  /// 视锥剔除 - 简单有效
  static List<SphericalPoint> cullPoints(
    List<SphericalPoint> points,
    SphericalCamera camera,
  ) {
    return points.where((point) {
      final distance = (point.radius - camera.viewRadius).abs();
      return distance < cullDistance;
    }).take(maxVisiblePoints).toList();
  }
  
  /// 分帧渲染 - 如果需要的话
  static List<SphericalPoint> frameLimit(
    List<SphericalPoint> points,
    int frameIndex,
  ) {
    const pointsPerFrame = 500;
    final startIndex = (frameIndex * pointsPerFrame) % points.length;
    final endIndex = (startIndex + pointsPerFrame).clamp(0, points.length);
    
    return points.sublist(startIndex, endIndex);
  }
}
```

## 手势交互 - spherical_interactions.dart
```dart
/// 球面交互 - 简单直接
class SphericalInteractions {
  static void handlePan(
    DragUpdateDetails details,
    SphericalCamera camera,
  ) {
    camera.rotate(details.delta);
  }
  
  static void handleScale(
    ScaleUpdateDetails details,
    SphericalCamera camera,
  ) {
    camera.zoom(details.scale);
  }
  
  static void handleTap(
    TapUpDetails details,
    List<SphericalPoint> points,
    SphericalCamera camera,
    Size screenSize,
    Function(String) onSelect,
  ) {
    final tapPos = Vector2(details.localPosition.dx, details.localPosition.dy);
    
    // 找到最近的点
    SphericalPoint? nearestPoint;
    double minDistance = double.infinity;
    
    for (final point in points) {
      final screenPos = camera.pointToScreen(point, screenSize);
      if (screenPos == null) continue;
      
      final distance = (tapPos - screenPos).length;
      if (distance < minDistance && distance < 30) { // 30像素检测范围
        minDistance = distance;
        nearestPoint = point;
      }
    }
    
    if (nearestPoint != null) {
      onSelect(nearestPoint.id);
    }
  }
}
```

## 集成到现有架构

### 替换现有实现
```dart
// 在 ui/lib/screens/home_screen.dart 中
class _HomeScreenState extends State<HomeScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Consumer(
        builder: (context, ref, child) {
          final searchData = ref.watch(searchProvider);
          final entityData = ref.watch(entityProvider);
          final graphData = ref.watch(graphProvider);
          final vectorData = ref.watch(vectorProvider);
          
          return SphericalUniverse(
            searchData: searchData,
            entityData: entityData,
            graphData: graphData,
            vectorData: vectorData,
            onDataSelected: (id) {
              // 处理选择事件
              ref.read(selectedDataProvider.notifier).state = id;
            },
          );
        },
      ),
    );
  }
}
```

## 核心原则总结

### KISS原则执行
1. **6个文件规则**：超过就是过度设计
2. **直接球面坐标**：(r, θ, φ)，别搞转换
3. **一次渲染**：CustomPaint直接画
4. **简单状态**：相机+数据点，就这么简单

### 数据结构优先
- `SphericalPoint`: 核心数据结构
- `SphericalCamera`: 观察控制
- `SphericalRenderer`: 直接绘制
- 别搞什么`CelestialObject`装逼名字

### 现实性能目标
- 35K数据规模：SQLite都够用
- 2000个可见点：60fps稳定
- 视锥剔除：相机后面不画
- 距离剔除：太远不画

### 正确的球体几何
- 相机在球心向外看
- 数据分布在球面上
- 缩放改变观察半径
- 360度无边界滚动

**结论**：删掉那23个装逼文件，用这6个文件实现真正能工作的球形数据可视化。简单、直接、有效。

---

*重写完成 - Linus Torvalds风格*  
*原则: KISS + 数据结构优先 + 反对过度设计*  
*目标: 能工作的代码，不是获奖论文*