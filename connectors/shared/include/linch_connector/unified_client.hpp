#pragma once

#include "ipc_client.hpp"
#include "daemon_discovery.hpp"
#include <memory>

namespace linch_connector {

/**
 * 统一客户端 - 纯IPC通信
 */
class UnifiedClient {
public:
    // Response is now defined in ipc_client.hpp, so we can remove this.
    // struct Response {
    //     int statusCode;
    //     std::string body;
    //     
    //     bool isSuccess() const { return statusCode >= 200 && statusCode < 300; }
    // };

    UnifiedClient();
    ~UnifiedClient();

    /**
     * 连接到daemon (仅支持IPC)
     * @param daemonInfo daemon信息
     * @return 是否连接成功
     */
    bool connect(const DaemonInfo& daemonInfo);

    /**
     * 发送查询消息
     * @param path 请求路径 (e.g. /health)
     * @return 响应
     */
    IPCClient::IPCResponse get(const std::string& path);

    /**
     * 发送数据消息
     * @param path 请求路径
     * @param jsonData JSON数据
     * @return 响应
     */
    IPCClient::IPCResponse post(const std::string& path, const std::string& jsonData);

    /**
     * 设置请求头 (IPC模式下通常忽略)
     */
    void addHeader(const std::string& key, const std::string& value);

    /**
     * 设置超时时间
     */
    void setTimeout(int timeout_seconds);

    /**
     * 检查是否已连接
     */
    bool isConnected() const;

private:
    class Impl;
    std::unique_ptr<Impl> pImpl;
};

} // namespace linch_connector