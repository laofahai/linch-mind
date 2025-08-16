/// UI服务初始化器 - 从根本解决服务管理问题
/// 统一初始化所有服务，消除分散的.instance调用
library;

import '../services/daemon_port_service.dart';
import '../services/daemon_lifecycle_service.dart';
import '../services/connector_lifecycle_api_client.dart';
import '../services/ipc_client.dart';
import '../utils/enhanced_error_handler.dart';
import '../utils/error_monitor.dart';
import 'ui_service_facade.dart';

/// 初始化所有UI服务
/// 在main.dart中调用一次，整个应用就可以使用getService<T>()
void initializeServices() {
  // 工具服务 - 优先注册基础服务
  registerService<EnhancedErrorHandler>(EnhancedErrorHandler());
  registerService<ErrorMonitor>(ErrorMonitor());

  // IPC核心服务
  registerService<IPCClient>(IPCClient());

  // API客户端服务
  registerService<ConnectorLifecycleApiClient>(ConnectorLifecycleApiClient());

  // Daemon服务 - 先注册这些，其他服务后续添加
  registerService<DaemonPortService>(DaemonPortService.instance);
  registerService<DaemonLifecycleService>(DaemonLifecycleService.instance);
}
