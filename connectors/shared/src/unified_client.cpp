#include "linch_connector/unified_client.hpp"
#include <iostream>
#include <sstream>

namespace linch_connector {

class UnifiedClient::Impl {
public:
    std::unique_ptr<HttpClient> http_client;
    std::unique_ptr<IPCClient> ipc_client;
    std::string connection_mode;
    bool connected;
    std::string daemon_base_url;  // HTTP模式的基础URL

    Impl() : connected(false) {
        http_client = std::make_unique<HttpClient>();
        ipc_client = std::make_unique<IPCClient>();
    }

    bool connect(const DaemonInfo& daemonInfo) {
        connected = false;
        connection_mode.clear();
        
        if (daemonInfo.isIPCMode()) {
            // IPC模式连接
#ifdef _WIN32
            if (!daemonInfo.pipe_name.empty()) {
                if (ipc_client->connectNamedPipe(daemonInfo.pipe_name)) {
                    connection_mode = "ipc";
                    connected = true;
                    std::cout << "[UnifiedClient] 已连接到daemon (IPC Named Pipe)" << std::endl;
                    return true;
                }
            }
#else
            if (!daemonInfo.socket_path.empty()) {
                if (ipc_client->connectUnixSocket(daemonInfo.socket_path)) {
                    connection_mode = "ipc";
                    connected = true;
                    std::cout << "[UnifiedClient] 已连接到daemon (IPC Unix Socket)" << std::endl;
                    return true;
                }
            }
#endif
        } else {
            // HTTP模式连接
            daemon_base_url = daemonInfo.getBaseUrl();
            connection_mode = "http";
            connected = true;  // HTTP客户端不需要预连接
            std::cout << "[UnifiedClient] 配置为HTTP模式: " << daemon_base_url << std::endl;
            return true;
        }
        
        return false;
    }
    
    Response sendRequest(const std::string& method, const std::string& url_or_path, 
                        const std::string& data = "") {
        if (!connected) {
            Response error_resp;
            error_resp.statusCode = 500;
            error_resp.body = "Not connected to daemon";
            return error_resp;
        }
        
        // 仅支持IPC模式 - HTTP支持已彻底移除
        if (connection_mode != "ipc") {
            Response error_resp;
            error_resp.statusCode = 500;
            error_resp.body = "Only IPC mode is supported - HTTP has been removed";
            return error_resp;
        }
        
        // IPC模式 - url_or_path应该是路径
        std::string path = url_or_path;
        if (path.find("http://") == 0 || path.find("https://") == 0) {
            // 如果传入的是完整URL，提取路径部分
            size_t path_start = path.find('/', 8);  // 跳过 http://host:port
            if (path_start != std::string::npos) {
                path = path.substr(path_start);
            } else {
                path = "/";
            }
        }
        
        IPCClient::Response ipc_resp;
        if (method == "GET") {
            ipc_resp = ipc_client->get(path);
        } else if (method == "POST") {
            ipc_resp = ipc_client->post(path, data);
        } else {
            Response error_resp;
            error_resp.statusCode = 405;
            error_resp.body = "Method not allowed";
            return error_resp;
        }
        
        Response resp;
        resp.statusCode = ipc_resp.statusCode;
        resp.body = ipc_resp.body;
        return resp;
    }
    
    void addHeader(const std::string& key, const std::string& value) {
        // if (http_client) {  // HTTP支持已移除
        //     http_client->addHeader(key, value);
        // }
        if (ipc_client) {
            ipc_client->addHeader(key, value);
        }
    }
    
    void setTimeout(int timeout_seconds) {
        // if (http_client) {  // HTTP支持已移除
        //     http_client->setTimeout(timeout_seconds);
        // }
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

UnifiedClient::Response UnifiedClient::get(const std::string& url) {
    return pImpl->sendRequest("GET", url);
}

UnifiedClient::Response UnifiedClient::post(const std::string& url, const std::string& jsonData) {
    return pImpl->sendRequest("POST", url, jsonData);
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

std::string UnifiedClient::getConnectionMode() const {
    return pImpl->connection_mode;
}

} // namespace linch_connector