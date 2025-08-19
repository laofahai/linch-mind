// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ai_insight_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$AIInsightCardImpl _$$AIInsightCardImplFromJson(Map<String, dynamic> json) =>
    _$AIInsightCardImpl(
      id: json['id'] as String,
      type: json['type'] as String,
      title: json['title'] as String,
      message: json['message'] as String,
      iconName: json['iconName'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.8,
      entities: (json['entities'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      actions: (json['actions'] as List<dynamic>?)
              ?.map((e) => AIInsightAction.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      isDismissed: json['isDismissed'] as bool? ?? false,
      isRead: json['isRead'] as bool? ?? false,
    );

Map<String, dynamic> _$$AIInsightCardImplToJson(_$AIInsightCardImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'type': instance.type,
      'title': instance.title,
      'message': instance.message,
      'iconName': instance.iconName,
      'timestamp': instance.timestamp.toIso8601String(),
      'confidence': instance.confidence,
      'entities': instance.entities,
      'actions': instance.actions,
      'isDismissed': instance.isDismissed,
      'isRead': instance.isRead,
    };

_$AIInsightActionImpl _$$AIInsightActionImplFromJson(
        Map<String, dynamic> json) =>
    _$AIInsightActionImpl(
      id: json['id'] as String,
      label: json['label'] as String,
      type: json['type'] as String,
      route: json['route'] as String?,
      data: json['data'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$AIInsightActionImplToJson(
        _$AIInsightActionImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'label': instance.label,
      'type': instance.type,
      'route': instance.route,
      'data': instance.data,
    };

_$TodayOverviewImpl _$$TodayOverviewImplFromJson(Map<String, dynamic> json) =>
    _$TodayOverviewImpl(
      newDataPoints: (json['newDataPoints'] as num).toInt(),
      aiProcessedItems: (json['aiProcessedItems'] as num).toInt(),
      insightsGenerated: (json['insightsGenerated'] as num).toInt(),
      activeConnectors: (json['activeConnectors'] as num).toInt(),
      lastUpdate: DateTime.parse(json['lastUpdate'] as String),
    );

Map<String, dynamic> _$$TodayOverviewImplToJson(_$TodayOverviewImpl instance) =>
    <String, dynamic>{
      'newDataPoints': instance.newDataPoints,
      'aiProcessedItems': instance.aiProcessedItems,
      'insightsGenerated': instance.insightsGenerated,
      'activeConnectors': instance.activeConnectors,
      'lastUpdate': instance.lastUpdate.toIso8601String(),
    };

_$QuickAccessItemImpl _$$QuickAccessItemImplFromJson(
        Map<String, dynamic> json) =>
    _$QuickAccessItemImpl(
      id: json['id'] as String,
      title: json['title'] as String,
      subtitle: json['subtitle'] as String,
      iconName: json['iconName'] as String,
      type: json['type'] as String,
      lastAccessed: DateTime.parse(json['lastAccessed'] as String),
      data: json['data'] as String?,
    );

Map<String, dynamic> _$$QuickAccessItemImplToJson(
        _$QuickAccessItemImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'title': instance.title,
      'subtitle': instance.subtitle,
      'iconName': instance.iconName,
      'type': instance.type,
      'lastAccessed': instance.lastAccessed.toIso8601String(),
      'data': instance.data,
    };
