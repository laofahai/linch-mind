#pragma once

#include <linch_connector/connector_event.hpp>

namespace linch_connector {

/**
 * 空监控器 - 不执行任何监控操作
 * 用于只需要手动触发操作的连接器
 */
class NullMonitor : public IConnectorMonitor {
public:
    NullMonitor() = default;
    ~NullMonitor() override = default;

    bool start(std::function<void(ConnectorEvent&&)> callback) override {
        // 保存回调但不启动任何监控
        m_callback = std::move(callback);
        m_running = true;
        return true;
    }

    void stop() override {
        m_running = false;
        m_callback = nullptr;
    }

    bool isRunning() const override {
        return m_running;
    }

    Statistics getStatistics() const override {
        Statistics stats;
        stats.eventsProcessed = 0;
        stats.eventsFiltered = 0;
        stats.pathsMonitored = 0;
        stats.platformInfo = "NullMonitor (No Active Monitoring)";
        stats.startTime = std::chrono::system_clock::now();
        stats.isRunning = m_running;
        return stats;
    }

private:
    std::function<void(ConnectorEvent&&)> m_callback;
    bool m_running = false;
};

} // namespace linch_connector