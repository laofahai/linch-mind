# 剪贴板连接器

监控系统剪贴板变化，自动记录和索引复制的内容，支持文本、链接、图片等多种格式

## 基本信息

- **版本**: 1.5.0
- **分类**: system
- **作者**: Linch Mind Team
- **许可证**: MIT

## 功能特性

- 多实例支持: 否
- 最大实例数: 1
- 热重载配置: 是
- 健康检查: 是

## 配置说明

### 配置结构

```json
{
  "type": "object",
  "title": "剪贴板连接器配置",
  "properties": {
    "check_interval": {
      "type": "number",
      "title": "检查间隔 (秒)",
      "description": "剪贴板内容变化检查频率",
      "default": 1.0,
      "minimum": 0.1,
      "maximum": 10.0
    },
    "max_content_length": {
      "type": "integer",
      "title": "最大内容长度",
      "description": "超过此长度的内容将被截断",
      "default": 10000,
      "minimum": 100,
      "maximum": 100000
    },
    "content_filters": {
      "type": "object",
      "title": "内容过滤",
      "properties": {
        "ignore_passwords": {
          "type": "boolean",
          "title": "忽略密码",
          "description": "自动检测并忽略密码内容",
          "default": true
        },
        "ignore_duplicates": {
          "type": "boolean",
          "title": "忽略重复内容",
          "description": "不记录连续相同的剪贴板内容",
          "default": true
        },
        "min_content_length": {
          "type": "integer",
          "title": "最小内容长度",
          "description": "忽略过短的内容",
          "default": 3,
          "minimum": 1
        }
      }
    }
  },
  "required": [
    "check_interval",
    "max_content_length"
  ]
}
```

## 预定义模板

### 标准监控

推荐的剪贴板监控配置

```json
{
  "check_interval": 1.0,
  "max_content_length": 10000,
  "content_filters": {
    "ignore_passwords": true,
    "ignore_duplicates": true,
    "min_content_length": 3
  }
}
```

### 高频监控

更频繁的内容检查，适合密集工作

```json
{
  "check_interval": 0.5,
  "max_content_length": 50000,
  "content_filters": {
    "ignore_passwords": true,
    "ignore_duplicates": false,
    "min_content_length": 1
  }
}
```

## 安装说明

1. 下载连接器包
2. 在Linch Mind中导入连接器
3. 创建实例并配置

## 使用示例

1. 打开Linch Mind应用
2. 进入连接器管理页面
3. 点击"添加连接器"选择剪贴板连接器
4. 根据需要选择预定义模板或自定义配置
5. 启动连接器实例

---

*此文档由维护工具自动生成于 2025-08-02 16:17:59*
