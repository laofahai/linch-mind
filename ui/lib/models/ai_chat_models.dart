import 'package:freezed_annotation/freezed_annotation.dart';

part 'ai_chat_models.freezed.dart';
part 'ai_chat_models.g.dart';

/// AI聊天消息
@freezed
class AIChatMessage with _$AIChatMessage {
  const factory AIChatMessage({
    required String id,
    required String content,
    required MessageType type,
    required DateTime timestamp,
    @Default([]) List<MessageAction> actions,
    @Default(MessageStatus.sent) MessageStatus status,
    Map<String, dynamic>? metadata,
    String? replyToId,
  }) = _AIChatMessage;

  factory AIChatMessage.fromJson(Map<String, dynamic> json) =>
      _$AIChatMessageFromJson(json);
}

/// 消息类型
enum MessageType {
  @JsonValue('ai_greeting')
  aiGreeting,           // AI问候
  
  @JsonValue('ai_insight')
  aiInsight,           // AI洞察发现
  
  @JsonValue('ai_recommendation')
  aiRecommendation,    // AI推荐
  
  @JsonValue('ai_question')
  aiQuestion,          // AI询问
  
  @JsonValue('user_reply')
  userReply,           // 用户回复
  
  @JsonValue('user_request')
  userRequest,         // 用户请求
  
  @JsonValue('system_update')
  systemUpdate,        // 系统更新
}

/// 消息状态
enum MessageStatus {
  @JsonValue('sending')
  sending,
  
  @JsonValue('sent')
  sent,
  
  @JsonValue('delivered')
  delivered,
  
  @JsonValue('read')
  read,
  
  @JsonValue('error')
  error,
}

/// 消息操作按钮
@freezed
class MessageAction with _$MessageAction {
  const factory MessageAction({
    required String id,
    required String label,
    required ActionType type,
    String? payload,
    Map<String, dynamic>? data,
  }) = _MessageAction;

  factory MessageAction.fromJson(Map<String, dynamic> json) =>
      _$MessageActionFromJson(json);
}

/// 操作类型
enum ActionType {
  @JsonValue('quick_reply')
  quickReply,          // 快速回复
  
  @JsonValue('open_link')
  openLink,            // 打开链接
  
  @JsonValue('view_detail')
  viewDetail,          // 查看详情
  
  @JsonValue('dismiss')
  dismiss,             // 忽略
  
  @JsonValue('save')
  save,                // 保存
  
  @JsonValue('search')
  search,              // 搜索
}

/// AI智能推荐项
@freezed
class AIRecommendation with _$AIRecommendation {
  const factory AIRecommendation({
    required String id,
    required String title,
    required String description,
    required String iconName,
    required RecommendationType type,
    required double confidence,
    String? action,
    Map<String, dynamic>? data,
  }) = _AIRecommendation;

  factory AIRecommendation.fromJson(Map<String, dynamic> json) =>
      _$AIRecommendationFromJson(json);
}

/// 推荐类型
enum RecommendationType {
  @JsonValue('quick_access')
  quickAccess,         // 快速访问
  
  @JsonValue('learning_resource')
  learningResource,    // 学习资源
  
  @JsonValue('productivity_tool')
  productivityTool,    // 效率工具
  
  @JsonValue('recent_item')
  recentItem,          // 最近项目
}