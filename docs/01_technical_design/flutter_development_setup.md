# Flutter开发环境配置指南

**版本**: 1.0  
**状态**: 设计中  
**创建时间**: 2025-08-02  
**适用于**: Flutter迁移后的完整开发环境

## 1. 概述

本指南详细说明如何配置Linch Mind Flutter版本的完整开发环境，包括Flutter应用开发、Dart Daemon开发和多语言连接器插件开发环境。

### 1.1 技术栈总览
- **主应用**: Flutter + Dart
- **后台服务**: Dart HTTP Server (shelf)
- **连接器插件**: 多语言支持 (Python/Node.js/Rust/Go/等)
- **数据库**: SQLite
- **状态管理**: Riverpod
- **构建工具**: Flutter SDK + Dart SDK

## 2. 核心开发环境配置

### 2.1 Flutter SDK安装
```bash
# macOS 安装 (推荐使用官方安装器)
curl -fsSL https://flutter.dev/setup/install/macos | bash

# 或使用 Homebrew
brew install --cask flutter

# Linux 安装
wget https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.13.0-stable.tar.xz
tar xf flutter_linux_3.13.0-stable.tar.xz
export PATH="$PATH:`pwd`/flutter/bin"

# Windows 安装 (使用官方安装器)
# 下载并运行 https://docs.flutter.dev/get-started/install/windows
```

### 2.2 开发环境验证
```bash
# 检查Flutter环境
flutter doctor

# 期望输出类似:
# ✓ Flutter (Channel stable, 3.13.0)
# ✓ Android toolchain (if needed)
# ✓ Xcode (macOS only)
# ✓ Chrome (for web development)
# ✓ Android Studio (optional)
# ✓ VS Code (recommended)
```

### 2.3 IDE配置

#### VS Code推荐配置
```json
// .vscode/settings.json
{
  "dart.flutterSdkPath": "/path/to/flutter",
  "dart.showInspectorNotificationsForWidgetErrors": false,
  "dart.previewFlutterUiGuides": true,
  "dart.previewFlutterUiGuidesCustomTracking": true,
  "editor.formatOnSave": true,
  "editor.rulers": [80],
  "files.exclude": {
    "**/.dart_tool": true,
    "**/build": true
  }
}
```

#### VS Code推荐插件
```json
// .vscode/extensions.json
{
  "recommendations": [
    "dart-code.dart-code",
    "dart-code.flutter",
    "alexisvt.flutter-snippets",
    "nash.awesome-flutter-snippets",
    "robert-brunhage.flutter-riverpod-snippets",
    "ms-vscode.vscode-json"
  ]
}
```

## 3. 项目结构和依赖配置

### 3.1 Flutter应用配置
```yaml
# pubspec.yaml
name: linch_mind
description: Privacy-first Personal AI Assistant powered by Flutter

environment:
  sdk: '>=3.0.0 <4.0.0'
  flutter: ">=3.10.0"

dependencies:
  flutter:
    sdk: flutter
  
  # 状态管理
  flutter_riverpod: ^2.4.9
  riverpod_annotation: ^2.3.3
  
  # 网络和API
  dio: ^5.4.0
  retrofit: ^4.0.3
  json_annotation: ^4.8.1
  
  # 数据持久化
  sqflite: ^2.3.0
  sqflite_common_ffi: ^2.3.0  # 桌面端支持
  shared_preferences: ^2.2.2
  
  # UI和导航
  go_router: ^12.1.3
  flutter_svg: ^2.0.9
  animations: ^2.0.8
  
  # 图表和可视化
  fl_chart: ^0.65.0
  flutter_graph_view: ^1.1.0
  
  # 文件系统和路径
  path_provider: ^2.1.1
  file_picker: ^6.1.1
  
  # 工具和实用
  freezed_annotation: ^2.4.1
  logger: ^2.0.2+1
  crypto: ^3.0.3
  uuid: ^4.2.1

dev_dependencies:
  flutter_test:
    sdk: flutter
  
  # 代码生成
  build_runner: ^2.4.7
  freezed: ^2.4.6
  json_serializable: ^6.7.1
  retrofit_generator: ^8.0.4
  riverpod_generator: ^2.3.9
  
  # 静态分析
  flutter_lints: ^3.0.1
  dart_code_metrics: ^5.7.6
  
  # 测试工具
  mockito: ^5.4.2
  integration_test:
    sdk: flutter

flutter:
  uses-material-design: true
  
  assets:
    - assets/images/
    - assets/icons/
    - assets/data/
  
  fonts:
    - family: Roboto
      fonts:
        - asset: assets/fonts/Roboto-Regular.ttf
        - asset: assets/fonts/Roboto-Bold.ttf
          weight: 700
```

### 3.2 项目目录结构
```
linch_mind/
├── lib/                          # Flutter应用主代码
│   ├── main.dart                 # 应用入口
│   ├── app.dart                  # 应用配置
│   ├── core/                     # 核心功能
│   │   ├── constants/
│   │   ├── errors/
│   │   ├── network/
│   │   └── utils/
│   ├── features/                 # 功能模块
│   │   ├── dashboard/
│   │   ├── knowledge_graph/
│   │   ├── connectors/
│   │   ├── ai_chat/
│   │   └── settings/
│   ├── shared/                   # 共享组件
│   │   ├── models/
│   │   ├── providers/
│   │   ├── services/
│   │   └── widgets/
│   └── generated/                # 自动生成代码
├── daemon/                       # Dart后台服务
│   ├── bin/
│   │   └── daemon.dart          # Daemon入口
│   ├── lib/
│   │   ├── api/                 # REST API路由
│   │   ├── core/                # 核心服务
│   │   ├── connectors/          # 连接器管理
│   │   ├── models/              # 数据模型
│   │   └── utils/               # 工具函数
│   └── pubspec.yaml            # Daemon依赖配置
├── connectors/                   # 连接器插件
│   ├── python/                  # Python连接器
│   │   ├── obsidian_connector/
│   │   └── email_connector/
│   ├── nodejs/                  # Node.js连接器
│   │   ├── slack_connector/
│   │   └── browser_connector/
│   ├── rust/                    # Rust连接器
│   │   └── system_monitor/
│   └── templates/               # 连接器模板
├── test/                        # 测试代码
├── integration_test/            # 集成测试
├── assets/                      # 资源文件
├── scripts/                     # 构建和部署脚本
└── docs/                        # 项目文档
```

## 4. Daemon开发环境配置

### 4.1 Daemon项目配置
```yaml
# daemon/pubspec.yaml
name: linch_mind_daemon
description: Linch Mind background service

environment:
  sdk: '>=3.0.0 <4.0.0'

dependencies:
  # HTTP服务器
  shelf: ^1.4.1
  shelf_router: ^1.1.4
  shelf_cors_headers: ^0.1.5
  shelf_static: ^1.1.2
  
  # 数据库
  sqlite3: ^2.4.0
  
  # 网络和序列化
  dio: ^5.4.0
  json_annotation: ^4.8.1
  
  # 系统和文件
  path: ^1.8.3
  io: ^1.0.4
  process: ^4.2.4
  
  # 配置和日志
  yaml: ^3.1.2
  logging: ^1.2.0
  
  # 实用工具
  uuid: ^4.2.1
  crypto: ^3.0.3

dev_dependencies:
  test: ^1.24.0
  build_runner: ^2.4.7
  json_serializable: ^6.7.1
  lints: ^2.1.1

executables:
  linch_mind_daemon: daemon
```

### 4.2 Daemon开发调试
```bash
# 进入daemon目录
cd daemon

# 安装依赖
dart pub get

# 开发模式运行
dart run bin/daemon.dart --dev --port 61424

# 构建可执行文件
dart compile exe bin/daemon.dart -o linch_mind_daemon

# 后台运行
./linch_mind_daemon --config ../config/daemon.yaml &
```

## 5. 多语言连接器开发环境

### 5.1 Python连接器环境
```bash
# 安装Python (推荐3.9+)
pyenv install 3.11.0
pyenv global 3.11.0

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# 安装连接器开发框架
pip install linch-mind-connector-sdk
```

#### Python连接器模板
```python
# connectors/python/template/main.py
from linch_mind_sdk import ConnectorBase, ConnectorConfig
import asyncio
import logging

class TemplateConnector(ConnectorBase):
    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.logger = logging.getLogger(self.name)
    
    async def initialize(self):
        """初始化连接器"""
        self.logger.info(f"Initializing {self.name}")
        # 初始化逻辑
    
    async def start_monitoring(self):
        """开始数据监控"""
        self.logger.info("Starting data monitoring")
        # 监控逻辑
    
    async def collect_data(self):
        """收集数据"""
        # 数据收集逻辑
        data_items = []
        return data_items
    
    async def handle_command(self, command):
        """处理Daemon命令"""
        # 命令处理逻辑
        pass

if __name__ == "__main__":
    # 从配置文件加载配置
    config = ConnectorConfig.from_file("config.json")
    
    # 创建连接器实例
    connector = TemplateConnector(config)
    
    # 运行连接器
    asyncio.run(connector.run())
```

### 5.2 Node.js连接器环境
```bash
# 安装Node.js (推荐18+)
nvm install 18
nvm use 18

# 全局安装连接器开发工具
npm install -g @linch-mind/connector-cli

# 创建新连接器项目
linch-connector create my-connector --language typescript
cd my-connector
npm install
```

#### Node.js连接器模板
```javascript
// connectors/nodejs/template/src/index.ts
import { ConnectorBase, ConnectorConfig, DataItem } from '@linch-mind/connector-sdk';
import express from 'express';

export class TemplateConnector extends ConnectorBase {
    private app: express.Application;
    private server?: any;
    
    constructor(config: ConnectorConfig) {
        super(config);
        this.app = express();
        this.setupRoutes();
    }
    
    private setupRoutes() {
        this.app.use(express.json());
        
        this.app.post('/command', async (req, res) => {
            try {
                const result = await this.handleCommand(req.body);
                res.json(result);
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });
        
        this.app.post('/query', async (req, res) => {
            try {
                const result = await this.handleQuery(req.body);
                res.json(result);
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });
        
        this.app.get('/health', (req, res) => {
            res.json({ status: 'healthy', timestamp: Date.now() });
        });
    }
    
    async initialize(): Promise<void> {
        this.logger.info(`Initializing ${this.name}`);
        // 初始化逻辑
    }
    
    async start(): Promise<void> {
        const port = this.config.port || 0;
        this.server = this.app.listen(port, () => {
            this.logger.info(`${this.name} listening on port ${this.server.address().port}`);
        });
    }
    
    async stop(): Promise<void> {
        if (this.server) {
            this.server.close();
        }
    }
    
    async collectData(): Promise<DataItem[]> {
        // 数据收集逻辑
        return [];
    }
}

// 主函数
async function main() {
    const config = ConnectorConfig.fromFile('config.json');
    const connector = new TemplateConnector(config);
    
    await connector.initialize();
    await connector.start();
    
    // 优雅关闭处理
    process.on('SIGINT', async () => {
        await connector.stop();
        process.exit(0);
    });
}

main().catch(console.error);
```

### 5.3 Rust连接器环境
```bash
# 安装Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# 安装连接器开发工具
cargo install linch-mind-connector-cli

# 创建新连接器项目
linch-connector new my-connector --lang rust
cd my-connector
```

#### Rust连接器配置
```toml
# connectors/rust/template/Cargo.toml
[package]
name = "template-connector"
version = "0.1.0"
edition = "2021"

[[bin]]
name = "connector"
path = "src/main.rs"

[dependencies]
tokio = { version = "1.0", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
reqwest = { version = "0.11", features = ["json"] }
warp = "0.3"
uuid = { version = "1.0", features = ["v4"] }
chrono = { version = "0.4", features = ["serde"] }
tracing = "0.1"
tracing-subscriber = "0.3"
linch-mind-connector = "0.1"  # SDK包

[dev-dependencies]
tokio-test = "0.4"
```

## 6. 开发工作流程

### 6.1 日常开发流程
```bash
# 1. 启动开发环境
./scripts/dev-setup.sh

# 2. 启动Daemon (开发模式)
cd daemon
dart run bin/daemon.dart --dev

# 3. 启动Flutter应用 (另一个终端)
flutter run -d linux  # 或 macos/windows

# 4. 开发连接器插件 (第三个终端)
cd connectors/python/my-connector
python main.py --dev

# 5. 实时重载和热重启
# Flutter支持热重载 (r键)
# Daemon需要手动重启
# 连接器支持热重载 (取决于语言)
```

### 6.2 代码生成和构建
```bash
# Flutter代码生成
flutter packages pub run build_runner build

# 清理和重新生成
flutter packages pub run build_runner build --delete-conflicting-outputs

# Daemon构建
cd daemon
dart compile exe bin/daemon.dart -o ../build/linch_mind_daemon

# 构建所有平台
./scripts/build-all.sh
```

### 6.3 测试流程
```bash
# Flutter单元测试
flutter test

# Flutter集成测试
flutter test integration_test/

# Daemon测试
cd daemon
dart test

# 连接器测试
cd connectors/python/my-connector
python -m pytest tests/

# 端到端测试
./scripts/e2e-test.sh
```

## 7. 调试和故障排除

### 7.1 Flutter应用调试
```bash
# 启动调试模式
flutter run --debug

# 性能分析
flutter run --profile

# 查看日志
flutter logs

# Widget Inspector (VS Code中使用)
# Ctrl+Shift+P -> "Flutter: Open Widget Inspector"
```

### 7.2 Daemon调试
```bash
# 详细日志模式
dart run bin/daemon.dart --log-level debug

# 检查Daemon状态
curl http://localhost:61424/api/v1/health

# 查看连接器状态
curl http://localhost:61424/api/v1/connectors
```

### 7.3 连接器调试
```bash
# Python连接器调试
python main.py --debug --log-level DEBUG

# Node.js连接器调试
npm run dev -- --debug

# 检查连接器健康状态
curl http://localhost:3001/health
```

## 8. 性能优化建议

### 8.1 Flutter应用优化
```dart
// 使用const构造函数
const Text('Hello World')

// 优化ListView构建
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) => ItemWidget(items[index]),
)

// 使用RepaintBoundary优化重绘
RepaintBoundary(
  child: ExpensiveWidget(),
)
```

### 8.2 Daemon性能优化
```dart
// 使用连接池
class DatabasePool {
  final Queue<Database> _available = Queue();
  final int maxConnections;
  
  Future<T> withConnection<T>(Future<T> Function(Database) operation) async {
    final db = await _acquire();
    try {
      return await operation(db);
    } finally {
      _release(db);
    }
  }
}

// 批量处理数据
class BatchProcessor<T> {
  final int batchSize;
  final Duration flushInterval;
  final List<T> _buffer = [];
  
  Future<void> add(T item) async {
    _buffer.add(item);
    if (_buffer.length >= batchSize) {
      await _flush();
    }
  }
}
```

## 9. 部署和分发

### 9.1 开发构建脚本
```bash
#!/bin/bash
# scripts/build-dev.sh

echo "Building Linch Mind development version..."

# 清理旧构建
flutter clean
rm -rf build/

# 构建Flutter应用
flutter build linux --debug
flutter build macos --debug
flutter build windows --debug

# 构建Daemon
cd daemon
dart compile exe bin/daemon.dart -o ../build/daemon/linch_mind_daemon
cd ..

# 构建连接器
./scripts/build-connectors.sh

echo "Development build completed!"
```

### 9.2 生产构建配置
```bash
#!/bin/bash
# scripts/build-release.sh

echo "Building Linch Mind release version..."

# 构建优化版本
flutter build linux --release --obfuscate
flutter build macos --release --obfuscate  
flutter build windows --release --obfuscate

# 构建优化版Daemon
cd daemon
dart compile exe bin/daemon.dart -o ../build/daemon/linch_mind_daemon --target-os linux
cd ..

# 创建分发包
./scripts/package-release.sh
```

## 10. 开发者指南总结

### 10.1 快速开始检查清单
- [ ] Flutter SDK 3.13+ 已安装
- [ ] VS Code + Flutter插件已配置
- [ ] 项目依赖已安装 (`flutter pub get`)
- [ ] Daemon可以启动 (`dart run bin/daemon.dart`)
- [ ] Flutter应用可以运行 (`flutter run`)
- [ ] 至少一个连接器可以运行

### 10.2 开发最佳实践
1. **代码风格**: 遵循Dart官方代码规范
2. **状态管理**: 优先使用Riverpod Provider
3. **错误处理**: 实现完整的错误边界和恢复机制
4. **性能**: 定期运行性能分析和优化
5. **测试**: 保持高测试覆盖率 (>80%)
6. **文档**: 及时更新API文档和使用指南

### 10.3 常见问题解决
- **Flutter Doctor问题**: 按照提示安装缺失的组件
- **包依赖冲突**: 使用 `flutter pub deps` 检查依赖树
- **热重载失败**: 重启应用或使用热重启 (Shift+R)
- **Daemon连接失败**: 检查端口占用和防火墙设置
- **连接器无响应**: 检查日志和进程状态

这个开发环境配置为Linch Mind的Flutter迁移提供了完整的开发支持，特别强调了多语言连接器生态系统的开发便利性。

---

*文档版本: 1.0*  
*创建时间: 2025-08-02*  
*维护团队: Flutter开发组*