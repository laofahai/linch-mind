#include "linch_connector/daemon_discovery.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <thread>
#include <sstream>
#include <cstdlib>
#include <regex>

#ifdef _WIN32
#include <windows.h>
#include <tlhelp32.h>
#else
#include <sys/stat.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <signal.h>
#include <errno.h>
#endif

namespace linch_connector {

class DaemonDiscovery::Impl {
public:
    std::optional<DaemonInfo> cachedDaemonInfo;
    
    std::string getHomeDirectory() {
        const char* homeDir = nullptr;
#ifdef _WIN32
        homeDir = std::getenv("USERPROFILE");
#else
        homeDir = std::getenv("HOME");
#endif
        return homeDir ? std::string(homeDir) : "";
    }
    
    std::string getSocketFilePath() {
        auto homeDir = getHomeDirectory();
        if (homeDir.empty()) {
            return "";
        }
        
        // 🔧 环境感知: 读取LINCH_MIND_MODE环境变量，默认为development
        const char* envMode = std::getenv("LINCH_MIND_MODE");
        std::string environment = envMode ? std::string(envMode) : "development";
        
        return homeDir + "/.linch-mind/" + environment + "/daemon.socket.info";
    }
    
    std::string getPortFilePath() {
        auto homeDir = getHomeDirectory();
        if (homeDir.empty()) {
            return "";
        }
        return homeDir + "/.linch-mind/daemon.port";
    }
    
    std::optional<DaemonInfo> readSocketFile() {
        auto socketFilePath = getSocketFilePath();
        if (socketFilePath.empty()) {
            std::cerr << "[DaemonDiscovery] 无法获取用户主目录" << std::endl;
            return std::nullopt;
        }
        
        std::filesystem::path socketFile(socketFilePath);
        if (!std::filesystem::exists(socketFile)) {
            // socket文件不存在，这不是错误，可能使用HTTP模式
            return std::nullopt;
        }
        
        // 检查文件权限（Unix系统）
#ifndef _WIN32
        struct stat fileStat;
        if (stat(socketFilePath.c_str(), &fileStat) == 0) {
            // 检查是否只有owner有读写权限
            if ((fileStat.st_mode & 0x3F) != 0) {
                std::cerr << "[DaemonDiscovery] socket文件权限不安全，忽略" << std::endl;
                return std::nullopt;
            }
        }
#endif
        
        try {
            std::ifstream file(socketFilePath);
            if (!file.is_open()) {
                std::cerr << "[DaemonDiscovery] 无法打开socket文件: " << socketFilePath << std::endl;
                return std::nullopt;
            }
            
            std::string content;
            std::string line;
            while (std::getline(file, line)) {
                content += line;
            }
            file.close();
            
            // 解析JSON格式: {"type": "unix_socket", "path": "/path/to/socket", "pid": 12345}
            return parseSocketFileContent(content);
            
        } catch (const std::exception& e) {
            std::cerr << "[DaemonDiscovery] 解析socket文件失败: " << e.what() << std::endl;
            return std::nullopt;
        }
    }
    
    std::optional<DaemonInfo> readPortFile() {
        auto portFilePath = getPortFilePath();
        if (portFilePath.empty()) {
            std::cerr << "[DaemonDiscovery] 无法获取用户主目录" << std::endl;
            return std::nullopt;
        }
        
        std::filesystem::path portFile(portFilePath);
        if (!std::filesystem::exists(portFile)) {
            std::cerr << "[DaemonDiscovery] 端口文件不存在: " << portFilePath << std::endl;
            return std::nullopt;
        }
        
        // 检查文件权限（Unix系统）
#ifndef _WIN32
        struct stat fileStat;
        if (stat(portFilePath.c_str(), &fileStat) == 0) {
            // 检查是否只有owner有读写权限
            if ((fileStat.st_mode & 0x3F) != 0) {
                std::cerr << "[DaemonDiscovery] 端口文件权限不安全，忽略" << std::endl;
                return std::nullopt;
            }
        }
#endif
        
        try {
            std::ifstream file(portFilePath);
            if (!file.is_open()) {
                std::cerr << "[DaemonDiscovery] 无法打开端口文件: " << portFilePath << std::endl;
                return std::nullopt;
            }
            
            std::string content;
            std::getline(file, content);
            file.close();
            
            // 解析格式: port:pid
            auto colonPos = content.find(':');
            if (colonPos == std::string::npos) {
                std::cerr << "[DaemonDiscovery] 端口文件格式无效，期望 \"port:pid\"" << std::endl;
                return std::nullopt;
            }
            
            std::string portStr = content.substr(0, colonPos);
            std::string pidStr = content.substr(colonPos + 1);
            
            int port = std::stoi(portStr);
            int pid = std::stoi(pidStr);
            
            DaemonInfo daemonInfo;
            daemonInfo.pid = pid;
            // HTTP模式已经不再支持，返回nullopt
            std::cerr << "[DaemonDiscovery] HTTP mode is no longer supported" << std::endl;
            return std::nullopt;
            
            return daemonInfo;
            
        } catch (const std::exception& e) {
            std::cerr << "[DaemonDiscovery] 解析端口文件失败: " << e.what() << std::endl;
            return std::nullopt;
        }
    }
    
    std::optional<DaemonInfo> parseSocketFileContent(const std::string& content) {
        // 简单的JSON解析实现（生产环境中应该使用更健壮的JSON库）
        try {
            DaemonInfo daemonInfo;
            
            // 简化的JSON字段提取
            std::smatch match;
            std::string socket_type;
            
            // 提取type字段  
            std::regex type_regex("\"type\"\\s*:\\s*\"([^\"]+)\"");
            if (std::regex_search(content, match, type_regex)) {
                socket_type = match[1];
            }
            
            // 提取path字段
            std::regex path_regex("\"path\"\\s*:\\s*\"([^\"]+)\"");
            if (std::regex_search(content, match, path_regex)) {
                if (socket_type == "unix_socket") {
                    daemonInfo.socket_path = match[1];
                } else if (socket_type == "named_pipe") {
                    daemonInfo.socket_path = match[1];
                    daemonInfo.socket_type = "pipe";
                }
            }
            
            // 提取pid字段
            std::regex pid_regex("\"pid\"\\s*:\\s*(\\d+)");
            if (std::regex_search(content, match, pid_regex)) {
                daemonInfo.pid = std::stoi(match[1]);
            }
            
            if (socket_type == "unix_socket") {
                daemonInfo.socket_type = "unix";
            }
            
            return daemonInfo;
            
        } catch (const std::exception& e) {
            std::cerr << "[DaemonDiscovery] JSON解析失败: " << e.what() << std::endl;
            return std::nullopt;
        }
    }
    
    bool verifyDaemonProcess(int pid) {
#ifdef _WIN32
        // Windows系统的进程验证
        HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
        if (snapshot == INVALID_HANDLE_VALUE) {
            return false;
        }
        
        PROCESSENTRY32 processEntry;
        processEntry.dwSize = sizeof(PROCESSENTRY32);
        
        bool found = false;
        if (Process32First(snapshot, &processEntry)) {
            do {
                if (processEntry.th32ProcessID == static_cast<DWORD>(pid)) {
                    found = true;
                    break;
                }
            } while (Process32Next(snapshot, &processEntry));
        }
        
        CloseHandle(snapshot);
        return found;
#else
        // Unix系统的进程验证
        // macOS使用kill(pid, 0)来检测进程
        if (kill(pid, 0) == 0) {
            return true;  // 进程存在
        } else {
            return (errno == EPERM);  // 进程存在但没有权限也算存在
        }
#endif
    }
    
    bool testConnection(const std::string& host, int port) {
        try {
#ifdef _WIN32
            WSADATA wsaData;
            if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
                return false;
            }
            
            SOCKET sock = socket(AF_INET, SOCK_STREAM, 0);
            if (sock == INVALID_SOCKET) {
                WSACleanup();
                return false;
            }
            
            // 设置超时
            DWORD timeout = 3000; // 3秒
            setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, (char*)&timeout, sizeof(timeout));
            setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, (char*)&timeout, sizeof(timeout));
            
            sockaddr_in serverAddr{};
            serverAddr.sin_family = AF_INET;
            serverAddr.sin_port = htons(port);
            inet_pton(AF_INET, host.c_str(), &serverAddr.sin_addr);
            
            bool connected = (connect(sock, (sockaddr*)&serverAddr, sizeof(serverAddr)) == 0);
            
            closesocket(sock);
            WSACleanup();
            return connected;
#else
            int sock = socket(AF_INET, SOCK_STREAM, 0);
            if (sock < 0) {
                return false;
            }
            
            // 设置超时
            struct timeval timeout;
            timeout.tv_sec = 3;
            timeout.tv_usec = 0;
            setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
            setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));
            
            struct sockaddr_in serverAddr{};
            serverAddr.sin_family = AF_INET;
            serverAddr.sin_port = htons(port);
            inet_pton(AF_INET, host.c_str(), &serverAddr.sin_addr);
            
            bool connected = (connect(sock, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) == 0);
            
            close(sock);
            return connected;
#endif
        } catch (const std::exception& e) {
            std::cerr << "[DaemonDiscovery] 连接测试失败: " << e.what() << std::endl;
            return false;
        }
    }
};

DaemonDiscovery::DaemonDiscovery() : pImpl(std::make_unique<Impl>()) {}

DaemonDiscovery::~DaemonDiscovery() = default;

std::optional<DaemonInfo> DaemonDiscovery::discoverDaemon() {
    // 如果有缓存且有效，直接返回
    if (pImpl->cachedDaemonInfo && testIPCConnection(*pImpl->cachedDaemonInfo)) {
        return pImpl->cachedDaemonInfo;
    }
    
    // 清除无效缓存
    pImpl->cachedDaemonInfo = std::nullopt;
    
    // 纯IPC模式，只读取socket文件
    auto daemonInfoOpt = pImpl->readSocketFile();
    if (!daemonInfoOpt) {
        return std::nullopt;
    }
    
    auto& daemonInfo = *daemonInfoOpt;

    // 验证进程是否运行
    if (daemonInfo.pid > 0 && !pImpl->verifyDaemonProcess(daemonInfo.pid)) {
        std::cerr << "[DaemonDiscovery] Daemon进程 " << daemonInfo.pid << " 未运行" << std::endl;
        // 清理过时的socket文件
        std::remove(pImpl->getSocketFilePath().c_str());
        return std::nullopt;
    }
    
    // 测试连接性
    daemonInfo.is_accessible = testIPCConnection(daemonInfo);
    
    if (daemonInfo.is_accessible) {
        pImpl->cachedDaemonInfo = daemonInfo;
        std::cout << "[DaemonDiscovery] 发现可访问的daemon (IPC): " << daemonInfo.socket_path << std::endl;
    } else {
        std::cout << "[DaemonDiscovery] Daemon不可访问 (IPC): " << daemonInfo.socket_path << std::endl;
    }
    
    return daemonInfo;
}

std::optional<DaemonInfo> DaemonDiscovery::waitForDaemon(
    std::chrono::seconds timeout,
    std::chrono::milliseconds checkInterval) {
    
    auto startTime = std::chrono::steady_clock::now();
    
    while (std::chrono::steady_clock::now() - startTime < timeout) {
        auto daemonInfo = discoverDaemon();
        if (daemonInfo && daemonInfo->is_accessible) {
            return daemonInfo;
        }
        
        std::this_thread::sleep_for(checkInterval);
    }
    
    std::cerr << "[DaemonDiscovery] Daemon发现超时" << std::endl;
    return std::nullopt;
}

bool DaemonDiscovery::testDaemonConnection(const DaemonInfo& daemonInfo) {
    return testIPCConnection(daemonInfo);
}

bool DaemonDiscovery::testIPCConnection(const DaemonInfo& daemonInfo) {
    try {
        // 简单的IPC连接测试
#ifdef _WIN32
        if (!daemonInfo.pipe_name.empty()) {
            std::string full_pipe_name = "\\\\.\\pipe\\" + daemonInfo.pipe_name;
            HANDLE pipe = CreateFile(
                full_pipe_name.c_str(),
                GENERIC_READ | GENERIC_WRITE,
                0, NULL, OPEN_EXISTING, 0, NULL
            );
            if (pipe != INVALID_HANDLE_VALUE) {
                CloseHandle(pipe);
                return true;
            }
        }
#else
        if (!daemonInfo.socket_path.empty()) {
            int sock = socket(AF_UNIX, SOCK_STREAM, 0);
            if (sock >= 0) {
                struct sockaddr_un addr;
                std::memset(&addr, 0, sizeof(addr));
                addr.sun_family = AF_UNIX;
                std::strncpy(addr.sun_path, daemonInfo.socket_path.c_str(), sizeof(addr.sun_path) - 1);
                
                bool connected = (connect(sock, (struct sockaddr*)&addr, sizeof(addr)) == 0);
                close(sock);
                return connected;
            }
        }
#endif
        return false;
    } catch (const std::exception& e) {
        std::cerr << "[DaemonDiscovery] IPC连接测试失败: " << e.what() << std::endl;
        return false;
    }
}

void DaemonDiscovery::clearCache() {
    pImpl->cachedDaemonInfo = std::nullopt;
}

} // namespace linch_connector