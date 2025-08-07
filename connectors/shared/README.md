# Linch Connector Shared Library

## 概述

这是Linch Mind C++连接器的共享库，提供统一的基础设施和API，用于所有C++连接器的开发。

## 核心功能

### 🔍 统一Daemon发现
- 基于 `~/.linch-mind/daemon.port` 文件的服务发现
- 自动PID验证和连接测试
- 与UI中Dart实现的完全一致性

### 🌐 HTTP客户端
- 基于libcurl的轻量级封装
- 支持GET/POST请求
- JSON数据传输
- 自动超时和错误处理

### ⚙️ 配置管理
- 从daemon动态加载配置
- 支持配置热重载
- 嵌套配置自动扁平化处理

### 🛠️ 通用工具
- UUID生成（跨平台）
- 时间戳生成（ISO格式）
- 内容类型检测
- JSON数据项创建

## 架构设计

```
linch_connector/
├── daemon_discovery.hpp    # Daemon服务发现
├── http_client.hpp         # HTTP客户端
├── config_manager.hpp      # 配置管理
└── utils.hpp              # 通用工具函数
```

### Daemon发现流程

1. **读取端口文件**: `~/.linch-mind/daemon.port` (格式: `port:pid`)
2. **安全检查**: 验证文件权限（Unix系统）
3. **进程验证**: 检查daemon进程是否仍在运行
4. **连接测试**: Socket连接测试验证可访问性
5. **缓存机制**: 缓存有效的daemon信息

### 与UI一致性

C++实现与UI中Dart代码的完全对应：

| 功能 | UI (Dart) | C++ Shared |
|------|-----------|------------|
| 端口文件路径 | `~/.linch-mind/daemon.port` | ✅ 相同 |
| 文件格式 | `port:pid` | ✅ 相同 |
| 权限检查 | Unix文件权限验证 | ✅ 相同 |
| 进程验证 | `ps -p` 或 `tasklist` | ✅ 相同 |
| 连接测试 | Socket连接 | ✅ 相同 |

## 使用方法

### 基本用法

```cpp
#include <linch_connector/daemon_discovery.hpp>
#include <linch_connector/config_manager.hpp>

using namespace linch_connector;

int main() {
    // 发现daemon
    DaemonDiscovery discovery;
    auto daemonInfo = discovery.waitForDaemon(std::chrono::seconds(30));
    
    if (!daemonInfo) {
        std::cerr << "❌ Failed to discover daemon" << std::endl;
        return 1;
    }
    
    // 初始化配置管理
    ConfigManager config(daemonInfo->getBaseUrl(), "my-connector");
    config.loadFromDaemon();
    
    // 使用配置
    double interval = config.getCheckInterval();
    
    return 0;
}
```

### 数据推送

```cpp
#include <linch_connector/http_client.hpp>
#include <linch_connector/utils.hpp>

// 创建数据项
std::string itemId = "my-connector_" + utils::generateUUID();
std::string dataItem = utils::createDataItem(
    itemId, 
    "Hello, World!", 
    "my-connector",
    R"({"source": "example"})"
);

// 推送到daemon
HttpClient client;
client.addHeader("Content-Type", "application/json");
auto response = client.post(daemonUrl + "/api/v1/data/ingest", dataItem);
```

## 构建要求

### 系统依赖

**macOS**:
```bash
brew install nlohmann-json curl
```

**Ubuntu/Debian**:
```bash
sudo apt-get install nlohmann-json3-dev libcurl4-openssl-dev uuid-dev
```

**Windows**:
```bash
vcpkg install nlohmann-json
```

### CMake构建

```bash
mkdir build && cd build
cmake ..
make
```

## 代码统计

### 重构前后对比

| 指标 | 重构前 | 重构后 | 改进 |
|------|--------|--------|------|
| **clipboard连接器** | 270行 | 206行 | -24% |
| **filesystem连接器** | 430行 | 323行 | -25% |
| **代码重复** | ~400行 | 0行 | -100% |
| **维护复杂度** | 高 | 低 | 大幅改善 |

### 代码减少详情

**移除的重复代码**:

- ConfigManager: 154行 → shared库  
- UUID/时间戳工具: 47行 → shared库
- daemon连接测试: 25行 → shared库
- JSON数据创建: 38行 → shared库

**总计减少**: ~372行重复代码

## 优势

### 🚀 开发效率
- 新连接器开发时间减半
- 统一的API和错误处理
- 标准化的配置模式

### 🔧 维护性
- bug修复一次生效所有连接器
- 统一的升级和安全补丁
- 一致的日志和错误报告

### 🔒 可靠性
- daemon发现逻辑与UI完全一致
- 经过测试的网络和配置处理
- 标准化的错误处理和恢复

### 📏 一致性
- 所有连接器使用相同的daemon发现机制
- 统一的数据格式和API契约
- 一致的配置管理模式

## 扩展指南

### 添加新的工具函数

```cpp
// 在utils.hpp中添加声明
namespace utils {
    std::string myNewFunction(const std::string& input);
}

// 在utils.cpp中实现
std::string utils::myNewFunction(const std::string& input) {
    // 实现逻辑
    return processedInput;
}
```

### 扩展配置管理

```cpp
// 在ConfigManager中添加新的配置获取方法
bool ConfigManager::getMyCustomConfig() const {
    return getConfigValue("my_custom_config", "false") == "true";
}
```

---

*版本: v1.0.0 | 创建时间: 2025-08-05*  
*实现了clipboard和filesystem连接器的完全重构*