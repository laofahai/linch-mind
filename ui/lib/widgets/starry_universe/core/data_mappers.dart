/// 数据映射系统 - 将抽象数据转换为星空可视化元素
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:vector_math/vector_math.dart' as vm;
import '../../../models/connector_lifecycle_models.dart';
import '../../../models/api_response.dart';
import 'cosmic_theme.dart';
import 'starry_canvas.dart';

/// 通用索引数据映射器 - Universal Index → 搜索星河
class SearchStarMapper {
  static const double riverWidth = 200.0;
  static const double particleSpacing = 10.0;
  
  /// 将搜索结果映射为星河粒子
  static List<Star> mapSearchResultsToStars(
    List<Map<String, dynamic>> searchResults,
    Size canvasSize,
  ) {
    final stars = <Star>[];
    
    if (searchResults.isEmpty) return stars;
    
    // 计算河流路径 - S形曲线
    final riverPath = _generateRiverPath(canvasSize);
    
    for (int i = 0; i < searchResults.length; i++) {
      final result = searchResults[i];
      final score = (result['score'] as num?)?.toDouble() ?? 0.5;
      final type = result['type'] as String? ?? 'document';
      final id = result['id'] as String? ?? 'result_$i';
      
      // 沿河流分布位置
      final t = i / searchResults.length;
      final position = _getPositionOnRiver(riverPath, t);
      
      // 添加随机偏移创造自然效果
      final random = math.Random(id.hashCode);
      position.x += (random.nextDouble() - 0.5) * 30;
      position.y += (random.nextDouble() - 0.5) * 20;
      
      final star = Star(
        position: position,
        size: _calculateStarSize(score),
        color: CosmicTheme.getScoreBasedColor(
          CosmicTheme.getStarColor(type),
          score,
        ),
        id: id,
        intensity: score,
        metadata: {
          'type': type,
          'score': score,
          'title': result['title'] ?? '',
          'snippet': result['snippet'] ?? '',
        },
      );
      
      stars.add(star);
    }
    
    return stars;
  }
  
  /// 生成河流路径
  static List<vm.Vector2> _generateRiverPath(Size canvasSize) {
    final path = <vm.Vector2>[];
    const segments = 50;
    
    for (int i = 0; i <= segments; i++) {
      final t = i / segments;
      
      // S形曲线路径
      final x = canvasSize.width * t;
      final y = canvasSize.height * 0.5 + 
                math.sin(t * math.pi * 2) * canvasSize.height * 0.2;
      
      path.add(vm.Vector2(x, y));
    }
    
    return path;
  }
  
  /// 获取河流上指定位置的坐标
  static vm.Vector2 _getPositionOnRiver(List<vm.Vector2> riverPath, double t) {
    final index = (t * (riverPath.length - 1)).floor();
    final nextIndex = (index + 1).clamp(0, riverPath.length - 1);
    final localT = (t * (riverPath.length - 1)) - index;
    
    return riverPath[index] + (riverPath[nextIndex] - riverPath[index]) * localT;
  }
  
  /// 计算星体大小
  static double _calculateStarSize(double score) {
    return (score * 4 + 2).clamp(2.0, 8.0);
  }
}

/// 实体数据映射器 - Entity → 智慧星座
class ConstellationMapper {
  /// 将实体数据映射为星座
  static List<Star> mapEntitiesToStars(
    List<Map<String, dynamic>> entities,
    Size canvasSize,
  ) {
    final stars = <Star>[];
    
    // 使用力导向布局算法分布实体
    final positions = _calculateForceDirectedLayout(entities, canvasSize);
    
    for (int i = 0; i < entities.length; i++) {
      final entity = entities[i];
      final entityId = entity['entity_id'] as String? ?? 'entity_$i';
      final entityType = entity['type'] as String? ?? 'concept';
      final importance = _calculateImportance(entity);
      
      final star = Star(
        position: positions[i],
        size: _getStarSizeByImportance(importance),
        color: _getStarColorByType(entityType),
        id: entityId,
        metadata: {
          'type': entityType,
          'name': entity['name'] ?? '',
          'description': entity['description'] ?? '',
          'importance': importance,
          'properties': entity['properties'] ?? {},
        },
      );
      
      stars.add(star);
    }
    
    return stars;
  }
  
  /// 计算实体重要性
  static double _calculateImportance(Map<String, dynamic> entity) {
    final accessCount = (entity['access_count'] as num?)?.toDouble() ?? 0;
    final relationshipCount = (entity['relationship_count'] as num?)?.toDouble() ?? 0;
    
    // 综合访问次数和关系数量计算重要性
    return ((accessCount * 0.6 + relationshipCount * 0.4) / 10).clamp(0.1, 1.0);
  }
  
  /// 根据重要性获取星体大小
  static double _getStarSizeByImportance(double importance) {
    return (importance * 6 + 3).clamp(3.0, 12.0);
  }
  
  /// 根据类型获取星体颜色
  static Color _getStarColorByType(String type) {
    switch (type.toLowerCase()) {
      case 'person':
        return CosmicTheme.starBlue;
      case 'document':
      case 'file':
        return CosmicTheme.starGold;
      case 'concept':
      case 'idea':
        return CosmicTheme.starPurple;
      case 'project':
        return CosmicTheme.starRed;
      default:
        return CosmicTheme.starWhite;
    }
  }
  
  /// 力导向布局计算
  static List<vm.Vector2> _calculateForceDirectedLayout(
    List<Map<String, dynamic>> entities,
    Size canvasSize,
  ) {
    final positions = <vm.Vector2>[];
    final random = math.Random(42); // 固定种子保证一致性
    
    // 初始化随机位置
    for (int i = 0; i < entities.length; i++) {
      positions.add(vm.Vector2(
        random.nextDouble() * canvasSize.width,
        random.nextDouble() * canvasSize.height,
      ));
    }
    
    // 简化的力导向算法
    for (int iteration = 0; iteration < 50; iteration++) {
      final forces = List.generate(entities.length, (_) => vm.Vector2.zero());
      
      // 计算排斥力
      for (int i = 0; i < entities.length; i++) {
        for (int j = i + 1; j < entities.length; j++) {
          final distance = (positions[i] - positions[j]).length;
          if (distance > 0) {
            final repulsion = (positions[i] - positions[j]).normalized() * (100 / distance);
            forces[i] += repulsion;
            forces[j] -= repulsion;
          }
        }
      }
      
      // 应用力
      for (int i = 0; i < entities.length; i++) {
        positions[i] += forces[i] * 0.01;
        
        // 边界约束
        positions[i].x = positions[i].x.clamp(50.0, canvasSize.width - 50);
        positions[i].y = positions[i].y.clamp(50.0, canvasSize.height - 50);
      }
    }
    
    return positions;
  }
  
  /// 生成实体间的连接线
  static List<StarConnection> generateEntityConnections(
    List<Map<String, dynamic>> relationships,
    List<Star> stars,
  ) {
    final connections = <StarConnection>[];
    
    for (final relationship in relationships) {
      final sourceId = relationship['source_entity_id'] as String?;
      final targetId = relationship['target_entity_id'] as String?;
      final strength = (relationship['strength'] as num?)?.toDouble() ?? 0.5;
      
      if (sourceId != null && targetId != null) {
        // 检查星体是否存在
        final sourceExists = stars.any((star) => star.id == sourceId);
        final targetExists = stars.any((star) => star.id == targetId);
        
        if (sourceExists && targetExists) {
          final connection = StarConnection(
            fromStarId: sourceId,
            toStarId: targetId,
            strength: strength,
            color: _getConnectionColor(strength),
            animated: strength > 0.7, // 强连接动画化
          );
          
          connections.add(connection);
        }
      }
    }
    
    return connections;
  }
  
  /// 根据强度获取连接线颜色
  static Color _getConnectionColor(double strength) {
    if (strength > 0.8) {
      return CosmicTheme.connectionStrong;
    } else if (strength > 0.5) {
      return CosmicTheme.connectionMedium;
    } else {
      return CosmicTheme.connectionWeak;
    }
  }
}

/// 图数据映射器 - Graph → 知识宇宙
class UniverseMapper {
  /// 将图数据映射为宇宙布局
  static UniverseLayout mapGraphToUniverse(
    Map<String, dynamic> graphData,
    Size canvasSize,
  ) {
    final nodes = graphData['nodes'] as List<dynamic>? ?? [];
    final edges = graphData['edges'] as List<dynamic>? ?? [];
    
    // 执行聚类分析
    final clusters = _performClustering(nodes, edges);
    
    // 为每个聚类创建星系
    final galaxies = <Galaxy>[];
    for (int i = 0; i < clusters.length; i++) {
      final cluster = clusters[i];
      final galaxy = _createGalaxyFromCluster(cluster, i, canvasSize);
      galaxies.add(galaxy);
    }
    
    return UniverseLayout(
      galaxies: galaxies,
      scale: _determineUniverseScale(nodes.length),
      centerPoint: vm.Vector2(canvasSize.width / 2, canvasSize.height / 2),
    );
  }
  
  /// 执行聚类分析
  static List<List<Map<String, dynamic>>> _performClustering(
    List<dynamic> nodes,
    List<dynamic> edges,
  ) {
    // 简化的聚类算法 - 基于连接度
    final clusters = <List<Map<String, dynamic>>>[];
    final visited = <String>{};
    
    for (final node in nodes) {
      final nodeData = node as Map<String, dynamic>;
      final nodeId = nodeData['id'] as String? ?? '';
      
      if (!visited.contains(nodeId)) {
        final cluster = _findConnectedNodes(nodeId, nodes, edges, visited);
        if (cluster.isNotEmpty) {
          clusters.add(cluster);
        }
      }
    }
    
    return clusters;
  }
  
  /// 查找连接的节点
  static List<Map<String, dynamic>> _findConnectedNodes(
    String startNodeId,
    List<dynamic> nodes,
    List<dynamic> edges,
    Set<String> visited,
  ) {
    final cluster = <Map<String, dynamic>>[];
    final queue = <String>[startNodeId];
    
    while (queue.isNotEmpty) {
      final currentNodeId = queue.removeAt(0);
      if (visited.contains(currentNodeId)) continue;
      
      visited.add(currentNodeId);
      
      // 查找节点数据
      final nodeData = nodes.firstWhere(
        (node) => (node as Map<String, dynamic>)['id'] == currentNodeId,
        orElse: () => null,
      ) as Map<String, dynamic>?;
      
      if (nodeData != null) {
        cluster.add(nodeData);
        
        // 查找连接的节点
        for (final edge in edges) {
          final edgeData = edge as Map<String, dynamic>;
          final sourceId = edgeData['source'] as String?;
          final targetId = edgeData['target'] as String?;
          
          if (sourceId == currentNodeId && targetId != null && !visited.contains(targetId)) {
            queue.add(targetId);
          } else if (targetId == currentNodeId && sourceId != null && !visited.contains(sourceId)) {
            queue.add(sourceId);
          }
        }
      }
    }
    
    return cluster;
  }
  
  /// 从聚类创建星系
  static Galaxy _createGalaxyFromCluster(
    List<Map<String, dynamic>> cluster,
    int clusterIndex,
    Size canvasSize,
  ) {
    // 为星系分配位置
    final angle = (clusterIndex / 5) * 2 * math.pi; // 假设最多5个星系
    final radius = math.min(canvasSize.width, canvasSize.height) * 0.3;
    final center = vm.Vector2(
      canvasSize.width / 2 + math.cos(angle) * radius,
      canvasSize.height / 2 + math.sin(angle) * radius,
    );
    
    // 为星系中的节点创建恒星
    final stars = <Star>[];
    for (int i = 0; i < cluster.length; i++) {
      final node = cluster[i];
      final nodeId = node['id'] as String? ?? 'node_${clusterIndex}_$i';
      
      // 螺旋分布
      final spiralAngle = (i / cluster.length) * 4 * math.pi;
      final spiralRadius = (i / cluster.length) * 100;
      final position = center + vm.Vector2(
        math.cos(spiralAngle) * spiralRadius,
        math.sin(spiralAngle) * spiralRadius,
      );
      
      final star = Star(
        position: position,
        size: _getNodeSize(node),
        color: _getNodeColor(node),
        id: nodeId,
        metadata: node,
      );
      
      stars.add(star);
    }
    
    return Galaxy(
      id: 'galaxy_$clusterIndex',
      center: center,
      stars: stars,
      radius: 150.0,
      rotationSpeed: 0.1,
    );
  }
  
  /// 获取节点大小
  static double _getNodeSize(Map<String, dynamic> node) {
    final weight = (node['weight'] as num?)?.toDouble() ?? 1.0;
    return (weight * 3 + 2).clamp(2.0, 8.0);
  }
  
  /// 获取节点颜色
  static Color _getNodeColor(Map<String, dynamic> node) {
    final type = node['type'] as String? ?? 'default';
    return CosmicTheme.getStarColor(type);
  }
  
  /// 确定宇宙尺度
  static double _determineUniverseScale(int nodeCount) {
    if (nodeCount < 50) return 1.0;
    if (nodeCount < 200) return 1.5;
    if (nodeCount < 500) return 2.0;
    return 3.0;
  }
}

/// 向量数据映射器 - Vector → 相似星云
class NebulaMapper {
  /// 将向量数据映射为星云
  static List<NebulaCluster> mapVectorsToNebulae(
    List<Map<String, dynamic>> vectorDocuments,
    Size canvasSize,
  ) {
    // 执行向量聚类
    final clusters = _performVectorClustering(vectorDocuments);
    
    final nebulaClusters = <NebulaCluster>[];
    for (int i = 0; i < clusters.length; i++) {
      final cluster = clusters[i];
      final nebulaCluster = _createNebulaFromCluster(cluster, i, canvasSize);
      nebulaClusters.add(nebulaCluster);
    }
    
    return nebulaClusters;
  }
  
  /// 执行向量聚类
  static List<List<Map<String, dynamic>>> _performVectorClustering(
    List<Map<String, dynamic>> documents,
  ) {
    // 简化的聚类算法 - 基于文档类型和相似度
    final clusters = <String, List<Map<String, dynamic>>>{};
    
    for (final doc in documents) {
      final type = doc['type'] as String? ?? 'default';
      clusters.putIfAbsent(type, () => []);
      clusters[type]!.add(doc);
    }
    
    return clusters.values.toList();
  }
  
  /// 从聚类创建星云
  static NebulaCluster _createNebulaFromCluster(
    List<Map<String, dynamic>> cluster,
    int clusterIndex,
    Size canvasSize,
  ) {
    // 分配星云位置
    final random = math.Random(clusterIndex);
    final center = vm.Vector2(
      random.nextDouble() * canvasSize.width * 0.8 + canvasSize.width * 0.1,
      random.nextDouble() * canvasSize.height * 0.8 + canvasSize.height * 0.1,
    );
    
    // 确定星云类型和颜色
    final nebulaType = _determineNebulaType(cluster);
    final color = _getNebulaColor(nebulaType);
    
    return NebulaCluster(
      id: 'nebula_$clusterIndex',
      center: center,
      color: color,
      type: nebulaType,
      documents: cluster,
      density: _calculateClusterDensity(cluster),
      radius: _calculateClusterRadius(cluster),
    );
  }
  
  /// 确定星云类型
  static String _determineNebulaType(List<Map<String, dynamic>> cluster) {
    final typeCount = <String, int>{};
    for (final doc in cluster) {
      final type = doc['type'] as String? ?? 'default';
      typeCount[type] = (typeCount[type] ?? 0) + 1;
    }
    
    // 返回最常见的类型
    return typeCount.entries
        .reduce((a, b) => a.value > b.value ? a : b)
        .key;
  }
  
  /// 获取星云颜色
  static Color _getNebulaColor(String type) {
    switch (type.toLowerCase()) {
      case 'document':
        return CosmicTheme.nebulaBlue;
      case 'image':
        return CosmicTheme.nebulaRed;
      case 'code':
        return CosmicTheme.nebulaPurple;
      default:
        return CosmicTheme.nebulaDark;
    }
  }
  
  /// 计算聚类密度
  static double _calculateClusterDensity(List<Map<String, dynamic>> cluster) {
    return (cluster.length / 10.0).clamp(0.1, 1.0);
  }
  
  /// 计算聚类半径
  static double _calculateClusterRadius(List<Map<String, dynamic>> cluster) {
    return (cluster.length * 5.0 + 30.0).clamp(30.0, 150.0);
  }
}

/// 数据结构定义

/// 宇宙布局
class UniverseLayout {
  final List<Galaxy> galaxies;
  final double scale;
  final vm.Vector2 centerPoint;
  
  const UniverseLayout({
    required this.galaxies,
    required this.scale,
    required this.centerPoint,
  });
}

/// 星系
class Galaxy {
  final String id;
  final vm.Vector2 center;
  final List<Star> stars;
  final double radius;
  final double rotationSpeed;
  
  const Galaxy({
    required this.id,
    required this.center,
    required this.stars,
    required this.radius,
    required this.rotationSpeed,
  });
}

/// 星云聚类
class NebulaCluster {
  final String id;
  final vm.Vector2 center;
  final Color color;
  final String type;
  final List<Map<String, dynamic>> documents;
  final double density;
  final double radius;
  
  const NebulaCluster({
    required this.id,
    required this.center,
    required this.color,
    required this.type,
    required this.documents,
    required this.density,
    required this.radius,
  });
}