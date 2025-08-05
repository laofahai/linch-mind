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
#include <linch_connector/http_client.hpp>
#include <linch_connector/utils.hpp>

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

// 注册配置schema到daemon
bool registerConfigSchema(HttpClient& client, const std::string& daemonUrl) {
    json schema = {
        {"type", "object"},
        {"title", "文件系统连接器配置"},
        {"description", "配置文件系统监控参数和监控目录"},
        {"properties", {
            {"poll_interval", {
                {"type", "number"},
                {"title", "轮询间隔 (秒)"},
                {"description", "文件系统检查的间隔时间"},
                {"default", 2.0},
                {"minimum", 0.5},
                {"maximum", 60.0},
                {"ui_component", "number_input"}
            }},
            {"default_supported_extensions", {
                {"type", "array"},
                {"title", "默认支持的文件类型"},
                {"description", "监控的文件扩展名列表"},
                {"items", {"type", "string"}},
                {"default", {".txt", ".md", ".py", ".js", ".json", ".yaml", ".yml", ".html", ".css", ".cpp", ".hpp", ".c", ".h"}},
                {"ui_component", "tags_input"}
            }},
            {"default_max_file_size", {
                {"type", "integer"},
                {"title", "默认最大文件大小 (MB)"},
                {"description", "超过此大小的文件将被忽略"},
                {"default", 10},
                {"minimum", 1},
                {"maximum", 100},
                {"ui_component", "number_input"}
            }},
            {"default_ignore_patterns", {
                {"type", "array"},
                {"title", "默认忽略模式"},
                {"description", "忽略的文件模式，支持通配符"},
                {"items", {"type", "string"}},
                {"default", {"*.tmp", ".*", "node_modules/*", "__pycache__/*", "*.log", ".git/*", "build/*", "dist/*"}},
                {"ui_component", "tags_input"}
            }},
            {"max_content_length", {
                {"type", "integer"},
                {"title", "最大内容长度"},
                {"description", "文件内容截断长度（字符数）"},
                {"default", 50000},
                {"minimum", 1000},
                {"maximum", 200000},
                {"ui_component", "number_input"}
            }},
            {"monitoring_enabled", {
                {"type", "boolean"},
                {"title", "启用文件监控"},
                {"description", "总开关，控制是否启用文件系统监控"},
                {"default", true},
                {"ui_component", "switch"}
            }}
        }},
        {"required", {"poll_interval", "monitoring_enabled"}}
    };

    json payload = {
        {"connector_id", "filesystem"},
        {"config_schema", schema},
        {"ui_schema", json::object()},
        {"connector_name", "FileSystemConnector"},
        {"connector_description", "文件系统连接器 - 监控文件系统变化并推送到Daemon"},
        {"schema_source", "embedded"}
    };

    client.addHeader("Content-Type", "application/json");
    auto response = client.post(daemonUrl + "/connector-config/register-schema/filesystem", 
                               payload.dump());
    
    if (response.isSuccess()) {
        std::cout << "✅ Config schema registered successfully" << std::endl;
        return true;
    } else {
        std::cerr << "❌ Failed to register config schema: HTTP " << response.statusCode << std::endl;
        return false;
    }
}

// 从配置管理器加载监控配置
std::vector<FileSystemMonitor::WatchConfig> loadWatchConfigs(ConfigManager& config) {
    std::vector<FileSystemMonitor::WatchConfig> watchConfigs;
    
    // 简化的配置解析（实际项目中可以扩展为完整的JSON数组解析）
    std::string watchPaths = config.getConfigValue("watch_paths", "~/Downloads,~/Documents");
    std::string supportedExts = config.getConfigValue("supported_extensions", ".txt,.md,.py,.js,.json,.yaml,.yml,.html,.css,.cpp,.hpp,.c,.h");
    std::string ignorePatterns = config.getConfigValue("ignore_patterns", "*.tmp,.*,node_modules/*,__pycache__/*,*.log,.git/*,build/*,dist/*");
    int maxFileSize = std::stoi(config.getConfigValue("max_file_size_mb", "10"));
    
    // 解析监控路径（逗号分隔）
    std::stringstream ss(watchPaths);
    std::string path;
    while (std::getline(ss, path, ',')) {
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
            watchConfig.enabled = true;
            watchConfig.recursive = true;
            watchConfig.maxFileSize = maxFileSize * 1024 * 1024; // 转换为字节
            
            // 解析支持的扩展名
            std::stringstream extSs(supportedExts);
            std::string ext;
            while (std::getline(extSs, ext, ',')) {
                ext.erase(0, ext.find_first_not_of(" \t"));
                ext.erase(ext.find_last_not_of(" \t") + 1);
                if (!ext.empty()) {
                    watchConfig.supportedExtensions.insert(ext);
                }
            }
            
            // 解析忽略模式
            std::stringstream ignoreSs(ignorePatterns);
            std::string pattern;
            while (std::getline(ignoreSs, pattern, ',')) {
                pattern.erase(0, pattern.find_first_not_of(" \t"));
                pattern.erase(pattern.find_last_not_of(" \t") + 1);
                if (!pattern.empty()) {
                    watchConfig.ignorePatterns.push_back(pattern);
                }
            }
            
            watchConfigs.push_back(watchConfig);
        }
    }
    
    return watchConfigs;
}

// 处理文件系统事件
void processFilesystemEvent(const FileSystemMonitor::FileEvent& event, 
                           HttpClient& client, ConfigManager& config) {
    std::cout << "📁 Processing file event: " << event.eventType << " - " << event.path << std::endl;
    
    // 对于创建和修改事件，读取文件内容
    if (event.eventType == "created" || event.eventType == "modified") {
        try {
            std::ifstream file(event.path);
            if (!file.is_open()) {
                std::cerr << "❌ Cannot open file: " << event.path << std::endl;
                return;
            }
            
            std::string content((std::istreambuf_iterator<char>(file)),
                               std::istreambuf_iterator<char>());
            
            // 限制内容长度
            int maxContent = std::stoi(config.getConfigValue("max_content_length", "50000"));
            if (content.length() > static_cast<size_t>(maxContent)) {
                content = content.substr(0, maxContent) + "\n... (内容已截断)";
            }
            
            // 创建数据项
            std::string itemId = "filesystem_" + utils::generateUUID();
            fs::path filePath(event.path);
            
            // 创建元数据
            json metadata = {
                {"file_path", event.path},
                {"file_name", filePath.filename().string()},
                {"file_extension", filePath.extension().string()},
                {"directory", filePath.parent_path().string()},
                {"event_type", event.eventType}
            };
            
            std::string dataItem = utils::createDataItem(itemId, content, "filesystem", metadata.dump());
            
            client.addHeader("Content-Type", "application/json");
            auto response = client.post(config.getDaemonUrl() + "/api/v1/data/ingest", dataItem);
            
            if (response.isSuccess()) {
                std::cout << "✅ Processed file event: " << filePath.filename().string() 
                         << " (" << content.length() << " chars)" << std::endl;
            } else {
                std::cerr << "❌ Failed to push file data: HTTP " << response.statusCode << std::endl;
            }
            
        } catch (const std::exception& e) {
            std::cerr << "❌ Error processing file: " << e.what() << std::endl;
        }
    } else {
        // 对于删除事件，仅记录日志
        std::cout << "🗑️  File deleted: " << fs::path(event.path).filename().string() << std::endl;
    }
}

int main(int, char*[]) {
    std::cout << "🚀 Starting Linch Mind Filesystem Connector (C++ Edition with Shared Library)" << std::endl;
    
    // 设置信号处理器
    signal(SIGINT, signalHandler);
    signal(SIGTERM, signalHandler);
    
    // 发现daemon
    DaemonDiscovery discovery;
    std::cout << "🔍 Discovering daemon..." << std::endl;
    
    auto daemonInfo = discovery.waitForDaemon(std::chrono::seconds(30));
    if (!daemonInfo) {
        std::cerr << "❌ Failed to discover daemon. Exiting..." << std::endl;
        return 1;
    }
    
    std::cout << "📡 Found daemon at: " << daemonInfo->getBaseUrl() << " (PID: " << daemonInfo->pid << ")" << std::endl;
    
    // 初始化组件
    HttpClient httpClient;
    httpClient.setTimeout(30);
    
    ConfigManager configManager(daemonInfo->getBaseUrl(), "filesystem");
    FileSystemMonitor filesystemMonitor;
    
    // 注册配置schema
    registerConfigSchema(httpClient, daemonInfo->getBaseUrl());
    
    // 加载初始配置
    if (!configManager.loadFromDaemon()) {
        std::cerr << "⚠️  Failed to load configuration from daemon, using defaults" << std::endl;
    }
    
    // 开始配置监控
    configManager.startConfigMonitoring(30);
    
    // 检查监控是否启用
    bool monitoringEnabled = configManager.getConfigValue("monitoring_enabled", "true") == "true";
    if (!monitoringEnabled) {
        std::cout << "⚠️  Filesystem monitoring is disabled in configuration" << std::endl;
        return 0;
    }
    
    // 加载监控配置
    auto watchConfigs = loadWatchConfigs(configManager);
    if (watchConfigs.empty()) {
        std::cerr << "❌ No valid watch directories configured" << std::endl;
        return 1;
    }
    
    // 添加监控配置到监控器
    for (const auto& watchConfig : watchConfigs) {
        if (!filesystemMonitor.addWatch(watchConfig)) {
            std::cerr << "⚠️  Failed to add watch for: " << watchConfig.path << std::endl;
        }
    }
    
    // 开始文件系统监控
    double pollInterval = std::stod(configManager.getConfigValue("poll_interval", "2.0"));
    int pollIntervalMs = static_cast<int>(pollInterval * 1000);
    
    std::cout << "📁 Starting filesystem monitoring (poll interval: " << pollInterval << "s)" << std::endl;
    
    if (!filesystemMonitor.startMonitoring(
        [&](const FileSystemMonitor::FileEvent& event) {
            processFilesystemEvent(event, httpClient, configManager);
        }, 
        pollIntervalMs)) {
        std::cerr << "❌ Failed to start filesystem monitoring" << std::endl;
        return 1;
    }
    
    // 主循环
    while (!g_shouldStop) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    
    // 清理
    std::cout << "🛑 Stopping filesystem connector..." << std::endl;
    filesystemMonitor.stopMonitoring();
    configManager.stopConfigMonitoring();
    
    std::cout << "📁 Filesystem connector stopped" << std::endl;
    return 0;
}