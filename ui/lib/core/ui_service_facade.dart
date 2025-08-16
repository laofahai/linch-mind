/// UI服务获取Facade - 极简设计
/// 完全对标daemon/core/service_facade.py
/// 目标：消除所有.instance调用，统一为getService<T>()
library;

import 'service_container.dart';

/// 全局服务获取函数 - 替代所有.instance调用
///
/// 使用示例:
/// ```dart
/// // ❌ 旧方式
/// final api = ConnectorLifecycleApiService.instance;
/// final port = DaemonPortService.instance;
///
/// // ✅ 新方式
/// final api = getService<ConnectorLifecycleApiClient>();
/// final port = getService<DaemonPortService>();
/// ```
T getService<T extends Object>() {
  return ServiceContainer.get<T>();
}

/// 注册服务
void registerService<T extends Object>(T service) {
  ServiceContainer.register<T>(service);
}

/// 检查服务是否可用
bool hasService<T extends Object>() {
  return ServiceContainer.has<T>();
}

/// 尝试获取服务，失败返回null
T? tryGetService<T extends Object>() {
  try {
    return getService<T>();
  } catch (e) {
    return null;
  }
}
