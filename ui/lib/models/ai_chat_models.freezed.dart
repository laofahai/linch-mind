// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'ai_chat_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

AIChatMessage _$AIChatMessageFromJson(Map<String, dynamic> json) {
  return _AIChatMessage.fromJson(json);
}

/// @nodoc
mixin _$AIChatMessage {
  String get id => throw _privateConstructorUsedError;
  String get content => throw _privateConstructorUsedError;
  MessageType get type => throw _privateConstructorUsedError;
  DateTime get timestamp => throw _privateConstructorUsedError;
  List<MessageAction> get actions => throw _privateConstructorUsedError;
  MessageStatus get status => throw _privateConstructorUsedError;
  Map<String, dynamic>? get metadata => throw _privateConstructorUsedError;
  String? get replyToId => throw _privateConstructorUsedError;

  /// Serializes this AIChatMessage to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of AIChatMessage
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $AIChatMessageCopyWith<AIChatMessage> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AIChatMessageCopyWith<$Res> {
  factory $AIChatMessageCopyWith(
          AIChatMessage value, $Res Function(AIChatMessage) then) =
      _$AIChatMessageCopyWithImpl<$Res, AIChatMessage>;
  @useResult
  $Res call(
      {String id,
      String content,
      MessageType type,
      DateTime timestamp,
      List<MessageAction> actions,
      MessageStatus status,
      Map<String, dynamic>? metadata,
      String? replyToId});
}

/// @nodoc
class _$AIChatMessageCopyWithImpl<$Res, $Val extends AIChatMessage>
    implements $AIChatMessageCopyWith<$Res> {
  _$AIChatMessageCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of AIChatMessage
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? content = null,
    Object? type = null,
    Object? timestamp = null,
    Object? actions = null,
    Object? status = null,
    Object? metadata = freezed,
    Object? replyToId = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      content: null == content
          ? _value.content
          : content // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as MessageType,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      actions: null == actions
          ? _value.actions
          : actions // ignore: cast_nullable_to_non_nullable
              as List<MessageAction>,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as MessageStatus,
      metadata: freezed == metadata
          ? _value.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      replyToId: freezed == replyToId
          ? _value.replyToId
          : replyToId // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$AIChatMessageImplCopyWith<$Res>
    implements $AIChatMessageCopyWith<$Res> {
  factory _$$AIChatMessageImplCopyWith(
          _$AIChatMessageImpl value, $Res Function(_$AIChatMessageImpl) then) =
      __$$AIChatMessageImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String content,
      MessageType type,
      DateTime timestamp,
      List<MessageAction> actions,
      MessageStatus status,
      Map<String, dynamic>? metadata,
      String? replyToId});
}

/// @nodoc
class __$$AIChatMessageImplCopyWithImpl<$Res>
    extends _$AIChatMessageCopyWithImpl<$Res, _$AIChatMessageImpl>
    implements _$$AIChatMessageImplCopyWith<$Res> {
  __$$AIChatMessageImplCopyWithImpl(
      _$AIChatMessageImpl _value, $Res Function(_$AIChatMessageImpl) _then)
      : super(_value, _then);

  /// Create a copy of AIChatMessage
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? content = null,
    Object? type = null,
    Object? timestamp = null,
    Object? actions = null,
    Object? status = null,
    Object? metadata = freezed,
    Object? replyToId = freezed,
  }) {
    return _then(_$AIChatMessageImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      content: null == content
          ? _value.content
          : content // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as MessageType,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      actions: null == actions
          ? _value._actions
          : actions // ignore: cast_nullable_to_non_nullable
              as List<MessageAction>,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as MessageStatus,
      metadata: freezed == metadata
          ? _value._metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      replyToId: freezed == replyToId
          ? _value.replyToId
          : replyToId // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$AIChatMessageImpl implements _AIChatMessage {
  const _$AIChatMessageImpl(
      {required this.id,
      required this.content,
      required this.type,
      required this.timestamp,
      final List<MessageAction> actions = const [],
      this.status = MessageStatus.sent,
      final Map<String, dynamic>? metadata,
      this.replyToId})
      : _actions = actions,
        _metadata = metadata;

  factory _$AIChatMessageImpl.fromJson(Map<String, dynamic> json) =>
      _$$AIChatMessageImplFromJson(json);

  @override
  final String id;
  @override
  final String content;
  @override
  final MessageType type;
  @override
  final DateTime timestamp;
  final List<MessageAction> _actions;
  @override
  @JsonKey()
  List<MessageAction> get actions {
    if (_actions is EqualUnmodifiableListView) return _actions;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_actions);
  }

  @override
  @JsonKey()
  final MessageStatus status;
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
  final String? replyToId;

  @override
  String toString() {
    return 'AIChatMessage(id: $id, content: $content, type: $type, timestamp: $timestamp, actions: $actions, status: $status, metadata: $metadata, replyToId: $replyToId)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$AIChatMessageImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.content, content) || other.content == content) &&
            (identical(other.type, type) || other.type == type) &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp) &&
            const DeepCollectionEquality().equals(other._actions, _actions) &&
            (identical(other.status, status) || other.status == status) &&
            const DeepCollectionEquality().equals(other._metadata, _metadata) &&
            (identical(other.replyToId, replyToId) ||
                other.replyToId == replyToId));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      content,
      type,
      timestamp,
      const DeepCollectionEquality().hash(_actions),
      status,
      const DeepCollectionEquality().hash(_metadata),
      replyToId);

  /// Create a copy of AIChatMessage
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$AIChatMessageImplCopyWith<_$AIChatMessageImpl> get copyWith =>
      __$$AIChatMessageImplCopyWithImpl<_$AIChatMessageImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$AIChatMessageImplToJson(
      this,
    );
  }
}

abstract class _AIChatMessage implements AIChatMessage {
  const factory _AIChatMessage(
      {required final String id,
      required final String content,
      required final MessageType type,
      required final DateTime timestamp,
      final List<MessageAction> actions,
      final MessageStatus status,
      final Map<String, dynamic>? metadata,
      final String? replyToId}) = _$AIChatMessageImpl;

  factory _AIChatMessage.fromJson(Map<String, dynamic> json) =
      _$AIChatMessageImpl.fromJson;

  @override
  String get id;
  @override
  String get content;
  @override
  MessageType get type;
  @override
  DateTime get timestamp;
  @override
  List<MessageAction> get actions;
  @override
  MessageStatus get status;
  @override
  Map<String, dynamic>? get metadata;
  @override
  String? get replyToId;

  /// Create a copy of AIChatMessage
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$AIChatMessageImplCopyWith<_$AIChatMessageImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

MessageAction _$MessageActionFromJson(Map<String, dynamic> json) {
  return _MessageAction.fromJson(json);
}

/// @nodoc
mixin _$MessageAction {
  String get id => throw _privateConstructorUsedError;
  String get label => throw _privateConstructorUsedError;
  ActionType get type => throw _privateConstructorUsedError;
  String? get payload => throw _privateConstructorUsedError;
  Map<String, dynamic>? get data => throw _privateConstructorUsedError;

  /// Serializes this MessageAction to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of MessageAction
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $MessageActionCopyWith<MessageAction> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $MessageActionCopyWith<$Res> {
  factory $MessageActionCopyWith(
          MessageAction value, $Res Function(MessageAction) then) =
      _$MessageActionCopyWithImpl<$Res, MessageAction>;
  @useResult
  $Res call(
      {String id,
      String label,
      ActionType type,
      String? payload,
      Map<String, dynamic>? data});
}

/// @nodoc
class _$MessageActionCopyWithImpl<$Res, $Val extends MessageAction>
    implements $MessageActionCopyWith<$Res> {
  _$MessageActionCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of MessageAction
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? label = null,
    Object? type = null,
    Object? payload = freezed,
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
              as ActionType,
      payload: freezed == payload
          ? _value.payload
          : payload // ignore: cast_nullable_to_non_nullable
              as String?,
      data: freezed == data
          ? _value.data
          : data // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$MessageActionImplCopyWith<$Res>
    implements $MessageActionCopyWith<$Res> {
  factory _$$MessageActionImplCopyWith(
          _$MessageActionImpl value, $Res Function(_$MessageActionImpl) then) =
      __$$MessageActionImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String label,
      ActionType type,
      String? payload,
      Map<String, dynamic>? data});
}

/// @nodoc
class __$$MessageActionImplCopyWithImpl<$Res>
    extends _$MessageActionCopyWithImpl<$Res, _$MessageActionImpl>
    implements _$$MessageActionImplCopyWith<$Res> {
  __$$MessageActionImplCopyWithImpl(
      _$MessageActionImpl _value, $Res Function(_$MessageActionImpl) _then)
      : super(_value, _then);

  /// Create a copy of MessageAction
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? label = null,
    Object? type = null,
    Object? payload = freezed,
    Object? data = freezed,
  }) {
    return _then(_$MessageActionImpl(
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
              as ActionType,
      payload: freezed == payload
          ? _value.payload
          : payload // ignore: cast_nullable_to_non_nullable
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
class _$MessageActionImpl implements _MessageAction {
  const _$MessageActionImpl(
      {required this.id,
      required this.label,
      required this.type,
      this.payload,
      final Map<String, dynamic>? data})
      : _data = data;

  factory _$MessageActionImpl.fromJson(Map<String, dynamic> json) =>
      _$$MessageActionImplFromJson(json);

  @override
  final String id;
  @override
  final String label;
  @override
  final ActionType type;
  @override
  final String? payload;
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
    return 'MessageAction(id: $id, label: $label, type: $type, payload: $payload, data: $data)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$MessageActionImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.label, label) || other.label == label) &&
            (identical(other.type, type) || other.type == type) &&
            (identical(other.payload, payload) || other.payload == payload) &&
            const DeepCollectionEquality().equals(other._data, _data));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, id, label, type, payload,
      const DeepCollectionEquality().hash(_data));

  /// Create a copy of MessageAction
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$MessageActionImplCopyWith<_$MessageActionImpl> get copyWith =>
      __$$MessageActionImplCopyWithImpl<_$MessageActionImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$MessageActionImplToJson(
      this,
    );
  }
}

abstract class _MessageAction implements MessageAction {
  const factory _MessageAction(
      {required final String id,
      required final String label,
      required final ActionType type,
      final String? payload,
      final Map<String, dynamic>? data}) = _$MessageActionImpl;

  factory _MessageAction.fromJson(Map<String, dynamic> json) =
      _$MessageActionImpl.fromJson;

  @override
  String get id;
  @override
  String get label;
  @override
  ActionType get type;
  @override
  String? get payload;
  @override
  Map<String, dynamic>? get data;

  /// Create a copy of MessageAction
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$MessageActionImplCopyWith<_$MessageActionImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

AIRecommendation _$AIRecommendationFromJson(Map<String, dynamic> json) {
  return _AIRecommendation.fromJson(json);
}

/// @nodoc
mixin _$AIRecommendation {
  String get id => throw _privateConstructorUsedError;
  String get title => throw _privateConstructorUsedError;
  String get description => throw _privateConstructorUsedError;
  String get iconName => throw _privateConstructorUsedError;
  RecommendationType get type => throw _privateConstructorUsedError;
  double get confidence => throw _privateConstructorUsedError;
  String? get action => throw _privateConstructorUsedError;
  Map<String, dynamic>? get data => throw _privateConstructorUsedError;

  /// Serializes this AIRecommendation to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of AIRecommendation
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $AIRecommendationCopyWith<AIRecommendation> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AIRecommendationCopyWith<$Res> {
  factory $AIRecommendationCopyWith(
          AIRecommendation value, $Res Function(AIRecommendation) then) =
      _$AIRecommendationCopyWithImpl<$Res, AIRecommendation>;
  @useResult
  $Res call(
      {String id,
      String title,
      String description,
      String iconName,
      RecommendationType type,
      double confidence,
      String? action,
      Map<String, dynamic>? data});
}

/// @nodoc
class _$AIRecommendationCopyWithImpl<$Res, $Val extends AIRecommendation>
    implements $AIRecommendationCopyWith<$Res> {
  _$AIRecommendationCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of AIRecommendation
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? title = null,
    Object? description = null,
    Object? iconName = null,
    Object? type = null,
    Object? confidence = null,
    Object? action = freezed,
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
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      iconName: null == iconName
          ? _value.iconName
          : iconName // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as RecommendationType,
      confidence: null == confidence
          ? _value.confidence
          : confidence // ignore: cast_nullable_to_non_nullable
              as double,
      action: freezed == action
          ? _value.action
          : action // ignore: cast_nullable_to_non_nullable
              as String?,
      data: freezed == data
          ? _value.data
          : data // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$AIRecommendationImplCopyWith<$Res>
    implements $AIRecommendationCopyWith<$Res> {
  factory _$$AIRecommendationImplCopyWith(_$AIRecommendationImpl value,
          $Res Function(_$AIRecommendationImpl) then) =
      __$$AIRecommendationImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String title,
      String description,
      String iconName,
      RecommendationType type,
      double confidence,
      String? action,
      Map<String, dynamic>? data});
}

/// @nodoc
class __$$AIRecommendationImplCopyWithImpl<$Res>
    extends _$AIRecommendationCopyWithImpl<$Res, _$AIRecommendationImpl>
    implements _$$AIRecommendationImplCopyWith<$Res> {
  __$$AIRecommendationImplCopyWithImpl(_$AIRecommendationImpl _value,
      $Res Function(_$AIRecommendationImpl) _then)
      : super(_value, _then);

  /// Create a copy of AIRecommendation
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? title = null,
    Object? description = null,
    Object? iconName = null,
    Object? type = null,
    Object? confidence = null,
    Object? action = freezed,
    Object? data = freezed,
  }) {
    return _then(_$AIRecommendationImpl(
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
      iconName: null == iconName
          ? _value.iconName
          : iconName // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as RecommendationType,
      confidence: null == confidence
          ? _value.confidence
          : confidence // ignore: cast_nullable_to_non_nullable
              as double,
      action: freezed == action
          ? _value.action
          : action // ignore: cast_nullable_to_non_nullable
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
class _$AIRecommendationImpl implements _AIRecommendation {
  const _$AIRecommendationImpl(
      {required this.id,
      required this.title,
      required this.description,
      required this.iconName,
      required this.type,
      required this.confidence,
      this.action,
      final Map<String, dynamic>? data})
      : _data = data;

  factory _$AIRecommendationImpl.fromJson(Map<String, dynamic> json) =>
      _$$AIRecommendationImplFromJson(json);

  @override
  final String id;
  @override
  final String title;
  @override
  final String description;
  @override
  final String iconName;
  @override
  final RecommendationType type;
  @override
  final double confidence;
  @override
  final String? action;
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
    return 'AIRecommendation(id: $id, title: $title, description: $description, iconName: $iconName, type: $type, confidence: $confidence, action: $action, data: $data)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$AIRecommendationImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.iconName, iconName) ||
                other.iconName == iconName) &&
            (identical(other.type, type) || other.type == type) &&
            (identical(other.confidence, confidence) ||
                other.confidence == confidence) &&
            (identical(other.action, action) || other.action == action) &&
            const DeepCollectionEquality().equals(other._data, _data));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, id, title, description, iconName,
      type, confidence, action, const DeepCollectionEquality().hash(_data));

  /// Create a copy of AIRecommendation
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$AIRecommendationImplCopyWith<_$AIRecommendationImpl> get copyWith =>
      __$$AIRecommendationImplCopyWithImpl<_$AIRecommendationImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$AIRecommendationImplToJson(
      this,
    );
  }
}

abstract class _AIRecommendation implements AIRecommendation {
  const factory _AIRecommendation(
      {required final String id,
      required final String title,
      required final String description,
      required final String iconName,
      required final RecommendationType type,
      required final double confidence,
      final String? action,
      final Map<String, dynamic>? data}) = _$AIRecommendationImpl;

  factory _AIRecommendation.fromJson(Map<String, dynamic> json) =
      _$AIRecommendationImpl.fromJson;

  @override
  String get id;
  @override
  String get title;
  @override
  String get description;
  @override
  String get iconName;
  @override
  RecommendationType get type;
  @override
  double get confidence;
  @override
  String? get action;
  @override
  Map<String, dynamic>? get data;

  /// Create a copy of AIRecommendation
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$AIRecommendationImplCopyWith<_$AIRecommendationImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
