# Linch Mind UI

**跨平台用户界面** - Linch Mind个人AI生活助手的现代化Flutter前端

**版本**: 1.0.0+1  
**架构**: Flutter + Riverpod + IPC客户端  
**平台支持**: macOS, Windows, Linux, iOS, Android, Web  
**状态**: 生产就绪

---

## 🚀 核心特性

### 🔥 现代Flutter架构
- **Riverpod状态管理**: 类型安全、可测试的响应式状态管理
- **IPC原生通信**: 直接与Daemon IPC通信，零HTTP依赖
- **响应式设计**: 适配桌面、移动和Web平台
- **暗色模式支持**: 跟随系统主题自动切换

### 🎯 智能交互界面
- **连接器管理**: 可视化连接器状态监控和配置管理
- **知识星云**: 3D可视化知识图谱浏览器
- **智能推荐**: 基于AI的个性化内容推荐界面
- **实时反馈**: WebView配置界面，所见即所得

### 🔌 高级功能
- **动态表单**: JSON Schema驱动的配置表单生成
- **错误监控**: 实时错误监控和用户友好的错误提示
- **性能监控**: IPC连接状态和性能指标可视化
- **多语言支持**: 国际化i18n支持框架

---

## 🏗️ 应用架构

```
┌─────────────────────────────────────────┐
│           Flutter UI Layer             │
├─────────────────────────────────────────┤
│  Screens (页面层)                        │
│  ├─ 应用初始化 (AppInitializationScreen) │
│  ├─ 连接器管理 (ConnectorManagementScreen)│
│  ├─ 知识星云 (KnowledgeNebulaScreen)     │
│  └─ 设置页面 (SettingsScreen)           │
├─────────────────────────────────────────┤
│  Providers (状态管理层)                   │
│  ├─ DaemonProviders (daemon状态)        │
│  └─ AppProviders (应用状态)              │
├─────────────────────────────────────────┤
│  Services (服务层)                       │
│  ├─ IPCClient (IPC通信)                 │
│  ├─ DaemonLifecycleService (生命周期)    │
│  └─ ConnectorAPIClient (连接器API)      │
├─────────────────────────────────────────┤
│  Models (数据模型层)                      │
│  ├─ IPCProtocol (IPC协议模型)            │
│  ├─ ConnectorLifecycleModels (连接器模型)│
│  └─ APIResponse (通用响应模型)           │
└─────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 环境要求
- **Flutter**: 3.10.0+
- **Dart**: 3.0.0+
- **支持平台**: macOS, Windows, Linux, iOS, Android, Web

### 开发环境设置

```bash
# 1. 检查Flutter环境
flutter doctor

# 2. 获取依赖
flutter pub get

# 3. 生成代码 (Freezed + JsonAnnotation)
flutter packages pub run build_runner build

# 4. 运行应用 (macOS桌面版)
flutter run -d macos

# 5. 其他平台
flutter run -d windows     # Windows
flutter run -d linux       # Linux
flutter run -d chrome      # Web版本
```

### 项目配置
```yaml
# pubspec.yaml 核心依赖
dependencies:
  flutter_riverpod: ^2.4.0    # 状态管理
  reactive_forms: ^17.0.0     # 动态表单
  sqflite: ^2.3.0            # 本地数据库
  shared_preferences: ^2.2.0  # 配置存储
  freezed_annotation: ^2.4.4  # 不可变模型
```

---

## 📁 目录结构

```
ui/
├── lib/
│   ├── main.dart                    # 应用入口
│   ├── models/                      # 数据模型
│   │   ├── ipc_protocol.dart        # IPC协议模型
│   │   ├── connector_lifecycle_models.dart # 连接器生命周期
│   │   └── api_response.dart        # API响应模型
│   ├── providers/                   # Riverpod状态提供者
│   │   ├── app_providers.dart       # 应用级状态
│   │   └── daemon_providers.dart    # Daemon状态
│   ├── screens/                     # 页面组件
│   │   ├── app_initialization_screen.dart    # 初始化页面
│   │   ├── connector_management_screen.dart  # 连接器管理
│   │   ├── knowledge_nebula_screen.dart      # 知识星云
│   │   └── settings_screen.dart             # 设置页面
│   ├── services/                    # 业务服务
│   │   ├── ipc_client.dart          # IPC通信客户端
│   │   ├── daemon_lifecycle_service.dart # Daemon生命周期
│   │   └── connector_*_api_client.dart   # 各种API客户端
│   ├── widgets/                     # 可复用组件
│   │   ├── config/                  # 配置相关组件
│   │   │   ├── webview_config_widget.dart   # WebView配置
│   │   │   └── json_schema_form_widget.dart # 动态表单
│   │   └── error_monitor_widget.dart        # 错误监控
│   └── utils/                       # 工具类
│       ├── app_logger.dart          # 日志工具
│       └── error_monitor.dart       # 错误监控
├── test/                            # 测试文件
│   ├── models/                      # 模型测试
│   ├── providers/                   # 状态管理测试
│   └── widgets/                     # 组件测试
└── assets/                          # 静态资源
    ├── icons/                       # 应用图标
    └── images/                      # 图片资源
```

---

## 🔧 开发指南

### Riverpod状态管理模式

```dart
// 1. 定义状态提供者
@riverpod
class DaemonConnection extends _$DaemonConnection {
  @override
  Future<bool> build() async {
    return await ref.read(ipcClientProvider).isConnected();
  }

  Future<void> connect() async {
    state = const AsyncValue.loading();
    try {
      await ref.read(ipcClientProvider).connect();
      state = const AsyncValue.data(true);
    } catch (error) {
      state = AsyncValue.error(error, StackTrace.current);
    }
  }
}

// 2. 在组件中使用
class MyWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connectionState = ref.watch(daemonConnectionProvider);
    
    return connectionState.when(
      data: (isConnected) => isConnected 
        ? const ConnectedWidget()
        : const DisconnectedWidget(),
      loading: () => const CircularProgressIndicator(),
      error: (error, stack) => ErrorWidget(error.toString()),
    );
  }
}
```

### IPC客户端使用

```dart
// 创建IPC客户端
final ipcClient = IPCClient();

// 建立连接
await ipcClient.connect();

// 发送IPC请求
final response = await ipcClient.sendRequest(
  IPCRequest(
    method: 'GET',
    path: '/api/v1/connectors',
    data: null,
  ),
);

// 处理响应
if (response.statusCode == 200) {
  final connectors = response.data['connectors'];
  // 更新UI状态
}
```

### 动态配置表单

```dart
// JSON Schema驱动的配置表单
class ConnectorConfigWidget extends StatelessWidget {
  final Map<String, dynamic> schema;
  final Map<String, dynamic> initialValues;

  @override
  Widget build(BuildContext context) {
    return JsonSchemaFormWidget(
      schema: schema,
      initialValues: initialValues,
      onSubmit: (values) async {
        // 提交配置到Daemon
        await ref.read(connectorApiClientProvider)
            .updateConfig(connectorId, values);
      },
    );
  }
}
```

---

## 🧪 测试

### 运行测试套件

```bash
# 运行所有测试
flutter test

# 运行特定测试文件
flutter test test/providers/app_providers_test.dart

# 生成测试覆盖率报告
flutter test --coverage
lcov --summary coverage/lcov.info
```

### 测试最佳实践

```dart
// 1. Provider测试
void main() {
  group('DaemonConnectionProvider', () {
    testWidgets('should connect successfully', (tester) async {
      final container = ProviderContainer();
      final provider = daemonConnectionProvider;
      
      // 模拟成功连接
      when(mockIpcClient.connect()).thenAnswer((_) async => true);
      
      // 验证状态变化
      expect(
        container.read(provider.future),
        completion(isTrue),
      );
    });
  });
}

// 2. 组件测试
void main() {
  group('ConnectorStatusWidget', () {
    testWidgets('should display running status', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: ConnectorStatusWidget(
              status: ConnectorStatus.running,
            ),
          ),
        ),
      );

      expect(find.text('运行中'), findsOneWidget);
      expect(find.byIcon(Icons.check_circle), findsOneWidget);
    });
  });
}
```

---

## 🎨 UI/UX设计指南

### 设计系统
- **Material Design 3**: 遵循最新Material设计语言
- **响应式布局**: 适配桌面、平板、手机屏幕尺寸
- **无障碍支持**: 支持屏幕阅读器和键盘导航
- **主题系统**: 支持浅色、深色和系统主题

### 核心组件

```dart
// 统一应用栏
class UnifiedAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final List<Widget>? actions;

  @override
  Widget build(BuildContext context) {
    return AppBar(
      title: Text(title),
      backgroundColor: Theme.of(context).colorScheme.surface,
      actions: actions,
    );
  }
}

// 状态指示器
class StatusIndicator extends StatelessWidget {
  final ConnectorStatus status;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: _getStatusColor(status),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(_getStatusText(status)),
    );
  }
}
```

---

## 🔒 安全考虑

### IPC通信安全
- **本地通信**: 仅限本地进程间通信，无网络暴露
- **权限验证**: 验证IPC连接的进程身份
- **数据加密**: 敏感配置数据本地加密存储

### 用户数据保护
- **隐私优先**: 所有数据本地处理，不上传云端
- **安全存储**: 使用SharedPreferences安全存储用户配置
- **数据清理**: 应用卸载时自动清理所有用户数据

---

## 🚀 构建部署

### 桌面应用构建

```bash
# macOS应用
flutter build macos --release

# Windows应用
flutter build windows --release

# Linux应用
flutter build linux --release
```

### 移动应用构建

```bash
# Android APK
flutter build apk --release

# iOS应用 (需要macOS)
flutter build ios --release
```

### Web应用构建

```bash
# Web版本
flutter build web --release

# 部署到本地服务器
python -m http.server 8000 -d build/web
```

---

## 🔗 相关文档

- **[Daemon文档](../daemon/README.md)**: 后端服务完整文档
- **[IPC协议规范](../docs/01_technical_design/api_contract_design.md)**: IPC通信协议
- **[Flutter架构设计](../docs/01_technical_design/flutter_architecture_design.md)**: UI架构设计文档
- **[连接器管理](../connectors/README.md)**: 连接器开发和集成

---

**UI应用状态**: ✅ 生产就绪  
**版本**: 1.0.0+1  
**最后更新**: 2025-08-08  
**维护团队**: Linch Mind UI Team
