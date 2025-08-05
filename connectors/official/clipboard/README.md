# 剪贴板连接器 (C++版本)

高性能C++版本的剪贴板监控连接器，实现从8MB Python版本到50-200KB的大幅度体积优化。

**最新更新**: 修复CI/CD构建流程，确保构建成功状态正确返回。

## 🎯 性能优化成果

- **体积减少**: 从8MB减少到50-200KB (减少95%+)
- **启动速度**: 原生C++，启动几乎瞬时
- **内存占用**: 显著降低，适合后台长期运行
- **无依赖**: 单一可执行文件，无需Python环境

## 🏗️ 技术架构

### 核心组件

- **ClipboardMonitor**: 跨平台剪贴板监控
- **HttpClient**: 基于libcurl的HTTP客户端
- **ConfigManager**: 配置管理和热重载
- **Platform层**: Windows/macOS/Linux平台适配

### 技术栈

- **C++17**: 现代C++特性
- **libcurl**: HTTP通信
- **nlohmann/json**: JSON处理
- **平台原生API**: 剪贴板访问

## 🔧 构建说明

### 依赖安装

**macOS:**
```bash
brew install curl nlohmann-json cmake
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libcurl4-openssl-dev nlohmann-json3-dev uuid-dev libx11-dev cmake build-essential
```

### 构建步骤

```bash
# 自动构建（推荐）
./build.sh

# 手动构建
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
```

### 构建优化

构建脚本包含以下优化：

- **编译优化**: `-O3 -flto -DNDEBUG`
- **体积优化**: `--gc-sections --strip-all`
- **静态链接**: 减少运行时依赖
- **UPX压缩**: 进一步减小体积

## 📋 功能特性

### 完整API兼容

- 保持与Python版本相同的配置格式
- 相同的HTTP API接口
- 相同的数据格式和元数据

### 配置支持

```json
{
  "check_interval": 1.0,
  "min_content_length": 5,
  "max_content_length": 50000,
  "content_filters": {
    "filter_urls": false,
    "filter_sensitive": true
  }
}
```

### 平台支持

- **Windows 10+**: Win32 Clipboard API
- **macOS 10.15+**: NSPasteboard
- **Linux**: X11 Clipboard

## 🚀 部署运行

### 开发环境

```bash
# 设置daemon URL (可选)
export DAEMON_URL=http://localhost:58471

# 运行连接器
./clipboard-connector
```

### 生产部署

1. 构建发布版本: `./build.sh`
2. 复制二进制文件到目标机器
3. 配置daemon URL
4. 启动服务

### 系统服务 (Linux)

```ini
[Unit]
Description=Linch Mind Clipboard Connector
After=network.target

[Service]
Type=simple
User=your-user
ExecStart=/path/to/clipboard-connector
Environment=DAEMON_URL=http://localhost:58471
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## 🔍 监控和调试

### 日志输出

连接器输出结构化日志：

```
📋 Starting clipboard monitoring (interval: 1.0s)
✅ Processed clipboard change: 156 chars
❌ Failed to push clipboard data: HTTP 500
```

### 健康检查

连接器会定期测试daemon连接：

- 启动时验证连接
- 失败时自动重试
- 配置变更时热重载

## 📊 性能对比

| 指标 | Python版本 | C++版本 | 改进 |
|------|------------|---------|------|
| 文件大小 | ~8MB | 50-200KB | 95%+ |
| 启动时间 | 2-3秒 | <0.1秒 | 20x+ |
| 内存占用 | ~50MB | ~5MB | 10x |
| CPU占用 | 中等 | 极低 | 显著降低 |

## 🔧 故障排除

### 常见问题

1. **构建失败**: 检查依赖安装
2. **权限错误**: 确保剪贴板访问权限
3. **连接失败**: 验证daemon URL和端口

### 调试模式

```bash
# 详细输出
./clipboard-connector --verbose

# 测试连接
curl http://localhost:58471/
```

## 🤝 开发贡献

### 代码结构

```
src/
├── main.cpp              # 主程序入口
├── clipboard_monitor.*   # 剪贴板监控
├── http_client.*         # HTTP客户端
├── config_manager.*      # 配置管理
└── platform/            # 平台特定实现
    ├── windows_clipboard.*
    ├── macos_clipboard.*
    └── linux_clipboard.*
```

### 添加新平台

1. 创建平台特定的剪贴板实现
2. 更新CMakeLists.txt
3. 测试跨平台兼容性

## 📝 更新日志

### v0.1.2 (2025-08-05)
- 完整C++重写
- 跨平台支持
- 体积优化到50-200KB
- 保持完整API兼容性
- 集成构建系统支持