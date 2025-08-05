#include "linch_connector/daemon_discovery.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <thread>
#include <sstream>
#include <cstdlib>

#ifdef _WIN32
#include <windows.h>
#include <tlhelp32.h>
#else
#include <sys/stat.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
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
    
    std::string getPortFilePath() {
        auto homeDir = getHomeDirectory();
        if (homeDir.empty()) {
            return "";
        }
        return homeDir + "/.linch-mind/daemon.port";
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
            daemonInfo.host = "127.0.0.1";
            daemonInfo.port = port;
            daemonInfo.pid = pid;
            
            return daemonInfo;
            
        } catch (const std::exception& e) {
            std::cerr << "[DaemonDiscovery] 解析端口文件失败: " << e.what() << std::endl;
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
        std::string procPath = "/proc/" + std::to_string(pid);
        return std::filesystem::exists(procPath);
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
    if (pImpl->cachedDaemonInfo && testDaemonConnection(*pImpl->cachedDaemonInfo)) {
        return pImpl->cachedDaemonInfo;
    }
    
    // 清除无效缓存
    pImpl->cachedDaemonInfo = std::nullopt;
    
    // 读取端口文件
    auto daemonInfo = pImpl->readPortFile();
    if (!daemonInfo) {
        return std::nullopt;
    }
    
    // 验证进程是否运行
    if (daemonInfo->pid > 0 && !pImpl->verifyDaemonProcess(daemonInfo->pid)) {
        std::cerr << "[DaemonDiscovery] Daemon进程 " << daemonInfo->pid << " 未运行" << std::endl;
        return std::nullopt;
    }
    
    // 测试连接性
    daemonInfo->isAccessible = testDaemonConnection(*daemonInfo);
    
    if (daemonInfo->isAccessible) {
        pImpl->cachedDaemonInfo = *daemonInfo;
        std::cout << "[DaemonDiscovery] 发现可访问的daemon: " << daemonInfo->host << ":" << daemonInfo->port << std::endl;
    } else {
        std::cout << "[DaemonDiscovery] Daemon不可访问: " << daemonInfo->host << ":" << daemonInfo->port << std::endl;
    }
    
    return daemonInfo;
}

std::optional<DaemonInfo> DaemonDiscovery::waitForDaemon(
    std::chrono::seconds timeout,
    std::chrono::milliseconds checkInterval) {
    
    auto startTime = std::chrono::steady_clock::now();
    
    while (std::chrono::steady_clock::now() - startTime < timeout) {
        auto daemonInfo = discoverDaemon();
        if (daemonInfo && daemonInfo->isAccessible) {
            return daemonInfo;
        }
        
        std::this_thread::sleep_for(checkInterval);
    }
    
    std::cerr << "[DaemonDiscovery] Daemon发现超时" << std::endl;
    return std::nullopt;
}

bool DaemonDiscovery::testDaemonConnection(const DaemonInfo& daemonInfo) {
    return pImpl->testConnection(daemonInfo.host, daemonInfo.port);
}

void DaemonDiscovery::clearCache() {
    pImpl->cachedDaemonInfo = std::nullopt;
}

} // namespace linch_connector