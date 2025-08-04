// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'api_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$DataItemImpl _$$DataItemImplFromJson(Map<String, dynamic> json) =>
    _$DataItemImpl(
      id: json['id'] as String,
      content: json['content'] as String,
      sourceConnector: json['source_connector'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      filePath: json['file_path'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>? ?? const {},
    );

Map<String, dynamic> _$$DataItemImplToJson(_$DataItemImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'content': instance.content,
      'source_connector': instance.sourceConnector,
      'timestamp': instance.timestamp.toIso8601String(),
      'file_path': instance.filePath,
      'metadata': instance.metadata,
    };

_$AIRecommendationImpl _$$AIRecommendationImplFromJson(
        Map<String, dynamic> json) =>
    _$AIRecommendationImpl(
      id: json['id'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      confidence: (json['confidence'] as num).toDouble(),
      relatedItems: (json['related_items'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      createdAt: DateTime.parse(json['created_at'] as String),
    );

Map<String, dynamic> _$$AIRecommendationImplToJson(
        _$AIRecommendationImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'title': instance.title,
      'description': instance.description,
      'confidence': instance.confidence,
      'related_items': instance.relatedItems,
      'created_at': instance.createdAt.toIso8601String(),
    };

_$ApiResponseImpl _$$ApiResponseImplFromJson(Map<String, dynamic> json) =>
    _$ApiResponseImpl(
      success: json['success'] as bool,
      message: json['message'] as String,
      data: json['data'],
    );

Map<String, dynamic> _$$ApiResponseImplToJson(_$ApiResponseImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'message': instance.message,
      'data': instance.data,
    };

_$ServerInfoImpl _$$ServerInfoImplFromJson(Map<String, dynamic> json) =>
    _$ServerInfoImpl(
      version: json['version'] as String,
      port: (json['port'] as num).toInt(),
      startedAt: DateTime.parse(json['started_at'] as String),
      status: json['status'] as String? ?? 'running',
    );

Map<String, dynamic> _$$ServerInfoImplToJson(_$ServerInfoImpl instance) =>
    <String, dynamic>{
      'version': instance.version,
      'port': instance.port,
      'started_at': instance.startedAt.toIso8601String(),
      'status': instance.status,
    };

_$DatabaseStatsImpl _$$DatabaseStatsImplFromJson(Map<String, dynamic> json) =>
    _$DatabaseStatsImpl(
      totalItems: (json['total_items'] as num).toInt(),
      connectorCount: (json['connector_count'] as num).toInt(),
      graphNodes: (json['graph_nodes'] as num).toInt(),
      graphEdges: (json['graph_edges'] as num).toInt(),
    );

Map<String, dynamic> _$$DatabaseStatsImplToJson(_$DatabaseStatsImpl instance) =>
    <String, dynamic>{
      'total_items': instance.totalItems,
      'connector_count': instance.connectorCount,
      'graph_nodes': instance.graphNodes,
      'graph_edges': instance.graphEdges,
    };

_$GraphNodeImpl _$$GraphNodeImplFromJson(Map<String, dynamic> json) =>
    _$GraphNodeImpl(
      id: json['id'] as String,
      label: json['label'] as String,
      type: json['type'] as String,
      properties: json['properties'] as Map<String, dynamic>? ?? const {},
    );

Map<String, dynamic> _$$GraphNodeImplToJson(_$GraphNodeImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'label': instance.label,
      'type': instance.type,
      'properties': instance.properties,
    };

_$GraphEdgeImpl _$$GraphEdgeImplFromJson(Map<String, dynamic> json) =>
    _$GraphEdgeImpl(
      id: json['id'] as String,
      source: json['source'] as String,
      target: json['target'] as String,
      type: json['type'] as String,
      weight: (json['weight'] as num?)?.toDouble() ?? 1.0,
    );

Map<String, dynamic> _$$GraphEdgeImplToJson(_$GraphEdgeImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'source': instance.source,
      'target': instance.target,
      'type': instance.type,
      'weight': instance.weight,
    };

_$SystemDiagnosticsImpl _$$SystemDiagnosticsImplFromJson(
        Map<String, dynamic> json) =>
    _$SystemDiagnosticsImpl(
      overallStatus: json['overall_status'] as String,
      daemonStatus: json['daemon_status'] as String,
      databaseStatus: json['database_status'] as String,
      connectorSummary:
          json['connector_summary'] as Map<String, dynamic>? ?? const {},
      systemResources:
          json['system_resources'] as Map<String, dynamic>? ?? const {},
      errorSummary: (json['error_summary'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      lastCheck: DateTime.parse(json['last_check'] as String),
    );

Map<String, dynamic> _$$SystemDiagnosticsImplToJson(
        _$SystemDiagnosticsImpl instance) =>
    <String, dynamic>{
      'overall_status': instance.overallStatus,
      'daemon_status': instance.daemonStatus,
      'database_status': instance.databaseStatus,
      'connector_summary': instance.connectorSummary,
      'system_resources': instance.systemResources,
      'error_summary': instance.errorSummary,
      'last_check': instance.lastCheck.toIso8601String(),
    };
