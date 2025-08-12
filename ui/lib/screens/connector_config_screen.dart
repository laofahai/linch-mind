import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:reactive_forms/reactive_forms.dart';
import '../services/connector_config_api_client.dart';
import '../services/webview_config_api_client.dart';
import '../services/form_builder_service.dart';
import '../widgets/config/reactive_config_widgets.dart';
import '../widgets/config/webview_config_widget.dart';

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

class _ConnectorConfigScreenState extends ConsumerState<ConnectorConfigScreen> {
  FormGroup? _form;
  Map<String, dynamic> _configSchema = {};
  Map<String, dynamic> _uiSchema = {};
  Map<String, dynamic> _currentConfig = {};
  Map<String, dynamic> _defaultConfig = {};

  bool _isLoading = true;
  bool _isSaving = false;
  String? _errorMessage;
  List<String> _validationErrors = [];

  // WebView相关状态
  bool _supportsWebView = false;
  bool _useWebView = false;

  // 缓存上一次的表单数据，避免重复深度比较
  Map<String, dynamic>? _lastFormData;
  bool? _lastHasChanges;

  // 防止重复加载的标志
  bool _isCurrentlyLoading = false;

  @override
  void initState() {
    super.initState();
    debugPrint(
        '[DEBUG] ConnectorConfigScreen initState called for ${widget.connectorId}');
    _loadConfigData();
  }

  @override
  void dispose() {
    _form?.dispose();
    super.dispose();
  }

  /// 安全的Map类型转换
  Map<String, dynamic>? _safeMapCast(dynamic value) {
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

  Future<void> _loadConfigData() async {
    debugPrint('[DEBUG] _loadConfigData called for ${widget.connectorId}');

    // 防止重复加载
    if (_isCurrentlyLoading) {
      debugPrint(
          '[DEBUG] Already loading, skipping duplicate call for ${widget.connectorId}');
      return;
    }

    debugPrint('[DEBUG] Starting config load for ${widget.connectorId}');

    _isCurrentlyLoading = true;
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final configService = ref.read(connectorConfigApiClientProvider);
      final webViewService = ref.read(webViewConfigApiClientProvider);

      // 并行加载schema、当前配置和WebView支持检查
      final results = await Future.wait([
        configService.getConfigSchema(widget.connectorId),
        configService.getCurrentConfig(widget.connectorId),
        _checkWebViewSupport(webViewService),
      ]);

      final schemaResponse = results[0] as dynamic;
      final configResponse = results[1] as dynamic;
      final webViewSupported = results[2] as bool;

      // 添加调试信息
      if (schemaResponse.success) {
        debugPrint(
            '[DEBUG] Schema Response Data Type: ${schemaResponse.data.runtimeType}');
        debugPrint('[DEBUG] Schema Response Data: ${schemaResponse.data}');
      }
      if (configResponse.success) {
        debugPrint(
            '[DEBUG] Config Response Data Type: ${configResponse.data.runtimeType}');
        debugPrint('[DEBUG] Config Response Data: ${configResponse.data}');
      }

      setState(() {
        _supportsWebView = webViewSupported;
        _useWebView = webViewSupported; // 默认使用WebView（如果支持）
      });

      if (schemaResponse.success && configResponse.success) {
        final schemaData = _safeMapCast(schemaResponse.data) ?? {};
        final configData = _safeMapCast(configResponse.data) ?? {};

        // 正确提取后端返回的schema结构 - 使用安全的类型转换
        _configSchema = _safeMapCast(schemaData['json_schema']) ?? {};
        _uiSchema = _safeMapCast(schemaData['ui_schema']) ?? {};

        // 从json_schema中提取默认值
        final properties = _safeMapCast(_configSchema['properties']) ?? {};
        _defaultConfig = <String, dynamic>{};
        for (final entry in properties.entries) {
          final fieldSchema = _safeMapCast(entry.value) ?? {};
          if (fieldSchema.containsKey('default')) {
            _defaultConfig[entry.key] = fieldSchema['default'];
          }
        }

        _currentConfig = _safeMapCast(configData['config']) ?? {};
        debugPrint('[DEBUG] Initial _currentConfig loaded: $_currentConfig');

        // 构建reactive form - 传递正确的JSON Schema格式
        _form = FormBuilderService.buildFormFromSchema(
          schema: _configSchema,
          initialData: _currentConfig,
          uiSchema: _uiSchema,
        );

        // 优化：移除频繁setState的监听器，改为使用ReactiveFormConsumer
        // 这样可以避免每次表单值变化都触发整个页面重建

        debugPrint(
            '[DEBUG] Form built, immediate form data extraction: ${FormBuilderService.extractFormData(_form!, _configSchema)}');
        debugPrint(
            '[DEBUG] Config load completed successfully for ${widget.connectorId}');

        setState(() {
          _isLoading = false;
        });
        _isCurrentlyLoading = false;
      } else {
        setState(() {
          _errorMessage = schemaResponse.message.isNotEmpty
              ? schemaResponse.message
              : configResponse.message;
          _isLoading = false;
        });
        _isCurrentlyLoading = false;
      }
    } catch (e) {
      setState(() {
        _errorMessage = '加载配置时发生错误: $e';
        _isLoading = false;
      });
      _isCurrentlyLoading = false;
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
      final formData =
          FormBuilderService.extractFormData(_form!, _configSchema);

      // 先验证配置
      final validationResponse = await configService.validateConfig(
        widget.connectorId,
        formData,
      );

      final validationData = _safeMapCast(validationResponse.data) ?? {};
      if (!validationResponse.success ||
          !(validationData['valid'] as bool? ?? false)) {
        setState(() {
          _validationErrors = _parseValidationErrors(validationData['errors']);
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
        // 更新当前配置并清除缓存
        setState(() {
          _currentConfig = Map<String, dynamic>.from(formData);
          _isSaving = false;
          // 清除缓存以强制重新计算变更状态
          _lastFormData = null;
          _lastHasChanges = null;
        });

        final saveData = _safeMapCast(saveResponse.data) ?? {};
        _showSuccessSnackBar((saveData['hot_reload_applied'] as bool? ?? false)
            ? '配置已保存并热重载成功'
            : '配置已保存，需要重启连接器生效');
      } else {
        setState(() {
          _errorMessage = saveResponse.message;
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

  Future<bool> _checkWebViewSupport(
      WebViewConfigApiClient webViewService) async {
    try {
      final response =
          await webViewService.checkWebViewSupport(widget.connectorId);
      if (response.success && response.data != null) {
        final data = _safeMapCast(response.data);
        if (data == null) return false;
        return data['supports_webview'] as bool? ?? false;
      }
      return false;
    } catch (e) {
      debugPrint('检查WebView支持失败: $e');
      return false;
    }
  }

  /// 解析后端返回的验证错误信息
  List<String> _parseValidationErrors(dynamic errorsData) {
    final List<String> errors = [];

    if (errorsData is List) {
      for (final errorItem in errorsData) {
        final errorMap = _safeMapCast(errorItem);
        if (errorMap != null) {
          final field = errorMap['field'] as String? ?? '';
          final message = errorMap['message'] as String? ?? '';

          if (field.isNotEmpty && message.isNotEmpty) {
            // 格式化字段名（如果是嵌套字段，显示更友好的名称）
            final friendlyFieldName = _getFriendlyFieldName(field);
            errors.add('$friendlyFieldName: $message');
          } else if (message.isNotEmpty) {
            errors.add(message);
          }
        } else if (errorItem is String) {
          errors.add(errorItem);
        }
      }
    }

    return errors;
  }

  /// 获取字段的友好显示名称
  String _getFriendlyFieldName(String fieldPath) {
    // 尝试从schema中获取字段的title
    if (fieldPath.contains('.')) {
      // 嵌套字段
      final fieldSchema =
          FormBuilderService.getNestedFieldSchema(fieldPath, _configSchema);
      final title = fieldSchema['title'] as String?;
      if (title != null && title.isNotEmpty) {
        return title;
      }
    } else {
      // 普通字段
      final properties = _safeMapCast(_configSchema['properties']) ?? {};
      final fieldSchema = _safeMapCast(properties[fieldPath]) ?? {};
      final title = fieldSchema['title'] as String?;
      if (title != null && title.isNotEmpty) {
        return title;
      }
    }

    // 如果没有title，返回格式化的字段名
    return fieldPath.replaceAll('_', ' ').replaceAll('.', ' -> ');
  }

  void _onConfigChanged(Map<String, dynamic> newConfig) {
    setState(() {
      _currentConfig = newConfig;
    });
  }

  void _onWebViewSave() {
    _validateAndSaveConfig();
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

      // 清除缓存以强制重新计算变更状态
      _lastFormData = null;
      _lastHasChanges = null;
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
    // Check if we have a form to wrap with ReactiveForm
    if (_form != null && !_isLoading && _errorMessage == null) {
      return ReactiveForm(
        formGroup: _form!,
        child: Scaffold(
          appBar: AppBar(
            title: Text('${widget.connectorName} - 配置'),
            actions: [
              // 保存按钮 - 始终显示在应用栏中
              if (!_isLoading && _form != null)
                ReactiveFormConsumer(
                  builder: (context, form, child) {
                    final hasChanges = _hasConfigChanges();
                    return IconButton(
                      onPressed: _isSaving ? null : _validateAndSaveConfig,
                      icon: _isSaving
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : Icon(
                              Icons.save,
                              color: hasChanges
                                  ? Theme.of(context).colorScheme.primary
                                  : Theme.of(context)
                                      .colorScheme
                                      .onSurfaceVariant,
                            ),
                      tooltip: _isSaving
                          ? '保存中...'
                          : hasChanges
                              ? '保存配置'
                              : '无变更需保存',
                    );
                  },
                ),
              // 取消/重置按钮
              if (!_isLoading && _form != null)
                ReactiveFormConsumer(
                  builder: (context, form, child) {
                    final hasChanges = _hasConfigChanges();
                    return hasChanges
                        ? IconButton(
                            onPressed: _isSaving
                                ? null
                                : () async {
                                    final confirmed = await _showConfirmDialog(
                                      '取消修改',
                                      '确定要取消当前的修改吗？所有未保存的更改将丢失。',
                                    );
                                    if (confirmed) {
                                      // 重新加载原始配置
                                      _form!.dispose();
                                      _form = FormBuilderService
                                          .buildFormFromSchema(
                                        schema: _configSchema,
                                        initialData: _currentConfig,
                                        uiSchema: _uiSchema,
                                      );
                                      // 清除缓存以强制重新计算变更状态
                                      _lastFormData = null;
                                      _lastHasChanges = null;
                                      setState(() {});
                                    }
                                  },
                            icon: const Icon(Icons.cancel_outlined),
                            tooltip: '取消修改',
                          )
                        : const SizedBox.shrink();
                  },
                ),
              // WebView切换按钮
              if (_supportsWebView && !_isLoading)
                IconButton(
                  icon: Icon(_useWebView ? Icons.web : Icons.apps),
                  tooltip: _useWebView ? '切换到原生表单' : '切换到WebView界面',
                  onPressed: () {
                    setState(() {
                      _useWebView = !_useWebView;
                    });
                  },
                ),
              if (!_isLoading)
                PopupMenuButton<String>(
                  onSelected: (value) {
                    switch (value) {
                      case 'reset':
                        _resetToDefaults();
                        break;
                      case 'webview_toggle':
                        if (_supportsWebView) {
                          setState(() {
                            _useWebView = !_useWebView;
                          });
                        }
                        break;
                    }
                  },
                  itemBuilder: (context) => [
                    if (_supportsWebView)
                      PopupMenuItem(
                        value: 'webview_toggle',
                        child: ListTile(
                          leading: Icon(_useWebView ? Icons.apps : Icons.web),
                          title: Text(_useWebView ? '使用原生表单' : '使用WebView界面'),
                        ),
                      ),
                    const PopupMenuItem(
                      value: 'reset',
                      child: ListTile(
                        leading: Icon(Icons.refresh),
                        title: Text('重置为默认值'),
                      ),
                    ),
                  ],
                ),
            ],
          ),
          body: Column(
            children: [
              Expanded(child: _buildBody()),
              _buildBottomActionBar(),
            ],
          ),
          floatingActionButton: _buildFloatingActionButton(),
        ),
      );
    }

    // For loading, error, or no form state, use regular Scaffold
    return Scaffold(
      appBar: AppBar(
        title: Text('${widget.connectorName} - 配置'),
        actions: [
          // 保存按钮 - 在错误状态下禁用
          if (_errorMessage == null)
            IconButton(
              onPressed: null, // 在loading/error状态下禁用
              icon: const Icon(Icons.save),
              tooltip: '保存配置（暂不可用）',
            ),
          // WebView切换按钮
          if (_supportsWebView && !_isLoading)
            IconButton(
              icon: Icon(_useWebView ? Icons.web : Icons.apps),
              tooltip: _useWebView ? '切换到原生表单' : '切换到WebView界面',
              onPressed: () {
                setState(() {
                  _useWebView = !_useWebView;
                });
              },
            ),
          if (!_isLoading)
            PopupMenuButton<String>(
              onSelected: (value) {
                switch (value) {
                  case 'reset':
                    _resetToDefaults();
                    break;
                  case 'webview_toggle':
                    if (_supportsWebView) {
                      setState(() {
                        _useWebView = !_useWebView;
                      });
                    }
                    break;
                }
              },
              itemBuilder: (context) => [
                if (_supportsWebView)
                  PopupMenuItem(
                    value: 'webview_toggle',
                    child: ListTile(
                      leading: Icon(_useWebView ? Icons.apps : Icons.web),
                      title: Text(_useWebView ? '使用原生表单' : '使用WebView界面'),
                    ),
                  ),
                const PopupMenuItem(
                  value: 'reset',
                  child: ListTile(
                    leading: Icon(Icons.refresh),
                    title: Text('重置为默认值'),
                  ),
                ),
              ],
            ),
        ],
      ),
      body: Column(
        children: [
          Expanded(child: _buildBody()),
          _buildBottomActionBar(),
        ],
      ),
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

    return _buildConfigForm();
  }

  Widget _buildConfigForm() {
    // 如果支持WebView且用户选择使用WebView
    if (_supportsWebView && _useWebView) {
      return _buildWebViewConfig();
    }

    // 否则使用原生表单
    final sections = _safeMapCast(_uiSchema['ui:sections']) ?? {};

    if (sections.isEmpty) {
      return _buildBasicConfigForm();
    }

    return _buildSectionedConfigForm(sections);
  }

  Widget _buildWebViewConfig() {
    return WebViewConfigWidget(
      connectorId: widget.connectorId,
      connectorName: widget.connectorName,
      configSchema: _configSchema,
      currentConfig: _currentConfig,
      uiSchema: _uiSchema,
      onConfigChanged: _onConfigChanged,
      onSave: _onWebViewSave,
      isLoading: _isSaving,
    );
  }

  Widget _buildSectionedConfigForm(Map<String, dynamic> sections) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: sections.entries.map((entry) {
          final sectionId = entry.key;
          final sectionConfig = _safeMapCast(entry.value);
          if (sectionConfig == null) return const SizedBox.shrink();

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
    final fields = _safeMapCast(sectionConfig['ui:fields']) ?? {};

    Widget content = Column(
      children: fields.entries.map((fieldEntry) {
        final fieldName = fieldEntry.key;
        final fieldSchema =
            _safeMapCast(_configSchema['properties']?[fieldName]) ?? {};

        // 获取字段Schema和UI配置 - 支持嵌套字段
        Map<String, dynamic> actualFieldSchema;
        if (fieldName.contains('.')) {
          // 嵌套字段，从根Schema中获取正确的字段Schema
          actualFieldSchema = FormBuilderService.getNestedFieldSchema(
            fieldName,
            _configSchema,
          );
        } else {
          actualFieldSchema = fieldSchema;
        }

        // 合并UI配置
        final mergedConfig = FormBuilderService.getFieldUIConfig(
          fieldName,
          actualFieldSchema,
          _uiSchema,
        );

        return Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: ReactiveConfigWidgets.buildFieldWidget(
            fieldName: fieldName, // 直接使用原始字段路径，reactive_forms支持点号访问
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
    final properties = _safeMapCast(_configSchema['properties']) ?? {};

    // 处理空配置情况
    if (properties.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.settings_outlined,
              size: 64,
              color: Theme.of(context).disabledColor,
            ),
            const SizedBox(height: 16),
            Text(
              '此连接器无需额外配置',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Theme.of(context).disabledColor,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              '连接器使用默认设置运行，如有需要可联系管理员自定义配置。',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).disabledColor,
                  ),
            ),
          ],
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: properties.entries.map((entry) {
          final fieldName = entry.key;
          final fieldSchema = _safeMapCast(entry.value);
          if (fieldSchema == null) return const SizedBox.shrink();

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

  /// 构建底部操作栏
  Widget _buildBottomActionBar() {
    if (_isLoading || _form == null) {
      return const SizedBox.shrink();
    }

    return ReactiveFormConsumer(
      builder: (context, form, child) {
        final hasChanges = _hasConfigChanges();

        return Container(
          padding: const EdgeInsets.all(16.0),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surface,
            border: Border(
              top: BorderSide(
                color: Theme.of(context).dividerColor,
                width: 1.0,
              ),
            ),
          ),
          child: Row(
            children: [
              // 状态指示器
              if (hasChanges)
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.primaryContainer,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        Icons.edit_outlined,
                        size: 16,
                        color: Theme.of(context).colorScheme.onPrimaryContainer,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '有未保存的更改',
                        style: TextStyle(
                          fontSize: 12,
                          color:
                              Theme.of(context).colorScheme.onPrimaryContainer,
                        ),
                      ),
                    ],
                  ),
                ),
              const Spacer(),
              // 取消按钮
              if (hasChanges)
                OutlinedButton.icon(
                  onPressed: _isSaving
                      ? null
                      : () async {
                          final confirmed = await _showConfirmDialog(
                            '取消修改',
                            '确定要取消当前的修改吗？所有未保存的更改将丢失。',
                          );
                          if (confirmed) {
                            // 重新加载原始配置
                            _form!.dispose();
                            _form = FormBuilderService.buildFormFromSchema(
                              schema: _configSchema,
                              initialData: _currentConfig,
                              uiSchema: _uiSchema,
                            );
                            // 清除缓存以强制重新计算变更状态
                            _lastFormData = null;
                            _lastHasChanges = null;
                            setState(() {});
                          }
                        },
                  icon: const Icon(Icons.cancel_outlined),
                  label: const Text('取消'),
                ),
              if (hasChanges) const SizedBox(width: 12),
              // 保存按钮
              ElevatedButton.icon(
                onPressed:
                    (!hasChanges || _isSaving) ? null : _validateAndSaveConfig,
                icon: _isSaving
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.save),
                label: Text(
                  _isSaving
                      ? '保存中...'
                      : hasChanges
                          ? '保存配置'
                          : '已保存',
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget? _buildFloatingActionButton() {
    // 由于已经有底部操作栏，不再需要FloatingActionButton
    return null;
  }

  bool _hasConfigChanges() {
    if (_form == null) return false;

    try {
      final currentData =
          FormBuilderService.extractFormData(_form!, _configSchema);

      // 使用缓存优化：如果表单数据没变，直接返回缓存的结果
      if (_lastFormData != null && _deepEquals(currentData, _lastFormData!)) {
        return _lastHasChanges ?? false;
      }

      // 缓存当前表单数据
      _lastFormData = Map<String, dynamic>.from(currentData);

      // 使用深度比较检查是否有变化
      final hasChanges = !_deepEquals(currentData, _currentConfig);
      _lastHasChanges = hasChanges;

      // 只在有变更或首次检查时输出调试信息
      if (hasChanges || (_lastHasChanges == null)) {
        debugPrint('[DEBUG] Config changes detected: $hasChanges');
        if (hasChanges) {
          debugPrint('[DEBUG] Current: $currentData');
          debugPrint('[DEBUG] Original: $_currentConfig');
        }
      }

      return hasChanges;
    } catch (e) {
      debugPrint('[ERROR] Failed to check config changes: $e');
      // 发生错误时，返回true以确保保存按钮可见
      return true;
    }
  }

  /// 深度比较两个Map是否相等
  bool _deepEquals(Map<String, dynamic> map1, Map<String, dynamic> map2) {
    if (map1.length != map2.length) {
      return false;
    }

    for (final key in map1.keys) {
      if (!map2.containsKey(key)) {
        return false;
      }

      final value1 = map1[key];
      final value2 = map2[key];

      // 递归比较嵌套的Map
      if (value1 is Map<String, dynamic> && value2 is Map<String, dynamic>) {
        if (!_deepEquals(value1, value2)) {
          return false;
        }
      }
      // 比较列表类型
      else if (value1 is List && value2 is List) {
        if (!_deepEqualsList(value1, value2)) {
          return false;
        }
      }
      // 比较基本类型，使用类型安全的比较
      else if (!_valuesEqual(value1, value2)) {
        return false;
      }
    }

    return true;
  }

  /// 深度比较两个List是否相等
  bool _deepEqualsList(List list1, List list2) {
    if (list1.length != list2.length) return false;

    for (int i = 0; i < list1.length; i++) {
      final item1 = list1[i];
      final item2 = list2[i];

      if (item1 is Map<String, dynamic> && item2 is Map<String, dynamic>) {
        if (!_deepEquals(item1, item2)) return false;
      } else if (item1 is List && item2 is List) {
        if (!_deepEqualsList(item1, item2)) return false;
      } else if (!_valuesEqual(item1, item2)) {
        return false;
      }
    }

    return true;
  }

  /// 类型安全的值比较
  bool _valuesEqual(dynamic value1, dynamic value2) {
    // 处理null值
    if (value1 == null && value2 == null) return true;
    if (value1 == null || value2 == null) return false;

    // 类型必须相同
    if (value1.runtimeType != value2.runtimeType) return false;

    // 使用标准相等比较
    return value1 == value2;
  }
}
