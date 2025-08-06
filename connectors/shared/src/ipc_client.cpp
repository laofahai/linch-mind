#include "linch_connector/ipc_client.hpp"
#include <iostream>
#include <sstream>
#include <cstring>
#include <map>

#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <errno.h>
#include <sys/time.h>
#endif

namespace linch_connector {

class IPCClient::Impl {
public:
    bool connected;
    int timeout_seconds;
    std::map<std::string, std::string> headers;
    
#ifdef _WIN32
    HANDLE pipe_handle;
#else
    int socket_fd;
#endif

    Impl() : connected(false), timeout_seconds(30) {
#ifdef _WIN32
        pipe_handle = INVALID_HANDLE_VALUE;
#else
        socket_fd = -1;
#endif
    }

    ~Impl() {
        disconnect();
    }
    
    bool connectUnixSocket(const std::string& socket_path) {
#ifdef _WIN32
        std::cerr << "[IPCClient] Unix Socket不支持Windows平台" << std::endl;
        return false;
#else
        // 创建Unix domain socket
        socket_fd = socket(AF_UNIX, SOCK_STREAM, 0);
        if (socket_fd == -1) {
            std::cerr << "[IPCClient] 创建socket失败: " << strerror(errno) << std::endl;
            return false;
        }
        
        // 设置超时
        struct timeval timeout;
        timeout.tv_sec = timeout_seconds;
        timeout.tv_usec = 0;
        setsockopt(socket_fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
        setsockopt(socket_fd, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));
        
        // 连接到socket
        struct sockaddr_un addr;
        std::memset(&addr, 0, sizeof(addr));
        addr.sun_family = AF_UNIX;
        std::strncpy(addr.sun_path, socket_path.c_str(), sizeof(addr.sun_path) - 1);
        
        if (connect(socket_fd, (struct sockaddr*)&addr, sizeof(addr)) == -1) {
            std::cerr << "[IPCClient] 连接socket失败: " << strerror(errno) << std::endl;
            close(socket_fd);
            socket_fd = -1;
            return false;
        }
        
        connected = true;
        std::cout << "[IPCClient] 已连接到Unix socket: " << socket_path << std::endl;
        return true;
#endif
    }
    
    bool connectNamedPipe(const std::string& pipe_name) {
#ifdef _WIN32
        std::string full_pipe_name = "\\\\.\\pipe\\" + pipe_name;
        
        pipe_handle = CreateFile(
            full_pipe_name.c_str(),
            GENERIC_READ | GENERIC_WRITE,
            0,
            NULL,
            OPEN_EXISTING,
            0,
            NULL
        );
        
        if (pipe_handle == INVALID_HANDLE_VALUE) {
            DWORD error = GetLastError();
            std::cerr << "[IPCClient] 连接Named Pipe失败, 错误代码: " << error << std::endl;
            return false;
        }
        
        connected = true;
        std::cout << "[IPCClient] 已连接到Named Pipe: " << pipe_name << std::endl;
        return true;
#else
        (void)pipe_name;  // 避免未使用参数警告
        std::cerr << "[IPCClient] Named Pipe不支持非Windows平台" << std::endl;
        return false;
#endif
    }
    
    Response sendRequest(const std::string& method, const std::string& path, 
                        const std::string& data = "") {
        if (!connected) {
            Response error_resp;
            error_resp.statusCode = 500;
            error_resp.body = "Not connected to IPC server";
            return error_resp;
        }
        
        // 构建IPC消息 (简化的JSON格式)
        std::ostringstream json_msg;
        json_msg << "{";
        json_msg << "\"method\":\"" << method << "\",";
        json_msg << "\"path\":\"" << path << "\",";
        json_msg << "\"data\":" << (data.empty() ? "{}" : data) << ",";
        json_msg << "\"headers\":{";
        bool first = true;
        for (const auto& [key, value] : headers) {
            if (!first) json_msg << ",";
            json_msg << "\"" << key << "\":\"" << value << "\"";
            first = false;
        }
        json_msg << "},";
        json_msg << "\"query_params\":{}";
        json_msg << "}";
        
        std::string message = json_msg.str();
        
#ifdef _WIN32
        return sendMessageNamedPipe(message);
#else
        return sendMessageUnixSocket(message);
#endif
    }
    
private:
#ifdef _WIN32
    Response sendMessageNamedPipe(const std::string& message) {
        Response response;
        
        // 发送消息长度前缀
        uint32_t msg_length = static_cast<uint32_t>(message.length());
        DWORD bytes_written;
        
        if (!WriteFile(pipe_handle, &msg_length, sizeof(msg_length), &bytes_written, NULL) ||
            bytes_written != sizeof(msg_length)) {
            response.statusCode = 500;
            response.body = "Failed to send message length";
            return response;
        }
        
        // 发送消息内容
        if (!WriteFile(pipe_handle, message.c_str(), msg_length, &bytes_written, NULL) ||
            bytes_written != msg_length) {
            response.statusCode = 500;
            response.body = "Failed to send message content";
            return response;
        }
        
        // 读取响应长度
        uint32_t resp_length;
        DWORD bytes_read;
        if (!ReadFile(pipe_handle, &resp_length, sizeof(resp_length), &bytes_read, NULL) ||
            bytes_read != sizeof(resp_length)) {
            response.statusCode = 500;
            response.body = "Failed to read response length";
            return response;
        }
        
        // 读取响应内容
        std::string resp_data(resp_length, '\0');
        if (!ReadFile(pipe_handle, resp_data.data(), resp_length, &bytes_read, NULL) ||
            bytes_read != resp_length) {
            response.statusCode = 500;
            response.body = "Failed to read response content";
            return response;
        }
        
        // 简单解析响应
        return parseResponse(resp_data);
    }
#endif
    
    Response sendMessageUnixSocket(const std::string& message) {
        Response response;
        
        // 发送消息长度前缀 (4字节，大端序)
        uint32_t msg_length = htonl(static_cast<uint32_t>(message.length()));
        if (send(socket_fd, &msg_length, sizeof(msg_length), 0) != sizeof(msg_length)) {
            response.statusCode = 500;
            response.body = "Failed to send message length";
            return response;
        }
        
        // 发送消息内容
        if (send(socket_fd, message.c_str(), message.length(), 0) != static_cast<ssize_t>(message.length())) {
            response.statusCode = 500;
            response.body = "Failed to send message content";
            return response;
        }
        
        // 读取响应长度
        uint32_t resp_length_net;
        if (recv(socket_fd, &resp_length_net, sizeof(resp_length_net), 0) != sizeof(resp_length_net)) {
            response.statusCode = 500;
            response.body = "Failed to read response length";
            return response;
        }
        
        uint32_t resp_length = ntohl(resp_length_net);
        
        // 读取响应内容
        std::string resp_data(resp_length, '\0');
        ssize_t total_read = 0;
        while (total_read < static_cast<ssize_t>(resp_length)) {
            ssize_t bytes_read = recv(socket_fd, resp_data.data() + total_read, 
                                    resp_length - total_read, 0);
            if (bytes_read <= 0) {
                response.statusCode = 500;
                response.body = "Failed to read response content";
                return response;
            }
            total_read += bytes_read;
        }
        
        // 解析响应
        return parseResponse(resp_data);
    }
    
    Response parseResponse(const std::string& json_str) {
        Response response;
        response.statusCode = 500; // 默认错误状态
        
        std::cout << "[IPCClient] 解析响应: " << json_str << std::endl;
        
        // 简单的JSON解析 - 提取status_code
        size_t status_pos = json_str.find("\"status_code\":");
        if (status_pos != std::string::npos) {
            size_t start = json_str.find(":", status_pos) + 1;
            size_t end = json_str.find_first_of(",}", start);
            
            if (end != std::string::npos) {
                std::string status_str = json_str.substr(start, end - start);
                // 移除空白字符和引号
                status_str.erase(0, status_str.find_first_not_of(" \t\""));
                status_str.erase(status_str.find_last_not_of(" \t\"") + 1);
                
                try {
                    response.statusCode = std::stoi(status_str);
                } catch (...) {
                    std::cerr << "[IPCClient] 解析status_code失败: " << status_str << std::endl;
                    response.statusCode = 500;
                }
            }
        }
        
        // 提取data字段内容
        size_t data_pos = json_str.find("\"data\":");
        if (data_pos != std::string::npos) {
            size_t start = data_pos + 7; // 跳过"data":
            
            // 跳过空白字符
            while (start < json_str.length() && 
                   (json_str[start] == ' ' || json_str[start] == '\t')) {
                start++;
            }
            
            if (start < json_str.length()) {
                if (json_str[start] == '{') {
                    // data是对象，找匹配的}
                    int bracket_count = 1;
                    size_t end = start + 1;
                    while (end < json_str.length() && bracket_count > 0) {
                        if (json_str[end] == '{') bracket_count++;
                        else if (json_str[end] == '}') bracket_count--;
                        end++;
                    }
                    if (bracket_count == 0) {
                        response.body = json_str.substr(start, end - start);
                    }
                } else if (json_str[start] == '[') {
                    // data是数组，找匹配的]
                    int bracket_count = 1;
                    size_t end = start + 1;
                    while (end < json_str.length() && bracket_count > 0) {
                        if (json_str[end] == '[') bracket_count++;
                        else if (json_str[end] == ']') bracket_count--;
                        end++;
                    }
                    if (bracket_count == 0) {
                        response.body = json_str.substr(start, end - start);
                    }
                } else if (json_str[start] == '"') {
                    // data是字符串，找结束引号
                    size_t end = start + 1;
                    while (end < json_str.length()) {
                        if (json_str[end] == '"' && json_str[end-1] != '\\') {
                            break;
                        }
                        end++;
                    }
                    if (end < json_str.length()) {
                        response.body = json_str.substr(start, end - start + 1);
                    }
                } else {
                    // data是其他基础类型（数字、布尔等）
                    size_t end = json_str.find_first_of(",}", start);
                    if (end != std::string::npos) {
                        response.body = json_str.substr(start, end - start);
                        // 移除尾部空白字符
                        response.body.erase(response.body.find_last_not_of(" \t") + 1);
                    }
                }
            }
        }
        
        // 如果data字段为空，使用整个响应作为body
        if (response.body.empty()) {
            response.body = json_str;
            std::cerr << "[IPCClient] data字段为空，使用完整响应" << std::endl;
        }
        
        std::cout << "[IPCClient] 解析结果 - status_code: " << response.statusCode 
                  << ", body: " << response.body.substr(0, 100) << "..." << std::endl;
        
        return response;
    }
    
public:
    void disconnect() {
        connected = false;
        
#ifdef _WIN32
        if (pipe_handle != INVALID_HANDLE_VALUE) {
            CloseHandle(pipe_handle);
            pipe_handle = INVALID_HANDLE_VALUE;
        }
#else
        if (socket_fd != -1) {
            close(socket_fd);
            socket_fd = -1;
        }
#endif
    }
};

IPCClient::IPCClient() : pImpl(std::make_unique<Impl>()) {}

IPCClient::~IPCClient() = default;

bool IPCClient::connectUnixSocket(const std::string& socket_path) {
    return pImpl->connectUnixSocket(socket_path);
}

bool IPCClient::connectNamedPipe(const std::string& pipe_name) {
    return pImpl->connectNamedPipe(pipe_name);
}

IPCClient::Response IPCClient::get(const std::string& path) {
    return pImpl->sendRequest("GET", path);
}

IPCClient::Response IPCClient::post(const std::string& path, const std::string& jsonData) {
    return pImpl->sendRequest("POST", path, jsonData);
}

void IPCClient::addHeader(const std::string& key, const std::string& value) {
    pImpl->headers[key] = value;
}

void IPCClient::setTimeout(int timeout_seconds) {
    pImpl->timeout_seconds = timeout_seconds;
}

void IPCClient::disconnect() {
    pImpl->disconnect();
}

bool IPCClient::isConnected() const {
    return pImpl->connected;
}

} // namespace linch_connector