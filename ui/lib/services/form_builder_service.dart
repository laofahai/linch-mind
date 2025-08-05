import 'package:reactive_forms/reactive_forms.dart';

/// JSON Schema 到 ReactiveForm 的映射服务
class FormBuilderService {
  /// 从 JSON Schema 构建 FormGroup
  static FormGroup buildFormFromSchema({
    required Map<String, dynamic> schema,
    Map<String, dynamic>? initialData,
    Map<String, dynamic>? uiSchema,
  }) {
    final properties = schema['properties'] as Map<String, dynamic>? ?? {};
    final required = List<String>.from(schema['required'] ?? []);
    final controls = <String, AbstractControl<dynamic>>{};

    for (final entry in properties.entries) {
      final fieldName = entry.key;
      final fieldSchema = entry.value as Map<String, dynamic>;
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

  /// 创建数值控件
  static FormControl<num> _createNumberControl(
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

    final isInteger = fieldSchema['type'] == 'integer';
    num? value;
    
    if (initialValue != null) {
      if (isInteger) {
        value = initialValue is int ? initialValue : int.tryParse(initialValue.toString());
      } else {
        value = initialValue is num ? initialValue : double.tryParse(initialValue.toString());
      }
    }

    return FormControl<num>(
      value: value,
      validators: validators,
    );
  }

  /// 创建数组控件
  static FormArray<dynamic> _createArrayControl(
    Map<String, dynamic> fieldSchema,
    dynamic initialValue,
    List<Validator<dynamic>> validators,
  ) {
    final List<AbstractControl<dynamic>> controls = [];
    final items = fieldSchema['items'] as Map<String, dynamic>?;
    
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

  /// 创建对象控件
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

  /// 获取字段的UI配置
  static Map<String, dynamic> getFieldUIConfig(
    String fieldName,
    Map<String, dynamic> fieldSchema,
    Map<String, dynamic>? uiSchema,
  ) {
    final config = Map<String, dynamic>.from(fieldSchema);
    
    // 合并UI schema配置
    final fieldUIConfig = uiSchema?['properties']?[fieldName] as Map<String, dynamic>?;
    if (fieldUIConfig != null) {
      config.addAll(fieldUIConfig);
    }

    // 从sections中查找字段配置
    final sections = uiSchema?['ui:sections'] as Map<String, dynamic>?;
    if (sections != null) {
      for (final section in sections.values) {
        final sectionConfig = section as Map<String, dynamic>;
        final fields = sectionConfig['ui:fields'] as Map<String, dynamic>?;
        final fieldConfig = fields?[fieldName] as Map<String, dynamic>?;
        if (fieldConfig != null) {
          config.addAll(fieldConfig);
        }
      }
    }

    return config;
  }

  /// 推断Widget类型
  static String inferWidgetType(Map<String, dynamic> fieldSchema) {
    // 优先使用明确指定的widget类型
    final explicitWidget = fieldSchema['ui:widget'] as String?;
    if (explicitWidget != null) {
      return explicitWidget;
    }

    final type = fieldSchema['type'] as String?;
    
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
        final items = fieldSchema['items'] as Map<String, dynamic>?;
        if (items?['type'] == 'string') {
          return 'tag_input';
        }
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
        return 'text_input';
    }
  }

  /// 从FormGroup提取数据
  static Map<String, dynamic> extractFormData(FormGroup form) {
    final data = <String, dynamic>{};
    
    for (final entry in form.controls.entries) {
      final key = entry.key;
      final control = entry.value;
      
      if (control is FormGroup) {
        data[key] = extractFormData(control);
      } else if (control is FormArray) {
        data[key] = control.controls.map((c) {
          if (c is FormGroup) {
            return extractFormData(c);
          }
          return c.value;
        }).toList();
      } else {
        data[key] = control.value;
      }
    }
    
    return data;
  }
}