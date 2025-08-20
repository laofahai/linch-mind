// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'universe_provider.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

/// @nodoc
mixin _$UniverseState {
// 数据加载状态
  bool get isLoading => throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError; // 原始数据
  List<ConnectorInfo> get connectors => throw _privateConstructorUsedError;
  Map<String, dynamic> get relationshipData =>
      throw _privateConstructorUsedError; // 转换后的3D对象
  List<CelestialObject> get celestialObjects =>
      throw _privateConstructorUsedError;
  List<StarConnection> get connections =>
      throw _privateConstructorUsedError; // 统计信息
  int get totalConnectors => throw _privateConstructorUsedError;
  int get runningConnectors => throw _privateConstructorUsedError;
  int get errorConnectors => throw _privateConstructorUsedError;
  int get totalConnections => throw _privateConstructorUsedError; // 最后更新时间
  DateTime? get lastUpdated => throw _privateConstructorUsedError; // 选中状态
  String? get selectedConnectorId => throw _privateConstructorUsedError;
  Map<String, dynamic>? get selectedConnectorInfo =>
      throw _privateConstructorUsedError;

  /// Create a copy of UniverseState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $UniverseStateCopyWith<UniverseState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $UniverseStateCopyWith<$Res> {
  factory $UniverseStateCopyWith(
          UniverseState value, $Res Function(UniverseState) then) =
      _$UniverseStateCopyWithImpl<$Res, UniverseState>;
  @useResult
  $Res call(
      {bool isLoading,
      String? error,
      List<ConnectorInfo> connectors,
      Map<String, dynamic> relationshipData,
      List<CelestialObject> celestialObjects,
      List<StarConnection> connections,
      int totalConnectors,
      int runningConnectors,
      int errorConnectors,
      int totalConnections,
      DateTime? lastUpdated,
      String? selectedConnectorId,
      Map<String, dynamic>? selectedConnectorInfo});
}

/// @nodoc
class _$UniverseStateCopyWithImpl<$Res, $Val extends UniverseState>
    implements $UniverseStateCopyWith<$Res> {
  _$UniverseStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of UniverseState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? isLoading = null,
    Object? error = freezed,
    Object? connectors = null,
    Object? relationshipData = null,
    Object? celestialObjects = null,
    Object? connections = null,
    Object? totalConnectors = null,
    Object? runningConnectors = null,
    Object? errorConnectors = null,
    Object? totalConnections = null,
    Object? lastUpdated = freezed,
    Object? selectedConnectorId = freezed,
    Object? selectedConnectorInfo = freezed,
  }) {
    return _then(_value.copyWith(
      isLoading: null == isLoading
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
      connectors: null == connectors
          ? _value.connectors
          : connectors // ignore: cast_nullable_to_non_nullable
              as List<ConnectorInfo>,
      relationshipData: null == relationshipData
          ? _value.relationshipData
          : relationshipData // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      celestialObjects: null == celestialObjects
          ? _value.celestialObjects
          : celestialObjects // ignore: cast_nullable_to_non_nullable
              as List<CelestialObject>,
      connections: null == connections
          ? _value.connections
          : connections // ignore: cast_nullable_to_non_nullable
              as List<StarConnection>,
      totalConnectors: null == totalConnectors
          ? _value.totalConnectors
          : totalConnectors // ignore: cast_nullable_to_non_nullable
              as int,
      runningConnectors: null == runningConnectors
          ? _value.runningConnectors
          : runningConnectors // ignore: cast_nullable_to_non_nullable
              as int,
      errorConnectors: null == errorConnectors
          ? _value.errorConnectors
          : errorConnectors // ignore: cast_nullable_to_non_nullable
              as int,
      totalConnections: null == totalConnections
          ? _value.totalConnections
          : totalConnections // ignore: cast_nullable_to_non_nullable
              as int,
      lastUpdated: freezed == lastUpdated
          ? _value.lastUpdated
          : lastUpdated // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      selectedConnectorId: freezed == selectedConnectorId
          ? _value.selectedConnectorId
          : selectedConnectorId // ignore: cast_nullable_to_non_nullable
              as String?,
      selectedConnectorInfo: freezed == selectedConnectorInfo
          ? _value.selectedConnectorInfo
          : selectedConnectorInfo // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$UniverseStateImplCopyWith<$Res>
    implements $UniverseStateCopyWith<$Res> {
  factory _$$UniverseStateImplCopyWith(
          _$UniverseStateImpl value, $Res Function(_$UniverseStateImpl) then) =
      __$$UniverseStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {bool isLoading,
      String? error,
      List<ConnectorInfo> connectors,
      Map<String, dynamic> relationshipData,
      List<CelestialObject> celestialObjects,
      List<StarConnection> connections,
      int totalConnectors,
      int runningConnectors,
      int errorConnectors,
      int totalConnections,
      DateTime? lastUpdated,
      String? selectedConnectorId,
      Map<String, dynamic>? selectedConnectorInfo});
}

/// @nodoc
class __$$UniverseStateImplCopyWithImpl<$Res>
    extends _$UniverseStateCopyWithImpl<$Res, _$UniverseStateImpl>
    implements _$$UniverseStateImplCopyWith<$Res> {
  __$$UniverseStateImplCopyWithImpl(
      _$UniverseStateImpl _value, $Res Function(_$UniverseStateImpl) _then)
      : super(_value, _then);

  /// Create a copy of UniverseState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? isLoading = null,
    Object? error = freezed,
    Object? connectors = null,
    Object? relationshipData = null,
    Object? celestialObjects = null,
    Object? connections = null,
    Object? totalConnectors = null,
    Object? runningConnectors = null,
    Object? errorConnectors = null,
    Object? totalConnections = null,
    Object? lastUpdated = freezed,
    Object? selectedConnectorId = freezed,
    Object? selectedConnectorInfo = freezed,
  }) {
    return _then(_$UniverseStateImpl(
      isLoading: null == isLoading
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
      connectors: null == connectors
          ? _value._connectors
          : connectors // ignore: cast_nullable_to_non_nullable
              as List<ConnectorInfo>,
      relationshipData: null == relationshipData
          ? _value._relationshipData
          : relationshipData // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      celestialObjects: null == celestialObjects
          ? _value._celestialObjects
          : celestialObjects // ignore: cast_nullable_to_non_nullable
              as List<CelestialObject>,
      connections: null == connections
          ? _value._connections
          : connections // ignore: cast_nullable_to_non_nullable
              as List<StarConnection>,
      totalConnectors: null == totalConnectors
          ? _value.totalConnectors
          : totalConnectors // ignore: cast_nullable_to_non_nullable
              as int,
      runningConnectors: null == runningConnectors
          ? _value.runningConnectors
          : runningConnectors // ignore: cast_nullable_to_non_nullable
              as int,
      errorConnectors: null == errorConnectors
          ? _value.errorConnectors
          : errorConnectors // ignore: cast_nullable_to_non_nullable
              as int,
      totalConnections: null == totalConnections
          ? _value.totalConnections
          : totalConnections // ignore: cast_nullable_to_non_nullable
              as int,
      lastUpdated: freezed == lastUpdated
          ? _value.lastUpdated
          : lastUpdated // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      selectedConnectorId: freezed == selectedConnectorId
          ? _value.selectedConnectorId
          : selectedConnectorId // ignore: cast_nullable_to_non_nullable
              as String?,
      selectedConnectorInfo: freezed == selectedConnectorInfo
          ? _value._selectedConnectorInfo
          : selectedConnectorInfo // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc

class _$UniverseStateImpl implements _UniverseState {
  const _$UniverseStateImpl(
      {this.isLoading = false,
      this.error,
      final List<ConnectorInfo> connectors = const [],
      final Map<String, dynamic> relationshipData = const {},
      final List<CelestialObject> celestialObjects = const [],
      final List<StarConnection> connections = const [],
      this.totalConnectors = 0,
      this.runningConnectors = 0,
      this.errorConnectors = 0,
      this.totalConnections = 0,
      this.lastUpdated,
      this.selectedConnectorId,
      final Map<String, dynamic>? selectedConnectorInfo})
      : _connectors = connectors,
        _relationshipData = relationshipData,
        _celestialObjects = celestialObjects,
        _connections = connections,
        _selectedConnectorInfo = selectedConnectorInfo;

// 数据加载状态
  @override
  @JsonKey()
  final bool isLoading;
  @override
  final String? error;
// 原始数据
  final List<ConnectorInfo> _connectors;
// 原始数据
  @override
  @JsonKey()
  List<ConnectorInfo> get connectors {
    if (_connectors is EqualUnmodifiableListView) return _connectors;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_connectors);
  }

  final Map<String, dynamic> _relationshipData;
  @override
  @JsonKey()
  Map<String, dynamic> get relationshipData {
    if (_relationshipData is EqualUnmodifiableMapView) return _relationshipData;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_relationshipData);
  }

// 转换后的3D对象
  final List<CelestialObject> _celestialObjects;
// 转换后的3D对象
  @override
  @JsonKey()
  List<CelestialObject> get celestialObjects {
    if (_celestialObjects is EqualUnmodifiableListView)
      return _celestialObjects;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_celestialObjects);
  }

  final List<StarConnection> _connections;
  @override
  @JsonKey()
  List<StarConnection> get connections {
    if (_connections is EqualUnmodifiableListView) return _connections;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_connections);
  }

// 统计信息
  @override
  @JsonKey()
  final int totalConnectors;
  @override
  @JsonKey()
  final int runningConnectors;
  @override
  @JsonKey()
  final int errorConnectors;
  @override
  @JsonKey()
  final int totalConnections;
// 最后更新时间
  @override
  final DateTime? lastUpdated;
// 选中状态
  @override
  final String? selectedConnectorId;
  final Map<String, dynamic>? _selectedConnectorInfo;
  @override
  Map<String, dynamic>? get selectedConnectorInfo {
    final value = _selectedConnectorInfo;
    if (value == null) return null;
    if (_selectedConnectorInfo is EqualUnmodifiableMapView)
      return _selectedConnectorInfo;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'UniverseState(isLoading: $isLoading, error: $error, connectors: $connectors, relationshipData: $relationshipData, celestialObjects: $celestialObjects, connections: $connections, totalConnectors: $totalConnectors, runningConnectors: $runningConnectors, errorConnectors: $errorConnectors, totalConnections: $totalConnections, lastUpdated: $lastUpdated, selectedConnectorId: $selectedConnectorId, selectedConnectorInfo: $selectedConnectorInfo)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$UniverseStateImpl &&
            (identical(other.isLoading, isLoading) ||
                other.isLoading == isLoading) &&
            (identical(other.error, error) || other.error == error) &&
            const DeepCollectionEquality()
                .equals(other._connectors, _connectors) &&
            const DeepCollectionEquality()
                .equals(other._relationshipData, _relationshipData) &&
            const DeepCollectionEquality()
                .equals(other._celestialObjects, _celestialObjects) &&
            const DeepCollectionEquality()
                .equals(other._connections, _connections) &&
            (identical(other.totalConnectors, totalConnectors) ||
                other.totalConnectors == totalConnectors) &&
            (identical(other.runningConnectors, runningConnectors) ||
                other.runningConnectors == runningConnectors) &&
            (identical(other.errorConnectors, errorConnectors) ||
                other.errorConnectors == errorConnectors) &&
            (identical(other.totalConnections, totalConnections) ||
                other.totalConnections == totalConnections) &&
            (identical(other.lastUpdated, lastUpdated) ||
                other.lastUpdated == lastUpdated) &&
            (identical(other.selectedConnectorId, selectedConnectorId) ||
                other.selectedConnectorId == selectedConnectorId) &&
            const DeepCollectionEquality()
                .equals(other._selectedConnectorInfo, _selectedConnectorInfo));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      isLoading,
      error,
      const DeepCollectionEquality().hash(_connectors),
      const DeepCollectionEquality().hash(_relationshipData),
      const DeepCollectionEquality().hash(_celestialObjects),
      const DeepCollectionEquality().hash(_connections),
      totalConnectors,
      runningConnectors,
      errorConnectors,
      totalConnections,
      lastUpdated,
      selectedConnectorId,
      const DeepCollectionEquality().hash(_selectedConnectorInfo));

  /// Create a copy of UniverseState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$UniverseStateImplCopyWith<_$UniverseStateImpl> get copyWith =>
      __$$UniverseStateImplCopyWithImpl<_$UniverseStateImpl>(this, _$identity);
}

abstract class _UniverseState implements UniverseState {
  const factory _UniverseState(
      {final bool isLoading,
      final String? error,
      final List<ConnectorInfo> connectors,
      final Map<String, dynamic> relationshipData,
      final List<CelestialObject> celestialObjects,
      final List<StarConnection> connections,
      final int totalConnectors,
      final int runningConnectors,
      final int errorConnectors,
      final int totalConnections,
      final DateTime? lastUpdated,
      final String? selectedConnectorId,
      final Map<String, dynamic>? selectedConnectorInfo}) = _$UniverseStateImpl;

// 数据加载状态
  @override
  bool get isLoading;
  @override
  String? get error; // 原始数据
  @override
  List<ConnectorInfo> get connectors;
  @override
  Map<String, dynamic> get relationshipData; // 转换后的3D对象
  @override
  List<CelestialObject> get celestialObjects;
  @override
  List<StarConnection> get connections; // 统计信息
  @override
  int get totalConnectors;
  @override
  int get runningConnectors;
  @override
  int get errorConnectors;
  @override
  int get totalConnections; // 最后更新时间
  @override
  DateTime? get lastUpdated; // 选中状态
  @override
  String? get selectedConnectorId;
  @override
  Map<String, dynamic>? get selectedConnectorInfo;

  /// Create a copy of UniverseState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$UniverseStateImplCopyWith<_$UniverseStateImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
