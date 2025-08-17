#pragma once

#include "connector_event.hpp"
#include "unified_client.hpp"
#include "config_manager.hpp"
#include "connector_status.hpp"
#include "daemon_discovery.hpp"
#include "chunk_manager.hpp"
#include <memory>
#include <vector>
#include <functional>
#include <thread>
#include <atomic>
#include <chrono>
#include <mutex>
#include <queue>

namespace linch_connector {

/**
 * 连接器基类 - 统一所有连接器的核心功能
 * 消除代码重复，提供标准化的连接器实现框架
 */
class BaseConnector {
public:
    using EventCallback = std::function<void(ConnectorEvent&&)>;
    using BatchEventCallback = std::function<void(std::vector<ConnectorEvent>&&)>;

    BaseConnector(const std::string& connectorId, const std::string& displayName);
    virtual ~BaseConnector();

    // 禁用拷贝和移动
    BaseConnector(const BaseConnector&) = delete;
    BaseConnector& operator=(const BaseConnector&) = delete;

    /**
     * 初始化连接器
     * @param daemonTimeout 等待daemon连接的超时时间(秒)
     * @return 是否初始化成功
     */
    bool initialize(int daemonTimeout = 30);

    /**
     * 启动连接器
     * @return 是否启动成功
     */
    bool start();

    /**
     * 停止连接器
     */
    void stop();

    /**
     * 检查连接器是否正在运行
     */
    bool isRunning() const;

    /**
     * 获取连接器统计信息
     */
    virtual IConnectorMonitor::Statistics getStatistics() const;

    /**
     * 设置批处理配置
     * @param interval 批处理间隔
     * @param maxBatchSize 最大批处理大小
     */
    void setBatchConfig(std::chrono::milliseconds interval = std::chrono::milliseconds(300),
                       size_t maxBatchSize = 50);

protected:
    /**
     * 子类必须实现：创建具体的监控器
     */
    virtual std::unique_ptr<IConnectorMonitor> createMonitor() = 0;

    /**
     * 子类必须实现：加载连接器特定配置
     */
    virtual bool loadConnectorConfig() = 0;

    /**
     * 子类可选实现：自定义初始化逻辑
     */
    virtual bool onInitialize() { return true; }

    /**
     * 子类可选实现：自定义启动逻辑
     */
    virtual bool onStart() { return true; }

    /**
     * 子类可选实现：自定义停止逻辑
     */
    virtual void onStop() {}

    /**
     * 发送单个事件到daemon
     */
    void sendEvent(const ConnectorEvent& event);

    /**
     * 发送批量事件到daemon
     */
    void sendBatchEvents(const std::vector<ConnectorEvent>& events);

    /**
     * 发送大型JSON数据（自动分片传输）
     * @param endpoint IPC端点
     * @param jsonData 大型JSON数据
     * @return 传输是否成功
     */
    bool sendLargeJsonData(const std::string& endpoint, const nlohmann::json& jsonData);

    /**
     * 发送分片数据
     * @param chunks 分片列表
     * @param endpoint IPC端点
     * @return 成功发送的分片数量
     */
    size_t sendChunkedData(const std::vector<ChunkManager::ChunkInfo>& chunks, 
                          const std::string& endpoint);

    /**
     * 获取配置管理器
     */
    ConfigManager& getConfigManager() { return *m_configManager; }

    /**
     * 获取客户端
     */
    UnifiedClient& getClient() { return *m_client; }

    /**
     * 记录错误
     */
    void setError(const std::string& error, const std::string& details = "");

    /**
     * 记录信息日志
     */
    void logInfo(const std::string& message);

    /**
     * 记录错误日志
     */
    void logError(const std::string& message);

    /**
     * 记录警告日志
     */
    void logWarn(const std::string& message);

    /**
     * 获取连接器ID
     */
    const std::string& getId() const { return m_connectorId; }
    
    /**
     * 启动优雅停止流程
     * @param timeoutMs 停止超时时间（毫秒）
     * @return 是否在超时前完成停止
     */
    bool gracefulShutdown(std::chrono::milliseconds timeoutMs = std::chrono::milliseconds(30000));
    
    /**
     * 检查是否正在停止
     */
    bool isShuttingDown() const { return m_shuttingDown.load(); }
    
    /**
     * 等待当前操作完成
     */
    void waitForCurrentOperations();

private:
    // 连接器信息
    std::string m_connectorId;
    std::string m_displayName;

    // 核心组件
    std::unique_ptr<UnifiedClient> m_client;
    std::unique_ptr<ConfigManager> m_configManager;
    std::unique_ptr<ConnectorStatusManager> m_statusManager;
    std::unique_ptr<IConnectorMonitor> m_monitor;
    std::unique_ptr<ChunkManager> m_chunkManager;

    // 运行状态
    std::atomic<bool> m_running{false};
    std::atomic<bool> m_initialized{false};
    std::atomic<bool> m_shuttingDown{false};
    std::atomic<size_t> m_activeOperations{0};

    // 批处理配置
    std::chrono::milliseconds m_batchInterval{300};
    size_t m_maxBatchSize{50};

    // 批处理队列
    std::queue<ConnectorEvent> m_eventQueue;
    std::mutex m_queueMutex;
    std::thread m_batchThread;
    std::atomic<bool> m_batchThreadRunning{false};

    // 心跳线程
    std::thread m_heartbeatThread;
    std::atomic<bool> m_heartbeatRunning{false};

    // 统计信息
    mutable std::mutex m_statsMutex;
    size_t m_eventsSent{0};
    size_t m_batchesSent{0};
    size_t m_errorsOccurred{0};
    std::chrono::system_clock::time_point m_startTime;

    // 内部方法
    void eventCallback(const ConnectorEvent& event);
    void batchProcessingLoop();
    void heartbeatLoop();
    void processBatch();
    bool connectToDaemon(int timeoutSeconds);

    // 信号处理
    static void setupSignalHandlers();
    static void signalHandler(int signum);
    
public:
    static std::atomic<bool> s_shouldStop;
};

} // namespace linch_connector