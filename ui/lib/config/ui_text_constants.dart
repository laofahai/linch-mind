/// UI字符串常量管理系统
/// 
/// 提供集中化的UI文本管理，支持placeholder文本的动态配置
/// 为未来的国际化系统提供基础架构
class UITextConstants {
  
  /// 输入框Placeholder文本配置
  static const Map<String, String> placeholders = {
    // 基础输入类型
    'text': '请输入文本内容',
    'textarea': '请输入多行文本内容',
    'number': '请输入数字',
    'integer': '请输入整数',
    
    // 特殊格式输入
    'email': 'user@example.com',
    'url': 'https://example.com',
    'password': '请输入密码',
    
    // 数组和对象输入
    'tag_input': '输入后按回车添加标签',
    'array_input': '请添加列表项',
    'object_key': '属性名',
    'object_value': '属性值',
    
    // 目录和文件选择
    'directory': '选择目录路径',
    'file': '选择文件路径',
    
    // 搜索和过滤
    'search': '搜索...',
    'filter': '过滤条件',
    
    // 其他常用placeholder
    'name': '请输入名称',
    'title': '请输入标题',
    'description': '请输入描述',
    'comment': '请输入备注',
  };
  
  /// 根据字段配置生成智能placeholder文本
  /// 
  /// 优先级：
  /// 1. 配置中明确指定的placeholder
  /// 2. 根据字段格式(format)推断的placeholder
  /// 3. 根据字段类型(type)的默认placeholder  
  /// 4. 根据字段名称推断的placeholder
  /// 5. 通用默认placeholder
  static String getPlaceholder({
    required Map<String, dynamic> fieldConfig,
    String? fieldName,
    String? fieldType,
  }) {
    // 1. 优先使用配置中明确指定的placeholder
    final explicitPlaceholder = fieldConfig['placeholder'] as String?;
    if (explicitPlaceholder != null && explicitPlaceholder.isNotEmpty) {
      return explicitPlaceholder;
    }
    
    // 2. 根据字段格式推断placeholder
    final format = fieldConfig['format'] as String?;
    if (format != null) {
      final formatPlaceholder = placeholders[format];
      if (formatPlaceholder != null) {
        return formatPlaceholder;
      }
    }
    
    // 3. 根据字段类型获取默认placeholder
    final type = fieldType ?? fieldConfig['type'] as String?;
    if (type != null) {
      final typePlaceholder = placeholders[type];
      if (typePlaceholder != null) {
        return typePlaceholder;
      }
    }
    
    // 4. 根据字段名称推断placeholder
    if (fieldName != null) {
      final namePlaceholder = _inferPlaceholderFromFieldName(fieldName);
      if (namePlaceholder != null) {
        return namePlaceholder;
      }
    }
    
    // 5. 返回通用默认placeholder
    return placeholders['text'] ?? '请输入内容';
  }
  
  /// 获取组件类型专用的placeholder
  /// 
  /// 用于响应式配置组件的特定场景
  static String getWidgetPlaceholder(String widgetType, {
    Map<String, dynamic>? fieldConfig,
    String? fieldName,
  }) {
    // 优先检查字段配置
    if (fieldConfig != null) {
      final explicitPlaceholder = fieldConfig['placeholder'] as String?;
      if (explicitPlaceholder != null && explicitPlaceholder.isNotEmpty) {
        return explicitPlaceholder;
      }
    }
    
    // 根据组件类型返回专用placeholder
    switch (widgetType) {
      case 'email_input':
        return placeholders['email']!;
      case 'url_input':
        return placeholders['url']!;
      case 'password_input':
        return placeholders['password']!;
      case 'tag_input':
        return placeholders['tag_input']!;
      case 'textarea':
        return placeholders['textarea']!;
      case 'number_input':
        return placeholders['number']!;
      case 'directory_picker':
        return placeholders['directory']!;
      case 'text_input':
      default:
        return placeholders['text']!;
    }
  }
  
  /// 根据字段名称推断合适的placeholder
  static String? _inferPlaceholderFromFieldName(String fieldName) {
    final lowerFieldName = fieldName.toLowerCase();
    
    // 邮箱相关字段
    if (lowerFieldName.contains('email') || lowerFieldName.contains('mail')) {
      return placeholders['email'];
    }
    
    // URL相关字段
    if (lowerFieldName.contains('url') || 
        lowerFieldName.contains('link') ||
        lowerFieldName.contains('website') ||
        lowerFieldName.contains('endpoint')) {
      return placeholders['url'];
    }
    
    // 密码相关字段
    if (lowerFieldName.contains('password') || 
        lowerFieldName.contains('pwd') ||
        lowerFieldName.contains('secret') ||
        lowerFieldName.contains('token')) {
      return placeholders['password'];
    }
    
    // 名称相关字段
    if (lowerFieldName.contains('name') || lowerFieldName.contains('title')) {
      return placeholders['name'];
    }
    
    // 描述相关字段
    if (lowerFieldName.contains('description') || 
        lowerFieldName.contains('desc') ||
        lowerFieldName.contains('comment') ||
        lowerFieldName.contains('note')) {
      return placeholders['description'];
    }
    
    // 路径相关字段
    if (lowerFieldName.contains('path') || 
        lowerFieldName.contains('dir') ||
        lowerFieldName.contains('folder')) {
      return placeholders['directory'];
    }
    
    return null;
  }
  
  /// 验证消息配置
  static const Map<String, String> validationMessages = {
    'required': '此项为必填项',
    'email': '请输入有效的邮箱地址',
    'uri': '请输入有效的URL地址',
    'minLength': '输入内容太短',
    'maxLength': '输入内容太长',
    'min': '数值太小',
    'max': '数值太大',
    'pattern': '格式不正确',
  };
  
  /// 按钮文本配置
  static const Map<String, String> buttons = {
    'add': '添加',
    'remove': '移除',
    'delete': '删除',
    'edit': '编辑',
    'save': '保存',
    'cancel': '取消',
    'confirm': '确认',
    'browse': '浏览',
    'select': '选择',
    'clear': '清空',
    'reset': '重置',
  };
  
  /// 标签文本配置
  static const Map<String, String> labels = {
    'predefined_options': '常用选项',
    'selected_items': '已选择',
    'custom_input': '自定义输入',
    'array_item': '项目',
    'object_property': '属性',
    'object_value': '值',
  };
  
  /// 帮助文本配置
  static const Map<String, String> helpTexts = {
    'tag_input': '选择常用选项或输入自定义标签',
    'directory_picker': '点击浏览按钮选择目录',
    'array_input': '使用添加按钮增加列表项',
    'object_editor': '添加键值对配置项',
    'email_format': '请输入有效的邮箱地址格式',
    'url_format': '请输入完整的URL地址，包含协议（如 https://）',
  };
}