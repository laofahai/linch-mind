# Linch Mind 连接器套件

本目录包含Linch Mind的所有连接器实现，负责从各种数据源收集信息并推送到daemon。

## 连接器列表

### 官方连接器
- **filesystem**: 文件系统监控连接器
- **clipboard**: 剪贴板监控连接器

## 开发环境

使用Poetry管理依赖：

```bash
# 安装依赖
poetry install

# 运行特定连接器
poetry run python official/filesystem/main.py
poetry run python official/clipboard/main.py
```

## 架构说明

所有连接器都继承自`shared.base.BaseConnector`基类，提供统一的：
- 配置管理
- 数据推送接口
- 生命周期管理
- 错误处理

## 添加新连接器

1. 在`official/`或`community/`目录创建新连接器
2. 继承`BaseConnector`类
3. 实现`start_monitoring()`方法
4. 实现`get_config_schema()`方法