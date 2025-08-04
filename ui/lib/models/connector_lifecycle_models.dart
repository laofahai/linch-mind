// ignore_for_file: invalid_annotation_target

import 'package:freezed_annotation/freezed_annotation.dart';

part 'connector_lifecycle_models.freezed.dart';
part 'connector_lifecycle_models.g.dart';

/// 连接器状态枚举 - 对应后端ConnectorState
enum ConnectorState {
  @JsonValue('available')
  available,
  @JsonValue('installed')
  installed,
  @JsonValue('configured')
  configured,
  @JsonValue('enabled')
  enabled,
  @JsonValue('running')
  running,
  @JsonValue('error')
  error,
  @JsonValue('stopping')
  stopping,
  @JsonValue('updating')
  updating,
  @JsonValue('uninstalling')
  uninstalling,
}

/// 连接器类型信息
@freezed
class ConnectorTypeInfo with _$ConnectorTypeInfo {
  const factory ConnectorTypeInfo({
    @JsonKey(name: 'type_id') required String typeId,
    required String name,
    @JsonKey(name: 'display_name') required String displayName,
    required String description,
    required String category,
    required String version,
    required String author,
    @Default('') String license,
    @JsonKey(name: 'supports_multiple_instances') @Default(false) bool supportsMultipleInstances,
    @JsonKey(name: 'max_instances_per_user') @Default(1) int maxInstancesPerUser,
    @JsonKey(name: 'auto_discovery') @Default(false) bool autoDiscovery,
    @JsonKey(name: 'hot_config_reload') @Default(true) bool hotConfigReload,
    @JsonKey(name: 'health_check') @Default(true) bool healthCheck,
    @JsonKey(name: 'entry_point') @Default('main.py') String entryPoint,
    @Default([]) List<String> dependencies,
    @Default([]) List<String> permissions,
    @JsonKey(name: 'config_schema') @Default({}) Map<String, dynamic> configSchema,
    @JsonKey(name: 'default_config') @Default({}) Map<String, dynamic> defaultConfig,
    @JsonKey(name: 'instance_templates') @Default([]) List<InstanceTemplate> instanceTemplates,
  }) = _ConnectorTypeInfo;

  factory ConnectorTypeInfo.fromJson(Map<String, dynamic> json) =>
      _$ConnectorTypeInfoFromJson(json);
}

/// 实例模板
@freezed
class InstanceTemplate with _$InstanceTemplate {
  const factory InstanceTemplate({
    required String id,
    required String name,
    required String description,
    @Default({}) Map<String, dynamic> config,
  }) = _InstanceTemplate;

  factory InstanceTemplate.fromJson(Map<String, dynamic> json) =>
      _$InstanceTemplateFromJson(json);
}

/// 连接器实例信息
@freezed
class ConnectorInstanceInfo with _$ConnectorInstanceInfo {
  const factory ConnectorInstanceInfo({
    @JsonKey(name: 'instance_id') required String instanceId,
    @JsonKey(name: 'display_name') required String displayName,
    @JsonKey(name: 'type_id') required String typeId,
    @JsonKey(name: 'type_name') @Default('未知') String typeName,
    required ConnectorState state,
    @Default(true) bool enabled,
    @JsonKey(name: 'auto_start') @Default(true) bool autoStart,
    @JsonKey(name: 'process_id') int? processId,
    @JsonKey(name: 'last_heartbeat') DateTime? lastHeartbeat,
    @JsonKey(name: 'data_count') @Default(0) int dataCount,
    @JsonKey(name: 'error_message') String? errorMessage,
    @JsonKey(name: 'created_at') DateTime? createdAt,
    @JsonKey(name: 'updated_at') DateTime? updatedAt,
    @Default({}) Map<String, dynamic> config,
  }) = _ConnectorInstanceInfo;

  factory ConnectorInstanceInfo.fromJson(Map<String, dynamic> json) =>
      _$ConnectorInstanceInfoFromJson(json);
}

/// 创建连接器实例请求
@freezed
class CreateInstanceRequest with _$CreateInstanceRequest {
  const factory CreateInstanceRequest({
    @JsonKey(name: 'type_id') required String typeId,
    @JsonKey(name: 'display_name') required String displayName,
    @Default({}) Map<String, dynamic> config,
    @JsonKey(name: 'auto_start') @Default(true) bool autoStart,
    @JsonKey(name: 'template_id') String? templateId,
  }) = _CreateInstanceRequest;

  factory CreateInstanceRequest.fromJson(Map<String, dynamic> json) =>
      _$CreateInstanceRequestFromJson(json);
}

/// 更新配置请求
@freezed
class UpdateConfigRequest with _$UpdateConfigRequest {
  const factory UpdateConfigRequest({
    required Map<String, dynamic> config,
  }) = _UpdateConfigRequest;

  factory UpdateConfigRequest.fromJson(Map<String, dynamic> json) =>
      _$UpdateConfigRequestFromJson(json);
}

/// 连接器事件
@freezed
class ConnectorEvent with _$ConnectorEvent {
  const factory ConnectorEvent({
    required String event,
    required DateTime timestamp,
    required Map<String, dynamic> data,
  }) = _ConnectorEvent;

  factory ConnectorEvent.fromJson(Map<String, dynamic> json) =>
      _$ConnectorEventFromJson(json);
}

/// 状态变化事件
@freezed
class StateChangeEvent with _$StateChangeEvent {
  const factory StateChangeEvent({
    @JsonKey(name: 'instance_id') required String instanceId,
    @JsonKey(name: 'old_state') required ConnectorState oldState,
    @JsonKey(name: 'new_state') required ConnectorState newState,
  }) = _StateChangeEvent;

  factory StateChangeEvent.fromJson(Map<String, dynamic> json) =>
      _$StateChangeEventFromJson(json);
}

/// 系统健康检查结果
@freezed
class ConnectorHealthResponse with _$ConnectorHealthResponse {
  const factory ConnectorHealthResponse({
    required bool success,
    required HealthStatus health,
  }) = _ConnectorHealthResponse;

  factory ConnectorHealthResponse.fromJson(Map<String, dynamic> json) =>
      _$ConnectorHealthResponseFromJson(json);
}

/// 健康状态详情
@freezed
class HealthStatus with _$HealthStatus {
  const factory HealthStatus({
    @JsonKey(name: 'overall_score') required double overallScore,
    required String status, // healthy, degraded, unhealthy
    @JsonKey(name: 'config_system') required ConfigSystemHealth configSystem,
    @JsonKey(name: 'runtime_system') required RuntimeSystemHealth runtimeSystem,
  }) = _HealthStatus;

  factory HealthStatus.fromJson(Map<String, dynamic> json) =>
      _$HealthStatusFromJson(json);
}

/// 配置系统健康状态
@freezed
class ConfigSystemHealth with _$ConfigSystemHealth {
  const factory ConfigSystemHealth({
    required String status,
    @JsonKey(name: 'config_version') required String configVersion,
    @JsonKey(name: 'last_reload') DateTime? lastReload,
    @Default({}) Map<String, dynamic> errors,
  }) = _ConfigSystemHealth;

  factory ConfigSystemHealth.fromJson(Map<String, dynamic> json) =>
      _$ConfigSystemHealthFromJson(json);
}

/// 运行时系统健康状态
@freezed
class RuntimeSystemHealth with _$RuntimeSystemHealth {
  const factory RuntimeSystemHealth({
    @JsonKey(name: 'total_instances') required int totalInstances,
    @JsonKey(name: 'healthy_instances') required int healthyInstances,
    @JsonKey(name: 'error_instances') required int errorInstances,
    @JsonKey(name: 'running_instances') required int runningInstances,
  }) = _RuntimeSystemHealth;

  factory RuntimeSystemHealth.fromJson(Map<String, dynamic> json) =>
      _$RuntimeSystemHealthFromJson(json);
}

/// 连接器状态概览
@freezed
class ConnectorStatesOverview with _$ConnectorStatesOverview {
  const factory ConnectorStatesOverview({
    required bool success,
    required StateOverview overview,
    @JsonKey(name: 'running_instances') @Default([]) List<String> runningInstances,
  }) = _ConnectorStatesOverview;

  factory ConnectorStatesOverview.fromJson(Map<String, dynamic> json) =>
      _$ConnectorStatesOverviewFromJson(json);
}

/// 状态概览详情
@freezed
class StateOverview with _$StateOverview {
  const factory StateOverview({
    @JsonKey(name: 'total_instances') required int totalInstances,
    @JsonKey(name: 'running_instances') required int runningInstances,
    @JsonKey(name: 'state_distribution') required Map<String, int> stateDistribution,
  }) = _StateOverview;

  factory StateOverview.fromJson(Map<String, dynamic> json) =>
      _$StateOverviewFromJson(json);
}

/// API响应通用包装器
@freezed
class ConnectorApiResponse with _$ConnectorApiResponse {
  const factory ConnectorApiResponse({
    required bool success,
    required String message,
    Object? data,
    String? error,
  }) = _ConnectorApiResponse;

  factory ConnectorApiResponse.fromJson(Map<String, dynamic> json) =>
      _$ConnectorApiResponseFromJson(json);
}

/// 连接器类型发现响应
@freezed
class DiscoveryResponse with _$DiscoveryResponse {
  const factory DiscoveryResponse({
    required bool success,
    required String message,
    @JsonKey(name: 'connector_types') @Default([]) List<ConnectorTypeInfo> connectorTypes,
  }) = _DiscoveryResponse;

  factory DiscoveryResponse.fromJson(Map<String, dynamic> json) =>
      _$DiscoveryResponseFromJson(json);
}

/// 实例列表响应
@freezed
class InstanceListResponse with _$InstanceListResponse {
  const factory InstanceListResponse({
    required bool success,
    @Default([]) List<ConnectorInstanceInfo> instances,
    @JsonKey(name: 'total_count') @Default(0) int totalCount,
  }) = _InstanceListResponse;

  factory InstanceListResponse.fromJson(Map<String, dynamic> json) =>
      _$InstanceListResponseFromJson(json);
}

/// 实例详情响应
@freezed
class InstanceDetailResponse with _$InstanceDetailResponse {
  const factory InstanceDetailResponse({
    required bool success,
    required ConnectorInstanceDetail instance,
  }) = _InstanceDetailResponse;

  factory InstanceDetailResponse.fromJson(Map<String, dynamic> json) =>
      _$InstanceDetailResponseFromJson(json);
}

/// 连接器实例详情（包含类型信息）
@freezed
class ConnectorInstanceDetail with _$ConnectorInstanceDetail {
  const factory ConnectorInstanceDetail({
    @JsonKey(name: 'instance_id') required String instanceId,
    @JsonKey(name: 'display_name') required String displayName,
    @JsonKey(name: 'type_id') required String typeId,
    required Map<String, dynamic> config,
    required ConnectorState state,
    @Default(true) bool enabled,
    @JsonKey(name: 'auto_start') @Default(true) bool autoStart,
    @JsonKey(name: 'process_id') int? processId,
    @JsonKey(name: 'last_heartbeat') DateTime? lastHeartbeat,
    @JsonKey(name: 'data_count') @Default(0) int dataCount,
    @JsonKey(name: 'error_message') String? errorMessage,
    @JsonKey(name: 'created_at') DateTime? createdAt,
    @JsonKey(name: 'updated_at') DateTime? updatedAt,
    @JsonKey(name: 'connector_type') ConnectorTypeInfo? connectorType,
  }) = _ConnectorInstanceDetail;

  factory ConnectorInstanceDetail.fromJson(Map<String, dynamic> json) =>
      _$ConnectorInstanceDetailFromJson(json);
}

/// 操作响应（启动、停止、重启等）
@freezed
class OperationResponse with _$OperationResponse {
  const factory OperationResponse({
    required bool success,
    required String message,
    @JsonKey(name: 'instance_id') required String instanceId,
    required ConnectorState state,
    @JsonKey(name: 'hot_reload_applied') bool? hotReloadApplied,
    @JsonKey(name: 'requires_restart') bool? requiresRestart,
    @JsonKey(name: 'was_running') bool? wasRunning,
  }) = _OperationResponse;

  factory OperationResponse.fromJson(Map<String, dynamic> json) =>
      _$OperationResponseFromJson(json);
}