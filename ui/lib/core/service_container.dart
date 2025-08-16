/// UI服务容器 - 极简设计
/// 直接对标daemon/core/container.py核心思路
library;

/// 服务未注册异常
class ServiceNotRegisteredException implements Exception {
  final String message;
  ServiceNotRegisteredException(this.message);
  @override
  String toString() => message;
}

/// 极简服务容器 - 只做服务存储和获取
class ServiceContainer {
  static final Map<Type, Object> _services = {};

  /// 注册服务
  static void register<T extends Object>(T service) {
    _services[T] = service;
  }

  /// 获取服务
  static T get<T extends Object>() {
    final service = _services[T];
    if (service == null) {
      throw ServiceNotRegisteredException('服务 ${T.toString()} 未注册');
    }
    return service as T;
  }

  /// 检查是否已注册
  static bool has<T extends Object>() => _services.containsKey(T);

  /// 重置（测试用）
  static void reset() => _services.clear();
}
