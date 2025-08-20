import 'package:freezed_annotation/freezed_annotation.dart';

part 'ai_insights_models.freezed.dart';
part 'ai_insights_models.g.dart';

/// AI洞察时间维度
enum InsightTimeframe {
  @JsonValue('realtime')
  realtime, // 实时（秒级）

  @JsonValue('session')
  session, // 会话（分钟级）

  @JsonValue('daily')
  daily, // 今日（小时级）

  @JsonValue('weekly')
  weekly, // 本周（天级）

  @JsonValue('trend')
  trend, // 趋势（周/月级）

  @JsonValue('prediction')
  prediction, // 预测（未来）
}

/// AI洞察类型
enum InsightType {
  @JsonValue('activity')
  activity, // 活动观察

  @JsonValue('pattern')
  pattern, // 模式识别

  @JsonValue('performance')
  performance, // 效率分析

  @JsonValue('learning')
  learning, // 学习轨迹

  @JsonValue('suggestion')
  suggestion, // 建议推荐

  @JsonValue('trend')
  trend, // 趋势分析
}

/// AI洞察项目
@freezed
class AIInsight with _$AIInsight {
  const factory AIInsight({
    required String id,
    required String title,
    required String description,
    required InsightTimeframe timeframe,
    required InsightType type,
    required double confidence,
    required DateTime timestamp,
    @Default([]) List<InsightAction> actions,
    Map<String, dynamic>? metadata,
    String? iconName,
    @Default(false) bool isImportant,
    @Default(false) bool isDismissed,
  }) = _AIInsight;

  factory AIInsight.fromJson(Map<String, dynamic> json) =>
      _$AIInsightFromJson(json);
}

/// 洞察操作按钮
@freezed
class InsightAction with _$InsightAction {
  const factory InsightAction({
    required String id,
    required String label,
    required String prompt, // 要填入聊天框的提示词
    String? iconName,
    @Default(false) bool isPrimary,
  }) = _InsightAction;

  factory InsightAction.fromJson(Map<String, dynamic> json) =>
      _$InsightActionFromJson(json);
}

/// AI洞察面板状态
@freezed
class AIInsightsState with _$AIInsightsState {
  const factory AIInsightsState({
    @Default([]) List<AIInsight> realtimeInsights, // 实时洞察
    @Default([]) List<AIInsight> sessionInsights, // 会话洞察
    @Default([]) List<AIInsight> dailyInsights, // 今日洞察
    @Default([]) List<AIInsight> trendInsights, // 趋势洞察
    @Default([]) List<AIInsight> predictions, // 预测建议
    @Default(false) bool isLoading,
    @Default(false) bool isCollapsed, // 是否折叠
    String? error,
    DateTime? lastUpdated,
  }) = _AIInsightsState;

  factory AIInsightsState.fromJson(Map<String, dynamic> json) =>
      _$AIInsightsStateFromJson(json);
}

/// 工作会话信息
@freezed
class WorkSession with _$WorkSession {
  const factory WorkSession({
    required String id,
    required DateTime startTime,
    DateTime? endTime,
    required String mainTopic, // 主要工作主题
    @Default([]) List<String> keywords, // 关键词
    @Default([]) List<String> files, // 涉及文件
    @Default(0) int focusMinutes, // 专注时间（分钟）
    @Default(0) int breaksCount, // 休息次数
    Map<String, dynamic>? metrics, // 其他指标
  }) = _WorkSession;

  factory WorkSession.fromJson(Map<String, dynamic> json) =>
      _$WorkSessionFromJson(json);
}

/// 长期趋势数据
@freezed
class TrendData with _$TrendData {
  const factory TrendData({
    required String metric, // 指标名称
    required List<TrendPoint> points, // 数据点
    required String unit, // 单位
    @Default(0.0) double changePercent, // 变化百分比
    String? interpretation, // 趋势解释
  }) = _TrendData;

  factory TrendData.fromJson(Map<String, dynamic> json) =>
      _$TrendDataFromJson(json);
}

/// 趋势数据点
@freezed
class TrendPoint with _$TrendPoint {
  const factory TrendPoint({
    required DateTime timestamp,
    required double value,
    String? label,
  }) = _TrendPoint;

  factory TrendPoint.fromJson(Map<String, dynamic> json) =>
      _$TrendPointFromJson(json);
}

/// 技能评估
@freezed
class SkillAssessment with _$SkillAssessment {
  const factory SkillAssessment({
    required String skillName,
    required double currentLevel, // 当前水平 (0-1)
    required double previousLevel, // 之前水平
    required List<String> evidence, // 证据/表现
    String? nextMilestone, // 下一个里程碑
    @Default([]) List<String> suggestions, // 提升建议
  }) = _SkillAssessment;

  factory SkillAssessment.fromJson(Map<String, dynamic> json) =>
      _$SkillAssessmentFromJson(json);
}
