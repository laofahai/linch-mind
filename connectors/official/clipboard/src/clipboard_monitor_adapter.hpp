#pragma once

#include <linch_connector/connector_event.hpp>
#include <linch_connector/unified_config.hpp>
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

    // IConnectorMonitor 接口实现 - 零拷贝优化版本
    bool start(std::function<void(ConnectorEvent&&)> callback) override;
    void stop() override;
    bool isRunning() const override;
    Statistics getStatistics() const override;

    /**
     * 设置统一配置 - 新的配置接口
     */
    bool setConfig(const config::ClipboardConfig& config);
    
    /**
     * 获取当前配置
     */
    config::ClipboardConfig getConfig() const;
    
    /**
     * 获取当前剪贴板内容
     */
    std::string getCurrentContent();

private:
    std::unique_ptr<ClipboardMonitor> m_monitor;
    std::function<void(ConnectorEvent&&)> m_eventCallback;
    std::string m_lastContent;
    
    // 配置
    config::ClipboardConfig m_config;
    
    // 统计信息
    mutable std::mutex m_statsMutex;
    size_t m_eventsProcessed{0};
    std::chrono::system_clock::time_point m_startTime;
    bool m_isRunning{false};

    void onClipboardChange(const std::string& content);
};

} // namespace linch_connector