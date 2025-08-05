import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';

/// 通用动态列表配置Widget
/// 基于JSON Schema配置，支持任意对象的列表编辑
class DynamicListWidget extends StatefulWidget {
  /// 列表数据
  final List<Map<String, dynamic>> items;

  /// 列表项的JSON Schema定义
  final Map<String, dynamic> itemSchema;

  /// Widget配置
  final Map<String, dynamic> widgetConfig;

  /// 数据变更回调
  final ValueChanged<List<Map<String, dynamic>>> onChanged;

  const DynamicListWidget({
    Key? key,
    required this.items,
    required this.itemSchema,
    required this.widgetConfig,
    required this.onChanged,
  }) : super(key: key);

  @override
  _DynamicListWidgetState createState() => _DynamicListWidgetState();
}

class _DynamicListWidgetState extends State<DynamicListWidget> {
  late List<Map<String, dynamic>> _items;

  @override
  void initState() {
    super.initState();
    _items = List.from(widget.items);
  }

  @override
  Widget build(BuildContext context) {
    final config = widget.widgetConfig;
    final maxItems = config['max_items'] ?? 999;
    final allowReorder = config['allow_reorder'] ?? false;
    final collapseItems = config['collapse_items'] ?? false;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 标题栏
        _buildHeader(config, maxItems),
        const SizedBox(height: 16),

        // 列表内容
        if (_items.isEmpty)
          _buildEmptyState(config)
        else
          _buildItemList(collapseItems, allowReorder),
      ],
    );
  }

  Widget _buildHeader(Map<String, dynamic> config, int maxItems) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        // 左侧信息
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              config['title'] ?? '列表配置',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            if (config['description'] != null)
              Text(
                config['description'],
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.grey.shade600,
                    ),
              ),
          ],
        ),

        // 添加按钮
        if (_items.length < maxItems)
          ElevatedButton.icon(
            onPressed: _addItem,
            icon: const Icon(Icons.add, size: 16),
            label: Text(config['add_button_text'] ?? '添加项目'),
            style: ElevatedButton.styleFrom(
              minimumSize: const Size(100, 32),
            ),
          ),
      ],
    );
  }

  Widget _buildEmptyState(Map<String, dynamic> config) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        border:
            Border.all(color: Colors.grey.shade300, style: BorderStyle.solid),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Icon(Icons.list_outlined, size: 48, color: Colors.grey.shade400),
          const SizedBox(height: 16),
          Text(
            config['empty_text'] ?? '暂无项目',
            style: TextStyle(color: Colors.grey.shade600),
          ),
          const SizedBox(height: 8),
          Text(
            config['empty_hint'] ??
                '点击"${config['add_button_text'] ?? '添加项目'}"开始配置',
            style: TextStyle(color: Colors.grey.shade500, fontSize: 12),
          ),
        ],
      ),
    );
  }

  Widget _buildItemList(bool collapseItems, bool allowReorder) {
    if (allowReorder) {
      return ReorderableListView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: _items.length,
        onReorder: _reorderItems,
        itemBuilder: (context, index) => _buildItemCard(
          index,
          _items[index],
          collapseItems,
          key: ValueKey('item_$index'),
        ),
      );
    } else {
      return Column(
        children: _items
            .asMap()
            .entries
            .map(
              (entry) => _buildItemCard(entry.key, entry.value, collapseItems),
            )
            .toList(),
      );
    }
  }

  Widget _buildItemCard(
    int index,
    Map<String, dynamic> item,
    bool collapsible, {
    Key? key,
  }) {
    final config = widget.widgetConfig;
    final titleTemplate = config['item_title_template'] ?? '';
    final subtitleTemplate = config['item_subtitle_template'] ?? '';
    final showIndex = config['show_item_index'] ?? true;

    // 渲染标题和副标题模板
    final title = _renderTemplate(titleTemplate, item) ??
        (showIndex ? '项目 ${index + 1}' : '项目');
    final subtitle = _renderTemplate(subtitleTemplate, item);

    return Card(
      key: key,
      margin: const EdgeInsets.only(bottom: 12),
      child: collapsible
          ? _buildCollapsibleItem(index, item, title, subtitle)
          : _buildExpandedItem(index, item, title, subtitle),
    );
  }

  Widget _buildCollapsibleItem(
    int index,
    Map<String, dynamic> item,
    String title,
    String? subtitle,
  ) {
    return ExpansionTile(
      title: Text(title),
      subtitle: subtitle != null ? Text(subtitle) : null,
      leading: _buildItemStatusIndicator(item),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (widget.widgetConfig['allow_reorder'] == true)
            const Icon(Icons.drag_handle),
          IconButton(
            onPressed: () => _removeItem(index),
            icon: const Icon(Icons.delete_outline, color: Colors.red),
            tooltip: widget.widgetConfig['remove_button_text'] ?? '删除',
          ),
        ],
      ),
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: _buildItemForm(index, item),
        ),
      ],
    );
  }

  Widget _buildExpandedItem(
    int index,
    Map<String, dynamic> item,
    String title,
    String? subtitle,
  ) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 头部
          Row(
            children: [
              _buildItemStatusIndicator(item),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: Theme.of(context).textTheme.titleSmall),
                    if (subtitle != null)
                      Text(
                        subtitle,
                        style: TextStyle(
                          color: Colors.grey.shade600,
                          fontSize: 12,
                        ),
                      ),
                  ],
                ),
              ),
              if (widget.widgetConfig['allow_reorder'] == true)
                const Icon(Icons.drag_handle),
              IconButton(
                onPressed: () => _removeItem(index),
                icon: const Icon(Icons.delete_outline, color: Colors.red),
                tooltip: widget.widgetConfig['remove_button_text'] ?? '删除',
              ),
            ],
          ),
          const Divider(height: 24),
          // 表单内容
          _buildItemForm(index, item),
        ],
      ),
    );
  }

  Widget _buildItemStatusIndicator(Map<String, dynamic> item) {
    final enabled = item['enabled'] ?? true;
    return Container(
      width: 12,
      height: 12,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: enabled ? Colors.green : Colors.grey,
      ),
    );
  }

  Widget _buildItemForm(int index, Map<String, dynamic> item) {
    final properties =
        widget.itemSchema['properties'] as Map<String, dynamic>? ?? {};

    return Column(
      children: properties.entries.map((entry) {
        final fieldName = entry.key;
        final fieldSchema = entry.value as Map<String, dynamic>;

        return Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: _buildFormField(
            index,
            fieldName,
            fieldSchema,
            item[fieldName],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildFormField(
    int index,
    String fieldName,
    Map<String, dynamic> fieldSchema,
    dynamic currentValue,
  ) {
    final fieldType = fieldSchema['type'] as String? ?? 'string';
    final widget = fieldSchema['widget'] as String?;
    final title = fieldSchema['title'] as String? ?? fieldName;
    final description = fieldSchema['description'] as String?;

    switch (widget ?? _getDefaultWidget(fieldType)) {
      case 'switch':
        return _buildSwitchField(
            index, fieldName, title, description, currentValue);
      case 'directory_picker':
        return _buildDirectoryPickerField(index, fieldName, title, description,
            currentValue, fieldSchema['widget_config']);
      case 'tags_input':
        return _buildTagsInputField(
            index, fieldName, title, description, currentValue, fieldSchema);
      case 'slider':
        return _buildSliderField(
            index, fieldName, title, description, currentValue, fieldSchema);
      case 'conditional_section':
        return _buildConditionalSection(
            index, fieldName, title, description, currentValue, fieldSchema);
      default:
        return _buildTextInputField(
            index, fieldName, title, description, currentValue);
    }
  }

  Widget _buildSwitchField(int index, String fieldName, String title,
      String? description, dynamic currentValue) {
    return SwitchListTile(
      title: Text(title),
      subtitle: description != null ? Text(description) : null,
      value: currentValue ?? false,
      onChanged: (value) => _updateItem(index, {fieldName: value}),
    );
  }

  Widget _buildTextInputField(int index, String fieldName, String title,
      String? description, dynamic currentValue) {
    return TextFormField(
      initialValue: currentValue?.toString() ?? '',
      decoration: InputDecoration(
        labelText: title,
        hintText: description,
        border: const OutlineInputBorder(),
      ),
      onChanged: (value) => _updateItem(index, {fieldName: value}),
    );
  }

  Widget _buildDirectoryPickerField(
    int index,
    String fieldName,
    String title,
    String? description,
    dynamic currentValue,
    Map<String, dynamic>? widgetConfig,
  ) {
    return Row(
      children: [
        Expanded(
          child: TextFormField(
            initialValue: currentValue?.toString() ?? '',
            decoration: InputDecoration(
              labelText: title,
              hintText: description,
              border: const OutlineInputBorder(),
            ),
            onChanged: (value) => _updateItem(index, {fieldName: value}),
          ),
        ),
        const SizedBox(width: 8),
        IconButton(
          onPressed: () => _selectDirectory(index, fieldName),
          icon: const Icon(Icons.folder_open),
          tooltip: '选择目录',
        ),
      ],
    );
  }

  Widget _buildTagsInputField(
    int index,
    String fieldName,
    String title,
    String? description,
    dynamic currentValue,
    Map<String, dynamic> fieldSchema,
  ) {
    final tags = List<String>.from(currentValue ?? []);
    final widgetConfig =
        fieldSchema['widget_config'] as Map<String, dynamic>? ?? {};
    final predefinedTags =
        List<String>.from(widgetConfig['predefined_tags'] ?? []);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: const TextStyle(fontWeight: FontWeight.w500)),
        if (description != null)
          Text(description,
              style: TextStyle(color: Colors.grey.shade600, fontSize: 12)),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 4,
          children: [
            ...tags.map((tag) => Chip(
                  label: Text(tag),
                  deleteIcon: const Icon(Icons.close, size: 16),
                  onDeleted: () => _removeTag(index, fieldName, tag, tags),
                )),
            ...predefinedTags.where((tag) => !tags.contains(tag)).map(
                  (tag) => ActionChip(
                    label: Text(tag),
                    onPressed: () => _addTag(index, fieldName, tag, tags),
                  ),
                ),
            ActionChip(
              label: const Text('+ 自定义'),
              onPressed: () => _showAddTagDialog(index, fieldName, tags),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildSliderField(
    int index,
    String fieldName,
    String title,
    String? description,
    dynamic currentValue,
    Map<String, dynamic> fieldSchema,
  ) {
    final min = (fieldSchema['minimum'] ?? 0).toDouble();
    final max = (fieldSchema['maximum'] ?? 100).toDouble();
    final divisions = fieldSchema['divisions'] as int?;
    final value = (currentValue ?? min).toDouble();
    final widgetConfig =
        fieldSchema['widget_config'] as Map<String, dynamic>? ?? {};
    final specialValues =
        widgetConfig['special_values'] as Map<String, dynamic>? ?? {};

    String getLabel(double val) {
      final intVal = val.round();
      if (specialValues.containsKey(intVal.toString())) {
        return specialValues[intVal.toString()];
      }
      final unit = widgetConfig['unit'] ?? '';
      return '$intVal$unit';
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: const TextStyle(fontWeight: FontWeight.w500)),
        if (description != null)
          Text(description,
              style: TextStyle(color: Colors.grey.shade600, fontSize: 12)),
        Slider(
          value: value.clamp(min, max),
          min: min,
          max: max,
          divisions: divisions,
          label: getLabel(value),
          onChanged: (newValue) =>
              _updateItem(index, {fieldName: newValue.round()}),
        ),
      ],
    );
  }

  Widget _buildConditionalSection(
    int index,
    String fieldName,
    String title,
    String? description,
    dynamic currentValue,
    Map<String, dynamic> fieldSchema,
  ) {
    final widgetConfig =
        fieldSchema['widget_config'] as Map<String, dynamic>? ?? {};
    final condition = widgetConfig['condition'] as Map<String, dynamic>? ?? {};
    final conditionField = condition['field'] as String? ?? '';
    final conditionValue = condition['value'];

    // 检查条件是否满足
    final shouldShow = _items[index][conditionField] == conditionValue;

    if (!shouldShow) {
      return const SizedBox.shrink();
    }

    final properties = fieldSchema['properties'] as Map<String, dynamic>? ?? {};

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.settings, size: 16, color: Colors.blue.shade700),
              const SizedBox(width: 8),
              Text(
                title,
                style: TextStyle(
                  fontWeight: FontWeight.w500,
                  color: Colors.blue.shade700,
                ),
              ),
            ],
          ),
          if (description != null) ...[
            const SizedBox(height: 4),
            Text(description,
                style: TextStyle(color: Colors.blue.shade600, fontSize: 12)),
          ],
          const SizedBox(height: 12),
          ...properties.entries.map((entry) {
            final subFieldName = entry.key;
            final subFieldSchema = entry.value as Map<String, dynamic>;
            final subCurrentValue =
                (currentValue as Map<String, dynamic>?)?[subFieldName];

            return Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: _buildFormField(
                index,
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

  String _getDefaultWidget(String fieldType) {
    switch (fieldType) {
      case 'boolean':
        return 'switch';
      case 'integer':
      case 'number':
        return 'number_input';
      case 'array':
        return 'tags_input';
      default:
        return 'text_input';
    }
  }

  String? _renderTemplate(String template, Map<String, dynamic> item) {
    if (template.isEmpty) return null;

    String result = template;
    final regex = RegExp(r'\{\{([^}]+)\}\}');

    for (final match in regex.allMatches(template)) {
      final expression = match.group(1)?.trim() ?? '';
      final value = _evaluateExpression(expression, item);
      result = result.replaceAll(match.group(0)!, value?.toString() ?? '');
    }

    return result.isNotEmpty ? result : null;
  }

  dynamic _evaluateExpression(String expression, Map<String, dynamic> item) {
    // 简单表达式求值：支持 field || 'default' 语法
    if (expression.contains('||')) {
      final parts = expression.split('||').map((e) => e.trim()).toList();
      for (final part in parts) {
        final value = part.startsWith("'") && part.endsWith("'")
            ? part.substring(1, part.length - 1)
            : item[part];
        if (value != null && value.toString().isNotEmpty) {
          return value;
        }
      }
    }

    return item[expression];
  }

  void _addItem() {
    final defaultValues = <String, dynamic>{};
    final properties =
        widget.itemSchema['properties'] as Map<String, dynamic>? ?? {};

    // 根据schema设置默认值
    for (final entry in properties.entries) {
      final fieldSchema = entry.value as Map<String, dynamic>;
      defaultValues[entry.key] = fieldSchema['default'];
    }

    setState(() {
      _items.add(defaultValues);
    });
    widget.onChanged(_items);
  }

  void _removeItem(int index) {
    setState(() {
      _items.removeAt(index);
    });
    widget.onChanged(_items);
  }

  void _reorderItems(int oldIndex, int newIndex) {
    setState(() {
      if (newIndex > oldIndex) newIndex--;
      final item = _items.removeAt(oldIndex);
      _items.insert(newIndex, item);
    });
    widget.onChanged(_items);
  }

  void _updateItem(int index, Map<String, dynamic> updates) {
    setState(() {
      // 处理嵌套字段更新 (如 custom_config.priority)
      for (final entry in updates.entries) {
        if (entry.key.contains('.')) {
          final parts = entry.key.split('.');
          Map<String, dynamic> current = _items[index];

          // 导航到嵌套对象
          for (int i = 0; i < parts.length - 1; i++) {
            current[parts[i]] ??= <String, dynamic>{};
            current = current[parts[i]] as Map<String, dynamic>;
          }

          // 设置最终值
          current[parts.last] = entry.value;
        } else {
          _items[index][entry.key] = entry.value;
        }
      }
    });
    widget.onChanged(_items);
  }

  void _selectDirectory(int index, String fieldName) async {
    String? selectedDirectory = await FilePicker.platform.getDirectoryPath();
    if (selectedDirectory != null) {
      _updateItem(index, {fieldName: selectedDirectory});
    }
  }

  void _addTag(
      int index, String fieldName, String tag, List<String> currentTags) {
    final newTags = [...currentTags, tag];
    _updateItem(index, {fieldName: newTags});
  }

  void _removeTag(
      int index, String fieldName, String tag, List<String> currentTags) {
    final newTags = currentTags.where((t) => t != tag).toList();
    _updateItem(index, {fieldName: newTags});
  }

  void _showAddTagDialog(
      int index, String fieldName, List<String> currentTags) {
    final controller = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('添加自定义标签'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            labelText: '标签内容',
            hintText: '例如：.log',
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
                _addTag(index, fieldName, tag, currentTags);
              }
            },
            child: const Text('添加'),
          ),
        ],
      ),
    );
  }
}
