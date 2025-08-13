#pragma once

#include "native_monitor.hpp"
#include <memory>
#include <string>

// 前向声明
#ifdef __APPLE__
class MacOSFSEventsMonitor;
#endif

#ifdef __linux__
class LinuxInotifyMonitor;
#endif

#ifdef _WIN32
class WindowsRDCWMonitor;
#endif

// 监控器类型
enum class MonitorType {
    NATIVE,      // 使用平台原生API
    POLLING,     // 轮询模式（后备选项）
    AUTO         // 自动选择最佳方案
};

// 监控器工厂
class MonitorFactory {
public:
    // 创建监控器实例
    static std::unique_ptr<INativeMonitor> createMonitor(
        MonitorType type = MonitorType::AUTO);
    
    // 获取推荐的监控器类型
    static MonitorType getRecommendedType();
    
    // 检查监控器类型是否可用
    static bool isTypeSupported(MonitorType type);
    
    // 获取当前平台信息
    static std::string getPlatformInfo();
    
private:
    // 创建平台特定监控器
#ifdef __APPLE__
    static std::unique_ptr<INativeMonitor> createMacOSMonitor();
#endif

#ifdef __linux__
    static std::unique_ptr<INativeMonitor> createLinuxMonitor();
#endif

#ifdef _WIN32
    static std::unique_ptr<INativeMonitor> createWindowsMonitor();
#endif
    
    // 创建轮询监控器（后备）
    static std::unique_ptr<INativeMonitor> createPollingMonitor();
};

// 高级文件系统监控器 - 主要接口类
class FileSystemMonitor {
public:
    FileSystemMonitor(MonitorType type = MonitorType::AUTO);
    ~FileSystemMonitor();
    
    // 禁用拷贝
    FileSystemMonitor(const FileSystemMonitor&) = delete;
    FileSystemMonitor& operator=(const FileSystemMonitor&) = delete;
    
    // 移动构造
    FileSystemMonitor(FileSystemMonitor&& other) noexcept;
    FileSystemMonitor& operator=(FileSystemMonitor&& other) noexcept;
    
    // 监控控制
    bool start(EventCallback callback);
    void stop();
    bool isRunning() const;
    
    // 路径管理
    bool addPath(const MonitorConfig& config);
    bool removePath(const std::string& path);
    std::vector<std::string> getMonitoredPaths() const;
    
    // 批处理事件设置
    void setBatchCallback(BatchEventCallback callback, 
                         std::chrono::milliseconds interval = std::chrono::milliseconds(500));
    
    // 统计信息
    struct Statistics {
        size_t eventsProcessed = 0;
        size_t eventsFiltered = 0;
        size_t pathsMonitored = 0;
        MonitorType monitorType = MonitorType::AUTO;
        std::string platformInfo;
        std::chrono::system_clock::time_point startTime;
        bool isRunning = false;
    };
    
    Statistics getStatistics() const;
    
    // 配置验证
    static bool validateConfig(const MonitorConfig& config);
    
    // 创建默认配置
    static MonitorConfig createDefaultConfig(const std::string& path);
    
private:
    std::unique_ptr<INativeMonitor> m_monitor;
    Statistics m_stats;
    mutable std::mutex m_statsMutex;
    
    void updateStats();
};