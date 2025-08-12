import 'package:flutter/material.dart';
import 'skeleton_widgets.dart';

/// 连接器卡片骨架
class ConnectorCardSkeleton extends StatelessWidget {
  const ConnectorCardSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return SkeletonCard(
      margin: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 连接器头部：图标、名称和状态
          Row(
            children: [
              SkeletonBox(
                width: 48,
                height: 48,
                borderRadius: BorderRadius.circular(12),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const SkeletonText(width: 140, height: 18),
                    const SizedBox(height: 4),
                    const SkeletonText(width: 100, height: 14),
                  ],
                ),
              ),
              SkeletonBox(
                width: 80,
                height: 28,
                borderRadius: BorderRadius.circular(14),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // 连接器描述
          SkeletonText.multiLine(
            lines: 2,
            firstLineWidth: double.infinity,
            otherLinesWidth: 200,
          ),
          
          const SizedBox(height: 12),
          
          // 统计信息行
          Row(
            children: [
              _buildStatItem(),
              const SizedBox(width: 24),
              _buildStatItem(),
              const SizedBox(width: 24),
              _buildStatItem(),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // 操作按钮行
          Row(
            children: [
              SkeletonBox(
                width: 80,
                height: 36,
                borderRadius: BorderRadius.circular(18),
              ),
              const SizedBox(width: 8),
              SkeletonBox(
                width: 100,
                height: 36,
                borderRadius: BorderRadius.circular(18),
              ),
              const Spacer(),
              SkeletonBox(
                width: 36,
                height: 36,
                borderRadius: BorderRadius.circular(18),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SkeletonText(width: 40, height: 16),
        const SizedBox(height: 2),
        const SkeletonText(width: 60, height: 12),
      ],
    );
  }
}

/// 连接器状态列表骨架
class ConnectorStatusListSkeleton extends StatelessWidget {
  final int itemCount;

  const ConnectorStatusListSkeleton({
    super.key,
    this.itemCount = 6,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: List.generate(
        itemCount,
        (index) => Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Row(
            children: [
              SkeletonBox(
                width: 16,
                height: 16,
                borderRadius: BorderRadius.circular(8),
              ),
              const SizedBox(width: 8),
              const Expanded(child: SkeletonText(height: 14)),
              SkeletonBox(
                width: 60,
                height: 20,
                borderRadius: BorderRadius.circular(10),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// 连接器管理页面骨架
class ConnectorManagementSkeleton extends StatelessWidget {
  const ConnectorManagementSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 搜索和筛选区域
          Row(
            children: [
              Expanded(
                child: SkeletonBox(
                  height: 48,
                  borderRadius: BorderRadius.circular(24),
                ),
              ),
              const SizedBox(width: 12),
              SkeletonBox(
                width: 48,
                height: 48,
                borderRadius: BorderRadius.circular(24),
              ),
              const SizedBox(width: 8),
              SkeletonBox(
                width: 48,
                height: 48,
                borderRadius: BorderRadius.circular(24),
              ),
            ],
          ),
          
          const SizedBox(height: 20),
          
          // 状态概览卡片
          SkeletonCard(
            height: 120,
            child: Row(
              children: List.generate(4, (index) => 
                Expanded(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      SkeletonBox(
                        width: 32,
                        height: 32,
                        borderRadius: BorderRadius.circular(16),
                      ),
                      const SizedBox(height: 8),
                      const SkeletonText(width: 40, height: 20),
                      const SizedBox(height: 4),
                      const SkeletonText(width: 60, height: 14),
                    ],
                  ),
                ),
              ),
            ),
          ),
          
          const SizedBox(height: 20),
          
          // 连接器列表
          ...List.generate(5, (index) => const ConnectorCardSkeleton()),
        ],
      ),
    );
  }
}

/// 连接器配置表单骨架
class ConnectorConfigFormSkeleton extends StatelessWidget {
  const ConnectorConfigFormSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return SkeletonCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 表单标题
          const SkeletonText(width: 180, height: 20),
          const SizedBox(height: 16),
          
          // 表单字段
          ...List.generate(4, (index) => 
            Padding(
              padding: const EdgeInsets.only(bottom: 20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SkeletonText(width: 100, height: 14),
                  const SizedBox(height: 8),
                  SkeletonBox(
                    height: 48,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  if (index == 1) ...[
                    const SizedBox(height: 4),
                    const SkeletonText(width: 200, height: 12),
                  ],
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 20),
          
          // 按钮区域
          Row(
            children: [
              SkeletonBox(
                width: 80,
                height: 40,
                borderRadius: BorderRadius.circular(8),
              ),
              const SizedBox(width: 12),
              SkeletonBox(
                width: 100,
                height: 40,
                borderRadius: BorderRadius.circular(8),
              ),
              const Spacer(),
              SkeletonBox(
                width: 60,
                height: 40,
                borderRadius: BorderRadius.circular(8),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

/// 系统状态卡片骨架
class SystemStatusCardSkeleton extends StatelessWidget {
  const SystemStatusCardSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return SkeletonCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const SkeletonText(width: 80, height: 16),
              const Spacer(),
              SkeletonBox(
                width: 16,
                height: 16,
                borderRadius: BorderRadius.circular(8),
              ),
            ],
          ),
          const SizedBox(height: 4),
          const SkeletonText(width: 120, height: 12),
          const SizedBox(height: 16),
          
          // 状态列表
          const ConnectorStatusListSkeleton(itemCount: 4),
        ],
      ),
    );
  }
}

/// 快速统计卡片骨架
class QuickStatsCardSkeleton extends StatelessWidget {
  const QuickStatsCardSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return SkeletonCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SkeletonText(width: 80, height: 16),
          const SizedBox(height: 16),
          
          ...List.generate(3, (index) => 
            Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Row(
                children: [
                  SkeletonBox(
                    width: 16,
                    height: 16,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  const SizedBox(width: 8),
                  const Expanded(child: SkeletonText(height: 14)),
                  const SkeletonText(width: 40, height: 14),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}