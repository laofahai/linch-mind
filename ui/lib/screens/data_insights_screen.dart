// 智能数据洞察屏幕 - 取代MyMind占位页面
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/data_insights_provider.dart';
import '../providers/app_providers.dart';
import '../widgets/data_insights/responsive_dashboard_layout.dart';
import '../widgets/data_insights/stats_overview_widget.dart';
import '../widgets/data_insights/entity_display_widget.dart';
import '../widgets/data_insights/ai_insights_widget.dart';
import '../widgets/data_insights/timeline_widget.dart';
import '../widgets/data_insights/search_and_filter_widget.dart';
import '../widgets/skeleton/data_insights_skeleton.dart';
import '../widgets/skeleton/connector_skeleton.dart';
import '../widgets/skeleton/loading_state_wrapper.dart';
import '../utils/app_logger.dart';

/// 智能数据洞察屏幕
class DataInsightsScreen extends ConsumerStatefulWidget {
  const DataInsightsScreen({super.key});

  @override
  ConsumerState<DataInsightsScreen> createState() => _DataInsightsScreenState();
}

class _DataInsightsScreenState extends ConsumerState<DataInsightsScreen>
    with TickerProviderStateMixin {
  late TabController _mainTabController;

  @override
  void initState() {
    super.initState();
    _mainTabController = TabController(length: 3, vsync: this);

    // 记录页面访问
    AppLogger.info('智能数据洞察页面打开', module: 'DataInsightsScreen');
  }

  @override
  void dispose() {
    _mainTabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final dataInsightsState = ref.watch(dataInsightsProvider);

    return Scaffold(
      body: ResponsiveDashboardLayout(
        maxWidth: 1400,
        header: _buildHeader(context, theme),
        statsOverview: LoadingStateWrapper(
          isLoading: dataInsightsState.isLoading,
          error: dataInsightsState.error,
          loadingWidget: const StatsOverviewSkeleton(),
          errorWidget: ErrorRecoveryWidget(
            error: dataInsightsState.error ?? '加载统计数据失败',
            onRetry: () => ref.read(dataInsightsProvider.notifier).refresh(),
          ),
          child: const StatsOverviewWidget(),
        ),
        mainContent: _buildMainContent(context, theme),
        sidebar: _buildSidebar(context, theme),
        bottomContent: _buildBottomActions(context, theme),
      ),
      floatingActionButton: _buildFloatingActionButton(context),
    );
  }

  Widget _buildHeader(BuildContext context, ThemeData theme) {
    final dataInsightsState = ref.watch(dataInsightsProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            // 主标题和副标题
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [
                              theme.colorScheme.primary,
                              theme.colorScheme.secondary,
                            ],
                          ),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Icon(
                          Icons.psychology,
                          color: theme.colorScheme.onPrimary,
                          size: 24,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '智能数据洞察',
                              style: theme.textTheme.headlineMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: theme.colorScheme.onSurface,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'AI驱动的个人数据分析和智能发现',
                              style: theme.textTheme.bodyLarge?.copyWith(
                                color: theme.colorScheme.onSurfaceVariant,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            // 快速操作按钮
            QuickActionGroup(
              actions: [
                QuickAction(
                  label: '刷新数据',
                  icon: Icons.refresh,
                  onPressed: () => _refreshAllData(),
                ),
                QuickAction(
                  label: '导出报告',
                  icon: Icons.file_download,
                  onPressed: () => _exportReport(),
                ),
                QuickAction(
                  label: '设置',
                  icon: Icons.settings,
                  onPressed: () => _openSettings(),
                ),
              ],
            ),
          ],
        ),

        const SizedBox(height: 16),

        // 状态信息栏
        if (dataInsightsState.lastRefresh != null)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: theme.colorScheme.surfaceContainerHighest
                  .withValues(alpha: 0.5),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.access_time,
                  size: 16,
                  color: theme.colorScheme.onSurfaceVariant,
                ),
                const SizedBox(width: 8),
                Text(
                  '最后更新: ${_formatLastRefresh(dataInsightsState.lastRefresh!)}',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
                const Spacer(),
                if (dataInsightsState.isLoading)
                  SizedBox(
                    width: 12,
                    height: 12,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: theme.colorScheme.primary,
                    ),
                  )
                else
                  Icon(
                    Icons.check_circle,
                    size: 16,
                    color: Colors.green,
                  ),
              ],
            ),
          ),

        const SizedBox(height: 20),

        // 搜索和筛选
        const SmartSearchWidget(),
      ],
    );
  }

  Widget _buildMainContent(BuildContext context, ThemeData theme) {
    return Column(
      children: [
        // 主要内容标签页
        Container(
          height: 48,
          decoration: BoxDecoration(
            color: theme.colorScheme.surfaceContainerHighest
                .withValues(alpha: 0.3),
            borderRadius: BorderRadius.circular(8),
          ),
          child: TabBar(
            controller: _mainTabController,
            tabs: const [
              Tab(
                icon: Icon(Icons.dashboard, size: 18),
                text: '概览',
              ),
              Tab(
                icon: Icon(Icons.storage, size: 18),
                text: '实体数据',
              ),
              Tab(
                icon: Icon(Icons.timeline, size: 18),
                text: '活动时间线',
              ),
            ],
          ),
        ),

        const SizedBox(height: 20),

        // 标签页内容 - 修复RenderBox约束问题
        Expanded(
          child: LayoutBuilder(
            builder: (context, constraints) {
              final maxHeight = constraints.maxHeight.isFinite
                  ? constraints.maxHeight
                  : MediaQuery.of(context).size.height * 0.6;

              return SizedBox(
                height: maxHeight.clamp(
                    300.0, MediaQuery.of(context).size.height * 0.7),
                child: TabBarView(
                  controller: _mainTabController,
                  children: [
                    _buildOverviewTab(context),
                    _buildEntitiesTab(context),
                    _buildTimelineTab(context),
                  ],
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildOverviewTab(BuildContext context) {
    final dataInsightsState = ref.watch(dataInsightsProvider);

    return LoadingStateWrapper(
      isLoading:
          dataInsightsState.isLoading && dataInsightsState.overview == null,
      error: dataInsightsState.error,
      loadingWidget: SingleChildScrollView(
        child: Column(
          children: const [
            AIInsightsSkeleton(),
            SizedBox(height: 16),
            Row(
              children: [
                Expanded(child: TrendingEntitiesSkeleton()),
                SizedBox(width: 16),
                Expanded(child: EntityBreakdownChartSkeleton()),
              ],
            ),
          ],
        ),
      ),
      errorWidget: ErrorRecoveryWidget(
        error: dataInsightsState.error ?? '加载概览数据失败',
        onRetry: () => ref.read(dataInsightsProvider.notifier).refresh(),
      ),
      child: SingleChildScrollView(
        child: LayoutBuilder(
          builder: (context, constraints) {
            // 根据可用高度动态调整布局
            final availableHeight = constraints.maxHeight.isFinite
                ? constraints.maxHeight
                : MediaQuery.of(context).size.height * 0.6;
            final isWideScreen = constraints.maxWidth > 800;

            return FadeTransitionWrapper(
              child: Column(
                children: [
                  // AI洞察和趋势实体 - 动态高度
                  Container(
                    constraints: BoxConstraints(
                      minHeight: 200.0,
                      maxHeight: (availableHeight * 0.65).clamp(200.0, 350.0),
                    ),
                    child: isWideScreen
                        ? Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: const [
                              Expanded(
                                flex: 2,
                                child: SlideTransitionWrapper(
                                  child: AIInsightsWidget(),
                                ),
                              ),
                              SizedBox(width: 20),
                              Expanded(
                                flex: 1,
                                child: SlideTransitionWrapper(
                                  beginOffset: Offset(0.1, 0),
                                  child: TrendingEntitiesWidget(),
                                ),
                              ),
                            ],
                          )
                        : Column(
                            children: const [
                              Expanded(
                                flex: 2,
                                child: SlideTransitionWrapper(
                                  child: AIInsightsWidget(),
                                ),
                              ),
                              SizedBox(height: 16),
                              Expanded(
                                flex: 1,
                                child: SlideTransitionWrapper(
                                  beginOffset: Offset(0, 0.1),
                                  child: TrendingEntitiesWidget(),
                                ),
                              ),
                            ],
                          ),
                  ),

                  const SizedBox(height: 16),

                  // 实体类型分布图表 - 限制高度
                  ConstrainedBox(
                    constraints: BoxConstraints(
                      maxHeight: (availableHeight * 0.3).clamp(120.0, 200.0),
                    ),
                    child: const ScaleTransitionWrapper(
                      child: EntityBreakdownChart(),
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildEntitiesTab(BuildContext context) {
    final entityListState = ref.watch(entityListProvider);

    return LoadingStateWrapper(
      isLoading: entityListState.isLoading && entityListState.entities.isEmpty,
      error: entityListState.error,
      loadingWidget: const SingleChildScrollView(
        child: TrendingEntitiesSkeleton(),
      ),
      errorWidget: ErrorRecoveryWidget(
        error: entityListState.error ?? '加载实体数据失败',
        onRetry: () =>
            ref.read(entityListProvider.notifier).loadEntities(refresh: true),
      ),
      child: const SingleChildScrollView(
        child: FadeTransitionWrapper(
          child: EntityDisplayWidget(
            showAllTypes: true,
          ),
        ),
      ),
    );
  }

  Widget _buildTimelineTab(BuildContext context) {
    final timelineState = ref.watch(timelineProvider);

    return LoadingStateWrapper(
      isLoading: timelineState.isLoading && timelineState.items.isEmpty,
      error: timelineState.error,
      loadingWidget: const SingleChildScrollView(
        child: TimelineSkeleton(),
      ),
      errorWidget: ErrorRecoveryWidget(
        error: timelineState.error ?? '加载时间线数据失败',
        onRetry: () => ref.read(timelineProvider.notifier).loadTimeline(),
      ),
      child: const SingleChildScrollView(
        child: SlideTransitionWrapper(
          beginOffset: Offset(0, 0.05),
          child: TimelineWidget(
            showFilters: true,
          ),
        ),
      ),
    );
  }

  Widget _buildSidebar(BuildContext context, ThemeData theme) {
    return Column(
      children: [
        // 系统状态概览
        _buildSystemStatusCard(context, theme),

        const SizedBox(height: 16),

        // 快速统计
        _buildQuickStatsCard(context, theme),

        const SizedBox(height: 16),

        // 最近活动预览
        CollapsibleCard(
          title: '最近活动',
          subtitle: '系统活动快速预览',
          initiallyExpanded: false,
          child: const TimelineWidget(
            maxItems: 5,
            showFilters: false,
          ),
        ),
      ],
    );
  }

  Widget _buildSystemStatusCard(BuildContext context, ThemeData theme) {
    final connectorsAsync = ref.watch(connectorsProvider);

    return CollapsibleCard(
      title: '系统状态',
      subtitle: '连接器和服务状态',
      child: connectorsAsync.when(
        data: (connectors) => FadeTransitionWrapper(
          child: Column(
            children: [
              // 动态显示真实连接器状态
              for (final connector in connectors) ...[
                () {
                  final statusInfo = _getConnectorStatusInfo(connector);
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: SlideTransitionWrapper(
                      duration: Duration(
                          milliseconds:
                              200 + (connectors.indexOf(connector) * 50)),
                      beginOffset: const Offset(0.1, 0),
                      child: _buildStatusItem(
                        context,
                        connector.displayName,
                        statusInfo['status'] as String,
                        statusInfo['icon'] as IconData,
                        statusInfo['color'] as Color,
                      ),
                    ),
                  );
                }(),
              ],

              // AI分析服务 - 静态状态
              SlideTransitionWrapper(
                duration:
                    Duration(milliseconds: 200 + (connectors.length * 50)),
                beginOffset: const Offset(0.1, 0),
                child: _buildStatusItem(
                  context,
                  'AI分析服务',
                  '正常',
                  Icons.psychology,
                  Colors.blue,
                ),
              ),
            ],
          ),
        ),
        loading: () => const SystemStatusCardSkeleton(),
        error: (error, stack) => ErrorRecoveryWidget(
          error: '加载连接器状态失败: $error',
          onRetry: () => ref.refresh(connectorsProvider),
        ),
      ),
    );
  }

  /// 获取连接器状态信息
  Map<String, dynamic> _getConnectorStatusInfo(dynamic connector) {
    String status;
    IconData icon;
    Color color;

    // 检查连接器状态
    final connectorState = connector.state ?? connector.status;

    switch (connectorState.toString()) {
      case 'ConnectorState.running':
        status = '运行中';
        icon = Icons.sensors;
        color = Colors.green;
        break;
      case 'ConnectorState.starting':
        status = '启动中';
        icon = Icons.pending;
        color = Colors.orange;
        break;
      case 'ConnectorState.stopping':
        status = '停止中';
        icon = Icons.pending;
        color = Colors.orange;
        break;
      case 'ConnectorState.stopped':
        status = '已停止';
        icon = Icons.stop_circle;
        color = Colors.grey;
        break;
      case 'ConnectorState.error':
        status = '错误';
        icon = Icons.error;
        color = Colors.red;
        break;
      default:
        // 这种情况理论上不应该出现，但保留作为安全措施
        status = '未知状态';
        icon = Icons.help_outline;
        color = Colors.grey;
    }

    return {
      'status': status,
      'icon': icon,
      'color': color,
    };
  }

  Widget _buildStatusItem(
    BuildContext context,
    String name,
    String status,
    IconData icon,
    Color color,
  ) {
    final theme = Theme.of(context);

    return Row(
      children: [
        Icon(icon, size: 16, color: color),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            name,
            style: theme.textTheme.bodySmall,
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            status,
            style: theme.textTheme.bodySmall?.copyWith(
              color: color,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildQuickStatsCard(BuildContext context, ThemeData theme) {
    final dataInsightsState = ref.watch(dataInsightsProvider);
    final overview = dataInsightsState.overview;

    return CollapsibleCard(
      title: '快速统计',
      child: LoadingStateWrapper(
        isLoading: dataInsightsState.isLoading && overview == null,
        error: dataInsightsState.error,
        loadingWidget: const QuickStatsCardSkeleton(),
        errorWidget: ErrorRecoveryWidget(
          error: dataInsightsState.error ?? '加载统计数据失败',
          onRetry: () => ref.read(dataInsightsProvider.notifier).refresh(),
        ),
        child: FadeTransitionWrapper(
          child: Column(
            children: [
              SlideTransitionWrapper(
                duration: const Duration(milliseconds: 200),
                beginOffset: const Offset(0.1, 0),
                child: _buildQuickStatItem(
                    '总实体数', '${_getTotalEntities(overview)}', Icons.storage),
              ),
              const SizedBox(height: 8),
              SlideTransitionWrapper(
                duration: const Duration(milliseconds: 250),
                beginOffset: const Offset(0.1, 0),
                child: _buildQuickStatItem('AI洞察数',
                    '${overview?.recentInsights.length ?? 0}', Icons.lightbulb),
              ),
              const SizedBox(height: 8),
              SlideTransitionWrapper(
                duration: const Duration(milliseconds: 300),
                beginOffset: const Offset(0.1, 0),
                child: _buildQuickStatItem(
                    '活动记录',
                    '${overview?.recentActivities.length ?? 0}',
                    Icons.timeline),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildQuickStatItem(String label, String value, IconData icon) {
    final theme = Theme.of(context);

    return Row(
      children: [
        Icon(icon, size: 16, color: theme.colorScheme.primary),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            label,
            style: theme.textTheme.bodySmall,
          ),
        ),
        Text(
          value,
          style: theme.textTheme.bodySmall?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildBottomActions(BuildContext context, ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(
              Icons.info_outline,
              size: 16,
              color: theme.colorScheme.onSurfaceVariant,
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                '数据实时更新中，AI持续分析你的使用模式以提供个性化洞察',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ),
            TextButton(
              onPressed: () => _showHelpDialog(context),
              child: const Text('了解更多'),
            ),
          ],
        ),
      ),
    );
  }

  Widget? _buildFloatingActionButton(BuildContext context) {
    return FloatingActionButton.extended(
      heroTag: "dataInsightsFAB",
      onPressed: () => _showQuickActions(context),
      icon: const Icon(Icons.auto_awesome),
      label: const Text('AI助手'),
      tooltip: '快速AI操作',
    );
  }

  // 辅助方法

  String _formatLastRefresh(DateTime lastRefresh) {
    final now = DateTime.now();
    final difference = now.difference(lastRefresh);

    if (difference.inMinutes < 1) {
      return '刚刚';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}分钟前';
    } else {
      return '${difference.inHours}小时前';
    }
  }

  int _getTotalEntities(overview) {
    if (overview?.entityBreakdown == null) return 0;
    final breakdown = overview.entityBreakdown;
    return breakdown.url +
        breakdown.filePath +
        breakdown.email +
        breakdown.phone +
        breakdown.keyword +
        breakdown.other;
  }

  void _refreshAllData() {
    AppLogger.info('刷新所有数据', module: 'DataInsightsScreen');
    ref.read(dataInsightsProvider.notifier).refresh();
    ref.read(timelineProvider.notifier).loadTimeline();

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('正在刷新数据...')),
    );
  }

  void _exportReport() {
    // TODO: 实现导出报告功能
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('导出功能开发中...')),
    );
  }

  void _openSettings() {
    // TODO: 打开数据洞察设置
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('设置功能开发中...')),
    );
  }

  void _showQuickActions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'AI快速操作',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
            ),
            const SizedBox(height: 16),
            ListTile(
              leading: const Icon(Icons.search),
              title: const Text('智能搜索'),
              subtitle: const Text('使用AI搜索你的数据'),
              onTap: () {
                Navigator.pop(context);
                // 聚焦搜索框
              },
            ),
            ListTile(
              leading: const Icon(Icons.insights),
              title: const Text('生成洞察'),
              subtitle: const Text('基于当前数据生成新洞察'),
              onTap: () {
                Navigator.pop(context);
                // TODO: 手动触发洞察生成
              },
            ),
            ListTile(
              leading: const Icon(Icons.auto_fix_high),
              title: const Text('数据优化建议'),
              subtitle: const Text('获取数据管理优化建议'),
              onTap: () {
                Navigator.pop(context);
                // TODO: 显示优化建议
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showHelpDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('关于智能数据洞察'),
        content: const Text(
          'Linch Mind通过AI技术分析你的数据使用模式，自动识别重要信息，生成个性化洞察，帮助你更好地理解和利用个人数据。',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('了解了'),
          ),
        ],
      ),
    );
  }
}
