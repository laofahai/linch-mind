import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../services/daemon_port_service.dart';

/// 注册表配置数据模型
class RegistryConfig {
  final String registryUrl;
  final int cacheDurationHours;
  final bool autoRefresh;
  final String? currentSource;
  final String? lastUpdated;
  final int? totalConnectors;
  final String status;

  const RegistryConfig({
    required this.registryUrl,
    required this.cacheDurationHours,
    required this.autoRefresh,
    this.currentSource,
    this.lastUpdated,
    this.totalConnectors,
    required this.status,
  });

  factory RegistryConfig.fromJson(Map<String, dynamic> json) {
    return RegistryConfig(
      registryUrl: json['registry_url'] ?? '',
      cacheDurationHours: json['cache_duration_hours'] ?? 6,
      autoRefresh: json['auto_refresh'] ?? true,
      currentSource: json['current_source'],
      lastUpdated: json['last_updated'],
      totalConnectors: json['total_connectors'],
      status: json['status'] ?? 'unknown',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'registry_url': registryUrl,
      'cache_duration_hours': cacheDurationHours,
      'auto_refresh': autoRefresh,
    };
  }

  RegistryConfig copyWith({
    String? registryUrl,
    int? cacheDurationHours,
    bool? autoRefresh,
    String? currentSource,
    String? lastUpdated,
    int? totalConnectors,
    String? status,
  }) {
    return RegistryConfig(
      registryUrl: registryUrl ?? this.registryUrl,
      cacheDurationHours: cacheDurationHours ?? this.cacheDurationHours,
      autoRefresh: autoRefresh ?? this.autoRefresh,
      currentSource: currentSource ?? this.currentSource,
      lastUpdated: lastUpdated ?? this.lastUpdated,
      totalConnectors: totalConnectors ?? this.totalConnectors,
      status: status ?? this.status,
    );
  }
}

/// 注册表配置服务
class RegistryConfigService {
  static final DaemonPortService _portService = DaemonPortService.instance;

  static Future<RegistryConfig> getConfig() async {
    final baseUrl = await _portService.getDaemonBaseUrl();
    final response = await http.get(
      Uri.parse('$baseUrl/api/system/config/registry'),
      headers: {'Content-Type': 'application/json'},
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return RegistryConfig.fromJson(data);
    } else {
      throw Exception('获取注册表配置失败: ${response.statusCode}');
    }
  }

  static Future<RegistryConfig> updateConfig(RegistryConfig config) async {
    final baseUrl = await _portService.getDaemonBaseUrl();
    final response = await http.put(
      Uri.parse('$baseUrl/api/system/config/registry'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(config.toJson()),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return RegistryConfig.fromJson(data);
    } else {
      throw Exception('更新注册表配置失败: ${response.statusCode}');
    }
  }

  static Future<Map<String, dynamic>> testUrl(String url) async {
    final baseUrl = await _portService.getDaemonBaseUrl();
    final response = await http.post(
      Uri.parse(
          '$baseUrl/api/system/config/registry/test?test_url=${Uri.encodeComponent(url)}'),
      headers: {'Content-Type': 'application/json'},
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('测试URL失败: ${response.statusCode}');
    }
  }

  static Future<Map<String, dynamic>> refreshRegistry() async {
    final baseUrl = await _portService.getDaemonBaseUrl();
    final response = await http.post(
      Uri.parse('$baseUrl/api/system/config/registry/refresh'),
      headers: {'Content-Type': 'application/json'},
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('刷新注册表失败: ${response.statusCode}');
    }
  }
}

/// Riverpod Provider
final registryConfigProvider =
    StateNotifierProvider<RegistryConfigNotifier, AsyncValue<RegistryConfig>>(
        (ref) {
  return RegistryConfigNotifier();
});

class RegistryConfigNotifier extends StateNotifier<AsyncValue<RegistryConfig>> {
  RegistryConfigNotifier() : super(const AsyncValue.loading()) {
    loadConfig();
  }

  Future<void> loadConfig() async {
    try {
      state = const AsyncValue.loading();
      final config = await RegistryConfigService.getConfig();
      state = AsyncValue.data(config);
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
    }
  }

  Future<void> updateConfig(RegistryConfig config) async {
    try {
      final updatedConfig = await RegistryConfigService.updateConfig(config);
      state = AsyncValue.data(updatedConfig);
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
    }
  }

  Future<Map<String, dynamic>> testUrl(String url) async {
    return await RegistryConfigService.testUrl(url);
  }

  Future<Map<String, dynamic>> refreshRegistry() async {
    final result = await RegistryConfigService.refreshRegistry();
    await loadConfig(); // 刷新后重新加载配置
    return result;
  }
}

/// 注册表设置界面
class RegistrySettingsScreen extends ConsumerStatefulWidget {
  const RegistrySettingsScreen({super.key});

  @override
  ConsumerState<RegistrySettingsScreen> createState() =>
      _RegistrySettingsScreenState();
}

class _RegistrySettingsScreenState
    extends ConsumerState<RegistrySettingsScreen> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _urlController;
  late bool _autoRefresh;
  late int _cacheDuration;

  bool _isTestingUrl = false;
  String? _testResult;
  bool _testSuccess = false;

  @override
  void initState() {
    super.initState();
    _urlController = TextEditingController();
    _autoRefresh = true;
    _cacheDuration = 6;
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  void _initializeForm(RegistryConfig config) {
    _urlController.text = config.registryUrl;
    _autoRefresh = config.autoRefresh;
    _cacheDuration = config.cacheDurationHours;
  }

  Future<void> _testUrl() async {
    if (_urlController.text.isEmpty) return;

    setState(() {
      _isTestingUrl = true;
      _testResult = null;
    });

    try {
      final result = await ref
          .read(registryConfigProvider.notifier)
          .testUrl(_urlController.text);
      setState(() {
        _testSuccess = result['status'] == 'success';
        _testResult = result['message'];
      });
    } catch (e) {
      setState(() {
        _testSuccess = false;
        _testResult = '测试失败: $e';
      });
    } finally {
      setState(() {
        _isTestingUrl = false;
      });
    }
  }

  Future<void> _saveConfig() async {
    if (!_formKey.currentState!.validate()) return;

    final configAsync = ref.read(registryConfigProvider);
    final currentConfig = configAsync.value;
    if (currentConfig == null) return;

    final newConfig = currentConfig.copyWith(
      registryUrl: _urlController.text,
      autoRefresh: _autoRefresh,
      cacheDurationHours: _cacheDuration,
    );

    try {
      await ref.read(registryConfigProvider.notifier).updateConfig(newConfig);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('配置已保存')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('保存失败: $e'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }

  Future<void> _refreshRegistry() async {
    try {
      final result =
          await ref.read(registryConfigProvider.notifier).refreshRegistry();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(result['message'])),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('刷新失败: $e'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final configAsync = ref.watch(registryConfigProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('连接器注册表设置'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _refreshRegistry,
            tooltip: '刷新注册表',
          ),
        ],
      ),
      body: configAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.error_outline,
                size: 64,
                color: Theme.of(context).colorScheme.error,
              ),
              const SizedBox(height: 16),
              Text(
                '加载配置失败: $error',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: Theme.of(context).colorScheme.error,
                    ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () =>
                    ref.read(registryConfigProvider.notifier).loadConfig(),
                child: const Text('重试'),
              ),
            ],
          ),
        ),
        data: (config) {
          // 初始化表单数据
          WidgetsBinding.instance.addPostFrameCallback((_) {
            if (_urlController.text.isEmpty) {
              _initializeForm(config);
            }
          });

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 当前状态卡片
                  _buildStatusCard(config),

                  const SizedBox(height: 24),

                  // 注册表URL设置
                  _buildUrlSection(),

                  const SizedBox(height: 24),

                  // 高级设置
                  _buildAdvancedSettings(),

                  const SizedBox(height: 32),

                  // 保存按钮
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _saveConfig,
                      child: const Padding(
                        padding: EdgeInsets.symmetric(vertical: 12),
                        child: Text('保存配置'),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildStatusCard(RegistryConfig config) {
    final statusColor = config.status == 'available'
        ? Colors.green
        : config.status == 'unavailable'
            ? Colors.red
            : Colors.orange;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  config.status == 'available'
                      ? Icons.check_circle
                      : config.status == 'unavailable'
                          ? Icons.error
                          : Icons.help,
                  color: statusColor,
                ),
                const SizedBox(width: 8),
                Text(
                  '注册表状态',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            _buildInfoRow('状态', config.status == 'available' ? '可用' : '不可用'),
            if (config.currentSource != null)
              _buildInfoRow('当前源', config.currentSource!),
            if (config.totalConnectors != null)
              _buildInfoRow('连接器数量', '${config.totalConnectors} 个'),
            if (config.lastUpdated != null)
              _buildInfoRow('最后更新', _formatDateTime(config.lastUpdated!)),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              '$label:',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).disabledColor,
                  ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildUrlSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '注册表URL',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: _urlController,
          decoration: InputDecoration(
            hintText:
                'https://github.com/laofahai/linch-mind/releases/latest/download/registry.json',
            border: const OutlineInputBorder(),
            suffixIcon: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (_isTestingUrl)
                  const Padding(
                    padding: EdgeInsets.all(12),
                    child: SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                  )
                else
                  IconButton(
                    icon: const Icon(Icons.check_circle_outline),
                    onPressed: _testUrl,
                    tooltip: '测试URL',
                  ),
              ],
            ),
          ),
          validator: (value) {
            if (value == null || value.isEmpty) {
              return '请输入注册表URL';
            }
            if (Uri.tryParse(value)?.hasAbsolutePath != true) {
              return '请输入有效的URL';
            }
            return null;
          },
        ),
        if (_testResult != null) ...[
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: _testSuccess
                  ? Colors.green.withValues(alpha: 0.1)
                  : Colors.red.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: _testSuccess ? Colors.green : Colors.red,
                width: 1,
              ),
            ),
            child: Row(
              children: [
                Icon(
                  _testSuccess ? Icons.check_circle : Icons.error,
                  color: _testSuccess ? Colors.green : Colors.red,
                  size: 16,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    _testResult!,
                    style: TextStyle(
                      color: _testSuccess ? Colors.green : Colors.red,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
        const SizedBox(height: 8),
        Text(
          '这是连接器市场的数据源地址。默认使用GitHub Release，你也可以配置自己的注册表服务器。',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).disabledColor,
              ),
        ),
      ],
    );
  }

  Widget _buildAdvancedSettings() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '高级设置',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
        ),
        const SizedBox(height: 16),

        // 自动刷新开关
        SwitchListTile(
          title: const Text('自动刷新'),
          subtitle: const Text('定期自动检查注册表更新'),
          value: _autoRefresh,
          onChanged: (value) {
            setState(() {
              _autoRefresh = value;
            });
          },
        ),

        const SizedBox(height: 16),

        // 缓存时长设置
        Text(
          '缓存时长: $_cacheDuration 小时',
          style: Theme.of(context).textTheme.bodyMedium,
        ),
        const SizedBox(height: 8),
        Slider(
          value: _cacheDuration.toDouble(),
          min: 1,
          max: 24,
          divisions: 23,
          label: '$_cacheDuration 小时',
          onChanged: (value) {
            setState(() {
              _cacheDuration = value.round();
            });
          },
        ),
        const SizedBox(height: 8),
        Text(
          '缓存时间越长，减少网络请求但可能获取不到最新数据',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).disabledColor,
              ),
        ),
      ],
    );
  }

  String _formatDateTime(String isoString) {
    try {
      final dateTime = DateTime.parse(isoString);
      final now = DateTime.now();
      final difference = now.difference(dateTime);

      if (difference.inMinutes < 1) {
        return '刚刚';
      } else if (difference.inHours < 1) {
        return '${difference.inMinutes} 分钟前';
      } else if (difference.inDays < 1) {
        return '${difference.inHours} 小时前';
      } else {
        return '${difference.inDays} 天前';
      }
    } catch (e) {
      return isoString;
    }
  }
}
