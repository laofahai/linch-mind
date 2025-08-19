// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'ai_insight_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

AIInsightCard _$AIInsightCardFromJson(Map<String, dynamic> json) {
  return _AIInsightCard.fromJson(json);
}

/// @nodoc
mixin _$AIInsightCard {
  String get id => throw _privateConstructorUsedError;
  String get type =>
      throw _privateConstructorUsedError; // 'discovery', 'suggestion', 'pattern', 'alert'
  String get title => throw _privateConstructorUsedError;
  String get message => throw _privateConstructorUsedError;
  String get iconName => throw _privateConstructorUsedError;
  DateTime get timestamp => throw _privateConstructorUsedError;
  double get confidence => throw _privateConstructorUsedError;
  List<String> get entities => throw _privateConstructorUsedError;
  List<AIInsightAction> get actions => throw _privateConstructorUsedError;
  bool get isDismissed => throw _privateConstructorUsedError;
  bool get isRead => throw _privateConstructorUsedError;

  /// Serializes this AIInsightCard to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of AIInsightCard
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $AIInsightCardCopyWith<AIInsightCard> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AIInsightCardCopyWith<$Res> {
  factory $AIInsightCardCopyWith(
          AIInsightCard value, $Res Function(AIInsightCard) then) =
      _$AIInsightCardCopyWithImpl<$Res, AIInsightCard>;
  @useResult
  $Res call(
      {String id,
      String type,
      String title,
      String message,
      String iconName,
      DateTime timestamp,
      double confidence,
      List<String> entities,
      List<AIInsightAction> actions,
      bool isDismissed,
      bool isRead});
}

/// @nodoc
class _$AIInsightCardCopyWithImpl<$Res, $Val extends AIInsightCard>
    implements $AIInsightCardCopyWith<$Res> {
  _$AIInsightCardCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of AIInsightCard
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? type = null,
    Object? title = null,
    Object? message = null,
    Object? iconName = null,
    Object? timestamp = null,
    Object? confidence = null,
    Object? entities = null,
    Object? actions = null,
    Object? isDismissed = null,
    Object? isRead = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
      iconName: null == iconName
          ? _value.iconName
          : iconName // ignore: cast_nullable_to_non_nullable
              as String,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      confidence: null == confidence
          ? _value.confidence
          : confidence // ignore: cast_nullable_to_non_nullable
              as double,
      entities: null == entities
          ? _value.entities
          : entities // ignore: cast_nullable_to_non_nullable
              as List<String>,
      actions: null == actions
          ? _value.actions
          : actions // ignore: cast_nullable_to_non_nullable
              as List<AIInsightAction>,
      isDismissed: null == isDismissed
          ? _value.isDismissed
          : isDismissed // ignore: cast_nullable_to_non_nullable
              as bool,
      isRead: null == isRead
          ? _value.isRead
          : isRead // ignore: cast_nullable_to_non_nullable
              as bool,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$AIInsightCardImplCopyWith<$Res>
    implements $AIInsightCardCopyWith<$Res> {
  factory _$$AIInsightCardImplCopyWith(
          _$AIInsightCardImpl value, $Res Function(_$AIInsightCardImpl) then) =
      __$$AIInsightCardImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String type,
      String title,
      String message,
      String iconName,
      DateTime timestamp,
      double confidence,
      List<String> entities,
      List<AIInsightAction> actions,
      bool isDismissed,
      bool isRead});
}

/// @nodoc
class __$$AIInsightCardImplCopyWithImpl<$Res>
    extends _$AIInsightCardCopyWithImpl<$Res, _$AIInsightCardImpl>
    implements _$$AIInsightCardImplCopyWith<$Res> {
  __$$AIInsightCardImplCopyWithImpl(
      _$AIInsightCardImpl _value, $Res Function(_$AIInsightCardImpl) _then)
      : super(_value, _then);

  /// Create a copy of AIInsightCard
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? type = null,
    Object? title = null,
    Object? message = null,
    Object? iconName = null,
    Object? timestamp = null,
    Object? confidence = null,
    Object? entities = null,
    Object? actions = null,
    Object? isDismissed = null,
    Object? isRead = null,
  }) {
    return _then(_$AIInsightCardImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
      iconName: null == iconName
          ? _value.iconName
          : iconName // ignore: cast_nullable_to_non_nullable
              as String,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      confidence: null == confidence
          ? _value.confidence
          : confidence // ignore: cast_nullable_to_non_nullable
              as double,
      entities: null == entities
          ? _value._entities
          : entities // ignore: cast_nullable_to_non_nullable
              as List<String>,
      actions: null == actions
          ? _value._actions
          : actions // ignore: cast_nullable_to_non_nullable
              as List<AIInsightAction>,
      isDismissed: null == isDismissed
          ? _value.isDismissed
          : isDismissed // ignore: cast_nullable_to_non_nullable
              as bool,
      isRead: null == isRead
          ? _value.isRead
          : isRead // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$AIInsightCardImpl implements _AIInsightCard {
  const _$AIInsightCardImpl(
      {required this.id,
      required this.type,
      required this.title,
      required this.message,
      required this.iconName,
      required this.timestamp,
      this.confidence = 0.8,
      final List<String> entities = const [],
      final List<AIInsightAction> actions = const [],
      this.isDismissed = false,
      this.isRead = false})
      : _entities = entities,
        _actions = actions;

  factory _$AIInsightCardImpl.fromJson(Map<String, dynamic> json) =>
      _$$AIInsightCardImplFromJson(json);

  @override
  final String id;
  @override
  final String type;
// 'discovery', 'suggestion', 'pattern', 'alert'
  @override
  final String title;
  @override
  final String message;
  @override
  final String iconName;
  @override
  final DateTime timestamp;
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

  final List<AIInsightAction> _actions;
  @override
  @JsonKey()
  List<AIInsightAction> get actions {
    if (_actions is EqualUnmodifiableListView) return _actions;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_actions);
  }

  @override
  @JsonKey()
  final bool isDismissed;
  @override
  @JsonKey()
  final bool isRead;

  @override
  String toString() {
    return 'AIInsightCard(id: $id, type: $type, title: $title, message: $message, iconName: $iconName, timestamp: $timestamp, confidence: $confidence, entities: $entities, actions: $actions, isDismissed: $isDismissed, isRead: $isRead)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$AIInsightCardImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.type, type) || other.type == type) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.message, message) || other.message == message) &&
            (identical(other.iconName, iconName) ||
                other.iconName == iconName) &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp) &&
            (identical(other.confidence, confidence) ||
                other.confidence == confidence) &&
            const DeepCollectionEquality().equals(other._entities, _entities) &&
            const DeepCollectionEquality().equals(other._actions, _actions) &&
            (identical(other.isDismissed, isDismissed) ||
                other.isDismissed == isDismissed) &&
            (identical(other.isRead, isRead) || other.isRead == isRead));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      type,
      title,
      message,
      iconName,
      timestamp,
      confidence,
      const DeepCollectionEquality().hash(_entities),
      const DeepCollectionEquality().hash(_actions),
      isDismissed,
      isRead);

  /// Create a copy of AIInsightCard
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$AIInsightCardImplCopyWith<_$AIInsightCardImpl> get copyWith =>
      __$$AIInsightCardImplCopyWithImpl<_$AIInsightCardImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$AIInsightCardImplToJson(
      this,
    );
  }
}

abstract class _AIInsightCard implements AIInsightCard {
  const factory _AIInsightCard(
      {required final String id,
      required final String type,
      required final String title,
      required final String message,
      required final String iconName,
      required final DateTime timestamp,
      final double confidence,
      final List<String> entities,
      final List<AIInsightAction> actions,
      final bool isDismissed,
      final bool isRead}) = _$AIInsightCardImpl;

  factory _AIInsightCard.fromJson(Map<String, dynamic> json) =
      _$AIInsightCardImpl.fromJson;

  @override
  String get id;
  @override
  String get type; // 'discovery', 'suggestion', 'pattern', 'alert'
  @override
  String get title;
  @override
  String get message;
  @override
  String get iconName;
  @override
  DateTime get timestamp;
  @override
  double get confidence;
  @override
  List<String> get entities;
  @override
  List<AIInsightAction> get actions;
  @override
  bool get isDismissed;
  @override
  bool get isRead;

  /// Create a copy of AIInsightCard
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$AIInsightCardImplCopyWith<_$AIInsightCardImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

AIInsightAction _$AIInsightActionFromJson(Map<String, dynamic> json) {
  return _AIInsightAction.fromJson(json);
}

/// @nodoc
mixin _$AIInsightAction {
  String get id => throw _privateConstructorUsedError;
  String get label => throw _privateConstructorUsedError;
  String get type =>
      throw _privateConstructorUsedError; // 'primary', 'secondary', 'dismiss'
  String? get route => throw _privateConstructorUsedError;
  Map<String, dynamic>? get data => throw _privateConstructorUsedError;

  /// Serializes this AIInsightAction to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of AIInsightAction
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $AIInsightActionCopyWith<AIInsightAction> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AIInsightActionCopyWith<$Res> {
  factory $AIInsightActionCopyWith(
          AIInsightAction value, $Res Function(AIInsightAction) then) =
      _$AIInsightActionCopyWithImpl<$Res, AIInsightAction>;
  @useResult
  $Res call(
      {String id,
      String label,
      String type,
      String? route,
      Map<String, dynamic>? data});
}

/// @nodoc
class _$AIInsightActionCopyWithImpl<$Res, $Val extends AIInsightAction>
    implements $AIInsightActionCopyWith<$Res> {
  _$AIInsightActionCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of AIInsightAction
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? label = null,
    Object? type = null,
    Object? route = freezed,
    Object? data = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      label: null == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      route: freezed == route
          ? _value.route
          : route // ignore: cast_nullable_to_non_nullable
              as String?,
      data: freezed == data
          ? _value.data
          : data // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$AIInsightActionImplCopyWith<$Res>
    implements $AIInsightActionCopyWith<$Res> {
  factory _$$AIInsightActionImplCopyWith(_$AIInsightActionImpl value,
          $Res Function(_$AIInsightActionImpl) then) =
      __$$AIInsightActionImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String label,
      String type,
      String? route,
      Map<String, dynamic>? data});
}

/// @nodoc
class __$$AIInsightActionImplCopyWithImpl<$Res>
    extends _$AIInsightActionCopyWithImpl<$Res, _$AIInsightActionImpl>
    implements _$$AIInsightActionImplCopyWith<$Res> {
  __$$AIInsightActionImplCopyWithImpl(
      _$AIInsightActionImpl _value, $Res Function(_$AIInsightActionImpl) _then)
      : super(_value, _then);

  /// Create a copy of AIInsightAction
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? label = null,
    Object? type = null,
    Object? route = freezed,
    Object? data = freezed,
  }) {
    return _then(_$AIInsightActionImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      label: null == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      route: freezed == route
          ? _value.route
          : route // ignore: cast_nullable_to_non_nullable
              as String?,
      data: freezed == data
          ? _value._data
          : data // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$AIInsightActionImpl implements _AIInsightAction {
  const _$AIInsightActionImpl(
      {required this.id,
      required this.label,
      required this.type,
      this.route,
      final Map<String, dynamic>? data})
      : _data = data;

  factory _$AIInsightActionImpl.fromJson(Map<String, dynamic> json) =>
      _$$AIInsightActionImplFromJson(json);

  @override
  final String id;
  @override
  final String label;
  @override
  final String type;
// 'primary', 'secondary', 'dismiss'
  @override
  final String? route;
  final Map<String, dynamic>? _data;
  @override
  Map<String, dynamic>? get data {
    final value = _data;
    if (value == null) return null;
    if (_data is EqualUnmodifiableMapView) return _data;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'AIInsightAction(id: $id, label: $label, type: $type, route: $route, data: $data)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$AIInsightActionImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.label, label) || other.label == label) &&
            (identical(other.type, type) || other.type == type) &&
            (identical(other.route, route) || other.route == route) &&
            const DeepCollectionEquality().equals(other._data, _data));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, id, label, type, route,
      const DeepCollectionEquality().hash(_data));

  /// Create a copy of AIInsightAction
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$AIInsightActionImplCopyWith<_$AIInsightActionImpl> get copyWith =>
      __$$AIInsightActionImplCopyWithImpl<_$AIInsightActionImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$AIInsightActionImplToJson(
      this,
    );
  }
}

abstract class _AIInsightAction implements AIInsightAction {
  const factory _AIInsightAction(
      {required final String id,
      required final String label,
      required final String type,
      final String? route,
      final Map<String, dynamic>? data}) = _$AIInsightActionImpl;

  factory _AIInsightAction.fromJson(Map<String, dynamic> json) =
      _$AIInsightActionImpl.fromJson;

  @override
  String get id;
  @override
  String get label;
  @override
  String get type; // 'primary', 'secondary', 'dismiss'
  @override
  String? get route;
  @override
  Map<String, dynamic>? get data;

  /// Create a copy of AIInsightAction
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$AIInsightActionImplCopyWith<_$AIInsightActionImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

TodayOverview _$TodayOverviewFromJson(Map<String, dynamic> json) {
  return _TodayOverview.fromJson(json);
}

/// @nodoc
mixin _$TodayOverview {
  int get newDataPoints => throw _privateConstructorUsedError;
  int get aiProcessedItems => throw _privateConstructorUsedError;
  int get insightsGenerated => throw _privateConstructorUsedError;
  int get activeConnectors => throw _privateConstructorUsedError;
  DateTime get lastUpdate => throw _privateConstructorUsedError;

  /// Serializes this TodayOverview to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of TodayOverview
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $TodayOverviewCopyWith<TodayOverview> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $TodayOverviewCopyWith<$Res> {
  factory $TodayOverviewCopyWith(
          TodayOverview value, $Res Function(TodayOverview) then) =
      _$TodayOverviewCopyWithImpl<$Res, TodayOverview>;
  @useResult
  $Res call(
      {int newDataPoints,
      int aiProcessedItems,
      int insightsGenerated,
      int activeConnectors,
      DateTime lastUpdate});
}

/// @nodoc
class _$TodayOverviewCopyWithImpl<$Res, $Val extends TodayOverview>
    implements $TodayOverviewCopyWith<$Res> {
  _$TodayOverviewCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of TodayOverview
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? newDataPoints = null,
    Object? aiProcessedItems = null,
    Object? insightsGenerated = null,
    Object? activeConnectors = null,
    Object? lastUpdate = null,
  }) {
    return _then(_value.copyWith(
      newDataPoints: null == newDataPoints
          ? _value.newDataPoints
          : newDataPoints // ignore: cast_nullable_to_non_nullable
              as int,
      aiProcessedItems: null == aiProcessedItems
          ? _value.aiProcessedItems
          : aiProcessedItems // ignore: cast_nullable_to_non_nullable
              as int,
      insightsGenerated: null == insightsGenerated
          ? _value.insightsGenerated
          : insightsGenerated // ignore: cast_nullable_to_non_nullable
              as int,
      activeConnectors: null == activeConnectors
          ? _value.activeConnectors
          : activeConnectors // ignore: cast_nullable_to_non_nullable
              as int,
      lastUpdate: null == lastUpdate
          ? _value.lastUpdate
          : lastUpdate // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$TodayOverviewImplCopyWith<$Res>
    implements $TodayOverviewCopyWith<$Res> {
  factory _$$TodayOverviewImplCopyWith(
          _$TodayOverviewImpl value, $Res Function(_$TodayOverviewImpl) then) =
      __$$TodayOverviewImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int newDataPoints,
      int aiProcessedItems,
      int insightsGenerated,
      int activeConnectors,
      DateTime lastUpdate});
}

/// @nodoc
class __$$TodayOverviewImplCopyWithImpl<$Res>
    extends _$TodayOverviewCopyWithImpl<$Res, _$TodayOverviewImpl>
    implements _$$TodayOverviewImplCopyWith<$Res> {
  __$$TodayOverviewImplCopyWithImpl(
      _$TodayOverviewImpl _value, $Res Function(_$TodayOverviewImpl) _then)
      : super(_value, _then);

  /// Create a copy of TodayOverview
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? newDataPoints = null,
    Object? aiProcessedItems = null,
    Object? insightsGenerated = null,
    Object? activeConnectors = null,
    Object? lastUpdate = null,
  }) {
    return _then(_$TodayOverviewImpl(
      newDataPoints: null == newDataPoints
          ? _value.newDataPoints
          : newDataPoints // ignore: cast_nullable_to_non_nullable
              as int,
      aiProcessedItems: null == aiProcessedItems
          ? _value.aiProcessedItems
          : aiProcessedItems // ignore: cast_nullable_to_non_nullable
              as int,
      insightsGenerated: null == insightsGenerated
          ? _value.insightsGenerated
          : insightsGenerated // ignore: cast_nullable_to_non_nullable
              as int,
      activeConnectors: null == activeConnectors
          ? _value.activeConnectors
          : activeConnectors // ignore: cast_nullable_to_non_nullable
              as int,
      lastUpdate: null == lastUpdate
          ? _value.lastUpdate
          : lastUpdate // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$TodayOverviewImpl implements _TodayOverview {
  const _$TodayOverviewImpl(
      {required this.newDataPoints,
      required this.aiProcessedItems,
      required this.insightsGenerated,
      required this.activeConnectors,
      required this.lastUpdate});

  factory _$TodayOverviewImpl.fromJson(Map<String, dynamic> json) =>
      _$$TodayOverviewImplFromJson(json);

  @override
  final int newDataPoints;
  @override
  final int aiProcessedItems;
  @override
  final int insightsGenerated;
  @override
  final int activeConnectors;
  @override
  final DateTime lastUpdate;

  @override
  String toString() {
    return 'TodayOverview(newDataPoints: $newDataPoints, aiProcessedItems: $aiProcessedItems, insightsGenerated: $insightsGenerated, activeConnectors: $activeConnectors, lastUpdate: $lastUpdate)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$TodayOverviewImpl &&
            (identical(other.newDataPoints, newDataPoints) ||
                other.newDataPoints == newDataPoints) &&
            (identical(other.aiProcessedItems, aiProcessedItems) ||
                other.aiProcessedItems == aiProcessedItems) &&
            (identical(other.insightsGenerated, insightsGenerated) ||
                other.insightsGenerated == insightsGenerated) &&
            (identical(other.activeConnectors, activeConnectors) ||
                other.activeConnectors == activeConnectors) &&
            (identical(other.lastUpdate, lastUpdate) ||
                other.lastUpdate == lastUpdate));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, newDataPoints, aiProcessedItems,
      insightsGenerated, activeConnectors, lastUpdate);

  /// Create a copy of TodayOverview
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$TodayOverviewImplCopyWith<_$TodayOverviewImpl> get copyWith =>
      __$$TodayOverviewImplCopyWithImpl<_$TodayOverviewImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$TodayOverviewImplToJson(
      this,
    );
  }
}

abstract class _TodayOverview implements TodayOverview {
  const factory _TodayOverview(
      {required final int newDataPoints,
      required final int aiProcessedItems,
      required final int insightsGenerated,
      required final int activeConnectors,
      required final DateTime lastUpdate}) = _$TodayOverviewImpl;

  factory _TodayOverview.fromJson(Map<String, dynamic> json) =
      _$TodayOverviewImpl.fromJson;

  @override
  int get newDataPoints;
  @override
  int get aiProcessedItems;
  @override
  int get insightsGenerated;
  @override
  int get activeConnectors;
  @override
  DateTime get lastUpdate;

  /// Create a copy of TodayOverview
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$TodayOverviewImplCopyWith<_$TodayOverviewImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

QuickAccessItem _$QuickAccessItemFromJson(Map<String, dynamic> json) {
  return _QuickAccessItem.fromJson(json);
}

/// @nodoc
mixin _$QuickAccessItem {
  String get id => throw _privateConstructorUsedError;
  String get title => throw _privateConstructorUsedError;
  String get subtitle => throw _privateConstructorUsedError;
  String get iconName => throw _privateConstructorUsedError;
  String get type =>
      throw _privateConstructorUsedError; // 'url', 'file', 'contact', 'note'
  DateTime get lastAccessed => throw _privateConstructorUsedError;
  String? get data => throw _privateConstructorUsedError;

  /// Serializes this QuickAccessItem to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of QuickAccessItem
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $QuickAccessItemCopyWith<QuickAccessItem> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $QuickAccessItemCopyWith<$Res> {
  factory $QuickAccessItemCopyWith(
          QuickAccessItem value, $Res Function(QuickAccessItem) then) =
      _$QuickAccessItemCopyWithImpl<$Res, QuickAccessItem>;
  @useResult
  $Res call(
      {String id,
      String title,
      String subtitle,
      String iconName,
      String type,
      DateTime lastAccessed,
      String? data});
}

/// @nodoc
class _$QuickAccessItemCopyWithImpl<$Res, $Val extends QuickAccessItem>
    implements $QuickAccessItemCopyWith<$Res> {
  _$QuickAccessItemCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of QuickAccessItem
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? title = null,
    Object? subtitle = null,
    Object? iconName = null,
    Object? type = null,
    Object? lastAccessed = null,
    Object? data = freezed,
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
      subtitle: null == subtitle
          ? _value.subtitle
          : subtitle // ignore: cast_nullable_to_non_nullable
              as String,
      iconName: null == iconName
          ? _value.iconName
          : iconName // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      lastAccessed: null == lastAccessed
          ? _value.lastAccessed
          : lastAccessed // ignore: cast_nullable_to_non_nullable
              as DateTime,
      data: freezed == data
          ? _value.data
          : data // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$QuickAccessItemImplCopyWith<$Res>
    implements $QuickAccessItemCopyWith<$Res> {
  factory _$$QuickAccessItemImplCopyWith(_$QuickAccessItemImpl value,
          $Res Function(_$QuickAccessItemImpl) then) =
      __$$QuickAccessItemImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String title,
      String subtitle,
      String iconName,
      String type,
      DateTime lastAccessed,
      String? data});
}

/// @nodoc
class __$$QuickAccessItemImplCopyWithImpl<$Res>
    extends _$QuickAccessItemCopyWithImpl<$Res, _$QuickAccessItemImpl>
    implements _$$QuickAccessItemImplCopyWith<$Res> {
  __$$QuickAccessItemImplCopyWithImpl(
      _$QuickAccessItemImpl _value, $Res Function(_$QuickAccessItemImpl) _then)
      : super(_value, _then);

  /// Create a copy of QuickAccessItem
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? title = null,
    Object? subtitle = null,
    Object? iconName = null,
    Object? type = null,
    Object? lastAccessed = null,
    Object? data = freezed,
  }) {
    return _then(_$QuickAccessItemImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      subtitle: null == subtitle
          ? _value.subtitle
          : subtitle // ignore: cast_nullable_to_non_nullable
              as String,
      iconName: null == iconName
          ? _value.iconName
          : iconName // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      lastAccessed: null == lastAccessed
          ? _value.lastAccessed
          : lastAccessed // ignore: cast_nullable_to_non_nullable
              as DateTime,
      data: freezed == data
          ? _value.data
          : data // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$QuickAccessItemImpl implements _QuickAccessItem {
  const _$QuickAccessItemImpl(
      {required this.id,
      required this.title,
      required this.subtitle,
      required this.iconName,
      required this.type,
      required this.lastAccessed,
      this.data});

  factory _$QuickAccessItemImpl.fromJson(Map<String, dynamic> json) =>
      _$$QuickAccessItemImplFromJson(json);

  @override
  final String id;
  @override
  final String title;
  @override
  final String subtitle;
  @override
  final String iconName;
  @override
  final String type;
// 'url', 'file', 'contact', 'note'
  @override
  final DateTime lastAccessed;
  @override
  final String? data;

  @override
  String toString() {
    return 'QuickAccessItem(id: $id, title: $title, subtitle: $subtitle, iconName: $iconName, type: $type, lastAccessed: $lastAccessed, data: $data)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$QuickAccessItemImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.subtitle, subtitle) ||
                other.subtitle == subtitle) &&
            (identical(other.iconName, iconName) ||
                other.iconName == iconName) &&
            (identical(other.type, type) || other.type == type) &&
            (identical(other.lastAccessed, lastAccessed) ||
                other.lastAccessed == lastAccessed) &&
            (identical(other.data, data) || other.data == data));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType, id, title, subtitle, iconName, type, lastAccessed, data);

  /// Create a copy of QuickAccessItem
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$QuickAccessItemImplCopyWith<_$QuickAccessItemImpl> get copyWith =>
      __$$QuickAccessItemImplCopyWithImpl<_$QuickAccessItemImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$QuickAccessItemImplToJson(
      this,
    );
  }
}

abstract class _QuickAccessItem implements QuickAccessItem {
  const factory _QuickAccessItem(
      {required final String id,
      required final String title,
      required final String subtitle,
      required final String iconName,
      required final String type,
      required final DateTime lastAccessed,
      final String? data}) = _$QuickAccessItemImpl;

  factory _QuickAccessItem.fromJson(Map<String, dynamic> json) =
      _$QuickAccessItemImpl.fromJson;

  @override
  String get id;
  @override
  String get title;
  @override
  String get subtitle;
  @override
  String get iconName;
  @override
  String get type; // 'url', 'file', 'contact', 'note'
  @override
  DateTime get lastAccessed;
  @override
  String? get data;

  /// Create a copy of QuickAccessItem
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$QuickAccessItemImplCopyWith<_$QuickAccessItemImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
