#pragma once

// #include "http_client.hpp"  // 已移除 - 使用纯IPC通信
#include "ipc_client.hpp"
#include "daemon_discovery.hpp"
#include <memory>

namespace linch_connector {

/**
 * 统一客户端适配器 - 纯IPC通信 (HTTP已移除)
 * 提供与HttpClient兼容的接口，内部使用IPC通信
 */
class UnifiedClient {
public:
    struct Response {
        int statusCode;
        std::string body;
        
        bool isSuccess() const { return statusCode >= 200 && statusCode < 300; }
    };

    UnifiedClient();
    ~UnifiedClient();

    /**
     * 连接到daemon (仅支持IPC)
     * @param daemonInfo daemon信息 (必须是IPC模式)
     * @return 是否连接成功
     */
    bool connect(const DaemonInfo& daemonInfo);

    /**
     * 发送GET请求
     * @param url 完整URL或路径 (HTTP模式需要完整URL，IPC模式只需路径)
     * @return 响应
     */
    Response get(const std::string& url);

    /**
     * 发送POST请求
     * @param url 完整URL或路径
     * @param jsonData JSON数据
     * @return 响应
     */
    Response post(const std::string& url, const std::string& jsonData);

    /**
     * 设置请求头
     * @param key 头部名称
     * @param value 头部值
     */
    void addHeader(const std::string& key, const std::string& value);

    /**
     * 设置超时时间
     * @param timeout_seconds 超时秒数
     */
    void setTimeout(int timeout_seconds);

    /**
     * 检查是否已连接
     * @return 连接状态
     */
    bool isConnected() const;

    /**
     * 获取当前使用的通信模式
     * @return "ipc" 或 "http"
     */
    std::string getConnectionMode() const;

private:
    class Impl;
    std::unique_ptr<Impl> pImpl;
};

} // namespace linch_connector