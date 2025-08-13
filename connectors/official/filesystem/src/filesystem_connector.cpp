#include "filesystem_connector.hpp"
#include <iostream>

namespace linch_connector {

FilesystemConnector::FilesystemConnector() 
    : BaseConnector("filesystem", "文件系统连接器")
{
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
    logInfo("📁 文件系统连接器初始化完成");
    
    // 显示监控器信息
    if (m_fsAdapter) {
        auto stats = m_fsAdapter->getStatistics();
        logInfo("🔧 使用监控器: " + stats.platformInfo);
    }
    
    return true;
}

bool FilesystemConnector::onStart() {
    // 设置批处理配置
    setBatchConfig(std::chrono::milliseconds(m_config.batchInterval), 50);
    
    // 如果有文件系统适配器，设置其批量回调
    if (m_fsAdapter) {
        auto batchCallback = [this](const std::vector<ConnectorEvent>& events) {
            sendBatchEvents(events);
        };
        m_fsAdapter->setBatchCallback(batchCallback, std::chrono::milliseconds(m_config.batchInterval));
    }
    
    // 设置监控路径
    if (!setupWatchPaths()) {
        setError("Failed to setup watch paths");
        return false;
    }
    
    logInfo("📁 文件系统监控已启动");
    logInfo("📊 批处理间隔: " + std::to_string(m_config.batchInterval) + "ms");
    
    return true;
}

void FilesystemConnector::onStop() {
    logInfo("📁 文件系统监控已停止");
    
    // 显示最终监控路径统计
    if (m_fsAdapter) {
        auto paths = m_fsAdapter->getMonitoredPaths();
        logInfo("📊 监控了 " + std::to_string(paths.size()) + " 个路径");
    }
}

bool FilesystemConnector::setupWatchPaths() {
    if (!m_fsAdapter) {
        logError("文件系统适配器未初始化");
        return false;
    }
    
    int successCount = 0;
    int totalCount = static_cast<int>(m_config.watchDirectories.size());
    
    for (const std::string& path : m_config.watchDirectories) {
        // 创建监控配置
        MonitorConfig monitorConfig;
        monitorConfig.name = "watch_" + std::to_string(successCount);
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
            logInfo("✅ 已添加监控: " + path);
            successCount++;
        } else {
            logError("❌ 添加监控失败: " + path);
        }
    }
    
    if (successCount == 0) {
        logError("没有成功添加任何监控路径");
        return false;
    }
    
    logInfo("📂 成功设置监控: " + std::to_string(successCount) + "/" + std::to_string(totalCount) + " 个路径");
    return true;
}

void FilesystemConnector::logConfig() {
    logInfo("📋 文件系统配置加载:");
    logInfo("   监控目录: " + std::to_string(m_config.watchDirectories.size()) + " 个");
    for (const auto& dir : m_config.watchDirectories) {
        logInfo("     - " + dir);
    }
    logInfo("   包含扩展名: " + std::to_string(m_config.includeExtensions.size()) + " 个");
    logInfo("   排除模式: " + std::to_string(m_config.excludePatterns.size()) + " 个");
    logInfo("   最大文件大小: " + std::to_string(m_config.maxFileSize) + "MB");
    logInfo("   递归深度: " + std::to_string(m_config.recursiveDepth));
    logInfo("   批处理间隔: " + std::to_string(m_config.batchInterval) + "ms");
    logInfo("   防抖时间: " + std::to_string(m_config.debounceTime) + "ms");
    logInfo("   启用内容索引: " + std::string(m_config.enableContentIndexing ? "是" : "否"));
}

} // namespace linch_connector