#ifdef __APPLE__

#include "macos_fsevents_monitor.hpp"
#include <iostream>
#include <algorithm>
#include <cstring>

MacOSFSEventsMonitor::MacOSFSEventsMonitor() 
    : m_debouncer(std::make_unique<EventDebouncer>(std::chrono::milliseconds(300))) {
}

MacOSFSEventsMonitor::~MacOSFSEventsMonitor() {
    stop();
}

bool MacOSFSEventsMonitor::start(EventCallback callback) {
    if (m_running) {
        return false;
    }
    
    m_eventCallback = callback;
    m_running = true;
    
    // 启动事件循环线程
    m_eventThread = std::thread(&MacOSFSEventsMonitor::eventLoop, this);
    
    // 启动事件处理线程
    m_processThread = std::thread(&MacOSFSEventsMonitor::processLoop, this);
    
    // 等待事件流创建
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    
    return recreateEventStream();
}

void MacOSFSEventsMonitor::stop() {
    if (!m_running) {
        return;
    }
    
    m_running = false;
    
    // 停止FSEvents流
    if (m_eventStream) {
        FSEventStreamStop(m_eventStream);
        FSEventStreamInvalidate(m_eventStream);
        FSEventStreamRelease(m_eventStream);
        m_eventStream = nullptr;
    }
    
    // 停止运行循环
    if (m_runLoop) {
        CFRunLoopStop(m_runLoop);
    }
    
    // 唤醒处理线程
    m_queueCV.notify_all();
    
    // 等待线程结束
    if (m_eventThread.joinable()) {
        m_eventThread.join();
    }
    
    if (m_processThread.joinable()) {
        m_processThread.join();
    }
}

bool MacOSFSEventsMonitor::addPath(const MonitorConfig& config) {
    std::lock_guard<std::mutex> lock(m_configMutex);
    
    // 检查路径是否已存在
    auto it = std::find_if(m_configs.begin(), m_configs.end(),
        [&config](const MonitorConfig& c) {
            return c.path == config.path;
        });
    
    if (it != m_configs.end()) {
        // 更新配置
        *it = config;
    } else {
        m_configs.push_back(config);
    }
    
    // 如果正在运行，重新创建事件流
    if (m_running && m_eventStream) {
        return recreateEventStream();
    }
    
    return true;
}

bool MacOSFSEventsMonitor::removePath(const std::string& path) {
    std::lock_guard<std::mutex> lock(m_configMutex);
    
    auto it = std::find_if(m_configs.begin(), m_configs.end(),
        [&path](const MonitorConfig& c) {
            return c.path == path;
        });
    
    if (it == m_configs.end()) {
        return false;
    }
    
    m_configs.erase(it);
    
    // 如果正在运行，重新创建事件流
    if (m_running && m_eventStream) {
        return recreateEventStream();
    }
    
    return true;
}

std::vector<std::string> MacOSFSEventsMonitor::getMonitoredPaths() const {
    std::lock_guard<std::mutex> lock(m_configMutex);
    std::vector<std::string> paths;
    paths.reserve(m_configs.size());
    
    for (const auto& config : m_configs) {
        paths.push_back(config.path);
    }
    
    return paths;
}

void MacOSFSEventsMonitor::fsEventsCallback(
    ConstFSEventStreamRef streamRef,
    void* clientCallBackInfo,
    size_t numEvents,
    void* eventPaths,
    const FSEventStreamEventFlags eventFlags[],
    const FSEventStreamEventId eventIds[])
{
    auto* monitor = static_cast<MacOSFSEventsMonitor*>(clientCallBackInfo);
    char** paths = static_cast<char**>(eventPaths);
    
    for (size_t i = 0; i < numEvents; ++i) {
        monitor->handleFSEvent(paths[i], eventFlags[i]);
    }
}

void MacOSFSEventsMonitor::eventLoop() {
    m_runLoop = CFRunLoopGetCurrent();
    
    while (m_running) {
        CFRunLoopRunInMode(kCFRunLoopDefaultMode, 0.5, false);
    }
    
    m_runLoop = nullptr;
}

void MacOSFSEventsMonitor::processLoop() {
    while (m_running) {
        std::unique_lock<std::mutex> lock(m_queueMutex);
        
        // 等待事件或退出信号
        m_queueCV.wait_for(lock, std::chrono::milliseconds(100), [this] {
            return !m_eventQueue.empty() || !m_running;
        });
        
        // 处理队列中的事件
        while (!m_eventQueue.empty() && m_running) {
            FileSystemEvent event = m_eventQueue.front();
            m_eventQueue.pop();
            lock.unlock();
            
            // 添加到去重器
            m_debouncer->addEvent(event);
            
            // 检查是否有准备好的批量事件
            auto batchedEvents = m_debouncer->getEventsIfReady();
            if (!batchedEvents.empty()) {
                if (m_batchCallback) {
                    m_batchCallback(batchedEvents);
                } else {
                    // 逐个发送事件
                    for (const auto& evt : batchedEvents) {
                        if (m_eventCallback) {
                            m_eventCallback(evt);
                        }
                    }
                }
            }
            
            lock.lock();
        }
    }
    
    // 清理剩余事件
    auto remainingEvents = m_debouncer->forceFlush();
    if (!remainingEvents.empty()) {
        if (m_batchCallback) {
            m_batchCallback(remainingEvents);
        } else {
            for (const auto& evt : remainingEvents) {
                if (m_eventCallback) {
                    m_eventCallback(evt);
                }
            }
        }
    }
}

bool MacOSFSEventsMonitor::recreateEventStream() {
    // 停止现有流
    if (m_eventStream) {
        FSEventStreamStop(m_eventStream);
        FSEventStreamInvalidate(m_eventStream);
        FSEventStreamRelease(m_eventStream);
        m_eventStream = nullptr;
    }
    
    std::lock_guard<std::mutex> lock(m_configMutex);
    
    if (m_configs.empty()) {
        return true;  // 没有路径要监控
    }
    
    // 创建路径数组
    CFMutableArrayRef pathsToWatch = CFArrayCreateMutable(
        kCFAllocatorDefault, m_configs.size(), &kCFTypeArrayCallBacks);
    
    for (const auto& config : m_configs) {
        CFStringRef pathStr = CFStringCreateWithCString(
            kCFAllocatorDefault, config.path.c_str(), kCFStringEncodingUTF8);
        CFArrayAppendValue(pathsToWatch, pathStr);
        CFRelease(pathStr);
    }
    
    // 创建上下文
    FSEventStreamContext context;
    memset(&context, 0, sizeof(context));
    context.info = this;
    
    // 创建事件流
    m_eventStream = FSEventStreamCreate(
        kCFAllocatorDefault,
        &MacOSFSEventsMonitor::fsEventsCallback,
        &context,
        pathsToWatch,
        kFSEventStreamEventIdSinceNow,
        0.1,  // 延迟100ms
        kFSEventStreamCreateFlagFileEvents |  // 文件级事件
        kFSEventStreamCreateFlagNoDefer |      // 不延迟
        kFSEventStreamCreateFlagWatchRoot      // 监控根目录变化
    );
    
    CFRelease(pathsToWatch);
    
    if (!m_eventStream) {
        return false;
    }
    
    // 在运行循环上调度
    FSEventStreamScheduleWithRunLoop(
        m_eventStream, m_runLoop, kCFRunLoopDefaultMode);
    
    // 启动流
    return FSEventStreamStart(m_eventStream);
}

void MacOSFSEventsMonitor::handleFSEvent(const std::string& path, FSEventStreamEventFlags flags) {
    // 查找配置
    auto* config = findConfigForPath(path);
    if (!config) {
        return;
    }
    
    // 检查是否应该忽略
    if (shouldIgnorePath(path, *config)) {
        return;
    }
    
    // 转换事件类型
    FileEventType eventType = flagsToEventType(flags);
    if (eventType == FileEventType::UNKNOWN) {
        return;
    }
    
    // 创建事件
    FileSystemEvent event(path, eventType);
    
    // 填充额外信息
    try {
        fs::path fsPath(path);
        if (fs::exists(fsPath)) {
            event.isDirectory = fs::is_directory(fsPath);
            if (!event.isDirectory) {
                event.fileSize = fs::file_size(fsPath);
            }
        }
    } catch (...) {
        // 忽略错误
    }
    
    // 添加到队列
    {
        std::lock_guard<std::mutex> lock(m_queueMutex);
        m_eventQueue.push(event);
        m_queueCV.notify_one();
    }
}

FileEventType MacOSFSEventsMonitor::flagsToEventType(FSEventStreamEventFlags flags) {
    if (flags & kFSEventStreamEventFlagItemCreated) {
        return FileEventType::CREATED;
    }
    if (flags & kFSEventStreamEventFlagItemRemoved) {
        return FileEventType::DELETED;
    }
    if (flags & kFSEventStreamEventFlagItemRenamed) {
        // FSEvents不区分重命名的新旧路径，需要额外逻辑
        return FileEventType::MODIFIED;
    }
    if (flags & kFSEventStreamEventFlagItemModified) {
        return FileEventType::MODIFIED;
    }
    if (flags & kFSEventStreamEventFlagItemInodeMetaMod) {
        return FileEventType::MODIFIED;
    }
    
    return FileEventType::UNKNOWN;
}

MonitorConfig* MacOSFSEventsMonitor::findConfigForPath(const std::string& path) {
    for (auto& config : m_configs) {
        // 检查路径是否在监控目录下
        if (path.find(config.path) == 0) {
            // 如果不是递归监控，检查是否是直接子文件
            if (!config.recursive) {
                fs::path filePath(path);
                fs::path configPath(config.path);
                if (filePath.parent_path() != configPath) {
                    continue;
                }
            }
            return &config;
        }
    }
    return nullptr;
}

#endif // __APPLE__