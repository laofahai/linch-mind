#pragma once

#include <linch_connector/connector_event.hpp>
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

    // IConnectorMonitor 接口实现
    bool start(std::function<void(const ConnectorEvent&)> callback) override;
    void stop() override;
    bool isRunning() const override;
    Statistics getStatistics() const override;

    /**
     * 添加监控路径
     */
    bool addPath(const MonitorConfig& config);

    /**
     * 移除监控路径
     */
    bool removePath(const std::string& path);

    /**
     * 获取监控的路径列表
     */
    std::vector<std::string> getMonitoredPaths() const;

    /**
     * 设置批处理回调
     */
    void setBatchCallback(std::function<void(const std::vector<ConnectorEvent>&)> callback,
                         std::chrono::milliseconds interval = std::chrono::milliseconds(300));

private:
    std::unique_ptr<FileSystemMonitor> m_monitor;
    std::function<void(const ConnectorEvent&)> m_eventCallback;
    std::function<void(const std::vector<ConnectorEvent>&)> m_batchCallback;
    
    void onFileSystemEvent(const FileSystemEvent& event);
    void onBatchFileSystemEvents(const std::vector<FileSystemEvent>& events);
    
    ConnectorEvent convertFileSystemEvent(const FileSystemEvent& event) const;
};

} // namespace linch_connector