// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ai_insights_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$AIInsightImpl _$$AIInsightImplFromJson(Map<String, dynamic> json) =>
    _$AIInsightImpl(
      id: json['id'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      timeframe: $enumDecode(_$InsightTimeframeEnumMap, json['timeframe']),
      type: $enumDecode(_$InsightTypeEnumMap, json['type']),
      confidence: (json['confidence'] as num).toDouble(),
      timestamp: DateTime.parse(json['timestamp'] as String),
      actions: (json['actions'] as List<dynamic>?)
              ?.map((e) => InsightAction.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      metadata: json['metadata'] as Map<String, dynamic>?,
      iconName: json['iconName'] as String?,
      isImportant: json['isImportant'] as bool? ?? false,
      isDismissed: json['isDismissed'] as bool? ?? false,
    );

Map<String, dynamic> _$$AIInsightImplToJson(_$AIInsightImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'title': instance.title,
      'description': instance.description,
      'timeframe': _$InsightTimeframeEnumMap[instance.timeframe]!,
      'type': _$InsightTypeEnumMap[instance.type]!,
      'confidence': instance.confidence,
      'timestamp': instance.timestamp.toIso8601String(),
      'actions': instance.actions,
      'metadata': instance.metadata,
      'iconName': instance.iconName,
      'isImportant': instance.isImportant,
      'isDismissed': instance.isDismissed,
    };

const _$InsightTimeframeEnumMap = {
  InsightTimeframe.realtime: 'realtime',
  InsightTimeframe.session: 'session',
  InsightTimeframe.daily: 'daily',
  InsightTimeframe.weekly: 'weekly',
  InsightTimeframe.trend: 'trend',
  InsightTimeframe.prediction: 'prediction',
};

const _$InsightTypeEnumMap = {
  InsightType.activity: 'activity',
  InsightType.pattern: 'pattern',
  InsightType.performance: 'performance',
  InsightType.learning: 'learning',
  InsightType.suggestion: 'suggestion',
  InsightType.trend: 'trend',
};

_$InsightActionImpl _$$InsightActionImplFromJson(Map<String, dynamic> json) =>
    _$InsightActionImpl(
      id: json['id'] as String,
      label: json['label'] as String,
      prompt: json['prompt'] as String,
      iconName: json['iconName'] as String?,
      isPrimary: json['isPrimary'] as bool? ?? false,
    );

Map<String, dynamic> _$$InsightActionImplToJson(_$InsightActionImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'label': instance.label,
      'prompt': instance.prompt,
      'iconName': instance.iconName,
      'isPrimary': instance.isPrimary,
    };

_$AIInsightsStateImpl _$$AIInsightsStateImplFromJson(
        Map<String, dynamic> json) =>
    _$AIInsightsStateImpl(
      realtimeInsights: (json['realtimeInsights'] as List<dynamic>?)
              ?.map((e) => AIInsight.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      sessionInsights: (json['sessionInsights'] as List<dynamic>?)
              ?.map((e) => AIInsight.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      dailyInsights: (json['dailyInsights'] as List<dynamic>?)
              ?.map((e) => AIInsight.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      trendInsights: (json['trendInsights'] as List<dynamic>?)
              ?.map((e) => AIInsight.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      predictions: (json['predictions'] as List<dynamic>?)
              ?.map((e) => AIInsight.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      isLoading: json['isLoading'] as bool? ?? false,
      isCollapsed: json['isCollapsed'] as bool? ?? false,
      error: json['error'] as String?,
      lastUpdated: json['lastUpdated'] == null
          ? null
          : DateTime.parse(json['lastUpdated'] as String),
    );

Map<String, dynamic> _$$AIInsightsStateImplToJson(
        _$AIInsightsStateImpl instance) =>
    <String, dynamic>{
      'realtimeInsights': instance.realtimeInsights,
      'sessionInsights': instance.sessionInsights,
      'dailyInsights': instance.dailyInsights,
      'trendInsights': instance.trendInsights,
      'predictions': instance.predictions,
      'isLoading': instance.isLoading,
      'isCollapsed': instance.isCollapsed,
      'error': instance.error,
      'lastUpdated': instance.lastUpdated?.toIso8601String(),
    };

_$WorkSessionImpl _$$WorkSessionImplFromJson(Map<String, dynamic> json) =>
    _$WorkSessionImpl(
      id: json['id'] as String,
      startTime: DateTime.parse(json['startTime'] as String),
      endTime: json['endTime'] == null
          ? null
          : DateTime.parse(json['endTime'] as String),
      mainTopic: json['mainTopic'] as String,
      keywords: (json['keywords'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      files:
          (json['files'] as List<dynamic>?)?.map((e) => e as String).toList() ??
              const [],
      focusMinutes: (json['focusMinutes'] as num?)?.toInt() ?? 0,
      breaksCount: (json['breaksCount'] as num?)?.toInt() ?? 0,
      metrics: json['metrics'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$WorkSessionImplToJson(_$WorkSessionImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'startTime': instance.startTime.toIso8601String(),
      'endTime': instance.endTime?.toIso8601String(),
      'mainTopic': instance.mainTopic,
      'keywords': instance.keywords,
      'files': instance.files,
      'focusMinutes': instance.focusMinutes,
      'breaksCount': instance.breaksCount,
      'metrics': instance.metrics,
    };

_$TrendDataImpl _$$TrendDataImplFromJson(Map<String, dynamic> json) =>
    _$TrendDataImpl(
      metric: json['metric'] as String,
      points: (json['points'] as List<dynamic>)
          .map((e) => TrendPoint.fromJson(e as Map<String, dynamic>))
          .toList(),
      unit: json['unit'] as String,
      changePercent: (json['changePercent'] as num?)?.toDouble() ?? 0.0,
      interpretation: json['interpretation'] as String?,
    );

Map<String, dynamic> _$$TrendDataImplToJson(_$TrendDataImpl instance) =>
    <String, dynamic>{
      'metric': instance.metric,
      'points': instance.points,
      'unit': instance.unit,
      'changePercent': instance.changePercent,
      'interpretation': instance.interpretation,
    };

_$TrendPointImpl _$$TrendPointImplFromJson(Map<String, dynamic> json) =>
    _$TrendPointImpl(
      timestamp: DateTime.parse(json['timestamp'] as String),
      value: (json['value'] as num).toDouble(),
      label: json['label'] as String?,
    );

Map<String, dynamic> _$$TrendPointImplToJson(_$TrendPointImpl instance) =>
    <String, dynamic>{
      'timestamp': instance.timestamp.toIso8601String(),
      'value': instance.value,
      'label': instance.label,
    };

_$SkillAssessmentImpl _$$SkillAssessmentImplFromJson(
        Map<String, dynamic> json) =>
    _$SkillAssessmentImpl(
      skillName: json['skillName'] as String,
      currentLevel: (json['currentLevel'] as num).toDouble(),
      previousLevel: (json['previousLevel'] as num).toDouble(),
      evidence:
          (json['evidence'] as List<dynamic>).map((e) => e as String).toList(),
      nextMilestone: json['nextMilestone'] as String?,
      suggestions: (json['suggestions'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$SkillAssessmentImplToJson(
        _$SkillAssessmentImpl instance) =>
    <String, dynamic>{
      'skillName': instance.skillName,
      'currentLevel': instance.currentLevel,
      'previousLevel': instance.previousLevel,
      'evidence': instance.evidence,
      'nextMilestone': instance.nextMilestone,
      'suggestions': instance.suggestions,
    };
