# Linch Mind - 您的隐私优先个人AI助手

![状态](https://img.shields.io/badge/status-beta-blue)
![Python](https://img.shields.io/badge/python-3.12+-purple)
![Flutter](https://img.shields.io/badge/flutter-3.24+-green)
![架构](https://img.shields.io/badge/architecture-Python+Flutter-orange)
![许可证](https://img.shields.io/badge/license-MIT-lightgrey)

**Linch Mind** 是一个真正属于您自己的AI生活助手。它通过非侵入式的方式连接您所有的数字工具，主动为您发现价值、建立知识关联，并帮助您优化数字生活，同时确保您的数据隐私和完全控制权。

> **隐私至上 · 非侵入式 · 主动智能 · AI插件化**
> 您的数据保留在原地，我们只做智能连接与洞察。

---

## 🌟 核心愿景

我们致力于构建一个：
- **非侵入式**的智能连接器，尊重用户现有的数字生活方式。
- **隐私至上**的个人AI，数据主权完全属于用户，所有敏感计算均在本地进行。
- **主动推荐**的生活助手，从被动搜索转向主动洞察，为您发现隐藏的价值。
- **持续学习**的智能伙伴，与您共同成长和演进。

## ✨ 核心特性

- **🧠 本地AI优先架构**: 支持集成OpenAI、Claude、Ollama等多种AI服务，并可根据任务类型智能路由。核心功能支持离线运行，保障您的数据隐私。
- **🔗 非侵入式连接器**: 通过插件化生态系统连接您现有的工具（如文件系统、剪贴板、Obsidian、邮件等），无需迁移数据。
- **💡 主动智能推荐**: 基于您的行为模式和知识图谱，主动为您提供个性化推荐、发现知识缺口和优化工作流程。
- **🔒 军用级安全**: 采用SQLCipher对本地数据进行AES-256-GCM加密，并提供用户可控的安全级别选项，在安全和性能之间取得平衡。
- **📊 知识图谱**: 自动构建个人知识图谱，可视化您的数据关联和知识结构。

## 🏗️ 技术架构

Linch Mind 采用现代化的 **Python + Flutter** 架构，确保了强大的后端能力和流畅的跨平台用户体验。

```
┌─────────────────────────────────────────────────┐
│                Flutter 跨平台UI                  │
│ (macOS, Windows, Linux, iOS, Android)           │
└─────────────────────────────────────────────────┘
                      ↕ (HTTP/WebSocket)
┌─────────────────────────────────────────────────┐
│             Python FastAPI Daemon 后端服务         │
│  - API 服务 (FastAPI)                           │
│  - 智能推荐引擎                                 │
│  - 知识图谱管理 (NetworkX)                      │
│  - 向量搜索 (FAISS)                             │
│  - 数据持久化 (SQLCipher + SQLAlchemy)          │
│  - 连接器生命周期管理                           │
└─────────────────────────────────────────────────┘
                      ↕ (数据推送)
┌─────────────────────────────────────────────────┐
│              Python 连接器生态系统                │
│  (文件系统, 剪贴板, 邮件, 浏览器等)             │
└─────────────────────────────────────────────────┘
                      ↕ (非侵入式连接)
┌─────────────────────────────────────────────────┐
│           用户现有数据 (保持原位)                 │
└─────────────────────────────────────────────────┘
```

### 技术栈

- **后端**: Python 3.12+, FastAPI, SQLAlchemy, SQLCipher, NetworkX, FAISS
- **前端**: Flutter 3.24+, Dart, Riverpod (状态管理), Dio (HTTP)
- **连接器**: Python 3.12+, Poetry (依赖管理)
- **开发工具**: Makefile, PyInstaller

## 🚀 快速开始

### 系统要求
- Python 3.12+
- Flutter 3.24+
- Poetry

### 安装与启动

1.  **克隆项目**:
    ```bash
    git clone https://github.com/your-repo/linch-mind.git
    cd linch-mind
    ```

2.  **安装依赖**:
    ```bash
    # 安装后端依赖
    cd daemon && poetry install
    # 安装连接器依赖
    cd ../connectors && poetry install
    # 安装前端依赖
    cd ../ui && flutter pub get
    ```

3.  **启动服务 (推荐使用Makefile)**:
    ```bash
    # 启动后端Daemon和所有连接器
    make all
    ```
    或者，手动启动：
    ```bash
    # 启动Daemon
    cd daemon
    poetry run uvicorn api.main:app --host 127.0.0.1 --port 8000

    # 在另一个终端启动文件系统连接器
    cd connectors
    poetry run python official/filesystem/main.py
    ```

4.  **启动UI**:
    ```bash
    cd ui
    flutter run
    ```

## 📁 项目结构

```
linch-mind/
├── daemon/                  # Python FastAPI后端服务
├── connectors/              # Python连接器生态
├── ui/                      # Flutter跨平台应用
├── docs/                    # 详细的项目文档
├── .github/                 # GitHub Actions CI/CD
├── Makefile                 # 连接器管理脚本
└── README.md                # 您正在阅读的文件
```

## 📚 文档

我们拥有完善的内部设计文档，为您提供深入了解项目架构和决策的窗口。

- **[产品愿景与战略](./docs/00_vision_and_strategy/product_vision_and_strategy.md)**
- **[最终架构决策](./docs/02_decisions/python_flutter_architecture_final_decision.md)**
- **[数据存储架构](./docs/01_technical_design/data_storage_architecture.md)**
- **[安全架构设计](./docs/01_technical_design/security_architecture_design.md)**
- **[API契约设计](./docs/01_technical_design/api_contract_design.md)**
- **[连接器开发标准](./docs/01_technical_design/connector_internal_management_standards.md)**

## 🤝 贡献指南

我们欢迎各种形式的贡献！请查看我们的贡献指南（即将推出）以了解如何参与。

## 📄 许可证

本项目采用 [MIT](./LICENSE) 许可证。

---

**Linch Mind** - 连接您的数字生活，释放您的知识潜力。
