#pragma once

#ifdef __linux__

#include "../native_monitor.hpp"
#include <sys/inotify.h>
#include <thread>
#include <queue>
#include <condition_variable>
#include <unordered_map>

class LinuxInotifyMonitor : public INativeMonitor {
public:
    LinuxInotifyMonitor();
    ~LinuxInotifyMonitor() override;
    
    bool start(EventCallback callback) override;
    void stop() override;
    bool isRunning() const override { return m_running; }
    
    bool addPath(const MonitorConfig& config) override;
    bool removePath(const std::string& path) override;
    std::vector<std::string> getMonitoredPaths() const override;
    
private:
    // inotify相关
    int m_inotifyFd = -1;
    std::thread m_eventThread;
    std::thread m_processThread;
    
    // 监控句柄映射
    struct WatchInfo {
        std::string path;
        MonitorConfig config;
        int wd;  // watch descriptor
    };
    
    std::unordered_map<int, WatchInfo> m_watches;      // wd -> WatchInfo
    std::unordered_map<std::string, int> m_pathToWd;  // path -> wd
    mutable std::mutex m_watchMutex;
    
    // 事件队列
    std::queue<FileSystemEvent> m_eventQueue;
    std::mutex m_queueMutex;
    std::condition_variable m_queueCV;
    
    // 事件去重器
    std::unique_ptr<EventDebouncer> m_debouncer;
    
    // 内部方法
    void eventLoop();
    void processLoop();
    int addWatch(const std::string& path, const MonitorConfig& config);
    void removeWatch(int wd);
    void handleInotifyEvent(const inotify_event* event);
    FileEventType maskToEventType(uint32_t mask);
    void addDirectoryRecursive(const std::string& dirPath, const MonitorConfig& config);
    void removeDirectoryRecursive(const std::string& dirPath);
    
    // inotify事件掩码
    static constexpr uint32_t WATCH_MASK = 
        IN_CREATE | IN_DELETE | IN_MODIFY | IN_MOVED_FROM | IN_MOVED_TO |
        IN_CLOSE_WRITE | IN_ATTRIB | IN_DELETE_SELF | IN_MOVE_SELF;
};

#endif // __linux__