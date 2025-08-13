#pragma once

#include <linch_connector/base_connector.hpp>
#include <linch_connector/enhanced_config.hpp>
#include "filesystem_monitor_adapter.hpp"

namespace linch_connector {

/**
 * 文件系统连接器 - 使用新的统一架构
 * 大幅简化实现，消除代码重复
 */
class FilesystemConnector : public BaseConnector {
public:
    FilesystemConnector();
    ~FilesystemConnector() override = default;

protected:
    // 实现BaseConnector纯虚函数
    std::unique_ptr<IConnectorMonitor> createMonitor() override;
    bool loadConnectorConfig() override;
    bool onInitialize() override;
    bool onStart() override;
    void onStop() override;

private:
    EnhancedConfig::FileSystemConfig m_config;
    FilesystemMonitorAdapter* m_fsAdapter{nullptr}; // 用于访问特定功能
    
    void logConfig();
    bool setupWatchPaths();
};

} // namespace linch_connector