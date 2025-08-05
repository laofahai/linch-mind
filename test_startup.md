# UI启动逻辑测试指南

## 🎯 已实现的功能

### 1. 自动化daemon启动检查
- **开发模式**: 自动使用Poetry启动daemon，回退到Python直接启动
- **生产模式**: 检查系统服务状态，不直接启动

### 2. 智能启动流程
- UI启动时自动检查daemon状态
- 如果daemon未运行，根据模式自动启动
- 提供详细的初始化界面反馈

### 3. 设置界面daemon管理
- 实时显示daemon运行状态
- 开发模式支持手动启动/停止/重启
- 生产模式显示系统服务状态

## 🚀 测试步骤

### 测试1: 开发模式自动启动
1. 确保没有daemon进程运行: `pkill -f linch-daemon`
2. 启动UI应用: `flutter run -d macos`
3. **预期结果**: 
   - 显示初始化屏幕
   - 自动启动daemon
   - 成功连接后进入主界面

### 测试2: daemon已运行情况
1. 手动启动daemon: `cd daemon && poetry run linch-daemon`
2. 启动UI应用: `flutter run -d macos`
3. **预期结果**: 
   - 快速检测到已运行的daemon
   - 直接进入主界面

### 测试3: 设置界面管理
1. 在应用中进入设置页面
2. 展开"Daemon 状态"设置项
3. **预期结果**:
   - 显示详细的daemon信息
   - 在开发模式下可以控制daemon

## 🏗️ 技术架构

### 核心服务
- `DaemonLifecycleService`: daemon生命周期管理
- `DaemonPortService`: daemon发现和连接
- `AppInitializationScreen`: 初始化界面
- `DaemonStateNotifier`: daemon状态管理

### 启动模式检测
```dart
RunMode get runMode {
  // Debug模式 → 开发模式
  if (kDebugMode) return RunMode.development;
  
  // 环境变量检查
  if (Platform.environment['LINCH_MIND_MODE'] == 'production') {
    return RunMode.production;
  }
  
  // 开发环境文件检查
  final devIndicators = ['daemon/pyproject.toml', 'connectors/pyproject.toml', '.git'];
  // ...
}
```

### Daemon启动策略
```dart
// 优先使用Poetry
if (poetryPath != null) {
  process = await Process.start('poetry', ['run', 'linch-daemon'], 
    workingDirectory: 'daemon');
} else {
  // 回退到Python直接启动
  process = await Process.start(pythonPath, ['-m', 'api.main'], 
    workingDirectory: 'daemon');
}
```

## 🎨 用户体验

### 初始化界面
- 清晰的状态指示器(加载/成功/错误)
- 友好的状态文本说明
- 错误时提供重试和调试选项
- 运行模式指示器

### 设置界面
- 实时daemon状态显示
- 开发模式下的完整控制能力
- 生产模式的友好提示
- 错误信息的清晰展示

## 🔧 故障排除

### 常见问题
1. **Poetry未找到**: 系统会自动回退到Python直接启动
2. **端口冲突**: daemon会自动选择可用端口
3. **权限问题**: 端口文件权限验证确保安全性

### 调试功能
- 初始化屏幕的"查看详细信息"按钮
- 设置界面的daemon状态详情
- 控制台日志输出所有关键步骤

## 📝 总结

UI启动逻辑已完全重构，实现了：
✅ 自动daemon检查和启动
✅ 开发/生产模式智能切换  
✅ 友好的用户界面反馈
✅ 完整的错误处理机制
✅ 设置界面daemon管理功能

用户现在可以直接启动UI应用，系统会自动处理所有后端服务的启动和连接。