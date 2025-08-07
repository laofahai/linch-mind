// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ipc_protocol.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$IPCErrorImpl _$$IPCErrorImplFromJson(Map<String, dynamic> json) =>
    _$IPCErrorImpl(
      code: json['code'] as String,
      message: json['message'] as String,
      details: json['details'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$IPCErrorImplToJson(_$IPCErrorImpl instance) =>
    <String, dynamic>{
      'code': instance.code,
      'message': instance.message,
      'details': instance.details,
    };

_$IPCMetadataImpl _$$IPCMetadataImplFromJson(Map<String, dynamic> json) =>
    _$IPCMetadataImpl(
      timestamp: json['timestamp'] as String,
      requestId: json['request_id'] as String?,
    );

Map<String, dynamic> _$$IPCMetadataImplToJson(_$IPCMetadataImpl instance) =>
    <String, dynamic>{
      'timestamp': instance.timestamp,
      'request_id': instance.requestId,
    };

_$IPCResponseImpl _$$IPCResponseImplFromJson(Map<String, dynamic> json) =>
    _$IPCResponseImpl(
      success: json['success'] as bool,
      data: json['data'],
      error: json['error'] == null
          ? null
          : IPCError.fromJson(json['error'] as Map<String, dynamic>),
      metadata: json['metadata'] == null
          ? null
          : IPCMetadata.fromJson(json['metadata'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$$IPCResponseImplToJson(_$IPCResponseImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'data': instance.data,
      'error': instance.error,
      'metadata': instance.metadata,
    };

_$IPCRequestImpl _$$IPCRequestImplFromJson(Map<String, dynamic> json) =>
    _$IPCRequestImpl(
      method: json['method'] as String,
      path: json['path'] as String,
      data: json['data'] as Map<String, dynamic>?,
      queryParams: json['query_params'] as Map<String, dynamic>?,
      pathParams: (json['path_params'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, e as String),
      ),
      requestId: json['request_id'] as String?,
    );

Map<String, dynamic> _$$IPCRequestImplToJson(_$IPCRequestImpl instance) =>
    <String, dynamic>{
      'method': instance.method,
      'path': instance.path,
      'data': instance.data,
      'query_params': instance.queryParams,
      'path_params': instance.pathParams,
      'request_id': instance.requestId,
    };

_$ConnectorStatusV2Impl _$$ConnectorStatusV2ImplFromJson(
        Map<String, dynamic> json) =>
    _$ConnectorStatusV2Impl(
      connectorId: json['connector_id'] as String,
      displayName: json['display_name'] as String,
      enabled: json['enabled'] as bool? ?? true,
      runningState: $enumDecodeNullable(
              _$ConnectorRunningStateEnumMap, json['running_state']) ??
          ConnectorRunningState.stopped,
      isInstalled: json['is_installed'] as bool? ?? true,
      isHealthy: json['is_healthy'] as bool? ?? false,
      shouldBeRunning: json['should_be_running'] as bool? ?? false,
      processId: (json['process_id'] as num?)?.toInt(),
      lastHeartbeat: json['last_heartbeat'] as String?,
      dataCount: (json['data_count'] as num?)?.toInt() ?? 0,
      lastActivity: json['last_activity'] as String?,
      errorMessage: json['error_message'] as String?,
      errorCode: json['error_code'] as String?,
    );

Map<String, dynamic> _$$ConnectorStatusV2ImplToJson(
        _$ConnectorStatusV2Impl instance) =>
    <String, dynamic>{
      'connector_id': instance.connectorId,
      'display_name': instance.displayName,
      'enabled': instance.enabled,
      'running_state': _$ConnectorRunningStateEnumMap[instance.runningState]!,
      'is_installed': instance.isInstalled,
      'is_healthy': instance.isHealthy,
      'should_be_running': instance.shouldBeRunning,
      'process_id': instance.processId,
      'last_heartbeat': instance.lastHeartbeat,
      'data_count': instance.dataCount,
      'last_activity': instance.lastActivity,
      'error_message': instance.errorMessage,
      'error_code': instance.errorCode,
    };

const _$ConnectorRunningStateEnumMap = {
  ConnectorRunningState.stopped: 'stopped',
  ConnectorRunningState.starting: 'starting',
  ConnectorRunningState.running: 'running',
  ConnectorRunningState.stopping: 'stopping',
  ConnectorRunningState.error: 'error',
};
