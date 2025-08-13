#include "clipboard_connector.hpp"
#include <iostream>

namespace linch_connector {

ClipboardConnector::ClipboardConnector() 
    : BaseConnector("clipboard", "剪贴板连接器")
{
}

std::unique_ptr<IConnectorMonitor> ClipboardConnector::createMonitor() {
    return std::make_unique<ClipboardMonitorAdapter>();
}

bool ClipboardConnector::loadConnectorConfig() {
    EnhancedConfig enhancedConfig(getConfigManager());
    m_config = enhancedConfig.getClipboardConfig();
    
    logConfig();
    return true;
}

bool ClipboardConnector::onInitialize() {
    logInfo("📋 剪贴板连接器初始化完成");
    logInfo("🎯 监控模式: 事件驱动 (高性能)");
    return true;
}

bool ClipboardConnector::onStart() {
    // 设置批处理配置
    setBatchConfig(std::chrono::milliseconds(m_config.pollInterval), 20);
    
    logInfo("📋 剪贴板监控已启动");
    return true;
}

void ClipboardConnector::onStop() {
    logInfo("📋 剪贴板监控已停止");
}

void ClipboardConnector::logConfig() {
    logInfo("📋 剪贴板配置加载:");
    logInfo("   轮询间隔: " + std::to_string(m_config.pollInterval) + "ms");
    logInfo("   最大内容长度: " + std::to_string(m_config.maxContentLength));
    logInfo("   启用内容过滤: " + std::string(m_config.enableContentFilter ? "是" : "否"));
    logInfo("   启用历史记录: " + std::string(m_config.enableHistory ? "是" : "否"));
    if (m_config.enableHistory) {
        logInfo("   历史记录大小: " + std::to_string(m_config.historySize));
    }
}

} // namespace linch_connector