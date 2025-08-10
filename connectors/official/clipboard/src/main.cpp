#include <iostream>
#include <string>
#include <chrono>
#include <thread>
#include <signal.h>
#include <cstdlib>
#include <nlohmann/json.hpp>

// 使用shared库
#include <linch_connector/daemon_discovery.hpp>
#include <linch_connector/config_manager.hpp>
#include <linch_connector/unified_client.hpp>
#include <linch_connector/utils.hpp>
#include <linch_connector/connector_status.hpp>

// 本地头文件
#include "clipboard_monitor.hpp"

using json = nlohmann::json;
using namespace linch_connector;

// 全局标志位用于信号处理
volatile sig_atomic_t g_shouldStop = 0;

// 信号处理器
void signalHandler(int signum) {
    std::cout << "\n📋 Received signal " << signum << ", stopping clipboard monitor..." << std::endl;
    g_shouldStop = 1;
}

// 注册配置schema到daemon
bool registerConfigSchema(UnifiedClient& client, const std::string& daemonUrl) {
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

    // 注意：新API不再支持注册schema，跳过此步骤
    // auto response = client.post(daemonUrl + "/connector-config/register-schema/clipboard", 
    //                            payload.dump());
    
    // 临时跳过schema注册，直接返回成功
    std::cout << "⚠️  Schema registration skipped (new API doesn't support it)" << std::endl;
    return true;
}

// 处理剪贴板变化的函数已被内联到callback中，使用通用事件API

int main(int argc, char* argv[]) {
    std::cout << "🚀 Starting Linch Mind Clipboard Connector (Pure IPC)" << std::endl;
    
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
    unifiedClient.setTimeout(30);
    
    if (!unifiedClient.connect(*daemonInfoOpt)) {
        std::cerr << "❌ Failed to connect to daemon. Exiting..." << std::endl;
        return 1;
    }
    
    std::cout << "🔗 Connected to daemon via IPC." << std::endl;
    
    // 初始化状态管理器
    ConnectorStatusManager statusManager("clipboard", "剪贴板连接器");
    statusManager.setState(ConnectorRunningState::STARTING);
    statusManager.notifyStarting(unifiedClient);
    
    // 修正：ConfigManager构造函数参数顺序是(connectorId, daemonUrl)
    ConfigManager configManager("clipboard", "");
    if (!configManager.loadFromDaemon()) {
        std::cerr << "⚠️  Failed to load configuration from daemon, using defaults" << std::endl;
    }
    
    // Schema registration is handled by the daemon.

    ClipboardMonitor clipboardMonitor;
    
    std::cout << "📋 Starting clipboard monitoring..." << std::endl;
    
    // Create callback to handle clipboard changes using generic events API
    auto clipboardCallback = [&unifiedClient, &configManager](const std::string& content) {
        if (content.length() < static_cast<size_t>(configManager.getMinContentLength()) ||
            content.length() > static_cast<size_t>(configManager.getMaxContentLength())) {
            return; // Skip content outside length bounds
        }
        
        // Create clipboard event data for generic API
        nlohmann::json clipboard_event_data = {
            {"content", content},
            {"content_length", content.length()},
            {"content_type", "text/plain"},
            {"source", "system_clipboard"}
        };
        
        nlohmann::json event_data = {
            {"connector_id", "clipboard"},
            {"event_type", "content_changed"},
            {"event_data", clipboard_event_data},
            {"timestamp", utils::getCurrentTimestamp()},
            {"metadata", {}}
        };
        
        auto response = unifiedClient.post("/events/submit", event_data.dump());
        if (response.success) {
            std::cout << "✅ Sent clipboard event: " << content.length() << " chars" << std::endl;
        } else {
            std::cerr << "❌ Failed to send clipboard event: " << response.error_message << std::endl;
        }
    };
    
    if (!clipboardMonitor.startMonitoring(clipboardCallback, 
                                         static_cast<int>(configManager.getCheckInterval() * 1000))) {
        std::cerr << "❌ Failed to start clipboard monitoring" << std::endl;
        statusManager.setError("Failed to start clipboard monitoring");
        statusManager.sendStatusUpdate(unifiedClient);
        return 1;
    }
    
    // 设置为运行状态
    statusManager.setState(ConnectorRunningState::RUNNING);
    statusManager.sendStatusUpdate(unifiedClient);
    
    std::cout << "✅ Clipboard connector is now running with heartbeat support" << std::endl;
    
    // 主循环 - 加入心跳发送
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
    std::cout << "🛑 Stopping clipboard connector..." << std::endl;
    statusManager.setState(ConnectorRunningState::STOPPING);
    statusManager.notifyStopping(unifiedClient);
    
    clipboardMonitor.stopMonitoring();
    
    std::cout << "📋 Clipboard connector stopped" << std::endl;
    return 0;
}