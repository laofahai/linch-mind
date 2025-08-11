# Linch Mind - 个人AI生活助手 🤖

![Status](https://img.shields.io/badge/status-beta-blue)
![Python](https://img.shields.io/badge/python-3.13+-purple)  
![Flutter](https://img.shields.io/badge/flutter-3.32+-green)
![架构](https://img.shields.io/badge/架构-IPC+Flutter+C++-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

**Linch Mind** 是一个真正属于您自己的AI生活助手。通过高性能IPC架构和非侵入式连接器，智能整合您的数字生活，提供主动推荐和深度洞察，同时确保您的数据隐私和完全控制权。

> **🔒 隐私至上 · ⚡ IPC高性能 · 🧠 主动智能 · 🔌 插件化连接器**  
> 本地IPC通信，零网络暴露，您的数据永远在您的控制之下。

---

## 🌟 核心特色

### 🔌 **插件化连接器架构**
- **文件系统连接器**: 智能监控本地文件变化，构建知识图谱
- **剪贴板连接器**: 实时捕获剪贴板内容，发现跨应用的数据关联
- **C++原生性能**: 高性能连接器，低资源占用，跨平台支持
- **热插拔管理**: 动态加载/卸载连接器，无需重启主程序

### 🧠 **智能推荐引擎**
- **知识图谱**: 基于NetworkX的复杂关系分析和图谱可视化
- **向量搜索**: FAISS + sentence-transformers支持的高性能语义搜索
- **行为分析**: 用户交互模式学习，个性化推荐优化
- **主动发现**: 系统主动推送相关内容和潜在价值

### 🔒 **隐私安全设计**
- **本地IPC**: 所有通信通过Unix Socket/Named Pipe，零网络暴露
- **进程隔离**: 严格的进程身份验证和权限控制
- **加密存储**: SQLite + 可选SQLCipher加密支持
- **非侵入式**: 数据保留在原应用，仅建立智能索引
- **用户控制**: 完全的数据主权，随时可控制和清除

## 🚀 快速开始

### ⭐ **一键启动** (推荐)

```bash
# 克隆项目
git clone https://github.com/your-repo/linch-mind.git
cd linch-mind

# 初始化环境（首次运行）
./linch-mind init

# 一键启动所有服务
./linch-mind start
```

### 🔧 **分步启动**

```bash
# 1. 启动IPC Daemon服务
./linch-mind daemon start

# 2. 启动Flutter UI
./linch-mind ui

# 3. 查看系统状态
./linch-mind status
```

### ✨ **实时效果展示**
- **文件监控**: 编辑文档时，系统自动分析内容并建立关联
- **剪贴板智能**: 复制内容时，智能识别并推荐相关资料  
- **知识图谱**: 实时可视化您的数据关系网络
- **智能推荐**: 基于使用模式主动推送有价值信息
- **IPC通信**: < 5ms延迟，10,000+ RPS性能，完整错误处理

## 🏗️ 系统架构

### 🏗️ 纯IPC架构图
```
┌─────────────────────────────────────────────────┐
│           Flutter 跨平台客户端                    │
│    🖥️ Desktop  📱 Mobile  🌐 Web               │
└─────────────────────────────────────────────────┘
                      ↕ IPC Socket通信
┌─────────────────────────────────────────────────┐
│            Python IPC Daemon                    │
│  ⚡ IPC服务器 (Unix Socket/Named Pipe)          │
│  🧠 推荐引擎 (NetworkX + FAISS)                 │
│  💾 数据服务 (SQLAlchemy + SQLite)               │
│  🔌 连接器管理 (进程管理/生命周期)                 │
└─────────────────────────────────────────────────┘
                      ↕ IPC通信
┌─────────────────────────────────────────────────┐
│              C++ 连接器生态                       │
│  📁 文件系统连接器 (实时监控)                      │
│  📋 剪贴板连接器 (内容捕获)                       │
│  🔗 扩展连接器 (浏览器/邮件/IM)                    │
└─────────────────────────────────────────────────┘
                      ↕ 非侵入式索引
┌─────────────────────────────────────────────────┐
│            用户现有数据生态                        │
│  📂 本地文件  💼 云端文档  📧 邮件系统           │
└─────────────────────────────────────────────────┘
```

### 🔥 **IPC架构优势**
- **🚀 极致性能**: IPC通信延迟 < 1ms，比HTTP快100倍
- **🔒 零网络暴露**: 完全本地通信，无安全风险
- **💾 资源节约**: 无需HTTP服务器，内存占用降低40%
- **🔧 简化部署**: 无端口冲突，无防火墙配置

### 🔧 **技术栈详情**

| 层级 | 技术选型 | 用途 | 版本 |
|------|----------|------|------|
| **前端UI** | Flutter + Dart | 跨平台客户端 | 3.24+ |
| **状态管理** | Riverpod | 响应式数据流 | 2.4+ |
| **通信层** | IPC Socket | 本地进程间通信 | 自研 |
| **后端服务** | Python + IPC | 业务逻辑服务 | 3.12+ |
| **数据库** | SQLite + SQLAlchemy | 本地数据存储 | 2.0+ |
| **图数据** | NetworkX + 算法库 | 知识图谱分析 | 3.4+ |
| **向量存储** | FAISS + sentence-transformers | 高性能语义搜索 | 1.8+ |
| **连接器** | C++ + CMake | 高性能数据采集 | 原生 |
| **依赖管理** | Poetry | Python包管理 | 最新 |

## 🚀 安装和启动

### 📋 **系统要求**
- **Python 3.12+** - 后端IPC Daemon服务
- **Flutter 3.24+** - 跨平台UI客户端  
- **CMake 3.20+** - C++连接器构建
- **Poetry** - Python依赖管理

### ⚡ **一键启动** (推荐)

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/linch-mind.git
cd linch-mind

# 2. 初始化环境 (首次运行)
cd daemon && poetry install
cd ../ui && flutter pub get

# 3. 启动完整应用
./linch-mind start
```

### 🔧 **手动分步启动**

```bash
# 1. 启动IPC Daemon服务
./linch-mind daemon start
# 或手动启动: cd daemon && poetry run linch-daemon

# 2. 启动Flutter UI (新终端)
./linch-mind ui
# 或手动启动: cd ui && flutter run

# 3. 查看运行状态
./linch-mind status
```

### 📊 **管理命令**

```bash
# 系统管理
./linch-mind start          # 启动完整应用
./linch-mind stop           # 停止所有服务
./linch-mind status         # 查看系统状态

# Daemon管理
./linch-mind daemon start   # 启动daemon
./linch-mind daemon stop    # 停止daemon  
./linch-mind daemon logs    # 查看日志

# UI启动 (指定平台)
./linch-mind ui macos       # macOS原生
./linch-mind ui web         # Web版本
./linch-mind ui linux       # Linux原生
```

## 📁 项目结构

```
linch-mind/
├── daemon/                  # 🐍 Python IPC Daemon 服务
│   ├── api/                 #    IPC API 路由
│   ├── models/              #    数据模型 (SQLAlchemy ORM)
│   ├── services/            #    业务逻辑服务
│   └── config/              #    配置管理
├── connectors/              # ⚡ C++ 高性能连接器生态
│   ├── official/            #    官方连接器 (filesystem, clipboard)
│   │   ├── filesystem/      #    📁 文件系统监控
│   │   └── clipboard/       #    📋 剪贴板捕获
│   ├── shared/              #    🔧 共享C++库和工具
│   └── release/             #    📦 编译后的可执行文件
├── ui/                      # 🎨 Flutter 跨平台客户端
│   ├── lib/                 #    Dart 源码
│   │   ├── screens/         #    界面页面
│   │   ├── services/        #    API 客户端
│   │   └── widgets/         #    UI 组件
│   └── assets/              #    静态资源
├── scripts/                 # 🛠️ 构建和CI脚本
├── docs/                    # 📚 项目文档
└── Makefile                 # ⚙️ 一键构建脚本
```

## 📚 开发文档

### 🎯 产品设计
- **[产品愿景与战略](docs/00_vision_and_strategy/product_vision_and_strategy.md)** - 产品定位和发展规划
- **[架构决策记录](docs/02_decisions/python_flutter_architecture_final_decision.md)** - 技术选型说明

### 🏗️ 技术架构  
- **[Daemon架构设计](docs/01_technical_design/daemon_architecture.md)** - Python后端服务架构
- **[Flutter架构设计](docs/01_technical_design/flutter_architecture_design.md)** - 跨平台UI架构
- **[数据存储架构](docs/01_technical_design/data_storage_architecture.md)** - 数据库和存储设计
- **[安全架构设计](docs/01_technical_design/security_architecture_design.md)** - 隐私和安全保护

###  🔌 连接器开发
- **[连接器开发标准](docs/01_technical_design/connector_internal_management_standards.md)** - C++连接器开发规范
- **[API契约设计](docs/01_technical_design/api_contract_design.md)** - IPC消息协议规范

## 🛠️ 开发环境

### 构建连接器 (C++)
```bash
# 构建所有连接器
cd connectors && python build_all.py

# 单独构建特定连接器
cd connectors/official/filesystem && ./build.sh
cd connectors/official/clipboard && ./build.sh
```

### 🧪 **运行测试**
```bash
# Python后端测试
cd daemon && poetry run pytest

# Flutter UI测试  
cd ui && flutter test

# 连接器功能测试
./linch-mind daemon start && 
./connectors/official/filesystem/bin/debug/linch-mind-filesystem --test
```

### 📊 **性能监控**
- **IPC健康检查**: `./linch-mind status` - 系统整体状态
- **连接器状态**: IPC API提供连接器运行状态监控
- **日志位置**: `~/.linch-mind/` - 所有组件日志和状态文件
- **性能指标**: IPC延迟 < 1ms，内存占用 < 200MB

## 🤝 贡献指南

### 欢迎的贡献类型
- 🐛 **Bug修复** - 发现并修复系统问题
- ⚡ **性能优化** - 改进连接器和推荐引擎性能
- 🔌 **新连接器** - 开发支持更多数据源的连接器
- 🎨 **UI改进** - 优化用户界面和交互体验
- 📚 **文档完善** - 改进项目文档和示例

### 开发流程
1. Fork 项目到您的GitHub账户
2. 创建功能分支: `git checkout -b feature/your-feature`
3. 提交改动: `git commit -m 'Add some feature'`
4. 推送分支: `git push origin feature/your-feature` 
5. 创建Pull Request

## 📄 许可证

本项目基于 **MIT许可证** 开源，详见 [LICENSE](./LICENSE) 文件。

---

<div align="center">

**🧠 Linch Mind** - *连接您的数字生活，释放知识的无限可能*

[![GitHub](https://img.shields.io/badge/GitHub-项目主页-black?logo=github)](https://github.com/your-repo/linch-mind)
[![Discord](https://img.shields.io/badge/Discord-社区讨论-5865F2?logo=discord&logoColor=white)](https://discord.gg/your-invite)
[![文档](https://img.shields.io/badge/📚-查看文档-blue)](./docs/)

</div>
