# 连接器发布目录

这个目录包含连接器的发布相关文件和构建产物。

## 目录结构

```
release/
├── README.md           # 本文件
├── dist/              # 构建产物目录 (自动生成)
│   ├── filesystem-connector
│   ├── clipboard-connector
│   └── ...
├── packages/          # 打包文件目录 (未来功能)
│   ├── filesystem-v1.0.0.zip
│   └── clipboard-v1.0.0.zip
└── changelog.md       # 发布日志 (自动生成)
```

## 自动构建流程

1. **版本管理**: `scripts/version_manager.py` 负责版本号递增
2. **构建**: `scripts/connector_builder.py` 使用PyInstaller打包
3. **注册表**: `scripts/registry_generator.py` 生成统一注册表
4. **发布**: GitHub Actions自动处理发布流程

## 手动构建

```bash
# 构建单个连接器
cd connectors
python scripts/connector_builder.py official/filesystem --output release/dist

# 生成注册表
python scripts/registry_generator.py --output release/registry.json --format

# 版本管理
python scripts/version_manager.py official/filesystem/connector.json --bump minor
```