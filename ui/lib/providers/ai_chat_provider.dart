import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/ai_chat_models.dart';

/// AI聊天状态
class AIChatState {
  final List<AIChatMessage> messages;
  final List<AIRecommendation> recommendations;
  final bool isLoading;
  final bool isAITyping;
  final String? error;

  const AIChatState({
    required this.messages,
    required this.recommendations,
    this.isLoading = false,
    this.isAITyping = false,
    this.error,
  });

  AIChatState copyWith({
    List<AIChatMessage>? messages,
    List<AIRecommendation>? recommendations,
    bool? isLoading,
    bool? isAITyping,
    String? error,
  }) {
    return AIChatState(
      messages: messages ?? this.messages,
      recommendations: recommendations ?? this.recommendations,
      isLoading: isLoading ?? this.isLoading,
      isAITyping: isAITyping ?? this.isAITyping,
      error: error ?? this.error,
    );
  }
}

/// AI聊天Provider
final aiChatProvider = StateNotifierProvider<AIChatNotifier, AIChatState>((ref) {
  return AIChatNotifier();
});

class AIChatNotifier extends StateNotifier<AIChatState> {
  AIChatNotifier() : super(_initialState()) {
    _initializeChat();
  }

  static AIChatState _initialState() {
    return const AIChatState(
      messages: [],
      recommendations: [],
      isLoading: true,
    );
  }

  void _initializeChat() {
    // 模拟初始化延迟
    Future.delayed(const Duration(milliseconds: 800), () {
      state = state.copyWith(
        messages: _generateInitialMessages(),
        recommendations: _generateMockRecommendations(),
        isLoading: false,
      );
    });
  }

  List<AIChatMessage> _generateInitialMessages() {
    final now = DateTime.now();
    final hour = now.hour;
    
    String greeting;
    if (hour < 12) {
      greeting = '🌅 早上好！';
    } else if (hour < 18) {
      greeting = '🌞 下午好！';
    } else {
      greeting = '🌙 晚上好！';
    }

    return [
      AIChatMessage(
        id: 'greeting_1',
        content: greeting,
        type: MessageType.aiGreeting,
        timestamp: now.subtract(const Duration(seconds: 10)),
      ),
      AIChatMessage(
        id: 'insight_1',
        content: '我发现你最近在学习Flutter开发，今天为你准备了一些有价值的资源。另外，我注意到你的工作效率在上午最高，建议重要的编程任务可以安排在这个时段。',
        type: MessageType.aiInsight,
        timestamp: now.subtract(const Duration(seconds: 5)),
        actions: [
          const MessageAction(
            id: 'view_resources',
            label: '查看资源',
            type: ActionType.viewDetail,
          ),
          const MessageAction(
            id: 'set_reminder',
            label: '设置提醒',
            type: ActionType.quickReply,
          ),
          const MessageAction(
            id: 'not_now',
            label: '稍后再说',
            type: ActionType.dismiss,
          ),
        ],
      ),
      AIChatMessage(
        id: 'question_1',
        content: '需要我帮你找什么吗？比如搜索最近复制的内容，或者分析你的学习进度？',
        type: MessageType.aiQuestion,
        timestamp: now.subtract(const Duration(seconds: 2)),
        actions: [
          const MessageAction(
            id: 'search_recent',
            label: '搜索最近内容',
            type: ActionType.quickReply,
          ),
          const MessageAction(
            id: 'analyze_progress',
            label: '分析学习进度',
            type: ActionType.quickReply,
          ),
          const MessageAction(
            id: 'show_insights',
            label: '显示更多洞察',
            type: ActionType.quickReply,
          ),
        ],
      ),
    ];
  }

  List<AIRecommendation> _generateMockRecommendations() {
    return [
      const AIRecommendation(
        id: 'rec_1',
        title: 'Flutter文档',
        description: 'docs.flutter.dev',
        iconName: 'description',
        type: RecommendationType.quickAccess,
        confidence: 0.95,
      ),
      const AIRecommendation(
        id: 'rec_2',
        title: 'main.dart',
        description: 'lib/main.dart',
        iconName: 'code',
        type: RecommendationType.recentItem,
        confidence: 0.88,
      ),
      const AIRecommendation(
        id: 'rec_3',
        title: 'Riverpod教程',
        description: 'riverpod.dev/docs',
        iconName: 'school',
        type: RecommendationType.learningResource,
        confidence: 0.82,
      ),
      const AIRecommendation(
        id: 'rec_4',
        title: 'VS Code',
        description: '打开项目',
        iconName: 'build',
        type: RecommendationType.productivityTool,
        confidence: 0.76,
      ),
    ];
  }

  void sendMessage(String content) {
    if (content.trim().isEmpty) return;

    final userMessage = AIChatMessage(
      id: 'user_${DateTime.now().millisecondsSinceEpoch}',
      content: content,
      type: MessageType.userRequest,
      timestamp: DateTime.now(),
    );

    // 添加用户消息
    state = state.copyWith(
      messages: [...state.messages, userMessage],
      isAITyping: true,
    );

    // 模拟AI回复
    _simulateAIResponse(content);
  }

  void _simulateAIResponse(String userInput) {
    // 模拟思考时间
    Future.delayed(const Duration(seconds: 1, milliseconds: 500), () {
      final aiResponse = _generateAIResponse(userInput);
      
      state = state.copyWith(
        messages: [...state.messages, aiResponse],
        isAITyping: false,
      );
    });
  }

  AIChatMessage _generateAIResponse(String userInput) {
    final lower = userInput.toLowerCase();
    String response;
    MessageType type = MessageType.aiGreeting;
    List<MessageAction> actions = [];

    if (lower.contains('搜索') || lower.contains('找')) {
      response = '好的！我来帮你搜索最近的内容。根据你的活动记录，我找到了3个相关项目：一个Flutter教程链接、两个代码文件路径，还有一个GitHub仓库。需要我展示详细信息吗？';
      type = MessageType.aiInsight;
      actions = [
        const MessageAction(
          id: 'show_results',
          label: '显示搜索结果',
          type: ActionType.viewDetail,
        ),
        const MessageAction(
          id: 'refine_search',
          label: '细化搜索',
          type: ActionType.quickReply,
        ),
      ];
    } else if (lower.contains('分析') || lower.contains('进度')) {
      response = '通过分析你的学习数据，我发现你在Flutter状态管理方面进步很快！已经掌握了Provider的基础用法，建议接下来学习Riverpod的高级特性。要我为你制定一个学习计划吗？';
      type = MessageType.aiInsight;
      actions = [
        const MessageAction(
          id: 'create_plan',
          label: '制定学习计划',
          type: ActionType.quickReply,
        ),
        const MessageAction(
          id: 'show_progress',
          label: '查看详细进度',
          type: ActionType.viewDetail,
        ),
      ];
    } else if (lower.contains('洞察') || lower.contains('建议')) {
      response = '基于你最近的活动，我有几个建议：1) 你经常在下午访问同一个文档，可以添加到快捷访问；2) 建议整理一下重复的学习资源；3) 你的编程效率在上午最高，重要任务可以安排在那个时段。';
      type = MessageType.aiRecommendation;
      actions = [
        const MessageAction(
          id: 'add_shortcuts',
          label: '添加快捷访问',
          type: ActionType.quickReply,
        ),
        const MessageAction(
          id: 'organize_resources',
          label: '整理资源',
          type: ActionType.quickReply,
        ),
      ];
    } else {
      response = '我理解了！让我想想如何更好地帮助你。你可以试试问我一些具体的问题，比如搜索某个内容、分析数据模式，或者让我给出一些效率建议。';
      actions = [
        const MessageAction(
          id: 'help_search',
          label: '帮我搜索',
          type: ActionType.quickReply,
        ),
        const MessageAction(
          id: 'help_analyze',
          label: '分析数据',
          type: ActionType.quickReply,
        ),
        const MessageAction(
          id: 'help_suggest',
          label: '给出建议',
          type: ActionType.quickReply,
        ),
      ];
    }

    return AIChatMessage(
      id: 'ai_${DateTime.now().millisecondsSinceEpoch}',
      content: response,
      type: type,
      timestamp: DateTime.now(),
      actions: actions,
    );
  }

  void handleActionTap(MessageAction action) {
    switch (action.type) {
      case ActionType.quickReply:
        sendMessage(action.label);
        break;
      case ActionType.viewDetail:
        // TODO: 处理查看详情
        break;
      case ActionType.dismiss:
        // TODO: 处理忽略
        break;
      default:
        break;
    }
  }

  void handleRecommendationTap(AIRecommendation recommendation) {
    final message = '我想了解更多关于"${recommendation.title}"的信息';
    sendMessage(message);
  }

  void refreshChat() {
    state = state.copyWith(isLoading: true);
    _initializeChat();
  }
}