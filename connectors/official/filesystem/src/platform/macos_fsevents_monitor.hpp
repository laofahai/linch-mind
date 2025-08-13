#pragma once

#ifdef __APPLE__

#include "../native_monitor.hpp"
#include <CoreServices/CoreServices.h>
#include <thread>
#include <queue>
#include <condition_variable>

class MacOSFSEventsMonitor : public INativeMonitor {
public:
    MacOSFSEventsMonitor();
    ~MacOSFSEventsMonitor() override;
    
    bool start(EventCallback callback) override;
    void stop() override;
    bool isRunning() const override { return m_running; }
    
    bool addPath(const MonitorConfig& config) override;
    bool removePath(const std::string& path) override;
    std::vector<std::string> getMonitoredPaths() const override;
    
private:
    // FSEvents相关
    FSEventStreamRef m_eventStream = nullptr;
    CFRunLoopRef m_runLoop = nullptr;
    std::thread m_eventThread;
    std::thread m_processThread;
    
    // 配置
    std::vector<MonitorConfig> m_configs;
    mutable std::mutex m_configMutex;
    
    // 事件队列
    std::queue<FileSystemEvent> m_eventQueue;
    std::mutex m_queueMutex;
    std::condition_variable m_queueCV;
    
    // 事件去重器
    std::unique_ptr<EventDebouncer> m_debouncer;
    
    // FSEvents回调
    static void fsEventsCallback(
        ConstFSEventStreamRef streamRef,
        void* clientCallBackInfo,
        size_t numEvents,
        void* eventPaths,
        const FSEventStreamEventFlags eventFlags[],
        const FSEventStreamEventId eventIds[]
    );
    
    // 内部方法
    void eventLoop();
    void processLoop();
    bool recreateEventStream();
    void handleFSEvent(const std::string& path, FSEventStreamEventFlags flags);
    FileEventType flagsToEventType(FSEventStreamEventFlags flags);
    MonitorConfig* findConfigForPath(const std::string& path);
};

#endif // __APPLE__