#include "filesystem_connector.hpp"
#include <iostream>
#include <chrono>

namespace linch_connector {

FilesystemConnector::FilesystemConnector() 
    : BaseConnector("filesystem", "文件系统连接器 (零扫描)")
    , m_startTime(std::chrono::steady_clock::now())
{
    logInfo("🚀 文件系统连接器初始化 - 零扫描架构");
}

std::unique_ptr<IConnectorMonitor> FilesystemConnector::createMonitor() {
    auto adapter = std::make_unique<FilesystemMonitorAdapter>();
    m_fsAdapter = adapter.get(); // 保存指针以便访问特定功能
    return std::move(adapter);
}

bool FilesystemConnector::loadConnectorConfig() {
    EnhancedConfig enhancedConfig(getConfigManager());
    m_config = enhancedConfig.getFileSystemConfig();
    
    logConfig();
    return true;
}

bool FilesystemConnector::onInitialize() {
    logInfo("📁 文件系统连接器V2初始化完成");
    
    // 显示平台信息
    if (FileIndexProviderFactory::isZeroScanSupported()) {
        logInfo("✅ 当前平台支持零扫描索引: " + FileIndexProviderFactory::getPlatformName());
    } else {
        logWarn("⚠️ 当前平台零扫描索引支持有限");
    }
    
    return true;
}

bool FilesystemConnector::onStart() {
    logInfo("🚀 启动文件系统连接器V2...");
    
    // 设置批处理配置
    setBatchConfig(std::chrono::milliseconds(m_config.batchInterval), 50);
    
    // 1. 首先设置实时监控（用于用户指定目录）
    if (!setupRealtimeMonitoring()) {
        setError("Failed to setup realtime monitoring");
        return false;
    }
    
    // 2. 然后设置零扫描索引（用于全盘快速搜索）
    if (!setupIndexProvider()) {
        logWarn("⚠️ 零扫描索引设置失败，仅启用实时监控");
    }
    
    logInfo("✅ 文件系统连接器V2启动完成");
    logInfo("📊 批处理间隔: " + std::to_string(m_config.batchInterval) + "ms");
    
    return true;
}

void FilesystemConnector::onStop() {
    logInfo("🛑 停止文件系统连接器V2");
    
    // 停止零扫描索引提供者
    if (m_indexProvider) {
        logInfo("🛑 停止零扫描索引提供者...");
        m_indexProvider->stop();
        
        // 显示性能统计
        logPerformanceStats();
    }
    
    // 显示最终统计
    if (m_fsAdapter) {
        auto paths = m_fsAdapter->getMonitoredPaths();
        logInfo("📊 实时监控了 " + std::to_string(paths.size()) + " 个路径");
    }
    
    logInfo("📊 总索引文件数: " + std::to_string(m_totalIndexedFiles.load()));
}

bool FilesystemConnector::setupRealtimeMonitoring() {
    if (!m_fsAdapter) {
        logError("文件系统适配器未初始化");
        return false;
    }
    
    logInfo("⚡ 设置实时文件监控...");
    
    int successCount = 0;
    int totalCount = static_cast<int>(m_config.watchDirectories.size());
    
    // 设置实时监控路径（通常是用户指定的重要目录）
    for (const std::string& path : m_config.watchDirectories) {
        MonitorConfig monitorConfig;
        monitorConfig.name = "realtime_" + std::to_string(successCount);
        monitorConfig.set("path", path);
        monitorConfig.set("recursive", m_config.recursive);
        monitorConfig.set("max_file_size", m_config.maxFileSize);
        
        // 设置包含的扩展名
        json includeExts = json::array();
        for (const auto& ext : m_config.includeExtensions) {
            includeExts.push_back(ext);
        }
        monitorConfig.set("include_extensions", includeExts);
        
        // 设置排除模式
        json excludePatterns = json::array();
        for (const auto& pattern : m_config.excludePatterns) {
            excludePatterns.push_back(pattern);
        }
        monitorConfig.set("exclude_patterns", excludePatterns);
        
        if (m_fsAdapter->addPath(monitorConfig)) {
            logInfo("✅ 实时监控: " + path);
            successCount++;
        } else {
            logError("❌ 实时监控失败: " + path);
        }
    }
    
    if (successCount > 0) {
        m_realtimeActive = true;
        logInfo("⚡ 实时监控设置完成: " + std::to_string(successCount) + "/" + 
                std::to_string(totalCount) + " 个路径");
        return true;
    } else {
        logWarn("⚠️ 没有成功设置任何实时监控路径");
        return false;
    }
}

bool FilesystemConnector::setupIndexProvider() {
    try {
        logInfo("🔍 初始化零扫描索引提供者...");
        
        // 创建平台特定的索引提供者
        m_indexProvider = FileIndexProviderFactory::createProvider();
        if (!m_indexProvider) {
            logError("❌ 无法创建索引提供者");
            return false;
        }
        
        // 检查可用性
        if (!m_indexProvider->isAvailable()) {
            logWarn("⚠️ 索引提供者不可用: " + m_indexProvider->getPlatformInfo());
            return false;
        }
        
        logInfo("📋 平台信息: " + m_indexProvider->getPlatformInfo());
        
        // 设置回调函数
        m_indexProvider->setInitialBatchCallback(
            [this](const std::vector<FileInfo>& files) {
                onInitialBatch(files);
            });
        
        m_indexProvider->setFileEventCallback(
            [this](const FileEvent& event) {
                onFileEvent(event);
            });
        
        m_indexProvider->setProgressCallback(
            [this](uint64_t indexed, uint64_t total) {
                onIndexProgress(indexed, total);
            });
        
        // 设置监控目录（通常是用户主目录或全盘）
        std::vector<std::string> indexDirectories;
        const char* homeDir = getenv("HOME");
        if (homeDir) {
            indexDirectories.push_back(std::string(homeDir));
        }
        m_indexProvider->setWatchDirectories(indexDirectories);
        
        // 设置排除模式 (转换set到vector)
        std::vector<std::string> excludePatterns(m_config.excludePatterns.begin(), m_config.excludePatterns.end());
        m_indexProvider->setExcludePatterns(excludePatterns);
        
        // 启动初始化
        if (!m_indexProvider->initialize()) {
            logError("❌ 索引提供者初始化失败");
            return false;
        }
        
        // 启动变更监控
        if (!m_indexProvider->watchChanges()) {
            logWarn("⚠️ 索引变更监控启动失败");
            return false;
        }
        
        logInfo("✅ 零扫描索引提供者启动成功");
        return true;
        
    } catch (const std::exception& e) {
        logError("❌ 设置索引提供者失败: " + std::string(e.what()));
        m_indexProvider.reset();
        return false;
    }
}

void FilesystemConnector::onInitialBatch(const std::vector<FileInfo>& files) {
    if (files.empty()) return;
    
    try {
        logInfo("📦 收到初始索引批次: " + std::to_string(files.size()) + " 个文件");
        
        // 转换为连接器事件并批量发送
        sendFileInfoBatch(files);
        
        // 更新统计
        m_totalIndexedFiles += files.size();
        
    } catch (const std::exception& e) {
        logError("❌ 处理初始批次失败: " + std::string(e.what()));
    }
}

void FilesystemConnector::onFileEvent(const FileEvent& event) {
    try {
        // 转换文件事件为连接器事件
        ConnectorEvent connectorEvent = convertFileEventToEvent(event);
        
        // 发送单个事件
        sendEvent(std::move(connectorEvent));
        
        logInfo("📄 索引变更事件: " + event.path + " (" + 
                (event.type == FileEventType::CREATED ? "创建" :
                 event.type == FileEventType::MODIFIED ? "修改" :
                 event.type == FileEventType::DELETED ? "删除" : "其他") + ")");
        
    } catch (const std::exception& e) {
        logError("❌ 处理文件事件失败: " + std::string(e.what()));
    }
}

void FilesystemConnector::onIndexProgress(uint64_t indexed, uint64_t total) {
    // 每隔一定数量报告进度
    static uint64_t lastReported = 0;
    if (indexed - lastReported >= 10000 || (total > 0 && indexed == total)) {
        lastReported = indexed;
        
        if (total > 0) {
            double progress = static_cast<double>(indexed) / total * 100.0;
            logInfo("📊 索引进度: " + std::to_string(indexed) + "/" + 
                   std::to_string(total) + " (" + 
                   std::to_string(static_cast<int>(progress)) + "%)");
        } else {
            logInfo("📊 已索引: " + std::to_string(indexed) + " 个文件");
        }
    }
}

void FilesystemConnector::sendFileInfoBatch(const std::vector<FileInfo>& files) {
    std::vector<ConnectorEvent> events;
    events.reserve(files.size());
    
    for (const auto& fileInfo : files) {
        ConnectorEvent event = convertFileInfoToEvent(fileInfo, "file_indexed");
        events.emplace_back(std::move(event));
    }
    
    // 批量发送事件
    sendBatchEvents(events);
}

ConnectorEvent FilesystemConnector::convertFileInfoToEvent(const FileInfo& fileInfo, const std::string& eventType) {
    nlohmann::json eventData;
    eventData["path"] = fileInfo.path;
    eventData["name"] = fileInfo.name;
    eventData["extension"] = fileInfo.extension;
    eventData["size"] = fileInfo.size;
    eventData["is_directory"] = fileInfo.is_directory;
    eventData["source"] = "index_provider";
    
    // 添加时间戳
    auto timeT = std::chrono::system_clock::to_time_t(fileInfo.modified_time);
    eventData["modified_time"] = timeT;
    
    return ConnectorEvent::create(getId(), eventType, std::move(eventData));
}

ConnectorEvent FilesystemConnector::convertFileEventToEvent(const FileEvent& fileEvent) {
    std::string eventType;
    switch (fileEvent.type) {
        case FileEventType::CREATED:  eventType = "file_created"; break;
        case FileEventType::MODIFIED: eventType = "file_modified"; break;
        case FileEventType::DELETED:  eventType = "file_deleted"; break;
        case FileEventType::RENAMED:  eventType = "file_renamed"; break;
        case FileEventType::MOVED:    eventType = "file_moved"; break;
        default: eventType = "file_changed"; break;
    }
    
    nlohmann::json eventData;
    eventData["path"] = fileEvent.path;
    eventData["source"] = "index_provider_realtime";
    
    if (!fileEvent.old_path.empty()) {
        eventData["old_path"] = fileEvent.old_path;
    }
    
    // 对于创建和修改事件，包含文件信息
    if (fileEvent.type == FileEventType::CREATED || fileEvent.type == FileEventType::MODIFIED) {
        eventData["name"] = fileEvent.file_info.name;
        eventData["extension"] = fileEvent.file_info.extension;
        eventData["size"] = fileEvent.file_info.size;
        eventData["is_directory"] = fileEvent.file_info.is_directory;
        
        auto timeT = std::chrono::system_clock::to_time_t(fileEvent.file_info.modified_time);
        eventData["modified_time"] = timeT;
    }
    
    auto eventTimeT = std::chrono::system_clock::to_time_t(fileEvent.timestamp);
    eventData["event_time"] = eventTimeT;
    
    return ConnectorEvent::create(getId(), eventType, std::move(eventData));
}

void FilesystemConnector::logConfig() {
    logInfo("📋 文件系统连接器V2配置:");
    logInfo("   实时监控目录: " + std::to_string(m_config.watchDirectories.size()) + " 个");
    for (const auto& dir : m_config.watchDirectories) {
        logInfo("     - " + dir);
    }
    logInfo("   包含扩展名: " + std::to_string(m_config.includeExtensions.size()) + " 个");
    logInfo("   排除模式: " + std::to_string(m_config.excludePatterns.size()) + " 个");
    logInfo("   最大文件大小: " + std::to_string(m_config.maxFileSize) + "MB");
    logInfo("   递归监控: " + std::string(m_config.recursive ? "是" : "否"));
    logInfo("   批处理间隔: " + std::to_string(m_config.batchInterval) + "ms");
    logInfo("   零扫描索引: " + std::string(FileIndexProviderFactory::isZeroScanSupported() ? "支持" : "有限"));
}

void FilesystemConnector::logPerformanceStats() {
    auto endTime = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::seconds>(endTime - m_startTime);
    
    uint64_t totalFiles = m_totalIndexedFiles.load();
    
    logInfo("📊 性能统计:");
    logInfo("   运行时间: " + std::to_string(duration.count()) + " 秒");
    logInfo("   索引文件数: " + std::to_string(totalFiles) + " 个");
    
    if (duration.count() > 0) {
        double filesPerSecond = static_cast<double>(totalFiles) / duration.count();
        logInfo("   平均索引速度: " + std::to_string(static_cast<int>(filesPerSecond)) + " 文件/秒");
    }
    
    if (m_indexProvider) {
        IndexStats stats = m_indexProvider->getStats();
        logInfo("   内存使用: " + std::to_string(stats.memory_usage_mb) + " MB");
        logInfo("   初始化状态: " + std::string(stats.is_initialized ? "完成" : "未完成"));
        logInfo("   监控状态: " + std::string(stats.is_watching ? "活跃" : "停止"));
    }
}

} // namespace linch_connector