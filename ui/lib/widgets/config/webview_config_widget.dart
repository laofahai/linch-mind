import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:webview_flutter/webview_flutter.dart';

/// WebView连接器配置组件
/// 支持复杂的HTML配置界面
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
  ConsumerState<WebViewConfigWidget> createState() => _WebViewConfigWidgetState();
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
          },
          onWebResourceError: (WebResourceError error) {
            setState(() {
              _hasError = true;
              _errorMessage = error.description;
              _isLoading = false;
            });
          },
          onNavigationRequest: (NavigationRequest request) {
            // 控制导航行为，阻止外部链接
            if (request.url.startsWith('http') && 
                !request.url.contains('localhost') && 
                !request.url.contains('127.0.0.1')) {
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

    _loadConfigurationURL();
  }

  /// 加载配置URL
  void _loadConfigurationURL() {
    // 构建WebView配置URL
    final configUrl = 'http://localhost:58471/webview-config/html/${widget.connectorId}';
    _controller?.loadRequest(Uri.parse(configUrl));
  }



  /// 处理来自JavaScript的消息
  void _handleJavaScriptMessage(String message) {
    try {
      final data = json.decode(message) as Map<String, dynamic>;
      final action = data['action'] as String?;
      final payload = data['data'] as Map<String, dynamic>?;

      switch (action) {
        case 'configChanged':
          if (payload != null) {
            _pendingConfig = payload;
            widget.onConfigChanged(payload);
          }
          break;

        case 'saveConfig':
          if (payload != null) {
            _pendingConfig = payload;
            widget.onConfigChanged(payload);
            if (widget.onSave != null) {
              widget.onSave!();
            }
          }
          break;

        case 'validateConfig':
          // 处理验证请求
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

      await _controller!.runJavaScript('''
        receiveFlutterMessage('$message');
      ''');
    } catch (e) {
      debugPrint('向WebView发送消息失败: $e');
    }
  }

  /// 刷新WebView内容
  void refresh() {
    _loadConfigurationURL();
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
            Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red.shade300,
            ),
            const SizedBox(height: 16),
            Text(
              'WebView 加载失败',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              _errorMessage,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.red.shade600,
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                setState(() {
                  _hasError = false;
                  _isLoading = true;
                });
                _loadConfigurationURL();
              },
              child: const Text('重试'),
            ),
          ],
        ),
      );
    }

    return Stack(
      children: [
        if (_controller != null)
          WebViewWidget(controller: _controller!),
        if (_isLoading || widget.isLoading)
          Container(
            color: Colors.white.withOpacity(0.9),
            child: const Center(
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