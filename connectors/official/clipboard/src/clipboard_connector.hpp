#pragma once

#include <linch_connector/base_connector.hpp>
#include <linch_connector/enhanced_config.hpp>
#include "clipboard_monitor_adapter.hpp"

namespace linch_connector {

/**
 * 剪贴板连接器 - 使用新的统一架构
 * 大幅简化实现，消除代码重复
 */
class ClipboardConnector : public BaseConnector {
public:
    ClipboardConnector();
    ~ClipboardConnector() override = default;

protected:
    // 实现BaseConnector纯虚函数
    std::unique_ptr<IConnectorMonitor> createMonitor() override;
    bool loadConnectorConfig() override;
    bool onInitialize() override;
    bool onStart() override;
    void onStop() override;

private:
    EnhancedConfig::ClipboardConfig m_config;
    
    void logConfig();
};

} // namespace linch_connector