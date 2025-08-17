# Linch Mind - 个人AI生活助手

![Architecture](https://img.shields.io/badge/architecture-IPC+Flutter+C++-orange)
![Backend](https://img.shields.io/badge/backend-Python_3.13-blue)
![Frontend](https://img.shields.io/badge/frontend-Flutter_3.32-blue)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

**本地化个人AI助手**，通过IPC架构和连接器系统整合数字生活数据，提供智能洞察和推荐。

> **🔒 完全本地化 · ⚡ IPC通信 · 🧠 智能推荐 · 🔌 插件化连接器**

---

## 🌟 核心特色

### 🏗️ **IPC架构**
- **本地通信**: Unix Socket/Named Pipe本地通信，无网络暴露
- **跨平台支持**: macOS、Linux、Windows统一架构
- **资源优化**: 轻量级后端服务

### 🔌 **连接器系统**
- **文件系统连接器**: 文件监控和索引
- **剪贴板连接器**: 剪贴板内容捕获
- **系统信息连接器**: 系统状态监控
- **插件化设计**: C++连接器，支持扩展

### 🧠 **智能处理**
- **向量搜索**: FAISS + sentence-transformers语义搜索
- **知识图谱**: NetworkX图结构关系分析
- **数据存储**: SQLite数据库

### 🎨 **现代UI**
- **跨平台界面**: Flutter响应式UI
- **状态管理**: Riverpod状态管理
- **数据模型**: Freezed数据模型

---

## 🚀 快速开始

### 环境要求
- **Python**: 3.11+
- **Flutter**: 3.32+
- **Poetry**: 依赖管理
- **CMake**: C++连接器构建

### 安装启动
```bash
# 1. 克隆项目
git clone <repository-url>
cd linch-mind

# 2. 初始化环境
./linch-mind init

# 3. 启动应用
./linch-mind start
```

### 管理命令
```bash
# 启动/停止daemon
./linch-mind daemon start
./linch-mind daemon stop

# 启动UI
./linch-mind ui

# 查看状态
./linch-mind status
./linch-mind doctor
```

---

## 🏗️ 项目结构

```
linch-mind/
├── daemon/                    # Python后端服务 (v0.2.0)
│   ├── core/                 # 核心架构
│   ├── services/             # 业务服务
│   ├── config/              # 配置管理
│   └── tests/               # 测试 (237个测试)
├── ui/                       # Flutter UI (v1.0.0)
│   ├── lib/                 # 源代码
│   └── test/                # UI测试
├── connectors/              # C++连接器
│   ├── official/            # 官方连接器
│   │   ├── filesystem/      # 文件系统
│   │   ├── clipboard/       # 剪贴板
│   │   └── system_info/     # 系统信息
│   └── shared/              # 共享库
├── docs/                    # 项目文档
└── scripts/                 # 构建脚本
```

### 实际统计
- **Python文件**: 132个
- **Dart文件**: 94个
- **测试用例**: 237个
- **连接器**: 3个官方连接器

---

## 🛠️ 开发指南

### 后端开发
```bash
cd daemon
poetry install          # 安装依赖
poetry shell            # 激活环境
poetry run pytest      # 运行测试
```

### 前端开发
```bash
cd ui
flutter pub get       # 安装依赖
flutter analyze       # 代码分析
flutter test          # 运行测试
```

### 连接器开发
```bash
cd connectors
./build.sh            # 构建连接器
```

---

## 📚 技术栈

- **后端**: Python 3.13 + Poetry + SQLAlchemy + SQLite
- **前端**: Flutter 3.32 + Riverpod + Freezed
- **AI/ML**: FAISS + NetworkX + sentence-transformers
- **连接器**: C++20 + CMake
- **工具**: Poetry + Black + Flutter Analyze

---

## 🔧 配置

项目支持多环境配置和TOML配置文件：

```bash
# 环境管理
./linch-mind init development
./linch-mind init production

# 配置管理
poetry run python scripts/config_manager_cli.py
```

---

## 🤝 贡献

欢迎贡献代码、报告问题和改进建议：

1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request

### 代码规范
- Python: Black + PEP 8
- Dart: Flutter标准规范
- C++: 现代C++实践

---

## 📄 许可证

本项目基于MIT许可证开源。

---

<div align="center">

**🧠 Linch Mind** - *连接您的数字生活*

*本地化 · 隐私安全 · 开源免费*

</div>
