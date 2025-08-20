#include "linch_connector/daemon_discovery.hpp"
#include <iostream>
#include <thread>
#include <cstdlib>

#ifdef _WIN32
#include <windows.h>
#else
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#endif

namespace linch_connector {

class DaemonDiscovery::Impl {
public:
    std::string getHomeDirectory() {
        const char* homeDir = nullptr;
#ifdef _WIN32
        homeDir = std::getenv("USERPROFILE");
#else
        homeDir = std::getenv("HOME");
#endif
        return homeDir ? std::string(homeDir) : "";
    }
};

DaemonDiscovery::DaemonDiscovery() : pImpl(std::make_unique<Impl>()) {}

DaemonDiscovery::~DaemonDiscovery() = default;

std::optional<DaemonInfo> DaemonDiscovery::discoverDaemon() {
    // 简化版本：直接使用环境变量和固定路径约定
    DaemonInfo daemonInfo;
    
    // 获取环境感知的socket路径
    auto homeDir = pImpl->getHomeDirectory();
    if (homeDir.empty()) {
        std::cerr << "[DaemonDiscovery] 无法获取用户主目录" << std::endl;
        return std::nullopt;
    }
    
    const char* envMode = std::getenv("LINCH_MIND_ENVIRONMENT");
    std::string environment = envMode ? std::string(envMode) : "development";
    
#ifdef _WIN32
    daemonInfo.socket_path = homeDir + "\\.linch-mind\\" + environment + "\\daemon.pipe";
    daemonInfo.socket_type = "pipe";
#else
    daemonInfo.socket_path = homeDir + "/.linch-mind/" + environment + "/data/daemon.socket";
    daemonInfo.socket_type = "unix";
#endif
    
    // 简单的连接测试
    daemonInfo.is_accessible = testIPCConnection(daemonInfo);
    
    if (daemonInfo.is_accessible) {
        std::cout << "[DaemonDiscovery] ✅ 连接成功: " << daemonInfo.socket_path << std::endl;
        return daemonInfo;
    } else {
        std::cout << "[DaemonDiscovery] ❌ 连接失败: " << daemonInfo.socket_path << std::endl;
        return std::nullopt;
    }
}

std::optional<DaemonInfo> DaemonDiscovery::waitForDaemon(
    std::chrono::seconds timeout,
    std::chrono::milliseconds checkInterval) {
    
    // 简化版本：最多重试3次，每次间隔1秒
    for (int i = 0; i < 3; i++) {
        auto daemonInfo = discoverDaemon();
        if (daemonInfo && daemonInfo->is_accessible) {
            return daemonInfo;
        }
        
        if (i < 2) { // 不在最后一次重试后sleep
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    }
    
    std::cerr << "[DaemonDiscovery] ❌ 3次重试后仍无法连接daemon" << std::endl;
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
    // 简化版本不需要缓存清理
}

} // namespace linch_connector