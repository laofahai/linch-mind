#pragma once

#include <linch_connector/base_connector.hpp>
#include "filesystem_monitor_adapter.hpp"
#include "file_content_parser.hpp"
#include <vector>
#include <string>
#include <unordered_set>
#include <mutex>

namespace linch_connector {

/**
 * 用户目录监听文件系统连接器
 * 
 * 核心功能：
 * 1. 监听用户指定目录的文件变更（实时）
 * 2. 解析文件内容（不仅是元数据）
 * 3. 支持多种文件格式的内容解析
 * 4. 资源控制和性能优化
 * 
 * 注意：不负责全盘文件索引，由system_info连接器处理
 */
class FilesystemConnector : public BaseConnector {
public:
    FilesystemConnector();
    ~FilesystemConnector() override = default;
    
    /**
     * 添加用户指定目录进行监听
     * @param directoryPath 目录路径
     * @param recursive 是否递归监听子目录
     * @param parseContent 是否解析文件内容
     */
    bool addWatchDirectory(const std::string& directoryPath, bool recursive = true, bool parseContent = true);
    
    /**
     * 移除监听目录
     * @param directoryPath 目录路径
     */
    bool removeWatchDirectory(const std::string& directoryPath);
    
    /**
     * 获取当前监听的目录列表
     */
    std::vector<std::string> getWatchedDirectories() const;
    

protected:
    // 实现BaseConnector纯虚函数
    std::unique_ptr<IConnectorMonitor> createMonitor() override;
    bool loadConnectorConfig() override;
    bool onInitialize() override;
    bool onStart() override;
    void onStop() override;

private:
    // 文件系统监听适配器
    std::unique_ptr<FilesystemMonitorAdapter> m_monitor;
    
    // 文件内容解析器
    std::unique_ptr<IFileContentParser> m_contentParser;
    
    // 用户指定的监听目录
    std::unordered_set<std::string> m_watchedDirectories;
    mutable std::mutex m_directoriesMutex;
    
    // 配置参数
    bool m_enableContentParsing = true;      // 是否启用内容解析
    size_t m_maxFileSize = 10 * 1024 * 1024; // 最大解析文件大小（10MB）
    int m_eventDebounceMs = 500;             // 事件去重延迟（毫秒）
    
    /**
     * 处理文件系统事件回调
     */
    void onFileSystemEvent(const FileSystemEvent& event);
    
    /**
     * 处理文件创建事件
     */
    void handleFileCreated(const std::string& filePath);
    
    /**
     * 处理文件修改事件
     */
    void handleFileModified(const std::string& filePath);
    
    /**
     * 处理文件删除事件
     */
    void handleFileDeleted(const std::string& filePath);
    
    /**
     * 发送文件事件给daemon
     */
    void sendFileEvent(const std::string& eventType, const std::string& filePath, 
                      const std::string& content = "");
    
    
    /**
     * 检查文件是否应该被处理
     */
    bool shouldProcessFile(const std::string& filePath) const;
    
    /**
     * 获取支持的文件扩展名
     */
    std::vector<std::string> getSupportedExtensions() const;
};

} // namespace linch_connector