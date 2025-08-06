// ignore_for_file: invalid_annotation_target

import 'package:freezed_annotation/freezed_annotation.dart';

part 'api_response.freezed.dart';
part 'api_response.g.dart';

/// 通用API响应包装器
@freezed
class APIResponse with _$APIResponse {
  const factory APIResponse({
    required bool success,
    @Default('') String message,
    Object? data,
    String? error,
  }) = _APIResponse;

  factory APIResponse.fromJson(Map<String, dynamic> json) =>
      _$APIResponseFromJson(json);

  /// 创建成功响应
  factory APIResponse.success({
    String message = '',
    Object? data,
  }) {
    return APIResponse(
      success: true,
      message: message,
      data: data,
    );
  }

  /// 创建失败响应
  factory APIResponse.failure({
    String message = '',
    String? error,
    Object? data,
  }) {
    return APIResponse(
      success: false,
      message: message,
      error: error,
      data: data,
    );
  }
}

/// WebView配置支持检查响应
@freezed
class WebViewSupportResponse with _$WebViewSupportResponse {
  const factory WebViewSupportResponse({
    @JsonKey(name: 'connector_id') required String connectorId,
    @JsonKey(name: 'supports_webview') required bool supportsWebview,
    @JsonKey(name: 'template_path') String? templatePath,
    @JsonKey(name: 'template_name') String? templateName,
  }) = _WebViewSupportResponse;

  factory WebViewSupportResponse.fromJson(Map<String, dynamic> json) =>
      _$WebViewSupportResponseFromJson(json);
}

/// 模板信息
@freezed
class TemplateInfo with _$TemplateInfo {
  const factory TemplateInfo({
    required String name,
    required String path,
    @JsonKey(name: 'display_name') String? displayName,
    String? description,
    @JsonKey(name: 'is_default') @Default(false) bool isDefault,
  }) = _TemplateInfo;

  factory TemplateInfo.fromJson(Map<String, dynamic> json) =>
      _$TemplateInfoFromJson(json);
}