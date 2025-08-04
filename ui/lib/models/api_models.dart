// ignore_for_file: invalid_annotation_target

import 'package:freezed_annotation/freezed_annotation.dart';

part 'api_models.freezed.dart';
part 'api_models.g.dart';


@freezed
class DataItem with _$DataItem {
  const factory DataItem({
    required String id,
    required String content,
    @JsonKey(name: 'source_connector') required String sourceConnector,
    required DateTime timestamp,
    @JsonKey(name: 'file_path') String? filePath,
    @Default({}) Map<String, dynamic> metadata,
  }) = _DataItem;

  factory DataItem.fromJson(Map<String, dynamic> json) =>
      _$DataItemFromJson(json);
}

@freezed
class AIRecommendation with _$AIRecommendation {
  const factory AIRecommendation({
    required String id,
    required String title,
    required String description,
    required double confidence,
    @JsonKey(name: 'related_items') @Default([]) List<String> relatedItems,
    @JsonKey(name: 'created_at') required DateTime createdAt,
  }) = _AIRecommendation;

  factory AIRecommendation.fromJson(Map<String, dynamic> json) =>
      _$AIRecommendationFromJson(json);
}

@freezed
class ApiResponse with _$ApiResponse {
  const factory ApiResponse({
    required bool success,
    required String message,
    Object? data,
  }) = _ApiResponse;

  factory ApiResponse.fromJson(Map<String, dynamic> json) =>
      _$ApiResponseFromJson(json);
}

@freezed
class ServerInfo with _$ServerInfo {
  const factory ServerInfo({
    required String version,
    required int port,
    @JsonKey(name: 'started_at') required DateTime startedAt,
    @Default('running') String status,
  }) = _ServerInfo;

  factory ServerInfo.fromJson(Map<String, dynamic> json) =>
      _$ServerInfoFromJson(json);
}

// 扩展本地UI需要的模型
@freezed
class DatabaseStats with _$DatabaseStats {
  const factory DatabaseStats({
    @JsonKey(name: 'total_items') required int totalItems,
    @JsonKey(name: 'connector_count') required int connectorCount,
    @JsonKey(name: 'graph_nodes') required int graphNodes,
    @JsonKey(name: 'graph_edges') required int graphEdges,
  }) = _DatabaseStats;

  factory DatabaseStats.fromJson(Map<String, dynamic> json) =>
      _$DatabaseStatsFromJson(json);
}

@freezed
class GraphNode with _$GraphNode {
  const factory GraphNode({
    required String id,
    required String label,
    required String type,
    @Default({}) Map<String, dynamic> properties,
  }) = _GraphNode;

  factory GraphNode.fromJson(Map<String, dynamic> json) =>
      _$GraphNodeFromJson(json);
}

@freezed
class GraphEdge with _$GraphEdge {
  const factory GraphEdge({
    required String id,
    required String source,
    required String target,
    required String type,
    @Default(1.0) double weight,
  }) = _GraphEdge;

  factory GraphEdge.fromJson(Map<String, dynamic> json) =>
      _$GraphEdgeFromJson(json);
}


// 系统诊断信息
@freezed
class SystemDiagnostics with _$SystemDiagnostics {
  const factory SystemDiagnostics({
    @JsonKey(name: 'overall_status') required String overallStatus,
    @JsonKey(name: 'daemon_status') required String daemonStatus,
    @JsonKey(name: 'database_status') required String databaseStatus,
    @JsonKey(name: 'connector_summary') @Default({}) Map<String, dynamic> connectorSummary,
    @JsonKey(name: 'system_resources') @Default({}) Map<String, dynamic> systemResources,
    @JsonKey(name: 'error_summary') @Default([]) List<String> errorSummary,
    @JsonKey(name: 'last_check') required DateTime lastCheck,
  }) = _SystemDiagnostics;

  factory SystemDiagnostics.fromJson(Map<String, dynamic> json) =>
      _$SystemDiagnosticsFromJson(json);
}

