/// 球形宇宙界面 - 基于新6文件架构的球面可视化
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/universe_provider.dart';
import '../widgets/starry_universe/spherical_universe.dart';
import '../widgets/universe/universe_control_panel.dart';
import '../widgets/universe/connector_detail_panel.dart';
import '../models/connector_lifecycle_models.dart';
import '../utils/responsive_utils.dart';
import '../utils/app_logger.dart';

/// 球形宇宙主界面
class UniverseScreen extends ConsumerStatefulWidget {
  const UniverseScreen({super.key});

  @override
  ConsumerState<UniverseScreen> createState() => _UniverseScreenState();
}

class _UniverseScreenState extends ConsumerState<UniverseScreen> {
  bool _showControlPanel = true;
  bool _showDetailPanel = false;

  @override
  void initState() {
    super.initState();
    AppLogger.info('球形宇宙界面初始化', module: 'UniverseScreen');
  }

  @override
  void dispose() {
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final universeState = ref.watch(universeProvider);
    final isLoading = ref.watch(isUniverseLoadingProvider);
    final error = ref.watch(universeErrorProvider);

    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          // 主要的球形宇宙视图
          _buildUniverseView(context, universeState, isLoading, error),

          // 控制面板
          if (_showControlPanel) _buildControlPanel(context),

          // 连接器详情面板
          if (_showDetailPanel && universeState.selectedConnectorId != null)
            _buildDetailPanel(context),

          // 顶部工具栏
          _buildTopToolbar(context, universeState),

          // 加载指示器
          if (isLoading) _buildLoadingIndicator(context),
        ],
      ),
    );
  }

  /// 构建宇宙视图
  Widget _buildUniverseView(BuildContext context, UniverseState state,
      bool isLoading, String? error) {
    if (error != null) {
      return _buildErrorView(context, error);
    }

    if (isLoading && state.celestialObjects.isEmpty) {
      return _buildInitialLoadingView(context);
    }

    // 使用新的球形宇宙组件（6文件架构）
    return SphericalUniverseWidget(
      searchData: state.searchData,
      entityData: state.entityData,
      graphData: state.graphData,
      vectorData: state.vectorData,
      showDebugInfo: true,
      enableInteractions: true,
      onDataSelected: (dataId) {
        AppLogger.info('球形宇宙数据选中', module: 'UniverseScreen', data: {
          'data_id': dataId,
        });
        // 可以在这里处理数据选中逻辑
      },
    );
  }

  /// 构建错误视图
  Widget _buildErrorView(BuildContext context, String error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.error_outline,
            size: 64,
            color: Colors.red.shade400,
          ),
          const SizedBox(height: 16),
          Text(
            '宇宙数据加载失败',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  color: Colors.white,
                ),
          ),
          const SizedBox(height: 8),
          Container(
            constraints: const BoxConstraints(maxWidth: 400),
            child: Text(
              error,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.white70,
                  ),
              textAlign: TextAlign.center,
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () => ref.read(universeProvider.notifier).forceRefresh(),
            icon: const Icon(Icons.refresh),
            label: const Text('重新加载'),
          ),
        ],
      ),
    );
  }

  /// 构建初始加载视图
  Widget _buildInitialLoadingView(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          SizedBox(
            width: 80,
            height: 80,
            child: CircularProgressIndicator(
              strokeWidth: 3,
              valueColor: AlwaysStoppedAnimation<Color>(
                Colors.blue.shade400,
              ),
            ),
          ),
          const SizedBox(height: 24),
          Text(
            '正在构建宇宙...',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: Colors.white,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            '加载连接器数据并生成3D可视化',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.white70,
                ),
          ),
        ],
      ),
    );
  }

  /// 构建控制面板
  Widget _buildControlPanel(BuildContext context) {
    return Positioned(
      left: 16,
      top: 80,
      bottom: 16,
      child: ResponsiveWrapper(
        mobile: Container(width: 280, child: UniverseControlPanel()),
        tablet: Container(width: 320, child: UniverseControlPanel()),
        desktop: Container(width: 360, child: UniverseControlPanel()),
      ),
    );
  }

  /// 构建详情面板
  Widget _buildDetailPanel(BuildContext context) {
    return Positioned(
      right: 16,
      top: 80,
      bottom: 16,
      child: ResponsiveWrapper(
        mobile: Container(width: 320, child: ConnectorDetailPanel()),
        tablet: Container(width: 380, child: ConnectorDetailPanel()),
        desktop: Container(width: 420, child: ConnectorDetailPanel()),
      ),
    );
  }

  /// 构建顶部工具栏
  Widget _buildTopToolbar(BuildContext context, UniverseState state) {
    final stats = ref.watch(universeStatsProvider);

    return Positioned(
      top: 0,
      left: 0,
      right: 0,
      child: Container(
        height: 64,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.black.withValues(alpha: 0.8),
              Colors.transparent,
            ],
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            children: [
              // 标题
              Icon(
                Icons.language,
                color: Colors.white,
                size: 24,
              ),
              const SizedBox(width: 12),
              Text(
                '数据宇宙',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
              ),

              const SizedBox(width: 32),

              // 统计信息
              _buildStatChip('连接器', stats['total'] ?? 0, Colors.blue.shade400),
              const SizedBox(width: 8),
              _buildStatChip(
                  '运行中', stats['running'] ?? 0, Colors.green.shade400),
              const SizedBox(width: 8),
              _buildStatChip('错误', stats['error'] ?? 0, Colors.red.shade400),
              const SizedBox(width: 8),
              _buildStatChip(
                  '连接', stats['connections'] ?? 0, Colors.purple.shade400),

              const Spacer(),

              // 控制按钮
              IconButton(
                onPressed: () =>
                    setState(() => _showControlPanel = !_showControlPanel),
                icon: Icon(
                  _showControlPanel
                      ? Icons.view_sidebar
                      : Icons.view_sidebar_outlined,
                  color: Colors.white70,
                ),
                tooltip: '切换控制面板',
              ),

              IconButton(
                onPressed: () =>
                    ref.read(universeProvider.notifier).forceRefresh(),
                icon: const Icon(
                  Icons.refresh,
                  color: Colors.white70,
                ),
                tooltip: '刷新数据',
              ),

              IconButton(
                onPressed: () =>
                    setState(() => _showDetailPanel = !_showDetailPanel),
                icon: Icon(
                  _showDetailPanel ? Icons.info : Icons.info_outline,
                  color: Colors.white70,
                ),
                tooltip: '切换详情面板',
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// 构建统计芯片
  Widget _buildStatChip(String label, int value, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.5)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            label,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(width: 4),
          Text(
            value.toString(),
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  /// 构建加载指示器
  Widget _buildLoadingIndicator(BuildContext context) {
    return Positioned(
      top: 80,
      right: 16,
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.black.withValues(alpha: 0.7),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.white.withValues(alpha: 0.2)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(Colors.blue.shade400),
              ),
            ),
            const SizedBox(width: 8),
            const Text(
              '同步中...',
              style: TextStyle(
                color: Colors.white,
                fontSize: 12,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
