#pragma once

#include <linch_connector/connector_event.hpp>
#include "clipboard_monitor.hpp"
#include <memory>
#include <mutex>

namespace linch_connector {

/**
 * 剪贴板监控器适配器
 * 将原有ClipboardMonitor适配为统一的IConnectorMonitor接口
 */
class ClipboardMonitorAdapter : public IConnectorMonitor {
public:
    ClipboardMonitorAdapter();
    ~ClipboardMonitorAdapter() override;

    // IConnectorMonitor 接口实现
    bool start(std::function<void(const ConnectorEvent&)> callback) override;
    void stop() override;
    bool isRunning() const override;
    Statistics getStatistics() const override;

    /**
     * 获取当前剪贴板内容
     */
    std::string getCurrentContent();

private:
    std::unique_ptr<ClipboardMonitor> m_monitor;
    std::function<void(const ConnectorEvent&)> m_eventCallback;
    std::string m_lastContent;
    
    // 统计信息
    mutable std::mutex m_statsMutex;
    size_t m_eventsProcessed{0};
    std::chrono::system_clock::time_point m_startTime;
    bool m_isRunning{false};

    void onClipboardChange(const std::string& content);
};

} // namespace linch_connector