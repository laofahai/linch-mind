#pragma once

#include <string>
#include <optional>
#include <chrono>

namespace linch_connector {

/**
 * Daemon信息数据结构
 */
struct DaemonInfo {
    int pid;
    std::string socket_path;
    std::string socket_type; // "unix" or "windows"
    bool is_accessible = false;
};

/**
 * Daemon发现服务 - 纯IPC架构的daemon发现机制
 * 读取~/.linch-mind/{env}/daemon.socket.info文件（纯IPC模式）
 */
class DaemonDiscovery {
public:
    DaemonDiscovery();
    ~DaemonDiscovery();

    /**
     * 发现daemon实例
     * @return daemon信息，如果未发现则返回nullopt
     */
    std::optional<DaemonInfo> discoverDaemon();

    /**
     * 等待daemon启动
     * @param timeout 最大等待时间
     * @param checkInterval 检查间隔
     * @return daemon信息，如果超时则返回nullopt
     */
    std::optional<DaemonInfo> waitForDaemon(
        std::chrono::seconds timeout = std::chrono::seconds(30),
        std::chrono::milliseconds checkInterval = std::chrono::milliseconds(1000)
    );

    /**
     * 测试daemon连接
     * @param daemonInfo daemon信息
     * @return 是否可连接
     */
    bool testDaemonConnection(const DaemonInfo& daemonInfo);
    
    /**
     * 测试IPC连接
     * @param daemonInfo daemon信息
     * @return 是否可连接
     */
    bool testIPCConnection(const DaemonInfo& daemonInfo);

    /**
     * 清除缓存的daemon信息
     */
    void clearCache();

private:
    class Impl;
    std::unique_ptr<Impl> pImpl;
};

} // namespace linch_connector