// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'connector_lifecycle_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

ConnectorTypeInfo _$ConnectorTypeInfoFromJson(Map<String, dynamic> json) {
  return _ConnectorTypeInfo.fromJson(json);
}

/// @nodoc
mixin _$ConnectorTypeInfo {
  @JsonKey(name: 'type_id')
  String get typeId => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  @JsonKey(name: 'display_name')
  String get displayName => throw _privateConstructorUsedError;
  String get description => throw _privateConstructorUsedError;
  String get category => throw _privateConstructorUsedError;
  String get version => throw _privateConstructorUsedError;
  String get author => throw _privateConstructorUsedError;
  String get license => throw _privateConstructorUsedError;
  @JsonKey(name: 'supports_multiple_instances')
  bool get supportsMultipleInstances => throw _privateConstructorUsedError;
  @JsonKey(name: 'max_instances_per_user')
  int get maxInstancesPerUser => throw _privateConstructorUsedError;
  @JsonKey(name: 'auto_discovery')
  bool get autoDiscovery => throw _privateConstructorUsedError;
  @JsonKey(name: 'hot_config_reload')
  bool get hotConfigReload => throw _privateConstructorUsedError;
  @JsonKey(name: 'health_check')
  bool get healthCheck => throw _privateConstructorUsedError;
  @JsonKey(name: 'entry_point')
  String get entryPoint => throw _privateConstructorUsedError;
  List<String> get dependencies => throw _privateConstructorUsedError;
  List<String> get permissions => throw _privateConstructorUsedError;
  @JsonKey(name: 'config_schema')
  Map<String, dynamic> get configSchema => throw _privateConstructorUsedError;
  @JsonKey(name: 'default_config')
  Map<String, dynamic> get defaultConfig => throw _privateConstructorUsedError;
  @JsonKey(name: 'instance_templates')
  List<InstanceTemplate> get instanceTemplates =>
      throw _privateConstructorUsedError;

  /// Serializes this ConnectorTypeInfo to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ConnectorTypeInfo
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ConnectorTypeInfoCopyWith<ConnectorTypeInfo> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ConnectorTypeInfoCopyWith<$Res> {
  factory $ConnectorTypeInfoCopyWith(
          ConnectorTypeInfo value, $Res Function(ConnectorTypeInfo) then) =
      _$ConnectorTypeInfoCopyWithImpl<$Res, ConnectorTypeInfo>;
  @useResult
  $Res call(
      {@JsonKey(name: 'type_id') String typeId,
      String name,
      @JsonKey(name: 'display_name') String displayName,
      String description,
      String category,
      String version,
      String author,
      String license,
      @JsonKey(name: 'supports_multiple_instances')
      bool supportsMultipleInstances,
      @JsonKey(name: 'max_instances_per_user') int maxInstancesPerUser,
      @JsonKey(name: 'auto_discovery') bool autoDiscovery,
      @JsonKey(name: 'hot_config_reload') bool hotConfigReload,
      @JsonKey(name: 'health_check') bool healthCheck,
      @JsonKey(name: 'entry_point') String entryPoint,
      List<String> dependencies,
      List<String> permissions,
      @JsonKey(name: 'config_schema') Map<String, dynamic> configSchema,
      @JsonKey(name: 'default_config') Map<String, dynamic> defaultConfig,
      @JsonKey(name: 'instance_templates')
      List<InstanceTemplate> instanceTemplates});
}

/// @nodoc
class _$ConnectorTypeInfoCopyWithImpl<$Res, $Val extends ConnectorTypeInfo>
    implements $ConnectorTypeInfoCopyWith<$Res> {
  _$ConnectorTypeInfoCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ConnectorTypeInfo
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? typeId = null,
    Object? name = null,
    Object? displayName = null,
    Object? description = null,
    Object? category = null,
    Object? version = null,
    Object? author = null,
    Object? license = null,
    Object? supportsMultipleInstances = null,
    Object? maxInstancesPerUser = null,
    Object? autoDiscovery = null,
    Object? hotConfigReload = null,
    Object? healthCheck = null,
    Object? entryPoint = null,
    Object? dependencies = null,
    Object? permissions = null,
    Object? configSchema = null,
    Object? defaultConfig = null,
    Object? instanceTemplates = null,
  }) {
    return _then(_value.copyWith(
      typeId: null == typeId
          ? _value.typeId
          : typeId // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: null == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      category: null == category
          ? _value.category
          : category // ignore: cast_nullable_to_non_nullable
              as String,
      version: null == version
          ? _value.version
          : version // ignore: cast_nullable_to_non_nullable
              as String,
      author: null == author
          ? _value.author
          : author // ignore: cast_nullable_to_non_nullable
              as String,
      license: null == license
          ? _value.license
          : license // ignore: cast_nullable_to_non_nullable
              as String,
      supportsMultipleInstances: null == supportsMultipleInstances
          ? _value.supportsMultipleInstances
          : supportsMultipleInstances // ignore: cast_nullable_to_non_nullable
              as bool,
      maxInstancesPerUser: null == maxInstancesPerUser
          ? _value.maxInstancesPerUser
          : maxInstancesPerUser // ignore: cast_nullable_to_non_nullable
              as int,
      autoDiscovery: null == autoDiscovery
          ? _value.autoDiscovery
          : autoDiscovery // ignore: cast_nullable_to_non_nullable
              as bool,
      hotConfigReload: null == hotConfigReload
          ? _value.hotConfigReload
          : hotConfigReload // ignore: cast_nullable_to_non_nullable
              as bool,
      healthCheck: null == healthCheck
          ? _value.healthCheck
          : healthCheck // ignore: cast_nullable_to_non_nullable
              as bool,
      entryPoint: null == entryPoint
          ? _value.entryPoint
          : entryPoint // ignore: cast_nullable_to_non_nullable
              as String,
      dependencies: null == dependencies
          ? _value.dependencies
          : dependencies // ignore: cast_nullable_to_non_nullable
              as List<String>,
      permissions: null == permissions
          ? _value.permissions
          : permissions // ignore: cast_nullable_to_non_nullable
              as List<String>,
      configSchema: null == configSchema
          ? _value.configSchema
          : configSchema // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      defaultConfig: null == defaultConfig
          ? _value.defaultConfig
          : defaultConfig // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      instanceTemplates: null == instanceTemplates
          ? _value.instanceTemplates
          : instanceTemplates // ignore: cast_nullable_to_non_nullable
              as List<InstanceTemplate>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ConnectorTypeInfoImplCopyWith<$Res>
    implements $ConnectorTypeInfoCopyWith<$Res> {
  factory _$$ConnectorTypeInfoImplCopyWith(_$ConnectorTypeInfoImpl value,
          $Res Function(_$ConnectorTypeInfoImpl) then) =
      __$$ConnectorTypeInfoImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'type_id') String typeId,
      String name,
      @JsonKey(name: 'display_name') String displayName,
      String description,
      String category,
      String version,
      String author,
      String license,
      @JsonKey(name: 'supports_multiple_instances')
      bool supportsMultipleInstances,
      @JsonKey(name: 'max_instances_per_user') int maxInstancesPerUser,
      @JsonKey(name: 'auto_discovery') bool autoDiscovery,
      @JsonKey(name: 'hot_config_reload') bool hotConfigReload,
      @JsonKey(name: 'health_check') bool healthCheck,
      @JsonKey(name: 'entry_point') String entryPoint,
      List<String> dependencies,
      List<String> permissions,
      @JsonKey(name: 'config_schema') Map<String, dynamic> configSchema,
      @JsonKey(name: 'default_config') Map<String, dynamic> defaultConfig,
      @JsonKey(name: 'instance_templates')
      List<InstanceTemplate> instanceTemplates});
}

/// @nodoc
class __$$ConnectorTypeInfoImplCopyWithImpl<$Res>
    extends _$ConnectorTypeInfoCopyWithImpl<$Res, _$ConnectorTypeInfoImpl>
    implements _$$ConnectorTypeInfoImplCopyWith<$Res> {
  __$$ConnectorTypeInfoImplCopyWithImpl(_$ConnectorTypeInfoImpl _value,
      $Res Function(_$ConnectorTypeInfoImpl) _then)
      : super(_value, _then);

  /// Create a copy of ConnectorTypeInfo
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? typeId = null,
    Object? name = null,
    Object? displayName = null,
    Object? description = null,
    Object? category = null,
    Object? version = null,
    Object? author = null,
    Object? license = null,
    Object? supportsMultipleInstances = null,
    Object? maxInstancesPerUser = null,
    Object? autoDiscovery = null,
    Object? hotConfigReload = null,
    Object? healthCheck = null,
    Object? entryPoint = null,
    Object? dependencies = null,
    Object? permissions = null,
    Object? configSchema = null,
    Object? defaultConfig = null,
    Object? instanceTemplates = null,
  }) {
    return _then(_$ConnectorTypeInfoImpl(
      typeId: null == typeId
          ? _value.typeId
          : typeId // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: null == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      category: null == category
          ? _value.category
          : category // ignore: cast_nullable_to_non_nullable
              as String,
      version: null == version
          ? _value.version
          : version // ignore: cast_nullable_to_non_nullable
              as String,
      author: null == author
          ? _value.author
          : author // ignore: cast_nullable_to_non_nullable
              as String,
      license: null == license
          ? _value.license
          : license // ignore: cast_nullable_to_non_nullable
              as String,
      supportsMultipleInstances: null == supportsMultipleInstances
          ? _value.supportsMultipleInstances
          : supportsMultipleInstances // ignore: cast_nullable_to_non_nullable
              as bool,
      maxInstancesPerUser: null == maxInstancesPerUser
          ? _value.maxInstancesPerUser
          : maxInstancesPerUser // ignore: cast_nullable_to_non_nullable
              as int,
      autoDiscovery: null == autoDiscovery
          ? _value.autoDiscovery
          : autoDiscovery // ignore: cast_nullable_to_non_nullable
              as bool,
      hotConfigReload: null == hotConfigReload
          ? _value.hotConfigReload
          : hotConfigReload // ignore: cast_nullable_to_non_nullable
              as bool,
      healthCheck: null == healthCheck
          ? _value.healthCheck
          : healthCheck // ignore: cast_nullable_to_non_nullable
              as bool,
      entryPoint: null == entryPoint
          ? _value.entryPoint
          : entryPoint // ignore: cast_nullable_to_non_nullable
              as String,
      dependencies: null == dependencies
          ? _value._dependencies
          : dependencies // ignore: cast_nullable_to_non_nullable
              as List<String>,
      permissions: null == permissions
          ? _value._permissions
          : permissions // ignore: cast_nullable_to_non_nullable
              as List<String>,
      configSchema: null == configSchema
          ? _value._configSchema
          : configSchema // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      defaultConfig: null == defaultConfig
          ? _value._defaultConfig
          : defaultConfig // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      instanceTemplates: null == instanceTemplates
          ? _value._instanceTemplates
          : instanceTemplates // ignore: cast_nullable_to_non_nullable
              as List<InstanceTemplate>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ConnectorTypeInfoImpl implements _ConnectorTypeInfo {
  const _$ConnectorTypeInfoImpl(
      {@JsonKey(name: 'type_id') required this.typeId,
      required this.name,
      @JsonKey(name: 'display_name') required this.displayName,
      required this.description,
      required this.category,
      required this.version,
      required this.author,
      this.license = '',
      @JsonKey(name: 'supports_multiple_instances')
      this.supportsMultipleInstances = false,
      @JsonKey(name: 'max_instances_per_user') this.maxInstancesPerUser = 1,
      @JsonKey(name: 'auto_discovery') this.autoDiscovery = false,
      @JsonKey(name: 'hot_config_reload') this.hotConfigReload = true,
      @JsonKey(name: 'health_check') this.healthCheck = true,
      @JsonKey(name: 'entry_point') this.entryPoint = 'main.py',
      final List<String> dependencies = const [],
      final List<String> permissions = const [],
      @JsonKey(name: 'config_schema')
      final Map<String, dynamic> configSchema = const {},
      @JsonKey(name: 'default_config')
      final Map<String, dynamic> defaultConfig = const {},
      @JsonKey(name: 'instance_templates')
      final List<InstanceTemplate> instanceTemplates = const []})
      : _dependencies = dependencies,
        _permissions = permissions,
        _configSchema = configSchema,
        _defaultConfig = defaultConfig,
        _instanceTemplates = instanceTemplates;

  factory _$ConnectorTypeInfoImpl.fromJson(Map<String, dynamic> json) =>
      _$$ConnectorTypeInfoImplFromJson(json);

  @override
  @JsonKey(name: 'type_id')
  final String typeId;
  @override
  final String name;
  @override
  @JsonKey(name: 'display_name')
  final String displayName;
  @override
  final String description;
  @override
  final String category;
  @override
  final String version;
  @override
  final String author;
  @override
  @JsonKey()
  final String license;
  @override
  @JsonKey(name: 'supports_multiple_instances')
  final bool supportsMultipleInstances;
  @override
  @JsonKey(name: 'max_instances_per_user')
  final int maxInstancesPerUser;
  @override
  @JsonKey(name: 'auto_discovery')
  final bool autoDiscovery;
  @override
  @JsonKey(name: 'hot_config_reload')
  final bool hotConfigReload;
  @override
  @JsonKey(name: 'health_check')
  final bool healthCheck;
  @override
  @JsonKey(name: 'entry_point')
  final String entryPoint;
  final List<String> _dependencies;
  @override
  @JsonKey()
  List<String> get dependencies {
    if (_dependencies is EqualUnmodifiableListView) return _dependencies;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_dependencies);
  }

  final List<String> _permissions;
  @override
  @JsonKey()
  List<String> get permissions {
    if (_permissions is EqualUnmodifiableListView) return _permissions;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_permissions);
  }

  final Map<String, dynamic> _configSchema;
  @override
  @JsonKey(name: 'config_schema')
  Map<String, dynamic> get configSchema {
    if (_configSchema is EqualUnmodifiableMapView) return _configSchema;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_configSchema);
  }

  final Map<String, dynamic> _defaultConfig;
  @override
  @JsonKey(name: 'default_config')
  Map<String, dynamic> get defaultConfig {
    if (_defaultConfig is EqualUnmodifiableMapView) return _defaultConfig;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_defaultConfig);
  }

  final List<InstanceTemplate> _instanceTemplates;
  @override
  @JsonKey(name: 'instance_templates')
  List<InstanceTemplate> get instanceTemplates {
    if (_instanceTemplates is EqualUnmodifiableListView)
      return _instanceTemplates;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_instanceTemplates);
  }

  @override
  String toString() {
    return 'ConnectorTypeInfo(typeId: $typeId, name: $name, displayName: $displayName, description: $description, category: $category, version: $version, author: $author, license: $license, supportsMultipleInstances: $supportsMultipleInstances, maxInstancesPerUser: $maxInstancesPerUser, autoDiscovery: $autoDiscovery, hotConfigReload: $hotConfigReload, healthCheck: $healthCheck, entryPoint: $entryPoint, dependencies: $dependencies, permissions: $permissions, configSchema: $configSchema, defaultConfig: $defaultConfig, instanceTemplates: $instanceTemplates)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ConnectorTypeInfoImpl &&
            (identical(other.typeId, typeId) || other.typeId == typeId) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.displayName, displayName) ||
                other.displayName == displayName) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.category, category) ||
                other.category == category) &&
            (identical(other.version, version) || other.version == version) &&
            (identical(other.author, author) || other.author == author) &&
            (identical(other.license, license) || other.license == license) &&
            (identical(other.supportsMultipleInstances,
                    supportsMultipleInstances) ||
                other.supportsMultipleInstances == supportsMultipleInstances) &&
            (identical(other.maxInstancesPerUser, maxInstancesPerUser) ||
                other.maxInstancesPerUser == maxInstancesPerUser) &&
            (identical(other.autoDiscovery, autoDiscovery) ||
                other.autoDiscovery == autoDiscovery) &&
            (identical(other.hotConfigReload, hotConfigReload) ||
                other.hotConfigReload == hotConfigReload) &&
            (identical(other.healthCheck, healthCheck) ||
                other.healthCheck == healthCheck) &&
            (identical(other.entryPoint, entryPoint) ||
                other.entryPoint == entryPoint) &&
            const DeepCollectionEquality()
                .equals(other._dependencies, _dependencies) &&
            const DeepCollectionEquality()
                .equals(other._permissions, _permissions) &&
            const DeepCollectionEquality()
                .equals(other._configSchema, _configSchema) &&
            const DeepCollectionEquality()
                .equals(other._defaultConfig, _defaultConfig) &&
            const DeepCollectionEquality()
                .equals(other._instanceTemplates, _instanceTemplates));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hashAll([
        runtimeType,
        typeId,
        name,
        displayName,
        description,
        category,
        version,
        author,
        license,
        supportsMultipleInstances,
        maxInstancesPerUser,
        autoDiscovery,
        hotConfigReload,
        healthCheck,
        entryPoint,
        const DeepCollectionEquality().hash(_dependencies),
        const DeepCollectionEquality().hash(_permissions),
        const DeepCollectionEquality().hash(_configSchema),
        const DeepCollectionEquality().hash(_defaultConfig),
        const DeepCollectionEquality().hash(_instanceTemplates)
      ]);

  /// Create a copy of ConnectorTypeInfo
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ConnectorTypeInfoImplCopyWith<_$ConnectorTypeInfoImpl> get copyWith =>
      __$$ConnectorTypeInfoImplCopyWithImpl<_$ConnectorTypeInfoImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ConnectorTypeInfoImplToJson(
      this,
    );
  }
}

abstract class _ConnectorTypeInfo implements ConnectorTypeInfo {
  const factory _ConnectorTypeInfo(
      {@JsonKey(name: 'type_id') required final String typeId,
      required final String name,
      @JsonKey(name: 'display_name') required final String displayName,
      required final String description,
      required final String category,
      required final String version,
      required final String author,
      final String license,
      @JsonKey(name: 'supports_multiple_instances')
      final bool supportsMultipleInstances,
      @JsonKey(name: 'max_instances_per_user') final int maxInstancesPerUser,
      @JsonKey(name: 'auto_discovery') final bool autoDiscovery,
      @JsonKey(name: 'hot_config_reload') final bool hotConfigReload,
      @JsonKey(name: 'health_check') final bool healthCheck,
      @JsonKey(name: 'entry_point') final String entryPoint,
      final List<String> dependencies,
      final List<String> permissions,
      @JsonKey(name: 'config_schema') final Map<String, dynamic> configSchema,
      @JsonKey(name: 'default_config') final Map<String, dynamic> defaultConfig,
      @JsonKey(name: 'instance_templates')
      final List<InstanceTemplate>
          instanceTemplates}) = _$ConnectorTypeInfoImpl;

  factory _ConnectorTypeInfo.fromJson(Map<String, dynamic> json) =
      _$ConnectorTypeInfoImpl.fromJson;

  @override
  @JsonKey(name: 'type_id')
  String get typeId;
  @override
  String get name;
  @override
  @JsonKey(name: 'display_name')
  String get displayName;
  @override
  String get description;
  @override
  String get category;
  @override
  String get version;
  @override
  String get author;
  @override
  String get license;
  @override
  @JsonKey(name: 'supports_multiple_instances')
  bool get supportsMultipleInstances;
  @override
  @JsonKey(name: 'max_instances_per_user')
  int get maxInstancesPerUser;
  @override
  @JsonKey(name: 'auto_discovery')
  bool get autoDiscovery;
  @override
  @JsonKey(name: 'hot_config_reload')
  bool get hotConfigReload;
  @override
  @JsonKey(name: 'health_check')
  bool get healthCheck;
  @override
  @JsonKey(name: 'entry_point')
  String get entryPoint;
  @override
  List<String> get dependencies;
  @override
  List<String> get permissions;
  @override
  @JsonKey(name: 'config_schema')
  Map<String, dynamic> get configSchema;
  @override
  @JsonKey(name: 'default_config')
  Map<String, dynamic> get defaultConfig;
  @override
  @JsonKey(name: 'instance_templates')
  List<InstanceTemplate> get instanceTemplates;

  /// Create a copy of ConnectorTypeInfo
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ConnectorTypeInfoImplCopyWith<_$ConnectorTypeInfoImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

InstanceTemplate _$InstanceTemplateFromJson(Map<String, dynamic> json) {
  return _InstanceTemplate.fromJson(json);
}

/// @nodoc
mixin _$InstanceTemplate {
  String get id => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get description => throw _privateConstructorUsedError;
  Map<String, dynamic> get config => throw _privateConstructorUsedError;

  /// Serializes this InstanceTemplate to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of InstanceTemplate
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $InstanceTemplateCopyWith<InstanceTemplate> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $InstanceTemplateCopyWith<$Res> {
  factory $InstanceTemplateCopyWith(
          InstanceTemplate value, $Res Function(InstanceTemplate) then) =
      _$InstanceTemplateCopyWithImpl<$Res, InstanceTemplate>;
  @useResult
  $Res call(
      {String id,
      String name,
      String description,
      Map<String, dynamic> config});
}

/// @nodoc
class _$InstanceTemplateCopyWithImpl<$Res, $Val extends InstanceTemplate>
    implements $InstanceTemplateCopyWith<$Res> {
  _$InstanceTemplateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of InstanceTemplate
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? description = null,
    Object? config = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      config: null == config
          ? _value.config
          : config // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$InstanceTemplateImplCopyWith<$Res>
    implements $InstanceTemplateCopyWith<$Res> {
  factory _$$InstanceTemplateImplCopyWith(_$InstanceTemplateImpl value,
          $Res Function(_$InstanceTemplateImpl) then) =
      __$$InstanceTemplateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String name,
      String description,
      Map<String, dynamic> config});
}

/// @nodoc
class __$$InstanceTemplateImplCopyWithImpl<$Res>
    extends _$InstanceTemplateCopyWithImpl<$Res, _$InstanceTemplateImpl>
    implements _$$InstanceTemplateImplCopyWith<$Res> {
  __$$InstanceTemplateImplCopyWithImpl(_$InstanceTemplateImpl _value,
      $Res Function(_$InstanceTemplateImpl) _then)
      : super(_value, _then);

  /// Create a copy of InstanceTemplate
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? description = null,
    Object? config = null,
  }) {
    return _then(_$InstanceTemplateImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      config: null == config
          ? _value._config
          : config // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$InstanceTemplateImpl implements _InstanceTemplate {
  const _$InstanceTemplateImpl(
      {required this.id,
      required this.name,
      required this.description,
      final Map<String, dynamic> config = const {}})
      : _config = config;

  factory _$InstanceTemplateImpl.fromJson(Map<String, dynamic> json) =>
      _$$InstanceTemplateImplFromJson(json);

  @override
  final String id;
  @override
  final String name;
  @override
  final String description;
  final Map<String, dynamic> _config;
  @override
  @JsonKey()
  Map<String, dynamic> get config {
    if (_config is EqualUnmodifiableMapView) return _config;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_config);
  }

  @override
  String toString() {
    return 'InstanceTemplate(id: $id, name: $name, description: $description, config: $config)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$InstanceTemplateImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.description, description) ||
                other.description == description) &&
            const DeepCollectionEquality().equals(other._config, _config));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, id, name, description,
      const DeepCollectionEquality().hash(_config));

  /// Create a copy of InstanceTemplate
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$InstanceTemplateImplCopyWith<_$InstanceTemplateImpl> get copyWith =>
      __$$InstanceTemplateImplCopyWithImpl<_$InstanceTemplateImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$InstanceTemplateImplToJson(
      this,
    );
  }
}

abstract class _InstanceTemplate implements InstanceTemplate {
  const factory _InstanceTemplate(
      {required final String id,
      required final String name,
      required final String description,
      final Map<String, dynamic> config}) = _$InstanceTemplateImpl;

  factory _InstanceTemplate.fromJson(Map<String, dynamic> json) =
      _$InstanceTemplateImpl.fromJson;

  @override
  String get id;
  @override
  String get name;
  @override
  String get description;
  @override
  Map<String, dynamic> get config;

  /// Create a copy of InstanceTemplate
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$InstanceTemplateImplCopyWith<_$InstanceTemplateImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ConnectorInstanceInfo _$ConnectorInstanceInfoFromJson(
    Map<String, dynamic> json) {
  return _ConnectorInstanceInfo.fromJson(json);
}

/// @nodoc
mixin _$ConnectorInstanceInfo {
  @JsonKey(name: 'instance_id')
  String get instanceId => throw _privateConstructorUsedError;
  @JsonKey(name: 'display_name')
  String get displayName => throw _privateConstructorUsedError;
  @JsonKey(name: 'type_id')
  String get typeId => throw _privateConstructorUsedError;
  @JsonKey(name: 'type_name')
  String get typeName => throw _privateConstructorUsedError;
  ConnectorState get state => throw _privateConstructorUsedError;
  bool get enabled => throw _privateConstructorUsedError;
  @JsonKey(name: 'auto_start')
  bool get autoStart => throw _privateConstructorUsedError;
  @JsonKey(name: 'process_id')
  int? get processId => throw _privateConstructorUsedError;
  @JsonKey(name: 'last_heartbeat')
  DateTime? get lastHeartbeat => throw _privateConstructorUsedError;
  @JsonKey(name: 'data_count')
  int get dataCount => throw _privateConstructorUsedError;
  @JsonKey(name: 'error_message')
  String? get errorMessage => throw _privateConstructorUsedError;
  @JsonKey(name: 'created_at')
  DateTime? get createdAt => throw _privateConstructorUsedError;
  @JsonKey(name: 'updated_at')
  DateTime? get updatedAt => throw _privateConstructorUsedError;
  Map<String, dynamic> get config => throw _privateConstructorUsedError;

  /// Serializes this ConnectorInstanceInfo to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ConnectorInstanceInfo
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ConnectorInstanceInfoCopyWith<ConnectorInstanceInfo> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ConnectorInstanceInfoCopyWith<$Res> {
  factory $ConnectorInstanceInfoCopyWith(ConnectorInstanceInfo value,
          $Res Function(ConnectorInstanceInfo) then) =
      _$ConnectorInstanceInfoCopyWithImpl<$Res, ConnectorInstanceInfo>;
  @useResult
  $Res call(
      {@JsonKey(name: 'instance_id') String instanceId,
      @JsonKey(name: 'display_name') String displayName,
      @JsonKey(name: 'type_id') String typeId,
      @JsonKey(name: 'type_name') String typeName,
      ConnectorState state,
      bool enabled,
      @JsonKey(name: 'auto_start') bool autoStart,
      @JsonKey(name: 'process_id') int? processId,
      @JsonKey(name: 'last_heartbeat') DateTime? lastHeartbeat,
      @JsonKey(name: 'data_count') int dataCount,
      @JsonKey(name: 'error_message') String? errorMessage,
      @JsonKey(name: 'created_at') DateTime? createdAt,
      @JsonKey(name: 'updated_at') DateTime? updatedAt,
      Map<String, dynamic> config});
}

/// @nodoc
class _$ConnectorInstanceInfoCopyWithImpl<$Res,
        $Val extends ConnectorInstanceInfo>
    implements $ConnectorInstanceInfoCopyWith<$Res> {
  _$ConnectorInstanceInfoCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ConnectorInstanceInfo
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? instanceId = null,
    Object? displayName = null,
    Object? typeId = null,
    Object? typeName = null,
    Object? state = null,
    Object? enabled = null,
    Object? autoStart = null,
    Object? processId = freezed,
    Object? lastHeartbeat = freezed,
    Object? dataCount = null,
    Object? errorMessage = freezed,
    Object? createdAt = freezed,
    Object? updatedAt = freezed,
    Object? config = null,
  }) {
    return _then(_value.copyWith(
      instanceId: null == instanceId
          ? _value.instanceId
          : instanceId // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: null == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String,
      typeId: null == typeId
          ? _value.typeId
          : typeId // ignore: cast_nullable_to_non_nullable
              as String,
      typeName: null == typeName
          ? _value.typeName
          : typeName // ignore: cast_nullable_to_non_nullable
              as String,
      state: null == state
          ? _value.state
          : state // ignore: cast_nullable_to_non_nullable
              as ConnectorState,
      enabled: null == enabled
          ? _value.enabled
          : enabled // ignore: cast_nullable_to_non_nullable
              as bool,
      autoStart: null == autoStart
          ? _value.autoStart
          : autoStart // ignore: cast_nullable_to_non_nullable
              as bool,
      processId: freezed == processId
          ? _value.processId
          : processId // ignore: cast_nullable_to_non_nullable
              as int?,
      lastHeartbeat: freezed == lastHeartbeat
          ? _value.lastHeartbeat
          : lastHeartbeat // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      dataCount: null == dataCount
          ? _value.dataCount
          : dataCount // ignore: cast_nullable_to_non_nullable
              as int,
      errorMessage: freezed == errorMessage
          ? _value.errorMessage
          : errorMessage // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      updatedAt: freezed == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      config: null == config
          ? _value.config
          : config // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ConnectorInstanceInfoImplCopyWith<$Res>
    implements $ConnectorInstanceInfoCopyWith<$Res> {
  factory _$$ConnectorInstanceInfoImplCopyWith(
          _$ConnectorInstanceInfoImpl value,
          $Res Function(_$ConnectorInstanceInfoImpl) then) =
      __$$ConnectorInstanceInfoImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'instance_id') String instanceId,
      @JsonKey(name: 'display_name') String displayName,
      @JsonKey(name: 'type_id') String typeId,
      @JsonKey(name: 'type_name') String typeName,
      ConnectorState state,
      bool enabled,
      @JsonKey(name: 'auto_start') bool autoStart,
      @JsonKey(name: 'process_id') int? processId,
      @JsonKey(name: 'last_heartbeat') DateTime? lastHeartbeat,
      @JsonKey(name: 'data_count') int dataCount,
      @JsonKey(name: 'error_message') String? errorMessage,
      @JsonKey(name: 'created_at') DateTime? createdAt,
      @JsonKey(name: 'updated_at') DateTime? updatedAt,
      Map<String, dynamic> config});
}

/// @nodoc
class __$$ConnectorInstanceInfoImplCopyWithImpl<$Res>
    extends _$ConnectorInstanceInfoCopyWithImpl<$Res,
        _$ConnectorInstanceInfoImpl>
    implements _$$ConnectorInstanceInfoImplCopyWith<$Res> {
  __$$ConnectorInstanceInfoImplCopyWithImpl(_$ConnectorInstanceInfoImpl _value,
      $Res Function(_$ConnectorInstanceInfoImpl) _then)
      : super(_value, _then);

  /// Create a copy of ConnectorInstanceInfo
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? instanceId = null,
    Object? displayName = null,
    Object? typeId = null,
    Object? typeName = null,
    Object? state = null,
    Object? enabled = null,
    Object? autoStart = null,
    Object? processId = freezed,
    Object? lastHeartbeat = freezed,
    Object? dataCount = null,
    Object? errorMessage = freezed,
    Object? createdAt = freezed,
    Object? updatedAt = freezed,
    Object? config = null,
  }) {
    return _then(_$ConnectorInstanceInfoImpl(
      instanceId: null == instanceId
          ? _value.instanceId
          : instanceId // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: null == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String,
      typeId: null == typeId
          ? _value.typeId
          : typeId // ignore: cast_nullable_to_non_nullable
              as String,
      typeName: null == typeName
          ? _value.typeName
          : typeName // ignore: cast_nullable_to_non_nullable
              as String,
      state: null == state
          ? _value.state
          : state // ignore: cast_nullable_to_non_nullable
              as ConnectorState,
      enabled: null == enabled
          ? _value.enabled
          : enabled // ignore: cast_nullable_to_non_nullable
              as bool,
      autoStart: null == autoStart
          ? _value.autoStart
          : autoStart // ignore: cast_nullable_to_non_nullable
              as bool,
      processId: freezed == processId
          ? _value.processId
          : processId // ignore: cast_nullable_to_non_nullable
              as int?,
      lastHeartbeat: freezed == lastHeartbeat
          ? _value.lastHeartbeat
          : lastHeartbeat // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      dataCount: null == dataCount
          ? _value.dataCount
          : dataCount // ignore: cast_nullable_to_non_nullable
              as int,
      errorMessage: freezed == errorMessage
          ? _value.errorMessage
          : errorMessage // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      updatedAt: freezed == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      config: null == config
          ? _value._config
          : config // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ConnectorInstanceInfoImpl implements _ConnectorInstanceInfo {
  const _$ConnectorInstanceInfoImpl(
      {@JsonKey(name: 'instance_id') required this.instanceId,
      @JsonKey(name: 'display_name') required this.displayName,
      @JsonKey(name: 'type_id') required this.typeId,
      @JsonKey(name: 'type_name') this.typeName = '未知',
      required this.state,
      this.enabled = true,
      @JsonKey(name: 'auto_start') this.autoStart = true,
      @JsonKey(name: 'process_id') this.processId,
      @JsonKey(name: 'last_heartbeat') this.lastHeartbeat,
      @JsonKey(name: 'data_count') this.dataCount = 0,
      @JsonKey(name: 'error_message') this.errorMessage,
      @JsonKey(name: 'created_at') this.createdAt,
      @JsonKey(name: 'updated_at') this.updatedAt,
      final Map<String, dynamic> config = const {}})
      : _config = config;

  factory _$ConnectorInstanceInfoImpl.fromJson(Map<String, dynamic> json) =>
      _$$ConnectorInstanceInfoImplFromJson(json);

  @override
  @JsonKey(name: 'instance_id')
  final String instanceId;
  @override
  @JsonKey(name: 'display_name')
  final String displayName;
  @override
  @JsonKey(name: 'type_id')
  final String typeId;
  @override
  @JsonKey(name: 'type_name')
  final String typeName;
  @override
  final ConnectorState state;
  @override
  @JsonKey()
  final bool enabled;
  @override
  @JsonKey(name: 'auto_start')
  final bool autoStart;
  @override
  @JsonKey(name: 'process_id')
  final int? processId;
  @override
  @JsonKey(name: 'last_heartbeat')
  final DateTime? lastHeartbeat;
  @override
  @JsonKey(name: 'data_count')
  final int dataCount;
  @override
  @JsonKey(name: 'error_message')
  final String? errorMessage;
  @override
  @JsonKey(name: 'created_at')
  final DateTime? createdAt;
  @override
  @JsonKey(name: 'updated_at')
  final DateTime? updatedAt;
  final Map<String, dynamic> _config;
  @override
  @JsonKey()
  Map<String, dynamic> get config {
    if (_config is EqualUnmodifiableMapView) return _config;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_config);
  }

  @override
  String toString() {
    return 'ConnectorInstanceInfo(instanceId: $instanceId, displayName: $displayName, typeId: $typeId, typeName: $typeName, state: $state, enabled: $enabled, autoStart: $autoStart, processId: $processId, lastHeartbeat: $lastHeartbeat, dataCount: $dataCount, errorMessage: $errorMessage, createdAt: $createdAt, updatedAt: $updatedAt, config: $config)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ConnectorInstanceInfoImpl &&
            (identical(other.instanceId, instanceId) ||
                other.instanceId == instanceId) &&
            (identical(other.displayName, displayName) ||
                other.displayName == displayName) &&
            (identical(other.typeId, typeId) || other.typeId == typeId) &&
            (identical(other.typeName, typeName) ||
                other.typeName == typeName) &&
            (identical(other.state, state) || other.state == state) &&
            (identical(other.enabled, enabled) || other.enabled == enabled) &&
            (identical(other.autoStart, autoStart) ||
                other.autoStart == autoStart) &&
            (identical(other.processId, processId) ||
                other.processId == processId) &&
            (identical(other.lastHeartbeat, lastHeartbeat) ||
                other.lastHeartbeat == lastHeartbeat) &&
            (identical(other.dataCount, dataCount) ||
                other.dataCount == dataCount) &&
            (identical(other.errorMessage, errorMessage) ||
                other.errorMessage == errorMessage) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt) &&
            const DeepCollectionEquality().equals(other._config, _config));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      instanceId,
      displayName,
      typeId,
      typeName,
      state,
      enabled,
      autoStart,
      processId,
      lastHeartbeat,
      dataCount,
      errorMessage,
      createdAt,
      updatedAt,
      const DeepCollectionEquality().hash(_config));

  /// Create a copy of ConnectorInstanceInfo
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ConnectorInstanceInfoImplCopyWith<_$ConnectorInstanceInfoImpl>
      get copyWith => __$$ConnectorInstanceInfoImplCopyWithImpl<
          _$ConnectorInstanceInfoImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ConnectorInstanceInfoImplToJson(
      this,
    );
  }
}

abstract class _ConnectorInstanceInfo implements ConnectorInstanceInfo {
  const factory _ConnectorInstanceInfo(
      {@JsonKey(name: 'instance_id') required final String instanceId,
      @JsonKey(name: 'display_name') required final String displayName,
      @JsonKey(name: 'type_id') required final String typeId,
      @JsonKey(name: 'type_name') final String typeName,
      required final ConnectorState state,
      final bool enabled,
      @JsonKey(name: 'auto_start') final bool autoStart,
      @JsonKey(name: 'process_id') final int? processId,
      @JsonKey(name: 'last_heartbeat') final DateTime? lastHeartbeat,
      @JsonKey(name: 'data_count') final int dataCount,
      @JsonKey(name: 'error_message') final String? errorMessage,
      @JsonKey(name: 'created_at') final DateTime? createdAt,
      @JsonKey(name: 'updated_at') final DateTime? updatedAt,
      final Map<String, dynamic> config}) = _$ConnectorInstanceInfoImpl;

  factory _ConnectorInstanceInfo.fromJson(Map<String, dynamic> json) =
      _$ConnectorInstanceInfoImpl.fromJson;

  @override
  @JsonKey(name: 'instance_id')
  String get instanceId;
  @override
  @JsonKey(name: 'display_name')
  String get displayName;
  @override
  @JsonKey(name: 'type_id')
  String get typeId;
  @override
  @JsonKey(name: 'type_name')
  String get typeName;
  @override
  ConnectorState get state;
  @override
  bool get enabled;
  @override
  @JsonKey(name: 'auto_start')
  bool get autoStart;
  @override
  @JsonKey(name: 'process_id')
  int? get processId;
  @override
  @JsonKey(name: 'last_heartbeat')
  DateTime? get lastHeartbeat;
  @override
  @JsonKey(name: 'data_count')
  int get dataCount;
  @override
  @JsonKey(name: 'error_message')
  String? get errorMessage;
  @override
  @JsonKey(name: 'created_at')
  DateTime? get createdAt;
  @override
  @JsonKey(name: 'updated_at')
  DateTime? get updatedAt;
  @override
  Map<String, dynamic> get config;

  /// Create a copy of ConnectorInstanceInfo
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ConnectorInstanceInfoImplCopyWith<_$ConnectorInstanceInfoImpl>
      get copyWith => throw _privateConstructorUsedError;
}

CreateInstanceRequest _$CreateInstanceRequestFromJson(
    Map<String, dynamic> json) {
  return _CreateInstanceRequest.fromJson(json);
}

/// @nodoc
mixin _$CreateInstanceRequest {
  @JsonKey(name: 'type_id')
  String get typeId => throw _privateConstructorUsedError;
  @JsonKey(name: 'display_name')
  String get displayName => throw _privateConstructorUsedError;
  Map<String, dynamic> get config => throw _privateConstructorUsedError;
  @JsonKey(name: 'auto_start')
  bool get autoStart => throw _privateConstructorUsedError;
  @JsonKey(name: 'template_id')
  String? get templateId => throw _privateConstructorUsedError;

  /// Serializes this CreateInstanceRequest to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CreateInstanceRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CreateInstanceRequestCopyWith<CreateInstanceRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CreateInstanceRequestCopyWith<$Res> {
  factory $CreateInstanceRequestCopyWith(CreateInstanceRequest value,
          $Res Function(CreateInstanceRequest) then) =
      _$CreateInstanceRequestCopyWithImpl<$Res, CreateInstanceRequest>;
  @useResult
  $Res call(
      {@JsonKey(name: 'type_id') String typeId,
      @JsonKey(name: 'display_name') String displayName,
      Map<String, dynamic> config,
      @JsonKey(name: 'auto_start') bool autoStart,
      @JsonKey(name: 'template_id') String? templateId});
}

/// @nodoc
class _$CreateInstanceRequestCopyWithImpl<$Res,
        $Val extends CreateInstanceRequest>
    implements $CreateInstanceRequestCopyWith<$Res> {
  _$CreateInstanceRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CreateInstanceRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? typeId = null,
    Object? displayName = null,
    Object? config = null,
    Object? autoStart = null,
    Object? templateId = freezed,
  }) {
    return _then(_value.copyWith(
      typeId: null == typeId
          ? _value.typeId
          : typeId // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: null == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String,
      config: null == config
          ? _value.config
          : config // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      autoStart: null == autoStart
          ? _value.autoStart
          : autoStart // ignore: cast_nullable_to_non_nullable
              as bool,
      templateId: freezed == templateId
          ? _value.templateId
          : templateId // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$CreateInstanceRequestImplCopyWith<$Res>
    implements $CreateInstanceRequestCopyWith<$Res> {
  factory _$$CreateInstanceRequestImplCopyWith(
          _$CreateInstanceRequestImpl value,
          $Res Function(_$CreateInstanceRequestImpl) then) =
      __$$CreateInstanceRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'type_id') String typeId,
      @JsonKey(name: 'display_name') String displayName,
      Map<String, dynamic> config,
      @JsonKey(name: 'auto_start') bool autoStart,
      @JsonKey(name: 'template_id') String? templateId});
}

/// @nodoc
class __$$CreateInstanceRequestImplCopyWithImpl<$Res>
    extends _$CreateInstanceRequestCopyWithImpl<$Res,
        _$CreateInstanceRequestImpl>
    implements _$$CreateInstanceRequestImplCopyWith<$Res> {
  __$$CreateInstanceRequestImplCopyWithImpl(_$CreateInstanceRequestImpl _value,
      $Res Function(_$CreateInstanceRequestImpl) _then)
      : super(_value, _then);

  /// Create a copy of CreateInstanceRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? typeId = null,
    Object? displayName = null,
    Object? config = null,
    Object? autoStart = null,
    Object? templateId = freezed,
  }) {
    return _then(_$CreateInstanceRequestImpl(
      typeId: null == typeId
          ? _value.typeId
          : typeId // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: null == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String,
      config: null == config
          ? _value._config
          : config // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      autoStart: null == autoStart
          ? _value.autoStart
          : autoStart // ignore: cast_nullable_to_non_nullable
              as bool,
      templateId: freezed == templateId
          ? _value.templateId
          : templateId // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CreateInstanceRequestImpl implements _CreateInstanceRequest {
  const _$CreateInstanceRequestImpl(
      {@JsonKey(name: 'type_id') required this.typeId,
      @JsonKey(name: 'display_name') required this.displayName,
      final Map<String, dynamic> config = const {},
      @JsonKey(name: 'auto_start') this.autoStart = true,
      @JsonKey(name: 'template_id') this.templateId})
      : _config = config;

  factory _$CreateInstanceRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$CreateInstanceRequestImplFromJson(json);

  @override
  @JsonKey(name: 'type_id')
  final String typeId;
  @override
  @JsonKey(name: 'display_name')
  final String displayName;
  final Map<String, dynamic> _config;
  @override
  @JsonKey()
  Map<String, dynamic> get config {
    if (_config is EqualUnmodifiableMapView) return _config;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_config);
  }

  @override
  @JsonKey(name: 'auto_start')
  final bool autoStart;
  @override
  @JsonKey(name: 'template_id')
  final String? templateId;

  @override
  String toString() {
    return 'CreateInstanceRequest(typeId: $typeId, displayName: $displayName, config: $config, autoStart: $autoStart, templateId: $templateId)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CreateInstanceRequestImpl &&
            (identical(other.typeId, typeId) || other.typeId == typeId) &&
            (identical(other.displayName, displayName) ||
                other.displayName == displayName) &&
            const DeepCollectionEquality().equals(other._config, _config) &&
            (identical(other.autoStart, autoStart) ||
                other.autoStart == autoStart) &&
            (identical(other.templateId, templateId) ||
                other.templateId == templateId));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, typeId, displayName,
      const DeepCollectionEquality().hash(_config), autoStart, templateId);

  /// Create a copy of CreateInstanceRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CreateInstanceRequestImplCopyWith<_$CreateInstanceRequestImpl>
      get copyWith => __$$CreateInstanceRequestImplCopyWithImpl<
          _$CreateInstanceRequestImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CreateInstanceRequestImplToJson(
      this,
    );
  }
}

abstract class _CreateInstanceRequest implements CreateInstanceRequest {
  const factory _CreateInstanceRequest(
          {@JsonKey(name: 'type_id') required final String typeId,
          @JsonKey(name: 'display_name') required final String displayName,
          final Map<String, dynamic> config,
          @JsonKey(name: 'auto_start') final bool autoStart,
          @JsonKey(name: 'template_id') final String? templateId}) =
      _$CreateInstanceRequestImpl;

  factory _CreateInstanceRequest.fromJson(Map<String, dynamic> json) =
      _$CreateInstanceRequestImpl.fromJson;

  @override
  @JsonKey(name: 'type_id')
  String get typeId;
  @override
  @JsonKey(name: 'display_name')
  String get displayName;
  @override
  Map<String, dynamic> get config;
  @override
  @JsonKey(name: 'auto_start')
  bool get autoStart;
  @override
  @JsonKey(name: 'template_id')
  String? get templateId;

  /// Create a copy of CreateInstanceRequest
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CreateInstanceRequestImplCopyWith<_$CreateInstanceRequestImpl>
      get copyWith => throw _privateConstructorUsedError;
}

UpdateConfigRequest _$UpdateConfigRequestFromJson(Map<String, dynamic> json) {
  return _UpdateConfigRequest.fromJson(json);
}

/// @nodoc
mixin _$UpdateConfigRequest {
  Map<String, dynamic> get config => throw _privateConstructorUsedError;

  /// Serializes this UpdateConfigRequest to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of UpdateConfigRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $UpdateConfigRequestCopyWith<UpdateConfigRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $UpdateConfigRequestCopyWith<$Res> {
  factory $UpdateConfigRequestCopyWith(
          UpdateConfigRequest value, $Res Function(UpdateConfigRequest) then) =
      _$UpdateConfigRequestCopyWithImpl<$Res, UpdateConfigRequest>;
  @useResult
  $Res call({Map<String, dynamic> config});
}

/// @nodoc
class _$UpdateConfigRequestCopyWithImpl<$Res, $Val extends UpdateConfigRequest>
    implements $UpdateConfigRequestCopyWith<$Res> {
  _$UpdateConfigRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of UpdateConfigRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? config = null,
  }) {
    return _then(_value.copyWith(
      config: null == config
          ? _value.config
          : config // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$UpdateConfigRequestImplCopyWith<$Res>
    implements $UpdateConfigRequestCopyWith<$Res> {
  factory _$$UpdateConfigRequestImplCopyWith(_$UpdateConfigRequestImpl value,
          $Res Function(_$UpdateConfigRequestImpl) then) =
      __$$UpdateConfigRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({Map<String, dynamic> config});
}

/// @nodoc
class __$$UpdateConfigRequestImplCopyWithImpl<$Res>
    extends _$UpdateConfigRequestCopyWithImpl<$Res, _$UpdateConfigRequestImpl>
    implements _$$UpdateConfigRequestImplCopyWith<$Res> {
  __$$UpdateConfigRequestImplCopyWithImpl(_$UpdateConfigRequestImpl _value,
      $Res Function(_$UpdateConfigRequestImpl) _then)
      : super(_value, _then);

  /// Create a copy of UpdateConfigRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? config = null,
  }) {
    return _then(_$UpdateConfigRequestImpl(
      config: null == config
          ? _value._config
          : config // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$UpdateConfigRequestImpl implements _UpdateConfigRequest {
  const _$UpdateConfigRequestImpl({required final Map<String, dynamic> config})
      : _config = config;

  factory _$UpdateConfigRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$UpdateConfigRequestImplFromJson(json);

  final Map<String, dynamic> _config;
  @override
  Map<String, dynamic> get config {
    if (_config is EqualUnmodifiableMapView) return _config;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_config);
  }

  @override
  String toString() {
    return 'UpdateConfigRequest(config: $config)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$UpdateConfigRequestImpl &&
            const DeepCollectionEquality().equals(other._config, _config));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, const DeepCollectionEquality().hash(_config));

  /// Create a copy of UpdateConfigRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$UpdateConfigRequestImplCopyWith<_$UpdateConfigRequestImpl> get copyWith =>
      __$$UpdateConfigRequestImplCopyWithImpl<_$UpdateConfigRequestImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$UpdateConfigRequestImplToJson(
      this,
    );
  }
}

abstract class _UpdateConfigRequest implements UpdateConfigRequest {
  const factory _UpdateConfigRequest(
      {required final Map<String, dynamic> config}) = _$UpdateConfigRequestImpl;

  factory _UpdateConfigRequest.fromJson(Map<String, dynamic> json) =
      _$UpdateConfigRequestImpl.fromJson;

  @override
  Map<String, dynamic> get config;

  /// Create a copy of UpdateConfigRequest
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$UpdateConfigRequestImplCopyWith<_$UpdateConfigRequestImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ConnectorEvent _$ConnectorEventFromJson(Map<String, dynamic> json) {
  return _ConnectorEvent.fromJson(json);
}

/// @nodoc
mixin _$ConnectorEvent {
  String get event => throw _privateConstructorUsedError;
  DateTime get timestamp => throw _privateConstructorUsedError;
  Map<String, dynamic> get data => throw _privateConstructorUsedError;

  /// Serializes this ConnectorEvent to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ConnectorEvent
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ConnectorEventCopyWith<ConnectorEvent> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ConnectorEventCopyWith<$Res> {
  factory $ConnectorEventCopyWith(
          ConnectorEvent value, $Res Function(ConnectorEvent) then) =
      _$ConnectorEventCopyWithImpl<$Res, ConnectorEvent>;
  @useResult
  $Res call({String event, DateTime timestamp, Map<String, dynamic> data});
}

/// @nodoc
class _$ConnectorEventCopyWithImpl<$Res, $Val extends ConnectorEvent>
    implements $ConnectorEventCopyWith<$Res> {
  _$ConnectorEventCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ConnectorEvent
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? event = null,
    Object? timestamp = null,
    Object? data = null,
  }) {
    return _then(_value.copyWith(
      event: null == event
          ? _value.event
          : event // ignore: cast_nullable_to_non_nullable
              as String,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      data: null == data
          ? _value.data
          : data // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ConnectorEventImplCopyWith<$Res>
    implements $ConnectorEventCopyWith<$Res> {
  factory _$$ConnectorEventImplCopyWith(_$ConnectorEventImpl value,
          $Res Function(_$ConnectorEventImpl) then) =
      __$$ConnectorEventImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String event, DateTime timestamp, Map<String, dynamic> data});
}

/// @nodoc
class __$$ConnectorEventImplCopyWithImpl<$Res>
    extends _$ConnectorEventCopyWithImpl<$Res, _$ConnectorEventImpl>
    implements _$$ConnectorEventImplCopyWith<$Res> {
  __$$ConnectorEventImplCopyWithImpl(
      _$ConnectorEventImpl _value, $Res Function(_$ConnectorEventImpl) _then)
      : super(_value, _then);

  /// Create a copy of ConnectorEvent
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? event = null,
    Object? timestamp = null,
    Object? data = null,
  }) {
    return _then(_$ConnectorEventImpl(
      event: null == event
          ? _value.event
          : event // ignore: cast_nullable_to_non_nullable
              as String,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      data: null == data
          ? _value._data
          : data // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ConnectorEventImpl implements _ConnectorEvent {
  const _$ConnectorEventImpl(
      {required this.event,
      required this.timestamp,
      required final Map<String, dynamic> data})
      : _data = data;

  factory _$ConnectorEventImpl.fromJson(Map<String, dynamic> json) =>
      _$$ConnectorEventImplFromJson(json);

  @override
  final String event;
  @override
  final DateTime timestamp;
  final Map<String, dynamic> _data;
  @override
  Map<String, dynamic> get data {
    if (_data is EqualUnmodifiableMapView) return _data;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_data);
  }

  @override
  String toString() {
    return 'ConnectorEvent(event: $event, timestamp: $timestamp, data: $data)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ConnectorEventImpl &&
            (identical(other.event, event) || other.event == event) &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp) &&
            const DeepCollectionEquality().equals(other._data, _data));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, event, timestamp,
      const DeepCollectionEquality().hash(_data));

  /// Create a copy of ConnectorEvent
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ConnectorEventImplCopyWith<_$ConnectorEventImpl> get copyWith =>
      __$$ConnectorEventImplCopyWithImpl<_$ConnectorEventImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ConnectorEventImplToJson(
      this,
    );
  }
}

abstract class _ConnectorEvent implements ConnectorEvent {
  const factory _ConnectorEvent(
      {required final String event,
      required final DateTime timestamp,
      required final Map<String, dynamic> data}) = _$ConnectorEventImpl;

  factory _ConnectorEvent.fromJson(Map<String, dynamic> json) =
      _$ConnectorEventImpl.fromJson;

  @override
  String get event;
  @override
  DateTime get timestamp;
  @override
  Map<String, dynamic> get data;

  /// Create a copy of ConnectorEvent
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ConnectorEventImplCopyWith<_$ConnectorEventImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

StateChangeEvent _$StateChangeEventFromJson(Map<String, dynamic> json) {
  return _StateChangeEvent.fromJson(json);
}

/// @nodoc
mixin _$StateChangeEvent {
  @JsonKey(name: 'instance_id')
  String get instanceId => throw _privateConstructorUsedError;
  @JsonKey(name: 'old_state')
  ConnectorState get oldState => throw _privateConstructorUsedError;
  @JsonKey(name: 'new_state')
  ConnectorState get newState => throw _privateConstructorUsedError;

  /// Serializes this StateChangeEvent to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of StateChangeEvent
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $StateChangeEventCopyWith<StateChangeEvent> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $StateChangeEventCopyWith<$Res> {
  factory $StateChangeEventCopyWith(
          StateChangeEvent value, $Res Function(StateChangeEvent) then) =
      _$StateChangeEventCopyWithImpl<$Res, StateChangeEvent>;
  @useResult
  $Res call(
      {@JsonKey(name: 'instance_id') String instanceId,
      @JsonKey(name: 'old_state') ConnectorState oldState,
      @JsonKey(name: 'new_state') ConnectorState newState});
}

/// @nodoc
class _$StateChangeEventCopyWithImpl<$Res, $Val extends StateChangeEvent>
    implements $StateChangeEventCopyWith<$Res> {
  _$StateChangeEventCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of StateChangeEvent
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? instanceId = null,
    Object? oldState = null,
    Object? newState = null,
  }) {
    return _then(_value.copyWith(
      instanceId: null == instanceId
          ? _value.instanceId
          : instanceId // ignore: cast_nullable_to_non_nullable
              as String,
      oldState: null == oldState
          ? _value.oldState
          : oldState // ignore: cast_nullable_to_non_nullable
              as ConnectorState,
      newState: null == newState
          ? _value.newState
          : newState // ignore: cast_nullable_to_non_nullable
              as ConnectorState,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$StateChangeEventImplCopyWith<$Res>
    implements $StateChangeEventCopyWith<$Res> {
  factory _$$StateChangeEventImplCopyWith(_$StateChangeEventImpl value,
          $Res Function(_$StateChangeEventImpl) then) =
      __$$StateChangeEventImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'instance_id') String instanceId,
      @JsonKey(name: 'old_state') ConnectorState oldState,
      @JsonKey(name: 'new_state') ConnectorState newState});
}

/// @nodoc
class __$$StateChangeEventImplCopyWithImpl<$Res>
    extends _$StateChangeEventCopyWithImpl<$Res, _$StateChangeEventImpl>
    implements _$$StateChangeEventImplCopyWith<$Res> {
  __$$StateChangeEventImplCopyWithImpl(_$StateChangeEventImpl _value,
      $Res Function(_$StateChangeEventImpl) _then)
      : super(_value, _then);

  /// Create a copy of StateChangeEvent
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? instanceId = null,
    Object? oldState = null,
    Object? newState = null,
  }) {
    return _then(_$StateChangeEventImpl(
      instanceId: null == instanceId
          ? _value.instanceId
          : instanceId // ignore: cast_nullable_to_non_nullable
              as String,
      oldState: null == oldState
          ? _value.oldState
          : oldState // ignore: cast_nullable_to_non_nullable
              as ConnectorState,
      newState: null == newState
          ? _value.newState
          : newState // ignore: cast_nullable_to_non_nullable
              as ConnectorState,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$StateChangeEventImpl implements _StateChangeEvent {
  const _$StateChangeEventImpl(
      {@JsonKey(name: 'instance_id') required this.instanceId,
      @JsonKey(name: 'old_state') required this.oldState,
      @JsonKey(name: 'new_state') required this.newState});

  factory _$StateChangeEventImpl.fromJson(Map<String, dynamic> json) =>
      _$$StateChangeEventImplFromJson(json);

  @override
  @JsonKey(name: 'instance_id')
  final String instanceId;
  @override
  @JsonKey(name: 'old_state')
  final ConnectorState oldState;
  @override
  @JsonKey(name: 'new_state')
  final ConnectorState newState;

  @override
  String toString() {
    return 'StateChangeEvent(instanceId: $instanceId, oldState: $oldState, newState: $newState)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$StateChangeEventImpl &&
            (identical(other.instanceId, instanceId) ||
                other.instanceId == instanceId) &&
            (identical(other.oldState, oldState) ||
                other.oldState == oldState) &&
            (identical(other.newState, newState) ||
                other.newState == newState));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, instanceId, oldState, newState);

  /// Create a copy of StateChangeEvent
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$StateChangeEventImplCopyWith<_$StateChangeEventImpl> get copyWith =>
      __$$StateChangeEventImplCopyWithImpl<_$StateChangeEventImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$StateChangeEventImplToJson(
      this,
    );
  }
}

abstract class _StateChangeEvent implements StateChangeEvent {
  const factory _StateChangeEvent(
          {@JsonKey(name: 'instance_id') required final String instanceId,
          @JsonKey(name: 'old_state') required final ConnectorState oldState,
          @JsonKey(name: 'new_state') required final ConnectorState newState}) =
      _$StateChangeEventImpl;

  factory _StateChangeEvent.fromJson(Map<String, dynamic> json) =
      _$StateChangeEventImpl.fromJson;

  @override
  @JsonKey(name: 'instance_id')
  String get instanceId;
  @override
  @JsonKey(name: 'old_state')
  ConnectorState get oldState;
  @override
  @JsonKey(name: 'new_state')
  ConnectorState get newState;

  /// Create a copy of StateChangeEvent
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$StateChangeEventImplCopyWith<_$StateChangeEventImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ConnectorHealthResponse _$ConnectorHealthResponseFromJson(
    Map<String, dynamic> json) {
  return _ConnectorHealthResponse.fromJson(json);
}

/// @nodoc
mixin _$ConnectorHealthResponse {
  bool get success => throw _privateConstructorUsedError;
  HealthStatus get health => throw _privateConstructorUsedError;

  /// Serializes this ConnectorHealthResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ConnectorHealthResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ConnectorHealthResponseCopyWith<ConnectorHealthResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ConnectorHealthResponseCopyWith<$Res> {
  factory $ConnectorHealthResponseCopyWith(ConnectorHealthResponse value,
          $Res Function(ConnectorHealthResponse) then) =
      _$ConnectorHealthResponseCopyWithImpl<$Res, ConnectorHealthResponse>;
  @useResult
  $Res call({bool success, HealthStatus health});

  $HealthStatusCopyWith<$Res> get health;
}

/// @nodoc
class _$ConnectorHealthResponseCopyWithImpl<$Res,
        $Val extends ConnectorHealthResponse>
    implements $ConnectorHealthResponseCopyWith<$Res> {
  _$ConnectorHealthResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ConnectorHealthResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? health = null,
  }) {
    return _then(_value.copyWith(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      health: null == health
          ? _value.health
          : health // ignore: cast_nullable_to_non_nullable
              as HealthStatus,
    ) as $Val);
  }

  /// Create a copy of ConnectorHealthResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $HealthStatusCopyWith<$Res> get health {
    return $HealthStatusCopyWith<$Res>(_value.health, (value) {
      return _then(_value.copyWith(health: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$ConnectorHealthResponseImplCopyWith<$Res>
    implements $ConnectorHealthResponseCopyWith<$Res> {
  factory _$$ConnectorHealthResponseImplCopyWith(
          _$ConnectorHealthResponseImpl value,
          $Res Function(_$ConnectorHealthResponseImpl) then) =
      __$$ConnectorHealthResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({bool success, HealthStatus health});

  @override
  $HealthStatusCopyWith<$Res> get health;
}

/// @nodoc
class __$$ConnectorHealthResponseImplCopyWithImpl<$Res>
    extends _$ConnectorHealthResponseCopyWithImpl<$Res,
        _$ConnectorHealthResponseImpl>
    implements _$$ConnectorHealthResponseImplCopyWith<$Res> {
  __$$ConnectorHealthResponseImplCopyWithImpl(
      _$ConnectorHealthResponseImpl _value,
      $Res Function(_$ConnectorHealthResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of ConnectorHealthResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? health = null,
  }) {
    return _then(_$ConnectorHealthResponseImpl(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      health: null == health
          ? _value.health
          : health // ignore: cast_nullable_to_non_nullable
              as HealthStatus,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ConnectorHealthResponseImpl implements _ConnectorHealthResponse {
  const _$ConnectorHealthResponseImpl(
      {required this.success, required this.health});

  factory _$ConnectorHealthResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$ConnectorHealthResponseImplFromJson(json);

  @override
  final bool success;
  @override
  final HealthStatus health;

  @override
  String toString() {
    return 'ConnectorHealthResponse(success: $success, health: $health)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ConnectorHealthResponseImpl &&
            (identical(other.success, success) || other.success == success) &&
            (identical(other.health, health) || other.health == health));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, success, health);

  /// Create a copy of ConnectorHealthResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ConnectorHealthResponseImplCopyWith<_$ConnectorHealthResponseImpl>
      get copyWith => __$$ConnectorHealthResponseImplCopyWithImpl<
          _$ConnectorHealthResponseImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ConnectorHealthResponseImplToJson(
      this,
    );
  }
}

abstract class _ConnectorHealthResponse implements ConnectorHealthResponse {
  const factory _ConnectorHealthResponse(
      {required final bool success,
      required final HealthStatus health}) = _$ConnectorHealthResponseImpl;

  factory _ConnectorHealthResponse.fromJson(Map<String, dynamic> json) =
      _$ConnectorHealthResponseImpl.fromJson;

  @override
  bool get success;
  @override
  HealthStatus get health;

  /// Create a copy of ConnectorHealthResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ConnectorHealthResponseImplCopyWith<_$ConnectorHealthResponseImpl>
      get copyWith => throw _privateConstructorUsedError;
}

HealthStatus _$HealthStatusFromJson(Map<String, dynamic> json) {
  return _HealthStatus.fromJson(json);
}

/// @nodoc
mixin _$HealthStatus {
  @JsonKey(name: 'overall_score')
  double get overallScore => throw _privateConstructorUsedError;
  String get status =>
      throw _privateConstructorUsedError; // healthy, degraded, unhealthy
  @JsonKey(name: 'config_system')
  ConfigSystemHealth get configSystem => throw _privateConstructorUsedError;
  @JsonKey(name: 'runtime_system')
  RuntimeSystemHealth get runtimeSystem => throw _privateConstructorUsedError;

  /// Serializes this HealthStatus to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of HealthStatus
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $HealthStatusCopyWith<HealthStatus> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $HealthStatusCopyWith<$Res> {
  factory $HealthStatusCopyWith(
          HealthStatus value, $Res Function(HealthStatus) then) =
      _$HealthStatusCopyWithImpl<$Res, HealthStatus>;
  @useResult
  $Res call(
      {@JsonKey(name: 'overall_score') double overallScore,
      String status,
      @JsonKey(name: 'config_system') ConfigSystemHealth configSystem,
      @JsonKey(name: 'runtime_system') RuntimeSystemHealth runtimeSystem});

  $ConfigSystemHealthCopyWith<$Res> get configSystem;
  $RuntimeSystemHealthCopyWith<$Res> get runtimeSystem;
}

/// @nodoc
class _$HealthStatusCopyWithImpl<$Res, $Val extends HealthStatus>
    implements $HealthStatusCopyWith<$Res> {
  _$HealthStatusCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of HealthStatus
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? overallScore = null,
    Object? status = null,
    Object? configSystem = null,
    Object? runtimeSystem = null,
  }) {
    return _then(_value.copyWith(
      overallScore: null == overallScore
          ? _value.overallScore
          : overallScore // ignore: cast_nullable_to_non_nullable
              as double,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      configSystem: null == configSystem
          ? _value.configSystem
          : configSystem // ignore: cast_nullable_to_non_nullable
              as ConfigSystemHealth,
      runtimeSystem: null == runtimeSystem
          ? _value.runtimeSystem
          : runtimeSystem // ignore: cast_nullable_to_non_nullable
              as RuntimeSystemHealth,
    ) as $Val);
  }

  /// Create a copy of HealthStatus
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $ConfigSystemHealthCopyWith<$Res> get configSystem {
    return $ConfigSystemHealthCopyWith<$Res>(_value.configSystem, (value) {
      return _then(_value.copyWith(configSystem: value) as $Val);
    });
  }

  /// Create a copy of HealthStatus
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $RuntimeSystemHealthCopyWith<$Res> get runtimeSystem {
    return $RuntimeSystemHealthCopyWith<$Res>(_value.runtimeSystem, (value) {
      return _then(_value.copyWith(runtimeSystem: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$HealthStatusImplCopyWith<$Res>
    implements $HealthStatusCopyWith<$Res> {
  factory _$$HealthStatusImplCopyWith(
          _$HealthStatusImpl value, $Res Function(_$HealthStatusImpl) then) =
      __$$HealthStatusImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'overall_score') double overallScore,
      String status,
      @JsonKey(name: 'config_system') ConfigSystemHealth configSystem,
      @JsonKey(name: 'runtime_system') RuntimeSystemHealth runtimeSystem});

  @override
  $ConfigSystemHealthCopyWith<$Res> get configSystem;
  @override
  $RuntimeSystemHealthCopyWith<$Res> get runtimeSystem;
}

/// @nodoc
class __$$HealthStatusImplCopyWithImpl<$Res>
    extends _$HealthStatusCopyWithImpl<$Res, _$HealthStatusImpl>
    implements _$$HealthStatusImplCopyWith<$Res> {
  __$$HealthStatusImplCopyWithImpl(
      _$HealthStatusImpl _value, $Res Function(_$HealthStatusImpl) _then)
      : super(_value, _then);

  /// Create a copy of HealthStatus
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? overallScore = null,
    Object? status = null,
    Object? configSystem = null,
    Object? runtimeSystem = null,
  }) {
    return _then(_$HealthStatusImpl(
      overallScore: null == overallScore
          ? _value.overallScore
          : overallScore // ignore: cast_nullable_to_non_nullable
              as double,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      configSystem: null == configSystem
          ? _value.configSystem
          : configSystem // ignore: cast_nullable_to_non_nullable
              as ConfigSystemHealth,
      runtimeSystem: null == runtimeSystem
          ? _value.runtimeSystem
          : runtimeSystem // ignore: cast_nullable_to_non_nullable
              as RuntimeSystemHealth,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$HealthStatusImpl implements _HealthStatus {
  const _$HealthStatusImpl(
      {@JsonKey(name: 'overall_score') required this.overallScore,
      required this.status,
      @JsonKey(name: 'config_system') required this.configSystem,
      @JsonKey(name: 'runtime_system') required this.runtimeSystem});

  factory _$HealthStatusImpl.fromJson(Map<String, dynamic> json) =>
      _$$HealthStatusImplFromJson(json);

  @override
  @JsonKey(name: 'overall_score')
  final double overallScore;
  @override
  final String status;
// healthy, degraded, unhealthy
  @override
  @JsonKey(name: 'config_system')
  final ConfigSystemHealth configSystem;
  @override
  @JsonKey(name: 'runtime_system')
  final RuntimeSystemHealth runtimeSystem;

  @override
  String toString() {
    return 'HealthStatus(overallScore: $overallScore, status: $status, configSystem: $configSystem, runtimeSystem: $runtimeSystem)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$HealthStatusImpl &&
            (identical(other.overallScore, overallScore) ||
                other.overallScore == overallScore) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.configSystem, configSystem) ||
                other.configSystem == configSystem) &&
            (identical(other.runtimeSystem, runtimeSystem) ||
                other.runtimeSystem == runtimeSystem));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType, overallScore, status, configSystem, runtimeSystem);

  /// Create a copy of HealthStatus
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$HealthStatusImplCopyWith<_$HealthStatusImpl> get copyWith =>
      __$$HealthStatusImplCopyWithImpl<_$HealthStatusImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$HealthStatusImplToJson(
      this,
    );
  }
}

abstract class _HealthStatus implements HealthStatus {
  const factory _HealthStatus(
      {@JsonKey(name: 'overall_score') required final double overallScore,
      required final String status,
      @JsonKey(name: 'config_system')
      required final ConfigSystemHealth configSystem,
      @JsonKey(name: 'runtime_system')
      required final RuntimeSystemHealth runtimeSystem}) = _$HealthStatusImpl;

  factory _HealthStatus.fromJson(Map<String, dynamic> json) =
      _$HealthStatusImpl.fromJson;

  @override
  @JsonKey(name: 'overall_score')
  double get overallScore;
  @override
  String get status; // healthy, degraded, unhealthy
  @override
  @JsonKey(name: 'config_system')
  ConfigSystemHealth get configSystem;
  @override
  @JsonKey(name: 'runtime_system')
  RuntimeSystemHealth get runtimeSystem;

  /// Create a copy of HealthStatus
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$HealthStatusImplCopyWith<_$HealthStatusImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ConfigSystemHealth _$ConfigSystemHealthFromJson(Map<String, dynamic> json) {
  return _ConfigSystemHealth.fromJson(json);
}

/// @nodoc
mixin _$ConfigSystemHealth {
  String get status => throw _privateConstructorUsedError;
  @JsonKey(name: 'config_version')
  String get configVersion => throw _privateConstructorUsedError;
  @JsonKey(name: 'last_reload')
  DateTime? get lastReload => throw _privateConstructorUsedError;
  Map<String, dynamic> get errors => throw _privateConstructorUsedError;

  /// Serializes this ConfigSystemHealth to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ConfigSystemHealth
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ConfigSystemHealthCopyWith<ConfigSystemHealth> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ConfigSystemHealthCopyWith<$Res> {
  factory $ConfigSystemHealthCopyWith(
          ConfigSystemHealth value, $Res Function(ConfigSystemHealth) then) =
      _$ConfigSystemHealthCopyWithImpl<$Res, ConfigSystemHealth>;
  @useResult
  $Res call(
      {String status,
      @JsonKey(name: 'config_version') String configVersion,
      @JsonKey(name: 'last_reload') DateTime? lastReload,
      Map<String, dynamic> errors});
}

/// @nodoc
class _$ConfigSystemHealthCopyWithImpl<$Res, $Val extends ConfigSystemHealth>
    implements $ConfigSystemHealthCopyWith<$Res> {
  _$ConfigSystemHealthCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ConfigSystemHealth
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? status = null,
    Object? configVersion = null,
    Object? lastReload = freezed,
    Object? errors = null,
  }) {
    return _then(_value.copyWith(
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      configVersion: null == configVersion
          ? _value.configVersion
          : configVersion // ignore: cast_nullable_to_non_nullable
              as String,
      lastReload: freezed == lastReload
          ? _value.lastReload
          : lastReload // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      errors: null == errors
          ? _value.errors
          : errors // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ConfigSystemHealthImplCopyWith<$Res>
    implements $ConfigSystemHealthCopyWith<$Res> {
  factory _$$ConfigSystemHealthImplCopyWith(_$ConfigSystemHealthImpl value,
          $Res Function(_$ConfigSystemHealthImpl) then) =
      __$$ConfigSystemHealthImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String status,
      @JsonKey(name: 'config_version') String configVersion,
      @JsonKey(name: 'last_reload') DateTime? lastReload,
      Map<String, dynamic> errors});
}

/// @nodoc
class __$$ConfigSystemHealthImplCopyWithImpl<$Res>
    extends _$ConfigSystemHealthCopyWithImpl<$Res, _$ConfigSystemHealthImpl>
    implements _$$ConfigSystemHealthImplCopyWith<$Res> {
  __$$ConfigSystemHealthImplCopyWithImpl(_$ConfigSystemHealthImpl _value,
      $Res Function(_$ConfigSystemHealthImpl) _then)
      : super(_value, _then);

  /// Create a copy of ConfigSystemHealth
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? status = null,
    Object? configVersion = null,
    Object? lastReload = freezed,
    Object? errors = null,
  }) {
    return _then(_$ConfigSystemHealthImpl(
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      configVersion: null == configVersion
          ? _value.configVersion
          : configVersion // ignore: cast_nullable_to_non_nullable
              as String,
      lastReload: freezed == lastReload
          ? _value.lastReload
          : lastReload // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      errors: null == errors
          ? _value._errors
          : errors // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ConfigSystemHealthImpl implements _ConfigSystemHealth {
  const _$ConfigSystemHealthImpl(
      {required this.status,
      @JsonKey(name: 'config_version') required this.configVersion,
      @JsonKey(name: 'last_reload') this.lastReload,
      final Map<String, dynamic> errors = const {}})
      : _errors = errors;

  factory _$ConfigSystemHealthImpl.fromJson(Map<String, dynamic> json) =>
      _$$ConfigSystemHealthImplFromJson(json);

  @override
  final String status;
  @override
  @JsonKey(name: 'config_version')
  final String configVersion;
  @override
  @JsonKey(name: 'last_reload')
  final DateTime? lastReload;
  final Map<String, dynamic> _errors;
  @override
  @JsonKey()
  Map<String, dynamic> get errors {
    if (_errors is EqualUnmodifiableMapView) return _errors;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_errors);
  }

  @override
  String toString() {
    return 'ConfigSystemHealth(status: $status, configVersion: $configVersion, lastReload: $lastReload, errors: $errors)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ConfigSystemHealthImpl &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.configVersion, configVersion) ||
                other.configVersion == configVersion) &&
            (identical(other.lastReload, lastReload) ||
                other.lastReload == lastReload) &&
            const DeepCollectionEquality().equals(other._errors, _errors));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, status, configVersion,
      lastReload, const DeepCollectionEquality().hash(_errors));

  /// Create a copy of ConfigSystemHealth
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ConfigSystemHealthImplCopyWith<_$ConfigSystemHealthImpl> get copyWith =>
      __$$ConfigSystemHealthImplCopyWithImpl<_$ConfigSystemHealthImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ConfigSystemHealthImplToJson(
      this,
    );
  }
}

abstract class _ConfigSystemHealth implements ConfigSystemHealth {
  const factory _ConfigSystemHealth(
      {required final String status,
      @JsonKey(name: 'config_version') required final String configVersion,
      @JsonKey(name: 'last_reload') final DateTime? lastReload,
      final Map<String, dynamic> errors}) = _$ConfigSystemHealthImpl;

  factory _ConfigSystemHealth.fromJson(Map<String, dynamic> json) =
      _$ConfigSystemHealthImpl.fromJson;

  @override
  String get status;
  @override
  @JsonKey(name: 'config_version')
  String get configVersion;
  @override
  @JsonKey(name: 'last_reload')
  DateTime? get lastReload;
  @override
  Map<String, dynamic> get errors;

  /// Create a copy of ConfigSystemHealth
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ConfigSystemHealthImplCopyWith<_$ConfigSystemHealthImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

RuntimeSystemHealth _$RuntimeSystemHealthFromJson(Map<String, dynamic> json) {
  return _RuntimeSystemHealth.fromJson(json);
}

/// @nodoc
mixin _$RuntimeSystemHealth {
  @JsonKey(name: 'total_instances')
  int get totalInstances => throw _privateConstructorUsedError;
  @JsonKey(name: 'healthy_instances')
  int get healthyInstances => throw _privateConstructorUsedError;
  @JsonKey(name: 'error_instances')
  int get errorInstances => throw _privateConstructorUsedError;
  @JsonKey(name: 'running_instances')
  int get runningInstances => throw _privateConstructorUsedError;

  /// Serializes this RuntimeSystemHealth to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of RuntimeSystemHealth
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $RuntimeSystemHealthCopyWith<RuntimeSystemHealth> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $RuntimeSystemHealthCopyWith<$Res> {
  factory $RuntimeSystemHealthCopyWith(
          RuntimeSystemHealth value, $Res Function(RuntimeSystemHealth) then) =
      _$RuntimeSystemHealthCopyWithImpl<$Res, RuntimeSystemHealth>;
  @useResult
  $Res call(
      {@JsonKey(name: 'total_instances') int totalInstances,
      @JsonKey(name: 'healthy_instances') int healthyInstances,
      @JsonKey(name: 'error_instances') int errorInstances,
      @JsonKey(name: 'running_instances') int runningInstances});
}

/// @nodoc
class _$RuntimeSystemHealthCopyWithImpl<$Res, $Val extends RuntimeSystemHealth>
    implements $RuntimeSystemHealthCopyWith<$Res> {
  _$RuntimeSystemHealthCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of RuntimeSystemHealth
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalInstances = null,
    Object? healthyInstances = null,
    Object? errorInstances = null,
    Object? runningInstances = null,
  }) {
    return _then(_value.copyWith(
      totalInstances: null == totalInstances
          ? _value.totalInstances
          : totalInstances // ignore: cast_nullable_to_non_nullable
              as int,
      healthyInstances: null == healthyInstances
          ? _value.healthyInstances
          : healthyInstances // ignore: cast_nullable_to_non_nullable
              as int,
      errorInstances: null == errorInstances
          ? _value.errorInstances
          : errorInstances // ignore: cast_nullable_to_non_nullable
              as int,
      runningInstances: null == runningInstances
          ? _value.runningInstances
          : runningInstances // ignore: cast_nullable_to_non_nullable
              as int,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$RuntimeSystemHealthImplCopyWith<$Res>
    implements $RuntimeSystemHealthCopyWith<$Res> {
  factory _$$RuntimeSystemHealthImplCopyWith(_$RuntimeSystemHealthImpl value,
          $Res Function(_$RuntimeSystemHealthImpl) then) =
      __$$RuntimeSystemHealthImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'total_instances') int totalInstances,
      @JsonKey(name: 'healthy_instances') int healthyInstances,
      @JsonKey(name: 'error_instances') int errorInstances,
      @JsonKey(name: 'running_instances') int runningInstances});
}

/// @nodoc
class __$$RuntimeSystemHealthImplCopyWithImpl<$Res>
    extends _$RuntimeSystemHealthCopyWithImpl<$Res, _$RuntimeSystemHealthImpl>
    implements _$$RuntimeSystemHealthImplCopyWith<$Res> {
  __$$RuntimeSystemHealthImplCopyWithImpl(_$RuntimeSystemHealthImpl _value,
      $Res Function(_$RuntimeSystemHealthImpl) _then)
      : super(_value, _then);

  /// Create a copy of RuntimeSystemHealth
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalInstances = null,
    Object? healthyInstances = null,
    Object? errorInstances = null,
    Object? runningInstances = null,
  }) {
    return _then(_$RuntimeSystemHealthImpl(
      totalInstances: null == totalInstances
          ? _value.totalInstances
          : totalInstances // ignore: cast_nullable_to_non_nullable
              as int,
      healthyInstances: null == healthyInstances
          ? _value.healthyInstances
          : healthyInstances // ignore: cast_nullable_to_non_nullable
              as int,
      errorInstances: null == errorInstances
          ? _value.errorInstances
          : errorInstances // ignore: cast_nullable_to_non_nullable
              as int,
      runningInstances: null == runningInstances
          ? _value.runningInstances
          : runningInstances // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$RuntimeSystemHealthImpl implements _RuntimeSystemHealth {
  const _$RuntimeSystemHealthImpl(
      {@JsonKey(name: 'total_instances') required this.totalInstances,
      @JsonKey(name: 'healthy_instances') required this.healthyInstances,
      @JsonKey(name: 'error_instances') required this.errorInstances,
      @JsonKey(name: 'running_instances') required this.runningInstances});

  factory _$RuntimeSystemHealthImpl.fromJson(Map<String, dynamic> json) =>
      _$$RuntimeSystemHealthImplFromJson(json);

  @override
  @JsonKey(name: 'total_instances')
  final int totalInstances;
  @override
  @JsonKey(name: 'healthy_instances')
  final int healthyInstances;
  @override
  @JsonKey(name: 'error_instances')
  final int errorInstances;
  @override
  @JsonKey(name: 'running_instances')
  final int runningInstances;

  @override
  String toString() {
    return 'RuntimeSystemHealth(totalInstances: $totalInstances, healthyInstances: $healthyInstances, errorInstances: $errorInstances, runningInstances: $runningInstances)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$RuntimeSystemHealthImpl &&
            (identical(other.totalInstances, totalInstances) ||
                other.totalInstances == totalInstances) &&
            (identical(other.healthyInstances, healthyInstances) ||
                other.healthyInstances == healthyInstances) &&
            (identical(other.errorInstances, errorInstances) ||
                other.errorInstances == errorInstances) &&
            (identical(other.runningInstances, runningInstances) ||
                other.runningInstances == runningInstances));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, totalInstances, healthyInstances,
      errorInstances, runningInstances);

  /// Create a copy of RuntimeSystemHealth
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$RuntimeSystemHealthImplCopyWith<_$RuntimeSystemHealthImpl> get copyWith =>
      __$$RuntimeSystemHealthImplCopyWithImpl<_$RuntimeSystemHealthImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$RuntimeSystemHealthImplToJson(
      this,
    );
  }
}

abstract class _RuntimeSystemHealth implements RuntimeSystemHealth {
  const factory _RuntimeSystemHealth(
      {@JsonKey(name: 'total_instances') required final int totalInstances,
      @JsonKey(name: 'healthy_instances') required final int healthyInstances,
      @JsonKey(name: 'error_instances') required final int errorInstances,
      @JsonKey(name: 'running_instances')
      required final int runningInstances}) = _$RuntimeSystemHealthImpl;

  factory _RuntimeSystemHealth.fromJson(Map<String, dynamic> json) =
      _$RuntimeSystemHealthImpl.fromJson;

  @override
  @JsonKey(name: 'total_instances')
  int get totalInstances;
  @override
  @JsonKey(name: 'healthy_instances')
  int get healthyInstances;
  @override
  @JsonKey(name: 'error_instances')
  int get errorInstances;
  @override
  @JsonKey(name: 'running_instances')
  int get runningInstances;

  /// Create a copy of RuntimeSystemHealth
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$RuntimeSystemHealthImplCopyWith<_$RuntimeSystemHealthImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ConnectorStatesOverview _$ConnectorStatesOverviewFromJson(
    Map<String, dynamic> json) {
  return _ConnectorStatesOverview.fromJson(json);
}

/// @nodoc
mixin _$ConnectorStatesOverview {
  bool get success => throw _privateConstructorUsedError;
  StateOverview get overview => throw _privateConstructorUsedError;
  @JsonKey(name: 'running_instances')
  List<String> get runningInstances => throw _privateConstructorUsedError;

  /// Serializes this ConnectorStatesOverview to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ConnectorStatesOverview
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ConnectorStatesOverviewCopyWith<ConnectorStatesOverview> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ConnectorStatesOverviewCopyWith<$Res> {
  factory $ConnectorStatesOverviewCopyWith(ConnectorStatesOverview value,
          $Res Function(ConnectorStatesOverview) then) =
      _$ConnectorStatesOverviewCopyWithImpl<$Res, ConnectorStatesOverview>;
  @useResult
  $Res call(
      {bool success,
      StateOverview overview,
      @JsonKey(name: 'running_instances') List<String> runningInstances});

  $StateOverviewCopyWith<$Res> get overview;
}

/// @nodoc
class _$ConnectorStatesOverviewCopyWithImpl<$Res,
        $Val extends ConnectorStatesOverview>
    implements $ConnectorStatesOverviewCopyWith<$Res> {
  _$ConnectorStatesOverviewCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ConnectorStatesOverview
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? overview = null,
    Object? runningInstances = null,
  }) {
    return _then(_value.copyWith(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      overview: null == overview
          ? _value.overview
          : overview // ignore: cast_nullable_to_non_nullable
              as StateOverview,
      runningInstances: null == runningInstances
          ? _value.runningInstances
          : runningInstances // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ) as $Val);
  }

  /// Create a copy of ConnectorStatesOverview
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $StateOverviewCopyWith<$Res> get overview {
    return $StateOverviewCopyWith<$Res>(_value.overview, (value) {
      return _then(_value.copyWith(overview: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$ConnectorStatesOverviewImplCopyWith<$Res>
    implements $ConnectorStatesOverviewCopyWith<$Res> {
  factory _$$ConnectorStatesOverviewImplCopyWith(
          _$ConnectorStatesOverviewImpl value,
          $Res Function(_$ConnectorStatesOverviewImpl) then) =
      __$$ConnectorStatesOverviewImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {bool success,
      StateOverview overview,
      @JsonKey(name: 'running_instances') List<String> runningInstances});

  @override
  $StateOverviewCopyWith<$Res> get overview;
}

/// @nodoc
class __$$ConnectorStatesOverviewImplCopyWithImpl<$Res>
    extends _$ConnectorStatesOverviewCopyWithImpl<$Res,
        _$ConnectorStatesOverviewImpl>
    implements _$$ConnectorStatesOverviewImplCopyWith<$Res> {
  __$$ConnectorStatesOverviewImplCopyWithImpl(
      _$ConnectorStatesOverviewImpl _value,
      $Res Function(_$ConnectorStatesOverviewImpl) _then)
      : super(_value, _then);

  /// Create a copy of ConnectorStatesOverview
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? overview = null,
    Object? runningInstances = null,
  }) {
    return _then(_$ConnectorStatesOverviewImpl(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      overview: null == overview
          ? _value.overview
          : overview // ignore: cast_nullable_to_non_nullable
              as StateOverview,
      runningInstances: null == runningInstances
          ? _value._runningInstances
          : runningInstances // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ConnectorStatesOverviewImpl implements _ConnectorStatesOverview {
  const _$ConnectorStatesOverviewImpl(
      {required this.success,
      required this.overview,
      @JsonKey(name: 'running_instances')
      final List<String> runningInstances = const []})
      : _runningInstances = runningInstances;

  factory _$ConnectorStatesOverviewImpl.fromJson(Map<String, dynamic> json) =>
      _$$ConnectorStatesOverviewImplFromJson(json);

  @override
  final bool success;
  @override
  final StateOverview overview;
  final List<String> _runningInstances;
  @override
  @JsonKey(name: 'running_instances')
  List<String> get runningInstances {
    if (_runningInstances is EqualUnmodifiableListView)
      return _runningInstances;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_runningInstances);
  }

  @override
  String toString() {
    return 'ConnectorStatesOverview(success: $success, overview: $overview, runningInstances: $runningInstances)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ConnectorStatesOverviewImpl &&
            (identical(other.success, success) || other.success == success) &&
            (identical(other.overview, overview) ||
                other.overview == overview) &&
            const DeepCollectionEquality()
                .equals(other._runningInstances, _runningInstances));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, success, overview,
      const DeepCollectionEquality().hash(_runningInstances));

  /// Create a copy of ConnectorStatesOverview
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ConnectorStatesOverviewImplCopyWith<_$ConnectorStatesOverviewImpl>
      get copyWith => __$$ConnectorStatesOverviewImplCopyWithImpl<
          _$ConnectorStatesOverviewImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ConnectorStatesOverviewImplToJson(
      this,
    );
  }
}

abstract class _ConnectorStatesOverview implements ConnectorStatesOverview {
  const factory _ConnectorStatesOverview(
      {required final bool success,
      required final StateOverview overview,
      @JsonKey(name: 'running_instances')
      final List<String> runningInstances}) = _$ConnectorStatesOverviewImpl;

  factory _ConnectorStatesOverview.fromJson(Map<String, dynamic> json) =
      _$ConnectorStatesOverviewImpl.fromJson;

  @override
  bool get success;
  @override
  StateOverview get overview;
  @override
  @JsonKey(name: 'running_instances')
  List<String> get runningInstances;

  /// Create a copy of ConnectorStatesOverview
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ConnectorStatesOverviewImplCopyWith<_$ConnectorStatesOverviewImpl>
      get copyWith => throw _privateConstructorUsedError;
}

StateOverview _$StateOverviewFromJson(Map<String, dynamic> json) {
  return _StateOverview.fromJson(json);
}

/// @nodoc
mixin _$StateOverview {
  @JsonKey(name: 'total_instances')
  int get totalInstances => throw _privateConstructorUsedError;
  @JsonKey(name: 'running_instances')
  int get runningInstances => throw _privateConstructorUsedError;
  @JsonKey(name: 'state_distribution')
  Map<String, int> get stateDistribution => throw _privateConstructorUsedError;

  /// Serializes this StateOverview to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of StateOverview
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $StateOverviewCopyWith<StateOverview> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $StateOverviewCopyWith<$Res> {
  factory $StateOverviewCopyWith(
          StateOverview value, $Res Function(StateOverview) then) =
      _$StateOverviewCopyWithImpl<$Res, StateOverview>;
  @useResult
  $Res call(
      {@JsonKey(name: 'total_instances') int totalInstances,
      @JsonKey(name: 'running_instances') int runningInstances,
      @JsonKey(name: 'state_distribution') Map<String, int> stateDistribution});
}

/// @nodoc
class _$StateOverviewCopyWithImpl<$Res, $Val extends StateOverview>
    implements $StateOverviewCopyWith<$Res> {
  _$StateOverviewCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of StateOverview
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalInstances = null,
    Object? runningInstances = null,
    Object? stateDistribution = null,
  }) {
    return _then(_value.copyWith(
      totalInstances: null == totalInstances
          ? _value.totalInstances
          : totalInstances // ignore: cast_nullable_to_non_nullable
              as int,
      runningInstances: null == runningInstances
          ? _value.runningInstances
          : runningInstances // ignore: cast_nullable_to_non_nullable
              as int,
      stateDistribution: null == stateDistribution
          ? _value.stateDistribution
          : stateDistribution // ignore: cast_nullable_to_non_nullable
              as Map<String, int>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$StateOverviewImplCopyWith<$Res>
    implements $StateOverviewCopyWith<$Res> {
  factory _$$StateOverviewImplCopyWith(
          _$StateOverviewImpl value, $Res Function(_$StateOverviewImpl) then) =
      __$$StateOverviewImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'total_instances') int totalInstances,
      @JsonKey(name: 'running_instances') int runningInstances,
      @JsonKey(name: 'state_distribution') Map<String, int> stateDistribution});
}

/// @nodoc
class __$$StateOverviewImplCopyWithImpl<$Res>
    extends _$StateOverviewCopyWithImpl<$Res, _$StateOverviewImpl>
    implements _$$StateOverviewImplCopyWith<$Res> {
  __$$StateOverviewImplCopyWithImpl(
      _$StateOverviewImpl _value, $Res Function(_$StateOverviewImpl) _then)
      : super(_value, _then);

  /// Create a copy of StateOverview
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalInstances = null,
    Object? runningInstances = null,
    Object? stateDistribution = null,
  }) {
    return _then(_$StateOverviewImpl(
      totalInstances: null == totalInstances
          ? _value.totalInstances
          : totalInstances // ignore: cast_nullable_to_non_nullable
              as int,
      runningInstances: null == runningInstances
          ? _value.runningInstances
          : runningInstances // ignore: cast_nullable_to_non_nullable
              as int,
      stateDistribution: null == stateDistribution
          ? _value._stateDistribution
          : stateDistribution // ignore: cast_nullable_to_non_nullable
              as Map<String, int>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$StateOverviewImpl implements _StateOverview {
  const _$StateOverviewImpl(
      {@JsonKey(name: 'total_instances') required this.totalInstances,
      @JsonKey(name: 'running_instances') required this.runningInstances,
      @JsonKey(name: 'state_distribution')
      required final Map<String, int> stateDistribution})
      : _stateDistribution = stateDistribution;

  factory _$StateOverviewImpl.fromJson(Map<String, dynamic> json) =>
      _$$StateOverviewImplFromJson(json);

  @override
  @JsonKey(name: 'total_instances')
  final int totalInstances;
  @override
  @JsonKey(name: 'running_instances')
  final int runningInstances;
  final Map<String, int> _stateDistribution;
  @override
  @JsonKey(name: 'state_distribution')
  Map<String, int> get stateDistribution {
    if (_stateDistribution is EqualUnmodifiableMapView)
      return _stateDistribution;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_stateDistribution);
  }

  @override
  String toString() {
    return 'StateOverview(totalInstances: $totalInstances, runningInstances: $runningInstances, stateDistribution: $stateDistribution)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$StateOverviewImpl &&
            (identical(other.totalInstances, totalInstances) ||
                other.totalInstances == totalInstances) &&
            (identical(other.runningInstances, runningInstances) ||
                other.runningInstances == runningInstances) &&
            const DeepCollectionEquality()
                .equals(other._stateDistribution, _stateDistribution));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, totalInstances, runningInstances,
      const DeepCollectionEquality().hash(_stateDistribution));

  /// Create a copy of StateOverview
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$StateOverviewImplCopyWith<_$StateOverviewImpl> get copyWith =>
      __$$StateOverviewImplCopyWithImpl<_$StateOverviewImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$StateOverviewImplToJson(
      this,
    );
  }
}

abstract class _StateOverview implements StateOverview {
  const factory _StateOverview(
      {@JsonKey(name: 'total_instances') required final int totalInstances,
      @JsonKey(name: 'running_instances') required final int runningInstances,
      @JsonKey(name: 'state_distribution')
      required final Map<String, int> stateDistribution}) = _$StateOverviewImpl;

  factory _StateOverview.fromJson(Map<String, dynamic> json) =
      _$StateOverviewImpl.fromJson;

  @override
  @JsonKey(name: 'total_instances')
  int get totalInstances;
  @override
  @JsonKey(name: 'running_instances')
  int get runningInstances;
  @override
  @JsonKey(name: 'state_distribution')
  Map<String, int> get stateDistribution;

  /// Create a copy of StateOverview
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$StateOverviewImplCopyWith<_$StateOverviewImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ConnectorApiResponse _$ConnectorApiResponseFromJson(Map<String, dynamic> json) {
  return _ConnectorApiResponse.fromJson(json);
}

/// @nodoc
mixin _$ConnectorApiResponse {
  bool get success => throw _privateConstructorUsedError;
  String get message => throw _privateConstructorUsedError;
  Object? get data => throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;

  /// Serializes this ConnectorApiResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ConnectorApiResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ConnectorApiResponseCopyWith<ConnectorApiResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ConnectorApiResponseCopyWith<$Res> {
  factory $ConnectorApiResponseCopyWith(ConnectorApiResponse value,
          $Res Function(ConnectorApiResponse) then) =
      _$ConnectorApiResponseCopyWithImpl<$Res, ConnectorApiResponse>;
  @useResult
  $Res call({bool success, String message, Object? data, String? error});
}

/// @nodoc
class _$ConnectorApiResponseCopyWithImpl<$Res,
        $Val extends ConnectorApiResponse>
    implements $ConnectorApiResponseCopyWith<$Res> {
  _$ConnectorApiResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ConnectorApiResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? message = null,
    Object? data = freezed,
    Object? error = freezed,
  }) {
    return _then(_value.copyWith(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
      data: freezed == data ? _value.data : data,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ConnectorApiResponseImplCopyWith<$Res>
    implements $ConnectorApiResponseCopyWith<$Res> {
  factory _$$ConnectorApiResponseImplCopyWith(_$ConnectorApiResponseImpl value,
          $Res Function(_$ConnectorApiResponseImpl) then) =
      __$$ConnectorApiResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({bool success, String message, Object? data, String? error});
}

/// @nodoc
class __$$ConnectorApiResponseImplCopyWithImpl<$Res>
    extends _$ConnectorApiResponseCopyWithImpl<$Res, _$ConnectorApiResponseImpl>
    implements _$$ConnectorApiResponseImplCopyWith<$Res> {
  __$$ConnectorApiResponseImplCopyWithImpl(_$ConnectorApiResponseImpl _value,
      $Res Function(_$ConnectorApiResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of ConnectorApiResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? message = null,
    Object? data = freezed,
    Object? error = freezed,
  }) {
    return _then(_$ConnectorApiResponseImpl(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
      data: freezed == data ? _value.data : data,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ConnectorApiResponseImpl implements _ConnectorApiResponse {
  const _$ConnectorApiResponseImpl(
      {required this.success, required this.message, this.data, this.error});

  factory _$ConnectorApiResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$ConnectorApiResponseImplFromJson(json);

  @override
  final bool success;
  @override
  final String message;
  @override
  final Object? data;
  @override
  final String? error;

  @override
  String toString() {
    return 'ConnectorApiResponse(success: $success, message: $message, data: $data, error: $error)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ConnectorApiResponseImpl &&
            (identical(other.success, success) || other.success == success) &&
            (identical(other.message, message) || other.message == message) &&
            const DeepCollectionEquality().equals(other.data, data) &&
            (identical(other.error, error) || other.error == error));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, success, message,
      const DeepCollectionEquality().hash(data), error);

  /// Create a copy of ConnectorApiResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ConnectorApiResponseImplCopyWith<_$ConnectorApiResponseImpl>
      get copyWith =>
          __$$ConnectorApiResponseImplCopyWithImpl<_$ConnectorApiResponseImpl>(
              this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ConnectorApiResponseImplToJson(
      this,
    );
  }
}

abstract class _ConnectorApiResponse implements ConnectorApiResponse {
  const factory _ConnectorApiResponse(
      {required final bool success,
      required final String message,
      final Object? data,
      final String? error}) = _$ConnectorApiResponseImpl;

  factory _ConnectorApiResponse.fromJson(Map<String, dynamic> json) =
      _$ConnectorApiResponseImpl.fromJson;

  @override
  bool get success;
  @override
  String get message;
  @override
  Object? get data;
  @override
  String? get error;

  /// Create a copy of ConnectorApiResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ConnectorApiResponseImplCopyWith<_$ConnectorApiResponseImpl>
      get copyWith => throw _privateConstructorUsedError;
}

DiscoveryResponse _$DiscoveryResponseFromJson(Map<String, dynamic> json) {
  return _DiscoveryResponse.fromJson(json);
}

/// @nodoc
mixin _$DiscoveryResponse {
  bool get success => throw _privateConstructorUsedError;
  String get message => throw _privateConstructorUsedError;
  @JsonKey(name: 'connector_types')
  List<ConnectorTypeInfo> get connectorTypes =>
      throw _privateConstructorUsedError;

  /// Serializes this DiscoveryResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of DiscoveryResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DiscoveryResponseCopyWith<DiscoveryResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DiscoveryResponseCopyWith<$Res> {
  factory $DiscoveryResponseCopyWith(
          DiscoveryResponse value, $Res Function(DiscoveryResponse) then) =
      _$DiscoveryResponseCopyWithImpl<$Res, DiscoveryResponse>;
  @useResult
  $Res call(
      {bool success,
      String message,
      @JsonKey(name: 'connector_types')
      List<ConnectorTypeInfo> connectorTypes});
}

/// @nodoc
class _$DiscoveryResponseCopyWithImpl<$Res, $Val extends DiscoveryResponse>
    implements $DiscoveryResponseCopyWith<$Res> {
  _$DiscoveryResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DiscoveryResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? message = null,
    Object? connectorTypes = null,
  }) {
    return _then(_value.copyWith(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
      connectorTypes: null == connectorTypes
          ? _value.connectorTypes
          : connectorTypes // ignore: cast_nullable_to_non_nullable
              as List<ConnectorTypeInfo>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DiscoveryResponseImplCopyWith<$Res>
    implements $DiscoveryResponseCopyWith<$Res> {
  factory _$$DiscoveryResponseImplCopyWith(_$DiscoveryResponseImpl value,
          $Res Function(_$DiscoveryResponseImpl) then) =
      __$$DiscoveryResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {bool success,
      String message,
      @JsonKey(name: 'connector_types')
      List<ConnectorTypeInfo> connectorTypes});
}

/// @nodoc
class __$$DiscoveryResponseImplCopyWithImpl<$Res>
    extends _$DiscoveryResponseCopyWithImpl<$Res, _$DiscoveryResponseImpl>
    implements _$$DiscoveryResponseImplCopyWith<$Res> {
  __$$DiscoveryResponseImplCopyWithImpl(_$DiscoveryResponseImpl _value,
      $Res Function(_$DiscoveryResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of DiscoveryResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? message = null,
    Object? connectorTypes = null,
  }) {
    return _then(_$DiscoveryResponseImpl(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
      connectorTypes: null == connectorTypes
          ? _value._connectorTypes
          : connectorTypes // ignore: cast_nullable_to_non_nullable
              as List<ConnectorTypeInfo>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DiscoveryResponseImpl implements _DiscoveryResponse {
  const _$DiscoveryResponseImpl(
      {required this.success,
      required this.message,
      @JsonKey(name: 'connector_types')
      final List<ConnectorTypeInfo> connectorTypes = const []})
      : _connectorTypes = connectorTypes;

  factory _$DiscoveryResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$DiscoveryResponseImplFromJson(json);

  @override
  final bool success;
  @override
  final String message;
  final List<ConnectorTypeInfo> _connectorTypes;
  @override
  @JsonKey(name: 'connector_types')
  List<ConnectorTypeInfo> get connectorTypes {
    if (_connectorTypes is EqualUnmodifiableListView) return _connectorTypes;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_connectorTypes);
  }

  @override
  String toString() {
    return 'DiscoveryResponse(success: $success, message: $message, connectorTypes: $connectorTypes)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DiscoveryResponseImpl &&
            (identical(other.success, success) || other.success == success) &&
            (identical(other.message, message) || other.message == message) &&
            const DeepCollectionEquality()
                .equals(other._connectorTypes, _connectorTypes));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, success, message,
      const DeepCollectionEquality().hash(_connectorTypes));

  /// Create a copy of DiscoveryResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DiscoveryResponseImplCopyWith<_$DiscoveryResponseImpl> get copyWith =>
      __$$DiscoveryResponseImplCopyWithImpl<_$DiscoveryResponseImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DiscoveryResponseImplToJson(
      this,
    );
  }
}

abstract class _DiscoveryResponse implements DiscoveryResponse {
  const factory _DiscoveryResponse(
      {required final bool success,
      required final String message,
      @JsonKey(name: 'connector_types')
      final List<ConnectorTypeInfo> connectorTypes}) = _$DiscoveryResponseImpl;

  factory _DiscoveryResponse.fromJson(Map<String, dynamic> json) =
      _$DiscoveryResponseImpl.fromJson;

  @override
  bool get success;
  @override
  String get message;
  @override
  @JsonKey(name: 'connector_types')
  List<ConnectorTypeInfo> get connectorTypes;

  /// Create a copy of DiscoveryResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DiscoveryResponseImplCopyWith<_$DiscoveryResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

InstanceListResponse _$InstanceListResponseFromJson(Map<String, dynamic> json) {
  return _InstanceListResponse.fromJson(json);
}

/// @nodoc
mixin _$InstanceListResponse {
  bool get success => throw _privateConstructorUsedError;
  List<ConnectorInstanceInfo> get instances =>
      throw _privateConstructorUsedError;
  @JsonKey(name: 'total_count')
  int get totalCount => throw _privateConstructorUsedError;

  /// Serializes this InstanceListResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of InstanceListResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $InstanceListResponseCopyWith<InstanceListResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $InstanceListResponseCopyWith<$Res> {
  factory $InstanceListResponseCopyWith(InstanceListResponse value,
          $Res Function(InstanceListResponse) then) =
      _$InstanceListResponseCopyWithImpl<$Res, InstanceListResponse>;
  @useResult
  $Res call(
      {bool success,
      List<ConnectorInstanceInfo> instances,
      @JsonKey(name: 'total_count') int totalCount});
}

/// @nodoc
class _$InstanceListResponseCopyWithImpl<$Res,
        $Val extends InstanceListResponse>
    implements $InstanceListResponseCopyWith<$Res> {
  _$InstanceListResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of InstanceListResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? instances = null,
    Object? totalCount = null,
  }) {
    return _then(_value.copyWith(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      instances: null == instances
          ? _value.instances
          : instances // ignore: cast_nullable_to_non_nullable
              as List<ConnectorInstanceInfo>,
      totalCount: null == totalCount
          ? _value.totalCount
          : totalCount // ignore: cast_nullable_to_non_nullable
              as int,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$InstanceListResponseImplCopyWith<$Res>
    implements $InstanceListResponseCopyWith<$Res> {
  factory _$$InstanceListResponseImplCopyWith(_$InstanceListResponseImpl value,
          $Res Function(_$InstanceListResponseImpl) then) =
      __$$InstanceListResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {bool success,
      List<ConnectorInstanceInfo> instances,
      @JsonKey(name: 'total_count') int totalCount});
}

/// @nodoc
class __$$InstanceListResponseImplCopyWithImpl<$Res>
    extends _$InstanceListResponseCopyWithImpl<$Res, _$InstanceListResponseImpl>
    implements _$$InstanceListResponseImplCopyWith<$Res> {
  __$$InstanceListResponseImplCopyWithImpl(_$InstanceListResponseImpl _value,
      $Res Function(_$InstanceListResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of InstanceListResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? instances = null,
    Object? totalCount = null,
  }) {
    return _then(_$InstanceListResponseImpl(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      instances: null == instances
          ? _value._instances
          : instances // ignore: cast_nullable_to_non_nullable
              as List<ConnectorInstanceInfo>,
      totalCount: null == totalCount
          ? _value.totalCount
          : totalCount // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$InstanceListResponseImpl implements _InstanceListResponse {
  const _$InstanceListResponseImpl(
      {required this.success,
      final List<ConnectorInstanceInfo> instances = const [],
      @JsonKey(name: 'total_count') this.totalCount = 0})
      : _instances = instances;

  factory _$InstanceListResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$InstanceListResponseImplFromJson(json);

  @override
  final bool success;
  final List<ConnectorInstanceInfo> _instances;
  @override
  @JsonKey()
  List<ConnectorInstanceInfo> get instances {
    if (_instances is EqualUnmodifiableListView) return _instances;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_instances);
  }

  @override
  @JsonKey(name: 'total_count')
  final int totalCount;

  @override
  String toString() {
    return 'InstanceListResponse(success: $success, instances: $instances, totalCount: $totalCount)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$InstanceListResponseImpl &&
            (identical(other.success, success) || other.success == success) &&
            const DeepCollectionEquality()
                .equals(other._instances, _instances) &&
            (identical(other.totalCount, totalCount) ||
                other.totalCount == totalCount));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, success,
      const DeepCollectionEquality().hash(_instances), totalCount);

  /// Create a copy of InstanceListResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$InstanceListResponseImplCopyWith<_$InstanceListResponseImpl>
      get copyWith =>
          __$$InstanceListResponseImplCopyWithImpl<_$InstanceListResponseImpl>(
              this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$InstanceListResponseImplToJson(
      this,
    );
  }
}

abstract class _InstanceListResponse implements InstanceListResponse {
  const factory _InstanceListResponse(
          {required final bool success,
          final List<ConnectorInstanceInfo> instances,
          @JsonKey(name: 'total_count') final int totalCount}) =
      _$InstanceListResponseImpl;

  factory _InstanceListResponse.fromJson(Map<String, dynamic> json) =
      _$InstanceListResponseImpl.fromJson;

  @override
  bool get success;
  @override
  List<ConnectorInstanceInfo> get instances;
  @override
  @JsonKey(name: 'total_count')
  int get totalCount;

  /// Create a copy of InstanceListResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$InstanceListResponseImplCopyWith<_$InstanceListResponseImpl>
      get copyWith => throw _privateConstructorUsedError;
}

InstanceDetailResponse _$InstanceDetailResponseFromJson(
    Map<String, dynamic> json) {
  return _InstanceDetailResponse.fromJson(json);
}

/// @nodoc
mixin _$InstanceDetailResponse {
  bool get success => throw _privateConstructorUsedError;
  ConnectorInstanceDetail get instance => throw _privateConstructorUsedError;

  /// Serializes this InstanceDetailResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of InstanceDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $InstanceDetailResponseCopyWith<InstanceDetailResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $InstanceDetailResponseCopyWith<$Res> {
  factory $InstanceDetailResponseCopyWith(InstanceDetailResponse value,
          $Res Function(InstanceDetailResponse) then) =
      _$InstanceDetailResponseCopyWithImpl<$Res, InstanceDetailResponse>;
  @useResult
  $Res call({bool success, ConnectorInstanceDetail instance});

  $ConnectorInstanceDetailCopyWith<$Res> get instance;
}

/// @nodoc
class _$InstanceDetailResponseCopyWithImpl<$Res,
        $Val extends InstanceDetailResponse>
    implements $InstanceDetailResponseCopyWith<$Res> {
  _$InstanceDetailResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of InstanceDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? instance = null,
  }) {
    return _then(_value.copyWith(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      instance: null == instance
          ? _value.instance
          : instance // ignore: cast_nullable_to_non_nullable
              as ConnectorInstanceDetail,
    ) as $Val);
  }

  /// Create a copy of InstanceDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $ConnectorInstanceDetailCopyWith<$Res> get instance {
    return $ConnectorInstanceDetailCopyWith<$Res>(_value.instance, (value) {
      return _then(_value.copyWith(instance: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$InstanceDetailResponseImplCopyWith<$Res>
    implements $InstanceDetailResponseCopyWith<$Res> {
  factory _$$InstanceDetailResponseImplCopyWith(
          _$InstanceDetailResponseImpl value,
          $Res Function(_$InstanceDetailResponseImpl) then) =
      __$$InstanceDetailResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({bool success, ConnectorInstanceDetail instance});

  @override
  $ConnectorInstanceDetailCopyWith<$Res> get instance;
}

/// @nodoc
class __$$InstanceDetailResponseImplCopyWithImpl<$Res>
    extends _$InstanceDetailResponseCopyWithImpl<$Res,
        _$InstanceDetailResponseImpl>
    implements _$$InstanceDetailResponseImplCopyWith<$Res> {
  __$$InstanceDetailResponseImplCopyWithImpl(
      _$InstanceDetailResponseImpl _value,
      $Res Function(_$InstanceDetailResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of InstanceDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? instance = null,
  }) {
    return _then(_$InstanceDetailResponseImpl(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      instance: null == instance
          ? _value.instance
          : instance // ignore: cast_nullable_to_non_nullable
              as ConnectorInstanceDetail,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$InstanceDetailResponseImpl implements _InstanceDetailResponse {
  const _$InstanceDetailResponseImpl(
      {required this.success, required this.instance});

  factory _$InstanceDetailResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$InstanceDetailResponseImplFromJson(json);

  @override
  final bool success;
  @override
  final ConnectorInstanceDetail instance;

  @override
  String toString() {
    return 'InstanceDetailResponse(success: $success, instance: $instance)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$InstanceDetailResponseImpl &&
            (identical(other.success, success) || other.success == success) &&
            (identical(other.instance, instance) ||
                other.instance == instance));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, success, instance);

  /// Create a copy of InstanceDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$InstanceDetailResponseImplCopyWith<_$InstanceDetailResponseImpl>
      get copyWith => __$$InstanceDetailResponseImplCopyWithImpl<
          _$InstanceDetailResponseImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$InstanceDetailResponseImplToJson(
      this,
    );
  }
}

abstract class _InstanceDetailResponse implements InstanceDetailResponse {
  const factory _InstanceDetailResponse(
          {required final bool success,
          required final ConnectorInstanceDetail instance}) =
      _$InstanceDetailResponseImpl;

  factory _InstanceDetailResponse.fromJson(Map<String, dynamic> json) =
      _$InstanceDetailResponseImpl.fromJson;

  @override
  bool get success;
  @override
  ConnectorInstanceDetail get instance;

  /// Create a copy of InstanceDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$InstanceDetailResponseImplCopyWith<_$InstanceDetailResponseImpl>
      get copyWith => throw _privateConstructorUsedError;
}

ConnectorInstanceDetail _$ConnectorInstanceDetailFromJson(
    Map<String, dynamic> json) {
  return _ConnectorInstanceDetail.fromJson(json);
}

/// @nodoc
mixin _$ConnectorInstanceDetail {
  @JsonKey(name: 'instance_id')
  String get instanceId => throw _privateConstructorUsedError;
  @JsonKey(name: 'display_name')
  String get displayName => throw _privateConstructorUsedError;
  @JsonKey(name: 'type_id')
  String get typeId => throw _privateConstructorUsedError;
  Map<String, dynamic> get config => throw _privateConstructorUsedError;
  ConnectorState get state => throw _privateConstructorUsedError;
  bool get enabled => throw _privateConstructorUsedError;
  @JsonKey(name: 'auto_start')
  bool get autoStart => throw _privateConstructorUsedError;
  @JsonKey(name: 'process_id')
  int? get processId => throw _privateConstructorUsedError;
  @JsonKey(name: 'last_heartbeat')
  DateTime? get lastHeartbeat => throw _privateConstructorUsedError;
  @JsonKey(name: 'data_count')
  int get dataCount => throw _privateConstructorUsedError;
  @JsonKey(name: 'error_message')
  String? get errorMessage => throw _privateConstructorUsedError;
  @JsonKey(name: 'created_at')
  DateTime? get createdAt => throw _privateConstructorUsedError;
  @JsonKey(name: 'updated_at')
  DateTime? get updatedAt => throw _privateConstructorUsedError;
  @JsonKey(name: 'connector_type')
  ConnectorTypeInfo? get connectorType => throw _privateConstructorUsedError;

  /// Serializes this ConnectorInstanceDetail to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ConnectorInstanceDetail
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ConnectorInstanceDetailCopyWith<ConnectorInstanceDetail> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ConnectorInstanceDetailCopyWith<$Res> {
  factory $ConnectorInstanceDetailCopyWith(ConnectorInstanceDetail value,
          $Res Function(ConnectorInstanceDetail) then) =
      _$ConnectorInstanceDetailCopyWithImpl<$Res, ConnectorInstanceDetail>;
  @useResult
  $Res call(
      {@JsonKey(name: 'instance_id') String instanceId,
      @JsonKey(name: 'display_name') String displayName,
      @JsonKey(name: 'type_id') String typeId,
      Map<String, dynamic> config,
      ConnectorState state,
      bool enabled,
      @JsonKey(name: 'auto_start') bool autoStart,
      @JsonKey(name: 'process_id') int? processId,
      @JsonKey(name: 'last_heartbeat') DateTime? lastHeartbeat,
      @JsonKey(name: 'data_count') int dataCount,
      @JsonKey(name: 'error_message') String? errorMessage,
      @JsonKey(name: 'created_at') DateTime? createdAt,
      @JsonKey(name: 'updated_at') DateTime? updatedAt,
      @JsonKey(name: 'connector_type') ConnectorTypeInfo? connectorType});

  $ConnectorTypeInfoCopyWith<$Res>? get connectorType;
}

/// @nodoc
class _$ConnectorInstanceDetailCopyWithImpl<$Res,
        $Val extends ConnectorInstanceDetail>
    implements $ConnectorInstanceDetailCopyWith<$Res> {
  _$ConnectorInstanceDetailCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ConnectorInstanceDetail
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? instanceId = null,
    Object? displayName = null,
    Object? typeId = null,
    Object? config = null,
    Object? state = null,
    Object? enabled = null,
    Object? autoStart = null,
    Object? processId = freezed,
    Object? lastHeartbeat = freezed,
    Object? dataCount = null,
    Object? errorMessage = freezed,
    Object? createdAt = freezed,
    Object? updatedAt = freezed,
    Object? connectorType = freezed,
  }) {
    return _then(_value.copyWith(
      instanceId: null == instanceId
          ? _value.instanceId
          : instanceId // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: null == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String,
      typeId: null == typeId
          ? _value.typeId
          : typeId // ignore: cast_nullable_to_non_nullable
              as String,
      config: null == config
          ? _value.config
          : config // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      state: null == state
          ? _value.state
          : state // ignore: cast_nullable_to_non_nullable
              as ConnectorState,
      enabled: null == enabled
          ? _value.enabled
          : enabled // ignore: cast_nullable_to_non_nullable
              as bool,
      autoStart: null == autoStart
          ? _value.autoStart
          : autoStart // ignore: cast_nullable_to_non_nullable
              as bool,
      processId: freezed == processId
          ? _value.processId
          : processId // ignore: cast_nullable_to_non_nullable
              as int?,
      lastHeartbeat: freezed == lastHeartbeat
          ? _value.lastHeartbeat
          : lastHeartbeat // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      dataCount: null == dataCount
          ? _value.dataCount
          : dataCount // ignore: cast_nullable_to_non_nullable
              as int,
      errorMessage: freezed == errorMessage
          ? _value.errorMessage
          : errorMessage // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      updatedAt: freezed == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      connectorType: freezed == connectorType
          ? _value.connectorType
          : connectorType // ignore: cast_nullable_to_non_nullable
              as ConnectorTypeInfo?,
    ) as $Val);
  }

  /// Create a copy of ConnectorInstanceDetail
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $ConnectorTypeInfoCopyWith<$Res>? get connectorType {
    if (_value.connectorType == null) {
      return null;
    }

    return $ConnectorTypeInfoCopyWith<$Res>(_value.connectorType!, (value) {
      return _then(_value.copyWith(connectorType: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$ConnectorInstanceDetailImplCopyWith<$Res>
    implements $ConnectorInstanceDetailCopyWith<$Res> {
  factory _$$ConnectorInstanceDetailImplCopyWith(
          _$ConnectorInstanceDetailImpl value,
          $Res Function(_$ConnectorInstanceDetailImpl) then) =
      __$$ConnectorInstanceDetailImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'instance_id') String instanceId,
      @JsonKey(name: 'display_name') String displayName,
      @JsonKey(name: 'type_id') String typeId,
      Map<String, dynamic> config,
      ConnectorState state,
      bool enabled,
      @JsonKey(name: 'auto_start') bool autoStart,
      @JsonKey(name: 'process_id') int? processId,
      @JsonKey(name: 'last_heartbeat') DateTime? lastHeartbeat,
      @JsonKey(name: 'data_count') int dataCount,
      @JsonKey(name: 'error_message') String? errorMessage,
      @JsonKey(name: 'created_at') DateTime? createdAt,
      @JsonKey(name: 'updated_at') DateTime? updatedAt,
      @JsonKey(name: 'connector_type') ConnectorTypeInfo? connectorType});

  @override
  $ConnectorTypeInfoCopyWith<$Res>? get connectorType;
}

/// @nodoc
class __$$ConnectorInstanceDetailImplCopyWithImpl<$Res>
    extends _$ConnectorInstanceDetailCopyWithImpl<$Res,
        _$ConnectorInstanceDetailImpl>
    implements _$$ConnectorInstanceDetailImplCopyWith<$Res> {
  __$$ConnectorInstanceDetailImplCopyWithImpl(
      _$ConnectorInstanceDetailImpl _value,
      $Res Function(_$ConnectorInstanceDetailImpl) _then)
      : super(_value, _then);

  /// Create a copy of ConnectorInstanceDetail
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? instanceId = null,
    Object? displayName = null,
    Object? typeId = null,
    Object? config = null,
    Object? state = null,
    Object? enabled = null,
    Object? autoStart = null,
    Object? processId = freezed,
    Object? lastHeartbeat = freezed,
    Object? dataCount = null,
    Object? errorMessage = freezed,
    Object? createdAt = freezed,
    Object? updatedAt = freezed,
    Object? connectorType = freezed,
  }) {
    return _then(_$ConnectorInstanceDetailImpl(
      instanceId: null == instanceId
          ? _value.instanceId
          : instanceId // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: null == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String,
      typeId: null == typeId
          ? _value.typeId
          : typeId // ignore: cast_nullable_to_non_nullable
              as String,
      config: null == config
          ? _value._config
          : config // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      state: null == state
          ? _value.state
          : state // ignore: cast_nullable_to_non_nullable
              as ConnectorState,
      enabled: null == enabled
          ? _value.enabled
          : enabled // ignore: cast_nullable_to_non_nullable
              as bool,
      autoStart: null == autoStart
          ? _value.autoStart
          : autoStart // ignore: cast_nullable_to_non_nullable
              as bool,
      processId: freezed == processId
          ? _value.processId
          : processId // ignore: cast_nullable_to_non_nullable
              as int?,
      lastHeartbeat: freezed == lastHeartbeat
          ? _value.lastHeartbeat
          : lastHeartbeat // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      dataCount: null == dataCount
          ? _value.dataCount
          : dataCount // ignore: cast_nullable_to_non_nullable
              as int,
      errorMessage: freezed == errorMessage
          ? _value.errorMessage
          : errorMessage // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      updatedAt: freezed == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      connectorType: freezed == connectorType
          ? _value.connectorType
          : connectorType // ignore: cast_nullable_to_non_nullable
              as ConnectorTypeInfo?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ConnectorInstanceDetailImpl implements _ConnectorInstanceDetail {
  const _$ConnectorInstanceDetailImpl(
      {@JsonKey(name: 'instance_id') required this.instanceId,
      @JsonKey(name: 'display_name') required this.displayName,
      @JsonKey(name: 'type_id') required this.typeId,
      required final Map<String, dynamic> config,
      required this.state,
      this.enabled = true,
      @JsonKey(name: 'auto_start') this.autoStart = true,
      @JsonKey(name: 'process_id') this.processId,
      @JsonKey(name: 'last_heartbeat') this.lastHeartbeat,
      @JsonKey(name: 'data_count') this.dataCount = 0,
      @JsonKey(name: 'error_message') this.errorMessage,
      @JsonKey(name: 'created_at') this.createdAt,
      @JsonKey(name: 'updated_at') this.updatedAt,
      @JsonKey(name: 'connector_type') this.connectorType})
      : _config = config;

  factory _$ConnectorInstanceDetailImpl.fromJson(Map<String, dynamic> json) =>
      _$$ConnectorInstanceDetailImplFromJson(json);

  @override
  @JsonKey(name: 'instance_id')
  final String instanceId;
  @override
  @JsonKey(name: 'display_name')
  final String displayName;
  @override
  @JsonKey(name: 'type_id')
  final String typeId;
  final Map<String, dynamic> _config;
  @override
  Map<String, dynamic> get config {
    if (_config is EqualUnmodifiableMapView) return _config;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_config);
  }

  @override
  final ConnectorState state;
  @override
  @JsonKey()
  final bool enabled;
  @override
  @JsonKey(name: 'auto_start')
  final bool autoStart;
  @override
  @JsonKey(name: 'process_id')
  final int? processId;
  @override
  @JsonKey(name: 'last_heartbeat')
  final DateTime? lastHeartbeat;
  @override
  @JsonKey(name: 'data_count')
  final int dataCount;
  @override
  @JsonKey(name: 'error_message')
  final String? errorMessage;
  @override
  @JsonKey(name: 'created_at')
  final DateTime? createdAt;
  @override
  @JsonKey(name: 'updated_at')
  final DateTime? updatedAt;
  @override
  @JsonKey(name: 'connector_type')
  final ConnectorTypeInfo? connectorType;

  @override
  String toString() {
    return 'ConnectorInstanceDetail(instanceId: $instanceId, displayName: $displayName, typeId: $typeId, config: $config, state: $state, enabled: $enabled, autoStart: $autoStart, processId: $processId, lastHeartbeat: $lastHeartbeat, dataCount: $dataCount, errorMessage: $errorMessage, createdAt: $createdAt, updatedAt: $updatedAt, connectorType: $connectorType)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ConnectorInstanceDetailImpl &&
            (identical(other.instanceId, instanceId) ||
                other.instanceId == instanceId) &&
            (identical(other.displayName, displayName) ||
                other.displayName == displayName) &&
            (identical(other.typeId, typeId) || other.typeId == typeId) &&
            const DeepCollectionEquality().equals(other._config, _config) &&
            (identical(other.state, state) || other.state == state) &&
            (identical(other.enabled, enabled) || other.enabled == enabled) &&
            (identical(other.autoStart, autoStart) ||
                other.autoStart == autoStart) &&
            (identical(other.processId, processId) ||
                other.processId == processId) &&
            (identical(other.lastHeartbeat, lastHeartbeat) ||
                other.lastHeartbeat == lastHeartbeat) &&
            (identical(other.dataCount, dataCount) ||
                other.dataCount == dataCount) &&
            (identical(other.errorMessage, errorMessage) ||
                other.errorMessage == errorMessage) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt) &&
            (identical(other.connectorType, connectorType) ||
                other.connectorType == connectorType));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      instanceId,
      displayName,
      typeId,
      const DeepCollectionEquality().hash(_config),
      state,
      enabled,
      autoStart,
      processId,
      lastHeartbeat,
      dataCount,
      errorMessage,
      createdAt,
      updatedAt,
      connectorType);

  /// Create a copy of ConnectorInstanceDetail
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ConnectorInstanceDetailImplCopyWith<_$ConnectorInstanceDetailImpl>
      get copyWith => __$$ConnectorInstanceDetailImplCopyWithImpl<
          _$ConnectorInstanceDetailImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ConnectorInstanceDetailImplToJson(
      this,
    );
  }
}

abstract class _ConnectorInstanceDetail implements ConnectorInstanceDetail {
  const factory _ConnectorInstanceDetail(
      {@JsonKey(name: 'instance_id') required final String instanceId,
      @JsonKey(name: 'display_name') required final String displayName,
      @JsonKey(name: 'type_id') required final String typeId,
      required final Map<String, dynamic> config,
      required final ConnectorState state,
      final bool enabled,
      @JsonKey(name: 'auto_start') final bool autoStart,
      @JsonKey(name: 'process_id') final int? processId,
      @JsonKey(name: 'last_heartbeat') final DateTime? lastHeartbeat,
      @JsonKey(name: 'data_count') final int dataCount,
      @JsonKey(name: 'error_message') final String? errorMessage,
      @JsonKey(name: 'created_at') final DateTime? createdAt,
      @JsonKey(name: 'updated_at') final DateTime? updatedAt,
      @JsonKey(name: 'connector_type')
      final ConnectorTypeInfo? connectorType}) = _$ConnectorInstanceDetailImpl;

  factory _ConnectorInstanceDetail.fromJson(Map<String, dynamic> json) =
      _$ConnectorInstanceDetailImpl.fromJson;

  @override
  @JsonKey(name: 'instance_id')
  String get instanceId;
  @override
  @JsonKey(name: 'display_name')
  String get displayName;
  @override
  @JsonKey(name: 'type_id')
  String get typeId;
  @override
  Map<String, dynamic> get config;
  @override
  ConnectorState get state;
  @override
  bool get enabled;
  @override
  @JsonKey(name: 'auto_start')
  bool get autoStart;
  @override
  @JsonKey(name: 'process_id')
  int? get processId;
  @override
  @JsonKey(name: 'last_heartbeat')
  DateTime? get lastHeartbeat;
  @override
  @JsonKey(name: 'data_count')
  int get dataCount;
  @override
  @JsonKey(name: 'error_message')
  String? get errorMessage;
  @override
  @JsonKey(name: 'created_at')
  DateTime? get createdAt;
  @override
  @JsonKey(name: 'updated_at')
  DateTime? get updatedAt;
  @override
  @JsonKey(name: 'connector_type')
  ConnectorTypeInfo? get connectorType;

  /// Create a copy of ConnectorInstanceDetail
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ConnectorInstanceDetailImplCopyWith<_$ConnectorInstanceDetailImpl>
      get copyWith => throw _privateConstructorUsedError;
}

OperationResponse _$OperationResponseFromJson(Map<String, dynamic> json) {
  return _OperationResponse.fromJson(json);
}

/// @nodoc
mixin _$OperationResponse {
  bool get success => throw _privateConstructorUsedError;
  String get message => throw _privateConstructorUsedError;
  @JsonKey(name: 'instance_id')
  String get instanceId => throw _privateConstructorUsedError;
  ConnectorState get state => throw _privateConstructorUsedError;
  @JsonKey(name: 'hot_reload_applied')
  bool? get hotReloadApplied => throw _privateConstructorUsedError;
  @JsonKey(name: 'requires_restart')
  bool? get requiresRestart => throw _privateConstructorUsedError;
  @JsonKey(name: 'was_running')
  bool? get wasRunning => throw _privateConstructorUsedError;

  /// Serializes this OperationResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of OperationResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $OperationResponseCopyWith<OperationResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $OperationResponseCopyWith<$Res> {
  factory $OperationResponseCopyWith(
          OperationResponse value, $Res Function(OperationResponse) then) =
      _$OperationResponseCopyWithImpl<$Res, OperationResponse>;
  @useResult
  $Res call(
      {bool success,
      String message,
      @JsonKey(name: 'instance_id') String instanceId,
      ConnectorState state,
      @JsonKey(name: 'hot_reload_applied') bool? hotReloadApplied,
      @JsonKey(name: 'requires_restart') bool? requiresRestart,
      @JsonKey(name: 'was_running') bool? wasRunning});
}

/// @nodoc
class _$OperationResponseCopyWithImpl<$Res, $Val extends OperationResponse>
    implements $OperationResponseCopyWith<$Res> {
  _$OperationResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of OperationResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? message = null,
    Object? instanceId = null,
    Object? state = null,
    Object? hotReloadApplied = freezed,
    Object? requiresRestart = freezed,
    Object? wasRunning = freezed,
  }) {
    return _then(_value.copyWith(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
      instanceId: null == instanceId
          ? _value.instanceId
          : instanceId // ignore: cast_nullable_to_non_nullable
              as String,
      state: null == state
          ? _value.state
          : state // ignore: cast_nullable_to_non_nullable
              as ConnectorState,
      hotReloadApplied: freezed == hotReloadApplied
          ? _value.hotReloadApplied
          : hotReloadApplied // ignore: cast_nullable_to_non_nullable
              as bool?,
      requiresRestart: freezed == requiresRestart
          ? _value.requiresRestart
          : requiresRestart // ignore: cast_nullable_to_non_nullable
              as bool?,
      wasRunning: freezed == wasRunning
          ? _value.wasRunning
          : wasRunning // ignore: cast_nullable_to_non_nullable
              as bool?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$OperationResponseImplCopyWith<$Res>
    implements $OperationResponseCopyWith<$Res> {
  factory _$$OperationResponseImplCopyWith(_$OperationResponseImpl value,
          $Res Function(_$OperationResponseImpl) then) =
      __$$OperationResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {bool success,
      String message,
      @JsonKey(name: 'instance_id') String instanceId,
      ConnectorState state,
      @JsonKey(name: 'hot_reload_applied') bool? hotReloadApplied,
      @JsonKey(name: 'requires_restart') bool? requiresRestart,
      @JsonKey(name: 'was_running') bool? wasRunning});
}

/// @nodoc
class __$$OperationResponseImplCopyWithImpl<$Res>
    extends _$OperationResponseCopyWithImpl<$Res, _$OperationResponseImpl>
    implements _$$OperationResponseImplCopyWith<$Res> {
  __$$OperationResponseImplCopyWithImpl(_$OperationResponseImpl _value,
      $Res Function(_$OperationResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of OperationResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? message = null,
    Object? instanceId = null,
    Object? state = null,
    Object? hotReloadApplied = freezed,
    Object? requiresRestart = freezed,
    Object? wasRunning = freezed,
  }) {
    return _then(_$OperationResponseImpl(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
      instanceId: null == instanceId
          ? _value.instanceId
          : instanceId // ignore: cast_nullable_to_non_nullable
              as String,
      state: null == state
          ? _value.state
          : state // ignore: cast_nullable_to_non_nullable
              as ConnectorState,
      hotReloadApplied: freezed == hotReloadApplied
          ? _value.hotReloadApplied
          : hotReloadApplied // ignore: cast_nullable_to_non_nullable
              as bool?,
      requiresRestart: freezed == requiresRestart
          ? _value.requiresRestart
          : requiresRestart // ignore: cast_nullable_to_non_nullable
              as bool?,
      wasRunning: freezed == wasRunning
          ? _value.wasRunning
          : wasRunning // ignore: cast_nullable_to_non_nullable
              as bool?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$OperationResponseImpl implements _OperationResponse {
  const _$OperationResponseImpl(
      {required this.success,
      required this.message,
      @JsonKey(name: 'instance_id') required this.instanceId,
      required this.state,
      @JsonKey(name: 'hot_reload_applied') this.hotReloadApplied,
      @JsonKey(name: 'requires_restart') this.requiresRestart,
      @JsonKey(name: 'was_running') this.wasRunning});

  factory _$OperationResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$OperationResponseImplFromJson(json);

  @override
  final bool success;
  @override
  final String message;
  @override
  @JsonKey(name: 'instance_id')
  final String instanceId;
  @override
  final ConnectorState state;
  @override
  @JsonKey(name: 'hot_reload_applied')
  final bool? hotReloadApplied;
  @override
  @JsonKey(name: 'requires_restart')
  final bool? requiresRestart;
  @override
  @JsonKey(name: 'was_running')
  final bool? wasRunning;

  @override
  String toString() {
    return 'OperationResponse(success: $success, message: $message, instanceId: $instanceId, state: $state, hotReloadApplied: $hotReloadApplied, requiresRestart: $requiresRestart, wasRunning: $wasRunning)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$OperationResponseImpl &&
            (identical(other.success, success) || other.success == success) &&
            (identical(other.message, message) || other.message == message) &&
            (identical(other.instanceId, instanceId) ||
                other.instanceId == instanceId) &&
            (identical(other.state, state) || other.state == state) &&
            (identical(other.hotReloadApplied, hotReloadApplied) ||
                other.hotReloadApplied == hotReloadApplied) &&
            (identical(other.requiresRestart, requiresRestart) ||
                other.requiresRestart == requiresRestart) &&
            (identical(other.wasRunning, wasRunning) ||
                other.wasRunning == wasRunning));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, success, message, instanceId,
      state, hotReloadApplied, requiresRestart, wasRunning);

  /// Create a copy of OperationResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$OperationResponseImplCopyWith<_$OperationResponseImpl> get copyWith =>
      __$$OperationResponseImplCopyWithImpl<_$OperationResponseImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$OperationResponseImplToJson(
      this,
    );
  }
}

abstract class _OperationResponse implements OperationResponse {
  const factory _OperationResponse(
          {required final bool success,
          required final String message,
          @JsonKey(name: 'instance_id') required final String instanceId,
          required final ConnectorState state,
          @JsonKey(name: 'hot_reload_applied') final bool? hotReloadApplied,
          @JsonKey(name: 'requires_restart') final bool? requiresRestart,
          @JsonKey(name: 'was_running') final bool? wasRunning}) =
      _$OperationResponseImpl;

  factory _OperationResponse.fromJson(Map<String, dynamic> json) =
      _$OperationResponseImpl.fromJson;

  @override
  bool get success;
  @override
  String get message;
  @override
  @JsonKey(name: 'instance_id')
  String get instanceId;
  @override
  ConnectorState get state;
  @override
  @JsonKey(name: 'hot_reload_applied')
  bool? get hotReloadApplied;
  @override
  @JsonKey(name: 'requires_restart')
  bool? get requiresRestart;
  @override
  @JsonKey(name: 'was_running')
  bool? get wasRunning;

  /// Create a copy of OperationResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$OperationResponseImplCopyWith<_$OperationResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
