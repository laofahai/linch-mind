#include "filesystem_monitor_adapter.hpp"
#include <linch_connector/optimized_event_utils.hpp>
#include <iostream>
#include <filesystem>

namespace linch_connector {

namespace fs = std::filesystem;

FilesystemMonitorAdapter::FilesystemMonitorAdapter()
    : m_monitor(std::make_unique<FileSystemMonitor>(MonitorType::AUTO))
    , m_config(config::FilesystemConfig::createDefault())
{
}

FilesystemMonitorAdapter::~FilesystemMonitorAdapter() {
    stop();
}

bool FilesystemMonitorAdapter::start(std::function<void(ConnectorEvent&&)> callback) {
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

void FilesystemMonitorAdapter::setBatchCallback(std::function<void(std::vector<ConnectorEvent>&&)> callback,
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
        // 🚀 性能优化: 直接使用优化的事件构造工具
        ConnectorEvent connectorEvent = optimization::EventUtils::createFilesystemEvent(
            std::string(event.path),    // 复制路径用于移动
            getEventTypeString(event.type),
            event.isDirectory,
            event.fileSize,
            std::string(event.oldPath)  // 复制旧路径用于移动
        );
        
        // 🚀 性能优化: 使用移动语义传递事件
        m_eventCallback(std::move(connectorEvent));
    }
}

void FilesystemMonitorAdapter::onBatchFileSystemEvents(const std::vector<FileSystemEvent>& events) {
    if (m_batchCallback && !events.empty()) {
        // 🚀 性能优化: 预分配容器并使用零拷贝构造
        auto connectorEvents = optimization::EventUtils::createEventBatch(events.size());
        
        for (const auto& event : events) {
            connectorEvents.emplace_back(
                optimization::EventUtils::createFilesystemEvent(
                    std::string(event.path),
                    getEventTypeString(event.type),
                    event.isDirectory,
                    event.fileSize,
                    std::string(event.oldPath)
                )
            );
        }
        
        // 🚀 性能优化: 使用移动语义传递整个批次
        m_batchCallback(std::move(connectorEvents));
    }
}

std::string_view FilesystemMonitorAdapter::getEventTypeString(FileEventType type) const {
    // 🚀 性能优化: 使用string_view避免字符串分配
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
    
    // 应用配置到监控器
    if (m_monitor) {
        // 清除现有路径
        auto currentPaths = m_monitor->getMonitoredPaths();
        for (const auto& path : currentPaths) {
            m_monitor->removePath(path);
        }
        
        // 添加新配置的路径
        for (const auto& pathConfig : m_config.paths) {
            // 转换为旧式MonitorConfig (向后兼容)
            ::MonitorConfig legacyConfig(pathConfig.path);
            legacyConfig.recursive = pathConfig.recursive;
            legacyConfig.maxFileSize = pathConfig.maxFileSize;
            legacyConfig.includeExtensions = pathConfig.includeExtensions;
            legacyConfig.excludePatterns = pathConfig.excludePatterns;
            legacyConfig.watchDirectories = pathConfig.watchDirectories;
            legacyConfig.watchFiles = pathConfig.watchFiles;
            
            if (!m_monitor->addPath(legacyConfig)) {
                std::cerr << "添加监控路径失败: " << pathConfig.path << std::endl;
            }
        }
        
        // 应用批处理配置
        if (m_batchCallback) {
            auto batchCb = [this](const std::vector<FileSystemEvent>& events) {
                onBatchFileSystemEvents(events);
            };
            m_monitor->setBatchCallback(batchCb, m_config.batchInterval);
        }
    }
    
    std::cout << "✅ " << config.getDescription() << std::endl;
    return true;
}

config::FilesystemConfig FilesystemMonitorAdapter::getConfig() const {
    return m_config;
}

} // namespace linch_connector