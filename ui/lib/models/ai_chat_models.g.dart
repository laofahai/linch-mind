// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ai_chat_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$AIChatMessageImpl _$$AIChatMessageImplFromJson(Map<String, dynamic> json) =>
    _$AIChatMessageImpl(
      id: json['id'] as String,
      content: json['content'] as String,
      type: $enumDecode(_$MessageTypeEnumMap, json['type']),
      timestamp: DateTime.parse(json['timestamp'] as String),
      actions: (json['actions'] as List<dynamic>?)
              ?.map((e) => MessageAction.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      status: $enumDecodeNullable(_$MessageStatusEnumMap, json['status']) ??
          MessageStatus.sent,
      metadata: json['metadata'] as Map<String, dynamic>?,
      replyToId: json['replyToId'] as String?,
    );

Map<String, dynamic> _$$AIChatMessageImplToJson(_$AIChatMessageImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'content': instance.content,
      'type': _$MessageTypeEnumMap[instance.type]!,
      'timestamp': instance.timestamp.toIso8601String(),
      'actions': instance.actions,
      'status': _$MessageStatusEnumMap[instance.status]!,
      'metadata': instance.metadata,
      'replyToId': instance.replyToId,
    };

const _$MessageTypeEnumMap = {
  MessageType.aiGreeting: 'ai_greeting',
  MessageType.aiInsight: 'ai_insight',
  MessageType.aiRecommendation: 'ai_recommendation',
  MessageType.aiQuestion: 'ai_question',
  MessageType.userReply: 'user_reply',
  MessageType.userRequest: 'user_request',
  MessageType.systemUpdate: 'system_update',
};

const _$MessageStatusEnumMap = {
  MessageStatus.sending: 'sending',
  MessageStatus.sent: 'sent',
  MessageStatus.delivered: 'delivered',
  MessageStatus.read: 'read',
  MessageStatus.error: 'error',
};

_$MessageActionImpl _$$MessageActionImplFromJson(Map<String, dynamic> json) =>
    _$MessageActionImpl(
      id: json['id'] as String,
      label: json['label'] as String,
      type: $enumDecode(_$ActionTypeEnumMap, json['type']),
      payload: json['payload'] as String?,
      data: json['data'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$MessageActionImplToJson(_$MessageActionImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'label': instance.label,
      'type': _$ActionTypeEnumMap[instance.type]!,
      'payload': instance.payload,
      'data': instance.data,
    };

const _$ActionTypeEnumMap = {
  ActionType.quickReply: 'quick_reply',
  ActionType.openLink: 'open_link',
  ActionType.viewDetail: 'view_detail',
  ActionType.dismiss: 'dismiss',
  ActionType.save: 'save',
  ActionType.search: 'search',
};

_$AIRecommendationImpl _$$AIRecommendationImplFromJson(
        Map<String, dynamic> json) =>
    _$AIRecommendationImpl(
      id: json['id'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      iconName: json['iconName'] as String,
      type: $enumDecode(_$RecommendationTypeEnumMap, json['type']),
      confidence: (json['confidence'] as num).toDouble(),
      action: json['action'] as String?,
      data: json['data'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$AIRecommendationImplToJson(
        _$AIRecommendationImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'title': instance.title,
      'description': instance.description,
      'iconName': instance.iconName,
      'type': _$RecommendationTypeEnumMap[instance.type]!,
      'confidence': instance.confidence,
      'action': instance.action,
      'data': instance.data,
    };

const _$RecommendationTypeEnumMap = {
  RecommendationType.quickAccess: 'quick_access',
  RecommendationType.learningResource: 'learning_resource',
  RecommendationType.productivityTool: 'productivity_tool',
  RecommendationType.recentItem: 'recent_item',
};
