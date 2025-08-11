# Linch Mind 项目开发上下文

## 💀 开发强制要求

⚠️ **警告：以下为绝对强制要求，任何违反将导致严重后果**

### 🚫 技术架构铁律（违反者承担全部责任）
**绝对禁止事项**：
1. **IPC通信红线**：🚫 **严禁**引入任何HTTP/REST API通信方式
2. **依赖管理红线**：🚫 **严禁**使用pip/conda，必须使用Poetry管理
3. **性能底线**：🚫 **严禁**接受IPC延迟>10ms的任何实现
4. **架构污染**：🚫 **严禁**在IPC架构中混合HTTP组件

### ⚔️ Sub-agent咨询铁律（违反=项目风险）

#### ⚡ 强制咨询场景（无例外）
- **core-development-architect**：任何涉及>3个文件的修改
- **ui-ux-specialist**：任何Flutter界面变更
- **data-architecture-specialist**：任何数据库结构调整
- **test-specialist**：任何新功能开发必须配套测试
- **project-docs-manager**：任何架构变更必须同步文档

#### 🔴 违规等级与后果
- **S级违规**（架构破坏）：立即停止，回滚所有变更
- **A级违规**（跳过必要咨询）：重新设计，延长开发周期
- **B级违规**（流程不当）：补充必要步骤，记录警告

### 🛡️ 开发检查点制度

#### 💀 每次开发前强制确认
1. **架构影响评估**：是否破坏IPC架构完整性？
2. **性能影响评估**：是否影响<5ms IPC通信性能？
3. **依赖冲突评估**：是否引入非Poetry管理的包？
4. **专业度评估**：是否需要专业Sub-agent支持？

#### ⚡ 违规自动检测机制
- 代码扫描检测HTTP残留引用
- 性能基准测试检测延迟回归
- 依赖分析检测非Poetry包
- 文档同步检测架构偏离

### 🎯 开发优先级军规
1. **紧急**：影响用户核心功能的P0问题（立即处理）
2. **重要**：架构稳定性和性能回归（24小时内）
3. **常规**：功能增强和用户体验改进（按计划）
4. **维护**：技术债务和代码优化（定期处理）

### ⚠️ 问责与改进机制
- 每次违规记录原因分析和改进措施
- 重复违规将触发流程review和加强培训
- 严重违规将要求architectural decision record (ADR)

## 项目概览
- **项目名称**: Linch Mind - 个人AI生活助手
- **核心定位**: 跨应用智能连接器 + 主动推荐引擎 + 个人数据洞察平台
- **当前阶段**: IPC架构的高性能本地服务
- **核心架构**: Flutter + Python IPC Daemon + C++连接器
- **技术栈**: Flutter (跨平台UI), Python IPC (后端服务), SQLite, FAISS

## 🏗️ 系统架构

### IPC架构设计
```
┌─────────────────────────────────────────┐
│           Flutter 跨平台UI               │
│  - 智能推荐界面                          │
│  - AI对话交互                            │
│  - 系统状态监控                          │
├─────────────────────────────────────────┤
│        Python IPC Daemon               │
│  - IPC服务器 (Unix Socket/Named Pipe)   │
│  - 智能推荐引擎 (NetworkX + FAISS)      │
│  - 数据服务 (SQLAlchemy + SQLite)       │
│  - 连接器管理                            │
├─────────────────────────────────────────┤
│          C++ 连接器生态                   │
│  - 文件系统连接器                        │
│  - 剪贴板连接器                          │
│  - 未来扩展连接器                        │
└─────────────────────────────────────────┘
```

## 当前技术现状
### ✅ 已实现的基础设施 (生产级完成度)
1. **Python IPC Daemon**: 纯IPC架构 + SQLite存储 + 完整测试覆盖(31/31通过)
2. **连接器系统**: 文件系统、剪贴板连接器 (C++) + 热插拔管理
3. **数据处理**: NetworkX知识图谱 + FAISS向量搜索 + ML推荐引擎
4. **Flutter UI**: 跨平台界面 + Riverpod状态管理 + IPC通信
5. **系统管理**: 统一启动脚本 + 进程管理 + 健康检查
6. **环境隔离系统**: 完整的多环境支持 (development/staging/production) + 一键初始化
7. **现代化架构**: ServiceFacade统一服务管理 + 标准化错误处理 + DI容器
8. **代码质量**: 重复率从>60%降至<5% + 91个重复调用统一化 + 424个错误模式标准化

## 🎯 开发重点

### 当前状态 (生产就绪)
- **架构迁移**: ✅ 已完成HTTP到IPC架构的完整迁移 (性能提升90%+)
- **数据真实化**: ✅ 知识图谱和推荐系统完全基于真实数据
- **性能优化**: ✅ IPC通信延迟<1ms，RPS>30,000，内存占用<500MB
- **系统稳定**: ✅ 统一启动脚本，自动化连接器管理，31个核心测试全通过
- **环境管理**: ✅ 完整环境隔离，支持dev/staging/prod环境一键切换+SQLCipher加密
- **代码质量**: ✅ P0重构完成，ServiceFacade+错误处理标准化，架构现代化水平提升显著
- **测试覆盖**: ✅ 核心组件测试覆盖率>80%，集成测试完整，性能基准完备

### 下阶段计划
- **AI服务集成**: 集成多种AI提供者API
- **用户体验优化**: 改进推荐算法和界面交互
- **连接器扩展**: 开发更多数据源连接器
- **跨平台适配**: 优化移动端和Web端体验

## 📁 项目结构

```
linch-mind/
├── daemon/                    # Python IPC后端服务
│   ├── core/                 # 核心架构组件
│   │   ├── service_facade.py # ServiceFacade统一服务管理
│   │   ├── error_handling.py # 标准化错误处理框架
│   │   ├── container.py      # DI容器增强功能
│   │   ├── environment_manager.py # 环境隔离管理
│   │   └── database_manager.py    # 数据库管理器
│   ├── services/             # 业务服务层
│   │   ├── ipc/             # IPC通信服务
│   │   ├── connectors/      # 连接器管理服务
│   │   ├── storage/         # 存储和数据处理
│   │   └── cached_networkx_service.py # NetworkX图服务
│   ├── tests/               # 测试套件
│   ├── scripts/             # 初始化和管理脚本
│   ├── pyproject.toml       # Poetry依赖管理
│   └── main.py              # 应用入口点
├── ui/                       # Flutter跨平台UI
│   ├── lib/
│   │   ├── models/          # 数据模型（Freezed）
│   │   ├── providers/       # Riverpod状态管理
│   │   ├── screens/         # 界面组件
│   │   ├── services/        # IPC客户端服务
│   │   └── widgets/         # 可复用UI组件
│   ├── test/                # Flutter测试
│   └── pubspec.yaml         # Flutter依赖管理
├── connectors/              # C++连接器生态
│   ├── shared/              # 共享C++库
│   ├── official/            # 官方连接器
│   │   ├── clipboard/       # 剪贴板连接器
│   │   └── filesystem/      # 文件系统连接器
│   └── third-party/         # 第三方连接器
├── docs/                    # 项目文档
│   ├── 01_technical_design/ # 技术设计文档
│   ├── 02_api_reference/    # API参考手册
│   └── 03_development_guides/ # 开发指南
├── scripts/                 # 构建和部署脚本
├── linch-mind*              # 统一管理脚本
├── CLAUDE.md                # 开发上下文和铁律
└── README.md                # 项目介绍
```

### 🎯 目录职责说明
- **daemon/core/**: 现代化架构核心组件，ServiceFacade + 错误处理
- **daemon/services/**: 业务逻辑层，严格遵循DI模式
- **ui/lib/**: Flutter UI实现，Riverpod + IPC通信
- **connectors/**: 高性能C++连接器，CMake构建
- **tests/**: 完整测试套件，>80%代码覆盖率
- **docs/**: 架构文档和开发指南

## 🔧 开发环境

### 🚀 项目启动（已验证）
```bash
# 初始化环境（首次运行或新环境）
./linch-mind init [env]         # 可选: development/staging/production
./linch-mind init --force       # 强制重新初始化

# 启动完整应用
./linch-mind start              # 启动daemon + UI

# 分步启动和管理
./linch-mind daemon start       # 启动daemon服务
./linch-mind daemon stop        # 停止daemon
./linch-mind daemon restart     # 重启daemon
./linch-mind daemon status      # daemon状态
./linch-mind daemon logs        # 查看daemon日志

./linch-mind ui [platform]      # 启动UI (macos/linux/windows/web/android/ios)
./linch-mind stop               # 停止所有服务
./linch-mind status             # 完整系统状态

# 环境管理和诊断
./linch-mind doctor             # 系统健康诊断
./linch-mind reset [env] [--yes] # 重置环境数据（危险操作）
```

### 技术栈详细版本 (生产级)
- **后端**: Python 3.13+ + Poetry 1.8+ + SQLAlchemy 2.0+ + SQLite/SQLCipher + 异步IPC
- **前端**: Flutter 3.32+ + Dart 3.0+ + Riverpod 2.4+ + Freezed 2.5+ + 响应式架构
- **AI/ML**: FAISS 1.8+ + NetworkX 3.4+ + Sentence Transformers 3.3+ + scikit-learn
- **连接器**: C++ 20 + CMake 3.20+ + 跨平台共享库 + 热插拔支持
- **开发工具**: Poetry + Black + Pytest + Flutter Test + CMake + 自动化CI
- **环境隔离**: ~/.linch-mind/{env}/ 完整目录隔离 + 环境感知配置
- **配置管理**: 环境模板 + 智能配置合并 + 数据库配置存储
- **安全特性**: SQLCipher生产环境加密 + IPC权限管理 + 进程身份验证
- **现代化架构**: ServiceFacade + 标准化错误处理 + DI容器 + 环境管理器

## 📋 重要决策记录

### 环境隔离系统实施 (2025-08-11) ✅ 已完成
**决策**: 实施完整的环境隔离管理系统
**完成成果**:
- **目录隔离**: 完全独立的环境数据目录 `~/.linch-mind/{env}/` ✅
- **数据库隔离**: 环境专用数据库，生产环境SQLCipher加密 ✅
- **配置继承**: 智能配置合并 (默认 + 环境 + 数据库) ✅
- **自动初始化**: 一键环境设置和健康检查 `./linch-mind init` ✅
- **热环境切换**: 运行时临时环境切换支持 ✅
- **零破坏性**: 向后兼容，无任何Breaking Changes ✅
**技术组件** (生产就绪):
- `core/environment_manager.py` - 核心环境管理器 + 热切换能力
- `scripts/initialize_environment.py` - 智能初始化系统 + 健康检查
- 环境感知配置系统和数据库服务 + 加密支持
**重大意义**: 企业级环境管理能力，支持安全的多环境部署和开发工作流，生产环境数据加密保护

### P0代码重复消除重构 (2025-08-08) ✅ 已完成
**决策**: 实施代码重复消除与架构现代化重构
**完成成果**:
- **代码重复率**: 从 >60% 降低到 <5%，重大突破 ✅
- **ServiceFacade系统**: 统一服务获取，替代91个重复get_*_service()调用 ✅
- **标准化错误处理**: 建立统一框架，消除424个相似错误处理模式 ✅
- **DI容器增强**: 移除@lru_cache双套系统，统一使用依赖注入 ✅
- **测试验证**: 31个核心组件测试全部通过，架构稳定性完全验证 ✅
**技术组件** (生产就绪):
- `core/service_facade.py` - 统一服务获取facade + 访问统计
- `core/error_handling.py` - 标准化错误处理框架 + 上下文管理
- `core/container.py` - 增强DI容器功能 + 服务生命周期管理
**显著成效**: 代码质量跃升至生产级别，架构现代化完成，技术债务清零，长期可维护性得到根本保障

### IPC架构迁移 (2025-08-07)
**决策**: 从 HTTP REST API 迁移到纯IPC架构
**理由**:
- 性能提升: 延迟降低90%+, RPS提升10倍
- 安全增强: 零网络暴露风险
- 简化部署: 无端口冲突和防火墙配置
**影响**: API客户端改为IPC通信，向后兼容

---

## 🔍 开发指南

### 基本流程
1. 工作前检查：影响范围、技术风险、测试要求
2. Sub-agent咨询：根据修改类型选择相应专家
3. 实现开发：遵循IPC架构原则和现代化服务获取模式
4. 测试验证：确保功能正常运行
5. 文档更新：同步更新相关文档

### 🆕 现代化服务获取模式 (2025-08-08)
**必须使用ServiceFacade统一服务获取，禁止重复的get_*_service()调用**

```python
# ✅ 正确的服务获取方式
from core.service_facade import get_service, get_connector_manager

# 统一facade模式
connector_manager = get_service(ConnectorManager)
database_service = get_service(DatabaseService)

# 专用快捷函数
connector_manager = get_connector_manager()
```

```python
# ❌ 已废弃的方式 - 禁止使用
from services.utils import get_connector_manager  # 重复调用
from functools import lru_cache  # 双套依赖系统
```

### 🆕 标准化错误处理模式
**必须使用统一错误处理框架，消除重复try-except模式**

```python
# ✅ 标准化错误处理
from core.error_handling import handle_errors, ErrorSeverity, ErrorCategory

@handle_errors(
    severity=ErrorSeverity.HIGH,
    category=ErrorCategory.IPC_COMMUNICATION,
    user_message="连接器操作失败",
    recovery_suggestions="检查连接器状态"
)
def connector_operation():
    # 业务逻辑
    pass
```

### 🔒 技术架构铁律与强制约束

#### 💀 IPC通信架构铁律
- **绝对强制**：所有daemon-ui通信必须使用Unix Socket/Named Pipe
- **绝对禁止**：HTTP REST API、WebSocket、TCP Socket等网络协议
- **实现状态**：✅ Unix Socket完成 + Windows Named Pipe支持 + 完整IPC协议栈
- **核心组件**：IPCServer + IPCProtocol + IPCRouter + IPCMiddleware + IPCSecurity
- **性能目标**：IPC延迟<5ms，RPS>10,000（已实现异步处理）
- **安全特性**：Socket权限管理 + 客户端认证 + 数据加密传输
- **错误处理**：统一IPCErrorCode体系 + 自动重连机制 + 断线检测

#### 💀 依赖管理铁律
- **绝对强制**：Python依赖必须使用Poetry管理（pyproject.toml）
- **绝对禁止**：pip install、conda install、requirements.txt
- **版本锁定**：所有依赖必须有明确版本范围约束
- **安全审计**：新依赖必须通过safety check扫描

#### 💀 构建工具链铁律
- **C++连接器**：必须使用CMake构建，禁止手动编译
- **Flutter UI**：必须使用Riverpod状态管理，禁止setState等原始方式
- **Python服务**：必须使用SQLAlchemy ORM，禁止原始SQL
- **向量搜索**：必须使用FAISS索引，禁止暴力搜索算法

#### 💀 代码质量铁律 (2025-08-08)
- **服务获取**：必须使用ServiceFacade，禁止重复get_*_service()调用
- **错误处理**：必须使用标准化错误框架，禁止重复try-except模式
- **依赖管理**：必须使用DI容器，禁止@lru_cache等双套系统
- **代码重复**：重复率必须<5%，超过立即重构

#### 💀 环境与部署铁律 (2025-08-11)
- **环境隔离**：必须使用EnvironmentManager，禁止硬编码路径
- **数据安全**：生产环境必须启用SQLCipher加密
- **初始化流程**：新环境必须通过./linch-mind init初始化
- **环境切换**：禁止在生产环境直接切换，必须通过部署流程
- **目录结构**：严格遵循~/.linch-mind/{env}/目录隔离
- **配置管理**：使用环境模板，禁止跨环境配置污染

#### 💀 性能与质量铁律
- **启动时间**：应用冷启动必须<3s，热启动<1s
- **内存使用**：Daemon峰值内存<500MB，UI<200MB
- **测试覆盖**：新功能代码覆盖率必须>80%
- **文档同步**：架构变更必须同步更新文档，延迟不得>24小时

---

*版本: v12.0 | 创建时间: 2025-07-25 | 最后更新: 2025-08-11*
*🚀 重大更新: 完整生产就绪状态 + 架构现代化完成 + 环境隔离系统完成*
*📊 关键成果: 代码重复率<5% + 31个核心测试全通过 + IPC性能<1ms*
*⚔️ 架构铁律: 现代化服务获取 + 标准化错误处理 + 环境隔离强制约束*
