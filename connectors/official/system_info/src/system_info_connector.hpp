#pragma once

#include <linch_connector/base_connector.hpp>
#include <linch_connector/file_index_provider.hpp>
#include <linch_connector/null_monitor.hpp>
#include <memory>
#include <thread>
#include <atomic>
#include <chrono>
#include <functional>
#include <mutex>

namespace linch_connector {

/**
 * 系统信息收集类型
 */
enum class SystemInfoType {
    STATIC_INFO,      // 静态信息：CPU型号、内存总量等（启动时收集一次）
    DYNAMIC_INFO,     // 动态信息：CPU使用率、内存使用率等（定期更新）
    FILE_INDEX_FULL,  // 全局文件索引：全盘扫描（启动时或手动触发）
    FILE_INDEX_INCREMENTAL // 增量文件索引：定期更新变更文件
};

/**
 * 轻量级系统监控调度器
 * 
 * 特性：
 * - 分层收集策略（静态信息 vs 动态信息）
 * - 低频轻量操作，专注系统监控
 * - 简化的错误处理和重试机制
 */
class SystemInfoScheduler {
public:
    SystemInfoScheduler();
    ~SystemInfoScheduler();
    
    /**
     * 启动系统信息收集调度
     */
    void start();
    
    /**
     * 停止系统信息收集调度
     */
    void stop();
    
    /**
     * 立即执行一次系统信息收集
     */
    void triggerCollection(SystemInfoType type);
    
    /**
     * 设置动态信息收集间隔（分钟）
     */
    void setDynamicInfoInterval(int minutes);
    
    /**
     * 设置文件索引收集间隔（小时）
     */
    void setFileIndexInterval(int hours);

private:
    std::unique_ptr<std::thread> m_schedulerThread;
    std::atomic<bool> m_shouldStop{false};
    std::atomic<int> m_dynamicInfoIntervalMinutes{15}; // 默认15分钟
    std::atomic<int> m_fileIndexIntervalHours{24};     // 默认24小时
    std::chrono::steady_clock::time_point m_lastDynamicCollection;
    std::chrono::steady_clock::time_point m_lastFileIndexCollection;
    mutable std::mutex m_schedulerMutex;
    
    // 系统信息收集回调函数
    std::function<void(SystemInfoType)> m_collectionCallback;
    
    /**
     * 调度器主循环
     */
    void schedulerLoop();
    
    /**
     * 检查是否需要收集动态信息
     */
    bool shouldCollectDynamicInfo() const;
    
    /**
     * 检查是否需要执行文件索引
     */
    bool shouldPerformFileIndex() const;
    
public:
    /**
     * 设置信息收集回调函数
     */
    void setCollectionCallback(std::function<void(SystemInfoType)> callback);
};

/**
 * 系统信息连接器（重构简化版）
 * 
 * 核心职责：
 * 1. 系统硬件信息收集（CPU、内存、磁盘、网络）
 * 2. 系统状态监控（负载、进程数、运行时间）
 * 3. 已安装软件列表收集
 * 
 * 设计特点：
 * - 轻量化：专注系统监控，无文件索引功能
 * - 分层策略：静态信息一次收集，动态信息低频更新
 * - 低资源占用：最小化系统命令调用和内存使用
 */
class SystemInfoConnector : public BaseConnector {
public:
    SystemInfoConnector();
    ~SystemInfoConnector() override = default;
    
    /**
     * 手动触发系统信息收集
     */
    void triggerSystemInfoCollection(SystemInfoType type = SystemInfoType::DYNAMIC_INFO);

protected:
    // 实现BaseConnector纯虚函数
    std::unique_ptr<IConnectorMonitor> createMonitor() override;
    bool loadConnectorConfig() override;
    bool onInitialize() override;
    bool onStart() override;
    void onStop() override;

private:
    // 轻量级调度器
    std::unique_ptr<SystemInfoScheduler> m_scheduler;
    
    // 配置参数
    int m_dynamicInfoIntervalMinutes = 15;  // 动态信息收集间隔（默认15分钟）
    int m_fileIndexIntervalHours = 24;      // 文件索引收集间隔（默认24小时）
    bool m_collectSoftwareInfo = true;      // 是否收集软件信息
    bool m_enableFileIndex = true;          // 是否启用文件索引功能
    size_t m_fileIndexBatchSize = 1000;     // 文件索引批处理大小
    
    // 缓存静态信息，避免重复收集
    nlohmann::json m_cachedStaticInfo;
    bool m_staticInfoCollected = false;
    
    // 文件索引相关
    std::unique_ptr<IFileIndexProvider> m_fileIndexProvider;
    std::chrono::steady_clock::time_point m_lastFullIndexTime;
    bool m_fullIndexCompleted = false;
    
    /**
     * 系统信息收集处理器（回调函数）
     */
    void handleSystemInfoCollection(SystemInfoType type);
    
    /**
     * 收集静态系统信息（启动时执行一次）
     */
    nlohmann::json collectStaticSystemInfo();
    
    /**
     * 收集动态系统信息（定期更新）
     */
    nlohmann::json collectDynamicSystemInfo();
    
    /**
     * 发送系统信息数据到daemon
     */
    void sendSystemInfoData(const nlohmann::json& systemInfo, SystemInfoType type);
    
    // === 系统信息收集方法 ===
    
    /**
     * 收集CPU静态信息（型号、核心数、频率）
     */
    nlohmann::json collectCPUStaticInfo();
    
    /**
     * 收集CPU动态信息（使用率）
     */
    nlohmann::json collectCPUDynamicInfo();
    
    /**
     * 收集内存静态信息（总量）
     */
    nlohmann::json collectMemoryStaticInfo();
    
    /**
     * 收集内存动态信息（使用率、交换分区使用情况）
     */
    nlohmann::json collectMemoryDynamicInfo();
    
    /**
     * 收集磁盘静态信息（磁盘规格、挂载点）
     */
    nlohmann::json collectDiskStaticInfo();
    
    /**
     * 收集磁盘动态信息（空间使用情况）
     */
    nlohmann::json collectDiskDynamicInfo();
    
    /**
     * 收集网络接口信息（相对静态）
     */
    nlohmann::json collectNetworkInfo();
    
    /**
     * 收集磁盘I/O信息（动态）
     */
    nlohmann::json collectDiskIOInfo();
    
    /**
     * 收集TOP进程信息（动态）
     */
    nlohmann::json collectTopProcesses();
    
    /**
     * 收集系统负载信息（动态）
     */
    nlohmann::json collectSystemLoadInfo();
    
    /**
     * 收集已安装软件信息（相对静态，启动时收集）
     */
    nlohmann::json collectInstalledSoftware();
    
    /**
     * 获取基本系统信息（主机名、平台等）
     */
    nlohmann::json collectBasicSystemInfo();
    
    /**
     * 执行系统命令并获取输出
     */
    std::string executeCommand(const std::string& command);
    
    // === 文件索引相关方法 ===
    
    /**
     * 执行全局文件索引扫描
     */
    void performFullFileIndex();
    
    /**
     * 执行增量文件索引更新
     */
    void performIncrementalFileIndex();
    
    /**
     * 发送文件索引数据（分批发送）
     */
    void sendFileIndexData(const std::vector<FileRecord>& records, bool isIncremental = false);
    
    /**
     * 检查是否需要执行全索引
     */
    bool shouldPerformFullIndex() const;
    
    /**
     * 查询最近修改的文件（利用Spotlight时间查询）
     * @param hours 查询最近N小时内修改的文件
     * @return 最近修改的文件列表
     */
    std::vector<FileRecord> queryRecentlyModifiedFiles(size_t hours);
};

} // namespace linch_connector