import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// AI聊天输入框组件
class AIChatInputWidget extends ConsumerStatefulWidget {
  final Function(String)? onSendMessage;
  final Function(String)? onVoiceInput;
  final VoidCallback? onSearchTap;
  final bool isEnabled;

  const AIChatInputWidget({
    super.key,
    this.onSendMessage,
    this.onVoiceInput,
    this.onSearchTap,
    this.isEnabled = true,
  });

  @override
  ConsumerState<AIChatInputWidget> createState() => _AIChatInputWidgetState();
}

class _AIChatInputWidgetState extends ConsumerState<AIChatInputWidget> {
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focusNode = FocusNode();
  bool _isComposing = false;

  @override
  void initState() {
    super.initState();
    _controller.addListener(_handleTextChanged);
  }

  @override
  void dispose() {
    _controller.removeListener(_handleTextChanged);
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _handleTextChanged() {
    setState(() {
      _isComposing = _controller.text.trim().isNotEmpty;
    });
  }

  void _handleSubmitted() {
    final text = _controller.text.trim();
    if (text.isNotEmpty && widget.isEnabled) {
      widget.onSendMessage?.call(text);
      _controller.clear();
      setState(() {
        _isComposing = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        border: Border(
          top: BorderSide(
            color: theme.colorScheme.outline.withValues(alpha: 0.2),
          ),
        ),
      ),
      child: SafeArea(
        top: false,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildQuickSuggestions(context, theme),
            const SizedBox(height: 8),
            _buildInputRow(context, theme),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickSuggestions(BuildContext context, ThemeData theme) {
    final suggestions = [
      '🔍 搜索最近的内容',
      '📊 查看今天的数据分析',
      '💡 给我一些建议',
      '🔗 找找昨天的链接',
    ];

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: suggestions.map((suggestion) => 
          _SuggestionChip(
            text: suggestion,
            onTap: () => _handleSuggestionTap(suggestion),
          ),
        ).toList(),
      ),
    );
  }

  Widget _buildInputRow(BuildContext context, ThemeData theme) {
    return Row(
      children: [
        // 搜索按钮
        IconButton(
          onPressed: widget.isEnabled ? widget.onSearchTap : null,
          icon: Icon(
            Icons.search,
            color: widget.isEnabled 
                ? theme.colorScheme.onSurfaceVariant 
                : theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.5),
          ),
          tooltip: '搜索',
        ),
        
        // 输入框
        Expanded(
          child: Container(
            decoration: BoxDecoration(
              color: theme.colorScheme.surfaceContainerHighest,
              borderRadius: BorderRadius.circular(24),
            ),
            child: TextField(
              controller: _controller,
              focusNode: _focusNode,
              enabled: widget.isEnabled,
              maxLines: null,
              textCapitalization: TextCapitalization.sentences,
              decoration: InputDecoration(
                hintText: widget.isEnabled ? '和AI聊聊，或者问问题...' : 'AI暂时不可用',
                hintStyle: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.6),
                ),
                border: InputBorder.none,
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
              ),
              onSubmitted: widget.isEnabled ? (_) => _handleSubmitted() : null,
            ),
          ),
        ),
        
        const SizedBox(width: 8),
        
        // 语音/发送按钮
        _isComposing
            ? IconButton(
                onPressed: widget.isEnabled ? _handleSubmitted : null,
                icon: Icon(
                  Icons.send,
                  color: widget.isEnabled 
                      ? theme.colorScheme.primary 
                      : theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.5),
                ),
                tooltip: '发送',
              )
            : IconButton(
                onPressed: widget.isEnabled ? _handleVoiceInput : null,
                icon: Icon(
                  Icons.mic,
                  color: widget.isEnabled 
                      ? theme.colorScheme.onSurfaceVariant 
                      : theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.5),
                ),
                tooltip: '语音输入',
              ),
      ],
    );
  }

  void _handleSuggestionTap(String suggestion) {
    if (!widget.isEnabled) return;
    
    // 移除emoji，提取实际内容
    final cleanText = suggestion.replaceAll(RegExp(r'[^\w\s\u4e00-\u9fa5]'), '').trim();
    widget.onSendMessage?.call(cleanText);
  }

  void _handleVoiceInput() {
    // TODO: 实现语音输入
    widget.onVoiceInput?.call('语音输入功能待实现');
  }
}

/// 建议芯片
class _SuggestionChip extends StatelessWidget {
  final String text;
  final VoidCallback? onTap;

  const _SuggestionChip({
    required this.text,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: theme.colorScheme.primaryContainer.withValues(alpha: 0.5),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: theme.colorScheme.outline.withValues(alpha: 0.3),
            ),
          ),
          child: Text(
            text,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
        ),
      ),
    );
  }
}