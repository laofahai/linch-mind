#pragma once

#include <linch_connector/connector_event.hpp>
#include <linch_connector/unified_config.hpp>
#include "monitor_factory.hpp"
#include <memory>
#include <vector>

namespace linch_connector {

/**
 * 文件系统监控器适配器
 * 将现有的FileSystemMonitor适配为统一的IConnectorMonitor接口
 */
class FilesystemMonitorAdapter : public IConnectorMonitor {
public:
    FilesystemMonitorAdapter();
    ~FilesystemMonitorAdapter() override;

    // IConnectorMonitor 接口实现 - 零拷贝优化版本
    bool start(std::function<void(ConnectorEvent&&)> callback) override;
    void stop() override;
    bool isRunning() const override;
    Statistics getStatistics() const override;

    /**
     * 设置统一配置 - 新的配置接口
     */
    bool setConfig(const config::FilesystemConfig& config);
    
    /**
     * 获取当前配置
     */
    config::FilesystemConfig getConfig() const;
    
    /**
     * 添加监控路径 (兼容接口)
     */
    bool addPath(const MonitorConfig& legacyConfig);

    /**
     * 移除监控路径
     */
    bool removePath(const std::string& path);

    /**
     * 获取监控的路径列表
     */
    std::vector<std::string> getMonitoredPaths() const;

    /**
     * 设置批处理回调 - 零拷贝优化版本
     */
    void setBatchCallback(std::function<void(std::vector<ConnectorEvent>&&)> callback,
                         std::chrono::milliseconds interval = std::chrono::milliseconds(300));

private:
    std::function<void(ConnectorEvent&&)> m_eventCallback;
    std::function<void(std::vector<ConnectorEvent>&&)> m_batchCallback;
    
    // 🚀 统一配置系统
    config::FilesystemConfig m_config;
    
    // 简化的运行状态
    bool m_running;
    
    // 🚀 性能优化: 轻量级事件类型转换
    std::string_view getEventTypeString(FileEventType type) const;
};

} // namespace linch_connector