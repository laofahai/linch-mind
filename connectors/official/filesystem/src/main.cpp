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

// 注册配置schema到daemon
bool registerConfigSchema(UnifiedClient& client, const std::string& daemonUrl) {
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

    // 注意：新API不再支持注册schema，跳过此步骤
    // auto response = client.post(daemonUrl + "/connector-config/register-schema/filesystem", 
    //                            payload.dump());
    
    // 临时跳过schema注册，直接返回成功
    std::cout << "⚠️  Schema registration skipped (new API doesn't support it)" << std::endl;
    return true;
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
                           UnifiedClient& client, ConfigManager& config) {
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
            
            // 使用新的storage API创建实体
            json entity_data = {
                {"entity_id", itemId},
                {"name", filePath.filename().string()},
                {"entity_type", "file"},
                {"description", "File from filesystem connector"},
                {"attributes", metadata},
                {"source_path", event.path},
                {"content", content},
                {"auto_embed", true}
            };
            
            auto response = client.post("/storage/entities", entity_data.dump());
            
            if (response.success) {
                std::cout << "✅ Processed file event: " << filePath.filename().string() 
                         << " (" << content.length() << " chars)" << std::endl;
            } else {
                std::cerr << "❌ Failed to push file data: " << response.error_message 
                          << " (code: " << response.error_code << ")" << std::endl;
            }
            
        } catch (const std::exception& e) {
            std::cerr << "❌ Error processing file: " << e.what() << std::endl;
        }
    } else {
        // 对于删除事件，仅记录日志
        std::cout << "🗑️  File deleted: " << fs::path(event.path).filename().string() << std::endl;
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

    // Schema registration is handled by the daemon.

    FileSystemMonitor monitor;

    // Create callback to handle filesystem changes
    auto filesystemCallback = [&unifiedClient, &configManager](const FileSystemMonitor::FileEvent& event) {
        processFilesystemEvent(event, unifiedClient, configManager);
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