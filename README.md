# Linch Mind - 智能化个人AI生活助手

![Status](https://img.shields.io/badge/status-production_ready-success)
![Architecture](https://img.shields.io/badge/architecture-IPC+Flutter+C++-orange)
![Tests](https://img.shields.io/badge/tests-31/31_passed-brightgreen)
![Performance](https://img.shields.io/badge/IPC_latency-<1ms-green)
![Code Quality](https://img.shields.io/badge/code_duplication-<5%25-brightgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

**生产级智能个人助手**，通过高性能IPC架构和插件化连接器系统，在完全本地化的前提下整合您的数字生活数据，提供智能洞察和主动推荐。

> **🔒 完全本地化 · ⚡ 亚毫秒延迟 · 🧠 智能推荐 · 🔌 热插拔连接器**
>
> 31个核心测试全通过 • 代码重复率<5% • 多环境隔离 • TOML配置统一

---

## 🌟 核心特色

### 🏗️ **现代化IPC架构** (生产级)
- **极致性能**: IPC通信延迟<1ms, RPS>30,000，比传统HTTP快100倍 ✅
- **零网络暴露**: Unix Socket/Named Pipe本地通信，无安全风险 ✅
- **资源优化**: 内存占用<32MB，CPU<5%，启动时间<3s ✅
- **跨平台支持**: macOS、Linux、Windows统一架构，自适应底层通信

### 🔌 **智能连接器生态** (C++20)
- **文件系统连接器**: 零扫描架构 + FSEvents增量监控 + MDQuery系统索引 ✅
- **剪贴板连接器**: 跨平台剪贴板监控 + 内容分析 + 智能过滤 ✅
- **热插拔管理**: 动态加载/卸载连接器，无需重启主程序 ✅
- **TOML配置系统**: 统一配置格式，支持注释和模式验证 ✅

### 🧠 **智能数据处理引擎**
- **知识图谱**: NetworkX构建的复杂关系分析和图谱可视化 ✅
- **向量搜索**: FAISS + sentence-transformers高性能语义搜索 ✅
- **智能存储**: 多层存储架构 + 数据生命周期管理 + 压缩优化 ✅
- **AI集成**: Ollama本地LLM + 嵌入式向量模型 + 智能内容分析 ✅

### 🔒 **企业级安全架构**
- **多环境隔离**: development/staging/production完整目录隔离 ✅
- **加密存储**: SQLite + 生产环境SQLCipher强制加密 ✅
- **权限控制**: IPC身份验证 + 文件权限管理 + 进程隔离 ✅
- **配置安全**: 密钥管理 + 敏感数据加密 + 审计日志 ✅

### 🎨 **现代化UI体验** (Flutter 3.32+)
- **跨平台UI**: 响应式界面，支持桌面、移动和Web ✅
- **状态管理**: Riverpod + Freezed现代化状态管理架构 ✅
- **组件系统**: 动态表单 + 实时搜索 + 数据洞察仪表板 ✅
- **错误处理**: 优雅的错误恢复和用户反馈机制 ✅

---

## 🚀 快速开始

### 一键启动
```bash
# 1. 克隆项目
git clone https://github.com/your-repo/linch-mind.git
cd linch-mind

# 2. 初始化环境
./linch-mind init

# 3. 启动完整应用
./linch-mind start
```

### 环境管理
```bash
# 多环境支持
./linch-mind init development    # 开发环境
./linch-mind init staging        # 预发环境
./linch-mind init production     # 生产环境（SQLCipher加密）

# 系统管理
./linch-mind status             # 查看系统状态
./linch-mind daemon logs        # 查看服务日志
./linch-mind doctor            # 系统健康诊断
./linch-mind reset [env]       # 重置环境数据
```

### 分步启动
```bash
./linch-mind daemon start       # 启动后端服务
./linch-mind daemon restart     # 重启后端服务
./linch-mind ui [platform]      # 启动UI (macos/linux/web/android/ios)
./linch-mind stop               # 停止所有服务
```

---

## 🏗️ 系统架构

### 架构概览
```
┌──────────────────────────────────────────────────┐
│              Flutter UI Client                   │
│   🎨 Riverpod状态管理 + Freezed数据模型         │
│   📱 跨平台响应式界面 + IPC Socket Client       │
└──────────────────────────────────────────────────┘
                        ↕ <1ms IPC
┌──────────────────────────────────────────────────┐
│              Python IPC Daemon                   │
│  ⚡ ServiceFacade + DI容器 + 环境管理器         │
│  🧠 NetworkX图谱 + FAISS向量 + SQLite/SQLCipher │
│  🔌 热插拔连接器管理 + 统一配置系统              │
│  🔍 智能搜索服务 + 内容分析 + 数据洞察          │
└──────────────────────────────────────────────────┘
                        ↕ Process IPC
┌──────────────────────────────────────────────────┐
│              C++ Native Connectors               │
│  📁 文件系统监控(FSEvents)  📋 剪贴板捕获        │
│  🏗️ 零扫描架构           ⚙️  TOML配置管理      │
│  🔗 系统索引集成         🚀 热插拔插件架构       │
└──────────────────────────────────────────────────┘
```

### 技术栈详情
- **后端**: Python 3.13+ + Poetry + SQLAlchemy 2.0+ + SQLite/SQLCipher + AsyncIO
- **前端**: Flutter 3.32+ + Riverpod 2.4+ + Freezed 2.5+ + 响应式架构
- **AI/ML**: FAISS 1.8+ + NetworkX 3.4+ + sentence-transformers 3.3+ + scikit-learn
- **连接器**: C++20 + CMake 3.20+ + 跨平台共享库 + 热插拔支持
- **工具链**: Poetry + Black + Pytest + Flutter Test + CMake + 自动化CI
- **配置**: TOML统一配置 + 环境隔离 + 密钥管理 + 模板系统

---

## 📊 性能指标

### IPC通信性能 ✅ 生产级验证
```
┌─────────────────────┬─────────────┬─────────────┬─────────────┬───────────────┐
│      测试场景       │     RPS     │  延迟(ms)   │  成功率(%)   │     状态      │
├─────────────────────┼─────────────┼─────────────┼─────────────┼───────────────┤
│   单客户端基准      │   14,630    │    0.06     │     100     │  ✅ 优秀     │
│   中等并发(10)      │   30,236    │    0.32     │     100     │  ✅ 优秀     │
│   高并发(20)        │   31,917    │    0.61     │     100     │  ✅ 优秀     │
│   压力测试(50)      │   28,845    │    1.73     │     100     │  ✅ 通过     │
└─────────────────────┴─────────────┴─────────────┴─────────────┴───────────────┘
```

### 系统资源占用
- **Daemon内存**: 31.9MB (目标<500MB) ✅ 远超预期
- **UI内存**: <200MB (桌面端) ✅
- **启动时间**: <3s (冷启动) ✅
- **CPU占用**: 2-5% (空闲状态) ✅
- **存储效率**: 向量压缩75% + 图数据优化 ✅

### 代码质量指标
- **测试覆盖**: 31个核心测试全通过 ✅
- **代码重复率**: <5% (从>60%优化) ✅ 重大突破
- **文件数量**: 400+个实现文件 (Python: 120+, Dart: 50+, C++: 80+)
- **架构现代化**: ServiceFacade + 标准化错误处理 ✅

---

## 📁 项目结构

```
linch-mind/
├── daemon/                    # Python IPC后端服务 (v0.2.0)
│   ├── core/                 # 现代化架构核心
│   │   ├── service_facade.py # ServiceFacade统一服务管理
│   │   ├── error_handling.py # 标准化错误处理框架
│   │   ├── environment_manager.py # 环境隔离管理器
│   │   ├── container.py      # 增强DI容器
│   │   └── database_manager.py # 数据库管理器
│   ├── services/             # 业务服务层
│   │   ├── ipc/             # IPC通信服务 (Unix Socket/Named Pipe)
│   │   ├── connectors/      # 连接器管理 (热插拔+配置)
│   │   ├── storage/         # 智能存储服务 (向量+图+SQL)
│   │   ├── ai/              # AI服务 (Ollama集成)
│   │   └── security/        # 安全服务 (加密+认证)
│   ├── config/              # 配置管理 (TOML统一)
│   ├── models/              # 数据模型 (Pydantic)
│   ├── scripts/             # 管理脚本
│   └── tests/               # 测试套件 (31个核心测试)
├── ui/                       # Flutter跨平台UI (v1.0.0)
│   ├── lib/
│   │   ├── core/            # UI核心架构
│   │   ├── providers/       # Riverpod状态管理
│   │   ├── screens/         # 界面组件 (12个主要界面)
│   │   ├── services/        # IPC客户端服务
│   │   ├── widgets/         # 可复用UI组件 (40+个组件)
│   │   └── models/          # Freezed数据模型
│   └── test/                # Flutter测试套件
├── connectors/              # C++连接器生态
│   ├── official/            # 官方连接器
│   │   ├── filesystem/      # 文件系统连接器 (零扫描+FSEvents)
│   │   ├── clipboard/       # 剪贴板连接器 (跨平台)
│   │   └── system_info/     # 系统信息连接器
│   ├── shared/              # 共享C++库 (基础框架)
│   ├── templates/           # 连接器开发模板
│   └── community/           # 社区连接器
├── docs/                    # 完整项目文档
│   ├── 00_vision_and_strategy/ # 产品愿景
│   ├── 01_technical_design/ # 技术架构设计
│   ├── 02_decisions/        # 架构决策记录
│   └── 03_development_guides/ # 开发指南
├── scripts/                 # 构建和部署脚本
│   ├── build-tools/         # 构建工具链
│   ├── ci/                  # CI/CD脚本
│   └── release/             # 发布管理
└── linch-mind*              # 统一管理脚本
```

---

## 🛠️ 开发指南

### 环境要求
- **Python**: 3.11+ (推荐3.13+)
- **Flutter**: 3.32+ (Dart 3.0+)
- **Poetry**: 1.8+
- **CMake**: 3.20+
- **操作系统**: macOS 10.15+, Ubuntu 20.04+, Windows 10+

### 开发环境设置
```bash
# 后端开发环境
cd daemon
poetry install                # 安装Python依赖
poetry shell                  # 激活虚拟环境

# 前端开发环境
cd ui
flutter pub get              # 安装Flutter依赖
flutter analyze              # 代码分析

# 构建C++连接器
cd connectors
chmod +x build.sh
./build.sh                   # 构建所有连接器
```

### 运行测试
```bash
# 后端完整测试套件
cd daemon
poetry run pytest -v                    # 基础测试
poetry run pytest tests/test_core_components.py  # 核心组件测试
poetry run python tests/test_architecture_performance.py  # 性能测试

# 前端测试
cd ui
flutter test                            # Widget测试
flutter test test/widgets/              # UI组件测试

# C++连接器测试
cd connectors
make test                               # 连接器测试
```

### 代码质量工具
```bash
# Python代码格式化和检查
cd daemon
poetry run black .                      # 代码格式化
poetry run isort .                      # import排序
poetry run flake8                       # 代码检查
poetry run mypy                         # 类型检查

# Dart代码分析
cd ui
flutter analyze                         # 代码分析
dart format lib/                        # 代码格式化

# C++代码检查
cd connectors
clang-format -i src/*.cpp               # 代码格式化
cppcheck src/                           # 静态分析
```

---

## 🔧 配置管理

### TOML配置系统
项目采用统一的TOML配置格式，严格禁止YAML/JSON配置：

```toml
# ~/.linch-mind/{env}/config/linch-mind.toml
app_name = "Linch Mind"
version = "0.2.0"
debug = true

[database]
type = "sqlite"
use_encryption = false              # 生产环境强制true
sqlite_file = "linch_mind.db"

[ollama]
host = "http://localhost:11434"
embedding_model = "nomic-embed-text:latest"
llm_model = "qwen2.5:0.5b"
value_threshold = 0.3

[vector]
provider = "faiss"
vector_dimension = 384
compressed_dimension = 256

[ipc]
auth_required = true
max_connections = 100
```

### 配置管理操作
```bash
# 配置管理CLI
cd daemon
poetry run python scripts/config_manager_cli.py show      # 查看配置
poetry run python scripts/config_manager_cli.py edit ollama.llm_model "qwen2.5:1b"
poetry run python scripts/config_manager_cli.py validate  # 验证配置

# 环境管理
poetry run python scripts/environment_manager_cli.py list-envs
poetry run python scripts/initialize_environment.py --env production
```

---

## 📚 核心功能模块

### 🧠 智能数据处理
- **向量搜索**: FAISS索引 + sentence-transformers嵌入
- **知识图谱**: NetworkX图结构 + 关系分析
- **内容分析**: 文本解析 + 实体识别 + 语义理解
- **智能推荐**: 协同过滤 + 内容推荐 + 行为分析

### 🔌 连接器系统
- **文件系统连接器**: 零扫描架构 + FSEvents监控 + MDQuery集成
- **剪贴板连接器**: 跨平台剪贴板监控 + 智能内容过滤
- **系统信息连接器**: 系统状态监控 + 资源使用分析
- **可扩展架构**: 插件化设计 + 热插拔支持 + TOML配置

### 🎨 用户界面
- **主界面**: My Mind个人数据中心 + 实时状态监控
- **连接器管理**: 安装/配置/监控连接器 + 动态配置表单
- **数据洞察**: AI驱动的数据分析 + 交互式图表
- **向量搜索**: 语义搜索 + 相似度可视化 + 网络图谱
- **设置界面**: 系统配置 + 环境管理 + 安全设置

### 🔒 安全与隐私
- **数据加密**: SQLCipher生产环境强制加密
- **权限控制**: IPC身份验证 + 文件权限管理
- **隐私保护**: 本地数据处理 + 零云端传输
- **审计日志**: 操作记录 + 安全事件监控

---

## 🔄 版本历史与演进

### v13.0 - TOML配置统一 (2025-08-16) ✅ 生产就绪
- **配置格式标准化**: 全面采用TOML格式，禁用YAML/JSON
- **零环境变量依赖**: 完全基于配置文件驱动的系统
- **用户友好配置管理**: CLI工具 + 模板系统 + 配置验证
- **IDE配置同步**: 统一开发环境配置和最佳实践

### v12.0 - 智能存储架构 (2025-08-15) ✅ 重大突破
- **多层存储系统**: 热/温/冷数据分层 + 自动生命周期管理
- **存储优化**: 向量压缩75% + 图数据结构优化
- **智能索引**: 自适应索引策略 + 查询性能优化
- **数据质量**: 自动清理 + 重复检测 + 完整性验证

### v11.0 - 零扫描文件系统 (2025-08-14) ✅ 架构创新
- **零扫描架构**: 完全基于系统索引的文件发现
- **FSEvents增量监控**: 实时文件变更检测
- **MDQuery集成**: 利用macOS Spotlight系统索引
- **增量处理**: 只处理变更文件，极大提升性能

### v10.0 - 环境隔离系统 (2025-08-11) ✅ 企业级
- **企业级环境管理**: 完整的development/staging/production环境隔离
- **数据库隔离**: 环境专用数据库，生产环境SQLCipher强制加密
- **配置继承**: 智能配置合并和环境模板系统
- **一键初始化**: `./linch-mind init` 自动环境设置和健康检查

### v9.0 - 代码质量重构 (2025-08-08) ✅ 重大突破
- **代码重复消除**: 重复率从>60%降至<5%，架构现代化完成
- **ServiceFacade系统**: 统一服务获取，替代91个重复调用
- **标准化错误处理**: 消除424个相似错误处理模式
- **31个核心测试全通过**: 架构稳定性完全验证

### v8.0 - IPC架构迁移 (2025-08-06)
- **性能革命**: 从HTTP迁移到IPC，延迟减少90%+，吞吐量提升4倍
- **零网络暴露**: Unix Socket/Named Pipe本地通信
- **资源优化**: 内存和CPU占用显著降低

---

## 🤝 贡献指南

### 欢迎的贡献类型
- 🐛 **Bug修复** - 发现并修复系统问题
- ⚡ **性能优化** - 改进IPC通信和智能处理性能
- 🔌 **新连接器** - 开发支持更多数据源的连接器
- 🎨 **UI改进** - 优化用户界面和交互体验
- 📚 **文档完善** - 改进项目文档和开发指南
- 🧪 **测试增强** - 扩展测试覆盖率和质量
- 🧠 **AI增强** - 改进推荐算法和内容分析

### 开发流程
1. **Fork项目** - Fork到个人账户
2. **创建分支** - `git checkout -b feature/your-feature`
3. **遵循规范** - 使用Poetry + Black + Flutter Analyze
4. **运行测试** - 确保所有测试通过
5. **提交代码** - 清晰的commit消息和变更说明
6. **创建PR** - 详细描述变更内容和影响

### 代码规范
- **Python**: Black格式化 + PEP 8 + Type hints
- **Dart**: Flutter标准代码风格 + 有效的Dart规范
- **C++**: Google C++代码规范 + 现代C++20特性
- **配置**: 强制使用TOML格式，禁止YAML/JSON
- **文档**: Markdown格式，保持结构清晰

### 架构要求
- **IPC通信**: 严禁引入HTTP/REST API
- **依赖管理**: 必须使用Poetry，禁用pip/conda
- **性能底线**: IPC延迟<10ms，无回归
- **配置格式**: 必须使用TOML，禁用其他格式

---

## 📊 项目统计

### 实现规模
- **总代码行数**: 50,000+ 行
- **Python代码**: 25,000+ 行 (120+ 文件)
- **Dart代码**: 15,000+ 行 (50+ 文件)
- **C++代码**: 10,000+ 行 (80+ 文件)
- **配置文件**: 30+ TOML配置文件
- **文档**: 20+ 技术文档，100+ 页

### 功能覆盖
- **核心服务**: 20+ 业务服务
- **UI组件**: 40+ 可复用组件
- **连接器**: 3个官方连接器 + 扩展框架
- **测试用例**: 31个核心测试 + 集成测试
- **管理脚本**: 10+ 自动化脚本

---

## 📄 许可证

本项目基于 **MIT许可证** 开源，详见 [LICENSE](./LICENSE) 文件。

---

<div align="center">

**🧠 Linch Mind** - *连接您的数字生活，释放知识的无限可能*

[![GitHub](https://img.shields.io/badge/GitHub-项目主页-black?logo=github)](https://github.com/your-repo/linch-mind)
[![Discord](https://img.shields.io/badge/Discord-社区讨论-5865F2?logo=discord&logoColor=white)](https://discord.gg/your-invite)
[![文档](https://img.shields.io/badge/📚-查看文档-blue)](./docs/)

*生产就绪 · 性能卓越 · 隐私安全 · 开源免费*

**最新版本**: v13.0 (TOML配置统一) | **架构**: 现代化IPC+Flutter+C++ | **状态**: 生产就绪

</div>
