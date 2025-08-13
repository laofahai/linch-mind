#include "clipboard_monitor_adapter.hpp"
#include <iostream>

namespace linch_connector {

ClipboardMonitorAdapter::ClipboardMonitorAdapter()
    : m_monitor(std::make_unique<ClipboardMonitor>())
{
}

ClipboardMonitorAdapter::~ClipboardMonitorAdapter() {
    stop();
}

bool ClipboardMonitorAdapter::start(std::function<void(const ConnectorEvent&)> callback) {
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
    if (!m_eventCallback || content == m_lastContent) {
        return;
    }
    
    m_lastContent = content;
    
    // 创建剪贴板事件
    json eventData = {
        {"content", content},
        {"content_length", content.length()},
        {"content_type", "text"}, // 目前只支持文本
        {"timestamp", std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count()}
    };
    
    ConnectorEvent event = ConnectorEvent::create("clipboard", "changed", eventData);
    
    // 更新统计信息
    {
        std::lock_guard<std::mutex> lock(m_statsMutex);
        m_eventsProcessed++;
    }
    
    // 调用回调
    m_eventCallback(event);
}

} // namespace linch_connector