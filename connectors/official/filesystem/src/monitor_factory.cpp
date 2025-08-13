#include "monitor_factory.hpp"

// 平台特定头文件
#ifdef __APPLE__
#include "platform/macos_fsevents_monitor.hpp"
#endif

#ifdef __linux__
#include "platform/linux_inotify_monitor.hpp"
#endif

#ifdef _WIN32
#include "platform/windows_rdcw_monitor.hpp"
#endif

#include <iostream>
#include <sstream>

// 简单的轮询监控器实现（后备方案）
class PollingMonitor : public INativeMonitor {
public:
    PollingMonitor() : m_debouncer(std::make_unique<EventDebouncer>(std::chrono::milliseconds(500))) {}
    
    bool start(EventCallback callback) override {
        // 简化的轮询实现 - 这里只是占位符
        // 在实际使用中，应该实现完整的轮询逻辑
        m_eventCallback = callback;
        m_running = true;
        return true;
    }
    
    void stop() override {
        m_running = false;
    }
    
    bool isRunning() const override {
        return m_running;
    }
    
    bool addPath(const MonitorConfig& config) override {
        m_configs.push_back(config);
        return true;
    }
    
    bool removePath(const std::string& path) override {
        auto it = std::find_if(m_configs.begin(), m_configs.end(),
            [&path](const MonitorConfig& c) { return c.path == path; });
        if (it != m_configs.end()) {
            m_configs.erase(it);
            return true;
        }
        return false;
    }
    
    std::vector<std::string> getMonitoredPaths() const override {
        std::vector<std::string> paths;
        for (const auto& config : m_configs) {
            paths.push_back(config.path);
        }
        return paths;
    }
    
private:
    std::vector<MonitorConfig> m_configs;
    std::unique_ptr<EventDebouncer> m_debouncer;
};

// MonitorFactory 实现

std::unique_ptr<INativeMonitor> MonitorFactory::createMonitor(MonitorType type) {
    if (type == MonitorType::AUTO) {
        type = getRecommendedType();
    }
    
    try {
        switch (type) {
            case MonitorType::NATIVE:
#ifdef __APPLE__
                return createMacOSMonitor();
#elif defined(__linux__)
                return createLinuxMonitor();
#elif defined(_WIN32)
                return createWindowsMonitor();
#else
                std::cerr << "Native monitor not supported on this platform, falling back to polling" << std::endl;
                return createPollingMonitor();
#endif
                
            case MonitorType::POLLING:
                return createPollingMonitor();
                
            default:
                return createPollingMonitor();
        }
    } catch (const std::exception& e) {
        std::cerr << "Failed to create monitor: " << e.what() 
                  << ", falling back to polling monitor" << std::endl;
        return createPollingMonitor();
    }
}

MonitorType MonitorFactory::getRecommendedType() {
#if defined(__APPLE__) || defined(__linux__) || defined(_WIN32)
    return MonitorType::NATIVE;
#else
    return MonitorType::POLLING;
#endif
}

bool MonitorFactory::isTypeSupported(MonitorType type) {
    switch (type) {
        case MonitorType::POLLING:
            return true;  // 轮询总是支持的
            
        case MonitorType::NATIVE:
#if defined(__APPLE__) || defined(__linux__) || defined(_WIN32)
            return true;
#else
            return false;
#endif
            
        case MonitorType::AUTO:
            return true;  // AUTO总是支持的，会回退到支持的类型
            
        default:
            return false;
    }
}

std::string MonitorFactory::getPlatformInfo() {
    std::ostringstream oss;
    
#ifdef __APPLE__
    oss << "macOS (FSEvents API)";
#elif defined(__linux__)
    oss << "Linux (inotify API)";
#elif defined(_WIN32)
    oss << "Windows (ReadDirectoryChangesW API)";
#else
    oss << "Unknown platform (polling only)";
#endif
    
    return oss.str();
}

#ifdef __APPLE__
std::unique_ptr<INativeMonitor> MonitorFactory::createMacOSMonitor() {
    return std::make_unique<MacOSFSEventsMonitor>();
}
#endif

#ifdef __linux__
std::unique_ptr<INativeMonitor> MonitorFactory::createLinuxMonitor() {
    return std::make_unique<LinuxInotifyMonitor>();
}
#endif

#ifdef _WIN32
std::unique_ptr<INativeMonitor> MonitorFactory::createWindowsMonitor() {
    return std::make_unique<WindowsRDCWMonitor>();
}
#endif

std::unique_ptr<INativeMonitor> MonitorFactory::createPollingMonitor() {
    return std::make_unique<PollingMonitor>();
}

// FileSystemMonitor 实现

FileSystemMonitor::FileSystemMonitor(MonitorType type) {
    m_monitor = MonitorFactory::createMonitor(type);
    m_stats.monitorType = type;
    m_stats.platformInfo = MonitorFactory::getPlatformInfo();
}

FileSystemMonitor::~FileSystemMonitor() {
    stop();
}

FileSystemMonitor::FileSystemMonitor(FileSystemMonitor&& other) noexcept 
    : m_monitor(std::move(other.m_monitor)), m_stats(other.m_stats) {
}

FileSystemMonitor& FileSystemMonitor::operator=(FileSystemMonitor&& other) noexcept {
    if (this != &other) {
        stop();
        m_monitor = std::move(other.m_monitor);
        m_stats = other.m_stats;
    }
    return *this;
}

bool FileSystemMonitor::start(EventCallback callback) {
    if (!m_monitor) {
        return false;
    }
    
    // 包装回调以更新统计信息
    auto wrappedCallback = [this, callback](const FileSystemEvent& event) {
        {
            std::lock_guard<std::mutex> lock(m_statsMutex);
            m_stats.eventsProcessed++;
        }
        callback(event);
    };
    
    bool result = m_monitor->start(wrappedCallback);
    if (result) {
        std::lock_guard<std::mutex> lock(m_statsMutex);
        m_stats.startTime = std::chrono::system_clock::now();
        m_stats.isRunning = true;
    }
    
    return result;
}

void FileSystemMonitor::stop() {
    if (m_monitor) {
        m_monitor->stop();
        std::lock_guard<std::mutex> lock(m_statsMutex);
        m_stats.isRunning = false;
    }
}

bool FileSystemMonitor::isRunning() const {
    return m_monitor && m_monitor->isRunning();
}

bool FileSystemMonitor::addPath(const MonitorConfig& config) {
    if (!validateConfig(config)) {
        return false;
    }
    
    bool result = m_monitor && m_monitor->addPath(config);
    if (result) {
        updateStats();
    }
    return result;
}

bool FileSystemMonitor::removePath(const std::string& path) {
    bool result = m_monitor && m_monitor->removePath(path);
    if (result) {
        updateStats();
    }
    return result;
}

std::vector<std::string> FileSystemMonitor::getMonitoredPaths() const {
    return m_monitor ? m_monitor->getMonitoredPaths() : std::vector<std::string>{};
}

void FileSystemMonitor::setBatchCallback(BatchEventCallback callback, std::chrono::milliseconds interval) {
    if (m_monitor) {
        m_monitor->setBatchCallback(callback, interval);
    }
}

FileSystemMonitor::Statistics FileSystemMonitor::getStatistics() const {
    std::lock_guard<std::mutex> lock(m_statsMutex);
    return m_stats;
}

bool FileSystemMonitor::validateConfig(const MonitorConfig& config) {
    // 检查路径是否存在
    if (!fs::exists(config.path)) {
        std::cerr << "Path does not exist: " << config.path << std::endl;
        return false;
    }
    
    // 检查是否是目录
    if (!fs::is_directory(config.path)) {
        std::cerr << "Path is not a directory: " << config.path << std::endl;
        return false;
    }
    
    // 检查最大文件大小
    if (config.maxFileSize == 0) {
        std::cerr << "Max file size must be greater than 0" << std::endl;
        return false;
    }
    
    return true;
}

MonitorConfig FileSystemMonitor::createDefaultConfig(const std::string& path) {
    MonitorConfig config(path);
    
    // 设置默认的包含扩展名
    config.includeExtensions = {
        ".txt", ".md", ".pdf", ".doc", ".docx",
        ".xls", ".xlsx", ".ppt", ".pptx",
        ".cpp", ".hpp", ".c", ".h", ".py", ".js", ".ts",
        ".json", ".xml", ".html", ".css"
    };
    
    // 设置默认排除模式
    config.excludePatterns = {
        "*.tmp", "*.log", "*.cache", "*.backup",
        "~*", "#*#", ".#*"
    };
    
    // 50MB最大文件大小
    config.maxFileSize = 50 * 1024 * 1024;
    
    // 默认递归监控
    config.recursive = true;
    
    return config;
}

void FileSystemMonitor::updateStats() {
    std::lock_guard<std::mutex> lock(m_statsMutex);
    m_stats.pathsMonitored = getMonitoredPaths().size();
}