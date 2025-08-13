#include "clipboard_monitor_adapter.hpp"
#include <linch_connector/optimized_event_utils.hpp>
#include <iostream>

namespace linch_connector {

ClipboardMonitorAdapter::ClipboardMonitorAdapter()
    : m_monitor(std::make_unique<ClipboardMonitor>())
    , m_config(config::ClipboardConfig::createDefault())
{
}

ClipboardMonitorAdapter::~ClipboardMonitorAdapter() {
    stop();
}

bool ClipboardMonitorAdapter::start(std::function<void(ConnectorEvent&&)> callback) {
    if (m_isRunning) {
        return false;
    }

    m_eventCallback = callback;
    m_startTime = std::chrono::system_clock::now();
    
    // 获取初始内容
    m_lastContent = m_monitor->getCurrentContent();
    
    // 启动监控
    auto clipboardCallback = [this](const std::string& content) {
        onClipboardChange(content);
    };
    
    if (m_monitor->startMonitoring(clipboardCallback)) {
        std::lock_guard<std::mutex> lock(m_statsMutex);
        m_isRunning = true;
        return true;
    }
    
    return false;
}

void ClipboardMonitorAdapter::stop() {
    if (!m_isRunning) {
        return;
    }
    
    m_monitor->stopMonitoring();
    
    std::lock_guard<std::mutex> lock(m_statsMutex);
    m_isRunning = false;
}

bool ClipboardMonitorAdapter::isRunning() const {
    std::lock_guard<std::mutex> lock(m_statsMutex);
    return m_isRunning;
}

IConnectorMonitor::Statistics ClipboardMonitorAdapter::getStatistics() const {
    std::lock_guard<std::mutex> lock(m_statsMutex);
    
    Statistics stats;
    stats.eventsProcessed = m_eventsProcessed;
    stats.eventsFiltered = 0; // 暂时不实现过滤功能
    stats.pathsMonitored = 1; // 剪贴板只有一个"路径"
    stats.platformInfo = "Clipboard Monitor (Event-Driven)";
    stats.startTime = m_startTime;
    stats.isRunning = m_isRunning;
    
    return stats;
}

std::string ClipboardMonitorAdapter::getCurrentContent() {
    return m_monitor->getCurrentContent();
}

void ClipboardMonitorAdapter::onClipboardChange(const std::string& content) {
    // 早期返回，避免不必要的处理
    if (!m_eventCallback || content == m_lastContent) {
        return;
    }
    
    // 基础长度检查 - 防止系统崩溃
    if (content.length() > m_config.maxContentLength) {
        std::cout << "📋 剪贴板内容过长，已截断: " << content.length() << " 字符" << std::endl;
        return;
    }
    
    // 存储内容
    m_lastContent = content;
    
    // 创建事件
    ConnectorEvent event = optimization::EventUtils::createClipboardEvent(content);
    
    // 更新统计
    {
        std::lock_guard<std::mutex> lock(m_statsMutex);
        m_eventsProcessed++;
    }
    
    // 传递事件
    m_eventCallback(std::move(event));
}

bool ClipboardMonitorAdapter::setConfig(const config::ClipboardConfig& config) {
    std::string errorMessage;
    if (!config.validate(errorMessage)) {
        std::cerr << "配置验证失败: " << errorMessage << std::endl;
        return false;
    }
    
    m_config = config;
    std::cout << "✅ " << config.getDescription() << std::endl;
    return true;
}

config::ClipboardConfig ClipboardMonitorAdapter::getConfig() const {
    return m_config;
}

} // namespace linch_connector