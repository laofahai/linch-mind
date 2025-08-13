#include <iostream>
#include <string>
#include <chrono>
#include <thread>
#include <signal.h>
#include <cstdlib>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <nlohmann/json.hpp>
#include <filesystem>

// 使用shared库
#include <linch_connector/daemon_discovery.hpp>
#include <linch_connector/config_manager.hpp>
#include <linch_connector/unified_client.hpp>
#include <linch_connector/utils.hpp>
#include <linch_connector/connector_status.hpp>

// 新的监控器
#include "monitor_factory.hpp"

using json = nlohmann::json;
using namespace linch_connector;
namespace fs = std::filesystem;

// 全局标志位用于信号处理
volatile sig_atomic_t g_shouldStop = 0;

// 信号处理器
void signalHandler(int signum) {
    std::cout << "\n📁 Received signal " << signum << ", stopping filesystem monitor..." << std::endl;
    g_shouldStop = 1;
}

// 从配置管理器加载监控配置
std::vector<MonitorConfig> loadMonitorConfigs(ConfigManager& config) {
    std::vector<MonitorConfig> monitorConfigs;
    
    // 处理监控目录列表 - 支持数组格式和逗号分隔字符串
    std::vector<std::string> watchDirs;
    std::string watchDirsStr = config.getConfigValue("watch_directories", "~/Documents,~/Desktop");
    
    // 如果是JSON数组格式，解析JSON
    if (watchDirsStr.front() == '[' && watchDirsStr.back() == ']') {
        try {
            json watchDirsJson = json::parse(watchDirsStr);
            for (const auto& dir : watchDirsJson) {
                if (dir.is_string()) {
                    watchDirs.push_back(dir.get<std::string>());
                }
            }
        } catch (const std::exception& e) {
            std::cerr << "⚠️ Failed to parse watch_directories as JSON, fallback to comma-separated" << std::endl;
            // Fallback to comma-separated parsing
        }
    }
    
    // 如果JSON解析失败或不是JSON格式，使用逗号分隔解析
    if (watchDirs.empty()) {
        std::stringstream ss(watchDirsStr);
        std::string dir;
        while (std::getline(ss, dir, ',')) {
            dir.erase(0, dir.find_first_not_of(" \t"));
            dir.erase(dir.find_last_not_of(" \t") + 1);
            if (!dir.empty()) {
                watchDirs.push_back(dir);
            }
        }
    }
    
    // 处理文件扩展名列表 - 支持数组格式和逗号分隔字符串
    std::set<std::string> includeExts;
    std::string includeExtsStr = config.getConfigValue("include_extensions", 
        ".txt,.md,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx");
    
    if (includeExtsStr.front() == '[' && includeExtsStr.back() == ']') {
        try {
            json includeExtsJson = json::parse(includeExtsStr);
            for (const auto& ext : includeExtsJson) {
                if (ext.is_string()) {
                    includeExts.insert(ext.get<std::string>());
                }
            }
        } catch (const std::exception& e) {
            std::cerr << "⚠️ Failed to parse include_extensions as JSON, fallback to comma-separated" << std::endl;
        }
    }
    
    if (includeExts.empty()) {
        std::stringstream extSs(includeExtsStr);
        std::string ext;
        while (std::getline(extSs, ext, ',')) {
            ext.erase(0, ext.find_first_not_of(" \t"));
            ext.erase(ext.find_last_not_of(" \t") + 1);
            if (!ext.empty()) {
                includeExts.insert(ext);
            }
        }
    }
    
    // 处理排除模式列表 - 支持数组格式和逗号分隔字符串
    std::set<std::string> excludePatterns;
    std::string excludePatternsStr = config.getConfigValue("exclude_patterns",
        "^\\..*,.*\\.tmp$,.*\\.log$,__pycache__,node_modules");
    
    if (excludePatternsStr.front() == '[' && excludePatternsStr.back() == ']') {
        try {
            json excludePatternsJson = json::parse(excludePatternsStr);
            for (const auto& pattern : excludePatternsJson) {
                if (pattern.is_string()) {
                    excludePatterns.insert(pattern.get<std::string>());
                }
            }
        } catch (const std::exception& e) {
            std::cerr << "⚠️ Failed to parse exclude_patterns as JSON, fallback to comma-separated" << std::endl;
        }
    }
    
    if (excludePatterns.empty()) {
        std::stringstream patternSs(excludePatternsStr);
        std::string pattern;
        while (std::getline(patternSs, pattern, ',')) {
            pattern.erase(0, pattern.find_first_not_of(" \t"));
            pattern.erase(pattern.find_last_not_of(" \t") + 1);
            if (!pattern.empty()) {
                excludePatterns.insert(pattern);
            }
        }
    }
    
    // 获取其他配置值，使用TOML配置中定义的键名
    int maxFileSize = std::stoi(config.getConfigValue("max_file_size", "50"));
    int recursiveDepth = std::stoi(config.getConfigValue("recursive_depth", "5"));
    int batchInterval = std::stoi(config.getConfigValue("batch_interval", "300"));
    int debounceTime = std::stoi(config.getConfigValue("debounce_time", "300"));
    int maxContentLength = std::stoi(config.getConfigValue("max_content_length", "50000"));
    bool enableContentIndexing = config.getConfigValue("enable_content_indexing", "true") == "true";
    
    std::cout << "📋 Configuration loaded:" << std::endl;
    std::cout << "   Watch directories: " << watchDirs.size() << std::endl;
    std::cout << "   Include extensions: " << includeExts.size() << std::endl;
    std::cout << "   Exclude patterns: " << excludePatterns.size() << std::endl;
    std::cout << "   Max file size: " << maxFileSize << "MB" << std::endl;
    std::cout << "   Recursive depth: " << recursiveDepth << std::endl;
    std::cout << "   Batch interval: " << batchInterval << "ms" << std::endl;
    std::cout << "   Debounce time: " << debounceTime << "ms" << std::endl;
    
    // 处理每个监控目录
    for (std::string path : watchDirs) {
        // 去除空白字符
        path.erase(0, path.find_first_not_of(" \t"));
        path.erase(path.find_last_not_of(" \t") + 1);
        
        // 展开 ~ 为用户主目录
        if (path.substr(0, 2) == "~/") {
            const char* homeDir = std::getenv("HOME");
            if (!homeDir) homeDir = std::getenv("USERPROFILE"); // Windows
            if (homeDir) {
                path = std::string(homeDir) + path.substr(1);
            }
        }
        
        if (!path.empty() && fs::exists(path) && fs::is_directory(path)) {
            MonitorConfig monitorConfig(path);
            monitorConfig.recursive = (recursiveDepth > 1);
            monitorConfig.maxFileSize = maxFileSize * 1024 * 1024; // 转换为字节
            
            // 添加支持的扩展名
            monitorConfig.includeExtensions = includeExts;
            
            // 添加忽略模式
            for (const auto& pattern : excludePatterns) {
                monitorConfig.excludePatterns.insert(pattern);
            }
            
            monitorConfigs.push_back(monitorConfig);
        }
    }
    
    return monitorConfigs;
}

// 发送文件系统事件到daemon（轻量级事件模式）
void sendFilesystemEvent(const FileSystemEvent& event, 
                        UnifiedClient& client, ConfigManager& config) {
    std::cout << "📁 Sending file event: " << static_cast<int>(event.type) << " - " << event.path << std::endl;
    
    fs::path filePath(event.path);
    
    try {
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
        json file_event_data = {
            {"file_path", event.path},
            {"file_name", filePath.filename().string()},
            {"extension", filePath.extension().string()},
            {"directory", filePath.parent_path().string()},
            {"is_directory", event.isDirectory}
        };
        
        // 如果文件存在，添加大小信息
        if (!event.isDirectory && event.fileSize > 0) {
            file_event_data["size"] = event.fileSize;
        }
        
        // 如果有旧路径（重命名事件）
        if (!event.oldPath.empty()) {
            file_event_data["old_path"] = event.oldPath;
        }
        
        json event_data = {
            {"connector_id", "filesystem"},
            {"event_type", eventTypeStr},
            {"event_data", file_event_data},
            {"timestamp", utils::getCurrentTimestamp()},
            {"metadata", {}} // 空元数据，所有信息都在event_data中
        };
        
        // 发送到通用事件API
        auto response = client.post("/events/submit", event_data.dump());
        
        if (response.success) {
            std::cout << "✅ Sent file event: " << filePath.filename().string() << std::endl;
        } else {
            std::cerr << "❌ Failed to send file event: " << response.error_message 
                      << " (code: " << response.error_code << ")" << std::endl;
        }
        
    } catch (const std::exception& e) {
        std::cerr << "❌ Error sending file event: " << e.what() << std::endl;
    }
}

// 批量发送文件系统事件
void sendBatchFilesystemEvents(const std::vector<FileSystemEvent>& events,
                              UnifiedClient& client, ConfigManager& config) {
    if (events.empty()) {
        return;
    }
    
    std::cout << "📁 Sending batch of " << events.size() << " file events" << std::endl;
    
    try {
        json batch_data = json::array();
        
        for (const auto& event : events) {
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
            
            json file_event_data = {
                {"file_path", event.path},
                {"file_name", filePath.filename().string()},
                {"extension", filePath.extension().string()},
                {"directory", filePath.parent_path().string()},
                {"is_directory", event.isDirectory}
            };
            
            if (!event.isDirectory && event.fileSize > 0) {
                file_event_data["size"] = event.fileSize;
            }
            
            if (!event.oldPath.empty()) {
                file_event_data["old_path"] = event.oldPath;
            }
            
            json event_data = {
                {"connector_id", "filesystem"},
                {"event_type", eventTypeStr},
                {"event_data", file_event_data},
                {"timestamp", utils::getCurrentTimestamp()},
                {"metadata", {}}
            };
            
            batch_data.push_back(event_data);
        }
        
        json request_data = {
            {"batch_events", batch_data}
        };
        
        // 发送批量事件
        auto response = client.post("/events/submit_batch", request_data.dump());
        
        if (response.success) {
            std::cout << "✅ Sent batch of " << events.size() << " file events" << std::endl;
        } else {
            std::cerr << "❌ Failed to send batch events: " << response.error_message 
                      << " (code: " << response.error_code << ")" << std::endl;
            
            // 如果批量发送失败，尝试逐个发送
            std::cout << "🔄 Falling back to individual event sending..." << std::endl;
            for (const auto& event : events) {
                sendFilesystemEvent(event, client, config);
            }
        }
        
    } catch (const std::exception& e) {
        std::cerr << "❌ Error sending batch events: " << e.what() << std::endl;
    }
}

int main(int argc, char* argv[]) {
    std::cout << "🚀 Starting Linch Mind Filesystem Connector (Native Event-Driven)" << std::endl;
    std::cout << "📍 Platform: " << MonitorFactory::getPlatformInfo() << std::endl;

    signal(SIGINT, signalHandler);
    signal(SIGTERM, signalHandler);

    DaemonDiscovery discovery;
    std::cout << "🔍 Discovering daemon..." << std::endl;

    auto daemonInfoOpt = discovery.waitForDaemon(std::chrono::seconds(30));
    if (!daemonInfoOpt) {
        std::cerr << "❌ Failed to discover daemon. Exiting..." << std::endl;
        return 1;
    }

    UnifiedClient unifiedClient;
    unifiedClient.setTimeout(60); // File operations can take longer

    if (!unifiedClient.connect(*daemonInfoOpt)) {
        std::cerr << "❌ Failed to connect to daemon. Exiting..." << std::endl;
        return 1;
    }

    std::cout << "🔗 Connected to daemon via IPC." << std::endl;

    // 初始化状态管理器
    ConnectorStatusManager statusManager("filesystem", "文件系统连接器");
    statusManager.setState(ConnectorRunningState::STARTING);
    statusManager.notifyStarting(unifiedClient);

    ConfigManager configManager("filesystem", "");
    if (!configManager.loadFromDaemon()) {
        std::cerr << "⚠️ Failed to load configuration from daemon, using defaults." << std::endl;
    }

    // 创建新的文件系统监控器
    FileSystemMonitor monitor(MonitorType::AUTO);
    
    // 显示监控器信息
    auto stats = monitor.getStatistics();
    std::cout << "🔧 Using monitor: " << stats.platformInfo << std::endl;

    // 创建事件回调
    auto eventCallback = [&unifiedClient, &configManager](const FileSystemEvent& event) {
        sendFilesystemEvent(event, unifiedClient, configManager);
    };
    
    // 创建批量事件回调
    auto batchCallback = [&unifiedClient, &configManager](const std::vector<FileSystemEvent>& events) {
        sendBatchFilesystemEvents(events, unifiedClient, configManager);
    };

    std::cout << "📂 Setting up filesystem watches..." << std::endl;
    
    // Load watch configurations from daemon config
    auto monitorConfigs = loadMonitorConfigs(configManager);
    for (const auto& config : monitorConfigs) {
        if (monitor.addPath(config)) {
            std::cout << "✅ Added watch for: " << config.path << std::endl;
        } else {
            std::cerr << "❌ Failed to add watch for: " << config.path << std::endl;
        }
    }

    // 使用配置的批量处理间隔
    int batchIntervalMs = std::stoi(configManager.getConfigValue("batch_interval", "300"));
    
    std::cout << "📊 Setting batch interval: " << batchIntervalMs << "ms" << std::endl;
    monitor.setBatchCallback(batchCallback, std::chrono::milliseconds(batchIntervalMs));

    std::cout << "📂 Starting filesystem monitoring..." << std::endl;
    if (!monitor.start(eventCallback)) {
        std::cerr << "❌ Failed to start filesystem monitoring" << std::endl;
        statusManager.setError("Failed to start filesystem monitoring");
        statusManager.sendStatusUpdate(unifiedClient);
        return 1;
    }

    // 设置为运行状态
    statusManager.setState(ConnectorRunningState::RUNNING);
    statusManager.sendStatusUpdate(unifiedClient);
    
    std::cout << "✅ Native filesystem connector is now running" << std::endl;

    // Main loop with heartbeat and statistics
    auto lastHeartbeat = std::chrono::system_clock::now();
    auto lastStats = std::chrono::system_clock::now();
    const auto heartbeatInterval = std::chrono::seconds(30); // 30秒心跳间隔
    const auto statsInterval = std::chrono::seconds(60);     // 60秒统计间隔
    
    while (!g_shouldStop) {
        auto now = std::chrono::system_clock::now();
        
        // 检查是否应该发送心跳
        if (now - lastHeartbeat >= heartbeatInterval) {
            statusManager.sendHeartbeat(unifiedClient);
            lastHeartbeat = now;
        }
        
        // 检查是否应该显示统计信息
        if (now - lastStats >= statsInterval) {
            auto currentStats = monitor.getStatistics();
            std::cout << "📊 Statistics: " 
                      << currentStats.eventsProcessed << " events processed, "
                      << currentStats.pathsMonitored << " paths monitored" << std::endl;
            lastStats = now;
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    }
    
    // 清理
    std::cout << "🛑 Stopping filesystem connector..." << std::endl;
    statusManager.setState(ConnectorRunningState::STOPPING);
    statusManager.notifyStopping(unifiedClient);
    
    monitor.stop();
    
    // 显示最终统计信息
    auto finalStats = monitor.getStatistics();
    std::cout << "📊 Final Statistics:" << std::endl;
    std::cout << "   Events processed: " << finalStats.eventsProcessed << std::endl;
    std::cout << "   Events filtered: " << finalStats.eventsFiltered << std::endl;
    std::cout << "   Paths monitored: " << finalStats.pathsMonitored << std::endl;
    
    std::cout << "✅ Filesystem connector stopped successfully" << std::endl;
    
    return 0;
}