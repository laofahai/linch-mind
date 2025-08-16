#pragma once

#ifdef __APPLE__

#include "../file_index_provider.hpp"
#include <CoreServices/CoreServices.h>
#include <thread>
#include <atomic>
#include <queue>
#include <mutex>
#include <condition_variable>

namespace linch_connector {

/**
 * macOS 文件索引提供者
 * 
 * 利用Spotlight索引实现零扫描文件索引：
 * 1. initialize() - 使用mdfind查询Spotlight索引
 * 2. watchChanges() - 使用FSEvents监控文件变更
 * 
 * 优势：
 * - 零扫描：完全利用系统已有索引
 * - 无需特殊权限：运行在用户权限下
 * - 实时性好：FSEvents提供毫秒级通知
 */
class MacOSFileIndexProvider : public FileIndexProvider {
public:
    MacOSFileIndexProvider();
    ~MacOSFileIndexProvider() override;
    
    // FileIndexProvider接口实现
    bool initialize() override;
    bool watchChanges() override;
    void stop() override;
    IndexStats getStats() const override;
    bool isAvailable() const override;
    std::string getPlatformInfo() const override;
    
    // 回调设置
    void setInitialBatchCallback(InitialBatchCallback callback) override;
    void setFileEventCallback(FileEventCallback callback) override;
    void setProgressCallback(ProgressCallback callback) override;
    
    // 配置
    void setWatchDirectories(const std::vector<std::string>& directories) override;
    void setExcludePatterns(const std::vector<std::string>& patterns) override;

private:
    // Spotlight索引查询
    bool querySpotlightIndex();
    void executeSpotlightQuery(const std::string& query);
    void parseSpotlightOutput(const std::string& output);
    FileInfo createFileInfoFromPath(const std::string& path);
    
    // FSEvents监控
    bool startFSEventsMonitoring();
    void stopFSEventsMonitoring();
    static void fsEventsCallback(
        ConstFSEventStreamRef streamRef,
        void* clientCallBackInfo,
        size_t numEvents,
        void* eventPaths,
        const FSEventStreamEventFlags eventFlags[],
        const FSEventStreamEventId eventIds[]
    );
    void processFSEvent(const std::string& path, FSEventStreamEventFlags flags);
    
    // 工作线程
    void initializationWorker();
    void eventProcessingWorker();
    
    // 辅助方法
    bool shouldExcludePath(const std::string& path) const;
    FileEventType determineFSEventType(FSEventStreamEventFlags flags) const;
    bool isSpotlightEnabled(const std::string& path) const;
    std::string executeCommand(const std::string& command) const;
    
    // 性能监控和限流
    bool shouldThrottleProcessing() const;
    void updateResourceUsage();
    double getCurrentCPUUsage() const;
    size_t getCurrentMemoryUsage() const;
    
    // Spotlight可用性检查
    bool checkSpotlightAvailability() const;
    std::string getSpotlightStatus() const;
    
    // 状态管理
    mutable std::mutex m_statsMutex;
    IndexStats m_stats;
    std::atomic<bool> m_running{false};
    std::atomic<bool> m_initialized{false};
    std::atomic<bool> m_watching{false};
    
    // 回调函数
    InitialBatchCallback m_initialBatchCallback;
    FileEventCallback m_fileEventCallback;
    ProgressCallback m_progressCallback;
    
    // 配置
    std::vector<std::string> m_watchDirectories;
    std::vector<std::string> m_excludePatterns;
    
    // FSEvents相关
    FSEventStreamRef m_eventStream{nullptr};
    CFRunLoopRef m_runLoop{nullptr};
    std::unique_ptr<std::thread> m_fsEventsThread;
    
    // 工作线程
    std::unique_ptr<std::thread> m_initThread;
    std::unique_ptr<std::thread> m_eventThread;
    
    // 事件队列 (用于从FSEvents回调到工作线程)
    std::queue<FileEvent> m_eventQueue;
    std::mutex m_eventQueueMutex;
    std::condition_variable m_eventQueueCV;
    
    // 批处理（性能优化）
    static constexpr size_t BATCH_SIZE = 100;  // 减小批次大小
    static constexpr size_t MAX_QUEUE_SIZE = 1000;  // 减小队列大小
    
    // Spotlight查询配置
    static constexpr const char* SPOTLIGHT_QUERY_ALL_FILES = 
        "kMDItemKind != 'Folder'";  // 查询所有非目录文件
    
    // 默认排除模式
    static const std::vector<std::string> DEFAULT_EXCLUDE_PATTERNS;
};

} // namespace linch_connector

#endif // __APPLE__