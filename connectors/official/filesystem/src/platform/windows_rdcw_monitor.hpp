#pragma once

#ifdef _WIN32

#include "../native_monitor.hpp"
#include <windows.h>
#include <thread>
#include <queue>
#include <condition_variable>
#include <unordered_map>

class WindowsRDCWMonitor : public INativeMonitor {
public:
    WindowsRDCWMonitor();
    ~WindowsRDCWMonitor() override;
    
    bool start(EventCallback callback) override;
    void stop() override;
    bool isRunning() const override { return m_running; }
    
    bool addPath(const MonitorConfig& config) override;
    bool removePath(const std::string& path) override;
    std::vector<std::string> getMonitoredPaths() const override;
    
private:
    // 监控信息
    struct WatchInfo {
        std::string path;
        MonitorConfig config;
        HANDLE hDir;
        OVERLAPPED overlapped;
        std::vector<BYTE> buffer;
        bool active;
    };
    
    // 监控映射
    std::unordered_map<std::string, std::unique_ptr<WatchInfo>> m_watches;
    mutable std::mutex m_watchMutex;
    
    // IOCP句柄
    HANDLE m_iocpHandle = INVALID_HANDLE_VALUE;
    
    // 线程
    std::thread m_eventThread;
    std::thread m_processThread;
    
    // 事件队列
    std::queue<FileSystemEvent> m_eventQueue;
    std::mutex m_queueMutex;
    std::condition_variable m_queueCV;
    
    // 事件去重器
    std::unique_ptr<EventDebouncer> m_debouncer;
    
    // 内部方法
    void eventLoop();
    void processLoop();
    bool addWatchInternal(const MonitorConfig& config);
    void removeWatchInternal(const std::string& path);
    void startMonitoring(WatchInfo* watchInfo);
    void handleCompletionStatus(WatchInfo* watchInfo, DWORD bytesTransferred);
    void processNotifications(WatchInfo* watchInfo, FILE_NOTIFY_INFORMATION* pNotify);
    FileEventType actionToEventType(DWORD action);
    std::string wideToUtf8(const std::wstring& wstr);
    
    // 监控标志
    static constexpr DWORD WATCH_FLAGS = 
        FILE_NOTIFY_CHANGE_FILE_NAME |
        FILE_NOTIFY_CHANGE_DIR_NAME |
        FILE_NOTIFY_CHANGE_ATTRIBUTES |
        FILE_NOTIFY_CHANGE_SIZE |
        FILE_NOTIFY_CHANGE_LAST_WRITE |
        FILE_NOTIFY_CHANGE_CREATION;
};

#endif // _WIN32