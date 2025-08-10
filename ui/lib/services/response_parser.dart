/// 通用的响应解析器，统一处理IPC和API响应格式
class ResponseParser {
  /// 解析IPC响应数据，标准化响应格式
  static Map<String, dynamic> parseIPCResponse(Map<String, dynamic> responseData) {
    // 安全地获取data结构
    final data = responseData['data'] as Map<String, dynamic>? ?? responseData;
    
    // 检查响应是否成功
    final success = data['success'] ?? 
                   responseData['success'] ?? 
                   (responseData['status_code'] == 200);
    
    return {
      'success': success,
      'data': data,
      'error': data['error'] ?? responseData['error'],
      'message': data['message'] ?? responseData['message'],
    };
  }

  /// 提取响应中的数据部分
  static Map<String, dynamic> extractData(Map<String, dynamic> responseData) {
    final parsed = parseIPCResponse(responseData);
    return parsed['data'] as Map<String, dynamic>? ?? {};
  }

  /// 检查响应是否成功
  static bool isSuccess(Map<String, dynamic> responseData) {
    final parsed = parseIPCResponse(responseData);
    return parsed['success'] as bool? ?? false;
  }

  /// 获取错误消息
  static String? getError(Map<String, dynamic> responseData) {
    final parsed = parseIPCResponse(responseData);
    return parsed['error'] as String?;
  }

  /// 获取成功消息
  static String? getMessage(Map<String, dynamic> responseData) {
    final parsed = parseIPCResponse(responseData);
    return parsed['message'] as String?;
  }

  /// 适配响应数据为指定格式，用于向后兼容
  static Map<String, dynamic> adaptResponseData(dynamic data) {
    if (data is Map<String, dynamic>) {
      return data;
    } else if (data is List) {
      // 如果是List，包装成Map返回
      return {'data': data};
    } else {
      return data != null ? {'data': data} : {};
    }
  }

  /// 创建标准化的成功响应
  static Map<String, dynamic> createSuccessResponse({
    required dynamic data,
    String? message,
  }) {
    return {
      'success': true,
      'data': data,
      'message': message ?? 'Operation completed successfully',
    };
  }

  /// 创建标准化的错误响应
  static Map<String, dynamic> createErrorResponse({
    required String error,
    dynamic data,
  }) {
    return {
      'success': false,
      'error': error,
      'data': data,
    };
  }
}