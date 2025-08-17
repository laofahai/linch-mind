#include "filesystem_monitor_adapter.hpp"
#include <iostream>
#include <filesystem>

namespace linch_connector {

namespace fs = std::filesystem;

FilesystemMonitorAdapter::FilesystemMonitorAdapter()
    : m_config(config::FilesystemConfig::createDefault())
    , m_running(false)
{
    std::cout << "📁 文件系统监听适配器初始化（简化模式）" << std::endl;
}

FilesystemMonitorAdapter::~FilesystemMonitorAdapter() {
    stop();
}

bool FilesystemMonitorAdapter::start(std::function<void(ConnectorEvent&&)> callback) {
    if (m_running) {
        return false;
    }

    m_eventCallback = callback;
    m_running = true;
    
    std::cout << "📁 文件系统监听器已启动（简化模式）" << std::endl;
    return true;
}

void FilesystemMonitorAdapter::stop() {
    if (m_running) {
        m_running = false;
        std::cout << "📁 文件系统监听器已停止" << std::endl;
    }
}

bool FilesystemMonitorAdapter::isRunning() const {
    return m_running;
}

IConnectorMonitor::Statistics FilesystemMonitorAdapter::getStatistics() const {
    Statistics stats;
    stats.eventsProcessed = 0;
    stats.eventsFiltered = 0;
    stats.pathsMonitored = 0;
    stats.platformInfo = "简化文件系统监听器";
    stats.startTime = std::chrono::system_clock::now();
    stats.isRunning = m_running;
    return stats;
}

bool FilesystemMonitorAdapter::addPath(const MonitorConfig& config) {
    std::string path = config.settings.value("path", "");
    if (path.empty()) {
        std::cerr << "❌ 监听路径为空" << std::endl;
        return false;
    }
    
    if (!fs::exists(path) || !fs::is_directory(path)) {
        std::cerr << "❌ 监听路径不存在或不是目录: " << path << std::endl;
        return false;
    }
    
    std::cout << "✅ 添加监听路径: " << path << std::endl;
    return true;
}

bool FilesystemMonitorAdapter::removePath(const std::string& path) {
    std::cout << "✅ 移除监听路径: " << path << std::endl;
    return true;
}

std::vector<std::string> FilesystemMonitorAdapter::getMonitoredPaths() const {
    return std::vector<std::string>{};
}

void FilesystemMonitorAdapter::setBatchCallback(std::function<void(std::vector<ConnectorEvent>&&)> callback,
                                               std::chrono::milliseconds interval) {
    m_batchCallback = callback;
    std::cout << "✅ 设置批处理回调，间隔: " << interval.count() << "ms" << std::endl;
}

std::string_view FilesystemMonitorAdapter::getEventTypeString(FileEventType type) const {
    switch (type) {
        case FileEventType::CREATED:     return "created";
        case FileEventType::MODIFIED:    return "modified";
        case FileEventType::DELETED:     return "deleted";
        case FileEventType::RENAMED_OLD: return "renamed_old";
        case FileEventType::RENAMED_NEW: return "renamed_new";
        default:                         return "unknown";
    }
}

bool FilesystemMonitorAdapter::setConfig(const config::FilesystemConfig& config) {
    std::string errorMessage;
    if (!config.validate(errorMessage)) {
        std::cerr << "配置验证失败: " << errorMessage << std::endl;
        return false;
    }
    
    m_config = config;
    std::cout << "✅ " << config.getDescription() << std::endl;
    return true;
}

config::FilesystemConfig FilesystemMonitorAdapter::getConfig() const {
    return m_config;
}

} // namespace linch_connector