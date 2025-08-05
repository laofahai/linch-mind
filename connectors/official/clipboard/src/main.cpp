#include <iostream>
#include <string>
#include <chrono>
#include <thread>
#include <signal.h>
#include <cstdlib>
#include <algorithm>
#include <nlohmann/json.hpp>
#include <uuid/uuid.h>

#include "clipboard_monitor.hpp"
#include "http_client.hpp"
#include "config_manager.hpp"

using json = nlohmann::json;

// Global flag for signal handling
volatile sig_atomic_t g_shouldStop = 0;

// Signal handler
void signalHandler(int signum) {
    std::cout << "\n📋 Received signal " << signum << ", stopping clipboard monitor..." << std::endl;
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
    
    if (content_lower.find("http://") == 0 || content_lower.find("https://") == 0) {
        return "url";
    } else if (content_lower.find("def ") == 0 || content_lower.find("function ") == 0 || 
               content_lower.find("class ") == 0 || content_lower.find("import ") == 0) {
        return "code";
    } else if (content.find("@") != std::string::npos && content.find(".") != std::string::npos) {
        return "email_or_contact";
    } else if (content_lower.find("todo") != std::string::npos || 
               content_lower.find("task") != std::string::npos ||
               content_lower.find("deadline") != std::string::npos) {
        return "task_or_reminder";
    }
    
    return "text";
}

// Create data item for daemon
json createDataItem(const std::string& content) {
    json item;
    item["id"] = "clipboard_" + generateUUID();
    item["content"] = content;
    item["source_connector"] = "clipboard";
    item["timestamp"] = getCurrentTimestamp();
    item["metadata"] = {
        {"content_length", content.length()},
        {"content_type", detectContentType(content)}
    };
    
    return item;
}

// Register config schema with daemon
bool registerConfigSchema(HttpClient& client, const std::string& daemonUrl) {
    json schema = {
        {"type", "object"},
        {"title", "剪贴板连接器配置"},
        {"description", "配置剪贴板监控的检查间隔和内容过滤规则"},
        {"properties", {
            {"check_interval", {
                {"type", "number"},
                {"title", "检查间隔 (秒)"},
                {"description", "剪贴板内容检查的间隔时间"},
                {"default", 1.0},
                {"minimum", 0.5},
                {"maximum", 10.0},
                {"ui_component", "number_input"}
            }},
            {"min_content_length", {
                {"type", "integer"},
                {"title", "最小内容长度"},
                {"description", "过滤掉短于此长度的剪贴板内容"},
                {"default", 5},
                {"minimum", 1},
                {"maximum", 100},
                {"ui_component", "number_input"}
            }},
            {"max_content_length", {
                {"type", "integer"},
                {"title", "最大内容长度"},
                {"description", "超过此长度的内容将被截断"},
                {"default", 50000},
                {"minimum", 1000},
                {"maximum", 100000},
                {"ui_component", "number_input"}
            }},
            {"content_filters", {
                {"type", "object"},
                {"title", "内容过滤设置"},
                {"properties", {
                    {"filter_urls", {
                        {"type", "boolean"},
                        {"title", "过滤URL"},
                        {"description", "是否跳过纯URL内容"},
                        {"default", false},
                        {"ui_component", "switch"}
                    }},
                    {"filter_sensitive", {
                        {"type", "boolean"},
                        {"title", "过滤敏感内容"},
                        {"description", "跳过可能包含密码或密钥的内容"},
                        {"default", true},
                        {"ui_component", "switch"}
                    }}
                }}
            }}
        }},
        {"required", {"check_interval", "min_content_length", "max_content_length"}}
    };

    json payload = {
        {"connector_id", "clipboard"},
        {"config_schema", schema},
        {"ui_schema", json::object()},
        {"connector_name", "ClipboardConnector"},
        {"connector_description", "剪贴板连接器 - 监控剪贴板变化并推送到Daemon"},
        {"schema_source", "embedded"}
    };

    client.addHeader("Content-Type", "application/json");
    auto response = client.post(daemonUrl + "/connector-config/register-schema/clipboard", 
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

// Process clipboard change
void processClipboardChange(const std::string& content, HttpClient& client, 
                          ConfigManager& config) {
    // Check content length
    int minLength = config.getMinContentLength();
    if (content.length() < static_cast<size_t>(minLength)) {
        std::cout << "📋 Skipping short clipboard content" << std::endl;
        return;
    }
    
    int maxLength = config.getMaxContentLength();
    std::string processedContent = content;
    if (content.length() > static_cast<size_t>(maxLength)) {
        processedContent = content.substr(0, maxLength) + "\n... (内容已截断)";
        std::cout << "📋 Clipboard content truncated" << std::endl;
    }
    
    // Create and send data item
    json dataItem = createDataItem(processedContent);
    
    client.addHeader("Content-Type", "application/json");
    auto response = client.post(config.getDaemonUrl() + "/api/v1/data/ingest", 
                               dataItem.dump());
    
    if (response.isSuccess()) {
        std::cout << "✅ Processed clipboard change: " << content.length() << " chars" << std::endl;
    } else {
        std::cerr << "❌ Failed to push clipboard data: HTTP " << response.statusCode << std::endl;
    }
}

int main(int argc, char* argv[]) {
    std::cout << "🚀 Starting Linch Mind Clipboard Connector (C++ Edition)" << std::endl;
    
    // Setup signal handlers
    signal(SIGINT, signalHandler);
    signal(SIGTERM, signalHandler);
    
    // Get daemon URL from environment or use default
    std::string daemonUrl = std::getenv("DAEMON_URL") ? std::getenv("DAEMON_URL") : "http://localhost:58471";
    std::cout << "📡 Daemon URL: " << daemonUrl << std::endl;
    
    // Initialize components
    HttpClient httpClient;
    httpClient.setTimeout(30);
    
    ConfigManager configManager(daemonUrl);
    ClipboardMonitor clipboardMonitor;
    
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
    
    // Start clipboard monitoring
    double checkInterval = configManager.getCheckInterval();
    int intervalMs = static_cast<int>(checkInterval * 1000);
    
    std::cout << "📋 Starting clipboard monitoring (interval: " << checkInterval << "s)" << std::endl;
    
    if (!clipboardMonitor.startMonitoring(
        [&](const std::string& content) {
            processClipboardChange(content, httpClient, configManager);
        }, 
        intervalMs)) {
        std::cerr << "❌ Failed to start clipboard monitoring" << std::endl;
        return 1;
    }
    
    // Main loop
    while (!g_shouldStop) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    
    // Cleanup
    std::cout << "🛑 Stopping clipboard connector..." << std::endl;
    clipboardMonitor.stopMonitoring();
    configManager.stopConfigMonitoring();
    
    std::cout << "📋 Clipboard connector stopped" << std::endl;
    return 0;
}