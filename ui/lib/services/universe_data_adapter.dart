/// 统一星空宇宙数据适配器 - 将真实IPC数据转换为星空可视化
import 'dart:math' as math;
import 'package:vector_math/vector_math.dart' as vm;
import 'package:flutter/material.dart';
import '../models/unified_data_models.dart';
import '../models/connector_lifecycle_models.dart';
import '../widgets/starry_universe/core/starry_canvas.dart';
import '../widgets/starry_universe/core/data_mappers.dart';
import '../services/starry_universe_api_client.dart';
import '../utils/app_logger.dart';

/// 统一星空数据适配器 - 集成所有数据类型的可视化转换
class UnifiedStarryDataAdapter {
  // 球形宇宙坐标系统常量
  static final double _goldenAngle = math.pi * (3.0 - math.sqrt(5.0));
  static const double _baseRadius = 500.0;

  // 球面分层半径 (按照球形宇宙设计)
  static const double _searchLayerRadius = _baseRadius * 1.0; // 搜索结果在最外层
  static const double _entityLayerRadius = _baseRadius * 0.8; // 实体在中层
  static const double _graphLayerRadius = _baseRadius * 0.6; // 图谱在深层
  static const double _vectorLayerRadius = _baseRadius * 0.4; // 向量在内层

  // 星空主题颜色
  static const Color starGold = Color(0xFFFFD700);
  static const Color starBlue = Color(0xFF87CEEB);
  static const Color starPurple = Color(0xFF9370DB);
  static const Color nebulaRed = Color(0xFFFF073A);
  static const Color nebulaBlue = Color(0xFF40E0D0);

  // API客户端
  static final StarryUniverseApiClient _apiClient =
      StarryUniverseApiClient.instance;

  // ================================
  // 统一数据获取接口
  // ================================

  /// 获取搜索星河数据
  static Future<List<CelestialObject>> getSearchStarRiver(
      String query, Size canvasSize) async {
    try {
      final response = await _apiClient.searchUniversalIndex(
        query: query,
        limit: 100,
        includeMetadata: true,
      );

      AppLogger.info('获取搜索星河数据', module: 'UnifiedAdapter', data: {
        'query': query,
        'results': response.results.length,
      });

      return _convertSearchResultsToStars(response.results, canvasSize);
    } catch (e) {
      AppLogger.error('获取搜索数据失败', module: 'UnifiedAdapter', exception: e);
      return [];
    }
  }

  /// 获取智慧星座数据
  static Future<StarConstellationData> getWisdomConstellation(
      Size canvasSize) async {
    try {
      final response = await _apiClient.getEntities(
        limit: 50,
        includeRelationships: true,
      );

      AppLogger.info('获取智慧星座数据', module: 'UnifiedAdapter', data: {
        'entities': response.entities.length,
        'relationships': response.relationships.length,
      });

      final stars = _convertEntitiesToStars(response.entities, canvasSize);
      final connections =
          _convertRelationshipsToConnections(response.relationships, stars);

      return StarConstellationData(
        stars: stars,
        connections: connections,
        metadata: response.stats,
      );
    } catch (e) {
      AppLogger.error('获取实体数据失败', module: 'UnifiedAdapter', exception: e);
      return StarConstellationData(stars: [], connections: [], metadata: {});
    }
  }

  /// 获取知识宇宙数据
  static Future<UniverseGalaxyData> getKnowledgeUniverse(
      Size canvasSize) async {
    try {
      final response = await _apiClient.getGraphData(
        maxNodes: 200,
        maxEdges: 500,
        includeCentrality: true,
      );

      AppLogger.info('获取知识宇宙数据', module: 'UnifiedAdapter', data: {
        'nodes': response.nodes.length,
        'edges': response.edges.length,
      });

      return _convertGraphToUniverse(response, canvasSize);
    } catch (e) {
      AppLogger.error('获取图谱数据失败', module: 'UnifiedAdapter', exception: e);
      return UniverseGalaxyData(galaxies: [], metrics: {});
    }
  }

  /// 获取相似星云数据
  static Future<NebulaClusterData> getSimilarityNebula(Size canvasSize) async {
    try {
      final response = await _apiClient.getVectorData(
        limit: 100,
        clusterCount: 8,
        similarityThreshold: 0.7,
      );

      AppLogger.info('获取相似星云数据', module: 'UnifiedAdapter', data: {
        'documents': response.documents.length,
        'clusters': response.clusters.length,
      });

      return _convertVectorsToNebulae(response, canvasSize);
    } catch (e) {
      AppLogger.error('获取向量数据失败', module: 'UnifiedAdapter', exception: e);
      return NebulaClusterData(clusters: [], documents: []);
    }
  }

  /// 获取连接器星球数据（保留兼容性）
  static List<CelestialObject> convertConnectorsToStars(
      List<ConnectorInfo> connectors) {
    AppLogger.info('转换连接器为星球',
        module: 'UnifiedAdapter', data: {'count': connectors.length});

    final celestialObjects = <CelestialObject>[];
    final sortedConnectors = List<ConnectorInfo>.from(connectors)
      ..sort((a, b) => _calculateConnectorImportance(b)
          .compareTo(_calculateConnectorImportance(a)));

    for (int i = 0; i < sortedConnectors.length; i++) {
      final connector = sortedConnectors[i];
      final position =
          _assignSphericalPosition(connector, i, sortedConnectors.length);

      celestialObjects.add(Star(
        position: vm.Vector2(position.x, position.y),
        size: _calculateConnectorStarSize(connector),
        color: _getConnectorColor(connector),
        id: connector.connectorId,
        metadata: {
          'connector_data': connector,
          'display_name': connector.displayName,
          'state': connector.state.name,
          'importance': _calculateConnectorImportance(connector),
        },
      ));
    }

    return celestialObjects;
  }

  // ================================
  // 数据转换核心方法
  // ================================

  /// 搜索结果转换为星河
  static List<CelestialObject> _convertSearchResultsToStars(
      List<UniversalIndexEntry> results, Size canvasSize) {
    final stars = <CelestialObject>[];

    for (int i = 0; i < results.length; i++) {
      final result = results[i];
      final position =
          _calculateSearchStarPosition(result, i, results.length, canvasSize);

      stars.add(Star(
        position: position,
        size: _calculateSearchStarSize(result),
        color: _getContentTypeColor(result.contentType),
        id: result.id,
        metadata: {
          'search_result': result,
          'display_name': result.displayName,
          'content_type': result.contentType.name,
          'score': result.score,
          'tier': result.indexTier.name,
          'layer': 'search_outer',
        },
      ));
    }

    return stars;
  }

  /// 实体转换为星座恒星
  static List<CelestialObject> _convertEntitiesToStars(
      List<UnifiedEntityMetadata> entities, Size canvasSize) {
    final stars = <CelestialObject>[];

    for (int i = 0; i < entities.length; i++) {
      final entity = entities[i];
      final position =
          _calculateEntityStarPosition(entity, i, entities.length, canvasSize);

      stars.add(Star(
        position: position,
        size: _calculateEntityStarSize(entity),
        color: _getEntityTypeColor(entity.entityType ?? 'unknown'),
        id: entity.entityId,
        metadata: {
          'entity': entity,
          'display_name': entity.displayName,
          'entity_type': entity.entityType,
          'importance': entity.importance,
          'access_count': entity.accessCount,
          'layer': 'entity_middle',
        },
      ));
    }

    return stars;
  }

  /// 关系转换为星座连线
  static List<StarConnection> _convertRelationshipsToConnections(
      List<UnifiedEntityRelationship> relationships,
      List<CelestialObject> stars) {
    final connections = <StarConnection>[];
    final starMap = {for (var star in stars) star.id: star};

    for (final rel in relationships) {
      final fromStar = starMap[rel.sourceEntityId];
      final toStar = starMap[rel.targetEntityId];

      if (fromStar != null && toStar != null) {
        connections.add(StarConnection(
          fromStarId: rel.sourceEntityId,
          toStarId: rel.targetEntityId,
          strength: rel.strength.toDouble(),
          color: _getRelationshipColor(
              rel.relationshipType, rel.strength.toDouble()),
        ));
      }
    }

    return connections;
  }

  /// 图数据转换为宇宙星系
  static UniverseGalaxyData _convertGraphToUniverse(
      GraphDataResponse response, Size canvasSize) {
    final galaxies = <Galaxy>[];

    // 根据聚类创建星系
    for (final clusterEntry in response.clusters.entries) {
      final clusterId = clusterEntry.key;
      final nodeIds = clusterEntry.value;

      final clusterNodes =
          response.nodes.where((n) => nodeIds.contains(n.id)).toList();
      final clusterStars = clusterNodes
          .map((node) => _convertGraphNodeToStar(node, canvasSize))
          .toList();

      galaxies.add(Galaxy(
        id: clusterId,
        stars: clusterStars,
        center: _calculateClusterCenter(clusterStars),
        radius: _calculateClusterRadius(clusterStars),
      ));
    }

    return UniverseGalaxyData(
      galaxies: galaxies,
      metrics: response.graphMetrics,
    );
  }

  /// 向量数据转换为星云聚类
  static NebulaClusterData _convertVectorsToNebulae(
      VectorDataResponse response, Size canvasSize) {
    final clusters = <NebulaCluster>[];

    for (final cluster in response.clusters) {
      final clusterDocs = response.documents
          .where((doc) => cluster.documentIds.contains(doc.documentId))
          .toList();

      clusters.add(NebulaCluster(
        id: cluster.clusterId,
        center: _calculateVectorClusterCenter(cluster, canvasSize),
        radius: 50.0, // 默认半径
        color: _getSemanticColor(cluster.topic ?? 'unknown'),
        documents: clusterDocs.map((doc) => doc.toJson()).toList(),
        type: cluster.topic ?? 'unknown',
        density: cluster.cohesion,
      ));
    }

    return NebulaClusterData(
      clusters: clusters,
      documents: response.documents,
    );
  }

  // ================================
  // 位置计算方法
  // ================================

  /// 计算搜索星河中星体位置（球面上层）
  static vm.Vector2 _calculateSearchStarPosition(
      UniversalIndexEntry result, int index, int totalCount, Size canvasSize) {
    // 使用黄金角度算法在球面上层均匀分布
    final phi = _goldenAngle * index;
    final theta = math.acos(1.0 - 2.0 * (index + 0.5) / totalCount);

    // 球面坐标转换为2D投影
    final x = _searchLayerRadius * math.sin(theta) * math.cos(phi);
    final y = _searchLayerRadius * math.sin(theta) * math.sin(phi);

    // 转换到画布坐标系，居中显示
    return vm.Vector2(
      canvasSize.width * 0.5 + x,
      canvasSize.height * 0.5 + y,
    );
  }

  /// 计算实体星座中恒星位置（球面中层）
  static vm.Vector2 _calculateEntityStarPosition(UnifiedEntityMetadata entity,
      int index, int totalCount, Size canvasSize) {
    // 在球面中层使用黄金角度算法分布，考虑重要性
    final importance = entity.importance;
    final layerRadius =
        _entityLayerRadius * (0.8 + 0.2 * importance); // 重要实体稍微向外

    final phi = _goldenAngle * index;
    final theta = math.acos(1.0 - 2.0 * (index + 0.5) / totalCount);

    // 球面坐标转换为2D投影
    final x = layerRadius * math.sin(theta) * math.cos(phi);
    final y = layerRadius * math.sin(theta) * math.sin(phi);

    // 转换到画布坐标系，居中显示
    return vm.Vector2(
      canvasSize.width * 0.5 + x,
      canvasSize.height * 0.5 + y,
    );
  }

  /// 计算图节点转星体位置（球面深层）
  static CelestialObject _convertGraphNodeToStar(
      GraphNode node, Size canvasSize) {
    final centrality = node.centralityScore;
    final layerRadius =
        _graphLayerRadius * (0.8 + 0.2 * centrality); // 中心度高的节点稍微向外

    // 使用节点ID的哈希值确保位置的确定性
    final random = math.Random(node.id.hashCode);
    final phi = random.nextDouble() * 2 * math.pi;
    final theta = math.acos(1.0 - 2.0 * random.nextDouble());

    // 球面坐标转换为2D投影
    final x = layerRadius * math.sin(theta) * math.cos(phi);
    final y = layerRadius * math.sin(theta) * math.sin(phi);

    final position = vm.Vector2(
      canvasSize.width * 0.5 + x,
      canvasSize.height * 0.5 + y,
    );

    return Star(
      position: position,
      size: 6.0 + 8.0 * centrality,
      color: _getNodeTypeColor(node.nodeType ?? 'unknown'),
      id: node.id,
      metadata: {
        'graph_node': node,
        'centrality': centrality,
        'node_type': node.nodeType,
        'layer': 'graph_deep',
      },
    );
  }

  /// 计算向量聚类中心位置（球面内层）
  static vm.Vector2 _calculateVectorClusterCenter(
      VectorCluster cluster, Size canvasSize) {
    // 在球面内层分布星云聚类
    final random = math.Random(cluster.clusterId.hashCode);
    final phi = random.nextDouble() * 2 * math.pi;
    final theta = math.acos(1.0 - 2.0 * random.nextDouble());

    // 球面坐标转换为2D投影
    final x = _vectorLayerRadius * math.sin(theta) * math.cos(phi);
    final y = _vectorLayerRadius * math.sin(theta) * math.sin(phi);

    return vm.Vector2(
      canvasSize.width * 0.5 + x,
      canvasSize.height * 0.5 + y,
    );
  }

  // ================================
  // 大小和颜色计算方法
  // ================================

  /// 计算搜索星体大小
  static double _calculateSearchStarSize(UniversalIndexEntry result) {
    final baseSize = 4.0;
    final maxSize = 12.0;
    return baseSize + (maxSize - baseSize) * result.score;
  }

  /// 计算实体星体大小
  static double _calculateEntityStarSize(UnifiedEntityMetadata entity) {
    final baseSize = 6.0;
    final maxSize = 16.0;
    final importanceSize = baseSize + (maxSize - baseSize) * entity.importance;
    final accessModifier =
        math.log(entity.accessCount + 1) / math.log(100) * 2.0;
    return (importanceSize + accessModifier).clamp(4.0, 18.0);
  }

  /// 获取内容类型颜色
  static Color _getContentTypeColor(UniversalContentType type) {
    switch (type) {
      case UniversalContentType.document:
        return starGold;
      case UniversalContentType.image:
        return starBlue;
      case UniversalContentType.code:
        return starPurple;
      case UniversalContentType.contact:
        return Colors.green.shade400;
      case UniversalContentType.url:
        return Colors.cyan.shade400;
      default:
        return Colors.white;
    }
  }

  /// 获取实体类型颜色
  static Color _getEntityTypeColor(String entityType) {
    switch (entityType.toLowerCase()) {
      case 'person':
        return starBlue;
      case 'concept':
        return starPurple;
      case 'document':
        return starGold;
      case 'project':
        return Colors.orange.shade400;
      default:
        return Colors.white;
    }
  }

  /// 获取节点类型颜色
  static Color _getNodeTypeColor(String nodeType) {
    switch (nodeType.toLowerCase()) {
      case 'concept':
        return starPurple;
      case 'document':
        return starGold;
      case 'person':
        return starBlue;
      case 'organization':
        return Colors.red.shade400;
      default:
        return Colors.white;
    }
  }

  /// 获取关系类型颜色
  static Color _getRelationshipColor(String relType, double strength) {
    final alpha = (0.3 + 0.7 * strength).clamp(0.0, 1.0);

    switch (relType.toLowerCase()) {
      case 'related_to':
        return Colors.blue.withValues(alpha: alpha);
      case 'contains':
        return Colors.green.withValues(alpha: alpha);
      case 'references':
        return Colors.orange.withValues(alpha: alpha);
      default:
        return Colors.white.withValues(alpha: alpha);
    }
  }

  /// 获取语义主题颜色
  static Color _getSemanticColor(String topic) {
    switch (topic.toLowerCase()) {
      case 'technology':
        return nebulaBlue;
      case 'business':
        return Colors.green.shade400;
      case 'research':
        return starPurple;
      case 'personal':
        return Colors.yellow.shade400;
      default:
        return nebulaRed;
    }
  }

  // ================================
  // 几何计算辅助方法
  // ================================

  /// 计算聚类中心
  static vm.Vector2 _calculateClusterCenter(List<CelestialObject> stars) {
    if (stars.isEmpty) return vm.Vector2.zero();

    double x = 0, y = 0;
    for (final star in stars) {
      x += star.position.x;
      y += star.position.y;
    }

    return vm.Vector2(x / stars.length, y / stars.length);
  }

  /// 计算聚类半径
  static double _calculateClusterRadius(List<CelestialObject> stars) {
    if (stars.isEmpty) return 0.0;

    final center = _calculateClusterCenter(stars);
    double maxDistance = 0.0;

    for (final star in stars) {
      final distance = (star.position - center).length;
      if (distance > maxDistance) maxDistance = distance;
    }

    return maxDistance + 50.0; // 添加边距
  }

  /// 生成球面内层向量星体位置
  static vm.Vector2 _generateVectorStarPosition(int index, int totalDocs,
      vm.Vector2 clusterCenter, double clusterRadius, Size canvasSize) {
    // 在星云聚类内部使用黄金角度分布
    final phi = _goldenAngle * index;
    final localRadius = clusterRadius * math.sqrt(index / totalDocs); // 从中心向外分布

    final offsetX = localRadius * math.cos(phi);
    final offsetY = localRadius * math.sin(phi);

    return vm.Vector2(
      clusterCenter.x + offsetX,
      clusterCenter.y + offsetY,
    );
  }

  /// 连接器相关方法（兼容性保留）
  static vm.Vector3 _assignSphericalPosition(
      ConnectorInfo connector, int index, int totalCount) {
    final importance = _calculateConnectorImportance(connector);
    final radius = _baseRadius * (0.8 + 0.2 * importance);

    final phi = _goldenAngle * index;
    final theta = math.acos(1.0 - 2.0 * (index + 0.5) / totalCount);

    return vm.Vector3(
      radius * math.sin(theta) * math.cos(phi),
      radius * math.sin(theta) * math.sin(phi),
      radius * math.cos(theta),
    );
  }

  /// 计算连接器重要性
  static double _calculateConnectorImportance(ConnectorInfo connector) {
    double score = 0.0;

    switch (connector.state) {
      case ConnectorState.running:
        score += 0.4;
      case ConnectorState.starting:
        score += 0.3;
      case ConnectorState.error:
        score += 0.25;
      default:
        score += 0.1;
    }

    if (connector.dataCount > 0) {
      score += 0.3 *
          (math.log(connector.dataCount + 1) / math.log(10000)).clamp(0.0, 1.0);
    }

    if (connector.enabled) score += 0.1;

    return score.clamp(0.0, 1.0);
  }

  /// 计算连接器星体大小
  static double _calculateConnectorStarSize(ConnectorInfo connector) {
    final importance = _calculateConnectorImportance(connector);
    return (4.0 + 8.0 * importance).clamp(3.0, 15.0);
  }

  /// 获取连接器颜色
  static Color _getConnectorColor(ConnectorInfo connector) {
    switch (connector.state) {
      case ConnectorState.running:
        return Colors.green.shade400;
      case ConnectorState.starting:
        return Colors.orange.shade400;
      case ConnectorState.error:
        return Colors.red.shade400;
      case ConnectorState.stopped:
        return Colors.grey.shade500;
      default:
        return Colors.purple.shade400;
    }
  }

  /// 连接器关系转换（兼容性保留）
  static List<StarConnection> convertRelationshipsToConnections(
    List<ConnectorInfo> connectors,
    Map<String, dynamic> relationshipData,
  ) {
    final connections = <StarConnection>[];

    for (int i = 0; i < connectors.length; i++) {
      for (int j = i + 1; j < connectors.length; j++) {
        final connector1 = connectors[i];
        final connector2 = connectors[j];

        final strength =
            _calculateConnectorConnectionStrength(connector1, connector2);

        if (strength > 0.3) {
          connections.add(StarConnection(
            fromStarId: connector1.connectorId,
            toStarId: connector2.connectorId,
            strength: strength,
            color:
                _getConnectorConnectionColor(connector1, connector2, strength),
          ));
        }
      }
    }

    return connections;
  }

  /// 计算连接器连接强度
  static double _calculateConnectorConnectionStrength(
      ConnectorInfo connector1, ConnectorInfo connector2) {
    double strength = 0.0;

    if (connector1.state == connector2.state) strength += 0.3;

    final dataRatio = connector1.dataCount > 0 && connector2.dataCount > 0
        ? math.min(connector1.dataCount, connector2.dataCount) /
            math.max(connector1.dataCount, connector2.dataCount)
        : 0.0;
    strength += 0.25 * dataRatio;

    if (connector1.enabled == connector2.enabled) strength += 0.15;

    return strength.clamp(0.0, 1.0);
  }

  /// 获取连接器连接颜色
  static Color _getConnectorConnectionColor(
      ConnectorInfo connector1, ConnectorInfo connector2, double strength) {
    final alpha = (0.3 + 0.7 * strength).clamp(0.0, 1.0);

    if (connector1.state == ConnectorState.running &&
        connector2.state == ConnectorState.running) {
      return Colors.green.withValues(alpha: alpha);
    } else if (connector1.state == ConnectorState.error ||
        connector2.state == ConnectorState.error) {
      return Colors.red.withValues(alpha: alpha);
    } else {
      return Colors.blue.withValues(alpha: alpha);
    }
  }

  /// 获取连接器详细信息（兼容性保留）
  static Map<String, dynamic> getConnectorDisplayInfo(ConnectorInfo connector) {
    final importance = _calculateConnectorImportance(connector);

    return {
      'id': connector.connectorId,
      'display_name': connector.displayName,
      'state': connector.state.name,
      'enabled': connector.enabled,
      'data_count': connector.dataCount,
      'importance': importance,
    };
  }
}

// ================================
// 统一星空数据结构
// ================================

/// 星座数据结构
class StarConstellationData {
  final List<CelestialObject> stars;
  final List<StarConnection> connections;
  final Map<String, dynamic> metadata;

  StarConstellationData({
    required this.stars,
    required this.connections,
    required this.metadata,
  });
}

/// 宇宙星系数据结构
class UniverseGalaxyData {
  final List<Galaxy> galaxies;
  final Map<String, dynamic> metrics;

  UniverseGalaxyData({
    required this.galaxies,
    required this.metrics,
  });
}

/// 星云聚类数据结构
class NebulaClusterData {
  final List<NebulaCluster> clusters;
  final List<UnifiedVectorDocument> documents;

  NebulaClusterData({
    required this.clusters,
    required this.documents,
  });
}

/// 星系数据结构
class Galaxy {
  final String id;
  final List<CelestialObject> stars;
  final vm.Vector2 center;
  final double radius;

  Galaxy({
    required this.id,
    required this.stars,
    required this.center,
    required this.radius,
  });
}
