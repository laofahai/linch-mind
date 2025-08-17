#pragma once

#include <linch_connector/base_connector.hpp>
#include "file_index_query.hpp"
#include "null_monitor.hpp"

namespace linch_connector {

/**
 * 简化的文件系统连接器
 * 
 * 核心功能：
 * 1. 利用系统文件索引（macOS Spotlight/Windows Search/Linux locate）
 * 2. 简单的daemon交互
 * 3. 无复杂监控、无异步处理、无缓冲机制
 */
class FilesystemConnector : public BaseConnector {
public:
    FilesystemConnector();
    ~FilesystemConnector() override = default;
    
    /**
     * 手动触发文件索引查询
     * 查询系统中的文档文件并发送给daemon
     */
    void performFileQuery();
    
    /**
     * 启动定时全量扫描（每30分钟一次）
     */
    void startPeriodicScanning();
    
    /**
     * 停止定时全量扫描
     */
    void stopPeriodicScanning();

protected:
    // 实现BaseConnector纯虚函数
    std::unique_ptr<IConnectorMonitor> createMonitor() override;
    bool loadConnectorConfig() override;
    bool onInitialize() override;
    bool onStart() override;
    void onStop() override;

private:
    // 文件索引查询器
    std::unique_ptr<IFileIndexQuery> m_indexQuery;
    
    // 定时扫描线程
    std::unique_ptr<std::thread> m_scanThread;
    std::atomic<bool> m_shouldStopScanning{false};
    
    /**
     * 将FileRecord转换为ConnectorEvent
     */
    ConnectorEvent convertFileRecordToEvent(const FileRecord& record);
    
    /**
     * 批量发送文件事件给daemon
     */
    void sendFileRecords(const std::vector<FileRecord>& records);
};

} // namespace linch_connector