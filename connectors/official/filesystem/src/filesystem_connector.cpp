#include "filesystem_connector.hpp"
#include <linch_connector/utils.hpp>
#include <iostream>
#include <chrono>
#include <thread>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

namespace linch_connector {

FilesystemConnector::FilesystemConnector() 
    : BaseConnector("filesystem", "简化文件系统连接器")
{
    std::cout << "🚀 简化文件系统连接器初始化" << std::endl;
}

std::unique_ptr<IConnectorMonitor> FilesystemConnector::createMonitor() {
    // 暂时使用空监控器，专注于定时全量扫描
    return std::make_unique<NullMonitor>();
}

bool FilesystemConnector::loadConnectorConfig() {
    // 简化配置 - 只需要基本连接器配置
    logInfo("📋 加载简化配置");
    return true;
}

bool FilesystemConnector::onInitialize() {
    logInfo("🔧 初始化文件索引查询器");
    
    // 创建平台特定的文件索引查询器
    m_indexQuery = createFileIndexQuery();
    if (!m_indexQuery) {
        logError("❌ 无法创建文件索引查询器 - 平台不支持");
        return false;
    }
    
    if (!m_indexQuery->isAvailable()) {
        logError("❌ 文件索引查询器不可用");
        return false;
    }
    
    logInfo("✅ 文件索引查询器初始化成功: " + m_indexQuery->getProviderName());
    return true;
}

bool FilesystemConnector::onStart() {
    logInfo("🚀 启动简化文件系统连接器");
    
    if (!m_indexQuery) {
        logError("❌ 文件索引查询器未初始化");
        return false;
    }
    
    // 启动时执行一次文件查询
    performFileQuery();
    
    // 启动定时扫描
    startPeriodicScanning();
    
    logInfo("✅ 文件系统连接器启动成功");
    return true;
}

void FilesystemConnector::onStop() {
    logInfo("🛑 停止文件系统连接器");
    
    // 停止定时扫描
    stopPeriodicScanning();
    
    m_indexQuery.reset();
}

void FilesystemConnector::performFileQuery() {
    if (!m_indexQuery) {
        logError("❌ 文件索引查询器未初始化");
        return;
    }
    
    logInfo("🔍 开始查询文档文件...");
    auto startTime = std::chrono::steady_clock::now();
    
    try {
        // 查询所有文档文件
        std::vector<FileRecord> records = m_indexQuery->queryDocuments();
        
        auto endTime = std::chrono::steady_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime);
        
        logInfo("📊 查询完成，找到 " + std::to_string(records.size()) + " 个文件，耗时 " + std::to_string(duration.count()) + "ms");
        
        // 发送文件记录给daemon
        if (!records.empty()) {
            sendFileRecords(records);
        }
    }
    catch (const std::exception& e) {
        logError("❌ 文件查询失败: " + std::string(e.what()));
    }
}

ConnectorEvent FilesystemConnector::convertFileRecordToEvent(const FileRecord& record) {
    json eventData = {
        {"path", record.path},
        {"name", record.name},
        {"extension", record.extension},
        {"size", record.size},
        {"modified_time", record.modified_time}
    };
    
    return ConnectorEvent::create("filesystem", "file_discovered", std::move(eventData));
}

void FilesystemConnector::sendFileRecords(const std::vector<FileRecord>& records) {
    if (records.empty()) {
        return;
    }
    
    logInfo("📤 准备批量发送 " + std::to_string(records.size()) + " 个文件记录给daemon");
    
    // 批量发送，每批1000个文件
    const size_t BATCH_SIZE = 1000;
    size_t sent = 0;
    
    for (size_t i = 0; i < records.size(); i += BATCH_SIZE) {
        size_t end = std::min(i + BATCH_SIZE, records.size());
        size_t batchSize = end - i;
        
        // 创建批量事件数据
        json batchData = {
            {"event_type", "file_batch"},
            {"batch_id", i / BATCH_SIZE + 1},
            {"total_batches", (records.size() + BATCH_SIZE - 1) / BATCH_SIZE},
            {"files", json::array()}
        };
        
        // 添加当前批次的文件
        for (size_t j = i; j < end; ++j) {
            const auto& record = records[j];
            batchData["files"].push_back({
                {"path", record.path},
                {"name", record.name},
                {"extension", record.extension},
                {"size", record.size},
                {"modified_time", record.modified_time}
            });
        }
        
        // 发送批量事件
        ConnectorEvent batchEvent = ConnectorEvent::create("filesystem", "file_batch_discovered", std::move(batchData));
        sendEvent(batchEvent);
        
        sent += batchSize;
        logInfo("📊 已发送 " + std::to_string(sent) + "/" + std::to_string(records.size()) + " 个文件 (批次 " + std::to_string(i / BATCH_SIZE + 1) + ")");
        
        // 批次间短暂延迟，避免压垮daemon
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    
    // 发送汇总信息
    json summaryData = {
        {"event_type", "file_indexing_complete"},
        {"total_files", records.size()},
        {"total_batches", (records.size() + BATCH_SIZE - 1) / BATCH_SIZE},
        {"indexing_timestamp", std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count()}
    };
    
    ConnectorEvent summaryEvent = ConnectorEvent::create("filesystem", "indexing_summary", std::move(summaryData));
    sendEvent(summaryEvent);
    
    logInfo("✅ 文件记录批量发送完成，汇总信息已发送");
}

void FilesystemConnector::startPeriodicScanning() {
    m_shouldStopScanning = false;
    
    m_scanThread = std::make_unique<std::thread>([this]() {
        logInfo("🔄 定时扫描线程启动，每30分钟执行一次全量扫描");
        
        while (!m_shouldStopScanning) {
            // 等待30分钟，但每秒检查一次停止信号
            for (int i = 0; i < 1800 && !m_shouldStopScanning; ++i) {
                std::this_thread::sleep_for(std::chrono::seconds(1));
            }
            
            if (!m_shouldStopScanning) {
                logInfo("🔄 执行定时全量扫描...");
                performFileQuery();
            }
        }
        
        logInfo("✅ 定时扫描线程已退出");
    });
}

void FilesystemConnector::stopPeriodicScanning() {
    if (m_scanThread) {
        logInfo("🛑 停止定时扫描...");
        m_shouldStopScanning = true;
        
        if (m_scanThread->joinable()) {
            m_scanThread->join();
        }
        
        m_scanThread.reset();
        logInfo("✅ 定时扫描已停止");
    }
}

} // namespace linch_connector