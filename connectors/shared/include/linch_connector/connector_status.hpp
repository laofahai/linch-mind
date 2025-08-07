#pragma once

#include <string>
#include <chrono>
#include <nlohmann/json.hpp>

namespace linch_connector {

/**
 * 连接器运行状态 - 与Python端完全一致
 */
enum class ConnectorRunningState {
    STOPPED = 0,     // "stopped" - 已停止
    STARTING,        // "starting" - 启动中
    RUNNING,         // "running" - 正在运行
    STOPPING,        // "stopping" - 停止中
    ERROR            // "error" - 错误状态
};

/**
 * 运行状态字符串转换
 */
class RunningStateHelper {
public:
    static std::string toString(ConnectorRunningState state) {
        switch (state) {
            case ConnectorRunningState::STOPPED: return "stopped";
            case ConnectorRunningState::STARTING: return "starting";
            case ConnectorRunningState::RUNNING: return "running";
            case ConnectorRunningState::STOPPING: return "stopping";
            case ConnectorRunningState::ERROR: return "error";
            default: return "stopped";
        }
    }
    
    static ConnectorRunningState fromString(const std::string& state) {
        if (state == "stopped") return ConnectorRunningState::STOPPED;
        if (state == "starting") return ConnectorRunningState::STARTING;
        if (state == "running") return ConnectorRunningState::RUNNING;
        if (state == "stopping") return ConnectorRunningState::STOPPING;
        if (state == "error") return ConnectorRunningState::ERROR;
        return ConnectorRunningState::STOPPED;
    }
};

/**
 * 连接器完整状态信息 - V2版本
 * 
 * 设计理念：
 * - enabled: 基本状态，是否启用（由daemon管理）
 * - running_state: 运行状态，表示实际运行情况（由connector管理）
 * - is_installed: 虚拟字段（由daemon计算）
 */
struct ConnectorStatusV2 {
    std::string connector_id;
    std::string display_name;
    bool enabled = true;                                             // 是否启用（基本状态）
    ConnectorRunningState running_state = ConnectorRunningState::STOPPED; // 运行状态
    
    // 进程信息
    int process_id = 0;
    std::chrono::system_clock::time_point last_heartbeat;
    
    // 统计信息
    int data_count = 0;
    std::string last_activity;
    
    // 错误信息
    std::string error_message;
    std::string error_code;
    
    // 转换为JSON（发送给daemon）- 使用纯IPC格式
    nlohmann::json toIPCJson() const {
        nlohmann::json j = {
            {"connector_id", connector_id},
            {"display_name", display_name},
            {"enabled", enabled},
            {"running_state", RunningStateHelper::toString(running_state)},
            {"process_id", process_id},
            {"data_count", data_count}
        };
        
        if (!last_activity.empty()) {
            j["last_activity"] = last_activity;
        }
        
        if (!error_message.empty()) {
            j["error_message"] = error_message;
        }
        
        if (!error_code.empty()) {
            j["error_code"] = error_code;
        }
        
        return j;
    }
    
    // 从JSON解析（从daemon接收）
    static ConnectorStatusV2 fromIPCJson(const nlohmann::json& json) {
        ConnectorStatusV2 status;
        
        if (json.contains("connector_id")) {
            status.connector_id = json["connector_id"].get<std::string>();
        }
        
        if (json.contains("display_name")) {
            status.display_name = json["display_name"].get<std::string>();
        }
        
        if (json.contains("enabled")) {
            status.enabled = json["enabled"].get<bool>();
        }
        
        if (json.contains("running_state")) {
            std::string state_str = json["running_state"].get<std::string>();
            status.running_state = RunningStateHelper::fromString(state_str);
        }
        
        if (json.contains("process_id")) {
            status.process_id = json["process_id"].get<int>();
        }
        
        if (json.contains("data_count")) {
            status.data_count = json["data_count"].get<int>();
        }
        
        if (json.contains("last_activity")) {
            status.last_activity = json["last_activity"].get<std::string>();
        }
        
        if (json.contains("error_message")) {
            status.error_message = json["error_message"].get<std::string>();
        }
        
        if (json.contains("error_code")) {
            status.error_code = json["error_code"].get<std::string>();
        }
        
        return status;
    }
    
    // 更新心跳时间
    void updateHeartbeat() {
        last_heartbeat = std::chrono::system_clock::now();
        // 如果是启动中状态，心跳后变为运行状态
        if (running_state == ConnectorRunningState::STARTING) {
            running_state = ConnectorRunningState::RUNNING;
        }
    }
    
    // 设置错误状态
    void setError(const std::string& message, const std::string& code = "") {
        running_state = ConnectorRunningState::ERROR;
        error_message = message;
        error_code = code;
    }
    
    // 清除错误状态
    void clearError() {
        error_message.clear();
        error_code.clear();
        if (running_state == ConnectorRunningState::ERROR) {
            running_state = ConnectorRunningState::STOPPED;
        }
    }
    
    // 检查是否健康
    bool isHealthy() const {
        return enabled && running_state == ConnectorRunningState::RUNNING;
    }
    
    // 检查是否应该运行
    bool shouldBeRunning() const {
        return enabled;
    }
};

/**
 * 连接器状态管理器
 * 使用纯IPC协议与daemon通信
 */
class ConnectorStatusManager {
public:
    ConnectorStatusManager(const std::string& connector_id, const std::string& display_name);
    
    // 状态管理
    void setState(ConnectorRunningState state);
    void setError(const std::string& error_message, const std::string& error_code = "");
    void setDataCount(int count);
    void setLastActivity(const std::string& activity);
    void clearError();
    
    // 获取状态
    const ConnectorStatusV2& getStatus() const { return status_; }
    
    // 与daemon通信 - 使用纯IPC协议
    bool sendHeartbeat(class UnifiedClient& client);
    bool sendStatusUpdate(class UnifiedClient& client);
    
    // 启动时通知daemon
    bool notifyStarting(class UnifiedClient& client);
    
    // 停止时通知daemon
    bool notifyStopping(class UnifiedClient& client);
    
private:
    ConnectorStatusV2 status_;
    std::chrono::system_clock::time_point last_heartbeat_sent_;
    
    static constexpr int HEARTBEAT_INTERVAL_SECONDS = 30;
    
    // 内部方法：发送IPC响应
    bool sendIPCUpdate(class UnifiedClient& client, const std::string& endpoint, const nlohmann::json& data);
};

// 工厂函数
ConnectorStatusV2 createNewConnectorStatus(const std::string& connector_id, const std::string& display_name);

} // namespace linch_connector