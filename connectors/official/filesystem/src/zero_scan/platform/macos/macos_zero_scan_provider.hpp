#pragma once

#ifdef __APPLE__

#include "../../zero_scan_interface.hpp"
#include "../../../progress/scan_progress_manager.hpp"
#include <memory>
#include <atomic>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <future>  // 🚀 异步处理支持

namespace linch_connector {
namespace zero_scan {

/**
 * macOS 零扫描提供者
 * 
 * 核心策略：
 * 1. 主索引：Spotlight MDQuery API（不是 mdfind 命令）
 * 2. 增量更新：FSEvents API
 * 3. 备选方案：APFS 快照 API（需要 macOS 10.13+）
 * 
 * 这是真正的零扫描：利用 Spotlight 已建立的索引，
 * 而不是重新扫描文件系统。
 */
class MacOSZeroScanProvider : public IZeroScanProvider {
public:
    MacOSZeroScanProvider();
    ~MacOSZeroScanProvider() override;
    
    // IZeroScanProvider 接口实现
    bool initialize(const ScanConfiguration& config) override;
    void shutdown() override;
    
    bool performZeroScan(
        std::function<void(const UnifiedFileRecord&)> callback
    ) override;
    
    bool subscribeToChanges(
        std::function<void(const FileChangeEvent&)> callback
    ) override;
    
    void unsubscribeFromChanges() override;
    
    ScanStatistics getStatistics() const override;
    bool isAvailable() const override;
    std::string getPlatformInfo() const override;
    
    void updateConfiguration(const ScanConfiguration& config) override;
    
    void clearCache() override;
    bool warmupCache() override;
    
    void pause() override;
    void resume() override;
    void setThrottleLevel(int level) override;

private:
    // 配置和状态
    ScanConfiguration m_config;
    mutable ScanStatistics m_stats;
    std::atomic<bool> m_initialized{false};
    std::atomic<bool> m_scanning{false};
    std::atomic<bool> m_paused{false};
    std::atomic<int> m_throttle_level{0};
    
    // 系统负载监控
    double m_max_mds_cpu_percent = 50.0;
    mutable std::atomic<size_t> m_current_batch_size{0};
    
    // 回调函数
    std::function<void(const UnifiedFileRecord&)> m_file_callback;
    std::function<void(const FileChangeEvent&)> m_change_callback;
    
    // 平台特定对象（使用 void* 避免 Objective-C 头文件）
    void* m_mdquery = nullptr;           // MDQueryRef
    void* m_fsevents_stream = nullptr;   // FSEventStreamRef
    void* m_operation_queue = nullptr;   // NSOperationQueue
    
    // 线程管理
    std::unique_ptr<std::thread> m_fsevents_thread;
    std::unique_ptr<std::thread> m_worker_thread;
    mutable std::mutex m_mutex;
    std::condition_variable m_cv;
    
    // 缓存
    struct Cache {
        std::vector<UnifiedFileRecord> records;
        std::chrono::system_clock::time_point last_update;
        bool valid = false;
    };
    Cache m_cache;
    
    // 进度管理器
    std::unique_ptr<progress::ScanProgressManager> m_progress_manager;
    
    // 核心实现方法
    bool initializeSystemMonitoring();
    bool initializeFSEvents();
    bool executeMDQuery(std::function<void(const UnifiedFileRecord&)> callback);
    // 🧪 极简mdfind测试方法
    bool executeSimpleMDFind(std::function<void(const UnifiedFileRecord&)> callback);
    bool checkSystemLoad() const;
    // 已删除：processMDQueryResults - 废弃的方法
    
    // FSEvents 处理
    void startFSEventsRunLoop();
    static void fsEventsCallback(
        void* streamRef,
        void* clientCallBackInfo,
        size_t numEvents,
        void* eventPaths,
        const void* eventFlags,
        const void* eventIds
    );
    void handleFSEvent(const std::string& path, uint32_t flags);
    
    // 已删除：executeAsyncChunkedProcessing - 过度复杂
    
    
    // 辅助方法
    // 🔍 轻量级记录创建方法
    UnifiedFileRecord createMinimalIndexRecord(const std::string& file_path);
    FileChangeType determineChangeType(uint32_t flags);
    bool shouldIncludeFile(const std::string& path) const;
    std::string getQueryString() const;
    
    // 性能监控
    void updateStatistics();
    size_t getCurrentMemoryUsage() const;
    double getCurrentCPUUsage() const;
    
    // 平台检测
    bool checkSpotlightAvailability() const;
    bool checkAPFSAvailability() const;
    std::string getOSVersion() const;
};

/**
 * Spotlight 直接访问器（高级功能）
 * 
 * 直接访问 Spotlight 数据库文件
 * 需要特殊权限，作为备选方案
 */
class SpotlightDirectAccess {
public:
    SpotlightDirectAccess();
    ~SpotlightDirectAccess();
    
    bool open(const std::string& volume_path);
    void close();
    
    bool isOpen() const { return m_database != nullptr; }
    
    // 直接查询数据库
    bool queryAllFiles(std::function<void(const UnifiedFileRecord&)> callback);
    
    // 获取数据库统计
    struct DatabaseStats {
        size_t total_records;
        size_t index_size_bytes;
        std::chrono::system_clock::time_point last_update;
        std::string database_version;
    };
    
    DatabaseStats getStats() const;

private:
    void* m_database = nullptr;  // 数据库句柄
    std::string m_database_path;
    
    bool openDatabase(const std::string& path);
    bool readDatabaseHeader();
    bool parseRecord(const void* record_data, UnifiedFileRecord& record);
};

/**
 * APFS 快照扫描器（macOS 10.13+）
 * 
 * 利用 APFS 文件系统的快照功能
 * 可以快速获取文件系统状态
 */
class APFSSnapshotScanner {
public:
    APFSSnapshotScanner();
    ~APFSSnapshotScanner();
    
    bool isSupported() const;
    
    // 创建快照
    bool createSnapshot(const std::string& volume_path);
    
    // 比较快照差异
    struct SnapshotDiff {
        std::vector<UnifiedFileRecord> added;
        std::vector<UnifiedFileRecord> modified;
        std::vector<std::string> deleted;
    };
    
    SnapshotDiff compareSnapshots(
        const std::string& snapshot1,
        const std::string& snapshot2
    );
    
    // 列出所有快照
    std::vector<std::string> listSnapshots(const std::string& volume_path);
    
    // 删除快照
    bool deleteSnapshot(const std::string& snapshot_name);

private:
    bool checkAPFSVolume(const std::string& path) const;
    void* m_snapshot_handle = nullptr;
};

} // namespace zero_scan
} // namespace linch_connector

#endif // __APPLE__