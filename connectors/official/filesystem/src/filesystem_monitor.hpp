#pragma once

#include <functional>
#include <memory>
#include <string>
#include <vector>
#include <set>
#include <unordered_map>
#include <thread>
#include <atomic>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <filesystem>
#include <chrono>

/**
 * Cross-platform filesystem monitoring using polling
 * Simple and reliable approach that works on all platforms
 */
class FileSystemMonitor {
public:
    struct FileEvent {
        std::string path;
        std::string eventType;  // "created", "modified", "deleted"
        uint64_t timestamp;
        size_t fileSize;
        
        FileEvent(const std::string& p, const std::string& type, uint64_t ts = 0, size_t size = 0)
            : path(p), eventType(type), timestamp(ts), fileSize(size) {}
    };

    using ChangeCallback = std::function<void(const FileEvent&)>;

    struct WatchConfig {
        std::string path;
        std::string name;
        bool enabled = true;
        bool recursive = true;
        std::set<std::string> supportedExtensions;
        size_t maxFileSize = 10 * 1024 * 1024;  // 10MB
        std::vector<std::string> ignorePatterns;
        int priority = 5;
        
        WatchConfig(const std::string& p) : path(p) {}
    };

    FileSystemMonitor();
    ~FileSystemMonitor();

    /**
     * Add a directory to watch
     * @param config Watch configuration for the directory
     * @return true if watch was added successfully
     */
    bool addWatch(const WatchConfig& config);

    /**
     * Remove a directory watch
     * @param path Directory path to stop watching
     * @return true if watch was removed successfully
     */
    bool removeWatch(const std::string& path);

    /**
     * Start monitoring filesystem changes
     * @param callback Function to call when filesystem events occur
     * @param pollInterval Polling interval in milliseconds (default: 1000)
     * @return true if monitoring started successfully
     */
    bool startMonitoring(ChangeCallback callback, int pollInterval = 1000);

    /**
     * Stop filesystem monitoring
     */
    void stopMonitoring();

    /**
     * Check if monitoring is currently active
     */
    bool isMonitoring() const;

    /**
     * Get list of currently watched directories
     */
    std::vector<std::string> getWatchedPaths() const;

    /**
     * Update configuration for a watched directory
     */
    bool updateWatchConfig(const std::string& path, const WatchConfig& config);

private:
    struct FileInfo {
        std::filesystem::file_time_type lastWriteTime;
        size_t fileSize;
        bool exists;
        
        FileInfo() : fileSize(0), exists(false) {}
        FileInfo(const std::filesystem::file_time_type& time, size_t size)
            : lastWriteTime(time), fileSize(size), exists(true) {}
    };

    std::atomic<bool> m_monitoring{false};
    std::thread m_monitorThread;
    std::thread m_processingThread;
    ChangeCallback m_callback;
    int m_pollInterval = 1000;
    
    // Event queue for processing
    std::queue<FileEvent> m_eventQueue;
    std::mutex m_queueMutex;
    std::condition_variable m_queueCondition;
    
    // Watch configurations
    std::vector<WatchConfig> m_watchConfigs;
    mutable std::mutex m_configMutex;
    
    // File state tracking
    std::unordered_map<std::string, FileInfo> m_fileStates;
    std::mutex m_statesMutex;

    void monitorLoop();
    void processEvents();
    void scanDirectory(const WatchConfig& config);
    void scanDirectoryRecursive(const std::string& dirPath, const WatchConfig& config);
    bool shouldProcessFile(const std::string& filePath, const WatchConfig& config);
    bool matchesIgnorePattern(const std::string& filePath, const std::vector<std::string>& patterns);
    WatchConfig* findConfigForPath(const std::string& filePath);
    uint64_t getCurrentTimestamp();
    void detectChanges(const std::string& filePath, const WatchConfig& config);
};