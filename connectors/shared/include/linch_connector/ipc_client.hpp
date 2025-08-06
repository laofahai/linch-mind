#pragma once

#include <string>
#include <memory>

namespace linch_connector {

/**
 * IPC客户端 - Unix Domain Socket和Named Pipe通信
 * 提供与daemon的安全本地进程间通信
 */
class IPCClient {
public:
    struct Response {
        int statusCode = 0;
        std::string body;
        
        bool isSuccess() const { return statusCode >= 200 && statusCode < 300; }
    };

    IPCClient();
    ~IPCClient();

    /**
     * 连接到Unix Domain Socket
     * @param socket_path Socket文件路径
     * @return 是否连接成功
     */
    bool connectUnixSocket(const std::string& socket_path);
    
    /**
     * 连接到Windows Named Pipe
     * @param pipe_name Named Pipe名称
     * @return 是否连接成功
     */
    bool connectNamedPipe(const std::string& pipe_name);

    /**
     * 发送GET请求
     * @param path API路径
     * @return 响应
     */
    Response get(const std::string& path);

    /**
     * 发送POST请求
     * @param path API路径
     * @param jsonData JSON数据
     * @return 响应
     */
    Response post(const std::string& path, const std::string& jsonData);

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
     * 断开连接
     */
    void disconnect();

    /**
     * 检查是否已连接
     * @return 连接状态
     */
    bool isConnected() const;

private:
    class Impl;
    std::unique_ptr<Impl> pImpl;
};

} // namespace linch_connector