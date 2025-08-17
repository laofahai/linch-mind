#include "linch_connector/unified_client.hpp"
#include <iostream>
#include <unistd.h>
#include <nlohmann/json.hpp>

namespace linch_connector {

class UnifiedClient::Impl {
public:
    std::unique_ptr<IPCClient> ipc_client;
    bool connected = false;

    Impl() = default;

    bool connect(const DaemonInfo& daemonInfo) {
        ipc_client = std::make_unique<IPCClient>();
        
        // 根据socket_type连接
        if (daemonInfo.socket_type == "unix") {
            connected = ipc_client->connectUnixSocket(daemonInfo.socket_path);
        } else if (daemonInfo.socket_type == "pipe") {
            connected = ipc_client->connectNamedPipe(daemonInfo.socket_path);
        } else {
            std::cerr << "[UnifiedClient] Unknown socket type: " << daemonInfo.socket_type << std::endl;
            connected = false;
        }
        
        if (connected) {
            std::cout << "[UnifiedClient] Connected to daemon via IPC: " << daemonInfo.socket_path << std::endl;
            
            // 进行认证握手
            if (!performAuthentication()) {
                std::cerr << "[UnifiedClient] Authentication failed" << std::endl;
                connected = false;
                return false;
            }
        }
        return connected;
    }
    
    bool performAuthentication() {
        // 构造认证请求
        nlohmann::json auth_data = {
            {"client_pid", getpid()},
            {"client_type", "connector"}
        };
        
        auto response = ipc_client->post("/auth/handshake", auth_data.dump());
        
        if (response.success && !response.body.empty()) {
            try {
                auto json_response = nlohmann::json::parse(response.body);
                
                // Debug: 输出完整的认证响应
                std::cout << "[UnifiedClient DEBUG] Full auth response: " << json_response.dump(2) << std::endl;
                
                // 处理两种可能的响应格式
                bool authenticated = false;
                
                // 格式1: 直接在根级别有authenticated字段 (IPCClient可能只返回data部分)
                if (json_response.contains("authenticated")) {
                    std::cout << "[UnifiedClient DEBUG] Found authenticated field at root level" << std::endl;
                    if (json_response["authenticated"].is_boolean()) {
                        authenticated = json_response["authenticated"];
                    } else if (json_response["authenticated"].is_string()) {
                        std::string auth_str = json_response["authenticated"];
                        authenticated = (auth_str == "true" || auth_str == "True");
                    }
                }
                // 格式2: 完整的IPC响应格式 (success -> data -> authenticated)
                else if (json_response.contains("success") && json_response["success"].is_boolean()) {
                    bool ipc_success = json_response["success"];
                    std::cout << "[UnifiedClient DEBUG] Found IPC success field: " << ipc_success << std::endl;
                    
                    if (ipc_success && json_response.contains("data") && !json_response["data"].is_null()) {
                        auto data = json_response["data"];
                        std::cout << "[UnifiedClient DEBUG] Data section: " << data.dump(2) << std::endl;
                        
                        if (data.contains("authenticated")) {
                            if (data["authenticated"].is_boolean()) {
                                authenticated = data["authenticated"];
                            } else if (data["authenticated"].is_string()) {
                                std::string auth_str = data["authenticated"];
                                authenticated = (auth_str == "true" || auth_str == "True");
                            }
                        }
                    } else if (!ipc_success) {
                        std::cerr << "[UnifiedClient] IPC request failed" << std::endl;
                        if (json_response.contains("error") && !json_response["error"].is_null()) {
                            auto error = json_response["error"];
                            std::cerr << "[UnifiedClient] Server error: " << error.dump() << std::endl;
                        }
                        return false;
                    }
                } else {
                    std::cerr << "[UnifiedClient] Unrecognized response format" << std::endl;
                }
                
                std::cout << "[UnifiedClient DEBUG] Final authenticated value: " << authenticated << std::endl;
                
                if (authenticated) {
                    std::cout << "[UnifiedClient] Authentication successful" << std::endl;
                    return true;
                } else {
                    std::cerr << "[UnifiedClient] Authentication failed - authenticated=false" << std::endl;
                }
                
                std::cerr << "[UnifiedClient] Authentication failed - see debug output above" << std::endl;
                return false;
            } catch (const std::exception& e) {
                std::cerr << "[UnifiedClient] Failed to parse auth response: " << e.what() << std::endl;
                std::cerr << "[UnifiedClient] Response body: " << response.body << std::endl;
                return false;
            }
        } else {
            std::cerr << "[UnifiedClient] Authentication request failed: " << response.error_message << std::endl;
            return false;
        }
    }

    IPCClient::IPCResponse sendRequest(const std::string& method, const std::string& path, const std::string& data = "") {
        if (!connected || !ipc_client) {
            IPCClient::IPCResponse error_resp;
            error_resp.success = false;
            error_resp.error_code = "CONNECTION_ERROR";
            error_resp.error_message = "Not connected to daemon";
            return error_resp;
        }
        
        // 使用IPCClient的get或post方法
        if (method == "GET") {
            return ipc_client->get(path);
        } else if (method == "POST") {
            return ipc_client->post(path, data);
        } else {
            IPCClient::IPCResponse error_resp;
            error_resp.success = false;
            error_resp.error_code = "METHOD_ERROR";
            error_resp.error_message = "Unsupported method: " + method;
            return error_resp;
        }
    }

    void addHeader(const std::string& /* key */, const std::string& /* value */) {
        // IPC client does not use headers, this is a no-op.
    }

    void setTimeout(int timeout_seconds) {
        if (ipc_client) {
            ipc_client->setTimeout(timeout_seconds);
        }
    }
};

UnifiedClient::UnifiedClient() : pImpl(std::make_unique<Impl>()) {}

UnifiedClient::~UnifiedClient() = default;

bool UnifiedClient::connect(const DaemonInfo& daemonInfo) {
    return pImpl->connect(daemonInfo);
}

IPCClient::IPCResponse UnifiedClient::get(const std::string& path) {
    return pImpl->sendRequest("GET", path);
}

IPCClient::IPCResponse UnifiedClient::post(const std::string& path, const std::string& jsonData) {
    return pImpl->sendRequest("POST", path, jsonData);
}

void UnifiedClient::addHeader(const std::string& key, const std::string& value) {
    pImpl->addHeader(key, value);
}

void UnifiedClient::setTimeout(int timeout_seconds) {
    pImpl->setTimeout(timeout_seconds);
}

bool UnifiedClient::isConnected() const {
    return pImpl->connected;
}

} // namespace linch_connector