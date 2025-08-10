import 'package:flutter/material.dart';
import 'package:reactive_forms/reactive_forms.dart';
import 'package:file_picker/file_picker.dart';

/// Reactive目录选择器组件 - 处理List<String>类型的目录路径
class ReactiveDirectoryPicker extends StatelessWidget {
  final String formControlName;
  final Map<String, dynamic> fieldConfig;

  const ReactiveDirectoryPicker({
    required this.formControlName,
    required this.fieldConfig,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return ReactiveFormField<List<String>, List<String>>(
      formControlName: formControlName,
      builder: (ReactiveFormFieldState<List<String>, List<String>> field) {
        debugPrint('[DEBUG] ReactiveDirectoryPicker builder called for $formControlName');
        debugPrint('[DEBUG] Field control type: ${field.control.runtimeType}');
        debugPrint('[DEBUG] Field value type: ${field.value.runtimeType}');
        debugPrint('[DEBUG] Field value: ${field.value}');

        return _DirectoryPickerWidget(
          value: field.value ?? <String>[],
          onChanged: (List<String> value) => field.didChange(value),
          fieldConfig: fieldConfig,
          hasError: field.control.invalid,
          errorText: field.errorText,
        );
      },
    );
  }
}

/// 目录选择器具体实现组件
class _DirectoryPickerWidget extends StatefulWidget {
  final List<String> value;
  final ValueChanged<List<String>> onChanged;
  final Map<String, dynamic> fieldConfig;
  final bool hasError;
  final String? errorText;

  const _DirectoryPickerWidget({
    required this.value,
    required this.onChanged,
    required this.fieldConfig,
    required this.hasError,
    this.errorText,
  });

  @override
  State<_DirectoryPickerWidget> createState() => _DirectoryPickerWidgetState();
}

class _DirectoryPickerWidgetState extends State<_DirectoryPickerWidget> {
  late List<String> _directories;

  @override
  void initState() {
    super.initState();
    _directories = List<String>.from(widget.value);
  }

  @override
  void didUpdateWidget(_DirectoryPickerWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.value != oldWidget.value) {
      _directories = List<String>.from(widget.value);
    }
  }

  Future<void> _addDirectory() async {
    String? selectedDirectory = await FilePicker.platform.getDirectoryPath();
    if (selectedDirectory != null) {
      setState(() {
        if (!_directories.contains(selectedDirectory)) {
          _directories.add(selectedDirectory);
          widget.onChanged(_directories);
        }
      });
    }
  }

  void _removeDirectory(int index) {
    setState(() {
      _directories.removeAt(index);
      widget.onChanged(_directories);
    });
  }

  void _editDirectory(int index, String newPath) {
    setState(() {
      _directories[index] = newPath;
      widget.onChanged(_directories);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 标题和添加按钮
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              widget.fieldConfig['title'] ?? '目录路径',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
            ),
            ElevatedButton.icon(
              onPressed: _addDirectory,
              icon: const Icon(Icons.folder_open, size: 18),
              label: const Text('选择目录'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              ),
            ),
          ],
        ),

        // 描述信息
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

        // 目录列表
        if (_directories.isEmpty) ...[
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey.shade300),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              '暂无选择目录，点击上方"选择目录"按钮添加',
              style: TextStyle(
                color: Colors.grey.shade600,
                fontStyle: FontStyle.italic,
              ),
              textAlign: TextAlign.center,
            ),
          ),
        ] else ...[
          Container(
            decoration: BoxDecoration(
              border: Border.all(
                color: widget.hasError ? Colors.red : Colors.grey.shade300,
              ),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              children: _directories.asMap().entries.map((entry) {
                final index = entry.key;
                final directory = entry.value;

                return Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    border: index > 0 
                        ? Border(top: BorderSide(color: Colors.grey.shade200))
                        : null,
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.folder,
                        color: Colors.blue.shade600,
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: TextFormField(
                          initialValue: directory,
                          decoration: const InputDecoration(
                            border: InputBorder.none,
                            isDense: true,
                            contentPadding: EdgeInsets.zero,
                          ),
                          style: const TextStyle(fontSize: 14),
                          onChanged: (value) => _editDirectory(index, value),
                        ),
                      ),
                      const SizedBox(width: 8),
                      IconButton(
                        icon: const Icon(Icons.delete, color: Colors.red, size: 20),
                        onPressed: () => _removeDirectory(index),
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(
                          minWidth: 32,
                          minHeight: 32,
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ),
          ),
        ],

        // 错误信息
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