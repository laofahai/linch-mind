#pragma once

#include <linch_connector/base_connector.hpp>
#include <linch_connector/enhanced_config.hpp>
#include "filesystem_monitor_adapter.hpp"
#include "file_index_provider.hpp"
#include "zero_scan/zero_scan_interface.hpp"

namespace linch_connector {

/**
 * 文件系统连接器 - 零扫描架构
 * 
 * 新架构特点：
 * 1. 双重模式：实时监控 + 零扫描索引
 * 2. 利用系统已有索引：Spotlight/MFT/locate
 * 3. 最小系统负担：避免全盘扫描
 * 4. 流式数据传输：批量IPC通信
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
    // 配置
    EnhancedConfig::FileSystemConfig m_config;
    
    // 双重监控模式
    FilesystemMonitorAdapter* m_fsAdapter{nullptr};          // 实时监控适配器
    std::unique_ptr<FileIndexProvider> m_indexProvider;      // 文件索引提供者
    std::unique_ptr<zero_scan::IZeroScanProvider> m_zeroScanProvider;  // 零扫描提供者
    
    // 初始化和配置
    void logConfig();
    bool setupRealtimeMonitoring();  // 设置实时文件监控
    bool setupIndexProvider();       // 设置文件索引提供者
    bool setupZeroScanProvider();    // 设置零扫描提供者
    
    // FileIndexProvider回调处理
    void onInitialBatch(const std::vector<FileInfo>& files);
    void onFileEvent(const FileEvent& event);
    void onIndexProgress(uint64_t indexed, uint64_t total);
    
    // ZeroScanProvider回调处理
    void onZeroScanFile(const zero_scan::UnifiedFileRecord& record);
    void onZeroScanChange(const zero_scan::FileChangeEvent& event);
    
    // 数据转换和发送
    ConnectorEvent convertFileInfoToEvent(const FileInfo& fileInfo, const std::string& eventType);
    ConnectorEvent convertFileEventToEvent(const FileEvent& fileEvent);
    void sendFileInfoBatch(const std::vector<FileInfo>& files);
    
    // 状态管理
    std::atomic<bool> m_indexInitialized{false};
    std::atomic<bool> m_realtimeActive{false};
    std::atomic<uint64_t> m_totalIndexedFiles{0};
    
    // 性能统计
    std::chrono::steady_clock::time_point m_startTime;
    void logPerformanceStats();
};

} // namespace linch_connector