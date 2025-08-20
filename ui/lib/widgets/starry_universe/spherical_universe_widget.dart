/// 球形宇宙组件 - 简单直接的实现
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'spherical_config.dart';
import 'spherical_camera.dart';
import 'spherical_renderer.dart';
import 'spherical_data_mapper.dart';
import 'spherical_interactions.dart';

/// 球形宇宙主组件
class SphericalUniverseWidget extends StatefulWidget {
  final List<dynamic>? searchData;
  final List<dynamic>? entityData;
  final dynamic graphData;
  final List<dynamic>? vectorData;
  final Function(String)? onDataSelected;
  final bool showDebugInfo;
  final bool enableInteractions;

  const SphericalUniverseWidget({
    super.key,
    this.searchData,
    this.entityData,
    this.graphData,
    this.vectorData,
    this.onDataSelected,
    this.showDebugInfo = false,
    this.enableInteractions = true,
  });

  @override
  State<SphericalUniverseWidget> createState() =>
      _SphericalUniverseWidgetState();
}

class _SphericalUniverseWidgetState extends State<SphericalUniverseWidget>
    with TickerProviderStateMixin, AutomaticKeepAliveClientMixin {
  late SphericalCamera _camera;
  late SphericalDataMapper _dataMapper;
  late SphericalInteractions _interactions;

  List<SphericalPoint> _points = [];
  String? _selectedPointId;
  bool _isInitialized = false;

  // 性能监控
  int _frameCount = 0;
  double _fps = 60.0;
  DateTime? _lastFrameTime;

  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
    _initializeComponents();
    _updateData();
  }

  @override
  void didUpdateWidget(SphericalUniverseWidget oldWidget) {
    super.didUpdateWidget(oldWidget);

    // 检查数据是否变化
    if (widget.searchData != oldWidget.searchData ||
        widget.entityData != oldWidget.entityData ||
        widget.graphData != oldWidget.graphData ||
        widget.vectorData != oldWidget.vectorData) {
      _updateData();
    }
  }

  @override
  void dispose() {
    _camera.dispose();
    super.dispose();
  }

  /// 初始化组件
  void _initializeComponents() {
    _camera = SphericalCamera();
    _dataMapper = SphericalDataMapper();
    _interactions = SphericalInteractions(
      camera: _camera,
      onPointSelected: _handlePointSelected,
      onInteractionStart: _handleInteractionStart,
      onInteractionEnd: _handleInteractionEnd,
    );

    _camera.addListener(_handleCameraChange);

    setState(() {
      _isInitialized = true;
    });
  }

  /// 更新数据
  void _updateData() {
    if (!_isInitialized) return;

    _points = _dataMapper.mapAllData(
      searchData: widget.searchData,
      entityData: widget.entityData,
      graphData: widget.graphData,
      vectorData: widget.vectorData,
    );

    if (mounted) {
      setState(() {});
    }
  }

  /// 处理相机变化
  void _handleCameraChange() {
    if (mounted) {
      setState(() {});
      _updatePerformanceMetrics();
    }
  }

  /// 处理点选择
  void _handlePointSelected(String pointId) {
    setState(() {
      _selectedPointId = pointId;
    });
    widget.onDataSelected?.call(pointId);
  }

  /// 处理交互开始
  void _handleInteractionStart() {
    // 可以在这里停止自动动画等
  }

  /// 处理交互结束
  void _handleInteractionEnd() {
    // 可以在这里恢复自动动画等
  }

  /// 更新性能指标
  void _updatePerformanceMetrics() {
    final now = DateTime.now();
    if (_lastFrameTime != null) {
      final frameDuration = now.difference(_lastFrameTime!);
      _fps = 1000.0 / frameDuration.inMilliseconds.clamp(1, 1000);
      _frameCount++;
    }
    _lastFrameTime = now;
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);

    if (!_isInitialized) {
      return Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [
              SphericalConfig.backgroundColor,
              SphericalConfig.backgroundAccent
            ],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: const Center(
          child: CircularProgressIndicator(
            color: Color(0xFFFFD700),
          ),
        ),
      );
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        final screenSize = Size(constraints.maxWidth, constraints.maxHeight);

        return Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [
                SphericalConfig.backgroundColor,
                SphericalConfig.backgroundAccent
              ],
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
            ),
          ),
          child: Stack(
            children: [
              // 主要的球形宇宙画布
              if (widget.enableInteractions)
                _buildInteractiveCanvas(screenSize)
              else
                _buildStaticCanvas(screenSize),

              // 调试信息面板
              if (widget.showDebugInfo) _buildDebugPanel(),

              // 选中数据面板
              if (_selectedPointId != null) _buildSelectedDataPanel(),

              // 控制面板
              _buildControlPanel(),
            ],
          ),
        );
      },
    );
  }

  /// 构建交互式画布
  Widget _buildInteractiveCanvas(Size screenSize) {
    return RawGestureDetector(
      gestures: _interactions.getGestureRecognizers(_points, screenSize),
      child: Focus(
        autofocus: true,
        onKeyEvent: (node, event) {
          if (_interactions.handleKeyEvent(event, _points)) {
            return KeyEventResult.handled;
          }
          return KeyEventResult.ignored;
        },
        child: Listener(
          onPointerSignal: _interactions.handlePointerSignal,
          child: CustomPaint(
            painter: SphericalRenderer(
              camera: _camera,
              points: _points,
              selectedPointId: _selectedPointId,
              showDebugInfo: false, // 调试信息单独显示
            ),
            size: Size.infinite,
          ),
        ),
      ),
    );
  }

  /// 构建静态画布
  Widget _buildStaticCanvas(Size screenSize) {
    return CustomPaint(
      painter: SphericalRenderer(
        camera: _camera,
        points: _points,
        selectedPointId: _selectedPointId,
        showDebugInfo: false,
      ),
      size: Size.infinite,
    );
  }

  /// 构建调试面板
  Widget _buildDebugPanel() {
    return Positioned(
      top: 16,
      left: 16,
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.8),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: Colors.green.withOpacity(0.5),
            width: 1,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '调试信息',
              style: TextStyle(
                color: Colors.green,
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 8),
            ...(() {
              final cameraInfo = _camera.getDebugInfo();
              final stats = _dataMapper.getDataTypeStats(_points);

              return [
                _debugText('FPS: ${_fps.toStringAsFixed(1)}'),
                _debugText('帧数: $_frameCount'),
                _debugText('总点数: ${_points.length}'),
                _debugText(
                    '可见: ${_camera.getVisiblePoints(_points, MediaQuery.of(context).size).length}'),
                _debugText('相机半径: ${cameraInfo['viewRadius']}'),
                _debugText('θ角: ${cameraInfo['rotationTheta']}°'),
                _debugText('φ角: ${cameraInfo['rotationPhi']}°'),
                _debugText('缩放: ${cameraInfo['zoomLevel']}x'),
                const SizedBox(height: 4),

                // 数据类型统计
                ...stats.entries.map((entry) => _debugText(
                      '${entry.key}: ${entry.value}',
                      color: SphericalConfig.dataTypeColors[entry.key],
                    )),
              ];
            })(),
          ],
        ),
      ),
    );
  }

  /// 调试文本
  Widget _debugText(String text, {Color? color}) {
    return Text(
      text,
      style: TextStyle(
        color: color ?? Colors.green,
        fontSize: 11,
        fontFamily: 'monospace',
      ),
    );
  }

  /// 构建选中数据面板
  Widget _buildSelectedDataPanel() {
    final selectedPoint = _points.firstWhere(
      (point) => point.id == _selectedPointId,
      orElse: () => _points.first,
    );

    return Positioned(
      bottom: 16,
      left: 16,
      right: 16,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.9),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: selectedPoint.color.withOpacity(0.7),
            width: 2,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Container(
                  width: 16,
                  height: 16,
                  decoration: BoxDecoration(
                    color: selectedPoint.color,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    '${selectedPoint.type.toUpperCase()} - ${selectedPoint.id}',
                    style: TextStyle(
                      color: selectedPoint.color,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close, color: Colors.white70),
                  onPressed: () {
                    setState(() {
                      _selectedPointId = null;
                    });
                  },
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              '位置: r=${selectedPoint.radius.toStringAsFixed(1)}, '
              'θ=${(selectedPoint.theta * 180 / 3.14159).toStringAsFixed(1)}°, '
              'φ=${(selectedPoint.phi * 180 / 3.14159).toStringAsFixed(1)}°',
              style: const TextStyle(
                color: Colors.white70,
                fontSize: 12,
                fontFamily: 'monospace',
              ),
            ),
            if (selectedPoint.data.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                '数据: ${selectedPoint.data.toString()}',
                style: const TextStyle(
                  color: Colors.white60,
                  fontSize: 11,
                ),
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ],
        ),
      ),
    );
  }

  /// 构建控制面板
  Widget _buildControlPanel() {
    return Positioned(
      top: 16,
      right: 16,
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.8),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: const Color(0xFFFFD700).withOpacity(0.5),
            width: 1,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            const Text(
              '控制',
              style: TextStyle(
                color: Color(0xFFFFD700),
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),

            const SizedBox(height: 12),

            // 重置按钮
            _controlButton(
              Icons.refresh,
              '重置',
              () => _camera.reset(),
            ),

            const SizedBox(height: 8),

            // 数据类型按钮
            _controlButton(
              Icons.search,
              '搜索',
              () => _interactions.focusOnDataType(_points, 'search'),
              color: SphericalConfig.dataTypeColors['search'],
            ),

            const SizedBox(height: 4),

            _controlButton(
              Icons.scatter_plot,
              '实体',
              () => _interactions.focusOnDataType(_points, 'entity'),
              color: SphericalConfig.dataTypeColors['entity'],
            ),

            const SizedBox(height: 4),

            _controlButton(
              Icons.account_tree,
              '图谱',
              () => _interactions.focusOnDataType(_points, 'graph'),
              color: SphericalConfig.dataTypeColors['graph'],
            ),

            const SizedBox(height: 4),

            _controlButton(
              Icons.cloud,
              '向量',
              () => _interactions.focusOnDataType(_points, 'vector'),
              color: SphericalConfig.dataTypeColors['vector'],
            ),

            if (widget.enableInteractions) ...[
              const SizedBox(height: 12),
              const Text(
                '快捷键',
                style: TextStyle(
                  color: Colors.white70,
                  fontSize: 10,
                ),
              ),
              const Text(
                'SPACE: 重置\n方向键: 旋转\n+/-: 缩放\n1-4: 聚焦',
                style: TextStyle(
                  color: Colors.white54,
                  fontSize: 9,
                  fontFamily: 'monospace',
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ],
        ),
      ),
    );
  }

  /// 控制按钮
  Widget _controlButton(
    IconData icon,
    String label,
    VoidCallback onPressed, {
    Color? color,
  }) {
    return SizedBox(
      width: 80,
      height: 28,
      child: ElevatedButton.icon(
        onPressed: onPressed,
        icon: Icon(icon, size: 12, color: color ?? Colors.white),
        label: Text(
          label,
          style: TextStyle(
            fontSize: 10,
            color: color ?? Colors.white,
          ),
        ),
        style: ElevatedButton.styleFrom(
          backgroundColor: (color ?? Colors.white).withOpacity(0.1),
          foregroundColor: color ?? Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 4),
          side: BorderSide(
            color: (color ?? Colors.white).withOpacity(0.3),
            width: 1,
          ),
        ),
      ),
    );
  }
}
