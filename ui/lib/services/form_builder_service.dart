import 'package:flutter/foundation.dart';
import 'package:reactive_forms/reactive_forms.dart';
import '../config/ui_text_constants.dart';

/// JSON Schema 到 ReactiveForm 的映射服务
class FormBuilderService {
  /// 安全的Map类型转换
  static Map<String, dynamic>? _safeMapCast(dynamic value) {
    if (value == null) return null;
    if (value is Map<String, dynamic>) return value;

    // 尝试转换Map<dynamic, dynamic>或其他Map类型
    if (value is Map) {
      try {
        return Map<String, dynamic>.from(value);
      } catch (e) {
        debugPrint('[WARNING] Map cast failed: $e');
        return null;
      }
    }

    debugPrint('[WARNING] Expected Map but got ${value.runtimeType}');
    return null;
  }

  /// 安全的List类型转换
  static List<T>? _safeListCast<T>(dynamic value) {
    if (value == null) return null;
    if (value is List<T>) return value;

    if (value is List) {
      try {
        return List<T>.from(value);
      } catch (e) {
        debugPrint('[WARNING] List cast failed: $e');
        return null;
      }
    }

    debugPrint('[WARNING] Expected List but got ${value.runtimeType}');
    return null;
  }

  /// 从 JSON Schema 构建 FormGroup - 原生嵌套结构，无字符替换
  static FormGroup buildFormFromSchema({
    required Map<String, dynamic> schema,
    Map<String, dynamic>? initialData,
    Map<String, dynamic>? uiSchema,
  }) {
    final properties =
        _safeMapCast(schema['properties']) ?? <String, dynamic>{};

    final required = _safeListCast<String>(schema['required']) ?? <String>[];
    final controls = <String, AbstractControl<dynamic>>{};

    // 直接构建原生嵌套结构，完全消除字符替换转换
    for (final entry in properties.entries) {
      final fieldName = entry.key;
      final fieldSchema = _safeMapCast(entry.value) ?? <String, dynamic>{};
      final isRequired = required.contains(fieldName);
      final initialValue = initialData?[fieldName];

      controls[fieldName] = _createControlForField(
        fieldSchema: fieldSchema,
        initialValue: initialValue,
        isRequired: isRequired,
      );
    }

    return FormGroup(controls);
  }

  /// 为单个字段创建控件
  static AbstractControl<dynamic> _createControlForField({
    required Map<String, dynamic> fieldSchema,
    dynamic initialValue,
    bool isRequired = false,
  }) {
    final type = fieldSchema['type'] as String?;
    final validators = <Validator<dynamic>>[];

    // 添加必填验证
    if (isRequired) {
      validators.add(Validators.required);
    }

    // 根据字段类型添加特定验证
    switch (type) {
      case 'string':
        return _createStringControl(fieldSchema, initialValue, validators);
      case 'integer':
      case 'number':
        return _createNumberControl(fieldSchema, initialValue, validators);
      case 'boolean':
        return FormControl<bool>(
          value: initialValue as bool?,
          validators: validators,
        );
      case 'array':
        return _createArrayControl(fieldSchema, initialValue, validators);
      case 'object':
        return _createObjectControl(fieldSchema, initialValue, validators);
      default:
        return FormControl<String>(
          value: initialValue?.toString(),
          validators: validators,
        );
    }
  }

  /// 创建字符串控件
  static FormControl<String> _createStringControl(
    Map<String, dynamic> fieldSchema,
    dynamic initialValue,
    List<Validator<dynamic>> validators,
  ) {
    // 长度验证
    final minLength = fieldSchema['minLength'] as int?;
    final maxLength = fieldSchema['maxLength'] as int?;

    if (minLength != null) {
      validators.add(Validators.minLength(minLength));
    }
    if (maxLength != null) {
      validators.add(Validators.maxLength(maxLength));
    }

    // 模式验证
    final pattern = fieldSchema['pattern'] as String?;
    if (pattern != null) {
      validators.add(Validators.pattern(pattern));
    }

    // 格式验证
    final format = fieldSchema['format'] as String?;
    switch (format) {
      case 'email':
        validators.add(Validators.email);
        break;
      case 'uri':
        validators.add(Validators.pattern(r'^https?://.*'));
        break;
    }

    // 枚举验证 - 使用简化版本
    final enumValues = fieldSchema['enum'] as List?;
    if (enumValues != null && enumValues.isNotEmpty) {
      // 对于枚举值，reactive_forms会在下拉框中自动限制选择
      // 这里只做基本类型验证
    }

    return FormControl<String>(
      value: initialValue?.toString(),
      validators: validators,
    );
  }

  /// 创建数值控件 - 使用动态类型以支持各种数值组件
  static AbstractControl<dynamic> _createNumberControl(
    Map<String, dynamic> fieldSchema,
    dynamic initialValue,
    List<Validator<dynamic>> validators,
  ) {
    final minimum = fieldSchema['minimum'] as num?;
    final maximum = fieldSchema['maximum'] as num?;

    if (minimum != null) {
      validators.add(Validators.min(minimum));
    }
    if (maximum != null) {
      validators.add(Validators.max(maximum));
    }

    // 智能类型推断 - 根据组件类型决定最合适的数据类型
    final inferredWidget = inferWidgetType(fieldSchema);
    final isInteger = fieldSchema['type'] == 'integer';

    // Slider组件优先使用double类型，确保兼容性
    if (inferredWidget == 'slider') {
      final doubleValue = _safeConvertToDouble(initialValue);
      return FormControl<double>(
        value: doubleValue,
        validators: validators,
      );
    }

    // 其他数值组件使用num类型，保持灵活性
    final numValue = _safeConvertToNum(initialValue, isInteger);
    return FormControl<num>(
      value: numValue,
      validators: validators,
    );
  }

  /// 安全转换为double类型
  static double? _safeConvertToDouble(dynamic value) {
    if (value == null) return null;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value);
    return double.tryParse(value.toString());
  }

  /// 安全转换为num类型
  static num? _safeConvertToNum(dynamic value, bool preferInt) {
    if (value == null) return null;
    if (value is num) return value;
    if (value is String) {
      if (preferInt) {
        return int.tryParse(value) ?? double.tryParse(value);
      } else {
        return double.tryParse(value) ?? int.tryParse(value);
      }
    }
    final str = value.toString();
    if (preferInt) {
      return int.tryParse(str) ?? double.tryParse(str);
    } else {
      return double.tryParse(str) ?? int.tryParse(str);
    }
  }

  /// 创建数组控件 - 智能类型检测
  static AbstractControl<dynamic> _createArrayControl(
    Map<String, dynamic> fieldSchema,
    dynamic initialValue,
    List<Validator<dynamic>> validators,
  ) {
    final items = _safeMapCast(fieldSchema['items']);

    // 对于简单的字符串数组，使用 FormControl<List<String>>
    // 这种类型更适合标签输入等场景
    if (items != null && items['type'] == 'string') {
      late final List<String> initialList;
      if (initialValue is List) {
        // 安全转换，确保所有项都是字符串类型
        try {
          initialList = initialValue
              .map((item) => item?.toString() ?? '')
              .where((str) => str.isNotEmpty)
              .toList();
        } catch (e) {
          debugPrint('[WARNING] Failed to convert array items to strings: $e');
          initialList = <String>[];
        }
      } else {
        initialList = <String>[];
      }

      // 创建适用于List<String>的验证器 - 使用动态类型以兼容reactive_forms 17.0
      final listValidators = <Validator<dynamic>>[];

      // 对于required验证，使用Validators.delegate
      if (validators.any((v) => v == Validators.required)) {
        listValidators.add(Validators.delegate((AbstractControl control) {
          final value = control.value as List<String>?;
          return (value == null || value.isEmpty)
              ? <String, dynamic>{'required': true}
              : null;
        }));
      }

      // 对于minItems验证（如果schema中定义了）
      final minItems = fieldSchema['minItems'] as int?;
      if (minItems != null && minItems > 0) {
        listValidators.add(Validators.delegate((AbstractControl control) {
          final value = control.value as List<String>?;
          return (value == null || value.length < minItems)
              ? <String, dynamic>{
                  'minItems': {
                    'requiredLength': minItems,
                    'actualLength': value?.length ?? 0
                  }
                }
              : null;
        }));
      }

      // 对于maxItems验证
      final maxItems = fieldSchema['maxItems'] as int?;
      if (maxItems != null && maxItems > 0) {
        listValidators.add(Validators.delegate((AbstractControl control) {
          final value = control.value as List<String>?;
          return (value != null && value.length > maxItems)
              ? <String, dynamic>{
                  'maxItems': {
                    'requiredLength': maxItems,
                    'actualLength': value.length
                  }
                }
              : null;
        }));
      }

      debugPrint(
          '[DEBUG] Creating FormControl<List<String>> for array field with ${initialList.length} items');
      return FormControl<List<String>>(
        value: initialList,
        validators: listValidators,
      );
    }

    // 对于复杂数组（对象数组等），继续使用 FormArray
    final List<AbstractControl<dynamic>> controls = [];

    if (initialValue is List) {
      for (final item in initialValue) {
        if (items != null) {
          controls.add(_createControlForField(
            fieldSchema: items,
            initialValue: item,
          ));
        } else {
          controls.add(FormControl<dynamic>(value: item));
        }
      }
    }

    // 数组长度验证 - 简化版本
    final minItems = fieldSchema['minItems'] as int?;
    final maxItems = fieldSchema['maxItems'] as int?;

    if (minItems != null) {
      // TODO: 添加数组最小长度验证
    }

    if (maxItems != null) {
      // TODO: 添加数组最大长度验证
    }

    return FormArray<dynamic>(
      controls,
      validators: validators,
    );
  }

  /// 创建对象控件 - 递归构建嵌套FormGroup
  static FormGroup _createObjectControl(
    Map<String, dynamic> fieldSchema,
    dynamic initialValue,
    List<Validator<dynamic>> validators,
  ) {
    return buildFormFromSchema(
      schema: fieldSchema,
      initialData: initialValue is Map<String, dynamic> ? initialValue : null,
    );
  }

  /// 获取字段的UI配置 - 支持点号路径访问和智能placeholder生成
  static Map<String, dynamic> getFieldUIConfig(
    String fieldPath,
    Map<String, dynamic> fieldSchema,
    Map<String, dynamic>? uiSchema,
  ) {
    final config = Map<String, dynamic>.from(fieldSchema);

    // 合并UI schema配置
    final fieldUIConfig = _safeMapCast(uiSchema?['properties']?[fieldPath]);
    if (fieldUIConfig != null) {
      config.addAll(fieldUIConfig);
    }

    // 从sections中查找字段配置 - 直接使用点号路径
    final sections = _safeMapCast(uiSchema?['ui:sections']);
    if (sections != null) {
      for (final section in sections.values) {
        final sectionConfig = _safeMapCast(section);
        if (sectionConfig == null) continue;
        final fields = _safeMapCast(sectionConfig['ui:fields']);

        // 直接查找点号路径字段配置
        final fieldConfig =
            fields != null ? _safeMapCast(fields[fieldPath]) : null;
        if (fieldConfig != null) {
          config.addAll(fieldConfig);
        }
      }
    }

    // 智能生成placeholder（如果配置中没有明确指定）
    if (!config.containsKey('placeholder') || config['placeholder'] == null) {
      config['placeholder'] = UITextConstants.getPlaceholder(
        fieldConfig: config,
        fieldName: fieldPath,
        fieldType: config['type'] as String?,
      );
    }

    return config;
  }

  /// 获取增强的字段UI配置，包含所有UI提示文本
  static Map<String, dynamic> getEnhancedFieldUIConfig(
    String fieldPath,
    Map<String, dynamic> fieldSchema,
    Map<String, dynamic>? uiSchema,
  ) {
    final config = getFieldUIConfig(fieldPath, fieldSchema, uiSchema);
    
    // 确保有合适的帮助文本
    if (!config.containsKey('help_text') && !config.containsKey('description')) {
      final inferredWidget = inferWidgetType(config);
      final helpText = UITextConstants.helpTexts[inferredWidget];
      if (helpText != null) {
        config['help_text'] = helpText;
      }
    }
    
    return config;
  }

  /// 根据点号路径获取嵌套字段的Schema配置
  static Map<String, dynamic> getNestedFieldSchema(
    String fieldPath,
    Map<String, dynamic> rootSchema,
  ) {
    final parts = fieldPath.split('.');
    Map<String, dynamic> currentSchema = rootSchema;

    for (final part in parts) {
      final properties = _safeMapCast(currentSchema['properties']) ?? {};
      currentSchema = _safeMapCast(properties[part]) ?? {};
      if (currentSchema.isEmpty) break;
    }

    return currentSchema;
  }

  /// 推断Widget类型
  static String inferWidgetType(Map<String, dynamic> fieldSchema) {
    // 优先使用明确指定的widget类型
    final explicitWidget = fieldSchema['ui:widget'] as String?;
    if (explicitWidget != null) {
      debugPrint('[DEBUG] Using explicit widget type: $explicitWidget');
      return explicitWidget;
    }

    final type = fieldSchema['type'] as String?;
    debugPrint('[DEBUG] Inferring widget type for field type: $type');

    switch (type) {
      case 'boolean':
        return 'switch';

      case 'integer':
      case 'number':
        // 如果有范围限制且范围合理，使用slider
        final minimum = fieldSchema['minimum'] as num?;
        final maximum = fieldSchema['maximum'] as num?;
        if (minimum != null && maximum != null && (maximum - minimum) <= 1000) {
          return 'slider';
        }
        return 'number_input';

      case 'array':
        final items = _safeMapCast(fieldSchema['items']);
        if (items != null && items['type'] == 'string') {
          debugPrint(
              '[DEBUG] Array of strings detected, using tag_input widget');
          return 'tag_input';
        }
        debugPrint('[DEBUG] Complex array detected, using array_input widget');
        return 'array_input';

      case 'string':
        // 检查格式提示
        final format = fieldSchema['format'] as String?;
        if (format == 'email') return 'email_input';
        if (format == 'uri') return 'url_input';
        if (format == 'password') return 'password_input';

        // 检查枚举选项
        if (fieldSchema.containsKey('enum')) {
          return 'select';
        }

        // 检查多行文本
        final multiline = fieldSchema['ui:multiline'] as bool?;
        if (multiline == true) {
          return 'textarea';
        }

        return 'text_input';

      case 'object':
        return 'object_editor';

      default:
        debugPrint(
            '[WARNING] Unknown field type: $type, falling back to text_input');
        return 'text_input';
    }
  }

  /// 从FormGroup提取数据 - 原生嵌套结构，类型安全转换
  static Map<String, dynamic> extractFormData(FormGroup form,
      [Map<String, dynamic>? schema]) {
    final data = <String, dynamic>{};

    for (final entry in form.controls.entries) {
      final key = entry.key;
      final control = entry.value;

      if (control is FormGroup) {
        // 递归处理嵌套表单组 - 直接保持嵌套结构
        final nestedSchema = _safeMapCast(schema?['properties']?[key]);
        final nestedData = extractFormData(control, nestedSchema);
        if (nestedData.isNotEmpty) {
          data[key] = nestedData;
        }
      } else if (control is FormArray) {
        // 处理数组类型控件
        final arrayData = control.controls.map((c) {
          if (c is FormGroup) {
            return extractFormData(c, null); // 数组项通常没有直接的schema引用
          }
          return c.value;
        }).toList();
        if (arrayData.isNotEmpty) {
          data[key] = arrayData;
        }
      } else {
        // 处理简单值，进行类型安全转换
        final value = control.value;
        if (value != null) {
          data[key] = _convertValueToSchemaType(value, key, schema);
        }
      }
    }

    return data;
  }

  /// 根据 Schema 将值转换为正确类型
  static dynamic _convertValueToSchemaType(
      dynamic value, String fieldName, Map<String, dynamic>? schema) {
    if (schema == null) return value;

    final properties = _safeMapCast(schema['properties']);
    if (properties == null) return value;

    final fieldSchema = _safeMapCast(properties[fieldName]);
    if (fieldSchema == null) return value;

    final expectedType = fieldSchema['type'] as String?;

    switch (expectedType) {
      case 'integer':
        if (value is int) return value;
        if (value is double) return value.round();
        if (value is String) return int.tryParse(value) ?? value;
        if (value is num) return value.toInt();
        break;

      case 'number':
        if (value is num) return value;
        if (value is String) return double.tryParse(value) ?? value;
        break;

      case 'string':
        if (value is String) return value;
        return value.toString();

      case 'boolean':
        if (value is bool) return value;
        if (value is String) {
          return value.toLowerCase() == 'true';
        }
        break;
    }

    return value;
  }
}
