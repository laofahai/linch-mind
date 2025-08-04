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
  
  /// 构建配置字段组件
  static Widget buildConfigField({
    required String fieldName,
    required Map<String, dynamic> fieldSchema,
    required dynamic currentValue,
    required Function(dynamic) onChanged,
    required BuildContext context,
  }) {
    final String widgetType = fieldSchema['widget'] ?? 'text_input';
    
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