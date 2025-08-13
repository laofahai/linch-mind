#ifdef __linux__

#include "linux_inotify_monitor.hpp"
#include <iostream>
#include <algorithm>
#include <unistd.h>
#include <errno.h>
#include <cstring>
#include <poll.h>

LinuxInotifyMonitor::LinuxInotifyMonitor()
    : m_debouncer(std::make_unique<EventDebouncer>(std::chrono::milliseconds(300))) {
}

LinuxInotifyMonitor::~LinuxInotifyMonitor() {
    stop();
}

bool LinuxInotifyMonitor::start(EventCallback callback) {
    if (m_running) {
        return false;
    }
    
    // 创建inotify实例
    m_inotifyFd = inotify_init1(IN_NONBLOCK | IN_CLOEXEC);
    if (m_inotifyFd < 0) {
        std::cerr << "Failed to initialize inotify: " << strerror(errno) << std::endl;
        return false;
    }
    
    m_eventCallback = callback;
    m_running = true;
    
    // 启动事件循环线程
    m_eventThread = std::thread(&LinuxInotifyMonitor::eventLoop, this);
    
    // 启动事件处理线程
    m_processThread = std::thread(&LinuxInotifyMonitor::processLoop, this);
    
    return true;
}

void LinuxInotifyMonitor::stop() {
    if (!m_running) {
        return;
    }
    
    m_running = false;
    
    // 关闭inotify
    if (m_inotifyFd >= 0) {
        close(m_inotifyFd);
        m_inotifyFd = -1;
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
    
    // 清理监控
    std::lock_guard<std::mutex> lock(m_watchMutex);
    m_watches.clear();
    m_pathToWd.clear();
}

bool LinuxInotifyMonitor::addPath(const MonitorConfig& config) {
    if (m_inotifyFd < 0) {
        return false;
    }
    
    std::lock_guard<std::mutex> lock(m_watchMutex);
    
    // 检查路径是否已存在
    if (m_pathToWd.find(config.path) != m_pathToWd.end()) {
        // 更新配置
        int wd = m_pathToWd[config.path];
        m_watches[wd].config = config;
        return true;
    }
    
    // 添加监控
    if (config.recursive && fs::is_directory(config.path)) {
        addDirectoryRecursive(config.path, config);
    } else {
        addWatch(config.path, config);
    }
    
    return true;
}

bool LinuxInotifyMonitor::removePath(const std::string& path) {
    if (m_inotifyFd < 0) {
        return false;
    }
    
    std::lock_guard<std::mutex> lock(m_watchMutex);
    
    auto it = m_pathToWd.find(path);
    if (it == m_pathToWd.end()) {
        return false;
    }
    
    // 如果是目录，递归移除
    if (fs::is_directory(path)) {
        removeDirectoryRecursive(path);
    } else {
        removeWatch(it->second);
    }
    
    return true;
}

std::vector<std::string> LinuxInotifyMonitor::getMonitoredPaths() const {
    std::lock_guard<std::mutex> lock(m_watchMutex);
    std::vector<std::string> paths;
    paths.reserve(m_pathToWd.size());
    
    for (const auto& [path, wd] : m_pathToWd) {
        paths.push_back(path);
    }
    
    return paths;
}

void LinuxInotifyMonitor::eventLoop() {
    const size_t BUFFER_SIZE = 4096;
    char buffer[BUFFER_SIZE] __attribute__((aligned(8)));
    
    struct pollfd pfd;
    pfd.fd = m_inotifyFd;
    pfd.events = POLLIN;
    
    while (m_running) {
        // 使用poll等待事件，超时100ms
        int ret = poll(&pfd, 1, 100);
        
        if (ret < 0) {
            if (errno != EINTR) {
                std::cerr << "Poll error: " << strerror(errno) << std::endl;
            }
            continue;
        }
        
        if (ret == 0) {
            // 超时，继续
            continue;
        }
        
        // 读取事件
        ssize_t len = read(m_inotifyFd, buffer, BUFFER_SIZE);
        if (len < 0) {
            if (errno != EAGAIN && errno != EWOULDBLOCK) {
                std::cerr << "Read error: " << strerror(errno) << std::endl;
            }
            continue;
        }
        
        // 处理事件
        const char* ptr = buffer;
        while (ptr < buffer + len) {
            const inotify_event* event = reinterpret_cast<const inotify_event*>(ptr);
            handleInotifyEvent(event);
            ptr += sizeof(inotify_event) + event->len;
        }
    }
}

void LinuxInotifyMonitor::processLoop() {
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

int LinuxInotifyMonitor::addWatch(const std::string& path, const MonitorConfig& config) {
    int wd = inotify_add_watch(m_inotifyFd, path.c_str(), WATCH_MASK);
    if (wd < 0) {
        std::cerr << "Failed to add watch for " << path << ": " << strerror(errno) << std::endl;
        return -1;
    }
    
    WatchInfo info;
    info.path = path;
    info.config = config;
    info.wd = wd;
    
    m_watches[wd] = info;
    m_pathToWd[path] = wd;
    
    return wd;
}

void LinuxInotifyMonitor::removeWatch(int wd) {
    auto it = m_watches.find(wd);
    if (it == m_watches.end()) {
        return;
    }
    
    inotify_rm_watch(m_inotifyFd, wd);
    m_pathToWd.erase(it->second.path);
    m_watches.erase(it);
}

void LinuxInotifyMonitor::handleInotifyEvent(const inotify_event* event) {
    std::lock_guard<std::mutex> lock(m_watchMutex);
    
    auto it = m_watches.find(event->wd);
    if (it == m_watches.end()) {
        return;
    }
    
    const WatchInfo& watchInfo = it->second;
    
    // 构建完整路径
    std::string fullPath = watchInfo.path;
    if (event->len > 0) {
        fullPath = fs::path(watchInfo.path) / event->name;
    }
    
    // 检查是否应该忽略
    if (shouldIgnorePath(fullPath, watchInfo.config)) {
        return;
    }
    
    // 如果是目录创建事件，且配置为递归监控，添加新目录
    if ((event->mask & IN_CREATE) && (event->mask & IN_ISDIR) && watchInfo.config.recursive) {
        addWatch(fullPath, watchInfo.config);
    }
    
    // 如果是目录删除事件，移除监控
    if ((event->mask & IN_DELETE) && (event->mask & IN_ISDIR)) {
        auto pathIt = m_pathToWd.find(fullPath);
        if (pathIt != m_pathToWd.end()) {
            removeWatch(pathIt->second);
        }
    }
    
    // 转换事件类型
    FileEventType eventType = maskToEventType(event->mask);
    if (eventType == FileEventType::UNKNOWN) {
        return;
    }
    
    // 创建事件
    FileSystemEvent fsEvent(fullPath, eventType);
    fsEvent.isDirectory = (event->mask & IN_ISDIR) != 0;
    
    // 获取文件信息
    if (!fsEvent.isDirectory && fs::exists(fullPath)) {
        try {
            fsEvent.fileSize = fs::file_size(fullPath);
        } catch (...) {
            // 忽略错误
        }
    }
    
    // 添加到队列
    {
        std::lock_guard<std::mutex> queueLock(m_queueMutex);
        m_eventQueue.push(fsEvent);
        m_queueCV.notify_one();
    }
}

FileEventType LinuxInotifyMonitor::maskToEventType(uint32_t mask) {
    if (mask & IN_CREATE) {
        return FileEventType::CREATED;
    }
    if (mask & IN_DELETE || mask & IN_DELETE_SELF) {
        return FileEventType::DELETED;
    }
    if (mask & IN_MOVED_FROM) {
        return FileEventType::RENAMED_OLD;
    }
    if (mask & IN_MOVED_TO) {
        return FileEventType::RENAMED_NEW;
    }
    if (mask & IN_MODIFY || mask & IN_CLOSE_WRITE || mask & IN_ATTRIB) {
        return FileEventType::MODIFIED;
    }
    
    return FileEventType::UNKNOWN;
}

void LinuxInotifyMonitor::addDirectoryRecursive(const std::string& dirPath, const MonitorConfig& config) {
    // 先添加目录本身
    addWatch(dirPath, config);
    
    // 递归添加子目录
    try {
        for (const auto& entry : fs::recursive_directory_iterator(dirPath)) {
            if (entry.is_directory()) {
                std::string subDir = entry.path().string();
                
                // 检查是否应该跳过这个目录
                if (shouldIgnorePath(subDir, config)) {
                    continue;
                }
                
                addWatch(subDir, config);
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "Error adding recursive watches: " << e.what() << std::endl;
    }
}

void LinuxInotifyMonitor::removeDirectoryRecursive(const std::string& dirPath) {
    // 查找所有以dirPath开头的路径
    std::vector<int> toRemove;
    
    for (const auto& [wd, info] : m_watches) {
        if (info.path.find(dirPath) == 0) {
            toRemove.push_back(wd);
        }
    }
    
    // 移除所有找到的监控
    for (int wd : toRemove) {
        removeWatch(wd);
    }
}

#endif // __linux__