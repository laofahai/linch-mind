# Linch Mind 用户情境感知连接器

## 概述

用户情境感知连接器是Linch Mind系统的核心组件，专门负责理解和分析用户的当前活动情境。与传统的系统监控不同，该连接器专注于回答"用户在干什么"而非"系统在干什么"。

## 核心特性

### 🧠 用户活动监控
- **前台应用感知**：实时监控当前活动的应用程序
- **应用切换检测**：基于NSWorkspace API的事件驱动监控
- **活动模式识别**：智能分析用户的工作模式（专注工作、轻度使用、后台待机等）

### 🔋 设备状态感知  
- **电源状态监控**：电池/充电/插电状态检测
- **网络环境识别**：Wi-Fi/以太网/断开连接状态
- **设备唤醒/睡眠**：系统状态变化监控

### 📊 智能负载分析
- **轻量级采样**：最小化系统资源占用（<1% CPU，<50MB内存）
- **TOP进程识别**：关注高资源消耗的前5个进程
- **自适应采样**：根据用户活动模式调整监控频率
- **存储空间监控**：主要磁盘使用情况

### ⚡ 事件驱动架构
- **零轮询设计**：完全基于macOS通知机制
- **实时响应**：应用切换等关键事件的即时感知
- **低延迟处理**：事件处理延迟<100ms

## 技术架构

### 数据流转换
```
传统系统监控：系统指标 → 原始数据 → 存储
用户情境感知：用户行为 → 情境分析 → 智能推荐
```

### 核心组件
- **UserContextConnector**：主连接器类，协调所有感知功能
- **UserContextScheduler**：轻量级调度器，管理定期采样
- **NSWorkspace Integration**：macOS应用监控集成
- **智能事件处理**：基于用户行为模式的事件优先级

### 事件类型
- `ACTIVE_APP_CHANGED`：前台应用切换
- `DEVICE_STATE_CHANGED`：设备状态变化
- `SYSTEM_LOAD_UPDATE`：系统负载更新
- `USER_ACTIVITY_SUMMARY`：用户活动摘要

## 配置参数

```toml
# 用户情境感知连接器配置
[user_context]
load_sampling_interval = 10      # 负载采样间隔（分钟）
activity_summary_interval = 2    # 活动摘要间隔（小时）
enable_app_monitoring = true     # 启用应用监控
enable_device_state_monitoring = true  # 启用设备状态监控
top_process_count = 5            # TOP进程数量
```

## 性能指标

### 资源占用
- **CPU使用率**：< 1%（正常运行）
- **内存占用**：< 50MB
- **磁盘I/O**：最小化（仅事件记录）
- **网络流量**：零（本地处理）

### 响应性能
- **应用切换检测**：< 100ms
- **事件处理延迟**：< 50ms
- **数据更新频率**：事件驱动 + 10分钟定期采样

## 输出数据示例

### 用户活动情境
```json
{
  "event_type": "active_user_context",
  "timestamp": 1692312450123,
  "active_app": {
    "name": "Visual Studio Code",
    "bundle_id": "com.microsoft.VSCode",
    "pid": 1234,
    "is_frontmost": true
  },
  "activity_pattern": "focused_deep",
  "session_duration_minutes": 45
}
```

### 设备状态
```json
{
  "event_type": "device_state",
  "timestamp": 1692312450123,
  "power_state": "charging",
  "network_type": "wifi",
  "screen_locked": false,
  "user_idle_minutes": 0
}
```

### 智能负载信息
```json
{
  "event_type": "intelligent_load",
  "timestamp": 1692312450123,
  "system_load": {
    "load_average_1min": 1.5,
    "cpu_usage_percent": 25.3
  },
  "top_processes": [
    {
      "pid": 1234,
      "command": "Code Helper",
      "cpu_percent": 15.2
    }
  ],
  "resource_pressure": "normal"
}
```

## 与传统监控的对比

| 特性 | 传统系统监控 | 用户情境感知 |
|------|-------------|-------------|
| 关注点 | 系统性能指标 | 用户行为模式 |
| 数据类型 | CPU/内存/磁盘 | 应用使用/工作模式 |
| 更新频率 | 固定间隔轮询 | 事件驱动 + 智能采样 |
| 资源占用 | 较高（持续监控） | 极低（按需监控） |
| AI价值 | 技术指标 | 用户意图理解 |

## 构建和运行

### 编译
```bash
cd /path/to/system_info
mkdir build && cd build
cmake ..
make
```

### 运行
```bash
./bin/release/linch-mind-user-context
```

### 测试
```bash
./bin/release/linch-mind-user-context --version
./bin/release/linch-mind-user-context --help
```

## 兼容性

### 系统要求
- **操作系统**：macOS 10.15+
- **架构**：Intel x64 / Apple Silicon (M1/M2)
- **权限**：无需特殊权限（基础监控）

### 可选权限
- **无障碍访问**：获取窗口标题（可选）
- **完整磁盘访问**：增强文件监控（可选）

## 隐私保护

### 数据安全
- ✅ **本地处理**：所有数据本地分析，不上传云端
- ✅ **最小收集**：仅收集必要的用户活动信息
- ✅ **敏感过滤**：自动过滤敏感应用和内容
- ✅ **用户控制**：用户可完全控制监控范围

### 遵循原则
- 透明性：明确告知收集的数据类型
- 最小化：仅收集AI推荐所需的最少信息
- 用户控制：提供完整的开关和配置选项
- 本地优先：优先本地处理，避免数据传输

## 后续扩展

### 短期计划
- 窗口标题智能提取（需要权限授权）
- 更精确的用户空闲时间检测
- 应用使用时长统计

### 长期愿景
- 跨设备用户情境同步
- 基于机器学习的行为模式预测
- 个性化的工作效率建议

## 版本历史

### v1.0.0 (2025-08-17)
- 🎉 首次发布
- ✅ 基础用户情境感知功能
- ✅ 事件驱动的应用监控
- ✅ 设备状态感知
- ✅ 轻量级系统负载监控
- ✅ macOS NSWorkspace API集成

---

**注意**：本连接器代表了从传统"系统监控"向现代"用户情境理解"的重要转型，为AI推荐引擎提供更有价值的用户行为数据。