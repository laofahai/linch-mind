import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:reactive_forms/reactive_forms.dart';
import '../../services/form_builder_service.dart';

/// 基于reactive_forms的配置组件库
class ReactiveConfigWidgets {
  /// 构建字段组件
  static Widget buildFieldWidget({
    required String fieldName,
    required Map<String, dynamic> fieldConfig,
    required BuildContext context,
  }) {
    final widgetType = FormBuilderService.inferWidgetType(fieldConfig);

    switch (widgetType) {
      case 'text_input':
        return _buildTextInput(fieldName, fieldConfig);
      case 'textarea':
        return _buildTextArea(fieldName, fieldConfig);
      case 'number_input':
        return _buildNumberInput(fieldName, fieldConfig);
      case 'switch':
        return _buildSwitch(fieldName, fieldConfig);
      case 'slider':
        return _buildSlider(fieldName, fieldConfig);
      case 'select':
        return _buildSelect(fieldName, fieldConfig);
      case 'tag_input':
        return _buildTagInput(fieldName, fieldConfig);
      case 'email_input':
        return _buildEmailInput(fieldName, fieldConfig);
      case 'url_input':
        return _buildUrlInput(fieldName, fieldConfig);
      case 'password_input':
        return _buildPasswordInput(fieldName, fieldConfig);
      case 'array_input':
        return _buildArrayInput(fieldName, fieldConfig);
      case 'object_editor':
        return _buildObjectEditor(fieldName, fieldConfig);
      default:
        return _buildTextInput(fieldName, fieldConfig);
    }
  }

  /// 文本输入框
  static Widget _buildTextInput(String fieldName, Map<String, dynamic> config) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ReactiveTextField<String>(
          formControlName: fieldName,
          decoration: InputDecoration(
            labelText: config['title'],
            hintText: config['placeholder'],
            helperText: config['description'] ?? config['help_text'],
            border: const OutlineInputBorder(),
          ),
          validationMessages: _getValidationMessages(),
        ),
      ],
    );
  }

  /// 多行文本框
  static Widget _buildTextArea(String fieldName, Map<String, dynamic> config) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ReactiveTextField<String>(
          formControlName: fieldName,
          maxLines: config['ui:rows'] ?? 4,
          decoration: InputDecoration(
            labelText: config['title'],
            hintText: config['placeholder'],
            helperText: config['description'] ?? config['help_text'],
            border: const OutlineInputBorder(),
            alignLabelWithHint: true,
          ),
          validationMessages: _getValidationMessages(),
        ),
      ],
    );
  }

  /// 数字输入框
  static Widget _buildNumberInput(
      String fieldName, Map<String, dynamic> config) {
    final isInteger = config['type'] == 'integer';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ReactiveTextField<num>(
          formControlName: fieldName,
          keyboardType: isInteger
              ? TextInputType.number
              : const TextInputType.numberWithOptions(decimal: true),
          inputFormatters: isInteger
              ? [FilteringTextInputFormatter.digitsOnly]
              : [FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d*'))],
          decoration: InputDecoration(
            labelText: config['title'],
            hintText: config['placeholder'],
            helperText: config['description'] ?? config['help_text'],
            suffixText: config['ui:unit'],
            border: const OutlineInputBorder(),
          ),
          validationMessages: _getValidationMessages(),
        ),
      ],
    );
  }

  /// 开关组件
  static Widget _buildSwitch(String fieldName, Map<String, dynamic> config) {
    return ReactiveSwitchListTile(
      formControlName: fieldName,
      title: Text(config['title'] ?? fieldName),
      subtitle: config['description'] != null || config['help_text'] != null
          ? Text(config['description'] ?? config['help_text'])
          : null,
    );
  }

  /// 滑块组件
  static Widget _buildSlider(String fieldName, Map<String, dynamic> config) {
    final minimum = (config['minimum'] ?? 0).toDouble();
    final maximum = (config['maximum'] ?? 100).toDouble();
    final step = (config['ui:step'] ?? 1.0).toDouble();
    final unit = config['ui:unit'] as String?;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          config['title'] ?? fieldName,
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
        ),
        if (config['description'] != null || config['help_text'] != null) ...[
          const SizedBox(height: 4),
          Text(
            config['description'] ?? config['help_text'],
            style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
          ),
        ],
        const SizedBox(height: 8),
        ReactiveSlider(
          formControlName: fieldName,
          min: minimum,
          max: maximum,
          divisions: ((maximum - minimum) / step).round(),
          labelBuilder: (value) =>
              '${value.toStringAsFixed(step < 1 ? 1 : 0)}${unit ?? ''}',
        ),
        // 数字输入框用于精确输入
        Row(
          children: [
            Expanded(child: Container()), // 占位
            SizedBox(
              width: 100,
              child: ReactiveTextField<num>(
                formControlName: fieldName,
                keyboardType:
                    const TextInputType.numberWithOptions(decimal: true),
                decoration: InputDecoration(
                  isDense: true,
                  suffixText: unit,
                  border: const OutlineInputBorder(),
                ),
                validationMessages: _getValidationMessages(),
              ),
            ),
          ],
        ),
      ],
    );
  }

  /// 下拉选择框
  static Widget _buildSelect(String fieldName, Map<String, dynamic> config) {
    final enumValues = config['enum'] as List? ?? [];
    final enumNames = config['enumNames'] as List? ?? enumValues;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ReactiveDropdownField<String>(
          formControlName: fieldName,
          decoration: InputDecoration(
            labelText: config['title'],
            helperText: config['description'] ?? config['help_text'],
            border: const OutlineInputBorder(),
          ),
          items: enumValues
              .asMap()
              .entries
              .map((entry) => DropdownMenuItem<String>(
                    value: entry.value.toString(),
                    child: Text(enumNames.length > entry.key
                        ? enumNames[entry.key].toString()
                        : entry.value.toString()),
                  ))
              .toList(),
          validationMessages: _getValidationMessages(),
        ),
      ],
    );
  }

  /// 标签输入组件
  static Widget _buildTagInput(String fieldName, Map<String, dynamic> config) {
    return _ReactiveTagInput(
      formControlName: fieldName,
      fieldConfig: config,
    );
  }

  /// 邮箱输入框
  static Widget _buildEmailInput(
      String fieldName, Map<String, dynamic> config) {
    return ReactiveTextField<String>(
      formControlName: fieldName,
      keyboardType: TextInputType.emailAddress,
      decoration: InputDecoration(
        labelText: config['title'],
        hintText: config['placeholder'] ?? 'user@example.com',
        helperText: config['description'] ?? config['help_text'],
        prefixIcon: const Icon(Icons.email),
        border: const OutlineInputBorder(),
      ),
      validationMessages: _getValidationMessages(),
    );
  }

  /// URL输入框
  static Widget _buildUrlInput(String fieldName, Map<String, dynamic> config) {
    return ReactiveTextField<String>(
      formControlName: fieldName,
      keyboardType: TextInputType.url,
      decoration: InputDecoration(
        labelText: config['title'],
        hintText: config['placeholder'] ?? 'https://example.com',
        helperText: config['description'] ?? config['help_text'],
        prefixIcon: const Icon(Icons.link),
        border: const OutlineInputBorder(),
      ),
      validationMessages: _getValidationMessages(),
    );
  }

  /// 密码输入框
  static Widget _buildPasswordInput(
      String fieldName, Map<String, dynamic> config) {
    return _ReactivePasswordField(
      formControlName: fieldName,
      fieldConfig: config,
    );
  }

  /// 数组输入组件
  static Widget _buildArrayInput(
      String fieldName, Map<String, dynamic> config) {
    return _ReactiveArrayInput(
      formControlName: fieldName,
      fieldConfig: config,
    );
  }

  /// 对象编辑器
  static Widget _buildObjectEditor(
      String fieldName, Map<String, dynamic> config) {
    return _ReactiveObjectEditor(
      formControlName: fieldName,
      fieldConfig: config,
    );
  }

  /// 获取标准验证消息
  static Map<String, String Function(Object)> _getValidationMessages() {
    return {
      'required': (error) => '此项为必填项',
      'email': (error) => '请输入有效的邮箱地址',
      'minLength': (error) => '最少需要 ${(error as Map)['requiredLength']} 个字符',
      'maxLength': (error) => '最多允许 ${(error as Map)['requiredLength']} 个字符',
      'min': (error) => '不能小于 ${(error as Map)['min']}',
      'max': (error) => '不能大于 ${(error as Map)['max']}',
      'pattern': (error) => '格式不正确',
      'uri': (error) => '请输入有效的URL地址',
    };
  }
}

/// 标签输入组件
class _ReactiveTagInput extends ReactiveFormField<List<String>, List<String>> {
  final Map<String, dynamic> fieldConfig;

  _ReactiveTagInput({
    required String formControlName,
    required this.fieldConfig,
  }) : super(
          formControlName: formControlName,
          builder: (field) {
            return _TagInputWidget(
              value: field.value ?? [],
              onChanged: field.didChange,
              fieldConfig: fieldConfig,
              hasError: field.control.invalid,
              errorText: field.errorText,
            );
          },
        );
}

class _TagInputWidget extends StatefulWidget {
  final List<String> value;
  final ValueChanged<List<String>> onChanged;
  final Map<String, dynamic> fieldConfig;
  final bool hasError;
  final String? errorText;

  const _TagInputWidget({
    required this.value,
    required this.onChanged,
    required this.fieldConfig,
    required this.hasError,
    this.errorText,
  });

  @override
  State<_TagInputWidget> createState() => _TagInputWidgetState();
}

class _TagInputWidgetState extends State<_TagInputWidget> {
  late List<String> _tags;
  final TextEditingController _controller = TextEditingController();

  @override
  void initState() {
    super.initState();
    _tags = List<String>.from(widget.value);
  }

  @override
  void didUpdateWidget(_TagInputWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.value != oldWidget.value) {
      _tags = List<String>.from(widget.value);
    }
  }

  void _addTag(String tag) {
    final trimmed = tag.trim();
    if (trimmed.isNotEmpty && !_tags.contains(trimmed)) {
      setState(() {
        _tags.add(trimmed);
        widget.onChanged(_tags);
      });
      _controller.clear();
    }
  }

  void _removeTag(int index) {
    setState(() {
      _tags.removeAt(index);
      widget.onChanged(_tags);
    });
  }

  @override
  Widget build(BuildContext context) {
    final predefinedTags =
        widget.fieldConfig['predefined_tags'] as List<dynamic>? ?? [];
    final allowCustom = widget.fieldConfig['allow_custom'] as bool? ?? true;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          widget.fieldConfig['title'] ?? '标签',
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
        ),
        if (widget.fieldConfig['description'] != null ||
            widget.fieldConfig['help_text'] != null) ...[
          const SizedBox(height: 4),
          Text(
            widget.fieldConfig['description'] ??
                widget.fieldConfig['help_text'],
            style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
          ),
        ],
        const SizedBox(height: 8),

        // 预定义标签
        if (predefinedTags.isNotEmpty) ...[
          Text('常用选项:', style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 4),
          Wrap(
            spacing: 8,
            runSpacing: 4,
            children: predefinedTags.map<Widget>((tag) {
              final isSelected = _tags.contains(tag.toString());
              return FilterChip(
                label: Text(tag.toString()),
                selected: isSelected,
                onSelected: (selected) {
                  if (selected) {
                    _addTag(tag.toString());
                  } else {
                    _tags.remove(tag.toString());
                    setState(() {
                      widget.onChanged(_tags);
                    });
                  }
                },
              );
            }).toList(),
          ),
          const SizedBox(height: 12),
        ],

        // 自定义输入
        if (allowCustom) ...[
          TextField(
            controller: _controller,
            decoration: InputDecoration(
              hintText: widget.fieldConfig['placeholder'] ?? '输入后按回车添加',
              border: OutlineInputBorder(
                borderSide: BorderSide(
                  color: widget.hasError ? Colors.red : Colors.grey,
                ),
              ),
              suffixIcon: IconButton(
                icon: const Icon(Icons.add),
                onPressed: () => _addTag(_controller.text),
              ),
              errorText: widget.errorText,
            ),
            onSubmitted: _addTag,
          ),
          const SizedBox(height: 8),
        ],

        // 当前标签
        if (_tags.isNotEmpty) ...[
          Text('已选择:', style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 4),
          Wrap(
            spacing: 8,
            runSpacing: 4,
            children: _tags.asMap().entries.map<Widget>((entry) {
              final index = entry.key;
              final tag = entry.value;
              return Chip(
                label: Text(tag),
                deleteIcon: const Icon(Icons.close, size: 18),
                onDeleted: () => _removeTag(index),
              );
            }).toList(),
          ),
        ],
      ],
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}

/// 密码输入组件
class _ReactivePasswordField extends ReactiveFormField<String, String> {
  final Map<String, dynamic> fieldConfig;

  _ReactivePasswordField({
    required String formControlName,
    required this.fieldConfig,
  }) : super(
          formControlName: formControlName,
          builder: (field) {
            return _PasswordInputWidget(
              value: field.value ?? '',
              onChanged: field.didChange,
              fieldConfig: fieldConfig,
              hasError: field.control.invalid,
              errorText: field.errorText,
            );
          },
        );
}

class _PasswordInputWidget extends StatefulWidget {
  final String value;
  final ValueChanged<String> onChanged;
  final Map<String, dynamic> fieldConfig;
  final bool hasError;
  final String? errorText;

  const _PasswordInputWidget({
    required this.value,
    required this.onChanged,
    required this.fieldConfig,
    required this.hasError,
    this.errorText,
  });

  @override
  State<_PasswordInputWidget> createState() => _PasswordInputWidgetState();
}

class _PasswordInputWidgetState extends State<_PasswordInputWidget> {
  bool _obscureText = true;
  late TextEditingController _controller;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.value);
    _controller.addListener(() {
      widget.onChanged(_controller.text);
    });
  }

  @override
  void didUpdateWidget(_PasswordInputWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.value != _controller.text) {
      _controller.text = widget.value;
    }
  }

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: _controller,
      obscureText: _obscureText,
      decoration: InputDecoration(
        labelText: widget.fieldConfig['title'],
        hintText: widget.fieldConfig['placeholder'],
        helperText: widget.fieldConfig['description'] ??
            widget.fieldConfig['help_text'],
        prefixIcon: const Icon(Icons.lock),
        suffixIcon: IconButton(
          icon: Icon(_obscureText ? Icons.visibility : Icons.visibility_off),
          onPressed: () {
            setState(() {
              _obscureText = !_obscureText;
            });
          },
        ),
        border: const OutlineInputBorder(),
        errorText: widget.errorText,
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}

/// 数组输入组件
class _ReactiveArrayInput
    extends ReactiveFormField<List<dynamic>, List<dynamic>> {
  final Map<String, dynamic> fieldConfig;

  _ReactiveArrayInput({
    required String formControlName,
    required this.fieldConfig,
  }) : super(
          formControlName: formControlName,
          builder: (field) {
            return _ArrayInputWidget(
              value: field.value ?? <dynamic>[],
              onChanged: (List<dynamic> value) => field.didChange(value),
              fieldConfig: fieldConfig,
              hasError: field.control.invalid,
              errorText: field.errorText,
            );
          },
        );
}

class _ArrayInputWidget extends StatefulWidget {
  final List<dynamic> value;
  final ValueChanged<List<dynamic>> onChanged;
  final Map<String, dynamic> fieldConfig;
  final bool hasError;
  final String? errorText;

  const _ArrayInputWidget({
    required this.value,
    required this.onChanged,
    required this.fieldConfig,
    required this.hasError,
    this.errorText,
  });

  @override
  State<_ArrayInputWidget> createState() => _ArrayInputWidgetState();
}

class _ArrayInputWidgetState extends State<_ArrayInputWidget> {
  late List<dynamic> _items;

  @override
  void initState() {
    super.initState();
    _items = List<dynamic>.from(widget.value);
  }

  @override
  void didUpdateWidget(_ArrayInputWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.value != oldWidget.value) {
      _items = List<dynamic>.from(widget.value);
    }
  }

  void _addItem() {
    setState(() {
      final items = widget.fieldConfig['items'] as Map<String, dynamic>?;
      final defaultValue = items?['type'] == 'string'
          ? ''
          : items?['type'] == 'number'
              ? 0
              : null;
      _items.add(defaultValue);
      widget.onChanged(_items);
    });
  }

  void _removeItem(int index) {
    setState(() {
      _items.removeAt(index);
      widget.onChanged(_items);
    });
  }

  void _updateItem(int index, dynamic value) {
    setState(() {
      _items[index] = value;
      widget.onChanged(_items);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              widget.fieldConfig['title'] ?? '列表',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
            ),
            IconButton(
              icon: const Icon(Icons.add),
              onPressed: _addItem,
            ),
          ],
        ),
        if (widget.fieldConfig['description'] != null ||
            widget.fieldConfig['help_text'] != null) ...[
          const SizedBox(height: 4),
          Text(
            widget.fieldConfig['description'] ??
                widget.fieldConfig['help_text'],
            style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
          ),
        ],
        const SizedBox(height: 8),

        // 数组项
        ..._items.asMap().entries.map((entry) {
          final index = entry.key;
          final item = entry.value;

          return Card(
            margin: const EdgeInsets.only(bottom: 8),
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller:
                          TextEditingController(text: item?.toString() ?? ''),
                      onChanged: (value) => _updateItem(index, value),
                      decoration: InputDecoration(
                        hintText: '项目 ${index + 1}',
                        border: const OutlineInputBorder(),
                        isDense: true,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    icon: const Icon(Icons.delete, color: Colors.red),
                    onPressed: () => _removeItem(index),
                  ),
                ],
              ),
            ),
          );
        }),

        if (widget.errorText != null) ...[
          const SizedBox(height: 8),
          Text(
            widget.errorText!,
            style: TextStyle(
              color: Theme.of(context).colorScheme.error,
              fontSize: 12,
            ),
          ),
        ],
      ],
    );
  }
}

/// 对象编辑器
class _ReactiveObjectEditor
    extends ReactiveFormField<Map<String, dynamic>, Map<String, dynamic>> {
  final Map<String, dynamic> fieldConfig;

  _ReactiveObjectEditor({
    required String formControlName,
    required this.fieldConfig,
  }) : super(
          formControlName: formControlName,
          builder: (field) {
            return _ObjectEditorWidget(
              value: field.value ?? <String, dynamic>{},
              onChanged: (Map<String, dynamic> value) => field.didChange(value),
              fieldConfig: fieldConfig,
              hasError: field.control.invalid,
              errorText: field.errorText,
            );
          },
        );
}

class _ObjectEditorWidget extends StatefulWidget {
  final Map<String, dynamic> value;
  final ValueChanged<Map<String, dynamic>> onChanged;
  final Map<String, dynamic> fieldConfig;
  final bool hasError;
  final String? errorText;

  const _ObjectEditorWidget({
    required this.value,
    required this.onChanged,
    required this.fieldConfig,
    required this.hasError,
    this.errorText,
  });

  @override
  State<_ObjectEditorWidget> createState() => _ObjectEditorWidgetState();
}

class _ObjectEditorWidgetState extends State<_ObjectEditorWidget> {
  late Map<String, dynamic> _data;

  @override
  void initState() {
    super.initState();
    _data = Map<String, dynamic>.from(widget.value);
  }

  @override
  void didUpdateWidget(_ObjectEditorWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.value != oldWidget.value) {
      _data = Map<String, dynamic>.from(widget.value);
    }
  }

  void _addProperty() {
    setState(() {
      _data[''] = '';
      widget.onChanged(_data);
    });
  }

  void _removeProperty(String key) {
    setState(() {
      _data.remove(key);
      widget.onChanged(_data);
    });
  }

  void _updateProperty(String oldKey, String newKey, dynamic value) {
    setState(() {
      if (oldKey != newKey) {
        _data.remove(oldKey);
      }
      _data[newKey] = value;
      widget.onChanged(_data);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              widget.fieldConfig['title'] ?? '对象',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
            ),
            IconButton(
              icon: const Icon(Icons.add),
              onPressed: _addProperty,
            ),
          ],
        ),
        if (widget.fieldConfig['description'] != null ||
            widget.fieldConfig['help_text'] != null) ...[
          const SizedBox(height: 4),
          Text(
            widget.fieldConfig['description'] ??
                widget.fieldConfig['help_text'],
            style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
          ),
        ],
        const SizedBox(height: 8),

        // 对象属性
        ..._data.entries.map((entry) {
          final key = entry.key;
          final value = entry.value;

          return Card(
            margin: const EdgeInsets.only(bottom: 8),
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Row(
                children: [
                  Expanded(
                    flex: 2,
                    child: TextField(
                      controller: TextEditingController(text: key),
                      onChanged: (newKey) =>
                          _updateProperty(key, newKey, value),
                      decoration: const InputDecoration(
                        labelText: '属性名',
                        border: OutlineInputBorder(),
                        isDense: true,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    flex: 3,
                    child: TextField(
                      controller:
                          TextEditingController(text: value?.toString() ?? ''),
                      onChanged: (newValue) =>
                          _updateProperty(key, key, newValue),
                      decoration: const InputDecoration(
                        labelText: '值',
                        border: OutlineInputBorder(),
                        isDense: true,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    icon: const Icon(Icons.delete, color: Colors.red),
                    onPressed: () => _removeProperty(key),
                  ),
                ],
              ),
            ),
          );
        }),

        if (widget.errorText != null) ...[
          const SizedBox(height: 8),
          Text(
            widget.errorText!,
            style: TextStyle(
              color: Theme.of(context).colorScheme.error,
              fontSize: 12,
            ),
          ),
        ],
      ],
    );
  }
}
