import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/ai_chat_provider.dart';
import '../widgets/ai_chat/ai_chat_message_widget.dart';
import '../widgets/ai_chat/ai_recommendation_widget.dart';
import '../widgets/ai_chat/ai_chat_input_widget.dart';
import '../widgets/sidebar/smart_sidebar_panel.dart';
import '../utils/responsive_utils.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final aiChatState = ref.watch(aiChatProvider);

    if (aiChatState.isLoading) {
      return Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const CircularProgressIndicator(),
              const SizedBox(height: 16),
              Text(
                'AI正在准备中...',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
        ),
      );
    }

    if (aiChatState.error != null) {
      return Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.psychology_alt,
                size: 64,
                color: Theme.of(context).colorScheme.error,
              ),
              const SizedBox(height: 16),
              Text(
                'AI助手暂时不可用',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 8),
              Text(
                aiChatState.error!,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () => ref.read(aiChatProvider.notifier).refreshChat(),
                child: const Text('重新连接'),
              ),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      body: ResponsiveWrapper(
        mobile: _buildMobileLayout(context, ref, aiChatState),
        tablet: _buildTabletLayout(context, ref, aiChatState),
        desktop: _buildDesktopLayout(context, ref, aiChatState),
      ),
    );
  }

  // 移动端布局
  Widget _buildMobileLayout(BuildContext context, WidgetRef ref, aiChatState) {
    return Column(
      children: [
        Expanded(
          child: _buildChatArea(context, ref, aiChatState),
        ),
        _buildInputArea(context, ref, aiChatState),
      ],
    );
  }

  // 平板布局
  Widget _buildTabletLayout(BuildContext context, WidgetRef ref, aiChatState) {
    return Row(
      children: [
        // 主聊天区域
        Expanded(
          flex: 3,
          child: Column(
            children: [
              Expanded(
                child: _buildChatArea(context, ref, aiChatState),
              ),
              _buildInputArea(context, ref, aiChatState),
            ],
          ),
        ),
        // AI智能洞察面板（可选）
        if (ResponsiveUtils.shouldShowSidebar(context))
          Container(
            width: 300,
            decoration: BoxDecoration(
              border: Border(
                left: BorderSide(
                  color: Theme.of(context).colorScheme.outline.withValues(alpha: 0.2),
                ),
              ),
            ),
            child: SmartSidebarPanel(
              onPromptTap: (prompt) => _handleInsightPromptTap(context, ref, prompt),
            ),
          ),
      ],
    );
  }

  // 桌面端布局
  Widget _buildDesktopLayout(BuildContext context, WidgetRef ref, aiChatState) {
    return Row(
      children: [
        // 主聊天区域
        Expanded(
          child: Center(
            child: Container(
              constraints: ResponsiveUtils.getChatConstraints(context),
              child: Column(
                children: [
                  Expanded(
                    child: _buildChatArea(context, ref, aiChatState),
                  ),
                  _buildInputArea(context, ref, aiChatState),
                ],
              ),
            ),
          ),
        ),
        // 桌面端AI洞察面板
        Container(
          width: 350, // 固定宽度侧边栏
          decoration: BoxDecoration(
            border: Border(
              left: BorderSide(
                color: Theme.of(context).colorScheme.outline.withValues(alpha: 0.2),
              ),
            ),
          ),
          child: SmartSidebarPanel(
            onPromptTap: (prompt) => _handleInsightPromptTap(context, ref, prompt),
          ),
        ),
      ],
    );
  }

  // 聊天区域
  Widget _buildChatArea(BuildContext context, WidgetRef ref, aiChatState) {
    return RefreshIndicator(
      onRefresh: () async {
        ref.read(aiChatProvider.notifier).refreshChat();
        await Future.delayed(const Duration(milliseconds: 500));
      },
      child: CustomScrollView(
        slivers: [
          const SliverToBoxAdapter(
            child: SizedBox(height: 16),
          ),
          SliverList(
            delegate: SliverChildBuilderDelegate(
              (context, index) {
                final message = aiChatState.messages[index];
                return AIChatMessageWidget(
                  message: message,
                  onActionTap: (action) => ref
                      .read(aiChatProvider.notifier)
                      .handleActionTap(action),
                  onTap: () => _handleMessageTap(context, message),
                );
              },
              childCount: aiChatState.messages.length,
            ),
          ),
          if (aiChatState.recommendations.isNotEmpty)
            SliverToBoxAdapter(
              child: AIRecommendationWidget(
                recommendations: aiChatState.recommendations,
                onRecommendationTap: (recommendation) => ref
                    .read(aiChatProvider.notifier)
                    .handleRecommendationTap(recommendation),
              ),
            ),
          if (aiChatState.isAITyping)
            SliverToBoxAdapter(
              child: _buildTypingIndicator(context),
            ),
          const SliverToBoxAdapter(
            child: SizedBox(height: 120),
          ),
        ],
      ),
    );
  }

  // 输入区域
  Widget _buildInputArea(BuildContext context, WidgetRef ref, aiChatState) {
    return AIChatInputWidget(
      onSendMessage: (message) => ref
          .read(aiChatProvider.notifier)
          .sendMessage(message),
      onVoiceInput: (text) => _handleVoiceInput(context, text),
      onSearchTap: () => _handleSearchTap(context),
      isEnabled: !aiChatState.isAITyping,
    );
  }

  // 处理洞察面板提示词点击
  void _handleInsightPromptTap(BuildContext context, WidgetRef ref, String prompt) {
    // 将提示词发送给AI聊天
    ref.read(aiChatProvider.notifier).sendMessage(prompt);
  }

  Widget _buildTypingIndicator(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: theme.colorScheme.primaryContainer,
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.psychology,
              size: 20,
              color: theme.colorScheme.onPrimaryContainer,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: theme.colorScheme.surfaceContainerHighest,
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(16),
                  topRight: Radius.circular(16),
                  bottomLeft: Radius.circular(4),
                  bottomRight: Radius.circular(16),
                ),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation(
                        theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'AI正在思考...',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _handleMessageTap(BuildContext context, message) {
    // 可以显示消息详情或执行特定操作
  }

  void _handleVoiceInput(BuildContext context, String text) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('语音输入: $text'),
        duration: const Duration(seconds: 2),
      ),
    );
  }

  void _handleSearchTap(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('打开搜索功能'),
        duration: Duration(seconds: 2),
      ),
    );
  }
}
