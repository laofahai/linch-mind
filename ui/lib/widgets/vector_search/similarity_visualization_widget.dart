// 相似性可视化组件 - 热力图、聚类图谱、网络图
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:math' as math;

import '../../models/data_insights_models.dart';
import '../../providers/vector_search_provider.dart';

/// 可视化模式
enum VisualizationMode {
  heatmap, // 相似度热力图
  network, // 网络关系图
  clustering, // 聚类分析图
  timeline, // 时间轴相似性
}

/// 相似性可视化组件
class SimilarityVisualizationWidget extends ConsumerStatefulWidget {
  final String? focusEntityId;
  final VoidCallback? onEntitySelected;
  final bool showControls;

  const SimilarityVisualizationWidget({
    super.key,
    this.focusEntityId,
    this.onEntitySelected,
    this.showControls = true,
  });

  @override
  ConsumerState<SimilarityVisualizationWidget> createState() =>
      _SimilarityVisualizationWidgetState();
}

class _SimilarityVisualizationWidgetState
    extends ConsumerState<SimilarityVisualizationWidget>
    with TickerProviderStateMixin {
  VisualizationMode _currentMode = VisualizationMode.heatmap;
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  double _similarityThreshold = 0.3;
  bool _showLabels = true;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // 控制面板
        if (widget.showControls) _buildControlPanel(),

        // 可视化内容
        Expanded(
          child: AnimatedBuilder(
            animation: _fadeAnimation,
            builder: (context, child) {
              return Opacity(
                opacity: _fadeAnimation.value,
                child: _buildVisualizationContent(),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildControlPanel() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        border: Border(
          bottom: BorderSide(
            color: Theme.of(context).dividerColor,
            width: 1,
          ),
        ),
      ),
      child: Column(
        children: [
          // 模式选择
          Row(
            children: [
              Text(
                '可视化模式',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: Theme.of(context).primaryColor,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: VisualizationMode.values.map((mode) {
                      return Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: _buildModeChip(mode),
                      );
                    }).toList(),
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 12),

          // 参数控制
          Row(
            children: [
              // 相似度阈值
              Text(
                '阈值',
                style: TextStyle(
                  fontSize: 14,
                  color: Theme.of(context).textTheme.bodyMedium?.color,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Slider(
                  value: _similarityThreshold,
                  min: 0.0,
                  max: 1.0,
                  divisions: 20,
                  label: _similarityThreshold.toStringAsFixed(2),
                  onChanged: (value) {
                    setState(() {
                      _similarityThreshold = value;
                    });
                  },
                ),
              ),

              // 标签显示开关
              Switch(
                value: _showLabels,
                onChanged: (value) {
                  setState(() {
                    _showLabels = value;
                  });
                },
              ),
              const Text('标签'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildModeChip(VisualizationMode mode) {
    final isSelected = _currentMode == mode;
    final icon = _getModeIcon(mode);
    final label = _getModeLabel(mode);

    return FilterChip(
      selected: isSelected,
      label: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16),
          const SizedBox(width: 4),
          Text(label),
        ],
      ),
      onSelected: (selected) {
        if (selected) {
          setState(() {
            _currentMode = mode;
          });
          _animationController.reset();
          _animationController.forward();
        }
      },
      selectedColor: Theme.of(context).primaryColor.withValues(alpha: 0.2),
      checkmarkColor: Theme.of(context).primaryColor,
    );
  }

  Widget _buildVisualizationContent() {
    switch (_currentMode) {
      case VisualizationMode.heatmap:
        return _buildHeatmapView();
      case VisualizationMode.network:
        return _buildNetworkView();
      case VisualizationMode.clustering:
        return _buildClusteringView();
      case VisualizationMode.timeline:
        return _buildTimelineView();
    }
  }

  Widget _buildHeatmapView() {
    final similarityState = ref.watch(similarityAnalysisProvider);

    if (similarityState.isLoading) {
      return _buildLoadingState('生成相似度热力图...');
    }

    if (similarityState.results.isEmpty) {
      return _buildEmptyState('选择一个实体以查看相似度分析');
    }

    return _buildHeatmap(similarityState.results);
  }

  Widget _buildHeatmap(List<SimilarityResult> results) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // 热力图标题
          Row(
            children: [
              Icon(
                Icons.grid_on,
                color: Theme.of(context).primaryColor,
              ),
              const SizedBox(width: 8),
              Text(
                '相似度热力图',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  color: Theme.of(context).primaryColor,
                ),
              ),
              const Spacer(),
              _buildHeatmapLegend(),
            ],
          ),

          const SizedBox(height: 16),

          // 热力图网格
          Expanded(
            child: _buildHeatmapGrid(results),
          ),
        ],
      ),
    );
  }

  Widget _buildHeatmapGrid(List<SimilarityResult> results) {
    // 过滤符合阈值的结果
    final filteredResults = results
        .where((result) => result.similarity >= _similarityThreshold)
        .toList();

    if (filteredResults.isEmpty) {
      return Center(
        child: Text(
          '没有符合阈值 ${_similarityThreshold.toStringAsFixed(2)} 的相似实体',
          style: TextStyle(color: Theme.of(context).hintColor),
        ),
      );
    }

    // 创建网格布局
    const crossAxisCount = 5;
    final itemCount =
        (filteredResults.length / crossAxisCount).ceil() * crossAxisCount;

    return GridView.builder(
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        crossAxisSpacing: 2,
        mainAxisSpacing: 2,
        childAspectRatio: 1,
      ),
      itemCount: itemCount,
      itemBuilder: (context, index) {
        if (index < filteredResults.length) {
          return _buildHeatmapCell(filteredResults[index]);
        }
        return Container(color: Colors.grey.withValues(alpha: 0.1));
      },
    );
  }

  Widget _buildHeatmapCell(SimilarityResult result) {
    final intensity = result.similarity;
    final color = _getHeatmapColor(intensity);

    return Tooltip(
      message:
          '${result.targetContent ?? result.targetId}\n相似度: ${(intensity * 100).toStringAsFixed(1)}%',
      child: Container(
        decoration: BoxDecoration(
          color: color,
          border: Border.all(
            color: Colors.white.withValues(alpha: 0.3),
            width: 0.5,
          ),
        ),
        child: InkWell(
          onTap: () {
            _showSimilarityDetails(result);
          },
          child: Center(
            child: _showLabels
                ? Text(
                    '${(intensity * 100).toInt()}',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      color: intensity > 0.6 ? Colors.white : Colors.black87,
                    ),
                  )
                : null,
          ),
        ),
      ),
    );
  }

  Widget _buildHeatmapLegend() {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          '低',
          style: TextStyle(
            fontSize: 12,
            color: Theme.of(context).hintColor,
          ),
        ),
        const SizedBox(width: 4),
        Container(
          width: 100,
          height: 8,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(4),
            gradient: const LinearGradient(
              colors: [
                Colors.blue,
                Colors.green,
                Colors.yellow,
                Colors.orange,
                Colors.red,
              ],
            ),
          ),
        ),
        const SizedBox(width: 4),
        Text(
          '高',
          style: TextStyle(
            fontSize: 12,
            color: Theme.of(context).hintColor,
          ),
        ),
      ],
    );
  }

  Widget _buildNetworkView() {
    final similarityState = ref.watch(similarityAnalysisProvider);

    if (similarityState.isLoading) {
      return _buildLoadingState('构建关系网络图...');
    }

    if (similarityState.results.isEmpty) {
      return _buildEmptyState('选择一个实体以查看关系网络');
    }

    return _buildNetworkGraph(similarityState.results);
  }

  Widget _buildNetworkGraph(List<SimilarityResult> results) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // 网络图标题
          Row(
            children: [
              Icon(
                Icons.account_tree,
                color: Theme.of(context).primaryColor,
              ),
              const SizedBox(width: 8),
              Text(
                '相似性网络图',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  color: Theme.of(context).primaryColor,
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // 网络图画布
          Expanded(
            child: _buildNetworkCanvas(results),
          ),
        ],
      ),
    );
  }

  Widget _buildNetworkCanvas(List<SimilarityResult> results) {
    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Theme.of(context).dividerColor,
        ),
      ),
      child: CustomPaint(
        painter: NetworkGraphPainter(
          results: results
              .where((r) => r.similarity >= _similarityThreshold)
              .toList(),
          showLabels: _showLabels,
          theme: Theme.of(context),
        ),
        child: Container(),
      ),
    );
  }

  Widget _buildClusteringView() {
    final clusteringState = ref.watch(clusteringAnalysisProvider);

    if (clusteringState.isLoading) {
      return _buildLoadingState('执行聚类分析...');
    }

    if (clusteringState.clusters.isEmpty) {
      return _buildEmptyState('点击开始聚类分析');
    }

    return _buildClusteringResult(clusteringState.clusters);
  }

  Widget _buildClusteringResult(List<ClusterResult> clusters) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // 聚类标题
          Row(
            children: [
              Icon(
                Icons.scatter_plot,
                color: Theme.of(context).primaryColor,
              ),
              const SizedBox(width: 8),
              Text(
                '聚类分析结果',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  color: Theme.of(context).primaryColor,
                ),
              ),
              const Spacer(),
              ElevatedButton.icon(
                onPressed: () {
                  ref
                      .read(clusteringAnalysisProvider.notifier)
                      .analyzeClusters();
                },
                icon: const Icon(Icons.refresh),
                label: const Text('重新分析'),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // 聚类图表
          Expanded(
            child: _buildClusterChart(clusters),
          ),
        ],
      ),
    );
  }

  Widget _buildClusterChart(List<ClusterResult> clusters) {
    return GridView.builder(
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: 1,
      ),
      itemCount: clusters.length,
      itemBuilder: (context, index) {
        final cluster = clusters[index];
        return _buildClusterCard(cluster);
      },
    );
  }

  Widget _buildClusterCard(ClusterResult cluster) {
    final color = _getClusterColor(cluster.clusterId);

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        onTap: () {
          _showClusterDetails(cluster);
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 集群标题
              Row(
                children: [
                  Container(
                    width: 12,
                    height: 12,
                    decoration: BoxDecoration(
                      color: color,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      cluster.label.isNotEmpty
                          ? cluster.label
                          : '集群 ${cluster.clusterId}',
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 14,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 8),

              // 统计信息
              Text(
                '${cluster.entityIds.length} 个实体',
                style: TextStyle(
                  fontSize: 12,
                  color: Theme.of(context).hintColor,
                ),
              ),

              if (cluster.coherence > 0)
                Text(
                  '一致性: ${(cluster.coherence * 100).toStringAsFixed(1)}%',
                  style: TextStyle(
                    fontSize: 12,
                    color: Theme.of(context).hintColor,
                  ),
                ),

              const SizedBox(height: 8),

              // 关键词
              if (cluster.keywords.isNotEmpty)
                Expanded(
                  child: Wrap(
                    spacing: 4,
                    runSpacing: 4,
                    children: cluster.keywords.take(3).map((keyword) {
                      return Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: color.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          keyword,
                          style: TextStyle(
                            fontSize: 10,
                            color: color.withValues(alpha: 0.8),
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTimelineView() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Row(
            children: [
              Icon(
                Icons.timeline,
                color: Theme.of(context).primaryColor,
              ),
              const SizedBox(width: 8),
              Text(
                '时间轴相似性分析',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  color: Theme.of(context).primaryColor,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Expanded(
            child: Center(
              child: Text(
                '时间轴相似性分析功能开发中...',
                style: TextStyle(
                  color: Theme.of(context).hintColor,
                  fontSize: 16,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // 辅助方法
  IconData _getModeIcon(VisualizationMode mode) {
    switch (mode) {
      case VisualizationMode.heatmap:
        return Icons.grid_on;
      case VisualizationMode.network:
        return Icons.account_tree;
      case VisualizationMode.clustering:
        return Icons.scatter_plot;
      case VisualizationMode.timeline:
        return Icons.timeline;
    }
  }

  String _getModeLabel(VisualizationMode mode) {
    switch (mode) {
      case VisualizationMode.heatmap:
        return '热力图';
      case VisualizationMode.network:
        return '网络图';
      case VisualizationMode.clustering:
        return '聚类图';
      case VisualizationMode.timeline:
        return '时间轴';
    }
  }

  Color _getHeatmapColor(double intensity) {
    if (intensity < 0.2) return Colors.blue.withValues(alpha: 0.3);
    if (intensity < 0.4) return Colors.green.withValues(alpha: 0.5);
    if (intensity < 0.6) return Colors.yellow.withValues(alpha: 0.7);
    if (intensity < 0.8) return Colors.orange.withValues(alpha: 0.8);
    return Colors.red.withValues(alpha: 0.9);
  }

  Color _getClusterColor(int clusterId) {
    final colors = [
      Colors.blue,
      Colors.green,
      Colors.orange,
      Colors.purple,
      Colors.teal,
      Colors.pink,
      Colors.indigo,
      Colors.cyan,
      Colors.lime,
      Colors.amber,
    ];
    return colors[clusterId % colors.length];
  }

  void _showSimilarityDetails(SimilarityResult result) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('相似度详情'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('源实体: ${result.sourceContent ?? result.sourceId}'),
            const SizedBox(height: 8),
            Text('目标实体: ${result.targetContent ?? result.targetId}'),
            const SizedBox(height: 8),
            Text('相似度: ${(result.similarity * 100).toStringAsFixed(2)}%'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('关闭'),
          ),
        ],
      ),
    );
  }

  void _showClusterDetails(ClusterResult cluster) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('集群详情: ${cluster.label}'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('实体数量: ${cluster.entityIds.length}'),
            const SizedBox(height: 8),
            Text('一致性: ${(cluster.coherence * 100).toStringAsFixed(1)}%'),
            const SizedBox(height: 8),
            if (cluster.keywords.isNotEmpty) ...[
              const Text('关键词:'),
              const SizedBox(height: 4),
              Text(cluster.keywords.join(', ')),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('关闭'),
          ),
        ],
      ),
    );
  }

  // 状态组件
  Widget _buildLoadingState(String message) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(),
          const SizedBox(height: 16),
          Text(message),
        ],
      ),
    );
  }

  Widget _buildEmptyState(String message) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.visibility_off,
            size: 64,
            color: Theme.of(context).hintColor,
          ),
          const SizedBox(height: 16),
          Text(
            message,
            style: TextStyle(
              color: Theme.of(context).hintColor,
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }
}

/// 网络图绘制器
class NetworkGraphPainter extends CustomPainter {
  final List<SimilarityResult> results;
  final bool showLabels;
  final ThemeData theme;

  NetworkGraphPainter({
    required this.results,
    required this.showLabels,
    required this.theme,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (results.isEmpty) return;

    final paint = Paint()..style = PaintingStyle.fill;

    final linePaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;

    // 简化的网络图布局
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) * 0.3;

    // 绘制连接线
    for (int i = 0; i < results.length; i++) {
      final result = results[i];
      final angle = (i / results.length) * 2 * math.pi;
      final nodePos = Offset(
        center.dx + radius * math.cos(angle),
        center.dy + radius * math.sin(angle),
      );

      // 绘制到中心的连线
      linePaint.color = _getConnectionColor(result.similarity);
      linePaint.strokeWidth = result.similarity * 3;

      canvas.drawLine(center, nodePos, linePaint);
    }

    // 绘制节点
    for (int i = 0; i < results.length; i++) {
      final result = results[i];
      final angle = (i / results.length) * 2 * math.pi;
      final nodePos = Offset(
        center.dx + radius * math.cos(angle),
        center.dy + radius * math.sin(angle),
      );

      // 绘制节点
      paint.color = _getNodeColor(result.similarity);
      canvas.drawCircle(nodePos, 8, paint);

      // 绘制标签
      if (showLabels && result.targetContent != null) {
        final textPainter = TextPainter(
          text: TextSpan(
            text: result.targetContent!.length > 10
                ? '${result.targetContent!.substring(0, 10)}...'
                : result.targetContent!,
            style: TextStyle(
              color: theme.textTheme.bodySmall?.color,
              fontSize: 10,
            ),
          ),
          textDirection: TextDirection.ltr,
        );
        textPainter.layout();
        textPainter.paint(
          canvas,
          Offset(
            nodePos.dx - textPainter.width / 2,
            nodePos.dy + 12,
          ),
        );
      }
    }

    // 绘制中心节点
    paint.color = theme.primaryColor;
    canvas.drawCircle(center, 12, paint);
  }

  Color _getConnectionColor(double similarity) {
    if (similarity >= 0.8) return Colors.red.withValues(alpha: 0.8);
    if (similarity >= 0.6) return Colors.orange.withValues(alpha: 0.6);
    if (similarity >= 0.4) return Colors.blue.withValues(alpha: 0.4);
    return Colors.grey.withValues(alpha: 0.3);
  }

  Color _getNodeColor(double similarity) {
    if (similarity >= 0.8) return Colors.red;
    if (similarity >= 0.6) return Colors.orange;
    if (similarity >= 0.4) return Colors.blue;
    return Colors.grey;
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return true;
  }
}
