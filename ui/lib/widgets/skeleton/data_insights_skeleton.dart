import 'package:flutter/material.dart';
import 'skeleton_widgets.dart';
import '../data_insights/responsive_dashboard_layout.dart';

/// 统计概览骨架屏
class StatsOverviewSkeleton extends StatelessWidget {
  const StatsOverviewSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return RepaintBoundary(
      child: ResponsiveGrid(
        maxCrossAxisExtent: 280,
        childAspectRatio: 3.2,
        children: List.generate(4, (index) => const StatCardSkeleton()),
      ),
    );
  }
}

/// 统计卡片骨架
class StatCardSkeleton extends StatelessWidget {
  const StatCardSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return SkeletonCard(
      child: LayoutBuilder(
        builder: (context, constraints) {
          final availableHeight = constraints.maxHeight.isFinite 
              ? constraints.maxHeight 
              : 120.0;
          
          return SizedBox(
            height: availableHeight.clamp(80.0, 120.0),
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  // 顶部行：图标和趋势指示器
                  Row(
                    children: [
                      SkeletonBox(
                        width: 36,
                        height: 36,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      const Spacer(),
                      SkeletonBox(
                        width: 60,
                        height: 24,
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4), // 减少间距
                  // 主要数值
                  const SkeletonText(width: 80, height: 20), // 减少高度
                  const SizedBox(height: 2), // 减少间距
                  // 标题
                  const SkeletonText(width: 120, height: 14), // 减少高度
                  const SizedBox(height: 2),
                  // 副标题
                  const SkeletonText(width: 100, height: 12), // 减少高度
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

/// AI洞察骨架屏
class AIInsightsSkeleton extends StatelessWidget {
  const AIInsightsSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final maxHeight = constraints.maxHeight.isFinite 
            ? constraints.maxHeight.clamp(200.0, 350.0)
            : 300.0;
            
        return SkeletonCard(
          height: maxHeight,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 标题行
              Row(
                children: [
                  const SkeletonText(width: 120, height: 20),
                  const Spacer(),
                  SkeletonBox(
                    width: 80,
                    height: 32,
                    borderRadius: BorderRadius.circular(16),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              // AI洞察内容
              Expanded(
                child: Column(
                  children: [
                    _buildInsightItem(),
                    const SizedBox(height: 12),
                    _buildInsightItem(),
                    const SizedBox(height: 12),
                    _buildInsightItem(),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildInsightItem() {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: const [
        SkeletonCircle(size: 24),
        SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SkeletonText(width: double.infinity, height: 16),
              SizedBox(height: 4),
              SkeletonText(
                width: 300,
                height: 14,
              ),
            ],
          ),
        ),
      ],
    );
  }
}

/// 实体类型分布图表骨架
class EntityBreakdownChartSkeleton extends StatelessWidget {
  const EntityBreakdownChartSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final availableHeight = constraints.maxHeight.isFinite 
            ? constraints.maxHeight.clamp(120.0, 300.0)
            : 200.0;
        final chartHeight = (availableHeight * 0.4).clamp(60.0, 120.0);
        
        return SkeletonCard(
          height: availableHeight,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              const SkeletonText(width: 120, height: 18),
              const SizedBox(height: 12),
              // 图表区域
              SizedBox(
                height: chartHeight,
                child: Row(
                  children: List.generate(6, (index) => 
                    Expanded(
                      flex: [2, 3, 2, 4, 1, 2][index],
                      child: Container(
                        margin: const EdgeInsets.symmetric(horizontal: 1),
                        child: SkeletonBox(
                          height: double.infinity,
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              // 图例区域
              Flexible(
                child: Wrap(
                  spacing: 12,
                  runSpacing: 6,
                  children: List.generate(6, (index) => 
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        SkeletonBox(
                          width: 12,
                          height: 12,
                          borderRadius: BorderRadius.circular(6),
                        ),
                        const SizedBox(width: 6),
                        SkeletonText(
                          width: 60 + (index * 10.0), // 不同长度的标签
                          height: 14,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

/// 热门实体骨架屏
class TrendingEntitiesSkeleton extends StatelessWidget {
  const TrendingEntitiesSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final maxHeight = constraints.maxHeight.isFinite 
            ? constraints.maxHeight.clamp(250.0, 450.0)
            : 400.0;
            
        return SkeletonCard(
          height: maxHeight,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 标题和搜索框
              Row(
                children: [
                  const SkeletonText(width: 100, height: 20),
                  const Spacer(),
                  SkeletonBox(
                    width: 200,
                    height: 36,
                    borderRadius: BorderRadius.circular(18),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              // 实体列表
              Expanded(
                child: ListView.separated(
                  itemCount: 8,
                  separatorBuilder: (context, index) => const SizedBox(height: 12),
                  itemBuilder: (context, index) => const SkeletonListItem(
                    hasAvatar: true,
                    hasSubtitle: true,
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

/// 时间线骨架屏
class TimelineSkeleton extends StatelessWidget {
  const TimelineSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final maxHeight = constraints.maxHeight.isFinite 
            ? constraints.maxHeight.clamp(250.0, 450.0)
            : 400.0;
            
        return SkeletonCard(
          height: maxHeight,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SkeletonText(width: 80, height: 20),
              const SizedBox(height: 16),
              Expanded(
                child: ListView.separated(
                  itemCount: 6,
                  separatorBuilder: (context, index) => const SizedBox(height: 16),
                  itemBuilder: (context, index) => _buildTimelineItem(),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildTimelineItem() {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 时间轴指示器
        Column(
          children: [
            SkeletonCircle(size: 12),
            if (true) // 不是最后一个
              Container(
                width: 2,
                height: 60,
                margin: const EdgeInsets.symmetric(vertical: 4),
                child: const SkeletonBox(width: 2, height: 60),
              ),
          ],
        ),
        const SizedBox(width: 16),
        // 内容区域
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: const [
              SkeletonText(width: 80, height: 12), // 时间
              SizedBox(height: 4),
              SkeletonText(width: double.infinity, height: 16), // 标题
              SizedBox(height: 4),
              SkeletonText(
                width: 250,
                height: 14,
              ), // 描述
            ],
          ),
        ),
      ],
    );
  }
}

/// 完整的数据洞察页面骨架屏
class DataInsightsPageSkeleton extends StatelessWidget {
  const DataInsightsPageSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        return SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              // 统计概览
              const StatsOverviewSkeleton(),
              const SizedBox(height: 20),
              
              // AI洞察和实体分布图表
              ConstrainedBox(
                constraints: const BoxConstraints(
                  maxHeight: 350,
                ),
                child: const Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      flex: 2,
                      child: AIInsightsSkeleton(),
                    ),
                    SizedBox(width: 16),
                    Expanded(
                      flex: 1,
                      child: EntityBreakdownChartSkeleton(),
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 20),
              
              // 热门实体和时间线
              ConstrainedBox(
                constraints: const BoxConstraints(
                  maxHeight: 450,
                ),
                child: const Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(child: TrendingEntitiesSkeleton()),
                    SizedBox(width: 16),
                    Expanded(child: TimelineSkeleton()),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}