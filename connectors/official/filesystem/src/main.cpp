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
#include <uuid/uuid.h>
#include <filesystem>

#include "filesystem_monitor.hpp"
#include "http_client.hpp"
#include "config_manager.hpp"

using json = nlohmann::json;
namespace fs = std::filesystem;

// Global flag for signal handling
volatile sig_atomic_t g_shouldStop = 0;

// Signal handler
void signalHandler(int signum) {
    std::cout << "\n📁 Received signal " << signum << ", stopping filesystem monitor..." << std::endl;
    g_shouldStop = 1;
}

// Generate UUID
std::string generateUUID() {
    uuid_t uuid;
    uuid_generate(uuid);
    char uuid_str[37];
    uuid_unparse_lower(uuid, uuid_str);
    return std::string(uuid_str);
}

// Get current timestamp in ISO format
std::string getCurrentTimestamp() {
    auto now = std::chrono::system_clock::now();
    auto time_t = std::chrono::system_clock::to_time_t(now);
    char buffer[100];
    strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%S", gmtime(&time_t));
    
    // Add milliseconds
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        now.time_since_epoch()).count() % 1000;
    
    return std::string(buffer) + "." + std::to_string(ms) + "Z";
}

// Detect content type
std::string detectContentType(const std::string& content) {
    std::string content_lower = content;
    std::transform(content_lower.begin(), content_lower.end(), content_lower.begin(), ::tolower);
    
    if (content_lower.find("def ") == 0 || content_lower.find("function ") == 0 || 
        content_lower.find("class ") == 0 || content_lower.find("import ") == 0) {
        return "code";
    } else if (content_lower.find("# ") == 0 || content_lower.find("## ") == 0) {
        return "markdown";
    } else if (content.find("{") != std::string::npos && content.find("}") != std::string::npos) {
        return "json_or_config";
    } else if (content_lower.find("todo") != std::string::npos || 
               content_lower.find("fixme") != std::string::npos ||
               content_lower.find("note") != std::string::npos) {
        return "notes_or_todos";
    }
    
    return "text";
}

// Create data item for daemon
json createDataItem(const std::string& filePath, const std::string& content) {
    fs::path path(filePath);
    json item;
    item["id"] = "filesystem_" + generateUUID();
    item["content"] = content;
    item["source_connector"] = "filesystem";
    item["timestamp"] = getCurrentTimestamp();
    item["metadata"] = {
        {"file_path", filePath},
        {"file_name", path.filename().string()},
        {"file_extension", path.extension().string()},
        {"directory", path.parent_path().string()},
        {"content_length", content.length()},
        {"content_type", detectContentType(content)}
    };
    
    return item;
}

// Register config schema with daemon
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
            {"watch_directories", {
                {"type", "array"},
                {"title", "监控目录"},
                {"description", "要监控的目录列表"},
                {"items", {
                    {"type", "object"},
                    {"properties", {
                        {"path", {
                            {"type", "string"},
                            {"title", "目录路径"},
                            {"description", "要监控的目录路径"},
                            {"ui_component", "directory_picker"}
                        }},
                        {"name", {
                            {"type", "string"},
                            {"title", "显示名称"},
                            {"description", "此目录的显示名称（可选）"},
                            {"default", ""}
                        }},
                        {"enabled", {
                            {"type", "boolean"},
                            {"title", "启用监控"},
                            {"description", "是否监控此目录"},
                            {"default", true},
                            {"ui_component", "switch"}
                        }},
                        {"recursive", {
                            {"type", "boolean"},
                            {"title", "递归监控子目录"},
                            {"description", "是否监控此目录下的所有子目录"},
                            {"default", true},
                            {"ui_component", "switch"}
                        }}
                    }},
                    {"required", {"path"}}
                }},
                {"default", {
                    {
                        {"path", "~/Downloads"},
                        {"name", "下载目录"},
                        {"enabled", true},
                        {"recursive", true}
                    },
                    {
                        {"path", "~/Documents"},
                        {"name", "文档目录"},
                        {"enabled", true},
                        {"recursive", true}
                    }
                }},
                {"ui_component", "dynamic_list"}
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
        {"required", {"poll_interval", "watch_directories", "monitoring_enabled"}}
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

// Test daemon connection
bool testDaemonConnection(HttpClient& client, const std::string& daemonUrl) {
    auto response = client.get(daemonUrl + "/");
    if (response.isSuccess()) {
        std::cout << "✅ Daemon connection successful" << std::endl;
        return true;
    } else {
        std::cerr << "❌ Cannot connect to daemon: HTTP " << response.statusCode << std::endl;
        return false;
    }
}

// Load watch configurations from config manager
std::vector<FileSystemMonitor::WatchConfig> loadWatchConfigs(ConfigManager& config) {
    std::vector<FileSystemMonitor::WatchConfig> watchConfigs;
    
    // For now, use simple configuration parsing
    // In a real implementation, you'd parse the JSON array from config
    std::string watchPaths = config.getConfigValue("watch_paths", "~/Downloads,~/Documents");
    std::string supportedExts = config.getConfigValue("supported_extensions", ".txt,.md,.py,.js,.json,.yaml,.yml,.html,.css,.cpp,.hpp,.c,.h");
    std::string ignorePatterns = config.getConfigValue("ignore_patterns", "*.tmp,.*,node_modules/*,__pycache__/*,*.log,.git/*,build/*,dist/*");
    int maxFileSize = std::stoi(config.getConfigValue("max_file_size_mb", "10"));
    
    // Parse watch paths (comma-separated)
    std::stringstream ss(watchPaths);
    std::string path;
    while (std::getline(ss, path, ',')) {
        // Trim whitespace
        path.erase(0, path.find_first_not_of(" \t"));
        path.erase(path.find_last_not_of(" \t") + 1);
        
        // Expand ~ to home directory
        if (path.substr(0, 2) == "~/") {
            path = std::string(std::getenv("HOME")) + path.substr(1);
        }
        
        if (!path.empty() && fs::exists(path) && fs::is_directory(path)) {
            FileSystemMonitor::WatchConfig watchConfig(path);
            watchConfig.name = fs::path(path).filename().string();
            watchConfig.enabled = true;
            watchConfig.recursive = true;
            watchConfig.maxFileSize = maxFileSize * 1024 * 1024; // Convert to bytes
            
            // Parse supported extensions
            std::stringstream extSs(supportedExts);
            std::string ext;
            while (std::getline(extSs, ext, ',')) {
                ext.erase(0, ext.find_first_not_of(" \t"));
                ext.erase(ext.find_last_not_of(" \t") + 1);
                if (!ext.empty()) {
                    watchConfig.supportedExtensions.insert(ext);
                }
            }
            
            // Parse ignore patterns
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

// Process filesystem event
void processFilesystemEvent(const FileSystemMonitor::FileEvent& event, 
                           HttpClient& client, ConfigManager& config) {
    std::cout << "📁 Processing file event: " << event.eventType << " - " << event.path << std::endl;
    
    // For created and modified events, read the file content
    if (event.eventType == "created" || event.eventType == "modified") {
        try {
            std::ifstream file(event.path);
            if (!file.is_open()) {
                std::cerr << "❌ Cannot open file: " << event.path << std::endl;
                return;
            }
            
            std::string content((std::istreambuf_iterator<char>(file)),
                               std::istreambuf_iterator<char>());
            
            // Limit content length
            int maxContent = std::stoi(config.getConfigValue("max_content_length", "50000"));
            if (content.length() > static_cast<size_t>(maxContent)) {
                content = content.substr(0, maxContent) + "\n... (内容已截断)";
            }
            
            // Create and send data item
            json dataItem = createDataItem(event.path, content);
            
            client.addHeader("Content-Type", "application/json");
            auto response = client.post(config.getDaemonUrl() + "/api/v1/data/ingest", 
                                       dataItem.dump());
            
            if (response.isSuccess()) {
                std::cout << "✅ Processed file event: " << fs::path(event.path).filename().string() 
                         << " (" << content.length() << " chars)" << std::endl;
            } else {
                std::cerr << "❌ Failed to push file data: HTTP " << response.statusCode << std::endl;
            }
            
        } catch (const std::exception& e) {
            std::cerr << "❌ Error processing file: " << e.what() << std::endl;
        }
    } else {
        // For deleted events, just log
        std::cout << "🗑️  File deleted: " << fs::path(event.path).filename().string() << std::endl;
    }
}

int main(int, char*[]) {
    std::cout << "🚀 Starting Linch Mind Filesystem Connector (C++ Edition)" << std::endl;
    
    // Setup signal handlers
    signal(SIGINT, signalHandler);
    signal(SIGTERM, signalHandler);
    
    // Get daemon URL from environment or use default
    std::string daemonUrl = std::getenv("DAEMON_URL") ? std::getenv("DAEMON_URL") : "http://localhost:58471";
    std::cout << "📡 Daemon URL: " << daemonUrl << std::endl;
    
    // Initialize components
    HttpClient httpClient;
    httpClient.setTimeout(30);
    
    ConfigManager configManager(daemonUrl, "filesystem");
    FileSystemMonitor filesystemMonitor;
    
    // Test daemon connection
    if (!testDaemonConnection(httpClient, daemonUrl)) {
        std::cerr << "❌ Failed to connect to daemon. Exiting..." << std::endl;
        return 1;
    }
    
    // Register config schema
    registerConfigSchema(httpClient, daemonUrl);
    
    // Load initial configuration
    if (!configManager.loadFromDaemon()) {
        std::cerr << "⚠️  Failed to load configuration from daemon, using defaults" << std::endl;
    }
    
    // Start config monitoring
    configManager.startConfigMonitoring(30);
    
    // Check if monitoring is enabled
    bool monitoringEnabled = configManager.getConfigValue("monitoring_enabled", "true") == "true";
    if (!monitoringEnabled) {
        std::cout << "⚠️  Filesystem monitoring is disabled in configuration" << std::endl;
        return 0;
    }
    
    // Load watch configurations
    auto watchConfigs = loadWatchConfigs(configManager);
    if (watchConfigs.empty()) {
        std::cerr << "❌ No valid watch directories configured" << std::endl;
        return 1;
    }
    
    // Add watch configurations to monitor
    for (const auto& watchConfig : watchConfigs) {
        if (!filesystemMonitor.addWatch(watchConfig)) {
            std::cerr << "⚠️  Failed to add watch for: " << watchConfig.path << std::endl;
        }
    }
    
    // Start filesystem monitoring
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
    
    // Main loop
    while (!g_shouldStop) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    
    // Cleanup
    std::cout << "🛑 Stopping filesystem connector..." << std::endl;
    filesystemMonitor.stopMonitoring();
    configManager.stopConfigMonitoring();
    
    std::cout << "📁 Filesystem connector stopped" << std::endl;
    return 0;
}