import 'package:freezed_annotation/freezed_annotation.dart';

part 'ai_insight_models.freezed.dart';
part 'ai_insight_models.g.dart';

/// AI洞察卡片数据模型
@freezed
class AIInsightCard with _$AIInsightCard {
  const factory AIInsightCard({
    required String id,
    required String type, // 'discovery', 'suggestion', 'pattern', 'alert'
    required String title,
    required String message,
    required String iconName,
    required DateTime timestamp,
    @Default(0.8) double confidence,
    @Default([]) List<String> entities,
    @Default([]) List<AIInsightAction> actions,
    @Default(false) bool isDismissed,
    @Default(false) bool isRead,
  }) = _AIInsightCard;

  factory AIInsightCard.fromJson(Map<String, dynamic> json) =>
      _$AIInsightCardFromJson(json);
}

/// AI洞察操作
@freezed
class AIInsightAction with _$AIInsightAction {
  const factory AIInsightAction({
    required String id,
    required String label,
    required String type, // 'primary', 'secondary', 'dismiss'
    String? route,
    Map<String, dynamic>? data,
  }) = _AIInsightAction;

  factory AIInsightAction.fromJson(Map<String, dynamic> json) =>
      _$AIInsightActionFromJson(json);
}

/// 今日概览数据
@freezed
class TodayOverview with _$TodayOverview {
  const factory TodayOverview({
    required int newDataPoints,
    required int aiProcessedItems,
    required int insightsGenerated,
    required int activeConnectors,
    required DateTime lastUpdate,
  }) = _TodayOverview;

  factory TodayOverview.fromJson(Map<String, dynamic> json) =>
      _$TodayOverviewFromJson(json);
}

/// 快速访问项目
@freezed
class QuickAccessItem with _$QuickAccessItem {
  const factory QuickAccessItem({
    required String id,
    required String title,
    required String subtitle,
    required String iconName,
    required String type, // 'url', 'file', 'contact', 'note'
    required DateTime lastAccessed,
    String? data,
  }) = _QuickAccessItem;

  factory QuickAccessItem.fromJson(Map<String, dynamic> json) =>
      _$QuickAccessItemFromJson(json);
}
