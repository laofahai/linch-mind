// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'ipc_protocol.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

IPCError _$IPCErrorFromJson(Map<String, dynamic> json) {
  return _IPCError.fromJson(json);
}

/// @nodoc
mixin _$IPCError {
  String get code => throw _privateConstructorUsedError;
  String get message => throw _privateConstructorUsedError;
  Map<String, dynamic>? get details => throw _privateConstructorUsedError;

  /// Serializes this IPCError to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of IPCError
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $IPCErrorCopyWith<IPCError> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $IPCErrorCopyWith<$Res> {
  factory $IPCErrorCopyWith(IPCError value, $Res Function(IPCError) then) =
      _$IPCErrorCopyWithImpl<$Res, IPCError>;
  @useResult
  $Res call({String code, String message, Map<String, dynamic>? details});
}

/// @nodoc
class _$IPCErrorCopyWithImpl<$Res, $Val extends IPCError>
    implements $IPCErrorCopyWith<$Res> {
  _$IPCErrorCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of IPCError
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? code = null,
    Object? message = null,
    Object? details = freezed,
  }) {
    return _then(_value.copyWith(
      code: null == code
          ? _value.code
          : code // ignore: cast_nullable_to_non_nullable
              as String,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
      details: freezed == details
          ? _value.details
          : details // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$IPCErrorImplCopyWith<$Res>
    implements $IPCErrorCopyWith<$Res> {
  factory _$$IPCErrorImplCopyWith(
          _$IPCErrorImpl value, $Res Function(_$IPCErrorImpl) then) =
      __$$IPCErrorImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String code, String message, Map<String, dynamic>? details});
}

/// @nodoc
class __$$IPCErrorImplCopyWithImpl<$Res>
    extends _$IPCErrorCopyWithImpl<$Res, _$IPCErrorImpl>
    implements _$$IPCErrorImplCopyWith<$Res> {
  __$$IPCErrorImplCopyWithImpl(
      _$IPCErrorImpl _value, $Res Function(_$IPCErrorImpl) _then)
      : super(_value, _then);

  /// Create a copy of IPCError
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? code = null,
    Object? message = null,
    Object? details = freezed,
  }) {
    return _then(_$IPCErrorImpl(
      code: null == code
          ? _value.code
          : code // ignore: cast_nullable_to_non_nullable
              as String,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
      details: freezed == details
          ? _value._details
          : details // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$IPCErrorImpl implements _IPCError {
  const _$IPCErrorImpl(
      {required this.code,
      required this.message,
      final Map<String, dynamic>? details})
      : _details = details;

  factory _$IPCErrorImpl.fromJson(Map<String, dynamic> json) =>
      _$$IPCErrorImplFromJson(json);

  @override
  final String code;
  @override
  final String message;
  final Map<String, dynamic>? _details;
  @override
  Map<String, dynamic>? get details {
    final value = _details;
    if (value == null) return null;
    if (_details is EqualUnmodifiableMapView) return _details;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'IPCError(code: $code, message: $message, details: $details)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$IPCErrorImpl &&
            (identical(other.code, code) || other.code == code) &&
            (identical(other.message, message) || other.message == message) &&
            const DeepCollectionEquality().equals(other._details, _details));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, code, message,
      const DeepCollectionEquality().hash(_details));

  /// Create a copy of IPCError
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$IPCErrorImplCopyWith<_$IPCErrorImpl> get copyWith =>
      __$$IPCErrorImplCopyWithImpl<_$IPCErrorImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$IPCErrorImplToJson(
      this,
    );
  }
}

abstract class _IPCError implements IPCError {
  const factory _IPCError(
      {required final String code,
      required final String message,
      final Map<String, dynamic>? details}) = _$IPCErrorImpl;

  factory _IPCError.fromJson(Map<String, dynamic> json) =
      _$IPCErrorImpl.fromJson;

  @override
  String get code;
  @override
  String get message;
  @override
  Map<String, dynamic>? get details;

  /// Create a copy of IPCError
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$IPCErrorImplCopyWith<_$IPCErrorImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

IPCMetadata _$IPCMetadataFromJson(Map<String, dynamic> json) {
  return _IPCMetadata.fromJson(json);
}

/// @nodoc
mixin _$IPCMetadata {
  String get timestamp => throw _privateConstructorUsedError;
  @JsonKey(name: 'request_id')
  String? get requestId => throw _privateConstructorUsedError;

  /// Serializes this IPCMetadata to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of IPCMetadata
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $IPCMetadataCopyWith<IPCMetadata> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $IPCMetadataCopyWith<$Res> {
  factory $IPCMetadataCopyWith(
          IPCMetadata value, $Res Function(IPCMetadata) then) =
      _$IPCMetadataCopyWithImpl<$Res, IPCMetadata>;
  @useResult
  $Res call({String timestamp, @JsonKey(name: 'request_id') String? requestId});
}

/// @nodoc
class _$IPCMetadataCopyWithImpl<$Res, $Val extends IPCMetadata>
    implements $IPCMetadataCopyWith<$Res> {
  _$IPCMetadataCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of IPCMetadata
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? timestamp = null,
    Object? requestId = freezed,
  }) {
    return _then(_value.copyWith(
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as String,
      requestId: freezed == requestId
          ? _value.requestId
          : requestId // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$IPCMetadataImplCopyWith<$Res>
    implements $IPCMetadataCopyWith<$Res> {
  factory _$$IPCMetadataImplCopyWith(
          _$IPCMetadataImpl value, $Res Function(_$IPCMetadataImpl) then) =
      __$$IPCMetadataImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String timestamp, @JsonKey(name: 'request_id') String? requestId});
}

/// @nodoc
class __$$IPCMetadataImplCopyWithImpl<$Res>
    extends _$IPCMetadataCopyWithImpl<$Res, _$IPCMetadataImpl>
    implements _$$IPCMetadataImplCopyWith<$Res> {
  __$$IPCMetadataImplCopyWithImpl(
      _$IPCMetadataImpl _value, $Res Function(_$IPCMetadataImpl) _then)
      : super(_value, _then);

  /// Create a copy of IPCMetadata
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? timestamp = null,
    Object? requestId = freezed,
  }) {
    return _then(_$IPCMetadataImpl(
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as String,
      requestId: freezed == requestId
          ? _value.requestId
          : requestId // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$IPCMetadataImpl implements _IPCMetadata {
  const _$IPCMetadataImpl(
      {required this.timestamp, @JsonKey(name: 'request_id') this.requestId});

  factory _$IPCMetadataImpl.fromJson(Map<String, dynamic> json) =>
      _$$IPCMetadataImplFromJson(json);

  @override
  final String timestamp;
  @override
  @JsonKey(name: 'request_id')
  final String? requestId;

  @override
  String toString() {
    return 'IPCMetadata(timestamp: $timestamp, requestId: $requestId)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$IPCMetadataImpl &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp) &&
            (identical(other.requestId, requestId) ||
                other.requestId == requestId));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, timestamp, requestId);

  /// Create a copy of IPCMetadata
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$IPCMetadataImplCopyWith<_$IPCMetadataImpl> get copyWith =>
      __$$IPCMetadataImplCopyWithImpl<_$IPCMetadataImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$IPCMetadataImplToJson(
      this,
    );
  }
}

abstract class _IPCMetadata implements IPCMetadata {
  const factory _IPCMetadata(
          {required final String timestamp,
          @JsonKey(name: 'request_id') final String? requestId}) =
      _$IPCMetadataImpl;

  factory _IPCMetadata.fromJson(Map<String, dynamic> json) =
      _$IPCMetadataImpl.fromJson;

  @override
  String get timestamp;
  @override
  @JsonKey(name: 'request_id')
  String? get requestId;

  /// Create a copy of IPCMetadata
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$IPCMetadataImplCopyWith<_$IPCMetadataImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

IPCResponse _$IPCResponseFromJson(Map<String, dynamic> json) {
  return _IPCResponse.fromJson(json);
}

/// @nodoc
mixin _$IPCResponse {
  bool get success => throw _privateConstructorUsedError;
  dynamic get data =>
      throw _privateConstructorUsedError; // 允许任何类型的data，包括Map、List等
  IPCError? get error => throw _privateConstructorUsedError;
  IPCMetadata? get metadata => throw _privateConstructorUsedError;

  /// Serializes this IPCResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of IPCResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $IPCResponseCopyWith<IPCResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $IPCResponseCopyWith<$Res> {
  factory $IPCResponseCopyWith(
          IPCResponse value, $Res Function(IPCResponse) then) =
      _$IPCResponseCopyWithImpl<$Res, IPCResponse>;
  @useResult
  $Res call(
      {bool success, dynamic data, IPCError? error, IPCMetadata? metadata});

  $IPCErrorCopyWith<$Res>? get error;
  $IPCMetadataCopyWith<$Res>? get metadata;
}

/// @nodoc
class _$IPCResponseCopyWithImpl<$Res, $Val extends IPCResponse>
    implements $IPCResponseCopyWith<$Res> {
  _$IPCResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of IPCResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? data = freezed,
    Object? error = freezed,
    Object? metadata = freezed,
  }) {
    return _then(_value.copyWith(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      data: freezed == data
          ? _value.data
          : data // ignore: cast_nullable_to_non_nullable
              as dynamic,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as IPCError?,
      metadata: freezed == metadata
          ? _value.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as IPCMetadata?,
    ) as $Val);
  }

  /// Create a copy of IPCResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $IPCErrorCopyWith<$Res>? get error {
    if (_value.error == null) {
      return null;
    }

    return $IPCErrorCopyWith<$Res>(_value.error!, (value) {
      return _then(_value.copyWith(error: value) as $Val);
    });
  }

  /// Create a copy of IPCResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $IPCMetadataCopyWith<$Res>? get metadata {
    if (_value.metadata == null) {
      return null;
    }

    return $IPCMetadataCopyWith<$Res>(_value.metadata!, (value) {
      return _then(_value.copyWith(metadata: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$IPCResponseImplCopyWith<$Res>
    implements $IPCResponseCopyWith<$Res> {
  factory _$$IPCResponseImplCopyWith(
          _$IPCResponseImpl value, $Res Function(_$IPCResponseImpl) then) =
      __$$IPCResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {bool success, dynamic data, IPCError? error, IPCMetadata? metadata});

  @override
  $IPCErrorCopyWith<$Res>? get error;
  @override
  $IPCMetadataCopyWith<$Res>? get metadata;
}

/// @nodoc
class __$$IPCResponseImplCopyWithImpl<$Res>
    extends _$IPCResponseCopyWithImpl<$Res, _$IPCResponseImpl>
    implements _$$IPCResponseImplCopyWith<$Res> {
  __$$IPCResponseImplCopyWithImpl(
      _$IPCResponseImpl _value, $Res Function(_$IPCResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of IPCResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? data = freezed,
    Object? error = freezed,
    Object? metadata = freezed,
  }) {
    return _then(_$IPCResponseImpl(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      data: freezed == data
          ? _value.data
          : data // ignore: cast_nullable_to_non_nullable
              as dynamic,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as IPCError?,
      metadata: freezed == metadata
          ? _value.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as IPCMetadata?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$IPCResponseImpl implements _IPCResponse {
  const _$IPCResponseImpl(
      {required this.success, this.data, this.error, this.metadata});

  factory _$IPCResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$IPCResponseImplFromJson(json);

  @override
  final bool success;
  @override
  final dynamic data;
// 允许任何类型的data，包括Map、List等
  @override
  final IPCError? error;
  @override
  final IPCMetadata? metadata;

  @override
  String toString() {
    return 'IPCResponse(success: $success, data: $data, error: $error, metadata: $metadata)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$IPCResponseImpl &&
            (identical(other.success, success) || other.success == success) &&
            const DeepCollectionEquality().equals(other.data, data) &&
            (identical(other.error, error) || other.error == error) &&
            (identical(other.metadata, metadata) ||
                other.metadata == metadata));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, success,
      const DeepCollectionEquality().hash(data), error, metadata);

  /// Create a copy of IPCResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$IPCResponseImplCopyWith<_$IPCResponseImpl> get copyWith =>
      __$$IPCResponseImplCopyWithImpl<_$IPCResponseImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$IPCResponseImplToJson(
      this,
    );
  }
}

abstract class _IPCResponse implements IPCResponse {
  const factory _IPCResponse(
      {required final bool success,
      final dynamic data,
      final IPCError? error,
      final IPCMetadata? metadata}) = _$IPCResponseImpl;

  factory _IPCResponse.fromJson(Map<String, dynamic> json) =
      _$IPCResponseImpl.fromJson;

  @override
  bool get success;
  @override
  dynamic get data; // 允许任何类型的data，包括Map、List等
  @override
  IPCError? get error;
  @override
  IPCMetadata? get metadata;

  /// Create a copy of IPCResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$IPCResponseImplCopyWith<_$IPCResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

IPCRequest _$IPCRequestFromJson(Map<String, dynamic> json) {
  return _IPCRequest.fromJson(json);
}

/// @nodoc
mixin _$IPCRequest {
  String get method => throw _privateConstructorUsedError;
  String get path => throw _privateConstructorUsedError;
  Map<String, dynamic>? get data => throw _privateConstructorUsedError;
  @JsonKey(name: 'query_params')
  Map<String, dynamic>? get queryParams => throw _privateConstructorUsedError;
  @JsonKey(name: 'path_params')
  Map<String, String>? get pathParams => throw _privateConstructorUsedError;
  @JsonKey(name: 'request_id')
  String? get requestId => throw _privateConstructorUsedError;

  /// Serializes this IPCRequest to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of IPCRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $IPCRequestCopyWith<IPCRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $IPCRequestCopyWith<$Res> {
  factory $IPCRequestCopyWith(
          IPCRequest value, $Res Function(IPCRequest) then) =
      _$IPCRequestCopyWithImpl<$Res, IPCRequest>;
  @useResult
  $Res call(
      {String method,
      String path,
      Map<String, dynamic>? data,
      @JsonKey(name: 'query_params') Map<String, dynamic>? queryParams,
      @JsonKey(name: 'path_params') Map<String, String>? pathParams,
      @JsonKey(name: 'request_id') String? requestId});
}

/// @nodoc
class _$IPCRequestCopyWithImpl<$Res, $Val extends IPCRequest>
    implements $IPCRequestCopyWith<$Res> {
  _$IPCRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of IPCRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? method = null,
    Object? path = null,
    Object? data = freezed,
    Object? queryParams = freezed,
    Object? pathParams = freezed,
    Object? requestId = freezed,
  }) {
    return _then(_value.copyWith(
      method: null == method
          ? _value.method
          : method // ignore: cast_nullable_to_non_nullable
              as String,
      path: null == path
          ? _value.path
          : path // ignore: cast_nullable_to_non_nullable
              as String,
      data: freezed == data
          ? _value.data
          : data // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      queryParams: freezed == queryParams
          ? _value.queryParams
          : queryParams // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      pathParams: freezed == pathParams
          ? _value.pathParams
          : pathParams // ignore: cast_nullable_to_non_nullable
              as Map<String, String>?,
      requestId: freezed == requestId
          ? _value.requestId
          : requestId // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$IPCRequestImplCopyWith<$Res>
    implements $IPCRequestCopyWith<$Res> {
  factory _$$IPCRequestImplCopyWith(
          _$IPCRequestImpl value, $Res Function(_$IPCRequestImpl) then) =
      __$$IPCRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String method,
      String path,
      Map<String, dynamic>? data,
      @JsonKey(name: 'query_params') Map<String, dynamic>? queryParams,
      @JsonKey(name: 'path_params') Map<String, String>? pathParams,
      @JsonKey(name: 'request_id') String? requestId});
}

/// @nodoc
class __$$IPCRequestImplCopyWithImpl<$Res>
    extends _$IPCRequestCopyWithImpl<$Res, _$IPCRequestImpl>
    implements _$$IPCRequestImplCopyWith<$Res> {
  __$$IPCRequestImplCopyWithImpl(
      _$IPCRequestImpl _value, $Res Function(_$IPCRequestImpl) _then)
      : super(_value, _then);

  /// Create a copy of IPCRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? method = null,
    Object? path = null,
    Object? data = freezed,
    Object? queryParams = freezed,
    Object? pathParams = freezed,
    Object? requestId = freezed,
  }) {
    return _then(_$IPCRequestImpl(
      method: null == method
          ? _value.method
          : method // ignore: cast_nullable_to_non_nullable
              as String,
      path: null == path
          ? _value.path
          : path // ignore: cast_nullable_to_non_nullable
              as String,
      data: freezed == data
          ? _value._data
          : data // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      queryParams: freezed == queryParams
          ? _value._queryParams
          : queryParams // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      pathParams: freezed == pathParams
          ? _value._pathParams
          : pathParams // ignore: cast_nullable_to_non_nullable
              as Map<String, String>?,
      requestId: freezed == requestId
          ? _value.requestId
          : requestId // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$IPCRequestImpl implements _IPCRequest {
  const _$IPCRequestImpl(
      {required this.method,
      required this.path,
      final Map<String, dynamic>? data,
      @JsonKey(name: 'query_params') final Map<String, dynamic>? queryParams,
      @JsonKey(name: 'path_params') final Map<String, String>? pathParams,
      @JsonKey(name: 'request_id') this.requestId})
      : _data = data,
        _queryParams = queryParams,
        _pathParams = pathParams;

  factory _$IPCRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$IPCRequestImplFromJson(json);

  @override
  final String method;
  @override
  final String path;
  final Map<String, dynamic>? _data;
  @override
  Map<String, dynamic>? get data {
    final value = _data;
    if (value == null) return null;
    if (_data is EqualUnmodifiableMapView) return _data;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  final Map<String, dynamic>? _queryParams;
  @override
  @JsonKey(name: 'query_params')
  Map<String, dynamic>? get queryParams {
    final value = _queryParams;
    if (value == null) return null;
    if (_queryParams is EqualUnmodifiableMapView) return _queryParams;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  final Map<String, String>? _pathParams;
  @override
  @JsonKey(name: 'path_params')
  Map<String, String>? get pathParams {
    final value = _pathParams;
    if (value == null) return null;
    if (_pathParams is EqualUnmodifiableMapView) return _pathParams;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  @JsonKey(name: 'request_id')
  final String? requestId;

  @override
  String toString() {
    return 'IPCRequest(method: $method, path: $path, data: $data, queryParams: $queryParams, pathParams: $pathParams, requestId: $requestId)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$IPCRequestImpl &&
            (identical(other.method, method) || other.method == method) &&
            (identical(other.path, path) || other.path == path) &&
            const DeepCollectionEquality().equals(other._data, _data) &&
            const DeepCollectionEquality()
                .equals(other._queryParams, _queryParams) &&
            const DeepCollectionEquality()
                .equals(other._pathParams, _pathParams) &&
            (identical(other.requestId, requestId) ||
                other.requestId == requestId));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      method,
      path,
      const DeepCollectionEquality().hash(_data),
      const DeepCollectionEquality().hash(_queryParams),
      const DeepCollectionEquality().hash(_pathParams),
      requestId);

  /// Create a copy of IPCRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$IPCRequestImplCopyWith<_$IPCRequestImpl> get copyWith =>
      __$$IPCRequestImplCopyWithImpl<_$IPCRequestImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$IPCRequestImplToJson(
      this,
    );
  }
}

abstract class _IPCRequest implements IPCRequest {
  const factory _IPCRequest(
      {required final String method,
      required final String path,
      final Map<String, dynamic>? data,
      @JsonKey(name: 'query_params') final Map<String, dynamic>? queryParams,
      @JsonKey(name: 'path_params') final Map<String, String>? pathParams,
      @JsonKey(name: 'request_id') final String? requestId}) = _$IPCRequestImpl;

  factory _IPCRequest.fromJson(Map<String, dynamic> json) =
      _$IPCRequestImpl.fromJson;

  @override
  String get method;
  @override
  String get path;
  @override
  Map<String, dynamic>? get data;
  @override
  @JsonKey(name: 'query_params')
  Map<String, dynamic>? get queryParams;
  @override
  @JsonKey(name: 'path_params')
  Map<String, String>? get pathParams;
  @override
  @JsonKey(name: 'request_id')
  String? get requestId;

  /// Create a copy of IPCRequest
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$IPCRequestImplCopyWith<_$IPCRequestImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ConnectorStatusV2 _$ConnectorStatusV2FromJson(Map<String, dynamic> json) {
  return _ConnectorStatusV2.fromJson(json);
}

/// @nodoc
mixin _$ConnectorStatusV2 {
  @JsonKey(name: 'connector_id')
  String get connectorId => throw _privateConstructorUsedError;
  @JsonKey(name: 'display_name')
  String get displayName => throw _privateConstructorUsedError;
  bool get enabled => throw _privateConstructorUsedError; // 是否启用（基本状态）
  @JsonKey(name: 'running_state')
  ConnectorRunningState get runningState =>
      throw _privateConstructorUsedError; // 运行状态
  @JsonKey(name: 'is_installed')
  bool get isInstalled => throw _privateConstructorUsedError; // 虚拟字段
  @JsonKey(name: 'is_healthy')
  bool get isHealthy => throw _privateConstructorUsedError; // 是否健康
  @JsonKey(name: 'should_be_running')
  bool get shouldBeRunning => throw _privateConstructorUsedError; // 是否应该运行
  @JsonKey(name: 'process_id')
  int? get processId => throw _privateConstructorUsedError;
  @JsonKey(name: 'last_heartbeat')
  String? get lastHeartbeat => throw _privateConstructorUsedError;
  @JsonKey(name: 'data_count')
  int get dataCount => throw _privateConstructorUsedError;
  @JsonKey(name: 'last_activity')
  String? get lastActivity => throw _privateConstructorUsedError;
  @JsonKey(name: 'error_message')
  String? get errorMessage => throw _privateConstructorUsedError;
  @JsonKey(name: 'error_code')
  String? get errorCode => throw _privateConstructorUsedError;

  /// Serializes this ConnectorStatusV2 to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ConnectorStatusV2
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ConnectorStatusV2CopyWith<ConnectorStatusV2> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ConnectorStatusV2CopyWith<$Res> {
  factory $ConnectorStatusV2CopyWith(
          ConnectorStatusV2 value, $Res Function(ConnectorStatusV2) then) =
      _$ConnectorStatusV2CopyWithImpl<$Res, ConnectorStatusV2>;
  @useResult
  $Res call(
      {@JsonKey(name: 'connector_id') String connectorId,
      @JsonKey(name: 'display_name') String displayName,
      bool enabled,
      @JsonKey(name: 'running_state') ConnectorRunningState runningState,
      @JsonKey(name: 'is_installed') bool isInstalled,
      @JsonKey(name: 'is_healthy') bool isHealthy,
      @JsonKey(name: 'should_be_running') bool shouldBeRunning,
      @JsonKey(name: 'process_id') int? processId,
      @JsonKey(name: 'last_heartbeat') String? lastHeartbeat,
      @JsonKey(name: 'data_count') int dataCount,
      @JsonKey(name: 'last_activity') String? lastActivity,
      @JsonKey(name: 'error_message') String? errorMessage,
      @JsonKey(name: 'error_code') String? errorCode});
}

/// @nodoc
class _$ConnectorStatusV2CopyWithImpl<$Res, $Val extends ConnectorStatusV2>
    implements $ConnectorStatusV2CopyWith<$Res> {
  _$ConnectorStatusV2CopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ConnectorStatusV2
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? connectorId = null,
    Object? displayName = null,
    Object? enabled = null,
    Object? runningState = null,
    Object? isInstalled = null,
    Object? isHealthy = null,
    Object? shouldBeRunning = null,
    Object? processId = freezed,
    Object? lastHeartbeat = freezed,
    Object? dataCount = null,
    Object? lastActivity = freezed,
    Object? errorMessage = freezed,
    Object? errorCode = freezed,
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
      enabled: null == enabled
          ? _value.enabled
          : enabled // ignore: cast_nullable_to_non_nullable
              as bool,
      runningState: null == runningState
          ? _value.runningState
          : runningState // ignore: cast_nullable_to_non_nullable
              as ConnectorRunningState,
      isInstalled: null == isInstalled
          ? _value.isInstalled
          : isInstalled // ignore: cast_nullable_to_non_nullable
              as bool,
      isHealthy: null == isHealthy
          ? _value.isHealthy
          : isHealthy // ignore: cast_nullable_to_non_nullable
              as bool,
      shouldBeRunning: null == shouldBeRunning
          ? _value.shouldBeRunning
          : shouldBeRunning // ignore: cast_nullable_to_non_nullable
              as bool,
      processId: freezed == processId
          ? _value.processId
          : processId // ignore: cast_nullable_to_non_nullable
              as int?,
      lastHeartbeat: freezed == lastHeartbeat
          ? _value.lastHeartbeat
          : lastHeartbeat // ignore: cast_nullable_to_non_nullable
              as String?,
      dataCount: null == dataCount
          ? _value.dataCount
          : dataCount // ignore: cast_nullable_to_non_nullable
              as int,
      lastActivity: freezed == lastActivity
          ? _value.lastActivity
          : lastActivity // ignore: cast_nullable_to_non_nullable
              as String?,
      errorMessage: freezed == errorMessage
          ? _value.errorMessage
          : errorMessage // ignore: cast_nullable_to_non_nullable
              as String?,
      errorCode: freezed == errorCode
          ? _value.errorCode
          : errorCode // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ConnectorStatusV2ImplCopyWith<$Res>
    implements $ConnectorStatusV2CopyWith<$Res> {
  factory _$$ConnectorStatusV2ImplCopyWith(_$ConnectorStatusV2Impl value,
          $Res Function(_$ConnectorStatusV2Impl) then) =
      __$$ConnectorStatusV2ImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'connector_id') String connectorId,
      @JsonKey(name: 'display_name') String displayName,
      bool enabled,
      @JsonKey(name: 'running_state') ConnectorRunningState runningState,
      @JsonKey(name: 'is_installed') bool isInstalled,
      @JsonKey(name: 'is_healthy') bool isHealthy,
      @JsonKey(name: 'should_be_running') bool shouldBeRunning,
      @JsonKey(name: 'process_id') int? processId,
      @JsonKey(name: 'last_heartbeat') String? lastHeartbeat,
      @JsonKey(name: 'data_count') int dataCount,
      @JsonKey(name: 'last_activity') String? lastActivity,
      @JsonKey(name: 'error_message') String? errorMessage,
      @JsonKey(name: 'error_code') String? errorCode});
}

/// @nodoc
class __$$ConnectorStatusV2ImplCopyWithImpl<$Res>
    extends _$ConnectorStatusV2CopyWithImpl<$Res, _$ConnectorStatusV2Impl>
    implements _$$ConnectorStatusV2ImplCopyWith<$Res> {
  __$$ConnectorStatusV2ImplCopyWithImpl(_$ConnectorStatusV2Impl _value,
      $Res Function(_$ConnectorStatusV2Impl) _then)
      : super(_value, _then);

  /// Create a copy of ConnectorStatusV2
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? connectorId = null,
    Object? displayName = null,
    Object? enabled = null,
    Object? runningState = null,
    Object? isInstalled = null,
    Object? isHealthy = null,
    Object? shouldBeRunning = null,
    Object? processId = freezed,
    Object? lastHeartbeat = freezed,
    Object? dataCount = null,
    Object? lastActivity = freezed,
    Object? errorMessage = freezed,
    Object? errorCode = freezed,
  }) {
    return _then(_$ConnectorStatusV2Impl(
      connectorId: null == connectorId
          ? _value.connectorId
          : connectorId // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: null == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String,
      enabled: null == enabled
          ? _value.enabled
          : enabled // ignore: cast_nullable_to_non_nullable
              as bool,
      runningState: null == runningState
          ? _value.runningState
          : runningState // ignore: cast_nullable_to_non_nullable
              as ConnectorRunningState,
      isInstalled: null == isInstalled
          ? _value.isInstalled
          : isInstalled // ignore: cast_nullable_to_non_nullable
              as bool,
      isHealthy: null == isHealthy
          ? _value.isHealthy
          : isHealthy // ignore: cast_nullable_to_non_nullable
              as bool,
      shouldBeRunning: null == shouldBeRunning
          ? _value.shouldBeRunning
          : shouldBeRunning // ignore: cast_nullable_to_non_nullable
              as bool,
      processId: freezed == processId
          ? _value.processId
          : processId // ignore: cast_nullable_to_non_nullable
              as int?,
      lastHeartbeat: freezed == lastHeartbeat
          ? _value.lastHeartbeat
          : lastHeartbeat // ignore: cast_nullable_to_non_nullable
              as String?,
      dataCount: null == dataCount
          ? _value.dataCount
          : dataCount // ignore: cast_nullable_to_non_nullable
              as int,
      lastActivity: freezed == lastActivity
          ? _value.lastActivity
          : lastActivity // ignore: cast_nullable_to_non_nullable
              as String?,
      errorMessage: freezed == errorMessage
          ? _value.errorMessage
          : errorMessage // ignore: cast_nullable_to_non_nullable
              as String?,
      errorCode: freezed == errorCode
          ? _value.errorCode
          : errorCode // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ConnectorStatusV2Impl implements _ConnectorStatusV2 {
  const _$ConnectorStatusV2Impl(
      {@JsonKey(name: 'connector_id') required this.connectorId,
      @JsonKey(name: 'display_name') required this.displayName,
      this.enabled = true,
      @JsonKey(name: 'running_state')
      this.runningState = ConnectorRunningState.stopped,
      @JsonKey(name: 'is_installed') this.isInstalled = true,
      @JsonKey(name: 'is_healthy') this.isHealthy = false,
      @JsonKey(name: 'should_be_running') this.shouldBeRunning = false,
      @JsonKey(name: 'process_id') this.processId,
      @JsonKey(name: 'last_heartbeat') this.lastHeartbeat,
      @JsonKey(name: 'data_count') this.dataCount = 0,
      @JsonKey(name: 'last_activity') this.lastActivity,
      @JsonKey(name: 'error_message') this.errorMessage,
      @JsonKey(name: 'error_code') this.errorCode});

  factory _$ConnectorStatusV2Impl.fromJson(Map<String, dynamic> json) =>
      _$$ConnectorStatusV2ImplFromJson(json);

  @override
  @JsonKey(name: 'connector_id')
  final String connectorId;
  @override
  @JsonKey(name: 'display_name')
  final String displayName;
  @override
  @JsonKey()
  final bool enabled;
// 是否启用（基本状态）
  @override
  @JsonKey(name: 'running_state')
  final ConnectorRunningState runningState;
// 运行状态
  @override
  @JsonKey(name: 'is_installed')
  final bool isInstalled;
// 虚拟字段
  @override
  @JsonKey(name: 'is_healthy')
  final bool isHealthy;
// 是否健康
  @override
  @JsonKey(name: 'should_be_running')
  final bool shouldBeRunning;
// 是否应该运行
  @override
  @JsonKey(name: 'process_id')
  final int? processId;
  @override
  @JsonKey(name: 'last_heartbeat')
  final String? lastHeartbeat;
  @override
  @JsonKey(name: 'data_count')
  final int dataCount;
  @override
  @JsonKey(name: 'last_activity')
  final String? lastActivity;
  @override
  @JsonKey(name: 'error_message')
  final String? errorMessage;
  @override
  @JsonKey(name: 'error_code')
  final String? errorCode;

  @override
  String toString() {
    return 'ConnectorStatusV2(connectorId: $connectorId, displayName: $displayName, enabled: $enabled, runningState: $runningState, isInstalled: $isInstalled, isHealthy: $isHealthy, shouldBeRunning: $shouldBeRunning, processId: $processId, lastHeartbeat: $lastHeartbeat, dataCount: $dataCount, lastActivity: $lastActivity, errorMessage: $errorMessage, errorCode: $errorCode)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ConnectorStatusV2Impl &&
            (identical(other.connectorId, connectorId) ||
                other.connectorId == connectorId) &&
            (identical(other.displayName, displayName) ||
                other.displayName == displayName) &&
            (identical(other.enabled, enabled) || other.enabled == enabled) &&
            (identical(other.runningState, runningState) ||
                other.runningState == runningState) &&
            (identical(other.isInstalled, isInstalled) ||
                other.isInstalled == isInstalled) &&
            (identical(other.isHealthy, isHealthy) ||
                other.isHealthy == isHealthy) &&
            (identical(other.shouldBeRunning, shouldBeRunning) ||
                other.shouldBeRunning == shouldBeRunning) &&
            (identical(other.processId, processId) ||
                other.processId == processId) &&
            (identical(other.lastHeartbeat, lastHeartbeat) ||
                other.lastHeartbeat == lastHeartbeat) &&
            (identical(other.dataCount, dataCount) ||
                other.dataCount == dataCount) &&
            (identical(other.lastActivity, lastActivity) ||
                other.lastActivity == lastActivity) &&
            (identical(other.errorMessage, errorMessage) ||
                other.errorMessage == errorMessage) &&
            (identical(other.errorCode, errorCode) ||
                other.errorCode == errorCode));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      connectorId,
      displayName,
      enabled,
      runningState,
      isInstalled,
      isHealthy,
      shouldBeRunning,
      processId,
      lastHeartbeat,
      dataCount,
      lastActivity,
      errorMessage,
      errorCode);

  /// Create a copy of ConnectorStatusV2
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ConnectorStatusV2ImplCopyWith<_$ConnectorStatusV2Impl> get copyWith =>
      __$$ConnectorStatusV2ImplCopyWithImpl<_$ConnectorStatusV2Impl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ConnectorStatusV2ImplToJson(
      this,
    );
  }
}

abstract class _ConnectorStatusV2 implements ConnectorStatusV2 {
  const factory _ConnectorStatusV2(
      {@JsonKey(name: 'connector_id') required final String connectorId,
      @JsonKey(name: 'display_name') required final String displayName,
      final bool enabled,
      @JsonKey(name: 'running_state') final ConnectorRunningState runningState,
      @JsonKey(name: 'is_installed') final bool isInstalled,
      @JsonKey(name: 'is_healthy') final bool isHealthy,
      @JsonKey(name: 'should_be_running') final bool shouldBeRunning,
      @JsonKey(name: 'process_id') final int? processId,
      @JsonKey(name: 'last_heartbeat') final String? lastHeartbeat,
      @JsonKey(name: 'data_count') final int dataCount,
      @JsonKey(name: 'last_activity') final String? lastActivity,
      @JsonKey(name: 'error_message') final String? errorMessage,
      @JsonKey(name: 'error_code')
      final String? errorCode}) = _$ConnectorStatusV2Impl;

  factory _ConnectorStatusV2.fromJson(Map<String, dynamic> json) =
      _$ConnectorStatusV2Impl.fromJson;

  @override
  @JsonKey(name: 'connector_id')
  String get connectorId;
  @override
  @JsonKey(name: 'display_name')
  String get displayName;
  @override
  bool get enabled; // 是否启用（基本状态）
  @override
  @JsonKey(name: 'running_state')
  ConnectorRunningState get runningState; // 运行状态
  @override
  @JsonKey(name: 'is_installed')
  bool get isInstalled; // 虚拟字段
  @override
  @JsonKey(name: 'is_healthy')
  bool get isHealthy; // 是否健康
  @override
  @JsonKey(name: 'should_be_running')
  bool get shouldBeRunning; // 是否应该运行
  @override
  @JsonKey(name: 'process_id')
  int? get processId;
  @override
  @JsonKey(name: 'last_heartbeat')
  String? get lastHeartbeat;
  @override
  @JsonKey(name: 'data_count')
  int get dataCount;
  @override
  @JsonKey(name: 'last_activity')
  String? get lastActivity;
  @override
  @JsonKey(name: 'error_message')
  String? get errorMessage;
  @override
  @JsonKey(name: 'error_code')
  String? get errorCode;

  /// Create a copy of ConnectorStatusV2
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ConnectorStatusV2ImplCopyWith<_$ConnectorStatusV2Impl> get copyWith =>
      throw _privateConstructorUsedError;
}
