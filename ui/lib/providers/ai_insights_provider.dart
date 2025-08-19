import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/ai_insight_models.dart';

/// AI洞察数据Provider
final aiInsightsProvider = StateNotifierProvider<AIInsightsNotifier, AIInsightsState>((ref) {
  return AIInsightsNotifier();
});

class AIInsightsState {
  final List<AIInsightCard> insights;
  final TodayOverview overview;
  final List<QuickAccessItem> quickAccess;
  final bool isLoading;
  final String? error;

  const AIInsightsState({
    required this.insights,
    required this.overview,
    required this.quickAccess,
    this.isLoading = false,
    this.error,
  });

  AIInsightsState copyWith({
    List<AIInsightCard>? insights,
    TodayOverview? overview,
    List<QuickAccessItem>? quickAccess,
    bool? isLoading,
    String? error,
  }) {
    return AIInsightsState(
      insights: insights ?? this.insights,
      overview: overview ?? this.overview,
      quickAccess: quickAccess ?? this.quickAccess,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

class AIInsightsNotifier extends StateNotifier<AIInsightsState> {
  AIInsightsNotifier() : super(_initialState()) {
    _loadMockData();
  }

  static AIInsightsState _initialState() {
    return AIInsightsState(
      insights: [],
      overview: TodayOverview(
        newDataPoints: 0,
        aiProcessedItems: 0,
        insightsGenerated: 0,
        activeConnectors: 0,
        lastUpdate: DateTime.now(),
      ),
      quickAccess: [],
      isLoading: true,
    );
  }

  void _loadMockData() {
    // 模拟网络延迟
    Future.delayed(const Duration(seconds: 1), () {
      state = state.copyWith(
        insights: _generateMockInsights(),
        overview: _generateMockOverview(),
        quickAccess: _generateMockQuickAccess(),
        isLoading: false,
      );
    });
  }

  List<AIInsightCard> _generateMockInsights() {
    final now = DateTime.now();
    
    return [
      AIInsightCard(
        id: '1',
        type: 'discovery',
        title: '发现学习模式',
        message: '我注意到你最近在学习Flutter开发，刚才复制的链接是关于Flutter状态管理的教程。这和你上周研究的Riverpod方向很匹配！建议你按照Provider → Riverpod → Bloc的顺序学习。',
        iconName: 'lightbulb',
        timestamp: now.subtract(const Duration(minutes: 5)),
        confidence: 0.92,
        entities: ['Flutter', 'Riverpod', '状态管理'],
        actions: [
          const AIInsightAction(
            id: 'view_tutorial',
            label: '查看教程',
            type: 'primary',
          ),
          const AIInsightAction(
            id: 'save_later',
            label: '稍后阅读',
            type: 'secondary',
          ),
        ],
      ),
      AIInsightCard(
        id: '2',
        type: 'suggestion',
        title: '效率提升建议',
        message: '分析你的工作模式发现，你在上午10-12点效率最高，专注度达到95%。建议把重要的编程任务安排在这个时段。',
        iconName: 'trending_up',
        timestamp: now.subtract(const Duration(hours: 1)),
        confidence: 0.87,
        entities: ['工作效率', '时间管理'],
        actions: [
          const AIInsightAction(
            id: 'set_schedule',
            label: '设置提醒',
            type: 'primary',
          ),
        ],
      ),
      AIInsightCard(
        id: '3',
        type: 'pattern',
        title: '重复内容检测',
        message: '你已经收集了5个关于React Hook的教程链接，其中3个内容重复。我帮你整理了一份去重清单，保留最有价值的资源。',
        iconName: 'filter_list',
        timestamp: now.subtract(const Duration(hours: 3)),
        confidence: 0.95,
        entities: ['React Hook', '教程整理'],
        actions: [
          const AIInsightAction(
            id: 'view_list',
            label: '查看清单',
            type: 'primary',
          ),
          const AIInsightAction(
            id: 'auto_organize',
            label: '自动整理',
            type: 'secondary',
          ),
        ],
      ),
      AIInsightCard(
        id: '4',
        type: 'alert',
        title: '重要信息提醒',
        message: '刚才复制的邮箱地址似乎是工作相关的重要联系人，建议添加到通讯录并设置备注。',
        iconName: 'priority_high',
        timestamp: now.subtract(const Duration(minutes: 30)),
        confidence: 0.78,
        entities: ['邮箱', '联系人'],
        actions: [
          const AIInsightAction(
            id: 'add_contact',
            label: '添加联系人',
            type: 'primary',
          ),
        ],
      ),
    ];
  }

  TodayOverview _generateMockOverview() {
    return TodayOverview(
      newDataPoints: 127,
      aiProcessedItems: 89,
      insightsGenerated: 12,
      activeConnectors: 3,
      lastUpdate: DateTime.now().subtract(const Duration(minutes: 2)),
    );
  }

  List<QuickAccessItem> _generateMockQuickAccess() {
    final now = DateTime.now();
    
    return [
      QuickAccessItem(
        id: '1',
        title: 'Flutter官方文档',
        subtitle: 'docs.flutter.dev',
        iconName: 'description',
        type: 'url',
        lastAccessed: now.subtract(const Duration(hours: 2)),
        data: 'https://docs.flutter.dev',
      ),
      QuickAccessItem(
        id: '2',
        title: 'main.dart',
        subtitle: '/Users/project/lib/',
        iconName: 'code',
        type: 'file',
        lastAccessed: now.subtract(const Duration(minutes: 45)),
        data: '/Users/project/lib/main.dart',
      ),
      QuickAccessItem(
        id: '3',
        title: 'John Smith',
        subtitle: 'john@example.com',
        iconName: 'person',
        type: 'contact',
        lastAccessed: now.subtract(const Duration(hours: 1)),
        data: 'john@example.com',
      ),
      QuickAccessItem(
        id: '4',
        title: '学习笔记',
        subtitle: 'Riverpod状态管理',
        iconName: 'note',
        type: 'note',
        lastAccessed: now.subtract(const Duration(hours: 3)),
        data: 'Riverpod学习要点...',
      ),
    ];
  }

  void dismissInsight(String insightId) {
    state = state.copyWith(
      insights: state.insights.map((insight) {
        if (insight.id == insightId) {
          return insight.copyWith(isDismissed: true);
        }
        return insight;
      }).where((insight) => !insight.isDismissed).toList(),
    );
  }

  void markInsightAsRead(String insightId) {
    state = state.copyWith(
      insights: state.insights.map((insight) {
        if (insight.id == insightId) {
          return insight.copyWith(isRead: true);
        }
        return insight;
      }).toList(),
    );
  }

  void refreshData() {
    state = state.copyWith(isLoading: true);
    _loadMockData();
  }
}