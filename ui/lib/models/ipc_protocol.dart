// ignore_for_file: invalid_annotation_target

import 'package:freezed_annotation/freezed_annotation.dart';

part 'ipc_protocol.freezed.dart';
part 'ipc_protocol.g.dart';

/// 纯IPC协议 - 与Python端完全一致
/// 完全摒弃HTTP概念，使用IPC特定的成功/失败标志

/// IPC错误信息
@freezed
class IPCError with _$IPCError {
  const factory IPCError({
    required String code,
    required String message,
    Map<String, dynamic>? details,
  }) = _IPCError;

  factory IPCError.fromJson(Map<String, dynamic> json) =>
      _$IPCErrorFromJson(json);
}

/// IPC元数据
@freezed
class IPCMetadata with _$IPCMetadata {
  const factory IPCMetadata({
    required String timestamp,
    @JsonKey(name: 'request_id') String? requestId,
  }) = _IPCMetadata;

  factory IPCMetadata.fromJson(Map<String, dynamic> json) =>
      _$IPCMetadataFromJson(json);
}

/// 纯IPC响应格式
@freezed
class IPCResponse with _$IPCResponse {
  const factory IPCResponse({
    required bool success,
    dynamic data,  // 允许任何类型的data，包括Map、List等
    IPCError? error,
    IPCMetadata? metadata,
  }) = _IPCResponse;

  factory IPCResponse.fromJson(Map<String, dynamic> json) =>
      _$IPCResponseFromJson(json);

  /// 创建成功响应
  factory IPCResponse.success({
    dynamic data,
    String? requestId,
  }) {
    return IPCResponse(
      success: true,
      data: data,
      metadata: IPCMetadata(
        timestamp: DateTime.now().toIso8601String(),
        requestId: requestId,
      ),
    );
  }

  /// 创建错误响应
  factory IPCResponse.failure({
    required String errorCode,
    required String message,
    Map<String, dynamic>? details,
    String? requestId,
  }) {
    return IPCResponse(
      success: false,
      error: IPCError(
        code: errorCode,
        message: message,
        details: details,
      ),
      metadata: IPCMetadata(
        timestamp: DateTime.now().toIso8601String(),
        requestId: requestId,
      ),
    );
  }
}

/// IPC请求格式
@freezed
class IPCRequest with _$IPCRequest {
  const factory IPCRequest({
    required String method,
    required String path,
    Map<String, dynamic>? data,
    @JsonKey(name: 'query_params') Map<String, dynamic>? queryParams,
    @JsonKey(name: 'path_params') Map<String, String>? pathParams,
    @JsonKey(name: 'request_id') String? requestId,
  }) = _IPCRequest;

  factory IPCRequest.fromJson(Map<String, dynamic> json) =>
      _$IPCRequestFromJson(json);

  /// 创建GET请求
  factory IPCRequest.get({
    required String path,
    Map<String, dynamic>? queryParams,
    String? requestId,
  }) {
    return IPCRequest(
      method: 'GET',
      path: path,
      queryParams: queryParams,
      requestId: requestId,
    );
  }

  /// 创建POST请求
  factory IPCRequest.post({
    required String path,
    Map<String, dynamic>? data,
    String? requestId,
  }) {
    return IPCRequest(
      method: 'POST',
      path: path,
      data: data,
      requestId: requestId,
    );
  }

  /// 创建PUT请求
  factory IPCRequest.put({
    required String path,
    Map<String, dynamic>? data,
    String? requestId,
  }) {
    return IPCRequest(
      method: 'PUT',
      path: path,
      data: data,
      requestId: requestId,
    );
  }
}

/// 连接器运行状态枚举 - 与Python/C++完全一致
enum ConnectorRunningState {
  @JsonValue('stopped')
  stopped,

  @JsonValue('starting')
  starting,

  @JsonValue('running')
  running,

  @JsonValue('stopping')
  stopping,

  @JsonValue('error')
  error;

  /// 获取显示文本
  String get displayName {
    switch (this) {
      case ConnectorRunningState.stopped:
        return '已停止';
      case ConnectorRunningState.starting:
        return '启动中';
      case ConnectorRunningState.running:
        return '运行中';
      case ConnectorRunningState.stopping:
        return '停止中';
      case ConnectorRunningState.error:
        return '错误';
    }
  }

  /// 获取颜色
  int get color {
    switch (this) {
      case ConnectorRunningState.stopped:
        return 0xFF666666; // 灰色
      case ConnectorRunningState.starting:
        return 0xFF2196F3; // 蓝色
      case ConnectorRunningState.running:
        return 0xFF4CAF50; // 绿色
      case ConnectorRunningState.stopping:
        return 0xFFFF9800; // 橙色
      case ConnectorRunningState.error:
        return 0xFFF44336; // 红色
    }
  }

  /// 从字符串创建
  static ConnectorRunningState fromString(String state) {
    switch (state.toLowerCase()) {
      case 'stopped':
        return ConnectorRunningState.stopped;
      case 'starting':
        return ConnectorRunningState.starting;
      case 'running':
        return ConnectorRunningState.running;
      case 'stopping':
        return ConnectorRunningState.stopping;
      case 'error':
        return ConnectorRunningState.error;
      default:
        return ConnectorRunningState.stopped;
    }
  }
}

/// 连接器状态信息 V2 - 使用新的状态模型
@freezed
class ConnectorStatusV2 with _$ConnectorStatusV2 {
  const factory ConnectorStatusV2({
    @JsonKey(name: 'connector_id') required String connectorId,
    @JsonKey(name: 'display_name') required String displayName,
    @Default(true) bool enabled, // 是否启用（基本状态）
    @JsonKey(name: 'running_state')
    @Default(ConnectorRunningState.stopped)
        ConnectorRunningState runningState, // 运行状态
    @JsonKey(name: 'is_installed') @Default(true) bool isInstalled, // 虚拟字段
    @JsonKey(name: 'is_healthy') @Default(false) bool isHealthy, // 是否健康
    @JsonKey(name: 'should_be_running') @Default(false) bool shouldBeRunning, // 是否应该运行
    @JsonKey(name: 'process_id') int? processId,
    @JsonKey(name: 'last_heartbeat') String? lastHeartbeat,
    @JsonKey(name: 'data_count') @Default(0) int dataCount,
    @JsonKey(name: 'last_activity') String? lastActivity,
    @JsonKey(name: 'error_message') String? errorMessage,
    @JsonKey(name: 'error_code') String? errorCode,
  }) = _ConnectorStatusV2;

  factory ConnectorStatusV2.fromJson(Map<String, dynamic> json) =>
      _$ConnectorStatusV2FromJson(json);

  /// 创建新连接器的默认状态
  factory ConnectorStatusV2.newConnector({
    required String connectorId,
    required String displayName,
  }) {
    return ConnectorStatusV2(
      connectorId: connectorId,
      displayName: displayName,
      enabled: true,
      runningState: ConnectorRunningState.stopped,
      isInstalled: true,
    );
  }

  /// 创建禁用连接器状态
  factory ConnectorStatusV2.disabled({
    required String connectorId,
    required String displayName,
  }) {
    return ConnectorStatusV2(
      connectorId: connectorId,
      displayName: displayName,
      enabled: false,
      runningState: ConnectorRunningState.stopped,
      isInstalled: true,
    );
  }
}

/// 常用IPC错误码
class IPCErrorCode {
  // 连接和认证错误
  static const String connectionFailed = 'IPC_CONNECTION_FAILED';
  static const String authRequired = 'IPC_AUTH_REQUIRED';
  static const String authFailed = 'IPC_AUTH_FAILED';
  
  // 请求处理错误
  static const String invalidRequest = 'IPC_INVALID_REQUEST';
  static const String missingParameter = 'IPC_MISSING_PARAMETER';
  static const String requestTimeout = 'IPC_REQUEST_TIMEOUT';
  
  // 连接器相关错误
  static const String connectorNotFound = 'CONNECTOR_NOT_FOUND';
  static const String connectorConfigInvalid = 'CONNECTOR_CONFIG_INVALID';
  static const String connectorStartFailed = 'CONNECTOR_START_FAILED';
  static const String connectorStopFailed = 'CONNECTOR_STOP_FAILED';
  
  // 系统错误
  static const String internalError = 'INTERNAL_ERROR';
  static const String serviceUnavailable = 'SERVICE_UNAVAILABLE';
  static const String resourceNotFound = 'RESOURCE_NOT_FOUND';
}