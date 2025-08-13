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
    try {
        auto response = m_client->post("/events/submit", event.toJson().dump());
        
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
}

void BaseConnector::sendBatchEvents(const std::vector<ConnectorEvent>& events) {
    if (events.empty()) {
        return;
    }

    try {
        json batch_data = json::array();
        for (const auto& event : events) {
            batch_data.push_back(event.toJson());
        }

        json request_data = {
            {"batch_events", batch_data}
        };

        auto response = m_client->post("/events/submit_batch", request_data.dump());
        
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
    } catch (const std::exception& e) {
        logError("❌ 发送批量事件异常: " + std::string(e.what()));
        std::lock_guard<std::mutex> lock(m_statsMutex);
        m_errorsOccurred++;
    }
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
    std::cout << "\n📡 收到信号 " << signum << "，正在停止连接器..." << std::endl;
    s_shouldStop.store(true);
}

} // namespace linch_connector