/// 球面数据映射器 - 将4种数据类型映射到球面坐标
import 'dart:math' as math;
import 'spherical_config.dart';

/// 球面数据映射器
class SphericalDataMapper {
  final math.Random _random = math.Random(42); // 固定种子确保一致性

  /// 映射所有数据类型到球面
  List<SphericalPoint> mapAllData({
    List<dynamic>? searchData,
    List<dynamic>? entityData,
    dynamic graphData,
    List<dynamic>? vectorData,
  }) {
    final points = <SphericalPoint>[];

    // Universal Index → 搜索数据分布在内层
    if (searchData != null && searchData.isNotEmpty) {
      points.addAll(_mapSearchData(searchData));
    }

    // Entity → 实体数据分布在中层
    if (entityData != null && entityData.isNotEmpty) {
      points.addAll(_mapEntityData(entityData));
    }

    // Graph → 图数据分布在外层
    if (graphData != null) {
      points.addAll(_mapGraphData(graphData));
    }

    // Vector → 向量数据动态聚类
    if (vectorData != null && vectorData.isNotEmpty) {
      points.addAll(_mapVectorData(vectorData));
    }

    return points;
  }

  /// 映射搜索数据到球面
  List<SphericalPoint> _mapSearchData(List<dynamic> data) {
    final points = <SphericalPoint>[];

    for (int i = 0; i < data.length; i++) {
      final item = data[i];

      // 时间轴分布：按索引顺序分布在赤道面
      final theta = (i / data.length) * 2 * math.pi;
      final phi = math.pi / 2; // 赤道面

      // 添加一些随机偏移避免重叠
      final offsetRadius =
          SphericalConfig.searchLayerRadius + (_random.nextDouble() - 0.5) * 50;
      final offsetTheta = theta + (_random.nextDouble() - 0.5) * 0.1;
      final offsetPhi = phi + (_random.nextDouble() - 0.5) * 0.2;

      final pointData = _extractDataInfo(item, 'search');

      points.add(SphericalPoint.search(
        id: pointData['id'],
        data: pointData['data'],
        theta: offsetTheta,
        phi: offsetPhi,
      ));
    }

    return points;
  }

  /// 映射实体数据到球面
  List<SphericalPoint> _mapEntityData(List<dynamic> data) {
    final points = <SphericalPoint>[];

    for (final item in data) {
      // 均匀球面分布
      final theta = _random.nextDouble() * 2 * math.pi;
      final phi = math.acos(1 - 2 * _random.nextDouble());

      final pointData = _extractDataInfo(item, 'entity');

      points.add(SphericalPoint.entity(
        id: pointData['id'],
        data: pointData['data'],
        theta: theta,
        phi: phi,
      ));
    }

    return points;
  }

  /// 映射图数据到球面
  List<SphericalPoint> _mapGraphData(dynamic graphData) {
    final points = <SphericalPoint>[];

    // 处理图数据结构
    List<dynamic> nodes = [];

    if (graphData is Map) {
      nodes = graphData['nodes'] ?? [];
    } else if (graphData is List) {
      nodes = graphData;
    }

    for (final node in nodes) {
      // 图节点使用稍微聚类的分布
      final clusterCenter = _random.nextDouble() * 2 * math.pi;
      final theta = clusterCenter + (_random.nextDouble() - 0.5) * 0.5;
      final phi = math.pi / 3 + (_random.nextDouble() - 0.5) * math.pi / 3;

      final pointData = _extractDataInfo(node, 'graph');

      points.add(SphericalPoint.graph(
        id: pointData['id'],
        data: pointData['data'],
        theta: theta,
        phi: phi,
      ));
    }

    return points;
  }

  /// 映射向量数据到球面（使用简化聚类）
  List<SphericalPoint> _mapVectorData(List<dynamic> data) {
    final points = <SphericalPoint>[];

    // 简化的聚类：将数据分为5个聚类
    const clusterCount = 5;
    final clusters = <int, List<dynamic>>{};

    // 分配到聚类
    for (int i = 0; i < data.length; i++) {
      final clusterIndex = i % clusterCount;
      clusters[clusterIndex] ??= [];
      clusters[clusterIndex]!.add(data[i]);
    }

    // 为每个聚类分配球面区域
    for (int clusterIndex = 0; clusterIndex < clusterCount; clusterIndex++) {
      final clusterData = clusters[clusterIndex];
      if (clusterData == null || clusterData.isEmpty) continue;

      // 聚类中心
      final clusterTheta = (clusterIndex / clusterCount) * 2 * math.pi;
      final clusterPhi =
          math.pi / 4 + (_random.nextDouble() - 0.5) * math.pi / 2;

      // 在聚类中心周围分布点
      for (final item in clusterData) {
        final theta = clusterTheta + (_random.nextDouble() - 0.5) * 0.3;
        final phi = clusterPhi + (_random.nextDouble() - 0.5) * 0.3;
        final radius = SphericalConfig.vectorLayerMinRadius +
            _random.nextDouble() *
                (SphericalConfig.vectorLayerMaxRadius -
                    SphericalConfig.vectorLayerMinRadius);

        final pointData = _extractDataInfo(item, 'vector');

        points.add(SphericalPoint.vector(
          id: pointData['id'],
          data: pointData['data'],
          theta: theta,
          phi: phi,
          radius: radius,
        ));
      }
    }

    return points;
  }

  /// 提取数据信息的通用方法
  Map<String, dynamic> _extractDataInfo(dynamic item, String type) {
    String id;
    Map<String, dynamic> data;

    if (item is Map<String, dynamic>) {
      id = item['id']?.toString() ??
          item['entityId']?.toString() ??
          item['documentId']?.toString() ??
          _generateId(type);

      data = Map<String, dynamic>.from(item);
    } else if (item is String) {
      id = item;
      data = {'content': item, 'type': type};
    } else {
      id = _generateId(type);
      data = {'content': item.toString(), 'type': type};
    }

    return {
      'id': id,
      'data': data,
    };
  }

  /// 生成唯一ID
  String _generateId(String type) {
    return '${type}_${DateTime.now().millisecondsSinceEpoch}_${_random.nextInt(10000)}';
  }

  /// 计算两个球面点之间的角度距离
  double calculateAngularDistance(SphericalPoint a, SphericalPoint b) {
    final deltaTheta = (a.theta - b.theta).abs();
    final deltaPhi = (a.phi - b.phi).abs();

    // 简化的角度距离计算
    return math.sqrt(deltaTheta * deltaTheta + deltaPhi * deltaPhi);
  }

  /// 查找指定点的邻近点
  List<SphericalPoint> findNearbyPoints(
    SphericalPoint center,
    List<SphericalPoint> allPoints,
    double maxDistance,
  ) {
    final nearbyPoints = <SphericalPoint>[];

    for (final point in allPoints) {
      if (point.id != center.id) {
        final distance = calculateAngularDistance(center, point);
        if (distance <= maxDistance) {
          nearbyPoints.add(point);
        }
      }
    }

    return nearbyPoints;
  }

  /// 获取数据类型统计
  Map<String, int> getDataTypeStats(List<SphericalPoint> points) {
    final stats = <String, int>{};

    for (final point in points) {
      stats[point.type] = (stats[point.type] ?? 0) + 1;
    }

    return stats;
  }

  /// 按数据类型筛选点
  List<SphericalPoint> filterByType(List<SphericalPoint> points, String type) {
    return points.where((point) => point.type == type).toList();
  }

  /// 在指定区域内分布点
  List<SphericalPoint> distributeInRegion({
    required List<SphericalPoint> points,
    required double centerTheta,
    required double centerPhi,
    required double regionSize,
  }) {
    final redistributed = <SphericalPoint>[];

    for (int i = 0; i < points.length; i++) {
      final point = points[i];
      final angle = (i / points.length) * 2 * math.pi;
      final distance = _random.nextDouble() * regionSize;

      final newTheta = centerTheta + distance * math.cos(angle);
      final newPhi = centerPhi + distance * math.sin(angle);

      redistributed.add(SphericalPoint(
        radius: point.radius,
        theta: newTheta,
        phi: newPhi.clamp(0, math.pi), // 确保phi在有效范围内
        id: point.id,
        type: point.type,
        data: point.data,
        color: point.color,
        size: point.size,
      ));
    }

    return redistributed;
  }
}
