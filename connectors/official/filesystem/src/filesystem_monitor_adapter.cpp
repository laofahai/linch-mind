#include "filesystem_monitor_adapter.hpp"
#include <iostream>
#include <filesystem>

namespace linch_connector {

namespace fs = std::filesystem;

FilesystemMonitorAdapter::FilesystemMonitorAdapter()
    : m_monitor(std::make_unique<FileSystemMonitor>(MonitorType::AUTO))
{
}

FilesystemMonitorAdapter::~FilesystemMonitorAdapter() {
    stop();
}

bool FilesystemMonitorAdapter::start(std::function<void(const ConnectorEvent&)> callback) {
    if (isRunning()) {
        return false;
    }

    m_eventCallback = callback;
    
    // 设置单个事件回调
    auto eventCb = [this](const FileSystemEvent& event) {
        onFileSystemEvent(event);
    };
    
    return m_monitor->start(eventCb);
}

void FilesystemMonitorAdapter::stop() {
    if (m_monitor) {
        m_monitor->stop();
    }
}

bool FilesystemMonitorAdapter::isRunning() const {
    return m_monitor && m_monitor->isRunning();
}

IConnectorMonitor::Statistics FilesystemMonitorAdapter::getStatistics() const {
    if (!m_monitor) {
        return Statistics{};
    }
    
    auto fsStats = m_monitor->getStatistics();
    
    Statistics stats;
    stats.eventsProcessed = fsStats.eventsProcessed;
    stats.eventsFiltered = fsStats.eventsFiltered;
    stats.pathsMonitored = fsStats.pathsMonitored;
    stats.platformInfo = fsStats.platformInfo;
    stats.startTime = fsStats.startTime;
    stats.isRunning = fsStats.isRunning;
    
    return stats;
}

bool FilesystemMonitorAdapter::addPath(const MonitorConfig& config) {
    if (!m_monitor) {
        return false;
    }
    
    // 将统一的MonitorConfig转换为FileSystemMonitor的MonitorConfig
    ::MonitorConfig fsConfig(config.get<std::string>("path", ""));
    
    // 从配置中读取各种设置
    fsConfig.recursive = config.get<bool>("recursive", true);
    fsConfig.maxFileSize = config.get<int>("max_file_size", 50) * 1024 * 1024; // MB转字节
    
    // 读取扩展名集合
    if (config.settings.contains("include_extensions") && config.settings["include_extensions"].is_array()) {
        for (const auto& ext : config.settings["include_extensions"]) {
            if (ext.is_string()) {
                fsConfig.includeExtensions.insert(ext.get<std::string>());
            }
        }
    }
    
    // 读取排除模式
    if (config.settings.contains("exclude_patterns") && config.settings["exclude_patterns"].is_array()) {
        for (const auto& pattern : config.settings["exclude_patterns"]) {
            if (pattern.is_string()) {
                fsConfig.excludePatterns.insert(pattern.get<std::string>());
            }
        }
    }
    
    return m_monitor->addPath(fsConfig);
}

bool FilesystemMonitorAdapter::removePath(const std::string& path) {
    return m_monitor ? m_monitor->removePath(path) : false;
}

std::vector<std::string> FilesystemMonitorAdapter::getMonitoredPaths() const {
    return m_monitor ? m_monitor->getMonitoredPaths() : std::vector<std::string>{};
}

void FilesystemMonitorAdapter::setBatchCallback(std::function<void(const std::vector<ConnectorEvent>&)> callback,
                                               std::chrono::milliseconds interval) {
    m_batchCallback = callback;
    
    if (m_monitor) {
        auto batchCb = [this](const std::vector<FileSystemEvent>& events) {
            onBatchFileSystemEvents(events);
        };
        
        m_monitor->setBatchCallback(batchCb, interval);
    }
}

void FilesystemMonitorAdapter::onFileSystemEvent(const FileSystemEvent& event) {
    if (m_eventCallback) {
        ConnectorEvent connectorEvent = convertFileSystemEvent(event);
        m_eventCallback(connectorEvent);
    }
}

void FilesystemMonitorAdapter::onBatchFileSystemEvents(const std::vector<FileSystemEvent>& events) {
    if (m_batchCallback && !events.empty()) {
        std::vector<ConnectorEvent> connectorEvents;
        connectorEvents.reserve(events.size());
        
        for (const auto& event : events) {
            connectorEvents.push_back(convertFileSystemEvent(event));
        }
        
        m_batchCallback(connectorEvents);
    }
}

ConnectorEvent FilesystemMonitorAdapter::convertFileSystemEvent(const FileSystemEvent& event) const {
    fs::path filePath(event.path);
    
    std::string eventTypeStr;
    switch (event.type) {
        case FileEventType::CREATED:
            eventTypeStr = "created";
            break;
        case FileEventType::MODIFIED:
            eventTypeStr = "modified";
            break;
        case FileEventType::DELETED:
            eventTypeStr = "deleted";
            break;
        case FileEventType::RENAMED_OLD:
            eventTypeStr = "renamed_old";
            break;
        case FileEventType::RENAMED_NEW:
            eventTypeStr = "renamed_new";
            break;
        default:
            eventTypeStr = "unknown";
            break;
    }
    
    // 创建文件事件数据
    json eventData = {
        {"file_path", event.path},
        {"file_name", filePath.filename().string()},
        {"extension", filePath.extension().string()},
        {"directory", filePath.parent_path().string()},
        {"is_directory", event.isDirectory}
    };
    
    // 如果文件存在，添加大小信息
    if (!event.isDirectory && event.fileSize > 0) {
        eventData["size"] = event.fileSize;
    }
    
    // 如果有旧路径（重命名事件）
    if (!event.oldPath.empty()) {
        eventData["old_path"] = event.oldPath;
    }
    
    return ConnectorEvent::create("filesystem", eventTypeStr, eventData);
}

} // namespace linch_connector