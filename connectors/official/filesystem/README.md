# 文件系统连接器

实时监控文件系统变化，智能索引文件内容。支持多目录配置、文件类型过滤、内容提取等功能

## 基本信息

- **版本**: 2.0.0
- **分类**: local_files
- **作者**: Linch Mind Team
- **许可证**: MIT

## 功能特性

- 多实例支持: 是
- 最大实例数: 10
- 热重载配置: 是
- 健康检查: 是

## 配置说明

### 配置结构

```json
{
  "type": "object",
  "title": "文件系统连接器配置",
  "description": "配置文件系统监控的路径、文件类型和过滤规则",
  "properties": {
    "global_config": {
      "type": "object",
      "title": "全局默认配置",
      "properties": {
        "default_extensions": {
          "type": "array",
          "title": "默认文件类型",
          "items": {
            "type": "string"
          },
          "default": [
            ".txt",
            ".md",
            ".py",
            ".js",
            ".html"
          ]
        },
        "max_file_size": {
          "type": "integer",
          "title": "最大文件大小 (MB)",
          "default": 10,
          "minimum": 1,
          "maximum": 1000
        }
      }
    },
    "directory_configs": {
      "type": "array",
      "title": "目录配置",
      "items": {
        "type": "object",
        "properties": {
          "path": {
            "type": "string",
            "title": "监控路径"
          },
          "display_name": {
            "type": "string",
            "title": "显示名称"
          },
          "extensions": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "priority": {
            "type": "string",
            "enum": [
              "low",
              "normal",
              "high"
            ],
            "default": "normal"
          }
        },
        "required": [
          "path"
        ]
      }
    }
  },
  "required": [
    "global_config",
    "directory_configs"
  ]
}
```

## 预定义模板

### 文档监控

监控文档目录，适合笔记和写作

```json
{
  "global_config": {
    "default_extensions": [
      ".md",
      ".txt",
      ".doc",
      ".docx",
      ".pdf"
    ],
    "max_file_size": 50
  },
  "directory_configs": [
    {
      "path": "~/Documents",
      "display_name": "文档目录",
      "priority": "high"
    }
  ]
}
```

### 开发监控

监控代码项目，适合开发者

```json
{
  "global_config": {
    "default_extensions": [
      ".py",
      ".js",
      ".ts",
      ".java",
      ".go",
      ".rs"
    ],
    "max_file_size": 5
  },
  "directory_configs": [
    {
      "path": "~/Projects",
      "display_name": "项目目录",
      "priority": "high"
    }
  ]
}
```

### 下载监控

监控下载目录，自动整理新文件

```json
{
  "global_config": {
    "default_extensions": [
      ".pdf",
      ".txt",
      ".md",
      ".epub"
    ],
    "max_file_size": 100
  },
  "directory_configs": [
    {
      "path": "~/Downloads",
      "display_name": "下载目录",
      "priority": "low"
    }
  ]
}
```

## 安装说明

1. 下载连接器包
2. 在Linch Mind中导入连接器
3. 创建实例并配置

## 使用示例

1. 打开Linch Mind应用
2. 进入连接器管理页面
3. 点击"添加连接器"选择文件系统连接器
4. 根据需要选择预定义模板或自定义配置
5. 启动连接器实例

---

*此文档由维护工具自动生成于 2025-08-05 08:40:00*
