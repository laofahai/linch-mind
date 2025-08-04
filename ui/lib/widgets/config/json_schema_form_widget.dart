import 'package:flutter/material.dart';
import 'dynamic_list_widget.dart';

/// 通用JSON Schema表单渲染器
/// 根据JSON Schema自动生成配置表单UI
class JsonSchemaFormWidget extends StatefulWidget {
  /// JSON Schema定义
  final Map<String, dynamic> schema;
  
  /// 当前表单数据
  final Map<String, dynamic> data;
  
  /// 数据变更回调
  final ValueChanged<Map<String, dynamic>> onChanged;
  
  /// 是否只读模式
  final bool readOnly;

  const JsonSchemaFormWidget({
    Key? key,
    required this.schema,
    required this.data,
    required this.onChanged,
    this.readOnly = false,
  }) : super(key: key);

  @override
  _JsonSchemaFormWidgetState createState() => _JsonSchemaFormWidgetState();
}

class _JsonSchemaFormWidgetState extends State<JsonSchemaFormWidget> {
  late Map<String, dynamic> _data;

  @override
  void initState() {
    super.initState();
    _data = Map.from(widget.data);
  }

  @override
  void didUpdateWidget(JsonSchemaFormWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.data != oldWidget.data) {
      _data = Map.from(widget.data);
    }
  }

  @override
  Widget build(BuildContext context) {
    final properties = widget.schema['properties'] as Map<String, dynamic>? ?? {};
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: properties.entries.map((entry) {
        final fieldName = entry.key;
        final fieldSchema = entry.value as Map<String, dynamic>;
        
        return Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: _buildFormField(fieldName, fieldSchema, _data[fieldName]),
        );
      }).toList(),
    );
  }

  Widget _buildFormField(
    String fieldName,
    Map<String, dynamic> fieldSchema,
    dynamic currentValue,
  ) {
    final fieldType = fieldSchema['type'] as String? ?? 'string';
    final widget = fieldSchema['widget'] as String?;
    final title = fieldSchema['title'] as String? ?? fieldName;
    final description = fieldSchema['description'] as String?;

    // 根据widget类型或fieldType选择合适的UI组件
    switch (widget ?? _getDefaultWidget(fieldType)) {
      case 'dynamic_list':
        return _buildDynamicListField(fieldName, title, description, fieldSchema, currentValue);
      case 'conditional_section':
        return _buildConditionalSectionField(fieldName, title, description, fieldSchema, currentValue);
      case 'collapsible_section':
        return _buildCollapsibleSectionField(fieldName, title, description, fieldSchema, currentValue);
      case 'tabbed_section':
        return _buildTabbedSectionField(fieldName, title, description, fieldSchema, currentValue);
      case 'nested_object':
        return _buildNestedObjectField(fieldName, title, description, fieldSchema, currentValue);
      case 'switch':
        return _buildSwitchField(fieldName, title, description, currentValue);
      case 'tags_input':
        return _buildTagsInputField(fieldName, title, description, fieldSchema, currentValue);
      case 'slider':
        return _buildSliderField(fieldName, title, description, fieldSchema, currentValue);
      case 'select':
        return _buildSelectField(fieldName, title, description, fieldSchema, currentValue);
      case 'number_input':
        return _buildNumberInputField(fieldName, title, description, fieldSchema, currentValue);
      default:
        return _buildTextInputField(fieldName, title, description, currentValue);
    }
  }

  Widget _buildDynamicListField(
    String fieldName,
    String title,
    String? description,
    Map<String, dynamic> fieldSchema,
    dynamic currentValue,
  ) {
    final items = List<Map<String, dynamic>>.from(currentValue ?? []);
    final itemSchema = fieldSchema['items'] as Map<String, dynamic>? ?? {};
    final widgetConfig = fieldSchema['widget_config'] as Map<String, dynamic>? ?? {};
    
    // 合并标题和描述到widgetConfig
    final enhancedWidgetConfig = {
      'title': title,
      'description': description,
      ...widgetConfig,
    };
    
    return DynamicListWidget(
      items: items,
      itemSchema: itemSchema,
      widgetConfig: enhancedWidgetConfig,
      onChanged: (newItems) => _updateData(fieldName, newItems),
    );
  }

  Widget _buildConditionalSectionField(
    String fieldName,
    String title,
    String? description,
    Map<String, dynamic> fieldSchema,
    dynamic currentValue,
  ) {
    final widgetConfig = fieldSchema['widget_config'] as Map<String, dynamic>? ?? {};
    final condition = widgetConfig['condition'] as Map<String, dynamic>? ?? {};
    final conditionField = condition['field'] as String? ?? '';
    final conditionOperator = condition['operator'] as String? ?? 'equals';
    final conditionValue = condition['value'];
    
    // 检查条件是否满足
    final shouldShow = _evaluateCondition(_data[conditionField], conditionOperator, conditionValue);
    
    if (!shouldShow) {
      return const SizedBox.shrink();
    }
    
    return _buildNestedObjectField(fieldName, title, description, fieldSchema, currentValue);
  }

  Widget _buildCollapsibleSectionField(
    String fieldName,
    String title,
    String? description,
    Map<String, dynamic> fieldSchema,
    dynamic currentValue,
  ) {
    final widgetConfig = fieldSchema['widget_config'] as Map<String, dynamic>? ?? {};
    final collapsed = widgetConfig['collapsed'] ?? false;
    final properties = fieldSchema['properties'] as Map<String, dynamic>? ?? {};
    
    return Card(
      child: ExpansionTile(
        title: Text(title),
        subtitle: description != null ? Text(description) : null,
        initiallyExpanded: !collapsed,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: properties.entries.map((entry) {
                final subFieldName = entry.key;
                final subFieldSchema = entry.value as Map<String, dynamic>;
                final subCurrentValue = (currentValue as Map<String, dynamic>?)?[subFieldName];
                
                return Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: _buildFormField(
                    '$fieldName.$subFieldName',
                    subFieldSchema,
                    subCurrentValue,
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTabbedSectionField(
    String fieldName,
    String title,
    String? description,
    Map<String, dynamic> fieldSchema,
    dynamic currentValue,
  ) {
    final properties = fieldSchema['properties'] as Map<String, dynamic>? ?? {};
    final tabTitles = properties.keys.toList();
    
    return DefaultTabController(
      length: tabTitles.length,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: Theme.of(context).textTheme.titleMedium),
          if (description != null)
            Text(description, style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 8),
          TabBar(
            tabs: tabTitles.map((tabTitle) => Tab(text: tabTitle)).toList(),
          ),
          SizedBox(
            height: 400, // 固定高度，实际应用中可能需要动态计算
            child: TabBarView(
              children: tabTitles.map((tabTitle) {
                final tabSchema = properties[tabTitle] as Map<String, dynamic>;
                final tabCurrentValue = (currentValue as Map<String, dynamic>?)?[tabTitle];
                
                return Padding(
                  padding: const EdgeInsets.all(16),
                  child: _buildFormField(
                    '$fieldName.$tabTitle',
                    tabSchema,
                    tabCurrentValue,
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNestedObjectField(
    String fieldName,
    String title,
    String? description,
    Map<String, dynamic> fieldSchema,
    dynamic currentValue,
  ) {
    final properties = fieldSchema['properties'] as Map<String, dynamic>? ?? {};
    
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey.shade300),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: Theme.of(context).textTheme.titleSmall),
          if (description != null) ...[
            const SizedBox(height: 4),
            Text(description, style: Theme.of(context).textTheme.bodySmall),
          ],
          const SizedBox(height: 12),
          ...properties.entries.map((entry) {
            final subFieldName = entry.key;
            final subFieldSchema = entry.value as Map<String, dynamic>;
            final subCurrentValue = (currentValue as Map<String, dynamic>?)?[subFieldName];
            
            return Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: _buildFormField(
                '$fieldName.$subFieldName',
                subFieldSchema,
                subCurrentValue,
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildSwitchField(String fieldName, String title, String? description, dynamic currentValue) {
    return SwitchListTile(
      title: Text(title),
      subtitle: description != null ? Text(description) : null,
      value: currentValue ?? false,
      onChanged: widget.readOnly ? null : (value) => _updateData(fieldName, value),
    );
  }

  Widget _buildTextInputField(String fieldName, String title, String? description, dynamic currentValue) {
    return TextFormField(
      initialValue: currentValue?.toString() ?? '',
      decoration: InputDecoration(
        labelText: title,
        hintText: description,
        border: const OutlineInputBorder(),
      ),
      readOnly: widget.readOnly,
      onChanged: widget.readOnly ? null : (value) => _updateData(fieldName, value),
    );
  }

  Widget _buildNumberInputField(
    String fieldName,
    String title,
    String? description,
    Map<String, dynamic> fieldSchema,
    dynamic currentValue,
  ) {
    final minimum = fieldSchema['minimum'];
    final maximum = fieldSchema['maximum'];
    
    return TextFormField(
      initialValue: currentValue?.toString() ?? '',
      decoration: InputDecoration(
        labelText: title,
        hintText: description,
        border: const OutlineInputBorder(),
        suffixText: minimum != null && maximum != null ? '($minimum-$maximum)' : null,
      ),
      keyboardType: TextInputType.number,
      readOnly: widget.readOnly,
      onChanged: widget.readOnly ? null : (value) {
        final numValue = int.tryParse(value) ?? double.tryParse(value);
        _updateData(fieldName, numValue);
      },
    );
  }

  Widget _buildSelectField(
    String fieldName,
    String title,
    String? description,
    Map<String, dynamic> fieldSchema,
    dynamic currentValue,
  ) {
    final options = fieldSchema['options'] as List<dynamic>? ?? [];
    
    return DropdownButtonFormField<dynamic>(
      value: currentValue,
      decoration: InputDecoration(
        labelText: title,
        hintText: description,
        border: const OutlineInputBorder(),
      ),
      items: options.map((option) {
        final value = option is Map ? option['value'] : option;
        final label = option is Map ? option['label'] : option.toString();
        
        return DropdownMenuItem<dynamic>(
          value: value,
          child: Text(label),
        );
      }).toList(),
      onChanged: widget.readOnly ? null : (value) => _updateData(fieldName, value),
    );
  }

  Widget _buildTagsInputField(
    String fieldName,
    String title,
    String? description, 
    Map<String, dynamic> fieldSchema,
    dynamic currentValue,
  ) {
    final tags = List<String>.from(currentValue ?? []);
    final widgetConfig = fieldSchema['widget_config'] as Map<String, dynamic>? ?? {};
    final predefinedTags = List<String>.from(widgetConfig['predefined_tags'] ?? []);
    final allowCustom = widgetConfig['allow_custom'] ?? true;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: const TextStyle(fontWeight: FontWeight.w500)),
        if (description != null)
          Text(description, style: TextStyle(color: Colors.grey.shade600, fontSize: 12)),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 4,
          children: [
            ...tags.map((tag) => Chip(
              label: Text(tag),
              deleteIcon: widget.readOnly ? null : const Icon(Icons.close, size: 16),
              onDeleted: widget.readOnly ? null : () => _removeTag(fieldName, tag, tags),
            )),
            if (!widget.readOnly) ...[
              ...predefinedTags.where((tag) => !tags.contains(tag)).map((tag) => 
                ActionChip(
                  label: Text(tag),
                  onPressed: () => _addTag(fieldName, tag, tags),
                ),
              ),
              if (allowCustom)
                ActionChip(
                  label: const Text('+ 自定义'),
                  onPressed: () => _showAddTagDialog(fieldName, tags),
                ),
            ],
          ],
        ),
      ],
    );
  }

  Widget _buildSliderField(
    String fieldName,
    String title,
    String? description,
    Map<String, dynamic> fieldSchema,
    dynamic currentValue,
  ) {
    final min = (fieldSchema['minimum'] ?? 0).toDouble();
    final max = (fieldSchema['maximum'] ?? 100).toDouble();
    final divisions = fieldSchema['divisions'] as int?;
    final value = (currentValue ?? min).toDouble();
    final widgetConfig = fieldSchema['widget_config'] as Map<String, dynamic>? ?? {};
    final unit = widgetConfig['unit'] ?? '';
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: const TextStyle(fontWeight: FontWeight.w500)),
        if (description != null)
          Text(description, style: TextStyle(color: Colors.grey.shade600, fontSize: 12)),
        Slider(
          value: value.clamp(min, max),
          min: min,
          max: max,
          divisions: divisions,
          label: '${value.round()}$unit',
          onChanged: widget.readOnly ? null : (newValue) => _updateData(fieldName, newValue.round()),
        ),
      ],
    );
  }

  bool _evaluateCondition(dynamic fieldValue, String operator, dynamic expectedValue) {
    switch (operator) {
      case 'equals':
        return fieldValue == expectedValue;
      case 'not_equals':
        return fieldValue != expectedValue;
      case 'greater_than':
        return (fieldValue ?? 0) > expectedValue;
      case 'less_than':
        return (fieldValue ?? 0) < expectedValue;
      case 'contains':
        return fieldValue?.toString().contains(expectedValue.toString()) ?? false;
      default:
        return false;
    }
  }

  String _getDefaultWidget(String fieldType) {
    switch (fieldType) {
      case 'boolean': return 'switch';
      case 'integer':
      case 'number': return 'number_input';
      case 'array': return 'tags_input';
      case 'object': return 'nested_object';
      default: return 'text_input';
    }
  }

  void _updateData(String fieldName, dynamic value) {
    setState(() {
      // 处理嵌套字段更新 (如 global_settings.max_file_size)
      if (fieldName.contains('.')) {
        final parts = fieldName.split('.');
        Map<String, dynamic> current = _data;
        
        // 导航到嵌套对象
        for (int i = 0; i < parts.length - 1; i++) {
          current[parts[i]] ??= <String, dynamic>{};
          current = current[parts[i]] as Map<String, dynamic>;
        }
        
        // 设置最终值
        current[parts.last] = value;
      } else {
        _data[fieldName] = value;
      }
    });
    widget.onChanged(_data);
  }

  void _addTag(String fieldName, String tag, List<String> currentTags) {
    final newTags = [...currentTags, tag];
    _updateData(fieldName, newTags);
  }

  void _removeTag(String fieldName, String tag, List<String> currentTags) {
    final newTags = currentTags.where((t) => t != tag).toList();
    _updateData(fieldName, newTags);
  }

  void _showAddTagDialog(String fieldName, List<String> currentTags) {
    final controller = TextEditingController();
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('添加自定义标签'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            labelText: '标签内容',
            hintText: '请输入标签',
          ),
          autofocus: true,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () {
              final tag = controller.text.trim();
              if (tag.isNotEmpty && !currentTags.contains(tag)) {
                Navigator.of(context).pop();
                _addTag(fieldName, tag, currentTags);
              }
            },
            child: const Text('添加'),
          ),
        ],
      ),
    );
  }
}