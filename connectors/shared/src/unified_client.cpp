#include "linch_connector/unified_client.hpp"
#include <iostream>

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
        }
        return connected;
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

    void addHeader(const std::string& key, const std::string& value) {
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