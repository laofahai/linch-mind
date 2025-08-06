// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'api_response.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

APIResponse _$APIResponseFromJson(Map<String, dynamic> json) {
  return _APIResponse.fromJson(json);
}

/// @nodoc
mixin _$APIResponse {
  bool get success => throw _privateConstructorUsedError;
  String get message => throw _privateConstructorUsedError;
  Object? get data => throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;

  /// Serializes this APIResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of APIResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $APIResponseCopyWith<APIResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $APIResponseCopyWith<$Res> {
  factory $APIResponseCopyWith(
          APIResponse value, $Res Function(APIResponse) then) =
      _$APIResponseCopyWithImpl<$Res, APIResponse>;
  @useResult
  $Res call({bool success, String message, Object? data, String? error});
}

/// @nodoc
class _$APIResponseCopyWithImpl<$Res, $Val extends APIResponse>
    implements $APIResponseCopyWith<$Res> {
  _$APIResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of APIResponse
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
abstract class _$$APIResponseImplCopyWith<$Res>
    implements $APIResponseCopyWith<$Res> {
  factory _$$APIResponseImplCopyWith(
          _$APIResponseImpl value, $Res Function(_$APIResponseImpl) then) =
      __$$APIResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({bool success, String message, Object? data, String? error});
}

/// @nodoc
class __$$APIResponseImplCopyWithImpl<$Res>
    extends _$APIResponseCopyWithImpl<$Res, _$APIResponseImpl>
    implements _$$APIResponseImplCopyWith<$Res> {
  __$$APIResponseImplCopyWithImpl(
      _$APIResponseImpl _value, $Res Function(_$APIResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of APIResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? message = null,
    Object? data = freezed,
    Object? error = freezed,
  }) {
    return _then(_$APIResponseImpl(
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
class _$APIResponseImpl implements _APIResponse {
  const _$APIResponseImpl(
      {required this.success, this.message = '', this.data, this.error});

  factory _$APIResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$APIResponseImplFromJson(json);

  @override
  final bool success;
  @override
  @JsonKey()
  final String message;
  @override
  final Object? data;
  @override
  final String? error;

  @override
  String toString() {
    return 'APIResponse(success: $success, message: $message, data: $data, error: $error)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$APIResponseImpl &&
            (identical(other.success, success) || other.success == success) &&
            (identical(other.message, message) || other.message == message) &&
            const DeepCollectionEquality().equals(other.data, data) &&
            (identical(other.error, error) || other.error == error));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, success, message,
      const DeepCollectionEquality().hash(data), error);

  /// Create a copy of APIResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$APIResponseImplCopyWith<_$APIResponseImpl> get copyWith =>
      __$$APIResponseImplCopyWithImpl<_$APIResponseImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$APIResponseImplToJson(
      this,
    );
  }
}

abstract class _APIResponse implements APIResponse {
  const factory _APIResponse(
      {required final bool success,
      final String message,
      final Object? data,
      final String? error}) = _$APIResponseImpl;

  factory _APIResponse.fromJson(Map<String, dynamic> json) =
      _$APIResponseImpl.fromJson;

  @override
  bool get success;
  @override
  String get message;
  @override
  Object? get data;
  @override
  String? get error;

  /// Create a copy of APIResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$APIResponseImplCopyWith<_$APIResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

WebViewSupportResponse _$WebViewSupportResponseFromJson(
    Map<String, dynamic> json) {
  return _WebViewSupportResponse.fromJson(json);
}

/// @nodoc
mixin _$WebViewSupportResponse {
  @JsonKey(name: 'connector_id')
  String get connectorId => throw _privateConstructorUsedError;
  @JsonKey(name: 'supports_webview')
  bool get supportsWebview => throw _privateConstructorUsedError;
  @JsonKey(name: 'template_path')
  String? get templatePath => throw _privateConstructorUsedError;
  @JsonKey(name: 'template_name')
  String? get templateName => throw _privateConstructorUsedError;

  /// Serializes this WebViewSupportResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of WebViewSupportResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $WebViewSupportResponseCopyWith<WebViewSupportResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $WebViewSupportResponseCopyWith<$Res> {
  factory $WebViewSupportResponseCopyWith(WebViewSupportResponse value,
          $Res Function(WebViewSupportResponse) then) =
      _$WebViewSupportResponseCopyWithImpl<$Res, WebViewSupportResponse>;
  @useResult
  $Res call(
      {@JsonKey(name: 'connector_id') String connectorId,
      @JsonKey(name: 'supports_webview') bool supportsWebview,
      @JsonKey(name: 'template_path') String? templatePath,
      @JsonKey(name: 'template_name') String? templateName});
}

/// @nodoc
class _$WebViewSupportResponseCopyWithImpl<$Res,
        $Val extends WebViewSupportResponse>
    implements $WebViewSupportResponseCopyWith<$Res> {
  _$WebViewSupportResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of WebViewSupportResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? connectorId = null,
    Object? supportsWebview = null,
    Object? templatePath = freezed,
    Object? templateName = freezed,
  }) {
    return _then(_value.copyWith(
      connectorId: null == connectorId
          ? _value.connectorId
          : connectorId // ignore: cast_nullable_to_non_nullable
              as String,
      supportsWebview: null == supportsWebview
          ? _value.supportsWebview
          : supportsWebview // ignore: cast_nullable_to_non_nullable
              as bool,
      templatePath: freezed == templatePath
          ? _value.templatePath
          : templatePath // ignore: cast_nullable_to_non_nullable
              as String?,
      templateName: freezed == templateName
          ? _value.templateName
          : templateName // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$WebViewSupportResponseImplCopyWith<$Res>
    implements $WebViewSupportResponseCopyWith<$Res> {
  factory _$$WebViewSupportResponseImplCopyWith(
          _$WebViewSupportResponseImpl value,
          $Res Function(_$WebViewSupportResponseImpl) then) =
      __$$WebViewSupportResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'connector_id') String connectorId,
      @JsonKey(name: 'supports_webview') bool supportsWebview,
      @JsonKey(name: 'template_path') String? templatePath,
      @JsonKey(name: 'template_name') String? templateName});
}

/// @nodoc
class __$$WebViewSupportResponseImplCopyWithImpl<$Res>
    extends _$WebViewSupportResponseCopyWithImpl<$Res,
        _$WebViewSupportResponseImpl>
    implements _$$WebViewSupportResponseImplCopyWith<$Res> {
  __$$WebViewSupportResponseImplCopyWithImpl(
      _$WebViewSupportResponseImpl _value,
      $Res Function(_$WebViewSupportResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of WebViewSupportResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? connectorId = null,
    Object? supportsWebview = null,
    Object? templatePath = freezed,
    Object? templateName = freezed,
  }) {
    return _then(_$WebViewSupportResponseImpl(
      connectorId: null == connectorId
          ? _value.connectorId
          : connectorId // ignore: cast_nullable_to_non_nullable
              as String,
      supportsWebview: null == supportsWebview
          ? _value.supportsWebview
          : supportsWebview // ignore: cast_nullable_to_non_nullable
              as bool,
      templatePath: freezed == templatePath
          ? _value.templatePath
          : templatePath // ignore: cast_nullable_to_non_nullable
              as String?,
      templateName: freezed == templateName
          ? _value.templateName
          : templateName // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$WebViewSupportResponseImpl implements _WebViewSupportResponse {
  const _$WebViewSupportResponseImpl(
      {@JsonKey(name: 'connector_id') required this.connectorId,
      @JsonKey(name: 'supports_webview') required this.supportsWebview,
      @JsonKey(name: 'template_path') this.templatePath,
      @JsonKey(name: 'template_name') this.templateName});

  factory _$WebViewSupportResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$WebViewSupportResponseImplFromJson(json);

  @override
  @JsonKey(name: 'connector_id')
  final String connectorId;
  @override
  @JsonKey(name: 'supports_webview')
  final bool supportsWebview;
  @override
  @JsonKey(name: 'template_path')
  final String? templatePath;
  @override
  @JsonKey(name: 'template_name')
  final String? templateName;

  @override
  String toString() {
    return 'WebViewSupportResponse(connectorId: $connectorId, supportsWebview: $supportsWebview, templatePath: $templatePath, templateName: $templateName)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$WebViewSupportResponseImpl &&
            (identical(other.connectorId, connectorId) ||
                other.connectorId == connectorId) &&
            (identical(other.supportsWebview, supportsWebview) ||
                other.supportsWebview == supportsWebview) &&
            (identical(other.templatePath, templatePath) ||
                other.templatePath == templatePath) &&
            (identical(other.templateName, templateName) ||
                other.templateName == templateName));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType, connectorId, supportsWebview, templatePath, templateName);

  /// Create a copy of WebViewSupportResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$WebViewSupportResponseImplCopyWith<_$WebViewSupportResponseImpl>
      get copyWith => __$$WebViewSupportResponseImplCopyWithImpl<
          _$WebViewSupportResponseImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$WebViewSupportResponseImplToJson(
      this,
    );
  }
}

abstract class _WebViewSupportResponse implements WebViewSupportResponse {
  const factory _WebViewSupportResponse(
      {@JsonKey(name: 'connector_id') required final String connectorId,
      @JsonKey(name: 'supports_webview') required final bool supportsWebview,
      @JsonKey(name: 'template_path') final String? templatePath,
      @JsonKey(name: 'template_name')
      final String? templateName}) = _$WebViewSupportResponseImpl;

  factory _WebViewSupportResponse.fromJson(Map<String, dynamic> json) =
      _$WebViewSupportResponseImpl.fromJson;

  @override
  @JsonKey(name: 'connector_id')
  String get connectorId;
  @override
  @JsonKey(name: 'supports_webview')
  bool get supportsWebview;
  @override
  @JsonKey(name: 'template_path')
  String? get templatePath;
  @override
  @JsonKey(name: 'template_name')
  String? get templateName;

  /// Create a copy of WebViewSupportResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$WebViewSupportResponseImplCopyWith<_$WebViewSupportResponseImpl>
      get copyWith => throw _privateConstructorUsedError;
}

TemplateInfo _$TemplateInfoFromJson(Map<String, dynamic> json) {
  return _TemplateInfo.fromJson(json);
}

/// @nodoc
mixin _$TemplateInfo {
  String get name => throw _privateConstructorUsedError;
  String get path => throw _privateConstructorUsedError;
  @JsonKey(name: 'display_name')
  String? get displayName => throw _privateConstructorUsedError;
  String? get description => throw _privateConstructorUsedError;
  @JsonKey(name: 'is_default')
  bool get isDefault => throw _privateConstructorUsedError;

  /// Serializes this TemplateInfo to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of TemplateInfo
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $TemplateInfoCopyWith<TemplateInfo> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $TemplateInfoCopyWith<$Res> {
  factory $TemplateInfoCopyWith(
          TemplateInfo value, $Res Function(TemplateInfo) then) =
      _$TemplateInfoCopyWithImpl<$Res, TemplateInfo>;
  @useResult
  $Res call(
      {String name,
      String path,
      @JsonKey(name: 'display_name') String? displayName,
      String? description,
      @JsonKey(name: 'is_default') bool isDefault});
}

/// @nodoc
class _$TemplateInfoCopyWithImpl<$Res, $Val extends TemplateInfo>
    implements $TemplateInfoCopyWith<$Res> {
  _$TemplateInfoCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of TemplateInfo
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? path = null,
    Object? displayName = freezed,
    Object? description = freezed,
    Object? isDefault = null,
  }) {
    return _then(_value.copyWith(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      path: null == path
          ? _value.path
          : path // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: freezed == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String?,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
      isDefault: null == isDefault
          ? _value.isDefault
          : isDefault // ignore: cast_nullable_to_non_nullable
              as bool,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$TemplateInfoImplCopyWith<$Res>
    implements $TemplateInfoCopyWith<$Res> {
  factory _$$TemplateInfoImplCopyWith(
          _$TemplateInfoImpl value, $Res Function(_$TemplateInfoImpl) then) =
      __$$TemplateInfoImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String name,
      String path,
      @JsonKey(name: 'display_name') String? displayName,
      String? description,
      @JsonKey(name: 'is_default') bool isDefault});
}

/// @nodoc
class __$$TemplateInfoImplCopyWithImpl<$Res>
    extends _$TemplateInfoCopyWithImpl<$Res, _$TemplateInfoImpl>
    implements _$$TemplateInfoImplCopyWith<$Res> {
  __$$TemplateInfoImplCopyWithImpl(
      _$TemplateInfoImpl _value, $Res Function(_$TemplateInfoImpl) _then)
      : super(_value, _then);

  /// Create a copy of TemplateInfo
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? path = null,
    Object? displayName = freezed,
    Object? description = freezed,
    Object? isDefault = null,
  }) {
    return _then(_$TemplateInfoImpl(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      path: null == path
          ? _value.path
          : path // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: freezed == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String?,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
      isDefault: null == isDefault
          ? _value.isDefault
          : isDefault // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$TemplateInfoImpl implements _TemplateInfo {
  const _$TemplateInfoImpl(
      {required this.name,
      required this.path,
      @JsonKey(name: 'display_name') this.displayName,
      this.description,
      @JsonKey(name: 'is_default') this.isDefault = false});

  factory _$TemplateInfoImpl.fromJson(Map<String, dynamic> json) =>
      _$$TemplateInfoImplFromJson(json);

  @override
  final String name;
  @override
  final String path;
  @override
  @JsonKey(name: 'display_name')
  final String? displayName;
  @override
  final String? description;
  @override
  @JsonKey(name: 'is_default')
  final bool isDefault;

  @override
  String toString() {
    return 'TemplateInfo(name: $name, path: $path, displayName: $displayName, description: $description, isDefault: $isDefault)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$TemplateInfoImpl &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.path, path) || other.path == path) &&
            (identical(other.displayName, displayName) ||
                other.displayName == displayName) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.isDefault, isDefault) ||
                other.isDefault == isDefault));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, name, path, displayName, description, isDefault);

  /// Create a copy of TemplateInfo
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$TemplateInfoImplCopyWith<_$TemplateInfoImpl> get copyWith =>
      __$$TemplateInfoImplCopyWithImpl<_$TemplateInfoImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$TemplateInfoImplToJson(
      this,
    );
  }
}

abstract class _TemplateInfo implements TemplateInfo {
  const factory _TemplateInfo(
      {required final String name,
      required final String path,
      @JsonKey(name: 'display_name') final String? displayName,
      final String? description,
      @JsonKey(name: 'is_default') final bool isDefault}) = _$TemplateInfoImpl;

  factory _TemplateInfo.fromJson(Map<String, dynamic> json) =
      _$TemplateInfoImpl.fromJson;

  @override
  String get name;
  @override
  String get path;
  @override
  @JsonKey(name: 'display_name')
  String? get displayName;
  @override
  String? get description;
  @override
  @JsonKey(name: 'is_default')
  bool get isDefault;

  /// Create a copy of TemplateInfo
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$TemplateInfoImplCopyWith<_$TemplateInfoImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
