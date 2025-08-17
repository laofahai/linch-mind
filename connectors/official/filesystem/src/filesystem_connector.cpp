#include "filesystem_connector.hpp"
#include <linch_connector/utils.hpp>
#include <iostream>
#include <chrono>
#include <thread>
#include <filesystem>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

namespace linch_connector {

FilesystemConnector::FilesystemConnector() 
    : BaseConnector("filesystem", "用户目录监听文件系统连接器")
{
    logInfo("🚀 用户目录监听文件系统连接器初始化");
}

std::unique_ptr<IConnectorMonitor> FilesystemConnector::createMonitor() {
    // 创建文件系统监听适配器
    return std::make_unique<FilesystemMonitorAdapter>();
}

bool FilesystemConnector::loadConnectorConfig() {
    logInfo("📋 加载文件系统连接器配置");
    
    // 使用ConfigManager加载配置
    auto& configManager = getConfigManager();
    
    // 从配置中加载参数
    std::string enableContentParsingStr = configManager.getConfigValue("enable_content_parsing", "true");
    m_enableContentParsing = (enableContentParsingStr == "true" || enableContentParsingStr == "1");
    
    std::string maxFileSizeStr = configManager.getConfigValue("max_file_size", "10485760"); // 10MB
    try {
        m_maxFileSize = std::stoull(maxFileSizeStr);
    } catch (const std::exception&) {
        m_maxFileSize = 10 * 1024 * 1024; // 默认10MB
    }
    
    std::string eventDebounceStr = configManager.getConfigValue("event_debounce_ms", "500");
    try {
        m_eventDebounceMs = std::stoi(eventDebounceStr);
    } catch (const std::exception&) {
        m_eventDebounceMs = 500; // 默认500ms
    }
    
    logInfo("✅ 配置加载完成 - 内容解析: " + std::string(m_enableContentParsing ? "启用" : "禁用") + 
            ", 最大文件大小: " + std::to_string(m_maxFileSize) + " 字节");
    
    return true;
}

bool FilesystemConnector::onInitialize() {
    logInfo("🔧 初始化文件系统连接器组件");
    
    // 创建文件系统监听适配器
    m_monitor = std::make_unique<FilesystemMonitorAdapter>();
    if (!m_monitor) {
        logError("❌ 无法创建文件系统监听适配器");
        return false;
    }
    
    // 创建文件内容解析器
    if (m_enableContentParsing) {
        m_contentParser = createDefaultFileContentParser();
        if (!m_contentParser) {
            logError("❌ 无法创建文件内容解析器");
            return false;
        }
        logInfo("✅ 文件内容解析器初始化成功");
    }
    
    logInfo("✅ 文件系统连接器组件初始化完成");
    return true;
}

bool FilesystemConnector::onStart() {
    logInfo("🚀 启动用户目录监听文件系统连接器");
    
    if (!m_monitor) {
        logError("❌ 文件系统监听器未初始化");
        return false;
    }
    
    // 设置连接器事件回调
    auto callback = [this](ConnectorEvent&& event) {
        // 将ConnectorEvent转换为FileSystemEvent并处理
        json eventData = event.eventData;
        FileSystemEvent fsEvent;
        fsEvent.path = eventData.value("path", "");
        
        std::string eventType = event.eventType;
        if (eventType == "created") {
            fsEvent.type = FileEventType::CREATED;
        } else if (eventType == "modified") {
            fsEvent.type = FileEventType::MODIFIED;
        } else if (eventType == "deleted") {
            fsEvent.type = FileEventType::DELETED;
        } else {
            fsEvent.type = FileEventType::MODIFIED; // 默认
        }
        
        onFileSystemEvent(fsEvent);
    };
    
    // 启动监听器
    if (!m_monitor->start(std::move(callback))) {
        logError("❌ 启动文件系统监听器失败");
        return false;
    }
    
    logInfo("✅ 文件系统连接器启动成功");
    return true;
}

void FilesystemConnector::onStop() {
    logInfo("🛑 停止文件系统连接器");
    
    if (m_monitor) {
        m_monitor->stop();
        m_monitor.reset();
    }
    
    m_contentParser.reset();
    
    std::lock_guard<std::mutex> lock(m_directoriesMutex);
    m_watchedDirectories.clear();
    
    logInfo("✅ 文件系统连接器已停止");
}

bool FilesystemConnector::addWatchDirectory(const std::string& directoryPath, bool recursive, bool parseContent) {
    if (!std::filesystem::exists(directoryPath) || !std::filesystem::is_directory(directoryPath)) {
        logError("❌ 目录不存在或不是有效目录: " + directoryPath);
        return false;
    }
    
    std::lock_guard<std::mutex> lock(m_directoriesMutex);
    
    // 检查是否已经在监听
    if (m_watchedDirectories.find(directoryPath) != m_watchedDirectories.end()) {
        logInfo("📁 目录已在监听中: " + directoryPath);
        return true;
    }
    
    // 添加到监听器
    if (m_monitor) {
        MonitorConfig config;
        config.name = "watch_directory_" + directoryPath;
        config.settings = json{
            {"path", directoryPath},
            {"recursive", recursive},
            {"enabled", true}
        };
        
        if (!m_monitor->addPath(config)) {
            logError("❌ 添加监听目录失败: " + directoryPath);
            return false;
        }
    }
    
    // 添加到内部列表
    m_watchedDirectories.insert(directoryPath);
    
    logInfo("✅ 添加监听目录成功: " + directoryPath + " (递归: " + (recursive ? "是" : "否") + 
            ", 解析内容: " + (parseContent ? "是" : "否") + ")");
    
    // TODO: 可选实现初始扫描功能
    // 当前版本只监听增量变化，减少系统负载
    
    return true;
}

bool FilesystemConnector::removeWatchDirectory(const std::string& directoryPath) {
    std::lock_guard<std::mutex> lock(m_directoriesMutex);
    
    auto it = m_watchedDirectories.find(directoryPath);
    if (it == m_watchedDirectories.end()) {
        logInfo("📁 目录未在监听中: " + directoryPath);
        return true;
    }
    
    // 从监听器移除
    if (m_monitor) {
        if (!m_monitor->removePath(directoryPath)) {
            logError("❌ 从监听器移除目录失败: " + directoryPath);
            return false;
        }
    }
    
    // 从内部列表移除
    m_watchedDirectories.erase(it);
    
    logInfo("✅ 移除监听目录成功: " + directoryPath);
    return true;
}

std::vector<std::string> FilesystemConnector::getWatchedDirectories() const {
    std::lock_guard<std::mutex> lock(m_directoriesMutex);
    
    std::vector<std::string> directories;
    directories.reserve(m_watchedDirectories.size());
    
    for (const auto& dir : m_watchedDirectories) {
        directories.push_back(dir);
    }
    
    return directories;
}


void FilesystemConnector::onFileSystemEvent(const FileSystemEvent& event) {
    // 检查文件是否应该被处理
    if (!shouldProcessFile(event.path)) {
        return;
    }
    
    switch (event.type) {
        case FileEventType::CREATED:
            handleFileCreated(event.path);
            break;
        case FileEventType::MODIFIED:
            handleFileModified(event.path);
            break;
        case FileEventType::DELETED:
            handleFileDeleted(event.path);
            break;
        default:
            break;
    }
}

void FilesystemConnector::handleFileCreated(const std::string& filePath) {
    logInfo("📝 检测到文件创建: " + filePath);
    
    std::string content;
    if (m_enableContentParsing && m_contentParser) {
        try {
            FileContent fileContent = m_contentParser->parseFile(filePath, m_maxFileSize);
            if (fileContent.contentExtracted) {
                content = fileContent.textContent;
            }
        } catch (const std::exception& e) {
            logError("⚠️ 解析文件内容失败: " + filePath + " - " + std::string(e.what()));
        }
    }
    
    sendFileEvent("file_created", filePath, content);
}

void FilesystemConnector::handleFileModified(const std::string& filePath) {
    logInfo("📝 检测到文件修改: " + filePath);
    
    std::string content;
    if (m_enableContentParsing && m_contentParser) {
        try {
            FileContent fileContent = m_contentParser->parseFile(filePath, m_maxFileSize);
            if (fileContent.contentExtracted) {
                content = fileContent.textContent;
            }
        } catch (const std::exception& e) {
            logError("⚠️ 解析文件内容失败: " + filePath + " - " + std::string(e.what()));
        }
    }
    
    sendFileEvent("file_modified", filePath, content);
}

void FilesystemConnector::handleFileDeleted(const std::string& filePath) {
    logInfo("🗑️ 检测到文件删除: " + filePath);
    sendFileEvent("file_deleted", filePath);
}

void FilesystemConnector::sendFileEvent(const std::string& eventType, const std::string& filePath, const std::string& content) {
    json eventData = {
        {"path", filePath},
        {"event_type", eventType},
        {"timestamp", std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count()}
    };
    
    // 添加文件基础信息
    try {
        auto path = std::filesystem::path(filePath);
        eventData["name"] = path.filename().string();
        eventData["extension"] = path.extension().string();
        
        if (std::filesystem::exists(filePath) && eventType != "file_deleted") {
            eventData["size"] = std::filesystem::file_size(filePath);
            
            auto ftime = std::filesystem::last_write_time(filePath);
            auto sctp = std::chrono::time_point_cast<std::chrono::system_clock::duration>(
                ftime - std::filesystem::file_time_type::clock::now() + std::chrono::system_clock::now()
            );
            eventData["modified_time"] = std::chrono::duration_cast<std::chrono::seconds>(sctp.time_since_epoch()).count();
        }
        
        // 添加内容（如果有）
        if (!content.empty()) {
            eventData["content"] = content;
            eventData["content_extracted"] = true;
        } else {
            eventData["content_extracted"] = false;
        }
        
    } catch (const std::exception& e) {
        logError("⚠️ 获取文件信息失败: " + filePath + " - " + std::string(e.what()));
    }
    
    ConnectorEvent event = ConnectorEvent::create("filesystem", eventType, std::move(eventData));
    sendEvent(event);
}


bool FilesystemConnector::shouldProcessFile(const std::string& filePath) const {
    // 检查文件扩展名是否受支持
    if (m_contentParser && !m_contentParser->isSupported(filePath)) {
        return false;
    }
    
    // 检查文件大小
    try {
        if (std::filesystem::exists(filePath) && std::filesystem::is_regular_file(filePath)) {
            auto fileSize = std::filesystem::file_size(filePath);
            if (fileSize > m_maxFileSize) {
                return false;
            }
        }
    } catch (const std::exception&) {
        return false;
    }
    
    // 排除隐藏文件和系统文件
    auto fileName = std::filesystem::path(filePath).filename().string();
    if (!fileName.empty() && (fileName[0] == '.' || fileName[0] == '~')) {
        return false;
    }
    
    return true;
}

std::vector<std::string> FilesystemConnector::getSupportedExtensions() const {
    if (m_contentParser) {
        return m_contentParser->getSupportedExtensions();
    }
    return {};
}

} // namespace linch_connector