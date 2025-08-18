# 🖥️ Linch Mind 系统信息连接器

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](README.md)
[![Language](https://img.shields.io/badge/language-C%2B%2B17-blue.svg)](CMakeLists.txt)
[![Build](https://img.shields.io/badge/build-CMake-green.svg)](CMakeLists.txt)

高性能系统信息收集连接器，专为 Linch Mind 个人AI助手设计。基于统一架构框架的C++17实现，提供系统监控、文件索引和资源使用情况统计。

## 🚀 核心特性

### ⚡ 系统监控能力
- **静态信息收集**: CPU型号、内存总量、系统版本等基础信息
- **动态监控**: CPU使用率、内存使用、磁盘空间、网络状态
- **分层收集策略**: 静态信息一次性收集，动态信息定期更新
- **轻量级设计**: 最小化系统资源占用

### 🗂️ 文件索引功能
- **全局文件索引**: 支持全盘文件扫描和索引
- **增量更新**: 定期检测文件变更，更新索引
- **智能过滤**: 跳过系统文件和临时文件
- **性能优化**: 异步扫描，不阻塞主线程

### 🌐 跨平台支持
- **Windows 10+**: WMI接口 + Win32 API
- **macOS 10.15+**: System Information框架 + Cocoa API
- **Linux**: procfs + sysfs + 标准UNIX工具
- **统一接口**: 所有平台使用相同的API和配置

### 🔧 企业级特性
- **心跳机制**: 自动维持与daemon的连接
- **健康检查**: 定期自检和状态报告
- **错误恢复**: 自动重试和故障转移
- **配置热重载**: 支持运行时配置更新

## 📊 收集的系统信息

### 静态信息（启动时收集）
- **硬件信息**: CPU型号、核心数、内存总量、存储设备
- **系统信息**: 操作系统版本、内核版本、主机名
- **网络配置**: 网络接口、IP地址、DNS配置

### 动态信息（定期更新）
- **CPU状态**: 使用率、负载均衡、温度（如支持）
- **内存状态**: 已用内存、可用内存、缓存使用
- **磁盘状态**: 磁盘使用率、I/O统计、剩余空间
- **网络状态**: 网络流量、连接数、延迟统计

### 文件索引信息
- **文件路径**: 完整路径和相对路径
- **文件属性**: 大小、创建时间、修改时间、权限
- **文件类型**: MIME类型识别和分类
- **文件内容**: 文本文件内容摘要（可配置）

## ⚙️ 配置选项

```toml
# 系统监控配置
[monitoring]
collect_interval = 30        # 动态信息收集间隔（秒）
enable_cpu_monitoring = true
enable_memory_monitoring = true
enable_disk_monitoring = true
enable_network_monitoring = true

# 文件索引配置
[file_index]
enable_file_indexing = false     # 默认禁用文件索引
scan_directories = ["/Users", "/Documents"]
exclude_patterns = [
    ".*\\.log$", ".*\\.tmp$", "\\.git", 
    "node_modules", "__pycache__"
]
max_file_size = 50              # 最大文件大小(MB)
scan_interval = 3600            # 增量扫描间隔(秒)

# 性能配置
[performance]
max_cpu_usage = 10              # 最大CPU使用率(%)
max_memory_usage = 100          # 最大内存使用(MB)
enable_low_priority = true      # 启用低优先级模式
```

## 🔒 隐私和安全

- **本地处理**: 所有数据在本地处理，不上传到云端
- **权限最小化**: 只请求必要的系统权限
- **数据过滤**: 自动排除敏感文件和目录
- **安全传输**: 通过IPC安全通道传输数据

## 📈 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 可执行文件大小 | ~380KB | 包含所有依赖的完整可执行文件 |
| 启动时间 | <300ms | 包括系统信息初始化 |
| 内存占用 | ~12MB | 包括文件索引缓存 |
| CPU使用率 | <5% | 正常监控状态下 |
| 系统影响 | 极低 | 低优先级后台运行 |

## 🛠️ 编译和安装

### 前置要求
- CMake 3.20+
- C++17兼容编译器
- 平台特定依赖（详见构建文档）

### 编译命令
```bash
# 进入连接器目录
cd connectors/official/system_info

# 构建
./build.sh

# 生成的可执行文件
ls -la bin/release/linch-mind-system-info
```

## 🚀 使用示例

### 启动连接器
```bash
# 直接运行
./bin/release/linch-mind-system-info

# 后台运行
./bin/release/linch-mind-system-info &
```

### 通过Daemon管理
```bash
# 注册连接器
linch-mind connector register system_info

# 启动连接器
linch-mind connector start system_info

# 查看状态
linch-mind connector status system_info
```

## 📋 数据格式

系统信息以JSON格式发送到Daemon：

```json
{
  "type": "system_info",
  "timestamp": "2024-01-15T10:30:00Z",
  "info_type": "dynamic",
  "data": {
    "cpu": {
      "usage_percent": 25.5,
      "cores": 8,
      "frequency_mhz": 3200
    },
    "memory": {
      "total_gb": 16,
      "used_gb": 8.2,
      "available_gb": 7.8
    },
    "disk": [
      {
        "mount_point": "/",
        "total_gb": 500,
        "used_gb": 250,
        "free_gb": 250
      }
    ]
  }
}
```

## 🔧 故障排除

### 常见问题

1. **权限不足**
   - 确保连接器有读取系统信息的权限
   - Linux下可能需要sudo权限

2. **性能影响**
   - 调整`collect_interval`增加采集间隔
   - 禁用不需要的监控模块

3. **文件索引慢**
   - 减少`scan_directories`范围
   - 增加`exclude_patterns`过滤规则

### 日志和调试
- 连接器日志：查看系统日志或stdout输出
- Daemon日志：检查Daemon的连接器管理日志
- 性能监控：使用系统监控工具检查资源使用

## 📝 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交Pull Request和Issue。请确保：
- 遵循C++17标准
- 添加适当的测试
- 更新相关文档
- 保持跨平台兼容性

---

**注意**: 此连接器收集系统信息用于个人AI助手优化，不会上传任何数据到外部服务器。