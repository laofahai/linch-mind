// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'ai_insights_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

AIInsight _$AIInsightFromJson(Map<String, dynamic> json) {
  return _AIInsight.fromJson(json);
}

/// @nodoc
mixin _$AIInsight {
  String get id => throw _privateConstructorUsedError;
  String get title => throw _privateConstructorUsedError;
  String get description => throw _privateConstructorUsedError;
  InsightTimeframe get timeframe => throw _privateConstructorUsedError;
  InsightType get type => throw _privateConstructorUsedError;
  double get confidence => throw _privateConstructorUsedError;
  DateTime get timestamp => throw _privateConstructorUsedError;
  List<InsightAction> get actions => throw _privateConstructorUsedError;
  Map<String, dynamic>? get metadata => throw _privateConstructorUsedError;
  String? get iconName => throw _privateConstructorUsedError;
  bool get isImportant => throw _privateConstructorUsedError;
  bool get isDismissed => throw _privateConstructorUsedError;

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
      {String id,
      String title,
      String description,
      InsightTimeframe timeframe,
      InsightType type,
      double confidence,
      DateTime timestamp,
      List<InsightAction> actions,
      Map<String, dynamic>? metadata,
      String? iconName,
      bool isImportant,
      bool isDismissed});
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
    Object? id = null,
    Object? title = null,
    Object? description = null,
    Object? timeframe = null,
    Object? type = null,
    Object? confidence = null,
    Object? timestamp = null,
    Object? actions = null,
    Object? metadata = freezed,
    Object? iconName = freezed,
    Object? isImportant = null,
    Object? isDismissed = null,
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
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      timeframe: null == timeframe
          ? _value.timeframe
          : timeframe // ignore: cast_nullable_to_non_nullable
              as InsightTimeframe,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as InsightType,
      confidence: null == confidence
          ? _value.confidence
          : confidence // ignore: cast_nullable_to_non_nullable
              as double,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      actions: null == actions
          ? _value.actions
          : actions // ignore: cast_nullable_to_non_nullable
              as List<InsightAction>,
      metadata: freezed == metadata
          ? _value.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      iconName: freezed == iconName
          ? _value.iconName
          : iconName // ignore: cast_nullable_to_non_nullable
              as String?,
      isImportant: null == isImportant
          ? _value.isImportant
          : isImportant // ignore: cast_nullable_to_non_nullable
              as bool,
      isDismissed: null == isDismissed
          ? _value.isDismissed
          : isDismissed // ignore: cast_nullable_to_non_nullable
              as bool,
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
      {String id,
      String title,
      String description,
      InsightTimeframe timeframe,
      InsightType type,
      double confidence,
      DateTime timestamp,
      List<InsightAction> actions,
      Map<String, dynamic>? metadata,
      String? iconName,
      bool isImportant,
      bool isDismissed});
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
    Object? id = null,
    Object? title = null,
    Object? description = null,
    Object? timeframe = null,
    Object? type = null,
    Object? confidence = null,
    Object? timestamp = null,
    Object? actions = null,
    Object? metadata = freezed,
    Object? iconName = freezed,
    Object? isImportant = null,
    Object? isDismissed = null,
  }) {
    return _then(_$AIInsightImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      timeframe: null == timeframe
          ? _value.timeframe
          : timeframe // ignore: cast_nullable_to_non_nullable
              as InsightTimeframe,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as InsightType,
      confidence: null == confidence
          ? _value.confidence
          : confidence // ignore: cast_nullable_to_non_nullable
              as double,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      actions: null == actions
          ? _value._actions
          : actions // ignore: cast_nullable_to_non_nullable
              as List<InsightAction>,
      metadata: freezed == metadata
          ? _value._metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      iconName: freezed == iconName
          ? _value.iconName
          : iconName // ignore: cast_nullable_to_non_nullable
              as String?,
      isImportant: null == isImportant
          ? _value.isImportant
          : isImportant // ignore: cast_nullable_to_non_nullable
              as bool,
      isDismissed: null == isDismissed
          ? _value.isDismissed
          : isDismissed // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$AIInsightImpl implements _AIInsight {
  const _$AIInsightImpl(
      {required this.id,
      required this.title,
      required this.description,
      required this.timeframe,
      required this.type,
      required this.confidence,
      required this.timestamp,
      final List<InsightAction> actions = const [],
      final Map<String, dynamic>? metadata,
      this.iconName,
      this.isImportant = false,
      this.isDismissed = false})
      : _actions = actions,
        _metadata = metadata;

  factory _$AIInsightImpl.fromJson(Map<String, dynamic> json) =>
      _$$AIInsightImplFromJson(json);

  @override
  final String id;
  @override
  final String title;
  @override
  final String description;
  @override
  final InsightTimeframe timeframe;
  @override
  final InsightType type;
  @override
  final double confidence;
  @override
  final DateTime timestamp;
  final List<InsightAction> _actions;
  @override
  @JsonKey()
  List<InsightAction> get actions {
    if (_actions is EqualUnmodifiableListView) return _actions;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_actions);
  }

  final Map<String, dynamic>? _metadata;
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
  @JsonKey()
  final bool isImportant;
  @override
  @JsonKey()
  final bool isDismissed;

  @override
  String toString() {
    return 'AIInsight(id: $id, title: $title, description: $description, timeframe: $timeframe, type: $type, confidence: $confidence, timestamp: $timestamp, actions: $actions, metadata: $metadata, iconName: $iconName, isImportant: $isImportant, isDismissed: $isDismissed)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$AIInsightImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.timeframe, timeframe) ||
                other.timeframe == timeframe) &&
            (identical(other.type, type) || other.type == type) &&
            (identical(other.confidence, confidence) ||
                other.confidence == confidence) &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp) &&
            const DeepCollectionEquality().equals(other._actions, _actions) &&
            const DeepCollectionEquality().equals(other._metadata, _metadata) &&
            (identical(other.iconName, iconName) ||
                other.iconName == iconName) &&
            (identical(other.isImportant, isImportant) ||
                other.isImportant == isImportant) &&
            (identical(other.isDismissed, isDismissed) ||
                other.isDismissed == isDismissed));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      title,
      description,
      timeframe,
      type,
      confidence,
      timestamp,
      const DeepCollectionEquality().hash(_actions),
      const DeepCollectionEquality().hash(_metadata),
      iconName,
      isImportant,
      isDismissed);

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
      {required final String id,
      required final String title,
      required final String description,
      required final InsightTimeframe timeframe,
      required final InsightType type,
      required final double confidence,
      required final DateTime timestamp,
      final List<InsightAction> actions,
      final Map<String, dynamic>? metadata,
      final String? iconName,
      final bool isImportant,
      final bool isDismissed}) = _$AIInsightImpl;

  factory _AIInsight.fromJson(Map<String, dynamic> json) =
      _$AIInsightImpl.fromJson;

  @override
  String get id;
  @override
  String get title;
  @override
  String get description;
  @override
  InsightTimeframe get timeframe;
  @override
  InsightType get type;
  @override
  double get confidence;
  @override
  DateTime get timestamp;
  @override
  List<InsightAction> get actions;
  @override
  Map<String, dynamic>? get metadata;
  @override
  String? get iconName;
  @override
  bool get isImportant;
  @override
  bool get isDismissed;

  /// Create a copy of AIInsight
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$AIInsightImplCopyWith<_$AIInsightImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

InsightAction _$InsightActionFromJson(Map<String, dynamic> json) {
  return _InsightAction.fromJson(json);
}

/// @nodoc
mixin _$InsightAction {
  String get id => throw _privateConstructorUsedError;
  String get label => throw _privateConstructorUsedError;
  String get prompt => throw _privateConstructorUsedError; // 要填入聊天框的提示词
  String? get iconName => throw _privateConstructorUsedError;
  bool get isPrimary => throw _privateConstructorUsedError;

  /// Serializes this InsightAction to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of InsightAction
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $InsightActionCopyWith<InsightAction> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $InsightActionCopyWith<$Res> {
  factory $InsightActionCopyWith(
          InsightAction value, $Res Function(InsightAction) then) =
      _$InsightActionCopyWithImpl<$Res, InsightAction>;
  @useResult
  $Res call(
      {String id,
      String label,
      String prompt,
      String? iconName,
      bool isPrimary});
}

/// @nodoc
class _$InsightActionCopyWithImpl<$Res, $Val extends InsightAction>
    implements $InsightActionCopyWith<$Res> {
  _$InsightActionCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of InsightAction
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? label = null,
    Object? prompt = null,
    Object? iconName = freezed,
    Object? isPrimary = null,
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
      prompt: null == prompt
          ? _value.prompt
          : prompt // ignore: cast_nullable_to_non_nullable
              as String,
      iconName: freezed == iconName
          ? _value.iconName
          : iconName // ignore: cast_nullable_to_non_nullable
              as String?,
      isPrimary: null == isPrimary
          ? _value.isPrimary
          : isPrimary // ignore: cast_nullable_to_non_nullable
              as bool,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$InsightActionImplCopyWith<$Res>
    implements $InsightActionCopyWith<$Res> {
  factory _$$InsightActionImplCopyWith(
          _$InsightActionImpl value, $Res Function(_$InsightActionImpl) then) =
      __$$InsightActionImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String label,
      String prompt,
      String? iconName,
      bool isPrimary});
}

/// @nodoc
class __$$InsightActionImplCopyWithImpl<$Res>
    extends _$InsightActionCopyWithImpl<$Res, _$InsightActionImpl>
    implements _$$InsightActionImplCopyWith<$Res> {
  __$$InsightActionImplCopyWithImpl(
      _$InsightActionImpl _value, $Res Function(_$InsightActionImpl) _then)
      : super(_value, _then);

  /// Create a copy of InsightAction
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? label = null,
    Object? prompt = null,
    Object? iconName = freezed,
    Object? isPrimary = null,
  }) {
    return _then(_$InsightActionImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      label: null == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String,
      prompt: null == prompt
          ? _value.prompt
          : prompt // ignore: cast_nullable_to_non_nullable
              as String,
      iconName: freezed == iconName
          ? _value.iconName
          : iconName // ignore: cast_nullable_to_non_nullable
              as String?,
      isPrimary: null == isPrimary
          ? _value.isPrimary
          : isPrimary // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$InsightActionImpl implements _InsightAction {
  const _$InsightActionImpl(
      {required this.id,
      required this.label,
      required this.prompt,
      this.iconName,
      this.isPrimary = false});

  factory _$InsightActionImpl.fromJson(Map<String, dynamic> json) =>
      _$$InsightActionImplFromJson(json);

  @override
  final String id;
  @override
  final String label;
  @override
  final String prompt;
// 要填入聊天框的提示词
  @override
  final String? iconName;
  @override
  @JsonKey()
  final bool isPrimary;

  @override
  String toString() {
    return 'InsightAction(id: $id, label: $label, prompt: $prompt, iconName: $iconName, isPrimary: $isPrimary)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$InsightActionImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.label, label) || other.label == label) &&
            (identical(other.prompt, prompt) || other.prompt == prompt) &&
            (identical(other.iconName, iconName) ||
                other.iconName == iconName) &&
            (identical(other.isPrimary, isPrimary) ||
                other.isPrimary == isPrimary));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, id, label, prompt, iconName, isPrimary);

  /// Create a copy of InsightAction
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$InsightActionImplCopyWith<_$InsightActionImpl> get copyWith =>
      __$$InsightActionImplCopyWithImpl<_$InsightActionImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$InsightActionImplToJson(
      this,
    );
  }
}

abstract class _InsightAction implements InsightAction {
  const factory _InsightAction(
      {required final String id,
      required final String label,
      required final String prompt,
      final String? iconName,
      final bool isPrimary}) = _$InsightActionImpl;

  factory _InsightAction.fromJson(Map<String, dynamic> json) =
      _$InsightActionImpl.fromJson;

  @override
  String get id;
  @override
  String get label;
  @override
  String get prompt; // 要填入聊天框的提示词
  @override
  String? get iconName;
  @override
  bool get isPrimary;

  /// Create a copy of InsightAction
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$InsightActionImplCopyWith<_$InsightActionImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

AIInsightsState _$AIInsightsStateFromJson(Map<String, dynamic> json) {
  return _AIInsightsState.fromJson(json);
}

/// @nodoc
mixin _$AIInsightsState {
  List<AIInsight> get realtimeInsights =>
      throw _privateConstructorUsedError; // 实时洞察
  List<AIInsight> get sessionInsights =>
      throw _privateConstructorUsedError; // 会话洞察
  List<AIInsight> get dailyInsights =>
      throw _privateConstructorUsedError; // 今日洞察
  List<AIInsight> get trendInsights =>
      throw _privateConstructorUsedError; // 趋势洞察
  List<AIInsight> get predictions => throw _privateConstructorUsedError; // 预测建议
  bool get isLoading => throw _privateConstructorUsedError;
  bool get isCollapsed => throw _privateConstructorUsedError; // 是否折叠
  String? get error => throw _privateConstructorUsedError;
  DateTime? get lastUpdated => throw _privateConstructorUsedError;

  /// Serializes this AIInsightsState to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of AIInsightsState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $AIInsightsStateCopyWith<AIInsightsState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AIInsightsStateCopyWith<$Res> {
  factory $AIInsightsStateCopyWith(
          AIInsightsState value, $Res Function(AIInsightsState) then) =
      _$AIInsightsStateCopyWithImpl<$Res, AIInsightsState>;
  @useResult
  $Res call(
      {List<AIInsight> realtimeInsights,
      List<AIInsight> sessionInsights,
      List<AIInsight> dailyInsights,
      List<AIInsight> trendInsights,
      List<AIInsight> predictions,
      bool isLoading,
      bool isCollapsed,
      String? error,
      DateTime? lastUpdated});
}

/// @nodoc
class _$AIInsightsStateCopyWithImpl<$Res, $Val extends AIInsightsState>
    implements $AIInsightsStateCopyWith<$Res> {
  _$AIInsightsStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of AIInsightsState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? realtimeInsights = null,
    Object? sessionInsights = null,
    Object? dailyInsights = null,
    Object? trendInsights = null,
    Object? predictions = null,
    Object? isLoading = null,
    Object? isCollapsed = null,
    Object? error = freezed,
    Object? lastUpdated = freezed,
  }) {
    return _then(_value.copyWith(
      realtimeInsights: null == realtimeInsights
          ? _value.realtimeInsights
          : realtimeInsights // ignore: cast_nullable_to_non_nullable
              as List<AIInsight>,
      sessionInsights: null == sessionInsights
          ? _value.sessionInsights
          : sessionInsights // ignore: cast_nullable_to_non_nullable
              as List<AIInsight>,
      dailyInsights: null == dailyInsights
          ? _value.dailyInsights
          : dailyInsights // ignore: cast_nullable_to_non_nullable
              as List<AIInsight>,
      trendInsights: null == trendInsights
          ? _value.trendInsights
          : trendInsights // ignore: cast_nullable_to_non_nullable
              as List<AIInsight>,
      predictions: null == predictions
          ? _value.predictions
          : predictions // ignore: cast_nullable_to_non_nullable
              as List<AIInsight>,
      isLoading: null == isLoading
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
      isCollapsed: null == isCollapsed
          ? _value.isCollapsed
          : isCollapsed // ignore: cast_nullable_to_non_nullable
              as bool,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
      lastUpdated: freezed == lastUpdated
          ? _value.lastUpdated
          : lastUpdated // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$AIInsightsStateImplCopyWith<$Res>
    implements $AIInsightsStateCopyWith<$Res> {
  factory _$$AIInsightsStateImplCopyWith(_$AIInsightsStateImpl value,
          $Res Function(_$AIInsightsStateImpl) then) =
      __$$AIInsightsStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {List<AIInsight> realtimeInsights,
      List<AIInsight> sessionInsights,
      List<AIInsight> dailyInsights,
      List<AIInsight> trendInsights,
      List<AIInsight> predictions,
      bool isLoading,
      bool isCollapsed,
      String? error,
      DateTime? lastUpdated});
}

/// @nodoc
class __$$AIInsightsStateImplCopyWithImpl<$Res>
    extends _$AIInsightsStateCopyWithImpl<$Res, _$AIInsightsStateImpl>
    implements _$$AIInsightsStateImplCopyWith<$Res> {
  __$$AIInsightsStateImplCopyWithImpl(
      _$AIInsightsStateImpl _value, $Res Function(_$AIInsightsStateImpl) _then)
      : super(_value, _then);

  /// Create a copy of AIInsightsState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? realtimeInsights = null,
    Object? sessionInsights = null,
    Object? dailyInsights = null,
    Object? trendInsights = null,
    Object? predictions = null,
    Object? isLoading = null,
    Object? isCollapsed = null,
    Object? error = freezed,
    Object? lastUpdated = freezed,
  }) {
    return _then(_$AIInsightsStateImpl(
      realtimeInsights: null == realtimeInsights
          ? _value._realtimeInsights
          : realtimeInsights // ignore: cast_nullable_to_non_nullable
              as List<AIInsight>,
      sessionInsights: null == sessionInsights
          ? _value._sessionInsights
          : sessionInsights // ignore: cast_nullable_to_non_nullable
              as List<AIInsight>,
      dailyInsights: null == dailyInsights
          ? _value._dailyInsights
          : dailyInsights // ignore: cast_nullable_to_non_nullable
              as List<AIInsight>,
      trendInsights: null == trendInsights
          ? _value._trendInsights
          : trendInsights // ignore: cast_nullable_to_non_nullable
              as List<AIInsight>,
      predictions: null == predictions
          ? _value._predictions
          : predictions // ignore: cast_nullable_to_non_nullable
              as List<AIInsight>,
      isLoading: null == isLoading
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
      isCollapsed: null == isCollapsed
          ? _value.isCollapsed
          : isCollapsed // ignore: cast_nullable_to_non_nullable
              as bool,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
      lastUpdated: freezed == lastUpdated
          ? _value.lastUpdated
          : lastUpdated // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$AIInsightsStateImpl implements _AIInsightsState {
  const _$AIInsightsStateImpl(
      {final List<AIInsight> realtimeInsights = const [],
      final List<AIInsight> sessionInsights = const [],
      final List<AIInsight> dailyInsights = const [],
      final List<AIInsight> trendInsights = const [],
      final List<AIInsight> predictions = const [],
      this.isLoading = false,
      this.isCollapsed = false,
      this.error,
      this.lastUpdated})
      : _realtimeInsights = realtimeInsights,
        _sessionInsights = sessionInsights,
        _dailyInsights = dailyInsights,
        _trendInsights = trendInsights,
        _predictions = predictions;

  factory _$AIInsightsStateImpl.fromJson(Map<String, dynamic> json) =>
      _$$AIInsightsStateImplFromJson(json);

  final List<AIInsight> _realtimeInsights;
  @override
  @JsonKey()
  List<AIInsight> get realtimeInsights {
    if (_realtimeInsights is EqualUnmodifiableListView)
      return _realtimeInsights;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_realtimeInsights);
  }

// 实时洞察
  final List<AIInsight> _sessionInsights;
// 实时洞察
  @override
  @JsonKey()
  List<AIInsight> get sessionInsights {
    if (_sessionInsights is EqualUnmodifiableListView) return _sessionInsights;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_sessionInsights);
  }

// 会话洞察
  final List<AIInsight> _dailyInsights;
// 会话洞察
  @override
  @JsonKey()
  List<AIInsight> get dailyInsights {
    if (_dailyInsights is EqualUnmodifiableListView) return _dailyInsights;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_dailyInsights);
  }

// 今日洞察
  final List<AIInsight> _trendInsights;
// 今日洞察
  @override
  @JsonKey()
  List<AIInsight> get trendInsights {
    if (_trendInsights is EqualUnmodifiableListView) return _trendInsights;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_trendInsights);
  }

// 趋势洞察
  final List<AIInsight> _predictions;
// 趋势洞察
  @override
  @JsonKey()
  List<AIInsight> get predictions {
    if (_predictions is EqualUnmodifiableListView) return _predictions;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_predictions);
  }

// 预测建议
  @override
  @JsonKey()
  final bool isLoading;
  @override
  @JsonKey()
  final bool isCollapsed;
// 是否折叠
  @override
  final String? error;
  @override
  final DateTime? lastUpdated;

  @override
  String toString() {
    return 'AIInsightsState(realtimeInsights: $realtimeInsights, sessionInsights: $sessionInsights, dailyInsights: $dailyInsights, trendInsights: $trendInsights, predictions: $predictions, isLoading: $isLoading, isCollapsed: $isCollapsed, error: $error, lastUpdated: $lastUpdated)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$AIInsightsStateImpl &&
            const DeepCollectionEquality()
                .equals(other._realtimeInsights, _realtimeInsights) &&
            const DeepCollectionEquality()
                .equals(other._sessionInsights, _sessionInsights) &&
            const DeepCollectionEquality()
                .equals(other._dailyInsights, _dailyInsights) &&
            const DeepCollectionEquality()
                .equals(other._trendInsights, _trendInsights) &&
            const DeepCollectionEquality()
                .equals(other._predictions, _predictions) &&
            (identical(other.isLoading, isLoading) ||
                other.isLoading == isLoading) &&
            (identical(other.isCollapsed, isCollapsed) ||
                other.isCollapsed == isCollapsed) &&
            (identical(other.error, error) || other.error == error) &&
            (identical(other.lastUpdated, lastUpdated) ||
                other.lastUpdated == lastUpdated));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(_realtimeInsights),
      const DeepCollectionEquality().hash(_sessionInsights),
      const DeepCollectionEquality().hash(_dailyInsights),
      const DeepCollectionEquality().hash(_trendInsights),
      const DeepCollectionEquality().hash(_predictions),
      isLoading,
      isCollapsed,
      error,
      lastUpdated);

  /// Create a copy of AIInsightsState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$AIInsightsStateImplCopyWith<_$AIInsightsStateImpl> get copyWith =>
      __$$AIInsightsStateImplCopyWithImpl<_$AIInsightsStateImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$AIInsightsStateImplToJson(
      this,
    );
  }
}

abstract class _AIInsightsState implements AIInsightsState {
  const factory _AIInsightsState(
      {final List<AIInsight> realtimeInsights,
      final List<AIInsight> sessionInsights,
      final List<AIInsight> dailyInsights,
      final List<AIInsight> trendInsights,
      final List<AIInsight> predictions,
      final bool isLoading,
      final bool isCollapsed,
      final String? error,
      final DateTime? lastUpdated}) = _$AIInsightsStateImpl;

  factory _AIInsightsState.fromJson(Map<String, dynamic> json) =
      _$AIInsightsStateImpl.fromJson;

  @override
  List<AIInsight> get realtimeInsights; // 实时洞察
  @override
  List<AIInsight> get sessionInsights; // 会话洞察
  @override
  List<AIInsight> get dailyInsights; // 今日洞察
  @override
  List<AIInsight> get trendInsights; // 趋势洞察
  @override
  List<AIInsight> get predictions; // 预测建议
  @override
  bool get isLoading;
  @override
  bool get isCollapsed; // 是否折叠
  @override
  String? get error;
  @override
  DateTime? get lastUpdated;

  /// Create a copy of AIInsightsState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$AIInsightsStateImplCopyWith<_$AIInsightsStateImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

WorkSession _$WorkSessionFromJson(Map<String, dynamic> json) {
  return _WorkSession.fromJson(json);
}

/// @nodoc
mixin _$WorkSession {
  String get id => throw _privateConstructorUsedError;
  DateTime get startTime => throw _privateConstructorUsedError;
  DateTime? get endTime => throw _privateConstructorUsedError;
  String get mainTopic => throw _privateConstructorUsedError; // 主要工作主题
  List<String> get keywords => throw _privateConstructorUsedError; // 关键词
  List<String> get files => throw _privateConstructorUsedError; // 涉及文件
  int get focusMinutes => throw _privateConstructorUsedError; // 专注时间（分钟）
  int get breaksCount => throw _privateConstructorUsedError; // 休息次数
  Map<String, dynamic>? get metrics => throw _privateConstructorUsedError;

  /// Serializes this WorkSession to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of WorkSession
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $WorkSessionCopyWith<WorkSession> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $WorkSessionCopyWith<$Res> {
  factory $WorkSessionCopyWith(
          WorkSession value, $Res Function(WorkSession) then) =
      _$WorkSessionCopyWithImpl<$Res, WorkSession>;
  @useResult
  $Res call(
      {String id,
      DateTime startTime,
      DateTime? endTime,
      String mainTopic,
      List<String> keywords,
      List<String> files,
      int focusMinutes,
      int breaksCount,
      Map<String, dynamic>? metrics});
}

/// @nodoc
class _$WorkSessionCopyWithImpl<$Res, $Val extends WorkSession>
    implements $WorkSessionCopyWith<$Res> {
  _$WorkSessionCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of WorkSession
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? startTime = null,
    Object? endTime = freezed,
    Object? mainTopic = null,
    Object? keywords = null,
    Object? files = null,
    Object? focusMinutes = null,
    Object? breaksCount = null,
    Object? metrics = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      startTime: null == startTime
          ? _value.startTime
          : startTime // ignore: cast_nullable_to_non_nullable
              as DateTime,
      endTime: freezed == endTime
          ? _value.endTime
          : endTime // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      mainTopic: null == mainTopic
          ? _value.mainTopic
          : mainTopic // ignore: cast_nullable_to_non_nullable
              as String,
      keywords: null == keywords
          ? _value.keywords
          : keywords // ignore: cast_nullable_to_non_nullable
              as List<String>,
      files: null == files
          ? _value.files
          : files // ignore: cast_nullable_to_non_nullable
              as List<String>,
      focusMinutes: null == focusMinutes
          ? _value.focusMinutes
          : focusMinutes // ignore: cast_nullable_to_non_nullable
              as int,
      breaksCount: null == breaksCount
          ? _value.breaksCount
          : breaksCount // ignore: cast_nullable_to_non_nullable
              as int,
      metrics: freezed == metrics
          ? _value.metrics
          : metrics // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$WorkSessionImplCopyWith<$Res>
    implements $WorkSessionCopyWith<$Res> {
  factory _$$WorkSessionImplCopyWith(
          _$WorkSessionImpl value, $Res Function(_$WorkSessionImpl) then) =
      __$$WorkSessionImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      DateTime startTime,
      DateTime? endTime,
      String mainTopic,
      List<String> keywords,
      List<String> files,
      int focusMinutes,
      int breaksCount,
      Map<String, dynamic>? metrics});
}

/// @nodoc
class __$$WorkSessionImplCopyWithImpl<$Res>
    extends _$WorkSessionCopyWithImpl<$Res, _$WorkSessionImpl>
    implements _$$WorkSessionImplCopyWith<$Res> {
  __$$WorkSessionImplCopyWithImpl(
      _$WorkSessionImpl _value, $Res Function(_$WorkSessionImpl) _then)
      : super(_value, _then);

  /// Create a copy of WorkSession
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? startTime = null,
    Object? endTime = freezed,
    Object? mainTopic = null,
    Object? keywords = null,
    Object? files = null,
    Object? focusMinutes = null,
    Object? breaksCount = null,
    Object? metrics = freezed,
  }) {
    return _then(_$WorkSessionImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      startTime: null == startTime
          ? _value.startTime
          : startTime // ignore: cast_nullable_to_non_nullable
              as DateTime,
      endTime: freezed == endTime
          ? _value.endTime
          : endTime // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      mainTopic: null == mainTopic
          ? _value.mainTopic
          : mainTopic // ignore: cast_nullable_to_non_nullable
              as String,
      keywords: null == keywords
          ? _value._keywords
          : keywords // ignore: cast_nullable_to_non_nullable
              as List<String>,
      files: null == files
          ? _value._files
          : files // ignore: cast_nullable_to_non_nullable
              as List<String>,
      focusMinutes: null == focusMinutes
          ? _value.focusMinutes
          : focusMinutes // ignore: cast_nullable_to_non_nullable
              as int,
      breaksCount: null == breaksCount
          ? _value.breaksCount
          : breaksCount // ignore: cast_nullable_to_non_nullable
              as int,
      metrics: freezed == metrics
          ? _value._metrics
          : metrics // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$WorkSessionImpl implements _WorkSession {
  const _$WorkSessionImpl(
      {required this.id,
      required this.startTime,
      this.endTime,
      required this.mainTopic,
      final List<String> keywords = const [],
      final List<String> files = const [],
      this.focusMinutes = 0,
      this.breaksCount = 0,
      final Map<String, dynamic>? metrics})
      : _keywords = keywords,
        _files = files,
        _metrics = metrics;

  factory _$WorkSessionImpl.fromJson(Map<String, dynamic> json) =>
      _$$WorkSessionImplFromJson(json);

  @override
  final String id;
  @override
  final DateTime startTime;
  @override
  final DateTime? endTime;
  @override
  final String mainTopic;
// 主要工作主题
  final List<String> _keywords;
// 主要工作主题
  @override
  @JsonKey()
  List<String> get keywords {
    if (_keywords is EqualUnmodifiableListView) return _keywords;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_keywords);
  }

// 关键词
  final List<String> _files;
// 关键词
  @override
  @JsonKey()
  List<String> get files {
    if (_files is EqualUnmodifiableListView) return _files;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_files);
  }

// 涉及文件
  @override
  @JsonKey()
  final int focusMinutes;
// 专注时间（分钟）
  @override
  @JsonKey()
  final int breaksCount;
// 休息次数
  final Map<String, dynamic>? _metrics;
// 休息次数
  @override
  Map<String, dynamic>? get metrics {
    final value = _metrics;
    if (value == null) return null;
    if (_metrics is EqualUnmodifiableMapView) return _metrics;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'WorkSession(id: $id, startTime: $startTime, endTime: $endTime, mainTopic: $mainTopic, keywords: $keywords, files: $files, focusMinutes: $focusMinutes, breaksCount: $breaksCount, metrics: $metrics)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$WorkSessionImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.startTime, startTime) ||
                other.startTime == startTime) &&
            (identical(other.endTime, endTime) || other.endTime == endTime) &&
            (identical(other.mainTopic, mainTopic) ||
                other.mainTopic == mainTopic) &&
            const DeepCollectionEquality().equals(other._keywords, _keywords) &&
            const DeepCollectionEquality().equals(other._files, _files) &&
            (identical(other.focusMinutes, focusMinutes) ||
                other.focusMinutes == focusMinutes) &&
            (identical(other.breaksCount, breaksCount) ||
                other.breaksCount == breaksCount) &&
            const DeepCollectionEquality().equals(other._metrics, _metrics));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      startTime,
      endTime,
      mainTopic,
      const DeepCollectionEquality().hash(_keywords),
      const DeepCollectionEquality().hash(_files),
      focusMinutes,
      breaksCount,
      const DeepCollectionEquality().hash(_metrics));

  /// Create a copy of WorkSession
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$WorkSessionImplCopyWith<_$WorkSessionImpl> get copyWith =>
      __$$WorkSessionImplCopyWithImpl<_$WorkSessionImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$WorkSessionImplToJson(
      this,
    );
  }
}

abstract class _WorkSession implements WorkSession {
  const factory _WorkSession(
      {required final String id,
      required final DateTime startTime,
      final DateTime? endTime,
      required final String mainTopic,
      final List<String> keywords,
      final List<String> files,
      final int focusMinutes,
      final int breaksCount,
      final Map<String, dynamic>? metrics}) = _$WorkSessionImpl;

  factory _WorkSession.fromJson(Map<String, dynamic> json) =
      _$WorkSessionImpl.fromJson;

  @override
  String get id;
  @override
  DateTime get startTime;
  @override
  DateTime? get endTime;
  @override
  String get mainTopic; // 主要工作主题
  @override
  List<String> get keywords; // 关键词
  @override
  List<String> get files; // 涉及文件
  @override
  int get focusMinutes; // 专注时间（分钟）
  @override
  int get breaksCount; // 休息次数
  @override
  Map<String, dynamic>? get metrics;

  /// Create a copy of WorkSession
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$WorkSessionImplCopyWith<_$WorkSessionImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

TrendData _$TrendDataFromJson(Map<String, dynamic> json) {
  return _TrendData.fromJson(json);
}

/// @nodoc
mixin _$TrendData {
  String get metric => throw _privateConstructorUsedError; // 指标名称
  List<TrendPoint> get points => throw _privateConstructorUsedError; // 数据点
  String get unit => throw _privateConstructorUsedError; // 单位
  double get changePercent => throw _privateConstructorUsedError; // 变化百分比
  String? get interpretation => throw _privateConstructorUsedError;

  /// Serializes this TrendData to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of TrendData
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $TrendDataCopyWith<TrendData> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $TrendDataCopyWith<$Res> {
  factory $TrendDataCopyWith(TrendData value, $Res Function(TrendData) then) =
      _$TrendDataCopyWithImpl<$Res, TrendData>;
  @useResult
  $Res call(
      {String metric,
      List<TrendPoint> points,
      String unit,
      double changePercent,
      String? interpretation});
}

/// @nodoc
class _$TrendDataCopyWithImpl<$Res, $Val extends TrendData>
    implements $TrendDataCopyWith<$Res> {
  _$TrendDataCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of TrendData
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? metric = null,
    Object? points = null,
    Object? unit = null,
    Object? changePercent = null,
    Object? interpretation = freezed,
  }) {
    return _then(_value.copyWith(
      metric: null == metric
          ? _value.metric
          : metric // ignore: cast_nullable_to_non_nullable
              as String,
      points: null == points
          ? _value.points
          : points // ignore: cast_nullable_to_non_nullable
              as List<TrendPoint>,
      unit: null == unit
          ? _value.unit
          : unit // ignore: cast_nullable_to_non_nullable
              as String,
      changePercent: null == changePercent
          ? _value.changePercent
          : changePercent // ignore: cast_nullable_to_non_nullable
              as double,
      interpretation: freezed == interpretation
          ? _value.interpretation
          : interpretation // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$TrendDataImplCopyWith<$Res>
    implements $TrendDataCopyWith<$Res> {
  factory _$$TrendDataImplCopyWith(
          _$TrendDataImpl value, $Res Function(_$TrendDataImpl) then) =
      __$$TrendDataImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String metric,
      List<TrendPoint> points,
      String unit,
      double changePercent,
      String? interpretation});
}

/// @nodoc
class __$$TrendDataImplCopyWithImpl<$Res>
    extends _$TrendDataCopyWithImpl<$Res, _$TrendDataImpl>
    implements _$$TrendDataImplCopyWith<$Res> {
  __$$TrendDataImplCopyWithImpl(
      _$TrendDataImpl _value, $Res Function(_$TrendDataImpl) _then)
      : super(_value, _then);

  /// Create a copy of TrendData
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? metric = null,
    Object? points = null,
    Object? unit = null,
    Object? changePercent = null,
    Object? interpretation = freezed,
  }) {
    return _then(_$TrendDataImpl(
      metric: null == metric
          ? _value.metric
          : metric // ignore: cast_nullable_to_non_nullable
              as String,
      points: null == points
          ? _value._points
          : points // ignore: cast_nullable_to_non_nullable
              as List<TrendPoint>,
      unit: null == unit
          ? _value.unit
          : unit // ignore: cast_nullable_to_non_nullable
              as String,
      changePercent: null == changePercent
          ? _value.changePercent
          : changePercent // ignore: cast_nullable_to_non_nullable
              as double,
      interpretation: freezed == interpretation
          ? _value.interpretation
          : interpretation // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$TrendDataImpl implements _TrendData {
  const _$TrendDataImpl(
      {required this.metric,
      required final List<TrendPoint> points,
      required this.unit,
      this.changePercent = 0.0,
      this.interpretation})
      : _points = points;

  factory _$TrendDataImpl.fromJson(Map<String, dynamic> json) =>
      _$$TrendDataImplFromJson(json);

  @override
  final String metric;
// 指标名称
  final List<TrendPoint> _points;
// 指标名称
  @override
  List<TrendPoint> get points {
    if (_points is EqualUnmodifiableListView) return _points;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_points);
  }

// 数据点
  @override
  final String unit;
// 单位
  @override
  @JsonKey()
  final double changePercent;
// 变化百分比
  @override
  final String? interpretation;

  @override
  String toString() {
    return 'TrendData(metric: $metric, points: $points, unit: $unit, changePercent: $changePercent, interpretation: $interpretation)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$TrendDataImpl &&
            (identical(other.metric, metric) || other.metric == metric) &&
            const DeepCollectionEquality().equals(other._points, _points) &&
            (identical(other.unit, unit) || other.unit == unit) &&
            (identical(other.changePercent, changePercent) ||
                other.changePercent == changePercent) &&
            (identical(other.interpretation, interpretation) ||
                other.interpretation == interpretation));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      metric,
      const DeepCollectionEquality().hash(_points),
      unit,
      changePercent,
      interpretation);

  /// Create a copy of TrendData
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$TrendDataImplCopyWith<_$TrendDataImpl> get copyWith =>
      __$$TrendDataImplCopyWithImpl<_$TrendDataImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$TrendDataImplToJson(
      this,
    );
  }
}

abstract class _TrendData implements TrendData {
  const factory _TrendData(
      {required final String metric,
      required final List<TrendPoint> points,
      required final String unit,
      final double changePercent,
      final String? interpretation}) = _$TrendDataImpl;

  factory _TrendData.fromJson(Map<String, dynamic> json) =
      _$TrendDataImpl.fromJson;

  @override
  String get metric; // 指标名称
  @override
  List<TrendPoint> get points; // 数据点
  @override
  String get unit; // 单位
  @override
  double get changePercent; // 变化百分比
  @override
  String? get interpretation;

  /// Create a copy of TrendData
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$TrendDataImplCopyWith<_$TrendDataImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

TrendPoint _$TrendPointFromJson(Map<String, dynamic> json) {
  return _TrendPoint.fromJson(json);
}

/// @nodoc
mixin _$TrendPoint {
  DateTime get timestamp => throw _privateConstructorUsedError;
  double get value => throw _privateConstructorUsedError;
  String? get label => throw _privateConstructorUsedError;

  /// Serializes this TrendPoint to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of TrendPoint
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $TrendPointCopyWith<TrendPoint> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $TrendPointCopyWith<$Res> {
  factory $TrendPointCopyWith(
          TrendPoint value, $Res Function(TrendPoint) then) =
      _$TrendPointCopyWithImpl<$Res, TrendPoint>;
  @useResult
  $Res call({DateTime timestamp, double value, String? label});
}

/// @nodoc
class _$TrendPointCopyWithImpl<$Res, $Val extends TrendPoint>
    implements $TrendPointCopyWith<$Res> {
  _$TrendPointCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of TrendPoint
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? timestamp = null,
    Object? value = null,
    Object? label = freezed,
  }) {
    return _then(_value.copyWith(
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      value: null == value
          ? _value.value
          : value // ignore: cast_nullable_to_non_nullable
              as double,
      label: freezed == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$TrendPointImplCopyWith<$Res>
    implements $TrendPointCopyWith<$Res> {
  factory _$$TrendPointImplCopyWith(
          _$TrendPointImpl value, $Res Function(_$TrendPointImpl) then) =
      __$$TrendPointImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({DateTime timestamp, double value, String? label});
}

/// @nodoc
class __$$TrendPointImplCopyWithImpl<$Res>
    extends _$TrendPointCopyWithImpl<$Res, _$TrendPointImpl>
    implements _$$TrendPointImplCopyWith<$Res> {
  __$$TrendPointImplCopyWithImpl(
      _$TrendPointImpl _value, $Res Function(_$TrendPointImpl) _then)
      : super(_value, _then);

  /// Create a copy of TrendPoint
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? timestamp = null,
    Object? value = null,
    Object? label = freezed,
  }) {
    return _then(_$TrendPointImpl(
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      value: null == value
          ? _value.value
          : value // ignore: cast_nullable_to_non_nullable
              as double,
      label: freezed == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$TrendPointImpl implements _TrendPoint {
  const _$TrendPointImpl(
      {required this.timestamp, required this.value, this.label});

  factory _$TrendPointImpl.fromJson(Map<String, dynamic> json) =>
      _$$TrendPointImplFromJson(json);

  @override
  final DateTime timestamp;
  @override
  final double value;
  @override
  final String? label;

  @override
  String toString() {
    return 'TrendPoint(timestamp: $timestamp, value: $value, label: $label)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$TrendPointImpl &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp) &&
            (identical(other.value, value) || other.value == value) &&
            (identical(other.label, label) || other.label == label));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, timestamp, value, label);

  /// Create a copy of TrendPoint
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$TrendPointImplCopyWith<_$TrendPointImpl> get copyWith =>
      __$$TrendPointImplCopyWithImpl<_$TrendPointImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$TrendPointImplToJson(
      this,
    );
  }
}

abstract class _TrendPoint implements TrendPoint {
  const factory _TrendPoint(
      {required final DateTime timestamp,
      required final double value,
      final String? label}) = _$TrendPointImpl;

  factory _TrendPoint.fromJson(Map<String, dynamic> json) =
      _$TrendPointImpl.fromJson;

  @override
  DateTime get timestamp;
  @override
  double get value;
  @override
  String? get label;

  /// Create a copy of TrendPoint
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$TrendPointImplCopyWith<_$TrendPointImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

SkillAssessment _$SkillAssessmentFromJson(Map<String, dynamic> json) {
  return _SkillAssessment.fromJson(json);
}

/// @nodoc
mixin _$SkillAssessment {
  String get skillName => throw _privateConstructorUsedError;
  double get currentLevel => throw _privateConstructorUsedError; // 当前水平 (0-1)
  double get previousLevel => throw _privateConstructorUsedError; // 之前水平
  List<String> get evidence => throw _privateConstructorUsedError; // 证据/表现
  String? get nextMilestone => throw _privateConstructorUsedError; // 下一个里程碑
  List<String> get suggestions => throw _privateConstructorUsedError;

  /// Serializes this SkillAssessment to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of SkillAssessment
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SkillAssessmentCopyWith<SkillAssessment> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SkillAssessmentCopyWith<$Res> {
  factory $SkillAssessmentCopyWith(
          SkillAssessment value, $Res Function(SkillAssessment) then) =
      _$SkillAssessmentCopyWithImpl<$Res, SkillAssessment>;
  @useResult
  $Res call(
      {String skillName,
      double currentLevel,
      double previousLevel,
      List<String> evidence,
      String? nextMilestone,
      List<String> suggestions});
}

/// @nodoc
class _$SkillAssessmentCopyWithImpl<$Res, $Val extends SkillAssessment>
    implements $SkillAssessmentCopyWith<$Res> {
  _$SkillAssessmentCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of SkillAssessment
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? skillName = null,
    Object? currentLevel = null,
    Object? previousLevel = null,
    Object? evidence = null,
    Object? nextMilestone = freezed,
    Object? suggestions = null,
  }) {
    return _then(_value.copyWith(
      skillName: null == skillName
          ? _value.skillName
          : skillName // ignore: cast_nullable_to_non_nullable
              as String,
      currentLevel: null == currentLevel
          ? _value.currentLevel
          : currentLevel // ignore: cast_nullable_to_non_nullable
              as double,
      previousLevel: null == previousLevel
          ? _value.previousLevel
          : previousLevel // ignore: cast_nullable_to_non_nullable
              as double,
      evidence: null == evidence
          ? _value.evidence
          : evidence // ignore: cast_nullable_to_non_nullable
              as List<String>,
      nextMilestone: freezed == nextMilestone
          ? _value.nextMilestone
          : nextMilestone // ignore: cast_nullable_to_non_nullable
              as String?,
      suggestions: null == suggestions
          ? _value.suggestions
          : suggestions // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$SkillAssessmentImplCopyWith<$Res>
    implements $SkillAssessmentCopyWith<$Res> {
  factory _$$SkillAssessmentImplCopyWith(_$SkillAssessmentImpl value,
          $Res Function(_$SkillAssessmentImpl) then) =
      __$$SkillAssessmentImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String skillName,
      double currentLevel,
      double previousLevel,
      List<String> evidence,
      String? nextMilestone,
      List<String> suggestions});
}

/// @nodoc
class __$$SkillAssessmentImplCopyWithImpl<$Res>
    extends _$SkillAssessmentCopyWithImpl<$Res, _$SkillAssessmentImpl>
    implements _$$SkillAssessmentImplCopyWith<$Res> {
  __$$SkillAssessmentImplCopyWithImpl(
      _$SkillAssessmentImpl _value, $Res Function(_$SkillAssessmentImpl) _then)
      : super(_value, _then);

  /// Create a copy of SkillAssessment
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? skillName = null,
    Object? currentLevel = null,
    Object? previousLevel = null,
    Object? evidence = null,
    Object? nextMilestone = freezed,
    Object? suggestions = null,
  }) {
    return _then(_$SkillAssessmentImpl(
      skillName: null == skillName
          ? _value.skillName
          : skillName // ignore: cast_nullable_to_non_nullable
              as String,
      currentLevel: null == currentLevel
          ? _value.currentLevel
          : currentLevel // ignore: cast_nullable_to_non_nullable
              as double,
      previousLevel: null == previousLevel
          ? _value.previousLevel
          : previousLevel // ignore: cast_nullable_to_non_nullable
              as double,
      evidence: null == evidence
          ? _value._evidence
          : evidence // ignore: cast_nullable_to_non_nullable
              as List<String>,
      nextMilestone: freezed == nextMilestone
          ? _value.nextMilestone
          : nextMilestone // ignore: cast_nullable_to_non_nullable
              as String?,
      suggestions: null == suggestions
          ? _value._suggestions
          : suggestions // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$SkillAssessmentImpl implements _SkillAssessment {
  const _$SkillAssessmentImpl(
      {required this.skillName,
      required this.currentLevel,
      required this.previousLevel,
      required final List<String> evidence,
      this.nextMilestone,
      final List<String> suggestions = const []})
      : _evidence = evidence,
        _suggestions = suggestions;

  factory _$SkillAssessmentImpl.fromJson(Map<String, dynamic> json) =>
      _$$SkillAssessmentImplFromJson(json);

  @override
  final String skillName;
  @override
  final double currentLevel;
// 当前水平 (0-1)
  @override
  final double previousLevel;
// 之前水平
  final List<String> _evidence;
// 之前水平
  @override
  List<String> get evidence {
    if (_evidence is EqualUnmodifiableListView) return _evidence;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_evidence);
  }

// 证据/表现
  @override
  final String? nextMilestone;
// 下一个里程碑
  final List<String> _suggestions;
// 下一个里程碑
  @override
  @JsonKey()
  List<String> get suggestions {
    if (_suggestions is EqualUnmodifiableListView) return _suggestions;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_suggestions);
  }

  @override
  String toString() {
    return 'SkillAssessment(skillName: $skillName, currentLevel: $currentLevel, previousLevel: $previousLevel, evidence: $evidence, nextMilestone: $nextMilestone, suggestions: $suggestions)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SkillAssessmentImpl &&
            (identical(other.skillName, skillName) ||
                other.skillName == skillName) &&
            (identical(other.currentLevel, currentLevel) ||
                other.currentLevel == currentLevel) &&
            (identical(other.previousLevel, previousLevel) ||
                other.previousLevel == previousLevel) &&
            const DeepCollectionEquality().equals(other._evidence, _evidence) &&
            (identical(other.nextMilestone, nextMilestone) ||
                other.nextMilestone == nextMilestone) &&
            const DeepCollectionEquality()
                .equals(other._suggestions, _suggestions));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      skillName,
      currentLevel,
      previousLevel,
      const DeepCollectionEquality().hash(_evidence),
      nextMilestone,
      const DeepCollectionEquality().hash(_suggestions));

  /// Create a copy of SkillAssessment
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SkillAssessmentImplCopyWith<_$SkillAssessmentImpl> get copyWith =>
      __$$SkillAssessmentImplCopyWithImpl<_$SkillAssessmentImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SkillAssessmentImplToJson(
      this,
    );
  }
}

abstract class _SkillAssessment implements SkillAssessment {
  const factory _SkillAssessment(
      {required final String skillName,
      required final double currentLevel,
      required final double previousLevel,
      required final List<String> evidence,
      final String? nextMilestone,
      final List<String> suggestions}) = _$SkillAssessmentImpl;

  factory _SkillAssessment.fromJson(Map<String, dynamic> json) =
      _$SkillAssessmentImpl.fromJson;

  @override
  String get skillName;
  @override
  double get currentLevel; // 当前水平 (0-1)
  @override
  double get previousLevel; // 之前水平
  @override
  List<String> get evidence; // 证据/表现
  @override
  String? get nextMilestone; // 下一个里程碑
  @override
  List<String> get suggestions;

  /// Create a copy of SkillAssessment
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SkillAssessmentImplCopyWith<_$SkillAssessmentImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
