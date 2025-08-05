import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:convert';

/// 自定义配置组件工厂
class CustomConfigWidgetFactory {
  static final Map<String, Function> _customWidgets = {};
  
  /// 注册自定义组件
  static void registerWidget(String widgetType, Function builder) {
    _customWidgets[widgetType] = builder;
  }
  
  /// 根据字段schema自动推断widget类型
  static String _inferWidgetType(Map<String, dynamic> fieldSchema) {
    final String? type = fieldSchema['type'];
    
    switch (type) {
      case 'boolean':
        return 'switch';
      
      case 'integer':
      case 'number':
        // 如果有范围限制，使用slider
        if (fieldSchema.containsKey('minimum') && fieldSchema.containsKey('maximum')) {
          final min = fieldSchema['minimum'];
          final max = fieldSchema['maximum'];
          // 合理的范围使用slider，过大范围使用数字输入
          if (min != null && max != null && (max - min) <= 1000) {
            return 'slider';
          }
        }
        return 'number_input';
      
      case 'array':
        final items = fieldSchema['items'] as Map<String, dynamic>?;
        if (items?['type'] == 'string') {
          return 'tag_input';
        }
        return 'text_input';
      
      case 'string':
        // 检查格式提示
        final format = fieldSchema['format'];
        if (format == 'email') return 'email_input';
        if (format == 'uri') return 'url_input';
        if (format == 'password') return 'password_input';
        
        // 检查枚举选项
        if (fieldSchema.containsKey('enum')) {
          return 'select';
        }
        
        return 'text_input';
      
      case 'object':
        return 'object_editor';
      
      default:
        return 'text_input';
    }
  }
  
  /// 构建配置字段组件
  static Widget buildConfigField({
    required String fieldName,
    required Map<String, dynamic> fieldSchema,
    required dynamic currentValue,
    required Function(dynamic) onChanged,
    required BuildContext context,
  }) {
    // 优先使用UI schema中的widget类型，然后是schema中的widget，最后根据类型自动推断
    String widgetType = fieldSchema['ui:widget'] ?? 
                       fieldSchema['widget'] ?? 
                       _inferWidgetType(fieldSchema);
    
    switch (widgetType) {
      case 'custom_widget':
        return _buildCustomWidget(
          fieldName: fieldName,
          fieldSchema: fieldSchema,
          currentValue: currentValue,
          onChanged: onChanged,
          context: context,
        );
      
      case 'iframe_widget':
        return _buildIframeWidget(
          fieldName: fieldName,
          fieldSchema: fieldSchema,
          currentValue: currentValue,
          onChanged: onChanged,
          context: context,
        );
      
      case 'cron_editor':
        return _buildCronEditor(
          fieldName: fieldName,
          fieldSchema: fieldSchema,
          currentValue: currentValue,
          onChanged: onChanged,
          context: context,
        );
      
      case 'code_editor':
        return _buildCodeEditor(
          fieldName: fieldName,
          fieldSchema: fieldSchema,
          currentValue: currentValue,
          onChanged: onChanged,
          context: context,
        );
      
      case 'api_endpoint_builder':
        return _buildApiEndpointBuilder(
          fieldName: fieldName,
          fieldSchema: fieldSchema,
          currentValue: currentValue,
          onChanged: onChanged,
          context: context,
        );
      
      case 'dynamic_form':
        return _buildDynamicForm(
          fieldName: fieldName,
          fieldSchema: fieldSchema,
          currentValue: currentValue,
          onChanged: onChanged,
          context: context,
        );
      
      default:
        return _buildBasicWidget(
          fieldName: fieldName,
          fieldSchema: fieldSchema,
          currentValue: currentValue,
          onChanged: onChanged,
          context: context,
          widgetType: widgetType,
        );
    }
  }
  
  /// 构建自定义组件
  static Widget _buildCustomWidget({
    required String fieldName,
    required Map<String, dynamic> fieldSchema,
    required dynamic currentValue,
    required Function(dynamic) onChanged,
    required BuildContext context,
  }) {
    final String? customComponentName = fieldSchema['custom_component_name'];
    final Map<String, dynamic>? customConfig = fieldSchema['custom_widget_config'];
    
    if (customComponentName != null && _customWidgets.containsKey(customComponentName)) {
      return _customWidgets[customComponentName]!(
        fieldName: fieldName,
        fieldSchema: fieldSchema,
        currentValue: currentValue,
        onChanged: onChanged,
        context: context,
        customConfig: customConfig,
      );
    }
    
    // 回退到基础组件
    return _buildBasicWidget(
      fieldName: fieldName,
      fieldSchema: fieldSchema,
      currentValue: currentValue,
      onChanged: onChanged,
      context: context,
      widgetType: 'text_input',
    );
  }
  
  /// 构建iframe组件
  static Widget _buildIframeWidget({
    required String fieldName,
    required Map<String, dynamic> fieldSchema,
    required dynamic currentValue,
    required Function(dynamic) onChanged,
    required BuildContext context,
  }) {
    final String? iframeSrc = fieldSchema['iframe_src'];
    
    return Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              fieldSchema['title'] ?? fieldName,
              style: Theme.of(context).textTheme.titleMedium,
            ),
          ),
          if (iframeSrc != null)
            SizedBox(
              height: 400,
              child: Container(
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey.shade300),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: _IframeWebView(
                    src: iframeSrc,
                    onDataChange: onChanged,
                    initialData: currentValue,
                  ),
                ),
              ),
            ),
          if (fieldSchema['help_text'] != null)
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Text(
                fieldSchema['help_text'],
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ),
        ],
      ),
    );
  }
  
  /// 构建Cron表达式编辑器
  static Widget _buildCronEditor({
    required String fieldName,
    required Map<String, dynamic> fieldSchema,
    required dynamic currentValue,
    required Function(dynamic) onChanged,
    required BuildContext context,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              fieldSchema['title'] ?? fieldName,
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            CronEditorWidget(
              initialValue: currentValue?.toString() ?? '0 0 * * *',
              onChanged: onChanged,
            ),
            if (fieldSchema['help_text'] != null) ...[
              const SizedBox(height: 8),
              Text(
                fieldSchema['help_text'],
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ],
        ),
      ),
    );
  }
  
  /// 构建代码编辑器
  static Widget _buildCodeEditor({
    required String fieldName,
    required Map<String, dynamic> fieldSchema,
    required dynamic currentValue,
    required Function(dynamic) onChanged,
    required BuildContext context,
  }) {
    final String language = fieldSchema['code_language'] ?? 'text';
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              fieldSchema['title'] ?? fieldName,
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            Container(
              height: 300,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey.shade300),
                borderRadius: BorderRadius.circular(8),
              ),
              child: CodeEditorWidget(
                language: language,
                initialValue: currentValue?.toString() ?? '',
                onChanged: onChanged,
              ),
            ),
            if (fieldSchema['help_text'] != null) ...[
              const SizedBox(height: 8),
              Text(
                fieldSchema['help_text'],
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ],
        ),
      ),
    );
  }
  
  /// 构建API端点构建器
  static Widget _buildApiEndpointBuilder({
    required String fieldName,
    required Map<String, dynamic> fieldSchema,
    required dynamic currentValue,
    required Function(dynamic) onChanged,
    required BuildContext context,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              fieldSchema['title'] ?? fieldName,
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 16),
            ApiEndpointBuilderWidget(
              initialConfig: currentValue is Map ? Map<String, dynamic>.from(currentValue) : {},
              onChanged: onChanged,
            ),
            if (fieldSchema['help_text'] != null) ...[
              const SizedBox(height: 8),
              Text(
                fieldSchema['help_text'],
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ],
        ),
      ),
    );
  }
  
  /// 构建动态表单
  static Widget _buildDynamicForm({
    required String fieldName,
    required Map<String, dynamic> fieldSchema,
    required dynamic currentValue,
    required Function(dynamic) onChanged,
    required BuildContext context,
  }) {
    final Map<String, dynamic>? formSchema = fieldSchema['custom_widget_config'];
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              fieldSchema['title'] ?? fieldName,
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 16),
            if (formSchema != null)
              DynamicFormWidget(
                schema: formSchema,
                initialData: currentValue is Map ? Map<String, dynamic>.from(currentValue) : {},
                onChanged: onChanged,
              ),
            if (fieldSchema['help_text'] != null) ...[
              const SizedBox(height: 8),
              Text(
                fieldSchema['help_text'],
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ],
        ),
      ),
    );
  }
  
  /// 构建基础组件
  static Widget _buildBasicWidget({
    required String fieldName,
    required Map<String, dynamic> fieldSchema,
    required dynamic currentValue,
    required Function(dynamic) onChanged,
    required BuildContext context,
    required String widgetType,
  }) {
    // 这里实现基础组件的构建逻辑
    switch (widgetType) {
      case 'text_input':
        return TextFormField(
          initialValue: currentValue?.toString() ?? '',
          decoration: InputDecoration(
            labelText: fieldSchema['title'],
            hintText: fieldSchema['placeholder'],
            helperText: fieldSchema['help_text'],
          ),
          onChanged: onChanged,
        );
      
      case 'switch':
        return SwitchListTile(
          title: Text(fieldSchema['title'] ?? fieldName),
          subtitle: fieldSchema['help_text'] != null ? Text(fieldSchema['help_text']) : null,
          value: currentValue == true,
          onChanged: onChanged,
        );
      
      case 'slider':
        final double minValue = (fieldSchema['minimum'] ?? 0).toDouble();
        final double maxValue = (fieldSchema['maximum'] ?? 100).toDouble();
        final double step = (fieldSchema['ui:step'] ?? 1.0).toDouble();
        final String? unit = fieldSchema['ui:unit'];
        
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(fieldSchema['title'] ?? fieldName, style: Theme.of(context).textTheme.titleSmall),
            if (fieldSchema['help_text'] != null) ...[
              const SizedBox(height: 4),
              Text(fieldSchema['help_text'], style: Theme.of(context).textTheme.bodySmall),
              const SizedBox(height: 8),
            ],
            Row(
              children: [
                Expanded(
                  child: Slider(
                    value: (currentValue ?? minValue).toDouble().clamp(minValue, maxValue),
                    min: minValue,
                    max: maxValue,
                    divisions: ((maxValue - minValue) / step).round(),
                    label: '${currentValue ?? minValue}${unit ?? ''}',
                    onChanged: (value) => onChanged(value),
                  ),
                ),
                Container(
                  width: 80,
                  child: TextFormField(
                    initialValue: currentValue?.toString() ?? minValue.toString(),
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      suffix: unit != null ? Text(unit) : null,
                      isDense: true,
                      contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    ),
                    onChanged: (value) {
                      final numValue = double.tryParse(value);
                      if (numValue != null) onChanged(numValue.clamp(minValue, maxValue));
                    },
                  ),
                ),
              ],
            ),
          ],
        );
      
      case 'tag_input':
        return TagInputWidget(
          fieldName: fieldName,
          fieldSchema: fieldSchema,
          currentValue: currentValue,
          onChanged: onChanged,
        );
      
      case 'number_input':
        final int? minValue = fieldSchema['minimum'];
        final int? maxValue = fieldSchema['maximum'];
        
        return TextFormField(
          initialValue: currentValue?.toString() ?? '',
          keyboardType: TextInputType.number,
          decoration: InputDecoration(
            labelText: fieldSchema['title'],
            hintText: fieldSchema['placeholder'],
            helperText: fieldSchema['help_text'],
            suffixText: fieldSchema['ui:unit'],
          ),
          onChanged: (value) {
            final numValue = fieldSchema['type'] == 'integer' 
                ? int.tryParse(value) 
                : double.tryParse(value);
            if (numValue != null) {
              if (minValue != null && numValue < minValue) return;
              if (maxValue != null && numValue > maxValue) return;
              onChanged(numValue);
            }
          },
        );
      
      // ... 其他基础组件实现
      
      default:
        return TextFormField(
          initialValue: currentValue?.toString() ?? '',
          decoration: InputDecoration(
            labelText: fieldSchema['title'],
          ),
          onChanged: onChanged,
        );
    }
  }
}

/// iframe WebView组件
class _IframeWebView extends StatefulWidget {
  final String src;
  final Function(dynamic) onDataChange;
  final dynamic initialData;
  
  const _IframeWebView({
    required this.src,
    required this.onDataChange,
    this.initialData,
  });
  
  @override
  State<_IframeWebView> createState() => _IframeWebViewState();
}

class _IframeWebViewState extends State<_IframeWebView> {
  @override
  Widget build(BuildContext context) {
    // 实际实现需要使用webview_flutter插件
    return Container(
      color: Colors.grey.shade100,
      child: const Center(
        child: Text('WebView组件 - 需要webview_flutter插件'),
      ),
    );
  }
}

/// Cron表达式编辑器组件
class CronEditorWidget extends StatefulWidget {
  final String initialValue;
  final Function(String) onChanged;
  
  const CronEditorWidget({
    super.key,
    required this.initialValue,
    required this.onChanged,
  });
  
  @override
  State<CronEditorWidget> createState() => _CronEditorWidgetState();
}

class _CronEditorWidgetState extends State<CronEditorWidget> {
  late TextEditingController _controller;
  
  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.initialValue);
  }
  
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        TextFormField(
          controller: _controller,
          decoration: const InputDecoration(
            labelText: 'Cron表达式',
            hintText: '0 0 * * *',
          ),
          onChanged: widget.onChanged,
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.blue.shade50,
            borderRadius: BorderRadius.circular(4),
          ),
          child: const Text(
            '格式: 分 时 日 月 周\n例如: 0 9 * * 1-5 (工作日上午9点)',
            style: TextStyle(fontSize: 12),
          ),
        ),
      ],
    );
  }
  
  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}

/// 代码编辑器组件
class CodeEditorWidget extends StatefulWidget {
  final String language;
  final String initialValue;
  final Function(String) onChanged;
  
  const CodeEditorWidget({
    super.key,
    required this.language,
    required this.initialValue,
    required this.onChanged,
  });
  
  @override
  State<CodeEditorWidget> createState() => _CodeEditorWidgetState();
}

class _CodeEditorWidgetState extends State<CodeEditorWidget> {
  late TextEditingController _controller;
  
  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.initialValue);
  }
  
  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: _controller,
      maxLines: null,
      expands: true,
      decoration: InputDecoration(
        hintText: '输入${widget.language}代码...',
        border: InputBorder.none,
        contentPadding: const EdgeInsets.all(16),
      ),
      style: TextStyle(
        fontFamily: 'Monaco',
        fontSize: 14,
        color: Colors.grey.shade800,
      ),
      onChanged: widget.onChanged,
    );
  }
  
  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}

/// API端点构建器组件
class ApiEndpointBuilderWidget extends StatefulWidget {
  final Map<String, dynamic> initialConfig;
  final Function(Map<String, dynamic>) onChanged;
  
  const ApiEndpointBuilderWidget({
    super.key,
    required this.initialConfig,
    required this.onChanged,
  });
  
  @override
  State<ApiEndpointBuilderWidget> createState() => _ApiEndpointBuilderWidgetState();
}

class _ApiEndpointBuilderWidgetState extends State<ApiEndpointBuilderWidget> {
  late Map<String, dynamic> _config;
  
  @override
  void initState() {
    super.initState();
    _config = Map<String, dynamic>.from(widget.initialConfig);
  }
  
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // HTTP方法选择
        DropdownButtonFormField<String>(
          value: _config['method'] ?? 'GET',
          decoration: const InputDecoration(labelText: 'HTTP方法'),
          items: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
              .map((method) => DropdownMenuItem(value: method, child: Text(method)))
              .toList(),
          onChanged: (value) {
            setState(() {
              _config['method'] = value;
              widget.onChanged(_config);
            });
          },
        ),
        const SizedBox(height: 16),
        
        // URL输入
        TextFormField(
          initialValue: _config['url']?.toString() ?? '',
          decoration: const InputDecoration(labelText: 'API端点URL'),
          onChanged: (value) {
            _config['url'] = value;
            widget.onChanged(_config);
          },
        ),
        const SizedBox(height: 16),
        
        // 请求头编辑
        const Text('请求头', style: TextStyle(fontWeight: FontWeight.bold)),
        _buildKeyValueEditor(
          'headers',
          _config['headers'] as Map<String, dynamic>? ?? {},
        ),
        const SizedBox(height: 16),
        
        // 查询参数编辑
        const Text('查询参数', style: TextStyle(fontWeight: FontWeight.bold)),
        _buildKeyValueEditor(
          'params',
          _config['params'] as Map<String, dynamic>? ?? {},
        ),
      ],
    );
  }
  
  Widget _buildKeyValueEditor(String key, Map<String, dynamic> data) {
    return Column(
      children: [
        ...data.entries.map((entry) => Row(
          children: [
            Expanded(
              child: TextFormField(
                initialValue: entry.key,
                decoration: const InputDecoration(labelText: '键'),
                onChanged: (newKey) {
                  if (newKey != entry.key) {
                    data.remove(entry.key);
                    data[newKey] = entry.value;
                    _config[key] = data;
                    widget.onChanged(_config);
                  }
                },
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: TextFormField(
                initialValue: entry.value?.toString() ?? '',
                decoration: const InputDecoration(labelText: '值'),
                onChanged: (value) {
                  data[entry.key] = value;
                  _config[key] = data;
                  widget.onChanged(_config);
                },
              ),
            ),
            IconButton(
              icon: const Icon(Icons.delete),
              onPressed: () {
                setState(() {
                  data.remove(entry.key);
                  _config[key] = data;
                  widget.onChanged(_config);
                });
              },
            ),
          ],
        )),
        ElevatedButton.icon(
          onPressed: () {
            setState(() {
              data[''] = '';
              _config[key] = data;
              widget.onChanged(_config);
            });
          },
          icon: const Icon(Icons.add),
          label: const Text('添加'),
        ),
      ],
    );
  }
}

/// 标签输入组件
class TagInputWidget extends StatefulWidget {
  final String fieldName;
  final Map<String, dynamic> fieldSchema;
  final dynamic currentValue;
  final Function(dynamic) onChanged;
  
  const TagInputWidget({
    super.key,
    required this.fieldName,
    required this.fieldSchema,
    required this.currentValue,
    required this.onChanged,
  });
  
  @override
  State<TagInputWidget> createState() => _TagInputWidgetState();
}

class _TagInputWidgetState extends State<TagInputWidget> {
  late List<String> _tags;
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focusNode = FocusNode();
  
  @override
  void initState() {
    super.initState();
    _tags = List<String>.from(widget.currentValue ?? []);
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
    final predefinedTags = widget.fieldSchema['predefined_tags'] as List<dynamic>? ?? [];
    final allowCustom = widget.fieldSchema['allow_custom'] as bool? ?? true;
    final placeholder = widget.fieldSchema['placeholder'] as String? ?? '输入后按回车添加';
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          widget.fieldSchema['title'] ?? widget.fieldName,
          style: Theme.of(context).textTheme.titleSmall,
        ),
        if (widget.fieldSchema['help_text'] != null) ...[
          const SizedBox(height: 4),
          Text(
            widget.fieldSchema['help_text'],
            style: Theme.of(context).textTheme.bodySmall,
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
              final isSelected = _tags.contains(tag);
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
          TextFormField(
            controller: _controller,
            focusNode: _focusNode,
            decoration: InputDecoration(
              hintText: placeholder,
              border: const OutlineInputBorder(),
              suffixIcon: IconButton(
                icon: const Icon(Icons.add),
                onPressed: () => _addTag(_controller.text),
              ),
            ),
            onFieldSubmitted: _addTag,
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
    _focusNode.dispose();
    super.dispose();
  }
}

/// 动态表单组件
class DynamicFormWidget extends StatefulWidget {
  final Map<String, dynamic> schema;
  final Map<String, dynamic> initialData;
  final Function(Map<String, dynamic>) onChanged;
  
  const DynamicFormWidget({
    super.key,
    required this.schema,
    required this.initialData,
    required this.onChanged,
  });
  
  @override
  State<DynamicFormWidget> createState() => _DynamicFormWidgetState();
}

class _DynamicFormWidgetState extends State<DynamicFormWidget> {
  late Map<String, dynamic> _formData;
  
  @override
  void initState() {
    super.initState();
    _formData = Map<String, dynamic>.from(widget.initialData);
  }
  
  @override
  Widget build(BuildContext context) {
    final Map<String, dynamic> fields = widget.schema['fields'] ?? {};
    
    return Column(
      children: fields.entries.map((entry) {
        final String fieldName = entry.key;
        final Map<String, dynamic> fieldSchema = entry.value;
        
        return Padding(
          padding: const EdgeInsets.only(bottom: 16.0),
          child: CustomConfigWidgetFactory.buildConfigField(
            fieldName: fieldName,
            fieldSchema: fieldSchema,
            currentValue: _formData[fieldName],
            onChanged: (value) {
              setState(() {
                _formData[fieldName] = value;
                widget.onChanged(_formData);
              });
            },
            context: context,
          ),
        );
      }).toList(),
    );
  }
}