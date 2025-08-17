#include "linch_connector/base_connector.hpp"
#include "linch_connector/daemon_discovery.hpp"
#include "linch_connector/utils.hpp"
#include <iostream>
#include <signal.h>
#include <algorithm>

namespace linch_connector {

// 静态成员初始化
std::atomic<bool> BaseConnector::s_shouldStop{false};

BaseConnector::BaseConnector(const std::string& connectorId, const std::string& displayName)
    : m_connectorId(connectorId)
    , m_displayName(displayName)
    , m_client(std::make_unique<UnifiedClient>())
    , m_configManager(std::make_unique<ConfigManager>(connectorId, ""))
    , m_statusManager(std::make_unique<ConnectorStatusManager>(connectorId, displayName))
{
    setupSignalHandlers();
    
    // 初始化分片管理器（根据CLAUDE.md中的IPC性能要求配置）
    ChunkManager::ChunkConfig chunkConfig;
    chunkConfig.maxChunkSize = 32 * 1024;  // 32KB - 确保IPC延迟<10ms
    chunkConfig.maxRetries = 3;
    chunkConfig.retryDelay = std::chrono::milliseconds(50);
    chunkConfig.minChunkSize = 1024;       // 1KB最小分片
    m_chunkManager = std::make_unique<ChunkManager>(chunkConfig);
}

BaseConnector::~BaseConnector() {
    stop();
}

bool BaseConnector::initialize(int daemonTimeout) {
    if (m_initialized.load()) {
        logInfo("连接器已经初始化");
        return true;
    }

    logInfo("🚀 正在初始化 " + m_displayName + " 连接器...");

    // 连接到daemon
    if (!connectToDaemon(daemonTimeout)) {
        setError("Failed to connect to daemon", "Timeout or connection error");
        return false;
    }

    // 加载配置
    if (!m_configManager->loadFromDaemon()) {
        logError("⚠️ 无法从daemon加载配置，使用默认配置");
    }

    // 加载连接器特定配置
    if (!loadConnectorConfig()) {
        setError("Failed to load connector configuration");
        return false;
    }

    // 创建监控器
    m_monitor = createMonitor();
    if (!m_monitor) {
        setError("Failed to create monitor");
        return false;
    }

    // 子类自定义初始化
    if (!onInitialize()) {
        setError("Connector-specific initialization failed");
        return false;
    }

    // 设置为启动状态
    m_statusManager->setState(ConnectorRunningState::STARTING);
    m_statusManager->notifyStarting(*m_client);

    m_initialized.store(true);
    logInfo("✅ " + m_displayName + " 连接器初始化完成");
    return true;
}

bool BaseConnector::start() {
    if (!m_initialized.load()) {
        logError("连接器未初始化，请先调用initialize()");
        return false;
    }

    if (m_running.load()) {
        logInfo("连接器已在运行");
        return true;
    }

    logInfo("▶️ 正在启动 " + m_displayName + " 连接器...");
    m_startTime = std::chrono::system_clock::now();

    // 启动监控器
    auto eventCb = [this](const ConnectorEvent& event) {
        eventCallback(event);
    };

    if (!m_monitor->start(eventCb)) {
        setError("Failed to start monitor");
        return false;
    }

    // 启动批处理线程
    m_batchThreadRunning.store(true);
    m_batchThread = std::thread(&BaseConnector::batchProcessingLoop, this);

    // 启动心跳线程
    m_heartbeatRunning.store(true);
    m_heartbeatThread = std::thread(&BaseConnector::heartbeatLoop, this);

    // 子类自定义启动逻辑
    if (!onStart()) {
        stop();
        setError("Connector-specific start failed");
        return false;
    }

    // 设置为运行状态
    m_running.store(true);
    m_statusManager->setState(ConnectorRunningState::RUNNING);
    m_statusManager->sendStatusUpdate(*m_client);

    logInfo("✅ " + m_displayName + " 连接器已启动");
    return true;
}

void BaseConnector::stop() {
    if (!m_running.load()) {
        return;
    }

    logInfo("🛑 正在停止 " + m_displayName + " 连接器...");

    // 设置为停止状态
    m_statusManager->setState(ConnectorRunningState::STOPPING);
    m_statusManager->notifyStopping(*m_client);

    // 停止监控器
    if (m_monitor) {
        m_monitor->stop();
    }

    // 子类自定义停止逻辑
    onStop();

    // 停止批处理线程
    m_batchThreadRunning.store(false);
    if (m_batchThread.joinable()) {
        m_batchThread.join();
    }

    // 停止心跳线程
    m_heartbeatRunning.store(false);
    if (m_heartbeatThread.joinable()) {
        m_heartbeatThread.join();
    }

    // 处理剩余的批处理事件
    processBatch();

    m_running.store(false);
    logInfo("✅ " + m_displayName + " 连接器已停止");

    // 显示最终统计信息
    auto stats = getStatistics();
    logInfo("📊 最终统计: " + std::to_string(stats.eventsProcessed) + " 事件已处理");
}

bool BaseConnector::isRunning() const {
    return m_running.load();
}

IConnectorMonitor::Statistics BaseConnector::getStatistics() const {
    std::lock_guard<std::mutex> lock(m_statsMutex);
    
    auto stats = m_monitor ? m_monitor->getStatistics() : IConnectorMonitor::Statistics{};
    
    // 添加连接器级别的统计信息
    stats.eventsProcessed = m_eventsSent;
    stats.startTime = m_startTime;
    stats.isRunning = m_running.load();
    
    return stats;
}

void BaseConnector::setBatchConfig(std::chrono::milliseconds interval, size_t maxBatchSize) {
    m_batchInterval = interval;
    m_maxBatchSize = maxBatchSize;
    logInfo("📊 批处理配置: 间隔=" + std::to_string(interval.count()) + "ms, 最大大小=" + std::to_string(maxBatchSize));
}

void BaseConnector::sendEvent(const ConnectorEvent& event) {
    // 检查是否正在停止
    if (m_shuttingDown.load()) {
        logWarn("⚠️ 连接器正在停止，跳过事件发送");
        return;
    }
    
    // 增加活跃操作计数
    m_activeOperations.fetch_add(1);
    
    try {
        // 🛡️ 防护机制：检查事件有效性
        if (!event.isValid()) {
            logInfo("🚫 跳过无效事件 (connectorId: '" + event.connectorId + 
                   "', eventType: '" + event.eventType + "')");
            m_activeOperations.fetch_sub(1);
            return;
        }
        
        // 使用安全的JSON序列化
        auto jsonData = event.toJson();
        std::string safeJsonStr = utils::safeJsonDump(jsonData);
        
        auto response = m_client->post("/events/submit", safeJsonStr);
        
        if (response.success) {
            std::lock_guard<std::mutex> lock(m_statsMutex);
            m_eventsSent++;
            logInfo("✅ 已发送事件: " + event.eventType);
        } else {
            logError("❌ 发送事件失败: " + response.error_message + 
                    " (代码: " + response.error_code + ")");
            std::lock_guard<std::mutex> lock(m_statsMutex);
            m_errorsOccurred++;
        }
    } catch (const std::exception& e) {
        logError("❌ 发送事件异常: " + std::string(e.what()));
        std::lock_guard<std::mutex> lock(m_statsMutex);
        m_errorsOccurred++;
    }
    
    // 减少活跃操作计数
    m_activeOperations.fetch_sub(1);
}

void BaseConnector::sendBatchEvents(const std::vector<ConnectorEvent>& events) {
    if (events.empty()) {
        return;
    }
    
    // 检查是否正在停止
    if (m_shuttingDown.load()) {
        logWarn("⚠️ 连接器正在停止，跳过批量事件发送");
        return;
    }
    
    // 增加活跃操作计数
    m_activeOperations.fetch_add(1);

    try {
        json batch_data = json::array();
        for (const auto& event : events) {
            batch_data.push_back(event.toJson());
        }

        json request_data = {
            {"connector_id", utils::cleanString(m_connectorId)},
            {"events", batch_data}
        };

        // 检查批量数据大小，如果过大则使用分片传输
        std::string safeJsonStr = utils::safeJsonDump(request_data);
        
        // 如果批量数据超过64KB，使用分片传输
        if (safeJsonStr.size() > 64 * 1024) {
            logInfo("📦 批量数据较大 (" + std::to_string(safeJsonStr.size()) + " 字节)，使用分片传输");
            
            bool chunkSuccess = sendLargeJsonData("/events/submit_batch", request_data);
            if (chunkSuccess) {
                std::lock_guard<std::mutex> lock(m_statsMutex);
                m_eventsSent += events.size();
                m_batchesSent++;
                logInfo("✅ 已通过分片发送批量事件: " + std::to_string(events.size()) + " 个");
            } else {
                logError("❌ 分片发送批量事件失败");
                // 降级到逐个发送
                logInfo("🔄 降级为逐个发送事件...");
                for (const auto& event : events) {
                    sendEvent(event);
                }
            }
        } else {
            // 正常发送
            auto response = m_client->post("/events/submit_batch", safeJsonStr);
            
            if (response.success) {
                std::lock_guard<std::mutex> lock(m_statsMutex);
                m_eventsSent += events.size();
                m_batchesSent++;
                logInfo("✅ 已发送批量事件: " + std::to_string(events.size()) + " 个");
            } else {
                logError("❌ 发送批量事件失败: " + response.error_message);
                
                // 如果批量发送失败，尝试逐个发送
                logInfo("🔄 正在逐个重试发送事件...");
                for (const auto& event : events) {
                    sendEvent(event);
                }
            }
        }
    } catch (const std::exception& e) {
        logError("❌ 发送批量事件异常: " + std::string(e.what()));
        std::lock_guard<std::mutex> lock(m_statsMutex);
        m_errorsOccurred++;
    }
    
    // 减少活跃操作计数
    m_activeOperations.fetch_sub(1);
}

void BaseConnector::setError(const std::string& error, const std::string& details) {
    std::string fullError = error;
    if (!details.empty()) {
        fullError += " - " + details;
    }
    
    m_statusManager->setError(fullError);
    m_statusManager->sendStatusUpdate(*m_client);
    logError("🚨 " + fullError);
    
    std::lock_guard<std::mutex> lock(m_statsMutex);
    m_errorsOccurred++;
}

void BaseConnector::logInfo(const std::string& message) {
    std::cout << "[" << m_connectorId << "] " << message << std::endl;
}

void BaseConnector::logError(const std::string& message) {
    std::cerr << "[" << m_connectorId << "] " << message << std::endl;
}

void BaseConnector::logWarn(const std::string& message) {
    std::cout << "[" << m_connectorId << "] WARN: " << message << std::endl;
}

void BaseConnector::eventCallback(const ConnectorEvent& event) {
    // 将事件添加到批处理队列
    std::lock_guard<std::mutex> lock(m_queueMutex);
    m_eventQueue.push(event);
}

void BaseConnector::batchProcessingLoop() {
    while (m_batchThreadRunning.load()) {
        auto start = std::chrono::steady_clock::now();
        
        processBatch();
        
        auto elapsed = std::chrono::steady_clock::now() - start;
        auto sleep_time = m_batchInterval - std::chrono::duration_cast<std::chrono::milliseconds>(elapsed);
        
        if (sleep_time > std::chrono::milliseconds(0)) {
            std::this_thread::sleep_for(sleep_time);
        }
    }
}

void BaseConnector::heartbeatLoop() {
    const auto heartbeatInterval = std::chrono::seconds(30);
    
    while (m_heartbeatRunning.load()) {
        m_statusManager->sendHeartbeat(*m_client);
        std::this_thread::sleep_for(heartbeatInterval);
    }
}

void BaseConnector::processBatch() {
    std::vector<ConnectorEvent> batch;
    
    {
        std::lock_guard<std::mutex> lock(m_queueMutex);
        
        // 收集批量事件
        while (!m_eventQueue.empty() && batch.size() < m_maxBatchSize) {
            batch.push_back(m_eventQueue.front());
            m_eventQueue.pop();
        }
    }
    
    if (!batch.empty()) {
        if (batch.size() == 1) {
            sendEvent(batch[0]);
        } else {
            sendBatchEvents(batch);
        }
    }
}

bool BaseConnector::connectToDaemon(int timeoutSeconds) {
    logInfo("🔍 正在发现daemon...");
    
    DaemonDiscovery discovery;
    auto daemonInfoOpt = discovery.waitForDaemon(std::chrono::seconds(timeoutSeconds));
    
    if (!daemonInfoOpt) {
        logError("❌ 无法发现daemon，超时：" + std::to_string(timeoutSeconds) + "秒");
        return false;
    }
    
    m_client->setTimeout(60); // 文件操作可能需要更长时间
    
    if (!m_client->connect(*daemonInfoOpt)) {
        logError("❌ 无法连接到daemon");
        return false;
    }
    
    logInfo("🔗 已通过IPC连接到daemon");
    return true;
}

void BaseConnector::setupSignalHandlers() {
    signal(SIGINT, signalHandler);
    signal(SIGTERM, signalHandler);
}

void BaseConnector::signalHandler(int signum) {
    std::cout << "\n📡 收到信号 " << signum << "，启动优雅停止..." << std::endl;
    s_shouldStop.store(true);
    
    // 注意：在信号处理器中只能做最小的操作
    // 实际的优雅停止逻辑在主线程中执行
}

bool BaseConnector::sendLargeJsonData(const std::string& endpoint, const nlohmann::json& jsonData) {
    try {
        auto start = std::chrono::steady_clock::now();
        
        // 尝试直接发送（如果数据不大）
        std::string jsonString = utils::safeJsonDump(jsonData);
        
        // 如果小于16KB，直接发送
        if (jsonString.size() <= 16 * 1024) {
            auto response = m_client->post(endpoint, jsonString);
            if (response.success) {
                logInfo("✅ 直接发送JSON数据成功 (" + std::to_string(jsonString.size()) + " 字节)");
                return true;
            }
        }
        
        // 大数据使用分片传输
        logInfo("📦 数据较大 (" + std::to_string(jsonString.size()) + " 字节)，启用分片传输");
        
        auto chunks = m_chunkManager->chunkifyJson(jsonData);
        if (chunks.empty()) {
            logError("❌ 分片失败");
            return false;
        }
        
        size_t successCount = sendChunkedData(chunks, endpoint + "_chunked");
        
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::steady_clock::now() - start);
        
        bool success = (successCount == chunks.size());
        logInfo("📊 分片传输完成: " + std::to_string(successCount) + "/" + 
                std::to_string(chunks.size()) + " 分片，耗时 " + 
                std::to_string(duration.count()) + "ms");
        
        return success;
        
    } catch (const std::exception& e) {
        logError("❌ 大数据传输异常: " + std::string(e.what()));
        return false;
    }
}

size_t BaseConnector::sendChunkedData(const std::vector<ChunkManager::ChunkInfo>& chunks, 
                                      const std::string& endpoint) {
    size_t successCount = 0;
    const auto& config = m_chunkManager->getConfig();
    
    for (const auto& chunk : chunks) {
        bool chunkSuccess = false;
        
        // 重试机制
        for (size_t retry = 0; retry <= config.maxRetries; ++retry) {
            try {
                nlohmann::json chunkMessage = m_chunkManager->createChunkMessage(chunk);
                std::string chunkJsonStr = utils::safeJsonDump(chunkMessage);
                
                auto response = m_client->post(endpoint, chunkJsonStr);
                
                if (response.success) {
                    chunkSuccess = true;
                    break;
                } else {
                    logWarn("⚠️ 分片 " + std::to_string(chunk.chunkIndex) + "/" + 
                           std::to_string(chunk.totalChunks) + " 发送失败 (尝试 " + 
                           std::to_string(retry + 1) + "/" + std::to_string(config.maxRetries + 1) + 
                           "): " + response.error_message);
                    
                    // 根据错误类型调整分片大小
                    if (retry == config.maxRetries) {
                        m_chunkManager->adaptChunkSize(response.error_code);
                    }
                }
            } catch (const std::exception& e) {
                logError("❌ 分片传输异常 (尝试 " + std::to_string(retry + 1) + "): " + 
                        std::string(e.what()));
            }
            
            // 重试延迟
            if (retry < config.maxRetries) {
                std::this_thread::sleep_for(config.retryDelay);
            }
        }
        
        if (chunkSuccess) {
            successCount++;
        } else {
            logError("❌ 分片 " + std::to_string(chunk.chunkIndex) + 
                    " 最终发送失败，会话ID: " + chunk.sessionId);
        }
    }
    
    return successCount;
}

bool BaseConnector::gracefulShutdown(std::chrono::milliseconds timeoutMs) {
    logInfo("🛑 启动优雅停止流程...");
    m_shuttingDown.store(true);
    
    auto shutdownStart = std::chrono::steady_clock::now();
    
    // 1. 停止接收新的任务
    if (m_running.load()) {
        logInfo("⏹️ 停止连接器主循环");
        m_running.store(false);
    }
    
    // 2. 等待当前操作完成
    logInfo("⌛ 等待当前操作完成...");
    waitForCurrentOperations();
    
    // 3. 停止批处理线程
    if (m_batchThreadRunning.load()) {
        logInfo("🔄 停止批处理线程");
        m_batchThreadRunning.store(false);
        if (m_batchThread.joinable()) {
            m_batchThread.join();
        }
    }
    
    // 4. 发送剩余的批处理事件
    {
        std::lock_guard<std::mutex> lock(m_queueMutex);
        if (!m_eventQueue.empty()) {
            logInfo("📦 发送剩余的 " + std::to_string(m_eventQueue.size()) + " 个事件");
            
            std::vector<ConnectorEvent> remainingEvents;
            while (!m_eventQueue.empty()) {
                remainingEvents.push_back(m_eventQueue.front());
                m_eventQueue.pop();
            }
            
            if (!remainingEvents.empty()) {
                sendBatchEvents(remainingEvents);
            }
        }
    }
    
    // 5. 停止监控器
    if (m_monitor) {
        logInfo("👁️ 停止监控器");
        m_monitor->stop();
    }
    
    // 6. 停止心跳线程
    if (m_heartbeatRunning.load()) {
        logInfo("💗 停止心跳线程");
        m_heartbeatRunning.store(false);
        if (m_heartbeatThread.joinable()) {
            m_heartbeatThread.join();
        }
    }
    
    // 7. 调用子类的停止逻辑
    try {
        onStop();
    } catch (const std::exception& e) {
        logError("⚠️ 停止过程中出现异常: " + std::string(e.what()));
    }
    
    auto shutdownDuration = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now() - shutdownStart);
    
    bool timedOut = shutdownDuration >= timeoutMs;
    
    if (timedOut) {
        logWarn("⚠️ 优雅停止超时 (" + std::to_string(shutdownDuration.count()) + 
                "ms > " + std::to_string(timeoutMs.count()) + "ms)");
    } else {
        logInfo("✅ 优雅停止完成，耗时 " + std::to_string(shutdownDuration.count()) + "ms");
    }
    
    return !timedOut;
}

void BaseConnector::waitForCurrentOperations() {
    auto startTime = std::chrono::steady_clock::now();
    const auto maxWaitTime = std::chrono::seconds(10);
    
    while (m_activeOperations.load() > 0) {
        auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(
            std::chrono::steady_clock::now() - startTime);
        
        if (elapsed >= maxWaitTime) {
            logWarn("⚠️ 等待操作完成超时，当前还有 " + 
                   std::to_string(m_activeOperations.load()) + " 个操作未完成");
            break;
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    
    if (m_activeOperations.load() == 0) {
        logInfo("✅ 所有操作已完成");
    }
}

} // namespace linch_connector