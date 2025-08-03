# 连接器包格式规范 v1.0

## 概述

Linch Mind连接器包格式定义了连接器的分发标准，确保连接器可以在用户环境中安全、可靠地运行。

## 包结构

```
connector-name.zip
├── connector.json          # 连接器元数据 (必需)
├── main.py                 # Python源码入口 (开发)
├── main.exe               # Windows可执行文件 (生产)
├── main-macos             # macOS可执行文件 (生产)  
├── main-linux             # Linux可执行文件 (生产)
└── README.md              # 用户文档 (必需)
```

## 文件说明

### connector.json (必需)
包含连接器元数据，遵循 `/connectors/connector.schema.json` 规范。

关键字段：
- `id`: 唯一标识符 (如 "filesystem", "clipboard")
- `name`: 人类可读名称
- `version`: 语义化版本号
- `entry.production`: 各平台可执行文件映射
- `permissions`: 所需权限列表

### 可执行文件 (必需至少一个)
- **开发模式**: main.py + Python运行时
- **生产模式**: 平台特定的独立可执行文件

### README.md (必需)
用户安装和配置指南，包含：
- 连接器功能描述
- 配置参数说明
- 故障排除指南
- 依赖要求

## 打包流程

```bash
# 1. 编译可执行文件
python build_executable.py

# 2. 验证connector.json
linch-cli validate connector.json

# 3. 打包为zip
linch-cli pack --output connector-name.zip

# 4. 发布到注册表
linch-cli publish connector-name.zip
```

## 验证要求

包在分发前必须通过以下验证：
1. connector.json符合schema
2. 至少包含一个有效的可执行文件
3. README.md存在且非空
4. 包大小合理 (< 50MB)
5. 权限声明完整

## 安全考虑

- 可执行文件必须是独立的，不依赖用户环境
- 不允许包含源码中的敏感信息
- 权限申请必须最小化
- 所有外部网络访问需明确声明

## 向后兼容性

当前版本: 1.0
- 未来版本变更将保持向后兼容
- 重大格式变更将递增主版本号
- 旧版本连接器继续支持运行