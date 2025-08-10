import 'package:flutter_riverpod/flutter_riverpod.dart';

/// 基础状态接口，所有状态类都应该实现此接口
abstract class BaseState {
  /// 状态最后更新时间
  DateTime get lastUpdate;

  /// 是否有错误
  bool get hasError;

  /// 错误消息
  String? get errorMessage;

  /// 是否正在加载
  bool get isLoading;
}

/// 基础StateNotifier，提供通用的状态管理功能
abstract class BaseStateNotifier<T extends BaseState> extends StateNotifier<T> {
  BaseStateNotifier(super.initialState);

  /// 处理错误的通用方法
  void handleError(String error) {
    state = updateStateWithError(error);
  }

  /// 清除错误的通用方法
  void clearError() {
    state = updateStateWithClearError();
  }

  /// 设置加载状态的通用方法
  void setLoading(bool loading) {
    state = updateStateWithLoading(loading);
  }

  /// 获取最后更新时间
  DateTime get lastUpdate => state.lastUpdate;

  /// 检查是否有错误
  bool get hasError => state.hasError;

  /// 子类需要实现：更新状态时设置错误
  T updateStateWithError(String error);

  /// 子类需要实现：更新状态时清除错误
  T updateStateWithClearError();

  /// 子类需要实现：更新状态时设置加载状态
  T updateStateWithLoading(bool loading);
}

/// 用于带有连接状态的StateNotifier的Mixin
mixin ConnectionStateMixin<T extends BaseState> on BaseStateNotifier<T> {
  /// 设置连接状态的通用方法
  void setConnected(bool connected) {
    state = updateStateWithConnection(connected);
  }

  /// 子类需要实现：更新连接状态
  T updateStateWithConnection(bool connected);
}
