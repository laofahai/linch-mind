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

/// 连接器信息 - 不再区分类型，每个连接器都是独立的
@freezed
class ConnectorDefinition with _$ConnectorDefinition {
  const factory ConnectorDefinition({
    @JsonKey(name: 'connector_id') required String connectorId,
    required String name,
    @JsonKey(name: 'display_name') required String displayName,
    required String description,
    required String category,
    required String version,
    required String author,
    @Default('') String license,
    @JsonKey(name: 'auto_discovery') @Default(false) bool autoDiscovery,
    @JsonKey(name: 'hot_config_reload') @Default(true) bool hotConfigReload,
    @JsonKey(name: 'health_check') @Default(true) bool healthCheck,
    @JsonKey(name: 'entry_point') @Default('main.py') String entryPoint,
    @Default([]) List<String> dependencies,
    @Default([]) List<String> permissions,
    @JsonKey(name: 'config_schema')
    @Default({})
    Map<String, dynamic> configSchema,
    @JsonKey(name: 'config_default_values')
    @Default({})
    Map<String, dynamic> defaultConfig,
    // 添加path字段来直接处理路径信息
    String? path,
    @JsonKey(name: 'is_registered') bool? isRegistered,
    // Registry 相关字段
    @JsonKey(name: 'download_url') String? downloadUrl,
    @Default({}) Map<String, dynamic> platforms,
    @Default({}) Map<String, dynamic> capabilities,
    @JsonKey(name: 'last_updated') String? lastUpdated,
  }) = _ConnectorDefinition;

  factory ConnectorDefinition.fromJson(Map<String, dynamic> json) =>
      _$ConnectorDefinitionFromJson(json);
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

/// 连接器信息 - 运行时状态信息
@freezed
class ConnectorInfo with _$ConnectorInfo {
  const factory ConnectorInfo({
    @JsonKey(name: 'connector_id') required String connectorId,
    @JsonKey(name: 'display_name') required String displayName,
    required ConnectorState state,
    @Default(true) bool enabled,
    // 移除 auto_start 字段，因为数据库模型已经简化了逻辑
    @JsonKey(name: 'process_id') int? processId,
    @JsonKey(name: 'last_heartbeat') DateTime? lastHeartbeat,
    @JsonKey(name: 'data_count') @Default(0) int dataCount,
    @JsonKey(name: 'error_message') String? errorMessage,
    @JsonKey(name: 'created_at') DateTime? createdAt,
    @JsonKey(name: 'updated_at') DateTime? updatedAt,
    @Default({}) Map<String, dynamic> config,
  }) = _ConnectorInfo;

  factory ConnectorInfo.fromJson(Map<String, dynamic> json) =>
      _$ConnectorInfoFromJson(json);
}

/// 统一的连接器安装请求
@freezed
class InstallConnectorRequest with _$InstallConnectorRequest {
  const factory InstallConnectorRequest({
    @JsonKey(name: 'connector_id') required String connectorId,
    @JsonKey(name: 'source')
    @Default('registry')
    String source, // registry, manual, scan
    @JsonKey(name: 'display_name') String? displayName,
    @Default({}) Map<String, dynamic> config,
    // 移除 auto_start 字段，因为数据库模型已经简化了逻辑
    String? path, // for scan source
    String? description, // for manual source
  }) = _InstallConnectorRequest;

  factory InstallConnectorRequest.fromJson(Map<String, dynamic> json) =>
      _$InstallConnectorRequestFromJson(json);
}

/// 创建连接器请求 - 保持向后兼容
@freezed
class CreateConnectorRequest with _$CreateConnectorRequest {
  const factory CreateConnectorRequest({
    @JsonKey(name: 'connector_id') required String connectorId,
    @JsonKey(name: 'display_name') required String displayName,
    @Default({}) Map<String, dynamic> config,
    // 移除 auto_start 字段，因为数据库模型已经简化了逻辑
    @JsonKey(name: 'template_id') String? templateId,
  }) = _CreateConnectorRequest;

  factory CreateConnectorRequest.fromJson(Map<String, dynamic> json) =>
      _$CreateConnectorRequestFromJson(json);
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
    @JsonKey(name: 'connector_id') required String connectorId,
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
    @JsonKey(name: 'running_instances')
    @Default([])
    List<String> runningInstances,
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
    @JsonKey(name: 'state_distribution')
    required Map<String, int> stateDistribution,
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

/// 连接器发现响应 - 发现可用的连接器
@freezed
class DiscoveryResponse with _$DiscoveryResponse {
  const factory DiscoveryResponse({
    required bool success,
    required String message,
    @JsonKey(name: 'connectors')
    @Default([])
    List<ConnectorDefinition> connectors,
  }) = _DiscoveryResponse;

  factory DiscoveryResponse.fromJson(Map<String, dynamic> json) =>
      _$DiscoveryResponseFromJson(json);
}

/// 连接器列表响应
@freezed
class ConnectorListResponse with _$ConnectorListResponse {
  const factory ConnectorListResponse({
    required bool success,
    @Default([]) List<ConnectorInfo> connectors,
    @JsonKey(name: 'total_count') @Default(0) int totalCount,
  }) = _ConnectorListResponse;

  factory ConnectorListResponse.fromJson(Map<String, dynamic> json) =>
      _$ConnectorListResponseFromJson(json);
}

/// 连接器详情响应
@freezed
class ConnectorDetailResponse with _$ConnectorDetailResponse {
  const factory ConnectorDetailResponse({
    required bool success,
    required ConnectorInfo connector,
  }) = _ConnectorDetailResponse;

  factory ConnectorDetailResponse.fromJson(Map<String, dynamic> json) =>
      _$ConnectorDetailResponseFromJson(json);
}

/// 操作响应（启动、停止、重启等）
@freezed
class OperationResponse with _$OperationResponse {
  const factory OperationResponse({
    required bool success,
    required String message,
    @JsonKey(name: 'connector_id') required String connectorId,
    required ConnectorState state,
    @JsonKey(name: 'hot_reload_applied') bool? hotReloadApplied,
    @JsonKey(name: 'requires_restart') bool? requiresRestart,
    @JsonKey(name: 'was_running') bool? wasRunning,
  }) = _OperationResponse;

  factory OperationResponse.fromJson(Map<String, dynamic> json) =>
      _$OperationResponseFromJson(json);
}

/// 发现的连接器信息
@freezed
class DiscoveredConnectorInfo with _$DiscoveredConnectorInfo {
  const factory DiscoveredConnectorInfo({
    required String path,
    @JsonKey(name: 'connector_id') required String connectorId,
    required String name,
    required String description,
    required String version,
    @JsonKey(name: 'entry_point') required String entryPoint,
    @JsonKey(name: 'is_registered') required bool isRegistered,
  }) = _DiscoveredConnectorInfo;

  factory DiscoveredConnectorInfo.fromJson(Map<String, dynamic> json) =>
      _$DiscoveredConnectorInfoFromJson(json);
}

/// 目录扫描响应
@freezed
class DirectoryScanResponse with _$DirectoryScanResponse {
  const factory DirectoryScanResponse({
    required bool success,
    required Map<String, dynamic> data,
    required String message,
  }) = _DirectoryScanResponse;

  factory DirectoryScanResponse.fromJson(Map<String, dynamic> json) =>
      _$DirectoryScanResponseFromJson(json);
}

/// 连接器注册响应
@freezed
class ConnectorRegistrationResponse with _$ConnectorRegistrationResponse {
  const factory ConnectorRegistrationResponse({
    required bool success,
    required Map<String, dynamic> data,
    required String message,
  }) = _ConnectorRegistrationResponse;

  factory ConnectorRegistrationResponse.fromJson(Map<String, dynamic> json) =>
      _$ConnectorRegistrationResponseFromJson(json);
}
