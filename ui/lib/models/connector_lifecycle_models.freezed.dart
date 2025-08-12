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

ConnectorDefinition _$ConnectorDefinitionFromJson(Map<String, dynamic> json) {
  return _ConnectorDefinition.fromJson(json);
}

/// @nodoc
mixin _$ConnectorDefinition {
  @JsonKey(name: 'connector_id')
  String get connectorId => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  @JsonKey(name: 'display_name')
  String get displayName => throw _privateConstructorUsedError;
  String get description => throw _privateConstructorUsedError;
  String get category => throw _privateConstructorUsedError;
  String get version => throw _privateConstructorUsedError;
  String get author => throw _privateConstructorUsedError;
  String get license => throw _privateConstructorUsedError;
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
  @JsonKey(name: 'config_default_values')
  Map<String, dynamic> get defaultConfig =>
      throw _privateConstructorUsedError; // 添加path字段来直接处理路径信息
  String? get path => throw _privateConstructorUsedError;
  @JsonKey(name: 'is_registered')
  bool? get isRegistered => throw _privateConstructorUsedError; // Registry 相关字段
  @JsonKey(name: 'download_url')
  String? get downloadUrl => throw _privateConstructorUsedError;
  Map<String, dynamic> get platforms => throw _privateConstructorUsedError;
  Map<String, dynamic> get capabilities => throw _privateConstructorUsedError;
  @JsonKey(name: 'last_updated')
  String? get lastUpdated => throw _privateConstructorUsedError;

  /// Serializes this ConnectorDefinition to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ConnectorDefinition
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ConnectorDefinitionCopyWith<ConnectorDefinition> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ConnectorDefinitionCopyWith<$Res> {
  factory $ConnectorDefinitionCopyWith(
          ConnectorDefinition value, $Res Function(ConnectorDefinition) then) =
      _$ConnectorDefinitionCopyWithImpl<$Res, ConnectorDefinition>;
  @useResult
  $Res call(
      {@JsonKey(name: 'connector_id') String connectorId,
      String name,
      @JsonKey(name: 'display_name') String displayName,
      String description,
      String category,
      String version,
      String author,
      String license,
      @JsonKey(name: 'auto_discovery') bool autoDiscovery,
      @JsonKey(name: 'hot_config_reload') bool hotConfigReload,
      @JsonKey(name: 'health_check') bool healthCheck,
      @JsonKey(name: 'entry_point') String entryPoint,
      List<String> dependencies,
      List<String> permissions,
      @JsonKey(name: 'config_schema') Map<String, dynamic> configSchema,
      @JsonKey(name: 'config_default_values')
      Map<String, dynamic> defaultConfig,
      String? path,
      @JsonKey(name: 'is_registered') bool? isRegistered,
      @JsonKey(name: 'download_url') String? downloadUrl,
      Map<String, dynamic> platforms,
      Map<String, dynamic> capabilities,
      @JsonKey(name: 'last_updated') String? lastUpdated});
}

/// @nodoc
class _$ConnectorDefinitionCopyWithImpl<$Res, $Val extends ConnectorDefinition>
    implements $ConnectorDefinitionCopyWith<$Res> {
  _$ConnectorDefinitionCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ConnectorDefinition
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? connectorId = null,
    Object? name = null,
    Object? displayName = null,
    Object? description = null,
    Object? category = null,
    Object? version = null,
    Object? author = null,
    Object? license = null,
    Object? autoDiscovery = null,
    Object? hotConfigReload = null,
    Object? healthCheck = null,
    Object? entryPoint = null,
    Object? dependencies = null,
    Object? permissions = null,
    Object? configSchema = null,
    Object? defaultConfig = null,
    Object? path = freezed,
    Object? isRegistered = freezed,
    Object? downloadUrl = freezed,
    Object? platforms = null,
    Object? capabilities = null,
    Object? lastUpdated = freezed,
  }) {
    return _then(_value.copyWith(
      connectorId: null == connectorId
          ? _value.connectorId
          : connectorId // ignore: cast_nullable_to_non_nullable
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
      path: freezed == path
          ? _value.path
          : path // ignore: cast_nullable_to_non_nullable
              as String?,
      isRegistered: freezed == isRegistered
          ? _value.isRegistered
          : isRegistered // ignore: cast_nullable_to_non_nullable
              as bool?,
      downloadUrl: freezed == downloadUrl
          ? _value.downloadUrl
          : downloadUrl // ignore: cast_nullable_to_non_nullable
              as String?,
      platforms: null == platforms
          ? _value.platforms
          : platforms // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      capabilities: null == capabilities
          ? _value.capabilities
          : capabilities // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      lastUpdated: freezed == lastUpdated
          ? _value.lastUpdated
          : lastUpdated // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ConnectorDefinitionImplCopyWith<$Res>
    implements $ConnectorDefinitionCopyWith<$Res> {
  factory _$$ConnectorDefinitionImplCopyWith(_$ConnectorDefinitionImpl value,
          $Res Function(_$ConnectorDefinitionImpl) then) =
      __$$ConnectorDefinitionImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'connector_id') String connectorId,
      String name,
      @JsonKey(name: 'display_name') String displayName,
      String description,
      String category,
      String version,
      String author,
      String license,
      @JsonKey(name: 'auto_discovery') bool autoDiscovery,
      @JsonKey(name: 'hot_config_reload') bool hotConfigReload,
      @JsonKey(name: 'health_check') bool healthCheck,
      @JsonKey(name: 'entry_point') String entryPoint,
      List<String> dependencies,
      List<String> permissions,
      @JsonKey(name: 'config_schema') Map<String, dynamic> configSchema,
      @JsonKey(name: 'config_default_values')
      Map<String, dynamic> defaultConfig,
      String? path,
      @JsonKey(name: 'is_registered') bool? isRegistered,
      @JsonKey(name: 'download_url') String? downloadUrl,
      Map<String, dynamic> platforms,
      Map<String, dynamic> capabilities,
      @JsonKey(name: 'last_updated') String? lastUpdated});
}

/// @nodoc
class __$$ConnectorDefinitionImplCopyWithImpl<$Res>
    extends _$ConnectorDefinitionCopyWithImpl<$Res, _$ConnectorDefinitionImpl>
    implements _$$ConnectorDefinitionImplCopyWith<$Res> {
  __$$ConnectorDefinitionImplCopyWithImpl(_$ConnectorDefinitionImpl _value,
      $Res Function(_$ConnectorDefinitionImpl) _then)
      : super(_value, _then);

  /// Create a copy of ConnectorDefinition
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? connectorId = null,
    Object? name = null,
    Object? displayName = null,
    Object? description = null,
    Object? category = null,
    Object? version = null,
    Object? author = null,
    Object? license = null,
    Object? autoDiscovery = null,
    Object? hotConfigReload = null,
    Object? healthCheck = null,
    Object? entryPoint = null,
    Object? dependencies = null,
    Object? permissions = null,
    Object? configSchema = null,
    Object? defaultConfig = null,
    Object? path = freezed,
    Object? isRegistered = freezed,
    Object? downloadUrl = freezed,
    Object? platforms = null,
    Object? capabilities = null,
    Object? lastUpdated = freezed,
  }) {
    return _then(_$ConnectorDefinitionImpl(
      connectorId: null == connectorId
          ? _value.connectorId
          : connectorId // ignore: cast_nullable_to_non_nullable
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
      path: freezed == path
          ? _value.path
          : path // ignore: cast_nullable_to_non_nullable
              as String?,
      isRegistered: freezed == isRegistered
          ? _value.isRegistered
          : isRegistered // ignore: cast_nullable_to_non_nullable
              as bool?,
      downloadUrl: freezed == downloadUrl
          ? _value.downloadUrl
          : downloadUrl // ignore: cast_nullable_to_non_nullable
              as String?,
      platforms: null == platforms
          ? _value._platforms
          : platforms // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      capabilities: null == capabilities
          ? _value._capabilities
          : capabilities // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      lastUpdated: freezed == lastUpdated
          ? _value.lastUpdated
          : lastUpdated // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ConnectorDefinitionImpl implements _ConnectorDefinition {
  const _$ConnectorDefinitionImpl(
      {@JsonKey(name: 'connector_id') required this.connectorId,
      required this.name,
      @JsonKey(name: 'display_name') required this.displayName,
      required this.description,
      required this.category,
      required this.version,
      required this.author,
      this.license = '',
      @JsonKey(name: 'auto_discovery') this.autoDiscovery = false,
      @JsonKey(name: 'hot_config_reload') this.hotConfigReload = true,
      @JsonKey(name: 'health_check') this.healthCheck = true,
      @JsonKey(name: 'entry_point') this.entryPoint = 'main.py',
      final List<String> dependencies = const [],
      final List<String> permissions = const [],
      @JsonKey(name: 'config_schema')
      final Map<String, dynamic> configSchema = const {},
      @JsonKey(name: 'config_default_values')
      final Map<String, dynamic> defaultConfig = const {},
      this.path,
      @JsonKey(name: 'is_registered') this.isRegistered,
      @JsonKey(name: 'download_url') this.downloadUrl,
      final Map<String, dynamic> platforms = const {},
      final Map<String, dynamic> capabilities = const {},
      @JsonKey(name: 'last_updated') this.lastUpdated})
      : _dependencies = dependencies,
        _permissions = permissions,
        _configSchema = configSchema,
        _defaultConfig = defaultConfig,
        _platforms = platforms,
        _capabilities = capabilities;

  factory _$ConnectorDefinitionImpl.fromJson(Map<String, dynamic> json) =>
      _$$ConnectorDefinitionImplFromJson(json);

  @override
  @JsonKey(name: 'connector_id')
  final String connectorId;
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
  @JsonKey(name: 'config_default_values')
  Map<String, dynamic> get defaultConfig {
    if (_defaultConfig is EqualUnmodifiableMapView) return _defaultConfig;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_defaultConfig);
  }

// 添加path字段来直接处理路径信息
  @override
  final String? path;
  @override
  @JsonKey(name: 'is_registered')
  final bool? isRegistered;
// Registry 相关字段
  @override
  @JsonKey(name: 'download_url')
  final String? downloadUrl;
  final Map<String, dynamic> _platforms;
  @override
  @JsonKey()
  Map<String, dynamic> get platforms {
    if (_platforms is EqualUnmodifiableMapView) return _platforms;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_platforms);
  }

  final Map<String, dynamic> _capabilities;
  @override
  @JsonKey()
  Map<String, dynamic> get capabilities {
    if (_capabilities is EqualUnmodifiableMapView) return _capabilities;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_capabilities);
  }

  @override
  @JsonKey(name: 'last_updated')
  final String? lastUpdated;

  @override
  String toString() {
    return 'ConnectorDefinition(connectorId: $connectorId, name: $name, displayName: $displayName, description: $description, category: $category, version: $version, author: $author, license: $license, autoDiscovery: $autoDiscovery, hotConfigReload: $hotConfigReload, healthCheck: $healthCheck, entryPoint: $entryPoint, dependencies: $dependencies, permissions: $permissions, configSchema: $configSchema, defaultConfig: $defaultConfig, path: $path, isRegistered: $isRegistered, downloadUrl: $downloadUrl, platforms: $platforms, capabilities: $capabilities, lastUpdated: $lastUpdated)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ConnectorDefinitionImpl &&
            (identical(other.connectorId, connectorId) ||
                other.connectorId == connectorId) &&
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
            (identical(other.path, path) || other.path == path) &&
            (identical(other.isRegistered, isRegistered) ||
                other.isRegistered == isRegistered) &&
            (identical(other.downloadUrl, downloadUrl) ||
                other.downloadUrl == downloadUrl) &&
            const DeepCollectionEquality()
                .equals(other._platforms, _platforms) &&
            const DeepCollectionEquality()
                .equals(other._capabilities, _capabilities) &&
            (identical(other.lastUpdated, lastUpdated) ||
                other.lastUpdated == lastUpdated));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hashAll([
        runtimeType,
        connectorId,
        name,
        displayName,
        description,
        category,
        version,
        author,
        license,
        autoDiscovery,
        hotConfigReload,
        healthCheck,
        entryPoint,
        const DeepCollectionEquality().hash(_dependencies),
        const DeepCollectionEquality().hash(_permissions),
        const DeepCollectionEquality().hash(_configSchema),
        const DeepCollectionEquality().hash(_defaultConfig),
        path,
        isRegistered,
        downloadUrl,
        const DeepCollectionEquality().hash(_platforms),
        const DeepCollectionEquality().hash(_capabilities),
        lastUpdated
      ]);

  /// Create a copy of ConnectorDefinition
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ConnectorDefinitionImplCopyWith<_$ConnectorDefinitionImpl> get copyWith =>
      __$$ConnectorDefinitionImplCopyWithImpl<_$ConnectorDefinitionImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ConnectorDefinitionImplToJson(
      this,
    );
  }
}

abstract class _ConnectorDefinition implements ConnectorDefinition {
  const factory _ConnectorDefinition(
      {@JsonKey(name: 'connector_id') required final String connectorId,
      required final String name,
      @JsonKey(name: 'display_name') required final String displayName,
      required final String description,
      required final String category,
      required final String version,
      required final String author,
      final String license,
      @JsonKey(name: 'auto_discovery') final bool autoDiscovery,
      @JsonKey(name: 'hot_config_reload') final bool hotConfigReload,
      @JsonKey(name: 'health_check') final bool healthCheck,
      @JsonKey(name: 'entry_point') final String entryPoint,
      final List<String> dependencies,
      final List<String> permissions,
      @JsonKey(name: 'config_schema') final Map<String, dynamic> configSchema,
      @JsonKey(name: 'config_default_values')
      final Map<String, dynamic> defaultConfig,
      final String? path,
      @JsonKey(name: 'is_registered') final bool? isRegistered,
      @JsonKey(name: 'download_url') final String? downloadUrl,
      final Map<String, dynamic> platforms,
      final Map<String, dynamic> capabilities,
      @JsonKey(name: 'last_updated')
      final String? lastUpdated}) = _$ConnectorDefinitionImpl;

  factory _ConnectorDefinition.fromJson(Map<String, dynamic> json) =
      _$ConnectorDefinitionImpl.fromJson;

  @override
  @JsonKey(name: 'connector_id')
  String get connectorId;
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
  @JsonKey(name: 'config_default_values')
  Map<String, dynamic> get defaultConfig; // 添加path字段来直接处理路径信息
  @override
  String? get path;
  @override
  @JsonKey(name: 'is_registered')
  bool? get isRegistered; // Registry 相关字段
  @override
  @JsonKey(name: 'download_url')
  String? get downloadUrl;
  @override
  Map<String, dynamic> get platforms;
  @override
  Map<String, dynamic> get capabilities;
  @override
  @JsonKey(name: 'last_updated')
  String? get lastUpdated;

  /// Create a copy of ConnectorDefinition
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ConnectorDefinitionImplCopyWith<_$ConnectorDefinitionImpl> get copyWith =>
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

ConnectorInfo _$ConnectorInfoFromJson(Map<String, dynamic> json) {
  return _ConnectorInfo.fromJson(json);
}

/// @nodoc
mixin _$ConnectorInfo {
  @JsonKey(name: 'connector_id')
  String get connectorId => throw _privateConstructorUsedError;
  @JsonKey(name: 'display_name')
  String get displayName => throw _privateConstructorUsedError;
  ConnectorState get state => throw _privateConstructorUsedError;
  bool get enabled =>
      throw _privateConstructorUsedError; // 移除 auto_start 字段，因为数据库模型已经简化了逻辑
  @JsonKey(name: 'process_id', fromJson: _processIdFromJson)
  int? get processId => throw _privateConstructorUsedError;
  @JsonKey(name: 'last_heartbeat')
  DateTime? get lastHeartbeat => throw _privateConstructorUsedError;
  @JsonKey(name: 'data_count', fromJson: _dataCountFromJson)
  int get dataCount => throw _privateConstructorUsedError;
  @JsonKey(name: 'error_message')
  String? get errorMessage => throw _privateConstructorUsedError;
  @JsonKey(name: 'created_at')
  DateTime? get createdAt => throw _privateConstructorUsedError;
  @JsonKey(name: 'updated_at')
  DateTime? get updatedAt => throw _privateConstructorUsedError; // 添加运行时间相关字段
  @JsonKey(name: 'uptime_seconds')
  int? get uptimeSeconds => throw _privateConstructorUsedError;
  @JsonKey(name: 'started_at')
  DateTime? get startedAt => throw _privateConstructorUsedError;
  Map<String, dynamic> get config => throw _privateConstructorUsedError;

  /// Serializes this ConnectorInfo to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ConnectorInfo
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ConnectorInfoCopyWith<ConnectorInfo> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ConnectorInfoCopyWith<$Res> {
  factory $ConnectorInfoCopyWith(
          ConnectorInfo value, $Res Function(ConnectorInfo) then) =
      _$ConnectorInfoCopyWithImpl<$Res, ConnectorInfo>;
  @useResult
  $Res call(
      {@JsonKey(name: 'connector_id') String connectorId,
      @JsonKey(name: 'display_name') String displayName,
      ConnectorState state,
      bool enabled,
      @JsonKey(name: 'process_id', fromJson: _processIdFromJson) int? processId,
      @JsonKey(name: 'last_heartbeat') DateTime? lastHeartbeat,
      @JsonKey(name: 'data_count', fromJson: _dataCountFromJson) int dataCount,
      @JsonKey(name: 'error_message') String? errorMessage,
      @JsonKey(name: 'created_at') DateTime? createdAt,
      @JsonKey(name: 'updated_at') DateTime? updatedAt,
      @JsonKey(name: 'uptime_seconds') int? uptimeSeconds,
      @JsonKey(name: 'started_at') DateTime? startedAt,
      Map<String, dynamic> config});
}

/// @nodoc
class _$ConnectorInfoCopyWithImpl<$Res, $Val extends ConnectorInfo>
    implements $ConnectorInfoCopyWith<$Res> {
  _$ConnectorInfoCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ConnectorInfo
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? connectorId = null,
    Object? displayName = null,
    Object? state = null,
    Object? enabled = null,
    Object? processId = freezed,
    Object? lastHeartbeat = freezed,
    Object? dataCount = null,
    Object? errorMessage = freezed,
    Object? createdAt = freezed,
    Object? updatedAt = freezed,
    Object? uptimeSeconds = freezed,
    Object? startedAt = freezed,
    Object? config = null,
  }) {
    return _then(_value.copyWith(
      connectorId: null == connectorId
          ? _value.connectorId
          : connectorId // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: null == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String,
      state: null == state
          ? _value.state
          : state // ignore: cast_nullable_to_non_nullable
              as ConnectorState,
      enabled: null == enabled
          ? _value.enabled
          : enabled // ignore: cast_nullable_to_non_nullable
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
      uptimeSeconds: freezed == uptimeSeconds
          ? _value.uptimeSeconds
          : uptimeSeconds // ignore: cast_nullable_to_non_nullable
              as int?,
      startedAt: freezed == startedAt
          ? _value.startedAt
          : startedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      config: null == config
          ? _value.config
          : config // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ConnectorInfoImplCopyWith<$Res>
    implements $ConnectorInfoCopyWith<$Res> {
  factory _$$ConnectorInfoImplCopyWith(
          _$ConnectorInfoImpl value, $Res Function(_$ConnectorInfoImpl) then) =
      __$$ConnectorInfoImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'connector_id') String connectorId,
      @JsonKey(name: 'display_name') String displayName,
      ConnectorState state,
      bool enabled,
      @JsonKey(name: 'process_id', fromJson: _processIdFromJson) int? processId,
      @JsonKey(name: 'last_heartbeat') DateTime? lastHeartbeat,
      @JsonKey(name: 'data_count', fromJson: _dataCountFromJson) int dataCount,
      @JsonKey(name: 'error_message') String? errorMessage,
      @JsonKey(name: 'created_at') DateTime? createdAt,
      @JsonKey(name: 'updated_at') DateTime? updatedAt,
      @JsonKey(name: 'uptime_seconds') int? uptimeSeconds,
      @JsonKey(name: 'started_at') DateTime? startedAt,
      Map<String, dynamic> config});
}

/// @nodoc
class __$$ConnectorInfoImplCopyWithImpl<$Res>
    extends _$ConnectorInfoCopyWithImpl<$Res, _$ConnectorInfoImpl>
    implements _$$ConnectorInfoImplCopyWith<$Res> {
  __$$ConnectorInfoImplCopyWithImpl(
      _$ConnectorInfoImpl _value, $Res Function(_$ConnectorInfoImpl) _then)
      : super(_value, _then);

  /// Create a copy of ConnectorInfo
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? connectorId = null,
    Object? displayName = null,
    Object? state = null,
    Object? enabled = null,
    Object? processId = freezed,
    Object? lastHeartbeat = freezed,
    Object? dataCount = null,
    Object? errorMessage = freezed,
    Object? createdAt = freezed,
    Object? updatedAt = freezed,
    Object? uptimeSeconds = freezed,
    Object? startedAt = freezed,
    Object? config = null,
  }) {
    return _then(_$ConnectorInfoImpl(
      connectorId: null == connectorId
          ? _value.connectorId
          : connectorId // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: null == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String,
      state: null == state
          ? _value.state
          : state // ignore: cast_nullable_to_non_nullable
              as ConnectorState,
      enabled: null == enabled
          ? _value.enabled
          : enabled // ignore: cast_nullable_to_non_nullable
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
      uptimeSeconds: freezed == uptimeSeconds
          ? _value.uptimeSeconds
          : uptimeSeconds // ignore: cast_nullable_to_non_nullable
              as int?,
      startedAt: freezed == startedAt
          ? _value.startedAt
          : startedAt // ignore: cast_nullable_to_non_nullable
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
class _$ConnectorInfoImpl implements _ConnectorInfo {
  const _$ConnectorInfoImpl(
      {@JsonKey(name: 'connector_id') required this.connectorId,
      @JsonKey(name: 'display_name') required this.displayName,
      required this.state,
      this.enabled = true,
      @JsonKey(name: 'process_id', fromJson: _processIdFromJson) this.processId,
      @JsonKey(name: 'last_heartbeat') this.lastHeartbeat,
      @JsonKey(name: 'data_count', fromJson: _dataCountFromJson)
      this.dataCount = 0,
      @JsonKey(name: 'error_message') this.errorMessage,
      @JsonKey(name: 'created_at') this.createdAt,
      @JsonKey(name: 'updated_at') this.updatedAt,
      @JsonKey(name: 'uptime_seconds') this.uptimeSeconds,
      @JsonKey(name: 'started_at') this.startedAt,
      final Map<String, dynamic> config = const {}})
      : _config = config;

  factory _$ConnectorInfoImpl.fromJson(Map<String, dynamic> json) =>
      _$$ConnectorInfoImplFromJson(json);

  @override
  @JsonKey(name: 'connector_id')
  final String connectorId;
  @override
  @JsonKey(name: 'display_name')
  final String displayName;
  @override
  final ConnectorState state;
  @override
  @JsonKey()
  final bool enabled;
// 移除 auto_start 字段，因为数据库模型已经简化了逻辑
  @override
  @JsonKey(name: 'process_id', fromJson: _processIdFromJson)
  final int? processId;
  @override
  @JsonKey(name: 'last_heartbeat')
  final DateTime? lastHeartbeat;
  @override
  @JsonKey(name: 'data_count', fromJson: _dataCountFromJson)
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
// 添加运行时间相关字段
  @override
  @JsonKey(name: 'uptime_seconds')
  final int? uptimeSeconds;
  @override
  @JsonKey(name: 'started_at')
  final DateTime? startedAt;
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
    return 'ConnectorInfo(connectorId: $connectorId, displayName: $displayName, state: $state, enabled: $enabled, processId: $processId, lastHeartbeat: $lastHeartbeat, dataCount: $dataCount, errorMessage: $errorMessage, createdAt: $createdAt, updatedAt: $updatedAt, uptimeSeconds: $uptimeSeconds, startedAt: $startedAt, config: $config)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ConnectorInfoImpl &&
            (identical(other.connectorId, connectorId) ||
                other.connectorId == connectorId) &&
            (identical(other.displayName, displayName) ||
                other.displayName == displayName) &&
            (identical(other.state, state) || other.state == state) &&
            (identical(other.enabled, enabled) || other.enabled == enabled) &&
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
            (identical(other.uptimeSeconds, uptimeSeconds) ||
                other.uptimeSeconds == uptimeSeconds) &&
            (identical(other.startedAt, startedAt) ||
                other.startedAt == startedAt) &&
            const DeepCollectionEquality().equals(other._config, _config));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      connectorId,
      displayName,
      state,
      enabled,
      processId,
      lastHeartbeat,
      dataCount,
      errorMessage,
      createdAt,
      updatedAt,
      uptimeSeconds,
      startedAt,
      const DeepCollectionEquality().hash(_config));

  /// Create a copy of ConnectorInfo
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ConnectorInfoImplCopyWith<_$ConnectorInfoImpl> get copyWith =>
      __$$ConnectorInfoImplCopyWithImpl<_$ConnectorInfoImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ConnectorInfoImplToJson(
      this,
    );
  }
}

abstract class _ConnectorInfo implements ConnectorInfo {
  const factory _ConnectorInfo(
      {@JsonKey(name: 'connector_id') required final String connectorId,
      @JsonKey(name: 'display_name') required final String displayName,
      required final ConnectorState state,
      final bool enabled,
      @JsonKey(name: 'process_id', fromJson: _processIdFromJson)
      final int? processId,
      @JsonKey(name: 'last_heartbeat') final DateTime? lastHeartbeat,
      @JsonKey(name: 'data_count', fromJson: _dataCountFromJson)
      final int dataCount,
      @JsonKey(name: 'error_message') final String? errorMessage,
      @JsonKey(name: 'created_at') final DateTime? createdAt,
      @JsonKey(name: 'updated_at') final DateTime? updatedAt,
      @JsonKey(name: 'uptime_seconds') final int? uptimeSeconds,
      @JsonKey(name: 'started_at') final DateTime? startedAt,
      final Map<String, dynamic> config}) = _$ConnectorInfoImpl;

  factory _ConnectorInfo.fromJson(Map<String, dynamic> json) =
      _$ConnectorInfoImpl.fromJson;

  @override
  @JsonKey(name: 'connector_id')
  String get connectorId;
  @override
  @JsonKey(name: 'display_name')
  String get displayName;
  @override
  ConnectorState get state;
  @override
  bool get enabled; // 移除 auto_start 字段，因为数据库模型已经简化了逻辑
  @override
  @JsonKey(name: 'process_id', fromJson: _processIdFromJson)
  int? get processId;
  @override
  @JsonKey(name: 'last_heartbeat')
  DateTime? get lastHeartbeat;
  @override
  @JsonKey(name: 'data_count', fromJson: _dataCountFromJson)
  int get dataCount;
  @override
  @JsonKey(name: 'error_message')
  String? get errorMessage;
  @override
  @JsonKey(name: 'created_at')
  DateTime? get createdAt;
  @override
  @JsonKey(name: 'updated_at')
  DateTime? get updatedAt; // 添加运行时间相关字段
  @override
  @JsonKey(name: 'uptime_seconds')
  int? get uptimeSeconds;
  @override
  @JsonKey(name: 'started_at')
  DateTime? get startedAt;
  @override
  Map<String, dynamic> get config;

  /// Create a copy of ConnectorInfo
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ConnectorInfoImplCopyWith<_$ConnectorInfoImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

InstallConnectorRequest _$InstallConnectorRequestFromJson(
    Map<String, dynamic> json) {
  return _InstallConnectorRequest.fromJson(json);
}

/// @nodoc
mixin _$InstallConnectorRequest {
  @JsonKey(name: 'connector_id')
  String get connectorId => throw _privateConstructorUsedError;
  @JsonKey(name: 'source')
  String get source =>
      throw _privateConstructorUsedError; // registry, manual, scan
  @JsonKey(name: 'display_name')
  String? get displayName => throw _privateConstructorUsedError;
  Map<String, dynamic> get config =>
      throw _privateConstructorUsedError; // 移除 auto_start 字段，因为数据库模型已经简化了逻辑
  String? get path => throw _privateConstructorUsedError; // for scan source
  String? get description => throw _privateConstructorUsedError;

  /// Serializes this InstallConnectorRequest to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of InstallConnectorRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $InstallConnectorRequestCopyWith<InstallConnectorRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $InstallConnectorRequestCopyWith<$Res> {
  factory $InstallConnectorRequestCopyWith(InstallConnectorRequest value,
          $Res Function(InstallConnectorRequest) then) =
      _$InstallConnectorRequestCopyWithImpl<$Res, InstallConnectorRequest>;
  @useResult
  $Res call(
      {@JsonKey(name: 'connector_id') String connectorId,
      @JsonKey(name: 'source') String source,
      @JsonKey(name: 'display_name') String? displayName,
      Map<String, dynamic> config,
      String? path,
      String? description});
}

/// @nodoc
class _$InstallConnectorRequestCopyWithImpl<$Res,
        $Val extends InstallConnectorRequest>
    implements $InstallConnectorRequestCopyWith<$Res> {
  _$InstallConnectorRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of InstallConnectorRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? connectorId = null,
    Object? source = null,
    Object? displayName = freezed,
    Object? config = null,
    Object? path = freezed,
    Object? description = freezed,
  }) {
    return _then(_value.copyWith(
      connectorId: null == connectorId
          ? _value.connectorId
          : connectorId // ignore: cast_nullable_to_non_nullable
              as String,
      source: null == source
          ? _value.source
          : source // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: freezed == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String?,
      config: null == config
          ? _value.config
          : config // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      path: freezed == path
          ? _value.path
          : path // ignore: cast_nullable_to_non_nullable
              as String?,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$InstallConnectorRequestImplCopyWith<$Res>
    implements $InstallConnectorRequestCopyWith<$Res> {
  factory _$$InstallConnectorRequestImplCopyWith(
          _$InstallConnectorRequestImpl value,
          $Res Function(_$InstallConnectorRequestImpl) then) =
      __$$InstallConnectorRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'connector_id') String connectorId,
      @JsonKey(name: 'source') String source,
      @JsonKey(name: 'display_name') String? displayName,
      Map<String, dynamic> config,
      String? path,
      String? description});
}

/// @nodoc
class __$$InstallConnectorRequestImplCopyWithImpl<$Res>
    extends _$InstallConnectorRequestCopyWithImpl<$Res,
        _$InstallConnectorRequestImpl>
    implements _$$InstallConnectorRequestImplCopyWith<$Res> {
  __$$InstallConnectorRequestImplCopyWithImpl(
      _$InstallConnectorRequestImpl _value,
      $Res Function(_$InstallConnectorRequestImpl) _then)
      : super(_value, _then);

  /// Create a copy of InstallConnectorRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? connectorId = null,
    Object? source = null,
    Object? displayName = freezed,
    Object? config = null,
    Object? path = freezed,
    Object? description = freezed,
  }) {
    return _then(_$InstallConnectorRequestImpl(
      connectorId: null == connectorId
          ? _value.connectorId
          : connectorId // ignore: cast_nullable_to_non_nullable
              as String,
      source: null == source
          ? _value.source
          : source // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: freezed == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String?,
      config: null == config
          ? _value._config
          : config // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      path: freezed == path
          ? _value.path
          : path // ignore: cast_nullable_to_non_nullable
              as String?,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$InstallConnectorRequestImpl implements _InstallConnectorRequest {
  const _$InstallConnectorRequestImpl(
      {@JsonKey(name: 'connector_id') required this.connectorId,
      @JsonKey(name: 'source') this.source = 'registry',
      @JsonKey(name: 'display_name') this.displayName,
      final Map<String, dynamic> config = const {},
      this.path,
      this.description})
      : _config = config;

  factory _$InstallConnectorRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$InstallConnectorRequestImplFromJson(json);

  @override
  @JsonKey(name: 'connector_id')
  final String connectorId;
  @override
  @JsonKey(name: 'source')
  final String source;
// registry, manual, scan
  @override
  @JsonKey(name: 'display_name')
  final String? displayName;
  final Map<String, dynamic> _config;
  @override
  @JsonKey()
  Map<String, dynamic> get config {
    if (_config is EqualUnmodifiableMapView) return _config;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_config);
  }

// 移除 auto_start 字段，因为数据库模型已经简化了逻辑
  @override
  final String? path;
// for scan source
  @override
  final String? description;

  @override
  String toString() {
    return 'InstallConnectorRequest(connectorId: $connectorId, source: $source, displayName: $displayName, config: $config, path: $path, description: $description)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$InstallConnectorRequestImpl &&
            (identical(other.connectorId, connectorId) ||
                other.connectorId == connectorId) &&
            (identical(other.source, source) || other.source == source) &&
            (identical(other.displayName, displayName) ||
                other.displayName == displayName) &&
            const DeepCollectionEquality().equals(other._config, _config) &&
            (identical(other.path, path) || other.path == path) &&
            (identical(other.description, description) ||
                other.description == description));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, connectorId, source, displayName,
      const DeepCollectionEquality().hash(_config), path, description);

  /// Create a copy of InstallConnectorRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$InstallConnectorRequestImplCopyWith<_$InstallConnectorRequestImpl>
      get copyWith => __$$InstallConnectorRequestImplCopyWithImpl<
          _$InstallConnectorRequestImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$InstallConnectorRequestImplToJson(
      this,
    );
  }
}

abstract class _InstallConnectorRequest implements InstallConnectorRequest {
  const factory _InstallConnectorRequest(
      {@JsonKey(name: 'connector_id') required final String connectorId,
      @JsonKey(name: 'source') final String source,
      @JsonKey(name: 'display_name') final String? displayName,
      final Map<String, dynamic> config,
      final String? path,
      final String? description}) = _$InstallConnectorRequestImpl;

  factory _InstallConnectorRequest.fromJson(Map<String, dynamic> json) =
      _$InstallConnectorRequestImpl.fromJson;

  @override
  @JsonKey(name: 'connector_id')
  String get connectorId;
  @override
  @JsonKey(name: 'source')
  String get source; // registry, manual, scan
  @override
  @JsonKey(name: 'display_name')
  String? get displayName;
  @override
  Map<String, dynamic> get config; // 移除 auto_start 字段，因为数据库模型已经简化了逻辑
  @override
  String? get path; // for scan source
  @override
  String? get description;

  /// Create a copy of InstallConnectorRequest
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$InstallConnectorRequestImplCopyWith<_$InstallConnectorRequestImpl>
      get copyWith => throw _privateConstructorUsedError;
}

CreateConnectorRequest _$CreateConnectorRequestFromJson(
    Map<String, dynamic> json) {
  return _CreateConnectorRequest.fromJson(json);
}

/// @nodoc
mixin _$CreateConnectorRequest {
  @JsonKey(name: 'connector_id')
  String get connectorId => throw _privateConstructorUsedError;
  @JsonKey(name: 'display_name')
  String get displayName => throw _privateConstructorUsedError;
  Map<String, dynamic> get config =>
      throw _privateConstructorUsedError; // 移除 auto_start 字段，因为数据库模型已经简化了逻辑
  @JsonKey(name: 'template_id')
  String? get templateId => throw _privateConstructorUsedError;

  /// Serializes this CreateConnectorRequest to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CreateConnectorRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CreateConnectorRequestCopyWith<CreateConnectorRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CreateConnectorRequestCopyWith<$Res> {
  factory $CreateConnectorRequestCopyWith(CreateConnectorRequest value,
          $Res Function(CreateConnectorRequest) then) =
      _$CreateConnectorRequestCopyWithImpl<$Res, CreateConnectorRequest>;
  @useResult
  $Res call(
      {@JsonKey(name: 'connector_id') String connectorId,
      @JsonKey(name: 'display_name') String displayName,
      Map<String, dynamic> config,
      @JsonKey(name: 'template_id') String? templateId});
}

/// @nodoc
class _$CreateConnectorRequestCopyWithImpl<$Res,
        $Val extends CreateConnectorRequest>
    implements $CreateConnectorRequestCopyWith<$Res> {
  _$CreateConnectorRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CreateConnectorRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? connectorId = null,
    Object? displayName = null,
    Object? config = null,
    Object? templateId = freezed,
  }) {
    return _then(_value.copyWith(
      connectorId: null == connectorId
          ? _value.connectorId
          : connectorId // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: null == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String,
      config: null == config
          ? _value.config
          : config // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      templateId: freezed == templateId
          ? _value.templateId
          : templateId // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$CreateConnectorRequestImplCopyWith<$Res>
    implements $CreateConnectorRequestCopyWith<$Res> {
  factory _$$CreateConnectorRequestImplCopyWith(
          _$CreateConnectorRequestImpl value,
          $Res Function(_$CreateConnectorRequestImpl) then) =
      __$$CreateConnectorRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'connector_id') String connectorId,
      @JsonKey(name: 'display_name') String displayName,
      Map<String, dynamic> config,
      @JsonKey(name: 'template_id') String? templateId});
}

/// @nodoc
class __$$CreateConnectorRequestImplCopyWithImpl<$Res>
    extends _$CreateConnectorRequestCopyWithImpl<$Res,
        _$CreateConnectorRequestImpl>
    implements _$$CreateConnectorRequestImplCopyWith<$Res> {
  __$$CreateConnectorRequestImplCopyWithImpl(
      _$CreateConnectorRequestImpl _value,
      $Res Function(_$CreateConnectorRequestImpl) _then)
      : super(_value, _then);

  /// Create a copy of CreateConnectorRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? connectorId = null,
    Object? displayName = null,
    Object? config = null,
    Object? templateId = freezed,
  }) {
    return _then(_$CreateConnectorRequestImpl(
      connectorId: null == connectorId
          ? _value.connectorId
          : connectorId // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: null == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String,
      config: null == config
          ? _value._config
          : config // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      templateId: freezed == templateId
          ? _value.templateId
          : templateId // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CreateConnectorRequestImpl implements _CreateConnectorRequest {
  const _$CreateConnectorRequestImpl(
      {@JsonKey(name: 'connector_id') required this.connectorId,
      @JsonKey(name: 'display_name') required this.displayName,
      final Map<String, dynamic> config = const {},
      @JsonKey(name: 'template_id') this.templateId})
      : _config = config;

  factory _$CreateConnectorRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$CreateConnectorRequestImplFromJson(json);

  @override
  @JsonKey(name: 'connector_id')
  final String connectorId;
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

// 移除 auto_start 字段，因为数据库模型已经简化了逻辑
  @override
  @JsonKey(name: 'template_id')
  final String? templateId;

  @override
  String toString() {
    return 'CreateConnectorRequest(connectorId: $connectorId, displayName: $displayName, config: $config, templateId: $templateId)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CreateConnectorRequestImpl &&
            (identical(other.connectorId, connectorId) ||
                other.connectorId == connectorId) &&
            (identical(other.displayName, displayName) ||
                other.displayName == displayName) &&
            const DeepCollectionEquality().equals(other._config, _config) &&
            (identical(other.templateId, templateId) ||
                other.templateId == templateId));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, connectorId, displayName,
      const DeepCollectionEquality().hash(_config), templateId);

  /// Create a copy of CreateConnectorRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CreateConnectorRequestImplCopyWith<_$CreateConnectorRequestImpl>
      get copyWith => __$$CreateConnectorRequestImplCopyWithImpl<
          _$CreateConnectorRequestImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CreateConnectorRequestImplToJson(
      this,
    );
  }
}

abstract class _CreateConnectorRequest implements CreateConnectorRequest {
  const factory _CreateConnectorRequest(
          {@JsonKey(name: 'connector_id') required final String connectorId,
          @JsonKey(name: 'display_name') required final String displayName,
          final Map<String, dynamic> config,
          @JsonKey(name: 'template_id') final String? templateId}) =
      _$CreateConnectorRequestImpl;

  factory _CreateConnectorRequest.fromJson(Map<String, dynamic> json) =
      _$CreateConnectorRequestImpl.fromJson;

  @override
  @JsonKey(name: 'connector_id')
  String get connectorId;
  @override
  @JsonKey(name: 'display_name')
  String get displayName;
  @override
  Map<String, dynamic> get config; // 移除 auto_start 字段，因为数据库模型已经简化了逻辑
  @override
  @JsonKey(name: 'template_id')
  String? get templateId;

  /// Create a copy of CreateConnectorRequest
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CreateConnectorRequestImplCopyWith<_$CreateConnectorRequestImpl>
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
  @JsonKey(name: 'connector_id')
  String get connectorId => throw _privateConstructorUsedError;
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
      {@JsonKey(name: 'connector_id') String connectorId,
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
    Object? connectorId = null,
    Object? oldState = null,
    Object? newState = null,
  }) {
    return _then(_value.copyWith(
      connectorId: null == connectorId
          ? _value.connectorId
          : connectorId // ignore: cast_nullable_to_non_nullable
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
      {@JsonKey(name: 'connector_id') String connectorId,
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
    Object? connectorId = null,
    Object? oldState = null,
    Object? newState = null,
  }) {
    return _then(_$StateChangeEventImpl(
      connectorId: null == connectorId
          ? _value.connectorId
          : connectorId // ignore: cast_nullable_to_non_nullable
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
      {@JsonKey(name: 'connector_id') required this.connectorId,
      @JsonKey(name: 'old_state') required this.oldState,
      @JsonKey(name: 'new_state') required this.newState});

  factory _$StateChangeEventImpl.fromJson(Map<String, dynamic> json) =>
      _$$StateChangeEventImplFromJson(json);

  @override
  @JsonKey(name: 'connector_id')
  final String connectorId;
  @override
  @JsonKey(name: 'old_state')
  final ConnectorState oldState;
  @override
  @JsonKey(name: 'new_state')
  final ConnectorState newState;

  @override
  String toString() {
    return 'StateChangeEvent(connectorId: $connectorId, oldState: $oldState, newState: $newState)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$StateChangeEventImpl &&
            (identical(other.connectorId, connectorId) ||
                other.connectorId == connectorId) &&
            (identical(other.oldState, oldState) ||
                other.oldState == oldState) &&
            (identical(other.newState, newState) ||
                other.newState == newState));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, connectorId, oldState, newState);

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
          {@JsonKey(name: 'connector_id') required final String connectorId,
          @JsonKey(name: 'old_state') required final ConnectorState oldState,
          @JsonKey(name: 'new_state') required final ConnectorState newState}) =
      _$StateChangeEventImpl;

  factory _StateChangeEvent.fromJson(Map<String, dynamic> json) =
      _$StateChangeEventImpl.fromJson;

  @override
  @JsonKey(name: 'connector_id')
  String get connectorId;
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
  @JsonKey(name: 'connectors')
  List<ConnectorDefinition> get connectors =>
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
      @JsonKey(name: 'connectors') List<ConnectorDefinition> connectors});
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
    Object? connectors = null,
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
      connectors: null == connectors
          ? _value.connectors
          : connectors // ignore: cast_nullable_to_non_nullable
              as List<ConnectorDefinition>,
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
      @JsonKey(name: 'connectors') List<ConnectorDefinition> connectors});
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
    Object? connectors = null,
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
      connectors: null == connectors
          ? _value._connectors
          : connectors // ignore: cast_nullable_to_non_nullable
              as List<ConnectorDefinition>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DiscoveryResponseImpl implements _DiscoveryResponse {
  const _$DiscoveryResponseImpl(
      {required this.success,
      required this.message,
      @JsonKey(name: 'connectors')
      final List<ConnectorDefinition> connectors = const []})
      : _connectors = connectors;

  factory _$DiscoveryResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$DiscoveryResponseImplFromJson(json);

  @override
  final bool success;
  @override
  final String message;
  final List<ConnectorDefinition> _connectors;
  @override
  @JsonKey(name: 'connectors')
  List<ConnectorDefinition> get connectors {
    if (_connectors is EqualUnmodifiableListView) return _connectors;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_connectors);
  }

  @override
  String toString() {
    return 'DiscoveryResponse(success: $success, message: $message, connectors: $connectors)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DiscoveryResponseImpl &&
            (identical(other.success, success) || other.success == success) &&
            (identical(other.message, message) || other.message == message) &&
            const DeepCollectionEquality()
                .equals(other._connectors, _connectors));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, success, message,
      const DeepCollectionEquality().hash(_connectors));

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
      @JsonKey(name: 'connectors')
      final List<ConnectorDefinition> connectors}) = _$DiscoveryResponseImpl;

  factory _DiscoveryResponse.fromJson(Map<String, dynamic> json) =
      _$DiscoveryResponseImpl.fromJson;

  @override
  bool get success;
  @override
  String get message;
  @override
  @JsonKey(name: 'connectors')
  List<ConnectorDefinition> get connectors;

  /// Create a copy of DiscoveryResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DiscoveryResponseImplCopyWith<_$DiscoveryResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ConnectorListResponse _$ConnectorListResponseFromJson(
    Map<String, dynamic> json) {
  return _ConnectorListResponse.fromJson(json);
}

/// @nodoc
mixin _$ConnectorListResponse {
  bool get success => throw _privateConstructorUsedError;
  List<ConnectorInfo> get connectors => throw _privateConstructorUsedError;
  @JsonKey(name: 'total_count')
  int get totalCount => throw _privateConstructorUsedError;

  /// Serializes this ConnectorListResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ConnectorListResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ConnectorListResponseCopyWith<ConnectorListResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ConnectorListResponseCopyWith<$Res> {
  factory $ConnectorListResponseCopyWith(ConnectorListResponse value,
          $Res Function(ConnectorListResponse) then) =
      _$ConnectorListResponseCopyWithImpl<$Res, ConnectorListResponse>;
  @useResult
  $Res call(
      {bool success,
      List<ConnectorInfo> connectors,
      @JsonKey(name: 'total_count') int totalCount});
}

/// @nodoc
class _$ConnectorListResponseCopyWithImpl<$Res,
        $Val extends ConnectorListResponse>
    implements $ConnectorListResponseCopyWith<$Res> {
  _$ConnectorListResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ConnectorListResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? connectors = null,
    Object? totalCount = null,
  }) {
    return _then(_value.copyWith(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      connectors: null == connectors
          ? _value.connectors
          : connectors // ignore: cast_nullable_to_non_nullable
              as List<ConnectorInfo>,
      totalCount: null == totalCount
          ? _value.totalCount
          : totalCount // ignore: cast_nullable_to_non_nullable
              as int,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ConnectorListResponseImplCopyWith<$Res>
    implements $ConnectorListResponseCopyWith<$Res> {
  factory _$$ConnectorListResponseImplCopyWith(
          _$ConnectorListResponseImpl value,
          $Res Function(_$ConnectorListResponseImpl) then) =
      __$$ConnectorListResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {bool success,
      List<ConnectorInfo> connectors,
      @JsonKey(name: 'total_count') int totalCount});
}

/// @nodoc
class __$$ConnectorListResponseImplCopyWithImpl<$Res>
    extends _$ConnectorListResponseCopyWithImpl<$Res,
        _$ConnectorListResponseImpl>
    implements _$$ConnectorListResponseImplCopyWith<$Res> {
  __$$ConnectorListResponseImplCopyWithImpl(_$ConnectorListResponseImpl _value,
      $Res Function(_$ConnectorListResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of ConnectorListResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? connectors = null,
    Object? totalCount = null,
  }) {
    return _then(_$ConnectorListResponseImpl(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      connectors: null == connectors
          ? _value._connectors
          : connectors // ignore: cast_nullable_to_non_nullable
              as List<ConnectorInfo>,
      totalCount: null == totalCount
          ? _value.totalCount
          : totalCount // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ConnectorListResponseImpl implements _ConnectorListResponse {
  const _$ConnectorListResponseImpl(
      {required this.success,
      final List<ConnectorInfo> connectors = const [],
      @JsonKey(name: 'total_count') this.totalCount = 0})
      : _connectors = connectors;

  factory _$ConnectorListResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$ConnectorListResponseImplFromJson(json);

  @override
  final bool success;
  final List<ConnectorInfo> _connectors;
  @override
  @JsonKey()
  List<ConnectorInfo> get connectors {
    if (_connectors is EqualUnmodifiableListView) return _connectors;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_connectors);
  }

  @override
  @JsonKey(name: 'total_count')
  final int totalCount;

  @override
  String toString() {
    return 'ConnectorListResponse(success: $success, connectors: $connectors, totalCount: $totalCount)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ConnectorListResponseImpl &&
            (identical(other.success, success) || other.success == success) &&
            const DeepCollectionEquality()
                .equals(other._connectors, _connectors) &&
            (identical(other.totalCount, totalCount) ||
                other.totalCount == totalCount));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, success,
      const DeepCollectionEquality().hash(_connectors), totalCount);

  /// Create a copy of ConnectorListResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ConnectorListResponseImplCopyWith<_$ConnectorListResponseImpl>
      get copyWith => __$$ConnectorListResponseImplCopyWithImpl<
          _$ConnectorListResponseImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ConnectorListResponseImplToJson(
      this,
    );
  }
}

abstract class _ConnectorListResponse implements ConnectorListResponse {
  const factory _ConnectorListResponse(
          {required final bool success,
          final List<ConnectorInfo> connectors,
          @JsonKey(name: 'total_count') final int totalCount}) =
      _$ConnectorListResponseImpl;

  factory _ConnectorListResponse.fromJson(Map<String, dynamic> json) =
      _$ConnectorListResponseImpl.fromJson;

  @override
  bool get success;
  @override
  List<ConnectorInfo> get connectors;
  @override
  @JsonKey(name: 'total_count')
  int get totalCount;

  /// Create a copy of ConnectorListResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ConnectorListResponseImplCopyWith<_$ConnectorListResponseImpl>
      get copyWith => throw _privateConstructorUsedError;
}

ConnectorDetailResponse _$ConnectorDetailResponseFromJson(
    Map<String, dynamic> json) {
  return _ConnectorDetailResponse.fromJson(json);
}

/// @nodoc
mixin _$ConnectorDetailResponse {
  bool get success => throw _privateConstructorUsedError;
  ConnectorInfo get connector => throw _privateConstructorUsedError;

  /// Serializes this ConnectorDetailResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ConnectorDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ConnectorDetailResponseCopyWith<ConnectorDetailResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ConnectorDetailResponseCopyWith<$Res> {
  factory $ConnectorDetailResponseCopyWith(ConnectorDetailResponse value,
          $Res Function(ConnectorDetailResponse) then) =
      _$ConnectorDetailResponseCopyWithImpl<$Res, ConnectorDetailResponse>;
  @useResult
  $Res call({bool success, ConnectorInfo connector});

  $ConnectorInfoCopyWith<$Res> get connector;
}

/// @nodoc
class _$ConnectorDetailResponseCopyWithImpl<$Res,
        $Val extends ConnectorDetailResponse>
    implements $ConnectorDetailResponseCopyWith<$Res> {
  _$ConnectorDetailResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ConnectorDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? connector = null,
  }) {
    return _then(_value.copyWith(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      connector: null == connector
          ? _value.connector
          : connector // ignore: cast_nullable_to_non_nullable
              as ConnectorInfo,
    ) as $Val);
  }

  /// Create a copy of ConnectorDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $ConnectorInfoCopyWith<$Res> get connector {
    return $ConnectorInfoCopyWith<$Res>(_value.connector, (value) {
      return _then(_value.copyWith(connector: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$ConnectorDetailResponseImplCopyWith<$Res>
    implements $ConnectorDetailResponseCopyWith<$Res> {
  factory _$$ConnectorDetailResponseImplCopyWith(
          _$ConnectorDetailResponseImpl value,
          $Res Function(_$ConnectorDetailResponseImpl) then) =
      __$$ConnectorDetailResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({bool success, ConnectorInfo connector});

  @override
  $ConnectorInfoCopyWith<$Res> get connector;
}

/// @nodoc
class __$$ConnectorDetailResponseImplCopyWithImpl<$Res>
    extends _$ConnectorDetailResponseCopyWithImpl<$Res,
        _$ConnectorDetailResponseImpl>
    implements _$$ConnectorDetailResponseImplCopyWith<$Res> {
  __$$ConnectorDetailResponseImplCopyWithImpl(
      _$ConnectorDetailResponseImpl _value,
      $Res Function(_$ConnectorDetailResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of ConnectorDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? connector = null,
  }) {
    return _then(_$ConnectorDetailResponseImpl(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      connector: null == connector
          ? _value.connector
          : connector // ignore: cast_nullable_to_non_nullable
              as ConnectorInfo,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ConnectorDetailResponseImpl implements _ConnectorDetailResponse {
  const _$ConnectorDetailResponseImpl(
      {required this.success, required this.connector});

  factory _$ConnectorDetailResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$ConnectorDetailResponseImplFromJson(json);

  @override
  final bool success;
  @override
  final ConnectorInfo connector;

  @override
  String toString() {
    return 'ConnectorDetailResponse(success: $success, connector: $connector)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ConnectorDetailResponseImpl &&
            (identical(other.success, success) || other.success == success) &&
            (identical(other.connector, connector) ||
                other.connector == connector));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, success, connector);

  /// Create a copy of ConnectorDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ConnectorDetailResponseImplCopyWith<_$ConnectorDetailResponseImpl>
      get copyWith => __$$ConnectorDetailResponseImplCopyWithImpl<
          _$ConnectorDetailResponseImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ConnectorDetailResponseImplToJson(
      this,
    );
  }
}

abstract class _ConnectorDetailResponse implements ConnectorDetailResponse {
  const factory _ConnectorDetailResponse(
      {required final bool success,
      required final ConnectorInfo connector}) = _$ConnectorDetailResponseImpl;

  factory _ConnectorDetailResponse.fromJson(Map<String, dynamic> json) =
      _$ConnectorDetailResponseImpl.fromJson;

  @override
  bool get success;
  @override
  ConnectorInfo get connector;

  /// Create a copy of ConnectorDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ConnectorDetailResponseImplCopyWith<_$ConnectorDetailResponseImpl>
      get copyWith => throw _privateConstructorUsedError;
}

OperationResponse _$OperationResponseFromJson(Map<String, dynamic> json) {
  return _OperationResponse.fromJson(json);
}

/// @nodoc
mixin _$OperationResponse {
  bool get success => throw _privateConstructorUsedError;
  String get message => throw _privateConstructorUsedError;
  @JsonKey(name: 'connector_id')
  String get connectorId => throw _privateConstructorUsedError;
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
      @JsonKey(name: 'connector_id') String connectorId,
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
    Object? connectorId = null,
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
      connectorId: null == connectorId
          ? _value.connectorId
          : connectorId // ignore: cast_nullable_to_non_nullable
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
      @JsonKey(name: 'connector_id') String connectorId,
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
    Object? connectorId = null,
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
      connectorId: null == connectorId
          ? _value.connectorId
          : connectorId // ignore: cast_nullable_to_non_nullable
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
      @JsonKey(name: 'connector_id') required this.connectorId,
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
  @JsonKey(name: 'connector_id')
  final String connectorId;
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
    return 'OperationResponse(success: $success, message: $message, connectorId: $connectorId, state: $state, hotReloadApplied: $hotReloadApplied, requiresRestart: $requiresRestart, wasRunning: $wasRunning)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$OperationResponseImpl &&
            (identical(other.success, success) || other.success == success) &&
            (identical(other.message, message) || other.message == message) &&
            (identical(other.connectorId, connectorId) ||
                other.connectorId == connectorId) &&
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
  int get hashCode => Object.hash(runtimeType, success, message, connectorId,
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
          @JsonKey(name: 'connector_id') required final String connectorId,
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
  @JsonKey(name: 'connector_id')
  String get connectorId;
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

DiscoveredConnectorInfo _$DiscoveredConnectorInfoFromJson(
    Map<String, dynamic> json) {
  return _DiscoveredConnectorInfo.fromJson(json);
}

/// @nodoc
mixin _$DiscoveredConnectorInfo {
  String get path => throw _privateConstructorUsedError;
  @JsonKey(name: 'connector_id')
  String get connectorId => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get description => throw _privateConstructorUsedError;
  String get version => throw _privateConstructorUsedError;
  @JsonKey(name: 'entry_point')
  String get entryPoint => throw _privateConstructorUsedError;
  @JsonKey(name: 'is_registered')
  bool get isRegistered => throw _privateConstructorUsedError;

  /// Serializes this DiscoveredConnectorInfo to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of DiscoveredConnectorInfo
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DiscoveredConnectorInfoCopyWith<DiscoveredConnectorInfo> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DiscoveredConnectorInfoCopyWith<$Res> {
  factory $DiscoveredConnectorInfoCopyWith(DiscoveredConnectorInfo value,
          $Res Function(DiscoveredConnectorInfo) then) =
      _$DiscoveredConnectorInfoCopyWithImpl<$Res, DiscoveredConnectorInfo>;
  @useResult
  $Res call(
      {String path,
      @JsonKey(name: 'connector_id') String connectorId,
      String name,
      String description,
      String version,
      @JsonKey(name: 'entry_point') String entryPoint,
      @JsonKey(name: 'is_registered') bool isRegistered});
}

/// @nodoc
class _$DiscoveredConnectorInfoCopyWithImpl<$Res,
        $Val extends DiscoveredConnectorInfo>
    implements $DiscoveredConnectorInfoCopyWith<$Res> {
  _$DiscoveredConnectorInfoCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DiscoveredConnectorInfo
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? path = null,
    Object? connectorId = null,
    Object? name = null,
    Object? description = null,
    Object? version = null,
    Object? entryPoint = null,
    Object? isRegistered = null,
  }) {
    return _then(_value.copyWith(
      path: null == path
          ? _value.path
          : path // ignore: cast_nullable_to_non_nullable
              as String,
      connectorId: null == connectorId
          ? _value.connectorId
          : connectorId // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      version: null == version
          ? _value.version
          : version // ignore: cast_nullable_to_non_nullable
              as String,
      entryPoint: null == entryPoint
          ? _value.entryPoint
          : entryPoint // ignore: cast_nullable_to_non_nullable
              as String,
      isRegistered: null == isRegistered
          ? _value.isRegistered
          : isRegistered // ignore: cast_nullable_to_non_nullable
              as bool,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DiscoveredConnectorInfoImplCopyWith<$Res>
    implements $DiscoveredConnectorInfoCopyWith<$Res> {
  factory _$$DiscoveredConnectorInfoImplCopyWith(
          _$DiscoveredConnectorInfoImpl value,
          $Res Function(_$DiscoveredConnectorInfoImpl) then) =
      __$$DiscoveredConnectorInfoImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String path,
      @JsonKey(name: 'connector_id') String connectorId,
      String name,
      String description,
      String version,
      @JsonKey(name: 'entry_point') String entryPoint,
      @JsonKey(name: 'is_registered') bool isRegistered});
}

/// @nodoc
class __$$DiscoveredConnectorInfoImplCopyWithImpl<$Res>
    extends _$DiscoveredConnectorInfoCopyWithImpl<$Res,
        _$DiscoveredConnectorInfoImpl>
    implements _$$DiscoveredConnectorInfoImplCopyWith<$Res> {
  __$$DiscoveredConnectorInfoImplCopyWithImpl(
      _$DiscoveredConnectorInfoImpl _value,
      $Res Function(_$DiscoveredConnectorInfoImpl) _then)
      : super(_value, _then);

  /// Create a copy of DiscoveredConnectorInfo
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? path = null,
    Object? connectorId = null,
    Object? name = null,
    Object? description = null,
    Object? version = null,
    Object? entryPoint = null,
    Object? isRegistered = null,
  }) {
    return _then(_$DiscoveredConnectorInfoImpl(
      path: null == path
          ? _value.path
          : path // ignore: cast_nullable_to_non_nullable
              as String,
      connectorId: null == connectorId
          ? _value.connectorId
          : connectorId // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      version: null == version
          ? _value.version
          : version // ignore: cast_nullable_to_non_nullable
              as String,
      entryPoint: null == entryPoint
          ? _value.entryPoint
          : entryPoint // ignore: cast_nullable_to_non_nullable
              as String,
      isRegistered: null == isRegistered
          ? _value.isRegistered
          : isRegistered // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DiscoveredConnectorInfoImpl implements _DiscoveredConnectorInfo {
  const _$DiscoveredConnectorInfoImpl(
      {required this.path,
      @JsonKey(name: 'connector_id') required this.connectorId,
      required this.name,
      required this.description,
      required this.version,
      @JsonKey(name: 'entry_point') required this.entryPoint,
      @JsonKey(name: 'is_registered') required this.isRegistered});

  factory _$DiscoveredConnectorInfoImpl.fromJson(Map<String, dynamic> json) =>
      _$$DiscoveredConnectorInfoImplFromJson(json);

  @override
  final String path;
  @override
  @JsonKey(name: 'connector_id')
  final String connectorId;
  @override
  final String name;
  @override
  final String description;
  @override
  final String version;
  @override
  @JsonKey(name: 'entry_point')
  final String entryPoint;
  @override
  @JsonKey(name: 'is_registered')
  final bool isRegistered;

  @override
  String toString() {
    return 'DiscoveredConnectorInfo(path: $path, connectorId: $connectorId, name: $name, description: $description, version: $version, entryPoint: $entryPoint, isRegistered: $isRegistered)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DiscoveredConnectorInfoImpl &&
            (identical(other.path, path) || other.path == path) &&
            (identical(other.connectorId, connectorId) ||
                other.connectorId == connectorId) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.version, version) || other.version == version) &&
            (identical(other.entryPoint, entryPoint) ||
                other.entryPoint == entryPoint) &&
            (identical(other.isRegistered, isRegistered) ||
                other.isRegistered == isRegistered));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, path, connectorId, name,
      description, version, entryPoint, isRegistered);

  /// Create a copy of DiscoveredConnectorInfo
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DiscoveredConnectorInfoImplCopyWith<_$DiscoveredConnectorInfoImpl>
      get copyWith => __$$DiscoveredConnectorInfoImplCopyWithImpl<
          _$DiscoveredConnectorInfoImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DiscoveredConnectorInfoImplToJson(
      this,
    );
  }
}

abstract class _DiscoveredConnectorInfo implements DiscoveredConnectorInfo {
  const factory _DiscoveredConnectorInfo(
          {required final String path,
          @JsonKey(name: 'connector_id') required final String connectorId,
          required final String name,
          required final String description,
          required final String version,
          @JsonKey(name: 'entry_point') required final String entryPoint,
          @JsonKey(name: 'is_registered') required final bool isRegistered}) =
      _$DiscoveredConnectorInfoImpl;

  factory _DiscoveredConnectorInfo.fromJson(Map<String, dynamic> json) =
      _$DiscoveredConnectorInfoImpl.fromJson;

  @override
  String get path;
  @override
  @JsonKey(name: 'connector_id')
  String get connectorId;
  @override
  String get name;
  @override
  String get description;
  @override
  String get version;
  @override
  @JsonKey(name: 'entry_point')
  String get entryPoint;
  @override
  @JsonKey(name: 'is_registered')
  bool get isRegistered;

  /// Create a copy of DiscoveredConnectorInfo
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DiscoveredConnectorInfoImplCopyWith<_$DiscoveredConnectorInfoImpl>
      get copyWith => throw _privateConstructorUsedError;
}

DirectoryScanResponse _$DirectoryScanResponseFromJson(
    Map<String, dynamic> json) {
  return _DirectoryScanResponse.fromJson(json);
}

/// @nodoc
mixin _$DirectoryScanResponse {
  bool get success => throw _privateConstructorUsedError;
  Map<String, dynamic> get data => throw _privateConstructorUsedError;
  String get message => throw _privateConstructorUsedError;

  /// Serializes this DirectoryScanResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of DirectoryScanResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DirectoryScanResponseCopyWith<DirectoryScanResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DirectoryScanResponseCopyWith<$Res> {
  factory $DirectoryScanResponseCopyWith(DirectoryScanResponse value,
          $Res Function(DirectoryScanResponse) then) =
      _$DirectoryScanResponseCopyWithImpl<$Res, DirectoryScanResponse>;
  @useResult
  $Res call({bool success, Map<String, dynamic> data, String message});
}

/// @nodoc
class _$DirectoryScanResponseCopyWithImpl<$Res,
        $Val extends DirectoryScanResponse>
    implements $DirectoryScanResponseCopyWith<$Res> {
  _$DirectoryScanResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DirectoryScanResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? data = null,
    Object? message = null,
  }) {
    return _then(_value.copyWith(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      data: null == data
          ? _value.data
          : data // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DirectoryScanResponseImplCopyWith<$Res>
    implements $DirectoryScanResponseCopyWith<$Res> {
  factory _$$DirectoryScanResponseImplCopyWith(
          _$DirectoryScanResponseImpl value,
          $Res Function(_$DirectoryScanResponseImpl) then) =
      __$$DirectoryScanResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({bool success, Map<String, dynamic> data, String message});
}

/// @nodoc
class __$$DirectoryScanResponseImplCopyWithImpl<$Res>
    extends _$DirectoryScanResponseCopyWithImpl<$Res,
        _$DirectoryScanResponseImpl>
    implements _$$DirectoryScanResponseImplCopyWith<$Res> {
  __$$DirectoryScanResponseImplCopyWithImpl(_$DirectoryScanResponseImpl _value,
      $Res Function(_$DirectoryScanResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of DirectoryScanResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? data = null,
    Object? message = null,
  }) {
    return _then(_$DirectoryScanResponseImpl(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      data: null == data
          ? _value._data
          : data // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DirectoryScanResponseImpl implements _DirectoryScanResponse {
  const _$DirectoryScanResponseImpl(
      {required this.success,
      required final Map<String, dynamic> data,
      required this.message})
      : _data = data;

  factory _$DirectoryScanResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$DirectoryScanResponseImplFromJson(json);

  @override
  final bool success;
  final Map<String, dynamic> _data;
  @override
  Map<String, dynamic> get data {
    if (_data is EqualUnmodifiableMapView) return _data;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_data);
  }

  @override
  final String message;

  @override
  String toString() {
    return 'DirectoryScanResponse(success: $success, data: $data, message: $message)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DirectoryScanResponseImpl &&
            (identical(other.success, success) || other.success == success) &&
            const DeepCollectionEquality().equals(other._data, _data) &&
            (identical(other.message, message) || other.message == message));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, success,
      const DeepCollectionEquality().hash(_data), message);

  /// Create a copy of DirectoryScanResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DirectoryScanResponseImplCopyWith<_$DirectoryScanResponseImpl>
      get copyWith => __$$DirectoryScanResponseImplCopyWithImpl<
          _$DirectoryScanResponseImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DirectoryScanResponseImplToJson(
      this,
    );
  }
}

abstract class _DirectoryScanResponse implements DirectoryScanResponse {
  const factory _DirectoryScanResponse(
      {required final bool success,
      required final Map<String, dynamic> data,
      required final String message}) = _$DirectoryScanResponseImpl;

  factory _DirectoryScanResponse.fromJson(Map<String, dynamic> json) =
      _$DirectoryScanResponseImpl.fromJson;

  @override
  bool get success;
  @override
  Map<String, dynamic> get data;
  @override
  String get message;

  /// Create a copy of DirectoryScanResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DirectoryScanResponseImplCopyWith<_$DirectoryScanResponseImpl>
      get copyWith => throw _privateConstructorUsedError;
}

ConnectorRegistrationResponse _$ConnectorRegistrationResponseFromJson(
    Map<String, dynamic> json) {
  return _ConnectorRegistrationResponse.fromJson(json);
}

/// @nodoc
mixin _$ConnectorRegistrationResponse {
  bool get success => throw _privateConstructorUsedError;
  Map<String, dynamic> get data => throw _privateConstructorUsedError;
  String get message => throw _privateConstructorUsedError;

  /// Serializes this ConnectorRegistrationResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ConnectorRegistrationResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ConnectorRegistrationResponseCopyWith<ConnectorRegistrationResponse>
      get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ConnectorRegistrationResponseCopyWith<$Res> {
  factory $ConnectorRegistrationResponseCopyWith(
          ConnectorRegistrationResponse value,
          $Res Function(ConnectorRegistrationResponse) then) =
      _$ConnectorRegistrationResponseCopyWithImpl<$Res,
          ConnectorRegistrationResponse>;
  @useResult
  $Res call({bool success, Map<String, dynamic> data, String message});
}

/// @nodoc
class _$ConnectorRegistrationResponseCopyWithImpl<$Res,
        $Val extends ConnectorRegistrationResponse>
    implements $ConnectorRegistrationResponseCopyWith<$Res> {
  _$ConnectorRegistrationResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ConnectorRegistrationResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? data = null,
    Object? message = null,
  }) {
    return _then(_value.copyWith(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      data: null == data
          ? _value.data
          : data // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ConnectorRegistrationResponseImplCopyWith<$Res>
    implements $ConnectorRegistrationResponseCopyWith<$Res> {
  factory _$$ConnectorRegistrationResponseImplCopyWith(
          _$ConnectorRegistrationResponseImpl value,
          $Res Function(_$ConnectorRegistrationResponseImpl) then) =
      __$$ConnectorRegistrationResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({bool success, Map<String, dynamic> data, String message});
}

/// @nodoc
class __$$ConnectorRegistrationResponseImplCopyWithImpl<$Res>
    extends _$ConnectorRegistrationResponseCopyWithImpl<$Res,
        _$ConnectorRegistrationResponseImpl>
    implements _$$ConnectorRegistrationResponseImplCopyWith<$Res> {
  __$$ConnectorRegistrationResponseImplCopyWithImpl(
      _$ConnectorRegistrationResponseImpl _value,
      $Res Function(_$ConnectorRegistrationResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of ConnectorRegistrationResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? data = null,
    Object? message = null,
  }) {
    return _then(_$ConnectorRegistrationResponseImpl(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      data: null == data
          ? _value._data
          : data // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ConnectorRegistrationResponseImpl
    implements _ConnectorRegistrationResponse {
  const _$ConnectorRegistrationResponseImpl(
      {required this.success,
      required final Map<String, dynamic> data,
      required this.message})
      : _data = data;

  factory _$ConnectorRegistrationResponseImpl.fromJson(
          Map<String, dynamic> json) =>
      _$$ConnectorRegistrationResponseImplFromJson(json);

  @override
  final bool success;
  final Map<String, dynamic> _data;
  @override
  Map<String, dynamic> get data {
    if (_data is EqualUnmodifiableMapView) return _data;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_data);
  }

  @override
  final String message;

  @override
  String toString() {
    return 'ConnectorRegistrationResponse(success: $success, data: $data, message: $message)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ConnectorRegistrationResponseImpl &&
            (identical(other.success, success) || other.success == success) &&
            const DeepCollectionEquality().equals(other._data, _data) &&
            (identical(other.message, message) || other.message == message));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, success,
      const DeepCollectionEquality().hash(_data), message);

  /// Create a copy of ConnectorRegistrationResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ConnectorRegistrationResponseImplCopyWith<
          _$ConnectorRegistrationResponseImpl>
      get copyWith => __$$ConnectorRegistrationResponseImplCopyWithImpl<
          _$ConnectorRegistrationResponseImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ConnectorRegistrationResponseImplToJson(
      this,
    );
  }
}

abstract class _ConnectorRegistrationResponse
    implements ConnectorRegistrationResponse {
  const factory _ConnectorRegistrationResponse(
      {required final bool success,
      required final Map<String, dynamic> data,
      required final String message}) = _$ConnectorRegistrationResponseImpl;

  factory _ConnectorRegistrationResponse.fromJson(Map<String, dynamic> json) =
      _$ConnectorRegistrationResponseImpl.fromJson;

  @override
  bool get success;
  @override
  Map<String, dynamic> get data;
  @override
  String get message;

  /// Create a copy of ConnectorRegistrationResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ConnectorRegistrationResponseImplCopyWith<
          _$ConnectorRegistrationResponseImpl>
      get copyWith => throw _privateConstructorUsedError;
}
