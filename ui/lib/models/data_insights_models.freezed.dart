// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'data_insights_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

TodayStats _$TodayStatsFromJson(Map<String, dynamic> json) {
  return _TodayStats.fromJson(json);
}

/// @nodoc
mixin _$TodayStats {
  int get newEntities => throw _privateConstructorUsedError;
  int get activeConnectors => throw _privateConstructorUsedError;
  int get aiAnalysisCompleted => throw _privateConstructorUsedError;
  int get knowledgeConnections => throw _privateConstructorUsedError;

  /// Serializes this TodayStats to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of TodayStats
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $TodayStatsCopyWith<TodayStats> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $TodayStatsCopyWith<$Res> {
  factory $TodayStatsCopyWith(
          TodayStats value, $Res Function(TodayStats) then) =
      _$TodayStatsCopyWithImpl<$Res, TodayStats>;
  @useResult
  $Res call(
      {int newEntities,
      int activeConnectors,
      int aiAnalysisCompleted,
      int knowledgeConnections});
}

/// @nodoc
class _$TodayStatsCopyWithImpl<$Res, $Val extends TodayStats>
    implements $TodayStatsCopyWith<$Res> {
  _$TodayStatsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of TodayStats
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? newEntities = null,
    Object? activeConnectors = null,
    Object? aiAnalysisCompleted = null,
    Object? knowledgeConnections = null,
  }) {
    return _then(_value.copyWith(
      newEntities: null == newEntities
          ? _value.newEntities
          : newEntities // ignore: cast_nullable_to_non_nullable
              as int,
      activeConnectors: null == activeConnectors
          ? _value.activeConnectors
          : activeConnectors // ignore: cast_nullable_to_non_nullable
              as int,
      aiAnalysisCompleted: null == aiAnalysisCompleted
          ? _value.aiAnalysisCompleted
          : aiAnalysisCompleted // ignore: cast_nullable_to_non_nullable
              as int,
      knowledgeConnections: null == knowledgeConnections
          ? _value.knowledgeConnections
          : knowledgeConnections // ignore: cast_nullable_to_non_nullable
              as int,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$TodayStatsImplCopyWith<$Res>
    implements $TodayStatsCopyWith<$Res> {
  factory _$$TodayStatsImplCopyWith(
          _$TodayStatsImpl value, $Res Function(_$TodayStatsImpl) then) =
      __$$TodayStatsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int newEntities,
      int activeConnectors,
      int aiAnalysisCompleted,
      int knowledgeConnections});
}

/// @nodoc
class __$$TodayStatsImplCopyWithImpl<$Res>
    extends _$TodayStatsCopyWithImpl<$Res, _$TodayStatsImpl>
    implements _$$TodayStatsImplCopyWith<$Res> {
  __$$TodayStatsImplCopyWithImpl(
      _$TodayStatsImpl _value, $Res Function(_$TodayStatsImpl) _then)
      : super(_value, _then);

  /// Create a copy of TodayStats
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? newEntities = null,
    Object? activeConnectors = null,
    Object? aiAnalysisCompleted = null,
    Object? knowledgeConnections = null,
  }) {
    return _then(_$TodayStatsImpl(
      newEntities: null == newEntities
          ? _value.newEntities
          : newEntities // ignore: cast_nullable_to_non_nullable
              as int,
      activeConnectors: null == activeConnectors
          ? _value.activeConnectors
          : activeConnectors // ignore: cast_nullable_to_non_nullable
              as int,
      aiAnalysisCompleted: null == aiAnalysisCompleted
          ? _value.aiAnalysisCompleted
          : aiAnalysisCompleted // ignore: cast_nullable_to_non_nullable
              as int,
      knowledgeConnections: null == knowledgeConnections
          ? _value.knowledgeConnections
          : knowledgeConnections // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$TodayStatsImpl implements _TodayStats {
  const _$TodayStatsImpl(
      {this.newEntities = 0,
      this.activeConnectors = 0,
      this.aiAnalysisCompleted = 0,
      this.knowledgeConnections = 0});

  factory _$TodayStatsImpl.fromJson(Map<String, dynamic> json) =>
      _$$TodayStatsImplFromJson(json);

  @override
  @JsonKey()
  final int newEntities;
  @override
  @JsonKey()
  final int activeConnectors;
  @override
  @JsonKey()
  final int aiAnalysisCompleted;
  @override
  @JsonKey()
  final int knowledgeConnections;

  @override
  String toString() {
    return 'TodayStats(newEntities: $newEntities, activeConnectors: $activeConnectors, aiAnalysisCompleted: $aiAnalysisCompleted, knowledgeConnections: $knowledgeConnections)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$TodayStatsImpl &&
            (identical(other.newEntities, newEntities) ||
                other.newEntities == newEntities) &&
            (identical(other.activeConnectors, activeConnectors) ||
                other.activeConnectors == activeConnectors) &&
            (identical(other.aiAnalysisCompleted, aiAnalysisCompleted) ||
                other.aiAnalysisCompleted == aiAnalysisCompleted) &&
            (identical(other.knowledgeConnections, knowledgeConnections) ||
                other.knowledgeConnections == knowledgeConnections));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, newEntities, activeConnectors,
      aiAnalysisCompleted, knowledgeConnections);

  /// Create a copy of TodayStats
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$TodayStatsImplCopyWith<_$TodayStatsImpl> get copyWith =>
      __$$TodayStatsImplCopyWithImpl<_$TodayStatsImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$TodayStatsImplToJson(
      this,
    );
  }
}

abstract class _TodayStats implements TodayStats {
  const factory _TodayStats(
      {final int newEntities,
      final int activeConnectors,
      final int aiAnalysisCompleted,
      final int knowledgeConnections}) = _$TodayStatsImpl;

  factory _TodayStats.fromJson(Map<String, dynamic> json) =
      _$TodayStatsImpl.fromJson;

  @override
  int get newEntities;
  @override
  int get activeConnectors;
  @override
  int get aiAnalysisCompleted;
  @override
  int get knowledgeConnections;

  /// Create a copy of TodayStats
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$TodayStatsImplCopyWith<_$TodayStatsImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

EntityBreakdown _$EntityBreakdownFromJson(Map<String, dynamic> json) {
  return _EntityBreakdown.fromJson(json);
}

/// @nodoc
mixin _$EntityBreakdown {
  int get url => throw _privateConstructorUsedError;
  int get filePath => throw _privateConstructorUsedError;
  int get email => throw _privateConstructorUsedError;
  int get phone => throw _privateConstructorUsedError;
  int get keyword => throw _privateConstructorUsedError;
  int get other => throw _privateConstructorUsedError;

  /// Serializes this EntityBreakdown to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of EntityBreakdown
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $EntityBreakdownCopyWith<EntityBreakdown> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $EntityBreakdownCopyWith<$Res> {
  factory $EntityBreakdownCopyWith(
          EntityBreakdown value, $Res Function(EntityBreakdown) then) =
      _$EntityBreakdownCopyWithImpl<$Res, EntityBreakdown>;
  @useResult
  $Res call(
      {int url, int filePath, int email, int phone, int keyword, int other});
}

/// @nodoc
class _$EntityBreakdownCopyWithImpl<$Res, $Val extends EntityBreakdown>
    implements $EntityBreakdownCopyWith<$Res> {
  _$EntityBreakdownCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of EntityBreakdown
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? url = null,
    Object? filePath = null,
    Object? email = null,
    Object? phone = null,
    Object? keyword = null,
    Object? other = null,
  }) {
    return _then(_value.copyWith(
      url: null == url
          ? _value.url
          : url // ignore: cast_nullable_to_non_nullable
              as int,
      filePath: null == filePath
          ? _value.filePath
          : filePath // ignore: cast_nullable_to_non_nullable
              as int,
      email: null == email
          ? _value.email
          : email // ignore: cast_nullable_to_non_nullable
              as int,
      phone: null == phone
          ? _value.phone
          : phone // ignore: cast_nullable_to_non_nullable
              as int,
      keyword: null == keyword
          ? _value.keyword
          : keyword // ignore: cast_nullable_to_non_nullable
              as int,
      other: null == other
          ? _value.other
          : other // ignore: cast_nullable_to_non_nullable
              as int,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$EntityBreakdownImplCopyWith<$Res>
    implements $EntityBreakdownCopyWith<$Res> {
  factory _$$EntityBreakdownImplCopyWith(_$EntityBreakdownImpl value,
          $Res Function(_$EntityBreakdownImpl) then) =
      __$$EntityBreakdownImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int url, int filePath, int email, int phone, int keyword, int other});
}

/// @nodoc
class __$$EntityBreakdownImplCopyWithImpl<$Res>
    extends _$EntityBreakdownCopyWithImpl<$Res, _$EntityBreakdownImpl>
    implements _$$EntityBreakdownImplCopyWith<$Res> {
  __$$EntityBreakdownImplCopyWithImpl(
      _$EntityBreakdownImpl _value, $Res Function(_$EntityBreakdownImpl) _then)
      : super(_value, _then);

  /// Create a copy of EntityBreakdown
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? url = null,
    Object? filePath = null,
    Object? email = null,
    Object? phone = null,
    Object? keyword = null,
    Object? other = null,
  }) {
    return _then(_$EntityBreakdownImpl(
      url: null == url
          ? _value.url
          : url // ignore: cast_nullable_to_non_nullable
              as int,
      filePath: null == filePath
          ? _value.filePath
          : filePath // ignore: cast_nullable_to_non_nullable
              as int,
      email: null == email
          ? _value.email
          : email // ignore: cast_nullable_to_non_nullable
              as int,
      phone: null == phone
          ? _value.phone
          : phone // ignore: cast_nullable_to_non_nullable
              as int,
      keyword: null == keyword
          ? _value.keyword
          : keyword // ignore: cast_nullable_to_non_nullable
              as int,
      other: null == other
          ? _value.other
          : other // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$EntityBreakdownImpl implements _EntityBreakdown {
  const _$EntityBreakdownImpl(
      {this.url = 0,
      this.filePath = 0,
      this.email = 0,
      this.phone = 0,
      this.keyword = 0,
      this.other = 0});

  factory _$EntityBreakdownImpl.fromJson(Map<String, dynamic> json) =>
      _$$EntityBreakdownImplFromJson(json);

  @override
  @JsonKey()
  final int url;
  @override
  @JsonKey()
  final int filePath;
  @override
  @JsonKey()
  final int email;
  @override
  @JsonKey()
  final int phone;
  @override
  @JsonKey()
  final int keyword;
  @override
  @JsonKey()
  final int other;

  @override
  String toString() {
    return 'EntityBreakdown(url: $url, filePath: $filePath, email: $email, phone: $phone, keyword: $keyword, other: $other)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$EntityBreakdownImpl &&
            (identical(other.url, url) || other.url == url) &&
            (identical(other.filePath, filePath) ||
                other.filePath == filePath) &&
            (identical(other.email, email) || other.email == email) &&
            (identical(other.phone, phone) || other.phone == phone) &&
            (identical(other.keyword, keyword) || other.keyword == keyword) &&
            (identical(other.other, this.other) || other.other == this.other));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, url, filePath, email, phone, keyword, other);

  /// Create a copy of EntityBreakdown
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$EntityBreakdownImplCopyWith<_$EntityBreakdownImpl> get copyWith =>
      __$$EntityBreakdownImplCopyWithImpl<_$EntityBreakdownImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$EntityBreakdownImplToJson(
      this,
    );
  }
}

abstract class _EntityBreakdown implements EntityBreakdown {
  const factory _EntityBreakdown(
      {final int url,
      final int filePath,
      final int email,
      final int phone,
      final int keyword,
      final int other}) = _$EntityBreakdownImpl;

  factory _EntityBreakdown.fromJson(Map<String, dynamic> json) =
      _$EntityBreakdownImpl.fromJson;

  @override
  int get url;
  @override
  int get filePath;
  @override
  int get email;
  @override
  int get phone;
  @override
  int get keyword;
  @override
  int get other;

  /// Create a copy of EntityBreakdown
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$EntityBreakdownImplCopyWith<_$EntityBreakdownImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

AIInsight _$AIInsightFromJson(Map<String, dynamic> json) {
  return _AIInsight.fromJson(json);
}

/// @nodoc
mixin _$AIInsight {
  String get type => throw _privateConstructorUsedError;
  String get title => throw _privateConstructorUsedError;
  String get description => throw _privateConstructorUsedError;
  double get confidence => throw _privateConstructorUsedError;
  List<String> get entities => throw _privateConstructorUsedError;
  DateTime? get detectedAt => throw _privateConstructorUsedError;
  String? get iconName => throw _privateConstructorUsedError;
  String? get actionLabel => throw _privateConstructorUsedError;

  /// Serializes this AIInsight to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of AIInsight
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $AIInsightCopyWith<AIInsight> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AIInsightCopyWith<$Res> {
  factory $AIInsightCopyWith(AIInsight value, $Res Function(AIInsight) then) =
      _$AIInsightCopyWithImpl<$Res, AIInsight>;
  @useResult
  $Res call(
      {String type,
      String title,
      String description,
      double confidence,
      List<String> entities,
      DateTime? detectedAt,
      String? iconName,
      String? actionLabel});
}

/// @nodoc
class _$AIInsightCopyWithImpl<$Res, $Val extends AIInsight>
    implements $AIInsightCopyWith<$Res> {
  _$AIInsightCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of AIInsight
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? type = null,
    Object? title = null,
    Object? description = null,
    Object? confidence = null,
    Object? entities = null,
    Object? detectedAt = freezed,
    Object? iconName = freezed,
    Object? actionLabel = freezed,
  }) {
    return _then(_value.copyWith(
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      confidence: null == confidence
          ? _value.confidence
          : confidence // ignore: cast_nullable_to_non_nullable
              as double,
      entities: null == entities
          ? _value.entities
          : entities // ignore: cast_nullable_to_non_nullable
              as List<String>,
      detectedAt: freezed == detectedAt
          ? _value.detectedAt
          : detectedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      iconName: freezed == iconName
          ? _value.iconName
          : iconName // ignore: cast_nullable_to_non_nullable
              as String?,
      actionLabel: freezed == actionLabel
          ? _value.actionLabel
          : actionLabel // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$AIInsightImplCopyWith<$Res>
    implements $AIInsightCopyWith<$Res> {
  factory _$$AIInsightImplCopyWith(
          _$AIInsightImpl value, $Res Function(_$AIInsightImpl) then) =
      __$$AIInsightImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String type,
      String title,
      String description,
      double confidence,
      List<String> entities,
      DateTime? detectedAt,
      String? iconName,
      String? actionLabel});
}

/// @nodoc
class __$$AIInsightImplCopyWithImpl<$Res>
    extends _$AIInsightCopyWithImpl<$Res, _$AIInsightImpl>
    implements _$$AIInsightImplCopyWith<$Res> {
  __$$AIInsightImplCopyWithImpl(
      _$AIInsightImpl _value, $Res Function(_$AIInsightImpl) _then)
      : super(_value, _then);

  /// Create a copy of AIInsight
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? type = null,
    Object? title = null,
    Object? description = null,
    Object? confidence = null,
    Object? entities = null,
    Object? detectedAt = freezed,
    Object? iconName = freezed,
    Object? actionLabel = freezed,
  }) {
    return _then(_$AIInsightImpl(
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      confidence: null == confidence
          ? _value.confidence
          : confidence // ignore: cast_nullable_to_non_nullable
              as double,
      entities: null == entities
          ? _value._entities
          : entities // ignore: cast_nullable_to_non_nullable
              as List<String>,
      detectedAt: freezed == detectedAt
          ? _value.detectedAt
          : detectedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      iconName: freezed == iconName
          ? _value.iconName
          : iconName // ignore: cast_nullable_to_non_nullable
              as String?,
      actionLabel: freezed == actionLabel
          ? _value.actionLabel
          : actionLabel // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$AIInsightImpl implements _AIInsight {
  const _$AIInsightImpl(
      {required this.type,
      required this.title,
      required this.description,
      this.confidence = 0.0,
      final List<String> entities = const [],
      this.detectedAt,
      this.iconName,
      this.actionLabel})
      : _entities = entities;

  factory _$AIInsightImpl.fromJson(Map<String, dynamic> json) =>
      _$$AIInsightImplFromJson(json);

  @override
  final String type;
  @override
  final String title;
  @override
  final String description;
  @override
  @JsonKey()
  final double confidence;
  final List<String> _entities;
  @override
  @JsonKey()
  List<String> get entities {
    if (_entities is EqualUnmodifiableListView) return _entities;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_entities);
  }

  @override
  final DateTime? detectedAt;
  @override
  final String? iconName;
  @override
  final String? actionLabel;

  @override
  String toString() {
    return 'AIInsight(type: $type, title: $title, description: $description, confidence: $confidence, entities: $entities, detectedAt: $detectedAt, iconName: $iconName, actionLabel: $actionLabel)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$AIInsightImpl &&
            (identical(other.type, type) || other.type == type) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.confidence, confidence) ||
                other.confidence == confidence) &&
            const DeepCollectionEquality().equals(other._entities, _entities) &&
            (identical(other.detectedAt, detectedAt) ||
                other.detectedAt == detectedAt) &&
            (identical(other.iconName, iconName) ||
                other.iconName == iconName) &&
            (identical(other.actionLabel, actionLabel) ||
                other.actionLabel == actionLabel));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      type,
      title,
      description,
      confidence,
      const DeepCollectionEquality().hash(_entities),
      detectedAt,
      iconName,
      actionLabel);

  /// Create a copy of AIInsight
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$AIInsightImplCopyWith<_$AIInsightImpl> get copyWith =>
      __$$AIInsightImplCopyWithImpl<_$AIInsightImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$AIInsightImplToJson(
      this,
    );
  }
}

abstract class _AIInsight implements AIInsight {
  const factory _AIInsight(
      {required final String type,
      required final String title,
      required final String description,
      final double confidence,
      final List<String> entities,
      final DateTime? detectedAt,
      final String? iconName,
      final String? actionLabel}) = _$AIInsightImpl;

  factory _AIInsight.fromJson(Map<String, dynamic> json) =
      _$AIInsightImpl.fromJson;

  @override
  String get type;
  @override
  String get title;
  @override
  String get description;
  @override
  double get confidence;
  @override
  List<String> get entities;
  @override
  DateTime? get detectedAt;
  @override
  String? get iconName;
  @override
  String? get actionLabel;

  /// Create a copy of AIInsight
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$AIInsightImplCopyWith<_$AIInsightImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

TrendingEntity _$TrendingEntityFromJson(Map<String, dynamic> json) {
  return _TrendingEntity.fromJson(json);
}

/// @nodoc
mixin _$TrendingEntity {
  String get name => throw _privateConstructorUsedError;
  String get type => throw _privateConstructorUsedError;
  int get frequency => throw _privateConstructorUsedError;
  String? get trend => throw _privateConstructorUsedError;
  double? get trendValue => throw _privateConstructorUsedError;
  String? get description => throw _privateConstructorUsedError;

  /// Serializes this TrendingEntity to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of TrendingEntity
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $TrendingEntityCopyWith<TrendingEntity> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $TrendingEntityCopyWith<$Res> {
  factory $TrendingEntityCopyWith(
          TrendingEntity value, $Res Function(TrendingEntity) then) =
      _$TrendingEntityCopyWithImpl<$Res, TrendingEntity>;
  @useResult
  $Res call(
      {String name,
      String type,
      int frequency,
      String? trend,
      double? trendValue,
      String? description});
}

/// @nodoc
class _$TrendingEntityCopyWithImpl<$Res, $Val extends TrendingEntity>
    implements $TrendingEntityCopyWith<$Res> {
  _$TrendingEntityCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of TrendingEntity
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? type = null,
    Object? frequency = null,
    Object? trend = freezed,
    Object? trendValue = freezed,
    Object? description = freezed,
  }) {
    return _then(_value.copyWith(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      frequency: null == frequency
          ? _value.frequency
          : frequency // ignore: cast_nullable_to_non_nullable
              as int,
      trend: freezed == trend
          ? _value.trend
          : trend // ignore: cast_nullable_to_non_nullable
              as String?,
      trendValue: freezed == trendValue
          ? _value.trendValue
          : trendValue // ignore: cast_nullable_to_non_nullable
              as double?,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$TrendingEntityImplCopyWith<$Res>
    implements $TrendingEntityCopyWith<$Res> {
  factory _$$TrendingEntityImplCopyWith(_$TrendingEntityImpl value,
          $Res Function(_$TrendingEntityImpl) then) =
      __$$TrendingEntityImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String name,
      String type,
      int frequency,
      String? trend,
      double? trendValue,
      String? description});
}

/// @nodoc
class __$$TrendingEntityImplCopyWithImpl<$Res>
    extends _$TrendingEntityCopyWithImpl<$Res, _$TrendingEntityImpl>
    implements _$$TrendingEntityImplCopyWith<$Res> {
  __$$TrendingEntityImplCopyWithImpl(
      _$TrendingEntityImpl _value, $Res Function(_$TrendingEntityImpl) _then)
      : super(_value, _then);

  /// Create a copy of TrendingEntity
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? type = null,
    Object? frequency = null,
    Object? trend = freezed,
    Object? trendValue = freezed,
    Object? description = freezed,
  }) {
    return _then(_$TrendingEntityImpl(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      frequency: null == frequency
          ? _value.frequency
          : frequency // ignore: cast_nullable_to_non_nullable
              as int,
      trend: freezed == trend
          ? _value.trend
          : trend // ignore: cast_nullable_to_non_nullable
              as String?,
      trendValue: freezed == trendValue
          ? _value.trendValue
          : trendValue // ignore: cast_nullable_to_non_nullable
              as double?,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$TrendingEntityImpl implements _TrendingEntity {
  const _$TrendingEntityImpl(
      {required this.name,
      required this.type,
      this.frequency = 0,
      this.trend,
      this.trendValue,
      this.description});

  factory _$TrendingEntityImpl.fromJson(Map<String, dynamic> json) =>
      _$$TrendingEntityImplFromJson(json);

  @override
  final String name;
  @override
  final String type;
  @override
  @JsonKey()
  final int frequency;
  @override
  final String? trend;
  @override
  final double? trendValue;
  @override
  final String? description;

  @override
  String toString() {
    return 'TrendingEntity(name: $name, type: $type, frequency: $frequency, trend: $trend, trendValue: $trendValue, description: $description)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$TrendingEntityImpl &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.type, type) || other.type == type) &&
            (identical(other.frequency, frequency) ||
                other.frequency == frequency) &&
            (identical(other.trend, trend) || other.trend == trend) &&
            (identical(other.trendValue, trendValue) ||
                other.trendValue == trendValue) &&
            (identical(other.description, description) ||
                other.description == description));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType, name, type, frequency, trend, trendValue, description);

  /// Create a copy of TrendingEntity
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$TrendingEntityImplCopyWith<_$TrendingEntityImpl> get copyWith =>
      __$$TrendingEntityImplCopyWithImpl<_$TrendingEntityImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$TrendingEntityImplToJson(
      this,
    );
  }
}

abstract class _TrendingEntity implements TrendingEntity {
  const factory _TrendingEntity(
      {required final String name,
      required final String type,
      final int frequency,
      final String? trend,
      final double? trendValue,
      final String? description}) = _$TrendingEntityImpl;

  factory _TrendingEntity.fromJson(Map<String, dynamic> json) =
      _$TrendingEntityImpl.fromJson;

  @override
  String get name;
  @override
  String get type;
  @override
  int get frequency;
  @override
  String? get trend;
  @override
  double? get trendValue;
  @override
  String? get description;

  /// Create a copy of TrendingEntity
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$TrendingEntityImplCopyWith<_$TrendingEntityImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

EntityDetail _$EntityDetailFromJson(Map<String, dynamic> json) {
  return _EntityDetail.fromJson(json);
}

/// @nodoc
mixin _$EntityDetail {
  String get id => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get type => throw _privateConstructorUsedError;
  String? get description => throw _privateConstructorUsedError;
  DateTime? get createdAt => throw _privateConstructorUsedError;
  DateTime? get lastAccessed => throw _privateConstructorUsedError;
  int get accessCount => throw _privateConstructorUsedError;
  Map<String, dynamic>? get properties => throw _privateConstructorUsedError;
  List<String> get tags => throw _privateConstructorUsedError;

  /// Serializes this EntityDetail to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of EntityDetail
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $EntityDetailCopyWith<EntityDetail> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $EntityDetailCopyWith<$Res> {
  factory $EntityDetailCopyWith(
          EntityDetail value, $Res Function(EntityDetail) then) =
      _$EntityDetailCopyWithImpl<$Res, EntityDetail>;
  @useResult
  $Res call(
      {String id,
      String name,
      String type,
      String? description,
      DateTime? createdAt,
      DateTime? lastAccessed,
      int accessCount,
      Map<String, dynamic>? properties,
      List<String> tags});
}

/// @nodoc
class _$EntityDetailCopyWithImpl<$Res, $Val extends EntityDetail>
    implements $EntityDetailCopyWith<$Res> {
  _$EntityDetailCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of EntityDetail
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? type = null,
    Object? description = freezed,
    Object? createdAt = freezed,
    Object? lastAccessed = freezed,
    Object? accessCount = null,
    Object? properties = freezed,
    Object? tags = null,
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
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      lastAccessed: freezed == lastAccessed
          ? _value.lastAccessed
          : lastAccessed // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      accessCount: null == accessCount
          ? _value.accessCount
          : accessCount // ignore: cast_nullable_to_non_nullable
              as int,
      properties: freezed == properties
          ? _value.properties
          : properties // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      tags: null == tags
          ? _value.tags
          : tags // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$EntityDetailImplCopyWith<$Res>
    implements $EntityDetailCopyWith<$Res> {
  factory _$$EntityDetailImplCopyWith(
          _$EntityDetailImpl value, $Res Function(_$EntityDetailImpl) then) =
      __$$EntityDetailImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String name,
      String type,
      String? description,
      DateTime? createdAt,
      DateTime? lastAccessed,
      int accessCount,
      Map<String, dynamic>? properties,
      List<String> tags});
}

/// @nodoc
class __$$EntityDetailImplCopyWithImpl<$Res>
    extends _$EntityDetailCopyWithImpl<$Res, _$EntityDetailImpl>
    implements _$$EntityDetailImplCopyWith<$Res> {
  __$$EntityDetailImplCopyWithImpl(
      _$EntityDetailImpl _value, $Res Function(_$EntityDetailImpl) _then)
      : super(_value, _then);

  /// Create a copy of EntityDetail
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? type = null,
    Object? description = freezed,
    Object? createdAt = freezed,
    Object? lastAccessed = freezed,
    Object? accessCount = null,
    Object? properties = freezed,
    Object? tags = null,
  }) {
    return _then(_$EntityDetailImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      lastAccessed: freezed == lastAccessed
          ? _value.lastAccessed
          : lastAccessed // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      accessCount: null == accessCount
          ? _value.accessCount
          : accessCount // ignore: cast_nullable_to_non_nullable
              as int,
      properties: freezed == properties
          ? _value._properties
          : properties // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      tags: null == tags
          ? _value._tags
          : tags // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$EntityDetailImpl implements _EntityDetail {
  const _$EntityDetailImpl(
      {required this.id,
      required this.name,
      required this.type,
      this.description,
      this.createdAt,
      this.lastAccessed,
      this.accessCount = 0,
      final Map<String, dynamic>? properties,
      final List<String> tags = const []})
      : _properties = properties,
        _tags = tags;

  factory _$EntityDetailImpl.fromJson(Map<String, dynamic> json) =>
      _$$EntityDetailImplFromJson(json);

  @override
  final String id;
  @override
  final String name;
  @override
  final String type;
  @override
  final String? description;
  @override
  final DateTime? createdAt;
  @override
  final DateTime? lastAccessed;
  @override
  @JsonKey()
  final int accessCount;
  final Map<String, dynamic>? _properties;
  @override
  Map<String, dynamic>? get properties {
    final value = _properties;
    if (value == null) return null;
    if (_properties is EqualUnmodifiableMapView) return _properties;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  final List<String> _tags;
  @override
  @JsonKey()
  List<String> get tags {
    if (_tags is EqualUnmodifiableListView) return _tags;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_tags);
  }

  @override
  String toString() {
    return 'EntityDetail(id: $id, name: $name, type: $type, description: $description, createdAt: $createdAt, lastAccessed: $lastAccessed, accessCount: $accessCount, properties: $properties, tags: $tags)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$EntityDetailImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.type, type) || other.type == type) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.lastAccessed, lastAccessed) ||
                other.lastAccessed == lastAccessed) &&
            (identical(other.accessCount, accessCount) ||
                other.accessCount == accessCount) &&
            const DeepCollectionEquality()
                .equals(other._properties, _properties) &&
            const DeepCollectionEquality().equals(other._tags, _tags));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      name,
      type,
      description,
      createdAt,
      lastAccessed,
      accessCount,
      const DeepCollectionEquality().hash(_properties),
      const DeepCollectionEquality().hash(_tags));

  /// Create a copy of EntityDetail
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$EntityDetailImplCopyWith<_$EntityDetailImpl> get copyWith =>
      __$$EntityDetailImplCopyWithImpl<_$EntityDetailImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$EntityDetailImplToJson(
      this,
    );
  }
}

abstract class _EntityDetail implements EntityDetail {
  const factory _EntityDetail(
      {required final String id,
      required final String name,
      required final String type,
      final String? description,
      final DateTime? createdAt,
      final DateTime? lastAccessed,
      final int accessCount,
      final Map<String, dynamic>? properties,
      final List<String> tags}) = _$EntityDetailImpl;

  factory _EntityDetail.fromJson(Map<String, dynamic> json) =
      _$EntityDetailImpl.fromJson;

  @override
  String get id;
  @override
  String get name;
  @override
  String get type;
  @override
  String? get description;
  @override
  DateTime? get createdAt;
  @override
  DateTime? get lastAccessed;
  @override
  int get accessCount;
  @override
  Map<String, dynamic>? get properties;
  @override
  List<String> get tags;

  /// Create a copy of EntityDetail
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$EntityDetailImplCopyWith<_$EntityDetailImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

TimelineItem _$TimelineItemFromJson(Map<String, dynamic> json) {
  return _TimelineItem.fromJson(json);
}

/// @nodoc
mixin _$TimelineItem {
  String get id => throw _privateConstructorUsedError;
  String get title => throw _privateConstructorUsedError;
  String? get description => throw _privateConstructorUsedError;
  DateTime get timestamp => throw _privateConstructorUsedError;
  String get type =>
      throw _privateConstructorUsedError; // 'entity_created', 'insight_generated', 'connector_activity'
  Map<String, dynamic>? get metadata => throw _privateConstructorUsedError;
  String? get iconName => throw _privateConstructorUsedError;
  String? get connectorId => throw _privateConstructorUsedError;

  /// Serializes this TimelineItem to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of TimelineItem
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $TimelineItemCopyWith<TimelineItem> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $TimelineItemCopyWith<$Res> {
  factory $TimelineItemCopyWith(
          TimelineItem value, $Res Function(TimelineItem) then) =
      _$TimelineItemCopyWithImpl<$Res, TimelineItem>;
  @useResult
  $Res call(
      {String id,
      String title,
      String? description,
      DateTime timestamp,
      String type,
      Map<String, dynamic>? metadata,
      String? iconName,
      String? connectorId});
}

/// @nodoc
class _$TimelineItemCopyWithImpl<$Res, $Val extends TimelineItem>
    implements $TimelineItemCopyWith<$Res> {
  _$TimelineItemCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of TimelineItem
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? title = null,
    Object? description = freezed,
    Object? timestamp = null,
    Object? type = null,
    Object? metadata = freezed,
    Object? iconName = freezed,
    Object? connectorId = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      metadata: freezed == metadata
          ? _value.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      iconName: freezed == iconName
          ? _value.iconName
          : iconName // ignore: cast_nullable_to_non_nullable
              as String?,
      connectorId: freezed == connectorId
          ? _value.connectorId
          : connectorId // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$TimelineItemImplCopyWith<$Res>
    implements $TimelineItemCopyWith<$Res> {
  factory _$$TimelineItemImplCopyWith(
          _$TimelineItemImpl value, $Res Function(_$TimelineItemImpl) then) =
      __$$TimelineItemImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String title,
      String? description,
      DateTime timestamp,
      String type,
      Map<String, dynamic>? metadata,
      String? iconName,
      String? connectorId});
}

/// @nodoc
class __$$TimelineItemImplCopyWithImpl<$Res>
    extends _$TimelineItemCopyWithImpl<$Res, _$TimelineItemImpl>
    implements _$$TimelineItemImplCopyWith<$Res> {
  __$$TimelineItemImplCopyWithImpl(
      _$TimelineItemImpl _value, $Res Function(_$TimelineItemImpl) _then)
      : super(_value, _then);

  /// Create a copy of TimelineItem
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? title = null,
    Object? description = freezed,
    Object? timestamp = null,
    Object? type = null,
    Object? metadata = freezed,
    Object? iconName = freezed,
    Object? connectorId = freezed,
  }) {
    return _then(_$TimelineItemImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      metadata: freezed == metadata
          ? _value._metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      iconName: freezed == iconName
          ? _value.iconName
          : iconName // ignore: cast_nullable_to_non_nullable
              as String?,
      connectorId: freezed == connectorId
          ? _value.connectorId
          : connectorId // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$TimelineItemImpl implements _TimelineItem {
  const _$TimelineItemImpl(
      {required this.id,
      required this.title,
      this.description,
      required this.timestamp,
      required this.type,
      final Map<String, dynamic>? metadata,
      this.iconName,
      this.connectorId})
      : _metadata = metadata;

  factory _$TimelineItemImpl.fromJson(Map<String, dynamic> json) =>
      _$$TimelineItemImplFromJson(json);

  @override
  final String id;
  @override
  final String title;
  @override
  final String? description;
  @override
  final DateTime timestamp;
  @override
  final String type;
// 'entity_created', 'insight_generated', 'connector_activity'
  final Map<String, dynamic>? _metadata;
// 'entity_created', 'insight_generated', 'connector_activity'
  @override
  Map<String, dynamic>? get metadata {
    final value = _metadata;
    if (value == null) return null;
    if (_metadata is EqualUnmodifiableMapView) return _metadata;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  final String? iconName;
  @override
  final String? connectorId;

  @override
  String toString() {
    return 'TimelineItem(id: $id, title: $title, description: $description, timestamp: $timestamp, type: $type, metadata: $metadata, iconName: $iconName, connectorId: $connectorId)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$TimelineItemImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp) &&
            (identical(other.type, type) || other.type == type) &&
            const DeepCollectionEquality().equals(other._metadata, _metadata) &&
            (identical(other.iconName, iconName) ||
                other.iconName == iconName) &&
            (identical(other.connectorId, connectorId) ||
                other.connectorId == connectorId));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      title,
      description,
      timestamp,
      type,
      const DeepCollectionEquality().hash(_metadata),
      iconName,
      connectorId);

  /// Create a copy of TimelineItem
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$TimelineItemImplCopyWith<_$TimelineItemImpl> get copyWith =>
      __$$TimelineItemImplCopyWithImpl<_$TimelineItemImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$TimelineItemImplToJson(
      this,
    );
  }
}

abstract class _TimelineItem implements TimelineItem {
  const factory _TimelineItem(
      {required final String id,
      required final String title,
      final String? description,
      required final DateTime timestamp,
      required final String type,
      final Map<String, dynamic>? metadata,
      final String? iconName,
      final String? connectorId}) = _$TimelineItemImpl;

  factory _TimelineItem.fromJson(Map<String, dynamic> json) =
      _$TimelineItemImpl.fromJson;

  @override
  String get id;
  @override
  String get title;
  @override
  String? get description;
  @override
  DateTime get timestamp;
  @override
  String
      get type; // 'entity_created', 'insight_generated', 'connector_activity'
  @override
  Map<String, dynamic>? get metadata;
  @override
  String? get iconName;
  @override
  String? get connectorId;

  /// Create a copy of TimelineItem
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$TimelineItemImplCopyWith<_$TimelineItemImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ConnectorStatus _$ConnectorStatusFromJson(Map<String, dynamic> json) {
  return _ConnectorStatus.fromJson(json);
}

/// @nodoc
mixin _$ConnectorStatus {
  String get id => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get status =>
      throw _privateConstructorUsedError; // 'running', 'stopped', 'error'
  bool get enabled => throw _privateConstructorUsedError;
  int get dataCount => throw _privateConstructorUsedError;
  DateTime? get lastHeartbeat => throw _privateConstructorUsedError;
  String? get errorMessage => throw _privateConstructorUsedError;

  /// Serializes this ConnectorStatus to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ConnectorStatus
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ConnectorStatusCopyWith<ConnectorStatus> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ConnectorStatusCopyWith<$Res> {
  factory $ConnectorStatusCopyWith(
          ConnectorStatus value, $Res Function(ConnectorStatus) then) =
      _$ConnectorStatusCopyWithImpl<$Res, ConnectorStatus>;
  @useResult
  $Res call(
      {String id,
      String name,
      String status,
      bool enabled,
      int dataCount,
      DateTime? lastHeartbeat,
      String? errorMessage});
}

/// @nodoc
class _$ConnectorStatusCopyWithImpl<$Res, $Val extends ConnectorStatus>
    implements $ConnectorStatusCopyWith<$Res> {
  _$ConnectorStatusCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ConnectorStatus
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? status = null,
    Object? enabled = null,
    Object? dataCount = null,
    Object? lastHeartbeat = freezed,
    Object? errorMessage = freezed,
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
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      enabled: null == enabled
          ? _value.enabled
          : enabled // ignore: cast_nullable_to_non_nullable
              as bool,
      dataCount: null == dataCount
          ? _value.dataCount
          : dataCount // ignore: cast_nullable_to_non_nullable
              as int,
      lastHeartbeat: freezed == lastHeartbeat
          ? _value.lastHeartbeat
          : lastHeartbeat // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      errorMessage: freezed == errorMessage
          ? _value.errorMessage
          : errorMessage // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ConnectorStatusImplCopyWith<$Res>
    implements $ConnectorStatusCopyWith<$Res> {
  factory _$$ConnectorStatusImplCopyWith(_$ConnectorStatusImpl value,
          $Res Function(_$ConnectorStatusImpl) then) =
      __$$ConnectorStatusImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String name,
      String status,
      bool enabled,
      int dataCount,
      DateTime? lastHeartbeat,
      String? errorMessage});
}

/// @nodoc
class __$$ConnectorStatusImplCopyWithImpl<$Res>
    extends _$ConnectorStatusCopyWithImpl<$Res, _$ConnectorStatusImpl>
    implements _$$ConnectorStatusImplCopyWith<$Res> {
  __$$ConnectorStatusImplCopyWithImpl(
      _$ConnectorStatusImpl _value, $Res Function(_$ConnectorStatusImpl) _then)
      : super(_value, _then);

  /// Create a copy of ConnectorStatus
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? status = null,
    Object? enabled = null,
    Object? dataCount = null,
    Object? lastHeartbeat = freezed,
    Object? errorMessage = freezed,
  }) {
    return _then(_$ConnectorStatusImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      enabled: null == enabled
          ? _value.enabled
          : enabled // ignore: cast_nullable_to_non_nullable
              as bool,
      dataCount: null == dataCount
          ? _value.dataCount
          : dataCount // ignore: cast_nullable_to_non_nullable
              as int,
      lastHeartbeat: freezed == lastHeartbeat
          ? _value.lastHeartbeat
          : lastHeartbeat // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      errorMessage: freezed == errorMessage
          ? _value.errorMessage
          : errorMessage // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ConnectorStatusImpl implements _ConnectorStatus {
  const _$ConnectorStatusImpl(
      {required this.id,
      required this.name,
      required this.status,
      this.enabled = true,
      this.dataCount = 0,
      this.lastHeartbeat,
      this.errorMessage});

  factory _$ConnectorStatusImpl.fromJson(Map<String, dynamic> json) =>
      _$$ConnectorStatusImplFromJson(json);

  @override
  final String id;
  @override
  final String name;
  @override
  final String status;
// 'running', 'stopped', 'error'
  @override
  @JsonKey()
  final bool enabled;
  @override
  @JsonKey()
  final int dataCount;
  @override
  final DateTime? lastHeartbeat;
  @override
  final String? errorMessage;

  @override
  String toString() {
    return 'ConnectorStatus(id: $id, name: $name, status: $status, enabled: $enabled, dataCount: $dataCount, lastHeartbeat: $lastHeartbeat, errorMessage: $errorMessage)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ConnectorStatusImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.enabled, enabled) || other.enabled == enabled) &&
            (identical(other.dataCount, dataCount) ||
                other.dataCount == dataCount) &&
            (identical(other.lastHeartbeat, lastHeartbeat) ||
                other.lastHeartbeat == lastHeartbeat) &&
            (identical(other.errorMessage, errorMessage) ||
                other.errorMessage == errorMessage));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, id, name, status, enabled,
      dataCount, lastHeartbeat, errorMessage);

  /// Create a copy of ConnectorStatus
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ConnectorStatusImplCopyWith<_$ConnectorStatusImpl> get copyWith =>
      __$$ConnectorStatusImplCopyWithImpl<_$ConnectorStatusImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ConnectorStatusImplToJson(
      this,
    );
  }
}

abstract class _ConnectorStatus implements ConnectorStatus {
  const factory _ConnectorStatus(
      {required final String id,
      required final String name,
      required final String status,
      final bool enabled,
      final int dataCount,
      final DateTime? lastHeartbeat,
      final String? errorMessage}) = _$ConnectorStatusImpl;

  factory _ConnectorStatus.fromJson(Map<String, dynamic> json) =
      _$ConnectorStatusImpl.fromJson;

  @override
  String get id;
  @override
  String get name;
  @override
  String get status; // 'running', 'stopped', 'error'
  @override
  bool get enabled;
  @override
  int get dataCount;
  @override
  DateTime? get lastHeartbeat;
  @override
  String? get errorMessage;

  /// Create a copy of ConnectorStatus
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ConnectorStatusImplCopyWith<_$ConnectorStatusImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

DataInsightsOverview _$DataInsightsOverviewFromJson(Map<String, dynamic> json) {
  return _DataInsightsOverview.fromJson(json);
}

/// @nodoc
mixin _$DataInsightsOverview {
  TodayStats get todayStats => throw _privateConstructorUsedError;
  EntityBreakdown get entityBreakdown => throw _privateConstructorUsedError;
  List<AIInsight> get recentInsights => throw _privateConstructorUsedError;
  List<TrendingEntity> get trendingEntities =>
      throw _privateConstructorUsedError;
  List<TimelineItem> get recentActivities => throw _privateConstructorUsedError;
  List<ConnectorStatus> get connectorStatuses =>
      throw _privateConstructorUsedError;
  DateTime? get lastUpdated => throw _privateConstructorUsedError;

  /// Serializes this DataInsightsOverview to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of DataInsightsOverview
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DataInsightsOverviewCopyWith<DataInsightsOverview> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DataInsightsOverviewCopyWith<$Res> {
  factory $DataInsightsOverviewCopyWith(DataInsightsOverview value,
          $Res Function(DataInsightsOverview) then) =
      _$DataInsightsOverviewCopyWithImpl<$Res, DataInsightsOverview>;
  @useResult
  $Res call(
      {TodayStats todayStats,
      EntityBreakdown entityBreakdown,
      List<AIInsight> recentInsights,
      List<TrendingEntity> trendingEntities,
      List<TimelineItem> recentActivities,
      List<ConnectorStatus> connectorStatuses,
      DateTime? lastUpdated});

  $TodayStatsCopyWith<$Res> get todayStats;
  $EntityBreakdownCopyWith<$Res> get entityBreakdown;
}

/// @nodoc
class _$DataInsightsOverviewCopyWithImpl<$Res,
        $Val extends DataInsightsOverview>
    implements $DataInsightsOverviewCopyWith<$Res> {
  _$DataInsightsOverviewCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DataInsightsOverview
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? todayStats = null,
    Object? entityBreakdown = null,
    Object? recentInsights = null,
    Object? trendingEntities = null,
    Object? recentActivities = null,
    Object? connectorStatuses = null,
    Object? lastUpdated = freezed,
  }) {
    return _then(_value.copyWith(
      todayStats: null == todayStats
          ? _value.todayStats
          : todayStats // ignore: cast_nullable_to_non_nullable
              as TodayStats,
      entityBreakdown: null == entityBreakdown
          ? _value.entityBreakdown
          : entityBreakdown // ignore: cast_nullable_to_non_nullable
              as EntityBreakdown,
      recentInsights: null == recentInsights
          ? _value.recentInsights
          : recentInsights // ignore: cast_nullable_to_non_nullable
              as List<AIInsight>,
      trendingEntities: null == trendingEntities
          ? _value.trendingEntities
          : trendingEntities // ignore: cast_nullable_to_non_nullable
              as List<TrendingEntity>,
      recentActivities: null == recentActivities
          ? _value.recentActivities
          : recentActivities // ignore: cast_nullable_to_non_nullable
              as List<TimelineItem>,
      connectorStatuses: null == connectorStatuses
          ? _value.connectorStatuses
          : connectorStatuses // ignore: cast_nullable_to_non_nullable
              as List<ConnectorStatus>,
      lastUpdated: freezed == lastUpdated
          ? _value.lastUpdated
          : lastUpdated // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ) as $Val);
  }

  /// Create a copy of DataInsightsOverview
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $TodayStatsCopyWith<$Res> get todayStats {
    return $TodayStatsCopyWith<$Res>(_value.todayStats, (value) {
      return _then(_value.copyWith(todayStats: value) as $Val);
    });
  }

  /// Create a copy of DataInsightsOverview
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $EntityBreakdownCopyWith<$Res> get entityBreakdown {
    return $EntityBreakdownCopyWith<$Res>(_value.entityBreakdown, (value) {
      return _then(_value.copyWith(entityBreakdown: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$DataInsightsOverviewImplCopyWith<$Res>
    implements $DataInsightsOverviewCopyWith<$Res> {
  factory _$$DataInsightsOverviewImplCopyWith(_$DataInsightsOverviewImpl value,
          $Res Function(_$DataInsightsOverviewImpl) then) =
      __$$DataInsightsOverviewImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {TodayStats todayStats,
      EntityBreakdown entityBreakdown,
      List<AIInsight> recentInsights,
      List<TrendingEntity> trendingEntities,
      List<TimelineItem> recentActivities,
      List<ConnectorStatus> connectorStatuses,
      DateTime? lastUpdated});

  @override
  $TodayStatsCopyWith<$Res> get todayStats;
  @override
  $EntityBreakdownCopyWith<$Res> get entityBreakdown;
}

/// @nodoc
class __$$DataInsightsOverviewImplCopyWithImpl<$Res>
    extends _$DataInsightsOverviewCopyWithImpl<$Res, _$DataInsightsOverviewImpl>
    implements _$$DataInsightsOverviewImplCopyWith<$Res> {
  __$$DataInsightsOverviewImplCopyWithImpl(_$DataInsightsOverviewImpl _value,
      $Res Function(_$DataInsightsOverviewImpl) _then)
      : super(_value, _then);

  /// Create a copy of DataInsightsOverview
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? todayStats = null,
    Object? entityBreakdown = null,
    Object? recentInsights = null,
    Object? trendingEntities = null,
    Object? recentActivities = null,
    Object? connectorStatuses = null,
    Object? lastUpdated = freezed,
  }) {
    return _then(_$DataInsightsOverviewImpl(
      todayStats: null == todayStats
          ? _value.todayStats
          : todayStats // ignore: cast_nullable_to_non_nullable
              as TodayStats,
      entityBreakdown: null == entityBreakdown
          ? _value.entityBreakdown
          : entityBreakdown // ignore: cast_nullable_to_non_nullable
              as EntityBreakdown,
      recentInsights: null == recentInsights
          ? _value._recentInsights
          : recentInsights // ignore: cast_nullable_to_non_nullable
              as List<AIInsight>,
      trendingEntities: null == trendingEntities
          ? _value._trendingEntities
          : trendingEntities // ignore: cast_nullable_to_non_nullable
              as List<TrendingEntity>,
      recentActivities: null == recentActivities
          ? _value._recentActivities
          : recentActivities // ignore: cast_nullable_to_non_nullable
              as List<TimelineItem>,
      connectorStatuses: null == connectorStatuses
          ? _value._connectorStatuses
          : connectorStatuses // ignore: cast_nullable_to_non_nullable
              as List<ConnectorStatus>,
      lastUpdated: freezed == lastUpdated
          ? _value.lastUpdated
          : lastUpdated // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DataInsightsOverviewImpl implements _DataInsightsOverview {
  const _$DataInsightsOverviewImpl(
      {required this.todayStats,
      required this.entityBreakdown,
      final List<AIInsight> recentInsights = const [],
      final List<TrendingEntity> trendingEntities = const [],
      final List<TimelineItem> recentActivities = const [],
      final List<ConnectorStatus> connectorStatuses = const [],
      this.lastUpdated})
      : _recentInsights = recentInsights,
        _trendingEntities = trendingEntities,
        _recentActivities = recentActivities,
        _connectorStatuses = connectorStatuses;

  factory _$DataInsightsOverviewImpl.fromJson(Map<String, dynamic> json) =>
      _$$DataInsightsOverviewImplFromJson(json);

  @override
  final TodayStats todayStats;
  @override
  final EntityBreakdown entityBreakdown;
  final List<AIInsight> _recentInsights;
  @override
  @JsonKey()
  List<AIInsight> get recentInsights {
    if (_recentInsights is EqualUnmodifiableListView) return _recentInsights;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_recentInsights);
  }

  final List<TrendingEntity> _trendingEntities;
  @override
  @JsonKey()
  List<TrendingEntity> get trendingEntities {
    if (_trendingEntities is EqualUnmodifiableListView)
      return _trendingEntities;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_trendingEntities);
  }

  final List<TimelineItem> _recentActivities;
  @override
  @JsonKey()
  List<TimelineItem> get recentActivities {
    if (_recentActivities is EqualUnmodifiableListView)
      return _recentActivities;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_recentActivities);
  }

  final List<ConnectorStatus> _connectorStatuses;
  @override
  @JsonKey()
  List<ConnectorStatus> get connectorStatuses {
    if (_connectorStatuses is EqualUnmodifiableListView)
      return _connectorStatuses;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_connectorStatuses);
  }

  @override
  final DateTime? lastUpdated;

  @override
  String toString() {
    return 'DataInsightsOverview(todayStats: $todayStats, entityBreakdown: $entityBreakdown, recentInsights: $recentInsights, trendingEntities: $trendingEntities, recentActivities: $recentActivities, connectorStatuses: $connectorStatuses, lastUpdated: $lastUpdated)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DataInsightsOverviewImpl &&
            (identical(other.todayStats, todayStats) ||
                other.todayStats == todayStats) &&
            (identical(other.entityBreakdown, entityBreakdown) ||
                other.entityBreakdown == entityBreakdown) &&
            const DeepCollectionEquality()
                .equals(other._recentInsights, _recentInsights) &&
            const DeepCollectionEquality()
                .equals(other._trendingEntities, _trendingEntities) &&
            const DeepCollectionEquality()
                .equals(other._recentActivities, _recentActivities) &&
            const DeepCollectionEquality()
                .equals(other._connectorStatuses, _connectorStatuses) &&
            (identical(other.lastUpdated, lastUpdated) ||
                other.lastUpdated == lastUpdated));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      todayStats,
      entityBreakdown,
      const DeepCollectionEquality().hash(_recentInsights),
      const DeepCollectionEquality().hash(_trendingEntities),
      const DeepCollectionEquality().hash(_recentActivities),
      const DeepCollectionEquality().hash(_connectorStatuses),
      lastUpdated);

  /// Create a copy of DataInsightsOverview
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DataInsightsOverviewImplCopyWith<_$DataInsightsOverviewImpl>
      get copyWith =>
          __$$DataInsightsOverviewImplCopyWithImpl<_$DataInsightsOverviewImpl>(
              this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DataInsightsOverviewImplToJson(
      this,
    );
  }
}

abstract class _DataInsightsOverview implements DataInsightsOverview {
  const factory _DataInsightsOverview(
      {required final TodayStats todayStats,
      required final EntityBreakdown entityBreakdown,
      final List<AIInsight> recentInsights,
      final List<TrendingEntity> trendingEntities,
      final List<TimelineItem> recentActivities,
      final List<ConnectorStatus> connectorStatuses,
      final DateTime? lastUpdated}) = _$DataInsightsOverviewImpl;

  factory _DataInsightsOverview.fromJson(Map<String, dynamic> json) =
      _$DataInsightsOverviewImpl.fromJson;

  @override
  TodayStats get todayStats;
  @override
  EntityBreakdown get entityBreakdown;
  @override
  List<AIInsight> get recentInsights;
  @override
  List<TrendingEntity> get trendingEntities;
  @override
  List<TimelineItem> get recentActivities;
  @override
  List<ConnectorStatus> get connectorStatuses;
  @override
  DateTime? get lastUpdated;

  /// Create a copy of DataInsightsOverview
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DataInsightsOverviewImplCopyWith<_$DataInsightsOverviewImpl>
      get copyWith => throw _privateConstructorUsedError;
}

FilterOptions _$FilterOptionsFromJson(Map<String, dynamic> json) {
  return _FilterOptions.fromJson(json);
}

/// @nodoc
mixin _$FilterOptions {
  List<String> get entityTypes => throw _privateConstructorUsedError;
  List<String> get connectorIds => throw _privateConstructorUsedError;
  DateTime? get startDate => throw _privateConstructorUsedError;
  DateTime? get endDate => throw _privateConstructorUsedError;
  String? get searchQuery => throw _privateConstructorUsedError;

  /// Serializes this FilterOptions to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of FilterOptions
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $FilterOptionsCopyWith<FilterOptions> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $FilterOptionsCopyWith<$Res> {
  factory $FilterOptionsCopyWith(
          FilterOptions value, $Res Function(FilterOptions) then) =
      _$FilterOptionsCopyWithImpl<$Res, FilterOptions>;
  @useResult
  $Res call(
      {List<String> entityTypes,
      List<String> connectorIds,
      DateTime? startDate,
      DateTime? endDate,
      String? searchQuery});
}

/// @nodoc
class _$FilterOptionsCopyWithImpl<$Res, $Val extends FilterOptions>
    implements $FilterOptionsCopyWith<$Res> {
  _$FilterOptionsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of FilterOptions
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? entityTypes = null,
    Object? connectorIds = null,
    Object? startDate = freezed,
    Object? endDate = freezed,
    Object? searchQuery = freezed,
  }) {
    return _then(_value.copyWith(
      entityTypes: null == entityTypes
          ? _value.entityTypes
          : entityTypes // ignore: cast_nullable_to_non_nullable
              as List<String>,
      connectorIds: null == connectorIds
          ? _value.connectorIds
          : connectorIds // ignore: cast_nullable_to_non_nullable
              as List<String>,
      startDate: freezed == startDate
          ? _value.startDate
          : startDate // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      endDate: freezed == endDate
          ? _value.endDate
          : endDate // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      searchQuery: freezed == searchQuery
          ? _value.searchQuery
          : searchQuery // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$FilterOptionsImplCopyWith<$Res>
    implements $FilterOptionsCopyWith<$Res> {
  factory _$$FilterOptionsImplCopyWith(
          _$FilterOptionsImpl value, $Res Function(_$FilterOptionsImpl) then) =
      __$$FilterOptionsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {List<String> entityTypes,
      List<String> connectorIds,
      DateTime? startDate,
      DateTime? endDate,
      String? searchQuery});
}

/// @nodoc
class __$$FilterOptionsImplCopyWithImpl<$Res>
    extends _$FilterOptionsCopyWithImpl<$Res, _$FilterOptionsImpl>
    implements _$$FilterOptionsImplCopyWith<$Res> {
  __$$FilterOptionsImplCopyWithImpl(
      _$FilterOptionsImpl _value, $Res Function(_$FilterOptionsImpl) _then)
      : super(_value, _then);

  /// Create a copy of FilterOptions
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? entityTypes = null,
    Object? connectorIds = null,
    Object? startDate = freezed,
    Object? endDate = freezed,
    Object? searchQuery = freezed,
  }) {
    return _then(_$FilterOptionsImpl(
      entityTypes: null == entityTypes
          ? _value._entityTypes
          : entityTypes // ignore: cast_nullable_to_non_nullable
              as List<String>,
      connectorIds: null == connectorIds
          ? _value._connectorIds
          : connectorIds // ignore: cast_nullable_to_non_nullable
              as List<String>,
      startDate: freezed == startDate
          ? _value.startDate
          : startDate // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      endDate: freezed == endDate
          ? _value.endDate
          : endDate // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      searchQuery: freezed == searchQuery
          ? _value.searchQuery
          : searchQuery // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$FilterOptionsImpl implements _FilterOptions {
  const _$FilterOptionsImpl(
      {final List<String> entityTypes = const [],
      final List<String> connectorIds = const [],
      this.startDate,
      this.endDate,
      this.searchQuery})
      : _entityTypes = entityTypes,
        _connectorIds = connectorIds;

  factory _$FilterOptionsImpl.fromJson(Map<String, dynamic> json) =>
      _$$FilterOptionsImplFromJson(json);

  final List<String> _entityTypes;
  @override
  @JsonKey()
  List<String> get entityTypes {
    if (_entityTypes is EqualUnmodifiableListView) return _entityTypes;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_entityTypes);
  }

  final List<String> _connectorIds;
  @override
  @JsonKey()
  List<String> get connectorIds {
    if (_connectorIds is EqualUnmodifiableListView) return _connectorIds;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_connectorIds);
  }

  @override
  final DateTime? startDate;
  @override
  final DateTime? endDate;
  @override
  final String? searchQuery;

  @override
  String toString() {
    return 'FilterOptions(entityTypes: $entityTypes, connectorIds: $connectorIds, startDate: $startDate, endDate: $endDate, searchQuery: $searchQuery)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$FilterOptionsImpl &&
            const DeepCollectionEquality()
                .equals(other._entityTypes, _entityTypes) &&
            const DeepCollectionEquality()
                .equals(other._connectorIds, _connectorIds) &&
            (identical(other.startDate, startDate) ||
                other.startDate == startDate) &&
            (identical(other.endDate, endDate) || other.endDate == endDate) &&
            (identical(other.searchQuery, searchQuery) ||
                other.searchQuery == searchQuery));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(_entityTypes),
      const DeepCollectionEquality().hash(_connectorIds),
      startDate,
      endDate,
      searchQuery);

  /// Create a copy of FilterOptions
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$FilterOptionsImplCopyWith<_$FilterOptionsImpl> get copyWith =>
      __$$FilterOptionsImplCopyWithImpl<_$FilterOptionsImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$FilterOptionsImplToJson(
      this,
    );
  }
}

abstract class _FilterOptions implements FilterOptions {
  const factory _FilterOptions(
      {final List<String> entityTypes,
      final List<String> connectorIds,
      final DateTime? startDate,
      final DateTime? endDate,
      final String? searchQuery}) = _$FilterOptionsImpl;

  factory _FilterOptions.fromJson(Map<String, dynamic> json) =
      _$FilterOptionsImpl.fromJson;

  @override
  List<String> get entityTypes;
  @override
  List<String> get connectorIds;
  @override
  DateTime? get startDate;
  @override
  DateTime? get endDate;
  @override
  String? get searchQuery;

  /// Create a copy of FilterOptions
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$FilterOptionsImplCopyWith<_$FilterOptionsImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
