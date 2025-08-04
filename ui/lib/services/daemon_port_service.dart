import 'dart:io';
import 'dart:async';

/// Daemon端口服务 - 动态读取~/.linch-mind/daemon.port文件
class DaemonPortService {
  static const String _portFilePath = '.linch-mind/daemon.port';
  static const int _defaultPort = 50001;
  static const String _defaultHost = '127.0.0.1';
  
  static DaemonPortService? _instance;
  static DaemonPortService get instance => _instance ??= DaemonPortService._();
  
  DaemonPortService._();
  
  String? _cachedBaseUrl;
  
  /// 获取daemon的基础URL
  Future<String> getDaemonBaseUrl() async {
    if (_cachedBaseUrl != null) {
      return _cachedBaseUrl!;
    }
    
    try {
      final homeDir = Platform.environment['HOME'] ?? Platform.environment['USERPROFILE'];
      if (homeDir == null) {
        print('[DaemonPortService] 无法获取用户主目录，使用默认端口');
        _cachedBaseUrl = 'http://$_defaultHost:$_defaultPort';
        return _cachedBaseUrl!;
      }
      
      final portFile = File('$homeDir/$_portFilePath');
      
      if (!await portFile.exists()) {
        print('[DaemonPortService] 端口文件不存在: ${portFile.path}，使用默认端口');
        _cachedBaseUrl = 'http://$_defaultHost:$_defaultPort';
        return _cachedBaseUrl!;
      }
      
      final portContent = await portFile.readAsString();
      final port = int.tryParse(portContent.trim());
      
      if (port == null || port <= 0 || port > 65535) {
        print('[DaemonPortService] 端口文件内容无效: "$portContent"，使用默认端口');
        _cachedBaseUrl = 'http://$_defaultHost:$_defaultPort';
        return _cachedBaseUrl!;
      }
      
      _cachedBaseUrl = 'http://$_defaultHost:$port';
      print('[DaemonPortService] 从端口文件读取到端口: $port');
      return _cachedBaseUrl!;
      
    } catch (e) {
      print('[DaemonPortService] 读取端口文件时出错: $e，使用默认端口');
      _cachedBaseUrl = 'http://$_defaultHost:$_defaultPort';
      return _cachedBaseUrl!;
    }
  }
  
  /// 获取daemon端口（仅端口号）
  Future<int> getDaemonPort() async {
    final baseUrl = await getDaemonBaseUrl();
    final uri = Uri.parse(baseUrl);
    return uri.port;
  }
  
  /// 清除缓存的端口信息（用于重新读取）
  void clearCache() {
    _cachedBaseUrl = null;
  }
  
  /// 检查daemon是否可访问
  Future<bool> isDaemonReachable() async {
    try {
      final baseUrl = await getDaemonBaseUrl();
      final client = HttpClient();
      client.connectionTimeout = const Duration(seconds: 2);
      
      final uri = Uri.parse('$baseUrl/health');
      final request = await client.getUrl(uri);
      final response = await request.close();
      
      client.close();
      return response.statusCode == 200;
    } catch (e) {
      print('[DaemonPortService] Daemon不可访问: $e');
      return false;
    }
  }
}