import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:webview_flutter/webview_flutter.dart';
import '../../services/webview_config_api_client.dart';

/// WebView连接器配置组件
/// 支持复杂的HTML配置界面 (纯IPC模式)
class WebViewConfigWidget extends ConsumerStatefulWidget {
  final String connectorId;
  final String connectorName;
  final Map<String, dynamic> configSchema;
  final Map<String, dynamic> currentConfig;
  final Map<String, dynamic> uiSchema;
  final Function(Map<String, dynamic> config) onConfigChanged;
  final VoidCallback? onSave;
  final bool isLoading;

  const WebViewConfigWidget({
    super.key,
    required this.connectorId,
    required this.connectorName,
    required this.configSchema,
    required this.currentConfig,
    required this.uiSchema,
    required this.onConfigChanged,
    this.onSave,
    this.isLoading = false,
  });

  @override
  ConsumerState<WebViewConfigWidget> createState() =>
      _WebViewConfigWidgetState();
}

class _WebViewConfigWidgetState extends ConsumerState<WebViewConfigWidget> {
  WebViewController? _controller;
  bool _isLoading = true;
  bool _hasError = false;
  String _errorMessage = '';
  Map<String, dynamic> _pendingConfig = {};

  @override
  void initState() {
    super.initState();
    _initializeWebView();
  }

  void _initializeWebView() {
    // 创建WebViewController
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(const Color(0x00000000))
      ..setNavigationDelegate(
        NavigationDelegate(
          onProgress: (int progress) {
            // 更新加载进度
          },
          onPageStarted: (String url) {
            setState(() {
              _isLoading = true;
              _hasError = false;
            });
          },
          onPageFinished: (String url) {
            setState(() {
              _isLoading = false;
            });
            // 页面加载完成后，发送初始配置
            _sendMessageToWebView('updateConfig', widget.currentConfig);
            _sendMessageToWebView('updateSchema', {
              'configSchema': widget.configSchema,
              'uiSchema': widget.uiSchema,
            });
          },
          onWebResourceError: (WebResourceError error) {
            setState(() {
              _hasError = true;
              _errorMessage = error.description;
              _isLoading = false;
            });
          },
          onNavigationRequest: (NavigationRequest request) {
            // 仅允许加载data URI
            if (!request.url.startsWith('data:')) {
              return NavigationDecision.prevent;
            }
            return NavigationDecision.navigate;
          },
        ),
      )
      ..addJavaScriptChannel(
        'FlutterConfigBridge',
        onMessageReceived: (JavaScriptMessage message) {
          _handleJavaScriptMessage(message.message);
        },
      );

    _loadConfigurationHtml();
  }

  /// 通过IPC加载配置HTML
  Future<void> _loadConfigurationHtml() async {
    setState(() {
      _isLoading = true;
      _hasError = false;
    });
    try {
      final apiClient = ref.read(webViewConfigApiClientProvider);
      final htmlContent =
          await apiClient.getWebViewConfigHtml(widget.connectorId);

      // 使用loadHtmlString加载从IPC获取的HTML
      await _controller?.loadHtmlString(htmlContent);
    } catch (e) {
      setState(() {
        _hasError = true;
        _errorMessage = '无法加载配置界面: $e';
        _isLoading = false;
      });
    }
  }

  /// 处理来自JavaScript的消息
  void _handleJavaScriptMessage(String message) {
    try {
      final data = json.decode(message) as Map<String, dynamic>;
      final action = data['action'] as String?;
      final payload = data['data'];

      switch (action) {
        case 'configChanged':
          if (payload is Map<String, dynamic>) {
            _pendingConfig = payload;
            widget.onConfigChanged(payload);
          }
          break;

        case 'saveConfig':
          if (payload is Map<String, dynamic>) {
            _pendingConfig = payload;
            widget.onConfigChanged(payload);
          }
          if (widget.onSave != null) {
            widget.onSave!();
          }
          break;

        case 'requestInitialData':
          _sendMessageToWebView('updateConfig', widget.currentConfig);
          _sendMessageToWebView('updateSchema', {
            'configSchema': widget.configSchema,
            'uiSchema': widget.uiSchema,
          });
          break;

        default:
          debugPrint('未知的JavaScript消息: $action');
      }
    } catch (e) {
      debugPrint('处理JavaScript消息失败: $e');
    }
  }

  /// 向WebView发送消息
  void _sendMessageToWebView(String action, dynamic data) async {
    if (_controller == null) return;

    try {
      final message = json.encode({
        'action': action,
        'data': data,
        'timestamp': DateTime.now().millisecondsSinceEpoch,
      });

      // 使用 runJavaScript 而不是不安全的 evaluateJavascript
      await _controller!
          .runJavaScript('window.receiveFlutterMessage(\'$message\');');
    } catch (e) {
      debugPrint('向WebView发送消息失败: $e');
    }
  }

  /// 刷新WebView内容
  void refresh() {
    _loadConfigurationHtml();
  }

  /// 更新配置数据
  void updateConfig(Map<String, dynamic> newConfig) {
    _sendMessageToWebView('updateConfig', newConfig);
  }

  /// 更新Schema
  void updateSchema({
    Map<String, dynamic>? configSchema,
    Map<String, dynamic>? uiSchema,
  }) {
    _sendMessageToWebView('updateSchema', {
      'configSchema': configSchema ?? widget.configSchema,
      'uiSchema': uiSchema ?? widget.uiSchema,
    });
  }

  /// 显示验证错误
  void showValidationErrors(List<String> errors) {
    _sendMessageToWebView('showValidationErrors', errors);
  }

  @override
  Widget build(BuildContext context) {
    if (_hasError) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red,
            ),
            const SizedBox(height: 16),
            Text(
              'WebView 加载失败',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Text(
                _errorMessage,
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Colors.red.shade700,
                    ),
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadConfigurationHtml,
              child: const Text('重试'),
            ),
          ],
        ),
      );
    }

    return Stack(
      children: [
        if (_controller != null) WebViewWidget(controller: _controller!),
        if (_isLoading || widget.isLoading)
          const AbsorbPointer(
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('正在加载配置界面...'),
                ],
              ),
            ),
          ),
      ],
    );
  }
}
