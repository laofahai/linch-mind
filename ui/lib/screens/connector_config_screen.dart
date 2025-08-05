import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:reactive_forms/reactive_forms.dart';
import '../services/connector_config_api_client.dart';
import '../services/form_builder_service.dart';
import '../widgets/config/reactive_config_widgets.dart';

/// 连接器配置界面 - 使用reactive_forms重写
class ConnectorConfigScreen extends ConsumerStatefulWidget {
  final String connectorId;
  final String connectorName;

  const ConnectorConfigScreen({
    super.key,
    required this.connectorId,
    required this.connectorName,
  });

  @override
  ConsumerState<ConnectorConfigScreen> createState() =>
      _ConnectorConfigScreenState();
}

class _ConnectorConfigScreenState extends ConsumerState<ConnectorConfigScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  FormGroup? _form;
  Map<String, dynamic> _configSchema = {};
  Map<String, dynamic> _uiSchema = {};
  Map<String, dynamic> _currentConfig = {};
  Map<String, dynamic> _defaultConfig = {};

  bool _isLoading = true;
  bool _isSaving = false;
  String? _errorMessage;
  List<String> _validationErrors = [];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadConfigData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _form?.dispose();
    super.dispose();
  }

  Future<void> _loadConfigData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final configService = ref.read(connectorConfigApiClientProvider);

      // 并行加载schema和当前配置
      final results = await Future.wait([
        configService.getConfigSchema(widget.connectorId),
        configService.getCurrentConfig(widget.connectorId),
      ]);

      final schemaResponse = results[0];
      final configResponse = results[1];

      if (schemaResponse.success && configResponse.success) {
        final schemaData = schemaResponse.data as Map<String, dynamic>? ?? {};
        final configData = configResponse.data as Map<String, dynamic>? ?? {};

        _configSchema = schemaData['schema'] as Map<String, dynamic>? ?? {};
        _uiSchema = schemaData['ui_schema'] as Map<String, dynamic>? ?? {};
        _defaultConfig =
            schemaData['default_values'] as Map<String, dynamic>? ?? {};
        _currentConfig = configData['config'] as Map<String, dynamic>? ?? {};

        // 构建reactive form
        _form = FormBuilderService.buildFormFromSchema(
          schema: _configSchema,
          initialData: _currentConfig,
          uiSchema: _uiSchema,
        );

        setState(() {
          _isLoading = false;
        });
      } else {
        setState(() {
          _errorMessage =
              schemaResponse.message ?? configResponse.message ?? '加载配置失败';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = '加载配置时发生错误: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _validateAndSaveConfig() async {
    if (_form == null || !_form!.valid) {
      setState(() {
        _validationErrors = _extractValidationErrors();
      });
      _showValidationErrorDialog();
      return;
    }

    setState(() {
      _isSaving = true;
      _validationErrors = [];
    });

    try {
      final configService = ref.read(connectorConfigApiClientProvider);
      final formData = FormBuilderService.extractFormData(_form!);

      // 先验证配置
      final validationResponse = await configService.validateConfig(
        widget.connectorId,
        formData,
      );

      final validationData =
          validationResponse.data as Map<String, dynamic>? ?? {};
      if (!validationResponse.success ||
          !(validationData['valid'] as bool? ?? false)) {
        setState(() {
          _validationErrors =
              List<String>.from(validationData['errors'] as List? ?? []);
          _isSaving = false;
        });

        _showValidationErrorDialog();
        return;
      }

      // 保存配置
      final saveResponse = await configService.updateConfig(
        widget.connectorId,
        formData,
        changeReason: '用户界面更新',
      );

      if (saveResponse.success) {
        // 更新当前配置
        setState(() {
          _currentConfig = Map<String, dynamic>.from(formData);
          _isSaving = false;
        });

        final saveData = saveResponse.data as Map<String, dynamic>? ?? {};
        _showSuccessSnackBar((saveData['hot_reload_applied'] as bool? ?? false)
            ? '配置已保存并热重载成功'
            : '配置已保存，需要重启连接器生效');
      } else {
        setState(() {
          _errorMessage = saveResponse.message ?? '保存配置失败';
          _isSaving = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = '保存配置时发生错误: $e';
        _isSaving = false;
      });
    }
  }

  List<String> _extractValidationErrors() {
    if (_form == null) return [];

    final errors = <String>[];

    void collectErrors(AbstractControl control, String path) {
      if (control.hasErrors) {
        for (final error in control.errors.entries) {
          final field = path.isEmpty ? '表单' : path;
          switch (error.key) {
            case 'required':
              errors.add('$field 为必填项');
              break;
            case 'email':
              errors.add('$field 必须是有效的邮箱地址');
              break;
            case 'minLength':
              final errorMap = error.value as Map<String, dynamic>? ?? {};
              final minLength = errorMap['requiredLength'] ?? '?';
              errors.add('$field 最少需要 $minLength 个字符');
              break;
            case 'maxLength':
              final errorMap = error.value as Map<String, dynamic>? ?? {};
              final maxLength = errorMap['requiredLength'] ?? '?';
              errors.add('$field 最多允许 $maxLength 个字符');
              break;
            case 'min':
              final errorMap = error.value as Map<String, dynamic>? ?? {};
              final min = errorMap['min'] ?? '?';
              errors.add('$field 不能小于 $min');
              break;
            case 'max':
              final errorMap = error.value as Map<String, dynamic>? ?? {};
              final max = errorMap['max'] ?? '?';
              errors.add('$field 不能大于 $max');
              break;
            case 'pattern':
              errors.add('$field 格式不正确');
              break;
            default:
              errors.add('$field 验证失败: ${error.key}');
              break;
          }
        }
      }

      if (control is FormGroup) {
        for (final entry in control.controls.entries) {
          final childPath = path.isEmpty ? entry.key : '$path.${entry.key}';
          collectErrors(entry.value, childPath);
        }
      } else if (control is FormArray) {
        for (int i = 0; i < control.controls.length; i++) {
          final childPath = path.isEmpty ? '[$i]' : '$path[$i]';
          collectErrors(control.controls[i], childPath);
        }
      }
    }

    collectErrors(_form!, '');
    return errors;
  }

  Future<void> _resetToDefaults() async {
    final confirmed = await _showConfirmDialog(
      '重置配置',
      '确定要将配置重置为默认值吗？此操作不可撤销。',
    );

    if (confirmed && _form != null) {
      // 重新构建表单使用默认值
      _form!.dispose();
      _form = FormBuilderService.buildFormFromSchema(
        schema: _configSchema,
        initialData: _defaultConfig,
        uiSchema: _uiSchema,
      );
      setState(() {});
    }
  }

  void _showValidationErrorDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('配置验证失败'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('请修复以下错误：'),
            const SizedBox(height: 8),
            ..._validationErrors.map((error) => Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(Icons.error, color: Colors.red, size: 16),
                      const SizedBox(width: 8),
                      Expanded(child: Text(error)),
                    ],
                  ),
                )),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }

  Future<bool> _showConfirmDialog(String title, String content) async {
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(content),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('确定'),
          ),
        ],
      ),
    );
    return result ?? false;
  }

  void _showSuccessSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
        duration: const Duration(seconds: 3),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('${widget.connectorName} - 配置'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(icon: Icon(Icons.settings), text: '配置'),
            Tab(icon: Icon(Icons.preview), text: '预览'),
          ],
        ),
        actions: [
          if (!_isLoading)
            PopupMenuButton<String>(
              onSelected: (value) {
                switch (value) {
                  case 'reset':
                    _resetToDefaults();
                    break;
                  case 'export':
                    _exportConfig();
                    break;
                  case 'import':
                    _importConfig();
                    break;
                }
              },
              itemBuilder: (context) => [
                const PopupMenuItem(
                  value: 'reset',
                  child: ListTile(
                    leading: Icon(Icons.refresh),
                    title: Text('重置为默认值'),
                  ),
                ),
                const PopupMenuItem(
                  value: 'export',
                  child: ListTile(
                    leading: Icon(Icons.download),
                    title: Text('导出配置'),
                  ),
                ),
                const PopupMenuItem(
                  value: 'import',
                  child: ListTile(
                    leading: Icon(Icons.upload),
                    title: Text('导入配置'),
                  ),
                ),
              ],
            ),
        ],
      ),
      body: _buildBody(),
      floatingActionButton: _buildFloatingActionButton(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (_errorMessage != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error, size: 64, color: Colors.red.shade300),
            const SizedBox(height: 16),
            Text(
              _errorMessage!,
              style: Theme.of(context).textTheme.titleMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadConfigData,
              child: const Text('重试'),
            ),
          ],
        ),
      );
    }

    if (_form == null) {
      return const Center(
        child: Text('无法创建表单'),
      );
    }

    return ReactiveForm(
      formGroup: _form!,
      child: TabBarView(
        controller: _tabController,
        children: [
          _buildConfigTab(),
          _buildPreviewTab(),
        ],
      ),
    );
  }

  Widget _buildConfigTab() {
    final sections = _uiSchema['ui:sections'] as Map<String, dynamic>? ?? {};

    if (sections.isEmpty) {
      return _buildBasicConfigForm();
    }

    return _buildSectionedConfigForm(sections);
  }

  Widget _buildSectionedConfigForm(Map<String, dynamic> sections) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: sections.entries.map((entry) {
          final sectionId = entry.key;
          final sectionConfig = entry.value as Map<String, dynamic>;

          return _buildConfigSection(sectionId, sectionConfig);
        }).toList(),
      ),
    );
  }

  Widget _buildConfigSection(
      String sectionId, Map<String, dynamic> sectionConfig) {
    final title = sectionConfig['ui:title'] as String? ?? sectionId;
    final description = sectionConfig['ui:description'] as String?;
    final collapsible = sectionConfig['ui:collapsible'] as bool? ?? false;
    final collapsed = sectionConfig['ui:collapsed'] as bool? ?? false;
    final fields = sectionConfig['ui:fields'] as Map<String, dynamic>? ?? {};

    Widget content = Column(
      children: fields.entries.map((fieldEntry) {
        final fieldName = fieldEntry.key;
        final fieldSchema =
            _configSchema['properties']?[fieldName] as Map<String, dynamic>? ??
                {};

        // 合并schema和UI配置
        final mergedConfig = FormBuilderService.getFieldUIConfig(
          fieldName,
          fieldSchema,
          _uiSchema,
        );

        return Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: ReactiveConfigWidgets.buildFieldWidget(
            fieldName: fieldName,
            fieldConfig: mergedConfig,
            context: context,
          ),
        );
      }).toList(),
    );

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: collapsible
          ? ExpansionTile(
              title: Text(title),
              subtitle: description != null ? Text(description) : null,
              initiallyExpanded: !collapsed,
              children: [
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: content,
                ),
              ],
            )
          : Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  if (description != null) ...[
                    const SizedBox(height: 8),
                    Text(
                      description,
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ],
                  const SizedBox(height: 16),
                  content,
                ],
              ),
            ),
    );
  }

  Widget _buildBasicConfigForm() {
    final properties =
        _configSchema['properties'] as Map<String, dynamic>? ?? {};

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: properties.entries.map((entry) {
          final fieldName = entry.key;
          final fieldSchema = entry.value as Map<String, dynamic>;

          final mergedConfig = FormBuilderService.getFieldUIConfig(
            fieldName,
            fieldSchema,
            _uiSchema,
          );

          return Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: ReactiveConfigWidgets.buildFieldWidget(
              fieldName: fieldName,
              fieldConfig: mergedConfig,
              context: context,
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildPreviewTab() {
    if (_form == null) {
      return const Center(child: Text('表单未初始化'));
    }

    final currentData = FormBuilderService.extractFormData(_form!);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '当前配置预览',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 16),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey.shade100,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.grey.shade300),
            ),
            child: SelectableText(
              _formatConfigForPreview(currentData),
              style: const TextStyle(
                fontFamily: 'Monaco',
                fontSize: 12,
              ),
            ),
          ),
          const SizedBox(height: 24),

          // 配置差异对比
          if (_hasConfigChanges()) ...[
            Text(
              '与当前配置的差异',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.blue.shade200),
              ),
              child: Text(
                _getConfigDiff(),
                style: const TextStyle(
                  fontFamily: 'Monaco',
                  fontSize: 12,
                ),
              ),
            ),
          ],

          // 表单验证状态
          const SizedBox(height: 24),
          Text(
            '表单验证状态',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        _form!.valid ? Icons.check_circle : Icons.error,
                        color: _form!.valid ? Colors.green : Colors.red,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        _form!.valid ? '表单验证通过' : '表单存在验证错误',
                        style: TextStyle(
                          color: _form!.valid ? Colors.green : Colors.red,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  if (!_form!.valid) ...[
                    const SizedBox(height: 8),
                    const Divider(),
                    const SizedBox(height: 8),
                    ..._extractValidationErrors().map(
                      (error) => Padding(
                        padding: const EdgeInsets.only(bottom: 4),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Icon(Icons.error,
                                color: Colors.red, size: 16),
                            const SizedBox(width: 8),
                            Expanded(child: Text(error)),
                          ],
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget? _buildFloatingActionButton() {
    if (_isLoading || _form == null) {
      return null;
    }

    final hasChanges = _hasConfigChanges();

    if (!hasChanges) {
      return const SizedBox.shrink();
    }

    return FloatingActionButton.extended(
      onPressed: _isSaving ? null : _validateAndSaveConfig,
      icon: _isSaving
          ? const SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          : const Icon(Icons.save),
      label: Text(_isSaving ? '保存中...' : '保存配置'),
    );
  }

  bool _hasConfigChanges() {
    if (_form == null) return false;

    final currentData = FormBuilderService.extractFormData(_form!);
    return currentData.toString() != _currentConfig.toString();
  }

  String _formatConfigForPreview(Map<String, dynamic> config) {
    return JsonEncoder.withIndent('  ').convert(config);
  }

  String _getConfigDiff() {
    if (_form == null) return '无变更';

    final formData = FormBuilderService.extractFormData(_form!);
    final changes = <String>[];

    for (final key in formData.keys) {
      if (formData[key] != _currentConfig[key]) {
        changes.add('$key: ${_currentConfig[key]} → ${formData[key]}');
      }
    }

    // 检查删除的键
    for (final key in _currentConfig.keys) {
      if (!formData.containsKey(key)) {
        changes.add('$key: ${_currentConfig[key]} → (已删除)');
      }
    }

    return changes.isEmpty ? '无变更' : changes.join('\n');
  }

  void _exportConfig() {
    // TODO: 实现配置导出功能
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('配置导出功能开发中')),
    );
  }

  void _importConfig() {
    // TODO: 实现配置导入功能
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('配置导入功能开发中')),
    );
  }
}
