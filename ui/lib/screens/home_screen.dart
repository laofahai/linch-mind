import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/app_providers.dart';
import '../widgets/recommendation_card.dart';
import '../widgets/stats_card.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final serverInfoAsync = ref.watch(serverInfoProvider);
    final recommendationsAsync = ref.watch(recommendationsProvider(5));
    final databaseStatsAsync = ref.watch(databaseStatsProvider);

    return RefreshIndicator(
      onRefresh: () async {
        // 刷新所有数据
        // ignore: unused_result
        ref.refresh(serverInfoProvider);
        // ignore: unused_result
        ref.refresh(recommendationsProvider(5));
        // ignore: unused_result
        ref.refresh(databaseStatsProvider);
      },
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 服务器状态卡片
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Server Status',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 8),
                    serverInfoAsync.when(
                      data: (serverInfo) => Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Version: ${serverInfo.version}'),
                          Text('Port: ${serverInfo.port}'),
                          Text('Started: ${_formatDateTime(serverInfo.startedAt)}'),
                          Text('Status: ${serverInfo.status}'),
                        ],
                      ),
                      loading: () => const Center(child: CircularProgressIndicator()),
                      error: (error, _) => Text(
                        'Failed to connect to server: $error',
                        style: TextStyle(color: Theme.of(context).colorScheme.error),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // 数据库统计
            databaseStatsAsync.when(
              data: (stats) => Row(
                children: [
                  Expanded(
                    child: StatsCard(
                      title: 'Total Items',
                      value: stats.totalItems.toString(),
                      icon: Icons.storage,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: StatsCard(
                      title: 'Connectors',
                      value: stats.connectorCount.toString(),
                      icon: Icons.cable,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: StatsCard(
                      title: 'Graph Nodes',
                      value: stats.graphNodes.toString(),
                      icon: Icons.account_tree,
                    ),
                  ),
                ],
              ),
              loading: () => const Row(
                children: [
                  Expanded(child: StatsCard.loading()),
                  SizedBox(width: 8),
                  Expanded(child: StatsCard.loading()),
                  SizedBox(width: 8),
                  Expanded(child: StatsCard.loading()),
                ],
              ),
              error: (error, _) => Text('Error loading stats: $error'),
            ),
            const SizedBox(height: 24),

            // AI 推荐区域
            Text(
              '🤖 AI Recommendations',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 16),
            recommendationsAsync.when(
              data: (recommendations) {
                if (recommendations.isEmpty) {
                  return Card(
                    child: Padding(
                      padding: const EdgeInsets.all(24.0),
                      child: Column(
                        children: [
                          Icon(
                            Icons.lightbulb_outline,
                            size: 48,
                            color: Theme.of(context).colorScheme.primary,
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'No recommendations yet',
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Start collecting data to get AI-powered insights and recommendations.',
                            textAlign: TextAlign.center,
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                          const SizedBox(height: 16),
                          FilledButton(
                            onPressed: () => context.go('/connectors'),
                            child: const Text('Set up Connectors'),
                          ),
                        ],
                      ),
                    ),
                  );
                }

                return Column(
                  children: recommendations
                      .map((recommendation) => Padding(
                            padding: const EdgeInsets.only(bottom: 12.0),
                            child: RecommendationCard(recommendation: recommendation),
                          ))
                      .toList(),
                );
              },
              loading: () => Column(
                children: List.generate(
                  3,
                  (index) => Padding(
                    padding: const EdgeInsets.only(bottom: 12.0),
                    child: RecommendationCard.loading(),
                  ),
                ),
              ),
              error: (error, _) => Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      Icon(
                        Icons.error_outline,
                        color: Theme.of(context).colorScheme.error,
                      ),
                      const SizedBox(height: 8),
                      Text('Error loading recommendations: $error'),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.day}/${dateTime.month}/${dateTime.year} ${dateTime.hour}:${dateTime.minute.toString().padLeft(2, '0')}';
  }
}