#ifdef __APPLE__

#include "macos_fsevents_monitor.hpp"
#include <iostream>
#include <algorithm>
#include <cstring>

MacOSFSEventsMonitor::MacOSFSEventsMonitor() 
    : m_debouncer(std::make_unique<EventDebouncer>(std::chrono::milliseconds(500))),  // 🔧 修复过度防抖: 改为500ms合理值
      m_eventProcessingEnabled(true) {
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
    
    // 创建 GCD 队列
    m_dispatchQueue = dispatch_queue_create("com.linch-mind.filesystem-monitor", DISPATCH_QUEUE_SERIAL);
    
    // 启动事件处理线程
    m_processThread = std::thread(&MacOSFSEventsMonitor::processLoop, this);
    
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
    
    // 释放 GCD 队列
    if (m_dispatchQueue) {
        dispatch_release(m_dispatchQueue);
        m_dispatchQueue = nullptr;
    }
    
    // 唤醒处理线程
    m_queueCV.notify_all();
    
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

// 不再需要 eventLoop，使用 dispatch queue 代替

void MacOSFSEventsMonitor::processLoop() {
    while (m_running) {
        std::unique_lock<std::mutex> lock(m_queueMutex);
        
        // 🔧 修复过度超时：使用合理的超时避免响应迟缓
        // 每2秒检查一次批量事件，平衡响应性和性能
        auto timeout = std::chrono::milliseconds(2000);
        bool hasEvents = m_queueCV.wait_for(lock, timeout, [this] {
            return !m_eventQueue.empty() || !m_running;
        });
        
        // 处理队列中的事件（如果有）
        if (hasEvents && !m_eventQueue.empty() && m_running) {
            // 批量处理事件以减少锁操作
            std::vector<FileSystemEvent> localEvents;
            while (!m_eventQueue.empty() && localEvents.size() < 100) { // 限制批量大小
                localEvents.push_back(m_eventQueue.front());
                m_eventQueue.pop();
            }
            lock.unlock();
            
            // 在无锁状态下处理事件
            for (const auto& event : localEvents) {
                m_debouncer->addEvent(event);
            }
        } else {
            lock.unlock();
        }
        
        // 无论是否有新事件，都检查批量事件（超时机制）
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
    
    // 创建事件流 - 优化配置以大幅降低CPU使用率
    m_eventStream = FSEventStreamCreate(
        kCFAllocatorDefault,
        &MacOSFSEventsMonitor::fsEventsCallback,
        &context,
        pathsToWatch,
        kFSEventStreamEventIdSinceNow,
        1.0,   // 🔧 修复过度延迟: 改为1秒，保持响应性
        // 🔧 性能优化: 仅使用必要的标志位，避免系统级监控
        // 移除 kFSEventStreamCreateFlagWatchRoot 以防止监控整个文件系统
        // 移除 kFSEventStreamCreateFlagFileEvents 以使用目录级监控减少事件量
        kFSEventStreamCreateFlagUseCFTypes |   // 使用CF类型优化性能
        kFSEventStreamCreateFlagIgnoreSelf     // 忽略自身进程产生的事件
    );
    
    CFRelease(pathsToWatch);
    
    if (!m_eventStream) {
        return false;
    }
    
    // 使用 dispatch queue 调度（替代废弃的 RunLoop API）
    FSEventStreamSetDispatchQueue(m_eventStream, m_dispatchQueue);
    
    // 启动流
    return FSEventStreamStart(m_eventStream);
}

void MacOSFSEventsMonitor::handleFSEvent(const std::string& path, FSEventStreamEventFlags flags) {
    // 快速路径过滤：在查找配置之前进行基础过滤
    if (isQuickIgnorePath(path)) {
        return;
    }
    
    // 检查事件处理是否暂停（用于过载保护）
    if (!m_eventProcessingEnabled) {
        return;
    }
    
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
    
    // 创建事件 - 延迟文件系统检查到批处理阶段以减少CPU使用
    FileSystemEvent event(path, eventType);
    
    // 不在此处进行文件系统检查，延迟到批处理时进行
    // 这避免了每个FSEvents事件都触发同步文件系统调用
    event.isDirectory = false;  // 将在批处理时确定
    event.fileSize = 0;         // 将在批处理时确定
    
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

bool MacOSFSEventsMonitor::isQuickIgnorePath(const std::string& path) const {
    // 快速路径过滤：在详细配置检查之前进行基础过滤
    // 这些模式匹配开销很小，但能过滤掉大量无用事件
    
    static const std::vector<std::string> quickIgnorePatterns = {
        // 开发工具和IDE文件
        "/.git/", "/.svn/", "/.hg/", "/.bzr/",
        "/.vscode/", "/.idea/", "/.vs/",
        
        // Node.js和前端开发
        "/node_modules/", "/.npm/", "/.yarn/",
        "/dist/", "/build/", "/.next/", "/.nuxt/",
        
        // Python开发
        "/__pycache__/", "/.pytest_cache/", "/venv/", "/.env/",
        
        // 系统和缓存文件
        "/.DS_Store", "/Thumbs.db", "/.Spotlight-V100/",
        "/.Trashes/", "/.fseventsd/", "/.TemporaryItems/",
        
        // 日志和临时文件
        ".tmp", ".log", ".cache", "~$", ".swp", ".bak",
        
        // 媒体和二进制文件（如果不需要监控）
        ".dmg", ".iso", ".app/", ".pkg", ".deb", ".rpm"
    };
    
    // 快速字符串匹配检查
    for (const auto& pattern : quickIgnorePatterns) {
        if (path.find(pattern) != std::string::npos) {
            return true;
        }
    }
    
    // 检查文件名是否以特定字符开头（隐藏文件等）
    size_t lastSlash = path.find_last_of('/');
    if (lastSlash != std::string::npos && lastSlash + 1 < path.length()) {
        const std::string filename = path.substr(lastSlash + 1);
        
        // 隐藏文件
        if (filename[0] == '.') {
            return true;
        }
        
        // 临时文件
        if (filename[0] == '~' || filename.back() == '~') {
            return true;
        }
    }
    
    return false;
}

#endif // __APPLE__