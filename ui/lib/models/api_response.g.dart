// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'api_response.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$APIResponseImpl _$$APIResponseImplFromJson(Map<String, dynamic> json) =>
    _$APIResponseImpl(
      success: json['success'] as bool,
      message: json['message'] as String? ?? '',
      data: json['data'],
      error: json['error'] as String?,
    );

Map<String, dynamic> _$$APIResponseImplToJson(_$APIResponseImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'message': instance.message,
      'data': instance.data,
      'error': instance.error,
    };

_$WebViewSupportResponseImpl _$$WebViewSupportResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$WebViewSupportResponseImpl(
      connectorId: json['connector_id'] as String,
      supportsWebview: json['supports_webview'] as bool,
      templatePath: json['template_path'] as String?,
      templateName: json['template_name'] as String?,
    );

Map<String, dynamic> _$$WebViewSupportResponseImplToJson(
        _$WebViewSupportResponseImpl instance) =>
    <String, dynamic>{
      'connector_id': instance.connectorId,
      'supports_webview': instance.supportsWebview,
      'template_path': instance.templatePath,
      'template_name': instance.templateName,
    };

_$TemplateInfoImpl _$$TemplateInfoImplFromJson(Map<String, dynamic> json) =>
    _$TemplateInfoImpl(
      name: json['name'] as String,
      path: json['path'] as String,
      displayName: json['display_name'] as String?,
      description: json['description'] as String?,
      isDefault: json['is_default'] as bool? ?? false,
    );

Map<String, dynamic> _$$TemplateInfoImplToJson(_$TemplateInfoImpl instance) =>
    <String, dynamic>{
      'name': instance.name,
      'path': instance.path,
      'display_name': instance.displayName,
      'description': instance.description,
      'is_default': instance.isDefault,
    };
