// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'api_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

DataItem _$DataItemFromJson(Map<String, dynamic> json) {
  return _DataItem.fromJson(json);
}

/// @nodoc
mixin _$DataItem {
  String get id => throw _privateConstructorUsedError;
  String get content => throw _privateConstructorUsedError;
  @JsonKey(name: 'source_connector')
  String get sourceConnector => throw _privateConstructorUsedError;
  DateTime get timestamp => throw _privateConstructorUsedError;
  @JsonKey(name: 'file_path')
  String? get filePath => throw _privateConstructorUsedError;
  Map<String, dynamic> get metadata => throw _privateConstructorUsedError;

  /// Serializes this DataItem to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of DataItem
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DataItemCopyWith<DataItem> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DataItemCopyWith<$Res> {
  factory $DataItemCopyWith(DataItem value, $Res Function(DataItem) then) =
      _$DataItemCopyWithImpl<$Res, DataItem>;
  @useResult
  $Res call(
      {String id,
      String content,
      @JsonKey(name: 'source_connector') String sourceConnector,
      DateTime timestamp,
      @JsonKey(name: 'file_path') String? filePath,
      Map<String, dynamic> metadata});
}

/// @nodoc
class _$DataItemCopyWithImpl<$Res, $Val extends DataItem>
    implements $DataItemCopyWith<$Res> {
  _$DataItemCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DataItem
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? content = null,
    Object? sourceConnector = null,
    Object? timestamp = null,
    Object? filePath = freezed,
    Object? metadata = null,
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
      sourceConnector: null == sourceConnector
          ? _value.sourceConnector
          : sourceConnector // ignore: cast_nullable_to_non_nullable
              as String,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      filePath: freezed == filePath
          ? _value.filePath
          : filePath // ignore: cast_nullable_to_non_nullable
              as String?,
      metadata: null == metadata
          ? _value.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DataItemImplCopyWith<$Res>
    implements $DataItemCopyWith<$Res> {
  factory _$$DataItemImplCopyWith(
          _$DataItemImpl value, $Res Function(_$DataItemImpl) then) =
      __$$DataItemImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String content,
      @JsonKey(name: 'source_connector') String sourceConnector,
      DateTime timestamp,
      @JsonKey(name: 'file_path') String? filePath,
      Map<String, dynamic> metadata});
}

/// @nodoc
class __$$DataItemImplCopyWithImpl<$Res>
    extends _$DataItemCopyWithImpl<$Res, _$DataItemImpl>
    implements _$$DataItemImplCopyWith<$Res> {
  __$$DataItemImplCopyWithImpl(
      _$DataItemImpl _value, $Res Function(_$DataItemImpl) _then)
      : super(_value, _then);

  /// Create a copy of DataItem
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? content = null,
    Object? sourceConnector = null,
    Object? timestamp = null,
    Object? filePath = freezed,
    Object? metadata = null,
  }) {
    return _then(_$DataItemImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      content: null == content
          ? _value.content
          : content // ignore: cast_nullable_to_non_nullable
              as String,
      sourceConnector: null == sourceConnector
          ? _value.sourceConnector
          : sourceConnector // ignore: cast_nullable_to_non_nullable
              as String,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      filePath: freezed == filePath
          ? _value.filePath
          : filePath // ignore: cast_nullable_to_non_nullable
              as String?,
      metadata: null == metadata
          ? _value._metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DataItemImpl implements _DataItem {
  const _$DataItemImpl(
      {required this.id,
      required this.content,
      @JsonKey(name: 'source_connector') required this.sourceConnector,
      required this.timestamp,
      @JsonKey(name: 'file_path') this.filePath,
      final Map<String, dynamic> metadata = const {}})
      : _metadata = metadata;

  factory _$DataItemImpl.fromJson(Map<String, dynamic> json) =>
      _$$DataItemImplFromJson(json);

  @override
  final String id;
  @override
  final String content;
  @override
  @JsonKey(name: 'source_connector')
  final String sourceConnector;
  @override
  final DateTime timestamp;
  @override
  @JsonKey(name: 'file_path')
  final String? filePath;
  final Map<String, dynamic> _metadata;
  @override
  @JsonKey()
  Map<String, dynamic> get metadata {
    if (_metadata is EqualUnmodifiableMapView) return _metadata;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_metadata);
  }

  @override
  String toString() {
    return 'DataItem(id: $id, content: $content, sourceConnector: $sourceConnector, timestamp: $timestamp, filePath: $filePath, metadata: $metadata)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DataItemImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.content, content) || other.content == content) &&
            (identical(other.sourceConnector, sourceConnector) ||
                other.sourceConnector == sourceConnector) &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp) &&
            (identical(other.filePath, filePath) ||
                other.filePath == filePath) &&
            const DeepCollectionEquality().equals(other._metadata, _metadata));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, id, content, sourceConnector,
      timestamp, filePath, const DeepCollectionEquality().hash(_metadata));

  /// Create a copy of DataItem
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DataItemImplCopyWith<_$DataItemImpl> get copyWith =>
      __$$DataItemImplCopyWithImpl<_$DataItemImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DataItemImplToJson(
      this,
    );
  }
}

abstract class _DataItem implements DataItem {
  const factory _DataItem(
      {required final String id,
      required final String content,
      @JsonKey(name: 'source_connector') required final String sourceConnector,
      required final DateTime timestamp,
      @JsonKey(name: 'file_path') final String? filePath,
      final Map<String, dynamic> metadata}) = _$DataItemImpl;

  factory _DataItem.fromJson(Map<String, dynamic> json) =
      _$DataItemImpl.fromJson;

  @override
  String get id;
  @override
  String get content;
  @override
  @JsonKey(name: 'source_connector')
  String get sourceConnector;
  @override
  DateTime get timestamp;
  @override
  @JsonKey(name: 'file_path')
  String? get filePath;
  @override
  Map<String, dynamic> get metadata;

  /// Create a copy of DataItem
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DataItemImplCopyWith<_$DataItemImpl> get copyWith =>
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
  double get confidence => throw _privateConstructorUsedError;
  @JsonKey(name: 'related_items')
  List<String> get relatedItems => throw _privateConstructorUsedError;
  @JsonKey(name: 'created_at')
  DateTime get createdAt => throw _privateConstructorUsedError;

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
      double confidence,
      @JsonKey(name: 'related_items') List<String> relatedItems,
      @JsonKey(name: 'created_at') DateTime createdAt});
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
    Object? confidence = null,
    Object? relatedItems = null,
    Object? createdAt = null,
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
      confidence: null == confidence
          ? _value.confidence
          : confidence // ignore: cast_nullable_to_non_nullable
              as double,
      relatedItems: null == relatedItems
          ? _value.relatedItems
          : relatedItems // ignore: cast_nullable_to_non_nullable
              as List<String>,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
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
      double confidence,
      @JsonKey(name: 'related_items') List<String> relatedItems,
      @JsonKey(name: 'created_at') DateTime createdAt});
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
    Object? confidence = null,
    Object? relatedItems = null,
    Object? createdAt = null,
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
      confidence: null == confidence
          ? _value.confidence
          : confidence // ignore: cast_nullable_to_non_nullable
              as double,
      relatedItems: null == relatedItems
          ? _value._relatedItems
          : relatedItems // ignore: cast_nullable_to_non_nullable
              as List<String>,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
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
      required this.confidence,
      @JsonKey(name: 'related_items')
      final List<String> relatedItems = const [],
      @JsonKey(name: 'created_at') required this.createdAt})
      : _relatedItems = relatedItems;

  factory _$AIRecommendationImpl.fromJson(Map<String, dynamic> json) =>
      _$$AIRecommendationImplFromJson(json);

  @override
  final String id;
  @override
  final String title;
  @override
  final String description;
  @override
  final double confidence;
  final List<String> _relatedItems;
  @override
  @JsonKey(name: 'related_items')
  List<String> get relatedItems {
    if (_relatedItems is EqualUnmodifiableListView) return _relatedItems;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_relatedItems);
  }

  @override
  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  @override
  String toString() {
    return 'AIRecommendation(id: $id, title: $title, description: $description, confidence: $confidence, relatedItems: $relatedItems, createdAt: $createdAt)';
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
            (identical(other.confidence, confidence) ||
                other.confidence == confidence) &&
            const DeepCollectionEquality()
                .equals(other._relatedItems, _relatedItems) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      title,
      description,
      confidence,
      const DeepCollectionEquality().hash(_relatedItems),
      createdAt);

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
          required final double confidence,
          @JsonKey(name: 'related_items') final List<String> relatedItems,
          @JsonKey(name: 'created_at') required final DateTime createdAt}) =
      _$AIRecommendationImpl;

  factory _AIRecommendation.fromJson(Map<String, dynamic> json) =
      _$AIRecommendationImpl.fromJson;

  @override
  String get id;
  @override
  String get title;
  @override
  String get description;
  @override
  double get confidence;
  @override
  @JsonKey(name: 'related_items')
  List<String> get relatedItems;
  @override
  @JsonKey(name: 'created_at')
  DateTime get createdAt;

  /// Create a copy of AIRecommendation
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$AIRecommendationImplCopyWith<_$AIRecommendationImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ApiResponse _$ApiResponseFromJson(Map<String, dynamic> json) {
  return _ApiResponse.fromJson(json);
}

/// @nodoc
mixin _$ApiResponse {
  bool get success => throw _privateConstructorUsedError;
  String get message => throw _privateConstructorUsedError;
  Object? get data => throw _privateConstructorUsedError;

  /// Serializes this ApiResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ApiResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ApiResponseCopyWith<ApiResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ApiResponseCopyWith<$Res> {
  factory $ApiResponseCopyWith(
          ApiResponse value, $Res Function(ApiResponse) then) =
      _$ApiResponseCopyWithImpl<$Res, ApiResponse>;
  @useResult
  $Res call({bool success, String message, Object? data});
}

/// @nodoc
class _$ApiResponseCopyWithImpl<$Res, $Val extends ApiResponse>
    implements $ApiResponseCopyWith<$Res> {
  _$ApiResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ApiResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? message = null,
    Object? data = freezed,
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
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ApiResponseImplCopyWith<$Res>
    implements $ApiResponseCopyWith<$Res> {
  factory _$$ApiResponseImplCopyWith(
          _$ApiResponseImpl value, $Res Function(_$ApiResponseImpl) then) =
      __$$ApiResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({bool success, String message, Object? data});
}

/// @nodoc
class __$$ApiResponseImplCopyWithImpl<$Res>
    extends _$ApiResponseCopyWithImpl<$Res, _$ApiResponseImpl>
    implements _$$ApiResponseImplCopyWith<$Res> {
  __$$ApiResponseImplCopyWithImpl(
      _$ApiResponseImpl _value, $Res Function(_$ApiResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of ApiResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? message = null,
    Object? data = freezed,
  }) {
    return _then(_$ApiResponseImpl(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
      data: freezed == data ? _value.data : data,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ApiResponseImpl implements _ApiResponse {
  const _$ApiResponseImpl(
      {required this.success, required this.message, this.data});

  factory _$ApiResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$ApiResponseImplFromJson(json);

  @override
  final bool success;
  @override
  final String message;
  @override
  final Object? data;

  @override
  String toString() {
    return 'ApiResponse(success: $success, message: $message, data: $data)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ApiResponseImpl &&
            (identical(other.success, success) || other.success == success) &&
            (identical(other.message, message) || other.message == message) &&
            const DeepCollectionEquality().equals(other.data, data));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType, success, message, const DeepCollectionEquality().hash(data));

  /// Create a copy of ApiResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ApiResponseImplCopyWith<_$ApiResponseImpl> get copyWith =>
      __$$ApiResponseImplCopyWithImpl<_$ApiResponseImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ApiResponseImplToJson(
      this,
    );
  }
}

abstract class _ApiResponse implements ApiResponse {
  const factory _ApiResponse(
      {required final bool success,
      required final String message,
      final Object? data}) = _$ApiResponseImpl;

  factory _ApiResponse.fromJson(Map<String, dynamic> json) =
      _$ApiResponseImpl.fromJson;

  @override
  bool get success;
  @override
  String get message;
  @override
  Object? get data;

  /// Create a copy of ApiResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ApiResponseImplCopyWith<_$ApiResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ServerInfo _$ServerInfoFromJson(Map<String, dynamic> json) {
  return _ServerInfo.fromJson(json);
}

/// @nodoc
mixin _$ServerInfo {
  String get version => throw _privateConstructorUsedError;
  int get port => throw _privateConstructorUsedError;
  @JsonKey(name: 'started_at')
  DateTime get startedAt => throw _privateConstructorUsedError;
  String get status => throw _privateConstructorUsedError;

  /// Serializes this ServerInfo to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ServerInfo
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ServerInfoCopyWith<ServerInfo> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ServerInfoCopyWith<$Res> {
  factory $ServerInfoCopyWith(
          ServerInfo value, $Res Function(ServerInfo) then) =
      _$ServerInfoCopyWithImpl<$Res, ServerInfo>;
  @useResult
  $Res call(
      {String version,
      int port,
      @JsonKey(name: 'started_at') DateTime startedAt,
      String status});
}

/// @nodoc
class _$ServerInfoCopyWithImpl<$Res, $Val extends ServerInfo>
    implements $ServerInfoCopyWith<$Res> {
  _$ServerInfoCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ServerInfo
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? version = null,
    Object? port = null,
    Object? startedAt = null,
    Object? status = null,
  }) {
    return _then(_value.copyWith(
      version: null == version
          ? _value.version
          : version // ignore: cast_nullable_to_non_nullable
              as String,
      port: null == port
          ? _value.port
          : port // ignore: cast_nullable_to_non_nullable
              as int,
      startedAt: null == startedAt
          ? _value.startedAt
          : startedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ServerInfoImplCopyWith<$Res>
    implements $ServerInfoCopyWith<$Res> {
  factory _$$ServerInfoImplCopyWith(
          _$ServerInfoImpl value, $Res Function(_$ServerInfoImpl) then) =
      __$$ServerInfoImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String version,
      int port,
      @JsonKey(name: 'started_at') DateTime startedAt,
      String status});
}

/// @nodoc
class __$$ServerInfoImplCopyWithImpl<$Res>
    extends _$ServerInfoCopyWithImpl<$Res, _$ServerInfoImpl>
    implements _$$ServerInfoImplCopyWith<$Res> {
  __$$ServerInfoImplCopyWithImpl(
      _$ServerInfoImpl _value, $Res Function(_$ServerInfoImpl) _then)
      : super(_value, _then);

  /// Create a copy of ServerInfo
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? version = null,
    Object? port = null,
    Object? startedAt = null,
    Object? status = null,
  }) {
    return _then(_$ServerInfoImpl(
      version: null == version
          ? _value.version
          : version // ignore: cast_nullable_to_non_nullable
              as String,
      port: null == port
          ? _value.port
          : port // ignore: cast_nullable_to_non_nullable
              as int,
      startedAt: null == startedAt
          ? _value.startedAt
          : startedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ServerInfoImpl implements _ServerInfo {
  const _$ServerInfoImpl(
      {required this.version,
      required this.port,
      @JsonKey(name: 'started_at') required this.startedAt,
      this.status = 'running'});

  factory _$ServerInfoImpl.fromJson(Map<String, dynamic> json) =>
      _$$ServerInfoImplFromJson(json);

  @override
  final String version;
  @override
  final int port;
  @override
  @JsonKey(name: 'started_at')
  final DateTime startedAt;
  @override
  @JsonKey()
  final String status;

  @override
  String toString() {
    return 'ServerInfo(version: $version, port: $port, startedAt: $startedAt, status: $status)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ServerInfoImpl &&
            (identical(other.version, version) || other.version == version) &&
            (identical(other.port, port) || other.port == port) &&
            (identical(other.startedAt, startedAt) ||
                other.startedAt == startedAt) &&
            (identical(other.status, status) || other.status == status));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, version, port, startedAt, status);

  /// Create a copy of ServerInfo
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ServerInfoImplCopyWith<_$ServerInfoImpl> get copyWith =>
      __$$ServerInfoImplCopyWithImpl<_$ServerInfoImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ServerInfoImplToJson(
      this,
    );
  }
}

abstract class _ServerInfo implements ServerInfo {
  const factory _ServerInfo(
      {required final String version,
      required final int port,
      @JsonKey(name: 'started_at') required final DateTime startedAt,
      final String status}) = _$ServerInfoImpl;

  factory _ServerInfo.fromJson(Map<String, dynamic> json) =
      _$ServerInfoImpl.fromJson;

  @override
  String get version;
  @override
  int get port;
  @override
  @JsonKey(name: 'started_at')
  DateTime get startedAt;
  @override
  String get status;

  /// Create a copy of ServerInfo
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ServerInfoImplCopyWith<_$ServerInfoImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

DatabaseStats _$DatabaseStatsFromJson(Map<String, dynamic> json) {
  return _DatabaseStats.fromJson(json);
}

/// @nodoc
mixin _$DatabaseStats {
  @JsonKey(name: 'total_items')
  int get totalItems => throw _privateConstructorUsedError;
  @JsonKey(name: 'connector_count')
  int get connectorCount => throw _privateConstructorUsedError;
  @JsonKey(name: 'graph_nodes')
  int get graphNodes => throw _privateConstructorUsedError;
  @JsonKey(name: 'graph_edges')
  int get graphEdges => throw _privateConstructorUsedError;

  /// Serializes this DatabaseStats to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of DatabaseStats
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DatabaseStatsCopyWith<DatabaseStats> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DatabaseStatsCopyWith<$Res> {
  factory $DatabaseStatsCopyWith(
          DatabaseStats value, $Res Function(DatabaseStats) then) =
      _$DatabaseStatsCopyWithImpl<$Res, DatabaseStats>;
  @useResult
  $Res call(
      {@JsonKey(name: 'total_items') int totalItems,
      @JsonKey(name: 'connector_count') int connectorCount,
      @JsonKey(name: 'graph_nodes') int graphNodes,
      @JsonKey(name: 'graph_edges') int graphEdges});
}

/// @nodoc
class _$DatabaseStatsCopyWithImpl<$Res, $Val extends DatabaseStats>
    implements $DatabaseStatsCopyWith<$Res> {
  _$DatabaseStatsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DatabaseStats
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalItems = null,
    Object? connectorCount = null,
    Object? graphNodes = null,
    Object? graphEdges = null,
  }) {
    return _then(_value.copyWith(
      totalItems: null == totalItems
          ? _value.totalItems
          : totalItems // ignore: cast_nullable_to_non_nullable
              as int,
      connectorCount: null == connectorCount
          ? _value.connectorCount
          : connectorCount // ignore: cast_nullable_to_non_nullable
              as int,
      graphNodes: null == graphNodes
          ? _value.graphNodes
          : graphNodes // ignore: cast_nullable_to_non_nullable
              as int,
      graphEdges: null == graphEdges
          ? _value.graphEdges
          : graphEdges // ignore: cast_nullable_to_non_nullable
              as int,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DatabaseStatsImplCopyWith<$Res>
    implements $DatabaseStatsCopyWith<$Res> {
  factory _$$DatabaseStatsImplCopyWith(
          _$DatabaseStatsImpl value, $Res Function(_$DatabaseStatsImpl) then) =
      __$$DatabaseStatsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'total_items') int totalItems,
      @JsonKey(name: 'connector_count') int connectorCount,
      @JsonKey(name: 'graph_nodes') int graphNodes,
      @JsonKey(name: 'graph_edges') int graphEdges});
}

/// @nodoc
class __$$DatabaseStatsImplCopyWithImpl<$Res>
    extends _$DatabaseStatsCopyWithImpl<$Res, _$DatabaseStatsImpl>
    implements _$$DatabaseStatsImplCopyWith<$Res> {
  __$$DatabaseStatsImplCopyWithImpl(
      _$DatabaseStatsImpl _value, $Res Function(_$DatabaseStatsImpl) _then)
      : super(_value, _then);

  /// Create a copy of DatabaseStats
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalItems = null,
    Object? connectorCount = null,
    Object? graphNodes = null,
    Object? graphEdges = null,
  }) {
    return _then(_$DatabaseStatsImpl(
      totalItems: null == totalItems
          ? _value.totalItems
          : totalItems // ignore: cast_nullable_to_non_nullable
              as int,
      connectorCount: null == connectorCount
          ? _value.connectorCount
          : connectorCount // ignore: cast_nullable_to_non_nullable
              as int,
      graphNodes: null == graphNodes
          ? _value.graphNodes
          : graphNodes // ignore: cast_nullable_to_non_nullable
              as int,
      graphEdges: null == graphEdges
          ? _value.graphEdges
          : graphEdges // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DatabaseStatsImpl implements _DatabaseStats {
  const _$DatabaseStatsImpl(
      {@JsonKey(name: 'total_items') required this.totalItems,
      @JsonKey(name: 'connector_count') required this.connectorCount,
      @JsonKey(name: 'graph_nodes') required this.graphNodes,
      @JsonKey(name: 'graph_edges') required this.graphEdges});

  factory _$DatabaseStatsImpl.fromJson(Map<String, dynamic> json) =>
      _$$DatabaseStatsImplFromJson(json);

  @override
  @JsonKey(name: 'total_items')
  final int totalItems;
  @override
  @JsonKey(name: 'connector_count')
  final int connectorCount;
  @override
  @JsonKey(name: 'graph_nodes')
  final int graphNodes;
  @override
  @JsonKey(name: 'graph_edges')
  final int graphEdges;

  @override
  String toString() {
    return 'DatabaseStats(totalItems: $totalItems, connectorCount: $connectorCount, graphNodes: $graphNodes, graphEdges: $graphEdges)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DatabaseStatsImpl &&
            (identical(other.totalItems, totalItems) ||
                other.totalItems == totalItems) &&
            (identical(other.connectorCount, connectorCount) ||
                other.connectorCount == connectorCount) &&
            (identical(other.graphNodes, graphNodes) ||
                other.graphNodes == graphNodes) &&
            (identical(other.graphEdges, graphEdges) ||
                other.graphEdges == graphEdges));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType, totalItems, connectorCount, graphNodes, graphEdges);

  /// Create a copy of DatabaseStats
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DatabaseStatsImplCopyWith<_$DatabaseStatsImpl> get copyWith =>
      __$$DatabaseStatsImplCopyWithImpl<_$DatabaseStatsImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DatabaseStatsImplToJson(
      this,
    );
  }
}

abstract class _DatabaseStats implements DatabaseStats {
  const factory _DatabaseStats(
          {@JsonKey(name: 'total_items') required final int totalItems,
          @JsonKey(name: 'connector_count') required final int connectorCount,
          @JsonKey(name: 'graph_nodes') required final int graphNodes,
          @JsonKey(name: 'graph_edges') required final int graphEdges}) =
      _$DatabaseStatsImpl;

  factory _DatabaseStats.fromJson(Map<String, dynamic> json) =
      _$DatabaseStatsImpl.fromJson;

  @override
  @JsonKey(name: 'total_items')
  int get totalItems;
  @override
  @JsonKey(name: 'connector_count')
  int get connectorCount;
  @override
  @JsonKey(name: 'graph_nodes')
  int get graphNodes;
  @override
  @JsonKey(name: 'graph_edges')
  int get graphEdges;

  /// Create a copy of DatabaseStats
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DatabaseStatsImplCopyWith<_$DatabaseStatsImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

GraphNode _$GraphNodeFromJson(Map<String, dynamic> json) {
  return _GraphNode.fromJson(json);
}

/// @nodoc
mixin _$GraphNode {
  String get id => throw _privateConstructorUsedError;
  String get label => throw _privateConstructorUsedError;
  String get type => throw _privateConstructorUsedError;
  Map<String, dynamic> get properties => throw _privateConstructorUsedError;

  /// Serializes this GraphNode to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of GraphNode
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $GraphNodeCopyWith<GraphNode> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $GraphNodeCopyWith<$Res> {
  factory $GraphNodeCopyWith(GraphNode value, $Res Function(GraphNode) then) =
      _$GraphNodeCopyWithImpl<$Res, GraphNode>;
  @useResult
  $Res call(
      {String id, String label, String type, Map<String, dynamic> properties});
}

/// @nodoc
class _$GraphNodeCopyWithImpl<$Res, $Val extends GraphNode>
    implements $GraphNodeCopyWith<$Res> {
  _$GraphNodeCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of GraphNode
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? label = null,
    Object? type = null,
    Object? properties = null,
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
      properties: null == properties
          ? _value.properties
          : properties // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$GraphNodeImplCopyWith<$Res>
    implements $GraphNodeCopyWith<$Res> {
  factory _$$GraphNodeImplCopyWith(
          _$GraphNodeImpl value, $Res Function(_$GraphNodeImpl) then) =
      __$$GraphNodeImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id, String label, String type, Map<String, dynamic> properties});
}

/// @nodoc
class __$$GraphNodeImplCopyWithImpl<$Res>
    extends _$GraphNodeCopyWithImpl<$Res, _$GraphNodeImpl>
    implements _$$GraphNodeImplCopyWith<$Res> {
  __$$GraphNodeImplCopyWithImpl(
      _$GraphNodeImpl _value, $Res Function(_$GraphNodeImpl) _then)
      : super(_value, _then);

  /// Create a copy of GraphNode
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? label = null,
    Object? type = null,
    Object? properties = null,
  }) {
    return _then(_$GraphNodeImpl(
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
      properties: null == properties
          ? _value._properties
          : properties // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$GraphNodeImpl implements _GraphNode {
  const _$GraphNodeImpl(
      {required this.id,
      required this.label,
      required this.type,
      final Map<String, dynamic> properties = const {}})
      : _properties = properties;

  factory _$GraphNodeImpl.fromJson(Map<String, dynamic> json) =>
      _$$GraphNodeImplFromJson(json);

  @override
  final String id;
  @override
  final String label;
  @override
  final String type;
  final Map<String, dynamic> _properties;
  @override
  @JsonKey()
  Map<String, dynamic> get properties {
    if (_properties is EqualUnmodifiableMapView) return _properties;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_properties);
  }

  @override
  String toString() {
    return 'GraphNode(id: $id, label: $label, type: $type, properties: $properties)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$GraphNodeImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.label, label) || other.label == label) &&
            (identical(other.type, type) || other.type == type) &&
            const DeepCollectionEquality()
                .equals(other._properties, _properties));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, id, label, type,
      const DeepCollectionEquality().hash(_properties));

  /// Create a copy of GraphNode
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$GraphNodeImplCopyWith<_$GraphNodeImpl> get copyWith =>
      __$$GraphNodeImplCopyWithImpl<_$GraphNodeImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$GraphNodeImplToJson(
      this,
    );
  }
}

abstract class _GraphNode implements GraphNode {
  const factory _GraphNode(
      {required final String id,
      required final String label,
      required final String type,
      final Map<String, dynamic> properties}) = _$GraphNodeImpl;

  factory _GraphNode.fromJson(Map<String, dynamic> json) =
      _$GraphNodeImpl.fromJson;

  @override
  String get id;
  @override
  String get label;
  @override
  String get type;
  @override
  Map<String, dynamic> get properties;

  /// Create a copy of GraphNode
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$GraphNodeImplCopyWith<_$GraphNodeImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

GraphEdge _$GraphEdgeFromJson(Map<String, dynamic> json) {
  return _GraphEdge.fromJson(json);
}

/// @nodoc
mixin _$GraphEdge {
  String get id => throw _privateConstructorUsedError;
  String get source => throw _privateConstructorUsedError;
  String get target => throw _privateConstructorUsedError;
  String get type => throw _privateConstructorUsedError;
  double get weight => throw _privateConstructorUsedError;

  /// Serializes this GraphEdge to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of GraphEdge
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $GraphEdgeCopyWith<GraphEdge> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $GraphEdgeCopyWith<$Res> {
  factory $GraphEdgeCopyWith(GraphEdge value, $Res Function(GraphEdge) then) =
      _$GraphEdgeCopyWithImpl<$Res, GraphEdge>;
  @useResult
  $Res call(
      {String id, String source, String target, String type, double weight});
}

/// @nodoc
class _$GraphEdgeCopyWithImpl<$Res, $Val extends GraphEdge>
    implements $GraphEdgeCopyWith<$Res> {
  _$GraphEdgeCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of GraphEdge
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? source = null,
    Object? target = null,
    Object? type = null,
    Object? weight = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      source: null == source
          ? _value.source
          : source // ignore: cast_nullable_to_non_nullable
              as String,
      target: null == target
          ? _value.target
          : target // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      weight: null == weight
          ? _value.weight
          : weight // ignore: cast_nullable_to_non_nullable
              as double,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$GraphEdgeImplCopyWith<$Res>
    implements $GraphEdgeCopyWith<$Res> {
  factory _$$GraphEdgeImplCopyWith(
          _$GraphEdgeImpl value, $Res Function(_$GraphEdgeImpl) then) =
      __$$GraphEdgeImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id, String source, String target, String type, double weight});
}

/// @nodoc
class __$$GraphEdgeImplCopyWithImpl<$Res>
    extends _$GraphEdgeCopyWithImpl<$Res, _$GraphEdgeImpl>
    implements _$$GraphEdgeImplCopyWith<$Res> {
  __$$GraphEdgeImplCopyWithImpl(
      _$GraphEdgeImpl _value, $Res Function(_$GraphEdgeImpl) _then)
      : super(_value, _then);

  /// Create a copy of GraphEdge
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? source = null,
    Object? target = null,
    Object? type = null,
    Object? weight = null,
  }) {
    return _then(_$GraphEdgeImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      source: null == source
          ? _value.source
          : source // ignore: cast_nullable_to_non_nullable
              as String,
      target: null == target
          ? _value.target
          : target // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      weight: null == weight
          ? _value.weight
          : weight // ignore: cast_nullable_to_non_nullable
              as double,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$GraphEdgeImpl implements _GraphEdge {
  const _$GraphEdgeImpl(
      {required this.id,
      required this.source,
      required this.target,
      required this.type,
      this.weight = 1.0});

  factory _$GraphEdgeImpl.fromJson(Map<String, dynamic> json) =>
      _$$GraphEdgeImplFromJson(json);

  @override
  final String id;
  @override
  final String source;
  @override
  final String target;
  @override
  final String type;
  @override
  @JsonKey()
  final double weight;

  @override
  String toString() {
    return 'GraphEdge(id: $id, source: $source, target: $target, type: $type, weight: $weight)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$GraphEdgeImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.source, source) || other.source == source) &&
            (identical(other.target, target) || other.target == target) &&
            (identical(other.type, type) || other.type == type) &&
            (identical(other.weight, weight) || other.weight == weight));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, id, source, target, type, weight);

  /// Create a copy of GraphEdge
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$GraphEdgeImplCopyWith<_$GraphEdgeImpl> get copyWith =>
      __$$GraphEdgeImplCopyWithImpl<_$GraphEdgeImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$GraphEdgeImplToJson(
      this,
    );
  }
}

abstract class _GraphEdge implements GraphEdge {
  const factory _GraphEdge(
      {required final String id,
      required final String source,
      required final String target,
      required final String type,
      final double weight}) = _$GraphEdgeImpl;

  factory _GraphEdge.fromJson(Map<String, dynamic> json) =
      _$GraphEdgeImpl.fromJson;

  @override
  String get id;
  @override
  String get source;
  @override
  String get target;
  @override
  String get type;
  @override
  double get weight;

  /// Create a copy of GraphEdge
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$GraphEdgeImplCopyWith<_$GraphEdgeImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

SystemDiagnostics _$SystemDiagnosticsFromJson(Map<String, dynamic> json) {
  return _SystemDiagnostics.fromJson(json);
}

/// @nodoc
mixin _$SystemDiagnostics {
  @JsonKey(name: 'overall_status')
  String get overallStatus => throw _privateConstructorUsedError;
  @JsonKey(name: 'daemon_status')
  String get daemonStatus => throw _privateConstructorUsedError;
  @JsonKey(name: 'database_status')
  String get databaseStatus => throw _privateConstructorUsedError;
  @JsonKey(name: 'connector_summary')
  Map<String, dynamic> get connectorSummary =>
      throw _privateConstructorUsedError;
  @JsonKey(name: 'system_resources')
  Map<String, dynamic> get systemResources =>
      throw _privateConstructorUsedError;
  @JsonKey(name: 'error_summary')
  List<String> get errorSummary => throw _privateConstructorUsedError;
  @JsonKey(name: 'last_check')
  DateTime get lastCheck => throw _privateConstructorUsedError;

  /// Serializes this SystemDiagnostics to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of SystemDiagnostics
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SystemDiagnosticsCopyWith<SystemDiagnostics> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SystemDiagnosticsCopyWith<$Res> {
  factory $SystemDiagnosticsCopyWith(
          SystemDiagnostics value, $Res Function(SystemDiagnostics) then) =
      _$SystemDiagnosticsCopyWithImpl<$Res, SystemDiagnostics>;
  @useResult
  $Res call(
      {@JsonKey(name: 'overall_status') String overallStatus,
      @JsonKey(name: 'daemon_status') String daemonStatus,
      @JsonKey(name: 'database_status') String databaseStatus,
      @JsonKey(name: 'connector_summary') Map<String, dynamic> connectorSummary,
      @JsonKey(name: 'system_resources') Map<String, dynamic> systemResources,
      @JsonKey(name: 'error_summary') List<String> errorSummary,
      @JsonKey(name: 'last_check') DateTime lastCheck});
}

/// @nodoc
class _$SystemDiagnosticsCopyWithImpl<$Res, $Val extends SystemDiagnostics>
    implements $SystemDiagnosticsCopyWith<$Res> {
  _$SystemDiagnosticsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of SystemDiagnostics
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? overallStatus = null,
    Object? daemonStatus = null,
    Object? databaseStatus = null,
    Object? connectorSummary = null,
    Object? systemResources = null,
    Object? errorSummary = null,
    Object? lastCheck = null,
  }) {
    return _then(_value.copyWith(
      overallStatus: null == overallStatus
          ? _value.overallStatus
          : overallStatus // ignore: cast_nullable_to_non_nullable
              as String,
      daemonStatus: null == daemonStatus
          ? _value.daemonStatus
          : daemonStatus // ignore: cast_nullable_to_non_nullable
              as String,
      databaseStatus: null == databaseStatus
          ? _value.databaseStatus
          : databaseStatus // ignore: cast_nullable_to_non_nullable
              as String,
      connectorSummary: null == connectorSummary
          ? _value.connectorSummary
          : connectorSummary // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      systemResources: null == systemResources
          ? _value.systemResources
          : systemResources // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      errorSummary: null == errorSummary
          ? _value.errorSummary
          : errorSummary // ignore: cast_nullable_to_non_nullable
              as List<String>,
      lastCheck: null == lastCheck
          ? _value.lastCheck
          : lastCheck // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$SystemDiagnosticsImplCopyWith<$Res>
    implements $SystemDiagnosticsCopyWith<$Res> {
  factory _$$SystemDiagnosticsImplCopyWith(_$SystemDiagnosticsImpl value,
          $Res Function(_$SystemDiagnosticsImpl) then) =
      __$$SystemDiagnosticsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'overall_status') String overallStatus,
      @JsonKey(name: 'daemon_status') String daemonStatus,
      @JsonKey(name: 'database_status') String databaseStatus,
      @JsonKey(name: 'connector_summary') Map<String, dynamic> connectorSummary,
      @JsonKey(name: 'system_resources') Map<String, dynamic> systemResources,
      @JsonKey(name: 'error_summary') List<String> errorSummary,
      @JsonKey(name: 'last_check') DateTime lastCheck});
}

/// @nodoc
class __$$SystemDiagnosticsImplCopyWithImpl<$Res>
    extends _$SystemDiagnosticsCopyWithImpl<$Res, _$SystemDiagnosticsImpl>
    implements _$$SystemDiagnosticsImplCopyWith<$Res> {
  __$$SystemDiagnosticsImplCopyWithImpl(_$SystemDiagnosticsImpl _value,
      $Res Function(_$SystemDiagnosticsImpl) _then)
      : super(_value, _then);

  /// Create a copy of SystemDiagnostics
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? overallStatus = null,
    Object? daemonStatus = null,
    Object? databaseStatus = null,
    Object? connectorSummary = null,
    Object? systemResources = null,
    Object? errorSummary = null,
    Object? lastCheck = null,
  }) {
    return _then(_$SystemDiagnosticsImpl(
      overallStatus: null == overallStatus
          ? _value.overallStatus
          : overallStatus // ignore: cast_nullable_to_non_nullable
              as String,
      daemonStatus: null == daemonStatus
          ? _value.daemonStatus
          : daemonStatus // ignore: cast_nullable_to_non_nullable
              as String,
      databaseStatus: null == databaseStatus
          ? _value.databaseStatus
          : databaseStatus // ignore: cast_nullable_to_non_nullable
              as String,
      connectorSummary: null == connectorSummary
          ? _value._connectorSummary
          : connectorSummary // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      systemResources: null == systemResources
          ? _value._systemResources
          : systemResources // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      errorSummary: null == errorSummary
          ? _value._errorSummary
          : errorSummary // ignore: cast_nullable_to_non_nullable
              as List<String>,
      lastCheck: null == lastCheck
          ? _value.lastCheck
          : lastCheck // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$SystemDiagnosticsImpl implements _SystemDiagnostics {
  const _$SystemDiagnosticsImpl(
      {@JsonKey(name: 'overall_status') required this.overallStatus,
      @JsonKey(name: 'daemon_status') required this.daemonStatus,
      @JsonKey(name: 'database_status') required this.databaseStatus,
      @JsonKey(name: 'connector_summary')
      final Map<String, dynamic> connectorSummary = const {},
      @JsonKey(name: 'system_resources')
      final Map<String, dynamic> systemResources = const {},
      @JsonKey(name: 'error_summary')
      final List<String> errorSummary = const [],
      @JsonKey(name: 'last_check') required this.lastCheck})
      : _connectorSummary = connectorSummary,
        _systemResources = systemResources,
        _errorSummary = errorSummary;

  factory _$SystemDiagnosticsImpl.fromJson(Map<String, dynamic> json) =>
      _$$SystemDiagnosticsImplFromJson(json);

  @override
  @JsonKey(name: 'overall_status')
  final String overallStatus;
  @override
  @JsonKey(name: 'daemon_status')
  final String daemonStatus;
  @override
  @JsonKey(name: 'database_status')
  final String databaseStatus;
  final Map<String, dynamic> _connectorSummary;
  @override
  @JsonKey(name: 'connector_summary')
  Map<String, dynamic> get connectorSummary {
    if (_connectorSummary is EqualUnmodifiableMapView) return _connectorSummary;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_connectorSummary);
  }

  final Map<String, dynamic> _systemResources;
  @override
  @JsonKey(name: 'system_resources')
  Map<String, dynamic> get systemResources {
    if (_systemResources is EqualUnmodifiableMapView) return _systemResources;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_systemResources);
  }

  final List<String> _errorSummary;
  @override
  @JsonKey(name: 'error_summary')
  List<String> get errorSummary {
    if (_errorSummary is EqualUnmodifiableListView) return _errorSummary;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_errorSummary);
  }

  @override
  @JsonKey(name: 'last_check')
  final DateTime lastCheck;

  @override
  String toString() {
    return 'SystemDiagnostics(overallStatus: $overallStatus, daemonStatus: $daemonStatus, databaseStatus: $databaseStatus, connectorSummary: $connectorSummary, systemResources: $systemResources, errorSummary: $errorSummary, lastCheck: $lastCheck)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SystemDiagnosticsImpl &&
            (identical(other.overallStatus, overallStatus) ||
                other.overallStatus == overallStatus) &&
            (identical(other.daemonStatus, daemonStatus) ||
                other.daemonStatus == daemonStatus) &&
            (identical(other.databaseStatus, databaseStatus) ||
                other.databaseStatus == databaseStatus) &&
            const DeepCollectionEquality()
                .equals(other._connectorSummary, _connectorSummary) &&
            const DeepCollectionEquality()
                .equals(other._systemResources, _systemResources) &&
            const DeepCollectionEquality()
                .equals(other._errorSummary, _errorSummary) &&
            (identical(other.lastCheck, lastCheck) ||
                other.lastCheck == lastCheck));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      overallStatus,
      daemonStatus,
      databaseStatus,
      const DeepCollectionEquality().hash(_connectorSummary),
      const DeepCollectionEquality().hash(_systemResources),
      const DeepCollectionEquality().hash(_errorSummary),
      lastCheck);

  /// Create a copy of SystemDiagnostics
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SystemDiagnosticsImplCopyWith<_$SystemDiagnosticsImpl> get copyWith =>
      __$$SystemDiagnosticsImplCopyWithImpl<_$SystemDiagnosticsImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SystemDiagnosticsImplToJson(
      this,
    );
  }
}

abstract class _SystemDiagnostics implements SystemDiagnostics {
  const factory _SystemDiagnostics(
      {@JsonKey(name: 'overall_status') required final String overallStatus,
      @JsonKey(name: 'daemon_status') required final String daemonStatus,
      @JsonKey(name: 'database_status') required final String databaseStatus,
      @JsonKey(name: 'connector_summary')
      final Map<String, dynamic> connectorSummary,
      @JsonKey(name: 'system_resources')
      final Map<String, dynamic> systemResources,
      @JsonKey(name: 'error_summary') final List<String> errorSummary,
      @JsonKey(name: 'last_check')
      required final DateTime lastCheck}) = _$SystemDiagnosticsImpl;

  factory _SystemDiagnostics.fromJson(Map<String, dynamic> json) =
      _$SystemDiagnosticsImpl.fromJson;

  @override
  @JsonKey(name: 'overall_status')
  String get overallStatus;
  @override
  @JsonKey(name: 'daemon_status')
  String get daemonStatus;
  @override
  @JsonKey(name: 'database_status')
  String get databaseStatus;
  @override
  @JsonKey(name: 'connector_summary')
  Map<String, dynamic> get connectorSummary;
  @override
  @JsonKey(name: 'system_resources')
  Map<String, dynamic> get systemResources;
  @override
  @JsonKey(name: 'error_summary')
  List<String> get errorSummary;
  @override
  @JsonKey(name: 'last_check')
  DateTime get lastCheck;

  /// Create a copy of SystemDiagnostics
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SystemDiagnosticsImplCopyWith<_$SystemDiagnosticsImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
