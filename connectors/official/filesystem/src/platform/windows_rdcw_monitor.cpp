#ifdef _WIN32

#include "windows_rdcw_monitor.hpp"
#include <iostream>
#include <algorithm>
#include <codecvt>
#include <locale>

WindowsRDCWMonitor::WindowsRDCWMonitor()
    : m_debouncer(std::make_unique<EventDebouncer>(std::chrono::milliseconds(300))) {
}

WindowsRDCWMonitor::~WindowsRDCWMonitor() {
    stop();
}

bool WindowsRDCWMonitor::start(EventCallback callback) {
    if (m_running) {
        return false;
    }
    
    // 创建IOCP
    m_iocpHandle = CreateIoCompletionPort(INVALID_HANDLE_VALUE, NULL, 0, 0);
    if (m_iocpHandle == NULL) {
        std::cerr << "Failed to create IOCP: " << GetLastError() << std::endl;
        return false;
    }
    
    m_eventCallback = callback;
    m_running = true;
    
    // 启动事件循环线程
    m_eventThread = std::thread(&WindowsRDCWMonitor::eventLoop, this);
    
    // 启动事件处理线程
    m_processThread = std::thread(&WindowsRDCWMonitor::processLoop, this);
    
    return true;
}

void WindowsRDCWMonitor::stop() {
    if (!m_running) {
        return;
    }
    
    m_running = false;
    
    // 发送退出信号到IOCP
    if (m_iocpHandle != INVALID_HANDLE_VALUE) {
        PostQueuedCompletionStatus(m_iocpHandle, 0, 0, NULL);
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
    {
        std::lock_guard<std::mutex> lock(m_watchMutex);
        for (auto& [path, watchInfo] : m_watches) {
            if (watchInfo->hDir != INVALID_HANDLE_VALUE) {
                CancelIo(watchInfo->hDir);
                CloseHandle(watchInfo->hDir);
            }
        }
        m_watches.clear();
    }
    
    // 关闭IOCP
    if (m_iocpHandle != INVALID_HANDLE_VALUE) {
        CloseHandle(m_iocpHandle);
        m_iocpHandle = INVALID_HANDLE_VALUE;
    }
}

bool WindowsRDCWMonitor::addPath(const MonitorConfig& config) {
    if (m_iocpHandle == INVALID_HANDLE_VALUE) {
        return false;
    }
    
    std::lock_guard<std::mutex> lock(m_watchMutex);
    
    // 检查路径是否已存在
    if (m_watches.find(config.path) != m_watches.end()) {
        // 更新配置
        m_watches[config.path]->config = config;
        return true;
    }
    
    return addWatchInternal(config);
}

bool WindowsRDCWMonitor::removePath(const std::string& path) {
    std::lock_guard<std::mutex> lock(m_watchMutex);
    
    auto it = m_watches.find(path);
    if (it == m_watches.end()) {
        return false;
    }
    
    removeWatchInternal(path);
    return true;
}

std::vector<std::string> WindowsRDCWMonitor::getMonitoredPaths() const {
    std::lock_guard<std::mutex> lock(m_watchMutex);
    std::vector<std::string> paths;
    paths.reserve(m_watches.size());
    
    for (const auto& [path, watchInfo] : m_watches) {
        paths.push_back(path);
    }
    
    return paths;
}

void WindowsRDCWMonitor::eventLoop() {
    while (m_running) {
        DWORD bytesTransferred = 0;
        ULONG_PTR completionKey = 0;
        LPOVERLAPPED pOverlapped = NULL;
        
        // 等待完成事件，超时100ms
        BOOL result = GetQueuedCompletionStatus(
            m_iocpHandle,
            &bytesTransferred,
            &completionKey,
            &pOverlapped,
            100
        );
        
        if (!result) {
            DWORD error = GetLastError();
            if (error == WAIT_TIMEOUT) {
                continue;
            }
            
            if (error != ERROR_OPERATION_ABORTED) {
                std::cerr << "GetQueuedCompletionStatus error: " << error << std::endl;
            }
            continue;
        }
        
        // 检查退出信号
        if (completionKey == 0 && pOverlapped == NULL) {
            break;
        }
        
        // 处理文件系统事件
        WatchInfo* watchInfo = reinterpret_cast<WatchInfo*>(completionKey);
        if (watchInfo && watchInfo->active) {
            handleCompletionStatus(watchInfo, bytesTransferred);
        }
    }
}

void WindowsRDCWMonitor::processLoop() {
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

bool WindowsRDCWMonitor::addWatchInternal(const MonitorConfig& config) {
    auto watchInfo = std::make_unique<WatchInfo>();
    watchInfo->path = config.path;
    watchInfo->config = config;
    watchInfo->buffer.resize(64 * 1024);  // 64KB缓冲区
    watchInfo->active = true;
    
    // 打开目录句柄
    watchInfo->hDir = CreateFileW(
        std::wstring(config.path.begin(), config.path.end()).c_str(),
        FILE_LIST_DIRECTORY,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        NULL,
        OPEN_EXISTING,
        FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OVERLAPPED,
        NULL
    );
    
    if (watchInfo->hDir == INVALID_HANDLE_VALUE) {
        std::cerr << "Failed to open directory " << config.path << ": " << GetLastError() << std::endl;
        return false;
    }
    
    // 关联到IOCP
    if (CreateIoCompletionPort(watchInfo->hDir, m_iocpHandle, 
                              reinterpret_cast<ULONG_PTR>(watchInfo.get()), 0) == NULL) {
        std::cerr << "Failed to associate handle with IOCP: " << GetLastError() << std::endl;
        CloseHandle(watchInfo->hDir);
        return false;
    }
    
    // 初始化OVERLAPPED结构
    ZeroMemory(&watchInfo->overlapped, sizeof(OVERLAPPED));
    
    // 开始监控
    startMonitoring(watchInfo.get());
    
    // 保存监控信息
    m_watches[config.path] = std::move(watchInfo);
    
    return true;
}

void WindowsRDCWMonitor::removeWatchInternal(const std::string& path) {
    auto it = m_watches.find(path);
    if (it == m_watches.end()) {
        return;
    }
    
    auto& watchInfo = it->second;
    watchInfo->active = false;
    
    if (watchInfo->hDir != INVALID_HANDLE_VALUE) {
        CancelIo(watchInfo->hDir);
        CloseHandle(watchInfo->hDir);
        watchInfo->hDir = INVALID_HANDLE_VALUE;
    }
    
    m_watches.erase(it);
}

void WindowsRDCWMonitor::startMonitoring(WatchInfo* watchInfo) {
    if (!watchInfo->active || watchInfo->hDir == INVALID_HANDLE_VALUE) {
        return;
    }
    
    DWORD bytesReturned = 0;
    BOOL result = ReadDirectoryChangesW(
        watchInfo->hDir,
        watchInfo->buffer.data(),
        static_cast<DWORD>(watchInfo->buffer.size()),
        watchInfo->config.recursive ? TRUE : FALSE,
        WATCH_FLAGS,
        &bytesReturned,
        &watchInfo->overlapped,
        NULL
    );
    
    if (!result) {
        DWORD error = GetLastError();
        if (error != ERROR_IO_PENDING) {
            std::cerr << "ReadDirectoryChangesW failed: " << error << std::endl;
        }
    }
}

void WindowsRDCWMonitor::handleCompletionStatus(WatchInfo* watchInfo, DWORD bytesTransferred) {
    if (bytesTransferred == 0) {
        // 缓冲区溢出或其他错误
        return;
    }
    
    // 处理通知
    FILE_NOTIFY_INFORMATION* pNotify = reinterpret_cast<FILE_NOTIFY_INFORMATION*>(watchInfo->buffer.data());
    processNotifications(watchInfo, pNotify);
    
    // 继续监控
    if (watchInfo->active) {
        startMonitoring(watchInfo);
    }
}

void WindowsRDCWMonitor::processNotifications(WatchInfo* watchInfo, FILE_NOTIFY_INFORMATION* pNotify) {
    while (pNotify) {
        // 转换文件名
        std::wstring wFileName(pNotify->FileName, pNotify->FileNameLength / sizeof(WCHAR));
        std::string fileName = wideToUtf8(wFileName);
        
        // 构建完整路径
        fs::path fullPath = fs::path(watchInfo->path) / fileName;
        std::string fullPathStr = fullPath.string();
        
        // 检查是否应该忽略
        if (shouldIgnorePath(fullPathStr, watchInfo->config)) {
            goto next;
        }
        
        // 转换事件类型
        {
            FileEventType eventType = actionToEventType(pNotify->Action);
            if (eventType != FileEventType::UNKNOWN) {
                // 创建事件
                FileSystemEvent event(fullPathStr, eventType);
                
                // 获取文件信息
                try {
                    if (fs::exists(fullPath)) {
                        event.isDirectory = fs::is_directory(fullPath);
                        if (!event.isDirectory) {
                            event.fileSize = fs::file_size(fullPath);
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
        }
        
    next:
        // 移动到下一个通知
        if (pNotify->NextEntryOffset == 0) {
            break;
        }
        pNotify = reinterpret_cast<FILE_NOTIFY_INFORMATION*>(
            reinterpret_cast<BYTE*>(pNotify) + pNotify->NextEntryOffset);
    }
}

FileEventType WindowsRDCWMonitor::actionToEventType(DWORD action) {
    switch (action) {
        case FILE_ACTION_ADDED:
            return FileEventType::CREATED;
        case FILE_ACTION_REMOVED:
            return FileEventType::DELETED;
        case FILE_ACTION_MODIFIED:
            return FileEventType::MODIFIED;
        case FILE_ACTION_RENAMED_OLD_NAME:
            return FileEventType::RENAMED_OLD;
        case FILE_ACTION_RENAMED_NEW_NAME:
            return FileEventType::RENAMED_NEW;
        default:
            return FileEventType::UNKNOWN;
    }
}

std::string WindowsRDCWMonitor::wideToUtf8(const std::wstring& wstr) {
    if (wstr.empty()) {
        return std::string();
    }
    
    int size = WideCharToMultiByte(CP_UTF8, 0, wstr.c_str(), -1, NULL, 0, NULL, NULL);
    if (size == 0) {
        return std::string();
    }
    
    std::string result(size - 1, '\0');
    WideCharToMultiByte(CP_UTF8, 0, wstr.c_str(), -1, &result[0], size, NULL, NULL);
    return result;
}

#endif // _WIN32