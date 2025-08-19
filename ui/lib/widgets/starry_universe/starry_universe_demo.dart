/// 星空宇宙演示组件 - 展示完整的星空可视化功能
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:vector_math/vector_math.dart' as vm;
import 'core/cosmic_theme.dart';
import 'core/starry_canvas.dart';
import 'core/particle_system.dart';
import 'core/cosmic_animations.dart';
import 'core/data_mappers.dart';
import 'core/performance_optimizer.dart';

/// 星空宇宙演示页面
class StarryUniverseDemo extends ConsumerStatefulWidget {
  const StarryUniverseDemo({super.key});

  @override
  ConsumerState<StarryUniverseDemo> createState() => _StarryUniverseDemoState();
}

class _StarryUniverseDemoState extends ConsumerState<StarryUniverseDemo>
    with TickerProviderStateMixin {
  late OptimizedParticleSystem _particleSystem;
  late CosmicAnimationController _animationController;
  late AdaptiveQualityManager _qualityManager;
  late SpatialIndex _spatialIndex;
  
  final List<CelestialObject> _celestialObjects = [];
  final List<StarConnection> _connections = [];
  
  bool _showDebugInfo = false;
  String _currentMode = 'search'; // search, constellation, universe, nebula
  
  @override
  void initState() {
    super.initState();
    _initializeComponents();
    _generateDemoData();
  }
  
  @override
  void dispose() {
    _animationController.dispose();
    _particleSystem.clear();
    super.dispose();
  }
  
  /// 初始化核心组件
  void _initializeComponents() {
    _particleSystem = OptimizedParticleSystem(
      maxParticles: CosmicPerformanceConfig.maxParticles,
      spawnRate: 30.0,
    );
    
    _animationController = CosmicAnimationController();
    _animationController.initialize(this);
    
    _qualityManager = AdaptiveQualityManager();
    
    _spatialIndex = SpatialIndex();
    _spatialIndex.initialize(const Rect.fromLTWH(0, 0, 1000, 1000));
  }
  
  /// 生成演示数据
  void _generateDemoData() {
    _generateSearchStarRiver();
    _generateWisdomConstellation();
  }
  
  /// 生成搜索星河演示数据
  void _generateSearchStarRiver() {
    final demoSearchResults = [
      {
        'id': 'doc_1',
        'title': '人工智能发展史',
        'type': 'document',
        'score': 0.95,
        'snippet': '详细介绍AI的发展历程...',
      },
      {
        'id': 'img_1',
        'title': '神经网络架构图',
        'type': 'image',
        'score': 0.88,
        'snippet': '展示深度学习网络结构...',
      },
      {
        'id': 'code_1',
        'title': 'Transformer实现',
        'type': 'code',
        'score': 0.82,
        'snippet': 'Python实现的Transformer模型...',
      },
      {
        'id': 'person_1',
        'title': 'Geoffrey Hinton',
        'type': 'person',
        'score': 0.90,
        'snippet': '深度学习之父...',
      },
    ];
    
    final searchStars = SearchStarMapper.mapSearchResultsToStars(
      demoSearchResults,
      const Size(800, 600),
    );
    
    _celestialObjects.addAll(searchStars);
  }
  
  /// 生成智慧星座演示数据
  void _generateWisdomConstellation() {
    final demoEntities = [
      {
        'entity_id': 'entity_1',
        'name': '机器学习',
        'type': 'concept',
        'access_count': 25,
        'relationship_count': 8,
      },
      {
        'entity_id': 'entity_2',
        'name': '深度学习',
        'type': 'concept',
        'access_count': 30,
        'relationship_count': 12,
      },
      {
        'entity_id': 'entity_3',
        'name': 'TensorFlow',
        'type': 'project',
        'access_count': 15,
        'relationship_count': 5,
      },
    ];
    
    final constellationStars = ConstellationMapper.mapEntitiesToStars(
      demoEntities,
      const Size(800, 600),
    );
    
    _celestialObjects.addAll(constellationStars);
    
    // 生成实体间连接
    final demoRelationships = [
      {
        'source_entity_id': 'entity_1',
        'target_entity_id': 'entity_2',
        'strength': 0.9,
      },
      {
        'source_entity_id': 'entity_2',
        'target_entity_id': 'entity_3',
        'strength': 0.7,
      },
    ];
    
    final entityConnections = ConstellationMapper.generateEntityConnections(
      demoRelationships,
      constellationStars,
    );
    
    _connections.addAll(entityConnections);
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('🌌 星空知识宇宙'),
        backgroundColor: CosmicTheme.primaryCosmic,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: Icon(_showDebugInfo ? Icons.bug_report : Icons.bug_report_outlined),
            onPressed: () {
              setState(() {
                _showDebugInfo = !_showDebugInfo;
              });
            },
            tooltip: '调试信息',
          ),
          PopupMenuButton<String>(
            icon: const Icon(Icons.tune),
            onSelected: (value) {
              setState(() {
                _currentMode = value;
              });
              _handleModeChange(value);
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'search',
                child: Row(
                  children: [
                    Icon(Icons.search, color: CosmicTheme.starGold),
                    SizedBox(width: 8),
                    Text('搜索星河'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'constellation',
                child: Row(
                  children: [
                    Icon(Icons.scatter_plot, color: CosmicTheme.starBlue),
                    SizedBox(width: 8),
                    Text('智慧星座'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'universe',
                child: Row(
                  children: [
                    Icon(Icons.public, color: CosmicTheme.starPurple),
                    SizedBox(width: 8),
                    Text('知识宇宙'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'nebula',
                child: Row(
                  children: [
                    Icon(Icons.cloud, color: CosmicTheme.nebulaRed),
                    SizedBox(width: 8),
                    Text('相似星云'),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: Stack(
        children: [
          // 主要的星空画布
          StarryCanvas(
            particleSystem: _particleSystem,
            celestialObjects: _celestialObjects,
            connections: _connections,
            onTap: _handleCanvasTap,
            onObjectTap: _handleObjectTap,
            showDebugInfo: _showDebugInfo,
          ),
          
          // 控制面板
          Positioned(
            top: 16,
            left: 16,
            child: _buildControlPanel(),
          ),
          
          // 性能监控面板
          if (_showDebugInfo)
            Positioned(
              top: 16,
              right: 16,
              child: _buildPerformancePanel(),
            ),
          
          // 底部信息栏
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: _buildInfoBar(),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _triggerSpecialEffect,
        backgroundColor: CosmicTheme.starGold,
        child: const Icon(Icons.auto_awesome),
        tooltip: '触发特效',
      ),
    );
  }
  
  /// 构建控制面板
  Widget _buildControlPanel() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.7),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: CosmicTheme.starGold.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text(
            '🎮 控制台',
            style: TextStyle(
              color: CosmicTheme.starGold,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          
          // 模式选择
          Text(
            '当前模式: ${_getModeDisplayName(_currentMode)}',
            style: const TextStyle(color: Colors.white70, fontSize: 12),
          ),
          
          const SizedBox(height: 8),
          
          // 快速操作按钮
          Wrap(
            spacing: 8,
            runSpacing: 4,
            children: [
              _buildQuickButton('💫', '粒子爆发', () => _triggerParticleBurst()),
              _buildQuickButton('🌊', '星河流动', () => _triggerStarRiver()),
              _buildQuickButton('⭐', '新星诞生', () => _triggerStarBirth()),
              _buildQuickButton('🔗', '连接形成', () => _triggerConnection()),
            ],
          ),
        ],
      ),
    );
  }
  
  /// 构建性能监控面板
  Widget _buildPerformancePanel() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.7),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: CosmicTheme.starBlue.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text(
            '📊 性能监控',
            style: TextStyle(
              color: CosmicTheme.starBlue,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          
          Text(
            'FPS: ${_qualityManager.monitor.currentFPS.toStringAsFixed(1)}',
            style: const TextStyle(color: Colors.white70, fontSize: 11),
          ),
          Text(
            '粒子数: ${_particleSystem.particleCount}',
            style: const TextStyle(color: Colors.white70, fontSize: 11),
          ),
          Text(
            '星体数: ${_celestialObjects.length}',
            style: const TextStyle(color: Colors.white70, fontSize: 11),
          ),
          Text(
            '质量级别: ${_getQualityLevelName(_qualityManager.currentLevel)}',
            style: const TextStyle(color: Colors.white70, fontSize: 11),
          ),
        ],
      ),
    );
  }
  
  /// 构建信息栏
  Widget _buildInfoBar() {
    return Container(
      height: 60,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Colors.transparent,
            Colors.black.withOpacity(0.8),
          ],
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: Text(
              _getModeDescription(_currentMode),
              style: const TextStyle(
                color: Colors.white70,
                fontSize: 13,
              ),
            ),
          ),
          Text(
            '👆 点击星体查看详情 | 🔍 双指缩放导航',
            style: TextStyle(
              color: CosmicTheme.starGold.withOpacity(0.7),
              fontSize: 11,
            ),
          ),
        ],
      ),
    );
  }
  
  /// 构建快速操作按钮
  Widget _buildQuickButton(String icon, String tooltip, VoidCallback onPressed) {
    return SizedBox(
      width: 32,
      height: 32,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          padding: EdgeInsets.zero,
          backgroundColor: CosmicTheme.primaryCosmic.withOpacity(0.8),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
        ),
        child: Text(icon, style: const TextStyle(fontSize: 16)),
      ),
    );
  }
  
  /// 处理模式变化
  void _handleModeChange(String mode) {
    _animationController.respondToDataChange(
      DataChangeEvent(
        type: DataChangeType.userInteraction,
        metadata: {'mode': mode},
      ),
    );
    
    // 根据模式调整粒子系统
    switch (mode) {
      case 'search':
        _particleSystem.spawnRate = 50.0;
        break;
      case 'constellation':
        _particleSystem.spawnRate = 20.0;
        break;
      case 'universe':
        _particleSystem.spawnRate = 30.0;
        break;
      case 'nebula':
        _particleSystem.spawnRate = 80.0;
        break;
    }
  }
  
  /// 处理画布点击
  void _handleCanvasTap(vm.Vector2 position) {
    _animationController.respondToDataChange(
      DataChangeEvent(
        type: DataChangeType.userInteraction,
        position: position,
      ),
    );
    
    // 在点击位置创建粒子效果
    _particleSystem.burst(position, 20, color: CosmicTheme.starGold);
  }
  
  /// 处理天体对象点击
  void _handleObjectTap(CelestialObject object) {
    if (object is Star) {
      _showStarDetails(object);
    }
    
    _animationController.respondToDataChange(
      DataChangeEvent(
        type: DataChangeType.userInteraction,
        entityId: object.id,
        position: object.position,
      ),
    );
  }
  
  /// 显示星体详情
  void _showStarDetails(Star star) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: CosmicTheme.primaryCosmic,
        title: Text(
          '⭐ ${star.metadata['name'] ?? star.id}',
          style: const TextStyle(color: CosmicTheme.starGold),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '类型: ${star.metadata['type'] ?? '未知'}',
              style: const TextStyle(color: Colors.white70),
            ),
            Text(
              '重要性: ${((star.metadata['importance'] ?? 0.5) * 100).toStringAsFixed(1)}%',
              style: const TextStyle(color: Colors.white70),
            ),
            if (star.metadata['snippet'] != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  star.metadata['snippet'],
                  style: const TextStyle(color: Colors.white60, fontSize: 12),
                ),
              ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('关闭', style: TextStyle(color: CosmicTheme.starGold)),
          ),
        ],
      ),
    );
  }
  
  /// 触发特殊效果
  void _triggerSpecialEffect() {
    final center = vm.Vector2(400, 300); // 屏幕中心
    
    switch (_currentMode) {
      case 'search':
        ParticleEffects.createStarRiver(
          _particleSystem,
          vm.Vector2(100, 300),
          vm.Vector2(700, 300),
        );
        break;
      case 'constellation':
        final points = [
          center + vm.Vector2(-50, -50),
          center + vm.Vector2(50, -50),
          center + vm.Vector2(0, 50),
        ];
        ParticleEffects.createConstellation(_particleSystem, points);
        break;
      case 'universe':
        _particleSystem.burst(center, 100, color: CosmicTheme.starPurple);
        break;
      case 'nebula':
        ParticleEffects.createNebulaExpansion(_particleSystem, center);
        break;
    }
  }
  
  /// 快速操作 - 粒子爆发
  void _triggerParticleBurst() {
    final center = vm.Vector2(400, 300);
    _particleSystem.burst(center, 50, color: CosmicTheme.starRed);
  }
  
  /// 快速操作 - 星河流动
  void _triggerStarRiver() {
    ParticleEffects.createStarRiver(
      _particleSystem,
      vm.Vector2(0, 200),
      vm.Vector2(800, 400),
    );
  }
  
  /// 快速操作 - 新星诞生
  void _triggerStarBirth() {
    final newStar = Star(
      position: vm.Vector2(400, 300),
      size: 8.0,
      color: CosmicTheme.starGold,
      id: 'new_star_${DateTime.now().millisecondsSinceEpoch}',
      metadata: {'type': 'new_concept', 'name': '新概念'},
    );
    
    setState(() {
      _celestialObjects.add(newStar);
    });
    
    _animationController.respondToDataChange(
      const DataChangeEvent(type: DataChangeType.newEntity),
    );
  }
  
  /// 快速操作 - 连接形成
  void _triggerConnection() {
    if (_celestialObjects.length >= 2) {
      final star1 = _celestialObjects[0];
      final star2 = _celestialObjects[1];
      
      final connection = StarConnection(
        fromStarId: star1.id,
        toStarId: star2.id,
        strength: 0.8,
        color: CosmicTheme.connectionStrong,
        animated: true,
      );
      
      setState(() {
        _connections.add(connection);
      });
      
      _animationController.respondToDataChange(
        const DataChangeEvent(type: DataChangeType.strongConnection),
      );
    }
  }
  
  /// 获取模式显示名称
  String _getModeDisplayName(String mode) {
    switch (mode) {
      case 'search': return '搜索星河';
      case 'constellation': return '智慧星座';
      case 'universe': return '知识宇宙';
      case 'nebula': return '相似星云';
      default: return '未知模式';
    }
  }
  
  /// 获取模式描述
  String _getModeDescription(String mode) {
    switch (mode) {
      case 'search':
        return '搜索结果如银河流淌，相关度决定星体亮度，类型决定颜色';
      case 'constellation':
        return '实体数据组成星座图案，关系强度形成连接线';
      case 'universe':
        return '知识图谱呈现为引力场星系，聚类形成不同的星系群';
      case 'nebula':
        return '相似内容聚集成色彩星云，语义相近的文档形成粒子团';
      default:
        return '探索知识的星空宇宙';
    }
  }
  
  /// 获取质量级别名称
  String _getQualityLevelName(PerformanceLevel level) {
    switch (level) {
      case PerformanceLevel.ultra: return '超高';
      case PerformanceLevel.high: return '高';
      case PerformanceLevel.medium: return '中';
      case PerformanceLevel.low: return '低';
      case PerformanceLevel.potato: return '极低';
    }
  }
}