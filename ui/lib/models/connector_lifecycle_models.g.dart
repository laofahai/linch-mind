// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'connector_lifecycle_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$ConnectorDefinitionImpl _$$ConnectorDefinitionImplFromJson(
        Map<String, dynamic> json) =>
    _$ConnectorDefinitionImpl(
      connectorId: json['connector_id'] as String,
      name: json['name'] as String,
      displayName: json['display_name'] as String,
      description: json['description'] as String,
      category: json['category'] as String,
      version: json['version'] as String,
      author: json['author'] as String,
      license: json['license'] as String? ?? '',
      autoDiscovery: json['auto_discovery'] as bool? ?? false,
      hotConfigReload: json['hot_config_reload'] as bool? ?? true,
      healthCheck: json['health_check'] as bool? ?? true,
      entryPoint: json['entry_point'] as String? ?? 'main.py',
      dependencies: (json['dependencies'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      permissions: (json['permissions'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      configSchema: json['config_schema'] as Map<String, dynamic>? ?? const {},
      defaultConfig:
          json['default_config'] as Map<String, dynamic>? ?? const {},
      path: json['path'] as String?,
      isRegistered: json['is_registered'] as bool?,
      downloadUrl: json['download_url'] as String?,
      platforms: json['platforms'] as Map<String, dynamic>? ?? const {},
      capabilities: json['capabilities'] as Map<String, dynamic>? ?? const {},
      lastUpdated: json['last_updated'] as String?,
    );

Map<String, dynamic> _$$ConnectorDefinitionImplToJson(
        _$ConnectorDefinitionImpl instance) =>
    <String, dynamic>{
      'connector_id': instance.connectorId,
      'name': instance.name,
      'display_name': instance.displayName,
      'description': instance.description,
      'category': instance.category,
      'version': instance.version,
      'author': instance.author,
      'license': instance.license,
      'auto_discovery': instance.autoDiscovery,
      'hot_config_reload': instance.hotConfigReload,
      'health_check': instance.healthCheck,
      'entry_point': instance.entryPoint,
      'dependencies': instance.dependencies,
      'permissions': instance.permissions,
      'config_schema': instance.configSchema,
      'default_config': instance.defaultConfig,
      'path': instance.path,
      'is_registered': instance.isRegistered,
      'download_url': instance.downloadUrl,
      'platforms': instance.platforms,
      'capabilities': instance.capabilities,
      'last_updated': instance.lastUpdated,
    };

_$InstanceTemplateImpl _$$InstanceTemplateImplFromJson(
        Map<String, dynamic> json) =>
    _$InstanceTemplateImpl(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String,
      config: json['config'] as Map<String, dynamic>? ?? const {},
    );

Map<String, dynamic> _$$InstanceTemplateImplToJson(
        _$InstanceTemplateImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'config': instance.config,
    };

_$ConnectorInfoImpl _$$ConnectorInfoImplFromJson(Map<String, dynamic> json) =>
    _$ConnectorInfoImpl(
      connectorId: json['connector_id'] as String,
      displayName: json['display_name'] as String,
      state: $enumDecode(_$ConnectorStateEnumMap, json['state']),
      enabled: json['enabled'] as bool? ?? true,
      autoStart: json['auto_start'] as bool? ?? true,
      processId: (json['process_id'] as num?)?.toInt(),
      lastHeartbeat: json['last_heartbeat'] == null
          ? null
          : DateTime.parse(json['last_heartbeat'] as String),
      dataCount: (json['data_count'] as num?)?.toInt() ?? 0,
      errorMessage: json['error_message'] as String?,
      createdAt: json['created_at'] == null
          ? null
          : DateTime.parse(json['created_at'] as String),
      updatedAt: json['updated_at'] == null
          ? null
          : DateTime.parse(json['updated_at'] as String),
      config: json['config'] as Map<String, dynamic>? ?? const {},
    );

Map<String, dynamic> _$$ConnectorInfoImplToJson(_$ConnectorInfoImpl instance) =>
    <String, dynamic>{
      'connector_id': instance.connectorId,
      'display_name': instance.displayName,
      'state': _$ConnectorStateEnumMap[instance.state]!,
      'enabled': instance.enabled,
      'auto_start': instance.autoStart,
      'process_id': instance.processId,
      'last_heartbeat': instance.lastHeartbeat?.toIso8601String(),
      'data_count': instance.dataCount,
      'error_message': instance.errorMessage,
      'created_at': instance.createdAt?.toIso8601String(),
      'updated_at': instance.updatedAt?.toIso8601String(),
      'config': instance.config,
    };

const _$ConnectorStateEnumMap = {
  ConnectorState.available: 'available',
  ConnectorState.installed: 'installed',
  ConnectorState.configured: 'configured',
  ConnectorState.enabled: 'enabled',
  ConnectorState.running: 'running',
  ConnectorState.error: 'error',
  ConnectorState.stopping: 'stopping',
  ConnectorState.updating: 'updating',
  ConnectorState.uninstalling: 'uninstalling',
};

_$InstallConnectorRequestImpl _$$InstallConnectorRequestImplFromJson(
        Map<String, dynamic> json) =>
    _$InstallConnectorRequestImpl(
      connectorId: json['connector_id'] as String,
      source: json['source'] as String? ?? 'registry',
      displayName: json['display_name'] as String?,
      config: json['config'] as Map<String, dynamic>? ?? const {},
      autoStart: json['auto_start'] as bool? ?? false,
      path: json['path'] as String?,
      description: json['description'] as String?,
    );

Map<String, dynamic> _$$InstallConnectorRequestImplToJson(
        _$InstallConnectorRequestImpl instance) =>
    <String, dynamic>{
      'connector_id': instance.connectorId,
      'source': instance.source,
      'display_name': instance.displayName,
      'config': instance.config,
      'auto_start': instance.autoStart,
      'path': instance.path,
      'description': instance.description,
    };

_$CreateConnectorRequestImpl _$$CreateConnectorRequestImplFromJson(
        Map<String, dynamic> json) =>
    _$CreateConnectorRequestImpl(
      connectorId: json['connector_id'] as String,
      displayName: json['display_name'] as String,
      config: json['config'] as Map<String, dynamic>? ?? const {},
      autoStart: json['auto_start'] as bool? ?? true,
      templateId: json['template_id'] as String?,
    );

Map<String, dynamic> _$$CreateConnectorRequestImplToJson(
        _$CreateConnectorRequestImpl instance) =>
    <String, dynamic>{
      'connector_id': instance.connectorId,
      'display_name': instance.displayName,
      'config': instance.config,
      'auto_start': instance.autoStart,
      'template_id': instance.templateId,
    };

_$UpdateConfigRequestImpl _$$UpdateConfigRequestImplFromJson(
        Map<String, dynamic> json) =>
    _$UpdateConfigRequestImpl(
      config: json['config'] as Map<String, dynamic>,
    );

Map<String, dynamic> _$$UpdateConfigRequestImplToJson(
        _$UpdateConfigRequestImpl instance) =>
    <String, dynamic>{
      'config': instance.config,
    };

_$ConnectorEventImpl _$$ConnectorEventImplFromJson(Map<String, dynamic> json) =>
    _$ConnectorEventImpl(
      event: json['event'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      data: json['data'] as Map<String, dynamic>,
    );

Map<String, dynamic> _$$ConnectorEventImplToJson(
        _$ConnectorEventImpl instance) =>
    <String, dynamic>{
      'event': instance.event,
      'timestamp': instance.timestamp.toIso8601String(),
      'data': instance.data,
    };

_$StateChangeEventImpl _$$StateChangeEventImplFromJson(
        Map<String, dynamic> json) =>
    _$StateChangeEventImpl(
      connectorId: json['connector_id'] as String,
      oldState: $enumDecode(_$ConnectorStateEnumMap, json['old_state']),
      newState: $enumDecode(_$ConnectorStateEnumMap, json['new_state']),
    );

Map<String, dynamic> _$$StateChangeEventImplToJson(
        _$StateChangeEventImpl instance) =>
    <String, dynamic>{
      'connector_id': instance.connectorId,
      'old_state': _$ConnectorStateEnumMap[instance.oldState]!,
      'new_state': _$ConnectorStateEnumMap[instance.newState]!,
    };

_$ConnectorHealthResponseImpl _$$ConnectorHealthResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$ConnectorHealthResponseImpl(
      success: json['success'] as bool,
      health: HealthStatus.fromJson(json['health'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$$ConnectorHealthResponseImplToJson(
        _$ConnectorHealthResponseImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'health': instance.health,
    };

_$HealthStatusImpl _$$HealthStatusImplFromJson(Map<String, dynamic> json) =>
    _$HealthStatusImpl(
      overallScore: (json['overall_score'] as num).toDouble(),
      status: json['status'] as String,
      configSystem: ConfigSystemHealth.fromJson(
          json['config_system'] as Map<String, dynamic>),
      runtimeSystem: RuntimeSystemHealth.fromJson(
          json['runtime_system'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$$HealthStatusImplToJson(_$HealthStatusImpl instance) =>
    <String, dynamic>{
      'overall_score': instance.overallScore,
      'status': instance.status,
      'config_system': instance.configSystem,
      'runtime_system': instance.runtimeSystem,
    };

_$ConfigSystemHealthImpl _$$ConfigSystemHealthImplFromJson(
        Map<String, dynamic> json) =>
    _$ConfigSystemHealthImpl(
      status: json['status'] as String,
      configVersion: json['config_version'] as String,
      lastReload: json['last_reload'] == null
          ? null
          : DateTime.parse(json['last_reload'] as String),
      errors: json['errors'] as Map<String, dynamic>? ?? const {},
    );

Map<String, dynamic> _$$ConfigSystemHealthImplToJson(
        _$ConfigSystemHealthImpl instance) =>
    <String, dynamic>{
      'status': instance.status,
      'config_version': instance.configVersion,
      'last_reload': instance.lastReload?.toIso8601String(),
      'errors': instance.errors,
    };

_$RuntimeSystemHealthImpl _$$RuntimeSystemHealthImplFromJson(
        Map<String, dynamic> json) =>
    _$RuntimeSystemHealthImpl(
      totalInstances: (json['total_instances'] as num).toInt(),
      healthyInstances: (json['healthy_instances'] as num).toInt(),
      errorInstances: (json['error_instances'] as num).toInt(),
      runningInstances: (json['running_instances'] as num).toInt(),
    );

Map<String, dynamic> _$$RuntimeSystemHealthImplToJson(
        _$RuntimeSystemHealthImpl instance) =>
    <String, dynamic>{
      'total_instances': instance.totalInstances,
      'healthy_instances': instance.healthyInstances,
      'error_instances': instance.errorInstances,
      'running_instances': instance.runningInstances,
    };

_$ConnectorStatesOverviewImpl _$$ConnectorStatesOverviewImplFromJson(
        Map<String, dynamic> json) =>
    _$ConnectorStatesOverviewImpl(
      success: json['success'] as bool,
      overview:
          StateOverview.fromJson(json['overview'] as Map<String, dynamic>),
      runningInstances: (json['running_instances'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$ConnectorStatesOverviewImplToJson(
        _$ConnectorStatesOverviewImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'overview': instance.overview,
      'running_instances': instance.runningInstances,
    };

_$StateOverviewImpl _$$StateOverviewImplFromJson(Map<String, dynamic> json) =>
    _$StateOverviewImpl(
      totalInstances: (json['total_instances'] as num).toInt(),
      runningInstances: (json['running_instances'] as num).toInt(),
      stateDistribution:
          Map<String, int>.from(json['state_distribution'] as Map),
    );

Map<String, dynamic> _$$StateOverviewImplToJson(_$StateOverviewImpl instance) =>
    <String, dynamic>{
      'total_instances': instance.totalInstances,
      'running_instances': instance.runningInstances,
      'state_distribution': instance.stateDistribution,
    };

_$ConnectorApiResponseImpl _$$ConnectorApiResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$ConnectorApiResponseImpl(
      success: json['success'] as bool,
      message: json['message'] as String,
      data: json['data'],
      error: json['error'] as String?,
    );

Map<String, dynamic> _$$ConnectorApiResponseImplToJson(
        _$ConnectorApiResponseImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'message': instance.message,
      'data': instance.data,
      'error': instance.error,
    };

_$DiscoveryResponseImpl _$$DiscoveryResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$DiscoveryResponseImpl(
      success: json['success'] as bool,
      message: json['message'] as String,
      connectors: (json['connectors'] as List<dynamic>?)
              ?.map((e) =>
                  ConnectorDefinition.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$DiscoveryResponseImplToJson(
        _$DiscoveryResponseImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'message': instance.message,
      'connectors': instance.connectors,
    };

_$ConnectorListResponseImpl _$$ConnectorListResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$ConnectorListResponseImpl(
      success: json['success'] as bool,
      connectors: (json['connectors'] as List<dynamic>?)
              ?.map((e) => ConnectorInfo.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      totalCount: (json['total_count'] as num?)?.toInt() ?? 0,
    );

Map<String, dynamic> _$$ConnectorListResponseImplToJson(
        _$ConnectorListResponseImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'connectors': instance.connectors,
      'total_count': instance.totalCount,
    };

_$ConnectorDetailResponseImpl _$$ConnectorDetailResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$ConnectorDetailResponseImpl(
      success: json['success'] as bool,
      connector:
          ConnectorInfo.fromJson(json['connector'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$$ConnectorDetailResponseImplToJson(
        _$ConnectorDetailResponseImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'connector': instance.connector,
    };

_$OperationResponseImpl _$$OperationResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$OperationResponseImpl(
      success: json['success'] as bool,
      message: json['message'] as String,
      connectorId: json['connector_id'] as String,
      state: $enumDecode(_$ConnectorStateEnumMap, json['state']),
      hotReloadApplied: json['hot_reload_applied'] as bool?,
      requiresRestart: json['requires_restart'] as bool?,
      wasRunning: json['was_running'] as bool?,
    );

Map<String, dynamic> _$$OperationResponseImplToJson(
        _$OperationResponseImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'message': instance.message,
      'connector_id': instance.connectorId,
      'state': _$ConnectorStateEnumMap[instance.state]!,
      'hot_reload_applied': instance.hotReloadApplied,
      'requires_restart': instance.requiresRestart,
      'was_running': instance.wasRunning,
    };

_$DiscoveredConnectorInfoImpl _$$DiscoveredConnectorInfoImplFromJson(
        Map<String, dynamic> json) =>
    _$DiscoveredConnectorInfoImpl(
      path: json['path'] as String,
      connectorId: json['connector_id'] as String,
      name: json['name'] as String,
      description: json['description'] as String,
      version: json['version'] as String,
      entryPoint: json['entry_point'] as String,
      isRegistered: json['is_registered'] as bool,
    );

Map<String, dynamic> _$$DiscoveredConnectorInfoImplToJson(
        _$DiscoveredConnectorInfoImpl instance) =>
    <String, dynamic>{
      'path': instance.path,
      'connector_id': instance.connectorId,
      'name': instance.name,
      'description': instance.description,
      'version': instance.version,
      'entry_point': instance.entryPoint,
      'is_registered': instance.isRegistered,
    };

_$DirectoryScanResponseImpl _$$DirectoryScanResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$DirectoryScanResponseImpl(
      success: json['success'] as bool,
      data: json['data'] as Map<String, dynamic>,
      message: json['message'] as String,
    );

Map<String, dynamic> _$$DirectoryScanResponseImplToJson(
        _$DirectoryScanResponseImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'data': instance.data,
      'message': instance.message,
    };

_$ConnectorRegistrationResponseImpl
    _$$ConnectorRegistrationResponseImplFromJson(Map<String, dynamic> json) =>
        _$ConnectorRegistrationResponseImpl(
          success: json['success'] as bool,
          data: json['data'] as Map<String, dynamic>,
          message: json['message'] as String,
        );

Map<String, dynamic> _$$ConnectorRegistrationResponseImplToJson(
        _$ConnectorRegistrationResponseImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'data': instance.data,
      'message': instance.message,
    };
