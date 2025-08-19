/// 星空宇宙组件 - 生产级的集成组件
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:vector_math/vector_math.dart' as vm;
import 'core/cosmic_theme.dart';
import 'core/starry_canvas.dart';
import 'core/particle_system.dart';
import 'core/cosmic_animations.dart';
import 'core/performance_optimizer.dart';
import 'providers/starry_universe_provider.dart';

/// 星空宇宙主组件
class StarryUniverseWidget extends ConsumerStatefulWidget {
  final String? initialMode;
  final bool enableInteraction;
  final bool showControls;
  final Function(String)? onModeChanged;
  final Function(CelestialObject)? onObjectSelected;
  
  const StarryUniverseWidget({
    super.key,
    this.initialMode = 'search',
    this.enableInteraction = true,
    this.showControls = true,
    this.onModeChanged,
    this.onObjectSelected,
  });

  @override
  ConsumerState<StarryUniverseWidget> createState() => _StarryUniverseWidgetState();
}

class _StarryUniverseWidgetState extends ConsumerState<StarryUniverseWidget>
    with TickerProviderStateMixin {
  late OptimizedParticleSystem _particleSystem;
  late CosmicAnimationController _animationController;
  late AdaptiveQualityManager _qualityManager;
  
  bool _isInitialized = false;
  String? _selectedObjectId;

  @override
  void initState() {
    super.initState();
    _initializeComponents();
    
    // 延迟初始化数据
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (widget.initialMode != null) {
        ref.read(starryUniverseProvider.notifier).switchMode(widget.initialMode!);
      }
    });
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
    
    setState(() {
      _isInitialized = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (!_isInitialized) {
      return const Center(
        child: CircularProgressIndicator(color: CosmicTheme.starGold),
      );
    }

    final starryState = ref.watch(starryUniverseProvider);

    return Container(
      decoration: BoxDecoration(
        gradient: CosmicTheme.createCosmicBackground(),
      ),
      child: Stack(
        children: [
          // 主要的星空画布
          Positioned.fill(
            child: _buildStarryCanvas(starryState),
          ),
          
          // 加载指示器
          if (starryState.isLoading)
            Positioned.fill(
              child: Container(
                color: Colors.black.withOpacity(0.3),
                child: const Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      CircularProgressIndicator(color: CosmicTheme.starGold),
                      SizedBox(height: 16),
                      Text(
                        '正在加载星空数据...',
                        style: TextStyle(color: Colors.white70),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          
          // 错误提示
          if (starryState.error != null)
            Positioned(
              top: 16,
              left: 16,
              right: 16,
              child: _buildErrorCard(starryState.error!),
            ),
          
          // 控制面板
          if (widget.showControls)
            Positioned(
              top: 16,
              left: 16,
              child: _buildControlPanel(starryState),
            ),
          
          // 模式切换器
          if (widget.showControls)
            Positioned(
              top: 16,
              right: 16,
              child: _buildModeSelector(starryState),
            ),
          
          // 对象详情面板
          if (_selectedObjectId != null)
            Positioned(
              bottom: 16,
              left: 16,
              right: 16,
              child: _buildObjectDetailsPanel(),
            ),
        ],
      ),
    );
  }

  /// 构建星空画布
  Widget _buildStarryCanvas(StarryUniverseState state) {
    return StarryCanvas(
      particleSystem: _particleSystem,
      celestialObjects: state.celestialObjects,
      connections: state.connections,
      onTap: widget.enableInteraction ? _handleCanvasTap : null,
      onObjectTap: widget.enableInteraction ? _handleObjectTap : null,
      enableGestures: widget.enableInteraction,
    );
  }

  /// 构建错误卡片
  Widget _buildErrorCard(String error) {
    return Card(
      color: Colors.red.shade900.withOpacity(0.9),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            const Icon(Icons.error_outline, color: Colors.redAccent),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                error,
                style: const TextStyle(color: Colors.white),
              ),
            ),
            IconButton(
              icon: const Icon(Icons.close, color: Colors.white70),
              onPressed: () {
                ref.read(starryUniverseProvider.notifier).clearError();
              },
            ),
          ],
        ),
      ),
    );
  }

  /// 构建控制面板
  Widget _buildControlPanel(StarryUniverseState state) {
    return Card(
      color: Colors.black.withOpacity(0.8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                const Icon(
                  Icons.control_camera,
                  color: CosmicTheme.starGold,
                  size: 16,
                ),
                const SizedBox(width: 4),
                const Text(
                  '控制台',
                  style: TextStyle(
                    color: CosmicTheme.starGold,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            
            // 性能指标
            Text(
              'FPS: ${_qualityManager.monitor.currentFPS.toStringAsFixed(1)}',
              style: const TextStyle(color: Colors.white70, fontSize: 10),
            ),
            Text(
              '粒子: ${_particleSystem.particleCount}',
              style: const TextStyle(color: Colors.white70, fontSize: 10),
            ),
            Text(
              '对象: ${state.celestialObjects.length}',
              style: const TextStyle(color: Colors.white70, fontSize: 10),
            ),
            
            const SizedBox(height: 8),
            
            // 快速操作
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                _buildQuickActionButton(
                  Icons.refresh,
                  '刷新',
                  () => ref.read(starryUniverseProvider.notifier).refreshData(),
                ),
                const SizedBox(width: 4),
                _buildQuickActionButton(
                  Icons.auto_awesome,
                  '特效',
                  _triggerRandomEffect,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  /// 构建模式选择器
  Widget _buildModeSelector(StarryUniverseState state) {
    return Card(
      color: Colors.black.withOpacity(0.8),
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              '视图模式',
              style: TextStyle(
                color: CosmicTheme.starBlue,
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
            ),
            const SizedBox(height: 8),
            
            ..._buildModeButtons(state.currentMode),
          ],
        ),
      ),
    );
  }

  /// 构建模式按钮
  List<Widget> _buildModeButtons(String currentMode) {
    final modes = [
      {'id': 'search', 'icon': Icons.search, 'label': '搜索', 'color': CosmicTheme.starGold},
      {'id': 'constellation', 'icon': Icons.scatter_plot, 'label': '星座', 'color': CosmicTheme.starBlue},
      {'id': 'universe', 'icon': Icons.public, 'label': '宇宙', 'color': CosmicTheme.starPurple},
      {'id': 'nebula', 'icon': Icons.cloud, 'label': '星云', 'color': CosmicTheme.nebulaRed},
    ];

    return modes.map((mode) {
      final isSelected = mode['id'] == currentMode;
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 2),
        child: SizedBox(
          width: 80,
          height: 32,
          child: ElevatedButton.icon(
            onPressed: () => _switchMode(mode['id'] as String),
            icon: Icon(
              mode['icon'] as IconData,
              size: 14,
              color: isSelected ? Colors.black : (mode['color'] as Color),
            ),
            label: Text(
              mode['label'] as String,
              style: TextStyle(
                fontSize: 10,
                color: isSelected ? Colors.black : Colors.white70,
              ),
            ),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 8),
              backgroundColor: isSelected 
                  ? (mode['color'] as Color)
                  : Colors.transparent,
              foregroundColor: isSelected ? Colors.black : Colors.white70,
              side: BorderSide(
                color: (mode['color'] as Color).withOpacity(0.5),
              ),
            ),
          ),
        ),
      );
    }).toList();
  }

  /// 构建对象详情面板
  Widget _buildObjectDetailsPanel() {
    final selectedObject = ref.read(starryUniverseProvider)
        .celestialObjects
        .where((obj) => obj.id == _selectedObjectId)
        .firstOrNull;

    if (selectedObject == null) {
      return const SizedBox.shrink();
    }

    return Card(
      color: Colors.black.withOpacity(0.9),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Icon(
                  _getObjectIcon(selectedObject),
                  color: selectedObject.color,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    selectedObject.metadata['name'] ?? selectedObject.id,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close, color: Colors.white70),
                  onPressed: () {
                    setState(() {
                      _selectedObjectId = null;
                    });
                  },
                ),
              ],
            ),
            
            if (selectedObject.metadata['type'] != null)
              Padding(
                padding: const EdgeInsets.only(top: 4),
                child: Text(
                  '类型: ${selectedObject.metadata['type']}',
                  style: const TextStyle(color: Colors.white70, fontSize: 12),
                ),
              ),
            
            if (selectedObject.metadata['snippet'] != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  selectedObject.metadata['snippet'],
                  style: const TextStyle(color: Colors.white60, fontSize: 11),
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
          ],
        ),
      ),
    );
  }

  /// 构建快速操作按钮
  Widget _buildQuickActionButton(IconData icon, String tooltip, VoidCallback onPressed) {
    return SizedBox(
      width: 28,
      height: 28,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          padding: EdgeInsets.zero,
          backgroundColor: CosmicTheme.primaryCosmic.withOpacity(0.8),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
        ),
        child: Icon(icon, size: 14, color: CosmicTheme.starGold),
      ),
    );
  }

  /// 切换模式
  void _switchMode(String mode) {
    ref.read(starryUniverseProvider.notifier).switchMode(mode);
    widget.onModeChanged?.call(mode);
    
    // 清除选中的对象
    setState(() {
      _selectedObjectId = null;
    });
  }

  /// 处理画布点击
  void _handleCanvasTap(vm.Vector2 position) {
    // 清除选中状态
    setState(() {
      _selectedObjectId = null;
    });

    // 触发粒子效果
    _particleSystem.burst(position, 15, color: CosmicTheme.starGold);
    
    // 触发动画响应
    _animationController.respondToDataChange(
      DataChangeEvent(
        type: DataChangeType.userInteraction,
        position: position,
      ),
    );
  }

  /// 处理对象点击
  void _handleObjectTap(CelestialObject object) {
    setState(() {
      _selectedObjectId = object.id;
    });

    widget.onObjectSelected?.call(object);

    // 触发粒子效果
    _particleSystem.burst(object.position, 10, color: object.color);
    
    // 触发动画响应
    _animationController.respondToDataChange(
      DataChangeEvent(
        type: DataChangeType.userInteraction,
        entityId: object.id,
        position: object.position,
      ),
    );
  }

  /// 触发随机特效
  void _triggerRandomEffect() {
    final center = vm.Vector2(400, 300);
    final effects = [
      () => _particleSystem.burst(center, 50, color: CosmicTheme.starRed),
      () => _particleSystem.burst(center, 30, color: CosmicTheme.starBlue),
      () => _particleSystem.burst(center, 40, color: CosmicTheme.starPurple),
    ];
    
    final randomEffect = effects[DateTime.now().millisecond % effects.length];
    randomEffect();
  }

  /// 获取对象图标
  IconData _getObjectIcon(CelestialObject object) {
    final type = object.metadata['type'] as String?;
    switch (type?.toLowerCase()) {
      case 'document':
        return Icons.description;
      case 'image':
        return Icons.image;
      case 'code':
        return Icons.code;
      case 'person':
        return Icons.person;
      case 'concept':
        return Icons.lightbulb_outline;
      case 'project':
        return Icons.work_outline;
      default:
        return Icons.star;
    }
  }
}

/// 星空搜索组件
class StarrySearchWidget extends ConsumerWidget {
  final Function(String)? onSearch;
  
  const StarrySearchWidget({
    super.key,
    this.onSearch,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.8),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: CosmicTheme.starGold.withOpacity(0.3)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              const Icon(Icons.search, color: CosmicTheme.starGold),
              const SizedBox(width: 8),
              const Text(
                '搜索知识宇宙',
                style: TextStyle(
                  color: CosmicTheme.starGold,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          
          TextField(
            decoration: InputDecoration(
              hintText: '输入搜索关键词...',
              hintStyle: TextStyle(color: Colors.white.withOpacity(0.5)),
              filled: true,
              fillColor: Colors.white.withOpacity(0.1),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide(color: CosmicTheme.starGold.withOpacity(0.3)),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide(color: CosmicTheme.starGold.withOpacity(0.3)),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: CosmicTheme.starGold),
              ),
              prefixIcon: const Icon(Icons.search, color: CosmicTheme.starGold),
            ),
            style: const TextStyle(color: Colors.white),
            onSubmitted: (query) {
              if (query.isNotEmpty) {
                ref.read(starryUniverseProvider.notifier).searchData(query);
                onSearch?.call(query);
              }
            },
          ),
        ],
      ),
    );
  }
}