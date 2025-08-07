#include "linch_connector/connector_status.hpp"
#include "linch_connector/unified_client.hpp"
#include <iostream>
#include <unistd.h>

namespace linch_connector {

ConnectorStatusManager::ConnectorStatusManager(const std::string& connector_id, const std::string& display_name) {
    status_.connector_id = connector_id;
    status_.display_name = display_name;
    status_.enabled = true;
    status_.running_state = ConnectorRunningState::STOPPED;
    status_.process_id = getpid();
    last_heartbeat_sent_ = std::chrono::system_clock::now();
}

void ConnectorStatusManager::setState(ConnectorRunningState state) {
    status_.running_state = state;
    status_.clearError(); // 状态改变时清除错误
}

void ConnectorStatusManager::setError(const std::string& error_message, const std::string& error_code) {
    status_.setError(error_message, error_code);
}

void ConnectorStatusManager::setDataCount(int count) {
    status_.data_count = count;
}

void ConnectorStatusManager::setLastActivity(const std::string& activity) {
    status_.last_activity = activity;
}

void ConnectorStatusManager::clearError() {
    status_.clearError();
}

bool ConnectorStatusManager::sendHeartbeat(UnifiedClient& client) {
    auto now = std::chrono::system_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::seconds>(now - last_heartbeat_sent_);
    
    if (duration.count() < HEARTBEAT_INTERVAL_SECONDS) {
        return true; // 还未到发送时间
    }
    
    // 准备心跳数据 - 使用纯IPC格式
    nlohmann::json heartbeat_data = {
        {"connector_id", status_.connector_id},
        {"process_id", status_.process_id},
        {"running_state", RunningStateHelper::toString(status_.running_state)},
        {"data_count", status_.data_count},
        {"timestamp", std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count()}
    };
    
    if (!status_.error_message.empty()) {
        heartbeat_data["error_message"] = status_.error_message;
        heartbeat_data["error_code"] = status_.error_code;
    }
    
    bool success = sendIPCUpdate(client, "/heartbeat", heartbeat_data);
    
    if (success) {
        last_heartbeat_sent_ = now;
        status_.updateHeartbeat();
        std::cout << "[INFO] Heartbeat sent successfully for " << status_.connector_id << std::endl;
    } else {
        std::cerr << "[ERROR] Failed to send heartbeat for " << status_.connector_id << std::endl;
    }
    
    return success;
}

bool ConnectorStatusManager::sendStatusUpdate(UnifiedClient& client) {
    // 发送完整状态更新
    nlohmann::json status_data = status_.toIPCJson();
    
    std::string endpoint = "/connectors/" + status_.connector_id + "/status";
    bool success = sendIPCUpdate(client, endpoint, status_data);
    
    if (success) {
        std::cout << "[INFO] Status update sent successfully for " << status_.connector_id << std::endl;
    } else {
        std::cerr << "[ERROR] Failed to send status update for " << status_.connector_id << std::endl;
    }
    
    return success;
}

bool ConnectorStatusManager::notifyStarting(UnifiedClient& client) {
    setState(ConnectorRunningState::STARTING);
    
    nlohmann::json starting_data = {
        {"connector_id", status_.connector_id},
        {"running_state", "starting"},
        {"process_id", status_.process_id},
        {"message", "Connector is starting"}
    };
    
    std::string endpoint = "/connectors/" + status_.connector_id + "/status";
    bool success = sendIPCUpdate(client, endpoint, starting_data);
    
    if (success) {
        std::cout << "[INFO] Starting notification sent for " << status_.connector_id << std::endl;
    }
    
    return success;
}

bool ConnectorStatusManager::notifyStopping(UnifiedClient& client) {
    setState(ConnectorRunningState::STOPPING);
    
    nlohmann::json stopping_data = {
        {"connector_id", status_.connector_id},
        {"running_state", "stopping"},
        {"process_id", status_.process_id},
        {"message", "Connector is stopping"}
    };
    
    std::string endpoint = "/connectors/" + status_.connector_id + "/status";
    bool success = sendIPCUpdate(client, endpoint, stopping_data);
    
    if (success) {
        std::cout << "[INFO] Stopping notification sent for " << status_.connector_id << std::endl;
    }
    
    return success;
}

bool ConnectorStatusManager::sendIPCUpdate(UnifiedClient& client, const std::string& endpoint, const nlohmann::json& data) {
    try {
        // 使用纯IPC协议格式发送
        std::string json_data = data.dump();
        auto response = client.post(endpoint, json_data);
        
        if (response.isSuccess()) { // IPC通信成功
            return true;
        } else {
            std::cerr << "[ERROR] IPC communication failed - " 
                      << response.error_code << ": " << response.error_message << std::endl;
            return false;
        }
    } catch (const std::exception& e) {
        std::cerr << "[ERROR] Exception in sendIPCUpdate: " << e.what() << std::endl;
        return false;
    }
}

// 工厂函数实现
ConnectorStatusV2 createNewConnectorStatus(const std::string& connector_id, const std::string& display_name) {
    ConnectorStatusV2 status;
    status.connector_id = connector_id;
    status.display_name = display_name;
    status.enabled = true;
    status.running_state = ConnectorRunningState::STOPPED;
    status.process_id = getpid();
    return status;
}

} // namespace linch_connector