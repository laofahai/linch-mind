// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'connector_lifecycle_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$ConnectorTypeInfoImpl _$$ConnectorTypeInfoImplFromJson(
        Map<String, dynamic> json) =>
    _$ConnectorTypeInfoImpl(
      typeId: json['type_id'] as String,
      name: json['name'] as String,
      displayName: json['display_name'] as String,
      description: json['description'] as String,
      category: json['category'] as String,
      version: json['version'] as String,
      author: json['author'] as String,
      license: json['license'] as String? ?? '',
      supportsMultipleInstances:
          json['supports_multiple_instances'] as bool? ?? false,
      maxInstancesPerUser:
          (json['max_instances_per_user'] as num?)?.toInt() ?? 1,
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
      instanceTemplates: (json['instance_templates'] as List<dynamic>?)
              ?.map((e) => InstanceTemplate.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$ConnectorTypeInfoImplToJson(
        _$ConnectorTypeInfoImpl instance) =>
    <String, dynamic>{
      'type_id': instance.typeId,
      'name': instance.name,
      'display_name': instance.displayName,
      'description': instance.description,
      'category': instance.category,
      'version': instance.version,
      'author': instance.author,
      'license': instance.license,
      'supports_multiple_instances': instance.supportsMultipleInstances,
      'max_instances_per_user': instance.maxInstancesPerUser,
      'auto_discovery': instance.autoDiscovery,
      'hot_config_reload': instance.hotConfigReload,
      'health_check': instance.healthCheck,
      'entry_point': instance.entryPoint,
      'dependencies': instance.dependencies,
      'permissions': instance.permissions,
      'config_schema': instance.configSchema,
      'default_config': instance.defaultConfig,
      'instance_templates': instance.instanceTemplates,
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

_$ConnectorInstanceInfoImpl _$$ConnectorInstanceInfoImplFromJson(
        Map<String, dynamic> json) =>
    _$ConnectorInstanceInfoImpl(
      instanceId: json['instance_id'] as String,
      displayName: json['display_name'] as String,
      typeId: json['type_id'] as String,
      typeName: json['type_name'] as String? ?? '未知',
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

Map<String, dynamic> _$$ConnectorInstanceInfoImplToJson(
        _$ConnectorInstanceInfoImpl instance) =>
    <String, dynamic>{
      'instance_id': instance.instanceId,
      'display_name': instance.displayName,
      'type_id': instance.typeId,
      'type_name': instance.typeName,
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

_$CreateInstanceRequestImpl _$$CreateInstanceRequestImplFromJson(
        Map<String, dynamic> json) =>
    _$CreateInstanceRequestImpl(
      typeId: json['type_id'] as String,
      displayName: json['display_name'] as String,
      config: json['config'] as Map<String, dynamic>? ?? const {},
      autoStart: json['auto_start'] as bool? ?? true,
      templateId: json['template_id'] as String?,
    );

Map<String, dynamic> _$$CreateInstanceRequestImplToJson(
        _$CreateInstanceRequestImpl instance) =>
    <String, dynamic>{
      'type_id': instance.typeId,
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
      instanceId: json['instance_id'] as String,
      oldState: $enumDecode(_$ConnectorStateEnumMap, json['old_state']),
      newState: $enumDecode(_$ConnectorStateEnumMap, json['new_state']),
    );

Map<String, dynamic> _$$StateChangeEventImplToJson(
        _$StateChangeEventImpl instance) =>
    <String, dynamic>{
      'instance_id': instance.instanceId,
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
      connectorTypes: (json['connector_types'] as List<dynamic>?)
              ?.map(
                  (e) => ConnectorTypeInfo.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$DiscoveryResponseImplToJson(
        _$DiscoveryResponseImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'message': instance.message,
      'connector_types': instance.connectorTypes,
    };

_$InstanceListResponseImpl _$$InstanceListResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$InstanceListResponseImpl(
      success: json['success'] as bool,
      instances: (json['instances'] as List<dynamic>?)
              ?.map((e) =>
                  ConnectorInstanceInfo.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      totalCount: (json['total_count'] as num?)?.toInt() ?? 0,
    );

Map<String, dynamic> _$$InstanceListResponseImplToJson(
        _$InstanceListResponseImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'instances': instance.instances,
      'total_count': instance.totalCount,
    };

_$InstanceDetailResponseImpl _$$InstanceDetailResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$InstanceDetailResponseImpl(
      success: json['success'] as bool,
      instance: ConnectorInstanceDetail.fromJson(
          json['instance'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$$InstanceDetailResponseImplToJson(
        _$InstanceDetailResponseImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'instance': instance.instance,
    };

_$ConnectorInstanceDetailImpl _$$ConnectorInstanceDetailImplFromJson(
        Map<String, dynamic> json) =>
    _$ConnectorInstanceDetailImpl(
      instanceId: json['instance_id'] as String,
      displayName: json['display_name'] as String,
      typeId: json['type_id'] as String,
      config: json['config'] as Map<String, dynamic>,
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
      connectorType: json['connector_type'] == null
          ? null
          : ConnectorTypeInfo.fromJson(
              json['connector_type'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$$ConnectorInstanceDetailImplToJson(
        _$ConnectorInstanceDetailImpl instance) =>
    <String, dynamic>{
      'instance_id': instance.instanceId,
      'display_name': instance.displayName,
      'type_id': instance.typeId,
      'config': instance.config,
      'state': _$ConnectorStateEnumMap[instance.state]!,
      'enabled': instance.enabled,
      'auto_start': instance.autoStart,
      'process_id': instance.processId,
      'last_heartbeat': instance.lastHeartbeat?.toIso8601String(),
      'data_count': instance.dataCount,
      'error_message': instance.errorMessage,
      'created_at': instance.createdAt?.toIso8601String(),
      'updated_at': instance.updatedAt?.toIso8601String(),
      'connector_type': instance.connectorType,
    };

_$OperationResponseImpl _$$OperationResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$OperationResponseImpl(
      success: json['success'] as bool,
      message: json['message'] as String,
      instanceId: json['instance_id'] as String,
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
      'instance_id': instance.instanceId,
      'state': _$ConnectorStateEnumMap[instance.state]!,
      'hot_reload_applied': instance.hotReloadApplied,
      'requires_restart': instance.requiresRestart,
      'was_running': instance.wasRunning,
    };
