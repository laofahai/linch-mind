# Linch Mind 连接器生态系统

**高性能C++连接器套件** - Linch Mind个人AI生活助手的数据收集引擎

**架构**: 原生C++实现 + 共享库架构  
**性能**: 体积优化95%+，启动速度提升20x  
**平台支持**: Windows, macOS, Linux  
**状态**: 生产就绪

---

## 🚀 连接器生态概览

### 📊 性能成果
- **体积优化**: 从8MB Python版本优化到50-200KB C++版本
- **启动速度**: 从2-3秒优化到<0.1秒
- **内存占用**: 从~50MB降低到~5MB
- **无依赖**: 单一可执行文件，无需运行时环境

### 🔌 官方连接器

| 连接器 | 功能描述 | 平台支持 | 状态 | 版本 |
|--------|----------|----------|------|------|
| **filesystem** | 文件系统实时监控 | Win/Mac/Linux | ✅ 生产 | v2.0.0 |
| **clipboard** | 剪贴板内容监控 | Win/Mac/Linux | ✅ 生产 | v0.1.2 |

### 🛠️ 共享基础设施
- **[shared/](./shared/README.md)**: C++连接器共享库
- **统一daemon发现**: 与UI完全一致的服务发现机制
- **标准化配置**: JSON Schema驱动的配置管理
- **HTTP客户端**: 基于libcurl的轻量封装

---

## 🏗️ 架构设计

### 连接器架构层次

```
┌─────────────────────────────────────────┐
│          Linch Mind Daemon             │
│        (IPC服务器 + 数据处理)            │
└─────────────────────────────────────────┘
                    ↑ HTTP推送
┌─────────────────────────────────────────┐
│            连接器生态系统                │
├─────────────────────────────────────────┤
│  官方连接器                              │
│  ├─ filesystem (文件系统监控)            │
│  ├─ clipboard (剪贴板监控)               │  
│  └─ [future] (更多连接器...)             │
├─────────────────────────────────────────┤
│  共享基础库 (shared/)                    │
│  ├─ DaemonDiscovery (服务发现)           │
│  ├─ ConfigManager (配置管理)             │
│  ├─ HttpClient (HTTP通信)                │
│  └─ Utils (通用工具)                     │
└─────────────────────────────────────────┘
```

### 统一数据流

```
数据源 → 连接器监控 → 数据处理 → HTTP推送 → Daemon IPC → UI显示
  ↓         ↓          ↓        ↓         ↓        ↓
文件系统   实时监控    JSON格式   API调用   图数据库   智能推荐
剪贴板     内容过滤    元数据     自动重试   向量索引   可视化
```

---

## 🚀 快速开始

### 环境要求
- **C++**: C++17标准兼容编译器
- **CMake**: 3.16+
- **依赖**: libcurl, nlohmann-json

### 构建所有连接器

```bash
# macOS系统
brew install curl nlohmann-json cmake

# Ubuntu/Debian系统  
sudo apt-get install libcurl4-openssl-dev nlohmann-json3-dev cmake build-essential

# 构建所有连接器
cd connectors/
./build_all.sh

# 构建特定连接器
cd official/filesystem/
./build.sh
```

### 运行连接器

```bash
# 启动文件系统连接器
./official/filesystem/filesystem-connector

# 启动剪贴板连接器  
./official/clipboard/clipboard-connector

# 查看连接器状态
./linch-mind connectors status
```

---

## 🔧 连接器开发指南

### 基础连接器模板

```cpp
#include <linch_connector/daemon_discovery.hpp>
#include <linch_connector/config_manager.hpp>
#include <linch_connector/http_client.hpp>
#include <linch_connector/utils.hpp>

using namespace linch_connector;

class MyConnector {
private:
    std::unique_ptr<ConfigManager> configManager;
    std::unique_ptr<HttpClient> httpClient;
    std::string daemonUrl;

public:
    bool initialize() {
        // 1. 发现daemon
        DaemonDiscovery discovery;
        auto daemonInfo = discovery.waitForDaemon(std::chrono::seconds(30));
        if (!daemonInfo) return false;
        
        daemonUrl = daemonInfo->getBaseUrl();
        
        // 2. 初始化配置
        configManager = std::make_unique<ConfigManager>(daemonUrl, "my-connector");
        configManager->loadFromDaemon();
        
        // 3. 初始化HTTP客户端
        httpClient = std::make_unique<HttpClient>();
        httpClient->addHeader("Content-Type", "application/json");
        
        return true;
    }
    
    void startMonitoring() {
        while (true) {
            // 监控数据源
            std::string data = collectData();
            
            // 推送到daemon
            pushData(data);
            
            // 等待下次检查
            std::this_thread::sleep_for(
                std::chrono::milliseconds(
                    static_cast<int>(configManager->getCheckInterval() * 1000)
                )
            );
        }
    }
    
private:
    std::string collectData() {
        // 实现具体的数据收集逻辑
        return "collected data";
    }
    
    void pushData(const std::string& data) {
        std::string itemId = "my-connector_" + utils::generateUUID();
        std::string dataItem = utils::createDataItem(
            itemId, data, "my-connector", "{}"
        );
        
        auto response = httpClient->post(
            daemonUrl + "/api/v1/data/ingest", 
            dataItem
        );
    }
};
```

### CMakeLists.txt 模板

```cmake
cmake_minimum_required(VERSION 3.16)
project(MyConnector)

set(CMAKE_CXX_STANDARD 17)

# 查找依赖
find_package(PkgConfig REQUIRED)
find_package(nlohmann_json REQUIRED)
pkg_check_modules(CURL REQUIRED libcurl)

# 添加共享库
add_subdirectory(../shared shared)

# 添加可执行文件
add_executable(my-connector
    src/main.cpp
    src/my_connector.cpp
)

# 链接库
target_link_libraries(my-connector
    linch_connector_shared
    nlohmann_json::nlohmann_json
    ${CURL_LIBRARIES}
)

target_include_directories(my-connector PRIVATE
    src
    ${CURL_INCLUDE_DIRS}
)
```

---

## 📋 连接器标准

### 必需实现
1. **daemon发现**: 使用shared库的DaemonDiscovery
2. **配置管理**: 实现JSON Schema配置格式
3. **数据推送**: 标准HTTP API调用
4. **健康检查**: 定期验证daemon连接
5. **错误处理**: 失败重试和优雅降级

### 配置标准

```json
{
  "type": "object",
  "title": "连接器名称配置",
  "description": "连接器功能描述",
  "properties": {
    "global_config": {
      "type": "object", 
      "title": "全局配置",
      "properties": {
        "check_interval": {
          "type": "number",
          "title": "检查间隔(秒)",
          "default": 1.0,
          "minimum": 0.1,
          "maximum": 3600.0
        }
      }
    }
  },
  "required": ["global_config"]
}
```

### 数据格式标准

```json
{
  "id": "connector-name_uuid",
  "content": "数据内容",
  "source": "connector-name", 
  "metadata": {
    "timestamp": "2025-08-08T10:30:00Z",
    "connector_version": "1.0.0",
    "data_type": "specific-type"
  }
}
```

---

## 🧪 测试与质量

### 单元测试

```cpp
// tests/test_my_connector.cpp
#include <gtest/gtest.h>
#include "my_connector.hpp"

TEST(MyConnectorTest, InitializationSuccess) {
    MyConnector connector;
    EXPECT_TRUE(connector.initialize());
}

TEST(MyConnectorTest, DataCollection) {
    MyConnector connector;
    std::string data = connector.collectTestData();
    EXPECT_FALSE(data.empty());
}
```

### 集成测试

```bash
# 构建测试版本
cmake -DBUILD_TESTS=ON ..
make

# 运行测试
./tests/my_connector_tests

# 性能基准测试
./tests/performance_benchmark
```

### 质量标准
- **代码覆盖率**: >80%
- **内存泄漏**: 零内存泄漏（Valgrind验证）
- **启动时间**: <1秒
- **运行稳定性**: >99.9%正常运行时间

---

## 📊 监控与运维

### 运行监控

```bash
# 查看所有连接器状态
./linch-mind connectors status

# 查看特定连接器日志
./linch-mind connectors logs filesystem

# 重启连接器
./linch-mind connectors restart clipboard
```

### 性能指标

```bash
# 连接器性能统计
./linch-mind connectors stats

# 输出示例:
# filesystem: 1.2MB processed, 0.01% CPU, 5.2MB RAM
# clipboard: 156 items, 0.001% CPU, 2.1MB RAM
```

### 故障排除

1. **连接失败**: 检查daemon状态和端口文件
2. **配置错误**: 验证JSON Schema格式
3. **权限问题**: 确保文件系统/剪贴板访问权限
4. **性能问题**: 调整check_interval参数

---

## 🔗 相关文档

- **[Shared库文档](./shared/README.md)**: 共享基础设施详细文档
- **[文件系统连接器](./official/filesystem/README.md)**: 文件系统监控连接器
- **[剪贴板连接器](./official/clipboard/README.md)**: 剪贴板监控连接器
- **[Daemon文档](../daemon/README.md)**: 后端服务集成文档

---

**连接器生态状态**: ✅ 生产就绪  
**总体版本**: v2.0.0  
**最后更新**: 2025-08-08  
**维护团队**: Linch Mind Connector Team