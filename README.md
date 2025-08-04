# Linch Mind - 个人AI生活助手

![Status](https://img.shields.io/badge/status-development-blue)
![Python](https://img.shields.io/badge/python-3.11+-purple)
![Flutter](https://img.shields.io/badge/flutter-3.24+-green)
![AI](https://img.shields.io/badge/AI-Local%20First-orange)

真正的个人AI生活助手，连接你的所有数字工具，主动发现价值，优化你的数字生活。

> **隐私优先 · 非侵入式 · 主动智能 · AI插件化**  
> 你的数据留在原地，我们只做智能连接和洞察

## ✨ 核心特性

### 🤖 本地AI优先架构
- **多AI集成**: 支持OpenAI、Claude、Ollama等多种AI提供者
- **智能路由**: 根据任务类型自动选择最佳AI模型
- **隐私保障**: 本地AI推理，数据不离开设备
- **实时推荐**: AI驱动的智能内容发现和关联分析

### 🔗 非侵入式连接器生态
- **文件系统监控**: 实时监控指定目录，智能索引文件变化
- **剪贴板采集**: 自动分析剪贴板内容，提取有价值信息
- **插件化设计**: 易于扩展的连接器架构
- **配置化监控**: 支持目录级别的个性化配置

### 💡 主动智能推荐引擎
- **行为驱动**: 基于用户交互模式的个性化推荐
- **关系发现**: 自动发现知识点间的深度关联
- **实时分析**: 即时处理新数据，动态更新推荐
- **多维权重**: 综合时间、频率、兴趣等多因素评分

### 🔒 隐私优先设计
- **本地处理**: 所有AI推理和数据分析在本地完成
- **数据主权**: 用户完全控制数据生命周期
- **加密存储**: 敏感数据本地加密存储
- **零云依赖**: 核心功能无需互联网连接

## 🚀 快速开始

### 系统要求
- Python 3.11+ 
- Flutter 3.24+ (UI开发)
- Poetry (依赖管理)
- 8GB+ 可用内存推荐

### 🎯 一键启动 (推荐)

```bash
# 克隆项目
git clone <repository-url>
cd linch-mind

# 使用开发脚本快速启动
./dev.sh                    # 启动daemon + filesystem连接器
./dev.sh all               # 启动daemon + 所有连接器
./dev.sh daemon            # 只启动daemon
./dev.sh connector filesystem  # 只启动指定连接器
```

### 📦 手动安装配置

```bash
# 1. 安装daemon依赖
cd daemon
poetry install

# 2. 安装连接器依赖  
cd ../connectors
poetry install

# 3. 安装Flutter依赖
cd ../ui
flutter pub get

# 4. 启动daemon
cd ../daemon
poetry run uvicorn api.main:app --host 127.0.0.1 --port 58471

# 5. 启动连接器
cd ../connectors
PYTHONPATH=. poetry run python official/filesystem/main.py

# 6. 启动UI
cd ../ui
flutter run -d macos
```

### 🧪 测试连接器管理

```bash
# 测试daemon连接器管理功能
python test_connector_management.py
```

## 🏗️ 系统架构

### 当前架构: Flutter + Python Daemon + 连接器生态

```
┌─────────────────────────────────────────────────┐
│                Flutter 跨平台UI                  │
│  ┌─────────────────────────────────────────────┐ │
│  │  智能推荐界面 + AI对话 + 知识图谱浏览      │ │
│  │  连接器管理 + 配置界面 + 实时监控          │ │
│  └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
                      ↕ HTTP API
┌─────────────────────────────────────────────────┐
│               Python Daemon 后端服务             │
│  ┌─────────────────────────────────────────────┐ │
│  │  FastAPI + SQLite + 智能推荐引擎           │ │
│  │  连接器管理 + 数据处理 + AI服务集成        │ │
│  └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
                      ↕ 数据推送
┌─────────────────────────────────────────────────┐
│                 连接器生态系统                    │
│  ┌──────────────┐ ┌──────────────┐ ┌─────────────┐ │
│  │ 文件系统监控  │ │ 剪贴板采集   │ │   更多...   │ │
│  │ Poetry环境   │ │ 内容分析     │ │   插件      │ │
│  └──────────────┘ └──────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────┘
                      ↕ 非侵入式连接
┌─────────────────────────────────────────────────┐
│              用户现有数据 (保持原位)               │
│     文件系统 + Obsidian + 文档 + 项目...         │
└─────────────────────────────────────────────────┘
```

### 架构优势
- **技术栈现代化**: Python后端 + Flutter跨平台UI
- **服务解耦**: Daemon与连接器独立运行，易于调试
- **Poetry统一管理**: 依赖管理标准化，环境隔离
- **开发友好**: 一键启动脚本，快速开发验证

## 📁 项目结构 (当前架构)

```
linch-mind/
├── daemon/                  # Python FastAPI后端服务
│   ├── api/                 # API路由和接口
│   │   ├── main.py         # 应用入口
│   │   └── routers/        # 模块化路由
│   ├── models/             # 数据模型定义
│   ├── services/           # 业务逻辑服务
│   ├── config/             # 配置管理
│   └── pyproject.toml      # Python依赖管理
├── connectors/             # Python连接器生态
│   ├── official/           # 官方连接器
│   │   ├── filesystem/     # 文件系统连接器
│   │   └── clipboard/      # 剪贴板连接器
│   ├── shared/             # 公共基础类
│   ├── pyproject.toml      # 连接器依赖管理
│   └── README.md           # 连接器开发指南
├── ui/                     # Flutter跨平台应用
│   ├── lib/
│   │   ├── screens/        # 应用界面
│   │   ├── services/       # API客户端
│   │   ├── models/         # 数据模型
│   │   └── widgets/        # UI组件
│   └── pubspec.yaml        # Flutter依赖管理
├── scripts/                # 开发工具脚本
│   └── dev-start.py        # Python开发启动器
├── docs/                   # 项目文档
├── dev.sh                  # 一键开发启动脚本 ⭐
├── test_connector_management.py  # 连接器测试脚本
└── CLAUDE.md               # 开发上下文和指导
```

## 📊 当前开发状态 (Session V62+)

### ✅ 已完成的核心基础设施
- **✅ 数据持久化**: SQLite + SQLAlchemy ORM + 完整数据模型
- **✅ 日志系统**: Python logging + 结构化日志输出  
- **✅ 智能推荐**: 行为驱动推荐引擎 + 多维权重计算
- **✅ 连接器架构**: Poetry统一管理 + 插件化设计
- **✅ 开发工具**: 一键启动脚本 + 测试工具

### 🔄 当前焦点: 连接器生态完善
- **✅ 依赖管理统一**: 连接器迁移到Poetry
- **✅ 开发脚本**: `dev.sh` 简化启动流程
- **✅ API端点修复**: 连接器配置和管理API
- **🔄 连接器管理UI**: Flutter界面开发中
- **📅 端到端验证**: 完整数据链路测试

### 📈 智能数据统计
- **知识实体**: 75个实体的真实知识图谱
- **关系网络**: 263个智能关联关系
- **推荐质量**: 基于真实数据的个性化推荐
- **行为追踪**: 用户交互模式分析和优化

## 🛠️ 开发工具

### 一键启动脚本 `dev.sh` ⭐
```bash
./dev.sh                    # 默认: daemon + filesystem连接器
./dev.sh daemon             # 只启动daemon
./dev.sh connector <name>   # 启动指定连接器
./dev.sh all                # 启动daemon + 所有连接器
./dev.sh ui                 # 启动Flutter UI
./dev.sh help               # 显示帮助
```

### 连接器开发
```bash
# 开发新连接器
cd connectors
poetry run python scripts/connector-dev.py

# 测试连接器
poetry run python official/filesystem/main.py
```

### API测试
```bash
# 测试daemon连接器管理
python test_connector_management.py

# 手动API测试
curl http://localhost:58471/api/v1/connectors/
curl http://localhost:58471/api/v1/connectors/filesystem/config
```

## 🔧 技术栈

- **后端**: Python 3.11+ + FastAPI + SQLAlchemy + SQLite
- **前端**: Flutter 3.24+ + Dart (跨平台UI)
- **连接器**: Python + Poetry + 异步处理
- **AI集成**: 多AI提供者支持 (OpenAI, Claude, Ollama)
- **数据处理**: 实时数据流 + 智能索引 + 向量搜索
- **开发工具**: Poetry + 一键启动脚本 + 自动化测试

## 📚 文档导航

### 🌟 核心文档
- **[开发上下文 (CLAUDE.md)](CLAUDE.md)** - 完整开发指导和当前状态
- **[连接器开发指南](connectors/README.md)** - 连接器开发和扩展

### 🏗️ 技术设计
- **[Daemon架构设计](docs/01_technical_design/daemon_architecture.md)** - Python FastAPI后台服务架构
- **[Flutter架构设计](docs/01_technical_design/flutter_architecture_design.md)** - 跨平台UI架构和状态管理
- **[连接器开发标准](docs/01_technical_design/connector_internal_management_standards.md)** - 连接器开发指南
- **[日志系统设计](docs/01_technical_design/logging_system/)** - 结构化日志和监控
- **[API契约设计](docs/01_technical_design/api_contract_design.md)** - RESTful API接口规范

### 📋 重要决策
- **[架构迁移决策](docs/02_decisions/flutter_migration_decision_record.md)** - Kotlin → Python + Flutter迁移完成
- **[硬件扩展决策](docs/02_decisions/hardware_extension_decision_record.md)** - 硬件支持已决策推迟

## 🧪 测试和验证

### 启动验证
```bash
# 检查daemon健康状态
curl http://localhost:58471/

# 验证连接器列表
curl http://localhost:58471/api/v1/connectors/

# 测试连接器启动
curl -X POST http://localhost:58471/api/v1/connectors/filesystem/start
```

### 开发流程
1. 启动开发环境: `./dev.sh`
2. 验证基础功能: `python test_connector_management.py`
3. 开发新功能
4. 测试端到端流程
5. 提交变更

## 🤝 贡献指南

### 开发准备
1. Fork 本项目
2. 安装依赖: `poetry install` (在daemon和connectors目录)
3. 启动开发环境: `./dev.sh`
4. 运行测试: `python test_connector_management.py`

### 提交流程
1. 创建特性分支: `git checkout -b feature/AmazingFeature`
2. 开发和测试
3. 提交更改: `git commit -m 'Add some AmazingFeature'`
4. 推送分支: `git push origin feature/AmazingFeature`
5. 创建 Pull Request

## 📄 许可证

本项目采用 [MIT](LICENSE) 许可证

---

**Linch Mind - Flutter + Python 架构** 🚀  
*真正的个人AI生活助手，连接你的数字生活*

*最后更新: 2025-08-03 | Session V62+ - Python + Flutter架构稳定运行*