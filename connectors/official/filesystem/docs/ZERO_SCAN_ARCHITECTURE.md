# 零扫描文件索引架构设计

## 架构理念

### 核心原则
1. **利用已有索引**：每个操作系统都已经维护了文件索引
2. **平台原生优先**：使用每个平台的最佳实践
3. **统一抽象接口**：对上层提供一致的 API
4. **增量更新机制**：实时跟踪文件变化

## 跨平台架构

```
┌──────────────────────────────────────────────────┐
│              Application Layer                   │
│         (Linch Mind Filesystem Connector)        │
├──────────────────────────────────────────────────┤
│           Unified Zero-Scan Interface            │
│                                                  │
│  - initialize()                                  │
│  - performZeroScan()                            │
│  - subscribeToChanges()                         │
│  - getStatistics()                              │
├──────────────────────────────────────────────────┤
│             Platform Abstraction Layer           │
├────────────┬─────────────┬──────────────────────┤
│  Windows   │    macOS    │       Linux          │
├────────────┼─────────────┼──────────────────────┤
│ MFT Reader │  Spotlight  │   locate DB          │
│ USN Journal│  FSEvents   │   inotify            │
│ Search API │  APFS API   │   fanotify           │
└────────────┴─────────────┴──────────────────────┘
```

## 平台实现策略

### Windows (Everything 原理)
```cpp
class WindowsZeroScan {
    // 方法1: 直接读取 MFT
    bool readMasterFileTable() {
        // 1. 打开卷设备
        // 2. 获取 MFT 位置
        // 3. 读取 MFT 记录
        // 4. 解析文件信息
    }
    
    // 方法2: USN Journal (增量更新)
    bool readUSNJournal() {
        // 监控文件系统变更日志
    }
    
    // 方法3: Windows Search Index
    bool queryWindowsSearch() {
        // 备选方案：利用 Windows 索引服务
    }
};
```

### macOS (当前平台)
```cpp
class MacOSZeroScan {
    // 方法1: Spotlight 数据库直接访问
    bool accessSpotlightDatabase() {
        // 位置: /.Spotlight-V100/Store-V2/
        // 格式: Core Data SQLite
    }
    
    // 方法2: MDQuery API (推荐)
    bool useMDQueryAPI() {
        // 使用 Metadata Query API
        // 无需文件系统遍历
    }
    
    // 方法3: APFS 快照 API
    bool useAPFSSnapshot() {
        // 利用文件系统快照功能
    }
    
    // 增量更新: FSEvents
    bool subscribeFSEvents() {
        // 实时文件系统事件
    }
};
```

### Linux
```cpp
class LinuxZeroScan {
    // 方法1: locate 数据库
    bool readLocateDatabase() {
        // 路径: /var/lib/mlocate/mlocate.db
        // 定期更新: updatedb
    }
    
    // 方法2: 文件系统特定 API
    bool useFilesystemAPI() {
        // ext4: 直接读取 inode 表
        // btrfs: 使用 btrfs-search
    }
    
    // 增量更新: inotify/fanotify
    bool subscribeInotify() {
        // 实时文件系统监控
    }
};
```

## 性能目标

| 指标 | 目标值 | Everything 参考值 |
|------|--------|------------------|
| 100万文件索引时间 | < 1秒 | ~0.5秒 |
| 内存占用 | < 100MB | ~50MB |
| CPU 使用率 | < 10% | < 5% |
| 增量更新延迟 | < 100ms | 实时 |

## 实现优先级

1. **P0: macOS MDQuery API 优化**
   - 当前平台
   - 已有 Spotlight 索引
   - 无需额外权限

2. **P1: Windows MFT 实现**
   - Everything 核心原理
   - 最高性能潜力

3. **P2: Linux locate 集成**
   - 广泛可用
   - 成熟稳定

## 关键技术挑战

### 1. 权限问题
- Windows: MFT 需要管理员权限
- macOS: Spotlight 数据库受保护
- Linux: 某些目录需要 root

**解决方案**: 多级降级策略
```
尝试顺序：
1. 直接访问 → 需要权限
2. 系统 API → 用户权限
3. 命令行工具 → 通用方案
```

### 2. 数据一致性
- 文件系统索引可能过时
- 实时变更需要同步

**解决方案**: 混合策略
```
初始化：批量索引
运行时：增量更新
定期：完整同步
```

### 3. 性能优化
- 大量文件的内存管理
- I/O 操作优化
- 并发处理

**解决方案**: 
```cpp
// 内存映射文件
mmap(database_file);

// 批处理
process_in_batches(1000);

// 多线程处理
parallel_for(files, process_file);
```

## 测试基准

### 测试环境
- 文件数量：1,000,000
- 目录深度：10 层
- 文件类型：混合

### 预期结果
| 平台 | 方法 | 预期时间 |
|------|------|----------|
| Windows | MFT | < 0.5s |
| Windows | Search API | < 2s |
| macOS | MDQuery | < 1s |
| macOS | mdfind | < 3s |
| Linux | locate | < 0.5s |
| Linux | find | > 30s (对比) |

## 代码组织

```
filesystem/
├── src/
│   ├── zero_scan/
│   │   ├── zero_scan_interface.hpp      # 统一接口
│   │   ├── zero_scan_factory.cpp        # 工厂模式
│   │   ├── platform/
│   │   │   ├── windows/
│   │   │   │   ├── mft_reader.cpp       # MFT 读取
│   │   │   │   ├── usn_journal.cpp      # USN 日志
│   │   │   │   └── windows_search.cpp   # Search API
│   │   │   ├── macos/
│   │   │   │   ├── spotlight_direct.cpp # 直接访问
│   │   │   │   ├── mdquery_api.cpp      # MDQuery
│   │   │   │   └── fsevents.cpp         # 增量更新
│   │   │   └── linux/
│   │   │       ├── locate_db.cpp        # locate 数据库
│   │   │       ├── inotify.cpp          # 实时监控
│   │   │       └── fs_specific.cpp      # 文件系统特定
│   │   └── common/
│   │       ├── file_filter.cpp          # 通用过滤
│   │       ├── batch_processor.cpp      # 批处理
│   │       └── performance_monitor.cpp  # 性能监控
```

## 实施计划

### 第一阶段：架构验证 (当前)
- [x] 架构设计文档
- [ ] 接口定义
- [ ] macOS MDQuery 原型

### 第二阶段：核心实现
- [ ] 三平台基础实现
- [ ] 性能测试基准
- [ ] 优化迭代

### 第三阶段：生产就绪
- [ ] 错误处理完善
- [ ] 权限降级策略
- [ ] 监控和日志

## 结论

真正的"零扫描"不是扫得快，而是不扫描。通过利用操作系统已有的文件索引，我们可以达到 Everything 级别的性能。关键是理解每个平台的文件系统架构，并使用正确的 API。

这不是一个临时方案，而是一个深思熟虑的架构设计。