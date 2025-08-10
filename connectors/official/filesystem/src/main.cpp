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

// 本地头文件
#include "filesystem_monitor.hpp"

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

// Schema注册函数（保留但不实际使用，schema从connector.json静态加载）
bool registerConfigSchema(UnifiedClient& client, const std::string& daemonUrl) {
    // Schema现在从connector.json静态加载，不需要动态注册
    std::cout << "ℹ️  Using static schema from connector.json" << std::endl;
    return true;
}

// 从配置管理器加载监控配置
std::vector<FileSystemMonitor::WatchConfig> loadWatchConfigs(ConfigManager& config) {
    std::vector<FileSystemMonitor::WatchConfig> watchConfigs;
    
    // 使用getConfigValue获取配置值（使用扁平化的键）
    // 监控目录列表（逗号分隔）
    std::string watchDirsStr = config.getConfigValue("watch_directories", "~/Documents,~/Desktop");
    std::vector<std::string> watchDirs;
    std::stringstream ss(watchDirsStr);
    std::string dir;
    while (std::getline(ss, dir, ',')) {
        dir.erase(0, dir.find_first_not_of(" \t"));
        dir.erase(dir.find_last_not_of(" \t") + 1);
        if (!dir.empty()) {
            watchDirs.push_back(dir);
        }
    }
    
    // 文件扩展名列表（使用扁平化的键）
    std::string includeExtsStr = config.getConfigValue("include_extensions", 
        ".txt,.md,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx");
    std::vector<std::string> includeExts;
    std::stringstream extSs(includeExtsStr);
    std::string ext;
    while (std::getline(extSs, ext, ',')) {
        ext.erase(0, ext.find_first_not_of(" \t"));
        ext.erase(ext.find_last_not_of(" \t") + 1);
        if (!ext.empty()) {
            includeExts.push_back(ext);
        }
    }
    
    // 排除模式列表（使用扁平化的键）
    std::string excludePatternsStr = config.getConfigValue("exclude_patterns",
        "^\\..*,.*\\.tmp$,.*\\.log$,__pycache__,node_modules");
    std::vector<std::string> excludePatterns;
    std::stringstream patternSs(excludePatternsStr);
    std::string pattern;
    while (std::getline(patternSs, pattern, ',')) {
        pattern.erase(0, pattern.find_first_not_of(" \t"));
        pattern.erase(pattern.find_last_not_of(" \t") + 1);
        if (!pattern.empty()) {
            excludePatterns.push_back(pattern);
        }
    }
    
    // 获取其他配置值（使用扁平化的键）
    int maxFileSize = std::stoi(config.getConfigValue("max_file_size", "50"));
    int recursiveDepth = std::stoi(config.getConfigValue("recursive_depth", "5"));
    bool enableContentIndexing = config.getConfigValue("enable_content_indexing", "true") == "true";
    
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
            FileSystemMonitor::WatchConfig watchConfig(path);
            watchConfig.name = fs::path(path).filename().string();
            watchConfig.enabled = enableContentIndexing;
            watchConfig.recursive = (recursiveDepth > 1);
            watchConfig.maxFileSize = maxFileSize * 1024 * 1024; // 转换为字节
            
            // 添加支持的扩展名
            for (const auto& ext : includeExts) {
                watchConfig.supportedExtensions.insert(ext);
            }
            
            // 添加忽略模式
            for (const auto& pattern : excludePatterns) {
                watchConfig.ignorePatterns.push_back(pattern);
            }
            
            watchConfigs.push_back(watchConfig);
        }
    }
    
    return watchConfigs;
}

// 发送文件系统事件到daemon（轻量级事件模式）
void sendFilesystemEvent(const FileSystemMonitor::FileEvent& event, 
                        UnifiedClient& client, ConfigManager& config) {
    std::cout << "📁 Sending file event: " << event.eventType << " - " << event.path << std::endl;
    
    fs::path filePath(event.path);
    
    try {
        // 创建文件事件数据
        json file_event_data = {
            {"file_path", event.path},
            {"file_name", filePath.filename().string()},
            {"extension", filePath.extension().string()},
            {"directory", filePath.parent_path().string()}
        };
        
        // 如果文件存在，添加大小信息
        if (fs::exists(filePath) && (event.eventType == "created" || event.eventType == "modified")) {
            try {
                file_event_data["size"] = fs::file_size(filePath);
            } catch (const std::exception& e) {
                // 文件大小获取失败时跳过
            }
        }
        
        json event_data = {
            {"connector_id", "filesystem"},
            {"event_type", event.eventType},
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

int main(int argc, char* argv[]) {
    std::cout << "🚀 Starting Linch Mind Filesystem Connector (Pure IPC)" << std::endl;

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

    // Schema is loaded from connector.json by the daemon

    FileSystemMonitor monitor;

    // Create callback to handle filesystem changes  
    auto filesystemCallback = [&unifiedClient, &configManager](const FileSystemMonitor::FileEvent& event) {
        sendFilesystemEvent(event, unifiedClient, configManager);
    };

    std::cout << "📂 Setting up filesystem watches..." << std::endl;
    
    // Load watch configurations from daemon config
    auto watchConfigs = loadWatchConfigs(configManager);
    for (const auto& config : watchConfigs) {
        if (config.enabled) {
            if (monitor.addWatch(config)) {
                std::cout << "✅ Added watch for: " << config.path << std::endl;
            } else {
                std::cerr << "❌ Failed to add watch for: " << config.path << std::endl;
            }
        }
    }

    std::cout << "📂 Starting filesystem monitoring..." << std::endl;
    if (!monitor.startMonitoring(filesystemCallback, 1000)) {
        std::cerr << "❌ Failed to start filesystem monitoring" << std::endl;
        statusManager.setError("Failed to start filesystem monitoring");
        statusManager.sendStatusUpdate(unifiedClient);
        return 1;
    }

    // 设置为运行状态
    statusManager.setState(ConnectorRunningState::RUNNING);
    statusManager.sendStatusUpdate(unifiedClient);
    
    std::cout << "✅ Filesystem connector is now running with heartbeat support" << std::endl;

    // Main loop with heartbeat
    auto lastHeartbeat = std::chrono::system_clock::now();
    const auto heartbeatInterval = std::chrono::seconds(30); // 30秒心跳间隔
    
    while (!g_shouldStop) {
        auto now = std::chrono::system_clock::now();
        
        // 检查是否应该发送心跳
        if (now - lastHeartbeat >= heartbeatInterval) {
            statusManager.sendHeartbeat(unifiedClient);
            lastHeartbeat = now;
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    }
    
    // 清理
    std::cout << "🛑 Stopping filesystem connector..." << std::endl;
    statusManager.setState(ConnectorRunningState::STOPPING);
    statusManager.notifyStopping(unifiedClient);
    
    monitor.stopMonitoring();
    
    return 0;
}